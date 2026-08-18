"""Emit `production_upgrade_desire_offset` strategies for branched roles.

WHY THIS MODULE EXISTS
======================
The original generator wrote `priority = { factor = N }` edits into
``common/ai_equipment/*.txt``.  Campaign ``bec4d829`` (build ``88e516780``)
proved that is the wrong layer: R30, R31, R32, R33 and R35 all failed, and in
the cleanest case - JAP submarines, a 28x priority inversion in a group with no
supersession chain at all - the AI's hull-switch dates reproduced the pre-fix
campaigns to within a month.

Vanilla's own ``common/ai_equipment/_documentation.info`` (section ``Syntax``,
the design-group ``priority`` key) defines `priority` as
the weight "for creating a design in this group or for creating or upgrading
equipment to use one of these designs".  It is the DESIGN layer.  Which
equipment type a running production line makes, and whether it converts to a
newer type, is arbitrated by the `ai_strategy` type
**production_upgrade_desire_offset** - stock vanilla (``common/ai_strategy/
SOV.txt:357``, ``ENG.txt:478``), already used in this mod by
``SOV_dont_build_shit_guns``, and used 46 times at ``-100`` by Expert AI 5.0 as
its keep-the-old-type knob.

WHAT IT EMITS
=============
One file per country, ``WA_AI_PRODUCTION_COUNTRY_<TAG>_TANKS.txt``.  The name
is deliberately distinct from the hand-written ``WA_AI_PRODUCTION_COUNTRY_
<TAG>.txt`` so generation can never clobber the hand-maintained naval blocks
(the evaluator has no naval domain at all).

THE PROJECTION, AND ITS ONE LOSSY STEP
======================================
A frontier is an ordered ranking of N designs.  `production_upgrade_desire_offset`
is a coarse knob - vanilla only ever uses +/-100 - so an N-level ranking cannot be
written directly.  What IS expressible, and what the AI actually needs, is:

    for each reachable resource-gate state, exactly one design is wanted.

So we walk the frontier best-first and emit one block per design that can ever
be the winner.  A block is enabled when every cumulative resource gate up to
that design is open AND at least one gate of the next-better design is shut.
Inside it:

  * ``+100`` on the wanted design - convert lines to it without waiting for a
    stockpile surplus (vanilla's own gloss on the positive direction);
  * ``-100`` on every design with a HIGHER file index, i.e. every newer chassis
    the engine would otherwise drift onto.

Older, lower-ranked designs are deliberately NOT suppressed: the offset only
biases *upgrading a line onto* an equipment, so leaving them alone costs nothing
and keeps the emergency floor reachable if everything else becomes unbuildable.

`abort_when_not_enabled = yes` on every block means exactly one is live at a
time per group.
"""

from __future__ import annotations

import io
import os
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from ..emit import _gate_for

WANT = 100
AVOID = -100

HEADER = """\
############################################################################################################
# WA AI Production - COUNTRY_{tag}, branched equipment roles
############################################################################################################
# GENERATED FILE - do not edit by hand.
# Source: tools/equipment_evaluator, `python -m equipment_evaluator --emit-production-strategy`.
# Ranking source of truth: tools/equipment_evaluator/output/parallel_branch_decisions.md
#
# Every ai_strategy here is `production_upgrade_desire_offset`, whose `id` is an equipment TYPE token
# (`tank_usa_medium_chassis_6`).  That is NOT the ai_equipment design name (`medium_tank_7`) and NOT the
# technology token (`usa_medium_tank_chassis_5`); the three numbering schemes do not line up.
#
# This is the PRODUCTION-LINE layer.  `ai_equipment` priority is the design layer and does not decide
# what a running line produces - see the module docstring of
# tools/equipment_evaluator/generation/production_strategy.py for the campaign evidence.
#
# Hand-written, NON-generated country production strategy lives in WA_AI_PRODUCTION_COUNTRY_{tag}.txt.
# The evaluator has no naval domain, so submarine/ship policy is hand-written there and never here.
"""


