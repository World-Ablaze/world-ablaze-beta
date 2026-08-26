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
- **Lever shipped 2026-08-25 (owner order): the -130 counter-bid is replaced by an EXEMPTION.**
  `WA_AI_MILITARY_ENG_east_africa_delegated_FRONT` DELETED (it saturated at -100 per E2 — the repo's
  one E2 violation, now purged — and still left ENG at net +50 on East Africa, above a quiet Egypt's
  +45; MEASURED on baseline `15176ce6`: EA+Sudan 13→18 ENG divisions vs Egypt 7→4 while Egypt fell,
  1940.8-11, to ITL alone). The stand-down is now a NOT-term inside the Faction +150
  (`ALLIES_east_africa_contested_FRONT`): mission owner + `commonwealth_east_africa_available` → not
  pulled at all (net 0 vs RAJ +250), correct under either cross-area summing reading; delegate
  unavailable → ENG back at the full +150 (the old block's fallback objection, kept, not refuted).
  Doc §16 rewritten. Reviews: architecture OK; lessons CONCERNS, 3 items applied here.
  **Flap exposure, stated (lessons item 2):** every availability term is a single threshold
  (`num_divisions > 29`, pacific quiet, theatre contested) with `abort_when_not_enabled`, so the
  month RAJ dips to 29 and back, ENG's +150 re-arms then re-exempts. Worst case of the flap = the
  PRE-fix behaviour (full +150), never worse; the bar was set at 29 precisely for margin (RAJ
  measured 40-44 across 1941) — same single-threshold shape as the old -130, unchanged by this
  lever. No hysteresis band added; if a campaign shows monthly flapping, that is the lever.
  **Known gap, named (lessons item 1 rationale): `num_divisions > 29` counts RAJ's TOTAL army** — a
  RAJ fully committed to the Burma wall still reads "available" while East Africa sits empty and
  ENG stays exempted. The pacific-quiet term covers the Japan case; the non-Japan variant of an
  absent delegate is uncovered and is what probe (a2) below watches.
- Verification, rewritten per the lessons review (divisions in the save, never the trigger reading
  true): (a1) while the exemption is live (delegate available), **RAJ divisions physically standing
  in the East-Africa states (regions 17/217/380/381) >= 8** and ENG's EA+Sudan contingent below its
  Egypt contingent; (a2) if RAJ's in-theatre count reads < 4 while `num_divisions > 29`, the
  total-vs-in-theatre conflation above is the live failure — reopen with that measurement; (a3)
  ENG on regions 17/217 under delegation: net -50 (africa_war_1 alone), zero ENG divisions there
  acceptable ONLY with RAJ present in the same regions.
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
- **Scope extended 2026-08-27 `[raj-gulf-garrisons]` (owner feedback, feedback_save - ironman, not measurable):**
  RAJ garrisons the Gulf so British divisions do not. (i) Kuwait STANDING watch - RAJ 0.02 on 656
  whenever ENG is at war (`RAJ_kuwait_standing_watch_available`), exclusive with the threat-gated
  mission, whose "a guard needs something to guard against" term is KEPT, not refuted. (ii) Aden
  converted from a flat ENG 0.075 buffer (protect_home order 6) to a delegated mission on the Kuwait
  pattern: RAJ 0.04 (order 9210), ENG floor 0.02 (order 18) / fallback 0.075 (order 19), verdicts
  `ENG_aden_guard_active` / `RAJ_aden_guard_available` / `commonwealth_aden_guard_available`. Spec
  doc SS26. All new buffers `subtract_fronts_from_need = no`. Reviews 2026-08-27: architecture
  CONCERNS + lessons CONCERNS, all required items applied (see the batch commit). **F9 boot test
  OK 2026-08-27 (owner).** Verification (SS26 probe): RAJ divisions physically standing in 656/659 -
  INCLUDING while JAP is neutral, the window where RAJ's areadef park competes hardest - with ENG at
  its 0.02 floors; ENG back at 0.075 on Aden when RAJ is unavailable.
  **Amended 2026-08-27 (owner order after review of the bars):** the three RAJ Gulf verdicts
  (Kuwait mission, standing watch, Aden) read `WA_AI_MILITARY_delegate_force_floor` instead of
  `army_still_operational` - the latter's 41-division / eq-0.9 collapse bars sit above a healthy
  reserve-quality Indian army (MEASURED `8f9b5653`: RAJ 30 divisions at 1941.6) and would have kept
  all three missions permanently disarmed. `num_divisions > 29` kept as the count bar (known
  reduced margin post-`ed109de9d`, no hysteresis - flap exposure already recorded above).
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

### fra-battle-of-france — OPEN (2026-08-27)
- Scope: owner feedback 2026-08-27 (feedback_save - ironman, so the ~20-division figure is the
  owner's report, not a save measurement): France garrisons North Africa / Corsica during the
  Battle of France while the Italian border sits open. One intended behaviour: while the metropole
  is invaded, the empire stops absorbing the army and the Alpine border is held.
- State: shipped 2026-08-27. (i) `FRA_homeland_invaded_recall_colonials_THEATRE` - `area_priority
  -90` on north_africa / mediterranean (Corsica sits in region 373 of that area) / middle_east,
  gated `home_threatened` + at war + not capitulated. (ii) Alpine pair `FRA_alpine_front_FRONT`
  (+100 south_france) / `_THEATRE` (+100), gated GEOGRAPHICALLY on `any_enemy_country =
  is_italian_homeland_power` (lessons ruling: never `has_war_with = ITA`, the armistice flip renames
  the tag). (iii) `FRA_defense_of_the_colonies_FRONT` re-armed from the economy-pass zeros to the
  -5000 release convention (audit E7), gated `home_threatened`; the all-zero no-op
  `FRA_ignore_garrisons_until_invasion_start` deleted. Spec doc SS25. Reviews 2026-08-27:
  architecture CONCERNS + lessons CONCERNS, required items applied. F9 boot test OK 2026-08-27.
- ASSUMED, stated: `garrison -5000` release semantics are WA convention, never engine-measured; the
  colonial channel of the reported 20 divisions is inferred from code, not from the (ironman) save.
- Closed when: a Battle-of-France save (non-ironman) shows (a) FRA North-Africa + Corsica division
  count falling once `surrender_progress > 0.05`, (b) >= 2 FRA divisions on the south_france fronts
  while an Italian homeland power is an enemy, (c) no regression of the Maginot/fall_rot arithmetic
  (north_france/france nets unchanged).

### rk-no-divisions — OPEN (2026-08-27)
- Scope: owner rule 2026-08-27: a Reichskommissariat builds (trains) NO division, of any role.
  Divisions granted by script are out of scope — the RCZ ger_armor.999 bootstrap (6 spawned
  garrison divisions, recorded design) and the Military Police `load_oob` template files stay.
- State: shipped 2026-08-27. (i) New archetype `WA_AI_CONFIG_is_reichskommissariat`
  (`WA_AI_CONFIG.txt`) = `has_autonomy_state = autonomy_reichskommissariat` — dynamic, covers all
  creation paths MEASURED this session (GER decisions 39 tags, ITA decisions 8 tags, ENG dominion
  conversions, toolpack) with no tag list. The reichsprotectorate autonomy (RCZ) deliberately does
  not pass; RCZ enters only if the GER decision later moves it to RK autonomy. **ITS (Italian East
  Africa) exempt by owner order 2026-08-27** (mid-session): script never gives ITS the RK autonomy
  (MEASURED: only `autonomy_collaboration_government`, ITA.txt establish_ITS), but the autonomy
  ladder can slide a fascist ITA subject into it, and ITS's Ascari divisions are a fed design
  (ITA sends equipment + `add_units_to_division_template`). Exception encoded as
  `NOT = { original_tag = ITS }` inside the CONFIG trigger (the one file where tags are legal).
  (ii) New block
  `WA_AI_PRODUCTION_DEFAULT_reichskommissariat_builds_no_divisions`
  (`WA_AI_PRODUCTION_DEFAULT_army_composition.txt`): `build_army infantry -500` (USA
  disarmed-nation precedent) + `role_ratio -1000` on every WA template role except the removed
  garrison role (infantry, cavalry, suppression, motorized, mechanized, armor, light/medium/
  heavy/modern_armor, marines, mountaineers). Legacy tag-list blocks
  (`GER_reichskomissariats_dont_build_divisions` -1 war-gated, `ENG_puppets_...`,
  `FRA_puppets_...`) kept untouched — additive change, they cover pre-RK windows.
- Why the old brake failed (MEASURED): `GER_reichskomissariats_dont_build_divisions` is value -1
  (vs USA's -500), war-gated (`enable = { has_war = yes }` — nothing at peace), infantry-id only
  (the Military Police templates are cavalry-role), and a tag list that misses ITA's 8 RK tags and
  ENG's dominion conversions. Meanwhile released RK tags inherit overlord templates and
  `WA_AI_PRODUCTION_build_army_base` asserts `role_ratio infantry = 100` for everyone.
- ASSUMED, stated: engine stacking of same-id entries across ai_strategy blocks; `role_ratio` base
  100 + value with a negative net reading as zero want (supported by the campaign-9be92c89 note in
  the same file: negative infantry want stopped USA training entirely). The engine may
  DECOMMISSION existing RK divisions of zero-want roles (garrison-role lesson, SOV Strelkovaya) —
  accepted, the owner rule wants them at none; the block comment says so instead of claiming
  "granted divisions stay".
- Reviews 2026-08-27: architecture CONCERNS + lessons CONCERNS — both on the same point (the
  "granted divisions stay" claim was ASSUMED against the decommission mechanism): claim relabelled
  and accepted as above. Lessons item 2 (12 role-id strings, one bad token silently voids the
  block — F9 + error.log id check) folded into Verification; lessons item 3 (ENG/FRA colonial
  blocks share `build_army id = infantry` with RK-eligible tags): both negative, summing cannot
  flip sign, recorded ASSUMED.
- Verification: F9 boot test owed (ai_strategy block add = launch-test territory, 2026-08-09 CTD
  precedent) INCLUDING error.log check that none of the 12 `role_ratio`/`build_army` id tokens is
  rejected; owner `imgui show ai-strategy` on an RK tag (e.g. RUK after conversion) listing the
  new block under Active strategies is the cheap confirmation.
- Closed when: a campaign save shows every country holding `autonomy_reichskommissariat` (ITS
  excepted) with zero divisions in training and a division count that only ever falls or holds
  (scripted grants aside); control: ITS still fields/trains its colonial divisions.

## PARKED

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
| `allied-total-commitment` | TESTED, parked 2026-08-27 for the next campaign (WIP limit; F9 boot test for the 2026-08-27 CAN reserve-batch reward still OWED) | CAN 4-9 div, 100% areadef home garrison (`8f9b5653`); release trigger PROVEN on CAN (wa_tc.1 harness 1942.2, closure PASS); `garrison -5000` engine honour still ASSUMED | Campaign legs: (a) CAN majority front/buffer outside North America while home safe; (b) AST/NZL/RAJ areadef ~0 while Pacific quiet AND re-garrisoned within 3 months of `pacific_threat_imminent`; (c) dominions on African fronts once past the 6-factory floor; (d) control: a non-faction minor at war keeps its home garrison; plus SS24 bulwark-guest probe (zero Commonwealth div on FRA soil while FRA holds `disjointed_government`, historical difficulty). Full record: git log of this file + [allied-total-commitment] commits |
| `scripted-invasion-reservation` | OPEN, parked 2026-08-27 (owner order; console harness legs A-C PASSED 2026-08-23, leg (b) NOT CHECKED on `8f9b5653` - the Allied AI never wanted a French landing, so the mechanism never ran) | Halab 1944.6: USA order 252 holds 9 divisions on a GER-held, GER-flagged reserved target - H1 (@FROM inert in ai_strategy context) vs H2 (-200 outbid on a pre-existing order) undecidable from the save | A campaign in which the Allied AI wants a reserved beach shows no engine invasion order against it; or an ai_strategy-context harness leg proves @FROM renders. Full record: git log of this file + [scripted-invasion-reservation] commits |
| `uk-truck-supply` | SHIPPED 2026-08-27, boot OK - parked for the next campaign (WIP limit) | Owner: ENG truck deficit every game, Africa supply fulfillment < 50%. MEASURED in code: demand multiplied (hub cost 60->500, motorize ratio 0.95, buffer 1.2) while ENG (36 arms factories) sat on the 3-factory tier with a 1000-stock cutoff | A campaign shows ENG on the 6-factory tier with motorized stock >= 1500 sustained at war, and Africa hub motorization no longer truck-starved. Shipped: stock bar 1500 = lend-lease starve (registry truck_stock_starve_floor), 30-49-factory tier at 6, min_wanted_supply_trucks 2000/1000 (vanilla precedent SIA). Successor of the raj-trucks SAF-tier residual |
| `suppression-templates` | SHIPPED 2026-08-27, boot OK - parked for the next campaign (WIP limit) | Owner: countries burn army XP designing 4x-light-cav garrison templates, field them to the FRONT, and the template (no MP) is also the state-garrison pick. MEASURED in code: role prio 1000 (~37% of XP draws), reinforce_prio 1, use_suppression_templates = always yes | A campaign shows minors' army XP not spent on suppression templates while neutral, and no suppression-template divisions under front orders. Shipped: trigger gated (war OR non-core control) + LATCH on the existing flag (no mid-campaign decommission flip), role prio 50, reinforce_prio 0, dead build_army_cavalry pair deleted. Engine garrison scoring untouched |
| `raj-trucks` | CAMPAIGN-OK (2026-08-25, campaign `8f9b5653`: all three positive legs + the control PASSED) | SAF runs the 3-factory truck tier 1940-42 then has NO motorized line at 1945.10 on 49 arms factories (possible tier regression; MEASURED as absence) | The SAF tier question is answered (regression fixed, or explained and accepted); every other criterion already met — full record: git log `[raj-trucks]` + this file's history |
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
