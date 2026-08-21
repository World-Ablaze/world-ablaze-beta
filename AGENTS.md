# AGENTS.md

Guidance for AI coding agents working in this repository.

## Talking to the user

These rules govern every user-facing message. They are about *how* you write, not *what* you conclude — the content rules below still apply in full.

**Reply in the user's language** (French, currently).

**Answer first.** The verdict is the first thing on screen: at most 5 short lines, one idea per line, the verdict in bold. Everything after it is evidence, and evidence goes in a table, not in prose. No preamble, no restating the question.

**Write for someone who is not a PDXScript expert and is juggling five other sessions.** Short sentences. No jargon without a three-word gloss in parentheses the first time it appears — `put_unit_buffers` (the order that parks reserve divisions on an area). A file path with a line number is not jargon; a system name used without saying what it does is.

**Label every factual claim about how the game or the mod behaved.** One of three tokens, in bold, at the front of the claim:

| Label | Means |
| --- | --- |
| **MEASURED** | Read directly out of a savegame, a game file, or a mod file — name the source. |
| **DERIVED** | Computed or inferred from something MEASURED. Say from what. |
| **ASSUMED** | Not verified. Plausible, unchecked, or engine behaviour nobody can observe. |

**The three tokens stay in English in every language**, including a French reply: they are labels, not prose, and a translated label drifts into a second vocabulary. The label **replaces hedging**. Do not write "probably", "it seems", "likely", "sans doute" — write **ASSUMED** and keep the sentence direct. An unlabelled claim reads as MEASURED, so an unlabelled guess is a lie.

**The engine is a black box, and unread code is not knowledge.** HOI4's internal AI weighting, its front assignment and its unit-request arbitration are not observable from a save. Anything about them you did not read in a game file is **ASSUMED**, however confident it feels — and so is any mod behaviour whose file you have not opened this session. "The first hypothesis about AI misbehaviour in this codebase is usually wrong" (principle 3) is a statement about how often ASSUMED turns out false.

**Deep detail goes in a file, not in chat.** Long tables, full extraction dumps, multi-page reasoning: write them to the scratchpad or to the owning document and hand the user the link. Chat carries the verdict and the evidence that supports it.

**Subagents obey this too.** A subagent's report back to the main agent carries the same three labels — an unlabelled subagent claim is exactly how a wrong "established fact" enters the pipeline (2026-08-17: the main agent asserted the Italian mainland was still contested; it was 120/120 held, and only the subagent's own reading caught it). When relaying, never upgrade a subagent's DERIVED into a MEASURED.

## One subject at a time

`QUEUE.md` (repo root) holds exactly one **ACTIVE** subject and everything else in **QUEUE**.

- Anything discovered mid-task that is not the ACTIVE subject goes to QUEUE, with what would close
  it. It does not get fixed on the way past. Opening a second subject means demoting the first to
  FILE with its state, not carrying both.
- A QUEUE row without a closing criterion is a wish, not a task.
- `python tools/check_worklist.py` enforces the one-ACTIVE rule, holds the **fix registry**
  (`tools/fix_registry.json`: one `Fix NN` = one row = one commit reachable from HEAD), and audits
  the campaign checklist for the failures that accumulate silently — its own docstring is the
  complete rule list.

## Agent Skills

`.claude/skills/` contains task-scoped skills that carry the working knowledge needed while editing. Claude Code loads them automatically; other agents should read the relevant `SKILL.md` directly. This file remains the authoritative system-ownership index — the skills route to it.

