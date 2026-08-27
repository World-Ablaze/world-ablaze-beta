#!/usr/bin/env python
"""Convoy war / submarine campaign dashboard: kills, losses, regions, posture.

One streaming pass per save assembles the Battle-of-the-Atlantic picture no
single structure carries:

  sunk_convoys_history   top-level; one record per (month, killer, owner) pair.
                         THE convoy-loss ledger, but a ROLLING 24-MONTH WINDOW
                         ending at the save's last complete month - pre-window
                         history is gone. Passing several saves of one campaign
                         stitches the windows; months in range that NO passed
                         save covers print as "no data", never as 0.
  convoys_destroyed      country depth 1, cumulative kills BY that country
                         (= wa_tlm_nav_conv_killed). Deltas between consecutive
                         saves turn the cumulative counter into a flow.
  ship sunk_convoys      per-ship kill counter - SURVIVOR-ONLY: the counter dies
                         with the boat (GER 1944.6: alive boats account for 3 992
                         of 13 493 national kills, 70% belong to dead boats).
                         The aces table states the covered share on its header.
  sunk_ship records      kill log held on the KILLER's surviving ship (warships
                         only - convoy=yes occurs 0 times in 1 536 records).
                         Read across ALL countries it is the only save-side view
                         of SUBMARINE LOSSES (escorts' records of subs they
                         killed). Survivor-biased too: records die with the
                         killer; the union across passed saves is a lower bound.
  strategic_navy         per-region need (required_convoys), last_sunk_convoy_date
                         and per_region_danger - the WHERE of the campaign.
                         `efficiency=` is serialized on ~4% of entries only
                         (ASSUMED omitted when 1.0); treat absence as ~1.0.

WHAT NO SAVE CARRIES (do not go looking): the victim's total convoy NEED
(free pool `wa_tlm_nav_convoys` is the only proxy: 0 = real famine, see the
skill gotcha), a victim-side loss counter (reconstructed here from the ledger's
owner= field), per-region loss counts, and any naval combat history beyond the
snapshot instant.

usage: convoywar.py FILE... [--killer TAGS] [--owner TAGS] [--limit N]
  --killer  comma list of raider tags to focus (default: top 2 by kills)
  --owner   comma list of victim tags to focus (default: top 2 by losses)
  --limit   max rows for pair/aces/region tables (default 15, 0 = unlimited)

Consumers: any convoy-raiding / sub-warfare efficiency question. Bulky output:
run inside a subagent per the skill's context discipline.
"""
import argparse
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402
import regions as rg   # noqa: E402

TAG_RE = re.compile(r"^\t([A-Z0-9]{3})=\{")


def _val(st):
    return st.split("=", 1)[1].strip().strip('"')


def _num(st):
    try:
        return float(_val(st))
    except ValueError:
        return 0.0


