#!/usr/bin/env python3
"""
gen_techtree_membership.py - render the TECH TREE MEMBERSHIP triggers of the AI.

[techtree-membership] "Which technology tree does this country have?" already has exactly one
answer in the game data: the `available` block of each folder in
common/technology_tags/00_technology.txt. The AI used to re-answer it with hand-written
`original_tag` lists in WA_AI_CONFIG.txt, which silently dropped the `has_country_flag =
*_technologies_tree_flag` half - a country handed the German tree by event was still classified
by its own tag. This tool copies the engine's answer into scripted triggers so the two cannot
diverge.

Output: common/scripted_triggers/WA_AI_TECHTREE_membership.txt
    WA_AI_TECHTREE_has_<folder> = { <the folder's steady-state availability> }

The only rewrite applied to the source block is the removal of the startup escape hatch
`NOT = { has_global_flag = tech_tree_startup_flag }`. That term makes every folder available to
everyone before the tree-startup flag is set (so the game can show the full tree on the main
menu); it is not a statement about who owns the tree, and keeping it would make every membership
trigger true for everybody in that window. Everything else - the positive OR, the exclusion NOTs
that keep CZE/HUN/POL out of the majors' folders, the complement form of the `minor_*` folders -
is emitted verbatim.

A folder with no `available` block at all is available to everyone; it gets `always = yes`.

Usage (any cwd; the mod root is derived from this file's location):
  python tools/gen/gen_techtree_membership.py --dry-run   # unified diff of what would change
  python tools/gen/gen_techtree_membership.py             # write the trigger file
  python tools/gen/gen_techtree_membership.py --check     # exit 1 if the file is out of sync
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "common" / "technology_tags" / "00_technology.txt"
DST = REPO / "common" / "scripted_triggers" / "WA_AI_TECHTREE_membership.txt"

STARTUP_ESCAPE = "tech_tree_startup_flag"

HEADER = """\
# GENERATED FILE - do not edit by hand.
# Source: common/technology_tags/00_technology.txt, rendered by tools/gen/gen_techtree_membership.py
# (`--check` verifies, `--dry-run` previews, no flag writes). Change the folder, not this file.
#
# [techtree-membership] DECLARATION-layer MATERIAL (identity + setup data, frontier 1/2 of
# documentation/WA_AI_LAYERS.md, which already names the *_technologies_tree_flag as setup data),
# named with the layer-2 `has_` vocabulary because that is what the trigger asks of a country.
# The named exception that lets these `original_tag` terms live outside WA_AI_CONFIG is in
# WA_AI_LAYERS.md §5: they are COPIED from the game's own folder file, never hand-written here.
#
# Which TECHNOLOGY TREE a country has: one trigger per technology
# folder, carrying that folder's own `available` block - so "GER has the German armour
# tree" is asked here exactly the way the engine asks it, tag OR tree flag, never by a hand-copied
# tag list. A country handed another tree by event (has_country_flag = *_technologies_tree_flag)
# is a member here, and that is the whole point of the layer.
#
# The startup escape `NOT = { has_global_flag = tech_tree_startup_flag }` is dropped on purpose:
# it opens every folder to everyone before the tree-startup flag is set, which is a UI concern,
# not an ownership statement. Everything else is copied verbatim, exclusions included.
#
# Read by the WA_AI_TECHTREE_* capability gates. Never gate a BEHAVIOUR on membership alone -
# owning a tree says what a country CAN research, not what it should build.
"""


# ---------------------------------------------------------------------------------------
# Minimal PDXScript block reader - enough for 00_technology.txt
# ---------------------------------------------------------------------------------------


def strip_comments(text: str) -> str:
    """Drop `#` comments, keeping line structure (no string literals in this file)."""
    return "\n".join(line.split("#", 1)[0].rstrip() for line in text.split("\n"))


def match_brace(text: str, open_idx: int) -> int:
    """Index just past the `}` matching the `{` at open_idx."""
    depth = 0
    i = open_idx
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError(f"unbalanced brace at {open_idx}")


def read_folders(text: str) -> list[tuple[str, str | None]]:
    """[(folder name, raw body of its `available` block or None)] in file order."""
    clean = strip_comments(text)
    m = re.search(r"\btechnology_folders\s*=\s*\{", clean)
    start = m.end() - 1 if m else clean.index("{")
    end = match_brace(clean, start)
    inner = clean[start + 1 : end - 1]

    folders: list[tuple[str, str | None]] = []
    i = 0
    while i < len(inner):
        mm = re.compile(r"([A-Za-z_]\w*)\s*=\s*\{").match(inner, i)
        if not mm:
            i += 1
            continue
        body_start = mm.end() - 1
        body_end = match_brace(inner, body_start)
        body = inner[body_start + 1 : body_end - 1]
        av = re.search(r"\bavailable\s*=\s*\{", body)
        if av:
            a_start = av.end() - 1
            a_end = match_brace(body, a_start)
            folders.append((mm.group(1), body[a_start + 1 : a_end - 1]))
        else:
            folders.append((mm.group(1), None))
        i = body_end
    return folders


# ---------------------------------------------------------------------------------------
# Term-level rewrite: drop the startup escape, keep everything else
# ---------------------------------------------------------------------------------------


def split_terms(body: str) -> list[str]:
    """Split a block body into its top-level terms (`X = { ... }` or `X = Y`)."""
    terms: list[str] = []
    i = 0
    n = len(body)
    while i < n:
        if body[i].isspace():
            i += 1
            continue
        m = re.compile(r"([A-Za-z_]\w*)\s*=\s*").match(body, i)
        if not m:
            i += 1
            continue
        j = m.end()
        while j < n and body[j].isspace():
            j += 1
        if j < n and body[j] == "{":
            end = match_brace(body, j)
            terms.append(body[i:end])
            i = end
        else:
            vm = re.compile(r"[^\s}]+").match(body, j)
            end = vm.end() if vm else j
            terms.append(body[i:end])
            i = end
    return terms


def is_startup_escape(term: str) -> bool:
    return term.startswith("NOT") and STARTUP_ESCAPE in term


def normalise(body: str) -> list[str]:
    """The folder's steady-state availability, as a list of top-level terms.

    Handles the two shapes the source uses:
      OR = { <startup escape> AND = { ... } }   -> the AND's own terms
      OR = { <startup escape> a b c }           -> OR = { a b c }
    and leaves every other shape untouched.
    """
    terms = split_terms(body)
    if len(terms) == 1 and terms[0].startswith("OR"):
        inner_open = terms[0].index("{")
        inner = terms[0][inner_open + 1 : match_brace(terms[0], inner_open) - 1]
        inner_terms = split_terms(inner)
        kept = [t for t in inner_terms if not is_startup_escape(t)]
        if len(kept) != len(inner_terms):
            if len(kept) == 1 and kept[0].startswith("AND"):
                and_open = kept[0].index("{")
                and_body = kept[0][and_open + 1 : match_brace(kept[0], and_open) - 1]
                return split_terms(and_body)
            if len(kept) == 1:
                return kept
            return ["OR = {\n" + "\n".join(kept) + "\n}"]
    return [t for t in terms if not is_startup_escape(t)]


# ---------------------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------------------


def reindent(term: str, level: int) -> str:
    """Re-render one `key = value` / `key = { ... }` term with tab indentation."""
    m = re.compile(r"\s*([A-Za-z_]\w*)\s*=\s*").match(term)
    if not m:
        return "\t" * level + term.strip()
    key = m.group(1)
    rest = term[m.end():].strip()
    pad = "\t" * level
    if not rest.startswith("{"):
        return f"{pad}{key} = {rest}"
    body = rest[1 : match_brace(rest, 0) - 1]
    inner = split_terms(body)
    if not inner:
        return f"{pad}{key} = {{ }}"
    if len(inner) == 1 and "{" not in inner[0]:
        one = re.sub(r"\s+", " ", inner[0]).strip()
        return f"{pad}{key} = {{ {one} }}"
    lines = "\n".join(reindent(t, level + 1) for t in inner)
    return f"{pad}{key} = {{\n{lines}\n{pad}}}"


def render(folders: list[tuple[str, str | None]]) -> str:
    chunks = [HEADER]
    for name, available in folders:
        chunks.append(f"\nWA_AI_TECHTREE_has_{name} = {{\n")
        if available is None or not available.strip():
            chunks.append("\talways = yes\n")
        else:
            terms = normalise(available)
            if not terms:
                chunks.append("\talways = yes\n")
            else:
                for t in terms:
                    chunks.append(reindent(t, 1) + "\n")
        chunks.append("}\n")
    return "".join(chunks)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print a unified diff, write nothing")
    ap.add_argument("--check", action="store_true", help="exit 1 if the output is out of sync")
    args = ap.parse_args()

    folders = read_folders(SRC.read_text(encoding="utf-8-sig"))
    new = render(folders)
    old = DST.read_text(encoding="utf-8") if DST.exists() else ""

    if args.check:
        if old == new:
            print(f"OK  {DST.relative_to(REPO)} in sync ({len(folders)} folders)")
            return 0
        print(f"STALE  {DST.relative_to(REPO)} - run tools/gen/gen_techtree_membership.py")
        return 1

    if args.dry_run:
        diff = difflib.unified_diff(
            old.splitlines(True), new.splitlines(True),
            fromfile=str(DST.relative_to(REPO)), tofile=str(DST.relative_to(REPO)) + " (new)",
        )
        sys.stdout.writelines(diff)
        return 0

    DST.write_text(new, encoding="utf-8", newline="\n")
    print(f"wrote {DST.relative_to(REPO)}  ({len(folders)} folders)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
