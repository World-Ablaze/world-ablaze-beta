# WA naval AI: inventory and gaps (for comparison with Kaiserreich / Sheep's Japan naval AI)

Read-only audit, 2026-09-25, branch `ai-rework`. All paths are relative to
`E:\Projets\HOI4\WA\world-ablaze-beta`. Labels follow AGENTS.md: **MEASURED** = read in a file
(cited), **DERIVED** = computed from MEASURED facts (source stated), **ASSUMED** = unverified /
engine behaviour.

Scratch artefacts produced during the audit (same folder as this report):
`inv_events.txt` (parsed table of every scripted invasion event), `naval_defines.tsv` (WA vs vanilla
naval defines), `nai_not_overridden.txt` (vanilla NAI naval keys WA leaves alone).

---

## 0. Verdict

1. **MEASURED** — WA's Japanese offensive is a **scripted calendar, not a naval AI**. 30 active
   Japanese landings (1938 Canton → 1942 Attu) are fired by `common/scripted_effects/WA_KDE_AI_effects.txt`
   and executed by `WA_AI_DIVISION_spawn_invasion`, which **creates divisions directly on the enemy
   beach** (`create_unit ... allow_spawning_on_enemy_provs = yes`,
   `common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt:2681-2790`). No fleet, convoy or
   engine invasion plan is involved.
2. **DERIVED** (from the 90 `var:_target_country = { is_ai = no }` guards in `events/WA_AI_invasions.txt`)
   — the sea-control check (`has_enemy_naval_control`) only applies when the **target is human**,
   and even then lapses after 180 days. Against an AI target a scripted landing ignores the naval
   situation entirely.
