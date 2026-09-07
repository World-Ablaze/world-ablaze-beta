"""Current training equipment, separate from stock and reinforcement requests.

MEASURED inputs: serialized military_deployment instances, their held equipment,
and template battalion counts. DERIVED requirements use this checkout's sub-unit
`need` definitions. Count instantiated rows once, never multiply serial conveyor
or line repeat amounts. This is not the engine's verified logistics shortfall.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=4)
def unit_equipment_needs(repo):
    """Read literal sub-unit needs; unsupported expressions remain unknown."""
    from .extract import Node, number, parse

    result = {}
    for path in sorted((Path(repo) / "common/units").glob("*.txt")):
        for key, node in parse(path.read_text(encoding="utf-8-sig", errors="replace")).block("sub_units"):
            if not isinstance(node, Node):
                continue
            need = node.get("need")
            if not isinstance(need, Node):
                result[key] = None
                continue
            parsed = [(equipment, number(value)) for equipment, value in need]
            result[key] = dict(parsed) if all(k is not None and v is not None and v >= 0 for k, v in parsed) else None
    return result


def analyze_training(deployment, templates, definitions, catalog, unit_needs):
    """Return family requirements/holdings/gaps and held variant counts.

    `None` deployment means unavailable; an empty parsed deployment means no
    instantiated training divisions. A gap is calculated per instance and
    family before summing, so surplus in one division cannot cover another.
    Transit, stock, future repeats and variant eligibility are not inferred.
    """
    from .extract import Node, _id, blocks, number

    result = dict(families={}, variants={}, instances=0,
                  requirements_complete=deployment is not None,
                  holdings_complete=deployment is not None, issues=[])
    if deployment is None:
        return result
    families, variants = {}, Counter()

    def family_row(family):
        return families.setdefault(family, dict(requirement=0, held=0, gap=0))

    for conveyor in blocks(deployment, "military_deployment_conveyor"):
        template_id = _id(conveyor, "division_template_id")
        template = templates.get(template_id)
        for line in blocks(conveyor, "military_deployment_line"):
            for instance in blocks(line, "military_deployment"):
                result["instances"] += 1
                requirement, held = Counter(), Counter()
                need_valid = template is not None
                if template is None:
                    result["issues"].append(f"Training template #{template_id} is absent from this save.")
                else:
                    for section in ("regs", "sup"):
                        for unit, count in template.get(section, {}).items():
                            needs = unit_needs.get(unit)
                            if needs is None:
                                need_valid = False
                                result["issues"].append(f"Training sub-unit {unit} has no supported equipment requirement in this checkout.")
                                continue
                            for archetype, amount in needs.items():
                                classification = catalog.get(archetype)
                                if not classification or classification.get("family") is None:
                                    need_valid = False
                                    result["issues"].append(f"Training equipment archetype {archetype} has no classification in this checkout.")
                                elif classification.get("domain") == "armor":
                                    requirement[classification["family"]] += count * amount
                inventory = instance.get("equipment")
                held_valid = isinstance(inventory, Node)
                if not held_valid:
                    result["issues"].append("A training instance has no equipment block; its holdings are unknown.")
                else:
                    for equipment in blocks(inventory, "equipment"):
                        eid, amount = _id(equipment), number(equipment.scalar("amount"))
                        definition = definitions.get(eid, {})
                        classification = catalog.get(definition.get("definition"))
                        if amount is None or amount < 0 or not classification or classification.get("family") is None:
                            held_valid = False
                            result["issues"].append(f"Training equipment #{eid} has an unsupported amount or classification.")
                        elif classification.get("domain") == "armor":
                            held[classification["family"]] += amount
                            variants[eid] += amount
                result["requirements_complete"] &= need_valid
                result["holdings_complete"] &= held_valid
                for family in set(requirement) | set(held):
                    row = family_row(family)
                    row["requirement"] += requirement[family]
                    row["held"] += held[family]
                    row["gap"] += max(0, requirement[family] - held[family])
    # Any unresolved row could belong to any family: do not publish partial totals.
    for row in families.values():
        if not result["requirements_complete"]:
            row["requirement"] = None
        if not result["holdings_complete"]:
            row["held"] = None
        if not (result["requirements_complete"] and result["holdings_complete"]):
            row["gap"] = None
    result.update(families=families, variants=dict(variants), issues=list(dict.fromkeys(result["issues"])))
    return result
