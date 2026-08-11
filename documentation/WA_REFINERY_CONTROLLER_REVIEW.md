# Refinery activation controller — architecture review

**Date:** 2026-08-11 · **Status:** review only, no fix implemented · **Evidence:** campaign `911bed3c`, checklist item R29, git history back to the 2020 initial import.

This reviews the mechanism that switches refineries between their active and `*_inactive` forms in response to input-resource availability. It states the functional need, compares it against what is built, names the weaknesses and the blind spots, and derives the controller that follows. **§1 is the part to read** — the need was clarified by the maintainer after the first draft and it inverts most of the conclusions an outside reading would reach.

---

## 1. The functional need — a bid/verdict protocol

**The deficit is a bid, not an emergency.** Iron and bauxite are modded resources with no direct engine consumer, so the AI's trade engine only imports them once the balance is deep enough to register. The controller therefore *deliberately* opens a refinery to create that depth, and then waits to see whether the market answers.

### 1.1 The protocol

| Step | What happens |
| --- | --- |
| **Bid** | open one inactive refinery — the balance falls by **Z** |
| **Verdict window** | hold the bid open for **D** days |
| **Accepted** | an import route commits, the balance recovers → **keep** the refinery and bid again |
| **Refused** | no import within D → **close** it, retreat, retry later |

**One outstanding bid at a time.** That single rule does the work a deadband would otherwise have to do: it bounds the deficit to `X + Z` by construction, and it bounds the tolerated unfunded production to exactly one refinery. It also removes any need to size a band on the worst-case variant — Z is simply the size of the bid being made.

Two consequences that invert an outside reading of the code:

- **The open/close cycling is the mechanism, not a failure.** A country that cycles repeatedly is one whose bids keep being **refused**. ENG's 23 cycles over 19 months are 23 refused bids, not 23 malfunctions.
- **The equilibrium is a ratchet, not a resting point.** Each accepted bid converts one spare civilian factory into one permanently-running refinery. The country climbs until it runs out of factories to commit, then keeps bidding and being refused — which is cheap and harmless.

### 1.2 Z is one civilian factory of trade — deliberately

`common/resources/00_resources.txt` gives `cic`, the civ-factory cost per unit imported; its inverse is what one factory buys:

| Resource | `cic` | units per civ factory | one refinery consumes |
| --- | --- | --- | --- |
| **bauxite** | 0.03125 | **32** | `aluminium_refinery` = **32** (hydro 35) |
| **iron** | 0.04 | **25** | `steel_refinery` = **25** (hydro 25) |
| coal | 0.010 | 100 | `synthetic_refinery` = 60 |

The alignment is explicit in the commit that set it — `29f2c1d59`: *"bauxite trade is 32 for 1 civ, alum mils use 32 bauxite"*. **A bid is therefore exactly a request for one more civilian factory on a trade route.** That is what makes the protocol legible: the controller is not tuning a balance, it is asking a yes/no question whose unit is a factory.

**X**, the depth at which the AI actually imports, has a principled lower bound: **one quantum**. A deficit shallower than a whole factory's purchase has no purchase that fills it. ENG sat at **−30 for 19 months — 94% of one quantum** — which is exactly the dead zone this bound excludes.

### 1.3 The current code already implements this protocol

This matters, because it narrows the fix enormously:

- the mission's `available` (`resource@bauxite > -25`) **is the acceptance test** — it self-cancels the moment the market answers;
- `days_mission_timeout = 9` **is the verdict window D**;
- the timeout closure **is the retreat**.

So the architecture is right and the parameters are suspect. The one clear structural error left is the **reopen gate** (`> -1`): it asks *"is the deficit cleared?"* when the question is *"is there room to place a bid?"*.

**The prime suspect is the reopen gate — and the campaign data already convicts it.**

Under a working protocol ENG should have spent much of its time *below* one quantum of deficit, with roughly 7 of 19 monthly snapshots catching an open bid. **Zero did.** The balance stayed between −26 and −33 at every one of the 19 readings, and `produced` was **exactly −137** each time — i.e. an identical park (1 plain mill at 32 + 3 hydro at 105) on every 1st of the month. Missing a ~9-day window in a ~25-day cycle 19 times running has a probability around 3×10⁻⁴.

So ENG never bid. The arithmetic reconstructs what actually happened:

1. `Y ≈ -30`, the mission is armed and counting down
2. day 9: timeout closes the plain mill → **+32** → `Y ≈ +2`
3. the reopen gate `> -1` is finally satisfied → the decision (`ai_will_do 4000`, `cost 0`) reopens **the same mill** within hours → `Y ≈ -30`
4. ~14-day re-enable cooldown, repeat

The mill is off for hours, which is why no snapshot ever caught it, and the balance oscillates between −30 and +2 — **never leaving the 0-to-32 band**.

**The cause is `resource@bauxite > -1`.** It demands the deficit be *erased* before reopening, so the country can never hold more than **one** quantum of deficit — while bidding requires **two**: the standing deficit plus the bid. The gate makes the auction structurally impossible. The bids were not refused; they were never placed, so D was never tested.

Consequently the "self-concealing signal" of §3.2 is **not an independent defect either** — the deficit never deepens in the first place.

**Falsifiable test, no new instrumentation needed:** a healthy country should never sit in the 0-to-one-quantum deficit band longer than the retry gap (~14 days), because that state *is* the order to bid. `produced` holding constant across consecutive monthly saves is sufficient evidence that no bid was ever held — it encodes the park configuration.

### 1.4 Why the mechanic must exist at all

**WA runs a two-tier resource economy that the engine has no support for, and this controller is the only thing that enforces it.**

| Tier | Resources | Declared by equipment |
| --- | --- | --- |
| **Processed** — what equipment burns | steel **2630**, tungsten **1702**, chromium **1291**, aluminium **1115**, coal **1075**, rubber **831** | yes, heavily |
| **Raw** — what refineries burn | **iron 1**, **bauxite 1** | only `trade_fix_equipment_0` (`ship_hull_heavy.txt:693-719`), a dummy at `build_cost_ic = 99999999` that exists purely to make the resource visible to the trade AI |

Iron and bauxite are never consumed by anything a country builds; they exist to feed the refineries. The engine has **no concept of a building that cannot run without its input** — `PRODUCTION_RESOURCE_LACK_PENALTY` only penalises production lines whose equipment declares the missing resource, and none declares iron or bauxite. An engine-only WA would run every refinery at full rate regardless of ore, and the raw tier would be decorative.

> **Correction to an earlier draft.** The first version read "only a dummy declares iron/bauxite" as evidence those deficits are harmless, and proposed retiring the mechanic. That inverted the meaning: a raw tier is *by definition* never declared by end products. The error was asking "what consumes iron?" and stopping, instead of "what does iron enable?".

**Accepted trade-off:** because nothing penalises an unfilled raw deficit, a refinery running on an unfunded bid produces its output anyway. One refinery's worth of that is the deliberate price of getting the AI to trade at all, and the one-bid-at-a-time rule is what caps it.

### 1.5 Coal is a different controller, with the opposite goal

`common/defines/05_defines.lua:184-193` sets `BASE_FACTORY_SPEED = 0.0` (vanilla 4.0) against `POWERED_FACTORY_SPEED = 2.5`: an unpowered factory in WA produces **literally zero**. Coal is the energy resource, an input at every refinery tier, and declared by 1075 equipment lines.

**Coal must have its deficit cleared, never held.** No bidding, no tolerated shortfall. It also breaks the quantum alignment (100 per factory vs 60 per refinery), so the protocol above does not transfer. The current code applies one clear-the-deficit shape to all three resources — correct for coal, wrong for the other two.

### 1.6 What this means for the ENG case

ENG closing 12 aluminium mills in 1944 was **correct**: it genuinely lacked bauxite. Its 3 hydro mills staying on was a defect (Fix 43, §3.3). Its 23 refused bids were the protocol working. The failure is that **no bid was ever accepted** despite money and supply both being available — which points at D, not at the controller's shape.

### 1.7 Vanilla has no equivalent, and that is expected

`refinery = yes`, `local_resources_*` and `country_resource_cost_*` are vanilla engine keys, but the combination is WA's: vanilla's `synthetic_refinery` creates rubber and consumes nothing, so vanilla has no raw tier to enforce and no building with an `_inactive` twin. Vanilla's `BUILD_REFINERY_LACK_OF_RESOURCE_MODIFIER` (build *more* on shortage) is coherent for a one-tier economy and does not address WA's question.

## 2. What is built

Three layers, added over four years, never unified:

| Layer | Added | Mechanism | Who it serves |
| --- | --- | --- | --- |
| Shortage missions | 2020 (pre-VCS) | `*_shortage` in `common/decisions/_economy_fatigue.txt`, 9-day timeout, `while_loop_effect` closure | player — **but `activation` carries `always = no`, so the iron/bauxite/coal player missions are permanently disabled** |
| AI mission + decision pair | 2021-10-10 `5b1390ff1` | `*_shortage_ai` (close, `-26`/`-61` deadband) + `reactivate_*_ai` (open, `> -1`) | AI |
| GUI + `manage_*` | 2024-05→09 (Lailatova) | `open_*_target` setpoint, weekly `is_ai = no` reconciliation, Refresh button | player |

Underneath: ten `enable_/disable_*` primitives (`WA_scripted_effects.txt:6688-6806`) and a fourth writer nobody coordinates with — `on_state_control_changed` (`100_wa_on_actions.txt:2493-2530`), which closes **everything** in a newly-controlled non-core state, unconditionally, updating no counter. It is the origin of every hydro-inactive level in the campaign.

**Five writers of the mill on/off state, no dispatcher and no owner.**

---

## 3. Weaknesses

### 3.1 The control loop is not a control loop

> **Reframed by §1 — read that first.** This section was written before the functional need was stated, and it treats the open/close cycling as pathological churn. It is not: cycling is the **bidding mechanism** (§1.1), and the measurements below are better read as *23 refused bids* than as 23 malfunctions. What survives the reframing is the arithmetic — the reopen gate asks the wrong question, and the verdict window may be too short. What does **not** survive is the implied remedy of damping the oscillation.


| Property | State |
| --- | --- |
| Setpoints overlap? | **No.** Shutdown stops at `≥ -26` (bauxite/iron) or `≥ -61` (coal); restart needs `> -1`. `[-26, -1]` is a band where neither controller acts. |
| Real hysteresis? | **No.** Shutdown band is 1 unit wide (bang-bang, over-shooting by a full 32/60 per closure); restart is a single threshold with nothing on the other side. |
| Shared state between the two arms? | **None.** Two mechanisms, no common variable, no cooldown, no target. |
| Release reachable by the action? | **No.** The AI trade engine imports only to reach ~0 at the current instant; it never accumulates. A gate demanding surplus is unreachable by construction — and `> -1` is *self-defeating*, since opening a mill costs 32-35 immediately. |

Measured consequence (`911bed3c`, ENG 1944.10→1946.4): 23 consecutive cycles of ~25 days (9-day mission + ~14-day cooldown), restart and shutdown counters advancing **+23 / +23 in exact lockstep**, refinery levels **completely flat**. Flapping, not deadlock. Across nine snapshots landing inside a live 9-day mission window the balance never once crossed the −25 cancel bar.

### 3.2 The signal erases itself

> **Reframed by §1.3.** Under the bid/verdict model this is very likely a *symptom*, not an independent defect: the deficit disappears because the bid is withdrawn after 9 days, not because the detector is badly built. If the D measurement (§5.2) confirms the window is too short, this section needs no separate fix. The measured numbers below stand either way.


`*_inactive` twins carry **no production and no consumption**. So when the controller acts, both legs of the AI's need detector move the *wrong way*: `resource@X` rises toward zero, and `resource_imported@X` falls because the engine stops buying. The ratio detector (`deficit > 5% of need`, `WA_AI_misc_effects.txt:262-479`) is worse — it divides by `resource_consumed@X`, which the shutdown also shrinks, so numerator and denominator collapse together. Measured on ENG at 1944.4: 489 consumed, −14.2 balance, ratio **0.028 < 0.05** ⇒ `wa_ai_bauxite_resource_shortage = 0` while the country was dismantling its aluminium industry.

### 3.3 The mission cannot reach half its own park

All four shortage loops close **plain variants only**; all four reactivate decisions **prefer hydro**. Combined with the surplus gates on the `close_*` family, the exact statement is: **no AI path can close a hydro refinery while the country is in an input deficit** — precisely when it needs to. On ENG, 3 hydro aluminium levels ran throughout, consuming 105 bauxite, while the mission re-armed every 9 days for ~21 months and closed nothing. **One hydro closure would have freed 35 bauxite and cleared the deficit outright.**

Steel is immune for an arithmetic reason (reopen costs exactly 25, leaving ≥ −25; the mission activates at ≤ −27) — do not "fix" its ordering.

### 3.4 Constants duplicated six ways, with a documented drift history

