# HOI4 Tests And Trigger Notes

Research notes for writing automated tests in the built-in Hearts of Iron IV mod test framework.

## Sources Consulted

- `tests/_documentation.info`
- `tests/wa_railway_strict_parity.txt`
- `tests/wa_spirits_strict_parity.txt`
- `tests/wa_stats_strict_parity.txt`
- `common/scripted_triggers/WA_TEST_triggers.txt`
- `common/scripted_effects/WA_TEST_railway.txt`
- `common/scripted_effects/WA_TEST_spirits.txt`
- `common/scripted_effects/WA_TEST_stats.txt`
- `events/wa_events_test.txt`
- `documentation/WA_AI_RAILWAY_SYSTEM_TEST_CASES.md`
- Vanilla examples in `C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\tests\`
- External trigger reference: <https://mod-coop-hoi4.fandom.com/wiki/Triggers>
- Official trigger page requested by the user: <https://hoi4.paradoxwikis.com/Triggers> (browser challenge encountered during research)

## Test Bundle Shape

Each file in `tests/` is a separate test bundle:

```txt
last_date = 1948.1.1

tests = {
    test_name = {
        success = {
            # trigger block
        }

        fail = {
            # trigger block
        }
    }
}
```

`last_date` ends the whole bundle and causes a final report to be logged. The game writes test output to the user profile HOI4 directory under:

```txt
logs/tests/tests_<timestamp>.log
```

`last_date` should be 1946.1.1 for all WA WW2 tests.

Each named test is continuously evaluated until either `success` or `fail` becomes true enough times to satisfy `run_count`. `run_count` defaults to `1`, and vanilla examples almost never override it. `run_count = -1` means the test never stops evaluating, but no shipped vanilla test example found during research uses that outside the documentation comment.

## Success And Fail Blocks

`success` and `fail` are trigger blocks. Multiple statements inside each block are implicitly ANDed.

When `success` becomes true, the test reports success and stops evaluating for the default single run. When `fail` becomes true, the test reports failure, stops evaluating for the default single run, and writes a save named like:

```txt
TEST_FAIL_<test-name>_<game-date>.hoi4
```

Good tests make `success` and `fail` mutually exclusive or at least order-independent. Avoid writing both blocks so they can become true on the same date for the same game state.

## Optional Fields

`acceptable_fail_rate` defaults to `0`. Use it only for tests with accepted randomness across repeated overnight or multi-machine runs:

```txt
acceptable_fail_rate = 0.2
```

Vanilla uses this for stochastic AI behavior such as invasion timing or faction outcomes. For deterministic WA parity tests, omit it.

`run_count` defaults to `1`. Omit it for ordinary regression and parity tests.

`loggers` can add extra diagnostic output, but local documentation is sparse. The user requested ignoring loggers for now, and the current WA parity tests omit them.

## Naming Pattern

The vanilla docs recommend naming the test for what failed. Examples:

```txt
GER_didnt_defeat_france = { ... }
ENG_hasnt_50_mills_by_1941 = { ... }
```

Current WA parity tests follow a more structured prefix plus failure phrase:

```txt
WA_SP_ENG_missing_relief_of_command_spirit
WA_ST_GER_CP1_civs_or_mils_below_threshold_at_1939_9_1
WA_RW_011_dalian_beijing_route_not_level_5_after_1939
```

This is useful because failure logs read naturally: the named condition is what went wrong.

## Two Main Test Patterns

### Deadline Achievement

Use this when the AI or game state must accomplish something by a deadline.

```txt
GER_didnt_defeat_france = {
    success = {
        date > 1939.1.1
        date < 1941.1.1
        FRA = { has_capitulated = yes }
    }

    fail = {
        date > 1941.1.1
    }
}
```

This passes as soon as France capitulates in the allowed window. It fails after the deadline.

### Invariant Guard

Use this when a bad state must never happen before a cutoff date.

```txt
ENG_has_fallen = {
    success = {
        date > 1945.1.1
    }

    fail = {
        date < 1945.1.1
        ENG = {
            OR = {
                has_capitulated = yes
                is_subject = yes
                exists = no
            }
        }
    }
}
```

This passes by surviving until the cutoff. It fails immediately if the forbidden condition occurs before then.

## WA Parity Test Pattern

The current migrated WA tests are strict snapshot/assertion bundles. They assert a condition after a specific date and make the fail block the logical inverse at the same date.

```txt
WA_SP_ENG_missing_relief_of_command_spirit = {
    success = {
        date > 1937.1.1
        ENG = { has_idea = relief_of_command_spirit }
    }
    fail = {
        date > 1937.1.1
        ENG = { NOT = { has_idea = relief_of_command_spirit } }
    }
}
```

This pattern is strong for deterministic state checks. It resolves on the first evaluation after the date gate.

Stats tests use the same structure with threshold inverses:

```txt
success = {
    date > 1939.8.31
    GER = {
        num_of_civilian_factories > 319
        num_of_military_factories > 299
    }
}

fail = {
    date > 1939.8.31
    GER = {
        OR = {
            NOT = { num_of_civilian_factories > 319 }
            NOT = { num_of_military_factories > 299 }
        }
    }
}
```

Railway tests use state scope and helper triggers:

```txt
success = {
    date > 1938.12.31
    745 = { WA_TEST_has_naval_base_at_least_level_7 = yes }
}

