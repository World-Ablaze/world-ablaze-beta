# PDXScript Language Notes

Research notes for writing and reviewing Hearts of Iron IV PDXScript in World Ablaze.

## Sources Consulted

- `AGENTS.md`
- `descriptor.mod`
- `common/scripted_triggers/WA_AI_CONFIG.txt`
- `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt`
- `common/scripted_triggers/WA_TEST_triggers.txt`
- `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_railway_*.txt`
- `common/scripted_effects/WA_TEST_railway.txt`
- `common/on_actions/WA_AI_misc_on_actions.txt`
- `events/WA_AI_misc.txt`
- `documentation/WA_AI_RAILWAY_SYSTEM.md`
- `documentation/WA_AI_MILITARY_SYSTEM.md`
- External trigger reference: <https://mod-coop-hoi4.fandom.com/wiki/Triggers>
- Official trigger page requested by the user: <https://hoi4.paradoxwikis.com/Triggers> (browser challenge encountered during research)

## Repository Context

World Ablaze is loaded as a HOI4 mod root. The mod replaces many vanilla folders through `replace_path`, including `common/scripted_effects`, `common/scripted_triggers`, `common/on_actions`, `events`, and `tests`. A file in a replaced path can effectively become the source of truth for that content class, so missing or malformed definitions can remove vanilla behavior from the running game.

`AGENTS.md` describes the current project target as game version `1.18.0`, while the local `descriptor.mod` currently has `version="1.10.4"` and `supported_version="1.10.4"`. Treat the descriptor as the runtime metadata unless it is intentionally updated.

## Core Syntax

PDXScript is a nested key/value language:

```txt
key = value
key = {
    nested_key = value
}
```

Values are usually tokens, numbers, dates, booleans, strings, country tags, state IDs, province IDs, variables, arrays, or nested blocks. Comments start with `#`.

Multiple trigger statements inside the same trigger block are implicitly ANDed:

```txt
GER = {
    has_war = yes
    num_of_military_factories > 99
}
```

This means Germany must be at war and have more than 99 military factories. Use explicit boolean blocks for non-default logic:

```txt
OR = {
    has_capitulated = yes
    exists = no
}

NOT = {
    has_idea = relief_of_command_spirit
}
```

Numeric and date comparisons commonly use `>` and `<`. These are strict comparisons. `date > 1939.8.31` becomes true on September 1, 1939 and later.

## Triggers And Effects

Triggers answer a true/false question. Effects mutate game state. The same syntax shape is used for both, so context matters.

Common trigger locations:

- `trigger = { ... }` in events.
- `allowed = { ... }` and `enable = { ... }` in AI strategy.
- `available = { ... }` or `visible = { ... }` in decisions/focuses.
- `success = { ... }` and `fail = { ... }` in test bundles.
- `limit = { ... }` inside an effect control block.
- Definitions in `common/scripted_triggers/*.txt`.

Common effect locations:

- `immediate = { ... }` and `option = { ... }` in events.
- `effect = { ... }` in on-actions.
- Definitions in `common/scripted_effects/*.txt`.

Scripted triggers are reusable trigger blocks:

```txt
WA_AI_CONFIG_is_major_country = {
    OR = {
        original_tag = ENG
        original_tag = FRA
        original_tag = USA
    }
}
```

Use them as:

```txt
WA_AI_CONFIG_is_major_country = yes
```

Scripted effects are reusable effect blocks:

```txt
WA_TEST_ST_suite = {
    log = "[GetYear] [GetMonth] | STATS | [This.GetName] | migrated"
    clr_country_flag = WA_TEST_ST_suite_active
}
```

Use them as:

```txt
WA_TEST_ST_suite = yes
```

In this mod, prefer clear scripted triggers/effects over large inline blocks when logic is reused or difficult to read.

## Scopes

Most HOI4 triggers and effects only work in specific scopes. Common scopes are country, state, unit leader, and province-like helper contexts. PDXScript changes scope by nesting a scope key:

```txt
GER = {
    has_war_with = POL
}

745 = {
    has_railway_level = {
        state = THIS
        level = 5
    }
}
```

Country tags usually enter country scope. Numeric state IDs usually enter state scope. Some scripted triggers document the expected scope in comments, for example:

```txt
# THIS = STATE
WA_TEST_has_naval_base_at_least_level_7 = {
    any_province_building_level = {
        province = {
            all_provinces = yes
            limit_to_coastal = yes
        }
        building = naval_base
        level > 6
    }
}
```

Important scope keywords:

- `ROOT`: the root scope of the current scripted call or event.
- `THIS`: the current scope.
- `PREV`: the previous scope in a scope chain.
- `FROM`: event/caller source scope when available.
- `CONTROLLER`, `OWNER`, `capital_scope`, and similar keys switch to specific related scopes.

Scope mistakes are one of the highest-risk PDXScript bugs. Before using a trigger in a test, confirm whether the assertion runs in country scope, state scope, or global-ish test root scope.

## Iteration And Filters

