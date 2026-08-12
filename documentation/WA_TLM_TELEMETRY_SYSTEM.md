# WA_TLM — Save-visible telemetry for AI systems

Status: **design + pilot** (2026-08-11). Owner files: `common/scripted_effects/WA_TLM_core.txt`,
`common/on_actions/WA_AI_startup_on_actions.txt` (init), `common/on_actions/WA_AI_misc_on_actions.txt` (monthly pulse).
Retrieval side: `.claude/skills/wa-savegame-analysis/scripts/savegame.py` (`tlm` subcommand).
Consumer protocol: `.claude/skills/wa-campaign-checklist/SKILL.md`.

## 1. Why this exists

The project's feedback loop is: cloud test campaign → savegame analysis by agents →
fix commits → checklist probes → next campaign. Savegames are the **only** reliable
evidence channel for cloud runs (local logs prove nothing — see
`wa-lessons-learned`, "Test campaigns run on a dedicated cloud machine"). Every fix
therefore ships with a save-visible probe.

Until now that instrumentation was ad hoc: per-fix `*_dbg_*` variable families with
heterogeneous names, types, and lifecycles. Four failure modes are already on record:

1. **Stamps over-affirm.** A `fire_only_once` stamp proves the gate held *once*, not
   that the behaviour persisted (R13: both stamps set, zero front movement for 31 months).
2. **Counters over-count.** `wa_ai_thair_dbg_started` incremented even when
   `WA_AI_PC_start_project` declined internally — attempts counted as actions
   (fixed post-live-test with a queue-growth check).
3. **Absent is ambiguous.** An absent variable can mean "build lacks the
   instrumentation", "country never reached the code path", or "code path reached,
   action count zero" — and `check_variable` reads absent as 0, so probes and brakes
   both misfire (see the `has_variable` brake lesson).
4. **No time series.** Saves are monthly snapshots; weekly gauges are overwritten
   between saves. Reconstructing a trend costs a full streaming parse of 8–15 saves
   × ~100 MB each, per question.

WA_TLM standardises the namespace, the data types, the write discipline, and the
retrieval path so that agents can pull a country's telemetry with **one regex on one
or two saves** and trust what they read.

## 2. Inventory of pre-TLM instrumentation (audit 2026-08-11)

Save-visible persistent families (grep `_dbg_` across `common/` and `events/`):

| Family | Writer(s) | Types used | Cadence | Consumer | Status |
| --- | --- | --- | --- | --- | --- |
| `WA_AI_uk_air_dbg_{called,planes,capacity,best,started}` | `WA_AI_CONSTRUCTION_PRIORITY_strategies.txt:892-1062` | counters + gauges (unstamped) | weekly PC pulse | R8, R23 | live; retire with items |
| `WA_AI_thair_dbg_{called,target,active,best,started}` | same file `:1130-1392` | counters + gauges | weekly PC pulse | R16 | live; over-count bug fixed; "retire with item" noted in code |
| `WA_AI_supply_line_dbg_{called,pf_ok,queued,last_state}` | same file `:489-590` | counters + gauge | weekly PC pulse | R9 | live |
| `WA_AI_invasions_dbg_{adds,removes,active}` | `events/WA_AI_invasions.txt`, `WA_AI_DIVISION_CREATOR_effects.txt:2304`, `WA_AI_MIGRATION_effects.txt` | counters + gauge | event-driven | **R14 — RETIRED 2026-08-12** (streak 3/3 on `9a4cd657`) | **consumer gone; disposition owed.** Split verdict under §3.8: `_adds`/`_removes` are pure probes → delete; `_active` was used beyond R14 (the stranded-invasions finding, `wa-lessons-learned/references/lessons-log.md:469`) → **promote** to a standing `WA_TLM_invasion_active` gauge with its own row. Deferred until after the Fixes 46-49 validation campaign so the edit does not risk the invasion system mid-cycle. Caveat while it lives: **migration deliberately falsifies adds−removes** |
| `wa_ai_ita_dbg_r13_{na_front,na_offensive}` (+`_r13` scratch) | `events/WA_AI_ITA.txt:188-253` | one-shot stamps | fire_only_once | R13 | live but **inadequate** — R13 explicitly asks for weekly counters to replace them |
| `WA_AI_overext_dbg_{active,mic_redirects_refinery,mic_redirects_cic}` | `WA_AI_misc_effects.txt:661-718`, `WA_AI_CONSTRUCTION_queue_functions.txt:113-155` | counters | monthly / on queue call | **none yet** (fix in flight, uncommitted) | needs its checklist probe at commit time |

