# WA AI Division Templates

## Scope

This guide documents how to add or change AI division designs in World Ablaze while keeping research, production, and army-composition behavior aligned.

The division template system is not only the files under `common/ai_templates/`. A complete template change usually touches four layers:

- Country classification and doctrine intent in `common/scripted_triggers/WA_AI_CONFIG.txt`.
- Template selection and unlock checks in `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt` and `common/scripted_effects/WA_AI_TEMPLATES_effects.txt`.
- AI division designs in `common/ai_templates/WA_AI_TEMPLATES_*.txt`.
- Research, production, and army composition triggers in `common/scripted_triggers/WA_AI_RESEARCH_*.txt`, `common/scripted_triggers/WA_AI_PRODUCTION_*.txt`, and matching `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_*.txt` files.

## System Flow

The current flow is:

1. `common/on_actions/WA_AI_startup_on_actions.txt` calls `WA_AI_TEMPLATES_calculate_templates` for every AI country on startup.
2. `common/on_actions/WA_AI_misc_on_actions.txt` calls `WA_AI_TEMPLATES_calculate_templates` monthly for every AI country.
3. `WA_AI_TEMPLATES_calculate_templates` gates default template use through `WA_AI_CONFIG_DIVISIONS_use_default_templates`.
4. `WA_AI_TEMPLATES_calculate_all_templates` calls one calculator per template family.
5. Each calculator sets `_template_type_code` and `_template_value`, then calls `WA_AI_TEMPLATES_update_target_template`.
6. `WA_AI_TEMPLATES_update_target_template` writes country flags such as `WA_INFANTRY_TEMPLATE`, `WA_MEDIUM_ARMOR_TEMPLATE`, or `WA_SUPPRESSION_TEMPLATE` with a numeric value.
7. `common/ai_templates/WA_AI_TEMPLATES_*.txt` enables the matching design through `has_country_flag = { flag = WA_<TYPE>_TEMPLATE value = <VALUE> }`.
8. Research triggers decide which technologies the AI wants before unlocks exist.
9. Template triggers decide whether a template can be selected after unlocks exist.
10. Production triggers and `role_ratio` strategies decide whether the AI builds enough equipment and enough divisions for the selected roles.

Do not skip the research or production layers. A template that selects equipment the AI does not research or produce will appear valid in script but fail in-game.

## Source Of Truth

| Concern | File | Rule |
| --- | --- | --- |
| Country archetypes and tag lists | `common/scripted_triggers/WA_AI_CONFIG.txt` | Put generic country classification here, not in template, research, or production files. ITS THE ONLY PLACE WHERE COUNTRY TAGS ARE ALLOWED !!! |
| Template selection conditions | `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt` | Use `WA_AI_TEMPLATES_use_*` for desired roles and `WA_AI_TEMPLATES_has_*_unlocked` for researched equipment checks. |
| Template value calculation | `common/scripted_effects/WA_AI_TEMPLATES_effects.txt` | Map country state to one active numeric template value per template family. |
| Template definitions | `common/ai_templates/WA_AI_TEMPLATES_*.txt` | Add the actual AI design under the correct role file. |
| Research demand | `common/scripted_triggers/WA_AI_RESEARCH_*.txt` | Use `WA_AI_RESEARCH_needs_*` triggers based on strategic desire, not unlock state. |
| Technology `ai_will_do` | `common/technologies/*.txt` and `tools/ai_will_do_replacer_all.py` | Preserve generated `ai_will_do` conventions and use dry-run tooling before applying generated changes. |
| Equipment production demand | `common/scripted_triggers/WA_AI_PRODUCTION_ground.txt` and `common/scripted_triggers/WA_AI_PRODUCTION_tanks.txt` | Use production triggers as one-line gates for `ai_strategy` files. |
| Army composition | `common/scripted_triggers/WA_AI_PRODUCTION_army_composition.txt` and `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_army_composition.txt` | Keep `role_ratio` changes additive and balanced against infantry. |

## Template Value Ranges

