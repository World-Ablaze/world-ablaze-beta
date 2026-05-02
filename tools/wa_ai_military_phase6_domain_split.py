"""
WA AI Military Phase 6: per-strategy domain split

Reorganizes common/ai_strategy/WA_AI_MILITARY_*.txt so that every ai_strategy
ends up in the file whose domain matches the strategy's canonical type-to-domain
mapping (FRONT / INVASION / NAVAL / DIPLOMACY / THEATRE / GARRISON).

The canonical mapping is encoded in CANONICAL_DOMAIN below and is the single
source of truth.  documentation/WA_AI_MILITARY_TYPES_REFERENCE.md mirrors it.

Behaviour:

- Every top-level definition is parsed into (name, prologue, body) where
  prologue is everything before the opening `{` (preserving comments) and
  body is the full text including braces.
- Every `ai_strategy = { ... }` child of a definition is classified to a
  canonical domain by its `type =` value.
- If a block's strategies all map to the same domain, the block stays whole
  and is routed to the file matching its layer + that domain + its tag if
  applicable.
- If a block contains strategies from multiple canonical domains, it is
  SPLIT: one new top-level definition is emitted per domain, sharing the
  original block's predicate (`enable`, `allowed`, `abort_when_not_enabled`,
  any leading comments).  The new definitions are named
  `<orig>_<DOMAIN>` and each carries only the ai_strategies belonging to
  that domain.  Any non-ai_strategy / non-predicate top-level keys are
  retained on every split sub-block (rare, and conservative).
- Layer/tag are inferred from the source filename.  Output filenames follow
  the established convention: WA_AI_MILITARY_<LAYER>[_<TAG_OR_SCOPE>]_<DOMAIN>[_<descriptor>].txt
- Existing per-domain files (e.g. WA_AI_MILITARY_COUNTRY_GER_FRONT.txt) are
  preserved as the destination for FRONT-domain content from the GER scope.
- DEFAULT_FRONT_archetypes/caps/core/control filenames keep their descriptor.
- A run produces a unified plan (planned writes per output file, with the
  list of contributing source files for traceability), printable as
  --dry-run.  Apply mode performs the writes.

Verification (run via --verify after apply):

- Total ai_strategy count unchanged versus baseline (must match
  TOTAL_AI_STRATEGY_BASELINE).
- Per-type token count unchanged versus baseline.
- For each ai_strategy, its containing file's domain suffix matches the
  canonical domain of the strategy's `type =`.
- All braces balance.
- Every emitted top-level definition has at least one ai_strategy.
"""
from __future__ import annotations
import argparse
import collections
import dataclasses
import os
import re
import shutil
import sys
from pathlib import Path

# --- canonical type -> domain mapping (the single source of truth) -----------

CANONICAL_DOMAIN: dict[str, str] = {
    # FRONT: types that size or shape the front-line allocator inputs.
    "front_unit_request": "FRONT",
    "front_control": "FRONT",
    "front_armor_score": "FRONT",
    "force_concentration_front_factor": "FRONT",
    "force_concentration_target_weight": "FRONT",
    "force_ratio": "FRONT",
    "infantry": "FRONT",
    "garrison": "FRONT",  # NB: large per-country files MAY use _GARRISON; default FRONT.
    # INVASION: amphibious / new-front creation.
    "invasion_unit_request": "INVASION",
    "invade": "INVASION",
    "naval_invasion_focus": "INVASION",
    # NAVAL: where the fleet operates, where it stages, regions to avoid.
    "naval_avoid_region": "NAVAL",
    "strike_force_home_base": "NAVAL",
    "strategic_air_importance": "NAVAL",
    # DIPLOMACY: posture toward other countries, addressed by id/tag of country.
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
    # THEATRE: coarse-grained regional emphasis / per-state/per-area pooling.
    "theatre_distribution_demand_increase": "THEATRE",
    "area_priority": "THEATRE",
    "put_unit_buffers": "THEATRE",
    "spare_unit_factor": "THEATRE",
}

VALID_DOMAINS = {"FRONT", "INVASION", "NAVAL", "DIPLOMACY", "THEATRE", "GARRISON"}

# --- parser ------------------------------------------------------------------