Fingerprints *outside* the `_dbg_` convention (found only by knowing where to look —
exactly the discoverability problem TLM removes):

| Name | Writer | Consumer | Note |
| --- | --- | --- | --- |
| `wa_warbonds_retry_upgrades` | `common/decisions/_economy_fatigue.txt:3156` | R20 | no prefix, invisible to a `_dbg_` grep |
| `global.WA_AI_invasions_migration_1_purged` | `WA_AI_MIGRATION_effects.txt:168` | R14 sub-probe | **global** — serializes near line ~4.96M of the save; a truncated scan misses it |
| `AIFC-DIAG` log lines | `WA_AI_AIFC_core.txt:85,132`, `WA_AI_AIFC_helpers.txt:260,625,631` | R1 (local runs only) | log-based, useless on cloud saves; `:625` carries a "do not commit" comment that was committed — retire with R1 |

Not save-visible (out of scope, fine as-is): the `_dbg_*` **temp** variables in
`zz_debug_effects.txt` and `WA_AI_CONSTRUCTION_PRIORITY_core.txt` are log-formatting
locals for console harnesses and `WA_AI_construction_logging` output; temp variables
never serialize.

**Migration policy for the legacy families:** they stay exactly as they are and
retire with their checklist items, per the existing protocol. New instrumentation —
standing metrics and per-fix probes alike — uses WA_TLM. Do not rename live families
mid-stream: the checklist probes reference them verbatim and old campaigns carry the
old names.

### 2.1 Semantics registry for the legacy `*_dbg_*` counters

§3 below is the written contract for `WA_TLM_*`. The older `*_dbg_*` families never
had one, and that gap is what allowed two plausible-but-wrong numbers to be reported
in a single analysis session. This registry is the contract for them, retroactively:
what each counter counts, what it does **not** count, whether it is zero-initialised,
and any known miscount. **Nothing here changes the code** — the families keep their
behaviour and retire with their items (see the migration policy above). Rows are added
whenever a family's real semantics are established by reading its write site.

**The general rule, and the one that inverts conclusions if you get it backwards:**

| Namespace | Zero-init? | An *absent* name in a save means |
| --- | --- | --- |
| `wa_tlm_*` | **yes** — `WA_TLM_init_country`, `WA_TLM_core.txt:61-62` | build predates WA_TLM (or a mid-game tag before its first monthly pulse) — **probe void**. A `wa_tlm_*` present at **0 is a real zero reading.** |
| `wa_ai_*_dbg_*` | **no** — bare `add_to_variable` / `set_variable`, no init pass | **never incremented** — which is a *result*, not a probe gap. A `_dbg_` name at 0 is essentially unreachable; absence is what "zero" looks like. |

Reading an absent `*_dbg_*` as "instrumentation missing" turns a confirmed failure
into an unscoreable one; reading an absent `wa_tlm_*` as "genuinely zero" turns a
pre-instrumentation build into a FAILED. Check which namespace you are in first.

