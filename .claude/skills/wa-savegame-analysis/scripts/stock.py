#!/usr/bin/env python
"""Equipment stockpile by holder, ATTRIBUTED TO THE COUNTRY THAT BUILT IT.

Why this exists (2026-08-20, campaign 3d68a183). "Did the scripted lend-lease
actually deliver?" was unanswerable from a save: the WA_TLM llr_* family counts
what the DONOR sent, and nothing read the other end. The counters can only prove
the send site fired - a send that silently moves nothing looks identical (that is
exactly how `send_equipment` passed review while carrying no convoys: QUEUE row 13).
This script reads the receiving end.

THE LOAD-BEARING FACT: equipment carries its maker. The save's top-level
`equipments={}` block defines one variant per (equipment name, creator country):

    equipments={ convoy_1={ id={ id=1 type=70 }  creator="GER" ... }
                 convoy_1={ id={ id=3 type=70 }  creator="ENG" ... } ... }

so an id is a (name, creator) pair, and a holder's stockpile entry against an id
whose creator is not the holder is equipment it did not build.

TWO DELIVERY PATHS, AND THE WHOLE POINT IS TELLING THEM APART:

    stockpile      country > production > equipments={ equipment={ id={id=N} amount=X } }
                   What `add_equipment_to_stockpile` writes - the WA scripted
                   transfer since QUEUE row 13's fix (b). The equipment is OWNED.
    foreign lease  country > production > foreign_lease_equipments={ equipment={id=N} }
                   VANILLA lend-lease. The equipment is on loan and returns.
                   `send_equipment` writes here - and does NOT carry convoys.

A recipient holding a donor's variant in its STOCKPILE is the WA path working.
The same id appearing only under foreign lease is vanilla's, and says nothing
about the scripted transfer.

CREATOR IS THE MAKER, NOT THE SENDER - the one thing to get wrong here.
An entry says who BUILT the equipment, never how the holder came by it. Measured case,
2026-08-20 on `3d68a183`: Germany's stockpile gains 733 ITA-built `convoy_1` between the
1939.10 and 1939.11 saves and holds them, frozen, for the next six years - while Italy's
own owned convoy stock sits at 581 / 581 / 582 / 583 across the same window and Germany's
`llr_convoy_donor_selected_n` for the whole campaign is 5. Italy sent nothing. In the same
month Germany also gains 1 353 POL-built and 130 FRA-built items it never held before:
war booty, which carries the original maker's stamp for ever. So a foreign-built row is
evidence of OWNERSHIP, and corroboration at best for any particular delivery mechanism.
To prove a WA scripted transfer, read `wa_tlm_llr_sent_n` - that counter increments only
after `WA_AI_LEND_LEASE_relief_record` has checked the recipient's stock actually rose
(`_llr_recipient_after > _llr_recipient_stock`), and books `llr_send_failed_n` otherwise.

WHAT THIS SCRIPT CANNOT TELL YOU: which transfer an item came from, or when.
Amounts are a stock, not a flow - consumption, losses and later transfers are all
folded into one number. Read it against the donor's `wa_tlm_llr_sent_amount`
(savegame.py tlm) as an order-of-magnitude check, never as an equality.

One streaming pass per save: the top-level `equipments={}` block precedes
`countries={}` (verified 129 090 vs 1 249 055 on 1946.1_Jan), so definitions are
always known by the time a holder is read.

usage: stock.py TAG[,TAG,...] FILE... [--match RE] [--creator TAG] [--all]
                                      [--foreign] [--limit N]
  --match    regex on the VARIANT name as the save stores it, which is not the archetype:
             WA's German rifle variants are `ger_inf_*` / `ger_hv_inf_*`, so `--match infantry`
             finds NOTHING and `--match "_inf"` finds them. Check a `--all` listing first.
  --creator  only rows built by this tag
  --all      include rows the holder built itself (default: foreign-built only)
  --foreign  also list the vanilla foreign-lease ids (loans, not owned)
  --limit    max rows per holder per save (default 40, 0 = unlimited)
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402

ID_RE = re.compile(r"id=(\d+)")
DEF_RE = re.compile(r"^\t([A-Za-z_][A-Za-z0-9_]*)=\{")
CREATOR_RE = re.compile(r'creator="([A-Z0-9]{3})"')


def equipment_definitions(fh):
    """{variant id: (equipment name, creator tag)} from the top-level equipments={}.

    Keyed by id because that is what a holder's stockpile references. Entries whose
    creator line is absent are kept with creator None rather than dropped - an
    unattributed variant is a real state (vanilla starting equipment on some tags)
    and silently discarding it would understate a holder's own production.
    """
    defs = {}
    for line in fh:
        if line.startswith("equipments={"):
            break
    else:
        return defs
    depth, name, eid, creator = 1, None, None, None
    for line in fh:
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            break
        m = DEF_RE.match(line)
        if m:
            if name is not None and eid is not None:
                defs[eid] = (name, creator)
            name, eid, creator = m.group(1), None, None
            continue
        t = line.strip()
        if eid is None and t.startswith("id={"):
            m2 = ID_RE.search(t)
            if m2:
                eid = int(m2.group(1))
        elif creator is None:
            m3 = CREATOR_RE.search(t)
            if m3:
                creator = m3.group(1)
    if name is not None and eid is not None:
        defs[eid] = (name, creator)
    return defs


def holders_equipment(fh, tags):
    """{tag: ({variant id: amount} owned, [variant ids on foreign lease])}, ONE PASS.

    Deliberately not a per-tag call of sg.iter_country_lines: that helper consumes the
    stream up to its tag, so a second call for a tag stored EARLIER in countries={}
    silently returns nothing. Reading every requested tag in one walk is what makes a
    multi-tag invocation honest - the first version of this script reported SOV as
    holding zero equipment for exactly that reason.
    """
    want = set(tags)
    out = {t: ({}, []) for t in tags}
    for line in fh:
        if line.startswith("countries={"):
            break
    else:
        return out
    depth = 1
    for line in fh:
        if depth == 1:
            m = re.match("^	([A-Z0-9]{3})=\{", line)
            if m and m.group(1) in want:
                tag = m.group(1)
                d = line.count("{") - line.count("}")
                body = []
                while d > 0:
                    nxt = next(fh, None)
                    if nxt is None:
                        break
                    d += nxt.count("{") - nxt.count("}")
                    if d > 0:
                        body.append(nxt)
                out[tag] = _scan_country_body(body, tag)
                want.discard(tag)
                if not want:
                    break
                continue
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            break
    return out


def _scan_country_body(lines, tag):
    """({variant id: amount} owned, [variant ids on foreign lease]) from one body.

    The stockpile entry is the MULTI-LINE `equipment={` form carrying both an
    `id={...}` and an `amount=`; the available/foreign-lease lists use a single-line
    `equipment={ id=N type=70 }` with no amount. That structural difference is the
    discriminator - block names are not, because a country block contains three
    different `equipments={}` blocks (equipment market, available, production).
    """
    owned, foreign = {}, []
    block, in_entry, eid, amount = None, False, None, None
    for line in lines:
        t = line.strip()
        if t.endswith("={") and not t.startswith("equipment={"):
            block = t[:-2]
        if t.startswith("equipment={"):
            if t.endswith("}"):
                m = ID_RE.search(t)
                if m and block == "foreign_lease_equipments":
                    foreign.append(int(m.group(1)))
                continue
            in_entry, eid, amount = True, None, None
            continue
        if in_entry:
            if t.startswith("id={"):
                m = ID_RE.search(t)
                if m:
                    eid = int(m.group(1))
            elif t.startswith("amount="):
                try:
                    amount = float(t.split("=", 1)[1])
                except ValueError:
                    amount = None
            elif t == "}":
                if eid is not None and amount is not None:
                    owned[eid] = owned.get(eid, 0.0) + amount
                in_entry = False
    return owned, foreign


def fmt(n):
    return f"{n:,.0f}" if abs(n - round(n)) < 0.01 else f"{n:,.2f}"


def main(argv):
    tags, files, match, creator, show_all, show_foreign, limit = None, [], None, None, False, False, 40
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--match":
            i += 1; match = re.compile(argv[i], re.I)
        elif a == "--creator":
            i += 1; creator = argv[i].upper()
        elif a == "--all":
            show_all = True
        elif a == "--foreign":
            show_foreign = True
        elif a == "--limit":
            i += 1; limit = int(argv[i])
        elif a.startswith("--"):
            sys.exit(f"unknown option {a}")
        elif tags is None:
            tags = [t.strip().upper() for t in a.split(",") if t.strip()]
        else:
            files.append(a)
        i += 1
    if not tags or not files:
        sys.exit(__doc__)

    print("# Equipment is attributed by the CREATOR of its variant, read from the save's")
    print("#   top-level equipments={} block. A row whose creator is not the holder is")
    print("#   equipment the holder did not build.")
    print("# OWNED (stockpile) is what add_equipment_to_stockpile writes - WA's scripted")
    print("#   transfer. FOREIGN LEASE is vanilla lend-lease: a loan, not a delivery, and")
    print("#   it never carries convoys. The two are different mechanisms; do not add them.")
    print("# Amounts are a STOCK, not a flow. Consumption and losses are already folded in,")
    print("#   so read against the donor's wa_tlm_llr_sent_amount as magnitude, not equality.")
    print("# A NEGATIVE amount is a real state the engine writes (equipment committed beyond")
    print("#   what is on hand), not a parse error - it is left signed rather than clamped.")
    print("# CREATOR IS THE MAKER, NOT THE SENDER: war booty and captured stock keep the")
    print("#   original builder's stamp for ever. A foreign-built row proves ownership, not a")
    print("#   delivery mechanism - for a WA scripted transfer read wa_tlm_llr_sent_n instead.")

    for path in files:
        fh = sg.open_save(path)
        defs = equipment_definitions(fh)
        date = sg.read_meta(path).get("date", "?")
        base = os.path.basename(path)
        held = holders_equipment(fh, tags)
        for tag in tags:
            owned, foreign = held[tag]
            rows = []
            for eid, amt in owned.items():
                name, made_by = defs.get(eid, (f"<id {eid}>", None))
                if match and not match.search(name):
                    continue
                if creator and made_by != creator:
                    continue
                if not show_all and made_by == tag:
                    continue
                rows.append((name, made_by, amt, eid))
            rows.sort(key=lambda r: -r[2])

            by_creator = {}
            for eid, amt in owned.items():
                made_by = defs.get(eid, (None, None))[1]
                by_creator[made_by] = by_creator.get(made_by, 0.0) + amt
            foreign_n = sum(1 for e in foreign if defs.get(e, (None, None))[1] != tag)

            print(f"\n=== {date}  {tag}  ({base}) ===")
            print(f"  stockpile variants={len(owned)}  foreign-built variants held="
                  f"{sum(1 for e in owned if defs.get(e, (None, None))[1] not in (tag, None))}"
                  f"  vanilla foreign-lease ids={len(foreign)} ({foreign_n} from other creators)")
            if not rows:
                scope = "any creator" if show_all else "a creator other than " + tag
                print(f"  NO MATCH: no stockpile row for {scope}"
                      + (f" matching '{match.pattern}'" if match else "")
                      + (f" built by {creator}" if creator else ""))
            else:
                print(f"  {'equipment':<34}{'built by':<10}{'amount':>14}   variant")
                shown = rows if limit == 0 else rows[:limit]
                for name, made_by, amt, eid in shown:
                    print(f"  {name:<34}{(made_by or '-'):<10}{fmt(amt):>14}   id {eid}")
                if len(rows) > len(shown):
                    print(f"  ... {len(rows) - len(shown)} more row(s) - raise --limit (0 = unlimited)")
            tot = ["%s %s" % (c or "-", fmt(v)) for c, v in
                   sorted(by_creator.items(), key=lambda kv: -kv[1])[:8]]
            print("  WHOLE-stockpile totals by builder (NOT filtered by --match/--creator): " + "  ".join(tot))
            if show_foreign and foreign:
                names = {}
                for e in foreign:
                    n, c = defs.get(e, (f"<id {e}>", None))
                    names.setdefault((n, c), 0)
                    names[(n, c)] += 1
                print("  vanilla foreign lease (LOANS, not owned):")
                for (n, c), k in sorted(names.items())[:limit or None]:
                    print(f"    {n:<34}{(c or '-'):<10} {k} variant(s)")


if __name__ == "__main__":
    main(sys.argv[1:])
