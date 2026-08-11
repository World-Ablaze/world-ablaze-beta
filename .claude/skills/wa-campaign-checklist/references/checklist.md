# Campaign verification checklist — living data file

**As of:** 2026-08-11 · last campaign scored: cloud `31eaf7e6` (BHU observer, 125 monthly saves 1936.2–1946.6, `dlcs=257535`). Build = the 2026-08-11 stack through at least `20f5d7597` (R16 fingerprint present; `2e3686fa1` committed ~2 min before the first save flushed — unprovable; Fix 34 `a3c2ef1a4` NOT in). R3 retired this session (3/3 on both tags). Headline: the SCW finally resolves on cloud (Franco 1939.4.3, F7 first PASSED) and R14/R18 (invasion penalty + sizes) both pass — but **the European war stalls after D-Day**: GER undefeated at 1946.6 (F5 first FAILED), ITA never capitulates (Avalanche stalls, Anzio beachhead destroyed), R9/R13/R15 still dead.

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
| `31eaf7e6` | cloud, `dlcs=257535` | BHU observer, 125 monthly saves 1936.2–1946.6, HOI4 1.19.2; build = 2026-08-11 stack (Fixes 30–33, ITA NA engine, R16, R17 all fingerprint-confirmed IN; `2e3686fa1` unprovable; Fix 34 out) | 2026-08-11 |

**DLC note (supersedes the old `dlcs=30` assumption):** the cloud box now ships `dlcs=257535` — La Résistance and Arms Against Tyranny both behaviourally confirmed in `66d6b53c` (LaR SCW flags, AAT MIO lines). Always read the save header's `dlcs=` per campaign instead of assuming by machine.

---

## FUNDAMENTAL — never removed

### F1. WW2 starts on time

- **Pass:** German–Polish war begins ~1939.9.1 (±4 months).
- **Probe:** global flags block near top of save (`flags` command, no TAG) — war-start flag set-dates; cross-check GER `diplomacy`.
- **Note:** the M-R pact focus manpower gate (`GER_mol_rib_pact` needs 1.5M army manpower under limited conscription) is the known variance source — see `campaign-audit-fix-plan` memory root-cause (a). Low priority; Barbarossa's hard date absorbs the delay.
- **Streak:** 3
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — war started 1940.1.17, 4.5 months late (outside ±4; M-R manpower gate, known variance).
  - 2026-08-10 · `cbca536d` · PASSED — war started 1939.9.1, on time.
  - 2026-08-10 · `66d6b53c` · PASSED — war started 1939.9.1 exactly (`GER_has_started_war` set 1939.9.1.8; Warsaw fell 1939.10.7).
  - 2026-08-11 · `31eaf7e6` · PASSED — war started 1939.10.11 (~6 weeks late, within ±4 months; M-R pact 1939.9.14, Warsaw fell 1939.11.19).

### F2. France falls on time

- **Pass:** France capitulates ~1940.6 (±3 months).
- **Probe:** global flags / FRA country block capitulation state; VP control of Paris.
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · NOT CHECKED — arc completed through German defeat (implies fall of France) but the date was not explicitly recorded; record it next run.
  - 2026-08-10 · `66d6b53c` · PASSED — Paris fell 1940.6.22, capitulation 1940.6.30 (`fall_of_france`), both near-exact historical dates.
  - 2026-08-11 · `31eaf7e6` · PASSED — Paris fell 1940.6.14, `fall_of_france` 1940.6.23 — exactly historical despite the 6-week-late war start.

### F3. Barbarossa fires

- **Pass:** GER–SOV war begins. Note it is hard-dated **1941.6.22** in `common/decisions/z_WA_ai_GER.txt` and silently absorbs upstream delays — a pass here says nothing about the war-start timeline.
- **Probe:** global flags war set-dates; SOV `diplomacy` section.
- **Streak:** 3
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER–SOV war fired on the anchored date; European war proceeded to conclusion.
  - 2026-08-10 · `66d6b53c` · PASSED — `barbarossa_counter` set 1941.6.22.17; Kiev fell 1941.9.24 (front moving on schedule).
  - 2026-08-11 · `31eaf7e6` · PASSED — war began 1941.6.22 exactly (proxy: GER country flag `SOV_third_five_year_plan_disruptor_flag` 1941.6.22.11; no dedicated global flag exists). Note: the front then ran SLOW — Kiev fell 1942.5.7 (8 months late), Sevastopol 1943.4.12.

### F4. Pearl Harbor / USA entry

- **Pass:** USA enters the war ~1941.12 (±3 months).
- **Probe:** USA `diplomacy` section, global war flags.
- **Streak:** 3
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — USA at war in the expected window (exact entry date not recorded; record it next run).
  - 2026-08-10 · `66d6b53c` · PASSED — `day_of_infamy_happened` 1941.12.4 (3 days early).
  - 2026-08-11 · `31eaf7e6` · PASSED — `day_of_infamy_happened` 1941.12.18 (11 days late).

### F5. Germany loses WW2 and the European war ends

- **Pass:** Germany is defeated and the European war terminates (white-peace chain or capitulation). Historical target ~1945.5; ending at all is the invariant, ending on time is the aspiration.
- **Probe:** global flags for the German white-peace chain; GER country state in late saves.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — scripted German white-peace chain fired 1946.9. Late vs ~1945.5 target but the war ENDS; lateness traces to the 4.5-month-late war start (F1).
  - 2026-08-10 · `66d6b53c` · NOT CHECKED — campaign truncated at 1945.6 with the war still running: GER uncapitulated and holds Berlin, but D-Day fired on time (1944.6.8), Allies are on German soil and GER carries the terminal-attrition idea set (`death_before_defeat`, `GER_werwolf`, `scraping_the_barrel`, `economy_fatigue_78`). Trajectory plausible for a 1946 white-peace as in `9be92c89`; unresolvable on a truncated run. If later saves of this campaign arrive, re-score.
  - 2026-08-11 · `31eaf7e6` · FAILED — Germany undefeated at campaign end 1946.6: holds Berlin, still occupies 14 FRA + 10 POL states; SOV (468 divisions) controls ZERO German states; Allies hold only 7. Zero global flags after `d_day_happened` 1944.6.8 — the war STALLS rather than merely running late. User-diagnosed proximate cause at 1944.7: the D-Day beachhead has no logistics (Normandy hubs at 18–31 demand vs 5 capacity, territory Free-France-owned) — see R9's dead supply-line construction. Caveat: `9be92c89`'s white-peace chain fired 1946.9, 3 months past this campaign's end, but there the Allies were advancing; here it is a two-year stalemate.

### F6. Pacific war terminates — KNOWN GAP

