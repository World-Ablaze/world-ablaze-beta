"""[armor-template-generator] Direct role transfer: the destination resolution the controller
reads (A5).

This module decides NOTHING about the engine primitive. It publishes, per source family, the
ordered destination families and the code of the destination composition a source should land on,
so the handwritten controller in common/scripted_effects/WA_AI_TEMPLATES_ARMOR_transition.txt
never reconstructs composition priorities. Whether a deployed division actually changed role is
observed in game, not inferred from this table.
"""

from __future__ import annotations


def build(registry, per_family_selections):
    out = {}
    for tid, spec in sorted(registry.transitions.items()):
        destinations = []
        for family_id in spec["destination_order"]:
            if family_id not in per_family_selections:
                continue
            fam = registry.families[family_id]
            destinations.append({
                "family": family_id,
                "flag": fam["flag"],
                "role": fam["role"],
                "admission": fam["admission"],
                "target_count": len(per_family_selections[family_id]),
            })
        out[tid] = {
            "source_families": spec["source_families"],
            "admission": spec.get("admission"),
            "destinations": destinations,
            "fallback": {
                "contract": ["preflight", "source_removed", "empty_successor_created", "verified"],
                "enabled_by_default": False,
                "_comment": "The delete-and-respawn fallback stays disabled until the direct "
                            "transfer has been observed to fail in game and the cause is "
                            "classified. Nothing here executes a deletion.",
            },
        }
    return out