| Counter | Counts | Does **not** count | Zero-init | Known miscount / trap |
| --- | --- | --- | --- | --- |
| `wa_ai_uk_air_dbg_called` | entries into `WA_AI_build_uk_air_hosting_capacity` (`WA_AI_CONSTRUCTION_PRIORITY_strategies.txt:968`), weekly PC pulse | anything about outcomes — a call in surplus increments it too | no | — |
| `wa_ai_uk_air_dbg_planes` | gauge: faction deployed planes at the last call (`:1069`) | — | no (`set_variable`) | overwritten weekly; meaningless without the save's date |
| `wa_ai_uk_air_dbg_capacity` | gauge: (air-base levels in UK hosting states **+** ROOT-queued type-2 projects targeting one) **× 100** (`:1043-1070`) | capacity outside the hosting states; other countries' queues (Fix 37 companion excluded USA Pacific projects) | no (`set_variable`) | **The ×100 is correct for this mod** — `common/defines/05_defines.lua:173` sets `AIRBASE_CAPACITY_MULT = 100` (vanilla is 200). Do **not** "correct" it to 200. |
| `wa_ai_uk_air_dbg_best` | the ladder level a project was started at (`:1126`) | — | no (`set_variable`) | **`-2` means "no deficit / satisfied"** (`:1071`), i.e. the system reporting health. It is not an error code and not a failure. A deficit pulse that starts nothing also leaves `-2`. |
| `wa_ai_uk_air_dbg_started` | **Fix 47 onward:** UK hosting air-base projects that **verifiably entered the queue** (gated on `WA_AI_PC_queue^num` growing, matching the `thair` twin). **Before Fix 47:** weekly pulses spent in deficit with an eligible state | air-base levels actually *built* (a queued project can still be cancelled or stall out) | no | **THE SEMANTIC CHANGED AT FIX 47 — the number is not comparable across that boundary.** Pre-Fix-47 it incremented unconditionally after `WA_AI_PC_start_project`, which declines silently on `queue_max` / same-type dedup / duplicate province: campaign `911bed3c` at 1946.4 read ENG 115 + USA 61 = **176** "starts" against ~47 levels of real capacity growth, and `9a4cd657` at 1944.7 read ENG 97 + USA 39 = 136 against 34 levels. A post-fix campaign reading *lower* than a pre-fix one is the fix working, **not** a regression. Still cross-check against building levels (`savegame.py buildings`) — queued is not built. |
| `wa_ai_thair_dbg_started` | theatre air-base projects that **verifiably entered the queue** | declined starts | no | Carried the queue-growth guard (`:1440-1451`) from the `2b607968` over-count onward; its UK counterpart above did not until Fix 47, when the two were made comparable. **The durable lesson outlives the specific bug:** a caveat recorded against one member of a twin pair says nothing about the other — check the other write site. |
| `wa_ai_thair_dbg_{called,target,active,best}` | as the uk_air equivalents, theatre-scoped (`:1130-1392`) | — | no | — |
| `wa_ai_supply_line_dbg_{called,pf_ok,queued}` | entries / A\* successes / queued corridor projects (`:558, :578, :614, :654`) | — | no | Absence is the **result**, not a gap: on `911bed3c` `_pf_ok`/`_queued`/`_last_state` are absent on every tag at every sample, which *is* the finding — the state-level A\* returned success zero times all campaign (R9). |
| `wa_ai_supply_line_dbg_last_state` | gauge: last state a corridor project was queued on (`:615`) | — | no (`set_variable`) | — |
| `wa_ai_overext_dbg_active` | **months** the overextension flag has been set — `+1 per monthly evaluation while the flag is up` (`WA_AI_misc_effects.txt:718`) | current state | no | **A monotone counter, not a boolean.** `= 34` means "flagged for 34 months", not "overextended = true". |
| `wa_ai_overext_dbg_mic_redirects_{cic,refinery}` | MIC queue calls actually substituted (`WA_AI_CONSTRUCTION_queue_functions.txt:147, :155`) | queue calls the brake declined to reach | no | Absence means **the substitution never ran**, not that the probe is missing — that is exactly how R24's "brake never bit for ENG" was established. |
| `wa_ai_invasions_dbg_{adds,removes,active}` **(consumer R14 retired 2026-08-12 — see §3.7 row for the split delete/promote disposition)** | scripted-invasion penalty applications / removals / live count (`WA_AI_DIVISION_CREATOR_effects.txt:2304-2305`, `events/WA_AI_invasions.txt:76, :103`) | — | no (but `_active` is `set_variable = 0` by the migration sweep, `WA_AI_MIGRATION_effects.txt:158-159`) | `WA_AI_invasions_migration_1` books a `_removes` per purged pair, so `adds − removes` is **deliberately falsified** across a migration — see R14's documented caveat. |
| `wa_ai_ita_dbg_r13_{na_front,na_offensive}` | one-shot `fire_only_once` stamps (`events/WA_AI_ITA.txt:188-253`) | persistence — the gate holding once says nothing about it holding after | no | The §3.6 rule 2 failure mode in its original form; R13 asks for weekly counters to replace them. |
| `wa_ai_aifc_sector_*` (`_states`, `_objectives`, `_anchor`, `_age`, `_enemy`, `_ref` twins) | live AIFC sector state — **not a counter family**, listed here because it is read the same way | — | n/a | Cleared with `clear_variable` / `clear_array` (`WA_AI_AIFC_core.txt:138-156`), so a country with no sector reads as **absent, not 0**. "Sector absent" is the real signal (R27); do not read it as an unwritten probe. |

