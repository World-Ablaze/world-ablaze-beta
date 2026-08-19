# WA AI Military Types Reference

Per-`type` migration TODO list. Companion to `WA_AI_MILITARY_SYSTEM.md`. Read the system doc first for layer/domain/policy definitions.

## Canonical TYPE \u2192 DOMAIN mapping (post-Phase 6)

This is the **single source of truth** for which domain file every `ai_strategy` block belongs in. Military-domain files use `WA_AI_MILITARY_<LAYER>..._<DOMAIN>.txt`; naval-domain files use `WA_AI_NAVAL_<LAYER>[_<TAG_OR_SCOPE>].txt`.

| `type =` value | Domain | File suffix | Rationale |
| --- | --- | --- | --- |
| `front_unit_request` | FRONT | `_FRONT` | Sizes division allocation against an enemy front. |
| `front_control` | FRONT | `_FRONT` | Per-area passive/active mode for an existing front. |
| `front_armor_score` | FRONT | `_FRONT` | Front-line armour scoring. |
| `force_concentration_factor` | FRONT | `_FRONT` | AIFC master ratio. Percentage points added to define `AIFC_UNIT_RATIO_BASE` (0.15). Owned by the AIFC system - see below. |
| `force_concentration_front_factor` | FRONT | `_FRONT` | Front allocator concentration tuning. |
| `force_concentration_target_weight` | FRONT | `_FRONT` | Front allocator target weighting. |
| `garrison` | FRONT | `_FRONT` | Occupation force sizing. May move to `_GARRISON` if a country has many entries (currently none do). |
| `invasion_unit_request` | INVASION | `_INVASION` | Sizes the amphibious-invasion division pool. |
| `invade` | INVASION | `_INVASION` | Picks invasion targets. |
| `naval_invasion_focus` | INVASION | `_INVASION` | Invasion-precondition flag (boolean per target). |
| `naval_avoid_region` | NAVAL | `WA_AI_NAVAL_*` | Sea regions the fleet should avoid. |
| `naval_convoy_raid_region` | NAVAL | `WA_AI_NAVAL_*` | Sea regions where convoy raiding should be emphasised. |
| `naval_dominance` | NAVAL | `WA_AI_NAVAL_*` | Sea-region or AI-area naval dominance objective. |
| `naval_mission_threshold` | NAVAL | `WA_AI_NAVAL_*` | Generic naval mission threshold tuning. |
| `naval_invasion_dominance_weight` | NAVAL | `WA_AI_NAVAL_*` | Fleet emphasis on supremacy along active invasion paths. |
| `naval_invasion_support_priority` | NAVAL | `WA_AI_NAVAL_*` | Ranks sea regions for invasion support. **Real but undocumented** (string present in `hoi4.exe` 1.19.2; absent from both editions of `documentation.info`). **Zero uses in WA** - see the unused-lever note below. |
| `strike_force_home_base` | NAVAL | `WA_AI_NAVAL_*` | Designates a base as fleet home. |
| `strategic_air_importance` | NAVAL / AIR | `WA_AI_NAVAL_*` (sea-facing) or `_AIR` (land-theatre-facing) | Strategic air emphasis per strategic region. |
| `conquer` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: targets to subdue. |
| `antagonize` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: increase friction. |
| `protect` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: prioritise survival of an ally. |
| `contain` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: contain expansion. |
| `ignore` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: do not model as a threat. |
| `ignore_claim` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: do not press claim. |
| `declare_war` | DIPLOMACY | `_DIPLOMACY` | Country-only war declaration nudge. |
| `diplo_action_desire` | DIPLOMACY | `_DIPLOMACY` | Country-only diplomatic action weighting. |
| `diplo_action_acceptance` | DIPLOMACY | `_DIPLOMACY` | Country-only diplomatic action acceptance. |
| `dont_defend_ally_borders` | DIPLOMACY | `_DIPLOMACY` | Per-ally umbrella opt-out. Addressed by `id = <ally>`; expresses a stance toward an ally rather than sizing a front against an enemy. Grouped with `protect`/`ignore`/`force_defend_ally_borders` for the same reason. |
| `force_defend_ally_borders` | DIPLOMACY | `_DIPLOMACY` | Per-ally umbrella commitment. Same rationale as above. |
| `theatre_distribution_demand_increase` | THEATRE | `_THEATRE` | Coarse-grained regional emphasis. |
| `area_priority` | THEATRE | `_THEATRE` | Per-area priority (above the front allocator). |
| `put_unit_buffers` | THEATRE | `_THEATRE` | Per-state unit buffer reservations. |
| `spare_unit_factor` | THEATRE | `_THEATRE` | Strategic-reserve factor. |

Domain definitions:

- **FRONT**: how divisions are deployed along **existing** land borders. The front allocator's input set.
- **INVASION**: how the AI **creates new fronts** via amphibious assault. Pre-invasion staging through post-landing buildup.
- **NAVAL**: where the fleet operates, what it avoids, where it stages. Sea-domain emphasis.
- **DIPLOMACY**: posture toward **specific other countries** (allies or enemies, addressed by `id =` or `tag =`). Not the same as front sizing even when the eventual effect is on division placement.
- **THEATRE**: coarse-grained regional emphasis - which map-theatre to weight, per-state pooling, strategic reserves.
- **GARRISON**: per-state occupation force sizing for already-conquered territory. Currently rolled into FRONT; promoted to its own file only if a country has enough garrison rules to warrant it.

Note: `dont_defend_ally_borders` and `force_defend_ally_borders` operate on division placement (FRONT-domain mechanism) but express a stance toward an ally (DIPLOMACY-domain intent). Phase 6 routes them to DIPLOMACY for consistency with `protect`/`ignore` and because they are addressed by ally `id =`, the diplomacy-grammar form. See `WA_AI_MILITARY_SYSTEM.md` \u00a73 for the broader convention.

---

## Per-type migration history (Phase 1 snapshot, kept for reference)