| Skill | Use it for |
| --- | --- |
| `.claude/skills/wa-orientation/SKILL.md` | Entry point. Repo layout, `replace_path` hazards, routing a task to its owner, validation matrix. |
| `.claude/skills/wa-engine-reference/SKILL.md` | How the ENGINE behaves, from outside this repo: the 1.19.2 install oracles, the defines override layer (`05_defines.lua` rebinds keys over `00_defines.lua` — an unnamed key keeps its vanilla value), Expert AI 5.0 as peer evidence, the wiki as hypothesis only, and the replace_path rule (is a base-game file LIVE in WA or deleted). Read it before asserting any engine fact. |
| `.claude/skills/wa-diagnosis/SKILL.md` | Symptom → the script line that causes it: the six-box output contract, the rule that a missing script line makes the report `INCOMPLETE DIAGNOSIS`, and the four techniques that each already caught a wrong conclusion here. Use it for every "why did the AI do X" question. |
| `.claude/skills/wa-pdxscript/SKILL.md` | PDXScript syntax, scopes, variables/arrays, `@` constants, `meta_trigger`, silent-failure pitfalls. |
| `.claude/skills/wa-ai-systems/SKILL.md` | `WA_AI_*` architecture: cadence, CONFIG archetypes, core/strategies/helpers/primitives split, military 4-layer model, railway queue. |
| `.claude/skills/wa-testing/SKILL.md` | Built-in `tests/` bundles and the `WA_TEST_*` scripted harness. |
| `.claude/skills/wa-tooling/SKILL.md` | Map generators, `ai_will_do` replacers, dry-run discipline. |
| `.claude/skills/wa-lessons-learned/SKILL.md` | Known gotchas (`references/lessons-log.md`) and the protocol for recording new ones. |
| `.claude/skills/wa-savegame-analysis/SKILL.md` | Reading HOI4 savegames: campaign identity, extracting variables/ideas/flags, cross-save trends. |
| `.claude/skills/wa-campaign-checklist/SKILL.md` | Scoring analysed test campaigns against the living verification checklist (`references/checklist.md`): WW2 arc, balance outcomes, fix probes, PASSED/FAILED streaks, retirement rules. Used in tandem with `wa-savegame-analysis`; every fix commit adds a probe here. |
| `.claude/skills/wa-constants-registry/SKILL.md` | How AI numbers are declared: script constants (`constant:cat.group.key`) vs the one case a file-scoped `@` is legal, the cross-format registry (`tools/constants_registry.json`) and `python tools/check_constants.py`, and the validated-contexts table (`constant:` does not work in `ai_strategy value =`). Run the checker before committing any change to `WA_AI_*` effects/triggers, `common/script_constants/`, `05_defines.lua`, `00_buildings.txt`, or `savegame.py`. |

## AI Design Philosophy

Three principles govern all new `WA_AI_*` code. When any other rule in this file conflicts with them, these win.

**1. Modular and setup-agnostic — no massive gaps.** AI behaviour must work in both historical and ahistorical games. Gate rules on *dynamic game state* — faction membership, active wars, ideology, doctrine archetype, geography, capability — never on the assumption that the historical script played out (Germany went fascist, France fell, Japan joined the Axis, the SOV–GER war happened). A rule that only fires on the historical path leaves the AI with *no behaviour at all* when the game diverges; every behaviour needs a generic fallback that produces sane play for any country in that situation. Historical-mode triggers may *tune* behaviour, but must never be the only path to having behaviour. Modularity is what makes this possible: build behaviour from archetype triggers and shared effects so a new situation is covered by composition, not by another hand-written special case.

**Two different axes are both called “historical”; never conflate them.** WA's Historical AI Difficulty (`WA_AI_DIFFICULTY_is_historical`) asks the AI to preserve the **sequence of WW2 events and campaigns**. Vanilla Historical AI Focuses (`is_historical_focus_on`) asks the game to preserve the **WW2 setup**. Choose the gate from the intended outcome, not from the word “historical”: an outcome that changes the setup uses the vanilla trigger. Canonical example: the Italo-Ethiopian war's victor changes the setup, so an AI-only Italian outcome assist uses `is_historical_focus_on`, not `WA_AI_DIFFICULTY_is_historical`. If the setup-versus-sequence classification is unclear, ask the user for examples before choosing either trigger.

