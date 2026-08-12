"""Infantry-equipment transition evaluator with production-efficiency policy.

Technology file order supplies each country's real unlock chain.  Equipment
stats and parent/family/archetype relationships come from infantry.txt.  The
tool remains report-only: it does not edit technologies or production rules.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from .config import Config
from .decision_policy import (decide_adoption, numeric_delta,
                              significant_increases)
from .pdx import Node, parse_file
from .production_efficiency import EfficiencyModel, classify_relation


INFANTRY_STATS = ("soft_attack", "hard_attack", "breakthrough", "defense",
                  "ap_attack", "reliability", "build_cost_ic")


@dataclass
class LandEquipment:
    name: str
    body: Node
    year: float = 0.0
    archetype: Optional[str] = None
    parent: Optional[str] = None
    family: Optional[str] = None
    is_archetype: bool = False
    stats: Dict[str, float] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=dict)
    can_convert_from: Set[str] = field(default_factory=set)


class InfantryDB:
    def __init__(self, path) -> None:
        self.items: Dict[str, LandEquipment] = {}
        paths = [path] if isinstance(path, Path) else list(path)
        for source in paths:
            root = parse_file(source)
            equipment = root.get_block("equipments")
            if equipment is None:
                continue
            for name, body in equipment.named_blocks():
                item = LandEquipment(
                    name=name,
                    body=body,
                    year=body.get_float("year", 0.0) or 0.0,
                    archetype=body.get_str("archetype"),
                    parent=body.get_str("parent"),
                    family=body.get_str("family"),
                    is_archetype=body.get_bool("is_archetype", False),
                )
                conv = body.get_block("can_convert_from")
                if conv:
                    item.can_convert_from = set(conv.scalars())
                self.items[name] = item
        for item in self.items.values():
            # Clausewitz/PDX identifiers are case-insensitive. Generated land
            # equipment routinely defines `cze_art_1` but references it as
            # `CZE_art_1`; canonicalise links before walking inheritance.
            item.parent = self.canonical_name(item.parent)
            item.archetype = self.canonical_name(item.archetype)
            item.family = self.canonical_name(item.family) if item.family else None
            item.can_convert_from = {
                self.canonical_name(name) or name for name in item.can_convert_from
            }
        for item in self.items.values():
            item.stats = {s: self.resolve_float(item.name, s) for s in INFANTRY_STATS}
            item.resources = self.resolve_resources(item.name)

    def canonical_name(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return name
        if name in self.items:
            return name
        lower = name.lower()
        return next((key for key in self.items if key.lower() == lower), name)

    def lineage(self, name: str) -> Iterable[str]:
        seen: Set[str] = set()
        cur = self.items.get(name)
        while cur and cur.parent and cur.parent not in seen:
            seen.add(cur.parent)
            yield cur.parent
            cur = self.items.get(cur.parent)

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        return ancestor in set(self.lineage(descendant))

    def _inheritance(self, name: str) -> Iterable[LandEquipment]:
        seen: Set[str] = set()
        queue = [name]
        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            item = self.items.get(current)
            if not item:
                continue
            yield item
            if item.parent:
                queue.append(item.parent)
            if item.archetype:
                queue.append(item.archetype)

    def resolve_float(self, name: str, stat: str) -> float:
        for item in self._inheritance(name):
            value = item.body.get_float(stat)
            if value is not None:
                return value
        return 0.0

    def resolve_resources(self, name: str) -> Dict[str, float]:
        for item in self._inheritance(name):
            block = item.body.get_block("resources")
            if block is not None:
                return block.float_map()
        return {}


@dataclass
class InfantryTransition:
    country: str
    technology_file: str
    old: LandEquipment
    new: LandEquipment
    relation: str
    retention: float
    efficiency_shock: float
    combat_gain: float
    adjusted_gain: float
    verdict: str
    stock_conversion: bool
    resource_delta: Dict[str, float]
    notes: List[str] = field(default_factory=list)


def _gain(old: LandEquipment, new: LandEquipment, cfg: Config) -> float:
    weights = cfg.infantry_weights
    floors = cfg.raw.get("stat_relative_floors", {})
    total = 0.0
    denom = sum(abs(float(v)) for v in weights.values()) or 1.0
    for stat, weight in weights.items():
        o = old.stats.get(stat, 0.0)
        n = new.stats.get(stat, 0.0)
        floor = float(floors.get(stat, floors.get("default", 1.0)))
        total += float(weight) * (n - o) / max(abs(o), floor)
    return total / denom


def _enabled_equipment(path: Path) -> List[str]:
    root = parse_file(path)
    techs = root.get_block("technologies")
    if techs is None:
        return []
    result: List[str] = []
    for _, tech in techs.named_blocks():
        enabled = tech.get_block("enable_equipments")
        if enabled:
            result.extend(enabled.scalars())
    return result


def _technology_pairs(path: Path, db: InfantryDB) -> List[tuple]:
    """Return real supersession edges from the technology graph.

    File order is not a tech chain: SOV contains two parallel rifle branches.
    Walk reverse ``path/leads_to_tech`` edges until the nearest predecessor
    technology that actually enables infantry equipment is reached.
    """
    root = parse_file(path)
    techs = root.get_block("technologies")
    if techs is None:
        return []
    enabled_by_tech: Dict[str, List[str]] = {}
    reverse: Dict[str, Set[str]] = {}
    for tech_name, tech in techs.named_blocks():
        enabled = tech.get_block("enable_equipments")
        names = []
        if enabled:
            names = [n for n in enabled.scalars()
                     if n in db.items and db.items[n].archetype == "infantry_equipment"]
        enabled_by_tech[tech_name] = names
        for _, _, value in tech.all("path"):
            if isinstance(value, Node):
                target = value.get_str("leads_to_tech")
                if target:
                    reverse.setdefault(target, set()).add(tech_name)

    result: List[tuple] = []
    seen_pairs: Set[tuple] = set()
    for target_tech, new_names in enabled_by_tech.items():
        if not new_names:
            continue
        frontier = sorted(reverse.get(target_tech, set()))
        visited: Set[str] = set()
        predecessor_names: Set[str] = set()
        while frontier and not predecessor_names:
            next_frontier: List[str] = []
            for tech_name in frontier:
                if tech_name in visited:
                    continue
                visited.add(tech_name)
                if enabled_by_tech.get(tech_name):
                    predecessor_names.update(enabled_by_tech[tech_name])
                else:
                    next_frontier.extend(sorted(reverse.get(tech_name, set())))
            frontier = sorted(next_frontier)
        for old_name in sorted(predecessor_names):
            for new_name in new_names:
                pair = (old_name, new_name)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    result.append((db.items[old_name], db.items[new_name]))
    return result


def evaluate_infantry(mod_root: Path, cfg: Config,
                      countries: Optional[Set[str]] = None) -> List[InfantryTransition]:
    db = InfantryDB(mod_root / "common/units/equipment/infantry.txt")
    model = cfg.efficiency_model
    out: List[InfantryTransition] = []
    tech_dir = mod_root / "common/technologies"
    for path in sorted(tech_dir.glob("infantry_*.txt")):
        tag = path.stem.removeprefix("infantry_").upper()
        if countries and tag not in countries:
            continue
        for old, new in _technology_pairs(path, db):
            relation = classify_relation(
                old.name, new.name,
                old_archetype=old.archetype, new_archetype=new.archetype,
                old_family=old.family, new_family=new.family,
                is_ancestor=db.is_ancestor,
            )
            retention = model.factor(relation)
            gain = _gain(old, new, cfg)
            adjusted = model.adjusted_gain(gain, retention)
            res_delta = numeric_delta(old.resources, new.resources)
            significant = significant_increases(res_delta, cfg.resource_threshold)
            notes: List[str] = []
            verdict = decide_adoption(
                adjusted_gain=adjusted, retention=retention,
                significant_resources=significant, blockers=(), model=model)
            if gain <= 0:
                notes.append("new equipment is not a net stat/cost improvement")
            elif (retention < model.full_switch_min_retention
                  and adjusted < model.low_retention_min_gain):
                notes.append("low-retention switch does not clear the stronger gain threshold")
            elif adjusted <= 0.0:
                notes.append("new equipment does not improve the efficiency-adjusted score")
            elif significant:
                notes.append("switch only when the economy can absorb the resource increase")
            out.append(InfantryTransition(
                country=tag, technology_file=path.name, old=old, new=new,
                relation=relation, retention=retention,
                efficiency_shock=1.0 - retention, combat_gain=gain,
                adjusted_gain=adjusted, verdict=verdict,
                stock_conversion=old.name in new.can_convert_from,
                resource_delta=res_delta, notes=notes,
            ))
    return out


def write_infantry_reports(out_dir: Path, rows: List[InfantryTransition], cfg: Config) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "infantry_equipment_transitions.csv"
    fields = ["country", "technology_file", "from_equipment", "to_equipment",
              "from_year", "to_year", "relation", "efficiency_retention",
              "efficiency_shock", "combat_gain", "efficiency_adjusted_gain",
              "stock_conversion", "verdict", "ic_old", "ic_new",
              "resource_delta", "notes"]
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(fields)
        for t in rows:
            writer.writerow([
                t.country, t.technology_file, t.old.name, t.new.name,
                t.old.year, t.new.year, t.relation, f"{t.retention:.3f}",
                f"{t.efficiency_shock:.3f}", f"{t.combat_gain:.4f}",
                f"{t.adjusted_gain:.4f}", "yes" if t.stock_conversion else "no",
                t.verdict, t.old.stats.get("build_cost_ic", 0.0),
                t.new.stats.get("build_cost_ic", 0.0),
                ";".join(f"{k}={v:+g}" for k, v in t.resource_delta.items() if v),
                " | ".join(t.notes),
            ])

    counts: Dict[str, int] = {}
    for t in rows:
        counts[t.verdict] = counts.get(t.verdict, 0) + 1
    md = ["# WA infantry equipment transition report", "",
          f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}; report-only._", "",
          "Retention of 90% or more is treated as operationally free. Low-retention transitions must clear the configured strong-gain threshold; the evaluator does not attempt to split old and new production lines.", "",
          "| verdict | count |", "| --- | --- |"]
    md += [f"| {k} | {v} |" for k, v in sorted(counts.items())]
    md += ["", "## Transitions", "",
           "| country | transition | relation | retained | raw gain | adjusted | verdict | stock conversion |",
           "| --- | --- | --- | ---: | ---: | ---: | --- | --- |"]
    for t in rows:
        md.append(f"| {t.country} | `{t.old.name}` → `{t.new.name}` | {t.relation} | "
                  f"{t.retention:.0%} | {t.combat_gain:+.3f} | {t.adjusted_gain:+.3f} | "
                  f"{t.verdict} | {'yes' if t.stock_conversion else 'no'} |")
    md += ["", "## Policy", "",
           f"- Retention at or above {cfg.efficiency_model.penalty_free_retention:.0%} carries no score penalty.",
           f"- Below that level, a full switch requires at least {cfg.efficiency_model.low_retention_min_gain:.0%} adjusted gain; otherwise keep the old equipment.",
           "- Parent/child and variants retain 95%; same family 90%; same archetype 75%; unrelated equipment starts at 10%.",
           "- `can_convert_from` is reported separately because stockpile conversion is not production-line efficiency retention.",
           "- This is an offline recommendation. Runtime stockpile, deficit and factory allocation gates remain a later gameplay integration step.", ""]
    (out_dir / "infantry_equipment_report.md").write_text("\n".join(md), encoding="utf-8")
