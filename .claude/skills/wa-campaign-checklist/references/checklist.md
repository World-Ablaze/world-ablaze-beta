# Campaign verification checklist — living data file

**As of:** 2026-08-10 · last campaign scored: cloud `66d6b53c` (BHU observer, 1936.2–1945.6, `dlcs=257535` — first cloud run with LaR/AAT active). Build = Tier-1 stack through `083b224ac`, **without** `17505d9a9` (R14 fix). R2 and R4 retired this session (streak 3/3).

Protocol for scoring, retiring, and adding items: see `../SKILL.md`. Streak = consecutive PASSED; FAILED resets it to 0; `N/A (DLC)` / `NOT CHECKED` leave it untouched.

## Campaign registry (analysed to date)

| game_unique_id | Machine / DLC | Scope | Analysed |
| --- | --- | --- | --- |
| `0e7e7852` | cloud, `dlcs=30` | BHU observer, 119 monthly saves 1936–45 | 2026-08-09 |
| `c9ab1062` | cloud, `dlcs=30` | SCW-focused check | 2026-08-09 |
| `9be92c89` | cloud, `dlcs=30` | all-AI observer 1936–1946.12 | 2026-08-10 |
| `cbca536d` | local, `dlcs=191999` | SOV control run, full DLC | 2026-08-10 |
| `66d6b53c` | cloud, `dlcs=257535` (LaR+AAT confirmed active) | BHU observer, 113 monthly saves 1936.2–1945.6 (truncated, war unresolved), HOI4 1.19.2; build through `083b224ac`, no R14 fix | 2026-08-10 |
| `2b607968` | local, full DLC | GER player campaign used for the R1 live-diagnostic + Fix 31 verification (1943.2–1943.5 saves) | 2026-08-10 |

**DLC note (supersedes the old `dlcs=30` assumption):** the cloud box now ships `dlcs=257535` — La Résistance and Arms Against Tyranny both behaviourally confirmed in `66d6b53c` (LaR SCW flags, AAT MIO lines). Always read the save header's `dlcs=` per campaign instead of assuming by machine.

---

## FUNDAMENTAL — never removed

### F1. WW2 starts on time

- **Pass:** German–Polish war begins ~1939.9.1 (±4 months).
- **Probe:** global flags block near top of save (`flags` command, no TAG) — war-start flag set-dates; cross-check GER `diplomacy`.
- **Note:** the M-R pact focus manpower gate (`GER_mol_rib_pact` needs 1.5M army manpower under limited conscription) is the known variance source — see `campaign-audit-fix-plan` memory root-cause (a). Low priority; Barbarossa's hard date absorbs the delay.
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — war started 1940.1.17, 4.5 months late (outside ±4; M-R manpower gate, known variance).
  - 2026-08-10 · `cbca536d` · PASSED — war started 1939.9.1, on time.
  - 2026-08-10 · `66d6b53c` · PASSED — war started 1939.9.1 exactly (`GER_has_started_war` set 1939.9.1.8; Warsaw fell 1939.10.7).

### F2. France falls on time

- **Pass:** France capitulates ~1940.6 (±3 months).
- **Probe:** global flags / FRA country block capitulation state; VP control of Paris.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · NOT CHECKED — arc completed through German defeat (implies fall of France) but the date was not explicitly recorded; record it next run.
  - 2026-08-10 · `66d6b53c` · PASSED — Paris fell 1940.6.22, capitulation 1940.6.30 (`fall_of_france`), both near-exact historical dates.

### F3. Barbarossa fires

- **Pass:** GER–SOV war begins. Note it is hard-dated **1941.6.22** in `common/decisions/z_WA_ai_GER.txt` and silently absorbs upstream delays — a pass here says nothing about the war-start timeline.
- **Probe:** global flags war set-dates; SOV `diplomacy` section.
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER–SOV war fired on the anchored date; European war proceeded to conclusion.
  - 2026-08-10 · `66d6b53c` · PASSED — `barbarossa_counter` set 1941.6.22.17; Kiev fell 1941.9.24 (front moving on schedule).

### F4. Pearl Harbor / USA entry

