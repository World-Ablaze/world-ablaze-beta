---
name: wa-pdxscript
description: How to read and write Hearts of Iron IV PDXScript correctly in the World Ablaze mod — scopes (ROOT/THIS/PREV/FROM), triggers vs effects, iterators and limit, variables and arrays, indexed `^` variables, file-scoped `@` constants, meta_trigger/meta_effect, and the silent-failure pitfalls. Use this whenever you write or review a `.txt` file under `common/` or `events/`, whenever a trigger or effect "does nothing" with no error, whenever you are unsure which scope a block runs in, and before adding any scripted trigger or scripted effect. PDXScript fails silently and only at game launch, so reason about scope before editing rather than after.
---

# PDXScript in World Ablaze

Deep reference: `documentation/PDXSCRIPT_LANGUAGE_NOTES.md`. This skill is the working subset — the things that cause real bugs.

## The core mental model

PDXScript is nested key/value. `#` starts a comment. The same syntax shape serves triggers (questions), effects (mutations), and data — **context decides which**, and the parser will not tell you when you have mixed them up.

Two failure modes dominate:

- **Wrong scope.** The trigger is valid, but evaluated against a country when it wants a state (or vice versa). Result: silently false, forever.
- **Effect in a trigger block** (or the reverse). Result: ignored, or a parse error visible only in the game log.

Neither shows up in a diff review unless you are explicitly looking for it.

## Triggers vs effects — where each is legal

| Trigger contexts | Effect contexts |
| --- | --- |
| `trigger = {}` in events | `immediate = {}`, `option = {}` in events |
| `allowed = {}`, `enable = {}` in ai_strategy | `effect = {}` in on_actions |
| `available = {}`, `visible = {}` in decisions/focuses | definitions in `common/scripted_effects/` |
| `success = {}`, `fail = {}` in test bundles | |
| `limit = {}` inside an effect control block | |
| definitions in `common/scripted_triggers/` | |

`limit = {}` is the bridge: it is a *trigger* block that lives inside an *effect* block, filtering which items an iterator or `if`/`else_if` acts on.

Both scripted triggers and scripted effects are invoked the same way, which is a genuine readability trap:

```txt
WA_AI_CONFIG_is_major_country = yes    # scripted trigger — asks
WA_AI_train_navy = yes                 # scripted effect — does
```

When you see `SOMETHING = yes` and cannot tell which it is, grep `common/scripted_triggers/` and `common/scripted_effects/` for the definition before assuming.

## Multiple statements are already an AND

```txt
GER = {
	has_war = yes
	num_of_military_factories > 99
}
```

Both must hold. Do not wrap in `AND = {}` unless you need it for clarity inside an `OR`. Use explicit `OR = {}` / `NOT = {}` for anything non-default.

## Comparisons are strict

`>` and `<` are strict; there is no `>=`.

- `date > 1939.8.31` first becomes true on **1939-09-01**.
- `date > 1941.1.1` does **not** include 1941-01-01.
- `num_of_military_factories > 99` means 100 or more.

This is why thresholds in this codebase are written as `> 319` rather than `>= 320`. Follow that; do not "fix" it.

## Scopes

Scope changes by nesting a scope key. Country tags enter country scope; numeric state IDs enter state scope.

```txt
GER = { has_war_with = POL }          # country scope

745 = {                                # state scope
	has_railway_level = { state = THIS level = 5 }
}
```

| Keyword | Means |
| --- | --- |
| `ROOT` | Root scope of the current event or scripted call |
| `THIS` | Current scope |
| `PREV` | Previous scope in the chain |
| `FROM` | Caller/source scope when available |
| `CONTROLLER`, `OWNER`, `capital_scope` | Switch to a specific related scope |

`ROOT`, `THIS`, and `PREV` mean different things depending on the call chain, so a scripted effect that works from one caller can be wrong from another. **Before changing a scope chain, trace every caller.**

Document the expected scope in a comment on any non-obvious scripted trigger or effect — the codebase convention is a one-line header:

```txt
# THIS = STATE
WA_TEST_has_naval_base_at_least_level_7 = {
	any_province_building_level = {
		province = { all_provinces = yes limit_to_coastal = yes }
		building = naval_base
		level > 6
	}
}
```

### The scope trap that bites most often

`every_controlled_state` iterates only states **directly controlled by the current country** — it does **not** include puppet or subject territory, because puppet land is controlled by the puppet. If a system needs to cover an overlord's whole sphere, it must additionally walk `every_subject_country`. Several railway bugs traced back to exactly this; see `wa-lessons-learned`.

## Iteration and filtering

```txt
every_country = {
	limit = { is_ai = yes }
	set_country_flag = WA_AI_research_logging
}

if = {
	limit = { has_war = yes }
	set_variable = { WA_AI_PC_railway_INTERVAL_counter = 0 }
}
```

`every_*` iterates and applies effects; `any_*` is the trigger-side existence check. `limit = {}` filters both, and drives `if` / `else_if` / `else` in effect contexts.

## Variables

Variables are **scope-owned**: a country variable named `X` and a state variable named `X` are unrelated.

```txt
set_variable = { WA_AI_PC_progress^_project_id = 1000 }
set_temp_variable = { _wt_test_id = 6 }
add_to_temp_variable = { _wt_count_passed = 1 }
check_variable = { _wt_elapsed > 120 }
check_variable = { ROOT.WA_AI_PC_building_type^v_proj = _project_building_type }
```

