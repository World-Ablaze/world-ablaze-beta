#!/usr/bin/env python
"""cohort_history.py SAVE... [--tag GER] [--ids]  - Q3: frozen-cohort search across saves.

Per save: every armour-role template with divisions (id, name, live/obsolete, count). Then, across
ALL passed saves: for each armour template, the id set present in EVERY save on that same template
(`constant ids`), and the composition diff of each fielded armour template against the main park
template of the LAST-but-reference choice: the live medium_armor template with most divisions in the
save named by --ref (default: the save dated 1943.4 if passed, else the last one)."""
import sys, collections
import wa_armor_lib as L

argv = sys.argv[1:]
tag, show_ids, ref_name = "GER", False, None
files = []
i = 0
while i < len(argv):
    a = argv[i]
    if a == "--tag": tag = argv[i + 1]; i += 2; continue
    if a == "--ref": ref_name = argv[i + 1]; i += 2; continue
    if a == "--ids": show_ids = True; i += 1; continue
    files.append(a); i += 1

runs = [L.load(f, tag) for f in files]
runs.sort(key=lambda r: L.sg.date_key(r["meta"].get("date", "0")))
per_save = []
for r in runs:
    bt = L.divs_by_template(r)
    arm = {tid: set(ids) for tid, ids in bt.items()
           if tid in r["templates"] and L.is_armour_template(r["templates"][tid])}
    per_save.append(arm)
    tot = sum(len(v) for v in bt.values())
    print("=== %s date=%s closure %d vs army %s %s" % (r["file"], r["meta"].get("date"), tot, r.get("army_count"),
          "OK" if tot == r.get("army_count") else "MISMATCH"))
    for tid, ids in sorted(arm.items()):
        t = r["templates"][tid]
        print("   #%d '%s' role=%s %s %s divisions=%d" % (tid, t["name"], t["role"], L.split_label(t),
              ("OBSOLETE@%s" % t["obsolete_change_date"]) if t["obsolete"] else "live", len(ids)))

ref = None
for r in runs:
    if ref_name and r["file"] == ref_name: ref = r
if ref is None:
    ref = next((r for r in runs if (r["meta"].get("date") or "").startswith("1943.4.")), runs[-1])
rbt = L.divs_by_template(ref)
cands = [(len(ids), tid) for tid, ids in rbt.items() if tid in ref["templates"]
         and ref["templates"][tid]["role"] == "medium_armor" and not ref["templates"][tid]["obsolete"]]
park = max(cands)[1]
P = ref["templates"][park]
print("\nMAIN PARK (in %s): #%d '%s' divisions=%d" % (ref["file"], park, P["name"], len(rbt[park])))

all_tids = set().union(*[set(a) for a in per_save])
print("\nCONSTANT IDS (on the same template in every one of the %d saves):" % len(runs))
for tid in sorted(all_tids):
    sets = [a.get(tid, set()) for a in per_save]
    const = set.intersection(*sets)
    union = set.union(*sets)
    counts = [len(s) for s in sets]
    name = next(r["templates"][tid]["name"] for r in runs if tid in r["templates"])
    print("   #%d '%s': per-save counts=%s  constant=%d  ever=%d%s" % (tid, name, counts, len(const), len(union),
          ("  ids=" + str(sorted(const))) if show_ids else ""))
    # where did the non-constant ones go
    if const != union:
        for did in sorted(union - const):
            trail = []
            for r in runs:
                d = r["divisions"].get(did)
                trail.append("gone" if d is None else str(d["tid"]))
            print("        id %d trail: %s" % (did, " > ".join(trail)))

print("\nCOMPOSITION DIFF vs main park #%d (template: -missing/+extra, all three slots):" % park)
seen = {}
for r in runs:
    for tid, t in r["templates"].items():
        if L.is_armour_template(t) and tid in all_tids and tid != park:
            seen[tid] = t
for tid, t in sorted(seen.items()):
    diffs = []
    for slot in ("regiments", "regimental_support", "support"):
        keys = set(P[slot]) | set(t[slot])
        for k in sorted(keys):
            if P[slot][k] != t[slot][k]:
                diffs.append("%s.%s: park %d / this %d" % (slot, k, P[slot][k], t[slot][k]))
    print("   #%d '%s':" % (tid, t["name"]))
    for d in diffs: print("        " + d)
    allk = set(t["support"]) | set(t["regimental_support"]) | set(t["regiments"])
    print("        heavy_armor_company_divisional=%s  maintenance=%s  TD=%s" % (
        "yes" if "heavy_armor_company_divisional" in t["support"] else "NO",
        [k for k in allk if "maintenance" in k] or "NONE",
        sorted(k for k in allk if "tank_destroyer" in k) or "NONE"))