Keep numeric values inside the existing family ranges. The value is stored on the country flag and matched by `enable` blocks in `common/ai_templates/`.

| Family | Value Range | Flag | Type Code |
| --- | ---: | --- | ---: |
| Infantry | `1000-1999` | `WA_INFANTRY_TEMPLATE` | `1` |
| Mountaineers | `2000-2999` | `WA_MOUNTAINEERS_TEMPLATE` | `11` |
| Motorized | `3000-3999` | `WA_MOTORIZED_TEMPLATE` | `2` |
| Mechanized | `4000-4999` | `WA_MECHANIZED_TEMPLATE` | `3` |
| Light Armor | `5000-5999` | `WA_LIGHT_ARMOR_TEMPLATE` | `4` |
| Medium Armor | `6000-6999` | `WA_MEDIUM_ARMOR_TEMPLATE` | `5` |
| Heavy Armor | `7000-7999` | `WA_HEAVY_ARMOR_TEMPLATE` | `6` |
| Modern Armor | `8000-8999` | `WA_MODERN_ARMOR_TEMPLATE` | `7` |
| Garrison | `9000-9999` | `WA_GARRISON_TEMPLATE` | `8` |
| Marines | `10000-10999` | `WA_MARINES_TEMPLATE` | `9` |
| Airborne | `11000-11999` | `WA_AIRBORNE_TEMPLATE` | `10` |
| Rangers | `13000-13999` | `WA_RANGERS_TEMPLATE` | `12` |
| Suppression | `14000-14999` | `WA_SUPPRESSION_TEMPLATE` | `13` |

Airborne and rangers currently have reserved type codes in `common/scripted_localisation/WA_AI_templates_scripted_loc.txt`, but no active calculator or `common/ai_templates/WA_AI_TEMPLATES_<family>.txt` file in the current system. Treat them as new families if implementing them.

When adding a new value, first search the matching `WA_AI_TEMPLATES_<family>.txt` file and the calculator in `WA_AI_TEMPLATES_effects.txt` to avoid collisions.

## Naming Conventions

Use the existing AI template naming pattern:

```txt
WA_AI_TEMPLATES_GENERIC_[TEMPLATE_TYPE]_[WIDTH]_[COMPOSITION]_[MOTORIZATION]
```

Common tokens:

- Width: `20`, `30`, or another combat width already used by the family.
- Composition: `INF`, `MIX`, `MOT`, `MEC`, `MAR`, or the closest existing family token.
- Motorization: `HRS` for horse-drawn or foot support, `MOT` for motorized support.

Preserve the top-level role naming convention in `common/ai_templates/`:

- `WA_infantry_role` uses `role = infantry`.
- `WA_medium_armor_role` uses `role = medium_armor`.
- Match `role` with the role used by `role_ratio` strategies in `WA_AI_PRODUCTION_DEFAULT_army_composition.txt`.

## Add A Variant To An Existing Family

Use this workflow when the role already exists, for example adding a new medium armor template value `6004`.

1. Add the AI design under the matching role file in `common/ai_templates/WA_AI_TEMPLATES_<family>.txt`.
2. Use an `enable` block that checks the family flag and new numeric value.
3. Add selection logic in the matching calculator in `common/scripted_effects/WA_AI_TEMPLATES_effects.txt`.
4. Add or reuse a `WA_AI_TEMPLATES_use_*` trigger if the selection condition is reusable.
5. Add or reuse a `WA_AI_TEMPLATES_has_*_unlocked` trigger for any equipment that must exist before selection.
6. Make sure the AI researches the required technologies through `WA_AI_RESEARCH_needs_*` triggers and technology `ai_will_do` blocks.
7. Make sure the AI produces the required equipment through `WA_AI_PRODUCTION_build_*` triggers and matching production strategies.
8. Make sure the AI builds divisions of that role through `WA_AI_PRODUCTION_build_army_*` and `role_ratio` strategies.

Minimal template block pattern:

```txt
WA_AI_TEMPLATES_GENERIC_MEDIUM_ARMOR_30_MEC_MOT = {
	enable = { has_country_flag = { flag = WA_MEDIUM_ARMOR_TEMPLATE value = 6004 } } upgrade_prio = { base = 10 }
	reinforce_prio = 1
	custom_icon = 140
	can_upgrade_in_field = { always = yes }
	upgrade_prio = { base = 10 }
	target_template = {
		regiments = {
			medium_armor = 8
			mechanized = 7
		}
		support = {
			armored_engineer = 1
			heavy_maintenance_company = 1
			armoured_recon = 1
			mot_field_hospital = 1
			mot_signal_company = 1
			mot_logistics_company = 1
			heavy_artillery = 1
			mot_anti_tank = 1
			mot_military_police = 1
			mot_anti_air = 1
		}
	}
}
```

Minimal calculator pattern:

```txt
WA_AI_TEMPLATES_calculate_medium_armor_template = {
	set_temp_variable = { _template_type_code = 5 }
	set_temp_variable = { _template_value = 0 }
	if = {
		limit = {
			WA_AI_TEMPLATES_use_medium_armor_templates = yes
		}
		if = {
			limit = {
				WA_AI_TEMPLATES_has_new_required_equipment_unlocked = yes
			}
			set_temp_variable = { _template_value = 6004 }
		}
		else = {
			set_temp_variable = { _template_value = 6001 }
		}
	}
	WA_AI_TEMPLATES_update_target_template = yes
}
```

Only use one final `_template_value` per family. The current system clears and rewrites one country flag value per family; it does not select multiple active variants for the same role at the same time.

## Add A New Template Family

Adding a new family is larger and should be rare. Prefer extending an existing family unless the role needs a distinct `role_ratio` and country flag.

Required changes:

1. Reserve a numeric range in the header of `WA_AI_TEMPLATES_effects.txt` and this document.
2. Add a type-code mapping to `common/scripted_localisation/WA_AI_templates_scripted_loc.txt` if the meta-effect mapping does not already support the new `WA_[TYPE]_TEMPLATE` flag.
3. Add a `WA_AI_TEMPLATES_calculate_<family>_template` effect.
4. Call it from `WA_AI_TEMPLATES_calculate_all_templates`.
5. Add blocking behavior to `WA_AI_TEMPLATES_block_all_templates` if it should be suppressed during doctrine-spirit gating.
6. Add `WA_AI_TEMPLATES_use_<family>` and any `WA_AI_TEMPLATES_has_<equipment>_unlocked` triggers.
7. Add `common/ai_templates/WA_AI_TEMPLATES_<family>.txt` with the top-level role and enabled variants.
8. Add army composition trigger and `role_ratio` strategy for the new role.
9. Add research and production triggers for all new equipment dependencies.

Do not add country tag checks directly in the new family unless the behavior is truly country-specific and belongs in a country file. Generic country groupings belong in `WA_AI_CONFIG.txt`.

## Trigger Responsibilities

### Config Triggers

`WA_AI_CONFIG_DIVISIONS_*` triggers describe country identity or strategic intent.

Use them for:

- Country archetypes, such as armor users, mechanized users, or mountain-war countries.
- Doctrine or equipment focus, such as light, medium, or heavy armor focus.
- Broad support preferences, such as line support, anti-tank, anti-air, or rocket artillery.
- System switches, such as `WA_AI_CONFIG_DIVISIONS_use_default_templates`, `WA_AI_CONFIG_uses_default_ground_production`, `WA_AI_CONFIG_uses_default_tanks_production`, and `WA_AI_CONFIG_uses_default_army_composition`.

Current division config triggers:

