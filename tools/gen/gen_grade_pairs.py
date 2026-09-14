#!/usr/bin/env python3
"""[resource-grade-downshift] Generate the steel-grade / ammunition-grade design twins.

For every AI tank design in common/ai_equipment/*_tank.txt the AI needs a way to
build the SAME design with the cheap modules when a strategic resource is short:
`tank_weakened_armor` instead of `tank_strengthend_armor` (chromium), the plain
`_ap_he` shell instead of `_ap_he_apcr` / `_hvap` (tungsten). The engine will not
create a second, better-matching design on a type that already holds one, so the
only mechanism that works (MEASURED, subject sov-cutting-corners-module) is an
enable-EXCLUSIVE partition: exactly one design per type is enabled in every
shortage state, and the AI redesigns on mismatch.

This tool derives the twins from the base designs and is the ONLY writer of them:
  * base design (and every `__cc` design) gains
        NOT = { WA_AI_EQUIPMENT_should_mount_weak_armor = yes }
        NOT = { WA_AI_EQUIPMENT_should_mount_low_ammo = yes }   (APCR/HVAP designs only)
  * twins `<key>__wa`, `<key>__la`, `<key>__wa_la` (or `__cc_wa` ... for a `__cc` base)
    copy the base with the opposite polarity and the substituted modules; the
    `# WA_EQUIPGEN_*` marker comments are stripped (the evaluator owns the BASE
    priority block; a twin is a derived copy and must never carry its ids twice).

ORDER RULE: twins are a copy of the base as it is NOW. Run this tool AFTER any
`tools/equipment_evaluator` apply; `--check` reports twins that drifted from
their base (exit 2). A rerun deletes every twin and every term it wrote, then
regenerates - idempotent. `--remove` deletes them and writes nothing back.

Usage:  python tools/gen/gen_grade_pairs.py [--dry-run | --apply | --check | --remove]
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DESIGN_GLOB = "common/ai_equipment/*_tank.txt"
WEAK_T = "WA_AI_EQUIPMENT_should_mount_weak_armor"
LOW_T = "WA_AI_EQUIPMENT_should_mount_low_ammo"
CC_T = "WA_AI_EQUIPMENT_should_mount_cutting_corners"
GEN_MARK = "# [resource-grade-downshift] GENERATED twin of "
STRONG, WEAK = "tank_strengthend_armor", "tank_weakened_armor"
TWIN_KEY = re.compile(r"__(?:cc_)?(?:wa|la|wa_la)$")
OUR_TERM = re.compile(r"^\s*(?:NOT = \{ )?(?:%s|%s) = yes(?: \})?\s*$" % (WEAK_T, LOW_T))
CC_TERM = re.compile(r"^\s*(NOT = \{ )?%s = yes( \})?\s*$" % CC_T)
BLOCK_OPEN = re.compile(r"^(\s*)([A-Za-z_][\w.]*)\s*=\s*\{\s*(#.*)?$")
MARKER = re.compile(r"^\s*#\s*WA_EQUIPGEN_(BEGIN|END)\b")


def low_ammo(module):
    for suf in ("_ap_he_apcr", "_hefit_hvap"):
        if module.endswith(suf):
            return module[:-5]
    return None


def blocks(lines):
    """(key, start, end, depth) for every `key = {` block; end is its `}` line."""
    stack, found, depth = [], [], 0
    for i, line in enumerate(lines):
        code = line.split("#", 1)[0]
        m = BLOCK_OPEN.match(line.rstrip("\r"))
        if m and code.count("{") == 1 and code.count("}") == 0:
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


def designs_of(lines):
    bl = blocks(lines)
    out = []
    for b in bl:
        if b[3] == 1 and child(bl, b, "target_variant"):
            out.append(b)
    return bl, sorted(out, key=lambda b: b[1])


def strip_generated(lines):
    """Remove every twin block and every term this tool wrote. Returns new lines."""
    bl, des = designs_of(lines)
    drop = set()
    for d in des:
        if TWIN_KEY.search(d[0]):
            drop.update(range(d[1], d[2] + 1))
            if d[1] > 0 and lines[d[1] - 1].strip().startswith(GEN_MARK.strip()):
                drop.add(d[1] - 1)
            # swallow one blank line after the twin so reruns do not accumulate blanks
            if d[2] + 1 < len(lines) and lines[d[2] + 1].strip() == "":
                drop.add(d[2] + 1)
        else:
            en = child(bl, d, "enable")
            if en:
                body = [i for i in range(en[1] + 1, en[2]) if OUR_TERM.match(lines[i])]
                drop.update(body)
                rest = [i for i in range(en[1] + 1, en[2])
                        if i not in body and lines[i].split("#", 1)[0].strip()]
                if not rest:
                    drop.update(range(en[1], en[2] + 1))
    return [l for i, l in enumerate(lines) if i not in drop]


def design_modules(lines, bl, d):
    tv = child(bl, d, "target_variant")
    mods = child(bl, tv, "modules")
    armor = ammo = None
    typ = None
    for i in range(tv[1] + 1, tv[2]):
        m = re.match(r"\s*type\s*=\s*([\w.]+)", lines[i].split("#", 1)[0])
        if m and not (mods[1] < i < mods[2]):
            typ = m.group(1)
    for i in range(mods[1] + 1, mods[2]):
        code = lines[i].split("#", 1)[0]
        m = re.match(r"\s*armor_type_slot\s*=\s*([\w.]+)", code)
        if m:
            armor = m.group(1)
        m = re.match(r"\s*ammo_type_slot\s*=\s*([\w.]+)", code)
        if m:
            ammo = m.group(1)
    return typ, armor, ammo


def terms(arm_axis, ammo_axis, wa, la):
    """Bare enable terms (no indent) for one state of the partition."""
    out = []
    if arm_axis:
        out.append("%s = yes" % WEAK_T if wa else "NOT = { %s = yes }" % WEAK_T)
    if ammo_axis:
        out.append("%s = yes" % LOW_T if la else "NOT = { %s = yes }" % LOW_T)
    return out


def with_terms(block, bl_local, d_local, new_terms):
    """Return block lines with new_terms inserted into (or as) the enable block."""
    en = child(bl_local, d_local, "enable")
    key_indent = re.match(r"(\s*)", block[0]).group(1)
    if en:
        ind = key_indent + "\t\t"
        if en[2] > en[1] + 1:
            ind = re.match(r"(\s*)", block[en[1] + 1]).group(1)
        return block[:en[1] + 1] + [ind + t for t in new_terms] + block[en[1] + 1:]
    ind = key_indent + "\t"
    enable = [ind + "enable = {"] + [ind + "\t" + t for t in new_terms] + [ind + "}"]
    return block[:1] + enable + block[1:]


def make_twin(block, base_key, twin_key, wa, la, ammo, arm_axis, ammo_axis):
    # designs_of expects file layout (group at depth 0): wrap the block in a fake group
    wrapper = ["x = {"] + block + ["}"]
    bl_w, des_w = designs_of(wrapper)
    d_w = des_w[0]
    tv = child(bl_w, d_w, "target_variant")
    mods = child(bl_w, tv, "modules")
    am = child(bl_w, d_w, "allowed_modules")
    en = child(bl_w, d_w, "enable")
    low = low_ammo(ammo) if ammo_axis else None
    new = []
    for i, line in enumerate(wrapper):
        if i == 0 or i == len(wrapper) - 1:
            continue
        if MARKER.match(line):
            continue
        if en and en[1] < i < en[2] and OUR_TERM.match(line):
            continue
        if i == d_w[1]:
            line = re.sub(r"^(\s*)%s(\s*=\s*\{)" % re.escape(base_key), r"\g<1>%s\g<2>" % twin_key, line, 1)
        elif (mods[1] < i < mods[2]) or (am and am[1] < i < am[2]):
            if wa:
                line = re.sub(r"\b%s\b" % STRONG, WEAK, line)
            if la and low:
                line = re.sub(r"\b%s\b" % re.escape(ammo), low, line)
        new.append(line)
    # re-parse the twin to place its enable terms
    bl_t, des_t = designs_of(["x = {"] + new + ["}"])
    d_t = des_t[0]
    shifted = [(k, s - 1, e - 1, d) for k, s, e, d in bl_t]
    d_t = (d_t[0], d_t[1] - 1, d_t[2] - 1, d_t[3])
    key_indent = re.match(r"(\s*)", new[0]).group(1)
    new = with_terms(new, shifted, d_t, terms(arm_axis, ammo_axis, wa, la))
    return [key_indent + GEN_MARK + base_key + " - regenerate with tools/gen/gen_grade_pairs.py, never edit"] + new


def generate(lines, report, path):
    lines = strip_generated(lines)
    bl, des = designs_of(lines)
    out = []
    pos = 0
    stats = {"bases": 0, "twins": 0, "no_axis": 0}
    for d in des:
        typ, armor, ammo = design_modules(lines, bl, d)
        arm_axis = armor == STRONG
        ammo_axis = bool(ammo and low_ammo(ammo))
        if armor and not arm_axis:
            report.append(("ODD-ARMOR", path, d[1] + 1, "%s: armor_type_slot = %s" % (d[0], armor)))
        if not arm_axis and not ammo_axis:
            stats["no_axis"] += 1
            continue
        block = lines[d[1]:d[2] + 1]
        out.extend(lines[pos:d[1]])
        # base with its NOT terms
        local_bl = [(k, s - d[1], e - d[1], dd) for k, s, e, dd in bl if d[1] <= s and e <= d[2]]
        local_d = (d[0], 0, d[2] - d[1], d[3])
        out.extend(with_terms(block, local_bl, local_d, terms(arm_axis, ammo_axis, False, False)))
        stats["bases"] += 1
        combos = []
        for wa in ((False, True) if arm_axis else (False,)):
            for la in ((False, True) if ammo_axis else (False,)):
                if wa or la:
                    combos.append((wa, la))
        for wa, la in combos:
            q = "_".join(x for x, on in (("wa", wa), ("la", la)) if on)
            twin_key = d[0] + ("_" if "__" in d[0] else "__") + q
            out.append("")
            out.extend(make_twin(block, d[0], twin_key, wa, la, ammo, arm_axis, ammo_axis))
            stats["twins"] += 1
        pos = d[2] + 1
    out.extend(lines[pos:])
    return out, stats


def assert_partition(lines, report, path):
    """Every (type, cc, wa, la) state enables exactly as many designs as the base count."""
    bl, des = designs_of(lines)
    from collections import defaultdict
    by_type = defaultdict(list)
    for d in des:
        typ, armor, ammo = design_modules(lines, bl, d)
        en = child(bl, d, "enable")
        pol = {}
        if en:
            for i in range(en[1] + 1, en[2]):
                for name, key in ((WEAK_T, "wa"), (LOW_T, "la"), (CC_T, "cc")):
                    if name in lines[i]:
                        pol[key] = "NOT" not in lines[i]
        by_type[typ].append((d[0], pol))
    for typ, ds in by_type.items():
        bases = [x for x in ds if not TWIN_KEY.search(x[0])]
        axes = {k for _, p in ds for k in p}
        import itertools
        for state in itertools.product(*[((k, False), (k, True)) for k in sorted(axes)]):
            st = dict(state)
            n = sum(1 for _, p in ds if all(p.get(k, st[k]) == st[k] for k in st))
            want = sum(1 for _, p in bases if all(p.get(k, st[k]) == st[k] for k in st if k == "cc"))
            if n != want:
                report.append(("PARTITION", path, 0, "%s state %s enables %d designs, expected %d"
                               % (typ, st, n, want)))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true")
    g.add_argument("--check", action="store_true", help="exit 2 if any file would change")
    g.add_argument("--remove", action="store_true", help="strip twins and terms, write back")
    g.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    report, dirty = [], 0
    tot = {"bases": 0, "twins": 0, "no_axis": 0}
    for path in sorted(glob.glob(os.path.join(ROOT, DESIGN_GLOB))):
        raw = open(path, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf":
            report.append(("BOM", path, 0, "UTF-8 BOM - refusing"))
            continue
        nl = "\r\n" if b"\r\n" in raw else "\n"
        lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
        if a.remove:
            new, st = strip_generated(lines), {"bases": 0, "twins": 0, "no_axis": 0}
        else:
            new, st = generate(lines, report, path)
            assert_partition(new, report, path)
        for k in tot:
            tot[k] += st[k]
        data = nl.join(new).encode("utf-8")
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        if data != raw:
            dirty += 1
            print("%-34s bases %3d  twins %3d  no-axis %2d  %s" % (rel, st["bases"], st["twins"], st["no_axis"],
                                                                  "CHANGED" if not (a.apply or a.remove) else "written"))
            if a.apply or a.remove:
                open(path, "wb").write(data)
        else:
            print("%-34s bases %3d  twins %3d  no-axis %2d  up to date" % (rel, st["bases"], st["twins"], st["no_axis"]))
    for kind, path, ln, msg in sorted(set(report)):
        print("  %-10s %s:%d %s" % (kind, os.path.relpath(path, ROOT), ln, msg), file=sys.stderr)
    print("\n%d files would change; %d bases, %d twins, %d designs without an axis"
          % (dirty, tot["bases"], tot["twins"], tot["no_axis"]))
    if any(k in ("BOM", "PARTITION") for k, *_ in report):
        return 1
    if a.check and dirty:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
