"""Complete evaluators for non-air land equipment and modular tanks."""

from __future__ import annotations

import csv
import itertools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .config import Config
from .decision_policy import (KEEP_OLD, SWITCH, SWITCH_CONDITIONAL,
                              SWITCH_REDESIGNED, UNRESOLVED, ADOPTION_VERDICTS,
                              decide_adoption,
                              numeric_delta, significant_increases,
                              weighted_relative_gain)
from .diagnostics import Diagnostics
from .efficiency_audit import _tech_edges
from .infantry import InfantryDB, LandEquipment
from .parse_ai_equipment import Design, discover_countries, parse_country_file
from .parse_equipment import EquipmentDB, find_files
from .production_efficiency import classify_relation
from .stats import DesignStats, StatModel
from .technology_graph import TechnologyGraph


@dataclass
class GroundTransition:
    domain: str
    country: str
    role: str
    source: str
    group: str
    old: str
    new: str
    relation: str
    retention: float
    raw_gain: float
    adjusted_gain: float
    verdict: str
    old_stats: Dict[str, float]
    new_stats: Dict[str, float]
    resource_delta: Dict[str, float]
    significant_resources: Dict[str, float]
    failed_thresholds: List[str] = field(default_factory=list)
    redesign_changes: List[str] = field(default_factory=list)
    redesign_stats: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


@dataclass
class FrontierDecision:
    """One candidate in a branched modular-equipment production role."""
    country: str
    group: str
    role: str
    design: str
    label: str
    unlock_tech: str
    quality_score: float
    score: float
    efficiency_retention: float
    rank: int                    # 1 = weakest valid fallback
    action: str                  # PRIMARY | FALLBACK | EMERGENCY_FALLBACK
    priority_factor: float
    stats: Dict[str, float]
    resources: Dict[str, float]
    resource_gates: Dict[str, float] = field(default_factory=dict)
    failed_thresholds: List[str] = field(default_factory=list)
    redesign_changes: List[str] = field(default_factory=list)
    redesign_stats: Dict[str, float] = field(default_factory=dict)
    fallback_design: str = ""
    notes: List[str] = field(default_factory=list)
    # `type =` of the design's target_variant, i.e. the EQUIPMENT token
    # (`tank_usa_medium_chassis_6`), which is what an ai_strategy
    # `production_upgrade_desire_offset` takes as its `id`.  Distinct from
    # `design` (the ai_equipment block name, `medium_tank_7`) and from
    # `unlock_tech` (the TECHNOLOGY token, `usa_medium_tank_chassis_5`) - the
    # three numbering schemes do not line up and confusing them silently
    # targets the wrong tank.
    equipment_type: str = ""
    # Position of the design inside its ai_equipment group.  These files are
    # written oldest-first, so a higher index means a newer chassis - which is
    # exactly what the engine prefers by default and what the production
    # strategy has to suppress when the frontier ranks it lower.
    file_index: int = 0


def _weighted_gain(old: Dict[str, float], new: Dict[str, float],
                   weights: Dict[str, float], cfg: Config) -> float:
    return weighted_relative_gain(old, new, weights, cfg.stat_floor)


def _delta(old: Dict[str, float], new: Dict[str, float]) -> Dict[str, float]:
    return numeric_delta(old, new)


def _significant(delta: Dict[str, float], cfg: Config) -> Dict[str, float]:
    return significant_increases(delta, cfg.resource_threshold)


def _threshold_failures(stats: Dict[str, float], thresholds: Dict[str, float]) -> List[str]:
    return [f"{stat}={stats.get(stat, 0.0):.3g}<{minimum:g}"
            for stat, minimum in thresholds.items() if stats.get(stat, 0.0) < minimum]


def _nominal_frontier_priority(anchor: float, distance: int, cfg: Config) -> float:
    ladder = cfg.frontier_priority_ladder
    if distance < len(ladder):
        return anchor * ladder[distance]
    # Future-proof unusually large frontiers without ever producing zero.
    return anchor * ladder[-1] * (0.3 ** (distance - len(ladder) + 1))