- `WA_AI_CONFIG_DIVISIONS_use_armored_divisions`
- `WA_AI_CONFIG_DIVISIONS_use_motorized_divisions`
- `WA_AI_CONFIG_DIVISIONS_use_mechanized_divisions`
- `WA_AI_CONFIG_DIVISIONS_use_default_templates`
- `WA_AI_CONFIG_DIVISIONS_is_expected_marshes_or_mountains`
- `WA_AI_CONFIG_DIVISIONS_use_line_support`
- `WA_AI_CONFIG_DIVISIONS_has_access_to_oil`
- `WA_AI_CONFIG_DIVISIONS_can_motorize_support`
- `WA_AI_CONFIG_DIVISIONS_focus_on_heavy_armor`
- `WA_AI_CONFIG_DIVISIONS_focus_on_medium_armor`
- `WA_AI_CONFIG_DIVISIONS_focus_on_light_armor`
- `WA_AI_CONFIG_DIVISIONS_force_mountainneers_instead_of_marines`
- `WA_AI_CONFIG_DIVISIONS_use_armored_cars`
- `WA_AI_CONFIG_DIVISIONS_use_heavy_artillery`
- `WA_AI_CONFIG_DIVISIONS_use_anti_tank_brigades`
- `WA_AI_CONFIG_DIVISIONS_use_anti_air_brigades`
- `WA_AI_CONFIG_DIVISIONS_use_rocket_artillery`
- `WA_AI_CONFIG_DIVISIONS_use_tank_destroyers`
- `WA_AI_CONFIG_DIVISIONS_use_self_propelled_artillery`
- `WA_AI_CONFIG_DIVISIONS_use_self_propelled_aa`

### Template Use Triggers

`WA_AI_TEMPLATES_use_*` triggers decide whether a role should be selected.

Current role-selection triggers:

- `WA_AI_TEMPLATES_use_heavy_infantry`
- `WA_AI_TEMPLATES_use_suppression_templates`
- `WA_AI_TEMPLATES_use_marines`
- `WA_AI_TEMPLATES_use_mountaineers`
- `WA_AI_TEMPLATES_use_motorized_templates`
- `WA_AI_TEMPLATES_use_mechanized_templates`
- `WA_AI_TEMPLATES_use_armor_templates`
- `WA_AI_TEMPLATES_use_heavy_armor_templates`
- `WA_AI_TEMPLATES_use_medium_armor_templates`
- `WA_AI_TEMPLATES_use_light_armor_templates`
- `WA_AI_TEMPLATES_use_modern_armor`
- `WA_AI_TEMPLATES_switch_from_light_to_medium_armor`

These triggers may call config triggers and unlock triggers. Keep them positive and reusable: `WA_AI_TEMPLATES_use_medium_armor_templates` is better than `WA_AI_TEMPLATES_do_not_use_light_armor`.

### Template Unlock Triggers

`WA_AI_TEMPLATES_has_*_unlocked` triggers check actual researched equipment availability.

Current unlock trigger groups:

- Base chassis and equipment: `WA_AI_TEMPLATES_has_light_armor_unlocked`, `WA_AI_TEMPLATES_has_medium_armor_unlocked`, `WA_AI_TEMPLATES_has_heavy_armor_unlocked`, `WA_AI_TEMPLATES_has_modern_armor_unlocked`, `WA_AI_TEMPLATES_has_mechanized_unlocked`, `WA_AI_TEMPLATES_has_amphibious_mechanized_unlocked`.
- Ground support equipment: `WA_AI_TEMPLATES_has_heavy_at_unlocked`, `WA_AI_TEMPLATES_has_heavy_aa_unlocked`.
- Mechanized variants: `WA_AI_TEMPLATES_has_mechanized_at_unlocked`, `WA_AI_TEMPLATES_has_mechanized_aa_unlocked`.
- Tank destroyers: `WA_AI_TEMPLATES_has_light_td_unlocked`, `WA_AI_TEMPLATES_has_medium_td_unlocked`, `WA_AI_TEMPLATES_has_heavy_td_unlocked`, `WA_AI_TEMPLATES_has_modern_td_unlocked`.
- Self-propelled artillery: `WA_AI_TEMPLATES_has_light_spg_unlocked`, `WA_AI_TEMPLATES_has_medium_spg_unlocked`, `WA_AI_TEMPLATES_has_heavy_spg_unlocked`, `WA_AI_TEMPLATES_has_modern_spg_unlocked`.
- Self-propelled anti-air: `WA_AI_TEMPLATES_has_light_spaa_unlocked`, `WA_AI_TEMPLATES_has_medium_spaa_unlocked`, `WA_AI_TEMPLATES_has_modern_spaa_unlocked`.
- Doctrine-spirit gating: `WA_AI_TEMPLATES_has_any_academy_spirit`, `WA_AI_TEMPLATES_has_required_spirits`.