- **Pass:** USA enters the war ~1941.12 (±3 months).
- **Probe:** USA `diplomacy` section, global war flags.
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — USA at war in the expected window (exact entry date not recorded; record it next run).
  - 2026-08-10 · `66d6b53c` · PASSED — `day_of_infamy_happened` 1941.12.4 (3 days early).

### F5. Germany loses WW2 and the European war ends

- **Pass:** Germany is defeated and the European war terminates (white-peace chain or capitulation). Historical target ~1945.5; ending at all is the invariant, ending on time is the aspiration.
- **Probe:** global flags for the German white-peace chain; GER country state in late saves.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — scripted German white-peace chain fired 1946.9. Late vs ~1945.5 target but the war ENDS; lateness traces to the 4.5-month-late war start (F1).
  - 2026-08-10 · `66d6b53c` · NOT CHECKED — campaign truncated at 1945.6 with the war still running: GER uncapitulated and holds Berlin, but D-Day fired on time (1944.6.8), Allies are on German soil and GER carries the terminal-attrition idea set (`death_before_defeat`, `GER_werwolf`, `scraping_the_barrel`, `economy_fatigue_78`). Trajectory plausible for a 1946 white-peace as in `9be92c89`; unresolvable on a truncated run. If later saves of this campaign arrive, re-score.

### F6. Pacific war terminates — KNOWN GAP