def _frontier_priority(anchor: float, rank: int, count: int, cfg: Config) -> float:
    """Map a quality rank onto the configured descending dominance ladder.

    `rank == count` is the primary and preserves the group's historical
    maximum. Lower ranks remain positive fallbacks, but are separated by about
    3x/10x steps instead of sharing an arbitrary linear probability mass.

    The tail is re-spaced when the pure geometric ladder would underflow past
    `frontier_priority_floor`.  Ranks above the knee keep their exact geometric
    value - dominance is a property of the *top* of the ladder, and that is
    where it must not be diluted - while everything below is redistributed
    geometrically to land exactly on the floor.  Those ranks are all emergency
    fallbacks whose only requirements are "ordered" and "not zero"; the old
    behaviour gave them `factor = 0.000009`, which the engine's fixed-point
    script numbers cannot distinguish from `factor = 0`, i.e. *never build this*
    - the exact opposite of an emergency fallback.  A group whose ladder already
    fits above the floor is untouched.
    """
    distance = count - rank
    deepest = count - 1
    floor = cfg.frontier_priority_floor
    if deepest <= 0 or _nominal_frontier_priority(anchor, deepest, cfg) >= floor:
        return _nominal_frontier_priority(anchor, distance, cfg)
    if _nominal_frontier_priority(anchor, 0, cfg) <= floor:
        # The group's own historical maximum is at or below the floor; there is
        # no room to re-space into, so leave the caller's data alone rather than
        # inventing an ordering.
        return _nominal_frontier_priority(anchor, distance, cfg)
    knee = max(d for d in range(deepest + 1)
               if _nominal_frontier_priority(anchor, d, cfg) > floor)
    if distance <= knee:
        return _nominal_frontier_priority(anchor, distance, cfg)
    knee_value = _nominal_frontier_priority(anchor, knee, cfg)
    ratio = (floor / knee_value) ** (1.0 / (deepest - knee))
    # 3 decimals: the re-spaced band is a fallback ORDER, and twelve significant
    # digits of it would be noise in a file a human has to read. Ranks above the
    # knee are returned unrounded so a group whose ladder already fits stays
    # byte-identical to what is on disk.
    return round(knee_value * (ratio ** (distance - knee)), 3)


def _final_verdict(gain: float, retention: float, significant: Dict[str, float],
                   failures: List[str], cfg: Config, redesigned: bool = False) -> str:
    return decide_adoption(
        adjusted_gain=gain, retention=retention,
        significant_resources=significant, blockers=failures,
        model=cfg.efficiency_model, redesigned=redesigned)


def evaluate_tech_ground(mod_root: Path, cfg: Config, domain: str,
                         equipment_globs: Iterable[str], tech_globs: Iterable[str],
                         archetypes: Set[str], countries: Optional[Set[str]]) -> List[GroundTransition]:
    eq_dir = mod_root / "common/units/equipment"
    paths = sorted({p for glob in equipment_globs for p in eq_dir.glob(glob) if p.stat().st_size})
    db = InfantryDB(paths)
    out: List[GroundTransition] = []
    for glob in tech_globs:
        for path in sorted((mod_root / "common/technologies").glob(glob)):
            tag = path.stem.split("_", 1)[1].upper() if "_" in path.stem else "GENERIC"
            if tag.startswith("NON_") or (countries and tag not in countries):
                continue
            for old, new in _tech_edges(path, db, archetypes):
                if old.archetype != new.archetype:
                    continue
                relation = classify_relation(
                    old.name, new.name, old_archetype=old.archetype,
                    new_archetype=new.archetype, old_family=old.family,
                    new_family=new.family, is_ancestor=db.is_ancestor)
                retention = cfg.efficiency_model.factor(relation)
                role = old.archetype or domain
                weights = cfg.ground_weights(domain, role)
                stats = set(weights) | set(cfg.ground_thresholds(domain, role))
                old_stats = {s: db.resolve_float(old.name, s) for s in stats}
                new_stats = {s: db.resolve_float(new.name, s) for s in stats}
                gain = _weighted_gain(old_stats, new_stats, weights, cfg)
                adjusted = cfg.efficiency_model.adjusted_gain(gain, retention)
                res_delta = _delta(old.resources, new.resources)
                sig = _significant(res_delta, cfg)
                failures = _threshold_failures(new_stats, cfg.ground_thresholds(domain, role))
                verdict = _final_verdict(adjusted, retention, sig, failures, cfg)
                out.append(GroundTransition(
                    domain, tag, role, path.name, role, old.name, new.name,
                    relation, retention, gain, adjusted, verdict, old_stats, new_stats,
                    res_delta, sig, failures,
                    notes=["non-modular equipment: no variant search"] if failures else []))
    return out


