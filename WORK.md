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

### armor-class-handoff — SHIPPED-UNTESTED (2026-08-29)
- SHIPPED-UNTESTED: it changes the ENTRY GATE of a system that has a `WA_TEST_armor_budget`
  harness, so the owner console run is owed before TESTED. Paste `event wa_abg.1 GER` output here.
- Scope: owner request 2026-08-29, from the question "pourquoi GER fait pas de chars moyens sur
  la save 29 juin 40". Intended behaviour: a country whose armour layer is switched on always
  holds at least one armour template — the light class is never closed before the medium class
  can open, and no tag list can gate the medium class shut.
- Symptom, MEASURED (`GER_1940_06_29_02.hoi4`, 1940.6.29, build ≥ `d86d5f5b9`): **3 countries on
  the whole map hold any `WA_*_ARMOR_TEMPLATE` flag** — ENG (heavy+medium), FRA (heavy), SOV
  (light-support+heavy). GER, ITA, JAP, USA and every minor hold none. GER's
  `wa_ai_armor_budget_medium` = 15 against `_light` = 0: the role budget wants 15% armour that
  no template can train. Its 8 armour divisions are `history/` leftovers (`Light Tank template
  E`), and its medium line runs at 15 factories = exactly the
  `WA_AI_PRODUCTION_DEFAULT_tank_floor_medium` floor, because
  `equipment_variant_production_factor` multiplies a need no template creates. 127 medium
  chassis sit in the stockpile with nothing to mount them.
- Cause, MEASURED (`813099474`, uncharted85, 2026-08-28): the light-era boundary moved 1941.1.1
  → 1940.1.1 while the medium gate went from `OR = { DIVISIONS_focus_on_medium ; date > 1941.1.1 }`
  — a universal date fallback — to a closed 7-entry OR of tag/tech literals with none. GER needs
  `ger_medium_tank_chassis_2_3` (Panzer III L) and holds `..._2_2`. Two dates for one handoff,
  moving in opposite directions, and every country outside the 7 entries could never field a
  medium division at all (AGENTS.md principle 1: no generic fallback; principle 2: `has_tech =
  ger_*` is a tag list in a tech costume).
- Their intent, quoted, and why this replaces it rather than reverting: the commit message is
  `"AI now uses multiple tank templates"` and the change's own shape says the rest — the
  `_TEMPLATES_` family exists so the TEMPLATE layer can ask "is the chassis good enough to field
  a division on" separately from the `_DIVISIONS_` family's "which chassis does the doctrine
  push", read by production and research. **Mine covers it because** the accelerator half of
  their list is kept verbatim — a tech leader still mounts mediums before the era boundary, which
  is the behaviour they added — and only its role changes: with
  `WA_AI_CONFIG_switch_from_light_to_medium_armor` as the last OR term the list can accelerate but
  never gate. Reverting would have thrown away that acceleration.
