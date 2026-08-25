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

> **Campaign `8f9b5653` scored 2026-08-25** (cloud, `dlcs=257535`, BHU observer, 117 monthly saves
> 1936.2-1945.10, unbranched, build = HEAD `ed109de9d` by a 4-minute commit->run gap,
> `wa_tlm_version = 31` first and last save). It is the first campaign carrying **all four** OPEN
> subjects' code. Per-subject verdicts are in each body below; F1-F5/F7/F8 are in
> `.claude/skills/wa-campaign-checklist/references/checklist.md`. **The campaign's headline is not
> any of the four subjects**: every upstream fundamental passed (war 1939.9.1 exact, France 1940.6.30,
> Barbarossa on the hard date, Pearl Harbor exact, `d_day_happened` 1944.6.9) and Germany still
> finishes **53/53 states, 436/436 provinces, 321 divisions and growing**, with Paris German at the
> last save. The three OPEN subjects that touch the western/Mediterranean arc are all downstream of
> that.


### scripted-invasion-reservation — OPEN (2026-08-23)
- **Campaign `8f9b5653` scored 2026-08-25 — legs (a) and (c) PASSED, leg (b) is NOT CHECKED, not a
  pass, and the subject does NOT close on this evidence.** Leg (a) MEASURED: `wa_tlm_resv_stamp_n`
  USA 135 (1942.6) -> 461 -> **724** (1944.6), ENG 80 -> 129 -> **159**, both families fresh
  (`_last_t` = the save's own month) with `resv_first_t` USA 1942.1 / ENG 1940.7; 31
  `WA_AI_LANDING_reserved_for_*` flags live on GER at 1942.6 / 1943.6 / 1944.1 / 1944.6 and on ITA
  through 1944.1. The 31 tags are the Allied faction roster, which is what
  `WA_AI_LANDING_stamp_reservation` is written to do (ROOT plus every AI faction peer) — checked at
  the write site before being called an anomaly. Leg (c) MEASURED: flags absent on GER from 1944.12,
  on ITA from 1944.6, on JAP from 1945.10, each inside one 50-day lease of its own last scheduled op;
  no leak on any target. The late `FROZEN` annotation on both invaders (USA last sample 1945.4, ENG
  1945.6) is calendar exhaustion — `Victor V` expiry day 3434 and `Dracula` 3452 — not a dead path.
- **Leg (b) passes on its letter and proves nothing.** MEASURED: zero type-3 (naval invasion) orders
  against any metropolitan French state across nine saves 1942.6-1944.6; every ENG/USA type-3 order in
  that window targets Gabon, Kuwait, Dhi Qar or Halab. Invasion-class staging never collapsed (ENG 1-5,
  USA 4-9). But the Allied AI never wanted a French landing in the first place, so **the mechanism
  under test did not run** — by the `wa-campaign-checklist` rule that is NOT CHECKED. No engine type-3
  order ever targeted states 15 or 1016 either, so the "dday_prep's own staging survives" clause is
  vacuously satisfied: there was never a competing order for the +1000 to outrank.
- **The one discriminating datum reads AGAINST the mechanism, inconclusively.** MEASURED: at 1944.6
  `control 677` gives GER 11 of 11 provinces in Halab, GER carries `WA_AI_LANDING_reserved_for_USA`
  (`set=1944.6.1.1`), and USA order instance **252 holds 9 divisions aimed at Halab** — still 9 at
  1944.7, 1944.8 and 1944.9 while GER holds the ground and stays flagged. That is verbatim the
  falsification signature the consumer block's own header names. DERIVED, and deliberately not
  upgraded: it is equally consistent with (i) `@FROM` failing to render in an `ai_strategy`
  `country_trigger`, and (ii) `invasion_unit_request -200` having no lever over an order created 16
  months earlier and already staffed (`creation_date` never refreshes; order 252 predates GER's
  control of its target by a year). **This campaign cannot separate them.** Both switches were live —
  `WA_AI_LANDING_reservations_enabled` = `always yes`, `WA_AI_LANDING_freeze_is_faction_wide` =
  `always no` — so the pass is not an artifact of a disabled block.
- **What would settle it**, and what this subject now waits on: a console harness leg exercising the
  predicate in `ai_strategy` context rather than trigger context (the 2026-08-23 harness proved
  trigger context only), or a campaign in which the Allied AI actually wants a reserved beach.
- Probe defect found while scoring, fix before reusing: **`plans.py --fronts` filters on
  `FRONT_TYPES = ("1","2")` and cannot emit a type-3 naval-invasion row at all.** The obvious command
  returns zero type-3 orders on every save, which reads exactly like "no invasion orders anywhere" and
  would have passed leg (b) for the wrong reason. Type-3 rows were obtained by importing `plans.py` and
  patching `FRONT_TYPES` before calling `main()`. Second defect: the reservation flag is re-issued by
  the monthly pulse (`clr` + `set … days = 50`), so its set-date is **always the save's own month, day
  1, hour 1** — a last-refresh stamp, never a first-reservation date.- Scope: owner request 2026-08-23 — while the scripted-invasion calendar is active, the invader's
  faction must not run engine-planned naval invasions against the calendar's target COUNTRIES until
  the date of the last scripted invasion against each (no corps parked for a Brittany landing while
  the calendar will open Normandy). Per country, per owner's explicit call over a state-level draft.
- State: written in the working tree, **committed and live in campaign `8f9b5653`** (see the scoring block below). Generator
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

### minor-expeditionary-fitness — SHIPPED-UNTESTED (2026-08-25)
- **FIX SHIPPED 2026-08-25, and it is NOT the one that was asked for — the value stays at -100.**
  Owner asked to deepen the brake. **That change cannot work and would have been reverted by a
  linter.** `documentation/WA_AI_MILITARY_ECONOMY.md` rule **E2** is normative: `front_unit_request`
  is a **percent factor** bounded to **[-100, +200]**, where -100 is already the full veto and
  anything lower is saturation — mechanically enforced at `tools/military_economy_audit.py:233`.
  **The block's own header had already predicted this exact residual and named the remedy**: *"the
  Faction layer pulls up to +150 on some areas (ALLIES on east_africa). An unfit member … nets +50
  there rather than 0. E2 caps this type at -100, so closing that gap means lowering the pull, not
  deepening this brake."* That objection cannot be refuted, so per AGENTS.md principle 3(g) it was
  kept and the pull was lowered instead.
- **What shipped:** `WA_AI_MILITARY_is_fit_for_expeditionary_front = yes` added to the `enable` of the
  two Faction pulls the imgui reconcile MEASURED reaching NEP —
  `WA_AI_MILITARY_ALLIES_europe_first` (+150 `tag = GER`, +75 `area = north_africa`) and
  `WA_AI_MILITARY_ALLIES_east_africa_contested_FRONT` (+150 `area = east_africa_regions`). The CAPS
  `-100` then stands alone and IS the full veto. The `residual:` line in
  `WA_AI_MILITARY_DEFAULT_FRONT_caps.txt` is rewritten to record the closure and to say that a NEW
  pull on a reachable area is fixed in that block's `enable`, never in this value.
- **Why gating those two blocks is safe** (impact analysis, AGENTS.md principle 3): both already carry
  `NOT = { WA_AI_MILITARY_home_threatened = yes }`, so **they only ever arm while nothing menaces the
  member's own ground — they are pure expeditionary pulls and gating them removes no home defence.**
  Audience check, MEASURED on `8f9b5653`: the theatre's intended manpower is RAJ 59-138, AST 47-94,
  CAN 35-111, SAF 21-49, NZL 17-34 arms factories, all far above the floor, so the intended audience
  is untouched; only NEP/BHU/LUX/HOL/COS-class members lose the pull. Ahistorical check: a normally
  large Ally crippled below 6 factories is also held home, which is the rule's stated intent.
  **Regression risk, stated:** the gate is dynamic, so a member that drops below 6 factories
  mid-campaign stops being pulled abroad — intended, but it means a bombed-out ally silently leaves
  the theatre. Audit: `military_economy_audit.py` E2 count unchanged at 1 (pre-existing, see the
  `commonwealth-handoff` note), brace-balanced, BOM-free.
- **Ceiling this fix does NOT raise (H3, unchanged):** only 5 of 12 (1943.6) and 7 of 16 (1944.6) NEP
  divisions are under a front order at all. The `buffer` / no-order remainder is out of reach of any
  `front_unit_request`, so a re-scored campaign should show the front-ordered half come home and the
  garrison half stay put. **If it does, the buffer layer is the next lever and a separate subject.**
- **Scope extended by owner request 2026-08-25: an unfit country is not a lend-lease recipient
  either** (*"équipement gâché dans des divisions inutiles"*). Shipped in the same session:
  new `WA_AI_LEND_LEASE_recipient_can_field_equipment` (`WA_AI_LEND_LEASE_triggers.txt`) delegates to
  the same military predicate so the threshold keeps ONE definition, and is applied at **both**
  recipient paths — `WA_AI_LEND_LEASE_relief_pair_is_valid` (the WA weekly relief pull; placed on the
  pair rather than on `is_starving_any` so `WA_TLM_llr_starving_n` still counts the country and only
  the pairing is refused) and the `TARGET` block of `WA_AI_lend_lease` (vanilla-style targeting), so
  the two cannot disagree.
  **Homeland escape hatch added the same day, on owner reversal** ("un pays inapte qui se fait
  envahir a quand meme besoin de fusils => c est vrai, il faut prendre en compte ce cas"). The
  trigger is renamed `WA_AI_LEND_LEASE_recipient_is_worth_equipping` and reads
  `WA_AI_MILITARY_is_fit_for_expeditionary_front` **OR** `WA_AI_MILITARY_home_threatened`.
  **The hatch reuses the SAME two predicates the Faction pulls are gated on, and that is the point:**
  while home is safe the pulls are fitness-gated and so is the aid; the moment home is threatened the
  pulls switch OFF (the country is kept home) and the aid switches ON. One event governs both, so the
  front brake and the lend-lease gate can never disagree about where an unfit army should be.
  Two things recorded rather than hidden. (i) `home_threatened` carries six tag branches
  (EGY/MAL/UKE in ENG faction, ROM/HUN/FIN vs SOV); **all six sit above the factory floor**, so that
  branch can never be the deciding term here - checked before reusing the trigger rather than after.
  (ii) **Residual, unbounded and stated:** `home_threatened` needs `surrender_progress > 0.05`, so aid
  resumes only once the invader has actually taken ground - there is a lag between the first enemy
  division on home soil and the hatch opening, and this session does NOT bound it. Narrowing it needs
  a new "an enemy holds one of my states" predicate, which cannot be written with ROOT/PREV at these
  call sites: **ROOT is the DONOR on the vanilla TARGET path and the RECIPIENT on the relief path**,
  so a scope-relative predicate would silently read the wrong country on one of the two.
- **State moves to `SHIPPED-UNTESTED`: the lend-lease half touches a system that HAS a harness**
  (`common/scripted_effects/WA_TEST_lend_lease_relief.txt`), so per AGENTS.md the owner must run it
  and paste the output before this returns to a tested state. **Also owed: an F9 boot test** — this
  session edited `enable` blocks in two `common/ai_strategy/` files, which the 2026-08-09
  strategy-DB CTD precedent makes launch-test territory, not parse-check territory.
- **Process note, stated plainly:** this session covered two subjects' worth of work (the front brake
  and the lend-lease recipient gate) against the AGENTS.md "one session = one subject" rule. Both
  were direct owner requests sharing one predicate, and both are recorded here rather than split, but
  the lend-lease half has had **no** campaign evidence and no harness run behind it.- **Campaign `8f9b5653` scored 2026-08-25 — legs (a) and (b) FAILED with the code confirmed live;
  leg (c) SPLIT.** The cap is not absent from the build: `WA_AI_MILITARY_CAPS_unfit_army_stays_home`
  and both its triggers entered at `e958ef934`, well before the run, so this is a behaviour failure,
  not a missing commit.
- **Leg (a) FAILED.** MEASURED (`plans.py NEP,BHU --where`, closure test passed on every tag×save):
  NEP holds **zero divisions in Nepal** at 1943.6 and 1944.6 — the entire army is in Africa. 1943.6:
  Sokoto 3, Chad 2, Socotra 1, Eritrea 1, Niger 1, Timbuktu 1 (9 of 12 located out of region).
  1944.6: Senegal 3, Gambia 2, Eritrea 1, South Darfur 1, Socotra 1, Chad 1, Niger 1, Bamako 1,
  Batna 1, Cameroon 1 (**13 of 16**, ten African states). 1941.6: Somaliland 3, Amhara 1, Eritrea 1.
  Several carry front-class orders, not transit. NEP is a full faction member (Allies, then United
  Nations) at war with 29 countries, no overlord.
- **Leg (b) FAILED — and the violator is NEP, not NZL/SAF.** MEASURED `arms_factory` owned: NEP **1**
  in all five saves, holding front-class orders in Somaliland/Amhara (1941.6), Chad/Eritrea/Niger/
  Timbuktu (1943.6), Senegal/Gambia/South Darfur/Chad (1944.6), Eritrea (1945.10). A country at 20 %
  of the floor holding fronts on a continent it does not border, sustained 4½ years.
- **The NZL/SAF interaction recorded above does NOT occur, and the WORK.md figures behind it were
  1936 readings.** MEASURED: NZL 17/22/30/32/34 and SAF 21/29/36/42/49 arms factories at
  1941.6/1942.6/1943.6/1944.6/1945.10 — **both are above the 5-factory floor in every scored save**.
  Their expeditions (SAF to Sudan 1943, Katanga 1944, Algeria 1945; NZL to the Horn, Sahel and
  Maghreb) are therefore permitted, not violations; SAF is in fact *more* home-bound than the rule
  requires in 1941-42. The accepted interaction with `commonwealth-handoff` never materialised.
- **Leg (c) SPLIT: RAJ and AST PASS, CAN FAILS.** MEASURED: RAJ 30->110 divisions, front-class 12->41,
  holding Burma/Assam, Bengal and a 4-17 division Africa/Middle East expedition simultaneously; AST
  7->21 divisions with African-front divisions in every save (10 of 16 abroad at 1943.6). **CAN fields
  4-9 divisions across the decade on 35->111 arms factories, and its order class is `areadef` ONLY in
  4 of 5 saves** — 100 % home garrison at 1941.6, 1942.6, 1944.6 and 1945.10, its single expedition
  being 3 front divisions in Batna at 1943.6, gone by 1944.6. Canada is over the floor by 22× and
  contributes nothing to any front. DERIVED: that is a separate defect from this subject's rule, and
  a candidate subject in its own right rather than something to fix on the way past.
- **Diagnosis run 2026-08-25 on the FAILED result (six boxes, `wa-diagnosis`). Verdict: the rule as
  written cannot produce the owner's outcome even if every line of it works, and a second, sharper
  reading says it is not working either.**
  1. *Symptom* — a 1-factory country holds front orders across the Sahel and the Horn.
  2. *Measurement* — MEASURED at 1943.6: NEP 12 divisions, all 12 outside its own and neighbouring
     states, 5 of them under a front order; at 1944.6, 16 divisions, 7 under a front order, mean org
     **6.0**. Closure test passed both saves (`--where` totals = `army` deployed, 12 = 12, 16 = 16).
  3. *Mod state* — NEP `num_of_military_factories` = 1 in every save and `has_war = yes`, so
     `WA_AI_MILITARY_CAPS_unfit_army_stays_home` **should** be armed. NEP's serialised `ai` section
     holds **70/71 entries and ZERO negatives** at both dates, while 12 other countries in the same
     save do carry negatives (SWE to −1000, DEN to −2000) — so the zero is a live reading, not a
     serialisation gap. The literal `−100` occurs **nowhere in the save, for any country**.
  4. *Mod decision* — **the discriminating comparison is ETH.** MEASURED: ETH has **8** arms
     factories, so `num_of_military_factories > 5` is TRUE and the block is **DISARMED** for it — and
     ETH puts **12 of its 13 divisions on a front in the same Sahel**, behaving identically to NEP.
     **Same outcome with the block on and off.** Every other ≤5-factory belligerent that "stayed
     home" (BHU, ICE, HON, ELS, COS, LUX, MON, TAN, BRA, CHL, COL) has 0–4 divisions or no distant
     front order, i.e. was never asked — so the campaign contains **no positive control**: the
     mechanism is never observed producing a non-zero effect anywhere.
  5. *Script line* — two, and the first is the one that makes the rule unachievable as written:
     - `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_caps.txt:162-166` — the payload is a single
       `front_unit_request`. MEASURED: only **5 of 12 (1943.6)** and **7 of 16 (1944.6)** NEP
       divisions sit under a front order at all; the rest are under a scripted `buffer`
       (`put_unit_buffers`) garrison order or under **no order**, where a `front_unit_request` has no
       lever by construction. **Even a perfectly working block could not have emptied Africa** — the
       buffer/garrison layer is untouched and is a second lever this subject does not have.
     - `common/scripted_triggers/WA_AI_MILITARY_triggers.txt:3319` —
       `num_of_military_factories > 5` does not select the population the owner's rule describes.
       ETH at 8 factories, 13 divisions, mean org 6.0 on a distant front is the same pathology and
       sits outside the gate. The rule says "cannot equip a real infantry division"; the gate asks a
       factory count, and the two disagree on the clearest case in the campaign.
  6. *Engine boundary* — **H1 (`FROM.FROM` inert, predicate matches nothing) and H2 (`-100` armed but
     outbid) survive and this campaign CANNOT separate them.** ASSUMED: every save-side signal lands
     identically for both (no negatives in NEP's `ai` section fits "never written" and "written then
     arbitrated away"; the `ai` section is known not to serialise every type). For scale on H2: the
     Allies faction file that also reaches NEP carries `+150` (europe_first, focus_on_europe_post_france
     ×5), `+100` and `+75 north_africa` — `commonwealth-handoff` needed **−130** against those same
     bids, so `−100` is a mid-range bid, not a veto. **What separates them is owner-run
     `imgui show ai-strategy` on NEP**: whether the block is listed under Active strategies settles
     H1's `enable`, and the `front_unit_request` panel's Weighted Values against the Allies entries
     settles H2 — subject to the unresolved question (`wa-diagnosis` technique 5 rule 3) of whether
     entries sharing an `area =` are summed at all, which is itself load-bearing for H2.
- **H4 is KILLED, and cleanly** (MEASURED): NEP's African divisions carry no `expeditionary_owner`,
  sit in NEP's own `units`, and are covered by NEP's own front/buffer orders with no army-group
  inheritance. NEP's only expeditionary traffic is **7 divisions lent outward to RAJ**, its neighbour
  — which is the intended behaviour if anything. Positive control for that scan: 7 countries command
  expeditionary divisions at 1943.6 (ITA 11, RAJ 7, JAP 6, GER 4, SOV 3, FRA 1, CHI 1), so a zero
  would have been a real zero.
- **Owner-run `imgui show ai-strategy` 2026-08-25 — the block IS armed. H1's enable-gate variant is
  KILLED.** MEASURED from the screenshot: `WA_AI_MILITARY_CAPS_unfit_army_stays_home` is listed under
  Active strategies, so `has_war = yes` AND NOT `is_fit_for_expeditionary_front` both passed and the
  `num_of_military_factories > 5` gate read the country as unfit. DERIVED that the country shown is a
  small Allied minor (NEP or equivalent): `WA_AI_MILITARY_ARCHETYPE_minors_home_first` is listed
  beside it and gates on `WA_AI_MILITARY_is_minor_country`. **Owner confirmation of the tag is still
  owed** — the window shows one country and the screenshot does not name it.
- **Incidental finding from the same screenshot, NOT this subject:** the `WA_AI_MILITARY_COUNTRY_ENG_*`
  blocks are listed for a country that is not ENG. MEASURED cause:
  `WA_AI_MILITARY_COUNTRY_ENG_INVASION.txt:194` gates on `is_in_faction_with = ENG`, not on a tag, so
  every Allied member loads ENG's Country-layer invasion strategies. Whether that is intended is a
  question for the military-layer spec (`WA_AI_MILITARY_SYSTEM.md` §5), not for this subject.
- **What the screenshot does NOT settle (`wa-diagnosis` technique 5, rule 1): a name under Active
  strategies proves `allowed`+`enable` passed and proves NOTHING about the `state_trigger` inside the
  payload**, which the engine evaluates later, per candidate state. So the narrow form of H1 survives
  intact — the entry can be listed and match no state at all if `FROM.FROM` does not render there.
  H2 survives unchanged. **The next discriminator is the same window, one panel down:** the
  `front_unit_request` tree, which lists one row per active ENTRY with its `Weighted Value`. An entry
  traceable to this block appearing there with a negative weight moves the failure to H2 (outbid); its
  absence from that tree while the block sits in Active strategies is the signature of H1.
- **Owner-run `front_unit_request` panel, NEP, 1942.2 — H1 is KILLED. The block IS armed AND the
  engine holds its entry at Weighted Value `-100`.** MEASURED: 9 active entries, reconciled 9/9 to
  `file:line` by enumerating `front_unit_request` + `front_control` + `invasion_unit_request` in
  `common/ai_strategy/` load order (`wa-diagnosis` technique 5 rule 3). **The base on this build is
  183, NOT the 736 / 779 recorded in the skill** — those were calibrated pre-`4f66a5822`, and deleting
  `africa_war_3` shifted every handle. The second-best candidate scores 6/9 with three value
  mismatches, so the fit is unambiguous; it is further corroborated by three consecutive entries of
  one block (`ALLIES_europe_first` lines 27/33/39) landing on 777/778/779 consecutively.

  | Target | Block | file:line | Value | via |
  | --- | --- | --- | --- | --- |
  | 745/746/747 | `ARCHETYPE_minors_home_first` | archetypes.txt:117/123/129 | -100 | area (south_america, central_america, sink_africa_regions) |
  | 748 | `ARCHETYPE_minors_home_first` | archetypes.txt:139 | -100 | state_trigger (southeast-asia sinks) |
  | **764** | **`CAPS_unfit_army_stays_home`** | **caps.txt:162** | **-100** | **state_trigger** |
  | 777 | `ALLIES_europe_first` | ALLIES_FRONT.txt:27 | **+150** | tag |
  | 778 | `ALLIES_europe_first` | ALLIES_FRONT.txt:33 | **+75** | area = north_africa |
  | 779 | `ALLIES_europe_first` | ALLIES_FRONT.txt:39 | -100 | state_trigger |
  | 851 | `ALLIES_east_africa_contested_FRONT` | ALLIES_FRONT.txt:1742 | **+150** | area = WA_AI_MILITARY_east_africa_regions |

- **The diagnosis is therefore H2 — and the design comment that delegated the job says so in writing.**
  `WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt:132-135` states that East Africa is deliberately NOT
  braked by `minors_home_first`, because a -100 there would cancel the Faction +150 for SAF/RAJ, and
  that the CAPS lane (home_threatened / not_safe / weak minor) is what keeps the unfit out instead.
  **This subject's block IS that CAPS lane** — and it was written at -100 against pulls of **+150**
  (`east_africa_regions`, the alias that covers the Kenya/Sudan approach corridors NEP occupies) and
  **+75** (`north_africa`, which is NEP's actual front-order path: Constantine-Tunisia-Gabès-Tripoli).
  The brake is the only thing standing between an unfit minor and a +150, and it is 100. DERIVED:
  under-sized, not inert.
- **Two things this still does NOT establish, and neither should be skipped when re-cutting the value.**
  (i) Per technique 5 rule 2 the panel lists ENTRIES, not matches: our row being present proves the
  engine holds -100 for the entry, **not that the `state_trigger` matched any state** — 748 and 779 are
  also `state_trigger` entries and are listed identically. (ii) Whether the engine SUMS entries sharing
  an `area =` is still ASSUMED (technique 5 rule 3), and it decides whether "-100 against +150" is even
  the right arithmetic. **A magnitude that works under either reading is the safe cut** — the repo's
  force-off convention (-2000 / -5000) plus the `# economy: was -300 / was -2000` comments on the
  neighbouring entries show these negatives were mass-reduced at some point; a veto-class lane should
  not have been in that reduction.
- **H3 is untouched by all of this and caps the ceiling of any value change.** MEASURED: only 5 of 12
  (1943.6) and 7 of 16 (1944.6) NEP divisions are under a front order at all. Raising -100 cannot reach
  the `buffer` / no-order remainder however large it gets.

- Tooling defect found while scoring: **`savegame.py buildings` does not accept a comma-separated tag
  list.** `buildings NZL,SAF,CAN --match arms_factory` returns `states owned=0 controlled=0` plus
  `NO MATCH: … 0 of 0`, which looks exactly like a wrong building key rather than a rejected argument.
  Run it once per tag. (`plans.py` and `stock.py` do take multi-tag — the inconsistency is the trap.)
  Second: **BHU dies between 1943.6 and 1944.6** (`controlled=0`, no `units` section) while its block
  still reports `arms_factory owned=1`, so any BHU reading at 1944.6/1945.10 is really a 1943.6
  reading — and BHU is the player tag besides, so the BHU half of leg (a) is void as an AI probe.- Scope: a country that cannot equip a real infantry division does not hold a front outside its
  own neighbourhood. Owner rule (2026-08-23): Nepal/Bhutan defend near home, never beyond India;
  no militia expeditionary corps on a faction's overseas front.
- State: `WA_AI_MILITARY_is_fit_for_expeditionary_front` + `WA_AI_MILITARY_state_is_beyond_home_reach`
  (`WA_AI_MILITARY_triggers.txt`) and `WA_AI_MILITARY_CAPS_unfit_army_stays_home`
  (`WA_AI_MILITARY_DEFAULT_FRONT_caps.txt`) written in the working tree, **committed and live in campaign `8f9b5653`** (see the scoring block below).
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
- **Finding 2026-08-25 that bears directly on why probe (a) failed: the `-130` is an E2 violation and
  the engine cannot be seeing -130.** MEASURED: `tools/military_economy_audit.py` reports exactly one
  `E2-front_unit_request-range` violation in the whole repo —
  `WA_AI_MILITARY_COUNTRY_ENG_FRONT.txt:694 WA_AI_MILITARY_ENG_east_africa_delegated_FRONT - value
  -130 outside [-100, +200]`. Per `documentation/WA_AI_MILITARY_ECONOMY.md` rule E2 the type is a
  **percent factor** where -100 is the full veto and **anything lower is saturation**. DERIVED: the
  2026-08-24 deepening from **-75 to -130 bought 25 points, not 55** — it saturates at -100 — and
  every net-bid figure written for this subject on the basis of -130 is off by 30. That is a concrete,
  previously unnamed reason probe (a) read ~1:1 instead of clearing. **Do not re-deepen it**; the
  lever that remains is the pull side, exactly as `minor-expeditionary-fitness` had to do in the same
  session. Pre-existing violation, not introduced by this session's edits (verified by stashing).- **Campaign `8f9b5653` scored 2026-08-25 (build = HEAD `ed109de9d`, i.e. the delegation `-130` + the
  `egypt_is_invaded` split + the `africa_war_3` deletion all live) — probe (a) FAILED again, probe (b)
  passes on its letter and FAILS as rewritten, and Egypt is lost harder than in `db5029c2`.**
- **Probe (a) FAILED.** MEASURED ENG divisions, East Africa + Sudan vs Egypt: **7/7, 9/6, 7/9, 8/8**
  at 1940.9 / 1940.12 / 1941.3 / 1941.6, then 0/8, 0/9, 1/1 once ENG has no East African presence at
  all. The bar ("EA+Sudan drops below Egypt") is met in **1 of the 4 saves where an East African
  theatre exists**; it ties twice and inverts once, and the 1941.12/1942.6 "0 vs 8" cells are vacuous,
  not passes. **The killing cell is 1940.12: EA+Sudan 9 vs Egypt 6** — Egypt was by then invaded
  (Marsa Matruh, Cairo, Alexandria all Axis), so the ENG `north_africa` net should have been the
  invaded **+85 against East Africa's +20, 65 points clear**, and East Africa still outdrew Egypt.
  Under the assumed cross-area ordering that cannot happen. Including Tanganyika/Uganda makes it worse
  (13/7 and 15/6 in the first two saves). **Improvement is real but short of the bar**: `db5029c2` read
  24/7, 24/11, 20/12, 21/12 (EA ~2-3× Egypt); this build reads ~1:1. DERIVED — the deletion moved the
  ratio from ~2.5 to ~1.0 and no further, and the `+20 < +25` cross-area ordering **remains unproven by
  the only probe that can prove it**.
- **Probe (b): 6 of 7 saves PASS on the letter while Egypt is being conquered — the rewrite is now
  owed, not optional.** MEASURED province-level control (`control --provinces`, both omitted-field
  defaults applied): Marsa Matruh falls between 1940.9 and 1940.12 and is **never retaken**; Cairo is
  GER 12/18 by 1940.12 and GER 18/18 from 1941.3; Suez falls by 1941.3, Sinai by 1941.6; by 1942.12 the
  20-state scope is **GER 89 / ITL 89 / ENG 0 provinces**. Force ratio inside Egypt (Axis:Allied
  divisions): 1.0 / **2.9** / 1.2 / 1.2 / 0.9 / 2.0 / **6.0** across the same seven saves. Egypt+Libya
  December 1940 = **Axis 61 vs Allies 13 (4.7:1)** against `db5029c2`'s 3.5:1, and December 1942 =
  **38 vs 2 (19:1)**. DERIVED: the ratio got worse, not better. **No Allied division stands on Libyan
  soil in any of the seven saves.**
- **The `africa_war_3` deletion cannot be credited or blamed on this campaign, because the British
  army it is measured against is half the size of the previous one — BY DESIGN.** MEASURED: ENG
  deployed 30 / 28 / 30 / 30 / 30 / 35 / 45 across these saves, against **63 in December 1940 in
  `db5029c2`**. The buffer share did fall (40 % = 25/63 -> **29 % = 8/28** in the same month, decaying
  to 18 % by 1942.12) but the absolute buffer pool fell 25 -> 8 mainly because the whole army is
  smaller; front went 26 -> 12 over the same comparison. **Owner, 2026-08-25: this is `reserve-quality`
  (`ed109de9d`) working as intended** — the reserve bank no longer opens for an overseas-only war, so
  ENG fields fewer, better-equipped divisions in the early game instead of a wave of 30 %-fill reserve
  divisions. Do NOT diagnose it as a defect, and do not compare a division COUNT across the
  `ed109de9d` boundary: `db5029c2`'s 63 and this campaign's 28 are not the same unit of army. Every
  ratio in this subject that divides by ENG's division count needs re-basing on quality (fill, front
  frontage held) before it can be compared to a pre-`ed109de9d` campaign.
- Two measurement traps found here, both of which inflate probe (b) if reused as written:
  **(i) divisions are located in states the enemy fully controls** — at 1941.12 ENG shows 7 front-ordered
  divisions in Cairo and RAJ 9 while `control 446 --provinces` reads GER on all 18 provinces (same shape
  at 1942.6). Location and control come from different blocks; ASSUMED naval transit or mid-battle
  stamping at the destination. Any "N divisions in Egypt" count must be restricted to
  **Allied-controlled ground**, which is what turns 6 letter-passes into 4 rewritten failures.
  **(ii) The state grouping in the probe text is wrong in two places**: state **960 "Libyan Platau" is
  UKE-owned with an EGY core** and belongs to the Egypt bucket despite its name, and **no state named
  Sallum, Sidi Barrani, Tobruk, Aswan or Fezzan exists** — they are provinces inside 452 / 552 / 451 /
  456. Libya has 8 states, not 7.
- Two further MEASURED facts for the next lever: **Italy is already inside Egypt before the probe
  window opens** (1940.9: 3 ITA front divisions in Marsa Matruh holding 4/14 provinces, 4 in Libyan
  Platau holding 2/6) — the decision point is earlier than 1940.9; and **RAJ's +50 El-Alamein
  reinforcement is invisible after 1941.12 because the delegate leaves the theatre for the Japanese
  war** (RAJ Egypt 0/7/6/3/17/0/1 while its 57-division army pivots to Assam 8, East Bengal 7,
  Kachin 6, Mandalay 4, Burma 4 by 1942.6). A reinforcement verdict that cannot fire once Japan is in
  the war is a gap in the rule, not a tuning error.
- Still owed and NOT delivered by this campaign: the **F9 boot test** for the block add/remove, the
  console harness for `WA_AI_MILITARY_egypt_is_invaded`, and the owner's `imgui show ai-strategy`
  confirmation that both brake blocks LEAVE Active strategies once an enemy is on Egyptian soil.- Scope: Commonwealth defensive missions, East Africa as the Indian army's campaign, Kuwait
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
- **Second lever shipped 2026-08-24 - the ENG `north_africa` throttles stand down while Egypt is
  invaded.** New control-panel trigger `WA_AI_MILITARY_egypt_is_invaded` (ROOT-relative, tag-free,
  11 Egyptian states - deliberately wider than the {446,447,453} East-Egypt anchor, because 452
  falls first). The `area = north_africa` `-40` is split out of `africa_war_1` into
  `WA_AI_MILITARY_COUNTRY_ENG_FRONT_north_africa_brake_egypt_held`, keeping its original gate plus
  `NOT egypt_is_invaded`; `africa_war_1` keeps `central_africa -50`. **Owner decision 2026-08-24, the
  second half of the lever: `WA_AI_MILITARY_ENG_africa_war_3_FRONT` and its `_border_held` split are
  DELETED outright**, so the `-20` peacetime-onward throttle is gone unconditionally rather than
  gated - and with the parent go its two `front_control` entries on the ITA / ITL fronts, i.e. ENG's
  north-African fronts return to engine-default `ordertype = front` handling. That last part is a
  behaviour change in its own right and is the thing to watch in the next campaign. ENG's
  `north_africa` net becomes `+45` clear and `+85` invaded (`WA_AI_MILITARY_SYSTEM.md` §16
  restated); the margin over East Africa's `+20` is 25 points clear, 65 invaded. The `-130` is NOT
  re-sized - its intent holds at both nets. Removal rather than a `+60` counter-entry is deliberate:
  a counter only works if the engine sums per area, a removal works under either reading.
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

### raj-trucks — CAMPAIGN-OK (2026-08-25)
- **Campaign `8f9b5653` scored 2026-08-25 — PASSED on all three positive legs AND on the control.**
  MEASURED: RAJ holds `eng_motorised_infantry` level 1 with `date = 1938.5.29.1` — a real in-campaign
  research date, not the `1936.1.1.12` start-grant marker — in every sampled save from 1940.6 on, with
  no `date="1.1.1.1"` in-progress twin anywhere (the false-duplicate gotcha did not fire). Its
  `eng_motorized_equipment_1` line runs **3 / 9 / 20 / 41 / 29 active factories** at 1940.6 / 1941.6 /
  1942.6 / 1943.6 / 1944.6 (scoped to `military_lines`, `equipment_variant_index` resolved through the
  top-level `equipments={}` registry against the 11 `archetype = motorized_equipment` defs, never by
  variant name). `wa_ai_fielded_eq_ratio` climbs **0.657 -> 0.903 -> 0.994 -> 0.998 -> 0.998 -> 0.999**
  while the army grows 49 -> 110 divisions: full fill and the truck line coexist.
- **The control holds — the fix did not become "everyone builds trucks".** MEASURED at 1943.6 and
  1945.10: NEP (1 arms factory), BHU (1) and AFG (1) carry **no `*_motorised_infantry` tech and no
  motorized line** at either date; TIB, SAU, VEN, COL and EIR the same. **An unplanned positive control
  for the new `num_of_military_factories > 10` arm**: ETH has neither tech nor line at 8 arms factories
  (1943.6), then researches `motorised_infantry` on **1944.10.3** and runs a **3-factory** line at
  1945.10 with 13 factories — exactly the tier boundary the amendment describes.
- **The 3-factory tier is visible and so is one possible regression.** MEASURED: CAN, AST and SAF each
  ran **exactly 3** active truck factories at 1940.6, SAF holding 3 through 1942.6 — the small-industry
  tier is in force. CAN and AST later scale far past it (CAN 14 -> 16 active, AST 34 -> 0/2 queued) as
  >10-factory dominions. **But SAF has no motorized line at all at 1945.10 on 49 owned arms
  factories**, after running the 3-tier for three years. MEASURED as absence; ASSUMED as a possible
  tier regression, and the one thing in this subject worth a look before it closes.
- Scoring notes: RAJ itself sits at 120->138 arms factories, so it satisfies the `> 10` arm as well as
  `can_motorize_support` — this campaign confirms the outcome, not which arm delivered it (DERIVED).
  Do not read AST / CAN / SAF / ROM tech presence as evidence either way: all four hold
  `*_motorised_infantry` at `date = 1936.1.1.12`, i.e. **start-granted**. YUG and SIA truck readings are
  dead-tag artefacts (0 controlled states, fill 0.000) and are not leaks. RAJ's 1945.10 line reads
  `active 0 / queued 27` while RAJ still runs 120 active mil-line factories — ASSUMED a snapshot taken
  mid-transfer, not a dead line.
- **Remaining before CLOSED:** the SAF tier question above. Everything else in the closing criterion is
  met.- Scope: owner report 2026-08-24 — the Raj produces no motorized_equipment. MEASURED chain: RAJ is in
  `WA_AI_CONFIG_DIVISIONS_can_motorize_support`, so its infantry target template is the `_MOT_` variant
  (`WA_AI_TEMPLATES_infantry.txt` 1002/1005/1006, ~220 motorized_equipment per division per
  `WA_AI_DIVISION_CREATOR_effects.txt`), but every `*_motorised_infantry` tech was gated on
  `WA_AI_RESEARCH_needs_mechanized` (USA/ENG/CAN/AST/SAF, or armor+medium/heavy focus, or >100 mil
  factories) — RAJ satisfies none, so it could never unlock `eng_motorized_equipment_1` and its
  motorised support companies had no equipment to fill. `WA_AI_RESEARCH_needs_trucks` existed for
  exactly this and was `always = yes`, i.e. inert inside the AND.
- State: written in the working tree, **committed and live in campaign `8f9b5653`** (see the scoring block below). `WA_AI_RESEARCH_needs_trucks`
  (`WA_AI_RESEARCH_tanks.txt`) now ORs can_motorize_support / needs_mechanized / use_armor_templates /
  use_motorized_templates; the 12 `*_motorised_infantry` ai_will_do blocks (`armor.txt` + 11
  `armor_<tag>.txt`) key on `needs_trucks` alone, which is what `tools/ai_will_do_replacer_armor.py`
  maps the `motorized_equipment` category to. Strict superset of the old gate: no country loses the
  tech. Side effect by design: `vehicle_winch`
  (`electronic_mechanical_engineering.txt`, `NOT = { needs_trucks }`) stops being researched by
  countries with no truck demand — it was unblockable while the trigger was `always = yes`.
- Closed when: a campaign save shows RAJ holding a `*_motorised_infantry` tech, a non-zero
  motorized_equipment production line, and its infantry divisions at full equipment; control =
  a foot-army minor outside `can_motorize_support` and outside the earned latch still has no truck
  tech and no truck line (the fix must not become "everyone builds trucks").
- Amended 2026-08-24 (owner, MEASURED in `05_defines.lua`): a horse army needs trucks too — 500
  motorized_equipment fully motorize one supply hub (`SUPPLY_HUB_FULL_MOTORIZATION_TRUCK_COST`) and
  the engine AI does it unprompted below `NDefines.NAI.DIVISION_SUPPLY_RATIO_TO_MOTORIZE = 0.95`,
  every 48h. `needs_trucks` therefore also fires on `WA_AI_CONFIG_is_major_country` or
  `num_of_military_factories > 10`. Because that widens the tech to small industries, the flat
  `equipment_production_min_factories_archetype = 10` truck floor is now tiered like the amphibious
  floors: > 49 mil factories keeps 10 (unchanged for majors), < 50 gets a new 3-factory tier
  (`WA_AI_PRODUCTION_build_trucks_stockpile_low_small`). Behaviour change to watch: CAN / AST / SAF
  had the tech and the flat 10 before; they now sit in the 3 tier.
- Not done here, latent: `WA_AI_TEMPLATES_has_motorized_unlocked` checks only the generic
  `motorised_infantry`, while every sibling `has_*_unlocked` ORs the national variants — so it is
  false for every tag-tree country. Harmless today (`use_motorized_divisions = always no`), a trap
  the day motorised divisions are switched on.

## PARKED

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
| `silo-breadth` | TESTED (console harness owner-PASSED 2026-08-24) | Fuel silos stall at the first state's cap of 6; shipped fix = CIC/MIC/NIC/REF availability standard + breadth-first walk, harness `event wa_silo.1`/`.2` | A campaign save shows a country with silo need > 6 holding BUILT `fuel_silo` levels in >= 2 states, and the harness walk skipping a state at its cap |
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
