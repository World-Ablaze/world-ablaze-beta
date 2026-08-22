"""Cross-domain production-efficiency retention audit.

Covers aircraft and tank designer groups plus technology-unlocked infantry,
artillery and vehicles.  It is intentionally independent from combat scoring:
its job is to answer the prior question "will switching this mature line throw
away too much output?" for every supported domain.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from .config import Config
from .diagnostics import Diagnostics
from .infantry import InfantryDB
from .parse_ai_equipment import discover_countries, parse_country_file
from .pdx import Node, parse_file
from .production_efficiency import classify_relation
from .technology_graph import TechnologyGraph


@dataclass
class EfficiencyTransition:
    domain: str
    country: str
    source: str
    group: str
    old: str
    new: str
    old_base: str
    new_base: str
    relation: str
    retention: float
    policy: str


def _policy(retention: float, cfg: Config) -> str:
    return ("SWITCH_SAFE" if retention >= cfg.efficiency_model.full_switch_min_retention
            else "LOW_RETENTION_REVIEW")


def _tech_edges(path: Path, db: InfantryDB, allowed: Set[str]) -> List[tuple]:
    root = parse_file(path)
    techs = root.get_block("technologies")
    if techs is None:
        return []
    enabled: Dict[str, List[str]] = {}
    reverse: Dict[str, Set[str]] = {}
    for tech_name, tech in techs.named_blocks():
        block = tech.get_block("enable_equipments")
        enabled[tech_name] = [n for n in block.scalars()
                              if n in db.items and db.items[n].archetype in allowed] if block else []
        for _, _, value in tech.all("path"):
            if isinstance(value, Node):
                target = value.get_str("leads_to_tech")
                if target:
                    reverse.setdefault(target, set()).add(tech_name)
    result: List[tuple] = []
    seen: Set[tuple] = set()
    for target, new_names in enabled.items():
        if not new_names:
            continue
        frontier = sorted(reverse.get(target, set()))
        visited: Set[str] = set()
        predecessors: Set[str] = set()
        while frontier and not predecessors:
            nxt: List[str] = []
            for tech in frontier:
                if tech in visited:
                    continue
                visited.add(tech)
                if enabled.get(tech):
                    predecessors.update(enabled[tech])
                else:
                    nxt.extend(sorted(reverse.get(tech, set())))
            frontier = sorted(nxt)
        for old in sorted(predecessors):
            for new in new_names:
                # A tech path often branches from artillery into AT/AA or from
                # a troop carrier into a specialised mechanized variant. Those
                # are parallel production roles, not replacement line switches.
                if db.items[old].archetype != db.items[new].archetype:
                    continue
                if (old, new) not in seen:
                    seen.add((old, new))
                    result.append((db.items[old], db.items[new]))
    return result


def _relation(db: InfantryDB, old: str, new: str, cfg: Config) -> tuple:
    a, b = db.items.get(old), db.items.get(new)
    if not a or not b:
        return "unresolved", cfg.efficiency_model.unrelated
    relation = classify_relation(
        old, new, old_archetype=a.archetype, new_archetype=b.archetype,
        old_family=a.family, new_family=b.family, is_ancestor=db.is_ancestor)
    return relation, cfg.efficiency_model.factor(relation)


def _tech_domain(mod_root: Path, cfg: Config, domain: str,
                 equipment_globs: Iterable[str], tech_globs: Iterable[str],
                 allowed_archetypes: Set[str], countries: Optional[Set[str]]) -> List[EfficiencyTransition]:
    eq_dir = mod_root / "common/units/equipment"
    paths = sorted({p for pattern in equipment_globs for p in eq_dir.glob(pattern) if p.stat().st_size})
    db = InfantryDB(paths)
    out: List[EfficiencyTransition] = []
    tech_dir = mod_root / "common/technologies"
    for pattern in tech_globs:
        for path in sorted(tech_dir.glob(pattern)):
            stem = path.stem
            tag = stem.split("_", 1)[1].upper() if "_" in stem else "GENERIC"
            if tag.startswith("NON_"):
                continue
            if countries and tag not in countries:
                continue
            for old, new in _tech_edges(path, db, allowed_archetypes):
                relation, retention = _relation(db, old.name, new.name, cfg)
                out.append(EfficiencyTransition(
                    domain, tag, path.name, old.archetype or "", old.name, new.name,
                    old.name, new.name, relation, retention, _policy(retention, cfg)))
    return out


def _designer_domain(mod_root: Path, cfg: Config, domain: str, suffix: str,
                     category: str, equipment_globs: Iterable[str],
                     countries: Optional[Set[str]]) -> List[EfficiencyTransition]:
    eq_dir = mod_root / "common/units/equipment"
    paths = sorted({p for pattern in equipment_globs for p in eq_dir.glob(pattern) if p.stat().st_size})
    db = InfantryDB(paths)
    ai_dir = mod_root / "common/ai_equipment"
    diag = Diagnostics()
    tech_graph = TechnologyGraph(mod_root, diag)
    available = discover_countries(ai_dir, suffix)
    selected = [c for c in available if not countries or c in countries]
    out: List[EfficiencyTransition] = []
    for tag in selected:
        path = ai_dir / f"{tag}_{suffix}.txt"
        groups = parse_country_file(path, tag, diag, category_filter=category)
        stop_techs = {
            tech for candidate_group in groups
            for design in candidate_group.designs for tech in design.enable_techs
        }
        for group in groups:
            designs = [d for d in group.designs if d.airframe]
            by_name = {design.name: design for design in designs}
            graph = tech_graph.design_graph(group, stop_techs)
            group.technology_edges = list(graph.edges)
            for old_name, new_name in graph.edges:
                old, new = by_name[old_name], by_name[new_name]
                relation, retention = _relation(db, old.airframe, new.airframe, cfg)
                out.append(EfficiencyTransition(
                    domain, tag, path.name, group.name, old.name, new.name,
                    old.airframe or "", new.airframe or "", relation, retention,
                    _policy(retention, cfg)))
    return out


def evaluate_efficiency_domains(mod_root: Path, cfg: Config,
                                domains: Set[str], countries: Optional[Set[str]] = None) -> List[EfficiencyTransition]:
    rows: List[EfficiencyTransition] = []
    if "air" in domains:
        rows += _designer_domain(mod_root, cfg, "air", "planes", "air",
                                 ("*plane*.txt",), countries)
    if "tanks" in domains:
        rows += _designer_domain(mod_root, cfg, "tanks", "tank", "land",
                                 ("tank_chassis.txt", "x_tank_chassis.txt"), countries)
    if "infantry" in domains:
        rows += _tech_domain(mod_root, cfg, "infantry", ("infantry.txt",),
                             ("infantry_*.txt",), {"infantry_equipment", "heavy_infantry_equipment"}, countries)
    if "artillery" in domains:
        artillery_archetypes = {
            "artillery_equipment", "heavy_artillery_equipment", "pack_artillery_equipment",
            "rocket_artillery_equipment", "anti_tank_equipment", "heavy_anti_tank_equipment",
            "anti_air_equipment", "heavy_anti_air_equipment",
        }
        rows += _tech_domain(mod_root, cfg, "artillery",
                             ("*artillery_GENERATED.txt", "*anti_tank_GENERATED.txt", "*anti_air_GENERATED.txt"),
                             ("artillery*.txt",), artillery_archetypes, countries)
    if "vehicles" in domains:
        vehicle_archetypes = {
            "motorized_equipment", "mechanized_equipment", "mechanized_td_equipment",
            "mechanized_artillery_equipment", "mechanized_aa_equipment",
            "amphibious_mechanized_equipment",
        }
        rows += _tech_domain(mod_root, cfg, "vehicles", ("motorized.txt", "mechanized.txt"),
                             ("armor*.txt",), vehicle_archetypes, countries)
    return rows


def write_efficiency_audit(out_dir: Path, rows: List[EfficiencyTransition], cfg: Config) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "production_efficiency_transitions.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(("domain", "country", "source", "group", "from_design", "to_design",
                    "from_base", "to_base", "relation", "retention", "efficiency_shock", "policy"))
        for r in rows:
            w.writerow((r.domain, r.country, r.source, r.group, r.old, r.new,
                        r.old_base, r.new_base, r.relation, f"{r.retention:.3f}",
                        f"{1-r.retention:.3f}", r.policy))
    counts: Dict[tuple, int] = {}
    for r in rows:
        counts[(r.domain, r.policy)] = counts.get((r.domain, r.policy), 0) + 1
    md = ["# Production-efficiency transition audit", "",
          f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}; report-only._", "",
          "`LOW_RETENTION_REVIEW` flags a transition below the safe-retention threshold. It does not imply that the AI can split established and new production lines.", "",
          "| domain | policy | count |", "| --- | --- | ---: |"]
    md += [f"| {d} | {p} | {n} |" for (d, p), n in sorted(counts.items())]
    md += ["", "## Transitions requiring line preservation", "",
           "| domain | country | transition | bases | relation | retained |",
           "| --- | --- | --- | --- | --- | ---: |"]
    for r in rows:
        if r.policy == "LOW_RETENTION_REVIEW":
            md.append(f"| {r.domain} | {r.country} | `{r.old}` → `{r.new}` | "
                      f"`{r.old_base}` → `{r.new_base}` | {r.relation} | {r.retention:.0%} |")
    md += ["", "The threshold and all retention factors are configurable in `config.json` under `production_efficiency`.", ""]
    (out_dir / "production_efficiency_report.md").write_text("\n".join(md), encoding="utf-8")
