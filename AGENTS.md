# AGENTS.md

Guidance for AI coding agents working in this repository.

## Agent Skills

`.claude/skills/` contains task-scoped skills that carry the working knowledge needed while editing. Claude Code loads them automatically; other agents should read the relevant `SKILL.md` directly. This file remains the authoritative system-ownership index — the skills route to it.

| Skill | Use it for |
| --- | --- |
| `.claude/skills/wa-orientation/SKILL.md` | Entry point. Repo layout, `replace_path` hazards, routing a task to its owner, validation matrix. |
| `.claude/skills/wa-pdxscript/SKILL.md` | PDXScript syntax, scopes, variables/arrays, `@` constants, `meta_trigger`, silent-failure pitfalls. |
| `.claude/skills/wa-ai-systems/SKILL.md` | `WA_AI_*` architecture: cadence, CONFIG archetypes, core/strategies/helpers/primitives split, military 4-layer model, railway queue. |
| `.claude/skills/wa-testing/SKILL.md` | Built-in `tests/` bundles and the `WA_TEST_*` scripted harness. |
| `.claude/skills/wa-tooling/SKILL.md` | Map generators, `ai_will_do` replacers, dry-run discipline. |
| `.claude/skills/wa-lessons-learned/SKILL.md` | Known gotchas (`references/lessons-log.md`) and the protocol for recording new ones. |
| `.claude/skills/wa-savegame-analysis/SKILL.md` | Reading HOI4 savegames: campaign identity, extracting variables/ideas/flags, cross-save trends. |
| `.claude/skills/wa-campaign-checklist/SKILL.md` | Scoring analysed test campaigns against the living verification checklist (`references/checklist.md`): WW2 arc, balance outcomes, fix probes, PASSED/FAILED streaks, retirement rules. Used in tandem with `wa-savegame-analysis`; every fix commit adds a probe here. |

## AI Design Philosophy

Three principles govern all new `WA_AI_*` code. When any other rule in this file conflicts with them, these win.

**1. Modular and setup-agnostic — no massive gaps.** AI behaviour must work in both historical and ahistorical games. Gate rules on *dynamic game state* — faction membership, active wars, ideology, doctrine archetype, geography, capability — never on the assumption that the historical script played out (Germany went fascist, France fell, Japan joined the Axis, the SOV–GER war happened). A rule that only fires on the historical path leaves the AI with *no behaviour at all* when the game diverges; every behaviour needs a generic fallback that produces sane play for any country in that situation. Historical-mode triggers (`WA_AI_DIFFICULTY_is_historical`) may *tune* behaviour, but must never be the only path to having behaviour. Modularity is what makes this possible: build behaviour from archetype triggers and shared effects so a new situation is covered by composition, not by another hand-written special case.

**2. Country tags live in `WA_AI_CONFIG.txt` — nowhere else.** All country classification goes through archetype triggers in `common/scripted_triggers/WA_AI_CONFIG.txt`. Before writing `tag =` / `original_tag =` anywhere else, reformulate the rule as an archetype question ("is this a major Axis land power?") and add or reuse a CONFIG trigger. The Country layer (`WA_AI_MILITARY_COUNTRY_<TAG>*`, `events/WA_AI_<TAG>.txt`, `common/ai_equipment/<TAG>_*`) is the sole sanctioned exception, reserved for behaviour genuinely unique to one nation — treat every addition there as a design decision to justify, not a convenience, and ask first whether an archetype trigger would cover it.

