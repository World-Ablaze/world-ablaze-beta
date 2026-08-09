#!/usr/bin/env python3
"""Lint common/ai_strategy/ against the WA AI military value economy.

Report-only: never edits files. Rules are defined in
documentation/WA_AI_MILITARY_ECONOMY.md (E1..E10); this tool checks the
mechanically-checkable subset and prints a per-rule violation count (the
Phase 7c / Phase 8 burndown metric) plus optional per-violation detail.

Usage (from anywhere; paths resolve relative to this script):
    python military_economy_audit.py            # summary + worst offenders
    python military_economy_audit.py --list     # every violation
    python military_economy_audit.py --csv out.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AI_STRATEGY_DIR = REPO_ROOT / "common" / "ai_strategy"
AI_AREAS_DIR = REPO_ROOT / "common" / "ai_areas"
DEFINES_FILE = REPO_ROOT / "common" / "defines" / "05_defines.lua"

FRONT_DOMAIN_TYPES = {
    "area_priority",
    "front_unit_request",
    "front_armor_score",
    "front_control",
    "put_unit_buffers",
    "theatre_distribution_demand_increase",
    "force_concentration_factor",
    "force_concentration_front_factor",
    "force_concentration_target_weight",
}

FORCE_CONCENTRATION_TYPES = {
    "force_concentration_factor",
    "force_concentration_front_factor",
    "force_concentration_target_weight",
}

AIFC_FILE = "WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt"

# E8: front-math defines that must stay at vanilla 1.19.2 values unless the
# line carries a "measured:" justification comment.
VANILLA_FRONT_DEFINES = {
    "MAX_UNITS_FACTOR_FRONT_ORDER": 1.0,
    "DESIRED_UNITS_FACTOR_FRONT_ORDER": 1.1,
    "MIN_UNITS_FACTOR_FRONT_ORDER": 1.0,
    "MAX_UNITS_FACTOR_AREA_ORDER": 0.75,
    "DESIRED_UNITS_FACTOR_AREA_ORDER": 0.7,
    "MIN_UNITS_FACTOR_AREA_ORDER": 1.0,
    "FRONT_UNITS_CAP_FACTOR": 15.0,
    "GARRISON_FRACTION": 0.0,
    "ENTRENCHMENT_WEIGHT": 2.0,
    "UNIT_ASSIGNMENT_TERRAIN_IMPORTANCE": 10.0,
}


def read_text(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def strip_comment(line):
    idx = line.find("#")
    return line if idx < 0 else line[:idx]


def parse_ai_areas():
    """area name -> number of strategic regions (for the E1 narrow-area allowance)."""
    sizes = {}
    for path in sorted(AI_AREAS_DIR.glob("*.txt")):
        text = read_text(path)
        # areas = { name = { strategic_regions = { 1 2 3 } } ... }
        for m in re.finditer(
            r"(\w+)\s*=\s*\{\s*strategic_regions\s*=\s*\{([^}]*)\}", text
        ):
            sizes[m.group(1)] = len(m.group(2).split())
    return sizes


class Block:
    """One top-level strategy block."""

    def __init__(self, name, file, line):
        self.name = name
        self.file = file  # Path
        self.line = line  # 1-based line of the opening
        self.lines = []  # (lineno, raw_text) inside the block, including opener

    @property
    def text(self):
        return "\n".join(raw for _, raw in self.lines)


def parse_blocks(path):
    """Yield top-level `name = { ... }` blocks with line numbers (brace tracking,
    comments stripped for counting)."""
    blocks = []
    depth = 0
    current = None
    opener_re = re.compile(r"^\s*([A-Za-z0-9_.@]+)\s*=\s*\{")
    for lineno, raw in enumerate(read_text(path).splitlines(), 1):
        code = strip_comment(raw)
        if depth == 0:
            m = opener_re.match(code)
            if m:
                current = Block(m.group(1), path, lineno)
        if current is not None:
            current.lines.append((lineno, raw))
        depth += code.count("{") - code.count("}")
        if depth == 0 and current is not None and code.count("}") > 0:
            blocks.append(current)
            current = None
        if depth < 0:  # unbalanced file; reset so we don't cascade
            depth = 0
    return blocks


def iter_ai_strategies(block):
    """Yield dicts for each ai_strategy sub-block: type, value, ratio, line, text."""
    entries = []
    depth = 0
    inside = False
    entry = None
    for lineno, raw in block.lines:
        code = strip_comment(raw)
        if not inside and re.search(r"\bai_strategy\s*=\s*\{", code):
            inside = True
            depth = 0
            entry = {"line": lineno, "raw": [], "type": None, "value": None,
                     "ratio": None, "subtract_fronts_no": False}
        if inside:
            entry["raw"].append(raw)
            m = re.search(r"^\s*type\s*=\s*(\w+)", code)
            if m:
                entry["type"] = m.group(1)
            m = re.search(r"^\s*value\s*=\s*(-?\d+(?:\.\d+)?)", code)
            if m:
                entry["value"] = float(m.group(1))
            m = re.search(r"^\s*ratio\s*=\s*(-?\d+(?:\.\d+)?)", code)
            if m:
                entry["ratio"] = float(m.group(1))
            if re.search(r"subtract_fronts_from_need\s*=\s*no", code):
                entry["subtract_fronts_no"] = True
            depth += code.count("{") - code.count("}")
            if depth <= 0 and code.count("}") > 0:
                inside = False
                entries.append(entry)
    return entries


def block_has_enable(block):
    return re.search(r"^\s*enable\s*=\s*\{", block.text, re.M) is not None


def enable_always_yes(block):
    m = re.search(r"enable\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", block.text)
    if not m:
        return False
    body = re.sub(r"#.*", "", m.group(1))
    return re.search(r"^\s*always\s*=\s*yes\s*$", body, re.M) is not None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="print every violation")
    ap.add_argument("--csv", metavar="PATH", help="write violations to CSV")
    ap.add_argument("--top", type=int, default=8,
                    help="worst offenders shown per rule in summary mode")
    args = ap.parse_args()

    area_sizes = parse_ai_areas()
    violations = []  # (rule, file, line, block, detail)

    def add(rule, block, line, detail):
        violations.append((rule, str(block.file.relative_to(REPO_ROOT)),
                           line, block.name, detail))

    for path in sorted(AI_STRATEGY_DIR.glob("*.txt")):
        is_wa_file = path.name.startswith(("WA_AI_MILITARY_", "WA_AI_NAVAL_"))
        for block in parse_blocks(path):
            strategies = iter_ai_strategies(block)
            has_front_domain = any(
                s["type"] in FRONT_DOMAIN_TYPES for s in strategies)

            # E10: gating (scoped to blocks carrying front-domain types - the
            # economy's remit; legacy production/research blocks are not lintable here)
            if has_front_domain:
                if not block_has_enable(block):
                    add("E10-no-enable", block, block.line, "block has no enable")
                elif enable_always_yes(block) and "# always-on:" not in block.text:
                    add("E10-always-yes", block, block.line,
                        "enable = always yes without '# always-on:' justification")

            # E9: legacy containment
            if not is_wa_file and has_front_domain:
                types = sorted({s["type"] for s in strategies
                                if s["type"] in FRONT_DOMAIN_TYPES})
                add("E9-legacy-front-domain", block, block.line,
                    "front-domain types in legacy file: " + ", ".join(types))

            for s in strategies:
                t, v, line = s["type"], s["value"], s["line"]
                if t == "area_priority" and v is not None:
                    # narrow-area allowance: id = <area> with <=2 regions
                    m = re.search(r"^\s*id\s*=\s*(\w+)", "\n".join(s["raw"]), re.M)
                    narrow = m and area_sizes.get(m.group(1), 99) <= 2
                    hi = 1000 if narrow else 200
                    if not (-200 <= v <= hi):
                        add("E1-area_priority-range", block, line,
                            f"value {v:g} outside [-200, +{hi}]"
                            + (" (narrow area)" if narrow else ""))
                elif t == "front_unit_request" and v is not None:
                    if not (-100 <= v <= 200):
                        add("E2-front_unit_request-range", block, line,
                            f"value {v:g} outside [-100, +200]")
                elif t == "theatre_distribution_demand_increase" and v is not None:
                    if not (0 <= v <= 15):
                        add("E3-theatre_demand-range", block, line,
                            f"value {v:g} outside [0, +15]")
                elif t == "put_unit_buffers":
                    r = s["ratio"]
                    if r is not None and r > 0.25 and "# siege:" not in block.text:
                        add("E4-buffer-ratio", block, line,
                            f"ratio {r:g} > 0.25 without '# siege:' justification")
                    if r is not None and r > 1.0:
                        add("E4-buffer-ratio-army", block, line,
                            f"ratio {r:g} exceeds the entire army")
                    if s["subtract_fronts_no"] and "# pool:" not in block.text:
                        add("E4-buffer-pool-comment", block, line,
                            "subtract_fronts_from_need = no without '# pool:' comment")
                    if enable_always_yes(block):
                        add("E4-buffer-always-on", block, line,
                            "put_unit_buffers with enable = always yes")
                elif t in FORCE_CONCENTRATION_TYPES:
                    if path.name != AIFC_FILE:
                        add("E5-aifc-ownership", block, line,
                            f"{t} written outside {AIFC_FILE}")
                elif t == "front_armor_score" and v is not None:
                    if not (-150 <= v <= 400):
                        add("E6-front_armor_score-range", block, line,
                            f"value {v:g} outside [-150, +400]")
                elif t == "garrison" and v is not None:
                    if v < 0 and v != -5000:
                        add("E7-garrison-negative", block, line,
                            f"negative garrison {v:g} is not the documented -5000")
                    elif v > 200:
                        add("E7-garrison-range", block, line,
                            f"value {v:g} outside [0, +200]")

    # E8: defines
    if DEFINES_FILE.exists():
        for lineno, raw in enumerate(read_text(DEFINES_FILE).splitlines(), 1):
            m = re.match(
                r"\s*NDefines\.\w+\.(\w+)\s*=\s*(-?\d+(?:\.\d+)?)", raw)
            if m and m.group(1) in VANILLA_FRONT_DEFINES:
                current = float(m.group(2))
                vanilla = VANILLA_FRONT_DEFINES[m.group(1)]
                if current != vanilla and "measured:" not in raw:
                    violations.append((
                        "E8-define-deviation",
                        str(DEFINES_FILE.relative_to(REPO_ROOT)), lineno,
                        m.group(1),
                        f"{current:g} (vanilla {vanilla:g}) without 'measured:' comment"))

    # ---- output ----
    by_rule = {}
    for v in violations:
        by_rule.setdefault(v[0], []).append(v)

    print(f"WA AI military economy audit - {len(violations)} violations "
          f"across {len(by_rule)} rule classes\n")
    for rule in sorted(by_rule):
        items = by_rule[rule]
        print(f"{rule:32} {len(items):5}")
        shown = items if args.list else items[: args.top]
        for _, file, line, name, detail in shown:
            print(f"    {file}:{line}  {name}  - {detail}")
        if not args.list and len(items) > args.top:
            print(f"    ... {len(items) - args.top} more (use --list)")
        print()

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["rule", "file", "line", "block", "detail"])
            w.writerows(violations)
        print(f"CSV written to {args.csv}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
