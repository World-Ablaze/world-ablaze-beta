# Medium -> modern armour switch: duplicate role entry diagnosis and the park-brake experiment

Date: 2026-09-21. Branch `ai-rework`. Subject it serves: `modern-switch-amorce` in `WORK.md`.
Status: **OPEN, and weaker than it read after `test6`.** First machine: `test5` / `test6` (one run
each, one date) read as "the engine reads the source's `can_upgrade_in_field` through a
`replace_with` edge". Second machine (section 7b): `test7` (twins, 0.3) does NOT hold the park;
`test8` (twins, 0.9) ends on 7+0 but by going down and coming back, with modern production frozen -
neither run needs the brake to be explained. Next owed run: **`test9`**, the brake control at 0.9.
The full list is "What remains to do" at the end of section 7b. No mod code was shipped.
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
3. Live experiment, six runs from one save: a source kept alive in a *separate* entry freezes
   everything (park, recruits, production need) whatever the brake says; a source inside the *same*
   entry with no `replace_with` holds nothing; a source inside the same entry **with a
   `replace_with` edge** gives the wanted shape - park held one rung up, recruits on a higher
   rung, modern chassis production requested - and the control with the brake OPEN (`test6`) makes
   the park follow the children like the baselines. **MEASURED**; the causal reading is
   **DERIVED** from the `test5` / `test6` pair, whose only difference is the brake line.
   **Weakened by section 7b:** one run each, read at one date, on a bed whose unedited baselines
   already differ by three rungs at that date; `test7` and `test8` show no braking effect.
4. The symptom the subject started from is live on the current build: converted divisions are
   nearly tank-less (17 divisions holding ~150 modern chassis for ~2 550 required, medium tanks
   stripped from ~197 to ~8 per division). **MEASURED.**
5. A static medium -> modern twin mapping is the already-failed "+500 mirror" design (unbuildable
   slots, `WORK.md` `modern-chassis-tier` Defect A). Proposal that needs NO mapping, NO second
   flag store and NO file merge: give every MODERN target a **medium-hull twin** inside the modern
   entry, enabled by the SAME flag value, carrying the brake and a `replace_with` to its modern
   target (section 7). `test7` tests it across the 1943.6.1 flag move.
6. Second machine, **MEASURED**: that proposal fails at `replace_at_match = 0.3` (full descent,
   `test7`) and at 0.9 produces a park that reverts to 7+0 with NO modern template, NO modern
   chassis built and no armour recruits (`test8`) - the arm 0 deadlock by another road. Whether the
   brake line does anything at all is what `test9` decides.

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
| 2 control | same, `always = yes` -> `test6` |

Readings at 1943.5.1, GER (all MEASURED; latch 1943.4.1.1 and flag 24186 in every column):

