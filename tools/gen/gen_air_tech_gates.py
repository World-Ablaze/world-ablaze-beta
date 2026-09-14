#!/usr/bin/env python3
"""
gen_air_tech_gates.py - generate the AI's air-production tech gates from one registry.

[air-budget] The AI opens an aircraft production line only from the tech rung it is willing to
spend a factory on (WA_AI_PRODUCTION_has_worthwhile_<line>), and a few has_*_tech observations
(jet vetoes, patrol). Those lists used to be hand-written OR blocks; a tree left out of one list
silently barred that nation from the line, and nobody could tell an omission from a decision.
The registry makes every entry a decision:

  tools/air_tech_registry.json
    triggers.<trigger>.trees.<tree>.base     tech ids of the non-BBA game (any one passes)
    triggers.<trigger>.trees.<tree>.ad_tech  tech ids of the BBA game (any one passes)
    triggers.<trigger>.note                  the protected-behaviour comment rendered above it
    exclude.airframes                        airframe ids the equipment evaluator must keep
                                             KEEP_OLD (read by tools/equipment_evaluator)

Output:
  common/scripted_triggers/WA_AI_PRODUCTION_air_tech.txt  (GENERATED - never hand-edit)

Checks (--check, exit 1 on any ERROR):
  ERROR  UNKNOWN-TECH   an id that no file under common/technologies/ declares
  ERROR  OUT-OF-DATE    the file on disk differs from what the registry renders
  ERROR  BAD-TREE       a tree key that is neither "generic" nor a 3-letter tag
  WARN   TREE-GAP       a tree that owns entries in other lines but none in this one -
                        legal (the archetype decides who builds) but must be deliberate

Usage (any cwd; the mod root is derived from this file's location):
  python tools/gen/gen_air_tech_gates.py --check      # verify, write nothing
  python tools/gen/gen_air_tech_gates.py --dry-run    # print what would change
  python tools/gen/gen_air_tech_gates.py              # write the trigger file
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "tools" / "air_tech_registry.json"
OUT = REPO / "common" / "scripted_triggers" / "WA_AI_PRODUCTION_air_tech.txt"
TECH_DIR = REPO / "common" / "technologies"

RE_TECH_DECL = re.compile(r"^([a-z][a-z0-9_]*)\s*=\s*\{", re.M)
RE_TREE = re.compile(r"^(generic|[a-z]{3})$")

HEADER = """\
# GENERATED FILE - do not edit by hand.
# Source: tools/air_tech_registry.json, rendered by tools/gen/gen_air_tech_gates.py
# (`--check` verifies, `--dry-run` previews, no flag writes). Retune the registry, not this file.
#
# Air-production TECH vocabulary of the AI. Read only by WA_AI_PRODUCTION_air.txt and by the air
# production effect; layer 2 (OBSERVATION), so it answers "what is true", never "should we act".
#
# Every has_worthwhile_<line> gate lists, per TECH TREE, the rung from which the AI is willing to
# fund the line: base ids for the non-BBA game, _ad_tech_ ids for the BBA one. A country holds only
# its own tree's techs, so the flat OR selects itself; who may actually build is the archetype's
# job (WA_AI_CONFIG), never this file's. A tree with no entry in a line is barred from that line
# outright - the registry check reports such gaps so they stay decisions.
#
# [techtree-capability] Each gate has a has_branch_<line> twin asking the OTHER question: not "has it
# reached the rung" but "does its TREE carry this line at all". has_tech cannot answer that - a
# country that has not researched the rung yet looks the same as one whose tree has no such plane -
# and that is the question the AIRFORCE archetype tag lists in WA_AI_CONFIG used to answer by hand.
# The twin is built from the folder ownership of common/technology_tags/00_technology.txt
# (registry key `tree_folders` -> WA_AI_TECHTREE_has_<folder>), so tag OR tree flag: a country that
# ADOPTED another air tree is answered on the tree it owns, not on the tag it was born with.
#
# [ai-owns-its-tech-list] Nothing here calls the player-facing WA_has_*_tech of WA_triggers.txt:
# the player asks "does this country hold the tech", the AI asks "may it spend a factory on this".
# The two are free to diverge, so a retune here must never be able to move player content.
"""


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def declared_techs() -> set[str]:
    """Tech ids = the keys at brace depth 1, i.e. directly inside `technologies = { }`."""
    ids: set[str] = set()
    for p in TECH_DIR.glob("*.txt"):
        depth = 0
        for raw in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            line = raw.split("#", 1)[0]
            m = RE_TECH_DECL.match(line.strip())
            if m and depth == 1:
                ids.add(m.group(1))
            depth += line.count("{") - line.count("}")
    return ids


def render(reg: dict) -> str:
    lines = [HEADER]
    folders = reg.get("tree_folders", {})
    for name, spec in reg["triggers"].items():
        lines.append("")
        note = spec.get("note", "").strip()
        if note:
            for row in wrap(note, 96):
                lines.append(f"# {row}")
        lines.append(f"{name} = {{")
        lines.append("\tOR = {")
        base, ad = [], []
        for tree, kinds in spec["trees"].items():
            base += kinds.get("base", [])
            ad += kinds.get("ad_tech", [])
        for tid in base:
            lines.append(f"\t\thas_tech = {tid}")
        if base and ad:
            lines.append("")
        for tid in ad:
            lines.append(f"\t\thas_tech = {tid}")
        lines.append("\t}")
        lines.append("}")

        # CAPABILITY twin - "could this country EVER fund this line", answered by tree ownership.
        if folders:
            owning = []
            for tree in spec["trees"]:
                folder = folders.get(tree)
                if folder and folder not in owning:
                    owning.append(folder)
            if owning:
                lines.append("")
                lines.append(f"{capability_name(name)} = {{")
                lines.append("\tOR = {")
                for folder in owning:
                    lines.append(f"\t\tWA_AI_TECHTREE_has_{folder} = yes")
                lines.append("\t}")
                lines.append("}")
    return "\n".join(lines) + "\n"


def capability_name(trigger: str) -> str:
    """WA_AI_PRODUCTION_has_worthwhile_cas -> WA_AI_PRODUCTION_has_branch_cas."""
    for prefix in ("WA_AI_PRODUCTION_has_worthwhile_", "WA_AI_PRODUCTION_has_"):
        if trigger.startswith(prefix):
            tail = trigger[len(prefix):]
            if prefix.endswith("has_") and tail.endswith("_tech"):
                tail = tail[: -len("_tech")]
            return "WA_AI_PRODUCTION_has_branch_" + tail
    return trigger + "_has_branch"


def wrap(text: str, width: int) -> list[str]:
    words, rows, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            rows.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        rows.append(cur)
    return rows


def check(reg: dict, rendered: str) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    techs = declared_techs()
    all_trees: set[str] = set()
    for name, spec in reg["triggers"].items():
        for tree, kinds in spec["trees"].items():
            if not RE_TREE.match(tree):
                errors.append(f"BAD-TREE      {name}: tree key {tree!r}")
            if tree != "generic":
                all_trees.add(tree)
            for kind, ids in kinds.items():
                if kind not in ("base", "ad_tech"):
                    errors.append(f"BAD-TREE      {name}.{tree}: kind {kind!r} (base | ad_tech)")
                for tid in ids:
                    if tid not in techs:
                        errors.append(f"UNKNOWN-TECH  {name}.{tree}.{kind}: {tid}")
    for name, spec in reg["triggers"].items():
        if not name.startswith("WA_AI_PRODUCTION_has_worthwhile_"):
            continue  # vetoes and observations are not line gates
        missing = sorted(all_trees - set(spec["trees"]))
        if missing:
            warns.append(f"TREE-GAP      {name}: no entry for {', '.join(missing)}")
    if OUT.exists():
        on_disk = OUT.read_text(encoding="utf-8", errors="replace")
        if on_disk.startswith("﻿"):
            errors.append("OUT-OF-DATE   trigger file carries a BOM (AGENTS.md rule 16)")
        if on_disk.replace("\r\n", "\n") != rendered:
            errors.append("OUT-OF-DATE   trigger file differs from the registry rendering - regenerate")
    else:
        errors.append("OUT-OF-DATE   trigger file missing - generate it")
    return errors, warns


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 on ERROR")
    ap.add_argument("--dry-run", action="store_true", help="show whether the file would change")
    args = ap.parse_args(argv)

    reg = load_registry()
    rendered = render(reg)
    errors, warns = check(reg, rendered)
    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if args.check:
        print(f"{len(errors)} ERROR, {len(warns)} WARN")
        return 1 if errors else 0

    hard = [e for e in errors if not e.startswith("OUT-OF-DATE")]
    if hard:
        print("registry errors - nothing written")
        return 1
    changed = any(e.startswith("OUT-OF-DATE") for e in errors)
    if args.dry_run:
        print(f"dry-run: {OUT.relative_to(REPO)} would {'change' if changed else 'not change'}")
        return 0
    if changed:
        OUT.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {OUT.relative_to(REPO)}")
    else:
        print("up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
