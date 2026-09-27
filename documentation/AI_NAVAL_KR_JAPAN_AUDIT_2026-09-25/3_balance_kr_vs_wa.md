# Naval BALANCE audit — Kaiserreich (+ Sheep's KR Japan AI) vs World Ablaze

Date: 2026-09-25. Read-only. Scope = balance (defines, stats, techs, modifiers, scenario), not AI scripting.

Paths used:
- VAN = `C:\Jeux\steamapps\common\Hearts of Iron IV` (install)
- KR = `C:\Jeux\steamapps\workshop\content\394360\1521695605`
- SHP = `C:\Jeux\steamapps\workshop\content\394360\3677914657` (Sheep's KR Japan AI)
- WA = `E:\Projets\HOI4\WA\world-ablaze-beta`

Tooling (scratchpad): `defcmp.py` (parses VAN 00_defines.lua tables + KR/WA `NDefines.X.Y =` overrides; output `diff_only.txt`, `rows.json`, vanilla comments `vcomments.txt`), `hulls.py`, `techcmp.py`, `dock.py`.

---

## 0. Verdict

- **MEASURED** KR's naval balance is almost pure vanilla. KR changes 4 naval-relevant defines, 0 ship-hull stats (except one tech year), 0 naval tech values, 0 naval doctrine values, 0 marine stats, 0 convoy stats.
- **MEASURED** WA changes ~110 naval-relevant defines and replaces the whole ship-equipment model (800 hull equipments vs 88 in vanilla).
- **DERIVED** So KR Japan's good naval results come from (a) vanilla naval balance, (b) the KR scenario, (c) Sheep's AI scripting — not from KR balance tuning. There is almost nothing in KR "balance" to copy.
- **DERIVED** The one KR define that plausibly helps ANY AI invader is `AREA_DEFENSE_SETTING_COASTLINES = false` (defenders stop garrisoning coastlines). It is global, AI-only, symmetric.
- **DERIVED** WA already gives its AI larger invasion help than KR does (`base_ai` −75 % prep, `hard_ai` −100 % invasion penalty). Invasion prep time is not where WA lags.

Side fact: **MEASURED** the install is `1.19.3.0` (`VAN\launcher-settings.json`, `"rawVersion": "1.19.3.0"`), not 1.19.2 as AGENTS.md says. KR `supported_version="1.19.3.*"` (KR descriptor.mod), SHP `1.19.3.0`.

---

## 1. What each mod touches (load-order facts)

| Fact | Label / source |
| --- | --- |
| KR has only 2 define files: `KR_defines.lua` (214 lines), `KR_embargo_defines.lua` (3 lines). | **MEASURED** `KR\common\defines\` |
| SHP defines file is fully commented out ("deactivated for the time being"). | **MEASURED** `SHP\common\defines\LSM_JAP_defines.lua:1-16` |
| KR does NOT `replace_path` `common/units`, `common/units/equipment`, `common/doctrines`, `common/terrain`. It overrides by filename: `ship_hull_{carrier,cruiser,heavy,light,submarine}.txt`, `infantry.txt`, sea subdoctrine files, `MTG_naval*.txt` (technologies is replace_path). | **MEASURED** `KR\descriptor.mod`; `KR\common\units\equipment\` listing |
| KR does NOT override `00_ship_modules.txt` or `convoys.txt` → vanilla ship modules and convoys are live. | **MEASURED** file listing `KR\common\units\equipment\modules\` (only `KR_tank_modules.txt`) |
| KR has no `sea_grand_doctrines.txt` → vanilla sea grand doctrines live. | **MEASURED** `KR\common\doctrines\grand_doctrines\` (only land) |
| WA `replace_path`s `common/units`, `common/units/equipment`, `common/doctrines/**`, `common/technologies`, `common/terrain`, `common/modifiers` is not replace_path but `00_static_modifiers.txt` is overridden. | **MEASURED** `WA\descriptor.mod:74-105` |

---

## 2. Define table — every naval-relevant key where KR or WA differs from vanilla

Line numbers: V = `VAN\common\defines\00_defines.lua`, K = `KR_defines.lua`, W = `WA\common\defines\05_defines.lua`. "—" = not set (vanilla value applies). All rows **MEASURED** for the values; the "effect" column is **DERIVED** from the vanilla comment on that key unless marked **ASSUMED**.

### 2a. Keys KR changes (the complete naval-relevant list)

| Key | Vanilla | KR | WA | Effect on AI naval play |
| --- | --- | --- | --- | --- |
| NAI.MAX_FULLY_TRAINED_SHIP_RATIO_FOR_TRAINING | 0.7 (V3268) | **0.99** (K188) | 0.8 (W1370) | AI keeps training until 99 % of ships are fully trained → more veteran fleets. Costs fuel/XP; WA already moved halfway. |
| NAI.REFIT_SHIP_PERCENTAGE_OF_FORCES | 0.1 (V2822) | 0.25 (K191) | **1.0** (W1345) | Share of navy considered for refit. WA is far more aggressive than KR. |
| NAI.MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS | 20 (V3327) | **100** (K175) | 60 (W1064) | Beachhead keeps priority until 100 provinces taken. Helps an island-hopper keep troops on invaded fronts. |
| NAI.XP_RATIO_REQUIRED_TO_RESEARCH_WITH_XP | 2.0 (V3008) | 1.6 (K105) | **1.0** (W1581) | KR comment: "needed to make AI research naval techs with XP". WA already lower. |
| NAI.RESEARCH_WITH_XP_AI_WEIGHT_MULT | 1.2 (V3009) | **4.0** (K106) | — (1.2) | AI prefers techs it can buy with (naval) XP ×4. Not set in WA. |
| NAI.NUM_SILOS_PER_DOCKYARDS | 0.02 (V3272) | 0 (K118) | — | Fuel silos not tied to dockyards. Negligible. |
| NCountry.MAX_CONVOYS_BEING_RAIDED_WAR_SUPPORT_IMPACT | −0.5 (V415) | −1 (K36) | −0.3 (W138) | War-support hit from raided convoys. Not AI naval behaviour. |
| NDiplomacy.PEACE_COST_FACTOR_CAPITAL/SCREENING_SHIP_IC | 0.005 (V62-63) | 0.02 (K84-85) | — | Peace-deal ship cost. Irrelevant to play. |
| NMilitary.EQUIPMENT_COMBAT_LOSS_FACTOR | 0.70 (V997) | **0.45** (K23) | **1.0** (W331) | Land equipment lost in combat. Beachheads in KR lose 36 % less equipment than vanilla, WA loses 43 % more than vanilla (DERIVED ratio). Global, affects players. |

Non-naval KR AI defines that bear on invasions (defender side):

| Key | Vanilla | KR | WA | Effect |
| --- | --- | --- | --- | --- |
| NAI.AREA_DEFENSE_SETTING_COASTLINES | true (V3454) | **false** (K183) | true (W1001) | KR AI defenders do not put area-defence on coastlines (only ports/VP/airbases). **ASSUMED**: makes landings against AI much easier (non-port beaches empty). |
| NAI.AREA_DEFENSE_SETTING_VP / AIRBASES | false/false | true/true (K178,180) | false/false (W997,999) | KR defenders spend garrisons on VPs & airbases instead. |
| NAI.MIN_FORCE_RATIO_TO_PROTECT | 0.5 (V2664) | 0 (K113) | — | "Tiny countries should not feel protective". **ASSUMED** minor. |
| NAI.FRONT_EVAL_PERCENT_TO_ASSIST_ALLY_FRONT | 0.5 (V3289) | 0 (K114) | — | AI never ships units to ally fronts. **ASSUMED**: fewer Allied reinforcements to Japan's targets. |
| NAI.ATTACK_HEAVILY_DEFENDED_LIMIT | 0.5 (V2871) | 1.1 (K173) | — | Land attack threshold. |

### 2b. Keys only WA changes — invasion planning / execution

| Key | Vanilla | WA | Effect |
| --- | --- | --- | --- |
| NNavy.BASE_NAVAL_INVASION_DIVISION_CAP | 4 (V1674) | **3** (W696) | −1 division per invasion. |
| NAI.MIN_INVASION_PLAN_VALUE_TO_EXECUTE | 0.3 (V3341) | **0.05** (W1379) | WA AI launches invasions at much weaker plan value. |
| NAI.ENEMY_NAVY_STRENGTH_DONT_BOTHER | 2.5 (V2844) | 5.0 (W1069) | WA AI still plans invasions vs a navy up to 5× stronger. |
| NAI.MAX_UNIT_RATIO_FOR_INVASIONS | 0.4 (V3316) | 0.35 (W1058) | Slightly fewer divisions allowed for invasions. |
| NAI.MAX/DESIRED/MIN_UNITS_FACTOR_INVASION_ORDER | 1.0/1.0/1.0 (V2886-2888) | 1.4/1.4/1.2 (W1066-1068) | Bigger invasion orders. |
| NAI.INVASION_COASTAL_PROVS_PER_ORDER | 24 (V2826) | 28 (W1061) | Fewer parallel invasion orders. |
| NAI.MAX_INVASION_FRONT_SCORE | 1000 (V3318) | 2400 (W1059) | Invasion fronts rank higher. |
| NAI.MIN_FRONT_SCORE_FOR_AFTER_INVASION_AREAS | 1500 (V3319) | 1800 (W1060) | Beachhead fronts rank higher. |
| NAI.NAVAL_INVADED_AREA_PRIO_DURATION / _MULT | 90 / 1.2 (V3325-3326) | 270 / 2.0 (W1062-1063) | Beachhead priority 3× longer, stronger. |
| NAI.MIN_INVASION_AREA_SIZE_FOR_FLOATING_HARBORS | 15 (V2827) | 5 (W1030) | AI uses floating harbours on small areas. |
| NSupply.FLOATING_HARBOR_BASE_SUPPLY / _DURATION | 15 / 21 d (V4302-4303) | **50 / 180 d** (W942-943) | Floating harbours 3.3× supply, 8.6× duration. Global. |
| NAI.MAX_SCREEN / CAPITAL_FORCES_FOR_INVASION_SUPPORT | 0 / 0 (V3194-3195) | 0.2 / 0.3 (W1138-1139) | WA AI assigns 20 % screens / 30 % capitals to invasion support; vanilla/KR assign none by ratio. |
| NNavy.BASE_SPOTTING_EFFECT_FOR_INITIAL_NAVAL_INVASION_SPOTTING | 2.4 (V2050) | **10.0** (W730) | Invasion convoys spotted ~4× faster → easier to intercept → invasions harder in WA. Global. |
| NNavy.SPOTTING_SPEED_EFFECT_FOR_INITIAL_NAVAL_INVASION_SPOTTING | 0.12 (V2051) | 0.5 (W731) | Same direction. |
| NNavy.NAVAL_TRANSFER_DAMAGE_REDUCTION | 0.25 (V1707) | 0.0625 (W870) | Factor on damage to transported units. **ASSUMED** lower = less damage (safer transports). |
| NNavy.NAVAL_TRANSFER_BASE_SPEED | 6 (V1677) | 27 (W891) | Troop convoys 4.5× faster. |
| NNavy.HEAVY/LIGHT_GUN_ATTACK_TO_SHORE_BOMBARDMENT | 0.05 / 0.025 (V2124-2125) | 0.025 / 0.0005 (W819-820) | Formula divides by this ×100 → **DERIVED** WA shore bombardment per gun is higher (2× heavy, 50× light) but capped by SHORE_BOMBARDMENT_CAP 0.30 vs 0.33. |
| NAir.AIR_INVASION_PREPARE_DAYS / PLAN_CAP / DIVISION_CAP | 7 / 1000 / 1000 | 30 / 1 / 1 (W533-535) | Paradrops nerfed. Not naval. |

### 2c. Keys only WA changes — naval combat lethality, positioning, spotting

| Key | Vanilla | WA | Effect |
| --- | --- | --- | --- |
| NNavy.COMBAT_DAMAGE_TO_STR_FACTOR | 0.6 (V1610) | **0.15** (W727) | Damage → strength 4× lower. **DERIVED**: naval battles far less decisive; a local-superiority fleet cannot wipe the enemy fleet quickly. Biggest single combat difference. Global. |
| NNavy.COMBAT_TORPEDO_CRITICAL_CHANCE / _DAMAGE_MULT | 0.1 / 2.0 (V1607-1608) | 0.9 / 6.0 (W723-724) | Torpedoes crit 90 % ×6. |
| NNavy.COMBAT_EVASION_TO_HIT_CHANCE_TORPEDO_MULT | 10.0 (V1602) | 1.0 (W722) | Evasion matters less vs torpedoes. |
| NNavy.AGGRESSION_SETTINGS_VALUES | {0,0.6,1.25,2.0,10000} (V1798) | {0,0.95,1.0,2.0,10000} (W839) | Engagement thresholds per aggression level. |
| NNavy.AGGRESSION_TORPEDO_EFFICIENCY_ON_HEAVY/LIGHT | 1.5 / 0.2 | 10.0 / 0.05 (W827-828) | Scoring for engage decisions. |
| NNavy.BASE_POSITIONING | 1.0 (V2063) | 0.75 (W798) | Lower base positioning. |
| NNavy.HIGHER_SHIP_RATIO_POSITIONING_PENALTY_FACTOR / MAX / MIN_SHIPS | 0.25 / 0.75 / 4 | 1.0 / 3.0 / 61 (W803,804,674) | Large-fleet penalty only above 61 ships but 4× harsher. |
| NNavy.DAMAGE_PENALTY_ON_MINIMUM_POSITIONING | 0.5 (V2084) | 0.9 (W813) | Bad positioning is near-fatal. |
| NNavy.MIN_HIT_PROFILE_MULT / HIT_PROFILE_SPEED_FACTOR | 0.0 / 0.5 | 0.25 / 1.2 (W720,725) | Hit-chance model changed. |
| NNavy.NAVY_PIERCING_THRESHOLDS / _CRITICAL_VALUES | see V2265/V2274 | changed (W767,776) | Armor model changed. |
| NNavy.BASE_ESCAPE_SPEED / SPEED_TO_ESCAPE_SPEED | 0.05 / 0.5 | 1.0 / 1.3 (W875,874) | **DERIVED**: ships escape combat 20× faster base → fewer sinkings. |
| NNavy.ESCAPE_SPEED_SUB_BASE / HIDDEN_SUB | 0.1 / 0.35 | 0.4 / 1.0 (W872-873) | Subs escape fast. |
| NNavy.NAVAL_SPEED_MODIFIER | 0.1 (V1670) | **0.032** (W890) | "basic speed control": fleets move ~⅓ speed. **ASSUMED**: slower fleet redeploy, slower dominance response. |
| NNavy.BASE_SPOTTING_FROM_AIR / RADAR / DECRYPTION | 20 / 5 / 10 | 5 / 10 / 20 (W787,786,790) | Air spotting nerfed. |
| NNavy.DETECTION_CHANCE_MULT_BASE / RADAR_BONUS | 0.1 / 0.1 | 0.05 / 0.2 (W735-736) | Harder base detection. |
| NNavy.SUB_DETECTION_CHANCE_BASE | 5 (V2028) | 1 (W681) | Subs harder to find. |
| NNavy.MIN_REPAIR_FOR_JOINING_COMBATS | {0,0.5,0.7,0.9,0} | {0,0.5,0.7,0.8,0} (W746) | |
| NNavy.REPAIR_AND_RETURN_PRIO_* (6 keys) | 0.45/0.65/0.90, combat 0.9/0.6/0.4 | 0.2/0.5/0.8, combat 0.2/0.3/0.6 (W706-712) | Repair thresholds reshaped. |
| NBuildings.NAVALBASE_REPAIR_MULT | 0.05 (V745) | 0.1 (W162) | Ports repair 2×. |
| NNavy.OUT_OF_FUEL_ATTACK/RANGE/TORPEDO_FACTOR | −0.5 / 0 / −0.8 | −0.9 / −0.75 / −0.9 (W880-882) | Out of fuel is much harsher in WA. |
| NNavy.MISSION_FUEL_COSTS | {0,1,1,1,1,1,1,0.6,0,1} | {0.5,0.8,1,0.6,0.6,1,1,0.4,0,1} (W901) | HOLD costs fuel; patrol/raid/escort cheaper. |
| NNavy.SUPPLY_NEED_FACTOR | 1 (V1696) | 0.75 (W899) | |
| NNavy.MISSION_DOMINANCE_RATIOS | TRAIN = 0.0 | TRAIN = 1.0 (W847) | Training fleets build dominance in WA. |
| NNavy.NAVAL_DOMINANCE_STRIKE_FORCE_FRACTION / MULTIREGION_DECAY | 0.0006 / 0.05 | 0.0004 / 0.10 (W669-670) | Strike force dominance buff weaker. |
| NNavy.DOMINANCE_PER_SHIP_PER_CARRIER_SIZE / HEAVY_GUN / RANGE_NEUTRAL | 0.1 / 0.01 / 2000 | 0.05 / 0.008 / 3500 (W860-863) | Dominance per ship lower. |
| NAir.NAVAL_STRIKE_DAMAGE_TO_ORG / CARRIER_MULTIPLIER / PORT_STRIKE_DAMAGE_FACTOR | 1.5 / 12 / 1.0 | 0.5 / 10 / 0.1 (W646-659) | Air power vs ships nerfed. |
| NAir.CARRIER_HOURS_DELAY_AFTER_EACH_COMBAT / DISRUPTION_FACTOR_CARRIER | 3 / 6.0 | 0 / 2.0 (W575-576) | |
| NNavy training/XP (TRAINING_*, UNIT_EXPERIENCE_PER_COMBAT_HOUR, EXPERIENCE_FACTOR_*) | see diff_only.txt | several | Country naval XP from training 3-7× lower in WA (TRAINING_MAX_DAILY_COUNTRY_EXP 1 → 0.15, W895). |

### 2d. Keys only WA changes — convoys, supply, ports

| Key | Vanilla | WA | Effect |
| --- | --- | --- | --- |
| NSupply.NAVAL_BASE_FLOW / NAVAL_FLOW_PER_LEVEL | 5 / 3 (V4338-4339) | 0 / 5 (W937-938) | **DERIVED** port supply throughput: level 1 = 8 (van/KR) vs 5 (WA); level 2 = 11 vs 10; level 5 = 20 vs 25. Small captured island ports supply less in WA. |
| NCountry.SUPPLY_CONVOY_FACTOR | 0.25 (V331) | 0.3 (W82) | +20 % convoys per supply. |
| NCountry.CONVOY_RANGE_FACTOR | 1 (V332) | 1.1 (W83) | |
| NNavy.CONVOY_EFFICIENCY_LOSS_MODIFIER / REGAIN_AFTER_DAYS | 1.25 / 7 | 1.1 / 1 (W865-866) | Convoy efficiency recovers much faster. |
| NNavy.SCREEN_RATIO_FOR_FULL_SCREENING_FOR_CONVOYS / CAPITAL_RATIO | 0.5 / 0.25 | 3.0 / 1.0 (W885,887) | Convoy screening needs 6× more escorts. |
| NAI.CONVOY_DANGER_FOR_MAX_IMPORTANCE / REGION_THREAT_PER_SUNK_CONVOY / DECAY | 400 / 25 / 2 | 50 / 300 / 4 (W1127-1129) | AI reacts far harder to sunk convoys. |
| NAI.MISSING_CONVOYS_BOOST_FACTOR | 50 (V2847) | 0 (W1076) | WA AI does not boost convoy production when short. |

### 2e. Keys only WA changes — taskforce / mission shaping (engine AI parameters)

| Key | Vanilla | WA |
| --- | --- | --- |
| CARRIER_TASKFORCE_MAX_CARRIER_COUNT | 4 (V3108) | 10 (W1141) |
| MIN_CAPITALS_FOR_CARRIER_TASKFORCE | 6 (V3113) | 10 (W1147) |
| CAPITALS_TO_CARRIER_RATIO | 1.5 (V3114) | 1.0 (W1148) |
| CAPITAL_TASKFORCE_MAX_CAPITAL_COUNT | 12 (V3109) | 10 (W1142) |
| SCREEN_TASKFORCE_MAX_SHIP_COUNT | 12 (V3110) | 5 (W1143) |
| SUB_TASKFORCE_MAX_SHIP_COUNT | 16 (V3111) | 5 (W1221) |
| SCREENS_TO_CAPITAL_RATIO | 4.0 (V3115) | 3.0 (W1144) |
| MAX_CARRIER_OVERFILL | 1.85 (V3067) | 1.0 (W1146) |
| MAX_MISSION_PER_TASKFORCE | {0,1,4,1.5,4,2,2,0,0,10} | {0,1.5,6,1.5,4,2,2,0,0,10} (W1179) |
| MAX_PATROL_TO_STRIKE_FORCE_RATIO | 4.0 (V3196) | 10 (W1199) |
| AI_TASKFORCE_REQUIRED_RESERVE_RATIO | 0.2 (V2338) | 0.05 (W1078) |
| NAVAL_IMPORTANCE_SCALE | 0.65 (V2920) | 10.0 (W1243) |
| NAVAL_COMBAT_AIR_IMPORTANCE / TRANSFER_AIR_IMPORTANCE | 8 / 50 | 500 / 500 (W1240,1293) |
| NAVAL_STRIKE_PLANES_PER_SHIP / PER_ARMY / MIN_EXCORT | 20 / 0 / 0 | 40 / 20 / 100 (W1242-1247) |

(These are AI knobs, listed for completeness; KR leaves them all vanilla. Full raw list: `diff_only.txt`.)

---

## 3. Stats, techs and modifiers that make invasions easier / harder

### 3a. Ship stats

| Claim | Label / source |
| --- | --- |
| KR hull stats = vanilla. Only diff: `ship_hull_super_heavy_1` year 1940 → 1924. KR removes 39 pre-MTG legacy equipments and adds `ship_hull_armoured_cruiser`. | **MEASURED** `hulls.py` over `ship_hull_*.txt` VAN vs KR |
| KR ship modules = vanilla (`00_ship_modules.txt` not overridden). | **MEASURED** file listing |
| WA has 800 hull equipments across 8 hull files (incl. `ship_hull_very_light`, `ship_hull_heavy_cruiser`, `ship_hull_cruiser_submarine`) + 9 national ship-module files. Vanilla has 88. | **MEASURED** `hulls.py` over `WA\common\units\equipment\` |
| WA archetype speeds lower: light 25 kn (van 32), cruiser 20 kn (van 27). Carrier archetype 2450 IC (van 2094), fuel 87 (van 70). | **MEASURED** archetype blocks in WA `ship_hull_light.txt`, `ship_hull_cruiser.txt`, `ship_hull_carrier.txt` |
| Convoy: WA `build_cost_ic = 700` vs vanilla/KR 70; WA max_strength 20 (van 60), org 60 (30), visibility 20 (14), AA 2.5 (0.1). | **MEASURED** `WA\common\units\equipment\convoys.txt:41`, `VAN\...\convoys.txt:40` |
| WA convoy 10× relative cost vs warships (warship archetype costs ≈ vanilla). | **DERIVED** from the two rows above. WA's factory output model is rewritten (`POWERED_FACTORY_SPEED_NAV = 4.2`, base 0, W193-194), so absolute build time is not comparable — do not estimate it. |

### 3b. Invasion capacity from techs (DERIVED sums of MEASURED modifiers)

| | Vanilla / KR (MTG) | WA |
| --- | --- | --- |
| Base division cap | 4 (V1674) | 3 (W696) |
| Tech 1 | `mtg_transport`: −10 prep days, +2 div, +1 plan (KR MTG_naval_Support.txt:1667-1670) | `mtg_transport`: +2 div, +1 plan, transport_capacity −0.5 (WA electronic_mechanical_engineering.txt:6697-6701); **gated** on having >14 ships incl. a cruiser/capital/carrier (`allow`, :6716-6743) |
| Tech 2 | `mtg_landing_craft`: −10 d, +4 div, +3 plan, +15 % amph. def. (KR :1724-1728) | `mtg_landing_craft`: invasion_preparation −0.5, +2 div, +2 plan (WA :6809-6814) |
| Tech 3 | `mtg_tank_landing_craft` (1944): −10 d, +5 div, +4 plan, +25 % amph. (KR :1780-1785) | `mtg_amphibious_assault_ships` (1942): +1 div, +1 plan, +25 % amph. (WA :7184-7189) |
| Tech 4 | — | `mtg_large_landing_craft`: +1 div, +1 plan (WA :7260-7263) |
| **Max div per invasion** | **15** | **9** |
| **Max concurrent plans** | **9** | **6** |
| **Prep days** | 60 −30 = **30 d** | 60 d base, only % reductions |
| JAP 1936 start | `mtg_transport` → 6 div, 2 plans, 50 d (KR history JAP - Japan.txt:66) | `mtg_transport` + `mtg_landing_craft` → 7 div, 4 plans (WA history JAP - Japan.txt:388-389) |

- **MEASURED** vanilla lines `#invasion_preparation = -0.25` and `#naval_invasion_capacity` are commented out in vanilla too (VAN MTG_naval_Support.txt ~2117, 2122, 2186) — KR equals vanilla here.
- **MEASURED** KR naval techs: every value in `MTG_naval.txt` and `MTG_naval_Support.txt` equals vanilla; KR removes 5 techs (`cruiser_submarines`, `midget_submarines`, `panzerschiffe`, `ship_hull_super_heavy`, `torpedo_cruiser_mtg`). Source: `techcmp.py`.
- **MEASURED** KR sea subdoctrines: every numeric modifier equals vanilla; KR only removed the vanilla tag-weighted `ai_will_do` blocks (flattened to `base = 1`). Source: numeric diff of `navy_*_doctrines.txt`.
- **MEASURED** Marines: KR `marine` = vanilla (org 70, amphibious attack +0.5, KR infantry.txt:128-170). WA `marine_horse_battalion_line` amphibious attack +0.25 (WA land_special_forces.txt:78-79).
- **ASSUMED** how `invasion_preparation` combines with the 60-day base (multiplicative, clamped) — the engine doc lists only the name (`VAN\documentation\modifiers_documentation.md:2982`).

### 3c. Japan-specific KR invasion boosts (player AND AI)

| Idea | Modifier | Granted by | Label |
| --- | --- | --- | --- |
| `JAP_south_seas_invasion_preparations` | +5 div cap, +2 plan cap, −10 % prep, +5 % amph., +2 % SF cap | focus `JAP_claim_colonies` (KR JAP focus (Japan base).txt:6603) | **MEASURED** KR JAP ideas (Japan).txt:2944-2954 |
| `JAP_overlord_military_excercise_idea` | +7 div cap, +2 plan cap, −20 % prep, −10 % invasion penalty | event `japan_foreign_events.550` (KR JAP events (Japan).txt:7543) | **MEASURED** KR JAP ideas (Japan).txt:2916-2926 |

**DERIVED** KR Japan can reach 15 + 5 (+7) = 20-27 divisions per invasion. WA Japan tops at 9 from techs.

### 3d. WA's own AI invasion helpers (already exist)

| Idea | Modifier | Gate | Label |
| --- | --- | --- | --- |
| `base_ai` | invasion_preparation −0.75, experience_loss −0.3, dig_in +0.5 … | `is_ai = yes`, every AI | **MEASURED** WA common/ideas/_WA_ai.txt:277-297 |
| `hard_ai` | **naval_invasion_penalty −1.0**, positioning +0.25, screening +0.25, navy AA +0.25, spotting +0.33, naval_coordination +0.5 … | `WA_AI_DIFFICULTY_has_cheats_enabled` + `is_ai` + major or listed tags | **MEASURED** _WA_ai.txt:234-274 |
| `JAP_tora_tora_tora_ai` | amphibious_invasion +5.0, invasion_preparation −0.49, convoy_retreat_speed +5 (240 d) | decision after `JAP_strike_south`, `is_ai = yes` | **MEASURED** WA ideas/japan.txt:3797-3810; decisions/JAP.txt:7374 |
| `JAP_navy_slighted` | invasion_preparation **+99.9** (90 d AI / 120 d player) | event `jap_armor.811` | **MEASURED** japan.txt:711 (block starts ~L708); events/wa_jap_events.txt:1758-1761 |
| `JAP_strategic_indecision` | invasion_preparation +1.0, max_planning −1.0 (720 d) | event after 1939.1.1 | **MEASURED** japan.txt:402; wa_jap_events.txt:3770,3813 |
| `diff_hard_ai` / `diff_very_hard_ai` | convoy_raiding_efficiency −0.48 / −0.72; NO navy fuel bonus | engine difficulty | **MEASURED** WA 00_static_modifiers.txt:543-556 |
| KR `diff_hard_ai` / `diff_very_hard_ai` | navy_fuel_consumption −0.25 / −0.5 (vanilla values) | engine difficulty | **MEASURED** KR 00_static_modifiers.txt:320-331 |
| WA `weather_rain_heavy` | amphibious_invasion −0.9 (not in vanilla/KR) | weather | **MEASURED** WA 00_static_modifiers.txt:30 |

**DERIVED** WA AI prep reduction (−0.75 all AI, −0.5 tech) already exceeds KR's (−30 days, no AI cheat). WA's `hard_ai` removes the amphibious penalty entirely; KR has nothing comparable.

---

## 4. Sheep's KR Japan AI — "fake" spirits and AI-only modifiers

| Item | Exact content | Gate | Label |
| --- | --- | --- | --- |
| `LSM_JAP_fleet_interoperability_navy_spirit` (navy_spirit) | naval_morale_factor +0.20; research naval_equipment +5 % | `allowed has_dlc_ncns`, `visible tag = JAP is_ai = yes`, ai_will_do 5000 | **MEASURED** SHP common/ideas/LSM_JAP_fake_navy_spirit.txt:3-17 |
| `LSM_JAP_efficient_communications_spirit` (naval_command_spirit) | positioning +0.15 | `available` new_fleet_in_being OR line_of_battle; `visible JAP AI`; ai_will_do 5000 | **MEASURED** same file :21-40 |
| `LSM_JAP_fake_professional_officer_corps_spirit` | army unit XP +15 %, max CP +30 | JAP AI | **MEASURED** LSM_JAP_fake_army_spirit.txt:3-11 |
| `LSM_JAP_fake_relief_of_command_spirit` | army XP +25 %, advisor cost −50 % | JAP AI, syndicalist/radsoc/elected | **MEASURED** :15-30 |
| `LSM_JAP_fake_mass_assault_army_spirit` | inf. combat XP +10 %, design cost −100 % inf/militia/mot/mech/bicycle | JAP AI, mass_assault | **MEASURED** :31-53 |
| `LSM_JAP_fake_logistical_focus_spirit` | planned-attack weight +1, supply −10 %, air & navy fuel −10 % | JAP AI, grand_battleplan | **MEASURED** :57-70 |
| `LSM_JAP_fake_operational_reserve_spirit` | relentless weight +1, army strength +10 % | JAP AI, mass_assault | **MEASURED** :72-83 |

- **MEASURED** Every "fake" spirit has the SAME modifiers as the real vanilla/KR spirit of the same name (compare VAN common/ideas/navy_spirits.txt:438-443, 543-550; KR common/ideas/01 Navy Spirits.txt:294-299, 386-393; army spirits likewise). The only difference: `visible` restricted to JAP AI and ai_will_do 5000. **DERIVED**: they are forced picks, not stat cheats.
- **MEASURED** Two free grants via hidden decisions: `LSM_JAP_buy_relief_of_command` adds the relief spirit with no XP cost (SHP common/decisions/LSM_JAP_decisions.txt:3-34); `LSM_JAP_buy_ma_spirit` adds the mass-assault spirit with no cost (:106-138). `LSM_JAP_buy_air_spirit` pays 50 air XP + 25 PP (:35-66). **DERIVED**: the army spirits bypass the XP price — a real AI-only economy cheat, but army-side.
- **MEASURED** Naval AI-only decisions just force sub-doctrines: `set_sub_doctrine = torpedo_primacy` if jeune_ecole, `long_range_submarines` if capital_hunters (LSM_JAP_decisions.txt:213-260). No stats.
- **MEASURED** `LSM_JAP_equipment.*` events only create Japanese land equipment variants with MIO design teams (SHP events/LSM_JAP_equipment.txt:1-137). No naval content.
- **MEASURED** `on_startup` instantly builds 1 air base (state 527) and 4 fuel silos (states 524, 1099, 527) — for everyone, not AI-gated (SHP on_actions_LSM_Japan.txt:16-47).
- **MEASURED** SHP overrides KR's `JAP ideas (Japan).txt`. Naval diffs in the live copy: `JAP_quality_shipbuilding_1/_2` destroyer bonus = torpedo +10 %, surface visibility −10 %, speed +10 % (KR current: light attack +10 %, sub attack +10 %); cruiser gets speed +10 % instead of sub attack (SHP file :1843-1921 vs KR). `JAP_rising_sun_idea_4` loses naval_equipment research +10 % and naval_doctrine_cost −10 %. **ASSUMED** version drift (SHP based on an older KR copy), not a deliberate AI change. Applies to players too.
- **MEASURED** SHP also ships JAP `ai_navy` fleet/taskforce templates (e.g. `JAP_KidoButai_1` optimal 4 CV + 4 BC + 4 BB + 8 CA + 35 CL + 25 DD, `naval_strike`) and warplan `ai_strategy` with `invasion_unit_request` / `naval_invasion_focus` (SHP common/ai_navy/taskforce/JAP_taskforce_templates.txt; common/ai_strategy/LSM_JAP_warplan.txt:118-1000). This is AI scripting — out of balance scope, but it is **DERIVED** the main thing SHP adds.

---

## 5. Scenario differences affecting Japan's naval war

| Claim | Label / source |
| --- | --- |
| KR JAP 1936 fleet: 6 BB, 3 BC, 3 CV, 12 CA, 17 CL, 106 DD, 53 SS. WA JAP: 6 BB, 3 BC, 3 CV + 2 CVL, 19 CA, 19 CL, 109 DD, 12 frigates, 8 cruiser-subs, 48 SS. Japan's own fleet is about equal. | **MEASURED** `definition =` counts, KR history/units/JAP_naval.txt; WA history/units/JAP_1936_naval.txt |
| Pacific rivals' fleets, KR: USA 17 BB 4 BC 3 CV; GEA (German East Asia) 6 BB 7 BC 3 CV; CAN 6 BB 3 BC 1 CV; AST 2 BC 1 CV; ENG 6 BB 2 BC 3 CV. WA: USA 16 BB 3 CV; ENG 12 BB 3 BC 4 CV + 1 CVL; FRA 5 BB 1 CV; HOL 3 CA 3 CL. | **MEASURED** same method, KR/WA history/units |
| Starting dockyards (undated state history only): KR JAP 15, USA 32, ENG 19, GER 12, FRA 9, GEA 0, AST 2, NFA 2. WA JAP 21, USA 42, ENG 50, FRA 22, HOL 7, AST 2. | **DERIVED** `dock.py` sum over history/states owner blocks (dated blocks ignored; KR CAN reads 0, likely a parser gap) |
| KR JAP's dockyard share vs its biggest Pacific rival: 15 vs 32 (USA), and GEA/AST/CAN can barely rebuild. WA: 21 vs 42 (USA) + 50 (ENG). | **DERIVED** from the row above |
| KR splits the USA fleet in the American Civil War: `USA_civil_war_begins` and `ACW_navy_redistribution_{WCA,APG,USA}` hand ships to breakaway tags. | **MEASURED** KR common/scripted_effects/01_American Civil War effects.txt:717, 1863-2126 (e.g. `transfer_ship` lines 566-586) |
| The ACW fires in most KR games, taking the USA out of the Pacific for years. | **ASSUMED** (KR default path; not verified in a save) |
| KR ENG is the Union of Britain (syndicalist, Atlantic-focused); the British Empire's Pacific assets sit with Canada/Australasia. | **ASSUMED**, supported by KR filenames `ENG ideas (Union of Britain).txt`, `CAN ACW` game rules |
| KR Japan's natural targets (GEA, Qing/China, Indochina, Pacific islands) have weak or non-rebuildable navies. | **ASSUMED** from the OOB/dockyard rows; not verified in a save |
| WA Japan faces the historical USA + UK + Netherlands with 92 dockyards combined vs 21. | **DERIVED** from dockyard sums |

**DERIVED**: the scenario gap (weak, split, non-rebuilding opponents in KR vs the historical USN+RN in WA) is large enough by itself to explain much of KR Japan's "good naval AI".

---

## 6. Copy-to-WA classification

"Global" = define/stat changes everyone (players too). "AI-only" = engine AI parameter or `is_ai` gate.

| Difference | Copy to WA improves WA AI naval play? | Changes player balance? |
| --- | --- | --- |
| KR `AREA_DEFENSE_SETTING_COASTLINES = false` | **Partial** — makes every AI attacker's landings easier (Japan's and the Allies' alike), but also strips AI coastal defence, including Japan's own islands vs USA and Axis coasts vs D-Day. Symmetric; a design choice, not a fix. | No (AI area-defence setting). **ASSUMED** player orders unaffected. |
| KR `MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS = 100` | **Partial** — WA already raised it to 60; going to 100 keeps beachheads prioritised longer (good for island chains). Low risk. | No (AI-only). |
| KR `MAX_FULLY_TRAINED_SHIP_RATIO_FOR_TRAINING = 0.99` | **Partial** — more veteran ships; WA's naval XP/training economy is heavily reduced (TRAINING_* keys) and fuel-harsh, so benefit is smaller and fuel cost real. | No (AI-only). |
| KR `RESEARCH_WITH_XP_AI_WEIGHT_MULT = 4.0` | **Partial** — pushes XP-buyable (naval) techs; affects all XP research, all branches. WA already has `XP_RATIO_REQUIRED = 1.0`. | No (AI-only). |
| KR `REFIT_SHIP_PERCENTAGE_OF_FORCES = 0.25` | **No** — WA already at 1.0. | No. |
| KR `EQUIPMENT_COMBAT_LOSS_FACTOR = 0.45` | **No** as a naval lever; land-wide rebalance. | **Yes** (global). |
| KR ship hulls/modules/techs/doctrines/marines | **No** — they ARE vanilla; WA replaced this layer on purpose. Reverting to vanilla is out of scope. | Yes (global). |
| Vanilla invasion tech capacity (15 div / 9 plans / −30 d) vs WA (9 / 6 / 0 d) | **Partial** — capacity is a real WA ceiling on large invasions. Raising WA's `naval_invasion_division_cap` in techs or base 3 → 4 lets AI ship bigger forces. WA's AI prep time is already short (base_ai −75 %). | **Yes** (techs/define are global). An AI-only route exists: add `naval_invasion_division_cap` to `base_ai`/`hard_ai` in _WA_ai.txt. |
| KR JAP-only ideas (+5/+7 div cap) | **Partial** — WA Japan has no equivalent capacity idea; its `JAP_tora_tora_tora_ai` gives amphibious +500 % but no division cap. | Yes if in a focus/event for everyone; No if added to the AI-only `JAP_tora_tora_tora_ai`. Per AGENTS.md principle 2, a tag-specific AI boost is a Country-layer design decision. |
| Sheep's fake spirits | **No** — same modifiers as real spirits; WA has its own spirit tree (`WA\common\ideas\_spirits_navy.txt`). The free-grant decisions are an army-side economy cheat. | No (AI-only). |
| Sheep's naval sub-doctrine forcing | **No** for balance; it is AI steering. | No. |
| KR/vanilla `COMBAT_DAMAGE_TO_STR_FACTOR = 0.6` (WA 0.15) | **ASSUMED yes** for decisiveness: vanilla battles let the stronger fleet destroy the weaker and gain supremacy; WA's 4× lower lethality plus 20× faster escape keeps inferior fleets alive to contest invasions. | **Yes** (global core combat) — needs a player-balance decision. |
| KR/vanilla invasion spotting 2.4 / 0.12 (WA 10 / 0.5) | **ASSUMED yes** — WA invasion convoys are spotted ~4× faster, so AI invasions get intercepted more. | **Yes** (global). |
| KR/vanilla `NAVAL_SPEED_MODIFIER 0.1` (WA 0.032) | **ASSUMED partial** — faster fleets respond to invasion regions quicker; interacts with every WA naval tuning. | **Yes** (global). |
| KR/vanilla `diff_hard_ai` navy fuel −25/−50 % (WA: convoy raid −48/−72 % instead) | **Partial** — WA's harsh out-of-fuel factors (−0.9) make fuel a bigger limiter than in KR; an AI fuel rebate would help fleets stay at sea. | No (AI difficulty modifier). |
| KR scenario (ACW, weak Pacific rivals) | **No** — not transferable; WA is historical. | n/a |

---

## 7. What this audit did NOT check

- **ASSUMED / unchecked**: starting naval doctrines and naval techs beyond the invasion line; fuel stockpiles; WA's national ship modules vs vanilla module stats; KR `difficulty_settings`; engine semantics of `naval_invasion_capacity` (doc gives only the name, `modifiers_documentation.md:3843`).
- No savegame was read. Every "effect on AI" statement is a reading of the vanilla define comment or an arithmetic consequence, not an observed campaign behaviour.
