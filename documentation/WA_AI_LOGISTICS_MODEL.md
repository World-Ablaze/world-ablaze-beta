# WA AI - Logistics model (supply reference)

Status: reference document. Written 2026-08-17 while designing the theatre-corridor dimensioning
work (Fix 95 follow-up). It records **how HOI4 supply actually works in this mod's tuning**, so that
any AI code deciding *what to build and at what level* reasons from the same model.

Scope: what determines whether a division is supplied, and which construction levers move it.
Not in scope: the AI systems themselves - see `WA_AI_RAILWAY_SYSTEM.md` and
`WA_AI_PC_QUEUE_FAIRNESS_DIAGNOSIS.md`.

Every number below is quoted with a source. A `[:NNN]` link points at this repository's
`common/defines/05_defines.lua`; a number vanilla owns is cited by section name in the install's
`common/defines/00_defines.lua`, because `common/defines` is **not** in `descriptor.mod`'s
`replace_path` list - the install's file loads first and WA's overrides individual keys on top, so a
key WA does not name still has vanilla's value. Where a statement is a mechanic rather than a value
read from a file, it is marked `[mechanic]` and its source is named.

**The key NAME is the citation; the `[:NNN]` anchor is only a convenience.** Nothing enforces those
line numbers, so verify a number by grepping its key in both defines files rather than by following
the anchor.

---

## 1. The model in one paragraph

Supply is a **flow network**. It originates at the capital and at naval bases, travels along
**railways** between **supply hubs**, and then radiates out from each hub into the surrounding
provinces, **losing a fixed amount per province of distance**. A division is supplied when the hub
network delivers enough flow, close enough. Two independent things can therefore fail: the supply
does not **reach** (range), or there is not **enough** of it (throughput). They have different
levers, and confusing them wastes civilian factories.

---

## 2. The two failure modes

This is the operative distinction. User ruling, 2026-08-17.

| A division is unsupplied because... | Diagnosis | Levers that help | Levers that do NOT help |
| --- | --- | --- | --- |
| **it is too far** from any hub | range | hub **motorization**; placing a **new hub** closer | raising railway level; raising port level |
| **demand exceeds throughput** | flow | raising **railway** level; raising **port** level; adding an entry port | motorization; a new hub at the same distance |

Corollary: before spending on a level, establish *which* of the two is binding. A level-5 railway
into a hub 12 provinces from the front fixes nothing, and a motorized hub behind a level-1 railway
fixes nothing either.

---

## 3. Building caps (`common/buildings/00_buildings.txt`)

