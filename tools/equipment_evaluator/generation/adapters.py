"""Adapters from domain result rows to the shared ai_equipment emitter API."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple


@dataclass
class GroundEmitterTransition:
    country: str
    group: str
    role: str
    from_design: str
    to_design: str
    verdict: str
    res_significant: Dict[str, float]
    ic_old: float
    ic_new: float
    redesign: Optional[object]


def _changes(items: List[str]) -> List[Tuple[str, str, str]]:
    parsed = []
    for item in items:
        if ":" not in item or "->" not in item:
            continue
        slot, values = item.split(":", 1)
        old, new = values.split("->", 1)
        parsed.append((slot.strip(), old.strip(), new.strip()))
    return parsed


def tank_emitter_transition(row) -> GroundEmitterTransition:
    redesign = None
    changes = _changes(row.redesign_changes)
    if changes:
        redesign = SimpleNamespace(
            changes=changes,
            gain_vs_old=row.adjusted_gain,
            gain_vs_new=0.0,
            stats=SimpleNamespace(range_km=0.0),
        )
    return GroundEmitterTransition(
        country=row.country, group=row.group, role=row.role,
        from_design=row.old, to_design=row.new, verdict=row.verdict,
        res_significant=dict(row.significant_resources),
        ic_old=row.old_stats.get("build_cost_ic", 0.0),
        ic_new=row.new_stats.get("build_cost_ic", 0.0), redesign=redesign)