This was a **snapshot** of `common/ai_strategy/WA_AI_MILITARY_*.txt` at the time of Phase 1. Counts have drifted across Phases 2-6. Keep current counts synchronized by statically reviewing `common/ai_strategy/WA_AI_MILITARY_*` and `common/ai_strategy/WA_AI_NAVAL_*` after future migrations.

## Inventory summary (Phase 1)

- 45 source files
- 28 distinct `type =` values
- 1791 total `ai_strategy` blocks

## Per-type table

For each type: total count, where it currently appears (counts per file), recommended target layer(s), and open questions or known issues.

### `front_unit_request` (469)

- Currently in: `FRONT_archetypes` (15), `FRONT_caps` (12), `FRONT_core` (4), every COUNTRY file with front content (USA 27, GER 84, SOV 60, AXIS 58, ALLIES 38, ENG 33, JAP 19, FRA 17, FIN 14, RAJ 13, CHI 12, CAN 12, RCZ 10, TUR 9, AST 6, ITA 6, PRC 5, GRE 3, RIT 3, CHINA_FRONT 3, ROM 1, SAF 1, NZL 1, POL 1, SPR 1).
- Target: Default for archetype/cap rules; Faction for coalition front shape; Country for tag-specific theatre adjustments.
- Notes: largest type by volume. Phase 4 should pull recurring patterns (e.g. minor-country front floors) out of country files into Default.

### `dont_defend_ally_borders` (228)

- Currently in: AXIS 59, SOUTH_AMERICA 46, ALLIES 28, GER 22, ITA 13, RCZ 11, USA 7, ENG 6, AST 3, CAN 1, CZE 3, FIN 3, CHI 3, CHINA_FRONT 2, BUL 1, POL 1, PRC 1, SIK 1.
- Target: Faction for intra-faction defaults; Country for overrides; Region for stay-at-home patterns (SOUTH_AMERICA).
- Policy: **Exclusive per ally**. Phase 5 must add `WA_AI_MILITARY_country_owns_dont_defend_<ALLY>` triggers.
- Open issue: AXIS file's 59 entries likely target specific allies and may need re-homing to country files in Phase 2.

### `front_control` (208)

- Currently in: GER 25, CHI 19, JAP 19, SOV 18, USA 17, AXIS 14, CAN 14, SPA 10, ITA 10, CHINA_FRONT 6, FIN 3, FRA 3, CZE 3, ALLIES 33, ENG 2, TUR 2, GRE 2, ROM 1, SAF 1, YUG 1, RAJ 1, SPR 4, DEFAULT_FRONT_control 2.
- Target: Default for the global passive/active baseline; Country for per-area overrides.
- Posture-gated writers: the exec/grind pairs `ALLIES_exec_vs_germany`/`_grind_vs_germany`, `AXIS_exec_vs_sov`/`_grind_vs_sov`, `CHINA_FRONT_exec_vs_japan`/`_grind_vs_japan` (each pair mutually exclusive by posture level), `ALLIES_downfall_push_FRONT`, `SOV_counterattack`, `JAP_chinese_war_4` (with `_chinese_war_3` as its posture-0 fallback), `ITA_north_africa_offensive_exec_FRONT` (via the controller-dynamic `WA_AI_MILITARY_north_africa_offensive_viable` trigger), and the Default-layer `EXEC_low_equipment_hold` brake all consume the weekly offensive-posture verdict - see section 9 of `WA_AI_MILITARY_SYSTEM.md` before adding new `execute_order = yes` blocks.
- Policy: **Exclusive per area**, resolved by TWO mechanisms - see `WA_AI_MILITARY_SYSTEM.md` §6 before adding a block.
  - The engine's own `priority` field (`common/ai_strategy/documentation.info` section `front_control`: default 0, higher overrides lower). 56 of 215 blocks set it, on a **semantic** ladder - brake 10000/500 (Default) > posture 300-340 (Faction) > routine 100 > unset 0. It is NOT a layer ladder: an ungated Faction posture block outranks a Country block.
  - The scripted ownership gates (`WA_AI_MILITARY_PHASE5_ownership_triggers.txt`, shipped `d149a204b`), which carry 7 `fc_*` slugs for this type: `fc_area_benelux` / `_italy` / `_japan` / `_north_france` / `_scandinavia` / `_south_france` (CAN, except `_japan` = JAP) and `fc_state_28` (GER).

### `support`