@dataclass
class CoverageGap:
    """An equipment token a role can research but no design in it describes.

    `ai_equipment` only steers equipment it has a design for.  When a technology
    inside a role unlocks a chassis the role's group never mentions, the engine
    falls back to its own auto-designer: the mod's ranking, its resource gates
    and its production-line offsets all miss that chassis, and the AI happily
    builds it.  ENG's Comet (`tank_eng_medium_chassis_5`) is the case that
    exposed this - `ENG_medium_tanks` stops at Cromwell, so the whole frontier
    is moot from 1944 on and the emitted strategy file carries no suppression
    for the chassis the AI actually runs.
    """
    country: str
    group: str
    role: str
    equipment: str
    archetype: str
    unlock_tech: str
    branched: bool


class TankEvaluator:
    def __init__(self, mod_root: Path, cfg: Config) -> None:
        self.root, self.cfg = mod_root, cfg
        self.diag = Diagnostics()
        self.db = EquipmentDB(self.diag)
        eq_dir = mod_root / "common/units/equipment"
        self.db.load_airframes(find_files(eq_dir, ["tank_chassis.txt", "x_tank_chassis.txt"]))
        self.db.load_modules(find_files(eq_dir / "modules", ["*tank_modules.txt"]))
        self.model = StatModel(self.db, self.diag,
                               multiply_base_only=cfg.multiply_base_only,
                               thrust_weight_agility_factor=0.0)
        self.availability: Dict[str, Dict[str, float]] = {}
        self.tech_graph = TechnologyGraph(mod_root, self.diag)
        self.frontier_decisions: List[FrontierDecision] = []
        self.coverage_gaps: List[CoverageGap] = []
        self._children: Optional[Dict[str, List[str]]] = None

    def _coverage_gaps(self, group, designs, country_covered: Set[str],
                       branched: bool) -> List[CoverageGap]:
        """Equipment this role can research that no design in it describes.

        Walk forward from the group's own unlock techs along `path` edges and
        collect every `enable_equipments` token of the same archetype as one of
        the group's designs.  Anything not covered by ANY of the country's
        groups is a hole in the design layer: the engine auto-designs it, and
        the ranking, the resource gates and the emitted
        `production_upgrade_desire_offset` blocks all miss it.

        Reported, never auto-suppressed.  The evaluator has not scored these
        designs - it cannot know whether the uncovered chassis is better or
        worse than the group's primary - and blanket `-100` on an unevaluated
        chassis is exactly the kind of unilateral decision `emit_linear`
        already refuses to make for shared equipment buckets.
        """
        archetypes = {af.archetype for af in
                      (self.db.airframes.get(d.airframe) for d in designs)
                      if af and af.archetype}
        if not archetypes:
            return []
        own = {d.airframe for d in designs if d.airframe}
        reachable = self.tech_graph.reachable(
            tech for design in designs for tech in design.enable_techs)
        candidates = {token for tech in reachable
                      for token in self.tech_graph.enables.get(tech, ())}
        # Two independent routes to the same question, unioned on purpose: a
        # chassis can be missed by the tech walk (its unlock sits on a `path`
        # branch that does not leave this group) and still be a descendant of a
        # covered chassis in the equipment graph, or vice versa. Either signal
        # alone under-reports, and the ENG medium chain shows both shapes.
        candidates |= self._equipment_descendants(own)
        enabled_by = self.tech_graph.enabled_by()
        gaps: List[CoverageGap] = []
        for token in sorted(candidates):
            if token in country_covered or "ghost" in token:
                continue
            airframe = self.db.airframes.get(token)
            if not airframe or airframe.archetype not in archetypes:
                continue
            unlocks = enabled_by.get(token)
            # Never unlocked by any technology: unreachable data, not a gap.
            if not unlocks:
                continue
            gaps.append(CoverageGap(
                group.country, group.name, group.role, token,
                airframe.archetype, sorted(unlocks)[0], branched))
        return gaps

    def _equipment_descendants(self, roots: Set[str]) -> Set[str]:
        """Everything downstream of *roots* along `parent =`, ghosts traversed.

        The mod's "ghost" spacer chassis carry the chain across generations and
        are never enabled by a tech, so the walk must pass THROUGH them while
        the caller filters them out of the result.
        """
        children = self._children_index()
        out: Set[str] = set()
        frontier = list(roots)
        while frontier:
            node = frontier.pop()
            for child in children.get(node, ()):
                if child in out:
                    continue
                out.add(child)
                frontier.append(child)
        return out - roots

    def _children_index(self) -> Dict[str, List[str]]:
        if self._children is None:
            index: Dict[str, List[str]] = {}
            for name, airframe in self.db.airframes.items():
                if airframe.parent:
                    index.setdefault(airframe.parent, []).append(name)
            self._children = index
        return self._children

    def _ancestor(self, old: str, new: str) -> bool:
        target, cur, seen = old.lower(), new, set()
        by_lower = {k.lower(): k for k in self.db.airframes}
        while cur and cur.lower() not in seen:
            seen.add(cur.lower())
            af = self.db.airframes.get(cur) or self.db.airframes.get(by_lower.get(cur.lower(), ""))
            if not af:
                return False
            parent = af.parent
            if parent and parent.lower() == target:
                return True
            cur = parent or af.archetype
        return False

    def _relation(self, old: str, new: str) -> str:
        a, b = self.db.airframes.get(old), self.db.airframes.get(new)
        if not a or not b:
            return "unrelated"
        return classify_relation(old, new, old_archetype=a.archetype,
                                 new_archetype=b.archetype,
                                 old_family=None, new_family=None,
                                 is_ancestor=self._ancestor)

    def _score(self, st: DesignStats, role: str) -> Dict[str, float]:
        keys = set(self.cfg.ground_weights("tanks", role)) | set(self.cfg.ground_thresholds("tanks", role))
        return {k: st.stat(k) for k in keys}

    def _year(self, chassis: str) -> float:
        af = self.db.airframes.get(chassis)
        return float(af.year) if af and af.year is not None else 9999.0

    def _build_availability(self, groups_by_country: Dict[str, list]) -> None:
        for tag, groups in groups_by_country.items():
            table: Dict[str, float] = {}
            for group in groups:
                for design in group.designs:
                    year = self._year(design.airframe or "")
                    refs = list(design.modules.values()) + list(design.allowed_modules)
                    if design.airframe:
                        refs += list(self.db.resolve_default_modules(design.airframe).values())
                    for ref in refs:
                        mod, _ = self.db.resolve_module_ref(ref, tag)
                        if mod and (mod.name not in table or year < table[mod.name]):
                            table[mod.name] = year
            self.availability[tag] = table

    def _candidate_modules(self, tag: str, year: float,
                           slot_categories: Set[str]) -> List[str]:
        candidates = []
        for name, first_year in self.availability.get(tag, {}).items():
            mod = self.db.modules.get(name)
            if not mod or first_year > year:
                continue
            if mod.category not in slot_categories:
                continue
            candidates.append(name)
        return candidates[:self.cfg.tank_max_candidates_per_slot]

    def _redesign(self, design: Design, old_stats: DesignStats, new_stats: DesignStats,
                  role: str) -> Optional[Tuple[Dict[str, str], DesignStats, List[str]]]:
        thresholds = self.cfg.ground_thresholds("tanks", role)
        if not _threshold_failures(self._score(new_stats, role), thresholds):
            return None
        slots = self.db.resolve_slots(design.airframe or "")
        year = self._year(design.airframe or "")
        base = self.model.effective_modules(design)
        mutable = [s for s in slots if "main_armament" not in s and "turret_type" not in s]
        choices: List[Tuple[str, List[str]]] = []
        for slot in mutable:
            candidates = self._candidate_modules(design.country, year,
                                                  slots[slot].allowed_categories)
            current = base.get(slot, "empty")
            # Required slots (engine, suspension, armour, ...) may never be
            # emptied to manufacture a better reliability score. Optional
            # special slots may be dropped when that is a legal trade-off.
            optional_empty = [] if slots[slot].required else ["empty"]
            values = list(dict.fromkeys([current] + optional_empty + candidates))
            if len(values) > 1:
                choices.append((slot, values))
        best = None
        for slot, values in choices:
            for value in values:
                if value == base.get(slot, "empty"):
                    continue
                modules = dict(base)
                modules[slot] = value
                if self.db.count_limit_violations(design.airframe or "", modules):
                    continue
                st = self.model.compute(design, modules)
                if not st.ok:
                    continue
                redesign_resource_shock = _significant(
                    _delta(new_stats.resources, st.resources), self.cfg)
                if set(redesign_resource_shock) - self.cfg.runtime_resource_gates:
                    continue
                scored = self._score(st, role)
                if _threshold_failures(scored, thresholds):
                    continue
                gain = _weighted_gain(self._score(old_stats, role), scored,
                                      self.cfg.ground_weights("tanks", role), self.cfg)
                sacrifice = _weighted_gain(self._score(new_stats, role), scored,
                                           self.cfg.ground_weights("tanks", role), self.cfg)
                if gain < self.cfg.ground_min_gain or sacrifice < -self.cfg.max_redesign_sacrifice:
                    continue
                key = (gain, sacrifice, -st.cost_ic)
                if best is None or key > best[0]:
                    best = (key, modules, st, [f"{slot}: {base.get(slot, 'empty')} -> {value}"])
        return (best[1], best[2], best[3]) if best else None

    def evaluate(self, countries: Optional[Set[str]]) -> List[GroundTransition]:
        out: List[GroundTransition] = []
        ai_dir = self.root / "common/ai_equipment"
        groups_by_country = {}
        for tag in discover_countries(ai_dir, "tank"):
            if countries and tag not in countries:
                continue
            path = ai_dir / f"{tag}_tank.txt"
            groups_by_country[tag] = parse_country_file(path, tag, self.diag,
                                                        category_filter="land")
        self._build_availability(groups_by_country)
        for tag, groups in groups_by_country.items():
            path = ai_dir / f"{tag}_tank.txt"
            stop_techs = {
                tech for candidate_group in groups
                for design in candidate_group.designs for tech in design.enable_techs
            }
            # Coverage is a COUNTRY-level question: a chassis described by any of
            # this country's groups is steered, whichever group owns it.
            country_covered = {
                design.airframe for candidate_group in groups
                for design in candidate_group.designs if design.airframe
            }
            for group in groups:
                role = group.role
                designs = [d for d in group.designs if d.airframe]
                if not designs:
                    continue
                graph = self.tech_graph.design_graph(group, stop_techs)
                group.technology_edges = list(graph.edges)
                self.coverage_gaps.extend(
                    self._coverage_gaps(group, designs, country_covered,
                                        graph.branched))
                by_name = {design.name: design for design in designs}
                adjacency = graph.adjacency()

                if graph.branched:
                    self.frontier_decisions.extend(
                        self._evaluate_frontier(group, designs, graph.roots,
                                                graph.edges))

                def evaluate_branch(node_name: str, retained_name: str,
                                    ancestry: Set[str]) -> None:
                    for child_name in adjacency.get(node_name, []):
                        if child_name in ancestry:
                            continue
                        old, new = by_name[retained_name], by_name[child_name]
                        # Duplicate named blocks represent alternative definitions
                        # of one design, not a production-generation transition.
                        if old.name == new.name:
                            continue
                        a, b = self.model.compute(old), self.model.compute(new)
                        if not a.ok or not b.ok:
                            out.append(GroundTransition("tanks", tag, role, path.name,
                                group.name, old.name, new.name, "unresolved", 0.1, 0, 0,
                                UNRESOLVED, {}, {}, {}, {}, notes=["unresolved design/module"]))
                            continue
                        relation = self._relation(old.airframe or "", new.airframe or "")
                        retention = self.cfg.efficiency_model.factor(relation)
                        old_scored, new_scored = self._score(a, role), self._score(b, role)
                        gain = _weighted_gain(old_scored, new_scored,
                                              self.cfg.ground_weights("tanks", role), self.cfg)
                        failures = _threshold_failures(
                            new_scored, self.cfg.ground_thresholds("tanks", role))
                        redesigned = self._redesign(new, a, b, role) if failures else None
                        final_stats, changes = b, []
                        if redesigned:
                            _, final_stats, changes = redesigned
                            new_scored = self._score(final_stats, role)
                            gain = _weighted_gain(
                                old_scored, new_scored,
                                self.cfg.ground_weights("tanks", role), self.cfg)
                            failures = _threshold_failures(
                                new_scored, self.cfg.ground_thresholds("tanks", role))
                        adjusted = self.cfg.efficiency_model.adjusted_gain(gain, retention)
                        res_delta = _delta(a.resources, final_stats.resources)
                        sig = _significant(res_delta, self.cfg)
                        verdict = _final_verdict(
                            adjusted, retention, sig, failures, self.cfg,
                            redesigned=bool(redesigned))
                        out.append(GroundTransition(
                            "tanks", tag, role, path.name, group.name, old.name, new.name,
                            relation, retention, gain, adjusted, verdict,
                            old_scored, new_scored, res_delta, sig, failures, changes,
                            self._score(final_stats, role) if redesigned else {}, []))
                        next_retained = new.name if verdict in ADOPTION_VERDICTS else old.name
                        evaluate_branch(child_name, next_retained, ancestry | {child_name})

                if not graph.edges:
                    self.diag.warn("design_group_without_tech_edges", f"{tag}/{group.name}",
                                   "no unambiguous technology succession edges; group not evaluated")
                    continue
                for root in graph.roots:
                    evaluate_branch(root, root, {root})
        return out

    def _evaluate_frontier(self, group, designs: List[Design],
                           roots: Tuple[str, ...],
                           edges: Tuple[Tuple[str, str], ...] = ()) -> List[FrontierDecision]:
        """Rank every design sharing one branched production role.

        Research order only controls availability.  Quality, hard thresholds,
        redesign and resource affordability control which available design
        wins production.
        """
        role = group.role
        by_name = {d.name: d for d in designs}
        baseline_design = next((by_name[name] for name in roots if name in by_name),
                               designs[0])
        baseline_stats = self.model.compute(baseline_design)
        if not baseline_stats.ok:
            return []
        baseline_score = self._score(baseline_stats, role)
        weights = self.cfg.ground_weights("tanks", role)
        parents: Dict[str, List[str]] = {}
        for parent, child in edges:
            parents.setdefault(child, []).append(parent)
        computed = []

        for design in designs:
            default = self.model.compute(design)
            if not default.ok:
                self.diag.warn("frontier_unresolved_design", design.path,
                               "complete branched frontier withheld to preserve the role floor")
                return []
            final = default
            changes: List[str] = []
            scored = self._score(final, role)
            failures = _threshold_failures(
                scored, self.cfg.ground_thresholds("tanks", role))
            if failures and self.cfg.redesign_enabled:
                repair = self._redesign(design, baseline_stats, default, role)
                if repair:
                    _modules, final, changes = repair
                    scored = self._score(final, role)
                    failures = _threshold_failures(
                        scored, self.cfg.ground_thresholds("tanks", role))
            quality_score = _weighted_gain(baseline_score, scored, weights, self.cfg)
            retentions = []
            for parent_name in parents.get(design.name, []):
                parent = by_name.get(parent_name)
                if parent:
                    relation = self._relation(parent.airframe or "", design.airframe or "")
                    retentions.append(self.cfg.efficiency_model.factor(relation))
            retention = max(retentions, default=1.0)
            model = self.cfg.efficiency_model
            continuity_tax = model.efficiency_penalty_weight * max(
                0.0, model.penalty_free_retention - retention)
            if retention < model.full_switch_min_retention:
                continuity_tax = max(continuity_tax, model.low_retention_min_gain)
            score = quality_score - continuity_tax
            computed.append((design, final, scored, failures, changes, score,
                             quality_score, retention))

        valid = sorted((item for item in computed if not item[3]),
                       key=lambda item: (item[5], -item[1].cost_ic,
                                         item[0].index, item[0].name))
        invalid = sorted((item for item in computed if item[3]),
                         key=lambda item: (item[5], -item[1].cost_ic,
                                           item[0].index, item[0].name))
        if not valid:
            return []
        anchor = max((float(item[0].priority_factor or 0.0) for item in valid),
                     default=100.0)
        if anchor <= 0:
            anchor = 100.0

        rows: List[FrontierDecision] = []
        previous = None
        ordered = invalid + valid
        for position, item in enumerate(ordered, 1):
            design, final, scored, failures, changes, score, quality_score, retention = item
            gates: Dict[str, float] = {}
            fallback = ""
            if previous is not None:
                fallback = previous[0].name
                gates = _significant(
                    _delta(previous[1].resources, final.resources), self.cfg)
            rows.append(FrontierDecision(
                country=group.country, group=group.name, role=role,
                design=design.name, label=design.comment or design.name,
                unlock_tech=design.enable_techs[0] if len(design.enable_techs) == 1 else "",
                quality_score=quality_score, score=score,
                efficiency_retention=retention, rank=position,
                action=("PRIMARY" if position == len(ordered) else
                        "EMERGENCY_FALLBACK" if failures else "FALLBACK"),
                priority_factor=_frontier_priority(
                    anchor, position, len(ordered), self.cfg), stats=scored,
                resources=dict(final.resources), resource_gates=gates,
                failed_thresholds=failures,
                redesign_changes=changes,
                redesign_stats=scored if changes else {}, fallback_design=fallback,
                equipment_type=design.airframe or "", file_index=design.index,
                notes=(["kept as a low-priority role floor until a compliant design unlocks"]
                       if failures else [])))
            previous = item
        return sorted(rows, key=lambda row: (row.rank, row.design))