- **Pass:** the Pacific war reaches a termination path (Japanese surrender chain).
- **Status:** **KNOWN GAP — no termination path exists in the mod.** Expected FAILED until the Japanese surrender chain is built (Tier 3 in `campaign-audit-fix-plan`); do not re-diagnose, do not count toward pathology findings.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — Japan frozen at 1942 extent through 1946.12; no termination mechanism fired (by design gap).
  - 2026-08-10 · `66d6b53c` · FAILED (known gap) — JAP undiminished at 1945.6 (units block larger than GER's); the Pacific contributes zero global flags after `fall_of_singapore` 1942.4.28 — 38 months dark.
  - 2026-08-11 · `31eaf7e6` · FAILED (known gap) — JAP undefeated at 1946.6, still occupying 1 USA + 1 AST state; `fall_of_singapore` 1943.11.4 (21 months late) is the last Pacific flag. New wrinkle: JAP's economy self-destructs anyway (steel 0 across 202 factories from 1944 — see the war-bonds finding), so a termination chain would now have material to work with.

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
  - 2026-08-11 · `31eaf7e6` · PASSED — **Franco won 1939.4.3** (`scw_over` + `nationalist_victory` + `SPR_franco_won`, near-historical); D02 annihilated (0 states, frozen husk from 1939.6 on). First cloud-LaR resolution; validates the aid-flow rebalance + `d5d88061d` brake exemption stack. Caveat: the global `spanish_civil_war` flag itself is never cleared on victory — cosmetic, added to the anomalies list below.

### F8. No major runs the old pathologies

- **Pass:** for every major: manpower not pinned at ceiling with falling division count; army-wide field fill ≥90%; no 100k+ equipment hoard sitting beside starving faction allies.
- **Probe:** per-major `units` fill sampling + stockpile vs allies' deficits; `var TAG "^wa_ai_"` deployment/lend-lease state. Cross-reads R5 (GER), R7 (relief legs), R10 (USA).
- **Note:** GER late-war 65% fill under the low supply-reach defines was ruled **by design** (Phase 1 rejection in `campaign-audit-fix-plan`) — do not count it here.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — USA collapsed to 42 divisions with 249k idle infantry equipment and 0 deploy conveyors from 1943.6; hoards moved to SOV/USA and unreachable neutrals (POR 116k). Fixes shipped since (`3da0be383`, `2d48a1a17`) — see R10/R7b.
  - 2026-08-10 · `66d6b53c` · PASSED — no major collapsed: GER 98→327 divisions, SOV army +140%, USA recovered 47→133 (no repeat of the 42-division collapse). Caveats: field fill not sampled this run; USA infantry stock peaked at 101.7k at 1944.6 (vs 249k last campaign) and drained to 29k by 1945.6.
  - 2026-08-11 · `31eaf7e6` · PASSED — no major collapsed: GER 95→315 (then 231 at 1946.6 under combat attrition), USA 47→157 monotonic, SOV 371→468; USA infantry stock peaked 143.6k at 1944.6 then drained to 25.5k (healthy absorption). Caveats: field fill again not sampled; USA peak is 41% above last campaign's and borderline vs a 150k hoard bar; SOV army flat 371→381 over 1941.9–1943.6 (21 months) — pathology-adjacent, watch.

### F9. Game boots

- **Pass:** the build the campaign runs on launches without CTD. Scored per build, before the campaign: run the launch harness after any commit touching `force_concentration` blocks in country ai_strategy files — the deterministic-CTD lesson is that `GER_fall_gelb` + `war_with_soviets` fc entries are load-bearing (see comments in `common/ai_strategy/GER.txt` and the `d69eef2fa` incident).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — build through `083b224ac` booted on the cloud box and ran 9.5 game-years without CTD. (HEAD adds only `17505d9a9` + docs on top; boot-test HEAD before the next campaign anyway.)
  - 2026-08-11 · `31eaf7e6` · PASSED — the 2026-08-11 stack (Fixes 30–33, R15/R16/R17) booted on the cloud box and ran 10.4 game-years without CTD; R15's two flagged parse-risk constructs cleared in campaign conditions.

---

## RETIREABLE — fix verifications

Delete an item when its streak reaches its threshold (3 = narrow probe, 5 = behavioural).

*Retired 2026-08-10 (streak 3/3 on `66d6b53c`): R2 (PC factory allocation, fix `974bad6f7`) and R4 (rubber shortage tracker, fix `974bad6f7`).*

*Retired 2026-08-11 (streak 3/3 on both tags, `31eaf7e6`): R3 (land majors queue type-13 railways, fix `3c55b9d17` Fix 29/29b). Final pass: SOV 74/75 rail slots at 1944.6; GER 12 type-13 at 1944.3 — the previous campaign's zero-railway hole did not repeat (the whole queue dips 49→17 slots at 1944.3 with `override_max_factories_factor=0.5` active, then refills to 42; railways survive the dip). Durable note: type 14 counts as rail-family in `wa_ai_pc_active_nonrail_projects`.*

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
  - 2026-08-11 · `31eaf7e6` · PASSED — first from-start cloud confirmation: age cycles (values 1/3/4 across 11 GER+SOV samples, never pinned), `sector_states_ref` present wherever a sector exists, and corridors are STABLE — GER's anchor+states+refs byte-identical across two separate 26-week windows (anchor 265, then 245): validity holds and re-selection re-converges instead of thrashing. Anomalies logged: GER 1943.3 degenerate 1-state sector at out-of-cluster anchor 137; SOV sector fully cleared at the 1943.9 snapshot while unambiguously at war (eligibility gate dropped it); sampling note — 26-week save gaps cannot resolve re-selection frequency (a full cycle is ≤5 weeks).

### R5. GER AI deploys

- **Fix under test:** supply/deployment stack through Phase 2–4 (post-`982ebfd12`).
- **Pass:** GER division count grows through the war, field fill >95% (early/mid war — late-war 65% under low supply reach is by design, see F8 note), no equipment hoard.
- **Probe:** GER `units` fill sampling + stockpile trend across saves.
- **Threshold:** 5 (behavioural).
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER grows, fills, queues railways, fields no hoard.
  - 2026-08-10 · `66d6b53c` · PASSED — 98→327 divisions (peak 1944.6), training pipeline peaks 1943 and dries up by 1945 as expected; no hoard signal. Fill % not directly sampled this run.
  - 2026-08-11 · `31eaf7e6` · PASSED — 95→315 divisions (peak 1945.6), railway queue healthy all war, no hoard signal; first net-negative interval 315→231 over 1945.6–1946.6 under the late-war multi-front attrition. Fill % again not sampled.

### R6. Majors mechanize

- **Fix under test:** `5d2663848` + Tier 1 composition work.
- **Pass:** GER and SOV fielded armor+mech share >18% of the army.
- **Probe:** `units` composition sampling for GER and SOV in mid/late-war saves. **Probe gap found 2026-08-10:** no `wa_ai_template*` variable is ever written to saves, and divisions reference templates by numeric id only — composition share is not recoverable from a save. Add a script-side `*_dbg_*` armor-share counter before this item can be scored again.
- **Threshold:** 5 (behavioural).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER fields 27% armor.
  - 2026-08-10 · `66d6b53c` · NOT CHECKED — no save-visible composition metric (see probe gap). Weak equipment-demand proxy: GER medium-tank demand appears 1943 and scales into 1944; heavy tanks never appear at all.
  - 2026-08-11 · `31eaf7e6` · NOT CHECKED — probe gap unchanged (the `*_dbg_*` armor-share counter has still not been shipped). Weak proxy: USA role wants show medium_armor 230 + modern_armor 115 vs infantry 57 at 1944.6 — armor-heavy intent at least.

### R7a. Lend-lease relief — support-equipment leg

- **Fix under test:** `128cc7995` (per-archetype pull model).
- **Pass:** GER-creator support equipment appears in ROM/HUN/BUL/ITA stockpiles.
- **Probe:** `creator="GER"` support-equipment entries in the recipient's `production` → `equipments` stockpile (resolve archetypes via the top-level `equipments={}` registry). **Do NOT use the diplomacy `lend_lease_to_allies_history` ledger — `send_equipment` transfers never touch it; zero ledger IC is a false negative.**
- **Threshold:** 5 (behavioural flow over time).
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — support flow confirmed. Caveat from `cbca536d`: absolute thresholds converge too low for big armies (ENG stabilized ~1.7k support for 97 divisions) — candidate follow-up fix, tracked in `campaign-audit-fix-plan`.
  - 2026-08-10 · `66d6b53c` · PASSED — GER-created support present in ROM and HUN at every sample 1942–1945, moving as a sawtooth (recurring weekly transfers, not one-time inheritance); 1943.3 spike: ROM 2 912 / HUN 3 886 while GER held 20.5k (the >14 999 → 2 400/pull tier).
  - 2026-08-11 · `31eaf7e6` · PASSED — GER-created support present and dominant in ROM/HUN at all 5 samples 1942.6–1945.3 (63–100% of recipient stock), recurring. Caveats: recipients pinned in the 4.0–6.5k drip band straddling the 3 999 starving line; GER's own support stock drains 16.8k→7.4k toward the 5 999 export floor — the leg will self-shut if the trend continues.

### R7b. Lend-lease relief — infantry-equipment leg (recalibrated)

- **Fix under test:** `2d48a1a17` (35k/6k surplus, 4k support starving, common-enemy pairs).
- **Pass:** ROM/HUN rifle stockpiles off zero while GER holds surplus.
- **Probe:** recipient `production` → `equipments` infantry-equipment totals + `creator="GER"` share (same registry-resolution and ledger caveat as R7a).
- **Threshold:** 5 (behavioural).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — the recalibrated gate demonstrably fired: HUN GER-created rifles 10 → 6 975 between 1943.6 and 1943.9 with GER at 41 764 (over the new 34 999 gate, under 49 999 → base 6 000/pull — a delivery the old 60k gate would never have allowed). Caveat: the leg opens only in brief donor-surplus windows (GER above gate at 2/8 samples; in 1944 donor and recipients starve together and the leg is correctly gated off).
  - 2026-08-11 · `31eaf7e6` · NOT CHECKED — the mechanism never ran: GER cleared the >34 999 donor gate at exactly one sample (1943.9, 36 062 — of which only 17.3k GER-created; the gate opened on captured war booty) while neither recipient was starving (<10k) on that date; on the dates ROM/HUN do starve (1944.6, 1945.3) GER sits below the gate. Zero GER-created rifles delivered all campaign. Finding for a follow-up: the donor/recipient gate windows never overlap for GER, and `has_equipment` reads a stockpile inflated by captures.

### R8. UK air hosting works

- **Fix under test:** `24ffda1ac` (level-ladder rewrite) + instrumentation `57d6136dd` + `124b2a3b6` (demand side: `Allies_dday_air` pre-arms 1944.2.1 with `Allies_dont_logi_strike_during_bob` standing down in step — +200k on region 239 live from February, so southern-England capacity finally has a pull to fill). New sub-probe: USAAF wings based in the UK at a **1944.3–1944.5 save** (pre-landing window), not just at 1944.6.
- **Pass:** `wa_ai_uk_air_dbg_started > 0` on ENG; type-2 (air base) projects queued; USAAF wings based in the UK pre-D-Day.
- **Probe:** `var ENG "^wa_ai_uk_air_dbg" <saves...>`; `var ENG "^wa_ai_pc_building_type"`; USA wing basing via the top-level `strategic_air` block (wings → `air_base` id → `state=`; see R12 note).
- **Threshold:** 5 (behavioural — the wing-basing outcome is the point; the dbg variable alone is not a pass).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — `started` 22→74→102 from 1942.6 (engages exactly when planes overshoot capacity — the pre-1942 `best=-2` is correct gating); type-2 projects at Cornwall/Warwickshire/Gloucestershire; those states' air-base levels flat for 6 years then step 1–2 → 7–8; hosting capacity 3 400 → 8 500. **Caveat:** the USAAF barely used it — 3 wings / 500 planes on UK soil pre-D-Day vs 8 595 planes parked in CONUS. Construction leg is proven; consider a numeric wing bar for the basing leg (engine wing placement, not the WA project system).
  - 2026-08-11 · `31eaf7e6` · FAILED — the construction leg is alive (`started` 13→52→83, capacity 3.9k→7.1k, ENG home air bases reach level 8–9) but the basing outcome — the point of the item — is absent: ZERO USA planes based in the UK at 1943.6 and a single 98-plane wing at 1944.6.1 (pre-D-Day), worse than `66d6b53c`'s 500. Second defect: ENG planes/capacity worsens to 3.5× at 1944.6 (+1.4k capacity added against +13.2k planes).
  - 2026-08-11 · code audit — the basing gap is R15's root cause (see R15: net-negative Allied air ledger; between the fall of France and 1944.5.15 NO positive-importance region is reachable from an English airfield, so the USAAF has no reason to cross the Atlantic — the single wing appears in exactly `Allies_dday_air`'s 6-week window). The 3.5× ratio is NOT a stale input: the target formula tracks fleet correctly (faction planes × 0.5) but is throttled by `queue_max = 3` × 1 level/project and structurally capped at 11 states × level 12 = 13 200 capacity — already reached vs a ~25k-plane faction. Real accounting bug found: the queue scan (`strategies.txt:970-974`) counts ANY type-2 project as UK hosting, including theatre-air-base projects elsewhere (bounded +300). Do not chase the capacity leg further until the demand ledger (R15 fix A/B) ships.

