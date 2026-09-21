#!/usr/bin/env python
"""read_run.py <reference_save> <run_save>... [--tag GER] [--park TID] [--ids]

Reads a medium -> modern armour switch run against a reference save.

Reference save: finds the MAIN PARK template (live, role medium_armor, most deployed divisions;
override with --park TID) and the other fielded armour templates ("other cohorts"); records the
division ids on each. Each run save: meta (date, version + checksum, campaign id), the two flags,
where the tracked ids are now (per template, with medium+modern battalion split and live/obsolete),
every armour-role template (live/obsolete, obsolete_change_date, divisions), recruits (ids absent
from the reference) on armour templates, the armour training queue, mean chassis per fielded
tracked division, free chassis stock, chassis production lines (active/requested factories), and
the closure test (sum per template == independent `army` count).
Bare filenames resolve against the default save dir. Output is plain text, one block per save.
"""
import sys, collections, argparse
import wa_armor_lib as L


def tdesc(res, tid):
    t = res["templates"].get(tid)
    if t is None:
        return "#%s (absent from save)" % tid
    st = "OBSOLETE@%s" % t["obsolete_change_date"] if t["obsolete"] else "live"
    return "#%d '%s' role=%s %s %s" % (tid, t["name"], t["role"], L.split_label(t), st)


def where(res, ids):
    c = collections.Counter()
    gone = []
    for i in ids:
        d = res["divisions"].get(i)
        if d is None:
            gone.append(i)
        else:
            c[d["tid"]] += 1
    return c, gone


def mean_chassis(res, ids):
    tot, n = collections.Counter(), 0
    for i in ids:
        d = res["divisions"].get(i)
        if d is None:
            continue
        n += 1
        tot.update(L.div_chassis(d, res["defs"]))
    return {k: (tot[k] / n if n else 0.0) for k in ("medium", "medium_gun", "modern", "medium_td", "heavy")}, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference"); ap.add_argument("runs", nargs="*")
    ap.add_argument("--tag", default="GER"); ap.add_argument("--park", type=int)
    ap.add_argument("--ids", action="store_true", help="print division id lists")
    a = ap.parse_args()
    ref = L.load(a.reference, a.tag)
    bt = L.divs_by_template(ref)
    arm = {tid: sorted(ids) for tid, ids in bt.items()
           if tid in ref["templates"] and L.is_armour_template(ref["templates"][tid])}
    park = a.park
    if park is None:
        cands = [(len(ids), tid) for tid, ids in arm.items()
                 if ref["templates"][tid]["role"] == "medium_armor" and not ref["templates"][tid]["obsolete"]]
        park = max(cands)[1] if cands else None
    print("REFERENCE %s date=%s version=%s id=%s" % (ref["file"], ref["meta"].get("date"),
          ref["meta"].get("version"), ref["meta"].get("game_unique_id")))
    print("  main park: %s  divisions=%d" % (tdesc(ref, park), len(arm.get(park, []))))
    for tid, ids in sorted(arm.items()):
        if tid != park:
            print("  other cohort: %s  divisions=%d" % (tdesc(ref, tid), len(ids)))
    if a.ids:
        for tid, ids in sorted(arm.items()):
            print("  ids #%d: %s" % (tid, ids))
    ref_ids = set(ref["divisions"])
    for f in [a.reference] + a.runs:
        r = ref if f == a.reference else L.load(f, a.tag)
        m = r["meta"]
        print("\n=== %s date=%s version=%s id=%s alive=%s" % (r["file"], m.get("date"), m.get("version"),
              (m.get("game_unique_id") or "")[:8], r["alive"]))
        if (m.get("game_unique_id") != ref["meta"].get("game_unique_id")):
            print("  !! DIFFERENT CAMPAIGN ID than the reference")
        for k, v in r["flags"].items():
            print("  flag %s = %s (set %s)" % (k, v.get("value"), v.get("date")))
        rbt = L.divs_by_template(r)
        tot = sum(len(v) for v in rbt.values())
        print("  closure: per-template sum=%d  army count=%s  %s" % (tot, r.get("army_count"),
              "OK" if tot == r.get("army_count") else "MISMATCH"))
        for label, tid in [("PARK", park)] + [("cohort", t) for t in sorted(arm) if t != park]:
            ids = arm.get(tid, [])
            c, gone = where(r, ids)
            mc, n = mean_chassis(r, ids)
            print("  %s ref#%s (%d ids): fielded=%d gone=%d%s" % (label, tid, len(ids), n, len(gone),
                  (" " + str(gone)) if gone and a.ids else ""))
            for t2, k in c.most_common():
                sub = [i for i in ids if i in r["divisions"] and r["divisions"][i]["tid"] == t2]
                m2, _ = mean_chassis(r, sub)
                print("      %2d on %s   [mean medium=%.1f gun=%.1f modern=%.1f]%s" % (k, tdesc(r, t2),
                      m2["medium"], m2["medium_gun"], m2["modern"], (" ids=" + str(sub)) if a.ids else ""))
            print("      mean chassis/div: medium=%.1f (of which gun tanks=%.1f) modern=%.1f medium_td=%.1f heavy=%.1f" % (
                mc["medium"], mc["medium_gun"], mc["modern"], mc["medium_td"], mc["heavy"]))
        print("  armour-role templates in save:")
        for tid, t in sorted(r["templates"].items()):
            if L.is_armour_template(t):
                print("      %s  divisions=%d" % (tdesc(r, tid), len(rbt.get(tid, []))))
        rec = collections.Counter()
        rec_ids = collections.defaultdict(list)
        for did, d in r["divisions"].items():
            if did not in ref_ids:
                t = r["templates"].get(d["tid"])
                if t and L.is_armour_template(t):
                    rec[d["tid"]] += 1; rec_ids[d["tid"]].append(did)
        print("  recruits (ids absent from reference) on armour templates: %d" % sum(rec.values()))
        for t2, k in rec.most_common():
            mc, n = mean_chassis(r, rec_ids[t2])
            print("      %2d on %s  (mean medium=%.1f modern=%.1f)%s" % (k, tdesc(r, t2), mc["medium"], mc["modern"],
                  (" ids=" + str(sorted(rec_ids[t2]))) if a.ids else ""))
        print("  armour training queue:")
        for q in r["queue"]:
            t = r["templates"].get(q["tid"])
            if t and L.is_armour_template(t):
                print("      %s  conveyor amount=%s lines=%d" % (tdesc(r, q["tid"]), q.get("amount"), q["n_lines"]))
        sc = L.stock_chassis(r)
        so = L.stock_chassis(r, a.tag)
        print("  free stock (all creators / own-built): modern=%.0f/%.0f medium=%.0f/%.0f (gun tanks %.0f/%.0f) medium_td=%.0f/%.0f heavy=%.0f/%.0f" % (
            sc["modern"], so["modern"], sc["medium"], so["medium"], sc["medium_gun"], so["medium_gun"],
            sc["medium_td"], so["medium_td"], sc["heavy"], so["heavy"]))
        lb = L.lines_by_bucket(r)
        for b in ("modern", "medium", "medium_td", "heavy"):
            o = lb.get(b, {"n": 0, "active": 0, "requested": 0})
            print("  lines %-9s n=%d active=%d requested=%d" % (b, o["n"], o["active"], o["requested"]))
        for ln in r["lines"]:
            if L.chassis_bucket(ln.get("defname") or ""):
                # a line with no `active_factories=` key is a queued line holding no factory (ASSUMED = 0)
                print("      line %s active=%s requested=%s" % (ln["defname"], ln.get("active_factories", "absent"), ln.get("requested_factories")))

main()