**3. Change existing systems only with an impact analysis.** Existing behaviour is load-bearing, encodes fixes for cases that already broke (see the `# Fix NN:` convention), and misbehaves silently — regressions surface mid-campaign, not at parse time. Before modifying an existing trigger, effect, or strategy block: (a) enumerate every caller and reader (grep the name across `common/` and `events/`); (b) identify which countries, archetypes, and cadences reach it; (c) walk both the historical and an ahistorical scenario through the change; (d) check `wa-lessons-learned` and surrounding `# Fix NN:` comments for the case the current code encodes; (e) state the regression risk explicitly in your summary. Prefer additive, gated changes over in-place rewrites of shared code paths. When the risk is unclear, diagnose first — the first hypothesis about AI misbehaviour in this codebase is usually wrong.

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
| Priority construction core | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`, `common/on_actions/WA_AI_misc_on_actions.txt`, `documentation/WA_AI_PC_QUEUE_FAIRNESS_DIAGNOSIS.md` | Dynamic project queue, factory assignment, progress tracking, and completion. Weekly update calls `WA_AI_PC_assign_factories` and `WA_AI_PC_update_project_progress`. **Queue fairness is the failure mode this system keeps having** — allocation is winner-takes-most from a priority-sorted queue, so any band below the head starves unless something reserves for it (Fix 41 lane, Fix 78 air lane) and any uncapped admission path floods it (Fix 77). Read the diagnosis doc before changing admission, allocation, or the stall sweep. |
| AI railway priority construction | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_primitives.txt`, `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`, `common/on_actions/WA_AI_misc_on_actions.txt`, `documentation/WA_AI_RAILWAY_SYSTEM.md` | Queue-based railway and naval-base construction for land war, overseas war, and pre-war preparation. Keep route orchestration in `railway_core`, strategy selection in `railway_strategies`, reusable calculations in `railway_helpers`, and low-level state/province checks in `railway_primitives`. |
| Map data, pathfinding, and math helpers | `common/scripted_effects/WA_AI_MAP_effects.txt`, `common/scripted_effects/WA_AI_MAP_province_connections.txt`, `common/scripted_effects/WA_AI_MAP_province_railway_connections.txt`, `common/scripted_effects/WA_AI_MAP_state_provinces.txt`, `common/scripted_effects/WA_AI_MAP_state_vp_provinces.txt`, `common/scripted_effects/WA_AI_MAP_province_coordinates.txt`, `common/scripted_effects/WA_AI_MAP_province_terrain.txt`, `common/scripted_effects/WA_AI_MAP_landmass_data.txt`, `common/scripted_effects/WA_AI_pathfinding_effects.txt`, `common/scripted_effects/WA_AI_MATH_effects.txt`, `tools/map_generators/`, `tools/run_generators.py` | Generated map lookup data supports province pathfinding, railway logic, landmass detection, state mappings, and distance calculation. Do not hand-edit generated `WA_AI_MAP_*` data files unless there is no viable generator path. |
| AI research weighting | `common/scripted_triggers/WA_AI_RESEARCH_*.txt`, `common/scripted_effects/WA_AI_RESEARCH_effects.txt`, `common/technologies/*.txt`, `tools/ai_will_do_replacer_all.py`, `tools/ai_replacer_base/`, `tools/REFACTORING_SUMMARY.md` | Research triggers drive `ai_will_do` blocks in technology files. Shared parser/generator code lives in `tools/ai_replacer_base/`. Preserve existing trigger logic when regenerating `ai_will_do`. |
| Resource needs and prospecting | `common/scripted_triggers/WA_AI_RESOURCE_NEEDS_triggers.txt`, `common/decisions/_resource_prospecting.txt`, `tools/needs_aware_generator.py`, `tools/prospecting_decision_analyzer.py`, `tools/ai_will_do_replacer_prospecting.py`, `PRESERVED_MODIFIER_FIX_FINAL.md`, `strategy_audit.csv` | Prospecting AI uses reactive, cooperative, and proactive layers. Preserve country-specific modifiers and indentation when regenerating decision `ai_will_do` blocks. |
| AI production and equipment behavior | `common/ai_strategy/WA_AI_PRODUCTION_*.txt`, `common/ai_strategy/World_Ablaze_production_air_strategies.txt`, `common/scripted_triggers/WA_AI_PRODUCTION_*.txt`, `common/scripted_effects/WA_production_strategy_effects.txt`, `common/ai_equipment/*.txt`, `common/decisions/z_WA_ai*.txt` | Handles production defaults, air-production flags, lend-lease production, equipment designs, and purge/fix decisions. Keep general production rules in shared WA_AI files and country-specific tuning in country-specific strategy/equipment files. |
| AI templates and division creation | `common/scripted_effects/WA_AI_TEMPLATES_effects.txt`, `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt`, `common/ai_templates/WA_AI_TEMPLATES_*.txt`, `common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt`, `common/on_actions/WA_AI_startup_on_actions.txt`, `common/on_actions/WA_AI_misc_on_actions.txt` | Template values are calculated at startup and monthly. Reuse existing template type codes and helper effects. Avoid adding one-off division templates outside the `WA_AI_TEMPLATES_*` pattern. |
| AI military fronts, invasions, and country strategy | `common/ai_strategy/WA_AI_MILITARY_DEFAULT_*.txt`, `common/ai_strategy/WA_AI_MILITARY_REGION_*.txt`, `common/ai_strategy/WA_AI_MILITARY_FACTION_*.txt`, `common/ai_strategy/WA_AI_MILITARY_COUNTRY_*.txt`, `common/ai_strategy/WA_AI_NAVAL_*.txt`, `common/scripted_triggers/WA_AI_MILITARY_triggers.txt`, `events/WA_AI_<TAG>.txt`, `documentation/WA_AI_MILITARY_SYSTEM.md`, `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` | Front archetypes and caps live in DEFAULT files; coalition behaviour in FACTION files; geography rules in REGION files; per-country tuning in COUNTRY files; naval-domain strategy files use the `WA_AI_NAVAL_*` prefix. **Read `documentation/WA_AI_MILITARY_SYSTEM.md` before adding or changing any `ai_strategy` block in `common/ai_strategy/WA_AI_MILITARY_*` or `common/ai_strategy/WA_AI_NAVAL_*`** - it is the authoritative spec for the 4-layer model (Default / Region / Faction / Country), domain split (FRONT / INVASION / NAVAL / DIPLOMACY / THEATRE / GARRISON), per-type Additive vs Exclusive overlap policy, and naming convention. The companion `WA_AI_MILITARY_TYPES_REFERENCE.md` lists every `type =` in use, where it currently lives, and its target layer. Do not duplicate a front rule per country if a front archetype or config trigger can express it. |
| Scripted-landing invasion freeze | `common/scripted_triggers/WA_AI_LANDING_triggers.txt`, `common/scripted_effects/WA_AI_LANDING_effects.txt`, `common/ai_strategy/WA_AI_MILITARY_DEFAULT_INVASION_landing_freeze.txt`, call site inside `WA_AI_DIVISION_spawn_invasion` (`WA_AI_DIVISION_CREATOR_effects.txt`), `documentation/WA_AI_MILITARY_SYSTEM.md` §10 | When a country *executes* a WA-scripted amphibious landing, AI-planned naval invasions are suppressed faction-wide for 90 days, scoped to the landing's macro-theatre. The marker is generic - all ~90 scripted operations route through `WA_AI_DIVISION_spawn_invasion`, so nothing here keys on a date or a tag. **All behavioural switches live in `WA_AI_LANDING_triggers.txt`** (window length, theatre definitions, and the blanket-vs-theatre-scoped switch) - change behaviour there, never by editing the strategy blocks. |
| Allied Reich bombing ladder | `common/ai_strategy/WA_AI_MILITARY_FACTION_ALLIES_AIR.txt`, the "AIR - Allied Reich bombing ladder" section of `common/scripted_triggers/WA_AI_MILITARY_triggers.txt`, `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` (`strategic_air_importance`) | How hard the western Allies are told to avoid German air space, and when that lifts. Three additive `strategic_air_importance` rungs over the near ring (regions 6/7/8/296) and deep ring (294/38), each gated on a **deployed strategic-bomber count** rather than a date, each enabling below its own bar and aborting above the next one so the net walks down with hysteresis. **All behavioural switches - the four thresholds, the ring membership, the contested-Germany backstop - live in `WA_AI_MILITARY_triggers.txt`**; change behaviour there, never by editing the strategy blocks. Replaced the legacy ENG.txt date-gated family (`Allies_bombing_germany_is_too_costly`, `allies_avoid_bombing_austria_prussia`, `ENG_FRA_allies_avoid_bombing_GER`). The positive half of the campaign is `WA_AI_MILITARY_ENG_strategic_bombing_focus_THEATRE`, which writes `area_priority` and is a separate axis. |
| AI force concentration (AIFC) | `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt`, `common/scripted_effects/WA_AI_AIFC_core.txt`, `common/scripted_effects/WA_AI_AIFC_helpers.txt`, `common/scripted_triggers/WA_AI_AIFC_triggers.txt`, `common/on_actions/WA_AI_misc_on_actions.txt` | The engine feature that lets the AI mass surplus divisions on a chosen offensive axis instead of spreading them evenly. Four layers: doctrine ladder (built on WA's own grand doctrines and `tier_N` tracks, not vanilla's), situational posture, a weekly scripted sector selection publishing `WA_AI_AIFC_sector_states` / `_objectives`, and the `ai_strategy` blocks that consume them. **All behavioural switches live in `WA_AI_AIFC_triggers.txt`** - change behaviour there, never by editing the strategy blocks. Every boost must be paired with a suppression of everything outside the target set; unpaired AIFC values do effectively nothing. Full system reference is the header comment of `WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt`. |
| AI diplomacy, lend-lease, volunteers, laws, espionage, and leaders | `common/scripted_effects/WA_AI_lend_lease_effects.txt`, `common/scripted_effects/WA_AI_volunteer_effects.txt`, `common/scripted_effects/WA_AI_law_effects.txt`, `common/scripted_effects/WA_AI_espionage_effects.txt`, `common/scripted_effects/WA_AI_leader_recruitment_effects.txt`, matching `common/scripted_triggers/WA_AI_*_triggers.txt`, `common/ai_strategy/WA_AI_espionage_strategies.txt`, `common/decisions/categories/WA_AI_decision_categories.txt` | Shared AI behavior for diplomacy-facing systems. Keep recurring updates routed through existing background events and avoid adding player-visible decisions unless intended. |
| Historical AI capital ships | `events/WA_AI_Capitals.txt`, `common/scripted_effects/WA_AI_Capital_Ship_effects.txt`, `common/ideas/_WA_ai.txt` | Spawns historical capital ships for AI and applies dockyard output penalties through `WA_AI_Capital_Ship_cost`. Keep cost math and penalty duration in the scripted effect. |
| Reserves and manpower-related systems | `common/decisions/_reserves.txt`, `common/scripted_effects/WA_reserves_effects.txt`, `common/scripted_triggers/WA_reserves_triggers.txt`, `common/ideas/_manpower.txt` | Reserve and manpower mechanics. Reuse the existing effects/triggers for new reserve decisions. |
| Economy fatigue, war bonds, and generic decisions | `common/decisions/_economy_fatigue.txt`, `common/scripted_effects/Economy_Fatigue_scripted_effects.txt`, `common/decisions/_warbond_payback_decisions.txt`, `common/ideas/zzz_payback_war_Bonds.txt` | Generic economic mechanics outside the main WA_AI prefix. Keep decision effects close to their scripted effects. |
| Testing and debug support | `tests/*.txt`, `common/scripted_effects/WA_TEST_*.txt`, `common/scripted_triggers/WA_TEST_triggers.txt`, `common/on_actions/WA_TEST_on_actions.txt`, `events/wa_events_test.txt`, `common/decisions/_debug_decisions.txt` | `tests/wa_*_strict_parity.txt` are vanilla HOI4 test bundles. Some scripted test suites are compatibility shims or railway-specific harnesses. |
| Save-visible telemetry (WA_TLM) | `common/scripted_effects/WA_TLM_core.txt`, `documentation/WA_TLM_TELEMETRY_SYSTEM.md`, startup + monthly wiring in the two `WA_AI_*_on_actions.txt` files | Standardized write-only instrumentation read by campaign-analysis agents from savegames (`wa_tlm_*` namespace, `savegame.py tlm`). Any new save-visible probe or metric — including the per-fix probes the campaign checklist requires — follows this standard; the doc's §7 is the author checklist. Telemetry must never be read by gameplay/AI logic. |

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
4. Keep generic AI country classification in `WA_AI_CONFIG.txt`. If a rule is based on country archetype, doctrine type, faction role, airforce type, or major/minor status, add or reuse a config trigger instead of copying country tag lists. For `common/ai_strategy/WA_AI_MILITARY_*` specifically, `tag = X` and `original_tag = X` are forbidden as **gating** terms (inside `allowed = {}` or `enable = {}`) outside Country-layer files (see `documentation/WA_AI_MILITARY_SYSTEM.md`); use `WA_AI_MILITARY_is_<faction>_member` or `WA_AI_CONFIG_MILITARY_*` archetype/region triggers in Default, Region, and Faction layer files. Phase 3 of the military refactor replaced all multi-tag OR-lists with archetype triggers; remaining single-tag literals (e.g. `NOT = { tag = ITA }` to gate "everyone except Italy") are permitted. Tag references inside `ai_strategy = {}` payload (e.g. `id = "USA"`, `target = ...`) are payload, not gating, and are unaffected by this rule.
5. Keep country-specific logic in country-specific files. Use `events/WA_AI_<TAG>.txt`, `common/ai_strategy/WA_AI_MILITARY_COUNTRY_<TAG>.txt`, `common/ai_equipment/<TAG>_*.txt`, and country decision/focus/idea files when behavior truly belongs to one country.
6. Split large AI systems by responsibility. The railway system is the model: `*_core` for entry/dispatch, `*_strategies` for high-level behavior, `*_helpers` for reusable calculations, and `*_primitives` for low-level checks.
7. Add clear scripted triggers and effects instead of inline complex blocks. Good triggers answer one positive question, for example `WA_AI_should_prospect_resource_steel`. Good effects document expected scope, inputs, and outputs in comments.
8. Respect HOI4 scopes. Be explicit in comments for effects that require `ROOT`, `THIS`, `PREV`, state scope, country scope, or province/state ID variables. Avoid changing scope chains unless you have traced all callers.
9. Clean temporary state. Clear temp arrays and temp variables when existing patterns do so, and avoid persistent variables/flags unless they are part of the system state.
10. Remember that `@` constants are file-scoped in HOI4 script. If a constant is needed in multiple files, redeclare it where used or store it as a global variable during initialization.
11. Preserve naming prefixes. Use `WA_` for mod gameplay content, `WA_AI_` for AI systems, `WA_TEST_` for test harnesses, and `WA_TLM_` for save-visible telemetry (reserved, write-only — see `documentation/WA_TLM_TELEMETRY_SYSTEM.md`). Avoid generic names that can collide with vanilla or DLC content.
12. Preserve indentation style. Existing Paradox script uses tabs heavily. Do not reformat unrelated blocks, especially generated or parser-managed `ai_will_do` sections.
13. Avoid hand-editing generated files. Prefer changing the generator under `tools/` and regenerating output for map data, generated localisation, and generated `ai_will_do` where applicable.
14. Preserve existing modifiers and triggers during generation. The resource prospecting tooling has had bugs around nested modifier extraction and indentation; review `PRESERVED_MODIFIER_FIX_FINAL.md` before changing that pipeline.
15. Update documentation when changing a documented system. The railway system has docs and test cases under `documentation/`; keep them in sync with behavior changes.
16. **Never write a UTF-8 BOM into a `.txt` script file.** Files under `common/` and `events/` must be plain UTF-8 with no byte-order mark. The HOI4 parser for `common/scripted_effects/` and `common/scripted_triggers/` treats the BOM as a stray token and desyncs on every `=` / `}` after it, so the whole file silently fails to load (seen 2026-08-15: `WA_AI_CONSTRUCTION_PRIORITY_core.txt` was re-saved with a BOM and the entire priority-construction system stopped parsing). Only `localisation/**/*.yml` requires a BOM. When you rewrite a whole file with Write, keep it BOM-free; when in doubt, check the first three bytes (`EF BB BF` = bad).

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
