---
name: wa-orientation
description: Entry point for working in the World Ablaze HOI4 mod repository. Explains what this repo is (a mod root that replaces vanilla folders), the hazards that follow from that, and routes any task to the file, document, or sibling skill that owns it. Use this whenever you are asked to change, review, or explain anything in this repo and you are not already certain which system owns the behaviour — including vague asks like "why does the AI do X", "add a decision for Italy", "where is the railway code", "fix this focus", or "the mod crashes on load". Read this before opening files; guessing at ownership in a 190-file ai_strategy folder wastes far more time than one routing lookup.
---

# World Ablaze — orientation and routing

## What this repository is

The repo root **is** the HOI4 mod root. `descriptor.mod` declares `version="1.18.0"` / `supported_version="1.18.0"` and roughly 70 `replace_path` entries.

That `replace_path` list is the single most important fact about this repo. For every replaced folder, HOI4 loads **only** this mod's files — vanilla content in that folder is not loaded at all. Replaced paths include `common/ai_strategy`, `common/decisions`, `common/ideas`, `common/scripted_effects`, `common/scripted_triggers`, `common/on_actions`, `events`, and `tests`.

Consequences you must hold in mind on every edit:

- Deleting or renaming a definition in a replaced folder **removes it from the running game**, even though it looks like vanilla should still provide it. There is no fallback.
- A parse error in one file in a replaced folder can silently drop everything after it. Brace balance is not cosmetic here.
- "Additive patch over vanilla" is the wrong mental model. Treat files in replaced paths as the full content of that category.

Check `descriptor.mod` when unsure whether a folder is replaced — it is a flat, greppable list.

## Route the task before opening files

| The task is about… | Go to |
| --- | --- |
| PDXScript syntax, scopes, variables, arrays, `meta_trigger`, why a trigger silently does nothing | skill `wa-pdxscript` |
| Any `WA_AI_*` system: construction, railway, military strategy, templates, research, production, config triggers, on-action cadence | skill `wa-ai-systems` |
| Writing or fixing tests, `tests/*.txt` bundles, `WA_TEST_*` harnesses, reading test logs | skill `wa-testing` |
| Python tooling: map generators, `ai_will_do` replacers, prospecting analyzers, DLC splitter | skill `wa-tooling` |
| A gotcha that already bit someone; also where to record a new one | skill `wa-lessons-learned` |
| Full system-ownership table, editing rules, validation matrix | `AGENTS.md` (repo root) |

`AGENTS.md` is the authoritative index of systems and their owning files. These skills do not replace it — they carry the working knowledge an agent needs *while* editing, and point back to `AGENTS.md` and `documentation/` for the full spec.

## Directory map

| Path | What lives there |
| --- | --- |
| `common/` | All scripted content. 70+ subfolders; the ones you will touch most are `scripted_effects/` (82 files), `scripted_triggers/` (69), `ai_strategy/` (187), `decisions/` (96), `national_focus/` (52), `ideas/`, `on_actions/`, `technologies/`. |
| `events/` | 154 files. `WA_AI_*.txt` are AI systems, `wa_<tag>_events.txt` are WA country events, vanilla-named files are overrides. |
| `history/` | Start state. `history/states/<ID>-<Name>.txt` is where you look up state IDs. |
| `localisation/` | Mostly `localisation/replace/*_l_english.yml`. `_GENERATED_` in a filename means tool-owned. |
| `documentation/` | 9 design docs. The deep reference behind these skills — see the table below. |
| `tests/` | Built-in HOI4 test bundles (parity + per-country geographic). |
| `tools/` | Python generators and `ai_will_do` replacers. |
| `map/`, `gfx/`, `interface/`, `portraits/`, `music/` | Assets and map data. |

## The documentation set

Read the relevant one before changing a documented system; several are explicitly authoritative and outrank inference from the code.

