"""
Data-integrity checks on the mod's own `ai_equipment` / airframe data.

These are findings about the MOD, not about switching. They matter more than a
switching verdict does: a `target_variant` that names a module its airframe
cannot mount, or in a count its airframe caps below, cannot be matched by the
in-game designer at all - so the AI silently never builds that design, and the
design group behaves as if the generation were missing.

Three checks:

  count_limit   the target_variant mounts N of something the airframe caps
                below N (`count < 1` means "cannot mount at all")
  slot_category the target_variant puts a module in a slot whose
                `allowed_module_categories` does not list that module's category
  chain_order   the design chain runs backwards in airframe year

CAVEAT, stated in the output as well as here: `module_count_limit` override
semantics are inferred from the data, not verified in-game - see the README
approximation note. Spot-check one finding in-game before acting on the list.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Optional

from .parse_ai_equipment import DesignGroup
from .parse_equipment import EquipmentDB

EMPTY_TOKENS = {"empty", "none"}


@dataclass
class Finding:
    kind: str
    country: str
    group: str
    design: str
    airframe: str
    detail: str
    suggestion: str = ""


def _year(db: EquipmentDB, airframe: Optional[str]) -> Optional[int]:
    seen = set()
    cur = airframe
    while cur and cur not in seen:
        seen.add(cur)
        af = db.airframes.get(cur)
        if af is None:
            return None
        if af.year is not None:
            return af.year
        cur = af.parent or af.archetype
    return None


def audit(db: EquipmentDB, groups_by_country: Dict[str, List[DesignGroup]]) -> List[Finding]:
    out: List[Finding] = []
    for country, groups in sorted(groups_by_country.items()):
        for g in groups:
            chain = [d for d in g.designs if d.airframe]

            for prev, nxt in zip(chain, chain[1:]):
                yp, yn = _year(db, prev.airframe), _year(db, nxt.airframe)
                if yp is not None and yn is not None and yn < yp:
                    out.append(Finding(
                        "chain_order", country, g.name,
                        f"{prev.name} -> {nxt.name}", nxt.airframe or "",
                        f"airframe year {yp} -> {yn} ({yp - yn} yr backwards)",
                        "check the design order in this group; file position IS the "
                        "generation chain for both this tool and the in-game designer"))

            for d in chain:
                slots = db.resolve_slots(d.airframe)
                counts: Counter = Counter()
                for slot, ref in d.modules.items():
                    if not ref or ref.lower() in EMPTY_TOKENS or slot not in slots:
                        continue
                    mod, _kind = db.resolve_module_ref(ref, country)
                    if mod is None:
                        continue
                    counts[("module", mod.name)] += 1
                    if mod.category:
                        counts[("category", mod.category)] += 1
                    spec = slots[slot]
                    if spec.allowed_categories and mod.category \
                            and mod.category not in spec.allowed_categories:
                        out.append(Finding(
                            "slot_category", country, g.name, d.name, d.airframe or "",
                            f"slot `{slot}` = `{mod.name}` (category `{mod.category}`), but the "
                            f"airframe allows only: {', '.join(sorted(spec.allowed_categories))}",
                            "either widen the slot's allowed_module_categories on the airframe "
                            "or pick a module of an allowed category"))

                for kind, value, op, count in db.resolve_count_limits(d.airframe):
                    cap = db._cap_of(op, count)
                    if cap is None:
                        continue
                    have = counts.get((kind, value), 0)
                    if have > cap:
                        out.append(Finding(
                            "count_limit", country, g.name, d.name, d.airframe or "",
                            f"mounts {have} x `{value}` ({kind}) but the airframe caps it at "
                            f"{cap:g}",
                            "drop the extra, or lift the cap on the airframe with "
                            f"`module_count_limit = {{ {kind} = {value} count = any }}` "
                            "(the SOV_la_5_airframe idiom)"))
    return out


def summarise(findings: List[Finding]) -> Counter:
    return Counter(f.kind for f in findings)
