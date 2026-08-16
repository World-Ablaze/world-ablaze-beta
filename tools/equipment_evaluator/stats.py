"""
Stat model: turn (airframe, slot -> module) into a stat block.

Stacking formula
----------------
For every stat `s`:

    final[s] = (base[s] + SUM add_stats[s]) * (1 + SUM multiply_stats[s])

`base[s]` is the airframe's own value, resolved up the parent/archetype chain.

Evidence for this formula (from the mod's own data):

* `SOV_i_15_airframe` has `maximum_speed = 317  # 367` and its default engine
  `SOV_engine_shvetsov_m_25a_1x` has `multiply_stats = { maximum_speed = 0.156 }`.
  317 * 1.156 = 366.5 -> the author's "367" annotation. So multiply_stats is a
  fraction of the base, added on, not a raw multiplier.
* `non_strategic_materials` (wooden construction) has
  `multiply_stats = { thrust = -0.15 }`, but no airframe declares a base
  `thrust` at all - thrust comes entirely from engine `add_stats`. A
  "multiply the base only" reading would make wooden construction a no-op on
  thrust, which is plainly not the intent. Therefore multipliers apply to
  `base + adds`.

The `multiply_base_only` config knob flips this back to
`base * (1 + SUM mult) + SUM add` if a future in-game measurement contradicts
the reading above.

Mission-conditional stats
-------------------------
A module may declare `mission_type_stats = { limit = { <missions> } add_stats
multiply_stats add_average_stats }`, which applies only while the aircraft
flies one of those missions. The mod's plane modules carry 683 such blocks and
they hold the stats that actually differentiate designs within a role:

* `air_ground_radar_1/2` grant `surface_detection` 30/40 and `sub_detection`
  2/3 there - and they are the ONLY meaningful source of those stats, since
  the only plain-`add_stats` sources in the whole module set are `floats`
  (+5/+1) and `flying_boat_large` (+10/+1).
* every torpedo mount grants `naval_strike_targetting` 4..18 there.
* 224 modules grant `air_attack` under `interception`.
* ordnance carries its agility/weight penalty there.

`compute(mission=...)` applies the blocks whose `limit` contains that mission
(an absent `limit` means unconditional). The mission comes from
`config.role_missions`, one primary mission per role: applying every block that
overlaps a role's mission set would double-count, since a design is scored as
if flying one job.

`add_average_stats` is a third stacking kind: contributions are AVERAGED over
the modules that declare the stat, not summed - two torpedo mounts declaring
`naval_strike_targetting = 10` give 10, not 20. It is folded into the `adds`
bucket after averaging, so the formula above is otherwise unchanged.

Derived stats
-------------
* Agility gets `NDefines.NAir.THRUST_WEIGHT_AGILITY_FACTOR * max(0, thrust - weight)`
  added on top (define is 1 in `common/defines/05_defines.lua:660`,
  "additive agility bonus per point of thrust exceeding weight").
* Resources: airframe `resources = {}` (inherited) plus every module's
  `build_cost_resources`, clamped at >= 0.

Not modelled: research/doctrine/national-spirit modifiers, equipment upgrade
levels (`common/units/equipment/upgrades/`), production-efficiency effects,
and any thrust -> speed relationship (the mod bakes speed into engine
`multiply_stats`, and no define ties thrust to speed).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .diagnostics import Diagnostics
from .parse_equipment import EquipmentDB
from .parse_ai_equipment import Design

EMPTY_TOKENS = {"empty", "none"}


@dataclass
class DesignStats:
    design: Design
    airframe: Optional[str]
    stats: Dict[str, float] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=dict)
    modules: Dict[str, str] = field(default_factory=dict)   # slot -> module (resolved, non-empty)
    unresolved_modules: List[str] = field(default_factory=list)
    airframe_resolved: bool = False
    flags: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.airframe_resolved and not self.unresolved_modules

    def stat(self, key: str) -> float:
        return self.stats.get(key, 0.0)

    @property
    def range_km(self) -> float:
        return self.stat("air_range")

    @property
    def cost_ic(self) -> float:
        return self.stat("build_cost_ic")


class StatModel:
    def __init__(self, db: EquipmentDB, diag: Diagnostics, *,
                 multiply_base_only: bool = False,
                 thrust_weight_agility_factor: float = 1.0) -> None:
        self.db = db
        self.diag = diag
        self.multiply_base_only = multiply_base_only
        self.twaf = thrust_weight_agility_factor

    # ------------------------------------------------------------------
    def effective_modules(self, design: Design,
                          override: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """The design's `modules`, plus airframe defaults for unfilled REQUIRED slots.

        Per `common/ai_equipment/_documentation.info`, `allowed_modules` lists
        the only modules the designer may put in remaining open slots - so when
        it is empty (which it is for every plane design in this mod) optional
        slots the `target_variant` does not mention stay empty. Required slots
        cannot: the designer has to fill them, and the airframe's
        `default_modules` is the closest offline stand-in for what it picks.

        This matters: four designs declare a completely empty `modules = {}`
        block and would otherwise be scored as an airframe with no engine.
        """
        chosen = dict(design.modules if override is None else override)
        if not design.airframe:
            return chosen
        defaults = self.db.resolve_default_modules(design.airframe)
        slots = self.db.resolve_slots(design.airframe)
        for slot, spec in slots.items():
            if slot in chosen or not spec.required:
                continue
            fallback = defaults.get(slot)
            if fallback and fallback.lower() not in EMPTY_TOKENS:
                chosen[slot] = fallback
        return chosen

    def compute(self, design: Design, modules: Optional[Dict[str, str]] = None,
                mission: Optional[str] = None) -> DesignStats:
        """Compute stats for `design`, optionally overriding its slot->module map.

        `mission` selects which `mission_type_stats` blocks apply (see the
        module docstring). Pass the role's primary mission; `None` reproduces
        the pre-mission behaviour and is only used by callers that genuinely
        have no role context.
        """
        out = DesignStats(design=design, airframe=design.airframe, flags=list(design.flags))
        slot_map = self.effective_modules(design, modules)
        if design.airframe and not design.modules:
            self.diag.warn("empty_modules_block", design.path,
                           f"target_variant declares no modules; the airframe's "
                           f"default_modules filled {len(slot_map)} required slot(s)")
            out.flags.append("defaults_assumed")

        if not design.airframe:
            return out
        if design.airframe not in self.db.airframes:
            self.diag.error("unresolved_airframe", design.path,
                            f"airframe `{design.airframe}` is not defined in any parsed "
                            f"equipment file")
            out.flags.append(f"unresolved_airframe:{design.airframe}")
            return out

        base = dict(self.db.resolve_stats(design.airframe))
        if "air_range" not in base:
            self.diag.warn("airframe_without_range", design.path,
                           f"airframe `{design.airframe}` has no air_range even after "
                           f"parent/archetype inheritance; treated as 0")
            out.flags.append("airframe_missing_air_range")
        out.airframe_resolved = True

        resources = dict(self.db.resolve_resources(design.airframe))
        adds: Dict[str, float] = {}
        mults: Dict[str, float] = {}
        # `add_average_stats` contributions: running sum and contributor count,
        # folded into `adds` as sum/count once every module has been seen.
        avg_sum: Dict[str, float] = {}
        avg_n: Dict[str, int] = {}

        def take(add_s: Dict[str, float], mul_s: Dict[str, float],
                 avg_s: Dict[str, float]) -> None:
            for k, v in add_s.items():
                adds[k] = adds.get(k, 0.0) + v
            for k, v in mul_s.items():
                mults[k] = mults.get(k, 0.0) + v
            for k, v in avg_s.items():
                avg_sum[k] = avg_sum.get(k, 0.0) + v
                avg_n[k] = avg_n.get(k, 0) + 1

        for slot, module_name in sorted(slot_map.items()):
            if not module_name or module_name.lower() in EMPTY_TOKENS:
                continue
            mod, kind = self.db.resolve_module_ref(module_name, design.country)
            if mod is None:
                self.diag.error("unresolved_module", design.path,
                                f"module `{module_name}` (slot `{slot}`) is neither a module "
                                f"nor a module category in any parsed module file")
                out.unresolved_modules.append(module_name)
                out.flags.append(f"unresolved_module:{module_name}")
                continue
            if kind == "category":
                self.diag.warn("category_slot", design.path,
                               f"slot `{slot}` names the module CATEGORY `{module_name}`; "
                               f"latest country-usable member `{mod.name}` assumed")
                out.flags.append(f"category_slot:{slot}={module_name}")
            out.modules[slot] = mod.name
            take(mod.add_stats, mod.multiply_stats, mod.avg_stats)
            if mission is not None:
                for ms in mod.mission_stats:
                    # An empty `limit` block means the entry is unconditional.
                    if ms.missions and mission not in ms.missions:
                        continue
                    take(ms.add_stats, ms.multiply_stats, ms.avg_stats)
            for r, v in mod.resources.items():
                resources[r] = resources.get(r, 0.0) + v

        for k, total in avg_sum.items():
            adds[k] = adds.get(k, 0.0) + total / avg_n[k]

        keys = set(base) | set(adds) | set(mults)
        stats: Dict[str, float] = {}
        for k in keys:
            b = base.get(k, 0.0)
            a = adds.get(k, 0.0)
            m = mults.get(k, 0.0)
            if self.multiply_base_only:
                stats[k] = b * (1.0 + m) + a
            else:
                stats[k] = (b + a) * (1.0 + m)

        # Thrust/weight agility bonus (NDefines.NAir.THRUST_WEIGHT_AGILITY_FACTOR)
        thrust = stats.get("thrust", 0.0)
        weight = stats.get("weight", 0.0)
        if self.twaf and thrust > weight:
            stats["air_agility"] = stats.get("air_agility", 0.0) + self.twaf * (thrust - weight)

        out.stats = stats
        out.resources = {r: max(0.0, v) for r, v in resources.items() if abs(v) > 1e-9}
        return out
