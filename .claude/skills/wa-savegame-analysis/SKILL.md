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

Inline exception: a single `meta FILE` on an already-known file is small enough to run directly, as is `army TAG FILE...` (one line per save) and `navy TAG FILE...` without `--fleets` (three lines per save). Everything else — `campaigns`, `sections`, `section`, `var`, `ideas`, `flags`, `tlm`, `resources`, `buildings`, `decisions`, `pc` — runs inside a subagent. (`pc --match no_such_thing` suppresses the project table and leaves only the ~10-line summary per save, which is the shape to ask a subagent for when the question is about factory share or queue depth rather than individual projects.)

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
| `navy TAG FILE... [--fleets]` | Fleet / task-force / **mission** breakdown: ships by mission, escort-hull (`screen_ship`) counts, idle share, and how much of the idle sits in fleets with no admiral. The mission enum is named nowhere in the game files — the map lives in `_NAVAL_MISSIONS` in the script (checklist R36). |
| `army TAG FILE...` | **Deployed** division count — `division={` blocks inside `units` only — with `num_armies_for_training` and `wa_tlm_comp_div_total` as cross-checks. Never hand-count divisions; see the units-scoping gotcha below. |
| `resources TAG FILE...` | Per-resource ledger: `produced`, `transfer_overlord_subject`, `imported`, net available (`to_use[0]`), unmet demand (`to_use[2]`), `to_export`, actually `exported`, plus the balance identity's residual. |
| `buildings TAG FILE... [--match RE]` | Building levels summed over states, **owned vs controlled** columns, with each `*_inactive` twin listed under its active counterpart. This is how refinery on/off becomes visible (R29). |
| `decisions TAG FILE... [--match RE]` | Decodes `decision_status`, labelling each entry kind separately: live `active_*`/`decision_to_*` entries carry a `days` countdown; `random_item` entries carry a **cumulative fire counter**. |
| `pc TAG FILE... [--match RE] [--limit N]` | Priority-construction queue: every project with its building type, strategy tag and priority band **by name**, plus a per-country summary (factory share, allocation override, gate counters) and the queue-invariant alarms. Absent and 0 are printed apart — see the gotcha below. |

Companion helper, same directory: `regions.py <id>…` / `regions.py --grep <regex>` turns a
strategic-region id (fleet `strategic_region={}`, `regional_convoys` indices, every
`naval_avoid_region`) into its in-game name. Do not resolve these by hand — WA replaces
vanilla's whole region table and two of its files disagree with their own id (see the
region-id entry in `wa-lessons-learned`).

Second companion: `cvair.py <save>…` (`--miss` for per-role and per-mission detail) — the
**carrier-deck vs land-airfield split of every country's `cv_*` aircraft**, in one pass per
save. Wings live at `strategic_air → <TAG> → air_wing_pool → air_wings`, and a wing is on a
carrier deck iff its `air_base` id has **no `state=`** in the depth-1 `air_base={}` map. It
anchors strictly on depth because `count=` also occurs one level deeper inside combat-history
`enemy={}` records — counting both over-reports ENG by 7×. Consumer: checklist R43.

