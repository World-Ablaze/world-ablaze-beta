# AI Railway System - Test Cases

## Part 1: Automated Functional Test Suite

### Overview

The railway system includes an automated in-game test suite that runs 8 functional tests using Japan (JAP) as the test bed. Japan is chosen because it:
- Goes to war early (Marco Polo Bridge, 1937)
- Is an island nation requiring overseas logistics
- Has edge cases (Ryukyu Islands state 1053 = single-node, no supply hub)
- Has multiple theatres (home islands, Asian mainland, Pacific)

### File Locations

| File | Purpose |
|------|---------|
| `common/scripted_effects/WA_TEST_railway_framework.txt` (~433 lines) | Generic test framework: state management, pass/fail marking, timeout, print function |
| `common/scripted_effects/WA_TEST_railway.txt` (~720 lines) | Railway test suite: 8 tests with launch/check pairs |
| `events/wa_events_test.txt` (~55 lines) | Periodic checker event (`wa_test.100`) |
| `common/scripted_effects/zz_debug_effects.txt` | Console commands: `d_WA_TEST_railway`, `d_WA_TEST_results` |
| `common/decisions/_debug_decisions.txt` | Debug decisions for launching/viewing tests |

### Test States

| Value | Constant | Meaning |
|-------|----------|---------|
| 0 | `@WA_TEST_NOT_LAUNCHED` | Test not yet started |
| 1 | `@WA_TEST_ONGOING` | Test currently running, awaiting resolution |
| 2 | `@WA_TEST_PASSED` | Test passed |
| 3 | `@WA_TEST_FAILED` | Test failed (check fail_code for reason) |

### Fail Codes

| Code | Meaning |
|------|---------|
| 0 | No failure |
| 98 | Timeout (120 days exceeded) |
| 99 | Skipped (game state precondition not met) |
| 1-6 | Test-specific failure codes (see individual tests below) |

### Per-Test Data Variables

Stored per country, indexed by test number (1-8):
```
WA_TEST_state^N          # Test state (0-3)
WA_TEST_fail_code^N      # Failure reason code
WA_TEST_launch_day^N     # global.num_days at launch time
WA_TEST_end_day^N        # global.num_days when resolved
WA_TEST_suite_run_count  # How many times the suite has been run
```

### Multi-Country Registry

A global array `global.WA_TEST_registered_countries` stores IDs of all countries that have run tests. The print function iterates this array to display results for all countries at once.

### Running the Tests

**Via console** (HOI4 requires the `effect` prefix):
```
effect WA_TEST_railway_suite       # Launch test suite (scopes to JAP)
effect WA_TEST_print_all           # Print results for ALL registered countries
```

Or using the `d_` shorthand wrappers:
```
effect d_WA_TEST_railway           # Same as above, with log confirmation
effect d_WA_TEST_results           # Same as above, with log confirmation
```

**Via debug decisions** (visible when `is_debug = yes`):
- `WA_AI_debug_run_test_railway` - Launch test suite
- `WA_AI_debug_view_test_results` - Print results to game.log

### Re-Run Behavior (Preserve Passed)

`WA_TEST_init` only resets tests that are NOT already PASSED. This means:
- **Run 1 at peace (1936)**: Tests 003/007/008 pass immediately, 004 is ONGOING, 001/002/006 skip
- **Run 2 at war (~1937.7+)**: Previously PASSED tests stay green, tests 001/002/005/006 now launch
- **Result**: All 8 tests can show PASSED after two runs at different game states

### Execution Flow