**2. Country tags live in `WA_AI_CONFIG.txt` — nowhere else.** All country classification goes through archetype triggers in `common/scripted_triggers/WA_AI_CONFIG.txt`. Before writing `tag =` / `original_tag =` anywhere else, reformulate the rule as an archetype question ("is this a major Axis land power?") and add or reuse a CONFIG trigger. The Country layer (`WA_AI_MILITARY_COUNTRY_<TAG>*`, `events/WA_AI_<TAG>.txt`, `common/ai_equipment/<TAG>_*`) is the sole sanctioned exception, reserved for behaviour genuinely unique to one nation — treat every addition there as a design decision to justify, not a convenience, and ask first whether an archetype trigger would cover it.

**3. Change existing systems only with an impact analysis.** Existing behaviour is load-bearing, encodes fixes for cases that already broke (see the `# Fix NN:` convention), and misbehaves silently — regressions surface mid-campaign, not at parse time. Before modifying an existing trigger, effect, or strategy block: (a) enumerate every caller and reader (grep the name across `common/` and `events/`); (b) identify which countries, archetypes, and cadences reach it; (c) walk both the historical and an ahistorical scenario through the change; (d) check `wa-lessons-learned` and surrounding `# Fix NN:` comments for the case the current code encodes — send the decision to the `wa-lessons-reviewer` subagent (`.claude/agents/wa-lessons-reviewer.md`) rather than reading the 1800-line log inline, and — in parallel — to the `wa-architecture-reviewer` subagent (`.claude/agents/wa-architecture-reviewer.md`), which checks the change against the constants registry, the PC allocation model, the WA_TLM honesty rules and the editing rules below; treat a CONFLICT verdict from either as blocking; (e) state the regression risk explicitly in your summary; (f) if you claim a residual is "bounded", "self-healing" or "at most N", show the t0/t1/t2 table at the real cadences (pulse interval vs completion time, monthly save vs 2-day event) — the adjective without the table is how Fix 81 cut 1 shipped a stall it called bounded; (g) if a reporter or colleague proposed a fix and you are choosing another, quote their objection and write the sentence "mine covers it because …" — if it cannot be written, keep theirs. Prefer additive, gated changes over in-place rewrites of shared code paths. When the risk is unclear, diagnose first — the first hypothesis about AI misbehaviour in this codebase is usually wrong.

## Project Context

World Ablaze Beta is a Hearts of Iron IV gameplay overhaul mod. The repository root is the mod root loaded by HOI4.

Key metadata is in `descriptor.mod`:

| Field | Value |
| --- | --- |
| Mod name | `World Ablaze BETA LOCAL` |
| Game version (descriptor) | `1.18.0` — **stale metadata**, kept only because the descriptor says so |
| Actual engine version | `1.19.2.0` — the install every analysed campaign runs on (`launcher-settings.json`; see `wa-engine-reference`). Any engine fact is checked against 1.19.2, never 1.18 |
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
| Priority construction core | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`, `common/on_actions/WA_AI_misc_on_actions.txt`, `documentation/WA_AI_PC_QUEUE_FAIRNESS_DIAGNOSIS.md` | Dynamic project queue, factory assignment, progress tracking, and completion (weekly `WA_AI_PC_assign_factories` / `WA_AI_PC_update_project_progress`). **Queue fairness is the failure mode this system keeps having** — allocation is winner-takes-most from a priority-sorted queue, so bands below the head starve unless a lane reserves for them, and uncapped admission floods. Read the diagnosis doc before changing admission, allocation, or the stall sweep. |
| AI railway priority construction | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt`, `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_primitives.txt`, `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`, `common/on_actions/WA_AI_misc_on_actions.txt`, `documentation/WA_AI_RAILWAY_SYSTEM.md`, `documentation/WA_AI_LOGISTICS_MODEL.md` | Queue-based railway and naval-base construction. Keep route orchestration in `railway_core`, strategy selection in `railway_strategies`, calculations in `railway_helpers`, low-level checks in `railway_primitives`. **`WA_AI_LOGISTICS_MODEL.md` is the supply reference** — *too far* and *not enough throughput* are separate failure modes with separate levers; read it before writing any code that chooses a building LEVEL. |
| Map data, pathfinding, and math helpers | `common/scripted_effects/WA_AI_MAP_effects.txt`, `common/scripted_effects/WA_AI_MAP_province_connections.txt`, `common/scripted_effects/WA_AI_MAP_province_railway_connections.txt`, `common/scripted_effects/WA_AI_MAP_state_provinces.txt`, `common/scripted_effects/WA_AI_MAP_state_vp_provinces.txt`, `common/scripted_effects/WA_AI_MAP_province_coordinates.txt`, `common/scripted_effects/WA_AI_MAP_province_terrain.txt`, `common/scripted_effects/WA_AI_MAP_landmass_data.txt`, `common/scripted_effects/WA_AI_pathfinding_effects.txt`, `common/scripted_effects/WA_AI_MATH_effects.txt`, `tools/map_generators/`, `tools/run_generators.py` | Generated map lookup data supports province pathfinding, railway logic, landmass detection, state mappings, and distance calculation. Do not hand-edit generated `WA_AI_MAP_*` data files unless there is no viable generator path. |
| AI research weighting | `common/scripted_triggers/WA_AI_RESEARCH_*.txt`, `common/scripted_effects/WA_AI_RESEARCH_effects.txt`, `common/technologies/*.txt`, `tools/ai_will_do_replacer_all.py`, `tools/ai_replacer_base/`, `tools/REFACTORING_SUMMARY.md` | Research triggers drive `ai_will_do` blocks in technology files. Shared parser/generator code lives in `tools/ai_replacer_base/`. Preserve existing trigger logic when regenerating `ai_will_do`. |
| Resource needs and prospecting | `common/scripted_triggers/WA_AI_RESOURCE_NEEDS_triggers.txt`, `common/decisions/_resource_prospecting.txt`, `tools/needs_aware_generator.py`, `tools/prospecting_decision_analyzer.py`, `tools/ai_will_do_replacer_prospecting.py`, `PRESERVED_MODIFIER_FIX_FINAL.md` | Prospecting AI uses reactive, cooperative, and proactive layers. Preserve country-specific modifiers and indentation when regenerating decision `ai_will_do` blocks. |
| AI production and equipment behavior | `common/ai_strategy/WA_AI_PRODUCTION_*.txt`, `common/ai_strategy/World_Ablaze_production_air_strategies.txt`, `common/scripted_triggers/WA_AI_PRODUCTION_*.txt`, `common/scripted_effects/WA_production_strategy_effects.txt`, `common/ai_equipment/*.txt`, `common/decisions/z_WA_ai*.txt` | Handles production defaults, air-production flags, lend-lease production, equipment designs, and purge/fix decisions. Keep general production rules in shared WA_AI files and country-specific tuning in country-specific strategy/equipment files. |
| AI templates and division creation | `common/scripted_effects/WA_AI_TEMPLATES_effects.txt`, `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt`, `common/ai_templates/WA_AI_TEMPLATES_*.txt`, `common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt`, `common/on_actions/WA_AI_startup_on_actions.txt`, `common/on_actions/WA_AI_misc_on_actions.txt` | Template values are calculated at startup and monthly. Reuse existing template type codes and helper effects. Avoid adding one-off division templates outside the `WA_AI_TEMPLATES_*` pattern. |
| AI military fronts, invasions, and country strategy | `common/ai_strategy/WA_AI_MILITARY_DEFAULT_*.txt`, `common/ai_strategy/WA_AI_MILITARY_REGION_*.txt`, `common/ai_strategy/WA_AI_MILITARY_FACTION_*.txt`, `common/ai_strategy/WA_AI_MILITARY_COUNTRY_*.txt`, `common/ai_strategy/WA_AI_NAVAL_*.txt`, `common/scripted_triggers/WA_AI_MILITARY_triggers.txt`, `events/WA_AI_<TAG>.txt`, `documentation/WA_AI_MILITARY_SYSTEM.md`, `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` | Front archetypes and caps live in DEFAULT files; coalition behaviour in FACTION files; geography rules in REGION files; per-country tuning in COUNTRY files; naval-domain strategy files use the `WA_AI_NAVAL_*` prefix. **Read `documentation/WA_AI_MILITARY_SYSTEM.md` before adding or changing any `ai_strategy` block in `common/ai_strategy/WA_AI_MILITARY_*` or `common/ai_strategy/WA_AI_NAVAL_*`** - it is the authoritative spec for the 4-layer model (Default / Region / Faction / Country), domain split (FRONT / INVASION / NAVAL / DIPLOMACY / THEATRE / GARRISON), per-type Additive vs Exclusive overlap policy, and naming convention. The companion `WA_AI_MILITARY_TYPES_REFERENCE.md` lists every `type =` in use, where it currently lives, and its target layer. Do not duplicate a front rule per country if a front archetype or config trigger can express it. |
| Military theatre and campaign features (landing freeze, Italian theatre, East Africa, Ethiopian war, Tunis bridge, faction theatres, Commonwealth handoff, Afrika Korps window, Allied/Axis air policy, Mediterranean convoy interdiction, Mediterranean Fleet) | `documentation/WA_AI_MILITARY_SYSTEM.md` §10–§21 — each section names its files, its triggers and its checklist probe | One section per feature lives in the doc, not here. Shared invariants: **all behavioural switches live in the scripted-trigger "control panel" sections (`WA_AI_MILITARY_triggers.txt`, `WA_AI_LANDING_triggers.txt`) — change behaviour there, never by editing the strategy blocks**; everything keys on dynamic geography (owner / controller / faction / war), never on a tag, a date or an event flag. Faction theatres (§15) are GENERATED — change `tools/gen_ai_faction_theaters.py`, never the file. |
| AI force concentration (AIFC) | `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt`, `common/scripted_effects/WA_AI_AIFC_core.txt`, `common/scripted_effects/WA_AI_AIFC_helpers.txt`, `common/scripted_triggers/WA_AI_AIFC_triggers.txt`, `common/on_actions/WA_AI_misc_on_actions.txt` | The engine feature that lets the AI mass surplus divisions on a chosen offensive axis. **All behavioural switches live in `WA_AI_AIFC_triggers.txt`** — change behaviour there, never in the strategy blocks. Every boost must be paired with a suppression of everything outside the target set; unpaired AIFC values do effectively nothing. Full system reference: the header comment of `WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt`. |
| AI diplomacy, lend-lease, volunteers, laws, espionage, and leaders | `common/scripted_effects/WA_AI_lend_lease_effects.txt`, `common/scripted_effects/WA_AI_law_effects.txt`, `common/scripted_effects/WA_AI_espionage_effects.txt`, `common/scripted_effects/WA_AI_leader_recruitment_effects.txt`, matching `common/scripted_triggers/WA_AI_*_triggers.txt`, `common/ai_strategy/WA_AI_espionage_strategies.txt`, `common/decisions/categories/WA_AI_decision_categories.txt` | Shared AI behavior for diplomacy-facing systems; route recurring updates through the existing background events. **Volunteers and expeditionary forces are engine-driven, no WA scripted layer** (Fix 106): the levers are the `send_volunteers_desire` and `support` ai_strategy types plus the three `NDefines.NAI` expeditionary values. |
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
7. Add clear scripted triggers and effects instead of inline complex blocks. Good triggers answer one positive question, for example `WA_AI_should_prospect_resource_steel`. Good effects document expected scope, inputs, and outputs in comments. **Those comments are written for a human, and they stay short.** Keep at the code site only what a reader needs in order to touch the code safely: what the thing protects, the engine/system fact it assumes, how to tell that fact is gone — plus **the architecture decisions and the reasons behind specific choices**, including alternatives that were rejected and why. Everything else already has an owner: campaign measurements and per-country numbers belong to the `wa-campaign-checklist` item, durable rules and the history of reasoning that went wrong belong to `wa-lessons-learned`, and drafts, reviewer exchanges and "recorded so it is not reintroduced" notes belong nowhere. A 55-line header over a six-line trigger is a defect, not thoroughness (2026-08-17, `WA_AI_RESOURCE_NEEDS_triggers.txt`, trimmed in `cb0e5db39`). Finally, comments drift while code does not: verify any cadence, threshold or call site a comment states against the source before you rely on it — three separate comments called `WA_AI_needs_<r>` a *monthly* counter when its only writer runs on a ~2-day event.
8. Respect HOI4 scopes. Be explicit in comments for effects that require `ROOT`, `THIS`, `PREV`, state scope, country scope, or province/state ID variables. Avoid changing scope chains unless you have traced all callers.
9. Clean temporary state. Clear temp arrays and temp variables when existing patterns do so, and avoid persistent variables/flags unless they are part of the system state.
10. `@` constants are file-scoped in HOI4 script. A number that more than one file reads is a **script constant** (`common/script_constants/wa_ai_<system>.txt`, read as `constant:wa_ai_<system>.<group>.<key>` — validated 2026-08-16 for every variable context and the raw numeric triggers the AI uses; NOT for `ai_strategy value =`). Never redeclare a `@` in a second file — the checker reports it as an error; a `@` is fine only while a single file reads it. Numbers that also exist in another format (`05_defines.lua`, `00_buildings.txt`, `savegame.py` tables) are registered in `tools/constants_registry.json` so `python tools/check_constants.py` holds the contract; a comment alone is not a mechanism (see `.claude/skills/wa-constants-registry/SKILL.md`). A gate, cap or shared temp you add carries a header sentence naming what it protects and which fact it assumes, or it will outlive its reason.
11. Preserve naming prefixes. Use `WA_` for mod gameplay content, `WA_AI_` for AI systems, `WA_TEST_` for test harnesses, and `WA_TLM_` for save-visible telemetry (reserved, write-only — see `documentation/WA_TLM_TELEMETRY_SYSTEM.md`). Avoid generic names that can collide with vanilla or DLC content.
12. Preserve indentation style. Existing Paradox script uses tabs heavily. Do not reformat unrelated blocks, especially generated or parser-managed `ai_will_do` sections.
13. Avoid hand-editing generated files. Prefer changing the generator under `tools/` and regenerating output for map data, generated localisation, and generated `ai_will_do` where applicable.
14. Preserve existing modifiers and triggers during generation. The resource prospecting tooling has had bugs around nested modifier extraction and indentation; review `PRESERVED_MODIFIER_FIX_FINAL.md` before changing that pipeline.
15. Update documentation when changing a documented system. The railway system has docs and test cases under `documentation/`; keep them in sync with behavior changes.
16. **Never write a UTF-8 BOM into a `.txt` script file.** The HOI4 parser for `common/scripted_effects/` and `common/scripted_triggers/` treats the BOM as a stray token and desyncs on every `=` / `}` after it, so the whole file silently fails to load (seen 2026-08-15: `WA_AI_CONSTRUCTION_PRIORITY_core.txt` was re-saved with a BOM and the entire priority-construction system stopped parsing) — `python tools/check_worklist.py` now enforces this zone mechanically (`BOM-IN-SCRIPT`). Elsewhere the engine tolerates it (measured 2026-08-20: 213 vanilla-inherited BOMs under `common/units` and `events/` run in campaigns), but write every new file BOM-free anyway — BOM-free is safe in every folder, a BOM is safe only where already proven. Only `localisation/**/*.yml` requires a BOM. When in doubt, check the first three bytes (`EF BB BF` = bad).