def _step_gates(row: "object") -> List[str]:
    """Gates for the step INTO this design, from the rank immediately below.

    Deliberately NOT accumulated down the frontier.  The runtime triggers are
    idempotent symbols ("can we absorb a small tungsten shock"), so unioning
    every step below a design collapses distinct ranks onto identical gate
    sets: in USA_medium_tanks the tungsten gate first appears at rank 2
    (M3 Lee), which under a cumulative model made M4A2 and M4A3E8
    indistinguishable and silently dropped the M4A2 fallback - the exact
    behaviour campaign `bec4d829` failed on.  Comparing adjacent steps keeps
    "afford the next step up or stay here" intact, which is the decision the
    gate actually encodes.
    """
    gates: List[str] = []
    for resource, delta in sorted(row.resource_gates.items()):
        gate = _gate_for(resource, delta)
        if gate is None:
            raise ValueError(
                f"{row.country}/{row.group}/{row.design}: no runtime gate "
                f"for resource {resource!r}")
        if gate not in gates:
            gates.append(gate)
    return gates


def _enable_block(indent: str, required: Sequence[str],
                  blocked: Sequence[Sequence[str]]) -> List[str]:
    """`enable` for "my gates open, and every better rank is shut out".

    *blocked* is a list of gate SETS, one per better rank that could otherwise
    win.  Each set becomes its own negation, because a better rank is out of
    reach as soon as ANY one of its gates is shut.
    """
    out = [f"{indent}enable = {{"]
    if not required and not blocked:
        out.append(f"{indent}\talways = yes")
    for gate in required:
        out.append(f"{indent}\t{gate} = yes")
    for gate_set in blocked:
        if len(gate_set) == 1:
            out.append(f"{indent}\tNOT = {{ {gate_set[0]} = yes }}")
        else:
            out.append(f"{indent}\tNOT = {{")
            out.append(f"{indent}\t\tAND = {{")
            for gate in gate_set:
                out.append(f"{indent}\t\t\t{gate} = yes")
            out.append(f"{indent}\t\t}}")
            out.append(f"{indent}\t}}")
    out.append(f"{indent}}}")
    return out


def _strategy(indent: str, equipment: str, value: int, note: str) -> List[str]:
    return [
        f"{indent}# {note}",
        f"{indent}ai_strategy = {{",
        f"{indent}\ttype = production_upgrade_desire_offset",
        f"{indent}\tid = {equipment}",
        f"{indent}\tvalue = {value}",
        f"{indent}}}",
    ]