```
Console: effect WA_TEST_railway_suite (or effect d_WA_TEST_railway)
  |
  v
WA_TEST_railway_suite (scopes to JAP)
  +-- WA_TEST_register_country (add JAP to global registry)
  +-- WA_TEST_init (reset non-PASSED tests only)
  +-- Enable logging, force interval=0
  +-- Clear existing railway projects (type 13 only)
  +-- WA_TEST_railway_launch_all (launch all 8 tests)
  +-- Schedule wa_test.100 in 7 days
  |
  v
on_weekly fires (existing on_actions)
  +-- WA_AI_PC_railway (runs with interval=0, forced immediate execution)
  |
  v
wa_test.100 (7 days later, then every 28 days)
  +-- WA_TEST_check_timeout on all 8 tests
  +-- WA_TEST_railway_check_all (per-test check logic)
  +-- If any ONGOING: re-fire in 28 days
  +-- If all resolved: log final results, clear suite flag
```

### Print Output Format

The `WA_TEST_print_all` function outputs to `game.log`:

```
=====================================================================
  WA TEST RESULTS - [date]
=====================================================================
  COUNTRY: Japan (JAP) - Suite run #3
---------------------------------------------------------------------
  #   | Name                    | Status  | Code | Activated | Resolved
  001 | Land War                | PASSED  |    0 | day=365   | day=425
  002 | Overseas Strategy       | PASSED  |    0 | day=365   | day=390
  003 | Ryukyu Filter           | PASSED  |    0 | day=0     | day=7
  004 | Pre-War Targets         | PASSED  |    0 | day=0     | day=120
  005 | Queue Data Integrity    | ONGOING |    0 | day=365   | -
  006 | Home Port Selection     | FAILED  |    2 | day=365   | day=425
  007 | Supply Chain Analysis   | PASSED  |    0 | day=0     | day=7
  008 | Single-Node Detection   | PASSED  |    0 | day=0     | day=7
---------------------------------------------------------------------
  SUMMARY: 6 PASSED, 1 FAILED, 1 ONGOING, 0 NOT_LAUNCHED
  Fail codes: 98=TIMEOUT 99=SKIPPED
=====================================================================
```

Day values are `global.num_days` counts. Cross-reference with lifecycle log lines (which contain `[GetYear] [GetMonth]`) for human-readable dates.

---

### The 8 Automated Tests

#### TEST 001: Land War Strategy

**Location:** `WA_TEST_railway.txt` lines 119-180
**Type:** Deferred (requires war + weekly on_action to populate queue)

**What it validates:** When Japan is at war, railway projects appear in the queue targeting Asian mainland states (continent_id = 4).

**Auto-skips when:** Japan is not at war (fail_code=99)

**Check logic:**
1. Verify at least one railway project (type 13) exists in queue
2. Verify at least one project targets a state on the Asian continent

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | Not at war (skipped) |
| 2 | No railway projects in queue |
| 3 | No railway projects target Asian mainland |

---

#### TEST 002: Overseas Strategy

**Location:** `WA_TEST_railway.txt` lines 188-256
**Type:** Deferred

**What it validates:** When Japan is at war with overseas enemies, port upgrade projects (building type 14 = naval_base) appear in the queue.

**Auto-skips when:** Japan is not at war (fail_code=99)

**Check logic:**
1. Verify Japan has at least one overseas enemy
2. Verify at least one port upgrade project (type 14) exists in queue

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | Not at war (skipped) |
| 2 | No overseas enemy found |
| 3 | No port upgrade projects queued |

---

#### TEST 003: Ryukyu Islands Filter

**Location:** `WA_TEST_railway.txt` lines 265-320
**Type:** Immediate (resolves on first checker fire)

**What it validates:** State 1053 (Ryukyu Islands) is correctly detected as a single-node state (port only, no supply hub) AND no railway project ever targets it.

**Auto-skips when:** Japan doesn't control state 1053 (fail_code=99)

**Check logic:**
1. Call `WA_AI_PC_coastal_state_is_single_node` on state 1053 → must return `is_single_node_ = 1`
2. Iterate all railway projects → none should have `target_state = 1053`

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | Single-node detection failed (1053 not detected as single-node) |
| 2 | A railway project targets state 1053 |

---

#### TEST 004: Pre-War Target Detection

**Location:** `WA_TEST_railway.txt` lines 328-380
**Type:** Deferred

