---
name: wa-tooling
description: The Python tooling under `tools/` that generates World Ablaze content — map data generators (province connections, terrain, landmass, state mappings), the `ai_will_do` replacers for technology and prospecting decisions, the DLC splitter, and the dry-run discipline they all share. Use this whenever a file looks generated (`WA_AI_MAP_*`, `_GENERATED_` localisation, tool-managed `ai_will_do` blocks), whenever asked to change map lookup data or research/prospecting AI weights, and before hand-editing anything that a generator owns. Editing generated output directly is the mistake this skill exists to prevent — the next regeneration silently reverts it.
---

# WA Python tooling

Reference: `tools/REFACTORING_SUMMARY.md` for current parser status and known limitations. `PRESERVED_MODIFIER_FIX_FINAL.md` (repo root) for the prospecting modifier-preservation history.

## Recognising generated content

If you are about to edit one of these, stop and find the generator instead:

| Generated area | Owned by |
| --- | --- |
| `common/scripted_effects/WA_AI_MAP_*.txt` lookup data | `tools/run_generators.py` + `tools/map_generators/*.py` |
| `ai_will_do` blocks in `common/technologies/*.txt` | `tools/ai_will_do_replacer_all.py` and the per-domain replacers |
| `ai_will_do` blocks in `common/decisions/_resource_prospecting.txt` | `tools/ai_will_do_replacer_prospecting.py`, `needs_aware_generator.py`, `prospecting_decision_analyzer.py` |
| `localisation/**/*_GENERATED_*.yml` | their generator workflow |
| `.claude/skills/wa-constants-registry/references/registry.md` | `python tools/check_constants.py --markdown` (from `tools/constants_registry.json`) |

Hand-editing is acceptable only when there is genuinely no viable generator path — and then say so in a comment, because the next regeneration will overwrite it.

## The universal rule: dry-run first

Every tool here defaults to dry run and needs an explicit flag to write. Run the dry run, read the diff, then apply. These tools rewrite hundreds of blocks across dozens of files; an unreviewed apply is very hard to unpick from an unrelated change in the same commit.

Commit (or at least stage) unrelated work before applying a generator, so `git diff` afterwards shows only generated output.

## Map data generators

Run from `tools/` so the default relative paths resolve:

```bash
python run_generators.py --help
```

```bash
python run_generators.py all --dry-run -v
```

```bash
python run_generators.py all
```

Individual generators can be named, and multiple can be combined — they are re-sorted into dependency order automatically (`EXECUTION_ORDER`):

```bash
python run_generators.py landmass province_terrain --dry-run
```

Available generators (`tools/map_generators/`): `landmass`, `province_connections`, `province_positions`, `province_terrain`, `railway_connections`, `state_provinces`, `state_vp_provinces`.

These read from `map/` and emit the `WA_AI_MAP_*` lookup effects consumed by `WA_AI_pathfinding_effects.txt` and the railway system. If pathfinding starts behaving oddly after a map change, regenerating is the first thing to try — the lookup tables and `map/` can drift apart silently.

## Technology `ai_will_do` replacers

Unified entry point with auto-detection by filename:

```bash
python ai_will_do_replacer_all.py
```

```bash
python ai_will_do_replacer_all.py --apply
```

```bash
python ai_will_do_replacer_all.py --file armor_ger.txt --apply
```

```bash
python ai_will_do_replacer_all.py --type infantry --apply
```

Dispatch map: `infantry_*.txt` / `special_forces_doctrine.txt` → infantry; `support*.txt` → support; `armor_*.txt` / `tanks_*.txt` → armor; `air_techs*.txt`, `naval*.txt` / `MTG_naval.txt`, `industry.txt` / `electronics.txt` → legacy parsers.

Shared parsing/generation lives in `tools/ai_replacer_base/` (`file_processor.py`, `block_finder.py`, `text_utils.py`, `trigger_resolver.py`, `tech_graph.py`, `generator.py`). Fix bugs there rather than in one domain replacer, or the fix applies to one tech family only.

`ai_will_do_replacer_land.py` is **deprecated** — it was split into infantry + support + armor. Do not add to it.

The weights these emit are driven by the `WA_AI_RESEARCH_*` scripted triggers in `common/scripted_triggers/`. To change research behaviour, change the trigger and regenerate; do not tune the emitted `ai_will_do` numbers by hand.

## Prospecting decision replacer

```bash
python ai_will_do_replacer_prospecting.py
```

```bash
python ai_will_do_replacer_prospecting.py --apply --verbose
```

This rebuilds prospecting `ai_will_do` blocks with reactive, cooperative, and proactive layers, driven by `WA_AI_RESOURCE_NEEDS_triggers.txt`.

This pipeline has a history of two specific bugs — **nested modifier extraction** and **indentation** — documented in `PRESERVED_MODIFIER_FIX_FINAL.md`. After any apply, verify in the diff that:

- Country-specific modifiers that existed before still exist after.
- Nested `modifier = {}` blocks were not flattened or dropped.
- Tab indentation matches the surrounding file.

Read that document before changing the pipeline itself.

## Other tooling

| Path | Purpose |
| --- | --- |
| `tools/check_constants.py` + `tools/constants_registry.json` | Constants registry checker: drift / phantom mirrors / unread copies across file-scoped `@` constants, `05_defines.lua`, `00_buildings.txt` and `savegame.py`. Stdlib only, exit 1 on ERROR. Run before committing `WA_AI_*` script (skill `wa-constants-registry`). |
| `tools/dlc_splitter/` | Lexer/parser/AST/splitter for detecting and separating DLC-gated content. Has its own `__main__.py`. |
| `tools/core/` | Shared CLI, CSV parsers, file IO, logging config. |
| `tools/misc/ai_will_do_date_updater.py` | Conservative date-only updater — changes date modifiers without touching trigger logic. Prefer this when a date is all you need. |
| `tools/misc/delete_naval_cheat_events.py` | One-off maintenance script. |
| `tools/apply_output.log`, `full_run.log` | Output from previous runs; useful for seeing what a past apply actually touched. |

## Changing a generator

1. Reproduce the wrong output first, and keep the failing case in front of you.
2. Change the shared base module if the bug is in parsing or block finding; change the domain module only for domain-specific rules.
3. Dry-run over the full file set, not just the file that showed the bug — these parsers are regex/brace-matching based and a fix in one shape often breaks another.
4. Inspect the diff for preserved modifiers and indentation before applying.
5. Apply, then confirm `git diff` contains only intended changes.

## Validation

There is no test suite for these tools. The practical checks are: the dry-run diff, brace balance of the rewritten files (see `wa-orientation`), and — for map data — whether the railway/pathfinding tests in `tests/` still behave. Python tooling cannot catch a missing localisation key or a game-side parse error, so a regenerated file still deserves a brace check before commit.
