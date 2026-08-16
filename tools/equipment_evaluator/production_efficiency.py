"""Production-line efficiency retention model shared by equipment domains.

The factors are read from WA's ``common/defines/05_defines.lua`` semantics:
variant 95 %, parent/child 95 %, family 90 %, archetype 75 %.  An unrelated
switch falls back to BASE_FACTORY_START_EFFICIENCY_FACTOR (10 %).

This module deliberately models *line switching*, not equipment conversion.
``can_convert_from`` controls stockpile conversion and is reported separately;
it does not make a production line retain more efficiency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional


VARIANT = "variant"
PARENT = "parent"
FAMILY = "family"
ARCHETYPE = "archetype"
UNRELATED = "unrelated"


@dataclass(frozen=True)
class EfficiencyModel:
    variant: float = 0.95
    parent: float = 0.95
    family: float = 0.90
    archetype: float = 0.75
    unrelated: float = 0.10
    full_switch_min_retention: float = 0.90
    efficiency_penalty_weight: float = 0.50
    penalty_free_retention: float = 0.90
    low_retention_min_gain: float = 0.10

    def factor(self, relation: str) -> float:
        return float(getattr(self, relation, self.unrelated))

    def adjusted_gain(self, combat_gain: float, retention: float) -> float:
        """Penalise a benefit by the immediate fraction of output discarded.

        This is intentionally a conservative, dimensionless decision score,
        not a claim to reproduce HOI4's day-by-day efficiency recovery curve.
        The raw retention and shock are always emitted so later runtime work can
        combine them with actual line efficiency, factory count and stockpile.
        """
        # A 5-10% loss is recovered quickly and must not veto a real upgrade.
        # Penalise only the portion below the configured grace level.
        shock = max(0.0, self.penalty_free_retention - retention)
        return combat_gain - self.efficiency_penalty_weight * shock


def classify_relation(
    old_name: str,
    new_name: str,
    *,
    old_archetype: Optional[str],
    new_archetype: Optional[str],
    old_family: Optional[str],
    new_family: Optional[str],
    is_ancestor: Callable[[str, str], bool],
) -> str:
    """Return the strongest HOI4 production-efficiency relationship."""
    if old_name == new_name:
        return VARIANT
    if is_ancestor(old_name, new_name) or is_ancestor(new_name, old_name):
        return PARENT
    if old_family and new_family and old_family == new_family:
        return FAMILY
    if old_archetype and new_archetype and old_archetype == new_archetype:
        return ARCHETYPE
    return UNRELATED
