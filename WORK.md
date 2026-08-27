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
> **[reserve-quality] v2 shipped 2026-08-27 (owner rulings, USA fork save 1944.6.20):** the flat
> division bar replaced by a capability gate — the bank exists to bootstrap a small army into a
> training snowball (USA/CAN); it stays shut when materiel is the limiting factor: MIL tiers
> (≤24 MILs closes above 20 div, ≤49 above 40, ≤99 above 80, 100+ never size-vetoed) OR new
> `WA_AI_CONFIG_is_reserve_materiel_limited` (ENG — owner chose "ENG reste fermé" over pure
> capability: its MILs build air/sea, no land stocks at war entry). Calibration MEASURED at war
> entries (24933fb9): RAJ 1939.10 22 MIL/50 div → closed; CAN 15/14 → open (snowball case); ENG
> 134/31 → closed by archetype; GER 243/107 → open (veto moot, home neighbour at war); USA 1942.1
> 340/7 → open; RAJ 1942.1 91/48 → open (industry grew into its army). Stock gating measured and
> REJECTED: RAJ holds 53k infantry eq at entry (licences) while CAN holds 11.6k yet must open —
> stock separates neither pair. Trigger symptom: USA fork 1944.6.20 `reserves=30` frozen at 59
> divisions — vetoed by the flat bar (owner commit 40b656379 lowering 29→20 tightened the veto
> further and strands 10 even in the drain case; superseded by the tiers). Probes: USA drains to
> 0 next campaign; ENG bank (40 at 1944.6) never drains while its war is overseas-only; a ≤24-MIL
> country at 40+ divisions never drains.
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

### allied-division-stability — OPEN (2026-08-27)
- Scope: owner request 2026-08-27: Allied divisions are permanently in transit between fronts
  (cross-theatre shuffling). Rails and naval corridors already cut transit COST; this subject cuts
  transit FREQUENCY. Step A (this ship) = engine theatre-distributor damping, defines only.
  Step B (hysteresis pass on the script oscillators: `home_threatened`, `total_commitment`,
  USA britain buffer, handoff ladders, AIFC dwell) is a separate owner decision, not shipped.
- Symptom (owner-reported, not yet measured in a save). Analysis 2026-08-27 (session scratchpad
  `allied-division-stability-analysis.md`; three-agent sweep): MEASURED — the engine's own comment
  on `NAITheatre.AI_THEATRE_DISTRIBUTION_MAX_PERCENT_UNMET_DEMAND_PER_FRONT` (vanilla 0.5) names
  it the unit-shuffle control ("0 means once a front gets hold of a unit it stays there forever");
  neither WA nor Expert AI 5.0 overrides it or any NAITheatre key. MEASURED — no Allied ground
  block (`front_unit_request`/`area_priority`/`put_unit_buffers`/`garrison`) has an enter/exit
  hysteresis pair; top oscillators ranked in the analysis file.
- State: shipped 2026-08-27, `05_defines.lua`: `AI_THEATRE_DISTRIBUTION_MAX_PERCENT_UNMET_DEMAND_PER_FRONT`
  0.5→0.2, `AI_THEATRE_DISTRIBUTION_SAME_THEATRE_SCORE_MODIFIER` 0.25→0.5,
  `NAI.REASSIGN_TO_ANOTHER_FRONT_FACTOR` 0.5→0.3. `FRONT_MIN_PATH_TO_REDEPLOY = 3` deliberately
  untouched (separate decision — it trades walking for rail transit, which the rail corridors
  serve). Change is global (all nations): a levelling, not an Allied buff.
- ASSUMED, stated: the SEMANTICS of all three defines rest on their engine comments alone
  (lessons ruling: author prose is not a spec) — direction plausible, magnitude unknown, neither
  save-measured; that the Allies benefit most because their fronts span theatres while Axis
  fronts are contiguous; the engine strategy re-evaluation cadence (still untimed). MEASURED:
  vanilla baselines 0.5 / 0.25 / 0.5 verified against the install's `00_defines.lua`
  (:4436/:4433/:3055, 1.19.2) this session; no prior WA or Expert AI override of any of them.
- Verification: F9 boot test owed (defines change). Campaign probes, BOTH required:
  (i) transit share = fraction of ENG+USA divisions whose theatre/state changed between
  consecutive monthly saves (order-disappearance signature per lessons; exclude divisions located
  on enemy-controlled ground; GER as contiguous-front control), compared to the PRE-fix baseline
  MEASURED 2026-08-27 on `24933fb9` (8 saves, per-save counts closed against `savegame.py army`
  exactly): in-transit snapshot (at-sea + hostile-ground / deployed) ENG 13-45%, USA 14-55%,
  GER 0-1% at every save; ENG 1944 worst case 9 divisions in transit across 4 consecutive saves.
  Trap, MEASURED: raw month-over-month state-change does NOT discriminate (GER front-combat churn
  26-67%) — score the SNAPSHOT and rear-class churn (GER buffer 2-19% vs ENG/USA areadef
  25-100%), never raw movement. Hostile-ground is an upper-bound bracket (22 ENG front divisions
  sat 4 months on ITA-held Cairo provinces — stamping vs stuck combat unresolved in a save).
  Extractor: plans.scan + savegame.py division iterators (rebuildable from this description);
  (ii) starvation probe: manning of fronts/invasion orders CREATED after the change (new
  beachheads, new war fronts) — a front born unmanned while idle divisions sit in a quiet
  theatre fails this subject even if (i) improves.
