#!/usr/bin/env python3
"""
gen_techtree_gates.py - render the AI's TECH-TREE capability gates.

[techtree-capability] Two questions the AI used to answer with the same tag list are separated
here, and neither is answered by a tag any more:

  WA_AI_TECHTREE_has_branch_<cap>  CAPABILITY   - does this country's TREE contain the branch?
  WA_AI_TECHTREE_has_<cap>         AVAILABILITY - does it hold a rung of that branch right now?

Both are built from tools/techtree_registry.json (capability -> folder -> rungs) and from the
membership triggers of WA_AI_TECHTREE_membership.txt (folder -> who owns it, generated straight
out of common/technology_tags/00_technology.txt). A country handed another country's tree by
event is therefore a full member of it here.

AVAILABILITY carries NO membership term, on purpose: 40 sites grant a national-tree rung to a
non-member without setting that tree's flag, so a tech held is a tech held. Membership answers
CAPABILITY only. Rungs under `granted` additionally live in no folder at all
(`allow = { always = no }`, reachable only through set_technology from a focus or an event).

Usage (any cwd; the mod root is derived from this file's location):
  python tools/gen/gen_techtree_gates.py --dry-run   # unified diff of what would change
  python tools/gen/gen_techtree_gates.py             # write the trigger file
  python tools/gen/gen_techtree_gates.py --check     # exit 1 out of sync, 2 on a BRANCH-GAP
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "tools" / "techtree_registry.json"
MEMBERSHIP = REPO / "common" / "scripted_triggers" / "WA_AI_TECHTREE_membership.txt"
DST = REPO / "common" / "scripted_triggers" / "WA_AI_TECHTREE_gates.txt"

HEADER = """\
# GENERATED FILE - do not edit by hand.
# Source: tools/techtree_registry.json, rendered by tools/gen/gen_techtree_gates.py
# (`--check` verifies, `--dry-run` previews, no flag writes). Retune the registry, not this file.
#
# [techtree-capability] OBSERVATION layer. Two questions, deliberately separate, neither answered
# by a country tag:
#
#   WA_AI_TECHTREE_has_branch_<cap>  CAPABILITY   - does this country's TREE contain the branch at all?
#   WA_AI_TECHTREE_has_<cap>         AVAILABILITY - does it hold a rung of that branch right now?
#
# `has_branch` is the one that replaces the hand-written tag lists ("ITA JAP GER" standing in for
# "the trees that have a light-TD branch"). It is built from tree MEMBERSHIP
# (WA_AI_TECHTREE_has_<folder>, WA_AI_TECHTREE_membership.txt, generated from
# common/technology_tags/00_technology.txt): tag OR tree flag, so a country handed another tree by
# event is a member of it here. `has_tech` cannot answer this question - a country that has not
# researched the branch yet is indistinguishable from one whose tree does not carry it.
#
# `has_<cap>` deliberately carries NO membership term. A tech you hold is a tech you hold, whatever
# tree it came from: 40 grant sites hand a national-tree rung to a non-member without setting that
# tree's flag (MEASURED - common/national_focus/finland.txt alone grants one rung from each of
# seven foreign trees; also bulgaria, canada, sweden, japan, turkey, history/CHI, ROM, the French
# colonies). ANDing membership into availability would have taken Finland's armour templates away.
# The tree grouping here is DATA, not a gate - it is what makes `has_branch` derivable.
#
# A folder absent from a capability is BARRED from `has_branch`: that tree has no such branch. That
# is a decision; --check reports a folder present in a sibling capability but absent here.
#
# These answer "what is true", never "should we act". The decision to build is the archetype's
# job (WA_AI_CONFIG) and the templates' gates - never this file's.
"""

FAMILY_SUFFIX = ("_armour_folder", "_artillery_folder", "_infantry_folder", "_air_techs_folder", "_naval_folder")


def family_of(folder: str) -> str:
    for suf in FAMILY_SUFFIX:
        if folder.endswith(suf):
            return suf[1:-7]
    if folder == "mtgnavalfolder":
        return "naval"
    if folder.endswith("_folder"):
        return folder[: -len("_folder")]
    return folder


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


def render(registry: dict) -> str:
    out = [HEADER]
    for cap, spec in registry["capabilities"].items():
        trees: dict[str, list[str]] = spec["trees"]
        granted: list[str] = spec.get("granted", [])
        note = spec.get("note")
        src = spec.get("source")

        out.append("\n\n")
        out.append(f"# ---- {cap} " + "-" * max(0, 96 - len(cap)) + "\n")
        if note:
            out.append(f"# {note}\n")
        if src:
            out.append(f"# Was: {src} (flat OR of every tree's rungs).\n")

        # CAPABILITY
        extra = spec.get("branch_extra", {})
        out.append(f"WA_AI_TECHTREE_has_branch_{cap} = {{\n\tOR = {{\n")
        for folder in trees:
            out.append(f"\t\tWA_AI_TECHTREE_has_{folder} = yes\n")
        if extra.get("folders"):
            for row in wrap(extra.get("reason", ""), 92):
                out.append(f"\t\t# {row}\n")
            for folder in extra["folders"]:
                out.append(f"\t\tWA_AI_TECHTREE_has_{folder} = yes\n")
        for tech in granted:
            out.append(f"\t\thas_tech = {tech}\n")
        out.append("\t}\n}\n\n")

        # AVAILABILITY
        out.append(f"WA_AI_TECHTREE_has_{cap} = {{\n\tOR = {{\n")
        for folder, rungs in trees.items():
            out.append(f"\t\t# {folder}\n")
            for tech in rungs:
                out.append(f"\t\thas_tech = {tech}\n")
        if granted:
            out.append("\t\t# granted only (no folder)\n")
            for tech in granted:
                out.append(f"\t\thas_tech = {tech}\n")
        out.append("\t}\n}\n")
    return "".join(out)


def tree_gaps(registry: dict) -> list[str]:
    """Folders that appear in a sibling capability of the same family but not in this one."""
    by_family: dict[str, set[str]] = {}
    for spec in registry["capabilities"].values():
        for folder in spec["trees"]:
            by_family.setdefault(family_of(folder), set()).add(folder)
    warns = []
    for cap, spec in registry["capabilities"].items():
        known = set(spec["trees"]) | set(spec.get("branch_extra", {}).get("folders", []))
        fams = {family_of(f) for f in spec["trees"]}
        for fam in sorted(fams):
            missing = sorted(by_family[fam] - known)
            if missing:
                warns.append(f"TREE-GAP  {cap} ({fam}): no rung for {', '.join(missing)}")
    return warns


# ---------------------------------------------------------------------------------------
# BRANCH-GAP: re-derive, from common/technologies/, folders that carry the branch
# ---------------------------------------------------------------------------------------
# [techtree-capability] This is the check that caught the real defect on the first pass: a folder
# whose rungs the old flat OR never listed is invisible to `trees`, so `has_branch` silently barred a
# country from weighting research for a technology it can actually reach (SOV / medium SPG). The
# candidate set is rebuilt from the tech files, never from the registry, so the registry cannot
# vouch for itself. A hit is a DECISION to record - either add the rungs to `trees`, or name the
# folder in `branch_extra` with its reason.

RE_PREFIX = re.compile(r"^[a-z]{3}_|^generic_")
RE_TAIL = re.compile(r"_?\d+(_\d+)?$")


def _shape(tech_id: str) -> str:
    """'ger_medium_spg_tank_4' -> 'medium_spg_tank' - the branch, without tree or rung number."""
    return RE_TAIL.sub("", RE_PREFIX.sub("", tech_id))


def branch_gaps(registry: dict, tech_folders: dict[str, list[str]]) -> list[str]:
    by_folder: dict[str, set[str]] = {}
    for tech, folders in tech_folders.items():
        for folder in folders:
            by_folder.setdefault(folder, set()).add(tech)
    warns = []
    for cap, spec in registry["capabilities"].items():
        shapes = {_shape(t) for r in spec["trees"].values() for t in r}
        known = set(spec["trees"]) | set(spec.get("branch_extra", {}).get("folders", []))
        fams = {family_of(f) for f in spec["trees"]}
        for folder in sorted(by_folder):
            if folder in known or family_of(folder) not in fams:
                continue
            hits = sorted(t for t in by_folder[folder] if _shape(t) in shapes)
            if hits:
                shown = ", ".join(hits[:4]) + (" ..." if len(hits) > 4 else "")
                warns.append(
                    f"BRANCH-GAP  {cap}: {folder} carries the branch ({len(hits)} rung(s): {shown}) "
                    f"but is in neither `trees` nor `branch_extra`")
    return warns


def tech_folders() -> dict[str, list[str]]:
    """tech id -> its technology folders, resolving `sub_technologies` to the parent's folder."""
    folders: dict[str, set[str]] = {}
    subs: dict[str, set[str]] = {}
    for path in sorted((REPO / "common" / "technologies").glob("*.txt")):
        text = "\n".join(l.split("#", 1)[0] for l in
                         path.read_text(encoding="utf-8-sig", errors="replace").split("\n"))
        m = re.search(r"\btechnologies\s*=\s*\{", text)
        if not m:
            continue
        start = m.end() - 1
        inner = text[start + 1: _match(text, start) - 1]
        i = 0
        while i < len(inner):
            mm = re.compile(r"([A-Za-z_]\w*)\s*=\s*\{").match(inner, i)
            if not mm:
                i += 1
                continue
            b0 = mm.end() - 1
            b1 = _match(inner, b0)
            body = inner[b0 + 1: b1 - 1]
            name = mm.group(1)
            folders.setdefault(name, set()).update(
                re.findall(r"folder\s*=\s*\{\s*name\s*=\s*(\w+)", body))
            st = re.search(r"sub_technologies\s*=\s*\{", body)
            if st:
                s0 = st.end() - 1
                subs.setdefault(name, set()).update(
                    re.findall(r"[A-Za-z_]\w*", body[s0 + 1: _match(body, s0) - 1]))
            i = b1
    for _ in range(6):  # sub-technologies inherit the parent's folder, possibly through a chain
        for parent, children in subs.items():
            for child in children:
                folders.setdefault(child, set()).update(folders.get(parent, ()))
    return {k: sorted(v) for k, v in folders.items()}


