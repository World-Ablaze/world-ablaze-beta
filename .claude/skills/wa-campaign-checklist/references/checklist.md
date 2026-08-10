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
- **Probe:** global flag `spanish_civil_war` (still set = unresolved); SPR `politics` (Nationalists = neutrality) vs D02 (Republicans, democratic) alive-ness across saves.
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

- **Fix under test:** `4bfea363d` (1-based sector age) then `128cc7995` (validity scope leak) — **both failed to cure it**. Next step is live-log instrumentation on a running game, not another source patch.
- **Pass:** `wa_ai_aifc_sector_age` observed cycling through values 1–5 across a campaign's saves, not pinned at 1.
- **Probe:** `var <major TAG> "^wa_ai_aifc_sector_age" <saves...>` across the campaign.
- **Threshold:** 5 (behavioural — commitment-window dynamics over time).
- **Streak:** 0
- **History:**
  - 2026-08-09 · `0e7e7852` · FAILED — age pinned at 1 all campaign.
  - 2026-08-10 · `9be92c89` · FAILED — still pinned at 1 after the ROOT-hop fix; reproduced on `cbca536d` too.
  - 2026-08-10 · `66d6b53c` · FAILED — GER 14/14 samples at age 1 while `sector_anchor` moves (28→731→193→205→245→258→22): the loop runs and re-picks, but the age is reset instead of incremented; variable entirely absent in two snapshots (mid-clear). SOV identical. **New related evidence:** SOV `wa_ai_aifc_armor_boost` ≈ 10 791 with all 22 `_suppressed` entries clustered ~10 780–10 797 — an armor-steering accumulator that never resets, same reset-vs-increment defect family.

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

- **Fix under test:** `24ffda1ac` (pathfinder param rename revived the strategy).
- **Pass:** type-1 projects appear targeting North Africa (ENG/ITA), GER→SOV, and JAP→RAJ routes.
- **Probe:** `var <TAG> "^wa_ai_pc_building_type"` plus target state/province vars on ENG, GER, JAP.
- **Threshold:** 3 (narrow queue/target probe).
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED — the strategy runs but targets wrong or not at all. ENG: exactly **one** type-1 project in the whole campaign, targeting state 860 (Norfolk, England) — never North Africa. JAP: **zero** type-1 projects 1942–44 (queue is all type 13/14) — the RAJ leg never queued. GER: type-1 present (states 855/42/810, paired with type-4) but one 1943.6 slot shows build_time 1 473 days at 0 assigned factories — a dead slot squatting the queue.

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

- **Fix under test:** `a5ea1fb84` (ENG `africa_war_2` X-AND-NOT-X restored from pre-split `a6fee253d`).
- **Pass:** ENG reaches the `africa_war_2` posture and the North Africa front actually moves. Pre-fix baseline: +2 provinces in 24 months.
- **Probe:** ENG ai_strategy state in the `ai` section; state-level owner/controller of Libya/Egypt (446–452, 458) across war-time saves (province granularity does not exist in saves).
- **Threshold:** 5 (behavioural front outcome). Interacts with R9 (NA supply lines) — score independently.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `66d6b53c` · FAILED — Libya/Egypt state control shows **zero changes from 1940.9 through 1943.6** (33 months frozen, worse than the +2-provinces baseline); by 1944.6 only two non-contiguous flips (Derna→ENG from the east, Tripoli→FRA from the west) with Sirte/Benghasi still Axis. **Root-cause lead:** ENG's region-priority log (`persistent_strategy` type=83) pins Libya (215) at −150 in every sample and never touches Egypt/Sahara, while ENG's only +400 priorities are Eastern Ukraine (270) and North Central China (278) — nonsensical for the UK; find what writes those before patching `africa_war_2` again.

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

---

## Recurring cosmetic anomalies — check here before reporting a "finding"

- **`ww2_*` theatre flags carry last-seen dates, not first-set dates.** They are re-stamped on every on_action fire, so their set-dates are useless as a war timeline — use the war/peace flags instead. (In `66d6b53c` all three read 1945.3.1.)
- **Double Trotsky flags** appear in SOV flag blocks; harmless duplication, not a political-path bug.
- **`atomic_research_completed` firing ~1940 is a research-tree marker, not a bomb.** It marks the research step, not weapon availability — do not report early nukes off this flag.
- **`production` stores equipment by numeric variant id.** A name grep (`--grep "tank"`) on the `production` section only hits MIO idea names — resolve `equipment_variant_index` via the top-level `equipments={}` registry before concluding a line doesn't exist.
- **`lend_lease_to_allies_history` misses `send_equipment` transfers.** The WA relief system moves stock instantly without touching the diplomacy IC ledger; zero ledger IC between two countries is NOT evidence of no equipment flow — check `creator=` tags in the recipient's stockpile.
- **`units` line count absorbs the navy** — it is a usable army-size trend proxy for land powers only; for USA/JAP count `division={` blocks instead.
