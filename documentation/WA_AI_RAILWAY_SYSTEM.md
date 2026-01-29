# World Ablaze AI Railway Building System

## Overview

The World Ablaze AI railway system automatically builds railways from a country's capital to front-line states with supply hubs. It supports land wars, overseas invasions, and pre-war preparation.

**Architecture:** Uses a **dynamic queue-based Priority Construction (PC) system** with progress tracking and weekly factory allocation, similar to Expert AI's architecture.

## File Locations

| File | Purpose |
|------|---------|
| `common/scripted_effects/WA_AI_CONSTRUCTION_effects.txt` | Core PC system (queue, factory allocation, progress tracking) |
| `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt` | Main railway strategies and logic |
| `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` | Supply hub and railway level detection triggers |
| `common/scripted_effects/WA_AI_MAP_province_connections.txt` | Pre-computed province adjacency data |
| `common/scripted_effects/WA_AI_MAP_province_railway_connections.txt` | Pre-computed initial railway levels |
| `common/scripted_effects/WA_AI_pathfinding_effects.txt` | A* pathfinding for route calculation |
| `common/scripted_effects/WA_AI_MAP_effects.txt` | Map utility effects (province neighbors, state mappings) |
| `common/on_actions/WA_AI_misc_on_actions.txt` | Weekly update calls for PC system |
| `tools/generate_province_connections.py` | Generates province adjacency from map files |
| `tools/generate_railway_connections.py` | Generates initial railway state from railways.txt |

## System Parameters

```pdx
@WA_AI_PC_railway_TYPE_ID = 13          # Internal type identifier (building type)
@WA_AI_PC_railway_PRIO = 9999           # Wartime priority (highest)
@WA_AI_PC_railway_PRIO_PREWAR = 5000    # Pre-war preparation priority
@WA_AI_PC_railway_INTERVAL = 12         # Runs every 12 weeks (3 months)
@WA_AI_PC_railway_MIN_CIVS = 50         # Minimum civilian factories required
```

## Priority Construction System Architecture

The railway system is fully integrated with the PC system, which uses a **dynamic queue** architecture:

### Key Data Structures

```pdx
# Country-level arrays
arr: WA_AI_PC_queue              # Dynamic queue of project IDs (unlimited)
arr: WA_AI_PC_target_state       # Project state targets (indexed by project_id)

# Project-level variables (indexed by _project_id)
var: WA_AI_PC_target_province^X      # Start province ID (for railways)
var: WA_AI_PC_connect_province^X     # End province ID (for railways)
var: WA_AI_PC_project_cost^X         # Total construction cost
var: WA_AI_PC_progress^X             # Remaining progress (decrements weekly)
var: WA_AI_PC_building_type^X        # Building type (13 for railways)
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
     - For each project with factories assigned:
       - Calculate: progress -= (speed * factories * 7)
       - If progress <= 0: complete project
       
  3. WA_AI_PC_railway (every 12 weeks)
     - Evaluate railway needs
     - Queue new railway projects via WA_AI_PC_start_project
```

### Project Completion

When a railway project completes:
1. `WA_AI_PC_add_finished_building_by_id` executes `build_railway` with stored province data
2. Updates `global.WA_AI_PC_railway_connection_level_X^Y` tracking variables
3. `WA_AI_PC_end_project_by_id` removes project from queue and clears variables

## Three Strategies

### 1. Land War Strategy (`WA_AI_PC_railway_STRATEGY_land_war`)

**Trigger:** Country is at war with an enemy that shares a land border