- **Pass:** the Pacific war reaches a termination path (Japanese surrender chain).
- **Status:** **KNOWN GAP — no termination path exists in the mod.** Expected FAILED until the Japanese surrender chain is built (Tier 3 in `campaign-audit-fix-plan`); do not re-diagnose, do not count toward pathology findings.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — Japan frozen at 1942 extent through 1946.12; no termination mechanism fired (by design gap).
  - 2026-08-10 · `66d6b53c` · FAILED (known gap) — JAP undiminished at 1945.6 (units block larger than GER's); the Pacific contributes zero global flags after `fall_of_singapore` 1942.4.28 — 38 months dark.

### F7. Spanish Civil War: Nationalists win — DLC-gated

- **Pass:** Nationalist Spain wins the SCW, ideally by ~1939.
- **DLC-gated:** scoreable only when La Résistance is active — **read the save's `dlcs=` per campaign** (the cloud box now has LaR: `dlcs=257535` since `66d6b53c`; the old `dlcs=30` cloud runs were N/A). Note the mod defines only `SPR` + dynamic `D01`–`D59` tags — LaR presence is proven by `SPA_`-prefixed LaR flags and D02 activation, not by SPA/SPB/SPC/SPD tag existence.
- **Probe:** global flag `spanish_civil_war` (still set = unresolved); SPR `politics` (Nationalists = neutrality) vs D02 (Republicans, democratic) alive-ness across saves. **S1-fix sub-probe (`d5d88061d`, civil-war brake exemption):** neither Spanish belligerent has `WA_AI_defensive_front_strategy` acting as a permanent veto — for each side, either the flag is absent in ≥1 mid-war save, or `wa_ai_fielded_eq_ratio` ≥ 0.5 in a save where front battles are occurring; corroborate with rising casualties on both sides (flat casualties = still frozen). If the SCW still deadlocks WITH S1 confirmed working, escalate to the shelved options (N1/N2/N4 balance nudges, B1/B3 scripted resolution backstops — see the 2026-08-10 SCW investigation).
- **Streak:** 0
- **History:**
  - 2026-08-09 · `c9ab1062` · N/A (DLC) — cloud non-LaR path; Republican win #3 was a dead-code artefact, not balance evidence.
  - 2026-08-10 · `9be92c89` · N/A (DLC) — cloud, no LaR.
  - 2026-08-10 · `cbca536d` · PASSED — LaR path, Franco won 1939.3.30; both balance commits' mechanisms fired. Residual: volunteer-airforce decisions never fired on either side.
  - 2026-08-10 · `66d6b53c` · FAILED — **nine-year SCW deadlock**: still at war at 1945.6 (`spanish_civil_war` never cleared, both sides' AIFC sector-enemy flags refreshed 1945.5.29). D02 alive all campaign, tech count doubled, PP ×4. The `e86d4d830` aid-flow rebalance is in this build and did not produce a decision; SPR had ITA/GER volunteers+lend-lease from 1936.7 yet never closed (its `SPR_preparing_offensive_in_progress_flag` from 1938.12 still present mid-1939).

### F8. No major runs the old pathologies

- **Pass:** for every major: manpower not pinned at ceiling with falling division count; army-wide field fill ≥90%; no 100k+ equipment hoard sitting beside starving faction allies.
- **Probe:** per-major `units` fill sampling + stockpile vs allies' deficits; `var TAG "^wa_ai_"` deployment/lend-lease state. Cross-reads R5 (GER), R7 (relief legs), R10 (USA).
- **Note:** GER late-war 65% fill under the low supply-reach defines was ruled **by design** (Phase 1 rejection in `campaign-audit-fix-plan`) — do not count it here.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — USA collapsed to 42 divisions with 249k idle infantry equipment and 0 deploy conveyors from 1943.6; hoards moved to SOV/USA and unreachable neutrals (POR 116k). Fixes shipped since (`3da0be383`, `2d48a1a17`) — see R10/R7b.
  - 2026-08-10 · `66d6b53c` · PASSED — no major collapsed: GER 98→327 divisions, SOV army +140%, USA recovered 47→133 (no repeat of the 42-division collapse). Caveats: field fill not sampled this run; USA infantry stock peaked at 101.7k at 1944.6 (vs 249k last campaign) and drained to 29k by 1945.6.

### F9. Game boots

- **Pass:** the build the campaign runs on launches without CTD. Scored per build, before the campaign: run the launch harness after any commit touching `force_concentration` blocks in country ai_strategy files — the deterministic-CTD lesson is that `GER_fall_gelb` + `war_with_soviets` fc entries are load-bearing (see comments in `common/ai_strategy/GER.txt` and the `d69eef2fa` incident).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — build through `083b224ac` booted on the cloud box and ran 9.5 game-years without CTD. (HEAD adds only `17505d9a9` + docs on top; boot-test HEAD before the next campaign anyway.)

---

## RETIREABLE — fix verifications

Delete an item when its streak reaches its threshold (3 = narrow probe, 5 = behavioural).

*Retired 2026-08-10 (streak 3/3 on `66d6b53c`): R2 (PC factory allocation, fix `974bad6f7`) and R4 (rubber shortage tracker, fix `974bad6f7`).*

### R1. AIFC sector_age cycles 1–5

- **Fix under test:** `9778316f2` (Fix 31). Root cause **live-confirmed 2026-08-10** on a 1943.3 local run: the validity check compared plain map-data ids against `THIS.id` (engine-encoded scope reference — observed `anchor=228` vs `scoped=-10737.41596`, DIFFERS on 108/108 samples) — equality never held, validity 0 every week, weekly re-pick reset age to 1. Fix 31 rewrites validity as a corridor-array walk and publishes engine-encoded `*_ref` twin arrays for the four Layer-4 `state_trigger`s (which had the same mixed comparison — boosts never matched, NOT-suppressions uniform no-op). Prior attempts `4bfea363d`/`128cc7995` patched real-but-downstream defects. Side-note kept for honesty: the "armor accumulators ~10 800" anomaly was retracted — serialized country scope refs, not growing sums.
- **Layer-4 residual check:** the `*_ref` twins assume engine trigger-context `THIS.id` matches script-side ROOT-hopped `PREV.id` encoding; if wrong, Layer 4 stays at the old relative no-op (not worse). Verify via the 5-minute observation from the R1 analysis (temporarily −50→−100 on the front suppression: uniform collapse = encoding still mismatched) or front-behaviour deltas in the next campaign.
- **Pass:** `wa_ai_aifc_sector_age` observed cycling through values 1–5 across a campaign's saves, not pinned at 1.
- **Probe:** `var <major TAG> "^wa_ai_aifc_sector_age" <saves...>` across the campaign. On a local run: `AIFC-DIAG` lines in game.log (is_major-gated telemetry shipped with Fix 31 — healthy is age climbing 2..5 with valid=1, re-selection only at age > 4; remove the telemetry when this item retires). Also check `wa_ai_aifc_sector_states_ref` exists alongside the plain array (encoded twins populated).
- **Threshold:** 5 (behavioural — commitment-window dynamics over time).
- **Streak:** 1
- **History:**
  - 2026-08-09 · `0e7e7852` · FAILED — age pinned at 1 all campaign.
  - 2026-08-10 · `9be92c89` · FAILED — still pinned at 1 after the ROOT-hop fix; reproduced on `cbca536d` too.
  - 2026-08-10 · `66d6b53c` · FAILED — GER 14/14 samples at age 1 while `sector_anchor` moves (28→731→193→205→245→258→22): the loop runs and re-picks, but the age is reset instead of incremented; variable entirely absent in two snapshots (mid-clear). SOV identical. (The "armor accumulator" side-observation was later retracted — serialized scope refs.)
  - 2026-08-10 · `2b607968` (local, Fix 31 build) · PASSED — live telemetry over 6 weekly pulses: all majors age 2→3→4→5 with valid=1, re-selection exactly at age>4 (GER re-anchors 228→195 on 1943.5.3, then ages again); USA correctly inert (no land contact). Save 1943.5.11: GER `sector_age=3` (first >1 ever seen in a save), `sector_states_ref` populated (3 encoded refs = corridor size). Layer-4 encoding-match still unverified (residual check above).

### R3. Land majors queue type-13 railways

- **Fix under test:** `3c55b9d17` (Fix 29/29b — land-war railway queueing).
- **Pass:** land-war majors (SOV, GER at minimum) show type-13 projects in the PC queue during their land wars.
- **Probe:** `var <TAG> "^wa_ai_pc_building_type" <saves...>`.
- **Threshold:** 3 (narrow queue probe). Retire when both SOV and GER reach 3.
- **Streak:** SOV 3, GER 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — SOV and GER both queued type-13 railway projects.
  - 2026-08-10 · `cbca536d` · PASSED (SOV) — control run confirms SOV queueing; GER not re-checked.
  - 2026-08-10 · `66d6b53c` · PASSED — SOV queue dominated by type-13 the whole war (68/71 slots at 1942.6); GER 26→55→42 type-13 across 1942–43 with real `connect_province` ids. Anomaly to watch: GER queue holds **zero** railways 1944.3–1944.6, then refills to 13 by 1944.9 — legitimate exhaustion vs stall not determined.

### R5. GER AI deploys

- **Fix under test:** supply/deployment stack through Phase 2–4 (post-`982ebfd12`).
- **Pass:** GER division count grows through the war, field fill >95% (early/mid war — late-war 65% under low supply reach is by design, see F8 note), no equipment hoard.
- **Probe:** GER `units` fill sampling + stockpile trend across saves.
- **Threshold:** 5 (behavioural).
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER grows, fills, queues railways, fields no hoard.
  - 2026-08-10 · `66d6b53c` · PASSED — 98→327 divisions (peak 1944.6), training pipeline peaks 1943 and dries up by 1945 as expected; no hoard signal. Fill % not directly sampled this run.

### R6. Majors mechanize

- **Fix under test:** `5d2663848` + Tier 1 composition work.
- **Pass:** GER and SOV fielded armor+mech share >18% of the army.
- **Probe:** `units` composition sampling for GER and SOV in mid/late-war saves. **Probe gap found 2026-08-10:** no `wa_ai_template*` variable is ever written to saves, and divisions reference templates by numeric id only — composition share is not recoverable from a save. Add a script-side `*_dbg_*` armor-share counter before this item can be scored again.
- **Threshold:** 5 (behavioural).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER fields 27% armor.
  - 2026-08-10 · `66d6b53c` · NOT CHECKED — no save-visible composition metric (see probe gap). Weak equipment-demand proxy: GER medium-tank demand appears 1943 and scales into 1944; heavy tanks never appear at all.

### R7a. Lend-lease relief — support-equipment leg

- **Fix under test:** `128cc7995` (per-archetype pull model).
- **Pass:** GER-creator support equipment appears in ROM/HUN/BUL/ITA stockpiles.
- **Probe:** `creator="GER"` support-equipment entries in the recipient's `production` → `equipments` stockpile (resolve archetypes via the top-level `equipments={}` registry). **Do NOT use the diplomacy `lend_lease_to_allies_history` ledger — `send_equipment` transfers never touch it; zero ledger IC is a false negative.**
- **Threshold:** 5 (behavioural flow over time).
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — support flow confirmed. Caveat from `cbca536d`: absolute thresholds converge too low for big armies (ENG stabilized ~1.7k support for 97 divisions) — candidate follow-up fix, tracked in `campaign-audit-fix-plan`.
  - 2026-08-10 · `66d6b53c` · PASSED — GER-created support present in ROM and HUN at every sample 1942–1945, moving as a sawtooth (recurring weekly transfers, not one-time inheritance); 1943.3 spike: ROM 2 912 / HUN 3 886 while GER held 20.5k (the >14 999 → 2 400/pull tier).

### R7b. Lend-lease relief — infantry-equipment leg (recalibrated)

- **Fix under test:** `2d48a1a17` (35k/6k surplus, 4k support starving, common-enemy pairs).
- **Pass:** ROM/HUN rifle stockpiles off zero while GER holds surplus.
- **Probe:** recipient `production` → `equipments` infantry-equipment totals + `creator="GER"` share (same registry-resolution and ledger caveat as R7a).
- **Threshold:** 5 (behavioural).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — the recalibrated gate demonstrably fired: HUN GER-created rifles 10 → 6 975 between 1943.6 and 1943.9 with GER at 41 764 (over the new 34 999 gate, under 49 999 → base 6 000/pull — a delivery the old 60k gate would never have allowed). Caveat: the leg opens only in brief donor-surplus windows (GER above gate at 2/8 samples; in 1944 donor and recipients starve together and the leg is correctly gated off).

### R8. UK air hosting works

- **Fix under test:** `24ffda1ac` (level-ladder rewrite) + instrumentation `57d6136dd`.
- **Pass:** `wa_ai_uk_air_dbg_started > 0` on ENG; type-2 (air base) projects queued; USAAF wings based in the UK pre-D-Day.
- **Probe:** `var ENG "^wa_ai_uk_air_dbg" <saves...>`; `var ENG "^wa_ai_pc_building_type"`; USA wing basing via the top-level `strategic_air` block (wings → `air_base` id → `state=`; see R12 note).
- **Threshold:** 5 (behavioural — the wing-basing outcome is the point; the dbg variable alone is not a pass).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — `started` 22→74→102 from 1942.6 (engages exactly when planes overshoot capacity — the pre-1942 `best=-2` is correct gating); type-2 projects at Cornwall/Warwickshire/Gloucestershire; those states' air-base levels flat for 6 years then step 1–2 → 7–8; hosting capacity 3 400 → 8 500. **Caveat:** the USAAF barely used it — 3 wings / 500 planes on UK soil pre-D-Day vs 8 595 planes parked in CONUS. Construction leg is proven; consider a numeric wing bar for the basing leg (engine wing placement, not the WA project system).

### R9. Supply-line construction targets the right corridors

- **Fix under test:** `24ffda1ac` (pathfinder param rename) then `84528ae47` (**Fix 30** — subject/faction traversal for the state-level A*, break hygiene incl. the success-leak, controller-aware NA anchors, dynamic JAP anchor, type-14 excluded from the `<5` nonrail gate, `wa_ai_supply_line_dbg_*` instrumentation).
- **Pass:** build fingerprint `wa_ai_supply_line_dbg_called > 0` on ENG or ITA post-1937.6 (absence = pre-Fix-30 build, probe void). Then: ENG or ITA shows `dbg_pf_ok > 0` AND `dbg_queued > 0` with `dbg_last_state` in the NA corridor by ~1938–39; GER shows `dbg_queued > 0` within ~3 months of the GER–SOV war. JAP: `dbg_called > 0` while at war with RAJ; `dbg_queued = 0` is PASS only if JAP holds no ground within 10 BFS states of Delhi, FAIL otherwise. FAILED if `dbg_called > 0` with `dbg_pf_ok = 0` everywhere (A* still dead) or `dbg_pf_ok > 0` with `dbg_queued = 0` everywhere (queueing broken). Secondary: JAP produces type-2/3/4 projects after war start (nonrail gate actually unblocked). Retire the `WA_AI_supply_line_dbg_*` instrumentation with this item.
- **Probe:** `var <TAG> "^wa_ai_pc_building_type"` plus target state/province vars on ENG, GER, JAP. **Probe caveat (2026-08-10):** type-1 is also produced by resource-INF (`WA_AI_priority_queue_INF_resource` queues infrastructure on resource/steel-mill states) — a type-1 on a home steel state is NOT supply-line evidence. Until the supply-line strategy stamps its own project-type id, only a type-1 on a *corridor* state (between capital and the named front) counts.
- **Threshold:** 3 (narrow queue/target probe).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED — investigation showed **zero supply-line-origin projects for any country all campaign**; every observed type-1 was resource-INF (ENG's Norfolk = AI-built steel mill; GER's 855/42/810 = steel/radar states). Root causes found by audit: the type-1 pathfinder walks only ROOT-controlled states while the NA corridor anchors are subject-owned (Cairo=UKE, Tripoli=ITL — path dies at iteration 1; and the subjects can't afford projects); JAP is dispatcher-gated (type-14 port projects count toward the `<5 non-rail` gate, permanently false for the archipelago) with a hardcoded Shanghai anchor that could never reach Burma under the 75-pop A* cap; plus shared `break` temp-variable pollution can abort the A* in gate-open pulses.

### R10. USA army composition recovers

- **Fix under test:** `3da0be383` (mech/exped exclusivity, infantry floor +15 double-gated).
- **Pass:** USA infantry role want POSITIVE (`ai` section, `ai_strategy` type=9 role ratios) and USA fields >100 divisions by 1943.
- **Probe:** `section <save> USA ai --grep "type=9"` for role wants; `division={` count inside `units` for the division count (the `division_template_id` entries at country level are template definitions, not divisions; `units` line count absorbs the navy — don't use either as proxy).
- **Threshold:** 5 (behavioural).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED on threshold, but the fix's axis works: infantry want now **+86** (1943.6) / **+57** (1944.6) vs −29 pre-fix, and no collapse (bottomed at 47 vs 42 last campaign, then monotonic 47→61→96→120→133). The >100-by-1943 bar is missed — 61 at 1943.6, crossed only ~1944.1. Recovery real but ~a year late.

### R11. Factory floors hold

- **Fix under test:** `3da0be383` (tank/mech/amtrac production floors).
- **Pass:** USA tank factories ≥30 late-war; JAP tank factories ≥5; USA amtrac factories ≥8 with amtrac stockpile >0.
- **Probe:** production lines identify equipment by numeric `equipment_variant_index` — a name grep on `production` returns only MIO idea names. Resolve ids through the top-level `equipments={}` registry (USA tank/amtrac/cv_fighter variants are `tank_usa_*`, `usa_amphibious_mechanized_equipment_*`, `USA_f_*`); for JAP, resolve via `industrial_manufacturer` MIO id against `common/military_industrial_organization/organizations/JAP_organization.txt` (Sagami arsenal = tank line).
- **Threshold:** 3 (narrow factory-count probe).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — USA tanks 30 (1943.6) → 221 (1944.6); JAP Sagami tank line 15 → 68 factories; USA amtrac 0 at 1943.6 but 15 factories by 1944.6 with stockpile 1 008 at 1944.1 then 0 (absorbed straight into divisions — the healthy outcome). Anomaly: JAP's 68-factory tank line runs on **steel 0/272** at 1944.6 (fully supplied otherwise) — output far below nominal; separate finding.

### R12. Carrier fighters get built and deck wings fill

- **Fix under test:** `a5ea1fb84` (cv-plane ratios 150/100, min 2 default / 6 carrier-major).
- **Pass:** USA cv_fighter factories ≥6; carrier wings filling toward 10/10 strength.
- **Probe:** USA cv_fighter production lines (resolve variants via the `equipments={}` registry, see R11); wing fill via the top-level `strategic_air` block — wings link to `air_base` blocks by numeric id, and **carrier bases are the `air_base` blocks WITHOUT a `state=` key**. Decks being "empty" without checking this layout is a parsing artefact.
- **Threshold:** 5 (behavioural — wing fill over time is the outcome).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — 9 cv_fighter factories (≥6) at both 1943.6 and 1944.6; all 29 USA carrier decks manned, 2 306/2 650 planes = 87% fill, every wing slot filled (shortfall is per-wing attrition lag on the newest decks, 74–80/100). Note: 3 decks carry only cv_nav_bomber wings — unescorted; watch.

### R13. North Africa front moves

- **Fix under test:** `a5ea1fb84` (no-op — restored gate was self-contradictory) then `71e729d05` (**ITA offensive engine**: +60 `front_unit_request` on north_africa + posture-gated `front_control` toward Egypt, dbg stamps `ita_armor.915/.916`). The ENG-side re-fix of `africa_war_2` and the AIFC −150 suppression contract are still open follow-ups.
- **Pass:** build fingerprint `wa_ai_ita_dbg_r13_na_front = 1` on ITA after the ITA–ENG war starts; `wa_ai_ita_dbg_r13_na_offensive = 1` at least once. Behavioural (the point): Libya/Egypt state control (446–453, 663) changes hands at least once in either direction within 12 months of the desert war starting. No-suicide guard: with `posture_vs` at 0 for 3+ consecutive monthly saves, ITA's Libya holdings don't shrink >2 states/quarter while its defensive flag is set. Pre-fix baseline: 33 months frozen.
- **Probe:** state-level owner/controller of Libya/Egypt (446–452, 458) across war-time saves (province granularity does not exist in saves). Do NOT probe file-defined `ai_strategy` blocks in the `ai` section — they never serialize; only `add_ai_strategy` residue does (the `persistent_strategy type=83` entries are AIFC `front_armor_score`, id-keyed by **country** id, not region id).
- **Threshold:** 5 (behavioural front outcome). Interacts with R9 (NA supply lines) — score independently.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED — Libya/Egypt state control shows **zero changes from 1940.9 through 1943.6** (33 months frozen, worse than the +2-provinces baseline); by 1944.6 only two non-contiguous flips (Derna→ENG from the east, Tripoli→FRA from the west) with Sirte/Benghasi still Axis. **Root cause found by audit (2026-08-10):** (a) the restored `africa_war_2` gate is STILL dead — its `NOT = { <state list> }` is a NOR over the same states as the `OR`, a contradiction inherited from the original `a6fee253d` text; the fix under test cannot fire, in any campaign. (b) ITA has no offensive engine in NA at all (zero `front_unit_request`/`front_control` vs ENG in its Country file). (c) AIFC armor steering suppresses the Mediterranean enemy at −150 weekly once the schwerpunkt moves elsewhere (the earlier "+400 Eastern Ukraine/N.C. China" reading was a mis-decode: type=83 ids are country ids). Re-fix required before this item can pass.

### R14. Scripted-invasion attack penalty does not stack

- **Fix under test:** `17505d9a9` (guard on `has_relation_modifier` in `WA_AI_DIVISION_spawn_invasion`; `WA_AI_invasions.1` re-scoped to fire ON the target with `FROM` = invader; removed the `is_ai` / historical gates and the `most_recent_invasion_target` scalar).
- **Bug being fixed:** `WA_AI_invasions_modifier` (`attack_bonus_against = -0.25`) was added once per `WA_AI_DIVISION_spawn_invasion` call, not once per invasion. The expiry event then read a single overwritten scalar and cleared it on its first fire, leaving permanent stacks.
- **Pass:** on every major that runs scripted invasions (GER, JAP at minimum), `wa_ai_invasions_dbg_active` is **0 in every save**, and `wa_ai_invasions_dbg_adds` is **> 0** by mid-war with `adds == removes`. `adds == 0` means no invasion ever fired in that campaign → `NOT CHECKED`, not PASSED. A transient `_active = 1` or `2` in a save that happens to land inside a 14-day landing window is a PASSED with the caveat noted; `_active ≥ 3`, or any non-zero value that persists across consecutive monthly saves, is FAILED.
- **Probe:** `var JAP "^wa_ai_invasions_dbg" <saves...>` and the same for GER, across 1940–1945 saves. **JAP is the reliable probe target** (see `66d6b53c` history: GER's Norway operation did not route through `WA_AI_DIVISION_spawn_invasion` there — Weserübung left zero residue on GER while JAP carried heavy stacks). Cross-check a suspected failure against the live modifier: `section <save> JAP diplomacy --grep "WA_AI_invasions_modifier" --max-lines 0` — invader-side storage.
- **Why instrumentation:** the penalty's natural fingerprint lives only 14 days and monthly saves almost never land inside that window; the `*_dbg_*` counters exist so the probe is reliable on monthly cadence.
- **Threshold:** 3 (narrow variable probe — `_active` returning to 0 is a direct state check, not a behavioural outcome).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix and its instrumentation postdate every campaign in the registry.
  - 2026-08-10 · `66d6b53c` · NOT YET TESTED (fix not in build) — **bug presence confirmed pre-fix**: JAP `diplomacy` carried MAL ×4 + USA ×3 + UKO ×1 stacks at 1942.1 (i.e. JAP invaded Malaya at −100% and fought USA at −75% attack), and an AST ×1 stack persisting unchanged 1942.6 → 1945.6 — the permanent-residue signature. GER showed zero residue in 11 saves despite Weserübung (Norway fell 1940.3.1 via another path).

### R15. Air forces deploy to contested theatres

- **Fix under test:** `edb746d17` (generic Default-layer AIR domain: 10 theatre blocks, +10k per strategic region while contested — enemy AND own side both hold anchor states; capital-theatre excluded).
- **Pass:** by 1943.6 USA has ≥25% of deployed planes based outside the continental US, with USA wings at bases in NA/Mediterranean states (446/447/452, 458–460, 115/117/156) or Pacific island states (629 Hawaii, 634 Solomons, 633 Marshalls, 639/643/725 Micronesia, 1001–1004 New Guinea, 327/623–628 Philippines). Secondary: ENG's home-based RAF share does not increase vs the `66d6b53c` baseline; GER gains air presence over a contested Normandy post-landing. Baseline to beat: USA 62% CONUS (8 595/13 791).
- **Probe:** walk the top-level `strategic_air` block — wings → `air_base` id → `state=` — classify CONUS vs overseas per wing; count per theatre. (Carrier decks are the `air_base` blocks without `state=` — exclude them from this count.)
- **Launch-validation note:** two parse-risk constructs need the boot test (F9) before the next campaign: `has_deployed_air_force_size` without `type`, and `region = <id>` inside `capital_scope`. If the size trigger proves type-mandatory, drop that gate line.
- **Threshold:** 5 (behavioural — basing shares over time).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates every campaign in the registry.

---

## Recurring cosmetic anomalies — check here before reporting a "finding"

- **`ww2_*` theatre flags carry last-seen dates, not first-set dates.** They are re-stamped on every on_action fire, so their set-dates are useless as a war timeline — use the war/peace flags instead. (In `66d6b53c` all three read 1945.3.1.)
- **Double Trotsky flags** appear in SOV flag blocks; harmless duplication, not a political-path bug.
- **`atomic_research_completed` firing ~1940 is a research-tree marker, not a bomb.** It marks the research step, not weapon availability — do not report early nukes off this flag.
- **`production` stores equipment by numeric variant id.** A name grep (`--grep "tank"`) on the `production` section only hits MIO idea names — resolve `equipment_variant_index` via the top-level `equipments={}` registry before concluding a line doesn't exist.
- **`lend_lease_to_allies_history` misses `send_equipment` transfers.** The WA relief system moves stock instantly without touching the diplomacy IC ledger; zero ledger IC between two countries is NOT evidence of no equipment flow — check `creator=` tags in the recipient's stockpile.
- **`units` line count absorbs the navy** — it is a usable army-size trend proxy for land powers only; for USA/JAP count `division={` blocks instead.
