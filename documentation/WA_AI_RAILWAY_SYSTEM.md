# World Ablaze AI Railway Building System

## Overview

The World Ablaze AI railway system automatically builds railways from a country's capital to front-line states with supply hubs. It supports three strategies: land wars, overseas invasions, and pre-war preparation.

**Architecture:** Uses a **dynamic queue-based Priority Construction (PC) system** with progress tracking and weekly factory allocation.

## File Structure

### Railway System Files

All files are in `common/scripted_effects/`.

| File | Lines | Purpose |
|------|-------|---------|
| `WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt` | ~282 | Entry point, dispatcher, constants, route processing |
| `WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt` | ~794 | Three strategy implementations |
| `WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt` | ~1031 | Helper functions (30+): port finding, BFS, supply chain, scoring, project management |
| `WA_AI_CONSTRUCTION_PRIORITY_railway_primitives.txt` | ~64 | Low-level helpers: state ID lookup, naval base level, land border check |

### Supporting Files

| File | Purpose |
|------|---------|
| `common/scripted_effects/WA_AI_CONSTRUCTION_effects.txt` | Core PC system (queue, factory allocation, progress tracking) |
| `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` | Supply hub and railway level detection triggers |
| `common/scripted_effects/WA_AI_MAP_province_connections.txt` | Pre-computed province adjacency data |
| `common/scripted_effects/WA_AI_MAP_province_railway_connections.txt` | Pre-computed initial railway levels |
| `common/scripted_effects/WA_AI_pathfinding_effects.txt` | A* pathfinding for route calculation |
| `common/scripted_effects/WA_AI_MAP_effects.txt` | Map utility effects (province neighbors, state mappings) |
| `common/on_actions/WA_AI_misc_on_actions.txt` | Weekly update calls with eligibility filters |

### Test System Files

| File | Purpose |
|------|---------|
| `common/scripted_effects/WA_TEST_railway_framework.txt` | Generic test framework (state management, print function) |
| `common/scripted_effects/WA_TEST_railway.txt` | Railway test suite (8 tests, Japan test bed) |
| `events/wa_events_test.txt` | Periodic checker event for test resolution |

### Tools

| File | Purpose |
|------|---------|
| `tools/generate_province_connections.py` | Generates province adjacency from map files |
| `tools/generate_railway_connections.py` | Generates initial railway state from railways.txt |

## System Parameters

### Core Constants (`railway_core.txt`, lines 11-36)

```
@WA_AI_PC_railway_TYPE_ID = 13              # Building type identifier for railways
@WA_AI_PC_railway_PRIO = 9999              # Wartime priority (highest)
@WA_AI_PC_railway_PRIO_PREWAR = 5000       # Pre-war preparation priority
@WA_AI_PC_railway_INTERVAL_PEACE = 12      # Runs every 12 weeks during peace (~3 months)
@WA_AI_PC_railway_INTERVAL_WAR = 8         # Runs every 8 weeks during war (~2 months)
@WA_AI_PC_railway_MIN_CIVS = 50            # Base minimum civilian factories
@WA_AI_PC_railway_MIN_CIVS_PEACE = 75      # Higher threshold during peace
@WA_AI_PC_railway_MIN_STATES = 5           # Minimum controlled states
@WA_AI_PC_railway_MAX_SURRENDER = 0.3      # Skip if surrender progress > 30%
@WA_AI_PC_railway_MINOR_CIV_THRESHOLD = 50 # Minor nations bypass eligibility above this
@WA_AI_PC_railway_MAX_ROUTES_TOTAL = 8     # Max routes processed per execution
@WA_AI_PC_railway_MAX_ROUTES_PER_ENEMY = 4 # Max routes per enemy country
@WA_AI_PC_railway_QUEUE_SKIP_THRESHOLD = 3 # Skip recalculation if queue >= 3
@WA_AI_PC_railway_PARTIAL_PATH_PRIORITY_FACTOR = 0.7  # Partial paths get 70% priority
```

### Helper Constants (`railway_helpers.txt`, lines 7-28)

