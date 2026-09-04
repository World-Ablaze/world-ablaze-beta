"""
Decision engine: per (country, role, generation N -> N+1) transition, decide
whether the AI should adopt the newer design.

Verdicts
--------
SWITCH              new default design is fine; adopt it.
SWITCH_REDESIGNED   new generation is worth it, but only with a modified
                    module loadout that restores range; the loadout is listed.
KEEP_OLD            new generation is a net regression - it misses the range
                    target and no redesign fixes it without giving up more than
                    it gains (or it is a flat stat regression).
SWITCH_CONDITIONAL  stats are better but the per-unit resource bill grows by a
                    significant amount; the switch should be gated at runtime
                    on economy state. The offending resource + delta is recorded.
PARALLEL_VARIANT    the pair is not a generation step at all - the two designs
                    share an airframe, or the chain jumps between two parallel
                    families in one design group. Numbers are still published,
                    but no switch decision is meaningful.
UNRESOLVED          the tool could not resolve the airframe or a module; the
                    row is emitted anyway and listed in the diagnostics. Never
                    silently dropped.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .config import Config
from .decision_policy import (ADOPTION_VERDICTS, KEEP_OLD, PARALLEL_VARIANT, SWITCH,
                              SWITCH_CONDITIONAL, SWITCH_REDESIGNED, UNRESOLVED,
                              apply_efficiency_gate, numeric_delta,
                              significant_increases)
from .production_efficiency import classify_relation
from .diagnostics import Diagnostics
from .parse_ai_equipment import Design, DesignGroup
from .parse_equipment import EquipmentDB
from .stats import DesignStats, StatModel
from .technology_graph import TechnologyGraph

# A design family is the airframe's archetype in common/units/equipment (small
# fighter, fast bomber, medium bomber...): two lines of one role group that are
# different products, e.g. JAP_light_bomber's Ki-48 (fast_bomber_airframe) next
# to its Ki-21/Ki-49 (medium_bomber_airframe). Design keys carry no family
# information - they are the airframe id (documentation/AI_EQUIPMENT_NAMING.md).


def airframe_family(airframes, airframe: Optional[str]) -> Optional[str]:
    """The airframe's archetype (small fighter, fast bomber, medium bomber...),
    read up the `parent` chain when the leaf does not declare one."""
    if not airframe:
        return None
    cur, seen = airframe, set()
    while cur and cur not in seen:
        seen.add(cur)
        af = airframes.get(cur)
        if af is None:
            return cur
        if af.archetype:
            return af.archetype
        cur = af.parent
    return airframe


REPORT_STATS = (
    "air_attack", "air_defence", "air_agility", "maximum_speed",
    "air_ground_attack", "air_bombing", "naval_strike_attack",
    "naval_strike_targetting", "surface_detection", "sub_detection",
    "reliability", "thrust", "weight",
)


# --------------------------------------------------------------------- scoring
def weighted_gain(old: DesignStats, new: DesignStats, cfg: Config, role: str) -> float:
    """Dimensionless weighted relative gain of `new` over `old`.

        gain = SUM_s w_s * (new_s - old_s) / max(|old_s|, floor_s)   /   SUM |w_s|
    """
    weights = cfg.role_weights(role)
    denom = sum(abs(w) for w in weights.values()) or 1.0
    total = 0.0
    for stat, w in weights.items():
        o = old.stat(stat)
        n = new.stat(stat)
        floor = cfg.stat_floor(stat)
        total += w * (n - o) / max(abs(o), floor)
    return total / denom


def resource_delta(old: DesignStats, new: DesignStats) -> Dict[str, float]:
    return numeric_delta(old.resources, new.resources)


def significant_resources(delta: Dict[str, float], cfg: Config) -> Dict[str, float]:
    return significant_increases(delta, cfg.resource_threshold)


# ------------------------------------------------------------------- redesign
@dataclass
class Redesign:
    modules: Dict[str, str]                 # full slot -> module map of the variant
    changes: List[Tuple[str, str, str]]     # (slot, old_module, new_module)
    stats: DesignStats
    gain_vs_old: float
    gain_vs_new: float

    def change_str(self) -> str:
        return "; ".join(f"{s}: {a or 'empty'} -> {b or 'empty'}" for s, a, b in self.changes)


class RedesignSearch:
    """Search the module space of the NEW airframe for a range-restoring variant."""

    def __init__(self, db: EquipmentDB, model: StatModel, cfg: Config,
                 diag: Diagnostics, availability: Dict[str, Dict[str, float]]) -> None:
        self.db = db
        self.model = model
        self.cfg = cfg
        self.diag = diag
        # country -> module name -> earliest airframe year it is seen with
        self.availability = availability

    def _pool(self, country: str, year: Optional[float], extra: Sequence[str]) -> set:
        avail = self.availability.get(country, {})
        if year is None:
            pool = set(avail)
        else:
            pool = {m for m, y in avail.items() if y <= year}
        pool.update(extra)
        return pool

    def _slot_candidates(self, airframe: str, slot: str, pool: set,
                         want_categories: Sequence[str], engine: bool) -> List[str]:
        slots = self.db.resolve_slots(airframe)
        spec = slots.get(slot)
        if spec is None or not spec.allowed_categories:
            # Empty allowed_module_categories on a concrete airframe is
            # ambiguous (archetype slots declare it empty and concrete frames
            # override). We refuse to invent modules for such a slot.
            return []
        banned = self.db.forbidden_modules(airframe)
        banned_cats = self.db.forbidden_categories(airframe)
        out: List[Tuple[float, str]] = []
        for name in pool:
            if name in banned:
                continue
            mod = self.db.modules.get(name)
            if mod is None or mod.category is None:
                continue
            if mod.category in banned_cats:
                continue
            if mod.category not in spec.allowed_categories:
                continue
            if engine:
                pass  # engine slot: category match already restricts to engines
            elif want_categories and not any(w in mod.category for w in want_categories):
                continue
            score = (mod.multiply_stats.get("air_range", 0.0) * 100.0
                     + mod.add_stats.get("air_range", 0.0))
            out.append((score, name))
        out.sort(key=lambda t: (-t[0], t[1]))
        return [n for _s, n in out[: self.cfg.max_candidates_per_slot]]

    def search(self, design: Design, base_stats: DesignStats, old_stats: DesignStats,
               role: str, target: float, year: Optional[float],
               mission: Optional[str] = None) -> Optional[Redesign]:
        if not self.cfg.redesign_enabled or not design.airframe:
            return None
        slots = self.db.resolve_slots(design.airframe)
        if not slots:
            return None

        pool = self._pool(design.country, year, design.allowed_modules)
        want = self.cfg.range_module_categories
        current_modules = self.model.effective_modules(design)

        slot_options: Dict[str, List[str]] = {}
        for slot, spec in slots.items():
            if not spec.allowed_categories:
                continue
            is_engine = "engine_type" in slot
            if is_engine and not self.cfg.allow_engine_swap:
                continue
            if not is_engine:
                if not any(any(w in cat for w in want) for cat in spec.allowed_categories):
                    continue
            cands = self._slot_candidates(design.airframe, slot, pool, want, is_engine)
            current = current_modules.get(slot, "empty")
            options = [c for c in cands if c != current]
            if not spec.required and current not in ("empty", ""):
                options.append("empty")   # dropping ordnance can free range-relevant slots
            if options:
                slot_options[slot] = options

        if not slot_options:
            return None

        max_changes = max(1, self.cfg.max_slot_changes)
        best: Optional[Redesign] = None
        evaluated = 0
        eval_cap = 4000

        slot_names = list(slot_options)
        for k in range(1, min(max_changes, len(slot_names)) + 1):
            for combo in itertools.combinations(slot_names, k):
                for picks in itertools.product(*(slot_options[s] for s in combo)):
                    evaluated += 1
                    if evaluated > eval_cap:
                        self.diag.warn("redesign_search_capped", design.path,
                                       f"module search hit the {eval_cap}-variant cap; "
                                       f"best result may not be optimal")
                        return best
                    candidate = dict(current_modules)
                    changes: List[Tuple[str, str, str]] = []
                    for slot, mod in zip(combo, picks):
                        changes.append((slot, candidate.get(slot, "empty"), mod))
                        candidate[slot] = mod
                    # Never propose a loadout the designer cannot build: the
                    # search can otherwise stack a second copy of a module the
                    # airframe caps at one.
                    if self.db.count_limit_violations(design.airframe, candidate):
                        continue
                    st = self.model.compute(design, candidate, mission)
                    if not st.airframe_resolved or st.unresolved_modules:
                        continue
                    if st.range_km < target:
                        continue
                    g_new = weighted_gain(base_stats, st, self.cfg, role)
                    g_old = weighted_gain(old_stats, st, self.cfg, role)
                    if best is None or g_new > best.gain_vs_new:
                        best = Redesign(modules=candidate, changes=changes, stats=st,
                                        gain_vs_old=g_old, gain_vs_new=g_new)
        return best


# ------------------------------------------------------------------ transition
@dataclass
class Transition:
    country: str
    group: str
    role: str
    from_design: str
    to_design: str
    from_label: str = ""
    to_label: str = ""
    from_airframe: str = ""
    to_airframe: str = ""
    from_year: Optional[int] = None
    to_year: Optional[int] = None
    mission: str = ""
    range_old: float = 0.0
    range_new: float = 0.0
    range_target: float = 0.0
    ic_old: float = 0.0
    ic_new: float = 0.0
    gain: float = 0.0
    efficiency_relation: str = ""
    efficiency_retention: float = 1.0
    efficiency_original_verdict: str = ""
    verdict: str = UNRESOLVED
    old_stats: Dict[str, float] = field(default_factory=dict)
    new_stats: Dict[str, float] = field(default_factory=dict)
    res_old: Dict[str, float] = field(default_factory=dict)
    res_new: Dict[str, float] = field(default_factory=dict)
    res_delta: Dict[str, float] = field(default_factory=dict)
    res_significant: Dict[str, float] = field(default_factory=dict)
    redesign: Optional[Redesign] = None
    flags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def range_gate(self) -> str:
        return "PASS" if self.range_new >= self.range_target else "FAIL"


class Evaluator:
    def __init__(self, db: EquipmentDB, model: StatModel, cfg: Config,
                 diag: Diagnostics, tech_graph: TechnologyGraph) -> None:
        self.db = db
        self.model = model
        self.cfg = cfg
        self.diag = diag
        self.availability: Dict[str, Dict[str, float]] = {}
        self.search: Optional[RedesignSearch] = None
        self.tech_graph = tech_graph

    # -- module availability proxy ---------------------------------------
    def build_availability(self, groups_by_country: Dict[str, List[DesignGroup]]) -> None:
        """For each country, the earliest airframe `year` each module is seen with.

        This is the tool's proxy for "does this country plausibly have this
        module at this point in the tech tree". A module is considered
        available to a redesign of an airframe of year Y if the country's own
        design set already uses it on some airframe of year <= Y.
        """
        for country, groups in groups_by_country.items():
            table: Dict[str, float] = {}
            for group in groups:
                for design in group.designs:
                    year = self._year(design.airframe)
                    y = float(year) if year is not None else 9999.0
                    refs = list(design.modules.values()) + list(design.allowed_modules)
                    for ref in refs:
                        if not ref or ref.lower() == "empty":
                            continue
                        mod, _kind = self.db.resolve_module_ref(ref, country)
                        if mod is None:
                            continue
                        if mod.name not in table or y < table[mod.name]:
                            table[mod.name] = y
            self.availability[country] = table
        self.search = RedesignSearch(self.db, self.model, self.cfg, self.diag, self.availability)

    def _year(self, airframe: Optional[str]) -> Optional[int]:
        if not airframe:
            return None
        seen = set()
        cur = airframe
        while cur and cur not in seen:
            seen.add(cur)
            af = self.db.airframes.get(cur)
            if af is None:
                return None
            if af.year is not None:
                return af.year
            cur = af.parent or af.archetype
        return None

    # -- main -------------------------------------------------------------
    def evaluate_group(self, group: DesignGroup) -> List[Transition]:
        role = group.role
        target = self.cfg.range_target(role)
        out: List[Transition] = []

        evaluable = [d for d in group.designs if d.airframe]
        skipped = [d for d in group.designs if not d.airframe]
        for d in skipped:
            self.diag.warn("design_skipped_no_airframe", d.path,
                           "design has no resolvable airframe; excluded from the transition chain")

        if not evaluable:
            return out
        graph = self.tech_graph.design_graph(group)
        group.technology_edges = list(graph.edges)
        if not graph.edges:
            self.diag.warn("design_group_without_tech_edges", f"{group.country}/{group.name}",
                           "no unambiguous technology succession edges; group not evaluated")
            return out
        by_name = {design.name: design for design in evaluable}
        adjacency = graph.adjacency()

        def evaluate_branch(node_name: str, retained_name: str, ancestry: set[str]) -> None:
            for child_name in adjacency.get(node_name, []):
                if child_name in ancestry:
                    continue
                retained, candidate = by_name[retained_name], by_name[child_name]
                transition = self.evaluate_transition(
                    group, role, target, retained, candidate)
                relation = classify_relation(
                    retained.airframe or "", candidate.airframe or "",
                    old_archetype=self._archetype(retained.airframe),
                    new_archetype=self._archetype(candidate.airframe),
                    old_family=None, new_family=None,
                    is_ancestor=self._airframe_ancestor)
                transition.efficiency_relation = relation
                transition.efficiency_retention = self.cfg.efficiency_model.factor(relation)
                transition.verdict = apply_efficiency_gate(
                    transition.verdict, transition.gain,
                    transition.efficiency_retention, self.cfg.efficiency_model)
                out.append(transition)
                next_retained = (candidate.name if transition.verdict in ADOPTION_VERDICTS
                                 else retained.name)
                evaluate_branch(child_name, next_retained, ancestry | {child_name})

        for root in graph.roots:
            evaluate_branch(root, root, {root})
        return out

    def _archetype(self, name: Optional[str]) -> Optional[str]:
        item = self.db.airframes.get(name or "")
        return item.archetype if item else None

    def _airframe_ancestor(self, old: str, new: str) -> bool:
        target, current, seen = old, new, set()
        while current and current not in seen:
            seen.add(current)
            item = self.db.airframes.get(current)
            if item is None:
                return False
            parent = item.parent
            if parent == target:
                return True
            current = parent or item.archetype
        return False

    def evaluate_transition(self, group: DesignGroup, role: str, target: float,
                            old: Design, new: Design) -> Transition:
        mission = self.cfg.role_mission(role)
        old_stats = self.model.compute(old, mission=mission)
        new_stats = self.model.compute(new, mission=mission)

        t = Transition(
            country=group.country, group=group.name, role=role,
            from_design=old.name, to_design=new.name,
            from_label=old.comment, to_label=new.comment,
            from_airframe=old.airframe or "", to_airframe=new.airframe or "",
            from_year=self._year(old.airframe), to_year=self._year(new.airframe),
            mission=mission,
            range_target=target,
        )
        t.flags = sorted(set(old_stats.flags) | set(new_stats.flags))

        if not (old_stats.airframe_resolved and new_stats.airframe_resolved) \
                or old_stats.unresolved_modules or new_stats.unresolved_modules:
            t.verdict = UNRESOLVED
            t.notes.append("stat model incomplete - see diagnostics")
            # still publish whatever numbers we do have
            t.range_old = old_stats.range_km
            t.range_new = new_stats.range_km
            t.ic_old = old_stats.cost_ic
            t.ic_new = new_stats.cost_ic
            t.old_stats = {k: old_stats.stat(k) for k in REPORT_STATS}
            t.new_stats = {k: new_stats.stat(k) for k in REPORT_STATS}
            t.res_old = dict(old_stats.resources)
            t.res_new = dict(new_stats.resources)
            t.res_delta = resource_delta(old_stats, new_stats)
            return t

        t.range_old = old_stats.range_km
        t.range_new = new_stats.range_km
        t.ic_old = old_stats.cost_ic
        t.ic_new = new_stats.cost_ic
        t.old_stats = {k: old_stats.stat(k) for k in REPORT_STATS}
        t.new_stats = {k: new_stats.stat(k) for k in REPORT_STATS}
        t.res_old = dict(old_stats.resources)
        t.res_new = dict(new_stats.resources)
        t.res_delta = resource_delta(old_stats, new_stats)
        t.res_significant = significant_resources(t.res_delta, self.cfg)
        t.gain = weighted_gain(old_stats, new_stats, self.cfg, role)

        # -- is this pair a generation step at all? --------------------------
        # File position is the generation chain, but a design group may hold
        # sibling loadouts on one airframe (GER heavy_fighter_5_1 air-to-air vs
        # 5_2 tank-buster) or two parallel families (JAP heavy_strike_bomber_*
        # and light_strike_bomber_* share JAP_strike_bomber). Neither is a
        # supersession, so no switch decision applies.
        year_regression = (t.from_year is not None and t.to_year is not None
                           and t.to_year < t.from_year)
        if old.airframe and new.airframe and old.airframe == new.airframe:
            t.verdict = PARALLEL_VARIANT
            t.flags.append("same_airframe")
            t.notes.append(
                f"not a generation step: both designs use `{t.to_airframe}` - "
                f"these are sibling loadouts, not a supersession")
            return t
        old_family = airframe_family(self.db.airframes, old.airframe)
        new_family = airframe_family(self.db.airframes, new.airframe)
        if year_regression and old_family != new_family:
            t.verdict = PARALLEL_VARIANT
            t.flags.append("parallel_family")
            t.notes.append(
                f"not a generation step: `{old_family}` "
                f"({t.from_year}) -> `{new_family}` ({t.to_year}) "
                f"crosses two parallel families in one design group")
            return t
        if year_regression:
            # Same family, but the chain runs backwards in time. That is a real
            # transition with a suspicious order - surface it, do not hide it.
            t.flags.append("chain_order_inversion")
            t.notes.append(
                f"chain order inversion: airframe year {t.from_year} -> {t.to_year}")

        range_ok = t.range_new >= target

        if range_ok:
            # The range gate is one-sided by construction (it tests the new
            # design only, and air_range is not a scored stat). A step that
            # lifts the design OVER the target therefore reads as a pure
            # regression - which marked the mod's own Fix 47/49 long-range
            # variants KEEP_OLD. Credit the recovery, subject to the same
            # "range at any price" guard the redesign search uses.
            recovers_range = t.range_old < target <= t.range_new
            if recovers_range and t.gain < 0.0:
                if t.gain >= -self.cfg.range_recovery_max_sacrifice:
                    t.verdict = SWITCH_CONDITIONAL if t.res_significant else SWITCH
                    t.notes.append(
                        f"range recovery: {t.range_old:.0f} -> {t.range_new:.0f} km "
                        f"clears the {target:.0f} km target the old generation missed, "
                        f"for {-t.gain:.3f} of weighted combat score "
                        f"(limit {self.cfg.range_recovery_max_sacrifice})")
                    if t.res_significant:
                        t.notes.append("gate at runtime on: " + ", ".join(
                            f"{k} +{v:.2f}/unit" for k, v in sorted(t.res_significant.items())))
                else:
                    t.verdict = KEEP_OLD
                    t.notes.append(
                        f"range recovery {t.range_old:.0f} -> {t.range_new:.0f} km rejected: "
                        f"gives up {-t.gain:.3f} > range_recovery_max_sacrifice "
                        f"{self.cfg.range_recovery_max_sacrifice}")
                return t
            if t.gain < 0.0:
                t.verdict = KEEP_OLD
                t.notes.append(f"range gate passed but stats regress (gain {t.gain:+.3f})")
            elif t.res_significant:
                t.verdict = SWITCH_CONDITIONAL
                t.notes.append("gate at runtime on: " + ", ".join(
                    f"{k} +{v:.2f}/unit" for k, v in sorted(t.res_significant.items())))
            else:
                t.verdict = SWITCH
                if t.gain < self.cfg.min_net_gain:
                    t.notes.append(f"marginal gain ({t.gain:+.3f} < min_net_gain "
                                   f"{self.cfg.min_net_gain})")
            return t

        # Range gate failed -> try to redesign the new airframe.
        if t.range_old < target:
            t.notes.append(f"note: the OLD generation is also below target "
                           f"({t.range_old:.0f} km) - the whole family is short-legged")
        redesign = None
        if self.search is not None:
            redesign = self.search.search(new, new_stats, old_stats, role, target,
                                          t.to_year, mission)
        t.redesign = redesign

        redesign_usable = (
            redesign is not None
            and redesign.gain_vs_old >= self.cfg.redesign_min_gain
            and redesign.gain_vs_new >= -self.cfg.max_redesign_sacrifice
        )

        if redesign_usable:
            t.verdict = SWITCH_REDESIGNED
            t.notes.append(
                f"range {t.range_new:.0f} -> {redesign.stats.range_km:.0f} km via "
                f"{redesign.change_str()} (combat gain vs old {redesign.gain_vs_old:+.3f}, "
                f"cost vs new default {redesign.gain_vs_new:+.3f})")
            redesign_res_delta = resource_delta(old_stats, redesign.stats)
            sig = significant_resources(redesign_res_delta, self.cfg)
            if sig:
                t.notes.append("redesign also raises: " + ", ".join(
                    f"{k} +{v:.2f}/unit" for k, v in sorted(sig.items())))
            return t

        if redesign is not None:
            t.notes.append(
                f"best range-restoring variant rejected: {redesign.change_str()} reaches "
                f"{redesign.stats.range_km:.0f} km but gives up {-redesign.gain_vs_new:.3f} "
                f"vs the new default (gain vs old {redesign.gain_vs_old:+.3f})")
        else:
            t.notes.append(f"no module combination on `{t.to_airframe}` reaches "
                           f"{target:.0f} km")

        # No usable redesign. The new generation is adopted anyway only if it is
        # genuinely better than the old one; otherwise the spec's KEEP_OLD case
        # applies (below range target AND not better than current).
        if t.gain >= self.cfg.range_override_gain:
            t.verdict = SWITCH_CONDITIONAL if t.res_significant else SWITCH
            t.notes.append(
                f"adopted despite the range gate: {t.range_new:.0f} < {target:.0f} km, "
                f"but the stat gain ({t.gain:+.3f}) clears range_override_gain "
                f"{self.cfg.range_override_gain}")
            if t.res_significant:
                t.notes.append("gate at runtime on: " + ", ".join(
                    f"{k} +{v:.2f}/unit" for k, v in sorted(t.res_significant.items())))
        else:
            t.verdict = KEEP_OLD
            t.notes.append(f"below range target and not better than current "
                           f"(gain {t.gain:+.3f} < {self.cfg.range_override_gain})")
        return t
