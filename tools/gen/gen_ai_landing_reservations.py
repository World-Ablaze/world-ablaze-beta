#!/usr/bin/env python3
"""
gen_ai_landing_reservations.py - generate the scripted-invasion target-reservation data.

[scripted-invasion-reservation] While the scripted-landing calendar still owes an operation
against a country, the invader's whole faction suppresses ENGINE-planned naval invasions of
that country (consumer: WA_AI_MILITARY_INV_reserved_scripted_target in
common/ai_strategy/WA_AI_MILITARY_DEFAULT_INVASION_landing_freeze.txt). This tool derives,
for every ACTIVE line of the KDE calendar, the (invader, anchor state, expiry day) triple the
runtime needs, and writes them as per-invader arrays into the generated data file.

Sources (both hand-maintained; this tool never edits them):
  common/scripted_effects/WA_KDE_AI_effects.txt   WHO fires WHAT and WHEN (year + day offset;
                                                  lines commented out with # are skipped)
  events/WA_AI_invasions.txt                      each operation's ANCHOR STATE = the state
                                                  whose CONTROLLER the event reads as its
                                                  target country (first
                                                  `<id> = { CONTROLLER = { set_temp_variable
                                                  = { _target_country = id } } }` block)

Output:
  common/scripted_effects/WA_AI_LANDING_reservations_data.txt
    WA_AI_LANDING_load_ops - clears and refills, per invader tag:
      WA_AI_LANDING_op_anchor  array of anchor state ids
      WA_AI_LANDING_op_expiry  array of expiry days since 1936.1.1 (fire date + GRACE_DAYS)
      WA_AI_LANDING_op_n       row count
    Idempotent (clear_array first), so on_startup may re-run it on every save load.

Expiry = scheduled fire date + GRACE_DAYS. GRACE_DAYS covers the event's own 7-day refire
loop (an operation whose preconditions are not met on its scheduled day lands late); after
the landing actually executes, the theatre freeze (doc sec.10) takes over, so the grace does
not need to cover the whole campaign tail. Day arithmetic uses the real (leap-aware) Python
calendar; if the engine's day count disagrees over leap days it is by <=3 days across the
whole calendar - immaterial against the 50-day reservation lease.

Calendar scope: the KDE yearly schedule ONLY. Events fired from other call sites (e.g. the
Mulberry pair WA_AI_invasions.101/.102) are not part of the reservation calendar.

Usage (any cwd; the mod root is derived from this file's location):
  python gen_ai_landing_reservations.py --dry-run   # report what would be written
  python gen_ai_landing_reservations.py             # write the data file
Exit 2 if any scheduled operation has no recoverable anchor state - fix the source first.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

GRACE_DAYS = 45  # days past the scheduled fire date a reservation stays pending
EPOCH = datetime.date(1936, 1, 1)

REPO = Path(__file__).resolve().parents[2]
KDE_PATH = REPO / "common" / "scripted_effects" / "WA_KDE_AI_effects.txt"
EVENTS_PATH = REPO / "events" / "WA_AI_invasions.txt"
OUT_PATH = REPO / "common" / "scripted_effects" / "WA_AI_LANDING_reservations_data.txt"

RE_YEAR = re.compile(r"WA_KDE_yearly_event_fire_(\d{4})\s*=\s*\{")
RE_TAG = re.compile(r"^\t([A-Z][A-Z0-9]{2})\s*=\s*\{")
RE_EVENT = re.compile(
    r"^(?P<comment>#?)\s*country_event\s*=\s*\{\s*id\s*=\s*WA_AI_invasions\.(?P<id>\d+)"
    r"\s+days\s*=\s*(?P<days>\d+)\s*\}\s*(?:#\s*(?P<name>.*))?$"
)
RE_EVENT_ID = re.compile(r"id\s*=\s*WA_AI_invasions\.(\d+)\b")
RE_ANCHOR = re.compile(
    r"(\d+)\s*=\s*\{[^{}]*#[^\n]*\n\s*CONTROLLER\s*=\s*\{"
    r"|(\d+)\s*=\s*\{\s*CONTROLLER\s*=\s*\{"
)


def parse_kde(text):
    """Yield (year, tag, event_id, day_offset, name) for every ACTIVE calendar line."""
    year = None
    tag = None
    for raw in text.splitlines():
        m = RE_YEAR.search(raw)
        if m:
            year = int(m.group(1))
            tag = None
            continue
        m = RE_TAG.match(raw)
        if m:
            tag = m.group(1)
            continue
        m = RE_EVENT.match(raw.strip())
        if m and year is not None and tag is not None:
            if raw.lstrip().startswith("#") or m.group("comment"):
                continue  # deliberately disabled operation
            yield year, tag, int(m.group("id")), int(m.group("days")), (m.group("name") or "").strip()


def split_events(text):
    """Return {event_id: body_text} for every country_event block in the events file."""
    events = {}
    for m in re.finditer(r"country_event\s*=\s*\{", text):
        start = m.end()
        depth = 1
        i = start
        while depth and i < len(text):
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        body = text[start:i]
        idm = RE_EVENT_ID.search(body)
        if not idm:
            continue
        eid = int(idm.group(1))
        # The files contain nested self-refire calls (`country_event = { id = ... days = 7 }`)
        # whose tiny bodies must not shadow the real definition: only a body with an
        # immediate block is a definition.
        if "immediate" in body or eid not in events:
            events[eid] = body
    return events


def find_anchor(body):
    """First `<state> = { CONTROLLER = { set_temp_variable = { _target_country = id } } }`."""
    # Three events (.39, .58, .59) read OWNER instead of CONTROLLER; the anchor state is the
    # same either way. The runtime always reads the CONTROLLER at pulse time - the entity the
    # engine would actually invade.
    m = re.search(
        r"(\d+)\s*=\s*\{[^{}]*?\n\s*(?:CONTROLLER|OWNER)\s*=\s*\{\s*\n?\s*"
        r"set_temp_variable\s*=\s*\{\s*_target_country\s*=\s*id\s*\}",
        body,
    )
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report without writing")
    args = ap.parse_args()

    kde = KDE_PATH.read_text(encoding="utf-8-sig")
    events_text = EVENTS_PATH.read_text(encoding="utf-8-sig")
    events = split_events(events_text)

    rows = []  # (tag, anchor, expiry_day, fire_date, event_id, name)
    missing = []
    for year, tag, eid, day_offset, name in parse_kde(kde):
        body = events.get(eid)
        if body is None:
            missing.append((tag, eid, name, "event id not found in events file"))
            continue
        anchor = find_anchor(body)
        if anchor is None:
            missing.append((tag, eid, name, "no anchor-state CONTROLLER block found"))
            continue
        fire = datetime.date(year, 1, 1) + datetime.timedelta(days=day_offset)
        expiry = (fire - EPOCH).days + GRACE_DAYS
        rows.append((tag, anchor, expiry, fire, eid, name))

    if missing:
        print("ERROR: %d scheduled operation(s) unusable:" % len(missing))
        for tag, eid, name, why in missing:
            print("  %s WA_AI_invasions.%d (%s): %s" % (tag, eid, name or "?", why))
        return 2

    by_tag = {}
    for row in rows:
        by_tag.setdefault(row[0], []).append(row)
    for tag in by_tag:
        by_tag[tag].sort(key=lambda r: r[2])

    lines = []
    lines.append("############################################################################################################")
    lines.append("#\tWA AI LANDING - scripted-invasion target-reservation data")
    lines.append("#")
    lines.append("#\tGENERATED FILE - do not hand-edit. Regenerate with:")
    lines.append("#\t    python tools/gen/gen_ai_landing_reservations.py")
    lines.append("#\tSources: WA_KDE_AI_effects.txt (calendar) + events/WA_AI_invasions.txt (anchor states).")
    lines.append("#\tConsumers: WA_AI_LANDING_update_reservations (WA_AI_LANDING_effects.txt).")
    lines.append("#")
    lines.append("#\tWA_AI_LANDING_op_anchor^i  anchor state of operation i (its CONTROLLER at pulse time is the")
    lines.append("#\t                           reservation target - dynamic, never a stored tag)")
    lines.append("#\tWA_AI_LANDING_op_expiry^i  last pending day, as days since 1936.1.1 (fire date + %d grace)" % GRACE_DAYS)
    lines.append("#\tCompared against global.num_days - global.WA_AI_LANDING_epoch (epoch set at startup).")
    lines.append("#")
    lines.append("#\tTag scopes below are DATA, not gating: this file is the generated mirror of the tag-keyed")
    lines.append("#\tKDE calendar (same standing as common/ai_faction_theaters). Rule 2 archetype triggers do")
    lines.append("#\tnot apply to a calendar that is itself per-country.")
    lines.append("############################################################################################################")
    lines.append("")
    lines.append("# SCOPE: any. Idempotent - safe to re-run on every startup, including save loads.")
    lines.append("WA_AI_LANDING_load_ops = {")
    for tag in sorted(by_tag):
        lines.append("\t%s = {" % tag)
        lines.append("\t\tclear_array = WA_AI_LANDING_op_anchor")
        lines.append("\t\tclear_array = WA_AI_LANDING_op_expiry")
        for _, anchor, expiry, fire, eid, name in by_tag[tag]:
            lines.append("\t\tadd_to_array = { WA_AI_LANDING_op_anchor = %d }\t# %s (.%d) fires %s" % (anchor, name or "?", eid, fire.isoformat()))
            lines.append("\t\tadd_to_array = { WA_AI_LANDING_op_expiry = %d }" % expiry)
        lines.append("\t\tset_variable = { WA_AI_LANDING_op_n = %d }" % len(by_tag[tag]))
        lines.append("\t}")
    lines.append("}")
    out = "\n".join(lines) + "\n"

    total = sum(len(v) for v in by_tag.values())
    print("calendar: %d active operations, %d invaders (%s)" % (
        total, len(by_tag), ", ".join("%s:%d" % (t, len(by_tag[t])) for t in sorted(by_tag))))
    for tag in sorted(by_tag):
        first = by_tag[tag][0]
        last = by_tag[tag][-1]
        print("  %s  first %s (%s)  last %s (%s)" % (
            tag, first[3].isoformat(), first[5] or "?", last[3].isoformat(), last[5] or "?"))
    if args.dry_run:
        print("dry-run: would write %d lines to %s" % (out.count("\n"), OUT_PATH))
        return 0
    OUT_PATH.write_text(out, encoding="utf-8", newline="\n")  # BOM-free by construction
    print("wrote %s" % OUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
