# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Context

World Ablaze Beta is a Hearts of Iron IV gameplay overhaul mod. The repository root is the mod root loaded by HOI4.

Key metadata is in `descriptor.mod`:

| Field | Value |
| --- | --- |
| Mod name | `World Ablaze BETA LOCAL` |
| Game version | `1.18.0` |
| Supported version | `1.18.0` |
| Main themes | Gameplay, historical behavior, national focuses, technologies |

This mod overrides many vanilla directories through `replace_path` entries. Treat edits as full-content replacements where applicable, not additive patches over vanilla behavior. Small mistakes in replaced folders can remove vanilla definitions from the running game.

## Repository Structure

| Path | Purpose |
| --- | --- |
| `descriptor.mod` | HOI4 mod descriptor, tags, version, and `replace_path` declarations. |
| `common/` | Main HOI4 scripted content: AI strategies, decisions, ideas, focus trees, technologies, scripted effects, scripted triggers, on-actions, units, buildings, terrain, defines, and related game rules. |
| `events/` | Country, news, vanilla/DLC override, and WA AI background events. `WA_AI_*.txt` files are AI systems; `wa_<tag>_events.txt` files are WA country events. |
| `history/` | Countries, states, units, and other start-state data. |
| `localisation/` | Localisation, mostly under `localisation/replace/`. Generated localisation files use `_GENERATED_` in the filename. |
| `interface/`, `gfx/`, `portraits/`, `music/` | UI, graphics, portraits, and music assets. |
| `map/` | Map data used by HOI4 and by WA map-data generators. |
| `documentation/` | Design docs for larger systems, currently focused on the WA AI railway system. |
| `tests/` | Vanilla HOI4 test bundles for parity and regression checks. |
| `tools/` | Python tooling for map-data generation, AI `ai_will_do` replacement, resource prospecting analysis, and DLC/content splitting. |
| `README.md` | Minimal project README. |

## Generic Systems

Use this table to find the existing source of truth before adding new logic.