- Closed when: (a) ENG+USA transit share drops vs the pre-fix baseline at matched dates, (b) no
  starvation regression — no active front under-manned while idle divisions sit in a quiet
  theatre (F-items unaffected), (c) owner confirms the in-game impression improved.

### aifc-traction — TESTED (2026-08-27)
- **Owner console run 1944.7.14 post-full-restart (`wa_aifc.1 ENG`) — gate constant loaded and
  computing, subject back to TESTED.** Pasted evidence: `native-maxpad=3
  exp-gate(native-maxpad<=2)=0` — the bar prints 2 (constant resolved; the 1944.7.7 run had
  caught it at 0 after a console `reload`, which reloads effects but NOT script_constants —
  the constants-file header's full-restart rule, now demonstrated in an instrument reading).
  The closed arm is CORRECT here, not a failure of the expectation written earlier: the fork's
  war moved — ENG now holds pad-3 native candidates in Egypt (Qattara/Beheira/Dakahlia/Suez),
  a real native front, so skipping the ally walk is the design working. Stored sector 680
  age 4wk = forced re-selection next tick, onto an Egypt pad-3 anchor vs ITA (the main-enemy
  rule picks ITA at max pad 3 with or without the merge this week). **Open-arm end-to-end proof
  still riding**: the run arm (weak native → merged candidate in a STORED sector) is proven at
  the instrument level (harness walk) but not yet in a shipped selection. `wa_aifc.1 ITA`
  1944.7.14 (owner): native-maxpad **5** (Cairo — the fork's Egyptian battle massed ITA
  divisions too) → gate closed CORRECTLY; no tag in this fork still combines a weak native
  front with real ally-soil mass (USA has neither), so the open arm's end-to-end proof rides
  on the next campaign — probe (L3d): a country whose native max pad reads <= 2 while holding
  3+ divisions on ally soil shows expeditionary states in its STORED corridor (aifc.py). Both
  stored sectors re-select next tick at age 4 onto their max-pad anchors (ENG → Egypt vs ITA,
  ITA → Cairo vs ENG) — the Egyptian front becomes schwerpunkt vs schwerpunkt, the intended
  shape of the system.
- **Expeditionary gate fix SHIPPED 2026-08-27 (owner order).** The 1b gate is now
  CAPABILITY-based: new `constant:wa_ai_aifc.selection.exp_gate_pad = 2`; a prepass computes the
  best NATIVE pad and the ally walk runs unless some native pad clears the bar (strict >, i.e.
  skips at pad >= 3). The count arm (`< 3`) deleted whole — empty native set reads best pad 0, so
  the 5709c8b9 token-island and empty cases stay covered. Pad band thresholds declared ONCE as
  file-scoped `@AIFC_PAD_T1/T2/T3` read by both the prepass and the 1c walk (must-match by
  mechanism, not comment); harness re-types them deliberately (independent instrument, contract
  rule 4) and now prints the NEW gate (`native-maxpad` vs bar). Docs synced: FRONT_aifc.txt
  system header, 1b comment rewritten (cost sentence honest: an eligible country with only weak
  native pads pays the ally walk weekly — bounded by its allies' controlled-state count, and it
  is exactly the country the merge exists for; a small-army faction minor below 12 divisions
  never reaches selection at all — the FIX-56 eligibility gate is upstream). Validity mirror
  needs no change (core:191-201 expeditionary arm ungated — FIX-65 lockstep holds).
  Reviews 2026-08-27: architecture CONCERNS (4 items: header sync, @ bands, cost sentence,
  checkers — all applied) + lessons CONCERNS (5 items: prepass init `= 0` present, minor-class
  cost stated here, @ bands, rule-10 gate header sentence in the constant + 1b comment,
  check_constants — all applied). Flap statement (structural, no timeline owed per lessons):
  the gate only ADDS candidates; worst case of a native pad wobbling across the bar is today's
  native-only selection, never worse.
- **Owner console run owed (moves this back to TESTED): re-run `event wa_aifc.1 ENG` on the
  fork.** Expected: `exp-gate(native-maxpad<=2)=1` and, after the next weekly tick, a stored
  sector anchored on Tunisia or a Normandy state vs GER — the shipped selection finally seeing
  the merged candidates. F9 boot: the game loading this build with the harness firing covers it.
- **Owner harness run 2026-08-27 (`event wa_aifc.2`, save 1944.4, all scope headers `1 1 1 1 0`)
  — L2 diagnosis COMPLETE, floor SAVE-PROVEN live, F9 boot OK (the build loaded and the new
  constant resolved in-game).** Key pasted lines:
  `USA: elig all green (shipped trigger reads 1, div=42) | cand_native=0 cand_total=0
  ally-states-with-3+div=0 max_pad=0 | NO sector` — **the six-box for L2**: eligibility passes;
  candidate collection returns ZERO because USA borders no enemy natively AND not one allied
  state on the map holds 3 US divisions (helpers:135 `divisions_in_state > 2` — working as
  designed on a real absence). The cause is UPSTREAM of AIFC: 42 divisions worldwide at 1944.4,
  none massed abroad — the allied-invasion-foothold-deadlock (six-boxed in the campaign header)
  plus the USA army-building gap own it. **Proposed ruling: no AIFC fix for L2 — lowering the
  3-division bar would aim a schwerpunkt nobody can execute. Owner acceptance closes L2.**
  Floor mechanics MEASURED live: `ENG Cairo pad=1 anchor-eligible=0`, `GER Constantine pad=1
  anchor-eligible=0` — pad-1 candidates excluded exactly as designed; FRA control case correct
  (capitulated, 7 div → shipped trigger 0, no sector). **Mass-alignment bonus reading (feeds
  L1)**: GER stored anchor 193 Chernigov = its max-pad candidate (pad 9/13 eligible), SOV anchor
  203 Cherkasy = max-pad 11 — at this date the anchor SITS on the mass; and ENG's main enemy
  now reads GER (Tunisia pad 3 > desert pad 2), so the next re-selection moves its schwerpunkt
  off the 24-month desert pointer onto the front where its divisions stand — the L3 unpinning,
  observable in-game. Full log in the session transcript; `wa_aifc.1 <TAG>` re-runs any tag.
- **Fork run 1944.4 → 1944.5.30 on the floor build (owner, `wa_aifc.2`, 2026-08-27) — the floor's
  live behaviour over ~2 re-selection cycles, MEASURED:**
  (i) **ITA UNPINNED**: anchor moved 456 Upper Egypt (pad 1, now floor-blocked) → 676 Ninawa
  (pad 2, eligible) vs ENG — the floor visibly moved an anchor off a pad-1 state.
  (ii) **ENG mid-unpin**: stored sector still 552 Western Desert vs ITA (age 2wk, a ~May-16
  decision) while TODAY's landscape reads desert pad 1 = floor-blocked, sole eligible = Tunisia
  pad 3, main enemy GER. Prediction, testable in ~2-3 game-weeks (age > 4 forces re-selection):
  the desert anchor cannot survive it — re-run `wa_aifc.1 ENG` then; if 552 persists past
  mid-June with pad 1, that is a floor bypass to diagnose. ASSUMED: whether the May-16 selection
  saw desert pad ≥ 2 (legitimate) — pads move with divisions, not decidable from this log.
  (iii) **GER/SOV/CHI stable AND on-mass**: anchors 193/203/593 unchanged across cycles, each on
  its max-pad candidate (9/9/9) — re-selection now converges instead of hopping.
  (iv) **The residual L1 churn shape, isolated**: JAP sector vs PRC while its max pad reads CHI;
  PRC hopped 936 Henan/JAP → 746/Mengjiang (age 1wk) — hopping continues exactly where several
  enemies hold NEAR-EQUAL pads (6-7). DERIVED: L1's remaining lever is not mass-awareness (done)
  but INCUMBENCY — the current anchor has no defender's bonus, so a 1-band pad wobble flips the
  main enemy. That is the "AIFC dwell" hysteresis `allied-division-stability` Step B names;
  design decision (margin size, keep-while-valid vs score bonus) is the owner's, not shipped.
  (v) USA unchanged (0 candidates, 0 ally states with 3+ of its 44 divisions) — consistent with
  the L2 no-fix ruling; FRA control still correctly gated.
- **Fork reading 1944.6.20 (owner, `wa_aifc.1 ENG`) — desert prediction VALIDATED, and the
  re-selection exposes the residual L3 defect: the expeditionary gate starves ENG of its real
  candidates.** MEASURED: stored sector re-selected ~June 13 to anchor 680 Deir-az-Zur (pad 2)
  vs ITA — the 552 desert anchor is dead as predicted (pad 1 < floor). But the harness's
  unconditional walk shows the real landscape: Tunisia pad 3 (GER) and FIVE post-D-Day French
  states with ENG divisions (Centre/Ile-de-France pad 2 eligible), ally-states-with-3+div = 5.
  **Six-box**: the shipped selection saw NONE of them — `cand_native = 5 ≥ 3` closes the
  expeditionary gate (`WA_AI_AIFC_helpers.txt:119`, `_aifc_cand^num < 3`), so the walk that
  would add Tunisia and Normandy never ran; among the 5 native Middle-East candidates the best
  floor-eligible pad is Deir-az-Zur 2 → main enemy ITA, anchor Syria — a WEEK AFTER D-Day.
  Same failure shape the gate's own comment records (token native contact suppressing the
  fallback; relaxed from "0" to "< 3" — 5 token contacts still starve it). Engine boundary:
  none — pure script gate. **Candidate lever (owner decision): make the gate capability-based,
  not count-based — run the expeditionary merge when the best NATIVE pad is weak (e.g. no
  native candidate above min_pad + 1), so ENG (best native 2) merges Tunisia/Normandy while
  GER/SOV (native pads 9) keep skipping the walk (the FIX-56 CPU concern stays covered).**
  Harness note: its `main enemy` line is computed over ALL candidates (walk unconditional)
  while the shipped selection sees native-only when the gate closes — that display divergence
  is exactly the instrument doing its job, but read it knowingly.
