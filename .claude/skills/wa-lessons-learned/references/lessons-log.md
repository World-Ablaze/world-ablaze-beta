# Lessons log

Append-only catalogue of non-obvious causes. Newest entries at the bottom. See `../SKILL.md` for the entry format and when to add one.

Entries dated 2026-08-08 were reconstructed from code archaeology (`# Fix NN:` comments, commit messages) and prior session notes when this log was created; their original dates are unknown.

---

## Scope and control

### `every_controlled_state` does not include subject territory

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Railway and construction logic covering an overlord skipped everything inside its puppets — routes stopped at the puppet border, ports inside puppet states were invisible to the port search.
- **Cause:** Puppet land is controlled by the puppet, not the overlord. `every_controlled_state` iterates only directly-controlled states, so the entire subject sphere was outside the loop.
- **Rule:** When a system must cover a country's whole sphere of influence, iterate `every_subject_country` in addition to `every_controlled_state`. When you duplicate a loop body to add subject support, also relax any `ROOT = { controls_province = X }` check to accept subject-controlled provinces — otherwise the loop runs and then filters everything back out.
- **Evidence:** `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_helpers.txt:404-422` (Fix 24, Fix 27), `:593`, `:673` (Fix 28); `WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt:258-289` (Fix 27).

### `build_railway` ignores the controller

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Uncertainty about whether railway construction needed a controller check before firing.
- **Cause:** `build_railway` is a map modification, not a country action. It works on any province regardless of who controls it.
- **Rule:** Do not add controller gating around `build_railway` for correctness reasons — it will succeed either way. Gate on *whether you want* the railway (eligibility, ownership policy), not on whether the effect can run. Conversely, `controls_province` is the right check when the question is genuinely about control.
- **Evidence:** Behaviour confirmed during railway system work; used throughout `railway_core.txt` route execution.

### Pathfinder province-type parameter

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Routes traversing (or refusing to traverse) allied and puppet territory unexpectedly.
- **Cause:** The pathfinder takes a province-type parameter that decides whose provinces are walkable. Types `0` and `1` allow allied + subject provinces; type `2` allows ROOT + allies + subjects.
- **Rule:** When a route "should obviously work" and does not, check the `_pathfind_prov_type` value at the call site before suspecting the pathfinder itself.
- **Evidence:** `WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt:678` (Fix 21); semantics changed in commit `9aef32f41`, which is what allowed Fix 27 to revoke Fix 25.

## Constants and file boundaries

### Railway eligibility constants are duplicated on purpose

- **Date:** 2026-08-08 (recorded); superseded 2026-08-16 — see the next entry. **The railway constants are no longer `@` at all**: they are HOI4 1.18 script constants in `common/script_constants/wa_ai_railway.txt`, read as `constant:wa_ai_railway.<group>.<key>` from every file, so there is nothing to keep in sync. Kept as history.
- **Symptom:** A threshold changed in one file had no effect on the scheduling gate.
- **Cause:** HOI4 `@` constants are file-scoped. `WA_AI_misc_on_actions.txt` redeclared `@WA_AI_PC_railway_MIN_CIVS_PEACE`, `_MIN_STATES`, `_MAX_SURRENDER`, `_MINOR_CIV_THRESHOLD` because the on-action needed them and could not see the core file's copies. (Fix 75 later removed the on_action copy — it calls `WA_AI_PC_country_can_run_railway_system` in `WA_AI_CONSTRUCTION_triggers.txt` instead — so the pair is now railway_core ↔ triggers, and it is registered.)
- **Rule:** Before changing any `@` constant, grep its name across the repo and update every declaration. When adding a constant that a second file will need, redeclare it there with a `# must match <file>` comment — that is the established convention, not an accident — **and register the pair** (next entry): the comment is for the human, the registry row is for the machine.
- **Evidence:** `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` header of the railway eligibility block (Fix 75 history); `tools/constants_registry.json` groups `railway_eligibility_*`.

### A "must match" comment is not a mechanism — file-scoped constants need a registry and a checker

- **Date:** 2026-08-16 (campaign `af003548` session; Fix 90)
- **Symptom:** `WA_AI_PC_can_afford_project` and the `WA_AI_PC_has_project_civs_16/_20` floors judged affordability at `@AI_MAX_FRACTION_OF_FACTORIES_TO_ASSIGN_ON_PROJECTS_TOTAL = 0.35` while `WA_AI_PC_assign_factories` funded at `@AI_PC_ALLOC_FRACTION = 0.40` — the gate refused ~12 % of the projects the fill would have paid for. The same name was declared a third time in core.txt at 0.35, read by nothing. `events/wa_events_debug.txt` carried a fourth copy at 0.35. `WA_AI_AIFC_helpers.txt` said "must match WA_AI_AIFC_core.txt" about a constant core.txt no longer declared; `WA_AI_AIFC_core.txt` and `railway_strategies.txt` carried five + one "must match" copies nothing in those files read; the per-enemy railway route budget was enforced by a bare literal `4` in the trigger file next to a comment naming a constant that had no reader anywhere. `savegame.py`'s `_PC_TYPE_ID` lacked type 23. None of it was visible in any diff.
- **Cause:** Two things. (1) `@` constants are file-scoped, so every shared quantity is N declarations, and the only thing holding them together was a comment — which the parser does not read and the next fix does not grep. (2) The same quantity lived under two names (`@AI_PC_ALLOC_FRACTION` in the allocator, `@AI_MAX_FRACTION_…` in the gate), so grepping one name found nothing to sync.
- **Supersession (same day, 2026-08-16 afternoon):** the in-game probe (`events/wa_test_constants.txt`, in git history) showed that HOI4 1.18 **script constants** (`common/script_constants/*.txt`, `constant:cat.group.key`) work in every variable context and in the raw numeric triggers the AI code uses, from scripted_effects / scripted_triggers / events — so the shared `@` families were moved there (PC, railway, AIFC, posture: `common/script_constants/wa_ai_*.txt`) and the per-file copies deleted outright. The rule below now applies only to **cross-format** copies (05_defines.lua, 00_buildings.txt, `global.` price table, savegame.py) — a `@` declared in two WA files is a checker ERROR (`SHARED-AT`), not something to register. Not usable in `ai_strategy value =`; untested for `has_country_flag days >` and `fighting_army_strength_ratio ratio >` (those stay `@`, single-file).
- **Rule (original, now for cross-format copies only):** every constant, engine define or building fact that exists in more than one place is a **registered group** in `tools/constants_registry.json` (owner + mirrors + what it governs), and `python tools/check_constants.py` runs before every commit that touches `WA_AI_*` effects/triggers, `05_defines.lua`, `00_buildings.txt` costs/caps or the `savegame.py` tables (AGENTS.md validation table). One quantity, one name — when two files hold the same number under two names, rename the mirror to the owner's name (renames are per file: grep readers, note the old name at the declaration). A mirror nothing in its file reads is a copy waiting to drift: delete it or make it the documented owner. A band or threshold that exists only as a repeated literal is declared as a constant and registered. Skill: `.claude/skills/wa-constants-registry/SKILL.md`; the `wa-architecture-reviewer` subagent runs the checker as part of a pre-ship review.
- **Detection:** `python tools/check_constants.py` (DRIFT / MISSING / UNREGISTERED / DEAD-MIRROR); the HEAD-of-2026-08-16 run reported 2 DRIFT + 4 MISSING + 20 DEAD + 13 UNREGISTERED across 51 groups; clean after the cleanup at 57 groups.
- **Evidence:** Fix 90 comment at `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` (`WA_AI_PC_can_afford_project` header); `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt` "Allocation base constants" block; `tools/constants_registry.json`; `tools/check_constants.py`.

## Railway system specifics

### Port search must be per-target and distance-limited

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Overseas supply routes picked absurd ports — e.g. UK home ports selected for European targets.
- **Cause:** Ports were cached per landmass rather than searched per target, and there was no exclusion of the capital's own landmass.
- **Rule:** Each target gets its own port analysis (BFS ~15 states from the target, same landmass); beachhead/receiving-port candidates must exclude the capital's landmass. Do not reintroduce per-landmass caching as an "optimisation" — it is the bug.
- **Evidence:** Fix 26 — `railway_helpers.txt:906-921`, `railway_strategies.txt:123`, `:557`, `:951`; mirrored in `zz_debug_effects.txt:426-480`, `:608-701`.

### Same-landmass failures need an overseas fallback

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Frontlines that were technically on the same landmass got no railway at all when the land route scored PARTIAL or FAIL.
- **Cause:** The land-route path had no fallback; overseas logic was only reachable for genuinely separate landmasses.
- **Rule:** A same-landmass route returning PARTIAL/FAIL should fall through to the overseas supply-chain path rather than abandoning the target.
- **Evidence:** Fix 28 — `railway_strategies.txt:175`, `:359`, `:986`, `:1107`.

## Testing

### Japan is not an Axis faction member in World Ablaze

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Geographic tests asserting Japanese conquests failed despite Japan holding the territory.
- **Cause:** WA has Japan leading its own faction with its puppets, unlike vanilla's Tripartite arrangement. `is_in_faction_with = GER` is false for Japan.
- **Rule:** Use `WA_TEST_is_controlled_by_JAP_aligned_country` for Japanese geographic assertions; never test Japan via `is_in_faction_with = GER/ITA`.
- **Evidence:** `documentation/WA_TEST_WRITING_GUIDELINES.md`, "Geographic Control Tests"; helpers in `common/scripted_triggers/WA_TEST_triggers.txt`.

### The scripted test harness needs seven registrations per test

- **Date:** 2026-08-08 (recorded)
- **Symptom:** A new harness test silently never ran, or ran but never reported a result.
- **Cause:** The `WA_TEST_RW_*` harness spreads one test across seven places; missing any one fails quietly.
- **Rule:** Adding a test to a `WA_TEST_*` harness means touching all of: init block, `log_summary` counter, `print` row, `launch_all` entry, `check_all` timeout check, `check_all` result check, checker-event re-launch entry, and the checker event's ongoing/waiting counters. Also: the suite runs as **JAP**, tests 012+ scope to **ITA**, and all test state variables live on the suite host (JAP) even when asserting about another country — that is intentional, do not "fix" it.
- **Evidence:** `common/scripted_effects/WA_TEST_railway.txt` (`WA_TEST_RW_init:61`, `_log_summary:215`, `_print:320`, `_launch_all:693`, `_check_all:709`), `events/wa_events_test.txt`.

### A failing test may be the test's fault

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Test failures attributed to AI regressions that had not occurred.
- **Cause:** Same-date inverse `fail` blocks firing before the AI could plausibly act; strict `>` / `<` off by one day; state IDs assumed rather than looked up.
- **Rule:** Before concluding the mod regressed, re-read the test: can `success` and `fail` both be true on the same tick? Is the date boundary off by one (`>` is strict)? Was the state ID verified against `history/states/`? Load the `TEST_FAIL_<name>_<date>.hoi4` save the framework writes — it shows the actual board state.
- **Evidence:** `documentation/HOI4_TESTS_AND_TRIGGERS_NOTES.md`, "Choosing Dates" and "Review Checklist".

## Repository hazards

### Deleting content in a `replace_path` folder removes it from the game

- **Date:** 2026-08-08 (recorded)
- **Symptom:** N/A — this is the failure mode the mod's structure invites.
- **Cause:** `descriptor.mod` declares ~70 `replace_path` entries. For those folders HOI4 loads only this mod's files; vanilla content is not loaded and does not fall back.
- **Rule:** Treat files in replaced folders as the complete content of that category. A parse error or an over-eager deletion can silently drop unrelated definitions. Check brace balance before finishing any edit in `common/`, `events/`, or `tests/`.
- **Evidence:** `descriptor.mod`; `AGENTS.md` "Project Context".

### A `replace_path` folder the mod only partly populates silently deletes the rest

- **Date:** 2026-08-14
- **Symptom:** `equipment_effects.cpp:814` — `common/national_focus/bulgaria.txt:3551: create_equipment_variant': 'Drazki Class' - Invalid name group 'BUL_DD_HISTORICAL'.` The group is standard vanilla content and reads as though it must exist.
- **Cause:** `descriptor.mod` declares `replace_path="common/units/names_ships"`, but the mod ships only **12** files there against vanilla's **~65**. Every country outside those 12 therefore has *no* ship name groups in the running game. The general shape: a replaced folder that the mod populates *selectively* is not a curated subset, it is a deletion of everything else — and the deletion is invisible in the diff, because nothing was ever deleted from the repo.
- **Rule:** For any `replace_path` folder, "the mod has files here" is not the same as "the category is covered". Before referencing a vanilla-defined name from mod script, check the folder is fully populated: `ls` the mod folder against the vanilla folder and diff the filename sets. When you add a reference to something vanilla defines in a replaced folder, restoring the vanilla file into the mod is the fix, not renaming the reference.
- **Corollary about logs:** the engine reports these only when the referencing code *runs*. Five of the six live bad references in this sweep sat behind focuses and decisions the campaign never took, so `error.log` showed one. **Treat a runtime log as a lower bound on a defect class, never as its inventory** — grep the whole repo for the construct and validate every site. In debug, `research all` on a tagged country is a cheap way to force every `on_research_complete` body to execute at once.
- **Evidence:** `descriptor.mod:84`; checklist R45; the six references were `BUL_DD_HISTORICAL`, `ICE_CA_HISTORICAL`, `NOR_DD_HISTORICAL` ×2, `POR_DD_HISTORICAL` ×3, `POR_CL_HISTORICAL` ×3.

### Documentation drifts from source

- **Date:** 2026-08-08 (recorded)
- **Symptom:** `documentation/PDXSCRIPT_LANGUAGE_NOTES.md` states that `descriptor.mod` has `version="1.10.4"` while `AGENTS.md` says 1.18.0, and advises trusting the descriptor.
- **Cause:** The descriptor has since been updated to `1.18.0`; the note was accurate when written and is now stale.
- **Rule:** Docs here are authoritative for *design intent* (especially `WA_AI_MILITARY_SYSTEM.md` and `WA_AI_RAILWAY_SYSTEM.md`) but verify *facts* — version numbers, line references, file inventories — against the source before relying on them. Line references in the railway doc in particular drift as the files change.
- **Evidence:** `documentation/PDXSCRIPT_LANGUAGE_NOTES.md:25` vs `descriptor.mod:1`.

### `create_unit` cannot reference a template by name when the country is AI

- **Date:** 2026-08-08
- **Symptom:** `Malformed token: <template name>` + `unit in <province> has no division template set` + `create_unit -- division string was not parsed correctly`, fired three times (once per `count`) from a focus completion reward.
- **Cause:** The AI redesigns and renames its own templates from `common/ai_templates/WA_AI_TEMPLATES_*`, so no template name — not even one from the country's `history/units/` OOB — is guaranteed to still exist by the time an AI completes the focus. Human players are safe only because WA ships starting templates with `is_locked = yes`, which blocks renaming until a focus unlocks them.
- **Rule:** Any `create_unit` reachable by the AI must create the template it spawns in the same effect block, immediately before the `create_unit`. Never gate a `division_template = { ... }` on `is_ai = no` while leaving the matching `create_unit` ungated. Where two focuses spawn the same template, extract it to a scripted effect and call that from both.
- **Evidence:** `common/scripted_effects/AST_scripted_effects.txt` (`AST_create_australian_infantry_division_template`), called from `common/national_focus/australia.txt` in `AST_rats_of_tobruk` and `AST_raise_additional_brigades`. Working precedents: `"Home Guard Unit"` in `australia.txt`, `"Canadian Mountaineer Division"` in `canada.txt` — both ungated.
- **Related:** When a scripted template is shared by player and AI, mirror its composition on the matching `WA_AI_TEMPLATES_GENERIC_*` entry in `common/ai_templates/` rather than hand-rolling one, so the scripted division matches what the AI designer would field. Watch the tech requirements of the support companies you copy — the generic entries assume the AI designer's tech gating, which a scripted `division_template` does not reproduce. Check each sub-unit's `active` flag in `common/units/`: `active = no` means a technology must enable it. See the next entry for which of those technologies are safe to put in a focus `available`.

### Never gate a focus on a technology whose AI research weight is conditional

- **Date:** 2026-08-08
- **Symptom:** None yet — this is a latent deadlock, and it would be silent. A focus becomes permanently unreachable for the AI with nothing in the log.
- **Cause:** Every technology's `ai_will_do` is zeroed by `NOT = { WA_AI_RESEARCH_needs_<x> = yes }`. Some of those triggers are `always = yes`; others depend on a `WA_AI_CONFIG_*` archetype. Gating a focus on a conditional one couples the focus tree to an archetype list in a file that does not reference it, so removing a tag from that list silently locks the focus.
- **Rule:** A focus may hard-gate on a technology only if its `WA_AI_RESEARCH_needs_*` trigger is unconditional. In `WA_AI_RESEARCH_support.txt` the safe ones are `tech_support`, `tech_engineers`, `tech_recon`, `tech_military_police`, `tech_field_hospital`, `tech_logistics_company`, `tech_signal_company` and camo. The unsafe ones are `tech_maintenance_company` (armoured/mechanized archetypes only), armoured trains and railway guns (`is_major`), trains (`NOT is_major`) and radar. When a scripted division needs an unsafe one, branch the `division_template` on `has_tech` and drop that company in the fallback rather than gating the focus.
- **Evidence:** `common/scripted_effects/AST_scripted_effects.txt` branches on `has_tech = tech_maintenance_company`; `AST_raise_additional_brigades` gates only on `tech_signal_company`. `common/scripted_triggers/WA_AI_RESEARCH_support.txt:18` vs `common/scripted_triggers/WA_AI_CONFIG.txt:391` (AST is in `use_mechanized_divisions` today — that is the only reason the tech is currently researched at all).

### Advisor and leader effects need the character recruited first

- **Date:** 2026-08-08
- **Symptom:** `Cannot find advisor with idea token <token> for country in scope <TAG>` from `activate_advisor`; `add_country_leader_role: Character does not exist`.
- **Cause:** Defining a character in `common/characters/` does not give any country that character. Until a `recruit_character` runs, the country has no such character and both effects fail.
- **Rule:** When adding a character used only by a later event or focus, add the matching `recruit_character` — in `history/countries/` if the character should exist from 1936, or in the event's own effect block if a start-of-game entry would show an unwanted greyed-out advisor slot. Role-less placeholder characters are recruited at start by convention (see `AST_iven_mackay`, `SPR_anarchist_commune`).
- **Evidence:** `history/countries/SPR - Spain.txt:278` (`SPR_julian_gorkin`, used by four `add_country_leader_role` calls in `events/LAR_Spain.txt`); `events/wa_chi_events.txt` `chi_armor.822` (`CHI_huang_guangrei`).

### Never delete an inherited template by a name the annexing country also owns

- **Date:** 2026-08-08
- **Symptom:** A large part of the German AI army vanished a day or two after the Anschluss.
- **Cause:** `delete_unit_template_and_units` matches on the template *name string*, and `annex_country = { transfer_troops = yes }` merges the target's templates into the annexer's list without renaming collisions. `ger_armor.904` cleaned up the inherited Austrian templates by name, and with Götterdämmerung installed Austria's OOB (`history/units/AUS_ww_1936.txt`) named its line infantry `"Infanterie Division"` — byte-identical to Germany's own template in `GER_1936.txt` / `GER_1936_land_nsb.txt`. The cleanup therefore destroyed the German line infantry too. Without `disband = yes` the equipment and manpower were destroyed rather than returned. The non-DLC OOB `AUS_1936.txt` used `"Oster Infanterie Division"` and was unaffected, so the bug only reproduced on one DLC branch. It was masked in intent by `ger_armor.901`, which would have deleted GER's starting templates in 1936 — but it is gated on `has_country_flag = infantry_template_ger`, a flag no file in the repo ever sets, so it never fires and GER still holds the vanilla template names in 1938.
- **Rule:** Templates deleted by name after an annexation must carry a name unique to the *donor* country. Before adding a `delete_unit_template_and_units` line, grep the annexer's `history/units/*.txt` for that exact name. Keep every DLC branch of a country's OOB using the same template names, so a cleanup written against one branch is correct for all of them. Always pass `disband = yes` unless destroying the equipment is the intent.
- **Evidence:** `events/WA_AI_GER.txt` `ger_armor.904`; `history/units/AUS_ww_1936.txt` vs `history/units/AUS_1936.txt`; `history/countries/AUS - Austria.txt:3-16` (the Götterdämmerung OOB branch); `events/Germany.txt` `germany.4` (`annex_country = { target = AUS transfer_troops = yes }`). The correct pattern is the rest of the family — `ger_armor.903` and `GER_trash_template_fix` in `common/decisions/z_WA_ai_GER.txt` — which only name donor-unique templates (`"Oster Infanterie Division"`, `"Pesi Divize"`, `"French Heavy Tank Division"`).

### A scripted division template must not name equipment the country cannot design

- **Date:** 2026-08-08
- **Symptom:** `equipmentpool.cpp: Trying to fill variant where none exist from type: anti_tank_equipment belonging to Australia`, repeated once per spawned division and paired with the same line for `anti_air_equipment`.
- **Cause:** `create_unit` asks the equipment pool to fill every sub-unit in the template. A sub-unit whose archetype has no unlocked *variant* for that country produces this line. Sub-unit availability and equipment availability are two different gates: a `division_template = { ... }` effect happily places a company the country has no design for. `AST_create_australian_infantry_division_template` was copied from `WA_AI_TEMPLATES_GENERIC_HEAVY_INFANTRY_30_MIX_MOT`, which carries AT battalions plus AT and AA companies — but `WA_AI_RESEARCH_needs_anti_tank` and `_needs_anti_air` are false for a non-major before 1940, and `history/countries/AST - Australia.txt` starts with `eng_heavy_anti_air_1` and `eng_heavy_artillery_1` but no light AA and no AT line.
- **Rule:** Before writing a scripted `division_template`, check each sub-unit's equipment archetype against the country's `set_technology` block and against the matching `WA_AI_RESEARCH_needs_*` trigger. Where the archetype is not guaranteed, build the base template with `division_template` and bolt the conditional part on with `add_units_to_division_template` under `limit = { has_design_based_on = <archetype> }`. Note that `heavy_anti_air_equipment` / `heavy_artillery_equipment` are separate archetypes from `anti_air_equipment` / `artillery_equipment` — having one says nothing about the other.
- **Evidence:** `common/scripted_effects/AST_scripted_effects.txt`; `common/scripted_triggers/WA_AI_RESEARCH_army.txt:44` and `:59`; `common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt:85-95` uses the same `has_design_based_on` gate before spawning.

### Two support companies sharing `same_support_type` cannot coexist in one template

- **Date:** 2026-08-08
- **Symptom:** `effectimplementation.cpp: add_units_to_division_template Not allowed to add support regiment (Military Police) to template Camicie Nere` — a rejection, not a parse error, so the rest of the effect still applies.
- **Cause:** WA defines several themed variants of the same support role — `military_police_horse_company_divisional`, `ss_officers_mot_company_divisional`, `blackshirt_officers_mot_company_divisional`, `garde_imperiale_officers_mot_company_divisional`, `nkvd_commissars_officers_mot_company_divisional` — all carrying `same_support_type = divisional_military_police` in `common/units/support_military_police.txt`. The engine allows one per template. `"Camicie Nere"` ships with the blackshirt officers company in its OOB, so `ITA_strengthen_the_blackshirts` could never add a plain MP company on top. The free support slot in the column is irrelevant; the check is on the support type, not on space.
- **Rule:** Before adding a support company to an existing template, grep that sub-unit's `same_support_type` and check no sub-unit already in the template shares it. The themed officer companies are the usual trap because their names do not contain `military_police`.
- **Evidence:** `common/national_focus/italy.txt` `ITA_strengthen_the_blackshirts`; `history/units/ITA_1936_land_nsb.txt:52-60`; `common/units/support_military_police.txt:56, 114, 216, 318, 424, 526`.

### `set_nationality` fails on characters that already hold an advisor role

- **Date:** 2026-08-08
- **Symptom:** `character.cpp: set_nationality: <generated name> already has an advisor role with slot type intelligence_minister`, one line per character, from a blanket `every_character = { set_nationality = X }`.
- **Cause:** `set_nationality` re-adds the character's roles on the destination country, and the engine refuses a second advisor role in a slot the character already occupies. The characters that trip it are usually the generic advisors the AI hired rather than anything the mod authored — TUG's three scripted characters are a country leader and two commanders, and transferred cleanly.
- **Rule:** Filter blanket character transfers with `limit = { is_advisor = no }` unless moving the advisors is actually the intent. Transferring the AI's generated advisors is rarely worth anything to the receiving country anyway.
- **Evidence:** `common/on_actions/100_wa_on_actions.txt` `on_capitulation` TUG → XSM. The sibling GNS → GER block a few lines below has the same shape and the same latent warning.

### Frame 0 of an army icon sheet must stay a generic, tintable icon

