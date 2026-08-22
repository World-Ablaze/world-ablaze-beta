"""
Turn air and modular-tank verdicts into reviewable `ai_equipment` patches.

REPORT-ONLY BY DEFAULT, like the rest of this package and like every other
generator under `tools/` (see the `wa-tooling` skill: dry run, read the diff,
then apply). `--emit` writes a patch document to `output/`; nothing is written
into `common/` unless `--emit-apply` is passed as well.

What it emits
-------------
1. RESOURCE GATES (`SWITCH_CONDITIONAL`). The mod's supersession idiom is a
   blanket `modifier = { has_tech = <next> factor = 0 }` on the older design -
   "the moment the next tech lands, stop building this". When the newer design
   costs materially more of a strategic resource per unit, that supersession
   should wait for the economy. Two insertions reproduce the hand-written
   Fix 47 / Fix 49 arrangement exactly:

     on the OLD design   add the gate to the modifier that kills it, so it is
                         retained while the gate is shut
     on the NEW design   add `modifier = { NOT = { <gate> } factor = 0 }`, so
                         the expensive design is unavailable while it is shut

   The gate names come from `common/scripted_triggers/WA_AI_EQUIPMENT_triggers.txt`
   (the Fix 47 vocabulary). Emitting anything else there would be inventing a
   contract; if a resource has no gate the transition is reported as blocked,
   never silently dropped.

2. MODULE LISTS (`SWITCH_REDESIGNED`). The redesign search already produces a
   concrete slot -> module map that restores range; this rewrites the new
   design's `target_variant.modules` to match it.

Both are produced as anchored text insertions against the file as written -
comments, tabs and all - so a reviewer diffs them against real line numbers.
Designs already carrying `WA_AI_EQUIPMENT_` conditions (the Fix 47/49 pilots)
are never touched.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Optional, Set, Tuple

from .config import Config
from .decision_policy import (ADOPTION_VERDICTS, KEEP_OLD, PARALLEL_VARIANT,
                              UNRESOLVED)
from .decide import SWITCH_CONDITIONAL, SWITCH_REDESIGNED, Transition
from .diagnostics import Diagnostics
from .parse_ai_equipment import DesignGroup
from .owned_source import logical_source
from .spans import Span, find_priority, find_design
from .technology_graph import TechnologyGraph

# Resource -> the latched trigger family in WA_AI_EQUIPMENT_triggers.txt.
# A resource absent from this map has no runtime vocabulary, and a transition
# that needs one is reported blocked rather than gated on the wrong reading.
GATE_TRIGGERS: Dict[str, str] = {
    "steel": "WA_AI_EQUIPMENT_can_absorb_steel_shock_{size}",
    "aluminium": "WA_AI_EQUIPMENT_can_absorb_aluminium_shock_{size}",
    "chromium": "WA_AI_EQUIPMENT_can_absorb_chromium_shock_{size}",
    "tungsten": "WA_AI_EQUIPMENT_can_absorb_tungsten_shock_{size}",
}

# Per-unit delta at or above which the `_large` gate is used instead of
# `_small`. HOI4 charges equipment resources per assigned military factory per
# day, so a +2/unit change on a 20-40 factory line is a +40..+80/day step -
# which is the `_large` threshold's stated design point. Fix 49 made exactly
# this call for a +2 aluminium step.
LARGE_GATE_DELTA = 2.0


@dataclass
class Patch:
    country: str
    file: str
    group: str
    design: str
    kind: str                 # retain_gate | new_gate | module_list
    anchor_line: int
    # Byte range of `original` in the source file. Application must go
    # bottom-up (descending `start`) so earlier edits do not shift later ones.
    start: int
    end: int
    original: str
    replacement: str
    rationale: List[str] = field(default_factory=list)

    @property
    def n_added(self) -> int:
        return len(self.replacement.splitlines()) - len(self.original.splitlines())


@dataclass
class Blocked:
    country: str
    group: str
    transition: str
    reason: str


@dataclass
class GateEdit:
    """All gate work owed to ONE design's `priority` block.

    A design is normally both sides of the chain: the expensive NEW design of
    the transition into it, and the retained OLD design of the transition out
    of it. Those two edits land in the same `priority` block - one inside a
    nested `modifier`, one appended to the block - so they must be merged into
    a single patch. Emitting them separately produced overlapping byte ranges
    that corrupted the file when applied.
    """
    country: str
    group: str
    design: str
    # has_tech value -> gate lines to add inside that supersession modifier
    hook_inserts: Dict[str, List[str]] = field(default_factory=dict)
    # Original supersession tech -> accepted successor tech.
    hook_replacements: Dict[str, str] = field(default_factory=dict)
    # Original supersession hooks which must never fire (final retained model).
    hook_disables: Set[str] = field(default_factory=set)
    # negation blocks to append to the priority block
    append_gates: List[List[str]] = field(default_factory=list)
    # Rejected generations remain defined but can never win this role.
    disable_design: bool = False
    # Branched-role frontier rank. The maximum historical factor is preserved;
    # only the ordering inside the role changes.
    priority_factor: Optional[float] = None
    original_priority_factor: Optional[float] = None
    # Rebuild this priority block from its logical pre-generator source. Used
    # when a model/config change legitimately changes an already-owned rank.
    rebuild_priority: bool = False
    rationale: List[str] = field(default_factory=list)


def _gate_for(resource: str, delta: float) -> Optional[str]:
    tmpl = GATE_TRIGGERS.get(resource)
    if tmpl is None:
        return None
    return tmpl.format(size="large" if delta >= LARGE_GATE_DELTA else "small")


def _gate_condition(gates: List[str], indent: str) -> List[str]:
    """The positive form: every gate must be open."""
    return [f"{indent}{g} = yes" for g in gates]


def _gate_negation(gates: List[str], indent: str) -> List[str]:
    """The negative form for the expensive design's own priority."""
    if len(gates) == 1:
        return [f"{indent}NOT = {{ {gates[0]} = yes }}"]
    out = [f"{indent}NOT = {{", f"{indent}\tAND = {{"]
    out += [f"{indent}\t\t{g} = yes" for g in gates]
    out += [f"{indent}\t}}", f"{indent}}}"]
    return out


