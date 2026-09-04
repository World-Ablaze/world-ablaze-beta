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
| `WA_AI_CONSTRUCTION_PRIORITY_corridor_data.txt` | ~60 | Fix 95: theatre-corridor node lists (pure data; North Africa today) |

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

Since 2026-08-16 every railway number is a HOI4 1.18 **script constant** in
`common/script_constants/wa_ai_railway.txt`, read as `constant:wa_ai_railway.<group>.<key>` from
`railway_core`, `railway_helpers`, `railway_strategies` **and** `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`
(the on_weekly eligibility filter `WA_AI_PC_country_can_build_own_logistics` and the per-enemy route
budget in `WA_AI_PC_railway_land_frontline_candidate`). One declaration, no per-file `@` copies to keep
in sync (see skill `wa-constants-registry`; the file carries a `# was @OLD_NAME` line per key). The
type id and the priority bands are PC-wide: `constant:wa_ai_pc.type_id.rail` (13),
`constant:wa_ai_pc.prio.rail_war` (1000, Fix 41 compressed 9999 -> 1000; x1.1 high-route multiplier
on top) and `constant:wa_ai_pc.prio.rail_prewar` (500, was 5000) in `wa_ai_pc.txt`.

```
wa_ai_railway.interval.peace_weeks = 12      # runs every 12 weeks during peace
wa_ai_railway.interval.war_weeks   = 8       # every 8 weeks during war
wa_ai_railway.eligibility.min_civs = 50      # base civ minimum inside the run, peacetime side
wa_ai_railway.eligibility.min_civs_war = 30  # Fix 104: absolute wartime floor, was min_civs x war_civs_factor (0.6)
                                             # computed at each site. A scripted TRIGGER cannot multiply, and
                                             # WA_AI_PC_country_can_fund_own_logistics must read this same floor.
wa_ai_railway.corridor.interval_weeks = 4    # Fix 95: theatre-corridor pass cadence (own counter)
wa_ai_railway.corridor.rail_level_floor = 2  # Fix 107: floor/cap pair around a COMPUTED target, not a flat level
wa_ai_railway.corridor.rail_level_cap = 4    # ...the irreversibility budget (railways cannot be downgraded)
wa_ai_railway.corridor.queue_max = 8         # corridor projects in flight per builder per building type (tag 27, scoped)
wa_ai_railway.corridor.max_routes_per_run = 19  # = the whole node-pair list; NOT a window (validator completeness).
                                                # 20 nodes since Fix 113 (western arm Oran..Tunis) -> 19 pairs. RAISE WITH ANY NODE ADDED.
wa_ai_railway.eligibility.min_civs_peace = 75
wa_ai_railway.eligibility.min_states = 5
wa_ai_railway.eligibility.max_surrender = 0.3     # skip above (see escape hatch below)
wa_ai_railway.eligibility.recovery_min_states = 20 # hatch: run anyway if civs > 75 and states > 20
wa_ai_railway.eligibility.minor_civ_threshold = 50 # minors bypass the state gate above this
wa_ai_railway.routes.max_total = 8           # routes processed per execution
wa_ai_railway.routes.max_per_enemy = 4       # routes per enemy country
wa_ai_railway.routes.queue_full = 12         # skip recalculation at/above (Fix 29b: live type-13 only)
                                             # AND the Fix 77 admission cap - one key, was two @ names
wa_ai_railway.routes.partial_path_priority_factor = 0.7
wa_ai_railway.routes.theatre_separation_distance = 10
wa_ai_railway.supply.railway_base = 4        # throughput = base + per_level x level
wa_ai_railway.supply.railway_per_level = 8   # L1=12, L2=20, L3=28, L4=36, L5=44
wa_ai_railway.supply.port_per_level = 5      # port throughput = level x 5
wa_ai_railway.supply.port_max_useful_level = 9
wa_ai_railway.supply.home_port_search_distance = 5
wa_ai_railway.supply.home_port_target_supply = 44
wa_ai_railway.cost.naval_base_per_level = -556  # naval_base.per_level_extra_cost (registered mirror of 00_buildings)
wa_ai_railway.cost.railway_segments_per_state = 3
wa_ai_pc.cost.railway = 800                  # rail_way.base_cost - PC-wide shadow price, read by scoring AND charging
wa_ai_pc.cost.naval_base = 10000             # naval_base.base_cost - idem
```

**Scoring and charging read the same declaration.** `WA_AI_PC_score_port_candidate` /
`WA_AI_PC_estimate_railway_cost` price candidate routes and ports with `constant:wa_ai_pc.cost.railway`
/ `.naval_base` (plus the per-level taper above), and `WA_AI_PC_get_building_cost`
(`..._PRIORITY_core.txt`) charges the same keys. **Fix 73 (2026-08-14) made the two tables agree**
(before that, charging used vanilla's `rail_way` numbers `170 + 130 × level` while scoring used this
mod's flat 800, so the system chose routes at one price and paid for them at another); the
2026-08-16 script-constant migration made them one declaration, so they cannot disagree again.
Charged prices today:

| Project type | Charged | Source |
|---|---|---|
| 13 railway | **800 flat per province connection**, one connection per project | `rail_way` `base_cost = 800`, `per_level_extra_cost = 0` |
| 14 naval base | **10000 flat** | `naval_base` `base_cost = 10000`; the real `per_level_extra_cost = -556` taper is modelled in scoring only, not in charging |

If `common/buildings/00_buildings.txt` is re-priced, **both** tables must be updated — `python tools/check_constants.py` (groups `cost_*`) reports the mismatch.

### Strategy / helper / trigger files

They declare no constants of their own any more; they read the script constants above.

## Eligibility Filters

The railway system runs inside `on_weekly` (`WA_AI_misc_on_actions.txt`). Since **Fix 75** the filter
block is the scripted trigger **`WA_AI_PC_country_can_build_own_logistics`**
(`common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`) rather than an inline `limit` — terms and
thresholds unchanged. **Fix 104 split it from the ally leg.** That trigger is an *authority* test: at
war it asks only for `> 5` controlled states and a surrender bar, with no civ-factory term, because the
run applies its own industrial floor one level down. Fix 74's ally leg needed a different question —
*can this country pay?* — and is now gated on `WA_AI_PC_country_cannot_fund_own_logistics`
(authority **and** `num_of_civilian_factories > min_civs_war` at war / `> min_civs_peace` at peace).
The two were one trigger from Fix 74 to Fix 103, which is why a belligerent under the wartime floor
read *capable* and locked every ally out of ground it could not develop itself. Before
`WA_AI_PC_railway` is called:

| Condition | Peace | War |
|-----------|-------|-----|
| Civilian factories | >= 75 (`@MIN_CIVS_PEACE`) | Always eligible |
| Country status | Must be major, OR at war, OR have 50+ civs | Always eligible |
| Controlled states | >= 5 | >= 5 |
| Surrender progress | < 30%, OR (civs > 75 AND states > 20) | same |
| AI only | Yes | Yes |

During war, the civilian factory threshold inside `WA_AI_PC_railway` itself is 50 * 0.6 = 30 civs.

**Capitulation is not a filter (Fix 75).** `has_capitulated = no` used to appear at *three* levels —
the weekly PC block gate, this eligibility filter, and again inside `WA_AI_PC_railway` — and all three
are gone. A capitulated country keeps its territory, its faction and its factories; whether rail is
worth building there is decided by the capability terms above. See "Capitulated countries" below.

Notes on the surrender gate: `surrender_progress` measures VP loss, not capability - the escape
hatch (`constant:wa_ai_railway.eligibility.recovery_min_states`) keeps a large power with an intact war economy
building rail even past 30% (the 1942-45 SOV case). While a country is ineligible, the interval
counter keeps ticking down in the on_action's `else` branch, so a recovering country fires on its
first eligible week instead of waiting out a frozen interval.

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
- **At war**: Counter resets to `constant:wa_ai_railway.interval.war_weeks` (8 weeks, ~2 months)
- **At peace**: Counter resets to `constant:wa_ai_railway.interval.peace_weeks` (12 weeks, ~3 months)
- Counter decrements by 1 each weekly call
- Execution occurs when counter reaches 0

## Three Strategies

### 1. Land War Strategy (`railway_strategies.txt`, lines 18-228)

**Trigger:** Country is at war with an enemy that shares a land border.

**Behavior:**
- Uses `WA_AI_PC_railway_get_relevant_enemies` to pre-filter enemies (majors, 50+ factories, or direct border)
- For each relevant enemy ROOT directly borders (via `WA_AI_PC_railway_country_borders_enemy`), it walks
  **three candidate populations in order** (Fix 74), each filtered by
  `WA_AI_PC_railway_land_frontline_candidate` and then handed to the single shared body
  `WA_AI_PC_railway_land_consider_frontline`:
  1. ROOT's own controlled states
  2. ROOT's subjects' controlled states (Fix 27)
  3. **faction allies that cannot build their own logistics** (Fix 74) — see "Coalition logistics" below
  The order is load-bearing: the per-enemy route budget (`constant:wa_ai_railway.routes.max_per_enemy`)
  is consumed top-down, so ROOT's own soil always outranks a subject's and a subject's an ally's.
- The shared body then:
  - Skips single-node states (detected via `WA_AI_PC_coastal_state_is_single_node`)
  - Requires the supply-hub **province** to be held by ROOT or by the state's controller (province
    control diverges from state control on contested fronts)
  - Handles cross-landmass targets via overseas supply chain analysis (per target since Fix 26)
  - Queues port upgrades for bottlenecked overseas routes