Common iterator scopes include:

```txt
every_country = {
    limit = { is_ai = yes }
    set_country_flag = WA_AI_research_logging
}

any_enemy_country = {
    original_tag = JAP
}

every_controlled_state = {
    limit = {
        any_neighbor_state = {
            controller = { has_war_with = ROOT }
        }
    }
}
```

`limit = { ... }` filters which items an iterator or conditional block acts on. In effect contexts, `if`, `else_if`, and `else` use `limit`:

```txt
if = {
    limit = { has_war = yes }
    set_variable = { WA_AI_PC_railway_INTERVAL_counter = 0 }
}
```

In a pure trigger block, avoid effect-only commands unless existing code proves they are valid in that context. Some HOI4 trigger contexts allow limited flow control, but test bundle `success` and `fail` should stay simple and side-effect-free.

## Variables

Variables are scope-owned. A country variable is not the same as a state variable with the same name.

Common forms:

```txt
set_variable = { WA_AI_PC_progress^_project_id = 1000 }
set_temp_variable = { _wt_test_id = 6 }
add_to_temp_variable = { _wt_count_passed = 1 }
subtract_from_temp_variable = { _wt_elapsed = WA_TEST_RW_launch_day^_wt_test_id }
check_variable = { _wt_elapsed > 120 }
check_variable = { ROOT.WA_AI_PC_building_type^v_proj = _project_building_type }
```

Patterns seen in WA:

- Temporary variables often use an underscore prefix, such as `_wt_test_id`.
- Indexed variables use `^`, such as `WA_TEST_RW_state^10`.
- Scope prefixes can read variables from another scope, such as `ROOT.WA_AI_PC_building_type^v_proj`.
- Global variables use `global.`.
- Test and AI systems store structured state in arrays and parallel indexed variables.

Clean temporary variables and arrays when local patterns do so. Avoid persistent variables unless they are intentional system state.

## Arrays

Arrays are used heavily in WA AI systems:

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

Common array-related commands in the codebase include `add_to_array`, `clear_array`, `clear_temp_array`, `for_each_loop`, `any_of`, and `is_in_array`. Arrays are often paired with indexed variables. For priority construction, `WA_AI_PC_queue` contains project IDs and related data lives in variables such as `WA_AI_PC_target_state^X`.

## Constants

File-scoped constants use `@`:

```txt
@WA_AI_PC_railway_TYPE_ID = 13
@WA_AI_PC_railway_PRIO = 9999
```

HOI4 `@` constants are file-scoped. If a constant is needed in multiple files, redeclare it where used or initialize shared data as variables. The railway docs call this out explicitly, and the railway files redeclare strategy constants where needed.

## Dynamic Script Construction

WA uses `meta_trigger` and `meta_effect` for cases where the script needs to inject a variable into a place that normally expects a literal token:

```txt
WA_AI_PC_state_has_railway_at_level = {
    meta_trigger = {
        text = {
            has_railway_level = {
                state = THIS
                level = [x]
            }
        }
        x = "[?_check_railway_level]"
    }
}
```

Prefer simpler concrete helper triggers when possible. The construction trigger file provides convenience triggers such as `WA_AI_PC_state_has_railway_at_level_5` for pure trigger contexts where setting temp variables is not practical.

## Events And On-Actions

Events have a standard shape:

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

On-actions schedule recurring work:

```txt
on_actions = {
    on_weekly = {
        effect = {
            # weekly AI work
        }
    }
}
```

For WA AI behavior, trace from on-actions or background events before changing effects. The AI lifecycle and scheduling files decide cadence and performance impact.

## WA Authoring Conventions

Use these local conventions when adding PDXScript:

- `WA_` for gameplay content.
- `WA_AI_` for AI systems.
- `WA_TEST_` for test harnesses and test helper triggers/effects.
- Put reusable conditions in `common/scripted_triggers/`.
- Put reusable actions in `common/scripted_effects/`.
- Keep generic AI country classifications in `WA_AI_CONFIG.txt`.
- For military AI strategy, read `documentation/WA_AI_MILITARY_SYSTEM.md` first and obey the layer/domain split.
- Preserve tabs and local indentation in PDXScript files.
- Do not hand-edit generated map lookup files unless tooling is not viable.
- Document expected scope in comments for non-obvious scripted triggers/effects.

## Common Pitfalls

- A block with multiple triggers is already an AND. Do not wrap in `AND` unless it improves clarity inside an `OR`.
- `=` is exact equality for many trigger comparisons. Use `>` or `<` when checking thresholds.
- `date > 1941.1.1` does not include January 1, 1941 itself.
- State IDs enter state scope; country tags enter country scope.
- `ROOT`, `THIS`, and `PREV` change meaning depending on call chain.
- `@` constants do not cross file boundaries.
- Test bundle trigger blocks should avoid side effects. Use scripted test effects only for custom in-game harnesses, not vanilla `tests/` parity bundles.
- In replaced paths, deleting or omitting content can remove vanilla definitions at runtime.

