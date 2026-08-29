---
name: wa-constants-registry
description: How World Ablaze declares tunable numbers and keeps every copy of a number equal. Since 2026-08-16 shared AI constants are HOI4 1.18 SCRIPT CONSTANTS in `common/script_constants/wa_ai_*.txt`, read as `constant:<category>.<group>.<key>` — one declaration visible from every file, replacing the file-scoped `@` copies that had to be kept in sync by hand. `@` constants remain legal ONLY when a single file reads them. Cross-format copies (05_defines.lua, 00_buildings.txt costs/caps, the `_PC_*` tables in savegame.py, `global.` price variables) are tracked by `tools/constants_registry.json` and verified by `python tools/check_constants.py`, which also fails on a `@` shared between two WA files, an unresolved `constant:` reference, or an unused `wa_ai_*` constant. Use this whenever you add / rename / retune any AI number, touch `common/script_constants/`, `05_defines.lua`, `00_buildings.txt`, `savegame.py` `_PC_*`, and ALWAYS before committing a change to `WA_AI_*` scripted effects/triggers. Also the home of the rule that a legacy gate needs a recorded purpose.
---

# Constants: script constants first, `@` only when private, a registry for the rest

## The three rules

1. **A number two files read is a script constant.** Declare it once in
   `common/script_constants/wa_ai_<system>.txt` and read it as `constant:wa_ai_<system>.<group>.<key>`.
   Never redeclare a `@` in a second file — the checker reports that as `SHARED-AT` (ERROR).
2. **A `@` constant is legal only when one file reads it** (WA_TEST enums, `@WA_TLM_VERSION`, a
   threshold used by one trigger family). The moment a second file needs it, it moves to
   script constants.
3. **A number that also exists in another format is a registered group.** Engine defines
   (`05_defines.lua` - an override layer over the install's `00_defines.lua`, not the whole table;
   `wa-engine-reference`, section "`common/defines` is an override layer", says which file a value
   actually comes from), building facts (`00_buildings.txt` `base_cost` / `state_max` — the PC
   shadow-price table `constant:wa_ai_pc.cost.*` mirrors them), and the savegame-analysis tables in
   `savegame.py` (`_PC_BANDS`, `_PC_TYPE_ID`, `_PC_*`) cannot read `constant:` — they are copies,
   and `tools/constants_registry.json` + `python tools/check_constants.py` is what holds them equal.

## Script constants — what was validated in-game (2026-08-16, HOI4 1.18)

| Works | Does not |
| --- | --- |
| every variable context: `set_temp_variable`, `set_variable` (incl. `global.`), `check_variable` (either side, `<`/`>`/`=`), `multiply_/divide_/add_to_/subtract_from_temp_variable`, `clamp_temp_variable max =`, `add_to_temp_array`, `is_in_array`, `[?constant:x.y.z]` in a log | `ai_strategy` `value =` (parse error "Malformed token") |
| raw numeric triggers: `num_of_civilian_factories`, `surrender_progress`, `num_of_controlled_states`, `has_army_size size >`, `has_deployed_air_force_size size >`, `has_manpower` — each with a FALSE control | `has_country_flag days >` (inconclusive probe — keep `@`) ; `fighting_army_strength_ratio ratio >` (untested, needs a war — keep `@`) |
| from `scripted_effects`, `scripted_triggers`, events; a chain temp set from a constant (`_project_priority = constant:…`) | |
| categories `int` and `fixed_point`; integer literals under `fixed_point`; negatives; ONE level of nested groups (`cat.group.key`) | deeper nesting untested |

Facts to keep in mind:
- The game reloads `common/script_constants` **separately** from the scripts that read it: full
  restart when tuning, `reload` is not enough (doc: `common/script_constants/documentation.md`).
- `common/script_constants` is a `replace_path` folder in `descriptor.mod`: the mod ships only its
  own files there (vanilla `state_groups.txt` / `propaganda_campaigns.txt` are dropped — nothing live
  in the mod reads them; the reference in `common/collections/collections.txt` is commented out).