class Emitter:
    def __init__(self, cfg: Config, diag: Diagnostics,
                 file_suffix: str = "planes", domain: str = "air") -> None:
        self.cfg = cfg
        self.diag = diag
        self.file_suffix = file_suffix
        self.domain = domain
        self.patches: List[Patch] = []
        self.blocked: List[Blocked] = []
        self._edits: Dict[Tuple[str, str, str], GateEdit] = {}

    # ------------------------------------------------------------------ API
    def run(self, transitions: List[Transition],
            groups_by_country: Dict[str, List[DesignGroup]],
            ai_dir: Path, frontier_rows: Optional[List[object]] = None) -> None:
        raws: Dict[str, str] = {}
        designs: Dict[Tuple[str, str, str], object] = {}
        group_index: Dict[Tuple[str, str], DesignGroup] = {}
        tech_graph = TechnologyGraph(ai_dir.parent.parent, self.diag)
        for country, groups in groups_by_country.items():
            path = ai_dir / f"{country}_{self.file_suffix}.txt"
            if path.exists():
                raws[country] = path.read_text(encoding="utf-8-sig", errors="replace")
            for g in groups:
                stop_techs = {
                    tech for candidate_group in groups
                    for candidate in candidate_group.designs for tech in candidate.enable_techs
                }
                g.technology_edges = list(tech_graph.design_graph(g, stop_techs).edges)
                group_index[(country, g.name)] = g
                for d in g.designs:
                    designs[(country, g.name, d.name)] = d

        by_group: Dict[Tuple[str, str], List[Transition]] = {}
        for transition in transitions:
            by_group.setdefault((transition.country, transition.group), []).append(transition)

        frontier_by_group: Dict[Tuple[str, str], List[object]] = {}
        for row in frontier_rows or []:
            frontier_by_group.setdefault((row.country, row.group), []).append(row)

        for key, rows in sorted(by_group.items()):
            raw = raws.get(key[0])
            group = group_index.get(key)
            if raw is None or group is None:
                continue
            graph_outgoing: Dict[str, Set[str]] = {}
            graph_incoming: Dict[str, Set[str]] = {}
            for old, new in group.technology_edges:
                graph_outgoing.setdefault(old, set()).add(new)
                graph_incoming.setdefault(new, set()).add(old)
            branched = (any(len(items) > 1 for items in graph_outgoing.values()) or
                        any(len(items) > 1 for items in graph_incoming.values()))
            if branched and key in frontier_by_group:
                self._plan_frontier(frontier_by_group[key], group, raw, designs)
                continue
            if branched and any(row.verdict not in ("SWITCH", PARALLEL_VARIANT)
                                for row in rows):
                self.blocked.append(Blocked(
                    group.country, group.name, f"{group.country}/{group.name}",
                    "branched designs share one production role but no complete frontier "
                    "analysis was supplied"))
                continue
            if any(row.verdict == KEEP_OLD for row in rows):
                self._plan_group_chain(rows, group, raw, designs)
            else:
                for row in rows:
                    if row.verdict == SWITCH_CONDITIONAL:
                        self._plan_gate(row, raw, designs)
                    elif row.verdict == SWITCH_REDESIGNED:
                        self._emit_modules(row, raw, designs)

        self._materialise_gates(raws)

    # ---------------------------------------------------------- gate merging
    def _edit(self, country: str, group: str, design: str) -> GateEdit:
        key = (country, group, design)
        if key not in self._edits:
            self._edits[key] = GateEdit(country=country, group=group, design=design)
        return self._edits[key]

    def _materialise_gates(self, raws: Dict[str, str]) -> None:
        """One patch per priority block, however many transitions touched it."""
        for (country, group, design), ed in sorted(self._edits.items()):
            raw = raws.get(country)
            if raw is None:
                continue
            pri = find_priority(raw, group, design)
            if pri is None:
                self.blocked.append(Blocked(country, group, design,
                                            "priority block disappeared between planning and emit"))
                continue
            text = pri.text(raw)
            working_text = logical_source(text) if ed.rebuild_priority else text
            lines = working_text.splitlines()

            # 0. replace the top-level factor with the frontier rank.  The
            # original is recorded so logical_source() can reconstruct the
            # pre-generator analysis input after application.
            if ed.priority_factor is not None:
                detail = _pdx_num(ed.priority_factor)
                marker = _marker_id(country, group, design, "priority_factor", detail)
                if ed.rebuild_priority or f"id={marker}" not in raw:
                    out = []
                    replaced = False
                    for ln in lines:
                        if not replaced and ln.strip().startswith("factor ="):
                            ind = _leading_ws(ln)
                            original = _pdx_num(ed.original_priority_factor or 0)
                            out.append(f"{ind}# WA_EQUIPGEN_BEGIN id={marker} "
                                       f"kind=priority_factor schema=1 mode=replace "
                                       f"original={original}")
                            out.append(f"{ind}factor = {detail}")
                            out.append(f"{ind}# WA_EQUIPGEN_END id={marker}")
                            replaced = True
                        else:
                            out.append(ln)
                    if not replaced:
                        self.blocked.append(Blocked(
                            country, group, design, "priority factor disappeared during emit"))
                        continue
                    lines = out

            # 1. insertions into the nested supersession modifiers
            if ed.hook_inserts or ed.hook_replacements or ed.hook_disables:
                out: List[str] = []
                for ln in lines:
                    target = next((tech for tech in
                                   set(ed.hook_inserts) | set(ed.hook_replacements) | ed.hook_disables
                                   if f"has_tech = {tech}" in ln), None)
                    if target is None:
                        out.append(ln)
                        continue
                    ind = _leading_ws(ln)
                    replacement = ed.hook_replacements.get(target)
                    if replacement:
                        marker = _marker_id(country, group, design, "supersede", target)
                        suffix = (" #" + ln.split("#", 1)[1]) if "#" in ln else ""
                        out.append(f"{ind}# WA_EQUIPGEN_BEGIN id={marker} kind=supersede "
                                   f"schema=1 mode=replace original={target}")
                        out.append(f"{ind}has_tech = {replacement}{suffix}")
                        out.append(f"{ind}# WA_EQUIPGEN_END id={marker}")
                    else:
                        out.append(ln)
                    if target in ed.hook_disables:
                        marker = _marker_id(country, group, design, "chain_guard", target)
                        out.append(f"{ind}# WA_EQUIPGEN_BEGIN id={marker} kind=chain_guard schema=1")
                        out.append(f"{ind}always = no")
                        out.append(f"{ind}# WA_EQUIPGEN_END id={marker}")
                    if target in ed.hook_inserts:
                        marker = _marker_id(country, group, design, "retain_gate", target)
                        out.append(f"{ind}# WA_EQUIPGEN_BEGIN id={marker} kind=retain_gate schema=1")
                        out.extend(f"{ind}{g}" for g in ed.hook_inserts[target])
                        out.append(f"{ind}# WA_EQUIPGEN_END id={marker}")
                lines = out

            # 2. appended negation blocks
            if ed.append_gates or ed.disable_design:
                inner = _body_indent(lines, _leading_ws(lines[-1]) + "\t")
                block: List[str] = []
                for gates in ed.append_gates:
                    marker = _marker_id(country, group, design, "hold_gate", ",".join(gates))
                    block.append(f"{inner}# WA_EQUIPGEN_BEGIN id={marker} kind=hold_gate schema=1")
                    block.append(f"{inner}modifier = {{")
                    block += _gate_negation(gates, inner + "\t")
                    block += [f"{inner}\tfactor = 0", f"{inner}}}"]
                    block.append(f"{inner}# WA_EQUIPGEN_END id={marker}")
                if ed.disable_design:
                    marker = _marker_id(country, group, design, "reject_design", "always")
                    block.append(f"{inner}# WA_EQUIPGEN_BEGIN id={marker} kind=reject_design schema=1")
                    block.append(f"{inner}modifier = {{")
                    block.append(f"{inner}\talways = yes")
                    block.append(f"{inner}\tfactor = 0")
                    block.append(f"{inner}}}")
                    block.append(f"{inner}# WA_EQUIPGEN_END id={marker}")
                lines = lines[:-1] + block + [lines[-1]]

            kind = ("priority_chain" if ed.hook_replacements or ed.hook_disables
                    or ed.disable_design or ed.priority_factor is not None
                    else "resource_gate")
            self.patches.append(Patch(
                country=country, file=f"{country}_{self.file_suffix}.txt", group=group,
                design=design, kind=kind, anchor_line=pri.line,
                start=pri.start, end=pri.end,
                original=text, replacement="\n".join(lines),
                rationale=ed.rationale))

    def _plan_frontier(self, rows: List[object], group: DesignGroup,
                       raw: str, designs) -> None:
        """Compile one complete competitive ladder for a branched role."""
        label = f"{group.country}/{group.name}"
        by_name = {d.name: d for d in group.designs if d.airframe}
        row_by_name = {row.design: row for row in rows}
        problems = []
        if set(row_by_name) != set(by_name):
            missing = sorted(set(by_name) - set(row_by_name))
            extra = sorted(set(row_by_name) - set(by_name))
            problems.append(f"frontier coverage mismatch (missing={missing}, extra={extra})")
        if any(d.already_gated for d in by_name.values()):
            problems.append("group contains hand-owned WA_AI_EQUIPMENT gates")
        for name, row in row_by_name.items():
            design = by_name.get(name)
            if design is None:
                continue
            if design.priority_factor is None or find_priority(raw, group.name, name) is None:
                problems.append(f"{name} has no writable priority factor")
            missing_gates = sorted(set(row.resource_gates) - set(GATE_TRIGGERS))
            if missing_gates:
                problems.append(f"{name} needs unsupported resource gates: {missing_gates}")
        if problems:
            self.blocked.append(Blocked(group.country, group.name, label,
                                        "; ".join(problems)))
            return

        expected = []
        for name, row in row_by_name.items():
            detail = _pdx_num(row.priority_factor)
            expected.append(_marker_id(group.country, group.name, name,
                                       "priority_factor", detail))
            for tech in by_name[name].supersede_techs:
                expected.append(_marker_id(group.country, group.name, name,
                                           "chain_guard", tech))
            gates = sorted({_gate_for(res, delta)
                            for res, delta in row.resource_gates.items()})
            gates = [gate for gate in gates if gate]
            if gates:
                expected.append(_marker_id(group.country, group.name, name,
                                           "hold_gate", ",".join(gates)))
            if row.action == "REJECT":
                expected.append(_marker_id(group.country, group.name, name,
                                           "reject_design", "always"))
        present = [f"id={marker}" in raw for marker in expected]
        has_owned_frontier = any(
            f"id={_marker_id(group.country, group.name, name, 'priority_factor', '')}" in raw
            for name in row_by_name)
        rebuilding = has_owned_frontier and not all(present)
        if not all(present):
            for name, row in row_by_name.items():
                design = by_name[name]
                ed = self._edit(group.country, group.name, name)
                ed.priority_factor = row.priority_factor
                ed.original_priority_factor = design.priority_factor
                ed.rebuild_priority = rebuilding
                ed.hook_disables.update(design.supersede_techs)
                ed.disable_design = row.action == "REJECT"
                gates = sorted({_gate_for(res, delta)
                                for res, delta in row.resource_gates.items()})
                gates = [gate for gate in gates if gate]
                if gates and gates not in ed.append_gates:
                    ed.append_gates.append(gates)
                fallback = (f"; fallback `{row.fallback_design}`"
                            if row.fallback_design else "")
                ed.rationale.append(
                    f"FRONTIER rank {row.rank} ({row.action}), quality "
                    f"{row.quality_score:+.3f}, efficiency-adjusted {row.score:+.3f} "
                    f"({row.efficiency_retention:.0%} retained)"
                    f"{fallback}. Research controls availability; quality and economy "
                    "control selection.")

        # Redesign patches live in target_variant.modules and are independent
        # from the priority block's all-or-none frontier ownership.
        for row in rows:
            changes = []
            for item in row.redesign_changes:
                if ":" in item and "->" in item:
                    slot, values = item.split(":", 1)
                    old, new = values.split("->", 1)
                    changes.append((slot.strip(), old.strip(), new.strip()))
            if not changes:
                continue
            synthetic = SimpleNamespace(
                country=row.country, group=row.group, role=row.role,
                from_design=row.fallback_design or row.design,
                to_design=row.design, redesign=SimpleNamespace(
                    changes=changes, gain_vs_old=row.score, gain_vs_new=0.0,
                    stats=SimpleNamespace(range_km=0.0)))
            self._emit_modules(synthetic, raw, designs)

    # --------------------------------------------------------- chain compile
    def _plan_group_chain(self, rows: List[Transition], group: DesignGroup,
                          raw: str, designs) -> None:
        """Compile a complete retained/rejected ladder for one linear group."""
        label = f"{group.country}/{group.name}"
        outgoing: Dict[str, Set[str]] = {}
        incoming: Dict[str, Set[str]] = {}
        for old, new in group.technology_edges:
            outgoing.setdefault(old, set()).add(new)
            incoming.setdefault(new, set()).add(old)
        if any(len(items) > 1 for items in outgoing.values()) or any(
                len(items) > 1 for items in incoming.values()):
            self.blocked.append(Blocked(
                group.country, group.name, label,
                "KEEP_OLD occurs in a branched technology graph; no linear chain rewrite emitted"))
            return
        if any(row.verdict in (PARALLEL_VARIANT, UNRESOLVED) for row in rows):
            self.blocked.append(Blocked(
                group.country, group.name, label,
                "KEEP_OLD chain also contains a parallel or unresolved transition"))
            return

        names = []
        by_name = {}
        for design in group.designs:
            if not design.airframe or design.name in by_name:
                continue
            names.append(design.name)
            by_name[design.name] = design
        involved = {row.from_design for row in rows} | {row.to_design for row in rows}
        if any(by_name[name].already_gated for name in involved if name in by_name):
            self.blocked.append(Blocked(
                group.country, group.name, label,
                "chain contains a hand-gated design; left entirely under manual ownership"))
            return

        retained = [rows[0].from_design]
        rejected = []
        accepted_rows: Dict[Tuple[str, str], Transition] = {}
        for row in rows:
            if row.verdict in ADOPTION_VERDICTS:
                if row.to_design not in retained:
                    retained.append(row.to_design)
                accepted_rows[(row.from_design, row.to_design)] = row
            elif row.verdict == KEEP_OLD:
                rejected.append(row.to_design)

        positions = {name: index for index, name in enumerate(names)}
        retained = sorted(set(retained), key=lambda name: positions.get(name, 10**9))
        rejected = sorted(set(rejected), key=lambda name: positions.get(name, 10**9))

        graph_predecessor = {new: old for old, new in group.technology_edges}

        def activation_tech(design_name: str) -> Optional[str]:
            design = by_name.get(design_name)
            if design and len(design.enable_techs) == 1:
                return design.enable_techs[0]
            # Legacy plane groups omit enable blocks.  In their linear priority
            # ladder, the immediately preceding design's supersession hook is
            # the tech which activates this candidate.
            previous = by_name.get(graph_predecessor.get(design_name, ""))
            if previous and len(previous.supersede_techs) == 1:
                return previous.supersede_techs[0]
            return None

        # Validate the entire chain before planning any partial edit.
        problems = []
        for predecessor, successor in zip(retained, retained[1:]):
            old, new = by_name.get(predecessor), by_name.get(successor)
            if old is None or new is None:
                problems.append(f"missing design object for {predecessor} -> {successor}")
                continue
            if len(old.supersede_techs) != 1:
                problems.append(f"{predecessor} has {len(old.supersede_techs)} supersession hooks")
            if activation_tech(successor) is None:
                problems.append(f"{successor} has no unique activation technology")
            if (predecessor, successor) not in accepted_rows:
                problems.append(f"no chain-aware verdict for {predecessor} -> {successor}")
        final = by_name.get(retained[-1]) if retained else None
        rejected_after_final = bool(final and any(
            positions.get(name, -1) > positions.get(final.name, -1) for name in rejected))
        if rejected_after_final and len(final.supersede_techs) != 1:
            problems.append(f"final retained {final.name} has no unique hook to neutralise")
        for name in rejected:
            if find_priority(raw, group.name, name) is None:
                problems.append(f"rejected design {name} has no priority block")
        if problems:
            self.blocked.append(Blocked(
                group.country, group.name, label, "; ".join(problems)))
            return

        # Reject every generation which failed against the last retained model.
        for name in rejected:
            marker = _marker_id(group.country, group.name, name, "reject_design", "always")
            if f"id={marker}" in raw:
                continue
            edit = self._edit(group.country, group.name, name)
            edit.disable_design = True
            edit.rationale.append(
                f"CHAIN KEEP_OLD: `{name}` is inferior to the last retained generation.")

        # Each retained model is released only by the next retained successor.
        for predecessor, successor in zip(retained, retained[1:]):
            old, new = by_name[predecessor], by_name[successor]
            original_tech = old.supersede_techs[0]
            successor_tech = activation_tech(successor)
            if successor_tech is None:  # fully validated above
                continue
            if original_tech != successor_tech:
                marker = _marker_id(
                    group.country, group.name, predecessor, "supersede", original_tech)
                if f"id={marker}" not in raw:
                    edit = self._edit(group.country, group.name, predecessor)
                    edit.hook_replacements[original_tech] = successor_tech
                    edit.rationale.append(
                        f"CHAIN REROUTE: `{predecessor}` now survives rejected generations "
                        f"until accepted `{successor}` unlocks via `{successor_tech}`.")
            row = accepted_rows[(predecessor, successor)]
            if row.verdict == SWITCH_CONDITIONAL:
                self._plan_gate(row, raw, designs)
            if row.verdict == SWITCH_REDESIGNED:
                self._emit_modules(row, raw, designs)

        # If every later candidate is rejected, the retained model must never
        # be killed by the first rejected technology.
        if rejected_after_final:
            original_tech = final.supersede_techs[0]
            marker = _marker_id(
                group.country, group.name, final.name, "chain_guard", original_tech)
            if f"id={marker}" not in raw:
                edit = self._edit(group.country, group.name, final.name)
                edit.hook_disables.add(original_tech)
                edit.rationale.append(
                    f"CHAIN TERMINAL KEEP: `{final.name}` remains active because all later "
                    "generations were rejected.")

    # --------------------------------------------------------- resource gate
    def _plan_gate(self, t: Transition, raw: str, designs) -> None:
        label = f"{t.from_design} -> {t.to_design}"
        old = designs.get((t.country, t.group, t.from_design))
        new = designs.get((t.country, t.group, t.to_design))
        if old is None or new is None:
            return

        if getattr(old, "already_gated", False) or getattr(new, "already_gated", False):
            self.blocked.append(Blocked(t.country, t.group, label,
                                        "already hand-gated (Fix 47 / Fix 49 pilot) - left alone"))
            return

        gates, missing = [], []
        for res, delta in sorted(t.res_significant.items()):
            g = _gate_for(res, delta)
            (gates.append(g) if g else missing.append(res))
        if missing:
            self.blocked.append(Blocked(
                t.country, t.group, label,
                f"no latched trigger exists for: {', '.join(missing)} "
                f"- add it to WA_AI_EQUIPMENT_triggers.txt before gating this"))
            return
        gates = sorted(set(gates))
        if find_priority(raw, t.group, t.to_design) is None:
            self.blocked.append(Blocked(t.country, t.group, label,
                                        f"`{t.to_design}` has no `priority` block to gate"))
            return

        # -- the OLD design must survive while the gate is shut --------------
        pri_old = find_priority(raw, t.group, t.from_design)
        hook = None
        expected_tech = (new.enable_techs[0]
                         if len(getattr(new, "enable_techs", [])) == 1 else None)
        hook_techs = list(getattr(old, "supersede_techs", []))
        if expected_tech:
            hook_techs = [tech for tech in hook_techs if tech == expected_tech]
        if pri_old is not None:
            for mod in pri_old.children:
                if mod.key != "modifier":
                    continue
                text = mod.text(raw)
                if any(f"has_tech = {tech}" in text for tech in hook_techs):
                    hook = mod
                    break
        hold_only = bool(expected_tech and pri_old is not None and hook is None)
        if pri_old is None or (hook is None and not hold_only):
            self.blocked.append(Blocked(
                t.country, t.group, label,
                "the older design has no `modifier = { has_tech = ... factor = 0 }` "
                "supersession hook to attach the gate to"))
            return

        hook_tech = next((tech for tech in hook_techs
                          if hook and f"has_tech = {tech}" in hook.text(raw)), None)
        if hook is not None and hook_tech is None:
            self.blocked.append(Blocked(t.country, t.group, label,
                                        "could not identify the supersession tech on the hook"))
            return

        retain_marker = (_marker_id(
            t.country, t.group, t.from_design, "retain_gate", hook_tech)
            if hook_tech else None)
        hold_marker = _marker_id(
            t.country, t.group, t.to_design, "hold_gate", ",".join(gates))
        owned = ([f"id={retain_marker}" in raw] if retain_marker else []) + [
            f"id={hold_marker}" in raw]
        if all(owned):
            return
        if any(owned):
            self.blocked.append(Blocked(
                t.country, t.group, label,
                "partial generated resource-gate pair found; refusing to repair one side silently"))
            return

        if hook_tech:
            ed_old = self._edit(t.country, t.group, t.from_design)
            ed_old.hook_inserts.setdefault(hook_tech, [])
            for g in gates:
                if f"{g} = yes" not in ed_old.hook_inserts[hook_tech]:
                    ed_old.hook_inserts[hook_tech].append(f"{g} = yes")
            ed_old.rationale.append(
                f"RETAIN for `{label}`: the newer design costs "
                + ", ".join(f"+{v:.0f} {k}/unit" for k, v in sorted(t.res_significant.items()))
                + f" (IC {t.ic_old:.1f} -> {t.ic_new:.1f}). Supersession on `{hook_tech}` "
                  f"now waits for the economy; `{t.from_design}` keeps its factor "
                  f"{getattr(old, 'priority_factor', '?')} while the gate is shut, so the role "
                  f"stays served.")

        # -- the NEW design is unavailable while the gate is shut ------------
        ed_new = self._edit(t.country, t.group, t.to_design)
        if gates not in ed_new.append_gates:
            ed_new.append_gates.append(gates)
        ed_new.rationale.append(
            f"HOLD for `{label}`: `{t.to_design}` stays unavailable until "
            + " and ".join(f"`{g}`" for g in gates) + " is satisfied.")
        if hold_only:
            ed_new.rationale.append(
                f"BRANCH-SAFE: `{t.from_design}` has no supersession hook for "
                f"`{expected_tech}`, so it already remains selectable; only the new branch "
                "needs a closed-gate hold.")

    # ----------------------------------------------------------- module list
    def _emit_modules(self, t: Transition, raw: str, designs) -> None:
        rd = t.redesign
        if rd is None:
            return
        label = f"{t.from_design} -> {t.to_design}"
        markers = [_marker_id(t.country, t.group, t.to_design, "module", slot)
                   for slot, _old, _new in rd.changes]
        present = [f"id={marker}" in raw for marker in markers]
        if present and all(present):
            return
        if any(present):
            self.blocked.append(Blocked(
                t.country, t.group, label,
                "partial generated module redesign found; refusing to overwrite it"))
            return
        dspan = find_design(raw, t.group, t.to_design)
        if dspan is None:
            return
        tv = dspan.child("target_variant")
        mods = tv.child("modules") if tv is not None else None
        if mods is None:
            self.blocked.append(Blocked(
                t.country, t.group, label,
                f"`{t.to_design}` has no `target_variant.modules` block to rewrite"))
            return

        mtext = mods.text(raw)
        lines = mtext.splitlines()
        # Indentation for lines we ADD; replaced lines keep their own.
        inner = _body_indent(lines, _line_indent(raw, mods) + "\t")
        out: List[str] = []
        pending = {slot: newmod for slot, _old, newmod in rd.changes}
        for ln in lines:
            stripped = ln.strip()
            hit = None
            for slot in pending:
                if stripped.startswith(slot) and "=" in stripped:
                    lead = stripped[len(slot):].lstrip()
                    if lead.startswith("="):
                        hit = slot
                        break
            if hit is not None:
                original = next(old for slot, old, _new in rd.changes if slot == hit)
                marker = _marker_id(t.country, t.group, t.to_design, "module", hit)
                indent = _leading_ws(ln)
                out.append(f"{indent}# WA_EQUIPGEN_BEGIN id={marker} kind=module schema=1 "
                           f"mode=replace slot={hit} original={original or 'empty'}")
                out.append(f"{indent}{hit} = {pending.pop(hit)}")
                out.append(f"{indent}# WA_EQUIPGEN_END id={marker}")
            else:
                out.append(ln)
        if pending:  # slots the design never mentioned
            closing = out.pop()
            for slot, mod in sorted(pending.items()):
                marker = _marker_id(t.country, t.group, t.to_design, "module", slot)
                out.append(f"{inner}# WA_EQUIPGEN_BEGIN id={marker} kind=module schema=1 "
                           f"mode=insert slot={slot} original=__absent__")
                out.append(f"{inner}{slot} = {mod}")
                out.append(f"{inner}# WA_EQUIPGEN_END id={marker}")
            out.append(closing)
        newtext = "\n".join(out)

        self.patches.append(Patch(
            country=t.country, file=f"{t.country}_{self.file_suffix}.txt", group=t.group,
            design=t.to_design, kind="module_list", anchor_line=mods.line,
            start=mods.start, end=mods.end, original=mtext, replacement=newtext,
            rationale=(
                [
                    f"{label}: default design reaches {t.range_new:.0f} km against a "
                    f"{t.range_target:.0f} km target; this loadout reaches "
                    f"{rd.stats.range_km:.0f} km.",
                    f"Combat score vs the old generation {rd.gain_vs_old:+.3f}, "
                    f"vs the new default {rd.gain_vs_new:+.3f}.",
                    "MODULE AVAILABILITY IS INFERRED, NOT READ FROM TECH - see README "
                    "approximation 4. Check the modules are researched by this airframe's year.",
                ] if self.domain == "air" else [
                    f"{label}: modular redesign restores the role's hard stat threshold(s).",
                    f"Adjusted score vs the old generation {rd.gain_vs_old:+.3f}.",
                    "Module availability is inferred from the country's own contemporary designs.",
                ])))