def build_group_blocks(rows: Sequence["object"]) -> Tuple[List[str], List[str]]:
    """Render every block for one frontier group.

    Returns ``(lines, skipped)`` where *skipped* explains each design that can
    never win, so the caller can report it instead of silently dropping it.
    """
    ordered = sorted(rows, key=lambda r: r.rank)            # weakest first
    if not ordered:
        return [], []
    missing = [r.design for r in ordered if not r.equipment_type]
    if missing:
        raise ValueError(
            f"{ordered[0].country}/{ordered[0].group}: no equipment token for "
            f"{', '.join(missing)} - target_variant `type =` did not parse")

    gates_by_rank = {row.rank: _step_gates(row) for row in ordered}
    by_rank = {r.rank: r for r in ordered}
    country = ordered[0].country
    group = ordered[0].group

    lines: List[str] = []
    skipped: List[str] = []

    for row in sorted(ordered, key=lambda r: -r.rank):       # best first
        required = gates_by_rank[row.rank]
        req_set = set(required)

        # A better rank wins over this one whenever ALL of its own gates are
        # open, so this design is only wanted while every better rank is shut
        # out.  Comparing against the adjacent rank alone is not enough: a
        # gate-free design several ranks up would still win, which would leave
        # two blocks handing out +100 at once.
        dominators = [by_rank[r] for r in sorted(by_rank) if r > row.rank]
        subsumed = next((d for d in dominators
                         if set(gates_by_rank[d.rank]) <= req_set), None)
        if subsumed is not None:
            skipped.append(
                f"{country}/{group}/{row.design} ({row.label}): rank "
                f"{row.rank} is never the winner - rank {subsumed.rank} "
                f"({subsumed.label}) needs no gate this rank does not already need")
            continue

        # Keep only the minimal gate sets: negating a subset already negates
        # every superset, so the wider ones are redundant clauses.
        better_sets = [tuple(gates_by_rank[d.rank]) for d in dominators]
        blocked: List[Sequence[str]] = []
        for gate_set in sorted(set(better_sets), key=len):
            if any(set(kept) <= set(gate_set) for kept in blocked):
                continue
            blocked.append(gate_set)

        newer = [r for r in ordered if r.file_index > row.file_index]

        lines.append("")
        lines.append(f"# {group} -> {row.label} ({row.action}, rank {row.rank}"
                     f" of {len(ordered)})")
        if row.failed_thresholds:
            lines.append(f"# Emergency floor: fails {', '.join(row.failed_thresholds)}")
        if required:
            lines.append(f"# Requires: {', '.join(required)}")
        for gate_set in blocked:
            lines.append(f"# Better rank shut out by: {' + '.join(gate_set)}")
        lines.append(f"WA_AI_PRODUCTION_COUNTRY_{country}_{group}_{row.design} = {{")
        lines.append("")
        lines.append("\tallowed = {")
        lines.append(f"\t\toriginal_tag = {country}")
        lines.append("\t}")
        lines.extend(_enable_block("\t", required, blocked))
        lines.append("")
        lines.append("\tabort_when_not_enabled = yes")
        lines.append("")
        lines.extend(_strategy("\t", row.equipment_type, WANT,
                               f"{row.label} - the wanted design in this gate state"))
        for other in newer:
            lines.append("")
            lines.extend(_strategy(
                "\t", other.equipment_type, AVOID,
                f"{other.label} - newer chassis, ranked {other.rank} below this one"))
        lines.append("}")

    return lines, skipped


def render_country(tag: str, rows_by_group: Dict[str, Sequence["object"]]
                   ) -> Tuple[str, List[str]]:
    body: List[str] = [HEADER.format(tag=tag)]
    skipped: List[str] = []
    for group in sorted(rows_by_group):
        lines, group_skipped = build_group_blocks(rows_by_group[group])
        body.extend(lines)
        skipped.extend(group_skipped)
    body.append("")
    return "\n".join(body), skipped


LINEAR_HEADER = """\
############################################################################################################
# WA AI Production - COUNTRY_{tag}, {domain} chains
############################################################################################################
# GENERATED FILE - do not edit by hand.
# Source: tools/equipment_evaluator, `--emit-production-strategy`.
#
# Linear equipment chains, as opposed to the branched roles in
# WA_AI_PRODUCTION_COUNTRY_{tag}_TANKS.txt.  A chain has one successor per step, so the only question is
# whether to take the step at all.  The engine's default is always to take it - that is exactly the
# "always builds the newest researched equipment" behaviour the evaluator exists to correct.
#
# Only two verdicts produce a strategy here:
#   KEEP_OLD            -> permanent -100 on the successor: the step is a net loss, never take it.
#   SWITCH_CONDITIONAL  -> -100 on the successor only while the economy cannot absorb the resource
#                          step. When the gate opens no block is enabled and the default switch runs.
# SWITCH and SWITCH_REDESIGNED emit nothing: the default behaviour is already right, and a redesign is
# a design-layer change that this layer cannot express.
"""


