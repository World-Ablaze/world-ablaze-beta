# PC queue fairness — diagnosis of two defects from campaign `be18f9c7`

**Campaign:** `be18f9c7-9d55-456b-9264-78cbdddb67f0`, build `d683fb022`, 126 monthly saves
1936.2–1946.7. **Diagnosed and fixed:** 2026-08-14. **Fixes:** 77 (railway admission cap +
live-count skip gate), 78 (air-basing reservation lane).

Both defects were reported against the WA_AI Priority Construction system and turn out to
share one root cause: **the PC queue admits work without bound and allocates it winner-takes-most,
so a queue can hold an arbitrary amount of work that is never funded and never expires.** Defect A
is the low-priority band starving; Defect B is the high-priority band self-flooding. They are the
same failure seen from the two ends of the priority scale.

---

## 0. What the original reports got wrong, and why it matters

Three of the reported symptoms were artefacts of reading per-pulse or never-initialised
variables. Recording them because each one sent an analysis pass in the wrong direction, and
two of them had been open watch items for multiple campaigns.

| Reported | Actual |
| --- | --- |
| `dbg_best = -2` for 5 consecutive months = "deficit branch entered, NO buildable site found" | `dbg_best` is reset every ~2-day pulse and overwritten only on a queue. A monthly save shows **one pulse**. `dbg_started` advanced **+1 in every one of those five months** — the builder was working fine. `-2` was also the resting value of *both* "no deficit" and "deficit open, queued nothing". |
| GER 1944.6 "80 type-13 slots all at exactly stall 0" = queue-wide stall **reset** (open watch item, 4 campaigns) | `stall_weeks^id` **does not exist** for those slots. `WA_AI_PC_start_project` never initialises it; absent reads as 0. All 80 (province, connect) pairs were **new** — a mass enqueue, not a reset. **Watch item closed.** |
| Level-8 plateau = **state building-slot exhaustion** (air bases competing with ENG's arms factories) | `air_base` has its own `level_cap { state_max = 20 }` in `00_buildings.txt` — it does **not** draw on the shared state slot pool. Plateau states sat at 8 of 12 with slots free. |

A fourth, load-bearing in the other direction: **`wa_ai_pc_progress` holds *remaining* cost, not
work done.** `progress == project_cost == 800` means **zero work**, verified by
`build_time = progress / (assigned × 2.5)` holding exactly on every funded project. 62 of 66 GER
rails were untouched at 1944.8. Reading it as "complete" inverts the entire Defect B diagnosis.

Both lessons are recorded in `.claude/skills/wa-lessons-learned/references/lessons-log.md`.

---

## 1. Defect A — UK air bases delivered far too slowly

### 1.1 Hypotheses falsified against the saves

Measured on 33 state × save cells (1942.6 / 1943.5 / 1944.6) over the 11 hosting states:

- **No counter leak.** Every `wa_ai_pc_state_type_projects^2 > 0` is backed by a live type-2
  project in the ENG or USA queue targeting that exact state; every `= 0` has empty builder
  arrays. **Zero mismatches.** Fix 46's builder-agnostic counter is correct.
- **No cross-builder double-booking** at any sampled date (R8 probe 5 clean).
- **No slot exhaustion** — see §0.
- **No list drift** — `wa_tlm_r8_uk_air_fallback_n = 0` for both builders in all 30 months.

### 1.2 The actual mechanism: the host never funds its own air bases

ENG's `wa_ai_pc_air_factories_assigned` reads **0 in 20 of 30 months** across 1942.1–1944.6, with
every one of its type-2 projects at 0 factories and stall 3–12 weeks. `wa_ai_uk_air_dbg_started`
froze at **17 for nine straight months** (1943.7–1944.3).

The cause is priority-band arithmetic, not capability:

- ENG's queue is permanently railway-saturated at band **1000**; air bases sit at band **300**.
- `WA_AI_PC_assign_factories` fills **winner-takes-most** from the sorted top: each project takes
  `clamp(pool, 1, 20)`, so the head absorbs the pool and band-300 entries get nothing.
- The Fix 41 overtake lane is the only counterweight and serves **exactly one project per week
  across the entire queue**, so a starving air project waits 12+ weeks for a turn it then loses
  again the following week.

**The decisive control is in the data.** At 1943.5 — the single sampled month where ENG's rail
queue was nearly empty (one rail queued) — its air projects took **53 factories immediately**.
The civilian pool was never the constraint. USA, whose queue is not rail-saturated, funded its
air projects at a steady 20 civs each and placed 41 of the 54 orders.

### 1.3 The reported "ordering drift" is a consequence, not a second defect

ENG's mean queue rank 7.26 vs USA's 4.43: the south-first walk stops at the first **buildable**
state, and a state holding a live same-type project is not buildable (Fix 46, builder-agnostic).
ENG's top-ranked states each held a starving, never-completing project, so every pulse fell
through them into the unranked tail. **Fixing the funding fixes the ordering.** The rank list must
not be re-tuned for this — `fallback_n = 0` already proved it was never list drift.

### 1.4 Fix 78 — an air-basing reservation lane

`WA_AI_PC_assign_factories` gains a second lane, after the Fix 41 lane and before the sorted fill,
granting `min(20, pool)` to the highest-priority **live** band-300 type-2 project — only while the
country holds `WA_AI_PC_air_basing_reserve`.

Design choices, and why:

- **A reservation, not a band change.** Promoting air above rail would reopen the livelock the
  Fix 41 band table exists to prevent. One reserved 20-civ slot leaves band order intact for
  everything else.
- **Flag-gated and self-releasing.** `WA_AI_PC_air_basing_reserve` is a 30-day flag written *only*
  by `WA_AI_build_uk_air_hosting_capacity`'s deficit branch, so allocation returns to normal
  within a month of the target being met. No country that is not in an air-hosting deficit is
  affected at all.
- **Mirrors proven machinery.** Chain-latched selection (`_pc_air_lane_selected_`), per-pass
  re-grant, and a latched TLM counter — the same shape as the Fix 41 lane, including its re-entry
  contract (a re-entry resets all assignments; without the re-grant the reserved project would be
  silently stripped back to 0 and the week voided).
- **Same liveness tests as the fill**, including the Fix 34 controller test, so the reservation can
  never feed a project on hostile ground.

Also in Fix 78: `dbg_best` now pre-sets to **−1** inside the deficit branch, splitting the two
states that shared `-2`; and the legend in the strategy header records the per-pulse cadence.

---

## 2. Defect B — the railway queue collapse

### 2.1 What actually removed the projects

GER type-13 count: **80 (1944.6) → 66 → 45 → 24 → 2 (1945.2)**. Two mechanisms, cleanly separable:

- **Intermediate attrition (34 projects, 1944.6→1945.1) is NOT the stall sweep.** At each
  transition only a *subset* of projects sharing an identical stall value dies, and the dying
  subsets are tightly clustered by target state (68×3, 852×4, 39×4 + 853×3 + 159×3). A stall
  threshold cannot do that. This is ground changing hands.
- **The terminal collapse (20 projects, 1945.1→1945.2) IS the sweep**, and it was correct. All 20
  sat at `stall_weeks = 30` and died together as they ticked past `> 30`. **All 20 were on
  enemy-controlled ground** — SOV 11, FRA 5, YUG 4 — every one queued onto *friendly* ground at
  1944.6 and flipped by 1944.10.

**The sweep destroyed nothing valid.** The defect is that those projects sat dead in the queue for
**4–6 months** before the backstop reached them.

Note the reported "stall pinned at exactly 26" was a sampling coincidence of the monthly saves;
the constant is `constant:wa_ai_pc.alloc.stall_cancel_weeks = 30` (raised 25 → 30 by Fix 73 in the same commit),
and the cohort died at 30.

### 2.2 Why nothing noticed for 4–6 months

`@WA_AI_PC_railway_QUEUE_SKIP_THRESHOLD = 12` skips route recalculation **and**
`WA_AI_PC_railway_validate_queued_projects` whenever 12+ type-13 projects are queued — counting
**dead** projects toward that total. The dead cohort therefore kept switched off the very
mechanism that would have cancelled it, for the entire collapse.

`wa_tlm_pc_aging_reval_cancels` froze at 64 from 1944.11 for a related reason: the overtake lane
only revalidates projects the allocator actually walks, and it stops when the pool empties, so the
starved tail is unreachable by that path too. Over the whole collapse the two existing counters
moved by 14 against 54 removals.

### 2.3 The queue is a sawtooth, campaign-wide

The 1944.6 mass enqueue is one tooth of a five-year pattern (GER: +40 at 1942.6, +47 at 1942.12,
+20, +22, **+80 at 1944.6**, +30 at 1945.3; JAP identical, +85 at 1945.11), with the queue hitting
**0 type-13 for six months** in between. Throughout, **1–7 of up to 90** queued projects hold
factories at any moment. ~75 projects exist only to accumulate stall until something deletes them.

Root cause: `WA_AI_PC_start_railway_project` set `_project_queue_max = 0` — *no maximum* — the only
uncapped path into the PC queue. One recalculation queues every segment of up to 8 routes at once.

### 2.4 Fix 77 — cap admission, and count only live work

- **(a)** `_project_queue_max = @WA_AI_PC_railway_MAX_QUEUED` (12) in
  `WA_AI_PC_start_railway_project`. `WA_AI_PC_start_project` counts queued type-13 country-wide
  (unscoped `queued_amount_`), so this bounds the whole railway family across land-war, overseas
  and prewar strategies at once.
- **(b)** The skip gate counts only **live** type-13 — target state friendly-controlled, using the
  same Fix 34 controller test as the allocator fill and the completion path. A project those paths
  would refuse to fund or spawn does not count as a full queue.

The two 12s are deliberately equal ("a full queue is 12") and must change together: a cap below
the threshold can never fill; a cap above it re-grows past the bound.

**Throughput is not reduced.** The winner-takes-most allocator never funds more than ~pool/20
segments anyway. Segments not admitted this pulse are re-derived from the *current* front on the
next interval instead of rotting against a front that has moved.

---

## 3. Impact analysis

### 3.1 Fix 77 — callers and readers

| Symbol | Callers / readers | Effect of the change |
| --- | --- | --- |
| `WA_AI_PC_start_railway_project` | `WA_AI_PC_railway` (core, per path segment); railway strategies via the same path | Segments beyond 12 queued type-13 are declined instead of queued. |
| `_project_queue_max` | Read only by `WA_AI_PC_start_project`'s `while_loop_effect` guard | Set immediately before the call and consumed there; no other caller inherits it (each of the ~35 call sites sets its own, and the shared-temp trap is the documented reason they must). |
| `@WA_AI_PC_railway_QUEUE_SKIP_THRESHOLD` | Only the skip gate in `WA_AI_PC_railway` | Now compared against a live count. |
| `queued_type_num_` / `WA_AI_PC_get_total_queued_num` | Second call site in `WA_AI_PC_railway` (the override-flag block) sets both its own inputs | Unaffected — the removed first call did not feed it. |

**Who reaches it:** every AI country passing `WA_AI_PC_country_can_build_own_logistics` on the
weekly pulse — in practice majors and larger minors with 30+ civs at war (50+ at peace). Both parts
are archetype-free and tag-free; no CONFIG change is needed.

### 3.2 Fix 78 — callers and readers

| Symbol | Callers / readers | Effect of the change |
| --- | --- | --- |
| `WA_AI_PC_assign_factories` | Weekly on_action; mid-week completion re-entry; cleanup re-entry; stall-sweep re-call | One additional lane, skipped entirely when the flag is absent. |
| `WA_AI_PC_air_basing_reserve` (new flag) | Written only by `WA_AI_build_uk_air_hosting_capacity`'s deficit branch; read only by the new lane | New name, no collisions (grepped). |
| `WA_AI_PC_air_factories_assigned` | Read cross-country by both air-base builder gates | Now includes the reserved grant — this is the intended semantic (Fix 38's accumulator counts every air assignment). |
| `_pc_air_lane_proj_` | New chain temp; excluded from the main fill like `_pc_lane_proj_` | Cannot be double-assigned. |
| `WA_AI_uk_air_dbg_best` | Checklist R8 probes | Legend gains `-1`; **`-2` keeps its documented meaning**, so existing probes still read correctly. |

**Who reaches it:** only countries running the UK-hosting deficit branch — in practice **ENG and
USA**, the only two tags the strategy admits. Every other AI country in the game is bit-identical:
the flag is never set, the lane's selection block short-circuits on `has_country_flag`, and
`_pc_air_lane_proj_` stays −1.

### 3.3 Historical and ahistorical walk-through

**Fix 77 is setup-agnostic by construction** — it gates on queue depth and *current* controller,
never on date, tag or faction.

- *Historical:* GER 1944.6 queues 12 segments instead of 80. As the eastern front collapses, flipped
  states stop counting as live; the gate opens on the next weekly pulse, validation cancels the
  stale segments, and routes are recomputed against the real front. The 4–6 month dead window
  becomes ≤ 1 interval.
- *Ahistorical (GER never invades the USSR; ENG lands in Norway 1943):* identical behaviour. Route
  selection has always been driven by live enemy borders; the cap bounds how much of that output
  is admitted per pulse, and the live count is a controller test. A country at peace queues its
  prewar routes to the same cap and drains them at the same rate.
- *Edge case — a country that loses ground faster than it can validate:* the first pulse after a
  mass flip validates-and-cancels but queues nothing new (the admission cap still counts all
  type-13, dead included). Fresh segments follow one interval later. This is deliberate: it
  prevents queueing new routes across ground that is still changing hands.

**Fix 78** is gated on a dynamic capability/deficit test, not on a date or on the Allies existing.

- *Historical:* ENG holds the flag from the first UK hosting deficit; its air projects get one
  funded slot per week alongside the rail head; `dbg_started` keeps climbing; the south-first walk
  reaches states 857/127/961 because completed projects free them.
- *Ahistorical (ENG fascist, or the USA never joins; a faction other than the Allies holds
  Britain):* the strategy's own gate (`has_war`, an enemy with a European capital, ENG-or-USA-in-
  faction-with-ENG) decides whether anyone runs the deficit branch at all — **unchanged by this
  fix**. If nobody does, the flag is never set and the lane never exists. If ENG runs it in a
  different faction, the lane behaves identically; nothing in it references the Allies, a date, or
  D-Day.
- *Edge case — deficit closes while a project is mid-build:* the flag expires within 30 days, the
  lane stops selecting, and the project reverts to the ordinary sorted fill (it keeps its progress).
- *Edge case — ENG capitulates:* `assign_factories` is unchanged in that respect; the lane's
  liveness and controller tests refuse projects on lost ground exactly as the fill does.

### 3.4 Regression risk — stated explicitly

**Fix 77.**
1. *Rail throughput could fall if the cap is too tight.* Judged low: only 1–7 segments were ever
   funded simultaneously in five years of campaign data, so a 12-deep queue is ~2× the observed
   working set. **Probe 4 measures exactly this** (world rail levels must keep growing;
   `wa_tlm_pc_built_by_type^13` non-zero for majors). Mitigation if it bites: raise **both** 12s.
2. *More frequent recalculation costs CPU.* The gate now opens more often, so pathfinding runs more
   often — up to once per interval per eligible country instead of being suppressed for months.
   This is the intended behaviour restored, and it is bounded by the unchanged
   `@WA_AI_PC_railway_MAX_ROUTES_TOTAL = 8`. The new live-count loop is O(queue) on a weekly
   cadence, negligible beside the existing sorting and progress loops.
3. *The live-count controller test runs per queued project per week.* Same shape and cost as the
   Fix 34 test already in the allocator fill, on the same cadence.
4. *Interaction with `on_peace`'s type-13 purge and Fix 5/19:* unchanged — that path ends projects
   and resets the interval counter, and a capped queue simply gives it less to purge.

**Fix 78.**
1. *Rail could be starved by the reservation.* At most one 20-civ slot, and only while an air
   deficit stands on ENG/USA. ENG's rail head keeps the remainder of the pool. **Probe 4 measures
   this**; mitigation is to cap the reservation below 20, not to remove the lane.
2. *Refineries could lose their turn.* The band-250 refineries already lose to band-300 air bases
   whenever the deficit stands (accepted and documented under Fix 75). The reservation does not
   change their relative order; it changes whether the air project that already outranks them
   actually gets funded. R8's Fix 75 probe 3 continues to score refinery liveness, and R25 is
   unaffected.
3. *Double-assignment.* Prevented by the explicit exclusion in the main fill, mirroring Fix 41.
4. *The `-1` sentinel could confuse existing probes.* `-2` retains its exact documented meaning,
   so probes testing `-2` (R8's Fix 75 probe 1) are unaffected; probes reading "negative" as a
   single class gain resolution rather than losing it.
5. *Two lanes could jointly divert 40 civs.* Bounded and intended: the Fix 41 lane is the
   anti-starvation floor for *any* band, the Fix 78 lane for air specifically, and both clamp at
   20 and at the remaining pool. On a country with a 40-civ PC pool this is the whole pool for one
   week — which is the same exposure the Fix 41 lane alone already had, and it self-releases.

---

## 4. Telemetry and verification

New in **WA_TLM v15** (registry rows in `documentation/WA_TLM_TELEMETRY_SYSTEM.md` §5):

| Metric | Kind | Site | Consumer |
| --- | --- | --- | --- |
| `WA_TLM_r8_air_lane_grants` | counter (funded **weeks**, chain-latched) | the Fix 78 grant in `WA_AI_PC_assign_factories` | R8 Fix-78 leg |
| `WA_TLM_r8_air_lane_last_t` | stamp | same site | R8 Fix-78 leg |

It counts weeks rather than factories on purpose: the existing snapshot gauge
`wa_ai_pc_air_factories_assigned` under-samples at monthly cadence — `be18f9c7` read ENG 0 in 20 of
30 months while any funding that did occur fell between saves. A cumulative counter cannot be
missed. Both are written only on verified effect (the `set_variable` granting ≥ 1 factory).

Fix 77 needs **no new instrumentation**: the v14 termination ledger (`pc_stale_n`, `pc_sweep_n`,
`pc_built_by_type^13`) already distinguishes every removal path, which is precisely what this
campaign lacked — GER's save carried `wa_tlm_version = 11`, so the ledger was a **probe void**, not
a zero, and the 54-project collapse was unattributable by design.

Checklist probes added in the same session: **R8** gains a Fix 78 leg (4 probes, retirement after
2 campaigns) plus recuts of the two stale metric notes; **R19** gains a Fix 77 leg (4 probes,
retirement after 2 campaigns), closes the four-campaign "synchronised stall counter" watch item,
and gains the dead-tag caveat.
