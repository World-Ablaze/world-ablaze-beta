---
name: wa-ai-systems
description: Architecture and design philosophy of the World Ablaze `WA_AI_*` systems — the startup/daily/weekly/monthly cadence, the WA_AI_CONFIG archetype triggers that replace country-tag lists, the core/strategies/helpers/primitives file split, the priority-construction and railway queue, the 4-layer military ai_strategy model, the map/pathfinding data layer, the rule that AI behaviour must work in historical AND ahistorical setups without gaps, and the impact-analysis checklist required before changing any existing AI system. Use this whenever you add, change, debug, or explain AI behaviour — construction, railways, military strategy, invasions, templates, production, research weighting, lend-lease, espionage — and whenever deciding *where* a new AI rule belongs. Getting the layer or the cadence wrong produces AI that looks fine in the diff and misbehaves for the entire campaign, so route through this before writing.
---

# WA AI systems

`AGENTS.md` holds the full system→files table. This skill is the architecture you need in your head while working: how AI code is scheduled, how it is layered, and where a new rule belongs.

Three design principles govern all AI work here (full statement in `AGENTS.md` § AI Design Philosophy):

1. **Setup-agnostic, no gaps** — behaviour must work in historical *and* ahistorical games; gate on dynamic game state, never on the assumption that history played out. See "Design for ahistorical games" below.
2. **Tags only in CONFIG** — country classification goes through `WA_AI_CONFIG.txt` archetype triggers; the Country layer is the sole, justified exception.
3. **Impact analysis before changing existing systems** — see "Changing an existing system" below.

## Naming tells you the layer

Every AI file name encodes its role. Read the name before the contents.

| Prefix / suffix | Meaning |
| --- | --- |
| `WA_AI_CONFIG_*` | Country classification triggers. **The only WA_AI file allowed to contain country tags** (its own header says so). |
| `WA_AI_<SUBSYSTEM>_*` | A subsystem: `CONSTRUCTION`, `MILITARY`, `NAVAL`, `RESEARCH`, `PRODUCTION`, `TEMPLATES`, `MAP`, `RESOURCE_NEEDS`, `DIVISION_CREATOR`… |
| `*_core` | Entry point and dispatch |
| `*_strategies` | High-level behaviour selection |
| `*_helpers` | Reusable calculations |
| `*_primitives` | Low-level state/province checks |
| `WA_AI_<TAG>.txt` in `events/` | Country-specific AI behaviour |

The railway system is the reference implementation of the four-part split. When a new AI system grows past one file, split it the same way — it keeps the call graph one-directional (`core → strategies → helpers → primitives`) and makes each layer independently testable.

## Scheduling: get the cadence right first

AI work is driven from on-actions, not from the effects themselves. Always identify the cadence before reading the logic — an effect that looks expensive is fine monthly and catastrophic daily.

| File | Role |
| --- | --- |
| `common/on_actions/WA_AI_startup_on_actions.txt` | One-time init: AI systems, templates, capitals, priority construction, map data. |
| `common/on_actions/WA_AI_misc_on_actions.txt` | The recurring pulses — `on_daily`, `on_weekly`, `on_monthly`. |
| `events/WA_AI_misc.txt` | Background AI events invoked from those pulses. |

Rules of thumb for adding recurring work:

- Everything under a pulse runs for **every AI country, every tick**. Gate on `is_ai = yes` and on the cheapest discriminating trigger first.
- Prefer a counter/interval inside the system over a more frequent on-action. The railway system runs weekly but only *acts* every 8 weeks at war / 12 at peace, by decrementing an interval counter.
- Country flags are used as cheap re-entry guards (`WA_AI_construction_timer` style). Clear them on the same path that sets them.

## Country classification — use CONFIG, not tag lists

`common/scripted_triggers/WA_AI_CONFIG.txt` is the central classifier. Before writing `original_tag = X` anywhere in a WA_AI file, look for an existing trigger there. Families present:

