# `common/ai_equipment/` — naming convention

Checker: `python tools/check_ai_equipment_names.py` (audit, exit 0 required; `plan` / `apply`
migrate). Subject: `ai-equipment-naming` (WORK.md).

## What an entry is

The engine doc (`common/ai_equipment/_documentation.info`, section *Syntax*) defines two levels:

| Level | What it is | Engine reads | Keyed by |
| --- | --- | --- | --- |
| **design group** | one ROLE bucket (`roles = { land_medium_tank }`) for the countries in `available_for` / not in `blocked_for`, with a group priority | `category`, `roles`, `available_for`, `blocked_for`, `priority` | free identifier |
| **design** | one target variant: a chassis/airframe/hull `type` plus module constraints, its own `priority` and `enable` | `target_variant.type`, `modules`, `allowed_modules`, `priority`, `enable`, `history` | free identifier |

Both keys are **script-local identifiers**. MEASURED 2026-09-04: no other file under `common/`,
`events/`, `history/` or `localisation/` references a group or design key; a savegame does not
persist them either (variants are saved as `(equipment definition, creator, modules)` only, save
`1944.6_Jun.hoi4`, 0 hits over 5.0 M lines). The only readers are the engine and
`tools/equipment_evaluator/`, which keys designs by name inside a group (`by_name = {design.name:
...}` in `decide.py`, `ground.py`, `efficiency_audit.py`) and embeds `country_group_design_kind`
in its `WA_EQUIPGEN` marker ids.

So a rename costs nothing in-game and everything in readability: the key is documentation.

## The problem the convention removes

MEASURED on the pre-migration tree (29 files, 358 groups, 1736 designs):

| Defect | Count | Example |
| --- | --- | --- |
| Design key number ≠ chassis mark | 316 | `ENG_medium_tanks.medium_tank_6` targets `tank_eng_medium_chassis_4` (Cavalier) |
| Same design key in ≥ 2 files | 313 of 526 keys | `medium_tank_1` in 11 files |
| Same key twice **inside one group** | 4 | `SOV_medium_tank_destroyer.medium_tank_destroyer_2` = SU-85 (l.1689) AND SU-100 (l.1774); `SWE_modern_tanks.modern_tank_1` = IKV Leo AND Lansen C |
| Same key in two groups of one file | 6 | `USA_planes.txt`: `strat_bomber_1..4` in `USA_strategic_bomber` and `USA_heavy_strategic_bomber` |
| Group prefix not the owner tag | 25 | `ger_destroyers`, `ita_naval_carrier`, `naval_carrier` (generic file), `destroyers` |
| Group slug ≠ its role | 104 | `ENG_destroyers` serves `naval_screen`; `ENG_heavy_fighter_interceptor` serves `air_night_fighter` |
| Ad-hoc suffix vocabulary | 9 forms | `_cc`, `_2_1`, `_lr`, `_attacker`, `_conversion`, `_default`, `_early`, `_late`, `_prewar` |
| Design without a display-name comment | 724 | |

The in-group duplicates are real defects: the evaluator's `by_name` dict keeps the last one
silently; the engine's behaviour on a duplicate key is **ASSUMED** (one design shadowed).
Vanilla is not a model here: its `GER_tank.txt` mixes `light_tank_artillery_1`,
`basic_medium_tank_default` and `fw_190_a1`.

## Convention

### Design group key: `<OWNER>_<role_slug>[_<qualifier>]`

| Part | Rule |
| --- | --- |
| `OWNER` | Upper-case tag of the **tech-tree owner** = the file prefix (`GER_tank.txt` → `GER`), or `generic` for `generic_*.txt`. It names whose equipment types the group targets, not who may use it: `ENG_fighter` has `available_for = {}` + `blocked_for = { majors }` and serves every minor flying British airframes. |
| `role_slug` | The group's **single** `roles` entry minus its domain prefix `land_` / `air_` / `naval_` (`cruiser_submarine` has none). `land_medium_tank` → `GER_medium_tank`; `naval_screen` → `GER_screen`; `air_night_fighter` → `GER_night_fighter`. |
| `qualifier` | Only when one file carries **two groups on the same role**; one word, from the old distinguishing word: `GER_light_bomber_fast` / `GER_light_bomber_strike`, `USA_carrier` / `USA_carrier_light`, `ENG_strategic_bomber` / `ENG_strategic_bomber_heavy`. |

One group = one role (rule G2). A group serving two roles is split.

### Design key: `<type>[__<qualifier>]`

