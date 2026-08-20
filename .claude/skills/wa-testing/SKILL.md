---
name: wa-testing
description: How to write, extend, and read World Ablaze tests — the built-in HOI4 `tests/` bundle framework (success/fail trigger blocks, date windows, geographic control assertions, `count_triggers` progress checks) and the in-game `WA_TEST_*` scripted harness for things a bundle cannot express. Use this whenever adding or fixing a test, whenever asked "how do I verify this AI change", whenever interpreting `logs/tests/tests_<timestamp>.log`, and whenever a test fails for a reason that may be the test's fault rather than the mod's. Choosing the wrong framework, or writing success/fail blocks that can both fire on the same day, produces tests that pass or fail for the wrong reason — decide here first.
---

# Testing in World Ablaze

Deep references: `documentation/WA_TEST_WRITING_GUIDELINES.md` (conventions) and `documentation/HOI4_TESTS_AND_TRIGGERS_NOTES.md` (framework mechanics). Read the guidelines file before writing a country test file — it is the house style.

## Two frameworks — pick deliberately

| Use the built-in `tests/` bundle when… | Use a `WA_TEST_*` scripted harness when… |
| --- | --- |
| The assertion is about observable game state at or by a date | The test needs active setup (set variables, force intervals, call effects) |
| "Did the AI conquer X by Y?", "Did GER have 300 mils by 1939?" | You must inspect arrays or internal system state |
| Deterministic, no side effects needed | You need multi-step state and custom pass/fail/skip codes |
| Runs unattended overnight | You are unit-testing a WA AI subsystem's internals |

Default to the built-in framework. The harness exists for the railway system because pathfinding internals are not observable from a trigger block; that is a high bar.

Note that `common/scripted_effects/WA_TEST_spirits.txt` and `WA_TEST_stats.txt` are now no-op compatibility shims — those checks migrated to `tests/wa_spirits_strict_parity.txt` and `tests/wa_stats_strict_parity.txt`. Do not add new logic to the shims.

## Built-in bundles

### Shape

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

- One bundle per topic or per country + category. `tests/` is a `replace_path` folder, so every bundle must be complete and parseable.
- `last_date = 1946.1.1` for all WW2-era tests. It must come after every fail deadline in the file.
- Omit `run_count` (defaults to 1), `acceptable_fail_rate` (defaults to 0), and `loggers` unless you have a concrete reason. `acceptable_fail_rate` is only for genuinely stochastic outcomes.
- `success` and `fail` are trigger blocks — implicitly ANDed, side-effect free.
- On failure the game writes a save named `TEST_FAIL_<test-name>_<game-date>.hoi4`, which is the fastest way to see what actually happened.

### Naming

`WA_<TAG>_<YEAR>_<short_success_condition>` — name the *success* condition, not the failure mode. The log already records the date and outcome, so `WA_GER_1941_barbarossa` reads better in a failure report than `WA_GER_1941_soviet_war_not_too_late_or_early`.

Organise long country files by year with ASCII banner headers, chronological within each year, and precede every test with the exact wording:

```txt
# Historical date: 1941.12.11
```

### The date-window pattern

For a historical milestone, allow roughly one month of leeway each side. `success` requires the condition plus a date past the early boundary; `fail` catches *both* too-early and too-late:

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

Remember `>` and `<` are strict: `date > 1938.2.12` first holds on 1938-02-13.

### Other patterns

**Peace-until** — catches wars starting too early; pair with an on-time war test:

```txt
success = { date > 1941.5.21 }
fail    = { date < 1941.5.22  GER = { has_war_with = SOV } }
```

**Guardrail** — a position must be held until a date. There is often no meaningful "too late" branch:

```txt
success = { date > 1944.11.30 }
fail = {
	date < 1944.12.1
	OR = {
		804 = { NOT = { WA_TEST_is_controlled_by_GER_aligned_country = yes } }
		810 = { NOT = { WA_TEST_is_controlled_by_GER_aligned_country = yes } }
	}
}
```

**Progress via `count_triggers`** — when full conquest is too strict and several valid campaigns exist:

```txt
count_triggers = {
	amount = 4
	966 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Riga
	206 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Minsk
	242 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Smolensk
	202 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Kiev
}
```

**Strict parity** — assert at a date with the fail block as the literal inverse at the same date. Correct only when the condition cannot legitimately arrive later; otherwise a same-date inverse fails before the AI has had a chance.

### Geographic assertions

State IDs come from `history/states/<ID>-<Name>.txt`. Always comment the city inline:

```txt
855 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Paris
```

Prefer **control** over ownership for conquest and frontline progress — occupation matters even when ownership has not transferred.

Aligned-control helpers in `common/scripted_triggers/WA_TEST_triggers.txt` accept the country, its subjects, or its faction members: `WA_TEST_is_controlled_by_<GER|ITA|ENG|USA|JAP|SOV>_aligned_country`.

**Japan is not an Axis faction member in World Ablaze** — it leads its own faction with its puppets. Use `WA_TEST_is_controlled_by_JAP_aligned_country`, never `is_in_faction_with = GER`.

