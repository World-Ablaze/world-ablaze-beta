"""
World Ablaze offline equipment evaluator - all constructible equipment domains,
with dry-run generation by default.

Evaluates air, tanks, infantry, artillery and vehicles using a shared adoption
policy over domain-specific stats, redesign constraints, production-efficiency
retention and resource deltas.

Only the explicit `--apply-plan` command writes into mod content. Plans are
fingerprinted, transactionally applied and idempotent; ordinary evaluation and
`--generate-plan` remain read-only with respect to the mod.

Entry point: `python -m equipment_evaluator --help` (run from `tools/`).
"""

__version__ = "2.0.0"