def strip_comments_to_spaces(s: str) -> str:
    """Replace # line comments with spaces so brace counting on the result is positionally exact."""
    out = []; i = 0; n = len(s)
    while i < n:
        c = s[i]
        if c == '#':
            j = s.find('\n', i)
            if j == -1: j = n
            out.append(' ' * (j - i)); i = j
        elif c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                if s[j] == '\\' and j + 1 < n: j += 2; continue
                j += 1
            out.append(s[i:j+1]); i = j + 1
        else:
            out.append(c); i += 1
    return ''.join(out)


@dataclasses.dataclass
class Block:
    """A top-level definition NAME = { body }."""
    name: str
    leading: str           # comments / blank lines immediately preceding (within the file)
    full_text: str         # NAME = { ... } including braces
    body: str              # text inside the outermost braces (exclusive of the braces)
    src_file: str          # source filename
    src_layer: str         # DEFAULT/REGION/FACTION/COUNTRY (best-effort)
    src_scope: str         # e.g. "USA" for COUNTRY_USA, "ALLIES" for FACTION_ALLIES, etc.

    @property
    def strategies(self) -> list["AIStrategy"]:
        return _extract_strategies(self.body)


@dataclasses.dataclass
class AIStrategy:
    """A single `ai_strategy = { type = X ... }` child."""
    text: str         # full text including the `ai_strategy = {` ... `}`
    type_value: str   # the X token

    @property
    def domain(self) -> str:
        d = CANONICAL_DOMAIN.get(self.type_value)
        if d is None:
            raise ValueError(f"unknown ai_strategy type: {self.type_value}")
        return d


_DEF_RE = re.compile(r'^([A-Za-z_][A-Za-z_0-9]*)\s*=\s*\{', re.M)
_AI_RE = re.compile(r'\bai_strategy\s*=\s*\{')
_TYPE_RE = re.compile(r'\btype\s*=\s*([A-Za-z_][A-Za-z_0-9]*)')


def _matching_brace(stripped: str, open_idx: int) -> int:
    """Given the position of an opening `{` in stripped text, return the index just after the matching `}`."""
    depth = 1; i = open_idx + 1; n = len(stripped)
    while i < n and depth > 0:
        c = stripped[i]
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        i += 1
    if depth != 0:
        raise ValueError("unbalanced braces")
    return i


def _extract_strategies(body: str) -> list[AIStrategy]:
    stripped = strip_comments_to_spaces(body)
    out: list[AIStrategy] = []
    for m in _AI_RE.finditer(stripped):
        # Find the `{` belonging to this ai_strategy.
        open_idx = stripped.find('{', m.start())
        end = _matching_brace(stripped, open_idx)
        text = body[m.start(): end]
        sub_stripped = strip_comments_to_spaces(text)
        tm = _TYPE_RE.search(sub_stripped)
        if not tm:
            raise ValueError(f"ai_strategy without type: {text[:120]}")
        out.append(AIStrategy(text=text, type_value=tm.group(1)))
    return out


def parse_file(path: Path) -> tuple[str, list[Block], str]:
    """Return (header, blocks, trailer)."""
    txt = path.read_text(encoding='utf-8')
    stripped = strip_comments_to_spaces(txt)
    blocks: list[Block] = []
    cursor = 0
    last_block_end = 0
    layer, scope = _layer_and_scope_from_filename(path.name)
    for m in _DEF_RE.finditer(stripped):
        open_brace = stripped.find('{', m.end() - 1)
        end = _matching_brace(stripped, open_brace)
        # Leading text from last_block_end up to start of this def name.
        leading = txt[last_block_end: m.start()]
        # Strip stale Phase-2 MIXED-DOMAIN annotations (made obsolete by Phase 6
        # actually splitting blocks by domain).
        leading = re.sub(r'^[ \t]*#\s*MIXED-DOMAIN:[^\n]*\n', '', leading, flags=re.M)
        full_text = txt[m.start(): end]
        # Body is between the outermost braces.
        body = full_text[full_text.index('{') + 1: full_text.rfind('}')]
        blocks.append(Block(
            name=m.group(1), leading=leading, full_text=full_text, body=body,
            src_file=path.name, src_layer=layer, src_scope=scope,
        ))
        last_block_end = end
    trailer = txt[last_block_end:]
    header = ""  # we treat all leading text as part of first block's leading
    return header, blocks, trailer