| System | Main Files | Notes |
| --- | --- | --- |
| AI lifecycle and scheduling | `common/on_actions/WA_AI_startup_on_actions.txt`, `common/on_actions/WA_AI_misc_on_actions.txt`, `events/WA_AI_misc.txt` | Startup initializes AI systems, templates, capitals, priority construction, and map data. Daily/weekly/monthly pulses call background AI effects. Add new recurring AI work here only after checking performance and cadence. |
| AI configuration and country archetypes | `common/scripted_triggers/WA_AI_CONFIG.txt` | Central place for generic AI difficulty, major/minor classification, doctrine archetypes, airforce archetypes, and similar country categories. The file header says this is the only WA_AI file intended to contain country tags. Prefer adding reusable config triggers here over scattering `tag =` or `original_tag =` checks. |
| Standard AI construction | `events/WA_AI_construction.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_queue_functions.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_building_adders.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_scoring.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`, `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` | Handles construction queues, target scoring, building adders, and scripted strategy choices. Reuse queue/add/scoring helpers instead of duplicating construction sequences in country files. |
| Priority construction core | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`, `common/on_actions/WA_AI_misc_on_actions.txt` | Dynamic project queue, factory assignment, progress tracking, and completion. Weekly update calls `WA_AI_PC_assign_factories` and `WA_AI_PC_update_project_progress`. |
| AI railway priority construction | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_primitives.txt`, `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`, `common/on_actions/WA_AI_misc_on_actions.txt`, `documentation/WA_AI_RAILWAY_SYSTEM.md` | Queue-based railway and naval-base construction for land war, overseas war, and pre-war preparation. Keep route orchestration in `railway_core`, strategy selection in `railway_strategies`, reusable calculations in `railway_helpers`, and low-level state/province checks in `railway_primitives`. |
| Map data, pathfinding, and math helpers | `common/scripted_effects/WA_AI_MAP_effects.txt`, `common/scripted_effects/WA_AI_MAP_province_connections.txt`, `common/scripted_effects/WA_AI_MAP_province_railway_connections.txt`, `common/scripted_effects/WA_AI_MAP_state_provinces.txt`, `common/scripted_effects/WA_AI_MAP_state_vp_provinces.txt`, `common/scripted_effects/WA_AI_MAP_province_coordinates.txt`, `common/scripted_effects/WA_AI_MAP_province_terrain.txt`, `common/scripted_effects/WA_AI_MAP_landmass_data.txt`, `common/scripted_effects/WA_AI_pathfinding_effects.txt`, `common/scripted_effects/WA_AI_MATH_effects.txt`, `tools/map_generators/`, `tools/run_generators.py` | Generated map lookup data supports province pathfinding, railway logic, landmass detection, state mappings, and distance calculation. Do not hand-edit generated `WA_AI_MAP_*` data files unless there is no viable generator path. |
| AI research weighting | `common/scripted_triggers/WA_AI_RESEARCH_*.txt`, `common/scripted_effects/WA_AI_RESEARCH_effects.txt`, `common/technologies/*.txt`, `tools/ai_will_do_replacer_all.py`, `tools/ai_replacer_base/`, `tools/REFACTORING_SUMMARY.md` | Research triggers drive `ai_will_do` blocks in technology files. Shared parser/generator code lives in `tools/ai_replacer_base/`. Preserve existing trigger logic when regenerating `ai_will_do`. |
| Resource needs and prospecting | `common/scripted_triggers/WA_AI_RESOURCE_NEEDS_triggers.txt`, `common/decisions/_resource_prospecting.txt`, `tools/needs_aware_generator.py`, `tools/prospecting_decision_analyzer.py`, `tools/ai_will_do_replacer_prospecting.py`, `PRESERVED_MODIFIER_FIX_FINAL.md`, `strategy_audit.csv` | Prospecting AI uses reactive, cooperative, and proactive layers. Preserve country-specific modifiers and indentation when regenerating decision `ai_will_do` blocks. |
| AI production and equipment behavior | `common/ai_strategy/WA_AI_PRODUCTION_*.txt`, `common/ai_strategy/World_Ablaze_production_air_strategies.txt`, `common/scripted_triggers/WA_AI_PRODUCTION_*.txt`, `common/scripted_effects/WA_production_strategy_effects.txt`, `common/ai_equipment/*.txt`, `common/decisions/z_WA_ai*.txt` | Handles production defaults, air-production flags, lend-lease production, equipment designs, and purge/fix decisions. Keep general production rules in shared WA_AI files and country-specific tuning in country-specific strategy/equipment files. |
| AI templates and division creation | `common/scripted_effects/WA_AI_TEMPLATES_effects.txt`, `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt`, `common/ai_templates/WA_AI_TEMPLATES_*.txt`, `common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt`, `common/on_actions/WA_AI_startup_on_actions.txt`, `common/on_actions/WA_AI_misc_on_actions.txt` | Template values are calculated at startup and monthly. Reuse existing template type codes and helper effects. Avoid adding one-off division templates outside the `WA_AI_TEMPLATES_*` pattern. |
| AI military fronts, invasions, and country strategy | `common/ai_strategy/WA_AI_MILITARY_FRONT_*.txt`, `common/ai_strategy/WA_AI_MILITARY_COUNTRY_*.txt`, `common/ai_strategy/WA_AI_MILITARY_INVASION_budget.txt`, `common/scripted_triggers/WA_AI_MILITARY_triggers.txt`, `events/WA_AI_<TAG>.txt`, `documentation/WA_AI_MILITARY_SYSTEM.md`, `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` | Front archetypes and caps are generic. Country strategy files hold country/faction behavior. **Read `documentation/WA_AI_MILITARY_SYSTEM.md` before adding or changing any `ai_strategy` block in `common/ai_strategy/WA_AI_MILITARY_*`** - it is the authoritative spec for the 4-layer model (Default / Region / Faction / Country), domain split (FRONT / INVASION / NAVAL / DIPLOMACY / THEATRE / GARRISON), per-type Additive vs Exclusive overlap policy, and naming convention. The companion `WA_AI_MILITARY_TYPES_REFERENCE.md` lists every `type =` in use, where it currently lives, and its target layer. Do not duplicate a front rule per country if a front archetype or config trigger can express it. |
| AI diplomacy, lend-lease, volunteers, laws, espionage, and leaders | `common/scripted_effects/WA_AI_lend_lease_effects.txt`, `common/scripted_effects/WA_AI_volunteer_effects.txt`, `common/scripted_effects/WA_AI_law_effects.txt`, `common/scripted_effects/WA_AI_espionage_effects.txt`, `common/scripted_effects/WA_AI_leader_recruitment_effects.txt`, matching `common/scripted_triggers/WA_AI_*_triggers.txt`, `common/ai_strategy/WA_AI_espionage_strategies.txt`, `common/decisions/categories/WA_AI_decision_categories.txt` | Shared AI behavior for diplomacy-facing systems. Keep recurring updates routed through existing background events and avoid adding player-visible decisions unless intended. |
| Historical AI capital ships | `events/WA_AI_Capitals.txt`, `common/scripted_effects/WA_AI_Capital_Ship_effects.txt`, `common/ideas/_WA_ai.txt` | Spawns historical capital ships for AI and applies dockyard output penalties through `WA_AI_Capital_Ship_cost`. Keep cost math and penalty duration in the scripted effect. |
| Reserves and manpower-related systems | `common/decisions/_reserves.txt`, `common/scripted_effects/WA_reserves_effects.txt`, `common/scripted_triggers/WA_reserves_triggers.txt`, `common/ideas/_manpower.txt` | Reserve and manpower mechanics. Reuse the existing effects/triggers for new reserve decisions. |
| Economy fatigue, war bonds, and generic decisions | `common/decisions/_economy_fatigue.txt`, `common/scripted_effects/Economy_Fatigue_scripted_effects.txt`, `common/decisions/_warbond_payback_decisions.txt`, `common/ideas/zzz_payback_war_Bonds.txt` | Generic economic mechanics outside the main WA_AI prefix. Keep decision effects close to their scripted effects. |
| Testing and debug support | `tests/*.txt`, `common/scripted_effects/WA_TEST_*.txt`, `common/scripted_triggers/WA_TEST_triggers.txt`, `common/on_actions/WA_TEST_on_actions.txt`, `events/wa_events_test.txt`, `common/decisions/_debug_decisions.txt` | `tests/wa_*_strict_parity.txt` are vanilla HOI4 test bundles. Some scripted test suites are compatibility shims or railway-specific harnesses. |

