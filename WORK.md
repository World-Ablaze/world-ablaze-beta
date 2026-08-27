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

> **Campaign `24933fb9` scored 2026-08-27** (cloud, `dlcs=257535`, BHU observer, 118 monthly saves
> 1936.2-1945.11, unbranched, build = HEAD `2f16ec583` — DERIVED from push 03:46 / run 04:05, and
> MEASURED by two fingerprints: CAN's 10 `Reserve Divisíon` deployed 1939.11 (`eb7338da4`) and ITA's
> 5-state AOI buffer (`4044dea78`). `wa_tlm_version = 31`, no bump in the batch). F1-F9 in the
> checklist. **Headline: first campaign of six where Germany actually COLLAPSES** (controlled states
> 115→72 over 1943.6→1945.11, fill 0.71, SOV on German soil, HUN/ROM flipped) — but won from the
> East alone. **The Western arc inverted after Torch**: landings (1942.11) took Algeria only, GER
> seized Tunisia (Case Anton), El Alamein fell 1943.1-2, Cairo 1943.5 (ITA), Suez 1943.7, and the
> Allies held zero Libyan provinces to the end; Tunis is still German at 1945.11. **Root MEASURED
> for the invasion half: ENG/USA/FRA hold ZERO type-3 orders anywhere on the map for 30 months
> (1942.12→1945.6).** Six-box diagnosis (2026-08-27): the closed loop
> `WA_AI_MILITARY_ALLIES_invasion_cap_without_foothold`
> (`WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt:304-318`) — enable `NOT has_western_foothold` never
> goes false because its own -100 `invasion_unit_request` on every enemy prevents the foothold that
> would disarm it; contributing: `dday_hold` branch 1 (-2000 pre-1944.3), the scripted-target
> reservation on GER (re-stamped monthly 1942.12→1944.9), `dday_fire_INVASION:739-744` carrying the
> unfixed date/JAP pair its FRONT twin was cured of, and FRA under `minor_allies_dont_invade` for
> the whole war. Post-landing freeze exonerated (inert ~26 of 30 months). ASSUMED (engine): whether
> -100 floors the request and whether entries sum per target — owner `imgui show ai-strategy` on
> ENG 1944.6 (`invade` + `invasion_unit_request` trees) separates them. **Candidate subject, not
> admitted (WIP limit): allied-invasion-foothold-deadlock.** Second candidate, sharpened from
> `8f9b5653`: **CAN never rebuilds** — 2-4 divisions 1941-1944 on 104 arms factories (the reserve
> batch deployed then was consumed by 1942; the army-building gap is upstream of any reserve grant).
> **USA half diagnosed and first lever SHIPPED 2026-08-27 `[reserve-quality]`** (owner order "l'US
> doit déployer toutes ses divisions de réserves"): MEASURED — USA bank frozen at `reserves=30`
> 1941.12→1943.6 while fielding 4 divisions with 2.5M free manpower (owner console), the
> conscription-law chain ruled out as binding. Blocker = `WA_reserves_is_expeditionary_only`
> (overseas-only war → deploy factor 0). Fix: `num_divisions > 29` added to the veto — under 30
> divisions the reserves ARE the army and the bank opens; ENG (36-75 divisions all war) stays
> vetoed so the blessed fewer-better-divisions behaviour is untouched. Retroactive on a running
> save (the decision re-evaluates). Probe: next campaign, USA `reserves` variable drains to 0
> within 3 months of Pearl Harbor and deployed count jumps by the banked amount.
> Reviews 2026-08-27: architecture CONCERNS (header cut to rule-7 length, RAJ-bar independence
> written) + lessons CONCERNS, resolved as follows. **Drain table (USA, deploy = 10/batch,
> decision cost 5 PP / 1 day):** t0 army 4 bank 30 → t1 14/20 → t2 24/10 → t3 34/0 — the third
> deploy passes because 24 < 30, so the USA case reaches bank = 0 and the owner's "toutes" is
> met. **Residue accepted, in writing:** a bank large enough to carry the army past 29 mid-drain
> strands its remainder (max bank 100 → worst residue 70 at army 29) — that IS the
> fewer-better-divisions intent re-arming at 30+ fielded; and attrition back under 30 redeploys
> it, i.e. reserves replace losses — intended, not flap. **Micro-dump interaction closed
> (DERIVED):** recruiting a batch needs > 200k manpower AND > 15k equipment stock
> (`WA_reserves_meets_recruitment_threshold`), out of reach of a < 5-MIL country, so a banked
> create_unit dump past the 5-division cap has no realistic population.
> **Second half (106→47 gap beyond the bank) — INCOMPLETE, build delta CLEARED.** MEASURED sweep
> of `ed109de9d..2f16ec583`: zero `force_build_armies`/`ai_wanted_divisions_factor` changes; the
> defines dedup (`fc1e82a7f`) changed no effective value (all removed lines were already-dead
> earlier duplicates); template-flag renumber orphan-free; the PRODUCTION/pp commits carry no
> training lever reaching USA/CAN-but-not-GER. Top structural candidate (PRE-existing, not a
> regression): the `role_ratio` residual stack in `WA_AI_PRODUCTION_DEFAULT_army_composition.txt`
> — the two USA-only subtractor blocks (expeditionary_mechanization -30, infantry_floor) sit on
> the deepest stack, and the file's own comment records USA's infantry want going NEGATIVE and
> training stopping (campaign 9be92c89); the in-range cavalry deletion returned +5 near that
> cliff. Deciding read (owner console): `tag USA` / `tag CAN` / control `tag GER` →
> `imgui show ai-strategy`, the **role_ratio per-type tree** — USA infantry row at/below -100
> with armour rows positive confirms; positive infantry row refutes and moves the ladder to the
> truck floors. Live rival, unexcluded: campaign variance (USA at 4 in 1942.6 is six months
> after entry; `8f9b5653`'s 106 was a 1944.6 reading on the same veto).

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
- **Scope extended 2026-08-27 (owner rule): a country with FEWER than 5 military factories does not
  BUILD more than 5 divisions.** Shipped: merged with [rk-no-divisions] into the single block
  `WA_AI_PRODUCTION_DEFAULT_trains_no_divisions` (`WA_AI_PRODUCTION_DEFAULT_army_composition.txt`);
  WHO is suppressed lives in the scripted trigger `WA_AI_PRODUCTION_trains_no_divisions`
  (`scripted_triggers/WA_AI_PRODUCTION_army_composition.txt`) — RK, OR `num_of_military_factories
  < 5` + `num_divisions > 4` + `has_civil_war = no` (SCW d5d88061d precedent). Payload = the
  13-line suppression (build_army -500, role_ratio -1000 all land roles).
  Deliberately a DIFFERENT band from the fitness floor (`> 5` at `WA_AI_MILITARY_triggers.txt`):
  exactly-5 = unfit abroad but uncapped at home. Overshoot bound and decommission cycle cost in
  the block header (t0/t1, ASSUMED terms named). Reviews: lessons CONCERNS — 3 items applied
  (bound table, cycle-cost sentence, probe below); architecture CONCERNS — 2 items applied
  (registry group `expeditionary_fitness_mil_factory_floor` ties the two 5s, commit hash moved
  out of the code header). **F9 boot test OWED** (new ai_strategy block).
  Verification (cap probe): next campaign, every no-civil-war country at < 5 MILs shows deployed
  divisions <= 8 (5 + conveyor bound 3) sustained after 6 months at war — NEP (1 MIL, read 10-16
  divisions on `8f9b5653`/`24933fb9`) is the known-positive that must flatten; control: a minor
  at >= 5 MILs (ETH-class, 8) still grows past 5. Enable-evaluates-true check: NEP's trajectory
  IS the check (no strategy names in saves); the imgui fallback is `tag NEP` Active strategies.
- **Campaign `24933fb9` scored 2026-08-27 — leg (a) FAILED, but materially improved.** MEASURED
  (`plans.py NEP --where`, closure test passed 10/6/12 = army deployed): 1941.6 **6 of 10 NEP
  divisions in Egypt/Libya** (Cyrenaica 4 front, Derna 1 front, Alexandria 1 NO_ORDER); 1943.6
  4 of 6 outside Nepal but only Persia/Rajahsthan buffers (Africa GONE); 1944.6 **12 of 12 home**.
  DERIVED: the 2026-08-25 gating of the two Allies pulls moved the steady state (previous campaign:
  whole army in Africa through 1944.6) but the 1941.6 window still violates "never" — consistent
  with the H2 under-sized -100 diagnosis and the untouched buffer layer (H3). BHU void (observer).

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
- **Campaign `24933fb9` scored 2026-08-27 — probe (a1) PASSED (first time), probe (a2) TRIPS at
  1943.6, and the theatre outcome still inverts after Torch.** MEASURED (`plans.py ENG,RAJ --where`,
  closure passed): RAJ in East Africa **11 / 13 / 17** at 1940.12/1941.6/1941.12 (bar >= 8 cleared
  with margin), ENG EA+Sudan vs Egypt **2/10, 3/4, 2/2** — never inverts while the delegate lives.
  The handoff itself is working. **(a2) fires**: at 1943.6 RAJ has **3** in East Africa on 76 total
  divisions (34 on the Burma wall) while `num_divisions > 29` reads "available" — the recorded
  total-vs-in-theatre conflation, now MEASURED; ENG back-fills with 14 (handoff inverted, ENG 14 EA
  vs 8 Egypt). **El Alamein: the known post-Japan gap became the campaign's Western headline.**
  MEASURED timeline: Torch 1942.11 takes Algeria only; GER seizes Tunisia (Case Anton 1942.11.17);
  state 452 breaks 1943.1, fully ITA 1943.2; Cairo ITA 1943.5; Suez 1943.7. At the flip (1943.2)
  ENG has **4 divisions on Allied ground in all Egypt, 0 in Cairo** (53 worldwide, ~1 div/state),
  Axis 55 in North Africa. RAJ's El-Alamein reinforcement is structurally OFF (Japan at war since
  1941.12) — exactly the "reinforcement verdict that cannot fire once Japan is in the war" gap
  recorded above. The Tunisia land front then stalls for 3 years (ENG 14-div army group vs GER 27
  divisions; Tunis German at 1945.11); the naval-invasion half of the answer is the
  foothold-deadlock diagnosis in the campaign header block.
- **`[raj-gulf-garrisons]` probe (SS26) scored on `24933fb9` — FAILED.** MEASURED: Aden PASSES the
  JAP-neutral window (RAJ 1 in 659 at 1940.12/1941.6/1941.12, ENG 0); Kuwait standing watch FAILS
  (RAJ in 656 only 1 of 3 neutral saves, empty from 1941.6); **both delegations collapse from 1942
  on** — RAJ 0/0 in every later save while ENG stands both guards itself (1-2 div, consistent with
  the 0.02 floor). Caveat: the 083a45c33 delegate_force_floor amendment IS in this build, so the
  failure is not the old army_still_operational bar; next discriminator is the owner's imgui read
  of the three RAJ Gulf verdicts vs RAJ's areadef park.
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

### lend-lease-observability — SHIPPED-UNTESTED (2026-08-27)
- Scope: owner request 2026-08-27 ("un outil spécial lend-lease : image complète des donneurs,
  receveurs, matériels envoyés, voie vanille (maritime) ou scriptée (terrestre)"). Two halves:
  a savegame extraction tool, and the telemetry closing the one hole a save cannot answer — the
  scripted channel's donor→recipient split (llr_sent_* is donor-side only, no receiver dimension).
- State: shipped 2026-08-27 (this session; slot freed by parking `fra-battle-of-france`, owner
  choice). (i) `lendlease.py` (`.claude/skills/wa-savegame-analysis/scripts/`) — three tables it
  never conflates: VANILLA per-pair cumulative IC/fuel ledger (`lend_lease_to_allies_history`,
  giver rows, receiver mirror reconciled, live `lend_lease={first=}` relations + start dates,
  `recently_leased_ic`), SCRIPTED donor per-archetype (`llr_sent_*`, rows 1–9 overland + 10
  convoy), SCRIPTED recipient pair matrix (`llr_recv_*`, v32+, donor ids scope-decoded; pre-v32
  saves say "not recoverable" instead of guessing), plus counters and decoded
  `wa_ai_lend_lease_targets`. Multi-save = date-ordered `d/save` deltas (cumulative → flow).
  MEASURED on `24933fb9`: 114 vanilla pairs at 1944.6, CAN→SOV +6 506 IC over 1944.6→7, decode
  yields clean 3-letter tags (validates the country-ref encoding on a real save). (ii) WA_TLM v32
  `WA_TLM_llr_recv_donor/_n/_amount` parallel pair arrays on the RECIPIENT, written in
  `WA_AI_LEND_LEASE_relief_record`'s verified-send branch (all legs incl. convoy row 10); break
  hygiene + `_llr_pair_idx` init; deliberately no zero-init (absence = never received;
  witnesses `llr_starving_n`/`llr_first_t` named at the init site). Doc §6e row added.
- Reviews 2026-08-27: architecture CONCERNS (2 items — `lendlease.py` had to exist: written;
  witness clause: applied) + lessons CONCERNS (4 items — break hygiene: applied; slot-temp init:
  already present; save-side decode: verified on a real save via `wa_ai_lend_lease_targets`;
  SHIPPED-UNTESTED process: this heading).
- Known limits, stated: the VANILLA channel's per-equipment split is not serialised by the engine
  (unrecoverable from any save); convoy losses en route invisible; `llr_recv_amount` sums units
  across archetypes (magnitude — the per-archetype split stays donor-side); recipient arrays
  freeze on annihilation / civil-war tag flips (write-only telemetry, decoded save-side).
- Verification: owner console harness — `event wa_test.301` on a donor with a starving recipient
  (existing LLR harness; `relief_record` now also appends the recv arrays), save, then
  `lendlease.py <save> --tag <recipient>` shows the pair row. Campaign probe: first v32 campaign,
  per-recipient `llr_recv_amount` totals reconcile with the donor-side `llr_sent_amount` deltas
  (global closure, donor vs recipient side).
- Closed when: the harness output is pasted here AND a v32 campaign shows the recipient matrix
  populated with donor/recipient closure holding — the full donor→receiver→materiel→channel
  picture readable from one tool call.

### aoi-border-garrison — OPEN (2026-08-27)
- Scope: owner request 2026-08-27: at Italy's war entry the AOI garrison must hold the colony's
  BORDER defensively instead of standing on the ports. The Fix 97 intent stays: no offensive into
  Sudan/Kenya, no mainland reinforcement of the AOI.
- Symptom (MEASURED, campaign `15176ce6` BHU, saves 1940.9/1940.10): ITA 9/9 AOI divisions inside
  the `put_unit_buffers` order pinned to {550,559}; ZERO front orders in East Africa for ITA **and**
  for ITS (the owning tag, engine garrisons only); Oromia/Somali/Amhara lost in two months; British
  Somaliland never attacked.
- State: shipped 2026-08-27. (i) `AXIS_abandon_east_africa_FRONT` -100 retargeted to
  `corridor_regions` {380,381} + `strategic_region = 217` — region 17 exempt for the whole family.
  (ii) `AXIS_abandon_east_africa_THEATRE` -200 retargeted to `corridor_regions`; new twin
  `_colony_THEATRE` -200 on `colony_regions` {17} gated `NOT owns_east_africa_colony` (new tag-free
  trigger, self/subject only — allies keep the brake, the owner-defender ITA/ITS/RIT is exempt; no
  counter-bid, per the 2026-08-25 ruling). (iii) ITA garrison buffer `states` widened to
  {550,559,271,909,910} (all five verified in region 17 against map/strategicregions). Shared
  family gate extracted verbatim to `WA_AI_MILITARY_AXIS_abandon_east_africa_family_gate` (4
  readers incl. DIPLOMACY, unchanged behaviour). Doc §12 updated. Reviews 2026-08-27: architecture
  CONFLICT on the v2 counter-bid (replaced by the enable exemption) + lessons CONCERNS (buffer
  divisions pinned — answered by (iii)); required items applied.
- ASSUMED, stated: engine attribution of the AOI border front to region 17 (R62 risk — if it
  attributes to the enemy-side region, (i) is inert and behaviour falls back to today's); front
  orders in region 17 drawing on the buffer (`area` = {17} permits it, never observed); 217 keeps
  only its FRONT brake (area_priority cannot address a bare strategic region).
- Verification: F9 boot test owed (ai_strategy block add). Owner `imgui show ai-strategy` on ITA
  and ITS in a 1940 war save: corridor -100 + s.r. 217 -100 listed, NO -100/-200 entry covering
  region 17 for the owner-defender, `_colony_THEATRE` listed for GER. §12's East-Africa telemetry
  was retired with R62 — re-instrument (WA_TLM) before the next campaign scores this theatre.
- Closed when: a campaign save at Italy-at-war shows (a) >= half the AOI divisions in border states
  (271/909/910/550) rather than all in 559/550 port stacks, (b) a front order in East Africa for
  the AOI holder (ITA or ITS), (c) zero ITA/ITS divisions in 217/380/381 states (Sudan/Kenya), and
  (d) control: GER holds no divisions in the AOI.
- **Campaign `24933fb9` scored 2026-08-27 — fix LIVE and the colony holds 37 months (vs 2 pre-fix);
  (b) PASS, (d) PASS, (c) marginal FAIL, (a) FAIL as written / PASS on the buffer population.**
  MEASURED: ITS never existed this run (no `units` at 1936.2 — never released; owner symptom "slow
  to kill ITS" is about ITA's own colony). Fingerprint: ITA's buffer army occupies ALL FIVE states
  {550,559,271,909,910} at 1940.9→1942.6 — impossible under the old 2-state list. (a): all-division
  border share 20-55 % (port stacks are naval-invasion STAGING, a different order class — probe
  measures the wrong population; buffer-only share 43-57 %). (b): East-Africa front orders manned
  (inst 190 + the 298/297 Sudan corridor, 3-4 div). (c): 1-2 stray divisions in Kenya/Sudan most
  saves, worst a **buffer-class division in Kurdufan 1942.6** — a garrison outside its own state
  list, unexplained leak from order 9607. (d): zero GER divisions in the AOI at all four dates.
  **The "slow kill" is Allied under-commitment, not garrison strength**: Allies in region 17 =
  4-6 div (RAJ only) for 18 months, parity (1.13:1) reached only in 1943 against 11-23 ITA — the
  lever is Allied theatre sizing, outside this subject.

### rail-corridors — SHIPPED-UNTESTED (2026-08-27)
- Scope: owner request 2026-08-27 ("éviter que les IA passent trop de temps en transit maritime").
  A declared CHEAT, no gameplay-economy intent: once every state along a land corridor is held by
  one side (faction + subjects), a level-5 railway is spawned instantly and free between the
  endpoint cities so strategic redeployment prefers land over convoys. 8 corridors:
  Dakar-Djibouti (Sahel), Pretoria-Khartoum (east-African line), Prayagraj-Karachi, Karachi-Fars
  (prov 10797), Kuwait-Baghdad, Baghdad-Cairo, Casablanca-Cairo (gated on ALL of North Africa,
  owner rule), Miami-Halifax (eastern seaboard).
- State: shipped 2026-08-27. Dispatch `WA_AI_RAIL_CORRIDOR_monthly_tick`
  (`WA_AI_RAIL_CORRIDOR_effects.txt`, once-per-month global claim via timed flag, retired for good
  once all 8 built), same-side predicate (`WA_AI_RAIL_CORRIDOR_triggers.txt`), GENERATED gates +
  builds (`WA_AI_RAIL_CORRIDOR_data.txt`, tool `tools/gen_rail_corridors.py` — BFS on the
  WA_AI_MAP land adjacency with waypoint anchors; plain BFS was measured cutting through the deep
  Sahara, hence the waypoints), harness `WA_TEST_rail_corridors.txt` +
  `events/wa_test_rail_corridors.txt` (report `wa_test_rail.1`, force-builds `.11`-`.18`).
  Monthly call added in `WA_AI_misc_on_actions.txt`.
- ASSUMED, stated: (i) `build_railway` over an existing line RAISES it and clamps at
  MAX_RAILWAY_LEVEL 5 instead of stacking or laying a parallel line — unobservable in script, the
  force-build events are the visual check; (ii) the engine's build path between two anchors matches
  the generator's BFS chain only approximately — a deviation can lay track through a state the gate
  never checked (bounded by the waypoint spacing); (iii) trigger-AND short-circuits left to right.
- Verification: owner console run owed — `event wa_test_rail.1` (report pasted here), then one
  force-build (`event wa_test_rail.11`) on a throwaway save with the supply mapmode open: existing
  rails upgraded not duplicated, level caps at 5. F9 boot test owed (new on_action call + 2 new
  scripted_effects files + 1 trigger file + 1 event file).
- Closed when: a campaign save shows (a) at least one corridor's global flag
  (`WA_rail_corridor_<i>_built`) set with the railway present on the map at level 5, (b) the flag
  only set while the corridor's gate states were same-side at some prior month, and (c) no
  corridor built while its corridor was split between factions (control: flags all absent in an
  early-1936 save).

## PARKED

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
| `fra-battle-of-france` | OPEN, fix shipped 2026-08-27, parked 2026-08-27 (WIP limit, owner choice — slot given to `lend-lease-observability`). Shipped: `FRA_homeland_invaded_recall_colonials_THEATRE` (area_priority -90 NA/med/middle_east, gated `home_threatened`), Alpine pair `FRA_alpine_front_FRONT`/`_THEATRE` (+100 south_france, gated `any_enemy_country = is_italian_homeland_power`), `FRA_defense_of_the_colonies_FRONT` re-armed to -5000 release, no-op `FRA_ignore_garrisons_until_invasion_start` deleted; spec SS25; reviews applied; F9 boot OK. Campaign `24933fb9` NOT CHECKED — `surrender_progress` not serialised and the gate window falls between monthly saves (ITA declares 1940.6.11, FRA dead by 1940.7.1); symptom near-vacuous this run (FRA 3/121 div in NA+Corsica). ASSUMED stated: garrison -5000 release semantics; colonial channel of the ~20 div | Owner report (ironman `feedback_save`, so owner figure not save-MEASURED): FRA garrisons North Africa/Corsica (~20 div) during the Battle of France while the Italian border sits open | A non-ironman Battle-of-France save (mid-June, or the console harness) shows (a) FRA NA+Corsica division count falling once `surrender_progress > 0.05`, (b) >= 2 FRA divisions on the south_france fronts while an Italian homeland power is an enemy, (c) Maginot/fall_rot nets unchanged |
| `rk-no-divisions` | SHIPPED 2026-08-27 (`1652af012`), parked (WIP limit). **Campaign `24933fb9` PASSED**: 7 of 8 `autonomy_reichskommissariat` tags (RBA/RBE/RGR/RHO/RNO/RPO/RSE) at ZERO divisions on every save, ALB flat at its 3 scripted starters, no count ever rises; ITS-control leg vacuous (ITS never released). F9 boot + error.log id check still OWED | Old brake value -1, war-gated, infantry-id only, tag list missing ITA's 8 RK tags and ENG conversions — RK tags train divisions (MEASURED in code) | F9 boot + error.log id check pass; a campaign shows every `autonomy_reichskommissariat` country (ITS excepted) with zero divisions in training and a non-rising division count (scripted grants aside); control: ITS still fields/trains its colonial divisions. Full record: git log `[rk-no-divisions]` + this file's history |
| `allied-total-commitment` | TESTED, parked 2026-08-27 (WIP limit; F9 boot test for the CAN reserve-batch reward still OWED). Campaign `24933fb9`: the batch FIRED and DEPLOYED (MEASURED: 10 `Reserve Divisíon` at 1939.11) but was consumed on a front by 1942 and CAN never rebuilds (2-4 div 1941-44 on 104 arms factories — separate defect, candidate subject); leg (a) still FAIL through 1943 (100% home areadef at 1943.6), half the army abroad by 1945.6. Amended same day (owner orders, two rounds): (1) the one-shot closes the reserve program after its batch — `WA_reserves_unlock_template` + `reserves_deployment_complete_flag` applied directly (NOT a bank flush; owner refused deploying more) so the template becomes modifiable; (2) a READY batch (bank >= 10) is spent like a normal activation — the +10 grant fires only on an empty/short bank, so no residual bank remains when the country had recruited its own. Fresh campaigns only (a save past the focus keeps its locked template). Reviews: architecture OK, lessons CONCERNS — retroactivity stated here, no `break` writes in the deploy path (MEASURED), refill impossible pre-unlock (`WA_reserves_can_recruit` needs `has_war = no`, the focus needs `has_war = yes`) | CAN 4-9 div, 100% areadef home garrison (`8f9b5653`); release trigger PROVEN on CAN (wa_tc.1 harness 1942.2, closure PASS). **Owner imgui 2026-08-27 (MEASURED): CAN garrison tree = ONE summed entry, Weighted Value -4950 (-5000 release + 50 minors_home_first) — armed, held, and SUMMED (first direct proof same-type/same-target entries sum) — yet the home engine areadef divisions do not move: a negative `garrison` does NOT empty existing engine area-defense orders; the buffer is the proven mover (Scotland div, 1942.3).** Shipped same day (owner order "zéro division au mainland"): `protect_home_floor` gated off under `total_commitment_active` (threatened +200 tier keeps its own gate), new `CAN_THEATRE_total_commitment_empty_mainland` buffer ratio 0.75 (sums with defend_britain 0.25 to 1.0, per-order summing ASSUMED) on the britain states, `subtract_fronts_from_need` so front divisions stay abroad. Reviews: architecture CONCERNS (SS23 consumer rows + summing relabelled) + lessons CONCERNS (all applied: 0.75 re-sized as its own order — the ratio-pool arithmetic is lessons-REFUTED, each block is a separate order and >1.0 arbitration UNKNOWN; buffer→continental-front feed labelled ASSUMED, USA unit_buffer_for_europe pattern; no new ai_area alias, area=britain reused, cap-72 item void). **Landing-residual t0/t1/t2, stated:** t0 enemy lands on a Canadian core → `home_theatre_threatened` trips at the enemy-on-core term; t1 next engine strategy re-evaluation (ASSUMED sub-weekly, SS23 cadence limit) — commitment flips off, buffer disarms, threatened +200 arms; t2 transatlantic return crossing ~2-4 weeks; worst case ~3-5 weeks of thin mainland, and front-engaged divisions in Europe return slower still — ACCEPTED, it is the owner's zero-mainland order. defend_britain 0.25 armed for CAN is MEASURED (the 1942.3 Lanark order, states byte-equal); both-blocks-together is only observable next campaign. F9 boot owed. Probe: next campaign, zero CAN divisions in Canadian states while committed and home safe (vs 2-3 in `24933fb9`), AND CAN divisions appearing on continental fronts (tests the buffer feed) | Campaign legs: (a) CAN majority front/buffer outside North America while home safe; (b) AST/NZL/RAJ areadef ~0 while Pacific quiet AND re-garrisoned within 3 months of `pacific_threat_imminent`; (c) dominions on African fronts once past the 6-factory floor; (d) control: a non-faction minor at war keeps its home garrison; plus SS24 bulwark-guest probe (zero Commonwealth div on FRA soil while FRA holds `disjointed_government`, historical difficulty). Full record: git log of this file + [allied-total-commitment] commits |
| `scripted-invasion-reservation` | OPEN, parked 2026-08-27 (owner order; console harness legs A-C PASSED 2026-08-23, leg (b) NOT CHECKED on `8f9b5653` - the Allied AI never wanted a French landing, so the mechanism never ran) | Halab 1944.6: USA order 252 holds 9 divisions on a GER-held, GER-flagged reserved target - H1 (@FROM inert in ai_strategy context) vs H2 (-200 outbid on a pre-existing order) undecidable from the save | A campaign in which the Allied AI wants a reserved beach shows no engine invasion order against it; or an ai_strategy-context harness leg proves @FROM renders. Full record: git log of this file + [scripted-invasion-reservation] commits |
| `uk-truck-supply` | SHIPPED 2026-08-27, boot OK. **Campaign `24933fb9` PASSED on the stock leg**: ENG motorized stock 8k-19.6k in every war save (5-13x the 1500 floor), the deficit pathology absent. Criterion correction: ENG is on the >49-factory band from ~1937 (117-330 arms factories), never the 30-49 tier the criterion names; the live lever is `min_wanted_supply_trucks = 2000`. Africa hub-motorization leg NOT CHECKED. Probe defect: the `var` probe is void — both levers are trigger literals/ai_strategy, probe with `stock.py --all --match motorized` + `buildings --match arms_factory` | Owner: ENG truck deficit every game, Africa supply fulfillment < 50%. MEASURED in code: demand multiplied (hub cost 60->500, motorize ratio 0.95, buffer 1.2) while ENG (36 arms factories) sat on the 3-factory tier with a 1000-stock cutoff | A campaign shows ENG on the 6-factory tier with motorized stock >= 1500 sustained at war, and Africa hub motorization no longer truck-starved. Shipped: stock bar 1500 = lend-lease starve (registry truck_stock_starve_floor), 30-49-factory tier at 6, min_wanted_supply_trucks 2000/1000 (vanilla precedent SIA). Successor of the raj-trucks SAF-tier residual |
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
| `prospecting-coop-solvency` | SHIPPED 2026-08-27, parked same day (WIP limit; F9 boot test OWED) | Owner request: coop prospecting must check the needy ally can IMPORT. GER 1945.7 (`15176ce6`) re-prospects coal on 20 164 effective; sole weight = coop branch; ITA at -1046 imports 0 with 0 civs avail. Shipped: ally-side gate in all 9 `WA_AI_allies_need_<r>` (avail>0 OR `resource_imported@<r>` > 0 — the import leg answers the lessons CONFLICT on saturation collapse). Sweep on the save: 206 needs=3 rows, 176 PASS / 24 live BLOCK, every BLOCK imports 0. ASSUMED: trade preempts construction, so a solvent wanting ally already imports; if solvent-at-0-imports exists (WA-native trade AI incomplete), gate over-blocks | F9 boot passes; a post-fix campaign shows supplier prospecting counters flat while a member sits at needs=3 / 0 avail / 0 imports, AND still growing for an importing member (HUN-like); no report of a buying ally starved |
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