def _verdict_blocks(tag: str, domain: str, rows: Sequence[dict]) -> List[str]:
    """Render one block per suppressed successor. *rows* are plain dicts so the
    three unrelated transition dataclasses can share this path."""
    lines: List[str] = []
    for row in rows:
        gates = row["gates"]
        lines.append("")
        lines.append(f"# {row['group']}: keep {row['old_label']}, "
                     f"do not convert to {row['new_label']} ({row['verdict']})")
        if row["reason"]:
            lines.append(f"# {row['reason']}")
        if gates:
            lines.append(f"# Released when: {' + '.join(gates)}")
        lines.append(f"WA_AI_PRODUCTION_COUNTRY_{tag}_{domain}_{row['new']} = {{")
        lines.append("")
        lines.append("\tallowed = {")
        lines.append(f"\t\toriginal_tag = {tag}")
        lines.append("\t}")
        if not gates:
            lines.extend(["\tenable = {", "\t\talways = yes", "\t}"])
        elif len(gates) == 1:
            lines.extend([f"\tenable = {{",
                          f"\t\tNOT = {{ {gates[0]} = yes }}", "\t}"])
        else:
            lines.append("\tenable = {")
            lines.append("\t\tNOT = {")
            lines.append("\t\t\tAND = {")
            for gate in gates:
                lines.append(f"\t\t\t\t{gate} = yes")
            lines.append("\t\t\t}")
            lines.append("\t\t}")
            lines.append("\t}")
        lines.append("")
        lines.append("\tabort_when_not_enabled = yes")
        lines.append("")
        lines.extend(_strategy(
            "\t", row["new"], AVOID,
            f"{row['new_label']} - successor the evaluator rejected"))
        lines.append("}")
    return lines


def _chain_rank(name: str) -> Tuple:
    """Order two successors of the same node by generation.

    Equipment chains in this mod are numerically suffixed - ``usa_inf_9``,
    ``tank_usa_medium_chassis_4_2`` - so the trailing numeric components order
    them.  Names carrying no digit at all sort first and fall back to the raw
    string, which keeps the key total.
    """
    parts = re.findall(r"\d+", name)
    return (bool(parts), tuple(int(p) for p in parts), name)


def _released_from_sealed_nodes(
        rows: Sequence[dict],
        approved: Dict[Tuple[str, str], bool]) -> set:
    """Successors that must NOT be suppressed because their node is a sink.

    A KEEP_OLD pins a production line onto ``old``.  That is a legitimate,
    deliberate verdict - "keep the Sherman" is exactly this - for as long as
    ``old`` still has SOME successor the chain can eventually take.  When a node
    has SEVERAL successors and every one of them is KEEP_OLD, the node becomes a
    sink instead: no route out of it exists, everything downstream is dead code,
    and the country is frozen on that equipment for the rest of the game.

    Campaign ``5078fe10`` is the case this guard exists for.  ``usa_inf_3`` (a
    1939 rifle) has three producible successors - ``usa_inf_4``, ``usa_inf_5``
    and, through ``ghost_usa_inf_3``, ``usa_inf_9`` - and all three were emitted
    at ``-100 / always = yes``.  The USA held 94 factories on that 1939 rifle for
    the entire war, while ``usa_hv_inf_5`` next to it in the same file stayed
    fully current; ``usa_inf_6``/``_7``/``_8`` became unreachable dead blocks.

    A SINGLE-successor node is deliberately NOT treated as sealed: that is a
    plain linear chain, and stopping it is the whole point of KEEP_OLD.  Nor is a
    node with a SWITCH_CONDITIONAL successor, which already offers a gated escape.

    Of a sealed node's successors the NEWEST is released, so KEEP_OLD keeps its
    literal meaning - "do not take the next step" - while the chain stays
    reachable and the country ends up on the best equipment rather than the one
    the evaluator was least sure about.  Releasing the *nearest* successor
    instead would be the more conservative reading; change ``max`` to ``min``
    here if a campaign shows the jump is too large a resource shock.
    """
    successors: Dict[Tuple[str, str], List[dict]] = {}
    for row in rows:
        successors.setdefault((row["country"], row["old"]), []).append(row)

    released: set = set()
    for (country, _old), succs in successors.items():
        if len(succs) < 2:
            continue
        if any(r["verdict"] != "KEEP_OLD" for r in succs):
            continue
        if any(approved.get((country, r["new"])) for r in succs):
            continue
        newest = max(succs, key=lambda r: _chain_rank(r["new"]))
        released.add((country, newest["new"]))
    return released