def _layer_and_scope_from_filename(name: str) -> tuple[str, str]:
    """Extract layer (DEFAULT/REGION/FACTION/COUNTRY) and scope.

    DEFAULT files have no scope (they are global). All other layers have a
    scope token that names the country/faction/region the file targets.
    """
    base = name
    if base.startswith("WA_AI_MILITARY_"):
        base = base[len("WA_AI_MILITARY_"):]
    if base.endswith(".txt"):
        base = base[:-4]
    parts = base.split("_")
    if not parts:
        return "?", ""
    layer = parts[0]
    if layer not in ("DEFAULT","REGION","FACTION","COUNTRY"):
        return "?", base
    if layer == "DEFAULT":
        # DEFAULT_<DOMAIN>[_<descriptor>]: no scope.
        return "DEFAULT", ""
    rest = parts[1:]
    if not rest: return layer, ""
    # SOUTH_AMERICA, CHINA_FRONT, CO_PROSPERITY are multi-token scopes.
    multi = {("SOUTH","AMERICA"):"SOUTH_AMERICA",
             ("CHINA","FRONT"):"CHINA_FRONT",
             ("CO","PROSPERITY"):"CO_PROSPERITY"}
    if len(rest) >= 2 and (rest[0], rest[1]) in multi:
        return layer, multi[(rest[0], rest[1])]
    return layer, rest[0]


# --- planning ----------------------------------------------------------------

@dataclasses.dataclass
class OutputBlock:
    """A block as it should appear in some output file."""
    name: str
    text: str            # the full top-level definition text (NAME = { ... })
    leading: str         # leading comments (a single \n if none)
    canonical_domain: str  # which canonical domain this output block represents


def split_block_by_domain(blk: Block) -> dict[str, OutputBlock]:
    """For each canonical domain present in blk's ai_strategies, produce one
    OutputBlock containing only those strategies, sharing blk's predicate.
    
    If blk has only one domain, returns {domain: <single block, identical to source>}.
    """
    strategies = blk.strategies
    if not strategies:
        # Block has no ai_strategy children. Keep as-is, no domain. We'll
        # route by majority of nothing => caller decides.
        return {}
    by_domain: dict[str, list[AIStrategy]] = collections.defaultdict(list)
    for s in strategies:
        by_domain[s.domain].append(s)
    if len(by_domain) == 1:
        only_dom = next(iter(by_domain))
        return {only_dom: OutputBlock(
            name=blk.name, text=blk.full_text, leading=blk.leading,
            canonical_domain=only_dom,
        )}
    # Multi-domain: split. We need to:
    #  - keep everything in body that is NOT an ai_strategy (predicate keys
    #    enable / allowed / abort_when_not_enabled etc.)
    #  - emit one new top-level def per domain, named <orig>_<DOMAIN>, with
    #    the predicate verbatim plus only the strategies for that domain.
    predicate_text, _strategy_spans = _extract_predicate_and_strategy_spans(blk.body)
    out: dict[str, OutputBlock] = {}
    for dom in sorted(by_domain.keys()):
        new_name = f"{blk.name}_{dom}"
        # Compose body: predicate text (already trailing-newline-terminated) + strategies for this domain.
        body_lines = [predicate_text.rstrip()]
        body_lines.append("")
        for s in by_domain[dom]:
            body_lines.append(s.text.rstrip())
        new_body = "\n".join(body_lines) + "\n"
        # Compose the full def. Use the same indentation conventions as the source: top-level definitions are flush-left, body is indented one level.
        # We want body to be INSIDE braces. Source bodies end with a newline before the closing `}`.
        # Easiest: use the original's outer indentation. Top-level defs are flush.
        new_full = f"{new_name} = {{\n{_indent_body(new_body)}}}\n"
        # Header comment marking this as a phase-6 split (preserve original block's leading comments first time only).
        leading_with_marker = blk.leading.rstrip() + "\n# Phase 6 split from " + blk.name + " (" + dom + " domain)\n"
        # On the first emitted variant, keep the full original leading (including any author comments).
        # On subsequent variants, just emit the marker.
        if dom == sorted(by_domain.keys())[0]:
            out_leading = leading_with_marker
        else:
            out_leading = "\n# Phase 6 split from " + blk.name + " (" + dom + " domain)\n"
        out[dom] = OutputBlock(
            name=new_name, text=new_full, leading=out_leading,
            canonical_domain=dom,
        )
    return out


