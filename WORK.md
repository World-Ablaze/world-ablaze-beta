# WORK — subjects

One SUBJECT = one intended behaviour, named by a stable slug. Everything attaches to it:
commits, code comments (`# [slug] ...`), console harness, campaign probe. Rules:
`AGENTS.md § Subjects and sessions`. Enforced by `python tools/check_worklist.py`.

- **Admission**: a subject enters only if (a) the owner asked for it, or (b) it rests on a
  MEASURED symptom (save, playthrough report) about MOD behaviour. Meta-work (tooling, docs,
  checker, skills): never without an explicit owner request. Default = do not add; mention
  in one line at end of session.
- **One session = one subject.** At most **4** subjects in OPEN (WIP-LIMIT).
- **States**: `OPEN` → `SHIPPED-UNTESTED` → `TESTED` → `CAMPAIGN-OK` → `CLOSED`; or `PARKED`.
  A criterion met once = closed; a regression reopens from the symptom. F1–F9
  (`.claude/skills/wa-campaign-checklist/references/checklist.md`) remain the safety net.
- `SHIPPED-UNTESTED` means: code committed, the owner has NOT run the console harness.
  Older than 3 days = checker ERROR (`UNTESTED-STALE`). Paste the harness output here to
  move to `TESTED`.
- Heading format (parsed by the checker): `### <slug> — <STATE> (<YYYY-MM-DD>)`.
- Detailed probes of subsumed R-items: `documentation/archive/CHECKLIST_R_ARCHIVE.md`
  (frozen copy, not checked).

## OPEN

### scripted-invasion-reservation — OPEN (2026-08-23)
- Scope: owner request 2026-08-23 — while the scripted-invasion calendar is active, the invader's
  faction must not run engine-planned naval invasions against the calendar's target COUNTRIES until
  the date of the last scripted invasion against each (no corps parked for a Brittany landing while
  the calendar will open Normandy). Per country, per owner's explicit call over a state-level draft.
- State: written in the working tree, **uncommitted, untested**. Generator
  `tools/gen_ai_landing_reservations.py` (75/75 active calendar ops covered) → generated
  `WA_AI_LANDING_reservations_data.txt`; updater/stamp in `WA_AI_LANDING_effects.txt`; switch
  `WA_AI_LANDING_reservations_enabled`; consumer `WA_AI_MILITARY_INV_reserved_scripted_target`
  (`invasion_unit_request -200`, `country_trigger` flag `WA_AI_LANDING_reserved_for_@FROM`);
  spec `documentation/WA_AI_MILITARY_SYSTEM.md` §22; telemetry `WA_TLM_resv_*` (v30).
- Open engine questions (both stated in the consumer block): (a) `@FROM` dynamic-flag rendering
  inside an ai_strategy `country_trigger` has no other user in this repo — if inert, the block
  never matches, silently; (b) `-200` flooring the unit request is the same unmeasured assumption
  §10 carries. Fallback if (a) fails: scripted `add_ai_strategy type = invade` emission (AIFC
  armor-reconcile idiom), accepted-accumulation caveat and all.
- Closed when: a campaign shows (a) `wa_tlm_resv_stamp_n > 0` on the calendar invaders at war and
  the `WA_AI_LANDING_reserved_for_*` flags on their pending targets, (b) no engine-planned Allied
  invasion order against GER-held France before 1944.6 while dday_prep's own staging survives, and
  (c) reservations absent after each target's last scheduled op (+ one 50-day lease).
- Reviews 2026-08-23: wa-lessons CONCERNS + wa-architecture CONCERNS, both addressed in-session —
  the false "on_startup re-fires on save load" comment corrected (lessons-log MEASURED: it does
  not; pre-fix saves stay inert BY DESIGN, fingerprint = `wa_tlm_resv_*` absent), the rule-f
  t0/t1/t2 residual table added to §22 (late-firing op unprotected past schedule+45; early success
  lingers ≤ last-stamp+50), TLM §5 wording fixed (counter is per pending op, not per pair).
