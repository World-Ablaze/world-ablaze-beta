# WA_AI air production — lines, budget, tech registry

Owning subject: `WORK.md` `[air-budget]`. Console harness: `event wa_airb.4 <TAG>`
(`common/scripted_effects/WA_TEST_air_budget.txt`, recipe in `events/wa_test_air_budget.txt`).

## 1. The model in one paragraph

The engine gives a land air TYPE the share `unit_ratio(type) / Σ unit_ratio(land types)` of the
planes it wants (`common/ai_strategy/documentation.info`, UNIT RATIOS / AIR — pure weights, no
base 100; carrier planes are a separate pool). WA therefore emits one integer WEIGHT per type
while the type has an open production LINE and retires it when it has none; the engine
normalises over the open set, so "fighter + cas = 60/40" and "fighter + cas + strategic =
43/29/29" are the same table with one more type open. A FIGHTER FLOOR raises the fighter weight
when the table alone would put fighters under 40 % of the pool.

## 2. Vocabulary

| Term | Meaning | Where |
| --- | --- | --- |
| **Type** | The engine role that receives a `unit_ratio`: `fighter`, `cas`, `tactical_bomber`, `strategic_bomber`, `naval_bomber`, `heavy_fighter`; carrier pool `cv_fighter`, `cv_cas`, `cv_naval_bomber`; support `scout_plane`, `air_transport` (min-factory lines, no weight). | DECLARATION |
| **Archetype** | An airframe inside a type. fighter = {small_fighter, small_fighter_multirole, small_fighter_interceptor}; tactical = {fast_bomber, medium_bomber (strike), medium_heavy_bomber (tactical)}; heavy_fighter = {medium_fighter, medium_fighter_multirole (attacker)}; strategic = {large, large_heavy}. | `common/units/equipment/plane_airframes.txt` (`allowed_types`) |
| **Line** | One `ai_strategy` block per archetype-and-mode, enabled by `WA_AI_PRODUCTION_should_open_<line>_line`. | `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_air.txt` |
| **Weight** | `constant:wa_ai_production.air_budget.weight_<type>`; share = weight / Σ open weights. | `common/script_constants/wa_ai_production.txt` |
| **Book** | `WA_AI_AIR_BUDGET_<type>`, the value currently applied to the role id (country variable, save-visible). | `common/scripted_effects/WA_AI_PRODUCTION_air_budget.txt` |
| **Purge book** | `WA_AI_PRODUCTION_AIR_open_<archetype>` country flag: the line funded this archetype at the last pulse. Its open→closed edge fires the archetype's `AI_purge_*` flag (1 day), which `can_be_produced` reads — the engine cancels the running lines. | `common/scripted_effects/WA_production_strategy_effects.txt` (`WA_aircraft_production_strategies`) |

## 3. Layers

| Layer | File | Content |
| --- | --- | --- |
| DECLARATION | `common/scripted_triggers/WA_AI_CONFIG.txt` § AIRFORCE | who uses which archetype / cap ladder (tags live here only) |
| DECLARATION | `common/script_constants/wa_ai_production.txt` `air` + `air_budget` | park caps, their `_reopen` bars (90 %), the weights, the fighter floor |
| DECLARATION | `tools/air_tech_registry.json` | per line, per tech tree, the rung the AI will fund (base / ad_tech); `exclude.airframes` = models the evaluator must never adopt |
| OBSERVATION | `common/scripted_triggers/WA_AI_PRODUCTION_air_tech.txt` (**GENERATED** by `tools/gen/gen_air_tech_gates.py`) | `WA_AI_PRODUCTION_has_worthwhile_<line>`, jet vetoes |
| OBSERVATION | `common/scripted_triggers/WA_AI_PRODUCTION_air.txt` (top) | park-below-cap pairs, bomber bases lost, own air arm |
| DECISION | `common/scripted_triggers/WA_AI_PRODUCTION_air.txt` | `should_build_<line>` (want) and `should_open_<line>_line` (want + industry band + exclusions) |
| CONSUMPTION | `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_air.txt` | one block per line: archetype factor at parity (100), category factor at parity (100), `min_factories 1`; CANCEL blocks (-1000) as complements. **No land `unit_ratio` here.** |
| CONSUMPTION | `common/scripted_effects/WA_AI_PRODUCTION_air_budget.txt` | `WA_AI_AIR_BUDGET_reconcile`: open types → weights → diff vs books → `add_ai_strategy unit_ratio ±delta` (meta_effect). Monthly + on_startup. |
| CONSUMPTION | `common/scripted_effects/WA_production_strategy_effects.txt` | the ~2-day pulse: land fighter park variable, BoB flag, purge books |
| Legacy | `common/ai_strategy/World_Ablaze_production_air_strategies.txt` | `air_factory_balance` per tag + date — the AIR SHARE of the industry, subject `air-share-windows`, out of this model |