- Scope: owner request 2026-08-27 ("diagnostic masse qui ne suit pas + USA + ENG bloqué dans le
  désert"), from the AIFC passivity measurement (campaign `24933fb9`, quarterly sweep
  1939.9→1945.10, 3 extraction passes; full tables in the session scratchpad
  `aifc_passivity_measurement_24933fb9.md`, delivered to owner). Intended behaviour: the AIFC
  schwerpunkt has operational TRACTION — the sector points at ground the country can attack with
  mass, and the mass is there. Three legs: (L1) the mass does not follow the anchor, (L2) USA
  never gets a sector, (L3) ENG pinned 24 months on an unreachable corridor.
- Symptom (MEASURED, `24933fb9`): corridor capture at t+6mo productive in ~1/3 of 11 snapshots —
  2 objective captures of 22, 3 total stalls (SOV 1942.1 and ENG 1943.1/1944.1 byte-identical
  province split six months later), 2 net reverses (GER 1943.10, 1944.7). (L1) GER 1942.7:
  8/259 divisions (3.1 %) in the named corridor (Novgorod anchor) — the real mass (84 div, 32 %)
  sits at Bryansk/Sumy/Roslavl, the PREVIOUS anchor; GER anchor churn 87 % of quarterly
  transitions, 17 distinct anchors, vs `constant:wa_ai_aifc.sector.max_age = 4` weekly
  re-evaluation. (L2) USA: 0 sectors in 47 war months while its offensive-bonus conditions hold
  88 % of war quarters; armour book installed/retired 7× (only churning tag, r67), never caught
  live on 25 snapshots; its sole surviving `front_armor_score` signal is a stale +400 on dead FRN.
  (L3) ENG: corridor ids byte-identical 1943.7→1945.7 (552 Western Desert vs ITA), 0/71 corridor
  provinces held for 24 months, 12/61 divisions in theatre; `age` reads 1 wk — weekly re-selection
  CONVERGING on the same unreachable state (a stable pointer, not churn). Exonerated by the same
  sweep: the posture brake (`hold_the_line` on 4/132 war tag-quarters, 3 %) and sector presence
  (100 % of war quarters for GER/SOV/ITA/JAP — the machinery runs).