- Pathfinds (type 2 = ROOT + allied + subject provinces, allows partial paths)
- Sorts all targets by enemy threat (factories + divisions*5) via `WA_AI_PC_railway_score_and_sort_by_enemy_threat`
- Default route level: 5, priority: 1000 (`constant:wa_ai_pc.prio.rail_war`; Fix 41 band compression)

**Fix 74 scope correction — Fix 27 had never run.** The subject loop used to sit inside
`for_each_scope_loop = { array = _relevant_enemies_ }` *without* a `ROOT = {}` wrapper, so
`every_subject_country` iterated the **enemy's** puppets. Its own acceptance test
(`controller = { is_subject_of = ROOT }`) can never pass there, and ROOT does not control those
hub provinces, so the loop produced nothing from the day it was written. It is now explicitly
`ROOT = { every_subject_country = { … } }`. Expect subject frontlines (UKE Egypt, ITL Libya,
RAJ Burma) to start receiving routes for the first time.

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
- Pathfinding validation (type 2, ROOT + allied + subject provinces)

**Overseas Target Handling:**
- Only if ROOT has coastal access (prevents landlocked nations like Hungary from running overseas logic)
- Upgrades home port infrastructure via overseas supply chain analysis (cached per landmass)

**Route priority:** 500 (`constant:wa_ai_pc.prio.rail_prewar`; Fix 41 band compression)

## Coalition logistics — building on an ally's soil (Fix 74)

The PC **executor** has always accepted allied ground: `WA_AI_PC_start_project` passes on
`CONTROLLER = { is_in_faction_with = ROOT }`, the Fix 34 controller test in
`WA_AI_PC_assign_factories` and the completion path do the same, `supply_node` / `rail_way` /
`naval_base` are all `allied_build = yes`, and provincial pathfinder type 2 walks allied provinces.
Only the **selectors** were ROOT-or-subject gated, so a corridor that ended up on an ally's soil had
no builder at all. `_project_build_for_ally = 1` has been set in `railway_core.txt` since the
original design and read nowhere — Fix 74 is that intent, implemented.

Four triggers in `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` carry the policy:

| Trigger | Scope | Answers |
|---|---|---|
| `WA_AI_PC_country_can_build_own_logistics` | country | **AUTHORITY.** May this country run the railway system at all? At war: `> 5` controlled states and the surrender bar — **no civ-factory term**, because the run applies its own industrial floor one level down. This is the `on_weekly` entry gate and nothing else. |
| `WA_AI_PC_country_can_fund_own_logistics` / `_cannot_fund_own_logistics` | country | **FUNDING (Fix 104).** The authority test **and** the floor the run actually applies: `num_of_civilian_factories > min_civs_war` at war, `> min_civs_peace` at peace. Fails on the authority terms too, so a surrender-pinned or tiny ally also reads "cannot fund" — the name is the dominant term, not the only one. |
| `WA_AI_PC_can_build_logistics_here` | state, ROOT = builder | May ROOT queue logistics on this state? (ROOT-controlled, subject-controlled, or controlled by an ally that **cannot fund**) |
| `WA_AI_PC_is_logistics_build_partner` | country, ROOT = builder | Country-scoped twin, for selectors that iterate `every_country → every_controlled_state`. Also what Fix 103's `WA_AI_PC_corridor_node_is_my_charge` reads |

`WA_AI_PC_country_cannot_build_own_logistics` — the authority complement, and the ally leg's gate from
Fix 74 to Fix 103 — was **deleted by Fix 104** once all three readers moved to the funding complement.
The "capitulated" half of its old description had already been removed by Fix 75.

**The ally leg is deliberately not "any faction member."** It fires only where the controller cannot
run the railway system for itself. That is exactly the population the gap was about — a capitulated
ally keeps its territory and faction membership but the whole weekly PC block is gated
`has_capitulated = no`, so its queue simply fossilises — and it keeps two healthy majors out of each
other's rail networks. **The eligibility terms in that trigger read the same script constants
(`constant:wa_ai_railway.eligibility.*`) as `railway_core.txt`** — since 2026-08-16 there is one
declaration (`common/script_constants/wa_ai_railway.txt`), not three copies to change together.

Sites made ally-aware: the land-war candidate walk (above), all three overseas Part-B scans
(beachhead candidate, beachhead validation, frontline targets), both port searches
(`WA_AI_PC_get_best_port_on_landmass`, `WA_AI_PC_get_best_port_near_state` — which also folds away
their duplicated Fix 28 subject loops), `WA_AI_PC_process_port_upgrades` and
`WA_AI_PC_create_frontier_port`.

The port searches matter as much as the target selector: without them a route *to* ally soil still
starts from ROOT's own nearest port, so an ENG route to FRA-held Tunisia would begin at Alexandria
and have to pathfind across Italian Libya while Bizerte (naval base 5) sits at the target.

