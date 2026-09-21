# Medium -> modern armour switch: duplicate role entry diagnosis and the park-brake experiment

Date: 2026-09-21. Branch `ai-rework`. Subject it serves: `modern-switch-amorce` in `WORK.md`.
Status: **experiment in progress - one control run (`test6`) is owed.** No mod code was shipped.
No `WORK.md` subject was opened (admission rule); the owner decides what enters.

Labels, as everywhere in this repo: **MEASURED** = read from a named save, game file or mod file.
**DERIVED** = computed from a MEASURED. **ASSUMED** = not verified. Save readings were produced by
an extraction subagent; its labels are relayed without upgrade.

Engine version: the install reads **1.19.3.0** since 2026-09-18 (**MEASURED**,
`launcher-settings.json` `rawVersion`). `AGENTS.md` and `wa-engine-reference` still say 1.19.2 -
stale. Every binary/doc reading below is of 1.19.3.0, the version that produced the saves.

---

## 1. Verdict so far

1. Two role entries on one role is **not undefined in practice**: the engine works per ENTRY. Each
   entry has its own lottery weight, its own target list, its own arrow (currently targeted
   template). **MEASURED.**
2. The park brake `can_upgrade_in_field` does nothing where WA put it (on the modern, i.e.
   destination, targets). Vanilla and Expert AI put it on the SOURCE target, 7 of 7 and always.
   **MEASURED.**
3. Live experiment, five runs from one save: a source kept alive in a *separate* entry freezes
   everything (park, recruits, production need) whatever the brake says; a source inside the *same*
   entry with no `replace_with` holds nothing; a source inside the same entry **with a
   `replace_with` edge** produced the wanted shape for the first time - park held one rung up,
   recruits on a higher rung, modern chassis production requested. **MEASURED** for the facts,
   **ASSUMED** that the brake is the cause until the control run (`test6`, brake open) is read.
4. The symptom the subject started from is live on the current build: converted divisions are
   nearly tank-less (17 divisions holding ~150 modern chassis for ~2 550 required, medium tanks
   stripped from ~197 to ~8 per division). **MEASURED.**
5. A static medium -> modern twin mapping is the already-failed "+500 mirror" design (unbuildable
   slots, `WORK.md` `modern-chassis-tier` Defect A). If the edge is confirmed, the mapping problem
   is the next thing to solve (section 7).

---

## 2. What the engine does with two entries on one role

| # | Claim | Label | Source |
| --- | --- | --- | --- |
| 1 | The unit is the role ENTRY (group), not the role token: one line per entry with `prio / weight / pick %`, its own target list, its own arrow. | MEASURED | `hoi4.exe` strings, contiguous block: `AI template roles` / `%s (prio: %s, weight: %s, pick: %s%%)` / `Target templates:` / `%s %s (upgrade prio: %s)` / `Best (all): ` / `Best (role): ` / `There is no existing template with correct role` / `replace with '%s' at match %s (target_min_match: %s)` |
| 2 | Both `medium_armor` entries sit in the XP lottery; factor 0 gives `prio 0 / weight 0 / pick 0%` in both directions across the latch. | MEASURED (owner imgui 2026-08-30) | `WORK.md` `modern-chassis-tier`, Defect B |
| 3 | Each entry keeps its own arrow even when both declare the same role. | MEASURED (owner imgui 2026-09-21, arm 0: medium entry arrow on the 21718 target, modern entry arrow on a modern target, same instant) | section 5 |
| 4 | A disabled target does not exist for the engine; its `can_upgrade_in_field` can never be read. | MEASURED | install `common/ai_templates/_documentation.md`, `enable` comment |
| 5 | Role-level weight 0 only stops XP spending. An ENABLED target in a weight-0 entry is still consulted, and its best match keeps the role. | MEASURED (arm 0, `test1`-`test3`) | section 5 |
| 6 | `Best (role)` is scoped by role TOKEN, `Best (all)` by nothing: the modern target's best existing match is the fielded medium template. | DERIVED | claim 1 + lessons log 2026-09-04 |
| 7 | `replace_with` resolves only inside its own entry. | MEASURED (owner live 2026-08-29) | lessons log, "replace_with must resolve inside its own role group" |
| 8 | Vanilla never gives one country two entries on one role, except nine Chinese warlord tags (in `infantry_CHI.available_for`, not in `infantry_generic.blocked_for`). Expert AI: one entry per role, 8 of 8. | MEASURED | install + EAI `common/ai_templates/` |
| 9 | WA has THREE duplicate-role pairs: `infantry` (fallback + role), `light_armor` (light + light_support), `medium_armor` (medium + modern). None uses `available_for` / `blocked_for`. | MEASURED | WA `common/ai_templates/` |
| 10 | The Paradox wiki "AI templates" section is the install doc verbatim. Its one addition - `enable` listed as a role-level argument - is contradicted by vanilla's only `enable` (`templates_JAP.txt:293`, target level). | MEASURED / the wiki-error reading ASSUMED | owner screenshot vs install doc |