**Behavior:**
- **Direct Border Check:** Only builds railways to enemies that ROOT (or ROOT's puppets) directly borders
  - Prevents wasteful construction like Italy building railways to SOV front through Germany
  - Uses `WA_AI_PC_railway_country_borders_enemy` helper to check owned state borders
- Finds all controlled states that border those direct-border enemies
- Filters to states with supply hubs (supply_node or naval_base building)
- Skips states that already have level 5 railways
- Builds level 5 railways from capital to each front-line supply hub
- Prioritizes the "central" hub (closest to geometric center of all targets)

**Example:** Germany vs Soviet Union
- Germany directly borders SOV territory → builds railways
- Front line spans 10 states from Baltic to Black Sea
- System identifies states with supply hubs on the front
- Builds railways from Berlin to each supply hub
- Central hub (e.g., Warsaw area) gets +10% priority boost

**Example:** Italy in Axis vs Soviet Union
- Italy does NOT directly border SOV territory
- Italy's puppets (Libya, etc.) do NOT border SOV
- Result: Italy does NOT build railways to SOV front (correct behavior)

### 2. Overseas War Strategy (`WA_AI_PC_railway_STRATEGY_overseas_war`)

**Trigger:** Country is at war with an enemy on a different continent (no land border)

**Behavior (Part A - Home Port):**
- Finds the best naval base within 5 states (by adjacency) of capital
- Queues level 5 railway from capital to that port
- Marks port for upgrade construction

**Behavior (Part B - Beachhead):**
- For each overseas enemy, identifies their capital's continent
- Finds our largest port on that continent (beachhead)
- **Distance Check:** Beachhead must be within 15 states (by adjacency) of enemy capital
  - Prevents selecting beachheads too far from the actual theater of war
- **Beachhead Validation:** Tests pathfinding from beachhead to at least one frontline supply hub
  - If no valid path exists, the beachhead is skipped (prevents useless beachheads like Hong Kong surrounded by enemy)
- Builds railways from validated beachhead to front-line supply hubs on that continent
- Skips states that already have level 5 railways

**Example:** USA vs Japan
- Part A: Build railway from Washington D.C. to best West Coast port
- Part B: From captured port in Philippines, build railways to front-line supply hubs

**Example:** England vs Japan (Hong Kong scenario)
- Hong Kong is England's port in Asia
- If Hong Kong is surrounded by Japanese-occupied China with no path to frontlines
- Pathfinding validation fails → Hong Kong is skipped as beachhead
- England waits for a better beachhead (e.g., captured port with actual frontline access)

### 3. Pre-War Preparation Strategy (`WA_AI_PC_railway_STRATEGY_prewar_preparation`)

**Trigger:** Country is NOT at war, but is:
- Justifying a war goal against another country
- Has an existing war goal against another country
- Has claims on a neighbor country's states

**Behavior (Land Target):**
- Builds level 3 railways to border states with supply hubs
- Skips states that already have level 3+ railways

**Behavior (Overseas Target):**
- Upgrades home port infrastructure (same as overseas war Part A)

## Supply Hub Detection

The system uses proper HOI4 building checks instead of infrastructure proxies. These are defined as **scripted triggers** in `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`:

```pdx
# State-level check (THIS = state scope)
WA_AI_PC_state_has_supply_hub = {
    OR = {
        any_province_building_level = {
            province = { all_provinces = yes }
            building = supply_node
            level > 0
        }
        any_province_building_level = {
            province = { all_provinces = yes }
            building = naval_base
            level > 0
        }
    }
}

# Province-level check (uses meta_trigger for variable province ID)
WA_AI_PC_prov_has_supply_hub = {
    meta_trigger = {
        text = {
            OR = {
                any_province_building_level = {
                    province = { id = [x] }
                    building = supply_node
                    level > 0
                }
                any_province_building_level = {
                    province = { id = [x] }
                    building = naval_base
                    level > 0
                }
            }
        }
        x = "[?_province_hub_id]"
    }
}
```

**Note:** These triggers are defined in `WA_AI_CONSTRUCTION_triggers.txt` (lines 505-539), not in `WA_AI_MAP_effects.txt`. The `WA_AI_MAP_effects.txt` file only contains map-related effects, not triggers.

## Railway Level Detection

Uses native HOI4 `has_railway_level` trigger to detect ALL railways, including:
- AI-built railways
- Focus-built railways
- Event-built railways
- Starting game railways

```pdx
WA_AI_PC_state_has_railway_level_5 = {
    has_railway_level = {
        state = THIS
        level = 5
    }
}

WA_AI_PC_state_has_railway_level_3 = {
    has_railway_level = {
        state = THIS
        level = 3
    }
}
```

## State Adjacency Calculation

Uses breadth-first wave propagation to find states within N steps:

```pdx
WA_AI_PC_railway_get_states_within_distance = {
    # Input: _origin_state_id, _max_distance
    # Output: states_within_distance_ array

    # Wave 0: origin state
    # Wave 1: immediate neighbors
    # Wave 2: neighbors of neighbors
    # ... up to _max_distance waves
}
```

## Pathfinding

Uses A* algorithm via `WA_AI_PATHFIND_PROV_get_path`:
- Input: `_pathfind_prov_start`, `_pathfind_prov_end`, `_pathfind_prov_type`
- Output: `pathfind_prov_path_` array of province IDs
- Uses pre-computed province connections from `WA_AI_MAP_province_connections_X` arrays

**Note:** The function name is `WA_AI_PATHFIND_PROV_get_path` (with underscores, not slashes). There is also a state-level pathfinding function `WA_AI_PATHFIND_get_path` used for supply line building.

### Pathfinding Types

The `_pathfind_prov_type` parameter controls neighbor filtering and cost calculation:

| Type | Neighbor Filter | G-Cost (Movement) | H-Cost (Heuristic) | Use Case |
|------|-----------------|-------------------|-------------------|----------|
| **0** | ROOT + allies | Distance only | Distance × 1.1 | General pathfinding through friendly territory |
| **1** | ROOT + allies | Distance + terrain modifiers | Distance × 1.1 | Defensible positions (prefers mountains/hills) |
| **2** | ROOT only | Railway cost reduction | Railway heuristic bonus | Railway building (prefers existing railways) |

**Railway strategies use type 2**, which:
- Restricts pathfinding to ROOT-controlled provinces only (no allied territory)
- Applies cost reduction for existing railways: `cost = base_cost / (railway_level + 1)`
- Applies heuristic bonuses for provinces with railway connections
- Ensures railways are only built through own territory

**Important:** This was fixed to prevent pathfinding failures where a path through allied territory would be found, but railway construction would fail because railways can only be built in your own territory.

## Data Flow

```
1. on_weekly (weekly pulse)
   ├── WA_AI_PC_assign_factories
   │   └── Allocate factories to queued projects
   ├── WA_AI_PC_update_project_progress
   │   ├── Update progress for each project
   │   └── Complete finished projects (build railways)
   └── WA_AI_PC_railway (every 12 weeks)

2. WA_AI_PC_railway (main entry)
   ├── Check interval (every 12 weeks / 3 months)
   ├── Check requirements (50+ civs, not capitulated)
   └── Call WA_AI_PC_railway_STRATEGIES
       ├── Get capital info (state, continent, province)
       ├── Check enemy types (land/overseas)
       ├── Execute applicable strategies
       │   ├── STRATEGY_land_war → Find front-line supply hubs
       │   ├── STRATEGY_overseas_war → Home port + beachhead expansion
       │   └── STRATEGY_prewar_preparation → Border states + home port
       └── Build arrays: railway_start_provinces_, railway_end_provinces_, etc.

3. For each route in arrays:
   ├── Call A* pathfinding (WA_AI_PATHFIND_PROV_get_path)
   └── For each segment in path:
       └── WA_AI_PC_start_railway_project
           ├── Check if segment already at target level
           └── Call WA_AI_PC_start_project (adds to queue)

4. Project completion (via WA_AI_PC_update_project_progress)
   ├── WA_AI_PC_complete_project_by_id
   │   └── WA_AI_PC_add_finished_building_by_id
   │       └── Execute build_railway with stored province data
   └── WA_AI_PC_end_project_by_id
       └── Remove from queue, clear variables
```

## Limitations

### 1. Province-to-Province Tracking
The system tracks railway connections at the province level (e.g., `global.WA_AI_PC_railway_connection_level_6521^11444`). This is necessary because:
- `build_railway` command requires province IDs
- The pathfinder works at province level
- Supply hub location needs to be precise

**Limitation:** This creates many variables. The pre-computed file has ~9,300 connection entries.

### 2. Queue Unlimited but Practical Limits
The dynamic queue has no hard limit, but practical constraints exist:
- Factory allocation is limited to 35% of available civs (configurable via `WA_AI_PC_override_max_factories_factor`)
- Each project can receive up to 15 factories
- `_project_queue_max` parameter allows limiting concurrent projects of a type

### 2. Continent Detection
Uses hardcoded continent IDs:
```pdx
europe = 1, north_america = 2, south_america = 3, asia = 4,
africa = 5, middle_east = 6, australia = 7
```

**Limitation:** If HOI4 adds new continents, this needs updating.

### 3. No Dynamic Supply Hub Building
The system builds railways TO existing supply hubs, but doesn't build new supply hubs.

**Limitation:** If a state has no supply hub, it won't be connected even if strategically important.

### 4. Central Hub Prioritization
The "central hub" is determined by geometric center of all targets.

**Limitation:** Doesn't account for:
- Terrain difficulty
- Existing partial railways
- Strategic importance of specific areas

### 5. Single Capital Start Point
Land war and pre-war strategies always start from capital province.

**Limitation:** Doesn't optimize for:
- Multiple starting points (e.g., existing railway network)
- Shortest path from nearest existing level-5 railway

### 6. Fixed Intervals
Runs every 12 weeks (3 months) regardless of war intensity or economic situation.

**Note:** This interval was reduced from 26 weeks (6 months) to allow more frequent updates and better responsiveness to changing front lines.

### 7. No Railway Repair
Only builds new railways, doesn't prioritize repairing damaged ones.

### 8. Overseas: Single Beachhead Per Enemy
Only identifies one beachhead port per enemy continent.

**Limitation:** If fighting on multiple fronts of same continent, only one port is upgraded.

## Python Tools

### generate_province_connections.py

Parses HOI4 map files to generate province adjacency data:
- Reads `definition.csv` for province colors and types
- Scans `provinces.bmp` pixel-by-pixel to detect neighbors
- Optionally includes `adjacencies.csv` for straits/canals
- Filters to land-only provinces by default

```bash
python generate_province_connections.py --map-dir ../map --output ../common/scripted_effects/WA_AI_MAP_province_connections.txt
```

### generate_railway_connections.py

Parses `railways.txt` to pre-compute initial railway state:
- Format: `level count prov1 prov2 prov3...`
- Generates bidirectional connection levels
- Sets `global.WA_AI_PC_railway_connections^PROV = 1` for provinces with railways
- Sets `global.WA_AI_PC_railway_connection_level_X^Y = level` for each connection

```bash
python generate_railway_connections.py --map-dir ../map --output ../common/scripted_effects/WA_AI_MAP_province_railway_connections.txt
```

## Debugging

Enable logging with country flag:
```pdx
set_country_flag = WA_AI_construction_logging
```

Log output format:
```
[Year] [Month] | AI | [Country] | CONSTRUCTION: WA_AI_PC_railway
[Year] [Month] | AI | [Country] | CONSTRUCTION: Port upgrade in [State]
```

## Related Systems

- **WA_AI_MAP_startup**: Initializes province connections and railway data at game start
- **WA_AI_PC_assign_factories**: Weekly factory allocation to queued projects
- **WA_AI_PC_update_project_progress**: Weekly progress calculation and project completion
- **WA_AI_PC_start_project**: Adds new projects to the dynamic queue
- **WA_AI_PC_complete_project_by_id**: Spawns completed buildings
- **WA_AI_PC_end_project_by_id**: Removes projects from queue
- **WA_AI_PC_get_total_queued_num**: Helper effect to count queued projects by building type
- **WA_AI_PC_process_port_upgrades**: Builds naval bases for overseas operations
- **WA_AI_PATHFIND_PROV_***: A* pathfinding implementation for province-level routing
- **WA_AI_PATHFIND_get_path**: State-level pathfinding for supply line building

## Recent Fixes and Architecture Changes

### Dynamic Queue Architecture (Major Refactor)
- **Changed:** Replaced fixed 5-slot decision-based system with dynamic queue
- **Old System:** 5 project slots tied to decision timers, one-time factory allocation
- **New System:** Unlimited queue, weekly progress calculation, dynamic factory allocation
- **Benefits:**
  - No more 5-project limit for railways
  - Proper factory allocation shared with other PC buildings
  - `_project_queue_num` and `_project_queue_max` parameters for controlled batching
  - Progress visibility via `WA_AI_PC_progress^_project_id`
- **Key Functions Added:**
  - `WA_AI_PC_get_new_project_ID`: Gets next available project ID
  - `WA_AI_PC_assign_factories`: Weekly factory allocation
  - `WA_AI_PC_update_project_progress`: Weekly progress calculation
  - `WA_AI_PC_complete_project_by_id`: Completes project and spawns building
  - `WA_AI_PC_end_project_by_id`: Removes project from queue
  - `WA_AI_PC_get_build_speed`: Calculates construction speed for a state
  - `WA_AI_PC_get_building_cost`: Calculates building cost

### Railway PC Integration
- **Changed:** Railways now use the PC system for factory allocation and timing
- **Old:** Separate queue arrays (`WA_AI_PC_railway_queue_*`), instant `build_railway`
- **New:** Uses `WA_AI_PC_start_project` with `connect_province` variable, construction time
- **Variables Added:**
  - `WA_AI_PC_target_province^X`: Start province ID for railway segment
  - `WA_AI_PC_connect_province^X`: End province ID for railway segment
- **Removed:** `WA_AI_PC_process_railway_queue` (now a no-op for compatibility)

### Scripted Triggers vs Scripted Effects
- **Fixed:** Removed duplicate supply hub trigger definitions from `WA_AI_MAP_effects.txt`
- **Reason:** `WA_AI_PC_state_has_supply_hub` and `WA_AI_PC_prov_has_supply_hub` are scripted **triggers** (conditions), not scripted **effects** (actions)
- **Location:** Properly defined in `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` (lines 505-539)
- **Impact:** Prevents "Unknown trigger-type" errors when these are used in `limit` blocks

### Pathfinding Function Names
- **Fixed:** Corrected `WA_AI_PATHFIND/get_path` → `WA_AI_PATHFIND_get_path` (underscore, not slash)
- **Location:** `WA_AI_CONSTRUCTION_effects.txt` line 925
- **Impact:** Prevents "Unknown effect-type" errors

### Trigger vs Effect Usage
- **Fixed:** Changed `any_controlled_state` to `every_controlled_state` in effect contexts
- **Reason:** `any_controlled_state` is a trigger (returns true/false), `every_controlled_state` is an effect (iterates and executes)
- **Locations:** Multiple locations in `WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt` (lines 189, 528, 823)
- **Impact:** Prevents "Unknown effect-type" errors when iterating over states to set variables

### Scripted Effect Usage in Triggers
- **Fixed:** Moved `WA_AI_PC_get_total_queued_num` call outside of `limit` block
- **Reason:** Scripted effects cannot be called inside trigger/limit contexts
- **Location:** `WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt` line 87
- **Impact:** Effect now executes before the condition check, allowing proper variable evaluation

### Pathfinding Code Corruption
- **Fixed:** Corrected mangled code in `WA_AI_pathfinding_effects.txt` (line 249)
- **Issue:** `owest_f_score` typo and broken `set_temp_variable` statement
- **Fix:** Proper `set_temp_variable = { lowest_f_score = WA_AI_PATHFIND_f_score }`
- **Impact:** Prevents parser errors and ensures correct lowest f-score calculation in A* algorithm

## Future Improvements (Ideas)

1. **Smart Starting Points**: Start from nearest existing high-level railway instead of always from capital
2. **Dynamic Intervals**: More frequent checks during active offensives
3. **Supply Hub Construction**: Build supply hubs in strategic locations
4. **Multi-Beachhead Support**: Handle multiple landing zones per continent
5. **Railway Repair Priority**: Detect and prioritize damaged railways
6. **Faction Coordination**: Consider ally railway networks
7. **Economic Scaling**: Adjust railway level targets based on available resources