### R9. Supply-line construction targets the right corridors

- **Fix under test:** `24ffda1ac` (pathfinder param rename) then `84528ae47` (**Fix 30** — subject/faction traversal for the state-level A*, break hygiene incl. the success-leak, controller-aware NA anchors, dynamic JAP anchor, type-14 excluded from the `<5` nonrail gate, `wa_ai_supply_line_dbg_*` instrumentation).
- **Pass:** build fingerprint `wa_ai_supply_line_dbg_called > 0` on ENG or ITA post-1937.6 (absence = pre-Fix-30 build, probe void). Then: ENG or ITA shows `dbg_pf_ok > 0` AND `dbg_queued > 0` with `dbg_last_state` in the NA corridor by ~1938–39; GER shows `dbg_queued > 0` within ~3 months of the GER–SOV war. JAP: `dbg_called > 0` while at war with RAJ; `dbg_queued = 0` is PASS only if JAP holds no ground within 10 BFS states of Delhi, FAIL otherwise. FAILED if `dbg_called > 0` with `dbg_pf_ok = 0` everywhere (A* still dead) or `dbg_pf_ok > 0` with `dbg_queued = 0` everywhere (queueing broken). Secondary: JAP produces type-2/3/4 projects after war start (nonrail gate actually unblocked). Retire the `WA_AI_supply_line_dbg_*` instrumentation with this item.
- **Probe:** `var <TAG> "^wa_ai_pc_building_type"` plus target state/province vars on ENG, GER, JAP. **Probe caveat (2026-08-10):** type-1 is also produced by resource-INF (`WA_AI_priority_queue_INF_resource` queues infrastructure on resource/steel-mill states) — a type-1 on a home steel state is NOT supply-line evidence. Until the supply-line strategy stamps its own project-type id, only a type-1 on a *corridor* state (between capital and the named front) counts.
- **Threshold:** 3 (narrow queue/target probe).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED — investigation showed **zero supply-line-origin projects for any country all campaign**; every observed type-1 was resource-INF (ENG's Norfolk = AI-built steel mill; GER's 855/42/810 = steel/radar states). Root causes found by audit: the type-1 pathfinder walks only ROOT-controlled states while the NA corridor anchors are subject-owned (Cairo=UKE, Tripoli=ITL — path dies at iteration 1; and the subjects can't afford projects); JAP is dispatcher-gated (type-14 port projects count toward the `<5 non-rail` gate, permanently false for the archipelago) with a hardcoded Shanghai anchor that could never reach Burma under the 75-pop A* cap; plus shared `break` temp-variable pollution can abort the A* in gate-open pulses.
  - 2026-08-11 · `31eaf7e6` · FAILED — Fix 30 is in the build (`dbg_called` present: ENG 92→102, ITA 2) but `dbg_pf_ok`/`dbg_queued`/`dbg_last_state` are ABSENT everywhere = the state-level A* returned success **zero times in 104 pulses** (the item's explicit still-dead signature). Worse, two upstream blocks: GER and JAP never reach the effect at all (`dbg_called` absent — dispatcher-blocked), and ENG's calls stall after 1940 (92 by 1939.6, +10 over the next four years). Campaign consequence now user-confirmed: the D-Day beachhead starves (Normandy hubs 18–31 demand vs 5 capacity at 1944.7) with no Allied path to build logistics in Free-France-owned Normandy — this item is on the critical path of F5.

### R10. USA army composition recovers

- **Fix under test:** `3da0be383` (mech/exped exclusivity, infantry floor +15 double-gated).
- **Pass:** USA infantry role want POSITIVE (`ai` section, `ai_strategy` type=9 role ratios) and USA fields >100 divisions by 1943.
- **Probe:** `section <save> USA ai --grep "type=9"` for role wants; `division={` count inside `units` for the division count (the `division_template_id` entries at country level are template definitions, not divisions; `units` line count absorbs the navy — don't use either as proxy).
- **Threshold:** 5 (behavioural).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED on threshold, but the fix's axis works: infantry want now **+86** (1943.6) / **+57** (1944.6) vs −29 pre-fix, and no collapse (bottomed at 47 vs 42 last campaign, then monotonic 47→61→96→120→133). The >100-by-1943 bar is missed — 61 at 1943.6, crossed only ~1944.1. Recovery real but ~a year late.
  - 2026-08-11 · `31eaf7e6` · PASSED — infantry want positive at both checkpoints (+86 / +57), no collapse (floor 47 at 1942.6, then 94→102→137→157), and the >100 bar is met at the 1944.1.1 snapshot (102 = end-1943 within monthly sampling; 94 already at 1943.6). Caveats: infantry want halves as modern_armor (115) comes online — watch the trend; USA stays structurally small vs GER 315 / SOV 468.

### R11. Factory floors hold

- **Fix under test:** `3da0be383` (tank/mech/amtrac production floors).
- **Pass:** USA tank factories ≥30 late-war; JAP tank factories ≥5; USA amtrac factories ≥8 with amtrac stockpile >0.
- **Probe:** production lines identify equipment by numeric `equipment_variant_index` — a name grep on `production` returns only MIO idea names. Resolve ids through the top-level `equipments={}` registry (USA tank/amtrac/cv_fighter variants are `tank_usa_*`, `usa_amphibious_mechanized_equipment_*`, `USA_f_*`); for JAP, resolve via `industrial_manufacturer` MIO id against `common/military_industrial_organization/organizations/JAP_organization.txt` (Sagami arsenal = tank line).
- **Threshold:** 3 (narrow factory-count probe).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — USA tanks 30 (1943.6) → 221 (1944.6); JAP Sagami tank line 15 → 68 factories; USA amtrac 0 at 1943.6 but 15 factories by 1944.6 with stockpile 1 008 at 1944.1 then 0 (absorbed straight into divisions — the healthy outcome). Anomaly: JAP's 68-factory tank line runs on **steel 0/272** at 1944.6 (fully supplied otherwise) — output far below nominal; separate finding.
  - 2026-08-11 · `31eaf7e6` · PASSED — USA tanks 98 (1943.6) → 190 (1944.6, peak 282 at 1944.9); USA amtracs 15/15 at 1944.6 with stock absorbed into divisions (the 1943.6 reading of 1/15 was a freshly opened line, ramped to 15/15 by 1944.3); JAP Sagami line 54→72. Anomalies: the amtrac line is entirely ABSENT at the 1944.9 snapshot then back at 15/15 by 1944.12 (cancel/re-add on variant upgrade?); JAP steel famine is now SYSTEMIC — 202 factories across 20 lines at steel 0 at 1944.6 vs zero deficits at 1943.6; root cause user-identified: JAP never takes war-bonds series C (see session findings), economy collapses during 1943→44.

### R12. Carrier fighters get built and deck wings fill

- **Fix under test:** `a5ea1fb84` (cv-plane ratios 150/100, min 2 default / 6 carrier-major).
- **Pass:** USA cv_fighter factories ≥6; carrier wings filling toward 10/10 strength.
- **Probe:** USA cv_fighter production lines (resolve variants via the `equipments={}` registry, see R11); wing fill via the top-level `strategic_air` block — wings link to `air_base` blocks by numeric id, and **carrier bases are the `air_base` blocks WITHOUT a `state=` key**. Decks being "empty" without checking this layout is a parsing artefact.
- **Threshold:** 5 (behavioural — wing fill over time is the outcome).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `66d6b53c` · PASSED — 9 cv_fighter factories (≥6) at both 1943.6 and 1944.6; all 29 USA carrier decks manned, 2 306/2 650 planes = 87% fill, every wing slot filled (shortfall is per-wing attrition lag on the newest decks, 74–80/100). Note: 3 decks carry only cv_nav_bomber wings — unescorted; watch.
  - 2026-08-11 · `31eaf7e6` · PASSED — 8 cv_fighter factories (≥6) at both checkpoints (9 by 1945.12); all decks manned (17/17, then 31/31). Degradations to watch: fill drops 94.3%→76.4% as decks double 17→31 against flat air production; 12 decks sit at exactly 50/100 with count=0 cv_nav_bomber wings (strike-side famine — only 8 USA_btd factories vs 1 298 fighters demand-met); the SAME 3 decks are unescorted in both saves (recurring from `66d6b53c` — stable assignment bug). Consider adding a cv_nav_bomber factory bar next to the fighter one.

### R13. North Africa front moves

- **Fix under test:** `a5ea1fb84` (no-op — restored gate was self-contradictory) then `71e729d05` (**ITA offensive engine**: +60 `front_unit_request` on north_africa + posture-gated `front_control` toward Egypt, dbg stamps `ita_armor.915/.916`). The ENG-side re-fix of `africa_war_2` and the AIFC −150 suppression contract are still open follow-ups.
- **Pass:** build fingerprint `wa_ai_ita_dbg_r13_na_front = 1` on ITA after the ITA–ENG war starts; `wa_ai_ita_dbg_r13_na_offensive = 1` at least once. Behavioural (the point): Libya/Egypt state control (446–453, 663) changes hands at least once in either direction within 12 months of the desert war starting. No-suicide guard: with `posture_vs` at 0 for 3+ consecutive monthly saves, ITA's Libya holdings don't shrink >2 states/quarter while its defensive flag is set. Pre-fix baseline: 33 months frozen.
- **Probe:** state-level owner/controller of Libya/Egypt (446–452, 458) across war-time saves (province granularity does not exist in saves). Do NOT probe file-defined `ai_strategy` blocks in the `ai` section — they never serialize; only `add_ai_strategy` residue does (the `persistent_strategy type=83` entries are AIFC `front_armor_score`, id-keyed by **country** id, not region id).
- **Threshold:** 5 (behavioural front outcome). Interacts with R9 (NA supply lines) — score independently.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED — Libya/Egypt state control shows **zero changes from 1940.9 through 1943.6** (33 months frozen, worse than the +2-provinces baseline); by 1944.6 only two non-contiguous flips (Derna→ENG from the east, Tripoli→FRA from the west) with Sirte/Benghasi still Axis. **Root cause found by audit (2026-08-10):** (a) the restored `africa_war_2` gate is STILL dead — its `NOT = { <state list> }` is a NOR over the same states as the `OR`, a contradiction inherited from the original `a6fee253d` text; the fix under test cannot fire, in any campaign. (b) ITA has no offensive engine in NA at all (zero `front_unit_request`/`front_control` vs ENG in its Country file). (c) AIFC armor steering suppresses the Mediterranean enemy at −150 weekly once the schwerpunkt moves elsewhere (the earlier "+400 Eastern Ukraine/N.C. China" reading was a mis-decode: type=83 ids are country ids). Re-fix required before this item can pass.
  - 2026-08-11 · `31eaf7e6` · FAILED — first post-fix campaign: both one-shot dbg stamps (`_na_front`, `_na_offensive`) set by 1940.9 — the gate held and the engine armed — yet **zero** state flips in the 12-month window; first flip at ~31 months (663→ENG, 1943.2), every flip is the Allies pushing WEST, and ITA never takes a single Egyptian state 1936–1946. ITA held 6 captured provinces at 1940.9 (province_capture=34), so there is sub-state movement that then dies.
  - 2026-08-11 · code audit + save falsification — **ITL ownership ruled a red herring** (all gates already accept ITL control; the 1940 province captures prove a live front). The audit's two lead hypotheses were then **falsified against the saves**: (1) the `EXEC_low_equipment_hold` latch never armed — ITA `wa_ai_fielded_eq_ratio` 0.894–0.974 all war, `WA_AI_defensive_front_strategy` flag absent in all six samples (`WA_AI_MILITARY_SYSTEM.md:235` already calls the flag long-orphaned; its 0.6 trip threshold looks unreachable for a major — dead code, not a latch); (2) `posture_vs_ENG` is NOT pinned at 0 — it cycles 1/0/1/1/2/0, so the priority-100 exec block's viability gate was OPEN at 4 of 6 samples and the offensive still produced nothing. **Diagnosis re-opened.** Remaining suspects, now the priority order: (a) NA logistics — both sides' desert supply construction is dead (R9: `WA_AI_improve_north_africa_infrastructure` Tripoli↔Cairo is one of the dead supply-line paths), so offensives may die of supply regardless of orders; (b) AIFC `front_armor_score id=ENG −150` weekly once ITA's schwerpunkt is Greece/SOV (`WA_AI_AIFC_helpers.txt:477-484`); (c) sheer force levels/theatre allocation in NA vs a reinforced ENG. Instrumentation fix still needed: replace the `fire_only_once` dbg stamps with weekly counters (armed-weeks, exec-open-weeks, NA division counts both sides) so the next campaign discriminates (a)/(b)/(c). `africa_war_2` NOR-contradiction confirmed still dead in HEAD but ENG-scope (would reduce ENG NA units) — not a cause of ITA passivity.

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
  - 2026-08-11 · `31eaf7e6` · PASSED — first from-start campaign with Fix 32: `removes` tracks `adds` on every tag at every sample (JAP 13/13, GER 3/2, USA 15/14, ENG 6/5 at 1945.6); `active`=0 outside landing windows (the three non-zero readings — JAP 1942.1/1942.6, USA 1944.6 — each coincide with a live landing sequence); full-save diplomacy scans at 6 dates show live `WA_AI_invasions_modifier` count == `active` exactly, with 0 at 1943.1, 1945.6 and 1946.6 — no orphan stacks, the old JAP→AST permanent-residue signature is gone. Benign residual: GER/USA/ENG each carry one dedup no-op add (adds−removes = active+1 — the anti-stack guard declining a duplicate; diplomacy scan confirms no modifier behind it).

### R15. Air forces deploy to contested theatres

- **Fix under test:** `edb746d17` (generic Default-layer AIR domain: 10 theatre blocks — enemy AND own side both hold anchor states; capital-theatre excluded) + `124b2a3b6` (pulls raised +10k→+50k AND the ENG.txt Allied suppression family retuned −250k…−1M → −2k…−40k, making the Allied European ledger net-positive in every contested region — worst case Poland/296 = +2k; this removes the `31eaf7e6` root cause). Watch item from the retune: +50k exceeds the engine's hot-front ~35k reference — air abandoning an active non-capital home front for a foreign contested theatre would be the over-correction signature.
- **Pass:** by 1943.6 USA has ≥25% of deployed planes based outside the continental US, with USA wings at bases in NA/Mediterranean states (446/447/452, 458–460, 115/117/156) or Pacific island states (629 Hawaii, 634 Solomons, 633 Marshalls, 639/643/725 Micronesia, 1001–1004 New Guinea, 327/623–628 Philippines). Secondary: ENG's home-based RAF share does not increase vs the `66d6b53c` baseline; GER gains air presence over a contested Normandy post-landing. Baseline to beat: USA 62% CONUS (8 595/13 791).
- **Probe:** walk the top-level `strategic_air` block — wings → `air_base` id → `state=` — classify CONUS vs overseas per wing; count per theatre. (Carrier decks are the `air_base` blocks without `state=` — exclude them from this count.)
- **Launch-validation note:** two parse-risk constructs need the boot test (F9) before the next campaign: `has_deployed_air_force_size` without `type`, and `region = <id>` inside `capital_scope`. If the size trigger proves type-mandatory, drop that gate line.
- **Threshold:** 5 (behavioural — basing shares over time).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `2b607968` (local, fix loaded mid-campaign 1943.3, probed 1943.7.15) · FAILED with caveats — USA at 71.7% CONUS (worse than the 62% baseline), **zero** USA planes in the contested Italy/Med theatre; ENG's 30% Med deployment is real but attributable to pre-existing ENG.txt specials; GER 70% east by engine combat terms, zero over Italy. Caveats: only 2.5 game-months since load; migration IS live (1 000-plane Newfoundland→Azores→Madeira ferry chain, ENG wings on Sicily 5 days post-landing); Med bases possibly RAF-saturated. **Suspected binding gap: no friendly in-range air-base capacity — the air-base-construction follow-up is the dependency to test next.** Re-score on a from-start campaign before concluding the pull values are wrong.
  - 2026-08-11 · `31eaf7e6` · FAILED — from-start scoring: USA 16.1% overseas at 1943.6 (bar ≥25%), i.e. 83.9% CONUS — worse than the 62% pre-fix baseline; 24.6% at 1944.6, still under the bar. Only ~700 planes across the Pacific islands at 1944.6; zero UK basing in 1943. Overseas placement is garrison scatter (100–300-plane singletons at Jamaica, Bahamas, Bermuda, Baja California, Lisbon, across four continents), not theatre mass.
  - 2026-08-11 · code audit — **root cause found, shared with R8: the Allied `strategic_air_importance` ledger is net-negative across all of Europe 1940→1944.** The `Allies_*` suppression family in `common/ai_strategy/ENG.txt` (`:508` −1M on German heartland 1941.10→1944.2, `:912`, `:1216`, `:1301`, `:1359` −250k…−1M on ~30 regions, all listing `original_tag = USA` and gated on whole-war-true conditions) drowns R15's +10k additively — the R15 file header even says so; the false premise was that those negatives were narrow emergencies. The garrison scatter is the engine falling back on its own armies×25 term (area-defence garrisons at ports/coastlines) — proof the demand channel works and just receives ≤0 everywhere. Verdict: R15 inert, not harmful; the 62→84% delta is campaign variance. Fix order: (A) retune the suppression family to −20k…−40k (blast radius: ENG/FRA/CAN/AUS/NZL/SAF/RAJ share the allowed lists); (B) standing positive on the German heartland once a bomber arm exists; (C) arm `Allies_dday_air` (+200k on 239, currently 1944.5.15→1944.7.1 only — the exact window the single USAAF wing appeared) on invasion-prepared instead of France-partly-liberated; (D) only then revisit R15's contested gate (add a staging notion) and its deliberate UK-region omission.

### R16. Theatre air-base construction fills contested theatres without overbuilding

- **Fix under test:** `20f5d7597` (**`WA_AI_build_theatre_air_bases`** in `WA_AI_CONSTRUCTION_PRIORITY_strategies.txt — PC type-2 projects in contested-theatre member states via the `WA_AI_MILITARY_AIR_theatre_state_*` triggers; side-wide capacity-deficit gate at 25% of side planes / theatre; level ladder to 4 per state; allied-build branch; includes the post-live-test dbg_started queue-growth fix). This is R15's declared dependency — score both, independently.
- **Pass:** build fingerprint `wa_ai_thair_dbg_called > 0` on USA/ENG/JAP once at war (absence = pre-fix build, probe void). Then: `wa_ai_thair_dbg_started > 0` on at least one major with a contested theatre, with type-2 PC projects on theatre member states; behavioural: for the side fighting the Pacific war, summed air-base levels across the island-chain states (629, 634, 633, 639/643/725, 638/646/863, 1001–1004, 327/623–628) rise from the `66d6b53c` flatline, individual states reaching 2–4 by ~1944. **Overproduction guard (the guardrail is part of the pass):** `dbg_active` drops to 0 on later saves once side capacity meets the target (levels plateau, not monotonic to slot-cap); minors sharing the theatre (e.g. CAN) show `dbg_started` at 0 or a small fraction of the majors'; no type-2 project from this system ever appears OUTSIDE a theatre member state (a Vladivostok/home-soil air-base spree = FAIL).
- **Probe:** `var <TAG> "^wa_ai_thair_dbg" <saves...>` on USA/ENG/JAP/CAN; `var <TAG> "^wa_ai_pc_building_type"` + target-state vars to attribute type-2 projects to member states; state `air_base` building levels on the island-chain states across saves. Retire the `WA_AI_thair_dbg_*` instrumentation with this item.
- **Launch-validation note:** ~~needs the boot test (F9)~~ CLEARED 2026-08-11 — live test booted with zero `error.log` mentions of the new names; all three flagged constructs work.
- **Probe caveat (2026-08-11):** `wa_ai_thair_dbg_started` values from the live-test build OVER-COUNT — the counter incremented even when `WA_AI_PC_start_project` declined internally (queue_max/dedup), fixed post-test with a queue-growth check. ENG's type-2 queue slots can be fully occupied by UK-hosting (R8) projects — its theatre starts were permanent no-ops; a shared `queue_max = 3` across both air strategies is a known limit, not a bug. Attribute type-2 projects to the correct strategy via target state (UK states → R8, theatre member states → R16).
- **Threshold:** 5 (behavioural — capacity appearing AND plateauing is the outcome).
- **Streak:** 1
- **History:**
  - 2026-08-11 · `31eaf7e6` · PASSED — first from-start campaign: fingerprint present on USA/ENG/JAP/CAN; island-chain air-base sum rises 28→32→35→40 (1942.6→1945.6) from the `66d6b53c` flatline, six states move, individual states reach 2–4 by 1944, plateau ≤4 holds (sole exception: 1002 NW Papua 1→5 in the year after an INS→IPI owner change — likely transfer artefact, watch). Deficit gate discriminates (JAP `active`=0 with met target; Allied `active` 4–5 = the documented slot-bounded terminal state). Caveats: total effect small (+12 levels over 3 years); the entire IPP-owned Philippine group 623–628 flatlines at 0 — the allied-build branch never reaches IPP territory; CAN `started`=14 vs USA 31 is more than the 'small fraction' the guard expects.
  - 2026-08-11 · `2b607968` (local live test, fix loaded at 1943.4.1, run to 1943.9.1) · PASSED (smoke — mid-campaign load, needs a from-start campaign for a full score) — system fired on both sides: +32 air-base levels across 21 member states in 5 months (pacific 28→36, burma_india 6→19, scandinavia 13→19, north_africa 56→60, italy 41→42), **zero** growth past level 4, **zero** builds outside member states, states already >4 untouched (ladder exclusion works). Deficit gate provably filtered theatres on the Axis-Pacific side (JAP `dbg_active` 2→1 of 4 contested); Allied island theatres never close their 33-level target (slot-bounded — terminal state is the cheap `ladder exhausted` no-op, by design). Negatives clean: SOV and FRA never enter (no dbg vars — SOV blocked by the civ-floor/afford gate, correct), CAN built only in genuine side-deficit theatres (Burma/Pacific), nothing on home soil, no Vladivostok. Behavioural nuances observed: multi-country same-state pile-on (AUS+USA same day on 431) is real but harmless — the per-state cap absorbed it; ITA correctly switched to defending its own contested homeland (Abruzzo) post-Husky; GER/ROM/ITA used the allied-build branch into German-controlled Norway (dynamic-state-correct). Instrumentation over-count found and fixed (see probe caveat).

### R17. Italian campaign: Sicily held, mainland reached, Axis defends

- **Fix under test:** `f99217c39` (hold-Sicily bridge blocks, USA suppression window, `fall_achse` flag fix, ITA home buffer 0.15). **Husky size dependency:** the landing is 12 ENG + 8 USA = 20 divisions per Fix 33 (R18), NOT the 40 that `76dde84ed` briefly produced — criterion (1) was recalibrated accordingly.
- **Pass:** next campaign with a successful Husky: (1) Allied divisions on Sicily (115+1032) ≥ 12 two weeks after both states flip, Sicily never recaptured; (2) USA divisions present in region 238 during the bridge window (suppressions inert in-window); (3) USA divisions on the Italian mainland by 1943.9; (4) once GER sets `GER_fall_achse_prepared` (not at war with ITA), GER divisions in northern Italy (158/162/159/161/160/736/856/157/2) > 0 within 60 days; (5) ITA pre-invasion garrison on 115/1032/117/156 lighter than the `2b607968` baseline but non-zero.
- **Probe:** state controllers + division locations for the listed states across 1943.7–1943.10 saves; GER flag `GER_fall_achse_prepared` set-date; division-location counts per the province lists in `history/states/`.
- **Watch item (regression risk from the fix):** the reactivated fall_achse buffers let GER park up to 0.2 army-fraction in N. Italy while fighting SOV — watch eastern-front density; and the 0.15 buffer also lightens Campania/Calabria (Avalanche zone), single shared ratio.
- **Threshold:** 5 (behavioural campaign outcome).
- **Streak:** 0
- **History:**
  - 2026-08-11 · `31eaf7e6` · FAILED as written — two criteria miscalibrated, one vacuous, and a real theatre stall found. (1) Sicily flips between 1943.7.1 and 1943.8.1 and is NEVER recaptured ✓, but the Allied garrison is 7 at 1943.8.1 (≥12 only by 1943.9.1) — misses the ≥12-at-two-weeks bar; (2) PASSED — USA divisions on Sicily at every post-landing snapshot (suppressions inert in-window); (3) zero USA mainland divisions at 1943.9.1, but Avalanche/Slapstick fire at days=251 = 1943.9.9 — met by 1943.10.1 (USA 2 in Campania). **Recalibrate: '(3) by 1943.10' and '(1) ≥12 at the second monthly snapshot after the flip';** (4) NOT CHECKED/vacuous — `GER_fall_achse_prepared` never set because **ITA never capitulates** (holds Rome + ~105 divisions at 1944.6); (5) PASSED (9 ITA divisions pre-invasion across 115/1032/117/156; no baseline figure to judge 'lighter'). Theatre finding upstream of this item: the Italian campaign stalls on the Calabria/Campania line — Avalanche never takes Campania despite Allied divisions present (ENG 3 + USA 2 at 1943.10 vs ITA 8–9), and the Anzio beachhead (Shingle 1944.1.22, ENG 5 divisions, state 2 flips) is DESTROYED by 1944.4 — the theatre's only Axis recapture. Italy flips sides only 1945.9 by another path. `2e3686fa1` (bridge opens at landing) committed ~2 min before the first save flushed — unprovable in this build; re-score it next campaign.

### R18. Scripted-invasion sizes match the per-wave design (Fix 33 dead-code purge)

- **Fix under test:** Fix 33 on `ai-rework` (commit pending). Three parts: (a) 68 dead `_divisions_per_province` + `adjust_invasion_for_difficulty` pairs removed across 44 events in `events/WA_AI_invasions.txt` — **behaviour-neutral by construction**, the removed pairs were overwritten before any spawn; (b) `.47`/`.5` (Husky) reverted from Fix 32's 24/16 back to 12/8 — the `= 1` Fix 32 deleted was the deliberate half of a size-preserving infantry/armor split introduced by `608177207`, and `.4`/`.32`/`.35`/`.46`/`.75` still follow that idiom; (c) 5 orphaned `adjust_invasion_for_difficulty` calls removed, of which `.41` (Timor) was live on hard difficulty only — a bare re-adjust took it 3 → 6 → 12 divisions in one province.
- **Bug being fixed:** the dead pairs are day-one duplicated boilerplate (present with matching values at the original authoring commit `2aaec3200`) that later per-wave refactors left stranded at pre-refactor values. They misled Fix 32 into reading a live design value as residue. No campaign behaviour depended on them.
- **Pass:** (1) **Husky sizes** — landing-month save has ~12 ENG divisions in 1032 and ~8 USA in 115 on normal difficulty (this supersedes R14's old 24/16 sub-probe and is the same observation, score once and cite in both); (2) **no size regressions elsewhere** — the seven other scripted landings that are cheap to observe come in at their table values on normal: `.3` Weserübung 22 GER across Norway, `.2` D-Day 12 + `.34` Neptune 21 in Normandy, `.40` Mercury 12 on Crete (182), `.46`/`.4` Torch 12 + 14 in North Africa, `.75` Iceberg 6 on Okinawa. A landing arriving at **half or double** its table value means a pair that was not actually dead — that is the only failure mode this purge can introduce, and it is the thing to look for; (3) **`.41` Timor** — on a *hard*-difficulty run, the second Timor wave is 6/province, not 12 (on normal, 3 either way — unscoreable, mark `NOT CHECKED`); (4) game boots with no parse error touching `WA_AI_invasions.txt` or `WA_AI_DIVISION_CREATOR_effects.txt`.
- **Probe:** division-location counts per landing state in the landing-month save and the one after (`history/states/` province lists for 1032, 115, 182, 459, 458, 111, 1020/1017/142/143/144/110, Okinawa). No new instrumentation — the sizes are directly observable as divisions on the ground, and the full expected-value table is in the Fix 33 header comment at the top of `events/WA_AI_invasions.txt`.
- **Also verifies the `log = "yes"` removal** (`WA_AI_DIVISION_CREATOR_effects.txt:2355`, a debug leftover in the hard-difficulty `OR` gate): if it had been evaluating true, every landing above would come in at **exactly double** its table value on a normal-difficulty run. So criteria (1)+(2) passing at table value is simultaneously the evidence that the difficulty gate now works. A uniform 2× across all landings on normal = the gate is still short-circuited somewhere.
- **Threshold:** 3 (narrow — counting divisions on the ground at known states and dates, not a behavioural outcome).
- **Streak:** 1
- **History:**
  - 2026-08-11 · `31eaf7e6` · PASSED — Husky is 12 ENG / 8 USA per the design table, NOT 24/16 (national-delta method: ENG +8 / USA +4 across the landing month, net of ~3 weeks' conquest losses — incompatible with a 24/16 spawn; method validated on D-Day, which reproduces +21/+13 against a designed 21/12); Weserübung +15 net of Norway combat (22 designed) consistent; no landing anywhere at double table value → the hard-difficulty `log = "yes"` gate is no longer short-circuited. Timor sub-criterion (3) NOT CHECKED (normal difficulty). Caveat: both Husky components net to exactly 2/3 of design — attrition is the parsimonious read, but a partial spawn (2 provinces skipped per landing) would produce identical numbers; if the 2/3 ratio recurs next campaign, probe the spawn loop. Probe note: monthly saves never catch the landing day — use month-over-month national division deltas, validated against a known-good landing.

### R19. Starved priority-construction projects age out; no factories burn in hostile states (Fix 34)

- **Fix under test:** Fix 34 on `ai-rework` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`). Two parts: (a) the stall sweep's `queue^num > 5` gate replaced with `WA_AI_PC_assigned_factories_total > 0` — a project starved of factories for 25+ weeks is now cancelled whenever factories were flowing to *other* projects, regardless of queue length; (b) `WA_AI_PC_assign_factories` skips projects whose target state is hostile-controlled (same controller test as the completion path), freezing their progress instead of burning civ-weeks toward a completion that spawns nothing.
- **Bug being fixed:** `2b607968` @ 1943.9.1: ROM queue `[6,1,7,0]` — naval base slot 7 (prio 5000, 3000/3000, stall 17w) and air base slot 0 (prio 100, target state 143 no longer ROM-controlled, stall 17w, ~140 civ-days already burned) both starved behind prio-9999 railway segments, with the sweep unreachable at queue=4 ≤ 5. The old gate also allowed 5 starved nonrail projects to lock every `< 5` strategy gate shut permanently.
- **Pass:** on any campaign save carrying the fix, mid/late war: (1) no AI country has a queued project with `wa_ai_pc_stall_weeks^id > 26` while its `wa_ai_pc_assigned_factories_total > 0`; (2) no queued project whose target state is enemy-controlled has `wa_ai_pc_assigned_factories^id > 0`; (3) negative guard — a country with `assigned_factories_total = 0` (collapse/full occupation) keeps its stalled queue uncancelled: stall_weeks > 26 with total = 0 is correct behaviour there, not a failure; (4) railway construction still completes normally (the sweep must not eat live low-priority projects the week before they'd get factories — spot-check that cancelled ids were genuinely starved 25+ consecutive weeks via logging or save deltas).
- **Probe:** extract `wa_ai_pc_queue`, `wa_ai_pc_stall_weeks`, `wa_ai_pc_assigned_factories`, `wa_ai_pc_assigned_factories_total`, `wa_ai_pc_target_state` for all majors plus 2–3 occupied/front-line minors (ROM is the reference case); cross-check target-state controllers in the save's `states={}` block.
- **Threshold:** 3 (narrow — direct variable observation, no behavioural judgement).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates every campaign in the registry.
  - 2026-08-11 · `31eaf7e6` · NOT YET TESTED (fix not in build — `a3c2ef1a4` committed 02:10, saves flushed 00:42–01:55). Supporting observation for the bug: GER's queue dips 49→17 slots at 1944.3 with `override_max_factories_factor=0.5` active, refilling by 1944.9 — consistent with starvation dynamics the sweep should now handle.

### R20. Warbond ladder recovers from the fatigue-0 dead-end (Fix 35)

- **Fix under test:** `a03fc502b` (Fix 35). Two parts: (a) `upgrade_warbonds` arms a 30-day `warbonds_upgrade_retry_mission` when a completed series cannot advance (typically fatigue driven to exactly 0 by the final mission tick); the watcher re-calls `check_and_fire_auto_warbond_event` once `economic_fatigue > 9` and terminates on Series_G / repayment / opt-out / next series issuing; (b) history desyncs aligned — JAP/FIN start `economic_fatigue` at 5, YUG at 10, matching their starting ideas.
- **Bug being fixed:** campaign `31eaf7e6` — JAP completed Series_B at fatigue 0 in 1938.2 and stayed there to 1945 while fatigue ratcheted to 93 → `local_resources_factor −0.215` → iron deficit → `iron_shortage_ai` disabled 23/25 steel refineries → steel 0 across 202 factory lines. USA/CHI/FRA parked on Series_C by the same trap; only GER/ENG reached G.
- **Pass:** (1) no major at war with `economic_fatigue > 30` for 6+ months still holds the same bond series it completed — JAP specifically progresses past Series_B (probe: `ideas JAP <saves> --match "Series_"` across 1939–1944, plus `var JAP "^economic_fatigue"`); (2) at least one country shows `wa_warbonds_retry_upgrades ≥ 1` (fingerprint that the retry path fired; absent everywhere on a run where no ladder ever dead-ends is NOT a failure — check criterion 1 first); (3) no regression: GER/ENG still reach Series_F/G on the historical arc; (4) downstream: JAP active steel refineries stay > inactive ones through 1944 (`steel_refinery` vs `steel_refinery_inactive` in JAP-controlled states) — the economic collapse this fix targets does not recur.
- **Threshold:** 3 (narrow — idea/variable observation; criterion 4 is the behavioural corroboration, judge it as evidence not as a separate gate).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates every campaign in the registry.

### R22. Mulberry harbours spawn at D-Day and dismantle on schedule (Fix 36b)

- **Fix under test:** `763488d04`. Two level-5 naval bases set instantly at the scripted landing — province 3579 (Mulberry A, `WA_AI_invasions.2`) and 13851 (Mulberry B, `.34`) — removed 120 days later by `WA_AI_invasions.84` (idempotent double-fire by design).
- **Pass:** in the first campaign with a scripted D-Day: (1) the first post-landing save shows `naval_base` level 5 at provinces 3579 and 13851 (top-level `provinces={}` block); (2) a save ≥5 months post-landing shows them back at 0 (dismantled); (3) beachhead supply corroboration — the landing does not repeat the `31eaf7e6` capacity-5 starvation signature (Normandy hubs' demand/capacity gap closes vs that baseline, judged qualitatively with R21's port-healthy read).
- **Probe:** `provinces={}` naval_base levels at 3579/13851 in the landing-month save +1 and +5 months; cross-read R21 (Cherbourg/Le Havre healthy) and F5.
- **Threshold:** 3 (narrow — building levels at fixed provinces and dates).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates every campaign in the registry.

### R21. Port demolition is capped and gated (Fix 36)

- **Fix under test:** `b74f91889` (Fix 36). The `GER_nero_decree` on_action demolition (`100_wa_on_actions.txt`, `on_state_control_changed`) now requires the capturer to be at war with GER, fires once per state (state flag `WA_port_demolished`), and deals `clamp(level−3, 0, 4)` naval-base damage instead of a flat 10; the `scorch_earth` decision's naval_base component shares the cap and the flag guard. Ports ≤3 untouched.
- **Bug being fixed:** `fc76d9038` made demolition unconditional and total — campaign `31eaf7e6` had Brest 10→0 healthy, Cherbourg/Le Havre 5→0 at capture, starving the D-Day beachhead (F5/R9 chain).
- **Pass:** in the first campaign where the Allies capture Nero-decree French ports: (1) each captured port state with pre-capture level >3 carries `WA_port_demolished` and its naval_base shows healthy ≥ level−4 (concretely Brest ≥6 healthy, Cherbourg/Le Havre ≥3 healthy at the first post-flip save — combat damage on top is the accepted deviation, judge with the province `buildings` healthy value); (2) states with ports ≤3 (e.g. Loire 13853 level 2) carry NO flag and NO demolition; (3) no `WA_port_demolished` on any state that never flipped from Axis to an at-war-with-GER controller (ROOT gate leak check); (4) no port shows healthy < level−4 attributable to script (stacking guard held).
- **Probe:** top-level `provinces={}` block — `naval_base` level/healthy_levels for 6449 Cherbourg, 9434 Le Havre, 3552 Brest, 13853 in the first post-capture save; state flags via `flags` on the owning states (15, 1016, 14, 30).
- **Threshold:** 3 (narrow — direct building-state observation).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates every campaign in the registry.

---

## Recurring cosmetic anomalies — check here before reporting a "finding"

- **The global `spanish_civil_war` flag is never cleared on SCW resolution.** `scw_over` / `nationalist_victory` / `SPR_franco_won` are the authoritative end markers; the war flag still being set says nothing about the war still running (seen resolved-but-set in `31eaf7e6`).
- **`ww2_*` theatre flags carry last-seen dates, not first-set dates.** They are re-stamped on every on_action fire, so their set-dates are useless as a war timeline — use the war/peace flags instead. (In `66d6b53c` all three read 1945.3.1.)
- **Double Trotsky flags** appear in SOV flag blocks; harmless duplication, not a political-path bug.
- **`atomic_research_completed` firing ~1940 is a research-tree marker, not a bomb.** It marks the research step, not weapon availability — do not report early nukes off this flag.
- **`production` stores equipment by numeric variant id.** A name grep (`--grep "tank"`) on the `production` section only hits MIO idea names — resolve `equipment_variant_index` via the top-level `equipments={}` registry before concluding a line doesn't exist.
- **`lend_lease_to_allies_history` misses `send_equipment` transfers.** The WA relief system moves stock instantly without touching the diplomacy IC ledger; zero ledger IC between two countries is NOT evidence of no equipment flow — check `creator=` tags in the recipient's stockpile.
- **`units` line count absorbs the navy** — it is a usable army-size trend proxy for land powers only; for USA/JAP count `division={` blocks instead.