**What it validates:** During peacetime, railway projects with pre-war priority (5000) appear when Japan has wargoals, justifications, or claims.

**Auto-skips when:** Japan is already at war (fail_code=99). Best tested at game start (1936).

**Check logic:**
1. Verify at least one railway project exists
2. Verify at least one project has priority = 5000 (`@WA_AI_PC_railway_PRIO_PREWAR`)

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | Already at war (skipped) |
| 2 | No railway projects in queue |
| 3 | No projects with pre-war priority (5000) |

---

#### TEST 005: Queue Data Integrity

**Location:** `WA_TEST_railway.txt` lines 389-493
**Type:** Deferred (needs queue to be populated)

**What it validates:** Every railway project in the queue has valid data: non-zero target_province, connect_province, target_state, positive cost, positive progress, positive priority.

**Auto-skips when:** Never (always launches)

**Check logic:** Iterates all queued projects where `building_type = 13`. For each project, validates:
- `target_province > 0`
- `connect_province > 0`
- `target_state > 0`
- `project_cost > 0`
- `progress > 0`
- `priority > 0`

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | target_province is 0 |
| 2 | connect_province is 0 |
| 3 | target_state is 0 |
| 4 | cost <= 0 |
| 5 | progress <= 0 |
| 6 | priority <= 0 |

---

#### TEST 006: Home Port Selection

**Location:** `WA_TEST_railway.txt` lines 501-571
**Type:** Deferred

**What it validates:** Port upgrade projects target a Japanese home island state. Home island states: 282, 528, 529, 530, 531, 532, 533, 534, 535, 536.

**Auto-skips when:** Japan is not at war (fail_code=99)

**Check logic:**
1. Verify at least one port upgrade project (type 14) exists
2. For each port project, verify its target_state is one of the home island state IDs

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | No port projects in queue |
| 2 | Port project targets a non-home-island state |

---

#### TEST 007: Supply Chain Analysis

**Location:** `WA_TEST_railway.txt` lines 580-657
**Type:** Immediate

**What it validates:** The `WA_AI_PC_analyze_overseas_supply_chain` helper returns valid data when analyzing Japan's capital landmass to Korea (state 525's landmass).

**Auto-skips when:** Never (always launches)

**Check logic:** Directly calls the supply chain analysis function and validates:
- `overseas_route_start_ > 0` (valid route start province)
- `overseas_max_railway_level_ > 0` (non-zero max level)
- `overseas_max_railway_level_ <= 5` (within valid range)
- `overseas_receiving_port_state_ > 0` (valid receiving port)

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | route_start is 0 |
| 2 | max_level is 0 |
| 3 | max_level > 5 (invalid) |
| 4 | receiving_port_state is 0 |
| 5 | Landmass data invalid |

---

#### TEST 008: Single-Node State Detection

**Location:** `WA_TEST_railway.txt` lines 665-719
**Type:** Immediate

**What it validates:** The `WA_AI_PC_coastal_state_is_single_node` primitive correctly identifies:
- State 1053 (Ryukyu Islands) as a single-node state (port only, no supply hub)
- State 528 (Kyushu) as NOT a single-node state (has both port and supply hub)

**Auto-skips when:** Japan doesn't control both states 1053 and 528 (fail_code=99)

**Check logic:**
1. Call single-node check on state 1053 → must return `is_single_node_ = 1`
2. Call single-node check on state 528 → must return `is_single_node_ = 0`

**Fail codes:**
| Code | Meaning |
|------|---------|
| 1 | State 1053 not detected as single-node |
| 2 | State 528 incorrectly detected as single-node |

---

### Test Coverage Matrix

| System Component | Tests |
|-----------------|-------|
| Land war strategy | 001 |
| Overseas war strategy | 002 |
| Pre-war preparation | 004 |
| Single-node detection | 003, 008 |
| Supply chain analysis | 007 |
| Home port selection | 006 |
| Queue data integrity | 005 |
| Railway filtering (Ryukyu) | 003 |

