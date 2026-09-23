#!/usr/bin/env python
"""q_reference.py SAVE [TAG]  - Q2: every armour-role template of TAG (default GER) in one save:
id, name, role, live/obsolete, full composition, deployed divisions and their ids, training queue,
plus the closure test (divisions per template vs total deployed) and the role census."""
import sys, collections
import wa_armor_lib as L

def main():
    save = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else "GER"
    r = L.load(save, tag)
    m = r["meta"]
    print("FILE %s date=%s id=%s version=%s player=%s" % (r["file"], m.get("date"), m.get("game_unique_id"), m.get("version"), m.get("player")))
    print("FLAGS", r["flags"])
    bt = L.divs_by_template(r)
    print("deployed divisions=%d  templates(country==%s)=%d  own_template_ids=%d alive=%s" % (
        len(r["divisions"]), tag, len(r["templates"]), len(r["own_template_ids"]), r["alive"]))
    roles = collections.Counter()
    for tid, ids in bt.items():
        t = r["templates"].get(tid)
        roles[(t or {}).get("role")] += len(ids)
    print("ROLE CENSUS (divisions):", dict(roles), "sum=%d" % sum(roles.values()))
    missing = [tid for tid in bt if tid not in r["templates"]]
    print("division template ids not in %s templates: %s" % (tag, missing))
    other_keys = set()
    for tid, t in sorted(r["templates"].items()):
        other_keys |= t["other_keys"]
        if not L.is_armour_template(t):
            continue
        ids = sorted(bt.get(tid, []))
        print("\n#%d  %s  role=%s  %s%s  in_own_list=%s  split(med+mod)=%s  divisions=%d" % (
            tid, t["name"], t["role"], "OBSOLETE" if t["obsolete"] else "live",
            (" since " + t["obsolete_change_date"]) if t["obsolete_change_date"] else "",
            tid in r["own_template_ids"], L.split_label(t), len(ids)))
        print("   regiments: " + L.comp_str(t["regiments"]))
        print("   regimental_support: " + L.comp_str(t["regimental_support"]))
        print("   support: " + L.comp_str(t["support"]))
        print("   division ids: %s" % ids)
    print("\nTRAINING QUEUE (armour templates):")
    for q in r["queue"]:
        t = r["templates"].get(q["tid"])
        if t and L.is_armour_template(t):
            print("   #%s %s role=%s amount=%s lines=%d" % (q["tid"], q.get("name"), q.get("role"), q.get("amount"), q["n_lines"]))
    print("other template keys seen:", sorted(other_keys))

main()