```
@WA_AI_PC_railway_THEATRE_SEPARATION_DISTANCE = 10   # BFS distance for separate theatres
@WA_AI_PC_SUPPLY_RAILWAY_BASE = 4                    # Railway throughput base
@WA_AI_PC_SUPPLY_RAILWAY_PER_LEVEL = 8               # Per level: L1=12, L2=20, L3=28, L4=36, L5=44
@WA_AI_PC_SUPPLY_PORT_PER_LEVEL = 5                  # Port throughput: level * 5
@WA_AI_PC_HOME_PORT_SEARCH_DISTANCE = 5              # Max BFS from capital for home port
@WA_AI_PC_HOME_PORT_TARGET_SUPPLY = 36               # Target supply (L4 railway = 36)
@WA_AI_PC_RAILWAY_BASE_COST = 800                    # Rail segment base cost
@WA_AI_PC_NAVAL_BASE_BASE_COST = 10000               # Naval base base cost
@WA_AI_PC_NAVAL_BASE_PER_LEVEL_COST = -556            # Naval base per-level (decreasing)
@WA_AI_PC_RAILWAY_SEGMENTS_PER_STATE = 3              # Estimated segments per state
```

### Strategy Constants (`railway_strategies.txt`, lines 7-8)

```
@WA_AI_PC_railway_MAX_ROUTES_PER_ENEMY = 4   # Redeclared (file-scoped)
@WA_AI_PC_railway_PRIO_PREWAR = 5000          # Redeclared (file-scoped)
```

**Note:** HOI4 `@` constants are file-scoped, so required constants are redeclared in each file that uses them.

## Eligibility Filters

The railway system runs inside `on_weekly` (`WA_AI_misc_on_actions.txt`, lines 110-145). Before `WA_AI_PC_railway` is called, the following filters apply:

| Condition | Peace | War |
|-----------|-------|-----|
| Civilian factories | >= 75 (`@MIN_CIVS_PEACE`) | Always eligible |
| Country status | Must be major, OR at war, OR have 50+ civs | Always eligible |
| Controlled states | >= 5 | >= 5 |
| Surrender progress | < 30% | < 30% |
| AI only | Yes | Yes |

During war, the civilian factory threshold inside `WA_AI_PC_railway` itself is 50 * 0.6 = 30 civs.

## Priority Construction System Architecture

### Key Data Structures

```
# Country-level arrays
arr: WA_AI_PC_queue              # Dynamic queue of project IDs
arr: WA_AI_PC_target_state       # Project state targets (indexed by project_id)

# Project-level variables (indexed by _project_id)
var: WA_AI_PC_target_province^X      # Start province ID (for railways)
var: WA_AI_PC_connect_province^X     # End province ID (for railways)
var: WA_AI_PC_project_cost^X         # Total construction cost
var: WA_AI_PC_progress^X             # Remaining progress (decrements weekly)
var: WA_AI_PC_building_type^X        # Building type (13=railway, 14=naval_base)
var: WA_AI_PC_assigned_factories^X   # Factories currently assigned
var: WA_AI_PC_priority^X             # Project priority
```

### Weekly Update Cycle

```
on_weekly:
  1. WA_AI_PC_assign_factories
     - Reset all project factory assignments
     - Allocate 35% of available civs to projects
     - Assign from top of queue (up to 15 per project)

  2. WA_AI_PC_update_project_progress
     - For each project with factories:
       progress -= (speed * factories * 7)
     - If progress <= 0: complete project

  3. WA_AI_PC_railway (every 8-12 weeks depending on peace/war)
     - Evaluate railway needs
     - Queue new railway projects
```

### Interval Behavior

The interval counter is managed inside `WA_AI_PC_railway` (`railway_core.txt`, line 43):
- **At war**: Counter resets to `@WA_AI_PC_railway_INTERVAL_WAR` (8 weeks, ~2 months)
- **At peace**: Counter resets to `@WA_AI_PC_railway_INTERVAL_PEACE` (12 weeks, ~3 months)
- Counter decrements by 1 each weekly call
- Execution occurs when counter reaches 0

## Three Strategies

### 1. Land War Strategy (`railway_strategies.txt`, lines 18-228)

**Trigger:** Country is at war with an enemy that shares a land border.

**Behavior:**
- Uses `WA_AI_PC_railway_get_relevant_enemies` to pre-filter enemies (majors, 50+ factories, or direct border)
- For each relevant enemy ROOT directly borders (via `WA_AI_PC_railway_country_borders_enemy`):
  - Finds frontline controlled states with supply hubs bordering that enemy
  - Skips single-node states (detected via `WA_AI_PC_coastal_state_is_single_node`)
  - Skips states already at railway level 5
  - Handles cross-landmass targets via overseas supply chain analysis (cached per landmass)
  - Queues port upgrades for bottlenecked overseas routes
