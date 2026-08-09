---
name: wa-savegame-analysis
description: Navigating and extracting data from HOI4 savegames to verify World Ablaze behaviour in real campaigns — selecting saves, determining which saves belong to the same campaign, and reading variables, ideas, flags, politics, and ai_strategy state out of 60–150MB save files. Use this whenever a task involves checking what actually happened in a game (as opposed to what the script says should happen), tracking how a value or idea evolved over months/years of a campaign, or debugging AI misbehaviour reported from a playthrough. Never open a savegame with Read or plain grep — this skill's streaming script is the only practical way in — and run the exploration in subagents so the bulky output never enters the main context.
---

# WA savegame analysis

Savegames are the ground truth for how the mod actually behaved in a campaign. Use them to verify AI systems (did the variable get set? did the idea get applied? when?), to trace trends over in-game time, and to debug reports from playthroughs.

## Context discipline — subagents do the exploring

Savegame output is bulky even through the script: a `campaigns` listing over a real save dir runs hundreds of lines, and `section`/`var`/`ideas` output scales with what you ask for. The main agent must not run exploration commands inline — delegate to subagents (Explore for read-only extraction) and keep only the distilled result:

1. **Selection pass** — one subagent runs `campaigns` (plus `meta` where needed), filters to relevant mods and save file dates, and returns a *compact shortlist*: campaign id, save filenames with in-game dates and player tags, and any branched-timeline warnings. Subagents cannot talk to the user, so ambiguity comes back to the main agent, which resolves it with AskUserQuestion.
2. **Extraction pass** — one subagent per independent question (different campaigns, countries, or systems can run as parallel subagents). The prompt must be self-contained: tell it to read this SKILL.md first, then give the exact save files, country tag, section/pattern, and the shape of the answer you want (date-vs-value table, idea presence matrix, matched lines only).
3. The main agent interprets the distilled results against the owning mod system (see `wa-ai-systems` for cadence).

Every extraction subagent prompt should end with an instruction like: *"Return only the distilled table/findings and any anomalies you noticed. Do not echo raw command output, section dumps, or file contents."*

Inline exception: a single `meta FILE` on an already-known file is small enough to run directly. Everything else — `campaigns`, `sections`, `section`, `var`, `ideas`, `flags` — runs inside a subagent.

## The helper script

