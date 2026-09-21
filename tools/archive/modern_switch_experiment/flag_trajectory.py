#!/usr/bin/env python
"""flag_trajectory.py SAVE... [--tag GER]  - Q1: per save, date, version string (with its 4-char
checksum), campaign id, and the two armour flags (value + set-date). Header + flags section only
would be cheaper, but this reuses the shared loader so the reading is the same code as read_run.py."""
import sys
import wa_armor_lib as L
args = [a for a in sys.argv[1:] if not a.startswith("--")]
tag = "GER"
if "--tag" in sys.argv:
    tag = sys.argv[sys.argv.index("--tag") + 1]; args.remove(tag)
for f in args:
    r = L.load(f, tag)
    m = r["meta"]
    fl = r["flags"]
    a = fl.get("WA_MEDIUM_ARMOR_TEMPLATE", {}); b = fl.get("WA_AI_TEMPLATES_modern_chassis_earned", {})
    print("%-18s date=%s id=%s version=%s | MEDIUM_ARMOR_TEMPLATE=%s (set %s) | modern_chassis_earned=%s (set %s) | divisions=%s alive=%s" % (
        r["file"], m.get("date"), (m.get("game_unique_id") or "")[:8], m.get("version"),
        a.get("value"), a.get("date"), b.get("value"), b.get("date"), r.get("army_count"), r["alive"]))