Third companion: `airload.py [--states ids] [--owner TAG] [--tag TAG] [--top N] [--all] <save>…` —
**air-base LOAD per state: NOMINAL wing slots vs capacity, beside planes present.** The engine
books capacity per WING at the wing's fixed type size (`land_air_wing_size` in
`common/units/air.txt`: 100 for every type except tac_bomber 200, strat/heavy_strat 300,
scout/maritime_patrol 25), not per plane present; a wing's `definition=` is that `sub_units`
key, so the nominal load is derivable from the save while planes-present is not the load at
all. Verified on `af003548` 1944.7: 7 of the 11 UK hosting states sit at exactly 100.0 %
nominal while reading 86–98 % in planes. Consumers: R8, R15, R52 — any "is there room on
these airfields" question.

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
- **`resource@X` in script reads `to_use[0] + to_use[2]` — net available MINUS unmet demand.** Neither `produced` nor `net` alone. The `resources` command prints it as the **EFFECTIVE** column. ENG aluminium at 1942.6 is net `807.3`, deficit `−799.0`, **effective `+8.3`** — which is why its `> 50` latch stayed shut while the net column looked like 16× headroom. Measured 2026-08-13 on campaign `02bd4445` against the `WA_AI_EQUIPMENT_*` latches: **36 discriminating (country, date, resource, bar) cells all side with net+deficit and zero with net**, with pass/fail bracketing the bars to within one unit. *The superseded "net alone" rule was drawn from ENG **bauxite** in the same save, whose deficit happens to be −1.0 so both readings coincide there — one resource where the two agree is not evidence for the general rule.* The `produced`-alone mistake is still a mistake (it nearly produced a false FAIL on R25); this correction makes the *right* column two columns over.
- **`decision_status` mixes two entry kinds whose numbers mean different things.** `active_timed_decision={ decision= days= state= }` exists **only while live**: with `state=active`, `days` is time *remaining* (≤ the decision's `days_mission_timeout`); with `state=failed` or `re_enable_cooldown` the same field is a **re-arm cooldown on a different clock** — verified unrelated to the timeout (`economy_fatigue_export_focus_mission` has `days_mission_timeout = 70` and shows `days=13` when failed; `iron_shortage_ai` has timeout 9 and shows 12). `random_item={ decision= count= target= }` is not a state and not days at all — `count` is a **monotone cumulative fire counter**, and it is the field to read for "how many times did this decision fire". Conflating the two has already happened twice in one session; use the `decisions` command, which labels them apart.
- **A ship's `history` contains other ships.** `ship={}` blocks carry `sunk_ship={ … definition=<the VICTIM's hull> … }` kill records nested three levels down, so counting every `definition=` inside a ship reads each successful sub-hunting destroyer as a submarine. It produced a confident, wrong "ENG has 204 cruiser_submarines and its escort task forces are half full of submarines" (2026-08-13) — the escort task forces are in fact pure screens. Count `definition=` at ship depth **1** only; `navy` does, ad-hoc parses must.
- **Task forces are not the unit of naval AI — fleets are.** A mission is attached to the task force but granted at the fleet level: a fleet with no `strategic_region={}` has every task force idle, without exception in a 10-year campaign. Read fleets before concluding anything about naval behaviour (`navy --fleets`).
- **A state block omits `controller=` when the controller is the owner.** Reading it literally makes a country look like it controls only its conquests (ENG 1946.4: 3 "controlled" states instead of 75). The `buildings` command defaults controller to owner; do the same in ad-hoc parsing.
- **Production lines live in sibling blocks — name `military_lines`, `naval_lines` and `air_lines` explicitly.** Scoping a production scan to `military_lines` alone silently returns **zero** submarine lines (a whole campaign reads as "the AI never built subs"); scoping to none of them pulls `equipment_variant_index` out of design and licence blocks and inflates tank counts several-fold. Name all three explicitly. Related, and already burned twice: resolve every `equipment_variant_index` through the top-level `equipments={}` registry and select on **`archetype`**, never on the variant name — this mod has no generic `infantry_equipment_N` stock for its majors (GER rifles are all `ger_inf_*`), so a name-prefix filter undercounts GER by ~70× while looking plausible on recipients whose stock happens to carry the vanilla name.
  - **Correction (2026-08-14, `f9321934`): aircraft lines are in `military_lines`, not `air_lines`.** The earlier wording here said `military_lines`-only scoping also loses aircraft; it does not. Measured on `1944.6_Jun.hoi4`: SOV 19 `military_lines` + 3 `naval_lines`, USA 35 + 34, GER 24 + 12, ENG 23 + 19, and **no `air_lines` block on any of them** — while SOV's `SOV_la_7_airframe` and `SOV_il_10_airframe` lines sit inside `military_lines`. The operational rule is unchanged (name all three; `air_lines` costs nothing and may exist elsewhere), but do **not** infer from its absence that a country built no aircraft, and never scope an aircraft scan to `air_lines` alone.
- **`var`'s regex is matched against the whole `name=value` string, not the name alone.** A `$`-anchored pattern (`"^wa_ai_foo$"`) therefore matches nothing and returns the same "no variable matching" as a genuinely absent variable. Anchor with a trailing `=` instead (`"^wa_ai_foo="`), or with `\^` for arrays.
- **The top-level `equipments={}` registry has no `archetype` field, and `obsolete` is write-only-`yes`.** An entry's *block key is the equipment definition name*; resolve archetype and the def-level `parent =` out of `common/units/equipment/*.txt`, never out of the save. `obsolete=no` never occurs — **absence is the non-obsolete state**. The entry's own `parent_id={}` is a *design-variant* lineage pointer (id→id) and is unrelated to the def-level `parent =`. Only entries carrying `name=` are designed variants (164 of 7 190 in the `02bd4445` final save); the rest are per-country type registrations. Registry presence means "this country has the type", which is a **weaker** claim than "researched it" — ENG holds non-obsolete `usa_hv_inf_3..6` it never researched.
- **`obsolete=yes` does not gate anything the AI does.** It is not an archetype-uniqueness marker (288 (creator, archetype) groups in the `02bd4445` final save hold two or more non-obsolete members, one of them five members of a single linear chain) and it does **not** stop production: 7.0% of all production lines and **9.6% of all assigned factories** in that save run obsolete-flagged equipment, including USA's 68-factory `tank_usa_medium_chassis_3` line and its 75-factory `usa_mechanized_equipment_4` line. The share *rises* through the campaign. Never conclude "the AI cannot build X" from an obsolete flag — check the lines.
- **`production_upgrade_desire_offset` is not serialized into a country's `ai` section.** Only ~10 numeric strategy type codes ever appear there (plan/area/country/template-shaped) and **no `ai_strategy` entry carries a negative value at all**. Verified with three ungated controls (including the long-standing `SOV_dont_build_shit_guns`), all equally invisible. So a save can never answer "did this strategy arm" — probe its *effect* on the production lines instead. The `ai`-section reading that works for R34's `invade` suppressions does not generalise to this type.
- **`date="1.1.1.1"` in `technology/technologies` marks a tech being researched RIGHT NOW, not a duplicate or a start-grant.** It carries accumulated `research_points`, no `level=`, and a twin entry under the sibling `technology/slots` block holding the slot's `points_factor`. A name-grep across the whole `technology` section therefore reports a false duplicate for every in-progress tech (ENG 6, GER 6, USA 3 in the `02bd4445` final save; exact 1:1 match with `slots` in all three). Scope to `technologies={}` and select on the presence of `level=`. Start-granted techs carry a real date (`1936.1.1.12`).
- **An annihilated tag keeps its country block, and every variable in it reads as a live value.** The block is never removed — only territory, army and the AI systems that write to it stop. On campaign `be18f9c7`, GER holds **0 owned / 0 controlled states and no `units` section from 1945.7 onward**, yet its 1946.7 block still reports a 4-project PC queue with `wa_ai_pc_assigned_factories_total = 14`, `wa_ai_fielded_eq_ratio` byte-identical at `0.93313` across 13 consecutive saves, and a `ruling_party` that flipped to communism. Everything freezes at the same boundary, so **any probe reading "the last save" for a dead tag is really reading its last live save** — here 1945.6, twelve months earlier. **Prove the tag is alive before trusting a late-campaign variable:** owned states > 0, or a `units` section present, or (on an instrumented build, cheapest) the family's `*_last_t` stamp equal to the live tags' — GER pins at `wa_tlm_comp_last_t = wa_tlm_nav_last_t = 113` while live tags read 126. Two other tells: byte-identical values across consecutive saves, and an aggregate contradicting its own array (that `= 14` total sits over `wa_ai_pc_assigned_factories^0..^3` all reading **0**). When a dead tag is the subject of the probe, run it on its last live save and say so in the evidence line. Distinct from the frozen-sector case in checklist R39/R42, which is a *live* tag the weekly on_action skips.
- **A global flag's set-date is a first-occurrence timestamp only if its `set_global_flag` is guarded.** Re-setting an already-set flag refreshes its date, so an unguarded write records the **latest** occurrence under a name that usually says "first". `first_nuke_dropped` is the live example: set unguarded in `common/on_actions/00_on_actions.txt` `on_nuke_drop` (vanilla-inherited), it reads **1946.5.18.24** on `be18f9c7` — the instant of `JAP_nuke_2` — while the first bomb fell **1945.12.5.23** per the guarded `JAP_nuke_1`, a 164-day error. Read the write site before dating any event from a flag, and anchor timelines on flags that are written once by construction. Same rule for `set_country_flag`.
- **Absence of a country variable does not prove a build lacks the fix that writes it — check the write site's scope first.** `WA_AI_PC_state_type_projects` (Fix 46) is written inside `var:WA_AI_PC_target_state^_project_id = { … }`, i.e. **state scope**, so `var ENG` reports it absent on a build that has it. One build-fingerprint pass concluded a whole commit was OUT on that basis and mis-scored the campaign's headline item until a country-scope fingerprint (`wa_ai_pc_type_id` carrying the new tag values) settled it. Prefer fingerprints you have confirmed are written in the scope you are probing.
- **In the PC queue, an absent per-project variable is not a zero — and three of the families are routinely absent.** `WA_AI_PC_start_project` never initialises `assigned_factories`, `stall_weeks` or `build_time`, and `WA_AI_PC_end_project_by_id` clears them, so a project that has never been funded, or has never yet been through a weekly stall sweep, simply has no entry. Script cannot tell the two apart (`check_variable` reads absent as 0) and neither can a naive parse — which is how "GER 1944.6 has 80 type-13 slots all at exactly 0" was reported for a queue where **none of the 80 carried a stall counter at all**. The `pc` command prints absent as `-` and zero as `0`. On the same save the right reading is "80 railway projects appended since the last assignment pass", which `pc` also states outright.
- **The queue array is sorted only *as of* the last assignment pass.** `WA_AI_PC_assign_factories` rebuilds `wa_ai_pc_queue` in descending priority order, but the strategies run from a 2-day background event and **append**, so a save taken mid-week shows a sorted prefix plus an unsorted tail. Reading queue position as priority rank across that boundary turns "queued three days ago" into "starved": on `be18f9c7` 1944.6, GER's two funded projects are priority-100 while 80 unfunded priority-1100 railways sit behind them, and nothing is wrong. `pc` reports the tail length explicitly.
- **Air-base capacity is booked per wing at the wing type's fixed size, not per plane present.** A save carries only `count=` on a wing (= Σ `equipment.amount`, 1 117/1 117 wings on `af003548` 1944.7); the nominal size is `land_air_wing_size` of the wing's `definition=` in `common/units/air.txt`. "Capacity − planes present" therefore over-reads free room by the wings' fill gap and once produced a confident "the UK held 3 800–5 700 spare slots and the USAAF still would not move" — the same states were at exactly 100.0 % nominal. Use `airload.py`, never a plane count, for any room-on-the-airfield question; the builders' `wa_ai_uk_air_dbg_planes` / `_capacity` gauges are plane counts too and read ~10 % under the true load.
- **The `buildings` header's `states owned=N controlled=M` is not a liberation reading.** "Controlled" counts every state the country controls, owned or not (colonies, Maghreb, states held for someone else), so owned = controlled proves nothing about the homeland: on `a232d96c` FRA read **58/58 at 1946.6 while GER held 20 of the 24 metropolitan French states**. To answer "is France liberated", walk `states={}` for the metropolitan ids (`controller=` defaulting to `owner=`) and count per controller — the direct walk read GER 20 / FRA 2 / RBE 1 / ITA 1.
- **`wa_tlm_nav_convoys`, `num_equipment@convoy` and `has_equipment = { convoy … }` read the FREE convoy pool — and a free pool of 0 IS a shortage; do not "correct" it with the fleet size.** The fleet is `convoys={ equipment={ … creator= } }` at depth 1 of the country block (sum the entries; `creator=` separates own-built hulls from exile / lend-lease ones), but the fleet count says nothing without the NEED, which is **not serialised**: on `a232d96c` ENG read free 0 for 46 months with a fleet of 627–842, and the in-game tooltip at 1944.6.1 showed 676 held / 676 used, trade **49 of 387** needed, supply 577 — a real famine that a first pass had dismissed as "the fleet never dropped below 600" (retracted the same day; the free pool is the only save-side proxy for Use/Need). `convoys_destroyed=` at country depth 1 is kills **by** that country (= `wa_tlm_nav_conv_killed`), not its losses.
- **Lend-lease ledgers are written from the GIVER's side and carry no payload; read direction off `first=`, not off the stockpile.** `active_relations/<B>/lend_lease={ first= second= start_date= }` sits in the **giver's** block with `first=` the giver (three fields — no equipment, amounts or fuel are ever serialised); `lend_lease_to_allies_history.ic_given` in A's block toward B is what **A gave B** (byte-equal to B's `ic_received` toward A); `recently_leased_ic` sits on the **receiver's** side; `diplomacy/proposed_diplo_action { action=lend_lease index= date= }` (country depth 2, `index` = 1-based position in the save's `countries={}` order) is the giver's *offer* stamp — a per-proposal retry cooldown that escalates 4/5/6/7 months and is written on accepted offers too. Two agents in one session (2026-08-16, `a232d96c`) inferred the mirrored convention from a single pair and inverted USA↔SOV; three control pairs (SOV→FRA, USA→CHI, ENG→SOV) settled it — the flow is **SOV → USA 101 697 IC**, and USA divisions hold 1 518 Soviet medium tanks to prove it. Do not size a lend-lease from `creator=` holdings either: the WA relief `send_equipment` legs move rifles without touching the ledger (SOV held 64k `usa_inf_3` in 1942 against 5.5k ledger IC), and `foreign_lease_equipments` is a type catalogue (captures included) with no amounts.

- **Air-wing mission state (verified `a232d96c` 1944.6/1944.9, all tags): the idle test is `mission={ type=0 }` / absent `strategic_region=` — never `active=` and never `mission={}` presence.** Every wing carries `mission={}` and `active=yes` on 1132/1132 wings, missions or not. Keys at `mission` depth 5: `type=` (bitmask: 1 air_superiority, 2 cas, 8 strategic_bomber, 16 naval_bomber, 512 attack_logistics, 1024 air_supply, 16384 recon; 0 = none), `strategic_region=` (assigned), `executing_mission=` (actually flying — `cvair.py --miss` keys "NO-MISSION" on its absence). At wing depth 4: `transferring_to=<STATE id>` (a state, not an air-base id — values 830–860 exceed the base-id space), `transfer_progress=` (accumulator, not %), `transfer_cancelled=yes|no`, `region_to_assign=`. Also: the depth-1 `air_base={}` block's `level=` is NOT the airfield level (Virginia reads `level=1` at capacity 800) — read `capacity=` (= state `air_base` × 100).
- **`naval_base` is not in the state blocks of these saves** — every state's `naval_base` sums to 0 in `1944.6_Jun` (`a232d96c`); naval bases are province-scoped in the top-level `provinces={}` block. `buildings … --match naval_base` therefore reads a silent 0 for every country; walk `provinces={}` and map through `history/states/<id>-*.txt` instead.

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

Example — what priority construction was doing for GER as its railway queue collapsed, and how much civ industry it was eating (the `--match` filter here is a deliberate no-match, so only the per-save summaries print):

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py pc GER 1944.6_Jun.hoi4 1944.9_Sep.hoi4 1944.12_Dec.hoi4 --match "^$"
python .claude/skills/wa-savegame-analysis/scripts/savegame.py pc ENG 1944.6_Jun.hoi4 --match "air_base|refinery" --limit 0
python .claude/skills/wa-savegame-analysis/scripts/savegame.py tlm GER 1944.12_Dec.hoi4 --match "^wa_tlm_pc_"
```

The third line is the other half of the same question on a v14+ build: `pc` reads the queue that survives, the `wa_tlm_pc_*` termination ledger says why the rest of it left (built / refused / swept / stale-path / orphaned / lost with the state / peace-purged), and `wa_tlm_pc_avail_share_pct` gives the allocation denominator no save carries.

Example — whether the WA_AI cheat ideas were still on GER by 1943:

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py ideas GER GER_1939_05_13_13.hoi4 GER_1943_03_02_02.hoi4 --match "WA_AI|economy_fatigue"
```