def write_coverage_audit(out_dir: Path, gaps: List[CoverageGap]) -> None:
    """List every chassis a role can research but no design in it describes."""
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ai_equipment coverage gaps",
        "",
        "Every equipment token unlocked by a technology reachable from inside an",
        "`ai_equipment` group, of the same archetype as that group's designs, and",
        "described by **no design in any group of that country**.",
        "",
        "The AI still builds these: with no design to match, the engine falls back to",
        "its own auto-designer. The evaluator's ranking, the `WA_AI_EQUIPMENT_*`",
        "resource gates and the emitted `production_upgrade_desire_offset` blocks all",
        "miss them, so a role whose newest chassis is uncovered is steered only until",
        "that chassis is researched, and unsteered afterwards.",
        "",
        "**Branched roles are listed first**: those are the ones",
        "`WA_AI_PRODUCTION_COUNTRY_<TAG>_TANKS.txt` claims to control.",
        "",
        "Closing a gap means authoring the missing design in the group (which lets the",
        "evaluator rank it), not suppressing the chassis - nothing here has been scored,",
        "so a blanket `-100` would be an unevaluated guess.",
        "",
        "| country | group | role | uncovered equipment | archetype | unlocked by | branched role |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for gap in sorted(gaps, key=lambda g: (not g.branched, g.country, g.group,
                                           g.equipment)):
        lines.append(f"| {gap.country} | {gap.group} | {gap.role} | "
                     f"`{gap.equipment}` | {gap.archetype} | `{gap.unlock_tech}` | "
                     f"{'YES' if gap.branched else 'no'} |")
    lines.append("")
    (out_dir / "coverage_gaps.md").write_text("\n".join(lines), encoding="utf-8")