---

## Part 2: Manual Test Cases Reference

The following test cases describe scenarios for manual validation. They reference the current refactored file structure.

### Category 1: Basic Functionality

#### TC-001: Germany builds railways to SOV frontline

**Scenario:** Germany at war with Soviet Union, direct land border.

**Expected:**
- `STRATEGY_land_war` triggers (`strategies.txt` line 18)
- `WA_AI_PC_railway_country_borders_enemy` returns `borders_enemy_ = 1` (`helpers.txt` line 400)
- Frontline states with supply hubs found on SOV border (`strategies.txt` lines 60-97)
- Level 5 railways queued from Berlin to each frontline supply hub
- Threat scoring sorts SOV as high priority (`helpers.txt` line 428)

**Validation:** Check `railway_end_provinces_` contains SOV border supply hubs, `railway_target_levels_` = 5.

---

#### TC-002: Italy should NOT build to SOV frontline

**Scenario:** Italy at war with SOV (same faction as Germany), but no direct border.

**Expected:**
- `WA_AI_PC_railway_country_borders_enemy` returns `borders_enemy_ = 0` for SOV
- Land war strategy skips SOV (`strategies.txt` lines 49-50: `check_variable = { borders_enemy_ = 1 }`)
- Italy may build to enemies it directly borders (e.g., France, Yugoslavia)

**Validation:** SOV frontier provinces NOT in `railway_end_provinces_` for Italy.

---

#### TC-003: England overseas war against Germany

**Scenario:** England at war with Germany, overseas requiring beachhead.

**Expected:**
- `STRATEGY_overseas_war` triggers (`strategies.txt` line 236)
- Part A: Best port within 5 BFS states of London found (`helpers.txt` line 54)
- Part B: Largest port on Europe continent controlled by ENG identified as beachhead
- Theatre separation check (`helpers.txt` line 147) validates beachhead
- Distance check: beachhead within 15 states of Berlin
- Pathfinding validation: valid path (type 2) from beachhead to frontline

**Validation:** Home port railway queued, beachhead railways to frontline supply hubs queued.

---

#### TC-004: England should NOT build from isolated Hong Kong

**Scenario:** England at war with Japan, Hong Kong surrounded by enemy.

**Expected:**
- Hong Kong identified as potential beachhead (port on Asia continent)
- Pathfinding validation fails (type 2, no ROOT-controlled path to frontline)
- Beachhead rejected
- No railways queued from Hong Kong

**Validation:** `pathfind_prov_success_ = 0` for Hong Kong to frontline, no railways queued.

---

#### TC-005: Romania builds to SOV, NOT to France

**Scenario:** Romania at war with both SOV (direct border) and France (no border).

**Expected:**
- `borders_enemy_ = 1` for SOV (direct border)
- `borders_enemy_ = 0` for France (no border)
- Railways queued only to SOV frontline

**Validation:** All `railway_end_provinces_` on SOV border, none towards France.

---

### Category 2: Border Detection

#### TC-010: Enemy puppet territory triggers border

**Scenario:** ROOT borders enemy's puppet (e.g., Germany borders Mongolia, SOV puppet).

**Expected:** Border check includes enemy puppets at `helpers.txt` lines 411-414:
```
OR = {
    is_controlled_by = var:_enemy_tag
    controller = { is_subject_of = var:_enemy_tag }
}
```
`borders_enemy_ = 1` when bordering enemy puppet.

---

#### TC-011: Owned vs Controlled consistency (Fix 24)

**Scenario:** Country owns state but doesn't control it (enemy occupation).

**Expected:** Both border check and frontline detection use `every_controlled_state`. Occupied states excluded from both checks consistently.

**Location:** `helpers.txt` lines 403-408.

---

#### TC-012: Self-border impossible

**Scenario:** Country checks borders against itself.