- Pathfinds (type 2 = ROOT-controlled provinces only, allows partial paths)
- Sorts all targets by enemy threat (factories + divisions*5) via `WA_AI_PC_railway_score_and_sort_by_enemy_threat`
- Default route level: 5, priority: 9999

**Example:** Germany vs Soviet Union
- Germany borders SOV → builds railways from Berlin to each frontline supply hub
- Italy does NOT border SOV → Italy builds nothing to SOV front (correct)

### 2. Overseas War Strategy (`railway_strategies.txt`, lines 236-528)

**Trigger:** Country is at war with an enemy on a different landmass (no land border).

**Part A - Home Port (lines 236-350):**
- Finds best naval base within 5 BFS states of capital using cost-based scoring (maximize supply, minimize cost as tiebreaker)
- Queues level 5 railway from capital to that port
- Marks port for upgrade construction

**Part B - Beachhead Expansion (lines 352-528):**
- For each overseas enemy, identifies their capital's continent
- Finds ROOT's largest port on that continent (beachhead candidate)
- **Theatre separation check**: If multiple beachheads on same continent, must be 10+ BFS states apart
- **Distance check**: Beachhead must be within 15 BFS states of enemy capital
- **Pathfinding validation**: Tests if beachhead has a valid path (type 2) to at least one frontline supply hub
- If valid, builds railways from beachhead to all frontline supply hubs on that continent
- Skips states already at level 5

**Example:** USA vs Japan
- Part A: Railway from Washington D.C. to best West Coast port
- Part B: From captured Philippines port, railways to frontline supply hubs

### 3. Pre-War Preparation Strategy (`railway_strategies.txt`, lines 560-793)

**Trigger:** Country is NOT at war, but has wargoals, justifications, or claims.

**Target Detection:**
1. Scripted overrides (e.g., GER→SOV for Barbarossa) via `WA_AI_PC_railway_get_scripted_override_targets` (line 536)
2. Countries ROOT is justifying against
3. Countries ROOT has wargoals against
4. Neighbor countries with ROOT's claims on their states
5. Non-neighbor countries with ROOT's claims (any distance)

**Land Target Handling:**
- Builds level 3 railways to border states with supply hubs
- Skips states already at level 3+ railways
- Pathfinding validation (type 2, ROOT-only provinces)

**Overseas Target Handling:**
- Only if ROOT has coastal access (prevents landlocked nations like Hungary from running overseas logic)
- Upgrades home port infrastructure via overseas supply chain analysis (cached per landmass)

**Route priority:** 5000 (`@WA_AI_PC_railway_PRIO_PREWAR`)

## Route Processing Pipeline (`railway_core.txt`, lines 85-200)

After strategies populate the output arrays, the core processes each route:

1. **Pathfinding**: A* via `WA_AI_PATHFIND_PROV_get_path` with `_pathfind_prov_type = 2` (ROOT-only) and `_pathfind_prov_allow_partial = 1`
2. **Partial path handling**: Dead-end paths at coastal provinces trigger `WA_AI_PC_create_frontier_port` (queues port construction)
3. **Segment creation**: For each segment in the path, calls `WA_AI_PC_start_railway_project`
4. **Stale project validation**: Existing queued projects are checked; those targeting states no longer on the frontline are cancelled
5. **Port upgrades**: Processed via `WA_AI_PC_process_port_upgrades` (builds naval bases via PC system)
6. **Factory override**: When railway projects are queued, sets override flag to allocate up to 50% extra factory capacity for 30 days

## Function Reference

### Core (`railway_core.txt`)

| Function | Line | Description |
|----------|------|-------------|
| `WA_AI_PC_railway` | 43 | Main entry point. Manages interval, checks eligibility, dispatches strategies, processes routes. |
| `WA_AI_PC_railway_STRATEGIES` | 209 | Strategy dispatcher. Gets capital info, checks enemy types, calls strategies. |

### Strategies (`railway_strategies.txt`)

| Function | Line | Description |
|----------|------|-------------|
| `WA_AI_PC_railway_STRATEGY_land_war` | 18 | Land war: capital → frontline supply hubs per direct-border enemy. |
| `WA_AI_PC_railway_STRATEGY_overseas_war` | 236 | Overseas war: home port + beachhead expansion. |
| `WA_AI_PC_railway_get_scripted_override_targets` | 536 | Scripted override targets (e.g., GER→SOV). |
| `WA_AI_PC_railway_STRATEGY_prewar_preparation` | 560 | Pre-war: wargoal/claim/override targets at level 3. |

### Helpers (`railway_helpers.txt`)