PDXScript cannot read a building's `country_resource_cost_*` back, so every consumer hard-codes its own copy: the six shortage missions, `manage_*`'s pre-charge/patch scheme, `calculate_resource_deficite`, the reopen ladders, and the localisation prose. **Two commits changed a cost without touching any dependent script** — `08dca0fa8` (2022-11-13, bauxite 25→35) and `29f2c1d59` (2025-07-05, 35→32) — plus a 2021 loc-only edit. At HEAD, **none of the four aluminium sites agreed**: building 32/20, closure scripts 25/15, tooltip 35/15, reopen ladder 35.

Fix 42 (this session) reconciled the missions, `manage_alu_mills` and the tooltip, and installed a sync header at `common/buildings/00_buildings.txt` listing every copy site. The ladders and `calculate_resource_deficite`'s bauxite-35 remain unreconciled by choice.

### 3.5 Structural debt found in the responsibility map

- **Write-only variables:** `WA_AI_{coal,bauxite,iron}_resource_shortage` are computed every ~2 days for every AI country and read by **nothing** — and they are exactly the three refinery inputs.
- **Read-but-never-written:** `WA_AI_resource_{coal,oil,iron,tungsten,chromium,bauxite}_shortage_months` — 6 of 9 reactive prospecting triggers run on a permanently-false OR-leg.
- **Naming defect:** `_shortage_months` ticks on a ~2-day event, so `= 3` means **~6 days**, not 3 months. Three files carry comments asserting a monthly cadence.
- **Cadence mismatch:** `WA_AI_industry_overextended_flag` is evaluated **monthly** from inputs that saturate 0→3 in ~6 days — its hysteresis band is sampled at 1/15th the rate of its own signal.
- **Namespace collision:** `WA_AI_allies_need_*` exists both as country flags (written, never read) and as scripted triggers of the *same names* that re-derive the answer per call, with different semantics.
- **Dead code:** `reactivate_steel_refineries` has `is_ai = no` and `is_ai = yes` as siblings (never visible); `close_*_occupied_all` have `ai_will_do = { base = 0 }` and no caller.
- **21 hardcoded tag gates** in this domain and **zero** resource archetypes in `WA_AI_CONFIG.txt`. The recurring question — *"am I import-dependent on resource R from a supplier I am not at war with?"* — is hand-written four times as GER/SWE and GER/HUN pairs.

### 3.6 Layer placement against the repo's own doctrine

Every other `WA_AI_*` system has `_core` dispatch, `_strategies` behaviour, `_helpers` calculations, `_primitives`, and behavioural switches in a dedicated triggers file on a declared pulse. This system has **no core**, its switches inline in decision `available`/`ai_will_do` blocks, and **no on_action registration at all** — the AI cadence is engine decision evaluation, so you cannot determine it by reading any on_action. Two reactivation decisions are hand-unrolled 20-rung `else_if` ladders of ~417 lines each; ~830 lines expressing what a `meta_trigger` would say in eight.

---

## 4. Blind spots

**The one that matters:** *no AI-path controller in this repo derives a resource signal from installed or intended capacity.* Every AI input — `resource@X`, `resource_consumed@X`, `resource_imported@X`, the 0-3 bands, the 5% ratio — is **realised flow**, which is exactly the quantity the controller's own action changes. Self-concealment is therefore structural, not a bug in one predicate.

The capability exists in the codebase but has never been wired to an AI controller:
- `calculate_resource_deficite` (`WA_scripted_effects.txt:7773-7788`) computes `need_coal = (open_synth_target − current_synth) × 60 − current_coal` — demand from *intended* capacity, priced at the building cost. **Player-only, and a display projection, not a control input.**
- `WA_AI_calculate_fielded_eq_ratio` (`WA_AI_misc_effects.txt:227-257`) divides by `num_target_equipment_in_armies_k@X` — an establishment figure the action cannot move. This is *why* the 0.6/0.9 posture band works as a release condition.
- `WA_AI_calculate_fuel_need` (`:722-767`) estimates from force structure, not from burn.

