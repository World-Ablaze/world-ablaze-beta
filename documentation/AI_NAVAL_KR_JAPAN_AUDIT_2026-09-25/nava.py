import json, glob, os, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MAJ = ["GER", "ITA", "JAP", "ENG", "FRA", "USA", "SOV"]
MIS = {"0": "none/hold", "1": "patrol", "2": "strike", "3": "raid", "4": "escort", "5": "mine5",
       "6": "mine6", "7": "train", "8": "reserve", "9": "inv-support?", None: "(no mission block)"}
IDLE = {"0", "7", "8", None}
ABBR = {"carrier": "CV", "light_carrier": "CVL", "battleship": "BB", "battle_cruiser": "BC",
        "heavy_cruiser": "CA", "light_cruiser": "CL", "destroyer": "DD", "frigate": "FF",
        "submarine": "SS", "cruiser_submarine": "SSC"}
W = {"carrier": 10, "battleship": 10, "battle_cruiser": 10, "heavy_cruiser": 5, "light_carrier": 5,
     "light_cruiser": 3, "destroyer": 1, "frigate": 1, "submarine": 1, "cruiser_submarine": 1}


def dk(d):
    return tuple(int(x) for x in d.split(".")[:3])


def load():
    camps = collections.defaultdict(list)
    for p in glob.glob(os.path.join(HERE, "navjson", "*.json")):
        d = json.load(open(p))
        camps[d["campaign"][:8]].append(d)
    for c in camps:
        camps[c].sort(key=lambda d: dk(d["date"]))
    return camps


def comp(c):
    return " ".join(f"{ABBR.get(k,k)}{v}" for k, v in sorted(c.items(), key=lambda kv: -W.get(kv[0], 0)))


def totals(fleets):
    t = collections.Counter()
    for f in fleets:
        for tf in f["tfs"]:
            t.update(tf["ships"])
    return t


def strength(fleets, mode):
    t = totals(fleets)
    return sum(v * (W.get(k, 1) if mode == "w" else 1) for k, v in t.items())


def meets_min(c):
    return c.get("carrier", 0) >= 2 and c.get("battleship", 0) >= 2 and c.get("light_cruiser", 0) >= 10


