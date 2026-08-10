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

### put_unit_buffers: same order_id means one shared ratio pool, and fronts in the area eat the buffer by default

- **Date:** 2026-08-09
- **Symptom:** Observer campaign 5709c8b9: AI Germany's Atlantic Wall garrison eroded from 31 divisions (Jun 1941) to 3 (Jun 1944) even with the wall `put_unit_buffers` blocks active and forts built — the eastern front absorbed everything and D-Day landed against ~7 defenders (3 GER + 4 RCZ).
- **Cause:** Two stacked engine defaults. (1) All six `atlantik_wall` buffer blocks in `WA_AI_MILITARY_COUNTRY_GER_THEATRE.txt` shared `order_id = 1` with each other *and* with the Balkans/Italy garrison buffers — per `documentation.info`, same order_ids share a single ratio pool, so "0.25" was one pool diluted from Norway to the Balkans, not 0.25 per sector. (2) `subtract_fronts_from_need` defaults to *yes*: front orders in the buffer's `area` subtract from its need, so the moment real fronts existed in France the buffer demand collapsed. The `festung_*` blocks (order_id 2-6, `subtract_fronts_from_need = no`) already encoded the correct pattern.
- **Rule:** When a `put_unit_buffers` garrison must hold against competing front demand, give it its own `order_id` and set `subtract_fronts_from_need = no` explicitly — and remember that with a dedicated order_id the `ratio` becomes "of total armies" for that pool alone, so size it per sector (the 2026-08-09 rebalance: north_france 0.12, benelux 0.06, others 0.05-0.06) rather than copying 0.25 everywhere.
- **Evidence:** Campaign 5709c8b9 division placement per save (31→10→4→3 in the wall states 1941-1944); `common/ai_strategy/documentation.info` lines 199-226; festung blocks in the same file as the working counter-example.

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
