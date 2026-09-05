# tools/ — index by usage tier

The folder is laid out by how often a script runs, so a session can tell at a glance
what it is expected to launch. Full rationale and the measurements behind the split:
`documentation/TOOLS_REORG_PROPOSAL.md`.

| Tier | Where | Run when | Contents |
| --- | --- | --- | --- |
| **Gates** | `tools/` (root) | Before every commit / before scoring a campaign (AGENTS.md validation matrix) | `check_constants.py` + `constants_registry.json`, `check_ai_layers.py` + `ai_layers_baseline.json`, `check_worklist.py` + `check_worklist_selftest.py`, `check_ai_equipment_names.py`, `check_engine_docs.py` + `engine_docs_manifest.json`, `check_skill_refs.py`, `check_templates.py`, `military_economy_audit.py` |
| **Log readers** | `tools/` (root) | After every owner boot / console harness run | `read_harness_log.py`, `triage_error_log.py` |
| **Generators** | `tools/gen/` | When their source changes (map, corridors, medium ladder, faction theatres, landing calendar) | `run_generators.py` + `map_generators/` + `core/`, `gen_rail_corridors.py`, `gen_ai_medium_modern_mirror.py`, `gen_ai_faction_theaters.py`, `gen_ai_landing_reservations.py` |
| **Evaluator** | `tools/equipment_evaluator/` | On demand (`python -m equipment_evaluator`, pytest inside) | Self-contained package, see its README |
| **Migrations** | `tools/migrations/` | Replayable pipelines, rarely replayed (`ai_will_do/` tech replacers + `ai_replacer_base/`; `prospecting/` decision replacer) | Dry-run first, always |
| **Archive** | `tools/archive/` | Never — one-shot scripts already applied, kept for provenance, not maintained | `fix_tracking/` (Fix-NN → slug collapse, `fix_registry.json` read by `documentation/FIX_HISTORY.md`), `misc/`, `dlc_splitter/` |

Every script resolves the mod root from its own location, so all of them run from any
working directory: `python tools/gen/run_generators.py all --dry-run`.

Adding a script: put it in the tier matching its cadence, not its subject. A generator that
is run once and never again belongs in `archive/`, not `gen/`.