- Schema: one category per file, `schema = { any_key = yes data = { { any_key = yes data = fixed_point } } }`,
  then `group = { key = value  # doc }`. Every key carries a `# was @OLD_NAME` line so `git log -S`
  and old comments/lessons stay followable.
- Probe harness — deleted after use, recover it from git at the commit that shipped `wa_ai_pc.txt`
  (`13eb2b9c6`): `events/wa_test_constants.txt` + `common/script_constants/wa_test_constants.txt` (both deleted)
  + the two `WA_TEST_constants.txt` scripted files (also deleted). Re-run it before relying on a context not in the table.

## Where the numbers live

| Category file (`common/script_constants/`) | Groups | Read by |
| --- | --- | --- |
| `wa_ai_pc.txt` — priority construction | `alloc` (fraction 0.40, stable_base 0.30, hard cap 0.50, stall/aging weeks, 20-civ slot, air lane 20 %), `prio` (Fix 41 bands 1100/1000/500/350/300/250/100), `type_id` (13 rail, 14 port … 25 inf_resource), `qmax` (Fix 90 budgets), `air_prio`, `air` (UK / theatre basing tunables), `cost` (shadow prices = registered mirrors of `00_buildings.txt`; were `global.WA_AI_PC_BUILDING_*_COST`) | `WA_AI_CONSTRUCTION_PRIORITY_core / _strategies / _railway_*`, `queue_functions`, `WA_AI_CONSTRUCTION_triggers.txt`, `wa_events_debug.txt` |
| `wa_ai_railway.txt` — railway control panel | `interval`, `eligibility` (Fix 43 hatch), `routes` (incl. `queue_full` = skip threshold = admission cap, Fix 77), `supply`, `cost` (naval-base per-level taper + segment estimate; base prices are `wa_ai_pc.cost.*`) | `railway_core / helpers / strategies`, `WA_AI_CONSTRUCTION_triggers.txt` (eligibility filter, per-enemy budget) |
| `wa_ai_aifc.txt` | `eligibility`, `selection` (anchor feasibility floor, [aifc-traction]), `sector` | `WA_AI_AIFC_triggers / core / helpers` |
| `wa_ai_posture.txt` | `enter`, `local`, `manpower`, `brake`, `alive`, `xr`, `air` (three `fighting_army_strength_ratio` bars stay `@` in the effects file — untested context) | `WA_AI_MILITARY_posture_triggers / effects` |

Not yet migrated / still `@` by design: standard-queue constants in `WA_AI_CONSTRUCTION_triggers.txt`
(`@WA_AI_*_STATE_MAX` mirrors of `00_buildings`, `@WA_AI_QUEUE_DEPTH_*`) and `queue_functions`
(`@WA_AI_BF_*`), the bomber-ladder thresholds in `WA_AI_MILITARY_triggers.txt`, `@WA_AI_LANDING_FREEZE_DAYS_STRICT`,
`@WA_TLM_VERSION`, `WA_TEST_*` enums, `@map_width` — all single-file. `python tools/check_constants.py --list`
prints every `@` still declared.

## Run this before you commit

```bash
python tools/check_constants.py
```

| Level | Kind | Meaning | What to do |
| --- | --- | --- | --- |
| ERROR | `SHARED-AT` | the same `@NAME` is declared in two WA files | move it to `common/script_constants/wa_ai_<system>.txt`, read `constant:` everywhere, delete both `@` |
| ERROR | `UNRESOLVED` | a `constant:x.y.z` no script_constants file declares | typo or missing key — the game would read garbage silently |
| WARN | `UNUSED-CONST` | a `wa_ai_*` key nothing reads | delete it, or find the reader that should use it instead of a literal |
| ERROR | `DRIFT` | a registered mirror (define / building / savegame / global) differs from its owner | change every copy the group lists |
| ERROR | `MISSING` | the registry names a declaration that is not there | you renamed/removed something — update `tools/constants_registry.json` |
| ERROR | `UNREGISTERED` | same `@NAME` in several non-WA files with different values | decide, fix, register or list under `independent_paths` |
| WARN | `DEAD` / `DEAD-MIRROR` | a `WA_*` file declares a `@` nothing in that file reads | delete it (owners of registered groups are exempt) |
| INFO | `DEAD` (non-WA file), `ADVISORY` | informational | — |

