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

- **Date:** 2026-08-08 (recorded)
- **Symptom:** A threshold changed in one file had no effect on the scheduling gate.
- **Cause:** HOI4 `@` constants are file-scoped. `WA_AI_misc_on_actions.txt` redeclares `@WA_AI_PC_railway_MIN_CIVS_PEACE`, `_MIN_STATES`, `_MAX_SURRENDER`, `_MINOR_CIV_THRESHOLD` because the on-action needs them and cannot see the core file's copies.
- **Rule:** Before changing any `@` constant, grep its name across the repo and update every declaration. When adding a constant that a second file will need, redeclare it there with a `# must match <file>` comment — that is the established convention, not an accident.
- **Evidence:** `common/on_actions/WA_AI_misc_on_actions.txt:5-9` ("must match WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt").

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

## Working in this repo

### Match tabs exactly when editing

- **Date:** 2026-08-08 (recorded)
- **Symptom:** Edits failing to apply, or applying with broken indentation.
- **Cause:** PDXScript here is tab-indented; string-matching edits that assume spaces do not match, and mixed indentation breaks the visual structure reviewers rely on.
- **Rule:** Copy the exact whitespace from the file when constructing an edit, include enough surrounding context to be unique, and never reformat blocks you are not changing — especially generated or parser-managed `ai_will_do` sections.
- **Evidence:** Repository-wide convention; `AGENTS.md` editing rule 12.