fail = {
    date > 1938.12.31
    745 = { NOT = { WA_TEST_has_naval_base_at_least_level_7 = yes } }
}
```

## Trigger Authoring For Tests

Test `success` and `fail` can use normal HOI4 triggers plus scripted triggers. Existing vanilla examples use:

- `date > 1940.1.1`
- `threat > 0.99`
- `TAG = { has_war_with = OTHER }`
- `TAG = { has_capitulated = yes }`
- `TAG = { exists = yes/no }`
- `TAG = { is_subject = yes }`
- `TAG = { is_in_faction_with = OTHER }`
- `TAG = { num_of_military_factories > 49 }`
- `state_id = { is_controlled_by = TAG }`
- `state_id = { controller = { is_in_faction_with = TAG } }`
- `any_state = { region = 208 controller = { tag = FRA } }`

The external trigger reference confirms the general rules:

- Trigger scopes have a context such as country or state.
- Country tags scope into country context.
- State IDs scope into state context.
- `AND`, `OR`, and `NOT` are execution scopes.
- Trigger blocks are AND by default.
- `>` and `<` are strict numeric/date comparisons.

## Helper Triggers

When a test needs a repeated or scope-sensitive assertion, add a helper under `common/scripted_triggers/` with a clear expected scope comment.

Current example:

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

For railway level checks, WA already has convenience triggers:

```txt
WA_AI_PC_state_has_railway_at_level_5 = {
    has_railway_level = {
        state = THIS
        level = 5
    }
}
```

Prefer helper triggers when:

- The same assertion appears in multiple tests.
- The trigger needs state scope or country scope clarity.
- The underlying native trigger requires a verbose block.
- The assertion may later need a bug fix in one place.

Avoid helper triggers when a single inline check is clearer.

## Choosing Dates

Use exact dates that match the design expectation:

- `date > 1938.12.31` means January 1, 1939 or later.
- `date > 1939.8.31` means September 1, 1939 or later.
- If checking a state at a deadline, use the same date gate in success and fail.
- If checking a window, put both lower and upper bounds in `success` and a later hard deadline in `fail`.

Be careful with immediate inverses on the same date. If the condition can legitimately become true later, a same-date inverse fail block will fail too early. Use a later deadline fail instead.

## Scope Recipes

Country assertion:

```txt
USA = {
    has_idea = relief_of_command_spirit
}
```

State controller assertion:

```txt
446 = {
    is_controlled_by = ENG
}
```

State controlled by faction member:

```txt
451 = {
    OR = {
        is_controlled_by = ENG
        controller = { is_in_faction_with = ENG }
    }
}
```

Country missing one of several required values:

```txt
GER = {
    OR = {
        NOT = { num_of_civilian_factories > 319 }
        NOT = { num_of_military_factories > 299 }
    }
}
```

Route with alternative acceptable states:

```txt
OR = {
    608 = { WA_AI_PC_state_has_railway_at_level_5 = yes }
    949 = { WA_AI_PC_state_has_railway_at_level_5 = yes }
}
```

Inverse of that alternative:

```txt
AND = {
    608 = { NOT = { WA_AI_PC_state_has_railway_at_level_5 = yes } }
    949 = { NOT = { WA_AI_PC_state_has_railway_at_level_5 = yes } }
}
```

## Built-In Tests Versus Scripted Harnesses

The built-in `tests/` framework is best for long-running game-state assertions:

- Did a country have enough factories by a date?
- Did a country keep or gain a spirit by a date?
- Did an AI build enough railway/port infrastructure by a date?
- Did a country avoid an unwanted diplomatic or military state before a date?

The older WA scripted harness in `common/scripted_effects/WA_TEST_railway.txt` is more like an in-game unit/integration test framework. It can set variables, force intervals, inspect arrays, call scripted effects, and log custom pass/fail codes. Current spirits and stats harnesses are no-op compatibility shims because those checks migrated to built-in test bundles.

Use the built-in `tests/` framework for the automated tests requested here unless the assertion requires active setup, array inspection, direct effect calls, or custom multi-step state.

## Writing A New WA Test

1. Pick the owning bundle or create a focused new bundle in `tests/`.
2. Add `last_date` far enough after the latest fail deadline.
3. Name the test as the failure condition.
4. Write `success` as the desired condition.
5. Write `fail` as either a deadline or a true inverse at the assertion date.
6. Use existing scripted triggers for scope-sensitive assertions.
7. Add a `WA_TEST_` helper trigger only if the assertion is reused or verbose.
8. Omit `run_count`, `acceptable_fail_rate`, and `loggers` unless there is a concrete reason.
9. Manually check brace balance and scope.
10. Run the game test bundle and inspect `logs/tests/tests_<timestamp>.log`.

## Review Checklist

- Does the test resolve eventually in both pass and fail cases?
- Are `success` and `fail` mutually exclusive for the same tick?
- Is the date gate strictness intentional?
- Is each trigger in the correct country/state scope?
- Is a same-date inverse fail too aggressive for AI behavior that needs time?
- Is `acceptable_fail_rate` omitted for deterministic tests?
- Does the test rely on a helper trigger whose scope is documented?
- Does the bundle `last_date` come after every fail deadline?
- If the test is in a replaced `tests` path, is the bundle complete and parseable?