## Generated And Tool-Managed Content

| Generated Or Tool-Managed Area | Source Tooling |
| --- | --- |
| `common/scripted_effects/WA_AI_MAP_*` lookup data | `tools/run_generators.py` and `tools/map_generators/*.py` |
| `common/ai_faction_theaters/ai_faction_theaters.txt` | `tools/gen_ai_faction_theaters.py` (`--dry-run` first) |
| Technology `ai_will_do` blocks | `tools/ai_will_do_replacer_all.py`, domain replacers, and `tools/ai_replacer_base/` |
| Prospecting decision `ai_will_do` blocks | `tools/needs_aware_generator.py`, `tools/prospecting_decision_analyzer.py`, `tools/ai_will_do_replacer_prospecting.py` |
| `_GENERATED_` localisation files | Existing generator workflow for their corresponding content |
| `.claude/skills/wa-constants-registry/references/registry.md` | `python tools/check_constants.py --markdown` from `tools/constants_registry.json` |

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
| Any `common/script_constants/` edit, `@` constant, `05_defines.lua`, `00_buildings.txt` cost/cap, `savegame.py` `_PC_*` table, or `WA_AI_*` effect/trigger commit | Run `python tools/check_constants.py` (exit 0 required; `--strict` for WARN-clean). Regenerate `.claude/skills/wa-constants-registry/references/registry.md` with `--markdown` when the manifest changed. For structural review of the change itself, run the `wa-architecture-reviewer` and `wa-lessons-reviewer` subagents in parallel. |
| AI railway, spirit, or stats behavior | Use vanilla HOI4 test bundles in `tests/wa_railway_strict_parity.txt`, `tests/wa_spirits_strict_parity.txt`, and `tests/wa_stats_strict_parity.txt`; inspect HOI4 `logs/tests/tests_<timestamp>.log`. |
| Any vendored engine doc under `common/**/documentation*`, or a claim citing one | Run `python tools/check_engine_docs.py` (exit 0 required). A doc listed in `tools/engine_docs_manifest.json` is SYNCED and citable; one reported `STALE` is a frozen copy of an older patch - read the install instead. Cite these files by **section name**, never by line number. |
| Any change to `tools/check_worklist.py` itself | Run `python tools/check_worklist.py --selftest` (exit 0 required). It rebuilds a clean fixture tree, mutates it once per rule, and fails if any rule does not fire on the input built to break it. **A new rule with no fixture fails the self-test** - that clause is the whole point. Three rules shipped inert on 2026-08-18 before this existed. |
| Any change to `QUEUE.md`, `references/checklist.md`, `tools/fix_registry.json`, or a `WA_TLM_*` write site | Run `python tools/check_worklist.py` (exit 0 required). It is also the pre-flight before scoring a campaign: an item flagged ORPHAN-FIX, STATUS-STALE or NEVER-SCORED is not scoreable as written, and scoring it produces a confident wrong result. |
| Any edit to `.claude/skills/**`, `.claude/agents/**`, or this file | Run `python tools/check_skill_refs.py` (exit 0 required). Every backtick-quoted repo path cited by the agent instructions must still exist; a legitimately absent file is named on a line that says so (deleted / install / vanilla / …). |
| Any new or modified `WA_TEST_*` console harness (a scripted effect that logs measurements) | Follow the **harness contract v1** in `wa-testing`: context header printed first (who/scope lines + known-false control + STOP rule, inline, never behind a shared helper), independent walk, own event file — never `events/wa_events_test.txt` (QUEUE 21). `python tools/check_worklist.py` enforces the header mechanically (`HARNESS-CONTRACT`). |
| Localisation/UI changes | Launch the game or inspect in-game UI where possible; missing localisation is not caught by Python tooling. |

## Safe Workflow

1. Identify the system from the table above.
2. Search for existing trigger/effect names and callers before adding new ones.
3. Make the minimal change in the file that owns the behavior.
4. Add or reuse scripted triggers/effects for reusable logic.
5. Update generated files only through their tooling when practical.
6. Run dry-run tools or in-game tests where feasible.
7. Document non-obvious new behavior near the owning system, not in unrelated country files.
