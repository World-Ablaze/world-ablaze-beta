#!/usr/bin/env python3
"""
add_research_bonus_exemption.py - put the [research-rush] exemption into every standardized
date gate of common/technologies/*.txt, touching nothing else.

The generated `ai_will_do` date gate is a hard `factor = 0` before `start_year`, which also
silences the engine's own weighting of research bonuses. The generators now emit, right after
that `factor = 0`, two blocks reading the WA_rb_* counters kept by
tools/gen/gen_research_bonus_tracking.py (documentation/WA_RESEARCH_RUSH.md):

    OR = {                                   # 1-year rush: a bonus use is available
        NOT = { OR = { check_variable = { WA_rb_uses_<c> > 0 } ... check_variable = { WA_rb_uses_t_<tech> > 0 } } }
        date < <start_year - 1>.1.1
    }
    OR = {                                   # 2-year rush: that bonus has ahead_reduction >= 2
        NOT = { OR = { check_variable = { WA_rb_ahead2_<c> > 0 } ... check_variable = { WA_rb_ahead2_t_<tech> > 0 } } }
        date < <start_year - 2>.1.1
    }

This one-shot migration rewrites the blocks on disk WITHOUT regenerating them, so hand-tuned
or drifted trigger sets are preserved byte for byte. It replaces every earlier exemption shape
this tool wrote (has_tech_bonus one-liner, has_tech_bonus floored block, has_tech_bonus
category block - all defective: `has_tech_bonus` does not read bonus availability, harness
WA_TEST_research_bonus 2026-09-08) and inserts where none exists. Idempotent: a gate already in
the counter form is counted, not changed.

Recognised gate (any indentation, CRLF or LF, BOM left as found):
    factor = 0
    [exemption span: zero or more lines made only of OR/NOT/AND braces, has_tech_bonus,
     check_variable WA_rb_*, and `date <` lines]
    OR = {
        AND = {
            NOT = { has_country_flag = WA_AI_unused_research_slots }
            date < <start_year>.1.1
start_year is read from that `date <` line. The tech name and its `categories = {}` come from
the enclosing `<name> = {` header at brace depth 1 (any indentation), collected in a first pass.

Usage (any cwd; the mod root is derived from this file's location):
  python add_research_bonus_exemption.py            # dry run: per-file counts
  python add_research_bonus_exemption.py --apply    # write the technology files
  python add_research_bonus_exemption.py --check    # exit 1 if any gate is not in the counter form
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TECH_DIR = REPO / "common" / "technologies"

RE_TECH_HEADER = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{")
RE_CATEGORIES_OPEN = re.compile(r"^\s*categories\s*=\s*\{(.*)$")
RE_FACTOR_0 = re.compile(r"^(\s*)factor\s*=\s*0\s*$")
RE_OR_OPEN = re.compile(r"^\s*OR\s*=\s*\{\s*$")
RE_AND_OPEN = re.compile(r"^\s*AND\s*=\s*\{\s*$")
RE_SLOT_FLAG = re.compile(r"^\s*NOT\s*=\s*\{\s*has_country_flag\s*=\s*WA_AI_unused_research_slots\s*\}\s*$")
RE_DATE = re.compile(r"^\s*date\s*<\s*(\d{4})\.1\.1\s*$")
# a line that may belong to an exemption span (any earlier shape or the current one)
RE_SPAN_LINE = re.compile(
    r"^\s*(OR\s*=\s*\{|NOT\s*=\s*\{|\}|NOT\s*=\s*\{\s*has_tech_bonus\s*=.*\}\s*\}|"
    r"has_tech_bonus\s*=\s*\{.*\}|check_variable\s*=\s*\{\s*WA_rb_\w+\s*>\s*0\s*\}|date\s*<\s*\d{4}\.1\.1)\s*$")
MAX_SPAN = 60


def _strip(line: str) -> str:
    return line.rstrip("\r\n")


def _is_date_gate(lines, i) -> bool:
    return (i + 3 < len(lines)
            and RE_OR_OPEN.match(_strip(lines[i]))
            and RE_AND_OPEN.match(_strip(lines[i + 1]))
            and RE_SLOT_FLAG.match(_strip(lines[i + 2]))
            and RE_DATE.match(_strip(lines[i + 3])))


def _find_date_gate(lines, start):
    """First k >= start such that lines[k] opens the standard date gate and every line in
    [start, k) is an exemption-span line. None when the shape is not recognised."""
    for k in range(start, min(start + MAX_SPAN, len(lines))):
        if _is_date_gate(lines, k):
            return k
        if not RE_SPAN_LINE.match(_strip(lines[k])):
            return None
    return None


def counter_block(ind: str, tech: str, categories, start_year: int, nl: str):
    keys = list(categories) + [f"t_{tech}"]
    out = []
    for fam, years in (("uses", 1), ("ahead2", 2)):
        out += [f"{ind}OR = {{{nl}", f"{ind}\tNOT = {{{nl}", f"{ind}\t\tOR = {{{nl}"]
        out += [f"{ind}\t\t\tcheck_variable = {{ WA_rb_{fam}_{k} > 0 }}{nl}" for k in keys]
        out += [f"{ind}\t\t}}{nl}", f"{ind}\t}}{nl}", f"{ind}\tdate < {start_year - years}.1.1{nl}", f"{ind}}}{nl}"]
    return out


def _tech_categories(lines):
    cats = {}
    depth = 0
    tech = None
    in_cats = False
    for line in lines:
        code = line.split("#", 1)[0]
        if in_cats:
            cats[tech] += re.findall(r"[A-Za-z0-9_]+", code.split("}", 1)[0])
            if "}" in code:
                in_cats = False
        else:
            m = RE_TECH_HEADER.match(code)
            if m and depth == 1:
                tech = m.group(1)
                cats.setdefault(tech, [])
            cm = RE_CATEGORIES_OPEN.match(code)
            if cm and depth == 2 and tech:
                rest = cm.group(1)
                cats[tech] += re.findall(r"[A-Za-z0-9_]+", rest.split("}", 1)[0])
                in_cats = "}" not in rest
        depth += code.count("{") - code.count("}")
    return cats


def process(data: bytes):
    """Return (new_bytes, stats); stats keys: inserted, upgraded, already."""
    text = data.decode("utf-8")
    lines = text.splitlines(keepends=True)
    cats = _tech_categories(lines)
    out = []
    st = {"inserted": 0, "upgraded": 0, "already": 0}
    tech = None
    depth = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        code = line.split("#", 1)[0]
        m = RE_TECH_HEADER.match(code)
        if m and depth == 1:
            tech = m.group(1)
        depth += code.count("{") - code.count("}")
        out.append(line)
        fm = RE_FACTOR_0.match(_strip(line))
        if fm and tech and i + 1 < n:
            k = _find_date_gate(lines, i + 1)
            if k is not None:
                year = int(RE_DATE.match(_strip(lines[k + 3])).group(1))
                block = counter_block(fm.group(1), tech, cats.get(tech, []), year, line[len(_strip(line)):] or "\n")
                span = lines[i + 1:k]
                if span == block:
                    st["already"] += 1
                else:
                    st["inserted" if not span else "upgraded"] += 1
                out += block
                i = k  # continue at the date gate (it is copied unchanged)
                continue
        i += 1
    return "".join(out).encode("utf-8"), st


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="write the files")
    mode.add_argument("--check", action="store_true", help="exit 1 if any gate is not in the counter form")
    args = ap.parse_args()

    tot = {"inserted": 0, "upgraded": 0, "already": 0}
    files_changed = 0
    for path in sorted(TECH_DIR.glob("*.txt")):
        data = path.read_bytes()
        new, st = process(data)
        for k in tot:
            tot[k] += st[k]
        if new != data:
            files_changed += 1
            print(f"  {path.name}: +{st['inserted']} inserted, {st['upgraded']} upgraded"
                  + (f", {st['already']} already" if st["already"] else ""))
            if args.apply:
                assert new.startswith(b"\xef\xbb\xbf") == data.startswith(b"\xef\xbb\xbf")
                path.write_bytes(new)
    verb = "written" if args.apply else "would change"
    print(f"{files_changed} file(s) {verb}, {tot['inserted']} inserted, {tot['upgraded']} upgraded, "
          f"{tot['already']} already in counter form")
    pending = tot["inserted"] + tot["upgraded"]
    if args.check and pending:
        return 1
    if not args.apply and not args.check and pending:
        print("Dry run - rerun with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