def _match(text: str, open_idx: int) -> int:
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
    raise ValueError("unbalanced brace")


def check_membership(registry: dict) -> list[str]:
    """Every folder the registry names must have a membership trigger."""
    text = MEMBERSHIP.read_text(encoding="utf-8") if MEMBERSHIP.exists() else ""
    missing = []
    for spec in registry["capabilities"].values():
        for folder in spec["trees"]:
            if f"WA_AI_TECHTREE_has_{folder} = {{" not in text:
                missing.append(folder)
    return sorted(set(missing))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print a unified diff, write nothing")
    ap.add_argument("--check", action="store_true", help="exit 1 if the output is out of sync")
    ap.add_argument("--quiet", action="store_true", help="suppress the TREE-GAP warnings")
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    missing = check_membership(registry)
    if missing:
        print("ERROR  no membership trigger for: " + ", ".join(missing), file=sys.stderr)
        print("       run tools/gen/gen_techtree_membership.py first", file=sys.stderr)
        return 2

    new = render(registry)
    old = DST.read_text(encoding="utf-8") if DST.exists() else ""

    gaps = branch_gaps(registry, tech_folders())
    for w in gaps:
        print("ERROR " + w, file=sys.stderr)
    if not args.quiet:
        for w in tree_gaps(registry):
            print("WARN  " + w)
    if gaps:
        print(f"       {len(gaps)} folder(s) carry a branch the capability gate does not admit -", file=sys.stderr)
        print("       add the rungs to `trees`, or name the folder in `branch_extra` with its reason", file=sys.stderr)
        return 2

    if args.check:
        if old == new:
            print(f"OK  {DST.relative_to(REPO)} in sync ({len(registry['capabilities'])} capabilities)")
            return 0
        print(f"STALE  {DST.relative_to(REPO)} - run tools/gen/gen_techtree_gates.py")
        return 1

    if args.dry_run:
        sys.stdout.writelines(difflib.unified_diff(
            old.splitlines(True), new.splitlines(True),
            fromfile=str(DST.relative_to(REPO)), tofile=str(DST.relative_to(REPO)) + " (new)"))
        return 0

    DST.write_text(new, encoding="utf-8", newline="\n")
    print(f"wrote {DST.relative_to(REPO)}  ({len(registry['capabilities'])} capabilities)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