Local conventions:

- Temporaries take a leading underscore: `_wt_test_id`, `_project_id`.
- `^` indexes: `WA_TEST_RW_state^10`, `WA_AI_PC_target_state^_proj`.
- A scope prefix reads across scopes: `ROOT.WA_AI_PC_building_type^v_proj`.
- `global.` reads global variables.
- Clear temp variables and arrays when the surrounding code does. Persistent variables are system state and need a deliberate reason.

## Arrays

WA AI systems keep structured state as an array of IDs plus parallel indexed variables — `WA_AI_PC_queue` holds project IDs, and per-project data lives in `WA_AI_PC_target_state^X`, `WA_AI_PC_building_type^X`, and so on.

```txt
for_each_loop = {
	array = WA_AI_PC_queue
	value = _wt_proj
	if = {
		limit = { check_variable = { WA_AI_PC_building_type^_wt_proj = 13 } }
		add_to_temp_variable = { _wt_railway_count = 1 }
	}
}
```

Commands in use: `add_to_array`, `clear_array`, `clear_temp_array`, `for_each_loop`, `any_of`, `is_in_array`.

When you add a field to such a record, you must add it in **every** place the record is created, copied, and destroyed — a missing clear leaves stale data that the next project silently inherits.

## `@` constants are file-scoped — shared numbers are script constants

```txt
@WA_TLM_VERSION = 17          # `@`: text substitution at parse time, visible in THIS file only
constant:wa_ai_pc.prio.rail_war   # script constant: declared once in common/script_constants/wa_ai_pc.txt,
                                  # readable from every file (HOI4 1.18)
```

`@` constants do **not** cross file boundaries. Since 2026-08-16 the rule is: a number one file
reads may stay `@`; a number two files read is a **script constant** — declare it once in
`common/script_constants/wa_ai_<system>.txt` (`schema = { any_key = yes data = { { any_key = yes data = fixed_point } } }`,
then `group = { key = value }`) and read `constant:wa_ai_<system>.<group>.<key>`. Never redeclare a `@` in a
second file with a "must match" comment — that convention held nothing (the PC affordability gate sat
at 0.35 while the allocator funded at 0.40, Fix 90) and `python tools/check_constants.py` now reports a
`@` shared between two WA files as an error.

Where `constant:` was validated in-game (full table in skill `wa-constants-registry`): every
variable context (`set_/check_/multiply_/clamp_temp_variable`, arrays, `global.`), the raw numeric
triggers the AI uses (`num_of_civilian_factories`, `surrender_progress`, `num_of_controlled_states`,
`has_army_size`, `has_deployed_air_force_size`, `has_manpower`), from scripted_effects /
scripted_triggers / events. **Not** in `ai_strategy value =` (parse error). Untested: `has_country_flag
days >`, `fighting_army_strength_ratio ratio >` — those readers keep `@`. Two traps: the game reloads
`common/script_constants` separately from the scripts (full restart when tuning, `reload` is not
enough), and the folder is a `replace_path` (the mod ships its own file set there).

Cross-format copies (`05_defines.lua`, `00_buildings.txt`, `savegame.py`) cannot read `constant:`;
they are registered in `tools/constants_registry.json` and the checker holds them equal.

## meta_trigger / meta_effect

Use only when a variable must be injected where the engine expects a literal token:

```txt
WA_AI_PC_state_has_railway_at_level = {
	meta_trigger = {
		text = { has_railway_level = { state = THIS level = [x] } }
		x = "[?_check_railway_level]"
	}
}
```

Prefer a concrete helper when one will do — the codebase already ships `WA_AI_PC_state_has_railway_at_level_5` for pure trigger contexts where setting a temp variable is impractical. Meta blocks are harder to read, harder to debug, and cost more at runtime.

## Events and on-actions

```txt
country_event = {
	id = wa_test.100
	hidden = yes
	is_triggered_only = yes

	immediate = {
		if = {
			limit = { has_country_flag = WA_TEST_RW_suite_active }
			WA_TEST_RW_check_all = yes
		}
	}

	option = {}
}
```

Hidden AI background events still need `option = {}`. `is_triggered_only = yes` means something must fire it — usually an on-action. See `wa-ai-systems` for the cadence rules.

## Authoring conventions

- Reusable conditions → `common/scripted_triggers/`. Reusable actions → `common/scripted_effects/`.
- Name a trigger as one positive question: `WA_AI_should_prospect_resource_steel`, not `WA_AI_check_steel`.
- Prefixes: `WA_` gameplay, `WA_AI_` AI systems, `WA_TEST_` test harnesses.
- Tabs, always. Do not reformat neighbouring blocks.
- Comment the expected scope, inputs, and outputs on non-obvious effects.

## Review checklist

- Is every trigger in the scope the surrounding block actually provides?
- Are `>` / `<` boundaries off by the intended day/unit?
- Is an implicit AND doing what you think, or did you mean `OR`?
- Do all temp variables and temp arrays get cleared on every exit path?
- Is every shared number a `constant:` (script constant), every `@` single-file, and does `python tools/check_constants.py` exit 0?
- Do braces balance? (See the PowerShell one-liner in `wa-orientation`.)
- If the file is in a `replace_path` folder, is it complete and parseable — nothing accidentally deleted?
