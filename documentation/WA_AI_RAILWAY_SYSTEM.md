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
wa_ai_railway.eligibility.min_civs = 50      # base civ minimum inside the run (war = war_civs_factor x this)
wa_ai_railway.eligibility.war_civs_factor = 0.6  # Fix 95: one declaration for the main pass and the corridor pass
wa_ai_railway.corridor.interval_weeks = 4    # Fix 95: theatre-corridor pass cadence (own counter)
wa_ai_railway.corridor.rail_level = 2        # target level on every corridor hop
wa_ai_railway.corridor.queue_max = 8         # corridor projects in flight per builder per building type (tag 27, scoped)
wa_ai_railway.corridor.max_routes_per_run = 14  # = the whole node-pair list; NOT a window (validator completeness)
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
thresholds unchanged, but it is now a single definition shared with Fix 74's ally leg, which needs
exactly the same judgement. Before `WA_AI_PC_railway` is called:

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

Three triggers in `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` carry the policy:

| Trigger | Scope | Answers |
|---|---|---|
| `WA_AI_PC_country_cannot_build_own_logistics` | country | Is this country locked out of the railway system? (capitulated, or below the civ/state eligibility thresholds) |
| `WA_AI_PC_can_build_logistics_here` | state, ROOT = builder | May ROOT queue logistics on this state? (ROOT-controlled, subject-controlled, or dependent-ally-controlled) |
| `WA_AI_PC_is_logistics_build_partner` | country, ROOT = builder | Country-scoped twin, for selectors that iterate `every_country → every_controlled_state` |

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

**Files.**

| Layer | File | What |
|---|---|---|
| data | `WA_AI_CONSTRUCTION_PRIORITY_corridor_data.txt` | `WA_AI_PC_CORRIDOR_define_north_africa` fills `corridor_node_prov_` / `_depot_` / `_port_`. Pure data. A second theatre = a second define. |
| strategy | `railway_strategies.txt` `WA_AI_PC_railway_STRATEGY_theatre_corridor` | classifies every node (ours / enemy-held), applies the theatre gate, publishes routes (`corridor_route_*`) and hubs (`corridor_hub_*`) for this pass |
| core | `railway_core.txt` `WA_AI_PC_railway_corridor_pass` | own interval counter, civ floor, pathfinding (type 2, **no partial**), segment admission through `WA_AI_PC_start_railway_project` with `_railway_family_ = 1`, hubs through `WA_AI_PC_corridor_start_hub`, stale-path validation pinned to `type_id` corridor, `WA_TLM_r95_corridor_*` |
| helpers | `railway_helpers.txt` `WA_AI_PC_corridor_start_hub` | queues a supply hub (PC type 17, new in Fix 95 part 1) or a naval base (14) at a named province, idempotent on the building's existence |
| triggers | `WA_AI_CONSTRUCTION_triggers.txt` `WA_AI_PC_corridor_node_is_ours` / `_is_hostile` / `WA_AI_PC_corridor_theatre_live_north_africa` | province-level control tests over `any_country`; theatre gate = AIR contested trigger OR no enemy on any node (preparation) |
| constants | `wa_ai_railway.txt` `corridor.*` (`interval_weeks` 4, `rail_level` 2, `queue_max` 8 per building type, `max_routes_per_run` 14 = the whole pair list, so the validator's cancel set is always complete); `wa_ai_pc.txt` `type_id.corridor` 27, `cost.supply_node` | |

**Rules the engine applies — no tag, no date, no side (the corridor is symmetric):**

- A node is *ours* when a country satisfying `WA_AI_PC_is_logistics_build_partner` (ROOT, a subject
  of ROOT, or a faction ally that `cannot_build_own_logistics` — the Fix 74 leg, so ENG/USA build in
  Free-French Tunisia and stop the day FRA can build for itself) **controls the province**. State
  control is never consulted (Cyrenaica 663 was ITL-controlled with ENG provinces inside).
- The rail between two consecutive nodes is requested only when **both** are ours; the pathfinder
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
  and *every* pathfind failed (a transient hole must not cancel paid-for progress). Peace purges the
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

Two partners building on the same host soil (ENG + USA on FRA's Tunisia) each see only their own
queue, so both may add +1 on the same hop in the same pass; `current_level` is read from the built
global, so the overshoot is bounded at `rail_level + 1` and costs one segment per partner. Accepted.

**Not solved here:** the corridor gives the ground campaign its logistics; it does not put divisions
in Africa (`66636ff4`: 92/117 ENG divisions under garrison orders, offensive `plan_value = -1`).

**Verification:** checklist item R60; `savegame.py pc <TAG> --match corridor` for the queue side,
`tlm <TAG> --match r95` for admissions, and the map (railway connection level between two nodes,
`supply_node` at 10049 / 9980, `naval_base` at 11957) for the built side.

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

After strategies populate the output arrays, the core processes each route:

1. **Pathfinding**: A* via `WA_AI_PATHFIND_PROV_get_path` with `_pathfind_prov_type = 2` (ROOT + allied + subject provinces since `9aef32f41`) and `_pathfind_prov_allow_partial = 1`
2. **Partial path handling**: Dead-end paths at coastal provinces trigger `WA_AI_PC_create_frontier_port` (queues port construction)
3. **Segment creation**: For each segment in the path, calls `WA_AI_PC_start_railway_project`
4. **Stale project validation**: Existing queued railway projects (`type_id = 13`) are checked; those targeting provinces no longer on a valid path are cancelled. Fix 50 pins this filter to the railway constant instead of the shared `_project_type_id` temp, which frontier-port creation temporarily changes to 14.
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
