# AI Railway System - Test Cases Document

## Purpose

This document contains all test cases for validating the AI railway building system. Each test case includes:
- **Scenario**: The game situation to evaluate
- **Setup**: Required conditions for the test
- **Expected Behavior**: What the system should do
- **Code Locations**: Where to verify the logic
- **Validation Method**: How to confirm pass/fail

Use this document to evaluate whether the current codebase correctly handles each scenario.

---

## Test Case Categories

1. [Basic Functionality Tests](#1-basic-functionality-tests) (TC-001 to TC-005)
2. [Border Detection Tests](#2-border-detection-tests) (TC-010 to TC-015)
3. [Overseas War Tests](#3-overseas-war-tests) (TC-020 to TC-028)
4. [Pre-War Preparation Tests](#4-pre-war-preparation-tests) (TC-030 to TC-036)
5. [Pathfinding Tests](#5-pathfinding-tests) (TC-040 to TC-046)
6. [Edge Case Tests](#6-edge-case-tests) (TC-050 to TC-062)

---

## 1. Basic Functionality Tests

### TC-001: Germany builds railways to SOV frontline

**Scenario:** Germany at war with Soviet Union, direct land border exists.

**Setup:**
- Country: Germany (GER)
- Enemy: Soviet Union (SOV)
- War status: Active war
- Border: Germany directly borders SOV-controlled territory
- Civilian factories: 50+

**Expected Behavior:**
- System triggers `WA_AI_PC_railway_STRATEGY_land_war`
- Finds frontline states with supply hubs bordering SOV
- Queues level 5 railways from Berlin (capital) to each frontline supply hub
- Prioritizes central hub with 1.1x multiplier

**Code Locations:**
- Strategy trigger: `WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt` lines 386-456
- Border check: `WA_AI_PC_railway_country_borders_enemy` (defined in same file, lines 343-376)

**Validation Method:**
1. Check `borders_enemy_` = 1 after border check
2. Verify `railway_end_provinces_` array contains frontline supply hub provinces
3. Verify `railway_target_levels_` = 5
4. Verify pathfinding succeeds (`pathfind_prov_success_` = 1)

**Expected Result:** PASS - Railways should be queued to SOV frontline

---

### TC-002: Italy should NOT build railways to SOV frontline

**Scenario:** Italy at war with Soviet Union, but NO direct land border (Germany is between).

**Setup:**
- Country: Italy (ITA)
- Enemy: Soviet Union (SOV)
- War status: Active war (same faction as Germany)
- Border: Italy does NOT directly border SOV (Germany/Hungary in between)
- Italy has NO puppets bordering SOV

**Expected Behavior:**
- `WA_AI_PC_railway_country_borders_enemy` returns `borders_enemy_` = 0
- Land war strategy skips SOV as a target
- NO railways queued to SOV frontline
- Italy may still build railways to enemies it DOES border (e.g., France, Yugoslavia)

**Code Locations:**
- Border check: `WA_AI_PC_railway_country_borders_enemy` lines 343-376
- Skip condition: lines 406-407 `if = { limit = { check_variable = { borders_enemy_ = 1 } } }`

**Validation Method:**
1. Check `borders_enemy_` = 0 after checking SOV
2. Verify SOV frontline provinces are NOT in `railway_end_provinces_` array
3. Verify Italy only queues railways to enemies it directly borders

**Expected Result:** PASS - NO railways to SOV frontline

---

### TC-003: England builds railways to port and European beachhead

**Scenario:** England at war with Germany, overseas war requiring naval invasion.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Germany (GER)
- War status: Active war
- Border: NO direct land border with Germany
- ENG controls beachhead in France/Belgium (e.g., Normandy)
- Beachhead has path to German frontline

**Expected Behavior:**
- System triggers `WA_AI_PC_railway_STRATEGY_overseas_war`
- Part A: Finds best port within 5 states of London, queues railway London → port
- Part B: Finds largest port on Europe continent controlled by ENG
- Validates beachhead is within 15 states of Berlin
- Validates pathfinding from beachhead to frontline succeeds
- Queues railways from beachhead to frontline supply hubs

**Code Locations:**
- Strategy: `WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt` lines 464-758
- Home port: lines 472-523
- Beachhead selection: lines 583-619
- Beachhead validation: lines 621-699
- Frontline railways: lines 701-753

**Validation Method:**
1. Verify home port railway queued (if port ≠ capital)
2. Verify `best_beachhead_state` > 0 and on Europe continent
3. Verify beachhead within 15 states of enemy capital
4. Verify `beachhead_valid_` = 1 (pathfinding succeeded)
5. Verify railways queued from beachhead province to frontline

**Expected Result:** PASS - Railways to port AND from beachhead to frontline

---

### TC-004: England should NOT build from Hong Kong against occupied China

**Scenario:** England at war with Japan, Hong Kong is isolated enclave surrounded by enemy.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Japan (JAP) controlling China
- War status: Active war
- ENG controls Hong Kong (Asia continent)
- Hong Kong is surrounded by Japanese-controlled territory
- NO path exists from Hong Kong to any frontline

**Expected Behavior:**
- System identifies Hong Kong as potential beachhead (largest port on Asia?)
- Beachhead validation: Tests pathfinding from Hong Kong to frontline
- Pathfinding FAILS (no friendly provinces connecting to frontline)
- `beachhead_valid_` = 0
- Hong Kong rejected as beachhead
- NO railways queued from Hong Kong

**Code Locations:**
- Beachhead validation: lines 640-699
- Pathfinding test: lines 679-688
- Rejection: lines 694-698

**Validation Method:**
1. Check `best_beachhead_province` initially set to Hong Kong port
2. Verify pathfinding fails (`pathfind_prov_success_` = 0)
3. Verify `beachhead_valid_` = 0
4. Verify `best_beachhead_state` reset to 0
5. Verify NO railways queued from Hong Kong

**Expected Result:** PASS - NO railways from Hong Kong

---

### TC-005: Romania builds to SOV frontline, NOT to France

**Scenario:** Romania at war with both SOV and France (via faction).

**Setup:**
- Country: Romania (ROM)
- Enemies: Soviet Union (SOV), France (FRA)
- War status: Active war with both
- Border: Romania directly borders SOV
- Border: Romania does NOT border France
- Civilian factories: 30+ (war threshold)

**Expected Behavior:**
- Border check for SOV: `borders_enemy_` = 1
- Border check for France: `borders_enemy_` = 0
- Railways queued to SOV frontline supply hubs
- NO railways queued towards France

**Code Locations:**
- Border check: lines 343-376
- Enemy iteration: lines 396-450

**Validation Method:**
1. For SOV: `borders_enemy_` = 1, railways queued
2. For FRA: `borders_enemy_` = 0, no railways queued
3. Verify all `railway_end_provinces_` are on SOV border, not French

**Expected Result:** PASS - Railways to SOV only

---

## 2. Border Detection Tests

### TC-010: Puppet territory extends border detection

**Scenario:** Country's puppet borders enemy, triggering border detection.

**Setup:**
- Country: Germany (GER)
- Puppet: Slovakia (SLO)
- Enemy: Soviet Union (SOV)
- Slovakia borders SOV-controlled territory
- Germany proper does NOT border SOV

**Expected Behavior:**
- `WA_AI_PC_railway_country_borders_enemy` checks ROOT's puppets (lines 359-374)
- Slovakia's owned states border SOV → `borders_enemy_` = 1
- Germany proceeds with land war strategy against SOV

**Code Locations:**
- Puppet check: lines 359-374
```
every_subject_country = {
    any_owned_state = {
        any_neighbor_state = { is_owned_by = var:_enemy_tag }
    }
}
```

**Validation Method:**
1. Verify puppet iteration occurs
2. Verify puppet's states checked against enemy
3. Verify `borders_enemy_` = 1 due to puppet

**Expected Result:** PASS - Border detected through puppet

---

### TC-011: Enemy puppet territory triggers border detection

**Scenario:** ROOT borders enemy's puppet, should count as bordering enemy.

**Setup:**
- Country: Germany (GER)
- Enemy: Soviet Union (SOV)
- SOV puppet: Mongolia (MON)
- Germany borders Mongolia (hypothetically)

**Expected Behavior:**
- Border check includes enemy's puppets (lines 350-353):
```
OR = {
    is_owned_by = var:_enemy_tag
    owner = { is_subject_of = var:_enemy_tag }
}
```
- Bordering Mongolia counts as bordering SOV
- `borders_enemy_` = 1

**Code Locations:**
- Enemy puppet check: lines 350-353

**Validation Method:**
1. Verify border check includes `owner = { is_subject_of = var:_enemy_tag }`
2. Verify bordering enemy puppet triggers `borders_enemy_` = 1

**Expected Result:** PASS - Border detected through enemy puppet

---

### TC-012: Owned vs Controlled state consistency

**Scenario:** Country owns a state but doesn't control it (enemy occupation).

**Setup:**
- Country: France (FRA)
- Enemy: Germany (GER)
- France owns Alsace-Lorraine
- Germany controls (occupies) Alsace-Lorraine
- Alsace-Lorraine borders Germany proper

**Expected Behavior:**
- Border check uses `any_owned_state` (line 347) → Alsace counts
- `borders_enemy_` = 1 (France "borders" Germany via owned Alsace)
- BUT: Frontline detection uses `every_controlled_state` (line 411)
- Alsace NOT in controlled states → NOT selected as frontline
- Potential inconsistency: border detected but no frontline found

**Code Locations:**
- Border check (owned): line 347
- Frontline detection (controlled): line 411

**Validation Method:**
1. Verify `borders_enemy_` = 1 (owned state borders enemy)
2. Verify Alsace excluded from frontline states (not controlled)
3. Check if other controlled states border Germany
4. Verify system handles this gracefully (no crash, may find other frontlines)

**Expected Result:** EDGE CASE - Border detected but frontline may be empty

---

### TC-013: No border with distant faction enemy

**Scenario:** Two countries at war via faction, but no border at all.

**Setup:**
- Country: Australia (AST)
- Enemy: Germany (GER)
- War status: Active (Australia in Allies)
- Border: NO border between Australia and Germany
- Australia has no puppets bordering Germany

**Expected Behavior:**
- `borders_enemy_` = 0 for Germany
- Land war strategy skipped for Germany
- Overseas war strategy may trigger if Australia has beachhead in Europe

**Code Locations:**
- Border check: lines 343-376
- Strategy selection: lines 396-450 (land), 531-757 (overseas)

**Validation Method:**
1. Verify `borders_enemy_` = 0
2. Verify land war strategy skipped
3. Verify overseas strategy triggered (if applicable)

**Expected Result:** PASS - Correctly identifies no land border

---

### TC-014: Frontline detection includes enemy puppet territories

**Scenario:** Frontline state borders enemy's puppet, not enemy directly.

**Setup:**
- Country: Germany (GER)
- Enemy: Soviet Union (SOV)
- SOV puppet: Tannu Tuva (TAN)
- German state borders Tannu Tuva, not SOV proper

**Expected Behavior:**
- After Fix 11 (EDGE CASE 11): Frontline should be detected
- Check if frontline detection includes:
```
any_neighbor_state = {
    OR = {
        is_controlled_by = var:_current_enemy_tag
        controller = { is_subject_of = var:_current_enemy_tag }
    }
}
```

**Code Locations:**
- Frontline detection: lines 414-416

**Validation Method:**
1. Check current code at line 415
2. If only `is_controlled_by = var:_current_enemy_tag` → FAIL (missing puppet check)
3. If includes puppet check → PASS

**Expected Result:** CHECK CODE - May need fix for enemy puppet frontlines

---

### TC-015: Self-border check (shouldn't trigger)

**Scenario:** Edge case where country might be checked against itself.

**Setup:**
- Country: Any (e.g., Germany)
- Check: Ensure country doesn't trigger border detection against itself

**Expected Behavior:**
- `every_enemy_country` naturally excludes ROOT
- No self-border detection possible

**Code Locations:**
- Enemy iteration: line 396 `every_enemy_country`

**Validation Method:**
1. Verify `every_enemy_country` scope excludes ROOT
2. Verify no self-border check occurs

**Expected Result:** PASS - Self-border impossible

---

## 3. Overseas War Tests

### TC-020: Home port selection within 5 states

**Scenario:** Finding best port near capital for overseas operations.

**Setup:**
- Country: United Kingdom (ENG)
- Capital: London
- Ports within 5 states: Portsmouth (level 8), Dover (level 5), Plymouth (level 6)
- Port beyond 5 states: Gibraltar (level 10)

**Expected Behavior:**
- `WA_AI_PC_railway_get_states_within_distance` finds states within 5 steps
- Gibraltar excluded (too far)
- Portsmouth selected (highest level within range)
- Railway queued: London → Portsmouth

**Code Locations:**
- Distance calculation: lines 472-474
- Port selection: lines 483-505
- Railway queue: lines 508-517

**Validation Method:**
1. Verify `states_within_distance_` contains only states ≤5 steps from capital
2. Verify Gibraltar NOT in array
3. Verify `best_home_port_level` = 8 (Portsmouth)
4. Verify railway queued to Portsmouth

**Expected Result:** PASS - Closest best port selected

---

### TC-021: Beachhead within 15 states of enemy capital

**Scenario:** Beachhead distance validation.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Germany (GER)
- Enemy capital: Berlin
- Beachhead candidate A: Normandy (10 states from Berlin)
- Beachhead candidate B: Morocco (20 states from Berlin)

**Expected Behavior:**
- Distance check: lines 621-638
- Normandy passes (≤15 states)
- Morocco fails (>15 states)
- Morocco rejected even if larger port

**Code Locations:**
- Distance check: lines 623-638

**Validation Method:**
1. Verify `_max_distance = 15` used for enemy capital check
2. Verify `states_within_distance_` populated from enemy capital
3. Verify beachhead rejected if NOT in array

**Expected Result:** PASS - Far beachheads rejected

---

### TC-022: Beachhead pathfinding validation

**Scenario:** Beachhead must have valid path to frontline.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Japan (JAP)
- Beachhead: Singapore (controlled by ENG)
- Japanese territory surrounds Singapore
- NO friendly provinces between Singapore and frontline

**Expected Behavior:**
- Beachhead selected (largest port on continent)
- Pathfinding test: Singapore → any frontline supply hub
- `_pathfind_prov_type = 2` (only ROOT-controlled provinces)
- Path fails (no friendly route)
- `beachhead_valid_` = 0
- Beachhead rejected

**Code Locations:**
- Pathfinding test: lines 679-688
- Validation check: lines 694-698

**Validation Method:**
1. Verify `_pathfind_prov_type = 2` (Fix 21 applied)
2. Verify pathfinding attempted
3. Verify `pathfind_prov_success_` = 0
4. Verify `beachhead_valid_` = 0
5. Verify `best_beachhead_state` = 0 after rejection

**Expected Result:** PASS - Invalid beachhead rejected

---

### TC-023: Single beachhead per continent (Fix 8)

**Scenario:** Multiple enemies on same continent.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy 1: Germany (GER) - Europe
- Enemy 2: Italy (ITA) - Europe
- ENG controls beachheads in both Normandy and Sicily

**Expected Behavior:**
- Fix 8: `_processed_continents_` tracks handled continents
- First enemy (e.g., Germany) → Europe added to processed
- Second enemy (Italy) → Europe already processed → SKIPPED
- Only ONE beachhead processed for Europe

**Code Locations:**
- Continent tracking: lines 528-577
- Skip check: lines 563-577

**Validation Method:**
1. Verify `_processed_continents_` array populated
2. Verify second enemy on same continent skipped
3. Verify only one beachhead railway set queued per continent

**Expected Result:** PASS - Single beachhead per continent (may be limitation)

---

### TC-024: Continent identification accuracy

**Scenario:** Correct continent assignment for states.

**Setup:**
- Test states across all continents:
  - Europe (1): France, Germany
  - North America (2): USA, Canada
  - South America (3): Brazil
  - Asia (4): China, Japan
  - Africa (5): Egypt
  - Middle East (6): Iran, Iraq
  - Australia (7): Australia

**Expected Behavior:**
- Each state correctly identified by continent
- Continent codes match: lines 554-560

**Code Locations:**
- Continent checks: lines 554-560, 651-658, 715-722

**Validation Method:**
1. Verify `is_on_continent` triggers work correctly
2. Verify continent variable set correctly for each region

**Expected Result:** PASS - Correct continent identification

---

### TC-025: Middle East vs Asia continent split

**Scenario:** Beachhead selection across Middle East/Asia boundary.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Iran (PER) - Middle East continent
- ENG controls India (Asia continent)
- India closer geographically to Iran than UK home ports

**Expected Behavior:**
- Iran capital → Middle East continent (6)
- India states → Asia continent (4)
- India NOT considered as beachhead (wrong continent)
- System looks for Middle East beachhead instead

**Code Locations:**
- Continent matching: lines 660-662 `check_variable = { _state_continent = enemy_continent }`

**Validation Method:**
1. Verify Iran identified as Middle East
2. Verify India identified as Asia
3. Verify India excluded from beachhead candidates for Iran war

**Expected Result:** PASS (but potentially suboptimal - design limitation)

---

### TC-026: Beachhead port level comparison

**Scenario:** Selecting beachhead by port level.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Germany (GER)
- ENG controls:
  - Normandy: level 3 port
  - Antwerp: level 7 port
  - Marseille: level 5 port

**Expected Behavior:**
- All three on Europe continent
- All within 15 states of Berlin
- Antwerp selected (highest level)
- `best_beachhead_state` = Antwerp

**Code Locations:**
- Port comparison: lines 598-611

**Validation Method:**
1. Verify iteration through all controlled coastal states
2. Verify level comparison: `naval_base_level_ > best_beachhead_level`
3. Verify Antwerp selected as `best_beachhead_state`

**Expected Result:** PASS - Highest level port selected

---

### TC-027: No valid beachhead found

**Scenario:** Country has no controlled territory on enemy continent.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Japan (JAP)
- ENG controls NO territory in Asia
- All Asian colonies lost to Japan

**Expected Behavior:**
- Beachhead search on Asia continent
- No controlled states on Asia found
- `best_beachhead_state` = 0
- No frontline railways queued for Asia theater
- Home port infrastructure still upgraded (Part A)

**Code Locations:**
- Beachhead search: lines 583-619
- Skip condition: line 703 `check_variable = { best_beachhead_state > 0 }`

**Validation Method:**
1. Verify `best_beachhead_state` remains 0
2. Verify lines 701-753 skipped (no beachhead)
3. Verify home port still processed (Part A independent)

**Expected Result:** PASS - Graceful handling of no beachhead

---

### TC-028: Railway from beachhead (not capital)

**Scenario:** Frontline railways start from beachhead, not capital.

**Setup:**
- Country: United Kingdom (ENG)
- Enemy: Germany (GER)
- Capital: London
- Beachhead: Normandy
- Frontline supply hub: Metz

**Expected Behavior:**
- Part A: Railway London → home port
- Part B: Railway Normandy → Metz
- Frontline railway starts from `best_beachhead_province`, NOT `capital_province`

**Code Locations:**
- Beachhead as start: line 746 `add_to_temp_array = { railway_start_provinces_ = best_beachhead_province }`

**Validation Method:**
1. Verify `railway_start_provinces_` for frontline contains beachhead province
2. Verify `railway_start_provinces_` does NOT contain capital for frontline
3. Capital only used for home port railway

**Expected Result:** PASS - Correct start points

---

## 4. Pre-War Preparation Tests

### TC-030: Justifying wargoal triggers pre-war preparation

**Scenario:** Country justifying wargoal builds preparation railways.

**Setup:**
- Country: Germany (GER)
- Target: Poland (POL)
- Status: Justifying wargoal (NOT at war yet)
- Border: Germany borders Poland
- Civilian factories: 50+

**Expected Behavior:**
- `WA_AI_PC_railway_STRATEGY_prewar_preparation` triggers
- Poland added to `_target_countries_` (line 785)
- Land border detected → land target handling
- Level 3 railways queued (not level 5)
- Priority: @WA_AI_PC_railway_PRIO_PREWAR (lower than wartime)

**Code Locations:**
- Target detection: lines 774-786
- Level setting: line 768 `route_level = 3`
- Priority: line 769

**Validation Method:**
1. Verify `_target_countries_` contains Poland
2. Verify `route_level` = 3
3. Verify `railway_target_levels_` = 3 for all queued

**Expected Result:** PASS - Pre-war railways at level 3

---

### TC-031: Existing wargoal triggers pre-war preparation

**Scenario:** Country has wargoal but hasn't declared war.

**Setup:**
- Country: Germany (GER)
- Target: Czechoslovakia (CZE)
- Status: Has wargoal from focus (NOT at war)
- Trigger: `ROOT = { has_wargoal_against = PREV }`

**Expected Behavior:**
- Czechoslovakia added to `_target_countries_`
- Pre-war preparation executed

**Code Locations:**
- Wargoal check: line 782 `ROOT = { has_wargoal_against = PREV }`

**Validation Method:**
1. Verify `has_wargoal_against` trigger works
2. Verify target added to array

**Expected Result:** PASS - Wargoal detected

---

### TC-032: Claims on neighbor trigger pre-war preparation

**Scenario:** Country has claims on neighboring country's territory.

**Setup:**
- Country: Hungary (HUN)
- Target: Czechoslovakia (CZE)
- Status: Hungary has claims on Slovak territory
- CZE is neighbor of Hungary

**Expected Behavior:**
- Lines 788-801: `every_neighbor_country` with claims check
- CZE added to `_target_countries_`

**Code Locations:**
- Neighbor claims: lines 788-801

**Validation Method:**
1. Verify `every_neighbor_country` iteration
2. Verify `any_owned_state = { is_claimed_by = ROOT }` check
3. Verify CZE added to targets

**Expected Result:** PASS - Neighbor claims detected

---

### TC-033: Claims on non-neighbor trigger pre-war preparation (Fix 14)

**Scenario:** Country has claims on non-neighboring country.

**Setup:**
- Country: Hungary (HUN)
- Target: Romania (ROM)
- Status: Hungary has claims on Transylvania
- Romania is NOT direct neighbor (Yugoslavia in between)

**Expected Behavior:**
- Fix 14: lines 803-816 check all countries with claims
- Romania added to `_target_countries_`
- Land border check: `target_has_land_border` = 0 (no direct border)
- If Hungary is landlocked → overseas logic skipped (Fix 22)

**Code Locations:**
- Non-neighbor claims: lines 803-816
- Border check: lines 821-830

**Validation Method:**
1. Verify Romania added via Fix 14 (lines 803-816)
2. Verify `target_has_land_border` = 0
3. Verify Fix 22 prevents overseas logic for landlocked Hungary

**Expected Result:** PASS - Claims detected, overseas logic skipped for landlocked

---

### TC-034: Pre-war level 3 threshold (not level 5)

**Scenario:** Pre-war skips states with level 3+ railways.

**Setup:**
- Country: Germany (GER)
- Target: Poland (POL)
- State A: Level 2 railway (should upgrade)
- State B: Level 3 railway (should skip)
- State C: Level 5 railway (should skip)

**Expected Behavior:**
- Line 844: `NOT = { WA_AI_PC_state_has_railway_level_3 = yes }`
- State A: Queued for upgrade to level 3
- State B: Skipped (already level 3)
- State C: Skipped (already level 5)

**Code Locations:**
- Level check: line 844

**Validation Method:**
1. Verify level 3 threshold used (not level 5)
2. Verify states with level 3+ excluded
3. Verify only <3 level states queued

**Expected Result:** PASS - Correct level threshold

---

### TC-035: Pre-war pathfinding validation (Fix 23)

**Scenario:** Pre-war targets validated with pathfinding.

**Setup:**
- Country: Germany (GER)
- Target: Lithuania (LIT) - Memel
- Memel potentially detached from main Germany

**Expected Behavior:**
- Fix 23: Pathfinding validation added to pre-war
- `_pathfind_prov_type = 2` (ROOT-only)
- If no path exists → railway NOT queued

**Code Locations:**
- Fix 23: lines 855-867 (approximately, after fix applied)

**Validation Method:**
1. Verify pathfinding call exists in pre-war land target handling
2. Verify `_pathfind_prov_type = 2`
3. Verify conditional queue based on `pathfind_prov_success_`

**Expected Result:** PASS - Pathfinding validation present

---

### TC-036: Landlocked nation pre-war overseas skip (Fix 22)

**Scenario:** Landlocked nation with claims on non-neighbor.

**Setup:**
- Country: Hungary (HUN) - LANDLOCKED
- Target: Romania (ROM) via claims
- No land border: `target_has_land_border` = 0

**Expected Behavior:**
- Fix 22: `else_if` with coastal check
- Hungary has no coastal states → `any_controlled_state = { is_coastal = yes }` = FALSE
- Overseas logic block SKIPPED entirely
- No port infrastructure attempted

**Code Locations:**
- Fix 22: line 862 `else_if = { limit = { any_controlled_state = { is_coastal = yes } } }`

**Validation Method:**
1. Verify `else_if` structure (not `else`)
2. Verify coastal check in limit
3. Verify Hungary skips entire overseas block

**Expected Result:** PASS - Landlocked overseas skip

---

## 5. Pathfinding Tests

### TC-040: Pathfinding type 2 for railways (Fix 21)

**Scenario:** Railway pathfinding only uses ROOT-controlled provinces.

**Setup:**
- Country: United Kingdom (ENG)
- Ally: France (FRA)
- French provinces between UK beachhead and frontline

**Expected Behavior:**
- `_pathfind_prov_type = 2` (Fix 21)
- Type 2 filter: `controls_province = neighbor_id` only
- NO `any_allied_country` check
- Path through French provinces FAILS
- Only UK-controlled path considered

**Code Locations:**
- Type 2 filter: `WA_AI_pathfinding_effects.txt` lines 447-450 (only ROOT-controlled provinces allowed)
- Railway usage: All railway pathfinding calls use `_pathfind_prov_type = 2` (see `WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt`)

**Validation Method:**
1. Verify `_pathfind_prov_type = 2` in railway code
2. Verify type 2 only allows ROOT-controlled
3. Verify allied provinces excluded

**Expected Result:** PASS - Allied territory excluded

---

### TC-041: Pathfinding through own territory only

**Scenario:** Valid path exists only through own territory.

**Setup:**
- Country: Germany (GER)
- Start: Berlin
- End: Warsaw (after Polish conquest)
- All provinces German-controlled

**Expected Behavior:**
- Pathfinding succeeds
- `pathfind_prov_success_` = 1
- `pathfind_prov_path_` contains valid province sequence

**Code Locations:**
- Main pathfinding: `WA_AI_pathfinding_effects.txt` lines 264-408

**Validation Method:**
1. Verify pathfinding called with valid start/end
2. Verify success flag = 1
3. Verify path array populated

**Expected Result:** PASS - Valid path found

---

### TC-042: Pathfinding fails for enclave

**Scenario:** Target province in enclave (no land connection).

**Setup:**
- Country: Germany (GER)
- Start: Berlin
- End: East Prussia (pre-war, separated by Polish Corridor)
- Polish Corridor NOT controlled by Germany

**Expected Behavior:**
- Pathfinding type 2: only German provinces
- Polish Corridor excluded
- No valid path exists
- `pathfind_prov_success_` = 0

**Code Locations:**
- Failure handling: lines 404-407

**Validation Method:**
1. Verify pathfinding attempted
2. Verify Polish provinces excluded (not ROOT-controlled)
3. Verify `pathfind_prov_success_` = 0

**Expected Result:** PASS - Enclave correctly identified

---

### TC-043: Pathfinding iteration limit (100)

**Scenario:** Very long path might hit iteration limit.

**Setup:**
- Very long distance path (edge of map to edge)
- Path exists but requires >100 iterations

**Expected Behavior:**
- Max iterations: line 276 `while_loop_effect = { limit = { check_variable = { its < 100 } }`
- If limit hit before path found → failure
- `pathfind_prov_success_` = 0

**Code Locations:**
- Iteration limit: line 276

**Validation Method:**
1. Verify iteration limit exists
2. For very long paths, verify graceful failure

**Expected Result:** EDGE CASE - May fail for extremely long paths

---

### TC-044: Railway cost reduction for existing railways

**Scenario:** Pathfinding prefers existing railway connections.

**Setup:**
- Two possible paths:
  - Path A: No railways, 10 provinces
  - Path B: Existing level 3 railway, 12 provinces

**Expected Behavior:**
- G-cost calculation: lines 493-517
- Existing railway: `divisor = level + 1`, `neighbor_g_ / divisor`
- Level 3 railway: cost divided by 4
- Path B may be preferred despite longer distance

**Code Locations:**
- Railway bonus: lines 511-515

**Validation Method:**
1. Verify railway connection check
2. Verify cost reduction applied
3. Verify path selection considers railway bonus

**Expected Result:** PASS - Railways reduce pathfinding cost

---

### TC-045: Path reconstruction

**Scenario:** Correct path array built from A* result.

**Setup:**
- Valid path found from A to B
- Multiple intermediate provinces

**Expected Behavior:**
- `WA_AI_PATHFIND_PROV_build_path` reconstructs path
- Uses `came_from_id` array
- Builds `pathfind_prov_path_` from end to start, then reverses

**Code Locations:**
- Path reconstruction: lines 331-346

**Validation Method:**
1. Verify `pathfind_prov_path_` populated
2. Verify path starts at start province
3. Verify path ends at end province
4. Verify all intermediate provinces are connected

**Expected Result:** PASS - Correct path reconstruction

---

### TC-046: Ocean province exclusion

**Scenario:** Pathfinding doesn't cross ocean provinces.

**Setup:**
- Start: Mainland province
- End: Island province
- Only ocean between them

**Expected Behavior:**
- Ocean provinces excluded from neighbors (implicit in control check)
- Pathfinding fails (no land route)
- `pathfind_prov_success_` = 0

**Code Locations:**
- Province filtering: lines 418-456

**Validation Method:**
1. Verify ocean provinces not considered
2. Verify path fails for water-separated territories

**Expected Result:** PASS - Ocean excluded

---

## 6. Edge Case Tests

### TC-050: Civilian factory threshold - 50 (normal)

**Scenario:** Country below 50 civilian factories.

**Setup:**
- Country: Romania (ROM)
- Civilian factories: 40
- War status: NOT at war

**Expected Behavior:**
- Threshold check: line 34-38
- 40 < 50 → requirement NOT met
- Railway system does NOT trigger

**Code Locations:**
- Threshold: lines 34-38

**Validation Method:**
1. Verify `num_factories >= 50` check
2. Verify system skipped for <50 civs

**Expected Result:** PASS - Below threshold skipped

---

### TC-051: Civilian factory threshold - 30 (wartime)

**Scenario:** Country at war with reduced threshold.

**Setup:**
- Country: Romania (ROM)
- Civilian factories: 35
- War status: AT WAR

**Expected Behavior:**
- War adjustment: 60% multiplier (line 36-38)
- Adjusted threshold: 50 × 0.6 = 30
- 35 ≥ 30 → requirement met
- Railway system triggers

**Code Locations:**
- War adjustment: lines 36-38

**Validation Method:**
1. Verify war condition checked
2. Verify multiplier applied (0.6)
3. Verify 35 passes threshold

**Expected Result:** PASS - War threshold allows lower civs

---

### TC-052: 12-week update interval

**Scenario:** System respects update interval.

**Setup:**
- Initial run at week 0
- Check at week 6 (mid-interval)
- Check at week 12 (next interval)

**Expected Behavior:**
- Counter decremented each call
- At 0: full execution + reset to 12
- Between 0-12: skip execution

**Code Locations:**
- Interval check: line 21
- Interval value: line 14 `@WA_AI_PC_railway_INTERVAL = 12`

**Validation Method:**
1. Verify counter mechanism
2. Verify execution only at counter = 0
3. Verify reset after execution to 12 (not 26)

**Expected Result:** PASS - Correct interval behavior (3 months / 12 weeks)

---

### TC-053: Capitulated country exclusion

**Scenario:** Capitulated country doesn't build railways.

**Setup:**
- Country: France (FRA)
- Status: Capitulated to Germany

**Expected Behavior:**
- Check: `NOT = { has_capitulated = yes }`
- Capitulated → system skipped

**Code Locations:**
- Capitulation check: lines 40-44

**Validation Method:**
1. Verify capitulation check exists
2. Verify capitulated countries skip system

**Expected Result:** PASS - Capitulated excluded

---

### TC-054: Peace treaty clears railway queue (Fix 5 & 19)

**Scenario:** Peace signed, queued railways cleared.

**Setup:**
- Country: Germany (GER)
- War with: Poland (POL)
- Railways queued to Polish front
- Peace signed

**Expected Behavior:**
- `on_peace` action triggers
- Railway queue cleared
- No outdated railways built

**Code Locations:**
- Peace handling: `WA_AI_misc_on_actions.txt` lines 289-312

**Validation Method:**
1. Verify `on_peace` handler exists
2. Verify queue clearing logic
3. Verify no post-peace railway construction to old targets

**Expected Result:** PASS - Queue cleared on peace

---

### TC-055: Multi-front central hub calculation

**Scenario:** Two opposite fronts, center calculation.

**Setup:**
- Country: Germany (GER)
- Front 1: Western (France) - supply hubs at x=100
- Front 2: Eastern (Soviet) - supply hubs at x=500
- Center: approximately x=300

**Expected Behavior:**
- `WA_AI_PC_railway_prioritize_central_hub` calculates geometric center
- Hub closest to center gets 1.1x priority boost
- May prioritize middle hub over strategically important one

**Code Locations:**
- Central hub: lines 922-977

**Validation Method:**
1. Verify center calculation logic
2. Verify priority boost applied
3. Note: This may be suboptimal (documented limitation)

**Expected Result:** PASS (but potentially suboptimal prioritization)

---

### TC-056: Duplicate supply hub prevention

**Scenario:** Same supply hub found multiple times.

**Setup:**
- Supply hub province borders two enemy states
- Could be added twice

**Expected Behavior:**
- Check: `NOT = { is_in_array = { railway_end_provinces_ = supply_hub_province_ } }`
- Duplicate prevented

**Code Locations:**
- Duplicate check: line 429, 743, 853

**Validation Method:**
1. Verify `is_in_array` check before adding
2. Verify no duplicates in `railway_end_provinces_`

**Expected Result:** PASS - Duplicates prevented

---

### TC-057: Supply hub detection (supply_node OR naval_base)

**Scenario:** State has supply hub, correctly detected.

**Setup:**
- State A: Has supply_node building
- State B: Has naval_base building
- State C: Has neither

**Expected Behavior:**
- `WA_AI_PC_state_has_supply_hub` returns:
  - State A: YES
  - State B: YES
  - State C: NO

**Code Locations:**
- Trigger: `WA_AI_CONSTRUCTION_triggers.txt` lines 505-539 (`WA_AI_PC_state_has_supply_hub` and `WA_AI_PC_prov_has_supply_hub`)

**Validation Method:**
1. Verify trigger checks both supply_node and naval_base
2. Verify OR logic (either one = hub)

**Expected Result:** PASS - Both types detected

---

### TC-058: Railway level 5 skip (wartime)

**Scenario:** State already has level 5 railway.

**Setup:**
- Frontline state with supply hub
- Already has level 5 railway (from focus/event)

**Expected Behavior:**
- Check: `NOT = { WA_AI_PC_state_has_railway_level_5 = yes }`
- State skipped (no need to rebuild)

**Code Locations:**
- Level 5 check: line 420, 734

**Validation Method:**
1. Verify level 5 check
2. Verify state excluded from queue

**Expected Result:** PASS - Level 5 states skipped

---

### TC-059: Port upgrade queuing

**Scenario:** Best port marked for upgrade.

**Setup:**
- Best home port: level 5
- Beachhead port: level 3

**Expected Behavior:**
- Both added to `railway_port_upgrades_` array
- Processed by `WA_AI_PC_process_port_upgrades`

**Code Locations:**
- Home port upgrade: line 522
- Beachhead upgrade: line 708
- Processing: lines 1075-1110

**Validation Method:**
1. Verify ports added to upgrade array
2. Verify processing function exists
3. Verify `build naval_base` triggered

**Expected Result:** PASS - Ports queued for upgrade

---

### TC-060: No enemies edge case

**Scenario:** Country at peace, no enemies.

**Setup:**
- Country: Switzerland (SWI)
- Status: Neutral, no wars, no justifications, no claims

**Expected Behavior:**
- `every_enemy_country` returns nothing
- No land war strategy
- No overseas war strategy
- `_target_countries_` empty for pre-war
- System completes without action

**Code Locations:**
- Enemy iteration: line 396

**Validation Method:**
1. Verify empty enemy iteration handled
2. Verify no crashes/errors
3. Verify graceful completion

**Expected Result:** PASS - Graceful handling of no enemies

---

### TC-061: AI-only execution

**Scenario:** System only runs for AI, not player.

**Setup:**
- Player country: Germany
- AI country: Soviet Union

**Expected Behavior:**
- Check: `is_ai = yes` (implicit in AI construction system)
- Player Germany: skipped
- AI Soviet Union: executes

**Code Locations:**
- AI check: Implicit in construction priority system

**Validation Method:**
1. Verify player exclusion
2. Verify AI-only execution

**Expected Result:** PASS - AI only

---

### TC-062: Logging when enabled

**Scenario:** Debug logging outputs correctly.

**Setup:**
- Flag: `WA_AI_construction_logging` enabled
- Railway system executes

**Expected Behavior:**
- Log output: `[Year] [Month] | AI | [Country] | CONSTRUCTION: WA_AI_PC_railway`

**Code Locations:**
- Logging calls throughout code

**Validation Method:**
1. Verify logging flag check
2. Verify log output format
3. Verify no logging when disabled

**Expected Result:** PASS - Logging works correctly

---

## Summary Checklist

### Basic Functionality
- [ ] TC-001: Germany → SOV frontline
- [ ] TC-002: Italy NOT → SOV frontline
- [ ] TC-003: England → port + beachhead
- [ ] TC-004: England NOT → Hong Kong
- [ ] TC-005: Romania → SOV, NOT → France

### Border Detection
- [ ] TC-010: Puppet extends border
- [ ] TC-011: Enemy puppet triggers border
- [ ] TC-012: Owned vs Controlled consistency
- [ ] TC-013: No border with distant enemy
- [ ] TC-014: Enemy puppet frontline detection
- [ ] TC-015: No self-border

### Overseas War
- [ ] TC-020: Home port within 5 states
- [ ] TC-021: Beachhead within 15 states
- [ ] TC-022: Beachhead pathfinding validation
- [ ] TC-023: Single beachhead per continent
- [ ] TC-024: Continent identification
- [ ] TC-025: Middle East vs Asia split
- [ ] TC-026: Port level comparison
- [ ] TC-027: No beachhead found
- [ ] TC-028: Railway from beachhead not capital

### Pre-War Preparation
- [ ] TC-030: Justifying wargoal
- [ ] TC-031: Existing wargoal
- [ ] TC-032: Claims on neighbor
- [ ] TC-033: Claims on non-neighbor (Fix 14)
- [ ] TC-034: Level 3 threshold
- [ ] TC-035: Pathfinding validation (Fix 23)
- [ ] TC-036: Landlocked overseas skip (Fix 22)

### Pathfinding
- [ ] TC-040: Type 2 for railways (Fix 21)
- [ ] TC-041: Own territory path
- [ ] TC-042: Enclave path failure
- [ ] TC-043: Iteration limit
- [ ] TC-044: Railway cost reduction
- [ ] TC-045: Path reconstruction
- [ ] TC-046: Ocean exclusion

### Edge Cases
- [ ] TC-050: 50 civ threshold
- [ ] TC-051: 30 civ war threshold
- [ ] TC-052: 26-week interval
- [ ] TC-053: Capitulated exclusion
- [ ] TC-054: Peace clears queue
- [ ] TC-055: Multi-front center
- [ ] TC-056: Duplicate prevention
- [ ] TC-057: Supply hub detection
- [ ] TC-058: Level 5 skip
- [ ] TC-059: Port upgrade
- [ ] TC-060: No enemies
- [ ] TC-061: AI only
- [ ] TC-062: Logging

---

## Notes for Evaluator

1. **Code locations** reference the main file: `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt`
2. **Fix numbers** (21, 22, 23) refer to recent patches applied to address critical edge cases
3. **Type 2 pathfinding** is the corrected type for railways (only ROOT-controlled provinces)
4. Some tests marked "CHECK CODE" require verification that the fix was properly applied
5. Tests marked "EDGE CASE" may have known limitations that are documented but not necessarily bugs