3. **MEASURED** — the calendar only runs on Historical difficulty (`WA_AI_DIFFICULTY_is_historical`,
   `difficulty < 3`, `WA_AI_CONFIG.txt:31-33`, required by every invasion event's `trigger`). On
   Competitive difficulty Japan has no scripted landings at all.
4. **MEASURED** — the engine-driven Japanese naval layer is thin: 7 blocks in
   `common/ai_strategy/WA_AI_NAVAL_COUNTRY_JAP.txt` (4 `strike_force_home_base`, 35 `naval_avoid_region`
   walls, 1 escort-suppression threshold), **zero `naval_dominance`, zero `naval_convoy_raid_region`,
   zero invasion-support priority**, no JAP `ai_navy` fleet/taskforce template, no JAP naval `unit_ratio`.
5. **DERIVED** — after the last scheduled Japanese op (Attu, 1942 day 157) Japan has no offensive or
   defensive naval plan beyond home-base anchoring and blanket "don't invade X" negatives.

---

## 1. `ai_strategy` naval / invasion blocks

### 1.1 Census by type (all of `common/ai_strategy/`)

**MEASURED** (`grep -cE "type *= *<t>"` per file, 2026-09-25):

| Type | Writers (file: count) | Notes |
| --- | --- | --- |
| `naval_avoid_region` | ALLIES 85, GER 78, ENG 54, JAP 35, USA 34 (+3 legacy USA.txt, commented), DEFAULT 21, RCZ 11, AXIS 10, COMINTERN 9, FRA 8, ITA 8, MAN 5, SPA 5, CAN 2, SOV 2 | Signed: +2000 hard wall, -1000 corridor pull (convention: `documentation/WA_AI_MILITARY_SYSTEM.md` §4 notes) |
| `naval_convoy_raid_region` | GER 28, USA 17, ENG 3, ALLIES 3 | No Axis-Pacific / JAP writer |
| `naval_dominance` | ALLIES 21 only | **No Axis, no JAP, no USA-Pacific writer** |
| `naval_mission_threshold` | DEFAULT 2, ALLIES 2, JAP 1 | |
| `strike_force_home_base` | USA 6, ENG 5, ITA 4, JAP 4, ALLIES 4, FRA 3 | |
| `naval_invasion_dominance_weight` | DEFAULT 1 (value 50, every belligerent with >9 ships) | `WA_AI_NAVAL_DEFAULT.txt:16-27` |
| `naval_invasion_focus` | JAP_INVASION 6 (value 100) | only JAP uses it |
| `naval_invasion_support_priority` | **0** | real engine type, used 7× by vanilla ENG (`documentation/WA_AI_MILITARY_TYPES_REFERENCE.md:279-295`) |
| `naval_convoy_escort` | **0** | not an engine type (absent from the install's `_documentation.md` and vanilla files) |
| `naval_invasion_supremacy` | **0** | not an engine type (same check) |
| `invasion_unit_request` | ALLIES_INV 15, JAP_INV 10, GER_INV 7, landing_freeze 5, FRA_INV 4, USA_INV 4, DEFAULT_INV 2, SOV_INV 2 | |
| `invade` | ALLIES_INV 89, ENG_INV 50, USA_INV 50, JAP_INV 47, GER_INV 44, S.AMERICA 19, ITA_INV 12, SOV 7, AST 6, GRE 4, BUL 3 … | overwhelmingly negative suppressors |
| `dockyard_to_military_factory_ratio` | JAP.txt:941-955 (value 40), GER.txt:2155 | JAP gate: `num_of_civilian_factories_available_for_projects > 15` |
| `put_unit_buffers` (naval-adjacent) | USA THEATRE Pacific island buffers (11+1 orders, capped twin) | `WORK.md:2320-2400` `usa-pacific-hoard` |

### 1.2 DEFAULT layer (every country)

| Block (file:line) | Types / magnitudes | Gate |
| --- | --- | --- |
| `WA_AI_NAVAL_DEFAULT_invasion_path_supremacy` (`WA_AI_NAVAL_DEFAULT.txt:16`) | `naval_invasion_dominance_weight` 50 | `WA_AI_NAVAL_should_focus_supremacy_on_invasion_paths` = `has_war` + `has_navy_size > 9` (`WA_AI_NAVAL_triggers.txt:746-751`) |
| `WA_AI_NAVAL_DEFAULT_legacy_AI_naval_mission_fix` (`:377`) | `MISSION_STRIKE_FORCE` -500, `MISSION_PATROL` -1000 | `always = yes`, no `allowed` → **reaches Japan too** |
| 19 `legacy_DONT_GET_TRAPPED_HERE_*` + `st_lawrence_river_trap` (`:31-401`) | `naval_avoid_region` +2000 on Baltic gulfs, Black Sea-ish traps, 241, 322 | per-region `WA_AI_NAVAL_should_avoid_sea_region_<id>` |
| `WA_AI_MILITARY_INV_freeze_when_home_threatened` (`WA_AI_MILITARY_DEFAULT_INVASION.txt:11`) | `invasion_unit_request` -200 | `WA_AI_MILITARY_home_threatened` + war (`WA_AI_MILITARY_INVASION_gate_triggers.txt:1136`) |
| `WA_AI_MILITARY_INV_majors_open_when_force_surplus` (`:26`) | `invasion_unit_request` +40 | major, at war, `can_open_secondary_fronts`, home not threatened (`:1128`) |
| Landing freeze WEST / EAST / faction-wide (`WA_AI_MILITARY_DEFAULT_INVASION_landing_freeze.txt:51,76,103`) | `invasion_unit_request` -200 for 90 days after a scripted landing, theatre-scoped by continent | `WA_AI_LANDING_triggers.txt:82-121`; blanket mode `always = no` |
| `WA_AI_MILITARY_INV_reserved_scripted_target` (`:136`) | `invasion_unit_request` -200 against countries the calendar still owes an operation | `WA_AI_LANDING_reservations_enabled = always yes` (`WA_AI_LANDING_triggers.txt:64`); spec §22 |

**MEASURED** comment at `WA_AI_NAVAL_DEFAULT.txt:360-375`: the mission-fix pair used to be written
twice and summed to -1000/-2000; now single. The lesson `naval_mission_threshold is a bar, not a
priority — positive SUPPRESSES` (`.claude/skills/wa-lessons-learned/references/lessons-log.md:1356`)
governs the sign.

### 1.3 FACTION layer

| Faction file | Blocks | Content |
| --- | --- | --- |
| `WA_AI_NAVAL_FACTION_ALLIES.txt` | 29 | Atlantic north/south corridors (`naval_dominance` 80/70 + avoid -1000 pulls, `:194,:273`), `MISSION_CONVOY_ESCORT` -100 (`:252`), off-corridor walls, Gibraltar approaches, Atlantic home bases 43 / 55+54 (`:406,:436`), Med lifeline raid 29/269 (+250 raid, `MISSION_CONVOY_RAIDING` -100, `:629`), Tobruk route raid 327 (`:659`), **Med Fleet at Alexandria (sfhb 69, `naval_dominance` 69/327 = 500, `:728-745`)**, narrows sea control 269/29 = 500 (`:755-769`), Pacific walls (`western_pacific_trap`, `uninvaded_malaya_borneo`, `uninvaded_australia_new_zealand`, `neutral_china_seas`, `:800-890`), Sealion air pull, Downfall air pull |
| `WA_AI_NAVAL_FACTION_AXIS.txt` | 2 | deep-Atlantic avoidance for non-German Axis members (1000), East-Africa cut-off lane (1000) |
| `WA_AI_NAVAL_FACTION_COMINTERN.txt` | 1 | Atlantic off-corridor avoidance |
| **none** for Co-Prosperity | — | **MEASURED**: no `WA_AI_NAVAL_FACTION_CO_PROSPERITY*` file exists. Japan is not an Axis member in WA (lessons-log:75), so Axis naval blocks never reach it (**DERIVED**) |

**MEASURED doc drift**: `documentation/WA_AI_MILITARY_SYSTEM.md` §21 (lines ~1480) says the Med Fleet
blocks use `naval_dominance` 80 / 70 and §4 says live values are 70-80 inside the engine's
documented 0-100 percentage; the file now writes **500** (`WA_AI_NAVAL_FACTION_ALLIES.txt:741-742,
766-767`, header `range: naval_dominance 500`). **ASSUMED**: the engine clamps or saturates >100.

Allied INVASION (`WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`, 17 blocks, **MEASURED** names):
Norway hold/fire, `dday_hold` (-2000 on GER/FRA…), `invasion_cap_without_foothold` (-100 `invasion_unit_request`,
`:98`), `minor_allies_dont_invade`, `no_italy_invasion_early`, `dday_prep` (+1000 on Normandy states),
`dday_fire`, Husky prep/fire (`invade ITA` 4000), `pacific_side_shows_wait`, etc.

### 1.4 COUNTRY layer — naval files

| File | Blocks | Key content (MEASURED) |
| --- | --- | --- |
| `WA_AI_NAVAL_COUNTRY_JAP.txt` | 7 | see §7 |
| `WA_AI_NAVAL_COUNTRY_USA.txt` | 13 | Torch corridor, europe_first walls on Indian Ocean, `pacific_offensive` walls (`:150`, gate `has_war_with JAP` + `WA_AI_MILITARY_pacific_offensive_ready`, `WA_AI_NAVAL_triggers.txt:710`), convoy raid -1000 across the Med, strike bases 349 Hawaii / 224 / 180 (`:393`, gate war with JAP or peace), east-coast bases 55/54/170, four "death-trap" walls (Philippines, home islands, Okinawa 240, Iwo Jima 94) |
| `WA_AI_NAVAL_COUNTRY_ENG.txt` | 12 | `protect_home` (Channel 18 = -10000, `always`), home bases 16/365/18, Azores 112, Gibraltar 249, home-water raid 16/365/18 (+250 when invaded), `ignore_japan_until_germany_is_dealt_with` (walls on 75/106/110/231/252/87/90/240 while at war with GER, `WA_AI_NAVAL_triggers.txt:17-19`), Indian-sea strategy, `med_is_lost` |
| `WA_AI_NAVAL_COUNTRY_GER.txt` | 19 | 78 avoid, 28 raid regions (Atlantic 1000; far-away -1000), BoB / Sealion air pulls, "shallow seas are terrible for subs" |
| `WA_AI_NAVAL_COUNTRY_ITA.txt` | 6 | home bases 218/29/373/169, Tobruk-risk and Med-transport walls, air pulls |
| FRA 3, SOV 3, SPA 2, CAN 1, MAN 1, RCZ 1 | — | mostly avoid walls / home bases |

### 1.5 COUNTRY layer — invasion files (non-JAP)

**MEASURED** (block summaries): USA 10 blocks (Torch targets `invade VIC/FRM` 4000, Pacific offensive
`invade JAP` 4000, `invade_japan_units` `invasion_unit_request` 1000, `dont_invade_japan_yet` -4000,
Normandy reinforcement); ENG 15 (mostly suppressors; `fight_the_japanese` `invade JAP` 5000); GER 18
(Norway, Denmark, Sealion time / not-time, avoid Greenland/Faroes/Siberia); ITA 7 (Crete, Greece,
Turkey, Ireland suppressors).

---

## 2. `common/ai_navy/`

**MEASURED**: `descriptor.mod:15-18` replaces `common/ai_navy`, `/fleet`, `/goals`, `/taskforce`, so
vanilla navy templates are **not live**; only WA's 9 files run.

| File | Content (MEASURED) |
| --- | --- |
| `fleet/generic_fleet_templates.txt` | 8 live fleets: `generic_dominance_fleet_1` (1-2× StrikeForce_1), raiding fleets 2/3/4 (subs / cruiser subs / surface raiders), escort fleet 6 (frigates), minelaying 7 + 12, naval support 8, patrol DD 9. Escort fleet 5 and CA/BC patrol fleets commented out |
| `fleet/USA_fleet_templates.txt`, `fleet/CAN_fleet_templates.txt` | DD convoy-escort fleet (`[can-transit-attrition]`) |
| `taskforce/generic_taskforce_templates.txt` | `StrikeForce_1` min **2 CV + 2 BB + 10 CL**, optimal 4 CV / 8 BB / 10 CA / 20 CL / 30 DD (`:1-38`); `PatrolReconForce_1` 5-20 DD; `ConvoyRaiding_1` 5-10 SS; `_2` 5-10 cruiser subs; `ConvoySurfaceRaiding_1` 1-2 BC + 3-6 CA; `ConvoyEscort_2` 5-20 frigates + 1 CVL; `MineLaying_1` DD role 4; `MineLayingFrigate_1`; `NavalInvasionSupport_1` min 1 CA + 4 CL, optimal 4 BC / 4 CA / 12 CL (comment "Commented out for now as it throws the error" but the block is live, `:282`) |
| `taskforce/USA_*`, `taskforce/CAN_*` | DD convoy escort until `WA_AI_NAVY_frigate_mass_reached` (`common/scripted_triggers/WA_AI_NAVY_triggers.txt:10-15`) |
| `goals/goals_generic.txt` | 10 goals with min/max priorities: invasion support 4-15, mine sweeping 2-8, invasion defense 15-25, coast defense 5-16, convoy protection 15-30, convoy raiding 1-7, naval dominance 10-20, mine laying 1-8 (blocked for ENG), training 10-20, blockade 10-20 |
| `goals/goals_ENG.txt` | ENG mine laying 10-18 |

**DERIVED** (from the StrikeForce_1 minimum): a navy without ≥2 carriers AND ≥2 battleships AND ≥10
light cruisers cannot form WA's only strike-force template — ITA (no carrier programme,
`WA_AI_CONFIG.txt:390-395` comment) and GER can never field one. **ASSUMED**: `min_composition`
is an AND of all listed ship types; whether the engine then falls back to its own auto-composition
is not documented.

**MEASURED gaps**: no JAP-specific fleet or taskforce template; no carrier-only (Kido Butai style)
taskforce; no dedicated invasion-support fleet per country; no surface-action (BB/CA) patrol template
(CA/BC patrol templates commented out, `generic_taskforce_templates.txt:66-117`).

---

## 3. `common/ai_strategy_plans/`

**MEASURED**: `JAP_historical_strategy_plan.txt` (enable: historical focus / DEFAULT / FASCIST rule)
and `JAP_alternate_strategy_plan.txt` (NEUTRALITY rule, strike north) carry **only a focus list**
(`ai_national_focuses`) — `research = {}` and `ideas = {}` empty, no `ai_strategy`. Naval focuses in
the historical order: `JAP_the_ultimate_battleship`, `JAP_new_naval_estimates`, `JAP_expand_the_dockyards`,
`JAP_rebuild_the_heavy_escort_fleet`, `JAP_supremacy_of_the_battlefleet`, `JAP_kantai_kessen`,
`JAP_imperial_japanese_navy_air_service`, `JAP_carrier_warfare_experiments`, `JAP_first_air_fleet`,
`JAP_strike_south_doctrine`, `JAP_island_bulwarks`, `JAP_hi_convoys`. **MEASURED**: no plan file in the
folder carries a naval `type =`; only CHI/CZE/GER/HUN/PRC/USA plans carry any `ai_strategy` at all.

---

## 4. Naval defines (`common/defines/05_defines.lua` vs install `00_defines.lua`)

**MEASURED** (script diff, `naval_defines.tsv`): of 260 vanilla `NAI` keys matching naval keywords,
WA rebinds **91**; the rest keep vanilla values (`nai_not_overridden.txt`). Key overrides:

| Area | WA (vanilla) — `05_defines.lua` line |
| --- | --- |
| Invasion planning | `MAX_UNIT_RATIO_FOR_INVASIONS` 0.35 (0.4) :1058; `MAX_INVASION_FRONT_SCORE` 2400 (1000) :1059; `NAVAL_INVADED_AREA_PRIO_DURATION` 270 (90) :1062; `NAVAL_INVADED_AREA_PRIO_MULT` 2.0 (1.2) :1063; `MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS` 60 (20) :1064; `MAX/DESIRED/MIN_UNITS_FACTOR_INVASION_ORDER` 1.4/1.4/1.2 (1.0) :1066-1068; `MIN_INVASION_PLAN_VALUE_TO_EXECUTE` 0.05 (0.3) :1379; `ENEMY_NAVY_STRENGTH_DONT_BOTHER` 5.0 (2.5) :1069; `NNavy.BASE_NAVAL_INVASION_DIVISION_CAP` 3 (4) :696 |
| Invasion support | `MAX_SCREEN_FORCES_FOR_INVASION_SUPPORT` 0.2 (0) :1138; `MAX_CAPITAL_FORCES_FOR_INVASION_SUPPORT` 0.3 (0) :1139 |
| Taskforce shape | `CARRIER_TASKFORCE_MAX_CARRIER_COUNT` 10 (4) :1141; `CAPITAL_TASKFORCE_MAX_CAPITAL_COUNT` 10 (12); `SCREEN_TASKFORCE_MAX_SHIP_COUNT` 5 (12); `SCREENS_TO_CAPITAL_RATIO` 3 (4); `MIN_CAPITALS_FOR_CARRIER_TASKFORCE` **10** (6) :1147; `CAPITALS_TO_CARRIER_RATIO` 1.0 (1.5); `MAX_CARRIER_OVERFILL` 1.0 (1.85); `SUB_TASKFORCE_MAX_SHIP_COUNT` 5 (16) :1221; `AI_TASKFORCE_REQUIRED_RESERVE_RATIO` 0.05 (0.2); `MAX_PATROL_TO_STRIKE_FORCE_RATIO` 10 (4) :1199 |
| Convoys / escort | `MISSING_CONVOYS_BOOST_FACTOR` 0 (50) :1076; `REGION_THREAT_PER_SUNK_CONVOY` 300 (25) :1128; `CONVOY_DANGER_FOR_MAX_IMPORTANCE` 50 (400) :1129; `REGION_CONVOY_DANGER_DAILY_DECAY` 4 (2); `MAX_SCREEN_TASKFORCES_FOR_CONVOY_DEFENSE_MIN` 0.3 (0.2); `EXTRA_NAVY_INTEL_FOR_CONVOY_RAIDING` 1.0 (0) |
| Naval air | `NAVAL_COMBAT_AIR_IMPORTANCE` 500 (8) :1240; `NAVAL_IMPORTANCE_SCALE` 10 (0.65); `NAVAL_STRIKE_PLANES_PER_SHIP` 40 (20); `NAVAL_MIN_EXCORT_PLANES` 100 (0); `NAVAL_COMBAT_TRANSFER_AIR_IMPORTANCE` 500 (50); `PRODUCTION_CARRIER_PLANE_BUFFER_RATIO` 5 (1.5) |
| Refit / XP | `REFIT_SHIP_RELUCTANCE` 7 (28); `REFIT_SHIP_PERCENTAGE_OF_FORCES` 1.0 (0.1); `DESIRE_USE_XP_TO_UPGRADE_NAVAL_EQUIPMENT` 100 (1) |
| Production | `NAVAL_DOCKYARDS_SHIP_FACTOR` 2 (1.5) :1213; `NProduction.POWERED_FACTORY_SPEED_NAV` 4.2 (2.5) :194, mirrored by the 4.2 constant in `WA_AI_Capital_Ship_effects.txt` |
| Repair | `REPAIR_AND_RETURN_PRIO_*` lowered (0.2/0.5/0.8 vs 0.45/0.65/0.9) → fleets stay out longer |
| Combat (NNavy, ~70 keys) | positioning, torpedo crits 0.9×6 (0.1×2), detection, sub escape, speed — combat balance, not AI |

**Left at vanilla (MEASURED, `nai_not_overridden.txt`)**: `NAVAL_MISSION_DISTANCE_BASE` 3500,
`NAVAL_MISSION_INVASION_BASE` 1000, `NAVAL_MISSION_PATROL_NEAR_OWNED` 500 / `_CONTROLLED` 140,
`INVASION_TARGET_*` scoring, `FAILED_INVASION_AVOID_DURATION` 60, `MIN_INVASION_ORG_FACTOR_TO_EXECUTE`
0.4, `MIN_INVASION_UNITS_READY_TO_EXECUTE` 0.25, `ENEMY_HOME_AREA_RATIO_TO_DISABLE_INVASIONS` 0.3,
`AI_NAVAL_GOALS_UPDATE_FREQUENCY_DAYS` 7, the `MIN_NAVAL_MISSION_PRIO_TO_ASSIGN` / `HIGH_PRIO_NAVAL_MISSION_SCORES` tables.

**ASSUMED**: `MIN_CAPITALS_FOR_CARRIER_TASKFORCE = 10` means an engine-built carrier TF wants 10
capitals; with `CARRIER_TASKFORCE_MAX_CARRIER_COUNT = 10` the engine favours very large carrier
groups. Interaction with the `StrikeForce_1` template (2-4 CV) is not documented. Defines are global
(no per-country gating).

---

## 5. Naval production

### 5.1 Role / unit ratios

| Block (file) | Values (MEASURED) | Gate (MEASURED) |
| --- | --- | --- |
| `WA_DEFAULT_production_navy_base_ratios` (`WA_AI_PRODUCTION_DEFAULT_navy.txt:1`) | `role_ratio` screen 100, sub 25, CL 10 | always (default system) |
| `_major_navy` (`:11`) | BB 7, BC 3, CA 7 | `WA_AI_CONFIG_is_major_country` + not sub navy + `WA_AI_PRODUCTION_should_build_capitals` |
| `_minor_navy` (`:23`) | CA 7 | minor, not sub navy |
| `_main_focus_on_carriers` (`:32`) | CV 10 | `WA_AI_CONFIG_is_carrier_navy` = USA, JAP (`WA_AI_CONFIG.txt:351-356`) + capitals allowed |
| `_secondary_focus_on_carriers` (`:42`) | CV 5 | FRA, ENG (`:390-395`) |
| `_main_focus_on_submarines` / `_cruiser_submarines` (`:52,:61`) | subs 75 / cruiser subs 100, screens -100 | sub navy = GER, SOV, non-Allied minors; cruiser subs = GER, SOV (`:358-367,:440-445`) |
| `_main_focus_on_escorts` (`:71`) | screen -50, escort +50 | `WA_AI_NAVY_is_escort_focused` = Allied minor OR `is_convoy_escort_power` (ENG FRA USA **JAP**, `WA_AI_CONFIG.txt:401-408`) |
| `_major_no_capitals` (`:90`) | CV/BB/BC/CA -50 | `should_build_capitals = no` |
| Convoy ladder (`:147-286`) | `unit_ratio convoy` 15 (+85 arsenal relief), floors 1/3/3/3/3, stop -200 | dockyard / stock bands |
| `default_unit_production` (`wa_default.txt:1-71`) | `unit_ratio` capital 20, sub 10, screen 40 | **excludes ENG GER SOV USA JAP FRA CHI ITA CZE** |
| `JAP_building_boats_is_great` (`JAP.txt:941-955`) | `dockyard_to_military_factory_ratio` 40 | civ factories available > 15 |
| `WA_AI_PRODUCTION_COUNTRY_JAP_ocean_going_submarines` (`WA_AI_PRODUCTION_COUNTRY_JAP.txt`) | `production_upgrade_desire_offset` hull_4 +100, hull_5/6 -100 | always, JAP |

**MEASURED**: no naval `unit_ratio` for JAP anywhere (`JAP.txt:6` is a comment; JAP excluded from
`default_unit_production`). **DERIVED**: JAP's naval volume is set by the engine
(`NAVAL_DOCKYARDS_SHIP_FACTOR` 2) plus the dockyard ratio 40, and its mix by `role_ratio` — screen 50
/ escort 50 / sub 25 / CL 10 / BB 7 / CA 7 / BC 3 / CV 10 while capitals are allowed.

**Capital gate, MEASURED** (`WA_AI_PRODUCTION_navy.txt:136-151`): on Historical difficulty a major
may build capitals only if `WA_AI_CONFIG_naval_treaty_era_expired` (`date > 1948.1.1`,
`WA_AI_CONFIG.txt:417-419`) OR any of ENG FRA GER ITA JAP SOV USA holds a naval-treaty idea
(`has_naval_treaty_trigger`, `00_scripted_triggers.txt:202-211`). **DERIVED contradiction**: the
comment says capitals are held back "until the treaty era ends"; the code allows them WHILE a treaty
idea exists and forbids them (until 1948) once every major has left the treaty. Which reading is
intended is not verified. **ASSUMED**: in a historical game the treaty collapses by ~1937-39, so
from then on AI majors on Historical get BB/BC/CA/CV at -50 and rely on scripted spawns (§5.3).

### 5.2 `common/ai_equipment/` naval designs

**MEASURED** (`target_variant` counts): ENG 82, JAP 72, USA 65, ITA 61, FRA 54, GER 51, SOV 43,
generic 31. JAP groups: screen 12 (DD hulls 1-12), escort 6 (frigates), CL 7, CA 9, capital_bb 6
(BC hull 1, BB 2-4, super-BB 1-2), carrier 8, carrier_light 7, submarine 7, cruiser_submarine 7,
mine_sweeper 1, mine_layer 2 (`JAP_naval.txt`). Lesson: tech + design + role must all line up
before an AI builds a ship (`lessons-log.md:2222`).

### 5.3 Scripted capital-ship spawns (`events/WA_AI_Capitals.txt`)

**MEASURED**: 112 `create_ship` calls; each event is AI + Historical only, charges the ship's IC via
`WA_AI_Capital_Ship_cost` (`industrial_capacity_dockyard -0.50` for `IC / (4.2 × dockyards × output) / 0.5`
days, `common/ideas/_WA_ai.txt:130-139`, `WA_AI_Capital_Ship_effects.txt:11-60`). Active calendar
entries by country (`WA_KDE_AI_effects.txt`): USA 80, ENG 15, **JAP 9**, GER 3, FRA 2, ITA 2.

JAP spawns (MEASURED): Hiryu (1937 d319), Shokaku + Zuikaku (1939 d151/d330), Taiho (1943 d65),
Unryu / Amagi / Katsuragi (1943 d267, d287; 1944 d18), Ibuki + "301" CA (1944 d274, 1945 d18; both
require `controls_state = 645` Iwo Jima). **MEASURED**: no Yamato/Musashi spawn (no "Yamato" string
in history/units, events or scripted_effects).

---

## 6. Scripted naval logic, cadence, marines

### 6.1 The scripted invasion calendar (the core of WA's amphibious AI)

| Piece | File (MEASURED) |
| --- | --- |
| Yearly scheduler | `common/on_actions/WA_KDE_on_actions.txt`: `on_startup` fires 1936 on the dummy tag **AIU**; `on_monthly_AIU` detects the year change and calls `WA_KDE_yearly_event_fire_<year>` via `meta_effect` |
| Schedule | `common/scripted_effects/WA_KDE_AI_effects.txt:1-333` — per country, `country_event = { id = WA_AI_invasions.N days = D }` |
| Operations | `events/WA_AI_invasions.txt` — 86 `country_event`s, 201 `WA_AI_DIVISION_spawn_invasion` calls |
| Executor | `WA_AI_DIVISION_spawn_invasion` (`WA_AI_DIVISION_CREATOR_effects.txt:2681`): flips the target province controller, `create_unit` on it, takes equipment/manpower from stockpile, adds 1-day `WA_AI_scripted_invasion_fix` (reinforce rate) |
| Difficulty scaling | `WA_AI_DIVISION_adjust_invasion_for_difficulty` (`:2897-2940`): ×0.5 historical-easy, ×2 historical-hard / competitive-hard |
| Post-landing freeze | §10 of `WA_AI_MILITARY_SYSTEM.md`; stamp in `WA_AI_LANDING_effects.txt` |
| Pre-landing reservation | §22; generated `WA_AI_LANDING_reservations_data.txt` (75 ops, AST 5 / ENG 6 / GER 4 / JAP 30 / USA 30 at generation time) |

Per-event pattern (MEASURED on `WA_AI_invasions.9`, lines ~1013-1075; DERIVED to be universal from
the counts 86 events / 90 `is_ai = no` guards / 91 `invasion_launcher_not_collapsing`):
- target = current CONTROLLER of an anchor state (dynamic);
- fires only if at war with it, the target still controls the anchor, launcher `surrender_progress < 0.1`
  (`WA_AI_MILITARY_INVASION_gate_triggers.txt:1528-1530`), and a launch state is held by ROOT or an ally;
- `NOT has_enemy_naval_control = <sea region>` **only when the target is human**, and that check
  lapses after a 180-day flag;
- if at war but preconditions fail → re-fire in 7 days; **if not at war on the scheduled day → nothing,
  no retry** (DERIVED from the `else_if` limit requiring `has_war_with = ROOT`).

Active calendar counts (MEASURED): USA 32, JAP 30, ENG 5, AST 5, GER 4. ENG Neptune/Shingle
commented out (`WA_KDE_AI_effects.txt:201-203`); USA D-Day is a scripted variant roll
(`WA_AI_invasions.random` d57 → `dday_launch` d157, `:220-221`).

### 6.2 Other scripted naval pieces

- **MEASURED**: `common/scripted_triggers/WA_AI_NAVAL_triggers.txt` (1363 lines) = the `_should_*` gates of
  every naval block; `WA_AI_NAVY_triggers.txt` (35 lines) = frigate-mass + escort-navy archetypes.
- **MEASURED**: `WA_AI_DOCTRINES_navy.txt` (493 lines) selects naval sub-doctrines
  (`WA_AI_NAVY_DOCTRINES_SELECT_*`, 18 triggers); `WA_AI_RESEARCH_naval.txt` (146 lines) = 11
  `WA_AI_RESEARCH_needs_<ship>` research gates.
- **MEASURED**: on_actions carry no naval AI pulse (grep of `common/on_actions/*.txt`); the only naval
  cadence is the monthly reservation updater and the KDE calendar. `on_naval_invasion`
  (`00_on_actions.txt:2386`) sets an `invasion_alert` flag.
- **MEASURED**: harness `common/scripted_effects/WA_TEST_explain_naval.txt` + `events/wa_test_explain_naval.txt`.
- **MEASURED** (AGENTS.md): naval-base construction lives in the railway priority-construction queue.

### 6.3 Marines / amphibious templates

- **MEASURED**: `common/ai_templates/WA_AI_TEMPLATES_marines.txt` (233 lines, `WA_marines_role`,
  flag-coded `WA_MARINES_TEMPLATE` targets); production `role_ratio marines` +10 / infantry -10 when
  `WA_AI_TEMPLATES_use_marines` (`WA_AI_PRODUCTION_army_composition.txt:198-202`).
- **MEASURED**: scripted landings use their own spawn templates (`_division_template` 1-15; 8/12 marines,
  9/13 amtrac + tanks, 10/11 SNLF). Census in `WA_AI_invasions.txt`: template 1 ×36, 4 ×30, 6 ×19,
  11 ×18, 10 ×15, 7 ×14, 13 ×13, 9 ×12, 12 ×4, 8 ×2.

---

## 7. Japan specifically

### 7.1 Scripted landings (MEASURED, `inv_events.txt` + `WA_KDE_AI_effects.txt`)

| Year | Ops (day) | Anchor state / sea checked (human target only) |
| --- | --- | --- |
| 1938 | Canton `.6` (d284) | 592 / 75 South China Sea, SNLF ×2/prov |
| 1939 | Hainan `.7` (d39), Chinese port cities `.8` (d98) | 591, 595 / 75 |
| 1941 | Malaya `.9`, Guam `.10`, Wake `.11` (d341); Gilberts `.12` (d342); N. Luzon `.13` (d343); Legazpi `.14` (d345); Borneo `.15` (d349); Luzon/Dagupan `.16`, Mindanao `.17` (d352) | 862/73, 638/350, 632/351, 639/227, 623/75, 624/75, 333/231, 623/75, 627/280 |
| 1942 | Tarakan `.19`, Manado `.20` (d10); Pontianak `.86` (d19); Balikpapan `.21`, Rabaul/Kavieng `.22` (d22); Kendari `.23` (d23); Ambon `.24` (d29); Makassar `.84` (d40); Palembang `.25` (d44); Timor `.41` (d49); Java `.26` (d59); Lae `.27` (d66); Sumatra `.28` (d70); Andaman `.29` (d81); Christmas I. `.42` (d89); Solomons `.43` (d122); Nauru `.44` (d130); Attu `.30` (d157) | see `inv_events.txt` |
| commented out | Bataan `.18`, Kiska `.45` | — |

**MEASURED**: no Pearl Harbor, Midway, Port Moresby, Ceylon/Indian Ocean raid or any fleet-action
script. `JAP_pearl_harbor` in `common/decisions/_STRATEGIC_REGION_pacific.txt:6428-6465` is a
**human-only** mission (`activation = { is_ai = no ... }`) with no effect but a war-support timeout.

### 7.2 Engine-side JAP blocks

| Block (file:line) | Types / values (MEASURED) | Gate (MEASURED) |
| --- | --- | --- |
| `..._strike_force_home_base_home_waters` (`WA_AI_NAVAL_COUNTRY_JAP.txt:10`) | sfhb 90, 240 | `always = yes` |
| `..._iwo_jima` (`:34`) | sfhb 94 | 645 not held by an enemy (`WA_AI_NAVAL_triggers.txt:522`) |
| `..._taiwan` (`:53`) | sfhb 75 | 524 not held by an enemy (`:515`) |
| `..._complete_southern_expansion` (`:72-261`) | avoid +2000 on the whole Med (16 regions), central Pacific 96/114/232/110/107/175/172/95, Solomon 83 / Coral 81 / Tasman 86/341; 169 at +100 | `has_completed_focus = JAP_strike_south_doctrine`; abort when MAL+PHI+INS all capitulated |
| `..._no_touching_india` (`:266`) | avoid 111 | at war with USA |
| `..._conserve_fuel_for_usa_fight` (`:287`) | `MISSION_CONVOY_ESCORT` +150 (suppresses escort) | before 1941, not at war with USA/ENG |
| `..._avoid_europe` (`:307`) | avoid 100/102/103/65/63 | Suez 446 not JAP-held |
| Southern expansion 1/2/3 prep+fire (`WA_AI_MILITARY_COUNTRY_JAP_INVASION.txt:52-276`) | `naval_invasion_focus` 100; `invade` target 4000, the other two -2000; `invasion_unit_request tag = target` 1000 — PHI → MAL → INS | **date windows**: 1941.12.1-1942.1.1, 1942.1.1-1.15, 1.15-2.1, 2.1-2.15, 2.15-3.1, 3.1-3.15, each + `WA_AI_MILITARY_is_at_war_in_southeast_asia` (war with INS/MAL/PHI, `WA_AI_MILITARY_triggers.txt:3902`) + `surrender_progress = 0` (`WA_AI_MILITARY_FRONT_gate_triggers.txt:1300-1345`) |
| `malaya_done` / `indonesia_done` (`:280,:310`) | `invade` -1000, `invasion_unit_request` -1000 | **both** = `country_exists IPI` AND `IPM` (`WA_AI_MILITARY_INVASION_gate_triggers.txt:880-889`) — identical bodies |
| `first_southern_expansion` (`:340`) | `invade CHI` -4000, ENG -1000 | strike-south doctrine, puppets not all formed |
| China war invasions 2/3/4/5 | `invade CHI` +4000 / +2000 / -5000 / -5000 | coastal-state control ladders, dates 1938.4-1940 |
| `no_go_zones`, `fight_the_US`, `no_touching_india`, `avoid_europe` | `invade` USA/AST/NZL/RAJ/BRM/FRA/UKM/UKO -2000 | war with those / puppets |
| `if_usa_gets_too_strong_stop_invading` (`:490`) | `invade` USA ENG INS MAL PHI AST UKO -1000 | after 1943, `naval_strength_ratio < 0.5` vs USA (`:610-619`) |
| `WA_AI_MILITARY_JAP_attack_hawaii` (`WA_AI_MILITARY_COUNTRY_JAP_FRONT.txt:61`) | `front_unit_request state 629` +100 | at war with USA, 629 not fully held (`WA_AI_MILITARY_FRONT_gate_triggers.txt:1656`) |
| JAP THEATRE (`WA_AI_MILITARY_COUNTRY_JAP_THEATRE.txt`) | `area_priority` philippines 1000, east_asia/malaysia 1000, central/south pacific +80 to +200, australia -200 | focus / war gates |
| Co-Prosperity FRONT (`WA_AI_MILITARY_FACTION_CO_PROSPERITY_FRONT.txt`) | China-front priority, Pacific bias +120/+75, minors home hold -1500 | faction triggers; **no naval content** |

**DERIVED** observations:
- `attack_hawaii` is a `front_unit_request`: it only sizes a front that already exists; nothing
  asks Japan to invade Hawaii (no `invade USA` > 0, no `invasion_unit_request` on 629).
- While `complete_southern_expansion` holds, the IJN is walled out of every route east and
  south-east of the Marianas; once MAL+PHI+INS capitulate the block aborts and **no naval guidance
  replaces it** (no dominance target, no raid region, no forward base beyond 94/75).
- The six southern-expansion windows end 1942.3.15. A war that starts late (focus timing is emergent:
  `JAP_strike_south` `ai_will_do` has no date term, `common/national_focus/japan.txt:5521-5541`) misses
  both the ai_strategy windows and the scripted landings whose day has passed.
- The legacy DEFAULT mission fix (strike force -500 / patrol -1000) reaches JAP; its own escort bar
  is +150 before 1941 and default afterwards.

**MEASURED** (`WORK.md` usa-pacific-hoard, campaign `d1c51a6c`): JAP entered war with USA 1941.12.4 in
that run — so the calendar's day-341 landings can line up.

`events/WA_AI_JAP.txt` (MEASURED): leader promotions + state transfers/controller flips of RAJ states
288/640/432/430 when SIA/IPM hold them. **No naval content.**

---

## 8. Known problems (from WORK.md, lessons log, memory)

| Failure mode | Source | Label |
| --- | --- | --- |
| Allied invasion foothold deadlock: ENG/USA/FRA held **zero** type-3 (naval invasion) orders for 30 months (1942.12→1945.6); `invasion_cap_without_foothold` -100 prevents the foothold that would disarm it; `dday_hold` -2000, reservation re-stamped monthly, FRA under `minor_allies_dont_invade`. Candidate subject, not admitted | `WORK.md:97-111` (campaign `24933fb9`) | MEASURED |
| Italy 1943 beachheads (Avalanche/Slapstick) die: WEST freeze stamps -200 on every Allied invasion for 90 days regardless of beachhead survival; no engine invasion order on any Ally | memory `campaign-66636ff4-italy-1943.md` | MEASURED (in that note) |
| D-Day rollback: posture local ratio 1.5 without hysteresis; later D-Day = scripted Aquitaine roll (variant 95) crushed within a month | memory `campaign-af003548-findings.md`, `campaign-5ee2d112-bhutan-findings.md` | MEASURED (in those notes) |
| Permanent suppression without exit (`dday_hold` branch 2 date + JAP war) kept France at 0 Allied divisions 18 months | `lessons-log.md:1906` | MEASURED |
| USN ran 0 % convoy escort: escort objectives come from own convoy losses (danger), score terms only rank | `lessons-log.md:1915` | MEASURED |
| RN heavy hulls never entered the Med (0 of 46); fix = Alexandria base + dominance; next lever named `MISSION_STRIKE_FORCE` | `WA_AI_MILITARY_SYSTEM.md` §21 | MEASURED |
| Italian convoy pool dented 1.9 % over 3 years — no Allied raid region on 29/269/327 before Fix 122 | §19 | MEASURED |
| `MISSION_CONVOY_RAID` literal shipped and failed at boot (substring grep) | §19 | MEASURED |
| Dominions ran 1 naval factory each: no `ai_equipment` design for their tech tree | `lessons-log.md:2222` | MEASURED |
| USA Pacific island buffers hoarded 62 % of the army; capped twin shipped, harness run owed | `WORK.md:2320-2400` | MEASURED |
| `naval_mission_threshold` sign misread (positive suppresses) | `lessons-log.md:1356` | MEASURED |
| Overseas theatre needs a destination (Tunis bridge); landing sensors missing | `lessons-log.md:2062` | MEASURED |
| `naval_dominance` 500 vs doc 70-80 / engine 0-100 | §1.3 above | MEASURED drift; effect ASSUMED |
| Capital-ship gate comment vs code direction | §5.1 above | DERIVED |

---

## 9. Gaps (for the Kaiserreich comparison)

Nothing below is measured in a campaign; each is a repo absence (**MEASURED**) and its consequence
is **DERIVED** unless stated.

1. **No engine-driven Japanese naval campaign.** Japanese expansion = teleported divisions on a date
   list; the IJN is never asked to win sea control first. Against AI targets naval control is not even
   checked.
2. **No `naval_dominance` for any non-Allied country**, and none in the Pacific for anyone.
3. **No JAP `naval_convoy_raid_region`, no `naval_invasion_support_priority` anywhere, no invasion-support
   thresholds** — the engine's invasion-support mission is shaped only by goals (4-15) and the two
   0.2 / 0.3 defines.
4. **No JAP/Pacific fleet or taskforce templates**; the only strike-force template needs 2 CV + 2 BB
   + 10 CL; no carrier-group template, no surface-action group, CA/BC patrol templates commented out.
5. **No post-mid-1942 Japanese plan**: no Midway / Port Moresby / Guadalcanal counter, no defensive
   perimeter dominance, no forward strike base beyond Iwo Jima 94 / Taiwan 75 / home 90-240.
6. **Date-windowed JAP ai_strategy** (1941.12-1942.3.15) and a calendar that does not retry when the
   war is late → an ahistorical war timing leaves Japan with suppressors only (principle 1 risk).
7. **Competitive difficulty = no scripted landings at all**, and the engine layer was not built to
   carry the Pacific alone.
8. **No Co-Prosperity faction naval file**; Axis faction naval blocks never reach Japan.
9. **No JAP naval `unit_ratio`**; volume is engine + dockyard ratio 40; Historical capital gate may
   zero BB/CV role ratios once the treaty collapses (direction unverified), leaving 9 scripted spawns.
10. **No Yamato-class spawn** in the Capitals calendar.
11. Doc drift: `naval_dominance` 500 in code vs 70-80 in §21 / §4.

**ASSUMED** — whether Kaiserreich/Sheep's submod covers these with ai_strategy phases, ai_navy
templates or scripted effects is not in this repo; the comparison itself needs that submod's files.
