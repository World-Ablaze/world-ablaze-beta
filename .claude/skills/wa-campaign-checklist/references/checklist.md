# Campaign verification checklist — living data file

**As of:** 2026-08-10 · last campaigns scored: cloud `9be92c89` (1936–1946.12, all-AI observer) and local `cbca536d` (SOV control run, full DLC). Latest item added: R14 (scripted-invasion penalty stacking), no campaign yet.

Protocol for scoring, retiring, and adding items: see `../SKILL.md`. Streak = consecutive PASSED; FAILED resets it to 0; `N/A (DLC)` / `NOT CHECKED` leave it untouched.

## Campaign registry (analysed to date)

| game_unique_id | Machine / DLC | Scope | Analysed |
| --- | --- | --- | --- |
| `0e7e7852` | cloud, `dlcs=30` | BHU observer, 119 monthly saves 1936–45 | 2026-08-09 |
| `c9ab1062` | cloud, `dlcs=30` | SCW-focused check | 2026-08-09 |
| `9be92c89` | cloud, `dlcs=30` | all-AI observer 1936–1946.12 | 2026-08-10 |
| `cbca536d` | local, `dlcs=191999` | SOV control run, full DLC | 2026-08-10 |

---

## FUNDAMENTAL — never removed

### F1. WW2 starts on time

- **Pass:** German–Polish war begins ~1939.9.1 (±4 months).
- **Probe:** global flags block near top of save (`flags` command, no TAG) — war-start flag set-dates; cross-check GER `diplomacy`.
- **Note:** the M-R pact focus manpower gate (`GER_mol_rib_pact` needs 1.5M army manpower under limited conscription) is the known variance source — see `campaign-audit-fix-plan` memory root-cause (a). Low priority; Barbarossa's hard date absorbs the delay.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — war started 1940.1.17, 4.5 months late (outside ±4; M-R manpower gate, known variance).
  - 2026-08-10 · `cbca536d` · PASSED — war started 1939.9.1, on time.

### F2. France falls on time

- **Pass:** France capitulates ~1940.6 (±3 months).
- **Probe:** global flags / FRA country block capitulation state; VP control of Paris.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `9be92c89` · NOT CHECKED — arc completed through German defeat (implies fall of France) but the date was not explicitly recorded; record it next run.

### F3. Barbarossa fires

- **Pass:** GER–SOV war begins. Note it is hard-dated **1941.6.22** in `common/decisions/z_WA_ai_GER.txt` and silently absorbs upstream delays — a pass here says nothing about the war-start timeline.
- **Probe:** global flags war set-dates; SOV `diplomacy` section.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER–SOV war fired on the anchored date; European war proceeded to conclusion.

### F4. Pearl Harbor / USA entry

- **Pass:** USA enters the war ~1941.12 (±3 months).
- **Probe:** USA `diplomacy` section, global war flags.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — USA at war in the expected window (exact entry date not recorded; record it next run).

### F5. Germany loses WW2 and the European war ends

- **Pass:** Germany is defeated and the European war terminates (white-peace chain or capitulation). Historical target ~1945.5; ending at all is the invariant, ending on time is the aspiration.
- **Probe:** global flags for the German white-peace chain; GER country state in late saves.
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — scripted German white-peace chain fired 1946.9. Late vs ~1945.5 target but the war ENDS; lateness traces to the 4.5-month-late war start (F1).

### F6. Pacific war terminates — KNOWN GAP

- **Pass:** the Pacific war reaches a termination path (Japanese surrender chain).
- **Status:** **KNOWN GAP — no termination path exists in the mod.** Japan sat frozen at its 1942 maximum through end-1946 in `9be92c89`: no nukes ever ready, no SOV–JAP war, no surrender chain. Expected FAILED until the Japanese surrender chain is built (Tier 3 in `campaign-audit-fix-plan`); do not re-diagnose, do not count toward pathology findings.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — Japan frozen at 1942 extent through 1946.12; no termination mechanism fired (by design gap).

### F7. Spanish Civil War: Nationalists win — DLC-gated