- **Date:** 2026-08-08
- **Symptom:** Every army icon in the theatre panel drawn plain white instead of the country's map colour, for all countries — while army *group* icons stayed correctly coloured.
- **Cause:** `gfx/army_icons/army_icons.txt` lists one `icon = {}` block per frame of the matching `.dds`, in frame order. An icon with no `color_override` line is tinted with the country colour at runtime — that is why vanilla ships its generic symbols (shield, castle, spade, anchor…) as flat greyscale on frames 0-14. `color_override = no` means "keep the texture's own colours" and belongs on named historical insignia, which are authored pre-coloured. The third-party pack in this repo (399 frames instead of vanilla's 81, added in `25e92838e`) inserted 36 Japanese insignia *ahead* of vanilla's generic block, pushing the generics to frames 36-49 and 161-175. Frame 0 became `"Infantry"` — a white NATO symbol carrying `color_override = no` and gated `available = { tag = JAP tag = USA }`. Frame 0 is what an army gets when nothing has been chosen, and that default ignores the `available = {}` gate, so every country's armies rendered it untinted. The army-group sheet kept a generic tintable frame 0, which is why group icons were unaffected.
- **Rule:** Frame 0 of each `gfx = ...` block must be a generic icon with no `color_override` line. Do not fix this by stripping the flag from greyscale historical insignia — many are legitimately monochrome (Panzer division runes, British formation signs) and are meant to render in their own colours; stripping it there is wrong even though it also removes white. Fix it by moving a generic icon onto frame 0, which means editing the `.dds` sheets and the `.txt` together since the two are index-locked.
- **Evidence:** `gfx/army_icons/army_icons.txt`; sprite frame counts in `interface/theatreselector_ai.gfx` (399/19) override `interface/theatreselector.gfx` (81/6) because `_ai` sorts later; `interface/theatreselector.gui:73` `orders_group_item` draws `GFX_theatre_army_shield`.

### Savegames store script variable names lowercased

- **Date:** 2026-08-09
- **Symptom:** Grepping a savegame for `WA_AI_AIFC_sector_states` (or any `WA_AI_*` variable) finds nothing, suggesting a system never ran — while flags, idea names, and dynamic modifier names DO appear with their original casing.
- **Cause:** HOI4 serializes script *variables* into the save with lowercased names (`wa_ai_aifc_sector_states^0=17`). Flags and token references keep their authored case. A case-sensitive search therefore "proves" a false negative for variables only.
- **Rule:** When diagnosing AI state from a savegame, search variables case-insensitively or in lowercase. A missing lowercase variable is meaningful (the system genuinely never wrote it); a missing uppercase one is not.
- **Evidence:** `GER_1944_10_29_06.hoi4` diagnosis session — zero hits for `WA_AI_AIFC` vs 6 countries holding `wa_ai_aifc_sector_*` state.

### `alliance_strength_ratio` is worldwide - never gate theatre behaviour on it

- **Date:** 2026-08-09
- **Symptom:** Allied AI sat passive in France for the entire late war despite crushing local superiority; the "attack Germany" execution block never fired in any campaign where the Axis stayed near global division parity.
- **Cause:** `WA_AI_MILITARY_ALLIES_exec_vs_germany` was gated on `alliance_strength_ratio > 2`, which compares the *worldwide* strength of ROOT's faction against *all* its enemies. With the Allies at 706 divisions vs the Axis at 766, the gate could never pass — no amount of local superiority in one theatre moves a global ratio.
- **Rule:** For "should we attack X" decisions use `fighting_army_strength_ratio = { tag = X }` (engaged armies only, expeditionaries count wherever they stand) or the offensive posture system (`WA_AI_MILITARY_posture_effects.txt`), which owns this calculus. Reserve `alliance_strength_ratio` for genuinely global questions (join war, capitulation panic).
- **Evidence:** `common/ai_strategy/WA_AI_MILITARY_FACTION_ALLIES_FRONT.txt` `exec_vs_germany`, 1944 France passivity diagnosis; fixed by gating on `WA_AI_MILITARY_posture_vs_GER`.

### `every_controlled_state` also blinds expeditionary powers, not just overlords

- **Date:** 2026-08-09
- **Symptom:** USA — the largest army in liberated France — never received an AIFC sector: no anchor, no corridor, not even the bookkeeping age variable.
- **Cause:** AIFC candidate collection walked `every_controlled_state` for enemy-adjacent states. An expeditionary power fights entirely from faction members' soil and *controls* none of it, so the scan came up empty every week. This is the same scope trap as the railway system's puppet fixes (24/25/27), in a third costume: puppets, controllers, and now expeditionary allies.
- **Rule:** Any "where can I act" scan built on `every_controlled_state` must decide explicitly whether allied/subject territory where ROOT has divisions counts. If it should, add a fallback pass over faction members' controlled states filtered by `ROOT = { divisions_in_state = { state = PREV size > N } }` — and mirror the same relaxation in the corresponding validity check, or the selected state dies on the next validation.
- **Evidence:** `WA_AI_AIFC_helpers.txt` / `WA_AI_AIFC_core.txt` Fix 28; savegame showed ENG/FRA/CAN with sectors, USA/ITA with none.

### Wartime economic fatigue has no relief valve except war bonds - and the AI never entered the ladder

- **Date:** 2026-08-09
- **Symptom:** AI ENG imported zero resources from March 1943 to the end of the war despite ~4,600 free convoys, huge deficits, and willing sellers; trade window showed 218/218 civilian factories used, fuel at 0.
- **Cause:** A chain. (1) Per-law fatigue missions (`_economy_fatigue.txt`) add +1 every 28-35 days for each heavy economy/conscription law, and every healing decision requires `has_war = no`, so at war fatigue only rises unless war bonds drain it. (2) The AI's only entry into the bond ladder is the vanilla law AI buying `Series_A_bonds` for 50 PP (`ministry_of_defence` slot) at a flat weight of 400 - not PP shortage (ENG held 114-190 PP through 1941-43) but priority: on majors with many competing PP sinks the purchase loses the AI's pick for years, so ENG sat on `No_bonds` until ~mid-1945 and its fatigue climbed 19 -> 93 while 16+ other AIs entered the ladder earlier. (3) At fatigue > 89, `WA_AI_can_take_civilian_economy` becomes true and the weekly `WA_AI_upgrade_economy_law` demotes the country to civilian economy mid-war (scripted `add_ideas` bypasses the idea's peace-only `available`); civilian economy's 40% consumer goods + fatigue's +17% then eat the entire civilian factory pool, and with zero spendable civs the engine AI cannot open any resource trade. War support < 0.15 blocks every re-mobilization path, locking the state permanently. Also latent: `upgrade_warbonds` F->G branch checked `has_idea = Series_G_bonds` instead of F (dead-ends the ladder at F); `afo_event.23` had no `ai_chance` (25% random permanent opt-out); repay missions are AI-selectable at fatigue > 39 but uncompletable at war (`available` requires peace) - guaranteed +10 timeout that destroys the bond.
- **Rule:** Any recurring wartime cost whose relief decisions are peace-gated MUST have a scripted AI path that exercises the wartime relief mechanism - a flat `ai_will_do` on a custom-slot law competes against every other political-power sink, so scale the weight with the need it answers or decision-heavy majors will defer it for years. When a mission is uncompletable in some state, gate its `ai_will_do` to zero in that state.
- **Meta-rule (diagnosis):** Before diffing two saves as "the same campaign", check file mtimes and system fingerprints (decision counter names, variable names present). This repo updates mid-timeline constantly; an old save on a pre-overhaul system diffs against a new save as impossible state transitions (here: a phantom "Series_C -> No_bonds fall"). Also never scan a fixed-size window past a country block's end - brace-match the block first, or the next country's flags get attributed to the wrong tag (a `SOV` flag masqueraded as ENG's for half this investigation).
- **Evidence:** Current campaign (all saves mtime 2026-08-08/09): ENG `No_bonds` + fatigue 19->93 at every snapshot 1937-1945.3, `Series_B` only by 1945.11; 16 AI countries hold `auto_upgrade_warbonds`; ENG at 49.2 PP in Oct 1944. Old campaign save (mtime 2026-04-29, pre-June-10 warbonds overhaul) held the misleading Series_C state. Root-cause fix: the bond series' flat `ai_will_do` (400-1000) loses the AI's political-power pick to routine decision spending for years on decision-heavy majors (adoption delay correlated with decision load: CAN 2 months, SAF 1 year, RAJ 2 years, NZL 4, AST 4.5, ENG 5.7) - now scaled by fatigue tier (x2 at 25+, x2 at 50+, x2.5 at 75+) in `zzz_ministries.txt`. Plus the F->G copy-paste fix in `Economy_Fatigue_scripted_effects.txt`, `ai_chance` on `afo_event.23` (was a 4-way coin flip with 25% permanent opt-out), and peace-gating repay `ai_will_do` in `_warbond_payback_decisions.txt`. A scripted issuance effect was considered and rejected: the AI handles the ladder itself once the priority is right.

### A "garrison country" needs a bootstrap path, and delegating defense needs a fallback

- **Date:** 2026-08-09
- **Symptom:** AI Germany had 2 divisions in all of metropolitan France pre-D-Day; the Channel coast (states 14/15/29) had zero forts while Biscay had 67+ coastal bunker levels.
- **Cause:** Three interlocking failures. (1) The RCZ garrison-country design gates ALL of GER's own atlantik_wall put_unit_buffers on `NOT has_country_flag = RCZ_garrison_flag` - but the flag is set unconditionally in GER's history file and RCZ exists from 1939, so GER never defends its own west. Design intent (author): RCZ is a *complement*, not the main defender. (2) RCZ itself could never field a division: `ger_armor.999` deletes all its templates, and `WA_AI_TEMPLATES_has_infantry_focus_completed` is a focus whitelist a released tag can never satisfy, so the monthly template system never creates one - 500k manpower and a full stockpile sat unused for the whole war. (3) The GER Atlantic Wall fort decisions self-lock: each running project eats 70 civs, every `_start` has `factor = -9999` below 200 available civs, start and stop are the same toggle decision, and `remove_effect` re-arms unconditionally - so the first two sectors started (Biscay + Benelux) ran forever and blocked the Channel sectors permanently.
- **Rule:** When one country's duty is delegated to another (garrison country, expeditionary guarantor), the delegator's own behaviour must stay on as a floor, and the delegate needs a verified bootstrap (template + equipment + recruitment driver) - check the save for actual divisions, not just for the event having fired. For repeatable toggle decisions with a `days_remove` cost modifier, the AI path must self-terminate in `remove_effect` at a cap; never rely on `ai_will_do` to stop a running project (it only gates the toggle, and a `factor = -9999` availability gate blocks stopping too).
- **Evidence:** `GER_1944_06_23_20.hoi4`: RCZ block has zero `division_template`; GER flags `GER_atlantik_wall_west_france`/`_benelux` set 1942.4.6 still active June 1944 with cost variable at 144 (cap 36); France garrison = ITA 13 / GER 2. Fixed by removing the RCZ gates from 6 GER blocks, bootstrapping RCZ in `ger_armor.999` via `WA_AI_DIVISION_spawn_divisions`, adding `has_idea = GER_okw` to the template whitelist, and self-terminating the fort decisions at their caps.

### AI political power vanished into scripted leader recruitment and a write-only reserve

- **Date:** 2026-08-09
- **Symptom:** AI ENG never bought war bonds, advisors, or anything else visible with political power - even when console-given thousands of PP, the pool drained with no identifiable purchases. Decision counters for 1941-43 showed almost exclusively cost-0 AI-helper decisions, yet ~1,000+ PP was spent.
- **Cause:** Two scripted sinks outside the visible decision/law economy. (1) `WA_AI_recruit_general` / `WA_AI_recruit_marshal` (`WA_AI_leader_recruitment_effects.txt`, called every ~2 days) charge `5 x total recruited army leaders` per recruit. A major like ENG starts with ~45 leaders, so every general cost 225+ PP and the cost inflated with each hire (ENG: 50 -> 75 unit leaders over the war = thousands of PP). Console-gifted PP just triggered a chain of recruits at ~250-300 each. The escalating cost was redundant anti-spam - the `divisions/generals > 18` gate already limits recruiting. (2) `WA_AI_store_PP` deducted 15 real PP per pulse into `WA_AI_stored_PP`, a variable nothing ever read or spent (scripted law changes use free `add_ideas`) - ~150-210 PP destroyed per AI country. Bonus bug: in `WA_AI_recruit_marshal`, the "promote a general instead" block was nested as the `else` of the logging-flag `if`, so with logging off every scripted marshal recruit ALSO promoted a general to marshal (second marshal + 15-30 extra command power).
- **Rule:** Any scripted effect that deducts `political_power` competes invisibly with the entire vanilla PP economy - audit these first when an AI "buys nothing": grep `add_political_power = -` in `WA_AI_*` files before blaming the vanilla spender. Scripted costs must be bounded (clamp), must scale with what they gate (not with roster size a major starts with), and a "reserve" variable that is only ever written is a PP shredder, not a reserve. Watch `else = {}` placement after a trailing logging `if` - it binds to the log check, not the block you meant.
- **Evidence:** ENG PP 20-190 across 1939-45 saves while `wa_ai_stored_pp` sat at 150-210 unspent; unit_leaders 50 -> 56 -> 62 -> 75; decision-counter diff 1941->43 contained no PP-costed purchases. Fixed by converting recruitment to command power (2 x leaders, clamped 10-50, mirroring `NDefines.NPolitics.ARMY_LEADER_COST` - recruitment is a military cost and should never have touched political power), restructuring the marshal else, and removing `WA_AI_store_PP` (effect + pulse call).

### `fighting_army_strength_ratio` is pairwise - coalition members can never pass it against a major

- **Date:** 2026-08-09
- **Symptom:** With the posture system live, ENG (and CAN, AST, RAJ) reached posture 1 against every Axis *minor* but stayed at 0 vs GER/ITA/JAP — no "POSTURE: vs Germany" line in game.log, no battleplanning in France. Only the USA passed vs Germany.
- **Cause:** `fighting_army_strength_ratio = { tag = X }` compares ROOT's own fighting army against X's *entire* fighting army. In a coalition war each member individually fails that comparison against a major even when the coalition together holds a 2:1 edge — the exact class of bug the posture system replaced (`alliance_strength_ratio` was too global; the pairwise trigger is too local).
- **Rule:** Any "can we beat X" gate needs a second branch alongside the pairwise one - and make it *front-local*, not a global force sum. Global sums (battalions, divisions) are quality-blind and mix separate wars twice over: a member's Pacific army votes on its European verdict, and the enemy's whole army inflates the denominator even though most of it faces someone else (Germany's SOV-front divisions are not what ENG meets in France). The posture calculus counts divisions standing on the shared contact line - the enemy's front states and our states across them - via banded `divisions_in_state` ladders (no numeric getter exists), armour double-weighted, coalition membership restricted to faction/subject countries *at war with that enemy*. Locality also makes the co-belligerent question moot: SOV needs no place in ENG's numerator once GER's eastern divisions are out of ENG's denominator.
- **Evidence:** `ENG_1944_07_03_03.hoi4` posture variables (21 per-enemy entries: all minors at 1, all majors at 0); front-local branch and `WA_AI_MILITARY_posture_count_state_divs` in `WA_AI_MILITARY_posture_effects.txt`.

### Allied AI aviation grounded in the US/UK - air basing is a construction problem, not an air-strategy problem

- **Date:** 2026-08-09
- **Symptom:** Oct 1944 save: ~7,300 of USA's 15,300 planes parked in continental US bases with no mission, RAF mostly standing by in the UK, liberated French airfields near-empty; GER flew 66 wing-pools over France vs 33 allied.
- **Cause:** Layered basing shortage, not missing mission logic. (1) WA sets `NDefines.NBuildings.AIRBASE_CAPACITY_MULT = 100` - half of vanilla's 200 planes per airbase level - so the 1936-era UK bases fill with the RAF alone. (2) ENG's construction queue (`events/WA_AI_construction.txt` WA_AI_C.0) contains zero `WA_AI_queue_AIR` calls and no PC strategy built airbases in Britain, so UK capacity never grew all war; the engine then finds no free capacity in range of the front and USA wings never cross the Atlantic (cheat-adding UK airbases made the USA rebase immediately). (3) `common/ai_strategy` is a `replace_path`, and the mod ships no `strategic_air_importance` for USA at all - vanilla's Europe-push guidance is deleted, not overridden. Aggravators found in `ENG.txt`: `Allies_bombing_germany_is_too_costly` enables at <900 deployed strat bombers but only aborts at USA>2100/ENG>1500 (ENG had 552 in late 1944, so Germany's air regions sit at -1,000,000 importance indefinitely; CAN has no abort clause at all), and `battle_of_britain_priority` (+500,000 on UK home regions) is gated on `GER = { is_ai = no }` with no other end condition, so it runs for an entire human-Germany campaign.
- **Rule:** When AI planes sit grounded, audit basing capacity *in range of the front* before touching air strategies: capacity per level is a define WA halves, and airbase construction only happens where a script explicitly queues it. Check hysteresis on every enable/abort threshold pair (a `<900` enable with a `>2100` abort is a trap the force-size curve may never escape) and remember save `ai` blocks only store engine/dynamic strategies - static `ai_strategy` blocks must be evaluated by hand against save state.
- **Evidence:** `USA_1944_10_04_08.hoi4`: ENG-controlled land bases 3,543/10,300 planes worldwide but UK hosting states saturated; 122/126 USA and 51/73 ENG wing-pools missionless; all allied missions in region 19 (France). Fixed by `WA_AI_build_uk_air_hosting_capacity` (PC strategy, ENG builds central/southern England airbases sized to 50% of faction deployed planes) + `WA_AI_uk_air_hosting_state` trigger. Aggravator blocks in `ENG.txt` fixed 2026-08-09: `Allies_bombing_germany_is_too_costly` rescaled to WA force sizes (enable < 300, abort > 450 deployed strat bombers) with a shared `date > 1944.2.1` abort backstop that also covers CAN, plus an `any_allied_country` size > 450 abort branch so faction partners that never build bombers (CAN fielded zero all campaign) stop suppressing the shared regions once any ally masses the raid force; thresholds verified against campaign 973154a7 wing counts (`strat_bomber` + `heavy_strat_bomber` both have `type = strategic_bomber` in `common/units/air.txt`, so the trigger counts their sum): ENG 84 (Sep 41) / 203 (Mar 42) / 761 (Mar 43) / 552 (Oct 44) / 469 (Mar 45), USA 300 (Mar 42) / 900 (Mar 43) / 2400 (Jun 44) — ENG and USA both cross the 450 abort during late 1942/early 1943 and never fall back under the 300 re-enable; `allies_avoid_bombing_austria_prussia` given a `date < 1944.2.1` enable backstop because AI USA (tier 2 in Oct 1944) never reaches the `usa_strategic_bomber_5` gate (start_year 1944) in time; `battle_of_britain_priority` had already been given Sealion-threat enable conditions + `abort_when_not_enabled` in an earlier pass. The `battle_of_britain_priority` aggravator was subsequently bounded (2026-08-09): its enable now also requires an enemy-controlled Channel invasion coast (states 6/7/29/785/1016/15/14) and no allied foothold on that coast or in Paris (16/855), so the +500,000 arms only between the fall of France and a successful allied landing, and re-arms if a beachhead is destroyed.

### Flag-gated ai_template targets re-run the decommission pass when the flag first sets - the garrison fix only protected the 1936 window

- **Date:** 2026-08-09
- **Symptom:** In the first post-garrison-fix observer campaign (973154a7, run overnight 2026-08-09), ENG/SOV/USA - all `WA_INFANTRY_TEMPLATE = 1006` countries - still lost their national line infantry templates. Jan 1938 save: `Strelkovaya Diviziya` / `Infantry Division` alive and holding the infantry role (the fix held through the 1936 window). May 1939: ENG and SOV have the flag at 1006 (set when their infantry focus completed), nationals obsolete or already deleted, engine-lettered `Infantry template A..G` ladders in their place. USA followed 1940-41 when its focus fired. Same fate for ROM/ITA/JAP (1004) and FIN (1001); countries whose infantry focus never completed (HUN, SPA - no flag) kept their nationals.
- **Cause:** The engine's one-template-per-role pass is not a one-shot 1936 event - it re-runs whenever the set of enabled `ai_templates` targets changes. `WA_AI_TEMPLATES_calculate_all_templates` gates infantry on the infantry focus, so `WA_INFANTRY_TEMPLATE` flips from unset (FALLBACK target enabled via `NOT has_country_flag`) to its final value mid-campaign. The newly enabled target has a different composition (e.g. 1006: 10 heavy/3 art/2 AT + mot support vs FALLBACK's 15 heavy inf), so the designer creates its own lettered template for it, gives it the role, and decommissions the national - the exact mechanic the 2026-08-09 garrison-target fix suppressed for the 1936 window. Downstream effects: the decommissioned national is frozen (never recruited again) and eventually deleted at zero divisions; the division creator's `has_template` check does not see decommissioned copies, so every spawn wave re-created `Infantry Divisíon` and the engine re-decommissioned it (`Infantry Divisíon 2..9` locked-obsolete ladder for USA/ENG/GER); ENG's replacement `Infantry template E` (10 heavy/3 art/1 light/1 AT) froze one battalion short of the 1006 target from May 1939 to March 1945, leaving a light-infantry battalion in every ENG line division for six years.
- **Rule:** Any change to which ai_template target is enabled (first flag set, flag value change, `WA_AI_TEMPLATES_block_all_templates`) is a decommission hazard for whatever template currently holds that role. Tuning targets against the fallback window alone is not enough - the first flag-set is a second deciding window, and it hits every country whose flag-gated target differs in shape from the fallback. The suppression ladder (`Light Cavalry template A..W`, +1 battalion per redesign toward the intended 25-cavalry 14001 target) shows the designer's per-step template churn even when converging correctly.
- **Evidence:** `SOV_1938_01_09_15.hoi4` (nationals alive, no `WA_INFANTRY_TEMPLATE` flags), `GER_1939_05_13_13.hoi4` (ENG/SOV flag=1006, ladders present, `Strelkovaya Diviziya` obsolete, ENG `Infantry Division` deleted), `GER_1941_09_09_20.hoi4` (USA national obsolete after its flag set), `USA_1945_03_24_01.hoi4` (ENG E still 10/3/1/1). Fix-active marker: SOV `division_templates` appear in the post-fix OOB order (Strelkovaya before NKVD), proving the run included commit `4f67ea1c0`.

### The AI template designer deadlocks on regimental-support column rules - targets must be reachable without restacking columns

- **Date:** 2026-08-09
- **Symptom:** Late-game (1944-45) AI infantry templates of every `WA_INFANTRY_TEMPLATE = 1006` country (ENG/SOV/USA) sat permanently one or two edits short of the `HEAVY_INFANTRY_30_MIX_MOT` target - leftover `infantry_light_horse_battalion_line` where the AT battalions should be, or 5/6 regimental support - frozen for up to six in-game years (ENG's `Infantry template E` unchanged May 1939 to Mar 1945). 1004 countries (JAP/ITA) fully converged on the same regiments; ROM converged regiments but froze at 4/6 regimental support. Manually opening the stuck template in the designer shows the same wall: the remaining regimental-support "+" offers an empty selection until you restack the line battalions into different columns by hand.
- **Cause:** The 1.18 regimental-support rules make some targets unreachable from some column layouts, and the engine's designer converges greedily one edit at a time without ever restructuring columns. Rules: `NDefines.NMilitary.REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS = { 3, 3, 3 }` (each RS row needs >= 3 battalions in that column), combat-support-type columns (art/AT) accept no RS at all, and one company per support type per regiment - with only pack-artillery and AT company types, an eligible column caps at 2 RS, so a 3+3 RS target needs exactly three infantry columns of >= 3 battalions. JAP/ITA landed on the one workable layout (inf 4/3/3 + all art/AT stacked in one 5-high column). ENG/SOV/USA froze RS under columns before the battalion grid settled (their 1006 targets demand ~15 extra horse->mot support/RS conversions, so RS finalizes early); after that, converting the leftover light-inf battalion to AT would drop its column below the 3-battalion RS threshold and orphan the RS companies above it, so the engine rejects the edit forever. Same trap in the mechanized family (USA APC template: AT/art columns ineligible, two mech columns capped at 2 RS each, designer won't restack 9 mech into 3x3).
- **Rule:** When authoring `target_template` blocks, verify the target is reachable by single greedy edits from any plausible intermediate: RS count must be `<= 2 x (number of infantry-type columns of >= 3 battalions the battalion mix can form)`, and never rely on the designer to move a battalion out of an RS-carrying column. Diagnose by dumping the save template's x/y grid per column, not the flat battalion counts - the counts looked "one battalion short" while the real blocker was column geometry. Levers if this bites again: fewer RS in targets (2+2), battalion mixes that force the good stacking, or lowering `REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS` (player-facing balance change).
- **Evidence:** `USA_1945_03_24_01.hoi4` grids - ENG E: inf 5/3/(2H+1L) + art col 3art+1AT, RS 5/6; USA E: five columns 3/3/(2H+1L)/2/(3art+1AT), RS 5/6; SOV G: RS 6/6 done but 2 light inf stuck in the third RS-carrying column, 0 AT; JAP F / ITA C: inf 4/3/3 + 5-high art/AT column, fully converged. In-GUI reproduction: restacking to 3x3 columns by hand immediately re-enables the empty RS "+" (user-verified).

### Token-substituted unit names break when the naming scheme is asymmetric across the token's values

- **Date:** 2026-08-09
- **Symptom:** Division-creator spawn templates 1, 7, 8, and 10 (`WA_AI_DIVISION_setup` in `common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt`) referenced `engineers_[SUPPORT_MOT]_company_divisional` in their support blocks. After meta_effect substitution this resolved to `engineers_mot_company_divisional` or `engineers_horse_company_divisional` — neither is a defined sub-unit, so those templates were created without an engineer company (the engine drops unknown support entries silently).
- **Cause:** The `[SUPPORT_MOT]` mot/horse token assumes every support type follows the pattern `<type>_<mot|horse>_company_divisional`. Engineers don't: `common/units/support_engineer.txt` defines `engineer_horse_company_divisional` (singular "engineer", a *company*) but `engineer_mot_battalion_divisional` (a *battalion*, no mot company exists). No single infix substitution can produce both names.
- **Rule:** A meta_effect token that splices into the middle of a unit name only works if every value of the token yields a defined unit under the same surrounding pattern. When the naming scheme is asymmetric (company vs battalion, singular vs plural), give the whole unit name its own `defined_text` that returns the full name per branch — here `WA_AI_DIVISION_GetSpawnDivisionTemplateSupportEngineer` in `common/scripted_localisation/WA_AI_DIVISION_CREATOR_scripted_loc.txt`. Validate by expanding every token combination and grepping each resulting name in `common/units/`.
- **Evidence:** Fix of 2026-08-09; prior partial fixes in commits a9c0407ee "fix engineer names" and 0e3976eca (templates 2-11 hardcoded `engineer_mot_battalion_divisional` correctly, but the four `[SUPPORT_MOT]`-based blocks were missed). All 47 expanded unit names in the 11 spawn templates now verified to exist in `common/units/`. **2026-08-09 follow-up: the full-name defined_text recommended here failed in-game for a second reason — see the next entry.**

### defined_text output is localised - returning a full unit name returns its display name instead

- **Date:** 2026-08-09
- **Symptom:** Observer campaign 5709c8b9 (first run carrying commit d4b0c6965): every spawn template of types 1/7/8/10, across GER/RCZ/JAP/ENG/USA/AST and both motorization branches, still missing its engineer support slot despite the `SUPPORT_ENGINEER` defined_text fix being verifiably loaded. Armour templates' SPG/SPAA support companies and SPG/TD/heavy-AT line battalions equally absent, silently, for as long as those defined_texts have existed.
- **Cause:** `defined_text` resolves its `localization_key` through the localisation database — if the returned string is a loc key, the *localised display text* comes back instead of the raw string. Every full unit name is a loc key (`localisation/replace/afo_unit_l_english.yml`), so `WA_AI_DIVISION_GetSpawnDivisionTemplateSupportEngineer` returned `Engineers Company` / `Assault Engineers Battalion`, the meta_effect spliced that into the template, and the engine dropped the invalid token — identical symptom to the original bug, new mechanism. Literal names typed directly in meta_effect text are NOT localised (template 2's hardcoded `engineer_mot_battalion_divisional` always worked), which made the fix look correct in review.
- **Rule:** A defined_text used to build script identifiers must never return a string that is also a localisation key. Return a fragment that cannot be one — trailing underscore (`medium_armor_`), embedded `" = { x = 1 y = 4 }"` suffix, or a partial name — and splice the literal remainder in the meta_effect. Before shipping, grep `localisation/` for `^<returned-string>:` on every branch to prove none is a key. Savegame templates are the only reliable verification: the transient meta_effect text is never stored.
- **Evidence:** Campaign 5709c8b9 saves 1941.6/1943.6/1944.6 (streamed template extraction: all affected templates lack the `x = 0 y = 0` slot while every pattern-spliced support company is present). Fix of 2026-08-09: all six full-name defined_texts in `WA_AI_DIVISION_CREATOR_scripted_loc.txt` now return non-key fragments, splice sites updated in `WA_AI_DIVISION_CREATOR_effects.txt`; template 9's duplicated x=4 armour column (invisible while its tokens resolved to nothing) restacked to x=3/x=4.

### put_unit_buffers: fronts in the area eat the buffer by default — but "same `order_id` = one shared ratio pool" was inferred, and measurement refutes it

- **Date:** 2026-08-09; **pooling half falsified and corrected 2026-08-17** by direct savegame measurement (campaign `7c7803a8`). Original title: "put_unit_buffers: same order_id means one shared ratio pool, and fronts in the area eat the buffer by default". Corrected in place rather than deleted because it was being cited: on 2026-08-17 a reviewer blocked a change to `WA_AI_MILITARY_ENG_defense_of_el_alamein` (`common/ai_strategy/WA_AI_MILITARY_COUNTRY_ENG_THEATRE.txt:762`) on the reasoning that its `ratio = 0.5` "was sized while diluted inside pool 1, so moving it to a private pool changes what the number means" — that reasoning rests entirely on the refuted half and is void.
- **Symptom:** Observer campaign 5709c8b9: AI Germany's Atlantic Wall garrison eroded from 31 divisions (Jun 1941) to 3 (Jun 1944) even with the wall `put_unit_buffers` blocks active and forts built — the eastern front absorbed everything and D-Day landed against ~7 defenders (3 GER + 4 RCZ).
- **Cause (as diagnosed 2026-08-09 — part (1) is now WITHDRAWN):** Two stacked engine defaults. (1) ~~All six `atlantik_wall` buffer blocks in `WA_AI_MILITARY_COUNTRY_GER_THEATRE.txt` shared `order_id = 1` with each other *and* with the Balkans/Italy garrison buffers — per `documentation.info`, same order_ids share a single ratio pool, so "0.25" was one pool diluted from Norway to the Balkans, not 0.25 per sector.~~ **This half was read off the `documentation.info` comment (`:202`, "ratio of same orders ids will be share same ratio") and never measured. Measurement refutes it — see "Measured" below. The block-sharing explanation of the erosion is withdrawn; what actually thinned the wall is (2) plus whatever the unmeasured country-wide arbitration does.** (2) `subtract_fronts_from_need` defaults to *yes*: front orders in the buffer's `area` subtract from its need, so the moment real fronts existed in France the buffer demand collapsed. The `festung_*` blocks (order_id 2-6, `subtract_fronts_from_need = no`) already encoded the correct pattern.
- **Measured 2026-08-17 — ESTABLISHED:** (a) **`order_id` is not serialized at all.** Every `type=5` `order_instance`, every country, all three saves, carries exactly seven scalar keys — `type`, `instance_id`, `creation_date`, `starting_date`, `area_defense_settings`, `route_is_ok`, `manage_child_sections` — plus `states={}`, N x `scheduled_member={}` and `area_defense_state_assignment={}`. No `order_id`, no ratio field, no needed-units field (`can_execute` exists, but only on type=1/type=2). (b) **Same `order_id` produces SEPARATE orders.** `WA_AI_MILITARY_USA_buffer_pacific` declares several blocks all with `order_id = 9101` *and* the same `area = central_pacific`; at 1943.11 they are five separate order instances in five separate armies (states 629 / 630 / 631 / 638 / 632). On ENG, instances 1761 (`order_id=1`, Britain, 9 states) and 1750 (`order_id=1`, Alexandria state 447) are live in the same save, in different armies, with disjoint state sets. Across ENG+GER+USA x 3 saves, **zero** `orders_group` holds two type=5 orders. (c) **The relation runs the other way — one block can SPLIT into N orders.** USA `unit_buffer_for_europe_*` (`order_id=1`, `area=britain`, states `{123,125,127,130,857,859,860}`) becomes three instances (`{125,857,860}` 11 div, `{123,859}` 12 div, `{127,130}` 12 div — union exact, 35 divisions); GER `atlantik_wall_north_france_THEATRE` (`order_id=11`, states `{14,15,23,29,30}`) becomes two. Block→instance is 1→N, never N→1.
- **Still UNKNOWN — do not fill these in by inference:** (i) **what `order_id` actually does.** `documentation.info section put_unit_buffers` describes `ratio`, `area` and `order_id`, but the save contradicts the pooling reading and the field is not persisted, so its real effect is unestablished. (ii) **how the engine arbitrates when the summed `ratio` demand across a country's blocks exceeds 1.0.** The measured *outcome* at 1943.11 is ENG 55 of 110 deployed divisions (50%) in area-defence orders, GER 42 of 275 (15%), USA 63 of 87 (72%) — an outcome, not a demonstration of the arbitration rule. Do not derive a sizing formula from those three numbers.
- **Rule:** Set `subtract_fronts_from_need = no` explicitly on any `put_unit_buffers` garrison that must hold against competing front demand — the default *yes* is what collapsed the Atlantic Wall, and that half is unaffected by the correction. Do **not** reason about a block's `ratio` as "diluted by the other blocks sharing its `order_id`": each block becomes its own order (1→N), so changing a block's `order_id` is not by itself a resizing of its `ratio`, and a `ratio` sized under the pooling reading was never in fact sharing anything. Per-sector sizing (the 2026-08-09 rebalance: north_france 0.12, benelux 0.06, others 0.05-0.06) remains the right shape — but justify it by what the sector needs, not by pool arithmetic that does not exist. Generally: the `documentation.info` comments are the engine authors' prose, not a spec — this one has now been wrong once, so any claim about `order_id` semantics needs a save measurement (`countries/<TAG>/theatres/theatre/{orders_group|field_marshal_group}/order_instance`) before it is allowed to block a change.
- **Still open, and NOT settled by this measurement:** whether an `area`-less `put_unit_buffers` is defective. 62 of 154 buffer blocks repo-wide carry no `area` — including the GER `festung_*` family this entry itself cites as the correct reference pattern — and `documentation.info section put_unit_buffers` never states what the absence defaults to. Cross-links: the Fix 99 rule "a state-keyed `put_unit_buffers` … with its own `order_id` and an `area` alias limited to that theatre's region (Fix 97 pattern)" is prescriptive design guidance, not a measured claim about area-less blocks; leave both standing until someone measures it.
- **Evidence:** Original half — campaign 5709c8b9 division placement per save (31→10→4→3 in the wall states 1941-1944); `common/ai_strategy/documentation.info` lines 194-226; festung blocks in the same file as the working counter-example. Correction — campaign `game_unique_id = 7c7803a8-21f7-47df-99da-f82d3e3bd6c3` (`world-ablaze-beta`, HOI4 1.19.2, observer `player=BHU`), saves `1941.6_Jun.hoi4` / `1943.11_Nov.hoi4` / `1944.6_Jun.hoi4`; `documentation.info section put_unit_buffers` is the comment the withdrawn half was inferred from. The buffer-block census (154 total / 62 without `area`) was counted over `common/ai_strategy/` on 2026-08-17.

### Test campaigns run on a dedicated cloud machine - local HOI4 logs prove nothing about a verification run

- **Date:** 2026-08-09 (corrected same day - the first version of this entry drew the wrong conclusion)
- **Symptom:** Observer campaign 0e7e7852 reproduced the UK-airbase failure on what should have been the fixed build. The local `error.log` showed a HOI4 process launched at 14:58 (before the fixes existed) with a 15:48 mid-session reload failing on the new helper (`Unknown effect-type: WA_AI_PC_add_deployed_land_planes`), which led to a confident - and wrong - "stale process, campaign ran pre-fix code" verdict.
- **Cause:** The user's test campaigns run on a dedicated cloud machine; the saves are synced back into the local save-games directory. The local `error.log` belonged to the user's own local session (the fix-5 screenshot game) and had no connection to the campaign. In-save behavioural fingerprints settle what the campaign actually ran: the template fix and AIFC front-first behaviour were both active, and those commits are descendants of the airbase fix, so the cloud build contained all six fixes - the airbase and wall-buffer failures were real, not stale-code artefacts.
- **Rule:** Before diagnosing a verification campaign, establish *which machine ran it* - local logs, error.log timestamps, and launcher mod-copy hashes only describe the local box. The reliable build check is behavioural fingerprints inside the saves themselves (a value or structure only the new code can produce), plus git ancestry to pin which sibling commits must also be present. When a fix has no natural fingerprint, add save-visible instrumentation (persistent `*_dbg_*` variables at each decision stage) so the next run carries its own diagnosis. Two true sub-facts worth keeping: a console reload cannot register newly *added* scripted-effect names (the local 15:48 error proves it), and `error.log`'s first-line timestamp is the launch time of the local process only.
- **Evidence:** Campaign 0e7e7852 (template slots present + front-first sectors = fixed build; zero type-2 projects = real airbase failure); user correction 2026-08-09; instrumentation added to `WA_AI_build_uk_air_hosting_capacity` (`WA_AI_uk_air_dbg_called/planes/capacity/best/started`) and the helper inlined to eliminate the new-name registration failure class entirely.

### An absent script variable reads as 0 - guard brake conditions with has_variable

- **Date:** 2026-08-09
- **Symptom:** Any country whose `WA_AI_fielded_eq_ratio` had not yet been computed (the variable is written by a `mean_time_to_happen = 2 days` background event, throttled to 7-day windows in performance mode) satisfied every `check_variable = { WA_AI_fielded_eq_ratio < 0.9 }` test, because an absent variable evaluates as 0. Combined with `WA_AI_MILITARY_home_threatened`, that froze all fronts at priority 10000 (`WA_AI_MILITARY_EXEC_no_stockpiles_stop`), dropped AIFC into linear defence (`WA_AI_AIFC_posture_defensive`), and latched the posture hard brake - worst for freshly spawned tags (civil wars, releases) that can be at war with home threatened from their first day.
- **Cause:** PDXScript `check_variable` treats a missing variable as 0, so every `< threshold` comparison used as a *brake* condition fires spuriously until the producer event runs. The producer being an MTTH background event means the uninitialized window is unbounded in principle.
- **Rule:** Any `check_variable = { X < threshold }` whose truth triggers a brake, veto, or suppression must be wrapped with `has_variable = X` - absent must read as "unknown", never as "critically low". `> threshold` checks gating *bonuses* are safe to leave unguarded (absent just withholds the bonus). Codified as rule §2.7 of `documentation/WA_AI_MILITARY_ECONOMY.md`.
- **Evidence:** Fix of 2026-08-09 in `WA_AI_AIFC_triggers.txt` (posture_defensive), `WA_AI_MILITARY_DEFAULT_FRONT_control.txt` (no_stockpiles_stop), `WA_AI_MILITARY_posture_triggers.txt` (hard_brake, both branches); producer in `WA_AI_misc_effects.txt:256` called only from `events/WA_AI_misc.txt:43`.

## Working in this repo

### Match tabs exactly when editing

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Edits failing to apply, or applying with broken indentation.
- **Cause:** PDXScript here is tab-indented; string-matching edits that assume spaces do not match, and mixed indentation breaks the visual structure reviewers rely on.
- **Rule:** Copy the exact whitespace from the file when constructing an edit, include enough surrounding context to be unique, and never reformat blocks you are not changing — especially generated or parser-managed `ai_will_do` sections.
- **Evidence:** Repository-wide convention; `AGENTS.md` editing rule 12.

## 2026-08-09 - Deleting ai_strategy force_concentration blocks can CTD the game at database load

**Symptom:** deterministic EXCEPTION_ACCESS_VIOLATION ~15s into game boot (during country-history
load, before the menu), after commit d5fde822e removed legacy force_concentration_* blocks from
country ai_strategy files (Phase 7c "AIFC owns concentration").

**Diagnosis method:** automated bisect harness - launch `hoi4.exe --debug --start_tag=BHU`
headlessly, watch the crashes/ folder for a new dump vs in-game lines in game.log (crash = 15s,
survive = ~55s per cycle). ~20 launches: commit bisect -> file bisect (GER.txt alone reproduces)
-> hunk bisect -> surgical byte-level variants.

**Findings that defy a simple rule:**
- At d5fde822e, the minimal crashing pair was: GER_fall_gelb block deleted AND war_with_soviets'
  six entries stripped. EITHER one alone survived. At later HEAD (after 4917890f5/1a3eb868a),
  restoring only fall_gelb still crashed - BOTH restores were needed.
- Not syntax: every variant was brace-balanced and parsed fine in isolation.
- Not "zero force_concentration entries": a surgical file with all three front_factor entries
  removed (containers kept) survived.
- Not empty containers (GER_roles was always empty and fine), not the AIFC file (crash persists
  with it removed), not file size or parse-chunk offset (padding at top or bottom changes nothing).

**Conclusion:** the engine crash is sensitive to the combined shape of the strategy DB in a way we
could not reduce further. GER_fall_gelb and the war_with_soviets force_concentration entries are
restored in GER.txt with load-bearing comments. Treat any future deletion of force_concentration_*
blocks from country files as a change that REQUIRES a launch test, and keep the repro harness
(scratchpad hoi4_repro.py pattern: --start_tag launch + crashes-folder watch) - it turns a
"game crashes, no error logged" report into a ~1-minute-per-probe bisect.

## 2026-08-09 - The Spanish Civil War was decided by the WA_AI lend-lease drip, not by opening strength

**Symptom:** Republicans (D02) win the SCW in every campaign, even after ea7abaf7f front-loaded
the Nationalists (opening reinforcement, retargeted front_control, trimmed International
Brigades). Post-fix campaign c9ab1062: SPR was WINNING in Jan 1939 (19 states vs 7, more
divisions, more manpower) and still lost a 6-year war by 1942.9.

**Cause (layered, all verified against saves SWE_1937_11_18_05 / SWE_1939_01_02_22):**
- `WA_AI_lend_lease` (WA_AI_LEND_LEASE_triggers.txt) let democratic senders relieve any
  democratic target - D02 held `WA_AI_lend_lease_from_ENG/FRA/USA` flags all war and pulled
  6-24k rifles/week whenever it starved. The fascist-sender branch required the target to be
  `WA_AI_fascist_nation`, and Nationalist Spain rules as **neutrality** (fascism popularity never
  exceeds it), so GER/ITA never qualified: SPR had zero relief donors for six years.
- The volunteer defines (`VOLUNTEERS_PER_TARGET_PROVINCE = 0.005`) cap sponsors at ~1-2 token
  divisions; the sponsor commitment idea `SPA_spanish_civil_war_commitments` (GER/POR) had **no
  send_volunteer_size**, unlike its ITA twin (+3) and POR's own idea (+3) - the GER leg of the
  aid chain was tension-discounts only.
- lar_spain.2 gives every Republican "División de Infantería" two extra artillery slots via
  `add_units_to_division_template` (all six options) with no Nationalist equivalent, and
  `SPR_soviet_volunteer_airforce` hands the Republicans 300 free fighters with no volunteer gate
  and no Nationalist mirror.

**Rule:** when a war's outcome reverses months after the last balance change, audit the FLOWS
(lend-lease relief, timed-idea expiry, focus-tree exhaustion), not the opening state - a one-shot
opening buff cannot outweigh a permanent weekly supply channel. And when an ideology-gated WA_AI
rule must catch a country, check the country's RULING party against `WA_AI_*_nation` semantics:
popularity-plurality only reclassifies a neutrality government when the other ideology is
strictly largest.

**Evidence:** campaign c9ab1062 probes (D02 `WA_AI_lend_lease_from_ENG/FRA/USA` flags vs none on
SPR; SPR focus tree idle + single-line production by 1939.1); fix commit following ea7abaf7f
(WA_AI_LEND_LEASE_triggers.txt fascist/democratic branches, WA_SPA_civil_war_effects.txt
artillery parity, decisions/SPR.txt SPA_german_volunteer_airforce). A send_volunteer_size = 3
on SPA_spanish_civil_war_commitments was proposed for parity with the ITA/POR sponsor ideas but
deliberately not adopted - GER/POR sponsors stay at the define-capped 1-2 token volunteers.

## 2026-08-10 - .id of a scope is an engine-encoded reference, never a plain map-data id

**Symptom:** `WA_AI_AIFC_sector_age` pinned at 1 in every campaign since the AIFC system shipped,
across two fix attempts (4bfea363d, 128cc7995) that each patched a real but downstream defect.
The weekly sector loop demonstrably ran (anchor moved, arrays repopulated) yet validity read 0
every pulse.

**Cause (live-confirmed 1943.3 local run, decision-point telemetry):** the validity check tested
corridor membership with `is_in_array = { ROOT.WA_AI_AIFC_sector_states = THIS.id }`. The array
holds PLAIN ids from generated map data (`WA_AI_PC_get_state_id`), while `THIS.id` / a
scope-hopped `PREV.id` yields the engine-encoded scope reference - observed `anchor=228` vs
`scoped=-10737.41596`, DIFFERS on 108/108 samples across all majors. Equality can never hold.
The same mixed comparison sat in all four Layer-4 `state_trigger`s, where it made the boosts
dead and the NOT-suppressions uniform (a relative no-op - which is why nothing ever LOOKED
broken). Corollary: values like `10791.3` or `-10737.4` in saved variables are serialized scope
references, not runaway accumulators - decode before reporting an anomaly.

**Rule:** never compare `.id` of a scope against a plain stored id, in script triggers OR
ai_strategy state_triggers. Encoding-consistent comparisons are fine (`THIS.id` vs stored
`THIS.id`, pathfinding closed_list pattern). To test membership of the current state in a
plain-id array, invert: walk the array with `for_each_loop` + `var:` scoping and use native
triggers. If an engine-side state_trigger genuinely needs the comparison, publish a twin array
stored via ROOT-hopped `PREV.id` (Fix 31, 9778316f2) so both sides carry the same encoding.

**Evidence:** AIFC-DIAG telemetry protocol (session 2026-08-10); `WA_AI_MAP_effects.txt:202`
("THIS.id doesn't work for states"); `WA_AI_CONSTRUCTION_PRIORITY_strategies.txt` UK-air fix
comment (scope-encoded sentinel, campaign 9be92c89).

## 2026-08-10 - The shared `break` temp variable leaks across effects - even on success

**Symptom:** the supply-line strategy produced zero projects in every campaign (66d6b53c audit)
even in pulses where its gates were open and, once traversal was fixed, even when the A* found a
path.

**Cause:** `while_loop_effect`/`for_each_loop` default their break condition to the shared temp
variable `break`. Queue functions set plain `break = 1` after queueing and nothing resets it, so
any later default-break loop in the same pulse aborts before its first iteration. Worse, the
state-level A* itself set `break = 1` on BOTH exit paths - including success - so the caller's
own path-walk loop died immediately after a successful pathfind (Fix 30, 84528ae47).

**Rule:** in any reusable effect, give every loop an explicit break variable
(`break = _myeffect_break`) and reset `break = 0` at the effect head if callers may run after
other strategies in the same pulse. Sixth member of the temp-variable trap lineage (railway
Fixes 24/25/27, AIFC hop comments).

## 2026-08-10 - An if/else_if ladder with no matching branch is vacuously TRUE

**Symptom:** USA upgraded its conscription law via `WA_AI_upgrade_conscription_law` even though
`WA_AI_can_upgrade_manpower_law` has no branch for `USA_selective_service` - the trigger passed
by falling through the whole ladder.

**Cause:** in PDXScript trigger context, an `if = { limit = {...} ... }` whose limit fails
contributes true; a ladder keyed on "current law idea" where the country's law matches no branch
therefore allows everything. USA's law progression works only by this accident.

**Rule:** every if/else_if ladder keyed on an enumerable (law ideas, archetypes) needs either an
explicit branch per member or a terminal `else = { always = no }` - and adding that terminal else
to an existing ladder is a BEHAVIOUR CHANGE for every country on an unlisted member (here: it
would silently freeze USA's laws). Audit before "cleaning up".

**Evidence:** R10 re-analysis 2026-08-10 (campaign 66d6b53c: USA extensive at 1943.8 via the
vacuous path; `WA_AI_LAW_triggers.txt:15-22` ladder, `:1097` gate; the real ramp limiter was the
2% law + `conscription_ratio >= 0.99` wait at `:1111`).

## 2026-08-10 - "Dead" duplicated code may be the ONLY record of the design intent

**Symptom:** `events/WA_AI_invasions.txt` carried 68 pairs of
`set_temp_variable = { _divisions_per_province = N }` + `WA_AI_DIVISION_adjust_invasion_for_difficulty`
that were overwritten before any spawn. It read as a mass-nerf pass done by inserting overrides,
so Fix 32 "restored" the header value on Husky (`.47`/`.5`) - doubling those two landings from
12/8 to 24/16 divisions.

**Cause:** the header pair was duplicated boilerplate present with a MATCHING value at the
original authoring commit (`2aaec3200`) - redundant from day one, harmless. A later pass
(`608177207`, "spawned templates re org") split each landing into an infantry wave and a
`_division_template = 4` (#Armor) wave and edited only the pre-spawn assignment, deliberately
at half the value so the total stayed constant. The header kept the pre-refactor number. So the
value that looked like an accidental override *was the design*, and the value that looked
original was the stale one. Direction matters: vs `2aaec3200` the later passes were net BUFFS
(the `.51`-`.83` island family went 1 -> 4 divisions), not nerfs.

**Rule:** before deciding which of two competing values in duplicated code is authoritative,
reconstruct the value at the ORIGINAL authoring commit and diff forward commit by commit. If
both copies started equal, the one that was *edited* is the intent and the untouched one is
stale - the opposite of the usual "the later insertion is the hack" instinct. Cheap test: total
divisions before and after the suspicious commit. A total that is exactly preserved across a
structural change (1 wave of N -> 2 waves of N/2) is a deliberate size-preserving refactor, not
a bug. Also: a bare `adjust_invasion_for_difficulty` with no assignment in front of it multiplies
whatever is already there, so on hard it doubles an already-doubled value (`.41` Timor: 3 -> 6
-> 12 in one province).

**Evidence:** Fix 33 (this session). 81 events inventoried; 79 provably behaviour-neutral after
the purge, only `.47`/`.5` changed size (revert of Fix 32). Checklist probe R18.

---

## `on_startup` does not re-fire when a savegame is loaded

**Symptom:** a one-shot save migration (`WA_AI_invasions_migration_1`, purging the pre-Fix-32
permanent invasion penalties) was wired into `common/on_actions/WA_AI_startup_on_actions.txt` on
the stated assumption that `on_startup` runs both on a new game and on every save load. Loading
the target campaign and re-saving produced *nothing*: no `WA_AI_invasions_migration_1_done`
global flag, `wa_ai_invasions_dbg_active` still 2/2/1/6 on GER/USA/ENG/JAP, all seven stranded
relation modifiers still live.

**Cause:** `on_startup` fires on new game only (HOI4 1.19.2). Everything else in the chain was
correct, which is what made it look like a script bug: `World Ablaze BETA.mod` really does point
at the repo, `error.log` was free of script errors, and the process restart was properly ordered
(files 23:38, process 23:54:40, save 23:57:03). The first attempt had ALSO been invalid for a
duller reason - a process started nine minutes before the files existed - so the real cause was
only isolated on the second, clean run.

**Rule (two parts, and the second is the one that was got wrong twice):**

1. *There is no load-time hook.* `on_startup` covers new games only, so anything that must touch
an already-started campaign has to come from a recurring pulse (`on_daily` and friends in
`WA_AI_misc_on_actions.txt`) or from the console. Do not assume a "runs when the save opens"
on_action exists — it does not.

2. *A one-shot repair does not belong on a pulse either.* The reflex after finding (1) is to
move the migration to `on_daily` behind a global-flag guard. That was done, then reverted: it
makes every campaign forever pay a gameplay-tick hook, and an O(n²) `meta_trigger` sweep, so a
handful of legacy saves can be repaired once. **Migrations live in
`common/scripted_effects/WA_AI_MIGRATION_effects.txt` and are invoked by hand from the console
(`effect WA_AI_invasions_migration_1 = yes`).** A one-off maintenance action on one specific
save is console work, not mod behaviour. The distinction to apply: recurring *behaviour* earns a
hook; one-shot *maintenance* does not.

Consequences for how such an effect is written — a console tool is not an on_action effect:
- **No `has_global_flag` guard.** The guard only ever existed to stop a pulse re-running. A
  manual tool that silently does nothing on the second invocation is a trap. Make it idempotent
  instead (the second sweep finds nothing to remove), and *accumulate* its counter rather than
  assigning it, so re-running cannot erase the record of what the first run repaired.
- **Still set a flag, but as a record, not a gate** — it is the only thing that distinguishes
  "swept, save was already clean" from "never swept" when both leave the country variables
  identical.
- **`log = "... [?var] ..."`** so the operator sees the outcome in `logs/game.log` immediately,
  instead of saving the game and parsing a 120 MB file to find out whether anything happened.

**Diagnostic shortcut worth reusing:** put an *unconditional* `set_global_flag` at the end of an
effect body while debugging. If the flag is absent, the body never executed — that cleanly
separates "never invoked" from "invoked but silently no-oped". Without it, this would have been
read as a broken `meta_effect` and debugged in the wrong file entirely.

**Evidence:** campaign `2b607968`, 2026-08-10. Checklist R14 migration sub-probe records both
process caveats (stale process, and the absence of a load-time hook).

### Liberated territory goes to the poorest ally — and every PC selector refuses to build there

- **Date:** 2026-08-11
- **Symptom:** D-Day succeeds, then the European war stalls for two years (campaign `31eaf7e6`: GER
  undefeated at 1946.6). At 1944.7 the Normandy supply hubs sit at 18–31 demand vs **5 capacity**;
  Cherbourg and Le Havre are naval_base healthy-level **0**; nobody repairs or builds anything.
- **Cause:** Two stacked mechanisms. (1) Liberating an ally's owned states hands control to that
  ally — Normandy went to Free France (capital **Algiers**, 30 civ levels, `economy_fatigue_68`),
  so the supply net has no land path to a capital and hangs off level-1 ports: capacity
  5 = `NAVAL_BASE_FLOW 0.0 + NAVAL_FLOW_PER_LEVEL 5.0 × 1` (`common/defines/05_defines.lua:937-938`).
  (2) Every WA_AI PC *target selector* is ROOT/subject-gated in six places
  (`railway_strategies.txt:59-60/95/279-314/565-566/582/674/755/783`,
  `WA_AI_CONSTRUCTION_triggers.txt:127-133`, `railway_helpers.txt:1029/1105`), so ENG (217 civs)
  and USA (462 civs) structurally cannot raise the port, the rails, or the infrastructure of a
  Free-France-controlled beachhead — while FRA burns its only 15 factories on a GER-controlled
  Brittany rail and dead Paris queue entries (the Fix 34 bug class).
- **Rule:** Before assuming the builder will control the territory a system is meant to serve,
  walk the liberation case: owned-by-ally states revert to the ally. The *executor* already
  permits faction builds (`WA_AI_PC_start_project` accepts `is_in_faction_with`,
  `core.txt:906`; `supply_node`/`rail_way`/`naval_base` are `allied_build = yes`; pathfinder
  type 2 walks allied provinces) — only the selectors exclude allies. New coalition-serving
  construction should gate on `is_in_faction_with` like the UK-hosting and theatre-air-base
  strategies already do (`strategies.txt:960-967`, `:1205`). Note `_project_build_for_ally = 1`
  is set at `railway_core.txt:66` and read nowhere — designed, never implemented.
- **Evidence:** campaign `31eaf7e6` save `1944.7_Jul.hoi4`; checklist F5/R9 entries 2026-08-11.
- **RESOLVED 2026-08-14 by Fix 74** (checklist R46), after the same defect resurfaced in a second
  theatre: campaign `f9321934` at 1944.3 had the whole Maghreb FRA-controlled with rail 1-2 at the
  Tripoli front, ENG-held Egypt at rail 5, and **zero railway projects on ENG or USA for the entire
  campaign**. The selectors now go through `WA_AI_PC_can_build_logistics_here` /
  `WA_AI_PC_is_logistics_build_partner`, gated on the ally being unable to build for itself. The
  capitulated-ally half of the cause is deliberately still open - see R46's "Explicitly NOT fixed".

### The warbond ladder dead-ends when a series completes at fatigue 0

- **Date:** 2026-08-11
- **Symptom:** JAP frozen on `Series_B_bonds` from 1938.2 to campaign end (`31eaf7e6`);
  `economic_fatigue` ratchets 0→93; `economy_fatigue_93` applies `local_resources_factor -0.215`;
  the iron-deficit AI (`iron_shortage_ai`, `_economy_fatigue.txt:304`) then loops
  `disable_steel_mill` until **23 of 25 refineries are inactive** — steel 0 across 202 JAP
  factory lines at 1944.6 and the Japanese war economy is dead. USA, CHI and FRA are parked on
  Series C by the same trap; only GER and ENG reach G.
- **Cause:** `upgrade_warbonds` (`Economy_Fatigue_scripted_effects.txt:859-926`) gates every
  series swap on `check_variable = { economic_fatigue > 0 }` — evaluated on the terminal mission
  tick, immediately after `economy_fatigue_level_down_1` just spent ten ticks driving fatigue
  toward 0. A country that fully succeeds at its current series is thereby disqualified from the
  next one, and when the swap no-ops **`activate_mission = warbonds_mission` is never re-issued**:
  no retry, no re-evaluation, ai_will_do is 0 below fatigue 10 (`zzz_ministries.txt:378-381` etc.),
  so the state is a permanent dead-end. Aggravating data bug: JAP starts idea/variable desynced —
  `economy_fatigue_5` idea but `set_variable = { economic_fatigue = 0 }`
  (`history/countries/JAP - Japan.txt:155/171`; FIN and YUG have the same desync).
- **Rule:** A one-shot ladder step whose precondition the *previous* step actively destroys needs
  either the guard removed or a recurring re-evaluation path — never "check once at the terminal
  tick". When an idea has a paired tracking variable, the history files must initialise both to
  the same value; grep for the pair when auditing a country's start state.
- **Evidence:** save trace 1937.9→1944.7 (Series A 1937.9 → B 1937.11 → 10/10 at 1938.2 with
  fatigue 0 → stuck); cross-country table at 1944.7 (GER/ENG=G, USA/CHI/FRA=C, JAP=B);
  checklist R11/F6 entries 2026-08-11.

### Buildings placed in a landing's immediate predate the state-control flip

- **Date:** 2026-08-11
- **Symptom:** The scripted D-Day Mulberry harbours (level-5 naval bases at the beach provinces)
  were destroyed the moment they appeared: the Nero-decree port demolition hit them at landing.
- **Cause:** The harbour was built in the same `immediate` as `WA_AI_DIVISION_spawn_invasion`.
  Spawning sets province controllers, and the engine resolves the *state*-control flip
  afterwards — `on_state_control_changed` (where the Nero demolition lives) then fires and sees
  the brand-new building as part of the state being captured. Anything created at landing time
  exists *before* every on-flip effect runs.
- **Rule:** Never create or upgrade buildings in the landing event itself when an
  `on_state_control_changed` effect can damage them. Defer placement to a follow-up event gated
  on the state being ROOT/ally-controlled — the flip effects are synchronous with the flip, so
  once the state reads as yours they have already resolved (and Fix 36's `WA_port_demolished`
  once-per-state flag keeps later re-flips from re-demolishing). Use the retry-every-N-days +
  give-up-flag pattern already used by the invasion events.
- **Evidence:** `763488d04` (bug) → `e944259a3` (fix), `events/WA_AI_invasions.txt` events
  `.85`/`.86`; user-observed in-game 2026-08-11.


### A self-arming fix cannot re-arm state that is already dead

- **Date:** 2026-08-11
- **Symptom:** Fix 35 (`a03fc502b`) makes a dead-ended war-bond ladder re-arm itself: when
  `upgrade_warbonds` finds no swap possible it activates a 30-day retry watcher. It is correct,
  it was verified, and it does **nothing at all** for the campaign that motivated it — JAP is
  still parked on Series_B after resuming that save on the fixed build.
- **Cause:** the fix's arming site sits *inside the code path the bug prevents from running*.
  `upgrade_warbonds` is only reached from `check_and_fire_auto_warbond_event`, fired at
  `warbonds_mission`'s terminal timeout (or from an `afo_event.23` answer). A country that has
  already dead-ended has no mission left to time out, so it never calls the effect that would
  arm its own recovery. The fix cures countries that dead-end *after* it ships; those that
  dead-ended *before* it shipped are frozen forever on a build that contains the fix.
- **Rule:** when a fix takes the form "on failure, arm a retry", ask what re-enters the arming
  site — and specifically whether an *already-failed* instance ever does. If the answer is no,
  the fix is non-retroactive by construction and needs a companion one-shot migration
  (`common/scripted_effects/WA_AI_MIGRATION_effects.txt`, console-invoked). The general test,
  applicable to every fix in this repo: **enumerate the state the fix never reaches.** Script
  fixes are re-parsed at launch and apply to a live save, but only along code paths that still
  execute; latched, parked or already-consumed state is invisible to them. A fix that only
  changes what happens at a *transition* (a landing, a mission timeout, a capture) cannot repair
  a save that is already past that transition.
- **Corollary for detection:** the parked signature is usually expressible as a trigger, because
  the post-fix build makes it unreachable — here "holds Series_A..F, not issuing, no retry
  mission" is impossible on a healthy post-fix country, which is exactly what makes it a safe,
  idempotent migration filter. Look for that "impossible on the fixed build" predicate; it is
  both the detector and the idempotency guard.
- **Evidence:** `WA_AI_warbonds_migration_1` (this session), checklist R20 migration sub-probe.
  Same shape as the Fix 32 / `WA_AI_invasions_migration_1` case above — that one is now two
  instances of the pattern, not a one-off.


### `surrender_progress` is not a capability test — and a fixed idiom does not fix its copies

- **Date:** 2026-08-11
- **Symptom:** in campaign `911bed3c` the Soviet Union had **no AIFC force-concentration sector
  at all** from 1942.9 to the end of the campaign (3.7 game-years) while fighting for its life:
  every `wa_ai_aifc_sector_*` variable absent, armour steering gone with it, and the front
  reversed (Moscow fell 1944.1, Stalingrad 1944.5). The same defect appeared in the previous
  campaign as a single-snapshot blip and was written off as noise.
- **Cause:** `WA_AI_AIFC_should_select_sector` gates on `surrender_progress < 0.35`
  (`common/scripted_triggers/WA_AI_AIFC_triggers.txt:17,79-86`). `surrender_progress` is a pure
  **VP-loss** metric, so it measures how much territory you have lost, not whether you can still
  fight. A big country being invaded crosses the threshold with a full army intact — and because
  WA raises the Soviet capitulation limit, it sits above the threshold *permanently* without
  capitulating. The weekly pulse then takes the "not eligible → clear" branch forever and the
  entire selection body is never re-entered.
- **The part that matters:** this exact bug had **already been diagnosed and fixed one day
  earlier, in the railway system** — `3c55b9d17` (Fix 29/29b), whose comment reads *"surrender_progress
  measures VP loss, not capability: SOV crossed 30% in Oct 1942 with ~180 states and 300+
  divisions and was locked out of railway building for the entire eastern war."* AIFC was
  authored the day before that fix and deliberately copied the then-current railway gate; its own
  comment says *"Mirrors the railway system's on_weekly eligibility gate"*. The copy inherited the
  bug, the fix landed only on the original, and nothing linked them.
- **Rule:** when you copy a gate, trigger or dispatcher from a sibling system, **record the
  source commit in a comment and check whether the source has since been fixed** — a comment
  saying "mirrors X" is a standing dependency, not a decoration. When you fix a shared-idiom bug,
  `grep` the codebase for the idiom (here: `surrender_progress`) before closing it out; a fix
  applied to one copy of a duplicated gate leaves the others silently broken. Duplication in this
  repo is normal and often correct (`@` constants are file-scoped, effects are copied between
  systems) — which is exactly why fixes do not propagate on their own.
- **Domain corollary:** treat `surrender_progress` as *unfit* for any "is this country capable"
  test. It answers "how close to capitulating", which for a country with a raised surrender limit
  is a state it can occupy indefinitely. Gate on capability (divisions, factories, controlled
  states, equipment ratio) instead. Note the same metric also drives
  `WA_AI_AIFC_posture_defensive` (`> 0.2`) and `posture_offensive` (`< 0.05`), so a losing major
  is forced into linear defence months before it loses its sector entirely.
- **Evidence:** checklist item R27 (retired 2026-08-14 at 5/5); `WA_AI_AIFC_core.txt:61-65,127-155`,
  `WA_AI_AIFC_helpers.txt:508-514`, the already-fixed sibling gate at
  `WA_AI_misc_on_actions.txt:149-163`. Puppet-scope was investigated as the lead hypothesis and
  **refuted** — RBL/RUK are at war with SOV, so puppet-held states are valid enemy corridors.

- **Scope correction (same day, after a full trace):** the entry above was written from the AIFC
  *sector* gate alone. That gate is real but it is **not** the load-bearing one, and the general
  lesson is bigger than "a copy missed a fix". `surrender_progress` is read as a fitness test in
  roughly a dozen places, and campaign `911bed3c` walked SOV through all of them in sequence:
  `> 0.05` (`WA_AI_MILITARY_triggers.txt:110`, `home_threatened`) latched a **priority-10000
  `front_control` with `execute_order = no`** from ~Sep 1941 — a total offensive veto that
  outranks every Country-layer block, all of which carry no `priority` field at all (= 0);
  `> 0.2` unconditional (`WA_AI_AIFC_triggers.txt:114`) published
  `force_concentration_factor = -100`, far below the engine's −15 hard-off point, killing AIFC
  outright from ~Dec 1941; `< 0.35` (`:84`) then wiped the sector in Sep 1942 — **nine months
  after AIFC had already stopped working**, which is why the dramatic-looking save signature
  (every `wa_ai_aifc_sector_*` variable vanishing) is a symptom marker and not the cause;
  `> 0.45` unconditional (`WA_AI_MILITARY_posture_triggers.txt:102`) re-latched the brake in
  1944. Alongside those, `< 0.1` locked SOV out of theatre air bases for the entire eastern war
  and `< 0.3` out of all three synthetic refineries and the PC stable-base floor.
- **The diagnostic lesson, which is the transferable one:** when several gates share a metric,
  the most *visible* failure is usually not the earliest one. The sector wipe was easy to see
  because it deletes variables from the save; the −100 concentration factor left no save-visible
  trace at all and preceded it by nine months. **Order the gates by when they first tripped, not
  by how loud their fingerprint is** — and get that ordering before proposing a fix, or you will
  fix the symptom and leave the country just as broken.
- **The precedent that makes this inexcusable:** `WA_AI_MILITARY_posture_triggers.txt:87-99` had
  *already* been refined so `surrender_progress > 0.2` alone cannot latch the hard brake, with a
  comment citing "1943-44 SOV sits above 0.2 for years with 350+ divisions".
  `WA_AI_AIFC_triggers.txt:114` is the identical pattern and never got the same treatment. Two
  independent misses of the same insight in the same subsystem family.
- **Rule:** treat `surrender_progress` as answering only "how close is this country to
  capitulating", never "can this country still fight". For a country whose capitulation limit is
  raised by script (SOV via `sov_the_politburo_max_surrender_limit_offset`), it is a state the
  country can occupy **indefinitely** — so every bare `surrender_progress` threshold is a
  potential permanent lockout, not a temporary emergency mode. Gate on capability instead
  (divisions, factories, controlled states, `wa_ai_fielded_eq_ratio`), or pair the metric with a
  capability term as the posture brake already does. Before adding one, `grep surrender_progress`
  across `common/` and check what the country you care about will look like at 0.4.
- **Corollary — recovery must be reachable.** SOV recovered materially in 1943 (`fielded_eq_ratio`
  0.995, brake released, posture 1) and *still* had AIFC off and no sector, because those two
  gates keyed on the one metric that never recovers. A brake whose release condition cannot be
  met by getting stronger is not a brake, it is a death spiral.
- **Resolution (2026-08-11, Fix 43):** the four permanent capability-blind predicates were reworked —
  the standalone `sp > 0.2` AIFC branch deleted, the `sp > 0.45` posture tier paired with
  `WA_AI_MILITARY_army_still_operational`, the sector gate given the railway escape hatch, and the
  offensive bonus rekeyed onto `WA_AI_MILITARY_posture`. The posture system is now the single writer of
  "we are collapsing" and every brake releases on recovery. Details and the two-direction validation
  record are in checklist R27 (retired 2026-08-14 at 5/5; see this log and `documentation/WA_AI_MILITARY_SYSTEM.md` §9); the *self-releasing* sp gates (air bases, refineries, PC floor,
  `home_threatened` itself) were left alone and are still worth re-measuring.


### `num_of_available_civilian_factories` reads ~0 once the vanilla queue saturates

- **Date:** 2026-08-11
- **Symptom:** `WA_AI_C.10`, the recurring construction event that carries almost all of WA's
  factory-queueing logic, silently stopped firing for ENG in **January 1943** and never fired
  again for the remaining 3.3 game-years. Nothing in the save says so directly — the only visible
  trace is that counters downstream of it (`WA_AI_overext_dbg_mic_redirects_*`) never increment,
  and ENG built **zero** civilian factories and zero infrastructure in the British Isles across
  the entire campaign while its arms factories went 72 → 377.
- **Cause:** the on-action gate at `common/on_actions/WA_AI_misc_on_actions.txt:68-88` opens on
  the bare engine variable `num_of_available_civilian_factories > 1`. Once the vanilla AI
  saturates the construction queue, that variable reads ~0 — permanently, for any late-war major.
  The two other clauses (a construction-timer flag, a per-country date) were demonstrably
  satisfied: the timer flag is **absent** from the saves from 1944.6 on.
- **This was already known and already worked around — on a different path.** Fix 40's own
  comment says it outright (`common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies.txt:309-311`:
  *"the bare engine variable reads ~0 once the vanilla queue saturates"*) and shipped
  `WA_AI_PC_has_project_civs_16/_20` (`common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt:150-162`)
  as the floored replacement. The five bare gates *inside* the PC system were converted; the
  on-action gate that feeds the entire standard construction system was not. `WA_AI_C.100` is
  dead for the same reason.
- **Rule:** never gate a recurring AI pulse on a bare engine "available factories" reading. Use
  the floored `WA_AI_PC_has_project_civs_*` triggers, or any capability measure that does not
  collapse when the engine queue is full. More generally — **when you fix an idiom, fix every
  instance of it, including the ones outside the file you are editing.** This is the second
  instance of the same omission found in one campaign (see the `surrender_progress` entry above:
  the posture brake was refined, its AIFC twin was not; the railway surrender gate got an escape
  hatch, the AIFC sector gate did not). Two different metrics, three copies, same failure shape.
- **Diagnostic corollary — a silent on-action is nearly invisible.** An event that stops firing
  leaves no error, no flag and no variable; it is detectable only by the *absence* of increments
  in counters that live downstream of it. When a fix "does nothing" and its own instrumentation is
  absent rather than zero, check whether the event that owns the call site is still firing at all
  before touching the fix's logic. The arithmetic that proves it: ENG's C.10 branch would emit
  ≥8 `WA_AI_queue_MIC` calls per firing, so a single firing in 34 flagged months would have left
  a counter behind.
- **Corollary on brake placement.** Fix 39 brakes *queue insertion*, but ENG's military factories
  were bulk-ordered by `fire_only_once` events (C.60–C.64, 220 `queue_MIC` calls, all before
  1943.1) and drained through the engine queue for the next three years — growth decayed +46,
  +45, +17, +5. Even a correctly-wired insertion-time brake would have caught nothing. **Before
  writing a brake, check when the decisions it gates are actually made**; if they are made in
  bulk by one-shot events, the lever has to act on the committed pipeline
  (`WA_AI_priority_convert_MIC_to_CIC`), not on new insertions.
- **Evidence:** checklist R24 (`911bed3c`); confirmed independently by two separate audits, one
  from the ENG-economy side and one from the brake side. USA fingerprint that clinches it:
  `_mic_redirects_cic` 49 → 64 = exactly the 15 `WA_AI_queue_MIC` calls in the one-shot
  `WA_AI_C.78`, after which its counters froze forever.


### A multi-child `NOT = { A B C }` is a NOR, and it has now killed two systems

- **Date:** 2026-08-11
- **Symptom:** `WA_AI_can_take_limited_exports` never granted the law to a single AI country —
  **zero grants across 21 countries over the full 1936–1946 campaign `911bed3c`** — while the
  sibling branches of the same `else_if` chain fired normally (seven countries flipped between
  `free_trade` and `export_focus` mid-campaign). Every country observed holding `limited_exports`
  got it from `history/countries/` at game start or from a national-focus reward, never from
  `WA_AI_upgrade_trade_law`.
- **Cause:** three multi-child `NOT` blocks sitting as direct children of the trigger
  (`common/scripted_triggers/WA_AI_LAW_triggers.txt:1953-1967`). HOI4 evaluates
  `NOT = { A B C }` as **NOR** — true only when *none* of the children is true — not as
  `NOT (A AND B AND C)`. So `NOT = { is_major = no  is_in_faction = yes  has_war = yes }` means
  "major AND not in a faction AND **not at war**", while `NOT = { is_major = no  has_war = no }`
  nine lines below means "major AND **at war**". `has_war` is required to be true and false at
  once: the trigger is unsatisfiable for every country at every date, and nothing about tag,
  date or world state escapes it.
- **This is the second confirmed instance.** The first is `africa_war_2`
  (`common/ai_strategy/WA_AI_MILITARY_COUNTRY_ENG_FRONT.txt:399-410`), where an `OR` over states
  450/663/451 is followed by `NOT = { 450 663 451 550 910 271 }` — dead in every campaign, and
  the reason a shipped R13 fix could never fire. That case is also the one that **discriminates
  the two readings**: under the naive `NOT(A AND B)` reading it is perfectly satisfiable, and it
  was observed dead. So the NOR reading is settled by behaviour, not by documentation.
- **Rule:** write `NOT = { OR = { A B C } }` when you mean "none of these", and
  `NOT = { AND = { A B C } }` when you mean "not all of these". **Never leave a bare multi-child
  `NOT`** — it reads like the second and behaves like the first. When reviewing, treat every
  multi-child `NOT` as a defect until proven otherwise, and check specifically for two clauses
  that constrain the *same* variable in opposite directions: that is the signature of an UNSAT
  trigger, and it produces no error, no log line and no fingerprint — only a behaviour that
  silently never happens. The authors of this very file knew the idiom: where they wanted "not
  any of these" they wrote `NOT = { OR = { … } }` explicitly at `:1639`, `:1815-1818`,
  `:1916-1934`. The bare ones are the outliers.
- **Detection recipe that works:** a dead gate is invisible in isolation, but it shows up as a
  *branch that never produces an outcome while its siblings do*. `ideas <TAG>` across a campaign
  for every value the ladder can take, on ~20 countries, settles it in one pass — and always
  check whether the observed holders acquired the state through the code path under test or
  through `history/`, a focus, or an event, before crediting the path.
- **Evidence:** checklist R28 (trade-law ladder, this session) and R13's `africa_war_2` audit
  (2026-08-10).


### A resource controller that switches off consumers erases its own demand signal

- **Date:** 2026-08-11
- **Symptom:** ENG ran its aluminium industry down from 12 active refineries to 1 (12 levels left
  inactive) over 1944-46 while its own ratio-based shortage detector read **zero bauxite
  shortage**, and while the USA sat on 9 978 units of bauxite flagged for export and shipped 409.
  Nobody in the chain knew anything was wrong.
- **Cause — the general shape, which is the transferable part:** the `*_inactive` building twins
  carry no `local_resources_*` **and no `country_modifiers`**, so a deactivated refinery consumes
  nothing as well as producing nothing. Both legs of the need detector therefore move the *wrong
  way* when the controller acts: `resource@bauxite` rises toward zero as each refinery closes, and
  `resource_imported@bauxite` falls because the engine stops buying the ore. **The act of coping
  with the shortage deletes the evidence of the shortage.** Worse, the ratio detector
  (`WA_AI_check_resource_shortages`, deficit > 5% of need) divides by `resource_consumed@X`, which
  the shutdown also shrinks — so the denominator and numerator collapse together and the ratio
  reads healthy. Measured: 489 consumed, −14.2 balance, ratio 0.028 < 0.05 ⇒ shortage 0.
- **Rule:** whenever a controller responds to scarcity by *reducing demand* (switching off
  consumers, cancelling production lines, disbanding units), check what that does to the metric
  the rest of the AI uses to detect the same scarcity. If the metric is a net balance or a
  consumed-vs-available ratio, the controller is a negative feedback loop on its own alarm. The
  demand signal has to be computed from **intended** capacity (built levels, desired lines), not
  from realised consumption, or it goes silent exactly when the problem is worst.
- **Second rule — setpoint overlap.** The shutdown loop closed refineries until the balance
  reached ≥ −26; the restart decision required > −1. The band [−26, −1] is a trap the controller
  deliberately parks in: once anything switches off, nothing switches it back on without an
  external shock. Measured futility: 30 shutdown firings against 26 restart firings over two game
  years with the inactive count never falling. **When you write a hysteresis pair, verify the
  release condition is reachable from the state the trip condition leaves you in.** Same family as
  the `surrender_progress` death-spiral entry above.
- **Third rule — a player-only maintenance path is a landmine for AI countries.** The refinery
  counters (`total_X_mill`, `open_X_target`, `current_X_mills`) are refreshed only under
  `is_ai = no`, so for every AI country they are frozen at their `on_startup` values for the whole
  campaign — ENG read 31/31/31 at 1946.4 against 70 real steel refineries. Any code that later
  *acts* on those counters treats a 1936 snapshot as current. Here the GUI's Refresh button does
  exactly that: it runs `recalculate_*` and then `manage_*`, whose "close down to target" loop
  culled ~39 steel and ~13 aluminium refineries in one click on a 1944 AI save. **If a variable is
  maintained only for the player, either gate every consumer on `is_ai = no` too, or maintain it
  for everyone — never leave a stale value reachable by a live code path.**
- **Detection note:** none of this is visible in a savegame through any WA variable. There is no
  trigger, effect or telemetry metric anywhere in the mod that reads `*_refinery_inactive`; the
  only way to see it is to sum the inactive building levels out of the `states` block by hand.
  **Instrumentation is a prerequisite for this class of fix, not a follow-up to it** — a
  self-concealing failure cannot be verified by the same metric it conceals itself from.
- **Evidence:** checklist R29; campaign `911bed3c`; user in-game observation on the 1944.4 ENG
  save that started the investigation.


### The HOI4 trade AI buys to reach equilibrium, never to build a reserve

- **Date:** 2026-08-11
- **The fact:** the engine's trade AI imports only enough to bring `resource@X` to **~0** at the
  current instant. It does not anticipate demand, does not stockpile, and will never accumulate a
  surplus in order to make some future action affordable. A country sitting at `resource@bauxite`
  = +1 will **not** import its way to +50 so that it can switch a refinery back on.
- **Why this matters, and the mistake it caused:** faced with the R29 refinery deadlock (AI
  refineries switch off and never come back), the obvious-looking fix was to gate the
  reactivation decisions on *affordability* — "only restart a mill if I can already feed it",
  i.e. `resource@bauxite > 32 + margin`. That is correct control theory and **completely wrong
  for this engine**: the threshold is unreachable by construction, because nothing in the game
  ever pushes an AI's balance to +42. The fix would have frozen every AI refinery off
  permanently — strictly worse than the bug it replaced. Written, then reverted before it shipped.
- **The corollary that makes the existing design make sense:** the break-even gates
  (`resource@bauxite > -1`) in `reactivate_*_refineries_ai` are not sloppy — they are the only
  reachable bar in a world where the AI lives at zero. The intended flow is **speculative**:
  switch a mill on, let it open a deficit, and let the trade AI import to cover it. Consumption
  is what *creates* the import; the import never precedes the consumption. Any "check you can
  afford it first" gate inverts that causality and deadlocks.
- **Where the real defect lives, therefore:** in the *race*, not in the threshold. A restarted
  aluminium mill drops the balance by 32 instantly, while the trade AI needs time to respond;
  `bauxite_shortage_ai` activates at `< -26` on a 9-day timeout and closes a mill if the gap has
  not closed. Campaign `911bed3c` shows the signature — 26 reactivation firings against 30
  shutdown firings over two game-years with the inactive count never moving. It was flapping, not
  frozen. A fix has to give the trade response time to land (a grace period after enabling, or a
  cancel condition the trade AI can actually satisfy), not raise the bar to enter.
- **Rule:** before writing any AI gate of the form "only act when resource X is comfortably
  positive", remember the AI has no mechanism to *become* comfortably positive. Gate on a
  reachable state (at or near equilibrium, a deficit shrinking, a partner having stock to sell),
  and handle the transient the action itself creates by protecting it, not by preventing it.
- **Diagnostic corollary:** a mechanism that fires often but changes nothing is flapping, not
  dead. Two counters moving together (26 restarts / 30 shutdowns) with a flat outcome is the
  fingerprint — and it points at a race or a hysteresis gap, never at an unreachable gate. An
  unreachable gate produces one counter at zero, not two counters in lockstep.
- **Evidence:** user correction, 2026-08-11, on the R29 fix attempt; checklist R29 defect C.


### `resource@X` is the retained domestic surplus — the "AI lives at zero" rule is for importers only

- **Date:** 2026-08-16
- **The fact (owner's model of the trade system):** a country extracts X of a resource; the
  trade law reserves an export share E of it (that share is gone from the country's own books);
  own consumption comes off the rest. `resource@X` is what remains: **X − export share −
  consumption**. The engine trade AI reacts **only when that number is negative**, importing just
  enough to bring it back to ~0. A producer whose retained surplus is +50 is not an importer, is
  not pushed to 0, and stays at +50 — the previous entry's "the AI lives at zero" describes the
  *importer* branch of this arithmetic, not every country.
- **The mistake it caused (2026-08-16, coal prospecting):** the proposal was "prospect coal
  proactively while `resource@coal < 100`". The lessons reviewer — and the main agent, who
  accepted it — over-generalised the entry above into "the trade AI parks every non-exporter at
  ~0, so `< 100` is true for everyone and only excludes 100+ net exporters, i.e. *keep
  prospecting until you export 100+*". Wrong twice: (a) a domestic producer with 0 < surplus <
  100 sits exactly where the bar means it to; (b) the +100 is a *retained* surplus, measured
  after the export share has been taken — it is not "exporting 100". Prospecting is domestic
  extraction, so it raises precisely this number; the bar is reachable and self-limiting. The
  owner corrected the framing before it shipped; the trigger comment was rewritten.
- **The second fact, easy to miss:** coal, iron and bauxite are **WA-native resources**, not
  vanilla ones. The engine AI's handling of them is incomplete — that is *why* the mod carries
  scripted machinery around them (`coal_shortage_ai`, the `WA_AI_needs_<r>` counters, the
  prospecting layers). Do not assume the vanilla-resource trade behaviour (import-to-zero,
  partner search) transfers to them; read the save ledger. GER on `af003548` holds an
  `imported = 0` coal column next to a −3 200…−3 700 unmet-demand column for eight consecutive
  months while sitting on +15 000 net — a vanilla resource would not show that shape.
- **Rule:** before scoring any `resource@X` threshold, say which branch the country is in —
  *importer* (parked at ~0 by the engine, thresholds above 0 unreachable *by trade*) or
  *producer* (retained surplus is real, reachable *by extraction/prospecting*, and thresholds
  above 0 are meaningful). "The AI lives at zero" applies to the first branch only. And for
  WA-native resources, verify the engine even imports (ledger `imported` column) before
  reasoning from vanilla trade behaviour at all.
- **Evidence:** user correction 2026-08-16 on the coal-prospecting change; `savegame.py
  resources GER 1943.7_Jul.hoi4 … 1944.1_Jan.hoi4` on campaign `af003548`.


### The export share scales with extraction — a positive `resource@X` does NOT mean prospecting is useless

- **Date:** 2026-08-17
- **The missing third branch.** The entry above splits countries into *importer* (parked at ~0)
  and *producer* (real retained surplus). Both branches describe what `resource@X` means for the
  country's **own** consumption. Neither says what it means for **an ally**, and that is where the
  next mistake happened. The offered export share is `min_export × EXTRACTION` — `0.8` free trade,
  `0.5` export focus, `0.25` limited exports, `0` closed economy (`common/ideas/_trade.txt`),
  shifted by national ideas (GER `+0.1`, SOV `+0.25`, TUR `+0.2`, BUL `−0.15`, generic `−0.3`).
  Because that share is a **fraction of output**, raising extraction raises *both* the retained
  balance *and* the tonnage offered to the market. Measured: GER coal `to_export / produced` =
  0.281 at 1943.6 and 0.298 at 1945.6 — a constant fraction, exactly as the formula predicts.
- **The mistake it caused (2026-08-17, Fix 101).** The trigger header asserted "a positive
  `resource@<r>` is a real retained surplus and EXTRACTION IS NOT THE BINDING CONSTRAINT" and
  applied it to eight resources. That inference is invalid: if a producer's offered share is being
  bought out, extraction *is* the binding constraint on what allies receive, positive balance or
  not, and a gate that blocks prospecting on the balance sign is backwards. The owner caught it by
  asking the question the header should have answered — "can't a country be in positive balance
  with 100 % of its exports consumed?"
- **Why the reviewer did not catch it either.** `wa-lessons-reviewer` checks against *recorded*
  knowledge, and this branch was not recorded — the entry above stops at the own-consumption
  reading. It did endorse the phrasing, but **conditioned on measuring `to_export` vs `exported`**;
  the condition was dropped and the sentence kept. A conditional endorsement carried past its
  condition is the same failure as a copied idiom carried past its data (entry below).
- **The first measurement looked like a rescue, and it was a sampling artefact.** Checking only the
  eight harm pairs showed none of them sold out (ITA bauxite 73–79 %, HUN 41 %, USA 16–25 %, SAF
  7–9 %, five offering `to_export = 0` outright), so the entry originally read "correct outcome,
  invalid reasoning". **That conclusion was wrong.** Sweeping all 2706 country/resource/date rows
  instead of the eight cases the fix was built from found **184 rows whose offered share IS bought
  out, 160 of them (87 %) on a POSITIVE balance** — CAN sells all 1126.7 aluminium it offers on
  +148, ENG all 216 iron on +201, USA all 177.2 tungsten on +1. Scored against "fire if short OR
  sold out", the balance-sign gate makes **166 errors, every one of them a refusal to prospect
  where extraction would have delivered**. The outcome was not correct either. Fix 102 replaced it.
- **The methodological lesson, which is the durable one.** The first sweep only measured the rows
  the fix was designed from, so it could confirm the fix and could not falsify it. A gate is scored
  on the population it will *run* on, not on the cases that motivated it — and the discriminating
  rows are the ones nobody thought to look at. The same sweep also caught a bad criterion: counting
  `unsold < quantum` as "sold out" silently included offers *below* one quantum that nobody can
  buy, which is the opposite state; 415 of the first 459 flags were that artefact.
- **Rule:** before claiming extraction is not the binding constraint for a country, read
  **`exported / to_export`** for that country and that resource (`savegame.py resources <TAG>
  <save>` prints both). Near 100 % means extraction *is* binding. `to_export = 0` means the country
  cannot supply an ally at all, whatever its balance. Never infer either from `resource@X` alone,
  and never from the ally's `imported` column, which moves for reasons unrelated to ROOT. When you
  test "is the offer sold out", require `to_export >= quantum` first, or a sub-quantum offer passes
  trivially.
- **Built, and what it cost.** Fix 102 implements exactly the gate this entry called sharper:
  `WA_AI_coop_can_supply_<r>`, computed per country in `WA_AI_check_resource_needs`. Since no token
  exposes `to_export` or `transfer_overlord_subject`, the offered share is estimated as
  `min_export × resource_produced@<r>`, which carries three biases named at the compute site —
  subject transfers in are ignored, `min_export` is shifted by traits/ideas/modifiers by up to ±0.3
  with only the base law value readable, and an output siphoned to an overlord offers nothing. Cost
  of all three: 9 false fires against 166 false blocks removed.
- **Evidence:** user correction 2026-08-17 during Fix 101, then the full sweep during Fix 102;
  `savegame.py resources` over 2706 rows at 1939.9 / 1941.6 / 1943.6 / 1946.4 on campaign
  `7c7803a8`; `common/ideas/_trade.txt` `min_export`; `common/resources/00_resources.txt` `cic`.


### A correct idiom can become wrong when copied, if its correctness rests on the data

- **Date:** 2026-08-11
- **Symptom:** `manage_alu_mills` mis-counted how much bauxite and coal each refinery closure
  frees — over-crediting 3 bauxite per plain closure and 5 coal per hydro closure — so its loop
  exited early and closed fewer mills than the deficit required.
- **Cause, and the interesting part:** the code is a faithful copy of `manage_steel_mills`, which
  is **correct**. That routine uses a neat idiom: pre-charge the cost of the variant its *first*
  branch handles, then patch the difference inside whichever branch actually fires
  (`-15 coal` when it closes a hydro instead of a plain mill). The idiom works for steel because
  `hydro_steel_refinery` differs from `steel_refinery` on **exactly one axis, by exactly 15**.
  Aluminium's hydro variant differs on **two** axes — bauxite 32 → 35 *and* coal 20 → 0 — so a
  single one-axis patch cannot express it, whatever value you put in it. The copied code was not
  sloppy; it was structurally incapable of being right.
- **Rule:** before copying a numeric idiom between two systems, state out loud the property of
  the *data* that makes it correct in the source, then check that property holds in the target.
  "Pre-charge one variant and patch the delta" is only valid when the delta is one-dimensional.
  If the variants differ on more axes than the patch has terms, either give the patch a term per
  axis (what Fix 42 did: +3 bauxite *and* −20 coal in the hydro branch) or charge each branch its
  own full cost — verbosity beats a silently wrong invariant.
- **Caveat found while fixing it, which reverses the naive advice:** in this particular loop the
  pre-charge is not a stylistic choice, it is the **termination guarantee**. The enclosing `if`
  checks that a refinery exists only once, before the loop; once the last mill has been closed no
  branch can fire, so if the temp variables were advanced only inside the branches they would stop
  moving while the loop condition stayed true — an infinite loop. Advancing them unconditionally
  at the top means every iteration makes progress whether or not anything was closed. **Before
  "simplifying" an unconditional counter update out of a `while_loop_effect`, check whether it is
  the only thing that guarantees the loop ends.** That is now noted in the code itself.
- **Corollary on direction, worth knowing when triaging:** two arithmetic bugs in the same system
  can point opposite ways. The shortage missions in `_economy_fatigue.txt` **under**-credited
  (25 where the building frees 32), so their loop ran long and closed **too many** mills — that
  is what reduced ENG's aluminium industry to 1 active level of 16. `manage_alu_mills`
  **over**-credited, so it closed **too few**. Same system, same kind of error, opposite
  consequences; do not assume one diagnosis transfers to the sibling routine.
- **Where the duplication is now documented:** a header block above the refinery definitions in
  `common/buildings/00_buildings.txt` lists every site that copies a `country_resource_cost_*`
  value, plus a per-building reminder. PDXScript cannot read a building's modifiers back, so this
  duplication is unavoidable and the sync is manual — a mismatch throws no error, it just makes
  the controller close too many or too few.
- **Evidence:** Fix 42 (2026-08-11); checklist R29 defect C-bis.


### In a multi-tier resource economy, "nothing consumes X" is evidence of design, not absence

- **Date:** 2026-08-11
- **Symptom:** an architecture review concluded that WA's refinery shutdown mechanic "mitigates
  nothing" for iron and bauxite, and proposed retiring it. That would have destroyed the mod's
  resource balance.
- **The evidence, which was correct:** grepping `common/units/equipment/` for resource
  declarations gives steel 2630, tungsten 1702, chromium 1291, aluminium 1115, coal 1075,
  rubber 831 — and **iron 1, bauxite 1**, both from `trade_fix_equipment_0`
  (`ship_hull_heavy.txt:693-719`), a dummy at `build_cost_ic = 99999999` that exists only to make
  the resource visible to the trade AI. Since the engine's `PRODUCTION_RESOURCE_LACK_PENALTY`
  only bites on production lines whose equipment declares the missing resource, an iron or
  bauxite deficit carries **no direct engine penalty**. All true.
- **The inference, which was wrong:** "therefore a deficit is harmless, therefore the mechanic is
  flavour." WA runs a **two-tier economy** — iron + coal -> steel, bauxite + coal -> aluminium —
  and a raw tier is *by definition* never declared by end products. The grep result was the
  signature of the design, read as its absence. And because the engine has **no concept of a
  building that cannot run without its input**, the scripted on/off is the *only* thing making
  the raw tier bind at all: delete it and refineries produce steel and aluminium regardless of ore.
- **Rule:** when a resource, flag or variable appears to be consumed by nothing, ask **"what does
  it enable?"** before concluding it is inert. Trace one hop downstream. In a layered economy the
  most load-bearing inputs are precisely the ones with no direct consumers — that is what makes
  them inputs. The same trap applies to any intermediate: a variable read only by one trigger, a
  building that only feeds another building, a flag only another flag tests.
- **Corollary on engine gaps:** "the engine applies no penalty here" is not an argument that
  nothing should. It is often the *reason* a mod scripts something — the script exists to express
  a rule the engine cannot. Before proposing removal of a scripted enforcement, establish what
  the engine would do in its absence, not merely what it does alongside it.
- **Process note:** the wrong conclusion survived three parallel investigations and reached a
  written design document, because every agent was asked to verify the *evidence* and none was
  asked to challenge the *framing*. When a review concludes that a long-standing mechanic is
  pointless, that conclusion deserves an explicit adversarial pass before it is written down —
  the prior should be that it encodes something not yet understood.
- **Evidence:** `documentation/WA_REFINERY_CONTROLLER_REVIEW.md` §1 (and its withdrawn option
  O1); user correction, 2026-08-11.


### Read `common/defines/` before quoting any engine constant — this mod overrides them

- **Date:** 2026-08-11
- **Symptom:** an analysis wrote into the campaign checklist that a telemetry gauge's `×100`
  multiplier was wrong and should be 200, on the strength of remembered vanilla behaviour. The
  gauge was correct and the correction was the error.
- **Cause:** WA sets
  `NDefines.NBuildings.AIRBASE_CAPACITY_MULT = 100` (`common/defines/05_defines.lua:173`), half of
  vanilla's 200, and the strategy file's `@UK_AIR_CAPACITY_PER_LEVEL = 100`
  (`WA_AI_CONSTRUCTION_PRIORITY_strategies.txt:951`) is a deliberate mirror of it. Vanilla
  knowledge about *any* engine constant is a hypothesis here, not a fact.
- **Corrected 2026-08-18 - the mechanism named here was wrong, the rule was right.** This entry said
  `common/defines/` is a `replace_path` folder. It is **not**: `descriptor.mod` lists 110 paths and
  `common/defines` is not one of them. Both files load - the install's `00_defines.lua` (3230 keys)
  first, WA's `05_defines.lua` (849) rebinding individual keys on top - so `05_defines.lua` is a
  **diff, not a state**. Two consequences the replace_path reading gets backwards: a key WA does not
  name keeps **vanilla's** value (it is not unset), and a key WA writes under the **wrong**
  `NDefines.<category>` binds a brand-new Lua field nobody reads and is **silently dead**. That is
  how 18 WA assignments sat inert for years, one of them making `WA_AI_LOGISTICS_MODEL.md` quote
  `SUPPLY_FROM_DAMAGED_INFRA` as 0.01 when the live value was vanilla's 0.15. Grep **both** files.
- **Rule:** grep `common/defines/` for the constant before asserting an engine value, exactly as
  you already grep the install's `documentation/modifiers_documentation.md` before claiming a
  modifier is scoped wrong. Generalise: for anything the engine "just does" — define, modifier
  scope, default flag on a `put_unit_buffers` field — the mod's own replaced copy is the oracle,
  and remembered vanilla is only a prior. Same reflex, three different oracles. **Where the folder
  is an override layer rather than a replacement - `common/defines` is the one that matters - the
  oracle is the pair: the install's file for what a key defaults to, WA's for what it changed.**
- **Evidence:** `common/defines/05_defines.lua:173`; checklist anomaly entry "This mod sets
  `AIRBASE_CAPACITY_MULT = 100`, not vanilla's 200"; the doc note it corrects. For the 2026-08-18
  correction: `descriptor.mod` (no `common/defines` entry), install
  `common/defines/00_defines.lua` at `C:\Jeux\steamapps\common\Hearts of Iron IV` (1.19.2.0), and
  the `common/defines` section of `.claude/skills/wa-engine-reference/SKILL.md`.


### A probe caveat recorded on one member of a twin pair says nothing about the twin

- **Date:** 2026-08-11
- **Symptom:** `wa_ai_uk_air_dbg_started` was read as "projects built" and produced a 3.5×
  over-statement (ENG 115 + USA 61 = 176 "starts" against ~47 air-base levels of real capacity
  growth) — in a session where the checklist already carried an explicit over-count warning for
  the counter's sibling.
- **Cause:** the two counters are copies of one pattern in one file. `wa_ai_thair_dbg_started`
  (`WA_AI_CONSTRUCTION_PRIORITY_strategies.txt:1440-1451`) was given a queue-growth guard after
  the `2b607968` over-count was found; `wa_ai_uk_air_dbg_started` (`:1126-1127`) still increments
  unconditionally after `WA_AI_PC_start_project`, which declines silently on `queue_max`, on
  same-type dedup and on a duplicate province. The written caveat sat on the *fixed* one, which
  read as reassurance about the family rather than a warning about the other member.
- **Rule:** when a caveat, fix or guard is recorded against one of two sibling constructs, open
  the sibling's write site in the same pass and record the answer either way — "twin checked,
  same guard present" is a useful line. A guard is evidence about exactly the lines it is on.
  This is the same shape as the `# Fix NN:` lesson (later fixes revoke earlier ones) and the
  NOR/`surrender_progress` families: in this codebase, one instance of a pattern is never the
  whole population.
- **Evidence:** `WA_AI_CONSTRUCTION_PRIORITY_strategies.txt:1126-1127` vs `:1440-1451`;
  `documentation/WA_TLM_TELEMETRY_SYSTEM.md` §2.1 registry rows for both counters.


### Never conclude a code defect from a structural or grep scan — read the block

- **Date:** 2026-08-11
- **Symptom:** four arithmetic "mismatches" were reported in the refinery `manage_*` routines
  from the proximity of numeric literals to call sites. **Three of them did not exist.**
  `manage_steel_mills` is correct on all four paths, and one `−15` that looked like a wrong
  constant is a deliberate variant patch.
- **Cause:** the scan compared a building's `country_resource_cost_*` against the nearest literal
  in the controller and flagged every difference. It could not see the idiom the literals belong
  to — pre-charge the plain variant's cost at the top of the loop, then patch the delta inside
  whichever branch actually fired — under which a `−15` sitting next to a `20` is the *correct*
  expression of a variant that costs 5. Structural scans read tokens; correctness lives in the
  control flow between them.
- **Rule:** a grep, a diff-shaped audit or a "these two numbers differ" scan may only ever produce
  **candidates**. Before any of them is written down as a defect, read the enclosing block top to
  bottom and state the invariant it maintains. Report the candidates that survive and say
  explicitly which ones you checked and cleared — a cleared candidate is a finding too, and it is
  what stops the next session re-raising it.
- **Evidence:** `common/scripted_effects/WA_scripted_effects.txt` `manage_steel_mills` (correct)
  vs `manage_alu_mills` (the one real defect, Fix 42); checklist R29 duplication-hazard entry,
  corrected 2026-08-11 "after reading the code rather than scanning it".


### A controller that advances and retreats must move the same distance both ways

- **Date:** 2026-08-11
- **Symptom:** none observed yet — found by re-reading the refinery controller after Fixes 42-44
  landed. The aluminium bid arm opens a mill to create trade demand and closes it again if the
  market does not answer, and the two halves disagreed by 3 units.
- **Cause:** the two halves pick **different variants**. `reactivate_aluminium_refineries_ai`
  prefers `hydro_aluminium_refinery` (35 bauxite, no coal — the preference exists to protect coal,
  which is the resource WA cannot tolerate a deficit in); the retreat loop in `bauxite_shortage_ai`
  closes the plain `aluminium_refinery` first (32 bauxite). So every hydro round trip ended 3
  bauxite below where it started, and repetition walked the balance into `[-33, -32]` — below the
  reopen gate (`> -32`) and above the mission's arm (`< -33`), **a band where neither arm of the
  controller acts.** It also swapped active plain mills for hydro ones at zero change in output.
- **Rule:** in any open/close, advance/retreat, allocate/release pair, state the size of the step
  each half takes and check they are equal **for every variant either half can pick**. If the two
  halves choose their target independently, they will eventually choose differently, and the
  residue accumulates. The fix that works is to make the retreat follow the advance (record what
  was taken and give back the same thing); fixes that only move a threshold cannot work, because
  a fixed constant cannot absorb a difference that depends on which variant was chosen.
- **Corollary — where these bands hide:** a hysteresis pair is normally checked by asking "is the
  release condition reachable from the state the trip leaves you in?" That check passes here for
  the *plain* path and fails only for the hydro one. **Run the reachability check once per variant,
  not once per pair.**
- **Why iron was immune, which is how the asymmetry was spotted:** `hydro_steel_refinery` costs the
  same 25 iron as the plain variant, so its bid and retreat cancel whatever gets picked. Aluminium's
  hydro differs from plain on **two** axes (bauxite 32→35, coal 20→0). That is the same one-axis
  vs two-axis distinction that caused Fix 42 — third appearance in this one system. When a family
  has a "safe" member and a "broken" member, the safe one is usually safe by arithmetic accident,
  so it is evidence about its own numbers only.
- **Evidence:** Fix 45 (`common/decisions/_economy_fatigue.txt`, `WA_AI_bauxite_bid_hydro`);
  checklist R29 defect H; `documentation/WA_REFINERY_CONTROLLER_REVIEW.md` §5.2a. Witness
  configuration in campaign `911bed3c`: RIT at 1946.4 holds 2 hydro-inactive + 3 plain-active +
  10 plain-inactive aluminium levels.

### An idempotent writer also needs an idempotent analysis view

- **Date:** 2026-08-12
- **Symptom:** Replaying one equipment-generator plan was a clean no-op, but
  analysing the generated files changed 54 redesign verdicts and proposed 26
  new resource gates. Textual idempotence passed while end-to-end idempotence
  failed.
- **Cause:** The evaluator read its own generated module choices as original
  mod data. The redesign had repaired the deficient stat, so the next analysis
  saw a different transition and produced second-order decisions.
- **Rule:** When generated output is also analysis input, ownership markers
  must carry enough baseline information to reconstruct a logical pre-generation
  view. Test `analyse -> apply -> analyse -> empty plan`, not merely
  `apply the same plan twice`. Also normalize line endings in memory when
  matching source spans, then preserve the file's original BOM and newline
  convention on write.
- **Evidence:** `tools/equipment_evaluator/owned_source.py`,
  `generation/apply.py`, and `test_generation.py`.

### Never infer modular-equipment succession from ai_equipment file order

- **Date:** 2026-08-12
- **Symptom:** The equipment evaluator reported `M4A3E8 Sherman -> T20 -> T23` and proposed retaining the Sherman against both as if they were consecutive generations.
- **Cause:** `common/ai_equipment/USA_tank.txt` stores every design serving `land_medium_tank` in one ordered group, while `common/technologies/armor_usa.txt` branches from the M3 Lee into independent Sherman and T20 lines. A later Pershing convergence and reciprocal visual `path` edges can also create a false path back into the other branch if traversal crosses another design group.
- **Rule:** For modular equipment with explicit enable techs, derive succession from the technology graph, stop at the nearest design unlock on every branch, and treat any unlock owned by another ai_equipment group as a traversal barrier. File order is formatting, not topology.
- **Evidence:** `common/technologies/armor_usa.txt` (`usa_medium_tank_chassis_2`, `_3`, `_4`, `_5`, `usa_modern_tank_chassis_1`); `common/ai_equipment/USA_tank.txt` (`USA_medium_tanks`); `tools/equipment_evaluator/technology_graph.py`.

### A hard quality threshold must not remove the only production floor

- **Date:** 2026-08-12
- **Symptom:** The first competitive-frontier dry run rejected early British
  and Soviet tanks whose reliability was below the configured minimum, which
  could leave their shared production role with no selectable researched design.
- **Cause:** The offline quality threshold was treated as an unconditional
  runtime blacklist without asking whether a compliant successor was available.
- **Rule:** In a generated equipment selector, a below-threshold but resolvable
  design is an emergency fallback, not a rejection. Give it the lowest positive
  priority so it serves the role until a compliant model unlocks; withhold the
  whole frontier if a design cannot be resolved safely.
- **Evidence:** `tools/equipment_evaluator/ground.py` (`FrontierDecision`,
  `_evaluate_frontier`) and the ENG/SOV rows in
  `tools/equipment_evaluator/output/ground_equipment_report.md`.

### Validate redesign legality before scoring its stats

- **Date:** 2026-08-12
- **Symptom:** A tank redesign dry run improved reliability by proposing an
  empty required engine slot, and another proposal duplicated a module whose
  chassis cap permits only one copy.
- **Cause:** The ground redesign search scored candidate stats without applying
  the slot's `required` property or the airframe's effective
  `module_count_limit` declarations.
- **Rule:** A modular-equipment redesign candidate enters scoring only after
  required-slot, allowed-category, count-limit and runtime-resource-gate
  validation. Optional slots alone may become `empty`. Validate the generated
  raw `target_variant`, not only the analyser's logical pre-generation view.
- **Evidence:** `tools/equipment_evaluator/ground.py::_redesign`,
  `parse_equipment.py::count_limit_violations`, and
  `test_generation.py::test_frontier_redesigns_keep_required_slots_and_count_limits_legal`.

### Drop byte-identical generator patches before planning

- **Date:** 2026-08-12
- **Symptom:** A frontier migration applied every real edit correctly, but a
  second apply reported four unchanged GER priority blocks as pending after a
  neighbouring edit changed the file fingerprint.
- **Cause:** Reconciliation emitted before/after blocks that were byte-for-byte
  identical. The apply result counted them as operations although no textual
  state could distinguish pending from applied.
- **Rule:** Filter `original == replacement` before assigning operation IDs or
  source fingerprints. An idempotent apply protocol cannot represent a no-op as
  a state transition.
- **Evidence:** `tools/equipment_evaluator/generation/planner.py::build_plan`
  and `test_generation.py::test_planner_drops_byte_identical_reconciliation_patches`.

### Strategic-region ids are WA's own — vanilla and the wiki give wrong names

- **Date:** 2026-08-13
- **Symptom:** A naval diagnosis reported that `WA_AI_NAVAL_COUNTRY_ENG_protect_home`
  avoids region 18 (English Channel) and 368 (Bristol Channel). The reader could not
  find either region and challenged it. The id→name mapping turned out to be right —
  but only by luck of which lookup had been used — and re-reading the block to prove it
  exposed a *second*, worse error in the same claim: id 18 carries `value = -10000`,
  a negative avoid weight, which **attracts** the fleet rather than repelling it. Two
  independent ways to be wrong about one line.
- **Cause:** three separate identifiers exist per region and they do **not** always
  agree — the filename number in `map/strategicregions/`, the `id =` inside the block,
  and the `name = STRATEGICREGION_<n>` localisation key. Only the `id =` is what
  `naval_avoid_region`, `naval_convoy_raid_region`, a fleet's `strategic_region={}` in
  a savegame, and every other script reference mean. On top of that, **WA replaces the
  whole table**: 383 regions against vanilla's 304, 79 ids that do not exist in vanilla
  at all, and existing ids repurposed (vanilla 241 = Dasht-e Kavir, WA 241 = Irish Sea;
  vanilla 249 = Yunnan, WA 249 = Alboran Sea). 365 / 368 / 369 are WA-only — looking
  them up in vanilla or on the wiki returns nothing, which is exactly what happened.
  Two mod files also have a filename that contradicts their own id:
  `237-Azores Region.txt` carries `id = 112` and `name = STRATEGICREGION_237`, and
  `112-Far South Pacific.txt` carries `id = 237` — so id 112 displays as "Azores
  Region" in game and id 237 as "Far South Pacific". Four more (`380.txt`-`383.txt`)
  are unnamed.
- **Rule:** resolve a region id as **id → `name =` token → localisation**, reading the
  mod's `map/strategicregions/` only. Never infer a region from a filename, never from
  vanilla's table, never from the wiki. State the id *and* the resolved name whenever
  you report one, so a wrong resolution is visible instead of silent.
- **Second rule, from the same claim:** `naval_avoid_region` values are **signed**, and
  a negative value is an *attractor*. Never bulk-extract `id =` from these blocks
  without its `value =` — ENG id 18 (`-10000`) and USA id 42 (`-2000`, twice) invert
  under an id-only reading, and an audit that misses the sign concludes the opposite of
  what the script does.
- **Evidence:** `map/strategicregions/` (383 blocks) vs the game install's 304;
  `localisation/replace/english/strategic_region_names_l_english.yml`; checklist item
  R36's early-war baseline, whose first draft called ids 29/48/112 "central Atlantic"
  when they are Strait of Sicily, African Coast and Azores Region;
  `WA_AI_NAVAL_COUNTRY_ENG.txt:42-64` for the signed-value half.
- **Helper:** `.claude/skills/wa-savegame-analysis/scripts/regions.py <id>…` does the
  three-step resolution; `--grep <regex>` searches by name.

### `num_ships_with_type@` takes hull types, not the `screen_ship` category — and `convoy` is not a ship

- **Symptom:** `WA_TLM_nav_screens = num_ships_with_type@screen_ship` and
  `WA_TLM_nav_convoys = num_ships_with_type@convoy` returned **0 on every country, in
  every save, for the whole life of WA_TLM v4**. No parse error, no log line. Because
  `nav_port_pct` divides by `nav_screens`, the zero propagated: the derived metric took
  its `else = 0` branch, so the headline number *and* all 40 quarterly
  `nav_port_pct_hist` samples were a hard-coded constant. Checklist item R36's
  designated independent cross-check silently did not exist on that build.
- **Cause:** the engine's own reference
  (`<install>/documentation/dynamic_variables_documentation.md`) says the target "can be
  a sub unit def type or one of carrier, capital, screen, submarine". `screen_ship` is
  neither: it is the **sub-unit category** written as `type = { screen_ship }` inside
  `common/units/ship_destroyer.txt` / `ship_frigate.txt` / `ship_light_cruiser.txt`. The
  aggregate spelling is `screen`. `convoy` fails for a different reason — convoys are an
  **equipment archetype**, not a hull; there is no `common/units/ship_convoy.txt`, and the
  country-scope read is `num_equipment@convoy`.
- **Rule:** before writing `num_ships_with_type@X`, confirm X is either a filename-backed
  sub-unit in `common/units/ship_*.txt` or one of the four aggregates. Category names read
  as 0. And when a metric is a *sum over hull types*, prefer the explicit sum over the
  aggregate if any consumer compares it to a savegame parse — `savegame.py navy` defines
  `screens = destroyer + frigate + light_cruiser`, so summing those three makes the
  cross-check an identity instead of a dependency on aggregate membership.
- **Generalisation — the token oracle.** The game install's `documentation/` folder is the
  authority for *four* separate questions, and each has caught a wrong claim in this repo:
  `modifiers_documentation.md` for which scopes a modifier is legal in,
  `dynamic_variables_documentation.md` for **which tokens can be read into a variable**,
  and `triggers_documentation.md` / `effects_documentation.md` for the rest. Grep the
  relevant one before asserting that a token works or that a zero is real.
- **Corollary for zeros:** a WA_TLM metric reading 0 has three possible meanings — never
  instrumented, real zero, or *bad token*. Only the first two are covered by the absence
  contract. When a fix corrects a token, **bump `WA_TLM_version`** even though the metric
  set is unchanged, so analysts can tell an artefact save from a measurement save.
- **Evidence:** `WA_TLM_core.txt` v4 → v5; campaign `02bd4445`, where `@submarine` and
  `num_ships` are exact to the hull while `@screen_ship` and `@convoy` read 0 on
  ENG/USA/GER/JAP; correct in-repo usages at `common/national_focus/usa.txt:12486-12593`
  and `common/scripted_effects/WA_AI_misc_effects.txt:770-778`.

### `naval_mission_threshold` is a bar, not a priority — positive SUPPRESSES the mission

- **Symptom:** WA's Atlantic escort plan
  (`WA_AI_NAVAL_FACTION_ALLIES_atlantic_north_corridor`) ended with
  `naval_mission_threshold MISSION_CONVOY_ESCORT value = 5000` — a block whose entire
  purpose is to make the Allies escort the Atlantic convoy corridor, ending with an
  instruction not to escort it. It read as a boost to two separate passes, and the
  session brief for R36 repeated the same misreading about the JAP line.
- **Cause:** the value is added to the **score bar a mission must clear** before the AI
  will assign it, so *higher = less of that mission*. Vanilla states this in its own
  comment: `JAP.txt:970` writes `value = 150 #puts our threshold at 250` (engine base
  100) inside a block named `conserve_fuel_for_usa_fight` that exists to *stop* escorting.
  WA's own `WA_AI_NAVAL_DEFAULT_legacy_AI_naval_mission_fix` writes patrol and strike
  force **negative** under the comment "Fixes the AI not putting out its strike force and
  patrols" — the same convention, read the other way.
- **Second rule, from the same block:** the type is **Additive per mission**
  (`WA_AI_MILITARY_SYSTEM.md:106`, documented range −100..+100), and **both the quoted
  and the bare id spelling are legal** (vanilla uses bare at `ENG.txt:1379`, quoted at
  `JAP.txt:970`). `legacy_AI_naval_mission_fix` wrote each id twice, once quoted once
  bare, which looked like belt-and-braces and was in fact a **doubling**: patrol ran at
  −2000 and strike force at −1000. Any `ai_strategy` type marked Additive in the spec
  will sum duplicate writes — never assume a repeated `id =` is idempotent, and never
  assume quoting changes the key.
- **Rule:** when auditing a `naval_mission_threshold`, read it as "how much harder/easier
  did we make this mission", state the resulting bar against the engine base of 100, and
  check the block's stated purpose against the sign. A value outside the documented
  ±100 band is a smell on its own — +5000 is 50× the ceiling.
- **Evidence:** checklist R36, Fix 53a; `WA_AI_NAVAL_FACTION_ALLIES.txt`,
  `WA_AI_NAVAL_DEFAULT.txt:576`, `WA_AI_NAVAL_COUNTRY_JAP.txt:304`.

## 2026-08-13 - `obsolete=yes` on an equipment explains nothing: it is not an archetype rule and it does not gate production

- **Date:** 2026-08-13
- **Symptom:** Fixes 46, 48, 50 and 51 all failed together (checklist R30/R31/R33/R35) and a
  single shared cause looked settled: in every case the equipment the mod wanted built
  carried `obsolete=yes` in the savegame's top-level `equipments={}` registry while the
  type it wanted avoided was the only non-obsolete member of its chain. The proposed fix
  was to re-parent the unwanted chassis out of the wanted one's descent line so the
  equipment graph would match the branching technology graph.
- **Cause:** the premise does not survive measurement. Two independent readings of
  campaign `02bd4445` kill both halves of it:
  1. **It is not an archetype-uniqueness rule.** 288 of 3 540 (creator, archetype) groups
     in the final save hold **two or more** non-obsolete members - up to six - including
     five members of one strictly linear parent chain (ENG's `usa_hv_inf_3..6`). JAP's
     `jap_cruiser_submarine_hull_2` is non-obsolete while the strictly newer `_3`/`_4`/`_5`
     are obsolete, the exact reverse of the rule. Parentless roots
     (`generic_destroyer_hull_*`) never go obsolete at all.
  2. **It does not gate production.** 7.0% of production lines and **9.6% of assigned
     factories** in the final save run obsolete-flagged equipment, and the share *rises*
     across the campaign (3.6% → 4.9% → 7.0% of lines). USA runs 68 factories on the
     obsolete `tank_usa_medium_chassis_3` and 75 on the obsolete `usa_mechanized_equipment_4`.
     By the final save USA's own `tank_usa_medium_chassis_6` - the chassis it was building
     on six lines and 439 factories - is *itself* flagged obsolete.
  The flag correlates with supersession (94.7% agreement with "some enabled equipment of the
  same creator has you in its parent ancestry") because supersession and obsolescence share
  a cause, not because the flag drives selection. It is a UI/weighting marker.
- **Rule:** an `obsolete=yes` reading is **descriptive, never causal**. Do not build a fix on
  it, and do not conclude "the AI cannot build X" from it - go and read the production
  lines. More generally: when a shared explanation fits several failures at once, find the
  case where the two candidate mechanisms *disagree* before acting on it. Here every
  observed chain was linear, so "parent-ancestry supersession" and "newest of archetype"
  were indistinguishable - and both turned out to be irrelevant to the actual failure.
  The discriminator already existed in the shipped saves (90 fork points in the equipment
  `parent` graph) and cost one extraction pass; the proposed re-parenting would have been a
  content change to `tank_chassis.txt` and `ship_hull_submarine.txt` that fixed nothing.
- **Evidence:** campaign `02bd4445` (build `313633035`, confirmed by `wa_tlm_version = 4`
  present from the first save plus linear git ancestry through `e3629b3f0` → `a2744825d`
  → `88e516780`); checklist R30/R33/R35 history for 2026-08-13.

## 2026-08-13 - `resource@X` reads net available MINUS unmet demand, not the net column

- **Date:** 2026-08-13
- **Symptom:** R32's `WA_AI_EQUIPMENT_can_absorb_aluminium_shock_large` latch (`resource@aluminium > 50`)
  stayed shut on ENG for the whole campaign while the savegame's net aluminium read +185 to
  +976/day. With the resource bar apparently cleared by 16x, the only remaining term in the
  trigger was `NOT = { WA_AI_industry_overextended = yes }`, so Fix 39's fragility guard was
  written up as a design collision that nailed ENG's latches shut permanently.
- **Cause:** `resource@X` is `to_use[0] + to_use[2]` - net available **minus** unmet demand -
  not `to_use[0]`. ENG's aluminium at 1942.6 is net 807.3, deficit −799.0, **effective +8.3**
  against a `> 50` bar. The latch was failing on the resource value itself and Fix 39 never
  came into it: the latch shut in 1938.11, 57 months before ENG's overextension flag was
  first set, and `wa_ai_overext_dbg_active` is absent for ENG/SOV/USA/GER at every sampled
  date before 1944. **Fix 39 is exonerated.**
- **Rule:** score every `resource@X` guard on **net + deficit** (`savegame.py resources` now
  prints it as the `EFFECTIVE` column). Two failure modes stack here and both have burned a
  scoring session: reading `produced` alone (nearly a false FAIL on R25) and reading `net`
  alone (a false accusation against Fix 39). Related and more general: **a rule induced from
  a single resource is not a rule.** The superseded "net alone" wording was drawn from ENG
  *bauxite* in the very same save, whose deficit happens to be −1.0 so both readings agree
  there; the aluminium row two lines below it disagreed by a factor of 97.
- **Evidence:** campaign `02bd4445`, 36 discriminating (country, date, resource, bar) cells
  across ENG/SOV/USA/GER at 1939.6 / 1941.6 / 1942.6 - all consistent with net+deficit, none
  with net, pass/fail bracketing the `> 5` / `> 15` / `> 20` / `> 50` bars to within one unit
  (PASS at 6.0, 21.0, 26.0, 28.0; FAIL at 4.0, 9.0, 14.0, 14.2, 15.0). Triggers at
  `common/scripted_triggers/WA_AI_EQUIPMENT_triggers.txt:86-152`; corrected in
  `.claude/skills/wa-savegame-analysis/SKILL.md` and `scripts/savegame.py`.

## 2026-08-13 - `production_upgrade_desire_offset` waives a stockpile-surplus check on an EXISTING line; it cannot choose what a new line builds

- **Date:** 2026-08-13
- **Symptom:** Fix 51 moved the whole equipment-selection package onto
  `production_upgrade_desire_offset` (57 entries over 11 tank frontiers, plus the SOV
  submarine pair), on the reasoning that `ai_equipment` `priority` is the design layer and
  this is the production-line layer. Campaign `02bd4445` then reproduced every failure
  exactly: SOV ran the coastal Malyutka in **all 120 saves**, JAP held a coastal line for
  the last 39 months, USA converged on T23 across six lines and 439 factories. Nothing
  moved by a single factory.
- **Cause:** the type does something narrower than its use assumed. Vanilla's own comment
  on it, at `common/ai_strategy/SOV.txt:360` in the game install, reads: *"100 essentially
  means we don't require a stockpile surplus"*. It offsets the **desire to upgrade an
  existing production line** onto a newer equipment, and what it modulates is the
  stockpile-surplus threshold that upgrade normally waits for. Two consequences that
  invalidate the way WA used it:
  1. **`+100` on an older/wanted design is a no-op.** You never "upgrade" a line *to* an
     older chassis, so roughly half of Fix 51's emitted entries could never do anything.
  2. **It never sees line CREATION.** The observed failures are new lines being opened on
     the unwanted equipment (USA jumps M3 Lee straight to T20 and later opens *new* T23
     lines; SOV opens fresh Malyutka lines), not existing lines drifting newer. A `-100`
     cannot stop a line that was never an upgrade.
  Expert AI 5.0 uses the type 46 times and every use fits the real semantics: each `-100`
  is gated on a stockpile condition (`enable = { has_equipment = { infantry_equipment <
  10000 } }`) and holds an *existing* line on the old rifle until the stockpile fills, with
  a comment that says the point is not spending XP yet
  (`EAI_PRODUCTION_equipment_strategies.txt`). It is a "don't upgrade yet" knob, and that
  is exactly what it is named.
- **Rule:** before adopting an `ai_strategy` type, find a **vanilla or Expert AI use of it
  and read what that use is trying to achieve** - not just its type name and id shape. The
  id form matching (an equipment token, which WA got right) proves nothing about whether
  the lever answers your question. Here the type name contains the answer: *upgrade*
  desire. Related: `equipment_variant_production_factor` is not the alternative either -
  vanilla only ever gives it an **archetype** id (`medium_tank_chassis`,
  `large_plane_airframe`), so it cannot discriminate between two chassis of the same
  archetype.
- **Evidence:** game install `common/ai_strategy/SOV.txt:357-366` (the comment) and
  `_documentation.md` (the type is listed but never described); Expert AI 5.0
  `common/ai_strategy/EAI_PRODUCTION_equipment_strategies.txt`; checklist R30/R33/R35
  history for campaign `02bd4445`. See also the sibling entry on `obsolete=yes`, which was
  the other candidate explanation and is equally dead.

## 2026-08-13 - An `ai_equipment` priority ladder must stay inside the range the engine is observed to honour

- **Date:** 2026-08-13
- **Symptom:** `SOV_heavy_tanks` (13 ranks) emitted `factor = 0.000009` at its floor, and
  four other frontiers bottomed out between `0.001` and `0.01`.
- **Cause:** the generated ladder is geometric (`1 / 0.3 / 0.1 / 0.03 / ...`) applied to the
  group's historical maximum, so its span grows as `3^ranks`. A ≥3x step on every one of 12
  steps needs a 531 441x span, while only 100x is available above any sane floor. The
  bottom rungs then land where the engine's fixed-point script numbers cannot distinguish
  them from `0` - and `factor = 0` in `ai_equipment` means *never pick this design*, so the
  ladder was enforcing dominance by **disabling the emergency fallbacks it existed to
  protect**. External calibration: the smallest priority factor in **all of vanilla
  `ai_equipment` is 0.1**, and in Expert AI 5.0 it is 0.5.
- **Rule:** when generating engine-facing numbers, bound them by the range the engine is
  *observed* to use, not by what the arithmetic produces - and when two invariants cannot
  both hold (here "≥3x between every rank" and "never emit an unrepresentable factor"),
  keep the one whose violation is a **correctness** failure and relax the one whose
  violation is a **fidelity** failure. The fix keeps every rank above the knee at its exact
  geometric value and re-spaces only the underflowing tail down to a configurable floor, so
  dominance is untouched where it decides anything.
- **Evidence:** `tools/equipment_evaluator/ground.py::_frontier_priority`,
  `config.json` `frontier_priority.floor`, tests in `test_generation.py::FrontierLadderTests`;
  25 factors rescaled across `FRA/GER/JAP/SOV/USA_tank.txt`.

## 2026-08-13 - Check what a technology LEADS TO before suppressing it, and suppress it from ai_strategy, not from ai_will_do

- **Date:** 2026-08-13
- **Symptom:** with the design layer and the production-line layer both settled negatively,
  the remaining way to stop the AI building an unwanted chassis is to stop it researching
  the branch. The obvious implementation - `ai_will_do = { factor = 0 }` on the two USA
  techs - was already written up as the plan.
- **Cause:** two independent traps, both invisible in the diff that plan would have produced.
  1. **Downstream stranding.** `usa_medium_tank_chassis_5` (T23) leads to
     `usa_modern_tank_chassis_1` (M26 Pershing), and the entire USA heavy line (chassis 2-7)
     hangs off that in turn - **15 equipment tokens** would have gone with it. The same shape
     on the SOV side: `sov_medium_tank_chassis_5` (T-43) gates the whole T-44 -> T-54 modern
     line. Both survived only because the technology graph forks *and rejoins*:
     `usa_modern_tank_chassis_1` is also reachable from `usa_medium_tank_chassis_3_3`
     (M4A3E8) and `sov_modern_tank_chassis_1` from `sov_medium_tank_chassis_3_4` (T 34 85) -
     the very branches being steered onto. Had the fork not rejoined, the fix would have
     traded a medium-tank preference for the loss of every USA heavy and modern tank, and
     nothing in the campaign that motivated it would have shown that.
  2. **Wrong file to edit.** Technology `ai_will_do` blocks are **tool-managed**
     (`tools/ai_will_do_replacer_all.py`, `tools/ai_replacer_base/`; every WA tech carries the
     same generated shape - `factor = 1` plus a `WA_AI_RESEARCH_needs_*` modifier and a date
     gate). A hand-written `factor = 0` there survives until the next regeneration and then
     vanishes silently. The `ai_strategy` type **`research_weight_factor`** does the same job
     from outside that pipeline, and is documented: *"Factor the ai_will_do value for the
     specified technology with this. (50 means 50 % increase, -30 means 30 % decrease)"*, so
     `-100` zeroes the weight.
- **Rule:** before suppressing any technology, compute its **transitive downstream reach**
  and the **in-edges of everything in that reach** - the suppression is safe only if every
  stranded node has another live path. State the equipment that would be lost, not just the
  tech. And when the natural target file is generated, look for an `ai_strategy` type that
  expresses the same intent; editing generated output is a fix with a shelf life.
- **Evidence:** Fix 57, `common/ai_strategy/WA_AI_RESEARCH_COUNTRY_{USA,SOV,JAP}.txt`,
  checklist R40 (opened as R37, renumbered 2026-08-14); game install `common/ai_strategy/_documentation.md` for
  `research_weight_factor`; `common/technologies/armor_usa.txt:2935,2993`,
  `armor_sov.txt:3053`, `naval_jap.txt:3987,4038`.

## 2026-08-13 - A missing ai_equipment design is invisible everywhere, and it frames the AI for a decision it made correctly

- **Date:** 2026-08-13
- **Symptom:** checklist R35 recorded "ENG medium 1944.6 & 1946.4 Cromwell (100) -> **Comet**"
  as one of six faulty frontiers - the AI ignoring the mod's ranking and building the newest
  chassis. `WA_AI_PRODUCTION_COUNTRY_ENG_TANKS.txt` looked consistent with that reading: a
  single `+100` on the Cromwell, `enable = always`, and no suppressions at all.
- **Cause:** `tank_eng_medium_chassis_5` (Comet) had **no design in any ENG `ai_equipment`
  group**. `ai_equipment` only steers equipment it has a design for, so the engine
  auto-designed the Comet and built it outside the ranking, outside the
  `WA_AI_EQUIPMENT_*` resource gates, and outside the emitted
  `production_upgrade_desire_offset` blocks. The generator had ranked 7 designs while the AI
  was building an 8th it had never heard of - and it emitted a lone `+100` not because the
  emitter was broken but because, among the designs it could see, the Cromwell really was
  top rank with nothing newer to suppress. **Once the design was authored, the evaluator
  ranked the Comet PRIMARY, above the Cromwell (+1.224 vs +1.157): the AI had been right and
  the mod was wrong.** The tell was there all along - `medium_tank_7` (Cromwell) already
  carried `modifier = { has_tech = eng_medium_tank_chassis_5 ... factor = 0 }`, a
  supersession pointing at a Comet design that was never written.
- **Rule:** a coverage gap in the design layer is invisible in **every** output the
  generator produces - the role looks fully covered and simply ranks its top design first.
  So before recording "the AI ignored our ranking", check that the equipment it actually
  built **has a design at all** (`tools/equipment_evaluator --domain tanks` now reports
  these into `output/coverage_gaps.md`). Corollary for authoring: a design's supersession
  hook must point at the next chassis **in the same role**. The Comet's successor tech
  `eng_modern_tank_chassis_1` belongs to `ENG_modern_tanks`, and hooking a medium design to
  it would empty the medium role the moment modern tanks are researched.
- **Evidence:** Fix 58, `common/ai_equipment/ENG_tank.txt` `medium_tank_8`; checklist R35
  Comet sub-probe and its retraction; `output/coverage_gaps.md` (39 -> 38 gaps, 11 -> 10 in
  branched roles).


### `has_capitulated = no` on an ALLY hides the ground an expeditionary army is standing on

- **Date:** 2026-08-14
- **Symptom:** in campaign `f9321934` Britain held **no AIFC sector at all from May 1944 to July
  1946** — every `wa_ai_aifc_*` variable absent for ~118 consecutive weeks — while fielding
  116–143 divisions, holding standing level-1 execute orders against Germany, and having 15–17 of
  those divisions physically standing in Lower Normandy. France, meanwhile, held a sector frozen
  byte-identical (`anchor=34` Wallonie, `age=4`) from 1940 to the last save.
- **Cause:** two separate sites, one word. (1) The Fix 28 expeditionary fallback in
  `WA_AI_AIFC_helpers.txt:92-101` walks `every_country` filtered on `has_capitulated = no` before
  looking for allied soil ROOT has ≥3 divisions on. **FRA carried `capitulated=yes` for the entire
  campaign while owning 60 states and controlling 50** — including the liberated French soil the
  whole British expeditionary army was standing on. The filter skipped FRA, the candidate array
  came back empty, and the effect fell through to `WA_AI_AIFC_clear_sector` every single week.
  (2) The weekly caller itself, `WA_AI_misc_on_actions.txt:112-116`, wraps the call in
  `is_ai = yes` + `has_capitulated = no` **on ROOT**, so FRA was never iterated at all and its
  1940 sector could neither age nor clear.
- **Why it is not obvious:** "capitulated" reads as "dead", and the AIFC comments treat the two as
  synonyms ("harmless — the tags do not exist"). In HOI4 they are not synonyms: a capitulated tag
  keeps its faction membership, keeps owning and controlling territory, and **regains control of
  liberated home soil** while still reporting `capitulated=yes`. A liberating ally therefore fights
  its whole campaign on the territory of a country every capitulation filter is throwing away. The
  same commit that added the filter (`4ffb8e442`, Fix 28) **omitted it 60 lines later** in the
  launching-pad measurement (`helpers:147-160`), which is the tell that it was an incidental paste
  of the "usable ally" idiom rather than a designed rule.
- **Rule:** `has_capitulated` answers "did this country's government fall", never "is this
  country's territory usable" and never "does this country still exist". Before filtering an ally
  on it, ask which of the three questions you actually mean. For *existence* use `exists = yes`;
  for *usable territory* use the thing you actually need (`is_in_faction_with`, controller checks,
  and above all ROOT's own `divisions_in_state`, which is the real guard here — a capitulated
  ally's territory ROOT is not standing on is excluded by that term anyway). Same family as the
  `surrender_progress` lesson above: a *status* metric substituted for a *capability* one, and a
  release condition the country cannot reach by recovering.
- **Not a fix for the front, and do not sell it as one.** AIFC issues no attack orders, and Layers
  1–2 (`force_concentration_factor`) are not sector-gated, so the missing sector cost ENG a
  *scripted axis*, not its concentration. A Normandy-anchored sector would have published +50 front
  factor / +50 target weight there and −50/−99 everywhere else — i.e. pushed **more** divisions into
  a state that already held 42→79 Allied divisions against ~11 defenders. Diagnose the blast radius
  of the layer before promoting a correlation to a cause.
- **Evidence:** checklist R39 (2026-08-14 diagnosis entry, campaign `f9321934`) and R42 (the fix);
  **Fix 65** removed the ally-side filter at `WA_AI_AIFC_helpers.txt` section 1b and its lockstep
  twin in `WA_AI_AIFC_core.txt` (Fix 28 validity mirror), replacing it with `exists = yes`; the
  unfiltered launching-pad twin at `helpers` section 1c needed no change. **Fix 68** handled the
  ROOT-scoped copy at `WA_AI_misc_on_actions.txt` by **moving the call, not deleting the word**:
  `WA_AI_AIFC_update_sector` now sits in its own `is_ai = yes` block instead of inside the
  `is_ai = yes` + `has_capitulated = no` Priority-Construction block, so the effect's own
  "not eligible -> clear" branch becomes reachable while the other six calls in that block stay gated.
- **Second-order rule, from the shape of Fix 68:** when an effect is *designed* to be entered while
  ineligible - "the effect no-ops and clears any stale sector when the country does not qualify" -
  then hosting it inside a shared eligibility gate **silently deletes its cleanup path** for exactly
  the population that needs it. The gate and the effect's own trigger were testing the same thing, so
  the outer one looked redundant and was in fact load-bearing in the wrong direction. Check where a
  self-gating effect is *called from* before trusting its "no-ops when ineligible" comment.
  Cleanest confirmation: ENG's sector returns at 1946.8 anchored on **47 Thessaly** in the same
  month it acquires **187 Aegean Islands**, whose province 3401 carries the map's only special
  adjacency to Thessaly's 7127 (`map/adjacencies.csv`) — native contact, restored one state at a time.

## 2026-08-14 - `equipment_production_min_factories` is need-blind AND additive across blocks, so a flat factory count on every line of every country is the fingerprint of a floor, not of demand

- **Symptom:** carrier navies built far more `cv_*` aircraft than their decks could hold and
  parked the surplus on land airfields — campaign `f9321934`, JAP finishing at 8 619 carrier
  planes on land against 1 380 on deck (6.25:1, 75% of its whole air force), ENG at 2.09:1
  with **52% of the RAF being naval aviation**. 92% of JAP's and 94% of ENG's land-parked
  carrier planes carried **no mission at all**, so it was waste, not an improvised shore role.
- **The reading that pointed at the cause, and it was a shape, not a number.** Every
  carrier-fighter and carrier-naval-bomber production line of ENG, JAP and USA ran at
  `requested_factories = active_factories =` **exactly 8**, at 1944.6 *and* at 1946.8. Six
  independent cells, one number, across three economies of wildly different size — and 8 is
  exactly `2 + 6`, the base floor plus the carrier-major floor in
  `WA_AI_PRODUCTION_DEFAULT_cv_plane.txt`. USA's carrier-CAS line sat at exactly 1, its own
  lone floor. **`ai_strategy` values of the same type and id from several enabled blocks sum**,
  and vanilla's own comment says the type *"Forces the AI to allocate this many factories …
  it doesn't take into account how many factories are actually available"*
  (`common/ai_strategy/documentation.info section EQUIPMENT PRODUCTION FACTOR`). A flat, identical, cross-country factory count
  is therefore a floor signature; demand-driven allocation never looks like that.
- **Why the obvious lever was the wrong one, twice over.** The instinct is to cut
  `ai_equipment` `priority` on the `cv_*` design groups. It would have done nothing: those
  groups declare **dedicated roles** (`air_cv_fighter`, `air_cv_naval_bomber`), so they never
  compete with a land role, and priority chooses *which airframe gets designed*, never *how
  many get built* — the same design-layer error already recorded after `bec4d829`. The second
  instinct, cutting `unit_ratio`, is also wrong: `documentation.info` (### UNIT RATIOS, AIR)
  says land-based and carrier plane types are pooled **completely separately**, and the carrier
  pool total is computed by the engine from deck capacity × 1.5
  (`WANTED_CARRIER_PLANES_PER_CARRIER_CAPACITY_FACTOR`, `00_defines.lua:2796`) **minus the
  carrier planes already in airwings, land-parked ones included**. `unit_ratio` only splits
  that total between the cv roles, so it cannot raise it. Which yields the punchline: a
  saturated country's engine demand is **already zero** and the floor is the only thing still
  building. `equipment_production_factor` was no escape either — its documented id namespace is
  `script_enum_equipment_category`, which contains no `cv_*` entry at all.
- **Rule:** before tuning any production-volume lever, ask *which layer sets the volume*.
  `ai_equipment` priority = which design. `unit_ratio` = the split within an engine-computed
  pool. `equipment_production_factor` = a percentage of computed need, so it self-zeroes.
  `equipment_production_min_factories` = an unconditional, additive, need-blind override, and
  it is the **only** one of the four that can keep building after demand reaches zero. If a
  fix has to stop over-production, it almost certainly has to gate a min-factories floor.
- **Corollary for gating it:** a rule keyed on fleet *size* could not have worked here. JAP
  (4.83× the engine's target, 20 hulls) and USA (0.96×, 47 hulls) are both large carrier
  fleets; the discriminator is planes-vs-decks, which forces an actual plane count
  (`num_deployed_planes_with_type@<archetype>`). Where the measurement is unproven, build the
  gate so an unresolvable token reads 0 and the brake simply never trips — then behaviour
  degrades to today's, never to something worse. **Fix 66**, checklist **R43**.
- **Evidence:** checklist R43; `.claude/skills/wa-savegame-analysis/scripts/cvair.py`.

## 2026-08-14 - `air_lines` does not exist in the 1.19.2 save format: aircraft production lines are in `military_lines`

- **Symptom / contradiction:** `wa-savegame-analysis`'s gotcha list says production lines live
  in **three** sibling blocks, `military_lines`, `naval_lines` and `air_lines`, and that naming
  only `military_lines` "silently returns zero submarine and zero aircraft lines". Scanning all
  three names explicitly across six (country, date) cells of `f9321934` found **zero
  occurrences of `air_lines` in any country block**, and every aircraft line — carrier and
  land, ENG/JAP/USA — inside `military_lines`. The third sibling that does exist is
  `general_lines`, and it holds buildings.
- **Status: not resolved, deliberately.** The submarine half of the original gotcha is
  consistent with this (subs are in `naval_lines`, so `military_lines` alone does miss them);
  the aircraft half is not. Whether the old note was a wrong generalisation or the block name
  changed between game versions has **not** been established, so the SKILL.md gotcha was left
  standing rather than silently rewritten.
- **Rule:** scope a production scan to `military_lines` **and** `naval_lines` **and**
  `air_lines`, and have it **report which block names it actually found**. Naming a block that
  does not exist fails silently and returns a confident zero — which on this question reads as
  "the AI never built any aircraft". Never conclude "the AI does not build X" from an empty
  result without first confirming the block you scoped to is present in the file.
- **Evidence:** checklist R43's probe, step 3.

## 2026-08-14 - A shadow cost table that matches VANILLA is still a bug: check what the mod re-priced, not just whether the numbers look principled

- **Symptom:** the AI's priority-construction system (`WA_AI_PC_get_building_cost`) charged
  `170 + 130 * (1 + existing level)` for a railway segment. Reviewed against
  `common/buildings/00_buildings.txt` — where `rail_way` is `base_cost = 800`,
  `per_level_extra_cost = 0` — it looked like an invented, undocumented model: wrong shape
  (escalating where the engine is flat), wrong magnitude (300 for a fresh segment against 800),
  no `# Fix NN:` rationale, and contradicting the system's own scoring constant
  (`@WA_AI_PC_RAILWAY_BASE_COST = 800  # flat per segment`). The first audit wrote it up as
  "UNRECONCILED, origin unknown, introduced whole by `cad27bfbd`".
- **Cause:** 170 and 130 are **vanilla's** `rail_way` `base_cost` and `per_level_extra_cost`,
  exactly. The block was a faithful copy of the base game and was correct the day it was
  written. WA later re-priced `rail_way` to a flat 800 (1000 → 800 in `42b53eccb`, Oct 2023,
  "Decreased the cost of railroads") and nobody updated the AI's shadow table, so for ~3 years
  the AI bought rail at the base game's price — 37% of the mod's. Reading the vanilla install's
  `00_buildings.txt` settled in one command what the repo alone could not.
- **Rule:** in a mod that `replace_path`s a vanilla folder, a constant that disagrees with the
  mod's data is **not evidence that someone invented it** — diff it against the *vanilla* file
  before writing "origin unknown". The default history of any such mismatch is "copied from
  vanilla, then vanilla-side data was re-tuned and the copy drifted", and that reframing changes
  the fix: you are not designing a model, you are re-syncing one, and the correct new value is
  whatever the mod's data says today. Generally: **whenever mod script hardcodes a number that
  also exists in a replaced vanilla data file, the vanilla file is a required source in the
  audit, not an optional one.** The install ships its own `documentation/` too
  (`effects_documentation.md`, `modifiers_documentation.md`) — see the modifier-scope oracle.
- **Corollary that generalises past this case:** a *shadow* system — one that recomputes a game
  value in script instead of asking the engine — has no failure mode that surfaces at parse
  time or in a log. It silently diverges the moment its source data moves. Every such table
  needs a comment naming its source file, which is now on the table itself - since 2026-08-16
  the table is `constant:wa_ai_pc.cost.*` in `common/script_constants/wa_ai_pc.txt` (was the
  `global.WA_AI_PC_BUILDING_*_COST` block of `WA_AI_PC_set_global_variables`), and every key is a
  registered mirror of `00_buildings.txt` so `python tools/check_constants.py` reports a
  re-price. The same audit found air base (250 vs 300), radar (500 vs
  2500) and naval base (3000 vs 10000) drifted the same way, all in the same table.
- **Evidence:** **Fix 72** (air base / radar / naval base) and **Fix 73** (railway) in
  `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt`; checklist **R8** and **R19**;
  vanilla `rail_way` at `<install>/common/buildings/00_buildings.txt`.

### A loop inside `for_each_scope_loop` runs in the ITERATED scope, not ROOT

- **Date:** 2026-08-14
- **Symptom:** none, for three years. `WA_AI_PC_railway_STRATEGY_land_war`'s Fix 27 puppet-frontline
  scan produced no routes in any campaign, and nobody noticed because the ROOT loop above it
  produced plenty.
- **Cause:** the effect's shape was

  ```txt
  for_each_scope_loop = { array = _relevant_enemies_      # THIS = the ENEMY from here on
      if = { limit = { ... }
          ROOT = { every_controlled_state = { ... } }     # explicit, correct
          every_subject_country = { ... }                 # NO wrapper -> the ENEMY's subjects
      }
  }
  ```

  The sibling loop above it carries an explicit `ROOT = {}`, which is exactly what makes the missing
  one invisible on a read: the two look like a matched pair. `every_subject_country` bound to the
  enemy, so the body's own acceptance test (`controller = { is_subject_of = ROOT }`) could never pass
  and ROOT never controlled those hub provinces. Dead from the day it was written.
- **Rule:** inside a `for_each_scope_loop` / `every_*` block, **every** country-level iterator needs an
  explicit scope wrapper — write `ROOT = { every_subject_country = { … } }` even when it reads as
  redundant. When auditing, don't check the iterator against the *nearest* wrapper; check it against
  the innermost enclosing **scope-changing** construct. A `# Fix NN:` comment on a block is not
  evidence the block ever ran: confirm it in a save or with a counter before treating it as covered.
- **Detection:** a fix whose behaviour has never once been observed in a campaign is the tell. If a
  loop's acceptance test is structurally unsatisfiable in its actual scope, it is dead code wearing a
  changelog comment.
- **Evidence:** `WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt`, found while implementing Fix 74;
  checklist R46 leg 3 verifies the revival.

### An annihilated tag keeps stale country variables that read as live values

- **Date:** 2026-08-14
- **Symptom:** on campaign `be18f9c7`, GER's final save (1946.7) reports a 4-project Priority
  Construction queue with `wa_ai_pc_assigned_factories_total = 14`, `wa_ai_fielded_eq_ratio =
  0.93313`, an intact `wa_tlm_*` block and a `ruling_party` that had flipped from fascism to
  communism. Every one of those readings describes a country that no longer exists: GER holds
  **0 owned and 0 controlled states from 1945.7 onward** and has **no `units` section** in any
  of the 13 saves from 1945.7 to 1946.7.
- **Cause:** a country block is never removed from a save when the country is annihilated - only
  its territory, army and the AI systems that write to it stop. Every variable keeps its last
  written value forever. GER's whole variable set freezes at the **same** boundary (1945.6 →
  1945.7): `wa_tlm_comp_last_t` and `wa_tlm_nav_last_t` both pin at **113** (1945.6) while live
  tags read 126, and `wa_ai_fielded_eq_ratio` is byte-identical across 13 consecutive saves. The
  values are not corrupt and not zero - they are a **1945.6 snapshot wearing a 1946.7 filename**,
  which is exactly what makes them dangerous: a probe reading "the last save" gets a plausible,
  well-formed, twelve-months-stale number and nothing in the output says so.
- **Rule:** before trusting any country variable on a late-campaign save, **prove the tag is still
  alive**: owned states > 0, or a `units` section present, or - cheapest on an instrumented build -
  the family's own `*_last_t` stamp equal to the live tags' stamp. Byte-identical values across
  consecutive saves are the tell; so is an aggregate that disagrees with its own array (GER's
  `assigned_factories_total = 14` while every `wa_ai_pc_assigned_factories^0..^3` reads **0**).
  When a dead tag is the *subject* of a probe, run it on the tag's last live save instead, and say
  in the evidence line which save that was.
- **Detection:** any late-save reading that looks reasonable for a country that should be dead.
  This is a different failure from the `wa_ai_aifc_*` frozen-sector case already recorded in the
  checklist (R39/R42): that one is a **live** tag whose weekly on_action skips it, this one is a
  tag with nothing left to iterate. Both produce frozen variables; only the first is fixable in
  script.
- **Evidence:** campaign `be18f9c7` (build `d683fb022`), GER on `1945.6_Jun.hoi4` (last live save)
  vs `1945.7_Jul.hoi4` … `1946.7_Jul.hoi4`; checklist R41's GER cruiser-submarine control, which
  has to be read on 1945.6 for exactly this reason.

### `first_nuke_dropped` records the LATEST nuke, not the first

- **Date:** 2026-08-14
- **Symptom:** campaign `be18f9c7` stamps `JAP_nuke_1` at **1945.12.5.23** but the global flag
  `first_nuke_dropped` at **1946.5.18.24** - the same instant as `JAP_nuke_2`, and **164 days**
  after the first bomb actually fell.
- **Cause:** in `common/on_actions/00_on_actions.txt`, `on_nuke_drop` sets the flag with **no
  guard** (`set_global_flag = first_nuke_dropped`, ~line 207) while the two JAP flags immediately
  below it are each wrapped in `NOT = { has_global_flag = … }`. Re-setting an already-set global
  flag refreshes its recorded date, so the save stores the date of the **most recent** drop. The
  flag's *presence* is correct from the first bomb; only its date is wrong, and the name says
  otherwise. **Inherited from vanilla** - vanilla's own copy sets it unguarded too, then tests
  `NOT = { has_global_flag = first_nuke_dropped }` on the very next line, a branch that can never
  be true.
- **Rule:** a global flag's set-date is only a first-occurrence timestamp if the `set_global_flag`
  is guarded by its own `NOT = { has_global_flag = … }`. Before dating **any** event from a flag,
  read the write site and check for that guard - and prefer a flag that is written once by
  construction (WA's `*_nuke_1` shape) as the timeline anchor. The same applies to `set_country_flag`.
- **Detection:** two flags from one on_action sharing an instant when they describe different
  events. If a "first X" flag's date equals a "second X" flag's date, the first one is unguarded.
- **Evidence:** `common/on_actions/00_on_actions.txt:205-232`; the only in-repo reader is
  `common/national_focus/soviet.txt:15543`, which tests **presence**, not date - so no gameplay
  behaviour is wrong today and this is an analysis trap first. Guarding the set (or reading
  `JAP_nuke_1`) is the fix if a date consumer is ever written.

### An absent indexed variable is indistinguishable from a zero one - check presence before reading a cohort as "reset"

- **Date:** 2026-08-14
- **Symptom:** campaign `be18f9c7`, GER 1944.6: **80 railway projects all reading
  `wa_ai_pc_stall_weeks = 0`** simultaneously. Read as a queue-wide *stall-counter reset*, which
  had been on the R19 watch list as a suspected instrumentation bug for **four consecutive
  campaigns** (SOV 13@13, JAP 27@14, GER 69@18, SOV 36@24...). If real, it meant R19's central
  criterion was measuring an artefact and the mechanism under test might never have run.
- **Cause:** there was no reset and no bug. `WA_AI_PC_start_project` never initialises
  `WA_AI_PC_stall_weeks^id`, `WA_AI_PC_assigned_factories^id` or `WA_AI_PC_build_time^id` - those
  are written first by the weekly maintenance pass. `check_variable` reads an absent variable as
  **0**, and a savegame simply omits it, so a freshly enqueued cohort and a reset cohort look
  identical. The 80 projects were a **mass enqueue**: all 80 (province, connect) pairs were new
  versus the previous month, which held zero type-13. Stalls synchronise **iff** the projects were
  never funded - the control is JAP 1946.7, whose 13 *partially built* survivors carry fully
  desynchronised stalls (0,1,3,4,5,10,11,12,13,20,21,21,22).
- **Rule:** when several slots of an indexed variable share a suspiciously uniform value, test
  whether the variable **exists** before interpreting the value. In a save that means grepping for
  the `name^index` key itself, not reading a parsed 0. More generally: any per-record field not
  written at record creation is unreadable as state until its first maintenance pass, so
  **initialise indexed fields at `add_to_array` time** if a reader (or an analyst) will ever
  compare them across records.
- **Detection:** a uniform value across many slots, together with the *other* per-record fields
  being equally uniform. Real aging desynchronises; creation does not.
- **Evidence:** `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt` -
  `WA_AI_PC_start_project` sets target/cost/progress/type/priority but no stall or assignment
  field; the counters are first written in `WA_AI_PC_update_project_progress`. Checklist R19's
  "synchronised stall counter" watch item is closed by this entry.

### A single-pulse debug variable is not a multi-month state - and a shared resting value hides which branch you are in

- **Date:** 2026-08-14
- **Symptom:** campaign `be18f9c7` scored "`wa_ai_uk_air_dbg_best = -2` persists **5 consecutive
  months** for USA (1943.2-1943.6), i.e. the deficit branch was entered and **no buildable site was
  found**" - which pointed the whole UK air-base diagnosis at state eligibility (building slots,
  a leaked per-state project counter). Both hypotheses were false: 33 of 33 state x save cells
  were clean, and air bases have their own `state_max` cap and never compete for shared slots.
- **Cause:** two compounding traps. (1) `WA_AI_uk_air_dbg_best` is **reset at the top of every
  gated pulse** (~2-day cadence) and overwritten only when a site is actually queued, so a monthly
  save reports **one pulse**, not the month. `dbg_started` advanced **+1 in every one of those five
  months** - the builder was healthy throughout. (2) The reset value `-2` was documented as "no
  deficit" while the deficit branch left it untouched when it queued nothing, so `-2` had silently
  become the resting value of *two different states*: "satisfied" and "deficit open, budget full".
- **Rule:** a debug/telemetry variable that is re-initialised every pulse can only ever be read as
  a snapshot; **trend questions must go to a cumulative counter** (`dbg_started`, `WA_TLM_*_n`),
  which cannot fall between saves. And when a variable encodes branch identity, every branch needs
  its **own** sentinel - a shared resting value across two branches is unfalsifiable by
  construction. Corollary for authors: pair every such gauge with a counter, and state the cadence
  in the legend next to the sentinels.
- **Detection:** a sentinel that appears at a *sample rate* rather than in runs matched by other
  evidence; or a counter that advances while the gauge claims nothing happened. Those two
  statements contradicting each other means the gauge is per-pulse.
- **Evidence:** `WA_AI_build_uk_air_hosting_capacity` in
  `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies.txt` - the `dbg_best = -2`
  pre-set sits above the deficit branch. Fix 78 splits the legend (`-1` = deficit open, nothing
  queued this pulse) and adds the cumulative `WA_TLM_r8_air_lane_grants`. Checklist R8's metric
  note is recut accordingly.

### A UTF-8 BOM in a scripted_effects file kills the whole file - and the error log points at the wrong line

- **Date:** 2026-08-15
- **Symptom:** `error.log`: `unexpected token in file: "common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt" near line: 10 (  )`, followed by `( = )` and a cascade of `( } )` at later lines. The file read as syntactically perfect; braces balanced 874/874.
- **Cause:** commit `fc9fc5fab` re-saved the file with a UTF-8 BOM (`EF BB BF`). The parser for `common/scripted_effects/` and `common/scripted_triggers/` treats the BOM as a token, so the first key (`WA_AI_PC_set_global_variables`, line 10) is where it reports, and every `=`/`}` afterwards desyncs. The whole priority-construction cost table and queue init silently failed to load. The token in the log is the invisible U+FEFF itself - it renders as `(  )`.
- **Rule:** script files under `common/` and `events/` are BOM-free UTF-8; only `localisation/**/*.yml` takes a BOM (AGENTS.md rule 16). Editors/tools defaulting to "UTF-8 with BOM" reintroduce it on the next save - the fix recurred within minutes when another writer touched the file.
- **Detection:** `unexpected token ... near line: N (  )` with an *empty-looking* token, on the file's first key, in a file that reads fine. Check the first three bytes: `head -c 3 file | xxd -p` -> `efbbbf` = bad. `git cat-file -p <rev>:<file> | head -c 3` finds the commit that introduced it.
- **Evidence:** local `logs/error.log` 2026-08-15 00:52; the errors began the run after `fc9fc5fab`, and every prior revision back to 2026-02 started with `23 23 23` (`###`).

### A situational invasion suppression needs an exit condition, or it becomes a permanent lock (checklist R34, retired)

- **Date:** 2026-08-15 (rule dates from 2026-08-12; retired from the campaign checklist at 5/5 after `af003548`)
- **Symptom:** campaign `9a4cd657` - Allied divisions in metropolitan France 69 (1944.9) -> 0 (1944.10) and never re-attempted for the remaining 18 months while GER held only 23-25 divisions there.
- **Cause:** branch 2 of `ALLIES_dday_hold` (`common/ai_strategy/WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`) was the bare pair `date > 1944.12.1` AND `has_war_with = JAP`, with no exit term. From December 1944 onward, with Japan still at war, every western major was permanently under `invade GER/FRA/RFR -2000`. `abort_when_not_enabled = yes` cannot help a branch whose enable never turns false.
- **Rule:** any `ai_strategy` block that *suppresses* an operation on a situational cue (a date, an ally in the war, a landing having fired) must carry a term that reads the situation ending - the enemy's collapse (`surrender_progress`, state share), the war ending, or a scripted flag that is cleared. Read the ENEMY's state for the exit, never own capability (the R27 anti-pattern). Mirror of the situational exit `ALLIES_dday_fire_FRONT` already carried.
- **Detection:** a `value=-2000` (or any large negative) `invade`/`front` entry present in a country's `ai` section across consecutive late-war saves while that country holds a foothold and the enemy is far from collapse; on the ground, a theatre the AI *could* re-enter staying at zero divisions for 3+ months.
- **Evidence:** fix verified on `a8b29e09`, `bec4d829`, `02bd4445`, `be18f9c7`, `af003548` (no `-2000` invade suppression on ENG/USA at 1945.1/1945.6 in any of them; France never at zero after the landing). Note the item measured re-enterability only - `af003548` passed it while the western front sat frozen on two states for 18 months (posture front-local ratio, a different gate).

### Convoy-escort objectives are created by a country's OWN recent convoy losses - score terms rank them, they do not create them

- **Date:** 2026-08-15 (campaign `af003548`, checklist R36, Fix 86)
- **Symptom:** the USN ran 0% of its screens on convoy escort at three anchors across six campaigns with 22 pure-screen task forces parked, 14 idle admirals and full fuel, while ENG escorted 17-60% - and every naval `ai_strategy` that pushes escort (the -100 escort bar, corridor `naval_dominance`, no `naval_avoid_region` on the corridor) already reached the USA. Fix 53b had restored the vanilla escort SCORE terms with the note "escort no longer depends on this term" about `REGION_THREAT_PER_SUNK_CONVOY`.
- **Cause:** ENG's escort set is exactly its `per_region_danger` set (7 of 8 danger regions escorted, none without); the USA's `convoy_escort_presence_history` shows it escorted 48/69/243 while those regions carried danger and dropped each as danger decayed to 0. Vanilla's own comment on `CONVOY_DANGER_FOR_MAX_IMPORTANCE` says protection importance "will scale with convoy danger" - the objective exists only where the country's own convoys were sunk recently. The Kriegsmarine sinks British convoys, not American ones, so the USN has nothing to react to.
- **Rule:** never read "the score terms are non-zero" as "objectives will be generated". For any engine mission whose importance scales with an accumulated per-country signal (danger, threat), a country that does not accumulate the signal will not run the mission whatever the scores say. Diagnose from the engine-state block (`strategic_navy` → `per_region_danger`, `convoy_escort_presence_history`), not from the `ai_strategy` layer, and check whether WA overrode the decay/saturation of the signal (WA had `REGION_CONVOY_DANGER_DAILY_DECAY = 5`, vanilla 2, uncommented since 2020).
- **Detection:** one navy escorting exactly where it bleeds and another with the same script reach escorting nowhere; `presence_history` entries flipping to -1 as danger decays.
- **Evidence:** `af003548` 1944.6/1942.6 `strategic_navy` blocks for USA/ENG; R36 Fix-86 leg carries the pre-registered read.

### `free_building_slots` ignores a shared-slot building's own `state_max` - and a built-level check is not a queue check (Fix 81)

- **Date:** 2026-08-15 (community report on Discord, two cuts the same day)
- **Symptom:** `WA_AI_queue_AR` keeps picking the same top-scored state after it has 15 aluminium refineries queued; every later `add_building_construction` there silently no-ops, the state stays #1 in `WA_AI_shared_slot_scores`, and the type stops being built country-wide.
- **Cause:** `free_building_slots = { building = aluminium_refinery size > 0 }` reports the **shared** slot pool only; it never consults `level_cap.state_max` of the building itself (`common/buildings/00_buildings.txt`: REF 6, SR/HSR/AR/HAR 15). Refused adds do not consume shared slots, so nothing in the candidate filter ever changes. **Cut 1** added `<building> < cap` and was rejected by the reporter within the hour, correctly: the *built* level rises only when a refinery **finishes** (months, 10-12.5k IC), so a state stays under the cap on built level while its queue is already full, and every construction pulse in between keeps feeding it. The stall was shortened to "until the batch completes", not removed. **Cut 2** counted queued levels in a state variable reconciled from the rise in `building_level@X` - verified working on a local fork, but the reconcile only ran at C.10 pulses, so a state whose line finished between pulses read stale (GER 51: 7 > 6 for months, its lane sitting behind C.41's 1100-day `WA_AI_construction_timer`). **Cut 3** stores the SUM `WA_AI_committed_<X>` = built + queued, which a completion leaves unchanged, so nothing is reconciled on any cadence; the TTL flag remains for the cancellation case and `on_state_control_changed` clears it.
- **Rule:** (1) for any `shares_slots = yes` building with a `state_max`, the availability test must be `built + queued < state_max`; script cannot read the construction queue, so keep the count yourself at the add site - and keep it as the **sum** built + queued, which is invariant under completion, rather than a queued count that needs a completion hook the engine does not offer. (2) **Two states of one object are two variables** - queued vs built here; controlled vs owned vs core, flag vs variable elsewhere. Name them separately before reasoning. (3) **A claim that a residual is "bounded / self-healing / at most N" is not a claim until it comes with a t0/t1/t2 table at the real cadences** (pulse interval vs completion time). Cut 1 shipped on the sentence "bounded to one pulse"; the table would have shown pulse 2 at built 0 / queued 4. (4) When a reporter proposes a fix and you take another, quote their objection and write "mine covers it because ..." - if that sentence cannot be written, keep theirs.
- **Detection:** in saves, a state whose `<refinery>=` sits at the cap while the owner's per-type total stops rising with the matching resource still in EFFECTIVE deficit; on the cut-3 build, `wa_ai_committed_<x>` on states (checklist R49 leg 3: built <= committed <= cap while the TTL flag is live, committed - built = the state's live engine lines for that building).
- **Evidence:** `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` header (Fix 81), adders in `WA_AI_CONSTRUCTION_building_adders.txt` (timelines for completion / cancelled / unfunded in its header), flag reset in `WA_AI_misc_on_actions.txt` `on_state_control_changed`; cut 1 `7c4de2b53`, cut 2 `55dc64cd7`, cut 3 `68ce50c6b`. Cut 3's unconditional rebase on TTL lapse and the control-change reset were both raised by the `wa-lessons-reviewer` subagent on the cut-3 design (CONCERNS: upward-only rebase would have re-locked a cancelled state for another 1000 days per add). The `dummy` building (`common/buildings/dummy.txt`) exists for the same trigger's shared-pool semantics - it was already known to be fragile.

### "Empty" air-base capacity read from planes present is over-read - the save has no nominal wing size

- **Date:** 2026-08-16 (campaign `af003548`, R52 / R8 / R15)
- **Symptom:** an analysis pass concluded "the UK held 3 800-5 700 spare plane-slots at every post-D-Day save and the USAAF still did not rebase into them", i.e. capacity was not the binder. The modder's in-game observation is the opposite: a 50/100 wing fills 100 slots of a base - the engine books capacity per wing size, not per plane present.
- **Cause:** every wing block in a save carries exactly one strength number, `count=` (= Σ `equipment.amount`, 1 117/1 117 wings). The NOMINAL size is not stored on the wing but is fixed per plane type: the wing pool's `definition=` is the `sub_units` key of `common/units/air.txt`, and `land_air_wing_size` there is 100 for every type except tac_bomber 200, strat/heavy_strat 300, scout/maritime_patrol 25 (carrier 10). Verified on `1944.7_Jul`: 0 of 605 land wings exceed their type's size, and **7 of the 11 UK hosting states sit at exactly 100.0 % nominal** (Kent 1 200/1 200, Sussex 1 000/1 000, N. London 900/900, four fields at 800/800) while reading 86-98 % in planes present - the packing rule books capacity per wing size. Aggregate 90 % nominal / 77 % actual in the hosting states; the UK's structural ceiling (12 levels x 11 hosting states) cannot host RAF + USAAF at any measure.
- **Rule:** never conclude "capacity was not the constraint" from planes-present vs level × 100. Compute the NOMINAL load (Σ `land_air_wing_size(definition)` over the wings based in the state) - that is the engine-side load - and report actual beside it. Sizing decisions (UK hosting target, theatre air-base target) should be reasoned on wing slots, not on `num_deployed_planes_with_type` alone; the builders' plane-count deficit gate under-estimates need by the wings' fill gap.
- **Detection:** a base reading "X % empty" while the AI refuses to rebase wings into it; wings whose `count` is well below 100 clustering on those bases.
- **Evidence:** R52 opening paragraph corrected 2026-08-16; the `1944.7_Jul` census (79 wings / 8 196 planes / 10 600 capacity in the hosting states; 8 ENG heavy-bomber wings at 300 each, mean wing 102.3).

### A script-queued building on a saturated AI construction queue is not a build - measure `produced=`, not the add

- **Date:** 2026-08-16 (campaign `af003548`, 1941.9 -> 1942.6 local fork; checklist R48, retired)
- **Symptom:** the proactive synthetic-rubber lane finally fired for the USA (`prebuild_synth_n = 2`, adds on 1941.7 and 1941.9, rubber still positive) and nine months later the park was still 0 levels; the reactive branch's 1942.3 adds took until 1943.6 on the cloud path.
- **Cause:** `add_building_construction` (via `WA_AI_add_REF`) puts the entry into the country's VANILLA construction queue at whatever priority the engine gives it (32-50 here); a big AI economy keeps that queue full of its own mil/civ factories, so an 18 000-IC refinery sits at `produced = 49.7` for nine months. Every WA_AI counter upstream (trigger, dispatch, add) reads "success" while nothing gets built.
- **Rule:** any WA_AI construction that must actually happen goes through the priority-construction system (funded civs, sorted bands, lanes), never through a bare `add_building_construction` into the vanilla queue - and "queued" is never the verified effect; read the queue entry's `produced=` / the state's building level. Conversely, do not make WA_AI adds `prioritized` in a shared adder (`WA_AI_add_REF` has ~100 callers) - the PC is the priority mechanism.
- **Detection:** `production` section of the save: `building={ ... cost=18000 created_date=... produced=<tiny> priority=<30-50> }` entries months old; a `WA_TLM_*_n` counter climbing while `buildings TAG --match <type>` does not.
- **Evidence:** `ENG_1942_04_19_12.hoi4` / `ENG_1942_06_06_08.hoi4` USA production queue; `documentation/WA_SYNTHETIC_RUBBER_PREBUILD.md` §3.4e.

### A legacy gate without a recorded purpose outlives its reason — and a shared temp without a clear-on-read leaks it

- **Date:** 2026-08-16 (campaign `af003548`; Fix 90 / 90b, Fix 40, Fix 47)
- **Symptom:** the USA held 4-6 radar projects at every anchor and ENG 1-2 supply lines — the whole allowance of `WA_AI_PC_active_nonrail_projects < 5`, a gate wrapping the priority-construction dispatcher — while hundreds of civs sat idle. Nobody had touched the gate in three refactors of the queue (fixed 5-slot array → dynamic queue → Fix 41 bands → Fix 77/78 lanes) because no comment said what it protected. Earlier, Fix 40 found refinery projects running on a `_project_queue_max` of "3 from the two air strategies, 5 from the railway core, 0 from the railway helpers": the temp is chain-global and the refinery callers set `_project_queue_num` but never `_project_queue_max`, so each inherited whatever the previous caller left.
- **Cause:** the `< 5` gate was born with the pre-2026-01 engine, where *admitting* a project committed its 20 civs, so five projects = 100 civs = the whole budget; the dynamic queue made admission free (the fill decides funding) and the gate became a pure throttle on the count of non-rail projects — a fact that lived nowhere but in `git log`. The `_project_queue_max` leak is the same shape one level down: a shared temp whose *reason for being shared* (one dispatcher, one caller at a time) stopped being true when strategies multiplied.
- **Rule:** (1) every gate, cap, floor and shared temp carries a header sentence naming **what it protects, which engine/system fact it assumes, and how to tell that fact is gone**; when you meet one without it, do not delete it on sight (AGENTS.md principle 3) — reconstruct the purpose from `git log -S <name>`, write it down at the site, then decide, and if you keep it as a brake say so (`WA_AI_PC_can_afford_project`, Fix 90b: "kept only as a brake … do not add new readers"). (2) A chain-global temp is either an explicit input at **every** call site or latched-and-zeroed at the reader (Fix 47's `_project_queue_max_scoped` pattern); a comment names which. (3) Per-strategy budgets are explicit constants (`@AI_PC_QMAX_*`), not a shared count. The `wa-architecture-reviewer` subagent checks new gates and temps for the header sentence.
- **Detection:** in saves, one project family pinned at exactly the gate's allowance while `civs_avail` is large; in code, a `< N` on a system-wide counter with no `# Fix` or purpose comment; a `_project_*` temp read by a function that only some callers set.
- **Evidence:** `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` (`WA_AI_PC_can_afford_project` "LEGACY ADMISSION GATE" header, Fix 90b); `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_strategies.txt` (`@AI_PC_QMAX_*`, Fix 90; dispatcher comment "the per-strategy active_nonrail < 5 gate was removed by Fix 90"); Fix 40 header in `WA_AI_CONSTRUCTION_queue_functions.txt`; Fix 47 clear-on-read latch in `WA_AI_PC_start_project` (`WA_AI_CONSTRUCTION_PRIORITY_core.txt`).

### A "cheat" decision can be the only implementation of a behaviour — check what the honest path is gated on before deleting the cheat

- **Date:** 2026-08-16
- **Symptom:** After `8643389d5` removed the free-convoy decisions (`*_AI_cant_build_convoys`, `WA_convoy_fix`, `*_is_greedy`, six `sov_armor` events), a check for "does the AI have a convoy production system" found `WA_DEFAULT_production_convoy_strategy(_2,_3)` and stop blocks in `WA_AI_PRODUCTION_DEFAULT_navy.txt` (centralised there 2025-11-25, `e19aa66c1`) — and yet no AI country in any save had ever run a convoy line (`ENG_1942_06_06_08.hoi4`: GER 57 dockyards / 126 convoys / no line; ITA 38 dockyards / **0** convoys / no line).
- **Cause:** `common/units/equipment/convoys.txt` carried `can_be_produced = { is_ai = no }` on the `convoy` archetype AND on `convoy_1` since 2024-02-20 (`358e8be12`, message "ai"), which also deleted vanilla's `convoy_voy_voy_voy` and whose companion commits added the `_cant_build_convoys` decisions. The decisions were not a top-up on a working production path; they were the AI's *only* convoy source, and the later ai_strategy centralisation was written on top of a lock nobody re-checked. Compounding: `NDefines.NAI.MISSING_CONVOYS_BOOST_FACTOR = 0.0` (vanilla 50) in `05_defines.lua` since the initial commit, so the engine's own "I am short of convoys" reflex is off too, and the twelve majors listed in `wa_default.txt::default_unit_production.allowed` have no `unit_ratio convoy` at all.
- **Rule:** Before deleting an AI cheat (`add_equipment_to_stockpile`, `add_manpower`, free tech), find the honest path the AI is supposed to use instead **and check its gates end-to-end** — `can_be_produced`, `allowed`, `is_ai`, engine defines — not just that ai_strategy blocks exist. An `is_ai = no` on an equipment's `can_be_produced` is a silent production ban that no ai_strategy can override; grep `can_be_produced` under `common/units/equipment/` whenever an AI "never builds X". Symmetrically, when writing a production strategy for an archetype, prove in a save that a line exists before calling the system live.
- **Detection:** `savegame.py section <save> <TAG> production --grep <archetype>` empty across all AI majors while the min_factories strategy's enable conditions hold; the archetype's `can_be_produced` in `common/units/equipment/`.
- **Evidence:** Fix 91 (2026-08-16): gates removed from `convoys.txt`; convoy section of `WA_AI_PRODUCTION_DEFAULT_navy.txt` rewritten on `has_equipment` bands with a tier 0 / emergency tier; convoy leg added to `WA_AI_LEND_LEASE_request_surplus_relief`. Probe: campaign checklist R56.

### HOI4 1.18 script constants replace shared `@` copies - and where `constant:` does not reach

- **Date:** 2026-08-16 (in-game probe `events/wa_test_constants.txt`, in git history at commit 13eb2b9c6's parent tree; families 1-5 shipped 13eb2b9c6 / 39d28e0ec / 83dff4557 / next)
- **Symptom:** the morning's answer to file-scoped `@` drift was a registry + checker holding N copies equal. The same day the game's own `common/script_constants/documentation.md` ("All scoped variables can access script constants by using the `constant:` prefix") turned out to cover everything the AI code needs, so the copies could simply stop existing.
- **Cause / facts established by the probe (54 sondes, FALSE controls on every raw trigger):** `constant:cat.group.key` works in every variable context (`set_/check_/multiply_/divide_/add_to_/subtract_from_/clamp_temp_variable`, `set_variable` incl. `global.`, `add_to_temp_array`, `is_in_array`, either side of `check_variable`, `[?constant:…]` in a log), in the raw numeric triggers `num_of_civilian_factories` / `surrender_progress` / `num_of_controlled_states` / `has_army_size size >` / `has_deployed_air_force_size size >` / `has_manpower`, from scripted_effects / scripted_triggers / events, with `int` and `fixed_point` schemas, integer literals under `fixed_point`, negatives, one level of nested groups. It does **not** parse in `ai_strategy value =` ("Malformed token"). Inconclusive: `has_country_flag = { days > constant:… }` (probe design flaw); untested: `fighting_army_strength_ratio ratio >` (needs a war) - both keep `@`. Two engine traps: the constant database is reloaded separately from the scripts that read it (full restart, `reload` is not enough), and `common/script_constants` is a `replace_path` folder in `descriptor.mod` - the mod's file set replaces vanilla's (vanilla `state_groups.txt` / `propaganda_campaigns.txt` are dropped; nothing live in the mod reads them, but a future vanilla script that does will silently lose them).
- **Rule:** a number two files read is a script constant in `common/script_constants/wa_ai_<system>.txt`; a `@` is legal only while one file reads it; a `@` shared between two WA files is a checker ERROR (`SHARED-AT`); every key carries a `# was @OLD_NAME` line so history stays followable; the registry keeps only the cross-format copies (`05_defines.lua`, `00_buildings.txt`, `savegame.py`). Before using `constant:` in a context not in the validated table, re-run the probe (git history) rather than assume - the failure mode is a silent 0, not an error.
- **Detection:** `python tools/check_constants.py` (`SHARED-AT`, `UNRESOLVED`, `UNUSED-CONST`); in error.log, "Malformed token: constant:…" names an unsupported context.
- **Evidence:** `.claude/skills/wa-constants-registry/SKILL.md` (validated-context table), `common/script_constants/documentation.md`, `common/script_constants/wa_ai_pc.txt` / `wa_ai_railway.txt` / `wa_ai_aifc.txt` / `wa_ai_posture.txt`, game.log of the probe run 2026-08-16 07:03 (54 lines `WA_TEST_CONST`).

### "Fleet never below N" is not "not starving" — a convoy free pool of 0 is a real shortage; the tooltip's Use/Need is the measure, and it is not in the save

- **Date:** 2026-08-16 (campaign `a232d96c`, checklist R56 / Fix 91) — **supersedes, the same day, a retracted entry that called the Fix 91 gates a "free-pool latch".**
- **Symptom:** the first campaign with AI convoy production shows ENG on 4 lines / 50–57 dockyards (51–57 % of its yards) for 43 months, CAN 100 % of its yards, and `wa_tlm_nav_convoys` (= `num_equipment@convoy` = the free stockpile) at 0 on ENG for 46 consecutive months while its fleet (`convoys={ equipment={} }` in the country block) held 627–842 hulls. A first pass concluded "not starving, the gates read the wrong quantity, the floors latch and the stops are unreachable".
- **Cause of the misreading:** the fleet count says nothing without the NEED. The in-game tooltip at 1944.6.1 read **676 held / 676 used — trade 49 of 387 needed, supply 577, 0 unused**: ENG was short by ~350 convoys plus losses, trade ran at 13 % of demand, and its EFFECTIVE aluminium/rubber were −211 / −173. A free pool of 0 IS the shortage; `has_equipment = { convoy < N }` reading the free stockpile is the correct semantics; the floors are correctly ON and the stops (> 1 000 spare) correctly silent. The real Fix 91 findings are volume and lag: ENG's line opened ~11 months after the free pool crossed < 200, and 50–57 dockyards at 700 IC/convoy make ~130/yr against a 350+ hole — the price / a `unit_ratio convoy`, not the gates.
- **Rule:** never read a convoy fleet size (or any stockpile total) as health without the demand side. Use/Need is **not serialised**; the free pool (`wa_tlm_nav_convoys`) is the only save-side proxy and 0 there means short. When a probe result contradicts what the modder sees in game, the tooltip wins — re-derive the mechanism from it before writing a diagnosis. And do not retract a design's semantics ("the gate reads the wrong quantity") on the strength of a proxy you have not tied to the in-game figure.
- **Detection:** `wa_tlm_nav_convoys` at 0 for months on a trading major = starving; ask for (or resume and read) the convoy tooltip before scoring; ENG own-built hulls at 2 (1943.12) is the production-side confirmation.
- **Evidence:** checklist R56 history and Diagnosis bullet (`a232d96c`, retraction recorded there); user screenshot of the ENG convoy tooltip 1944.6.1; `WA_AI_PRODUCTION_DEFAULT_navy.txt` convoy section (Fix 91, `f99d52d74`).

### Re-adding an event family means re-adding its call site — grep for `country_event = { id = X }` before declaring it re-added

- **Date:** 2026-08-16 (campaign `a232d96c`; Mulberry re-add `9f7839647` / `eb19ebccd`)
- **Symptom:** the Mulberry harbour events were "re-added" after the cheat removal, and on the first campaign carrying them nothing Mulberry-shaped fired at D-Day (the beachhead sat at 2 states with unchanged infrastructure/naval-base levels for 24 months).
- **Cause:** the re-add restored three event *definitions* (`WA_AI_invasions.101` / `.102` and a sibling) but nothing schedules them — no `country_event = { id = WA_AI_invasions.101 }` exists anywhere in `common/` or `events/`. The old ids (`.84` / `.86`) had meanwhile been reused by an unrelated event family, so the historical callers point at different content. A definition with no caller is dead code that reads as shipped.
- **Rule:** re-adding an event, decision or scripted effect is two edits — the body **and** the caller — and the commit is not done until `grep -rn "id = <ns>.<n>"` (or the effect name) shows at least one live scheduling site outside the definition itself. When an id has been recycled since the original was deleted, allocate fresh ids and re-point the callers explicitly rather than trusting the old numbers.
- **Detection:** an event id that appears exactly once in the repo (its own definition); a `# Fix NN` re-add commit that touches only `events/`.
- **Evidence:** `events/WA_AI_invasions.txt` (`.101` / `.102`), `git log -S "WA_AI_invasions.84"`; checklist As-of 2026-08-16 defect (d).

### `infantry_equipment` and `heavy_infantry_equipment` are complementary archetypes - a relief leg per archetype, never a sum; and scripted relief needs land access

- **Date:** 2026-08-16 (campaign `a232d96c`, checklist R7b)
- **Symptom:** the lend-lease infantry-relief leg failed again — largest single GER-created rifle delivery to any Axis minor 1 130 (never the 6 000 base tier), ROM at ~0 rifles for 7 months with GER-created deliveries 0 — while GER's support leg fired constantly on the same pairs. GER "passed" the > 34 999 donor gate only at 1942.6 and 1945.6, the two windows in which no minor starved.
- **Cause:** `WA_AI_LEND_LEASE_*` reads `has_equipment = { infantry_equipment > N }`. In this mod a division needs BOTH `infantry_equipment` and `heavy_infantry_equipment` (`ger_hv_inf_*`, 17 646 -> 40 045 held by GER 1943-45) - the modder's ruling (2026-08-16) is that they are **complementary, not substitutes**. So the infantry leg is right to refuse (GER's `infantry_equipment` is 10-19 k, mostly booty - no surplus) and what is missing is a **separate heavy-infantry leg** with its own donor/recipient bars and its own `send_equipment` type. A first pass here proposed summing the two archetypes - wrong, retracted the same day.
- **Second ruling, same day:** the `send_equipment` relief system stands in for an overland truck convoy and must only fire between countries with **land access** (USA->ENG, USA->SOV, CAN->SOV must NOT use it; the engine's native lend-lease is the sea channel). Refined the same day: land access = a capital-to-capital state path crossing only allied or puppet territory (same landmass is NOT enough - Eurasia is one landmass). Candidate: the state-level A* `WA_AI_PATHFIND_get_path` with a new pathfind type (controller in {recipient, donor, subjects of either, faction/co-belligerent}) called from `WA_AI_LEND_LEASE_relief_pair_is_valid`, one call per starving recipient per weekly pull. The Fix 91 convoy relief leg is a sea transfer by construction and falls under the same rule.
- **Rule:** never merge two archetypes into one gate because they are both "rifles"; write one leg per archetype the recipient's templates actually consume, and check the donor's stock in THAT archetype before tuning a threshold that "never fires". And any scripted instant transfer must carry the geography the mechanism it imitates would need.
- **Detection:** a country holding tens of thousands of a category in the save (`equipments={}` registry, `archetype =`) while the gate's named archetype reads near 0 for it; a support/other leg on the same pair firing while the rifle leg does not.
- **Evidence:** checklist R7b history + Diagnosis bullet (`a232d96c`); F8 measurement correction 2026-08-12.

### The Soviet offensive has no live execute-order consumer once two legacy gates expire

- **Date:** 2026-08-16 (campaign `a232d96c`, checklist F5 / F3)
- **Symptom:** SOV `posture_vs_ger` = 1 at every anchor 1942.6 → 1946.6 (`post_exec_n` 3 145), 418 SOV divisions vs 198 GER on Soviet soil at 1946.6, eq ≥ 0.931 throughout — and the front moved +17 states in 42 months; RBL held the same 18 Soviet states at 1944.6 and 1946.6, Kiev still RUK-held, GER never fell.
- **Cause:** the posture verdict is published, but nothing consumes it for SOV: `WA_AI_MILITARY_FACTION_COMINTERN_FRONT.txt` carries only `front_unit_request` (the ALLIES / AXIS / CHINA exec/grind pairs are gated on faction membership SOV never has); SOV's own Country-layer exec blocks are gated on `ai_barb_timer` (a 140-day flag from the Barbarossa decision, expired ~1941.11) and on `coordinate_offensive` — a global flag read in 6 places and **set nowhere in the repo**; what remains is `WA_AI_MILITARY_SOV_balanced_plan` with `manual_attack = yes` and no `execute_order`. `af003548` (same files) still won the East by SOV alone, so the gap is necessary-not-sufficient — the differing factor (SOV 422 vs 489 divisions; SOV EFFECTIVE tungsten −220 / steel −114 from 1945.6 after the free-convoy events were removed; the removed USA→SOV scripted transfers) is unresolved.
- **Rule:** a posture verdict without a consumer at *some* layer is a gap, and every faction layer must carry an exec/grind pair or explicitly delegate to Default (AGENTS.md principle 1 — no behaviour that exists only on the historical path); a Country-layer gate on a timed flag or on a global flag must be paired with a grep proving the flag is set somewhere, and the setter named at the gate. When diagnosing "the front does not move" first list every `execute_order` block the country can reach and its gates, before touching equipment or supply.
- **Detection:** `posture_vs_<enemy> > 0` for years with `wa_tlm_post_exec_n` climbing and no state flips; `grep -rn "coordinate_offensive" common/ events/` returning only readers; `has_country_flag = ai_barb_timer` on a block meant to run past 1941.
- **Evidence:** checklist F5 history (`a232d96c`); `common/ai_strategy/WA_AI_MILITARY_FACTION_COMINTERN_FRONT.txt`, `WA_AI_MILITARY_COUNTRY_SOV*.txt`, `common/decisions/z_WA_ai_GER.txt` (`ai_barb_timer`).

### `strategic_air_importance` ranks regions; it does not create air demand — the USAAF follows US ground troops, not the ledger

- **Date:** 2026-08-16 (campaign `a232d96c`, checklist R15 / R8 / R52)
- **Symptom:** eight campaigns of "USAAF 62–85 % in CONUS, 0 planes in France, 79–94 % no-mission" while region 239 read +250k for the USA from 1944.2 (`Allies_dday_air` +200k, `WA_AI_MILITARY_DEFAULT_AIR_western_europe` +50k), UK fields at 57 % nominal load, and a continuous friendly airfield chain across the North Atlantic (Newfoundland → W. Greenland 2 → Iceland 1 → Shetland).
- **Cause:** every CONUS wing carries `mission={ type=0 }` with no `strategic_region=` — the engine never *requested* it anywhere. Plane demand comes from engine terms (own combats/armies in the region, enemy planes in a combat region, enemy factories for strategic bombing, ships); scripted importance only orders regions for the planes that ARE requested. Proof on the saves: 0 US divisions in France at 1944.6 → 673 USAAF planes in the UK; 70 divisions at 1944.9 → 1 682 UK + 172 France + 1 982 mid-transfer, all assigned to 239. GER shows the same law (1 000 idle in France on 1944.6.1, 3 689 executing over 239 at 1944.9); ENG too (3 094 idle in the UK at 1944.6, 2 800 executing at 1944.9). Not capacity, not range: the short-legged P-47/P-51 are the wings that DID reach the UK; the B-17s went to Sicily.
- **Rule:** never read a positive `strategic_air_importance` (or a "pre-arm") as "wings will move"; it moves only the marginal share the engine already wants (a8b29e09: 323–449 planes under +200k). To move an air force, move the ground force (or the enemy activity) that generates its demand; score air items on *planes executing over the theatre regions*, not on the state they are based in (UK bases cover 239 — ENG never needs France). Air-domain twin of the naval "score terms rank objectives, they do not create them" entry.
- **Detection:** wing `mission={ type=0 … }` / absent `strategic_region=` on the parked mass while the pulled region reads strongly positive; the parked pool being 100 % of one role; wing-level `active=yes` is a constant on every wing (1132/1132) and `mission={}` is never absent — neither can be a signal. Companion: `transferring_to=<STATE id>` + `transfer_cancelled=yes` at low `transfer_progress` on the outbound leg while the return leg completes = the reassignment flap (`d683fb022` raised `DAYS_BETWEEN_AIR_PRIORITIES_UPDATE` 2 → 5 against it).
- **Evidence:** checklist R15 RECUT 2026-08-16 (`a232d96c` 1943.6 / 1944.6 / 1944.9 / 1945.3); `common/ai_strategy/ENG.txt` `Allies_dday_air` / `Allies_dont_logi_strike_during_bob`; `common/defines/05_defines.lua` NAI air block (`LAND_COMBAT_*`, `LAND_COMBAT_GUIDE_DISTANCE = 0.0` vs vanilla 290, unrecorded purpose since 2023).

### meta_effect / meta_trigger do not see scripted-localisation lookups on the scope's variables — and a `has_equipment` meta_trigger with an invalid token evaluates TRUE

- **Date:** 2026-08-16 (boot tests `wa_test.300` / `wa_test.301` for the lend-lease relief redesign, `documentation/WA_AI_LEND_LEASE_RELIEF_DESIGN.md` §5)
- **Symptom:** rendering the equipment archetype token from a scripted localisation keyed on a country variable (`ARCH = "[GetWA_TEST_LLR_arch]"`) printed correctly in the `log` line but the `meta_effect` / `meta_trigger` render received the loc's fallback branch (`NONE`); error.log: `equipment type is not valid (memfile:1: has_equipment)`, `invalid database object for effect/trigger: NONE`. Meanwhile the effect's `if = { limit = { meta_trigger … has_equipment = { NONE > 0 } } }` took the TRUE branch.
- **Cause:** the meta render evaluates loc functions without the scope's variable context (temp or country), so any index→token mapping through scripted loc collapses to the fallback; and the engine treats a `has_equipment` whose type failed to parse as satisfied.
- **Rule:** in `meta_effect`/`meta_trigger`, only render NUMBERS and TAGS from variables (`[?_var]`, `[?_var.GetTag]` — proven by `wa_test.300`: `send_equipment = { type = <literal> amount = [AMT] target = [TGT] }` lands). Tokens (archetype names, building names, ideas) stay literals, one branch per token. Never trust a meta_trigger as a gate without a boot test that shows the FALSE branch too — an unparsable token gates nothing. Side trap: a loc value equal to an existing key (`infantry_equipment`) is re-localised to its display name ("Infantry Equipment") in log output.
- **Detection:** error.log `memfile:1` lines at the render timestamp; a log line printing the intended token while the effect has no visible result.
- **Evidence:** boot session 2026-08-16 09:35 (user's error.log excerpt); harness kept as `events/wa_events_test.txt` `wa_test.300` + `common/scripted_effects/WA_TEST_lend_lease_relief.txt`.

### An "Italy" is whoever owns and cores Italian soil — theatre rules that name the tag die at the flip, at the RIT release, and at the ITL annexation

- **Date:** 2026-08-17 (campaign `0edbc955`, checklist R61, Fix 96)
- **Symptom:** mainland Italy fell Oct–Dec 1943 to 7–12 Allied divisions with 0–3 Italian and 0–2 German divisions on it. ITA's 30 divisions sat in Libya / Sudan / Kenya (8 at Tripoli with no order at all) under three stacked `area_priority north_africa +200` (one gated `date > 1937.1.1`, one on any ITA/ITL-held Libyan state, one to 1941), the only home rule a `put_unit_buffers` gated `date > 1938`, and the "leave Africa" switch needing all four Libyan states lost. Germany's `fall_achse_a/b` armed on `GER_fall_achse_prepared` — the AI mission stamps it 60 days after `ita_armor.893` (1943.11.28 here, after Rome fell) and the blocks aborted on `has_war_with = ITA`, i.e. the day Germany needed to be in Italy; `protect_our_weak_underbelly` was gated on GER holding three FRENCH states; GER armies were handed "Northern Kenya / Mombasa / Khartoum" fronts because `GER_area_tilt` tilted only `north_africa`.
- **Cause (the general one):** every rule of the theatre asked "is this ITA / RIT / ITL, is it 1943, did the event fire" instead of "who owns this soil and is an enemy standing on it". The tag facts make that fatal by construction: on the AI path the pro-Allied Italy KEEPS `ITA` (`ita_armor.897` re-factions it in place), the fascist rump is a released `RIT` (`original_tag = RIT`, cores on all ITA cores), and `ITL` (Libya) is annexed the same tick — so `has_war_with = ITA` blocks die at the flip, `original_tag = ITA` never matches RIT, `is_controlled_by = ITL` lists go false in one day, and `is_in_faction_with = ITA` selects the wrong side of the war. `RSI` in this mod is Switzerland, `REP`/`ITF` are undefined tags scoped by the civil-war script.
- **Rule:** classify Italy by geography — `WA_AI_MILITARY_is_italian_homeland_power` (owns AND cores a mainland anchor state), `_italy_homeland_invaded`, `_italy_home_threatened`, `_ally_italy_theatre_*`, `_at_war_with_italian_homeland_power`, `_libya_bridgehead_held` — and write those triggers **PREV-relative from the state scope**, never `ROOT`, because the ally/enemy variants evaluate them inside `any_allied_country` / `any_enemy_country` / `country_trigger` where ROOT is the iterating country (`FIN_scripted_triggers.txt:183` for the `PREV.PREV` walk). "Threatened" must be LOST ground (enemy-held AND owned by the enquired country) or an occupied Tunisia whose controller is not its owner — a belt that counts Malta or French Corsica reads "threatened" from the day Italy declares war and switches the Africa effort off in June 1940. Gate Region-layer blocks in `enable`, not `allowed`: `allowed` is evaluated at country creation, before a released RIT owns a single state. Two tiers that must stack take two `order_id`s (~~same order_id = one pool~~ — refuted by savegame measurement 2026-08-17, campaign `7c7803a8`: blocks sharing an `order_id` still become separate orders; see the corrected `put_unit_buffers` entry. The two-`order_id`s habit is harmless, but it is not what makes the tiers stack, and `order_id` semantics remain unestablished). Home-territory `front_control` stays unconditional on posture (the calculus reads ~0 before the armies engage). **Post-code review of the same day added four more:** (a) the anchor set must include Sicily/south - the Fall Achse chain (`GER_fall_achse_preperation_ai` flags every ITA-controlled state, `ita_armor.897` transfers them all to GER) can leave the co-belligerent ITA owning nothing north of Naples, so a 10-state north/central anchor made it "not an Italy" in the historical shape; (b) walk `any_subject_country` beside `any_allied_country` - the RSI is `set_autonomy autonomy_reichskommissariat`, never `add_to_faction`; (c) an ally's port is a bridgehead only while an enemy holds the far shore, or the flip hands ENG's Libya to the co-belligerent as "its" bridgehead and the whole war-against-ENG family re-arms for the wrong side; (d) a legacy `date >` gate is not always "the Africa effort" - the INVASION/NAVAL twins of `ITA_focus_on_north_africa` carry invasion vetoes and sea-zone avoidance, and re-gating them on the bridgehead released them exactly when Italy was weakest (reverted).
- **Detection:** `tag = RIT` / `has_war_with = ITA` / `is_in_faction_with = ITA` / `is_controlled_by = ITL` in any Faction or Default file; a `put_unit_buffers` armed by a decision/mission flag; a `date >` on a theatre gate; an army given a front on a continent its country has no `area_priority` malus for.
- **Evidence:** checklist R61 (baseline `0edbc955`); `documentation/WA_AI_MILITARY_SYSTEM.md` §11; `events/wa_ita_events.txt` `ita_armor.893/.896/.897`, `common/decisions/GER.txt` `GER_fall_achse_preperation_ai` (timeout_effect byte-identical to complete_effect — a guaranteed success at J+60), `GER_reichskommissariat_italy` (`release = RIT`).

### `NOT = { A B C }` is a NOR — and East Africa was never a theatre because ITS was the only key

- **Date:** 2026-08-17 (campaign `0edbc955`, checklist R62, Fix 97)
- **Symptom:** the Allies never took Italian East Africa: ITA massed 39/61 divisions in Eritrea/Somaliland in 1940 (Italy had LOST the 1936 Ethiopian war — `ITA_defeat_in_ethiopia_flag`; ITS never existed; ETH neutral with 36-40 idle divisions), then camped two 8-division armies inside the Sudan/Kenya out of supply for three years and took Khartoum in 1943; the Allies never had more than one 4-6-division army per axis, UKT 0 divisions; AOI fell only with Italy's collapse.
- **Cause:** (a) every East-Africa rule on both sides keyed on `country_exists = ITS` / `tag = ITS` / `date <` — none fired without the tag; (b) region 17 sat in `WA_AI_MILITARY_sink_africa_regions`, so ENG's Default sinks summed ≈ −200 there; (c) regions 380/381 (Sudan-South, Kenya) were in NO ai_area — `area_priority` 0 against a baseline of 100, unreachable by any `area =` rule; (d) `ENG_africa_war_1` −100 delegated to a RAJ rule that was dated and ITS-gated; (e) nothing told Italy to `ignore` a neutral Ethiopia, so the engine's border-threat reflex garrisoned against 40 idle divisions.
- **Also learned, twice in one session:** `NOT = { A B C }` in PDXScript is a **NOR** (true iff none is true), not NOT(A∧B∧C). One agent read it as NAND and the misreading was repeated to the user before the lessons-reviewer corrected it: `ENG_africa_war_2_*` was `OR{450,663,451} ∧ NOT{450,663,451,…}` = X ∧ ¬X, dead since the Phase-6 split; `WA_AI_MILITARY_ENG_africa_hostile_presence`'s `NOT { tag=ROOT is_subject_of=ROOT is_in_faction_with=ROOT has_government=ROOT }` is a correct "controller is none of ours". Read every multi-child NOT as NOR before claiming a block is dead or live.
- **Rule:** a theatre exists in the map data before it exists in the AI: give it an ai_area only after auditing the global database budget (on HOI4 1.19.2, 72 total booted and 73 crashed in `ai_area.cpp`; see the dedicated lesson below), a `WA_AI_MILITARY_AIR_theatre_contested_<name>` trigger, and never let it live inside a "keep out" sink alias; key its rules on "an enemy at war holds ground there / our side has a foothold / we hold the colony", never on the tag of a puppet the script may never release. Where a Default sink must still keep a bloc out, name the theatre alias explicitly in that block so boost and brake see the same regions. Retire or merge an alias only after enumerating every reader and preserving theatre, corridor, order-buffer and sink semantics; an area read only by `front_unit_request` may be a candidate for an exact state-scoped geographic predicate, but its aggregation parity remains campaign evidence, not a structural claim.
- **Detection:** `country_exists = <puppet tag>` in a Faction gate; a strategic region that no ai_area lists (`area_priority` reads 0 there); a NOT with several children whose members overlap the OR beside it.
- **Evidence:** checklist R62 (baseline `0edbc955`); `documentation/WA_AI_MILITARY_SYSTEM.md` §12; `common/decisions/ITA.txt` `ITA_establish_ITS` (only creator of ITS); `events/Ethiopia.txt` `ETH_events.1` (Italy's defeat path).

### A scripted mission decides a war by named states - the AI must aim at THOSE states, and aiming is AIFC's job

- **Date:** 2026-08-17 (campaign `0edbc955`, checklist R63, Fix 98)
- **Symptom:** AI Italy lost the 1936 Ethiopian war (`ITA_defeat_in_ethiopia_flag` 1936.8.11) while winning 17:1 with 32 divisions in the AOI: `ETH_push_into_ethiopia_mission` (100 days from 1936.5.1) succeeds only if Italy controls BOTH 910 Amhara AND 909 Somali; the AIFC sector sat on 271 Addis (objectives {271, 909}) from March to August, the Somali armies drained 11 -> 2 divisions toward Oromia, 909 stayed Ethiopian, the timeout fired the scripted peace. The only execute block was `date < 1937.1.1` + rule in {DEFAULT, FASCIST_HISTORICAL}.
- **Cause:** (a) nothing told the AI which states the war is scored on - `front_control tag = ETH rush` executes the whole front, and the AIFC scorer (industry, VP, thin seams) naturally picks the capital; (b) the execute was gated on a calendar and a game-rule whitelist (FASCIST_ALTERNATE / RANDOM had none, nobody after 1938); (c) the theatre is the worst-supplied on the map (two level-1 one-province railways, no forward hub - by design, do not touch defines), so 100 days is only enough if every division goes to the right two states.
- **Rule:** when a script scores a war on named states, ship an `# aifc-tuning:` `force_concentration_target_weight` pair (+ on the mission states, - on the magnet the scorer would otherwise pick, same gate) plus `front_unit_request state =` pulls - `front_control state = X priority N` does NOT point the attack, it only selects which orders a mode applies to (documentation.info); a Country-layer execute must exist on EVERY rule option (a slow variant is a tuning, never the only path); check the AIFC sector arrays in the saves before blaming request/control types. First read the mission's own success test (`controls_state`, both states) and mirror it in the probe.
- **Detection:** `wa_ai_aifc_sector_anchor` on the capital while a mission names other states; a Country execute gated `has_game_rule` whitelist + `date <`; a scripted defeat flag set while casualties read a rout the other way.
- **Evidence:** checklist R63 (baseline `0edbc955`); `documentation/WA_AI_MILITARY_SYSTEM.md` §13; `common/decisions/ITA.txt` `ETH_push_into_ethiopia_mission`; `events/BBA_Italy.txt` `.1/.2`; `events/BBA_ItaloEthiopianWar.txt` (almost entirely unreachable code - buffs, maluses, volunteers, mediation).


### A theatre the AI can only reach by sea needs a destination it can be told about — a blob-level negative plus "no rule reads the landing" is an empty bridge

- **Date:** 2026-08-17 (campaign `0edbc955`, checklist R64, Fix 99)
- **Symptom:** Torch landed 1942.11.8, Case Anton (`GER.txt:2381`) handed Tunisia 458/1061/665 to Germany by the 1942.12 save, and **not one German division stood in Africa or Sicily/Sardinia in any save 1942.9 → 1943.6** (252-263 deployed); a single French division walked into Tunis by 1943.1, 17 Allied divisions followed. Italy (10-17 in Libya) had `Army 10` (4-6 div) with NO ORDER on all 10 saves and posture 0 vs ENG/USA/FRA; nobody's AIFC sector ever touched Tunisia; GER's convoy pool sat at 211-600 free — transport was never the constraint.
- **Cause (the general one):** the Axis land layer had no *destination* and no *sensor* for the landing. No block named 458/1061/665 as a target for GER or ITA; no Axis-readable trigger looked at Algeria/Morocco at all (only `WA_AI_MILITARY_AIR_theatre_contested_north_africa`, which moves planes); the only Germany-side terms on the theatre were coarse negatives on the 7-region `north_africa` blob (`war_with_soviets_2` −75 on `has_war_with = SOV`, `africa_is_lost` −100 on the vanilla-inherited `date > 1942.10.1` + Suez calendar) whose one positive twin was `NOT has_war_with = SOV`; and `libya_bridgehead_held` had no Tunisian term, so a Tunis-only foothold read "no bridgehead" and armed Italy's −200 abandon at the very moment the historical bridgehead existed. `area_priority`/`front_unit_request` on a blob that spans Morocco→Egypt cannot say "hold Tunis"; a `date >` on "Africa is lost" fires five weeks before the landing it is supposed to follow.
- **Rule:** an overseas theatre the AI must *hold* gets (a) a state-keyed `put_unit_buffers` on the ports it must keep, with its own `order_id` and an `area` alias limited to that theatre's region (Fix 97 pattern) so neighbouring offensives may not draw on it, plus (b) a region-keyed `front_unit_request` sized to offset the country's blob-level negatives on that front only, and (c) a gate that reads the *landing* (an enemy controlling the anchor states of the neighbouring region) and *our port* — controller geography, one "our side" definition = self / subject / faction ally / `has_war_together_with` (the last term is what makes a subject of an ally count — ITL for GER; Fix 27 lesson). "The theatre is lost" is "our side holds no port on that shore", never a date. When a shared bridgehead trigger is widened, add a **sibling** (`african_shore_port_held`) and re-point each consumer as an explicit decision — a buffer that sits on Libyan states still needs the Libyan gate; a "keep the effort alive" pull needs the wider one.
- **Detection:** a Faction/Country file with several negatives on a multi-region ai_area and no state- or region-keyed positive inside it; a `date >` gating an "X is lost" veto; a bridgehead trigger whose port list omits the ports the enemy actually contests; a landing (`spawn_invasion`, engine invasion) that no trigger of the *defending* side reads; `savegame.py army <TAG>` reading 0 divisions on a continent the tag owns states on.
- **Evidence:** checklist R64 (baseline `0edbc955`); `documentation/WA_AI_MILITARY_SYSTEM.md` §14; `common/scripted_triggers/WA_AI_MILITARY_triggers.txt` Fix 99 section; `common/ai_strategy/WA_AI_MILITARY_FACTION_AXIS_THEATRE.txt` `AXIS_tunis_bridge_THEATRE` (bounded-claim table + the sea-lift hypothesis R64 leg 1 falsifies).

### A logistics reserve is a function of network scale — one absolute convoy threshold cannot serve South Africa and Britain

- **Date:** 2026-08-19 (campaign `2f8cbd51`, checklist R56 recut)
- **Symptom:** ENG held 0 free convoys and no convoy line in 1942.12 / 1943.1 / 1943.2 despite 100 owned dockyards, while USA held 1,412 / 1,507 / 1,592 free and sent none. A flat 200-free recipient target would treat a small coastal power and the British oceanic network as equally healthy.
- **Cause:** an absolute reserve encodes no proxy for the scale of trade, supply and overseas commitments. Save-side Use/Need is unavailable, but dockyard count is observable in script and separates small from oceanic naval economies. The separate problem in production was volume: the 12 countries excluded from `wa_default.txt` also lost the only explicit `unit_ratio convoy`.
- **Rule:** scale convoy recipient reserve and weekly relief cap from a shared naval-capacity band, but apply a separate major-power floor because a continental major can run a worldwide lend-lease network with few dockyards; give the donor its own lower floor. Never reuse the recipient target as the donor floor or a rich donor just above its own target can transfer almost nothing. Keep all bands and floors in script constants and read them from production, pair gates and transfer amounts. A scripted convoy transfer is a maritime system of its own and must never be routed through the Fix-92 land A* for the nine land-equipment cargos. Prove the bound at the actual weekly cadence with donor headroom and recipient gap, not with an adjective.
- **Detection:** a major with few dockyards (SOV: 22 in 1943.1) gets the same 200/500 target as a minor; an oceanic major at 0 free hulls while an allied 81+ dockyard country holds >1,000 free; the major has no `unit_ratio convoy`; or a transfer computes `donor stock - recipient reserve` instead of `donor stock - donor floor`.
- **Evidence:** checklist R56 history (`2f8cbd51`); `documentation/WA_AI_LEND_LEASE_RELIEF_DESIGN.md` maritime extension; `common/script_constants/wa_ai_lend_lease.txt` convoy row.

### Count the whole `ai_area` database before adding an alias — 73 crashes HOI4 1.19.2

- **Date:** 2026-08-17
- **Symptom:** commit `1b437e397ff74bbd1477be82bdf7501978ec96f9` crashed at startup with access violation C0000005 in `ai_area.cpp`; `setup.log` stopped while loading AI strategies and the script logs contained no relevant parse error. Its parent booted.
- **Cause:** HOI4 1.19.2 has an observed effective ceiling of 72 definitions in the global `common/ai_areas` database. The replaced `default.txt` contributes 67 and the parent had 4 WA aliases (71 total). Either newly added alias alone produced 72 and booted; both produced 73 and crashed. A sixth WA alias still crashed when renamed, given disjoint regions, or pointed at another valid region, excluding the alias name, contents, overlap and consumers as causes. Final remediation removed the unreferenced India alias, replaced the exact `{21,23}` Italy duplicate with vanilla `italy`, and converted all nine `front_unit_request` readers of the former Southeast-Asia sink area to one state-scoped predicate over the exact regions `{142,167,196,260,340}`. That freed the slot for the `{380,381}` corridor baseline alias: 5 WA aliases / 72 total, with the active East-Africa theatre, corridor, colony buffer, Tunis buffer and Africa sink all preserved.
- **Rule:** before adding or restoring an `ai_area`, count every top-level definition across the complete replaced folder, not just the edited file. On HOI4 1.19.2 keep the total at 72 or below, then boot-test the exact final database. Treat 72 as version-scoped engine evidence, not a timeless format rule: after an engine upgrade, re-run a 72/73 boundary pair. Never free a slot by deleting or merging an alias until every reader has been enumerated and the retained mapping preserves its theatre, corridor, order-buffer and sink semantics.
- **Evidence:** controlled boot matrix on 2026-08-17: 67 default + 4 WA = 71 booted; + either new alias = 72 booted; + both = 73 crashed; removing the unused India alias from current HEAD left 7 WA / 74 total and reproduced the same C0000005 at address `0x00007FF768DA17DD`; the completed remediation at 5 WA / 72 total passed AI-strategy loading and reached on-action loading with the process alive, no related `error.log` entry and no new crash report. Disabling all changed `ai_strategy` files, `WA_TLM_core`, or `WA_AI_MILITARY_triggers` still crashed at 73+; disabling `WA_AI_MILITARY_areas.txt` passed strategy loading. BOM, brace and constants checks passed. Crash dump resolves to `ai_area.cpp`. The strict state-scope bundle is authored but not yet run; its aggregation outcome remains R62 campaign evidence.

### Two order fields in savegames are not signals: `enemy_power = 0` is structural, and `starting_date = "1.1.1.1"` does not mean "never executed"

- **Date:** 2026-08-17 (campaign `7c7803a8`, the same measurement that corrected the `put_unit_buffers` `order_id` entry above)
- **Symptom:** while auditing `order_instance` blocks, two fields read like ready-made verdicts — every non-front order showed `enemy_power = 0` ("the AI sees no threat there"), and garrison/invasion orders showed `starting_date = "1.1.1.1"` ("this order never ran"). Both readings are wrong, and both are the kind that get repeated into a checklist before anyone samples the population.
- **Cause:** (a) `enemy_power` is 0 on 1175 of 1175 sampled orders, across every `type` and every country — it is a constant of the serialization for these order kinds, so it carries no information at all; a field that never varies cannot be a signal. (b) `starting_date` is written on execution and the execution window is *hours*, while the observer saves are day-1 monthly — Operation Torch's own orders still read `1.1.1.1` in the save taken seven days before the landing. Absence of a start date is therefore mostly a sampling artefact.
- **Rule:** before reading any savegame field as evidence, check that it *varies* over the population you sampled — a value that is constant on 1175/1175 rows is structure, not signal (same shape as the wing-level `active=yes` on 1132/1132 in the `strategic_air_importance` entry). For "did this order ever execute", the usable signature is order **disappearance** between consecutive saves plus `can_execute = 1`, which is present on 210/210 started and 0/699 unstarted orders; never infer "never executed" from `starting_date = "1.1.1.1"` in a monthly-cadence save series, because the event you are looking for is shorter than the sampling interval.
- **Detection:** you are about to write "the AI never X" from a single field on a single save; count distinct values of that field across the whole sample first, and compare the field's write cadence against the save cadence.
- **Evidence:** campaign `game_unique_id = 7c7803a8-21f7-47df-99da-f82d3e3bd6c3` (`world-ablaze-beta`, HOI4 1.19.2, observer `player=BHU`), saves `1941.6_Jun.hoi4` / `1943.11_Nov.hoi4` / `1944.6_Jun.hoi4`; orders read at `countries/<TAG>/theatres/theatre/{orders_group|field_marshal_group}/order_instance`.

## `common/ai_strategy/documentation.info` is the TOKEN oracle, not the EXAMPLE list — grep the token list before concluding "no script lever exists"

- **Symptom:** an investigation into why no Allied minor ever sends an expeditionary force concluded, in writing and to two reviewers, that "no other lever exists — the engine's ai_strategy token list has no expeditionary type", and moved on to retuning three `NDefines.NAI` values instead. The user produced a wiki screenshot of the `support` type: *"Pursues AI to support a certain country within wars, sending lend lease, volunteers, or **expeditionary forces**."*
- **Cause:** `common/ai_strategy/documentation.info` has two halves that are easy to conflate. Lines 6–105 are a bare **token list**, one name per comment line, no descriptions. Lines 190+ are **worked examples**, one commented `ai_strategy = { … }` block per interesting type. `support` appears in the first half (line 29) and **has no worked example**, like roughly half the tokens. The investigation printed the whole token list, scanned it for the word "expedition", found nothing — because the token is named `support`, not `expeditionary` — and then treated the absence of an example as the absence of a feature.
- **Rule:** the token list is the authority on **what exists**; the examples are only the authority on **how to write it**. A type with no example is not a type that does nothing. Before writing "there is no script lever for X", read the ~90 token names and ask what each one *could* mean for X — and if a name is generic (`support`, `befriend`, `influence`), look it up externally rather than inferring from the local file.
- **Detection:** you are about to justify a `05_defines.lua` change with "the defines are the only lever". That sentence is the trigger to re-read the token list. Corollary: a defines change to reach a behaviour that a strategy type also reaches is almost always the wrong instrument — the type is per-country and gated, the define is global.
- **Second-order lesson from the same near-miss:** the fix that replaced the defines change is *still* only a hypothesis, because the positive control contradicts it. On campaign `7c7803a8` the three countries that actually lent divisions (SIK→SOV, ITL→ITA, BUL→ROM) carry **no `support` block at all**, so lending demonstrably happens at support value 0. Finding the right lever is not the same as proving it is the cause; the campaign item (checklist R70) branches on the engine's own serialised verdict (`ai/expeditionary_force_data`) for exactly that reason.
- **Evidence:** campaign `game_unique_id = 7c7803a8-21f7-47df-99da-f82d3e3bd6c3`, 2026-08-17. 56 `support` blocks already in the mod, none of them Allied-minor → major; the engine's expeditionary decision block absent on all seven Allied minors at every sampled date. Fix 106; `common/ai_strategy/documentation.info token list, Related to diplomacy` (token) vs `:190+` (examples).


## An unset temp variable does not read as 0 — it reads as a scope token, and a `while_loop_effect` guarded on one never runs

- **Date:** 2026-08-19 (campaign `07270b64`, boot probe `wa_test.301`)
- **Symptom:** the state-level A* `WA_AI_PATHFIND_get_path` returned "no path" for **every** caller, every type, for a whole campaign. Lend-lease relief (type 3): `wa_tlm_llr_donor_selected_n` equals `wa_tlm_llr_path_refused_n` **exactly** on all 94 recipients that ever picked a donor — roughly 30,000 calls, 0 successes in ten in-game years, continental neighbours included. Supply lines (type 1), a different consumer with its own counters: `WA_AI_supply_line_dbg_called` 1,814 across ITL/ITA/ENG/JAP/GER/UKE, `WA_AI_supply_line_dbg_pf_ok` **0**.
- **Cause:** the A*'s iteration counter `its` was zeroed only at the **END** of `WA_AI_PATHFIND_get_path`, so the first call in any effect execution entered `while_loop_effect = { ... limit = { check_variable = { its < 75 } ... } }` with `its` never set. Reading it did not yield 0: the boot probe printed `iterations = 10792.02889` — a scope token in the same magnitude family as the state references beside it (`_pathfind_start = -10737.41778` decodes as signed `0xC0000000 | 46` = state 46, Bucharest). Anything of that size fails `< 75`, so the loop exited **before its first iteration** and the effect reported failure without ever looking at the map. Both live consumers call the pathfinder once per pulse, so in practice *every* call was a first call.
- **Rule:** initialise every temp a loop guard reads at the **entry** of the effect that owns the loop, never only at the exit — an exit-only reset protects the second call and leaves the first one reading whatever the engine hands back. Treat "unset temp" as *undefined*, not as zero. This file already carried the same lesson one variable over: the Fix 30 "break hygiene" block zeroes `break` and `pathfind_success` at entry for exactly this reason, and `its` was simply missed.
- **Detection:** a loop-bounded effect whose success counter is 0 across a whole campaign while its call counter is large — the pair `dbg_called` / `dbg_pf_ok` is what made this visible without a boot test. In code: a `set_temp_variable = { x = 0 }` that appears only after the loop it guards. Also, print the counter in the effect's own END log line; `iterations = <a number with five decimals and six digits before the point>` is a scope reference, not a count.
- **Second-order lesson:** the first hypothesis for the same evidence was that temp variables are scope-owned, so a temp written inside `ROOT = { }` would read 0 in the donor's scope. The campaign's own counters refuted it (`llr_send_failed_n` = 5,924 on the USA is only reachable if those ROOT-written temps ARE visible), and the boot probe then confirmed sharing in one line: a temp set inside `ROOT = { }` read back **4242** in the donor scope. Two different variables, two opposite failure modes, one symptom — the cheap in-game probe separated them, three rounds of code reading did not.
- **Verified in game 2026-08-19:** after the entry init, the same probe prints `counter after init = 0`, `PATHFIND: found path, end = E. Berlin`, `iterations = 16`, `path_ok = 1` on the pair that had refused twice. The counter was also renamed off the bare `its` to `_pathfind_its`: the temp pool is shared across scopes for the whole execution (probe: 4242), so a generic name in a shared pool is a collision waiting to happen.
- **Evidence:** `common/scripted_effects/WA_AI_pathfinding_effects.txt` (entry init beside the Fix 30 block); probe `wa_test.301` + `WA_TEST_LLR_probe_scope` / `_probe_legs` in `common/scripted_effects/WA_TEST_lend_lease_relief.txt`; campaign `07270b64`, checklist R7b / R56.


## `send_equipment` does not move convoys - vanilla and Expert AI never ask it to

- **Date:** 2026-08-19 (boot probe `wa_test.301`, campaign `07270b64`)
- **Symptom:** the maritime convoy relief leg reached `send_equipment` on every weekly pulse for ten in-game years - `wa_tlm_llr_send_failed_n` 5,924 on the USA, 1,834 on ENG - and not one convoy hull ever moved: no foreign-created hull in any starving Ally's `convoys={}` block on any save, `wa_tlm_llr_sent_n^10` = 0 everywhere.
- **Cause:** `send_equipment` simply does not carry convoys. The probe sent 50 as the `convoy_1` variant and 50 as the `convoy` archetype, in the SAME effect execution in which the infantry leg moved 12,000 rifles through the identical code shape (same scope, same meta render, same target): both convoy rows left the recipient at 0, the rifle row landed and was verified. No error, no log line, no engine complaint.
- **Rule:** move convoys with a **pair of `add_equipment_to_stockpile`** - negative in the donor's scope, positive in the recipient's with `producer = <donor>`. That is what vanilla does in every single case: across 1,575 vanilla and 580 Expert AI equipment-transfer blocks, **zero** `send_equipment` carries a convoy, while all 123 convoy movements use the pair (`AST_diplomatic_events.7/8` -50/+50, `MEX.txt`, `POR.txt`, `NOR.txt`, `SEA_Philippines.txt`). The pair is create-and-destroy rather than a transfer, so the two halves must stay together in one effect. `amount` accepts a variable, so no `meta_effect` is needed at all.
- **First wrong answer, recorded because it was plausible:** the leg sent the `convoy_1` VARIANT while every land leg sends an archetype (`convoy` carries `is_archetype = yes`), and `num_equipment@convoy` - what the whole convoy family reads - is the archetype too. The token disagreement was real and worth fixing, but it was not the cause: the archetype spelling failed identically. A code smell that explains the symptom is not the same as the cause.
- **Detection:** a send whose verify (`stock after > stock before`) fails 100 % of the time while a sibling send in the same execution succeeds. Run the sibling as a positive control in the same effect before theorising - it clears scope, amount, target and render in one line each. Then check what vanilla does with that cargo: `grep` the base game for the effect and the equipment together, and count how often the combination occurs. Zero occurrences in 2,155 blocks is an answer.
- **Corollary settled by the same run:** `TGT = "[ROOT.GetTag]"` inside `meta_effect` renders correctly, and `num_equipment@<arch>` DOES reflect an equipment transfer made earlier in the same effect execution (recipient -1 -> 11,999) - so the read-back verify in `WA_AI_LEND_LEASE_relief_record` is sound and `llr_send_failed_n` is a real failure count.
- **Evidence:** `common/scripted_effects/WA_AI_lend_lease_effects.txt` (`WA_AI_LEND_LEASE_relief_leg_convoy`); `common/units/equipment/convoys.txt`; `WA_TEST_LLR_probe_convoy_token` keeps the A/B as a negative control beside a rifle positive control.


## Temp variables live in one pool shared by every scope of an effect execution - address them by BARE name, never with a scope prefix

- **Date:** 2026-08-19 (boot probes `wa_test.301`, `WA_TEST_LLR_probe_scope`)
- **Symptom, first half:** a diagnosis concluded that `ROOT = { set_temp_variable = { x = ... } }` writes on the recipient and is invisible to the donor's scope, and blamed a whole dead subsystem on it. **Wrong.** The probe writes 4242 inside `ROOT = { }` and reads it back, unprefixed, in the donor's scope: it prints 4242. The campaign's own counters had already refuted the theory (`llr_send_failed_n` = 5,924 is unreachable if those temps read 0), which is why the probe was written before the "fix" was shipped.
- **Symptom, second half:** the opposite mistake, made the same day in the replacement code. `ROOT = { add_equipment_to_stockpile = { type = convoy amount = PREV._llr_amount producer = PREV } }` rendered in the effect tooltip as *"0 units of German Convoy Ships is removed"* - `producer = PREV` resolved correctly (the tooltip says "German"), the amount resolved to nothing. The pair's positive half moved zero hulls while its negative half removed 100 from the donor.
- **Cause:** temps are not stored on the scope object. They live in one pool for the duration of the effect execution, reachable from every scope by bare name. A scope prefix asks the engine for a variable held BY that scope object, which for a temp is nothing - so the read silently returns 0 rather than erroring.
- **Rule:** inside a nested scope, write and read temps by **bare name**. Use a scope prefix only for genuinely scope-owned things: persistent country/state variables (`ROOT.WA_AI_PC_queue`), dynamic variables (`ROOT.num_equipment@infantry_equipment`), and effect parameters that take a scope (`producer = PREV`, `target = ROOT`). Corollary: because the pool is shared and flat, a generic temp name is a collision across systems - prefix names by owner (`_llr_`, `_pathfind_`, `_project_`), which is also why the A* counter was renamed off the bare `its`.
- **Detection:** preview the effect tooltip before trusting an `amount`/`value` that came from a variable - a `0 units` in the tooltip is the whole bug, visible without a single log line. In code: any `SCOPE._something` where `_something` is a temp.
- **Evidence:** `common/scripted_effects/WA_AI_lend_lease_effects.txt` (`WA_AI_LEND_LEASE_relief_leg_convoy`); `WA_TEST_LLR_probe_scope`; vanilla writes prefixed temps in `common/scripted_effects/00_scripted_effects.txt:461/477`, which this entry does NOT vouch for - only the prefixed READ was measured.


## A probe that does not print the context it ran in produces confident nonsense - and six rounds of it

- **Date:** 2026-08-19 (boot probe `wa_test.302`, campaign `07270b64`)
- **Symptom:** a bisection harness returned, for byte-identical code on the same save at the same in-game time: `matched=1` on eleven nesting depths in six consecutive runs, then `matched=0` on the first three depths and `raw=0` on the rest, then `matched=1` everywhere again. Inside the real pathfinder the same predicate read false six different ways at once - `tag = ROOT`, `is_controlled_by = ROOT`, `is_owned_by = ROOT`, a literal tag, a variable holding ROOT's id, faction and co-belligerency - on a state whose controller printed as ROOT's own tag in the same log line, while `always = yes` read true. That combination is not physically possible and should have been read as "the instrument is lying", not as an engine mystery.
- **Cause:** the event was fired with a different country in scope on some runs, so `ROOT` was not the country the predicates were asking about, and `random_other_country` could not pick the donor. The harness printed none of that. Two full hypotheses were built and shipped on those readings - that `is_controlled_by = ROOT` was a broken idiom the file's own Fix 30 comment had already condemned, and that the loc scope and the script scope had diverged - and both are false: with a correct context every form measures TRUE, including the one that was "fixed".
- **Rule:** a probe prints the context it ran in, FIRST, on every run - who is THIS, who is ROOT, which scope the iteration starts from, and whether each `random_*` pick actually found anything. Quote that line beside any figure taken from the probe; a reading without it is not a measurement. And when several independent predicates disagree with a value printed beside them, suspect the harness before the engine - the engine is rarely six-ways inconsistent inside one log line.
- **Detection:** the same input producing different output across runs. Cheap to catch and impossible to catch without a header, which is exactly why it cost six rounds here.
- **What survived unchanged:** the symptom under investigation (`0 neighbours` inside the real A*) was stable across every run. Only the bench was not. A stable symptom beside an unstable bench is the signature of this failure.
- **Evidence:** `common/scripted_effects/WA_TEST_lend_lease_relief.txt` (`WA_TEST_PF_header` and the depth ladder); the retracted hypothesis is recorded in the type-3 branch comment of `WA_AI_pathfinding_effects.txt`.


## An `ai_strategy` block that is silently OFF looks exactly like a block that does nothing - check the gate before blaming the payload

- **Date:** 2026-08-19 (campaign `07270b64`, save 1943.8; Fix 108 / 109 / 110)
- **Symptom:** AI Italy held garrisons on the Adriatic coast with the Otranto strait shut, and none at all on the Provence coast (Toulon, Marseille). Both readings look like a payload problem - a missing state in a `states` list, a ratio too small, a wrong `area`.
- **Cause:** neither. (a) The Adriatic garrisons were **not WA's at all** - they were engine-generated area-defence orders (`order_instance` type 5 with `area_defense_settings = 100`; WA's own scripted buffers carry `102`). The engine was free to make them because `WA_AI_MILITARY_ITA_war_against_ENG_FRONT`, which carries Italy's only `garrison = -5000`, had been **disabled since 1941.2.7**: its gate was `NOT = { has_war_with = ETH }`, carried verbatim from the pre-convention import, and Ethiopia was liberated in Feb 1941 and stayed at war as a co-belligerent. Two sibling blocks split from the same original (`_DIPLOMACY` `force_defend_ally_borders`, NAVAL `strategic_air_importance` over the Italian war theatre) died with it. (b) Provence *was* in a WA `states` list - the order existed and held six divisions - but the list mixed three coastal states with six landlocked ones at a flat ratio, and the engine spread one division per state into the interior, leaving the only landable state empty.
- **Rule:** before concluding anything about an `ai_strategy` payload, establish that the block is **enabled at the date you are measuring**. Two cheap checks settle it: read the `enable` chain against the save (`relations`, `control`, `flags`) rather than against the historical script, and split the save's orders by `area_defense_settings` so an engine order is never read as a scripted one. A gate that names a *country* (`has_war_with = ETH`) as a proxy for an *era* ("the colonial war is over") inverts permanently the first time that country comes back into the war - the mod already had the era trigger (`WA_AI_MILITARY_ethiopian_war_finished`) and five sibling blocks were using it.
- **Detection:** an `ai_strategy` family whose effect is absent from every save after some date, with no code change at that date. Grep the family's gate for a tag-named proxy; `git log -S` it - a clause with no recoverable reason and a modern trigger covering the same question is the shape.
- **What this entry does NOT claim:** that `garrison = -5000` removes engine area-defence orders. That is WA convention, undocumented by the engine, and the save measured here only shows what happens when the block is OFF. Checklist R74 leg 1 is the first measurement of the ON case - do not quote a magnitude for it until that scores. **Answered 2026-08-27:** the ON case is now MEASURED — see "A negative `garrison` does NOT empty existing area-defence orders" (end of log): the value reaches the engine, summed at -4950, and existing areadef orders keep their divisions.
- **Evidence:** `plans.py ITA 1943.8_Aug.hoi4 --oob/--where/--armies` (16 of 106 divisions in five `ads=100` orders; Army 6 = 6 divisions over five inland French states, Provence 0); `savegame.py relations 1943.8_Aug.hoi4 --tag ITA` (`ETH … since 1941.2.7.1 recorded in ETH's block ONLY`); `savegame.py control 21,20,22,735` (Provence/Rhone/Languedoc = GER); `git show 79d64f6ff:common/ai_strategy/ITA.txt` for the original gate.


## Two call sites, one effect - a scripted effect's country-valued triggers can ALL read false depending on which event file fired it

- **Date:** 2026-08-20 (live campaign save 1940.5, running as GER - same save, same tick, same session for both readings)
- **Symptom:** `WA_TEST_CA_report` fired by `wa_test.310` (then homed in `events/wa_events_test.txt`): the report's own scope self-check printed `always=1 I-am-ROOT=0 I-am-THIS=0 ROOT-scope-usable=1`, and EVERY trigger taking a country on its right read false - `tag = GER` (a LITERAL tag, while playing GER), `tag = ROOT`, `tag = THIS`, `original_tag = ROOT`, `has_war_with = ROOT`, `is_in_faction_with = ROOT`, `is_subject_of = ROOT`, `is_owned_by = ROOT` - while every value/property trigger beside them read true (`always`, `is_major`, `has_equipment`, `num_of_*_factories`, `exists`). The coalition walk matched nobody and the gauge printed a plausible-looking `0.000`. The SAME effect, byte-identical, fired by `wa_iso.3` from `events/wa_test_scope_isolation.txt`: `always=1 I-am-ROOT=1 I-am-THIS=1`, and the correct answer - `coalition_sea_share = 0.000 (unreachable 0 of 706 factories)`, side = German Reich 689 self, Slovak State 2 overland, Protektorat Bohmen und Mahren 8 overland, Danish State 7 overland.
- **Cause: UNKNOWN.** Everything textual was cleared before concluding that: error.log said "no errors"; both files BOM-free; every top-level definition in both files starts and ends at brace depth 0 with no stray file-level tokens; `wa_test.310` defined exactly once; `add_namespace = wa_test` declared in exactly one file; the two events structurally identical (`country_event`, `hidden`, `is_triggered_only`, `immediate = { <effect> = yes }`, empty option). The engine was proven fine in the same session (`wa_iso.1`: literal and scoped tags, `has_war_with`, `every_country` over 107 countries all correct in a clean event immediate) and the scripted-effect indirection was proven innocent (`wa_iso.2`). The only remaining variable was the event FILE that fired the effect, and no textual difference explains it. **This is the same failure FAMILY as "A probe that does not print the context it ran in produces confident nonsense" (2026-08-19) but NOT the same cause, and that was checked before writing UNKNOWN:** that entry's cause was the event firing with a different country in scope, which cannot produce this signature - here `tag = THIS` read false beside `always = yes` true, and THIS is the executing scope itself, so no wrong-country-in-scope explains it; the country-valued trigger FAMILY failed as a family, on literal right-hand sides included, while the loc tokens printed the right country throughout.
- **Rule:** when a scripted effect's country-valued triggers all read false while its value triggers read true, the effect is NOT the suspect - fire it, unmodified, from a different event file BEFORE touching a line of it. And a harness whose readings depend on which file fired it gets REHOMED, not debugged: the convoy-arsenal harness now lives in its own `events/wa_test_convoy_arsenal.txt` (`wa_ca` namespace) for exactly this reason, cause still unknown.
- **Detection:** a scope self-check at the top of the effect, printed on EVERY run, asserting the country under test matches its own `tag = ROOT` (the `who:` / `scope:` lines of `WA_TEST_CA_report`). `I-am-ROOT=0` beside `always=1` is the whole signature. Loc tokens CANNOT detect it - `[Root.GetName]` printed the right name through the entire failure. The reusable clean call site is `events/wa_test_scope_isolation.txt` (`wa_iso.1/.2/.3`), kept deliberately for the next occurrence.
- **What it already cost:** Fix 118 (`83c6d1983`) shipped on a reading produced by the poisoned call site - "a bare OVERLORD scope voided the whole limit" was an artefact, not a measurement; the code site, `tools/fix_registry.json` row 118 and checklist R79 were corrected the same day, and whether a bare invalid scope really poisons an OR is back to ASSUMED. Second-order cost: every OTHER console harness homed in `events/wa_events_test.txt` (railway suite, pathfind probes) has readings of unknown validity until re-fired from a clean call site or rehomed - that audit is a QUEUE row, not done.
- **Evidence:** `events/wa_test_convoy_arsenal.txt` (rehomed harness, header carries the short reproduction), `events/wa_test_scope_isolation.txt` + `common/scripted_effects/WA_TEST_scope_isolation_effects.txt` (the kept isolation harness), `common/scripted_effects/WA_TEST_convoy_arsenal.txt` (the self-check that caught it), the withdrawn-claim comment in `WA_AI_PRODUCTION_update_coalition_sea_weight` (`common/scripted_effects/WA_production_strategy_effects.txt`).
- **Addendum 2026-08-27 (rail-corridors harness, save 1945.7.1): a dedicated event file is NOT sufficient protection — the firing-tag context also triggers it, and nested scripted triggers escape it.** MEASURED, same save, same event (`wa_test_rail.1` in its own `events/wa_test_rail_corridors.txt`), two consecutive console fires: as the spectated observer tag (BHU) the header read `1 0 0 1 0` and every INLINE country-valued compare in the report effect failed as a family (`is_controlled_by = var:` printed BLOCKED on states controlled by the anchor itself — state 366 "by United States of America", anchor USA) — while the SAME compares inside the nested scripted trigger `WA_AI_RAIL_CORRIDOR_state_is_friendly`, called from the same report effect in the same run, returned correct verdicts on all 8 corridors. After `tag FRA`, byte-identical everything: header `1 1 1 1 0` and the inline walk agreed with the nested trigger 8/8. So the poison discriminates by CALL CONTEXT (event file in 2026-08-20, firing tag here) and by NESTING (inline compares poisoned, scripted-trigger indirection clean in the same execution). Cause still UNKNOWN; practical rule unchanged plus one line: fire console harnesses AFTER a `tag` switch to a real country, never as the spectated observer, and treat an inline-vs-nested disagreement as this signature, not as a code bug.

### The engine refuses railways in `impassable = yes` states — and the WA land graph routes straight through them

- **Date:** 2026-08-27 ([rail-corridors] owner tests, saves `SAF_1945_08_05_23` / `SAF_1945_08_09_02`)
- **Symptom:** `build_railway` with a 30-province explicit `path` silently built NOTHING (flag latched, zero track); rebuilt edge-by-edge, 17 of 29 edges built at level 5 and 12 were refused by `can_build_railway`, leaving three gaps in the Sahara.
- **Cause:** every refused edge touched a province of a state marked `impassable = yes` in `history/states` (786 Mauritanian Desert, 515 Southern Sahara, 775 B.E.T., 767 North Darfur; also on other routes: 514, 273, 552). The engine refuses rail construction there — and rejects an entire multi-province `path` list if ANY edge in it is invalid, with no error and no log. The generated `WA_AI_MAP_province_connections.txt` land graph INCLUDES impassable-state provinces, and hop-minimising pathfinding prefers exactly those huge desert provinces, so any path computed on WA map data walks into them by default.
- **Rule:** (i) never emit a `build_railway`/`can_build_railway` path that touches an impassable-state province — filter `history/states` `impassable = yes` out of the graph before pathing (`tools/gen_rail_corridors.py parse_impassable_states`); (ii) build multi-hop rail EDGE BY EDGE (`path = { a b }`, the PC-core form) with `can_build_railway` guarding each edge — a whole-path call is all-or-nothing and fails silently; (iii) latch a save-visible incomplete flag off `has_railway_connection` so a partial build is measurable (it is what isolated this).
- **Wider caveat, unaudited:** WA script-side pathfinding (`WA_AI_pathfinding_effects`) runs on the same graph and can likewise route through impassable provinces; whether any consumer cares is not established.
- **Evidence:** `rail.py --corridor` on `SAF_1945_08_09_02` (12 BREAK pairs, all zero-rail provinces in the four impassable states); `history/states/786-*,515-*,775-*,767-*` (`impassable = yes`); triggers_documentation.md:1884 (`can_build_railway`), :4603 (`has_railway_connection`).

### `front_armor_score` with an ally's id is a silent no-op

- **Date:** 2026-08-20
- **Symptom:** Germany's only armour steer toward North Africa, `front_armor_score id = "ITL"` value 10 in `WA_AI_MILITARY_GER_focus_on_north_africa_FRONT` (plus its `value = 0` counterpart in `war_with_soviets_2`), had steered nothing for as long as it existed — no German armour ever went to Africa through it.
- **Cause:** `id` on `front_armor_score` names the ENEMY tag of the front (vanilla oracle: GER `id = POL` 250 for the Poland campaign, `id = SOV` 500 for Barbarossa, ALLIES `id = GER` +500 toward the European front). ITL is Germany's own side (ITA's Libyan subject), so no front against it ever exists and the entry scores nothing — no error, no log line. `documentation.info` lists the type with one line and no field semantics, so nothing in the repo contradicted the wrong reading ("armour toward fronts located in ITL's land").
- **Rule:** Before shipping a `front_armor_score` entry, check the `id` names a country the block's owner can actually be at war with while the block is enabled. The oracle is vanilla usage (the type is id-keyed only — no `country_trigger`, TYPES_REFERENCE §front_armor_score), so a dynamic enemy needs either enumerated payload tags of the anchor's plausible holders or the scripted AIFC emission route (which carries a measured list-accumulation defect).
- **Evidence:** vanilla `common/ai_strategy/GER.txt` front_armor_score usage; `WA_AI_MILITARY_COUNTRY_GER_FRONT.txt` (Fix 119 rework, 2026-08-20); `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` front_armor_score section.

### A shared priority band makes a missing railway compete with a level-5 upgrade — and insertion order decides

- **Date:** 2026-08-21 (campaign `8c0fea4c`, Fix 120 / checklist R81)
- **Symptom:** the North-African theatre corridor "consolidated before it extended". At 1941.12 the eight rear hops Tripoli→Tobruk all read rail level **5** — one *above* `corridor.rail_level_cap` = 4 — while **Tobruk 1130 → 5078 had been BREAK since 1940.6**, 21 months, 15 of them with both ends held by the same side. The visible consequence in game was an unconnected supply depot at the head of the chain.
- **Cause:** not a starved budget and not the admission gate. `WA_AI_PC_railway_STRATEGY_theatre_corridor` computes **one** `_corridor_prio_` for the whole corridor (`rail_war` 1000 / `rail_prewar` 500) and copies it into every `corridor_route_prio_` slot, and `WA_AI_PC_assign_factories` sorts by priority **alone** — so at a tie the bubble sort serves insertion order. A hop at level 0 therefore ranked equal with a hop being raised from 4 to 5, and equal with every land-war segment in Europe. MEASURED at the project level, 1941.6: ITA's **single funded railway factory** sat on `4120 → 13509`, an edge already at map level 5, while `1130→10120`, `10120→7079`, `7079→5078` — all at map level **0** — held 0 factories with 4 weeks of stall, queued *behind* 13 European land-war segments at the identical 1000.
- **Rule:** a priority band is only a band if the things inside it are interchangeable. When one queue mixes "create the thing" with "improve the thing", the create side needs its own value, or the sort decides by accident. The information was already there and free — `WA_AI_PC_start_railway_project` reads `global.WA_AI_PC_railway_connection_level_[x]^[y]` two lines before admission and used it only for an equality test. Read the RAW map level, before `_queued_for_segment` is folded in: the question is "does a railway exist here", not "has someone asked for one".
- **Detection:** `rail.py --corridor <node list>` on three saves a year apart. Any hop above the corridor's own `rail_level_cap` **while another hop of the same corridor reads BREAK** is this bug, and it is visible without opening the queue. Then `savegame.py pc <TAG> --limit 0` and cross-read the funded row's `prov ->prov` against `rail.py` — a funded edge already at target beside a starved edge at 0 is the confirmation. (`pc --match corridor` does **not** work: `--match` filters the building name, never the strategy tag.)
- **What this entry does NOT claim:** that the ordering was the only thing wrong. On the same save the Fix 41 aging lane served **16 of ITA's 17 factories** to a 10-month-old priority-**100** infrastructure project, leaving one for the sorted fill. That is the PC fairness subject and Fix 120 does not touch it. What the ordering explains is *where* the spend went: eight rear hops one level above the cap is ~6400 construction points against 2400 for the three missing segments, so the capacity to close the chain existed and was spent elsewhere.
- **Evidence:** `rail.py --corridor 1149,9980,4047,4057,1127,11954,10049,7082,1130,5078` over 1940.6 → 1942.3; `savegame.py pc ITA 1941.6_Jun.hoi4 --limit 0`; `savegame.py control 960,451 --provinces` (both ends Axis from 1940.12); `documentation/WA_AI_RAILWAY_SYSTEM.md` "Connect before consolidate".

### `garrison = +50` is the default for every minor at war, and it is why the dominions never leave home

- **Date:** 2026-08-21 (campaign `8c0fea4c`, Fixes 123/124 / checklist R84/R85)
- **Symptom:** with Japan still neutral, **AST held 17 of 22 divisions (77 %) and NZL 8 of 11 (73 %) in engine area-defence orders** at 1941.6, and Britain fought the East-African campaign alone — 37 of ENG's 66 divisions (56 %) in the theatre at 1940.10 against 8 in Egypt, while RAJ had 24 of 42 sitting in India. The obvious reading is "the pull toward Africa is missing".
- **Cause:** the pull was **not** missing. `WA_AI_MILITARY_ALLIES_east_africa_contested_FRONT` (+150) already reached RAJ and RAJ's own `-100` Asia-first suppression was not armed (it needs a war with PER/SOV/JAP). What was missing was an army to answer it: `WA_AI_MILITARY_ARCHETYPE_minors_home_first` (`WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt`) gives **every minor at war `garrison = +50`** — *more* engine area defence, not less — and AST and NZL have no `garrison` writer of their own at all. RAJ escapes it only through `WA_AI_MILITARY_RAJ_core_front_requests`, whose gate is `has_war_with = JAP`, and it additionally parks 0.25 of its army in a `subtract_fronts_from_need = no` reserve precisely while Japan is neutral.
- **Rule:** when divisions do not arrive somewhere, count the order classes before adding a pull. `plans.py <TAG>` splits front / buffer / areadef / NO_ORDER in one line; an army that is 70–80 % `areadef` is not being under-asked, it is being held. And check `minors_home_first` first — it matches every dominion, every neutral-ish Allied minor and (once its army passes 1M men) not ENG, so it is the widest-reaching FRONT block in the mod.
- **Bonus, and it answers a question the docs left open:** RAJ is a natural control for **what `garrison = -5000` actually does**, which `documentation/WA_AI_MILITARY_SYSTEM.md` §16 called an untested convention and R74 leg 1 was written for. Its area-defence divisions read **14 / 17 / 16** at 1940.10 / 1941.6 / 1941.12 (no `-5000`) and **0 / 3 / 2** at 1942.3 / 1942.6 / 1943.6 (the JAP war arms it), while its BUFFER count *rose* 17 → 21 → 25 — so the engine did not merely move the guards onto the new fronts. **DERIVED**, rival explanation named (the switch coincides with Japan's entry); the cross-section closes it without the date — on the single 1941.6 save GER reads 1 of 203 and ITA 4 of 84, both carrying `-5000`, against AST's 77 % and NZL's 73 %, neither of which does. **Refined 2026-08-27:** the direct CAN imgui measurement ("A negative `garrison` does NOT empty existing area-defence orders", end of log) shows `-5000` does not evacuate existing areadef orders — the rival explanation was the right one (the Japan-war fronts pulled RAJ's divisions); this cross-section stands as correlation (fewer areadef where `-5000` is armed early), not as evacuation.
- **Detection:** `plans.py <TAG> <saves>` order-class census, read as a *share* of the army rather than a count, plus `grep "type = garrison"` across `common/ai_strategy/` to find who writes one at all — thirteen files do, and the dominions are not among them.
- **Evidence:** `plans.py AST,NZL,RAJ,ITA,GER,ENG 1941.6_Jun.hoi4`; `plans.py RAJ` over 1940.10 → 1943.6; `plans.py ENG,RAJ 1940.10_Oct.hoi4 --where`; `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt:104-115`.

### A `grep -c` on `hoi4.exe` is not a token test — it matches substrings, and a negative control does not catch that

- **Date:** 2026-08-21 (Fix 122, caught by the boot test the same day)
- **Symptom:** `ai_strategy = { type = naval_mission_threshold id = "MISSION_CONVOY_RAID" value = -100 }` was rejected at load: `Error: "bad mission type: MISSION_CONVOY_RAID, near line: 860" in file: "common/ai_strategy/WA_AI_NAVAL_FACTION_ALLIES.txt"`. The whole block silently does nothing after that line.
- **Cause:** the token had been "verified present in the binary" by the method `wa-engine-reference` prescribes for undocumented tokens — `grep -c "<token>" hoi4.exe` with a control string that cannot exist. The control behaved correctly (`MISSION_ZZQXWV_NOT_A_TOKEN` returned 0), and the conclusion was still wrong: **grep matches substrings**, and `MISSION_CONVOY_RAID` is a prefix of the real token `MISSION_CONVOY_RAIDING`. The control proves the search works; it does not prove the match is the whole token.
- **Rule:** for an exact-token question, extract whole matches and compare, never count hits — `re.findall(rb'MISSION_[A-Z_]+', open('hoi4.exe','rb').read())` and check membership in the resulting set. Keep the negative control (it catches a broken search), and add the positive one that actually matters: a token you know is valid must appear **exactly**, and the candidate must not be a proper prefix or suffix of any other match. The same trap applies to `type =`, effect and trigger names — anything where one legal token contains another.
- **Where the naval mission names really live:** the install's `common/defines/00_defines.lua`, in the comment column of `MISSION_FUEL_COSTS` — HOLD, PATROL, STRIKE FORCE, CONVOY RAIDING, CONVOY ESCORT, MINES PLANTING, MINES SWEEPING, TRAIN, RESERVE_FLEET, NAVAL_INVASION_SUPPORT. `common/ai_strategy/_documentation.md` lists `naval_mission_threshold` in its index and gives it **no section at all**, which is why nobody read the enum in the first place. Vanilla only ever uses two of them (`MISSION_PATROL`, `MISSION_CONVOY_ESCORT`), so usage was not a complete oracle either.
- **Detection:** `error.log` at boot. `bad <something> type: <TOKEN>, near line: N` names the file and the line. Nothing in the mod's own Python checkers can see this — `check_constants.py` and `check_worklist.py` do not know engine enums — so **an ai_strategy carrying a string-valued `id` is F9-boot-test territory by construction**.
- **Evidence:** the boot `error.log` line above; `common/defines/00_defines.lua` `MISSION_FUEL_COSTS`; the exact-match extraction that produced the real list (`MISSION_CONVOY_RAIDING`, `MISSION_CONVOY_ESCORT`, `MISSION_PATROL`, `MISSION_STRIKE_FORCE`, `MISSION_HOLD`, `MISSION_MINES_PLANTING`, `MISSION_MINES_SWEEPING`, `MISSION_TRAINING`, `MISSION_NAVAL_INVASION_SUPPORT`); the corrected block header in `WA_AI_NAVAL_FACTION_ALLIES.txt`.

### An unlocked hull is not a buildable ship — `ai_equipment` is a separate permission, and a country can hold a whole tech tree with no design to match it

- **Date:** 2026-08-21 (campaign `8c0fea4c`, Fix 129 / checklist R90; it overturned Fix 126's first diagnosis the same day)
- **Symptom:** every Commonwealth dominion ran **exactly one** active naval factory for the whole war — RAJ 1 of **8** dockyard levels at 1941.6 and 1 of **15** at 1945.6, AST 1/6, CAN 1/16, NZL 1/7, SAF 1/4 — against ENG's **81 of 88**. 36 idle dockyard levels, and RAJ's fleet frozen at exactly **1 ship for ten years**.
- **First diagnosis, and it was WRONG:** the convoy ladder in `WA_AI_PRODUCTION_DEFAULT_navy.txt`. It is genuinely off for these countries (tier 0 needs `convoy < 200`, tiers 1-3 need 20 shipyards, `stop_MINORS` brakes above 300), the story fits every number, and it is not the cause.
- **The closure test that killed it, and it cost nothing:** find countries in the SAME save that face the SAME rule and do not have the symptom. Every minor on the **generic** naval tech tree saturates its dockyards — SWE 17 factories on 16 levels, TUR 21/20, ARG 6/5, BRA 6/5 — under the identical ladder. Only the countries on the **British** tree were idle. One command, and it moved the search from the production system to the tech/design layer.
- **Real cause:** the dominions inherit the **British** naval tech tree (`eng_frigate_1..5`, `eng_destroyer_1..6` — MEASURED on all five) and **no `ai_equipment` file in the mod named them**. `common/ai_equipment/ENG_naval.txt` had `available_for = { ENG }` on all twelve design groups; `generic_naval.txt`, which they *are* allowed to use (it blocks only the seven majors), gates every design on `has_tech = generic_frigate_1` / `generic_destroyer_*`, and they hold **zero** generic naval techs. A hull with no `ai_equipment` design is not buildable by the AI. WA meanwhile classes them as escort navies (`WA_AI_CONFIG_is_escort_navy` = minor AND in the Allies) and hands them `role_ratio naval_escort 50` — a role with nothing to bind to.
- **Rule:** **in HOI4 with MtG, three separate things must line up before an AI country can build a ship: the TECH (the hull), the DESIGN (`common/ai_equipment/`, `available_for` / `blocked_for` / `has_tech`), and the ROLE (`role_ratio`).** Reading only the tech list, as the first pass did, says "it has frigates unlocked" and is worthless on its own. When a country's inherited tech tree has a country prefix (`eng_*`, `ger_*`, `usa_*`), check whether the design file for that prefix admits it — the generic designs never will, because they are keyed on `generic_*` techs the country does not research.
- **Detection:** the whole check is `grep -rlnE "\b(TAG)\b" common/ai_equipment/` returning nothing, next to a tech list full of another country's prefix. Cross-check by counting active naval factories against dockyard levels per country in one save; a country pinned at 1 while its peers saturate is the shape.
- **Second-order cost, recorded:** Fix 126 shipped a forced `equipment_production_min_factories id = convoy value = 3/6` on the strength of the wrong diagnosis. With the designs restored that floor would have outbid the escorts the same mod asks these countries for, so it was removed the same day and Fix 126 kept only `equipment_production_surplus_management`. **A fix built on an unfalsified diagnosis does not merely fail to help — it competes with the real fix.**
- **Evidence:** `savegame.py section <save> <TAG> production --max-lines 0` (naval line / active factory counts; **the default 400-line cap truncates and made an earlier pass report "zero naval lines"**), `... technology --max-lines 0 | grep -oE 'eng_(frigate|destroyer)_[0-9]+'` and `... 'generic_[a-z]+_[0-9]+'`, `savegame.py buildings <TAG> <save> --match dockyard`, `common/ai_equipment/ENG_naval.txt` header, `common/ai_equipment/generic_naval.txt:1443`, `common/units/equipment/ship_hull_very_light.txt` (frigate hull, 80 IC).

### The corridor pathfinder filters by PROVINCE control, the executor admits by STATE controller — and a tie between two routes decides which one you get

- **Date:** 2026-08-21 (campaign `8c0fea4c`, Fix 130 / checklist R91)
- **Symptom:** with the connect-first phases live, Italy's rail still crawled from Tobruk 1130 to the hub 5078, and on the map it visibly ran **east along the coast** (Bardia, Sallum) and stopped instead of cutting inland. Every obvious explanation was wrong: the provinces were all friendly, the pathfinder found a route, and the corridor budget was not full.
- **Cause:** `WA_AI_PATHFIND_PROV_get_path` type 2 accepts a province held by ROOT, a subject or an ally — a **province** test. `WA_AI_PC_start_project` then applies `WA_AI_PC_state_controller_allows_admission` scoped to `global.WA_AI_MAP_province_state_id^<first province of the segment>` — a **state** test. On contested ground they disagree. MEASURED: **every province of both candidate routes was ITL-held**, but state **452 Marsa Matruh was ENG-controlled** with an 11/3 province split (10/4 later, and state 960 went ENG too). The coastal route's last segment was scoped to 452 and refused **every pass, for ever**, in silence — `wa_tlm_r103_corridor_blocked_n` 4 → 5 → 6 was the only trace. And the two routes are **both three hops**, so nothing but the pathfinder's tie-break chose the doomed one.
- **Rule:** when a pass *selects* work with one predicate and *executes* it with another, they must be the same predicate — the Fix 103 lesson, which split permission from payment and then extracted the admission gate verbatim so selector and executor could not drift. This is the same class one level down: province-scoped selection over state-scoped admission. Until they are unified, a corridor whose route crosses a contested state needs a **forced junction node**, which is what Constantine 9976 already was for the western arm and what 13481 now is for Tobruk.
- **Detection:** `wa_tlm_r103_corridor_blocked_n` rising while the map shows no progress on a hop whose provinces are all friendly. Then read the `state` column of the `corridor` rows in `savegame.py pc <TAG> --limit 0` and compare it with `savegame.py control <states> <save>` — **the state-controller line, not the per-province one**. A hop whose segment sits in a state the enemy controls is refused no matter who holds the ground.
- **Second trap, same session:** a province id quoted from an in-game tooltip in a report was **13841**, a digit transposition of **13481** — and 13841 is a real province, in **state 443 Sind, India**. A wrong id that resolves is worse than one that does not. Check every incoming province id against `WA_AI_MAP_state_provinces` before designing on it; two lines of Python answer it.
- **Evidence:** `savegame.py control 451,663,960,452 ITA_1941_05_23_21.hoi4` (state 452 ENG, 11/3) and `--provinces` (1130/4136/10120/7079/13481/5078 all ITL); `savegame.py pc ITA` corridor rows `10120→7079` and `7079→5078` scoped to 451 and 452; the generated province graph (`WA_AI_MAP_province_connections`), which gives 1130→4136→13481→5078 as a three-hop inland alternative; `documentation/WA_AI_RAILWAY_SYSTEM.md` "The mismatch phase A cannot see".

---

## `subtract_from_variable` on a TEMP operand leaves the temp unchanged — the `_temp_` twin is not optional

- **Symptom:** `WA_AI_LANDING_update_reservations` computed "days since 1936.1.1" as
  `set_temp_variable = { _resv_today = global.num_days }` followed by
  `subtract_from_variable = { _resv_today = global.WA_AI_LANDING_epoch }`. MEASURED (console harness
  `wa_resv.1` leg A, 2026-08-23, 1936.1.1 boot): `epoch = 706640`, `num_days = 706640`, and
  `today` printed **706640**, not 0 — the subtraction never touched the temp. Every
  `op_expiry > _resv_today` comparison would then read "expired" and the whole reservation system
  would have been silently inert, while parsing clean and looking correct in review (two reviewers
  read the line without flagging it).
- **Cause:** the non-temp arithmetic effects (`subtract_from_variable`, `add_to_variable`,
  `multiply_variable`, `divide_variable`) operate on the PERMANENT variable namespace. Given a name
  that only exists as a temp, they do not resolve it to the temp — the temp keeps its value and the
  reader sees the unmodified temp. The engine doc (`effects_documentation.md` §subtract_from_variable)
  does not say this; the `*_temp_variable` twins exist precisely because the namespaces are separate.
- **Rule:** arithmetic on a temp variable uses the `_temp_` effect form, always
  (`subtract_from_temp_variable`, `add_to_temp_variable`, …). `set_temp_variable` followed by
  `subtract_from_variable` on the same name is the broken mixed idiom; grep for it when a computed
  temp reads impossibly large or exactly equal to its first operand.
- **Detection that worked:** the harness printed the operands AND the result on one line, so
  `today = num_days` with a non-zero epoch was self-evident. A probe that prints only the result
  would have shown a huge number with nothing to compare it against.
- **Evidence:** `wa_resv.1` leg A log line (`op_n = 30  epoch = 706640  num_days = 706640
  today = 706640`); fix in `WA_AI_LANDING_effects.txt` (`subtract_from_temp_variable`) and
  `WA_TEST_resv.txt`, both commented with the measurement.
- **Bonus sighting, same session:** the verification re-run picked up the edited scripts WITHOUT a
  game restart (hot reload) and its context header read `I-am-ROOT=0 / I-am-THIS=0` while
  `always`, `ROOT-scope-usable` and the loc names all read correctly — the "Two call sites, one
  effect" syndrome, this time from the SAME file that had read clean minutes earlier. New data
  point for that entry: an in-session script hot-reload is a candidate trigger of the poisoned
  state (ASSUMED — one sighting). The harness's STOP rule caught it, which is the contract doing
  its job; variable arithmetic (leg A) read correctly throughout.

### Scope errors logged after a hot reload or a savegame load may be false — reproduce on a cold boot before diagnosing

- **Date:** 2026-08-24 (Discord report by 156, WA toolpack author — peer report, not measured in this repo)
- **Symptom:** Aigle2 kept getting scope errors in the log after an AI-authored change to 156's
  toolpack; 156 reverted the change, re-tested the toolpack, and saw no errors ("I have reverted
  and am testing the tool out, no errors so far") — the errors did not follow the code.
- **Cause:** per 156: "hot reloading files and also loading save games can cause random scope
  errors printed to log that aren't real errors" (ASSUMED — second-hand from a modder who has
  observed it across the standalone toolpack; mechanism unobservable). This corroborates two
  in-repo sightings: the 08-20 "Two call sites, one effect" poisoned-scope syndrome, and the
  08-23 bonus sighting where a hot-reloaded harness read `I-am-ROOT=0` from a file that had read
  clean minutes earlier. Savegame *loading* as a trigger is new information from this report.
- **Rule:** a scope error in `error.log` observed in a session that hot-reloaded scripts or loaded
  a savegame is not evidence of a script defect. Before diagnosing, reverting, or shipping a fix
  on the strength of logged scope errors, reproduce them from a **cold boot into a new game**; only
  errors that survive that reproduction are real. Symmetrically, a clean log after a hot reload
  proves nothing either — the 08-23 sighting shows hot reload can also *create* poisoned state.
- **Detection:** ask how the erroring session was started (fresh launch / reload / save load). The
  scope self-check header of the harness contract (`who:` / `scope:` lines + known-false control)
  distinguishes a poisoned session from a real scope bug in scripted effects.
- **Evidence:** Discord #wa channel, 2026-08-24 (156 ↔ Aigle2 exchange); log entries "Two call
  sites, one effect" (08-20) and the hot-reload bonus sighting under the temp-arithmetic entry
  (08-23).

### A negative `garrison` does NOT empty existing area-defence orders — and same-type/same-target entries sum

- **Date:** 2026-08-27 (`[allied-total-commitment]`, owner `imgui show ai-strategy` on CAN, campaign `24933fb9` resumed)
- **Symptom:** CAN's `garrison = -5000` release was proven armed and correctly gated (harness
  `wa_tc.1`, closure PASS 1942.2), yet CAN still held ~100 % of its home divisions in engine
  area-defence orders (1943.6) — the two usual explanations, "block silently OFF" and "wrong
  payload", were both already excluded.
- **Cause (MEASURED, the first ON-case reading this convention ever had):** the imgui strategy
  window shows CAN's garrison tree as **ONE summed row, Weighted Value -4950** (-5000 release
  + 50 `minors_home_first`) — armed and held. The value reaches the engine, and existing engine
  areadef orders still keep their divisions: a negative `garrison` *prevents/suppresses*, it does
  not *evacuate*. The proven mover is a `put_unit_buffers` catcher order (the Scotland division,
  1942.3, via `defend_britain`). The same read is the first direct proof that **same-TYPE /
  same-TARGET `ai_strategy` entries SUM** into one weighted value; the cross-AREA / cross-target
  variant of the summing question remains ASSUMED.
- **Rule:** to empty a mainland, do not deepen the negative `garrison` — pair it with a catcher
  (buffer) that gives the released divisions somewhere to go; a bigger negative moves nothing
  that already sits inside an engine areadef order. And when two blocks write the same type at
  the same target, budget their *sum*, because the engine nets them into one row.
- **Supersedes/answers:** the "does NOT claim" clause of "An `ai_strategy` block that is silently
  OFF…" (2026-08-19) — this is the ON-case measurement it demanded; and it refines the RAJ
  DERIVED bonus of "`garrison = +50` is the default…" (2026-08-21): RAJ's areadef drop at
  Japan's entry is explained by the new fronts pulling divisions, not by `-5000` evacuating them.
- **Evidence:** `documentation/WA_AI_MILITARY_SYSTEM.md` §24 "Known limits" (the imgui reading);
  WORK.md `allied-total-commitment` (parked row); `common/ai_strategy/WA_AI_MILITARY_COUNTRY_CAN_THEATRE.txt`
  (`..._empty_mainland` catcher, commit `8e4a44ef9`).

### A delegate-availability bar on TOTAL `num_divisions` reads "available" exactly when the delegate is fully committed elsewhere

- **Date:** 2026-08-27 (campaign `24933fb9`; `[commonwealth-handoff]` probe a2 + `[raj-gulf-garrisons]` SS26)
- **Symptom:** two delegated-mission systems shipped with availability verdicts of the shape
  "delegate `num_divisions > 29`" (+ force floor). Both failed the same way on the same
  campaign: at 1943.6 RAJ reads "available" at **76 total divisions while 34 stand on the Burma
  wall and 3 in East Africa** — ENG stays exempted and back-fills 14 divisions itself (the
  handoff inverts); and the Gulf guards (Kuwait 656 / Aden 659) are RAJ-empty from 1942 on while
  ENG stands both at its 0.02 floor.
- **Cause:** `num_divisions` counts the whole army wherever it stands, so the verdict conflates
  "the delegate has an army" with "the delegate can man THIS theatre". The first second war
  (Japan) consumes the army and every delegation keyed on the total stays armed over an empty
  theatre. The conflation was even written down as a known gap at ship time (2026-08-25) — it
  still shipped as the only bar, and became the campaign's measured failure mode in two systems
  at once.
- **Rule:** an availability verdict for a delegated mission must be falsifiable by the THEATRE,
  not by the army: measure in-theatre presence (divisions physically standing in the mission's
  regions) or at minimum subtract fronts already engaged elsewhere. Until a trigger can do that
  cheaply, every delegation ships with the probe "delegate in-theatre count < N while the
  availability trigger reads true" so the conflation is caught on the first campaign — probe a2
  is what turned this from a footnote into a measurement.
- **Detection:** `plans.py <delegate> <saves> --where` — total division count healthy, mission
  regions at 0-3, the delegating country's own divisions back in the theatre it delegated.
- **Evidence:** WORK.md `commonwealth-handoff` (probe a2, `plans.py ENG,RAJ --where` 1943.6) and
  the `[raj-gulf-garrisons]` SS26 FAILED verdict on `24933fb9`; the verdicts live in
  `common/scripted_triggers/WA_AI_MILITARY_triggers.txt` (`commonwealth_east_africa_available`,
  the three RAJ Gulf verdicts).

### A reserve-capability gate reads industry, not stockpile - and ENG closes by owner ruling

- **Date:** 2026-08-27 (campaign `24933fb9` war-entry saves; `[reserve-quality]` v2)
- **Symptom:** the reserve-bank veto needed a "can this country equip a reserve dump" term; both
  obvious candidates looked measurable - current infantry-equipment stockpile, or a flat
  division bar - and both were wrong.
- **Cause:** stockpile does not discriminate: RAJ holds 53k infantry equipment at its 1939.10
  war entry (licensed production) yet cannot sustain 10 more consumers on 22 MILs, while CAN
  holds only 11.6k yet must deploy (the snowball-bootstrap case, owner ruling). The flat
  division bar conflates USA (340 MILs, must deploy at any army size) with RAJ (22 MILs, 50
  divisions). MIL-count tiers separate every measured pair except ENG - 134 MILs but its land
  output is committed to air/sea (owner-reported empty land stocks at war entry), which no
  save-measurable proxy separates from USA.
- **Rule:** gate equipment capability on a production-scale proxy (MIL tiers), never on current
  stockpile - stock is inflated by licences/lend-lease and starved by commitments in ways that
  invert the verdict. Where the proxy fails for one tag (ENG), the carve-out is an owner ruling
  recorded as a CONFIG archetype (`WA_AI_CONFIG_is_reserve_materiel_limited`) with the rejected
  pure-capability alternative recorded here so it is not re-proposed. ASSUMED: whether
  `num_of_military_factories` counts occupied MILs (install doc says only "check amount of
  military factories"); benign direction - captured MILs do produce.
- **Evidence:** WORK.md `[reserve-quality]` v2 calibration table (`24933fb9`: RAJ 22 MIL/50 div,
  CAN 15/14, ENG 134/31, USA 340/7; stocks RAJ 53k vs CAN 11.6k);
  `common/scripted_triggers/WA_reserves_triggers.txt` (tier OR),
  `common/scripted_triggers/WA_AI_CONFIG.txt` (`is_reserve_materiel_limited`).

### A nameless create_corps_commander creates an orphan - and its caller loops forever

- **Date:** 2026-08-28 (campaign `0767987f`, all 4 sampled saves; `[recruit-loop]`)
- **Symptom:** owner-observed: ARG's AI spends 10 command power in a loop. Save: CP pinned
  under 13 for 9 years, 117 identical skill-1 corps commanders in the character DB that no
  in-game view ever showed.
- **Cause:** `create_corps_commander = { skill = 1 }` with no `name` creates the character in
  `character_manager` (auto token `TAG_` with EMPTY suffix) but never registers it in the
  country's characters list - so `every_army_leader` never counts it. The caller
  (`WA_AI_recruit_general`, 2-day event) gates on that count staying `< 3`, so every country
  whose official roster holds < 3 non-marshal generals re-fired the creation forever: 10 394
  orphan characters across 106 countries (> 55% of the save's character DB), each looper's CP
  income burned at the 10-CP min clamp. Zero exceptions over 74 measured cells on
  "official < 3 => growing orphans + pinned CP". Every vanilla and Expert AI use of
  `create_corps_commander`/`create_field_marshal` passes `name` (+ gfx); the bare form had
  never worked and nothing ever said so.
- **Rule:** never call `create_corps_commander`/`create_field_marshal` without a `name`; prefer
  `generate_character` (documented "create + recruit", random name from the country's own lists
  when omitted, install effects_documentation.md:4441) with a unique per-creation `token_base`.
  And any scripted creation whose caller gates on a COUNT must carry a registration watchdog
  (expected-count verify on the next firing, refund on failure, two-strike latch with a
  growth-since-latch exit) - a silent creation failure otherwise converts the gate into an
  infinite loop. Oracle note: character EXISTENCE is the wrong success check - the orphans
  exist; count what the gate reads.
- **Detection:** save-side: `character_manager` blocks with empty-suffix auto tokens absent
  from every country's characters list, count growing monthly. Console: `event wa_test_rl.2
  <TAG>` prints the general-count delta around one real recruit pass.
- **Evidence:** WORK.md `recruit-loop`;
  `common/scripted_effects/WA_AI_leader_recruitment_effects.txt` (watchdog + generate_character);
  harness `common/scripted_effects/WA_TEST_recruit_loop.txt`. Engine boundary, ASSUMED: why
  registration fails for the nameless form, and why XSM/YUN loop despite an official count >= 3
  (warlord/united-front reading).

### `role_ratio` shares are the strategy VALUES normalised, not "base 100 plus value" per role

- **Symptom:** `common/ai_strategy/documentation.info` (UNIT RATIOS / ALL BUT AIR) says unit ratios
  are "a base of 100 plus the value indicated in the strategy", which reads as: every role starts at
  100 and a role with no strategy competes on equal footing with infantry. Every WA header written
  against that sentence had to invent a reason why 13 roles do not all come out equal.
- **Real behaviour, MEASURED** (owner console `imgui show ai_division_production`, SOV 1943.11.3,
  372 wanted divisions). WA strategy sums for SOV that day were infantry 45 (100 base, -20
  mechanized, -10 mountaineers, -25 armor budget), mechanized 20, mountaineers 10, heavy_armor 13,
  medium_armor 12 - sum 100. The engine wanted infantry 167, mechanized 74, mountaineers 37,
  heavy 48, medium 45: **45.0 / 19.9 / 10.0 / 12.9 / 12.1 percent**, every row within rounding of
  its strategy value. `suppression` carried no strategy and wanted 0; `motorized` carried none and
  had no row at all.
- **Rule:** a role's share of the wanted divisions is `its strategy sum / the sum of all strategy
  sums`. A role with no `role_ratio` strategy wants **nothing**, it does not silently claim 100.
  So the WA convention of keeping the values summing to 100 is not a house style - it is what makes
  each value readable directly as a percent. Two consequences worth stating: giving a role a share
  it has no enabled target template for WASTES that share outright (the naval_escort case, above),
  and a role whose share reaches 0 has its templates decommissioned (the garrison case).
- **Detection:** `imgui show ai_division_production`, the per-role table under the country. Nothing
  in a savegame names a `role_ratio` strategy by role, so this is a live-window read only.
- **Evidence:** WORK.md `armor-role-budget` (harness run 1);
  `common/scripted_effects/WA_AI_PRODUCTION_armor_budget.txt`. Engine boundary, ASSUMED: what the
  documentation.info sentence actually describes - possibly `unit_ratio` for air, which the same
  section covers separately.

### An `ai_templates` flag value is a hand-maintained join key - a calculator branch with no entry deletes the role

- **Symptom:** the United Kingdom stopped wanting heavy tanks entirely (owner console 1943.11,
  `imgui show ai_division_production`: no `heavy_armor` row at all, while `medium_armor` was there).
  The role_ratio budget was correct and the console harness read `VERDICT 1 1 1`, so the AI was
  being told to want heavy divisions and simply could not.
- **Real cause, MEASURED:** `WA_AI_TEMPLATES_calculate_heavy_armor_template` selects a template by
  writing a NUMBER into `WA_HEAVY_ARMOR_TEMPLATE`, and each entry in
  `common/ai_templates/WA_AI_TEMPLATES_armored_heavy.txt` enables on
  `has_country_flag = { flag = WA_HEAVY_ARMOR_TEMPLATE value = N }`. The two lists had drifted: the
  calculator emitted 7103-7113, the file declared 7100-7109 plus **three entries left at the literal
  placeholder `value = xxxx`**, and one value (7102) was declared twice. Every template existed and
  was correctly composed - the numbers were simply never assigned. A country whose branch landed on
  a number no entry declares carries a flag pointing at nothing: the role has no target template,
  the AI cannot build it, the panel stops listing it, and its whole `role_ratio` share is spent on
  divisions that can never appear. The same defect existed in the light family (5104 dead, 5105
  duplicated). Introduced by `101fd357d "More AI template designs"`, silent ever since.
- **It is progressive, which is what makes it look like a regression.** ENG had heavy tanks while
  its unlocks landed it in 7100-7109; researching modern SPG/SPAA moved it up the else_if chain into
  a branch with no entry, and it lost the role. The country breaks itself by teching forward.
- **Rule:** the value in `set_temp_variable = { _template_value = N }` and the value in
  `has_country_flag = { flag = WA_<X>_TEMPLATE value = N }` are a JOIN KEY maintained by hand across
  two files, with no parser, no checker and no error message. After touching either side, diff the
  emitted set against the declared set - a value on only one side is a silently deleted role, not a
  warning. Match them by TEMPLATE NAME, never by position: the names encode the branch conditions
  (`..._MEC_MEDIUM_SPG_HEAVY_TD_MEDIUM_SPAA` is exactly `mech + medium_spg + heavy_td +
  medium_spaa`), so the name is the only reliable identity when the numbers have drifted.
- **Detection:** for each family, extract `_template_value = (\d+)` from the calculator and
  `WA_<X>_TEMPLATE value = (\d+)` from its `ai_templates` file and compare the two sets; also flag
  duplicates on the declared side and any literal `value = xxxx`. Live: `imgui show
  ai_division_production` - a role with a positive role_ratio share and NO row is this bug.
- **Evidence:** WORK.md `armor-role-budget`;
  `common/ai_templates/WA_AI_TEMPLATES_armored_heavy.txt` (7103-7113 renumbered by name 2026-08-28),
  `WA_AI_TEMPLATES_armored_light.txt` (5104). Engine boundary, ASSUMED: whether a role with a flag
  pointing at no entry is merely unbuildable or is also dropped from the ratio denominator - the ENG
  reading fits the denominator KEEPING it, i.e. the share is wasted rather than redistributed.
### A collapsed `expandedWindow` is still drawn - park it above its own height or the list bleeds into the window

- **Symptom:** two stray unit icons painted over the two name fields at the top of the division
  designer (owner screenshots 2026-08-29). They moved with the `divisions` dropdown, they were real
  subunit art (heavy infantry, then cavalry on another template), and they changed identity with the
  template list. Nothing in the `.gui` declares an icon at those coordinates, and the whole header
  block is byte-identical to vanilla 1.19.2, which does not show them.
- **Real cause, MEASURED:** a `dropDownBoxType`'s `expandedWindow` carries TWO positions - `position`
  (parked, i.e. closed) and `show_position` (open). The parked window is still DRAWN; it is hidden
  only by sitting above the box. WA had enlarged three of them from 260/325 to 400 px without
  moving `position`, so the bottom of the parked list re-entered the visible area. With
  `position = { y = -300 }`, `size.height = 400` and `slotsize.height = 50`, rows 7 and 8 land at
  relative y 3 and 53 - exactly on the collapsed box and on the field below it. Each row is a
  `designer_division_entry`, which draws its template's `GFX_unit_*_icon_medium`.
- **Rule:** `position.y <= -size.height` for every `expandedWindow`. Growing `size.height` without
  moving `position.y` by the same amount IS the bug. `show_position` is independent - the open list
  does not move, so there is no cost to parking further away.
- **Detection:** for each `expandedWindow`, compute `position.y + size.height`; anything above 0
  pokes into the window by that many pixels. Live: change the dropdown's `x` - stray art that is
  really the parked list moves with it.
- **Evidence:** `interface/divisiondesignerview.gui` l.909 / l.1481 / l.1618, parked at -410 on
  2026-08-29; the vanilla 1.19.2 pairs were -160/260 and -300/325, which clear the box by 5 px.

### In a `.gui`, z-order is declaration order - an element declared before a container passes UNDER everything that container draws

- **Symptom:** the exile/colonial flag in the division designer looked dimmed and half-swallowed by
  its frame, while the division symbol a few pixels away was crisp. Moving the flag only changed
  which part of it was swallowed.
- **Real cause, MEASURED:** `GFX_division_icon_bg` is a 96x45 panel whose interior alpha is ~180/255
  - SEMI-transparent, not opaque - and it is declared inside `non_hq_view`, a sibling container
  roughly 500 lines AFTER `colonial_force_flag` in the same parent. Paint order follows declaration
  order, so the panel was painted over the flag and darkened it by ~70%. `div_templ_symbol_button`
  is declared after the panel INSIDE that container, which is why the symbol stayed bright. The
  frame was never the culprit.
- **Rule:** to raise an element above a sibling container, MOVE ITS DECLARATION after that container
  in the same parent. Name and position stay identical, so the C++ still resolves it by name. There
  is no z-index attribute.
- **Detection:** art that looks TINTED rather than clipped means a later sibling with a non-opaque
  background covers it. Read the alpha channel of the suspected panel before concluding - "opaque
  hides, transparent is harmless" is false for anything in between.
- **Evidence:** `interface/divisiondesignerview.gui` - both `colonial_force_flag*` icons moved to the
  end of `countrydivisiondesignerview` on 2026-08-29. Separate finding from the same session, worth
  keeping: `GFX_flag_small` is a `maskedShieldType` drawn at its overlay size (26x21, of which 20x17
  is flag), larger than either frame opening (colonial 19x13, exile 16x11), so it needs `scale` -
  no position alone can make it fit.

### An ai_templates replace_with must resolve inside its own role group - and the switch has a second, silent condition

- **Date:** 2026-08-29
- **Symptom:** fielded light-armor divisions upgraded to the LIGHT_MEDIUM transition composition and
  froze there for months (GER Dec-1940 -> Apr-1941, `ale 20000` so equipment excluded); the imgui
  `ai_templates` window showed best match 0.8125 against `replace_at_match = 0.8` - the threshold
  MET - and the role still targeting the transition. Earlier in the same chain, no upgrade fired at
  all for months despite an armed target.
- **Cause:** three stacked blockers, found in order. (1) `NDefines.NAI.UPGRADES_DEFICIT_LIMIT_DAYS`
  (90): the AI refuses any field upgrade whose equipment deficit takes longer than that to fill, and
  a training queue that consumes tank production continuously keeps the estimate above ANY such
  limit - new-division training and conversion compete for the same stockpile. (2) The replace_with
  switch has TWO conditions (install `common/ai_templates/_documentation.md`, replace-with section):
  match >= `replace_at_match` AND match(best template, the replace_with target) >= `target_min_match`
  - the second is evaluated against the NEXT target and is the one that silently blocks when the
  compositions differ too much. (3) WA pointed `replace_with` at a template in ANOTHER role group;
  vanilla never does that - its whole light->medium->modern era chain lives inside ONE role
  (`generic.txt`, `target_min_match 0.5`, `replace_at_match 1.5` = prio-driven).
- **Rule:** an era-conversion chain for fielded divisions is built the vanilla shape: every
  `replace_with` resolves to a template declared in the SAME role group, ending at a FINAL step
  whose composition equals the destination role's target; the destination role then captures the
  division by best match. Check `target_min_match` against the REACHABLE intermediate composition
  (shared battalions / total), not against intent. A conversion that must beat a live training
  queue also needs the deficit valve (`UPGRADES_DEFICIT_LIMIT_DAYS`) sized for it.
- **Detection:** live, in `imgui show ai_templates`: a best-match score >= `replace_at_match` with
  the arrow still on the same target is condition (2) or (3) blocking; a correct chain moves the
  arrow to the replace_with target within one `DAYS_BETWEEN_CHECK_BEST_TEMPLATE` (7-day) pass.
  Positive control from the same session: the first hop (old composition -> transition) fires even
  on a role whose role_ratio want is NEGATIVE - want does not gate field upgrades.
- **Evidence:** WORK.md `armor-class-handoff` (conversion half); commits `e75346fea` (valves),
  `d898e2105` (light FINAL chain, owner-confirmed live PASS same day), `e5c497d2f` (light-support
  twin); install `common/ai_templates/_documentation.md` replace-with section; vanilla
  `common/ai_templates/generic.txt` era chain.

### meta_effect inline in an events/ file silently drops the rest of the event body

- **Date:** 2026-08-31 (`dday-mulberry` harness control run, save 1944.6.1)
- **Symptom:** `WA_AI_invasions.101`, rewritten with `meta_effect` blocks directly inside its
  `immediate`, executed its FIRST `if` (the country flag was set, MEASURED in the `wa_mulb.1`
  re-run) and produced nothing else - the following `else` log never printed, no error at fire
  time, no crash. The event looked live and was three-quarters dead.
- **Cause:** ASSUMED (error.log of the failing session not read): the events/ parser desyncs on
  the inline `meta_effect { text = { [TOKEN] = ... } }` block at load and swallows the remainder
  of the event body. The behavioural half is MEASURED both ways: inline in `events/` the body
  after the first if never ran; the same logic moved verbatim into
  `common/scripted_effects/WA_AI_MULBERRY_effects.txt` (with the events reduced to one-line
  callers) printed the expected branch log on the very next run (`1386cf6ea`). The repo had
  only ever used meta_effect in `common/scripted_effects/` - 16 files, zero in `events/`.
- **Rule:** never put `meta_effect` / `meta_trigger` inline in an `events/` file. Put the body
  in a scripted effect and have the event call it - which is editing rule 3 anyway. More
  generally: when an event demonstrably executes its prefix but not its suffix with no runtime
  error, suspect a LOAD-time parse desync inside the body (BOM lesson class), not the runtime
  state, and bisect by moving code out of the file rather than by adding logs to it.
- **Detection:** a flag/variable written by the top of an immediate is set while a log/effect
  lower in the same immediate never fires; the construct sits in a folder where the repo has no
  other instance of it (grep the token across `events/` vs `common/scripted_effects/`).
- **Evidence:** WORK.md `dday-mulberry` (control run FAILED then PASSED bullets); commits
  `a0fe44a81` (inline, broken) -> `1386cf6ea` (scripted-effect bodies, working); game.log
  excerpts pasted in the subject.

### A value-first branch ahead of a template calculator's else_if chain hides the whole chain

- **Date:** 2026-09-02 (`light-support-conversion` Change 7, campaign `5de66942`, owner imgui 1943.1)
- **Symptom:** the Soviet historical tank park held `WA_LIGHT_SUPPORT_ARMOR_TEMPLATE = 15006` on
  every monthly save from 1936.2 to 1945.12 and 31 divisions were still on light-support shapes
  in 1945.12; the conversion rungs 15002-15005 and their medium FINALs, shipped three days
  earlier and reviewed twice, never armed once. `check_templates.py` was green: every value
  had a template and every template a value.
- **Cause:** MEASURED in the script. `42206fcb6` added an `if` that emits 15006 BEFORE the
  existing `if ... else_if` pair; both of those require `_template_value = 0`, and the first
  of them was the only writer of the latch the window trigger reads. One branch placed ahead
  of the chain turned the chain into dead code without touching a line of it, and without
  any join-key mismatch for the checker to see.
- **Rule:** the join-key diff (values emitted vs values enabled) is necessary, not sufficient.
  When a calculator gains a branch, walk the ORDER: list every branch that can set the value,
  in file order, and for each later branch state which earlier branch leaves the value at 0
  for it. A branch that no state reaches is the defect, whatever the checker says. The same
  walk applies to any `if / else_if` ladder gated on a temp variable being unset.
- **Detection:** cross-save `flags` trend — one flag value constant for years while the
  design says the value must move; then `imgui show ai_templates` (arrow never leaves the
  same target) and the harness window bit (`conv-window=0` with the park still fielded).
- **Evidence:** WORK.md `light-support-conversion` Change 7; scratchpad
  `light_to_medium_diagnosis.md` (six boxes); `42206fcb6` (the branch), the fix commit.

### The field-upgrade destination is the FINAL's best EXISTING match, not the FINAL

- **Date:** 2026-09-04 (`light-support-conversion` Change 8, owner imgui + harness on `5de66942` 1943.3)
- **Symptom:** the light-support conversion rung switched correctly onto its 9 medium + 6 mec
  FINAL, and the Soviet light-support divisions turned into HEAVY divisions.
- **Cause:** MEASURED (imgui `Best (all) = Best (role) = "Heavy Tank template A" 0.7353`) plus the
  install doc ("make a copy of the best matching template"): when the arrow lands on a FINAL,
  the engine copies the fielded template that best matches the FINAL and moves the converting
  divisions onto that copy. The heavy target (9 heavy + 6 mec, RS 5+5, the same support set)
  is nearer to a pure 9+6 medium FINAL than the medium role's own target (7 M + 3 SPG + 5 mec,
  RS 3+3, SPG supports). Support companies and regimental supports weigh in the score; the
  battalion type alone does not decide it.
- **Rule:** a conversion FINAL is safe only when its composition IS the destination role's
  CURRENT target, so the best existing match is that role's own template. The destination
  target is a flag value and `replace_with` is static, so it takes one (rung, FINAL) pair per
  destination value (built and parked: `tools/gen_ai_armor_conversion_finals.py` on branch
  `parked/armor-conversion-finals` — the owners judged the ~9 000 generated lines a massive
  complexity increase against the dynamic principles and ACCEPTED the side effect for now: a
  country holding medium + heavy may see converting light divisions land on a heavy template).
- **Detection:** `imgui show ai_templates` on the converting role: `Best (all)` for the FINAL
  names a template of another class, or matches under ~0.9. In a save: divisions of the
  converting role appearing on the OTHER class's battalions (`plans.py --templates`).
- **Evidence:** WORK.md `light-support-conversion` (Change 7 defect + Change 8 decision); the heavy
  target `WA_AI_TEMPLATES_armored_heavy.txt` value 7105 vs medium 6111; the per-value generator on
  branch `parked/armor-conversion-finals` (`e26ab824f`), parked by owner order pending a decision.