- Difficulty: `WA_AI_DIFFICULTY_is_historical`, `_is_competitive`, `WA_AI_CONFIG_cheats_enabled`
- Size: `WA_AI_CONFIG_is_major_country`, `_is_minor_country`
- Faction: `WA_AI_CONFIG_is_in_allies`, and `WA_AI_MILITARY_is_<faction>_member` in `WA_AI_MILITARY_triggers.txt`
- Doctrine: `_is_mobile_warfare`, `_is_deep_battle`, `_is_superior_firepower`, `_is_grand_battle_plan[_offensive|_defensive]`
- Airforce: `_is_strategic_bombing_airforce`, `_is_close_air_support_airforce`, `_AIRFORCE_uses_interceptors`, `_uses_multirole_fighters`, …
- Geography: `WA_AI_CONFIG_MILITARY_is_<region>`

If your rule genuinely needs a new category, **add the trigger to `WA_AI_CONFIG.txt`** and use it — that keeps the tag list in one auditable place instead of spreading across ~240 ai_strategy files.

Before writing a tag anywhere else, reformulate the rule as an archetype question: not "is this Germany?" but "is this a major Axis land power with a western border threat?". If the question can be asked that way, it belongs in CONFIG. The Country layer exists only for behaviour genuinely unique to one nation, and even then ask the archetype question first.

### Two meanings of “historical” — choose by outcome

| Intent | Trigger |
| --- | --- |
| Preserve the sequence of WW2 events and campaigns — WA Historical AI Difficulty | `WA_AI_DIFFICULTY_is_historical` |
| Preserve the WW2 setup — vanilla Historical AI Focuses | `is_historical_focus_on` |

Do not choose from the word “historical” alone. Classify the outcome first. If the outcome changes the setup, use the vanilla trigger: the victor of the Italo-Ethiopian war is the canonical example. If setup versus sequence remains ambiguous, ask the user for examples before choosing a gate.

## Design for ahistorical games

The mod supports historical and ahistorical setups; AI code that assumes the historical script leaves *gaps* — countries or situations with no behaviour at all — the moment a game diverges. This is the most common way otherwise-correct AI code fails in real campaigns.

Concretely:

- **Gate on state, not on story.** Faction membership (`WA_AI_MILITARY_is_<faction>_member`), `has_war_with`, ideology, capability, and geography are dynamic and survive divergence. "It is 1941 so Barbarossa is coming" does not. If an `enable = {}` only becomes true on the historical path, the block is a gap generator.
- **Every situation needs a floor.** For each behaviour, ask: *what does a country in this situation do if none of the specific rules match?* If the answer is "nothing", add or extend a Default-layer / generic fallback so the AI degrades to sane generic play instead of no play. This is why the layer model is Default-first: the Default layer *is* the gap prevention.
- **Historical tuning does not gate existence.** Either historical axis may adjust weights, timings, aggression, or a required setup outcome — but a behaviour that exists only under one mode needs an explicit justification, because the other mode still needs a generic fallback.
- **Test the divergent scenario in your head.** When writing or reviewing a rule, walk at least one ahistorical case through it: the target country never joins its historical faction, the war starts two years late, the historical victim already capitulated. If the rule misfires or goes silent, restate its gate in terms of the actual strategic situation.
- **Composition over special cases.** A new situation should be covered because archetype triggers and shared effects compose to cover it, not because someone hand-wrote a rule for that situation. If covering a scenario requires a new one-off block, check whether the real fix is a more general archetype trigger.

## Changing an existing system

Existing AI code is load-bearing and misbehaves silently — a regression surfaces as a country playing badly three in-game years later, not as an error at launch. Redundant-looking code usually encodes a case that already broke (`# [slug]` markers; historical `# Fix NN:` comments resolve via `documentation/FIX_HISTORY.md`). So changes to existing triggers, effects, and strategy blocks carry a burden of proof that new code does not.

Before modifying anything that already exists:

1. **Enumerate the blast radius.** Grep the trigger/effect/flag/variable name across `common/` and `events/` — every caller, every reader, every file that redeclares a related `@` constant. A trigger with six callers is six behaviours you are changing.
2. **Identify who reaches it.** Which countries, archetypes, and cadences hit this code path? A change that is right for majors may wreck minors sharing the same Default-layer block.
3. **Walk both setups through the change.** Trace the historical scenario *and* at least one ahistorical one. A fix tuned on a historical test game can open a gap in divergent games.
4. **Check the paper trail.** Surrounding `# [slug]` / historical `# Fix NN:` comments, the subject in `WORK.md`, `wa-lessons-learned`, and the system's doc in `documentation/` — the case the current code encodes is usually written down somewhere.
5. **Prefer additive, gated changes.** A new branch behind a discriminating trigger regresses nothing when the trigger is false; an in-place rewrite of a shared path puts every caller at risk. Reserve rewrites for when the analysis shows the old behaviour is wrong for *all* callers.
6. **State the regression risk.** Your summary of the change must say what could break and why you believe it won't — "no risk" is a claim to substantiate with the caller list, not a default.

If the change is motivated by observed misbehaviour, diagnose before implementing — confirm what the AI actually sees (control vs ownership, subject scoping, landmass boundaries) before changing what it does. The first hypothesis is usually wrong here.

## Military ai_strategy — the 4-layer model

**Read `documentation/WA_AI_MILITARY_SYSTEM.md` before touching any block in `common/ai_strategy/WA_AI_MILITARY_*` or `WA_AI_NAVAL_*`.** It is the authoritative spec; what follows is the shape, not a substitute.

Layers, highest-shared first:

| Layer | Files | Gated by | Tags allowed |
| --- | --- | --- | --- |
| Default | `WA_AI_MILITARY_DEFAULT_*.txt` | Archetype triggers | No |
| Region | `WA_AI_MILITARY_REGION_<NAME>.txt` | Geography triggers | No |
| Faction | `WA_AI_MILITARY_FACTION_<NAME>[_<DOMAIN>].txt` | `WA_AI_MILITARY_is_<faction>_member` (+ optional archetype refinement) | No |
| Country | `WA_AI_MILITARY_COUNTRY_<TAG>[_<DOMAIN>].txt` | `tag` / `original_tag` | Yes |

Domains, one file per domain: `_FRONT`, `_INVASION`, `_DIPLOMACY`, `_THEATRE`, `_GARRISON`, plus naval as `WA_AI_NAVAL_<LAYER>[_<TAG_OR_SCOPE>].txt`.

The decisions that actually matter when you write a block:

1. **Pick the highest layer that captures the rule's real scope.** Default > Region > Faction > Country. Push down only when the higher layer's trigger does not describe who the rule is for.
2. **Know whether the type is Additive or Exclusive.** Additive types (`front_unit_request`, `invade`, `conquer`, `area_priority`, `naval_avoid_region`, …) may be written by several layers and sum. Exclusive types (`front_control`, `protect`, `ignore`, `contain`, `ignore_claim`, `naval_invasion_focus`, `strike_force_home_base`, `*_defend_ally_borders`) must have exactly one writer per key; precedence is Country > Faction > Default and is currently enforced **by the author, not the engine**. The full per-type table is section 4 of the spec.
3. **Every block needs a real `enable = {}`.** `always = yes` is forbidden except with a `# always-on:` comment justifying why no dynamic gate applies.
4. **Every block needs a header comment** with `purpose`, `range`, `policy`, `domain`:
   ```txt
   # purpose: discourage USN from sailing into the Black Sea
   # range:   0 to +500
   # policy:  Additive per region
   # domain:  NAVAL
   WA_AI_NAVAL_COUNTRY_USA_avoid_black_sea = { ... }
   ```
5. **No `tag =` / `original_tag =` as a gating term outside Country files.** Tags appearing inside the `ai_strategy = {}` payload (`id = "USA"`, `target = ...`) are payload, not gating, and are fine. A single-tag exclusion such as `NOT = { tag = ITA }` is permitted; multi-tag OR-lists are not.
6. **Naval rules stay adaptive.** The layer owns the concern, but `enable` should also test readiness/opportunity triggers so the rule turns off when the strategic situation changes.

`documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` tells you every `type =` in use, where it currently lives, and its target layer. Consult it before inventing a new one.

## Priority construction and the railway queue

Deep reference: `documentation/WA_AI_RAILWAY_SYSTEM.md` (+ `WA_AI_RAILWAY_SYSTEM_EDGE_CASES.md`, `WA_AI_RAILWAY_SYSTEM_TEST_CASES.md`).

State is a queue array plus parallel indexed variables on the country:

```txt
arr: WA_AI_PC_queue                  # project IDs
arr: WA_AI_PC_target_state           # per-project target state
var: WA_AI_PC_target_province^X      # start province (railways)
var: WA_AI_PC_connect_province^X     # end province (railways)
var: WA_AI_PC_project_cost^X
var: WA_AI_PC_progress^X             # decrements weekly
var: WA_AI_PC_building_type^X        # 13 = railway, 14 = naval_base
var: WA_AI_PC_assigned_factories^X
var: WA_AI_PC_priority^X
```

Weekly cycle:

1. `WA_AI_PC_assign_factories` — reset assignments, allocate ~35% of available civs, then sort the queue by `WA_AI_PC_priority` and fill **winner-takes-most** from the top: each project takes `clamp(all remaining, 1, 20)`, so the highest-priority project absorbs the whole pool up to 20 and lower projects usually get nothing until it completes. Projects whose target state is hostile-controlled are skipped entirely (`Fix 34`) — their progress freezes rather than burning civ-weeks on a building that cannot spawn.
2. `WA_AI_PC_update_project_progress` — `progress -= speed * factories * 7`; complete at `<= 0`.
3. `WA_AI_PC_railway` — runs only when its interval counter hits 0 (8 weeks at war, 12 at peace), then queues new projects.

Three strategies live in `WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt`: **land war** (border enemy), **overseas war** (port-to-port supply chains), **pre-war preparation**. Route orchestration belongs in `railway_core`, strategy selection in `railway_strategies`, calculations in `railway_helpers`, province/state checks in `railway_primitives`.

Two things to know before editing:

- **AI numbers are script constants** — `common/script_constants/wa_ai_pc.txt` / `wa_ai_railway.txt` / `wa_ai_aifc.txt` / `wa_ai_posture.txt`, read as `constant:wa_ai_<system>.<group>.<key>` from every file (the railway control panel, PC bands / budgets / shadow prices, AIFC and posture thresholds). Retune there, full game restart to see it; never add a per-file `@` copy of a shared number. `python tools/check_constants.py` after touching them (skill `wa-constants-registry`).
- **Puppet territory is not yours.** `every_controlled_state` skips subject states; several fixes here (`Fix 25`/`Fix 27`) exist purely because of that. See `wa-lessons-learned`.

The historical `# Fix NN:` comments throughout `WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt` and `WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt` were a changelog — a later fix can revoke an earlier one (`Fix 27` revokes `Fix 25`); numbers resolve via `documentation/FIX_HISTORY.md` and are being collapsed into `# [slug]` markers. Read the surrounding comments before "simplifying" logic that looks redundant; it usually encodes a case that broke.

## Map data and pathfinding

`common/scripted_effects/WA_AI_MAP_*.txt` are **generated lookup tables** — province connections, railway connections, state→provinces, VP provinces, coordinates, terrain, landmass. Do not hand-edit them; change the generator under `tools/map_generators/` and regenerate (see `wa-tooling`).

Consumers: `WA_AI_pathfinding_effects.txt` and `WA_AI_MATH_effects.txt`. Pathfinder province-type parameter: `0`/`1` = allied + subjects, `2` = ROOT + allies + subjects.

## Other subsystems — where things live