- **Pass:** Nationalist Spain wins the SCW, ideally by ~1939.
- **DLC-gated:** only scoreable on full-DLC campaigns. On the cloud box (no La Résistance) the game runs the non-LaR `spain.1` path where the SPA/SPB/SPC/SPD tag aliases resolve to nothing and every SPA-scoped buff/aid block is dead — mark `N/A (DLC)`. The non-LaR path itself is a **known gap** (fix the gating, not the balance — Tier 2 item 2.4).
- **Probe:** SPA/SPR country state and civil-war end flags; on full DLC check `SPR_nationalist_spain_flag` routing.
- **Streak:** 1
- **History:**
  - 2026-08-09 · `c9ab1062` · N/A (DLC) — cloud non-LaR path; Republican win #3 was a dead-code artefact, not balance evidence.
  - 2026-08-10 · `9be92c89` · N/A (DLC) — cloud, no LaR.
  - 2026-08-10 · `cbca536d` · PASSED — LaR path, Franco won 1939.3.30; both balance commits' mechanisms fired. Residual: volunteer-airforce decisions never fired on either side.

### F8. No major runs the old pathologies

- **Pass:** for every major: manpower not pinned at ceiling with falling division count; army-wide field fill ≥90%; no 100k+ equipment hoard sitting beside starving faction allies.
- **Probe:** per-major `units` fill sampling + stockpile vs allies' deficits; `var TAG "^wa_ai_"` deployment/lend-lease state. Cross-reads R5 (GER), R7 (relief legs), R10 (USA).
- **Note:** GER late-war 65% fill under the low supply-reach defines was ruled **by design** (Phase 1 rejection in `campaign-audit-fix-plan`) — do not count it here.
- **Streak:** 0
- **History:**
  - 2026-08-10 · `9be92c89` · FAILED — USA collapsed to 42 divisions with 249k idle infantry equipment and 0 deploy conveyors from 1943.6; hoards moved to SOV/USA and unreachable neutrals (POR 116k). Fixes shipped since (`3da0be383`, `2d48a1a17`) — see R10/R7b.

### F9. Game boots

- **Pass:** the build the campaign runs on launches without CTD. Scored per build, before the campaign: run the launch harness after any commit touching `force_concentration` blocks in country ai_strategy files — the deterministic-CTD lesson is that `GER_fall_gelb` + `war_with_soviets` fc entries are load-bearing (see comments in `common/ai_strategy/GER.txt` and the `d69eef2fa` incident).
- **Streak:** 0
- **History:**
  - 2026-08-10 · current HEAD (post-Tier-1 `a5ea1fb84`) · **NOT YET TESTED — boot test pending**; game was running locally all session. Run the launch harness before the next cloud campaign.

---

## RETIREABLE — fix verifications

Delete an item when its streak reaches its threshold (3 = narrow probe, 5 = behavioural).

### R1. AIFC sector_age cycles 1–5

- **Fix under test:** `4bfea363d` (1-based sector age) then `128cc7995` (validity scope leak) — **both failed to cure it**. Next step is live-log instrumentation on a running game, not another source patch.
- **Pass:** `wa_ai_aifc_sector_age` observed cycling through values 1–5 across a campaign's saves, not pinned at 1.
- **Probe:** `var <major TAG> "^wa_ai_aifc_sector_age" <saves...>` across the campaign.
- **Threshold:** 5 (behavioural — commitment-window dynamics over time).
- **Streak:** 0
- **History:**
  - 2026-08-09 · `0e7e7852` · FAILED — age pinned at 1 all campaign.
  - 2026-08-10 · `9be92c89` · FAILED — still pinned at 1 after the ROOT-hop fix; reproduced on `cbca536d` too.

### R2. PC factory allocation stays healthy

- **Fix under test:** `974bad6f7` (decay floor, affordability mirror, orphan cleanup).
- **Pass:** `wa_ai_pc_assigned_factories_total` on active builders stays in a sane band (observed 20–185), never decays to 1.
- **Probe:** `var <TAG> "^wa_ai_pc_assigned_factories" <saves...>` for 2–3 majors.
- **Threshold:** 3 (narrow variable probe).
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — totals in the 20–185 range, no decay.
  - 2026-08-10 · `cbca536d` · PASSED — healthy allocation confirmed on the control run.

### R3. Land majors queue type-13 railways

- **Fix under test:** `3c55b9d17` (Fix 29/29b — land-war railway queueing).
- **Pass:** land-war majors (SOV, GER at minimum) show type-13 projects in the PC queue during their land wars.
- **Probe:** `var <TAG> "^wa_ai_pc_building_type" <saves...>`.
- **Threshold:** 3 (narrow queue probe). Retire when both SOV and GER reach 3.
- **Streak:** SOV 2, GER 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — SOV and GER both queued type-13 railway projects.
  - 2026-08-10 · `cbca536d` · PASSED (SOV) — control run confirms SOV queueing; GER not re-checked.