## 4. Weights (owner ruling 2026-09-09)

| Type | Weight | Alone with fighter |
| --- | --- | --- |
| fighter | 60 | — |
| cas | 40 | 60 / 40 |
| tactical_bomber | 40 | 60 / 40 |
| strategic_bomber | 40 | 60 / 40 |
| naval_bomber | 10 | 86 / 14 |
| heavy_fighter | 15 | 80 / 20 |

Fighter floor 40 %: `w_fighter = max(60, others × 40 / 60)`. All six open: others 145 → fighter 97 →
40 %.

Carrier pool (separate engine pool, sized from deck capacity, no floor): `cv_fighter` 50,
`cv_cas` 30, `cv_naval_bomber` 50 — fighters and naval bombers at parity because the cv ratio also
sets the AI's deck composition (owner ruling 2026-09-09) — each funded while the country holds a deck AND its line is open
(`WA_AI_PRODUCTION_should_fund_cv_<type>_type`). Carrier naval bombers have their own line
(`should_open_cv_naval_bomber_line`: deck, naval rung, the `naval_cap_carrier` pair on the carrier
archetype, not the BoB programme) and their own purge key — the land naval line's archetype and
oceanic-enemy terms are about land-based maritime air and do not govern a deck.
A carrier navy outside the archetype (ENG) therefore weighs cv_naval_bomber only. **This is a
value change**: the removed static block gave every deck-holding navy cv_fighter 150 / cv_naval
100, so ENG's carrier pool went 60 % fighters; it is now 100 % naval bombers, the shape campaign
f9321934 measured as ENG's waste. The min-factory floors of `WA_AI_PRODUCTION_DEFAULT_cv_plane.txt`
(1 base per role, +6 for a fleet of ten decks and more) are gated on the same funded-type decision,
so floor, weight, CANCEL and purge share one decision. MEASURED (owner screenshot, ENG 1936): a
floor REQUESTS factories through the -1000 variant CANCEL, which is why a floor on a closed line
was a defect. A deck holder below its carrier-fighter rung builds no carrier fighters until the
rung (the `[rung-1940]` ruling: a pre-1940 model is not worth a factory) — a 1-factory deck-only
fallback was considered and not taken. Owner ruling Q8 (2026-09-09): carrier FIGHTERS follow the
deck — `should_build_cv_fighters` reads `needs_cv_planes` (holds a carrier), not the
`is_carrier_navy` archetype — so every deck holder with a worthwhile rung opens the line, gets the
weight and keeps the floors; the CANCEL and the purge follow the same decision. Carrier CAS stays
archetype-gated, and the archetype `WA_AI_CONFIG_AIRFORCE_is_carrier_strike_power` is EMPTY by
owner ruling Q9 (2026-09-09): no AI builds carrier CAS unless a nation is named there.
Pool separation (land vs carrier) is doc-sourced, ASSUMED until an `imgui` read shows the land
fighter share unmoved by the cv rows. Attacker belongs to heavy_fighter, not cas: MEASURED over every `ai_equipment` plane design,
air_attack per IC 1.91 (attacker) vs 1.90 (heavy fighter) vs 1.14 (CAS).