- Single source of truth (the owner's criterion for this session): the era boundary is now ONE
  literal, `WA_AI_CONFIG_switch_from_light_to_medium_armor`, and both sides of the handoff derive
  from it — `WA_AI_TEMPLATES_switch_from_light_to_medium_armor` closes light,
  `WA_AI_CONFIG_TEMPLATES_admits_medium_armor` opens medium. Net −1 trigger, −2 encodings.
  `date` has no validated `constant:` context (registry skill), so the derivation IS the
  mechanism; there is no script-constant form available.
- Commit hygiene, MEASURED and repaired: a CONCURRENT session committing the same two paths at
  04:45 swept this subject's trigger edits into `6654f729f` ("fix(templates): motorised tech gate
  read a tech the majors cannot have"), whose message described none of them. On the owner's
  instruction (unpushed, other session finished) that commit was split: `8d0b2e1c6` re-creates
  the motorised fix alone, with its original author and date, and this subject's ship carries the
  armour work. The split was hunk-classified mechanically, not by hand — 2 hunks theirs, 6 mine,
  none mixed — and the rebuild of base + all hunks was asserted byte-equal to the `6654f729f`
  blobs before anything was written.
- Changed:
  - `WA_AI_CONFIG.txt`: `_TEMPLATES_focus_on_medium_armor` → `_TEMPLATES_admits_medium_armor`,
    same 7 entries plus the boundary as a final OR term. `_TEMPLATES_focus_on_light_armor`
    DELETED (both readers go). `_TEMPLATES_focus_on_heavy_armor` untouched — heavy is optional,
    a country without it keeps medium, so it cannot open a gap.
  - `WA_AI_TEMPLATES_triggers.txt`: `switch_from_light_to_medium_armor` gains
    `has_medium_armor_unlocked` — a HANDOFF, not a cliff. `use_light_armor_templates` and
    `use_light_support_armor_templates` lose the deleted term; `use_medium_armor_templates` and
    `use_medium_support_armor_templates` take the renamed one.
  - Comment repaired (AGENTS rule 7, comments drift): the `[armor-role-budget]` header on
    `use_light_support_armor_templates` said the switch "fires 1941.1.1 for every country";
    `813099474` made it 1940.1.1 for non-SOV and the header had gone stale in a day.
- Widening, stated because the deletion causes it: `use_light_support_armor_templates` loses a
  tag term, so the finite light-support run is open to any country holding a light-support
  chassis. Today those techs are `sov_light_tank_support_chassis_*` only, so it is a no-op, and
  the widening is the intent already written into
  `WA_AI_TEMPLATES_light_support_armor_owns_light_role` ("a second country researching one takes
  the light slot the same way, which is the intent, not a leak"). A generic support chassis would
  make it a real behaviour change.
- Handoff walk at the real cadence (monthly template pulse). LIGHT / MEDIUM = the flag carried.

  | Country class | 1939.12 | 1940.1 | 1941.1 | 1942.1 |
  | --- | --- | --- | --- | --- |
  | GER-like (light + medium unlocked, not in the accelerator list) — HEAD today | light | **none** | **none** | **none** |
  | GER-like — after this change | light | medium | medium | medium |
  | Minor with light only, no medium tech — HEAD today | light | **none** | **none** | **none** |
  | Minor with light only — after this change | light | light | light | light |
  | SOV (boundary 1941.1.1, light-support owns the light role) | light-support | light-support | light-support + medium | medium |

  The GER-like `none` row IS the measured symptom. The minor row is a hole that predates
  `813099474` (the old boundary produced it at 1941.1.1 instead) and is closed here as well.
- Decommission window (lessons rule: a change to which `ai_template` target is enabled is a
  decommission hazard). At the 1940.1 pulse the light flag clears and the medium flag sets in the
  SAME `WA_AI_TEMPLATES_calculate_all_templates` pass, so the engine decommissions whatever held
  `light_armor` — for GER, `Light Tank template E` and its 8 divisions. That decommission is
  ALREADY what HEAD does: `813099474` closes light on the same date with or without this change.
  What changes is that the freed role gets a successor instead of the country being left empty.
- `role_ratio` entry burst, DERIVED at the real cadence (monthly reconcile, `armor_budget_ramp`
  rung 1940 = 15). Per country, not map-wide — `role_ratio` entries are per-country persistent
  strategies:

  | Pulse | Books before | Entries emitted |
  | --- | --- | --- |
  | t0 Dec-1939 | light 10, inf 10 | 0 |
  | t1 Jan-1940 (HEAD) | → light 0, inf 0 | 2 |
  | t1 Jan-1940 (after) | → light 0, medium 15, inf 15 | 3 |
  | t2 Feb-1940 | unchanged | 0 |

  **+1 entry per country, once.** The Jan-1940 pulse was already a rung transition, so this rides
  a burst the ramp's header already bounds (~9 transitions × 5 slots × 2, under 100 per country).
  All terms are monotone (`has_tech`, `original_tag`, `date >`), so no flap: the accelerator needs
  no latch. The pre-existing flicker risk is in the inherited parent
  `WA_AI_TEMPLATES_use_armor_templates` (`num_of_military_factories > 150`), unchanged here.
- Probe (standing, WA_TLM v34, `[armor-class-handoff]`): `WA_TLM_armor_enabled` /
  `_roles_open` / `_gap` / `_gap_n` / `_gap_first_t` / `_gap_t` / `_last_t`, monthly, all AI
  (`WA_TLM_sample_armor_templates`). The invariant is `enabled = 1` with `roles_open = 0`.
  Standing under §3.8 criterion 3 — a system-health invariant, not the mechanism of one fix.
  Second signal: `wa_ai_armor_budget_*` must be non-zero on any country reading `gap = 1`.
  Registry + reading rule: `documentation/WA_TLM_TELEMETRY_SYSTEM.md` §5 and §6f.
- Harness (contract rule 4): `WA_TEST_armor_budget.txt` section B1b re-types the handoff from its
  own terms — `era-boundary / admits-medium / medium-unlocked / light-unlocked` plus a
  `coverage:` line printing `use-armor-templates` against the count of armour flags carried. `1`
  and `0` on that line is the defect, in one row.
- Recorded, NOT admitted as a subject (admission rule — no MEASURED symptom yet): 16 tags can
  reach `has_medium_armor_unlocked` (ast bel can cze eng fra ger hun ita jap nzl pol sov spr swe
  usa) and only 11 have a `common/ai_equipment/<TAG>_tank.txt`. AST, BEL, CAN, NZL and SPR can
  now hold a medium template with no design behind it. **ASSUMED** that this leaves the line
  unfillable rather than falling back to a generic design — there is no `generic_tank.txt`, only
  `generic_naval.txt`. Pre-existing exposure (the old `date > 1941.1.1` fallback reached the same
  five tags a year later); this change moves it 12 months earlier. The probe will name it if it
  matters.
- Verification, script-level, DONE: `python tools/check_templates.py` 0 ERROR 0 WARN (this is the
  join-key diff the lessons reviewer asked for — VALUE-NO-TEMPLATE / TEMPLATE-NO-VALUE over the
  medium ladder and its generated +500 mirror). `check_constants.py`, `check_worklist.py`,
  `check_skill_refs.py` all exit 0.
- Verification OWED to the owner, in an observer game, before TESTED: `event wa_abg.1 GER`
  in 1940.6 reads `handoff: era-boundary=1 admits-medium=1 medium-unlocked=1` and
  `coverage: use-armor-templates=1 armour-template-flags-carried=1`. Control: the same command on
  a 1936 minor reads `use-armor-templates=0` and `flags-carried=0`, which is not a defect.
- Closed when: a campaign save shows **no major with `wa_tlm_armor_gap_n > 1`**, and GER holding
  `WA_MEDIUM_ARMOR_TEMPLATE` with medium-tank divisions in `plans.py --templates` by mid-1940.

### armor-budget-ramp — SHIPPED-UNTESTED (2026-08-29)
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

### armor-ladder-integrity — SHIPPED-UNTESTED (2026-08-29)
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
  `tools/gen_ai_medium_modern_mirror.py` generates the modern-chassis mirror. That is a rewrite of a
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
- Closed when: a campaign shows a light-armour AI that researched light tank destroyers fielding a
  template that contains them (the 4 -> 0 result above, confirmed in a save rather than in a
  simulation).

### mech-window — SHIPPED-UNTESTED (2026-08-29)
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
- Closed when: a campaign save taken during the Polish campaign (1939.9-1939.10) shows GER
  carrying a MOT light-armour value (5100 family, not 5101/5102/5103/5105), no
  `WA_AI_TEMPLATES_mechanization_earned` flag, and a NON-ZERO `mechanized_equipment` stock; and a
  save from 1940.2 or later shows the flip done with no production-line collapse onto mechanized at
  the crossing. Counter-check: the pre-fix reference campaign has GER on 5102 from 1938.10.

### mot-field-hospital — PARKED (2026-08-29)
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
- Closed when: a campaign save taken after GER crosses 300 military factories shows
  `WA_INFANTRY_TEMPLATE = 1104` (or 1103) and `WA_MOUNTAINEERS_TEMPLATE = 2102` (or 2100), the
  flag `WA_AI_TEMPLATES_motorized_hospital_earned` set, and GER infantry divisions carrying
  `field_hospital_mot_company_divisional`. Expected crossing on the current reference campaign:
  ~1941.8 (MEASURED: 300 owned arms factories at 1941.7, 303 at 1941.9).
  Counter-check on the same save: ITA and JAP still on 1003/1004/2000/2002.
- No console harness: the templates calculator has none, and this change is 33 lines of scripted
  effect with no signature or scope change, below the harness-writing threshold. Verification is
  the campaign probe above.

### modern-chassis-tier — PARKED (2026-08-29)
- PARKED 2026-08-29 for the WIP limit, owner's choice, NOT because it is verified: the code is
  shipped and the console run is still owed. Parked rather than another subject because its
  verification is the SAME command as `armor-class-handoff` — `event wa_abg.1 <TAG>`, whose
  section B2 prints the chassis tier — so one owner run still covers both. Paste that output and
  it unparks straight to TESTED.
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
  `tools/gen_ai_medium_modern_mirror.py` → `common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt`
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
- Change 5 — the German Panzer III/IV chain (`32dc70cb4`, shippable alone): `medium_tank_78` was
  enabled by `ger_medium_tank_chassis_2_6`, one tech before the chassis it designs;
  `medium_tank_7` had no zeroing modifier for `2_7` so the ladder never stepped past the Panzer
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

### can-transit-attrition — PARKED (2026-08-28)
- PARKED 2026-08-28 (owner call) to make room for `swi-militia` under the WIP limit; state below
  is intact, nothing was retracted.
- Scope: owner admission 2026-08-27 (candidate validated the same day, owner mechanism
  CONFIRMED against the first verdict). Intended behaviour: what Canada builds REACHES the
  war - divisions survive the transatlantic crossing, and the build rate is worth the name.
- Symptom (MEASURED, `1ac7e4ea`, 61 monthly saves, conveyor-reset series - the valid counter;
  `post_mortem` is a freed-NAME pool, never a death ledger): CAN builds CONTINUOUSLY (queue
  occupied 59/61 months, 16 divisions deployed 1941-46, ~3.1/year, ~5 months and ~18.5k
  manpower each) and **~15 of the 16 leave the OOB (±5)**; standing army pinned 1-2 divisions
  1942-45 on 37→113 arms factories. Not lent (0 `expeditionary_owner="CAN"`, positive
  control works), essentially never in land combat (`last_combat_date` null 47/61 months, 3
  episodes in 10 years); deaths cluster the month AFTER a high at-sea reading on
  transatlantic runs (1943.8: 4/4 embarked, one sea province → 1943.9: 3 lost; destinations
  Dorset/Sussex/Algiers/Gabès); `efficiency_due_to_lost_convoys` 0.875-0.93 on its routes.
  DERIVED: sunk in transit (own at-sea losses never serialised; failed-invasion residual for
  the minority under front orders). Second lever, MEASURED: the build rate is also LOW in
  absolute - 1-2 conveyors, never a backlog, while 153k own rifles bank and CAN→SOV runs the
  campaign's top lend-lease pair (206 656 IC).
- Six-box diagnosis (2026-08-27, this session; three extraction subagents, labels relayed
  unchanged):
  1. Symptom: CAN builds continuously yet its standing army pins at 1-4 divisions with
     near-zero land combat - what it builds leaves the OOB.
  2. Measurement (MEASURED, 77 war saves 1939.9-1946.1, closure vs `army` byte-equal):
     20 true transit losses (at sea -> gone next save), 17/20 North Atlantic; net growth
     -10 (14->4); 1943.8 = 100% of the army at sea. Comparative (7 Allied tags, table in
     session scratchpad `transit-comparative-1ac7e4ea.md`): CAN is the WORST case - 49% of
     its disappearances are at-sea vs ENG 14% / RAJ 16%; USA loses more absolutely (71
     at-sea losses, 1-4/month for 3.5 years) but grows +90; SAF loses 0. A coalition-wide
     pathology with CAN as its extreme, not an isolated case.
  3. Mod state (MEASURED, saves 1943.6/1943.8/1943.9/1944.6): Allied escort = 20 CAN +
     82-122 ENG + 20-40 USA hulls on 3-5 eastern regions vs 100-126 GER raiders covering
     30+ regions; the WESTERN half of the CAN->UK route (Newfoundland/Labrador waters)
     carries ZERO escort missions in all 4 saves; 36-61% of Allied screens parked in
     admiral-LESS fleets, share rising monotonically through 1944; CAN's main active force
     (40 screens) patrols Hudson Bay (danger 0); GER->CAN 1146 convoys sunk 1941.8-1944.5.
  4. Mod decision: the Atlantic escort plan IS armed for CAN (corridor-user includes CAN,
     `WA_AI_CONFIG.txt:1198`; dominance 70-80 + pull -1000 + escort bar at 0), so H1's
     strong form ("unescorted, no plan") is FALSE - the failure is coverage and response,
     the R36 "escorts parked" shape. H2 (shuttle) REFUTED as dominant mode: 9/13 at-sea
     losses died on their FIRST crossing, 4 were multi-crossing (real minority; lower
     bound, monthly sampling). H3 CONFIRMED: a committed CAN keeps no home floor
     (`CAN_FRONT.txt:103`), its only standing requests are fraction-of-army britain
     buffers (`CAN_THEATRE.txt:44` ratio 0.25, `:143` ratio 0.75) - wanted-count ~0 on a
     1-4 division army, and every fresh deployment must cross the Atlantic to reach its
     buffer order.
  5. Script lines: `WA_AI_NAVAL_FACTION_ALLIES.txt:290-327` (corridor dominance/pull the
     engine answers with a Hudson Bay patrol - no WA line steers CAN's navy anywhere, and
     the engine's patrol-near-owned score 500 is uncontested, per the Fix 53b note at
     `05_defines.lua:1082`); `05_defines.lua:1090-1131` (escort score/danger terms, Fix
     53b/86 - present and still insufficient in this campaign); `05_defines.lua:1135-1136`
     (escort screen-share band 0.3-0.7 - unreachable while the screens sit in admiral-less
     fleets); `CAN_THEATRE.txt:44`/`:143` + `CAN_FRONT.txt:103` (build-rate half).
  6. Engine boundary (ASSUMED): whether an escort mission protects an ALLY's troop convoys
     or only the escorter's own (Fix 86 established objectives are per-country
     own-danger-driven); how `naval_dominance` converts into patrol placement; admiral
     auto-assignment to parked fleets; the killer of an at-sea division is never
     serialised, and whether strategic redeployment vs invasion transit die differently is
     engine-internal. An owner-observed crossing with `imgui show ai-strategy` open is the
     only direct view.
- Rival explanations, counted apart (MEASURED): 6/19 losses 1941-46 were NOT at sea (3 last
  seen on Europe/Africa land = ground-combat deaths; 3 in the Americas = disband/merge at
  home); expeditionary transfer refuted campaign-wide (0 lost ids reappear under any of the
  7 tags at N+1 or N+2).
- Candidate levers (PROPOSED ONLY - nothing ships without an owner order; each requires its
  own impact analysis + wa-architecture-reviewer/wa-lessons-reviewer pass): (L1) escort
  response - western-corridor coverage, admiral supply for the parked screens, or escort
  share floor - owns the majority (first-crossing) mode; (L2) shuttle damping is
  `allied-division-stability` Step B, not this slug; (L3) build rate - a CAN standing-force
  floor (front_unit_request or buffer minimum) - secondary, owner-ranked below losses.
- State: L1 SHIPPED 2026-08-27 (owner order "il faut trouver une solution"; both reviewers
  CONCERNS, no CONFLICT, all required amendments applied). Two changes, each with its own
  probe: (C1) `05_defines.lua` `NAVY_PREFERED_MAX_SIZE` 80 -> 25 - vanilla 25 MEASURED at
  install `00_defines.lua:2824` (1.19.2); executes the file's own pre-registered R36
  candidate 3, whose re-measurement condition this campaign satisfies (parked screen share
  36-61% and rising post-Fix-53b/86). "On its own" honoured: no other R36 escort-score
  candidate is bundled - C2 is a different mechanism (fleet placement, not fleet sizing).
  (C2) new `WA_AI_NAVAL_COUNTRY_CAN.txt`: `naval_avoid_region` +1000 on regions 166
  (Hudson Bay) and 246 (Hudson Strait) - ids verified from the in-block `id =` of
  `map/strategicregions/166-*.txt`/`246-*.txt`, not filenames; enable = at war + AI +
  NOT `WA_AI_MILITARY_CAN_home_defense_required` (ahistorical escape: war with USA or a
  threatened homeland re-opens Hudson), abort_when_not_enabled. Caveat carried from the
  archive: a positive avoid is a DETERRENT weight, not a ban. F9 boot test OWED (defines +
  new strategy file).
- State add (C3, owner order + validation 2026-08-27 "je valide avec seuil, implémente";
  both reviewers CONCERNS, no CONFLICT, amendments applied): 4 new files in
  `common/ai_navy` give USA and CAN destroyer convoy-escort templates + matching fleets
  (`<TAG>_ConvoyEscort_DD_1` min 4 / optimal 10 DD, factor 4 < generic frigate 5), active
  only below 100 owned frigates. Owner follow-up 2026-08-27 applied: the threshold is a
  single scripted trigger `WA_AI_NAVY_frigate_mass_reached`
  (`common/scripted_triggers/WA_AI_NAVY_triggers.txt`, new system trigger file - CONFIG
  stays classification-only) read by both country files; the interim registry group was
  removed with the duplication. Root cause the
  files fix: the generic escort template is frigate-only (DD variant commented out by
  d3aaa5d0f on the recorded assumption "escort_fleet_6 covers it" - MEASURED false on
  `1ac7e4ea` for DD-heavy navies: their screens cannot form escort task forces at all).
  Population statement (lessons requirement): the affected class is frigate-poor DD-heavy
  navies bleeding on convoy routes; MEASURED members are USA and CAN (91 at-sea division
  losses between them); ENG is frigate-equipped (its frigates score ~90% of GER sub kills),
  AST/NZL/RAJ/SAF lose 0-13 off-corridor; JAP/GER/ITA sit on the raider side and their
  transit losses were never a measured symptom - if a later campaign shows one of them in
  this class, it enters as its own file under a new admission. ASSUMED, both recorded in
  the file comments: (i) whether ai_navy `allowed` re-evaluates in play AND resolves
  scripted triggers (vanilla/EAI use only static tags there; owner console check with
  `imgui show ai_navy` OWED, and F9 error.log catches an unknown-token failure - fallback
  if static or unresolved: drop the threshold term, factor 4 < 5 remains as soft
  handover); (ii)
  `has_navy_size` counting of under-repair/reserve hulls is undocumented (oracle read,
  install triggers_documentation.md section has_navy_size names type/archetype/unit but
  not fleet-state scope) - near the 100 mark either reading is acceptable. Alternative
  considered and deferred: an archetype gate ("DD-heavy AND frigate-poor" composition
  trigger) instead of original_tag - deferred because trigger support in ai_navy `allowed`
  beyond static tags is exactly the unattested question, and the owner specified USA/CAN.
  Verification (mechanism probe g): escort task forces containing destroyers exist for
  USA/CAN in a war save while their frigate count < 100 (read fleet composition + mission
  from the save via `navy TAG --fleets`; template presence proves nothing - formation is
  the claim), and after any save shows >= 100 frigates, no NEW DD escort task force
  appears. F9 boot test OWED for the ai_navy files (replace_path folder, no Python checker
  covers them - error.log is the only detector).
- Verification (probes with this campaign's method): (a) survival - in the next campaign,
  >= 10 of the divisions CAN deploys after 1941 are still in the OOB 6 months after
  deployment (vs ~1 of 16 on `1ac7e4ea`); (b) standing army - CAN holds >= 8 deployed
  divisions at any save from 1943 on (vs 1-2); (c) the at-sea death clustering signature is
  gone (no month where every embarked division of the previous save has left the OOB);
  (d) control: CAN→SOV lend-lease keeps flowing (the arsenal role must survive the fix).
  Mechanism probes, one per shipped change (avoid weight is a deterrent, not a ban - probe
  the outcome, never assume it): (e) C1 - the parked share falls: admiral-less/region-less
  share of ENG+USA+CAN screens < 30% at two mid-war saves (vs 36-61% rising on `1ac7e4ea`),
  and no single mission-none fleet > 40 ships (vs ENG Fleet 13 at 101); (f) C2 - CAN's
  active fleets hold no strategic_region in {166, 246} at any war save with home safe, AND
  >= 1 CAN or ENG escort/patrol mission operates a western-corridor region (Newfoundland
  Sea 55 / Labrador Sea 50 / Labrador Basin 247) at 2 consecutive sampled saves - fleet
  relocation alone does not create escort missions there (escort objectives are
  own-danger-driven), so (f) measures missions, not just position.
- **Campaign `0767987f` (first post-fix, 2026-08-27, 117 saves 1936.2-1945.10, build
  fingerprint MEASURED: `USA/CAN_ConvoyEscort_DD_1` serialised in-save; closure 14/14 vs
  `army`): coalition improves, CAN itself still fails.** Cross-campaign caveat: one run vs
  one run, different seed, ends 1945.10 vs 1946.1 - directions, not significance.
  - (a) FAIL: 7 post-1941 CAN deployments survive >= 6 months (bar 10); all 5 sub-6-month
    deaths died AT SEA (2 in their deployment month).
  - (b) FAIL, marginal: max 7 deployed from 1943 (bar 8); holds 5-7 through 1943-45 vs 1-2
    baseline.
  - (c) PARTIAL: 7 full-wipe months but ALL <= 1941.12; zero in 1942-45 (baseline had them
    through 1943). As written FAIL, post-1942 clean.
  - (d) PASS: CAN->SOV 195 853 IC cumulative at 1945.6, relief convoys still flowing.
  - (e) FAIL: active fleets DID shrink to the 17-40 median band (mechanism took) but
    admiral-less reserve fleets still grow - ENG Fleet 4 at 121-146 (bar: none > 40), CAN
    79-83% screens idle late-war (bar < 30%). DERIVED: `NAVY_PREFERED_MAX_SIZE` governs
    active-fleet merging, not the new-hull depot; the binding constraint has MOVED to
    admiral assignment / reserve-fleet drainage.
  - (f) PARTIAL: Hudson eliminated (no CAN fleet in 166/246 on any sampled save; CAN
    escorted 243/43 in 1943) - but the western corridor (55/50/247) still carries zero
    Allied escort/patrol while GER raids 247 all campaign.
  - (g) PARTIAL: formation PROVEN - USA 9-13 DD-escort TFs (90-158 hulls, 1944.6 dip to 1),
    CAN 1-2 TFs in 1943; `allowed` resolves the scripted trigger and the dynamic term in
    play (TFs formed below 100 frigates). Threshold cutoff untested (USA peaks 79 frigates,
    CAN 49). CAN stops escorting after 1943.9: its new hulls pool in admiral-less "Fleet 6"
    (20->90 ships) - same mechanism as (e).
  - Coalition deltas (baseline -> this run, DERIVED): total at-sea losses 129 -> 104; USA
    71 -> 42 with net growth +90 -> +264; ENG 11 -> 5; CAN 20 -> 13 but net still -9 on 12
    built; RAJ 13 -> 25 and AST 8 -> 12 (worse, off-corridor routes). Escort-vs-raider:
    261-339 active Allied escort hulls (baseline 60-100) vs GER raid 50-117; GER monthly
    kills collapse to 29-75 in 1945 (peak 468 in 1944.10); GER sub losses >= 388 (327 to
    frigates, 80 to destroyers - the DD escorts kill).
  - Next lever (PROPOSED ONLY, owner decision): the admiral-less reserve-fleet depot is
    now the named binding constraint for (e)/(g)-CAN. Second: western-corridor escort
    presence (f) is untouched by everything shipped so far - engine escort objectives
    never reach 55/50/247.
- **Depot six-box (2026-08-27, "why do new hulls stockpile in reserve", `0767987f`
  saves 1943.6/1943.9/1944.6/1945.6, CAN/ENG/USA; details scratchpad
  `depot-fleet-anatomy-0767987f.md`):**
  1. Symptom: new hulls pool in leaderless, region-less fleets; escort capacity stops
     growing (CAN stops escorting entirely after 1943.9).
  2. Measurement (MEASURED): the depot is the engine's DEPLOYMENT ENTRY POINT - 115/116
     newly produced ships across the 3 tags first appear in it. Drain out of it: ENG 1/131
     ships over 9 months then 0/20 sampled, CAN 0, USA a trickle (21/120). TWO species of
     leaderless fleet: the reserve DEPOT (single raw task force, mission 8, parked in a
     port, never a named template) and ORPHAN POOLS (multi-TF, mission 0, named escort
     compositions = dissolved former active fleets).
  3. Mod state (MEASURED): NOT admiral supply - every tag holds >= 3 UNASSIGNED admirals
     in every cell (incl. skill 6-7: Nimitz, Halsey, Cunningham idle) while depots sit
     leaderless; assigned == led fleets 12/12 cells. NOT command power (CP 7-127 in all
     but one cell). NOT fuel (USA 100% at its own escort collapse). Control: leaderless
     fleets CAN hold missions (ENG escort fleets, 40 frigates, no admiral) - the depot
     lacks mission+region, not a hard admiral prerequisite.
  4. Mod decision: NONE EXISTS - no WA code writes fleets, missions or admiral assignment
     (whole-repo check; the only WA touch is the benign `ai_admiral` XP trait,
     `z_WA_ai_fixes.txt:438`). The mechanism is 100% engine.
  5. Script line: none can exist for the core mechanism - MEASURED against the install's
     effects_documentation.md: script has create_navy_leader / every_navy_leader /
     transfer_navy and NO effect to create a fleet, assign a leader to a fleet, move
     ships between fleets, or set a mission. The reachable mod levers are all INDIRECT:
     defines that raise mission demand so the engine itself pulls from the depot.
  6. Engine boundary (ASSUMED): why the engine leaves available admirals unassigned; what
     triggered the 1943.9-1944.6 fleet-dissolution wave (CAN's two led escort fleets were
     dissolved INTO Fleet 6 - that dissolution, not intake starvation, is what ended CAN
     escorting; USA's orphan pool re-drained 98 ships into led escort fleets by 1945.6,
     CAN's never did); mission id 9 (unknown to the mission map). An owner run with
     `imgui show ai_navy` during the dissolution window is the only direct view.
  - Rival named and killed: "admiral shortage" (H-A) and "fuel" (H-B) both dead by
    measurement above; H-C (deployment sink with a near-closed engine drain valve) stands.
- **Radar-lock six-box (2026-08-27, owner symptom "dominions stuck on Egret/Tribal
  classes", `0767987f`):**
  1. Symptom: the five UK dominions never field a frigate past Egret or a destroyer past
     Tribal.
  2. Measurement (MEASURED, saves 1943.6 + 1945.6): CAN/AST/NZL/SAF/RAJ all own ZERO radar
     techs (radio_detection/decimetric/improved absent, none in progress, no alternate
     name) and sit at exactly eng_frigate_5 / eng_destroyer_6 in BOTH saves - a static
     ceiling, byte-identical across the five. Positive control: ENG owns the radar chain
     (1936/1938/1939) and advances frigate 9->10, destroyer 10->12 over the same window.
  3. Mod state: `eng_frigate_6`+ (Black Swan on) and `eng_destroyer_7`+ (J/K/N on) carry a
     HARD `dependencies = { decimetric_radar = 1 }` (`naval_eng.txt:314-316`, `:1063-1065`)
     - without the radar the AI cannot research them regardless of ai_will_do.
  4. Mod decision - a DOUBLE lock, both deliberate-looking: (i) research path:
     `WA_AI_RESEARCH_needs_radar` = major OR strategic-bombing airforce
     (`WA_AI_RESEARCH_electronics.txt:22-27`; the airforce trigger is ENG/USA only,
     `WA_AI_CONFIG.txt:161-166`) - a dominion fails both terms, so radio_detection and
     decimetric_radar ai_will_do = 0 for it; (ii) gift path: ENG's radar
     `on_research_complete` grants the tech to subjects but its limit EXCLUDES
     `autonomy_dominion`/`autonomy_colony` (`electronic_mechanical_engineering.txt:169-189`)
     - only integrated subjects (UKE) receive it.
  5. Script lines: `WA_AI_RESEARCH_electronics.txt:22-27` (the gate that zeroes dominion
     radar research) and `electronic_mechanical_engineering.txt:100-110/:172-181` (the
     gift filter). Candidate levers, PROPOSED ONLY: (L-a) widen `needs_radar` with an
     escort-capability term (`WA_AI_CONFIG_focus_on_escorts` or
     `has_navy_size = { type = screen_ship size > 10 }`, the same shape `needs_asw` already
     uses at `:49-59`); (L-b) extend the gift to dominions (the autonomy exclusion looks
     deliberate - legacy-gate trace owed before touching); (L-c) drop the hard radar
     dependency from hull techs (changes design intent, not recommended).
  6. Engine boundary: none - the whole mechanism is mod script; nothing here is ASSUMED.
  - Interaction with the shipped DD-escort fix: the lock caps hull QUALITY, not frigate
    existence (Egret/frigate_5 stays buildable - CAN holds 49). The ASW-relevant classes
    (Black Swan on) are exactly the locked ones.
- State add (L-a, owner order 2026-08-27 "étends needs_radar à
  WA_AI_CONFIG_focus_on_escorts"; architecture OK, lessons CONCERNS - all three required
  items resolved): `WA_AI_RESEARCH_needs_radar` gains `WA_AI_CONFIG_focus_on_escorts`
  as third OR term (`WA_AI_RESEARCH_electronics.txt:22`) - the six-box's "major OR
  strategic-bombing" description above is the PRE-fix state. Resolved items, all
  MEASURED: (1) design layer admits the dominions - `ENG_destroyers`/`ENG_escorts`
  `available_for` AST/CAN/NZL/RAJ/SAF (`ENG_naval.txt:41-52`, `[commonwealth-handoff]`),
  role variants enable on `has_tech = eng_frigate_6`+, so TECH+DESIGN+ROLE line up once
  radar unlocks; (2) the gift's dominion exclusion is deliberate by its own commit
  (`d69a92b94` "Integrated puppets get radar and AA tech from master") and stays
  untouched - the fix widens the honest research path instead; (3) accepted explicitly:
  the term also admits generic-tree Allied minors (BEL/GRE/NOR/...), for whom radar
  enables no hull - a research-slot dilution taken knowingly (radar cost 2.5+1.25 on
  factor 5). Residual, stated: an escort navy OUTSIDE the Allies stays radar-locked
  (is_escort_navy is faction-gated) - no worse than pre-fix. Regeneration-safe: the
  ai_will_do replacers re-emit the trigger NAME, never its definition. Verification
  (probe h): next campaign, >= 3 of the 5 dominions own radio_detection AND
  decimetric_radar by 1942.1, and >= 1 dominion's best eng_frigate tech > 5 or best
  eng_destroyer tech > 6 by 1944.1 (vs frozen 5/6 on `0767987f`). F9 boot test owed
  (trigger edit).
- **Campaign `067ef4ac` (second post-fix, 2026-08-28, 115 saves 1936.2-1945.8, carries BOTH
  fix waves - fingerprint MEASURED: dominions own 6 radar techs vs 0 on `0767987f`, and
  `USA/CAN_ConvoyEscort_DD_1` task forces serialised; closure 14/14 vs `army`). The
  subject's OWN probes (a)-(d) now all PASS; the residual failures are elsewhere.**
  Caveat: run ends 1945.8 vs 1945.10/1946.1 - 2-5 months shorter than the comparators.
  - (a) PASS: 17 post-1941 CAN deployments survive >= 6 months (bar 10; 1 then 7 before).
  - (b) PASS: max 23 CAN divisions deployed from 1943 (bar 8; 1-2 then 7 before); CAN grows
    monotonically 10->23 and ENDS ABOVE its 1939 strength - net +9 after -10 and -9.
  - (c) PASS: 1 wipe month (1939.10, one division at sea) vs 7 before.
  - (d) PASS: CAN->SOV 146 288 IC at 1945.6 and climbing (+78k in twelve months).
  - (h) PASS with margin: 5/5 dominions own radio_detection AND decimetric_radar by 1938
    (bar: 3/5 by 1942.1), centimetric by mid-1940; hulls unfreeze from frigate 5 /
    destroyer 6 to frigate 10 / destroyer 12.
  - (e) SPLIT - the depot pathology MOVED: CAN PASS (idle screens 22-39%, largest idle
    fleet 17-31 hulls vs bar 40 - the 79/83% catastrophe is gone), ENG FAIL (idle fleets
    87-118), USA FAIL HARD (200-292; at 1945.6 one admiral-less region-less fleet holds
    292 hulls incl. 140 frigates + 100 destroyers while four all-destroyer escort TFs run).
  - (f) PASS on Hudson (zero CAN fleets in 166/246 across all 32 monthly saves swept);
    western corridor literal FAIL, but the bar itself is now suspect: at 1945.6 ENG danger
    reads Western Approaches 13 160 / Icelandic Basin 8 596 vs **Labrador Basin 0 /
    Newfoundland Sea 0**, no convoy sunk there since 1944.12 - the escorts sit where the
    bleeding is. DERIVED: rewrite probe (f) around the danger map, not fixed region ids.
  - (g) PASS for CAN: convoy_escort task forces present in 31 of 32 saves (2-5 TF, 20-70
    hulls, composition `CAN_ConvoyEscort_DD_1` x2-3) - the wave-1 "CAN stops escorting
    after 1943.9" failure is fixed. Threshold: USA crossed 100 frigates at 1944.5 (101)
    and its DD-escort TF pool stayed flat at 11 while every escort TF added afterwards was
    the generic frigate template (+2) - consistent with the cutoff, but ASSUMED not proven
    (the pool was already flat for 16 months before the crossing). The two unattested
    assumptions stand; owner `imgui show ai_navy` check still OWED.
  - Coalition deltas (MEASURED, pre-fix -> wave 1 -> now): total at-sea losses
    **129 -> 104 -> 62**; CAN 20 -> 13 -> **5** (last transit loss 1942.1, zero in the final
    43 months); USA 71 -> 42 -> 21 (net +272); RAJ 25 -> 11; AST 12 -> 9; NZL 5 -> 4; SAF 0.
    ENG is the exception and rose 5 -> 12, on far higher exposure (peak 35% of its army at
    sea vs 19%). GER convoy kills over the comparable 24-month window fall to ~1/3 of the
    baseline for every victim EXCEPT CAN (122 -> 146). GER sub losses >= 392, now 366 to
    frigates / 47 to destroyers.
  - New findings, each a candidate subject rather than this slug (admission rule - do NOT
    fix on the way past): (1) the USA depot - 140 idle frigates in one fleet while its
    escorts are all-destroyer; (2) the four other dominions got the TECH but no escort
    BRIDGE - NZL and SAF ran zero convoy_escort task forces all campaign and RAJ lost its
    only one, because the DD-escort template exists solely for CAN/USA and the generic is
    frigate-only; (3) MEASURED anomaly, unexplained: CAN's frigate force collapses 41
    (1945.2) -> 9 (1945.4) -> 6 during a GER raiding surge, and CAN's last escort TF is
    gone at 1945.8 - ASSUMED combat loss, no warship-loss counter exists in a save.
- Closed when: the shipped fix passes F9 plus (a)-(f) in a campaign, or the owner accepts
  a written no-fix ruling on a named engine boundary.

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

## PARKED

A real MEASURED symptom, no owner and no fix in flight. One line each; reopen by moving to
OPEN with a session of its own.

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

### usa-military-refactor — PARKED (2026-08-27)
- Parked 2026-08-27 (WIP limit, owner choice; templates-admission enters). State at parking:
  SHIPPED-UNTESTED debt fully discharged (F9 boot PASSED twice), awaiting campaign probes
  (a)-(e) only. Reopen when the next scored campaign lands.
- Scope: owner request 2026-08-27 ("refactorise les fichiers WA_AI_MILITARY_COUNTRY_USA_* —
  noms avec conventions, triggers dynamiques ouverts à l'ahistorique, éviter les dates en dur,
  standardiser constantes/ratios; garde l'anti-shuffling à l'esprit; supprime les stratégies
  situationnelles type hold_okinawa").
- Shipped, all four COUNTRY_USA files rewritten + control panel + one CONFIG fix:
  (1) every block renamed `WA_AI_MILITARY_COUNTRY_USA_<DOMAIN>_<descriptor>` (doc §5 rule 4)
  with purpose/range/policy/domain headers; the two genuine always-ons carry `# always-on:`
  (abandon_turkey, ignore_south_america — the latter was `date > 1936.1.1` in disguise).
  (2) All 12 hard dates removed: new control-panel triggers
  `WA_AI_MILITARY_USA_pacific_offensive_ready` (phase flip; europe_first/pacific_offensive and
  dont_invade_japan_yet/pacific_offensive are exact NOT-mirrors) and
  `WA_AI_MILITARY_has_minimum_expeditionary_army` (num_divisions > 29 + home safe — owns the
  29/30 band, 6 sites; deathtrap brake is its NOT-mirror). Torch-done gate = metropolitan
  foothold, invade-Japan-execute = pacific_ready + (JAP surrender_progress > 0.02 OR Philippine
  foothold). ASSUMED, stated in the trigger header: the arms cross once and stay; if a campaign
  shows flapping, latch on a country flag (the flap surface is a JAP-only-war USA near 50 div).
  (3) Dedup with the halvings ACCEPTED IN WRITING (lessons CONFLICT items 1-2, resolved by git
  archaeology 79d64f6ff): bad_torpedos_suck was born `date < 1943.9` (torpedo era, calendar-only
  reason) and SUMMED with europe_first while both armed — twin deleted, one suppression at the
  economy band, rationale at each survivor's header; torch preparation/landing pairs (byte-
  identical payloads, both armed from 1942.11) merged — post-landing doubling deliberately
  halved; the FRONT merge LOSES the 2-month careful-prepare-only window (stated; engine
  invasion-prep timer is the remaining staging delay).
  (4) Anti-shuffling: buffer_pacific shares resized per state (was an aggregate demanding ~107
  of a 56-division army), and ONE order_id PER ENTRY (9105-9119) — the engine doc gives same-id
  entries one SHARED ratio, so the old ten-ratios-on-9101 was undefined; order_id never
  serialises, split = ASSUMED hygiene (REGION_ITALY rule). Britain buffer variants stay a
  single logical buffer on id 1.
  (5) `hold_okinawa` DELETED (owner order — a JAP-war block suppressing the RIT front was a
  situational tag-payload hack; the theatre-distributor damping owns the anti-pull intent).
  Remaining tag payloads are target enumerations (invade books, balkan minors), not hacks.
  (6) The 8-tag Allies suicide-invasion brake re-homed to FACTION_ALLIES_INVASION on the
  `is_western_invasion_pool` archetype, membership term dropped (audience preserved). Fixed the
  archetype's pre-existing typo `AUS` (landlocked Austria) → `AST` (Australia): 8 reader blocks
  had EXCLUDED Australia from the Allied invasion pool — audience change to verify next
  campaign (AST gains, Austria loses).
- Reviews 2026-08-27: architecture CONCERNS (5 — bar promoted to named trigger; buffer comments
  rewritten to the share-one-ratio model + per-entry ids; torch header states the careful-window
  loss; audience narrowing dropped; faction-block name kept on the FILE's own convention
  (ALLIES_<desc>_INVASION, its siblings' style) against the reviewer's variant) + lessons
  CONFLICT (all required items applied: archaeology done, halvings folded-or-justified, per-
  sector buffer rationale, war-facing term added to both bars, F9 obligation recorded).
- **NAVAL leg shipped 2026-08-27 (owner order "fais pareil sur WA_AI_NAVAL_COUNTRY_USA.txt").**
  Same pattern: legacy_USA_ noise stripped (18 blocks renamed, all cross-references updated —
  PHASE5 mirror comment, FACTION_ALLIES incl. one stale "known residual" corrected to RESOLVED,
  ENG file, system doc); 8 hard dates → the two triggers + state gates (threat > 0.50 for the
  pre-war Pacific posture; strike bases on peacetime-or-JAP-war; death-trap walls released by
  the phase trigger, held-while-weak ruled INTENDED caution with the enemy-state arms as the
  state-side release, stated at the site); bad_torpedos naval twin (strict SUBSET, 19 shared
  regions summing 4000) deleted — same accepted-halving ruling; torch pair merged into
  `torch_corridor` with the [atlantic-naval] Biscay audit RE-WALKED for the new state-keyed
  windows (−2000 still outvoted wherever the GER-war walls co-fire; the ITA-only-war no-wall
  corner is pre-existing and unchanged). **Phase flip now LATCHED one-way** (lessons item):
  `WA_AI_MILITARY_update_usa_phase_latch` on the monthly pulse sets
  `WA_AI_USA_pacific_offensive_latched` once the live conditions hold at a tick; the public
  trigger reads flag-OR-live — worst residual flap = one flip-back inside the first month.
  Reviews (NAVAL round): architecture OK (2 wording notes applied: the shared-regions list is
  SW-Pacific too, not just Indian-Ocean — ASSUMED the old 1943.6-1944.8 wall gap was date
  residue, campaign probe = USN presence in regions 84/88 during a Solomons-type war; the
  Europe-only-war strike-base handoff goes to the Faction western anchorage) + lessons
  CONCERNS (all 4 required applied: enemy-state release stated, latch implemented, audit
  re-walked, PHASE5-mirrored enable diff-verified byte-untouched).
- **F9 boot PASSED (owner, 2026-08-27) on the refactor build** — discharged the land+naval
  CTD-class debt, the comp-gauge v33 change and the AIFC merge-bar effect edit.
- **Factorisation batch SHIPPED 2026-08-27 (owner order "tout" on the promotion survey;
  survey table delivered as a file the same day).** Five commits: (1) RETIRED 7
  faction-duplicated USA blocks — the Adriatic was summing +8000 and Biscay +6000 on USA's
  own duplicate walls; strategic-bombing china/asia self-doubling folded into the japan twin;
  double RIT entry trimmed. NOT retired, stated at site: north_africa_focus (faction twin
  carries a hard date + ITA/ITL controller list — the Case-Anton corner would be uncovered),
  no_balkan_hops (faction twin is minors-only), unit_clumping_fix (state-vs-region precision
  unverified). (2) Phase trigger GENERALIZED (`WA_AI_MILITARY_pacific_offensive_ready`, USA_
  prefix dropped; latch widened to anglo majors). (3) PROMOTED with same-commit country-copy
  deletion: NAVAL aegean_hostile_coast + western_pacific_trap (25 regions — replaces the USA
  pair AND trims 25 entries of ENG's 68-region war-GER blanket; ENG is now phase-released
  where it was walled all war) + the uninvaded-ally-waters courtesy trio + St. Lawrence →
  DEFAULT; THEATRE britain_invaded_priority (ENG_all_in's britain pair trimmed); FRONT
  liberate_britain; INVASION britain_first_no_side_shows + pacific_side_shows_wait (ENG twin
  trimmed of the 5 shared targets). (4) INS ownership USA arm made conditional (sfhb
  pattern) so the faction deathtrap guard re-arms after the phase flip. (5) **Biscay
  correction**: the dedup turned the historically-inert Torch −2000 on region 42 LIVE
  (net 0 = the Bay would have opened, a design change nobody decided) — removed to preserve
  observed behaviour; **Biscay DECIDED 2026-08-27 (owner): the wall
  stays - Torch does not open the Bay; settled at the site**. Deferred with reasons (survey file): defend_britain
  DIPLOMACY (coupled to commonwealth-handoff's CAN guard), commit_to_europe partial,
  reinforce_normandy Balkan split, pacific_islands, ignore_south_america→archetype, the
  full ENG-blanket retirement and the two coalition-reaching COUNTRY_ENG blocks (the
  ENG-refactor chantier), sicily sign conflict (design accounts for it via the bridge +50).
- Reviews on the batch 2026-08-27: architecture CONCERNS (2 — provenance stripped from the 10
  new headers per rule 7; the pre-rename latch flag is now MIGRATED in the latch effect, so a
  resumed save keeps its latch) + lessons CONCERNS (3 — (i) archaeology done: at the authoring
  commit 79d64f6ff region 168 was already written 3× and 42 5× across independently-named
  blocks with no comment claiming a stacked total — the sums were ACCRETION, not calibration,
  so the single faction wall at the type's band is the honest form; (ii) the new F9 line below
  is that item; (iii) the courtesy trio's tag-anchored gates now carry their ASSUMED-FACT
  sentences at the site — UKO holds Malaya, ENG/NZL hold 636/726, CHI/PRC are the two Chinas).
  Latch flap bound restated at real cadences (engine-eval flips possible only inside the first
  month, zero after the latch). Pre-registered campaign probe for the halvings: `navy --fleets`
  region lists — anglo fleets do NOT newly operate in 168 Adriatic / 42 Biscay / 202 Aegean
  while those walls' conditions hold (a fleet parked there post-change = the halving was
  load-bearing, re-raise the wall).
- **F9 boot PASSED on the promotion batch too (owner, 2026-08-27)** — discharges the second
  CTD-class debt (USA+ENG deletions, 5 new FACTION blocks, 1 DEFAULT block, the latch
  migration). The build is campaign-ready; owner is weighing the two-state merge-bar
  alternative and the remaining deferred promotions.
- Verification: F9 boot passes with no new error.log ai_strategy entries. Campaign probes:
  (a) Torch arc fires on state conditions (north_africa priority armed when the Maghreb is
  enemy-held and USA ≥ 30 div — probe via control + plans.py, no date to check); (b) the
  Pacific flip happens (europe_first suppressions absent in a save where USA > 99 div or GER
  dead, invade-JAP book flipped); (c) r-flap watch: the phase pairs do not oscillate across
  consecutive monthly saves (same discriminator as the (i) transit probe); (d) AST appears in
  Allied invasion-pool behaviours (norway/D-Day staging blocks reachable); (e) USA buffer order
  instances stable per ocean (shared probe with allied-division-stability).
- Closed when: F9 passes AND probes (a)-(c) pass in the next campaign, or a regression traces
  to a specific removed date/merge and is fixed under this slug.


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
| `analysis-tooling` | TESTED, parked 2026-08-27 (slot freed for `can-transit-attrition`, owner admission). All three tools shipped+validated (comp rungs v33 F9-booted; aifc.py DEAD-TAG banner; plans.py --invasions) | comp gauges floored to 0 under 5 armour divisions; aifc.py printed dead tags as live churn; type-3 targets unreadable | v33 campaign probe: a major with 1-4 armour divisions reads `comp_armor` = that count, and `tlm` never reports comp_* FROZEN on live majors |
| commonwealth-handoff | OPEN (parked 2026-08-27, owner order - WIP limit; exemption lever live since 2026-08-25) | Handoff inverts: availability bars read TOTAL divisions, not in-theatre (24933fb9: RAJ reads available with 3 div in East Africa on 76 total, ENG back-fills 14); every bar single-threshold, flap lever documented in the block (git history of this file) | Delegate missions armed and manned (R72 legs), Indian army in East Africa/El Alamein, no dominion dockyard nailed by an unbuildable design |
| `aoi-border-garrison` | OPEN, both legs shipped 2026-08-27, parked 2026-08-27 (WIP limit, owner choice — slot given to `aifc-traction`). Leg 1: `AXIS_abandon_east_africa` FRONT/THEATRE retargeted off region 17 (corridor {380,381} + s.r. 217), new `_colony_THEATRE` -200 gated `NOT owns_east_africa_colony`, ITA buffer widened to {550,559,271,909,910}, family gate extracted. Leg 2 (sea reinforcement): buffer ratio 0.10→0.20, trigger `east_africa_sea_route_hostile` (Suez 923), `owner_cut_off_THEATRE` -200, `naval_avoid_region` +1000 on the 5 Red-Sea/Indian-Ocean lanes. Campaign `24933fb9`: colony holds 37 months vs 2 pre-fix; (b) PASS (EA front orders manned), (d) PASS (0 GER div), (c) marginal FAIL (1-2 strays, Kurdufan buffer leak order 9607 unexplained), (a) FAIL as written / PASS on buffer population (43-57 % border). OWED: F9 boot (new ai_strategy blocks), owner imgui (cut-off gate armed/released vs Suez), §12 telemetry re-instrumentation before next scoring | ITA 9/9 AOI divisions pinned to {550,559} port buffer, zero EA front orders for ITA and ITS (`15176ce6` 1940.9-10); leg 2: AOI grows 9→11-23 by 1943 by sea past the Allied navy (`24933fb9`; ITS never released, growth = external) — engine never refuses the route (`MAX_ALLOWED_NAVAL_DANGER 80` vs ceiling 50) | (a) >= half AOI divisions in border states {271,909,910,550}, (b) EA front order for the AOI holder, (c) zero ITA/ITS div in 217/380/381, (d) zero GER div in AOI, (e) no sea growth while Suez hostile (~0.20 prepositioned at entry), (f) reinforcement resumes once the Axis takes Suez. Full record: git log `[aoi-border-garrison]` + this file's history |
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
| `prospecting-coop-solvency` | SHIPPED 2026-08-27, parked same day (WIP limit; F9 boot test OWED) | Owner request: coop prospecting must check the needy ally can IMPORT. GER 1945.7 (`15176ce6`) re-prospects coal on 20 164 effective; sole weight = coop branch; ITA at -1046 imports 0 with 0 civs avail. Shipped: ally-side gate in all 9 `WA_AI_allies_need_<r>` (avail>0 OR `resource_imported@<r>` > 0 — the import leg answers the lessons CONFLICT on saturation collapse). Sweep on the save: 206 needs=3 rows, 176 PASS / 24 live BLOCK, every BLOCK imports 0. ASSUMED: trade preempts construction, so a solvent wanting ally already imports; if solvent-at-0-imports exists (WA-native trade AI incomplete), gate over-blocks | F9 boot passes; a post-fix campaign shows supplier prospecting counters flat while a member sits at needs=3 / 0 avail / 0 imports, AND still growing for an importing member (HUN-like); no report of a buying ally starved |
| `prospecting-coop` | MIXED (R65 FAILED, R66 PASSED once) | Coal coop leg reads wrong side (R65); `coop_can_supply` is 1 for everyone (QUEUE 0b) | R65 passes; sold-out test exercised |
| `templates-coverage` | MEASURED (2026-08-18, `2f8cbd51`) | 320 of 334 countries never get a WA infantry template | Criterion to be written at reopen (which tags SHOULD get one) |
| `front-control` | AUDITED, no fix | 3 real `front_control` collisions; per-field vs whole-block resolution unknown; 4 CHI blocks tie at prio 0 | Engine question answered (test or install doc), collisions resolved or accepted in writing |
| `resource-needs` | MEASURED (`3d68a183` 1944.4) | `WA_AI_calculate_resource_need` blind to shortage of a barely-produced resource (ENG, 6 of 8) | Need computed from consumption, not production share; probe passes |

## CLOSED (last 10, then pruned — git is the archive)

| Date | Subject | Note |
| --- | --- | --- |
| 2026-08-29 | `recruit-loop` | Scripted leader recruitment. Console harness PASSED twice (owner, 2026-08-28: `wa_test_rl2.1 ARG` scope 1 1 1 1 0, 2nd ship verified by a full quit + relaunch + reload). CLOSED BY OWNER ORDER 2026-08-29 with the campaign probes (i)-(iii) and (vi) never run on a scored campaign - that residual is accepted, not discharged. |
| 2026-08-29 | `armor-role-budget` | Constant per-role armour share + one open role at a time. Owner console 2026-08-28: harness run 1 PASSED (i), (vii) and (ii) partially (two open roles, not three); probe (vi) PASSED via `imgui show ai_division_production` on SOV 1943.11. CLOSED BY OWNER ORDER 2026-08-29 with (iii), (iv), (v), (viii), (ix), (x) NEVER RUN, including the re-read that was to confirm the template-flag join reads medium 17 / heavy 8. |
| 2026-08-29 | `rail-corridors` | Strategic corridor railways (free AI pathfinding cheat, level-5 rail so redeployment stays off the sea). Corridors 1-8: owner-tested and functional in-game 2026-08-27. Corridor 9 San Francisco-Washington (41 provinces, 40 edges, 16 gate states) SHIPPED 2026-08-27 and CLOSED BY OWNER ORDER 2026-08-29 WITHOUT its console run - `event wa_test_rail.19` and the supply-mapmode check were never performed. Campaign probe stays folded into the F-checks: `WA_rail_corridor_*_built` flags + level-5 track. |
| 2026-08-27 | `lend-lease-observability` | `lendlease.py` + WA_TLM v32 recipient matrix. Campaign `1ac7e4ea` (first v32): matrix populated (739 pairs, 65 donors), donor↔recipient closure exact on send-counts and to 2 units in 1.31M on amounts. Console harness waived by owner closure order 2026-08-27. Known limits recorded in git history of this file. |
| 2026-08-27 | `silo-breadth` | Breadth-first silo walk. Harness owner-PASSED 2026-08-24; campaign `1ac7e4ea`: GER 28 / ENG 19 / JAP 13 / USA 13 / SOV 12 built levels vs per-state cap 6 → ≥ 2 states each, SOV grew 7→12 (no first-state stall) against scripted need 17. |
| 2026-08-27 | `rk-no-divisions` | RK training brake. PASSED on `24933fb9` AND `1ac7e4ea` (7 RK tags with no `units` section, ALB flat at its 3 scripted starters); boot discharged by the F9 campaign entries; error.log id check waived by owner closure order. |
| 2026-08-27 | `uk-truck-supply` | ENG truck stock PASSED twice (`24933fb9` 8-19.6k, `1ac7e4ea` 9.4-12.6k own-built motorized vs bar 1500). Africa hub-motorization leg not save-visible (needs a WA_TLM gauge at the hub site) — residual accepted by owner closure order. |
| 2026-08-27 | `raj-trucks` | CAMPAIGN-OK since `8f9b5653` (all three positive legs + control). SAF tier residual accepted in writing by owner closure order 2026-08-27. |
| 2026-08-23 | `na-corridor` | NA corridor logistics (rail/depots/ports/theatre air bases, Fix 95–135). Human validation: tested and functional. Absorbed R9, R13, R52, R60, R68, R69, R71, R77, R78, R81, R91, R96, QUEUE 0q/0r/0m/0i. |
| 2026-08-23 | `med-axis-posture` | Axis Mediterranean posture (Afrika Korps, Tunis, Italy, Ethiopia, Med fleet, convoy interdiction; Fix 96–137). Human validation: tested and functional. Absorbed R17, R61, R63, R64, R74–R76, R80, R82, R83, R92, R94, R97, QUEUE 0t/0h/0f/0g/0. |
