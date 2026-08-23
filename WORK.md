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
  progress (2026-08-23).
- Closed when: a campaign shows the delegate missions armed and manned (R72's legs), the
  Indian army in East Africa/El Alamein, and no dominion dockyard nailed by an unbuildable
  design.
- Verification: campaign probes of R70/R72/R73/R84-R95 (archive); no console harness.

### lend-lease-relief — TESTED (2026-08-23)
- Scope: overland surplus relief per archetype (Fix 92) + USA native lend-lease offers.
  Absorbs R7b, R57.
- State: validated by the owner 2026-08-23; a **final audit remains**.
- Closed when: the final audit passes (leg 3 of R7b checked; USA sender restored or the
  R57 failure explained and accepted).
- Verification: console `WA_TEST_lend_lease_relief`; campaign probes of R7b/R57 (archive).

## PARKED

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
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