**Secondary blind spots:**
- **Zero `WA_TLM_*` probes** anywhere in the resource economy, including for shipped Fixes 41 and 42 — against the checklist's own rule that every fix ships with a probe.
- **No variable, trigger or metric anywhere exposes "N of my refineries are off for want of input."** For AI countries the counter family (`total_*`, `current_*`, `open_*_target`) is frozen at its 1936 startup values, because the only refresh path is gated `is_ai = no`. `open_*_target` — the single variable in the whole system that expresses *intent* — has **no AI writer at all**.
- **The analyst is blind too.** Seeing this required a hand-rolled scan of the `states={}` block; `savegame.py` has no command for it. A self-concealing failure cannot be verified by the metric it conceals itself from.

---

## 5. The design that follows

§1 fixes the functional need and §1.3 shows the existing architecture already implements it. So this is **not a rebuild** — it is a parameter correction plus one gate that asks the wrong question.

### 5.1 The controller

Per raw resource (iron, bauxite — **not coal**), on a declared pulse:

```
Y = resource@<raw>                     # signed balance, negative in deficit
Z = cost of the variant being toggled  # bauxite 32 plain / 35 hydro; iron 25 both

if no bid outstanding and Y > X:
        open one inactive refinery          # place the bid
        arm a verdict timer for D days
if bid outstanding:
        if Y recovered above the acceptance bar   -> accept: clear the bid, keep the mill
        else if D elapsed                          -> refuse: close that mill, back off
if Y < FLOOR:                                      # external collapse, not a bid
        close mills until Y >= FLOOR
```

Three things this shape gets that the current pair does not: **one bid at a time** (bounds both the deficit and the unfunded output to one refinery), **an explicit verdict timer** rather than a mission timeout that doubles as an emergency, and a **separate FLOOR arm** for the case the balance collapses for external reasons — ENG lost every bauxite route for three months in 1944, which is not a bid being refused and should not be handled by the bid logic.

State must persist across ticks (which bid is outstanding, how long it has been open), so this is a scripted effect on a weekly pulse in the P1/P2 style, not a decision. A decision's `ai_will_do` cannot remember it already acted — the reason the current pair has no notion of an outstanding bid at all.

### 5.2 Parameters — and which one to measure first

| Symbol | Meaning | Status |
| --- | --- | --- |
| **D** | verdict window: how long a bid stays open | currently 9 days. **Untested** — no bid was ever placed, so its adequacy is unknown. Measure after Fix 44. |
| **X** | depth at which the AI actually imports | **set to one quantum by Fix 44** (32 bauxite / 25 iron). Was `> -1`, which asked the wrong question. Whether it needs margin above one quantum is still empirical. |
| **Z** | bid size | read per variant. No band sizing needed — the one-bid rule bounds depth. |
| **FLOOR** | external-collapse threshold | does not exist today; the shutdown loop serves both roles. |
| retry gap | how long before re-bidding after a refusal | currently ~14 days of re-enable cooldown, giving a ~25-day cycle. Cheap; probably fine. |

**What Fix 44 changed (shipped 2026-08-11):** the reopen gates became `resource@iron > -25` / `resource@bauxite > -32` — bid room instead of deficit-cleared — and the bauxite mission's thresholds were re-derived from bauxite's own quantum (arm `< -33`, cancel `> -32`) instead of carrying iron's numbers. Iron's `-26 / -25` were already correct for its quantum of 25, which is why steel never exhibited the pathology. The same re-derivation also fixes a double-close: at −62 the loop now credits +32 to −30, exits, and closes **one** mill; under the old −26 it iterated again and closed **two**.

**The measurement that comes next:** with bids now possible, watch whether a bid is ever *accepted* — i.e. whether `imported@bauxite` rises during the verdict window. Only then does D become the live question.

### 5.2a The bid and the retreat must be the same size (Fix 45, shipped 2026-08-11)

A consequence of §1.1's *"Z is simply the size of the bid being made"* that the
implementation did not honour. The reopen decision prefers **hydro** (35 bauxite, no
coal); the retreat loop closes **plain** first (32 bauxite). So a hydro bid came back
3 bauxite short of where it started, and repetition walked the balance into
**[−33, −32]** — below the reopen gate and above the mission's arm, **a band where
neither arm acts**. Each cycle also swapped an active plain mill for a hydro one at
zero change in aluminium output, so it was churn as well as drift.

**Fix 45:** the reopen records which variant it opened (`WA_AI_bauxite_bid_hydro`,
written on every branch so it is never stale); the retreat reads it once, clears it,
and closes that variant first. Cost equals credit exactly, and the coal-sparing hydro
preference is kept. The marker steers only the **first** closure of a pass — an
external collapse closing several mills is not a refused bid (§5.1's FLOOR case, still
unbuilt) and must not be steered by one.