- Currently in: USA 31, SOV 5, SPR 5, GER 3, POR 3, CHI 2, HUN 2, JAP 2, ENG 1, FRA 1, `wa_default` 1, plus the two Faction-layer blocks added by Fix 106 in `WA_AI_MILITARY_FACTION_ALLIES_DIPLOMACY.txt`.
- Description **ASSUMED, provenance unknown**: *“Pursues AI to support a certain country within wars, sending lend lease, volunteers, or expeditionary forces.”* This was attributed to `documentation.info`; that string occurs nowhere in the install (`grep -r`, 0 hits) nor in the vendored copy - the wiki is the likely source. `documentation.info` lists the token and gives **no section and no example for it** - which is how it stays invisible. Grep the token list, not the worked examples, before concluding a script lever does not exist.
- Target: Country for a nation's own diplomatic preferences; **Faction for coalition behaviour** (a smaller member backing the major it fights under). Not Country-only despite sitting beside `declare_war` in the DIPLOMACY domain - see the note in `WA_AI_MILITARY_SYSTEM.md` §4.
- Policy: **Additive per target - ASSUMED, never measured** (see `WA_AI_MILITARY_SYSTEM.md` §4; `USA.txt`'s `USA_stop_uk_from_falling` already writes two `support` entries toward LUX and two toward GUA under one `enable`, so the sum is assumed there too). Values in use: 100 (nudge), 200, 500 (strong), -1000 (suppress), -2000 / -5000 (hard suppress: `wa_default` toward GER, GER toward SOV).
- Direction was one-way on the Allied side until Fix 106: every Allied block ran major → someone, none ran Allied minor → major. Minor → major blocks do exist elsewhere (`HUN.txt:131`, HUN → GER 200).
- **Unresolved:** creates vs ranks expeditionary intent - checklist R70.

### `invade` (197)

- Currently in: ALLIES 62, USA 54, JAP 25, SOUTH_AMERICA 19, GER 14, AST 6, ENG 4, GRE 4, SOV 4, GER 14, ITA 1, MAN 1, AXIS 1, RCZ 2, RAJ 0, CHINA_FRONT 0.
- Target: Faction for shared invasion targets; Country for tag-specific overrides.
- Notes: SOUTH_AMERICA's 19 `invade` entries are flagged for Region layer - check whether they are stay-home suppressors (negative values) or actual invasion targets.

### `put_unit_buffers` (151)

- Currently in: SOV 34, USA 21, ENG 17, GER 13, CHI 11, RAJ 9, ITA 7, FRA 5, FIN 3, AST 3, CAN 3, ALLIES 3, RCZ 6, JAP 6, MAN 2, RNC 2, SPR 1, MAL 1, GRE 1, HOL 1, POR 1, TUR 1.
- Target: Country (THEATRE domain). Faction layer should not set state-level buffers.
- Notes: high-volume per-state config. Candidate for tooling-assisted generation in a future phase.

### `area_priority` (124)

- Currently in: GER 20, SOV 19, JAP 17, ENG 15, USA 14, MAN 11, ITA 9, ALLIES 9, FRA 5, AXIS 2, CAN 1, RAJ 1, SAF 1.
- Target: Country (THEATRE domain) primarily; Faction for coalition focus.

### `naval_avoid_region` (91)

- Currently in: USA 67, RCZ 11, MAN 5, ALLIES 4, ENG 2, GER 2.
- Target: Country (NAVAL domain).
- **Known issue:** USA's 67 `naval_avoid_region` blocks are a candidate for tooling-assisted generation (one block per region, repetitive structure). Track for a Phase 4+ generator under `tools/`.

### `force_defend_ally_borders` (74)

- Currently in: ENG 14, CHINA_FRONT 13, USA 13, ITA 7, AXIS 3, FRA 3, CAN 3, JAP 2, MAN 2, SIA 2, FIN 0, AST 0, ALLIES 1, HUN 1, PRC 1, SAF 1, CHI 3, RAJ 3, COUNTRY_AXIS 3.
- Target: Faction for coalition defence patterns; Country for per-ally overrides.
- Policy: **Exclusive per ally**. Phase 5 mutual-exclusion needed.

### `conquer` (49)

- Currently in: SOV 13, JAP 12, ALLIES 4, USA 4, GER 3, FRA 2, SIA 3, ITA 2, AXIS 1, RAJ 1, HUN 1, CHINA_FRONT 1, PRC 1, MAN 1.
- Target: Country (DIPLOMACY domain). Faction may set bloc-wide conquer targets but most uses are country-specific.

### `invasion_unit_request` (42)

- Currently in: ALLIES 15, JAP 10, USA 7, GER 7, SOV 1, INVASION_budget 2.
- Target: Default for the global baseline (`INVASION_budget` -> `DEFAULT_INVASION`); Faction for coalition-wide modifiers (e.g. ALLIES); Country for tag-specific tuning.
- Policy: **Additive**. Multiple layers may contribute; the engine sums. ALLIES file's 15 entries can stay at the Faction layer when re-homed in Phase 2 (renamed to `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`).

### `garrison` (38)

- Currently in: FRA 15, GER 4, USA 4, SOV 4, ENG 2, ITA 2, RAJ 2, FIN 1, JAP 1, CHI 1, SPR 1, FRONT_archetypes 1.
- Target: Default for archetype floor (`FRONT_archetypes`); Country for state-specific overrides; `_GARRISON` domain file when a country has many garrison rules (FRA at 15 is the candidate).
- **Known issue:** `WA_AI_MILITARY_COUNTRY_SPR.txt:143-144` uses the WA-convention `value = -5000` (**not** engine-documented - the type has no engine section) force-off override. Preserve this pattern when migrating; do not collapse it into a regular garrison entry.

### `front_armor_score` (25)

- Currently in: SOV 13, GER 7, ALLIES 2 (`armor_to_european_front`: +500 GER / +100 ITA for western-allies majors), USA 1 (`armor_europe_first`: -300 JAP).
- Target: Country (FRONT domain); Faction for coalition-wide armour steering.
- Note: this type was inert mod-wide until commit af705e640 added `front_role_override = offence` to the armour/mechanized/motorized role blocks in `common/ai_templates` - the engine keys armour front assignment on those roles.
- **`front_armor_score` is id-keyed only.** It accepts `id = "TAG"` and nothing else - no `tag`, `state`, `strategic_region`, `area`, `country_trigger` or `state_trigger`. The DEFAULT-layer `AIFC_armor_follows_schwerpunkt` entry tried to target it with `country_trigger` and never parsed (`ai_strategy.cpp: Unexpected token: country_trigger`). `front_control`, `front_unit_request` and `invasion_unit_request` take the generic country/state targeting fields (`common/ai_strategy/documentation.info` sections `front_control` + `front_unit_request`) - **and so do both targeted `force_concentration_*` types**, which document the full set `tag` / `state` / `strategic_region` / `area` / `country_trigger` / `state_trigger` (`_front_factor` additionally `ratio`). The earlier claim that they took "only `state_trigger` in addition" came from reading the 2023-07 copy, which has no force_concentration section at all; the AIFC header (`WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt`) always had it right. **Consequence:** AIFC Layer 4's `state_trigger` + encoded `*_ref` array route is not the only option - `country_trigger` and `tag` are documented on both types and need no encoded scope reference.
- The tag-free AIFC armour steering (+400 toward the sector enemy / -150 toward every other war enemy) is therefore **scripted, not an ai_strategy block**: `WA_AI_AIFC_armor_reconcile` in `common/scripted_effects/WA_AI_AIFC_helpers.txt` emits `add_ai_strategy = { type = front_armor_score id = <runtime tag> ... }` via `meta_effect` weekly, retiring entries by exact negation (there is no `remove_ai_strategy`). Switch: `WA_AI_AIFC_armor_steering_enabled` in `WA_AI_AIFC_triggers.txt`. These scripted instances stack additively with the static SOV/GER/ALLIES/USA entries above, sitting below them by design.
- **The scripted instances accumulate in the save and the old "a few hundred, bounded" claim is measured false.** Campaign `7c7803a8`: USA's `persistent_strategy type=83` list ran 0 → 240 → 339 → **517** entries between 1942.6 and 1944.6 (ITA 357, GER 219; ENG stable at 84, JAP 38, FRA 18). The driver is not enemy change - it is `WA_AI_AIFC_select_sector` clearing `WA_AI_AIFC_sector_enemy` at its head and again on its no-anchor exit, so a **transient** selection failure makes the reconcile retire the whole suppression book and reinstall it the following week: ~56 entries per failure on a country tracking 28 enemies. The NET per country stays correct (+400 sector enemy / -150 other enemies), so armour scoring is not mis-steered; the cost is list length, growing ~250/year on a tag whose selection is unstable. Instrumented as `WA_TLM_r67_aifc_arm_*` (checklist R67); a retirement grace window is the candidate fix but must be sized from the measured mean episode length, not from the entry count.

### `strategic_air_importance` (40)

- Currently in: FRA 1, JAP 2, SOV 1 (Country legacy), the NAVAL files (sea-facing), 10 generic theatre blocks in `WA_AI_MILITARY_DEFAULT_AIR_theatres.txt`, **25 Faction-layer blocks in `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt`** (5 Reich-ladder + 8 Phase 7d + 12 home-only, 2026-08-18), **4 in `WA_AI_MILITARY_FACTION_AXIS_AIR.txt` and 1 in `WA_AI_MILITARY_COUNTRY_GER_AIR.txt`** (Phase 7e). **ENG.txt and GER.txt carry none since Phases 7d/7e (2026-08-16).**
- Target: Country (NAVAL when sea-facing); Default for the generic land-theatre pulls (AIR domain); Faction for coalition policy (bombing campaign, Channel/Sicily pushes, standing avoidance).
- **What the type does — read before writing a value.** The engine ORDERS strategic regions by importance (engine terms + this value) and fills them in that order with the planes it REQUESTS; the request comes only from engine terms (own combats/armies in the region, enemy planes in a combat region, enemy factories for strategic bombing, ships), never from this value. A positive value therefore decides *where already-requested planes go*; it cannot stage wings into a theatre before the ground war creates the request (verified on `a232d96c`: every USAAF wing in the continental US at mission `type=0` while Northern France read +250k; USA planes over the theatre tracked USA divisions in France — checklist R15 RECUT 2026-08-16). Engine-side ordering terms: own combats x100, own armies x25; a stocked main front in active combat scores ~35,000.
- The Default layer (`WA_AI_MILITARY_DEFAULT_AIR_theatres.txt`) provides the standing +50,000 "base air where your side is fighting" pull per contested theatre region, gated by `WA_AI_MILITARY_AIR_theatre_contested_*` (dynamic both-sides-control-land detection, no tags). The Faction-layer emergency pushes (+100k Sicily / +200k Channel, home-islands threat) and the retuned suppression tiers (-2k..-40k) compose with it; the remaining FRA/JAP/SOV Country legacy blocks still carry -500k black holes and a date (`FRA_dont_suicide_your_airforce`, `date < 1942.1.1`) — next conversion candidates.
- **Phase 7e (2026-08-16) — the GER.txt air family split between `WA_AI_MILITARY_FACTION_AXIS_AIR.txt` and `WA_AI_MILITARY_COUNTRY_GER_AIR.txt`.** Faction (any Axis member, `WA_AI_MILITARY_is_axis_member`): `battle_of_france_no` → `WA_AI_MILITARY_AXIS_AIR_western_front_not_open` (−20k on 19/239/20/290 while an enemy holds the Channel coast and our side holds nothing in WEU — was −500k below `date < 1940.5.1`); the −1M half of `battle_of_france_yes` → `_avoid_unfronted_western_france` / `_avoid_unfronted_southern_france` (−40k per region while contested and our side holds no state of that region; 11 Southern Norway DROPPED — the −1M there was live during Weserübung and cancelled the Scandinavia pull); `battle_of_britain_no` → `_avoid_british_isles` (−20k Channel/Southern Bight/North Sea, −40k British regions + Atlantic approaches, off during `WA_AI_MILITARY_AIR_battle_of_britain_window` = our side holds the coast with no enemy on it + enemy holds London + no Comintern war, or `sealion_active`; was −500k/−1M behind `date > 1940.11.1` and a seven-tag list). Country GER: `ger_defend_against_bombing` → `WA_AI_MILITARY_GER_AIR_reich_air_defence` (+50k on 6/7/8 — HEAD carried +10k, raised by the modder the same day — armed while an enemy fields > `@WA_AI_AIR_BOMBER_NUCLEUS` strategic bombers, released below `@WA_AI_AIR_ENEMY_BOMBER_ARM_OFF` 199 via explicit `abort`, replacing `has_war_with = SOV` + `fall_of_france`); the +100k half of `battle_of_france_yes` was NOT carried over — the +50k contested pull composed with the −40k unfronted south/west already gives the north/south differential, and no dateless gate tells the 1940 offensive from a 1944 defence of the same regions; its **−1M on 5 Benelux removed outright** (unrecorded purpose; it forbade the Luftwaffe Belgian airspace through the whole 1944 campaign — `a232d96c` GER 0 planes on region 5 at every sample). Switches in `WA_AI_MILITARY_triggers.txt` under "AIR - Axis western front / Battle of Britain / Reich air defence". `WA_AI_MILITARY_GER_battle_of_britain_yes_FRONT` (FRONT domain, `date < 1940.11.1`) is left as is — its date could be swapped for `WA_AI_MILITARY_AIR_battle_of_britain_window` in a FRONT-domain pass.
- **Phase 7d (2026-08-16) — the ENG.txt Allied family relocated to `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt`.** `battle_of_britain_priority` → `WA_AI_MILITARY_ALLIES_AIR_home_islands_invasion_threat` (+200k on 1/2 while a HUMAN enemy holds the far shore, was +500k and `GER = { is_ai = no }`); `Allies_avoid_bombing_occupied_allies` + `Allies_bomb_germany` → `_avoid_occupied_europe` (one gate, summed values); `Allies_dont_logi_strike_during_bob` → `_channel_coast_no_foothold` (-20k, was -500k re-arming after 1944.7.1); `Allies_dday_air` → `_channel_coast_push` (+200k on 239 while an overseas Allied army is STAGING in a Channel county — `divisions_in_state > @WA_AI_AIR_STAGING_DIVISIONS_ON` 6 to arm, released below `_OFF` 2, capital not in the British Isles, or an ally does — or the Allies hold the far shore; explicit `abort`; was the 1944.2.1–7.1 date pair); `Allies_husky_air` → `_sicily_landing_push` (+100k on 238 from the Sicily foothold until the mainland toe falls; was 1943.7–11); `Allies_avoid_bombing_occupied_uk` → `_home_islands_lost` (London AND Birmingham enemy-held; was any of 20 states); `Allies_bomb_germany_2` → `_avoid_italy_no_foothold`; `Allies_dont_bomb_random_places` → `_avoid_out_of_theatre`. Pushes gated on `WA_AI_MILITARY_is_allies_member` (any member); suppressions additionally `allowed` on the CONFIG archetype `WA_AI_CONFIG_MILITARY_is_western_allies_air_power` (the legacy eight tags, so no continental member is told to avoid its own homeland) with a France capital exclusion; switches in `WA_AI_MILITARY_triggers.txt` under "AIR - Allied Western Europe / Mediterranean state triggers".
- **Faction layer — a small Allied air force stays over its own soil (2026-08-18).** Twelve `WA_AI_MILITARY_ALLIES_AIR_home_only_*` blocks in `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt` write -300,000 on every foreign air theatre for an Allies member fielding <= 399 aircraft, leaving only the theatre containing its own capital untouched (per-block `capital_scope` exclusion, so no archetype gate and no tag). Region set: the ten Default air theatres, plus the British Isles (1/2/3/4) and the Reich ring (6/7/8/294/38) that this file's own pushes target; East Africa is excluded because no scripted pull points there. -300,000 is the dominance tier - it has to beat the +250,000 peak stack (Channel push +200k composed with the contested western-Europe pull +50k) or it does nothing. Two bars with hysteresis (`@WA_AI_AIR_HOME_ONLY_ARM` 399 / `@WA_AI_AIR_HOME_ONLY_RELEASE` 499) so a country building or attriting around the bar does not rebase its whole force every 5-day air-priority update; the family is off entirely for a government that does not control its own capital, which would otherwise be told to avoid the only airspace it can reach. Switches live in `WA_AI_MILITARY_triggers.txt` under "AIR - a small Allied air force stays over its own soil".
- **Faction layer — the Allied Reich bombing ladder.** `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt` owns the western coalition's avoidance of German air space (strategic regions 6/7/8/296 near ring, 294/38 deep ring). Its three blocks are rungs on a **deployed-strategic-bomber count**, not dates: each enables below its own threshold and aborts above the next one, so the net suppression walks from -60,000 down to 0 (near ring) / -80,000 down to 0 (deep ring) as the coalition arms, with hysteresis at every boundary. Thresholds (299/450/700/900, grounded in campaign `973154a7`) and the Reich ring state lists live in `WA_AI_MILITARY_triggers.txt` under "AIR - Allied Reich bombing ladder" — change the campaign there, never in the strategy blocks. All three rungs also abort on `WA_AI_MILITARY_AIR_theatre_contested_germany`, the setup-agnostic replacement for the old `date > 1944.2.1` backstop: `strategic_air_importance` suppresses *every* mission in a region, so it must lift the moment friendly armies are fighting on German soil. This file replaced legacy ENG.txt `Allies_bombing_germany_is_too_costly`, `allies_avoid_bombing_austria_prussia` and `ENG_FRA_allies_avoid_bombing_GER` (Phase 7c).

### `antagonize` (8)

- Currently in: JAP 3, MAN 1, AXIS 1, SIA 2, ITA 1.
- Target: Country (DIPLOMACY domain). The single AXIS entry should be re-homed.

### `naval_invasion_focus` (6)

- Currently in: JAP 6.
- Target: Country (INVASION domain).
- Policy: **Exclusive**. Single owner today (JAP), so no current conflict.

### `theatre_distribution_demand_increase` (6)

- Currently in: USA 1, ENG 1, JAP 1, SOV 1, CAN 1, ALLIES 1.
- Target: Country (THEATRE domain) for tag-specific; Faction for ALLIES.
- `value` is an **absolute count of divisions** added to the theatre's demand, not a percentage
  (`documentation.info` section `theatre_distribution_demand_increase`). Live values are 4-10.
- **`id` is a STATE, and the theatre it lands on is decided by `common/ai_faction_theaters`.**
  Before WA took ownership of that folder (2026-08-18) four of these six writers were wrong -
  three resolved to no theatre and Canada's European demand landed on the Middle East, because
  vanilla's theatres named region ids against a map WA had re-cut. Adding a writer here means
  checking which theatre its state resolves to; the chain and the before/after table are in
  `WA_AI_MILITARY_SYSTEM.md` §15.

### `ignore` (5)

- Currently in: FRA 2, ITA 1, GER 2.
- Target: Country (DIPLOMACY domain).
- Policy: **Exclusive per target**.

### AI Force Concentration (AIFC) - all three `force_concentration_*` types

The AIFC types are owned by a dedicated subsystem and should not be added ad hoc. Before adding any
`force_concentration_*` entry anywhere, read the system reference in the header of
`common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt`.

- Generic layer (doctrine ladder, posture, dynamic sector consumption):
  `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt`
- Sector selection (weekly, scripted): `common/scripted_effects/WA_AI_AIFC_core.txt`, `..._helpers.txt`
- All behavioural switches: `common/scripted_triggers/WA_AI_AIFC_triggers.txt`
- Country overrides that survive: GER (`GER.txt` legacy + `..._COUNTRY_GER_FRONT.txt`), FRA
  (`..._COUNTRY_FRA_FRONT.txt`). GER's entries are still split across the legacy vanilla-named file and
  its `_FRONT` file; consolidating them is outstanding work.

**The pairing rule.** `force_concentration_front_factor` and `force_concentration_target_weight` are
relative scores. A boost with no matching suppression of the alternatives does close to nothing - this is
why WA's pre-rework `+200` and `+80` entries produced no visible behaviour. Pair every new boost with a
suppression of everything outside the intended target set.

### `force_concentration_target_weight` (5)

- Currently in: GER 4, FRA 1.
- Target: Country (FRONT domain).

### `protect` (4)

- Currently in: USA 1, ENG 1, JAP 2.
- Target: Country (DIPLOMACY domain).
- Policy: **Exclusive per target**.

### `strike_force_home_base` (4)

- Currently in: ITA 4.
- Target: Country (NAVAL domain).
- Policy: **Exclusive per region**.

### `contain` (3)

- Currently in: ALLIES 2, USA 1.
- Target: Faction (DIPLOMACY) for ALLIES; Country for USA.
- Policy: **Exclusive per target**.

### `spare_unit_factor` (2)

- Currently in: USA 1, CHINA_FRONT 1.
- Target: Country (THEATRE domain) for USA. The CHINA_FRONT entry sits inside `WA_AI_MILITARY_CHINA_FRONT_sic_support_chi_against_japan` and is **country-specific** (gated by `tag = SIC`); see "Cross-cutting issues" below.

### `force_concentration_front_factor` (2)

- Currently in: GER 1, FRA 1.
- Target: Country (FRONT domain).

### `declare_war` (2)

- Currently in: GER 1, ITA 1.
- Target: Country only (DIPLOMACY domain).

### `diplo_action_desire` (1)

- Currently in: BUL 1.
- Target: Country only (DIPLOMACY domain).

### `diplo_action_acceptance` (1)

- Currently in: BUL 1.
- Target: Country only (DIPLOMACY domain).

### `ignore_claim` (1)

- Currently in: ITA 1.
- Target: Country (DIPLOMACY domain).
- Policy: **Exclusive per target**.

---

### `naval_invasion_support_priority` (0) - a real lever WA does not pull

- **Currently in: nowhere.** Zero occurrences in `common/ai_strategy/`.
- **Status: real but undocumented.** Absent from the 2024-11 and the 2023-07 editions of
  `documentation.info`, so a doc-only check reads it as invented. The literal string is present in
  `hoi4.exe` (1.19.2) - measured against a control string, which is not - and vanilla's own
  `common/ai_strategy/ENG.txt` writes 7 entries of it.
- **Shape, from vanilla's usage only:** `id = <strategic region>`, `value` a weight on the
  invasion-support objective for invasions whose path crosses that region. Vanilla writes `200` on the
  five Mediterranean regions to hold ENG's invasions there before 1943.6.1, then `25` and `-100` on the
  Bismarck Sea to keep ENG out of Pacific invasions. **ASSUMED** beyond that - no engine text describes
  the parameter, and nothing in WA has ever exercised it.
- **Why it matters here:** `common/ai_strategy` is a `replace_path` folder, so vanilla's ENG.txt does
  not run.
- **DECISION 2026-08-18: not adopted, and the gap is smaller than "replaced with nothing".** WA does
  sequence invasion theatres - it just does it on a different axis. Measured in
  `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`: 76 `invade` entries across 12 blocks, **7 of the 12
  date-gated**, arranged as explicit hold/fire pairs - `ALLIES_norway_invasion_hold_I` /
  `_fire_I`, `ALLIES_dday_hold`, `ALLIES_no_italy_invasion_early`,
  `ALLIES_war_against_ITA_north_africa_first`. Values run -5000 / -2000 (50 entries) / -500 / +500 /
  +1000 / +4000. Mod-wide: **351 `invade`, 46 `invasion_unit_request`, 6 `naval_invasion_focus`,
  zero of this type.**
- **The two axes are not the same, and that is the whole trade.** `invade` keys on the **target
  country**; `naval_invasion_support_priority` keys on the **sea region the invasion path crosses**.
  Route-keyed expresses "nothing in the Pacific until the Mediterranean is done" in one entry
  (vanilla writes exactly that: five Med regions at 200, Bismarck Sea at 25 then -100). Target-keyed
  expresses it by naming every country in the theatre - which is what WA's 50 `-2000` entries and
  the 16-target `ALLIES_minor_allies_dont_invade` block are doing.
- **So: enumeration works, and adopting the type would add a mechanism where nothing is broken** -
  the Fix 77 lesson. Revisit if the enumeration keeps growing, or the day a rule needs to be
  expressed about a *route* whose destinations are not enumerable in advance. Until then the entry
  here exists so the next reader knows the lever is real, undocumented, and deliberately unused.

## Phase 4 audit: cross-layer duplication is mostly by-design

Phase 4 was originally scoped to "consolidate cross-layer duplicates" — i.e. find cases where the same `(type, key)` block appears in DEFAULT/REGION/FACTION/COUNTRY and lift the duplicate to the highest shared layer. A scan across the 94 post-Phase-3 ai_strategy files (1826 indexed `ai_strategy = {}` blocks) found 153 cross-layer `(type, key)` groups. Closer inspection showed the headline number is misleading.

### Breakdown of the 153 cross-layer groups

| Type | Groups | Engine policy | Phase 4 actionable? |
| --- | --- | --- | --- |
| `dont_defend_ally_borders` | 58 | Binary per block (>0 on, <=0 off); **engine silent on multi-writer** - "highest value wins" was an inference, withdrawn | No - distinct rules from distinct sources targeting the same ally |
| `front_unit_request` | 35 | Additive | No - sums are intended |
| `invade` | 32 | Additive per target | No |
| `front_control` | 7 (128 instances) | Exclusive per area | Cannot be safely auto-deduped (see below) |
| `area_priority` / `put_unit_buffers` / `conquer` / `naval_avoid_region` / `strategic_air_importance` / `invasion_unit_request` / `garrison` / `spare_unit_factor` | 13 total | Additive | No |
| `force_defend_ally_borders` | 4 | Exclusive per ally | Reviewed; gates are meaningfully distinct |
| `contain` | 1 | Exclusive | Reviewed; legitimate |

### Why mechanical de-dup does not apply

1. **Cross-layer Exclusive entries are not duplicates.** For example, `dont_defend_ally_borders id = FIN` appears in 15 distinct blocks across REGION/FACTION/COUNTRY. They are gated on different sources (e.g. `BUL_stay_out_of_finland`, `GER_army_group_finland_does_not_exist`, `AXIS_hungary_stop_crowding_up_the_soviet_line`, `SOUTH_AMERICA_stay_in_south_america`). Each is the right rule for its source country/region. Merging them would either lose semantics or require conditional payloads that the `ai_strategy` DSL does not support. **Caveat:** the argument used to lean on a "highest value wins" engine semantic that the engine never states - it documents only the per-block binary. If the engine sums before thresholding, a -100 suppressor and a +100 activator cancel, and these 58 groups would need review rather than a pass.
2. **`ai_strategy` blocks are definitions, not effects.** They cannot be emitted from scripted effects (verified: zero `ai_strategy = {` occurrences in `common/scripted_effects/`). The only consolidation tool is collapsing the *outer* containing block by widening `allowed`/`enable` and accepting any per-tag tweaks as cross-cutting noise.
3. **Near-duplicate outer blocks have meaningful gate differences.** The 5-block `AXIS_*_stop_crowding_up_the_soviet_line` family is the closest candidate for collapse: all five share ~9 `dont_defend_ally_borders` entries plus ~4 `front_unit_request` entries. But each variant has at least one meaningful difference - Romania has an extra `NOT = { has_defensive_war_with = SOV ... }` clause, Bulgaria omits all `front_unit_request` and the `support_requested_by_germany` exclusion, Italy adds `crimea` plus ROM/BUL to the ally list, the "iberian" general variant uses a different gate. Forcibly merging them would either lose these differences or require complex conditional payloads.
4. **`front_control` cannot be safely auto-deduped.** All 128 instances collapse to `KEY=None` in the scanner because `front_control` is gated on embedded `country_trigger`/`state_trigger`/`ordertype` blocks rather than a top-level `id`/`area`/`target` field. The blocks are Exclusive-per-area in the spec, but mechanical overlap detection requires evaluating those embedded gates - this belongs to the Phase 5 mutual-exclusion triggers, not Phase 4 - and 7 `fc_*` slugs there now cover the pairs that were worth gating.

### Decision

Phase 4 (cross-layer duplicate consolidation) is **closed without a refactor commit**. The cross-layer counts represent legitimately distinct rules from distinct sources, not duplication. The genuine overlap-management work moved to **Phase 5**, which **shipped in `d149a204b`**: `common/scripted_triggers/WA_AI_MILITARY_PHASE5_ownership_triggers.txt`, 50 ownership slugs across 5 Exclusive types, all 50 read by at least one `ai_strategy` block (audited 2026-08-18, zero orphans). Inventory and the `priority`-vs-gate split are in `WA_AI_MILITARY_SYSTEM.md` §6.

Scanner artifact: `phase4_dup_scan.py` and `phase4_report.md` (1826 blocks, 153 cross-layer groups) preserved in the agent scratch directory for reference.

---

## Cross-cutting issues to address in Phases 2-4

1. **`WA_AI_MILITARY_COUNTRY_SOUTH_AMERICA.txt` is misnamed.** It is a regional rule, not a country file. Phase 2 renamed it to `WA_AI_MILITARY_REGION_SOUTH_AMERICA.txt`. **Phase 3 added `WA_AI_CONFIG_MILITARY_is_south_american` to `WA_AI_CONFIG.txt`** and replaced the inline 31-tag OR-lists in both `allowed` and `enable` with the trigger.

2. **`WA_AI_MILITARY_COUNTRY_CHINA_FRONT.txt` was a faction file with embedded country-specific blocks.** Phase 2 split the file into `WA_AI_MILITARY_FACTION_CHINA_FRONT_<DOMAIN>.txt`. **Phase 3** then:
   - Moved `WA_AI_MILITARY_CHINA_FRONT_sic_support_chi_against_japan` (gated on `tag = SIC`) into the new `WA_AI_MILITARY_COUNTRY_SIC_DIPLOMACY.txt`.
   - Replaced the warlord OR-tag-list in `WA_AI_MILITARY_CHINA_FRONT_warlords_china_needs_you` with the new `WA_AI_CONFIG_MILITARY_is_chinese_warlord` trigger (excludes CHI/PRC/SHX, distinct from the existing `WA_AI_MILITARY_is_china_front_member` which includes them).
   - Replaced the all-China-states OR-tag-list in `WA_AI_MILITARY_CHINA_FRONT_all_warlords_support_china_in_war` with the existing `WA_AI_MILITARY_is_china_front_member` trigger.

3. **`WA_AI_MILITARY_COUNTRY_AXIS.txt`, `_ALLIES.txt`, `_COMINTERN.txt`, `_CO_PROSPERITY.txt`** were faction files mis-prefixed `COUNTRY_`. Phase 2 renamed them to `WA_AI_MILITARY_FACTION_<NAME>_<DOMAIN>.txt`. (Note: COMINTERN and CO_PROSPERITY were initially flagged as empty during Phase 1 inventory; they actually contain real `front_unit_request` content gated on the corresponding `WA_AI_MILITARY_is_<faction>_member` trigger.)

4. **`WA_AI_MILITARY_COUNTRY_ALLIES.txt`** contains 15 `invasion_unit_request` blocks. Since `invasion_unit_request` is Additive, these can stay at the Faction layer; Phase 2 just renames the file to `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`.

5. **USA `naval_avoid_region` (67 blocks)** is the largest single repetitive pattern in the system. Phase 4 audit determined these are Additive and the duplication is by-design (per-region per-doctrine entries). No consolidation needed; revisit only if a per-region helper trigger emerges naturally.

6. **AXIS file's 59 `dont_defend_ally_borders` blocks.** Phase 2 split these across `WA_AI_MILITARY_FACTION_AXIS_*.txt` and `WA_AI_MILITARY_COUNTRY_*` files. Phase 4 audit confirmed the remaining FACTION-layer blocks (`AXIS_*_stop_crowding_up_the_soviet_line` family) have meaningfully distinct gates and cannot be safely merged. See "Phase 4 audit" section above.

7. **`WA_AI_MILITARY_FRONT_execution.txt`** carries a single `front_control` block. Rename to `WA_AI_MILITARY_DEFAULT_FRONT_control.txt` in Phase 2.

8. **`WA_AI_MILITARY_INVASION_budget.txt`** carries 2 default `invasion_unit_request` blocks. Rename to `WA_AI_MILITARY_DEFAULT_INVASION.txt` in Phase 2.

---

## Per-file summary (current state)

| File | Total blocks | Domain mix |
| --- | --- | --- |
| `WA_AI_MILITARY_FRONT_archetypes.txt` | 16 | FRONT |
| `WA_AI_MILITARY_FRONT_caps.txt` | 12 | FRONT |
| `WA_AI_MILITARY_FRONT_core.txt` | 4 | FRONT |
| `WA_AI_MILITARY_FRONT_execution.txt` | 1 | FRONT (control) |
| `WA_AI_MILITARY_INVASION_budget.txt` | 2 | INVASION |
| `WA_AI_MILITARY_COUNTRY_ALLIES.txt` | 231 | mixed (faction) |
| `WA_AI_MILITARY_COUNTRY_AXIS.txt` | 139 | mixed (faction) |
| `WA_AI_MILITARY_COUNTRY_COMINTERN.txt` | 0 | empty |
| `WA_AI_MILITARY_COUNTRY_CO_PROSPERITY.txt` | 0 | empty |
| `WA_AI_MILITARY_COUNTRY_CHINA_FRONT.txt` | 26 | mixed (faction + SIC) |
| `WA_AI_MILITARY_COUNTRY_SOUTH_AMERICA.txt` | 65 | DIPLOMACY+INVASION (region) |
| `WA_AI_MILITARY_COUNTRY_USA.txt` | 239 | mixed (all 5 domains) |
| `WA_AI_MILITARY_COUNTRY_GER.txt` | 219 | mixed |
| `WA_AI_MILITARY_COUNTRY_SOV.txt` | 168 | mixed |
| `WA_AI_MILITARY_COUNTRY_JAP.txt` | 124 | mixed |
| `WA_AI_MILITARY_COUNTRY_ENG.txt` | 99 | mixed |
| `WA_AI_MILITARY_COUNTRY_FRA.txt` | 76 | mixed |
| `WA_AI_MILITARY_COUNTRY_ITA.txt` | 67 | mixed |
| `WA_AI_MILITARY_COUNTRY_CHI.txt` | 49 | mixed |
| `WA_AI_MILITARY_COUNTRY_RCZ.txt` | 40 | mixed |
| `WA_AI_MILITARY_COUNTRY_CAN.txt` | 34 | FRONT+THEATRE+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_RAJ.txt` | 30 | mixed |
| `WA_AI_MILITARY_COUNTRY_FIN.txt` | 24 | FRONT+THEATRE |
| `WA_AI_MILITARY_COUNTRY_MAN.txt` | 23 | THEATRE+DIPLOMACY+NAVAL |
| `WA_AI_MILITARY_COUNTRY_AST.txt` | 18 | FRONT+INVASION+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_TUR.txt` | 12 | FRONT |
| `WA_AI_MILITARY_COUNTRY_SPA.txt` | 10 | FRONT |
| `WA_AI_MILITARY_COUNTRY_GRE.txt` | 10 | FRONT+INVASION |
| `WA_AI_MILITARY_COUNTRY_PRC.txt` | 8 | FRONT+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_SIA.txt` | 7 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_SPR.txt` | 7 | FRONT+THEATRE+GARRISON |
| `WA_AI_MILITARY_COUNTRY_CZE.txt` | 6 | FRONT+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_BUL.txt` | 4 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_SAF.txt` | 4 | FRONT+THEATRE |
| ~~`WA_AI_MILITARY_COUNTRY_RIT.txt`~~ | — | deleted 2026-08-17 (Fix 96): the RSI is served by `WA_AI_MILITARY_REGION_ITALY_FRONT.txt` / `_THEATRE.txt`, gated on `WA_AI_MILITARY_is_italian_homeland_power` |
| `WA_AI_MILITARY_COUNTRY_HUN.txt` | 2 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_POL.txt` | 2 | FRONT+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_RNC.txt` | 2 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_ROM.txt` | 2 | FRONT |
| `WA_AI_MILITARY_COUNTRY_HOL.txt` | 1 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_MAL.txt` | 1 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_NZL.txt` | 1 | FRONT |
| `WA_AI_MILITARY_COUNTRY_POR.txt` | 1 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_SIK.txt` | 1 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_YUG.txt` | 1 | FRONT |