Peer shapes, MEASURED (evidence, not authority):

| Mod | Shape | File |
| --- | --- | --- |
| Vanilla | brake on the SOURCE, source always enabled, NO `replace_with`, tests the OLD stock | `templates_GER.txt` `panzergrenadier_early_GER` (`light_tank_chassis < 600`), also `:79`, `:598` |
| Vanilla | brake on the SOURCE, `replace_with` with `replace_at_match = 1.5` ("will only upgrade/replace when upgrade_prio takes over") | `generic.txt` `light_armor_early`, `templates_JAP.txt:39`, `templates_SIA.txt:38` |
| Expert AI | ONE entry; steps A1..A4 of a width class share one flag value plus cumulative one-way latches, so source A3 and destination A4 are enabled at once; brake on the SOURCE (`EAI_fielded_eq_ratio_modern > 0.9`); `replace_at_match = 1.0`; equal `upgrade_prio`, first in file wins | `EAI_armor_role.txt:199-270`, `EAI_PRODUCTION_design_triggers.txt:135-143` |
| WA light-support | source and destination enabled at once under ONE flag value (`STARTER` and `30_MOT` both on 15000; `_FINAL` targets enabled by an `OR` of several values); chain owner-confirmed live 2026-08-29 / 09-04 | `WA_AI_TEMPLATES_armored_light_support.txt` |

