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
| `wa_ai_uk_air_dbg_planes` | gauge: faction deployed planes at the last call (`:1069`) | — | no (`set_variable`) | overwritten weekly; meaningless without the save's date. **And it counts PLANES, not wing slots** (2026-08-16): the engine books air-base capacity per wing at `land_air_wing_size` (100 / tac 200 / strat 300 / scout 25), so this gauge under-states the true load by the wings' fill gap (~10 % on `af003548` 1944.7, more after heavy attrition). Read the engine-side load with `airload.py`, not from this pair |
| `wa_ai_uk_air_dbg_capacity` | gauge: (air-base levels in UK hosting states **+** ROOT-queued type-2 projects targeting one) **× 100** (`:1043-1070`) | capacity outside the hosting states; other countries' queues (Fix 37 companion excluded USA Pacific projects) | no (`set_variable`) | **The ×100 is correct for this mod** — `common/defines/05_defines.lua:173` sets `AIRBASE_CAPACITY_MULT = 100`. Compare it against `airload.py`'s NOMINAL, not against `_planes` alone (see the row above) (vanilla is 200). Do **not** "correct" it to 200. |
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
| `WA_TLM_pc_built_n` | counter | **at the spawn site** in `WA_AI_PC_add_finished_building_by_id`, gated on `_build_type` being inside the 1..16 range the effect's own ladder covers — NOT the monthly sampler | standing — the **success** half of the PC termination ledger. A building actually appeared | v14 |
| `WA_TLM_pc_built_by_type^<code>` | counter, **indexed by building type** | same site | standing — "did the air bases ever finish" in one read. **Deliberately not zero-initialised**: an absent index means this country never completed that type, which is unambiguous because the zero-init'd `pc_built_n` beside it witnesses the family's presence. Codes are the `WA_AI_PC_building_type` set (2 = air_base, 4 = radar, 13 = railway, 14 = naval_base, …) | v14 |
| `WA_TLM_pc_refused_n` | counter | **at the completion site** in `WA_AI_PC_complete_project_by_id`, in the `else` of the two spawn branches | standing — **the failure mode that had no fingerprint at all**: a project that reached progress ≤ 0, i.e. was fully paid for in civ-weeks, and was then denied its building and discarded. From outside it is indistinguishable from a completion | v14 |
| `WA_TLM_pc_refused_ctrl_n` | counter | same site, subset | standing — the refusals caused by **control** of the target state, testing each branch's own controller rule (allied-buildable types accept faction/subject ground; factory types demand direct control). `_refused_n − _refused_ctrl_n` is therefore "friendly ground, no free building slot" | v14 |
| `WA_TLM_pc_sweep_n` | counter | **at the sweep decision** in `WA_AI_PC_update_project_progress` (`constant:wa_ai_pc.alloc.stall_cancel_weeks` = 30) | standing — the counter whose absence forced checklist R19 to be held rather than retired. Everything added to `_cancel_projects_IDS` there is unconditionally ended by the `WA_AI_PC_cancel_projects` call below it | v14 |
| `WA_TLM_pc_orphan_n` | counter | **after `end_project_by_id`** in the broken-project cleanup of `WA_AI_PC_update_project_progress` (`target_state = 0` or `cost ≤ 0`) | standing — bookkeeping corruption, as distinct from a strategic cancel | v14 |
| `WA_TLM_pc_stale_n` | counter | **at the cancel decision** in `WA_AI_PC_validate_queued_provincial_projects` | standing — route-selector churn: a queued project whose target province left the strategy's current valid path set. **This is the reason the pre-v14 counters could not explain.** On `be18f9c7`, GER's railway queue fell 80 → 24 → 2 across 1944.6–1945.2 while `pc_aging_reval_cancels` moved 50 → 64 and no project ever reached the 30-week sweep bar (max observed stall 26) | v14 |
| `WA_TLM_pc_lost_n` | counter | **at the cancel site** in `on_state_control_changed` (`WA_AI_misc_on_actions.txt`), written on the OLD controller, incremented by `_cancel_projects_IDS^num` immediately before the cancel call clears the array | standing — projects lost because the ground changed hands. Expected to dominate for any country losing territory, and previously invisible | v14 |
| `WA_TLM_pc_peace_n` | counter | **after `end_project_by_id`** in the `on_peace` railway purge (Fix 5/19, same file) | standing — kept apart from `pc_stale_n` on purpose: a peace purge is correct behaviour clearing an obsolete frontline, a stale-path cancel is the selector changing its mind mid-war | v14 |
| `WA_TLM_pc_queued_t^<project id>` | stamp, **indexed by project id** | **at the queue-write site** in `WA_AI_PC_start_project`; cleared with the slot in `WA_AI_PC_end_project_by_id` (ids are recycled, so the clear is load-bearing) | standing — the clock at which a project entered the queue, and **the only record of queue age anywhere in the system**. `WA_AI_PC_stall_weeks` is not a substitute: it resets to 0 every week a project is funded, so it is the current starvation streak, and the two diverge on exactly the projects worth asking about. Lives in the telemetry namespace rather than as a `wa_ai_pc_*` field precisely so that writing it may read `global.WA_TLM_clock` — a gameplay field fed from the clock would be gameplay reading telemetry (§3.1). Not zero-initialised (indexed); absent = slot free, or queued on a pre-v14 build. `savegame.py pc` prints it as `age_m` against `pc_last_t` | v14 |
| `WA_TLM_pc_queue` / `_civs` / `_civs_avail` / `_assigned` | gauges | monthly, all AI (`WA_TLM_sample_pc`) | standing — queue depth, `num_of_civilian_factories`, `num_of_civilian_factories_available_for_projects`, `WA_AI_PC_assigned_factories_total`. **`_civs_avail` exists nowhere else**: the engine does not serialize it, so the allocation base was previously unrecoverable from any save | v14 |
| `WA_TLM_pc_alloc_base` | gauge | same site | standing — `_civs_avail + _assigned`, the pool `WA_AI_PC_assign_factories` reconstructs before applying its fraction. Deliberately does **not** bake in the `constant:wa_ai_pc.alloc.stable_base_fraction` floor or `constant:wa_ai_pc.alloc.hard_cap_fraction` ceiling — both are functions of `pc_civs`, sampled beside it, and baking them in would hide the case where the floor is what is funding the queue | v14 |
| `WA_TLM_pc_share_pct` | gauge (derived) | same site | standing — `100 × assigned / civs`, PC's share of the country's whole civilian industry | v14 |
| `WA_TLM_pc_avail_share_pct` | gauge (derived) | same site | standing — `100 × assigned / alloc_base`, PC's share of what it was **allowed** to take. Read against the fraction in force that month (40, or `WA_AI_PC_override_max_factories_factor × 100` while its country flag is live — `savegame.py pc` prints which): at the fraction = pool-bound; well under = the fill found no eligible project; over = the stable-base floor is carrying the queue | v14 |
| `WA_TLM_pc_last_t` | stamp | monthly, all AI (written with the family's widest gauges, never inside the major gate) | `pc_*` absence contract | v14 |
| `WA_TLM_pc_hist_t` + `_pc_queue_hist` / `_pc_share_pct_hist` / `_pc_avail_share_pct_hist` | ring + **own** axis | quarterly, `WA_AI_CONFIG_is_major_country` | standing — PC trend inside one save. Own axis rather than `WA_TLM_hist_t`: the composition family happens to use the same gate today, and sharing an axis would make that a permanent coupling (§4, risk ii) | v14 |
| `WA_TLM_sq_adds_n` | counter | `WA_AI_add_<X>` (building_adders), all eight shared-slot types, only when `WA_AI_available_<X>` passed and the add was issued | standing — family **sq** (standard construction queue); R49, R53 | v17 |
| `WA_TLM_sq_adds_by_type^i` | counter (indexed 0 CIC · 1 MIC · 2 NIC · 3 REF · 4 SR · 5 HSR · 6 AR · 7 HAR; not zero-initialised, `sq_adds_n` is the witness) | same site | standing — per-type split of the above | v17 |
| `WA_TLM_sq_first_t` / `_last_t` | stamps | same site | standing — family absence contract | v17 |
| `WA_TLM_sq_tier_a_n` / `_b_n` / `_c_n` / `_d_n` | counters | `WA_AI_bf_record` after a selection add (queue_functions) — A breadth, B wrap-around, C over-depth breadth, D pre-Fix-88 fallback | standing — R53 spread leg; `d_n / adds_n` = how often breadth was exhausted | v17 |
| `WA_TLM_sq_k_max` | max-aggregate gauge | same site, `check_variable >` guard | standing — widest K ever used | v17 |
| `WA_TLM_sq_k` | gauge | monthly, all AI (`WA_TLM_sample_sq`) — `clamp((civs − PC assigned)/20, 1, 20)`, same arithmetic as `WA_AI_queue_breadth_prepare`; stored **fractional** (9.15, 12.8 …), effective K = ceil() because the walk compares an integer rank `<` it | standing — R53 K reading | v17 |
| `WA_TLM_sq_rebase_down_n` | counter | `WA_AI_add_<X>` when the TTL flag had lapsed and `committed > built` (the sum is being rebased down = a cancelled/lost queue forgotten) | standing — R49 cancellation path | v17 |
| `WA_TLM_sq_ctrl_reset_n` | counter | `on_state_control_changed` on the OLD controller (written from the effect root — inside the `FROM.FROM` state block `FROM` re-binds to the state; the first cut landed there, see R49 history), only when a live `WA_AI_committed_<X>_recent` flag is dropped | standing — R49 control-change path | v17 |
| `WA_TLM_r47_lrange_n` | counter | monthly, all AI (`WA_AI_EQUIPMENT_update_context_flags`) | R31 | v3 |
| `WA_TLM_r47_lrange_first_t` / `_last_t` | stamps | same site | R31 | v3 |
| `WA_TLM_r47_alu_large_n` | counter | monthly, all AI (same site) | R32 | v3 |
| `WA_TLM_r47_alu_large_first_t` / `_last_t` | stamps | same site | R32 | v3 |
| `WA_TLM_nav_ships` / `_subs` | gauges (`num_ships` / `num_ships_with_type@submarine`) | monthly, any AI with a hull | R36, convoy-war questions. **`_subs` is INCLUSIVE of cruiser submarines** — `submarine` is an engine aggregate as well as a sub-unit def name, and the aggregate wins (settled `be18f9c7` 2026-08-14: SOV 101 = 93 cruiser + 8 plain, GER 18 = 14 + 4, both matching `r64_csubs` exactly). Plain hulls = `_subs` − `r64_csubs`; never read `_subs` as the plain-boat count | v4 |
| `WA_TLM_nav_screens` | gauge (destroyer + frigate + light_cruiser) | monthly, any AI with a hull | R36 | v4, **valid from v5** |
| `WA_TLM_nav_convoys` | gauge (`num_equipment@convoy`) | monthly, any AI with a hull | R36 | v4, **valid from v5, unverified until F9** |
| `WA_TLM_nav_conv_threat` | gauge (engine 0-1, stored ×100) | monthly, any AI with a hull | R36 | v4 |
| `WA_TLM_nav_conv_ws` | gauge (engine 0-1, stored ×100; observable range 0-30, a RATE not a tally) | monthly, any AI with a hull | R36 | v4 |
| `WA_TLM_nav_conv_killed` | gauge (engine cumulative) | monthly, any AI with a hull | R36 | v4 |
| `WA_TLM_nav_last_t` | stamp | monthly, any AI with a hull (widest gauge of the family) | R36 absence contract | v4 |
| `WA_TLM_nav_port_screens` | gauge (banded, reads LOW) | monthly, `WA_AI_CONFIG_MILITARY_is_major_naval` | R36 | v4 |
| `WA_TLM_nav_port_pct` | gauge (derived) | monthly, naval majors | R36 headline | v4, **valid from v5** |
| `WA_TLM_nav_hist_t` + `WA_TLM_nav_port_pct_hist` | ring + **own** axis | quarterly, naval majors | R36 trend | v4, **valid from v5** |
| `WA_TLM_post_exec_n` | counter | **weekly, per (country, enemy)** at the posture calculus (`WA_AI_MILITARY_posture_effects.txt`, inside `every_enemy_country`) — NOT the monthly sampler | posture level-1 exchange-rate question | v6 |
| `WA_TLM_post_exec_xr_n` | counter | same site, level-1 observations that had a usable ratio | **denominator for the three buckets below** | v6 |
| `WA_TLM_post_exec_xr_lt100` / `_lt50` / `_lt25` | counters | same site | **cumulative and nested** (lt25 ⊂ lt50 ⊂ lt100); where a level-1 veto threshold should sit, if one is wanted | v6 |
| `WA_TLM_post_grind_n` | counter | same site, level-2 observations | context: how often the careful mode is actually reached | v6 |
| `WA_TLM_post_last_t` | stamp | same site, written on **every** observation whatever the level | `post_*` absence contract | v6 |
| `WA_TLM_r64_csubs` | gauge (`num_ships_with_type@cruiser_submarine`) | monthly, any AI with a hull (`WA_TLM_sample_navy`, same gate and `nav_last_t` stamp as the `nav_*` family) | R41 — read against `WA_TLM_nav_subs`, which it is a **SUBSET of, not a sibling series**: `nav_subs` counts these hulls too (settled `be18f9c7` 2026-08-14), so the plain-boat count is `nav_subs − r64_csubs`. **GER is the built-in control**, it has been on the cruiser role since before Fix 64, so GER = 0 too means a bad token, not a failed fix | v7 |
| `WA_TLM_r8_uk_air_q_n` | counter | **per verified queue** in `WA_AI_uk_air_queue_site` (`WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`), on the same queue-growth gate as `wa_ai_uk_air_dbg_started` — NOT the monthly sampler. ENG/USA only in practice | R8 concentration leg — **denominator** | v8 |
| `WA_TLM_r8_uk_air_rank_sum` | counter (aggregate) | same site, only when rank > 0 | R8 — **mean rank = `_rank_sum / (_q_n − _fallback_n)`**. 1 = Kent … 11 = Cornwall, so LOWER is more concentrated in the south. Pre-Fix-51 behaviour (random among the least-developed states) would tend to 6.0 | v8 |
| `WA_TLM_r8_uk_air_rank_max` | gauge (running max, `check_variable >` guard) | same site, only when rank > 0 | R8 — how far north the build ever reached. Rises only as southern ranks cap out or run out of building slots | v8 |
| `WA_TLM_r8_uk_air_fallback_n` | counter | same site, only when rank = 0 (queued by the unordered fallback tail) | R8 — **drift alarm.** Non-zero means either every ranked state was capped/unbuildable, or `WA_AI_uk_air_hosting_state` and `global.WA_AI_uk_air_priority_states` disagree. Deliberately excluded from `_rank_sum` / `_rank_max` | v8 |
| `WA_TLM_r8_uk_air_last_t` | stamp | same site, every verified queue | R8 absence contract + persistence (a `_q_n` with no `_last_t` movement is a dead builder, not a satisfied one) | v8 |
| `WA_TLM_r8_air_lane_grants` | counter | **at the reservation grant** in `WA_AI_PC_assign_factories` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`), one per WEEK the Fix 78 lane actually assigned ≥ 1 factory to a band-300 air-base project; chain-latched against re-entry re-grants exactly like `pc_aging_grants`. Not the monthly sampler | R8 Fix-78 leg — **counts funded WEEKS, not factories.** It exists because the snapshot gauge `wa_ai_pc_air_factories_assigned` under-samples at monthly cadence: `be18f9c7` read ENG **0 in 20 of 30 months** while whatever funding did occur fell between saves. `_grants = 0` across a deficit window is unambiguous starvation; a non-zero `_grants` with a 0 snapshot is normal | v15 |
| `WA_TLM_r8_air_lane_last_t` | stamp | same site, every verified grant | R8 Fix-78 leg — persistence. `_grants` climbing with a frozen `_last_t` cannot happen (same write); a frozen `_last_t` while the deficit stands means the lane stopped being reached — check `WA_AI_PC_air_basing_reserve` is still being refreshed | v15 |
| `WA_TLM_r44_freeze_n` | counter | **at the flag write** in `WA_AI_LANDING_stamp_freeze_west` / `_east` (`WA_AI_LANDING_effects.txt`) — one per stamped country per landing operation, NOT the monthly sampler. Written on the invader and on every AI faction member | R44 — **denominator**; `_n = _west_n + _east_n` by construction | v10 |
| `WA_TLM_r44_freeze_west_n` / `_east_n` | counters | same site | R44 — **the theatre split is the point.** A Pacific-fighting country whose `_east_n` is large is a country a blanket faction-wide freeze would have stalled; comparing USA's `_west_n` against `_east_n` is the direct measurement of the cost the theatre scoping avoids | v10 |
| `WA_TLM_r44_freeze_first_t` / `_last_t` | stamps | same site | R44 — persistence. `_first_t` is written under an `_n = 1` guard, so read `_n > 0` before trusting it (a stamp at clock 0 is a legitimate 0) | v10 |
| `WA_TLM_nav_cv_f` / `_n` | gauges (`num_deployed_planes_with_type@cv_small_fighter_airframe` / `@cv_small_naval_bomber_airframe`) | monthly, any AI with a hull (`WA_TLM_sample_navy`, same gate and `nav_last_t` stamp as the `nav_*` family) | R43 — the two quantities Fix 66's saturation gate compares, sampled at the values the gate sees. **Both 0 on a carrier major in a war year means the token is bad and the brake was never live** — nothing about Fix 66 may be scored (the v4 `nav_screens` failure mode, same class of token) | v9 |
| `WA_TLM_nav_cv_hulls` | gauge (`num_ships_with_type@carrier`) | same site | R43 — the hull count Fix 66 bands on. **SETTLED `be18f9c7` 2026-08-14: the `carrier` aggregate DOES include light carriers** — JAP 21 = 16 fleet + 5 light, ENG 20 = 18 + 2, USA 52 = 52 + 0. So the bands count a light deck at the weight of a fleet deck and are correspondingly loose for a light-heavy fleet (under-brakes, the safe direction) | v9 |
| `WA_TLM_r31_lrvar_t` | **invocation** stamp | **at the event site**, country event `sov_armor.980` (`events/WA_AI_SOV.txt`), once per campaign on the day SOV's `create_equipment_variant` for the long-range La-5FN runs — SOV only, NOT the monthly sampler | R31 — **only meaningful read against the `equipments={}` registry, because `create_equipment_variant` returns nothing.** `0` + no "Lavochkin La-5FN (long range)" entry = the event never fired (trigger/tech problem, debug the event); `> 0` + no entry = the effect was **rejected by the engine** (R31 branch (a) — the `ordnance_equipment` / `allowed_types` question in the shared equipment files, not this site); `> 0` + entry present = the design exists and the verdict moves to the selection layer. `0` is unambiguous as "never" here: the gating tech `sov_fighter_multirole_ad_tech_7` is a 1943 tech, so clock 0 is unreachable | v12 |
| ~~`WA_TLM_r48_prebuild_synth_*`~~ | — | **RETIRED 2026-08-16** with the proactive synthetic-rubber lane (R48 superseded by the industrial-planning rework); inits deleted, names free. A save carrying them is a v13–v17 build before the retirement | R48 (ledger) | v13–v17 |
| `WA_TLM_r54_air_lane2_grants` / `_first_t` / `_last_t` | counter + stamps | **at the second air-lane grant** in `WA_AI_PC_assign_factories` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`), one per WEEK the Fix 87 second slot assigned ≥ 1 factory, chain-latched like `r8_air_lane_grants` | R54 (P1) — the second slot exists only while `wa_ai_pc_air_deficit_pct > 20` (a save also carrying `wa_tlm_r54_air_headroom_*` is the one-day P2 build, removed 2026-08-16); `_grants = 0` with the deficit variable above 20 for months = the slot never found a second type-2 project (queue budget of 3 per builder is the usual reason) | v17 |
| `WA_TLM_r52_thair_front_n` | counter | **at the verified start** in `WA_AI_build_theatre_air_bases` (`WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`) — one per air-base project actually appended (queue grew) while the Fix 85 ground-committed rule was in force. NOT the monthly sampler | R52 — **did the ladder ever choose the theatre the country is fighting in.** `_n = 0` on a landing power with divisions ashore and the theatre in deficit = the committed rule never restricted the draw (check `wa_ai_thair_dbg_committed` on the same saves — 0 there means no ROOT division was seen on a side-controlled member state). Pair with `pc TAG --match air_base` for the target states: a count that lands on Balkans/Pacific states while the divisions are in France means the commitment detection is reading the wrong states | v17 |
| `WA_TLM_r52_thair_front_first_t` / `_last_t` | stamps | same site | R52 — timing: `_first_t` should sit within ~2 months of the landing that put divisions in the theatre; written under a `= 0` guard, read `_n > 0` first | v17 |
| `WA_TLM_r95_corridor_seg_n` / `_depot_n` / `_port_n` | counters | **at the end of a theatre-corridor pass** in `WA_AI_PC_railway_corridor_pass` (`WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt`) — one per rail segment / supply hub / naval base the pass ADMITTED into the PC queue (queue length grew across `WA_AI_PC_start_project`), NOT per request: `queue_max`, the province-duplicate guard and the controller test all refuse silently. Every 4 weeks (`corridor.interval_weeks`) on eligible builders. Not the monthly sampler | R60 — **the corridor engine ran and got projects in.** `_seg_n = 0` on ENG while it holds Tobruk + 5078 at war = the pass never admitted (theatre gate, `node_is_ours`, or a full scoped budget — read `pc ENG --match corridor`). "Built" is NOT this counter: read the map (`global.wa_ai_pc_railway_connection_level_<a>^<b>` between two nodes, `supply_node` at 10049 / 9980, `naval_base` at 11957) — a queued project can still be swept, stale-cancelled or peace-purged | v19 |
| `WA_TLM_r103_corridor_reach` | **gauge** | `set_variable` **every** corridor pass in `WA_AI_PC_railway_corridor_pass` — number of hops requestable *only* because of Fix 103's permission/payment split (both ends ours, **exactly one** our charge). A gauge, not a counter: "how many hops does the widening currently unlock" is sampled state, and a counter at a classification site would be the code-path count §3.6 rule 1 forbids | R68 — **the split changed what this builder can see.** `reach = 0` on every Axis member across the campaign means the widening never bit and the fix is inert; `reach > 0` on GER/ITA while `r103_corridor_seg_n` stays 0 means it saw the hop and something downstream refused it (read `blocked_n`, then `pc <TAG>` by node province id) | v25 |
| `WA_TLM_r103_corridor_orphan` | **gauge** | same site, same cadence — hops with both ends *ours* and **neither** our charge: legal for us, funded by nobody | R68, and the **regression test for Fix 104** — read it paired with `WA_TLM_r104_ally_fund_n`: `orphan` should **fall as `ally_fund_n` rises**, and sustained `orphan > 0` with `ally_fund_n = 0` means the authority/funding split did not take. After Fix 104 (v26) the ally leg tests FUNDING, so a surviving "neither end my charge" hop is one whose ends belong to partners that genuinely can fund — each has a foot on it and builds it itself, so a transient reading is normal and is not a defect. The remaining alarm is `orphan` high **while the hop is still unbuilt on the map**: the owner is not building it either, a defect of *its* pass (theatre gate, civ floor, queue depth). Never a pass/fail of Fix 103 itself | v25 |
| `WA_TLM_r103_corridor_seg_n` | counter | same site — one per rail segment **ADMITTED** (PC queue grew) on a pass where `reach > 0`. Verified effect, never per request | R68 — the widening turned into queued rail. "Built" is still the map, not this counter | v25 |
| `WA_TLM_r103_corridor_blocked_n` | counter | `WA_AI_PC_start_railway_project` (`railway_helpers.txt`), corridor family only, **placed after the `current_level < target` check** — one per corridor segment that wanted a level and whose state failed `WA_AI_PC_state_controller_allows_admission`. Placement is the definition: before the level check, every already-built hop with a hostile-state end would book a refusal that never happened. Calls the same trigger the executor calls, so probe and gate cannot drift | R68 — **makes the silent refusal visible.** This is the class that hid the *second* dead hop of `7c7803a8` (7079 ↔ 5078) for 28 months: an ally-held province inside an enemy-controlled state, requested and pathfound every 4 weeks, never queued, no trace. `blocked_n` climbing while `seg_n` is flat = the province/state scope mismatch, not a selector problem | v25 |
| `WA_TLM_r103_corridor_first_t` / `_last_t` | stamps | the `seg_n` site only, on a pass that admitted ≥ 1 | R68 — same "first **STAMPED**, not first requested" caveat as the r95 pair; `global.WA_TLM_clock` is 0 in Jan 1936. Read `seg_n > 0` before trusting either | v25 |
| `WA_TLM_r104_ally_fund_n` | counter | **at the queue append itself** in `WA_AI_PC_start_project` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`, immediately after `add_to_array = { WA_AI_PC_queue = _project_id }`) — one per project of **any** type whose target state is controlled by a faction ally that is neither ROOT nor a subject of ROOT. Verified effect, never per request: the selectors propose far more than the admission gate and the type budget accept. Not the monthly sampler | R69 — **the verified effect of Fix 104**, which gave the Fix 74 ally leg its own FUNDING test (`WA_AI_PC_country_cannot_fund_own_logistics`) instead of the authority test, whose war branch has no civ-factory term. Read **against `r103_corridor_orphan`**, the detector Fix 103 left for exactly this residual: orphan should fall as this rises. Sustained `orphan > 0` with `ally_fund_n = 0` on a live corridor means the split did not take. `ally_fund_n = 0` everywhere with no allied belligerent under `min_civs_war` is a legitimate zero, not a failure — check the allies' civ counts before scoring | v26 |
| `WA_TLM_r104_ally_fund_first_t` / `_last_t` | stamps | same site, `_first_t` under a `= 0` guard | R69 — timing: `_first_t` on ENG/USA should sit within ~1 railway interval (8 weeks at war) of the ally dropping below the wartime civ floor while holding front-adjacent ground. Read `_n > 0` before trusting either; clock 0 is Jan 1936 | v26 |
| `WA_TLM_r95_corridor_first_t` / `_last_t` | stamps | same site, only on a pass that admitted ≥ 1 project | R60 — timing: `_first_t` on ITA should be a 1936–37 clock (peace preparation of the Libyan spine at band 500), on ENG within ~1 pass of first holding two consecutive Egyptian / Cyrenaican nodes at war; written under a `= 0` guard, read `_seg_n + _depot_n + _port_n > 0` first. `_last_t` frozen while the corridor is contested = the pass went quiet | v19 |
| `WA_TLM_r96_italy_states_manned` / `_states_strong` | gauges | monthly, `WA_TLM_sample_italy_guard` (`WA_TLM_core.txt`), only on an AI country that is an Italy (`WA_AI_MILITARY_is_italian_homeland_power`), is allied with one, or is at war with one — the three triggers run first so the 30 `divisions_in_state` reads never run elsewhere | R61 — **the verified effect of Fix 96**: of the 15 Italian mainland + Sicily states (list = `WA_AI_MILITARY_italy_homeland_invaded`), how many hold ≥ 1 / ≥ 4 of the country's OWN divisions (`divisions_in_state` counts ROOT's). The number the 0edbc955 baseline reads as ITA 1 / GER 0 for the whole autumn of 1943. Never read `guard_level` alone — a level with `states_manned = 0` for two saves is the failure, not a pass | v20 |
| `WA_TLM_r96_italy_guard_level` | gauge (0 none / 1 threatened / 2 invaded / 3 at war with an Italy) | same site | R61 — the **code-path companion**: which tier the geography triggers currently read for this country (owner: `italy_home_threatened` → 1, `italy_homeland_invaded` → 2; non-owner: `ally_italy_theatre_threatened` → 1, `_invaded` → 2, `at_war_with_italian_homeland_power` → 3). A GER level ≥ 1 in a save where no Italy reads ≥ 1 is the PREV-scope bug the trigger header warns about | v20 |
| `WA_TLM_r96_italy_first_t` / `_last_t` | stamps | same site; `_first_t` written under a `= 0` guard the first month `guard_level > 0` was sampled, `_last_t` every sampled month | R61 — timing: the owner's `_first_t` should sit at the month the belt/Tunisia/Sicily was first lost, GER's within one month of the owner's. Read `_last_t > 0` before trusting a 0 | v20 |
| `WA_TLM_r98_eth_both_n` | counter | monthly, end of `WA_TLM_sample_east_africa` (`WA_TLM_core.txt`), on any AI country at war with ETH that `controls_state` BOTH 909 Somali and 910 Amhara - the success test of `ETH_push_into_ethiopia_mission` (`common/decisions/ITA.txt`) | R63 - **the verified effect of Fix 98**: months Italy held the two mission states while the war ran. `0edbc955` baseline: 0 (Somali never taken; mission timed out 1936.8.9). Second signal: `ITA_defeat_in_ethiopia_flag` absent + `ETH_forced_ITA_peace_achievement` absent on ITA/ETH, and ETH annexed / `ITA_establish_ITS` fired | v22 |
| `WA_TLM_r98_eth_both_first_t` / `_last_t` | stamps | same site; `_first_t` under a `= 0` guard | R63 - `_first_t` should decode to <= 1936.7 (inside the 100-day window that opens 1936.5.1); read `_n > 0` first | v22 |
| `WA_TLM_r99_tunis_states_manned` / `_states_strong` | gauges | monthly, `WA_TLM_sample_tunis_bridge` (`WA_TLM_core.txt`), only on an AI country for which the Tunis bridge is contested (`WA_AI_MILITARY_tunis_bridge_contested`: at war, own side holds Tunis 458 or Bizerte 1061, an enemy stands in Algeria/Morocco) - the trigger runs first so the 6 `divisions_in_state` reads never run elsewhere; symmetric (an Allied Tunis with an Axis army in Algeria samples too) | R64 - **the verified effect of Fix 99**: of the 3 Tunisian states (458 / 1061 / 665 = the `AXIS_tunis_bridge_THEATRE` buffer list), how many hold >= 1 / >= 4 of the country's OWN divisions. `0edbc955` baseline: GER 0 / ITA 0 for the whole Dec 42 - Jun 43 window. Never read `_contested` alone - `_contested = 1` with `_states_manned = 0` for two saves is the failure | v23 |
| `WA_TLM_r99_tunis_contested` | gauge (0/1) | same site; set 1 while contested, reset to 0 on the first uncontested month after a contested one (gauges keep the last contested reading) | R64 - code-path companion: the Faction pull's gate as this country reads it | v23 |
| `WA_TLM_r99_tunis_first_t` / `_last_t` | stamps | same site; `_first_t` under a `= 0` guard the first sampled month with `_contested = 1` | R64 - timing: GER's `_first_t` should sit at the Torch/Case-Anton month; the R64 bar is `_states_manned >= 2` (or `_states_strong >= 1`) within 2 monthly samples of it. Read `_last_t > 0` before trusting a 0 | v23 |
| `WA_TLM_r51_local_hold_n` | counter | **at the level-1 verdict** in `WA_AI_MILITARY_update_posture` (`WA_AI_MILITARY_posture_effects.txt`), one per (country, enemy, week) whose level-1 verdict ONLY the Fix 83 hold band delivered: local count in `(LOCAL_RATIO_HOLD × enemy, LOCAL_RATIO × enemy]`, an execute entry already held against that enemy, and the hollow/air-lowered pairwise route closed (the plain pairwise route is closed by construction — the local scan only runs when it failed). NOT the monthly sampler | R51 — **verified effect: each count is an observation that would have read posture 0 before Fix 83.** `_n = 0` on ENG/USA across a contested landing is not a failure of the fix by itself — it means the count never sat in the band (either it never dropped under 1.5, or it fell straight through 1.1) — read it against the monthly `posture_vs_*` snapshot and the divisions-in-theatre table. A large `_n` with the front still not moving is the "hold band keeps orders on a front that cannot advance" shape to look for | v16 |
| `WA_TLM_r67_aifc_arm_entries_n` | counter | **inside each of the four emitters** (`WA_AI_AIFC_armor_add_boost` / `_cancel_boost` / `_add_suppress` / `_cancel_suppress`, `WA_AI_AIFC_helpers.txt`), one per `add_ai_strategy` issued. WEEKLY, every AI country the reconcile reaches — NOT the monthly sampler | R67 — the save bloat, self-reported. **Counts emitter INVOCATIONS, not confirmed engine entries**: script cannot read back the `persistent_strategy` list, so honesty rule 1 is met only as far as the engine allows. **Second signal, and it is a strong one**: the save's own type-83 count per major, which is directly countable — baseline USA **517** at 1944.6 on campaign `7c7803a8` (ITA 357, GER 219, ENG 84, JAP 38, FRA 18). A campaign whose `entries_n` and type-83 count diverge means an emitter is failing silently (the meta_effect lesson) | v24 |
| `WA_TLM_r67_aifc_arm_retire_n` | counter | **at the head of `WA_AI_AIFC_armor_reconcile`**, on a week entered with no sector enemy AND a non-empty `WA_AI_AIFC_armor_suppressed` — i.e. exactly the weeks section 2 wipes the book | R67 — **episode COUNT.** Once per episode by construction: a second consecutive lapsed week finds the book already empty and books nothing | v24 |
| `WA_TLM_r67_aifc_arm_install_n` | counter | end of the same effect, on the verified transition (book empty at entry, non-empty at exit) | R67 — episode CLOSE. `install_n − retire_n ∈ {0,1}`; 1 means a book is currently installed | v24 |
| `WA_TLM_r67_aifc_arm_lapse_wk` | counter | head of the same effect, every week entered with `_aifc_want < 1` | R67 — **the whole point of the family.** `lapse_wk / retire_n` = **mean episode length in weeks**, which is the number a retirement grace window must be sized against and which the entry count *cannot* supply: each episode emits one retire + one reinstall regardless of length, so 517 entries cannot distinguish 8 short lapses from 8 long ones, and monthly saves cannot resolve a weekly cadence. Note `_aifc_want < 1` conflates the transient no-anchor case with deliberate switch-off / war end / ineligibility — read it against `wa_ai_aifc_sector_anchor` and the country's war state before sizing anything | v24 |
| `WA_TLM_r67_aifc_arm_first_t` / `_last_t` | stamps | same effect, written only on ticks that actually emitted | R67 — persistence. `_first_t` under a `= 0` guard, so read `entries_n > 0` first. A frozen `_last_t` on a healthy tag is the **expected** reading (ENG's reconcile did zero work for 24 months), not an alarm — pair it with `retire_n = 0` to tell health from a dead code path | v24 |
| `WA_TLM_r51_local_hold_first_t` / `_last_t` | stamps | same site | R51 — **timing is the pass criterion**: `_first_t` must fall inside the landing's contested window (the D-Day month + 3 on an `af003548`-shaped run), not years later on some other front. Written under a `= 0` guard; read `_n > 0` first. `_last_t` running to the war's end with `_n` climbing is the band being the *only* thing keeping orders on — pair with the front-movement proxy before calling that healthy | v16 |

**v4 naval readings are artefacts — do not score them.** `nav_screens` and
`nav_convoys` were written from `num_ships_with_type@screen_ship` and
`…@convoy`. Neither is a legal target: the engine accepts a **sub-unit def type**
(`destroyer`, `frigate`, `light_cruiser`, `heavy_cruiser`, `battleship`, `carrier`,
`light_carrier`, `submarine`, `cruiser_submarine`) or one of the four aggregates
`carrier` / `capital` / `screen` / `submarine` — `screen_ship` is the sub-unit
*category* name from `common/units/ship_*.txt`, and `convoy` is not a ship at all
(convoys are equipment; there is no `common/units/ship_convoy.txt`). Both returned
a silent 0 for every country on every v4 save, which in turn forced `nav_port_pct`
down its `else = 0` branch, so **`nav_port_pct` and all 40 quarterly
`nav_port_pct_hist` samples on a v4 save are a hard-coded constant, not a
measurement**. Confirmed in-save on campaign `02bd4445`: `@submarine` and
`num_ships` are exact to the hull while `@screen_ship` and `@convoy` read 0 on
ENG/USA/GER/JAP. Fixed in v5 — `nav_screens` sums the three concrete hull types
and `nav_convoys` uses `num_equipment@convoy`. **Absence contract for this family
is therefore version-gated: `wa_tlm_version < 5` ⇒ `nav_screens`, `nav_port_pct`
and `nav_port_pct_hist` are NOT CHECKED, never FAILED.**

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

## 6b. Naval / convoy war (checklist gap R36, v4)

**The split is deliberate: this family measures the OUTCOME of escorting, never the
assignment.** A task force's mission is not exposed to script — there is no trigger
that reads it (`has_active_mission` is an operation trigger, not a naval one) — so
"how many escorts are actually on convoy escort" is answerable *only* from the save,
via `savegame.py navy TAG FILE...` (added the same session; it brace-parses
`units → fleet → task_force → mission` and maps the bare mission enum). Telemetry that
pretended to answer it would be inventing a number, so it does not try.

What it does carry:

- **Outcome, invisible in the save:** `nav_conv_threat` (engine convoy danger, 0-1),
  `nav_conv_ws` (war-support malus already paid for sunk convoys), `nav_conv_killed`
  (convoys this country destroyed — the raider end of the same ledger). None of these
  are stored in readable form in a savegame. **`nav_conv_ws` is a rate, not a
  lifetime tally**: the engine accrues at most −0.01 war support per week from
  convoys being raided *right now* and decays the accumulated penalty by 0.025/week,
  capped at −0.3 total (`05_defines.lua:134-137`). Its observable range in this
  metric's units is 0-30 and it falls back to ~0 within a couple of months of the
  raiding stopping — so a 0 on a country that has lost thousands of convoys over the
  campaign is a **real zero**, not a bad token (`has_convoys_war_support` and
  `convoy_threat` are both listed as legal variable reads in the engine's
  `dynamic_variables_documentation.md`). For cumulative loss, use `nav_conv_killed`
  from the raider's side plus the save's convoy efficiency.
- **Inventory:** `nav_ships` / `nav_screens` / `nav_subs` / `nav_convoys`.
  `nav_screens` is the explicit sum `destroyer + frigate + light_cruiser` — the exact
  set carrying `type = screen_ship` in `common/units/ship_*.txt`, and also exactly
  what `savegame.py navy` counts as `screens=` (`_NAVAL_SCREENS`), which keeps R36's
  "must match exactly" cross-check an identity rather than a dependency on an engine
  aggregate's membership. `nav_convoys` uses `num_equipment@convoy` because convoys
  are an equipment archetype, not a hull. See the v4-artefact note in §5 before
  reading any of these off an older save.
- **An independent "they are in port" reading:** `nav_port_screens` sums a per-state
  floor ladder over `ships_in_state_ports` on our own naval-base states, and
  `nav_port_pct` divides it by `nav_screens`. This is the cross-check that does **not**
  depend on the empirically-derived mission-id map: if the save says 69% idle and
  `nav_port_pct` says ~10%, the mission map is wrong, not the game. The ladder floors
  each state (39 screens book 20), so the metric reads **low** — it cannot manufacture
  an idle-fleet problem that is not there.

Two contract points specific to this family. It runs on its **own** ring axis
(`WA_TLM_nav_hist_t`): the composition axis is pushed under
`WA_AI_CONFIG_is_major_country` and this series under
`WA_AI_CONFIG_MILITARY_is_major_naval`, and a gate mismatch on a shared axis
desynchronises index *i* for every series on it (§4, risk ii). And `nav_last_t` is
written with the widest gauge of the family, never inside the naval-major gate, so a
minor's genuine zero does not read as "never sampled" (§3.5).

Standing, not a probe, under §3.8 criteria 2 and 3: the question "what share of the
navy is at sea" is system health rather than one fix's mechanism, and answering it
already cost a full multi-save streaming parse (2026-08-13 session).

**Second signal for the first instrumented campaign:** `savegame.py navy ENG <same
save>` must agree with `nav_port_pct` to within the ladder's floor error, and
`nav_screens` must match the command's `screens=` count exactly.

**F9 boot check still owed, and now narrowed to one token.** `convoy_threat` and
`has_convoys_war_support` are confirmed legal variable reads against the engine's
`dynamic_variables_documentation.md`, and the v5 `nav_screens` sum uses only
sub-unit def types already proven in this repo (`WA_AI_misc_effects.txt:770-778`,
`common/national_focus/usa.txt:12486-12593`). The one unverified token left is
**`num_equipment@convoy`** — the archetype form is the repo's standard idiom for
every other archetype, but no in-game reading exists yet. Boot check: launch to
1936, and on any country with convoys confirm `wa_tlm_nav_convoys > 0` while
`wa_tlm_nav_ships > 0`. If it reads 0, the archetype target failed; drop the metric
and its registry row rather than shipping a second silent zero.

## 6c. Priority construction (standing, v14)

**The split with `savegame.py pc` is the whole design, and it runs the opposite way
from §6b.** The PC queue *is* fully readable from a savegame — it is a country-scope
array (`wa_ai_pc_queue`) plus ~11 parallel indexed families keyed by project id — and
the `pc` subcommand decodes it per project, labelling building-type and priority-band
codes by name. So the queue snapshot needs no telemetry, and duplicating it here would
be pure cost. This family covers only what a save physically cannot hand over:

- **The allocation base.** `num_of_civilian_factories_available_for_projects` is not
  serialized anywhere in a save. A save can approximate total civ industry by summing
  `industrial_complex` levels over controlled states — the `pc` command does — but that
  is an upper bound on `num_of_civilian_factories` and says nothing about how much of it
  the *vanilla* construction queue had already absorbed, which is exactly the number
  `WA_AI_PC_assign_factories` multiplies by `constant:wa_ai_pc.alloc.fraction`. "PC is using 7% of
  GER's civ industry" and "PC took its full 40% of what it was offered" are both true of
  1944.6 on `be18f9c7`, and only the second one is actionable. `pc_civs_avail`,
  `pc_alloc_base` and `pc_avail_share_pct` are that reading.
- **Why a project left the queue.** A savegame shows what is in the queue, never what
  used to be. Departures were a single unattributable number: on `be18f9c7` GER's railway
  queue fell 80 → 24 → 2 across 1944.6–1945.2 while the only two counters that existed
  (`pc_aging_grants`, `pc_aging_reval_cancels`) moved by 14 combined, and the stall
  counters never reached the 30-week sweep bar (max observed 26) — so neither of the two
  documented cancel paths explains ~90% of it. The termination ledger closes this: eight
  counters, one per exit path, and their **sum is the total number of departures** because
  between them they cover every caller of `WA_AI_PC_end_project_by_id` and
  `WA_AI_PC_cancel_projects` outside the `WA_TEST_` harness. A gap between that sum and
  the observed shrinkage means a new exit path shipped without its counter.
- **How long a project has been queued.** The queue records no entry time. `stall_weeks`
  looks like an age and is not one — it resets to 0 every week a project receives factories
  — so `pc_queued_t` is added as a per-slot stamp. It is the one metric here that is
  per-project rather than aggregate, and it earns that because the aggregate form of the
  question ("median age of the railway queue") is computed *from* it at read time, whereas
  the reverse is impossible.
- **A trend inside one save.** Monthly saves each carry a queue snapshot, so a multi-save
  `pc` sweep already works — it just costs a ~100 MB streaming parse per save per question.
  The quarterly ring collapses that to one read.

Two readings this family deliberately does **not** attempt. It does not count *queue
additions* — `WA_AI_PC_start_project` declines silently on `queue_max`, same-type dedup
and duplicate-province tests, and instrumenting "attempted" against "accepted" there
would re-run the `wa_ai_uk_air_dbg_started` over-count (§2.1) at thirty call sites; the
queue's composition is readable directly instead. And it does not carry a per-type
factory breakdown, because `savegame.py pc` already prints assigned factories grouped by
building type from the queue itself.

**Standing, not probes, under §3.8 criteria 2 and 3.** Queue depth, factory share and
termination causes are system health, not one fix's mechanism; and the 2026-08-14 scoring
session established the extraction cost — the queue-collapse question, the ENG air-base
starvation question (R8/R23) and the R19 stall-artefact question each cost a bespoke
multi-save parse, and R19 has been held at 3/3 rather than retired specifically because
its criterion (4) was not computable from a save.

**Cost.** Eight variable reads, two divides, and quarterly three array pushes for majors
— cheaper than the composition ladder next door (26 `has_army_size` evaluations). The
termination counters are one `add_to_variable` each on paths that only run when a project
actually leaves the queue.

**Precise statement of the loop cost, because the earlier blanket claim ("nothing is written
inside the per-project queue loops") was false and a future author would have relied on it.**
Three of the eight termination counters *are* written inside a loop: `pc_sweep_n`
(`WA_AI_CONSTRUCTION_PRIORITY_core.txt:947`, inside `for_each_loop = { array =
WA_AI_PC_queue }`), `pc_stale_n` (`:1166`, same array) and `pc_orphan_n` (`:800`, inside
`for_each_loop = { array = _orphan_project_ids }`). Each executes only on its loop's rare
cancel branch, so the measured cost is negligible — but the family is internally
inconsistent, since `pc_lost_n` (`WA_AI_misc_on_actions.txt:449`) takes the aggregate form
`add_to_variable = { … = <array>^num }` after the loop. **If you add a ninth counter, use the
aggregate form**, and prefer converting these three to it whenever this code is next touched
for another reason.

**F9 boot check owed, and cheap — there is no token risk here.**
`num_of_civilian_factories` and `num_of_civilian_factories_available_for_projects` are
both read by `WA_AI_PC_assign_factories` itself, so a bad token would have broken the
allocator years ago; the indexed-counter write is the same idiom as
`WA_AI_PC_state_type_projects^_project_building_type`. Boot check: launch to 1936 and
confirm on any AI country that `wa_tlm_pc_civs > 0` and `wa_tlm_pc_last_t` is present.
**Second signal for the first instrumented campaign:** `pc_built_by_type^13` against the
growth in `savegame.py buildings TAG --match rail`, and `pc_avail_share_pct` against the
`alloc override` line `savegame.py pc` prints for the same month — a country with the
override flag live should read near 50–60, not 40.

## 6d. Standard construction queue (standing, v17)

The scripted standard queue (`events/WA_AI_construction.txt` → `WA_AI_queue_<X>` → `WA_AI_add_<X>`)
places buildings by walking the score-sorted `WA_AI_shared_slot_scores`. Two fixes made its
placement observable: **Fix 81** keeps a per-state sum `WA_AI_committed_<X>` = built + queued (a
completion leaves it unchanged, so nothing is reconciled) so `free_building_slots` no longer
admits a state whose queue is already at the building's `state_max`; **Fix 88** spreads a burst of
calls across the top-K states (K = lines the country can feed) with a per-line depth preference,
four tiers deep, the last tier being the pre-fix pick.

What the save already shows and this family does **not** duplicate: the engine queue
(`production/general_lines`, per state, `amount`, `created_date`) and the sums + TTL flags on the
state blocks (`wa_ai_committed_<x>`, `WA_AI_committed_<X>_recent`) — `refq3.py` / `lines.py` join
them. What it cannot show and this family covers: **which tier** placed each add (was breadth ever
exhausted → `tier_d_n`), **how wide** the country was allowed to go (`sq_k`, `sq_k_max`), whether the
two forgetting paths of the sum ever ran (`rebase_down_n`, `ctrl_reset_n`), and a per-type add
ledger (`adds_by_type`) that a save can only reconstruct by diffing `general_lines` across
consecutive saves — lines merge and complete between snapshots, so that diff undercounts.

Honesty (§3.6): `adds_n` counts *availability passed + add issued* — the same evidence level as the
sum itself, since script cannot read the engine queue; a refused add (state at the real cap the
sum did not know about — engine-AI lines are invisible to it) is counted. `tier_*` are written only
after the selection produced a target and the adder ran. `rebase_down_n` / `ctrl_reset_n` count the
set/clear that actually happened. Second signal for the first instrumented campaign: `adds_n`
against the number of adder-made lines × amount in `general_lines` created in the same window
(should match within the merge/complete lag), and `sq_k` against `ceil((civs − pc_assigned)/20)`
computed from `pc_civs`.

Standing, not probes, under §3.8 criteria 2 and 3: every AI country runs this queue every
campaign, and the R49/R53 local scorings (2026-08-15/16) each required a bespoke general_lines
join to answer "how deep / how wide did it place".

## 6e. Lend-lease surplus relief (standing, v18; maritime extension v28)

`WA_AI_LEND_LEASE_request_surplus_relief` (`WA_AI_lend_lease_effects.txt`, weekly, ROOT =
recipient) pulls an overland `send_equipment` from ONE donor per week for the nine land-equipment
rows in `common/script_constants/wa_ai_lend_lease.txt`, only when a state path between the capitals
crosses friendly ground (Fix 92). Convoy row 10 is a separate maritime pull: same weekly entry point,
but its own donor selection and no land A*. Three campaigns of R7b were scored from stockpile
`creator=` deltas because nothing recorded whether a donor was ever picked, whether the pair was
refused, or which leg fired. Standing under §3.8 criterion 3 (every AI country runs it weekly).

| Metric | Kind | Written where | Consumer / reading | Version |
| --- | --- | --- | --- | --- |
| `WA_TLM_llr_starving_n` | counter, on the RECIPIENT | at entry of the weekly pull, when `WA_AI_LEND_LEASE_is_starving_any` holds | R7b — denominator: weeks the country was short of at least one archetype; `donor_selected_n / starving_n` = how often the lottery found a candidate at all | v18 |
| `WA_TLM_llr_donor_selected_n` | counter, on the RECIPIENT | at the `random_other_country` pick, before the path test | R7b — how often the lottery picked anyone; 0 with starving legs = the `donor_can_serve` limit never matched | v18 |
| `WA_TLM_llr_path_refused_n` | counter, on the RECIPIENT | after `WA_AI_LEND_LEASE_relief_land_access` returned 0 for the picked donor | R7b — the land-access rule at work; expect > 0 on island/overseas recipients (ENG, AST) and 0 on GER's continental clients | v18 |
| `WA_TLM_llr_convoy_starving_n` | counter, on the RECIPIENT | at entry of the weekly maritime pull when the recipient is below its scale-aware reserve | R56 — denominator: weeks a convoy-capable wartime recipient was below its dockyard-band reserve, with a 1,000 minimum for majors | v28 |
| `WA_TLM_llr_convoy_donor_selected_n` | counter, on the RECIPIENT | when the maritime `random_other_country` actually selected a donor | R56 — distinguishes no eligible donor from a silent send failure; no pathfinding is involved | v28 |
| `WA_TLM_llr_sent_n^idx` / `WA_TLM_llr_sent_amount^idx` | per-archetype counter + amount, on the DONOR, arrays sized 11 | `WA_AI_LEND_LEASE_relief_record` after the `send_equipment`, ONLY when the recipient's free stock re-read rose above the pre-send read (idx = constants row: 1 infantry, 2 heavy_infantry, 3 support, 4 artillery, 5 heavy_artillery, 6 anti_tank, 7 anti_air, 8 motorized, 9 train, 10 convoy; 0 unused) | R7b / R56 — which leg moved and how much; read with `savegame.py var TAG "^wa_tlm_llr_sent"` (indexed arrays, not ring buffers — the `tlm` renderer would misread them) | v18; idx 10 v28 |
| `WA_TLM_llr_send_failed_n` | counter, on the DONOR | same site, the ELSE branch: the recipient's free stock did not rise across the meta_effect send | R7b / R56 — must read 0; > 0 means the rendered `send_equipment` failed silently (see the meta_effect lesson) | v18 |
| `WA_TLM_llr_first_t` / `_last_t` | stamps, on BOTH sides | same site | R7b — timing; `_first_t` written under a `= 0` guard | v18 |

## 7. Adding a metric — checklist for authors

1. Register it here (§5) with type, cadence, gate, consumer.
2. Add the init line to `WA_TLM_init_country` (and bump `WA_TLM_version` — §3.5).
3. Write the sample/increment site with its `# tlm:` comment (§3.6).
4. If it is a per-fix probe: name it `WA_TLM_r<NN>_*` and add the checklist item's
   `Probe:` line in the same session (existing protocol).
5. Walk the honesty rules (§3.6) against the write site; state which second signal
   will validate the first campaign's readings.
