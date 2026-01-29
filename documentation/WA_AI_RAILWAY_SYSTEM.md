# World Ablaze AI Railway Building System

## Overview

The World Ablaze AI railway system automatically builds railways from a country's capital to front-line states with supply hubs. It supports land wars, overseas invasions, and pre-war preparation.

## File Locations

| File | Purpose |
|------|---------|
| `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies_misc.txt` | Main railway strategies and logic |
| `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` | Supply hub and railway level detection triggers |
| `common/scripted_effects/WA_AI_MAP_province_connections.txt` | Pre-computed province adjacency data |
| `common/scripted_effects/WA_AI_MAP_province_railway_connections.txt` | Pre-computed initial railway levels |
| `common/scripted_effects/WA_AI_pathfinding_effects.txt` | A* pathfinding for route calculation |
| `tools/generate_province_connections.py` | Generates province adjacency from map files |
| `tools/generate_railway_connections.py` | Generates initial railway state from railways.txt |

## System Parameters

```pdx
@WA_AI_PC_railway_TYPE_ID = 13          # Internal type identifier
@WA_AI_PC_railway_PRIO = 9999           # Wartime priority (highest)
@WA_AI_PC_railway_PRIO_PREWAR = 5000    # Pre-war preparation priority
@WA_AI_PC_railway_INTERVAL = 26         # Runs every 26 weeks (6 months)
@WA_AI_PC_railway_MIN_CIVS = 50         # Minimum civilian factories required
```

## Three Strategies

### 1. Land War Strategy (`WA_AI_PC_railway_STRATEGY_land_war`)

**Trigger:** Country is at war with an enemy that shares a land border

**Behavior:**
- Finds all controlled states that border enemy-controlled states
- Filters to states with supply hubs (supply_node or naval_base building)
- Skips states that already have level 5 railways
- Builds level 5 railways from capital to each front-line supply hub
- Prioritizes the "central" hub (closest to geometric center of all targets)

**Example:** Germany vs Soviet Union
- Front line spans 10 states from Baltic to Black Sea
- System identifies states with supply hubs on the front
- Builds railways from Berlin to each supply hub
- Central hub (e.g., Warsaw area) gets +10% priority boost

### 2. Overseas War Strategy (`WA_AI_PC_railway_STRATEGY_overseas_war`)

**Trigger:** Country is at war with an enemy on a different continent (no land border)

**Behavior (Part A - Home Port):**
- Finds the best naval base within 5 states (by adjacency) of capital
- Queues level 5 railway from capital to that port
- Marks port for upgrade construction

**Behavior (Part B - Beachhead):**
- For each overseas enemy, identifies their capital's continent
- Finds our largest port on that continent (beachhead)
- Builds railways from beachhead to front-line supply hubs on that continent
- Skips states that already have level 5 railways

**Example:** USA vs Japan
- Part A: Build railway from Washington D.C. to best West Coast port
- Part B: From captured port in Philippines, build railways to front-line supply hubs

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

The system uses proper HOI4 building checks instead of infrastructure proxies:

```pdx
# State-level check
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

## Data Flow

```
1. WA_AI_PC_railway (main entry)
   ├── Check interval (every 26 weeks)
   ├── Check requirements (50+ civs, not capitulated)
   └── Call WA_AI_PC_railway_STRATEGIES
       ├── Get capital info (state, continent, province)
       ├── Check enemy types (land/overseas)
       ├── Execute applicable strategies
       │   ├── STRATEGY_land_war → Find front-line supply hubs
       │   ├── STRATEGY_overseas_war → Home port + beachhead expansion
       │   └── STRATEGY_prewar_preparation → Border states + home port
       └── Build arrays: railway_start_provinces_, railway_end_provinces_, etc.

2. For each route in arrays:
   ├── Call A* pathfinding
   └── For each segment in path:
       └── WA_AI_PC_start_railway_project
           ├── Check if segment already at target level
           └── Queue for construction if needed

3. WA_AI_PC_process_railway_queue (called elsewhere)
   └── Execute build_railway command
```

## Limitations

### 1. Province-to-Province Tracking
The system tracks railway connections at the province level (e.g., `global.WA_AI_PC_railway_connection_level_6521^11444`). This is necessary because:
- `build_railway` command requires province IDs
- The pathfinder works at province level
- Supply hub location needs to be precise

**Limitation:** This creates many variables. The pre-computed file has ~9,300 connection entries.

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
Runs every 26 weeks regardless of war intensity or economic situation.

**Limitation:** Can't react quickly to:
- Sudden front line changes
- Economic booms allowing more construction

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
- **WA_AI_PC_process_railway_queue**: Executes queued railway construction
- **WA_AI_PC_process_port_upgrades**: Builds naval bases for overseas operations
- **WA_AI_PATHFIND_PROV_***: A* pathfinding implementation

## Future Improvements (Ideas)

1. **Smart Starting Points**: Start from nearest existing high-level railway instead of always from capital
2. **Dynamic Intervals**: More frequent checks during active offensives
3. **Supply Hub Construction**: Build supply hubs in strategic locations
4. **Multi-Beachhead Support**: Handle multiple landing zones per continent
5. **Railway Repair Priority**: Detect and prioritize damaged railways
6. **Faction Coordination**: Consider ally railway networks
7. **Economic Scaling**: Adjust railway level targets based on available resources