The last row falsifies blocker (a) as `WORK.md` words it ("WA enables exactly one target per
role"): the OR-enable fan-in pattern already exists and works in WA.

---

## 3. The mod side, current tree

| Fact | Label | Source |
| --- | --- | --- |
| Medium: 1752 targets, codes 20000-22231, 57 393 lines. Modern: 258 targets, codes 24000-24257, 7 969 lines. (`WORK.md` says 1368/402, later 198 - stale.) All targets `upgrade_prio base = 10`. | MEASURED | the two generated files |
| The two bands are mutually exclusive on the latch. | MEASURED | `WA_AI_TEMPLATES_ARMOR_generated.txt:184-188`, `:437-448` |
| All 258 modern targets carry `can_upgrade_in_field = { WA_AI_TEMPLATES_can_convert_park_to_modern = yes }`; all 1752 medium targets carry `always = yes`. | MEASURED | count over both files |
| The modern code is computed from live `WA_AI_TEMPLATES_ARMOR_modern_wins_*` triggers, not from the medium code. | MEASURED | generated ladder `:449-537` |
| A modern target mounts up to 10 `modern_armor_battalion_line` (first target) = 250 chassis per division; the fielded "Modern D" has 6 = 150. `modern_convert_spares_min = 100` dates from the 4-battalion composition. | MEASURED (10, 6) / DERIVED (x25 from `common/units`) | `WA_AI_TEMPLATES_armored_medium_modern.txt:35` |
| `WA_MEDIUM_ARMOR_TEMPLATE` has 10 readers in 6 script/tool files outside `common/ai_templates/` (+2 in the generated manifest). A second store for the source value is cheap on the reader side. | MEASURED | grep |

---

## 4. What recent saves show (no edit, current build)

Campaign `02795c2d` (GER, 1942.1 -> 1943.8, written 2026-09-21 00:53-02:46, several reload
branches), plus `b28209dd` and `1b8f853e` (2026-09-20) for reference. All **MEASURED** by the
subagent (`savegame.py flags/meta/army/section`, `plans.py --templates`, `stock.py --all`, a
streaming parse of the top-level `division_templates={}` block, a per-division equipment join
through `equipments={}`).

| Finding | Label |
| --- | --- |
| GER latches on 1943.4.1 in every campaign. Last medium code **21718** (`..._MEDIUM_ARMOR_30_MEC_F2_MISP_MTD_MAA_RMASS_HSUP`, `WA_AI_TEMPLATES_armored_medium.txt:43872`), first modern code **24186** (`..._MODERN_ARMOR_30_MEC_MISP_MTD_MAA_RMASS_HSUP`), then 24234 at 1943.6.1. | MEASURED |
| 1943.4.1: 34 divisions on medium templates, 0 free modern chassis. 1943.5.1: 16-18 on medium, 17-19 on hybrids, still 0 free modern chassis. | MEASURED |
| So the shipped brake was CLOSED (0 < 100 spares) while half the park converted - the owner's in-game observation, confirmed from saves. | DERIVED |
| The designer climbs ONE battalion per step: G (7 medium) -> A (6+1 modern) -> D (5+2) -> E (4+3) -> ... -> "Modern D" (6 modern). 8+ template generations in 4 months; in the baselines each child goes obsolete when the next appears and the whole park follows. | MEASURED (template ids + `obsolete_change_date`) |
| At 1943.8.1 the 17 "Modern D" divisions hold ~150 modern chassis in total for ~2 550 required; their medium tanks fell from ~197 to ~8 per division; 332 modern chassis sit in stock. | MEASURED / DERIVED (the requirement) |
| A frozen cohort exists: "Medium Tank template B", the same 11 division ids from 1942.7 to 1943.8, on the front, fighting. `b28209dd`: template C, 23 -> 17 by losses only over 14 months with 1 919 free modern chassis. | MEASURED |
| What distinguishes the frozen templates is COMPOSITION only: no `heavy_armor` divisional company, light tank destroyers. No flag, lock, role, priority, order class or location differs. `obsolete=yes` is not the cause (C and F were obsolete and still drained). | MEASURED |
| Cause of the freeze: `UPGRADES_DEFICIT_LIMIT_DAYS = 90` on the heavy chassis (heavy budget 0, no line). The same valve did NOT stop the move to modern with 0 modern chassis in stock - possibly it judges projected production, not stock. | ASSUMED |
| The save holds no parent -> child link between templates and no designer state (role map, failed-design timers, upgrade candidates). Only `role=` on each template. | MEASURED |

Consequence for any test bed: never count the B cohort - it does not move, brake or no brake.
A post-latch save whose remaining medium divisions are mostly that cohort (e.g. the 1943.8.1 save)
proves nothing.

---

## 5. The experiment

Test bed: **`trade_issue.hoi4`** (campaign `02795c2d`, GER, 1943.3.5, 27 days before the latch,
stable filename). Park: template G (id 3195) 20 divisions, B 11, F 2, C 1. Every run: fresh exe
(a hot reload voids designer readings - lessons log 2026-09-09), load, `observe`, save at
1943.5.1. The 20 G divisions are tracked BY DIVISION ID. Each run's save carries a distinct
checksum in `version=`, which proves the edited file loaded.

Baselines (no edit, checksum 7851): `conversion.hoi4` (branch B4, 1943.5.2, stable name) and the
branch-B3 1943.5.1 autosave (session 4402; autosave names rotate at every run - re-identify by
mtime/date/session/checksum, never by name).

Throwaway edits, all on GENERATED files, never committed:

| Arm | Edit |
| --- | --- |
| 0 | Medium file, target 21718: `enable` kept true for GER after the latch; `can_upgrade_in_field = { always = no }`. Source stays in the (weight-0) medium entry. |
| 0 control | same, `always = yes` |
| 1 | Medium file pristine. A COPY of the 21718 composition added inside `WA_modern_armor_role`, enabled for GER after the latch, `upgrade_prio = 5` (modern targets 10), `always = no`, no `replace_with`. |
| 2 | Same copy, FIRST in the modern entry, `upgrade_prio = 10` (tie, first in file wins), `always = no`, plus `replace_at_match = 0.9`, `replace_with = <the 24186 target>`, `target_min_match = 0.1` (the Expert AI shape). |
| 2 control (**owed**) | same, `always = yes` -> save `test6` |

Readings at 1943.5.1, GER (all MEASURED; latch 1943.4.1.1 and flag 24186 in every column):

| Reading | `test1` arm 0 | `test3` arm 0 ctrl | `test4` arm 1 | `test5` arm 2 | baseline B4 | baseline B3 |
| --- | --- | --- | --- | --- | --- | --- |
| checksum | 28a3 | 54cd | 88a2 | 2b8f | 7851 | 7851 |
| the 20 original G ids now on | G 20 | G 20 | A 18, G 2 | A 18, G 2 | Medium D 17, G 3 | Modern B 15, G 4, Medium D 1 |
| template G | live | live | obsolete 4.16 | obsolete 4.14 | obsolete 4.22 | obsolete 4.2 |
| live template(s) of the role | G | G | A (6+1) | **A (21 div), C (0), D (1)** | Medium D (5+2) | Modern B (2+5) |
| modern battalions: fielded park / recruits' template | 0 / 0 | 0 / 0 | 1 / 1 | **1 / 3** | 2 / 2 | 5 / 5 |
| armour training queue on | G | G | A | **D (4 medium + 3 modern)** | Medium D | Modern B |
| modern chassis lines, factories requested | 16 | 16 | 169 | **211** | 151 | 301 |
| medium chassis per fielded division (mean) | 193 | 193 | 150 | 148 | 125 | 50 |
| modern chassis per division / free stock | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| B cohort (11 ids) | B 11 | B 11 | B 11 | B 11 | B 11 | B 11 |

`test2` (arm 0 at 1943.6.1): G still 20 of 20, live, 27 divisions with recruits; children created
in April went obsolete with 0 divisions and none was created after 4.22; modern lines request 1
factory.

Owner imgui at `test5`: arrow on the 24186 modern target, `Best (all)` = `Best (role)` = "Medium
Tank template D", match 0.82858.

### What the runs establish

| Claim | Label |
| --- | --- |
| An enabled source holding the arrow of a separate entry keeps the role on the fielded template and freezes EVERYTHING - park, recruits, modern production need (16 then 1 factory). The brake value is irrelevant there (`test1` = `test3`). | MEASURED |
| Therefore gating the source's `enable` on stock is only a delayed latch with the known deadlock: no modern need -> no stock -> never opens. | DERIVED |
| A source in the SAME entry at lower priority and with NO edge holds nothing; `can_upgrade_in_field = no` is not read on that path. | MEASURED (`test4`) |
| Caveat on `test4`: the added target is a copy under another name. If the engine binds a template to its target by identity rather than by composition, the copy was never tied to G. Not readable from a save. | ASSUMED |
| With the `replace_with` edge, three live templates coexist - never seen in a baseline, where each child goes obsolete when the next appears. The park sits on A, recruits and the queue are on D, modern production is requested. This is the wanted shape: park held, step-up not blocked, production primed. | MEASURED (facts) / DERIVED (the reading) |
| Working hypothesis: the brake acts between CLASSES of templates. A (6+1) still best-matches the source target, so G -> A is not braked; A -> D goes toward the `replace_with` target's templates and is braked. Consistent with all five runs, written in no file. | ASSUMED |
| Rival: `test4` also sat on A for 16 days with no edge - a plain designer delay would give the same 1943.5.1 picture. The control (`test6`, brake open) separates them: if the park then follows the children like the baselines, the brake is read through the edge. | - |
| Even if confirmed, the FIRST rung (G -> A) swapped one battalion for the whole park with zero modern chassis in stock. Nobody - recruits included - holds a single modern chassis at 1943.5.1. | MEASURED |

---

## 6. How to resume on another machine

1. **Saves are local to the machine that ran them** (`~\Documents\Paradox Interactive\Hearts of
   Iron IV\save games`): `trade_issue.hoi4`, `conversion.hoi4`, `test1`..`test5`. Copy
   `trade_issue.hoi4` (and the test saves if they are to be re-read) or the experiment cannot
   continue there.
2. Re-apply the throwaway block below in `common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt`,
   immediately before the first target `WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_30_MEC = {`
   (tabs, CRLF, no BOM). This is the **arm 2 CONTROL** state (`always = yes`); set `always = no`
   for arm 2 itself.
3. Fresh exe -> load `trade_issue.hoi4` -> `observe` -> save at 1943.5.1 as `test6`. **Do not read
   past 1943.5.1**: the flag moves to 24234 at 1943.6.1 and the static edge to the 24186 target
   would dangle.
4. Revert: `git checkout -- common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt`.
   `python tools/gen/gen_ai_armor_templates.py --check` reports `DRIFT` while the block is in -
   expected, and it is what stops an accidental commit.

```
	# THROWAWAY-TEST arm 2 CONTROL - DO NOT COMMIT (GENERATED file)
	WA_AI_TEMPLATES_THROWAWAY_TEST_SOURCE_21718 = {
		enable = { tag = GER has_country_flag = WA_AI_TEMPLATES_modern_chassis_earned }
		reinforce_prio = 2
		custom_icon = 140
		can_upgrade_in_field = { always = yes }
		upgrade_prio = { base = 10 }
		target_template = {
			regiments = {
				infantry_heavy_mechanized_battalion_line = 5
				medium_armor_battalion_line = 7
				medium_infantry_support_armor_battalion_line = 3
			}
			regimental_support = {
				medium_assault_gun_company_regimental = 5
				medium_tank_destroyer_company_regimental = 5
			}
			support = {
				engineer_med_tank_battalion_divisional = 1
				field_hospital_mot_company_divisional = 1
				heavy_armor_company_divisional = 1
				logistics_mot_company_divisional = 1
				maintenance_med_tank_company_divisional = 1
				medium_infantry_support_company_divisional = 1
				medium_self_propelled_anti_air_company_divisional = 1
				military_police_mot_company_divisional = 1
				recon_light_tank_company_divisional = 1
				signal_mot_company_divisional = 1
			}
		}
		replace_at_match = 0.9
		replace_with = WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_30_MEC_MISP_MTD_MAA_RMASS_HSUP
		target_min_match = 0.1
	}
```

Reading a run (the method; the ad-hoc scripts lived in a session scratchpad and are not
committed):

| Reading | How |
| --- | --- |
| validity | `savegame.py meta FILE`: `game_unique_id` = `02795c2d...`, a NEW 4-char checksum in `version=` (not 7851 / 28a3 / 54cd / 88a2 / 2b8f) |
| latch and code | `savegame.py flags FILE GER --match "modern_chassis_earned|WA_MEDIUM_ARMOR_TEMPLATE"` |
| templates | stream the top-level `division_templates={}` block (it precedes `countries={}`): `id`, `name`, `obsolete`, `obsolete_change_date`, `role`, `regiments`, `support`, `regimental_support`. `obsolete` is only ever written `yes`; absence = live |
| cohort tracking | `plans.scan(path, tags={'GER'}, want_divisions=True, want_templates=True)` from `plans.py`: division id -> `division_template_id`. Take the 20 ids on template 3195 and the 11 on 2198 in `trade_issue.hoi4`, look them up in the run's save |
| chassis per division | in the `units` section, each `division={}` has `equipment={ id={ id=N type=70 } amount= }`; resolve N through the top-level `equipments={}` registry (`stock.equipment_definitions`) and bucket on the definition name (`modern_chassis`, `medium_chassis`, `medium_chassis_td`, `heavy_chassis`) |
| production | `savegame.py section FILE GER production`: per `military_lines` block, `active_factories`, `requested_factories`, `equipment_variant_index`; archetype from `common/units/equipment/*.txt` |
| recruits | division ids absent from `trade_issue.hoi4`; the training queue lines and the template each is on |
| tool faults met | `stock.py` needs the full save path and `--all` to show own-built stock; `plans.py --templates` truncates the battalion list at five types |

---

## 7. Decision tree after `test6`

| `test6` (edge, brake OPEN) at 1943.5.1 | Conclusion | Next |
| --- | --- | --- |
| The park follows the children like the baselines (A drains to C/D) | The engine reads the SOURCE's `can_upgrade_in_field` through the `replace_with` edge. The on/off gate the owner wants (scripted trigger on stock / production state) is feasible. | Solve the mapping (below), then the first-rung problem. |
| The park stays on A like `test5` | The brake is not what holds A - the edge itself or designer variance does. | Re-read at a later date with an edge that survives the 1943.6.1 flag move; if still ambiguous, the remaining levers are the ones in `WORK.md`: a stock bar on the latch, or the engine valve `UPGRADES_DEFICIT_LIMIT_DAYS`. |

If the edge is confirmed, the open design questions, in order:

1. **One entry.** The edge only resolves inside its entry, so medium and modern targets must be
   emitted into ONE role entry (generator change: `tools/gen/armor_templates/emit.py`, `model.py`,
   registry `families.modern.role_group`). This also removes the duplicate `medium_armor` entry;
   the `infantry` and `light_armor` pairs stay duplicated.
2. **Source must stay enabled after the latch.** One flag holds one value, so the medium target
   needs a second, frozen store for the last medium code (10 readers of the flag today). This is a
   signature-level change to a `WA_AI_*` effect called from an on_action - the owner console-harness
   rule applies (`WA_TEST_templates`, `WA_TEST_armor_budget` exist).
3. **The mapping.** 1752 medium -> 258 modern, and the modern code is computed live, not from the
   medium code. A static twin is the "+500 mirror" that already produced unbuildable slots
   (`modern-chassis-tier` Defect A); full (source, destination) pairs is the parked
   `parked/armor-conversion-finals` generator (~9 000 lines). Candidate to test next: a HUB - every
   medium target's `replace_with` points at ONE generic modern target per plane, relying on the
   MEASURED rule that field-upgraded divisions land on the best EXISTING match of the edge's
   destination (lessons log 2026-09-04), i.e. on the live modern template. Unknown: whether the
   engine follows an edge whose destination is not the arrow. ASSUMED until tested. The OR-enable
   fan-in already used by the light-support `_FINAL` targets is the in-tree precedent for many
   sources sharing one destination.
4. **Horizontal evolution.** In WA it is `enable`-driven (the flag changes value, another target
   becomes the enabled one); `replace_with` is only consulted on the enabled target. Expert AI ships
   the same combination (A3 -> A4 edge with A4 latched off for most of the game). DERIVED that an
   edge does not block horizontal moves; the dangling-edge case (destination disabled) is ASSUMED
   harmless and is exactly what happens at 1943.6.1 in the test bed.
5. **The first rung.** G -> A moved the whole park with 0 modern chassis. Either the gate must also
   cover that rung (the class hypothesis says it cannot, A still matches the source), or the
   source composition must be made to stop matching A, or the rung must be accepted (25 chassis
   per division). Needs its own run.
6. **Gate content.** Test stock per division to convert: ~150-250 modern chassis, not the current
   `modern_convert_spares_min = 100`. With the wanted shape the modern need exists (recruits are
   modern, 211 factories requested in `test5`), so stock can build while the park is held - the
   deadlock of the full hold (arm 0) does not apply. Oscillation of the gate changes no `enable`,
   hence triggers no decommission pass (DERIVED from the doc).
7. **Decommission hazard** (lessons log, flag-gated-target entry): at the latch no target goes
   true -> false in the merged shape, which is better than today's full swap; the pass still runs
   because a target appears. A park held by the brake sits on a template that is NOT obsolete in
   `test5` (three live templates) - better than feared, but only one date. Whether a long hold
   reinforces normally is ASSUMED. Already-latched campaigns on ship day: the frozen store does not
   exist, the medium targets stay disabled, the enabled set is unchanged (DERIVED).

Intermediate hand-written templates (half medium / half modern) are not recommended: the engine
already builds its own one-battalion rungs, and each extra scripted rung is one more place where
the designer's column rules can freeze a template (ENG, six years).

---

## 8. Stale statements found on the way (not edited here)

| Where | What is stale |
| --- | --- |
| `AGENTS.md`, `wa-engine-reference` | engine version 1.19.2 -> the install is 1.19.3.0 |
| `WORK.md` `modern-switch-amorce` | target counts 1368 / 402 / 198 -> 1752 / 258; "100 chassis per division" -> 150-250; blocker (a) "WA enables exactly one target per role" -> false in the light-support family; "bascule4: the park is NOT hollow" was read from strength, the per-division chassis join says otherwise on the current build |
| `modern_convert_spares_min = 100` and the four comment sites `WORK.md` already lists | describe a brake that the saves show is not read where it sits |