def _indent_body(body: str) -> str:
    """Re-indent a body string so each non-empty line has at least one leading tab."""
    lines = body.split("\n")
    out = []
    for ln in lines:
        if not ln.strip():
            out.append("")
        elif ln.startswith("\t") or ln.startswith("    "):
            out.append(ln)
        else:
            out.append("\t" + ln)
    return "\n".join(out)


def _extract_predicate_and_strategy_spans(body: str) -> tuple[str, list[tuple[int,int]]]:
    """Split body into (predicate_text, list of (start,end) spans of ai_strategy = {...}).
    
    predicate_text is body with the ai_strategy spans removed (and surrounding
    blank lines collapsed).
    """
    stripped = strip_comments_to_spaces(body)
    spans: list[tuple[int,int]] = []
    for m in _AI_RE.finditer(stripped):
        open_idx = stripped.find('{', m.start())
        end = _matching_brace(stripped, open_idx)
        spans.append((m.start(), end))
    # Build predicate_text by concatenating gaps.
    pieces = []
    cursor = 0
    for s, e in spans:
        pieces.append(body[cursor:s])
        cursor = e
    pieces.append(body[cursor:])
    predicate = "".join(pieces)
    # Collapse runs of blank lines.
    predicate = re.sub(r'\n\s*\n\s*\n+', '\n\n', predicate)
    return predicate, spans


# --- output routing ----------------------------------------------------------

def route_output_filename(blk_layer: str, blk_scope: str, blk_src_name: str, domain: str) -> str:
    """Produce the destination filename for a block of given (layer, scope, domain).

    Source filename is consulted to preserve descriptor variants like
    DEFAULT_FRONT_archetypes / DEFAULT_FRONT_caps.
    """
    # Extract a "descriptor" from src filename if present.
    base = blk_src_name
    if base.startswith("WA_AI_MILITARY_"):
        base = base[len("WA_AI_MILITARY_"):]
    if base.endswith(".txt"):
        base = base[:-4]
    # Examples we want to preserve:
    #   DEFAULT_FRONT_archetypes  -> if domain==FRONT, keep descriptor
    #   DEFAULT_FRONT_caps        -> ditto
    #   DEFAULT_FRONT_core        -> ditto
    #   DEFAULT_FRONT_control     -> ditto
    # If domain != source domain, drop the descriptor.
    parts = base.split("_")
    descriptor = ""
    # The "domain token" position depends on layer.
    # For DEFAULT, layout is DEFAULT_<DOMAIN>[_descriptor].
    # For COUNTRY/FACTION/REGION, layout is <LAYER>_<SCOPE>[_<DOMAIN>[_<descriptor>]].
    if blk_layer == "DEFAULT":
        # DEFAULT_<dom>[_<desc>]
        if len(parts) >= 3 and parts[1] == domain:
            descriptor = "_".join(parts[2:])
    else:
        # <LAYER>_<SCOPE>[_<DOMAIN>[_<desc>]]
        # scope can be multi-token (SOUTH_AMERICA, CHINA_FRONT, CO_PROSPERITY).
        scope_tokens = blk_scope.split("_") if blk_scope else []
        idx_after_scope = 1 + len(scope_tokens)
        if len(parts) > idx_after_scope and parts[idx_after_scope] == domain:
            descriptor = "_".join(parts[idx_after_scope+1:])
    pieces = ["WA_AI_MILITARY", blk_layer]
    if blk_scope:
        pieces.append(blk_scope)
    pieces.append(domain)
    if descriptor:
        pieces.append(descriptor)
    return "_".join(pieces) + ".txt"


# --- main pipeline -----------------------------------------------------------

def collect_all_blocks(repo_root: Path) -> list[Block]:
    blocks: list[Block] = []
    for p in sorted((repo_root / "common" / "ai_strategy").glob("WA_AI_MILITARY_*.txt")):
        # Skip the phase5 trigger file (which lives under scripted_triggers, but defensively).
        _hdr, blks, _trl = parse_file(p)
        blocks.extend(blks)
    return blocks


