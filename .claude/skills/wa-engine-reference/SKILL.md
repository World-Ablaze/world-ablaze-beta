---
name: wa-engine-reference
description: The three sources of truth OUTSIDE this repository about how Hearts of Iron IV actually behaves - the game install (authoritative, version-matched), the Expert AI 5.0 mod (a peer solution to the same AI problem), and the Paradox wiki (hypothesis only, frequently stale). Use this BEFORE asserting anything about engine behaviour: what an effect or trigger does, what scope a modifier is valid in, what an `ai_strategy type =` means or what magnitude the engine responds to, what an NDefines key defaults to, or how the engine groups a faction into theatres. Also carries the replace_path rule that decides whether a base-game file you are reading is LIVE in WA campaigns or was deleted by the mod. Wrong conclusions in this repo come from guessing at the engine instead of opening the file that documents it.
---

# Engine reference - read before you assert

Most wrong conclusions in this repo are not script bugs. They are confident statements about how
HOI4 behaves that nobody opened a file to check.

**The rule:** before writing a sentence about how the engine behaves, open the file that documents
it and cite `file:line`. If you did not open it, the claim is **ASSUMED** (`AGENTS.md`, section
"Talking to the user") and you label it as such.

## The three sources, ranked

| Rank | Source | Authority |
| --- | --- | --- |
| 1 | The game install | **Authoritative.** It is the code that ran. |
| 2 | Expert AI 5.0 | **Evidence, not authority.** A peer mod solving the same problem on the same version - proof that a token works, and at what magnitude. Never a rule. |
| 3 | The Paradox wiki | **Hypothesis only.** Good for understanding a mechanic in prose. Every number, token name or condition from it is ASSUMED until confirmed in source 1. |

When 3 contradicts 1, **1 wins, no discussion**. When 2 contradicts 1, you have misread one of the
two - go back and re-read, do not pick a side.

## Paths

| Source | Path |
| --- | --- |
| Game install | `C:\Jeux\steamapps\common\Hearts of Iron IV` |
| Expert AI 5.0 | `C:\Jeux\steamapps\workshop\content\394360\741805475` |
| Wiki | `https://hoi4.paradoxwikis.com/Hearts_of_Iron_4_Wiki` (WebFetch) |

Steam libraries move. If a path is gone, locate it with
`find <drive>:/ -maxdepth 5 -type d -iname "Hearts of Iron IV"` rather than concluding the
reference is unavailable.

**Version.** The install reads `1.19.2.0` (`launcher-settings.json`, field `rawVersion`) - the same
version the analysed campaigns ran. Expert AI 5.0 declares `supported_version="1.19.2.0"`. This
repo's `descriptor.mod` still says `1.18.0`; that is stale metadata, not the version campaigns run
on. Read `launcher-settings.json` rather than trusting either descriptor.

## What answers what

| Question | Open |
| --- | --- |
| Does this effect exist? what scope? what parameters? | install `documentation/effects_documentation.md` (217 KB) |
| Same for a trigger | install `documentation/triggers_documentation.md` (176 KB) |
| Is this modifier valid in this scope? | install `documentation/modifiers_documentation.md` (237 KB) - the scope oracle |
| Variable / array syntax, indexed reads, temp semantics | install `documentation/dynamic_variables_documentation.md` |
| Maths inside script | install `documentation/script_math_functions.md` |
| A console command for a manual in-game check | install `documentation/console_commands_documentation.md` |
| What does `ai_strategy type = X` mean? what parameters? | install `common/ai_strategy/_documentation.md` (712 lines, 103 tokens, **authoritative**) - see the per-folder documentation layer below |
| At what MAGNITUDE does the engine respond to that type? | not documented anywhere. Read real usage: install `common/ai_strategy/*.txt` and Expert AI `common/ai_strategy/EAI_MILITARY_strategies.txt` (98 KB) / `EAI_MILITARY_naval_strategies.txt` (73 KB) |
| Default value of an `NDefines` key | install `common/defines/00_defines.lua` (396 KB) - the full table. WA's `05_defines.lua` names only a quarter of it; see "`common/defines` is an override layer" below |
| How the engine groups a faction's members into theatres | install `common/ai_faction_theaters/_documentation.md` for the FORMAT. The live content is **WA's own** since 2026-08-18 (`common/ai_faction_theaters/`, generated) - vanilla's region lists no longer described WA's re-cut map. |
| Vanilla AI plan structure | install `common/ai_strategy_plans/`, and Expert AI's for a second reading |
| Does this token exist AT ALL, when no doc mentions it? | **grep `hoi4.exe` for the literal string** - and put a control string that cannot exist in the same run, or the test proves nothing. This settled `naval_invasion_support_priority` (2026-08-18): absent from both editions of the type doc, present in the binary, used 7x by vanilla `ENG.txt` - a documentation-only audit had called it an invented type. `force_ratio`, checked the same way, really is absent. **"Not in `_documentation.md`" is not evidence a token does not exist.** |

