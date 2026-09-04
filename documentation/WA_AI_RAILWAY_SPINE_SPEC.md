# Railway spine — final specification

Subjects: `rail-spine-tree` (the trunk/branch route model) and `pc-build-speed` (the ledger
speed model), both owner-admitted 2026-09-05, both OPEN in `WORK.md`. This document is the
build spec; `WORK.md` carries the state, the harness output and the campaign probes. Reads
with `WA_AI_RAILWAY_SYSTEM.md` (the system as it is) and `WA_AI_LOGISTICS_MODEL.md` (the
supply model).

Labels follow AGENTS.md: **MEASURED** = read in a save, a log or a file; **DERIVED** =
computed from a measurement; **ASSUMED** = not verified.

---

## 1. Problem

**MEASURED**, campaign `916b90f6` (cloud observer run, 1936-1945.12) and three owner console
passes (1943.5, 1943.6, 1943.7):

| Fact | Reading |
| --- | --- |
| Narrowest rail link Berlin→every Soviet-front hub = **3** on 60 of 60 (hub × date) cells, 1941.12-1944.6 | the front never read more than 28 supply from Germany |
| German rail went to the shared trunk WEST of the 1939 border (Ostmark/Poznan 3→4, Mazowieckie→Lublin 3→5); nothing east of Wilno / Polesie moved | the budget was spent where every route overlaps, never on the branches |
| The trunk flips between two lines pass to pass: north (Poznan–Warsaw–Białystok–Grodno–Vilnius) in May and June, south (Ostmark–Lublin–Lwów–Polesie) in July, Pskov detoured through Minsk–Vitebsk | the pathfinder's "designated network" ×0.5 is a temp of the current pass; the first route pathfound decides the trunk |
| 6 of 12 admitted rail projects in 1943.6 were a stub Katowice→Southern Slovakia at band 700 (partial-path factor), 4 never funded | a search toward a far south-eastern hub (Crimea / Odessa, RUK/ROM-held) exhausted `_pf_max_its = 100`; the fallback picked the closed node with the HIGHEST cumulative cost, not the one nearest the target |
| 80 of 80 rail civs on the North Africa corridor in 1943.5, 0 `rail` projects east | corridor and land-war share band 1000 |
| The ledger charges a 20-civ rail project 350 IC per weekly pulse (50/day); the engine tooltip builds the same project at 130.5/day | the ledger ignores the country construction modifiers (+45 %) and the state infrastructure (×1.8) |

## 2. Engine model this spec is built on

- A hub's supply from its capital = the **minimum** rail level along the path (4 + 8 × level:
  12 / 20 / 28 / 36 / 44). Owner ruling 2026-09-05 ("cas numéro 1"). **ASSUMED**: shared
  capacity on a trunk segment is not the binding model. Tell it is wrong: a trunk segment's
  supply-map tooltip reads used = capacity while hubs read below their last hop's level; the
  design then needs a second parallel trunk, which §5 step 4 already allows.
- A railway cannot be downgraded. Overbuilding is permanent (LOGISTICS_MODEL §10 rule 3).
- Engine construction speed of a building = factory output (2.5/day) × factories × (1 +
  country construction modifiers) × (1 + 0.1 × state infrastructure) — **MEASURED** on the
  June 1943 tooltip for a railway; other types ASSUMED until their tooltip is read.

## 3. Definitions

| Term | Definition |
| --- | --- |
| Trunk set **T** | provinces reachable from the capital province over rail edges of level ≥ `spine.trunk_level` (5), on the WA cache `global.WA_AI_PC_railway_connection_level_<a>^<b>` and the generated adjacency. One connected component; Paris–Berlin–Minsk at 5 is one trunk for GER. Empty → T = {capital}. |
| Railhead **R** | a province with a supply hub, in a state held by ROOT / a subject / a dependent ally, NOT a frontline state, chosen per enemy (§5 step 2). |
| Spine **S** | T ∪ the trunk routes of this pass (R1 → T, R2 → S). |
| Frontline hub | as today: a state bordering the enemy (or its subjects), with a supply hub, held by ROOT / subject / dependent ally, hub province held (`WA_AI_PC_railway_land_frontline_candidate` + `consider_frontline`). |
| Branch | the route from a frontline hub to the nearest element of S. |
| Hop | one province-to-province rail edge; one PC project = one level on one hop (800 IC). |

## 4. Gate