## Country Content Patterns

| Content Type | Preferred Location |
| --- | --- |
| Country events | `events/wa_<tag>_events.txt` for WA events, `events/<VanillaOrDLC>.txt` only when overriding vanilla/DLC content. |
| AI country events | `events/WA_AI_<TAG>.txt` for country-specific AI event behavior. |
| National focuses | `common/national_focus/<country>.txt`, with shared trees in files such as `generic.txt`, `nordic_shared.txt`, `china_shared.txt`, and `south_america_generic.txt`. |
| Decisions | Country files in `common/decisions/<TAG>.txt`; generic systems in underscored files such as `_resource_prospecting.txt`, `_reserves.txt`, `_economy_fatigue.txt`, and `_debug_decisions.txt`; AI decisions in `z_WA_ai*.txt`. |
| Ideas | Country files in `common/ideas/<country>.txt`; generic WA/AI ideas in `_WA_ai.txt`, `_spirits_*.txt`, `_economic.txt`, `_trade.txt`, and related underscored files. |
| Localisation | Follow existing `localisation/replace/*_l_english.yml` naming. Add or update localisation with the content it supports. Preserve existing encoding and formatting. |

## Editing Rules For Agents

1. Read the relevant system files before changing behavior. For AI work, start with the on-action or background event that calls the system, then read the scripted effect and scripted trigger files it uses.
2. Prefer the smallest correct change. This is a large replacement mod; broad rewrites can silently break unrelated vanilla overrides.
3. Do not duplicate logic across events, decisions, focuses, and AI files. Move reusable conditions into `common/scripted_triggers/` and reusable actions into `common/scripted_effects/`.
4. Keep generic AI country classification in `WA_AI_CONFIG.txt`. If a rule is based on country archetype, doctrine type, faction role, airforce type, or major/minor status, add or reuse a config trigger instead of copying country tag lists. For `common/ai_strategy/WA_AI_MILITARY_*` specifically, `tag = X` and `original_tag = X` are forbidden outside Country-layer files (see `documentation/WA_AI_MILITARY_SYSTEM.md`); use `WA_AI_MILITARY_is_<faction>_member` or `WA_AI_CONFIG_MILITARY_*` archetype/region triggers in Default, Region, and Faction layer files. Grace clause: until Phase 3 of the military refactor is complete, existing `tag` lists in faction files may remain but must not be extended; modifying any such block requires either replacing the tag list with an archetype trigger or relocating the block to a Country file.
5. Keep country-specific logic in country-specific files. Use `events/WA_AI_<TAG>.txt`, `common/ai_strategy/WA_AI_MILITARY_COUNTRY_<TAG>.txt`, `common/ai_equipment/<TAG>_*.txt`, and country decision/focus/idea files when behavior truly belongs to one country.
6. Split large AI systems by responsibility. The railway system is the model: `*_core` for entry/dispatch, `*_strategies` for high-level behavior, `*_helpers` for reusable calculations, and `*_primitives` for low-level checks.
7. Add clear scripted triggers and effects instead of inline complex blocks. Good triggers answer one positive question, for example `WA_AI_should_prospect_resource_steel`. Good effects document expected scope, inputs, and outputs in comments.
8. Respect HOI4 scopes. Be explicit in comments for effects that require `ROOT`, `THIS`, `PREV`, state scope, country scope, or province/state ID variables. Avoid changing scope chains unless you have traced all callers.
9. Clean temporary state. Clear temp arrays and temp variables when existing patterns do so, and avoid persistent variables/flags unless they are part of the system state.
10. Remember that `@` constants are file-scoped in HOI4 script. If a constant is needed in multiple files, redeclare it where used or store it as a global variable during initialization.
11. Preserve naming prefixes. Use `WA_` for mod gameplay content, `WA_AI_` for AI systems, and `WA_TEST_` for test harnesses. Avoid generic names that can collide with vanilla or DLC content.
12. Preserve indentation style. Existing Paradox script uses tabs heavily. Do not reformat unrelated blocks, especially generated or parser-managed `ai_will_do` sections.
13. Avoid hand-editing generated files. Prefer changing the generator under `tools/` and regenerating output for map data, generated localisation, and generated `ai_will_do` where applicable.
14. Preserve existing modifiers and triggers during generation. The resource prospecting tooling has had bugs around nested modifier extraction and indentation; review `PRESERVED_MODIFIER_FIX_FINAL.md` before changing that pipeline.
15. Update documentation when changing a documented system. The railway system has docs and test cases under `documentation/`; keep them in sync with behavior changes.