def _line_indent(raw: str, span: Span) -> str:
    line_start = raw.rfind("\n", 0, span.start) + 1
    lead = raw[line_start:span.start]
    return lead if lead.strip() == "" else ""


def _marker_id(country: str, group: str, design: str, kind: str, detail: str) -> str:
    """PDX-comment-safe stable ownership id."""
    clean = lambda value: "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in value)
    return clean(f"{country}:{group}:{design}:{kind}:{detail}")


def _pdx_num(value: float) -> str:
    """Format a number the way PDXScript can actually read it.

    `f"{x:.12g}"` switches to scientific notation below ~1e-5 ("9e-06"), and
    the HOI4 parser does not understand it - it reads the mantissa and stops,
    so `factor = 9e-06` is loaded as `factor = 9`.  That inverted the bottom of
    the SOV_heavy_tanks ladder (the T 35 emergency floor outranked IS 8/IS 4/
    IS 3) until campaign `bec4d829` surfaced it.  Always emit plain decimal.
    """
    text = f"{float(value):.12f}".rstrip("0").rstrip(".")
    return text or "0"


def _leading_ws(line: str) -> str:
    return line[:len(line) - len(line.lstrip())]


def _body_indent(lines: List[str], fallback: str) -> str:
    """Indentation used by the entries inside a block, for lines we ADD.

    This repo mixes tabs and spaces across files and sometimes within one block
    (AGENTS.md rule 12: preserve what is there, do not reformat). Taking the
    shallowest leading whitespace among the block's own body lines identifies
    direct children even when nested modifier lines outnumber them.
    """
    body = [ln for ln in lines[1:-1] if ln.strip()]
    if not body:
        return fallback
    return min((_leading_ws(ln) for ln in body), key=len)
