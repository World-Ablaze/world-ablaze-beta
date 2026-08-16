---
name: wa-constants-registry
description: The registry of every World Ablaze `@` constant, engine define and building fact that is declared in more than one place and must stay equal — HOI4 `@` constants are FILE-SCOPED, so the mod redeclares them across files ("must match" comments), mirrors 05_defines.lua / 00_buildings.txt values into script, and copies script constants into savegame.py's analysis tables; every copy drifts silently. Use this whenever you add, rename, move or change the value of any `@NAME = value` under `common/` or `events/`, touch `common/defines/05_defines.lua`, `common/buildings/00_buildings.txt` costs/caps, or the `_PC_*` tables in `.claude/skills/wa-savegame-analysis/scripts/savegame.py`, and ALWAYS before committing a change to `WA_AI_*` scripted effects/triggers — run `python tools/check_constants.py`; it fails on drift, phantom mirrors and unread copies. Also the home of the rule that a legacy gate without a recorded purpose outlives its reason.
---

# Constants registry — file-scoped `@` constants and their mirrors

## The rule in one line

`@` constants do not cross file boundaries. Any quantity that two files need is declared twice,
and the pair is a **contract** — one owner, N mirrors, same value — that only a checker can hold.
The contract list is `tools/constants_registry.json`; the checker is `tools/check_constants.py`;
the human-readable table is `references/registry.md` (generated — never hand-edit).

## Run this before you commit

```bash
python tools/check_constants.py
```

Exit 0 = every registered copy agrees and nothing is dead. Non-zero means one of:

| Level | Kind | Meaning | What to do |
| --- | --- | --- | --- |
| ERROR | `DRIFT` | a mirror's value differs from its owner | change the *other* copies too — or, if the split is deliberate, that is a design decision: say so in the commit and split the group |
| ERROR | `MISSING` | the registry names a declaration that is not there | either the "must match" comment is stale (fix the comment + registry) or you renamed/removed a constant and left the registry behind |
| ERROR | `UNREGISTERED` | same `@NAME` in several files with **different** values, no group | that is a live drift nobody recorded — decide the truth, fix, register |
| WARN | `UNREGISTERED` | same `@NAME` in several files, same value, no group | an implicit contract — register it (or list the files under `independent_paths` if the collision is coincidence) |
| WARN | `DEAD` / `DEAD-MIRROR` | a `WA_*` file declares a constant nothing in that file reads | delete it, or make it the registered **owner** if it is the reference declaration the docs point at (owners are exempt: they may be read only by mirrors) |
| INFO | `DEAD` | same, in a non-WA (vanilla-derived) file | left alone unless you are in that file anyway |
| INFO | `ADVISORY` | an `advisory` group disagrees | conventionally equal, may diverge on purpose — read the `governs` text and decide |

Other flags: `--strict` (WARN fails too), `--json`, `--list` (dump every `@` declaration seen),
`--markdown` (regenerate `references/registry.md`), `--repo <dir>` (check a `git archive` of
another commit with the current manifest).

## When to touch the registry

- **You change a registered value** → change every copy the table lists (owner and mirrors), then run the checker. The `governs` column tells you what the number does, so you know what breaks if the copies disagree.
- **You add a constant a second file needs** → declare it in both, keep the `# must match <file>` comment convention *and* add a group to `tools/constants_registry.json` (owner = the file whose header the docs call the control panel; mirrors = the rest). Then `python tools/check_constants.py --markdown > .claude/skills/wa-constants-registry/references/registry.md`.
- **You rename a constant** → renames are **per file** (file scope means a rename in one file touches nothing else). Grep the old name across `common/`, `events/`, `documentation/`, `.claude/`, `tools/`; update the registry member names; leave a one-line "was named X until <date>" comment at the declaration so a `git log -S` reader can follow it.
- **You mirror an engine fact** (`05_defines.lua`, `00_buildings.txt` `base_cost` / `state_max`, `common/units/air.txt` wing sizes …) into a script constant or `global.` variable → register it with the engine file as **owner** (`lua_define` / `pdx_block_key`). PC is a *shadow* construction system that pays its own price table — an unregistered cost mirror is free industry for the AI.
- **You add a `_PC_*` constant, band or type id to `savegame.py`** → it is a mirror of script; register it (`py_assign` / `py_literal_has`).

Member kinds the checker understands: `pdx_const` (`@NAME = v`), `pdx_global` (`set_variable = { global.NAME = v }`),
`pdx_block_key` (`block = { key = v }`, dotted key walks sub-blocks), `lua_define`, `py_assign`, `py_literal_has`
(dict key / sequence item / tuple-item[0] present), `regex` (all group-1 captures in the file must agree — use it for
a quantity that exists only as repeated literals, e.g. the PC 20-civ clamp).

## Where the families live (owner file → mirrors)