## The per-folder documentation layer - the part everyone misses

Beyond the six oracles in `documentation/`, the install ships **39 `_documentation.md` files, one
inside the `common/` subfolder it documents.** No WA document referenced them before 2026-08-18,
and a session that year asserted in writing that `ai_strategy` type tokens had no engine
documentation. That was **false** - the file was 712 lines long the whole time. If you are about to
say "the engine does not document X", run
`find "<install>/common" -maxdepth 3 -iname "*documentation*.md"` first.

The ones that matter here:

| File (under install `common/`) | Documents |
| --- | --- |
| `ai_strategy/_documentation.md` | **103 `type =` tokens** grouped by domain (diplomacy, fronts and armies, navies, intelligence, production and resources, airforce, raids), then a detailed section per type with parameters and examples. Covers the types WA leans on daily: `front_unit_request`, `invasion_unit_request`, `put_unit_buffers`, `front_control`, `invade`, `protect`, `theatre_distribution_demand_increase`, `dont_defend_ally_borders` and the three `force_concentration_*` types the AIFC system is built on. Header says "updated 2024-11" - treat undated behaviour as MEASURED-but-possibly-stale and confirm against 1.19.2 usage. |
| `ai_faction_theaters/_documentation.md` | The faction-theatre FORMAT (the live content is WA's generated file since 2026-08-18). |
| `ai_navy/_documentation.md`, `ai_navy/taskforce/_documentation.md` | Fleet / task-force AI. |
| `ai_templates/_documentation.md`, `ai_equipment/_documentation.md` | Division-template targeting and equipment-variant selection. |
| `peace_conference/ai_peace/_documentation.md` | AI peace-conference behaviour. |
| `script_constants/documentation.md` | The `constant:` mechanism - pairs with skill `wa-constants-registry`. |
| `on_actions/_documentation.md`, `decisions/_documentation.md`, `resources/_documentation.md`, `doctrines/*/_documentation.md`, `military_industrial_organization/*/_documentation.md`, `operations/_documentation.md`, `factions/_documentation.md`, `units/equipment/_documentation.md`, `strategic_locations/documentation.md` | Their own systems. |

`documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` in this repo is a WA-side inventory of which type
lives in which layer. It is **not** a substitute for `ai_strategy/_documentation.md`: ours says
where a type is used here, the install's says what it does.

## Vendored copies - use the manifest, not the folder

Replacing a vanilla folder copied its `_documentation.md` along with it, so `common/` holds **28
engine docs frozen at whatever patch they were taken from**. `python tools/check_engine_docs.py`
reports every one:

| Verdict | Meaning |
| --- | --- |
| listed in `tools/engine_docs_manifest.json` | SYNCED and citable. Drift against the install is an ERROR, and so is the install changing under it (game patched -> re-read everything citing it). |
| `STALE` | a frozen older edition. **Do not cite it** - read the install. Zero as of 2026-08-18. |
| `UNSYNCED-OK` | identical to the install today, but nothing holds it there. **Eight docs sit here on purpose (2026-08-18).** Measured: of the nine that were UNSYNCED-OK, exactly one is cited by anything - `common/script_constants/documentation.md`, referenced by `wa-constants-registry` and by this file - and that one is now in the manifest. The other eight (`collections`, `doctrines/folders`, `map_modes`, `scientist_traits`, the three `special_projects` docs, `strategic_locations`) have **zero citations anywhere in the repo**. Holding them would make the next game patch raise an ERROR demanding a re-read of documents nothing depends on. Add one to the manifest the day something cites it, not before. |

**All 19 vendored docs are synced as of 2026-08-18** - `ai_strategy` first, then the remaining 18
in the same session. Each carries a `WA-SYNC` header naming the install path, the edition and what
the frozen copy was missing. **Cite these files by section name**
(`documentation.info section put_unit_buffers`) - a line number is a silent-drift mechanism, a
section name is not.

What the refresh found, and where it matters:

| Refreshed doc | Token / behaviour that was absent from the frozen copy |
| --- | --- |
| `common/ai_strategy/documentation.info` | the three `force_concentration_*` types the AIFC system is built on; `naval_invasion_supremacy_weight` renamed `naval_invasion_dominance_weight` |
| `common/factions/_documentation.md` | **five ai_strategy types**: `spent_faction_initiative_priority` (ids `program`, `unlock_doctrine_sharing`, `unlock_faction_commander`) and `become_spymaster` / `become_head_of_crypto` / `become_head_of_counter_intel` / `become_head_of_operations`. The Faction-Upgrade subsystem the old copy described is gone. |
| `common/on_actions/documentation.info` | was the **2022-09** edition. It gained `on_before_peace_conference_start` and `on_deployed_leader_defeated`, both **live** tokens with scope notes. **Exactly one token is marked `[deprecated]`: `on_ruling_party_change_immediate`** ("Unsafe behavior, prefer using on_ruling_party_change instead") — and WA does not use it. An earlier reading of this refresh listed all three as deprecated; corrected 2026-08-18 against the install, which lists the other two under Politics and Diplomacy/War with no such mark. WA calls both (`12_wuw_on_actions.txt`, `00_on_actions.txt`) and that is fine. |
| `common/military_industrial_organization/organizations/documentation.info` | MIO equipment stat `naval_supremacy_factor` renamed `naval_dominance_factor` |
| `common/operations/_documentation.info` | `outcome_execute_extra` renamed `outcome_extra_execute`; unmet requirements now cancel a running operation |
| `common/doctrines/tracks/_documentation.md` | the `active = { ... }` gate on subdoctrine selection and mastery gain |
| `common/units/equipment/_documentation.info` | `max_military_factories`, `max_dockyard_factories` |
| `common/ai_equipment/_documentation.info` | `history = yes` |
| `common/raids/_documentation.md` | the whole custom success-chance-modifier system, plus `ai_min_success_chance` and `max_distance` |
| `common/characters/_documentation.md` | `can_be_captured`, the `scientist` role |
| `common/doctrines/grand_doctrines/_documentation.md` | `max_track_rows`, `max_track_columns` |
| `common/focus_inlay_windows/documentation.md` | `scripted_buttons`, `scripted_progressbars` |

Three vendored copies had been hand-edited and the sync discarded those edits, deliberately:
`ai_equipment` (five WA inline annotations, commit `c4883822b`), `raids` and
`special_projects/projects` (WA unit renames inside engine examples, commits `f647c2770` and
`abd3a3c9b`). None of the three is loaded by the game.

If the install is not present (cloud runner), the checker SKIPS and exits 0 rather than failing.

## The replace_path trap - a base-game file means two different things

Before citing a base-game file, check whether `descriptor.mod` replaces its folder.

| Folder replaced by WA? | What reading the base file tells you |
| --- | --- |
| **Yes** - `common/ai_strategy`, `scripted_effects`, `scripted_triggers`, `on_actions`, `decisions`, `ideas`, `units`, `technologies`, `national_focus`, `events`, `tests`, ~110 paths in all | The file **does not load** in WA. It is what vanilla did: useful as design reference, or to see a token in real use. **Never citable as "the game does X".** |
| **No** | The file **is live** in every WA campaign, unchanged. |

**The trap does not apply to `_documentation.md` files.** They describe engine-side behaviour, not
vanilla content, so `common/ai_strategy/_documentation.md` is authoritative even though
`common/ai_strategy` is a replaced folder. Replace_path decides what *script* loads, not what the
engine does with a token.

Live, AI-relevant, and confirmed absent from `descriptor.mod`'s replace list:

| Live base folder | Why it matters |
| --- | --- |
| `common/defines/` | Base `00_defines.lua` loads first, WA's `05_defines.lua` overrides individual keys on top - the section right below this table. |
| `common/ai_attitudes.txt`, `common/ai_personalities.txt` | Small, live, and owned by nobody in this repo. |

`common/ai_faction_theaters/` used to be listed here - **no longer true since 2026-08-18**: the
folder is now on `descriptor.mod`'s replace list (line 13) and the live content is WA's own
generated `ai_faction_theaters.txt` (`tools/gen_ai_faction_theaters.py`, `--dry-run` first - never
hand-edit). Vanilla's 22 KB copy no longer loads. See `documentation/WA_AI_MILITARY_SYSTEM.md` §15.

### `common/defines` is an override layer, not a table

`common/defines` is **absent from `descriptor.mod`'s replace list**, so both files load: the
install's `00_defines.lua` first, WA's `05_defines.lua` on top, and each assignment in WA's file
rebinds **one key**. `05_defines.lua` is a diff, not a state.

| File | Keys it names |
| --- | --- |
| install `common/defines/00_defines.lua` (1.19.2.0) | **3230** |
| WA `common/defines/05_defines.lua` | **854** - 26 % of the table; of `NDefines.NAI` alone, 288 of 946 |

Two readings of that diff are wrong, and both come from opening only WA's file:

- **"WA does not set it, so it is unset / zero / disabled."** It has vanilla's value, and vanilla's
  value is in the install, not in this repo. `NDefines.NAI.AIFC_MAX_NR_FRONTS` is **4**
  (`00_defines.lua:3500`) and WA names **none** of the 50 `AIFC_*` keys - the whole AI force
  concentration system runs on vanilla numbers.
- **"I changed WA's value, so the behaviour is now X."** Incomplete until you know what it was.
  `NDefines.NAI.MAX_DEPLOYED_ARMY_HQS` is `5` (`00_defines.lua:3423`) and `20`
  (`05_defines.lua:1040`) - a 4x that neither file states on its own.

So a define's live value is `05_defines.lua` when the key is there and `00_defines.lua` when it is
not. Grep both before quoting one.

## Expert AI - how to use it, how not to

Expert AI 5.0 solves the same problem WA solves - making the HOI4 AI play well - on the same
engine version. Its AI surface is large: `EAI_MILITARY_strategies.txt`,
`EAI_MILITARY_naval_strategies.txt`, `EAI_BUILDING_construction_strategies.txt` (628 KB),
`EAI_COUNTRY_diplomacy_lend_lease_strategies.txt` (77 KB), plus `ai_strategy_plans`, `ai_areas`,
`ai_navy`, `ai_templates`, `scripted_effects`, `scripted_triggers`, `on_actions` and `defines`.

Use it for:

- **Existence proof.** If EAI uses `type = X`, that token works on 1.19.2.
- **Magnitude calibration.** Its values for a given type show the scale the engine responds to -
  something no documentation states and that WA has repeatedly had to guess.
- **Prior art on decomposition.** How another author split the same problem into files.

Do not:

- Copy a block. Different mod, different assumptions, different balance.
- Cite it as engine behaviour. It is one author's reading of the engine, exactly like ours.
- Use it to bypass WA's own rules. The 4-layer military model, the `WA_AI_CONFIG` archetype rule
  and `AGENTS.md` principles 1-3 apply to anything inspired by it.

## The wiki - how to use it, how not to

`https://hoi4.paradoxwikis.com/Hearts_of_Iron_4_Wiki`, via WebFetch. The AI page is
`https://hoi4.paradoxwikis.com/AI_modding` - sections for AI strategies (with a `type =` list),
areas, focuses, peace, strategy plans, templates and equipment.

That page is a useful *index* - it groups the types and shows worked examples in prose. But it
**defers to the install itself**, in its own words: the authoritative list lives in the game's
`common/ai_strategy` documentation file. So use the wiki to find out that a type exists and roughly
what family it is in, then read the install file for what it actually does. A type present on the
wiki and absent from `_documentation.md` is ASSUMED, not a discovery.

**Use it to understand a mechanic** - what supply throughput is for, how naval invasions are
planned, what feeds air superiority. Prose explanation of intent is what it is good at, and the
install's documentation is deliberately terse about it.

**Never use it to source a number, a token name, a scope or a condition.** It lags patches, often
by several, and pages routinely describe behaviour removed two versions ago. Anything taken from
the wiki is **ASSUMED** and must be confirmed in the install before it enters a fix, a probe or a
checklist item.

## The check, in one line

A sentence about engine behaviour carries either a `file:line` from the install, or the label
**ASSUMED**. There is no third option.