| Document | Read it before |
| --- | --- |
| `documentation/WA_AI_MILITARY_SYSTEM.md` | Touching **any** `ai_strategy` block in `common/ai_strategy/WA_AI_MILITARY_*` or `WA_AI_NAVAL_*`. Authoritative spec for the 4-layer model and domain split. |
| `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` | Looking up which `type =` exists, where it lives, and its target layer. |
| `documentation/WA_AI_RAILWAY_SYSTEM.md` | Any railway / priority-construction work. Includes constants, data structures, and the weekly cycle. |
| `documentation/WA_AI_RAILWAY_SYSTEM_EDGE_CASES.md`, `_TEST_CASES.md` | Debugging railway behaviour or extending its test suite. |
| `documentation/WA_AI_DIVISION_TEMPLATES.md` | Template / division-creator work. |
| `documentation/PDXSCRIPT_LANGUAGE_NOTES.md` | Language questions — backing reference for `wa-pdxscript`. |
| `documentation/HOI4_TESTS_AND_TRIGGERS_NOTES.md`, `WA_TEST_WRITING_GUIDELINES.md` | Test work — backing reference for `wa-testing`. |

## Finding the owner of a behaviour

Ownership is usually discoverable in two greps. Work backwards from the name, not forwards from the folder.

```bash
# 1. Who defines it?
grep -rn "^\s*WA_AI_PC_assign_factories = {" common/scripted_effects/
# 2. Who calls it?
grep -rn "WA_AI_PC_assign_factories = yes" common/ events/
```

For AI behaviour specifically, trace **from the schedule inward**: find the `on_actions` entry or background event that fires the system, then read the scripted effect, then the scripted triggers it gates on. Starting from a leaf effect leaves you unable to tell whether it runs daily, weekly, or never.

Useful starting points:

- `common/on_actions/WA_AI_startup_on_actions.txt` — what initialises at game start.
- `common/on_actions/WA_AI_misc_on_actions.txt` — daily/weekly/monthly AI pulses.
- `common/scripted_triggers/WA_AI_CONFIG.txt` — country archetype classification; the one WA_AI file that is *meant* to contain country tags.

## Before you edit — the non-negotiables

These are the rules that produce silent, hard-to-diagnose breakage when violated. Full editing rules are in `AGENTS.md`; these are the ones worth carrying in your head.

1. **Smallest correct change.** This is a large replacement mod. A broad rewrite in a replaced folder can remove unrelated vanilla content.
2. **Preserve tabs.** Existing PDXScript is tab-indented. Do not reformat blocks you are not changing, and never reformat generated or parser-managed `ai_will_do` sections.
3. **Do not hand-edit generated files.** `common/scripted_effects/WA_AI_MAP_*` data, `_GENERATED_` localisation, and tool-managed `ai_will_do` blocks are outputs. Change the generator (see `wa-tooling`) and regenerate.
4. **Country tags belong in country-scoped places.** Archetype-driven rules go through `WA_AI_CONFIG.txt` triggers, not copied tag lists. In `common/ai_strategy/WA_AI_MILITARY_*`, `tag =` / `original_tag =` as a *gating* term is forbidden outside Country-layer files.
5. **Keep the prefixes.** `WA_` for gameplay content, `WA_AI_` for AI systems, `WA_TEST_` for test harnesses. Generic names collide with vanilla and DLC.
6. **Check brace balance before finishing.** HOI4 reports most parse errors only at game launch, so nothing in your toolchain will catch it for you.

```powershell
$text = Get-Content common\scripted_effects\SOME_FILE.txt -Raw
$open = ([regex]::Matches($text, '\{')).Count
$close = ([regex]::Matches($text, '\}')).Count
"open=$open close=$close delta=$($open-$close)"
```

7. **Update the doc when you change a documented system.** The railway and military systems have specs that agents are told to trust; a stale spec is worse than none.

## Validation, by change type

You cannot run HOI4 from the shell, so pick the strongest check the change allows.

| Change | Check |
| --- | --- |
| Any PDXScript edit | Brace balance, scope correctness, name collisions, event ID/namespace validity — by inspection. |
| Map / pathfinding / railway data | `python run_generators.py <name> --dry-run` from `tools/`, then without `--dry-run` only if the diff is intended. |
| Technology or prospecting `ai_will_do` | Run the replacer in dry-run, inspect the diff, confirm nested modifiers and indentation survived. |
| AI outcome behaviour | Built-in test bundles in `tests/`; results land in the HOI4 user directory under `logs/tests/tests_<timestamp>.log`. |
| Localisation / UI | In-game only. No tooling catches a missing loc key. |