| Part | Rule |
| --- | --- |
| `type` | **Exactly** the design's `target_variant.type` string: `tank_eng_medium_chassis_4`, `ENG_spitfire_mkia_airframe`, `eng_frigate_hull_2`. The key says what the design targets; nothing to decode, nothing to keep in sync. |
| `__qualifier` | Only when the group carries **two designs on the same type** (151 designs today: module-tier steps on one airframe, cutting-corners twins). Double underscore, never present in a type name (MEASURED 0/1631). Closed vocabulary below, else an ordinal `v2`, `v3`, … in file order; the first design on a type keeps the bare key. |

| Qualifier | Means |
| --- | --- |
| `cc` | cutting-corners module fit, gated by `WA_AI_EQUIPMENT_should_mount_cutting_corners` |
| `lr` | long-range fit |
| `aa` | anti-air refit |
| `atk` | ground-attack fit |
| `int` | interceptor fit |
| `conv` | conversion of an older airframe |
| `vN` | N-th design on the same type with no better word (module-tier step) |

Add a word to the vocabulary in `tools/check_ai_equipment_names.py` (`QUALIFIERS`) and in this
table in the same commit; the checker rejects unknown words (rule D2-QUAL).

### Display-name comment

Every design key line ends with `# <display name>` — the type's localisation
(`tank_eng_medium_chassis_4:0 "Cavalier"`), 7-bit ASCII, kept when already present.
`tools/check_ai_equipment_names.py apply` fills missing ones; the audit reports a missing one as
WARN (D3-COMMENT). Coverage is total: MEASURED 1631/1631 types have an English localisation.

### Example

```
ENG_medium_tank = {                              # was ENG_medium_tanks
	category = land
	available_for = { ENG }
	roles = { land_medium_tank }
	...
	tank_eng_medium_chassis_4 = { # Cavalier         # was medium_tank_6
		...
		target_variant = { type = tank_eng_medium_chassis_4 ... }
	}
	tank_eng_medium_chassis_4_2 = { # Cromwell       # was medium_tank_7
	...
	tank_sov_medium_chassis_td_3_2 = { # SU 85       # was medium_tank_destroyer_2
	tank_sov_medium_chassis_td_3_2__cc = { # SU 85   # was medium_tank_destroyer_2_cc
```

## Rules the checker enforces

| Rule | Level | Text |
| --- | --- | --- |
| G1-PREFIX / G1-OWNER | ERROR | group key starts with `<TAG>_` or `generic_`; a `<TAG>` prefix is in `available_for` when that list is non-empty |
| G2-ROLE | ERROR | exactly one `roles` entry |
| G3-SLUG | ERROR | key = `<OWNER>_<role_slug>[_<qualifier>]` as computed by the tool |
| D0-TYPE | ERROR | design has a `target_variant.type` |
| D1-DUP | ERROR | design key unique inside its group |
| D2-KEY / D2-QUAL | ERROR | key = `<type>` or `<type>__<known qualifier or vN>` |
| D3-COMMENT | WARN | key line carries `# <display name>` |

## Migration and what it touches

`apply` rewrites by byte span: only the two key tokens, the missing comments and the
`WA_EQUIPGEN_*` marker ids change; indentation, CRLF, priorities, modules and owned blocks are
untouched. Marker ids are rewritten `<country>_<oldgroup>_<olddesign>_<kind>` →
`<country>_<newgroup>_<newdesign>_<kind>` so `equipment_evaluator` recomputes the same ids and
reports no conflict. `tools/equipment_evaluator/output/` is generated (git-ignored) and is
regenerated by the next analyse.

Closing criterion of the subject: audit exit 0; `python -m unittest` on the evaluator green;
`python -m equipment_evaluator --domain all --all --generate-plan` yields the same decision
count before and after; F9 boot test (the mod loads, `error.log` free of `ai_equipment` lines).

## Rejected alternatives

| Alternative | Why not |
| --- | --- |
| Keep `medium_tank_N` but make N = chassis mark (`medium_tank_4_2`) | Still a number to decode, still collides across nations, still wrong for `_cc` / interceptor twins on one chassis. |
| Human slug from the vehicle (`medium_tank_cromwell`) | 724 designs had no comment to start from; a slug is a naming dispute per design and nothing can check it. The vehicle name lives in the comment, generated from localisation. |
| Prefix-only group normalisation (`ger_` → `GER_`, keep the slug) | Leaves 104 groups whose slug contradicts their role (`ENG_destroyers` = `naval_screen`). The marker rewrite cost is paid once either way. |