**Expected:** `every_enemy_country` naturally excludes ROOT. No self-border detection possible.

---

### Category 3: Pre-War Preparation

#### TC-030: Wargoal triggers pre-war preparation

**Scenario:** Germany justifying against Poland, not at war.

**Expected:**
- `STRATEGY_prewar_preparation` triggers (`strategies.txt` line 560)
- Poland found via `ROOT = { is_justifying_wargoal_against = PREV }` or `has_wargoal_against` (lines 615-616)
- Level 3 railways queued (line 568: `default_route_level = 3`)
- Priority 5000 (line 569: `route_priority = @WA_AI_PC_railway_PRIO_PREWAR`)

---

#### TC-031: Claims on non-neighbor + landlocked skip (Fix 14, Fix 22)

**Scenario:** Hungary (landlocked) has claims on Romania (non-neighbor).

**Expected:**
- Romania found via `any_owned_state = { is_claimed_by = ROOT }` (line 617)
- Land border check: `target_has_land_border = 0` (lines 631-639)
- Fix 22 coastal check: Hungary has no coastal states (line 761)
- Overseas logic block skipped entirely
- No nonsensical port construction

---

#### TC-032: Pre-war pathfinding validation (Fix 23)

**Scenario:** Pre-war target separated by foreign territory.

**Expected:**
- Pathfinding validation with `_pathfind_prov_type = 2` (line 740)
- If no ROOT-controlled path exists → railway NOT queued (lines 744-750)

---

#### TC-033: Scripted override targets

**Scenario:** Germany has a scripted override for SOV (Barbarossa preparation).

**Expected:**
- `WA_AI_CONFIG_RAILWAY_has_scripted_override = yes` triggers (line 581)
- `WA_AI_PC_railway_get_scripted_override_targets` populates `_scripted_override_targets_` (line 582)
- Override targets added to `_target_countries_` with safety checks (lines 589-602)
- Standard wargoal/claims targets also detected (no duplication via line 613 check)

---

### Category 4: Pathfinding

#### TC-040: Type 2 for railways (Fix 21)

**Scenario:** Railway pathfinding through territory with allied provinces.

**Expected:**
- `_pathfind_prov_type = 2` used everywhere in railway code
- Type 2 restricts to ROOT-controlled provinces only
- Allied provinces excluded from pathfinding
- No build failures from paths through allied territory

---

#### TC-041: Partial path handling

**Scenario:** Path from capital to target doesn't reach a supply hub but reaches a coastal province.

**Expected:**
- `_pathfind_prov_allow_partial = 1` enables partial paths
- Partial path at coastal province triggers `WA_AI_PC_create_frontier_port` (`helpers.txt` line 965)
- Port construction queued at path endpoint
- Partial path priority reduced by 30% (`@PARTIAL_PATH_PRIORITY_FACTOR = 0.7`)

---

#### TC-042: Enclave path failure

**Scenario:** Target in enclave separated by foreign territory (e.g., East Prussia through Polish Corridor).

**Expected:**
- Pathfinding type 2: Polish provinces excluded (not ROOT-controlled)
- `pathfind_prov_success_ = 0`
- No railway queued to enclave

---

### Category 5: System Behavior

#### TC-050: Interval peace vs war

**Scenario:** Country transitions from peace to war.

**Expected:**
- Peace: interval resets to 12 weeks (`@INTERVAL_PEACE`)
- War: interval resets to 8 weeks (`@INTERVAL_WAR`)
- Counter decrements by 1 each weekly call
- Execution at counter = 0

**Location:** `core.txt` lines 15-17, 47.

---

#### TC-051: Peace clears railway queue (Fix 5 & Fix 19)

**Scenario:** Peace signed after war.

**Expected:**
- `on_peace` handler in `on_actions.txt` lines 301-343
- All type 13 (railway) projects removed from queue
- While loop with safety limit of 100
- Interval counter reset to 0 (immediate recalculation)

---

#### TC-052: Queue skip threshold

