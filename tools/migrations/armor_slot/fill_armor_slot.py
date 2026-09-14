#!/usr/bin/env python3
"""[armor-grade-designs] Write armor_type_slot (steel grade) into every AI tank design.

The armour slots changed shape (commit 6291e3b5b0): `armor_type_slot` is now
`required = yes` and accepts only the two steel grades (`tank_armor_type`:
tank_strengthend_armor / tank_weakened_armor); the armour PLATES moved to the
new optional `extra_armor_slot` (`tank_extra_armor`). Before that, the plates
lived in `armor_type_slot` and the slot was optional, which is how 231 designs
came to say `armor_type_slot = tank_armor_plate_N` and 106 to say
`armor_type_slot = empty` - both illegal against the new chassis.

Per design, inside target_variant.modules:
  * `armor_type_slot = tank_armor_plate_N`  ->  `extra_armor_slot = tank_armor_plate_N`
    (only when the chassis carries extra_armor_slot; else reported PLATE-NO-SLOT)
  * `armor_type_slot = empty`               ->  `armor_type_slot = <grade>`
  * no armor_type_slot line                 ->  one is inserted after ammo_type_slot
  * `allowed_modules` gains <grade> when missing (sister rule of fill_ammo_slot.py).

<grade> is chosen by --grade: `auto` (default) takes the chassis' own
`default_modules` entry, falling back to --fallback (tank_strengthend_armor)
for the chassis that declare the slot but no default; a module name forces it
everywhere. A design that already names a grade keeps it (the `__wa` twins of
tools/gen/gen_grade_pairs.py carry tank_weakened_armor on purpose).
Idempotent; a second run changes nothing.

Usage:  python tools/migrations/armor_slot/fill_armor_slot.py
            [--grade auto|tank_strengthend_armor|tank_weakened_armor]
            [--fallback MODULE] [--apply] [--check] [--out DIR]
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CHASSIS_FILES = ["common/units/equipment/tank_chassis.txt",
                 "common/units/equipment/x_tank_chassis.txt"]
DESIGN_GLOB = "common/ai_equipment/*_tank.txt"
GRADES = ("tank_strengthend_armor", "tank_weakened_armor")
PLATE = re.compile(r'^(\s*)armor_type_slot\s*=\s*(tank_armor_plate_\d+)\s*$')
EMPTY = re.compile(r'^(\s*)armor_type_slot\s*=\s*empty\s*$')
ANY_ARMOR = re.compile(r'^\s*armor_type_slot\s*=\s*([\w.]+)\s*$')


def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8-sig", errors="replace").read()


def strip_comments(text):
    return "\n".join(l.split("#", 1)[0] for l in text.split("\n"))


def chassis_table():
    """name -> {'parent', 'own_slots' (dict slot->required) or None, 'own_default' or None}.

    A chassis that declares its own module_slots REPLACES the archetype's; one
    that declares none inherits them. Same for default_modules.
    """
    out = {}
    for f in CHASSIS_FILES:
        lines = strip_comments(read(f)).split("\n")
        depth, cur, sect, slot = 0, None, None, None
        for line in lines:
            opens, closes = line.count("{"), line.count("}")
            m = re.match(r'\s*([A-Za-z_][\w.]*)\s*=\s*\{\s*$', line)
            if depth == 1 and m and cur is None:
                cur = m.group(1)
                out[cur] = {"parent": None, "own_slots": None, "own_default": None, "has_dm": False}
            elif cur is not None:
                if depth == 2 and m and m.group(1) == "module_slots":
                    sect, out[cur]["own_slots"] = "ms", {}
                elif depth == 2 and m and m.group(1) == "default_modules":
                    sect, out[cur]["has_dm"] = "dm", True
                elif depth == 3 and m and sect == "ms":
                    slot = m.group(1)
                    out[cur]["own_slots"][slot] = None
                if sect == "ms" and slot:
                    r = re.match(r'\s*required\s*=\s*(\w+)', line)
                    if r:
                        out[cur]["own_slots"][slot] = r.group(1)
                if sect == "dm":
                    a = re.match(r'\s*armor_type_slot\s*=\s*([\w.]+)', line)
                    if a:
                        out[cur]["own_default"] = a.group(1)
                p = re.match(r'\s*archetype\s*=\s*([\w.]+)', line)
                if p:
                    out[cur]["parent"] = p.group(1)
            depth += opens - closes
            if depth < 3:
                slot = None
            if depth < 2 or (depth == 2 and closes):
                sect = None
            if cur is not None and depth <= 1:
                cur = None
    return out


def effective(table, name, key, marker):
    seen = set()
    while name in table and name not in seen:
        seen.add(name)
        if table[name][marker]:
            return table[name][key]
        name = table[name]["parent"]
    return None


def eff_slots(table, name):
    return effective(table, name, "own_slots", "own_slots") or {}


def eff_default(table, name):
    return effective(table, name, "own_default", "has_dm")


BLOCK_OPEN = re.compile(r'^(\s*)([A-Za-z_][\w.]*)\s*=\s*\{\s*$')


def blocks(lines):
    """(key, start, end, depth) for every `key = {` block; end is its `}` line."""
    stack, found, depth = [], [], 0
    for i, line in enumerate(lines):
        code = line.split("#", 1)[0]
        m = BLOCK_OPEN.match(code.rstrip("\r"))
        if m:
            stack.append((m.group(2), i, depth))
        depth += code.count("{") - code.count("}")
        while stack and depth <= stack[-1][2]:
            k, s, d = stack.pop()
            found.append((k, s, i, d))
    return found


def child(bl, parent, key):
    _, ps, pe, pd = parent
    for k, s, e, d in bl:
        if k == key and d == pd + 1 and ps < s < pe:
            return (k, s, e, d)
    return None


def process(path, table, grade_opt, fallback, report):
    raw = open(path, "rb").read()
    if raw[:3] == b"\xef\xbb\xbf":
        report.append(("BOM", path, 0, "file carries a UTF-8 BOM - refusing"))
        return None
    nl = "\r\n" if b"\r\n" in raw else "\n"
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
    bl = blocks(lines)
    replace, insert = {}, {}
    stats = {"moved": 0, "empty": 0, "inserted": 0, "allowed": 0, "fallback": 0}

    for tv in [b for b in bl if b[0] == "target_variant"]:
        mods = child(bl, tv, "modules")
        if not mods:
            continue
        typ = None
        for i in range(tv[1] + 1, tv[2]):
            if mods[1] < i < mods[2]:
                continue
            m = re.match(r'\s*type\s*=\s*([\w.]+)', lines[i].split("#", 1)[0])
            if m:
                typ = m.group(1)
                break
        if typ is None:
            report.append(("NO-TYPE", path, tv[1] + 1, "target_variant without type"))
            continue
        slots = eff_slots(table, typ)
        if "armor_type_slot" not in slots:
            report.append(("NO-SLOT", path, tv[1] + 1, "%s: chassis has no armor_type_slot" % typ))
            continue
        if grade_opt == "auto":
            grade = eff_default(table, typ)
            if grade is None:
                grade = fallback
                stats["fallback"] += 1
                report.append(("NO-DEFAULT", path, tv[1] + 1,
                               "%s: slot required, no chassis default -> %s" % (typ, fallback)))
        else:
            grade = grade_opt

        have_grade = False
        ammo_at = susp_at = first_special = None
        for i in range(mods[1] + 1, mods[2]):
            code = lines[i].split("#", 1)[0].rstrip()
            pm = PLATE.match(code)
            if pm:
                if "extra_armor_slot" in slots:
                    replace[i] = pm.group(1) + "extra_armor_slot = " + pm.group(2)
                    stats["moved"] += 1
                else:
                    report.append(("PLATE-NO-SLOT", path, i + 1,
                                   "%s: chassis has no extra_armor_slot for %s" % (typ, pm.group(2))))
                continue
            em = EMPTY.match(code)
            if em:
                replace[i] = em.group(1) + "armor_type_slot = " + grade
                stats["empty"] += 1
                have_grade = True
                continue
            am = ANY_ARMOR.match(code)
            if am:
                if am.group(1) not in GRADES:
                    report.append(("ODD-VALUE", path, i + 1, "armor_type_slot = " + am.group(1)))
                else:
                    grade = am.group(1)  # a design that already names a grade (a `__wa` twin) keeps it
                have_grade = True
                continue
            if re.match(r'\s*ammo_type_slot\s*=', code):
                ammo_at = i
            elif re.match(r'\s*suspension_type_slot\s*=', code):
                susp_at = i
            elif re.match(r'\s*(special_type_slot_\d|extra_armor_slot)\s*=', code) and first_special is None:
                first_special = i
        if not have_grade:
            at = mods[2]
            if ammo_at is not None:
                at = ammo_at + 1
            elif susp_at is not None:
                at = susp_at + 1
            elif first_special is not None:
                at = first_special
            indent = "\t\t\t\t"
            if mods[2] > mods[1] + 1:
                indent = re.match(r'(\s*)', lines[mods[1] + 1]).group(1)
            insert.setdefault(at, []).append(indent + "armor_type_slot = " + grade)
            stats["inserted"] += 1

        design = min((x for x in bl if x[3] == tv[3] - 1 and x[1] < tv[1] < x[2]),
                     key=lambda x: tv[1] - x[1], default=None)
        if design:
            am = child(bl, design, "allowed_modules")
            if am:
                have = [lines[i].split("#", 1)[0].strip() for i in range(am[1] + 1, am[2])]
                if grade not in have:
                    ind = "\t\t\t"
                    if am[2] > am[1] + 1:
                        ind = re.match(r'(\s*)', lines[am[1] + 1]).group(1)
                    insert.setdefault(am[2], []).append(ind + grade)
                    stats["allowed"] += 1
            else:
                report.append(("NO-ALLOWED", path, design[1] + 1, "design without allowed_modules"))

    if not replace and not insert:
        return None
    out = []
    for i, line in enumerate(lines):
        out.extend(insert.get(i, []))
        out.append(replace.get(i, line))
    out.extend(insert.get(len(lines), []))
    return nl.join(out).encode("utf-8"), stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", default="auto", choices=("auto",) + GRADES)
    ap.add_argument("--fallback", default="tank_strengthend_armor", choices=GRADES,
                    help="grade for chassis with a required slot but no default (auto mode)")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 2 if any file would change")
    ap.add_argument("--out", help="write results under DIR instead of in place (validation)")
    a = ap.parse_args()
    table = chassis_table()
    report, dirty = [], 0
    tot = {"moved": 0, "empty": 0, "inserted": 0, "allowed": 0, "fallback": 0}
    for path in sorted(glob.glob(os.path.join(ROOT, DESIGN_GLOB))):
        r = process(path, table, a.grade, a.fallback, report)
        if not r:
            continue
        data, st = r
        dirty += 1
        for k in tot:
            tot[k] += st[k]
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        print("%-34s plate->extra %3d  empty->grade %3d  inserted %3d  allowed +%3d"
              % (rel, st["moved"], st["empty"], st["inserted"], st["allowed"]))
        if a.apply:
            open(path, "wb").write(data)
        elif a.out:
            dst = os.path.join(a.out, os.path.basename(path))
            os.makedirs(a.out, exist_ok=True)
            open(dst, "wb").write(data)
    for kind, path, ln, msg in sorted(set(report)):
        print("  %-13s %s:%d %s" % (kind, os.path.relpath(path, ROOT), ln, msg), file=sys.stderr)
    mode = " (APPLIED)" if a.apply else (" (written to %s)" % a.out if a.out else " (dry run)")
    print("\n%d files: plate->extra %d, empty->grade %d, inserted %d, allowed +%d, fallback %d%s"
          % (dirty, tot["moved"], tot["empty"], tot["inserted"], tot["allowed"], tot["fallback"], mode))
    if a.check and dirty:
        return 2
    return 1 if any(k in ("BOM", "NO-SLOT", "PLATE-NO-SLOT") for k, *_ in report) else 0


if __name__ == "__main__":
    sys.exit(main())