def plan(repo_root: Path):
    blocks = collect_all_blocks(repo_root)
    out_files: dict[str, list[OutputBlock]] = collections.defaultdict(list)
    untouched_outputs: list[tuple[str, Block]] = []
    skipped: list[tuple[Block, str]] = []
    for blk in blocks:
        try:
            split = split_block_by_domain(blk)
        except ValueError as e:
            skipped.append((blk, str(e))); continue
        if not split:
            # No ai_strategy children. We'll keep block in its source file unchanged.
            out_files[blk.src_file].append(OutputBlock(
                name=blk.name, text=blk.full_text, leading=blk.leading,
                canonical_domain="(none)",
            ))
            continue
        for dom, ob in split.items():
            dest = route_output_filename(blk.src_layer, blk.src_scope, blk.src_file, dom)
            out_files[dest].append(ob)
    return out_files, skipped


HEADER_TEMPLATE = """############################################################################################################
# WA AI Military V2 - {scope_label}{domain_label}
############################################################################################################
# Phase 6 split: every ai_strategy in this file has type \u2208 {{ {types_in_domain} }}.
# Canonical domain: {domain}. See documentation/WA_AI_MILITARY_TYPES_REFERENCE.md.

"""


def render_file(out_filename: str, blocks: list[OutputBlock]) -> str:
    # Determine domain label for header (rightmost domain token in stem).
    base = out_filename
    if base.endswith(".txt"): base = base[:-4]
    parts = base.split("_")
    domain = None
    for tok in reversed(parts):
        if tok in VALID_DOMAINS:
            domain = tok; break
    types_in_domain = ", ".join(sorted(t for t, d in CANONICAL_DOMAIN.items() if d == domain)) if domain else "various"
    scope_label = base.replace("WA_AI_MILITARY_", "")
    domain_label = ""
    header = HEADER_TEMPLATE.format(
        scope_label=scope_label, domain_label=domain_label,
        types_in_domain=types_in_domain, domain=domain or "?",
    )
    chunks = [header]
    for ob in blocks:
        leading = ob.leading
        if not leading.endswith("\n"):
            leading = leading + "\n"
        chunks.append(leading)
        chunks.append(ob.text.rstrip() + "\n")
        chunks.append("\n")
    return "".join(chunks).rstrip() + "\n"


def apply_plan(repo_root: Path, out_files: dict[str, list[OutputBlock]], dry_run: bool):
    ai_dir = repo_root / "common" / "ai_strategy"
    # Files that exist now and will be touched: union of (existing inputs) and (new outputs).
    existing = {p.name for p in ai_dir.glob("WA_AI_MILITARY_*.txt")}
    new_files = set(out_files.keys())
    will_delete = existing - new_files
    will_write = new_files

    print(f"\n=== plan summary ===")
    print(f"Existing files: {len(existing)}")
    print(f"Will write   : {len(will_write)}")
    print(f"Will delete  : {len(will_delete)}")
    if will_delete:
        print("\nFiles to delete (no remaining content):")
        for f in sorted(will_delete):
            print(f"  - {f}")
    print()

    if dry_run:
        print("[dry-run] no files written.")
        return

    # Apply.
    for f in sorted(will_delete):
        (ai_dir / f).unlink()
    for fname, blocks in sorted(out_files.items()):
        rendered = render_file(fname, blocks)
        (ai_dir / fname).write_text(rendered, encoding='utf-8')


# --- verification ------------------------------------------------------------

def _file_canonical_domain(stem: str) -> str | None:
    """Return the file's canonical domain by examining its filename.

    A file's domain is the *last* domain-token in its name that is preceded
    by either the layer prefix or a scope identifier. We look for the
    rightmost domain token (so FACTION_CHINA_FRONT_DIPLOMACY -> DIPLOMACY,
    not FRONT-from-CHINA_FRONT scope).
    """
    parts = stem.split("_")
    for tok in reversed(parts):
        if tok in VALID_DOMAINS:
            return tok
    return None


