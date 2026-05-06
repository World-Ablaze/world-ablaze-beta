# World Ablaze Test Writing Guidelines

Practical conventions for writing World Ablaze automated tests using the built-in Hearts of Iron IV test framework.

## Basic File Shape

Use one test bundle per topic or country. For country AI progression tests, prefer one file per country and test category:

```txt
last_date = 1946.1.1

tests = {
	WA_GER_1938_anschluss = {
		success = {
			# trigger block
		}

		fail = {
			# trigger block
		}
	}
}
```

For World War II era country AI tests, use:

```txt
last_date = 1946.1.1
```

Omit `run_count` unless there is a specific reason to evaluate the same test repeatedly. The normal default is `1`.

Omit `acceptable_fail_rate` for most tests. Use it only for tests that intentionally tolerate randomness over repeated runs.

Ignore `loggers` unless the test framework is better documented later.

## Naming

Use names that describe the success condition, not every possible failure mode.

Preferred:

```txt
WA_GER_1938_anschluss
WA_GER_1941_barbarossa
WA_GER_1941_usa_war
```

Avoid:

```txt
WA_GER_1938_austria_not_absorbed_by_mid_1938
WA_GER_1941_soviet_war_not_too_late_or_early
```

Failure timing is self-evident in the test log because the game logs the date when the test fails.

Use this country test naming pattern:

```txt
WA_<TAG>_<YEAR>_<short_success_condition>
```

Keep names compact and readable.

## Organization

Split long country files by year with large ASCII comment headers:

```txt
############################################################################################################
# 1941
############################################################################################################
```

Put tests in rough chronological order inside each year.

Add one historical reference comment before each test:

```txt
# Historical date: 1941.12.11
WA_GER_1941_usa_war = {
	...
}
```

Use the exact `Historical date: yyyy.m.d` wording.

## Success And Fail Blocks

Each test should normally contain only:

```txt
success = {
	...
}

fail = {
	...
}
```

Multiple triggers inside a block are implicitly ANDed. Use `OR = {}` and `AND = {}` explicitly when needed.

Write `success` and `fail` so they do not both become true on the same day for the same game state.

## Date Windows

For historical milestone tests, allow one month of leeway on each side of the historical date.

Pattern:

```txt
# Historical date: 1941.12.11
WA_GER_1941_usa_war = {
	success = {
		date > 1941.11.10
		GER = { has_war_with = USA }
	}

	fail = {
		OR = {
			AND = {
				date < 1941.11.11
				GER = { has_war_with = USA }
			}
			AND = {
				date > 1942.1.11
				NOT = { GER = { has_war_with = USA } }
			}
		}
	}
}
```

For an event with historical date `Y.M.D`:

- `success` should require the success condition and `date >` one day before the early boundary.
- Early failure should require the success condition and `date <` the early boundary.
- Late failure should require the success condition to still be false and `date >` the late boundary.
- The early boundary is approximately one month before the historical date.
- The late boundary is approximately one month after the historical date.

Example for a historical date of `1938.3.13`:

```txt
success date: date > 1938.2.12
early fail:   date < 1938.2.13
late fail:    date > 1938.4.13
```

## Peace-Until Tests

Use peace-until tests to catch wars starting too early.

Example:

```txt
# Historical date: 1941.6.22
WA_GER_1941_soviet_peace_until_june = {
	success = {
		date > 1941.5.21
	}

	fail = {
		date < 1941.5.22
		GER = { has_war_with = SOV }
	}
}
```

Pair these with a separate on-time war test that catches both too-early and too-late declarations.

## Geographic Control Tests

Use state IDs from `history/states/`. File names follow:

```txt
<ID>-<Name>.txt
```

Comment important state IDs inline:

```txt
855 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Paris
```

Prefer control checks for conquest progress and frontline outcomes, because occupation can matter even when ownership has not been transferred.