## 3. The WA_TLM standard

### 3.1 Namespace

- Script-side prefix: `WA_TLM_` (variables, arrays, scripted effects, flags).
  Saves lowercase variable names, so the save-side namespace is **`wa_tlm_`** and one
  regex — `^wa_tlm_` — retrieves a country's entire telemetry surface, with zero
  noise from system state (`wa_ai_*` holds live working state; mixing telemetry into
  it is what made discovery regex-fragile).
- `WA_TLM_` is a **reserved prefix**: nothing that is not telemetry may use it, and
  telemetry must never be *read* by gameplay/AI logic. Telemetry is write-only from
  the mod's point of view — the moment a strategy branches on a `WA_TLM_` value, it
  stops being observability and becomes load-bearing state (and its retirement
  becomes a behaviour change).
- Standing metrics: `WA_TLM_<system>_<metric>` (e.g. `WA_TLM_comp_armor`).
  Per-fix probes: `WA_TLM_r<NN>_<metric>` keyed to the checklist item id
  (e.g. `WA_TLM_r13_exec_open_weeks`) — save-side `^wa_tlm_r\d+` isolates the
  probe subset.

### 3.2 Data types

| Type | Suffix | Write rule | Replaces |
| --- | --- | --- | --- |
| **Counter** | `_n` (or a named count) | `add_to_variable` only, **after confirming the action happened** (e.g. queue length grew, project id exists). Never count attempts, never reset outside init. | ad hoc `_called`/`_started` counters |
| **Gauge** | plain name | `set_variable` each sample tick; meaningful only next to the clock (§3.3) and its `_last_t` stamp | overwritten weekly values |
| **Stamp** | `_first_t`, `_last_t` | clock value at first/last occurrence: `_first_t` written once (`has_variable` guard on non-zero), `_last_t` every occurrence | `fire_only_once` event stamps — `_last_t` + a counter is what proves *persistence*, which a one-shot stamp cannot |
| **Ring buffer** | `_hist` | bounded array, pushed on the shared sample tick, oldest entry evicted (`remove_from_array index = 0`) past depth | nothing — this is the new capability |

Ring buffers share **one time axis per country**: `WA_TLM_hist_t` (clock values).
Every `_hist` array must push on exactly the same tick as the axis, so index *i* of
any series pairs with `wa_tlm_hist_t^i`. Default depth **44** samples (quarterly =
11 game-years, covering a full 1936–1947 campaign). A system needing monthly
resolution gets its own axis (`WA_TLM_<sys>_hist_t`) and justifies the cost.

Pre-computed aggregates (min/max/sum) are counters/gauges maintained at write time
(`WA_TLM_<sys>_<metric>_max` updated under `check_variable >` guard) — cheaper than
ring depth when only the extreme matters.

### 3.3 The clock

`global.WA_TLM_clock` = **months elapsed since 1936.1** (0 at startup, +1 on the
first country's monthly pulse, guarded by a 20-day timed global flag so it ticks
once per month, not once per country). Decode: `year = 1936 + floor(clock/12)`,
`month = 1 + clock % 12`. The `tlm` retrieval subcommand does this conversion.
HOI4 script has no readable current-date variable, which is why the clock exists;
it is also branch-robust (a reloaded earlier save carries its own clock value).

**Resumed-campaign caveat:** on a pre-TLM save loaded onto an instrumented build,
the clock starts at 0 *at load time* — it reads "months since first instrumented
pulse", not calendar months, and the `tlm` command's date decode is wrong there.
Calendar-correct only on campaigns started from 1936 on an instrumented build
(every cloud test campaign). On resumed legacy campaigns, read clock values as
relative offsets and anchor them against the save dates.

### 3.4 Cadence and cost discipline

- **Counters/stamps**: written at the owning event site, whatever its cadence — cost
  is one `add_to_variable` on a path that already runs.