Other flags: `--strict` (WARN fails), `--json`, `--list`, `--markdown` (regenerate `references/registry.md`), `--repo <dir>`.

## When to touch what

- **Retune a number** → edit the key in `common/script_constants/wa_ai_*.txt`; if the group has a
  cross-format mirror (savegame.py band/type tables, `00_buildings` cost/cap, a define) the checker
  tells you which copies to update. Full game restart to see it.
- **Add a new shared number** → new key in the right group (or new group), `# doc` + `# was` lines,
  read it as `constant:`. If it mirrors an engine/building fact or is read by `savegame.py`, add a
  registry group with the engine file as owner (`lua_define` / `pdx_block_key`) or the script
  constant as owner and the `py_*` table as mirror. `--markdown` to regenerate `references/registry.md`.
- **Add a new PC strategy tag / band** → `wa_ai_pc.type_id.*` / `prio.*` **and** `savegame.py`
  `_PC_TYPE_ID` / `_PC_BANDS` **and** a registry group (`py_literal_has`).
- **Rename a key** → grep `constant:old.path` across `common/`, `events/`, `documentation/`,
  `.claude/`, `tools/`; keep the `# was` trail.
- **Need a number in `ai_strategy`** → not possible; keep the literal, comment which script constant
  it must equal, and add a `regex` mirror to the registry if it matters.

Registry member kinds: `script_constant {path}`, `pdx_const {file,name}`, `pdx_global {file,name}`,
`pdx_block_key {file,block,key}`, `lua_define {file,name}`, `py_assign {file,name}`,
`py_literal_has {file,name,value}`, `regex {file,pattern}`. Manifest fields: `groups`, `policy`
(`strict` / `advisory`), `independent_paths`, `dead_allowlist`, `script_constant_prefixes`.

## Two durable rules this exists to enforce

**1. A "must match" comment is not a mechanism.** It held the railway five together for months and
still let the PC affordability gate sit at 0.35 while the allocator funded at 0.40 (Fix 90), with a
third dead copy nothing read. First answer (2026-08-16 morning) was the registry + checker; the
same afternoon the in-game probe showed 1.18 script constants work everywhere the AI code needs
them, so the mirrors were removed altogether — one declaration cannot drift. The registry now only
holds the copies that *cannot* be one declaration.

**2. A legacy gate needs a recorded purpose, or it outlives its reason.** `WA_AI_PC_active_nonrail_projects < 5`
was born with the pre-2026-01 fixed-5-slot engine and survived three refactors because no comment
said what it protected; the `_project_queue_max` temp inherited across call sites (Fix 40) is the
same shape. Every gate, cap and shared temp gets a header sentence naming (a) what it protects,
(b) which engine/system fact it assumes, (c) how to tell the fact is gone. When you meet one
without it, reconstruct the purpose from `git log -S`, write it down, then decide.

## Related

- `wa-pdxscript` — the language rule (`@` is file-scoped, `constant:` is not) and its silent-failure siblings.
- `wa-ai-systems` — the impact-analysis checklist this checker is one line of.
- `wa-lessons-learned` — the incidents behind rules 1 and 2 (`references/lessons-log.md`, "Constants and file boundaries").
- `.claude/agents/wa-architecture-reviewer.md` — runs the checker as part of a pre-ship review.

## FORBIDDEN context, measured: `date > constant:`

MEASURED 2026-08-29 (`WA_TEST_pdx_semantics`, engine 1.19.2): a script constant CANNOT carry a
date. The file loads, but `date > constant:<cat>.<g>.<k>` reads TRUE for past AND future dates -
a gate that silently stops gating. The declaration layer therefore has TWO vehicles: script
constants for NUMBERS, and a named `WA_AI_CONFIG*` trigger holding the literal for DATES
(`WA_AI_CONFIG_naval_treaty_era_expired` is the shape). Never put a date-shaped value in
`common/script_constants/`.