The spine mode runs for enemy E when BOTH hold; otherwise the current land-war behaviour
(routes from the capital, floor target) is kept unchanged for that enemy:

- frontline candidates against E (states passing the limit check, counted BEFORE the
  `routes.max_per_enemy` cap) ≥ `spine.min_hubs` (**4**, owner 2026-09-05);
- E `is_major = yes` OR E has ≥ `spine.min_enemy_divisions` (40) divisions.

Denmark, Luxembourg, an occupied Yugoslavia: no trunk. The Soviet Union in 1943: 9
candidates, passes. **DERIVED**: Poland 1939 (3-5 border states) sits at the threshold —
measure on the first harness.

## 5. Algorithm — per enemy, per land-war pass

Cadence unchanged: `interval.war_weeks` (8) at war, `interval.peace_weeks` (12) in peace.
Peace mode (§6) runs the same steps toward the CONFIG-declared target.

0. **Gate** (§4).
1. **Trunk walk**: bounded breadth-first walk from the capital over edges of level ≥
   `spine.trunk_level`, at most `spine.max_walk` (400) provinces; result = T (temp array).
2. **Railhead R1**: candidates = every state with a supply hub held by ROOT / subject /
   dependent ally that is not a frontline candidate of E. Score(R) = Σ over E's frontline
   hubs of dist(hub, R) + `spine.capital_weight` (0.25) × dist(capital, R) − `spine.in_trunk_bonus`
   × (R ∈ T). Distances are straight-line (`WA_AI_MATH_get_distance_between_provinces_a_b`
   on province coordinates). Hysteresis: the previous railhead (per-enemy country variable
   `WA_AI_PC_spine_railhead@E`) is kept unless the best candidate scores better by more than
   `spine.hysteresis` (0.2, relative). Log `RAILWAY SPINE`.
3. **Trunk route**: R1 → the element of T nearest to R1 (straight-line pick, then A\* with
   `_pathfind_prov_type = 2`, no partial); target `land_war.rail_level_cap_overland` (5); band
   `prio.rail_connect` (1100). R1 ∈ T → no trunk route. S = T ∪ that route's provinces.
4. **Second railhead** (at most `spine.max_second_railheads` = 1): group B = hubs whose
   distance to the centre of the hubs-not-nearest-to-R1 is smaller than their distance to R1
   (two-centre split, one iteration); R2 = best-scoring candidate for B alone. Keep R2 iff
   dist(R2, S) + Σ_B dist(h, R2) < Σ_B dist(h, S). Its trunk route R2 → nearest element of S,
   same target and band; S grows by it.
5. **Branches**: every frontline hub → the element of S nearest to it (straight-line pick,
   then A\*); target = the hub's demand from `WA_AI_PC_railway_land_size_this_route`
   (`rail-sizing-demand`: hub state + enemy-bordering neighbours, ratio 0.5, floor 2, cap 5);
   band as today (`rail_war`, ×0.7 never applies — see step 7). 10-20 hops per search
   instead of 50-65, so `_pf_max_its = 100` no longer binds.
6. **Admission** (one family budget, `routes.queue_full` = 12, validation before admission
   and the keep rule of `rail-admission-churn` unchanged):
   1. phase A as today: any hop below `land_war.rail_level_floor`, head band;
   2. **trunk hops by value**: value(h) = number of branches attached downstream of h whose
      effective minimum — min(trunk-prefix minimum from the capital to the attachment point,
      branch minimum) — equals level(h), i.e. the branches this very hop caps. Descending
      value, then level ascending, then capital-first. Log `RAILWAY TRUNK`.
   3. **branch hops** by the existing level sweep (raw level ascending, floor …
      cap_overland − 1), route order within a level;
   4. nothing else: partial paths are not admitted for the land family (step 7).
   The fill (`WA_AI_PC_assign_factories`) serves by band then insertion, so trunk hops at 1100
   are funded before branch hops at 1000 and before any corridor project.
7. **Partial paths**: the land family calls the pathfinder with `_pathfind_prov_allow_partial
   = 0`. The fallback stays for the overseas/beachhead strategies, with its frontier changed
   from "closed node with the highest g" to "closed node with the lowest h" (nearest the
   target). Impact analysis owed on the corridor and overseas users of the fallback.