**Evidence** (campaign `f9321934`, 1944.3): the Maghreb — Tunisia 458, Algiers 459, Constantine 460,
Casablanca 461, Marrakech 462 — is FRA-controlled; Egypt 446/447 is ENG. Egypt runs rail 5 on
provinces 3996/4055/10031 while Tunisia sits at 1–2 with supply hubs at 11921/11969. ENG and USA held
**zero** railway projects for the entire campaign, their interval counters advancing on schedule (the
pass fires and finds nothing). FRA, capitulated, held 14 fossil projects byte-identical for 12 months,
every one aimed at German-held metropolitan France. Same root cause as the Free-French Normandy
beachhead on campaign `31eaf7e6`.

## Theatre corridors — named-node logistics (Fix 95)

**Why.** The three strategies above derive every route from the capital, the ports and the
supply-hub discovery, so a theatre whose logistics are *known in advance* — the North African
coast, one province deep, Tripoli to Alexandria with nothing but sand between the hubs — was never
railed by anyone: on campaign `66636ff4` Tripoli and Benghazi were still Axis in October 1943 and
neither side had laid a metre of track between Tripoli (1149) and Marsa Matruh (11967). A corridor
is the answer: an **ordered list of named province nodes** with a per-node "wants a depot" / "wants a
port" attribute, and one engine that builds whatever consecutive pair the builder holds.

**Fix 113 (2026-08-20) — the western arm.** The North African list used to begin at **Tunis** and run
east to Alexandria, which is the *defender's* corridor: an invader landing in Morocco or Algeria walked
east on a chain that started beyond its own front. Campaign `3d68a183` measured the consequence at
1944.4 — east of Tunis the corridor had done its job (Tunis→Gabès 1 → 3, Gabès→Tripoli BREAK → 4,
`wa_tlm_r107_sizing_rail_tgt = 4`) while Oran–Algiers–Constantine–Bône–Bizerte–Tunis sat at its **1936
level 2** (20 supply) for ten years, with the Allied front asking 41 at Constantine. Five nodes were
prepended — Oran 7132, Algiers 1145, Constantine 9976, Bône 7081, Bizerte 9994 — taking the list to
**20 nodes / 19 pairs**. All five already carry a supply node, so no depot is wanted on the arm; the
four coastal ones are marked `port_ = 1` because **Bône is level 1 (5 supply)** and binds the whole
injection. Constantine is inland and is there as a forced junction: without it the pathfinder can route
the arm south through the level-1 Batna branch (`map/railways.txt:1152`).

`corridor.max_routes_per_run` went 14 → 19 **in the same change**. It is not a throughput knob: the
pass validates every corridor project against the routes it pathfound *this pass*, so a cap below the
pair count cancels the paid-for progress of the routes it skipped, every pass, for ever.

### [levant-iraq] (2026-09-01) — more than one corridor, and the Jordan approach to Iraq