- Rung reached (wa-diagnosis): measurement done, NO script line named for any leg — diagnosis
  INCOMPLETE by contract. Candidate hypotheses (ASSUMED, each needs its killing measurement):
  (H1/L1) AIFC steers only the surplus left after front minimum needs (writes no
  front_control/unit_request — FIX 56, verified inert), so on long fronts the surplus is ~0 and
  Layer 4 modulates nothing; (H2/L1) `max_age = 4` re-selects faster than armies redeploy or
  battles resolve — the anchor outruns the mass; (H3/L3) sector selection scores the LAUNCHING PAD
  (`WA_AI_AIFC_helpers.txt`) but has no corridor-wide feasibility term (own mass vs corridor
  size/ratio); (H4/L2) USA fails the expeditionary pass entry (3 native enemy-adjacent states / 3
  divisions on faction ground, `[offensive-posture]`) or the land-contact-first anchor never sees
  a USA pad — the "no sector" reason is not separable in a save.
- Engine boundary, stated: Layer 4 consumption (file-defined `force_concentration_*` values) never
  serialises, and the share of surplus actually concentrated is engine-internal. Owner
  `imgui show ai-strategy` (force_concentration tree, GER + USA in a war save) is the only view of
  what is armed — needed to separate H1 from H2 and to read USA's Layer 1/2 state.
- **L3 diagnosis COMPLETE 2026-08-27 (code read, MEASURED in source): H3 CONFIRMED — the scorer
  has no feasibility term, and its defender-side terms actively prefer un-attackable ground.**
  `WA_AI_AIFC_score_state` (`WA_AI_AIFC_helpers.txt:373-425`) scores baseline 100 + terrain
  (desert +20) + thin garrison (< 3 div → **+40**, helpers:400-403) + non-core +20 — all
  DEFENDER-side; the only own-force term anywhere is the launching-pad bonus (5/band, cap 60,
  helpers:244-250), and there is **no minimum**: selection proceeds at pad 0-1
  (helpers:226-258 has no floor), and when NO candidate has any pad the fallback scores
  everything rather than selecting nothing (helpers:233-236 — also explains the ITA-vs-SOV
  Mesopotamia anomaly). Nothing compares own mass to corridor size (corridor build
  helpers:301-337 caps at max_states only). DERIVED: an empty desert held by < 3 enemy
  divisions is near the global maximum score (+20 desert +40 thin +20 non-core) precisely
  BECAUSE nobody is there — ENG's 552 Western Desert wins every weekly re-selection with a
  pad bonus of ~5-10 against ~80 of defender-side score, and the validity test
  (`WA_AI_AIFC_core.txt:152-209`) only asks "still enemy-held and still adjacent", so the
  pointer is stable forever. ASSUMED (engine): with no mass, Layer 4's weights modulate an
  engine decision that never attacks — the sector is decorative. Candidate lever (owner
  decision, not shipped): a feasibility floor in section 2 — e.g. skip candidates whose pad
  is 0 when any pad > 0 exists is already half-present via main-enemy election; the missing
  half is a corridor-wide own-mass/enemy-mass term or a minimum pad for ANCHOR eligibility.