## 5. Closing a line

Two closures. **Hard** (archetype not allowed, tech not worthwhile, Battle of Britain programme,
bomber bases lost, own-air-arm test): the purge book cancels the running lines. **Cap** (park at its
cap): the line closes at the cap and REOPENS only at the `_reopen` bar (90 %), read through the purge
book — a Schmitt pair, so a mature park at its cap does not flip the line, and the monthly budget
entry, on every pulse. No book yet (fresh 1936, a save from a build before this system, a
human-to-AI switch): the trigger reads the reopen bar, so a park already in [90 %, cap) stays
closed with no purge until attrition takes it under 90 %; the pair reaches its fixed point on the
first pulse. Whether a cap closure should skip the purge (weight 0 and CANCEL only)
waits on the phase-0b measurement (`WA_TEST_AIRB_probe_cancel_tactical`).

## 6. Cadence and bounds

| t | Event | Line block | Purge book | Budget book |
| --- | --- | --- | --- | --- |
| t0 | decision flips (tech, cap, war) | same day (engine cadence, ASSUMED daily) | — | — |
| t1 | next pulse (MTTH 2 d; 7 d in performance mode) | — | edge: purge fires once | — |
| t2 | next monthly pulse | — | — | weight emitted / retired |

Worst case: a line cancelled up to one pulse late, never early; a new type weighs 0 for up to one
month (its `min_factories 1` keeps it alive).

**Entry accumulation.** One `unit_ratio` entry per type per change, at most one change per type
per monthly pulse: DERIVED hard bound 6 entries / month / country, 648 over a 108-month campaign
if every type flipped every month; the armour budget runs the same profile. The 17 park caps and
the Battle of Britain bar are Schmitt pairs (close at the cap, reopen at 90 %), so a park sitting
at its cap cannot re-emit. Three inputs are NOT paired and can oscillate — each is a decision, not
a park, so the pair would hide a real change:

| Input | Flips when | Purge (2-day pulse) | Budget (monthly) |
| --- | --- | --- | --- |
| `has_no_major_air_patron` | a major joins / leaves the alliance, `is_major` rank crosses | the patron-gated lines (cas, attacker, bombers) cancel on each close | ≤ 5 entries per flip pair |
| `num_of_military_factories > tier_*` band | bombing / conquest moves the count across 29 / 49 | same lines | same |
| jet-tech vetoes | once per campaign (monotone) | fast + strike cancel once | 1 entry |

Walk for the patron flip at the real cadences: t0 a major leaves → the bomber decisions read
closed the same day (engine cadence); t1 next pulse (~2 d) → purge books clear, running bomber
lines cancelled; t2 next monthly pulse → bomber weights retired (≤ 5 entries); t3 the major
returns → decisions open the same day, lines restart at the engine's pace; t4 next monthly pulse
→ weights re-emitted (≤ 5 entries). A country whose alliance changes every month is the
pathological case (10 entries / month); nothing in the mod produces it. **Save fingerprint**: a
country carrying hundreds of persistent `unit_ratio` entries has a flapping decision — read its
`WA_AI_PRODUCTION_AIR_open_*` flags across consecutive saves to find which line.

## 7. Retuning

- A weight or the fighter floor: `common/script_constants/wa_ai_production.txt` `air_budget` (the
  carrier min-factory floors are `ai_strategy` literals in `WA_AI_PRODUCTION_DEFAULT_cv_plane.txt`) — full restart,
  the reconcile diffs against stored books.
- A cap: `air` group, cap and `_reopen` together.
- A tech rung or an excluded model: `tools/air_tech_registry.json`, then
  `python tools/gen/gen_air_tech_gates.py` (`--check` in CI; `TREE-GAP` WARN = a tree deliberately
  barred from a line).
- Who builds what: `WA_AI_CONFIG_AIRFORCE_*` in `WA_AI_CONFIG.txt`.
- Never: a `unit_ratio` literal in the DEFAULT air file, a tag outside CONFIG, a hand edit of the
  generated trigger file.