For aligned geographic checks, prefer country-specific helper triggers in `common/scripted_triggers/WA_TEST_triggers.txt`.

For Germany-aligned checks:

```txt
<state_id> = { WA_TEST_is_controlled_by_GER_aligned_country = yes }
```

For Italy-aligned checks:

```txt
<state_id> = { WA_TEST_is_controlled_by_ITA_aligned_country = yes }
```

For Britain-aligned checks:

```txt
<state_id> = { WA_TEST_is_controlled_by_ENG_aligned_country = yes }
```

For United States-aligned checks:

```txt
<state_id> = { WA_TEST_is_controlled_by_USA_aligned_country = yes }
```

For Japan-aligned checks:

```txt
<state_id> = { WA_TEST_is_controlled_by_JAP_aligned_country = yes }
```

For Soviet-aligned checks:

```txt
<state_id> = { WA_TEST_is_controlled_by_SOV_aligned_country = yes }
```

These helpers treat a state as valid if its controller is the target country, that country's subject, or in that country's faction.

Japan should not be tested as an Axis or Tripartite Pact faction member. In World Ablaze, Japan is expected to lead its own faction with its puppets, so Japan geographic tests should use `WA_TEST_is_controlled_by_JAP_aligned_country` rather than checking `is_in_faction_with = GER` or `is_in_faction_with = ITA`.

## Country Defeat Tests

For defeated countries, combine country status with important controlled states:

```txt
OR = {
	FRA = { has_capitulated = yes }
	FRA = { exists = no }
}
855 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Paris
```

Do not rely only on `has_capitulated` if the test is meant to validate geographic progress. Include key state checks so the test proves the AI achieved the relevant map result.

## Faction And Alignment Tests

For Germany-led European Axis alignment, check faction or subject status:

```txt
ITA = {
	OR = {
		is_in_faction_with = GER
		is_subject_of = GER
	}
}
```

Use the same one-month early and late date pattern for alignment milestones.

## Progress Tests

When testing invasions or campaigns where exact full conquest may be too strict, use `count_triggers`:

```txt
count_triggers = {
	amount = 4
	966 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Riga
	206 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Minsk
	207 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Vitebsk
	242 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Smolensk
	202 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Kiev
	241 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Gomel
}
```

This is useful for Barbarossa-style tests where the AI should have made meaningful progress, but different valid campaigns may take different specific cities.

## Guardrail Tests

Some tests are not event-completion checks. They are guardrails against the AI collapsing too early or losing critical positions before a date.

Example:

```txt
# Historical date: 1944.12.31
WA_GER_1944_berlin_held = {
	success = {
		date > 1944.11.30
	}

	fail = {
		date < 1944.12.1
		OR = {
			804 = { NOT = { WA_TEST_is_controlled_by_GER_aligned_country = yes } }
			810 = { NOT = { WA_TEST_is_controlled_by_GER_aligned_country = yes } }
		}
	}
}
```

For guardrails, the fail block catches the bad state before the early boundary. There may not be a meaningful "too late" branch because the test is about survival until a date.

## Validation Checklist

Before finishing a test file:

- Confirm every test has a concise success-condition name.
- Confirm every test has a `# Historical date: yyyy.m.d` comment.
- Confirm historical milestone tests check both too early and too late with one-month leeway.
- Confirm `success` and `fail` cannot both be true on the same date.
- Confirm state IDs are correct and important state checks have inline comments.
- Confirm country tags are correct.
- Confirm scope is correct for every trigger.
- Confirm braces are balanced.
- Confirm the file uses tabs and existing PDXScript indentation style.
- Confirm `last_date = 1946.1.1` for WW2-era tests.

Useful PowerShell brace check:

```powershell
$text = Get-Content tests\wa_germany_geographic.txt -Raw
$open = ([regex]::Matches($text, '\{')).Count
$close = ([regex]::Matches($text, '\}')).Count
"open=$open close=$close delta=$($open-$close)"
```