| Subsystem | Owning files |
| --- | --- |
| Standard construction | `events/WA_AI_construction.txt`, `WA_AI_CONSTRUCTION_queue_functions.txt`, `WA_AI_CONSTRUCTION_building_adders.txt`, `WA_AI_CONSTRUCTION_scoring.txt`, `WA_AI_CONSTRUCTION_triggers.txt` |
| Templates / divisions | `WA_AI_TEMPLATES_effects.txt`, `WA_AI_TEMPLATES_triggers.txt`, `common/ai_templates/`, `WA_AI_DIVISION_CREATOR_effects.txt`, doc `WA_AI_DIVISION_TEMPLATES.md` |
| Production & equipment | `common/ai_strategy/WA_AI_PRODUCTION_*.txt`, `WA_production_strategy_effects.txt`, `common/ai_equipment/` |
| Research weighting | `WA_AI_RESEARCH_*` triggers/effects → `ai_will_do` in `common/technologies/` (tool-generated) |
| Resource needs / prospecting | `WA_AI_RESOURCE_NEEDS_triggers.txt`, `common/decisions/_resource_prospecting.txt` |
| Diplomacy, lend-lease, volunteers, laws, espionage, leaders | `WA_AI_lend_lease_effects.txt`, `_volunteer_`, `_law_`, `_espionage_`, `_leader_recruitment_` + matching trigger files |
| Historical capital ships | `events/WA_AI_Capitals.txt`, `WA_AI_Capital_Ship_effects.txt`, `common/ideas/_WA_ai.txt` |

## Deciding where a new rule goes

1. **Is it a country classification?** → `WA_AI_CONFIG.txt` as a trigger, then use it.
2. **Is it a military/naval `ai_strategy` block?** → pick the layer and domain per the spec; check the type's Additive/Exclusive policy.
3. **Is it truly one country's behaviour?** → `events/WA_AI_<TAG>.txt`, `WA_AI_MILITARY_COUNTRY_<TAG>_<DOMAIN>.txt`, `common/ai_equipment/<TAG>_*.txt`.
4. **Is it a reusable condition or action?** → `common/scripted_triggers/` or `common/scripted_effects/`, not inline.
5. **Does it need to run repeatedly?** → route through the existing pulse in `WA_AI_misc_on_actions.txt` with an interval counter; do not add a new on-action for it.
6. **Does it belong to a documented system?** → follow that system's file split and update its doc in `documentation/`.

If a rule would require duplicating a block per country, that is the signal to add an archetype trigger instead.

## Debugging AI behaviour

- Start from the on-action, not the effect, so you know the cadence and the gate.
- `common/scripted_effects/zz_debug_effects.txt` and `common/decisions/_debug_decisions.txt` contain existing debug harnesses — reuse them rather than writing throwaway logging.
- `log = "..."` with `[This.GetName]` / `[GetYear]` interpolation is the codebase's logging idiom; output lands in the HOI4 user directory `logs/game.log` — useful for **local** runs only.
- **Anything that must be verifiable from a cloud test campaign goes through WA_TLM** (`documentation/WA_TLM_TELEMETRY_SYSTEM.md`, effects in `common/scripted_effects/WA_TLM_core.txt`): a reserved, write-only `WA_TLM_*` variable namespace read out of savegames by the analysis agents (`savegame.py tlm`). Standing metrics are `WA_TLM_<system>_<metric>`; per-fix probes are `WA_TLM_r<NN>_*` keyed to their checklist item. The doc's §7 is the author checklist: register the metric, zero-init it, increment counters only on *verified* effect (never on code-path entry), pair stamps as `_first_t`/`_last_t`. Do not invent new ad hoc `*_dbg_*` families — the existing ones are legacy that retire with their checklist items. Gameplay/AI logic must never *read* a `WA_TLM_` value.
- **Run a diagnostic before implementing a fix.** In this codebase the first hypothesis about an AI misbehaviour is usually wrong — the scoping and control rules (puppets, controllers, landmasses) are subtler than they look. Confirm what the AI actually sees before changing what it does.