- **L3 fix SHIPPED 2026-08-27 (owner order "corrige d'abord ça").** Anchor feasibility floor:
  new `constant:wa_ai_aifc.selection.min_pad = 1` (strict `>`, repo idiom — i.e. pad band sum >= 2:
  two occupied adjacent friendly states, or one holding 5+ ROOT divisions); selection section 2
  now requires it for anchor eligibility, and the `_aifc_main_enemy = 0` "score everything"
  fallback arm is DELETED (not left dead — legacy-gates discipline; main_enemy = 0 implies all
  pads 0, which the floor rejects). No candidate above the floor → no sector → Layer 4 inert,
  engine default targeting (documented safe path). Pad WEIGHT (5/band cap 60) deliberately
  untouched — kept for the L1 diagnosis. Docs synced: helpers SELECTION MODEL, constants header,
  wa-constants-registry SKILL.md row. Checkers: check_constants 0 err/0 warn, check_skill_refs 0.
  Reviews 2026-08-27: architecture CONCERNS (3 items — else-comment both reasons, `selection`
  group documented, combined-commit constants run: all applied) + lessons CONCERNS (3 items,
  resolved as follows). **Flap table (lessons item 1), weekly cadence, country oscillating across
  the floor:** t0 pad drops ≤1 at re-selection → clear → armour reconcile retires the book, emits
  N+1 negations, ledger +N+1 entries, NET 0 (closure save-proven: aifc.py NET OK on all 25
  snapshots of `24933fb9` — entries never leave the type-83 list, only NET closes); t1 pad back
  ≥2 → reinstall, +N+1 entries, NET restored; t2 worst case weekly flap = 2(N+1) ≈ 58
  entries/week at N=28 (~3000/year pathological, vs USA's measured 365 in 10 years) — cost is
  ledger length at armour evaluation only, mis-steering none (one unsteered week per cycle = the
  pre-fix no-sector state). Grace-window sizing data now MEASURED for the next lever: real lapse
  episodes are 1 week (GER 195→195+1 once, ITA once), so a K=2-week retirement grace absorbs
  every measured episode — ship it only if a campaign shows r67 retire_n climbing post-floor.
  **L2 harness SHIPPED 2026-08-27 (contract v1): `WA_TEST_aifc.txt` + `events/wa_test_aifc.txt`.**
  Prints every selection stage for one country — eligibility term by term, native candidates,
  the expeditionary pass run UNCONDITIONALLY with the shipped gate (native < 3) and the
  ally-states-with-3+-ROOT-divisions count reported beside it (the USA discriminator), per-candidate
  pad + anchor-eligibility vs the new floor, stored sector, main enemy. Independent walk
  (duplicates helpers 1/1b/1c/2 limits; shares only the constants, which ARE the bars). **Owner
  console run owed, and it is BOTH tests at once**: `event wa_aifc.1 USA` then `event wa_aifc.1 ENG`
  (do NOT tag into them — tag-switching makes them human; fire with the target from any tag),
  paste the `elig`/`cand`/`sum` lines here. Expected reads: USA — which stage zeroes (H4 settles);
  ENG 1944-shape — cand_total > 0 with anchor-eligible = 0 proves the floor unpins the desert.
  `event wa_aifc.2` = all AI majors at once. F9 boot covers the new event file too.
  **Mission-war walk (lessons item 2):** `WA_AI_MILITARY_ITA_ethiopia_mission_objectives_FRONT`
  (`ITA_FRONT.txt:498`) is gated on `has_war_with = ETH` + mission states only — its
  `force_concentration_target_weight` ±80/−60 literal-state pairs aim AIFC INDEPENDENTLY of the
  scripted sector arrays, so the floor cannot break mission-war steering even at pad 0; ITA's
  AOI buffer additionally stands 9+ divisions adjacent to the mission states at war start
  (pad ≥ 2). **Fallback removal (lessons item 3): removed outright with the rationale in the
  section-2 comment.** F9 boot test OWED (scripted-effect edit + new constant group).
- Coordination: `allied-division-stability` Step B already names "AIFC dwell" as a candidate
  hysteresis — L1's churn measurement is what motivates it; a dwell change ships under ONE slug.
- **Owner imgui 2026-08-27 (MEASURED, save 1944.4): the Layer 4 arming question is settled.**
  GER `force_concentration` trees: `factor` 1 entry +28 points (engine total 15+28 = 43 % of
  surplus may concentrate), `front_factor` 2 entries +50/−50, `target_weight` 2 entries +50/−99 —
  boost and suppression PAIRED exactly as the file designs them (the −99 catch-all is the
  documented value). USA: `factor` +13 (→ 28 %) and **zero `front_factor`/`target_weight` rows**.
  DERIVED: (i) the hypothesis "Layer 4 blocks fail to arm" is DEAD for GER — the values are armed
  and paired, so L1's missing traction is H1 (no surplus to modulate) and/or H2 (anchor outruns
  the mass), which imgui cannot separate (surplus share is engine-internal); (ii) L2 is localised
  to SECTOR SELECTION: USA's Layers 1–2 work (factor armed at +13), the scripted axis never
  exists, so H4 is the only live branch for USA — next discriminator is a scripted probe on the
  expeditionary-pass entry conditions, not the strategy files. ASSUMED: the Target ids 714–717 are
  imgui-internal entry ids for the trigger-keyed Layer 4 blocks, not state ids — un-decoded.