Iron needs none of this: `hydro_steel_refinery` costs the same 25 iron as plain, so its
bid and retreat already cancel — the third appearance of the one-axis/two-axis
asymmetry that also produced Fix 42. **Do not mirror Fix 45 to the steel loops.**

Three alternatives were rejected and are recorded so they are not re-proposed: moving
the mission arm to `< -32` closes the band but makes a hydro bid close **two** mills;
reordering the reopen to plain-first equalises the sizes but spends 20 coal per bid
where hydro spends none, against §1.5; and widening the gate to `> -35` cannot work at
all, because a 3-unit mismatch between a 35-cost bid and a 32-credit retreat is not
expressible in fixed thresholds.

`WA_AI_bauxite_bid_hydro` is control state, not telemetry — it is read by gameplay
logic, so it is deliberately **not** a `WA_TLM_` name. It is nonetheless save-visible
(`wa_ai_bauxite_bid_hydro`), which is what makes R29's Fix 45 sub-probe free, and it is
the first piece of the persistent outstanding-bid bookkeeping §5.1 calls for.

### 5.3 Variant choice should follow the scarcer input

`aluminium_refinery` costs 32 bauxite + 20 coal; `hydro_aluminium_refinery` costs 35 bauxite + **no coal**. So when coal is tight, hydro is the correct mill to open, and when bauxite is tight, plain is. The current fixed preference (hydro first on reopen, plain first on close) encodes neither. Note also that opening any plain mill spends 20 coal — the bid arm needs a **real coal guard**, since coal is the opposite controller (§1.5) and its deficit is catastrophic.

### 5.4 Coal keeps the existing shape

`coal_shortage_ai` stays a clear-the-deficit emergency brake. No bidding, no tolerated shortfall, no band.

### 5.5 Build order

1. **Measure D** (§5.2). Everything below is conditional on it.
2. **Instrument** — a `WA_TLM_` metric for active-vs-inactive levels per family, plus `savegame.py buildings`, so bids and their verdicts are visible in a campaign. *(The `savegame.py` half is already scoped as a separate task.)*
3. **Fix 43 — done.** Both variants are now closable (§3.3), so a country holding only hydro mills is no longer stuck.
4. **Correct the parameters**: ~~the reopen gate from `> -1` to a bid-room test at X~~ — **done, Fix 44**; ~~make the retreat the same size as the bid~~ — **done, Fix 45 (§5.2a)**; still open: **D** from the measurement, and **split FLOOR out of the shutdown loop** (an external collapse is not a refused bid and currently runs through the bid logic).
5. **Then** revisit variant choice (§5.3) and the coal guard.

### 5.6 Recorded as withdrawn

**O1 — retire the iron/bauxite arms.** An earlier draft proposed deleting the machinery because those deficits carry no engine penalty. §1.4 shows why that is destructive: without the enforcement layer, refineries produce steel and aluminium regardless of ore and WA's raw tier becomes decorative. Recorded so the same grep does not lead someone back to it.

**Also withdrawn: the "rebuild as a band controller" proposal.** It assumed the open/close cycling was pathological churn to be damped. It is the bidding mechanism (§1.1); damping it would remove the only thing that ever triggers an import.

---

## 6. Open questions

1. **What is the engine's route-commit latency?** The one measurement that decides the rest. If it exceeds the 9-day verdict window, D alone condemns every bid and is the entire fix. Minutes in-game: open a refinery on a live save, watch when `imported@bauxite` moves.
2. **What is X?** Lower bound is one trade quantum (32 bauxite / 25 iron), because a shallower deficit has no whole-factory purchase that fills it. Whether it needs margin above that is empirical.
3. **Does X scale with country size?** The engine's want term is absolute, but converting want into a purchase costs a whole civilian factory, so a small economy may need a proportionally deeper bid. Unmeasured.
4. **What should FLOOR be, and should it close more than one mill at a time?** ENG lost every bauxite route for three months in 1944 — an external collapse, not a refused bid. That case needs its own arm (§5.1) and its own threshold.
5. **Should the player and AI paths be unified?** They are the same system split by `is_ai`, and neither half is complete: the AI has decisions with no bookkeeping, the player has bookkeeping wired only to a GUI. The player half already computes demand from *intended* capacity (`calculate_resource_deficite`) — the one calculation the AI path lacks.