| Function | Line | Input → Output | Description |
|----------|------|----------------|-------------|
| `WA_AI_PC_railway_get_continent` | 35 | THIS=state → `continent_id_` (1-7) | Continent detection. 1=europe, 2=north_america, 3=south_america, 4=asia, 5=africa, 6=middle_east, 7=australia. |
| `WA_AI_PC_railway_find_best_home_port` | 54 | `capital_state_id` → `best_home_port_state_`, `_level_`, `_province_`, `_score_` | Finds best port within BFS distance of capital using cost-based scoring. |
| `WA_AI_PC_check_theatre_separation` | 147 | `candidate_beachhead_state_`, `_beachhead_states_` → `_is_duplicate_theatre_` | Checks if beachhead is in separate theatre (landmass or 10+ BFS). |
| `WA_AI_PC_railway_check_land_access_to_enemies` | 189 | → `has_land_enemy_`, `has_overseas_enemy_` | Classifies each enemy as land or overseas. |
| `WA_AI_PC_railway_get_relevant_enemies` | 215 | → `_relevant_enemies_` array | Pre-filters enemies: majors, 50+ factories, or direct border. |
| `WA_AI_PC_railway_get_states_within_distance` | 271 | `_origin_state_id`, `_max_distance` → `states_within_distance_` | BFS state traversal within N adjacency steps. |
| `WA_AI_PC_railway_get_supply_hub_province` | 323 | THIS=state → `supply_hub_province_` | Finds supply hub province via `meta_effect`. |
| `WA_AI_PC_railway_get_naval_base_province` | 347 | THIS=state → `naval_base_province_`, `naval_base_level_` | Finds naval base province and level. |
| `WA_AI_PC_railway_state_has_supply_hub` | 380 | THIS=state → `has_supply_`, `supply_hub_province_` | Quick check + province ID. |
| `WA_AI_PC_railway_country_borders_enemy` | 400 | `_enemy_tag` → `borders_enemy_` | ROOT's controlled states border enemy (includes enemy puppets). |
| `WA_AI_PC_railway_score_and_sort_by_enemy_threat` | 428 | Modifies arrays in-place | Scores enemies by threat (factories + divs*5), bubble sorts, boosts top threat +10%. |
| `WA_AI_PC_get_best_port_on_landmass` | 544 | `_search_landmass` → `best_port_level_`, `_province_`, `_state_`, `_supply_` | Highest-level naval base on a landmass. |
| `WA_AI_PC_calculate_supply_bottleneck` | 583 | `_supply_a`, `_supply_b` → `bottleneck_supply_` | Returns min(a, b). |
| `WA_AI_PC_supply_to_railway_level` | 595 | `_supply_capacity` → `max_railway_level_` | Converts supply to max useful railway level: (supply-4)/8, clamped 0-5. |
| `WA_AI_PC_calculate_railway_supply` | 612 | `_railway_level` → `railway_supply_` | Railway supply formula: 4 + 8*level. |
| `WA_AI_PC_calculate_port_supply` | 620 | `_port_level` → `port_supply_` | Port supply formula: level * 5. |
| `WA_AI_PC_supply_to_target_railway` | 627 | `_target_supply` → `target_railway_level_` | Inverse: (supply-4)/8 rounded up, clamped 1-5. |
| `WA_AI_PC_supply_to_target_port` | 646 | `_target_supply` → `target_port_level_` | Inverse: supply/5 rounded up, clamped 1-10. |
| `WA_AI_PC_estimate_railway_cost` | 668 | `_bfs_distance`, `_target_level` → `estimated_railway_cost_` | Cost: distance * 3 segments * 800 * level. |
| `WA_AI_PC_calculate_port_upgrade_cost` | 682 | `_current_port_level`, `_target_port_level` → `port_upgrade_cost_` | Sum of per-level costs. |
| `WA_AI_PC_score_port_candidate` | 713 | `_candidate_port_level`, `_bfs_distance` → `port_score_` | Score: achievable_supply * 100000 - total_cost. |
| `WA_AI_PC_coastal_state_is_single_node` | 762 | THIS=state → `is_single_node_` | Detects states with only a port, no supply hub (e.g., Ryukyu). |
| `WA_AI_PC_analyze_overseas_supply_chain` | 783 | `capital_landmass`, `target_landmass` → `overseas_route_start_`, `overseas_max_railway_level_`, `overseas_receiving_port_state_`, `overseas_home_port_state_` | Full supply chain analysis: home port → receiving port → bottleneck → max railway level. |
| `WA_AI_PC_start_railway_project` | 819 | THIS=state, `_project_province_id`, `_project_connect_id`, `_project_target_level`, `_project_priority` | Creates railway project after level/queue checks. |
| `WA_AI_PC_clear_project_inputs` | 869 | — | Clears all temporary railway arrays. |
| `WA_AI_PC_get_total_queued_num` | 878 | `_get_queued_num_building_type`, `_type_id` → `queued_type_num_` | Counts projects of specified type in queue. |
| `WA_AI_PC_process_port_upgrades` | 893 | Uses `railway_port_upgrades_` | Processes port upgrade entries as naval base projects (type 14). |
| `WA_AI_PC_province_is_coastal` | 940 | `_check_province_id` → `is_coastal_province_` | Checks if province is in a coastal state. |
| `WA_AI_PC_create_frontier_port` | 965 | `_frontier_province_id` → `frontier_port_created_` | Queues port construction when partial path ends at coast. |