## Generated And Tool-Managed Content

| Generated Or Tool-Managed Area | Source Tooling |
| --- | --- |
| `common/scripted_effects/WA_AI_MAP_*` lookup data | `tools/run_generators.py` and `tools/map_generators/*.py` |
| Technology `ai_will_do` blocks | `tools/ai_will_do_replacer_all.py`, domain replacers, and `tools/ai_replacer_base/` |
| Prospecting decision `ai_will_do` blocks | `tools/needs_aware_generator.py`, `tools/prospecting_decision_analyzer.py`, `tools/ai_will_do_replacer_prospecting.py` |
| `_GENERATED_` localisation files | Existing generator workflow for their corresponding content |

Run map generators from `tools/` so default relative paths resolve correctly:

```powershell
python run_generators.py all --dry-run
python run_generators.py all
```

Run AI `ai_will_do` tooling in dry-run mode before applying changes, following `tools/REFACTORING_SUMMARY.md` for current parser status and limitations.

## Validation Guidance

Use the strongest practical validation for the files touched.

| Change Type | Suggested Validation |
| --- | --- |
| Map/pathfinding/railway generation | Run the relevant `tools/run_generators.py` generator with `--dry-run`, then run without `--dry-run` only when output changes are intended. Review `documentation/WA_AI_RAILWAY_SYSTEM.md` and related test docs. |
| Technology or prospecting AI weights | Run the relevant replacer/analyzer in dry-run mode, inspect diff, and verify nested modifiers and indentation are preserved. |
| Paradox script edits | Check brace balance, event IDs, namespaces, scopes, and trigger/effect names manually. HOI4 parser errors often appear only at game launch. |
| AI railway, spirit, or stats behavior | Use vanilla HOI4 test bundles in `tests/wa_railway_strict_parity.txt`, `tests/wa_spirits_strict_parity.txt`, and `tests/wa_stats_strict_parity.txt`; inspect HOI4 `logs/tests/tests_<timestamp>.log`. |
| Localisation/UI changes | Launch the game or inspect in-game UI where possible; missing localisation is not caught by Python tooling. |

## Safe Workflow

1. Identify the system from the table above.
2. Search for existing trigger/effect names and callers before adding new ones.
3. Make the minimal change in the file that owns the behavior.
4. Add or reuse scripted triggers/effects for reusable logic.
5. Update generated files only through their tooling when practical.
6. Run dry-run tools or in-game tests where feasible.
7. Document non-obvious new behavior near the owning system, not in unrelated country files.