- Verification (probes runnable with this sweep's method — `aifc.py` + `control` + `plans.py
  --where`): (L1) main attacker: >= 25 % of non-garrison divisions in or adjacent to the corridor
  within 2 months of selection, and corridor province gain > 0 in a majority of 6-month windows;
  (L2) USA holds a sector >= 2 consecutive quarters once at war with land contact (1943+); (L3) no
  country keeps a byte-identical corridor > 6 months while holding 0 % of its provinces. Added
  for the L3 floor: (L3b) a country with no pad >= 2 anywhere holds NO sector (aifc.py: sector
  absent, not decorative), and (L3c) r67 `retire_n` does not climb post-floor (flap watch — the
  K=2 grace window is the ready lever if it does).
- Closed when: each leg carries a six-box diagnosis naming the script line or documented engine
  boundary, AND per leg either a fix ships under this slug and its verification line passes in a
  campaign, or the owner accepts a written no-fix ruling.

## PARKED

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
| commonwealth-handoff | OPEN (parked 2026-08-27, owner order - WIP limit; exemption lever live since 2026-08-25) | Handoff inverts: availability bars read TOTAL divisions, not in-theatre (24933fb9: RAJ reads available with 3 div in East Africa on 76 total, ENG back-fills 14); every bar single-threshold, flap lever documented in the block (git history of this file) | Delegate missions armed and manned (R72 legs), Indian army in East Africa/El Alamein, no dominion dockyard nailed by an unbuildable design |
| `aoi-border-garrison` | OPEN, both legs shipped 2026-08-27, parked 2026-08-27 (WIP limit, owner choice — slot given to `aifc-traction`). Leg 1: `AXIS_abandon_east_africa` FRONT/THEATRE retargeted off region 17 (corridor {380,381} + s.r. 217), new `_colony_THEATRE` -200 gated `NOT owns_east_africa_colony`, ITA buffer widened to {550,559,271,909,910}, family gate extracted. Leg 2 (sea reinforcement): buffer ratio 0.10→0.20, trigger `east_africa_sea_route_hostile` (Suez 923), `owner_cut_off_THEATRE` -200, `naval_avoid_region` +1000 on the 5 Red-Sea/Indian-Ocean lanes. Campaign `24933fb9`: colony holds 37 months vs 2 pre-fix; (b) PASS (EA front orders manned), (d) PASS (0 GER div), (c) marginal FAIL (1-2 strays, Kurdufan buffer leak order 9607 unexplained), (a) FAIL as written / PASS on buffer population (43-57 % border). OWED: F9 boot (new ai_strategy blocks), owner imgui (cut-off gate armed/released vs Suez), §12 telemetry re-instrumentation before next scoring | ITA 9/9 AOI divisions pinned to {550,559} port buffer, zero EA front orders for ITA and ITS (`15176ce6` 1940.9-10); leg 2: AOI grows 9→11-23 by 1943 by sea past the Allied navy (`24933fb9`; ITS never released, growth = external) — engine never refuses the route (`MAX_ALLOWED_NAVAL_DANGER 80` vs ceiling 50) | (a) >= half AOI divisions in border states {271,909,910,550}, (b) EA front order for the AOI holder, (c) zero ITA/ITS div in 217/380/381, (d) zero GER div in AOI, (e) no sea growth while Suez hostile (~0.20 prepositioned at entry), (f) reinforcement resumes once the Axis takes Suez. Full record: git log `[aoi-border-garrison]` + this file's history |
| `aifc-closure-eth` | MEASURED 2026-08-27, never opened (found during the `aifc-traction` sweep) | ITA carries a `CLOSURE MISMATCH` on ETH — ledger NET +250 vs book -150 — on 8 consecutive quarterly saves, 1943.10→1945.10 (`24933fb9`): the +400 boost was never cancelled when ETH was annexed, a later -150 suppression stacked on top; the `WA_AI_AIFC_helpers.txt` KNOWN GAP's "rare and self-correcting" does NOT self-correct in 25 months | The armour reconcile retires/cancels book entries on annexed or dead tags (or the residual is bounded with a t0/t1/t2 table and accepted in writing); a campaign shows no ledger-vs-book mismatch persisting past 2 reconciles |
| `minor-expeditionary-fitness` | SHIPPED-UNTESTED, parked 2026-08-27 (owner order). Shipped: fitness floor `WA_AI_MILITARY_is_fit_for_expeditionary_front` (> 5 MIL; raised to > 10 on 2026-08-27, owner order on the ETH-at-8 symptom — trains cap kept at < 5, registry group `expeditionary_fitness_mil_factory_floor` now advisory, the 5-9 band trains at home but stays home) + CAPS `unfit_army_stays_home` -100 (`e958ef934`); the two ALLIES pulls (`europe_first`, `east_africa_contested_FRONT`) fitness-gated 2026-08-25; lend-lease gate `WA_AI_LEND_LEASE_recipient_is_worth_equipping` (fitness OR `home_threatened`, homeland hatch owner-ruled) on both recipient paths; 2026-08-27 `WA_AI_PRODUCTION_trains_no_divisions` (< 5 MIL + > 4 div + no civil war -> build suppression, merged [rk-no-divisions], registry group `expeditionary_fitness_mil_factory_floor`). Diagnosis settled: H1 KILLED (owner imgui MEASURED, entry armed at -100), live cause H2 (-100 under-sized vs ALLIES +150/+75 pulls, cross-area summing still ASSUMED) + H3 (buffer/no-order divisions out of any front_unit_request's reach). Campaign `24933fb9`: leg (a) materially improved (1944.6 12/12 NEP home; 1941.6 window still violated, 6/10 in Egypt/Libya). OWED: console harness (FROM.FROM state_trigger), F9 boot (`trains_no_divisions` block), lend-lease harness run (`wa_test.300`/`301`) | NEP at 1 arms factory holds front orders across the Sahel/Horn for 4.5 years, 9-13 of its 12-16 divisions out of region (`8f9b5653`); ETH at 8 factories behaves identically = the > 5 gate misses the owner's rule | (a) NEP/BHU divisions never beyond their own neighbourhood, (b) no country at <= 10 MILs fronting beyond its neighbourhood AND every no-civil-war < 5-MIL country deployed <= 8 div sustained after 6 months at war (NEP flattens; ETH-class control at >= 5 MILs still grows), (c) RAJ/AST/CAN theatres still manned once NZL/SAF are held back. Full record: git log `[minor-expeditionary-fitness]` + this file's history |
| `fra-battle-of-france` | OPEN, fix shipped 2026-08-27, parked 2026-08-27 (WIP limit, owner choice — slot given to `lend-lease-observability`). Shipped: `FRA_homeland_invaded_recall_colonials_THEATRE` (area_priority -90 NA/med/middle_east, gated `home_threatened`), Alpine pair `FRA_alpine_front_FRONT`/`_THEATRE` (+100 south_france, gated `any_enemy_country = is_italian_homeland_power`), `FRA_defense_of_the_colonies_FRONT` re-armed to -5000 release, no-op `FRA_ignore_garrisons_until_invasion_start` deleted; spec SS25; reviews applied; F9 boot OK. Campaign `24933fb9` NOT CHECKED — `surrender_progress` not serialised and the gate window falls between monthly saves (ITA declares 1940.6.11, FRA dead by 1940.7.1); symptom near-vacuous this run (FRA 3/121 div in NA+Corsica). ASSUMED stated: garrison -5000 release semantics; colonial channel of the ~20 div | Owner report (ironman `feedback_save`, so owner figure not save-MEASURED): FRA garrisons North Africa/Corsica (~20 div) during the Battle of France while the Italian border sits open | A non-ironman Battle-of-France save (mid-June, or the console harness) shows (a) FRA NA+Corsica division count falling once `surrender_progress > 0.05`, (b) >= 2 FRA divisions on the south_france fronts while an Italian homeland power is an enemy, (c) Maginot/fall_rot nets unchanged |
| `rk-no-divisions` | SHIPPED 2026-08-27 (`1652af012`), parked (WIP limit). **Campaign `24933fb9` PASSED**: 7 of 8 `autonomy_reichskommissariat` tags (RBA/RBE/RGR/RHO/RNO/RPO/RSE) at ZERO divisions on every save, ALB flat at its 3 scripted starters, no count ever rises; ITS-control leg vacuous (ITS never released). F9 boot + error.log id check still OWED | Old brake value -1, war-gated, infantry-id only, tag list missing ITA's 8 RK tags and ENG conversions — RK tags train divisions (MEASURED in code) | F9 boot + error.log id check pass; a campaign shows every `autonomy_reichskommissariat` country (ITS excepted) with zero divisions in training and a non-rising division count (scripted grants aside); control: ITS still fields/trains its colonial divisions. Full record: git log `[rk-no-divisions]` + this file's history |
| `allied-total-commitment` | TESTED, parked 2026-08-27 (WIP limit; F9 boot test for the CAN reserve-batch reward still OWED). Campaign `24933fb9`: the batch FIRED and DEPLOYED (MEASURED: 10 `Reserve Divisíon` at 1939.11) but was consumed on a front by 1942 and CAN never rebuilds (2-4 div 1941-44 on 104 arms factories — separate defect, candidate subject); leg (a) still FAIL through 1943 (100% home areadef at 1943.6), half the army abroad by 1945.6. Amended same day (owner orders, two rounds): (1) the one-shot closes the reserve program after its batch — `WA_reserves_unlock_template` + `reserves_deployment_complete_flag` applied directly (NOT a bank flush; owner refused deploying more) so the template becomes modifiable; (2) a READY batch (bank >= 10) is spent like a normal activation — the +10 grant fires only on an empty/short bank, so no residual bank remains when the country had recruited its own. Fresh campaigns only (a save past the focus keeps its locked template). Reviews: architecture OK, lessons CONCERNS — retroactivity stated here, no `break` writes in the deploy path (MEASURED), refill impossible pre-unlock (`WA_reserves_can_recruit` needs `has_war = no`, the focus needs `has_war = yes`) | CAN 4-9 div, 100% areadef home garrison (`8f9b5653`); release trigger PROVEN on CAN (wa_tc.1 harness 1942.2, closure PASS). **Owner imgui 2026-08-27 (MEASURED): CAN garrison tree = ONE summed entry, Weighted Value -4950 (-5000 release + 50 minors_home_first) — armed, held, and SUMMED (first direct proof same-type/same-target entries sum) — yet the home engine areadef divisions do not move: a negative `garrison` does NOT empty existing engine area-defense orders; the buffer is the proven mover (Scotland div, 1942.3).** Shipped same day (owner order "zéro division au mainland"): `protect_home_floor` gated off under `total_commitment_active` (threatened +200 tier keeps its own gate), new `CAN_THEATRE_total_commitment_empty_mainland` buffer ratio 0.75 (sums with defend_britain 0.25 to 1.0, per-order summing ASSUMED) on the britain states, `subtract_fronts_from_need` so front divisions stay abroad. Reviews: architecture CONCERNS (SS23 consumer rows + summing relabelled) + lessons CONCERNS (all applied: 0.75 re-sized as its own order — the ratio-pool arithmetic is lessons-REFUTED, each block is a separate order and >1.0 arbitration UNKNOWN; buffer→continental-front feed labelled ASSUMED, USA unit_buffer_for_europe pattern; no new ai_area alias, area=britain reused, cap-72 item void). **Landing-residual t0/t1/t2, stated:** t0 enemy lands on a Canadian core → `home_theatre_threatened` trips at the enemy-on-core term; t1 next engine strategy re-evaluation (ASSUMED sub-weekly, SS23 cadence limit) — commitment flips off, buffer disarms, threatened +200 arms; t2 transatlantic return crossing ~2-4 weeks; worst case ~3-5 weeks of thin mainland, and front-engaged divisions in Europe return slower still — ACCEPTED, it is the owner's zero-mainland order. defend_britain 0.25 armed for CAN is MEASURED (the 1942.3 Lanark order, states byte-equal); both-blocks-together is only observable next campaign. F9 boot owed. Probe: next campaign, zero CAN divisions in Canadian states while committed and home safe (vs 2-3 in `24933fb9`), AND CAN divisions appearing on continental fronts (tests the buffer feed). **2026-08-27, second owner report (RAJ divisions in BEL/HOL mid-Battle of France): the gate's missing BRAKE half shipped** — `WA_AI_MILITARY_ALLIES_overseas_guests_wait_for_bulwark` (`FACTION_ALLIES_FRONT`, front_unit_request -100 on benelux/north_france/france/west_france/south_france) + audience trigger `WA_AI_MILITARY_is_overseas_guest_refused_by_bulwark` (allies member, at war, capital outside Europe, gate closed). Six-box (static, rung 2 unmeasured — owner report, no save): the gate only withholds the +150 boosts; a total-commitment released army (RAJ: minor+subject+fit+home-safe) still reaches the only live European fronts via engine default on the flat baseline, the Africa direction +60 being inert pre-Italy-entry and no CAPS veto applying to a fit member. Doc §24 updated (counter-bid ruling: not violated — during the window every positive on those areas is enable-gated off by the same trigger, the -100 suppresses engine default only). Reviews: architecture CONCERNS (doc sync — applied) + lessons CONCERNS (ASSUMED header on -100-as-veto and static capitals added; all-enable already true). Owner confirmed 2026-08-27: the reported game ran HISTORICAL difficulty — the gate was closed, the missing brake was the live path, the fix targets the reported symptom; non-historical behaviour (gate open, brake inert) stands by the earlier owner ruling | Campaign legs: (a) CAN majority front/buffer outside North America while home safe; (b) AST/NZL/RAJ areadef ~0 while Pacific quiet AND re-garrisoned within 3 months of `pacific_threat_imminent`; (c) dominions on African fronts once past the 10-factory fitness floor (raised from 6 on 2026-08-27); (d) control: a non-faction minor at war keeps its home garrison; plus SS24 bulwark-guest probe (zero overseas-Allies div on FRA soil AND on the benelux/BEL/HOL fronts while FRA holds `disjointed_government`, historical difficulty; control: the flow resumes once the idea is shed or fall_of_france). Full record: git log of this file + [allied-total-commitment] commits |
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
| 2026-08-27 | `rail-corridors` | Strategic corridor railways (AI pathfinding cheat): 8 faction-gated land corridors get free level-5 rail so redeployment stays off the sea. Per-edge builds, impassable states routed around, PC mirror synced, `wa_test_rail` harness. Human validation: tested and functional in-game (owner, 2026-08-27). Campaign probe folded into F-checks: `WA_rail_corridor_*_built` flags + level-5 track. |
| 2026-08-23 | `na-corridor` | NA corridor logistics (rail/depots/ports/theatre air bases, Fix 95–135). Human validation: tested and functional. Absorbed R9, R13, R52, R60, R68, R69, R71, R77, R78, R81, R91, R96, QUEUE 0q/0r/0m/0i. |
| 2026-08-23 | `med-axis-posture` | Axis Mediterranean posture (Afrika Korps, Tunis, Italy, Ethiopia, Med fleet, convoy interdiction; Fix 96–137). Human validation: tested and functional. Absorbed R17, R61, R63, R64, R74–R76, R80, R82, R83, R92, R94, R97, QUEUE 0t/0h/0f/0g/0. |
| 2026-08-23 | 14 R-items retired on PASS | R10, R19, R31, R38, R39, R40, R42, R44, R45, R49, R50, R56, R66 (folded), + R53 dropped (probe tool never existed). Details: archive. |