### Primitives (`railway_primitives.txt`)

| Function | Line | Input → Output | Description |
|----------|------|----------------|-------------|
| `WA_AI_PC_get_state_id` | 13 | THIS=state → `state_id_` | Converts state scope to numeric ID. |
| `WA_AI_PC_get_naval_base_level` | 24 | THIS=state → `naval_base_level_` | Detects naval base level (0-10) via descending trigger chain. |
| `WA_AI_PC_has_land_border_with_enemy` | 48 | `_check_enemy_tag` → `has_land_border_with_enemy_` | Checks if ROOT's controlled states neighbor enemy's controlled states. |

## Output Arrays (populated by strategies)

```
railway_start_provinces_       # Route start province IDs
railway_end_provinces_         # Route end province IDs (supply hub provinces)
railway_target_levels_         # Target railway level per route (1-5)
railway_priorities_            # Priority value per route
railway_port_upgrades_         # State IDs of ports to upgrade
railway_enemy_tags_            # Enemy tag associated with each route
```

## Pathfinding

Uses A* algorithm via `WA_AI_PATHFIND_PROV_get_path`:
- Input: `_pathfind_prov_start`, `_pathfind_prov_end`, `_pathfind_prov_type`
- Output: `pathfind_prov_path_` array of province IDs

### Pathfinding Types

| Type | Neighbor Filter | Cost Model | Use Case |
|------|-----------------|------------|----------|
| 0 | ROOT + allies | Distance only | General pathfinding |
| 1 | ROOT + allies | Distance + terrain | Defensible positions |
| **2** | **ROOT only** | **Railway cost reduction** | **Railway building** |

**All railway strategies use type 2**, which:
- Restricts to ROOT-controlled provinces only (no allied territory)
- Applies cost reduction for existing railways: `cost = base_cost / (railway_level + 1)`
- Ensures railways are only built through own territory

## Peace Handling

When peace is signed (`on_peace` in `WA_AI_misc_on_actions.txt`, lines 301-343):
- All railway projects (type 13) are removed from the construction queue
- Uses a while loop with safety limit of 100
- Interval counter reset to 0 to trigger immediate recalculation

## Data Flow

```
1. on_weekly
   ├── WA_AI_PC_assign_factories (allocate civs to projects)
   ├── WA_AI_PC_update_project_progress (update + complete projects)
   └── Eligibility filters (civs, states, surrender, is_ai)
       └── WA_AI_PC_railway (every 8-12 weeks)

2. WA_AI_PC_railway
   ├── Check interval counter
   ├── Check industrial requirements (50 civs / 30 at war)
   ├── Check queue skip threshold (3+)
   └── WA_AI_PC_railway_STRATEGIES
       ├── Get capital info (state, continent, province, landmass)
       ├── Check enemy types (land/overseas)
       └── Execute applicable strategies
           ├── STRATEGY_land_war → frontline supply hubs
           ├── STRATEGY_overseas_war → home port + beachhead
           └── STRATEGY_prewar_preparation → border states + port

3. Route processing (for each route in arrays)
   ├── A* pathfinding (type 2, allow partial)
   ├── Partial path → frontier port creation
   └── Segment creation → WA_AI_PC_start_railway_project

4. Post-processing
   ├── Stale project validation + cancellation
   ├── Port upgrades via WA_AI_PC_process_port_upgrades
   └── Factory override (50% extra for 30 days)

5. Project completion (via WA_AI_PC_update_project_progress)
   ├── WA_AI_PC_add_finished_building_by_id → build_railway
   └── WA_AI_PC_end_project_by_id → remove from queue
```

