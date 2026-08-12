"""
Parsers for the two halves of the plane data model:

* `common/units/equipment/*plane*.txt`          -> airframes  (`equipments = {}`)
* `common/units/equipment/modules/*plane*.txt`  -> modules    (`equipment_modules = {}`)

Everything here is read-only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from .diagnostics import Diagnostics
from .pdx import Node, ParseError, parse_file

# Stat keys we care about. Anything else present in the data is still parsed
# and carried, this list only drives defaults / reporting order.
STAT_KEYS = (
    "air_range",
    "maximum_speed",
    "air_agility",
    "air_attack",
    "air_defence",
    "air_ground_attack",
    "air_bombing",
    "naval_strike_attack",
    "naval_strike_targetting",
    "surface_detection",
    "sub_detection",
    "reliability",
    "build_cost_ic",
    "weight",
    "thrust",
    "fuel_consumption",
)

# Blocks inside an equipment definition that are not stats.
_NON_STAT_KEYS = {
    "year", "is_archetype", "is_buildable", "is_convertable", "is_frame",
    "priority", "archetype", "parent", "type", "ai_type", "type_override",
    "upgrades", "can_be_produced", "can_be_lend_leased", "module_slots",
    "module_count_limit", "default_modules", "resources", "manpower",
    "picture", "sprite", "air_map_icon_frame", "interface_category",
    "interface_overview_category_index", "group_by", "max_military_factories",
    "substitute", "allowed_types", "allow_mission_type", "forbid_mission_type",
    "can_convert_from", "family", "visual_level", "derived_variant_name",
    "abbreviation", "lend_lease_cost", "one_use_only", "active",
    "carrier_capable", "hide_if_missing_tech", "only_targets",
}


@dataclass
class ModuleSlot:
    name: str
    required: bool = False
    allowed_categories: Set[str] = field(default_factory=set)


@dataclass
class Airframe:
    name: str
    source_file: str
    archetype: Optional[str] = None
    parent: Optional[str] = None
    is_archetype: bool = False
    year: Optional[int] = None
    own_stats: Dict[str, float] = field(default_factory=dict)
    own_resources: Dict[str, float] = field(default_factory=dict)
    own_slots: Dict[str, ModuleSlot] = field(default_factory=dict)
    slots_inherit: bool = False
    default_modules: Dict[str, str] = field(default_factory=dict)
    # module_count_limit entries: (match_kind, match_value, op, count)
    count_limits: List[tuple] = field(default_factory=list)


@dataclass
class MissionStats:
    """One `mission_type_stats = {}` block on a module.

    The stats apply only while the aircraft flies one of `missions`. An empty
    `missions` set means the block declared no `limit` and therefore always
    applies.
    """
    missions: Set[str] = field(default_factory=set)
    add_stats: Dict[str, float] = field(default_factory=dict)
    multiply_stats: Dict[str, float] = field(default_factory=dict)
    avg_stats: Dict[str, float] = field(default_factory=dict)


@dataclass
class EquipmentModule:
    name: str
    source_file: str
    category: Optional[str] = None
    gui_category: Optional[str] = None
    parent: Optional[str] = None
    add_stats: Dict[str, float] = field(default_factory=dict)
    multiply_stats: Dict[str, float] = field(default_factory=dict)
    # `add_average_stats`: contributions are AVERAGED over the modules that
    # declare the stat, not summed (two torpedo mounts at 10 give 10, not 20).
    avg_stats: Dict[str, float] = field(default_factory=dict)
    mission_stats: List[MissionStats] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=dict)
    xp_cost: float = 0.0


class EquipmentDB:
    """Airframes + modules, with archetype/parent inheritance resolution."""

    def __init__(self, diag: Diagnostics) -> None:
        self.diag = diag
        self.airframes: Dict[str, Airframe] = {}
        self.modules: Dict[str, EquipmentModule] = {}
        # module category -> ordered list of module names (file order)
        self.modules_by_category: Dict[str, List[str]] = {}
        self._stat_cache: Dict[str, Dict[str, float]] = {}
        self._res_cache: Dict[str, Dict[str, float]] = {}
        self._slot_cache: Dict[str, Dict[str, ModuleSlot]] = {}
        self._limit_cache: Dict[str, List[tuple]] = {}
        self.files_parsed: List[str] = []

    # ------------------------------------------------------------------ load
    def load_airframes(self, paths: List[Path]) -> None:
        for path in paths:
            try:
                root = parse_file(path)
            except ParseError as exc:
                self.diag.error("parse_failure", str(path), str(exc))
                continue
            self.files_parsed.append(str(path))
            equipments = root.get_block("equipments")
            if equipments is None:
                self.diag.warn("no_equipments_block", str(path),
                               "file has no top-level `equipments = {}` block; skipped")
                continue
            for name, body in equipments.named_blocks():
                if name in self.airframes:
                    self.diag.warn(
                        "duplicate_airframe", name,
                        f"redefined in {path.name} (previous: {self.airframes[name].source_file}); last wins")
                self.airframes[name] = self._read_airframe(name, body, path)

    def load_modules(self, paths: List[Path]) -> None:
        for path in paths:
            try:
                root = parse_file(path)
            except ParseError as exc:
                self.diag.error("parse_failure", str(path), str(exc))
                continue
            self.files_parsed.append(str(path))
            block = root.get_block("equipment_modules")
            if block is None:
                self.diag.warn("no_equipment_modules_block", str(path),
                               "file has no top-level `equipment_modules = {}` block; skipped")
                continue
            for name, body in block.named_blocks():
                if name == "limit":  # defensive: not a module
                    continue
                if name in self.modules:
                    self.diag.warn(
                        "duplicate_module", name,
                        f"redefined in {path.name} (previous: {self.modules[name].source_file}); last wins")
                mod = self._read_module(name, body, path)
                self.modules[name] = mod
                if mod.category:
                    self.modules_by_category.setdefault(mod.category, []).append(name)

    # --------------------------------------------------------------- readers
    def _read_airframe(self, name: str, body: Node, path: Path) -> Airframe:
        af = Airframe(name=name, source_file=path.name)
        af.archetype = body.get_str("archetype")
        af.parent = body.get_str("parent")
        af.is_archetype = body.get_bool("is_archetype", False)
        year = body.get_float("year")
        af.year = int(year) if year is not None else None

        for key, _op, value in body.items():
            if key is None or isinstance(value, Node):
                continue
            if key in _NON_STAT_KEYS:
                continue
            try:
                af.own_stats[key] = float(value)
            except ValueError:
                continue  # non-numeric flavour field, ignore

        res = body.get_block("resources")
        if res is not None:
            af.own_resources = res.float_map()

        slots = body.get("module_slots")
        if isinstance(slots, str) and slots == "inherit":
            af.slots_inherit = True
        elif isinstance(slots, Node):
            af.own_slots = self._read_slots(slots, name)

        defaults = body.get_block("default_modules")
        if defaults is not None:
            af.default_modules = defaults.scalar_map()

        for _k, _op, limit in body.all("module_count_limit"):
            if not isinstance(limit, Node):
                continue
            match_kind = match_value = None
            for k, _o, v in limit.items():
                if k in ("module", "category") and isinstance(v, str):
                    match_kind, match_value = k, v
            for k, o, v in limit.items():
                if k == "count" and isinstance(v, str):
                    af.count_limits.append((match_kind, match_value, o, v))
        return af

    def _read_slots(self, node: Node, owner: str) -> Dict[str, ModuleSlot]:
        slots: Dict[str, ModuleSlot] = {}
        for key, _op, value in node.items():
            if key is None:
                continue
            if isinstance(value, str):
                # `<slot> = inherit` or `<slot> = <earlier slot>`
                if value == "inherit":
                    slots[key] = ModuleSlot(name=key, required=False)
                    slots[key].allowed_categories = set()
                    slots[key].__dict__["_inherit"] = True
                elif value in slots:
                    src = slots[value]
                    slots[key] = ModuleSlot(key, src.required, set(src.allowed_categories))
                else:
                    slots[key] = ModuleSlot(name=key)
                    self.diag.info("slot_alias_unresolved", owner,
                                   f"slot `{key}` aliases `{value}` which is not defined earlier")
                continue
            cats = value.get_block("allowed_module_categories")
            slots[key] = ModuleSlot(
                name=key,
                required=value.get_bool("required", False),
                allowed_categories=set(cats.scalars()) if cats is not None else set(),
            )
        return slots

    def _read_module(self, name: str, body: Node, path: Path) -> EquipmentModule:
        mod = EquipmentModule(name=name, source_file=path.name)
        mod.category = body.get_str("category")
        mod.gui_category = body.get_str("gui_category")
        mod.parent = body.get_str("parent")
        mod.xp_cost = body.get_float("xp_cost", 0.0) or 0.0
        add = body.get_block("add_stats")
        if add is not None:
            mod.add_stats = add.float_map()
        mul = body.get_block("multiply_stats")
        if mul is not None:
            mod.multiply_stats = mul.float_map()
        avg = body.get_block("add_average_stats")
        if avg is not None:
            mod.avg_stats = avg.float_map()
        res = body.get_block("build_cost_resources")
        if res is not None:
            mod.resources = res.float_map()

        # Mission-conditional stats. 683 blocks across the mod's plane modules
        # carry the stats that actually differentiate designs in their role:
        # `surface_detection`/`sub_detection` on the air-ground radars,
        # `naval_strike_targetting` on every torpedo mount, the `interception`
        # `air_attack` grants, and the ordnance agility penalties. Ignoring
        # them made whole roles unscoreable - see README "Mission-conditional
        # stats".
        for _k, _op, mts in body.all("mission_type_stats"):
            if not isinstance(mts, Node):
                continue
            limit = mts.get_block("limit")
            add_b = mts.get_block("add_stats")
            mul_b = mts.get_block("multiply_stats")
            avg_b = mts.get_block("add_average_stats")
            mod.mission_stats.append(MissionStats(
                missions=set(limit.scalars()) if limit is not None else set(),
                add_stats=add_b.float_map() if add_b is not None else {},
                multiply_stats=mul_b.float_map() if mul_b is not None else {},
                avg_stats=avg_b.float_map() if avg_b is not None else {},
            ))
        return mod

    # ---------------------------------------------------------- inheritance
    def _chain(self, name: str) -> List[Airframe]:
        """Resolution order: self, parent chain, archetype chain (breadth-ish).

        HOI4 inherits undeclared fields from `archetype`; the mod's airframe
        lines additionally use `parent` for model-to-model lineage. We consult
        `parent` before `archetype` because a variant's immediate predecessor
        is the more specific source. Documented as an approximation in README.
        """
        out: List[Airframe] = []
        seen: Set[str] = set()
        queue = [name]
        while queue:
            cur = queue.pop(0)
            if cur in seen:
                continue
            seen.add(cur)
            af = self.airframes.get(cur)
            if af is None:
                continue
            out.append(af)
            if af.parent:
                queue.append(af.parent)
            if af.archetype:
                queue.append(af.archetype)
        return out

    def resolve_stats(self, name: str) -> Dict[str, float]:
        if name in self._stat_cache:
            return self._stat_cache[name]
        merged: Dict[str, float] = {}
        for af in self._chain(name):
            for k, v in af.own_stats.items():
                merged.setdefault(k, v)
        self._stat_cache[name] = merged
        return merged

    def resolve_resources(self, name: str) -> Dict[str, float]:
        if name in self._res_cache:
            return self._res_cache[name]
        for af in self._chain(name):
            if af.own_resources:
                self._res_cache[name] = dict(af.own_resources)
                return self._res_cache[name]
        self._res_cache[name] = {}
        return self._res_cache[name]

    def resolve_slots(self, name: str) -> Dict[str, ModuleSlot]:
        if name in self._slot_cache:
            return self._slot_cache[name]
        merged: Dict[str, ModuleSlot] = {}
        for af in reversed(self._chain(name)):
            for slot_name, slot in af.own_slots.items():
                if slot.__dict__.get("_inherit") and slot_name in merged:
                    continue
                merged[slot_name] = slot
        self._slot_cache[name] = merged
        return merged

    def resolve_default_modules(self, name: str) -> Dict[str, str]:
        """`default_modules` for an airframe, inheriting slots it does not override."""
        merged: Dict[str, str] = {}
        for af in reversed(self._chain(name)):
            merged.update(af.default_modules)
        return merged

    def resolve_count_limits(self, name: str) -> List[tuple]:
        """`module_count_limit` entries, NEAREST DECLARATION WINS per target.

        A concrete airframe lifts or tightens an archetype cap by re-declaring
        it for the same `(module|category, value)` target - the mod's own
        `SOV_la_5_airframe` declares
        `module_count_limit = { module = self_sealing_fuel_tanks_large count = any }`
        precisely to lift the `count < 1` its `small_fighter_multirole_airframe`
        archetype imposes, and the Fix 47 annotation in `SOV_planes.txt` states
        that reading explicitly. A `count = any` declaration is meaningless
        under any other semantics.

        This therefore overrides rather than accumulates, matching
        `resolve_stats` (setdefault), `resolve_resources` (first wins) and
        `resolve_slots` (nearest wins). `_chain` is nearest-first, so the first
        declaration seen for a target is the one that applies.
        """
        if name in self._limit_cache:
            return self._limit_cache[name]
        out: List[tuple] = []
        seen: Set[tuple] = set()
        for af in self._chain(name):
            for (match_kind, match_value, op, count) in af.count_limits:
                target = (match_kind, match_value)
                if target in seen:
                    continue
                seen.add(target)
                out.append((match_kind, match_value, op, count))
        self._limit_cache[name] = out
        return out

    @staticmethod
    def _cap_of(op: str, count: str) -> Optional[float]:
        """Maximum permitted occurrences, or None when the entry sets no cap.

        `count < N` caps at N-1; `count = any` (and any non-numeric count)
        removes the cap. `count > N` is a minimum, not a cap.
        """
        if op != "<":
            return None
        try:
            return float(count) - 1.0
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------- module lookup
    @staticmethod
    def _tag_prefix(module_name: str) -> Optional[str]:
        """`ENG_cannon_...` -> 'ENG'; generic modules -> None."""
        if len(module_name) > 4 and module_name[3] == "_" and module_name[:3].isupper():
            return module_name[:3]
        return None

    def resolve_module_ref(self, ref: str, country: Optional[str] = None):
        """Resolve a slot value to a concrete module.

        A `target_variant` slot may name either a module or a *module category*
        (see `common/ai_equipment/_documentation.info`: "A slot can be assigned
        a module category ... the latest available will be favored"). For a
        category we take the last member in file order that is either generic
        or prefixed with this country's tag - the closest offline stand-in for
        "latest available to this country".

        Returns `(EquipmentModule | None, kind)` where kind is one of
        'module', 'category', 'missing'.
        """
        mod = self.modules.get(ref)
        if mod is not None:
            return mod, "module"
        members = self.modules_by_category.get(ref)
        if members:
            usable = [m for m in members
                      if self._tag_prefix(m) in (None, country)]
            pick = (usable or members)[-1]
            return self.modules.get(pick), "category"
        return None, "missing"

    def forbidden_modules(self, airframe: str) -> Set[str]:
        """Modules this airframe cannot mount at all (effective cap of 0)."""
        banned: Set[str] = set()
        for kind, value, op, count in self.resolve_count_limits(airframe):
            if kind != "module":
                continue
            cap = self._cap_of(op, count)
            if cap is not None and cap < 1.0:
                banned.add(value)
        return banned

    def forbidden_categories(self, airframe: str) -> Set[str]:
        """Module categories this airframe cannot mount at all."""
        banned: Set[str] = set()
        for kind, value, op, count in self.resolve_count_limits(airframe):
            if kind != "category":
                continue
            cap = self._cap_of(op, count)
            if cap is not None and cap < 1.0:
                banned.add(value)
        return banned

    def count_limit_violations(self, airframe: str,
                               slot_map: Dict[str, str]) -> List[str]:
        """Which `module_count_limit` caps a slot->module map would exceed.

        Used to stop the redesign search proposing a loadout the designer
        cannot actually build. Values are human-readable, e.g.
        `self_sealing_fuel_tanks_large x2 > cap 0`.
        """
        counts: Dict[tuple, int] = {}
        for module_name in slot_map.values():
            if not module_name or module_name.lower() in ("empty", "none"):
                continue
            mod = self.modules.get(module_name)
            if mod is None:
                continue
            counts[("module", mod.name)] = counts.get(("module", mod.name), 0) + 1
            if mod.category:
                key = ("category", mod.category)
                counts[key] = counts.get(key, 0) + 1
        out: List[str] = []
        for kind, value, op, count in self.resolve_count_limits(airframe):
            cap = self._cap_of(op, count)
            if cap is None:
                continue
            have = counts.get((kind, value), 0)
            if have > cap:
                out.append(f"{value} x{have} > cap {cap:g}")
        return out


def find_files(root: Path, patterns: List[str]) -> List[Path]:
    """Glob `patterns` under `root`, de-duplicated and sorted by name."""
    seen: Dict[str, Path] = {}
    for pattern in patterns:
        for p in sorted(root.glob(pattern)):
            if p.is_file():
                seen[p.name] = p
    return [seen[k] for k in sorted(seen)]
