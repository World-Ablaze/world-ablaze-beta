"""Domain-independent equipment adoption policy."""

from __future__ import annotations

from typing import Dict, Mapping, Sequence

from .production_efficiency import EfficiencyModel

SWITCH = "SWITCH"
SWITCH_REDESIGNED = "SWITCH_REDESIGNED"
SWITCH_CONDITIONAL = "SWITCH_CONDITIONAL"
KEEP_OLD = "KEEP_OLD"
PARALLEL_VARIANT = "PARALLEL_VARIANT"
UNRESOLVED = "UNRESOLVED"

ADOPTION_VERDICTS = frozenset((SWITCH, SWITCH_REDESIGNED, SWITCH_CONDITIONAL))


def weighted_relative_gain(old: Mapping[str, float], new: Mapping[str, float],
                           weights: Mapping[str, float], floors) -> float:
    denom = sum(abs(value) for value in weights.values()) or 1.0
    # Deliberately accumulate in insertion order. Besides being deterministic,
    # this preserves the historical CSV floats across the refactor (Python's
    # built-in sum may use compensated summation depending on runtime version).
    total = 0.0
    for stat, weight in weights.items():
        total += (weight * (new.get(stat, 0.0) - old.get(stat, 0.0))
                  / max(abs(old.get(stat, 0.0)), floors(stat)))
    return total / denom


def numeric_delta(old: Mapping[str, float], new: Mapping[str, float]) -> Dict[str, float]:
    return {key: new.get(key, 0.0) - old.get(key, 0.0)
            for key in sorted(set(old) | set(new))}


def significant_increases(delta: Mapping[str, float], threshold) -> Dict[str, float]:
    return {key: value for key, value in delta.items() if value >= threshold(key)}


def decide_adoption(*, adjusted_gain: float, retention: float,
                    significant_resources: Mapping[str, float],
                    blockers: Sequence[str], model: EfficiencyModel,
                    redesigned: bool = False) -> str:
    """Apply hard constraints, efficiency policy, then economy gating."""
    if blockers or adjusted_gain <= 0.0:
        return KEEP_OLD
    if (retention < model.full_switch_min_retention
            and adjusted_gain < model.low_retention_min_gain):
        return KEEP_OLD
    if significant_resources:
        return SWITCH_CONDITIONAL
    return SWITCH_REDESIGNED if redesigned else SWITCH


def apply_efficiency_gate(verdict: str, gain: float, retention: float,
                          model: EfficiencyModel) -> str:
    if verdict not in ADOPTION_VERDICTS:
        return verdict
    if retention < model.full_switch_min_retention and gain < model.low_retention_min_gain:
        return KEEP_OLD
    return verdict