## Debugging

### Enable Logging

```
set_country_flag = WA_AI_construction_logging
```

Or use the debug decision `WA_AI_debug_toggle_construction_logging` (visible when `is_debug = yes`).

### Console Commands

HOI4 console requires the `effect` prefix to run scripted effects:

| Command | Effect |
|---------|--------|
| `effect d_WA_TEST_railway` | Launch functional test suite (Japan test bed) |
| `effect d_WA_TEST_results` | Print test results for all registered countries |

You can also call the effects directly: `effect WA_TEST_railway_suite` or `effect WA_TEST_print_all`.

### Debug Decisions (visible in debug mode)

| Decision | Effect |
|----------|--------|
| `WA_AI_debug_reload_map_data` | Reload all map data |
| `WA_AI_debug_toggle_construction_logging` | Enable construction logging |
| `WA_AI_debug_disable_construction_logging` | Disable construction logging |
| `WA_AI_debug_test_railway_system` | Force railway system execution with logging |
| `WA_AI_debug_run_test_railway` | Launch functional test suite |
| `WA_AI_debug_view_test_results` | Print all test results to game.log |

### Log Categories

| Category | Description |
|----------|-------------|
| `RAILWAY ENTRY:` | Entry point, eligibility checks, interval counter |
| `RAILWAY DISPATCH:` | Strategy selection, capital info |
| `RAILWAY LAND:` | Land war strategy decisions |
| `RAILWAY OVERSEAS:` | Overseas war decisions |
| `RAILWAY PREWAR:` | Pre-war preparation |
| `RAILWAY HELPER:` | Helper function calls |

### Log Format

```
[Year] [Month] | AI | [Country] | RAILWAY ENTRY: interval_counter=8
[Year] [Month] | AI | [Country] | RAILWAY DISPATCH: executing STRATEGY_land_war
[Year] [Month] | AI | [Country] | RAILWAY LAND: ADDED route - path_length=15
```

## Functional Test System

See `WA_AI_RAILWAY_SYSTEM_TEST_CASES.md` for the automated test suite documentation.

The test system uses 8 functional tests run as Japan (JAP) covering all strategies, edge cases, data integrity, and primitive functions. Tests are defined in `WA_TEST_railway.txt` with a generic framework in `WA_TEST_railway_framework.txt`.

Key features:
- 4 test states: NOT_LAUNCHED (0), ONGOING (1), PASSED (2), FAILED (3)
- Preserve PASSED results across re-runs (accumulate coverage at different game states)
- Multi-country registry with formatted results output
- 120-day timeout for deferred tests
- Auto-skip with fail_code=99 for game-state-dependent tests

## Limitations

### 1. Province-to-Province Tracking
The system tracks railway connections at the province level. This creates many variables (~9,300 connection entries in pre-computed data), but is necessary because `build_railway` requires province IDs.

### 2. Continent Detection
Uses hardcoded continent IDs (1=europe through 7=australia). Middle East is treated as separate from Asia. If HOI4 adds new continents, this needs updating.

### 3. No Dynamic Supply Hub Building
The system builds railways TO existing supply hubs, but doesn't build new supply hubs in strategic locations.

### 4. Single Capital Start Point
Land war and pre-war strategies always start from capital province. Doesn't optimize for existing railway network topology.

### 5. Single Beachhead Per Continent
Only one beachhead port per enemy continent. Multi-theater operations on the same continent get limited support.

### 6. No Railway Repair
Only builds new railways, doesn't prioritize repairing damaged ones.

### 7. Central Hub Prioritization
Uses geometric center of all targets for hub prioritization, which doesn't account for threat level or strategic importance.

## Related Systems

| System | Description |
|--------|-------------|
| `WA_AI_MAP_startup` | Initializes province connections and railway data at game start |
| `WA_AI_PC_assign_factories` | Weekly factory allocation to queued projects |
| `WA_AI_PC_update_project_progress` | Weekly progress calculation and project completion |
| `WA_AI_PC_start_project` | Adds new projects to the dynamic queue |
| `WA_AI_PC_complete_project_by_id` | Spawns completed buildings |
| `WA_AI_PC_end_project_by_id` | Removes projects from queue |
| `WA_AI_PATHFIND_PROV_get_path` | A* province-level pathfinding |
| `WA_AI_PATHFIND_get_path` | State-level pathfinding for supply lines |