- Verification: owner boot start OK 2026-08-23 (game launches, files parse — proves syntax only,
  not behaviour). Console harness written 2026-08-23: `tag USA` → `event wa_resv.1` → read
  logs/game.log "RESV TEST" (legs: A loader/epoch, B forced stamp + literal read-back, C @FROM
  read in trigger context with scope=target/FROM=reserver; PASS = legC `1 1 0` with FROM=USA);
  `event wa_resv.9` cleans up. Owner ran it 2026-08-23: **legC PASSED** — MEASURED console output:
  FROM = United States of America, `literal 1 / @FROM 1 / @ROOT-control 0` → the @FROM dynamic-flag
  rendering works in trigger context with the consumer's exact shape, and the event-FROM
  assumption held. legB PASSED (pre 0 / post 1). legA: arrays CORRECT (`op_n = 30`, op0 634/2455 =
  Watchtower+45 — the harness's "expected 543/2361" note was wrong, that is ENG's row; fixed), but
  it caught a REAL bug: `today = num_days`, epoch never subtracted — `subtract_from_variable` on a
  temp operand silently no-ops (lessons-log entry added). Fixed to `subtract_from_temp_variable`
  in the shipped updater + harness; re-run 2026-08-23 confirmed **`today = 0`** and op0 634/2455.
  Caveat on that second run: its context header read `I-am-ROOT=0 / I-am-THIS=0` with
  ROOT-scope-usable=1 — the "Two call sites, one effect" syndrome — ASSUMED caused by hot-reloading
  scripts mid-session (the fix was live without a reboot); run 1's clean-header PASS of legs B/C
  stands, legA's arithmetic is variable-only and accepted. Fresh-boot run 2026-08-23: header clean
  (`1 1 1 1 0` / `1 1 0`), legA `today = 0` + op0 634/2455, legB 0->1, legC `1 1 0` with FROM=USA —
  **console harness fully PASSED on the shipped code; chapter closed** (and the clean fresh boot
  supports the hot-reload reading of the poisoned run). legC's
  residual (does the ai_strategy evaluator itself render @FROM) is engine-only → campaign probe:
  the -200 entry in the save's `ai=` block + no engine invasion orders against reserved targets.

### minor-expeditionary-fitness — OPEN (2026-08-23)
- Scope: a country that cannot equip a real infantry division does not hold a front outside its
  own neighbourhood. Owner rule (2026-08-23): Nepal/Bhutan defend near home, never beyond India;
  no militia expeditionary corps on a faction's overseas front.
- State: `WA_AI_MILITARY_is_fit_for_expeditionary_front` + `WA_AI_MILITARY_state_is_beyond_home_reach`
  (`WA_AI_MILITARY_triggers.txt`) and `WA_AI_MILITARY_CAPS_unfit_army_stays_home`
  (`WA_AI_MILITARY_DEFAULT_FRONT_caps.txt`) written in the working tree, **uncommitted, untested**.
  Owner rule 2026-08-23: five military factories for everybody, no exemptions. MEASURED the same
  day: NZL starts at 2 arms factories and SAF at 4, both under the floor, so both are home-bound
  until they build past it — an accepted, intended interaction with `commonwealth-handoff`, not an
  oversight. An `is_subject` escape hatch was written, then removed on the owner's instruction.
- Open engine question: `FROM.FROM` inside a `front_unit_request` state_trigger is documented
  (`common/ai_strategy/documentation.info`) but has no other user in this repo. PDXScript fails
  silently, so the predicate could be inert and look identical to working.
- Closed when: a campaign shows (a) NEP/BHU divisions never outside their own and neighbouring
  states, (b) no country under 5 military factories holding a front beyond its own neighbourhood,
  and (c) the Commonwealth theatres still manned by the members that ARE above the floor (RAJ 12,
  AST 10, CAN 9) once NZL and SAF are held back.