### R4. Rubber shortage tracker exists and moves

- **Fix under test:** `974bad6f7` (rubber refinery wiring).
- **Pass:** `wa_ai_resource_rubber_shortage_months` exists on affected countries and changes value over the campaign.
- **Probe:** `var <TAG> "^wa_ai_resource_rubber_shortage_months" <saves...>`.
- **Threshold:** 3 (narrow variable probe).
- **Streak:** 2
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — variable present and moving.
  - 2026-08-10 · `cbca536d` · PASSED.

### R5. GER AI deploys

- **Fix under test:** supply/deployment stack through Phase 2–4 (post-`982ebfd12`).
- **Pass:** GER division count grows through the war, field fill >95% (early/mid war — late-war 65% under low supply reach is by design, see F8 note), no equipment hoard.
- **Probe:** GER `units` fill sampling + stockpile trend across saves.
- **Threshold:** 5 (behavioural).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER grows, fills, queues railways, fields no hoard.

### R6. Majors mechanize

- **Fix under test:** `5d2663848` + Tier 1 composition work.
- **Pass:** GER and SOV fielded armor+mech share >18% of the army.
- **Probe:** `units` composition sampling for GER and SOV in mid/late-war saves.
- **Threshold:** 5 (behavioural).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — GER fields 27% armor.

### R7a. Lend-lease relief — support-equipment leg

- **Fix under test:** `128cc7995` (per-archetype pull model).
- **Pass:** GER-creator support equipment appears in ROM/HUN/BUL/ITA stockpiles.
- **Probe:** minor-ally stockpile creator tags in `units`/equipment blocks; `WA_AI_logging` relief lines if a log is available.
- **Threshold:** 5 (behavioural flow over time).
- **Streak:** 1
- **History:**
  - 2026-08-10 · `9be92c89` · PASSED — support flow confirmed. Caveat from `cbca536d`: absolute thresholds converge too low for big armies (ENG stabilized ~1.7k support for 97 divisions) — candidate follow-up fix, tracked in `campaign-audit-fix-plan`.

### R7b. Lend-lease relief — infantry-equipment leg (recalibrated)

- **Fix under test:** `2d48a1a17` (35k/6k surplus, 4k support starving, common-enemy pairs).
- **Pass:** ROM/HUN rifle stockpiles off zero while GER holds surplus.
- **Probe:** ROM/HUN infantry-equipment stockpiles across war-time saves.
- **Threshold:** 5 (behavioural).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates campaign `9be92c89`.

### R8. UK air hosting works

- **Fix under test:** `24ffda1ac` (level-ladder rewrite) + instrumentation `57d6136dd`.
- **Pass:** `wa_ai_uk_air_dbg_started > 0` on ENG; type-2 (air base) projects queued; USAAF wings based in the UK pre-D-Day.
- **Probe:** `var ENG "^wa_ai_uk_air_dbg" <saves...>`; `var ENG "^wa_ai_pc_building_type"`; USA wing basing via `air_base` blocks (see R12 note on the save layout).
- **Threshold:** 5 (behavioural — the wing-basing outcome is the point; the dbg variable alone is not a pass).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates campaign `9be92c89`.

### R9. Supply-line construction targets the right corridors

- **Fix under test:** `24ffda1ac` (pathfinder param rename revived the strategy).
- **Pass:** type-1 projects appear targeting North Africa (ENG/ITA), GER→SOV, and JAP→RAJ routes.
- **Probe:** `var <TAG> "^wa_ai_pc_building_type"` plus target state/province vars on ENG, GER, JAP.
- **Threshold:** 3 (narrow queue/target probe).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates campaign `9be92c89`.

### R10. USA army composition recovers

- **Fix under test:** `3da0be383` (mech/exped exclusivity, infantry floor +15 double-gated).
- **Pass:** USA infantry role want POSITIVE (`ai` section, `ai_strategy` type=9 role ratios) and USA fields >100 divisions by 1943.
- **Probe:** `section <save> USA ai --grep "type=9"` for role wants; `units` division count in 1943+ saves.
- **Threshold:** 5 (behavioural).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates `9be92c89` (which FAILED at 42 divisions, infantry want −29, reproduced on `cbca536d`).

### R11. Factory floors hold