When a template uses a new equipment archetype, add an unlock trigger here and include every country-specific tech that unlocks that equipment. Do not gate research demand on these unlock triggers, because that creates circular logic.

### Research Triggers

`WA_AI_RESEARCH_needs_*` triggers decide whether the AI should want a technology. They are used inside technology `ai_will_do` blocks.

Important rule: research triggers must be based on strategic desire or country config, not on whether the equipment is already researched. For example, `WA_AI_RESEARCH_needs_mechanized` can use `WA_AI_CONFIG_DIVISIONS_use_mechanized_divisions`, but should not require `WA_AI_TEMPLATES_has_mechanized_unlocked`.

Land-template-relevant research triggers:

- Infantry and artillery: `WA_AI_RESEARCH_needs_infantry_weapons`, `WA_AI_RESEARCH_needs_line_artillery`, `WA_AI_RESEARCH_needs_pack_artillery`, `WA_AI_RESEARCH_needs_heavy_artillery`, `WA_AI_RESEARCH_needs_anti_tank`, `WA_AI_RESEARCH_needs_anti_air`, `WA_AI_RESEARCH_needs_rocket_artillery`, `WA_AI_RESEARCH_needs_marines`, `WA_AI_RESEARCH_needs_mountaineers`, `WA_AI_RESEARCH_needs_paratroopers`.
- Support: `WA_AI_RESEARCH_needs_support`, `WA_AI_RESEARCH_needs_engineer_company`, `WA_AI_RESEARCH_needs_recon_company`, `WA_AI_RESEARCH_needs_military_police`, `WA_AI_RESEARCH_needs_maintenance_company`, `WA_AI_RESEARCH_needs_field_hospitals`, `WA_AI_RESEARCH_needs_logistics_company`, `WA_AI_RESEARCH_needs_signal_company`, `WA_AI_RESEARCH_needs_camo`.
- Tanks and mobile: `WA_AI_RESEARCH_needs_light_armor`, `WA_AI_RESEARCH_needs_medium_armor`, `WA_AI_RESEARCH_needs_heavy_armor`, `WA_AI_RESEARCH_needs_modern_armor`, `WA_AI_RESEARCH_needs_trucks`, `WA_AI_RESEARCH_needs_mechanized`, `WA_AI_RESEARCH_needs_tank_destroyers`, `WA_AI_RESEARCH_needs_self_propelled_artillery`, `WA_AI_RESEARCH_needs_self_propelled_aa`, `WA_AI_RESEARCH_needs_armored_cars`.

The monthly on-action also calls `WA_AI_RESEARCH_check_for_empty_research_slots`, which sets `WA_AI_unused_research_slots` and `WA_AI_unused_research_slots_extended`. Existing generated `ai_will_do` blocks use those flags to relax date penalties when the AI has idle slots.

### Production Triggers

Production triggers are one-line gates for `ai_strategy` files. Keep country tags and complex country group logic out of `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_*.txt`; put that logic in triggers.

Ground production triggers:

- Master: `WA_AI_PRODUCTION_ground_is_enabled`.
- Infantry: `WA_AI_PRODUCTION_build_infantry_base`, `WA_AI_PRODUCTION_build_heavy_infantry`, `WA_AI_PRODUCTION_build_infantry_stockpile_low`.
- Artillery: `WA_AI_PRODUCTION_build_artillery`, `WA_AI_PRODUCTION_build_artillery_major`.
- Anti-tank: `WA_AI_PRODUCTION_build_anti_tank`, `WA_AI_PRODUCTION_build_heavy_anti_tank`.
- Anti-air: `WA_AI_PRODUCTION_build_anti_air`, `WA_AI_PRODUCTION_build_heavy_anti_air`.
- Trucks and trains: `WA_AI_PRODUCTION_build_trucks`, `WA_AI_PRODUCTION_build_trucks_stockpile_low`, `WA_AI_PRODUCTION_build_trucks_stockpile_very_low`, `WA_AI_PRODUCTION_build_trains`, `WA_AI_PRODUCTION_build_trains_reduce_factor`.

Tank and mechanized production triggers:

- Master: `WA_AI_PRODUCTION_tanks_is_enabled`.
- Light armor: `WA_AI_PRODUCTION_build_light_armor`, `WA_AI_PRODUCTION_build_medium_armor_in_replacement_of_light_armor`, `WA_AI_PRODUCTION_build_light_armor_td`, `WA_AI_PRODUCTION_build_light_armor_spg`, `WA_AI_PRODUCTION_build_light_armor_spaa`.
- Medium armor: `WA_AI_PRODUCTION_build_medium_armor`, `WA_AI_PRODUCTION_build_medium_armor_td`, `WA_AI_PRODUCTION_build_medium_armor_spg`, `WA_AI_PRODUCTION_build_medium_armor_spaa`.
- Heavy armor: `WA_AI_PRODUCTION_build_heavy_armor`, `WA_AI_PRODUCTION_build_heavy_armor_td`, `WA_AI_PRODUCTION_build_heavy_armor_spg`.
- Modern armor: `WA_AI_PRODUCTION_build_modern_armor`, `WA_AI_PRODUCTION_build_modern_armor_td`, `WA_AI_PRODUCTION_build_modern_armor_spg`, `WA_AI_PRODUCTION_build_modern_armor_spaa`.
- Mechanized: `WA_AI_PRODUCTION_build_mechanized`, `WA_AI_PRODUCTION_build_mechanized_td`, `WA_AI_PRODUCTION_build_mechanized_aa`.
- Armor focus: `WA_AI_PRODUCTION_focus_on_light_armor`, `WA_AI_PRODUCTION_focus_on_medium_armor`, `WA_AI_PRODUCTION_focus_on_heavy_armor`.

Army composition triggers:

- Master: `WA_AI_PRODUCTION_army_composition_is_enabled`.
- Armor: `WA_AI_PRODUCTION_build_army_light_armor`, `WA_AI_PRODUCTION_build_army_medium_armor`, `WA_AI_PRODUCTION_build_army_heavy_armor`, `WA_AI_PRODUCTION_build_army_modern_armor`.
- Mobile: `WA_AI_PRODUCTION_build_army_motorized`, `WA_AI_PRODUCTION_build_army_mechanized`.
- Special forces: `WA_AI_PRODUCTION_build_army_marines`, `WA_AI_PRODUCTION_build_army_mountaineers`.
- Garrison and support: `WA_AI_PRODUCTION_build_army_garrison`, `WA_AI_PRODUCTION_build_army_cavalry`.

In `WA_AI_PRODUCTION_DEFAULT_army_composition.txt`, keep role-ratio strategies additive. The current base is infantry `100`; each role modifier subtracts from infantry and adds the same amount to the new role.

## Technology `ai_will_do` Workflow

Technology `ai_will_do` blocks are tool-managed. Before changing them manually, check whether the relevant replacer already supports the file.

Use dry-run first from `tools/`:

```powershell
python ai_will_do_replacer_all.py
python ai_will_do_replacer_all.py --type infantry
python ai_will_do_replacer_all.py --type support
python ai_will_do_replacer_all.py --type armor
```

Apply only after reviewing the dry-run output:

```powershell
python ai_will_do_replacer_all.py --type armor --apply
```

When adding a new research trigger, update the appropriate parser mapping documented in `tools/REFACTORING_SUMMARY.md`:

- `tools/ai_will_do_replacer_infantry.py` for infantry and special forces.
- `tools/ai_will_do_replacer_support.py` for support companies.
- `tools/ai_will_do_replacer_armor.py` for armor and mechanized.

Update the parser methods that apply:

- `get_archetype_mappings()` for equipment archetypes.
- `get_category_mappings()` for technology categories.
- `get_name_patterns()` for fallback name matching.

## Complete Checklist

Use this checklist for every new AI template or major template change.

1. Pick the correct existing family and numeric range.
2. Add the `target_template` block in `common/ai_templates/WA_AI_TEMPLATES_<family>.txt`.
3. Add calculator selection in `WA_AI_TEMPLATES_effects.txt`.
4. Add or reuse a positive `WA_AI_TEMPLATES_use_*` trigger.
5. Add or reuse `WA_AI_TEMPLATES_has_*_unlocked` triggers for required researched equipment.
6. Add or reuse `WA_AI_CONFIG_DIVISIONS_*` triggers for country archetypes and tag lists.
7. Add or reuse `WA_AI_RESEARCH_needs_*` triggers for every required technology family.
8. Update technology `ai_will_do` tooling mappings if a new trigger must be emitted into tech files.
9. Add or reuse `WA_AI_PRODUCTION_build_*` triggers for every required equipment type.
10. Add or reuse `equipment_variant_production_factor` or `equipment_production_min_factories_archetype` strategies in the matching `WA_AI_PRODUCTION_DEFAULT_*.txt` file.
11. Add or reuse `WA_AI_PRODUCTION_build_army_*` and `role_ratio` strategies if the role should appear in army composition.
12. Check that early-game override behavior is respected through `WA_AI_CONFIG_early_game_army_expansion_override` where appropriate.
13. Check that doctrine-spirit gating still behaves correctly for countries with T1 land doctrine.
14. Run dry-run tooling for generated `ai_will_do` changes if technologies were touched.
15. Manually inspect brace balance, flag values, role names, and equipment archetype IDs.

## Common Failure Modes

- Adding a template value in `common/ai_templates/` without setting that value in `WA_AI_TEMPLATES_effects.txt`; the design never enables.
- Selecting a template before equipment unlocks exist; the AI tries to use equipment it cannot build.
- Gating research demand on unlock triggers; the AI never researches the unlock because it first needs the unlock.
- Adding country tag checks in production or template files instead of `WA_AI_CONFIG.txt`; behavior becomes duplicated and hard to audit.
- Adding a new role without a `role_ratio`; the template exists but the AI may not build divisions for it.
- Adding equipment to a template without production strategies; the AI builds divisions but lacks equipment stockpile.
- Reformatting generated or parser-managed `ai_will_do` blocks; this creates noisy diffs and can break future generator passes.
- Forgetting that `@` constants are file-scoped in HOI4 script; redeclare constants where needed or store shared values through initialization.

## Validation

There is no cheap parser validation that catches every HOI4 script issue. Use the strongest practical validation for the files touched.

For template-only changes:

- Search for duplicate numeric values in the family file.
- Check every `enable` flag has a matching calculator value.
- Check every calculator path ends with `WA_AI_TEMPLATES_update_target_template = yes`.
- Check the role name matches the `role_ratio` strategy ID.

For research changes:

- Run the relevant `ai_will_do` replacer in dry-run mode from `tools/`.
- Review generated diffs before applying.
- Preserve nested modifiers, date modifiers, and indentation.

For production changes:

- Check each `WA_AI_PRODUCTION_build_*` trigger has a matching enabled strategy.
- Check production trigger names use the `PRODUCTION` suffix and remain one-line in strategy files.
- Check army composition remains balanced: infantry loses the same value the new role gains.

For in-game validation:

- Launch with an AI country that should use the new template.
- Confirm the expected `WA_<TYPE>_TEMPLATE` flag value appears after startup or monthly recalculation.
- Confirm required technologies are prioritized before the template unlock point.
- Confirm equipment production lines appear before the AI starts fielding the design.
