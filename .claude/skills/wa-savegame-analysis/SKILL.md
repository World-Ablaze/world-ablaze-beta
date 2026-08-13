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

Inline exception: a single `meta FILE` on an already-known file is small enough to run directly, as is `army TAG FILE...` (one line per save). Everything else — `campaigns`, `sections`, `section`, `var`, `ideas`, `flags`, `tlm`, `resources`, `buildings`, `decisions` — runs inside a subagent.

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
| `tlm TAG FILE... [--match RE]` | WA_TLM telemetry dashboard: scalars (stamps decoded to dates) + ring-buffer series paired with the `wa_tlm_hist_t` axis. Contract and metric registry: `documentation/WA_TLM_TELEMETRY_SYSTEM.md`. |
| `army TAG FILE...` | **Deployed** division count — `division={` blocks inside `units` only — with `num_armies_for_training` and `wa_tlm_comp_div_total` as cross-checks. Never hand-count divisions; see the units-scoping gotcha below. |
| `resources TAG FILE...` | Per-resource ledger: `produced`, `transfer_overlord_subject`, `imported`, net available (`to_use[0]`), unmet demand (`to_use[2]`), `to_export`, actually `exported`, plus the balance identity's residual. |
| `buildings TAG FILE... [--match RE]` | Building levels summed over states, **owned vs controlled** columns, with each `*_inactive` twin listed under its active counterpart. This is how refinery on/off becomes visible (R29). |
| `decisions TAG FILE... [--match RE]` | Decodes `decision_status`, labelling each entry kind separately: live `active_*`/`decision_to_*` entries carry a `days` countdown; `random_item` entries carry a **cumulative fire counter**. |

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
- **`division={` blocks live in two sibling sections — count only the ones in `units`.** `experience_status` holds `xp_by_template` entries whose `division={ id= type= }` references are *siblings* of `units`, not nested inside it, so a whole-country-block count over-reports by 8–10% (USA 1944.1 = 97 total vs **80** deployed; SOV 1942.6 = 409 vs **373**). Use the `army` command. Its two cross-checks are not equivalent: `wa_tlm_comp_div_total` matches the units-only count (20/21 tag×date cells checked on `911bed3c`, one 1-division monthly-sample lag), while `num_armies_for_training` tracks it only while the army is stable and **overstates during losses** (ITA 1946.4: 28.0 vs 16 deployed).
- **`resource@X` in script reads NET available, not `produced`.** The ledger's `to_use[0]` is what the trigger sees. A negative `produced` line with positive `imported` / `transfer_overlord_subject` is still a *positive* `resource@X` — ENG 1942.6 is `produced.bauxite = −329`, `imported = +320`, `transfer = +19`, net **+10**. Scoring a `resource@X` guard off the `produced` line alone nearly produced a false FAIL on checklist item R25. Use the `resources` command, which prints all seven columns side by side.
- **`decision_status` mixes two entry kinds whose numbers mean different things.** `active_timed_decision={ decision= days= state= }` exists **only while live**: with `state=active`, `days` is time *remaining* (≤ the decision's `days_mission_timeout`); with `state=failed` or `re_enable_cooldown` the same field is a **re-arm cooldown on a different clock** — verified unrelated to the timeout (`economy_fatigue_export_focus_mission` has `days_mission_timeout = 70` and shows `days=13` when failed; `iron_shortage_ai` has timeout 9 and shows 12). `random_item={ decision= count= target= }` is not a state and not days at all — `count` is a **monotone cumulative fire counter**, and it is the field to read for "how many times did this decision fire". Conflating the two has already happened twice in one session; use the `decisions` command, which labels them apart.
- **A state block omits `controller=` when the controller is the owner.** Reading it literally makes a country look like it controls only its conquests (ENG 1946.4: 3 "controlled" states instead of 75). The `buildings` command defaults controller to owner; do the same in ad-hoc parsing.
- **Production lines live in THREE sibling blocks — `military_lines`, `naval_lines` and `air_lines`.** Scoping a production scan to `military_lines` alone silently returns **zero** submarine and zero aircraft lines (a whole campaign reads as "the AI never built subs"); scoping to none of them pulls `equipment_variant_index` out of design and licence blocks and inflates tank counts several-fold. Name all three explicitly. Related, and already burned twice: resolve every `equipment_variant_index` through the top-level `equipments={}` registry and select on **`archetype`**, never on the variant name — this mod has no generic `infantry_equipment_N` stock for its majors (GER rifles are all `ger_inf_*`), so a name-prefix filter undercounts GER by ~70× while looking plausible on recipients whose stock happens to carry the vanilla name.
- **`var`'s regex is matched against the whole `name=value` string, not the name alone.** A `$`-anchored pattern (`"^wa_ai_foo$"`) therefore matches nothing and returns the same "no variable matching" as a genuinely absent variable. Anchor with a trailing `=` instead (`"^wa_ai_foo="`), or with `\^` for arrays.
- **Absence of a country variable does not prove a build lacks the fix that writes it — check the write site's scope first.** `WA_AI_PC_state_type_projects` (Fix 46) is written inside `var:WA_AI_PC_target_state^_project_id = { … }`, i.e. **state scope**, so `var ENG` reports it absent on a build that has it. One build-fingerprint pass concluded a whole commit was OUT on that basis and mis-scored the campaign's headline item until a country-scope fingerprint (`wa_ai_pc_type_id` carrying the new tag values) settled it. Prefer fingerprints you have confirmed are written in the scope you are probing.

## WA_TLM telemetry (builds from 2026-08-11 on)

Instrumented builds carry a standardized `wa_tlm_*` namespace on every country
(design: `documentation/WA_TLM_TELEMETRY_SYSTEM.md`). Three things change how you probe:

- **Trends may not need multi-save parsing.** Ring-buffer series (`*_hist` paired with
  `wa_tlm_hist_t`) carry up to 11 game-years of quarterly samples inside the *latest* save —
  run `tlm TAG <last-save>` before planning an 8-save `var` sweep.
- **Absence is tri-state and trustworthy:** no `wa_tlm_*` at all = pre-TLM build (probe
  void, never FAILED); metric 0 with `_last_t` 0 = code path never sampled; metric 0 with
  `_last_t` > 0 = a real zero reading.
- Time is encoded as `global.WA_TLM_clock` = months since 1936.1; the `tlm` command decodes
  it (`101` → `1944.6`). Raw `var` output shows undecoded clock values.

Legacy `wa_ai_*_dbg_*` families remain per-fix and retire with their checklist items —
probe them exactly as each item's `Probe:` line says.

## Trend workflow

1. Selection subagent: `campaigns` → identify the campaign and its date-ordered saves; main agent confirms with the user if ambiguous.
2. Extraction subagent: pass the chosen files to `var` / `ideas` in one call — output is already date-sorted, one line per save per hit — and have it return the trend as a small date-vs-value table.
3. Main agent interprets the table against the owning system's cadence (see `wa-ai-systems` for which pulse writes what).

Example — how ITA's resource-need assessment evolved across a campaign:

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py var ITA "^wa_ai_needs_" GER_1939_05_13_13.hoi4 GER_1940_05_22_03.hoi4 GER_1943_03_02_02.hoi4
```

Example — the R29 refinery-shutdown shape (park on/off, the ledger behind it, and how often the two controllers fought over it):

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py buildings ENG 1944.4_Apr.hoi4 1946.4_Apr.hoi4 --match refinery
python .claude/skills/wa-savegame-analysis/scripts/savegame.py resources ENG 1944.4_Apr.hoi4 1946.4_Apr.hoi4
python .claude/skills/wa-savegame-analysis/scripts/savegame.py decisions ENG 1946.4_Apr.hoi4 --match "bauxite_shortage_ai|reactivate_aluminium"
```

Example — whether the WA_AI cheat ideas were still on GER by 1943:

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py ideas GER GER_1939_05_13_13.hoi4 GER_1943_03_02_02.hoi4 --match "WA_AI|economy_fatigue"
```