- **Gauges and ring buffers**: written only from `WA_TLM_monthly_sample`, called on
  the existing `on_monthly` pulse (`WA_AI_misc_on_actions.txt`), gated `is_ai`.
  Expensive samples (trigger ladders) additionally gate on
  `WA_AI_CONFIG_is_major_country` or the narrowest archetype that answers the
  question. **Never add a new on_action for telemetry.** Monthly cadence matches the
  cloud campaigns' monthly autosave cadence — sampling faster than the snapshot rate
  buys nothing for save-side retrieval (that's what ring buffers are for).
- No telemetry work on daily/weekly pulses. If a weekly system wants a weekly
  metric, it keeps a counter (free) and lets the monthly sampler snapshot the gauge.

### 3.5 Initialisation and the absence contract

`WA_TLM_init_country` is a **preserving** zero-init: it creates each registered
metric at 0 *only if absent* (`has_variable` guard per line), then stamps
`WA_TLM_version = <N>`. Called from `on_startup` for every country, and lazily from
the monthly sampler (version mismatch check) for tags created mid-game (civil wars,
releases). The guards are load-bearing: counters write at event sites at any
cadence, so a mid-game tag can accumulate counter values **before** its first
monthly pulse runs the init — an unconditional zero-init would wipe them; the same
mechanism preserves ring-buffer history across a version-bump re-init on resumed
campaigns. This makes absence tri-state and unambiguous:

| Observation in save | Meaning |
| --- | --- |
| no `wa_tlm_*` at all | build predates WA_TLM — **probe void**, never FAILED. One exception: a tag created mid-game shows nothing (or only event-written counters, no `wa_tlm_version`) until its **first monthly pulse** — check the tag's creation date before reading absence as a build statement. |
| `wa_tlm_version` present, metric = 0, `_last_t` = 0 | instrumented, code path never sampled/fired for this country |
| metric = 0, `_last_t` > 0 | sampled, genuinely zero — a real reading |

Bump `WA_TLM_version` when metrics are **added**; the sampler re-runs init on
version mismatch so the new metrics exist at 0 on old campaigns resumed on a new
build — existing values and ring buffers survive (preserving init).

### 3.6 Honesty rules (each one is a documented past failure)

1. A counter increments only on **verified effect** (queue grew, variable exists),
   never on entry into the code path (thair lesson).
2. Never ship a bare one-shot stamp as a behaviour probe; pair `_first_t` with
   `_last_t`/counter so persistence is measurable (R13 lesson).
3. Any consumer comparing adds/removes-style pairs must document every writer that
   can skew the pair (migration lesson: `dbg_removes` booked by the sweep).
4. Telemetry variables initialise to 0 (§3.5) so absent ≠ zero (brake lesson).
5. Store on the **country**, not globals — globals serialize ~4.9M lines deep and
   sit outside the `var`/`tlm` country-scoped retrieval; the clock is the sanctioned
   exception (small, and the `tlm` command reads it via the country's `_hist_t`).
6. Every write site carries a `# tlm:` comment naming the metric and its consumer
   (`standing` or the checklist item id). The registry (§5) is the index; a
   `WA_TLM_` write with no registry row is an orphan and gets removed.

### 3.7 Retirement

- `WA_TLM_r<NN>_*` probe metrics retire **with their checklist item**, same session:
  delete the write sites, drop the registry row, drop the init lines. (Old saves
  keep the values; that is fine and useful.) The checklist skill's retirement
  protocol enforces this — the agent retiring the item is the agent deleting the
  instrumentation. Before deleting, run the §3.8 promotion test.
- **Version bumps on addition only.** Removing metrics does NOT bump
  `WA_TLM_version`: stale `wa_tlm_*` leftovers in old saves and resumed campaigns
  are inert and self-identifying, and a needless re-init pass buys nothing. (A
  bump is otherwise harmless since the init is preserving — §3.5.)
- Standing metrics are permanent until the design question they answer disappears;
  removing one is a design decision recorded here.
- The rule already in `wa-campaign-checklist/SKILL.md` — "if the fix has no natural
  save-visible fingerprint, add instrumentation" — now reads: add a `WA_TLM_rNN_*`
  probe per this standard.

### 3.8 Standing vs probe — classification and promotion

**Default: every new metric is born a probe** (`WA_TLM_r<NN>_*`, dies with its
item). Claiming a standing name up front requires meeting at least one of:

1. **A FUNDAMENTAL consumer.** The metric scores or diagnoses an F-item (WW2 arc,
   F8 pathologies) or another permanent analysis question — something asked of
   *every* campaign, not of one fix.
2. **A documented extraction cost it retires.** The question it answers has already
   required a multi-save streaming parse in ≥2 analysis sessions (e.g. army
   composition before the R6 pilot). Cite the sessions in the registry row.
3. **A system-health invariant**, not a mechanism-of-one-fix: "how deep is the PC
   queue / what is the armor share / does sector age cycle" is health; "did this
   specific gate hold" is a probe, however important the fix.

Rules of thumb that follow: a probe normally needs only counters and `_first_t`/
`_last_t` stamps — **a probe that wants a ring buffer is usually a standing metric
in disguise** (trend = permanent question); and gameplay code never reads either
kind, so "something else might need it later" is not a reason to keep a probe —
old saves keep the values, and re-adding a metric is cheap.

**Promotion at retirement:** when the checklist item retires, ask whether analysis
sessions used the metric beyond the item's own pass/fail. If yes, rename it to
`WA_TLM_<system>_<metric>`, add the registry row (criterion 1–3 satisfied, say
which), bump the version (§3.5), and note the promotion in the retirement commit.
If no — delete it without sentiment; that is the normal fate of a probe.

## 4. Cost/benefit

**Save weight.** One variable line ≈ 25–40 bytes. Pilot scope: ~10 init'd scalars ×
~110 countries ≈ 4 400 lines ≈ 130 KB, plus ring buffers on ~10 majors
(2 arrays × 44 entries ≈ 90 lines ≈ 3 KB each) ≈ 30 KB. Total **< 200 KB on a
~100 MB save (+0.2%)**. Even a mature system (30 standing metrics, 6 ring series on
majors) stays under 1 MB (+1%). Save weight is not the constraint.

**CPU.** Counters are free (one add on an existing path). The monthly sampler runs
per AI country once a month; the pilot's trigger ladders (~26 `has_army_size`
evaluations) run only for ~7–9 majors. Against the existing monthly work
(`WA_AI_TEMPLATES_calculate_templates` for every AI country) this is noise. The
budget rule: a metric whose sample costs more than ~50 trigger evaluations must be
major-gated or demoted to quarterly.

**Benefit.** (a) Trend questions collapse from "stream-parse 8–15 saves" to
"read the ring buffer in the latest 1–2 saves" — roughly a 10× reduction in
extraction-subagent wall-time for the most common analysis shape, and branched
timelines stop corrupting trends (each save carries its own consistent history).
(b) Build fingerprinting becomes uniform (`wa_tlm_version` from the very first
save). (c) Probe authoring stops inventing conventions per fix.

**Risks, honestly.** (i) *Lying telemetry is worse than none* — the standard's
rules are countermeasures to observed lies, but new write sites can still lie;
probe authors must verify the first campaign's readings against a second signal
before trusting a family (as R14 did). (ii) *Ring-buffer bugs are silent* — a
desynced axis (pushed value without pushing the axis, or vice versa) shifts every
later pairing; the shared-tick rule plus the `tlm` command's length check
(mismatched array lengths are reported loudly) guard this. (iii) *Perf creep* —
the namespace makes adding metrics easy; the §3.4 gates and the registry review are
the brake. (iv) Array eviction (`remove_from_array index = 0`) is O(depth) monthly
per series — trivial at depth 44, but do not raise depth casually.

## 5. Metric registry

| Metric (script name) | Type | Cadence / gate | Consumer | Since |
| --- | --- | --- | --- | --- |
| `WA_TLM_version` | init stamp | startup / lazy | build fingerprint (all probes) | v1 |
| `WA_TLM_hist_t` | ring axis | quarterly, majors | all `_hist` series | v1 |
| `WA_TLM_comp_div_total` | gauge | monthly, all AI | R6, F8 | v1 |
| `WA_TLM_comp_armor` | gauge (banded) | monthly, majors | R6 | v1 |
| `WA_TLM_comp_mech` | gauge (banded) | monthly, majors | R6 | v1 |
| `WA_TLM_comp_armor_mech_pct` | gauge (derived) | monthly, majors | R6 | v1 |
| `WA_TLM_comp_last_t` | stamp | monthly, all AI (written with the family's widest gauge — a stamp inside a narrower gate breaks the absence contract for the excluded countries) | R6 absence contract | v1 |
| `WA_TLM_comp_armor_mech_pct_hist` | ring | quarterly, majors | R6 trend | v1 |
| `WA_TLM_pc_aging_grants` | counter | on verified lane grant (weekly PC allocator, `WA_AI_PC_assign_factories`) | R26 (PC allocator health) | v2 |
| `WA_TLM_pc_aging_reval_cancels` | counter | on revalidation-cancel (same site) | R26 | v2 |
| `WA_TLM_r47_lrange_n` | counter | monthly, all AI (`WA_AI_EQUIPMENT_update_context_flags`) | R31 | v3 |
| `WA_TLM_r47_lrange_first_t` / `_last_t` | stamps | same site | R31 | v3 |
| `WA_TLM_r47_alu_large_n` | counter | monthly, all AI (same site) | R32 | v3 |
| `WA_TLM_r47_alu_large_first_t` / `_last_t` | stamps | same site | R32 | v3 |

**Fix 47 probe semantics.** Both counters are *months the gate was OPEN*, sampled
**after** the latch update so they read the flag exactly as the `ai_equipment`
priority modifiers will see it that month — a verified state, not code-path entry
(§3.6 rule 1). The paired `_n` counter is what makes persistence measurable; the
`_first_t` stamp alone would over-affirm the way R13's `fire_only_once` stamps did
(rule 2). `_first_t` is written under a `_n = 1` guard, so a gate that opened at
clock 0 (1936.1) stamps 0 — read `_n > 0` first, not `_first_t > 0`. Only the two
gates the pilots consume are instrumented; the steel pair and the
strategic-bombing latch carry no probe, because a `WA_TLM_` write with no registry
consumer is an orphan (rule 6). Second signal for validating the first campaign's
readings: `savegame.py resources <TAG>` net aluminium against `r47_alu_large_*`
(the gate must only be open in months whose net balance clears +50), and the
production-line/variant reading for `r47_lrange_*` (SOV's `air_fighter_mr` line
must sit on the long-range variant exactly while the latch is up).

## 6. Pilot: army composition (checklist gap R6)

R6 ("majors mechanize", pass = GER/SOV armor+mech share > 18%) has been
`NOT CHECKED` for two campaigns because **no save-visible composition metric
exists** — divisions reference templates by numeric id only.

Design: script has no numeric getter for divisions-by-type (same limitation as
`divisions_in_state` — see the posture lesson), so the sampler brackets
`has_army_size = { size > N type = armor|mechanized }` over an ascending threshold
ladder (5…300) and stores the highest floor passed. Banded precision (~±10% of the
reading at worst) is ample for an 18% share bar on 100+ division armies. `type =
infantry/motorized` usage exists in-repo (`GER_factions.txt:155-161`); `armor` and
`mechanized` are vanilla tokens for this trigger — **boot-check on first launch**
(F9): an unknown token would error at parse, a silently-empty band on a country
with known tanks means the token filter failed and the metric must not be scored.

Share = `100 × (armor_band + mech_band) / num_divisions` (num_divisions is
variable-readable — `railway_helpers.txt:468`). Note the reading is *fielded
divisions whose dominant type matches*, which is what R6's "fielded share" means.

Probe (goes to checklist R6): `tlm GER <last-save>` → the quarterly
`comp_armor_mech_pct` series; pass if GER and SOV ≥ 18 at any sampled quarter of
1942+. Absence contract per §3.5.

## 7. Adding a metric — checklist for authors

1. Register it here (§5) with type, cadence, gate, consumer.
2. Add the init line to `WA_TLM_init_country` (and bump `WA_TLM_version` — §3.5).
3. Write the sample/increment site with its `# tlm:` comment (§3.6).
4. If it is a per-fix probe: name it `WA_TLM_r<NN>_*` and add the checklist item's
   `Probe:` line in the same session (existing protocol).
5. Walk the honesty rules (§3.6) against the write site; state which second signal
   will validate the first campaign's readings.