| Building | Cap | Base cost | Note |
| --- | --- | --- | --- |
| `supply_node` (hub) | **`province_max = 1`** - binary, **no level** ([:64](../common/buildings/00_buildings.txt#L64)) | 10000 | You cannot "upgrade a hub". You place one or you do not. |
| `naval_base` (port) | `province_max = 10` ([:561](../common/buildings/00_buildings.txt#L561)) | 10000, `per_level_extra_cost = -556` | Coastal only. Later levels are *cheaper* than the first. |
| `rail_way` | level per **connection**, max 5 `[mechanic]` | 800, `per_level_extra_cost = 0` ([:70](../common/buildings/00_buildings.txt#L70)) | Flat cost per level. Cost scales with the number of hops, not with the level. |

**A hub has no level.** Its throughput is whatever the railway feeding it delivers. This is the single
most important fact for AI sizing code, and the one that was got wrong before this document existed.

---

## 4. Throughput - the two ladders (`common/defines/05_defines.lua`)

They are **different shapes**. Do not use one formula for both.

### Railway

```
flow = RAILWAY_BASE_FLOW + RAILWAY_FLOW_PER_LEVEL * level
     = 4 + 8 * level
```
([:950-951](../common/defines/05_defines.lua#L950))

| Level | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Flow | 12 | 20 | 28 | 36 | **44** |

Each damaged railway subtracts `RAILWAY_FLOW_PENALTY_PER_DAMAGED = 8.0` ([:952](../common/defines/05_defines.lua#L952)) -
i.e. one full level. A river transfers between nodes as if it were a level-1 railway
(`RIVER_RAILWAY_LEVEL = 1`, [:940](../common/defines/05_defines.lua#L940)).

### Naval base (port)

```
flow = NAVAL_BASE_FLOW + NAVAL_FLOW_PER_LEVEL * level
     = 0 + 5 * level
```
([:937-938](../common/defines/05_defines.lua#L937))

| Level | 1 | 2 | 4 | 6 | 8 | 10 |
| --- | --- | --- | --- | --- | --- | --- |
| Flow | 5 | 10 | 20 | 30 | 40 | **50** |

**Ruling (user, 2026-08-17): the port flow ladder is 5 per level.**
`SUPPLY_PORT_LEVEL_THROUGHPUT = 3` exists and is commented "supply throughput per level of naval base",
but it is **not** the supply-node flow cap and must not be used in the flow model. Do not "correct"
the 5 to a 3. Two mechanical notes added 2026-08-18: the live key is `NDefines.NBuildings`
(install `common/defines/00_defines.lua`, section `NBuildings`), not `NDefines.NCountry`, and WA's old
`NCountry` write bound a field nobody reads - it has been removed. Vanilla's value is the same 3, so
nothing changed.

### The two ladders compared

| Equivalence | |
| --- | --- |
| Railway L1 (12) | ≈ port L2-L3 |
| Railway L3 (28) | ≈ port L6 |
| Railway L5 (44) | ≈ port **L9** (45) |

A level-5 railway is worth a level-9 port. That is the origin of
`constant:wa_ai_railway.supply.port_max_useful_level = 9` in `common/script_constants/wa_ai_railway.txt`
- the justification is correct **given the 5-per-level ladder**.

### Convoys

Sea-borne supply costs convoys: `SUPPLY_CONVOY_FACTOR = 0.3` ([:81](../common/defines/05_defines.lua#L81)),
scaled by range via `CONVOY_RANGE_FACTOR = 1.1` ([:82](../common/defines/05_defines.lua#L82)). A port
upgrade is therefore not only a construction cost - it raises convoy demand too.

### Trains

`NUM_RAILWAYS_TRAIN_FACTOR = 0.50` ([:920](../common/defines/05_defines.lua#L920)) - train usage scales
with the railway **distance** from the hub to the capital. A long corridor costs trains even at a low
level. `MIN_TRAIN_SUPPLY_FACTOR = 0` ([:921](../common/defines/05_defines.lua#L921)): with zero trains
in the stockpile, the penalty factor is **0**, i.e. total loss - trains are not optional.

---

## 5. Range - how far supply reaches from a hub

```
range budget = NODE_INITIAL_SUPPLY_FLOW  (+ motorization bonus)
decay        = NODE_STARTING_PENALTY_PER_PROVINCE per province of distance
```

| Define | Value | Line |
| --- | --- | --- |
| `NODE_INITIAL_SUPPLY_FLOW` | 5.0 | [:945](../common/defines/05_defines.lua#L945) |
| `NODE_STARTING_PENALTY_PER_PROVINCE` | **0.75** | [:948](../common/defines/05_defines.lua#L948) |
| `SUPPLY_HUB_FULL_MOTORIZATION_BONUS` | 10.0 | [:946](../common/defines/05_defines.lua#L946) |
| `SUPPLY_HUB_MOTORIZATION_MARGINAL_EFFECT_DECAY` | 0 | [:947](../common/defines/05_defines.lua#L947) |
| `SUPPLY_HUB_FULL_MOTORIZATION_TRUCK_COST` | 500 | [:923](../common/defines/05_defines.lua#L923) |

Two consequences:

1. **Distance is expensive.** At 0.75 per province, an unmotorized hub's 5.0 budget is spent in ~6
   provinces. Motorization roughly triples it (5 -> 15, decay 0 means every level pays fully).
2. **Motorization is the only way to extend an existing hub's reach.** Railway and port levels do not
   buy range - they buy flow into the hub. (User ruling, 2026-08-17.) The other way to shorten the
   distance is to place a **new hub** nearer the front.

> These defines are WA tuning and are **by design** - do not propose reverting them to vanilla
> (recorded in the campaign-audit findings: "supply-reach defines are BY DESIGN").

---

## 6. Sources of supply

| Source | Formula | Line |
| --- | --- | --- |
| Capital | `CAPITAL_SUPPLY_BASE = 5.0` + `0.1`/civ + `0.2`/mil + `0.2`/dockyard | [:925-928](../common/defines/05_defines.lua#L925) |
| State population | `AVAILABLE_MANPOWER_STATE_SUPPLY = 1.0`; **occupied**: `NON_CORE_MANPOWER_STATE_SUPPLY = 0.025` | [:934-935](../common/defines/05_defines.lua#L934) |
| Infrastructure | `INFRA_TO_SUPPLY = 1.5` per level | [:978](../common/defines/05_defines.lua#L978) |
| Victory points | `VP_TO_SUPPLY_BASE = 0.3` | [:979](../common/defines/05_defines.lua#L979) |
| Floating harbour | `FLOATING_HARBOR_BASE_SUPPLY = 50.0`, 180 days | [:942-943](../common/defines/05_defines.lua#L942) |
| Damaged infra | counts as `SUPPLY_FROM_DAMAGED_INFRA = 0.15` | install `00_defines.lua`, section `NSupply` |

The damaged-infra figure was **0.01** here until 2026-08-18, quoting a WA line that wrote the key
under `NDefines.NCountry` while the engine reads it under `NDefines.NSupply`. That write bound
nothing, so every campaign already ran at vanilla's **0.15** - fifteen times what this document
claimed. Damaged infrastructure is far less punishing than the model assumed. User ruling
2026-08-18: keep vanilla's 0.15; the dead line was deleted, not relocated.

**The occupied-territory cliff matters for every offensive.** Population supply drops to 2.5% on
non-core soil ([:935](../common/defines/05_defines.lua#L935)). An attacker advancing into enemy states
loses local supply almost entirely and must import all of it through the network - which is exactly
why a forward port at a spearhead is worth building for the attacker and not for the defender
(the Fix 95 forward-port ruling).

For reference, a floating harbour (50) outperforms a **level-10** naval base (50) instantly and
without construction - but expires after 180 days.

---

## 7. Additivity

**User ruling, 2026-08-17: two hubs in range each delivering 15 are worth one hub delivering 30.**

Design consequence: since a hub cannot be upgraded, "more supply at the front" is achieved by
**adding hubs**, not by making one bigger. And because a nearer hub also pays less range decay,
adding a hub is frequently the better buy:

| Buy | Cost | Gains |
| --- | --- | --- |
| One more railway level over N hops | `800 x N` | +8 flow into the existing hub |
| A new `supply_node` closer to the front | 10000 flat | a fresh flow budget **and** removes `0.75 x (distance saved)` of decay |
| Port +1 level | ~10000 minus `556 x (level-1)` | +5 entry flow, + convoy demand |

There is no single right answer; the point is that the three are **substitutes**, and AI code should
compare them rather than default to raising a level.

---

## 8. Combat consequences

| Define | Value | Line |
| --- | --- | --- |
| `SUPPLY_THRESHOLD_FOR_ARMY_ATTRITION` | 0.4 - attrition only **below** this ratio | [:969](../common/defines/05_defines.lua#L969) |
| `SUPPLY_GRACE` | 168 h (7 days) carried, hardcoded | [:460](../common/defines/05_defines.lua#L460) |
| `OUT_OF_SUPPLY_ATTRITION` | 2.0 max | [:435](../common/defines/05_defines.lua#L435) |
| `OUT_OF_SUPPLY_SPEED` | -1.0 (immobile) | [:437](../common/defines/05_defines.lua#L437) |
| `COMBAT_SUPPLY_LACK_ATTACKER_ATTACK` | -1.00 | [:317](../common/defines/05_defines.lua#L317) |
| `COMBAT_SUPPLY_LACK_ATTACKER_DEFEND` | -0.80 | [:318](../common/defines/05_defines.lua#L318) |
| `COMBAT_SUPPLY_LACK_DEFENDER_ATTACK` | -0.60 | [:319](../common/defines/05_defines.lua#L319) |
| `COMBAT_SUPPLY_LACK_DEFENDER_DEFEND` | -0.40 | [:320](../common/defines/05_defines.lua#L320) |
| `NON_CORE_SUPPLY_SPEED` | -0.7 | [:430](../common/defines/05_defines.lua#L430) |
| `ARMY_MAX_SUPPLY_RATIO_GAIN_PER_HOUR` | 0.33 | [:976](../common/defines/05_defines.lua#L976) |

**Supply ratio 0.4 is the target, not 1.0.** Above 0.4 there is no attrition. Sizing the network for
100% of theoretical demand overbuilds; the useful target is the point where the front stops taking
attrition and speed penalties. Any demand estimate in AI code should say which of the two it means.

Railways captured from the enemy are unusable for `RAILWAY_CONVERSION_COOLDOWN = 7` days
(5 on core, 0 in civil war) ([:965-967](../common/defines/05_defines.lua#L965)) - a corridor built
right up to the front line does not pay off the week it is captured.

---

## 9. What the WA AI encodes today

`common/script_constants/wa_ai_railway.txt`, block `supply`, consumed by
`common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt`:

| Constant | Value | Mirrors the define | Status |
| --- | --- | --- | --- |
| `supply.railway_base` | 4 | `NSupply.RAILWAY_BASE_FLOW` | correct |
| `supply.railway_per_level` | 8 | `NSupply.RAILWAY_FLOW_PER_LEVEL` | correct |
| `supply.port_per_level` | 5 | `NSupply.NAVAL_FLOW_PER_LEVEL` | correct |
| `supply.port_max_useful_level` | 9 | derived (L5 rail = 44 ≈ L9 port = 45) | correct |
| `supply.home_port_target_supply` | 44 | derived (L5 railway) | correct |

These three mirrors are registered in `tools/constants_registry.json`
(`engine_railway_flow_base`, `engine_railway_flow_per_level`, `engine_naval_flow_per_level`) so
`python tools/check_constants.py` fails if a define is retuned without updating the AI's model.

Available helpers (`railway_helpers.txt`):

| Helper | Line | Does |
| --- | --- | --- |
| `WA_AI_PC_calculate_railway_supply` | 694 | level -> flow |
| `WA_AI_PC_calculate_port_supply` | 702 | level -> flow |
| `WA_AI_PC_supply_to_target_railway` | 709 | flow -> level (round up, clamp 1-5) |
| `WA_AI_PC_supply_to_target_port` | 728 | flow -> level (round up, clamp 1-10) |
| `WA_AI_PC_supply_to_railway_level` | 677 | flow -> max useful level (clamp 0-5) |
| `WA_AI_PC_calculate_supply_bottleneck` | 665 | `min(a, b)` |

### What is NOT modelled anywhere

These are known gaps, not oversights to be re-discovered:

1. **Demand.** Nothing in `WA_AI_*` estimates how much supply a theatre's divisions actually need.
   Every sizing decision today uses a fixed target level.
2. **Range decay** (`0.75`/province). No AI code accounts for hub-to-front distance when deciding
   whether a level buys anything.
3. **Motorization** as a lever. Not considered at all - so the *range* failure mode has no AI answer.
4. **Train cost** of corridor length (`NUM_RAILWAYS_TRAIN_FACTOR`).
5. **Additivity across hubs** - no code compares "add a hub" against "raise a level".
6. **Convoy cost** of a port upgrade.

---

## 10. Rules of thumb for AI sizing code

1. Decide **which failure mode** you are fixing before choosing a lever (§2).
2. A hub is a **placement** decision, never a sizing one (§3).
3. The chain is in **series**: useful flow = `min(entry port, every railway hop on the path)`. A level
   above the weakest link buys nothing, and **railways cannot be downgraded** - overbuilding is
   permanent, underbuilding is recoverable. Bias low.
4. Size against `sizing.target_ratio` of the estimated need (0.5, `[rail-sizing-demand]`; the original 0.4 was the attrition threshold of §8), never against 100% demand.
5. Compare the three substitutes by cost before spending (§7).
6. On conquered soil, assume **no local supply** (2.5% population factor) (§6).

---

## 11. Theatre-corridor dimensioning - frozen design (2026-08-17)

Status: **SHIPPED 2026-08-18 as Fix 107**, with three recorded deviations - see §11.11, which is the
authority on what the code actually does where it differs from the text below. Applies to `WA_AI_PC_railway_corridor_pass`
(`railway_core`) and `WA_AI_PC_railway_STRATEGY_theatre_corridor` (`railway_strategies`) only.
The land-war / overseas / pre-war passes are out of scope for this iteration.

### 11.1 What is being fixed

| Defect today | Consequence |
| --- | --- |
| Every hop is built to a hardcoded `constant:wa_ai_railway.corridor.rail_level = 2` | Level is chosen with no reference to demand or to the entry-port bottleneck |
| The theatre gate `_corridor_hostile_n_ = 0` cannot tell "not started" from "already won" | The winner keeps building the whole corridor for the rest of the campaign |
| A missing port is placed, an existing one is never raised | The port bottleneck can never be relieved |

### 11.2 What is readable from script (verified 2026-08-17)

The design may only depend on these. **Actual supply is NOT readable from script** - nothing in the
mod reads it - so the AI must *model* flow from levels, never observe it. There is no closed loop;
WA_TLM telemetry compared against a real campaign is the only validation path.

| Input | Form | Source |
| --- | --- | --- |
| Divisions in a state | **comparison only** (`divisions_in_state` is a trigger) - use the 6-step staircase idiom of `WA_AI_MILITARY_posture_count_state_divs` | posture_effects:684 |
| Divisions of a country | exact value (`num_divisions`) | railway_helpers:462 |
| Railway level between two provinces | exact value | `global.WA_AI_PC_railway_connection_level_<a>^<b>` |
| Naval base / supply hub at a node | exact | `WA_AI_PC_railway_get_naval_base_province`, `_state_has_supply_hub` |
| Province path and its length | exact | `WA_AI_PATHFIND_PROV_get_path` -> `pathfind_prov_path_^num` |

### 11.3 Theatre state (three-way, replaces the two-legged gate)

Computed from the node classification the pass already does:

| State | Condition | Behaviour |
| --- | --- | --- |
| `PREP` | `hostile_n = 0` and not all nodes ours | prepare, band `rail_prewar` |
| `ACTIVE` | `WA_AI_MILITARY_AIR_theatre_contested_north_africa` | full sizing, band `rail_war` |
| `RESOLVED` | `hostile_n = 0` **and** `ours_n = corridor_node_prov_^num` | **only routes whose two nodes are flagged `corridor_node_permanent_ = 1`**, level = `sizing.resolved_rail_floor`, no depots, no ports, band `rail_prewar` |

`corridor_node_permanent_` is a **new column** in `WA_AI_PC_CORRIDOR_define_north_africa`, set to 1 on
the Libyan span (Tripoli 1149 .. Tobruk 1130). It expresses "this rail is permanent infrastructure
worth having even with no war on" - user ruling, 2026-08-17.

> Known limitation of `RESOLVED`: requiring **all** nodes ours is strict. A neutral Tunisia that never
> joins leaves the corridor in `PREP` forever, which keeps the pre-war preparation behaviour - the safe
> failure direction (prep is already the intended peacetime state), not a stall.

### 11.4 Demand

```
divs_    = SUM over corridor node states of staircase(divisions_in_state)   # ROOT + allies
demand_  = divs_ x sizing.supply_per_division x sizing.target_ratio
```

15 states x ~6 trigger evaluations, once per 4 weeks per builder - comparable to the weekly AIFC
sector selection, negligible.

| New constant | Value | Meaning |
| --- | --- | --- |
| `sizing.supply_per_division` | **2.5** | average supply need per division. **Calibration knob - user-set placeholder 2026-08-17, to be tuned on campaign results.** |
| `sizing.target_ratio` | **0.5** | share of the estimated need the rail is sized for. The original 0.4 was `SUPPLY_THRESHOLD_FOR_ARMY_ATTRITION` (§8), the *no-attrition floor*; raised one step by `[rail-sizing-demand]` because the AI is meant to advance, not merely avoid attrition — combat and speed penalties still scale below 1.0. **Second calibration knob**; next step is an owner decision after the widened demand count (§11.4, hub state + enemy-bordering neighbours) is measured. |

### 11.5 Injection capacity

```
inject_ = SUM over corridor nodes that are ours AND carry a naval base of (port_level x 5)
```

**Guard:** if ROOT's capital is on the same landmass as the corridor, the network is also fed by land
from the capital and `inject_` under-states it. In that case skip the cap and size on `demand_` alone.
Without this guard a land-connected owner would be told to build *more* than it needs - the wrong
error direction. Use the existing landmass data (`WA_AI_PC_railway_get_continent` idiom).

### 11.6 Railway target

```
cible_    = min(demand_, inject_)                       # the chain is in SERIES (§10 rule 3)
rail_tgt_ = WA_AI_PC_supply_to_target_railway(cible_)   # existing helper, clamp 1..5
rail_tgt_ = min(rail_tgt_, corridor.rail_level_cap)
if RESOLVED: rail_tgt_ = sizing.resolved_rail_floor
```

`constant:wa_ai_railway.corridor.rail_level` **changes meaning from target to cap** and is renamed
`rail_level_cap`. Its header comment and any registry entry must say so.

**No ratchet.** The target is recomputed every pass and simply stops queuing when reached.
`WA_AI_PC_start_railway_project` queues at most **one level per segment per pass**, so a transient
demand spike can commit at most one extra permanent level per 4 weeks. A ratchet would turn a single
spike reading into concrete for months. Since railways cannot be downgraded, following demand is the
*safer* option, not the looser one.

Residual: projects already in the PC queue when the target drops are not cancelled (the stale-path
validation only cancels provinces that left `_valid_provinces`, not lowered targets). Bounded by
`corridor.queue_max = 8` per building type.

### 11.7 Port upgrade - cost arbitration

Only when `inject_ < demand_`. A forward port is **not** redundant with a bigger port behind it:
ports *inject* flow at their own node and injections add (§7). The question is which is cheaper.

```
cost_per_point(port at level L)   = (10000 - 556 x (L-1)) / 5        # 00_buildings.txt naval_base
cost_per_point(rail over N segs)  = (800 x N) / 8 = 100 x N          # 00_buildings.txt rail_way
```

| Port level being bought | per point | | Rail, N segments | per point |
| --- | --- | --- | --- | --- |
| 1 | 2000 | | 3 | 300 |
| 3 | 1778 | | 6 | 600 |
| 5 | 1555 | | 10 | 1000 |
| 8 | 1289 | | 14 | 1400 |
| 10 | 999 | | 20 | 2000 |

**Break-even is roughly 10-14 province segments.** Shorter chain: raise the railway. Longer chain:
raise the forward port. `N` is available for free inside the route loop as `pathfind_prov_path_^num`.

Two effects tilt further toward the railway and are deliberately *not* modelled (they make the rule
conservative, i.e. it prefers rail slightly too often): a railway level also serves every hub further
down the chain, and a port upgrade raises convoy demand (`SUPPLY_CONVOY_FACTOR = 0.3`).

### 11.8 Hubs

Unchanged. A `supply_node` has no level (§3), so there is nothing to size - it is placed or not.
The two nodes already flagged (`Misrata 9980`, `Mechili 10049`) are justified by the **range** model,
not the flow model: at `0.75` supply lost per province (§5), they shorten the hub-to-front distance.
That justification belongs in the header of `WA_AI_PC_CORRIDOR_define_north_africa`.

### 11.9 Out of scope, recorded so it is not re-discovered

| Gap | Why deferred |
| --- | --- |
| **Hub motorization** - the only lever for the *range* failure mode (§2) | Not a construction project; it is a per-hub setting costing trucks (`SUPPLY_HUB_FULL_MOTORIZATION_TRUCK_COST = 500`). Separate system. **The range failure mode therefore still has no AI answer at all.** |
| Train cost of corridor length (`NUM_RAILWAYS_TRAIN_FACTOR`) | No AI model of train stock |
| Convoy cost of a port upgrade | see 11.7 |
| Applying this sizing to the land-war / overseas passes | Much larger blast radius; corridor first |

### 11.10 Verification

WA_TLM probe `r97_sizing_*` per builder, monthly: `divs_`, `demand_`, `inject_`, `rail_tgt_`, theatre
state, and which lever the arbitration chose. Checklist item R62. Because supply is not readable, the
probe records the **model's** view - confirming it against a campaign means reading the map (actual
railway levels, actual port levels) and the front's attrition, not trusting the probe alone.

---

### 11.11 What shipped (Fix 107, 2026-08-18) - and the three deviations

Implemented: §11.4 (demand), §11.5 (injection + guard), §11.6 (computed rail target, no ratchet),
§11.7 (port-vs-rail arbitration, and a port that can be **raised** rather than only placed).
Files: `WA_AI_PC_corridor_compute_sizing` and the rewritten `WA_AI_PC_corridor_start_hub` in
`railway_helpers`, `WA_AI_PC_prov_get_naval_base_level` in `railway_primitives`, the sizing call and the
`corridor_hub_target_` array in `railway_strategies`, the chain-length accumulator + break-even
arbitration + `WA_TLM_r107_sizing_*` in `railway_core`, five constants in
`common/script_constants/wa_ai_railway.txt`. Verification: checklist **R71**.

**Deviation 1 - §11.3 (the three-way `PREP` / `ACTIVE` / `RESOLVED` state) is NOT implemented, and is
out of scope rather than covered.** The user bounded the 2026-08-18 session to sizing plus probes. The
defect §11.3 names - "the winner keeps building the whole corridor for the rest of the campaign" - is
*narrowed* by the demand term (an emptied theatre computes a low target and stops emitting) but not
*closed*: with `corridor.rail_level_floor = 2` the post-victory behaviour on all 14 hops is exactly
today's, where §11.3 would have restricted it to the `corridor_node_permanent_` Libyan span. The
`corridor_node_permanent_` column does not exist. **Do not read the demand term as a substitute.**

**Deviation 2 - §11.7's break-even is 20 segments, not 10-14.** That table priced the port at the
*engine's* tapered cost. PC is a shadow system: it charges `constant:wa_ai_pc.cost.naval_base` **flat**
per level (that key's header, Fix 72). Port = 2000 per supply point at every level; rail = 100 x N.
Break-even 100 x N = 2000 -> N = 20. `N` is the whole chain pathfound in the pass, not one hop.

**Deviation 3 - the demand input is a presence INDEX, not a division count.** §11.4 writes
`divs_ = SUM staircase(divisions_in_state)` and then multiplies by a per-division constant. Those are
different units. `divisions_in_state` is comparison-only, so no exact per-state count exists in script;
the shipped ladder uses bucket midpoints (and drops the posture idiom's armour doubling, a combat-power
proxy) and is named `corridor_presence_` to stop it being read as a count. **Known bias, SUPPOSE:** it
over-reads a *dispersed* army - the same 25 divisions read ~25 in one state and ~35 across five, because
each state pays its own bucket floor. The bias is upward, i.e. toward the permanent direction;
`supply_per_division` is the knob that absorbs it and stays a placeholder until a campaign calibrates it.

**What §11.10 asked for and did not get:** the probe family is `r107_sizing_*`, not `r97_sizing_*`
(r97 was taken by the East-African theatre), and it carries a `_chain` gauge §11.10 did not list -
without it, a pass where the port lever did not fire is indistinguishable from one where it was not
considered.

## 12. Ledger speed - what a civilian factory delivers per day (`pc-build-speed`, 2026-09-05)

PC is a shadow construction system: it charges a project's cost against a speed of its own, then spawns
the building. That speed must be the engine's, or every level and every cap above is sized for a pace
the AI does not actually build at. `WA_AI_PC_get_build_speed` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`,
THIS = state, ROOT = builder) models it as:

```
speed per factory per day = factory_output x (1 + country production_speed modifiers + state_production_speed_buildings_factor)
                            x (1 + infra_per_level x state infrastructure)      # every PC type except infrastructure
```

| Term | Value | Source |
| --- | --- | --- |
| `factory_output` | 2.5 | `NDefines.NProduction.POWERED_FACTORY_SPEED` (`05_defines.lua`; `BASE_FACTORY_SPEED` is 0.0 here) - registered mirror `wa_ai_pc.speed.factory_output` |
| country modifiers | e.g. +0.45 (Germany, June 1943 tooltip) | `production_speed_buildings_factor` + the per-type `production_speed_<building>_factor`, category **country** (install `modifiers_documentation.md`) - read on the BUILDER |
| state modifier | usually 0 | `state_production_speed_buildings_factor`, category **state** - read on the target state |
| infrastructure | ×1.8 at level 8 | `INFRA_MAX_CONSTRUCTION_COST_EFFECT` = 1.0 (install `00_defines.lua`) over 10 levels = `wa_ai_pc.speed.infra_per_level` 0.1, on every building flagged `infrastructure_construction_effect = yes` in `common/buildings/00_buildings.txt` (every PC type except infrastructure) |

**MEASURED** (owner tooltip, a German railway project, June 1943): 20 factories → 130.5/day = 2.5 × 20 ×
1.45 × 1.8. **ASSUMED**: the building flag is the engine's switch for the infrastructure line on the
non-rail types (only the rail tooltip was read). Consequence for sizing: the corridor cadence table
(`WA_AI_RAILWAY_SYSTEM.md`) and the trunk arithmetic of `WA_AI_RAILWAY_SPINE_SPEC.md` §6 are stated at
this speed; an economy-fatigue penalty (`production_speed_buildings_factor -0.5` at its worst,
`00_static_modifiers.txt`) slows the ledger by the same rule.

## Changelog

| Date | Change |
| --- | --- |
| 2026-09-05 | §12 added - the ledger speed model shipped as `pc-build-speed`: country modifiers read on the builder, state modifier on the state, infrastructure multiplier on every flagged type (was factories only, and the modifiers read 0 in state scope). |
| 2026-08-18 | Three citations corrected. `SUPPLY_FROM_DAMAGED_INFRA` was quoted as 0.01 from a WA line that writes it under the wrong category; the live value is vanilla's **0.15** (`NSupply`). `COMBAT_SUPPLY_LACK_IMPACT` does not exist in 1.19.2 - replaced by the four `COMBAT_SUPPLY_LACK_{ATTACKER,DEFENDER}_{ATTACK,DEFEND}` keys WA does override. `SUPPLY_PORT_LEVEL_THROUGHPUT` lives in `NBuildings`, and WA's dead `NCountry` write is gone; the 5/level ruling is unaffected. |
| 2026-08-17 | Created while designing corridor dimensioning. Rulings recorded: port flow is 5/level (not the `SUPPLY_PORT_LEVEL_THROUGHPUT = 3` define); hubs have no level; range and throughput are separate failure modes with separate levers; hub supply is additive. |
| 2026-08-18 | §11 SHIPPED as Fix 107. §11.11 added with the three deviations (no §11.3, break-even 20 not 12, presence index not a division count). Measured trigger: campaign `9d83084c`, every corridor hop at level 2 on all 121 saves. |
| 2026-08-17 | §11 added - corridor dimensioning design frozen. User rulings: build both rails and ports arbitrated by cost per supply point; no ratchet on the target; `supply_per_division = 2.5` as a calibration placeholder. |