def write_ground_reports(out_dir: Path, rows: List[GroundTransition],
                         frontiers: Optional[List[FrontierDecision]] = None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "ground_equipment_transitions.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(("domain", "country", "role", "source", "group", "from", "to",
                    "relation", "retention", "raw_gain", "adjusted_gain", "verdict",
                    "failed_thresholds", "resource_delta", "significant_resources",
                    "redesign_changes", "notes"))
        for r in rows:
            pack = lambda d: ";".join(f"{k}={v:+.3g}" for k, v in d.items() if v)
            w.writerow((r.domain, r.country, r.role, r.source, r.group, r.old, r.new,
                        r.relation, r.retention, r.raw_gain, r.adjusted_gain, r.verdict,
                        "|".join(r.failed_thresholds), pack(r.resource_delta),
                        pack(r.significant_resources), "|".join(r.redesign_changes),
                        "|".join(r.notes)))
    counts: Dict[Tuple[str, str], int] = {}
    for r in rows:
        counts[(r.domain, r.verdict)] = counts.get((r.domain, r.verdict), 0) + 1
    lines = ["# Ground equipment decision report", "",
             "Integrated verdict: stats + thresholds + redesign (tanks) + production efficiency + resources.", "",
             "| domain | verdict | count |", "| --- | --- | ---: |"]
    lines += [f"| {d} | {v} | {n} |" for (d, v), n in sorted(counts.items())]
    lines += ["", "## Non-trivial decisions", "",
              "| domain | country | transition | gain | retained | verdict | thresholds/redesign/resources |",
              "| --- | --- | --- | ---: | ---: | --- | --- |"]
    for r in rows:
        if r.verdict != SWITCH or r.redesign_changes:
            detail = "; ".join(r.failed_thresholds + r.redesign_changes +
                               [f"{k} {v:+g}" for k, v in r.significant_resources.items()])
            lines.append(f"| {r.domain} | {r.country} | `{r.old}` → `{r.new}` | "
                         f"{r.adjusted_gain:+.3f} | {r.retention:.0%} | {r.verdict} | {detail} |")
    if frontiers:
        lines += ["", "## Branched production-role frontiers", "",
                  "The highest-ranked researched design wins. Resource gates temporarily "
                  "drop an expensive candidate to the next fallback; rejected designs "
                  "cannot take the production role.", "",
                  "| country/group | rank | design | decision | quality / adjusted | retention | factor | fallback / gates |",
                  "| --- | ---: | --- | --- | ---: | ---: | ---: | --- |"]
        for row in sorted(frontiers, key=lambda r: (r.country, r.group, -r.rank, r.design)):
            gates = ", ".join(f"{k} +{v:g}" for k, v in row.resource_gates.items())
            detail = (f"{row.fallback_design}; {gates}" if row.fallback_design else gates)
            if row.failed_thresholds:
                detail = "; ".join(row.failed_thresholds)
            lines.append(f"| {row.country}/{row.group} | {row.rank} | "
                         f"{row.label} (`{row.design}`) | {row.action} | "
                         f"{row.quality_score:+.3f} / {row.score:+.3f} | "
                         f"{row.efficiency_retention:.0%} | "
                         f"{row.priority_factor:.3g} | {detail} |")
        _write_frontier_report(out_dir / "parallel_branch_decisions.md", frontiers)
    (out_dir / "ground_equipment_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_frontier_report(path: Path, rows: List[FrontierDecision]) -> None:
    by_group: Dict[Tuple[str, str], List[FrontierDecision]] = {}
    for row in rows:
        by_group.setdefault((row.country, row.group), []).append(row)
    lines = [
        "# Parallel technology-branch decisions", "",
        "Generated from the real technology graph, not ai_equipment file order.", "",
        "Decision rules:", "",
        "- highest-ranked researched and affordable design wins the shared role;",
        "- 5-10% efficiency loss is free; deeper losses pay the configured continuity tax;",
        "- hard-stat failures remain low-priority emergency fallbacks, preventing gaps;",
        "- a strategic-resource shock holds a candidate and exposes the next rank;",
        "- no `NEW_LINES_ONLY` behaviour is emitted.", "",
        "## Group summary", "",
        "| country/group | primary | descending fallback order | emergency floor(s) |",
        "| --- | --- | --- | --- |",
    ]
    for key, group_rows in sorted(by_group.items()):
        ordered = sorted(group_rows, key=lambda row: (-row.rank, row.design))
        primary = next(row for row in ordered if row.action == "PRIMARY")
        fallbacks = " > ".join(row.label for row in ordered
                               if row.action == "FALLBACK") or "-"
        emergency = ", ".join(row.label for row in ordered
                              if row.action == "EMERGENCY_FALLBACK") or "-"
        lines.append(f"| {key[0]}/{key[1]} | {primary.label} | {fallbacks} | {emergency} |")
    lines += ["", "## Complete arbitration", "",
              "| country/group | rank | model | decision | quality | adjusted | retention | resource hold -> fallback |",
              "| --- | ---: | --- | --- | ---: | ---: | ---: | --- |"]
    for key, group_rows in sorted(by_group.items()):
        for row in sorted(group_rows, key=lambda item: (-item.rank, item.design)):
            gates = ", ".join(f"{resource} +{delta:g}"
                              for resource, delta in sorted(row.resource_gates.items()))
            hold = ""
            if gates:
                hold = f"{gates} -> {row.fallback_design}"
            elif row.fallback_design:
                hold = row.fallback_design
            lines.append(f"| {key[0]}/{key[1]} | {row.rank} | {row.label} "
                         f"(`{row.design}`) | {row.action} | {row.quality_score:+.3f} | "
                         f"{row.score:+.3f} | {row.efficiency_retention:.0%} | {hold} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