| Family | Owner (authoritative) | Mirrors | Registry ids |
| --- | --- | --- | --- |
| PC allocation (`ALLOC_FRACTION` 0.40, `STABLE_BASE` 0.30, hard cap 0.50, stall 30 w, aging 12 w, 20-civ clamp) | `common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt` | `WA_AI_CONSTRUCTION_triggers.txt` (affordability gate + civs_16/_20 floors), `events/wa_events_debug.txt`, `savegame.py` `_PC_*` | `pc_alloc_*`, `pc_stable_*`, `pc_stall_*`, `pc_aging_*`, `pc_max_civs_per_project` |
| Fix 41 priority bands (1100 / 1000 / 500 / 350 / 300 / 250 / 100) | core.txt (rail-war, legacy max); railway_core (rail-prewar); strategies.txt (air-front, air-basing, default); queue_functions.txt (strategic) | railway_helpers / railway_strategies / queue_functions redeclarations, `savegame.py` `_PC_BANDS` | `pc_band_*` |
| Fix 78/87 air lane switch (20 %) | core.txt `@AI_PC_AIR_LANE_2ND_SLOT_PCT` | strategies.txt `@UK_AIR_DEEP_DEFICIT_PCT` (same quantity, different name — the two must open together) | `pc_air_lane_2nd_slot_pct` |
| PC type ids (13 rail, 14 port, 20 uk_air, 21 theatre_air, 23 islands) | core.txt globals (13/14), strategies.txt (20/21/23) | railway_core / helpers, `savegame.py` `_PC_TYPE_ID` | `pc_type_id_*` |
| Railway control panel (eligibility five, routes per enemy, bands) | `WA_AI_CONSTRUCTION_PRIORITY_railway_core.txt` header block | `WA_AI_CONSTRUCTION_triggers.txt` (the on_weekly filter and the per-enemy budget test are the READERS), railway_helpers, railway_strategies | `railway_*`, `pc_band_rail_*`, `pc_type_id_rail` |
| AIFC eligibility five | `WA_AI_AIFC_triggers.txt` only (core copies removed 2026-08-16) | — (`SECTOR_MAX_STATES` lives only in helpers) | `recovery_min_states_hatch` (advisory) |
| Posture (`MIN_EQ` 0.9, `MIN_OWN_MP` 150000) | `WA_AI_MILITARY_posture_triggers.txt` is the control panel for the trigger-side twins; effects file owns arithmetic-only constants | the other posture file | `posture_*` |
| Shared-slot state caps (REF 6, SR/HSR/AR/HAR 15, CIC/MIC/NIC 45) | `common/buildings/00_buildings.txt` `level_cap.state_max` | `WA_AI_CONSTRUCTION_triggers.txt` `@WA_AI_*_STATE_MAX` (Fix 81/88 committed-level test) | `state_max_*` |
| PC shadow prices | `00_buildings.txt` `base_cost` / `per_level_extra_cost` / `base_cost_conversion` | core.txt `global.WA_AI_PC_BUILDING_*_COST` / `WA_AI_PC_CONVERSION_*`, railway_helpers `@WA_AI_PC_RAILWAY_BASE_COST` / `@WA_AI_PC_NAVAL_BASE_*` | `cost_*` |
| Engine defines | `common/defines/05_defines.lua` | `@WA_AI_BF_CIVS_PER_LINE` (MAX_CIV_FACTORIES_PER_LINE), `@UK_AIR_CAPACITY_PER_LEVEL` / `@THEATRE_AIR_CAPACITY_PER_LEVEL` (AIRBASE_CAPACITY_MULT), leader-recruit ×2 (ARMY_LEADER_COST) | `engine_*` |

Full row-by-row table with current values: `references/registry.md`.

## Two durable rules this registry exists to enforce

**1. A "must match" comment is not a mechanism.** It held the railway five together for months and
still let `@AI_MAX_FRACTION_OF_FACTORIES_TO_ASSIGN_ON_PROJECTS_TOTAL` sit at 0.35 in the affordability
gate while the allocator funded at `@AI_PC_ALLOC_FRACTION = 0.40` (Fix 90, 2026-08-16: ~12 % of
projects the fill would have paid for were refused), with a third dead copy in core.txt that nothing
read. Only a checker holds a contract; the comment is for the human, the registry row is for the
machine — write both.

**2. A legacy gate needs a recorded purpose, or it outlives its reason.** `WA_AI_PC_active_nonrail_projects < 5`
was born with the pre-2026-01 fixed-5-slot engine (admission committed 20 civs) and survived three
refactors of the queue because no comment said what it protected; by the time it was found it was
starving the USA's radar and supply lines behind a slot budget that no longer existed. Its
sibling: the `_project_queue_max` temp inherited across call sites (Fix 40) let radar run on the air
strategies' budget. Every gate, cap and shared temp gets a header sentence naming (a) what it
protects, (b) which engine/system fact it assumes, (c) how to tell the fact is gone. When you meet a
gate without one, do not delete it on sight (principle 3) — reconstruct the purpose from
`git log -S`, write it down, then decide.

## Related

- `wa-pdxscript` — the language rule (`@` constants are file-scoped) and its silent-failure siblings.
- `wa-ai-systems` — the impact-analysis checklist that this checker is one line of.
- `wa-lessons-learned` — the incidents behind rules 1 and 2 (`references/lessons-log.md`, section "Constants and file boundaries").
- `.claude/agents/wa-architecture-reviewer.md` — the read-only reviewer that runs this checker as part of a pre-ship architecture review.