- Verification: console harness owed for the country-scope trigger (the state_trigger's FROM.FROM
  scope exists only inside the engine's front call and cannot be reproduced from the console);
  campaign probe as above.

### commonwealth-handoff — OPEN (2026-08-23)
- Scope: Commonwealth defensive missions, East Africa as the Indian army's campaign, Kuwait
  guard, El Alamein reinforcement, Pacific home-garrison release, dominion ship designs.
  Absorbs R70, R72, R73, R84–R86, R88–R90, R93, R95 and QUEUE 0l / 14.
- State: fixes 123–129 / 132 / 134 shipped (`bc90346af`); owner campaign verification in
  progress (2026-08-23). 2026-08-24 (campaign `eefaa9fc`, save 1940.10, owner report "Egypt
  defence ridiculous"): MEASURED ENG 40/62 divisions in East Africa + Sudan vs 9 ITA, 3 in
  Egypt vs 39 ITA (Marsa Matruh lost). East-Africa delegation deepened −75 → −130
  (`WA_AI_MILITARY_ENG_east_africa_delegated_FRONT`), netting ENG +20 vs Egypt's +25 so
  Egypt outbids while the delegate lives; reviews: architecture OK, lessons CONCERNS all
  three addressed (full bid table MEASURED vs the save; RAJ delivers 16 div in-theatre;
  "never negative" comment corrected). **Open defect found doing it: every Commonwealth
  readiness verdict embeds `WA_AI_MILITARY_army_still_operational` (bars 41 div / eq 0.9,
  calibrated on major-power collapse) — RAJ at 36 div / 0.60 fails ALL verdicts, so the
  deepened stand-down AND RAJ's +50 El-Alamein reinforcement were both OFF in `eefaa9fc`
  while the unconditional Faction +150 sent 16 unready RAJ divisions to East Africa anyway.
  Owner decision 2026-08-24 ("plancher léger"): the two ADD-force verdicts (east_africa,
  egypt_reinforcement) now read `WA_AI_MILITARY_delegate_force_floor` (states + manpower +
  eq > 0.45 delegate-calibrated, own num_divisions bar kept); the three STAND-DOWN verdicts
  keep the full brake (Fix 128); the eq term covers the East-Africa verdict's dual role
  (ADD for RAJ, stand-down for ENG) against a hollow delegate. With RAJ 36 div / eq 0.60
  both ADD verdicts arm: RAJ +50 on north_africa, ENG −130 live.**
- Closed when: a campaign shows the delegate missions armed and manned (R72's legs), the
  Indian army in East Africa/El Alamein, and no dominion dockyard nailed by an unbuildable
  design.
- **Campaign `db5029c2` 1940.9–1940.12 scored 2026-08-24 (build `d7e9b91ee`, all fixes live) —
  probe (a) FAILS all four months, probe (b) passes on its letter while Egypt falls.** MEASURED:
  state 452 Marsa Matruh (the El-Alamein / Sallum / Sidi-Barrani VP state) falls to Italy in
  November and holds ZERO Allied divisions in December; Egypt+Libya December = Axis 56 (ITA 38,
  GER 10, ITL 8) vs Allies 16, with 21 Axis divisions already inside Egyptian states and Cairo
  contested 13/5. ENG East Africa + Sudan vs Egypt: 24/7, 24/11, 20/12, 21/12. RAJ Egypt 8→8→8→3
  while RAJ East Africa 5→9→14→14. **Probe (b) is badly written** — it counts divisions without
  looking at the front held or the force ratio, so it reads PASS (12 ≥ 8) on a collapsing theatre;
  rewrite it before the next scoring.
- **The "block never fired" hypothesis is REFUTED.** Owner-run `imgui show ai-strategy` (ENG @
  1940.11.1, same campaign) lists `WA_AI_MILITARY_ENG_east_africa_delegated_FRONT` under Active
  strategies, and 28/28 `front_unit_request` rows reconcile to file:line. The `-130` is armed and
  doing what it says. What survives is the cross-AREA ordering assumption — and a NEW doubt under
  it: four entries on `area = north_africa` occupy four DIFFERENT `Target` ids in that window, so
  whether the engine SUMS entries sharing an area is now itself ASSUMED
  (`.claude/skills/wa-diagnosis/SKILL.md` technique 5 rule 3, commit `e68387f2e`).
- **Second lever shipped 2026-08-24, uncommitted at time of writing — the ENG `north_africa`
  throttles stand down while Egypt is invaded.** New control-panel trigger
  `WA_AI_MILITARY_egypt_is_invaded` (ROOT-relative, tag-free, 11 Egyptian states — deliberately
  wider than the {446,447,453} East-Egypt anchor, because 452 falls first). The two
  `area = north_africa` entries are split out of `africa_war_1` (`-40`) and `africa_war_3_FRONT`
  (`-20`) into `WA_AI_MILITARY_COUNTRY_ENG_FRONT_north_africa_brake_egypt_held` / `_border_held`,
  each keeping its original gate plus `NOT egypt_is_invaded`; the parents keep `central_africa -50`
  and their two `front_control` entries. ENG's `north_africa` net becomes conditional: `+25` clear,
  `+85` invaded (`WA_AI_MILITARY_SYSTEM.md` §16 restated). The `-130` is NOT re-sized — its intent
  holds at both nets, and the margin over East Africa widens from 5 points to 65 exactly when Egypt
  is attacked. Removal rather than a `+60` counter-entry is deliberate: a counter only works if the
  engine sums per area, a removal works under either reading.
- **Known limit of that lever, recorded before shipping (MEASURED, `plans.py ENG`):** ENG's December
  order-class census is front 26 / buffer 25 / areadef 6 / invasion 6 of 63 — **40 % of the army sits
  in buffer orders across 9 armies**, only ~4 of them in Egypt. A `front_unit_request` does not by
  itself move a division held in a buffer pool, so this fix removes a real suppression on the
  Egyptian front request but is NOT established to reach the ~20 buffer-held divisions outside the
  theatre. The buffer layer is untouched and is the next lever, not this one.
- Reviews 2026-08-24 on that lever: architecture CONCERNS (5 required items, all applied — canonical
  block naming per §5 rule 4, §16 arithmetic restated, `military_economy_audit.py` run clean of the
  new blocks, `range:` wording corrected, `front_control` entries left in the parent) and lessons
  CONCERNS (6 items — the false "africa_war_3 arms on hostile presence" premise CORRECTED in its
  header, that gate has no hostile-presence term and its `-20` is a peacetime-onward throttle; the
  oscillation bound written as a t0/t1/t2 line, flap worst case = the pre-change net `+25`, never
  worse; the order-class census run and its adverse result recorded above; the 2026-08-17
  `[med-axis-posture]` decision re-priced `central_africa` only and records no rationale for the
  `north_africa` negatives, so it is not contradicted).
- Verification: campaign probes of R70/R72/R73/R84-R95 (archive); no console harness.
  Added 2026-08-24: (a) with the delegation live, ENG divisions in East Africa + Sudan drop
  below its Egypt/north-africa contingent (cross-area ordering +20 < +25 is ASSUMED engine
  behaviour — this probe is its only proof) — **FAILED on `db5029c2`, see above**; (b) Egypt holds
  ≥ 8 Allied divisions with front/buffer orders while Italy holds the Libyan border states —
  **passes on its letter, rewrite it**. Added for the throttle lever: **F9 boot test owed** (the
  strategy-DB CTD precedent of 2026-08-09 makes any block add/remove in a country `ai_strategy`
  file launch-test territory, not parse-check territory); console harness owed for
  `WA_AI_MILITARY_egypt_is_invaded` (plain country-scope trigger, so unlike
  `minor-expeditionary-fitness` it CAN be read from the console); and the cheapest confirmation is
  the owner's `imgui show ai-strategy` window showing both brake blocks LEAVE Active strategies
  once an enemy is on Egyptian soil.

### silo-breadth — TESTED (2026-08-24)
- Scope: owner request 2026-08-24 (Discord) — "make other buildings use the build-wide system
  implemented for mils, specifically fuel silos: I queue 20 fuel silos and it queues up 6 in one
  state and then stops (first state's cap of 6)."
- Diagnosis (MEASURED): fuel_silo is a shared-slot building with `state_max = 6`
  (`00_buildings.txt`), but `WA_AI_available_SILO` never got the [refineries]/Fix 81 committed
  standard — no state-cap test at all — and `WA_AI_queue_SILO` still uses the pre-Fix-88
  first-fit walk. Exactly the stall the triggers-file header documents: past the cap the top
  state stays "available" (free_building_slots reports only the shared pool), the engine no-ops
  every add, the state stays #1 in `WA_AI_shared_slot_scores`, silos stall country-wide.
- Fix: replicate the CIC/MIC/NIC/REF standard for SILO — `@WA_AI_SILO_STATE_MAX = 6` +
  committed-sum availability, `WA_AI_queue_depth_ok_SILO`, committed-maintaining
  `WA_AI_add_SILO` (TLM `sq_adds_by_type^8`, v31), Fix 88 breadth-first walk in
  `WA_AI_queue_SILO`, `on_state_control_changed` TTL reset extended to SILO, registry mirror
  for the state cap, console harness `WA_TEST_silo_breadth` (`event wa_silo.1` read-only /
  `.2` burst).
- State: shipped + console harness PASSED by the owner 2026-08-24. Reviews: lessons
  CONCERNS + architecture CONCERNS, all required items applied in-session (TTL reset on
  control change, closing criterion on built levels, TLM v31 bump + §5 row, caller-gate
  meta_trigger render measured by harness leg C, header sync in queue_functions). Also
  removed in passing, on the owner's explicit ask: the born-dead FRA∧ENG exclusion branch
  in the caller's silo gate (`events/WA_AI_construction.txt`, vacuously false since
  `bd11fde6b` — removal preserves behaviour).
- Harness run (owner, 2026-08-24, GER 1936 fresh boot, MEASURED from game.log): header
  `1 1 1 1 0`, tech 1; legA 30 scored states, top 8 all `avail = 1` (no FAIL line); legC
  `need 15 / gate 1 / known-true 1 / known-false 0` — the caller's meta_trigger render
  works; legB 8 picks on 8 DISTINCT states (W. Berlin, E. Berlin, W. Rhineland,
  E. Rhineland, Hamburg, Moselland, Saarland, N. Brandenburg), all tier 1, k = 10 — the
  pre-fix behaviour was 8× the top state. RESIDUAL, stated honestly: the save had no state
  at the silo cap, so "built = 6 reads avail = 0" was not exercised (vacuous on this run);
  the campaign probe owns it, same committed mechanism as the refineries' campaign-proven
  cap test.
- Closed when: the owner's console harness run shows the walk skipping a state at its silo cap
  and spreading a burst across ≥ 2 states; and a campaign save shows a country with silo need
  > 6 holding BUILT `fuel_silo` levels in ≥ 2 states (state building levels, not the adds
  counter — a queued add on a saturated queue is not a build; `wa_tlm_sq_adds_by_type^8` is
  supporting evidence only).
- Verification: console harness (owner-run, output pasted here); campaign probe as above.

## PARKED

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
| `lend-lease-relief` | TESTED (owner-validated 2026-08-23) | Overland surplus relief (Fix 92) + USA native offers work; final audit remains | Final audit passes: leg 3 of R7b checked; USA sender restored or the R57 failure explained and accepted |
| `trade-law` | SHIPPED-UNTESTED (`32c03c550` + revert, 2026-08-19) | Ladder has two reachable rungs (R28); dead flag `WA_AI_trade_law_recently_changed`; recovery path only covers export_focus/free_trade | In-game test of the shipped fix passes; ladder rungs reachable in a campaign |
| `majors-mechanize` | FAILED (2026-08-17, `9d83084c`) | Majors do not mechanize (R6) | A campaign shows majors' mobile divisions motorized/mechanized on schedule (R6 probe, archive) |
| `uk-air-basing` | FAILED (2026-08-16) | UK air hosting + throughput failing (R8, R54) | R54's ledger legs pass in a campaign |
| `air-deployment` | FAILED (2026-08-16) | Air forces not deployed to contested theatres (R15) | R15 probe passes (archive) |
| `overextension-brake` | FAILED (2026-08-15) | Industrial overextension brake does not fire/substitute (R24, Fix 39) | R24 probe passes (archive) |
| `refineries` | DIAGNOSED (2026-08-11) | Self-concealing shutdown, deadlocked setpoints (R29); admission behind default-band radars (R55, Fix 90) | R29+R55 probes pass (archive) |
| `equipment-selection` | SUSPENDED (first campaign failed all 5 probes) | Evaluator project generalisation suspended; R32/R35/R41/R43 FAILED | Owner decision to resume, then the 4 probes pass |
| `convoys` | FAILED / NOT TESTED | Escorts parked (R36); land-coalition convoy arsenal (R79, Fix 115); surplus dockyards (R87, Fix 126); JAP opens no convoy line and GER 2700-hull pile unexplained (QUEUE 15/20) | R36 passes; R79/R87 probes pass; GER pile explained |
| `pc-queue` | FAILED (R47) | Capitulated country runs no PC (R47, Fix 75); FRA queue deadlocked on pre-armistice projects (QUEUE 17) | R47 probe passes; FRA queue drains in a campaign |
| `landing-freeze` | FAILED outcome leg (R51) | Landing hysteresis: mechanism passes, outcome fails | R51 outcome leg passes (archive) |
| `prospecting-coop` | MIXED (R65 FAILED, R66 PASSED once) | Coal coop leg reads wrong side (R65); `coop_can_supply` is 1 for everyone (QUEUE 0b) | R65 passes; sold-out test exercised |
| `templates-coverage` | MEASURED (2026-08-18, `2f8cbd51`) | 320 of 334 countries never get a WA infantry template | Criterion to be written at reopen (which tags SHOULD get one) |
| `front-control` | AUDITED, no fix | 3 real `front_control` collisions; per-field vs whole-block resolution unknown; 4 CHI blocks tie at prio 0 | Engine question answered (test or install doc), collisions resolved or accepted in writing |
| `resource-needs` | MEASURED (`3d68a183` 1944.4) | `WA_AI_calculate_resource_need` blind to shortage of a barely-produced resource (ENG, 6 of 8) | Need computed from consumption, not production share; probe passes |

## CLOSED (last 10, then pruned — git is the archive)

| Date | Subject | Note |
| --- | --- | --- |
| 2026-08-23 | `na-corridor` | NA corridor logistics (rail/depots/ports/theatre air bases, Fix 95–135). Human validation: tested and functional. Absorbed R9, R13, R52, R60, R68, R69, R71, R77, R78, R81, R91, R96, QUEUE 0q/0r/0m/0i. |
| 2026-08-23 | `med-axis-posture` | Axis Mediterranean posture (Afrika Korps, Tunis, Italy, Ethiopia, Med fleet, convoy interdiction; Fix 96–137). Human validation: tested and functional. Absorbed R17, R61, R63, R64, R74–R76, R80, R82, R83, R92, R94, R97, QUEUE 0t/0h/0f/0g/0. |
| 2026-08-23 | 14 R-items retired on PASS | R10, R19, R31, R38, R39, R40, R42, R44, R45, R49, R50, R56, R66 (folded), + R53 dropped (probe tool never existed). Details: archive. |
