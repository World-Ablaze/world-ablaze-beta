# Campaign verification checklist — living data file

**As of:** 2026-08-10 · last campaign scored: cloud `66d6b53c` (BHU observer, 1936.2–1945.6, `dlcs=257535` — first cloud run with LaR/AAT active). Build = Tier-1 stack through `083b224ac`, **without** `17505d9a9` (R14 fix). R2 and R4 retired this session (streak 3/3). R18 added (Fix 33 — invasion dead-code purge + Husky size revert); R14's and R17's Husky criteria recalibrated to 12/8.

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

- **Fix under test:** `17505d9a9` (stacking guard — verified working on `2b607968`) + `76dde84ed` (**Fix 32** — expiry re-homed to the INVADER: delayed events lose FROM, so the old target-side event never removed anything; pending pairs tracked in `WA_AI_invasions_pending_targets`, wholesale-cleared on expiry with a documented ≤14-day early-clear tradeoff). **Fix 32's Husky size change was reverted by Fix 33 (R18) — Husky is 12 ENG / 8 USA, not 24/16.**
- **Bug being fixed:** `WA_AI_invasions_modifier` (`attack_bonus_against = -0.25`) was added once per `WA_AI_DIVISION_spawn_invasion` call, not once per invasion. The expiry event then read a single overwritten scalar and cleared it on its first fire, leaving permanent stacks.
- **Pass:** wherever `dbg_adds > 0` on a major: (a) `dbg_removes > 0`; (b) `dbg_active = 0` in every save more than 14 days after that country's last scripted landing (transient 1–2 inside a window = PASSED with caveat); (c) `adds − removes` ≤ targets annexed mid-window (investigate if > 2); (d) the diplomacy grep for `WA_AI_invasions_modifier` and the `wa_ai_invasions_pending_targets` array are both empty outside landing windows. `adds == 0` everywhere → NOT CHECKED. FAILED on the `2b607968` signature (`removes = 0` while `adds > 0`) or any persistent non-zero `active`. **Husky sub-probe:** landing-month save shows ~12 ENG divisions in 1032 and ~8 USA in 115 (normal difficulty) — sizes per Fix 33, see R18.
- **Migration sub-probe (one-shot save repair, commit pending on `ai-rework`):** `WA_AI_invasions_migration_1` (`common/scripted_effects/WA_AI_MIGRATION_effects.txt`, **console-invoked — no on_action, by design**) sweeps every country pair and strips leftover `WA_AI_invasions_modifier` relation modifiers, because Fix 32 only cures NEW invasions — pre-fix pairs have no `WA_AI_invasions_pending_targets` entry and would stay penalised forever. **Pass:** on a **pre-fix campaign resumed on a migrated build and swept from the console** (e.g. `2b607968`), the first save written after the sweep has `section <save> <TAG> diplomacy --grep "WA_AI_invasions_modifier" --max-lines 0` **empty** for every major outside a live landing window — no GER→SOV, no USA/ENG→ITA residue — and global `wa_ai_invasions_migration_1_purged > 0` with global flag `wa_ai_invasions_migration_1_done` set. On a from-start campaign: flag set, `_purged = 0`. Any pre-fix residue surviving a post-migration load = FAILED (migration did not run or the meta-block sweep is silently no-oping). **Counter caveat:** the migration books a `dbg_removes` for each purged pair, so on a migrated save `adds − removes` is deliberately falsified for pre-fix pairs — score criterion (c) only on landings that happened *after* the migration ran, never across it.
- **Probe:** `var JAP "^wa_ai_invasions_dbg" <saves...>` and the same for GER, across 1940–1945 saves. **JAP is the reliable probe target** (see `66d6b53c` history: GER's Norway operation did not route through `WA_AI_DIVISION_spawn_invasion` there — Weserübung left zero residue on GER while JAP carried heavy stacks). Cross-check a suspected failure against the live modifier: `section <save> JAP diplomacy --grep "WA_AI_invasions_modifier" --max-lines 0` — invader-side storage.
- **Why instrumentation:** the penalty's natural fingerprint lives only 14 days and monthly saves almost never land inside that window; the `*_dbg_*` counters exist so the probe is reliable on monthly cadence.
- **Threshold:** 3 (narrow variable probe — `_active` returning to 0 is a direct state check, not a behavioural outcome).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix and its instrumentation postdate every campaign in the registry.
  - 2026-08-10 · `66d6b53c` · NOT YET TESTED (fix not in build) — **bug presence confirmed pre-fix**: JAP `diplomacy` carried MAL ×4 + USA ×3 + UKO ×1 stacks at 1942.1 (i.e. JAP invaded Malaya at −100% and fought USA at −75% attack), and an AST ×1 stack persisting unchanged 1942.6 → 1945.6 — the permanent-residue signature. GER showed zero residue in 11 saves despite Weserübung (Norway fell 1940.3.1 via another path).
  - 2026-08-11 · `2b607968` · **migration sub-probe PASSED — sweep logic verified end to end.** Save `USA_1943_04_01_11` (1943.4.1, taken 2 days after loading the 1943.3.30 save on a migrated build): global flag `WA_AI_invasions_migration_1_done` set at **1943.3.30.5**, the load date; global `wa_ai_invasions_migration_1_purged=5` — matching the baseline's 5 live pairs exactly; `dbg_removes` GER 1 / USA 1 / JAP 3 = 5, `dbg_adds` unchanged at 2/2/1/6 (no double-application); `dbg_active` **0 on all four**, down from 2/2/1/6; and the diplomacy grep for `WA_AI_invasions_modifier` is **empty on GER, USA, ENG, JAP, ITA and SOV** — GER→SOV, USA→JAP and JAP→{AST, USA, UKO} all gone. ENG correctly books 0 removes (its one add had already lost its target). **Scope of this verification:** it proves the three-pass sweep — pair enumeration through `meta_trigger`/`meta_effect` + `[?var.GetTag]`, the counter reset, the pending-array clear. It does NOT cover the console packaging committed afterwards (`df4201441`: guard removed, `_purged` accumulating instead of assigned, `log` line), since the running process predated that commit. Re-run the console path once to close that gap. **Probe navigation note:** `wa_ai_invasions_migration_1_purged` sits near the END of the save (~line 4.96M), not in the top-level globals block — a truncated scan will miss it and read as a failure.
  - 2026-08-10 · `2b607968` · **migration baseline (pre-migration probe, to diff against after the first load on the migrated build).** Stranded invader→target pairs, identified by walking `diplomacy → active_relations → <TAG>={` and pairing each `modifier="WA_AI_invasions_modifier"` with its enclosing relation key: at **1943.3.30** GER→SOV, USA→JAP, JAP→{AST, USA, UKO} = 5 live (counters GER 2/2, USA 2/2, ENG 1/1, JAP 6/6 — 11 adds for 5 live modifiers, the rest GC'd with annexed targets); at **1943.7.15** + USA→ITA, ENG→ITA (Husky, landed 1943.7.9) = 7; at **1944.2.1** (autosave, latest) GER→SOV, USA→{ITA, JAP}, ENG→ITA, JAP→{AST, USA, UKO} = **7 live pairs**, unchanged, i.e. Husky's −25% still on USA/ENG 6.5 months after a 14-day penalty should have lapsed, and GER→SOV unchanged for the 10 months the campaign covers. GER counters `adds=2 active=2` with only **1** live modifier → the second target no longer exists (relation garbage-collected), which is exactly why the migration needs pass C: pass B alone would leave GER at `active=1` forever. `wa_ai_invasions_dbg_removes` and `wa_ai_invasions_pending_targets` are **absent on every country** — confirms a pre-Fix-32 build, so Fix 32's removal path has nothing to walk and cannot heal this save. `wa_ai_invasions_migration_1_done` not set (never loaded on a migrated build). **Post-migration expectation:** all live pairs gone, `_purged` = the live count of whichever save is loaded (5 for the 1943.3.30 save, 7 for the 1944.2.1 autosave), every `active` → 0. **Two process caveats, both hit on 2026-08-10 — check them before scoring a FAILED:** (1) HOI4 parses all script at process start, so the game must be **fully restarted** after the mod files change; a save re-written at 23:46 by a process started at 23:29 (nine minutes before the migration files existed) produced a clean false negative. Compare the `hoi4` process start time against the mod file mtimes. (2) **the migration does not run by itself — it is a console tool, invoke it.** `on_startup` does NOT re-fire on savegame load (established on a correctly-ordered rerun: process 23:54:40 → save 23:57:03, files 23:38, mod path `E:/Projets/HOI4/WA/world-ablaze-beta` confirmed via `World Ablaze BETA.mod`, `error.log` free of script errors — a migration wired there alone left no global flag, and that flag is set *unconditionally*, so the body demonstrably never ran), and it was deliberately NOT re-hooked to a recurring pulse. Probe procedure: load the save, open the console, run `effect WA_AI_invasions_migration_1 = yes`, read the purge count straight out of `logs/game.log` (`WA_AI migration 1 (invasion penalties): purged N stranded pair(s).`), then save and probe the file. A probe save taken without that console step shows nothing and means nothing.
  - 2026-08-10 · `2b607968` (local, fix IN build) · **FAILED — the stacking half is cured, the removal half is still dead.** dbg at 1943.7.15: ENG 2/2, USA 3/3, GER 2/2, JAP 6/6 adds/active, `_removes` absent (=0) everywhere; live −25% stacks include **GER→SOV since ~1941** (Eastern-Front-scale distortion) and USA/ENG→ITA from Husky. Root cause: `WA_AI_invasions.1` is queued `days = 14` from the *target's* scope and its trigger needs `FROM = { has_relation_modifier target = ROOT }` — FROM does not arrive as the invader on a delayed event, the `is_triggered_only` trigger fails silently, nothing is ever removed. Fix direction: store the invader id on the target (or fire the delayed event on the invader with the target stored) so removal doesn't depend on delayed-event FROM.

### R15. Air forces deploy to contested theatres

- **Fix under test:** `edb746d17` (generic Default-layer AIR domain: 10 theatre blocks, +10k per strategic region while contested — enemy AND own side both hold anchor states; capital-theatre excluded).
- **Pass:** by 1943.6 USA has ≥25% of deployed planes based outside the continental US, with USA wings at bases in NA/Mediterranean states (446/447/452, 458–460, 115/117/156) or Pacific island states (629 Hawaii, 634 Solomons, 633 Marshalls, 639/643/725 Micronesia, 1001–1004 New Guinea, 327/623–628 Philippines). Secondary: ENG's home-based RAF share does not increase vs the `66d6b53c` baseline; GER gains air presence over a contested Normandy post-landing. Baseline to beat: USA 62% CONUS (8 595/13 791).
- **Probe:** walk the top-level `strategic_air` block — wings → `air_base` id → `state=` — classify CONUS vs overseas per wing; count per theatre. (Carrier decks are the `air_base` blocks without `state=` — exclude them from this count.)
- **Launch-validation note:** two parse-risk constructs need the boot test (F9) before the next campaign: `has_deployed_air_force_size` without `type`, and `region = <id>` inside `capital_scope`. If the size trigger proves type-mandatory, drop that gate line.
- **Threshold:** 5 (behavioural — basing shares over time).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `2b607968` (local, fix loaded mid-campaign 1943.3, probed 1943.7.15) · FAILED with caveats — USA at 71.7% CONUS (worse than the 62% baseline), **zero** USA planes in the contested Italy/Med theatre; ENG's 30% Med deployment is real but attributable to pre-existing ENG.txt specials; GER 70% east by engine combat terms, zero over Italy. Caveats: only 2.5 game-months since load; migration IS live (1 000-plane Newfoundland→Azores→Madeira ferry chain, ENG wings on Sicily 5 days post-landing); Med bases possibly RAF-saturated. **Suspected binding gap: no friendly in-range air-base capacity — the air-base-construction follow-up is the dependency to test next.** Re-score on a from-start campaign before concluding the pull values are wrong.

### R16. Theatre air-base construction fills contested theatres without overbuilding

- **Fix under test:** `20f5d7597` (**`WA_AI_build_theatre_air_bases`** in `WA_AI_CONSTRUCTION_PRIORITY_strategies.txt — PC type-2 projects in contested-theatre member states via the `WA_AI_MILITARY_AIR_theatre_state_*` triggers; side-wide capacity-deficit gate at 25% of side planes / theatre; level ladder to 4 per state; allied-build branch; includes the post-live-test dbg_started queue-growth fix). This is R15's declared dependency — score both, independently.
- **Pass:** build fingerprint `wa_ai_thair_dbg_called > 0` on USA/ENG/JAP once at war (absence = pre-fix build, probe void). Then: `wa_ai_thair_dbg_started > 0` on at least one major with a contested theatre, with type-2 PC projects on theatre member states; behavioural: for the side fighting the Pacific war, summed air-base levels across the island-chain states (629, 634, 633, 639/643/725, 638/646/863, 1001–1004, 327/623–628) rise from the `66d6b53c` flatline, individual states reaching 2–4 by ~1944. **Overproduction guard (the guardrail is part of the pass):** `dbg_active` drops to 0 on later saves once side capacity meets the target (levels plateau, not monotonic to slot-cap); minors sharing the theatre (e.g. CAN) show `dbg_started` at 0 or a small fraction of the majors'; no type-2 project from this system ever appears OUTSIDE a theatre member state (a Vladivostok/home-soil air-base spree = FAIL).
- **Probe:** `var <TAG> "^wa_ai_thair_dbg" <saves...>` on USA/ENG/JAP/CAN; `var <TAG> "^wa_ai_pc_building_type"` + target-state vars to attribute type-2 projects to member states; state `air_base` building levels on the island-chain states across saves. Retire the `WA_AI_thair_dbg_*` instrumentation with this item.
- **Launch-validation note:** ~~needs the boot test (F9)~~ CLEARED 2026-08-11 — live test booted with zero `error.log` mentions of the new names; all three flagged constructs work.
- **Probe caveat (2026-08-11):** `wa_ai_thair_dbg_started` values from the live-test build OVER-COUNT — the counter incremented even when `WA_AI_PC_start_project` declined internally (queue_max/dedup), fixed post-test with a queue-growth check. ENG's type-2 queue slots can be fully occupied by UK-hosting (R8) projects — its theatre starts were permanent no-ops; a shared `queue_max = 3` across both air strategies is a known limit, not a bug. Attribute type-2 projects to the correct strategy via target state (UK states → R8, theatre member states → R16).
- **Threshold:** 5 (behavioural — capacity appearing AND plateauing is the outcome).
- **Streak:** 1
- **History:**
  - 2026-08-11 · `2b607968` (local live test, fix loaded at 1943.4.1, run to 1943.9.1) · PASSED (smoke — mid-campaign load, needs a from-start campaign for a full score) — system fired on both sides: +32 air-base levels across 21 member states in 5 months (pacific 28→36, burma_india 6→19, scandinavia 13→19, north_africa 56→60, italy 41→42), **zero** growth past level 4, **zero** builds outside member states, states already >4 untouched (ladder exclusion works). Deficit gate provably filtered theatres on the Axis-Pacific side (JAP `dbg_active` 2→1 of 4 contested); Allied island theatres never close their 33-level target (slot-bounded — terminal state is the cheap `ladder exhausted` no-op, by design). Negatives clean: SOV and FRA never enter (no dbg vars — SOV blocked by the civ-floor/afford gate, correct), CAN built only in genuine side-deficit theatres (Burma/Pacific), nothing on home soil, no Vladivostok. Behavioural nuances observed: multi-country same-state pile-on (AUS+USA same day on 431) is real but harmless — the per-state cap absorbed it; ITA correctly switched to defending its own contested homeland (Abruzzo) post-Husky; GER/ROM/ITA used the allied-build branch into German-controlled Norway (dynamic-state-correct). Instrumentation over-count found and fixed (see probe caveat).

### R17. Italian campaign: Sicily held, mainland reached, Axis defends

- **Fix under test:** `f99217c39` (hold-Sicily bridge blocks, USA suppression window, `fall_achse` flag fix, ITA home buffer 0.15). **Husky size dependency:** the landing is 12 ENG + 8 USA = 20 divisions per Fix 33 (R18), NOT the 40 that `76dde84ed` briefly produced — criterion (1) was recalibrated accordingly.
- **Pass:** next campaign with a successful Husky: (1) Allied divisions on Sicily (115+1032) ≥ 12 two weeks after both states flip, Sicily never recaptured; (2) USA divisions present in region 238 during the bridge window (suppressions inert in-window); (3) USA divisions on the Italian mainland by 1943.9; (4) once GER sets `GER_fall_achse_prepared` (not at war with ITA), GER divisions in northern Italy (158/162/159/161/160/736/856/157/2) > 0 within 60 days; (5) ITA pre-invasion garrison on 115/1032/117/156 lighter than the `2b607968` baseline but non-zero.
- **Probe:** state controllers + division locations for the listed states across 1943.7–1943.10 saves; GER flag `GER_fall_achse_prepared` set-date; division-location counts per the province lists in `history/states/`.
- **Watch item (regression risk from the fix):** the reactivated fall_achse buffers let GER park up to 0.2 army-fraction in N. Italy while fighting SOV — watch eastern-front density; and the 0.15 buffer also lightens Campania/Calabria (Avalanche zone), single shared ratio.
- **Threshold:** 5 (behavioural campaign outcome).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fixes postdate every campaign in the registry.

### R18. Scripted-invasion sizes match the per-wave design (Fix 33 dead-code purge)

- **Fix under test:** Fix 33 on `ai-rework` (commit pending). Three parts: (a) 68 dead `_divisions_per_province` + `adjust_invasion_for_difficulty` pairs removed across 44 events in `events/WA_AI_invasions.txt` — **behaviour-neutral by construction**, the removed pairs were overwritten before any spawn; (b) `.47`/`.5` (Husky) reverted from Fix 32's 24/16 back to 12/8 — the `= 1` Fix 32 deleted was the deliberate half of a size-preserving infantry/armor split introduced by `608177207`, and `.4`/`.32`/`.35`/`.46`/`.75` still follow that idiom; (c) 5 orphaned `adjust_invasion_for_difficulty` calls removed, of which `.41` (Timor) was live on hard difficulty only — a bare re-adjust took it 3 → 6 → 12 divisions in one province.
- **Bug being fixed:** the dead pairs are day-one duplicated boilerplate (present with matching values at the original authoring commit `2aaec3200`) that later per-wave refactors left stranded at pre-refactor values. They misled Fix 32 into reading a live design value as residue. No campaign behaviour depended on them.
- **Pass:** (1) **Husky sizes** — landing-month save has ~12 ENG divisions in 1032 and ~8 USA in 115 on normal difficulty (this supersedes R14's old 24/16 sub-probe and is the same observation, score once and cite in both); (2) **no size regressions elsewhere** — the seven other scripted landings that are cheap to observe come in at their table values on normal: `.3` Weserübung 22 GER across Norway, `.2` D-Day 12 + `.34` Neptune 21 in Normandy, `.40` Mercury 12 on Crete (182), `.46`/`.4` Torch 12 + 14 in North Africa, `.75` Iceberg 6 on Okinawa. A landing arriving at **half or double** its table value means a pair that was not actually dead — that is the only failure mode this purge can introduce, and it is the thing to look for; (3) **`.41` Timor** — on a *hard*-difficulty run, the second Timor wave is 6/province, not 12 (on normal, 3 either way — unscoreable, mark `NOT CHECKED`); (4) game boots with no parse error touching `WA_AI_invasions.txt` or `WA_AI_DIVISION_CREATOR_effects.txt`.
- **Probe:** division-location counts per landing state in the landing-month save and the one after (`history/states/` province lists for 1032, 115, 182, 459, 458, 111, 1020/1017/142/143/144/110, Okinawa). No new instrumentation — the sizes are directly observable as divisions on the ground, and the full expected-value table is in the Fix 33 header comment at the top of `events/WA_AI_invasions.txt`.
- **Also verifies the `log = "yes"` removal** (`WA_AI_DIVISION_CREATOR_effects.txt:2355`, a debug leftover in the hard-difficulty `OR` gate): if it had been evaluating true, every landing above would come in at **exactly double** its table value on a normal-difficulty run. So criteria (1)+(2) passing at table value is simultaneously the evidence that the difficulty gate now works. A uniform 2× across all landings on normal = the gate is still short-circuited somewhere.
- **Threshold:** 3 (narrow — counting divisions on the ground at known states and dates, not a behavioural outcome).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates every campaign in the registry.

### R19. Starved priority-construction projects age out; no factories burn in hostile states (Fix 34)

- **Fix under test:** Fix 34 on `ai-rework` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`). Two parts: (a) the stall sweep's `queue^num > 5` gate replaced with `WA_AI_PC_assigned_factories_total > 0` — a project starved of factories for 25+ weeks is now cancelled whenever factories were flowing to *other* projects, regardless of queue length; (b) `WA_AI_PC_assign_factories` skips projects whose target state is hostile-controlled (same controller test as the completion path), freezing their progress instead of burning civ-weeks toward a completion that spawns nothing.
- **Bug being fixed:** `2b607968` @ 1943.9.1: ROM queue `[6,1,7,0]` — naval base slot 7 (prio 5000, 3000/3000, stall 17w) and air base slot 0 (prio 100, target state 143 no longer ROM-controlled, stall 17w, ~140 civ-days already burned) both starved behind prio-9999 railway segments, with the sweep unreachable at queue=4 ≤ 5. The old gate also allowed 5 starved nonrail projects to lock every `< 5` strategy gate shut permanently.
- **Pass:** on any campaign save carrying the fix, mid/late war: (1) no AI country has a queued project with `wa_ai_pc_stall_weeks^id > 26` while its `wa_ai_pc_assigned_factories_total > 0`; (2) no queued project whose target state is enemy-controlled has `wa_ai_pc_assigned_factories^id > 0`; (3) negative guard — a country with `assigned_factories_total = 0` (collapse/full occupation) keeps its stalled queue uncancelled: stall_weeks > 26 with total = 0 is correct behaviour there, not a failure; (4) railway construction still completes normally (the sweep must not eat live low-priority projects the week before they'd get factories — spot-check that cancelled ids were genuinely starved 25+ consecutive weeks via logging or save deltas).
- **Probe:** extract `wa_ai_pc_queue`, `wa_ai_pc_stall_weeks`, `wa_ai_pc_assigned_factories`, `wa_ai_pc_assigned_factories_total`, `wa_ai_pc_target_state` for all majors plus 2–3 occupied/front-line minors (ROM is the reference case); cross-check target-state controllers in the save's `states={}` block.
- **Threshold:** 3 (narrow — direct variable observation, no behavioural judgement).
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
