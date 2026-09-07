#!/usr/bin/env python3
"""
add_research_bonus_exemption.py - put the [research-bonus-gate] exemption into every
standardized date gate of common/technologies/*.txt, touching nothing else.

The generated `ai_will_do` date gate is a hard `factor = 0` before `start_year`, which
also silences the engine's own weighting of research bonuses. The generators now emit,
right after that `factor = 0`:

    OR = {
        NOT = { has_tech_bonus = { technology = <tech> } }
        date < <start_year - 2>.1.1
    }

i.e. a tech bonus lifts the gate, but never earlier than two years before start_year.
This one-shot migration writes the same lines into the blocks already on disk WITHOUT
regenerating them, so hand-tuned or drifted trigger sets are preserved byte for byte
(the ai_will_do replacers' resolvers no longer match some infantry/support blocks -
regenerating them would change AI behaviour, not just add the exemption). It also
upgrades the earlier unfloored one-liner `NOT = { has_tech_bonus = ... }` to the
floored form. Idempotent: a gate already in the floored form is counted, not changed.

Recognised gate (any indentation, CRLF or LF, BOM left as found):
    factor = 0
    [exemption, one-liner or floored block]
    OR = {
        AND = {
            NOT = { has_country_flag = WA_AI_unused_research_slots }
            date < <start_year>.1.1
start_year is read from that `date <` line, so the floor follows what is on disk.
The tech name is the enclosing `<name> = {` header at brace depth 1 (any indentation).

Usage (any cwd; the mod root is derived from this file's location):
  python add_research_bonus_exemption.py            # dry run: per-file counts
  python add_research_bonus_exemption.py --apply    # write the technology files
  python add_research_bonus_exemption.py --check    # exit 1 if any gate is not in the floored form
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TECH_DIR = REPO / "common" / "technologies"

RE_TECH_HEADER = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{")
RE_FACTOR_0 = re.compile(r"^(\s*)factor\s*=\s*0\s*$")
RE_OR_OPEN = re.compile(r"^\s*OR\s*=\s*\{\s*$")
RE_AND_OPEN = re.compile(r"^\s*AND\s*=\s*\{\s*$")
RE_SLOT_FLAG = re.compile(r"^\s*NOT\s*=\s*\{\s*has_country_flag\s*=\s*WA_AI_unused_research_slots\s*\}\s*$")
RE_DATE = re.compile(r"^\s*date\s*<\s*(\d{4})\.1\.1\s*$")
RE_BONUS_ONELINER = re.compile(r"^\s*NOT\s*=\s*\{\s*has_tech_bonus\s*=\s*\{\s*technology\s*=\s*\w+\s*\}\s*\}\s*$")


def _strip(line: str) -> str:
    return line.rstrip("\r\n")


def _is_date_gate(lines, i) -> bool:
    """lines[i] is `OR = {` opening the standard date gate."""
    return (i + 3 < len(lines)
            and RE_OR_OPEN.match(_strip(lines[i]))
            and RE_AND_OPEN.match(_strip(lines[i + 1]))
            and RE_SLOT_FLAG.match(_strip(lines[i + 2]))
            and RE_DATE.match(_strip(lines[i + 3])))


def _floored_block(ind: str, tech: str, start_year: int, nl: str):
    return [
        f"{ind}OR = {{{nl}",
        f"{ind}\tNOT = {{ has_tech_bonus = {{ technology = {tech} }} }}{nl}",
        f"{ind}\tdate < {start_year - 2}.1.1{nl}",
        f"{ind}}}{nl}",
    ]


def process(data: bytes):
    """Return (new_bytes, inserted, upgraded, already) for one technology file."""
    text = data.decode("utf-8")
    lines = text.splitlines(keepends=True)
    out = []
    inserted = upgraded = already = 0
    tech = None
    depth = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        code = line.split("#", 1)[0]
        m = RE_TECH_HEADER.match(code)
        if m and depth == 1:  # direct child of `technologies = {`, whatever the indentation
            tech = m.group(1)
        depth += code.count("{") - code.count("}")
        out.append(line)
        fm = RE_FACTOR_0.match(_strip(line))
        if fm and tech and i + 1 < n:
            ind = fm.group(1)
            nl = line[len(_strip(line)):] or "\n"
            nxt = _strip(lines[i + 1])
            # (a) missing: factor = 0 directly followed by the date gate
            if _is_date_gate(lines, i + 1):
                year = int(RE_DATE.match(_strip(lines[i + 4])).group(1))
                out += _floored_block(ind, tech, year, nl)
                inserted += 1
            # (b) unfloored one-liner followed by the date gate -> replace it
            elif RE_BONUS_ONELINER.match(nxt) and _is_date_gate(lines, i + 2):
                year = int(RE_DATE.match(_strip(lines[i + 5])).group(1))
                out += _floored_block(ind, tech, year, nl)
                upgraded += 1
                i += 1  # skip the one-liner
            # (c) floored form already there
            elif (RE_OR_OPEN.match(nxt) and i + 4 < n
                  and RE_BONUS_ONELINER.match(_strip(lines[i + 2]))
                  and RE_DATE.match(_strip(lines[i + 3]))
                  and _is_date_gate(lines, i + 5)):
                already += 1
        i += 1
    return "".join(out).encode("utf-8"), inserted, upgraded, already


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="write the files")
    mode.add_argument("--check", action="store_true", help="exit 1 if any gate is not in the floored form")
    args = ap.parse_args()

    tot_ins = tot_up = tot_already = files_changed = 0
    for path in sorted(TECH_DIR.glob("*.txt")):
        data = path.read_bytes()
        new, ins, up, already = process(data)
        tot_ins += ins
        tot_up += up
        tot_already += already
        if ins or up:
            files_changed += 1
            print(f"  {path.name}: +{ins} inserted, {up} upgraded" + (f", {already} already" if already else ""))
            if args.apply:
                assert new.startswith(b"\xef\xbb\xbf") == data.startswith(b"\xef\xbb\xbf")
                path.write_bytes(new)
    verb = "written" if args.apply else "would change"
    print(f"{files_changed} file(s) {verb}, {tot_ins} inserted, {tot_up} upgraded, {tot_already} already in floored form")
    if args.check and (tot_ins or tot_up):
        return 1
    if not args.apply and not args.check and (tot_ins or tot_up):
        print("Dry run - rerun with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