def emit_linear(mod_root: str, domain: str, rows: Iterable[dict],
                apply: bool = False) -> Tuple[Dict[str, str], List[str]]:
    """Emit the KEEP_OLD / SWITCH_CONDITIONAL suppressions of a linear domain.

    *rows* are normalised dicts with keys: country, group, old, new, old_label,
    new_label, verdict, gates, reason.

    A successor reachable by a plain SWITCH from ANY predecessor is never
    suppressed: the chain offers a legitimate route onto it, and a blanket -100
    would strand the role.  This is the linear analogue of the branched
    emitter's "no gate state may empty a role" invariant.

    Nor is the newest successor of a SEALED node - one whose every successor was
    KEEP_OLD - suppressed; see :func:`_released_from_sealed_nodes`.
    """
    rows = list(rows)
    by_country: Dict[str, List[dict]] = {}
    approved: Dict[Tuple[str, str], bool] = {}
    collected: List[dict] = []
    for row in rows:
        key = (row["country"], row["new"])
        if row["verdict"] == "SWITCH" or row["verdict"] == "SWITCH_REDESIGNED":
            approved[key] = True
        elif row["verdict"] in ("KEEP_OLD", "SWITCH_CONDITIONAL"):
            collected.append(row)

    released = _released_from_sealed_nodes(rows, approved)

    skipped: List[str] = []
    seen: set = set()
    for row in collected:
        key = (row["country"], row["new"])
        # `GENERIC` is a shared equipment bucket, not a country - there is no
        # tag to put in `allowed`, and suppressing it would silently apply to
        # every minor that inherits the chain.  That is a much wider blast
        # radius than this generator is allowed to decide on its own.
        if not (len(row["country"]) == 3 and row["country"].isalpha()
                and row["country"].isupper()):
            skipped.append(
                f"{row['country']}/{row['group']}/{row['new']}: not a country "
                f"tag - shared equipment bucket, needs a human decision")
            continue
        if approved.get(key):
            skipped.append(
                f"{row['country']}/{row['group']}/{row['new']}: not suppressed - "
                f"another predecessor reaches it with a plain SWITCH")
            continue
        if key in released:
            skipped.append(
                f"{row['country']}/{row['group']}/{row['new']}: not suppressed - "
                f"every successor of {row['old']} was KEEP_OLD; releasing the "
                f"newest keeps the chain reachable")
            continue
        if key in seen:
            skipped.append(
                f"{row['country']}/{row['group']}/{row['new']}: duplicate "
                f"successor, first verdict kept")
            continue
        seen.add(key)
        by_country.setdefault(row["country"], []).append(row)

    files: Dict[str, str] = {}
    for tag in sorted(by_country):
        ordered = sorted(by_country[tag], key=lambda r: (r["group"], r["new"]))
        body = [LINEAR_HEADER.format(tag=tag, domain=domain.lower())]
        body.extend(_verdict_blocks(tag, domain.upper(), ordered))
        body.append("")
        rel = (f"common/ai_strategy/WA_AI_PRODUCTION_COUNTRY_"
               f"{tag}_{domain.upper()}.txt")
        files[rel] = "\n".join(body)

    if apply:
        _write(mod_root, files)
    return files, skipped


def _write(mod_root: str, files: Dict[str, str]) -> None:
    for rel, text in files.items():
        path = os.path.join(mod_root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp, path)


def emit(mod_root: str, decisions: Iterable["object"], apply: bool = False
         ) -> Tuple[Dict[str, str], List[str]]:
    """Render one file per country. Returns ``({relpath: text}, skipped)``.

    Writes to disk only when *apply* is true; dry-run is the default, matching
    the rest of the tool.
    """
    by_country: Dict[str, Dict[str, List["object"]]] = {}
    for row in decisions:
        by_country.setdefault(row.country, {}).setdefault(row.group, []).append(row)

    files: Dict[str, str] = {}
    skipped: List[str] = []
    for tag in sorted(by_country):
        text, tag_skipped = render_country(tag, by_country[tag])
        rel = f"common/ai_strategy/WA_AI_PRODUCTION_COUNTRY_{tag}_TANKS.txt"
        files[rel] = text
        skipped.extend(tag_skipped)

    if apply:
        _write(mod_root, files)

    return files, skipped
