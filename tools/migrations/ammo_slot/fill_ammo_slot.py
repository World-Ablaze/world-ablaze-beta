#!/usr/bin/env python3
"""[ammo-slot-designs] Write ammo_type_slot explicitly into every AI tank design.

`ammo_type_slot` is `required = yes` on every tank chassis, but no design in
common/ai_equipment/ names it, so every AI design leans on the chassis
`default_modules` for a slot the engine demands (vanilla's own designs name
every slot, `special_type_slot_N = empty` included).

The module written is the chassis' own `default_modules` ammo entry, which is
APCR wherever APCR is legal (360 of 541 designs) and the best legal fallback
where `forbid_equipment_type` bars it - SPG/flame/amphibious cannot take APCR,
SPAA takes the AA shell, machine-gun tanks take bullets.

Also deletes the commented `#special_type_slot_N = ammo_*` lines: ammo does not
live in a special slot (those accept tank_special_module / tank_radio_module
only), so uncommenting one would break the design match.

Usage:  python tools/migrations/ammo_slot/fill_ammo_slot.py [--apply] [--check]
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


def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8-sig", errors="replace").read()


def strip_comments(text):
    return "\n".join(l.split("#", 1)[0] for l in text.split("\n"))


def chassis_table():
    """chassis name -> {'default': ammo module or None, 'parent': archetype or None}"""
    out = {}
    for f in CHASSIS_FILES:
        lines = strip_comments(read(f)).split("\n")
        depth = 0
        cur = None
        cur_depth = None
        in_default = False
        for line in lines:
            opens, closes = line.count("{"), line.count("}")
            m = re.match(r'\s*([A-Za-z_][\w.]*)\s*=\s*\{\s*$', line)
            if m and depth == 1 and cur is None:
                cur, cur_depth = m.group(1), depth
                out.setdefault(cur, {"default": None, "parent": None})
            elif cur is not None:
                if re.match(r'\s*default_modules\s*=\s*\{', line):
                    in_default = True
                elif in_default and closes and not opens:
                    in_default = False
                elif in_default:
                    a = re.match(r'\s*ammo_type_slot\s*=\s*([\w.]+)', line)
                    if a:
                        out[cur]["default"] = a.group(1)
                else:
                    p = re.match(r'\s*archetype\s*=\s*([\w.]+)', line)
                    if p:
                        out[cur]["parent"] = p.group(1)
            depth += opens - closes
            if cur is not None and depth <= cur_depth:
                cur, cur_depth, in_default = None, None, False
    return out


def resolve_default(table, name):
    seen = set()
    while name in table and name not in seen:
        seen.add(name)
        if table[name]["default"]:
            return table[name]["default"]
        name = table[name]["parent"]
    return None


BLOCK_OPEN = re.compile(r'^(\s*)([A-Za-z_][\w.]*)\s*=\s*\{\s*$')
STRAY = re.compile(r'^\s*#+\s*special_type_slot_\d\s*=\s*ammo_[\w.]+\s*$')


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


def process(path, table, report):
    raw = open(path, "rb").read()
    if raw[:3] == b"\xef\xbb\xbf":
        report.append(("BOM", path, 0, "file carries a UTF-8 BOM - refusing"))
        return None
    nl = "\r\n" if b"\r\n" in raw else "\n"
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
    bl = blocks(lines)
    edits = []

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
        ammo = resolve_default(table, typ)
        if ammo is None:
            report.append(("NO-AMMO", path, tv[1] + 1, "%s: no ammo_type_slot default" % typ))
            continue
        body = [lines[i].split("#", 1)[0] for i in range(mods[1] + 1, mods[2])]
        if any(re.match(r'\s*ammo_type_slot\s*=', x) for x in body):
            continue

        at = mods[2]
        for i in range(mods[1] + 1, mods[2]):
            code = lines[i].split("#", 1)[0]
            if re.match(r'\s*suspension_type_slot\s*=', code):
                at = i + 1
                break
            if re.match(r'\s*special_type_slot_\d\s*=', code) and at == mods[2]:
                at = i
        indent = "\t\t\t\t"
        if mods[2] > mods[1] + 1:
            indent = re.match(r'(\s*)', lines[mods[1] + 1]).group(1)
        edits.append((at, "insert", indent + "ammo_type_slot = " + ammo))

        design = min((x for x in bl if x[3] == tv[3] - 1 and x[1] < tv[1] < x[2]),
                     key=lambda x: tv[1] - x[1], default=None)
        if design:
            am = child(bl, design, "allowed_modules")
            if am:
                have = [lines[i].split("#", 1)[0].strip() for i in range(am[1] + 1, am[2])]
                if ammo not in have:
                    ind = "\t\t\t"
                    if am[2] > am[1] + 1:
                        ind = re.match(r'(\s*)', lines[am[1] + 1]).group(1)
                    edits.append((am[2], "insert", ind + ammo))

    for i, line in enumerate(lines):
        if STRAY.match(line):
            edits.append((i, "delete", None))

    if not edits:
        return None
    dels = {i for i, k, _ in edits if k == "delete"}
    ins = {}
    for i, k, t in edits:
        if k == "insert":
            ins.setdefault(i, []).append(t)
    out = []
    for i, line in enumerate(lines):
        out.extend(ins.get(i, []))
        if i not in dels:
            out.append(line)
    out.extend(ins.get(len(lines), []))
    return nl.join(out).encode("utf-8"), sum(len(v) for v in ins.values()), len(dels)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 2 if any file would change")
    a = ap.parse_args()
    table = chassis_table()
    report, dirty, tot_i, tot_d = [], 0, 0, 0
    for path in sorted(glob.glob(os.path.join(ROOT, DESIGN_GLOB))):
        r = process(path, table, report)
        if not r:
            continue
        data, ni, nd = r
        dirty += 1
        tot_i += ni
        tot_d += nd
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        print("%-34s +%3d lines  -%3d stray" % (rel, ni, nd))
        if a.apply:
            open(path, "wb").write(data)
    for kind, path, ln, msg in report:
        print("  %-8s %s:%d %s" % (kind, os.path.relpath(path, ROOT), ln, msg), file=sys.stderr)
    print("\n%d files, +%d lines, -%d stray lines%s"
          % (dirty, tot_i, tot_d, " (APPLIED)" if a.apply else " (dry run)"))
    if a.check and dirty:
        return 2
    return 1 if any(k == "BOM" for k, *_ in report) else 0


if __name__ == "__main__":
    sys.exit(main())
