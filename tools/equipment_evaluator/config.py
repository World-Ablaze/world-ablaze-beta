"""
Config loading for the equipment evaluator.

JSON, because the rest of `tools/` is stdlib-only (no PyYAML anywhere in the
repo) and JSON needs no dependency. Keys beginning with `_` are documentation
and are ignored by the loader.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .production_efficiency import EfficiencyModel

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def _strip_comments(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_comments(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_strip_comments(v) for v in obj]
    return obj


@dataclass
class Config:
    raw: Dict[str, Any] = field(default_factory=dict)
    path: Path = DEFAULT_CONFIG_PATH

    # -- stat model -------------------------------------------------------
    @property
    def multiply_base_only(self) -> bool:
        return bool(self.raw.get("stat_model", {}).get("multiply_base_only", False))

    @property
    def thrust_weight_agility_factor(self) -> float:
        return float(self.raw.get("stat_model", {}).get("thrust_weight_agility_factor", 1.0))

    # -- gates ------------------------------------------------------------
    def range_target(self, role: str) -> float:
        targets = self.raw.get("range_targets", {})
        return float(targets.get(role, targets.get("default", 1000)))

    def role_weights(self, role: str) -> Dict[str, float]:
        weights = self.raw.get("role_weights", {})
        return dict(weights.get(role, weights.get("default", {})))

    def role_mission(self, role: str) -> str:
        """Primary HOI4 air mission this role is scored as flying.

        Selects which `mission_type_stats` blocks apply - see `stats.py`.
        """
        missions = self.raw.get("role_missions", {})
        return str(missions.get(role, missions.get("default", "air_superiority")))

    def stat_floor(self, stat: str) -> float:
        floors = self.raw.get("stat_relative_floors", {})
        return float(floors.get(stat, floors.get("default", 1.0)))

    @property
    def min_net_gain(self) -> float:
        return float(self.raw.get("switch", {}).get("min_net_gain", 0.05))

    @property
    def range_override_gain(self) -> float:
        return float(self.raw.get("switch", {}).get("range_override_gain", self.min_net_gain))

    @property
    def redesign_min_gain(self) -> float:
        return float(self.raw.get("switch", {}).get("redesign_min_gain", 0.0))

    @property
    def max_redesign_sacrifice(self) -> float:
        return float(self.raw.get("switch", {}).get("max_redesign_sacrifice", 0.25))

    @property
    def range_recovery_max_sacrifice(self) -> float:
        return float(self.raw.get("switch", {}).get(
            "range_recovery_max_sacrifice", self.max_redesign_sacrifice))

    def resource_threshold(self, resource: str) -> float:
        thresholds = self.raw.get("resource_significance", {})
        return float(thresholds.get(resource, thresholds.get("default", 1.0)))

    @property
    def runtime_resource_gates(self) -> set[str]:
        """Resources for which generated PDXScript has a live economy gate."""
        return set(self.raw.get("runtime_resource_gates",
                                ["steel", "aluminium", "chromium", "tungsten"]))

    @property
    def frontier_priority_ladder(self) -> List[float]:
        """Descending factors relative to a frontier's historical maximum.

        Rank alone selects a rung: combat-score magnitudes never leak into the
        engine priority.  The geometric spacing keeps the best available rank
        dominant under both max-choice and weighted-choice interpretations.
        """
        return [float(value) for value in self.raw.get(
            "frontier_priority", {}).get(
                "relative_ladder",
                [1.0, 0.3, 0.1, 0.03, 0.01, 0.003, 0.001, 0.0003, 0.0001])]

    # -- production efficiency / infantry -------------------------------
    @property
    def efficiency_model(self) -> EfficiencyModel:
        p = self.raw.get("production_efficiency", {})
        return EfficiencyModel(
            variant=float(p.get("variant_retention", 0.95)),
            parent=float(p.get("parent_retention", 0.95)),
            family=float(p.get("family_retention", 0.90)),
            archetype=float(p.get("archetype_retention", 0.75)),
            unrelated=float(p.get("unrelated_retention", 0.10)),
            full_switch_min_retention=float(p.get("full_switch_min_retention", 0.90)),
            efficiency_penalty_weight=float(p.get("efficiency_penalty_weight", 0.50)),
            penalty_free_retention=float(p.get("penalty_free_retention", 0.90)),
            low_retention_min_gain=float(p.get("low_retention_min_gain", 0.10)),
        )

    @property
    def infantry_weights(self) -> Dict[str, float]:
        return dict(self.raw.get("infantry", {}).get("weights", {
            "soft_attack": 0.30, "hard_attack": 0.05, "breakthrough": 0.15,
            "defense": 0.25, "ap_attack": 0.05, "reliability": 0.10,
            "build_cost_ic": -0.10,
        }))

    @property
    def infantry_min_adjusted_gain(self) -> float:
        return float(self.raw.get("infantry", {}).get("min_adjusted_gain", 0.02))

    @property
    def ground_min_gain(self) -> float:
        return float(self.raw.get("ground", {}).get("min_adjusted_gain", 0.02))

    def ground_weights(self, domain: str, role: str) -> Dict[str, float]:
        section = self.raw.get("ground", {}).get(domain, {}).get("weights", {})
        return dict(section.get(role, section.get("default", {})))

    def ground_thresholds(self, domain: str, role: str) -> Dict[str, float]:
        section = self.raw.get("ground", {}).get(domain, {}).get("thresholds", {})
        merged = dict(section.get("default", {}))
        merged.update(section.get(role, {}))
        return {k: float(v) for k, v in merged.items()}

    @property
    def tank_max_candidates_per_slot(self) -> int:
        return int(self.raw.get("ground", {}).get("tanks", {}).get(
            "max_candidates_per_slot", 32))

    # -- redesign ---------------------------------------------------------
    @property
    def redesign(self) -> Dict[str, Any]:
        return self.raw.get("redesign", {})

    @property
    def redesign_enabled(self) -> bool:
        return bool(self.redesign.get("enabled", True))

    @property
    def max_slot_changes(self) -> int:
        return int(self.redesign.get("max_slot_changes", 2))

    @property
    def allow_engine_swap(self) -> bool:
        return bool(self.redesign.get("allow_engine_swap", True))

    @property
    def range_module_categories(self) -> List[str]:
        return list(self.redesign.get("range_module_categories", ["extra_fuel", "drop_tanks"]))

    @property
    def max_candidates_per_slot(self) -> int:
        return int(self.redesign.get("max_candidates_per_slot", 24))

    # -- paths ------------------------------------------------------------
    @property
    def paths(self) -> Dict[str, Any]:
        return self.raw.get("paths", {})

    def dir_for(self, key: str, mod_root: Path) -> Path:
        return (mod_root / self.paths[key]).resolve()

    def globs_for(self, key: str) -> List[str]:
        return list(self.paths.get(key, []))

    # -- validation -------------------------------------------------------
    def validate(self) -> List[str]:
        problems: List[str] = []
        for section in ("range_targets", "role_weights", "switch",
                        "resource_significance", "frontier_priority",
                        "production_efficiency", "infantry", "ground", "paths"):
            if section not in self.raw:
                problems.append(f"config is missing required section `{section}`")
        if "default" not in self.raw.get("range_targets", {}):
            problems.append("range_targets has no `default` entry")
        if "default" not in self.raw.get("role_weights", {}):
            problems.append("role_weights has no `default` entry")
        for role, weights in self.raw.get("role_weights", {}).items():
            if not isinstance(weights, dict) or not weights:
                problems.append(f"role_weights.{role} is empty")
                continue
            if sum(abs(float(v)) for v in weights.values()) <= 0:
                problems.append(f"role_weights.{role} sums to zero absolute weight")
        for key in ("ai_equipment_dir", "equipment_dir", "modules_dir"):
            if key not in self.paths:
                problems.append(f"paths is missing `{key}`")
        ladder = self.frontier_priority_ladder
        if not ladder:
            problems.append("frontier_priority.relative_ladder is empty")
        elif ladder[0] != 1.0:
            problems.append("frontier_priority.relative_ladder must start at 1.0")
        elif any(value <= 0 for value in ladder):
            problems.append("frontier_priority.relative_ladder must stay positive")
        elif any(new >= old for old, new in zip(ladder, ladder[1:])):
            problems.append("frontier_priority.relative_ladder must be strictly descending")
        return problems


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> Config:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Config(raw=_strip_comments(data), path=path)
