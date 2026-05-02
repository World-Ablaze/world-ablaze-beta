#!/usr/bin/env python3
"""
WA AI Military Phase 2 splitter.

Renames legacy/mis-prefixed files and splits multi-domain country/faction files
into per-domain files, per `documentation/WA_AI_MILITARY_SYSTEM.md`.

NO LOGIC CHANGES. Block contents and ordering within a destination file are
preserved exactly. Header comments at the top of a source file are duplicated
onto every destination file so context is not lost.

NOTE (post-Phase 6): This Phase 2 tool routes each ai_strategy *block* to a
single domain by majority vote of its `type =` values. Phase 6 supersedes that
by physically splitting blocks whose contents touch multiple domains. The
canonical TYPE -> DOMAIN mapping below is the same one used by Phase 6 and is
the single source of truth: `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md`
(top-of-file table) plus `tools/wa_ai_military_phase6_domain_split.py`
(`CANONICAL_DOMAIN` dict). Keep all three in sync.

Usage:
    python wa_ai_military_phase2_split.py --dry-run
    python wa_ai_military_phase2_split.py --apply
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# --- type -> domain mapping (matches WA_AI_MILITARY_SYSTEM.md section 3) ----
TYPE_TO_DOMAIN: dict[str, str] = {
    # FRONT
    "front_unit_request": "FRONT",
    "front_control": "FRONT",
    "front_armor_score": "FRONT",
    "force_concentration_front_factor": "FRONT",
    "force_concentration_target_weight": "FRONT",
    "force_ratio": "FRONT",
    "infantry": "FRONT",
    "garrison": "FRONT",  # default; large garrison-only files can split out manually
    # INVASION
    "invasion_unit_request": "INVASION",
    "invade": "INVASION",
    "naval_invasion_focus": "INVASION",
    # NAVAL
    "naval_avoid_region": "NAVAL",
    "strike_force_home_base": "NAVAL",
    "strategic_air_importance": "NAVAL",
    # DIPLOMACY
    "conquer": "DIPLOMACY",
    "antagonize": "DIPLOMACY",
    "protect": "DIPLOMACY",
    "contain": "DIPLOMACY",
    "ignore": "DIPLOMACY",
    "ignore_claim": "DIPLOMACY",
    "declare_war": "DIPLOMACY",
    "diplo_action_desire": "DIPLOMACY",
    "diplo_action_acceptance": "DIPLOMACY",
    "dont_defend_ally_borders": "DIPLOMACY",
    "force_defend_ally_borders": "DIPLOMACY",
    # THEATRE
    "theatre_distribution_demand_increase": "THEATRE",
    "area_priority": "THEATRE",
    "put_unit_buffers": "THEATRE",
    "spare_unit_factor": "THEATRE",
}

# --- file rename map ---------------------------------------------------------
# Renames that are NOT also splits. Files that get split below are not in here.
RENAMES: dict[str, str] = {
    "WA_AI_MILITARY_FRONT_archetypes.txt": "WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt",
    "WA_AI_MILITARY_FRONT_caps.txt":       "WA_AI_MILITARY_DEFAULT_FRONT_caps.txt",
    "WA_AI_MILITARY_FRONT_core.txt":       "WA_AI_MILITARY_DEFAULT_FRONT_core.txt",
    "WA_AI_MILITARY_FRONT_execution.txt":  "WA_AI_MILITARY_DEFAULT_FRONT_control.txt",
    "WA_AI_MILITARY_INVASION_budget.txt":  "WA_AI_MILITARY_DEFAULT_INVASION.txt",
}

# Layer prefix mapping for sources that need to switch layer prefix as part of
# the split. Key: source filename. Value: (layer, base_name).
LAYER_REMAP: dict[str, tuple[str, str]] = {
    "WA_AI_MILITARY_COUNTRY_ALLIES.txt":         ("FACTION", "ALLIES"),
    "WA_AI_MILITARY_COUNTRY_AXIS.txt":           ("FACTION", "AXIS"),
    "WA_AI_MILITARY_COUNTRY_CHINA_FRONT.txt":    ("FACTION", "CHINA_FRONT"),
    "WA_AI_MILITARY_COUNTRY_COMINTERN.txt":      ("FACTION", "COMINTERN"),
    "WA_AI_MILITARY_COUNTRY_CO_PROSPERITY.txt":  ("FACTION", "CO_PROSPERITY"),
    "WA_AI_MILITARY_COUNTRY_SOUTH_AMERICA.txt":  ("REGION",  "SOUTH_AMERICA"),
}

# Empty files to delete outright. (None at this time; the supposedly-empty
# COMINTERN and CO_PROSPERITY files turned out to contain real faction content.)
DELETIONS: set[str] = set()

# --- parser ------------------------------------------------------------------

@dataclass
class Block:
    """A top-level definition: NAME = { ... }."""
    name: str
    text: str            # full source text including the NAME = { and trailing }
    leading: str         # comments / blank lines immediately preceding (within the file)
    types: Counter       # Counter of `type = X` occurrences inside ai_strategy children
    domain: str = ""     # assigned destination domain
    mixed: bool = False  # had multiple domains; routed to majority

    @property
    def domains(self) -> set[str]:
        return {TYPE_TO_DOMAIN[t] for t in self.types if t in TYPE_TO_DOMAIN}


def strip_comments_and_strings(s: str) -> str:
    """Replace # line comments and "..." strings with spaces of the same length
    so brace counting on the result matches positions in the original."""
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "#":
            j = s.find("\n", i)
            if j == -1: j = n
            out.append(" " * (j - i))
            i = j
        elif c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                if s[j] == "\\" and j + 1 < n:
                    j += 2
                else:
                    j += 1
            j = min(j + 1, n)
            out.append(" " * (j - i))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


DEF_RE = re.compile(r"([A-Za-z_][A-Za-z_0-9]*)\s*=\s*\{")


def parse_blocks(text: str) -> tuple[str, list[Block]]:
    """Return (file_header, [Block, ...]).
    file_header is the comment/blank-line preamble before the first definition."""
    scrub = strip_comments_and_strings(text)
    blocks: list[Block] = []
    pos = 0
    file_header: str | None = None
    while True:
        m = DEF_RE.search(scrub, pos)
        if not m:
            break
        # Walk back to capture leading comments/blank lines from end of previous
        # block (or start of file).
        leading_start = pos
        leading = text[leading_start:m.start()]
        # Find matching brace for this definition.
        depth = 0
        i = m.end() - 1  # the '{'
        end = -1
        while i < len(scrub):
            ch = scrub[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
            i += 1
        if end == -1:
            raise RuntimeError(f"Unbalanced braces starting at offset {m.start()}")
        block_text = text[m.start():end]
        # Find type = X tokens inside, restricted to ai_strategy children of
        # this top-level block. Simpler: find every `type = <ident>` whose
        # surrounding ai_strategy = { ... } we are inside. Cheap proxy: count
        # all `type = <ident>` in block_text; in practice these only appear
        # inside ai_strategy blocks.
        types = Counter(re.findall(r"\btype\s*=\s*([A-Za-z_][A-Za-z_0-9]*)", strip_comments_and_strings(block_text)))
        if file_header is None:
            file_header = leading
            leading_for_block = ""
        else:
            leading_for_block = leading
        blocks.append(Block(name=m.group(1), text=block_text, leading=leading_for_block, types=types))
        pos = end
    if file_header is None:
        file_header = text  # nothing parsed; whole file is "header"
    return file_header, blocks


def assign_domain(block: Block) -> None:
    if not block.types:
        # No ai_strategy children. Route to FRONT by convention; rare.
        block.domain = "FRONT"
        return
    domain_counts: Counter = Counter()
    for t, n in block.types.items():
        d = TYPE_TO_DOMAIN.get(t)
        if d:
            domain_counts[d] += n
    if not domain_counts:
        block.domain = "FRONT"
        return
    # majority domain; ties broken by FRONT > INVASION > NAVAL > DIPLOMACY > THEATRE > GARRISON.
    order = ["FRONT", "INVASION", "NAVAL", "DIPLOMACY", "THEATRE", "GARRISON"]
    top = max(domain_counts.items(), key=lambda kv: (kv[1], -order.index(kv[0])))
    block.domain = top[0]
    block.mixed = len(domain_counts) > 1


# --- planning ----------------------------------------------------------------

@dataclass
class FilePlan:
    src: Path
    action: str  # "rename", "split", "delete", "rename-and-split"
    layer: str   # DEFAULT / REGION / FACTION / COUNTRY
    base: str    # e.g. USA, ALLIES, SOUTH_AMERICA
    file_header: str = ""
    blocks_by_domain: dict[str, list[Block]] = field(default_factory=dict)
    rename_target: str = ""  # for pure rename
    notes: list[str] = field(default_factory=list)


def detect_layer_and_base(filename: str) -> tuple[str, str] | None:
    """Determine (layer, base) for a source file."""
    if filename in LAYER_REMAP:
        return LAYER_REMAP[filename]
    m = re.match(r"WA_AI_MILITARY_COUNTRY_([A-Z_]+)\.txt$", filename)
    if m:
        return ("COUNTRY", m.group(1))
    return None  # not a country/faction/region split candidate


def plan(ai_strat_dir: Path) -> list[FilePlan]:
    plans: list[FilePlan] = []
    for src in sorted(ai_strat_dir.glob("WA_AI_MILITARY_*.txt")):
        name = src.name
        if name in DELETIONS:
            plans.append(FilePlan(src=src, action="delete", layer="", base=""))
            continue
        if name in RENAMES:
            p = FilePlan(src=src, action="rename", layer="", base="")
            p.rename_target = RENAMES[name]
            plans.append(p)
            continue
        layer_base = detect_layer_and_base(name)
        if layer_base is None:
            # Not in our known set. Leave alone but record.
            p = FilePlan(src=src, action="leave", layer="", base="")
            p.notes.append("not in any phase-2 rule")
            plans.append(p)
            continue
        layer, base = layer_base
        text = src.read_text(encoding="utf-8")
        header, blocks = parse_blocks(text)
        for b in blocks:
            assign_domain(b)
        by_domain: dict[str, list[Block]] = {}
        for b in blocks:
            by_domain.setdefault(b.domain, []).append(b)
        action = "rename-and-split" if name in LAYER_REMAP else "split"
        p = FilePlan(
            src=src,
            action=action,
            layer=layer,
            base=base,
            file_header=header,
            blocks_by_domain=by_domain,
        )
        # Pull out unique mixed-domain blocks for the manifest.
        for b in blocks:
            if b.mixed:
                doms = sorted(b.domains)
                p.notes.append(
                    f"mixed-domain: {b.name} -> {b.domain} (also touches {', '.join(d for d in doms if d != b.domain)})"
                )
        plans.append(p)
    return plans


# --- execution ---------------------------------------------------------------

def out_filename(layer: str, base: str, domain: str, single_domain: bool) -> str:
    if layer == "DEFAULT":
        return f"WA_AI_MILITARY_DEFAULT_{domain}.txt"
    if layer == "REGION":
        # Region files don't always need a domain suffix when a single domain.
        if single_domain:
            return f"WA_AI_MILITARY_REGION_{base}.txt"
        return f"WA_AI_MILITARY_REGION_{base}_{domain}.txt"
    if layer == "FACTION":
        if single_domain:
            return f"WA_AI_MILITARY_FACTION_{base}.txt"
        return f"WA_AI_MILITARY_FACTION_{base}_{domain}.txt"
    if layer == "COUNTRY":
        if single_domain:
            return f"WA_AI_MILITARY_COUNTRY_{base}.txt"
        return f"WA_AI_MILITARY_COUNTRY_{base}_{domain}.txt"
    raise ValueError(layer)


def render_destination(file_header: str, domain: str, blocks: list[Block]) -> str:
    parts = [file_header.rstrip() + "\n"] if file_header.strip() else []
    parts.append(f"# Phase 2 split: {domain} domain blocks.\n\n")
    for b in blocks:
        if b.leading.strip():
            parts.append(b.leading.lstrip("\n"))
        if b.mixed:
            others = sorted(d for d in b.domains if d != b.domain)
            parts.append(
                f"# MIXED-DOMAIN: routed to {b.domain}; also touches {', '.join(others)}.\n"
            )
        # Inline TODO for the CHINA_FRONT SIC block (Phase 3 re-home target).
        if b.name == "WA_AI_MILITARY_CHINA_FRONT_sic_support_chi_against_japan":
            parts.append(
                "# TODO Phase 3: this block is country-specific (allowed = { tag = SIC })\n"
                "# and should be re-homed to WA_AI_MILITARY_COUNTRY_SIC_DIPLOMACY.txt once\n"
                "# the chinese-warlord archetype trigger work lands. Left in place so it\n"
                "# moves together with the warlord OR-tag-list block in Phase 3.\n"
            )
        parts.append(b.text)
        if not b.text.endswith("\n"):
            parts.append("\n")
        parts.append("\n")
    return "".join(parts)


def apply_plan(plans: list[FilePlan], ai_strat_dir: Path) -> None:
    written: list[Path] = []
    deleted: list[Path] = []
    for p in plans:
        if p.action == "leave":
            continue
        if p.action == "delete":
            p.src.unlink()
            deleted.append(p.src)
            continue
        if p.action == "rename":
            tgt = ai_strat_dir / p.rename_target
            shutil.move(str(p.src), str(tgt))
            written.append(tgt)
            continue
        if p.action in ("split", "rename-and-split"):
            single = len(p.blocks_by_domain) == 1
            for domain, blocks in sorted(p.blocks_by_domain.items()):
                fname = out_filename(p.layer, p.base, domain, single)
                tgt = ai_strat_dir / fname
                content = render_destination(p.file_header, domain, blocks)
                tgt.write_text(content, encoding="utf-8")
                written.append(tgt)
            # Original file deleted only if its name differs from any output.
            output_names = {
                out_filename(p.layer, p.base, d, len(p.blocks_by_domain) == 1)
                for d in p.blocks_by_domain
            }
            if p.src.name not in output_names:
                p.src.unlink()
                deleted.append(p.src)
    print(f"Wrote {len(written)} files, deleted {len(deleted)} files.")


# --- manifest ---------------------------------------------------------------

def print_manifest(plans: list[FilePlan]) -> None:
    print("=" * 80)
    print("PHASE 2 MANIFEST")
    print("=" * 80)
    total_blocks = 0
    total_mixed = 0
    for p in plans:
        if p.action == "leave":
            print(f"[leave]    {p.src.name}")
            continue
        if p.action == "delete":
            print(f"[delete]   {p.src.name}  (empty)")
            continue
        if p.action == "rename":
            print(f"[rename]   {p.src.name}  ->  {p.rename_target}")
            continue
        single = len(p.blocks_by_domain) == 1
        tag = "rename-split" if p.action == "rename-and-split" else "split"
        n = sum(len(v) for v in p.blocks_by_domain.values())
        total_blocks += n
        nm = sum(1 for v in p.blocks_by_domain.values() for b in v if b.mixed)
        total_mixed += nm
        print(f"[{tag:12s}] {p.src.name}  ({n} blocks, {nm} mixed-domain)")
        for d, blocks in sorted(p.blocks_by_domain.items()):
            tgt = out_filename(p.layer, p.base, d, single)
            print(f"             -> {tgt}  ({len(blocks)} blocks)")
        for note in p.notes:
            print(f"             note: {note}")
    print("-" * 80)
    print(f"Total blocks moved: {total_blocks}; mixed-domain blocks: {total_mixed}")


# --- main --------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ai-strat-dir", default=None,
                    help="Override path to common/ai_strategy")
    args = ap.parse_args(argv)

    if not (args.dry_run or args.apply):
        ap.error("specify --dry-run or --apply")

    if args.ai_strat_dir:
        ai_strat = Path(args.ai_strat_dir)
    else:
        # Default: ../common/ai_strategy relative to this script.
        ai_strat = Path(__file__).resolve().parent.parent / "common" / "ai_strategy"
    if not ai_strat.is_dir():
        print(f"ai_strategy dir not found: {ai_strat}", file=sys.stderr)
        return 2

    plans = plan(ai_strat)
    print_manifest(plans)
    if args.apply:
        apply_plan(plans, ai_strat)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