Worked example the trunk criterion must reproduce: trunk Berlin→Minsk, 30 hops at 3;
branch Warsaw→Pskov already at 5, attached at hop 10; other branches at 3 attached at hop
30. Hops 1-10 cap Pskov (effective min 3 = their level) and every other branch → value = all
branches; hops 11-30 cap only the Minsk branches → lower value. Hops 1-10 are raised 3→4→5
first (Pskov reads 44 after 20 hop-levels of work, not 60), then hops 11-30 at 3→4.

## 6. Peace mode (lever "time")

When a CONFIG railway window names a target (e.g. `WA_AI_CONFIG_RAILWAY_GER_to_SOV_window`)
and there is no war with it, the spine mode runs with the hub set = our states bordering the
target that hold a supply hub (the prewar strategy's population), gate satisfied by the window
itself (no division count in peace), trunk band `rail_prewar` (500). Goal: T reaches the
border railhead at 5 before the war; on day 1 only branches remain. **DERIVED** at the
corrected ledger speed (§8): Berlin→border ≈ 20 hops × 2 levels ≈ 40 hop-levels ≈ 40-55
weeks at 79 civs — fits between 1938 and 1941.6.

## 7. Theatre arbitration (lever "band")

Trunk hops of an enemy passing the gate carry `prio.rail_connect` (1100, already declared,
no new band, `savegame.py _PC_BANDS` unchanged). Branch hops keep `rail_war` (1000) — the
same band as the theatre corridors, so the Soviet branches and the Libyan corridor still
compete at the fill; the trunk does not. Tell it is gone: a `PC_ASSIGN` block funding a
corridor project above an unfunded trunk hop.

## 8. Ledger speed (`pc-build-speed`)

`WA_AI_PC_get_build_speed` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`, THIS = state, ROOT =
builder):

| Defect | Fix |
| --- | --- |
| `modifier@production_speed_buildings_factor` and the per-type `modifier@production_speed_<type>_factor` are read in STATE scope; the modifiers are category **country** (install `modifiers_documentation.md`) → 0 for every type | read them on the builder: inside `ROOT = { … modifier@… }` (shipped form; the scope-prefix read `ROOT.modifier@…` is the same fact) |
| infrastructure × (1 + 0.1 × level) applied to types 5-12 and 15-16 only | apply to type 13 (rail) — MEASURED on the tooltip; other province/state types (2 air base, 4 radar, 14 naval base, 17 supply node) only after their own tooltip is read |
| base 2.5/factory/day is a literal | keep; register in `tools/constants_registry.json` if it mirrors a define (`BASE_FACTORY_SPEED` family) |

Shipped 2026-09-05 (`pc-build-speed`, see `WORK.md`): the country family is read inside `ROOT = { }`,
the STATE-category member `state_production_speed_buildings_factor` is read on the state, and the
infrastructure multiplier is applied to **every PC type except infrastructure (type 1)** — the mod's
`common/buildings/00_buildings.txt` flags every other PC building `infrastructure_construction_effect =
yes` (MEASURED), the rail tooltip confirms one flagged type (MEASURED), and the flag being the engine's
switch is **ASSUMED** — the harness's known-false control on a non-rail type is where that assumption
is tested. 2.5 is `constant:wa_ai_pc.speed.factory_output`, registered against
`NDefines.NProduction.POWERED_FACTORY_SPEED`; 0.1 is `wa_ai_pc.speed.infra_per_level` (DERIVED from
`INFRA_MAX_CONSTRUCTION_COST_EFFECT` = 1.0 over 10 levels, not registrable as an equality).

**MEASURED** before: 350 IC per weekly pulse at 20 civs (50/day). Expected after, Germany
June 1943: 7 × 130.5 ≈ 913 per pulse. Consequence: every PC family accelerates by (1 +
country modifiers) — and slows under an economy-fatigue penalty — and rail additionally by
the state infrastructure. Allocation caps calibrated on the slow ledger (air bases,
refineries, corridor) are retuned on measurement, not pre-emptively (owner ruling).

## 9. Constants

New group `wa_ai_railway.spine` (`common/script_constants/wa_ai_railway.txt`), every key read
in exactly one file:

| Key | Value | Read by |
| --- | --- | --- |
| `trunk_level` | 5 | trunk walk (helpers) |
| `max_walk` | 400 | trunk walk |
| `hysteresis` | 0.2 | railhead select (strategies) |
| `capital_weight` | 0.25 | railhead select |
| `in_trunk_bonus` | to calibrate; start = one hub-distance unit | railhead select |
| `min_hubs` | 4 | gate (strategies) |
| `min_enemy_divisions` | 40 — the one number without a measurement behind it | gate |
| `max_second_railheads` | 1 | step 4 |

Unchanged and reused: `land_war.rail_level_floor` 2, `rail_level_cap` 4, `rail_level_cap_overland`
5, `corridor.target_ratio` 0.5, `routes.queue_full` 12, `routes.max_per_enemy` 4,
`routes.max_total` 16, `prio.rail_connect` 1100, `prio.rail_war` 1000, `prio.rail_prewar` 500.

## 10. Files and state

| File | Change |
| --- | --- |
| `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt` | gate; `WA_AI_PC_railway_spine_select` (railheads, hysteresis, R2 test); trunk routes appended to the route arrays with a trunk flag; branch `route_start` = nearest S element; peace mode toward the CONFIG target |
| `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt` | bounded trunk walk `WA_AI_PC_railway_spine_walk` (T); nearest-element pick |
| `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt` | phase 0 tags `_lseg_trunk_`, computes trunk-hop values; admission order §5.6; `_pathfind_prov_allow_partial = 0` for the land family |
| `common/scripted_effects/WA_AI_pathfinding_effects.txt` | partial-path frontier = lowest h (shared with overseas/corridor users — impact analysis) |
| `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt` | `WA_AI_PC_get_build_speed` (§8) |
| `common/script_constants/wa_ai_railway.txt` | group `spine` |
| `WORK.md`, `WA_AI_RAILWAY_SYSTEM.md`, `WA_AI_LOGISTICS_MODEL.md` | state, pipeline section, §11 sizing/speed |

Persistent state (country scope, system state, cleared by the peace purge with the rail
projects): `WA_AI_PC_spine_railhead@<enemy>` (province id). T and S are per-pass temps.

Logs (`WA_AI_construction_logging`): `RAILWAY SPINE: enemy=E cand=N T=n R1=p R2=p|0 trunk_hops=k`,
`RAILWAY TRUNK: hop a->b level=L value=v`, `PC SPEED: type=T mods=M infra=I speed=X` (first
project of each `PC_ASSIGN` only).

## 11. Verification

Console harness (owner-run, `tag GER`, never spectated — inline `is_controlled_by = var:` is
known to misread under the observer tag):

| Run | Expect | Known-false control |
| --- | --- | --- |
| 1941-42 GER save, one pass | one `RAILWAY SPINE` line per enemy passing the gate; R1 in the centre of the Pskov–Rostov front (Minsk/Gomel area), never Riga or Kiev; every branch ≤ 20 hops from an S element; first `PC QUEUED` = trunk hops in value order; no band-700 stub | Denmark / any enemy failing the gate: no SPINE line, direct routes as before |
| 1938 GER save | trunk toward the CONFIG target queued in peace at band 500 | a country with no CONFIG window: nothing |
| `pc-build-speed`, `barb_supply test.hoi4`, one pulse | a 20-civ rail project in a German state loses ≈ 913 (was 350); `PC SPEED mods=0.45 infra=1.8` | same project on a Soviet state at infrastructure 2: infra=1.2; a country with no construction modifiers: mods=0, 350 unchanged |

Campaign probes (save-visible): `rail.py 6521 <hub>` narrowest link > 3 on ≥ 1 route within
3 passes of the front settling; no two-spine signature (rail raised on both the Warsaw and the
Lublin line in one year); `pc GER --match rail-prewar` shows no 700-band stubs; corridor
projects no longer hold 100 % of rail civs while a land front is open; GER
`wa_tlm_pc_built_n` per war year ≥ 1.5 × `916b90f6` (503 over the war). Tell-tales of
over-reach: level-5 edges on routes whose hub area holds < 20 divisions; air-base / refinery
caps reached earlier than before (retune those caps, not the speed).

## 12. Out of scope, by owner ruling

Rail cost (800), civs per project (20), PC allocation fraction (0.40) and the 0.6 rail
override are untouched. Engine-side construction of rails (a second door to more factories) is
not part of this spec. The ratio 0.5 → 0.7/1.0 step waits for the campaign measurement of
`rail-sizing-demand`.

## 13. Order of implementation

1. `pc-build-speed` — small, isolated, immediate effect on every PC family; reviewers +
   harness.
2. `rail-spine-tree` — strategies → helpers → core → pathfinder fallback → constants → docs;
   reviewers + harness; then one cloud campaign for both.