**Scenario:** Railway queue already has 3+ projects.

**Expected:**
- `@QUEUE_SKIP_THRESHOLD = 3` check (core.txt line 33)
- If `queued_type_num_ >= 3`, skip strategy execution
- Prevents over-queuing when projects are still in progress

---

#### TC-053: Factory override on railway queueing

**Scenario:** Railway projects queued, factory allocation boosted.

**Expected:**
- Override flag set after projects queued (`core.txt` lines 184-189)
- Up to 50% extra factory capacity for 30 days
- Allows faster construction of critical railway infrastructure

---

### Category 6: Edge Cases

#### TC-060: Single-node state filtering

**Scenario:** Frontline state has only a port, no supply hub (e.g., Ryukyu Islands).

**Expected:**
- `WA_AI_PC_coastal_state_is_single_node` returns `is_single_node_ = 1` (`helpers.txt` line 762)
- State skipped in land war strategy (`strategies.txt` lines 82-86)
- No railway queued to dead-end port states

---

#### TC-061: Cross-landmass targets in land war

**Scenario:** Land war target on different landmass (e.g., Japan fighting on Asian mainland from home islands).

**Expected:**
- Different landmass detected (`strategies.txt` lines 109-110)
- `WA_AI_PC_analyze_overseas_supply_chain` called (`helpers.txt` line 783)
- Results cached per landmass to avoid redundant analysis (lines 118-145)
- Route start changed from capital to overseas supply chain entry point
- Route level capped by supply chain bottleneck

---

#### TC-062: Threat scoring and sorting

**Scenario:** Multiple enemies with different threat levels.

**Expected:**
- `WA_AI_PC_railway_score_and_sort_by_enemy_threat` (`helpers.txt` line 428)
- Threat = factories + divisions * 5
- Targets sorted by descending enemy threat (bubble sort)
- Highest-threat enemy's first target gets +10% priority boost

---

#### TC-063: Duplicate supply hub prevention

**Scenario:** Same supply hub borders two enemy states.

**Expected:**
- `NOT = { is_in_array = { railway_end_provinces_ = supply_hub_province_ } }` check
- Present in land war (`strategies.txt` line 94), pre-war (line 671), and overseas strategies
- No duplicate entries in output arrays

---

#### TC-064: Stale project validation

**Scenario:** Frontline shifts after railway projects were queued.

**Expected:**
- Post-processing in `core.txt` lines 170-173
- Existing projects checked against current frontline
- Projects targeting states no longer on frontline are cancelled
- Prevents building railways to outdated targets

---

## Verification Checklist

### Automated Tests (via `effect WA_TEST_railway_suite`)
- [ ] TEST 001: Land War Strategy (PASSED at war)
- [ ] TEST 002: Overseas Strategy (PASSED at war)
- [ ] TEST 003: Ryukyu Filter (PASSED anytime)
- [ ] TEST 004: Pre-War Targets (PASSED at peace)
- [ ] TEST 005: Queue Data Integrity (PASSED when queue populated)
- [ ] TEST 006: Home Port Selection (PASSED at war)
- [ ] TEST 007: Supply Chain Analysis (PASSED anytime)
- [ ] TEST 008: Single-Node Detection (PASSED anytime)

### Manual Verification
- [ ] TC-001 through TC-005: Basic functionality
- [ ] TC-010 through TC-012: Border detection
- [ ] TC-030 through TC-033: Pre-war preparation
- [ ] TC-040 through TC-042: Pathfinding
- [ ] TC-050 through TC-053: System behavior
- [ ] TC-060 through TC-064: Edge cases

### Two-Run Coverage Pattern
1. **Run 1 at peace (1936):** Tests 003/004/005/007/008 should resolve. Tests 001/002/006 skip.
2. **Run 2 at war (~1937.7+):** Previously PASSED tests preserved. Tests 001/002/005/006 now launch.
3. **Final check:** All 8 tests should show PASSED after both runs.