For defeat tests, combine status with geography so the test proves the map result:

```txt
OR = {
	FRA = { has_capitulated = yes }
	FRA = { exists = no }
}
855 = { WA_TEST_is_controlled_by_GER_aligned_country = yes } # Paris
```

### Helper triggers

Add a `WA_TEST_*` helper in `common/scripted_triggers/WA_TEST_triggers.txt` when the assertion is reused, needs an explicit scope, or wraps a verbose native trigger — and comment its scope:

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

A single inline check does not need a helper.

## The scripted `WA_TEST_*` harness

The railway suite (`common/scripted_effects/WA_TEST_railway.txt`, driven from `events/wa_events_test.txt` and `common/on_actions/WA_TEST_on_actions.txt`) is the live example. Entry points: `WA_TEST_RW_init`, `_launch_all`, `_check_all`, `_print`, `_log_summary`, `_suite`, plus `_mark_passed` / `_mark_failed` / `_mark_skipped` / `_check_timeout`.

Adding one test to a harness like this touches **seven** places. Missing any one produces a test that silently never runs or never reports:

1. Init block — declare the test's state variables.
2. `log_summary` — add its counter.
3. `print` — add its output row.
4. `launch_all` — add the launch entry.
5. `check_all` — add the timeout check **and** the result check.
6. The checker event — re-launch entry.
7. The checker event — ongoing/waiting counters.

Two harness facts worth knowing:

- The suite runs as **JAP**; tests numbered 012+ scope to **ITA** to exercise cross-country behaviour.
- Test state variables live on the **suite host** (JAP) even when the test asserts about another country. Do not "fix" this by moving them.

## Running and reading results

Bundles run from the game. Output goes to the HOI4 **user** directory (not the mod):

```txt
logs/tests/tests_<timestamp>.log
```

A failure also drops `TEST_FAIL_<name>_<date>.hoi4` next to your saves — load it to see the actual board state.

Before you conclude the mod is broken, check the test itself: a same-date inverse that fires before the AI could act, a state ID that changed, or a strict `>` off by one day are all common.

## Checklist before finishing a test file

- Every test named for its success condition, and every test has `# Historical date: yyyy.m.d`.
- Milestone tests cover both too-early and too-late with ~1 month leeway.
- `success` and `fail` cannot both be true on the same day.
- State IDs verified against `history/states/`, important ones commented.
- Every trigger is in the right country/state scope.
- Braces balanced (see the PowerShell check in `wa-orientation`).
- Tabs preserved.
- `last_date = 1946.1.1` and after every fail deadline.
- No `run_count` / `acceptable_fail_rate` / `loggers` unless justified.

## Console harness: the convoy arsenal chain (Fix 115 / 116 / 117 / 118)

`event wa_ca.2` fires a report on every AI major at war; `tag GER` then `event wa_ca.1` does one
country. Output goes to `logs/game.log` under `CONVOY ARSENAL TEST`. Effects live in
`common/scripted_effects/WA_TEST_convoy_arsenal.txt`, recipe and expected values in the header of
`events/wa_test_convoy_arsenal.txt` — its own file, its own namespace, on purpose (see below).

It is deliberately **not** a `tests/` bundle: the chain's answer depends on the world, so no date
carries a fixed success trigger. What a human needs is the intermediate readings — the shipped gate
is one boolean and a 0 can come from five different terms, so the report prints each of them.

Design points worth copying for the next gate of this shape:

- **The report must be fired PER COUNTRY, not looped in one scope.** The effect under test resolves
  its coalition against `ROOT`, so an `every_country` walk would score every candidate against the
  *firing* country's alliance. `wa_ca.2` fires `wa_ca.1` on each country for that reason.
- **The per-member block is an INDEPENDENT walk**, duplicating the shipped effect's own limit rather
  than sharing a helper with it. When the two disagree the fault is localised to one of them; a
  shared helper would hide exactly the bug the test exists to find.
- **The report prints a scope self-check FIRST (`who :` / `scope :`), and a run where `I-am-ROOT`
  is not 1 scores NOTHING.** This detector caught the 2026-08-20 call-site anomaly: fired from
  `events/wa_events_test.txt`, the same effect read every country-valued trigger false — the
  literal `tag = GER` while playing Germany included — while value triggers read true, and the
  gauge printed a plausible `0.000`. Cause unknown; the harness was rehomed. Lessons log, "Two
  call sites, one effect".

## Scope-sanity harness: `wa_iso`

`events/wa_test_scope_isolation.txt` (+ `common/scripted_effects/WA_TEST_scope_isolation_effects.txt`)
is a kept, reusable clean call site. When a scripted effect's country-valued triggers all read
false while its value triggers read true, do NOT edit the effect — re-fire it from here first:
`tag GER` then `event wa_iso.1` (engine/context sanity), `wa_iso.2` (scripted-effect indirection),
`wa_iso.3` (fires the real effect under suspicion — repoint its one call as needed). Output in
`logs/game.log` under `SCOPE ISOLATION`. If the effect works from here but not from its home file,
the home file is the fault and the harness gets rehomed, not debugged.