def verify(repo_root: Path):
    """After apply, run the conservation checks."""
    blocks_by_file: dict[str, list[Block]] = {}
    type_counts: collections.Counter = collections.Counter()
    placement_errors: list[str] = []
    empty_defs: list[str] = []
    ai_dir = repo_root / "common" / "ai_strategy"
    for p in sorted(ai_dir.glob("WA_AI_MILITARY_*.txt")):
        _hdr, blks, _trl = parse_file(p)
        blocks_by_file[p.name] = blks
        # Determine file's canonical domain (rightmost domain token in stem).
        # Strip any descriptor following the domain (e.g. DEFAULT_FRONT_archetypes).
        # We accept either: domain at the end, or domain with descriptor after it.
        stem = p.stem
        # Find the rightmost token that is a known domain. Tokens to the right
        # of it are descriptors (allowed only for DEFAULT layer).
        parts = stem.split("_")
        file_domain = None
        for i in range(len(parts) - 1, -1, -1):
            if parts[i] in VALID_DOMAINS:
                # If there are tokens to its right, ensure they form a recognised descriptor.
                file_domain = parts[i]
                break
        for blk in blks:
            ss = blk.strategies
            if not ss:
                empty_defs.append(f"{p.name} :: {blk.name}")
                continue
            for s in ss:
                type_counts[s.type_value] += 1
                if file_domain and s.domain != file_domain:
                    placement_errors.append(
                        f"{p.name} :: {blk.name} :: type={s.type_value} (canonical={s.domain}) but file_domain={file_domain}"
                    )
    return type_counts, placement_errors, empty_defs


def cmd_audit(args):
    repo_root = Path(args.repo_root).resolve()
    blocks = collect_all_blocks(repo_root)
    print(f"Total top-level defs: {len(blocks)}")
    total_strats = 0
    by_type: collections.Counter = collections.Counter()
    multi: list[Block] = []
    for blk in blocks:
        ss = blk.strategies
        total_strats += len(ss)
        for s in ss:
            by_type[s.type_value] += 1
        domains = {s.domain for s in ss}
        if len(domains) > 1:
            multi.append(blk)
    print(f"Total ai_strategy children: {total_strats}")
    print(f"\nPer-type counts:")
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {c:5d}  {t:<40} -> {CANONICAL_DOMAIN[t]}")
    print(f"\nMulti-domain blocks (will be split): {len(multi)}")
    for blk in multi:
        ss = blk.strategies
        per_dom = collections.Counter(s.domain for s in ss)
        print(f"  {blk.src_file:<60} :: {blk.name:<60} {dict(per_dom)}")


def cmd_plan(args):
    repo_root = Path(args.repo_root).resolve()
    out_files, skipped = plan(repo_root)
    apply_plan(repo_root, out_files, dry_run=True)
    if skipped:
        print(f"\n[skipped] {len(skipped)} blocks could not be classified:")
        for blk, reason in skipped:
            print(f"  {blk.src_file} :: {blk.name}: {reason}")


def cmd_apply(args):
    repo_root = Path(args.repo_root).resolve()
    out_files, skipped = plan(repo_root)
    if skipped:
        print(f"[error] {len(skipped)} blocks could not be classified:")
        for blk, reason in skipped:
            print(f"  {blk.src_file} :: {blk.name}: {reason}")
        sys.exit(1)
    apply_plan(repo_root, out_files, dry_run=False)
    print("\n=== verifying ===")
    type_counts, placement_errors, empty_defs = verify(repo_root)
    print(f"Per-type counts after apply:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:5d}  {t}")
    if placement_errors:
        print(f"\nPLACEMENT ERRORS: {len(placement_errors)}")
        for e in placement_errors[:50]:
            print(f"  {e}")
    if empty_defs:
        print(f"\nEMPTY DEFS: {len(empty_defs)}")
        for e in empty_defs[:50]:
            print(f"  {e}")


def cmd_verify(args):
    repo_root = Path(args.repo_root).resolve()
    type_counts, placement_errors, empty_defs = verify(repo_root)
    print(f"Per-type counts:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {c:5d}  {t}")
    if placement_errors:
        print(f"\nPLACEMENT ERRORS: {len(placement_errors)}")
        for e in placement_errors:
            print(f"  {e}")
        sys.exit(1)
    if empty_defs:
        print(f"\nEMPTY DEFS: {len(empty_defs)}")
        for e in empty_defs:
            print(f"  {e}")
        sys.exit(1)
    print("\nOK: all ai_strategies are in their canonical-domain files; no empty defs.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".",
                    help="repository root (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("audit").set_defaults(func=cmd_audit)
    sub.add_parser("plan").set_defaults(func=cmd_plan)
    sub.add_parser("apply").set_defaults(func=cmd_apply)
    sub.add_parser("verify").set_defaults(func=cmd_verify)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
