#!/usr/bin/env python
"""Land/manpower losses over time, from the save's war ledger, beside army size
and the free manpower pool.

THE SOURCE: every diplomacy/active_relations/<CP>/war_relation={} block carries
`first_casualties=` / `second_casualties=` - INTEGER manpower counters,
CUMULATIVE for that war (verified non-decreasing on 8 of 8 series across 5
saves of campaign 2d7b1b60, 1940.1-1945.8; GER-SOV reads 6,401,197 / 7,390,083
at 1945.8). The block is written in ONE country's block, chosen arbitrarily and
stable per war (GER hosts GER-SOV, ENG hosts ENG-GER, FIN hosts the 1941
FIN-SOV war while SOV hosted the 1939 one) - so this script scans EVERY
country's block and keys sides on the first=/second= fields, never on which
block hosts the record.

DIRECTION - DERIVED from magnitude, not an engine document: first_casualties =
losses OF the tag named first=. Four lopsided wars all point the same way
(SOV 7.39M vs GER 6.40M; CHI 3.25M vs JAP 1.50M; POL 278k vs GER 31k by
1940.1; FRA 770k vs GER 145k). The nested war_score_*/casualties key is a
war-participation SCORE in points (~ own losses / 2000, and the divisor is not
universal - POL/FRA rows fit ~/8000) - never read it as men.

WHAT A COUNTER COUNTS - ASSUMED: all manpower casualties the engine books to
that war; the combat-vs-attrition split is not serialised anywhere.

THE ONE STRUCTURAL TRAP: a war that ENDS IN A PEACE DELETES its war_relation
(the SOV-hosted Winter War block, start 1939.12.5, is gone by 1941.9; the
FIN-hosted 1941.6.22 block starts from zero). So a country's summed total can
DROP between saves - the drop IS the peace, and this script names the vanished
pair instead of printing a silent smaller number. "Total losses ever" is NOT
recoverable from one late save; pass the campaign's save series and read the
per-save deltas as the flow. Overrun-but-still-at-war pairs persist and keep
creeping (GER-POL alive 1939-1945, 278k -> 328k: exile units).

CONTEXT COLUMNS, for the losses-vs-forces comparison this exists for:
  divs    deployed divisions - division={ blocks at exact depth 1 inside
          units={} only, the same count as `savegame.py army` (the
          experience_status siblings that inflate a naive count are excluded).
  mp_pool the country's manpower={ ratio=N } scalar - ASSUMED the free
          manpower pool: it is the only shallow manpower number in a country
          block (no max_manpower / mobilized scalar exists at depth 2).

usage: losses.py TAG[,TAG,...]|ALL FILE... [--pairs] [--limit N]
  TAG,...  countries to report; ALL = every country holding a war ledger,
           sorted by cumulative losses, capped by --limit.
  --pairs  per-opponent breakdown under each country row.
  --limit  max countries per save in ALL mode (default 20, 0 = unlimited).

One streaming pass per save. A few tags without --pairs is one line per tag
per save (fine inline); ALL or --pairs over many saves belongs in a subagent.

Verified on campaign 2d7b1b60 (1941.9/1943.1/1945.8): pair values byte-equal
to the independent probe extraction, divs byte-equal to `savegame.py army`
and both its cross-check gauges, mp_pool equal to the probed manpower.ratio.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402

TAG_RE = re.compile(r"^\t([A-Z][A-Z0-9]{2})=\{")
WAR_FIELDS = ("first_casualties", "second_casualties", "first", "second",
              "start_date")
WAR_FIELD_RE = re.compile(r'(%s)="?([^"\s{}]+)"?' % "|".join(WAR_FIELDS))
RATIO_RE = re.compile(r"ratio=(-?[\d.]+)")


def scan(fh):
    """One pass over countries={}: ([war dicts], {tag: (divs, mp_pool)}).

    Depth-counted, never indentation (saves contain braces at column 0
    mid-file). war_relation={} is matched by block name at any depth inside a
    country - the save's only blocks of that name are the active_relations
    ones (path census, campaign 2d7b1b60, 1940.1 and 1945.8)."""
    for line in fh:
        if line.startswith("countries={"):
            break
    else:
        return [], {}
    wars, per = [], {}
    depth, tag = 1, None
    war, war_d = None, None
    units_d = mp_d = None
    divs = 0
    mp = None
    for line in fh:
        before = depth
        depth += line.count("{") - line.count("}")
        s = line.strip()
        if tag is None:
            if before == 1:
                m = TAG_RE.match(line)
                if m and depth > before:
                    tag, divs, mp = m.group(1), 0, None
            if depth <= 0:
                break
            continue
        if war is not None:
            for k, v in WAR_FIELD_RE.findall(s):
                war.setdefault(k, v)
            if depth <= war_d:
                wars.append(war)
                war, war_d = None, None
        elif s.startswith("war_relation={"):
            war = {"host": tag}
            for k, v in WAR_FIELD_RE.findall(s):
                war.setdefault(k, v)
            if depth > before:
                war_d = before
            else:
                wars.append(war)
                war = None
        elif units_d is not None:
            if before == 3 and depth > before and s.startswith("division={"):
                divs += 1
            if depth <= units_d:
                units_d = None
        elif mp_d is not None:
            m = RATIO_RE.search(s)
            if m:
                mp = int(float(m.group(1)))
            if depth <= mp_d:
                mp_d = None
        elif before == 2 and line.startswith("\t\tunits={") and depth > before:
            units_d = before
        elif before == 2 and line.startswith("\t\tmanpower={"):
            m = RATIO_RE.search(s)
            if m:
                mp = int(float(m.group(1)))
            elif depth > before:
                mp_d = before
        if depth <= 1 and tag is not None:
            per[tag] = (divs, mp)
            tag = None
            war = war_d = units_d = mp_d = None
        if depth <= 0:
            break
    return wars, per


def _int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def tally(wars):
    """{tag: {lost, inflicted, wars, pairs}} keyed on first=/second=, plus the
    war-identity set {(frozenset pair, start_date)} for peace detection."""
    out, keys = {}, set()
    for w in wars:
        f, s = w.get("first"), w.get("second")
        if not f or not s:
            continue
        fc, sc = _int(w.get("first_casualties")), _int(w.get("second_casualties"))
        start = w.get("start_date", "?")
        keys.add((frozenset((f, s)), start))
        for me, other, mine, theirs in ((f, s, fc, sc), (s, f, sc, fc)):
            e = out.setdefault(me, {"lost": 0, "inflicted": 0, "wars": 0,
                                    "pairs": []})
            e["lost"] += mine
            e["inflicted"] += theirs
            e["wars"] += 1
            e["pairs"].append((other, start, mine, theirs, w["host"]))
    return out, keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--pairs", action="store_true")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()
    want_all = args.tags.upper() == "ALL"
    want = None if want_all else [t.upper() for t in args.tags.split(",")]

    print("# Cumulative manpower losses PER LIVE WAR, summed per country over its "
          "war_relation ledger.")
    print("# lost/inflicted: DERIVED direction (first_casualties = losses OF "
          "first=; 4 lopsided wars concur).")
    print("# A peace DELETES its war's ledger: a dropping total is flagged with "
          "the vanished pair, and")
    print("#   no single save carries 'losses ever' - pass the campaign series "
          "and read the deltas.")
    print("# divs = deployed divisions (= savegame.py army); mp_pool = "
          "manpower={ratio=} free pool (ASSUMED).")

    prev_lost = {}
    prev_keys = set()
    prev_pairs = {}
    first_save = True
    for meta, f in sg.sorted_by_date([sg.resolve(x) for x in args.files]):
        with sg.open_save(f) as fh:
            wars, per = scan(fh)
        totals, keys = tally(wars)
        print(f"\n=== {meta.get('date', '?')}  {os.path.basename(f)} ===")

        if not first_save:
            # Most ledger exits are 0/0 diplomatic ends between micro-tags -
            # only a pair that carried losses AND touches a requested tag is
            # worth a line of its own; the rest is one count.
            zero = other = 0
            for pair, start in sorted(prev_keys - keys,
                                      key=lambda g: sorted(g[0])):
                a, b = sorted(pair)
                la, lb = prev_pairs.get((pair, start), (0, 0))
                if la + lb == 0:
                    zero += 1
                elif want is None or (pair & set(want)):
                    print(f"  PEACE: {a}-{b} (start {start}) left the ledger "
                          f"since the previous save - its {la:,}/{lb:,} "
                          f"cumulative losses leave every later total.")
                else:
                    other += 1
            if zero or other:
                extra = (f", {other} with losses among unrequested tags"
                         if other else "")
                print(f"  ({zero} zero-loss war ledgers left since the "
                      f"previous save{extra})")

        rows = want or sorted(totals, key=lambda t: -totals[t]["lost"])
        if want_all and args.limit:
            shown = rows[:args.limit]
            if len(rows) > len(shown):
                print(f"  ({len(rows) - len(shown)} more countries with a war "
                      f"ledger not shown - raise --limit, 0 = unlimited)")
            rows = shown
        for tag in rows:
            e = totals.get(tag)
            divs, mp = per.get(tag, (0, None))
            if e is None:
                if tag in per:
                    mp_s = f"{mp:,}" if mp is not None else "-"
                    print(f"  {tag:<5} no war ledger  divs={divs}  "
                          f"mp_pool={mp_s}")
                else:
                    print(f"  {tag:<5} no country block in this save")
                continue
            delta = ""
            if tag in prev_lost:
                d = e["lost"] - prev_lost[tag]
                delta = f"  d={d:+,}"
                if d < 0:
                    delta += " (peace removed a ledger, see PEACE line)"
            mp_s = f"{mp:,}" if mp is not None else "-"
            print(f"  {tag:<5} lost={e['lost']:>12,}{delta}  "
                  f"inflicted={e['inflicted']:,}  wars={e['wars']}  "
                  f"divs={divs}  mp_pool={mp_s}")
            if args.pairs:
                for other, start, mine, theirs, host in sorted(
                        e["pairs"], key=lambda p: -p[2]):
                    side = "own block" if host == tag else f"{host}'s block"
                    print(f"      vs {other:<5} since {start:<12} "
                          f"lost={mine:>12,}  inflicted={theirs:>12,}  "
                          f"[{side}]")

        prev_lost = {t: e["lost"] for t, e in totals.items()}
        prev_keys = keys
        prev_pairs = {}
        for w in wars:
            f2, s2 = w.get("first"), w.get("second")
            if not f2 or not s2:
                continue
            k = (frozenset((f2, s2)), w.get("start_date", "?"))
            prev_pairs[k] = (_int(w.get("first_casualties")),
                             _int(w.get("second_casualties")))
        first_save = False


if __name__ == "__main__":
    main()