def parse_save(path):
    """One pass: history records, and per-country convoy-war state."""
    hist = []                       # {month, convoys, killer, owner}
    countries = {}                  # tag -> dict

    def cnew():
        return {"kills": None, "fleet": 0, "tlm": {}, "missions": collections.Counter(),
                "subs": 0, "aces": [], "sunk": [], "regional": [], "danger": {}}

    with sg.open_save(path) as fh:
        depth = 0
        in_countries = False
        sch_d = None                # inside sunk_convoys_history
        rec = None
        tag = None
        cd = 0                      # depth within country block
        c = None
        section = None              # units | strategic_navy | variables | convoyfleet
        sec_d = None
        # units machine (savegame._parse_fleets pattern: content first, one
        # depth update per line, innermost closed first)
        tf_d = ship_d = miss_d = sunk_d = None
        tf_mission = None
        tf_ships = []                # ships buffered until the tf closes:
        ship = None                  # mission={} sits AFTER the ship blocks
        sunk = None
        # strategic_navy machine
        sn_child = None
        sn_d = None
        rc = None
        danger_nums = []

        for line in fh:
            st = line.strip()
            delta = line.count("{") - line.count("}")

            if sch_d is not None:
                if st.startswith("sunk_convoy={"):
                    rec = {}
                elif rec is not None:
                    if st.startswith("month="):
                        rec["month"] = int(_num(st))
                    elif st.startswith("convoys="):
                        rec["convoys"] = int(_num(st))
                    elif st.startswith("killer_country="):
                        rec["killer"] = _val(st)
                    elif st.startswith("owner="):
                        rec["owner"] = _val(st)
                    elif "}" in st:
                        if "month" in rec:
                            hist.append(rec)
                        rec = None
            elif tag is not None:
                if section == "units":
                    if ship_d is not None:
                        if sunk_d is not None:
                            if sunk_d == 1:
                                for k in ("name", "killer_name", "country",
                                          "killer_country", "definition",
                                          "killer_definition", "date", "convoy"):
                                    if st.startswith(k + "="):
                                        sunk[k] = _val(st)
                                        break
                        elif st.startswith("sunk_ship={"):
                            sunk_d = 0
                            sunk = {}
                        elif ship_d == 1:
                            # depth 1 ONLY: deeper history blocks carry the
                            # VICTIM's definition= (the 2026-08-13 gotcha).
                            if st.startswith("definition="):
                                ship["definition"] = _val(st)
                            elif st.startswith("sunk_convoys="):
                                ship["sunk_convoys"] = int(_num(st))
                            elif st.startswith("experience="):
                                ship["exp"] = _num(st)
                        elif st.startswith('override="') and "name" not in ship:
                            # the ship's display name: ship_name={ override="..." }
                            ship["name"] = _val(st)
                    elif tf_d is not None:
                        if st.startswith("ship={"):
                            ship_d = 0
                            ship = {}
                        elif miss_d is not None:
                            if st.startswith("mission="):
                                tf_mission = sg._NAVAL_MISSIONS.get(
                                    st.split("=")[1], st.split("=")[1])
                        elif st.startswith("mission={"):
                            miss_d = 0
                    elif st.startswith("task_force={"):
                        tf_d = 0
                        tf_mission = None
                        tf_ships = []
                elif section == "strategic_navy":
                    if sn_child == "regional_convoys":
                        # entries can be single-line: { index=29 data={
                        # required_convoys=81 efficiency=0.99 ... } } - regex
                        # the whole line instead of startswith per field
                        m = re.search(r"\bindex=(\d+)", st)
                        if m:
                            rc = {"index": int(m.group(1))}
                            c["regional"].append(rc)
                        if rc is not None:
                            m = re.search(r"\brequired_convoys=(\d+)", st)
                            if m:
                                rc["required"] = int(m.group(1))
                            m = re.search(r"\befficiency=([\d.]+)", st)
                            if m:
                                rc["eff"] = float(m.group(1))
                            m = re.search(r'last_sunk_convoy_date="([^"]+)"', st)
                            if m:
                                rc["last_sunk"] = m.group(1)
                    elif sn_child == "per_region_danger":
                        for tok in st.replace("{", " ").replace("}", " ").split():
                            if tok.lstrip("-").isdigit():
                                danger_nums.append(int(tok))
                    elif st.startswith("regional_convoys={"):
                        sn_child, sn_d, rc = "regional_convoys", 0, None
                    elif st.startswith("per_region_danger={"):
                        sn_child, sn_d = "per_region_danger", 0
                        danger_nums = []
                        # tokens can sit on the opening line
                        for tok in st.split("{", 1)[1].replace("}", " ").split():
                            if tok.lstrip("-").isdigit():
                                danger_nums.append(int(tok))
                elif section == "variables":
                    if cd == 2 and st.startswith("wa_tlm_nav_") and "^" not in st:
                        name = st.split("=", 1)[0]
                        c["tlm"][name] = _num(st)
                elif section == "convoyfleet":
                    if st.startswith("amount="):
                        c["fleet"] += int(_num(st))
                elif cd == 1:
                    if st.startswith("convoys_destroyed="):
                        c["kills"] = int(_num(st))
                    elif st.startswith("units={"):
                        section, sec_d = "units", 0
                    elif st.startswith("strategic_navy={"):
                        section, sec_d = "strategic_navy", 0
                    elif st.startswith("variables={"):
                        section, sec_d = "variables", 0
                    elif st.startswith("convoys={"):
                        section, sec_d = "convoyfleet", 0
            elif in_countries and depth == 1:
                m = TAG_RE.match(line)
                if m:
                    tag = m.group(1)
                    c = countries.setdefault(tag, cnew())
                    cd = 0
            elif depth == 0:
                if line.startswith("sunk_convoys_history={"):
                    sch_d = 0
                elif line.startswith("countries={"):
                    in_countries = True

            # --- one depth update per line, innermost first
            depth += delta
            if sch_d is not None:
                sch_d += delta
                if sch_d <= 0:
                    sch_d = None
            if sunk_d is not None:
                sunk_d += delta
                if sunk_d <= 0:
                    if sunk.get("date"):
                        c["sunk"].append(sunk)
                    sunk_d = sunk = None
            if miss_d is not None:
                miss_d += delta
                if miss_d <= 0:
                    miss_d = None
            if ship_d is not None:
                ship_d += delta
                if ship_d <= 0:
                    tf_ships.append(ship)
                    ship_d = ship = None
            if tf_d is not None:
                tf_d += delta
                if tf_d <= 0:
                    # flush now: the tf's mission={} block sits AFTER its ships
                    m = tf_mission or "none"
                    for s in tf_ships:
                        d2 = s.get("definition", "?")
                        c["missions"][m] += 1
                        if "submarine" in d2:
                            c["subs"] += 1
                        if s.get("sunk_convoys"):
                            c["aces"].append((s["sunk_convoys"],
                                              s.get("name", "-"), d2, m))
                    tf_d = None
                    tf_ships = []
            if sn_d is not None:
                sn_d += delta
                if sn_d <= 0:
                    if sn_child == "per_region_danger":
                        it = iter(danger_nums)
                        c["danger"] = dict(zip(it, it))
                    sn_child = sn_d = None
            if sec_d is not None:
                sec_d += delta
                if sec_d <= 0:
                    section = sec_d = None
            if tag is not None:
                cd += delta
                if cd <= 0:
                    tag = c = None
                    section = sec_d = None
            if in_countries and depth <= 0:
                in_countries = False
    return hist, countries