All access goes through [savegame.py](scripts/savegame.py) (stdlib-only, streams a single pass per file):

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py <command>
```

| Command | Purpose |
| --- | --- |
| `list [--dir D] [--limit N]` | Saves newest-first with date, player, campaign id, session, size. |
| `campaigns [--dir D]` | Group all saves by campaign identity, date-ordered within each group. **Start here when selecting saves.** |
| `meta FILE` | One save's header: player, date, version, session, seed, unique id, mods, ironman, start_date. |
| `sections FILE TAG` | Depth-2 sections of a country block with line counts — the navigation map before extracting. |
| `section FILE TAG NAME [--grep RE] [--max-lines N]` | Dump one country section (`variables`, `politics`, `ai`, `flags`, `focus`, `production`, `technology`, …). Default cap 400 lines; `--max-lines 0` = unlimited. |
| `var TAG PATTERN FILE...` | Country variables matching a regex, across several saves, date-ordered — the trend command. |
| `ideas TAG FILE... [--match RE]` | Active ideas (+ `timed_idea` days remaining, ruling party, political power) across saves, date-ordered. |
| `flags FILE [TAG] [--match RE]` | Global flags (no TAG) or country flags, each with value and set-date. |

Bare filenames resolve against the default save dir: `~\Documents\Paradox Interactive\Hearts of Iron IV\save games`. Files are 60–150MB / ~4.4M lines — never Read one, never load one into memory, and don't trust shell `grep` here (the rtk proxy mangles its output; the script or a streaming Python one-liner is the reliable path).

## Save formats

First 7 bytes decide everything; the script checks them and refuses what it can't parse:

- `HOI4txt` — plain text, fully readable.
- `HOI4bin` — ironman/binary. **Not parseable**; tell the user that save can't be analyzed (they can re-save non-ironman).
- `PK…` — zip-compressed save; the script transparently reads the inner `gamestate`.

## Selecting saves and campaign identity

- **`game_unique_id` (a GUID in the header) is the campaign identity.** Same id = same campaign, full stop.
- `game_unique_seed` is NOT sufficient — real save dirs contain distinct campaigns sharing a seed.
- The filename tag (`GER_1944_10_29_06.hoi4`) is only *who was being played at save time*. One campaign's saves can carry many tags (players tag-switch to inspect AI countries), and `autosave.hoi4` belongs to whatever was played last. Never group by filename.
- Check `mods=[…]` in `campaigns` output: the save dir mixes World Ablaze campaigns with other mods (Kaiserreich, Road to 56, …). Only `World Ablaze BETA LOCAL` saves are relevant to this mod, and even those may be from an older mod revision — compare the save's real-world file date against recent mod changes before drawing conclusions.
- Order saves within a campaign by in-game `date`, not by `session`. If `session` order contradicts `date` order, the player reloaded an earlier save and the campaign has **branched timelines** — the saves are not one consistent history.

**Ask the user (AskUserQuestion) instead of guessing** when: the campaign they mean is ambiguous (several groups match "my Germany game"), a campaign has branched timelines and the branch choice changes the answer, or the only candidate saves are ironman/binary.

## Save file structure

Top of file (first ~200 lines): `player`, `date` (format `Y.M.D.H`), `version`, `session`, `game_unique_seed`, `game_unique_id`, `mods`, saved event targets, then the **global flags** block (`flags={}`, with set-dates — a ready-made campaign timeline: war starts, civil wars, WA_AI init flags), `gameplaysettings` (ironman/historical), `start_date`.

Countries live in `countries={ TAG={ … } }`. Useful depth-2 sections inside a country block (run `sections` for the full per-save list):

| Section | Contains |
| --- | --- |
| `variables` | All country variables, **alphabetical**. Arrays as `name^0`, `name^1`, …, `name^num`. |
| `politics` | `ideas={ space separated list }` (all active ideas incl. hidden WA_AI ones), `timed_idea` blocks with days remaining, `ruling_party`, `political_power`, party popularity. |
| `flags` | Country flags with value + set-date. |
| `ai` | Engine AI state incl. active `ai_strategy={ type=… id=… value=… }` entries (numeric type codes). |
| `focus` | Focus progress and completed list. |
| `technology`, `production`, `resources`, `buildings`, `units`, `diplomacy`, `decision_status` | What their names say; `units` is by far the largest (~18k lines). |

## Gotchas (verified against real saves)

- **Variable names are lowercased in saves.** Script-side `WA_AI_needs_iron` is stored as `wa_ai_needs_iron`. Flag names keep their case. Search variables in lowercase or case-insensitively.
- An absent variable means *never set*, not zero — a country that was player-controlled (or never hit the code path) simply lacks the variable.
- The save's own indentation lies: malformed blocks put braces at column 0 mid-file. The script counts braces instead of trusting indentation; do the same in any ad-hoc parsing.
- Line numbers of anchors (`countries={`, a tag block) differ per save — never reuse offsets across files.
- Saves are snapshots at in-game hour granularity. A weekly-cadence AI value observed in a save was computed at the most recent pulse before the save date, not at the save date itself.

## Trend workflow

1. Selection subagent: `campaigns` → identify the campaign and its date-ordered saves; main agent confirms with the user if ambiguous.
2. Extraction subagent: pass the chosen files to `var` / `ideas` in one call — output is already date-sorted, one line per save per hit — and have it return the trend as a small date-vs-value table.
3. Main agent interprets the table against the owning system's cadence (see `wa-ai-systems` for which pulse writes what).

Example — how ITA's resource-need assessment evolved across a campaign:

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py var ITA "^wa_ai_needs_" GER_1939_05_13_13.hoi4 GER_1940_05_22_03.hoi4 GER_1943_03_02_02.hoi4
```

Example — whether the WA_AI cheat ideas were still on GER by 1943:

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py ideas GER GER_1939_05_13_13.hoi4 GER_1943_03_02_02.hoi4 --match "WA_AI|economy_fatigue"
```
