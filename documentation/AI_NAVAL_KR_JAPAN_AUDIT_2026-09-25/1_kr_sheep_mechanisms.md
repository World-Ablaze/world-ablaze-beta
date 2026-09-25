# Audit: how Sheep's KR Japan AI (and Kaiserreich base) make the Japanese AI good at naval play

Date: 2026-09-25. Read-only audit. Paths abbreviated:

| Short | Full path |
| --- | --- |
| `S/` | `C:\Jeux\steamapps\workshop\content\394360\3677914657` (Sheep's Kaiserreich Japan AI, descriptor `supported_version="1.19.3.0"`, dependency `Kaiserreich`) |
| `K/` | `C:\Jeux\steamapps\workshop\content\394360\1521695605` (Kaiserreich base) |
| `G/` | `C:\Jeux\steamapps\workshop\content\394360\3265939166` (Sheep's general vanilla mod, v1.17.3 — NOT part of the KR stack) |
| `V/` | `C:\Jeux\steamapps\common\Hearts of Iron IV` (engine install, oracle) |

Labels: **MEASURED** = read in the named file:line. **DERIVED** = inferred from MEASURED facts (source named). **ASSUMED** = unverified (engine internals, weighting, arbitration).

---

## 0. Verdict (short)

- **MEASURED** KR base does NOT contain Sheep's submod: zero `LSM_*` files or identifiers anywhere under `K/common`, `K/events` (grep).
- **DERIVED** But the two share ancestry: KR `JAP.txt` already carries the whole invasion-gating framework (stalemate flag, `invade -1000` tag lists, beachhead whitelist, follow-up rush, 90-day sync) and blocks with Sheep's naming style (`JAP_convoy_voy_voy`, also in `G/common/ai_strategy/JAP.txt:67`). Sheep's submod is a fork that *extends* that framework — it is not where the framework was born.
- **DERIVED** The submod's naval strength is **invasion discipline, not fleet cleverness**: it tells the engine *when not to invade* (land front moving, too few divisions, China not done), *where only* (8 Chinese coastal states, then SE Asia mainland cores), *how far* (km fences from allied coasts), and *what to do after landing* (rush the beachhead). Fleet-side it mainly shapes production (torpedo destroyers, subs, cruisers) and deletes KR's invasion-support fleet/supremacy strategies.
- **MEASURED** Sheep's defines file is entirely commented out (`S/common/defines/LSM_JAP_defines.lua:1-16`, line 16 `-- deactivated for the time being`). The only live define overrides are KR's.
- **MEASURED** None of `naval_mission_threshold`, `strike_force_home_base`, `naval_avoid_region`, `naval_invasion_dominance_weight`, `convoy_raiding_target`, `naval_blockade`, `coast_defense` appear in Sheep's three ai_strategy files, nor in KR `JAP.txt` (grep counts = 0).

---

## 1. Who owns what — KR base vs Sheep submod

### 1.1 File-level override

Sheep ships `common/ai_strategy/JAP.txt` with the same relative path as KR → **DERIVED** it fully replaces KR's `JAP.txt` (HOI4 file-override by path; KR itself declares `replace_path="common/ai_strategy"`, `K/descriptor.mod`). Sheep's two extra files `LSM_JAP.txt`, `LSM_JAP_warplan.txt` add blocks. KR files Sheep does NOT override stay live: `K/common/ai_strategy/00_naval_production.txt`, `00_default.txt`, `GEA.txt`, `china.txt`, `K/common/ai_navy/goals/goals_generic.txt`, `K/common/on_actions/on_actions_Japan.txt`, `K/common/defines/KR_defines.lua`.

### 1.2 Block-by-block diff of KR `JAP.txt` (49 blocks) vs Sheep (all three files)

Computed with a block parser (scratchpad `blocks.py`). **MEASURED**:

| Status | Blocks |
| --- | --- |
| Identical in both | `JAP_hates_reichspakt`, `JAP_hates_chinese_claimants`, `JAP_flattening_the_mountains`, `JAP_home_islands_are_safe_for_now`, `JAP_build_mils`, `JAP_no_garrison`, `JAP_raid_the_ocean_90`, `JAP_avoid_Shanghai_…`, 4× `JAP_spy_on_*`, `JAP_build_intel_agency`, `JAP_1936_research` |
| In both, Sheep modified | `JAP_dont_send_expeditionary_forces_to_FNG`, `JAP_convoy_voy_voy`, `JAP_build_up_asw_warfare`, `JAP_build_up_convoy_warfare`, `JAP_template_prio`, `JAP_parting_the_seas`, `JAP_raid_the_ocean_79`, **`JAP_beat_china_first`**, **`JAP_beat_GEA_and_friends_next`**, **`JAP_no_naval_invasion`**, **`JAP_do_not_naval_invade_these_state`**, **`JAP_only_naval_invade_these_states`**, **`JAP_only_naval_invade_china_once`**, **`JAP_bypass_the_islands`**, 5× `JAP_avoid_<port>_…`, research 1937/1938, 8× airbase, 3× Fengtian buffers. The bold ones were MOVED into `LSM_JAP_warplan.txt`. |
| KR only — **dropped by Sheep** (dead in the submod) | `JAP_no_naval_invasion_overseas` (K/…/JAP.txt:448), `JAP_follow_up_on_invasion_priority` (K:990, replaced by Sheep's `_2`/`_3`), `JAP_sync_invasions_on_china` (K:1051) |
| Sheep only (new) | JAP.txt: dock/airbase access denial, NAP refusal, subject support, 4 new convoy ladders, `JAP_build_up_invasion_warfare`, `JAP_build_up_kantai_kessen`, `JAP_build_kantai_kessen`, sonar research, templates, air, resources, `JAP_build_mils_2`, research 1940/1942. LSM_JAP.txt: 11 blocks (division limiter, role ratios, production, research). Warplan: 32 blocks incl. `JAP_protect_home_island`, follow-up `_2/_3`, intercontinental range fences, Oceania, all-hands-on-deck, paratrooper buffers, 16 `JAP_great_*_campaign` port/bunker builders, `JAP_reset_all_naval_invasion_frontline`, `JAP_support_RSA` |

### 1.3 What Sheep changed inside the moved invasion blocks (MEASURED, difflib)

| Block | KR | Sheep |
| --- | --- | --- |
| `JAP_only_naval_invade_these_states` (K:696-887 → S warplan:596-738) | includes 5× `naval_invasion_support_priority` (regions 77/76/75 = 300, 94/78 = 150) and 5× `naval_dominance` (77 = 555, 76 = 100, 75/94/78 = 25) — K/…/JAP.txt:797-855 | **all 10 removed**; added exit when China unified/key states held; added `JAP_landing_priority_boost days < 90` to the suppress list; `num_divisions < 100` AND-gate |
| `JAP_no_naval_invasion` | 5-clause stalemate OR | same + `JAP.num_divisions < 80` clause + `num_divisions < 100` AND on the "enemy outnumbers us" clause + China-done exit |
| `JAP_only_naval_invade_china_once`, `JAP_do_not_naval_invade_these_state` | — | + China-done exit, + `num_divisions < 150` gate (restriction lifts at 150 divisions) |
| `JAP_bypass_the_islands` | invasion request on SE-Asian mainland cores `value = 5`, `is_island_state = no`; small-pop penalty unconditional | `has_war_with = GEA` added; island filter removed on the invasion request, `value = 15`; small-pop penalty only while `owner surrender_progress < 0.70` |
| `JAP_beat_GEA_and_friends_next` | `front_unit_request 50` on GEA/DEI/PHI | + INS, + `invasion_unit_request 15`, + China-done path |
| `JAP_avoid_Ningbo…/Fuzhou/Shantou/Hong_Kong` | `-200` | `-75` |
| `JAP_1938_research` | `mtg_landing_craft` weight 10000 (K:1622-1629) | 2500 (S/JAP.txt:1028) |

### 1.4 ai_navy, strategy plans, equipment

| Piece | KR base | Sheep | Label |
| --- | --- | --- | --- |
| Taskforce templates | 8 JAP templates incl. `JAP_StrikeForce_1` (min 1 CV+1 BB+1 BC+2 CA+4 CL+12 DD), `JAP_NavalInvasionSupport_1` (mission `naval_invasion_support`, min 1 BB, opt 1 BB 2 CA 8 DD, factor 5), `JAP_PatrolDominanceForce_1` (factor 0), `JAP_ConvoyEscort_2` | 5 templates: `JAP_KidoButai_1`, `JAP_PatrolReconForce_1`, **new** `JAP_DeathSquad_1`, `JAP_ConvoyRaiding_1`, `JAP_ConvoyEscort_1`. StrikeForce, NavalInvasionSupport, PatrolDominance, ConvoyEscort_2 **deleted** | MEASURED `K/common/ai_navy/taskforce/JAP_taskforce_templates.txt:1-205`, `S/…:1-122` |
| Only template with `naval_invasion_support` mission in all of KR | `JAP_NavalInvasionSupport_1` (grep count: JAP file 1, all others 0) | none | MEASURED; **DERIVED** in the submod no JAP template is written for invasion support |
| Fleet templates | 4 fleets | 5 fleets: + `JAP_dominance_fleet_3` (DeathSquad 1 req + 9 opt); fleet_1 optional patrols 4→8; escort fleet 5+5+5 → 4+4 | MEASURED `S/common/ai_navy/fleet/JAP_fleet_templates.txt:1-46` |
| Naval goals | KR replaces `ai_navy/goals` with only `goals_generic.txt` (no `goals_JAP.txt`) | not touched | MEASURED `K/descriptor.mod` replace_path + `K/common/ai_navy/goals/goals_generic.txt:1-69` |
| Strategy plans | 5 plans | same 5 + `JAP_no_tot_eco`, `PRF_slave_to_the_great_emperor`, `JAP_block_india_mission`; focus lists reordered, adds `JAP_maintain_kantai_kessen`, `JAP_experimental_division`, `JAP_improve_the_long_lance` into dem/milcent/showa plans | MEASURED `S/common/ai_strategy_plans/JAP_strategy_plan.txt:58-59,152-155,240-252,326-389` |
| ai_equipment naval | `KR_DD_screens`, `KR_light_cruisers`, `KR_heavy_cruisers` open to all | same files with `blocked_for = { JAP }` + JAP-only `LSM_japan_screens/light_cruisers/heavy_cruisers` | MEASURED diff: only the `blocked_for` line differs |
| Marine templates | `marines.txt` generic | `marine_generic` blocked for JAP; `marine_artillery` JAP-only; `LSM_japan_marines.txt` role `marine_japan` | MEASURED `S/common/ai_templates/marines.txt:5-12,55-78`, `LSM_japan_marines.txt:5-6` |

---

## 2. Catalogue of mechanisms

Class key: **A** MECHANICAL (portable engine technique), **B** BALANCE-DEPENDENT, **C** SCENARIO-SPECIFIC (hard-coded KR tags/states/regions). Where a C mechanism has a portable core, the core is named.

### 2.1 Invasion gating — WHEN to invade (the heart of the system)

| # | Mechanism | Where | Exact lever + magnitude | Gating | What it achieves | Owner | Class + reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | **Land-stalemate detector** | `K/common/on_actions/on_actions_Japan.txt:247-261` | `on_state_control_changed` → `JAP = { set_country_flag = JAP_SSJW_last_major_frontline_change_flag }` | ROOT allied to JAP and at war with CUF, FROM allied to CUF, `FROM.FROM = { is_coastal = no }` (an INLAND state changed hands) | Timestamp of "the land front last moved". **DERIVED** read back via `has_country_flag = { flag = … days < N }` | KR (MEASURED) | **A** — flag timestamp + on_action is pure engine; the CUF tag is the only scenario part |
| G2 | **No-invasion switch** `JAP_no_naval_invasion` | `S/…/LSM_JAP_warplan.txt:350-533` | `invade id=<22 tags> value = -1000` (GEA GER DEI PHI USA AST HAW RAJ + 14 Chinese tags) ; `invasion_unit_request state_trigger={always=yes} -100`; `naval_invasion_focus -25` | During CUF war: ON if front moved < 60 d; OR allied Chinese < 50 div and moved < 90 d; OR (Chinese enemy outnumbers JAP AND JAP < 100 div); OR JAP < 80 div; OR Chinese ally surrender > 0.1; OR continental-warfare idea and moved < 30 d. Outside CUF war: ON until `mtg_landing_craft` AND focus `JAP_claim_colonies`. OFF once China unified/key states held (`LSM_JAP_control_all_key_states`, `S/common/scripted_triggers/LSM_JAP_scripted_triggers.txt:1-12`) | Invasions only when the land war is stuck AND Japan has the divisions to spare. **ASSUMED** per vanilla doc `V/common/ai_strategy/_documentation.md:335-343` ("If it's negative, it avoids invasions completely") | KR framework, Sheep added `<80`, `<100`, China-done exit | **A** — reads engine state (flags, `num_divisions`, `surrender_progress`); the tag list is re-expressible as "every enemy" |
| G3 | Division-count release | same blocks, warplan:552, 760 | `check_variable = { num_divisions < 150 }` in the enable of the two "restrict" blocks | < 150 divisions | **DERIVED** at ≥150 divisions both restrictions (G5 blacklist, G6 once-only) switch off → free invasions | Sheep | **A** — capacity gate, tag-free |
| G4 | China-first area weighting `JAP_beat_china_first` | warplan:73-205 (KR K:287-412) | `area_priority china +300`, `pacific -100`; `front_unit_request area china +300`, `pacific -300`; `invasion_unit_request area pacific -100`; `put_unit_buffers ratio 0.1` Taiwan 524 + Ryukyu 526; air/cv-plane `equipment_production_factor -100` (cv_fighter, cv_cas, cv_naval_bomber, tac, naval_bomber, strat), fighter -66, cas -50 | any Chinese/MON/LEC enemy AND China not done | One war at a time; no Pacific adventure while China is open; no carrier air wing spending during SSJW | KR (Sheep softened fighter/cas and added China-done exit) | **C** — hard-coded areas/tags; portable core = "area_priority + unit_request on one theatre while another war is open" |
| G5 | Beachhead **blacklist** `JAP_do_not_naval_invade_these_state` | warplan:535-595 | `invasion_unit_request` on 33 Chinese coastal states `-100` | at war with owner of Nanjing (613) (or FNG is), 613 and 1075 (Nantong) not held, no CUF idea_3, China not done, < 150 div | Never land in the wrong Chinese coastal pockets | KR, Sheep added gates | **C** — state-ID list |
| G6 | Beachhead **whitelist** `JAP_only_naval_invade_these_states` | warplan:596-738 | `invasion_unit_request` on 8 states (613 Nanjing, 596 Hangzhou, 746 Ningbo, 1067 Jinhua, 1065, 744 Qingdao, 1075 Nantong, 598 Yancheng) `+105`; `naval_invasion_focus +105`; `invade CHI/LEP/ANQ/QIE +1005` (= ×11.05 importance per doc); `invade GEA GER DEI PHI USA AST -1000` | tech `mtg_landing_craft` + focus `JAP_claim_colonies`; Nanjing's owner at war; 613 and 1075 not yet held; China not done; NOT (any G2 stalemate clause) AND NOT `JAP_landing_priority_boost days < 90` | The ONE decisive landing: the Yangtze-mouth hook behind the Chinese line, only when the land war stalls | KR framework; Sheep removed KR's supremacy/support lines, added 90-day post-landing cooldown | **C** — state IDs + tag multipliers; portable core = "whitelist + `invade` multiplier + cooldown after landing" |
| G7 | **Invade once** `JAP_only_naval_invade_china_once` | warplan:740-847 | 14× `invade <Chinese tag> -1000`; `invasion_unit_request always -100`; `naval_invasion_focus -100` | as G6 but 613 OR 1075 already held by ROOT or ally | Once the hook exists, stop landing in China; feed the beachhead by land | KR, Sheep added gates | **C** — tag list; portable core = "switch off invasions against target once a named foothold is held" |
| G8 | Post-China pivot `JAP_beat_GEA_and_friends_next` | warplan:297-349 | `front_unit_request` +50 and `invasion_unit_request` +15 on GEA/DEI/PHI/INS | China done or no Chinese enemy, and at war with GEA/DEI/PHI | Turn the invasion machine south | KR + Sheep | **C** — tags |
| G9 | Mainland-first in SE Asia `JAP_bypass_the_islands` | warplan:849-919 | `front_unit_request` Malaya states 846/1002/751/963/336 +10; mainland cores of PHI/GEA/MAL/INS/DEI +5; `invasion_unit_request` all their cores at war +15; `invasion_unit_request state_population_k < 50` **-100** while owner surrender < 0.70 | foci `JAP_claim_colonies` + `JAP_ultimatum`, war with GEA, (GER war OR no CUF war) | Skip worthless atolls, land where population/VP matters, pick up small islands only when the owner is collapsing | KR, Sheep changed values | **A** for the `state_population_k < 50` + `surrender_progress` filter (tag-free); rest **C** |
| G10 | Port-avoidance when isolated `JAP_avoid_<Tianjin/Shanghai/Ningbo/Fuzhou/Shantou/Hong_Kong>_…` | warplan:1573-1729 | `front_unit_request` (and for Ningbo `invasion_unit_request`) on the treaty-port pair `-25`/`-75` | port owned by JAP/ally but all neighbour states not held | Don't pour divisions into a surrounded treaty port | KR | **C** — state IDs; portable core = "deprioritise an enclave when no adjacent state is held" |
| G11 | Anti-player home defence `JAP_protect_home_island` | warplan:207-295 | `garrison +50`; `front_unit_request` cores +100, non-cores -100; `invasion_unit_request` non-Chinese -2000, Chinese +30; `front_control country_trigger=chinese ordertype=invasion execute_order=no` | fading-sun mission or surrender > 0.1, AND a **human** Chinese enemy with navy > 10 or paratroopers near Kyushu (528, < 200 km) | Only vs a human: pull home, keep invasions vs China prepared but not launched | Sheep | **A** — `is_ai = no` + `has_navy_size` + `divisions_in_state unit=paratrooper` are tag-free except `is_chinese_tag` |

### 2.2 Invasion execution — AFTER landing

| # | Mechanism | Where | Lever + magnitude | Gating | Achieves | Owner | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | **Beachhead tagging** | `K/common/on_actions/on_actions_Japan.txt:263-314` | `on_naval_invasion` → state flag `landing_priority` 30 d (first) / 25 d (subsequent); country flag `JAP_landing_priority_boost` (re-set each landing); `JAP_recent_naval_invasion` 30 d | ROOT tag JAP, landed state `is_island_state = no` | Marks the fresh beachhead so strategies can target it | KR | **A** — on_action + state flag, tag is ROOT |
| E2 | **Beachhead rush** `JAP_follow_up_on_invasion_priority_2` | warplan:920-961 | `front_control` on states flagged `landing_priority` or their neighbours, `ratio 0.0`, `priority 200`, `ordertype front`, `execution_type rush_weak`, `execute_order yes` | recent invasion flag, boost < 120 d, day-mod-14 < 8 (8 days on / 6 off), **and China done** | Forces the landed army to attack out of the beachhead immediately, in pulses | KR (K:990-1049, 60 d, ungated, with `invasion_unit_request -200` on the landed-in country), Sheep split it and gated it on China done | **A** — flag-keyed `front_control`, no tags |
| E3 | Beachhead reinforcement `JAP_follow_up_on_invasion_priority_3` | warplan:962-991 | `front_unit_request` flagged states/neighbours `+4` | as E2 without the day window | Keeps divisions flowing to the beachhead | Sheep (KR had +5 inside E2) | **A** |
| E4 | KR define: beachhead keeps priority longer | `K/common/defines/KR_defines.lua:175` | `MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS = 100` (vanilla 20, `V/common/defines/00_defines.lua:3327` "…it will lose its prio status and will act as a regular front") | global | Invasion fronts stay "priority" for 100 conquered provinces instead of 20 | KR | **A** — engine define, global |
| E5 | Periodic invasion reset (Sheep) `JAP_reset_all_naval_invasion_frontline` | warplan:2804-2837 + `S/common/on_actions/on_actions_LSM_Japan.txt:48-58` | `invasion_unit_request country_trigger always -9999`, `state_trigger always -9999`, `naval_invasion_focus -9999` | at war, not at war with CUF, flag `JAP_refresh_frontline_stuck_check` unset or > 90 d old (set when an ally of JAP takes an ISLAND state from an enemy), day-mod-90 < 2 | **DERIVED** 2-day wipe every 90 days when no island has fallen for 90 days → the engine drops stale invasion plans and re-plans. **ASSUMED** that a -9999 request cancels existing invasion orders | Sheep | **A** — tag-free |
| E6 | Periodic invasion reset (KR default, all majors) `default_refresh_naval_invasion_orders` | `K/common/ai_strategy/00_default.txt:617-647` + `K/common/on_actions/00_on_actions_global.txt:3043-3052` | same three -9999 lines | major, at war, `has_recent_naval_invasion` (125 d, set by global `on_naval_invasion`) unset or > 120 d, day-mod-120 < 3 | Same idea, keyed on "no landing for 120 days" | KR | **A** |
| E7 | Beachhead port building `JAP_great_indonesia/alaskan/australian_campaign_*` (16 blocks) | warplan:1949-2803 | `build_building naval_base target=<province> value 4` (Indonesia) / `10` (Alaska, Australia); Alaska also `bunker value 3` on 9 provinces | JAP has divisions in the state, state owner at war with JAP, target naval base level < 4 / < 10 | **DERIVED** supply ports at landing sites so the beachhead is not supply-starved. **ASSUMED** the engine lets AI build in occupied-but-not-owned states | Sheep | **C** — province IDs; portable core = "build_building naval_base where my divisions stand in enemy-owned coastal state" |

### 2.3 Invasion reach — HOW FAR

| # | Mechanism | Where | Lever + magnitude | Gating | Achieves | Owner | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | **Range fence, all majors** `default_naval_invasion_range` | `K/common/ai_strategy/00_default.txt:557-615` | `invasion_unit_request -2000` on any state with no allied coastal/island state within 3000 km (anchors: Hawaii 629 < 1200, Johnston 630 < 1200, Oregon 385 < 800, Phoenix 642 < 800, 757 < 1000) | major at war | Kills trans-ocean fantasy invasions | KR | **A** — `distance_to` + `is_coastal`; anchors are C |
| R2 | **Range fence, Japan** `JAP_intercontinental_warfare_excluded_range` | warplan:992-1183 | tier 1: `-2000` beyond 3000 km of an allied coastal state (exceptions near Hawaii/Oregon/Phoenix only if no Reichspakt Asian holder GEA/SIA/DEI/PHI alive); tier 2: `-100` beyond 800 km; tier 3: `-2000` on 7 Indian-Ocean/South-Pacific islands (642 941 635 281 710 422 1119) while a Reichspakt Asian holder is alive | always | Island-hop discipline: each invasion must be within 800 km of a coast Japan (or ally) already holds | Sheep | **A** — tag-free core; exception anchors/tags C. **ASSUMED** `is_ally_with` counts JAP itself (KR default uses `is_ally_with = FROM.FROM` the same way) |
| R3 | Range fence release `JAP_intercontinental_warfare_included_range` | warplan:1184-1292 | `+15` within 500 km of allied coast (+ anchors); `+60` within 300 km of Singapore 336 / Batavia 1020 at war | flag `JAP_defeated_by_china` OR allied to CHN | Alternate path when China is lost/allied: go south | Sheep | **C** — scenario path flag + states |
| R4 | Oceania pivot `JAP_area_priority_oceania` | warplan:1293-1365 | `area_priority oceania +100`, `pacific +50`; `invasion_unit_request` Asian/Oceanian enemies +25; Panama 685/304 +100; `garrison -80` | same path flag, GEA gone/capitulated/unaligned, no Reichspakt Asian holder, not allied to AST | Late-game Pacific expansion | Sheep | **C** |
| R5 | `JAP_oceania_invade_reverse` | warplan:1366-1481 | `reversed = yes`; `invade id=JAP value = 1000` | enable evaluated on Asian/Oceanian/American/Indian enemies near JAP-held coast | **ASSUMED** semantics of `reversed` (not in vanilla doc). Under the reading consistent with KR's own reversed block (K:448-467, where the enabling country is the actor), it RAISES enemy invasions of Japan — contrary to intent. Flag for manual check | Sheep | **C** |
| R6 | All-in Pacific `JAP_all_hands_on_deck` / `_RUS` | warplan:1482-1572 | `garrison -1000`; `front_unit_request` non-neighbour enemies +60; `invasion_unit_request` enemies within 500 km of allied coast / Hawaii / Johnston / Midway / area pacific +25. RUS variant: `garrison -100`, fronts vs RUS allies +100 | allied with CHN, navy > 150 ships, no RUS war / RUS war and no surrender | Everything to the Pacific once the fleet is big | Sheep | **C** |

### 2.4 Garrison / manpower release (feeds invasions)

| # | Mechanism | Where | Lever | Gating | Achieves | Owner | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | `JAP_no_garrison` | S/JAP.txt:764-778 (= K) | `garrison -1000`, `garrison_reinforcement_priority -100` | `surrender_progress < 0.01` | No divisions parked on home coasts | KR | **A** |
| M2 | `JAP_home_islands_are_safe_for_now` | S/JAP.txt:709-722 (= K) | `garrison -25` | `enemies_naval_strength_ratio < 1.5` | Strips garrison while enemy navies are not 1.5× stronger | KR | **A** — naval-strength trigger, tag-free |
| M3 | KR garrison defines | `K/common/defines/KR_defines.lua:177-185` | `AREA_DEFENSE_SETTING_COASTLINES = false` (vanilla true), `…PORTS = true`, `…VP = true`, `…AIRBASES = true` | global | **DERIVED** no AI (Japan's victims included) garrisons open coastline, only ports/VPs → soft landing sites everywhere | KR | **A** — engine define (global, symmetric) |
| M4 | Home-island buffers vs paratroopers | warplan:1853-1948; also G4 (Taiwan/Ryukyu 0.1) | `put_unit_buffers ratio 0.1` (524, 526), `0.2` (528, 1102), `0.5` (528, 529, 1104, 531), `subtract_*_from_need = yes` | human Chinese enemy with `paratroopers` and paratroopers < 140 / 60 km from Kyushu | Reactive home defence only when a real threat exists | Sheep | **A** core (reactive `put_unit_buffers`); state IDs C |
| M5 | Subjects de-garrison `JAP_manning_the_frontline` | warplan:2909-2923 | `garrison -75` | subject of JAP, no surrender, no enemy neighbour | Puppets send troops forward | Sheep | **A** |

### 2.5 Fleet production (what ships exist)

| # | Mechanism | Where | Lever + magnitude | Gating | Achieves | Owner | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | KR JAP base ratios | `K/common/ai_strategy/00_naval_production.txt:249-273` | `role_ratio naval_submarine +10`, `naval_screen +30`, `naval_cruiser_light +35` | always (`tag = JAP`) | Light-heavy baseline | KR | **B** — the right ratio depends on ship stats |
| P2 | KR late-game majors | same:363-401 | capital_bb +10, carrier +10, CL +20, CA +10 | `date > 1942.1.1` | Capital ships late | KR | **B** |
| P3 | KR convoy-threat reaction | same:405-472 | screen +200, others -50, `unit_ratio convoy +50` | `convoy_threat > 0.2` | ASW surge under raiding | KR | **A** — trigger-driven, tag list only filters majors |
| P4 | Destroyer count ladder | S/JAP.txt:227-264 | `role_ratio naval_screen +200` while DD < 170; `+50` more if dockyards > 50 and DD < 170 (KR: +50 while DD < 99) | `has_navy_size unit=destroyer` | Mass destroyers first (ASW + torpedo screens) | Sheep (KR +50/<99) | **B** — 170 DD is a KR-economy number; technique (count-threshold role_ratio) is A |
| P5 | Submarine ladder | S/JAP.txt:266-284 | `role_ratio naval_submarine +1000` while subs < 30 and not holding Hawaii 629 (KR: +50 while < 29) | `has_navy_size unit=submarine` | 30 subs early for raiding | Sheep | **B** |
| P6 | "Kantai kessen" unlock | S/JAP.txt:286-322 | CA +50, CL +50, screen +50 | DD > 169 AND (subs > 29 OR holds Hawaii) | Cruisers only after the screen/sub quotas are met | Sheep | **B** |
| P7 | Navy XP → designs | S/JAP.txt:323-336 | `navy_xp_spend_priority equipment_variant +500` | `date > 1938.1.1` | XP spent on ship designs, not left idle | Sheep | **A** |
| P8 | ASW research | S/JAP.txt:337-423 | `research_tech` sonar/improved/advanced/modern sonar `+100` | until improved_sonar; again after 1940.8.1 + `sp_air_radar` | ASW tech stays current | Sheep | **B** — value of sonar is balance |
| P9 | Convoy min-factory ladder | S/JAP.txt:162-225; KR `00_naval_production.txt:545-623` | `equipment_production_min_factories convoy` 5 (< 1000), +10 (war, < 3000), +10 each at > 60/80/100 dockyards (< 3000); KR majors +5/+5/+3/+2 on stockpile_ratio | stockpile / war / dockyards | Enough convoys for invasions + supply. **ASSUMED** multiple active min_factories strategies sum | Sheep + KR | **A** |
| P10 | Torpedo-heavy JAP designs | `S/common/ai_equipment/LSM_japan_screens.txt:1-105`, `LSM_japan_light_cruisers.txt:1-119`, `LSM_japan_heavy_cruisers.txt:1-33` | JAP-only groups, group priority 50000 / 10000; DDs: 2–4 `ship_torpedo`, 1 depth charge, sonar, radar; CLs: 2 torpedoes + light-medium batteries; CA role → `ship_hull_torpedo_cruiser` with 4 torpedoes | `available_for = { JAP }`; KR generic DD/CL/CA files `blocked_for = { JAP }` | Every screen is a torpedo boat with ASW. Module category tokens (`ship_torpedo`) are valid — vanilla uses them (`V/common/ai_equipment/ENG_naval.txt:44`) | Sheep | **B** — torpedo value depends on combat balance |
| P11 | Quality-shipbuilding buff edit | `S/common/ideas/JAP ideas (Japan).txt:1849-1930` vs KR | light hull: `lg_attack/sub_attack +0.1` → `torpedo_attack +0.1, surface_visibility -0.1, naval_speed +0.1`; cruiser hull `sub_attack` → `naval_speed` | idea from focus `JAP_maintain_kantai_kessen` (`K/common/national_focus/JAP focus (Japan base).txt:5108-5131`) — applies to human JAP too | Stat buff matching the torpedo doctrine | Sheep | **B** |
| P12 | Naval focuses pulled into AI plans | strategy plan (§1.4) | `JAP_maintain_kantai_kessen` (quality shipbuilding), `JAP_experimental_division` (naval_innovation: navy XP +10%, naval research +10%, +1 naval facility), `JAP_improve_the_long_lance` (+15% torpedo screen penetration) | plan flags `JAP_dem_ai` / `JAP_milcent_ai` / `JAP_showa_ai` | AI actually takes the naval focus branch | Sheep (focus rewards KR, MEASURED focus file:5133-5214, ideas file:1807-1834) | **B** — rewards are KR content |

### 2.6 Fleet organisation and missions (ai_navy)

| # | Mechanism | Where | Lever | Gating | Achieves | Owner | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | `JAP_KidoButai_1` strike force | S taskforce:1-35 | mission `naval_strike`, `keep_updated = yes`, min 1 carrier, optimal 4 CV 4 BC 4 BB 8 CA 35 CL 25 DD, factor 100 | `original_tag = JAP` | One big carrier-led strike group; KR's stricter all-types `JAP_StrikeForce_1` removed so a single carrier suffices to form it | KR (CA 4→8, CL 25→35 by Sheep) | **A** — template semantics per `V/common/ai_navy/taskforce/_documentation.md` |
| F2 | Patrols | S taskforce:37-53; fleet_1/2 | `naval_patrol`, min 3 DD opt 5 (KR 2/4); dominance_fleet_1 optional 8 (KR 4) | always | More, bigger DD patrols = more spotting for the strike force | Sheep | **A** |
| F3 | `JAP_DeathSquad_1` surface raiders + `JAP_dominance_fleet_3` | S taskforce:55-83, fleet:21-28 | `convoy_raiding`, min 10 DD, opt 5 CA 5 CL 20 DD; ai_will_do 10, `factor = 0` unless JAP controls Hawaii 629 | holds Hawaii | After Pearl, cruiser-destroyer groups raid (the P5 sub quota also turns off) | Sheep | **C** — Hawaii gate; portable core = "switch raider template on when a forward base is held" |
| F4 | Sub raiders | S taskforce:85-103 | `convoy_raiding` min 2 opt 4 subs, factor 2 (KR 3/6, factor 1) | always | Smaller wolfpacks, more of them | Sheep | **A** |
| F5 | Escorts | S taskforce:105-122, fleet:39-46 | `convoy_escort` min 3 opt 6 DD; escort fleet 4 req + 4 opt | always | Convoy protection for invasion lanes | KR/Sheep | **A** |
| F6 | **Deleted invasion-support fleet** | KR taskforce:124-147 absent in S | — | — | **DERIVED** with G6's deletion of 5 `naval_invasion_support_priority` and 5 `naval_dominance` lines, Sheep removed every JAP-specific lever that parks the fleet on invasion lanes. **ASSUMED** the generic goal `naval_invasion_support` (priority 10-20, `K/…/goals_generic.txt:1-6`) still assigns some task force | Sheep | **A** (the removal is a portable decision) |
| F7 | Home-water raid regions `JAP_raid_the_ocean_79/90` | S/JAP.txt:780-829 | `naval_convoy_raid_region` 79 (Sea of Japan) `+250`, 90 (Coast of Japan) `+250` | at war AND a home state not fully controlled (Sheep adds: or war with RUS for 79) | **DERIVED** when enemies have landed on Japan, raid their supply convoys at the landing | KR (+RUS by Sheep) | **C** — region/state IDs; core A |
| F8 | KR define: training | `K/common/defines/KR_defines.lua:188` | `MAX_FULLY_TRAINED_SHIP_RATIO_FOR_TRAINING = 0.99` (vanilla 0.7, `V/…/00_defines.lua:3268`) | global | Fleets keep training until ~all ships are fully trained (veteran crews) | KR | **A** |
| F9 | KR define: refit | `KR_defines.lua:191` | `REFIT_SHIP_PERCENTAGE_OF_FORCES = 0.25` (vanilla 0.1) | global | More of the fleet refitted | KR | **A** |
| F10 | KR defines: naval tech via XP | `KR_defines.lua:105-106` | `XP_RATIO_REQUIRED_TO_RESEARCH_WITH_XP = 1.6` (vanilla 2.0), `RESEARCH_WITH_XP_AI_WEIGHT_MULT = 4.0` (vanilla 1.2); comment "needed to make AI research naval techs with XP" | global | Navy XP converted to naval research | KR | **A** |

### 2.7 Doctrine / spirit steering (AI-only ideas & decisions)

| # | Mechanism | Where | Lever | Gating | Achieves | Owner | Class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | Fake navy spirits | `S/common/ideas/LSM_JAP_fake_navy_spirit.txt:1-42` | copies of KR `fleet_interoperability_navy_spirit` (naval_morale +0.20, naval research +5%) and `efficient_communications_spirit` (positioning +0.15) with `visible = { tag = JAP is_ai = yes }`, `ai_will_do factor = 5000` (KR originals factor 1, `K/common/ideas/01 Navy Spirits.txt:291-310,383-398`) | AI JAP only; NCNS DLC / fleet-in-being or line-of-battle doctrine | Forces the AI's navy-spirit pick. **MEASURED** modifiers are identical to the real spirits → a steering trick, not a stat cheat | Sheep | **A** — duplicate-idea + visibility + ai_will_do steering is portable |
| D2 | Free naval subdoctrines | `S/common/decisions/LSM_JAP_decisions.txt:211-266` | decision → `hidden_effect { set_sub_doctrine = torpedo_primacy }` if `jeune_ecole`; `long_range_submarines` if `capital_hunters`; `ai_will_do 9999`, no cost field | `available = { is_ai = yes }` | **DERIVED** AI gets the subdoctrine without spending navy XP | Sheep | **B** — an AI resource cheat whose value is doctrine balance |
| D3 | Fake army spirits (context) | `S/common/ideas/LSM_JAP_fake_army_spirit.txt:1-85`; decisions:3-138 | AI-only army spirits; `LSM_JAP_fake_logistical_focus_spirit` includes `navy_fuel_consumption_factor -0.10` | AI JAP | Mostly land; one navy fuel line | Sheep | **B** |

### 2.8 Diplomacy side-levers touching naval play

| # | Mechanism | Where | Lever | Achieves | Owner | Class |
| --- | --- | --- | --- | --- | --- | --- |
| X1 | Docking / airbase access denial | S/JAP.txt:65-107 | reversed `diplo_action_desire id=JAP docking_rights -2000`, `air_base_access -2000`; `OTHERS_dont_give_JAP_dock_access`: every non-ally `diplo_action_acceptance id=JAP docking_rights -2000` | **ASSUMED** keeps JAP's fleet (and foreign fleets) from basing in neutral ports → fleets stay concentrated | Sheep | **A** |
| X2 | Opponent passivity in KR — GEA | `K/common/ai_strategy/GEA.txt:199-235` (live, not overridden) | GEA: `strike_force_home_base 72` (Natuna); `naval_avoid_region` 76/77/79/90 `+100` | when `JAP naval_strength_comparison { other = ROOT ratio > 0.6 }` | The main Reichspakt navy in Asia stays out of Japanese home seas → uncontested lanes for Japan | KR | **C** — opponent-side, tag/region-specific (and is part of "opponent weakness in KR's setup") |
| X3 | Opponent passivity — Chinese warlords | `K/common/ai_strategy/china.txt:970-983` | `naval_avoid_region 77` (Yellow Sea) `+1000` | Chinese tag at war with JAP | Chinese fleets never contest the Yellow Sea | KR | **C** |
| X4 | Dropped KR protection `JAP_no_naval_invasion_overseas` | K/…/JAP.txt:448-467 | reversed, non-Asian enemies `invade id=JAP -2000`, `invasion_unit_request tag=JAP -2000` during CUF war | **DERIVED** dead in the submod (file override) → non-Asian enemies may invade Japan during SSJW | KR only | **C** |
| X5 | Dropped KR invasion batching `JAP_sync_invasions_on_china` | K/…/JAP.txt:1051-1074 | `front_control area china ordertype invasion execute_order = no` on days 0-44 of every 90 | **DERIVED** dead in the submod; KR held invasions for 45 days to batch them | KR only | **A** (technique) |
| X6 | `JAP_support_RSA` | warplan:2838-2907 | `prepare_for_war GER/ENG/FRA +150`; `naval_invasion_focus -200`; `invasion_unit_request` European Reichspakt -25 | faction leader with RSA facing GER/INT | Siberian land war → navy off invasions | Sheep | **C** |

---

## 3. Engine-oracle notes (what each type means)

| Type | Documented? | Semantics used above |
| --- | --- | --- |
| `invade` | **MEASURED** `V/common/ai_strategy/_documentation.md:335-343`: negative avoids invasions against the country completely; positive = factor on invasion importance (60 → ×1.6) | `+1005` → ×11.05 (DERIVED) |
| `front_unit_request` / `invasion_unit_request` | **MEASURED** doc:315-333, targets tag/state/strategic_region/area/country_trigger/state_trigger, "value will be added as a factor over regular requests"; state_trigger scope = state, FROM = enemy, FROM.FROM = us | |
| `front_control` | **MEASURED** doc:276-313: `ratio`, `priority`, `ordertype front/invasion`, `execution_type careful/balanced/rush/rush_weak`, `execute_order` | |
| `put_unit_buffers` | **MEASURED** doc:346-389 | |
| `naval_dominance`, `convoy_raiding_target`, `naval_blockade`, `coast_defense` | **MEASURED** doc:672-720, value 0-100 % | not used by Sheep |
| `naval_invasion_dominance_weight` | **MEASURED** doc:391-398 | not used by Sheep or KR JAP |
| `naval_invasion_focus`, `naval_convoy_raid_region`, `naval_avoid_region`, `naval_mission_threshold`, `strike_force_home_base`, `naval_invasion_support_priority` | listed (doc:53-61) but **not explained**; `naval_invasion_support_priority` not even listed but used by vanilla `V/common/ai_strategy/ENG.txt:1179-1204` | effect **ASSUMED** from name and vanilla use |
| `reversed = yes` | not in vanilla doc; vanilla uses it (`V/common/ai_strategy/FRA.txt:328`) | **ASSUMED** |
| Naval goal scoring | **MEASURED** `V/common/ai_navy/_documentation.md`: score = min + (max-min) × importance | KR goals: invasion support 10-20, invasion defense 10-18, dominance 1-13, raiding 3-7, protection 1-5 (`K/…/goals_generic.txt`) |
| `role_ratio` magnitudes | doc (ALL BUT AIR): "base of 100 plus the value" (stated for unit ratios) | **ASSUMED** same for role_ratio |

Mission-assignment defines are **vanilla** in the KR stack (KR sets none): `MIN_NAVAL_MISSION_PRIO_TO_ASSIGN` patrol 200 / strike 200 / raid 200 / escort 100 / invasion support 100; `HIGH_PRIO_NAVAL_MISSION_SCORES` patrol 100000 / strike 1000 / raid 1500 / escort 1000 / invasion support 1000 (**MEASURED** `V/common/defines/00_defines.lua:3140-3164`). Sheep's *general* vanilla mod does change them (patrol 100/2000, escort 200/2000 — `G/common/defines/lsm_defines.lua:198-222`) but that mod is not in the KR stack.

---

## 4. Sheep's general vanilla mod (G/) — naval items, skim only

**MEASURED** `G/common/ai_strategy/JAP.txt` has the same idioms: `jap_early_invasions_are_risky_and_best_wait_for_later` (`invade CHI/HBC -9999` until 1938.2.1 or while land ground is being gained, :2-30), `JAP_once_we_lose_the_fleet_do_not_contest` (`naval_avoid_region` 90/76/79 +500, :533-568), home-island `put_unit_buffers` (:359-500), `naval_convoy_raid_region` 94/177/18 (:700-724). `G/common/ai_strategy/LSM_navy.txt:41-83` sets JAP carriers -15, screens +70, CL +30, CA -15, `unit_ratio capital_ship +10`. **DERIVED** the "invade only when the land war stalls" rule is the author's signature idiom in both mods.

---

## 5. Portability summary

| Class | Mechanisms |
| --- | --- |
| **A** (portable engine technique) | G1 stalemate flag, G2 no-invasion switch, G3 division release, G9 population/surrender filter, G11 human-threat home defence, E1-E6 (beachhead tag, rush, reinforcement, KR deprio define, both reset loops), R1/R2 km range fences (core), M1-M5 garrison release + reactive buffers + KR coastline define, P3, P7, P9, F1, F2, F4, F5, F6, F8-F10, D1 fake-spirit steering, X1, X5 |
| **B** (balance-dependent) | P1, P2, P4-P6 ship-count ladders, P8 sonar, P10 torpedo designs, P11 quality-shipbuilding edit, P12 naval focuses, D2 free subdoctrines, D3 |
| **C** (scenario-specific) | G4 China-first areas, G5 blacklist, G6 whitelist + ×11 tag multiplier, G7 invade-once, G8, G10 treaty ports, E7 port building by province ID, R3-R6 post-China/Oceania/all-hands, F3 Hawaii-gated raiders, F7 home-water raid regions, X2-X4 opponent passivity, X6 |

## 6. Ranked impact (top 10) — ranking is **ASSUMED** (engine weighting is not observable; order from how many invasion decisions each lever touches, DERIVED from the gating tables)

| Rank | Mechanism | Class |
| --- | --- | --- |
| 1 | G1+G2 stalemate-gated no-invasion switch (on_action flag + `invade -1000` + division floors 80/100) | A |
| 2 | G6+G7 whitelist → one decisive landing (`invade ×11.05`, +105 requests) then invade-once off | C |
| 3 | E1+E2+E3 beachhead flag → `front_control rush_weak priority 200` + reinforcement | A |
| 4 | R1+R2 km range fences (-2000 beyond 3000 km, -100 beyond 800 km of allied coast) | A |
| 5 | M1+M2+M3 garrison stripping (-1000 / -25 on naval ratio; KR `AREA_DEFENSE_SETTING_COASTLINES=false`) | A |
| 6 | E4 KR `MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS 20→100` | A |
| 7 | E5+E6 periodic invasion reset (-9999 for 2-3 days every 90/120 days when stalled) | A |
| 8 | P4-P6+P10 ship-count ladders + torpedo DD/CL/torpedo-cruiser designs (KR generic designs blocked) | B |
| 9 | X2+X3 KR opponent passivity (GEA avoids JAP seas at ratio > 0.6; Chinese avoid Yellow Sea +1000) | C |
| 10 | F1+F3+F6 task-force redesign (KidoButai min 1 CV, Hawaii-gated DeathSquad raiders, invasion-support fleet and supremacy lines deleted) | A |