- **Fix under test:** `3da0be383` (tank/mech/amtrac production floors).
- **Pass:** USA tank factories ≥30 late-war; JAP tank factories ≥5; USA amtrac factories ≥8 with amtrac stockpile >0.
- **Probe:** `production` section factory counts per line for USA and JAP in 1943+ saves.
- **Threshold:** 3 (narrow factory-count probe).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates campaign `9be92c89`.

### R12. Carrier fighters get built and deck wings fill

- **Fix under test:** `a5ea1fb84` (cv-plane ratios 150/100, min 2 default / 6 carrier-major).
- **Pass:** USA cv_fighter factories ≥6; carrier wings filling toward 10/10 strength.
- **Probe:** USA `production` cv_fighter lines; wing fill via the carrier save layout — wings link to `air_base` blocks by numeric id from the per-country `strategic_air` pools, and **carrier bases are the `air_base` blocks WITHOUT a `state=` key**. Decks being "empty" without checking this layout is a parsing artefact (they were 75–97% manned in `9be92c89`).
- **Threshold:** 5 (behavioural — wing fill over time is the outcome).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates campaign `9be92c89`.

### R13. North Africa front moves

- **Fix under test:** `a5ea1fb84` (ENG `africa_war_2` X-AND-NOT-X restored from pre-split `a6fee253d`).
- **Pass:** ENG reaches the `africa_war_2` posture and the North Africa front actually moves. Pre-fix baseline: +2 provinces in 24 months.
- **Probe:** ENG ai_strategy state in the `ai` section; province control deltas in Libya/Egypt across war-time saves.
- **Threshold:** 5 (behavioural front outcome). Interacts with R9 (NA supply lines) — score independently.
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix postdates campaign `9be92c89`.

### R14. Scripted-invasion attack penalty does not stack

- **Fix under test:** `<PENDING — uncommitted on ai-rework, 2026-08-10>` (guard on `has_relation_modifier` in `WA_AI_DIVISION_spawn_invasion`; `WA_AI_invasions.1` re-scoped to fire ON the target with `FROM` = invader; removed the `is_ai` / historical gates and the `most_recent_invasion_target` scalar).
- **Bug being fixed:** `WA_AI_invasions_modifier` (`attack_bonus_against = -0.25`) was added once per `WA_AI_DIVISION_spawn_invasion` call, not once per invasion. Weserübung makes six calls → GER landed in Norway at **-150% attack**. The expiry event then read a single overwritten scalar and cleared it on its first fire, so five of the six stacks were never removed.
- **Pass:** on every major that runs scripted invasions (GER, JAP at minimum), `wa_ai_invasions_dbg_active` is **0 in every save**, and `wa_ai_invasions_dbg_adds` is **> 0** by mid-war with `adds == removes`. `adds == 0` means no invasion ever fired in that campaign → `NOT CHECKED`, not PASSED. A transient `_active = 1` or `2` in a save that happens to land inside a 14-day landing window is a PASSED with the caveat noted; `_active ≥ 3`, or any non-zero value that persists across consecutive monthly saves, is FAILED.
- **Probe:** `var GER "^wa_ai_invasions_dbg" <saves...>` and the same for JAP, across 1940–1945 saves. Cross-check a suspected failure against the live modifier: `section <save> GER diplomacy --grep "WA_AI_invasions_modifier" --max-lines 0` — under the bug the residue is permanent and shows up in any post-Weserübung save; under the fix it is absent outside the 14-day window.
- **Why instrumentation:** the penalty's natural fingerprint (the relation modifier itself) lives only 14 days and monthly saves almost never land inside that window — confirmed by scanning GER's `diplomacy` in `9be92c89` at 1940.7 / 1940.9 / 1941.1 / 1941.7, all zero hits. The `*_dbg_*` counters exist so the probe is reliable on monthly cadence.
- **Threshold:** 3 (narrow variable probe — `_active` returning to 0 is a direct state check, not a behavioural outcome).
- **Streak:** 0
- **History:**
  - NOT YET TESTED — fix and its instrumentation postdate every campaign in the registry.

---

## Recurring cosmetic anomalies — check here before reporting a "finding"

- **`ww2_*` theatre flags carry last-seen dates, not first-set dates.** They are re-stamped on every on_action fire, so their set-dates are useless as a war timeline — use the war/peace flags instead.
- **Double Trotsky flags** appear in SOV flag blocks; harmless duplication, not a political-path bug.
- **`atomic_research_completed` firing ~1940 is a research-tree marker, not a bomb.** It marks the research step, not weapon availability — do not report early nukes off this flag.