out = []
P = out.append
camps = load()
for cid, saves in camps.items():
    P(f"\n# Campaign {cid}: {len(saves)} saves {saves[0]['date']} .. {saves[-1]['date']}\n")
    # ---- all strike TFs anywhere in the campaign
    P("## Q-N2a. Every task force with mission=2 (strike), all countries, all saves\n")
    P("| date | tag | fleet | TF ships | TF meets 2CV+2BB+10CL | country total CV/BB/CL | country meets |")
    P("|---|---|---|---|---|---|---|")
    nstrike = 0
    for d in saves:
        for tag, fl in sorted(d["countries"].items()):
            t = totals(fl)
            for f in fl:
                for tf in f["tfs"]:
                    if tf["mission"] == "2":
                        nstrike += 1
                        P(f"| {d['date'][:-2]} | {tag} | {f['name']} | {comp(tf['ships'])} | {meets_min(tf['ships'])} | "
                          f"{t.get('carrier',0)}/{t.get('battleship',0)}/{t.get('light_cruiser',0)} | {meets_min(t)} |")
    P(f"\nTotal strike-TF observations: {nstrike}\n")
    # mission id census
    cen = collections.Counter()
    for d in saves:
        for tag, fl in d["countries"].items():
            for f in fl:
                for tf in f["tfs"]:
                    cen[tf["mission"]] += 1
    P("Mission-id census (TF observations over all saves, all countries): " +
      ", ".join(f"{k}={v}" for k, v in sorted(cen.items(), key=lambda kv: str(kv[0]))) + "\n")
    # TFs that satisfy the strike min composition, whatever their mission
    P("## Q-N2c. Task forces that satisfy StrikeForce_1 min (>=2CV,>=2BB,>=10CL), by mission (TF-observations; distinct tag list)\n")
    sm = collections.Counter()
    smt = collections.defaultdict(set)
    first = {}
    regs = collections.Counter()
    for d in saves:
        for tag, fl in d["countries"].items():
            for f in fl:
                for tf in f["tfs"]:
                    if meets_min(tf["ships"]):
                        k = MIS.get(tf["mission"], tf["mission"])
                        sm[k] += 1
                        smt[k].add(tag)
                        first.setdefault((tag, k), d["date"][:-2])
                        regs[(k, "fleet has regions" if f["regions"] else "fleet no regions")] += 1
    for k, v in sm.most_common():
        P(f"- {k}: {v} TF-obs, tags {sorted(smt[k])}")
    P("- fleet-region split: " + ", ".join(f"{a}/{b}={v}" for (a, b), v in sorted(regs.items())))
    P("- first save per (tag, mission): " + ", ".join(f"{t}:{m}@{dd}" for (t, m), dd in sorted(first.items())) + "\n")
    # mission-0 fleets with regions?
    r0 = collections.Counter()
    for d in saves:
        for tag, fl in d["countries"].items():
            for f in fl:
                for tf in f["tfs"]:
                    r0[(MIS.get(tf["mission"], tf["mission"]), bool(f["regions"]))] += 1
    P("Mission x fleet-has-strategic_region (TF obs): " + ", ".join(f"{a}/{'reg' if b else 'noreg'}={v}" for (a, b), v in sorted(r0.items(), key=str)) + "\n")
    # ---- per-major snapshots
    P("## Q-N2b. Majors at the sampled dates\n")
    targets = [(1939, 9), (1941, 6), (1942, 6), (1943, 6), (1944, 3)]
    for (y, m) in targets:
        cand = [d for d in saves if dk(d["date"])[:2] == (y, m)]
        if not cand:
            continue
        d = cand[0]
        P(f"### {d['date']} ({d['file']})\n")
        P("| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |")
        P("|---|---|---|---|---|---|---|---|")
        for tag in MAJ:
            fl = d["countries"].get(tag, [])
            t = totals(fl)
            by = collections.Counter()
            tfc = collections.Counter()
            for f in fl:
                for tf in f["tfs"]:
                    by[tf["mission"]] += sum(tf["ships"].values())
                    tfc[MIS.get(tf["mission"], tf["mission"])] += 1
            act = sum(v for k, v in by.items() if k not in IDLE)
            P(f"| {tag} | {comp(t)} (n={sum(t.values())}) | {meets_min(t)} | {act} | {by.get('0',0)+by.get(None,0)} | {by.get('7',0)} | {by.get('8',0)} | "
              + ", ".join(f"{k}:{v}" for k, v in sorted(tfc.items())) + " |")
        P("")
        P("Task-force detail (grouped: mission x composition -> count of TFs)\n")
        for tag in MAJ:
            fl = d["countries"].get(tag, [])
            g = collections.Counter()
            for f in fl:
                for tf in f["tfs"]:
                    g[(MIS.get(tf["mission"], tf["mission"]), comp(tf["ships"]))] += 1
            P(f"- **{tag}**: " + ("; ".join(f"{k[0]} [{k[1]}] x{v}" for k, v in sorted(g.items())) or "no fleets"))
        P("")
    # ---- Q-N3
    for mode, lab in (("w", "weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1"), ("h", "plain hull count")):
        P(f"## Q-N3 ({lab}) - ratio = sum(enemy strength) / own strength, monthly\n")
        series = {}
        for tag in MAJ:
            rows = []
            for d in saves:
                enemies = sorted({b if a == tag else a for a, b in map(tuple, d["wars"]) if tag in (a, b)})
                if not enemies:
                    continue
                own = strength(d["countries"].get(tag, []), mode)
                en = sum(strength(d["countries"].get(e, []), mode) for e in enemies)
                ratio = (en / own) if own else float("inf")
                post = "superior" if ratio < 0.8 else ("inferior" if ratio > 1.5 else "neutral")
                rows.append((d["date"][:-2], own, en, ratio, post, len(enemies)))
            series[tag] = rows
        P("| tag | war-months | superior | neutral | inferior | flips | flaps(<=3mo) |")
        P("|---|---|---|---|---|---|---|")
        detail = []
        for tag in MAJ:
            rows = series[tag]
            n = len(rows)
            c = collections.Counter(r[4] for r in rows)
            flips = []
            flaps = []
            for i in range(1, n):
                if rows[i][4] != rows[i - 1][4]:
                    flips.append(f"{rows[i][0]} {rows[i-1][4][:3]}->{rows[i][4][:3]}")
                    prev = rows[i - 1][4]
                    for j in range(i + 1, min(n, i + 4)):
                        if rows[j][4] == prev:
                            flaps.append(f"{rows[i][0]}..{rows[j][0]}")
                            break
            pct = lambda k: f"{c.get(k,0)} ({100*c.get(k,0)/n:.0f}%)" if n else "-"
            P(f"| {tag} | {n} | {pct('superior')} | {pct('neutral')} | {pct('inferior')} | {len(flips)} | {len(flaps)} |")
            detail.append((tag, rows, flips, flaps))
        P("")
        for tag, rows, flips, flaps in detail:
            P(f"### {tag} ({lab})\n")
            P("Flips: " + ("; ".join(flips) or "none"))
            P("Flaps: " + ("; ".join(flaps) or "none") + "\n")
            # compress runs
            P("| from | to | posture | ratio range | own | enemies' |")
            P("|---|---|---|---|---|---|")
            i = 0
            while i < len(rows):
                j = i
                while j + 1 < len(rows) and rows[j + 1][4] == rows[i][4]:
                    j += 1
                rs = [r[3] for r in rows[i:j + 1]]
                fmt = lambda x: "inf" if x == float("inf") else f"{x:.2f}"
                P(f"| {rows[i][0]} | {rows[j][0]} | {rows[i][4]} | {fmt(min(rs))}-{fmt(max(rs))} | {rows[i][1]}..{rows[j][1]} | {rows[i][2]}..{rows[j][2]} |")
                i = j + 1
            P("")
    json.dump({t: s for t, s in series.items()}, open(os.path.join(HERE, f"series_{cid}.json"), "w"))

open(os.path.join(HERE, "measure_n2_n3_body.md"), "w", encoding="utf-8").write("\n".join(out))
print("ok", len(out))