def month_dec(m):
    return "%d.%d" % (m // 12, m % 12 + 1)


def save_window(date):
    """[first, last] month index covered by this save's 24-month ledger window
    (last complete month, measured on 1ac7e4ea: 1944.6 save covers 1942.6-1944.5)."""
    parts = sg.date_key(date)
    last = parts[0] * 12 + (parts[1] - 1) - 1
    return last - 23, last


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--killer", help="comma list of raider tags to focus")
    ap.add_argument("--owner", help="comma list of victim tags to focus")
    ap.add_argument("--limit", type=int, default=15,
                    help="max rows for pair/aces/region tables (0 = unlimited)")
    args = ap.parse_args()
    lim = args.limit if args.limit else 10 ** 9

    print("# convoy war dashboard. Ledger window = 24 months per save; 'no data'")
    print("# = no passed save covers that month (NOT zero losses). Aces and sub-loss")
    print("# tables are survivor-biased lower bounds - headers state the covered share.")

    entries = sg.sorted_by_date([sg.resolve(f) for f in args.files])
    saves = []
    for meta, f in entries:
        hist, countries = parse_save(f)
        saves.append((meta.get("date", "?"), f, hist, countries))

    # --- stitch the ledgers: later save wins on overlap (values are identical
    # where windows overlap; the ledger is append-only within its window).
    merged = {}
    covered = set()
    for date, f, hist, _ in saves:
        lo, hi = save_window(date)
        covered.update(range(lo, hi + 1))
        for r in hist:
            merged[(r["month"], r.get("killer", "?"), r.get("owner", "?"))] = \
                r.get("convoys", 0)

    kfocus = args.killer.split(",") if args.killer else None
    ofocus = args.owner.split(",") if args.owner else None

    def keep(k, o):
        return (kfocus is None or k in kfocus) and (ofocus is None or o in ofocus)

    by_month = collections.defaultdict(int)
    by_month_killer = collections.defaultdict(collections.Counter)
    pair = collections.Counter()
    killer_tot = collections.Counter()
    owner_tot = collections.Counter()
    for (m, k, o), n in merged.items():
        if not keep(k, o):
            continue
        by_month[m] += n
        by_month_killer[m][k] += n
        pair[(k, o)] += n
        killer_tot[k] += n
        owner_tot[o] += n

    last_date, last_f, _, last_countries = saves[-1]
    if kfocus is None:
        kfocus = [t for t, _ in killer_tot.most_common(2)]
    if ofocus is None:
        ofocus = [t for t, _ in owner_tot.most_common(2)]
    filt = ""
    if args.killer or args.owner:
        filt = " [filtered: killer=%s owner=%s]" % (args.killer or "*",
                                                    args.owner or "*")

    # --- monthly curve
    cols = [t for t, _ in killer_tot.most_common(5)]
    if by_month:
        print("\n== monthly convoy losses (stitched from %d saves)%s ==" %
              (len(saves), filt))
        print("month    total  " + "".join("%6s" % t for t in cols) + "  other")
        for m in range(min(covered), max(covered) + 1):
            if m not in covered:
                print("%-8s no data (no passed save covers this month)"
                      % month_dec(m))
                continue
            tot = by_month.get(m, 0)
            per = by_month_killer.get(m, {})
            other = tot - sum(per.get(t, 0) for t in cols)
            print("%-8s %5d  " % (month_dec(m), tot)
                  + "".join("%6d" % per.get(t, 0) for t in cols)
                  + "  %5d" % other)
        print("window total: %d convoys over %d covered months"
              % (sum(by_month.values()), len(covered)))
    else:
        print("\nno sunk_convoys_history records match%s" % (filt or " (empty ledger)"))

    # --- killer -> owner pairs
    if pair:
        print("\n== killer -> victim totals (covered window)%s ==" % filt)
        for (k, o), n in pair.most_common(lim):
            print("  %s -> %-4s %6d" % (k, o, n))
        if len(pair) > lim:
            print("  ... %d more pairs (--limit 0 for all)" % (len(pair) - lim))

    # --- per-save posture for focus tags
    focus = list(dict.fromkeys(kfocus + ofocus))
    print("\n== posture per save (focus: %s) ==" % " ".join(focus))
    print("date        tag  kills_cum  delta  raid  escort  subs  fleet  free_pool")
    prev = {}
    for date, f, _, countries in saves:
        for t in focus:
            c = countries.get(t)
            if c is None or c["kills"] is None:
                print("%-11s %-4s (no country block / no convoys_destroyed)" % (date, t))
                continue
            d = "" if t not in prev else "+%d" % (c["kills"] - prev[t])
            free = c["tlm"].get("wa_tlm_nav_convoys")
            print("%-11s %-4s %7d  %6s  %4d  %6d  %4d  %5d  %9s"
                  % (date, t, c["kills"], d,
                     c["missions"].get("raid", 0), c["missions"].get("escort", 0),
                     c["subs"], c["fleet"],
                     "%d" % free if free is not None else "-"))
            prev[t] = c["kills"]

    # --- submarine losses, reconstructed from EVERY country's kill logs
    seen = {}
    for date, f, _, countries in saves:
        for t, c in countries.items():
            for s in c["sunk"]:
                key = (s.get("country"), s.get("name"), s.get("date"),
                       s.get("killer_country"))
                seen[key] = s
    subs_lost = [s for s in seen.values()
                 if "submarine" in s.get("definition", "")]
    by_sub = [s for s in seen.values()
              if "submarine" in s.get("killer_definition", "")]
    print("\n== submarine losses recorded in surviving killers' logs "
          "(union of %d saves; LOWER BOUND - records die with the killer ship) =="
          % len(saves))
    if subs_lost:
        per = collections.defaultdict(collections.Counter)
        for s in subs_lost:
            per[s.get("country", "?")][s["date"].split(".")[0]] += 1
        years = sorted({y for c2 in per.values() for y in c2})
        print("owner  total  " + "".join("%6s" % y for y in years))
        for o, c2 in sorted(per.items(), key=lambda kv: -sum(kv[1].values())):
            print("%-5s  %5d  " % (o, sum(c2.values()))
                  + "".join("%6d" % c2.get(y, 0) for y in years))
        killers = collections.Counter(s.get("killer_definition", "?")
                                      for s in subs_lost)
        print("killed by: " + "  ".join("%s=%d" % kv
                                        for kv in killers.most_common(6)))
    else:
        print("none recorded")
    if by_sub:
        per = collections.Counter((s.get("killer_country", "?"),
                                   s.get("definition", "?")) for s in by_sub)
        print("warships sunk BY submarines (same logs, same bias): "
              + "  ".join("%s:%s=%d" % (k, d, n)
                          for (k, d), n in per.most_common(8)))
    conv_flag = sum(1 for s in seen.values() if s.get("convoy") == "yes")
    if conv_flag:
        print("NOTE: %d records carry convoy=yes (never observed before - "
              "check them)" % conv_flag)

    # --- aces (latest save, survivors only)
    for t in kfocus:
        c = last_countries.get(t)
        if not c:
            continue
        tot = sum(a[0] for a in c["aces"])
        share = 100.0 * tot / c["kills"] if c["kills"] else 0.0
        print("\n== %s top raiders at %s (alive boats: %d kills = %.0f%% of the "
              "national %d; the rest died with their boats) =="
              % (t, last_date, tot, share, c["kills"] or 0))
        for n, name, d, mission in sorted(c["aces"], reverse=True)[:lim]:
            print("  %4d  %-28s %-20s %s" % (n, name, d, mission))

    # --- regional map (latest save)
    try:
        rnames = rg.load(sg.REPO)
    except Exception:
        rnames = {}
    for t in focus:
        c = last_countries.get(t)
        if not c or not c["regional"]:
            continue
        rows = []
        for r in c["regional"]:
            rows.append((c["danger"].get(r["index"], 0), r))
        rows.sort(key=lambda x: (-x[0], -(x[1].get("required", 0))))
        print("\n== %s convoy regions at %s (danger desc; efficiency absent "
              "~= 1.0 [ASSUMED]) ==" % (t, last_date))
        print("region                              need    eff   danger  last convoy sunk")
        for danger, r in rows[:lim]:
            name = rnames.get(r["index"], ("id %d" % r["index"],))[0]
            print("%-4d %-30s %5s  %5s  %7d  %s"
                  % (r["index"], name[:30],
                     r.get("required", "-"),
                     "%.2f" % r["eff"] if "eff" in r else "-",
                     danger, r.get("last_sunk", "-")))
        if len(rows) > lim:
            print("  ... %d more regions (--limit 0 for all)" % (len(rows) - lim))


if __name__ == "__main__":
    main()