**The family is now N corridors.** `WA_AI_PC_railway_corridor_pass` is the interval gate, the
industrial floor and the **call list**; one corridor's work is `WA_AI_PC_railway_corridor_run_one`,
called once per corridor id with `_corridor_id_` (which define and which theatre gate) and
`_corridor_type_id_` (that corridor's PC tag) set by the dispatcher and zeroed after the last call.

**One PC `type_id` per corridor is load-bearing, not bookkeeping.** `run_one` ends with a stale-path
validation that cancels *every queued project carrying its `_strategy_id`* whose target province is
not on the routes it just pathfound — except one paid past
`constant:wa_ai_pc.alloc.stale_keep_paid_fraction` (`[rail-admission-churn]`), which is kept and
holds its slot until completion. Two corridors under one tag would therefore cancel each other's
in-flight segments on every pass — the same failure the `max_routes_per_run` note above describes,
one level up. The per-tag `queue_max` follows from the same split, so the corridors do not compete
for one budget either. **A third corridor takes a third id and a third `type_id`** (`wa_ai_pc.txt`,
`savegame.py` `_PC_TYPE_ID`, `tools/constants_registry.json`).

**Corridor 2 — `levant_iraq`, Ma'an 7151 → Amman 4017 → Ruwaished 4440.** Owner order: while the
holder of Jordan is at war with the Iraqi power, put a depot on the last friendly province before
the Iraqi border and connect it to the rail the Levant already has; stop when that power
capitulates. Map facts (2026-09-01): 7151 and 4017 both carry a supply node and are railed to each
other at level 1 via 10089; 4440 is land/arid with **no** supply node and **no** railway, its only
Jordanian neighbour is 1544, and its neighbours 13831/13832 are state 675 (Iraq). **Every node and
every intermediate province the pathfinder can pick is in state 455**, so all segments are
admission-scoped to one state and the pathfinder/admission mismatch that forced junction 13481 into
the North African list cannot arise here.

Two things this corridor does *not* have, both deliberate: **no node inside Iraq** (the owner asked
for a depot fed from the Levant, not for rail laid into Iraq) and **no port** (it is inland).

**Gate** — `WA_AI_PC_corridor_theatre_live_levant_iraq`: the **OWNER of state 291 (Baghdad)** is at
war with ROOT and has not capitulated. Ownership rather than control, so occupying Baghdad does not
close the gate before the war is decided; it closes on capitulation, on annexation (the owner
becomes the annexer, who is not at war with itself) and on a white peace. Tag-free: any holder of
Jordan fighting any holder of Baghdad gets the same corridor.

**Band.** This corridor's node list is entirely behind our own lines, so `_corridor_hostile_n_` is 0
and the enemy-held-node rule would price a wartime measure as peacetime preparation. The define
declares `_corridor_war_band_ = 1` and the band rule gained an OR term; North Africa declares 0 and
its band is decided exactly as before.

**Telemetry.** The r103 `reach`/`orphan` and the five r107 `sizing_*` names are **GAUGES** — sampled
state, last writer wins — and every documented reading of them is a North Africa reading, so they
are pinned to corridor 1. The `r95_corridor_*` counters and `r107_port_raise_n` are per-project and
stay unguarded: "the corridor pass admitted N projects" is still true when the corridors sum into
them. A corridor that needs its own gauge takes its own metric names (WA_TLM doc §7).

**Files.**

| Layer | File | What |
|---|---|---|
| data | `WA_AI_CONSTRUCTION_PRIORITY_corridor_data.txt` | `WA_AI_PC_CORRIDOR_define_north_africa` and `WA_AI_PC_CORRIDOR_define_levant_iraq` fill `corridor_node_prov_` / `_depot_` / `_port_` / `_fwdport_` and declare `_corridor_war_band_`. Pure data. A second theatre = a second define. |
| strategy | `railway_strategies.txt` `WA_AI_PC_railway_STRATEGY_theatre_corridor` | classifies every node (ours / enemy-held), applies the theatre gate, publishes routes (`corridor_route_*`) and hubs (`corridor_hub_*`) for this pass |
| core | `railway_core.txt` `WA_AI_PC_railway_corridor_pass` | interval counter, civ floor, and the per-corridor call list (`_corridor_id_` / `_corridor_type_id_`) |
| core | `railway_core.txt` `WA_AI_PC_railway_corridor_run_one` | ONE corridor: pathfinding (type 2, **no partial**), segment admission through `WA_AI_PC_start_railway_project` with `_railway_family_ = 1`, hubs through `WA_AI_PC_corridor_start_hub`, stale-path validation pinned to **this corridor's** `type_id`, `WA_TLM_r95_corridor_*` |
| helpers | `railway_helpers.txt` `WA_AI_PC_corridor_start_hub` | queues a supply hub (PC type 17, new in Fix 95 part 1) or a naval base (14) at a named province, idempotent on the building's existence |
| triggers | `WA_AI_CONSTRUCTION_triggers.txt` `WA_AI_PC_corridor_node_is_ours` (→ `WA_AI_PC_is_corridor_side_holder`) / `_is_my_charge` (→ `WA_AI_PC_is_logistics_build_partner`) / `_is_hostile` / `WA_AI_PC_corridor_theatre_live_north_africa` / `WA_AI_PC_corridor_theatre_live_levant_iraq` | province-level control tests over `any_country`; permission vs payment split (Fix 103); NA theatre gate = AIR contested trigger OR no enemy on any node (preparation); Levant gate = the owner of Baghdad is at war with ROOT and standing. **One gate per corridor, dispatched as `OR = { AND = {id, gate} … }` — never as `if = { limit = { id = N } gate }`, which is vacuously TRUE for every other id** |
| admission | `WA_AI_CONSTRUCTION_triggers.txt` `WA_AI_PC_state_controller_allows_admission` | the three-term controller gate `WA_AI_PC_start_project` applies, extracted verbatim by Fix 103 so the corridor selector and the `blocked_n` probe agree with it by construction instead of by comment. **`selector ⊆ admission ⊆ validity`** — the lane / air-lane / fill / completion tests at `PRIORITY_core.txt` `:494`, `:627`, `:743`, `:1069` deliberately carry a fourth term `ROOT = { is_subject_of = PREV }` and must not be folded into this trigger |
| constants | `wa_ai_railway.txt` `corridor.*` (`interval_weeks` 4, `rail_level_floor` 2 / `rail_level_cap` 4 (Fix 107), `queue_max` 8 per building type **per corridor tag**, `max_routes_per_run` = the whole pair list **of the largest corridor**, applied per corridor, so the validator's cancel set is always complete); `wa_ai_pc.txt` `type_id.corridor` 27 (north_africa) and `type_id.corridor_levant` 28, `cost.supply_node` | |

**Rules the engine applies — no tag, no date, no side (the corridor is symmetric):**

- **Permission and payment are two questions (Fix 103).** Both are tested per **province** — state
  control is never consulted (Cyrenaica 663 was ITL-controlled with ENG provinces inside).
  - *ours* / **permission** — `WA_AI_PC_corridor_node_is_ours` → `WA_AI_PC_is_corridor_side_holder`:
    the province is controlled by ROOT, a subject of ROOT, or **any** faction ally. These are the
    same three terms, in the same order, as the PC **admission** gate
    `WA_AI_PC_state_controller_allows_admission` that `WA_AI_PC_start_project` applies — a selector
    wider than admission requests hops the executor refuses in silence, a narrower one refuses hops
    the executor would have taken.
  - *my charge* / **payment** — `WA_AI_PC_corridor_node_is_my_charge` →
    `WA_AI_PC_is_logistics_build_partner`: ROOT, a subject, or a faction ally that
    `cannot_fund_own_logistics` (so ENG/USA build in Free-French Tunisia and stop the day FRA can pay
    for itself). **Fix 104 changed that last term** — it was `cannot_build_own_logistics`, the
    authority test, which has no civ-factory term at war.
  - Before Fix 103 a single test did both jobs, and a hop between a healthy ally's node and our own
    had no builder anywhere: on campaign `7c7803a8` **Medenine 11957 ↔ Tripoli 1149** went unbuilt
    across all 123 monthly saves — GER held Medenine, ITL held Tripoli, ITL is a faction ally of GER
    that passes `can_build_own_logistics` on `min_states`, and ITL's ~1 civ factory can never clear
    the corridor's own civ floor. Both hubs sat at the *unconnected* `NODE_INITIAL_SUPPLY_FLOW`
    baseline of 5 (Gabès 28/5, Medenine 26/5) against Marsa Matruh's 39/20 = `4 + 8×2`.
- The rail between two consecutive nodes is requested when **both ends are ours and at least one is
  our charge** (Fix 103; before, both ends had to be our charge). This is what keeps Fix 74's
  recorded purpose — "keeps two healthy allies out of each other's rail networks" — literally true:
  a healthy ally's *interior* hops, both ends its own, still have no payer but itself, so no partner
  touches them; only a hop we already have a foot on crosses the line. It also bounds the duplicate
  spend to hops that **straddle** two partners' ground, and keeps an out-of-theatre faction member
  out (JAP passes the North Africa theatre gate the moment ENG holds Egypt, but has permission on
  ally nodes and charge on none). **Hubs use the charge test alone**, so hub behaviour is unchanged
  by Fix 103. The pass gate is the charge count, which is the same predicate the pre-Fix-103 gate
  used — **the set of countries that enter the corridor pass is unchanged**.
- **That residual is closed by Fix 104.** Fix 103 recorded it and built the detector: `can_build_own_logistics`
  is a *size* test (`min_states` 5), not a funding test, so ITL — 8 states, ~1 civ factory — read capable
  while being unable to build for itself, and a hop whose ends were all held by such "capable but
  unfundable" allies had permission from someone and payment from nobody. Fix 104 gave the charge test
  its own predicate, `WA_AI_PC_country_cannot_fund_own_logistics` (authority **and** the run's own civ
  floor), so `WA_AI_PC_is_logistics_build_partner` — which `WA_AI_PC_corridor_node_is_my_charge` reads —
  now names a payer for those hops. `WA_TLM_r103_corridor_orphan` stays as the detector and is now the
  *regression* test: it should fall as `WA_TLM_r104_ally_fund_n` rises. Sustained `orphan > 0` with
  `ally_fund_n = 0` means the split did not take.
  - Measured case that motivated it (campaign `7c7803a8`): FRA held 46 controlled states with 10–19 civ
    factories from 1940 to 1944, its PC available-factory share read 0 % for 15 consecutive quarters, and
    ENG (198 civs) and USA (455) — both fighting in that theatre — were forbidden from building rail on
    French-held Algeria for the whole war.
- The pathfinder
  runs without partial paths, so a hostile province in between simply postpones the hop — no
  frontier port is conjured in the desert. Sequencing therefore *emerges from control*:
  Mechili↔Tobruk is never asked before Mechili is held, Mechili↔Benghazi never before Benghazi.
- **Forward port (attacker only).** A node flagged `corridor_node_fwdport_` (Ajdabiya 1127) gets a
  naval base only when the holder is the *attacker*: the node is ours, its province is **owned by an
  enemy** (`WA_AI_PC_corridor_node_is_conquered` — we stand on conquered soil), one neighbouring node
  is enemy-held (the front: blocked at El Agheila 4057) and the other is ours (the rear: Benghazi
  already fell). Ruling 2026-08-16: the defender on its own soil never builds it — a supply port
  behind a static line is wasted civs. Symmetric by construction: the Axis holding a UKE-owned
  Egyptian node flagged the same way would qualify.
- Priority band: `rail_war` (1000) when any node of the corridor is enemy-held, `rail_prewar` (500)
  otherwise — the owner of Libya / Egypt / Tunisia prepares its corridor in peace. Keyed on the
  nodes, not on `has_war`, because ITA is at war in 1936 (Ethiopia).
- Own budget: every corridor project (rail 13, port 14, depot 17) carries `type_id` 27 and is
  admitted under `_project_queue_max_scoped = 1` against `corridor.queue_max`; the land-war family's
  `routes.queue_full` skip gate and admission cap are keyed on `type_id = rail` since Fix 95, so the
  two families never count each other. (Every rail project queued before Fix 95 already carried
  `type_id` 13, so nothing changes for a resumed save.)
- Own cadence: `corridor.interval_weeks` (4) instead of the main pass's 8/12. One type-13 project is
  one level on one hop and the province-duplicate guard admits one project per province per pass, so
  the pass cadence — not the civ pool — bounds how fast a corridor grows: a 20-hop route reaches
  level 1 in ~3 passes = 12 weeks (24 at the main cadence), level 2 in ~5.
- Stale-path validation is run only against the corridor tag and skipped when routes were requested
  and *every* pathfind failed (a transient hole must not cancel paid-for progress); off-path projects
  paid past `alloc.stale_keep_paid_fraction` are kept (`WA_TLM_pc_stale_kept_n`). Peace purges the
  corridor's rails with every other type-13 (Fix 5/19 sweep) and resets its counter; queued depots
  survive peace by design.

**Cadence table (t0/t1/t2, war, `queue_max` 8, one +1 level per hop per pass):**

| Route | Hops | Level 1 | Level 2 |
|---|---|---|---|
| Tobruk ↔ 5078 | ~4 | 4 wk | 8 wk |
| Tunis → Gabès (exists L1) | ~7 | — | 4 wk |
| Gabès → Medenine (+ port ~1 month) | 1 | 4 wk | 8 wk |
| Tripoli → Benghazi | ~20 | 12 wk | 20 wk |
| Benghazi → Tobruk via Mechili | ~10 | 8 wk | 12 wk |

**Duplicate spend when several partners can pay for the same hop** (ENG + USA on FRA's Tunisia; after
Fix 103, also the partners either side of a straddling hop). The claim previously recorded here — "both
may add +1 **in the same pass**, bounded at `rail_level + 1`" — was **wrong**, and was corrected in Fix
103 after both reviewers rejected it. Two facts make the window far wider than one pass:
`_queued_for_segment` (`railway_helpers.txt:926-938`) scans `ROOT = { for_each_loop = { array =
WA_AI_PC_queue ... } }` — **ROOT's own queue only** — and `global.WA_AI_PC_railway_connection_level_a^b`
moves only **at completion**. So a second builder running its pass four weeks later still reads
`current_level` as unbuilt and queues the hop again.

Segment cost is `constant:wa_ai_pc.cost.railway` = 800 and `_daily_progress = construction_speed_ ×
assigned_factories` with base speed 1 (`PRIORITY_core.txt:69`), so a segment takes `800 / F` days:

| F (assigned civs) | 20 (alloc clamp) | 10 | 5 | 1 |
|---|---|---|---|---|
| Build time | 5.7 wk | 11.4 wk | 22.9 wk | 114 wk |

Against a 4-week pass and a ~4.35-week monthly save, for N qualifying builders on one hop:

| t | Event | global level |
|---|---|---|
| t0 | builder A queues the hop | 1 |
| t0 + 4 wk | each other builder's pass: own-queue dedup is ROOT-scoped and blind to A, global still unbuilt → **each queues its own duplicate** | 1 |
| t0 + 8 wk | every builder's dedup now sees *its own* project → effective level = target → **no further adds; duplication does not accumulate** | 1 |
| + build (5.7–114 wk) | first completion | 2 |
| + build | remaining completions | **2 + (N−1)** |

**Accepted cost, stated:** `N−1` extra 800-cost segments per contested hop and a final level of
`rail_level + (N−1)`, held for one full build duration. Hard ceiling regardless: `corridor.queue_max`
= 8 concurrent corridor projects per builder per building type. Fix 103's "≥ 1 end is my charge" rule
is what keeps N small — it confines contention to hops that straddle two partners' ground (**S = 1**
on campaign `7c7803a8`: Medenine ↔ Tripoli) instead of every hop on a shared host. Note ITL itself
satisfies both predicates on the Libyan hops and is excluded only by the corridor's civ floor, i.e.
by data rather than by rule — so N is a property of the campaign, not a constant.

A cross-builder claim (a global per-segment builder tag with a TTL) was considered and rejected: with
N small it buys little, and it introduces persistent cross-country state whose expiry is a new failure
mode of its own.

**Not solved here:** the corridor gives the ground campaign its logistics; it does not put divisions
in Africa (`66636ff4`: 92/117 ENG divisions under garrison orders, offensive `plan_value = -1`).

**Sizing (Fix 107, 2026-08-18).** The rail target is **computed**, not flat. Every hop used to be asked
for `constant:wa_ai_railway.corridor.rail_level = 2`; campaign `9d83084c` then measured every corridor
hop at exactly 2 on all 121 monthly saves, 1940.12 to 1946.2 - the pass was not blocked and not late, it
had **finished**, and `4 + 8x2` = 20 supply was the ceiling by construction. `WA_AI_PC_corridor_compute_sizing`
(`railway_helpers`) now totals our side's divisions on the corridor states into a presence index, turns it
into a demand in supply points, caps it by what our corridor ports can inject (the chain is in **series**),
and converts that to a level clamped between `corridor.rail_level_floor` (2 - so the change can never
regress a peacetime corridor) and `corridor.rail_level_cap` (4 = 36 supply - the irreversibility budget,
since railways cannot be downgraded). A port node is now **raised** toward a computed level instead of only
being placed when missing - the defect that left Medenine/Gabes at level 1 for 121 saves under three
successive holders, because FRA placed it in 1936.4 and the existence test refused every later request for
ever. Which lever moves is a cost arbitration on the pathfound chain length N: port = 2000 per supply
point (PC charges `cost.naval_base` flat), rail = 100 x N, so at or above `port_break_even_segments` = 20
the port wins and below it the rail does. **Read `documentation/WA_AI_LOGISTICS_MODEL.md` §11 and §11.11
before touching any of it** - §11.11 is the authority on the three places the code deviates from the
frozen design. The presence index is **not** a division count; its header says why and what it biases.

**Connect before consolidate (Fix 120, 2026-08-21).** The corridor emits **one priority for all its
hops** — `_corridor_prio_` in `railway_strategies.txt`, `rail_war` 1000 or `rail_prewar` 500 — and
`WA_AI_PC_assign_factories` sorts by priority **alone**, so at a tie the bubble sort serves insertion
order. A hop that has no railway at all therefore competes on equal terms with a hop being raised from
4 to 5, and with every land-war segment in Europe.

MEASURED on campaign `8c0fea4c`, and it is the corridor's own behaviour, not a starved budget: at
1941.12 the eight rear hops Tripoli→Tobruk all read level **5** — one *above* `rail_level_cap` = 4 —
while **Tobruk 1130 → 5078 had been BREAK since 1940.6**, 21 months, of which 15 with both ends held by
the Axis (5078 was ITL from 1940.12, GER from 1941.6; 1130 ITL throughout). At the project level, the
1941.6 save shows the mechanism exactly: ITA's **single funded railway factory** sat on `4120 → 13509`,
an edge already at map level 5, while `1130→10120`, `10120→7079` and `7079→5078` — all at map level
**0** — held 0 factories with 4 weeks of stall, at the identical priority 1000, queued *behind* 13
European land-war segments also at 1000. The dépôt the user reported as unconnected is a consequence of
that ordering, not a separate rule: hubs are emitted at the same `_corridor_prio_` as the rails, so
once missing links outrank everything the hubs fall in behind them with no further change.

The fix is one branch in `WA_AI_PC_start_railway_project` (`railway_helpers.txt`), which **already
computes `current_level`** from `global.WA_AI_PC_railway_connection_level_[x]^[y]` two lines earlier
and only ever used it for an equality test. The raw map level is captured *before* `_queued_for_segment`
is folded in — the question is "does a railway exist here", not "has someone asked for one" — and a
corridor segment reading 0 takes `constant:wa_ai_pc.prio.rail_connect` = **1100**. That equals
`prio.legacy_max`, the ceiling this build already writes through the ×1.1 high-route multiplier
(`railway_helpers:543`), so **no band is added and no registry mirror moves** — `savegame.py _PC_BANDS`
already carries `(1100, "rail-war+")`, and the Fix 41 legacy clamp tests `> legacy_max`, so 1100 is not
clamped.

Scoped to the **corridor family** (`_rail_family_latched_ = 1`) by decision: land_war derives its routes
dynamically and the same rule there re-orders every AI country's whole rail queue. Widening it is a
second step behind a campaign that validates this one.

**Part 2 — the retest, and why priority alone was not enough (2026-08-21).** The build carrying part 1
was run over 1940.6 → 1941.10 and the corridor behaved exactly as before: at 1941.5 **all eight queued
railway projects were UPGRADES priced 1000**, on edges already at map level 2–5, while Derna 7082 →
Tobruk 1130 and Tobruk 1130 → 5078 were **BREAK and absent from the queue entirely**, and the rear ran
at level 5 against `wa_tlm_r107_sizing_rail_tgt = 4`. Priority orders **funding**; the binding
constraint here is **admission**. The pass walks the node list west to east and admits until
`corridor.queue_max` (8 per building type) is full, so the rear claims the budget before the head is
ever offered — and a project that is never admitted never gets a price.

`WA_AI_PC_railway_corridor_pass` therefore runs **two phases over one set of pathfinds**:

| Phase | What it does |
|---|---|
| 0 | pathfind every route once; collect each segment's `(a, b, target, priority, state)` **and its raw map level** into parallel temp arrays. `_valid_provinces` and `_corridor_chain_len_` are filled here as before, so stale-path validation and the Fix 107 port arbitration are unchanged |
| A — CONNECT | admit **only** segments at map level 0, **target level 1**. The clamp matters: without it the same unrailed segment is re-requested every pass until it reaches the sizing target, so one hop can hold several connect-band projects while the next hop has none |
| B — RAISE | runs **only if phase A admitted nothing**: either the chain is whole, or every remaining hole was refused and is not ours to build |

**The refusal case is why phase B is gated on "admitted nothing" rather than on "no BREAK hop exists".**
A hop the controller gate refuses never counts as admitted, so a permanently blocked hole cannot freeze
the corridor at level 1 for ever. That is not hypothetical: `wa_tlm_r103_corridor_blocked_n` rose 4 → 5
→ 6 across the retest saves, and Gabès 11957 → Tripoli 1149 — across Vichy Tunisia — is BREAK on every
save of that campaign. A naive "no upgrades while any hop is BREAK" rule would have shipped a corridor
that never rises above level 1 as long as Tunisia stays neutral.

**The mismatch phase A cannot see, and the node that works around it (Fix 130, 2026-08-21).** The
pathfinder filters by **province** control (`WA_AI_PATHFIND_PROV_get_path` type 2); the executor admits
by **state** controller (`WA_AI_PC_state_controller_allows_admission`, scoped to
`global.WA_AI_MAP_province_state_id^<first province of the segment>`). On contested ground the two
disagree, and the pass can pathfind a route whose segments are then refused in silence.

MEASURED on Tobruk 1130 → 5078, saves `ITA_1941_05_23_21` / `_06_10` / `_10_06`: **every province of
both candidate routes is ITL-held**, but **state 452 Marsa Matruh is ENG-controlled** (province split
11/3, then 10/4; by 1941.10 state 960 is ENG-controlled too, 4/2).

| Route | Hops | Segments, and the state each is scoped to |
|---|---|---|
| coastal | 3 | 1130→10120 (451 ITL, admitted) · 10120→**7079 (452 ENG, REFUSED)** · 7079→5078 |
| inland | 3 | 1130→4136 (451 ITL) · 4136→13481 (451 ITL) · 13481→5078 (663 ITL) |

Both routes are **three hops**, so the pathfinder's tie-break decided; when it took the coast the last
segment was refused for ever and the rail ran east from Tobruk and stopped. `wa_tlm_r103_corridor_blocked_n`
counted it, 4 → 5 → 6. Fix 130 adds **province 13481 (state 663) as a forced junction node** between
Tobruk and 5078 — the same kind of node as Constantine 9976 in Fix 113 — which splits the hop into
1130→13481 (scoped to 451 throughout) and 13481→5078 (scoped to 663), so no segment is ever scoped to
an Egyptian state. Node count 20 → 21, `corridor.max_routes_per_run` 19 → **20** with it. Probe **R91**.

**That is a work-around, not the fix.** The next contested state reproduces it; aligning the two filters
on one shared predicate is a QUEUE row (0m). And when a node id comes in from a report, check it against
`WA_AI_MAP_state_provinces` first: the id proposed for this junction was **13841**, a digit transposition
of 13481, and 13841 is in **state 443 Sind, India**.

**What it does not do.** It creates no construction capacity — it re-targets capacity that was already
spent, and the proof that the capacity existed is the level-5 rear itself (eight hops one level above
the cap ≈ 6400 construction points, against 2400 for the three missing segments). The Fix 41 aging lane
is untouched and can still take almost the whole pool: on that same 1941.6 save it served **16 of ITA's
17 factories** to a 10-month-old priority-**100** infrastructure project, leaving one for the sorted
fill. That is the PC fairness subject, not this one. Probe: checklist **R81**.

**Verification:** checklist items R60, R71 and R81; `savegame.py pc <TAG> --match corridor` for the queue side,
`tlm <TAG> --match r95` for admissions, and the map (railway connection level between two nodes,
`supply_node` at 10049 / 9980, `naval_base` at 11957) for the built side.

## Route sizing — one model, two families (Fix 135, 2026-08-21)

**The number a railway route targets is now computed by one helper, `WA_AI_PC_rail_size_route`
(`railway_helpers.txt`), called by both the theatre-corridor pass and the land-war / overseas route
selector.** Before this it was computed twice: once properly, once not at all.

### Why it is one helper and not two conventions

The same defect was measured on the two families in turn.

| Campaign | Family | Reading |
| --- | --- | --- |
| `9d83084c` | corridor | every corridor hop at exactly **2** on all 121 saves. The pass was not blocked — it had finished, and `4 + 8×2 = 20` supply was the ceiling by construction while an Allied army group fought at the far end. Fixed by **Fix 107**, which is the body this helper now holds. |
| `8c0fea4c` | land-war | Libya at level **5** from Tripoli to Derna by 1941.5 (from 6 BREAK hops at level 0–1 in 1940.6), i.e. 44 supply per hop, behind an entry port — Tripoli, `naval_base 5` — carrying **25**. The port-derived target for that chain is **2**. |

The land-war number came from two lines with no reference to anything: `default_route_level = 5` in
`WA_AI_PC_railway_STRATEGY_land_war`, and in `WA_AI_PC_railway_land_consider_frontline` a **ratchet**,
`route_level = _max_route_level_ + 1` clamped at 5 — "one level above whatever this route already
has", which climbs to the clamp on its own, one pass at a time. Because
`WA_AI_PC_start_railway_project` only compares `current_level < _project_target_level`, that target
also **overwrote the corridor's own cap of 4 on the same segments**. Both lines are gone.

### The contract

`WA_AI_PC_rail_size_route` runs in COUNTRY scope and reads five temps:

| Input | Meaning |
| --- | --- |
| `_rsize_prov_` | array of province ids whose **states** carry the demand |
| `_rsize_ours_` | parallel array, `1` = this node's port counts as ours (SUM mode only) |
| `_rsize_entry_mode_` | `0` SUM · `1` GIVEN · `2` OVERLAND — see below |
| `_rsize_entry_supply_` | entry capacity in supply units (GIVEN only) |
| `_rsize_floor_` / `_rsize_cap_` | the clamp, from the **caller's own** constants |

and publishes `rsize_presence_`, `rsize_demand_`, `rsize_inject_` (`-1` = cap not applied),
`rsize_rail_tgt_`, `rsize_port_tgt_`.

**The three entry modes are the one thing that must not be unified.** Each is right in its own
topology and any single rule would be wrong in the other two:

| Mode | Topology | Entry capacity |
| --- | --- | --- |
| `0` SUM | a corridor, fed by every port along it | **sum** of the naval bases at our nodes (injections add — `WA_AI_LOGISTICS_MODEL.md` §7) |
| `1` GIVEN | an overseas chain, in **series** across a sea leg | the caller's **bottleneck** of home port and receiving port (`overseas_entry_supply_`, published by `WA_AI_PC_analyze_overseas_supply_chain`) |
| `2` OVERLAND | our own capital across our own network | **none** — `CAPITAL_SUPPLY_BASE` feeds it, so demand alone decides. Deliberately not the same as "a node set that happens to contain no port": a frontline state with a small harbour would otherwise cap an overland chain at that harbour. |

### Callers

| Caller | Node set | Mode | Floor / cap |
| --- | --- | --- | --- |
| `WA_AI_PC_corridor_compute_sizing` | the corridor's whole node list | SUM | `constant:wa_ai_railway.corridor.rail_level_*` |
| `WA_AI_PC_railway_land_size_this_route` (overland route) | the **one** frontline hub province | OVERLAND | `constant:wa_ai_railway.land_war.rail_level_*` |
| `WA_AI_PC_railway_land_size_this_route` (overseas route, and the Fix 28 fallback) | the same one province | GIVEN | same |
| `WA_AI_PC_railway_STRATEGY_overseas_war` part B | beachhead port + frontline hub | SUM | same |

**Why the land-war caller passes ONE province while the corridor passes twenty.** The presence walk
inside the helper is `every_country` × states. The corridor sizes **once per pass**; the land-war
selector sizes **once per route**, up to `routes.max_total` (8) times per execution, per country. One
state keeps that affordable, and it is also the right demand: a chain exists to feed the army at its
head.

**Why the two families keep separate floor/cap constants.** `corridor.rail_level_*` and
`land_war.rail_level_*` are both `2 / 4` today, by choice and not by contract — nothing checks it. A
corridor is a named theatre spine WA commits to; a land-war route is any frontline the allocator
happens to reach. They should be retunable apart.

### What was NOT changed, and why

- **The pre-war family keeps its ratchet.** In peace there is no army on the target to measure, so the
  demand proxy would read a garrison and pin every prewar route at the floor — a regression, not a
  measurement. What Fix 135 changed there is the ceiling: `default_route_level` reads
  `land_war.rail_level_cap`, so the ratchet stops at 4.
- **`STRATEGY_overseas_war` part A (the home-port chain) keeps its flat 5.** Its target is
  `constant:wa_ai_railway.supply.home_port_target_supply` (44 = level 5) by design, and it is fed
  overland from the capital rather than by a port.
- **`_check_railway_level` reads the cap** — `land_war.rail_level_cap` in the overseas-war and prewar
  strategies, `land_war.rail_level_cap_overland` (5, `[rail-admission-churn]`) in the land-war strategy,
  whose sizer caps a capital-fed route at 5 and a port-fed one at 4; a different-landmass frontline
  already at 4 is dropped inside `WA_AI_PC_railway_land_consider_frontline` (route_start zeroed), and
  so is a same-landmass frontline reached only by the overseas fallback (`_direct_success` zeroed),
  so neither draws a route. Left above the sizer's cap, a frontline would stay for ever "not done" and keep
  drawing routes that queue nothing.

### What this cannot tell you

Actual supply is not readable from script — nothing in the mod reads it — so this **models** flow from
building levels and can never observe whether it was right. The demand proxy is not a division count
either (`divisions_in_state` is a comparison trigger; the ladder uses bucket midpoints and over-reads a
dispersed army). Both statements were already true of Fix 107; sharing the model does not make them
less true, it makes them true in one place. Consumers: checklist R96, and `WA_TLM r107` against a
campaign map reading.

## Capitulated countries (Fix 75)

Before Fix 75 the weekly PC block was gated `is_ai = yes` + `has_capitulated = no`, while
`WA_AI_priority_construction_strategies` fires from `WA_AI_background.1` gated only on `is_ai = yes`.
A capitulated country therefore kept **queueing** projects while never assigning factories to them or
progressing them — the queue was write-only, and froze at whatever it held the week the capital fell.
FRA on `f9321934` sat on 14 projects byte-identical across 12 months (`assigned_factories` and
`progress` stuck mid-value), 10 of them railways aimed at GER-held metropolitan France, while holding
49 controlled states — the whole Maghreb — and 21 idle civ factories.

The block gate is now `is_ai = yes` + `exists = yes`. Statement order is unchanged; the three calls
that genuinely need the capitulation test carry it individually:

| Call | Capitulation-gated after Fix 75? | Why |
|---|---|---|
| `WA_AI_update_training_modifier` | **Yes** | Trains divisions — not a fallen government's business |
| `WA_AI_PC_assign_factories` | No | Fix 34's controller test already refuses hostile-controlled targets |
| `WA_AI_PC_update_project_progress` | No | `WA_AI_PC_complete_project_by_id` applies the same controller test |
| `WA_AI_PC_railway` | No | Capability terms decide (see the eligibility table) |
| `WA_AI_MILITARY_update_posture` | **Yes** | Publishes an "attack now" verdict; no downstream controller test |
| `WA_AI_LEND_LEASE_request_surplus_relief` | **Yes** | Pulls equipment from allies; no downstream controller test |

`exists = yes` keeps annexed corpses out — the question Fix 68 flagged as unverified — for the cost of
one cheap trigger.

**What this does and does not give a capitulated country.** It unfreezes the queue: the fossils age,
the Fix 41 lane revalidates them, and obsolete ones are cancelled, which in turn unfreezes
`WA_AI_PC_active_nonrail_projects` and reopens the `WA_AI_priority_construction_strategies` dispatcher
for soil the country still controls. It does **not** generally hand it the railway system — for any
capitulated country the binding term is the surrender gate, whose escape hatch needs 75 civs, so a
rump like FRA (21 civs) still fails. That is deliberate: Fix 75 removes *capitulation* as a
disqualifier, it does not lower the capability bars. Whether `surrender_progress` should gate this at
all is the open question R27 owns; the Tunisian rail itself comes from Fix 74's ally leg, which keeps
firing for exactly the countries that fail here.

## Route Processing Pipeline (`railway_core.txt`, lines 85-200)

After strategies populate the output arrays, the core runs ONE pass in phases (`[rail-admission-churn]`,
the corridor's shape):

1. **Phase 0 — pathfind and collect** (every route, cap `routes.max_total`): A* via `WA_AI_PATHFIND_PROV_get_path` with `_pathfind_prov_type = 2` (ROOT + allied + subject provinces since `9aef32f41`) and `_pathfind_prov_allow_partial = 1`; each segment is collected into the `_lseg_*` temp arrays with its RAW map level, every path province into `_valid_provinces`. Dead-end paths at coastal provinces trigger `WA_AI_PC_create_frontier_port` here.
2. **Stale project validation, BEFORE admission**: queued railway projects (`type_id = 13`) whose target province is on no valid path are cancelled — unless paid past `constant:wa_ai_pc.alloc.stale_keep_paid_fraction` (kept, `WA_TLM_pc_stale_kept_n`) — so their slots are free for this pass. Skipped when routes were requested and every pathfind failed (an empty `_valid_provinces` would cancel 100 %). Fix 50 pins the filter to the railway constant instead of the shared `_project_type_id` temp, which frontier-port creation temporarily changes to 14.
3. **Phase A — head**: segments with map level below `land_war.rail_level_floor` are admitted first at target = floor, via `WA_AI_PC_start_railway_project`, at their route's band + (`prio.rail_connect` − `prio.rail_war`) so the fill funds them before any rail-war upgrade of any pass.
4. **Phase B — raise**: the remaining segments at the sizing target, one sweep per raw map level from the floor up to `rail_level_cap_overland − 1` (every level-2 hop of every route before any level-3 hop). Always runs after A (the corridor runs it only when A admitted nothing). Log: `RAILWAY ADMISSION: segments=N head=A rest=B`.
5. **Port upgrades**: Processed via `WA_AI_PC_process_port_upgrades` (builds naval bases via PC system, capped at level 9 since L5 railways bottleneck at 44 supply)
6. **Factory override**: When railway projects are queued, sets override flag to allocate up to 50% extra factory capacity for 30 days

## Function Reference

### Core (`railway_core.txt`)

| Function | Line | Description |
|----------|------|-------------|
| `WA_AI_PC_railway` | 43 | Main entry point. Manages interval, checks eligibility, dispatches strategies, processes routes. |
| `WA_AI_PC_railway_validate_queued_projects` | ~216 | Pins stale-project validation to railway `type_id = 13`, isolating it from shared project-input temporaries. |
| `WA_AI_PC_railway_STRATEGIES` | 209 | Strategy dispatcher. Gets capital info, checks enemy types, calls strategies. |

### Strategies (`railway_strategies.txt`)

| Function | Line | Description |
|----------|------|-------------|
| `WA_AI_PC_railway_STRATEGY_land_war` | 20 | Land war: capital → frontline supply hubs per direct-border enemy. Dispatches the three candidate populations (Fix 74). |
| `WA_AI_PC_railway_land_consider_frontline` | 143 | Fix 74: the shared per-state body, THIS = frontline state, ROOT = builder. Was duplicated between the ROOT loop and the Fix 27 subject loop; the two copies differed only in the supply-hub acceptance test. |
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
| `WA_AI_PC_process_port_upgrades` | 893 | Uses `railway_port_upgrades_` | Processes port upgrade entries as naval base projects (type 14), capped at level 9. |
| `WA_AI_PC_province_is_coastal` | 940 | `_check_province_id` → `is_coastal_province_` | Checks if province is in a coastal state. |
| `WA_AI_PC_create_frontier_port` | 965 | `_frontier_province_id` → `frontier_port_created_` | Queues port construction when partial path ends at coast, capped at level 9. |

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

### Provincial Pathfinding Types (`WA_AI_PATHFIND_PROV_get_path`)

Since commit `9aef32f41` ("pathfinding bug when puppet isn't in faction"), all three provincial
types share the same neighbor filter — ROOT + allied (faction) + subject controlled provinces —
and differ only in cost model:

| Type | Neighbor Filter | Cost Model | Use Case |
|------|-----------------|------------|----------|
| 0 | ROOT + allies + subjects | Distance only | General pathfinding |
| 1 | ROOT + allies + subjects | Distance + terrain | Defensible positions |
| **2** | **ROOT + allies + subjects** | **Railway cost reduction** | **Railway building** |

**All railway strategies use type 2**, which:
- Applies cost reduction for existing railways: `cost = base_cost / (railway_level + 1)`
- Can route through allied and subject territory (`build_railway` is a map modification and
  works regardless of the controller)

### State-Level Pathfinding Types (`WA_AI_PATHFIND_get_path`)

The state-level A* is used only by the supply-line strategies
(`WA_AI_build_supply_line` in `WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`).
- Input: `_pathfind_start`, `_pathfind_target`, `_pathfind_type` (state IDs)
- Output: `pathfind_success`, `pathfind_path_` array of state IDs
- Capped at 75 A* iterations — anchors must be reasonably close to the target front.

| Type | Neighbor Filter | Cost Model | Use Case |
|------|-----------------|------------|----------|
| 1 | ROOT + subjects + faction (Fix 30) | Distance / infrastructure preference | Supply-line infrastructure |
| other | ROOT only | Distance | Unused (legacy default) |

Type 1 succeeds either on reaching the target state or on reaching a state adjacent to
territory controlled by the target's controller (the front line). Fix 30 (R9, campaign
66d6b53c): the type-1 filter had been ROOT-only since the original supply system and was never
covered by the `9aef32f41` provincial fix — with subject-owned corridor anchors (Cairo 446 =
UKE, Tripoli 448 = ITL) the A* died at iteration 1. Both state-level loops now use explicit
break variables (`_pathfind_break`, `_pf_build_break`) instead of the shared `break` temp
variable, which other effects in the same pulse pollute.

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

3. Route processing (one pass, phases — [rail-admission-churn])
   ├── Phase 0: A* pathfinding (type 2, allow partial) for every route, segments collected
   │   ├── Partial path → frontier port creation
   │   └── path provinces → _valid_provinces
   ├── Stale project validation + cancellation (paid ≥ keep fraction → kept)
   ├── Phase A: segments below the floor → WA_AI_PC_start_railway_project (target = floor)
   └── Phase B: the rest → WA_AI_PC_start_railway_project (sizing target)

4. Post-processing
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

### 3. No Dynamic Supply Hub Building (partly lifted by Fix 95)
The three discovery strategies build railways TO existing supply hubs and never place new ones. Since
Fix 95 the PC system CAN build a `supply_node` (building type 17) and the theatre-corridor pass does so
at the nodes its data marks — but only there; there is still no general "where would a hub help"
selector.

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