| Reading | `test1` arm 0 | `test3` arm 0 ctrl | `test4` arm 1 | `test5` arm 2 | `test6` arm 2 ctrl | baseline B4 | baseline B3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| checksum | 28a3 | 54cd | 88a2 | 2b8f | 9553 | 7851 | 7851 |
| the 20 original G ids now on | G 20 | G 20 | A 18, G 2 | A 18, G 2 | **E 19, A 1** | Medium D 17, G 3 | Modern B 15, G 4, Medium D 1 |
| template G | live | live | obsolete 4.16 | obsolete 4.14 | obsolete 4.7 | obsolete 4.22 | obsolete 4.2 |
| live template(s) of the role | G | G | A (6+1) | **A (21 div), C (0), D (1)** | **E (4+3) only**, 21 div; A and D obsolete 4.28 | Medium D (5+2) | Modern B (2+5) |
| modern battalions: fielded park / recruits' template | 0 / 0 | 0 / 0 | 1 / 1 | **1 / 3** | **3 / 3** | 2 / 2 | 5 / 5 |
| armour training queue on | G | G | A | **D (4 medium + 3 modern)** | E (4 + 3) | Medium D | Modern B |
| modern chassis lines, factories requested | 16 | 16 | 169 | **211** | 151 | 151 | 301 |
| medium chassis per fielded division (mean) | 193 | 193 | 150 | 148 | **100** | 125 | 50 |
| modern chassis per division / free stock | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| B cohort (11 ids) | B 11 | B 11 | B 11 | B 11 | B 11 | B 11 | B 11 |

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
| Working hypothesis: the brake acts between CLASSES of templates. A (6+1) still best-matches the source target, so G -> A is not braked; A -> D goes toward the `replace_with` target's templates and is braked. Consistent with all six runs, written in no file. | ASSUMED |
| Rival, now answered: `test4` also sat on A for 16 days with no edge, so a plain designer delay could have produced the `test5` picture. The control `test6` (same edge, brake OPEN, same date) has ONE live template (E, 4+3), 19 of the 20 original ids on it, A and D obsolete since 4.28 - the baselines' one-live-template pattern. The `test5` hold is the brake. | MEASURED (`test6`) / DERIVED (the causal reading: one differing line, one run each) |
| Cost of the open brake, same date, same rung reached by the designer (#3462, 4+3, in both runs): fielded divisions fall from ~148 medium chassis (`test5`, held on A) to 100 (`test6`), with 0 modern chassis to replace them. | MEASURED |
| Even if confirmed, the FIRST rung (G -> A) swapped one battalion for the whole park with zero modern chassis in stock. Nobody - recruits included - holds a single modern chassis at 1943.5.1. | MEASURED |

---

## 6. How to resume on another machine

1. **Saves are local to the machine that ran them** (`~\Documents\Paradox Interactive\Hearts of
   Iron IV\save games`): `trade_issue.hoi4`, `conversion.hoi4`, `test1`..`test5`. Copy
   `trade_issue.hoi4` (and the test saves if they are to be re-read) or the experiment cannot
   continue there.
2. Re-apply the throwaway block below in `common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt`,
   immediately before the first target `WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_30_MEC = {`
   (tabs, CRLF, no BOM). This is the **`test7`** state: two medium-hull twins, one per modern code
   GER holds in the window (24186 until 1943.5, 24234 from 1943.6.1), brake closed. (Arm 2 itself
   was ONE such block named `..._SOURCE_21718`, enabled by `tag = GER` + the latch flag,
   `replace_at_match = 0.9`, pointing at the 24186 target; `always = no` for `test5`, `yes` for
   `test6`.)
3. Fresh exe -> load `trade_issue.hoi4` -> `observe` -> save at **1943.5.1 (`test7a`), 1943.6.15
   (`test7b`) and 1943.8.1 (`test7c`)**. The point of `test7` is to read ACROSS the 1943.6.1 flag
   move, which arm 2's static edge could not survive.
4. Revert: `git checkout -- common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt`.
   `python tools/gen/gen_ai_armor_templates.py --check` reports `DRIFT` while the block is in -
   expected, and it is what stops an accidental commit.

```
	# THROWAWAY-TEST test7 - DO NOT COMMIT (GENERATED file)
	WA_AI_TEMPLATES_THROWAWAY_TEST_MEDIUM_HULL_TWIN_24186 = {
		enable = { has_country_flag = { flag = WA_MEDIUM_ARMOR_TEMPLATE value = 24186 } }
		reinforce_prio = 2
		custom_icon = 140
		can_upgrade_in_field = { always = no }
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
		replace_at_match = 0.3
		replace_with = WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_30_MEC_MISP_MTD_MAA_RMASS_HSUP
		target_min_match = 0.1
	}

	WA_AI_TEMPLATES_THROWAWAY_TEST_MEDIUM_HULL_TWIN_24234 = {
		enable = { has_country_flag = { flag = WA_MEDIUM_ARMOR_TEMPLATE value = 24234 } }
		reinforce_prio = 2
		custom_icon = 140
		can_upgrade_in_field = { always = no }
		upgrade_prio = { base = 10 }
		target_template = {
			regiments = {
				infantry_heavy_mechanized_battalion_line = 5
				medium_armor_battalion_line = 7
				medium_self_propelled_gun_battalion_line = 3
			}
			regimental_support = {
				medium_self_propelled_gun_company_regimental = 5
				medium_tank_destroyer_company_regimental = 5
			}
			support = {
				engineer_med_tank_battalion_divisional = 1
				field_hospital_mot_company_divisional = 1
				heavy_armor_company_divisional = 1
				logistics_mot_company_divisional = 1
				maintenance_med_tank_company_divisional = 1
				medium_self_propelled_anti_air_company_divisional = 1
				medium_self_propelled_gun_company_divisional = 1
				military_police_mot_company_divisional = 1
				recon_light_tank_company_divisional = 1
				signal_mot_company_divisional = 1
			}
		}
		replace_at_match = 0.3
		replace_with = WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_30_MEC_MSPG_MTD_MAA_HSUP
		target_min_match = 0.1
	}
```

Reading a run. The scripts are committed since the second-machine session, under
`tools/archive/modern_switch_experiment/` (they resolve the repo from their own location):
`read_run.py <reference_save> <run_save>...` does every row of the table below in one call and
prints the closure test; `medium_hull_twins.py apply [--brake no|yes] [--ram 0.9]` writes the 258
twins of section 7b; `cohort_history.py`, `q_reference.py`, `flag_trajectory.py` are the
single-question readers. The method they implement:

| Reading | How |
| --- | --- |
| validity | `savegame.py meta FILE`: `game_unique_id` = `02795c2d...`, a NEW 4-char checksum in `version=` (not 7851 / 28a3 / 54cd / 88a2 / 2b8f) |
| latch and code | `savegame.py flags FILE GER --match "modern_chassis_earned|WA_MEDIUM_ARMOR_TEMPLATE"` |
| templates | stream the top-level `division_templates={}` block (it precedes `countries={}`): `id`, `name`, `obsolete`, `obsolete_change_date`, `role`, `regiments`, `support`, `regimental_support`. `obsolete` is only ever written `yes`; absence = live |
| cohort tracking | `plans.scan(path, tags={'GER'}, want_divisions=True, want_templates=True)` from `plans.py`: division id -> `division_template_id`. Take the 20 ids on template 3195 and the 11 on 2198 in `trade_issue.hoi4`, look them up in the run's save |
| chassis per division | in the `units` section, each `division={}` has `equipment={ id={ id=N type=70 } amount= }`; resolve N through the top-level `equipments={}` registry (`stock.equipment_definitions`) and bucket on the definition name (`modern_chassis`, `medium_chassis`, `medium_chassis_td`, `heavy_chassis`) |
| production | `savegame.py section FILE GER production`: per `military_lines` block, `active_factories`, `requested_factories`, `equipment_variant_index`; archetype from `common/units/equipment/*.txt` |
| recruits | division ids absent from `trade_issue.hoi4`; the training queue lines and the template each is on |
| tool faults met | `stock.py` needs the full save path and `--all` to show own-built stock, and `--all` ADDS division-held and training-queue equipment to the stockpile (section 7b) - read free stock from the `production > equipments` block, as `read_run.py` does; `plans.py --templates` truncates the battalion list at five types |
| binary saves | a local game writes `HOI4bin` unless `settings.txt` carries `save_as_binary=no` (edit it with the game CLOSED - the exe rewrites the file on exit). An existing binary save is recovered by loading it and re-saving while paused |
| which field is the checksum | in `version=Operation Postern v1.19.3.0.c01a (5122)` the mod checksum is the PARENTHESISED field; `c01a` is the engine build |

---

## 7. After `test6`: the medium-hull twin proposal, and `test7`

`test6` settled the mechanism: **source target in the same entry + `replace_with` edge +
`can_upgrade_in_field` on the source = an on/off gate on the fielded park that does not block
recruits, design or production.** What is left is how to emit that for 1752 medium and 258 modern
targets without a mapping.

### The proposal

The modern family is a `mirror_of` the medium one: the 24186 modern target IS the 21718 medium
target with the hulls swapped (7 `modern_armor` for 7 `medium_armor`, `engineer_mod_tank` /
`maintenance_mod_tank` for the `_med_` versions) - **MEASURED**, both blocks read side by side.
So for every MODERN target M the generator can emit, mechanically, a **medium-hull twin** S(M):

| Field of S(M) | Value |
| --- | --- |
| entry | `WA_modern_armor_role` - the same entry as M, emitted just BEFORE M (tie on `upgrade_prio`, first in file wins the arrow, then the edge hands it to M) |
| `enable` | the SAME flag value as M |
| composition | M with `modern_armor_battalion_line` -> `medium_armor_battalion_line` and the two `_mod_tank` companies -> `_med_tank` |
| `replace_with` | M. `replace_at_match` low (0.3 in `test7`) so the arrow goes to M as soon as any fielded template resembles S(M); `target_min_match` 0.1 |
| `can_upgrade_in_field` | the gate: a scripted trigger on modern chassis stock / production state |

What this removes, each against the blocker recorded in `WORK.md`:

| Blocker | Why it no longer binds | Label |
| --- | --- | --- |
| (a) one enabled target per role / one flag value | S(M) and M are enabled by the same value - the WA light-support and Expert AI pattern. No second, frozen store; no ladder change. | DERIVED |
| (b) twin mapping not 1:1 (1752 -> 258, modern code computed live) | The edge never leaves the modern code space: S(M) -> M is 1:1 by construction, 258 twins. Which MEDIUM code the country held is irrelevant - the fielded template only has to resemble S(M) more than M. | DERIVED |
| (c) `replace_with` does not cross entries | Both live in the modern entry. The medium entry dies at the latch exactly as today; no file merge. | DERIVED |
| dangling edge when the flag moves (24186 -> 24234) | The pair (S(M), M) switches off and (S(M'), M') switches on together. | DERIVED - this is what `test7` measures |

Cost: +258 generated targets (~8 000 lines) in one generated file, an emitter change
(`tools/gen/armor_templates/emit.py`), the gate trigger, and the removal of the inert
`can_upgrade_in_field` from the modern targets. No `WA_AI_*` effect changes signature.

### What `test7` must show (GER, from `trade_issue.hoi4`, brake closed)

| Date | Wanted reading | What it tests |
| --- | --- | --- |
| 1943.5.1 (`test7a`) | same shape as `test5`: park held on the first rung, several live templates, recruits and queue on the top child, modern lines requesting 150+ factories | that a flag-keyed twin with `replace_at_match = 0.3` behaves like arm 2's exact copy |
| 1943.6.15 (`test7b`) | the hold SURVIVES the 1943.6.1 move to 24234: park still on its rung with its medium tanks, arrow on the 24234 modern target, no full freeze (recruits not back on the park's template, modern lines still requested) | the twin design's answer to the dangling edge |
| 1943.6.15 / 1943.8.1 | does the HELD park evolve horizontally (24186 mounts 3 `medium_infantry_support_armor` + assault-gun companies, 24234 mounts 3 `medium_self_propelled_gun` + SPG companies)? Expected: no - every new design flows toward M, and the brake blocks the move | the owner's "horizontal evolution while targeting modern" question, measured rather than argued |
| 1943.8.1 (`test7c`) | chassis per held division still ~150 medium; stock of modern chassis RISING because recruits carry the need (in the baselines it is 332 at 1943.8.1 with a tank-less park) | that the gate can ever open on stock |

Then the control of the gate itself: flip both twins to `always = yes` from the `test7b` save and
check the park moves to the live template (expect `UPGRADE_PERCENTAGE_OF_FORCES` 20 % per 14 days
to pace it).

### Open design questions after `test7`

1. **The first rung slips.** In `test5` and `test6` alike 18 of 20 divisions left G for child A
   (6 medium + 1 modern) with 0 modern chassis in stock; the brake only bites from A upward.
   Working hypothesis (ASSUMED): A still best-matches the source, so G -> A is a move inside the
   source's class. Cost MEASURED: ~197 -> ~148 medium chassis per division, one battalion short,
   and A carries NO maintenance company. Tolerable next to the unbraked outcome (~8), but it needs
   its own run if the owner wants the park held on G itself.
2. **Gate content.** Stock needed per division to convert: 150-250 modern chassis, not
   `modern_convert_spares_min = 100`. With the wanted shape the modern need exists (recruits are
   modern, 211 factories requested in `test5`), so stock can build while the park is held - the
   deadlock of the full freeze (arm 0) does not apply. Oscillation of the gate changes no `enable`,
   hence triggers no decommission pass (DERIVED from the install doc).
3. **Decommission hazard** (lessons log, flag-gated-target entry). The twin design changes NO
   existing target's `enable`; it adds targets that switch with the flag value exactly as the
   modern targets already do. The held template is NOT obsolete in `test5` (three live templates) -
   better than feared, one date only; whether a long hold reinforces normally is what `test7c`
   reads. Already-latched campaigns on ship day: their flag value enables one more target (the
   twin); their park is already converted, so nothing resembles the twin - expected inert, ASSUMED.
4. **The other two duplicate-role pairs** (`infantry`, `light_armor`) stay as they are; nothing here
   requires merging entries any more. The `[dead-role-entry]` guards remain the mitigation.
5. **Intermediate hand-written templates** (half medium / half modern) are not recommended: the
   engine already builds its own one-battalion rungs, and each extra scripted rung is one more
   place where the designer's column rules can freeze a template (ENG, six years).

---

## 7b. `test7` re-based on the second machine (campaign `d6190fb7`)

`trade_issue.hoi4` did not travel. The test bed on the second machine is an observer campaign
(`d6190fb7`, player BHU, monthly saves, engine 1.19.3.0, mod checksum `5122`, produced by the cloud
test build - which commit it ran is **ASSUMED** close to HEAD: its codes 21718 / 24186 exist only
in the generator-era tree). All readings below **MEASURED** by an extraction subagent unless marked.

| Item | `d6190fb7` | `02795c2d` (sections 4-5) |
| --- | --- | --- |
| Test bed | `modern_bed.hoi4` = copy of `1943.4_Apr.hoi4` (1943.4.1.2, 30 days before the latch) | `trade_issue.hoi4` (1943.3.5) |
| Latch | 1943.5.1.1 | 1943.4.1.1 |
| Flag codes | 21718 -> 24186 (5.1) -> **24138** (7.1 .. 12.1) -> 24234 (1944.1.1) | 21718 -> 24186 -> 24234 (6.1) |
| Park | #3347 "Medium Tank template A" (7+0), **17 divisions** | G #3195, 20 divisions |
| Frozen cohort - never count it | #2210 "template H", 9 ids, no `heavy_armor` company, light TDs; plus ids 89471 / 95059 that stay on A | "template B", 11 ids |

Baseline of the 17 park ids (the existing monthly saves, no edit):

| Reading | 1943.5 | 1943.6 | 1943.7 | 1943.8 | 1943.9 |
| --- | --- | --- | --- | --- | --- |
| on template | A 17 | C (5+2) 15, A 2 | F (4+3) 15, A 2 | same | same |
| live templates of the role | A | C | F | F | F + "Modern C" (1+5, 0 div, holds the queue) |
| gun tanks per division (15 converted) | 196 | 124 | 100 | 100 | 100 |
| modern chassis per division | 0 | 0 | 0 | 0.2 | 2.4 |
| free modern chassis | 0 | 0 | 0 | 0 | 0 |
| modern lines, active / requested factories | 0 / 30 | 0 / 258 | 50 / 333 | 186 / 384 | 200 / 314 |

The subject's symptom reproduces: each converted division sheds ~97 gun tanks into the stockpile
(free medium gun tanks 108 -> 3 191) and holds 2.4 modern chassis four months after the latch.

Tool fault found: `stock.py --all` adds division-held and training-queue equipment to the
stockpile (1943.9: reports 152 modern chassis, the `production > equipments` block holds 0). The
"332 modern chassis sit in stock" of section 4 came through it and is **ASSUMED** contaminated.

`test7` state on this machine: a medium-hull twin for **all 258** modern targets (not two - a
replay may land on another modern code than 24186 / 24138), brake closed, written by a throwaway
script; the 24186 twin carries the same fields as the block of section 6. Runs, fresh exe, load
`modern_bed.hoi4`, `observe`:

| Save as | Date | Compare to baseline | Wanted |
| --- | --- | --- | --- |
| `test7a` | 1943.6.1 | C 15 / A 2, gun 124 | `test5` shape: park held on A or the first rung, several live templates, queue on a higher child, modern lines requested |
| `test7b` | 1943.7.15 | F 15, gun 100 | the hold survives the 7.1 move to 24138; no full freeze |
| `test7c` | 1943.9.1 | F 15, gun 100, free modern 0 | gun tanks still ~150+, free modern chassis RISING |

### `test7` result: the hold does NOT appear (2026-09-21, second machine)

Validity, **MEASURED**: three text saves, campaign `d6190fb7`, mod checksum `7bd1` (baseline
`5122`), latch 1943.5.1.1, closure test OK on all three (232 / 237 / 240 divisions). The replay
took 24186 -> 24138 (7.1) -> **24234 (9.1)**; the baseline stays on 24138 until 12.1 - a replay
does drift, which is what the 258 twins were for. Reader: `read_run.py` (session scratchpad).

| Reading, the 17 park ids | `test7a` 1943.6.1 | `test7b` 1943.7.15 | `test7c` 1943.9.1 | baseline 6.1 / 7.1 / 9.1 |
| --- | --- | --- | --- | --- |
| on template | B (6+1) 17 | Modern A (3+4) 17 | Modern A (3+4) 17 | C (5+2) 15 / F (4+3) 15 / F 15 |
| live templates of the role | B only | Modern A (19 div), Modern B 2+5 (0) | Modern A (19), Modern D 0+6 (0) | one, except 9.1 |
| gun tanks per division | 149.5 | 74.6 | 74.8 | 124 / 100 / 100 |
| modern chassis per division | 0 | 0.3 | 10.2 | 0 / 0 / 2.4 |
| free modern chassis | 0 | 0 | 0 | 0 |
| free medium gun tanks | 2 734 | 4 643 | 4 863 | 2 471 / 2 932 / 3 191 |
| modern lines active / requested | 0 / 178 | 32 / 416 | 186 / 403 | 0 / 258, 50 / 333, 200 / 314 |
| armour training queue / recruits | none / 0 | none / 0 | none / 0 | C (4 lines) / F, 4 recruits |

Template timeline in the run, **MEASURED** (`obsolete_change_date`): A obsolete 5.22, B 6.10,
C 6.22, D (4+3) 6.26, then "Modern A" (3+4). Four rungs fell between 6.10 and 6.26 with the flag
constant at 24186 - the park followed every child, each predecessor going obsolete as the next
appeared. That is the `test6` / baseline pattern (brake open), not the `test5` one (three live
templates, park held on the first rung). **The flag move of 7.1 is not what broke it: there was
no hold left to break.**

| Claim | Label |
| --- | --- |
| A flag-keyed medium-hull twin with `replace_at_match = 0.3`, brake `always = no`, does not hold the fielded park. | MEASURED (one run) |
| `test7` ends one rung BELOW the baseline (3+4 vs 4+3, 75 gun tanks vs 100). Not attributable to the twins: the baseline ran on the cloud build, `test7` on HEAD, and no HEAD-without-twins control exists on this machine. | MEASURED / the attribution ASSUMED |
| No armour division was queued in any of the three saves, against 4 lines in the baseline. Same confound. | MEASURED |
| Differences between `test5` (hold) and `test7` (no hold): `replace_at_match` 0.9 -> 0.3; twin enabled by flag VALUE instead of `tag = GER` + latch flag; twin placed before its M instead of first in the entry; 258 twins instead of 1; campaign and build. Which one matters is not readable from a save. | MEASURED (the list) |
| Rival that the data cannot exclude: `test5` was read at ONE date, +30 days. `test7a`, also +31 days, shows the park on the first rung (6+1) too - the rung `test5` sat on. The `test5` hold may have been a slower ladder, not a brake. What speaks against it: `test5` had THREE live templates at that date and `test6` (brake open) had one, 4+3, 19 of 20 ids. | DERIVED |
| Install doc, `can_upgrade_in_field`: "If false, the AI will not field-upgrade divisions matching this target template." What "matching" means (score above `replace_at_match`? best-matching target?) is documented nowhere. If it is the former, 0.3 should brake MORE than 0.9, and it did not. | MEASURED (the sentence) / ASSUMED (the readings) |

### `test8` - one variable back toward `test5`

Same 258 flag-keyed twins, brake closed, **`replace_at_match = 0.9`** (the `test5` value) - the one
deliberate parameter change between the run that held and the run that did not. Fresh exe, load
`modern_bed.hoi4`, `observe`. The rungs fell between 6.10 and 6.26 in `test7`, so the first save
moves there:

| Save as | Date | Hold = | No hold = |
| --- | --- | --- | --- |
| `test8a` | 1943.6.20 | park on A or B (7+0 / 6+1), two or more live templates, gun tanks >= 150 | park on C / D, one live template |
| `test8b` | 1943.7.15 | same after the 7.1 flag move | Modern A (3+4), ~75 gun tanks |
| `test8c` | 1943.9.1 | same; free modern chassis > 0 | as `test7c` |

If `test8` holds: 0.3 was the fault, and the generator proposal stands with 0.9. If it does not:
replay `test5` literally on this bed (ONE twin, first in the entry, `enable = { tag = GER
has_country_flag = WA_AI_TEMPLATES_modern_chassis_earned }`, 0.9) - if even that fails here, the
`test5` hold was a one-date reading and section 7 falls. In either failing case the owner's
`imgui show ai_templates` at 1943.6.15 (arrow, `Best (role)`, match scores of the twin and of M)
is the reading no save can replace.

### `test8` result: the park ends on 7+0, but by REVERTING, and the modern side is frozen

Validity, **MEASURED**: three text saves, campaign `d6190fb7`, mod checksum `152c`, closure OK
(235 / 237 / 243). Flag 24186 -> 24138 (7.1) -> 24234 (9.1), as in `test7`. Confound, MEASURED:
three unrelated files (`FRA.txt`, `WA_AI_MILITARY_FACTION_ALLIES_THEATRE.txt`, `WA_AI_CONFIG.txt`)
were modified in the working tree by another session (mtime 12:54, the minute `test8c` was
written); whether the exe that ran `test8` had loaded them is ASSUMED no - none touches templates.

| Reading, the 17 park ids | `test8a` 1943.6.20 | `test8b` 1943.7.15 | `test8c` 1943.9.1 |
| --- | --- | --- | --- |
| on template | C (5+2) 11, B (6+1) 3, A (7+0) 3 | **A (7+0) 16**, B 1 | **A (7+0) 17** |
| live templates of the role | C | **A - live AGAIN** (it was obsolete 5.26 in `test8a`); C obsolete 7.6 | "Medium Tank template E" #3559, 7+0, 0 div (A obsolete 8.9) |
| gun tanks per division | 140.6 | 187.1 | 194.5 |
| modern chassis per division / free | 0 / 0 | 0 / 0 | 0 / 0 |
| modern lines active / requested | **0** / 174 | **0** / 197 | **0** / 128 |
| any "Modern ..." template designed | no | no | no |
| armour training queue / recruits | none / 0 | none / 0 | none / 0 |

| Claim | Label |
| --- | --- |
| The park went DOWN the ladder first (11 of 17 on 5+2 ten days after C appeared) and then came BACK to 7+0. The closed brake did not stop the descent. | MEASURED |
| With 0.9 the role never leaves the medium shape: no modern template exists at any date, no modern chassis is built (0 active factories at all three dates; baseline 50 then 200, `test7` 32 then 186), none is held. A gate that waits for modern stock could never open - the arm 0 deadlock. | MEASURED (facts) / DERIVED (the deadlock) |
| Reading that fits both runs: the arrow sits on M only while the best live template matches S at >= `replace_at_match`. At 0.3 that is always (`test7`: full descent). At 0.9 it stops being true around 5+2, the arrow returns to S, the designer rebuilds toward S and the park follows it back up. A revived and then a new 7+0 template E cut to the 24234 twin is what that predicts. | ASSUMED (no imgui reading) |
| In NEITHER run is there a reading that needs `can_upgrade_in_field = no` to explain it: at 0.3 the park followed every rung, at 0.9 it followed the descent and the return alike. | DERIVED |
| This weakens section 5's causal reading. `test5` / `test6` were one run each, read at ONE date (+30 days), and two unedited baselines there already differed by three rungs at that date (5+2 vs 2+5). `test5`'s three live templates can be a snapshot of the same return movement. | DERIVED |
| Horizontal evolution (the owner's question): yes while the arrow is on S - template E is a new 7+0 cut after the move to 24234. | MEASURED (E exists, 7+0) / ASSUMED (that its support mix is the 24234 one - not read) |

### `test9` - the brake control on this bed

Same 258 twins, `replace_at_match = 0.9`, **`can_upgrade_in_field = { always = yes }`**. One line
differs from `test8`. Same dates: `test9a` 1943.6.20, `test9b` 1943.7.15, `test9c` 1943.9.1.

| Outcome | Meaning |
| --- | --- |
| same as `test8` (back on 7+0, modern frozen) | the brake does nothing here; the 0.9 threshold alone produces the hold; `can_upgrade_in_field` on a source twin is not a usable gate and section 7 falls |
| full descent like `test7` | the brake is read at 0.9 and not at 0.3; section 7 survives with 0.9, but still has to solve the frozen modern production |

### What remains to do (state at the hand-over back to the first machine, 2026-09-21)

Working tree: the generated modern file is REVERTED on the second machine (another session was
committing in the same tree); `python tools/archive/modern_switch_experiment/medium_hull_twins.py
apply --ram 0.9 --brake yes` rebuilds the `test9` state in one command on either machine. Saves
stay where they were made: `modern_bed.hoi4`, `test7a-c`, `test8a-c` on the second machine,
`trade_issue.hoi4`, `conversion.hoi4`, `test1`-`test6` on the first.

| # | Owed | Why | Where it can run |
| --- | --- | --- | --- |
| 1 | **`test9`**: twins at 0.9, brake OPEN, saves +50 d / +75 d / +120 d after the latch | the one-line control of `test8`; decides whether `can_upgrade_in_field` on a source twin does anything at all | either bed. On the first machine from `trade_issue.hoi4` (latch 1943.4.1): save 1943.5.20, 1943.6.15, 1943.8.1 - and read it against a `test8`-equivalent run made on THAT bed, never against the second machine's `test8` |
| 2 | owner `imgui show ai_templates` on GER mid-run (around +60 d): arrow, `Best (role)`, match of the twin and of M | the threshold reading of `test7` / `test8` is ASSUMED; no save carries the arrow | live game only |
| 3 | re-read `test5` / `test6` at LATER dates if those runs can be continued from their saves | both were read at one date (+30 d); `test8` shows the same bed going down then back up, so one date decides nothing | first machine |
| 4 | a HEAD-without-twins control on whichever bed is used | the second machine's baseline came from the cloud build (checksum `5122`), not from HEAD - the rung gap between `test7` and its baseline is unattributed | either |
| 5 | if `test9` = `test8` (brake inert): drop section 7, and put the owner decision on the table - hold the role on the medium shape, prime modern stock with the need-blind `equipment_production_min_factories_archetype` floor, switch once. `test8` measured the missing half of that design: with the role held on medium, modern lines get 0 factories for four months | the twin proposal then has no mechanism left | design, no run |
| 6 | if `test9` descends (brake read at 0.9): section 7 stands with `replace_at_match = 0.9`, and still owes an answer to the frozen modern production of `test8` before any emitter change | a held park with no modern chassis ever built is the arm 0 deadlock | design + one run |
| 7 | `WORK.md` `modern-switch-amorce` still describes a stock seed inside `WA_AI_TEMPLATES_update_modern_chassis_latch`; the effect at HEAD reads `WA_AI_TEMPLATES_modern_line_open` only (MEASURED, `WA_AI_TEMPLATES_effects.txt`), and both campaigns latch with 0 modern chassis | stale tracker text, listed with section 8 | edit when the subject is next touched |

---

## 8. Stale statements found on the way (not edited here)

| Where | What is stale |
| --- | --- |
| `AGENTS.md`, `wa-engine-reference` | engine version 1.19.2 -> the install is 1.19.3.0 |
| `WORK.md` `modern-switch-amorce` | target counts 1368 / 402 / 198 -> 1752 / 258; "100 chassis per division" -> 150-250; blocker (a) "WA enables exactly one target per role" -> false in the light-support family; "bascule4: the park is NOT hollow" was read from strength, the per-division chassis join says otherwise on the current build |
| `modern_convert_spares_min = 100` and the four comment sites `WORK.md` already lists | describe a brake that the saves show is not read where it sits |
