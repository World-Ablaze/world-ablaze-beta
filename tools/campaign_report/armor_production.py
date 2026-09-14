"""Observed output from two recorded country production counters.

MEASURED: country_reports/equipment_production/armor is a numeric counter.
DERIVED: its non-negative change divided by elapsed save days is an interval
average for the game's reported armor category, not a current production-line
rate and not an allocation to individual chassis families or variants.
"""
from __future__ import annotations

import math
from datetime import datetime


COUNTER_SOURCE = "countries/TAG/country_reports/equipment_production/armor"


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (ValueError, TypeError):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def production_counter(country_reports):
    """Read a parsed country_reports Node; missing fields remain unknown."""
    if country_reports is None:
        return None
    return _number(country_reports.block("equipment_production").scalar("armor"))


def _date(value):
    try:
        parts = [int(part) for part in value.split(".")]
        if len(parts) == 3:
            parts.append(0)
        if len(parts) != 4:
            return None
        return datetime(*parts)
    except (AttributeError, TypeError, ValueError):
        return None


def enrich_snapshots(snapshots):
    """Recompute interval output in place; return the supplied snapshot list.

Only adjacent observations of the same country are compared. Missing countries,
missing counters, non-increasing dates and counter resets break the interval.
Long intervals are retained with their exact duration, never labelled daily
samples or interpolated to conceal the observation gap. Campaign selection and
branch verification belong to campaign.py before this function is called.
"""
    previous = None
    for snapshot in snapshots:
        now = _date(snapshot.get("date"))
        before = _date(previous.get("date")) if previous else None
        days = (now - before).total_seconds() / 86400 if now and before else None
        for tag, country in snapshot.get("countries", {}).items():
            armor = country.setdefault("armor", {})
            armor.update(observed_production_per_day=None,
                         observed_production_count=None, production_interval=None)
            if days is None or days <= 0:
                continue
            old = previous.get("countries", {}).get(tag, {}).get("armor", {})
            current_value = _number(armor.get("production_total"))
            old_value = _number(old.get("production_total"))
            if current_value is None or old_value is None or current_value < old_value:
                continue
            count = current_value - old_value
            armor.update(observed_production_per_day=count / days,
                         observed_production_count=count,
                         production_interval={"from": previous["date"],
                                              "to": snapshot["date"], "days": days,
                                              "previous_file": previous.get("file")})
        previous = snapshot
    return snapshots
