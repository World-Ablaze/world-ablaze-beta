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
  A criterion met once = closed; a regression reopens from the symptom. The FUNDAMENTAL items
  (`.claude/skills/wa-campaign-checklist/references/checklist.md`; F2/F5/F6/F8/F9 since the
  2026-08-27 pruning) remain the safety net.
- `SHIPPED-UNTESTED` means: code committed, the owner has NOT run the console harness.
  Older than 3 days = checker ERROR (`UNTESTED-STALE`). Paste the harness output here to
  move to `TESTED`.
- Heading format (parsed by the checker): `### <slug> — <STATE> (<YYYY-MM-DD>)`.
- Detailed probes of subsumed R-items: `documentation/archive/CHECKLIST_R_ARCHIVE.md`
  (frozen copy, not checked).

## OPEN

> **Campaign `1ac7e4ea` scored 2026-08-27** (cloud, `dlcs=257535`, BHU observer, 120 monthly saves
> 1936.2-1946.1, unbranched, build = HEAD `cd234cc51` — DERIVED from commit 13:49:54 / first save
> 13:52, MEASURED by `wa_tlm_version = 32` first and last save + live `wa_tlm_llr_recv_*` arrays).
> F1-F4/F7 PASSED near-historical (war 1939.9.13, France 1940.6.23, Barbarossa exact 1941.6.22.13,
> Pearl Harbor 1941.12.4, Franco 1939.7.24). **F5 FAILED — stalemate, not collapse**: GER 51/53 own
> states, 307 divisions in monotone GROWTH, holds Paris (liberated 1944.6.19, re-lost by 1946.1);
> East a stalled grind (only Kiev fell, 1942.7.29); West HALF-alive — Torch 1942.10.1, D-Day
> 1944.6.9 on schedule, Normandy front manned (USA AG5 49 div, created 1944.6.13), North Africa
> French ground at 1945.6 (32/36 provinces) — but no Rhine crossing, ever. **The
> allied-invasion-foothold-deadlock candidate is FALSIFIED as a cause on this run**: France was
> never fully occupied (FRA keeps 12-19 metropolitan states all war → continuous land front, no
> landing needed), and the zero-type-3 census reproduces on a HEALTHY western arc — invasion
> orders live < 1 month (Torch orders present 1942.9-10, gone 1942.12; D-Day consumed inside
> 1944.6) so a monthly type-3 census cannot discriminate deadlock from health. If re-proposed, the
> candidate needs an OUTCOME metric (far-shore provinces over time), not an order count.
> **[reserve-quality] v2 verdicts**: conversion **PASS** twice (USA bank −20 → deployed +19 in
> Dec 1941; RAJ −30 → +37 at 1942.1-3), tier veto **PASS** on its real cell (RAJ 1939.10: 22 MIL /
> 30 div / bank 30 held; ≤24-MIL-at-40+-div cell empty this run), timing **FAIL** (USA's residual
> 10 banked frozen 1942.1→~1942.7 at 345-493 MILs — the veto is FALSE there; suspect upstream
> `WA_reserves_can_deploy` bars, e.g. `has_manpower > 150499`, not the tier rule — SAF 10 banked /
> 34 MIL / 4 div and AST/NZL never banking point the same way), ENG leg **FAIL** (bank 40 → 0 over
> 1945.2.1-5 with the British Isles INTACT — MEASURED zero home provinces lost; DERIVED suspect:
> IRQ at war with ENG since 1945.1.14 tripping `any_home_area_neighbor_country`, i.e. the Middle
> East counts as "home area"; console/live check needed, not save-decidable).
> **Candidate validation pass 2026-08-27 (owner doubt, three subagents, six-boxed each):**
> **(1) eng-reserve-wave — REAL, re-stated.** MEASURED: the release dumped 4 batches = 40
> unequipped divisions (create_unit 0.3 eq / 0.3 xp) into London over 1945.2.1-5
> (`days_remove = 1`, no throttle) and **ZERO survive to 1945.3** — the "1 survivor" first
> reported was pre-existing div 107628 (byte-identical strength both saves); killing closure:
> `post_mortem` records +41 in the month vs +1/0 in adjacent months, and 20 + 40 − 41 = 19
> exact. The `:206` unconditional-debit suspicion is KILLED as the cause (spawn fired; the
> hazard stays latent). Mechanism: the ENG brake `WA_reserves_is_expeditionary_only`
> (`WA_reserves_triggers.txt:287-292`) is defeated by its own AND-preconditions exactly when
> ENG is losing — IRQ at war 1945.1.14 (home-neighbour term) or `surrender_progress > 0` (22
> states lost); which term = not save-decidable, one console read settles it. Where the 40
> died (Tunisia front vs sea transit) is the engine boundary, ASSUMED.
> **(2) can-transit-attrition — REAL; the OWNER's mechanism CONFIRMED, the first verdict's
> "empty request set" REFUTED by his objection.** Owner: "CAN construit, mais perd ses divs à
> cause du convoy raiding" — tested on the 61-monthly-save conveyor-reset series (the
> discriminator snapshots cannot give): CAN builds CONTINUOUSLY — **16 divisions deployed
> 1941-1946, training queue occupied 59/61 months** (~3.1/year, one at a time, ~5 months and
> ~18.5k manpower each) — and **≈15 leave the OOB (±5)**. Not lent (0 `expeditionary_owner`,
> whole-file scan), and essentially NEVER in land combat (`last_combat_date` null in 47/61
> months, 3 episodes in 10 years): deaths cluster the month AFTER a high at-sea reading on
> transatlantic runs (1943.8: 4/4 divisions embarked, one sea province → 1943.9: 3 lost;
> destinations Dorset/Sussex/Algiers/Gabès), `efficiency_due_to_lost_convoys` 0.875-0.93 on
> live routes. "Sunk in transit" is DERIVED (a country's own convoy/at-sea division losses
> are not serialised; failed-invasion residual for the minority under front orders). The
> first verdict's snapshot read one-at-a-time building as an idle queue — its residue that
> STANDS: the build rate is also LOW in absolute (1-2 conveyors, never a backlog; ~3/year on
> 100 MILs while 153k own rifles bank and CAN→SOV runs 206k IC) — CAN builds slowly AND
> loses what it builds; both levers are real. Method note for future probes:
> `division_names_tracker`/`post_mortem` is a freed-NAME pool (consumed on reuse, count can
> FALL), never a cumulative death ledger — the conveyor-reset series is the valid counter.
> **(3) eng-zero-armour — KILLED, TELEMETRY-ARTIFACT, do not admit.** Ground truth
> (`plans.py --templates`, 4 dates): ENG held 3-5 armour + 1 mech divisions CONTINUOUSLY, on
> front orders, 72 factories on tank chassis at 1943.6, ~2 340 own-built hulls in stock.
> `wa_tlm_comp_armor/mech`'s lowest band is `size > 4` (`WA_TLM_core.txt:659/:675`) so the
> gauge floors to 0 below 5 divisions; the hist "spikes" are the band crossing exactly 5
> (5/34 = 14.7059, 5/43 = 11.6 — both reconcile to printed precision). Meta-defect recorded
> in F8: the comp gauges are unusable below ~5 armour divisions (band index over real count) —
> a WA_TLM fix is its own candidate (meta, owner request required). The real residue folds
> into F8's ENG attrition 43 → 19 (active losses at the last save, `num_armies_for_training`
> 24.5 vs 19 tell). Candidates (1) and (2) admissible; none admitted this session (WIP limit;
> owner decision).

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
> 134/31 → closed by archetype; GER 243/107 → open (veto moot, home neighbour at war — escape
> superseded 2026-09-05 `[reserve-capacity]`: tiers now hold in every war); USA 1942.1
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

### armoured-waves — PARKED (2026-09-10)
- State: code ships with this subject update; **the console harness has NOT been run**. Parked,
  not `SHIPPED-UNTESTED`, only because the four live slots were already taken
  (`resource-infra-targeting` precedent, 2026-09-09). Promote to `SHIPPED-UNTESTED` and run
  `event wa_test_tmpl.1 SOV` the moment a slot frees; until then the behaviour is unverified.
- Owner order 2026-09-10 ("oui, branche-le"). Intended behaviour: a country holding the
  `armoured_waves` sub-doctrine fields the ARMOURED_WAVES twin of whatever 30-width armour
  composition its ladder already chose, instead of the base twin.
- Symptom, **MEASURED** (mod files): 48 `*_ARMOURED_WAVES` ai_template blocks exist — 17 medium
  (`6200-6216`), 17 modern mirror (`6700-6716`), 14 heavy (`7200-7213`) — and NO code path in
  `common/` or `events/` ever wrote a `_template_value` in those bands. Dead code since
  `51bbac508e` "Finished AI Armoured Wave Templates".
- Cause, **MEASURED** (script): `WA_AI_TEMPLATES_calculate_medium_armor_template` writes only
  `6000/6001/6100-6116` (plus the `+500` modern-chassis `_tier_offset`) and
  `WA_AI_TEMPLATES_calculate_heavy_armor_template` only `7000/7001/7100-7113`. Neither ladder,
  and neither `WA_AI_TEMPLATES_*` trigger file, ever read the sub-doctrine.
- Change: `[armoured-waves]` adds the decision trigger
  `WA_AI_TEMPLATES_use_armoured_waves_templates` (`has_doctrine = armoured_waves`) and the
  effect `WA_AI_TEMPLATES_apply_armoured_waves_mirror` (`+100` on `_template_value`, copying the
  existing `WA_AI_TEMPLATES_apply_motorized_hospital_mirror` lever). Called in the medium ladder
  guarded on `_template_value > 6099` and BEFORE the `+500` chassis offset, and in the heavy
  ladder guarded on `> 7099`.
- Why `+100` is the whole change, **MEASURED**: the pairing is 1:1 for all 48 pairs — base value
  `+100` = wave value, wave block name = base block name + `_ARMOURED_WAVES` — and the only
  composition difference in every pair is battalion/company COUNTS. No wave twin names an
  equipment type its base twin did not, so the ladder's existing composition validation still
  holds and no branch needs re-validating at the wave tier.
- Impact, **DERIVED**: the `armoured_waves` sub-doctrine cuts armour combat width by 40 %
  (24 battalion lines, `common/doctrines/subdoctrines/land/armor_subdoctrines.txt`). With the
  doctrine the wave twins land at 26.4-28.2 width against 30-33 for the base twins; without it
  they would be 36-40. Today the doctrine is reached by historical difficulty +
  `WA_AI_CONFIG_is_deep_battle` (SOV) and by the GER Barbarossa catch-up fallback; competitive
  never picks it. The gate reads the live doctrine, so any country that acquires it is covered.
- Regression risk, **DERIVED**: the `+100` lever is shared with the motorised-hospital mirror,
  whose six call sites are all in the infantry / mountaineer / marines ladders — no collision on
  armour values (verified by grep). The order matters and is asserted in the code comment: after
  the chassis offset, `6500 + 100` would land on `6600` (20-width modern MEC → 30-width modern
  MOT). A country that gains the doctrine mid-campaign flips at the next monthly pass and its
  divisions converge in the field (`can_upgrade_in_field = yes` on every wave block).
- Readers of the changed value, **MEASURED** (principle 3(a), full enumeration): outside
  `common/ai_templates/` exactly three files read a literal `WA_MEDIUM/HEAVY_ARMOR_TEMPLATE`
  value. Two of them broke on this change and are fixed in the same commit:
  - `WA_AI_TEMPLATES_is_medium_mis_family` listed only `6105-6110`. With the doctrine the flag
    reads `6205-6210`, the trigger fell to false, and the light ladder's MIS redirect plus the
    `..._FINAL_MIS` enable went silent — conversion would land on the pure 9+6 that
    `[armor-class-handoff]` exists to prevent, on SOV, which is both the only wave country and
    the light-support park country. Added `6205-6210`. The MODERN bands `6605-6610` /
    `6705-6710` deliberately stay out: the FINAL is built from `medium_armor` /
    `medium_infantry_support` battalions, so a modern-chassis role would be pointed at a
    composition it never claims — that also explains the pre-existing absence of `6605-6610`,
    which is therefore NOT a gap to close here.
  - `WA_TEST_armor_budget.txt` band lists `_abt_bandmed` / `_abt_bandmod` omitted the wave
    values; its own header says a missing value "reads as no template and looks like a
    template-system failure". Added `6200-6216` to the medium band and `6700-6716` to the
    modern one — the doctrine moves the value, not the chassis.
  - the third, `WA_AI_TEMPLATES_effects.txt`, reads only `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE`
    `15007/15008` — unaffected.
- Checker updated: `tools/check_templates.py` modelled only the motorised-hospital `+100`, and
  reported all 48 wave blocks as `TEMPLATE-NO-VALUE`. It now reads the waves mirror's floor out
  of the script (`waves_mirror_floor`) instead of carrying its own copy, and applies it BEFORE
  the `+500` tier offset. Run: 0 WARN, 4 pre-existing `SLOT-SUFFIX-MISMATCH` ERRORs in
  `WA_AI_TEMPLATES_hq.txt`, untouched by this subject.
- Timeline of a doctrine pick, **MEASURED** except where marked (no "self-healing" adjective
  without this table, AGENTS.md 3(f)):

  | t | event | cadence | state |
  | --- | --- | --- | --- |
  | t0 | AI picks `armoured_waves` | whenever it spends army XP | flag still `61xx`/`71xx` |
  | t1 | monthly template pulse (`WA_AI_misc_on_actions.txt:274`) | ≤ 31 days after t0 | `update_target_template` clears the flag and sets `62xx`/`72xx`; INTENT has moved |
  | t2 | engine best-template / field-upgrade pass | **ASSUMED**, not measurable from script | fielded divisions walk to the new target (`can_upgrade_in_field = { always = yes }` on all 48 wave blocks, MEASURED) |

  My gate needs no latch-ordering slot in the monthly pulse: unlike the mechanization / chassis /
  hospital latches it reads the doctrine directly, not a WA flag another latch writes this tick.
- Shape check before arming, **MEASURED**: every wave block is 18 line battalions with 8-10
  regimental-support companies. Neither number is new to this mod — 20- and 22-battalion
  templates already ship live (`COUNTRY_SWI_MILITIA_20_HRS`, `COUNTRY_SOV_LIGHT_SUPPORT_ARMOR_44_
  TEMPORARY`) and 37 live templates already carry 10 regimental-support companies on only 15
  battalions. Whether the engine's designer can reach these targets by greedy edits is the
  engine boundary and stays **ASSUMED** until the harness runs.
- Residual NOT fixed, **DERIVED**: the light-support conversion FINALs
  (`..._TRANSITION_HVY_MOT_FINAL` and siblings) are compositional mirrors of `7100` / `7105`, so
  on a wave country they present 9+6 while the heavy role targets 11+7. Their `enable` blocks key
  on `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE` values only, so nothing goes silently false — the residual
  is a count mismatch the field upgrade closes, not a dead redirect. Naming it rather than
  claiming it is harmless: closing it means authoring wave FINALs, a design call for the owner.
- Recon drift fixed on owner order 2026-09-10 ("corrige aussi le recon de 6200"), **MEASURED**:
  three blocks had been missed by the `7f7cde47ef` sweep — `6200` in the hand-maintained medium
  file, `6600` and `6700` in the generated mirror. All three now read
  `recon_light_tank_company_divisional`, and the three armour template files are internally
  consistent: 36/36 medium, 36/36 modern, 30/30 heavy. The two mirror lines were applied by hand
  ONLY because they move the file TOWARD its generated form — the generator emits exactly them —
  so they do not collide with the divergence recorded below.
- **The modern mirror and its generator had both diverged. Resolved on owner order 2026-09-10
  ("option 1, reporte les reglages dans l'original") — the generator now reproduces the committed
  file byte for byte, verified.** Two separate faults were behind it:
  - The generator silently dropped the whole wave band. `build()` iterated exactly two width
    groups, `value % 1000` in `[0,100)` and `[100,200)`; `6200-6216` matched neither and was
    emitted nowhere, with no error and no count check — 19 blocks written where the source has
    36. Fixed by adding the `(200, "30 Width Armoured Waves")` group, with a comment saying the
    band list IS the contract with the source file.
  - Six modern twins had been hand-tuned in the OUTPUT: `6602`/`6603` and `6702`/`6703` promote 3
    of their own assault guns from regimental support to the LINE, and `6700`/`6701` shave one
    hull for one infantry battalion. The reason is cost — a modern hull is far dearer than a
    medium one, so these variants trade hulls away rather than field twelve.
  - **Where the tuning went, and why not into the medium source, MEASURED**: medium `6102` has no
    `light_assault_gun_battalion_line` at all; writing one there to satisfy the mirror would
    change the MEDIUM template, which is live for every non-modern country. The numbers therefore
    live in `COMPOSITION_OVERRIDE` in the generator — the thing that owns the output — keyed by
    medium value, each entry carrying its reason. `build()` raises on a key that no longer matches
    a medium block, so a stale override cannot silently stop applying (both guards exercised).
  - Closing check: `build()` output vs the committed file = 0 divergent lines, and a real run
    reports "up to date". The file is reproducible from its source again.
- Harness: `WA_TEST_TMPL_armoured_waves` added to `common/scripted_effects/WA_TEST_templates.txt`,
  called from both `wa_test_tmpl.1` (report) and `wa_test_tmpl.2` (pre/post of a real pass). It
  logs `doc` / `med_set` / `med` / `hvy_set` / `hvy`. `doc=1 med_set=1 med=0` = the mirror did not
  fire; `doc=0` with `med>0` or `hvy>0` = an overwidth target and a stop-the-campaign reading.
- No WA_TLM metric: §3.8 "standing" is a system-health invariant asked of EVERY campaign, and one
  country holds this doctrine on the historical path. The console harness is the decisive read.
- Verification (owner console): on a save where SOV holds `armoured_waves`, `event wa_test_tmpl.1
  SOV` must read `doc=1` with `med` in `6200-6216` or `6700-6716`. Control: any country without
  the doctrine must read `doc=0 med=0 hvy=0` while `med_set=1`.
- Closed when: the harness reads `doc=1` with a wave value on a doctrine-holding country, the
  control country reads `doc=0` with no wave value, and one campaign shows no country carrying a
  wave value with `doc=0`.

### resource-infra-targeting — PARKED (2026-09-09)
- State: implementation ships with this subject update; parked only because the four OPEN slots
  are already occupied. Re-open when one slot is free for owner-game verification.
- Owner order 2026-09-09 ("implémente le fix"). Intended behaviour: resource-extraction
  infrastructure targets only a state carrying a resource that currently justifies this strategy.
- Symptom, **MEASURED** (owner playthrough): with SOV `WA_AI_needs_bauxite = 3`, priority
  construction selected states 876 and 226; their state files contain no bauxite.
- Cause, **MEASURED** (script): `WA_AI_resource_extraction` proved only that one qualifying state
  existed, then `WA_AI_get_resource_slot_scores` admitted every rich controlled state and
  `WA_AI_priority_queue_INF_resource` accepted the first buildable score without rechecking need.
- Change: `[resource-infra-targeting]` centralises the existing seven active branches in the
  state-scope observation `WA_AI_CONSTRUCTION_has_needed_resource_for_infrastructure`, reused by
  the existence gate, score-list admission, standard queue consumer and PC queue consumer.
- Impact, **DERIVED**: historical SOV with only bauxite at need 3 excludes 876/226 and retains its
  bauxite states; an ahistorical country with another need at 3 retains states matching that need.
  Multiple simultaneous needs remain composable. The legacy standard consumer now gets the same
  final guard; it has no live caller in `common/` or `events/` at this revision.
- Regression risk, **DERIVED**: a state can disappear from resource scoring when it contains no
  currently needed resource. This is the intended restriction; resource thresholds, scores,
  priority, budget, cadence and controlled-state perimeter are unchanged.
- Harness: none owed — 36 changed PDXScript lines, no on-action effect signature/scope change, and
  non-rail priority construction has no existing `WA_TEST_*` harness.
- Verification (owner game): with only `WA_AI_needs_bauxite = 3`, first inspect the type-25 PC
  target state, then let that project complete; its state has bauxite >15 and 876/226 are absent
  from type-25 starts. Repeat with one non-bauxite need at 3 to prove the generic branch.
- Closed when: the owner game verifies both queue admission and one completed infrastructure level
  for bauxite-only and one other-resource scenario, with no type-25 start in an unrelated state.

### techtree-capability — PARKED (2026-09-09)
- PARKED 2026-09-09 at state TESTED (WIP limit, owner ruling): nothing is owed on the code side,
  only the CAMPAIGN-OK run below. Reopen at TESTED when a campaign is scored.
- State: shipped as `7aac08324e` on `ai-rework`, pushed. TESTED, not SHIPPED-UNTESTED: this change
  is scripted TRIGGERS only - no `WA_AI_*` effect called by an on_action changed signature or scope,
  so no `WA_TEST_*` console harness applies and none is owed. The test that gates it is the boot,
  and F9 PASSED (owner-run, below). CAMPAIGN-OK still owed: criterion (b) and the templates-intact
  half of (a) are only visible in a campaign.
- Owner order 2026-09-09 ("j'aimerais une refactorisation de la AI_CONFIG et des triggers utilisant
  la tech ... on abstracte des critères de tech à un pays, le sous entendu étant (ce pays a X arbre
  de tech) ... faire dépendre les triggers de tech des arbres de tech associés, et relier ces arbres
  de tech aux tags de pays qui les ont"). Owner decisions in the same session: table generated from
  `00_technology.txt`, scope = all five folder families, and the tree FLAG is taken now rather than
  in a second commit.
- Intended behaviour: no WA_AI trigger answers "does this country have technology X available to it"
  with a country tag. A tag answers WHO a country is; a technology FOLDER answers what it may
  research; `has_tech` answers what it holds today. The three stay separate and each is asked where
  it is defined.
- Symptom, MEASURED (script): `WA_AI_CONFIG_DIVISIONS_use_light_tank_destroyers = { ITA JAP GER }`
  and `..._use_mechanized_self_propelled_aa = { SOV }` are tag lists whose only meaning is "these
  trees carry the branch"; the seven `WA_AI_CONFIG_AIRFORCE_uses_*` archetypes say so in their own
  comments ("Only France has a separate interceptor tech tree", over a list of FRA/ITA/SOV); and the
  33 `WA_AI_TEMPLATES_has_*_unlocked` gates were flat ORs of 965 `has_tech` ids with the tree named
  only in a comment (one of them mislabelled `# Soviet Union` over three `eng_` ids).
- MEASURED, the fact the tag lists were dropping: every folder in
  `common/technology_tags/00_technology.txt` is owned by `original_tag = X` **OR**
  `has_country_flag = <x>_technologies_tree_flag`, and
  `common/decisions/_unique_technologies_adoption.txt` hands that flag out (21 `set_country_flag`).
  A country that adopted the German tree was still classified on the tag it was born with.
- MEASURED, the fact that decided the DESIGN: 40 further sites grant a national-tree rung WITHOUT
  the flag — `common/national_focus/finland.txt` grants one rung from each of seven foreign trees,
  plus bulgaria / canada / sweden / japan / turkey / uk, `history/countries/CHI`, `ROM`, `RIT`,
  `USP`, `FSM` and the French colonies. So membership answers CAPABILITY only. Availability
  (`WA_AI_TECHTREE_has_<cap>`) carries no membership term: ANDing it in would have taken Finland's
  armour templates away. Written into the generated file's header so it is not "simplified" later.
- Shipped:
  - `tools/gen/gen_techtree_membership.py` → `common/scripted_triggers/WA_AI_TECHTREE_membership.txt`
    (56 folders). Copies each folder's `available` verbatim; the only rewrite is dropping the
    startup escape `NOT = { has_global_flag = tech_tree_startup_flag }`, which is a UI concern.
  - `tools/techtree_registry.json` + `tools/gen/gen_techtree_gates.py` →
    `common/scripted_triggers/WA_AI_TECHTREE_gates.txt`: 33 capabilities × (`has_branch_`, `has_`).
    Armour and artillery families. Rung sets verified identical to the 33 old triggers.
  - `WA_AI_TEMPLATES_triggers.txt`: 2033 → 973 lines, the 33 gates now one line each.
  - `WA_AI_RESEARCH_tanks.txt`: 22 variant `needs_*` triggers gain `WA_AI_TECHTREE_has_branch_*`,
    plus the two tier-agnostic SPG/SPAA triggers. Their comments said "has X tech tree" already.
  - `gen_air_tech_gates.py` emits a `WA_AI_PRODUCTION_has_branch_<line>` twin per line from the new
    registry key `tree_folders`; the six `WA_AI_CONFIG_AIRFORCE_uses_*` tag lists were DELETED and their seven readers now call it directly.
- Behaviour deltas, all deliberate (a tech outside a country's folder is not researchable, so a
  widening only reaches trees that carry the branch): light TD ITA/JAP/GER → + cze/minor/usa trees;
  mechanized SPAA SOV → + ger/usa; interceptor FRA/ITA/SOV → + jap/usa; heavy fighter GER/ENG/USA →
  + fra/ita/jap/generic; multirole, strike bomber and attacker → + the ROM and minor air trees; and
  **ENG LOSES the fast bomber** — no rung of the English air tree unlocks one, it was weighting a
  tech it cannot research.
  CORRECTION to the first statement of this list, which said "all in the RESEARCH-weighting layer":
  the attacker delta is NOT research-only. `WA_AI_PRODUCTION_should_build_attackers`
  (`WA_AI_PRODUCTION_air.txt:176`) read the same archetype, so the minor and adopted air trees now
  also reach an attacker PRODUCTION line. DERIVED bounded: that block also ANDs
  `has_worthwhile_attacker` and the attacker park cap, so it cannot fire before the rung is
  actually researched.
- Left alone, on purpose: `WA_AI_CONFIG_AIRFORCE_uses_heavy_strategic` (no `has_worthwhile_heavy_strategic`
  line exists to build a twin from — it is a sub-class of the strategic bomber);
  `WA_AI_CONFIG_TEMPLATES_admits_medium_armor`, `..._focus_on_heavy_armor` and
  `WA_AI_CONFIG_switch_from_light_to_medium_armor`, which mix per-tree rungs with the
  `[armor-class-handoff]` era logic and an owner ruling — structural only, worth its own pass.
- Findings recorded, NOT acted on: `WA_AI_TEMPLATES_has_modern_inf_support_unlocked` was an empty
  `OR = { }` (now `always = no` with the reason: no technology anywhere unlocks a
  `modern_infantry_support_tank`, so its reader is dead). `WA_AI_TEMPLATES_has_medium_support_armor_unlocked`
  lists only three `eng_` rungs while `fra_support_tank_chassis_1..2` and `usa_support_tank_chassis_1..2`
  exist unlisted (5 rungs), and `sov_medium_spg_tank_4` is absent from `medium_spg`; the full audit
  found only those 6 candidate rungs missing across all 33 capabilities, so the old lists were
  otherwise complete. `minor_armour_folder` lacks the startup escape and excludes only the Swedish
  flag, so a country carrying `german_technologies_tree_flag` holds BOTH folders.
- Reviews 2026-09-09, both run before shipping, both CONCERNS, every required item applied:
  - **wa-architecture-reviewer** — (1) the header it flagged over the unlock aliases was FALSE:
    written for the first design (membership ANDed into availability) and never updated when that
    design was dropped, i.e. the one sentence most likely to make the next author re-add the AND
    that deletes Finland's templates. Rewritten to say what the gate does and why. (2)
    `documentation/WA_AI_LAYERS.md` §1/§3/§5/§7 updated — the layer-1 material list, the routing
    rows for "has tree X" / "tree has branch Y", the named exception for `original_tag` outside
    CONFIG, and the naming note. (3) the layer-1 inversion (CONFIG reading a layer-2 trigger) is
    gone: the six AIRFORCE archetypes were DELETED from CONFIG, not stubbed, and their seven
    readers now call `WA_AI_PRODUCTION_has_branch_<line>` directly. (4) `can_ever_` RENAMED to
    `has_branch_` — `_can_` is the layer-3 DECISION verb in `tools/check_ai_layers.py`, so the old
    name would have let a future `enable = { …_can_ever_x = yes }` gate on an observation and still
    satisfy LAYER4-NON-DECISION. (5) the empty-`OR` equivalence is now labelled ASSUMED at the site.
  - **wa-lessons-reviewer** — its lead concern (the ai_template decommission pass) is FALSIFIED for
    this change: MEASURED, the transitive read closure of the eight widened triggers reaches 57
    files and NONE under `common/ai_templates/` or `common/ai_equipment/`, and the 33 gates that DO
    feed template selection are value-identical. Its "no half-removed legacy gate" rule (owner
    2026-08-16) IS applied: the two armour switches moved bodily into the ALWAYS-FLAGS section with
    their fourteen `always =` siblings, the six air ones were deleted outright. Its "mechanical set
    diff, not an eyeball pass" is satisfied and now automated (below).
  - It also, indirectly, caught a REAL defect. Making the research gates conditional can only
    subtract where the registry is incomplete, and it was: `has_branch_medium_spg` had no Soviet
    folder while `sov_medium_spg_tank_4` is researchable, so SOV would have stopped weighting
    medium-SPG research. Same shape for `medium_support_armor` (fra/usa support chassis). Fixed by
    a `branch_extra` registry field (capability counts the folder, availability does not, reason
    recorded), and the audit that found it is now a generator ERROR: `BRANCH-GAP` re-derives the
    candidate folders from `common/technologies/` — never from the registry, so the registry cannot
    vouch for itself — and exits 2. Self-tested: stripping `branch_extra` makes it fire on exactly
    those three, restoring it returns exit 0.
- Closed when: (a) a boot leaves `logs/error.log` free of parse errors for the three new/rewritten
  trigger files AND an armour-fielding AI still holds armour templates in the first save (the
  regression the 33 rewritten gates could cause); and (b) one campaign save shows a country carrying
  a `*_technologies_tree_flag` researching or fielding the ADOPTED tree's variants - the behaviour
  the whole layer exists for, and the one thing the old tag lists could not do.
- **F9 PASSED 2026-09-09** (owner-run launch, working tree, uncommitted). Discharges the parse risk:
  three new/rewritten trigger files load, and the six triggers deleted from WA_AI_CONFIG.txt left no
  orphan reader. That is the FIRST HALF of criterion (a) only. Still owed: the templates-intact
  observation in a save, and criterion (b) entirely - both need a campaign, neither is boot-visible.
- Verification: a campaign save where a country that ADOPTED a foreign tree is answered on it. Probe: pick any AI with `has_country_flag = *_technologies_tree_flag` and check it
  fields/researches the adopted tree's variants. Until then the cheap gate is the pair of
  `--check` runs plus a boot with no parse error in `logs/error.log` — three new/rewritten trigger
  files load or the armour template system goes silent.

### air-budget — SHIPPED-UNTESTED (2026-09-09)
- **Maintenance floor SHIPPED 2026-09-09 (owner order: "je veux un filet d'usines minimum en
  permanence, pour continuer a un peu moderniser le parc"; N = 2 / 5, every type).** A line closed
  by its park CAP is no longer treated like one closed by a want: it enters a third state,
  MAINTAINED - archetype factor kept, `equipment_production_min_factories` floor of 2 (5 above
  `tier_large_mils`), `unit_ratio` weight and category factor retired, no `AI_purge_*`. The defect
  it fixes, MEASURED on campaign `2ee8a4ba`: USA 0 fighter factories 1943.12-1945.1, ENG 0 for the
  whole of 1943 - a park at its cap flies the airframe it had when it hit the bar for the rest of
  the campaign, because nothing is produced to replace it. This DELIVERS the maintenance half of
  the proposal recorded below ("80 % reopen or a maintenance weight at cap") and leaves the
  reopen-bar half untouched: it is a FLOOR, not a weight, so the type's share of the air pool is
  still 0 while capped and the fighter-floor arithmetic is unchanged. Secondary gain, DERIVED from
  the same campaign's MEASURED reopenings (ENG 1944.10 at efficiency 9.00 = engine base): the
  engine's production line is never deleted, so a reopening ramps from the efficiency it had.
- Mechanics: `should_open_<line>_line` UNCHANGED (it still drives the purge books, the type gates
  and the monthly weights); new `should_maintain_<line>_line` / `should_keep_<line>_line` (= open
  OR maintained) in a MAINTENANCE section of `WA_AI_PRODUCTION_air.txt`; every `should_build_<x>`
  split into `wants_<x>` + a named `<x>_park_is_below_cap`; the line blocks and every `_CANCEL`
  complement of `WA_AI_PRODUCTION_DEFAULT_air.txt` moved from `should_open_*` to `should_keep_*`;
  16 land maintenance-floor blocks; the purge pulse still writes its book from `should_open_*` (it
  IS the "was open" side of every Schmitt pair) but fires `AI_purge_*` only when no funder line is
  even kept. Reviewer MEASURED the wants/cap split equivalent to the old `should_build_*` for all
  18 arms by AST compare of HEAD against the tree.
- Impact analysis, changed protected behaviours (P3(a)/(e)): (1)
  `should_cancel_land_cas_for_carrier_power` now reads `should_keep_cv_cas_line`, so a carrier
  strike power whose carrier-CAS line is closed BY ITS CAP no longer gets the
  `equipment_production_factor id = cas = -1000` land-CAS denial of `[carrier-needs-config]`. That
  matches the OPEN state, which never carried it - the denial is for a power the archetype never
  gave a carrier CAS line, not for one that filled its decks - but it is a behaviour change and it
  is listed here rather than left to be found. (2) The Schmitt cap pair still reopens at 90 %, but
  a maintained line adds to the very park that must fall to reach the bar, so for a role with low
  attrition the reopen bar is now effectively unreachable and MAINTAINED is an absorbing state.
  Accepted: the floor is the point, and the weight staying at 0 is what the reopen bar guards.
- Carrier roles: the deck-derived `1 + 4` ladder of `WA_AI_PRODUCTION_DEFAULT_cv_plane.txt` stays
  gated on the line being OPEN, and a cap closure hands the role to a separate ONE-factory floor
  behind the same `[equipment-selection]` saturation brake. A first pass ungated the ladder itself
  and `wa-lessons-reviewer` returned CONFLICT on it, correctly: min-factories is need-blind and
  additive (Fix 66 / R43), and for a big fleet the brake bar sits far above the park cap - fighters
  cap 2000 vs bar 3510 at 20-39 hulls (1510 planes of headroom) and vs 5400 at 40+ (3400); naval
  bombers 1800 vs 2340 (540) and vs 3600 (1800). DERIVED at 5 factories that band takes ~8 years to
  cross, i.e. the rest of the campaign with the engine's own deck demand already at zero - the exact
  Fix 66 failure mode. At 1 factory it is +114 planes over three years and no bar is ever reached.
- **Park trajectory, the number instead of the adjective (P3(f))** - full table with its inputs in
  scratchpad `air_maintenance_floor_trajectory.md`. MEASURED `POWERED_FACTORY_SPEED_MIL = 2.5`
  IC/day (`05_defines.lua:192`, `BASE_FACTORY_SPEED_MIL` is 0), so 1 factory = 76 IC/month at 100 %
  efficiency. DERIVED park growth above the cap at the DEEP (5-factory) floor, t+12 / t+36 months,
  no attrition: fighter +190/+570 (+11 % of cap), cas +190/+570 (+19 %), heavy fighter +127/+380
  (+13 %), tactical +109/+326 (+16 %), strategic +67/+202 (+7 %), naval bomber +190/+570 (+38 %),
  **scout +127/+380 (+253 %)**, **transport +217/+652 (+326 %)**; carrier roles at their 1-factory
  floor +38/+114 (+6 %). The six combat roles are a replacement rate. Scout and transport are not:
  their caps are 150 and 200 and neither role takes attrition, so the cap stops binding for the
  rest of the campaign. Shipped as ruled ("tous les types") with the end-state numbers recorded at
  the code site; the one-line exception (drop their two `_large` blocks, transport base 2 -> 1) is
  written out in the scratchpad file and NOT applied.
- ASSUMED and NOT verified: that newly produced planes reach the EXISTING wings rather than sitting
  in the stockpile. If the engine does not refit a wing in place, modernisation only runs at the
  rate of wing turnover and the floor should be retuned or dropped. First thing to read on a save.
- Reviewers: `wa-lessons-reviewer` CONFLICT on the carrier ladder (fixed above, its two other
  required items - the trajectory table and the stale `cv_plane.txt` header - also applied);
  `wa-architecture-reviewer` CONCERNS, all six required items applied (floor total no longer
  re-typed as a literal in the harness, the harness no longer prints a factory expectation it
  cannot honour for the two documented deviations, this impact line, the carrier headroom numbers,
  the dated ruling stripped from the code comment, and the `[air-maintenance]` comment slug renamed
  to `[air-budget]` - this subject owns the work, no new subject opened).
- Checkers green: `check_ai_layers` 0 ERROR (the industry band moved out of the `ai_strategy`
  enable blocks into `should_deepen_<type>_maintenance` to keep LAYER4-RAW-GATE at 0),
  `check_constants` 0, `check_worklist` 0.
- Verification (maintenance floor): `event wa_airb.4 <TAG>` after a COLD boot on a save where a
  park is at its cap (USA or ENG fighters 1943-44 in `2ee8a4ba` are the known cells) must read
  `maintenance-disjoint=1`, `lines: f=0` with `maint: f=1` for that country, and `floors:
  fighter=2` (deep gate armed). In the production tab that country must show a small non-zero
  fighter factory count instead of 0. Harness section G is the new probe; the verdict line now
  carries FIVE values, all of which must read 1 - G1 and G3 restate terms the maintain triggers
  already assert and only catch a deletion, G2 re-derives the role set from the section C walk.
- **Campaign `2ee8a4ba` scored 2026-09-09 (133 saves 1936.2-1947.2, instrumented build, owner
  report HTML).** Decision side PASS: GER 1939-41 `wa_tlm_air_w_fighter_pct` 40/40/40/48/48, floor
  live, `air_emit_n` ≤ 41 on every major. **Factory side FAIL**: from the saves' military_lines
  (MEASURED) GER air factories on fighters 31 % (1939.1), **19 %** (1939.9), 22 % (1940.1), 50 %
  (1940.7), 22 % (1941.1), 31 % (1942.1) against a 40-48 % weight share - the original symptom
  survives on the factory axis. DERIVED: factories per weight point GER = fighter 0.32, cas 0.30,
  tactical 1.6-2.7, heavy 0.4; IC cost explains x1.7-1.8 of it (MEASURED evaluator medians:
  tactical 32-46 IC vs fighter 18-29, strategic x2.4-2.7); the rest is the engine's allocation
  (ASSUMED deficit/loss-driven - USA 1943.1 shows the inverse, tac 0.45 per point). Cap closures
  MEASURED: USA 0 fighter factories 1944.1-1945.1 (park 9214-10100 vs reopen 9000), ENG 0 for
  1943 (park 4827 vs 4500), GER 0 air factories at 1943.1 (13000 planes, bases full - engine pool
  0, ASSUMED). Anomaly: SOV 12000 naval bombers by 1947.2 (0 in 1946.6, war with JAP 1946.3,
  naval book 10 at 1946.7) against `naval_cap` 2000 - ASSUMED the `has_deployed_air_force_size
  size < constant:` form does not read the bar; `event wa_airb.5 SOV` (new cap probe) on the
  1947.2 save is the killing read before any cap retune. USA held 1 carrier fighter until 1943
  (rung `usa_cv_fighter_3`, Q2 "rung wins"). Full tables and five proposals (cost-corrected
  weights f60/cas38/tac24/strat15/nav10/hf10, industry-scaled caps, 80 % reopen or a maintenance
  weight at cap, a 1-factory deck fallback, the cap probe): scratchpad
  `air_campaign_2ee8a4ba.md`. Not closed; owner decisions pending.
- **SOV 12000 naval bombers DIAGNOSED 2026-09-09 - the cap was never the fault.** MEASURED (9
  monthly saves of `2ee8a4ba`): flag `WA_AI_PRODUCTION_AIR_open_naval_bomber` present 1946.6/.7/.8,
  ABSENT 1946.9 on, and `wa_ai_air_budget_naval` 10 -> 0 by 1946.9. A country flag set without
  `days` never expires, so its disappearance IS the `else_if` of `WA_production_strategy_effects.txt:167`
  firing - the Schmitt cap bound at the 2000 bar while the park was between 1000 and 3100.
  **The standing `ASSUMED the has_deployed_air_force_size size < constant: form does not read the bar`
  is REFUTED**; `size <` is a vanilla form (install `common/decisions/GER.txt:13076`) and `constant:`
  in that field was already a validated context. MEASURED cause instead: 287 factories stayed on 5
  `SOV_il_10t_airframe` lines and drained 287/250/194/124/63/3 over five months (89 further 100-plane
  wings), efficiency climbing monotonically 17 % -> 110 % - never cancelled. POSITIVE CONTROL,
  MEASURED: the archetypes that carry a `_CANCEL` block are DELETED from the save within one month of
  the same edge (USA fighters 1943.12->1944.1, 116 factories at 91-97 % -> line absent; ENG 1944.5->1944.6,
  53 -> absent with total air factories unchanged 147->148; ENG reopens 1944.10 at efficiency 9.00 =
  engine base). So the 5-month drain is not engine behaviour. Script line:
  `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_air.txt:244` - `WA_AI_PRODUCTION_air_line_naval_bomber`
  had no `_CANCEL` twin, so after closure the archetype's net production factor was 0 (SOV leads
  COMINFORM, MEASURED, so the `-100` of `ENG_allies_we_dont_want_your_planes` never applied). FIX
  SHIPPED: one additive block `WA_AI_PRODUCTION_air_line_naval_bomber_CANCEL` (`-1000`
  `equipment_variant_production_factor` on `small_naval_bomber_airframe`, enable = the exact
  complement of the funder). No constant retuned. Only funder MEASURED by grep: the funding block
  itself (`:248`/`:249`) plus the category block (`:327`), both aborting on the same trigger; no
  country file adds `min_factories naval_bomber`. Cadence table for the new cycle - t0 decision flips
  at the cap (engine cadence, ASSUMED daily); t1 next ~2-day pulse, purge book clears AND the CANCEL
  arms, MEASURED bound on the fighter control = line gone within <= 1 month; t2 next monthly pulse,
  naval weight retired; t3 park attrites below the 1800 reopen bar, line reopens at efficiency 9.00
  and climbs the whole curve again. **Flapping at the bar is therefore NOT covered by this fix**, and
  the earlier proposal from the same scoring - "80 % reopen or a maintenance weight at cap" - STANDS
  unrefuted: it addresses the reopen cost, this block addresses the overshoot after closure. Two
  reviewers returned CONCERNS, none CONFLICT; both concerns applied (header no longer claims the purge
  cannot cancel - only that purge-alone did not; no `equipment_production_factor` second lever, the
  category block already withdraws on the same edge). Known-unfixed, same gap, NOT touched:
  `cv_small_naval_bomber_airframe`, `medium_fighter_airframe`, `small_bomber_airframe`,
  `large_bomber_airframe`/`large_heavy_bomber_airframe`, `transport_plane_equipment` carry no `_CANCEL`.
  `documentation/WA_AI_AIR_PRODUCTION.md` sections 2 and 5 corrected (they asserted the purge book
  cancels running lines). Caveat on the control, stated: both control countries are FIGHTERS, which
  have a substitute archetype the land naval bomber lacks. Owner run owed: `event wa_airb.5 SOV` on the
  1947.2 save after a COLD boot - now a confirmation, not the blocking read (expected
  `below-cap(constant)=0 below-2000(literal)=0 above-2000(literal)=1 should_build_naval=0`); a
  disagreement between the constant and literal columns would reopen H1. Full tables: scratchpad
  `sov_naval_bomber_2ee8a4ba.md`.
- State: phases 1-4 committed; harness runs pasted below for GER / ENG / MAL / USA on the
  pre-retune constants. One `event wa_airb.4 USA` on the 50/50 + naval 10 constants (cold boot)
  moves this to TESTED; phase 0b remains optional. Phase 5 (2026-09-09): TLM family
  `WA_TLM_air_*` (standing, v36 - `documentation/WA_TLM_TELEMETRY_SYSTEM.md` §6g), the counter
  `WA_TLM_air_emit_n` written by the 18 emitters, the closing criterion re-stated on it. Boot
  test owed (WA_TLM_core.txt touched: a parse fault there silences every telemetry family).
- Owner order 2026-09-09 ("je veux une refactorisation du système de production aérien pour l'IA
  ... on veut par exemple que la somme des usines allouées sur les chasseurs fasse au moins 40 % du
  total des usines aériennes ... une IA chasseurs + cas doit faire du 60/40"). Intended behaviour:
  every AI's air factories are split between the air TYPES it is allowed and able to build by a
  declared weight per type, renormalised over the OPEN types, with a fighter floor; the archetype
  inside a type is a parity choice; a tech rung the AI should not fund is declared in one registry.
  Full plan (diagnosis, model, phases, decisions): session scratchpad `PLAN_air_production_refactor.md`,
  to be moved to `documentation/WA_AI_AIR_PRODUCTION.md` with phase 3.
- Symptom, MEASURED (script, `common/ai_strategy/World_Ablaze_production_air_strategies.txt`): three
  stacked levers, none normalised - `unit_ratio` (fighter 300 vs cas 80 / heavy_fighter 130 /
  `interceptor` 100 / tactical 80+40+40 / naval 10 / strategic 150), `equipment_production_factor`
  (fighter **25** vs every bomber category **100**), `equipment_variant_production_factor` (55-200 per
  airframe). DERIVED: GER with every line open gets 300/780 = 38 % of wanted planes, then
  38 x 1.25 vs 62 x 2 = **28 % of air factories** - the owner's "20 % chasseurs / 80 % bombardiers".
  MEASURED: the heavy-fighter block writes `unit_ratio id = interceptor` while `medium_fighter_airframe`
  is `allowed_types = { heavy_fighter }` - a ratio on no airframe. MEASURED: lines open on
  `WORLD_ABLAZE_PRODUCTION_*` flags set by a ~2-day event and close by `AI_purge_*` flags read in
  `can_be_produced` (cancels running lines); tanks and navy read triggers in `enable`.
- Engine model, MEASURED (`common/ai_strategy/documentation.info` § UNIT RATIOS / AIR): a land air
  type's share = `unit_ratio / sum(land unit_ratio)` x wanted planes, no base 100; carrier planes a
  separate pool. So integer weights emitted at runtime give exact shares; the model is the armour
  budget (`WA_AI_ARMOR_BUDGET_reconcile`, meta_effect emitters, books + diff).
- Decisions (owner 2026-09-09): Q1 `heavy_fighter` is its own type and the ATTACKER archetype
  belongs to it, not to cas - MEASURED over every `ai_equipment` plane design (evaluator
  `StatModel`, 35 attackers / 37 heavy fighters / 75 CAS): air_attack per IC 1.91 vs 1.90 vs 1.14,
  ground_attack per IC 0.52 vs 0.30 vs 0.69, and every `ai_equipment` file already files attackers
  under `air_heavy_fighter`. Q2 two closures: HARD (archetype not allowed / tech not worthwhile /
  BoB / bases lost) keeps the `can_be_produced` purge; CAP (park saturated) = weight 0 + hysteresis
  (reopen at 90 % of the cap), no purge - conditional on phase 0b. Q3 weights fighter 60 / cas 40 /
  tactical 40 / strategic 40 / naval 20 / heavy_fighter 15, fighter floor 40 %; Q4 fighter
  archetypes at parity; Q5 `air_factory_balance` tag+date blocks stay out of scope (separate subject
  `air-share-windows`); Q6 monthly reconcile.
- Phases: **0** owner console measurements - (a) is `add_ai_strategy unit_ratio` additive per id
  (BLOCKING for phase 3), (b) does weight 0 / `-1000` drain a running line, (c) `imgui show
  ai-strategy` GER 1939 effective ratios; **1** `tools/air_tech_registry.json` +
  `tools/gen/gen_air_tech_gates.py` generating `WA_AI_PRODUCTION_air_tech.txt` (semantic diff empty
  first, then the evaluator reads the registry's exclusions); **2** flags -> `_is_open` triggers,
  values unchanged, heavy-fighter id fixed, `check_ai_layers` debt DOWN; **3** reconcile
  `WA_AI_AIR_BUDGET_reconcile` + constants + lever parity + harness `WA_TEST_air_budget`;
  **4** carrier pool; **5** TLM probe + campaign.
- **Phases 1 + 2 in the working tree 2026-09-09 (uncommitted at the time of writing).** Phase 1:
  `tools/air_tech_registry.json` (127 tree entries, every id verified against `common/technologies/`)
  + `tools/gen/gen_air_tech_gates.py` (`--check` exit 0; the rendered file's has_tech SETS are
  identical to HEAD, 17/17 triggers, MEASURED by set comparison); the evaluator reads
  `exclude.airframes` as forced KEEP_OLD (`registry_excluded` flag; list empty until a model is
  named). Phase 2: `WA_AI_PRODUCTION_should_open_<line>_line` x17 + `should_run_bob_programme` +
  `should_cancel_land_cas_for_carrier_power` (end of `WA_AI_PRODUCTION_air.txt`); new
  `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_air.txt` (line blocks, values unchanged);
  `World_Ablaze_production_air_strategies.txt` trimmed to the `air_factory_balance` blocks; the
  pulse effect rewritten as purge books (`WA_AI_PRODUCTION_AIR_open_<archetype>` country flags).
  Three deliberate deviations from value-neutral: (a) heavy-fighter ratios move from the DEAD id
  `interceptor` to `heavy_fighter` (min_factories 10 becomes live, same as the mutually exclusive
  attacker line); (b) carrier CAS gets `AI_purge_cv_small_bomber_production` (`plane_airframes.txt`
  cv block) instead of sharing the land flag - closing one no longer cancels the other; (c) a
  fighter-mode switch no longer purges the archetype the country keeps; (d) (architecture review)
  HEAD re-set both land-fighter purge flags on EVERY pulse while no fighter line qualified (the
  `else` of the trio) - the edge purge alone would have left the engine free to run fighter lines
  there, so `small_fighter` / `small_fighter_multirole` now carry a CANCEL block (-1000 while no
  line funds them), the same denial without the cancel-per-pulse; (e) (lessons review, "two
  states of one object") fast / strike / tactical each read ONE purge key now
  (`plane_airframes.txt`: the shared `medium_bomber` / `medium_multirole` second key removed from
  each pair) so a book cancels its own archetype only - HEAD's jet-tactical veto closed fast+strike
  and its purge cancelled the still-open tactical line, and the BoB close of tactical cancelled
  fast+strike. Guard added (lessons "absent variable reads 0"): `should_build_bob_fighters` requires
  `has_variable = WA_AI_PRODUCTION_land_fighter_park`, so a fresh load or a human->AI switch does
  not run the BoB programme (which closes every bomber line) before the first pulse writes the park.
  Cadence, DERIVED for a line that flips between pulses (pulse = MTTH 2 d on `is_ai`, 7 d under
  `WA_AI_delay`; `enable` ASSUMED daily): t0 decision flips closed -> the block disables the same
  day (engine cadence), no purge yet; t1 next pulse (expected 2 d, 7 d in performance mode) -> book
  clears, purge fires, the running line is cancelled; t2 next pulse -> nothing. Open direction: t0
  block enables the same day, the line starts at the engine's own pace; t1 book set, no purge.
  Worst case = a line cancelled up to one pulse late, never early. Out of subject, recorded:
  `WA_AI_stop_air_production` (`WA_AI_misc_effects.txt`) is write-only on HEAD as well - no reader
  in the old flag ladder either (MEASURED `git show HEAD:` grep). Pre-existing, not moved:
  `should_build_bob_fighters` keys on `fall_of_france` / `REN` / `GER` (principle 1 debt, already
  in the trigger file at HEAD). One-shot on a save from a HEAD build
  (DERIVED): orphaned `WORLD_ABLAZE_PRODUCTION_*` flags stay unread; a line that closed between
  builds has no book and gets no purge - it runs to its end or to its CANCEL -1000; from the
  second pulse everything is edge-normal. Gates: `check_ai_layers`
  0 ERROR, ratchet unchanged (the new DEFAULT file reads only `_should_` triggers);
  `check_constants` clean; `check_worklist` clean. Pre-existing, unrelated: pytest
  `test_usa_medium_is_the_canonical_regression` fails on HEAD too.
- Harness: `common/scripted_effects/WA_TEST_air_budget.txt` + `events/wa_test_air_budget.txt`
  (contract v1). `event wa_airb.3 GER` (runs the pulse, then reports), `wa_airb.2` for every AI
  major. Section C re-derives the 17 lines from the wants + retyped bands; VERDICT
  `lines-match-walk=1 books-match-walk=1`.
- **Owner boot + console run 2026-09-09 ("boot start OK"), GER 1940.10.1, cold boot (game.log pasted):**
  ```
  scope : always=1  I-am-ROOT=1  I-am-THIS=1  ROOT-scope-usable=1  control-false=0
  inputs: is_ai=1  mils=454  park(resum)=3624  park(var)=3624  bob_flag=0  own_air_arm=1
  wants : f=1 mr=0 int=0 hf=1 att=1 cas=1 cvcas=0 fast=1 strike=1 tac=1 nav=1 strat=0 scout=1 cvf=0 trn=0 bob=0
  vetoes: jet_fighter=0 jet_tac=0 delayed_strat=0 after_1941_6=0
  lines : int=0 f+mr=0 f=1 mr=0 cas_low=0 cas=1 cvcas=0 hf=1 att=0 fast=1 strike=1 tac=1 nav=1 strat=0 scout=1 cvf=0 trn=0
  walk  : int=0 f+mr=0 f=1 mr=0 cas_low=0 cas=1 cvcas=0 hf=1 att=0 fast=1 strike=1 tac=1 nav=1 strat=0 scout=1 cvf=0 trn=0
  books : int=0 f=1 mr=0 cas=1 cvcas=0 hf=1 att=0 fast=1 strike=1 tac=1 nav=1 strat=0 scout=1 cvf=0 trn=0
  VERDICT German Reich: lines-match-walk=1 (mismatches 0)  books-match-walk=1 (mismatches 0)  purges-armed=0
  ```
  MEASURED: the shipped decisions, the independent walk and the purge books agree on all 17
  lines; the attacker line yields to the open heavy-fighter line as designed; the park variable
  equals its re-sum (the `has_variable` guard was live).
- **Same run, ENG 1940.10.1 (Battle of Britain) and British Malaya (control), game.log pasted:**
  ```
  ENG  inputs: is_ai=1  mils=187  park(resum)=700  park(var)=700  bob_flag=1  own_air_arm=1
       wants : f=1 mr=1 int=0 hf=0 att=0 cas=0 cvcas=0 fast=0 strike=1 tac=1 nav=1 strat=0 scout=0 cvf=0 trn=1 bob=1
       vetoes: jet_fighter=0 jet_tac=0 delayed_strat=1 after_1941_6=0
       lines : int=0 f+mr=1 f=0 mr=0 cas_low=0 cas=0 cvcas=0 hf=0 att=0 fast=0 strike=1 tac=0 nav=0 strat=0 scout=0 cvf=0 trn=0
       walk  : (identical)   books : int=0 f=1 mr=1 cas=0 cvcas=0 hf=0 att=0 fast=0 strike=1 tac=0 nav=0 strat=0 scout=0 cvf=0 trn=0
       VERDICT United Kingdom: lines-match-walk=1 (mismatches 0)  books-match-walk=1 (mismatches 0)  purges-armed=0
  MAL  inputs: is_ai=1  mils=0  park=0/0  bob_flag=0  own_air_arm=0   wants/lines/walk/books: all 0
       VERDICT British Malaya: lines-match-walk=1 (mismatches 0)  books-match-walk=1 (mismatches 0)  purges-armed=0
  ```
  MEASURED: the BoB programme closes tactical, naval and transport while their wants read 1, the
  fighter+multirole line stays open, the fighter book carries both archetypes; the minor with no
  own air arm reads every line 0 (patron control). Observation, pre-existing and out of this
  phase: the strike line is NOT closed by the BoB programme (HEAD's flag ladder never gated fast /
  strike on it either) - ENG keeps a strike-bomber line through the battle; the phase-3 weights
  are where that gets decided. Still owed: USA 1942+ (carrier lines).
- **Phase 0a MEASURED 2026-09-09 (owner console, GER 1940.10, cold boot):** `unit_ratio fighter`
  read 300; `effect WA_TEST_AIRB_probe_ratio_add` (+50) -> 350; `_probe_ratio_sub` (-50) -> back
  to 300 ("sub marche aussi"). `add_ai_strategy unit_ratio` is additive per id in both directions:
  the book-and-diff reconcile is buildable. Phase 0b (drain by -1000) not run yet - Q2(b) stays on
  the purge for cap closures; hysteresis on the reopen bar ships with phase 3 regardless.
- **Phase 3 in the working tree 2026-09-09 (uncommitted).** `WA_AI_AIR_BUDGET_reconcile`
  (`common/scripted_effects/WA_AI_PRODUCTION_air_budget.txt`; monthly after the armour reconcile +
  on_startup): open types from the `should_open_*_line` decisions -> table weights (script constants
  `air_budget`: 60/40/40/40/20/15, fighter floor 40 %) -> diff vs books `WA_AI_AIR_BUDGET_<type>` ->
  `add_ai_strategy unit_ratio ±delta` through meta_effect (the armour emitter form). The 13 static
  land `unit_ratio` lines left `WA_AI_PRODUCTION_DEFAULT_air.txt`; category factors and funded
  archetype factors are at parity 100 (fighter was 25 - the measured 20/80 lever); heavy-fighter
  `min_factories` 10 -> 1. Carrier-pool ratios untouched (phase 4). Hysteresis: every park cap now
  a Schmitt pair (close at cap, reopen at the `_reopen` bar = 90 %, 16 new constants) read through
  the purge books. Doc: `documentation/WA_AI_AIR_PRODUCTION.md`. Harness section E re-derives the
  weights from the walk and compares them to the books (`budget-match-walk`), `event wa_airb.4`
  runs pulse + reconcile first. Gates: `check_constants` clean (all 23 new constants read),
  `check_ai_layers` 0 ERROR ratchet unchanged, `check_worklist` clean. Owner runs owed:
  `wa_airb.4 GER` 1939-41 (expect f=60 cas=40 tac=40 nav=20 hf=15, fighter_share 34 % -> floor
  raises f to 77 -> 40 %), `wa_airb.4 ENG` in the BoB (expect fighter only), USA 1942+. TLM probe
  `wa_tlm_air_*` deferred to phase 5: the books are country variables, already save-visible.
- Reviews on phase 3 (architecture CONCERNS, lessons CONCERNS), all applied: (1) the category
  factor is ONE block per TYPE (`WA_AI_PRODUCTION_air_category_<type>`, enabled by new
  `WA_AI_PRODUCTION_should_fund_<type>_type` decisions that the reconcile reads too) - factors of
  one id SUM across enabled blocks, so per-line factors gave three open tactical lines 300 against
  fighters 100, the skew coming back by another door; (2) the Battle of Britain bar is a Schmitt
  pair the other way round (engages under `bob_fighter_cap_reopen` 4500 / `_sov_gone_reopen`
  7200, releases at the cap, read through `WA_bob_production_flag`); (3) doc §6 carries the
  entry-accumulation bound (6/month/country), the three unpaired decision inputs (patron, mil
  band, jet vetoes) with the t0-t4 walk, and the save fingerprint; (4) `armor-prod-category`
  carries a baseline re-cut line (fighter factor 25 -> 100 raises the air pull vs `armor` 60 -
  stated regression risk, no counter-term chosen: the level 100 is what every bomber line
  already carried); (5) `cv_cas` / `cv_fighter` category factors noted as outside
  `script_enum_equipment_category` (ASSUMED no-op) so phase 4 does not inherit them as a lever;
  (6) comment tells added (additivity gone = log weights differ from `imgui`; purge books written
  by the pulse only; `fighter_floor_pct` < 100).
- **Owner console run 2026-09-09, `event wa_airb.4 ENG`, 1939.9.1, fired twice (game.log pasted):**
  ```
  scope : always=1  I-am-ROOT=1  I-am-THIS=1  ROOT-scope-usable=1  control-false=0
  inputs: is_ai=1  mils=120  park(resum)=200  park(var)=200  bob_flag=0  own_air_arm=1
  lines : int=0 f+mr=1 f=0 mr=0 cas_low=0 cas=0 cvcas=0 hf=0 att=0 fast=0 strike=1 tac=1 nav=1 strat=0 scout=0 cvf=0 trn=1
  budget: expect f=60 cas=0 tac=40 strat=0 nav=20 hf=0 floor=0 fighter_share=50%
  budget: books  f=60 cas=0 tac=40 strat=0 nav=20 hf=0
  VERDICT United Kingdom: lines-match-walk=1 (mismatches 0)  books-match-walk=1 (mismatches 0)  budget-match-walk=1 (mismatches 0)  purges-armed=0
  ```
  MEASURED: three open types (fighter, tactical, naval), books = re-derived weights, floor not
  needed (60/120 = 50 % > 40 %); the second firing reads the same books (idempotent, no
  re-emission).
- **Engine-side MEASURED 2026-09-09 (owner `imgui show ai-strategy`, 1940.10 save, screenshots):**
  GER `unit_ratio`: convoy 15, fighter **77**, cas 40, tactical_bomber 40, naval_bomber 20,
  heavy_fighter 15 - the floor case exactly as derived (others 115 -> 77 -> 40 %). ENG (in the BoB):
  fighter 60, tactical_bomber 40 (the strike line is not BoB-gated), no naval entry (BoB closed it),
  plus the static carrier rows cv_fighter 150 / cv_cas -1000 / cv_naval_bomber 100 from
  `WA_AI_PRODUCTION_DEFAULT_cv_plane.txt`. Phase 3 verified script-side (harness) and engine-side.
  **Phase 4 finding, DERIVED from that ENG row**: the carrier base block puts cv_cas at -1000 for
  every carrier navy while the USA cv_cas line adds +80 -> net -920: the carrier strike power never
  gets a carrier-CAS share. Pre-existing; the carrier reconcile replaces both.
- **Phase 4 in the working tree 2026-09-09 (owner order "pars phase 4").** The carrier pool joins
  the reconcile (section 4, three books `WA_AI_AIR_BUDGET_cv_*`, six emitters): weights
  `cv_weight_fighter 60 / cv_weight_cas 30 / cv_weight_naval_bomber 40`, a type funded while the
  country holds a deck (`WA_AI_PRODUCTION_needs_cv_planes`) AND its line is open
  (`should_fund_cv_<type>_type`; carrier naval bombers ride the naval-bomber line). Removed: the
  static `WA_DEFAULT_production_carrier_planes_base_ratios` block (150 / 100 / -1000) and the
  `cv_cas 80` / `cv_fighter 80` lines of the two carrier line blocks - the -920 net is gone. The
  deck-gated min-factory floors of `cv_plane.txt` are untouched (volume lever, saturation brake).
  Observation, pre-existing, owner ruling `[carrier-needs-config]` kept: a carrier navy outside
  the archetype (ENG) has its cv fighters CANCELLED (-1000 variant factor) yet still gets the
  2 / 5 factory floors - the two levers disagree; not changed here. Harness section F
  (`cv-budget-match-walk`, VERDICT 4 values). Expected on the 1940.10 save: ENG cvf=0 cvcas=0
  cvnav=40 (naval closed by the BoB -> cvnav=0 during the battle); USA 1942+ cvf=60 cvcas=30
  cvnav=40; GER decks=0 -> all 0. **Regression risk stated (principle 3e)**: a carrier navy
  outside the archetype (ENG) loses its cv_fighter POOL share - the static block gave it
  150/250 = 60 % of its deck-sized pool, the archetype-gated type gives 0 - so only the 2/5
  deck-gated floors feed its carrier fighters. Signal on the next scored campaign: ENG
  carrier-fighter wing fill and the `imgui show ai-strategy` cv rows; if ENG decks run empty, the
  fix is the archetype (`WA_AI_CONFIG_is_carrier_navy`), not this emitter. Lessons review
  corrected the wording: this is NOT "unchanged" - MEASURED at HEAD the static block gave ENG
  cv_fighter 150 / cv_naval 100 (60 % fighters); phase 4 gives it 0 / 40 (100 % naval bombers,
  the ENG waste shape of f9321934). **Q8 for the owner**: (a) fund cv_fighter for EVERY deck
  holder whose carrier-fighter tech is worthwhile (weight while `needs_cv_planes` and
  `has_worthwhile_cv_fighter`, archetype keeps only the purge/CANCEL), or (b) keep the archetype
  gate and drop the deck-gated floors so one lever decides, or (c) as shipped (ENG fighters on
  the 2/5 floors alone, ASSUMED a floor builds through the -1000 CANCEL - phase 0b measures it).
  Recommendation: (a) - a deck without fighters is the measured failure, and the archetype was
  written to stop UNASKED carrier lines, not to starve existing decks. Cadence of the deck gate
  (DERIVED, monthly): t0 last deck sunk day 5 -> engine pool 0 at once (deck-sized), stale
  weights move no factory; t1 monthly pulse -> -60/-30/-40 emitted, books 0; t2 new deck ->
  engine pool > 0 at once, split re-emitted at the next monthly pulse (<= 30 d with no split, the
  floors cover it). HEAD's static block was engine-cadence; the lag is new and bounded by one
  pulse. `carrier_planes.txt` header re-derived: the saturation bars now sit at 2-4x the deck
  slots (less braking, conservative). ASSUMED and to close on the USA 1942 `imgui` read: land
  and carrier pools separate (doc-sourced only) - the land `fighter` row must not move when the
  cv rows appear.
- **Q8 = (a), owner 2026-09-09.** `WA_AI_PRODUCTION_should_build_cv_fighters` reads
  `WA_AI_PRODUCTION_needs_cv_planes` (holds a deck) instead of `WA_AI_CONFIG_is_carrier_navy`:
  a deck holder with a worthwhile carrier-fighter rung opens the line, gets the weight, keeps
  the floors, and its `cv_small_fighter` CANCEL / purge follow the same decision - one lever.
  Carrier CAS keeps the carrier-strike-power archetype. `WA_AI_CONFIG_is_carrier_navy` loses its
  only production reader (other readers listed by grep at the time of the change, see commit).
- **Owner console run 2026-09-09, `event wa_airb.4 USA` 1942.11.1 (game.log pasted):** land pool
  PASS - `expect f=77 cas=0 tac=40 strat=40 nav=20 hf=15 floor=1 fighter_share=40%`, books equal,
  `imgui` rows fighter 77 / tactical 40 / strategic 40 / naval 20 / heavy_fighter 15 (cas 0 =
  carrier strike power, no land CAS line: correct). Carrier pool read **0 everywhere** with
  `decks=1` and the cvf / cvcas lines open - both the harness EXPECT (constants x walk) and the
  books. DERIVED cause: the `cv_weight_*` constants read 0 in that session while the land
  `weight_*` (loaded at the earlier boot) read fine, and the harness's new section F was present
  - the shape of a `reload`/`reloadfile` of the effect files without a restart: script constants
  are not re-read by it (lessons: hot reload). MEASURED on disk: the three constants sit inside
  `air_budget`, LF, no BOM, `check_constants` clean. CONFIRMED: `logs/game.log` shows the cold
  boot at 12:44, after the 12:39 run, and `common/script_constants/documentation.md` states
  "reloading the script database is not enough to propagate the constants" (MEASURED, engine doc).
- **Owner console run 2026-09-09 after the cold boot, `event wa_airb.4 USA` 1942.9.7 (pasted):**
  ```
  budget: expect f=77 cas=0 tac=40 strat=40 nav=20 hf=15 floor=1 fighter_share=40%   books equal
  carrier: decks=1  expect cvf=60 cvcas=30 cvnav=40  books cvf=60 cvcas=30 cvnav=40
  VERDICT United States of America: lines-match-walk=1  books-match-walk=1  budget-match-walk=1  cv-budget-match-walk=1  purges-armed=0
  ```
  Phase 4 PASS script-side: the carrier pool is emitted from the deck x line gates; the land
  fighter weight stayed 77 with the cv books present. Owed: the `imgui` read of the USA cv rows
  (cv_fighter 60 / cv_cas 30 / cv_naval_bomber 40, land `fighter` still 77 = the pool-separation
  ASSUMPTION closed engine-side) and one ENG run (Q8a: cvf=60 expected outside the BoB).
- **Q9, owner 2026-09-09 ("pourquoi l'usa veut faire des cv cas ? ... jamais si pas configurée
  explicitement" -> option 2):** `WA_AI_CONFIG_AIRFORCE_is_carrier_strike_power` is now
  `always = no`. MEASURED before: the archetype named the USA (`WA_AI_CONFIG.txt:361`, carried
  by `dcfe18a8` from the old tag-gated `WA_usa_cas_strategy`), and the static `cv_cas -1000` of
  `cv_plane.txt` masked it (net -920), so the config never produced a plane the owner could see;
  phase 4 removed the mask and the config surfaced. Consequences (DERIVED): no AI opens the
  carrier-CAS line or gets a cv_cas weight (CANCEL -1000 stays on everywhere); the USA gets no
  land CAS either (`should_build_cas` needs `cas_is_strong` or no worthwhile multirole - the USA
  has multiroles); the `naval_cap_carrier` 1800 ladder branch is unreachable, the USA reads
  `naval_cap` 2000. The archetype stays declared so naming a nation is a one-line change.
  Expected on re-run: USA `cvcas=0` in wants, lines, books and `carrier:` (cvf=60 cvnav=40).
- **Engine-side MEASURED 2026-09-09 (owner `imgui`, USA 1942, after Q9, screenshot):** `unit_ratio`
  rows convoy 100, fighter 77, tactical_bomber 40, strategic_bomber 40, naval_bomber 20,
  cv_fighter 60, cv_naval_bomber 40, heavy_fighter 15 - no cv_cas row (Q9 live), the land rows
  unchanged next to the cv rows. Phase 4 verified engine-side; land/carrier pooling inside the
  engine stays doc-sourced (the rows are separate entries, what the engine sums is not visible).
- **Owner screenshot 2026-09-09, ENG 1936 production lines (MEASURED): Hawker Nimrod 1/7,
  Fairey Swordfish 1/7, Gloster Gauntlet 2/9.** The 7 is the carrier FLOOR pair of
  `cv_plane.txt` (base 2 + carrier-major 5, additive, ENG > 3 hulls), and the Nimrod ran while
  its line was CLOSED (`eng_cv_fighter_3` rung not held: the floor forced a model the AI judged
  not worth a factory - the floor-vs-CANCEL contradiction recorded at phase 4). Change: the four
  floor gates (`WA_AI_PRODUCTION_carrier_planes_floor_* / _major_*`) now require the role's
  funded-type decision (deck x line open x tech x cap). Reviews (architecture CONFLICT on
  comments/doc, lessons CONCERNS) applied: (1) the carrier-fighter line block's own
  `min_factories 1` is gone, so the floors of `cv_plane.txt` are the whole floor - base 1 per
  role, carrier-MAJOR +6 (7) and the major bar moves from > 3 to > 9 hulls: both measured
  big-fleet cells (9be92c89 USA 35 hulls on 5, f9321934 USA 47 hulls on 8) ran EXACTLY on the
  old floor sum, so that sum is kept for fleets and denied to a 1936 navy with six decks;
  whether the engine's deck demand carries a fleet ABOVE the floor is ASSUMED (both cells read
  requested = floor) - killing read: a many-deck USA save with unfilled wings, requested vs
  floor sum on the production screen; (2) carrier naval bombers get their OWN want and line
  (`should_build_cv_naval_bombers` = deck x naval rung x `naval_cap_carrier` pair on the carrier
  archetype; `should_open_cv_naval_bomber_line` = not BoB) and their own purge key - the land
  naval line's `is_maritime_air_power` / oceanic-enemy / coast terms no longer govern a deck
  (a USA at peace had no carrier naval-bomber floor under the previous wiring);
  `AI_purge_small_naval_bomber_production` is the new LAND key (`plane_airframes.txt` land
  block), the cv key stays on the cv block; (3) Q2 decided: a deck holder below its carrier-
  fighter rung builds NO carrier fighters until the rung - the `[rung-1940]` ruling wins over a
  1-factory fallback (recorded, owner may overturn); (4) the harness `carrier:` line prints the
  four floor gates, the walk carries `cvnav` as its own line, VERDICT still 4 values; (5) doc
  §4: floor requests through the -1000 CANCEL is now MEASURED (the ENG screenshot), not ASSUMED.
  Signal: USA carrier-fighter wing fill on the next scored campaign (`cvair.py`). Expected on the
  ENG 1936 save after a cold boot: Nimrod 0 factories requested, Swordfish 1.
- **Owner retune 2026-09-09:** (a) carrier split 50 / 50 (`cv_weight_fighter 50`,
  `cv_weight_naval_bomber 50`) - "la composition IA des porte-avions", the cv unit_ratio also sets
  the AI's deck composition (`cv_plane.txt` header); (b) `weight_naval` 20 -> 10, land naval
  bombers halved. New expectations (DERIVED): GER 1940.10 others 105 -> f=70 (floor), nav=10;
  USA 1942 f=70 nav=10 cvf=50 cvnav=50; ENG 1939.9 f=60 tac=40 nav=10 (share 55 %). Constants
  changed = cold restart before the re-run.
- Phase 0 console procedure (owner, any 1939 save, observer tag): (a) `tag GER`, `imgui show
  ai-strategy`, note the `unit_ratio fighter` row; `effect add_ai_strategy = { type = unit_ratio
  id = fighter value = 50 }`; re-read; `effect add_ai_strategy = { type = unit_ratio id = fighter
  value = -50 }`; re-read - additive means the row returns to its first value (BLOCKING for phase 3).
  (b) on a GER save with a running tactical line: `effect add_ai_strategy = { type =
  equipment_variant_production_factor id = medium_heavy_bomber_airframe value = -1000 }`, `tag
  BHU` back (GER returns to AI), run 3-4 weeks, read the production screen: does the line lose its
  factories (drain) or is it untouched (then the purge stays for cap closures too). (c) `tag GER`
  1939.9, `imgui show ai-strategy`: paste every `unit_ratio` / `equipment_production_factor` /
  `air_factory_balance` row - the MEASURED baseline the phase-3 weights are calibrated against.
- Verification (campaign): `tlm <TAG>` -> `wa_tlm_air_w_fighter_pct` (the decision, exact),
  `wa_tlm_air_park_fighter` / `_park_bomber` (the effect, 6-month window), `wa_tlm_air_emit_n`
  (entry accumulation), `wa_tlm_air_types_open`; second signal `wa_ai_air_budget_<type>` (books)
  and the purge books `wa_ai_production_air_open_<archetype>` (a line whose block should be armed
  with no such flag = the pulse is not running). The share of air FACTORIES per type is read from
  the save's production lines by the analysis script (script cannot read it); it must match
  `w_fighter_pct` within the engine's own allocation noise.
- Closed when: on one scored campaign, GER 1939-1941 `wa_tlm_air_w_fighter_pct` in [40, 60] AND
  its fighter share of air factories (production lines) within [40 %, 60 %] on 3 consecutive
  monthly saves; USA and ENG strategic share >= 25 % after 1942.1; `wa_tlm_air_emit_n` < 200 on
  every country at the last save; `check_ai_layers` baseline lower than before phase 2 (DONE:
  306 -> 305).

### pc-lost-state-purge — PARKED (2026-09-09)
- Parked 2026-09-09 on the owner's order (admission of `air-budget`, WIP limit: 8 under OPEN for 4); move it back to OPEN in one line when its owed item lands. State at parking: TESTED 2026-09-08 (owner console run pasted); the only item owed is the campaign probe (`wa_tlm_pc_lost_n` > 0 on a side-switch) - nothing to do in a session until a scored campaign is read.
- Owner order 2026-09-08 ("corrige la purge"), from the ITA side-switch audit (campaign `6fcbbe0d`,
  1943.9 vs 1944.1). Intended behaviour: when a state changes hands to a party the old controller may
  not build through (not itself, not faction, not subject either way, not in its
  `WA_AI_PC_construction_permissions`), the old controller's priority-construction projects in that
  state are cancelled at once and counted in `wa_tlm_pc_lost_n`.
- Symptom, MEASURED: `wa_tlm_pc_lost_n = 0` on every country (all 66 tags) at 1944.1 after four
  years of war - the purge never fired for anyone. ITA keeps 5 non-rail projects (naval_base +
  3 supply_line in Libya 448/449/450, lost ITA -> FRA between 1943.6 and 1943.8; inf_resource in
  Veneto 160, RIT-held) at 0 factories, stall 10-13 wk, `active_nonrail = 5` = the `< 5` admission
  gate, so ITA admits no non-rail project. The state-side arrays ARE populated
  (`wa_ai_pc_projects_in_state_of_ita^0 = 13` on 448): the data was there, the read was wrong.
- Cause, DERIVED from the hook's own measured comment: in `on_state_control_changed`
  (`common/on_actions/WA_AI_misc_on_actions.txt`) the purge read
  `WA_AI_PC_projects_in_state_of_@FROM` and the permission tests `FROM = { ... }` INSIDE the
  `FROM.FROM = { }` state block, where FROM re-binds to the state (recorded 30 lines above for
  `sq_ctrl_reset_n`, local run BHU_1941_11_18_12). Array keyed by the state = empty = no cancel.
  Rival not killed: the hook itself never fires (ASSUMED engine; `sq_ctrl_reset_n` is 0 everywhere
  too, but it only counts a live TTL flag, so it does not discriminate). The console test below is
  what separates the two.
- Change (working tree, NOT committed): (1) the old controller is captured at the effect root
  (`set_temp_variable = { _pc_lost_old_ctrl_ = FROM }`) and every read goes through
  `@var:_pc_lost_old_ctrl_` / `var:_pc_lost_old_ctrl_ = { }`; the permission OR runs in the old
  controller's scope (`ROOT` = new controller never re-binds; reverse subject test is
  `ROOT = { is_subject_of = PREV }`); the cancel runs in the old controller's country scope.
  (2) `WA_AI_PC_end_project_by_id` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`) removes the state-side
  entry from `..._of_@PREV` instead of `..._of_@ROOT`: under this on_action ROOT is the NEW controller,
  so `@ROOT` would strip the new controller's same-numbered slot and leave the loser's entry behind;
  every other caller runs in the builder's scope where PREV == ROOT; the add site in
  `WA_AI_PC_start_project` uses the same `@PREV` accessor so the pair cannot desync. `@var:` in a
  `for_each_loop array =` / `check_variable ^num` is ASSUMED (proven in this repo for
  set_temp_variable and clear_variable only); `@PREV` is proven (AIFC / LANDING flags).
  (3) Resumed saves: state-side arrays already carry ids from the years the purge was dead (ITA on
  Libya today), and slot ids are recycled, so a stale entry could cancel a live project elsewhere.
  The purge therefore drops any entry whose slot `WA_AI_PC_target_state` is not this state and never
  cancels through it (idempotent clean-up at the only read site; no load-time migration). Architecture
  review CONFLICT (ROOT-keyed removal, silent regression, comment date) -> all three applied. Lessons
  review CONFLICT (same ROOT defect; `WA_AI_PC_construction_permissions` has NO writer - noted at the
  site, term kept; `PC CANCELLED` log printed `[Root.GetName]` = the conqueror -> now `[This.GetName]`;
  `WA_AI_PC_cancel_projects` header now says THIS = builder) -> all applied.
- Impact: callers of `WA_AI_PC_end_project_by_id` - core (6), this on_action (2), WA_TEST_railway (3)
  - all in builder scope. Readers of `projects_in_state_of_`: `WA_AI_PC_has_same_type_project_here`,
  the thair strategy, WA_TEST_railway 014. Tag-free, date-free: historical and ahistorical identical.
  Regression risk, STATED: a purge that now actually fires cancels paid-for projects in a state lost
  to an enemy - the intended behaviour since 2026-01-29, never exercised; the [rail-admission-churn]
  keep-paid rule does not apply here (same as before). Civil-war splits (Veneto -> RIT) may never
  reach this hook (ASSUMED engine) - out of scope, would need a periodic re-validation sweep.
- Console run 1, MEASURED (`pc_purge_test.hoi4`, 1944.1.3, Tripoli 448 ITA -> GER): hook FIRED,
  `@var:` array iteration and the `var:` effect scope WORK (the state-side entry `_of_ita^0 = 13` was
  removed), but nothing was cancelled (`pc_lost_n = 0`, project 13 still queued). The first-cut stale
  guard classified the live project as stale: it compared the state's `THIS.id` (engine-encoded) with
  the stored plain `WA_AI_PC_target_state` inside a `var:` block used as a TRIGGER scope - two rivals,
  one measurement, both removed: the classification now runs as EFFECTS in the old controller's scope
  (a state flag `WA_AI_PC_lost_here` set/cleared on the lost state, read by a scope walk through
  `var:WA_AI_PC_target_state^id`) and feeds two plain temps the `if` reads. That save's 448 bookkeeping
  is desynced by the run (entry gone, project kept) - re-test from a fresh load of `1944.1_Jan.hoi4`.
- Harness (contract v1, owner order "des effets pour pas que je fasse tout en console"):
  `common/scripted_effects/WA_TEST_pc_lost_purge.txt` + `events/wa_test_pc_lost_purge.txt`. From
  any tag on a FRESH load of `1944.1_Jan.hoi4`: `event wa_pclost.9 ITA` runs report, leg A (448
  Tripoli -> ITA -> an enemy, expect cancel), leg B (450 Benghasi -> ITA -> a faction member, expect
  nothing), leg C (160 Veneto -> ITA -> an enemy, expect cancel), report; each leg prints
  `expect cancelled=N` beside the three measured deltas and a `VERDICT: PASS|FAIL`. The legs use
  `set_state_controller`, so they also answer whether that effect reaches `on_state_control_changed`
  (ASSUMED yes; the console `setcontroller` run above proved the hook fires for that path).
- Harness run 1, MEASURED (2026-09-08 19:10, `1944.1_Jan.hoi4`, `event wa_pclost.9 ITA` from BHU):
  scope line 1 1 1 1 0 on all five blocks; report correct (13 queued, 5 of them on ground ITA does
  not control); legs A/C FAIL, B PASS - but every "after step 1" row still read the OLD controller
  (Tripoli: United Kingdom), so the fixture never changed hands and the purge was never exercised.
  Cause, MEASURED in the engine doc (`effects_documentation.md`): `set_state_controller` is the
  COUNTRY-scope form taking a state; inside a state block the effect is `set_state_controller_to`.
  Harness fixed (`set_state_controller_to = ROOT` / `= PREV` from the partner's scope, both vanilla
  forms). Verdicts of run 1 are void for the purge.
- Harness run 2, MEASURED (owner, 2026-09-08 19:26, cold-restarted game, fresh `1944.1_Jan.hoi4`,
  `event wa_pclost.9 ITA` from BHU): scope `1 1 1 1 0` on all five blocks, and all three legs PASS.
  Leg A (448 Tripoli -> ITA -> GER, enemy): queue 13->12, active_nonrail 5->4, pc_lost_n 0->1,
  `projects_in_state_of_ITA^num` 1->0. Leg B (450 Benghasi -> ITA -> USA, faction member): queue
  12->12, pc_lost_n 1->1, array stays 2 (nothing cancelled). Leg C (160 Veneto -> ITA -> GER):
  queue 12->11, active_nonrail 4->3, pc_lost_n 1->2, array 1->0. So the purge fires, cancels only
  the enemy-lost projects, counts them, cleans the builder's state array, and leaves a faction
  transfer intact; `set_state_controller_to` reaches `on_state_control_changed` (the ASSUMED rung
  6 boundary is now MEASURED closed for this path). The `@var:` array iteration and both `var:`
  scopes work in-engine.
- Runs 19:17 and 19:21 were VOID (`I-am-ROOT=0`, all country-valued triggers false while name
  interpolation and `ROOT = { always = yes }` read true) - the console hot-reload poison. Discriminated
  by the cold restart at 19:26 reading `1 1 1 1 0` from the byte-identical file: it is the reload, not
  the harness. Durable rule -> [[hot-reload-poisons-country-triggers]] (lessons log).
- NOT committed: the working-tree diff (on_action classification, `@PREV` add-site, harness files) is
  not committed by me; the first-cut edits were swept into `054a4a87e4` (see [[concurrent-sessions-sweep-edits]]).
  Commit the remainder as one change before closing.
- Verification (campaign): `wa_tlm_pc_lost_n > 0` on at least one country that lost ground to an
  enemy (positive control), and no `pc` row whose state is controlled by an enemy for more than one
  save (`savegame.py pc TAG --limit 0` joined with `control`).
- Closed when: the remainder is committed and one campaign shows the two verification lines.

### research-rush — PARKED (2026-09-09)
- Parked 2026-09-09 on the owner's order (admission of `air-budget`, WIP limit: 8 under OPEN for 4); move it back to OPEN in one line when its owed item lands. State at parking: TESTED 2026-09-08 (owner console run pasted); the only item owed is the campaign probe - nothing to do in a session until a scored campaign is read.
- **Owner console run 2026-09-08 18:13, save `1937.4_Apr.hoi4`, ENG** (game.log, pasted):
  ```
  Q7    : WA_rb_uses_cat_transport=0 ahead2=0   uses_industry=0   uses_cat_light_armor=0   uses_t_eng_fighter_multirole_ad_tech_1=0
  GATE  : transport OR1=1 veto=1   hampden OR1=1 veto=1
  wa_rb.2 granted WA_TEST_rb_bonus (cat_transport, 0.5, uses 1)
  Q7    : WA_rb_uses_cat_transport=1 ahead2=0   uses_industry=0   uses_cat_light_armor=0   uses_t_eng_fighter_multirole_ad_tech_1=0
  GATE  : transport OR1=0 veto=0   hampden OR1=1 veto=1
  ```
  Then the game ran to 1938.6.20 (`test_research_3.hoi4`): Bristol Bombay `level=1 date="1938.1.4.1"`
  (normal completion, no slot entry), the test record a spent shell (no `uses`, no `claim`), and
  `var ENG "^wa_rb_"` = only `wa_rb_uses_t_eng_destroyer_7=1` (ENG_the_admiralty granted 1937.5,
  tech not yet researched) - `wa_rb_uses_cat_transport` consumed and cleared by the
  `on_research_complete` chain. MEASURED. Boot 18:07: 0 parser errors on technologies / grant files
  (the harness's own `clear_temp_variable` lines were the only errors, removed); 18:08-18:59: no
  runtime error naming the ledger's constructs.
- Verification (1) DONE above; (2) DONE (boot); (3) campaign probe pending.
- Owner order 2026-09-08 ("tous les bonus, compteur d'usages, plancher 1 an ... 2 ans pour les ahead
  of time de 2 ans"). Intended behaviour: an AI may start a tech one year before `start_year` while a
  research bonus use is available for it (any of its categories, or the tech itself), two years when
  that bonus carries `ahead_reduction >= 2`; without a bonus the generated date gate is unchanged.
- Symptom (MEASURED, campaign `6fcbbe0d` + owner observe run): on build `b829393945` ENG started
  four 1938 techs in August 1936 with no bonus on them - the `has_tech_bonus` exemption shipped that
  day was inverted. Console harness `wa_rb.1` (6 runs, ENG/LUX, 1936.8/1937.4): `technology =` form
  never depends on the tech; `category =` form stays true on spent records the engine never deletes
  (20-save trace). No usable engine trigger -> script-side ledger.
- Change (`documentation/WA_RESEARCH_RUSH.md`): `tools/gen/gen_research_bonus_tracking.py` writes
  `WA_rb_uses_<key>` / `WA_rb_ahead2_<key>` counters after every `add_tech_bonus` (1 610 blocks, 83
  files) and an `on_research_complete` consume chain in every tech (4 357); the 4 203 generated
  `ai_will_do` date gates read the counters (`add_research_bonus_exemption.py` migrated them, the
  ai_will_do generators emit the same shape). Residual, by construction: a tech of the category
  already running at grant time completes first and decrements in the bonus's place - closes early,
  never late (no research-START hook exists in the engine).
- Verification: (1) owner console, save 1937.4 of `6fcbbe0d`: `tag ENG`, `event wa_rb.1` (Q7 counters
  absent, GATE Bombay veto 1), `event wa_rb.2` (grants cat_transport: Q7 `uses_cat_transport = 1`,
  GATE Bombay veto 0), then a NORMAL completion of a cat_transport tech brings the counter to 0
  (`research all` does not fire on_research_complete the normal way - RUN 6). Paste here.
  (2) Boot log: 0 parser errors on `common/technologies/*` and the 83 grant files (F9).
  (3) Campaign: `savegame.py var ENG "^wa_rb_" <saves>` never monotone-growing; a major with a
  2-year ahead focus (GER `GER_synthetic_breakthroughs`, ITA `ITA_mare_nostrum`) has the covered
  `start_year+2` tech in progress within a year.
- Closed when: (1) pasted with the counter returning to 0, (2) clean, (3) observed on one campaign.

### ger-labour-law — OPEN (2026-09-09)
- Owner order 2026-09-09 ("testons de garder l'allemagne 100% en mandatory army service").
  Intended behaviour: the German AI holds `mandatory_army_service` in the `ministry_of_labour`
  slot for the whole game and never swaps to `factory_conscription`.
- Symptom: none - this is an owner-ordered experiment, not a measured defect.
- Previous behaviour, MEASURED (`common/ideas/zzz_ministries.txt`, both `ai_will_do` blocks of the
  slot): the two laws carried mirrored GER weights around a hard-coded `1942.2.1` - before it
  mandatory x200 / factory x0, after it the reverse, with the pre-1942 weights restored whenever
  GER took `surrender_progress` against SOV or reached `scraping_the_barrel`. So GER swapped to
  factory conscription on 1942.2.1 and could swap back later.
- Change: both GER modifier pairs replaced by one unconditional weight each - `factor = 200 / tag = GER`
  in `mandatory_army_service`, `factor = 0 / tag = GER` in `factory_conscription`. The date literal,
  the surrender/scraping clauses and the `NOT = { has_completed_focus = GER_prepare_the_opposition }`
  term disappear with them. No other tag touched. DERIVED: the slot's two other laws already read 0
  for GER (`offer_better_wages` `factor = 0`; `incentivise_employability_oppertunities` x0 on
  `is_major = yes`), so mandatory is the only positive weight GER can see.
- Regression risk, DERIVED: GER loses the +0.30 `industrial_capacity_factory` of factory conscription
  from 1942.2 on and keeps +0.10 `conscription_factor` / -0.20 `training_time_factor` instead - a
  deliberate trade, expected to show as lower late-war German equipment output and a larger manpower
  pool. ASSUMED: the human player is unaffected (this is an `ai_will_do` weight, the law stays
  selectable and its `available` block is untouched).
- No harness owed: `ai_will_do` weights in an idea file, no `WA_AI_*` scripted effect, no on_action.
- Verification (campaign): the report law-change table shows GER on `Mandatory Army Service` at every
  monthly save from the first labour-law pick to the end of the run, and no `-> Factory Conscription`
  row for GER; German military-factory output and manpower pool compared with `1ac7e4ea` to price the
  trade.
- Closed when: one campaign shows zero GER labour-law changes after its first pick, and the owner
  rules on the output-versus-manpower trade the run measures.

### repeatable-pp-decisions — OPEN (2026-09-08)
- Owner order 2026-09-08 ("certaines pays IA ont des décisions répétables qui coutent des PP ... ces
  décisions empêchent les IAs de faire les choses importantes"). Intended behaviour: an AI spends PP on
  a REPEATABLE PP-cost decision only when PP piles up with nothing better to buy; one-off choices
  (laws, advisors) get the PP first.
- Symptom: the owner's playthrough observation; "repeatables win by repetition" is ASSUMED, not
  measured from decision counters (the last ENG "buys nothing" case had a scripted-sink cause -
  lessons log - so a campaign law/advisor timing read is the probe, below).
- Inventory, MEASURED (`common/decisions/*.txt`, parser over every decision): 764 decisions are
  repeatable (`days_re_enable`, `days_remove`, or `fire_only_once = no`) and cost PP; most carry
  `ai_will_do factor = 1..800` with no PP term, so they re-enter the AI's daily decision pick every
  cooldown. Engine arbitration between decisions, laws and advisors is a black box.
- Change: `WA_AI_DECISIONS_has_spare_pp` (OBSERVATION, `common/scripted_triggers/WA_AI_DECISIONS_triggers.txt`)
  = native `has_political_power > constant:wa_ai_decisions.pp.spare_floor` (= 350,
  `common/script_constants/wa_ai_decisions.txt`), wrapped by the DECISION trigger
  `WA_AI_DECISIONS_can_spend_on_repeatable` that every gate names. Loud side chosen (lessons review):
  a `constant:` inside a native numeric trigger is ASSUMED to work (same family as the validated
  `num_of_civilian_factories` / `surrender_progress` rows, NOT itself in the 2026-08-16 probe list);
  if it does not resolve it reads 0, the trigger is always TRUE and the brake never trips = today's
  behaviour - never "216 decisions blocked forever", which a `check_variable` on `political_power`
  (never read as a variable anywhere in this repo) would have risked.
  218 decisions in 34 files (the owner's 3 + 215 added by classification) get
  `modifier = { factor = 0  NOT = { WA_AI_DECISIONS_can_spend_on_repeatable = yes } }` placed LAST
  in `ai_will_do` (a later `add` would revive a 0); 20 of them had no `ai_will_do` and got
  `factor = 1` + the gate (ASSUMED = engine default weight). Owner exclusion applied: decisions
  blocked at a maximum threshold (74 CAPPED) are untouched. Also untouched, by classification: 349
  CRITICAL (war-support / stability recovery, propaganda, reserves, wargoals and claims, prospecting,
  civil-war and coup races, aid to and from exile governments incl. `weapons_for_the_resistance`,
  economy-fatigue relief), 4 PP-generating buffs (`*_political_favours`, `*_special_orders`), 50
  already carrying a PP term. Full table (764 rows, per-verdict): scratchpad
  `repeatable_pp_decisions_classification.md` (session 2026-09-08). Lessons review CONFLICT ->
  resolved (native trigger, exile decision ungated, this symptom line); architecture review CONCERNS
  -> all applied (layer wrapper, comment form, counts).
- Regression risk, DERIVED: a country that never reaches 350 PP (small AI at war, PP-negative ideas)
  never takes a gated decision again - for the APPLY set that is the intended trade (buffs, flavour,
  South-American investments); the CRITICAL set was kept out for exactly this reason.
- Owed before commit (owner): a game boot with 0 errors on the 34 decision files + the two new files
  (`error.log`), and one console read on a 350+ PP country - `WA_AI_DECISIONS_can_spend_on_repeatable`
  TRUE there and FALSE on a country under 350 (the FALSE control is what proves the constant resolved).
  No `WA_TEST_*` harness: one-line trigger, no on_action caller.
- Verification (campaign): no AI takes an APPLY-listed decision (timed ideas / cooldown flags such as
  `ENG_labour_inspire_the_workforce`, `SOV_Workers_*`, `SOUTH_AMERICA_investment_*`) at a save where
  its `political_power` reads below 350; AI law/advisor timing on the report's law-change table is not
  later than the reference campaign `1ac7e4ea`.
- Closed when: one campaign shows zero APPLY-listed decision taken by an AI below the floor, and no
  law/advisor delay versus `1ac7e4ea`.

### sov-conscription-oscillation — SHIPPED-UNTESTED (2026-09-08)
- Owner order 2026-09-08 ("corrige le", on the law-change table of the campaign HTML report).
  Intended behaviour: the AI conscription ladder only climbs; `volunteer_only` is the step out of
  `disarmed_nation`, never a peacetime demotion.
- Symptom, MEASURED (saves `1936.2`-`1939.5` of the report campaign, SOV country block, one
  `mobilization_laws` idea per save): `limited_conscription` 1936.3 -> `volunteer_only` 1936.4-5 ->
  `limited` 1936.6-8 -> `volunteer` 1936.9 -> ... a ~2-month cycle at peace, all of 1936-1939.
  The report reads the save correctly; the mod oscillates.
- Cause, DERIVED: `WA_AI_upgrade_conscription_law` (`WA_AI_law_effects.txt:75`) gates on the
  one-step-up `WA_AI_can_upgrade_manpower_law` but its if-chain tests `WA_AI_can_take_volunteer_only`
  FIRST regardless of the current law. That trigger accepted `OR { disarmed_nation, has_war = no }` +
  `has_manpower > 750000`, so at peace a country whose gate passed was demoted. Non-SOV: gate
  (`can_take_extensive`, `has_manpower < 500000`) and demotion (`> 750000`) exclude each other on
  the limited rung, so the demotion was dead code; SOV bypasses the band via `original_tag = SOV`
  (`:988`, `:1114`), so it demoted and re-promoted every mobilisation cycle (`conscription_ratio >= 0.99`).
- Change: `WA_AI_can_take_volunteer_only` (`WA_AI_LAW_triggers.txt`) requires `has_idea = disarmed_nation`;
  the `has_war = no` branch is removed. 3 lines, no new tag/date/number. Lessons review CLEAR
  (no lesson records the peacetime demotion as a regulator; the non-AI fallbacks to `volunteer_only`
  - stability collapse `_stability_war_support.txt:457`, exiled government `100_wa_on_actions.txt:3336` -
  are untouched). Architecture review CONCERNS all applied (comment rewritten to the protects /
  assumes / how-to-tell form). Regression risk, DERIVED: non-SOV never reached the removed branch;
  SOV's new steady state is `extensive_conscription` at peace (service_by_requirement needs war) -
  ASSUMED acceptable. Pre-existing debt named, not fixed: tags in this non-CONFIG trigger file
  (`original_tag = SOV` `:988/:1114`, `tag = SOV/FRA` `:1119`, USA/ENG `:896/:905`, HUN/IRE
  `:962/:1135`). No harness: 4-line trigger change, no `WA_TEST_*` owed by the rule.
- **Change 2 (2026-09-08, owner order on the HUN / SOV law tables: "l'ia devrait changer de loi si son
  manpower restant est en dessous de soit 250k hommes, soit 10% des effectifs théoriques de l'armée";
  ruling `max`).** Symptom, MEASURED (report campaign, law-change table + pool chart): HUN
  `limited_conscription` 1938.7 with a ~100k pool, `extensive` 1940.5 at ~330k; SOV `extensive` 1939.10
  with ~2M free. Cause, MEASURED (`WA_AI_LAW_triggers.txt`): every rung compared the free pool to an
  ABSOLUTE number (500k / 750k / 1M / 300k) that never scaled with the army, so a small country was
  always "short"; SOV skipped the pool test by `original_tag = SOV` on the limited and extensive rungs
  and `NOT tag = SOV/FRA` on the 1M guard; the engine `ai_will_do` in `common/ideas/_manpower.txt`
  carried the same absolute caps plus +1000 for SOV/FRA at war.
  Change: one rule for both paths. `WA_AI_LAW_update_pool_floor` (`WA_AI_law_effects.txt`, first line
  of the ~2-day conscription pulse) writes `WA_AI_LAW_pool_floor = max(constant floor_min 250000,
  army_share 0.10 x deployed_army_manpower_k x 1000)` (`common/script_constants/wa_ai_law.txt`);
  `WA_AI_LAW_is_pool_short` (new OBSERVATION trigger) reads `has_manpower < WA_AI_LAW_pool_floor`
  and is 0 until the first pulse (safe side). The six `WA_AI_can_take_*` rungs name it in place of
  their absolute numbers, the SOV/FRA exemptions and the `< 10 mil factories -> 300k` clauses;
  `has_capitulated = no` now applies to every rung of extensive+. The five climbing `ai_will_do`
  blocks get `factor = 0` unless the trigger reads true - placed LAST in each block, because
  ai_will_do modifiers apply in order and an `add` after a 0 revives it (lessons review) - and lose
  their `has_manpower > N` caps (which would have blocked a 12M army at 1.1M free); the
  `volunteer_only` peacetime `add = 200` after 1943 is gated on `has_idea = disarmed_nation` so the
  engine path cannot demote at peace (the Change-1 oscillation rebuilt on the second path); the
  `volunteer_only` block carries the same last gate so rung 1 obeys one rule on both paths. Kept, pre-existing and outside this subject:
  the war / ideology / date gates per rung, the ENG `has_manpower < 50000` clause on limited
  (`:1078`, it now ANDs with the rule and keeps ENG at volunteer longer - owner to rule), the FRA
  1940 focus clause, the engine `manpower_per_military_factory` weights.
  MEASURED (install `dynamic_variables_documentation.md`): `has_manpower` and `deployed_army_manpower_k`
  are listed dynamic variables; ASSUMED until the harness runs: they read on the LEFT of `check_variable`
  (an unreadable left side reads 0 = ALWAYS short = climbs at every gate, the loud side - the harness
  pool line beside three literal triggers is the probe);
  `deployed_army_manpower_k` is the "theoretical army" the owner means (fielded divisions, not the
  training queue). Regression risk, DERIVED: FRA at war in 1940 with a 2M army needs < 250k free
  before extensive (it used to pass with any pool); disarmed nations leave `disarmed_nation` as
  soon as ideas allow instead of waiting for a 750k pool that small nations never had.
- Harness (contract v1, own file): `common/scripted_effects/WA_TEST_law.txt` + `events/wa_test_law.txt`
  - `event wa_law.1 SOV` (one country) / `event wa_law.2` (every AI army). Independent floor and
  short verdict beside the shipped ones; a `FAIL` line names a rung that climbs with the pool above
  its floor or a floor mismatch. First run owed (owner), after a 0-error boot log on the two law
  files (`check_variable` against `constant:` is the syntax the boot rule exists for). Lessons
  review CONCERNS, both applied (gate order, engine demotion path); architecture review CONCERNS,
  all four applied (no date at the code site, harness reads the constants with its own arithmetic
  order, FAIL on shipped/indep disagreement, rung-1 symmetry).
- Verification (campaign): SOV `conscription_law` monotone non-decreasing across the monthly saves
  from 1936.2 to the first war (report law-change table shows no `-> Volunteer only` row for SOV);
  for every AI law change in the table, the pool at the previous save reads under
  max(250k, 10% of `deployed_army_manpower_k`) - the report's "Pool at that save" column; no AI
  `-> Volunteer only` row at peace after 1943.1.1 (the engine demotion path stays closed).
- Closed when: one campaign shows zero SOV demotions before its first war, SOV reaches
  `extensive_conscription` only after its free pool drops under its floor, and no AI law change in
  the table happens with the previous save's pool above the floor.

### ai-equipment-naming — PARKED (2026-09-05)
- Parked 2026-09-05 on the owner's order ("parque ai-equipment-naming") to bring OPEN back under the
  WIP limit; move it back to OPEN in one line when a scored campaign is read. State at parking:
  TESTED 2026-09-04 (checker + evaluator diff DONE, boot OK); the AI GER Panzer III/IV variant reading
  from the next scored campaign is the only item owed; nothing else changes.
- Owner order 2026-09-04: "on a un soucis d'hygiène de code : les entrées ai_equipment comme
  medium_tank_6 n'ont pas de convention claire de nommage (noms dupliqués entre nations, le nom
  n'est pas clair, les outils python référencent ces id) - harmonisation + convention propre".
- Intended behaviour: every `common/ai_equipment/` key documents itself. Group key =
  `<OWNER>_<role_slug>[_<qualifier>]`; design key = the exact `target_variant.type` it targets
  (`__<qualifier>` only for a second design on the same type); every design line carries its
  `# <display name>`. Spec + rationale + rejected alternatives: `documentation/AI_EQUIPMENT_NAMING.md`.
- Symptom (MEASURED on the pre-migration tree, 29 files / 358 groups / 1736 designs): 316 design
  keys whose number is not the chassis mark (`ENG medium_tank_6` = `tank_eng_medium_chassis_4`
  Cavalier); 313/526 keys reused across files; 4 keys defined TWICE inside one group -
  `SOV_medium_tank_destroyer.medium_tank_destroyer_2` = SU-85 (l.1689) and SU-100 (l.1774) plus
  its `_cc` twin, `SWE_modern_tanks.modern_tank_1` = IKV Leo and Lansen C, `SWE_heavy_tanks.
  heavy_tank_1` = EMIL I and Kranvagn (evaluator `by_name` dict kept the last one silently; engine
  behaviour on the duplicate ASSUMED = one shadowed); 25 groups without the owner-tag prefix;
  104 group slugs contradicting their role; 724 designs without a display-name comment.
- Safety of the rename (MEASURED): no reference to any group/design key outside
  `common/ai_equipment/` in `common/ events/ history/ localisation/`; save `1944.6_Jun.hoi4`
  (campaign `5b7c30c6`, 5.0 M lines) holds 0 occurrences of any key - variants persist as
  `(equipment definition, creator, modules)` only, so a running campaign is unaffected.
- Shipped 2026-09-04 (working tree, uncommitted): `tools/check_ai_equipment_names.py`
  (audit / plan / apply, span-based rewrite, `WA_EQUIPGEN` marker ids rewritten with the keys);
  `apply` = 186 group renames + 1736 design renames + 724 comments, 3048 edits, 29 files,
  insertions == deletions (2324), CRLF/BOM state preserved, post-apply audit 0 errors 0 warnings.
  AGENTS.md validation row + production-system row; `tools/equipment_evaluator/decide.py`
  `design_family` (trailing-number regex on the design NAME) replaced by `airframe_family` =
  the airframe `archetype` from `common/units/equipment` (read up the `parent` chain); the two
  evaluator test files re-pointed at the new keys.
- Evaluator regression (MEASURED, `--domain all --all --generate-plan` before vs after, decisions
  keyed by mapped (country, group, from-type, to-type)): 1663 -> 1665 decisions - the +2 are the
  SWE heavy/modern chains the duplicate keys had hidden; 1 verdict changed,
  `ITA_maritime_patrol P.108A -> Z.506` PARALLEL_VARIANT -> SWITCH (the old name families
  `patrol_N` / `maritime_patrol_N` split what one `medium_bomber` archetype does not; two
  chain pairs re-routed around it), 2 encodability changes on the same pair; everything else
  identical. A first attempt with family = parent-lineage root moved 14 verdicts to
  PARALLEL_VARIANT and was dropped for the archetype reading.
- Tests: `python -m unittest equipment_evaluator.test_generation
  equipment_evaluator.test_production_efficiency` = 39 tests, 1 error, identical before and
  after: `CoverageAuditTests.setUpClass` fails in `config.py:251` (`'NoneType' object has no
  attribute 'open'`) - pre-existing, not this subject.
- Verification (closing criterion): (1) `python tools/check_ai_equipment_names.py` exit 0 -
  DONE; (2) evaluator decision diff as above - DONE; (3) F9 boot test by the owner: the mod
  loads and `error.log` carries no `ai_equipment` line, then one AI Germany in 1939 fields a
  Panzer III/IV variant (proves the design groups still match). Owner 2026-09-04: "boot OK" -
  the load half PASSES; the Panzer III/IV variant reading is owed from the next scored campaign.
- Anomalies the convention surfaced (owner 2026-09-04: "on ne devrait pas avoir de v2 pour les
  chars"), MEASURED against `common/units/equipment` + `common/technologies` (tech -> equipment
  it enables) - fixed in the working tree: Panzer IV G targeted `tank_ger_medium_chassis_3_3`
  (= Ausf. H) while its `enable` tech `ger_medium_tank_chassis_3_2` unlocks `_3_2`; Marder III
  Ausf. M targeted `tank_ger_light_chassis_td_4` (= Ausf. H) while `ger_light_td_tank_4_1`
  unlocks `_td_4_1`. Both designs were therefore unbuildable until the NEXT chassis tech, then
  competed with it on the same chassis. Types corrected, keys re-derived by the tool; no `__vN`
  design left on any tank file. Tool fix in the same pass: a second `apply` kept `__atk` etc.
  (it had re-derived `__v2` from the already-converted key).
- Closed when: (1) and (2) hold on the committed tree (DONE, commit below) and one scored campaign
  shows an AI GER Panzer III/IV variant.

### ger-barb-doctrine-catchup — PARKED (2026-09-04)
- Parked 2026-09-04 on the owner's order ("parke ces deux là") to bring OPEN back under the WIP
  limit; move it back to OPEN in one line when the harness is played. State at parking:
  SHIPPED-UNTESTED 2026-09-04 (commit `b049763e0`), owner console harness (GER, `ger_armor.1001`) not yet run, one Historical Normal/Hard campaign save owed afterwards; nothing else changes.
- Redesign 2026-09-06 (owner order: "il doit terminer les doctrines tiers 1, donner à l'Allemagne
  schwerpunkt, et enlever 80 d'xp terrestre"): `ger_armor.1001` is now a ONE-SHOT gift
  (`fire_only_once`, 1-day MTTH, no on_weekly pulse) on a FIXED date `WA_AI_CONFIG_after_ger_land_doctrine_gift`
  (date > 1940.1.1 - a calendar date on purpose, mastery gain is balanced by humans; replaces
  `WA_AI_CONFIG_after_barbarossa_doctrine_deadline`). Immediate: `WA_AI_DOCTRINES_finish_land_tier_1`
  (the step effect re-run up to 4 times until the observation trigger reads complete, WARNING log
  otherwise), then if `tier_2_armour` is empty `set_sub_doctrine = schwerpunkt` + `army_experience = -80`
  (owner's price; `armor_subdoctrines.txt` lists `xp_cost = 100`). The trigger no longer requires
  tier 1 incomplete, so the tier-2 gift lands even when tier 1 was already done. ASSUMED: a
  `set_sub_doctrine` / `add_mastery` is visible to `has_completed_track` inside the same effect
  (harness `wa_doc.2` measures it). Harness: `wa_doc.3 <TAG>` added = the whole gift, gate mirror
  no longer reads all-done. Verification lines below still name the 1941 saves of the first design:
  read "1940.1.2+" for "1941.3+" and "1939" for "1941.1"; the console readings are otherwise unchanged.
- Added 2026-09-06 (owner order: "ajoute un event de safety comme ger_armor.1001 qui, au moment de
  barbarossa (la date) donne à GER les doctrines tiers 2 qui lui manquent"): `ger_armor.1002`, same
  gate shape, on `WA_AI_CONFIG_after_1941_6` (date > 1941.6.1 - owner: three weeks before the
  historical jump-off "pour laisser le temps à l'event de trigger", no dedicated trigger). Immediate:
  `WA_AI_DOCTRINES_finish_land_tier_1` then `WA_AI_DOCTRINES_assign_land_tier_2` (each EMPTY
  `tier_2_infantry` / `tier_2_artillery` / `tier_2_armour` gets its SELECT-preferred subdoctrine,
  German default otherwise; `tier_2_operations` excluded, MEASURED needs `tier_3_infantry`).
  No mastery; owner order 2026-09-06 "80 d'xp enlevé par doctrine": each assignment charges
  `army_experience = -80` (same price as the 1940 schwerpunkt). Harness: `wa_doc.4 <TAG>` mirrors it; report gains
  `after-t2-deadline`, `tier2-all-sub`, `t2-gate-open`. Untested like the rest of the subject.
- Owner order 2026-09-04: "add a cheat for GER AI : when 4 months before historical barb date, it
  should have completed all land doctrines of tier 1 : if not, give mastery to finish them, so
  that it can unlock the focuses to add mastery to tier 2 before the barb start".
- Intended behaviour: from 1941.2.22 an AI Germany holds every tier-1 land doctrine track
  (`tier_1_infantry`, `tier_1_artillery`, `tier_1_armour`) complete within weeks, so the mastery
  its spring-1941 focuses grant (`WA_add_mastery_*` cascades to the first INCOMPLETE track) lands
  on tier 2. `tier_1_operations` is NOT part of the target: MEASURED its subdoctrines require
  `has_completed_track = tier_3_armour` (`operations_subdoctrines.txt`), a late track with a
  tier-1 name.
- Symptom (MEASURED, campaign `bd2612e8`, monthly saves, GER on `auftragstaktik`): at 1941.3
  `tier_1_artillery` 159.5/200 mastery (1 of 2 rewards) and `tier_1_armour` 182/200 (1 of 2);
  both complete only by 1942.1; tier 0 all complete, `tier_1_infantry` complete since 1941.1.
  Daily mastery gain Jan-Jun 1941 reads 0 to 0.002 on every land track (peacetime stall,
  ASSUMED cause: training weighted 0.03). `mastery_bank` = 0 everywhere (WA `MASTERY_BANK_MAX
  = 0`). Doctrine state lives in the save's top-level `doctrine={ countries={...} }` block,
  entries unkeyed, index = `countries={}` order + 1 (reproduce: scratchpad `doctrine_extract.py`,
  subagent reading 2026-09-04).
- Shipped 2026-09-04: CONFIG window
  `WA_AI_CONFIG_after_barbarossa_doctrine_deadline` (date > 1941.2.22); OBSERVATION trigger
  `WA_AI_DOCTRINES_has_completed_land_tier_1` (`WA_AI_DOCTRINES_land.txt`); effect
  `WA_AI_DOCTRINES_complete_land_tier_1` (new `WA_AI_DOCTRINES_effects.txt`): one step per land
  line per call - finish tier 0 (`add_mastery` 200, or `set_sub_doctrine` if the track is
  empty), else assign the tier-1 subdoctrine the existing `WA_AI_LAND_DOCTRINES_SELECT_*`
  triggers prefer, else `add_mastery` 200 on tier 1; event `ger_armor.1001` (`events/WA_AI_GER.txt`,
  `is_triggered_only`, fired every 7 days by `on_weekly_GER` in `100_wa_on_actions.txt`, gate = tag GER +
  `is_ai` + `WA_AI_CONFIG_securities_enabled` + the window + NOT the observation trigger); harness
  `wa_doc.1 <TAG>` / `wa_doc.2 <TAG>` (`WA_TEST_doctrines.txt`, `events/wa_test_doctrines.txt`).
- Gate decision (owner, 2026-09-04): new CONFIG class `WA_AI_CONFIG_securities_enabled` =
  Historical Normal + both Hard buttons - a "security" keeps the WW2 sequence on track, unlike a
  `cheats_enabled` assist (Hard only, e.g. `ger_armor.1000` Sealion). Off only on Historical Easy
  and Competitive Normal.
  No `is_historical_focus_on` gate: on an ahistorical path the catch-up is harmless (principle 1).
- Timeline at the real cadence. The pulse is `on_weekly_GER`: exactly 7 days apart. (First cut
  was an MTTH-1-day repeating event with a 7-day cooldown flag; MEASURED 2026-09-04 boot test,
  error.log `ger_armor.1001: Event is set to trigger every day` - the engine polls such an event
  daily, the only repeating MTTH-1 event in `events/WA_AI_*.txt`; replaced by the on_action the same
  day.) 200 mastery per pulse, 2 rewards x 100 per track (DERIVED from `DEFAULT_REWARD_MASTERY =
  100`, not overridden; MEASURED `tier_1_artillery` 159.5 mastery = 1 reward and tier-0 tracks
  200 = 2 rewards agree):

  | pulse | date (7 d) | worst case per line (tier 0 empty) | measured bd2612e8 case |
  | --- | --- | --- | --- |
  | 1 | <= 1941.3.1 | tier 0 subdoctrine assigned | art +200 -> done, arm +200 -> done, inf skipped |
  | 2 | <= 1941.3.8 | tier 0 +200 -> complete | trigger reads done, event stops |
  | 3 | <= 1941.3.15 | tier 1 subdoctrine assigned | - |
  | 4 | <= 1941.3.22 | tier 1 +200 -> complete | - |

  Lines advance in parallel; worst case done by 1941.3.22 (first weekly tick up to 7 days after
  1941.2.22, then 3 x 7 days), ~13 weeks before 1941.6.22. If the reward cost were higher than
  100 (ASSUMED define), each extra 200 costs one more pulse - still done by May. The event
  re-evaluates `has_completed_track` every pulse, so nothing is over-added. The date of the first
  tier-2-relevant GER mastery focus on bd2612e8 is NOT measured (no focus timeline pulled); the
  assist only needs to finish before it.
- Reviews 2026-09-04: architecture CONCERNS, applied - effect header cut to 5 lines, the
  unconditional `log =` lines justified in the header (<= 12 per campaign, read by the harness;
  not gated on `WA_AI_logging` on purpose), timeline redone at 7/14-day pulses. Lessons CONCERNS,
  applied - harness recipe says tag into a real non-GER country first (08-27 addendum: the
  observer context poisons country-valued triggers), the "twice" expectation reworded (one pulse
  for an assigned line, two for an empty one), event comment says why Country layer and not an
  archetype. Both reviewers: `set_sub_doctrine` bypassing a tier-1 `available` stays ASSUMED
  until the wa_doc.2 closure on an EMPTY line; on bd2612e8 all three lines were assigned, so the
  shipped path there is `add_mastery` only. Noted, not done: `WA_AI_DOCTRINES_*` has no row in
  AGENTS.md "Generic Systems" (meta-work, owner call).
- Impact analysis. New files + additive appends only; no existing trigger/effect/strategy
  modified. Readers of the new CONFIG window: 1 (the event). Readers of the new observation
  trigger: the event and the harness. `WA_AI_LAND_DOCTRINES_SELECT_*` are READ, not changed (their
  own readers = the subdoctrine `ai_will_do`). Non-GER countries: never reach the event. Human
  GER: `is_ai = no`. Regression risk: a GER that had NOT chosen tier-1 subdoctrines would have
  them chosen by the SELECT triggers (its own preference logic) - MEASURED on bd2612e8 GER had all
  three assigned by 1941.1, so on that path only `add_mastery` runs. Cost: 200 army XP worth of
  mastery per line, no XP spent.
- **ASSUMED** (engine, not save-observable): `set_sub_doctrine` bypasses `xp_cost` and
  `available` (doc: "activate (unlock and assign)"); a `country_event` fired from an on_action
  evaluates the event's `trigger` and does nothing when it reads false (vanilla relies on it in
  every `is_triggered_only` event that carries a `trigger` block); `has_completed_track` = every
  reward unlocked (the same
  reading `WA_add_mastery_*` already relies on); `add_mastery` on a track with 1 reward left and
  +200 unlocks the reward and completes the track in one tick.
- Verification (owner console, harness contract): load a Historical Normal/Hard GER-AI save dated
  1941.2.23-1941.6 (bd2612e8 `1941.3_Mar.hoi4` qualifies unless it ran Easy; the `gate` line
  tells): `event wa_doc.1 GER` must read `scope : 1 1 1 1 0`, then `gate : is-GER=1 is_ai=1
  securities-enabled=1 after-deadline=1`, and `art t1 done=0` / `arm t1 done=0` on the 1941.3 save.
  Then `event wa_doc.2 GER` once: `art t1 done=1  arm t1 done=1`, VERDICT `tier1-all-done=1
  trigger-says-done=1 gate-open=0`, and `logs/game.log` carries two
  `[ger-barb-doctrine-catchup] ... +200 mastery tier_1_*` lines. Control: the same on a 1941.1
  save reads `after-deadline=0 gate-open=0`; on a Historical Easy save `securities-enabled=0
  gate-open=0`.
  `tier1-all-done` != `trigger-says-done` = the observation trigger is wrong, stop.
- Campaign probe (Historical Normal/Hard run): in the `doctrine` save block, GER `tier_1_*` tracks read
  `rewards=2` on the first save after 1941.3.1; a tier-2 track shows mastery > 0 from a focus
  after that date.
- Closed when: the harness reading above is pasted here, then one Historical Normal/Hard campaign save
  after 1941.3 with all three GER tier-1 tracks at `rewards=2`.

### coal-prospect-loop — PARKED (2026-09-07)
- Parked 2026-09-07 by the agent, not by an owner decision, to admit the owner's
  `light-support-conversion` order under the WIP limit — move it back to OPEN in one line if that
  is the wrong pick. State at parking: SHIPPED-UNTESTED since 2026-09-04, owner console harness
  run owed; nothing else changes.
- Scope: owner report 2026-09-04 (National-Projects tooltip: GER running 11 "Expand X Coal Basin"
  at once, 55 civs). Intended behaviour, two levers under one slug: (A) a coal state is prospected
  at most twice (excavation4 tier, then excavation5 tier) and never again; (B) a supplier prospects
  for an ally only while that ally is short AFTER its imports — an ally the trade AI parks at ≥ 0
  is supplied, not needy.
- Symptom, MEASURED (campaign `5d2a391c`, 117 monthly saves 1936.2-1945.8, `mods=world-ablaze-beta`
  — DERIVED same build family, hash `80a3` vs local `3eb1`): GER's `coal_prospecting` fires cycle 1
  in 1941.1 (the month `excavation4` completes), pauses 27 months (flag = 1 needs `excavation5`,
  `start_year = 1943`), then runs cycles 2-5 BACK-TO-BACK from 1943.8 — state 4's `coal_developed`
  reads 1 → 4 → 5, the next instance is taken the day the previous completes (flag date 1944.9.7,
  cycle 5 ≈ 1944.9.8), each cycle 30 d longer (`coal_duration` 60 → 210), each re-adding the
  state's full coal (E. Rhineland: 5 × 254 = 1270 instead of 508). GER's OWN need is never true:
  `wa_ai_needs_coal = 0` on all 117 saves, effective coal min +8170 (1936.6) → +17206 (1945.2). Sole
  weight = the cooperative leg: HUN/ITA/ROM(/FIN/BUL) at `wa_ai_needs_coal = 3` in EVERY save 1941.1
  → 1944.12, held by the writer's import arm (`resource_imported@coal > 40`), while HUN sits at +81,
  ROM +9 (supplied). 5 of the 11 targets (Wallonie, Lublin, E. Mazowieckie, Serbia, Upper Bohemia)
  are RBE/RPO/RSE/RCZ-held at 1945.2 and still counting down — a taken instance is not re-validated
  (ASSUMED engine; no `cancel_trigger` in the block).
- Cause (A), MEASURED: of 126 prospecting decisions in `_resource_prospecting.txt`,
  `coal_prospecting` is the ONLY one whose `remove_effect` increments a flag (`modify_state_flag
  value = 1`, :114) with no `NOT = { has_state_flag value = N }` stop; the 37 tiered siblings all
  carry one (`develop_liaotung_iron_ore_deposits` :3533 is the shape it copied, cap dropped).
  Introduced whole by the upstream squash `ac1dbf19f` (2026-07-06) replacing 16 `fire_only_once`
  per-state decisions; hand-written (the `ai_will_do` replacer splices only the `ai_will_do` span).
- Cause (B), MEASURED: `WA_AI_allies_need_<r>` read "ally at needs = 3" and the writer
  (`WA_AI_misc_effects.txt:566-577`) ratchets any importer above 40/month to 3 — it measures import
  DEPENDENCE, not unmet need. That leg has legitimate readers (synth research, construction scoring
  :213, PC admission :158, the overextension brake already pairs a balance term for this reason),
  so the writer is untouched and the consumer that misread it is fixed.
- Change: (A) `common/decisions/_resource_prospecting.txt` `coal_prospecting.target_trigger` gains
  `NOT = { has_state_flag = { flag = coal_developed value > 1 } }` — `>` not `= 2` so a save already
  at 4-5 stops at its next selection (an instance in flight completes once more, ASSUMED engine).
  (B) all nine `WA_AI_allies_need_<r>` (`WA_AI_RESOURCE_NEEDS_triggers.txt`) gain
  `check_variable = { resource@<r> < 0 }` inside `any_other_country` — the ally's effective balance
  (net minus unmet, i.e. demand its imports do not cover). Owner ruling 2026-09-04: deficit-after-
  imports semantics, all 9 resources.
- Impact analysis. Readers of `coal_developed` / `coal_duration`: this decision file and
  `100_wa_on_actions.txt:98` only. Callers of `WA_AI_allies_need_<r>`: the prospecting `ai_will_do`
  blocks only (trigger file scope note). Reach: every country with excavation4/5 and an array state
  (no tag, no date — historical and ahistorical identical). Regression risk, STATED: the coop leg now
  fires only under market shortage. Sweep MEASURED on `5d2a391c` (4 saves, 895 needs=3 rows, 116
  faction-legs true today): 48 legs stay (allies ≥ 1 quantum short: USA alu/rubber/chromium −344
  to −825, GER chromium −314 / iron −95, ITA steel −226 / coal −598, CAN bauxite −85..−115), 68 go
  false — 37 with every member parked in [0, quantum), 31 with a member in SURPLUS (all 7 oil legs:
  ENG/SOV/JAP at +61..+941 oil counted as critical). Coal: 3 of 15 legs survive (quantum 100).
  Bound (f): chatter lives in the sub-quantum band (NEG→PARK flips 12/57 shallow vs 4/66 deep, at
  6-12-month sampling; the 2-day writer cadence is ASSUMED chattier) and a flicker fires a decision
  that then runs ≥ 60 d — but every prospecting decision is now capped per state (A here, the 37
  sibling caps, the 85 one-shots), so the worst case is an early firing of a bounded run, never a
  loop. Checkers: worklist / constants / ai_layers all exit 0; `0` is a sign test (same file reads
  `resource@<r> < 0` 9× already), `value > 1` is this decision's own tier count — no constant.
- Rejected alternative (g), quoted from R65 (`CHECKLIST_R_ARCHIVE.md:1161`, 2026-08-17): "also
  requiring the ally to be in deficit (`resource@coal < -40`) — the wa-lessons-reviewer showed it
  would delete the leg rather than narrow it, since importing pushes the ally's balance back toward
  0." Mine covers it because the leg's own question is "does an ally need help": an ally whose
  imports park it at ≥ 0 HAS been helped — the objection describes the case the leg must be false
  on. Measured, it narrows rather than deletes: 48 of 116 legs remain, exactly the allies still ≥ one
  quantum short after importing. The prior exit line of `prospecting-coop-solvency` ("counters still
  growing for an importing member (HUN-like)") asserted the opposite and is replaced (row below).
- Verification, owed to the owner: (1) F9 boot (decision file + trigger file parse only at launch);
  (2) resume `1945.2_Feb.hoi4` of `5d2a391c` as GER: the decisions tab lists NO `coal_prospecting`
  target whose state has `coal_developed > 1` once its running instance completes (the 6 GER-held
  states all read 4-5 → none re-selectable), and the civilian-factory tooltip's National Projects
  block drains from 11 basins to 0 over the following ~7 months; (3) next campaign probe
  (save-visible, no console): no state in `global.coal_states_array` carries `coal_developed > 2` or
  `coal_duration > 120`, AND at least one coal state reaches `coal_developed = 2` (control: cap, not
  kill); (4) coop probe: a supplier's prospecting counters (`decisions <TAG> --match prospecting`)
  are flat while every faction member at needs = 3 reads effective ≥ 0, and still climb for a member
  at effective < 0 with imports > 0 (ITA-1944-like). Tell-tale of over-blocking: an ally at effective
  < 0 for ≥ 3 saves with a supplier in the faction that never prospects.
- **Campaign `d1c51a6c` scored 2026-09-04 (build carries `6308759d3`): probe (3) PASS, probe (4)
  PASS on its main leg, control leg VOID.** MEASURED (streaming state-block scan, all 50 coal-key
  states, 1943.6/1944.6/1945.2/1945.8): max `coal_developed` = **2**, max `coal_duration` = **120**
  in every save; states at 2: 0 → 26 → 32 → **36**; states above 2: **0**. GER's 11 targets all at
  2 from 1944.6, `coal_prospecting` TOTAL 11 → 22 → 22 → 22, zero live instances — flat by CAP
  EXHAUSTION (DERIVED: nothing left to prospect regardless of the ally gate). Coop leg at 1944.6:
  every Axis member at needs = 3 reads effective ≥ 0 (HUN +40, ROM +27, BUL +248) while GER is
  flat — consistent with the `resource@coal < 0` gate. Control leg: no country in the probed set
  matches "effective < 0 AND imports > 0" (ITA at −383 has imports 0; ITA is in the United
  Nations here) — cannot discriminate over-blocking on these saves. Over-blocking tell-tale
  NEGATIVE: ITA at effective < 0 on three saves, but its faction suppliers DID prospect (USA 7 →
  12, ENG at cap). `coal_duration = 60 + 30 × coal_developed` in 200/200 cells (one mechanism, not
  independent evidence). Counter calibration: ENG reads `count = 1` on four states at dev = 2, GER
  `count = 2` — the flag table is load-bearing, the counter corroborates only.
  **Anomaly, outside this subject**: ITA state 114 sits at `coal_developed = 1`, decision
  `available days=0`, for 28 months while ITA reads needs = 3 / effective −383 → −43 — one cycle
  under the cap, offered, never taken; not the cap, not the ally gate (ITA's own need). Candidate
  for ITA's `ai_will_do` / activation terms — proposed, not admitted.
- Closed when: (1) and (2) are pasted here and pass, then (3) and (4) pass on one campaign; OR (2)
  fails and the in-flight-instance behaviour ships a `cancel_trigger` under this slug.

### posture-v3 — PARKED (2026-09-09)
- Parked 2026-09-09 on the owner's order (admission of `air-budget`, WIP limit: 8 under OPEN for 4); move it back to OPEN in one line when its owed item lands. State at parking: SHIPPED-UNTESTED since 2026-09-04 (UNTESTED-STALE); code committed, the owner console harness run is the only thing owed - paste it here and move to TESTED, no session work pending.
- Owner order 2026-09-04 ("vas-y pour les points 1 à 5" on the posture-formula review). Intended
  behaviour: the weekly offensive-posture verdict counts the whole contact line without a cap,
  weighs armoured AND mechanised divisions, never sends a globally strong army balanced into local
  inferiority, can reach the grind against a major, instruments its exchange rate, pursues a
  collapsing enemy, and is consumed by every AI country (the Comintern included).
- Symptoms, MEASURED (campaign `5d2a391c`, scratchpad `5d2a391c_effectifs_et_buffers.md` §1.6 and
  the 12-row limits table of the review): SOV `posture_vs_GER` = 1 on 12/17 quarters with NO
  consumer (Comintern had no exec/grind pair); USA `posture_vs_GER` = 1 in continuous execution
  with 59 vs 106 divisions in France at 1944.9 (pairwise pass skipped the local scan); the old
  ladder capped at 24 points above 20 divisions per state; armour-only bonus x2.5 for three tanks,
  x1.25 for twenty-four, mechanised invisible (46 % of the 1945 US army); `post_grind_n` SOV = 0
  all war (GER pool 1.86 M never under the absolute 500 k bar); `post_exec_xr_lt25` at 76-91 % of
  level-1 weeks against a ~1:1 cumulative ledger (artefact suspected, never instrumented).
- Change (this commit), five points:
  1. `WA_AI_MILITARY_posture_count_state_divs` (`WA_AI_MILITARY_posture_effects.txt`): 15-rung
     all-types ladder with band midpoints up to >100 (no cap), +50 % mobile weight per armoured
     and per mechanised division (two 6-rung ladders); `local.max_states` 12 → 40. The single-call
     `num_divisions_in_states` form was REJECTED: its `states = {}` list is literal in every usage
     (install and WA), the contact set is a runtime array - ASSUMED it cannot take one.
  2. The local scan always runs (cost gate removed) and its pass 1 also walks the enemy's SUBJECTS'
     controlled states at war with us (lessons: `every_controlled_state` excludes subject soil - the
     eastern line runs through RBL/RUK states); new `local.inferior = 1.0` / `inferior_hold = 1.2`
     (enter/hold pair); verdict inputs as flags (`_post_pairwise_ok`, `_post_local_ok`,
     `_post_local_inferior`, `_post_bars_ok`); **level 3** = pairwise pass ∧ local inferiority vs a
     MAJOR ∧ not local_ok; the four loops carry an explicit `break = _post_break_` reset at the head.
  3. Relative dry test: `manpower.grind_enemy_mp_per_div = 3` (thousands per fielded division,
     replaces `grind_enemy_mp = 500000`), `grind_mp_edge` 4 → 2 applied to faction pool PER
     fielded division (`_post_faction_div` accumulated in the faction loop); `xr.veto` follows the
     edge to 0.5 (recorded coupling 1/edge). **Bar vs the motivating series, DERIVED from
     `5d2a391c`:** GER 1.86 M / 301 div = 6.2 k per division at 1945.8 (5.2 k at 1944.6) - ABOVE the
     3 k bar, so the grind vs GER still rests on the exchange-rate route; the bar fires on an enemy
     that is genuinely bleeding (pool < 3 k per division at maximum mobilisation), which GER was not
     in that campaign (pool rising). Point 3 makes level 2 reachable, not automatic.
  4. Verbose per-enemy diagnostics (`WA_TEST_post_*_<TAG>`, written only under the country flag
     `WA_TEST_posture_verbose`) + harness `WA_TEST_posture.txt` / `events/wa_test_posture.txt`
     (contract v1; `wa_post.1` report, `.2` weekly on, `.3` tick, `.4` off): own bars, one line
     per major enemy with the shipped verdict/diagnostics AND an independent coarse contact-line
     count (own state walk, own ladder, no shared helper).
  5. **Level 4 pursuit** (`surrender_progress > brake.surrender_hard` ∧ a capability term that
     discriminates on the enemy's own population: `WA_AI_MILITARY_posture_enemy_army_is_broken`
     = the absolute alive.* bars for a MAJOR only, or for any enemy a pool under 3 k per fielded
     division or a hollow line; ignores the air veto) and the
     consumers moved to `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_posture.txt` (execute =1
     balanced 340 / careful =2|3 careful+manual 340 / pursuit =4 rush+manual 350), gates
     `WA_AI_MILITARY_should_posture_execute/careful/pursuit` (`FRONT_gate_triggers.txt`),
     `posture_has_grind_target` → `_has_careful_target` (2|3) + `_has_pursuit_target` (4). The
     six faction blocks `ALLIES/AXIS/CHINA_FRONT_exec|grind_vs_*` are DELETED (their only readers).
     The family yields (§6.2 ownership, `WA_AI_MILITARY_country_owns_front_control_scripted_opening`,
     body mirrors the owning gates) to the Country-layer scripted openings of the three countries
     that had NO faction pair before: JAP's China choreography (`chinese_war_1-4`), ITA's Ethiopian
     war blocks, SOV's Winter-War / Poland invasion-time rushes - their openings keep their own
     execution type exactly as before.
     `WA_TLM_post_exec_n` now counts levels 1 AND 3 (both executions); level 4 has no metric yet.
  Docs: `WA_AI_MILITARY_SYSTEM.md` §9 (consumers row, levels, a `[posture-v3]` paragraph),
  `WA_AI_MILITARY_TYPES_REFERENCE.md` (priority ladder note).
- Impact walk (principle 3): every AI country at war reaches the calculus weekly (unchanged
  population); consumers now reach EVERY AI country instead of Allies/Axis/China members - the
  Comintern, neutrals at war, and ahistorical factions gain execute/careful/pursuit blocks at
  priority 340/350: the tier the deleted CHINA_FRONT pair held (340), so the surviving CHINA_FRONT
  careful-exec blocks (330 vs JAP, 320 vs collaborators, not posture-gated) stay outranked exactly
  as before; for Allies/Axis the tier rises from 300 to 340 with NOTHING between 100 and 340 in
  those files (front_control ladder measured: 10000 / 500 / 330 / 320 / 100 / 0), so their
  precedence is unchanged. Whether the engine overrides whole blocks or per field when two
  front_control entries meet is ASSUMED (§6.1.1). Populations the family newly reaches, walked:
  JAP (own faction, never had a pair) - yields to its China choreography through the ownership
  trigger, so 1937-45 vs CHI is unchanged, and it gains the family vs USA/ENG/SOV land fronts
  only outside those windows (never, in practice: `chinese_war_3` holds for the whole China war);
  ITA 1936 vs ETH - yields to the Ethiopian blocks (the F-item war keeps its scripted rush);
  SOV vs FIN 1939 and POL 1939 - yields to the invasion-time rushes; SPA/SPR (civil war) - the
  posture calculus skips enemies under 5 states and both civil-war sides hold far more, so a
  verdict exists and the family arms at 340 above `SPA_*`/`SPR_*` Country blocks (priority 0):
  behavioural change ASSUMED small (both sides at level 1 execute balanced where the scripted
  blocks already said execute) - probe (vi) below. CHINA_FRONT survivors (`careful_exec_vs_japan`
  330, `_vs_collaborators` 320, not posture-gated) stay under the family at 340 as under the
  deleted pair.
  Historical: GER 1941-42 scripted Barbarossa openings (priority 0) were already outranked by the
  AXIS pair at 300 - unchanged; SOV now executes vs GER whenever its verdict is ≥ 1 (level 1 on
  12/17 quarters of `5d2a391c`) instead of only inside the 140-day `ai_barb_timer` window;
  `SOV_counterattack` (Country, priority 0) is now redundant while armed - left in place, one
  proposed cleanup line below. Ahistorical: a country in no faction at war with a major gets the
  family for the first time. Regression risks, stated: (a) level 3 makes a globally strong but
  locally outnumbered attacker careful - it can slow a scripted opening whose local count is
  thin (mitigation: the openings run at their own execution type only when no posture block is
  armed; a careful verdict is still `execute_order = yes`); (b) level 4 can rush into a rump the
  bars misread as broken - both `surrender_hard` AND a capability term are required; (c) the
  always-on scan costs up to 40 states x 27 rungs x (1 + coalition members) trigger evaluations
  per enemy per week - ASSUMED negligible at weekly cadence, no measurement; (d) the mobile weight
  and the taller ladder move the local ratio for every country - a front that used to read 1.0
  under the cap can now read its true value in either direction.
- Level 1 ↔ 3 boundary: enter under 1.0, hold until 1.2 (no weekly flip around a single bar).
- Reviews 2026-09-04: lessons CONFLICT → resolved (subject soil in pass 1 + harness; level-4
  capability term discriminating per population; `xr.veto` re-coupled at 0.5; explicit `break`;
  docs; impact walk extended; harness STOP re-fire target, type-token probe, dry-bar table);
  architecture CONFLICT → resolved (family re-tiered 340/350 above the China
  careful blocks; dates/campaign ids/measurements stripped from the new code comments and the two
  FIX history blocks retired into subject-named rules; §6.1 tier table, §9 and the TLM §5 rows
  updated; `wa_post.2`/`.4` now retract the `WA_TEST_post_*` diagnostics so `shipped-fresh` cannot
  print a stale week; trigger renamed `_enemy_army_is_broken`); lessons: see below.
- Bound claim, (f) table for the consumer swap (weekly pulse vs engine `enable` re-evaluation,
  cadence ASSUMED): t0 = commit loaded, first weekly pulse publishes levels on the new scale (a
  country holding a stale 2 keeps it one week - level 2 is still a valid careful verdict);
  t1 = the engine re-evaluates enables: the Default family arms on the same per-enemy variables
  the faction pairs read, so no country loses its execute for more than one pulse; t2 = steady.
  No re-swap path exists (the faction blocks are deleted, not gated off).
- Harness: `event wa_post.1 SOV` from the observer tag; `event wa_post.2 SOV` for the weekly
  exchange-rate readings (point 4) - never `tag` the country under test (weekly pulse is is_ai-gated).
- **Owner run 2026-09-04 04:07, fork `5d2a391c` 1945.4.1, fired after `tag SOV`** (`wa_post.1`
  then `wa_post.2`, pasted): scope `1 1 1 1 0`; own `eq=0.930 manpower_k=1390 divisions=426
  posture=1 should_update=0 hard_brake=0 still_operational=1 hold_the_line=0`; vs GER `verdict=1
  divisions=307 manpower_k=576 at-max-conscription=1 surrender>0.45=0 army_broken=0`, independent
  contact line `enemy=12 ours=13` states, coarse count `enemy=168 ours=224` (1.33: between the 1.0
  inferiority bar and the 1.5 entry bar, so the level 1 is the pairwise route - consistent);
  vs ROM `2/2` states, `27 vs 27`; RK Norwegen `0 vs 12`; every other enemy no contact; all
  verdicts 1; `own states reading armor=8 mechanized=0` (SOV fields no mechanised divisions -
  the `type = mechanized` probe needs USA). shipped-* all 0 / `shipped-fresh=0` on both runs.
  Reading: the harness itself PASSES (scope, independent walk, shipped verdicts read); the
  shipped-side diagnostics are VOID on this run - `should_update=0` while at war = SOV was human
  (tagged), so the weekly pulse never ran for it; the verdicts printed are the frozen last AI
  values. Recorded in the recipe and as a WARN line in the report. Stays SHIPPED-UNTESTED until
  a run fired as `event wa_post.2 SOV` from the observer has produced one weekly series with
  `shipped-fresh=1`. Also noted: GER `manpower_k=576` on the owner's GER-played fork vs 1 860 on
  the BHU line (different branch, not a contradiction).
- Probes (campaign): (i) SOV holds a `front_control` execute vs GER outside the barb window
  (`imgui show ai-strategy` on SOV: `WA_AI_MILITARY_DEFAULT_FRONT_posture_*` listed); (ii) USA
  vs GER reads level 3, not 1, on a save where its France contact count is under the German one
  (harness `indep` line); (iii) SOV ground recovery faster than the `5d2a391c` reading (8 SOV
  states in 26 months from the 1943.6 peak) on a scored campaign; (iv) no level-4 verdict against
  an enemy above `alive.min_div` divisions (harness `army_broken=0` ⇒ verdict ≠ 4); (v) eight
  weekly `xr` rows on the fork before any level-1 exchange-rate veto is proposed; (vi) the Spanish
  Civil War outcome and date within the F-item band on the next scored campaign; (vii) the harness
  `own states reading mechanized` column > 0 for USA on a 1944+ save (the `type = mechanized`
  assumption) - a 0 there retunes the mobile ladder to `armor` only.
- Proposed, not admitted: delete `WA_AI_MILITARY_SOV_counterattack` / `_coordinate_offensive`
  (dead: `coordinate_offensive` has no setter; the counterattack is outranked by the Default
  family) - legacy-gate trace first; a `WA_TLM_post_pursuit_n` metric (TLM doc §7 process).
- **Campaign `d1c51a6c` scored 2026-09-04 (build carries `664a94bc9`; 116 saves 1936.2-1945.8):
  probes (ii), (iii), (iv), (vi) PASS; (i), (v), (vii) NOT CHECKED (console/fork only).** Detail:
  scratchpad `d1c51a6c_subjects_report.md`. MEASURED verdict series (`var <TAG> "^wa_ai_military_posture"`,
  12 quarterly saves 1941.9→1945.8): **every level of the new scale fires** — level 3 on GER vs SOV
  (1942.9-1943.9), GER vs ENG (1943.3), ENG vs ITA (1942.3, 1943.9), USA vs ITA (1943.9), USA vs
  JAP (1945.3→), JAP vs PRC (all war); level 2 on USA vs GER (1944.3-1944.6, the post-D-Day
  exchange), GER vs SOV (1942.3, 1944.3); level 4 on POL/YUG/NOR/PHI/INS (0-2 divisions or
  annihilated), GER vs FRA (5-11 divisions), SOV/USA/ENG vs ITA (18-26 divisions, 4 states). (iv)
  PASS: no level-4 cell against an enemy above `alive.min_div` = 40. SOV vs GER reads **1 on every
  save 1942.9→1945.8** (0 at 1941.9/1942.3), never 2/3 — matches the DERIVED bar note above (GER
  1.86 M / 248 div = 7.5 k per division > 3 k; SOV `wa_tlm_post_grind_n` = 3 vs `exec_n` 2143).
  GER reads 0 (hold) vs SOV from 1944.6 and vs ENG/USA from 1945.3 while losing ground.
  (ii) PASS on the basis the scan actually uses (own + faction members + subjects at war with the
  enemy, vs enemy + its subjects): western bucket (metropolitan France + Benelux + western German
  states, `plans.py ALL --where`, closure exact) 1944.9 Allies **203** vs German side **128** (1.59),
  1945.3 **250** vs **201** (1.24 — above `inferior_hold` 1.2, so level 1 held; USA alone is 166 vs
  GER 193, which is why a USA-only count reads as a false FAIL — the probe wording must say
  coalition). USA vs GER = 1 at both dates. (iii) PASS: `control owner:SOV` 152/187 SOV-held at
  the 1943.6 peak (RBL 18 / GER 12 / ROM 5) → 155 (1944.6) → **189/189, 2772/2772 provinces**
  (1945.8) — all 35 states in 26 months vs 8 on `5d2a391c`; back-loaded (3 in the first 12 months,
  32 in the next 14). Exchange (`losses.py`, peace-ledger corrected): SOV/GER losses 1.29 over
  1943.6→1944.6, **0.42** over 1944.6→1945.8. (vi) PASS: `SPR_franco_won` 1939.4.3. TLM at 1945.8
  (live, `last_t` 114): exec_n SOV 2143 / USA 3188 / GER 4087 / ENG 3306; grind_n 3 / 20 / 38 /
  10; `xr_lt25 / xr_n` 85 / 80 / 87 / 76 % — the exchange-rate sample sits in the most favourable
  band everywhere, the artefact suspected in the symptom list is still uninstrumented on a
  campaign (probe v owed on the fork). Recorded, not defects: (a) SOV/USA/ENG keep `vs_ita = 4`
  after ITA's 1944.1.20 defection and GER/JAP/ITA keep `vs_phi/ins/nor = 4` on annihilated tags —
  the documented post-peace lingering, inert because every consumer and `_has_pursuit_target`
  gate on `has_war_with`/`any_enemy_country`; (b) JAP's family FROZEN from 1945.4 (`last_t` 111,
  all live-enemy verdicts 0 from 1945.3) — DERIVED candidate: `wa_ai_fielded_eq_ratio` 0.856 at
  1945.8 against `enter.min_eq_hold` 0.85, i.e. the equipment gate cleared the posture; (c) USA's
  overall tracks the highest single pairwise value (1→3→2→1→3), by construction. Also MEASURED on
  this campaign, outside the subject: D-Day 1944.2.8 (4 months early), Paris liberated 1944.12.23,
  and at 1945.3 the French front is an interleaved checkerboard (19 contested states, GER still in
  Brittany and the Massif Central behind Allied-held Champagne/Paris) — France reads 58/60 French
  by 1945.8. Stays SHIPPED-UNTESTED until the harness weekly series is pasted.
- Closed when: harness output pasted (both the report and one weekly series), and probes
  (i)-(iv) pass on one scored campaign.

### usa-pacific-hoard — PARKED (2026-09-09)
- Parked 2026-09-09 on the owner's order (admission of `air-budget`, WIP limit: 8 under OPEN for 4); move it back to OPEN in one line when its owed item lands. State at parking: SHIPPED-UNTESTED since 2026-09-04 (UNTESTED-STALE); code committed, the owner console harness run is the only thing owed - paste it here and move to TESTED, no session work pending.
- Owner order 2026-09-04: "à aucun moment, tant que USA est en guerre en Europe et vs le Japon,
  l'armée US ne doit avoir plus de 50 % de son armée (quand au-dessus de 75 divisions) dans le
  Pacifique". Intended behaviour: a two-ocean US army above 75 divisions keeps at most half of
  itself in Pacific island garrisons.
- Symptom, MEASURED (campaign `5d2a391c`, `plans.py USA --where` + type-5 order re-parse): 119 of
  193 divisions (62 %) under 15 scripted `put_unit_buffers` island orders at 1945.5, 26 on fronts;
  buffer share 44 % (1943.6) → 62 % (1945.5), instance ids unbroken since 1943.9.13. Cause:
  `WA_AI_MILITARY_COUNTRY_USA_THEATRE_buffer_pacific` (11 orders, Σ ratio 0.64, 0.54 non-yielding)
  + `_buffer_philippines` 0.25, both armed while `WA_AI_MILITARY_pacific_high_risk` (= at war with
  JAP) holds — nominal 0.89 of the whole army, no cap, no distance term. Evidence: scratchpad
  `5d2a391c_effectifs_et_buffers.md` §2.
- Change (this commit): `constant:wa_ai_theatre.usa_pacific.cap_min_div = 75`
  (`common/script_constants/wa_ai_theatre.txt`, new category); one-way monthly latch
  `WA_AI_MILITARY_update_pacific_share_cap_latch` (flag `WA_AI_pacific_share_cap_latched`,
  `has_army_size > constant`, anglo-major gated, `WA_AI_misc_effects.txt`, called from the monthly
  block of `WA_AI_misc_on_actions.txt`); observation `WA_AI_MILITARY_is_two_ocean_war_with_large_army`
  (latched ∧ `pacific_high_risk` ∧ an uncapitulated enemy with a European capital); gates
  `should_usa_buffer_pacific` / `_low_army` / `_philippines` take its `NOT`, twins
  `should_usa_buffer_pacific_capped` / `_philippines_capped` take it; blocks
  `WA_AI_MILITARY_COUNTRY_USA_THEATRE_buffer_pacific_capped` (order_ids 9120-9130, Σ 0.37, same
  states and pool flags) and `_buffer_philippines_capped` (9131, 0.12) — Pacific nominal sum 0.49.
  Doc: `documentation/WA_AI_MILITARY_ECONOMY.md` E4d (exclusive-family counting rule for E4c);
  registry SKILL row for `wa_ai_theatre.txt`.
- Reviews 2026-09-04, both CONCERNS, all required items applied or answered here: lessons —
  the Philippines twin keeps its own reachable-and-contested terms (applied), a latch instead of
  a bare 75 edge (applied), the probe stated as REALISED share (below); architecture — E4c
  worst-case count settled by E4d (the file's worst case stays full 0.54 + skeleton 0.50, a
  pre-existing co-fire below 110 divisions, outside this subject), `has_army_size` shape
  (applied), header sentences + registry row (applied).
- Bound claim, (f) table at the two cadences (latch monthly; `enable` re-evaluation cadence
  ASSUMED engine-side): t0 = first monthly tick with num_divisions > 75 → flag set; t1 = the next
  strategy re-evaluation: the 3 full-family blocks retract (`abort_when_not_enabled`), the 2
  capped blocks arm — whether the 15 existing garrison orders shrink to the new ratios or
  persist until re-planned is the engine boundary (ASSUMED; the Hawaii pair 596/597 surviving the
  `_low_army` disarm at 110 divisions says an order CAN outlive its block); t2 = steady: nominal
  0.49 (0.31 non-yielding). No re-swap: the latch is one-way. Below 75, or on one ocean, nothing
  changes.
- Probes (campaign): (i) realised share — buffer / `num_divisions` ≤ 0.50 on every save where
  USA is at war with a European-capital enemy AND `pacific_high_risk` AND `num_divisions` > 75
  (`plans.py USA <save>`); (ii) churn — the Pacific buffer instance ids stable across the
  consecutive saves after the crossing (`plans.py --oob` + type-5 re-parse); (iii) USA front
  divisions at 1944.9-1945.5 above the `5d2a391c` reading (26-68 of 193-209).
- Harness: `event wa_uph.1 USA` from the observer tag (`events/wa_test_usa_pacific_hoard.txt`,
  contract v1; PASS shape in the event header).
- **Owner run 2026-09-04 04:07, fork `5d2a391c` 1945.4.1, fired after `tag USA`** (pasted): scope
  `1 1 1 1 0`; `facts: num_divisions=191 cap_min_div=75 latched=0`; `indep: size-over-bar=1
  pacific-risk=1 enemy-in-europe=1`; `ship: two_ocean_large_army=0 gate full=1 capped=0 low_army=0
  philippines full=1 capped=0 home_threatened=0`. Reading: PASS shape for the UNLATCHED state (full
  family armed, capped family silent, never both) — the cap state itself is not yet observed:
  `latched=0` because the latch runs in the monthly `is_ai = yes` block and the run happened both
  mid-month and with USA tagged (human). MEASURED consequence, recorded in the recipe and as a
  WARN line in the report: never `tag` the country under test; fire `event wa_uph.1 USA` from the
  observer after the game has crossed a month boundary with USA as AI. Stays SHIPPED-UNTESTED
  until that second run reads `latched=1 full=0 capped=1`.
- Proposed, not admitted (outside subject): `_buffer_pacific` (0.54) and `_buffer_pacific_low_army`
  (0.50) still co-fire below 110 divisions in a Pacific-only war (nominal 1.04); the owner's idea
  "buffers sized by distance to the front" is the generic form of this cap — to explore.
- **Campaign `d1c51a6c` scored 2026-09-04 (build carries `29af55d4c`): probes (i), (ii), (iii) all
  PASS.** MEASURED: USA flag `WA_AI_pacific_share_cap_latched` set **1943.8.1.1**; two-ocean
  condition holds from 1941.12.5 (GER war in USA's block; JAP 1941.12.4 in JAP's; ITA carried by
  RIT/RBE… after 1944.1). (i) buffer/deployed (`plans.py USA` + `army USA`, closure exact on 13
  saves): 1943.6 **0.554** (65 div, pre-latch) → 1943.8 **0.494** (42/85, six thousandths under
  the bar on the latch save) → 0.380 → 0.324 → 0.313 → 0.294 → 0.299 (1944.6) → 0.189 → 0.155 →
  0.154 → 0.194 (1945.5) → 0.168 (1945.8): 11/11 qualifying rows ≤ 0.50. Pacific-only buffer
  share 48/184 = 0.261 (1944.6) → 42/320 = 0.131 (1945.5), the mass moving Hawaii 19 → 7 toward
  Okinawa/Iwo Jima/Saipan/Palau/Philippines. (ii) the 10 type-5 orders (4 Pacific `ads=102`
  instances 7/8/428/429, created 1941.12-1942.10) are byte-identical across 1943.8/9/10 — zero
  churn; the −7 buffer swing at 1943.9 is membership rotation out of the Hawaii armies. (iii) front
  divisions 1944.9-1945.5 = **202 / 172 / 196 / 207** of 254-320 vs the `5d2a391c` 26-68 — 3-8×
  (90 % inherited via army group; the `5d2a391c` figure may carry the `orders_group`-only artefact,
  so the comparison is generous). DERIVED: the latch did NOT drain the garrison — buffer flat 36 →
  42 → 35 → 36 across the crossing while deployed went 65 → 111; the share fell by denominator
  growth, exactly the (f)-table t1 reading (existing orders outlive the block swap). Recorded:
  engine `areadef` (ads=100) 30 → 3 over 1944.6→1944.9 while scripted buffers stay at 52 to the
  end; NO_ORDER spike 39 at 1945.3 (5 armies) → 20 → 6. Monthly sampling cannot exclude an
  excursion above 0.50 between saves (ASSUMED). Stays SHIPPED-UNTESTED until the harness run reads
  `latched=1 full=0 capped=1`.
- Closed when: harness output pasted (PASS shape) and probes (i)-(iii) pass on one scored campaign.

### eng-reserve-partner — PARKED (2026-09-04)
- PARKED 2026-09-04 (owner choice, WIP limit, to admit `east-front-rail`). State at parking: code
  committed (`a5fd7920a`), console read not yet run, campaign probes (i)-(iii) waiting for a save
  newer than the fix. Resumes as SHIPPED-UNTESTED once a slot frees.
- Owner order 2026-09-04, for ENG: "autorise le recrutement après que USA soit dans faction OU que
  taille armée inférieure à 1 million après 1941". Intended behaviour: the materiel-limited
  archetype's reserve bank deploys once a materiel partner is in its faction, or once its field
  army is under 1 M men after 1941. Supersedes the 2026-08-27 v2 ruling "ENG reste fermé"
  (`[reserve-quality]`); ENG division counts are non-comparable across this commit.
- Symptom, MEASURED (`5d2a391c`, `var ENG "^reserves="`, 9 saves 1941.12-1945.8): `reserves = 40`
  byte-identical for 45 months, no `WA_reserves_template_created` flag on ENG; ENG 75-81 divisions
  with 261 k rifles idle at 1945.1 (scratchpad `5d2a391c_effectifs_et_buffers.md` §1.4).
- Change (this commit): `WA_reserves_is_expeditionary_only` — the materiel-limited OR term is now
  `AND { WA_AI_CONFIG_is_reserve_materiel_limited  NOT WA_reserves_is_materiel_limit_relieved }`;
  new `WA_reserves_is_materiel_limit_relieved` = `any_allied_country { WA_AI_CONFIG_is_reserve_materiel_partner }`
  OR (`WA_AI_CONFIG_after_1941` ∧ `has_army_manpower < @RESERVES_MATERIEL_LIMITED_SMALL_ARMY`,
  1 000 000, single reader); new CONFIG archetype `WA_AI_CONFIG_is_reserve_materiel_partner` (USA).
  Comments re-aligned (`_reserves.txt` veto note, CONFIG header + readers line, lessons entry).
- Reading of "après 1941" = `WA_AI_CONFIG_after_1941` (`date > 1941.1.1`, the sanctioned date
  vehicle) — CONFIRMED by the owner 2026-09-04 ("après 1941 = date > 1941.1.1, ok").
- Walk (historical): ENG at 1941.1.1 ≈ 39 divisions ≈ 0.65 M men → the size term opens the bank at
  1941.1.1, eleven months before the USA joins (1941.12); `WA_reserves_can_deploy` passes (pool
  > 150 499, a major enemy). Drain: `deploy_reserves_infantry` (base 4000, `days_remove = 1`,
  10 divisions and −150 000 manpower per batch) → 4 batches within days; no refill in war
  (`WA_reserves_can_recruit` needs `has_war = no`) → one 40-division wave per war, bounded.
  Ahistorical: no partner ever joins → the size term is the only path; an army above 1 M keeps the
  bank shut.
- Regression risk, stated: the wave spawns at 0.3 equipment (`WA_reserves_spawn_divisions`); on
  `1ac7e4ea` a 40-division ENG wave at 1945.2 died within a month (`eng-reserve-wave`). ENG's rifle
  stock at 1941.1 is not measured (ASSUMED sufficient after 16 months of war; the v2 ruling's
  reason was "no land stocks at war entry" in 1939.9). Killing probe (ii) below.
- Reviews 2026-09-04, both CONCERNS, applied: lessons — supersession recorded in the lessons entry
  and the CONFIG header, first-firing term named, wave probe; architecture — drifted comments
  fixed, `after_1941` boundary raised to the owner (above).
- Probes (campaign): (i) ENG `reserves` 40 → 0 within a month of 1941.1.1 (or of the USA joining,
  whichever comes first); (ii) the spawned reserve divisions still in the OOB at +1 and +3 months
  (`plans.py ENG --templates`, reserve template count) and ENG `wa_ai_fielded_eq_ratio` trajectory
  — a fall under 0.85 the month after the wave = the eng-reserve-wave shape, then the relief needs
  a stock term; (iii) ENG deployed count at 1942.6 above the `5d2a391c` reading (51).
- No harness: not a `WA_AI_*` effect (< 40 lines, reserves has no `WA_TEST_*`); the console read is
  `tag ENG` on a 1941+ fork and the decision list (`deploy_reserves_infantry` available).
- Campaign-probe pass 2026-09-04: NOT SCOREABLE — MEASURED: the newest save on disk of any
  campaign (`autosave.hoi4`/`GER_1945_04_17_02.hoi4`, mtime 2026-09-04 01:34-01:35) predates fix
  commits `ff69c088a` (02:58) and `a5fd7920a` (03:56) by ~1h24m; no save anywhere in the 127-file
  save directory postdates the fix. Probes (i)-(iii) cannot be scored until a new campaign is run
  past that timestamp.
- Closed when: probes (i)-(iii) pass on one scored campaign, or the owner accepts a written no-fix
  ruling on (ii).

### reserve-capacity — PARKED (2026-09-05)
- PARKED at creation (WIP limit: 4 non-PARKED subjects, owner to free a slot). State: both changes
  in the working tree, UNCOMMITTED; no harness owed (`WA_reserves_*`, < 40 lines, no
  `WA_TEST_reserves`); campaign probes wait for a save newer than the fix. Reviews 2026-09-05:
  architecture CONCERNS (rule-7 comments trimmed, regression cases stated below), lessons CONCERNS
  (forward walk done, t-table below, non-comparability note, lessons supersession appended).
- Owner orders 2026-09-05: "corrige la coquille ×10 et remets le seuil d'origine" ; "sépare le veto
  en deux triggers".
- Symptom, MEASURED (`8bf94908`, BHU observer, monthly saves): ROM deployed 36 → 67 (1940.6, peace)
  → 92 (1941.6) → 142 (1943.6) → 145 (1945.6) divisions, "Reserve Divisíon" 50/92 → 97/142;
  `reserves` 80 (1939.6) → 0 (1943.6); `wa_ai_fielded_eq_ratio` 0.55–0.68 from 1942.1 vs HUN
  0.998–1.0 on the same 104 MILs (1945.6: ROM 145 div, HUN 60); 1941.6 the 50 reserve divisions
  read mean org 5.6 with 46 on a front order; `wa_tlm_llr_starving_n` 244. Manpower pool 1.97 M
  and flat: not the constraint. Scratchpad `rom_reserves_diagnosis.md` (six boxes).
- Cause 1, MEASURED (git): `WA_reserves_meets_recruitment_threshold` multipliers 2000/100 (std) and
  1000/50 (SOV) since refactor `2c9028075` (2026-02-05), against its own header 20000/1000 and
  10000/500 and the pre-refactor per-level triggers (`3b711ef39^`: bank 10 needed army > 399 999
  / > 25 000 rifles). Forward walk: no commit in `2c9028075..HEAD` touched those four lines
  (`git log -G`). DERIVED: ROM 1939.6 ≈ 330 k army men clears the loose level-70 bar (339 999) and
  would have stalled at bank 10 under the intended one.
- Cause 2, MEASURED (code): the MIL-tier capacity bars sat inside `WA_reserves_is_expeditionary_only`,
  whose `NOT any_home_area_neighbor_country { has_war_with = ROOT }` term makes the whole trigger
  false in a neighbour war (YUG 1941.4, SOV 1941.6) — the tiers were never evaluated for a
  continental war. `[reserve-quality]` v2 was calibrated on USA/CAN/RAJ/ENG, all overseas wars; the
  "GER 243/107 → open (veto moot, home neighbour at war)" cell recorded that escape as design.
- Change 1: multipliers restored to 20000/1000 and 10000/500 (`WA_reserves_triggers.txt`).
- Change 2: split. `WA_reserves_is_expeditionary_only` keeps has_war / no surrender / no neighbour
  at war / ENG materiel archetype (now AND terms, no OR). New `WA_reserves_is_over_capacity` =
  the three MIL tiers only, no war-state and no surrender term. `deploy_reserves_infantry` carries
  a second factor-0 modifier on it, escaped like the first by `WA_reserves_should_deploy_undersized_army`.
- Walk, ROM (DERIVED from the MEASURED cells): t0 1939.6 36 div / 31 MIL — tier 2 needs > 40, batch
  1 passes (→ 46), restored ladder leaves a bank of ~10 so that is the whole wave; t1 1940.6 46 div
  ≤ 49 MIL → vetoed; t2 1941.6 54 MIL: tier 2 no longer applies, tier 3 needs > 80 → open again
  for whatever bank remains (0 under the restored ladder; under the old ladder the veto alone would
  have capped ROM near 80–90 instead of 145). The ladder is the binding lever for ROM; the veto is
  the guard for a bank that fills anyway (a major's, or a minor grown past 400 k army men).
- Hover residue, accepted: a country at bar+10 has no hysteresis (dump → veto → losses → dump) —
  the same "reserves replace losses" residue accepted for the 30-division bar (`[reserve-quality]`).
- Blast radius, MEASURED (`8bf94908` 1939.6 / 1941.6 / 1943.6, every tag with `reserves` > 0): the
  veto changes exactly one at-war cell, ROM 1941.6 (50 banked, 92 div, 54 MIL). YUG 1939.6 fires at
  peace (10 banked, 22 div / 18 MIL). CHI, every warlord, FIN, GRE hold `reserves = 0`; POL/BEL are
  exiles with 0 divisions; RAJ 1939.6 sits exactly on tier 1 (20 div / 21 MIL, not > 20). CZE (50)
  and VIC (10) are dead tags carrying a frozen bank.
- Regression risk, stated: (a) the peace path (`early_reserve_mobilization_flag`) is now vetoed for
  an over-capacity country — YUG 1939 is the measured case; (b) a collapsing minor
  (`surrender_progress > 0`) stays vetoed until attrition brings it under its tier bar — the exit is
  the field army, not VP loss, chosen (lessons: `surrender_progress` is not a capability test);
  (c) bank sizes are NON-COMPARABLE across this commit: every bank read so far (ENG 40 on
  `5d2a391c`, USA 30, the v2 calibration cells) was measured under the 10×-loose ladder —
  `eng-reserve-partner` probe (i) must be re-based on the bank this ladder yields (ENG needs
  > 399 999 army men for bank 20).
- Closed when: a campaign on this build shows (i) no country under 100 MIL holding `reserves` > 20
  at its war entry unless `has_army_manpower` > the restored bar for that level; (ii) ROM deployed
  ≤ 60 divisions at 1943.6 with `wa_ai_fielded_eq_ratio` > 0.85; (iii) no tier-vetoed country with
  a bank > 0 reads `wa_ai_fielded_eq_ratio` > 0.9 for 6 consecutive months (that would say the
  tiers under-read its industry — the assumption-gone signal named in the trigger header).
- Probes: `var TAG "^reserves="`, `army TAG`, `buildings TAG --match arms_factory`,
  `var TAG "^wa_ai_fielded_eq_ratio="`, `plans.py ROM --templates` (reserve template count).

### hq-role-capture — PARKED (2026-09-04)
- Parked 2026-09-04 (owner decision): slot freed for `coal-prospect-loop`. Readings (1)-(4) below
  remain owed; nothing else changes. Reopens at the same state (SHIPPED-UNTESTED) when pasted.
- Scope: owner question 2026-09-02 ("pourquoi l'IA allemande considere qu'elle a 15 divisions de
  chars lourds ?"). Intended behaviour: an army-HQ division template is never counted as a combat
  role, so the AI's Current-vs-Wanted gap for a real combat role reflects the divisions it fields.
- Symptom, MEASURED (campaign `eaf1d1ea`, saves `GER_1942_08_26_01` and `GER_1943_12_09_22`, owner
  `imgui show ai_division_production` + `plans.py --templates`): GER `heavy_armor` Current = 15.0 at
  1942.8 and 19.0 at 1943.12, equal to its army-HQ division count on both dates, while every real
  tank division sat in `light_armor` / `medium_armor`. Same save 1943.12: SOV reads `heavy_armor`
  4.0 = its 4 real Heavy Tank G divisions, correct.
- Cause, MEASURED (save `division_template` blocks carry a `role="..."` key):
  a template stores a role ONLY when the AI designed it. Every history-authored template - the AOK,
  the SS divisions, the 20-width infantry, the Airborne - stores NONE, and the engine classifies
  those at runtime. Full 1943.12 GER reconciliation: stored roles give infantry 153 / light 7 /
  medium 11 / mountaineers 13 / heavy 0; the runtime pass adds +44 to infantry, +5 to mountaineers
  (SS Gebirgsjager) and **+19 to heavy_armor (the AOK)**, and leaves 16 unclassified (Motorized 6,
  SS Motorized 6, SS Kavallerie 4). 184 + 84 = 268 = `Nr Active Divisions`. The runtime rule itself
  is an ENGINE BOUNDARY - not in any readable file.
- FAILED first attempt, recorded so it is not retried: adding the `hq_role` that WA's
  `replace_path="common/ai_templates"` drops (vanilla `generic.txt` `hq_generic`) CANNOT work. The
  AI never designs an `is_army_hq` template, so nothing ever stores `role="hq_role"` - the owner's
  `imgui show ai_templates` reads "There is no existing template with correct role" on GER AND SOV.
  The role declaration is kept anyway (vanilla declares it, its purpose there is undocumented, and
  `upgrade_prio 0` makes it free); its header now states this measured limit.
- Change (Option B, owner-ordered 2026-09-02): every army-HQ template in
  `history/general/taog_hq_template.txt` now carries FOUR line battalions - the Soviet shape, the
  one the runtime classifier does NOT put in a combat role. 14 blocks rewritten (7 countries x the
  motorized/infantry halves): USA 2->4, SOV 4->4, GER 1->4, ENG 2->4, FRA 3->4, JAP 2->4,
  generic fallback 2->4. Per-country support flavour untouched. `WA_AI_TEMPLATES_hq.txt` target
  count aligned 2 -> 4 for consistency.
- Impact analysis. Reach: every TAOG country with an army HQ, historical and ahistorical alike -
  the gate stays `WA_AI_CONFIG_DIVISIONS_uses_motorized_hq`, no tag or date added. Cost, STATED:
  an HQ division goes from 1-3 to 4 line battalions, so its manpower and equipment bill rises
  (`hq_motorized` = 1200 manpower, 2 combat width each) - GER pays 3 extra battalions x 19 HQs.
  That is the price of the fix and must be read in the next campaign, not assumed negligible.
- Residual risk, ASSUMED: GER's HQ differs from SOV's in TWO ways, line count (1 vs 4) and support
  count (3 vs 1). This change equalises only the first. If GER still reports a non-zero
  `heavy_armor` Current with no heavy tank division, the support set is the remaining lever.
- Verification, owner-reported PASS 2026-09-02 ("ca a marche") - reported verbally, the panel
  numbers were NOT pasted, so the subject stays SHIPPED-UNTESTED until reading (3) below (which
  is save-visible and needs no console) is attached. Readings still owed:
  (1) `imgui show ai_division_production` GER - `heavy_armor` Current equals the number of divisions
  whose template actually contains `heavy_armor` battalions (0 or 2, not 19);
  (2) same screen on one infantry-HQ country for the `hq_infantry` branch;
  (3) a save shows every `is_army_hq` template with four line battalions and no `role=` key -
  save-visible, no console needed;
  (4) boot test - the history file parses only at launch.
- Reading (3) PASSED 2026-09-04 (`5d2a391c`, build commit `91c0f4287` confirmed live; `eaf1d1ea`
  excluded — its last save predates the fix by ~3 minutes): MEASURED at 1944.6, direct read of the
  top-level `division_templates={}` block — all six checked army-HQ templates (GER
  Armeeoberkommando, ENG Army HQ, USA Field Army HQ, SOV Shtab Armii, JAP Gun Shireibu, FRA
  Quartier General d'Armee) carry exactly 4 line battalions and no `role=` key, matching
  `history/general/taog_hq_template.txt` exactly. Readings (1)(2)(4) (owner
  `imgui show ai_division_production` + boot test) remain owed.
- Closed when: readings (1)-(4) are pasted here and pass, OR (1) fails and the support-set lever
  ships under this slug, OR the owner accepts a written no-fix ruling.

### armor-prod-category — PARKED (2026-09-04)
- 2026-09-09 `[air-budget]` phase 3 moves the arbitration this subject measures: the air category
  factors are now ONE block per type at 100 (fighter was 25, the other bomber lines summed their
  per-line 100s), so the air pull against `armor` 60 changes. The "tank share of military lines vs
  4aeb8327" baseline is re-cut on the first campaign after that commit before any verdict here.
- Parked 2026-09-04 (WIP limit, `modern-chassis-tier` re-enters). Code SHIPPED `eefd8b5ea`; its only
  exit is the campaign probe below (three post-fix runs read so far: `d8467fcf`, `5de66942`,
  `5d2a391c` — variants up on GER/SOV/JAP/ITA, run-to-run noise ±0.1-0.3, no verdict yet). Unpark
  when a run is scored against the Closed-when line.
- Slug renamed from `armor-prod-war-floor` on the owner's 2026-09-01 instruction to drop the
  chassis floors: the subject's mechanism is now the `armor` CATEGORY demand factor, and the
  code markers read `[armor-prod-category]`. Everything below the rename is the original
  measurement chain, kept because it is what motivated the change.
- Scope: owner request 2026-09-01 ("les pays investissent trop peu sur leurs besoins blindés —
  augmente le focus industriel sur la prod de matos, pas le besoin en divisions"). Intended
  behaviour: a country at war whose armour role is open keeps a wartime-sized share of its
  military industry on the medium-tank line instead of letting the engine's deficit heuristic
  pull it onto small arms.
- Symptom, MEASURED (campaign `4aeb8327`, GER, production-line parse + `stock.py` + `tlm`):
  tank lines fully funded in all three saves (`active = requested` — the bound is the engine's
  perceived NEED, not allocation); tank factories FALL 76 (1941.5) → 61 (1941.9) while
  military lines grow 492 → 518 and small-arms lines surge 106 → 156 — the pull lands exactly
  at Barbarossa's opening; tank share 15.4 % → 11.8 % of military lines; fielded armour 10 of
  220 divisions (4.5 %) against a 20 % role budget; the peace floor (15, band 150-399) does
  not bind (GER runs 46-59 above it).
- Change (this entry): wartime floor tiers — `WA_AI_PRODUCTION_tank_min_factories_medium_war`
  (150-249, floor **30**), `_medium_high_war` (250-399, floor **45**), `_large_war` (400+,
  floor **60**); peace triggers gain `NOT = { has_war = yes }` so tiers are exclusive. The
  medium band is split at 250 (lessons repair) so no floor exceeds ~20 % of its band's low
  edge — `equipment_production_min_factories_archetype` ignores availability (vendored
  `documentation.info`), which is also why the small band (<150) keeps its single 5-factory
  floor at war. During a small-arms deficit the floor outbids the deficit heuristic by design —
  that is its purpose — and coexists with the infantry-12/truck-10 floors: worst case at a
  band's low edge, all floors together hold ≤ ~35 % of the military base. Plus
  `equipment_variant_production_factor medium_tank_chassis` **75 → 150** in
  `WA_AI_PRODUCTION_build_medium_armor`. ASSUMED (doc-stated only, `documentation.info:485-493`;
  the lessons log records that file's prose being wrong once on production semantics): value =
  % increase of the perceived needed factories, and stacking with `focus_on_medium_armor`'s
  +75 on the same id is additive (225 total). Owner verification below is what upgrades this.
- Cadence walk (war-start flip): t0 declaration of war — peace tier's enable goes false
  (`abort_when_not_enabled` retires it), war tier arms the same evaluation; t1 next engine
  production reallocation — medium line ≥ 45/60, the 59→46 slide becomes impossible while the
  floor binds; t2 peace — tiers swap back, floor returns to 15/30. A major ground under 150
  military factories falls out of both upper bands into the small tier automatically (band
  terms unchanged), so a capitulating industry is never forced to hold 45 tank factories.
- Ratchet, justified widening: `check_ai_layers --update-baseline` raised
  LAYER4-NON-DECISION 330→333 and NUMBER-LEAK 351→356 — the war twins copy the shape and
  band literals of the six frozen-debt floor triggers beside them; renaming only the twins or
  extracting bands only for them would split the family's style without retiring its debt.
- Stockpile interplay, ACCEPTED surplus: the medium stock already grows (1.7k→3.1k) while
  training pace limits fielding, and a need-blind floor plus a bigger factor will grow it
  faster. Accepted because (a) while wanted divisions ≫ fielded (39 vs 15, ≈14k tanks of
  unfilled demand at ~600/division) the "surplus" is a real queue buffer — equipment on hand
  is what lets the engine put more divisions in training at once; (b) once the gap closes, the
  war floor's residual (30-60 factories) is wartime attrition-replacement capacity. If a
  campaign shows a five-digit medium stock with the wanted-gap closed, the floor is feeding a
  pile nobody drains — that reading retires or shrinks the war tiers.
- Verification OWED, owner (upgrades the ASSUMED factor semantics): live game with a
  medium-focus major, `imgui show ai-division-production` / production tab — the medium line's
  requested factories visibly jump when the 150 build loads vs the 75 build, confirming the
  engine honours the value and the +75 stack. Campaign probe (floors/factors do not serialise,
  production lines do): a save with a major at war shows its medium-tank-chassis line(s) at
  ≥ its band floor (30 / 45 / 60), and across the war-opening saves the tank-factory total no
  longer dips below the floor; secondary read: tank share of military lines rises vs the
  4aeb8327 baseline (15.4 % / 11.8 % / 13.4 % at 1941.5/1941.9/1942.1). Boot test owed with
  the next batch (new ai_strategy blocks parse only at launch).
- **ADDENDUM 2026-09-01 (owner, screenshot GER 1 June 1941): floors dropped, category factor in.**
  New MEASURED evidence changes what the lever must be. GER at 498/498 military factories, all
  allocated: guns 249, tanks **85**, planes 164. Its tank lines REQUEST 107 and are served 85
  (Panzer III L 60/75, Panzer IV F 21/26, StuG 3, Flakpanzer 1, Panzerjäger 0/1, a second
  Pz III L line 0/1). Two separate gaps against the owner's 140-factory target: the demand is
  33 short, and 22 more are lost in the allocation because the pool is saturated. DERIVED, and
  it retires the previous entry's lever: the war floor for the 400+ band was 60 on
  `medium_tank_chassis` while GER already ran 81 (Panzer III + Panzer IV are both medium
  chassis) — a **no-op for the country it was written for**.
- Cause of the allocation half, MEASURED (script): the air strategies carry TWO levers — a
  category `equipment_production_factor` (25-100 on fighter / cas / interceptor /
  tactical_bomber) AND a per-variant factor (100-200 on airframes) — while
  `WA_AI_PRODUCTION_DEFAULT_tanks.txt` carried only the per-variant factor. Tanks competed with
  one weapon out of two.
- Change (this entry): **lever A only, floors removed.** New OBSERVATION-free gate
  `WA_AI_PRODUCTION_armor_category_push` (tanks enabled + `use_armor_templates`, no industrial
  bands — a factor scales the engine's own need, so it needs none) driving
  `WA_AI_PRODUCTION_DEFAULT_armor_category_push`:
  `ai_strategy = { type = equipment_production_factor id = armor value = 60 }`. `armor` is an
  equipment CATEGORY (`common/script_enums.txt:132`), so one entry covers every chassis plus the
  assault-gun / TD / SPAA / infantry-support variants — exactly the owner's "chars / variantes
  spécialisées" scope. DELETED with it: all six `medium_tank_chassis` floors (peace 5/15/30 and
  the war tiers 30/45/60 shipped hours earlier) and their six band triggers. The
  `mechanized_equipment` floors are untouched — they are not a tank chassis.
- **REGRESSION RISK, stated because the deletion causes it (AGENTS principle 3e).** The floors
  existed for a measured failure: campaign `9be92c89`, USA slid 116 → 25 tank factories on a
  GROWING industrial base and JAP ran 2-4, because tank archetypes had ranking factors but no
  minimum allocation. Nothing now protects that case: a factor multiplies a need the engine
  computes, so a country whose computed need collapses to near zero gets 60 % of near zero.
  The owner accepted this trade explicitly ("en retirant les planchers chassis"). The probe
  below is what would catch a recurrence; restoring the peace tier is a one-block revert.
- Stacking, ASSUMED: the category factor (60) and the per-variant `medium_tank_chassis` factor
  (150, kept from the previous entry) apply to the same lines. No engine doc states whether a
  category and a variant factor sum, multiply, or one wins. `documentation.info` is the only
  source for the factor semantics at all, and the lessons log records that file's prose being
  wrong once on production semantics.
- Ratchet: `check_ai_layers --update-baseline` LOWERED LAYER4-NON-DECISION 333 → **328** and
  NUMBER-LEAK 356 → **347** — below where both sat before the war-floor entry (330 / 351),
  because six band triggers with their `num_of_military_factories` literals are gone and the
  one replacement trigger carries none.
- Verification OWED (unchanged in kind, new in target): the owner's own reading is the criterion
  — GER at ~500 military factories should show **~140 factories on tanks + specialised variants**
  in the production window, against the 85 measured at 1 June 1941. Save-side: the tank lines'
  `active` and `requested` totals, per class, at 1941.1 / 1941.7 / 1942.1. Boot test owed (new
  `ai_strategy` block, parses only at launch). If the campaign shows tank lines running BELOW
  their requested factories, the bound is allocation, not demand, and lever A is the wrong tool —
  that reading brings back a floor, this time on the `armor` category rather than one chassis.
- **ADDENDUM 2026-09-02 (owner: "les stratégies de production ne suivent pas le besoin" —
  variants first).** MEASURED, campaign `8c42d288` (63 monthly saves 1939.9→1944.11, 7 majors,
  save parse — Armour Ledger): the MAIN chassis runs full or in surplus (GER medium
  fielded/need 0.89 with stockpile 1.2× need, light 0.96 / stock 2×; USA medium 0.97; JAP
  0.91) while EVERY specialised variant of EVERY major sits in field deficit — GER StuG 0.56,
  light SPAA 0.41, medium SPAA 0.57, medium TD 0.66; ENG medium SPAA 0.30; USA medium SPAA
  0.45; ITA medium SPAA 0.52; JAP medium SPG 0.21. Correction to the previous addendum:
  `stock.py` sums stockpile + divisions + training queue; GER 1942.1 real stockpile of medium
  chassis is 479 (fielded 3 267 of 3 268 need, 516 in training), not 4 131 — the medium line
  was full, the variants starved. Two causes, MEASURED in code: (1) the variant factors were a
  fraction of the chassis factor (medium 150 +75 focus against SPAA 25 / StuG 45 / TD 60 /
  light SPAA 15), so the engine's template-proportional need was distorted a second time toward
  the chassis; (2) the variant gates read the armour ROLE — `build_light_armor_spaa` required
  `use_light_armor_templates`, false for everyone after 1940.1.1
  (`WA_AI_CONFIG_switch_from_light_to_medium_armor`), while the medium templates 6104 / 6106 /
  6109 / 6111 / 6112 / 6115 carry a LIGHT SPAA / SPG / infantry-support company — GER 1942.1
  on 6109 had no armed strategy for the SPAA its template demanded (2 factories, fill 0.15).
- Change (this entry, owner-directed: existing triggers + weights, no scripted computation, no
  factory floor): **parity rule** in `WA_AI_PRODUCTION_DEFAULT_tanks.txt` — every variant of a
  class carries its chassis factor (light 45, medium 150, heavy 60, modern 90), the three
  `focus_on_<class>_armor` blocks apply to the whole class (chassis + variants) instead of the
  chassis alone, and the duplicate heavy-assault line inside `build_heavy_armor` is dropped (it
  stacked to 90 with `build_heavy_armor_assault`). Values stay literals: `@` inside an
  `ai_strategy` payload is unverified (no vanilla or Expert AI file uses it) and `constant:` is
  not resolved there — parity is a stated rule in the file header, checked by eye.
  The modern infantry-support block stays commented as before:
  `WA_AI_TEMPLATES_has_modern_inf_support_unlocked` is an empty `OR` (no modern infantry-support
  tech exists, MEASURED `WA_AI_TEMPLATES_triggers.txt:1654`), so arming it would push an
  archetype nobody can build. Vanilla's own uses of this factor type sit in −100..60 (MEASURED,
  install `common/ai_strategy/*.txt`); WA now stacks up to 150 + 75 + 60 on the medium class —
  ASSUMED the engine honours the > 100 regime, nothing recorded either way.
  **Component gates** in `WA_AI_PRODUCTION_tanks.txt` — the 19 variant triggers read
  `WA_AI_TEMPLATES_use_<class>_<variant>_armor`, the very term the template ladders use (armour
  templates on + unlock), never the role. One narrowing to name: the assault-gun component
  triggers close on ANY lower-class SPG unlock (`WA_AI_TEMPLATES_triggers.txt:409`, `:416-417` —
  medium assault off once light OR medium SPG is researched, heavy assault off on light / medium /
  heavy SPG), where the old production gate closed only on the same-class SPG; this follows the
  template, which stops fielding the assault gun at the same point, so gate = demand. Chassis
  triggers, the light-support run, the category +60, mechanized blocks and floors: unchanged.
  DERIVED from `documentation.info` (factor = % of perceived need): a factor on an archetype no
  fielded template needs multiplies zero — the wider gates cost nothing.
- ASSUMED: `max_military_factories = 75` on every armour archetype (`tank_chassis.txt`) caps a
  line's request whatever the factor — the medium chassis already sat at 75 requested on
  `8c42d288` 1942.1, so the parity raise moves the VARIANTS, not the chassis; category and
  variant factors stack additively; under a saturated factory pool the
  engine serves lines in list order (GER 1942.1 StuG 8 of 11 requested, list position 13) — a
  larger variant request raises the variants' rank in that arbitration, which is the only
  save-visible mechanism left for them; if the next campaign shows variant lines still under
  their requested factories, the bound is allocation and this lever is spent.
- Verification OWED: boot test (ai_strategy parses at launch); next cloud campaign, Armour
  Ledger on its saves — every variant of GER/ENG/USA/ITA/JAP with need > 0 reaches
  fielded/need > 0.8 within 24 months of first need while the main chassis stays > 0.85; GER
  1942: StuG and SPAA lines at or above their requested factories.
- 4th post-fix reading, 2026-09-04 (`5d2a391c`, build commits `f5c342451`/`4c214b0ad`/`eefd8b5ea`
  confirmed live): MEASURED GER tank-family production lines (active/requested factories):
  257/283 @ 1941.1 (459 total mil factories), 151/152 @ 1941.7 (494 total — the ~500-factory
  bracket the original criterion names), 118/118 @ 1942.1 (548 total), 319/320 @ 1944.6 (655
  total) — every checkpoint runs at or within 1 factory of its own requested total, i.e. no
  starved tank-family line on this campaign; GER 1942.1 StuG-analog 38/38, medium SPAA 4/4, both
  AT requested (satisfies the GER-1942 clause of the `8c42d288` reading verbatim). Criterion (a)
  (~140 factories on tanks+variants at ~500 total) reads 151/152 at 494 total — above target.
  Caveat, stated honestly: this is an ALLOCATION proxy (active==requested), not the fielded/need
  ratio the Closed-when line actually asks for across GER/ENG/USA/ITA/JAP — `military_lines`
  carries no `num_needed` field, so the Armour Ledger fielded/need metric used in the `8c42d288`
  addendum was not re-derived this session. Still no verdict: the multi-country
  fielded/need > 0.8 reading remains the open half of Closed-when.
- Closed when: the campaign reading above holds on one cloud campaign, plus the original
  criterion (a major at ~500 military factories running ~140 on the armour category by mid-1941).

### bof-commonwealth-posture — PARKED (2026-09-02)
- Parked 2026-09-02 (WIP limit, `light-support-conversion` re-enters on an owner order; parked by the
  agent as the oldest OPEN subject with no console run pending — owner may swap). State at parking:
  OPEN — campaign `a2ad5f20` scored, Leg C PASS, Leg B mechanism PASS / Kuwait unsolved (options a-c
  owed to the owner), Leg A FAIL with root cause measured (Maghreb held by FRM/FRN/FRT subjects)
  and repair unshipped; the `imgui show ai-strategy` ENG sizing read is still owed.
- **Campaign `a2ad5f20` scored 2026-08-31** (cloud, BHU observer, 117 monthly saves 1936.2-1945.10,
  unbranched, difficulty normal = Historical). **BUILD CONFIRMED LIVE by positive control**: ENG's
  `protect_home_THEATRE` siblings (102 orders on 118/116/336) present while state 309 appears in
  ZERO ENG orders of either class in all 8 sampled saves, ENG at war — the deletion is in. Sequence
  near-historical (war 1939.9.20, Italy DoW 1940.6.5, France 1940.6.16, Barbarossa 1941.6.22.11,
  Pearl Harbor 1941.12.11, Torch 1942.10.1, D-Day 1944.6.7). Commonwealth armies grew normally
  (ENG 37→101, RAJ 49→47 peak 56, AST 10→22, SAF 1→18); ENG ends holding 75/77 states. No
  catastrophic regression anywhere.
- **Leg C (tripwire) — PASS on mechanism.** Both orders created **1939.9.22 (RAJ) / 1939.9.29-30
  (ENG)**, i.e. ~8.5 months before the Italian DoW, against "days to three weeks" before the
  widening. Frontier manned throughout the BoF (East Africa 7→12 divisions 1939.12→1940.5, Egypt
  +Libyan border 9→13), and the orders retire correctly at the Italian entry, converting to front
  /invasion (East Africa 9→22 at 1940.7). Outcome roughly historical: British Somaliland lost
  1940.7 (historically Aug 1940) but **retaken by 1940.10** vs March 1941 historically; AOI main
  position collapses 1941.8→1941.12 (historically Nov 1941), a 2-3 province rump surviving to
  1944.3. Open sizing question, NOT resolved: ENG schedules only **1-2** divisions per tripwire
  order against RAJ's **5-6** — a ratio is not recoverable from a save, so whether ENG's 0.12 is
  being consumed elsewhere needs `imgui show ai-strategy` on ENG, not another campaign.
- **Leg B (Gulf intent term) — PASS on mechanism, the Kuwait problem is UNSOLVED and the lessons
  reviewer's CONFLICT is now MEASURED.** Intended half works: IRQ carried **no wargoal and no
  justification** against ENG through 1941.4 (probe `section IRQ diplomacy --grep "wargoal|justif"`
  returns zero lines; positive control — GER/ITA/SOV all return blocks on the same save), so RAJ's
  Kuwait order scheduled **1-2** divisions instead of the surge's ~6-7. But the (f) table's ASSUMED
  premise — "the coup path carries war/wargoal before the surge matters" — is **FALSIFIED**: IRQ
  went neutral→war on **1941.4.24** with zero warning in the wargoal/justification channel, so the
  surge can arm at most 23 days before the shooting. Kuwait fell: controller GER already in the
  **1941.6.1** snapshot (baseline `8c0fea4c`: GER by 1941.9.20), recovered permanently 1943.3.
  Two different campaigns are NOT an A/B, so the 3-month difference is not attributable — what IS
  attributable is that the intent term cannot deliver force in this case. Options for the owner:
  (a) restore the massing→surge path but scoped to a masser that is not ENG-guaranteed / not a
  subject, (b) size the surge on the approach force rather than on intent, (c) accept the fall.
- **Leg A — FAIL, root cause MEASURED, my bug.** The African brake never covered the ground it was
  written for: **the Maghreb is controlled by French SUBJECTS — FRM (Morocco), FRN (Algeria), FRT
  (Tunisia) — not by FRA** (`control` over the 10 Maghreb states, all five BoF saves: FRM 4 / FRN 3
  / FRT 2 / FRA 1, no province-label disagreement). `WA_AI_MILITARY_is_western_bulwark_african_ground`
  reads `CONTROLLER = { WA_AI_CONFIG_MILITARY_is_western_european_bulwark }` = `original_tag = FRA`,
  which matches only state 1061 Bizerte. **Gabès (665) is CONTROLLED by FRT** — the claim is kept on
  control, not ownership, because the two diverge exactly in the Vichy/Torch window this leg avoids;
  never in the set. Result:
  **5-7 dominion divisions front-ordered at Gabès in every pre-fall save** (1939.12: AST 2 SAF 2 RAJ 3;
  1940.6: RAJ 4 AST 1 CAN 1), clearing only after the capitulation. Fix shape: the archetype must
  cover the bulwark's BLOC (add `is_subject_of` the bulwark), the same shape
  `WA_AI_MILITARY_is_french_africa_flank_quiet` already uses for Vichy. Same defect on a second
  front, out of v1's reach by construction (`is_on_continent = africa`): RAJ holds **front-ordered
  divisions inside the French Syrian mandate** — Halab 3 + Deir-az-Zur 1 at 1940.5, Rif Dimashq 1
  at 1940.6 (Levant controller **FRS**, also a FRA subject — same defect, second theatre).
- **Leg A repaired 2026-08-31 (owner order "vasy corrige"), v2 in the working tree.** New CONFIG
  archetype `WA_AI_CONFIG_MILITARY_is_western_european_bulwark_bloc` = the bulwark OR
  `OVERLORD = { bulwark }` — read through OVERLORD (18 existing uses in this repo) so it follows
  the archetype instead of naming a second tag; the state trigger is renamed
  `_is_western_bulwark_colonial_ground` and its geographic term widened from
  `is_on_continent = africa` to `NOT = { is_on_continent = europe }`, which picks up the Levant
  and keeps the metropole to the european leg so no state is vetoed twice. Verified before
  writing, not assumed: `relations 1940.5_May --tag FRA` lists subjects **FRC FRI FRJ FRM FRN FRO
  FRP FRS FRT FRV FRW**, and `control 554,680,677,901,553,665,458 1940.5_May` reads FRS 4 / FRT 2
  / TUR 1 — so both theatres resolve through OVERLORD.
- **Both reviewers ran on v2; both returned blocking items, all applied before commit.**
  Architecture CONFLICT (ECONOMY 2.4 rule 4, a veto reaching a homeland defender): the bulwark's
  own colonial subjects have NON-European capitals (MEASURED: FRM 461, FRT 458, FRS 554) and are
  Allies members through their overlord, so they passed the brake's audience and v2's first draft
  would have vetoed them off **their own soil**. Fixed in the control panel, not the block:
  `_is_overseas_guest_refused_by_bulwark` now also excludes the bloc. Lessons CONFLICT (the R34
  shape — a situational suppression whose only exit is a French event chain, while `NOT europe`
  handed it Indochina): fixed by bounding the geography to `africa` + `middle_east`. Also applied:
  `is_subject = yes` guarding OVERLORD (the only shape the repo's own WA_AI precedent uses), the
  (g) sentence in the `_bloc` header, and the two stale honesty claims (block `policy:` line and
  `WA_AI_MILITARY_SYSTEM.md` §24) re-worded to state the exclusion that actually shipped.
- **(f) walk of the colonial leg, per theatre and per phase** (the bound claim the lessons review
  required). Audience at every phase = overseas Allies guests **minus the bulwark bloc**.
  t0, war start with the gate closed: covered set = Maghreb (FRM/FRN/FRT) + Levant (FRS) ground the
  bloc CONTROLS; RAJ/AST/NZL/CAN/SAF refused there; Indochina, the Caribbean and the Pacific are
  outside the set **by continent**, so no veto exists there at any phase. t1, `fall_of_france` /
  bulwark capitulated / disjointed idea shed / non-historical difficulty: the gate opens and the
  whole block, colonial leg included, stands down — Torch and Vichy fronts are never touched.
  t2, the ahistorical branch where neither t1 term ever fires and Japan enters: the leg stays armed
  but still only over africa + middle_east, so the Asian fronts the dominions must hold are
  unreachable by it — this is what closes the R34 exit concern. Residual, accepted: while the
  bulwark still stands, a guest wanting to defend the bloc's Djibouti or Levant ground is refused,
  which is the rule the brake exists to state.
- **Leg B closed 2026-08-31 (owner order: "le signal idéologique avec le délai le plus long").**
  The premise the lessons review called CONFLICT is now not merely falsified but explained:
  **Iraq can NEVER hold a wargoal against ENG.** MEASURED in script — `IRQ_anglo_iraq_treaty`
  (`common/ideas/iraq.txt`) carries `rule = { can_not_declare_war = yes }`, and the focus
  `IRQ_the_habbaniya_incident` (`common/national_focus/iraq.txt`, `ai_will_do` 100 gated
  `date > 1941.3.11`) fires `irq_armor.805`, which removes the idea and `declare_war_on ENG` with
  `generator = { 656 }` in the SAME tick. Kuwait is not coveted — the war is fabricated around it.
  Every alternative tell (faction membership, loss of the ENG guarantee, loss of the treaty idea,
  the habbaniya flag) changes on the war day at **zero lead**; MEASURED campaign chain:
  `IRQ_dreams_of_iraq` 1940.4.4 → fascism 33 % (1940.9) → 43.15 % (1941.1) → 55.15 % (1941.3) →
  government flips ~1941.3.20 → war 1941.4.24. Fix: `_gulf_approach_massed`'s intent OR gains
  `WA_AI_MILITARY_is_in_an_enemy_ideological_camp` — the masser already governs by, or polls above
  0.45 for, the ideology of a power ENG is fighting. That is the longest-lead signal available
  (~2 months vs ~35 days for the government flip alone), it is tag-free and setup-agnostic, and
  0.45 is the same bar the seizure of power is itself gated on. **Neutrality is deliberately not
  enumerated** (unlike the Italian-entry pair, which asks whether two named majors align): it is
  the absence of a camp, and enumerating it would re-create the original false positive by reading
  every neutral neighbour's home army as hostile. Verification for the next campaign: on a save
  between the 0.45 crossing and the Iraqi declaration, RAJ's Kuwait order carries the 0.15 sizing
  (~7 divisions), and before that crossing it still carries 1-3.
- **Leg A1 re-diagnosed and extended 2026-08-31 (owner order: "je veux 0 sur la période voulue").**
  The earlier reading — "-100 is not a full veto" — was WRONG, or at least unproven: the residual
  has a simpler cause. MEASURED per-division attribution (`plans.py --where/--armies/--fronts/
  --oob`, 4 saves, closure test 12/12 PASS, no army-group inheritance, `NO_ORDER`/`UNATTACHED`
  absent): the 7 sightings are **4 front + 3 not-a-front**. The 4 are ONE order — RAJ Army 10,
  front instance 68, path Alsace-Lorraine + **Moselland + Baden + Württemberg**, i.e. straddling
  `france` and **`germany`**, and NO block in `common/ai_strategy/` put a negative
  `front_unit_request` on `germany` for a dominion. **Fix, after the owner asked whether the Raj
  could simply be kept out of Norway and Tunisia too — it can, and that is the better question:
  the five french area keys are REPLACED by one
  `state_trigger = { WA_AI_MILITARY_is_european_ground_barred_to_guests }` at -100.** An enumerated area list is always one theatre short — the measured leaks were a Rhine
  front in `germany` and Norway staging in `scandinavia`, neither named, and the Winter-War
  expedition to Finland is the same shape waiting to happen — and a per-state test also settles a
  front whose path straddles two areas, which was the open engine question. One targeting key, so
  no double-count and no value past the E2 floor. **Deliberately NOT mirrored into the RAJ Country
  veto**: that block's gate is `has_war = yes` alone, so it would be permanent and would keep
  Indian divisions out of Europe in 1944-45; the faction brake stands down at `fall_of_france`.
  The Tunisia half of the owner's question is already carried by the colonial leg (Gabès is FRT).
  The other 3 sightings are unreachable by ANY front lever and are not defects:
  AST Nord-Pas-de-Calais + RAJ Vlaanderen are on **Norway** army orders (and both states are
  German-controlled at that date), CAN Provence is on a **Tunisia** order, and the RAJ Provence
  "buffer" is assigned to our OWN Egyptian tripwire (order 9618, states {452,960}) sitting at the
  Marseille port en route — cutting it would re-open the Libyan frontier §20 exists to man.
  Bucket (d) expeditionary lending is EMPTY with a positive control (JAP←PGC 6-9 divisions lent in
  the same campaign, so the mechanism is live and the dominions simply never entered it).
- **Literal zero is not reachable and the probe was wrong to ask for it.** A division crossing a
  province cannot be forbidden by any `ai_strategy` type, so a `--where` headcount will always show
  transit. The probe now counts FRONT ORDERS whose path lies in France/Benelux/the Rhine
  (`plans.py --fronts` + `--armies`), which is the thing the brake can actually control.
- **(f) walk of the european leg — prevented is not evacuated, and the honest claim is weaker than
  "4 of 7 disappear".** t0, the block arms (guest at war, gate closed): the -100 lands on every
  European state at the front **except soil the mission owner OWNS** — its islands, Malta,
  Gibraltar, Cyprus — which stays defensible by the whole Commonwealth. t1, next AI
  front-reassignment tick: the request for those fronts is suppressed, so no NEW dominion division
  is asked for. t2, next monthly save: **whether RAJ's
  existing Army-10 Rhine order dissolves or merely stops being reinforced is UNKNOWN** — the
  lessons-log rule for the sibling case (`garrison` negative) is that a negative PREVENTS, it does
  not EVACUATE, and there is no measurement either way for `front_unit_request`. So the defensible
  prediction is "no new dominion front in Europe", not "the existing one vanishes"; if the campaign
  probe shows the order surviving, the remaining lever is a `put_unit_buffers` catcher parking the
  refused guest at home (the §23 mechanism, MEDIUM risk, not shipped). **ASSUMED, source-labelled:**
  "-100 is a full veto" is `WA_AI_MILITARY_ECONOMY.md` §3 E2, a NORMATIVE repo rule, not an engine
  measurement — nothing in the log settles it empirically.
- **Sea Lion carve-out (owner catch 2026-08-31, "ajouter une exception pour le royaume uni en cas
  de sea lion" — and the trigger renamed with it).** The British Isles ARE European ground, so the
  continent key as first written would have vetoed the whole Commonwealth off the defence of
  Britain: the ECONOMY 2.4 starvation shape, reachable precisely by compounding it with risk (1)
  below. `_is_european_ground` → `_is_european_ground_barred_to_guests`, now excluding
  `WA_AI_MILITARY_is_mission_owner_soil`. The old name was also simply wrong — it read as a
  geography fact while the trigger encodes a policy. On the historical path `fall_of_france` opens
  the gate long before any landing, so this is insurance for the ahistorical branch, not the common
  case. **OWNER only, and the CONTROLLER disjunct was dropped in review**: the first draft carved
  out ground the mission owner merely OCCUPIES, which un-barred an ENG-occupied Norway or a
  liberated bridgehead — the exact continental soil the gate exists to keep guests off, reachable
  in the very branch this insurance targets. Owner survives an occupation, which is the case that
  matters. Verified rather than assumed (the trap that made the colonial leg inert): the British
  home states read `owner = ENG` in `history/states` and ENG 9/9 by state and 46/46 by province in
  the 1940.6 save — no subject-tag layer like the Maghreb's FRM/FRN/FRT. The carved set is the
  owner's whole European holding, **not the Isles alone**: Malta 116 and Gibraltar 118 are
  `owner = ENG` (MEASURED), and the review adds Cyprus 183 — a Levant-theatre state the colonial
  leg's `middle_east` bound does not reach. Two residuals accepted: an ANNEXED Britain (owner no
  longer the mission owner) would leave guests barred from liberating it, and a non-British guest
  owning European soil — a US bridgehead on the ahistorical branch — is vetoed off its own ground;
  the trigger header names both as the assumption to watch. The only script path that ends the
  carve-out is the REN release (`common/decisions/GER.txt:6146-6169`, `transfer_state` 119-133),
  whose `controls_state` precondition means Britain is already lost end to end before it fires.
  Two deliberate choices, recorded so they are not silently "fixed": **(i) the rejected generic.**
  The bulwark bloc test one commit earlier uses `OVERLORD = { archetype }` because it asks a
  COUNTRY-scope question ("is this country in the bulwark's bloc"); this one asks a STATE-scope
  identity question ("is this soil the mission owner's"), and every member of the brake's audience
  is that owner's subject, so the archetype is equivalent and shorter. The asymmetry is intended.
  **(ii) Irish soil is NOT carved out** — states 113/134/135 read `owner = IRE`, so a guest stays
  barred there, which is the brake's intent: Ireland is not the mission owner's ground. Also
  deliberate: the sibling `_is_western_bulwark_colonial_ground` keeps a geography-shaped name
  because its body IS a geography-plus-ownership fact, where this one carries a policy carve-out.
- **Accepted risks, recorded rather than bounded (both raised by the lessons review).** (1) The
  european leg's only exits are France-shaped (`fall_of_france` / capitulated / out of faction /
  disjointed idea shed / non-historical difficulty). On an ahistorical branch where France SURVIVES
  and keeps a disjointed-government idea indefinitely, overseas guests stay vetoed off CONTINENTAL
  European ground with no bound — British soil now excepted, which was the dangerous half. One-line
  fix if the rest bites: add a calendar or "bulwark no longer at war" limb to
  `_western_bulwark_accepts_guests`. (2) Leg B's camp
  test has no path for a masser that is ideologically aligned but NEUTRALITY-ruled with its camp
  polling under 0.45 — the Nationalist-Spain shape from the lessons log, where fascism never passed
  neutrality. Its wargoal limbs are blocked too, so such a masser arms no surge at all.
- Open engine question, ASSUMED, owner-settleable in one screenshot: which area the engine matches
  a front to when its path straddles two (now moot for this leg, since it targets per state). `tag RAJ` + `imgui show ai-strategy` mid-battle — if the
  Rhine front already resolved to `france`, the `-100` was reaching it all along, the new `germany`
  entry is a no-op, and the only remaining lever is a `put_unit_buffers` catcher parking the
  refused guest at home (the mechanism §23 proved on CAN; MEDIUM risk, unresolved two-order
  arbitration, not shipped).
- **Leg A1 (benelux) — PARTIAL.** Dominion presence in metropolitan France/Benelux is down to
  **1-3 divisions per save** (RAJ Moselland + Alsace-Lorraine 1940.3/1940.5, RAJ Vlaanderen +
  Provence 1940.6, AST Nord-Pas-de-Calais 1940.6) but never zero, with both the Country -100 and
  the Faction -100 armed. **RETRACTED 2026-08-31, same day:** this bullet first read that as
  "`-100 is a full veto` is FALSIFIED". The per-division attribution below shows the residual is
  ground the vetoes never named (`germany`) plus transit, so the strength of -100 is UNTESTED by
  this campaign, not disproven. Nothing here supports escalating the value.
- Unrelated anomalies surfaced by the same pass, NOT admitted as subjects (one line each, per the
  admission rule): Axis held **Marsa Matruh 1943.2-1944.1** (14 months) and Libya was not cleared
  until 1945.6-10 — far downstream of a 1939-40 positioning change, cause unknown; **SAF drops 6→1
  divisions between 1939.12 and 1940.3** and only rebuilds in 1943-44; ENG home defence fell 16→11
  across the May→June 1940 saves with Yorkshire never refilled (the 5 divisions went to the BEF and
  Alexandria, not to Africa — regression risk (1) NOT realised).
- Scope: owner order 2026-08-31 ("Implémente A, B et C" on the save_demo Discord report,
  campaign `0700e591`, save at 1940.6.1, Historical Normal). One subject for the three legs of
  one intended behaviour: during the Battle of France the Commonwealth stands in Egypt / East
  Africa / the Gulf at the right size — not in France, not on the French side of the Maghreb,
  not seven divisions deep in Kuwait. Code committed + pushed 2026-08-31 (`4d11dbe1d`).
- Symptom, MEASURED (save_demo, plans.py --where + order dump): RAJ 6 front divisions in
  Île-de-France/Picardie/Provence and 4 at Gabès (+ AST 1) with the bulwark gate CLOSED
  (difficulty=normal → Historical); RAJ Kuwait scripted order carried 6 scheduled divisions
  (the 0.15 surge tier — IRQ, neutral, no wargoal, holds 3 divisions in Dhi Qar, which is all
  `gulf_approach_massed` asked); ENG scripted a 0.10 garrison of state 309 = SURINAME under a
  `# middle_east` comment (order created 1940.5.12, 2 divisions scheduled); the Italian-entry
  tripwire (§20) armed only days before the declaration (collapse limb) at ratios 0.06/0.04.
- Leg A (France/Maghreb): `benelux` added to the RAJ Country veto
  (`WA_AI_MILITARY_COUNTRY_RAJ_FRONT.txt`, its measured hole); colonial leg added to the faction
  brake — `state_trigger = { WA_AI_MILITARY_is_western_bulwark_colonial_ground = yes }` at -100
  (STATE-scope observation trigger: `NOT is_on_continent = europe` + CONTROLLER is the bulwark
  BLOC) in `WA_AI_MILITARY_ALLIES_overseas_guests_wait_for_bulwark`. **v2 2026-08-31 after
  campaign `a2ad5f20` measured v1 inert** — v1 asked `CONTROLLER = { _is_western_european_bulwark }`
  (= `original_tag = FRA`) over `is_on_continent = africa` and matched only Bizerte; see the
  campaign bullet above for the measurement and `WA_AI_MILITARY_SYSTEM.md` §24 for the rule. ASSUMED (stated in
  the brake's own header since 2026-08-27): -100 fully suppresses engine default assignment —
  save_demo shows RAJ on French fronts WITH the brake armed, so either the reporter's build
  ("WA Beta GITHUB", revision unverifiable from the save) predates the 27/08 brake or -100 is
  not a full veto. Owner imgui (`imgui show ai-strategy` on RAJ during a BoF) settles which;
  if the brake was armed and beaten, the value needs escalation, not more areas.
- Leg B (Gulf/Caribbean): Suriname `ai_strategy` block DELETED from
  `WA_AI_MILITARY_COUNTRY_ENG_THEATRE.txt` (nothing else pools its order 7; intended state
  unrecoverable). `WA_AI_MILITARY_gulf_approach_massed` gained an intent term (war OR wargoal
  OR justifying against ENG) — the 0.15 surge tier no longer arms on a neutral's peacetime
  army; ratio deliberately NOT lowered (the 0.15 sizing encodes the measured 1941 Kuwait fall,
  1 guard vs 7). Deviation from the tier author's design, named: their "massing alone is the
  reason" now requires intent; mine covers their 1941 case because the coup path carries
  war/wargoal before the surge matters, and the 0.05 watch + `_imminent` (massing kept there)
  still pre-position. (f) timeline at real cadences (per lessons review, the historical shape
  MEASURED on `8c0fea4c`): t0 pre-coup — watch 0.05 ≈ 2 div standing in 656, `_imminent`
  armed; t1 coup→hostility (historical Golden Square: coup 1941.4, war 1941.5.2; worst case a
  wargoal-less event war = surge arms only at t_war) — surge 0.15 arms, ~5 more divisions
  travel from India/Levant ≈ 4-8 weeks; t2 the measured fall took ≥ 3 months after t1 (state
  656 friendly at 1941.4.28, GER-controlled only by 1941.9.20) — arrival window ≥ fall window
  even in the worst case, floor never empty. ASSUMED, not save-decidable: WA's coup path
  actually produces a wargoal/war (an ahistorical masser that never justifies gets no surge
  ever — the probe line below watches for exactly that). Residual accepted: ENG's ~1 division
  in Kuwait is an ENGINE areadef order (Kuwait/Abu Dhabi/Qatar) — no script writes it, not
  addressable without an ENG-wide garrison suppressor.
- Leg C (pre-positioning): third OR limb in `WA_AI_MILITARY_italian_entry_likely` — the German
  homeland power (new CONFIG archetype `WA_AI_CONFIG_MILITARY_is_german_homeland_power`) at war
  with a non-capitulated bulwark — the §20 recorded widening, giving ~10 months of warning on a
  historical timeline instead of days; tripwire ratios 0.06/0.04 → 0.12/0.10 (owner rule:
  pre-positioned, not merely non-empty). Escape hatches unchanged (`NOT home_threatened`,
  audience ENG+RAJ, release on Italian entry). Two OWNER live working-tree tweaks made in
  parallel during the same session were preserved and folded in:
  `western_bulwark_is_collapsing` bar `surrender_progress > 0` → `> 0.4`, and the tripwire
  date fallback `1940.8.1` → `1940.9.1` — both compatible (the new war limb arms earlier than
  either, and `italian_entry_likely` is the collapse trigger's ONLY consumer — grep 2026-08-31).
- Regression risks, stated: (1) leg C parks ~14 ENG+RAJ divisions in Africa from late 1939 —
  if ENG home defence thins before `home_threatened` trips, the ratios come back down; (2) leg
  A's state_trigger brake covers ALL bulwark-controlled African ground incl. West Africa and
  Djibouti — intended (guests have no business there pre-fall), released with the gate; if
  Italy enters BEFORE France falls, the East-Africa faction +150 (area-keyed) and this -100
  (state_trigger-keyed) meet on FRA-controlled Somaliland fronts and cross-target summing is
  ASSUMED (the ai-strategy-window note: whether the engine sums across targeting keys is
  unresolved); (3) leg B may arm the Kuwait surge days later than before on the 1941 coup path
  (intent term) — the watch floor holds the gap, (f) table above. ASSUMED throughout (carried
  from the brake's own 2026-08-27 header): front_unit_request -100 fully vetoes engine default
  assignment — save_demo shows it beaten or absent; the owner imgui check below settles it.
  Tripwire buffers got `subtract_fronts_from_need = no` (lessons review): the default lets live
  front demand eat a yielding buffer, which during the BoF is the whole pre-position.
- Probe (next campaign reaching 1940.6 on this build): pre-fall saves show zero RAJ/dominion
  divisions on metropolitan-France/benelux fronts AND zero on FRA-controlled African states;
  tripwire buffers 9617/9618 exist from ~1939.9 with ENG+RAJ divisions standing in
  551/1096/549/1100/269/659 and 452/960 during the BoF; RAJ Kuwait order carries ≤3 scheduled
  divisions while IRQ is neutral; no ENG order on state 309. Surge-side probe (lessons review):
  on any save where a non-aligned power both CONTROLS an approach state and masses >2 divisions
  in one AND is at war/holds a wargoal vs ENG, the RAJ Kuwait order must read the 0.15 sizing —
  a surge disarmed in that cell is the narrowing over-shooting. Owner imgui (once, any BoF
  save): `imgui show ai-strategy` on RAJ — `overseas_guests_wait_for_bulwark` and
  `RAJ_unit_distribution` listed in Active strategies while RAJ still fronts in France would
  prove -100 is not a veto and the value needs escalation, not more areas.
- Closed when: one campaign (historical difficulty, unbranched) shows all four probe lines
  PASS at a save between 1940.4 and the Italian declaration, and the owner confirms the
  Battle-of-France report symptoms gone (or re-reports with a new save).

### light-support-conversion — PARKED (2026-09-09)
- Parked 2026-09-09 on the owner's order (admission of `air-budget`, WIP limit: 8 under OPEN for 4); move it back to OPEN in one line when its owed item lands. State at parking: SHIPPED-UNTESTED 2026-09-08; owner in-game report 2026-09-09 "les changements locaux marchent", harness output not yet pasted - paste it here and move to TESTED, no session work pending.
- Owner in-game report 2026-09-09, cold boot, working tree without Change 14: "les changements
  locaux marchent". Harness output not yet pasted, so the status stays. Owner live edit the same
  day, in the tree and this commit: the "Tankovaya brigada" deletion is removed from BOTH mission
  effects (complete_effect and timeout_effect) - the OOB brigades keep their units and template
  and bridge through STARTER_MIX under 15009; only the two cavalry templates lose their divisions
  (`delete_units`, templates kept). Change 13's "the deletion stays" ruling is superseded by this.
- Unparked 2026-09-07 on the owner order below; slot freed by parking `coal-prospect-loop`.
- **Change 14 (owner order 2026-09-08 "un event pour l'ia qui, une fois la mission accomplie, si la
  date est avant 1942, supprime tous les chars, puis respawne 30 chars au template 30w, avec 1%
  d'équipement") — delete + respawn replaces the designer-driven 44w -> 30w conversion.**
  - **STASHED 2026-09-09 (owner order)**: taken out of the working tree, not committed, to test
    whether the hot-reloaded build alone explains the missing 30w (lessons entry "A hot script
    reload can also stall the AI's own template upgrades"). Patch = `E:/Projets/HOI4/WA/
    stash-change14/change14-respawn.patch` (`git apply` from the repo root; `git apply --check`
    passed on the reverted tree), full copies of the seven files under `stash-change14/full/`.
    Kept in the tree: Changes 12-13, the mission's units-only deletes, the lessons entry.
  - **DROPPED 2026-09-09 (owner cold-boot control: "les changements locaux marchent")**: with the
    same files and a fresh executable the local changes behave; the missing 30w was the
    hot-reloaded build, not the design (the XP-starvation reading stays MEASURED on the save but
    is not the blocker the owner saw). The patch stays at the path above in case a campaign shows
    the 44w park again; nothing of Change 14 is in the tree or the commit.
  - Why (MEASURED, autosave 1941.2.1 of the owner's game + `imgui show ai_templates` 1940.4.27):
    30 divisions still on "Light Support Tank template A" = the 44w corps (12 LS / 6 L / 4 mot) 27
    months after the mission; no other light-support template; the arrow correctly on the MIX,
    best match 0.28; `army_experience = 10.1`, `army_experience_daily_training = 0.015`; the
    light-support role has 5.7 % of the design lottery (panel weights 71.9 vs infantry 733).
    Engine rule (install `common/ai_templates/_documentation.md`): the AI never creates a
    template, it copies the best match and edits it toward the target; A -> MIX needs >= 15
    single edits at 5 XP each with ~0 XP income. The same reading explains the missing medium /
    heavy rows: books `wa_ai_armor_budget_light=8 medium=8 heavy=4`, flags 6101 / 7105 set,
    targets enabled, and SOV owns no template with a medium or heavy battalion (7 templates in
    the save) - a role row needs an enabled target AND an owned template. Lowering
    `target_min_match` (owner's live edit) changed nothing: the chain has no 30w-like template
    to move divisions to.
  - Shipped: `WA_AI_TEMPLATES_delete_light_support_park_templates` (the A..Z + OOB sweep, moved
    out of the retire effect, plus the scripted name); `WA_AI_TEMPLATES_reset_light_support_park`
    = sweep, `division_template` "Legkaya Tankovaya Diviziya" (exact MIX composition, x/y grid
    with the 4 + 4 regimental supports on the four >= 3-battalion columns), `create_unit` x
    `tank_park_hold_divisions` in `capital_scope` at `start_equipment_factor = 0.01` (manpower
    engine default, ASSUMED full), flags `WA_AI_TEMPLATES_ls_park_reset` + `ls_bridge_done`,
    immediate recalculation of the role target, game.log line; `sov_armor.982` (hidden,
    triggered, once; AI + historical + park country + before 1942 + not retired) fired with
    `days = 1` from the mission's `complete_effect` AI branch after its own sweep - the timeout
    keeps the sweep alone (owner: "accomplie"); new constant
    `wa_ai_production.army_composition.tank_park_hold_divisions = 30` owning both the respawn
    count and the hold's `build_army value = 30` (regex mirror in `tools/constants_registry.json`
    - `constant:` does not resolve in `ai_strategy value =`); harness `lsphase` prints `reset` and
    `30w-template`; doc section rewritten.
  - Interplay: the reset sets `WA_AI_TEMPLATES_ls_bridge_done` and recalculates the role target
    at once, so the flag lands on STABLE 15010 (MIX alone) the day after completion; PONT is
    skipped for the rebuilt park (it bridged a corps that no longer exists). CONVERT-1 on the
    T-34 / KV-1 is unchanged: the rung matches the scripted template at ~1.0, and the FINAL needs a
    medium-like template that the same XP starvation still withholds - NEXT GAP, not fixed here.
    The hold keeps wanted at 30 so the share (8 % = 19) does not decommission the rebuilt park.
    Supports: the six the 1936 Soviet tech set has are in the template; maintenance / field
    hospital / signal are added by `add_units_to_division_template` under `has_tech`
    (`tech_maintenance_company` / `tech_field_hospital` / `tech_signal_company`, MEASURED
    `enable_subunits` join; the AST template uses the same guard).
  - t0/t1/t2 (daily events, 7-day designer pass, monthly calculator; DERIVED):
    | t | flag | enabled targets | park | expected |
    | --- | --- | --- | --- | --- |
    | t0 completion | 15006 | 44_TEMPORARY (44w) | corps + copies, brigades / cavalry deleted | +100 XP paid; a 7-day designer pass may land on this day, harmless: the park is still the 44w corps matching its own target at ~1.0 |
    | t0 + 1 d reset | 15010 | MIX alone | 30 x scripted 30w at 1 % | best match 1.0 (< 1.0 only until the three support techs exist) - nothing for the designer to edit; the MISSION branch is closed by `ls_park_reset` whatever `has_active_mission` reads |
    | t0 + 7 d .. monthly | 15010 | MIX alone | equipment filling from the refunded stock | calculator re-lands on 15010 every pulse (latch + bridge-done, mission inactive) |
    | t T-34 / KV-1 | 15007 / 15013.. | rung + FINAL | rung match ~1.0 | FINAL needs the medium / heavy template - next gap |
  - ASSUMED (i) `division_template` in an event `immediate` accepts `division_names_group`
    (OOB syntax; the boot test tells); (ii) `create_unit` `count = <temp var>` in `capital_scope`
    (form of `WA_AI_DIVISION_spawn_divisions`, meta_effect there); (iii) the disbanded corps
    refunds the chassis the 1 %-equipped divisions then draw. (`days = 1` and the reset flag on
    the calculator's MISSION branch are belt and braces: whatever `has_active_mission` reads on
    the reset day, the value cannot return to 15006 once the park is rebuilt.)
  - Drift risk, stated: the 30w composition is declared twice (ai_templates target and the
    scripted template) and no checker joins them; the only join is the imgui best match 1.0 on
    `30_MOT_LIGHT_MIX`, ASSUMED until the owner's console run prints it.
  - Owner order (same day, after the reviews): the mission's six `delete_unit_template_and_units`
    (complete_effect + timeout_effect: Kazachya / Kavaleriyskaya / Tankovaya brigada) become
    `delete_units` with the same `has_template` guards and `disband = yes` - units go, templates
    stay. Owner order 2026-09-09 "corrige l'event du lendemain": the reset now calls
    `WA_AI_TEMPLATES_delete_light_support_park_units` (delete_units on the two OOB names and the
    scripted rebuild, templates kept) + `WA_AI_TEMPLATES_delete_light_support_engine_copies`
    (the A..Z copies go with their templates); the retire keeps the full template sweep
    (`..._park_templates` = named templates + copies + MISS log).
  - Reviews 2026-09-08: lessons CONFLICT (44w target left over the rebuilt park for <= 3 months
    with 100 fresh XP; three unresearched supports; harness caveat) - all three applied
    (STABLE at reset via bridge-done + recalculation and `days = 1`; guarded supports; caveat
    in the harness comment); architecture CONCERNS (registry regex unbounded past the block;
    drift risk to state) - both applied (the mirror pattern refuses to cross a top-level `}`
    line, so a removed `value` line fails instead of capturing the next block; the line above).
    Second round: lessons CONCERNS (MISSION-branch exit resting on `has_active_mission` timing;
    t0 row wording) and architecture CONCERNS (`ls_park_reset` had no gameplay reader; calculator
    caller list) - all applied: the MISSION branch now reads `NOT ls_park_reset` (its gameplay
    reader), the caller list names the reset, the t0 row reworded.
  - Verification - owner console: restart; load a save BEFORE the mission completes (it fires from
    the completion, a post-mission save cannot replay it); run past completion without tagging
    SOV; `game.log` "rebuilt the light-support park: 30 divisions", and NO
    `add_units_to_division_template Not allowed` / `Trying to fill variant where none exist`
    line (`error.log` too); `sov-tank-mission-active=0` on the flags line; `event wa_abg.3 SOV`:
    `reset=1 30w-template=1 stable-15010=1 bridge-done=1`, park line `hold-30=1`; `imgui show
    ai_templates`: arrow on `30_MOT_LIGHT_MIX`, best match "Legkaya Tankovaya Diviziya" at 1.0
    (or the support-tech-bounded value below 1.0 before those techs); AI production panel:
    `light_armor` current 30 / wanted 30. Controls: timeout path (no rebuild), competitive SOV (no rebuild),
    1942 retire still deletes the scripted template (`retired=1 30w-template=0`).
  - Verification - campaign: SOV division count at mission end = pre-mission - brigades -
    cavalry - corps copies + 30; the 30 sit on the scripted template with rising equipment; the
    medium / heavy rows still absent until the next gap is closed.
- **Change 13 (owner order 2026-09-08, two panel screenshots 1938.11.1 / 1938.11.4) — the park
  survives the mission's end; 30 light-support divisions held until the T-34 / KV-1.**
  - Symptom, MEASURED (owner screenshots, build = working tree of Change 12): 1938.11.1 18:00
    167 active divisions, `light_armor` current 67 / wanted 100; 1938.11.4 124 active (-43),
    the `light_armor` row absent from the AI production panel, infantry current 86.6 -> 98.6.
  - Cause (script lines): (1) `SOV_factions.txt` mission `complete_effect` / `timeout_effect`
    delete "Tankovaya brigada" (21 OOB divisions) and "Kavaleriyskaya Diviziya" (30) with their
    units (`3b865fa8f7`) — 43 <= 51, the rest had already field-upgraded off those names. Owner
    ruling: the 18w brigade and the cavalry ARE dead weight; the deletion stays. (2)
    `WA_AI_TEMPLATES_armored_light_support.txt` `_44_TEMPORARY` enable = 15006 AND mission
    active; the calculator writes 15009 only at the next monthly pulse, so the role had ZERO
    enabled targets for up to a month and vanished from the panel — the row was gone while the
    light book still read 15 (the monthly reconcile precedes the 18:00 screenshot), so neither the
    role_ratio share nor `build_army` can hold a role with no target. Change 12's slot is
    complementary (it funds the FINAL divisions that stay in the light group), not the cure.
  - DERIVED from the 1938.11.1 panel: `build_army id = light_armor value = 100` read as wanted
    100 — the value is a wanted division count. The owner's `value = 30` proposal rests on that.
    CONFOUNDED: that reading was taken with `force_build_armies 300` and the role_ratio slot both
    live, so one data point cannot separate "absolute count" from "additive to the share"; the
    console check below (wanted exactly 30) is the killing measurement and stays blocking.
  - Shipped: `_44_TEMPORARY` enables on 15006 alone (values exclusive by construction since
    Change 11); `WA_AI_PRODUCTION_should_hold_historical_tank_park` (historical, park country,
    mission over, temporary latch, not retired, no major enemy, training allowed, SOV switch
    closed = T-34 / KV-1 not researched and before 1942) gates
    `WA_AI_PRODUCTION_DEFAULT_historical_tank_park_hold` = `build_army id = light_armor value = 30`,
    no `force_build_armies`; harness `wa_abg.3` prints `hold-30` (a reading of the shipped gate,
    not a retype) and `target-live` (set membership over the 17 declared values 15000-15016, not
    an enable evaluation; the STARTER `has_template` terms are not retyped); doc section
    rewritten. Deletion untouched. `tools/ai_layers_baseline.json` NUMBER-LEAK 338 -> 335 updated
    in the same commit: MEASURED the drop is inherited from merge `e670dfd372` (`WA_triggers.txt`
    10 -> 7, `WA_production_strategy_effects.txt` 2 -> 0, `WA_AI_PRODUCTION_air.txt` 0 -> 2), the
    four files touched here count identically at HEAD and in the working tree.
  - Reviews 2026-09-08: lessons CONCERNS (confounded wanted-100 reading; latch dependency;
    `target-live` wording) and architecture CONCERNS (rule 7 comment phrasing; `hold-30` is a
    reading; baseline provenance) - all applied. Latch dependency, stated: the hold needs
    `WA_AI_TEMPLATES_sov_light_support_temporary_latched`, written only while the mission is live;
    a save whose mission ended on a build predating the latch never arms it (no migration owed
    unless such a save is scored).
  - t0/t1/t2 (monthly calculator, 7-day engine selection, daily ai_strategy enable ASSUMED):
    | t | flag | enabled targets | wanted | expected |
    | --- | --- | --- | --- | --- |
    | t0 mission end | 15006 | 44_TEMPORARY (44w, no chain) | 30 (hold arms) | brigades + cavalry deleted by the mission; corps + copies stay in the role; recruits <= 30 - current on the 44w shape |
    | t1 next pulse | 15009 | CONVERT 44w (15) + MIX 30w (10) | 30 | arrow on the MIX; recruits still land on the 44w CONVERT (highest prio) |
    | t2 = t1 + 2 pulses | 15010 | MIX alone | 30 | recruits on the 30w; 44w divisions upgrade to the MIX |
    | t3 T-34 / KV-1 | 15007/15013... | rung + FINAL | share only (hold closes) | conversion window as Change 11 |
    Residual: <= (30 - current) divisions queued on the 44w shape during <= 3 months (ASSUMED the
    queue follows the template's field upgrade); how many of the 30 exist before the T-34 is
    training-time-bound, not script-bound.
  - Verification — owner console: restart the exe; post-mission pre-T-34 SOV save, no tag
    switch; `event wa_abg.3 SOV`: scope `1 1 1 1 0`, `continues=0`, `force-500=0`, `hold-30=1`,
    `light-role-open=1`, `target-live=1`, verdicts 1 1 1 1; the AI production panel must show
    the `light_armor` row with wanted EXACTLY 30 - "30 + share" or a percent refutes the
    wanted-count reading of `build_army` and the 30 is recomputed, not tuned. Controls:
    mission-active save (`hold-30=0`, `force-500=1`), post-T-34 save (`hold-30=0`), competitive
    SOV (`hold-30=0`).
  - Verification — campaign: the SOV division count across the mission's end drops by the OOB
    brigades + cavalry still on their names and by nothing else; `light_armor` current climbs
    toward 30 before the T-34; FINAL shapes carry the park after it.
- **Change 12 (owner order 2026-09-08) — keep the historical Soviet light budget open until 1942.**
  - Owner report: light need falls to zero when the mission ends; two thirds of the LS divisions
    disappear. ASSUMED causal link between budget withdrawal and those deletions; this change
    implements the requested retention policy, not a demonstrated engine-level cure.
  - MEASURED cause in script: `WA_AI_PRODUCTION_build_army_light_armor` vetoed historical SOV
    when `should_continue_historical_tank_park` closed, and also required a live light-template
    use trigger. Both gates could withdraw funding before the park finished conversion.
  - Implemented: exclusive historical-difficulty + CONFIG park-country branch, with the existing
    master gate, `before_global_war_begins` (`date < 1942.1.1`), a carried LS template flag and
    no retired flag. No mission, cap, major-war, expansion or light-template-use condition in
    that branch. No fallback to generic light after the boundary. Generic non-historical-SOV
    behavior is logically unchanged (its old mission exception required historical SOV).
  - Impact: only gameplay caller is `WA_AI_ARMOR_BUDGET_reconcile`; startup and monthly scheduling
    remain unchanged, with template calculation before reconciliation. Harness is the other
    reader. No change to mission continuation, its floor/force bonus, equipment policy, template
    phases, conversion gates or retirement. No new constant, CONFIG declaration or telemetry.
  - `WA_TEST_armor_budget.txt` independently retypes the new light gate. Its split expectation
    also now includes the existing master/expansion gates and SOV medium-switch exclusion;
    its floor expectation matches gameplay's either-cap-unmet condition and retired guard.
    These are measurement corrections, not changes to medium/heavy or floor gameplay.
  - Scenarios: historical SOV post-mission PONT/STABLE/CONVERT-1/CONVERT-2 keeps its ordinary
    light share, including FINAL targets still in that role. Competitive SOV and non-SOV
    countries use the previous generic path. Retired/missing-flag historical SOV closes;
    historical SOV at/after 1942 closes even if its mission remains active. No-training still
    zeros the budget independently of the open-role gate.
  - Regression risk: reopening light redistributes the ordinary tank budget from other open
    roles and permits recruitment in the park role. ASSUMED extra recruitment can compete
    for conversion equipment; no bound or guarantee on division retention/conversion time.
  - Final diff reviews: lessons CLEAR (carried-flag/retired guards, exclusive historical branch
    and retained brakes); architecture OK.
  - Validation (2026-09-08): constants and AI-layer checks exit 0; brace nesting and
    `git diff --check` pass; template-checker selftest passes. Parsed light-gate truth table:
    2 048 boolean combinations match the requested policy, including 1 536 generic cases
    identical to HEAD (offline logic check, not an engine test). Global template check still
    reports 4 HQ suffix errors / 48 warnings; all its inputs are unchanged. Worklist check
    reports 3 existing errors (8 OPEN, two stale untested subjects), confirmed identical by
    running its WORK checks against HEAD in memory. No unrelated tracker or HQ edit.
  - Verification — owner console: restart the game; on the post-mission 1939 save, without
    tag-switching, `event wa_abg.3 SOV` must show scope `1 1 1 1 0`, `continues=0`, `force-500=0`,
    `light-role-open=1`, positive light book if training is allowed, and all four verdicts 1.
    Repeat during conversion (including KV-1-only admission), and at/after 1942 (light book 0).
    Controls: competitive SOV, non-SOV and mission-active one-cap-reached case. The calendar
    gate changes immediately; normal applied books change on the next monthly reconciliation.
  - Verification — campaign: follow the same historical Soviet divisions from mission end
    through medium/heavy conversion; before 1942, a carried unretired park with training allowed
    must retain a positive `WA_AI_ARMOR_BUDGET_light` after reconciliation. Record deployed
    park counts/shapes to test the owner's retention hypothesis. Existing conversion criteria
    remain; this change additionally closes only after these console and campaign checks pass.
- **Change 11 (owner order 2026-09-07 "vas-y, implémente dans l'ordre C, B, A+D, D bis") — every
  bridge of the temporary corps carries its own exit; medium and heavy open on the T-34 / KV-1.**
  Owner intention (same day): mission over → the 44w corps goes to the 30w MIX and STAYS there;
  medium opens when `sov_medium_tank_chassis_3` (T-34) is researched, heavy when
  `sov_heavy_tank_chassis_2` (KV-1) is; the 30w park converts directly into whichever class is
  open. The mission-end budget closure left by this change is superseded by Change 12 above.
  - Symptom, MEASURED (campaign `a100b67c`, BHU observer, 132 monthly saves 1936.2-1947.1,
    unbranched, build of 2026-09-06 evening; full timeline in scratchpad
    `a100b67c_SOV_templates_timeline.md`): mission completed 1938.11 (1156 days early). Then the
    whole park (37 divisions, pinned 1939.06-1941.10, armour budget 0/0/0/0 for 14 months) walked
    6/3/4 → 7/3/4 → 8/3/4 → 9/3/4 as ONE pool (1939.12, 1940.01, 1940.02) — the 7/3/5 MIX was
    never fielded in 132 saves; flag 15007 at 1940.2 on a T-28 medium role (T-34 researched
    1940.6.27, KV-1 1940.6.23); 31 divisions on the 9 med/6 mot FINAL by 1941.02, then 18 of them
    walked back onto light shapes 1941.05-1941.08 (tid 2438 = 3 LS/6 mot/2 art, tid 2488 = 4 LS/
    5 L/5 mot) before landing on the medium role's own template 1941.08; 18 OOB brigades went to
    "Motorized Infantry template A" in 1939.01; `sov_armor.981` fired 1942.1.4 on an
    already-medium park; 12 707 support chassis byte-identical in stock 1942.6-1947.1.
  - Cause (script lines): (C) `WA_AI_CONFIG_switch_from_light_to_medium_armor` — the SOV
    `date > 1941.1.1` branch sat in an `OR` with the generic `date > 1940.1.1`, unreachable (blame
    `1848f569a40`), and `admits_medium_armor` inherited it, so medium opened on the calendar with
    the T-28 instead of on the T-34; (A) `_44_TEMPORARY_CONVERT` (base 15) and `30_MOT_LIGHT_MIX`
    (base 10) both enabled under 15006 + mission inactive, forever — a `replace_with` bridge is a
    one-shot with no memory, re-selected by priority every 7-day pass once the moved divisions no
    longer match it at 0.9, and the designer walks them back toward it; (B) STARTER / STARTER_MIX
    enabled on 15000 / 15001 only, so the brigades had no bridge under 15006; (D) the rung
    (15007/15008) is the same one-shot one level down: once the last LS template died its chain
    stopped firing, the rung stayed selected and pulled the FINAL's divisions back.
  - Shipped (commit on this subject, 2026-09-07):
    - `WA_AI_CONFIG.txt`: the SOV branch of the switch = T-34 or KV-1 or
      `WA_AI_CONFIG_after_global_war_begins` (the no-gap fallback, which is also the retire date
      — for the AI it only closes the role); the generic date branch excludes SOV;
      `admits_medium_armor`'s fallback excludes SOV, SOV admits on the T-34 accelerator or the
      global-war bound (KV-1 alone must not open a T-28 medium role).
      `WA_AI_PRODUCTION_army_composition.txt`: `build_army_medium_armor` no longer opens the
      medium budget slot on the switch for the park country (KV-1 before T-34 funded a slot
      with no template).
    - `WA_AI_TEMPLATES_effects.txt`, type-14 calculator: a five-phase machine for the temporary
      corps — MISSION 15006 (mission active) → PONT 15009 (CONVERT + MIX + STARTER_MIX enabled,
      `light_support_phase_pulses` = 2 monthly pulses, counter `WA_AI_TEMPLATES_ls_phase_pulses`,
      exit flag `ls_bridge_done`) → STABLE 15010 (MIX alone, until the window) → CONVERT-1
      15007/15008 medium or 15013/15014 heavy (rung + FINAL; class and MOT/MEC latched at entry
      in `ls_conversion_heavy` / `ls_conversion_mec`, sticky `ls_conversion_started`; exit = no
      template contains a support battalion any more, flag `ls_conversion_settled`) → CONVERT-2
      15011/15012/15015/15016 (FINAL alone, until the retire event clears everything). Migration:
      a save reloading on 15007/15008 sets bridge-done + started (+ mec) at its first pulse. The
      second monthly call of the calculator for the park country is removed
      (`WA_AI_TEMPLATES_calculate_all_templates`); the generic (pure/MIX) path is unchanged.
    - `WA_AI_TEMPLATES_triggers.txt`: the window opens on medium OR heavy.
      `wa_ai_production.txt`: `army_composition.light_support_phase_pulses = 2`.
    - `WA_AI_TEMPLATES_armored_light_support.txt`: STARTER_MIX enable + 15009; CONVERT enable =
      15009 only; MIX enable = 15001 / 15009 / 15010; rungs 15007/15008 retargeted 8/5/5 → 7/3/5
      with the MIX's RS 4+4 and 9 supports (D bis); two heavy rungs 15013/15014 (same target) →
      two heavy FINALs mirroring the heavy role's 7100 / 7105 shapes; MOT_FINAL + 15011,
      MEC_FINAL + 15012.
    - `WA_TEST_armor_budget.txt`: `flags` line re-typed (mission / pont / stable), new `lsphase`
      line (K, pulses, bridge-done, conv-started/settled/heavy/mec), conv-value knows 15011-15016.
    - `tools/check_templates.py`: the VALUE-NO-TEMPLATE join read `has_country_flag` only as a
      direct child of `enable`; every value that lived only inside an `OR` (all FINALs, the MIX's
      second and third values) was invisible to it. It now descends OR / AND (not NOT); fixture
      entry 1001 moved under an OR so the clean fixture proves it; `--selftest` OK.
  - t0/t1/t2 at the real cadences (monthly calculator, 7-day engine selection, monthly save;
    division moves are equipment-gated and take months — the phases bound the ARROW, and rely on
    the sole target keeping the divisions converging afterwards, see ASSUMED (i)):
    | t | flag | enabled | expected |
    | --- | --- | --- | --- |
    | t0 mission end (`a100b67c` 1938.11→12) | 15009 | STARTER_MIX, CONVERT, MIX | corps template tid 700 = 12/6/4 byte-identical to the CONVERT target (MEASURED) → match 1.0 ≥ 0.9, arrow on the MIX ≤ 7 days (the owner's screenshot of 2026-09-07 saw exactly this fire); brigades via STARTER_MIX (base 15, declared first, selected while "Tankovaya brigada" exists) |
    | t0 + 2 pulses | 15010 | MIX | arrow stays on the MIX; corps and brigade residuals keep moving (stock 12 977 LS + 5 669 L at 1938.11, MEASURED) |
    | t_T-34 (1940.7 here; STABLE lasted 19 months) | 15007/15008 | rung 7/3/5 + FINAL | park on 7/3/5 → match ~1.0 ≥ 0.8 → arrow on the FINAL ≤ 7 days; divisions move as medium chassis arrive (113 in stock 1940.6 → 1 475 at 1941.1, MEASURED: months) |
    | while any template contains a support battalion | same | same | the chain re-fires every pass against that template (MEASURED precedent: `6f52600d` 62 → 92, `a100b67c` 3 → 31 with the LS template alive) — no pull-back possible |
    | first pulse with no LS template | 15011/15012 | FINAL | arrow on the FINAL, nothing left to pull; sticky until the retire |
    | 1942.1.4 | absent | none | `sov_armor.981`: nothing to delete, role closed |
    Bound: the pull-back window is at most ONE monthly pulse between the last LS template dying
    and CONVERT-2 (on `a100b67c` the pull-back needed 2 months to show, 1941.03 → 1941.05).
  - Change 9 replaced (rule g). Its objection: "the rung target is a fixed literal; the fielded
    shape is emergent and changes per campaign, which is the coupling Change 8 was built to
    remove." Mine covers it because STABLE makes the fielded shape non-emergent: the MIX is the
    role's SOLE target from the end of PONT to the window (19 months on `a100b67c`), so the park
    converges on 7/3/5 and the rung target equals it by construction; when STABLE is short (T-34
    before the mission's end) the rung faces a 12/6/4 park and the symmetric pair scored 0.85 on
    the owner's 1943.1 read (12/6/4 target vs 6/3/6 park) ≥ 0.8.
  - ASSUMED, stated: (i) in STABLE and CONVERT-2 the divisions not yet moved keep converging on
    the sole target by ordinary field upgrade with no chain armed — DERIVED from `a100b67c`
    1939.12-1940.02 (the pool moved monthly while the CONVERT chain could not fire: no 12/6/4
    template existed after 1939.11) and 1941.05 (Med G → tid 2438 with the rung selected and its
    chain dead); if false, PONT residuals freeze on 12/6/4 until CONVERT-1, whose rung scores
    ~0.85 against them ≥ 0.8. (ii) The heavy FINALs mirror 7100/7105 so the heavy role captures
    them; the medium FINAL (9 M/6 mec) vs SOV's medium target 6111 (7 M/3 SPG/5 mec) residual —
    a T-34 + KV-1 SOV may still land its converted divisions on a heavy template — is unchanged
    and owner-accepted under Change 8. (iii) `WA_TEST_templates.txt:155` calls the calculator:
    one owner harness run = one extra PONT pulse.
  - Reviews 2026-09-07. Lessons **CONFLICT** (5 required): (1) "show the PONT bridge can fire" —
    answered by the t0 row (tid 700 = 12/6/4, match 1.0); (2) MOT/MEC latched at window entry —
    applied; (3) K bounds the arrow, not the divisions — CONVERT-1's exit is now the containing
    test (the rung is armed exactly as long as its source template exists), K applies to PONT
    alone and ASSUMED (i) carries the residuals; (4) migration for saves on 15007/15008 —
    applied; (5) rule (g) sentence — above. Architecture **CONCERNS**: (1) tag vs archetype in
    CONFIG — comment reworded, the tag is the intent (the tech ids are its own); (2) base-15 tie
    STARTER_MIX / CONVERT under 15009 — sentence added at the CONVERT block, the arrow lands on
    the MIX through either chain; (3) subject re-enters SHIPPED-UNTESTED — done; (4)
    `check_ai_layers` NUMBER-LEAK 348 > baseline 347 is pre-existing at HEAD (MEASURED: recount
    of the HEAD tree via `git show` = 348, the touched files count identically) — not bundled,
    owner to bump or fix on its own commit.
  - Checkers: `check_templates` 0 errors outside the 4 pre-existing HQ slot errors (`--selftest`
    OK); `check_constants` exit 0; `check_worklist` exit 0; `check_ai_layers` exit 1 on the
    pre-existing NUMBER-LEAK above. BOM-free, braces balanced on every touched file.
  - **Boot 2026-09-07 14:18 (owner log) FAILED on `943011b142`**: `parser.cpp: unexpected token
    near line 1410 (constant:...)` — the PONT exit was written `check_variable = { pulses >=
    constant:... }`, and the parser does not take `>=` there (zero `>=` existed in the repo; the
    `> constant:` form of the AIFC core parses). The trigger parser then desynced through the
    rest of the file (`Invalid trigger set_country_flag`, and an error 130 lines later in the
    retire effect). Fixed in the follow-up commit: K-1 computed into a temp and compared with
    `>`; the retire effect's `clear_variable` rewritten as `set_variable = 0` (harmless either
    way). No checker sees a parser error - only a boot does; lesson recorded.
- Verification — owner console, Change 11. (a) Post-mission, pre-T-34 SOV save (`a100b67c`
  1939.x): `event wa_abg.1 SOV` reads `pont-15009=1 bridge-done=0` for the first two pulses then
  `stable-15010=1 bridge-done=1 conv-started=0 light-role-open=0`; `imgui show ai_templates`:
  arrow on `30_MOT_LIGHT_MIX`, still there one month later. (b) Post-T-34 save (`a100b67c`
  1940.7+): `conv-started=1 conv-settled=0 containing-LS=1 conv-value=15007|15008`, `handoff`
  line `era-boundary=1 admits-medium=1`; arrow on `_44_TEMPORARY_TRANSITION_*` then on the FINAL
  within 7 days. NOTE: `a100b67c` saves from 1940.2 on reload with flag 15007/15008 → the
  migration path fires, expect `bridge-done=1 conv-started=1` on the first pulse. (c) Control on
  a 1937 save: `sov-mission-15006=1 pont-15009=0 stable-15010=0 bridge-done=0`.
- Verification — campaign probe, Change 11 (fresh campaign): no SOV division on an 8/3/4 or
  9/3/4 shape after the mission; ≥ 90 % of the park on 7/3/5 within 12 months of the mission;
  `WA_MEDIUM_ARMOR_TEMPLATE` first set the month after `sov_medium_tank_chassis_3` completes,
  never before; zero light-shaped templates created after the first FINAL division; the
  light-support flag never returns to a lower phase value.
- Parked 2026-09-04 by the agent, not by an owner decision, to admit the owner's `posture-v3`
  order under the WIP limit. State at that parking: SHIPPED-UNTESTED since 2026-09-02 (Change 7
  committed, WORK.md updated 2026-09-04 by another session), owner console run owed.
- **Change 10 — NOT SHIPPED. The proposed `upgrade_prio` retarget of the two SOV rungs is INERT;
  the arrow on the FINAL is the `replace_with` chain working, not a priority loss.** Owner brief
  2026-09-04: raise `upgrade_prio` of `..._44_TEMPORARY_TRANSITION_MOT` / `_MEC` above the FINALs'
  so the rung becomes the currently-targeted template. Verified first, per the brief's own
  instruction, and refuted. No file under `common/` was changed.
  - **MEASURED**, install `common/ai_templates/_documentation.md` (1.19.2.0), section *How do AI
    templates work?* and the `infantry_generic` parameter comments — two sentences settle it:
    target-level `upgrade_prio` "is used to determine (deterministically, no randomness involved)
    which of the target templates is the 'currently targeted template'"; and "If two target
    templates have the same `upgrade_prio`, the first one will be preferred (so order matters in
    those cases)". The field IS the arbiter — that half of the brief is right — but declaration
    order DOES break ties, so the brief's DERIVED ("l'ordre de déclaration ne décide pas du
    ciblage") is false and the FINAL's own `# Keep LAST in group` comment is correct.
  - **MEASURED**, `WA_AI_TEMPLATES_armored_light_support.txt`: under flag 15007 exactly two targets
    are enabled — the rung (line 321) and `TRANSITION_MOT_FINAL` (line 380); under 15008, the rung
    (347) and `TRANSITION_MEC_FINAL` (414). Both pairs tie at `base = 10` with the rung declared
    first, so **the rung already wins selection**. **DERIVED**: raising it to 15 changes nothing
    under either reading of the chain — selection recomputed each 7-day pass
    (`DAYS_BETWEEN_CHECK_BEST_TEMPLATE`, `05_defines.lua:1560`) or the switch persisted and prio
    re-evaluated: rung selected → chain fires → arrow on the FINAL, both times. The only field that
    would hold the arrow on the rung is `replace_at_match`, out of scope by owner instruction and
    destructive of the intended rung → FINAL progression.
  - **DERIVED**: the arrow sitting on the FINAL is therefore the chain having FIRED — the signature
    the lessons log already records for a correct chain (`replace_with` entry, 2026-08-29:
    "a correct chain moves the arrow to the replace_with target within one 7-day pass"). It matches
    Change 9's own Verification line, which expects the arrow on the FINAL within 7 days.
  - **The subject's open question is answered by the same reading.** Reaching the FINAL requires
    `match(best, FINAL) >= target_min_match 0.3`. Of the owner's two lines only `Best (all)` =
    0.94118 clears it (`Best (role)` = 0.14766 does not), so the engine's comparison used a value
    >= 0.3. **DERIVED**, corroborated by the log's `FINAL's best EXISTING match` entry, which is
    `Best (all)`-scoped. No second correctif is owed on the 0.3 bar.
  - **ASSUMED, the hole in the argument (architecture review):** two role-level entries share
    `role = light_armor` (`WA_light_armor_role`, `WA_light_support_armor_role`), which the install
    doc calls undefined. If the engine MERGES their target pools, "first declared" becomes file
    load order, `armored_light.txt` loads first, and a base-10 target of that file enabled at the
    same time would win — in that world the bump is not inert. Not claimed either way.
  - **ASSUMED, owed before any further work:** which value `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE` held
    at the owner's 1941.1.2 read. `TRANSITION_MOT_FINAL` enables on 15002 / 15004 / 15007, and the
    first two leave both rungs OFF. **DERIVED** from the calculator
    (`WA_AI_TEMPLATES_effects.txt:1400-1413`): with the SOV temporary latch only 15007/15008 are
    reachable, and MOT (not MEC) means no mechanized branch — so 15007 — but the console read is
    what settles it.
  - **Rivals for the 4-year freeze of the 37 divisions, NOT fixed here.** (1) The equipment gate:
    the doc gates field upgrade on "assuming they have enough manpower and equipment for it", the
    hop is 9 `medium_armor_battalion_line` x 37 divisions, and SOV holds **3** medium / wants 38.
    `UPGRADES_DEFICIT_LIMIT_DAYS` is **365** in WA (`05_defines.lua:1456`, vanilla 60) — the "(90)"
    in the Change 9 bullet and in the lessons log is the pre-`e75346fea` value and is stale — but
    the same lesson records that a live training queue keeps the estimate above ANY such limit.
    (2) Best-match capture: "makes a copy of the best matching template", and `Best (all)` is
    `Medium Tank template H` at 0.94118, so the role's work lands on an already-medium template.
    The lessons reviewer notes this predicts movement onto another class, not a freeze, so it
    ranks second. **Dropped as a rival**: "the role wants 0" — the log carries a MEASURED positive
    control that `role_ratio` want does not gate field upgrades.
  - Reviews 2026-09-04, both on the NOT-SHIP recommendation: architecture **CONCERNS** (editing
    rules 2 and 7 — an inert value edit is a zero-behaviour delta that reads as a decision; four
    bridge blocks carry `base = 15`, not three: lines 58, 86, **112**, 142, and all four precede
    every base-10 target, so none of them overtakes an earlier declaration either), lessons
    **CONCERNS** (no recorded case of a prio raise moving an arrow; vanilla's chain is prio-driven
    because `replace_at_match 1.5` is unreachable, WA's is switch-driven at 0.8). **No CONFLICT.**
  - Checkers (tree unchanged, run as the baseline this entry rests on): `check_constants`,
    `check_ai_layers`, `check_worklist`, `check_skill_refs` exit 0; `check_templates` exits 1 on
    the same 4 pre-existing HQ slot errors in `WA_AI_TEMPLATES_hq.txt`, nothing on the
    light-support file. Full working note: scratchpad `upgrade_prio_refutation.md`.
  - Second session, same day, same brief re-issued: re-read the install doc (lines 15-17, 58, 72,
    108-117) and the file (rung 321/347 first, FINAL 380/414 last, both `base = 10`, only that pair
    enabled per value) independently and reached the same NOT-SHIP. One precision on the 0.3 bar:
    the doc compares the best match TO THE RUNG (the park template, ~1.0 on 8/5/5) against the
    FINAL, before the switch; the two imgui `Best` lines are read AFTER the switch, against the
    FINAL, so neither is the value the engine compared. **DERIVED**: the arrow on the FINAL proves
    the 0.3 bar was cleared; which value cleared it stays ASSUMED and is moot. Reviewers not
    re-run — the recorded verdicts cover the identical decision. Checkers re-run on this tree:
    same results.
- Verification — Change 10 is a non-change; what would REOPEN it: (a) an owner `wa_abg.1 SOV`
  read showing `conv-value` = 15002 or 15004 (both rungs OFF — the diagnosis moves to the generic
  rung at line 246); (b) an `imgui show ai_templates` read where the arrow is on
  `_44_TEMPORARY_TRANSITION_*` with `Best (role)` below `replace_at_match` 0.8 (the park missing
  the bar, a different defect); (c) an in-engine observation that the two `role = light_armor`
  entries share one target pool, which would break the declaration-order argument above.
- **Change 7 (owner order 2026-09-02 "vas-y, corrige : rends la fenêtre de conversion joignable
  sous 15006") — the temporary-corps path reaches the medium conversion window.** Diagnosis
  (six boxes, scratchpad `light_to_medium_diagnosis.md`), campaign `5de66942` (BHU observer,
  1936.2-1945.12, build carrying `42206fcb6`): MEASURED `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE = 15006`
  on all 14 sampled SOV saves, `WA_AI_TEMPLATES_light_support_composition_latched` ABSENT on all,
  31-40 divisions on light-support shapes (tid 1487, 6 LS + 3 L + 6 mot) from 1941.1 to 1945.12,
  medium 0 in 1945.12 while SOV stocked 9 144 medium chassis (1945.1) and fielded 33 modern +
  15 heavy. Owner live read 1943.1.1: `imgui show ai_templates` arrow on
  `_44_TEMPORARY_CONVERT`, best match 0.85186 < replace_at 0.9, replace_with = `30_MOT_LIGHT_MIX`;
  `wa_abg.1 SOV`: `conv-window=0`, `sov-temporary-15006=1`, `light-role-open=0`, verdicts 1 1 1 1.
  Cause (script lines): the 15006 branch of `WA_AI_TEMPLATES_calculate_light_support_armor_template`
  ran before the 15000/15001 branch (sole writer of the composition latch) and before the conversion
  `else_if`, both of which require `_template_value = 0`; the window trigger required that latch;
  and under 15006 no enabled target pointed at a medium FINAL (CONVERT → MIX, MIX no replace_with).
  Rungs 15002-15005 were dead code for the historical park since `42206fcb6`.
  - `WA_AI_TEMPLATES_effects.txt`: the 15006 branch yields to
    `WA_AI_TEMPLATES_should_convert_light_support_to_medium_armor`; the conversion branch emits
    **15008** (temporary latch + mechanized) / **15007** (temporary latch) ahead of the MIX/pure
    values — exclusive by construction, the temporary path never writes the MIX latch.
  - `WA_AI_TEMPLATES_triggers.txt`: the window accepts EITHER latch; the park-fielded term is
    `has_template_ai_majority_unit` OR (temporary latch AND `has_template_containing_unit`) — the
    corps shape 6 LS / 3 L / 6 mot ties the majority vote (the tie ASSUMED in Change 4 is now a
    live risk, sidestepped); guard NOT (temporary latch AND `has_active_mission =
    SOV_the_greatest_tank_army`) — reviews turned the literal into ONE observation trigger,
    `WA_AI_PRODUCTION_historical_tank_park_mission_is_active` (`WA_AI_PRODUCTION_army_composition.txt`),
    now read by the window, the three corps enables and the two run-state gates.
  - `WA_AI_TEMPLATES_armored_light_support.txt` (shape SUPERSEDED by Change 9 below — the
    6/3/6 target and its majority-vote tie note describe campaign `5de66942` only): rungs
    `WA_AI_TEMPLATES_COUNTRY_SOV_LIGHT_SUPPORT_ARMOR_44_TEMPORARY_TRANSITION_MOT` (15007) / `_MEC`
    (15008), target = the shape the corps FIELDS, 6 LS / 3 L / 6 mot (tid 1487, 31 divisions in
    1945.12) — not the 12/6/4 it was built toward (lessons reviewer: a rung target that is not the
    fielded shape lets the designer drift divisions toward it while the switch waits, and 12/6/4
    shares 4 of 22 = 0.18 with the MOT FINAL, under the 0.3 bar). Arithmetic: fielded → rung
    match 1.0 ≥ 0.8; fielded → MOT FINAL 6 mot of 15 = 0.4 ≥ min_match 0.3; fielded → MEC FINAL
    shares no battalion by that count, but the identical hop (6/3/6 mot MIX → 9 M + 6 mec
    MEC_FINAL under 15005) is MEASURED live in campaign `6f52600d` (62 → 92 divisions), so the
    engine score is not the naive share — precedent, not arithmetic, carries the MEC case.
    replace_with = the existing same-group `TRANSITION_MOT_FINAL` / `_MEC_FINAL`, min_match 0.3;
    FINAL enables gain 15007/15008.
  - `WA_TEST_armor_budget.txt`: lsmix line gains `conv-value` / `majority-LS` / `containing-LS`.
  - Timeline (monthly calculator, 7-day engine re-selection): t0 = mission over + medium usable →
    next pulse emits 15007/15008, CONVERT/MIX/44_TEMPORARY disabled by flag-value equality, rung +
    FINAL enabled; t1 ≤ 7 days: rung targeted, 0.85 ≥ 0.8 → arrow to the FINAL (match(best,
    FINAL) ≥ 0.3 ASSUMED — same knob as the light chain that converted GER 1940.7 → 1944.1 in this
    campaign); t1-blocked row: if the deficit valve holds the switch for a pass, the rung target
    IS the fielded shape, so the designer has nothing to edit toward — match stays 1.0 / 0.4, no
    drift; t2 = park empties; the window lingers open while any template still contains a
    support battalion (harmless: only the FINAL is enabled) — ASSUMED that
    `has_template_containing_unit` still sees an emptied or decommissioned template; if it does
    not, the window closes a month early → 15006 → CONVERT/MIX enabled at match < 0.9 (inert),
    and if it reads true again the flag flaps 15006 ↔ 15007 monthly: each 15007 month re-arms the
    rung + FINAL for the divisions still on LS shapes, each 15006 month is today's status quo —
    a slower conversion, never a worse state. Closes on engine template deletion
    (ASSUMED timing) → 15006 re-emitted with CONVERT/MIX enabled and nothing to match. Residual:
    if emptied templates are never deleted, the flag holds 15007/15008 for good — the light chain
    carries the same residual (GER flag 5116 to 1945.12 with zero light divisions from 1944.1).
  - Positive controls from the same campaign (DERIVED): a role at want 0 still field-upgrades
    (GER budget_light 0 from 1940.7, 7 divisions on the transition shape by 1940.7, 0 light
    residue by 1944.1) and the medium role captures the FINAL shape (GER 6M+3MIS+6mec divisions
    became modern after the medium flag moved to 6611 — no light-role template carries modern).
  - Reviews 2026-09-02: architecture CONCERNS (campaign readings stripped from code comments;
    mission literal → named trigger; join-key line extended), lessons CONCERNS (rung target →
    fielded shape with the min_match arithmetic; containing-unit claim labelled ASSUMED with the
    flap row and the second console read) — all applied.
  - Checkers: `check_templates` (no VALUE/TEMPLATE mismatch; 4 pre-existing HQ slot errors
    untouched), `check_constants`, `check_ai_layers`, `check_worklist` exit 0.
- Verification — owner console, Change 7: `event wa_abg.1 SOV` on a post-mission save
  (1943.1 of `5de66942`): `conv-window=1`, `conv-value=15007` or `15008`, `containing-LS=1`, all
  four verdicts 1. Control: the same command on a pre-1942 SOV save reads `conv-window=0`,
  `conv-value=0`, `sov-temporary-15006=1`. Then `imgui show ai_templates`: arrow on
  `_44_TEMPORARY_TRANSITION_*`, best match ≥ 0.8, and within 7 days the arrow on the FINAL.
  Second read ONE MONTH after the first 15007/15008 reading (let the save run): `conv-value`
  still 15007/15008 — a fall-back to 15006 with `containing-LS=1` is the flap, the defect.
- Owner imgui read 2026-09-04 (save 1943.1 of `5de66942` reloaded on `cb5e1977f`): both
  `_44_TEMPORARY_TRANSITION_MOT/MEC` listed, arrow on `TRANSITION_MEC_FINAL` (flag 15008, the
  rung -> FINAL switch fired within the pass), `Best (all)` = `Best (role)` = "Heavy Tank template
  A" at 0.7353 — step 2 PASS. DERIVED: the engine builds the FINAL shape by copying that heavy
  template and moves the light-support divisions through the rung's field-upgrade path, as
  `6f52600d` measured for the MIX rungs. Steps 1 (`wa_abg.1` conv-value line) and 3 (one-month
  re-read, no fall-back to 15006) still owed; division movement needs a save 4-8 weeks later.
- Owner console 2026-09-04, same save run to 1943.3.24: `wa_abg.1 SOV` reads `conv-window=1
  conv-value=15008  majority-LS=1  containing-LS=1  sov-temporary-15006=0`, verdicts 1 1 1 1 —
  step 1 PASS (the majority tie did not bite). **New defect, owner-observed: the light-support
  divisions turn into HEAVY divisions.** Cause (MEASURED imgui + files): the FINAL's best existing
  match is "Heavy Tank template A" (0.7353) — heavy target 7105 is 9 heavy + 6 mec, RS 5+5 and the
  same support set as the 9 medium + 6 mec MEC_FINAL, while SOV's medium target 6111 is 7 medium +
  3 SPG + 5 mec, RS 3+3, other supports; the engine copies the best match as the field-upgrade
  destination (DERIVED from the install doc: "copy of the best matching template"). Same class of
  fault the light chain fixed with FINAL_MIS: a FINAL whose composition is not the medium role's
  CURRENT target is captured by whichever template is nearest, here the heavy one. Fix design owed
  to the owner (per-medium-value mirror of rung + FINAL, generated).
- **Change 9 (owner order 2026-09-04 "8/5/5 est le nouveau template stable pour les light support
  SOV, il doit etre utilise comme point de depart") — the rungs target the shape the park FIELDS
  in the current campaign.** Symptom, MEASURED (campaign `d1c51a6c`, BHU observer, build carrying
  `cb5e1977f`, 6 saves 1941.1-1945.8, plans.py as a module): the conversion window is ARMED —
  `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE` = 15007 at 1941.1 then 15008 from 1941.4, unchanged for 43
  months — and nothing moves. 37 divisions sit on ONE template, tid 1812 `Light Support Tank
  template F` = 8 light_support_armor / 5 light_armor / 5 infantry_heavy_motorized (18 line
  battalions), flat from 1941.10 to 1945.8 (296 support battalions). No deployment conveyor on any
  of the 6 saves carries tid 1812 or any light-support template: the park is never renewed. Its
  equipment drains — light-support chassis in armies 7 530 (1941.7) -> 858 (1945.8), free stock 0
  from 1943.1, i.e. 2.9 chassis per battalion.
  Cause (script line): the rung target was calibrated on the PREVIOUS campaign's fielded shape
  (`5de66942`, tid 1487 = 6/3/6 — the shape on which the owner's imgui read showed the rung ->
  FINAL switch fire). This campaign fields 8/5/5. The rung target is a fixed literal; the fielded
  shape is emergent and changes per campaign, which is the coupling Change 8 was built to remove.
  - `WA_AI_TEMPLATES_armored_light_support.txt`: both rungs
    `..._44_TEMPORARY_TRANSITION_MOT` (15007) and `_MEC` (15008) retargeted 6/3/6 -> **8/5/5**;
    `regimental_support`, `support`, `replace_at_match` 0.8, `replace_with` (same-group FINALs)
    and `target_min_match` 0.3 untouched; block header rewritten (it stated the old arithmetic).
  - Margin, DERIVED with the header's own convention (shared battalions over the FINAL's 15): the
    MOT hop falls from 6 of 15 = 0.40 to **5 of 15 = 0.33**, still >= target_min_match 0.3 but
    thinner. The MEC hop shares none by that count and rests on the MIX-rung precedent, unchanged.
  - ASSUMED, unresolved: the engine's own match value between tid 1812 and the rung. No save
    serialises it; only `imgui show ai_templates` does.
  - Residual the owner already accepted under Change 8: a country holding medium AND heavy may
    still see the converted divisions land on a heavy template (the 9+6 FINAL's best existing
    match). This change moves the FIRST hop only; it does not touch that second-hop defect.
  - Checkers: `check_constants`, `check_ai_layers`, `check_worklist`, `check_skill_refs` exit 0.
    `check_templates` exits 1 on the 4 pre-existing HQ slot errors in
    `WA_AI_TEMPLATES_hq.txt` (file untouched, already recorded under Change 7); no finding on the
    file changed here. BOM-free, braces balanced.
  - Trade, ASSUMED and stated because the change causes it: under the header's own naive
    convention a park frozen on the OLD 6/3/6 waypoint scores 14 of 18 = 0.78 against the new
    rung, under `replace_at_match` 0.8 — i.e. this retune buys the current campaign's shape and
    may cost the previous one's. The convention is known NOT to be the engine's formula (the MEC
    hop shares zero battalions and converts anyway), so the number bounds nothing; the owner's
    ruling that 8/5/5 is the stable shape is what settles which park is optimised for.
  - Two review points carried, not resolved: the park holds 3 support companies against the
    rung's 4 + 1 regimental, so "captures at 1.0" is ASSUMED, not arithmetic — only
    `imgui show ai_templates` `Best (role)` confirms it; and the hop now demands 13 armour
    battalions where the park fields 9, with free light-support stock at 0 since 1943.1, so
    `UPGRADES_DEFICIT_LIMIT_DAYS` (90) refusing the upgrade is an unmeasured rival explanation
    for any continued freeze.
  - Untouched by this change: the owner-observed heavy-capture defect (the FINAL's best existing
    match is a heavy template). This edit moves the FIRST hop only.
  - Reviews 2026-09-04: architecture CONCERNS + lessons CONCERNS, no CONFLICT. Header repaired
    (the 1.0 claim labelled ASSUMED, the 0.33 arithmetic dropped for the MIX precedent that
    covers both hops); the trade and the two open points are the bullets above. Committed on the
    owner's direct order BEFORE the reviewers returned —
    their verdicts are owed and, if either is CONFLICT, this change is amended or reverted.
- Verification — owner console, Change 9: on a SOV save of the current campaign with
  `conv-value` 15007/15008, `imgui show ai_templates` shows the arrow on
  `_44_TEMPORARY_TRANSITION_*` with best match at or near 1.0 (the rung target IS the fielded
  shape), then within 7 days the arrow on the FINAL. Campaign probe: a save 8-12 weeks later shows
  the light-support division count falling below 37 for the first time since 1941.10.
- **Change 8 — built, then PARKED by owner order 2026-09-04.** Per-medium-value generated
  rungs + FINALs for both chains (`tools/gen_ai_armor_conversion_finals.py`, ~9 000 generated
  lines, reviews applied) live on branch `parked/armor-conversion-finals` (`e26ab824f`), not on
  `ai-rework`. Owner ruling: a massive complexity increase, against the dynamic principles;
  decision owed to the owners. **Side effect ACCEPTED meanwhile**: a country holding medium AND
  heavy may see its converting light / light-support divisions land on a heavy template (the
  9+6 FINAL's best existing match). The Change 7 window stays as shipped.
- Verification — campaign probe, Change 7: a historical-difficulty SOV save ≥ 12 months after
  the mission resolution shows the light-support division count falling toward 0 and former park
  divisions on the 9 medium + 6 mot/mec shapes; `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE` reads
  15007/15008 while any template still carries a support battalion, never 15006 with
  `containing-LS=1` after the mission.
- Was parked 2026-08-31 (WIP limit, `dday-mulberry` entered on an owner task); unparked
  2026-09-02 on the owner order above, slot freed by parking `bof-commonwealth-posture`. State at the
  2026-08-31 parking:
  SHIPPED-UNTESTED — chosen for parking as the most-verified of the armor cluster: its exit-rung
  repair shares the mechanism the `armor-class-handoff` conversion chain PASSED live 2026-08-29.
  Still owed when unparked: the console runs in the Verification lines (wa_abg.1
  lsmix/conv-window, the two imgui reads).
- SHIPPED-UNTESTED (pre-parking): Changes 3-4 touch `WA_AI_TEMPLATES_effects.txt` (harnessed system); the owner
  console runs owed are listed in the Verification lines (wa_abg.1 lsmix/conv-window, the two
  imgui reads).
- Exit rungs repaired 2026-08-29 by the `armor-class-handoff` session, after its live stall
  measurement (owner imgui: match 0.8125 ≥ replace_at 0.8, switch never fires when replace_with
  points OUTSIDE its role group): the four transition rungs (15002-15005) pointed cross-group at
  `GENERIC_MEDIUM_ARMOR_30_MOT/30_MEC`. Retargeted onto two new same-group FINAL templates
  (`..._TRANSITION_MOT_FINAL`/`_MEC_FINAL`, pure-medium compositions, enabled while the flag
  holds any conversion value); exit = medium-role best-match capture, same ASSUMED and probe as
  the light chain, which PASSED live on the Apr-1941 GER save the same day.
- Scope: owner request 2026-08-29 ("vas-y, implémente") — deployed SOV 1936 tank brigades must be
  field-upgradeable to the light-support target template, so the fielded light-support count can
  reach the `[armor-role-budget]` 10k run cap instead of stalling at the army's composition
  ceiling; then (owner rulings, same day) the mission stays as written and historical difficulty
  fulfils all three bars; then the park converts to medium at end-of-run instead of
  decommissioning.
- Symptom (MEASURED, `SOV_1940_03_01_16.hoi4`, campaign 8a14581e): 8 400
  `light_tank_support_chassis` in armies vs 10 782 in stockpile; 23 divisions still on the
  8-battalion "Tankovaya brigada", 6 on the 9+6 target shape. DERIVED: full-strength ceiling of
  the current army is ~9 500 — the 10k cap is unreachable without conversion. Mission
  `SOV_the_greatest_tank_army` active, 670 days left, fails all three bars.
- Cause (MEASURED, install `common/ai_templates/_documentation.md`, target-template section):
  field upgrade only moves a division to a target's `replace_with`; the role's single target had
  `can_upgrade_in_field` but no `replace_with` and nothing matched the brigade shape — no
  destination, so no conversion, ever.
- Change (`common/ai_templates/WA_AI_TEMPLATES_armored_light_support.txt`): new target
  `WA_AI_TEMPLATES_GENERIC_LIGHT_SUPPORT_ARMOR_20_STARTER` mirroring the OOB brigade (8x
  light_support + 1x mot inf), `enable` = flag 15000 + `has_template = "Tankovaya brigada"`,
  prio 15 vs 10, `replace_at_match 0.9` / `replace_with` = 30_MOT / `target_min_match 0.3`.
  Vanilla ENG starter pattern (doc); EAI 5.0 uses enable-gated replace chains on 1.19.2.
- t0/t1/t2 walk (lessons-reviewer requirement; engine evaluation cadence unobservable, ASSUMED
  sub-monthly): t0 = flag 15000 present + brigades exist → starter enabled AND best-match 1.0 —
  gate and match are the SAME template object, so the target flips to 30_MOT the same evaluation
  and brigades convert as manpower/equipment allow (stock: +25 support chassis and 6 mot btns per
  division, 10.8k chassis available). t1 = brigades all converted, template empty: if it lingers,
  flip keeps firing (still the 1.0 match), field upgrade finds no matching division — no-op; if
  the engine deletes it, `enable` goes false the same state — file degrades to today's single
  30_MOT target. t2 residual: divisions sitting on engine-made RENAMED 8+1 copies when the
  original dies are stranded unconverted = exactly today's behaviour, never worse. ASSUMED
  (engine): deployed divisions do not migrate to copies except via field upgrade, so the stranded
  set is plausibly empty.
- Residual (architecture reviewer, ASSUMED): while the brigade exists, prio 15 could steer other
  light-support divisions toward the 8+1 STARTER shape as a detour — campaign probe watches for
  non-brigade divisions on that shape.
- Change 2 (owner ruling 2026-08-29: the mission stays as written; historical difficulty fulfils
  it, competitive will not; lever = build_army): conversion alone cannot cross 10k — wanted for
  the light role is 32 vs current 59 (the 30 OOB cavalry divisions classify into the role,
  DERIVED 29+30=59 from the 1940.3 save), so the AI builds ZERO new light-role divisions and the
  ceiling stays ~9 500. Added: `WA_AI_CONFIG_pursues_historical_tank_park` (CONFIG, original_tag
  SOV), decision trigger `WA_AI_PRODUCTION_should_build_historical_tank_park`
  (`WA_AI_PRODUCTION_army_composition.txt`) = historical difficulty + CONFIG + run open + NOT
  fielded-cap, and gate block `WA_AI_PRODUCTION_DEFAULT_historical_tank_park`
  (`WA_AI_PRODUCTION_DEFAULT_army_composition.txt`, OVERRIDE section): `build_army id =
  light_armor value = 500` + `force_build_armies value = 300` — magnitudes mirror the
  army_expansion_override block above it, the one pair with campaign precedent.
- Change 2 timeline at the real cadences (lessons-reviewer requirement; the race it prices: the
  1942.1.1 run close does not merely miss the bar, it INVERTS it — want → 0 retires the park):
  - t0 = 1940.3 (MEASURED state): 29 armor divisions, 8 400 fielded support chassis, 10 782 in
    stock, 12-factory line running. Equipment is NOT the binding constraint: conversions
    (~+1 700 to fill 23 brigades to 225) plus ~16 new divisions (3 600) draw ~5 300 < stock.
  - t1 (DERIVED, training-bound): 23 in-field conversions fill from stock as reinforcement flows;
    ~16 new 30_MOT divisions train under the force — at ASSUMED armor training ~4–6 months and
    parallel slots, deployment completes mid-to-late 1941. Fielded crosses 10 000 → cap trigger
    closes force and production line off the same measurement = mission bar 1 satisfied.
  - t2 = 1942.1.1: run closes, want → 0, park decommissions. Margin under the ASSUMED rates is
    ~3–6 months; if a campaign shows deployment slipping into 1942, the fix is a longer run for
    the mission country, not a bigger force value. ASSUMED and flagged in the block comment:
    build_army 500 / force_build_armies 300 actually push building past wanted<current — only
    id=infantry has campaign precedent; the owner `imgui show ai_division_production` read
    (light_armor Being Built > 0 with Current 59 > Wanted) is the killing measurement.
- Change 2 known limit: covers mission bars 1 (10k support) and 3 (>29 armor divisions) only.
  Bar 2 (5 000 plain light_tank_chassis in armies) was structurally unreachable — no SOV template
  outside the 30 OOB cavalry divisions (75 lights each) and the 15-per-division recon companies
  carries plain lights; ceiling ~2 900. Change 3 below is the owner-approved answer.
- Change 3 (owner approval 2026-08-29 "vas-y, fais le template mixte"): MIXED composition for the
  historical mission country — one target per role is an engine constraint (install ai_templates
  doc), so fielding both chassis means one template consuming both.
  - `WA_AI_TEMPLATES_triggers.txt`: new `WA_AI_TEMPLATES_use_mixed_light_support_armor` =
    run open + historical difficulty + `WA_AI_CONFIG_pursues_historical_tank_park`.
  - `WA_AI_TEMPLATES_armored_light_support.txt`: the role now holds an enable-exclusive pair of
    finals — pure 30_MOT (9 support + 6 mot, NOT mixed) vs 30_MOT_LIGHT_MIX (6 support + 3
    light_armor + 6 mot, mixed) — and a starter per final (`replace_with` is a static token, so
    each destination needs its own bridge; identical composition and prio 15).
  - Math (DERIVED, 25/battalion, recon 15): mixed division = 150 supports + 90 lights. At ~39
    mixed + the 6 existing pure divisions: supports ≈ 10 750 (incl. 3 550 in infantry), lights ≈
    5 850 with cavalry — both equipment bars cross. Cap interplay: at 150/div the 10k cap needs
    ~43 divisions instead of ~45 — same force lever, same shutdown.
  - Latch (lessons-reviewer requirement 1, was a CONFLICT): the composition is decided ONCE, at
    first arming, in `WA_AI_TEMPLATES_calculate_light_support_armor_template` — flag value 15000
    = pure, 15001 = mixed, latch flags `WA_AI_TEMPLATES_light_support_composition_latched` /
    `_light_support_mixed`. No template enable reads the live mixed trigger, so a mid-campaign
    difficulty change can never re-run the decommission pass on the fielded park (the
    flag-transition lesson). Exclusivity is now by flag-value equality, stronger than the NOT
    pairs the first review saw.
  - RS slack (lessons-reviewer requirement 2): MIX carries 4+4 regimental supports, not the pure
    template's 5+5 — 10 RS on 15 battalions of three types has zero grid-stacking slack
    (designer-deadlock rule). The pure template's inherited 5+5 tightness is pre-existing and
    untouched.
  - Production/fielded timeline (lessons-reviewer requirement 3 — the bars count FIELDED, the
    division math counts SLOTS; they converge only if equipment flows): t0 = latch (new campaign:
    when the run arms; the 1940.3 save: next monthly pulse). Lights needed in armor divisions ≈
    3 600 (39 × 90 + recon); stock already holds ~3 129 and cavalry carries its 2 250
    independently — the light bar is mostly STOCK-funded, the 2-factory line only covers the
    ~500 gap plus attrition. Supports needed ≈ +2 350 net over the measured 8 400; stock holds
    10 782 — also stock-funded. t1 = conversions + ~16 forced builds deploy (training-bound,
    ASSUMED 4–6 month training → mid/late 1941). t2 = 1942.1.1 run close. If a campaign shows
    either chassis starving instead, the named lever is an
    `equipment_production_min_factories_archetype` floor (need-blind, additive — use with a cap),
    not a bigger force value.
  - Residual, accepted: the 6 existing pure divisions cannot chain to MIX (their final is
    disabled under value 15001) and stay 9+6 — the math counts them as pure.
- Change 3 verification: `WA_TEST_armor_budget` gained the `lsmix` line (latched vs live trigger
  vs fielded plain lights) — owner run required, the subject enters SHIPPED-UNTESTED at commit
  because Change 3 touches a `WA_AI_*` scripted effect of a harnessed system. Campaign probe:
  under historical difficulty SOV light-role divisions mount BOTH battalion types;
  `num_equipment_in_armies@light_tank_chassis` > 5 000 before 1942; flag value is exactly one of
  15000/15001 and never flips after first arming.
- Change 4 (owner order 2026-08-29 "quand l'IA bascule aux medium/heavy, les divisions changent
  de template"): the plain-light half shipped in the CONCURRENT session (`06c485bfa` conversion
  window + rungs 5121/5122, `bf2568ae8` un-swap + retarget), whose window EXCLUDES the
  light-support country by design (`NOT light_support_armor_owns_light_role`). This change is its
  light-support twin, end-of-life for the park:
  - `WA_AI_TEMPLATES_triggers.txt`: `WA_AI_TEMPLATES_should_convert_light_support_to_medium_armor`
    = latch flag (memory the country ran the park) + run over + medium class live +
    `has_template_ai_majority_unit = light_support_armor_battalion_line` (retires the window with
    the park; syntax MEASURED vanilla `ai_strategy/SOV.txt:407`) + NOT expansion override.
  - Calculator code-14: else_if branch emits transition values — 15002 pure→MOT, 15003 pure→MEC,
    15004 MIX→MOT, 15005 MIX→MEC (MOT/MEC mirrors the medium calculator's mechanized branch;
    destination names verified post-un-swap: 30_MOT=6100, 30_MEC=6101).
  - Role file: 4 TRANSITION rungs, each targeting the park's own shape (fielded divisions match
    ~1.0 ≥ replace_at 0.8) with replace_with = the medium entry final, min_match 0.3.
  - Same ASSUMED as the light window, in writing: the engine still field-upgrades a role whose
    role_ratio want is 0 — if false, the park freezes instead of decommissioning (still better
    than decommission only if freeze is; the owner console run decides). Second ASSUMED: MIX has
    no strict majority unit (6/6/3) — if `has_template_ai_majority_unit` resolves ties away from
    light_support, the MIX park's window never opens and it decommissions as today (bounded to
    status quo, visible in the harness conv-window bit).
  - Join-key diff (lessons requirement, run by hand): calculator emissions for code 14 are
    exactly {0-clear, 15000, 15001, 15002, 15003, 15004, 15005} (Change 7 adds 15006,
    15007, 15008 — enables: TEMPORARY / _CONVERT / 30_MOT_LIGHT_MIX on 15006, the two TEMPORARY
    rungs + FINALs on 15007/15008); declared enables are 15000
    (STARTER + pure final), 15001 (STARTER_MIX + MIX final), 15002-15005 (the 4 rungs). No
    emission without a declared entry; the conversion branch sets its base value as a direct
    effect first, so no path leaves the trigger open with no value.
  - Lost-race bound (assumption a), in writing: if decommission beats conversion at the run-end
    flip, the outcome sits between today's status quo (all decommissioned) and full conversion —
    a partially converted park, never a broken state; the equipment of decommissioned divisions
    returns to stockpile as today.
  - Window close: conversion empties the park template; it lingers at 0 divisions until the
    engine deletes it (ASSUMED timing). While it lingers the window stays open harmlessly — the
    lingering template IS the 1.0 best-match, so the role target flips to the medium final every
    evaluation and field upgrade finds no matching division (same gate-and-match-same-object
    argument as the STARTER). Engine deletion → majority term false → window closes → flag
    cleared.
  - Non-retroactive: a campaign already past its run end (or predating the latch flag) has no
    park left to convert and keeps its decommission — new-campaign feature.
  - Telemetry, resolved by review: `WA_TLM_armor_roles_open` is defined as "flags the selector
    actually wrote" (registry row v34) and the committed light window already keeps its flag set
    while converting — so the flag holding 15002+ during conversion is the DEFINED semantics, not
    drift. A value guard was briefly added then reverted to keep the two windows consistent.
  - Verification: `wa_abg.1` lsmix line now prints `conv-window`; campaign probe — a SOV save
    post-1942.1 shows former park divisions on medium templates, not decommissioned; the flag
    holds 15002-15005 only while the majority term is true. Owner console run decides assumption
    (a) — the decommission-vs-conversion race has a measured lost precedent, so SHIPPED-UNTESTED
    until observed.
- Change 5 (owner order 2026-08-29 "ajoute un nettoyage de ces divisions passives"): AI-only
  cavalry cleanup in the mission itself (`common/decisions/SOV_factions.txt`, complete_effect +
  timeout_effect): `delete_unit_template_and_units` on "Kavaleriyskaya Diviziya" with
  `disband = yes` (refunds equipment+manpower — MEASURED effects_documentation.md:3493), gated
  `is_ai` + `has_template`. Order matters and is free: the effect fires AFTER the availability
  bars passed, so the cavalry's 2 250 fielded lights still count at the test. A human SOV keeps
  its cavalry. Known cost, owner-accepted: on timeout (~1942.1) 30 divisions leave the fronts
  mid-war; their equipment returns to stock. Probe: post-resolution SOV save has zero divisions
  on the cavalry template (AI) and `politics` shows the mission resolved.
- **Campaign `6f52600d` verdict (2026-08-29, BHU observer, 118 monthly saves 1936.2-1945.11,
  historical difficulty, `wa_tlm_version = 34`, first campaign carrying Changes 1-5): the CHAIN
  works, the MISSION timed out.** MEASURED: mission still `active` with `days=0` at 1942.1.1,
  `re_enable_cooldown` at 1942.2, and no +100 armour-mastery step in the doctrine ledger (positive
  control: ENG +53 the same month) — TIMEOUT, not complete. Bars: fielded support chassis peaked
  **9 078** (1941.8) vs 10 000; plain lights **4 911** (1941.6) vs 5 000; armor divisions 63 > 29
  met. Conversion PASSED: brigada 21 → 0 by 1941.9 while the MIX park rose 15 → 62 (flag 15001,
  latch stamped once 1938.4.1, never rewritten); the pure shape never fielded. Post-run conversion
  PASSED: flag 15005 by 1942.3, medium+heavy park 6 → 92 divisions (1942.6 → 1945.10) on the
  MEC_FINAL 9+6 shape; budget handoff agrees (light 0 / medium 17 at 1942.3). Industry followed
  then over-corrected: support line 0 → 58 factories (1940.9) → 38 (1942.1), terminated by 1942.9;
  the medium ramp lagged 18 months (30 factories 1941.6-1942.9, 84 at 1943.6, heavy took the freed
  capacity first). Cavalry cleanup (Change 5) was a NO-OP: the template left the save between
  1941.6 and 1941.7 (pre-timeout attrition/decommission), so the `has_template` guard was false —
  goal met by another path, not a defect. DERIVED causes of the miss: (1) at 150 supports/division
  the 10k bar needs ~68 filled divisions and the army peaked at 62 — equipment was NOT binding
  (stock 10 184 at 1941.6); (2) the division surge started only with the 1940 budget rung and the
  light share was diluted to 8 in 1941 when medium/heavy opened mid-run (MEASURED
  `wa_ai_armor_budget`: 10 → 8 → 0); (3) the Change 3 math counted ~3 550 supports in infantry —
  the carrying template (`Strelkovaya Diviziya`) was replaced by 1941.3 and that contribution
  evaporated. Residues watched, NOT admitted (owner decision owed): 9 divisions stranded on
  degraded light-support shapes at 1945.10 (strength 50-60 vs 400-600 for the mediums, conversion
  tail 3.5 years); a 24-division "Light Cavalry template A" burst 1942.2-1942.6 in the re-target
  window.
- Change 6 (owner order 2026-08-29 "dans l'idéal, l'ia doit réussir la mission avant barbarossa —
  implémente"): two calibration levers, from the arithmetic above, neither touching the mission
  bars (owner ruling: the mission stays as written) nor the force values (62 fielded vs want ~8
  proves the force already pushes past want).
  - MIX composition 6/3/6 → **7/3/5** (175 supports + 90 lights per division): the 10k bar crosses
    at ~59 filled divisions — the count this campaign reached by mid-1941 — instead of ~68. The
    two TRANSITION_MIX rungs (15004/15005) follow to 7/3/5 so their `replace_at_match 0.8` keeps
    matching the park at ~1.0; a mid-campaign 6/3/6 division matches the new target at 14/15 ≈
    0.93, so parked saves walk up by ordinary field upgrade. Cap interplay: at 175/div the fielded
    cap closes at ~57 divisions — same shutdown lever, comment on the constant updated. RS
    unchanged (4+4 on 15 battalions).
  - Armor-budget light floor, section 2b of `WA_AI_ARMOR_BUDGET_reconcile`: while the run is open
    the light slot floors at `constant:wa_ai_production.army_composition.tank_park_light_floor`
    (= 15, the 1940 rung) and infantry pays the difference — kills both the early-rung brake
    (5/10 pre-1940) and the 1941 dilution. Gate = new DECISION trigger
    `WA_AI_PRODUCTION_should_floor_tank_park_budget` = the build-force gate MINUS the fielded-cap
    term, deliberately: the cap must stop BUILDING, but dropping the WANT at the cap re-arms the
    decommission race on the fielded park (the want→0 inversion this subject already prices). No
    cap term = no flap; engage at role-open + release at run-close = 2 extra transitions per
    campaign, inside the reconcile's entry bound. The file header's "never a second budget lever"
    sentence now names this one gated exception. `WA_TEST_armor_budget` re-types the floor
    (contract rule 4, new `park-floor-add` field in the expect log) so V2/V3 stay honest on the
    park country.
  - ASSUMED, named: that the pre-1940 surge brake IS the budget rung — the coincidence (rung
    10→15 and the factory ramp 8→58 both landing in 1940) is DERIVED, not pinned. If the next
    campaign still shows the surge waiting for 1940 with the floor active from 1936, the brake is
    elsewhere (training slots / deployment cadence) and the next lever is not a bigger share.
  - Reviews 2026-08-29 (lessons CONCERNS + architecture CONCERNS), repairs applied:
    (1) `tank_park_light_floor = 15` reworded as an INDEPENDENT value calibrated to the park —
    the equality with `armor_budget_1940` is coincidence, not derivation, stated on the constant
    (the alternative, a registry mirror, would force the floor to follow every ramp retune);
    (2) the harness now re-types the GATE from its four terms instead of calling the shipped
    trigger, so a gate defect surfaces as a C/D mismatch; (3) early-success walk added below;
    (4) RS-grid reachability discharged empirically below.
  - Early-success walk (lessons req. — no gate term reads mission resolution; monthly reconcile
    cadence): t0 mission completes early (say 1941.4) → complete_effect fires, cavalry cleanup
    runs, floor still armed; t1..run-close (≤ 9 pulses) → light want holds 15, which maps to a
    division want BELOW the ~57-division fielded park (measured this campaign: want ~8-10 ≈
    unbuilt while fielded 62), and the build force + production line are already stopped by their
    own cap term — so the overshoot builds ZERO extra divisions; the floor only prevents the
    want-collapse decommission race, which is its purpose. t2 = 1942.1.1 window close → floor
    releases in the same pulse the light role closes; one retirement set, as in the timeout case.
    Bound: the early-success branch emits no additional entries at all.
  - RS-grid reachability, discharged empirically (lessons req.): campaign `6f52600d` MEASURED the
    engine field-upgrading 92 divisions onto the 9+6 MEC_FINAL shape (15 battalions, 5+5 = 10
    regimental supports) and 62 onto the three-type 6/3/6 MIX (8 RS) from 8+1 brigades — both
    strictly harder cases than one greedy mot→support edit from 6/3/6 to 7/3/5 under the same
    8 RS (fewer RS than the 9+6 precedent, same battalion count, match 14/15 ≈ 0.93). Any grid
    rule that forbade 7/3/5+4+4 would have forbidden what the campaign measured working.
  - Checkers after repairs: `check_constants` / `check_ai_layers` / `check_templates` /
    `check_worklist` all exit 0.
- Verification — owner live check: `tag SOV` then `imgui show ai_templates` (install doc,
  Tips section) on the 1940.3 save — the light_armor role must show the STARTER→30_MOT chain with
  "Tankovaya brigada" as best match. The build_army-forces-past-want assumption is SETTLED by
  campaign `6f52600d` (62 fielded against want ~8): no console read owed on it any more.
- Verification — owner console, Change 6: `event wa_abg.1 SOV` on any pre-1942 SOV save reads
  `park-floor-add` > 0 in the expect line, `light=15`, and all four verdicts at 1. Control: the
  same command on a non-park country reads `park-floor-add=0` with verdicts unchanged.
- Verification — campaign probe (updated for Change 6): divisions on the 8+1 shape falling toward
  0, the MIX park on the 7/3/5 shape, `num_equipment_in_armies@light_tank_support_chassis`
  crossing 10 000 and the MISSION resolving as COMPLETE (gone from `active_timed_decision` with
  the +100 armour-mastery step in the doctrine ledger) BEFORE Barbarossa; zero NEW divisions
  built on the STARTER shape.
- Closed when: a historical-difficulty campaign shows SOV completing `SOV_the_greatest_tank_army`
  before 1941.6, with former brigades fielded on the 7/3/5 MIX shape. Change 7 adds: the same campaign,
  ≥ 12 months after the mission resolves, fields 0 divisions on light-support shapes and the
  former park on medium shapes. (Supersedes the pre-Change-3
  criterion "≥ 1 former brigade on the 9+6 shape AND fielded support > 9 500", which the pure
  shape can never satisfy under historical difficulty — the MIX is what arms there.)
- Out of scope note SUPERSEDED by campaign `6f52600d`: bar 3 (30 armor divisions) was MET (63) and
  bar 2 (5 000 plain lights) peaked 98% under the MIX design — both reachable; mission-side
  alignment is no longer needed.

### armor-budget-ramp — PARKED (2026-08-29)
- PARKED state: code SHIPPED 2026-08-29, owner console run STILL OWED (Verification lines below
  unchanged and still the exit). Parked, not closed, only to keep the OPEN WIP limit at 4 when
  `light-support-conversion` opened; nothing about the fix or its evidence changed. Un-park it by
  restoring the `SHIPPED-UNTESTED (2026-08-29)` heading.
- Scope: owner order 2026-08-29 — the armour share of the wanted-division mix must grow with the
  era instead of jumping to its terminal size the month a country unlocks its first chassis.
  Successor to the CLOSED `armor-role-budget`, which fixed how the budget is SHARED between tank
  roles; this one fixes its SIZE over time.
- Symptom (MEASURED, owner `imgui show ai_division_production`, GER 1939): 84 wanted divisions,
  `light_armor` current 12 / wanted 21, infantry 57 / 55, mountaineers 7 / 8 — infantry `Being
  Built` 0. Owner report: GER never reaches its ~1.5M-men target for the Poland campaign.
- Cause (MEASURED, script): `constant:wa_ai_production.army_composition.armor_budget_total = 25`
  was a single flat number consumed by `WA_AI_ARMOR_BUDGET_reconcile`
  (`common/scripted_effects/WA_AI_PRODUCTION_armor_budget.txt`), so the 1942-sized armour share
  applied from the first month a tank role opened.
- Change: the budget becomes a calendar ladder — `armor_budget_start = 5` (start..1938.12.31),
  `_1939 = 10`, `_1940 = 15`, `_1941 = 20`, `_total = 25` from 1942 (terminal). Ladder in the
  reconcile; the console harness `WA_TEST_armor_budget.txt` re-types it (contract rule 4) and the
  four boundary dates are registry-mirrored (`armor_budget_ramp_boundary_*`) so the two copies
  cannot drift.
- Which of the two states this moves: the role SHARE, not the wanted-division TOTAL. role_ratio
  only redistributes the 84; the total is set by the `WANTED_UNITS_WEIGHT_*` defines and belongs
  to `division-target-scaling`. DERIVED for GER 1939 (one open tank role): 8 armour / 8 mountain /
  67 infantry instead of 21 / 8 / 55.
- The ramp does NOT move manpower, MEASURED 2026-08-29 (sum of `manpower` in `common/units/` over
  each `target_template`): a WA armour division is the same 15 line battalions as an infantry one —
  infantry 1004 = 18 200 men, light armour 5100 = 18 900, mountaineers 2002 = 20 700. Weighted
  average per division 18 625 before the ramp and 18 520 after: 0.6%. Its payoff is EQUIPMENT cost,
  not head-count. Any claim that this subject fixes the owner's 1.5M-men target is false — that is
  `division-target-scaling`'s formula, and `WANTED_UNITS_MANPOWER_DIVISOR = 17250`
  (`05_defines.lua:1358`) is the engine's own statement of the same division size.
- Keyed on the DATE and not on armour tech, because the tech unlock is the event that produced the
  jump. TIME-ONLY BY DESIGN: a country at war in 1937 stays at rung 5 with no war-state override.
- Zero-share floor (DERIVED, every open-role combination at rung 5): 5 / 3+2 / 4+1 / 2+2+1 — no
  slot floors to 0, so the engine's decommission-on-zero-share path is never armed.
- Entry accumulation (DERIVED, monthly cadence, three roles open): Dec-1938 pulse 0 entries,
  Jan-1939 pulse 4, Feb-1939 pulse 0. Four rungs per campaign take the documented bound from ~50
  to under 100 entries per country, against AIFC's ~250/year. Monthly interpolation was rejected
  for this reason and the rejection is written into the effect header.
- Mid-campaign load (ASSUMED — no lesson covers a role want dropping below current): a pre-1939
  save resumed on this build sees the armour want fall 25 → 5 on the first reconcile. Nothing
  recorded says the engine decommissions fielded divisions of a role whose want merely shrinks.
  Probe: owner `imgui show ai_division_production` on a resumed pre-1939 save one pulse after
  load — every armour row still present with a non-zero want.
- Closed when: a harness run (`event wa_abg.1 <TAG>`) on TWO different rungs pasted here shows all
  four verdicts at 1 with `budget=` reading the rung for that year; and a 1939 GER window shows
  wanted `light_armor` near 10% of the wanted total with infantry `Being Built` above 0.

### armor-ladder-integrity — PARKED (2026-09-01)
- Parked 2026-09-01 (WIP limit, `armor-prod-war-floor` enters on an owner task). State at
  parking: SHIPPED-UNTESTED, waiting only on the owner console runs in its verification line;
  no code work pending.
- SHIPPED-UNTESTED as of the flattening ship below: it rewrites seven calculators inside an
  effect an on_action calls, which is exactly the size of change the owner console-test rule
  covers. Owed: `event wa_test_tmpl.1 <TAG>` and `event wa_test_tmpl.2 <TAG>` output pasted here.
  Everything ABOVE that ship was structural and script-verified, and nothing there is owed.
- Scope: owner request 2026-08-29, after the duplicate template names surfaced during
  `modern-chassis-tier`. Intended behaviour: the armour template ladder always selects a template
  that mounts everything the country can actually build, and every template it can select exists
  and is reachable. Found by auditing the ladders mechanically rather than by reading them.
- Defect class, MEASURED: two `ai_template` entries under ONE key inside a role group means only
  one is reachable, and the flag value written for the other selects nothing — the country silently
  keeps its previous template. Four such pairs existed. Nothing in the game logs it.
- Fixed (`903bb73ad`): medium 6108/6109/6110 shared their names with 6105/6106/6107; the
  distinguishing `MEDIUM_ASSAULT` term was missing (their ladder branches carry
  `WA_AI_TEMPLATES_use_medium_assault_armor` and their regimental slot mounts
  `medium_assault_gun_company_regimental`). Light 5105 shared its name with 5107.
- Fixed (`903bb73ad`): medium 6107 and 6110 carried `medium_infantry_support_armor_battalion_line`
  inside their `support` block — a line battalion in a divisional support slot, where all four
  siblings carry `medium_infantry_support_company_divisional`.
- Fixed (`004c2aa4f`): light 5105 and 5107 also shared their ladder CONDITION, so 5107 won the
  else_if chain and 5105 was dead twice over. Traced: `d7e227e49` created 5107 as a duplicate of
  5108; `811e731b5` retargeted it onto 5105's condition. 5105 is now the SPAA-less twin of 5107 —
  the shape the medium ladder already uses with 6105/6106/6107 — with its regimental pair repaired.
  The identification is MEASURED, not inferred: across the armour role the regimental pair is
  invariably ONE artillery-type company (pack artillery, else assault gun, else SPG, by unlock)
  plus ONE anti-tank-type company (anti-tank, else tank destroyer), and 5105 was the only template
  of 74 that broke it — zero artillery, two anti-tank. That is what marks it as the botched copy.
- Fixed (`004c2aa4f`): heavy 7003 deleted, defined but selected by no branch. The 20-width branch
  of every armour class has exactly two variants (mechanized, motorized) and no component
  sub-branches, so it had no home. Inert content that reads as an available variant is a trap.
- Fixed (this ship) — `[light-td-coverage]`: the three TD-bearing light variants all required
  light SPAA, so a country holding light tank destroyers but no SPAA fell to 5101/5102 and fielded
  neither its TD battalion nor its TD company. Added 5117 (TD), 5118 (TD + SPAA), 5119 (SPG + TD),
  5120 (assault + TD), each placed BELOW the variant it is the reduced form of, so no existing
  capability set changes hands. 5119 sits below 5105 on purpose: a country with TDs, SPG and
  infantry-support tanks keeps 5105's infantry support instead of trading it for the SPG battalion.
- Fixed (this ship): restoring 5105's `heavy_anti_air_mot_company_divisional`. Removing its light
  SPAA company left it the only light template with NO air-defence company at all — a defect this
  session introduced and the AA audit caught. Every light template carries exactly one AA company:
  `heavy_anti_air_mot` without light SPAA, `light_self_propelled_anti_air` with it.
- Simulation, MEASURED (light role, all 24 reachable capability sets — SPG and assault are mutually
  exclusive by `WA_AI_TEMPLATES_use_light_assault_armor`, so the space is 2 x 3 x 2 x 2): sets where
  the selected template drops something the country can build went **16 -> 12**, and sets where a
  TD-capable country fields NO tank destroyer went **4 -> 0**.
- KNOWN REMAINING, not fixed, needs an owner decision: 12 of 24 light sets still lose an artillery
  tier (pack artillery instead of SPG or assault gun), an SPAA company, or trade infantry support
  for the SPG battalion. Closing them all is not more branches — the ladder is a 3 x 2 x 2 x 2 cross
  product and hand-writing it is exactly how the four duplicate pairs above got in. The real fix is
  to GENERATE the light 30-width ladder and its templates the way
  `tools/gen/gen_ai_medium_modern_mirror.py` generates the modern-chassis mirror. That is a rewrite of a
  file the collaborator also edits, and it renumbers live values, so it is not started.
- Tooling (this ship, owner request 2026-08-29): the audits below were run by hand and would have
  rotted the moment nobody re-ran them. `python tools/check_templates.py` now holds them
  mechanically — it parses the eleven calculators, rebuilds every if/else_if chain (both the
  sibling and the nested spelling), computes the values each role can actually reach including the
  +100 hospital and +500 chassis mirrors, and cross-checks that set against `common/ai_templates/`
  both ways. Eight rules: VALUE-NO-TEMPLATE, TEMPLATE-NO-VALUE, DUP-CONDITION, UNREACHABLE-BRANCH,
  DUP-TEMPLATE-NAME, SLOT-SUFFIX-MISMATCH, NO-DIRECT-EFFECT, ELSE-SEPARATED. `--selftest` mutates a
  fixture once per rule and fails if any rule does not fire on the input built to break it.
- Non-regression, MEASURED: run against `903bb73ad~1` (a git worktree at the commit before the
  hand fixes) it reports 4 DUP-TEMPLATE-NAME, 4 SLOT-SUFFIX-MISMATCH and 1 DUP-CONDITION — the
  same defects this subject found by reading. The rules are not inert.
- Flattened (this ship): the seven calculators with branches — infantry, mountaineer, marines,
  light, medium, heavy, suppression — are now flat first-match-wins sequences. Each branch is an
  independent `if` that tests `check_variable = { _template_claimed = 0 }` and sets it to 1 when
  it takes the role, so file order IS priority and no branch nests inside another. Zero `else` and
  zero `_weird_debug` remain in the seven. The `_template_claimed` guard is enforced by
  `check_templates.py` (CLAIM-GUARD-MISSING): a branch added later without both halves is an
  ERROR, not a silent overwrite of a higher-priority branch.
- Why it had to be flattened, MEASURED: the nested form was AMBIGUOUS and no syntactic rule
  recovers the intent. An `else` that sits inside one `if` and follows another means "not the
  OUTER if" in infantry/marines/light/medium/heavy, and "not the INNER if" in mountaineer. Read
  one way the five ladders were broken; read the other way mountaineer was broken — handing
  2002/2003 to a country that wants no mountain divisions at all, the decommission trap the
  garrison header describes. The flat form is correct under both readings.
- Equivalence, MEASURED: a boolean sweep of every calculator over every assignment of the
  triggers it reads (35 316 cells; `equiv.py`, an interpreter run against both file versions).
  Against the outer-if reading: heavy/light/medium/marines/suppression/motorized/mechanized/
  light_support all IDENTICAL, infantry differs in exactly one cell (the 1002 fix below), and
  mountaineer differs in the six cells that were the bug.
- Fixed (this ship) — `[templates-motorised-20w]`: infantry 1002 was declared and written by no
  calculator. It is the motorised twin of the 20-width 1001, the shape 1005/1006 already have at
  30 width, so a rich army in marsh or mountain terrain fielded the horse-drawn line and its
  motorised regimental companies went unused. Now selected on `marsh_or_mountain` +
  `can_motorize_support`. 1001 takes no hospital mirror — no 1101 exists.
- NOT resolved, and the flattening does not answer it: the owner ruling that a scripted-effect
  `if` block needs an effect of its own, which is what the six `_weird_debug` sentinels were
  supplying. The flat form gives every block two real effects, so the question no longer applies
  to these seven — but `check_templates.py` keeps the NO-DIRECT-EFFECT rule for whatever is
  written next.
- Harness (this ship): `common/scripted_effects/WA_TEST_templates.txt` +
  `events/wa_test_templates.txt`, contract v1. Its measurement is that
  `has_country_flag = WA_<TYPE>_TEMPLATE` with no `value` term is true exactly when the role holds
  a non-zero value, so a `used=1 set=0` pair on any role names the silent failure directly.
  `wa_test_tmpl.2` runs a real pass and prints pre/post, which a missing claim guard would split.
- Verification: `python tools/check_templates.py` — **0 ERROR, 0 WARN** (was 0/17 before the
  flattening: 16 NO-DIRECT-EFFECT, 3 ELSE-SEPARATED and the dead 1002 are all gone).
  `--selftest` exit 0 with nine rules, each firing on the input built to break it.
  `python tools/check_constants.py`, `python tools/check_worklist.py` both clean.
- Verification OWED to the owner, in an observer game: `event wa_test_tmpl.1 <TAG>` on a major
  reads no `used=1 set=0` pair on any role; on a country with heavy_inf + marsh_or_mountain +
  can_motorize it reads `value=1002`; `event wa_test_tmpl.2 <TAG>` prints pre and post that match
  line for line. Control: `wa_test_tmpl.1` on a 1936 minor before its infantry focus reads
  `admit : ... 0` and every `set=` legitimately 0.
- Campaign-probe attempt 2026-09-04 (`5d2a391c`, build commits `903bb73ad`/`004c2aa4f`/
  `ac7a3e78b`/`1785e5a91` confirmed live): FAILED to find a qualifying case — MEASURED JAP/ITA/GER
  all researched a light tank-destroyer tech by 1944.6-1944.12 (`jap_light_td_tank_3`,
  `ita_light_td_tank_1/2/4`, `ger_light_td_tank_1/2/4`) but field ZERO light-armour templates at
  that point (all switched to medium doctrine); one `light_tank_destroyer` battalion appears
  embedded in a medium-chassis template (JAP) and a cavalry template (GER), never a dedicated
  light-armour one. POL/HUN/ROM/SOV had not researched light TD tech in either save checked.
  DERIVED: likely a doctrine-timing gap — `WA_AI_CONFIG_switch_from_light_to_medium_armor`
  (`date > 1940.1.1`) typically moves majors off light armour before they research light TDs on
  this campaign's timeline — NOT confirmed as a residual defect in the 5117-5120 fix itself.
  Closed-when criterion NOT met on this campaign; needs either a minor that keeps light doctrine
  into its light-TD-tech window, or the owner's own `wa_test_tmpl` harness run.
- Closed when: a campaign shows a light-armour AI that researched light tank destroyers fielding a
  template that contains them (the 4 -> 0 result above, confirmed in a save rather than in a
  simulation).

### mech-window — PARKED (2026-09-04)
- Re-parked 2026-09-04 by the agent (WIP limit — 6 subjects would otherwise sit above `## PARKED`
  with the 2026-09-04 scoring pass): its Closed-when criterion is now MET (evidence below), state
  is CAMPAIGN-OK, but closure into the `## CLOSED` table is an owner decision in every precedent
  in this file — move it there directly in one line if that call should be made now.
- Parked 2026-09-01 (WIP limit, `armor-class-handoff` re-enters on an owner task — the May-1941
  two-medium-templates report). State at parking: SHIPPED-UNTESTED, waiting only on the owner
  console run in its verification line; no code work pending.
- Scope: owner request 2026-08-29 after a tester report. Intended behaviour: a country that reaches
  mechanization through the INDUSTRIAL branch does not flip its armour templates from motorised to
  mechanized until its army has stopped expanding. Germany specifically: not before 1.6M men
  deployed AND not before 1940.1.1 - i.e. after the Polish campaign, not before it. Owner chose
  option B (policy in one CONFIG trigger) containing option A (the date).
- Symptom (REPORTED, tester playthrough): GER converted its light-tank divisions from trucks to
  mechanized before the war with Poland; massive mechanized_equipment deficit; the AI moved its
  production lines onto it.
- Symptom CONFIRMED (MEASURED, monthly saves of the local campaign): GER carries
  `WA_LIGHT_ARMOR_TEMPLATE = 5100` (MOT) at the 1938.9 pulse and `5102` (MEC) at the 1938.10 pulse
  — eleven months before the Polish campaign. `WA_MECHANIZED_TEMPLATE = 4000` appears the same
  month. Still 5102 at 1938.11, 1938.12, 1939.3, 1939.6.
- Cause (MEASURED, script): `WA_AI_TEMPLATES_use_mechanized_templates` opened on
  `num_of_military_factories > 100` with NO date or state term. GER starts 1936 with 104
  `arms_factory` (summed over `owner = GER` states), so that branch is true on day one and the only
  remaining verrou is `ger_mechanized_infantry_1`, whose generated `ai_will_do` opens 1938.1.1
  (`common/technologies/armor_ger.txt:111`). GER reaches the tech early because
  `WA_AI_RESEARCH_needs_mechanized` admits it on `focus_on_medium_armor`, not on the factory branch
  — and the research trigger's OWN factory branch is dated `date > 1941.1.1`
  (`WA_AI_RESEARCH_tanks.txt:73`) while the template trigger's was not. That asymmetry is the bug.
- Which path carries the bill — CORRECTION to the first reading of this subject. I first attributed
  the deficit to the conversion of the FIELDED force. MEASURED (`savegame.py tlm GER 1939.4`:
  `wa_tlm_comp_armor = 4`, `wa_tlm_comp_mech = 0`, `wa_tlm_comp_div_total = 90`): GER had FOUR
  armour divisions and no mech divisions, so that path bills ~4 x 6 x 50 = 1200 pieces (DERIVED at
  50 `mechanized_equipment` per `infantry_heavy_mechanized_battalion_line`,
  `common/units/land_mot_mech.txt:409`) — real but not "massive". The production side is the larger
  lever and is UNMEASURED: at the same flip, `WA_AI_PRODUCTION_build_mechanized` turns on an
  `equipment_variant_production_factor id = mechanized_equipment value = 60` and
  `mech_min_factories_*` sets a hard floor of 3/8/15 factories. Which of the two the tester saw is
  ASSUMED; the fix moves BOTH, in opposite directions, deliberately.
- Fix (SHIPPED 2026-08-29), three parts:
  1. `WA_AI_CONFIG_DIVISIONS_mechanization_window_open` (CONFIG) = `date > 1941.1.1` OR
     (`original_tag = GER` AND `has_army_manpower = { size > 1600000 }` AND `date > 1940.1.1`).
     Owner set the 1940 term 2026-08-29 after the crossing measurement below: 1.6M alone landed
     ~1939.3, still six months BEFORE the Polish campaign. The two GER terms bind in different
     games - on the historical path the DATE binds (GER is already at ~124 divisions in 1940.1),
     in a slow-growth game the MANPOWER bar binds.
  2. The trigger is SPLIT. `WA_AI_TEMPLATES_mechanization_line_open` is the old body verbatim, no
     timing term — "does this country mechanize at all". `WA_AI_TEMPLATES_use_mechanized_templates`
     is now `mechanization_line_open` AND (identity OR the one-way flag
     `WA_AI_TEMPLATES_mechanization_earned`) — "may its templates carry mech NOW".
  3. Weight late, floor early. The three `mech_min_factories_*` FLOORS read the ungated line form,
     so a few factories build a buffer during the window; the three `build_mechanized*` production
     WEIGHTS keep the windowed form, because switching a weight on early IS the reported symptom.
- Latch: `WA_AI_TEMPLATES_update_mechanization_latch`, monthly pulse and on_startup, placed FIRST of
  the four template latches — `update_modern_chassis_latch` reads `use_mechanized_templates`, which
  reads this flag, so setting it after would arm the chassis latch a month late.
- Why a latch: the GER branch is NOT monotone (deployed manpower falls in war) and every change of
  the enabled ai_template re-runs the engine's decommission pass (`lessons-log.md:256`).
- t0/t1/t2 at the real cadences (division counts MEASURED; manpower DERIVED at 18 200 men per
  template-1004 division; stock DERIVED):

  | t | date | trigger state | mech stock | who pays |
  | --- | --- | --- | --- | --- |
  | t0 | ~1938.10, tech lands | `line_open` 1, window 0, latch 0 | 0, floor 3 opens | ~3 of ~110 mil factories (2.7%) |
  | t0b | ~1939.3, 90 div ~1.64M | manpower term met, DATE term not - window still 0 | buffer growing | unchanged |
  | t1 | 1940.1.1, 124 div | window 1, latch 1, same tick `calculate_templates` writes the MEC value | ~15 months x 3+ factories | fielded bill; weight 60 turns on |
  | t2 | t1 + months | floor rises to 8 above 149 factories | rising | normal line |

  Division counts MEASURED: 60 (1938.6), 74 (1938.12), 86 (1939.2), 90 (1939.4), 104 (1939.8),
  109 (1939.10), 119 (1939.12), 124 (1940.1), 146 (1940.6). The 1.6M crossing is bracketed at
  ~1939.3 (86 div ~1.57M, 90 div ~1.64M), so on this campaign the 1940 date is the binding term and
  the buffer window is ~15 months rather than ~5. The residual deficit at t1 is REDUCED, NOT
  eliminated, and is not claimed to be bounded.
- Timing outcome (DERIVED from the counts above): the flip moves from 1938.10 - eleven months
  before the Polish campaign - to 1940.1, four months after it and five months before the fall of
  France (1940.6.23 on the reference campaign). That is the behaviour the tester report asked for.
- Blast radius (MEASURED, grep of both trigger names):
  - windowed form: the 47 armour-ladder call sites in `WA_AI_TEMPLATES_effects.txt`,
    `use_mechanized_division_templates`, `update_modern_chassis_latch`, the three
    `WA_AI_PRODUCTION_build_mechanized*` weights, and the harness.
  - ungated line form: the three `WA_AI_PRODUCTION_mech_min_factories_*` floors and
    `WA_AI_TEMPLATES_use_motorized_templates`. That last one is the reader the first pass MISSED
    (caught by wa-architecture-reviewer): it reads `NOT = { use_mechanized_templates }`, so gating
    the industrial branch would have OPENED the motorised-substitute branch — and with it a
    `role_ratio` for motorised divisions — for any 101-150-factory country with no armour
    templates and no `mobile_warfare_drive_tech`, for the whole window. Pointing it at the line
    form keeps it byte-identical to before.
  - NOT affected: `use_mechanized_td_armor` / `_spg_armor` / `_spaa_armor` do not read either.
  - `update_modern_chassis_latch` is delayed with the window. Inert in practice: modern armour
    unlocks well after 1941 (DERIVED, not measured on a save).
- Identity branch NOT gated (USA/ENG/CAN/AST/SAF via `WA_AI_CONFIG_DIVISIONS_use_mechanized_divisions`):
  owner scope — the request was to gate the industrial path, and this list is the
  [mech-divisions-usa-only] identity. NOT because they are immune: CAN/AST/SAF have no factory floor
  in that branch and take the same conversion bill on the smallest industry in the set. Noted at the
  call site in `WA_AI_CONFIG.txt`, unmeasured, not fixed.
- Principle 1 residual, recorded not fixed: `date > 1941.1.1` is the only path for every country but
  GER, so an ahistorical 1938 industrialiser waits on the calendar and a 1941 late industrialiser
  flips mid-expansion. Deliberate tuning fallback; the GER branch shows the state-based form if it
  ever needs closing.
- `has_army_manpower` verified in the 1.19.2 install (`documentation/triggers_documentation.md`,
  section `has_army_manpower`, COUNTRY scope); syntax `= { size > N }` already used at
  `common/decisions/GER.txt:2840`. The 1.6M bar is held equal between CONFIG and the harness by
  `tools/constants_registry.json` group `ger_mechanization_manpower_bar` (proved live: mutating the
  harness copy to 1500000 raises DRIFT). NOT unified with the neighbouring `size > 1599999` in
  `common/decisions/GER.txt` — same idea, different decision, owner call.
- Checkers: `check_constants.py` 0 ERROR (75 groups), `check_worklist.py` 0 ERROR,
  `check_skill_refs.py` 0 dead references, `check_templates.py` 0 ERROR / 0 WARN (deterministic
  over three consecutive runs on the final tree).
- Working-tree caveat, MEASURED, NOT this subject's work: `WA_AI_TEMPLATES_effects.txt` in the
  working tree carries an uncommitted flattening of the calculators (`_template_claimed`, 161
  occurrences) that is absent from HEAD and from every `git stash` entry — the
  `armor-ladder-integrity` refactor, alongside the untracked `tools/check_templates.py`. I ran
  `git stash` / `git stash pop` over it to measure a baseline; the apply was clean (no conflict
  markers, braces balanced, checkers deterministic) but it flipped the file LF, which I normalised
  back to CRLF. `check_templates.py` read 17 / 28 / 0 WARN at three points of that session and I
  cannot reconcile those numbers — do not treat any of them as a verdict. Do NOT `git stash` in
  this tree again while that work is uncommitted.
- Verification (console harness, OWNER-RUN, section B3 of `WA_TEST_armor_budget.txt`): fire
  `event wa_abg.1 GER` from another tag, read `mline` / `mwin` / `mfloor` in `logs/game.log`.
  During 1939 the discriminating read is `over-1.6M-men=1  after-1940.1=0  window-open=0  latch=0`
  with `line-open=1`, `mech-factory-floor=3`, `mechanized=0` on the `tier` line and `mech-in-armies`
  rising — that single line proves the manpower term passed and the DATE term is what is holding
  the flip. From 1940.1: `after-1940.1=1 window-open=1 latch=1 mechanized=1 mech-production-line=1`
  with `mech-in-armies` NON-ZERO at the flip — zero stock there means the floor never ran and the
  decoupling is inert. Counter-check on the same run: `event wa_abg.1 USA` shows
  `identity-branch=1` and `mechanized=1` regardless of the window.
- Campaign probe PASSED 2026-09-04 (`5d2a391c`, build commit `e8c83af87` confirmed live): MEASURED
  GER `WA_LIGHT_ARMOR_TEMPLATE=5100` at 1939.9-1939.10 (no `mechanization_earned` flag,
  `mechanized_equipment` stock 749→828, non-zero); flag fires 1940.2.1.1, template flips to
  5215/5213 the same month with the mechanized line funded 8/8-8/9 factories and no collapse of
  infantry (31/32→37/37) or motorized (28/34→20/20) lines. Counter-check (GER on 5102 from
  1938.10 pre-fix) already established in the Symptom CONFIRMED bullet above. Console harness
  (section B3, `event wa_abg.1 GER`) was not separately run by the owner this pass — this closure
  rests on the campaign-probe criterion alone, which the Closed-when line below does not gate on
  the harness.
- Closed when: a campaign save taken during the Polish campaign (1939.9-1939.10) shows GER
  carrying a MOT light-armour value (5100 family, not 5101/5102/5103/5105), no
  `WA_AI_TEMPLATES_mechanization_earned` flag, and a NON-ZERO `mechanized_equipment` stock; and a
  save from 1940.2 or later shows the flip done with no production-line collapse onto mechanized at
  the crossing. Counter-check: the pre-fix reference campaign has GER on 5102 from 1938.10.
  **MET 2026-09-04 (evidence above).**

### mot-field-hospital — PARKED (2026-09-04)
- Re-parked 2026-09-04 by the agent (WIP limit — see `mech-window`'s identical note above/below):
  its Closed-when criterion is now MET (evidence below), state is CAMPAIGN-OK, but closure into
  the `## CLOSED` table is an owner decision in every precedent in this file.
- Parked 2026-08-29 (WIP limit, `armor-budget-ramp` enters). State at parking: code SHIPPED
  2026-08-29, unverified. Parked rather than one of the three SHIPPED-UNTESTED subjects because
  its verification owes the owner NOTHING to run now: it has no console harness (33 lines, below
  the threshold) and its only exit is a campaign probe on a save taken after GER crosses 300
  military factories — a waiting state, the same logic that parked `theorist-hiring` and
  `templates-admission`. Unpark when that campaign is scored.
- Scope: owner request 2026-08-29 — "je veux que l'Allemagne utilise les hôpitaux motorisés dans
  ses divisions". Intended behaviour: a rich army that is otherwise entirely horse-drawn still
  fields the MOTORISED field hospital, which is the one support company whose horse variant caps
  the whole division's speed.
- Symptom (MEASURED, `1943.1_Jan.hoi4`): GER runs `WA_INFANTRY_TEMPLATE = 1004` and
  `WA_MOUNTAINEERS_TEMPLATE = 2002` — both 100%-horse targets — with 439 owned arms factories.
  Cause (MEASURED, script): the horse/mot choice has exactly one gate,
  `WA_AI_CONFIG_DIVISIONS_can_motorize_support` (`WA_AI_CONFIG.txt:574`), whose two ways in are a
  tag list (USA/ENG/FRA/SOV + dominions) and a latch that needs `is_in_faction_with USA/ENG`.
  Germany can satisfy neither, ever, at any industrial level.
- Why the hospital and not the whole support line (MEASURED, `common/units/support_field_hospital.txt`):
  the horse company carries `maximum_speed = 0.6`, which caps the division; the mot company has no
  speed line, +0.04 casualty_trickleback and −0.06 experience_loss_factor. It pays 25
  motorized_equipment and the WA motorised-support combat nerfs (`max_strength −0.5`, `defense`
  and `breakthrough −0.5`, `soft/hard_attack −0.9`) — a deliberate trade the owner asked for.
- Fix (SHIPPED 2026-08-29): a THIRD motorisation tier between HRS and MOT, named `HMH` in the
  template legend. Six mirror targets, each identical to its source but for the hospital company:
  1003→1103, 1004→1104 (infantry), 2000→2100, 2002→2102 (mountaineers), 10000→10100,
  10002→10102 (marines). The calculator reaches them with `+100`
  (`WA_AI_TEMPLATES_apply_motorized_hospital_mirror`), called on the six horse leaves only — the
  same offset idiom as `[modern-chassis-tier]`'s `+500`. Gate:
  `WA_AI_TEMPLATES_can_motorize_field_hospital` = one-way flag set by
  `WA_AI_TEMPLATES_update_motorized_hospital_latch` at `num_of_military_factories > 300` AND
  `has_tech = motorised_infantry`. Owner decision 2026-08-29: 300 military factories, not 400,
  and not total factories.
- Why a latch and not a live threshold: the value picks WHICH ai_template is enabled, and every
  change of the enabled target re-runs the engine's template decommission pass — the rule the
  three latches above this one already encode. The tech term is not decoration:
  `motorised_infantry` is what unlocks `motorized_equipment` (`common/technologies/armor.txt:174`),
  so without it the mirror target is unfillable.
- Blast radius (MEASURED, grep): nothing outside `common/ai_templates/` reads
  `WA_INFANTRY_TEMPLATE` / `WA_MOUNTAINEERS_TEMPLATE` / `WA_MARINES_TEMPLATE` values — the six new
  values reach the six new blocks and nothing else. The reserve template
  (`WA_reserves_effects.txt:127`) is deliberately NOT mirrored (owner choice: emergency divisions
  stay cheap), and the scripted division creator keeps its own `can_motorize_support` splice, so
  its equipment calculator needs no new motorized_equipment term.
- Who else this reaches (MEASURED, savegames): ITA 111 and JAP 159 owned arms factories at
  1940.6 — neither crosses 300 in that campaign, so the tier is Germany-only in practice. USA /
  ENG / FRA / SOV are already fully motorised by tag and never see the mirror branch.
- Campaign probe PASSED 2026-09-04 (`5d2a391c`, build commit `67a9c2192` confirmed live): MEASURED
  at 1941.11 (GER owned arms_factory 308) `WA_INFANTRY_TEMPLATE=1104`, `WA_MOUNTAINEERS_TEMPLATE=
  2102`, flag `WA_AI_TEMPLATES_motorized_hospital_earned=1`, GER's active infantry template
  carries `field_hospital_mot_company_divisional`; holds unchanged through 1943.1/1944.6/1945.8.
  Counter-check clean: ITA and JAP stay on 1004/2002 (horse) through 1944.6, JAP flips only at
  1945.8 once its own factory count crosses independently. Caveat: the flag's set-date
  (1940.6.1.1) predates this owned-factory bracket (308 @ 1941.11), so the gate likely reads
  CONTROLLED not OWNED `num_of_military_factories` — doesn't affect the PASS, just means the true
  crossing date is earlier than stated here.
- Closed when: a campaign save taken after GER crosses 300 military factories shows
  `WA_INFANTRY_TEMPLATE = 1104` (or 1103) and `WA_MOUNTAINEERS_TEMPLATE = 2102` (or 2100), the
  flag `WA_AI_TEMPLATES_motorized_hospital_earned` set, and GER infantry divisions carrying
  `field_hospital_mot_company_divisional`. Expected crossing on the current reference campaign:
  ~1941.8 (MEASURED: 300 owned arms factories at 1941.7, 303 at 1941.9).
  Counter-check on the same save: ITA and JAP still on 1003/1004/2000/2002.
  **MET 2026-09-04 (evidence above).**
- No console harness: the templates calculator has none, and this change is 33 lines of scripted
  effect with no signature or scope change, below the harness-writing threshold. Verification is
  the campaign probe above.

### modern-chassis-tier — PARKED (2026-09-04)
- Parked 2026-09-04 by the agent, not by an owner decision, to admit the owner's two 2026-09-04
  orders (`usa-pacific-hoard`, `eng-reserve-partner`) under the WIP limit — move it back to OPEN
  in one line if that is the wrong pick. State at parking: SHIPPED-UNTESTED (code committed
  2026-09-04, `a7ee778db` and its two predecessors), owner console run owed; nothing else changes.
- **ADDENDUM 2026-09-04 (owner ruling, reverses the 2026-08-28 "every component one tier up"):
  the hull steps up, the variants stay on what the country stocks; modern variants are researched
  only while their chromium draw is absorbable.** Unparked for this (the WIP slot freed by
  `aifc-revived-tag-residue` parking). MEASURED, campaigns `5de66942` and `5d2a391c` (monthly saves,
  Armour Ledger + `armor_extract.py`): the month GER's medium template takes the +500 twin
  (6611 → 6616, 1944.10) the component need moves to modern TD / SPAA / SPG (1 769 / 396 / 1 278)
  and NOTHING is ever fielded — 0 in armies for twelve months with 55-91 factories on the modern
  TD line, then 0 factories in the next run — while the medium variants' stock sits idle (medium
  SPG 3 057 → 3 578, medium SPAA 437 → 451, need 0-36). Cause on the production side, MEASURED
  `1945.1_Jan.hoi4` GER lines: every modern line short of chromium (`tank_ger_modern_chassis_td_1`
  chromium 0/69, SPG 0/64 + tungsten 66/126, hull 0/102). MEASURED `x_tank_chassis.txt`: every
  country's modern TD / SPAA / SPG chassis carries chromium 2-4 (GER 2, USA/SOV/JAP/POL 3, HUN 3,
  ITA 2); the GER medium variants carry chromium 2 as well — the difference is the STOCK, not the
  recipe.
- Change: (A) `tools/gen/gen_ai_medium_modern_mirror.py` — `TIER_UP` maps the hull only
  (`medium_armor_battalion_line` → modern, engineer / maintenance tank companies follow); every
  TD / SPAA / SPG / assault / infantry-support component maps to itself, `NAME_SHIFT` emptied,
  header rewritten; `WA_AI_TEMPLATES_armored_medium_modern.txt` regenerated. (B) the nine
  `WA_AI_TEMPLATES_use_<tier>_<component>_armor_tiered` triggers are their plain component
  trigger (names kept — 30 ladder readers, and the seam where a future re-tiering lands).
  (C) `WA_AI_RESEARCH_needs_modern_{tank_destroyers, assault, infantry_support,
  self_propelled_guns, self_propelled_aa}` gain `WA_AI_EQUIPMENT_can_absorb_chromium_shock_small`
  — the existing constructibility latch (two consecutive months of net chromium > 5 outside
  overextension, held 180 days, `WA_AI_EQUIPMENT_update_context_flags`, monthly for every AI).
  MEASURED it discriminates: GER carries `chr_small_ok` / `chr_large_ok` at 1943.7 and no `chr_*`
  flag at 1945.1; SOV carries `chr_small_ok` at 1945.1. `needs_modern_armor` (the hull) is NOT
  gated — owner scope is the variants. Importer branch, stated: `resource@chromium` is the
  retained domestic surplus, so a pure chromium importer sits near 0 and never opens
  `chr_small_ok` — it never researches a modern variant, and under (A) loses nothing by it.
- **ADDENDUM 2026-09-04 b (owner: "les templates convertis que si le matériel a commencé la
  production (donc stock)"; a line CUT on shortage was proposed, objected to by the owner —
  "je ne veux pas couper les lignes de prod en cas de pénurie" — and reverted before commit).**
  (E) COMPONENT SEED, templates: the 19 `WA_AI_TEMPLATES_use_<class>_<component>_armor` triggers
  gain `OR { num_equipment@A > 0 ; num_equipment_in_armies@A > 0 ; chromium headroom latch ;
  NOT major chromium shortage }` — a component is mounted once it EXISTS or is AFFORDABLE. The
  seed is needed because the engine derives its need from the template: a stock-only rule never
  starts (no need → no line → no stock). Two reachable seeds by design: the headroom latch
  (`resource@chromium > 5` two months running, 180-day hold) is a PRODUCER reading — an importer
  sits at net ~0 by trade and never opens it — so an importer seeds on `NOT
  WA_AI_RESOURCE_is_major_shortage_chromium` (new OBSERVATION trigger over the existing counter,
  `WA_AI_RESOURCE_NEEDS_triggers.txt`; 3 = the counter ceiling, three bad ~2-day readings in a
  row). Existence bar `constant:wa_ai_production.army_composition.variant_component_seed_stock` =
  100 (owner 2026-09-04: not 0, so captured stock or a trickle line cannot hold the mount once the
  seed is gone). Production gates read the same component triggers, so an unmountable component is never
  pushed either. No line is cut anywhere: a shortage stops NEW components from being mounted and
  (addendum a) new modern variants from being researched; running lines keep running.
- Seed window, DERIVED (monthly calculate vs ~2-day counter vs line-to-first-unit): t0 monthly
  calculate mounts the component (seed true, stock 0) — `_template_value` moves one rung (e.g.
  6114 → 6116 for medium TD, `WA_AI_TEMPLATES_effects.txt:957-983`), which is the same event
  class as any tech-unlock rung change the ladder already makes, ASSUMED same decommission
  cost; t0+days the engine opens the line; the line's own draw can push the counter to 3 within
  ~6 days, but the seed is re-read only at the NEXT monthly calculate, by which time the line
  has produced its first units (ASSUMED weeks, not months — a 1-2 factory line on a 11-14 IC
  chassis) and the stock / in-armies terms hold the mount. Failure mode if the first unit is
  slower than a month: one unmount/remount cycle at monthly cadence, bounded by the counter
  falling back once the line stops. Attrition end: stock 0 and in-armies 0 with the seed false →
  the component leaves at the next calculate — one rung change, no flap (nothing re-seeds it).
- Replay on `5d2a391c` (MEASURED inputs): GER latch open 1943.1-1943.11, counter pinned at 3 from
  1943.12; under (E) medium SPG / SPAA / TD stay mounted on stock + in-armies (SPG 2 356 stock vs
  need 1 482, SPAA 521 vs 384, TD 311 + 222 in armies vs 1 257), nothing new is seeded after
  1943.12, and no line is cut.
- NOT done, owner to decide: "empêcher de produire la variante améliorée" during a shortage is
  the `production_upgrade_desire_offset` layer, whose `id` is a per-country equipment TYPE
  (`tank_usa_heavy_chassis_5`), not an archetype — the equipment evaluator's KEEP_OLD /
  SWITCH_CONDITIONAL blocks (`WA_AI_PRODUCTION_COUNTRY_USA_TANKS.txt`, gated on
  `WA_AI_EQUIPMENT_can_absorb_tungsten_shock_small`) are that mechanism, generated per country
  by `tools/equipment_evaluator`; GER's generated file carries only heavy / modern hull entries
  today. A generic archetype-level form does not exist in the engine.
- Verification OWED (adds to the list above): next cloud campaign — after the twin, GER medium
  variants keep fielded/need ≥ 0.8 on stock; a country whose chromium counter reaches 3 mounts no
  NEW variant component that month (the `use_*` flip is visible as the medium value staying put);
  an importer (ITA / JAP) still mounts its first TD / SPAA when its counter reads < 3.
  Console: `event wa_test_tmpl.2 GER` on a 1945 save — `medium used=1 set=1`, pre = post.
- Consequence, stated: under (A) no AI template ever mounts a modern variant, so (C) only stops
  research slots being spent on techs the AI cannot feed; a country that CAN feed them still
  researches them and still fields the medium variant. If the owner wants "modern variants when
  affordable", that is the tiered-trigger seam (B) reading the same latch — not done, not asked.
- Cadence walk (template flip on a live campaign): t0 next monthly calculate — the twin value is
  unchanged (same +500), only its composition changed, so the engine sees a different target
  template under the same flag → one field-upgrade pass per division toward medium components.
  ASSUMED: no decommission pass (flag value and template names unchanged — the lessons log
  covers a flag FIRST setting, not a composition change under the same name); ASSUMED the
  upgrade completes — the medium variant stock is there, but the same twin still mounts the
  modern HULL the country cannot feed (MEASURED `1945.1` hull line chromium 0/102), and whether
  the engine's 90-day deficit valve (`UPGRADES_DEFICIT_LIMIT_DAYS`) is judged per template, hull
  included, is not known — if it is, the hull blocks the upgrade the variants would allow. The
  owed `imgui show ai_templates` arrow on a post-1944.10 save settles it. t1 production: modern
  variant need drops to 0, the parity factors on modern archetypes multiply zero; medium variant
  need returns and the medium lines re-open from stock. Regression risk: a country holding NO
  medium variant stock and a modern one (none observed) loses nothing — the medium archetype is
  what it researched first.
- Verification OWED: (0) owner console `imgui show ai_templates` on GER, post-1944.10 save: the
  arrow on the medium-armour divisions must point at the twin with medium component slots and the
  field upgrade must be running, not refused; (1) owner console `event wa_test_tmpl.2 GER` on a save after 1944.10 — the
  harness prints the per-role used/set pairs and the pre/post parity of one calculation pass
  (`WA_TEST_templates.txt`): `medium used=1 set=1`, pre = post, no orphan flag — it proves the
  twin value is still answered, not the composition; (2) composition is a static-file fact:
  `python tools/gen/gen_ai_medium_modern_mirror.py --dry-run` unchanged, `check_templates.py` clean on
  the mirror, boot test (`error.log` clean of `WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR`); (3) next
  cloud campaign: GER modern TD / SPAA / SPG need = 0 after the twin, medium SPG / SPAA
  fielded/need > 0.8 with stock falling, and `ger_modern_td_tank_1` NOT researched while
  `WA_AI_EQUIPMENT_chr_small_ok` is absent.
- Campaign-probe attempt 2026-09-04: NOT SCOREABLE — MEASURED: the `5d2a391c` campaign build
  (commit `7fafae8b9`, 2026-09-03 17:09) and even the newest branch saves
  (`GER_1945_04_17_02.hoi4`/`autosave.hoi4`, 2026-09-04 01:34-01:35) predate `9f9106802`/
  `a7ee778db` (01:38/01:43) — the component-seed half of the ADDENDUM 2026-09-04 b change. No
  save on disk reflects the full A+B+C+E change set; a new campaign run after 2026-09-04 01:43 is
  needed.
- Closed when: the campaign reading above holds on one cloud campaign.
- Previous state (kept): PARKED for the WIP limit (owner's standing choice from 2026-08-29), NOT because unverified.
  Commit `2dd063da1` (2026-08-30: tiered slot validation + dead-role-entry guards, ADDENDUM
  below) ships on top of the 2026-08-29 code; the addendum's own harness run
  (`wa_test_tmpl.2 USA`) and both imgui measurements are DONE and pasted there. Still owed from
  the 2026-08-29 ship: `event wa_abg.1 <TAG>`, whose section B2 prints the chassis tier — the
  SAME command as `armor-class-handoff`, so one owner run still covers both. Paste it and this
  unparks straight to TESTED.
- Scope: owner request 2026-08-28, design validated before implementation. Germany fielded medium
  tank divisions on the Panzer IV to the end of every campaign. Intended behaviour: a tank role is
  a WEIGHT CLASS of division, not a chassis generation — a medium division that reaches the
  Panther keeps its role and its share of the army, and every component of the template steps up
  one tier with the hull (medium TD → modern TD, light SPAA → medium SPAA).
- Root cause, MEASURED: `WA_AI_RESEARCH_needs_modern_armor` required `date > 1945.1.1`
  (`common/scripted_triggers/WA_AI_RESEARCH_tanks.txt` before this change) while
  `WA_AI_TEMPLATES_use_modern_armor` accepted modern from `date > 1942.9.1`. Every modern chassis
  `ai_will_do` carries `modifier = { factor = 0 NOT = { WA_AI_RESEARCH_needs_modern_armor } }`
  (`common/technologies/armor_ger.txt`, `ger_modern_tank_chassis_1`), so no AI researched a modern
  chassis inside a normal campaign and the modern role never opened. The 28-month gap between the
  two gates is the whole symptom; the template system was not at fault.
- Not a bootstrap problem (owner objection, retained): the production lever is
  `equipment_variant_production_factor` (`WA_AI_PRODUCTION_DEFAULT_tanks.txt`), undocumented in the
  engine's own token list but whose documented twin `equipment_production_factor` "increases the
  perceived needed factories" (`common/ai_strategy/documentation.info`, SYNCED 1.19.2.0). It is a
  multiplier on a NEED, and the need exists only once a template mounts the battalion — so the
  template leads and production follows, exactly as the light→medium switch already does
  (`WA_AI_CONFIG_switch_from_light_to_medium_armor` = a bare date, no stock guard). An earlier
  draft that opened the production line first was DROPPED, along with its stock threshold.
- Change 1 — research: `WA_AI_RESEARCH_needs_modern_armor` takes the shape of
  `needs_medium_armor` (focus medium/heavy, `date > 1942.1.1`). The binding date becomes the
  per-tech `ai_will_do` window (1943, or 1942 with free research slots).
- Change 2 — one ladder, two chassis tiers. `WA_AI_TEMPLATES_calculate_medium_armor_template`
  still picks the COMPOSITION and writes 6000–6116; a flat `+500` then picks the CHASSIS. Every
  value therefore needs a twin, so the mirror is GENERATED:
  `tools/gen/gen_ai_medium_modern_mirror.py` → `common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt`
  (19 templates, `role = medium_armor`, the shape `WA_light_support_armor_role` already uses). A
  component with no modern-tier answer is a hard error in the generator, never a silent copy.
- Change 3 — the switch is a one-way latch `WA_AI_TEMPLATES_modern_chassis_earned` (medium
  templates + modern chassis + mechanized), set on the monthly pulse BEFORE the calculate. One-way
  because two of its three terms are not monotone and a flickering gate re-runs the engine's
  template decommission pass. Owner rule: a focus-medium country with no mechanized never switches.
- Change 4 — `role = modern_armor` retired. `WA_AI_TEMPLATES_armored_modern.txt` gone, template
  type code 7 and the 8000–8999 range freed, `WA_AI_PRODUCTION_build_army_modern_armor` removed,
  the static `role_ratio id = modern_armor value = -1000` removed. The armour budget now has THREE
  open roles, never four: medium+heavy stays 17/8 instead of splitting to 10/5/10 the day the
  Panther lands. The modern slot in `WA_AI_PRODUCTION_armor_budget.txt` is KEPT at target 0 so the
  reconcile emits the exact negation of any entry a pre-change save carries — do not delete it
  before a campaign shows `WA_AI_ARMOR_BUDGET_modern` at 0.
- Change 5 — the German Panzer III/IV chain (`32dc70cb4`, shippable alone): `medium_tank_9` was
  enabled by `ger_medium_tank_chassis_3_3`, one tech before the chassis it designs;
  `medium_tank_8` had no zeroing modifier for `2_7` so the ladder never stepped past the Panzer
  IV H; `2_7` was missing from `has_medium_armor_unlocked`.
- Superseded a collaborator's parallel change (`b19bf6a43` and the commit that moved the six modern
  templates into the medium file, owner decision 2026-08-28 to keep this design instead). Their
  four 30-width component signatures are reproduced at 6611/6612/6613/6616; their tuned
  compositions (7 tanks + 3 SPG + 5 mech against the medium 9 + 6) are NOT preserved, because the
  mirror is structure-preserving by construction. Retuning is a pass over all 19 slots.
- Residual, ASSUMED (engine): at the month of the switch a division loses its
  `medium_armor_battalion_line` and gains `modern_armor_battalion_line` it cannot yet equip. Depth
  and duration are not observable in a savegame. Mitigations already present, no new code:
  `can_upgrade_in_field = { always = yes }`, `reinforce_prio = 1`, and the `+90`
  `modern_tank_chassis` production factor active the same month.
- Pre-existing defect found in passing, NOT fixed here: the medium ladder carries duplicate
  template NAMES — 6105/6108, 6106/6109, 6107/6110 are each two `ai_template` entries with one key
  inside `WA_medium_armor_role`. Only one of each pair can be reachable. The generator works around
  it by suffixing its mirrors (`..._6608`), which is why three mirror names carry a number.
- Verification — console harness: `common/scripted_effects/WA_TEST_armor_budget.txt` extended with
  section B2 (chassis tier) and verdict V4. Fire `event wa_abg.1 GER` from another tag on a save
  past 1943. **All FOUR verdict values must read 1**, and the `tier`/`band` lines must show: a
  country with the medium role open sits in exactly one band, and that band agrees with
  `owns-medium-role`. Owner run required to leave SHIPPED-UNTESTED.
- Verification — campaign probe: GER at 1944.6 fields divisions of role `medium_armor` mounting
  `modern_armor_battalion_line`; zero divisions of role `modern_armor` anywhere; no residual
  `role_ratio id = modern_armor` entry in any `persistent_strategy` block.
- Closed when: the harness reads 1/1/1/1 on GER post-1943 AND a campaign shows German medium
  divisions mounting the modern chassis before 1945.
- ADDENDUM 2026-08-30, tester report (156) + campaign `2d7b1b60` + owner-run `imgui show
  ai_templates`: two defects found in the shipped design, fixes prepared this session (working
  tree, not yet committed).
  - Defect A, MEASURED: the ladder validates component slots at the MEDIUM tier, then +500
    promotes them one tier up unvalidated. USA (modern chassis researched 1944.3, zero modern
    SPG/TD/SPAA techs through 1945.8) got 6616, whose 4 battalions + both regimental supports +
    2 divisional companies were unbuildable; the engine converged on an 11-battalion 22w
    "Modern Tank F" (28 divisions by 1945.8, match capped at 11/15 = 0.733). Fix: nine
    `WA_AI_TEMPLATES_use_*_armor_tiered` wrappers validate each slot at the tier the mirror will
    field; USA-shaped tech now lands on 6611 (all slots buildable). Emitted-value/declared-twin
    join re-verified: 19/19 both files. Tier offset registered
    (`templates_modern_tier_offset`, registry).
  - Defect B, MEASURED (imgui, 1944.3): both `role = medium_armor` entries sit in the engine's
    role-entry lottery; the entry with ZERO enabled targets drew pick 17.2% vs 0.17% for the
    live one — a permanent army-XP sink (engine doc: max one role-level entry per role). Fix:
    `[dead-role-entry]` prio guards — factor 0 on the medium entry once the modern latch is set
    (and when no flag), on the mirror entry without the latch (generator-emitted), and on each
    light entry without its own flag. Mitigation, not restoration of one-entry-per-role.
  - Verification: (1) DONE, MEASURED (owner screenshot 2026-08-30, `2d7b1b60` 1944.3 save with
    the fix loaded): `WA_medium_armor_modern_role (prio: 0, weight: 0, pick: 0%)` and
    `WA_light_support_armor_role` idem — trigger modifiers ARE honored in role-level
    `upgrade_prio` and prio 0 leaves the lottery; live medium entry unchanged (arrow on 6116,
    match 1). (2) DONE, MEASURED (owner screenshot 2026-08-30, same campaign run past 1944.4.1
    with the fix): arrow on `..._MODERN_ARMOR_30_MEC_MEDIUM_SPG_MEDIUM_SPAA` (6611), best match
    0.7 and free to reach 1; medium entry flipped to prio 0 / pick 0% — the guard works in both
    directions. (3) DONE (owner console 2026-08-30, `event wa_test_tmpl.2 USA`, 1944.4.3):
    `armour: ... medium used=1 set=1 ...` on pre AND post, line-for-line identical — role wanted,
    template answers, no missing claim guard. Full paste:
    `pre/post: foot: infantry used=1 set=1 | mountaineers used=0 set=0 | marines used=1 set=1 /`
    `armour: light used=0 set=1 | medium used=1 set=1 | heavy used=0 set=0 | light_support used=0 set=0 /`
    `conv: window=1 trans=5122 / other: motorized used=0 set=0 | mechanized used=1 set=1 | suppression used=1 set=1`.
  - Ship-time effect on already-latched campaigns, DERIVED: monthly recalc rewrites 6616 → 6611;
    one within-role retarget, then the 28 "Modern Tank F" divisions (11/15 = 0.733 vs 6611) can
    finish converting on buildable slots — the parked degenerate state heals instead of persisting.
  - Gate note: `check_constants` exit 1 from 6 pre-existing `@advisor_*` errors
    (`common/characters/ENG.txt`/`GER.txt`, commit `5e179dfb6`, unrelated files) — parked for the
    owner as its own candidate subject; this change adds zero findings.

### swi-militia — PARKED (2026-08-29)
- PARKED state: code SHIPPED 2026-08-28, owner console run STILL OWED (the Verification lines
  below are unchanged and still the exit). Parked, not closed, only to keep the OPEN WIP limit at
  4 when `mech-window` opened; nothing about the fix or its evidence changed. Un-park it by
  restoring the `SHIPPED-UNTESTED (2026-08-28)` heading.
- Scope: owner request 2026-08-28 — "the Swiss tree can't create or recruit any division".
  Intended behaviour: a Switzerland that starts under the Citizen Militia system can actually
  raise, activate and later professionalise that militia.
- Symptom (MEASURED, mod files, no save needed): Switzerland starts with
  `country_lock_all_division_template = yes` (`history/countries/SWI - Switzerland.txt:175`), so
  no template can be CREATED. Separately, the Swiss Citizen Militia — the one template the Swiss
  mechanic is built around — had its whole activation/conversion/penalty chain broken (cause
  below). The special-forces cap is NOT part of this symptom: MEASURED `31/55` on HEAD, 24 free
  battalions (see the fix-2 retraction).
- Cause (MEASURED, script lines): the unit-rename pass split vanilla `militia` into
  `militia_light_horse_battalion_line` / `militia_heavy_horse_battalion_line`. The template
  BUILDER was rewritten to heavy, the three template READERS were left on light —
  `common/decisions/SWI.txt:4246` (`has_template_majority_unit`, gates `SWI_activate_militia`),
  `common/scripted_effects/SWI_scripted_effects.txt` `SWI_turn_militias_into_regulars`
  (`division_has_majority_template`, the professionalisation conversion) and
  `SWI_dormant_citizen_militia` (`common/dynamic_modifiers/bba_dynamic_modifiers.txt:1378-1386`,
  five `modifier_army_sub_unit_militia_light_*` lines). All three matched nothing.
- Fix 1 (SHIPPED, uncommitted): `SWI_upgrade_template_and_divisions` now builds the Swiss Citizen
  Militia from `militia_light_horse_battalion_line` only (6 regiment lines), restoring vanilla's
  single-sub-unit template. Rejected alternative — repoint the three readers at heavy: rejected
  because the template is MIXED after the first upgrade and heavy ties light at levels 2, 6 and
  10 (10H/10L at max), so "majority" would still fail at max level whichever unit the readers
  name, and one dynamic modifier cannot cover two sub-units. Light is also the 1:1 port of
  vanilla `militia` (abbreviation MIL, `need = { infantry_equipment }` only).
- Verification (owner, console, any 1936 Switzerland game): `tag SWI`, then (a) the Swiss Citizen
  Militia template is recruitable and the counter reads 0/6; (b) the decision "Activate Militias"
  is available and not greyed; (c) after `add_ideas`/focus path to `SWI_professionalize_militias`,
  existing militia divisions convert to "Swiss Infantry Division". All three fail on HEAD before
  this change.
- Fix 2 — RETRACTED 2026-08-28, my premise was FALSE. I claimed Switzerland was pinned at
  `31/10` special forces and shipped a `special_forces_min = 24` idea for it. MEASURED (owner
  screenshot, HEAD, Division Templates screen): the readout is **`31/55`** — 24 free battalions,
  the cap was never binding. `SWI_alpine_army` (idea + history line + localisation) reverted;
  only fix 1 remains. Where 55 comes from is still UNKNOWN: it is not
  `max(SPECIAL_FORCES_CAP_MIN 10, 0.02 x 56 regular battalions)` from
  `common/defines/05_defines.lua:116-117`, nor the vanilla `max(24, 0.05 x 56)`, and no other
  `special_forces_min` / `special_forces_cap` source in `common/` applies to SWI at start. The
  lesson is the one this file keeps re-learning: a define read off the file is not the number the
  engine used — read the in-game tooltip before building on it.
- Fix 3 (SHIPPED, uncommitted) — the ACTUAL "cannot recruit", from the owner's third screenshot
  (decommissioned templates shown): Switzerland has 9 templates and 7 are DECOMMISSIONED,
  including `Swiss Citizen Militia` at **0/36** — the AI had raised the cap to 36 via
  `SWI_broaden_militias` and never trained one. MEASURED chain:
  (a) `common/ai_strategy/SWI.txt:213-229` still ships `SWI_template_design` with
      `ai_strategy = { type = template_prio  id = militias  value = 100000 }`;
  (b) the ONLY file that ever defined `role = militias` for SWI was vanilla
      `common/ai_templates/templates_SWI.txt` (`available_for = { SWI }`, target `militia = 9`);
  (c) `descriptor.mod` has `replace_path="common/ai_templates"`, so that file is DELETED from the
      running game, and WA's replacement folder defines no `militias` role at all (roles present:
      cavalry, heavy_armor, infantry x2, light_armor x2, marines, mechanized, medium_armor,
      modern_armor, motorized, mountaineers, suppression).
  DERIVED: the Swiss AI is aimed at a role no file defines, so its wanted militia count is zero
  (install `common/ai_templates/_documentation.md`: "The AI strategy `role_ratio` determines how
  many divisions the AI wants for each role"). ASSUMED, in no doc: that the same missing role is
  also why the engine decommissioned the militia and the other unmatched scripted templates.
  Fix: new `common/ai_templates/WA_AI_TEMPLATES_COUNTRY_SWI_militia.txt` — a `militias` role-level
  entry, `available_for = { SWI }`, `upgrade_prio = { factor = 0 }` (the template is
  `is_locked = yes`; the AI must not spend army XP trying to edit what it cannot edit), target =
  20x `militia_light_horse_battalion_line`, the end state of the scripted template after fix 1.
- Fix 4 (SHIPPED, uncommitted, owner decision 2026-08-28: Switzerland-scoped lever, not a global
  floor and not a re-tune of the weights). MEASURED (`imgui show ai_division_production`, SWI):
  21 active / **4 wanted** — fronts 25 x 0.08 = 2.00, factories 40 x 0.09 = 3.60, manpower
  65 x 0.07 = 4.55, threat 0.72; per-role militias 3/0, infantry 13/4, mountaineers 5/0. Full
  analysis in `division-target-scaling` (COUNTER-EXAMPLE bullet). New SWI-only idea
  `SWI_nation_in_arms` (`common/ideas/switzerland.txt`, `ai_desired_divisions_factor = 10`),
  added unconditionally in `history/countries/SWI - Switzerland.txt` so both DLC branches get it,
  plus name/desc/tooltip in `localisation/replace/afo_focus_l_english.yml`.
  Value derivation, and it is a DERIVED estimate not a measured one: the readout shows wanted 4
  while `SWI_citizen_militia_1` already contributes `ai_desired_divisions_factor = 1`, so the
  observed 4 corresponds to a total factor of about 2; a total of ~12 lands wanted near 24, i.e.
  just above the 21 divisions Switzerland already fields. **10 is therefore a first cut to be
  re-read in game, not a computed constant** — one number to change if the readout lands wrong.
  Carrier is a NEW idea for the same reason fix 2 could not use `armed_neutrality`: that one is
  shared with FIN/GRE and removed by `swiss.1`; `SWI_swiss_neutrality` cancels on war and
  `SWI_citizen_militia_1` is swapped out by professionalisation (which would silently drop 1 from
  the total — harmless at 12, but only because the new idea carries the bulk).
- Verification for fix 4 (owner, any Swiss save): `imgui show ai_division_production` for SWI
  shows `Nr Wanted Divisions` ABOVE `Nr Active Divisions` (target ~24 vs 21), and the per-role
  table gives `militias` a non-zero Wanted. If wanted lands far above ~24, lower the 10.
- Verification for fix 3 (owner, any Swiss save): `imgui show ai_division_production` for SWI
  lists a `militias` row with a non-zero wanted count; `Swiss Citizen Militia` is no longer
  decommissioned and its counter climbs off 0/36.
- Fix 5 (SHIPPED, uncommitted) — owner report 2026-08-28, blank focus title in the Swiss tree.
  Adjacent to this subject, not part of it: it is localisation, not recruitment. It has NO subject
  of its own only because the OPEN section is at the WIP limit; comment tag is `# [swi-loc]`.
  MEASURED: `SWI_purchase_german_planes` renders empty. Its vanilla loc is
  `SWI_purchase_german_planes: "[SWI_purchase_fascist_planes_name]"` — a SCRIPTED-loc indirection.
  `descriptor.mod:66` has `replace_path="common/scripted_localisation"`, which deletes vanilla's
  `BBA_Switzerland_scripted_loc.txt`, and WA never shipped a replacement — so all 25 of its keys
  resolve to the empty string while the vanilla .yml that references them still loads
  (localisation is NOT replace_path'd). Same failure class as fix 3.
  Fix: restored the file verbatim as `common/scripted_localisation/BBA_Switzerland_scripted_loc.txt`
  after checking every symbol it reads still exists in WA — 5 triggers
  (`SWI_country_has_alpine_states`, `_opinion_is_excellent`, `_opinion_is_good`,
  `SWI_dem_usa_valid_to_buy_planes`, `SWI_is_country_to_balance`) and 7 variables
  (`SWI_biggest_fascist`, `_confederation_president`, `_councilor_1`, `_angriest_country`,
  `_influence_target_state`, `_state_being_claimed`, `_last_angriest_country`). All present.
- Verification for fix 5 (owner, Swiss focus tree): the focus above "Ban the Swiss Communist
  Party" reads "Purchase German Planes" (or "Purchase Planes from Fascist Neighbor" when the
  biggest fascist neighbour is not GER), and no other Swiss focus/decision title is blank.
- Observation outside this subject, NOT admitted (one line per the admission rule): MEASURED,
  `replace_path="common/scripted_localisation"` drops **30** vanilla scripted-loc files, ~900 keys
  (largest: `FR_SCRIPTING_FULL_AUTOMATED` 337, `TOA_shared_military_branch` 120,
  `WTT_china_political_struggle` 100, `WUW_GER` 62, `TAOG_AST` 48, `BBA_ethiopia` 46). Switzerland
  proves at least some of that is unintentional. A sweep would need, per file, a check that the
  keys are still referenced and the symbols still exist. Owner call whether it becomes a subject.
- Observation outside this subject, NOT admitted (one line per the admission rule): MEASURED,
  `SWI_expanded_special_forces` (the reward of focus `SWI_expand_special_forces`) is INERT under
  WA's numbers — `special_forces_cap = 0.3` scales the 2% path (`0.026 x 56 = 1.5`), which never
  beats the floor for a country this small. Every percentage-only `special_forces_cap` grant in
  the mod has the same problem. Owner call whether it becomes a subject.
- Closed when: the owner pastes (a), (b), (c), the fix-3 / fix-4 readouts and the fix-5 title here.

### allied-division-stability — PARKED (2026-08-28)
- PARKED 2026-08-28 only to make room for `modern-chassis-tier` under the WIP limit, by the agent,
  not by an owner decision — move it back to OPEN in one line if that is the wrong pick. Chosen
  because it is the only live subject owing the owner NOTHING right now: its Step A defines are
  shipped and its verification is a campaign probe that has not been run, so it waits either way,
  whereas the SHIPPED-UNTESTED subjects each owe a console-harness run. Step B (the hysteresis
  pass) was never started.
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
- **Campaign `1ac7e4ea` (first post-defines, 2026-08-27): probe (i) SPLIT — ENG PASS, USA FAIL.**
  MEASURED (8 war saves, closure 24/24 vs `army`): ENG in-transit 0-22 % vs baseline 13-45 %
  (ceiling 45→22, 5/8 saves below the old floor; at-sea 0-5 % — never > 1 division afloat; rear
  churn 20 %, into the GER band); USA 7-64 % with 1944.7 ABOVE the pre-fix ceiling 55 % — at-sea
  alone 21-53 % over 4 consecutive samples incl. **46 % at 1944.4 with no invasion order in the
  save**, rear churn 75 % (19/28 rear divisions at sea across the pair). GER control valid on
  at-sea only (0-3 %); the hostile-ground bracket is VOID for a contiguous power losing ground
  from 1944.10 (its front stands on flipped provinces). Trap re-confirmed: raw churn ENG 62 % /
  USA 64 % / GER 28 % — does not discriminate. **Probe (ii) FAIL, soft**: no order born at 0 div
  and the campaign's sole type-3 order (Madagascar 1942) was manned, but 4 post-1942 fronts held
  at 1-2 divisions with idle pools elsewhere — worst 1945.6: ENG Gabès/Batna front 2 div while
  USA idles 35/56, TWO of them in Batna on the starved front's own path. The defines took on ENG
  and did not take on USA; USA's at-sea shuttle is Step B's sharpest case.
- **USA-shuttle diagnosis COMPLETE 2026-08-27 (six-boxed).** MEASURED: at 1944.4 the 26
  at-sea divisions are 10 buffer + 13 front + 3 areadef, ZERO invasion class; 8/8 tracked
  division ids changed ARMY between every consecutive save-pair, routes Meknes→N.Texas,
  Constantine→Arkansas, Panama→Hawaii (westward) vs N.America→Essex (eastward) — the wrong
  ocean for Normandy, rival "D-Day staging" killed (positive control: 1944.7 buffer-at-sea
  = 1 while 29 front-class cross for the real landing). Org of shuttling ids frozen at 7-15
  for 3 months vs 153 once parked — the shuttle costs the entire recovery curve. Trigger
  inputs byte-identical across 1944.3-5 (control table unchanged): a STANDING demand the army
  cannot satisfy, not a toggling trigger. Mod decision (DERIVED trigger-walks): TWO scripted,
  simultaneously-armed, antipodal, permanently-unmet buffer pools —
  `unit_buffer_for_europe_aggressive` (`USA_THEATRE.txt:725-747`, britain ratio 0.5 = 28
  demanded, 7 delivered) vs `buffer_pacific` (`USA_THEATRE.txt:216-338`, ELEVEN entries on
  ONE order_id 9101, ratios summing **1.92** = 107 divisions demanded of a 56-division army,
  9 of them `subtract_fronts_from_need = no`) + `theatre_boost_pacific` demand raise (:396).
  Aggravators: `order_id = 1` shared by three blocks over three antipodal areas
  (britain 0.5 / usa_east 1.0 / philippines 0.25 — engine behaviour for differing ratios on
  one id UNDEFINED; `REGION_ITALY_THEATRE.txt:25` states the one-id-per-buffer rule and
  ENG_THEATRE follows it with 17 distinct ids, USA_THEATRE does not — **that asymmetry is
  why the defines took on ENG and not USA**); `unit_clumping_fix_3` (`USA_FRONT.txt:385`,
  `always = yes`, −25 on north_africa = USA's only live front, own comment asks for
  campaign-evidence revisit); the dday_prep window's four negatives exactly spans the
  at-sea climb 19→46 %. Engine boundary ASSUMED: arbitration of differing ratios on a
  shared order_id; whether an all-enemy-held states list poisons its pool; per-area
  front_unit_request aggregation. Owner imgui (USA, 1944-shape) names the armed variants.
  **Step B lever menu: (1) split the order_ids; (2) cut the Pacific pool (1.92 →
  realistic, or drop the nine subtract_fronts_from_need = no); (3) enter/exit hysteresis on
  the britain buffer; (4) one-ocean-at-a-time exclusion gate; (5) retire
  unit_clumping_fix_3. 2 and 4 are material and must not ship in the same commit as each
  other.**
- **Levers 1 + 5 SHIPPED 2026-08-27 (owner order "applique les levers 1 et 5 USA").**
  (1) `USA_THEATRE.txt`: usa_east buffer (oh_shit) order_id 1 → 9103, philippines 1 → 9104;
  the four britain variants stay on id 1 (same states/ratio, scenario-exclusive enables =
  one logical buffer). **Causal claim DOWNGRADED per lessons review**: the log MEASURED that
  a shared order_id produces SEPARATE order instances (ENG had two live id=1 orders), so
  "distinct ids cured ENG" is refuted — the split is hygiene per the REGION_ITALY rule, and
  the live unmeasured suspect for the shuttle is the ARBITRATION of summed ratios > 1.0
  (britain 0.5 + usa_east 1.0 + philippines 0.25, Pacific pool 1.92) — unchanged by this
  ship; lever 2 is the ready follow-up if the shuttle persists. (5) `unit_clumping_fix_3`
  DELETED whole (legacy-gates rule; own comment demanded campaign evidence; single
  definition, no other reader; siblings _2/_2_south_italy READ and left — _2 is also
  always-on but on region 161/23 + state 633, not the diagnosed front — noted for a later
  revisit). Honest path for north_africa now: engine default + the un-suppressed
  ALLIES_FRONT +75/+10 bids. Reviews: architecture OK (core:200 weaker-on-purpose sentence
  added; pre-existing observation: order_id 9101 already spans central_pacific AND
  central_america — same undefined pattern, candidate for this subject later) + lessons
  CONCERNS (all applied: causal downgrade above; **F9 boot test OWED before the next
  campaign — the CTD lesson treats ai_strategy BLOCK DELETIONS as launch-test-requiring**).
  Verification (fingerprint, per lessons — not "cured by split"): next campaign, USA's
  put_unit_buffers order instances are STABLE PER OCEAN across consecutive saves (plans.py
  --armies: buffer army membership not flipping between atlantic and pacific states
  month-over-month), buffer-at-sea share in non-invasion months ≤ GER's band, and probe (i)
  USA in-transit range compared save-for-save against this campaign's 7-64 %.
- Closed when: (a) ENG+USA transit share drops vs the pre-fix baseline at matched dates, (b) no
  starvation regression — no active front under-manned while idle divisions sit in a quiet
  theatre (F-items unaffected), (c) owner confirms the in-game impression improved.

### aifc-traction — PARKED (2026-08-29)
- Parked 2026-08-29 (WIP limit, `mot-field-hospital` enters on owner request). State at
  parking: Option A SHIPPED 2026-08-27, unverified — `WA_TEST_aifc.txt` carries the
  independently re-typed election and is waiting on one owner console run. Reopen by
  pasting that output; nothing in this subject is blocked on code.
- **Option A SHIPPED 2026-08-27 (owner order "partons sur A").** Main-enemy election rebuilt: §1c no
  longer elects (strict-max removed); new §1d elects the enemy whose FLOOR-ELIGIBLE candidates
  (pad > `constant:wa_ai_aifc.selection.min_pad` — the constant's documented second role) carry the
  largest SUM of pad bands (`WA_AI_AIFC_helpers.txt`, railway find-or-append idiom, temp books
  cleared head+tail). Kills the residual L3 shape: a single token pad (desert band-2 vs ITA) can no
  longer outvote a distributed real front (France/Tunisia vs GER); floor-ineligible candidates do
  not vote, so 1-division contact chains elect nobody; zero eligible candidates → main_enemy 0 →
  no sector (unchanged safe path). Section 2, §1b filters, validity mirror, FIX-65, ITA/ETH mission
  steering untouched. Headers synced (helpers SELECTION MODEL + FRONT_aifc.txt); harness
  `WA_TEST_aifc.txt` carries an independently re-typed election (per-enemy `eligible-pad-sum` lines
  + elected-enemy line). Accepted residuals: pre-D-Day single-front desert pointer persists (no
  alternative front exists); sum measures border geometry × mass (a pad state counts once per
  adjacent candidate); election flips at sum near-ties cost ~4 permanent type-83 entries per flip,
  ~48/yr worst case — full t0/t1/t2 table in session scratchpad `aifc_scorer_fix_options.md`.
  Reviews on the diff 2026-08-27: architecture OK; lessons CONCERNS (2 items, both applied:
  this WORK.md record; `_aifc_ctrl` loop-head init added). Checkers: constants 0 err/0 warn,
  worklist 0 ERROR. K=2 grace and the two-state dead-band alternative remain UNSHIPPED (designs
  ready in the scratchpad, owner decision pending).
- **Owner console run owed (moves this back to TESTED): `event wa_aifc.1 ENG` on the 1944.6.20+ fork
  (expected: `enemy :` sum lines printed, elected = GER with France/Tunisia mass vs desert ITA sum)
  and `event wa_aifc.2` (GER/SOV: elected enemy unchanged vs pre-fix, anchors still on their main
  front).** F9 boot OWED (scripted-effect edit). Campaign probe (L3 replay): no country keeps a
  byte-identical corridor > 6 months at 0 % held WHILE another enemy carries a larger eligible pad
  sum; GER/SOV anchors still stable 2 quarters (L1 regression watch); L3c retire_n watch unchanged.
- **Owner console run pasted 2026-08-27 (`wa_aifc.1 ENG`, save 1945.7.5) — the merge-bar build
  is live and correct, subject back to TESTED.** Scope header `1 1 1 1 0` (valid measurement);
  elig all green, shipped trigger 1. Key lines: native candidates Western Desert pad=1 /
  Cairo pad=1 / Libyan Desert pad=0 → all anchor-eligible=0 (floor); `exp-gate(native-maxpad
  <=2)=1` — the capability gate OPENED and the ally walk RAN; **`ally-states-with-5+div=0`**
  (new bar printed and enforced: no allied state holds 5+ ENG divisions) → zero merged
  candidates → **NO sector**. That is the shipped design working end-to-end: no decorative
  desert pointer (the old L3 pathology), Layer 4 inert, engine default targeting — AND it is
  the dead-band instance flagged at ship time, now live: ENG at 23 divisions spread 3-4/state
  gets no schwerpunkt at all. The two-state alternative (2 ally states at 3+ ROOT divisions)
  remains the ready lever if the owner wants dispersed liberators served; unshipped.
- **Lever 2 SHIPPED 2026-08-27 (owner order "lever 2 AIFC").** §1b merge admission bar
  (`WA_AI_AIFC_helpers.txt`): `divisions_in_state > 2` → `> @AIFC_PAD_T2` (5+ own divisions
  — the ally state must BY ITSELF be a band-2 launching pad). Kills the Gabès ferry-stop
  admission (4 div). Validity mirror (core:200) kept at > 2 DELIBERATELY — keep-while-valid
  hysteresis, now commented at the site ("do not raise to match"); architecture confirms
  weaker-validity is the safe direction (churn only comes from validity stricter than
  admission). Harness copy re-typed to > 4 + labels 3+→5+ (contract rule 4).
  **Dead-band population, enumerated and OWNER-FLAGGED (lessons item 3): the new bar also
  excludes every measured 3-4-division-per-state expeditionary case** — BUL-Gabès
  (intended), ENG 1944.7 France/Algeria (3-div states — no behaviour change, those
  candidates lost the scoring anyway), and **USA 1944.7 (Loire 4 / Paris 3 / Centre 3 /
  Picardy 3 — the campaign's one clean L3d success: under the new bar that corridor would
  NOT form; a dispersed liberation army spread 3-4/state now falls back to native-only →
  usually no sector → Layer 4 inert, the documented safe path). Accepted reading: the merge
  now serves only CONCENTRATED invasion armies; if the owner wants dispersed liberators
  served, the bar needs a two-state alternative (e.g. 2 ally states at 3+) instead of a
  lower single-state bar (> 3 would re-admit Gabès at 4).** Reviews: architecture OK,
  lessons CONCERNS (all applied; no flap table owed — the bar only REMOVES candidates,
  worst case = today's native-only selection). Checkers: constants 0 err, worklist 0 err.
  Owner console run owed (moves back to TESTED): `event wa_aifc.1 ENG` (fork 1944.6.20+) —
  expected `ally-states-with-5+div` printed and no merged candidate from a < 5-division
  state; F9 boot covers the effect edit.
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
- **Campaign `1ac7e4ea` (first post-floor + post-gate, 2026-08-27): L2 PASS, L3d PASS; L1/L3/L3b
  FAIL; L3c FAIL localised. R1 weekly churn ABSENT from every live tag (age never pinned at 1;
  GER anchors held 2 quarters each).** MEASURED (aifc.py, 13 quarterly + 12 bimonthly saves):
  **L2 PASS** — USA sector 1944 Q3+Q4 (458 Tunisia / 18 Champagne) and 1945 Q3→1946 Q1; the
  quarterly grid ALIASES it (bimonthly sweep required; USA still sector-less 10/18 months incl.
  1945.1-1945.7). **L3d PASS** — USA 1944.7 corridor = 6 FRA/BEL-owned states while USA controls
  zero European states: only the §1b expeditionary walk can have produced it; junior partners
  carry the leader's corridor byte-for-byte (ROM/HUN≡GER, MAN≡JAP, AST/RAJ≡ENG). **L1 FAIL** —
  3 of 4 GER/SOV fresh selections put < 18 % of non-garrison divisions in+adjacent (generous
  name-adjacency); corridor province gain ≤ 0 in 4 of 5 six-month windows. **L3 FAIL** — ENG 32
  months byte-identical Western Desert corridor at 0/71 provinces held (the exact shape the
  floor shipped to kill; also GXC 42mo, MEN 42mo, JAP 30mo, ITA 30mo at 0 %). **L3b FAIL** —
  BUL 1945.7 holds ITA's 8-state Algerian corridor while its only NA foothold is Gabès at 4
  divisions (band 1): a live floor bypass to diagnose. **L3c FAIL (ENG/USA only)** — retire_n
  ENG 0→14, USA 5→14 monotone, type-83 ledger 10-13× distinct pairs (737/70, 799/61); GER/SOV/
  JAP/ITA flat — co-occurs with their sector on/off flicker; not weekly, but unbounded ledger
  bloat with no compaction. **Key negative on the new gate**: ENG 1944.7 native best pad = 2 =
  NOT > exp_gate_pad, so the ally walk RAN and the merged French/Algerian candidates LOST the
  score to the defender-side-weighted desert (+20 desert +40 thin +20 non-core vs pad ~5-10) —
  the residual L3 lever is the scorer's defender-side terms / an own-mass corridor term, not the
  gate. Dead-tag trap for the tooling: SHA shows age=1 in all 13 saves but is annihilated
  pre-1940 (frozen variables) — aifc.py needs a liveness annotation or its own footer misleads
  (shipped under `analysis-tooling` same day).
- **L3b diagnosis COMPLETE 2026-08-27 — NOT a bypass; the floor ran and PASSED on its
  calibration.** Six-boxed, all three hypotheses REFUTED with killing measurements: no
  copy path exists (`sector_states` written only inside `select_sector`, helpers:351/386;
  HUN anchored 224 while GER anchored 205 same save — same faction, different answers; BUL age
  2wk ≠ ITA 4wk), not stale (BUL held NO sector in the 5 surrounding monthly samples — the
  corridor lived ONE sample and the validity mirror killed it the month BUL left Gabès), pad
  counts ROOT divisions only (helpers:195/:252-260; the 2→4→0 Gabès natural experiment).
  MEASURED mechanism: Gabès (665, neighbour of 514) held 4 BUL divisions in the selection
  week = pad band 1, plus a second occupied state or a 5th division mid-ferry → band sum 2 >
  `min_pad = 1` — a ferry stop qualified as a launching pad. Byte-identical junior corridors
  are EXPECTED without copying: identical anchor ⇒ identical corridor (deterministic
  neighbour walk, helpers:370-402), and §1b derives a junior's whole candidate set from the
  leader's territory. WORK.md correction: the validity mirror is NOT only
  "enemy-held + adjacent" — core:200 carries `divisions_in_state > 2` on the expeditionary
  branch (weaker than selection: any-neighbour, not band sum — a pad-2 sector survives at
  pad 1; real asymmetry, not this cause). Candidate levers (owner decision, nothing shipped):
  (1) `min_pad` 1→2 (wide blast radius — decides whether small belligerents keep sectors),
  (2) merge admission bar helpers:195 `> 2` raised (narrower — stops transient ferries at the
  source; FIX-65 liberator reach is the trade-off), (3) re-band pads (widest, moves
  exp_gate_pad too), (4) mirror the floor into validity core:191-201 (independent, fixes the
  asymmetry), (5) K=2 retirement grace at helpers:728 for the L3c ledger growth (section 0
  :670-679 already computes the lapse state; K unsizeable from saves — needs the harness;
  no compaction is possible, entries retire only by exact negation, ENG's 737-entry ledger
  is arithmetically correct and inert, its LENGTH is the only cost). Recommended: measure
  lever 2's blast radius across the campaign's junior partners before choosing 1 vs 2.
- **Residual-L3 mechanism re-diagnosed 2026-08-27 (source read): the failure stage is the MAIN-ENEMY
  ELECTION, not the scorer.** The desert (vs ITA — MEASURED sector_enemy) and the real front
  (Tunisia/France vs GER — MEASURED fork) have different controllers, so the scorer NEVER compares
  them: election (`WA_AI_AIFC_helpers.txt:277-281`) takes the strict max pad, first-seen wins ties,
  and `_aifc_cand` enumerates native (§1) before merged (§1b) — a single token pad-2 elects the
  stale enemy against an army whose total mass faces the other one. WORK.md's earlier "lost the
  score" wording was imprecise. Remaining unknown (one): the merged candidates' exact pads in the
  1944.7 selection week (tie vs strictly lower) — `wa_aifc.1 ENG` on that save would settle it;
  both cases are covered by the proposed fix. **Options PROPOSED to owner (Option A ORDERED and
  shipped same day — see the head of this entry)** — full a-g analysis, flap table under the measured type-83 accumulation
  defect, and both ready levers (K=2 grace; two-state dead-band alternative) in the session
  scratchpad `aifc_scorer_fix_options.md`. Recommended: Option A — elect the main enemy by
  PER-ENEMY SUM of pad bands over floor-eligible candidates (pad > min_pad) only; section 2,
  §1b filters, validity mirror, ITA/ETH mission steering all untouched; no new constant.
  Design reviews run 2026-08-27: lessons CONCERNS (break var + entry-init, id-encoding header
  sentence, t0/t1/t2 flip table with accumulation — all integrated into the proposal) +
  architecture CONCERNS (helpers SELECTION-MODEL header sync, dual-behaviour election comment,
  head+tail temp clears, min_pad second-role sentence, subject → SHIPPED-UNTESTED on ship — all
  queued as ship-time items). No CONFLICT.
- Closed when: each leg carries a six-box diagnosis naming the script line or documented engine
  boundary, AND per leg either a fix ships under this slug and its verification line passes in a
  campaign, or the owner accepts a written no-fix ruling.

### levant-iraq-corridor — PARKED (2026-09-04)
- Parked 2026-09-04 by the agent, not by an owner decision, to admit the owner's two 2026-09-04
  orders (`usa-pacific-hoard`, `eng-reserve-partner`) under the WIP limit — move it back to OPEN
  in one line if that is the wrong pick. State at parking: SHIPPED-UNTESTED since 2026-09-02,
  owner console run owed; nothing else changes.

Owner order 2026-09-01: while the holder of Jordan (state 455) is at war with the Iraqi power, that
holder must use PRIORITY CONSTRUCTION to place a supply depot on province 4440 — the Jordanian
province bordering Iraq — and connect it to the rail the Levant already has; stop once the Iraqi
power capitulates.

- Origin (MEASURED, campaign `8c42d288`, 107 monthly saves 1936.2-1944.11): the owner asked whether
  this already happened for ENG once Iraq joined the Axis. It does not exist. **No WA system places
  a supply_node anywhere on a Palestine/Jordan → Iraq line**: the PC theatre-corridor family is the
  only depot builder (`corridor_hub_kind_ = 17`) and its single corridor was North Africa,
  Oran → Alexandria. The `supply_node` counts of all ten Levant/Iraq states are byte-identical at
  1936.2 and 1944.11. What DOES exist there is the separate `[rail-corridors]` free-rail cheat,
  whose corridor 6 laid level-5 track Palestine → Baghdad on **1939.10.1** — 18 months before IRQ
  joined the Axis (1941.4.24) and across neutral Saudi and Iraqi ground. That cheat's own defect is
  a different subject (see the end-of-session note in the session log, not admitted here).
- Shipped (this session, one commit): the PC theatre-corridor family generalised from ONE hard-wired
  corridor to N. `WA_AI_PC_railway_corridor_pass` is now the interval gate + civ floor + call list;
  the old body is `WA_AI_PC_railway_corridor_run_one`, called per corridor with `_corridor_id_` and
  `_corridor_type_id_`. New corridor 2 `levant_iraq` (7151 Ma'an → 4017 Amman → 4440 Ruwaished,
  depot on 4440 only, no port, no node inside Iraq). New gate
  `WA_AI_PC_corridor_theatre_live_levant_iraq` = the OWNER of state 291 is at war with ROOT and has
  not capitulated — tag-free, closes on capitulation / annexation / white peace. New band term
  `_corridor_war_band_` (NA declares 0 = unchanged; Levant declares 1, because its node list is
  entirely behind our own lines and the enemy-held-node rule would price a wartime measure as
  preparation). New `constant:wa_ai_pc.type_id.corridor_levant = 28` + registry group + `savegame.py`
  `_PC_TYPE_ID` row.
- **Why one type_id PER CORRIDOR, not one per family.** `run_one` ends with a stale-path validation
  that cancels every queued project carrying its `_strategy_id` whose target province is not on the
  routes it just pathfound. Two corridors under one tag would cancel each other's in-flight segments
  every pass — the regression the first draft of this change would have shipped. The per-tag
  `queue_max` follows, so the corridors do not compete for one budget either.
- Map facts the design rests on (MEASURED 2026-09-01, `map/railways.txt`, `map/supply_nodes.txt`,
  `map/definition.csv`, generated province graph): 4440 is land/arid, has no supply node and no rail,
  its only Jordanian neighbour is 1544, and its neighbours 13831/13832 are state 675 (Iraq). 7151 and
  4017 both carry a supply node and are railed to each other at L1 via 10089. **Every node and every
  intermediate province the pathfinder can pick is inside state 455**, so all segments are
  admission-scoped to one state and the pathfinder/admission mismatch that forced junction 13481 into
  the North African list cannot arise. The gap the corridor closes is the four edges
  4017-4591-4574-1544-4440, all at level 0.
- **Residual 1 — the corridor is chartered by a WAR and can be cut off mid-build.** t0 the Iraqi
  power capitulates or is annexed → the gate reads false. t1 at most `corridor.interval_weeks` = 4
  weeks later, on the next corridor pass, `corridor_ran_` is 0 and nothing new is queued. t2 in-flight
  type-28 projects are NOT cancelled by that pass — the validator lives inside `run_one`, which the
  closed gate skips — so they drain through the normal PC allocator or are swept by the 30-week stall
  sweep. Worst case: a half-paid depot finishes after the war it was for. ACCEPTED — a depot on the
  Iraqi border is not waste, and cancelling it would need the validator to run on a corridor the gate
  just switched off, which is the "an empty valid set cancels 100 % of the queue" hazard the pass is
  explicitly built to avoid.
- **Residual 2 — two war-band corridors on one builder. NOT bounded by the type_id split, and the
  word is not used.** Separate tags separate the ADMISSION budget, not the factories: both corridors
  emit at `prio.rail_war` (1000) into one priority-sorted queue, and `WA_AI_PC_assign_factories` sorts
  by priority alone, so at a tie insertion order decides. The case that exists is ENG holding Egypt
  and Jordan while at war with the Iraqi power. t0 the Iraq war opens → corridor 2 arms at band 1000
  with **zero** contested nodes (`_corridor_war_band_ = 1`), alongside corridor 1 already at 1000
  because North Africa has enemy-held nodes; ceiling in flight doubles from 8 rails + 8 depots + 8
  ports to 16 + 16 + 16. t1 +4 weeks (one corridor interval): corridor 2 offers at most 4 rail
  segments (4017-4591-4574-1544-4440) plus one 10 000-IC `supply_node` at 4440, against corridor 1's
  ~20-pair list — so the *added* head-of-queue load is small in count but the depot alone is 12.5× a
  rail segment (800). t2 +12 weeks: with ~1 project admitted per province per pass, the four rail
  links need ≥ 4 passes ≈ 16 weeks to all be queued, and the depot competes with them the whole time.
  Consequence, stated plainly rather than called bounded: **for the duration of the Iraq war the
  lower bands — theatre air 350, air front 300, strategic 250 — get less of that builder's civilian
  allocation than they did.** Owner-ordered. The campaign probe below reads it (leg (c)).
- **Two states this subject must never conflate:** *queued* ≠ *built* ≠ *connected*. A `supply_node`
  admitted at 4440 is not a hub delivering supply — a hub has no level and carries whatever the
  railway feeding it delivers (LOGISTICS_MODEL §3), and an unconnected forward depot was the visible
  symptom of Fix 120. The closing criterion therefore asks for the depot AND the four edges.
- Reviews 2026-09-01, both run on the full diff, both **CONCERNS**, all repairs applied:
  **lessons** — (1) the `_project_type_id > 0` fallback was written against 0 while an unset temp
  reads as a scope token; removed, and the tag is now derived ONCE at the entry of `run_one` by
  equality on `_corridor_id_`, so no site tests an unset temp; (2) `_corridor_id_` / `_corridor_type_id_`
  zeroing moved OUTSIDE the civ-floor branch; (3) the "bounded budget" claim replaced by Residual 2
  above; (4) stale cap headers refreshed. **architecture** — (5) all WA_TLM writes of the pass (r95
  and r103 counters included, not only the gauges) now sit behind `_corridor_id_ = north_africa`, and
  `r103_corridor_blocked_n` in `railway_helpers` with them, so no existing metric is retargeted;
  corridor 2 emits none by design, its outcome being directly save-readable. No `wa_tlm_version` bump
  — no name, unit or semantic changed. (6) `WA_TLM_TELEMETRY_SYSTEM.md` write-site names and scoping
  updated; (7) the corridor-id enum promoted to `constant:wa_ai_pc.corridor_id.north_africa/levant_iraq`
  (read in three files); (8) the allocation consequence written into the pass header.
- Harness: `WA_TEST_levant_corridor.txt` + `events/wa_test_levant_corridor.txt` (contract v1).
  `tag ENG` then `event wa_lcor.1` = passive report (gate terms, per-node ours/charge/enemy, depot
  presence with 7151/4017 as the known-true control, per-EDGE rail levels, type-28 queue rows);
  `wa_lcor.2` forces one corridor-2 pass; `wa_lcor.3` is the known-false control — the same forced
  pass with an unknown corridor id must queue nothing. **OWNER RUN OWED** — output pasted here moves
  this to TESTED.
- **WIP collision, owner arbitration owed**: this makes 5 non-parked subjects against the limit of 4.
- Closed when: (a) the console harness run shows LIVE=1 for the holder of Jordan while at war with
  the Iraqi power, type-28 queue rows at the war band, and `wa_lcor.3` queueing nothing; AND (b) a
  campaign in which the holder of Jordan fights the Iraqi power shows a `supply_node` at province
  4440 that was absent at 1936.2, with the four edges 4017→4440 rail-continuous
  (`control 455 --buildings` + `rail.py 4017 4440`); AND (c) the control: North Africa's corridor
  projects and its `wa_tlm_r107_sizing_*` gauges are unchanged in the same campaign.


## PARKED

### axis-minor-home-buffer — PARKED (2026-09-10)
- Parked because the four OPEN slots are occupied. The implementation is committed as
  `SHIPPED-UNTESTED`; keep it parked until a slot frees up for the owner console run.
- Owner request: non-major Axis faction members keep 25% of their army at home while at war.
- Implementation: shared dynamic gate `WA_AI_MILITARY_should_axis_minor_keep_home_buffer_theatre`;
  Country THEATRE writers for FIN, HUN, ROM, BUL, SLO and CRO target their own home states
  with `put_unit_buffers`, order 9620, ratio 0.25, and both `subtract_*_from_need = no`.
- Amendment 2026-09-11 (owner): the writers listed only the capital state, which parked the whole
  reserve in one interior province. Each country now carries TWO blocks - a frontier tier (order
  9620, ratio 0.15, `subtract_fronts_from_need = no`) over its border states and an interior tier
  (order 9621, ratio 0.10, yielding) around the capital. They sum to the owner's 0.25. The split by
  order id rather than one longer list follows Fix 110: MEASURED on campaign `07270b64`, a flat
  nine-state Italian buffer put six divisions inland and none on the invasion shore.
- Amendment residuals, all ASSUMED: that an unfriendly listed state is dropped while the rest of
  the list arms (the engine documents only "if no state is friendly, strat is invalid"); that
  "friendly" excludes an ally-held state (it probably does not - CRO 887/103 and ROM 76 may be
  ally-held); how N listed states split into engine order instances, hence what `ratio` means per
  state. FIN drops 146/972 from both tiers because its winter-war orders 2/3 already hold them; its
  non-yielding sum is still 0.90 against the 0.75 E4c budget - pre-existing debt, reduced from 1.00
  by this split, closable only by retuning the winter-war blocks (different subject).
- Impact: this deliberately coexists with `WA_AI_MILITARY_total_commitment_active`; the existing
  generic `garrison = -5000` release remains, while the explicit buffer preserves the requested
  home reserve. The lessons review required explicit subtract flags and rejected a shared Faction
  state list; the architecture review required Country-tier writers.
- Verification: boot with no strategy parse errors; then campaign-check FIN/HUN/ROM/BUL/SLO/CRO in
  a German-faction war, including a safe-war `total_commitment_active` window, for armed 9620 and
  9621 buffers and approximately 25% of fielded divisions across the home states. The reading is
  divisions PER LISTED STATE, not a total: at least one FRONTIER state garrisoned in every country
  is the owner's actual request, and a flat total hides the Fix 110 failure. Also read the buffer
  order states before and after the Second Vienna Award and the Dalmatian transfers (the
  partial-ownership and friendly-versus-owned test), and FIN's total areadef share - at or above
  70% is the `minors_home_first` failure signature. Confirm GER/ITA are
  unchanged and a non-Axis minor has no 9620 entry.
- Closed when: the boot check and the campaign checks pass without a regression in the existing
  total-commitment release behavior.

### war-start-suppression-template — PARKED (2026-09-10)
- Parked at creation because the four OPEN slots are occupied. The implementation is applied in
  the working tree and remains uncommitted; move it to SHIPPED-UNTESTED when a slot frees up.
- Owner order 2026-09-10: on war start, give each AI a named `Suppression template` using a
  50-width cavalry design with military police when `tech_military_police` is researched, and a
  5-width fallback otherwise; do nothing when the named template already exists.
- Change: `WA_AI_TEMPLATES_create_war_suppression_template` is called by the existing engine
  `on_war` hook and guards both branches with `is_ai` plus `NOT has_template`.
- Change addendum: before creation, the effect deletes every `Light Cavalry template A` through `Z`
  with `disband = yes`, including when `Suppression template` already exists.
- Harness: `event wa_test_tmpl.3 <AI_TAG>` logs the AI/MP/existing state and the A/Z purge boundaries
  before and after two direct calls; the resulting regiment/support composition still requires the
  owner’s manual template check.
- Regression risk, DERIVED: only AI countries entering a war are affected; existing named templates
  and the separate WA suppression `ai_template` role are untouched. The purge intentionally removes
  any divisions using those lettered templates because it uses `disband = yes`. The fallback uses one
  2-width cavalry battalion plus one 3-width artillery battalion because the active suppression units
  in `common/units/land_cavalry.txt` and `common/units/land_artillery.txt` have those widths.
- Verification (owner game): start a war with an AI that has and one that lacks `tech_military_police`;
  inspect both countries' `Suppression template` designs, then fire another war entry after the
  template exists and confirm it is not duplicated or replaced.
- Closed when: the owner console confirms the 50-width + horse-MP branch, the exact 5-width fallback,
  and the idempotent existing-template branch in-game.

### campaign-html-report — PARKED (2026-09-07)
- Owner request: an English graphical campaign overview, seven majors and time filters,
  deterministic extraction, maintainable generator in the repository, ignored cache.
- Delivered: `tools/campaign_report/`, six-tab HTML, JSON/CSV export code, content-addressed
  cache, branch checks, English measurement contracts. No gameplay changes in this subject.
- MEASURED (`tools/campaign_report/output/campaign.json`): 132 observations of `a100b67c`,
  1936.2–1947.1. HTML 8.35 MB; cached selection/extraction 21.79 s (before final writing).
- Validation: 17 standard tests pass, one optional parity test skipped in the standard run;
  three-date real-save parity passed separately. Six tabs and shared filters checked in-browser.
- State 2026-09-07 (parked; the digest ask below was done in the same session without an OPEN slot, WIP limit reached): generator delivered; semantic validation of daily armor output, net
  shortage and training/variant needs remains open. These values are null, not guessed.
  Direct file opening was blocked by browser policy; CSV download confirmation, JSON
  download and mobile layout still need browser validation. No OPEN slot consumed.
- Closed when: remaining metric contracts are verified or their explicit limits accepted,
  and direct offline opening plus CSV/JSON downloads are verified in a desktop browser.
- MEASURED 2026-09-07 rerun (owner ask: does it work on the cache): cold build 431.66 s,
  cache 0/132 because the dependency digest covers `common/units` and 15 tank-gun commits
  landed after the first cache (by design); warm rebuild 6.57 s, cache 132/132, HTML 8.4 MB.
  31 unit tests pass (1 optional skipped). Six tabs, quick ranges and end-date filter checked
  over `http://localhost` (`.claude/launch.json` `campaign-report`, `python -m http.server`);
  `file://` still blocked in the in-app browser, CSV/JSON clicks raise no error but the
  sandbox shows no download - desktop-browser check still owed.
- 2026-09-07 owner ask: an `only` button on every row of the country filter (hover-revealed,
  keeps the panel open, selects that single tag). `web/app.js` `renderCountries` +
  `web/style.css` `.only-tag`; HTML re-rendered from the cached JSON via `render`.
- Verification: commands, evidence and limitations in
  `documentation/CAMPAIGN_HTML_REPORT_PROPOSAL.md` and `tools/campaign_report/README.md`.
- Owner ask 2026-09-07: make the report consultable by the savegame-analysis skill so an agent
  gets the high-level view cheaply. Delivered as `tools/campaign_report/digest.py` — `build` now
  also writes `campaign_digest.md` (MEASURED 428 lines / 30 KB for 132 saves x 7 majors; cache
  still 132/132 after the change, `digest.py` excluded from the key) and a `digest` subcommand
  re-cuts it from the JSON (`--tags`, `--every`). `wa-savegame-analysis` gained a "Start from the
  campaign digest" section, `wa-campaign-checklist` step 1 points to it. The HTML stays the
  human view (served via `.claude/launch.json` `campaign-report`).
- Owner report 2026-09-07 (screenshot): the Resource dropdown listed non-resources (delivered,
  destination, efficiency, fuel_*, lended_cic, origin, request, required_cic). MEASURED cause
  `extract.py`: the ledger keys were the union of EVERY depth-1 block of the save's `resources`
  section, while `savegame.py` reads only the five ledger blocks. Fixed to the ledger blocks +
  `to_use`; regression test `test_resource_rows_come_only_from_ledger_blocks`; extractor change =
  cache key change, full re-extraction: MEASURED 146.53 s with `--workers 4` (vs 431.66 s on the
  default 2), dropdown then lists exactly the nine `common/resources` entries, HTML 7.8 MB.
- Owner report 2026-09-07: changing the Resource select at the bottom of Industry reset the view
  to the top. Cause `web/app.js` `render()` empties and rebuilds the whole tab, so the browser
  clamps the scroll. Fix: `render()` restores `scrollY` when the tab is unchanged (covers scope,
  armor filter and heatmap cells too) and scrolls to top on a tab change; MEASURED in-browser
  2290 -> 2290 on select, -> 0 on tab switch.
- Owner report 2026-09-07 (USA 1942.9, no positive resource): the Resources heatmap showed the
  `to_use[2]` unmet-demand column, <= 0 by construction. Data MEASURED correct (`savegame.py
  resources USA 1942.9_Sep.hoi4` = JSON: aluminium net 684 / deficit -680 / effective +4, coal
  effective +5700). Fix `web/app.js`: heatmap and Overview pressure table now show the EFFECTIVE
  balance (net + deficit, what `resource@X` reads), signed, negative = shortage; headings say so.
- Owner report 2026-09-07 (Armor tab, empty charts): `Training requirement` and `Daily production`
  were always empty because `training_need` / `production_per_day` are null for every family
  (`extract.py:338-360`); `armor_production.py` and `armor_training.py` exist with tests but are
  NOT imported by the extractor. Removed the two charts and the always-empty `Units/day` column
  from `web/app.js`; the armor notice now names the three uncomputed metrics. Wiring the two
  modules in is criterion (c) - an owner decision, not done here.
- Owner report 2026-09-07 (SOV medium tank destroyers: 360 in stock, 0 factories, deployed
  spiking 2/0/1/2/0): data MEASURED correct - `stock.py SOV 1945.12_Dec.hoi4 --foreign` holds
  238 `tank_ger_medium_chassis_td_3_3` built by GER (Germany collapsed 1945.11; stock jumps 5 ->
  312 that month), the family is 100 % captured/received and the deployed spikes are 1-2
  vehicles in one division. Presentation fix in `web/app.js`: a notice names the foreign-built
  share of the selected family when it is >= 50 %, and small integer counts get integer
  gridlines (the 2.2 tick read as fake data).
- Owner question 2026-09-07 (variant names vs raw keys): MEASURED in `1947.1_Jan.hoi4` the
  equipment registry names only DESIGNED variants (`name="M36 Jackson"`, `version=1`,
  `parent_id`); the base chassis entry of the same key has no `name` (`obsolete=yes`) and the
  game shows its localised key. `extract.py:419` fell back to the key. Fix in `render.py`:
  `equipment_names()` reads `localisation/replace/*_l_english.yml` for the definitions present
  (presentation metadata in `english_report`, no cache impact); `web/app.js` `variantName()`
  uses it, raw key kept beneath. Test `test_equipment_names_resolve_bare_registry_keys`.
- Owner ask 2026-09-07: sortable columns on every data table. `web/app.js` `makeSortable(table)`
  wired into `tablePanel` (page panels), `showTable` (chart Data dialog) and the sources table:
  click = ascending, again = descending, third = original order; numeric when the primary cell
  text parses (thousands separators, signs), alphabetical otherwise, missing values last; the
  key is the cell's first non-`<small>` child so a snapshot delta or a raw variant key does not
  pollute it; rows are moved not rebuilt (heatmap cell handlers survive). MEASURED in-browser on
  Overview snapshot, Armor variants, Wars table and a Data dialog.
- Owner ask 2026-09-07, three features. (1) Convoy war: MEASURED in `1942.9_Sep.hoi4` USA the
  country `convoys={equipment=...}` pool (2209), telemetry `wa_tlm_nav_convoys` (1841),
  `convoys_destroyed` (9) and the top-level `sunk_convoys_history` ledger (301 records, 24-month
  window, per month/killer/owner); `country_reports/equipment_production` REJECTED as a
  production counter (armor frozen at 73 over four saves while USA built tanks). Shipped: metrics
  convoys_pool/free/in_use/convoy_kills, snapshot `convoy_losses` + `convoy_window`, Wars tab
  section (lost-last-month chart, kills, pool, losses-by-attacker and kills-by-victim share
  tables over the selected period, latest covering save wins per month), digest section.
  (2) Economy fatigue: MEASURED `variables/economic_fatigue` (USA 14 at 1942.9); metric +
  Country status chart + digest column. (3) Factory/dockyard output, consumer goods, efficiency
  growth/cap: NOT in the save - only the WA dynamic-modifier inputs are serialised
  (`dynamic_modifier` list, `usa_kaiser_dockyard_output=0.25`...), the engine total is not;
  needs a WA_TLM probe writing `modifier:<name>` monthly (owner decision, separate subject).
  Extractor change = full re-extraction (MEASURED 137.8 s, 4 workers). Two follow-ups in the same
  session: `convoys_in_use` is unknown when the telemetry exceeds the pool (GER 1947: pool 0,
  frozen telemetry 2582 read as -2582), and `web/app.js` builds its catalog from the UNION of its
  hard-coded keys and the JSON catalog (new metrics rendered as raw ids before).
- Owner batch 2026-09-07 (seven items): legend clicks toggle series (hidden set keyed by chart
  title + series, the axis rescales on the visible lines, last line cannot be hidden); text
  columns of the convoy share tables left-aligned (`tablePanel` `left` option); `convoys_free`
  unknown when above the pool (GER 1945.12+: pool 0, telemetry frozen 2582 - no negative
  convoys nor negative use); everything English at the source (METRICS, warnings, CLI, errors)
  and the render-time translation layer deleted (`presentation()` replaces `english_report`);
  `Negative stock balances` chart replaced by per-country `Stock versus recorded demand`
  panels with shortfall = max(0, requests - stock) DERIVED (digest armor lines say the same);
  helpers `section()` / `countryPanels()` / `armorMeta()` dedupe the tab code. No LLM anywhere:
  stdlib Python + static HTML/JS, no network import (grep). Catalog change = re-extraction.
- Owner question 2026-09-07 (gaps in `Factories assigned to armor`): MEASURED `1943.10_Oct.hoi4`
  USA, 2 of 36 `military_lines` carry no `active_factories=` (queued lines: `queued_factories=26
  requested_factories=26`, engine omits the field at default 0); the extractor read them as
  unknown, which nulled the family sum and cut the curve. Fixed to 0 in the aggregate (raw line
  kept as recorded); regression test added; re-extraction.
- Owner batch 2026-09-07 (four items): cumulative convoy losses derived at build time in
  `convoys.py` (stitched ledger, unknown past the first uncovered month; excluded from the
  cache key, MEASURED cache 132/132) with a last-month/cumulative toggle in the Wars tab;
  remaining factory-chart gaps NOT reproducible - MEASURED 0 null family counts for the 7
  majors and 1 SVG segment per curve in-browser, the screenshot was the stale cached page;
  `Factories requested versus assigned` per-country panel (MEASURED `requested_factories` vs
  `active_factories`, 1308 of 4056 lines differ) - bombing/sabotage attribution impossible,
  the save carries no per-building damage (scan of `states` in 1944.7: only named flags);
  `Import JSON data` button: `boot(text)` is re-entrant, the file replaces the embedded data
  for the session, schema/snapshots/campaign id validated, nothing uploaded.
- Owner batch 2026-09-07 (three items). Theme: `theme_assets.py` turns
  `gfx/loadingscreens/mainmenu_bg.dds` (1960x1440 DXT, MEASURED) into `web/theme_bg.jpg` (136 kB)
  embedded behind the sidebar; aged-paper page, brass accents, serif headings; tokens keep their
  names so no rule changed. Factories: MEASURED `military_lines` carries `damaged_factories`
  (GER 1944.7: 3 of 32 lines) - third curve added, extractor reads queued + damaged fields
  (re-extraction). Dedupe assessment: `extract.py` (534 lines) already imports 11 readers from
  the skill scripts and re-implements a block lexer, the equipment registry (also in `stock.py`),
  the convoy ledger (also `convoywar.py`) and the division/units walk (also `savegame.py army`);
  the skill scripts (6.1k lines, 12 files) each carry their own streaming parser. A shared
  `hoi4save` library is the right target but is a cross-cutting refactor of calibrated analysis
  tools = owner decision, not done here (see the session summary for the phased plan).
- Owner report 2026-09-07 (manpower never falls): MEASURED `manpower.ratio` is the only shallow
  manpower scalar (losses.py ASSUMED free pool) and it DOES fall, rarely - GER 2 decreases /
  132 saves (1937.2-3), ENG 2 (1940.5-6, 400000 -> 350000), FRA 5 (1940.8-10), SOV 23, JAP/ITA
  0 - consistent with the AI raising the law before the pool empties. Shipped: conscription law
  per save (`politics/ideas` x `mobilization_laws` ladder from `common/ideas`, now in the cache
  key), `conscription_rank` metric, Country status panel + law-change table, digest `law`
  column, honest manpower note. In-game comparison of `ratio` still owed (owner). Theme
  (owner dislike, colours distorted): fully reverted, `theme_assets.py` and the JPEG deleted.
- Owner correction 2026-09-07: my 'pool that rarely dips' reading was WRONG (GER flat/rising
  1943-45 under the top law while casualties 3.2M -> 9.5M). Owner: `manpower.ratio` = mobilised
  share of the population. MEASURED confirmation: state `manpower_pool={available locked total}`,
  Ruhr 1943.6 (total-locked)/total = 14.8 % = GER ratio 1481500/1e7. Shipped: `mobilised_share`
  (%), `population`, `manpower_recruitable`, `manpower_free` summed over controlled states'
  pools (the free pool the first question was about), law-rank chart removed (ids, not
  numbers), law kept as a change table + digest line. Re-extraction.
- Owner 2026-09-07: direct double-click opening of `campaign.html` CONFIRMED in a desktop
  browser (criterion (b) half done; CSV/JSON downloads still unconfirmed). Layout: one
  `Mobilisation` section with the mobilised share and the available pool side by side, population
  chart and per-country recruitable panels removed, `manpower_recruitable` metric deleted.
- Closed when: (a) an analysis session uses the digest first and records in WORK.md that it
  chose the right saves/countries from it; (b) CSV/JSON downloads confirmed in a desktop
  browser; (c) the null armor metrics are either verified or their limits accepted.
- Verification: `python -m unittest tools.campaign_report.test_digest`; `python -m
  tools.campaign_report build --campaign a100b67c` prints `cache : 132/132` and a `DIGEST :`
  line; the digest's trend table for GER shows `—` divisions from 1946.01 with the
  "No deployed-division record" line, never a 0.

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

### rail-sizing-demand — PARKED (2026-09-04)
- Parked heading only for the WIP limit (4 OPEN). Real state: **TESTED 2026-09-04** — console
  harness run by the owner (below) PASSED; campaign probe (2) still owed.
- Console harness, owner run 2026-09-04 (`barb_supply test.hoi4` resumed, GER, pass of
  1943.5.10, build `526acd975`): `RAILWAY SIZE:` on all 9 accepted hubs — Pskov `states=4
  presence=51 demand=63.75 target=5`, Nevel 5/54/67.5/5, Rostov 5/35/43.75/5, Kursk
  7/92/115/5, Kharkov 4/48/60/5, Orel 6/115/143.75/5, Bryansk 6/110/137.5/5, N. Donetsk
  6/64/80/5, Smolensk 6/57/71.25/5 — **PASS** (Smolensk/Bryansk/Nevel were `target=2` on the
  1943.7.19 pass). Every route reads the cap 5: the known-false control (`states` ≥ 2 with
  `target=2`) did not occur on this front — no thin sector exists here; it stays owed on a
  campaign save with a quiet front. Cost: 10 routes sized, no visible pulse stall.
- Intended behaviour: a land-war railway route is sized for the divisions its frontline hub
  actually feeds, so a hub carrying 35-66 supply of demand is not fed by a level-2 chain.
- Symptom, MEASURED (owner screenshot, supply map 1943.10.13, same GER campaign as
  `barb_supply test.hoi4`): centre-front hubs at 20/28 of capacity (rail level 2/3) against
  29-66 of demand — 29/28 Smolensk, 35/20, 59/28, 66/20, 56/28, 34/28, 21/20. MEASURED (owner
  console log, pass 1943.7.19): those hubs' routes sized at `target=2` (Smolensk, Bryansk, Nevel,
  Pskov, N. Donetsk), Kursk 3, Kharkov/Rostov 4, Orel 5.
- Cause, MEASURED (`WA_AI_PC_railway_land_size_this_route`, `railway_strategies.txt`): the
  demand count `_rsize_prov_` held ONE province — the hub's — so `WA_AI_PC_rail_size_route`
  counted divisions in the hub's state only; the presence ladder (≤ 10 div → 2, 16-20 → 3,
  21-30 → 4, > 30 → 5 after × 2.5 × ratio) then read "≤ 10 divisions" for a hub whose area held
  ~26. Second term, MEASURED: `corridor.target_ratio = 0.4` sizes every route to the
  no-attrition floor by design (LOGISTICS_MODEL §11.4), i.e. 40 % of the estimated need — a
  correctly counted 26-division hub still came out at level 3 (28) against 65 of need.
  ASSUMED (engine): a supply hub feeds an area spanning several states; it is the only reading
  that puts 66 of demand on a hub whose own state holds ≤ 10 divisions.
- Owner rulings 2026-09-04: (1) "oui, il faut compter les états voisins"; (2) "passe le ratio à
  0.5. on augmentera si les changements du 1) n'augmentent pas assez la demande".
- Change (one commit, `# [rail-sizing-demand]`): `WA_AI_PC_railway_land_size_this_route` adds,
  to the hub province, one province of every NEIGHBOURING state that borders the enemy being
  processed (`every_neighbor_state` + the candidate trigger's own enemy test on
  `_current_enemy_tag`); `_rsize_ours_` padded with 0 so the arrays stay aligned (the SUM
  injection mode is not used by this family). New log `RAILWAY SIZE: hub P states=N
  presence=X demand=D target=T`. `constant:wa_ai_railway.corridor.target_ratio` 0.4 → 0.5.
- Impact analysis. Callers of the binding: the three sites inside
  `WA_AI_PC_railway_land_consider_frontline` (land-war family only, all inside the per-enemy
  loop, so `_current_enemy_tag` is always set). The ratio is SHARED with the corridor family
  (`WA_AI_PC_rail_size_route` reads it for both): North Africa corridor targets rise by the same
  25 % under its own floor 2 / cap 4 — accepted, one demand model. Reach: every AI belligerent
  with a land front, historical and ahistorical (no tag, no date). Cost: `every_country` ×
  (1 + neighbours ≈ 3-6) `divisions_in_state` tests per route, ≤ 16 routes per 8-week pass.
  Regression risk, STATED: (i) routes to a hub whose neighbours hold a large parked reserve
  (not at the front) now size higher — bounded by the cap 5 only (the "borders the enemy"
  filter passes every enemy-controlled neighbour too, by design: spearhead divisions inside a
  partly occupied enemy state draw on this hub); (ii) rails never downgrade, so a front that
  later empties keeps its level — accepted by the cap ruling; (iii) two adjacent hubs count
  each other's neighbour states, so a dense front sizes both routes at the same (higher)
  target — intended: the trunk is shared; (iv) a neighbour across a strait touching the same
  enemy adds one state's presence to a route that does not feed it — upward, one state, accepted
  (lessons review). The presence index over-reads a dispersed army (sizer header, LOGISTICS_MODEL
  §11.11) and the widening multiplies the bucket floors paid at the same moment the ratio rises:
  MEASURE the over-reach tell-tale below before the 0.7 / 1.0 ratio step. Not done (optional,
  editing rule 3): extracting the enemy-adjacency test shared by the candidate trigger and the
  sizer into one scripted trigger. DERIVED on the 1943.10 map: Smolensk/Bryansk/Nevel routes go from 2 to
  4-5, and the July pass's 12 slots (now weakest-link first, `rail-admission-churn`) fill
  with their level-2/3 hops.
- Verification, owed to the owner: (1) console — resume `barb_supply test.hoi4` (or the
  1943.10 save) with `WA_AI_construction_logging` on GER, advance to the pass; expect
  `RAILWAY SIZE:` lines with `states=` ≥ 2 for every hub that has a neighbour on the front,
  and `target=` ≥ 3 for Smolensk/Bryansk/Nevel (were 2); known-false control: a hub with
  `states=` ≥ 2 whose neighbours hold few divisions keeps `target=2` (the widening must not
  inflate a thin front) — a frontline with a single enemy neighbour is the only `states=1` case
  and is not the control. (2) campaign
  probe (save-visible, no new TLM): `rail.py 6521 <hub>` on consecutive saves — the narrowest
  link of the Smolensk/Bryansk routes rises above 2 within two passes of the front settling;
  `control owner:SOV --buildings` GER rail_way total rising faster than before this commit.
  Tell-tale of over-reach: level-5 edges appearing on routes whose hub state and neighbours
  hold < 20 divisions in `plans.py --where`.
- Campaign `916b90f6` (same run as above; build ASSUMED to carry this commit). Probe (2)
  **FAIL on the front reading**, MEASURED (`rail.py 6521 <hub>` on 1941.12 / 1942.6 / 1942.12 /
  1943.6 / 1943.12 / 1944.6, 10 hubs): the narrowest link of EVERY Berlin→hub route is **3 on all
  60 cells** — never rose in 30 months. Where the rail went (MEASURED `--path`): the shared trunk
  west of the 1939 border — Ostmark/Poznan `444-3532-6558` 3 → 4, E. Mazowieckie → Lublin 3 → 5;
  east of Wilno (`3320 = 3 = 6340`) and Polesie (`560 = 3 = 6579`) every hop is 3 in 1941.12 and
  still 3 in 1944.6. Volume was not the issue: `pc_built_by_type^13` +303 over the war, rail
  share of PC completions 60 % → 78 %; 1943.6 queue = 12 `rail` projects (Kharkov, Vitebsk ×3,
  Nevel ×2 + 6 partial-path routes at band 700 toward Katowice/Těšínsko/Slovakia, 4 of them
  never funded). Front context (MEASURED `control owner:SOV`): Axis high-water 1942.12 at 16 %
  of Soviet provinces, Moscow never taken, occupation handed to RUK/RBL by 1943.6 (GER rail on
  Soviet soil 464 → 211 is the hand-over, Axis total 669 → 672), Pskov/Nevel/Kharkov hubs lost
  by 1944.6, Soviet reconquest complete 1945.6, SOV inside Germany 1945.12. DERIVED cause: the
  route min is 3 over ~40 hops per route; each pass admits 12 and the fill funds 4-8, so raising a
  route's min by one level needs every level-3 hop of it (~4 passes admitted, ~a year funded)
  before any hub reads 36 — and the level-3 sweep offers same-level hops capital-first, so the
  shared trunk absorbed the budget while the front hubs changed hands. Half the 1943.6 admission
  went to dead-end (partial-path) routes. The sizing fix made the target right; it cannot make
  the rail arrive. Levers for the owner (none taken): funding share for rail (`alloc.fraction` /
  override life), `max_civs_per_project` 20, partial-path routes barred from admission while a
  full route's hops are refused, front-first order within a level (the reverse of what
  irreversibility argues — a rear hop survives a retreat, a front hop is lost with the ground).
- Closed when: (1) pasted here and passing, then (2) on one campaign; ratio step to 0.7/1.0 is a
  separate owner decision recorded here when taken.

### rail-spine-tree — PARKED (2026-09-05)
- **Build spec: `documentation/WA_AI_RAILWAY_SPINE_SPEC.md`** (final, owner-ordered
  2026-09-05 "écris la spec finale"; this entry keeps the state and the evidence).
- Parked heading only for the WIP limit (4 OPEN). Real state: **SHIPPED-UNTESTED 2026-09-05** —
  design agreed with the owner 2026-09-05, code committed the same day, console harness
  (Verification (1) below) NOT yet run by the owner. Owner-admitted; supersedes the trunk/branch reading of
  `rail-sizing-demand` and `rail-admission-churn` (both stay as shipped: sizing and
  weakest-link admission are reused unchanged for the branches).
- Intended behaviour: a land power at war with an enemy worth it builds ONE railway trunk from
  its capital to a railhead placed at the centre of that front, then short branches from the
  trunk to every frontline hub; the trunk is unique (no parallel north/south spines), it is
  started before the war when the target is known, it outranks the theatre corridors, and the
  hop raised next is always the one that unblocks the most hubs.
- Symptom, MEASURED (campaign `916b90f6`, `rail.py` on 6 saves 1941.12-1944.6, 10 hubs): the
  narrowest link of every Berlin→hub route is 3 on 60/60 cells; the German rail went to the
  shared trunk west of the 1939 border (Ostmark/Poznan 3→4, Mazowieckie→Lublin 3→5), nothing
  east of Wilno/Polesie. MEASURED (owner console logs 1943.5 / 1943.6 / 1943.7): the trunk
  flips between two lines depending on which route is pathfound first in the pass — north
  Poznan→Warsaw→Białystok→Grodno→Vilnius (May, June) vs south Ostmark→Lublin→Lwów→Polesie
  (July, with Pskov detoured through Minsk→Vitebsk) — because the pathfinder's ×0.5 for
  "designated network" provinces is a temp of the current pass only
  (`WA_AI_pathfinding_effects.txt:726,769`; cost per hop = 1/(level+1)). MEASURED (`pc GER
  1943.6`): 6 of 12 admitted rail projects were a dead-end stub Katowice→Southern Slovakia at
  band 700 (partial-path factor), 4 never funded — the fallback of a search toward a far
  south-eastern hub (Crimea/Odessa, RUK/ROM-held) that exhausted `_pf_max_its = 100`; the
  partial-path fallback picks the closed node with the HIGHEST cumulative cost
  (`pathfinding_effects.txt:543-552`, comment says "most progress" and is wrong), not the one
  nearest the target. MEASURED (`barb_supply test.hoi4` 1943.5): 80 of 80 rail civs on the
  North Africa corridor while the east had 0 `rail` projects — corridor and land-war share
  band 1000.
- Engine reading, owner ruling 2026-09-05: a hub's supply = the MINIMUM level along its rail
  path (case 1). A single level-5 trunk plus branches suffices. ASSUMED (engine): shared
  capacity on a trunk segment is NOT the binding model; if a trunk tooltip ever reads
  used = capacity, add a second parallel trunk (the R2 rule below already allows it).
- Owner rulings 2026-09-05: (a) railhead = centre of the front by summed distance, 20 %
  hysteresis; (b) trunk only against an enemy worth it: ≥ 4 frontline hubs AND
  (`is_major` or ≥ 40 divisions) — Denmark gets no trunk (owner 2026-09-05: "monte la porte à
  4 hubs de front"; counted on the frontline CANDIDATES that pass the limit check, before the
  `routes.max_per_enemy = 4` route cap — counted after it, "≥ 4" would only ever mean "cap
  reached"); (c) one railhead by default, a second
  only when connecting the far hubs to a new railhead costs less than connecting them to the
  existing spine; routes are computed from the FRONT toward the nearest element of the trunk,
  the trunk being the level-5 network connected to the capital (Paris–Berlin–Minsk at 5 is one
  trunk for GER); trunk hops are raised by the number of hubs they unblock, not level by level
  ("hub served" criterion, 2026-09-05).
- Algorithm, per enemy, per land-war pass (8 weeks at war; also in PEACE toward the
  CONFIG-declared target, e.g. `WA_AI_CONFIG_RAILWAY_GER_to_SOV_window`, so the trunk exists
  on day 1 — lever 1, the only one that adds time instead of factories):
  0. Gate: enemy passes (b); else the current per-route behaviour (routes from the capital,
     floor target) — minors keep today's code path.
  1. Trunk set T = provinces reachable from the capital over rail edges of level ≥
     `spine.trunk_level` (5), walked on the WA cache `WA_AI_PC_railway_connection_level_*`
     with the generated adjacency, bounded (`spine.max_walk` provinces). T empty → {capital}.
  2. Railhead R1: candidates = states with a supply hub held by ROOT / subject / dependent ally,
     NOT frontline; score = Σ over this enemy's accepted hubs of dist(hub, R) +
     `spine.capital_weight` × dist(capital, R) − bonus if R ∈ T; keep the previous R1 (per-enemy
     country variable) unless a candidate beats it by `spine.hysteresis` (0.2). In peace the hub
     set = the border states of the CONFIG target.
  3. Trunk route: R1 → nearest element of T (straight-line pick, then A*); target
     `land_war.rail_level_cap_overland` (5); band `prio.rail_connect` (1100) — lever 2, the
     trunk outranks the corridors at 1000. R1 ∈ T → no trunk route. S = T ∪ trunk route.
  4. Second railhead (ruling c): group B = hubs closer to an alternative centre than to R1;
     R2 = centre of B; kept iff dist(R2, S) + Σ_B dist(h, R2) < Σ_B dist(h, S); at most
     `spine.max_second_railheads` (1). Its trunk route R2 → nearest element of S, same band.
  5. Branches: every accepted hub → nearest element of S (∪ R2 route): straight-line pick,
     then A* — 10-20 hops instead of 50-65, so `_pf_max_its = 100` no longer bites; target =
     the hub's demand (`rail-sizing-demand`, unchanged).
  6. Admission, one budget (`routes.queue_full`): (i) trunk hops by VALUE = number of
     branches attached downstream of the hop whose effective minimum
     min(trunk prefix min, branch min) equals this hop's level — i.e. the hop is what caps
     them — descending, ties by level ascending then capital-first; (ii) then branch hops by
     the existing level sweep (weakest links first); (iii) partial paths are NOT admitted for
     the land family (lever 3; the fallback keeps its coastal-beachhead use, with its
     frontier fixed to the closed node of LOWEST heuristic, nearest the target). Phase A
     (below the floor) stays first for both families.
  Worked example the criterion must reproduce (design wording; the SHIPPED rule adds "and the
  branch's own minimum lies strictly above the hop" — see the "Value rule, DEVIATION" bullet below
  for why the plain count does not reproduce it): trunk Berlin→Minsk 30 hops at 3, branch
  Warsaw→Pskov already at 5 attached at hop 10: value of hops 1-10 = every branch (all
  prefixes share them) and Pskov's min is capped by them → raised to 5 before any hop 11-30
  goes 3→4; Pskov reads 44 after 20 hops of work, not after 60.
- Constants (new group `wa_ai_railway.spine`, all read in one file each): `trunk_level = 5`,
  `hysteresis = 0.2`, `capital_weight = 0.25`, `min_hubs = 4`, `min_enemy_divisions = 40`,
  `max_second_railheads = 1`, `max_walk = 400`. The divisions gate is the one number without
  a measurement behind it — tune after the first campaign.
- Files: `railway_strategies.txt` (route_start per hub = nearest S element; trunk route;
  railhead selection effect `WA_AI_PC_railway_spine_select`, per-enemy railhead memory
  `WA_AI_PC_spine_railhead@<enemy>`); `railway_core.txt` (phase 0 tags `_lseg_trunk_`, the
  value computation and the trunk-first admission; partial routes skipped for the land
  family); a bounded trunk-walk helper in `railway_helpers.txt`; pathfinder fallback frontier
  fix in `WA_AI_pathfinding_effects.txt` (shared with the corridor's coastal use — impact
  analysis owed there); constants file. Log lines: `RAILWAY SPINE: enemy=T T=n R1=p R2=p
  trunk_hops=k`, `RAILWAY TRUNK: hop a->b level=L value=v`.
- Explicitly NOT in scope, owner-excluded: rail cost, civs per project, PC fraction. The
  trunk does not build faster than 79 civs × 5 IC/week allow (≈ 0.5 segment-level/week,
  DERIVED from `PC_ASSIGN` 1943.5); splitting the trunk into sections changes only the
  order, not the duration — hops are already one project each, and the shared prefix first is
  what serves the most hubs soonest. The one legitimate accelerator is the ledger's own speed
  error — see `pc-build-speed` (companion subject, owner-admitted 2026-09-05): the engine
  builds the same 20-civ project 2.6× faster than the ledger charges it.
- Change (shipped 2026-09-05, one commit, `# [rail-spine-tree]` at every site; system doc
  `WA_AI_RAILWAY_SYSTEM.md` "Railway spine" section):
  - `common/script_constants/wa_ai_railway.txt` group `spine` exactly as spec §9 (`trunk_level` 5,
    `max_walk` 400, `hysteresis` 0.2, `capital_weight` 0.25, `in_trunk_bonus` 1.0 = one MEAN
    hub-distance unit, relative, `min_hubs` 4, `min_enemy_divisions` 40, `max_second_railheads` 1),
    each key read in one file.
  - `WA_AI_CONSTRUCTION_triggers.txt`: `WA_AI_PC_railway_land_frontline_candidate` = the route
    budget term + new `WA_AI_PC_railway_state_is_frontline_hub` (the count the gate uses, BEFORE the
    budget); new `WA_AI_PC_railway_state_is_railhead_candidate` (hub state not bordering the enemy);
    new `WA_AI_PC_railway_state_is_served_frontline_hub` (a frontline hub state already at the done
    level: no route, but counted in the trunk values — review repair).
  - `railway_helpers.txt`: `WA_AI_PC_railway_spine_walk` (bounded BFS from the capital over
    `global.WA_AI_PC_railway_connection_level_a^b` ≥ trunk_level → `spine_T_`, once per pass),
    `WA_AI_PC_railway_spine_nearest`; the enemy-threat sort and `WA_AI_PC_clear_project_inputs`
    carry the new parallel route array `railway_route_kind_` (0 land plain route, 1 trunk, 2
    overseas beachhead, 3 land branch started on the spine); the sort's ×1.1 top-threat boost skips a
    trunk first route (it would go above the legacy clamp — review repair).
  - `railway_strategies.txt`: the per-enemy gate in `STRATEGY_land_war` (THIS = enemy: hubs ≥
    min_hubs AND `is_major` or `num_divisions` ≥ min_enemy_divisions); `WA_AI_PC_railway_spine_select`
    (ROOT scope: railhead candidates on the capital's landmass over the three populations, score =
    Σ hub dist + capital_weight × capital dist − in_trunk_bonus × mean hub dist if in T, hysteresis
    against `WA_AI_PC_spine_railhead@var:_current_enemy_tag`, trunk route pathfound at strategy time
    with NO partial and appended FIRST for its enemy at target `rail_level_cap_overland` and band
    `_spine_band_` (1100 at war / 500 in peace), its provinces marked as designated network and added
    to `spine_S_`; optional R2 by the two-centre split (seed = hub farthest from R1, one centroid
    iteration) and the keep test dist(R2,S) + Σ_B dist(h,R2) < Σ_B dist(h,S)); branches:
    `WA_AI_PC_railway_land_consider_frontline` and the two prewar same-landmass sites start at the
    nearest element of S when `spine_active_`; peace mode for the CONFIG-declared targets
    (`_spine_peace_targets_`, filled beside `_scripted_override_targets_`) at band `rail_prewar`,
    gate = the window; every route add site pushes its kind; the six land-family validation
    pathfinds run with `_pathfind_prov_allow_partial = 0`. Logs `RAILWAY SPINE: enemy=E cand=N T=n
    R1=p R2=p|0 trunk_hops=k` and `… BELOW GATE - direct routes`.
  - `railway_core.txt`: phase 0 collects `_lseg_kind_ / _route_ / _hop_` and allows partial paths
    for kind 2 only; a value block (`WA_AI_PC_railway_spine_attach` = the trunk segment whose far
    end is the branch's start; `WA_AI_PC_railway_spine_value_add` = the prefix walk of depth ≤ 2 for
    R2 on R1 and the vote, called for every branch drawn this pass with its own minimum AND for every
    SERVED hub — `spine_done_attach_`, attached at the spine element nearest it — with minimum = the
    level they read done at, `spine_done_min_`); admission = phase A (a trunk head hop never above `rail_connect`) →
    phase T (trunk hops by value desc, level asc, capital-first, priority clamped at `rail_connect`;
    log `RAILWAY TRUNK: hop a->b level=L value=v`) → phase B (branch hops by the existing level sweep);
    `RAILWAY ADMISSION: segments=N head=A trunk=T rest=B attach_miss=M` (M = spine branches, route
    kind 3, whose start is on no trunk segment collected this pass and not in T — phase 0 re-pathfound
    the trunk on another line; "value 0 by design" and "the trunk moved" are then distinguishable).
  - `WA_AI_pathfinding_effects.txt`: the partial-path frontier = the closed province with the LOWEST
    raw heuristic (nearest the target) instead of the highest cumulative cost; a DEEP iteration budget
    (`@WA_AI_PATHFIND_PROV_DEEP_ITS = 300`, file-scoped, single reader) switched on by equality on
    `_pathfind_prov_deep_ = 1` — never `> 0`, an unset temp reads as a scope token — for the trunk
    route's search only (the trunk effect sets it to 1 before and 0 after its call).
  - `tools/constants_registry.json`: group `engine_rail_max_level` ties `spine.trunk_level` to
    `land_war.rail_level_cap_overland` (both 5 = the engine maximum; apart, a finished trunk would
    never join T).
  - `WA_AI_misc_on_actions.txt` `on_peace`: `WA_AI_PC_spine_railhead@<country>` cleared for every
    country ROOT is no longer at war with EXCEPT the CONFIG-declared peace-mode targets
    (`WA_AI_PC_railway_get_scripted_override_targets`) — a peace with anyone else must not wipe the
    peace trunk's hysteresis (own effect block, not gated on the queue; `on_peace` documents no
    partner scope, MEASURED in the install's on_actions files, so the partner cannot be keyed on).
- Served hubs (review repair): a frontline hub state already at the done level fails the candidate
  test (`has_railway_level` at `_check_railway_level`, state-wide) and draws no branch — so the spec's
  "branch Warsaw→Pskov already at 5" is not a route. The trunk under it still caps it, so such hubs
  are collected per enemy (`WA_AI_PC_railway_state_is_served_frontline_hub`), attached at the spine
  element nearest them (DERIVED proxy for their real prefix; straight line, like the branches) and
  counted in the trunk values with the level they read done at as minimum. The worked example is reachable
  through this path: Pskov served at 5, attached at hop 10, gives hops 1-10 value 1 until they read 5.
- Value rule, DEVIATION from spec §5.6 (2) stated: the literal "branches whose effective minimum
  equals level(h)" flips the worked example at the second pass — with hops 1-10 at 4 and ≥ 2 far
  branches at 3 attached at hop 30, hops 11-30 (level 3 = the far branches' effective minimum) would
  outrank hops 1-10 (level 4, Pskov alone), and Pskov would read 44 after 40 hop-levels, not 20.
  Shipped: a branch counts for a hop only if the hop is its effective minimum AND the branch's own
  minimum is strictly above it — a branch whose own hops sit at the trunk's level is held back by
  itself and counts for nothing until phase B moves its hops. This reproduces the example's ordering
  exactly (pass 1 and 2: hops 1-10, value 1 = Pskov; pass 3: all values 0 → level ascending,
  capital-first → hops 11-30). "Mine covers it because": the owner's stated outcome is the example's
  ordering ("hops 1-10 raised 3→4→5 first"), and no static per-hop count reproduces both the example's
  pass-1 numbers ("value = all branches") and its pass-2 ordering; the ordering is the observable.
  Written next to the value computation as ordered.
- Impact analysis (AGENTS.md principle 3). Callers / readers, MEASURED by grep: the land-war gate
  runs for every relevant enemy ROOT directly borders (majors, > 50 factories, direct border); the
  peace mode only for `_scripted_override_targets_` (today `WA_AI_RAILWAY_should_override_GER_to_SOV`);
  `WA_AI_PC_railway_land_frontline_candidate` keeps its three readers (the three population loops)
  and its terms (budget + the new hub trigger = the old body); `railway_route_kind_` is pushed at all
  nine route add sites (consider_frontline 1, overseas A 2, overseas B 1 (kind 2), prewar 4, trunk 1)
  and carried by the sort; the partial-path fallback's remaining callers are phase 0 for kind-2 routes
  and the debug mirrors in `zz_debug_effects.txt` (a partial there now ends nearer the target — debug
  only); the corridor family (`WA_AI_PC_railway_corridor_run_one`) is untouched and already ran without
  partial. Reach: every AI belligerent with a land front, historical and ahistorical alike (no tag,
  no date; the gate is hub count + major/divisions; the peace mode keys on the CONFIG window that
  already existed). Below the gate (Denmark, Luxembourg, an occupied Yugoslavia) nothing changes but
  the loss of partial routes. Regression risk, STATED: (i) phase T admits every trunk hop below its
  target BEFORE any branch hop at or above the floor, so while a 30-hop trunk is being raised the
  branches get only the slots the trunk leaves — the owner's ordering (spec §5.6), stated here as
  the t-table below; phase A (level-0/1 hops anywhere) still goes first; (ii) the trunk pathfind
  runs under the deep budget (300 iterations; the measured 50-65-hop searches exhausted the default
  100; a 30-hop trunk under 300 is ASSUMED to fit — MEASURED only when the harness prints a
  `RAILWAY SPINE … trunk_hops=k` with k > 0). Walk of the failure case, GER→SOV 1941.7: t0 T = {Berlin}
  (ASSUMED no level-5 edge at the capital), trunk search Berlin→railhead fails → `trunk pathfind
  FAILED`, S = T = {Berlin}, the branches start at Berlin as before but WITHOUT partial paths: hubs
  reachable within the default 100 iterations get full routes, the far ones get nothing (they got a
  70 %-band stub before, which connected nothing); t1 (+8 w) the same, since nothing moved — the
  tell-tale is `trunk pathfind FAILED` on every pass with `cand ≥ 4`, and the lever is
  `@WA_AI_PATHFIND_PROV_DEEP_ITS`; (iii) phase 0 re-pathfinds the trunk route like every route; its
  strategy-time path is marked as designated network so the re-pathfind sees the same costs, but a
  route of ANOTHER enemy pathfound earlier in phase 0 can shift it — a branch whose start is then
  off the trunk path attaches nowhere and is admitted as a plain branch for that pass (self-healing
  next pass: same inputs, same marks); (iv) the land family no longer draws partial routes, so a hub
  unreachable through friendly ground gets NO route instead of a stub — intended (the stub connected
  nothing) — and the same-landmass overseas fallback still fires on a direct FAIL (it tested
  `NOT = { _direct_success = 1 }`, unchanged); (v) the railhead scoring costs (candidates ×
  hubs) script sqrt distances per gated enemy per pass, the walk one meta_effect per rail edge over
  ≤ 400 provinces once per pass — about one extra A* per enemy, at the 8-week cadence; (vi)
  `_current_enemy_tag` is overwritten in peace mode for the CONFIG target — nothing in the prewar
  strategy read it before; (vii) the parallel-array contract: a route add without a kind push
  misaligns every later route's kind — the nine sites are listed above, the sort copies the kind.
- Bounded, t-table at the real cadence (8-week pass, `routes.queue_full` 12, `pc-build-speed` ledger:
  a 20-civ segment on German ground ≈ 1 week, on Soviet ground at infrastructure 2 ≈ 1.3 weeks, GER
  79 civs = 4 slots), a 1941-42 GER save with a 30-hop Berlin→railhead trunk at 3 and 9 branches at
  2-3: t0 (pass 1) phase A takes the level-0/1 hops first (none on this trunk), phase T admits 12
  trunk hops 3→4 in value order (the prefix shared by every branch first), phase B gets 0 slots;
  t0+3w all 12 done, the queue idles until t1; t1 (+8w) 12 more trunk hops 3→4; t2 (+16w) the last
  6 to 4, then 6 branch hops at 2 by the sweep; t3-t5 (+24..40w) the trunk 4→5 (30 hop-levels), the
  branches interleave only through phase A / the slots the trunk leaves; ≈ t5 the railhead reads 44
  and every branch is a 5-15-hop job at its own demand target. The binding constraint is the
  ADMISSION cadence (12 hop-levels per 8-week pass), not funding (12 × 800 IC at 4 × 130/day ≈ 3
  weeks) — an observation on `interval.war_weeks` / `routes.queue_full`, both owner-tunable and
  both out of this subject's scope (spec §9 "unchanged"). In peace (§6, GER 1938-41) the same 60
  hop-levels take 5 passes at the 12-week cadence ≈ 60 weeks — fits between 1938.6 and 1941.6 only
  if the CONFIG window opens by early 1940; today `WA_AI_CONFIG_RAILWAY_GER_to_SOV_window` opens
  1941.1.1 (MEASURED, `WA_AI_CONFIG.txt`), i.e. ≈ 2 peace passes ≈ 24 trunk hop-levels before
  Barbarossa — the window is the lever, an owner decision, not taken here.
- Review repairs (lessons reviewer CONCERNS, architecture reviewer CONFLICT then re-reviewed, same
  session): the on_peace purge excludes the CONFIG-declared peace targets (every peace GER signs
  before Barbarossa would otherwise wipe the SOV memory); spec §5.6 (2) and its worked example, and
  this entry's algorithm bullet, carry the shipped "own minimum strictly above" clause; the
  `attach_miss` counter (route kind 3 = spine branch) in `RAILWAY ADMISSION`; the trunk / corridor
  CONNECT / phase-A tie at 1100 stated in the core comment and the system doc (insertion decides,
  no new band); the ×1.1 top-threat boost of the sort no longer applies to a trunk first route and
  phase T clamps at `rail_connect` (1210 would have hit the legacy clamp and dropped to 1000 a week
  later); `spine.trunk_level` registered against `land_war.rail_level_cap_overland`; served hubs
  counted in the trunk values (the example's level-5 branch is not a route); the trunk pathfind's
  deep budget and the failure walk in (ii). Noted, not changed: the peace-mode trunk pushes an
  enemy tag while the four prewar direct-route sites do not (`railway_enemy_tags_` is read only by
  the land-war sort — dormant misalignment, pre-existing shape); phase T keeps offering hops after
  the budget is full, like phase B.
- Owner tuning, 2026-09-05, after the first harness pulse (1941.9.29) and the 1941.12.20 save reading
  (12 hops built per 8-week pass, rail queue idle 5 weeks in 8, 9.5 weeks of war before the first
  pass): (a) the rail override flag timer 30 → **21 days** (`railway_core`; the ENG air-hosting
  writer keeps 30, the shared contract is the VALUE 0.6); (b) `interval.war_weeks` 8 → **6**;
  (c) new `on_declare_war` block in `WA_AI_misc_on_actions.txt`: the railway interval counter of the
  declaring country and of its target is set to 0 when they are AI. DERIVED at 6 weeks: trunk
  Berlin→Nowogródek ≈ 30 weeks instead of 40, rail monopolises the PC pool ≈ 3 weeks in 6,
  override armed ≈ 21 days in 42. Tell-tale to watch on the next campaign:
  `wa_tlm_pc_avail_share_pct` well above 60 % = the override bites too much.
- Owner tuning (2), 2026-09-05, after the logged pass of 1943.4.12 (campaign 1941.10-1943.4, GER vs SOV;
  owner: "implémente L1, L2, L3"). MEASURED on that pass: `RAILWAY ADMISSION: segments=70 head=7 trunk=1
  rest=0`; 8 = `queue_full` 12 − 4 live trunk hops of the previous pass (`queued=1` + `SKIP DUPLICATE`);
  every later `PC START_PROJECT ENTRY` without `PC QUEUED` = the cap. `PC_ASSIGN after_alloc_fraction=73`
  and `PC SPEED speed=4.745` per civ-day: one 20-civ slot finishes an 800-cost segment in ~1.2 weeks,
  DERIVED ≈ 18 segments fundable per 6-week interval against 8 admitted — the cap bound, not the pool.
  `RAILWAY SPINE: cand=6 served=0 T=55 R1=6373 R2=525 trunk_hops=19`: trunk 572 Wołyń → Polesie → Mozyr
  → Bobruysk (12 hops at 2-4) + Mozyr → Kiev (7); DERIVED from the 1943.4.1 save + province coordinates:
  Wołyń was the T element nearest Bobruysk at 83 map units against Grodno 92 (Grodno in T at 5), so the
  trunk ran through the Pripyat marshes and the Minsk / Latgale branches hung off Polesie — the owner's
  "axe secondaire parallèle Kraków–Minsk". `value=0` on every trunk hop (branches at level 1 cap
  themselves — by design).
  - L1 `railway_core` / `railway_helpers` / `PRIORITY_core`: the family cap = max(`routes.queue_full`,
    `WA_AI_PC_alloc_pool` / `alloc.max_civs_per_project` × new `routes.rails_per_slot` 4), the pool
    published by `WA_AI_PC_assign_factories` on the same pulse (assign → progress → railway); a trunk
    reserve of `spine.trunk_share` 0.34 × free admissions (≤ trunk hops phase T can raise) held back from
    the branch heads, which return in a phase A' after phase T. Log adds `cap= free= reserve=`.
  - L2 `railway_strategies` `WA_AI_PC_railway_spine_trunk_route`: `spine.trunk_starts` 3 candidate starts
    (nearest S elements, `_spn_excl_` on `WA_AI_PC_railway_spine_nearest`), each deep-pathfound, kept =
    fewest levels to raise (Σ cap_overland − level on the ledger). Logs `trunk start k a -> R hops= raise=`
    and `… KEPT`.
  - L3 `spine.in_trunk_bonus` 1.0 → 0.25.
  DERIVED at the new numbers, GER 1943.4: cap 14.7 → free ≈ 10-11, reserve 3-4 trunk hops per pass
  instead of 1; a 12-hop trunk from 3 to 5 (24 hop-levels) ≈ 6-8 passes (36-48 weeks) instead of 24
  passes. Owner question answered the same day: `routes.max_per_enemy` 4 → 8 changes nothing for ROOT's
  own hubs — MEASURED 6 `ACCEPTED` under a cap of 4, because `every_controlled_state`'s limit is evaluated
  before the body increments `_routes_for_this_enemy` (ASSUMED engine list-then-execute); it only widens
  the subject / ally populations that run after. Not changed.
  Review repairs (architecture reviewer, CONCERNS): (i) regression risk stated — a cap above 12 keeps
  1000/1100-band rails at the queue head for weeks the pool used to fall through to the 250/100 bands
  (winner-takes-most); the tail is carried by the `[pc-queue]` aging lane, and the tell-tale is the one
  tuning (1) already names, `wa_tlm_pc_avail_share_pct` well above 60 %. t-table at the new cap, GER
  1943.4 (73-civ pool, 3-4 funded rails, ~1.2 weeks each): t0 pass admits ~11 (cap 14.7 − 4 live),
  t0+3 weeks ≈ 9-10 of them built and the pool falls through, t0+6 weeks next pass — rail holds the pool
  ≈ 3-4 weeks in 6 instead of ≈ 2. (ii) the reading rule "every `PC START_PROJECT ENTRY` without `PC
  QUEUED` = the cap" holds for phase A / T / B only: phase A' re-offers the heads phase A admitted, which
  log `ENTRY` + `SKIP DUPLICATE`. (iii) `_rail_queue_cap_` is read with `>` in `railway_helpers`; an
  unset temp would pass — every rail-family caller runs inside `WA_AI_PC_railway` after it is set, and
  the HAZARD sentence at the read site binds any future caller.
  Review repairs (lessons reviewer, CONCERNS — one CONFLICT with the "create the thing outranks improve
  the thing" band lesson): the reserve as first written let phase T fill the queue while below-floor
  branch heads waited, so a hub with NO supply could lose a whole interval to trunk level-raises. Shipped
  shape: phase T is an effect (`WA_AI_PC_railway_spine_phase_T`, `_pt_limit_`) called twice — T takes at
  most the reserve while heads are pending, A' admits the waiting heads, T' takes the rest — so a head
  loses at most the reserve to the trunk in one pass, never the pass. t-table (6-week pass, ~1.2 weeks per
  20-civ segment, admissions counted as `queued_amount_ < cap` = up to the next integer):
  | case | cap | live | free | reserve | heads offered | A | T | A' | T' |
  | GER 1943.4, 73-civ pool | 14.7 | 4 | 10.7 | 3.6 | 7 | 7 | 4 | 0 | 0 (cap) |
  | same, 12 heads pending | 14.7 | 4 | 10.7 | 3.6 | 12 | 8 | 3 | 0 (cap) | 0 |
  | pool < 60 civs (cap = 12) | 12 | 4 | 8 | 2.7 | 8 | 6 | 2 | 0 (cap) | 0 |
  DERIVED: a minor at the floor cap loses 2 heads per pass to the trunk (they return next pass, the
  trunk hops built meanwhile are what those heads will draw supply through). ASSUMED acceptable —
  owner's call; revert = `spine.trunk_share = 0`, which restores today's order exactly. Two-states note:
  `free` is computed on the controller-filtered live count while the cap counts every queued type-13
  (dead included) — after a mass flip free overstates the room and the reserve can eat the real room
  for one pass; the validation sweep clears the dead ones on the same pass, so bounded to that pass.
  L3 release reachability, DERIVED on the 1943.4.1 save (177 hub candidates, the 6 hubs of the pass,
  straight-line scores): with Wołyń as incumbent the best candidate (Bobruysk) scored 0.802 × Wołyń's at
  bonus 1.0 — 0.2 % short of the 20 % release bar, the freeze — and 0.704 × at bonus 0.25: released.
  With Bobruysk as incumbent it stays best under both (ratio 1.0), so the trunk keeps its railhead.
- Owner tuning (3), 2026-09-05, after campaign run 2 (`5432bfeb`, 8 saves 1941.10.7 → 1943.6.28, all on
  the L1-L3 build — `wa_ai_pc_alloc_pool` present in every save; GER–SOV war since 1941.6.22). Owner:
  "c'est mieux sur la logique, le problème principal reste que c'est trop lent … en un an, pas deux";
  "je suis ouvert à un build du tronc de berlin vers la frontière SOV avant barbarossa".
  MEASURED (`pc`, `var`, `tlm`): pool 70-132 civs, fully assigned every save; rails all-or-nothing —
  4 saves fund only rails, 4 saves fund no rail, of which 1941.12 and 1943.1 hold ONE rail with the
  counter at 2 / 0 weeks (the lane ran dry) and 1942.9.13 / 1943.6 hold a fresh lot of 17 / 11 not yet
  assigned; `built[13]` 102 → 330 = 228 rails in 20 months. DERIVED: pool ≈ 5 slots × 3.6 rails/month
  = 18/month capacity → ~60 % used; GER-held east level-steps (rail.py) 163 in 21 months, 2-13 per
  month, worst 1941.12→1942.3. MEASURED shape: level 5 reached Grodno / Polesie / Zhytomyr between
  1942.4 and 1942.9, Kiev 1942.9, Daugavpils 1943.6; T = 107 provinces at 1943.6 (run 1: 80 at 1943.4);
  railhead Wilno → Bobruysk at 1943.1 (L3 released it); one trunk, no parallel axis. Prewar: at 1941.10
  nothing east of Berlin at 5 (T5 = 33). Cause MEASURED in code by the lessons review, not the cadence I
  first blamed: `WA_AI_PC_railway_STRATEGY_prewar_preparation` was dispatched under `has_war = no` only
  (`railway_core` STRATEGY 3), and on the historical path GER is at war with ENG for the whole window —
  the peace mode never ran for GER (ASSUMED for run 2: no save before 1941.10). Target "1943.6 network in one year" = 19 rails/month = 100 % of the
  pool: momentum + a prewar head start, without touching the PC fraction (owner-excluded above).
  M1 vs M2 (owner asked, chose M1 + rails_per_slot 5): M2 alone (`rails_per_slot` 6) fills one interval
  with a lot planned on day-1 geometry and idles again whenever the pool grows; M1 re-plans and
  self-paces to the pool. Shipped:
  - M1 `railway_core` head of `WA_AI_PC_railway`: when the counter is running, `WA_AI_PC_railway_refill_on`
    = 1 (set at the pass tail when the pass ADMITTED segments, head+trunk+rest of the admission; a pass
    that admits nothing switches it off — review repair, the first draft tested `has_war`) and live rails (`WA_AI_PC_railway_count_live_rail`, the skip gate's count extracted
    to `railway_helpers`) < new `routes.refill_slots` (1) × `WA_AI_PC_alloc_pool` / 20 → counter = 0, pass
    now with the countdown PRESERVED (`_rail_refill_saved_`, restored minus this week's tick at the tail —
    review repair: the first draft re-based the counter, so recurring refills would have pushed the
    scheduled pass out and the override to 0 days in 42); `_rail_refill_pass_` = 1 blocks the ×0.6
    override re-arm, so the ratio stays 21 days in 42.
    Log `RAILWAY REFILL: live= slots=`. `routes.rails_per_slot` 4 → 5.
  - P1 `railway_core` STRATEGY 3: the prewar strategy is dispatched at war too when
    `WA_AI_CONFIG_RAILWAY_has_scripted_override` holds (at war it reads the CONFIG targets alone — the
    wargoal / justification population is gated `has_war = no` in `railway_strategies`); band 500 sits
    below the overseas-war routes (1000) and above every non-rail band. `WA_AI_CONFIG.txt`
    `WA_AI_CONFIG_RAILWAY_GER_to_SOV_window`: `date > 1940.7.1` (was 1941.1.1). Pass tail: a country with
    `_rail_peace_work_` = 1 and no war resets the counter to `interval.war_weeks`.
  t-table at GER run-2 numbers (pool 100 = 5 slots, 1.2 weeks per segment, capacity 25 per 6 weeks):
  | step | today | M1 + slot 5 | note |
  | --- | --- | --- | --- |
  | t0 pass admits | 16 (cap 20 − 4 live) | 21 (cap 25 − 4) | cap = pool/20 × rails_per_slot |
  | t0 + 3 weeks | ~13 built, 3-7 live | ~13 built, 8 live | 5 slots × 1.2 weeks |
  | t0 + 4 weeks | lot done, lane empty | live < 5 → REFILL pass, +~20 admitted | assign funds them the next pulse |
  | t0 + 6 weeks | scheduled pass | scheduled pass (override re-armed here only) | 21 days in 42 unchanged |
  | built per 6 weeks | 16 (64 %) | ~23-24 (~95 %) | capacity 25 |
  | no-work case (network at target, every pathfind failed, cap full) | scheduled pass every 6 weeks | the pass admits 0 → `refill_on` = 0 → no refill until the scheduled pass | worst case one pass per weekly pulse never persists |
  Bounded: at most one pass per weekly pulse per country, and only while the previous pass admitted
  something; refill needs pool > 0 and a prior pass on this build. ASSUMED: the cost of ~2 passes per
  6 weeks (up to 3 deep pathfinds per railhead plus the branches) is negligible — not measured. Lower
  bands while rails hold the head continuously (air 350/300, strategic 250, default 100): carried by the
  `[pc-queue]` aging lane (`alloc.aging_lane_weeks` 12, up to 3 candidates per pass) and the `[uk-air-basing]`
  air lane; the tell-tale stays `wa_tlm_pc_avail_share_pct` well above 60 %. Prewar override share:
  the scheduled prewar pass at war cadence arms the ×0.6 flag 21 days in 42 of 1940.7-1941.6 (was never,
  since the strategy never ran) — accepted, it is the head start the owner asked for. Prewar DERIVED:
  Berlin→Grodno/Brest ≈ 50-60 level-steps ≈ 3-4 months at the war rate, 11 months available from 1940.7.
- Verification (3), owed: next run — a 1941.5 save: T reaches Grodno / Brest at 5 (`rail.py` widest
  from 6521), `WA_AI_PC_railway_INTERVAL_counter` ≤ 6 in peace, `RAILWAY REFILL` lines in a logged
  wartime month, `built[13]` ≥ 19/month on the war saves, no save with one rail left and the counter
  running; known-false control: a country at peace with no CONFIG target keeps the 12-week counter.
- Verification (3) RESULTS, campaign `8bf94908` (BHU observer, monthly saves 1936.2-1945.8, all on
  the M1/P1 build — `wa_ai_pc_railway_refill_on` present from 1940.6; Barbarossa 1941.6.22). Scripts
  `run3_rail.py` / `run3_rate2.py` / `run3_front_hubs.py`, extractions `run3_pc.md` / `run3_front.md`
  (session scratchpad). PASSED on the two owner criteria, one open question:
  - P1 PASSED, MEASURED (rail.py): the level-5 component from Berlin = 26 provinces at 1940.6, 35 at
    1940.9, 69 at 1940.12 with its eastern end at Grodno, 72 at 1941.3-6; `rail-prewar` (500) rails in
    the PC queue at 1940.9 (Poznań, Kraków, Ostmark, Brandenburg) and 1940.12 (Łódź, Kraków, Katowice,
    Kielce, Poznań); 1941.3 and 1941.6 hold NO rail with `refill_on` 0 = the border network was done
    (Grodno / Białystok read 5 at 1941.6). Railhead memory SOV = 6464 in peace, Wilno at 1941.9,
    Bobruysk from 1941.12.
  - One-year target PASSED, DERIVED: T5 = 89 (1941.12), 105 (1942.3), 120 (1942.6, one year in) against
    run 2's 107 after two years; GER+subject east level-steps 10-15 per month 1941.7-1942.6 (run 2: 8);
    `built[13]` +17 to +24 per month over the same window (run 2: 11). Hubs at 5 from Berlin: Minsk,
    Bobruysk, Gomel at 1942.3, Daugavpils 1942.6, Kiev and Dnipropetrovsk 1942.9. Trunk shape: Königsberg
    - Kaunas - Wilno - Minsk (no marshes) then Bobruysk, a Kiev line and a southern Lwów - Vinnytsia -
    Cherkasy - Dnipropetrovsk line at 1000.
  - M1 PASSED, MEASURED: no war snapshot with one rail left and the counter running; 1941.9 shows a fresh
    lot of 20 trunk hops (1100) appended; `refill_on` = 1 on every snapshot 1941.7-1942.6.
  - OPEN, MEASURED: from 1942.9 GER's queue holds no eastern rail in any snapshot (`refill_on` 0), while
    frontline hubs facing SOV read Kharkov 4, Chernigov 3, one Gomel hub 2 until they are lost
    (1943.6-1944.6); `built[13]` still +111 in 1942.12-1943.6 but in the Baltic, Kuwait and Tripoli. The
    railhead stayed Bobruysk 1941.12-1944.6 while the front stood 200 km east. Cause not readable from
    saves — harness: load `1942.10_Oct.hoi4`, `tag GER`, `effect d_WA_spine_pass`, tag back, next Monday;
    read `RAILWAY SPINE cand=`, the `PATHFIND … FAIL` lines and `RAILWAY ADMISSION`.
  - Noted, one line: spines also armed for ENG (railhead British Somaliland), FRA (Rhineland) and POL
    (Vienna); 1940.9 funded 60 civs of East-Africa rails at 1000 while the prewar trunk at 500 got 20.
  - Front, MEASURED (`control`, `army`): Axis peak 37 SOV states at 1942.9-12 (Kharkov, Crimea);
    Leningrad, Moscow, Rostov, Stalingrad never fall; SOV retakes Kharkov by 1943.12, Dnipropetrovsk,
    Riga, Minsk by 1945.1; 1945.8 war still open, GER 335 divisions vs SOV 434, Kiev and Crimea still
    Axis-held. Rail is not the reader's explanation for the stall: the 1942.9 front hubs read 4-5
    except Chernigov 3 and one Gomel hub 2.
- Verification, owed: (1) console — a 1941-42 GER save with logging: one `RAILWAY SPINE`
  line per enemy passing the gate (with `served=N` and `trunk_hops=k > 0`), R1 in the centre of the front (Minsk/Gomel area for a
  Pskov–Rostov front, never Riga or Kiev), every branch pathfound from an S element with ≤ 20
  hops, the first `PC QUEUED` of the pass on trunk hops in value order, no band-700 stub; a
  1938 GER save: trunk toward the CONFIG target queued in peace; known-false control: Denmark
  (or any enemy failing the gate) logs no SPINE line and keeps direct routes. (2) campaign —
  `rail.py 6521 <hub>` narrowest link rises above 3 on at least one route within 3 passes of
  the front settling, and the two-spine signature (rail raised on both the Warsaw and the
  Lublin lines in the same year) is absent; `pc GER --match rail-prewar` shows no 700-band
  stubs; corridor projects no longer hold 100 % of rail civs while a land front is open.
- Closed when: (1) pasted here and passing, then (2) on one campaign.

### pc-build-speed — PARKED (2026-09-05)
- **Build spec: `documentation/WA_AI_RAILWAY_SPINE_SPEC.md` §8.**
- Parked heading only for the WIP limit (4 OPEN). Real state: **SHIPPED-UNTESTED 2026-09-05** —
  owner-admitted 2026-09-05 ("ajoute la correction des défauts du modèle à la spec"), code committed
  the same day, console harness (Verification (1) below) NOT yet run by the owner. Companion
  of `rail-spine-tree`: it is the only lever that shortens the trunk without touching rail cost,
  civs per project or the PC fraction (all three owner-excluded), and it is a model error, not
  a knob.
- Intended behaviour: the priority-construction ledger charges a project at the same speed
  the engine would build it — factory output × the builder's country construction modifiers ×
  the state's infrastructure multiplier, per building type — so PC neither under- nor
  over-paces the AI relative to what the player sees in the construction tooltip.
- Symptom, MEASURED (owner screenshot, GER construction tooltip June 1943, a 3-province
  railway project): cost 2 400 = 3 × 800; factory output 2.50; "Output from 20 factories:
  50.00"; modifiers +5 +5 +5 +20 +10 −25 + 5×5 = **+45 %**; "State infrastructure: ×1.80";
  construction speed **130.50/day** (= 50 × 1.45 × 1.80). MEASURED (`barb_supply test.hoi4`
  vs `autosave.hoi4`, one weekly pulse apart, project 11 at 20 civs): remaining 495 → 145 =
  350 per pulse = 7 × **50/day** — the ledger runs at 2.5 × 1.0 × 1.0. Ratio engine/ledger
  **2.6** in Germany; DERIVED 1.7-1.9 on Soviet ground (infrastructure 2-3).
- Cause, MEASURED (`WA_AI_CONSTRUCTION_PRIORITY_core.txt` `WA_AI_PC_get_build_speed`, THIS =
  state, called as `var:WA_AI_PC_target_state^_project_id = { … }` from
  `WA_AI_PC_update_project_progress`): (1) `modifier@production_speed_buildings_factor` and the
  per-type `modifier@production_speed_<type>_factor` are read in STATE scope; the modifiers are
  of category **country** (install `modifiers_documentation.md`, "Categories: country,
  war_production"), so the read returns the state's value = 0 for every building type — the
  +45 % (and the −25 % fatigue) never reach the ledger; (2) the infrastructure multiplier
  `1 + 0.1 × infrastructure_level` is applied only to types 5-12 and 15-16 (factories,
  refineries); the engine applies it to the railway too (tooltip ×1.80 at infrastructure 8),
  and ASSUMED to every province/state building (to verify per type against the tooltip
  before widening beyond rail: air bases, radars, naval bases, supply hubs).
- Change (shipped 2026-09-05, one commit, `# [pc-build-speed]` at every site):
  `WA_AI_PC_get_build_speed` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`, THIS = state, ROOT =
  builder) reads the country-category `production_speed_*` modifiers inside `ROOT = { }` (the
  block form rather than the spec's `ROOT.modifier@…` prefix — same fact, temps are
  chain-global), adds the one STATE-category member `state_production_speed_buildings_factor`
  read on the state, and applies the infrastructure multiplier (1 + `infra_per_level` × level) to
  EVERY PC type except infrastructure (type 1) — MEASURED: the mod's `00_buildings.txt` flags
  every other PC building `infrastructure_construction_effect = yes`; MEASURED on the rail
  tooltip for one flagged type; ASSUMED that the flag is the engine's switch for the others
  (the harness's known-false control on a non-rail type tests it). Publishes `pc_speed_mods_`
  / `pc_speed_infra_`. Constants: `wa_ai_pc.speed.factory_output = 2.5` registered against
  `NDefines.NProduction.POWERED_FACTORY_SPEED` (05_defines.lua; BASE is 0.0 in this mod —
  MEASURED), `wa_ai_pc.speed.infra_per_level = 0.1` (DERIVED: vanilla
  `INFRA_MAX_CONSTRUCTION_COST_EFFECT` = 1.0 spread over 10 levels; a ratio, not registrable).
  `WA_AI_PC_assign_factories` logs `PC SPEED: type=T state=S mods=M infra=I speed=X` for the
  first funded project of each call (under `WA_AI_construction_logging`; the mid-week
  completion recursion re-enters the allocator, so up to ~10 lines a week, log-only).
- Impact analysis (AGENTS.md principle 3). Callers of `WA_AI_PC_get_build_speed`, MEASURED by
  grep: the two sites in `WA_AI_PC_update_project_progress` (ETA pick and progress apply) and
  the new log site — all reached from the per-country weekly block
  (`WA_AI_misc_on_actions.txt`) and its own recursion, so ROOT = builder everywhere; no event
  or WA_TEST caller. Shared by EVERY PC type (air bases, radars, refineries, ports, hubs,
  rails, corridors, conversions). Every PC project on every AI country gets ×(1 + country +
  state mods) × (1 + 0.1 × infrastructure) — faster in a healthy economy, SLOWER under an
  economy-fatigue penalty (MEASURED `00_static_modifiers.txt`: `economy_fatigue_bad_modifier`
  carries `production_speed_buildings_factor = -0.5`, so the slow side reaches −50 %, not only
  the −25 % of the June 1943 tooltip). `savegame.py pc` `eta_d` reads the stored
  `wa_ai_pc_build_time`, which the progress site now writes at the corrected speed — no
  arithmetic mirror to change (MEASURED, the command has no speed literal). Temp hygiene: the
  log site overwrites `_project_building_type` / `construction_speed_`; MEASURED no reader
  follows in the fill, and both recursion callers re-set them before reading. Reach: historical
  and ahistorical alike (no tag, no date). Regression risk, STATED: PC allocation
  (`alloc.fraction` 0.40) was calibrated with the slow ledger; the same civ share now buys
  1.5-2.6× more buildings (DERIVED from the tooltip ratio; up to ×2 more on high-infrastructure
  German ground for the non-rail types now under the multiplier) — the corridor, air-base and
  refinery families all accelerate, which may reopen the "over-building" readings the caps were
  set against (LOGISTICS_MODEL rule 3). The owner's ruling is explicit: speed honesty is
  wanted; retune caps on measurement, not pre-emptively.
- Review repairs (lessons + architecture reviewers, same session, both CONCERNS, no CONFLICT):
  the state-category modifier added (was ignored); the infrastructure type set keyed on the
  building file's flag instead of a per-type tooltip deferral (the flag is the mod's own
  statement, the deferral premise was false); 0.1 declared as a constant with its derivation;
  the spec's `ROOT.modifier@…` wording aligned to the shipped block form; the fatigue figure
  corrected to the static modifier's −0.5.
- DERIVED effect on `rail-spine-tree`: trunk Berlin→Minsk 3→5 at 79 civs from ≈ 122 weeks to
  ≈ 50-70 weeks (Reich hops ×2.6, Soviet hops ×1.7-1.9); the prewar trunk fits comfortably
  between 1938 and 1941.6.
- Verification: (1) console — resume `barb_supply test.hoi4` with logging, one pulse: a
  20-civ rail project in a German state loses ≈ 913/pulse (7 × 130.5) instead of 350 and the
  `PC SPEED` line shows mods=0.45 infra=1.8; known-false control: the same project on a
  Soviet-owned state with infrastructure 2 shows infra=1.2, and a country with no
  construction modifiers logs mods=0 and 350/pulse unchanged. (2) campaign — GER
  `wa_tlm_pc_built_n` per year ≥ 1.5× the `916b90f6` figure (503 over the war) at the same
  `avail_share_pct`; tell-tale of over-reach: air-base/refinery caps hit earlier than before
  (`pc_built_by_type` 2/16 rising faster) — then retune those caps, not the speed.
- Closed when: (1) pasted here and passing, then (2) on one campaign.

### dmz-build-loss — PARKED (2026-08-30)
- Parked at creation: WIP limit (4 OPEN slots held by the armour subjects). **Fix is APPLIED in
  the working tree, uncommitted** — move to SHIPPED-UNTESTED when a slot frees or at commit.
- Scope: owner report 2026-08-30 (Discord, joueur 156) + owner order "applique le fix". Intended
  behaviour: the shared-slot construction walk never targets a state where the building cannot
  legally land.
- Symptom, MEASURED (player report): GER's WA_AI_C.0 bootstrap fires `WA_AI_queue_MIC` 100×,
  only ~58 mils appear; CIC/REF/SILO after it land fine.
- Cause: `arms_factory` (and dockyard, air_base, anti_air_building) is `disabled_in_dmz = yes`
  (`common/buildings/00_buildings.txt:134`), GER starts with 5 demilitarized Rhineland states
  (42/51/799/800/801, cleared by the remilitarization focus `germany.txt:7680`), two of them
  infra-10 at the top of `WA_AI_shared_slot_scores`, and no WA_AI construction trigger checked
  `is_demilitarized_zone`. ASSUMED (engine): `add_building_construction` of a disabled_in_dmz
  building into a DMZ state is a silent no-op — corroborated by the MIC-only fingerprint and by
  a tier-machine simulation reproducing 53/100 landed.
- Fix applied 2026-08-30: `is_demilitarized_zone = no` added to `WA_AI_available_MIC/NIC/AIR/
  AIR_allied/AA` (`common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`, `# [dmz-build-loss]`
  comments; the MIC anchor names the 00_buildings.txt dependency and radar/CIC/REF/SILO as
  deliberate exclusions) AND to the four `WA_AI_queue_FORT_CITIES/FORT_BORDER/CFORT_BASES/
  CFORT_COAST` limits (`WA_AI_CONSTRUCTION_queue_functions.txt` — bunker/coastal_bunker are
  disabled_in_dmz and the `WA_AI_forts_constructed_*` counters would inflate on dropped adds,
  same idiom). `check_ai_layers.py` 0 ERROR; `check_constants.py` errors are pre-existing
  `@advisor_*` debt in `common/characters/{ENG,GER}.txt`, untouched here (recorded, needs its
  own owner-requested subject to fix or waive).
- Reviews 2026-08-30: architecture CONCERNS (its two in-tree items were a stale read mid-edit —
  all five terms + the anchor were already landed; the @advisor exit-0 point recorded above),
  lessons CONFLICT resolved as follows: idiom copies FORT/CFORT fixed in the same change (this
  entry); the PC copy is an explicit closing criterion below (its correct form is per-type — a
  blanket DMZ term in `WA_AI_PC_can_build_project` would also block CIC/REF/infra projects that
  ARE legal in a DMZ, so it needs the type→building map, not this change's one-liner); the
  phantom-committed residual gets its t0/t1/t2 table below instead of the bare word "persists".
- Phantom-committed walk (residual on saves that ran the PRE-fix build; a fresh game on this
  build writes no phantom at all). Cadences: monthly C.10 pulses, TTL 1000 days, completion
  moves a level queued→built. Reference state: GER 51, built ~3, phantom committed ~13:
  - t0 (pre-fix burst): committed = built+10, TTL flag live; engine dropped the adds (DMZ);
    loading the fix mid-save makes the DMZ term skip the state entirely from the next pulse.
  - t1 (remilitarization, ~1936.3 historical, possibly never ahistorical): DMZ term passes;
    committed still +10 but < 45 → the state is AVAILABLE, not blocked. Only `depth_ok` reads
    10 ≥ 3 → tier C/D (a preference), so the state is deprioritized yet still placeable in
    big bursts.
  - t1→t2: each completed level raises built, shrinking the gap by 1; any 1000-day add-free
    window lapses the TTL and the next add rebases committed = built. Depth preference recovers
    gradually; at no point is any state hard-blocked.
  - t2 (TTL lapse or gap absorbed): committed honest again (`WA_TLM_sq_rebase_down_n` counts
    the lapse path); behaviour normal.
- Closed when: (1) an observer game on this build shows GER's day-1 construction queue holding
  ~100 queued mils (owner count, or `WA_TLM_sq_adds_by_type^1` ≈ 100 with the in-game queue
  matching), with zero of them in states 42/51/799/800/801 before remilitarization; AND (2) the
  PC copy of the idiom is closed: `WA_AI_PC_can_build_project` (or
  `WA_AI_PC_building_slot_available_for_type`) refuses a DMZ state for the PC types whose
  building is disabled_in_dmz (rocket_site, rail_way/supply via the railway queue), verified by
  grep + one console read.

### eng-minelaying — PARKED (2026-08-30)
- Parked at creation: WIP limit (4 OPEN slots held by the armour subjects). **Fix is APPLIED in
  the working tree, uncommitted** — move to SHIPPED-UNTESTED when a slot frees or at commit.
- Scope: owner request 2026-08-30 (Discord, joueur 156): the UK must minelay around the home
  island; he added the "Black Swan Mine Layer" on_research variant (`5e179dfb6`) and asked for an
  ENG goal file under `ai_navy/goals`. Intended behaviour: the ENG AI lays mines in home waters.
- Symptom, MEASURED (script, both trees read): the chain was broken in four independent places —
  1. NO `role_ratio naval_mine_layer` anywhere in WA `common/ai_strategy`: vanilla gives it to
     every major (install `default.txt:280`, `ENG.txt:1041`) and the replace_path dropped them
     all, so the minelayer role had zero production share and the AI never built the designs
     `ai_equipment/ENG_naval.txt:3874` declares;
  2. the fleet template referenced `Minelaying_1` while the task force is `MineLaying_1`
     (WA-introduced case mismatch; vanilla is consistent both sides);
  3. `MineLaying_1` accepts only `destroyer role = 4` while ENG's minelayer designs sit on
     frigate hulls (unit type `frigate`, `ship_frigate.txt:8`) and a submarine — no match;
  4. goal `generic_mine_laying` at priority 1–8 against WA's convoy protection 15–30 /
     invasion defense 15–25 / dominance 10–20 — mining scores last, fleets never reach it.
- Fix applied 2026-08-30 (5 changes + 1 induced, `# [eng-minelaying]` comments):
  `WA_DEFAULT_production_navy_main_focus_on_minelayers` (`role_ratio naval_mine_layer 5`, gate
  `WA_AI_PRODUCTION_should_build_minelayers` — renamed from the unconsumed
  `_main_focus_on_minelayers` for the layer checker; ENG-only via
  `WA_AI_CONFIG_focus_on_minelayers`); new `goals_ENG.txt` (mines_planting 10–18) paired with
  `blocked_for = { ENG }` on the generic goal (vanilla pattern); new `MineLayingFrigate_1` task
  force + fleet template; case typo fixed; `role_icon_index = 4` on the on_research variant
  (`naval_eng.txt`, engine default is 'auto'). Both design paths carry role 4 — ai_equipment
  `mine_layer_light` already had it (`ENG_naval.txt:3909`).
- Displacement, DERIVED (lessons-reviewer requirement): ENG role_ratio sum 157 → 162, so
  minelayers take ~3% of dockyards (~3 of ~100), proportionally from every role; convoy floors
  (`equipment_production_min_factories`) are forced lines, unaffected.
- Deliberate scope cut, recorded: vanilla gave the ratio to ALL majors; here ENG only, per the
  owner ("Not every country needs to prioritize it"). Every other navy stays at 0 minelayer
  share by design, not by gap.
- Reviews 2026-08-30: architecture CONCERNS (its blocking point, +1 LAYER4-NON-DECISION, closed
  by the gate rename — `check_ai_layers` 0 ERROR, DATE-LEAK baseline tightened 130→120 for the
  drop inherited from `5e179dfb6`); lessons CONCERNS (all three required lines are the three
  bullets above). `check_constants` errors are pre-existing `@advisor_*` debt in
  `common/characters/`, untouched here.
- ASSUMED until live: the task force `role = 4` filter matches the design's `role_icon_index`
  (systematic vanilla correlation, no in-game measurement yet).
- Closed when: owner live check (`tag ENG` + `imgui show ai_navy`) shows a `mines_planting`
  objective armed in home waters with `MineLayingFrigate_1` filled, and a campaign save shows an
  ENG minelayer production line plus mines actually present in North Sea / Channel regions.

### division-target-scaling — PARKED (2026-08-28)
- Parked 2026-08-28 (WIP limit, `armor-role-budget` enters - its Change 2 moved there
  wholesale). State at parking: Change 1 shipped, unverified.
- **Change 3 shipped 2026-08-28 WHILE PARKED, and the subject stayed parked only because the OPEN
  section is at the WIP limit.** It is a tester report against Change 1, so it belongs here rather
  than in a new subject. Move this back to SHIPPED-UNTESTED when a slot frees up; until then the
  three-day `UNTESTED-STALE` pressure is NOT on it, which is the one thing parking costs here.
- Scope: owner request 2026-08-28 — reduce every AI country's theoretical division target by
  75% because WA's factory counts and combat-area geometry make vanilla's target unattainable.
- Symptom, MEASURED (owner `imgui show ai_division_production`, GER): 149 active divisions,
  target 521; breakdown fronts 274 x 0.35, factories 528 x 0.45, manpower 311 x 0.30,
  threat 1.06, war factor 1.15.
- Change 1: `05_defines.lua` overrides all three `WANTED_UNITS_WEIGHT_*` inputs: fronts 0.08,
  factories 0.09, manpower 0.07. Every downstream threat/war multiplier stays unchanged.
- COUNTER-EXAMPLE against Change 1, MEASURED 2026-08-28 (owner `imgui show
  ai_division_production`, SWI): **21 active divisions, 4 wanted.** Breakdown fronts 25 x 0.08 =
  2.00, factories 40 x 0.09 = 3.60, manpower 65 x 0.07 = 4.55, threat 0.72. Per-role: militias
  current 3 / wanted 0, infantry current 13 / wanted 4, mountaineers current 5 / wanted 0.
  At vanilla's weights the same country reads fronts 8.75, factories 18.0, manpower 19.5.
  DERIVED: the 75% cut was sized on GERMANY, where active (149) sat far BELOW target (521) — a
  country building toward its ceiling. It inverts for a country whose STARTING OOB already
  exceeds the scaled target: wanted < active means the AI builds nothing at all, ever, until
  combat losses drag it under 4. Switzerland starts with 13 OOB divisions and gains 8 more from
  its own focuses (5 Sharpshooters + 3 Militia Anti-Tank) = 21, on 40 factories. This is the
  mechanism behind the owner's 2026-08-28 report that Switzerland 'can't create or recruit any
  division' (subject `swi-militia`) — the two militia bugs fixed there are real but downstream:
  with a wanted budget of 4 fully consumed by infantry, the militias role gets 0 whatever its
  template says.
  NOT ACTED ON: the three weights are the owner's explicit 75% cut, so the lever choice is his.
  Open question - a global floor (wanted never below active), a per-country
  `ai_desired_divisions_factor`, or a re-tune of the weights.

- Symptom 2, MEASURED (owner `imgui show ai_division_production`, ENG): wanted medium armor 189,
  infantry 47 and mechanized 95; the live ratio is approximately 40:10:20.
- Change 2 (owner order 2026-08-28): halve every armor `role_ratio` transfer from -20/+20 to
  -10/+10. The dependent USA-only `infantry_floor +15` block and trigger were removed with it.
  **SUPERSEDED 2026-08-28 by `armor-role-budget`**: halving kept the armour share proportional to
  the NUMBER of open tank roles, which is the bug the owner named the same day. The five per-role
  blocks no longer exist, so the armour lines below (armor impact, reachable-stack audit, and the
  ENG / USA-infantry verification rows) describe a shape that is gone - read `armor-role-budget`
  for the live armour behaviour. Everything in this subject about the three
  `WANTED_UNITS_WEIGHT_*` defines is unaffected.
- Impact: global and setup-agnostic. USA/CAN are owner-confirmed capacity-bound at their current
  full build rate; whether their lowered theoretical targets remain non-binding is ASSUMED until
  the live window is checked. Existing training-queue cancellation/decommission behaviour is an
  engine boundary and is not claimed.
- Armor impact, MEASURED (composition + template triggers): every country reaching an armor role
  keeps that role at a positive weight of 10 per active block in historical and ahistorical games.
  Regression risk, ASSUMED: GER/SOV/ENG/USA may field too few armored formations for spearheads;
  compare their wanted and current armor counts in the next campaign.
- Reachable-stack audit, DERIVED from the composition and template gates: light and transition are
  mutually exclusive; motorized is a fallback when armor/mechanized are absent; exactly one of
  marines/mountaineers costs 10. The deepest non-USA stack is `100 -40 armor -20 mechanized -10
  special = 30`; USA is `100 -30 armor -30 expeditionary mechanized -10 special = 30`.
- Historical constraint from commit `3da0be383`: "GER/SOV composition was healthy and is
  deliberately left byte-identical." `mine covers it because` the new owner order deliberately
  retunes every armor role after a live disproportionate wanted value; both countries retain each
  armed armor role at 10 and are explicit regression controls below.
- Owner objection: "USA et CAN construisent déjà à pleine capacité, et la cap souhaitée est
  irréalisable avec l'équilibrage du mod". `mine covers it because` the change lowers theoretical
  demand without lowering build throughput; the USA/CAN controls explicitly fail the change if
  the quartered target becomes their binding constraint.
- Verification: after a full restart, the same GER save shows the lower `Nr Wanted Divisions`;
  USA and CAN show `Current + Total Being Built` below `Nr Wanted Divisions` while continuing to
  build at their pre-change full rate; the same ENG state shows wanted medium armor near 95 while
  wanted mechanized stays near 95; USA infantry stays positive near 30% on its deepest stack; GER
  and SOV retain non-zero wanted armor.
- Symptom 3, MEASURED (tester report 2026-08-28, playthrough): in the early game up to mid-1940,
  GER and ITA need about 30% more divisions than the quartered target gives them (owner corrected
  the figure from 50% to 30% the same day, before any of it was tested). This is the first
  feedback on Change 1 and it does not contradict it - the GER reading that motivated the quartering
  was 1943-shaped (149 active against a target of 521), and the same weights leave the two countries
  that must be ARMED BEFORE the war they start too small in 1936-40.
- Change 3 (owner order 2026-08-28, from the tester report): +30% theoretical division target for
  the two European Axis majors until 1940.7.1.
  - New archetype `WA_AI_CONFIG_MILITARY_is_axis_european_major` (GER, ITA) in `WA_AI_CONFIG.txt` -
    the tags live there and nowhere else. Deliberately NOT `WA_AI_MILITARY_is_axis_member` +
    `is_major`: Italy is not an Axis faction member for most of this window, so a faction-derived
    gate would silently miss half the request. Kept separate from
    `WA_AI_CONFIG_MILITARY_is_axis_continental_core`, which also carries ROM/HUN/SLO - minors that
    must not receive a major's army target.
  - Gate `WA_AI_PRODUCTION_early_war_army_target_boost` (archetype + `date < 1940.7.1`) in
    `common/scripted_triggers/WA_AI_PRODUCTION_army_composition.txt`; payload
    `WA_AI_PRODUCTION_DEFAULT_early_war_army_target_boost`,
    `ai_strategy = { type = ai_wanted_divisions_factor value = 30 }`.
  - The window closes at mid-1940 because after the fall of France the war itself drives the target
    (the threat and war factors multiply it) and a flat boost would compound with them.
  - Stacks with `WA_AI_PRODUCTION_DEFAULT_army_expansion_override` for GER before 1938 - different
    strategy types, intended: that block forces BUILDING, this one raises what the AI thinks it needs.
  - **ASSUMED, and this is the weak point of the change**: `ai_wanted_divisions_factor` is base
    100 + value like every other `*_factor` strategy, so 30 reads as x1.3. DERIVED from vanilla
    `USA_90_division_gamble` (-30 for a deliberately small army) and
    `CHI_stop_disbanding_your_army_during_war` (1000). The install documents this type by NAME only
    (`common/ai_strategy/documentation.info`, strategy list); vanilla `SOV_cant_stop_wont_stop` uses
    `0.15` with a "FEED THE MEATGRINDER" comment, which under this reading does nothing and is most
    likely a vanilla authoring slip. The DIRECTION is safe, the MAGNITUDE is not.
  - REVERTED by the owner 2026-08-29 (`b6271ad9d`), RE-APPLIED 2026-08-29 by owner order, byte-for-byte.
    It now stacks on a higher global base than it was sized against: `WANTED_UNITS_WEIGHT_FRONTS_WANT`
    went 0.08 -> 0.09 -> 0.10 and `_FACTORIES` 0.09 -> 0.11 after the revert (`2cbc706f9` and the
    commit before it), so GER's pre-war target moves from the 84 the owner measured to about 109.
    DERIVED against the measured WA division size (18 520 men, weighted): 84 divisions = 1.56M men,
    109 = 2.02M, against 103 divisions / 1.91M for the historical September 1939 army. The x1.3
    magnitude is still ASSUMED and still the thing the console must confirm.
- Verification of Change 3 (owner console; no harness - 15 lines, no scripted effect touched): on a
  1938-39 save, `imgui show ai_division_production` on GER and on ITA shows `Nr Wanted Divisions`
  about 1.3x what the testers reported, with the same `breakdown [nr wanted]` inputs; a 1941 save
  shows the boost gone; a control major outside the archetype (SOV or ENG) is unchanged on both
  dates. If GER moves by something other than ~50%, the ASSUMED magnitude is what is wrong - retune
  the one literal, do not add a second lever. `GER moves by ~30%` is the pass condition.
- Closed when: the GER target, ENG armor ratio, USA infantry residual, GER/SOV armor controls and
  both USA/CAN non-binding controls pass once in the live window, and the Change 3 verification
  passes on GER, ITA and one control.


### theorist-hiring — PARKED (2026-08-28)
- Parked 2026-08-28 (net removed on owner ruling, nothing actionable until the next scored
  campaign; same waiting-state logic as templates-admission). Reopen when it lands.
- Scope: owner order 2026-08-27/28, REDUCED 2026-08-28: the scripted safety net (force-hire an
  army theorist for the engine's non-hirer class) was shipped `a5ade407a` then REMOVED the same
  day on owner ruling — the `recruit-loop` fix unlocked ARG's advisor hiring, so the advisor-less
  class was downstream of the CP/orphan loop, not an engine-desire mystery (the earlier
  decorrelation held only on 0767987f's pre-fix saves). What remains under this slug is the slot
  revival, commit `6ee54b596`: 257 dead `slot = theorist` advisors converted to
  army/navy/air_theorist (majors included: GER 2, ENG 3, JAP 3, SOV 2, USA 2 — why GER/ENG/SOV
  had no army theorist), role-strip helpers extended, AUS theorist-cost variable wired, 16
  commented ex-scientist blocks deleted.
- Verification (campaign probes only — characters-file change, no WA_AI harness system): next
  scored run, (i) GER/ENG/SOV have an army_theorist hired (appointed_advisors scan,
  wa-savegame-analysis session 2026-08-28); (ii) ARG and >= 5 more of the former non-hirer class
  (VEN, COL, ECU, PAR, CUB, PAN, NIC, IRE...) hire an army_theorist by 1940.1 — this doubles as
  the confirmation probe for the recruit-loop unlock; (iii) MEX/ARG army XP > 50 by 1941
  (theorist trickle feeding template upgrades).
- Closed when: probes (i)-(iii) pass on one scored campaign.

### templates-admission — PARKED (2026-08-28)
- Parked 2026-08-28 (WIP limit, owner choice; theorist-hiring enters). State at parking: shipped,
  owner ruling = campaign probes only (no console harness); awaiting the next scored campaign's
  probes (i)-(iii). Reopen when it lands.
- Scope: owner request 2026-08-27 ("no country should be locked from this"): admission into the
  AI template system (`WA_AI_TEMPLATES_has_infantry/tank_focus_completed`) must have no gap on
  any path. Found while answering why RAJ fields only "Reserve Divisíon" in 1944.
- Symptom, MEASURED in script (not save): the infantry gate listed 20 country focuses; 21 trees
  grant the free-design spirit — RAJ (`RAJ_revise_indian_defence_plans`, india.txt:3540) was the
  missing one, so RAJ never designed a normal infantry template. Same class of gap for any
  country whose design focus is unreachable ahistorically; the tank gate additionally excluded
  every generic-tree country outright.
- Shipped 2026-08-27: (a) both gates now key on the hidden techs the design focuses set
  (`infantry_modernization_tech` / `mobile_warfare_drive_tech` — durable; the paired spirits are
  strippable by `WA_AI_TEMPLATES_remove_wrong_army_spirits`, verified 21/22-tree pairing exact);
  (b) one-way deadline latch `WA_AI_TEMPLATES_design_deadline_passed` (monthly, AI only: date >
  1941.1.1, or at war and date > 1939.6.1 — owner-approved dates) admits countries whose focus
  never comes, at full XP cost. Shared-tree entries (`army_effort` &c.) unchanged. Timing for
  the 20 previously-listed countries is identical (tech set by the same focus).
- Latch-flip walkthrough (lessons requirement — the flag-set is a SECOND deciding window: when
  `WA_INFANTRY_TEMPLATE` first sets, the enabled ai_template target changes and the engine
  re-runs its role/decommission pass; this window already opens today at every focus completion,
  the latch extends it to the never-focused cohort and synchronizes part of it at 1941.1.1):
  - Peace cohort (e.g. SPA, no design focus, no war): t0 = first monthly pulse after 1941.1.1
    (≤ 31 d) sets the deadline flag, same pulse runs calculate (latch ordered before it);
    if a T1 doctrine is picked without required spirits, calculate blocks one tick while
    `ensure_correct_spirits` repairs — worst t0 slip = +1 month. t1 = same tick,
    `WA_INFANTRY_TEMPLATE` set, FALLBACK target disabled, value target enabled. t2 = engine's
    next template-designer pass (cadence unobservable, ASSUMED days): role rescored, losing
    template copies decommissioned (recruitment frozen, live divisions untouched — ASSUMED per
    ITA_1936_land_nsb_ai.txt header semantics); conversion toward the new target crawls at full
    XP. In peace, nothing recruits meanwhile — residual = cosmetic template churn.
  - War cohort (country at war, > 1939.6.1): t0 = first monthly pulse after war entry — the flip
    lands AT mobilization by construction. t1 same tick; t2 = one engine pass during active
    recruitment: the recruitable infantry template can change identity mid-mobilization, and the
    division-creator `has_template` re-create ladder (lessons) is exposed for one window.
    Bounded to ONE transition per country per campaign (flag and techs are both one-way; no
    flicker), but the per-country cost of that single window is engine-side, ASSUMED, and is
    exactly what probe (iii) watches.
- ASSUMED, stated: engine role-reassignment/decommission semantics and cadence
  (ITA_1936_land_nsb_ai.txt header is the best written source); which template the engine then
  trains is its arbitration, not observable in script.
- Verification (campaign probe, next scored run): (i) by 1942.1 every AI country with ≥ 10
  divisions has country flag `WA_INFANTRY_TEMPLATE` set (save-visible flag; extractor:
  savegame.py flags) — RAJ explicitly named; (ii) RAJ 1944 division census: majority of line
  divisions on a designed infantry template, "Reserve Divisíon" no longer the plurality type;
  (iii) latch-window health on TWO deadline-admitted countries (one war-cohort, one peace/
  generic-tree with armor techs): division count does not drop across the admission month, and
  the template census does not ladder-churn (same template id set across 3 consecutive monthly
  saves after admission — the RS column-deadlock lesson has never been exercised by this
  population).
- Owner ruling 2026-08-28: NO console harness for this subject — campaign probes only ("attendre
  prochain test"). The harness-rule borderline (~40 lines, harness-less system) is settled by
  this line.
- Closed when: probes (i)-(iii) pass on one scored campaign.


> **Campaign `1ac7e4ea` PARKED-probe results (2026-08-27, all MEASURED unless noted):**
> `rk-no-divisions` **PASSED again** (7 RK tags with no `units` section at 1943.6+1945.6, ALB flat
> at 3). `silo-breadth` campaign leg **PASSED** → CAMPAIGN-OK (see row). `uk-truck-supply` stock
> leg **PASSED** wide (ENG own-built motorized 12.6k/9.4k/11.1k at 1942-44.6 vs bar 1500); Africa
> hub leg NOT CHECKED — not save-visible, needs a WA_TLM gauge at the hub-motorization site.
> `prospecting-coop-solvency` **PARTIAL PASS** — coal counter 36→55 with solvent importers
> (HUN 200 imports, ITA 1200-1467); iron/alu counters flat while ITA/BUL/ROM sit at 0 iron
> imports (shape matches) — but attribution is STRUCTURALLY blocked: the gate is OR-over-members
> and `num_of_civilian_factories_available_for_projects` is not serialised; note ROM lost ALL
> imports 1944.6→1945.6 while needs=3 (only starved-buyer candidate, cause not save-separable).
> `aoi-border-garrison` (a) PASS 60-70 % border, (b) PASS, (d) PASS, (e) PASS (flat 10 div while
> Suez ENG-held); (f) VOID — the colony FELL ~1940.12-1941.3 (ETH free from 1941.3, ITS
> annihilated), i.e. holds ~7-9 months vs **37 in `24933fb9` — a colony-survival regression
> signal to watch**; leg (c)'s ids 217/380/381 are WRONG in this file (Stalingrad/Utah/Wyoming) —
> intent PASS (ITS only ever in its 5 border/coast states); re-derive interior ids at reopen.
> `minor-expeditionary-fitness` (a) **FAIL on NEP** (2 of 5 divisions on Nahr/Sinai fronts
> 1941.6-1941.9 at 1 MIL — ~4 500 km out; BHU clean), (b) first half FAIL (same NEP), deploy-cap
> half PASS (NEP flattens ≤ 5), ETH control PASS-with-caveat (crosses the 5-MIL bar mid-growth),
> (c) PASS. `allied-total-commitment` headline **FAIL confounded** — CAN 4/4 divisions home
> 1941.6, 1/1 1942.6, but CAN fields 1-2 divisions on 37→100 MILs (the force-generation collapse
> upstream owns the reading, not the garrison rule); continental-feed leg PASS (Bourgogne +
> Trøndelag fronts 1940.6, Algiers buffer 1943.6); (b) PASS (AST/NZL/RAJ re-garrisoned < 3 months
> after JAP DoW 1941.12.8); (c) PASS for AST/RAJ/SAF; (d) UNSCOREABLE (no factionless belligerent
> exists — Allies have 21 members by 1941.6); **SS24 bulwark FAIL** — RAJ 4 divisions on
> metropolitan FRA soil (Bourgogne/Isère/Alpes) + CAN 1 at 1940.6 while `FRA_disjointed_government_3`
> active, before fall_of_france. `scripted-invasion-reservation` leg (b) still NOT MEASURABLE —
> landings happened (Torch orders 1942.9-10, D-Day consumed < 1 month) but `plans.py` cannot
> print a type-3 order's TARGET (tooling gap: a `--invasions` view would close it).
> `aifc-closure-eth` **FAIL — persists**: same +250 vs −150 on all 6 observable saves
> (1943.7→1946.1, 30 months); mechanism DERIVED — a stale 1940.1 +400 boost never negated,
> surfacing when ETH re-enters the book; GENERAL leak, not ETH-specific: ITA/UKT and ENG/FRS
> carry identical stale +400s hidden under the dead-tag RESIDUAL label, and residual counts grow
> monotonically (GER 2→12) — no reconcile ever retires an entry.

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
| `armor-class-handoff` | SHIPPED-UNTESTED, parked 2026-09-02 (WIP limit, owner order - slot given to `levant-iraq-corridor`). Was unparked 2026-09-01 on an owner task and re-parked without its console run. Shipped: `WA_AI_CONFIG_TEMPLATES_admits_medium_armor` (the old 7-entry tag/tech OR kept verbatim as an ACCELERATOR, plus `WA_AI_CONFIG_switch_from_light_to_medium_armor` as a final OR term so the list can never gate the medium class shut), `_TEMPLATES_focus_on_light_armor` deleted, `WA_AI_TEMPLATES_switch_from_light_to_medium_armor` gains `has_medium_armor_unlocked` (handoff, not cliff); era boundary is now ONE literal both sides derive from. Reviews applied; commit-hygiene split of `6654f729f` recorded in git. OWED: `event wa_abg.1 GER` in 1940.6 (harness exists, so TESTED needs it), the MIS console read, and the campaign legs below | Campaign `GER_1940_06_29_02.hoi4` (1940.6.29): **3 countries on the whole map hold any `WA_*_ARMOR_TEMPLATE` flag** (ENG, FRA, SOV); GER, ITA, JAP, USA and every minor hold none. GER `wa_ai_armor_budget_medium` = 15 against `_light` = 0 - the role budget wants 15 % armour no template can train; its 8 armour divisions are `history/` leftovers and 127 medium chassis sit unmounted. Cause: the light-era boundary moved 1941.1.1 -> 1940.1.1 while the medium gate lost its universal date fallback for a closed 7-entry OR of tag/tech literals | A campaign save shows **no major with `wa_tlm_armor_gap_n > 1`** and GER holding `WA_MEDIUM_ARMOR_TEMPLATE` with medium-tank divisions in `plans.py --templates` by mid-1940; AND (conversion half) a campaign crossing 1940 shows a major's pre-boundary light-armor divisions ending up on medium templates instead of frozen light ones; AND (MIS half) a major whose medium flag sits in 6105-6110 shows its ex-light divisions on a 6 med + 3 inf-support + 6 mech composition, not a pure 9+6, with at most one medium template family shape. Full record: git log `[armor-class-handoff]` + this file's history |
| `analysis-tooling` | TESTED, parked 2026-08-27 (slot freed for `can-transit-attrition`, owner admission). All three tools shipped+validated (comp rungs v33 F9-booted; aifc.py DEAD-TAG banner; plans.py --invasions) | comp gauges floored to 0 under 5 armour divisions; aifc.py printed dead tags as live churn; type-3 targets unreadable | v33 campaign probe: a major with 1-4 armour divisions reads `comp_armor` = that count, and `tlm` never reports comp_* FROZEN on live majors |
| commonwealth-handoff | OPEN (parked 2026-08-27, owner order - WIP limit; exemption lever live since 2026-08-25) | Handoff inverts: availability bars read TOTAL divisions, not in-theatre (24933fb9: RAJ reads available with 3 div in East Africa on 76 total, ENG back-fills 14); every bar single-threshold, flap lever documented in the block (git history of this file) | Delegate missions armed and manned (R72 legs), Indian army in East Africa/El Alamein, no dominion dockyard nailed by an unbuildable design |
| `aoi-border-garrison` | OPEN, both legs shipped 2026-08-27, parked 2026-08-27 (WIP limit, owner choice — slot given to `aifc-traction`). Leg 1: `AXIS_abandon_east_africa` FRONT/THEATRE retargeted off region 17 (corridor {380,381} + s.r. 217), new `_colony_THEATRE` -200 gated `NOT owns_east_africa_colony`, ITA buffer widened to {550,559,271,909,910}, family gate extracted. Leg 2 (sea reinforcement): buffer ratio 0.10→0.20, trigger `east_africa_sea_route_hostile` (Suez 923), `owner_cut_off_THEATRE` -200, `naval_avoid_region` +1000 on the 5 Red-Sea/Indian-Ocean lanes. Campaign `24933fb9`: colony holds 37 months vs 2 pre-fix; (b) PASS (EA front orders manned), (d) PASS (0 GER div), (c) marginal FAIL (1-2 strays, Kurdufan buffer leak order 9607 unexplained), (a) FAIL as written / PASS on buffer population (43-57 % border). OWED: F9 boot (new ai_strategy blocks), owner imgui (cut-off gate armed/released vs Suez), §12 telemetry re-instrumentation before next scoring | ITA 9/9 AOI divisions pinned to {550,559} port buffer, zero EA front orders for ITA and ITS (`15176ce6` 1940.9-10); leg 2: AOI grows 9→11-23 by 1943 by sea past the Allied navy (`24933fb9`; ITS never released, growth = external) — engine never refuses the route (`MAX_ALLOWED_NAVAL_DANGER 80` vs ceiling 50) | (a) >= half AOI divisions in border states {271,909,910,550}, (b) EA front order for the AOI holder, (c) zero ITA/ITS div in 217/380/381, (d) zero GER div in AOI, (e) no sea growth while Suez hostile (~0.20 prepositioned at entry), (f) reinforcement resumes once the Axis takes Suez. Full record: git log `[aoi-border-garrison]` + this file's history |
| `east-africa-stand-down` | SHIPPED 2026-08-31, parked same day (WIP limit; owner-requested subject). Gate `WA_AI_MILITARY_should_allies_war_against_ita_central_africa_diplomacy` gains `WA_AI_MILITARY_east_africa_enemy_is_substantial` (>= 2 of the 7 AOI core states enemy-controlled OR one enemy > `@WA_AI_EA_RUMP_ARMY_BAR` = 8 divisions in theatre); anglo-major `conquer ITS 500`/`contain ITS 200` now retires on a rump via `abort_when_not_enabled`. Reviews: architecture OK, lessons CONCERNS repaired (per-enemy strength documented — split 6+6 force stands down until it retakes a 2nd state, realistic AOI population is ITA/ITS only since GER is brake-barred; 7-state list cross-commented; ROOT-relative header). Flap walk: t0 rump at <= 1 state / <= 8 div per enemy → enable false, drive aborts (enable re-read cadence ASSUMED sub-weekly); t1 enemy retakes a 2nd state or masses > 8 in one tag → re-arms next evaluation (Fix-132 counter-landing: 12 div = armed); t2 worst case one abort/re-add cycle per boundary crossing, cost = a re-created invasion order — accepted, a re-arm against a re-expanding enemy is correct. ASSUMED (engine boundary): dropping conquer/contain retires standing engine invasion orders — the probe owns it. Doc §12 updated. Sibling rump hole in `east_africa_theatre_contested` OWNER limb deliberately untouched (separate subject) | ENG→Eritrea + USA→Eritrea naval-invasion orders live 18 months (USA order 47 created 1941.12.19, both present to 1943.6) against a 1-2 province ITS rump — the ONLY Allied invasion orders at 1942.9 and 1943.6 while Egypt fell; 11 Allied tags 34-52 div in East Africa vs a 4-8 div Axis rump, Egypt+Libya+Levant never > 13 Allied div (`5ee2d112`, BHU cloud observer) | A campaign where ITS falls to <= 1 AOI core state shows the ENG/USA invasion orders against ITS DISAPPEARING between consecutive monthly saves within ~2 months of the reduction (order-disappearance via `plans.py --invasions`, never `starting_date`), AND the drive armed earlier in the same campaign while ITS held >= 2 states (control: the East-Africa campaign is still fought and won); regression tell = an EA counter-landing > 8 div faces a re-armed drive |
| `east-africa-proportionality` | SHIPPED 2026-08-31, parked same day (owner-requested subject; supersedes the [east-africa-stand-down] division-of-labour sentence — owner order). The contested_FRONT +150 gate gains `east_africa_enemy_is_substantial` (same trigger as the DIPLOMACY drive), so the faction-wide manning pull retires against a rump; mop-up carriers = RAJ delegate +100, committed-minor +60, exec front_control untouched; sink-armed members now net -100 (was +50 through their own sink). Reviews: lessons CONCERNS (sum-arithmetic shown — RAJ +100 / minor +60 / fit 0 / sink -100, no net-negative carrier; multi-rump gap probe pre-registered below; abort-cost labelled ASSUMED), architecture CONFLICT resolved by explicit supersession (doc §12 rewritten, trigger header rewritten, P3(g) sentence at the gate: the mop-up reservation assumed the mass was needed, `5ee2d112` refuted it — 34-52 div on a 4-8 div rump 14 months, blocker was the unfired Massawa assault). Boundary walk: t0 rump (≤1 state, ≤8 div/enemy) → +150 aborts one evaluation later; t1 2nd state retaken or >8 div massed → re-arms; t2 cost per crossing = engine re-request, ASSUMED, probe-owned. F9 boot NOT owed (no new ai_strategy block — one gate term) | Campaign `5ee2d112`: 11 Allied tags held 34-52 divisions in East Africa vs a 4-8 div rump for 14 months (Egypt ≤13 div while falling); the +150 armed for every fit member until ITS annexation because the gate had no mass term | Next campaign: (a) once the AOI enemy is ≤1 state and ≤8 div per enemy, Allied divisions in the 7 AOI states fall below 15 within 3 months while the theatre still finishes (rump dies, no R62 empty-theatre); (b) multi-rump probe: if ≥2 enemies each ≤8 div together hold ≥16 div in the AOI while `enemy_is_substantial` reads no AND the theatre stalls, the per-enemy semantics is the cause — change to a sum mechanism; (c) regression: an EA counter-landing >8 div re-arms the +150 (Fix 132 scenario) |
| `naval-invasion-dominance` | SHIPPED 2026-08-31, parked same day (owner-requested subject). First WA use of `naval_invasion_dominance_weight`: `WA_AI_NAVAL_DEFAULT_invasion_path_supremacy` value 50 (EAI operation value; vanilla doc example 30), gate `WA_AI_NAVAL_should_focus_supremacy_on_invasion_paths` (has_war + navy >9), every belligerent both sides. Reviews: lessons CONCERNS (lever-is-hypothesis — probe pre-registered; ASSUMED inert without invasion plans, labelled in block header; boot-test required), architecture CONCERNS repaired (TYPES_REFERENCE row 25 edited not duplicated, NAVAL_DEFAULT header scope line amended). OWED: F9 boot test (new strategy block, first use of the type — owner run) | Campaign `5ee2d112`: USA→Massawa invasion order staged 18 months (created 1941.12.19) and ENG→Brittany orders 8 months fully convoyed (26/26), never executed; owner diagnosis = no on-path naval supremacy; WA used none of the supremacy-tasking levers (naval_invasion_dominance_weight/naval_invasion_support_priority zero uses) | Next campaign: a staged Allied invasion order of the Massawa/Brittany class (fully convoyed, target coastal) EXECUTES within 4 months of creation, or on-path dominance measurably rises vs `5ee2d112` baseline (navy --fleets region assignment on the path regions); regression tell = no fleet abandons convoy escort wholesale while convoys are being lost (escort mission share stays >50% of pre-fix share) |
| `aifc-closure-eth` | MEASURED 2026-08-27, never opened (found during the `aifc-traction` sweep) | ITA carries a `CLOSURE MISMATCH` on ETH — ledger NET +250 vs book -150 — on 8 consecutive quarterly saves, 1943.10→1945.10 (`24933fb9`): the +400 boost was never cancelled when ETH was annexed, a later -150 suppression stacked on top; the `WA_AI_AIFC_helpers.txt` KNOWN GAP's "rare and self-correcting" does NOT self-correct in 25 months | The armour reconcile retires/cancels book entries on annexed or dead tags (or the residual is bounded with a t0/t1/t2 table and accepted in writing); a campaign shows no ledger-vs-book mismatch persisting past 2 reconciles |
| `minor-expeditionary-fitness` | SHIPPED-UNTESTED, parked 2026-08-27 (owner order). Shipped: fitness floor `WA_AI_MILITARY_is_fit_for_expeditionary_front` (> 5 MIL; raised to > 10 on 2026-08-27, owner order on the ETH-at-8 symptom — trains cap kept at < 5, registry group `expeditionary_fitness_mil_factory_floor` now advisory, the 5-9 band trains at home but stays home) + CAPS `unfit_army_stays_home` -100 (`e958ef934`); the two ALLIES pulls (`europe_first`, `east_africa_contested_FRONT`) fitness-gated 2026-08-25; lend-lease gate `WA_AI_LEND_LEASE_recipient_is_worth_equipping` (fitness OR `home_threatened`, homeland hatch owner-ruled) on both recipient paths; 2026-08-27 `WA_AI_PRODUCTION_trains_no_divisions` (< 5 MIL + > 4 div + no civil war -> build suppression, merged [rk-no-divisions], registry group `expeditionary_fitness_mil_factory_floor`). Diagnosis settled: H1 KILLED (owner imgui MEASURED, entry armed at -100), live cause H2 (-100 under-sized vs ALLIES +150/+75 pulls, cross-area summing still ASSUMED) + H3 (buffer/no-order divisions out of any front_unit_request's reach). Campaign `24933fb9`: leg (a) materially improved (1944.6 12/12 NEP home; 1941.6 window still violated, 6/10 in Egypt/Libya). OWED: console harness (FROM.FROM state_trigger), F9 boot (`trains_no_divisions` block), lend-lease harness run (`wa_test.300`/`301`) | NEP at 1 arms factory holds front orders across the Sahel/Horn for 4.5 years, 9-13 of its 12-16 divisions out of region (`8f9b5653`); ETH at 8 factories behaves identically = the > 5 gate misses the owner's rule | (a) NEP/BHU divisions never beyond their own neighbourhood, (b) no country at <= 10 MILs fronting beyond its neighbourhood AND every no-civil-war < 5-MIL country deployed <= 8 div sustained after 6 months at war (NEP flattens; ETH-class control at >= 5 MILs still grows), (c) RAJ/AST/CAN theatres still manned once NZL/SAF are held back. Full record: git log `[minor-expeditionary-fitness]` + this file's history |
| `fra-battle-of-france` | OPEN, fix shipped 2026-08-27, parked 2026-08-27 (WIP limit, owner choice — slot given to `lend-lease-observability`). Shipped: `FRA_homeland_invaded_recall_colonials_THEATRE` (area_priority -90 NA/med/middle_east, gated `home_threatened`), Alpine pair `FRA_alpine_front_FRONT`/`_THEATRE` (+100 south_france, gated `any_enemy_country = is_italian_homeland_power`), `FRA_defense_of_the_colonies_FRONT` re-armed to -5000 release, no-op `FRA_ignore_garrisons_until_invasion_start` deleted; spec SS25; reviews applied; F9 boot OK. Campaign `24933fb9` NOT CHECKED — `surrender_progress` not serialised and the gate window falls between monthly saves (ITA declares 1940.6.11, FRA dead by 1940.7.1); symptom near-vacuous this run (FRA 3/121 div in NA+Corsica). ASSUMED stated: garrison -5000 release semantics; colonial channel of the ~20 div | Owner report (ironman `feedback_save`, so owner figure not save-MEASURED): FRA garrisons North Africa/Corsica (~20 div) during the Battle of France while the Italian border sits open | A non-ironman Battle-of-France save (mid-June, or the console harness) shows (a) FRA NA+Corsica division count falling once `surrender_progress > 0.05`, (b) >= 2 FRA divisions on the south_france fronts while an Italian homeland power is an enemy, (c) Maginot/fall_rot nets unchanged |
| `allied-total-commitment` | TESTED, parked 2026-08-27 (WIP limit; F9 boot test for the CAN reserve-batch reward still OWED). Campaign `24933fb9`: the batch FIRED and DEPLOYED (MEASURED: 10 `Reserve Divisíon` at 1939.11) but was consumed on a front by 1942 and CAN never rebuilds (2-4 div 1941-44 on 104 arms factories — separate defect, candidate subject); leg (a) still FAIL through 1943 (100% home areadef at 1943.6), half the army abroad by 1945.6. Amended same day (owner orders, two rounds): (1) the one-shot closes the reserve program after its batch — `WA_reserves_unlock_template` + `reserves_deployment_complete_flag` applied directly (NOT a bank flush; owner refused deploying more) so the template becomes modifiable; (2) a READY batch (bank >= 10) is spent like a normal activation — the +10 grant fires only on an empty/short bank, so no residual bank remains when the country had recruited its own. Fresh campaigns only (a save past the focus keeps its locked template). Reviews: architecture OK, lessons CONCERNS — retroactivity stated here, no `break` writes in the deploy path (MEASURED), refill impossible pre-unlock (`WA_reserves_can_recruit` needs `has_war = no`, the focus needs `has_war = yes`) | CAN 4-9 div, 100% areadef home garrison (`8f9b5653`); release trigger PROVEN on CAN (wa_tc.1 harness 1942.2, closure PASS). **Owner imgui 2026-08-27 (MEASURED): CAN garrison tree = ONE summed entry, Weighted Value -4950 (-5000 release + 50 minors_home_first) — armed, held, and SUMMED (first direct proof same-type/same-target entries sum) — yet the home engine areadef divisions do not move: a negative `garrison` does NOT empty existing engine area-defense orders; the buffer is the proven mover (Scotland div, 1942.3).** Shipped same day (owner order "zéro division au mainland"): `protect_home_floor` gated off under `total_commitment_active` (threatened +200 tier keeps its own gate), new `CAN_THEATRE_total_commitment_empty_mainland` buffer ratio 0.75 (sums with defend_britain 0.25 to 1.0, per-order summing ASSUMED) on the britain states, `subtract_fronts_from_need` so front divisions stay abroad. Reviews: architecture CONCERNS (SS23 consumer rows + summing relabelled) + lessons CONCERNS (all applied: 0.75 re-sized as its own order — the ratio-pool arithmetic is lessons-REFUTED, each block is a separate order and >1.0 arbitration UNKNOWN; buffer→continental-front feed labelled ASSUMED, USA unit_buffer_for_europe pattern; no new ai_area alias, area=britain reused, cap-72 item void). **Landing-residual t0/t1/t2, stated:** t0 enemy lands on a Canadian core → `home_theatre_threatened` trips at the enemy-on-core term; t1 next engine strategy re-evaluation (ASSUMED sub-weekly, SS23 cadence limit) — commitment flips off, buffer disarms, threatened +200 arms; t2 transatlantic return crossing ~2-4 weeks; worst case ~3-5 weeks of thin mainland, and front-engaged divisions in Europe return slower still — ACCEPTED, it is the owner's zero-mainland order. defend_britain 0.25 armed for CAN is MEASURED (the 1942.3 Lanark order, states byte-equal); both-blocks-together is only observable next campaign. F9 boot owed. Probe: next campaign, zero CAN divisions in Canadian states while committed and home safe (vs 2-3 in `24933fb9`), AND CAN divisions appearing on continental fronts (tests the buffer feed). **2026-08-27, second owner report (RAJ divisions in BEL/HOL mid-Battle of France): the gate's missing BRAKE half shipped** — `WA_AI_MILITARY_ALLIES_overseas_guests_wait_for_bulwark` (`FACTION_ALLIES_FRONT`, front_unit_request -100 on benelux/north_france/france/west_france/south_france) + audience trigger `WA_AI_MILITARY_is_overseas_guest_refused_by_bulwark` (allies member, at war, capital outside Europe, gate closed). Six-box (static, rung 2 unmeasured — owner report, no save): the gate only withholds the +150 boosts; a total-commitment released army (RAJ: minor+subject+fit+home-safe) still reaches the only live European fronts via engine default on the flat baseline, the Africa direction +60 being inert pre-Italy-entry and no CAPS veto applying to a fit member. Doc §24 updated (counter-bid ruling: not violated — during the window every positive on those areas is enable-gated off by the same trigger, the -100 suppresses engine default only). Reviews: architecture CONCERNS (doc sync — applied) + lessons CONCERNS (ASSUMED header on -100-as-veto and static capitals added; all-enable already true). Owner confirmed 2026-08-27: the reported game ran HISTORICAL difficulty — the gate was closed, the missing brake was the live path, the fix targets the reported symptom; non-historical behaviour (gate open, brake inert) stands by the earlier owner ruling | Campaign legs: (a) CAN majority front/buffer outside North America while home safe; (b) AST/NZL/RAJ areadef ~0 while Pacific quiet AND re-garrisoned within 3 months of `pacific_threat_imminent`; (c) dominions on African fronts once past the 10-factory fitness floor (raised from 6 on 2026-08-27); (d) control: a non-faction minor at war keeps its home garrison; plus SS24 bulwark-guest probe (zero overseas-Allies div on FRA soil AND on the benelux/BEL/HOL fronts while FRA holds `disjointed_government`, historical difficulty; control: the flow resumes once the idea is shed or fall_of_france). Full record: git log of this file + [allied-total-commitment] commits |
| `scripted-invasion-reservation` | OPEN, parked 2026-08-27 (owner order; console harness legs A-C PASSED 2026-08-23, leg (b) NOT CHECKED on `8f9b5653` - the Allied AI never wanted a French landing, so the mechanism never ran) | Halab 1944.6: USA order 252 holds 9 divisions on a GER-held, GER-flagged reserved target - H1 (@FROM inert in ai_strategy context) vs H2 (-200 outbid on a pre-existing order) undecidable from the save | A campaign in which the Allied AI wants a reserved beach shows no engine invasion order against it; or an ai_strategy-context harness leg proves @FROM renders. Full record: git log of this file + [scripted-invasion-reservation] commits |
| `suppression-templates` | SHIPPED 2026-08-27, boot OK - parked for the next campaign (WIP limit) | Owner: countries burn army XP designing 4x-light-cav garrison templates, field them to the FRONT, and the template (no MP) is also the state-garrison pick. MEASURED in code: role prio 1000 (~37% of XP draws), reinforce_prio 1, use_suppression_templates = always yes | A campaign shows minors' army XP not spent on suppression templates while neutral, and no suppression-template divisions under front orders. Shipped: trigger gated (war OR non-core control) + LATCH on the existing flag (no mid-campaign decommission flip), role prio 50, reinforce_prio 0, dead build_army_cavalry pair deleted. Engine garrison scoring untouched |
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
| `prospecting-coop-solvency` | SHIPPED 2026-08-27, parked same day (WIP limit; F9 boot test OWED) | Owner request: coop prospecting must check the needy ally can IMPORT. GER 1945.7 (`15176ce6`) re-prospects coal on 20 164 effective; sole weight = coop branch; ITA at -1046 imports 0 with 0 civs avail. Shipped: ally-side gate in all 9 `WA_AI_allies_need_<r>` (avail>0 OR `resource_imported@<r>` > 0 — the import leg answers the lessons CONFLICT on saturation collapse). Sweep on the save: 206 needs=3 rows, 176 PASS / 24 live BLOCK, every BLOCK imports 0. ASSUMED: trade preempts construction, so a solvent wanting ally already imports; if solvent-at-0-imports exists (WA-native trade AI incomplete), gate over-blocks. **2026-09-04: the "still growing for an importing member (HUN-like)" leg of the exit is WITHDRAWN** — `coal-prospect-loop` measured HUN at +81 effective while importing (supplied, not needy) and added the ally-side `resource@<r> < 0` term; the leg's probe (4) now lives there | F9 boot passes; a post-fix campaign shows supplier prospecting counters flat while a member sits at needs=3 / 0 avail / 0 imports; no report of a buying ally starved (the importing-member leg moved to `coal-prospect-loop` probe (4)) |
| `prospecting-coop` | MIXED (R65 FAILED, R66 PASSED once) | Coal coop leg reads wrong side (R65); `coop_can_supply` is 1 for everyone (QUEUE 0b) | R65 passes; sold-out test exercised |
| `templates-coverage` | MEASURED (2026-08-18, `2f8cbd51`) | 320 of 334 countries never get a WA infantry template | Criterion to be written at reopen (which tags SHOULD get one) |
| `front-control` | AUDITED, no fix | 3 real `front_control` collisions; per-field vs whole-block resolution unknown; 4 CHI blocks tie at prio 0 | Engine question answered (test or install doc), collisions resolved or accepted in writing |
| `resource-needs` | MEASURED (`3d68a183` 1944.4) | `WA_AI_calculate_resource_need` blind to shortage of a barely-produced resource (ENG, 6 of 8) | Need computed from consumption, not production share; probe passes |

## CLOSED (last 10, then pruned — git is the archive)

| Date | Subject | Note |
| --- | --- | --- |
| 2026-09-09 | `train-variant-choice` | AI train lines run on the cheap trains; the Armored Train only above 10000 in reserve. Campaign leg PASSED on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime): over GER/SOV/ENG/ITA/JAP/USA at ten dates 1940.1-1945.1, ZERO lines on `train_equipment_4` and zero on `_1` after 1941; GER `_2` 52/52 factories from 1942.1 then `_3` 62/71 at 1943.6, ITA `_3` 12/17, SOV `_3` 10/10 at 1945.1. Creation path proved, not just upgrade: no major holds a train line before 1942.1 and GER's first line APPEARS on `_2`. Whole-world control at 1945.1, all 409 countries: 5 train lines, all `_2` or `_3`, zero `_4` anywhere. Armoured branch correctly vacuous - free stock peaks at 7999 (GER 1945.1), never crosses 10000. The `e57efdea` regression (every line frozen on `_1`) is gone. CLOSED BY OWNER ORDER 2026-09-09 with the F9 boot test NEVER RUN - accepted, not discharged; the campaign answers its question empirically (an unresolved trigger inside `can_be_produced` would read TRUE and give armoured trains everywhere, and there are none). |
| 2026-09-09 | `sov-light-support-retire` | The SOV light-support park is retired once it is obsolete. Campaign leg PASSED on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime): `plans.py SOV --templates` shows ZERO deployed divisions carrying `light_support_armor` at 1942.6, 1943.6 and 1945.7; country flag `WA_AI_TEMPLATES_light_support_park_retired = 1` set 1942.1.4.1 and `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE` present at 1941.12, absent from 1942.6 on - the sweep ran. CLOSED BY OWNER ORDER 2026-09-09 with the console harness `wa_abg.1 SOV` NEVER RUN and, more important, the reviewers' stated regression NEVER EXERCISED: the 1942.1.1 leg was to delete a fielded park mid-Barbarossa (31-40 divisions on `5de66942`) and here it found nothing to delete (`army SOV` 321 / 322 / 323 across 1941.12-1942.2, no drop) because `light-support-conversion` Ch.11 had already converted the park off every light-support shape by 1940.12. Both residuals accepted, not discharged. |
| 2026-09-09 | `can-transit-attrition` | CAN builds an army and stops losing it in transit. Own probes (a)-(d), (g), (h) PASSED on `067ef4ac` (2026-08-28) and (a), (b), (h) PASSED AGAIN on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime): 14 of 17 post-1941 CAN deployments still in the OOB at +6 months with ZERO disappearing inside 6 months (bar 10, was about 1 of 16); 11-23 divisions deployed on every save 1943.1-1945.7 (bar 8, was 1-2); all 5 dominions own radio_detection AND decimetric_radar by 1942.1 (bar 3 of 5) and sit at eng_frigate 9 / eng_destroyer 11 by 1944.1 (bar frigate above 5 or destroyer above 6). CLOSED BY OWNER ORDER 2026-09-09 with (e) FAILING for ENG and USA (idle admiral-less fleets 87-118 and 200-292 hulls; CAN itself passes at 17-31) and (f) failing literally - and the (f) bar is itself suspect, the escorts sit where the bleeding is (ENG danger at 1945.6: Western Approaches 13160 / Icelandic Basin 8596 vs Labrador 0 / Newfoundland 0). Residuals accepted, not discharged; F9 boot never run. Recorded as candidates, NOT admitted: the USA escort depot (140 idle frigates in one fleet while its escort TFs are all-destroyer), the missing escort BRIDGE for NZL/SAF/RAJ (the DD-escort template exists only for CAN/USA, the generic is frigate-only), and CAN's unexplained frigate collapse 41 (1945.2) to 6. |
| 2026-09-09 | `rail-admission-churn` | The railway family spends its 12-slot budget on segments that survive, and never discards paid IC. Console leg PASSED for C and D (owner, 2026-09-04, cut-2 build on `barb_supply test.hoi4`: all twelve `PC QUEUED` are level-2 hops, every level-3 and level-4 hop refused - weakest links first; all routes `target=5`). Campaign leg PASSED twice - `916b90f6` (stale under 2 percent of growth) and now campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime), on far stronger evidence: `wa_tlm_pc_stale_kept_n` GER 5 (1941.6) to 46 (1945.7) and `pc_stale_n` 21 against `pc_built_by_type^13` +487 over the war = 4.3 percent (bar 20), with 67 stale judgements of which 69 percent were KEPT. CLOSED BY OWNER ORDER 2026-09-09 with console legs A and B NEVER EXERCISED (both owner runs had an empty `rail`-tag queue, so no `PC VALIDATION` line ever printed) - accepted, not discharged; the campaign exercises A and B from 1941.6 onward, which the console never could. |
| 2026-09-09 | `east-front-rail` | GER builds railway on enemy-owned ground it controls. Leg (1) owner console 2026-09-04 PASSED (`RAILWAY LAND: COMPLETED - 9 targets found`, twelve `PC QUEUED: type=13` on SOV-owned states). Leg (2) PASSED on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime): 4-27 `rail` PC projects on SOV-owned / GER-controlled states 1941.7-1942.12 (Chernigov, Nikolaev, Cherkasy, Pskov class); rail-cache diff raises 61 / 102 / 56 edges with an endpoint in those states per interval; control SOV's own `rail` projects persist 7 to 18; no theatre-air starvation. Recorded, NOT this slug: GER holds ZERO railway projects 1943.3 to 1944.3 and `wa_tlm_pc_built_by_type^13` freezes at 473 for twelve months - a candidate, not admitted. |
| 2026-09-09 | `dday-mulberry` | Mulberry harbours follow the chosen D-Day variant. Criterion MET on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime): variant 89 (Brittany 6572 / Loire 11616), byte-identical 1944.5 to 1944.12. Province 6572 carries no naval_base at 1944.5-6, level 5 at 1944.7-9; latches `a_placed_prov = 6572` / `a_placed_state = 14` equal the target, B mirrors it. At 1944.11 both provinces read naval_base 0 with all four `_placed_` latches zeroed while the target variables stand - placement 1944.6-7, dismantle 1944.10-11, about 120 days as designed. No pre-existing port overwritten; the 5ee2d112 zero-delta signature absent. |
| 2026-09-09 | `aifc-revived-tag-residue` | AIFC book drains a revived tag's parked boost. Criterion MET on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime): `aifc.py` over all 114 saves returns zero CLOSURE MISMATCH, zero residuals, zero REF MISMATCH and zero PENDING+ACTIVE alarms on about 25 tags carrying AIFC state. Annex-to-revive pair ITA-ETH: ITA `pending boost(-400 owed)=ETH` from 1936.11 through 1941.4 (54 consecutive saves) while ETH controls 0 states; ETH holds 3 states / 36 provinces at 1941.5 and ITA's pending book reads empty in that SAME save, closure OK both sides. The 5ee2d112 ITA/ETH +250 signature absent. Residual accepted: the console run `event wa_aifc.1 ITA` (target-exists flags) was never performed - it is not part of the Closed-when line. |
| 2026-09-09 | `sov-cutting-corners-module` | SOV AI designs tanks with the Cutting Corners module. Criterion MET on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime): tech `cutting_corners` 1943.1.7, latch `WA_AI_EQUIPMENT_cc_latched` set 1943.2.1 (one monthly pulse). 2 CC variants at 1943.6, 9 at 1944.6 and 1945.1 (T-70, T-34 (42), T-80, SU 122 x4, T-34 (85), SU-76M). IN PRODUCTION, not just designed: the SOV medium line runs variant 6001 T-34 (42) at 45/45 factories (1943.6), then 6347 T-34 (85) at 52/52 and 6478 SU-76M at 15/15 (1944.6). `SOV_cheap_construction_ai` absent from SOV's ideas at 1943.6, 1944.6 and 1945.7. |
| 2026-09-09 | `usa-military-refactor` | USA military files refactored to dynamic triggers. F9 boot PASSED twice (owner, recorded before parking); probes (a)-(c) PASSED on campaign `4b032e23` (114 monthly BHU saves 1936.2-1945.7, build MEASURED in (2026-09-08 19:29, 20:24] by `wa_tlm_pc_lost_n = 4` + first-save mtime). (a) Torch fires on state conditions, not a date - USA at 30+ divisions from 1942.1, Maghreb held by FRM/FRN/FRT, FRN declares on USA 1942.10.2 and the first USA Maghreb divisions land 1942.12. (b) `WA_AI_pacific_offensive_latched` sets 1943.10.1.1, the exact month USA crossed the 99-division bar (98 at 1943.9, 106 at 1943.10). (c) zero flip-backs in 114 saves; the inputs cross once and never return. Residuals ACCEPTED, not discharged: (d) FAILS - AST never stages in Britain or Norway (16-22 divisions stay in Australia/Papua/Solomons, one division reaches Upper Normandy at 1945.5, eleven months after the landing); (e) FAILS with `allied-division-stability`, which keeps it. Pre-registered navy wall probe PASSED - zero anglo entries in 168 Adriatic and 202 Aegean ever, and 42 Biscay only from 1944.7 with heavy = 0, the month after D-Day landed on that coast. |
| 2026-08-29 | `recruit-loop` | Scripted leader recruitment. Console harness PASSED twice (owner, 2026-08-28: `wa_test_rl2.1 ARG` scope 1 1 1 1 0, 2nd ship verified by a full quit + relaunch + reload). CLOSED BY OWNER ORDER 2026-08-29 with the campaign probes (i)-(iii) and (vi) never run on a scored campaign - that residual is accepted, not discharged. |
