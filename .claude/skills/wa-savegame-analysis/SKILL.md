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

Inline exception: a single `meta FILE` on an already-known file is small enough to run directly, as is `army TAG FILE...` (one line per save) and `navy TAG FILE...` without `--fleets` (three lines per save), and `plans.py TAG FILE...` in its default census mode (about six lines per country per save — but `plans.py ALL` and `--armies`/`--fronts`/`--where` over many saves belong in a subagent; `--where` is one row per state, so cap it with `--limit`), and `control SCOPE FILE...` without `--provinces` (about ten lines per save; `--provinces` is one row per province and belongs in a subagent), `relations FILE --tag TAG` (about fifteen lines per save; the no-`--tag` faction table is twelve), and `rail.py` on a handful of hops. Everything else — `campaigns`, `sections`, `section`, `var`, `ideas`, `flags`, `tlm`, `resources`, `buildings`, `decisions`, `pc` — runs inside a subagent. (`pc --match no_such_thing` suppresses the project table and leaves only the ~10-line summary per save, which is the shape to ask a subagent for when the question is about factory share or queue depth rather than individual projects.)

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
| `relations FILE... [--tag TAG]` | **Factions, subjects and wars read from BOTH sides.** No `--tag`: the top-level faction table (name, ideology, leader, members) plus a per-kind relation census. With `--tag`: that country's wars (each labelled with *whose* block records it), subjects, overlord, lend-lease direction, guarantees, NAPs, access. ~1.8 s/save. |
| `control SCOPE FILE... [--provinces] [--buildings] [--limit N]` | **Who really holds the ground.** `SCOPE` is a state-id list (`458,1061,459,460`) or `owner:TAG` (every state that TAG owns). Applies **both** omitted-field defaults — province `controller=` → state `controller=` → state `owner=` — and prints the states whose province split *contradicts* their state-controller label, which is the reading that lies. `--buildings` sums the province-scoped buildings by holder (`naval_base`, `rail_way`, `supply_node`, `naval_supply_hub`, bunkers — none of these are in a state block at all). Only reads the save's first ~124k lines, so it is fast enough to run over many saves. |

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

Fourth companion: `plans.py TAG[,TAG…]|ALL <save>… [--armies] [--fronts] [--divisions] [--where] [--limit N]` —
**AI battle plans: who holds an order, of what kind, and where every division sits.** Default is a
per-save census (divisions per order class: `front` / `invasion` / `buffer` / `areadef` / `NO_ORDER`);
`--fronts` lists every type-1/2 order with its `instance_id`, `creation_date` and `path` resolved to
state names; `--divisions` gives org / strength / recent-combat share per class; `--armies` maps each
army to the order it is covered by; **`--where` buckets divisions per STATE and splits each state by
order class** — the "is this front actually manned" view, and the one every agent used to rebuild by
hand (it needs a province→state join the save does not carry). ~2 s for all 66 countries of a 109 MB
save. **Never hand-parse `orders_group` for this** — see the two traps in the gotcha below, which this
script exists to close. Consumers: any "is the AI planning / where are its divisions / is this front
manned" question.

`--where` keeps two buckets apart that are routinely conflated: **`NO_ORDER`** is a division in an
army whose army *and army group* hold no order, while **`UNATTACHED`** is a division deployed in
`units` but in no army's member list at all, so no order could reach it however the plans are read.
Both are real — at `7c7803a8` 1943.11, JAP has 4 unattached divisions and USA 2, while ENG, GER, ITA
and SOV have none. **The closure test: `--where`'s total must equal `army`'s `deployed` count** (all
six verified equal on that save); if it does not, the attribution is wrong whatever the rows say.

Fifth companion: `rail.py A B <save>… | rail.py --corridor P1,P2,… <save>… [--path] [--thin N]` —
**is there a railed route between two provinces, and how thin is its narrowest link.**
Widest-path (maximise the minimum rail level) over the province adjacency graph, with **per-EDGE**
rail levels from the save's top-level `rail_way={}` map — not the per-province building level, and
not the `wa_ai_pc_railway_connection_level_*` globals (WA's own cached view). Reports `BREAK`
(no railed route: build rail or reroute) apart from `THIN` (route exists, narrowest link is low:
raise *that link's* level), the two separate levers of `WA_AI_LOGISTICS_MODEL.md`, and prints its
own tightness per save. An edge is matched by the widest level **both** its provinces report, so
**a `BREAK` is sound while an `ok`/`THIN` is an upper bound** — see the gotcha below and the script
header. Consumers: any corridor / supply-reach question (Fix 95, 97, 99).

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
- **Battle plans live in `field_marshal_group={}` as well as `orders_group={}` — and `creation_date` never refreshes.** Two traps, both of which have already produced a confident, wrong diagnosis (campaign `7c7803a8`, 2026-08-17, reproduced independently by two agents and only killed by a screenshot of the running game). Use `plans.py`; do not hand-parse.
  1. Inside `theatres={ theatre={ … } }` the depth-2 children are armies (`orders_group={ id={id=N type=53} name= member= order_instance= }`) **and** army groups (`field_marshal_group={ … name="Army Group 3" order_instance={…} }`), which are *siblings*, not nested. The `orders_group={ id=N type=53 }` lines inside an army group are **single-line id references**, not definitions. An army-group order covers its child armies, so scanning only `orders_group` reports those children as orderless: it made 29 armed British divisions on the Tunisian front read as having no plan for 30 months, and reported SOV as "75–99 % orderless" when 385 of its 407 divisions were on an army-group front order.
  2. `order_instance.creation_date` is stamped once at creation and is never refreshed — a live order keeps re-pathing and rotating members under the same `instance_id` and the same date (ENG instance 1982 held `1943.1.10` from 1943.6 to 1945.6 with a different `path` in every save). "Newest plan date per country" therefore measures front *birth/death*, not planner activity, and can move **backwards** between saves when a newer front dies (GER 1943.5.27 → 1942.12.20), which alone disproves the re-planning reading.
  - Order types attested across a full 1944 save (567 `order_instance` blocks, all countries): only `1` front line, `2` front advance, `3` naval invasion, `5` area defence. On type 5, `area_defense_settings=102` is a scripted `put_unit_buffers` garrison and `100` an engine-generated one — verified by matching the 102 state sets against the `states = { }` lists in `common/ai_strategy/WA_AI_MILITARY_COUNTRY_*_THEATRE.txt`.
  - **The two readings that were both reported as fact are now settled, arithmetically.** ENG at `7c7803a8` 1943.11: `plans.py ENG` gives front **31** divisions *"(19 via army group)"*, invasion 24, buffer 39, areadef 16, `NO_ORDER` **absent** — and 31+24+39+16 = **110**, byte-equal to `army ENG` `deployed=110`, `num_armies_for_training=110.0` and `wa_tlm_comp_div_total=110`. The rejected pass reported front 12 and 19 orderless; 31 − 19 = **12** and the "19 orderless" set *is* the army-group-inherited set, so the two disagreements are one error counted twice: scanning `orders_group` only. **31 and 0 are correct; 12 and 19 are the artifact.** The closure test is the one to reuse — if the per-class division counts do not sum to `army`'s deployed count, the attribution is wrong, whatever the individual numbers look like.
- **`resource@X` in script reads `to_use[0] + to_use[2]` — net available MINUS unmet demand.** Neither `produced` nor `net` alone. The `resources` command prints it as the **EFFECTIVE** column. ENG aluminium at 1942.6 is net `807.3`, deficit `−799.0`, **effective `+8.3`** — which is why its `> 50` latch stayed shut while the net column looked like 16× headroom. Measured 2026-08-13 on campaign `02bd4445` against the `WA_AI_EQUIPMENT_*` latches: **36 discriminating (country, date, resource, bar) cells all side with net+deficit and zero with net**, with pass/fail bracketing the bars to within one unit. *The superseded "net alone" rule was drawn from ENG **bauxite** in the same save, whose deficit happens to be −1.0 so both readings coincide there — one resource where the two agree is not evidence for the general rule.* The `produced`-alone mistake is still a mistake (it nearly produced a false FAIL on R25); this correction makes the *right* column two columns over.
- **`decision_status` mixes two entry kinds whose numbers mean different things.** `active_timed_decision={ decision= days= state= }` exists **only while live**: with `state=active`, `days` is time *remaining* (≤ the decision's `days_mission_timeout`); with `state=failed` or `re_enable_cooldown` the same field is a **re-arm cooldown on a different clock** — verified unrelated to the timeout (`economy_fatigue_export_focus_mission` has `days_mission_timeout = 70` and shows `days=13` when failed; `iron_shortage_ai` has timeout 9 and shows 12). `random_item={ decision= count= target= }` is not a state and not days at all — `count` is a **monotone cumulative fire counter**, and it is the field to read for "how many times did this decision fire". Conflating the two has already happened twice in one session; use the `decisions` command, which labels them apart.
- **A ship's `history` contains other ships.** `ship={}` blocks carry `sunk_ship={ … definition=<the VICTIM's hull> … }` kill records nested three levels down, so counting every `definition=` inside a ship reads each successful sub-hunting destroyer as a submarine. It produced a confident, wrong "ENG has 204 cruiser_submarines and its escort task forces are half full of submarines" (2026-08-13) — the escort task forces are in fact pure screens. Count `definition=` at ship depth **1** only; `navy` does, ad-hoc parses must.
- **Task forces are not the unit of naval AI — fleets are.** A mission is attached to the task force but granted at the fleet level: a fleet with no `strategic_region={}` has every task force idle, without exception in a 10-year campaign. Read fleets before concluding anything about naval behaviour (`navy --fleets`).
- **Control has TWO omitted-field defaults and one label that lies. Use `control`; never hand-walk it.**
  1. A state block omits `controller=` when the controller is the owner. Reading it literally makes a country look like it controls only its conquests (ENG 1946.4: 3 "controlled" states instead of 75).
  2. The top-level **`provinces={}`** block (which precedes `states={}`) carries a per-province `controller=` that overrides the state's, and it is omitted the same way when it matches the state controller. So the chain is province `controller=` → state `controller=` → state `owner=`.
  3. **A state's controller is a single-owner label that can be a minority holder.** It is not a summary of its provinces and it does not flip on a majority. Measured on `7c7803a8` 1943.11: state 224 (SOV-owned) reads `controller=SOV` while **Germany holds 12 of its 17 provinces**, and 14 SOV-owned states disagree with their own label on that one front; Tunisia (458) reads GER while **France holds 8 of its 14 provinces**. In a contested theatre the province split is the ground truth and the state label is noise — `control` prints the disagreements as its payload.
  - Caveat the command reports rather than hides: the province→state join comes from the generated `WA_AI_MAP_state_provinces.txt` (the save never lists a state's provinces), it covers **land provinces only** (11 203), and **impassable/wasteland states are absent from it entirely** (state 273 has zero provinces there). A scope state with no provinces is listed, not silently treated as uncontested.
- **Production lines live in sibling blocks — name `military_lines`, `naval_lines` and `air_lines` explicitly.** Scoping a production scan to `military_lines` alone silently returns **zero** submarine lines (a whole campaign reads as "the AI never built subs"); scoping to none of them pulls `equipment_variant_index` out of design and licence blocks and inflates tank counts several-fold. Name all three explicitly. Related, and already burned twice: resolve every `equipment_variant_index` through the top-level `equipments={}` registry and select on **`archetype`**, never on the variant name — this mod has no generic `infantry_equipment_N` stock for its majors (GER rifles are all `ger_inf_*`), so a name-prefix filter undercounts GER by ~70× while looking plausible on recipients whose stock happens to carry the vanilla name.
  - **Correction (2026-08-14, `f9321934`): aircraft lines are in `military_lines`, not `air_lines`.** The earlier wording here said `military_lines`-only scoping also loses aircraft; it does not. Measured on `1944.6_Jun.hoi4`: SOV 19 `military_lines` + 3 `naval_lines`, USA 35 + 34, GER 24 + 12, ENG 23 + 19, and **no `air_lines` block on any of them** — while SOV's `SOV_la_7_airframe` and `SOV_il_10_airframe` lines sit inside `military_lines`. The operational rule is unchanged (name all three; `air_lines` costs nothing and may exist elsewhere), but do **not** infer from its absence that a country built no aircraft, and never scope an aircraft scan to `air_lines` alone.
- **`var`'s regex is matched against the whole `name=value` string, not the name alone.** A `$`-anchored pattern (`"^wa_ai_foo$"`) therefore matches nothing and returns the same "no variable matching" as a genuinely absent variable. Anchor with a trailing `=` instead (`"^wa_ai_foo="`), or with `\^` for arrays.
- **The top-level `equipments={}` registry has no `archetype` field, and `obsolete` is write-only-`yes`.** An entry's *block key is the equipment definition name*; resolve archetype and the def-level `parent =` out of `common/units/equipment/*.txt`, never out of the save. `obsolete=no` never occurs — **absence is the non-obsolete state**. The entry's own `parent_id={}` is a *design-variant* lineage pointer (id→id) and is unrelated to the def-level `parent =`. Only entries carrying `name=` are designed variants (164 of 7 190 in the `02bd4445` final save); the rest are per-country type registrations. Registry presence means "this country has the type", which is a **weaker** claim than "researched it" — ENG holds non-obsolete `usa_hv_inf_3..6` it never researched.
- **`obsolete=yes` does not gate anything the AI does.** It is not an archetype-uniqueness marker (288 (creator, archetype) groups in the `02bd4445` final save hold two or more non-obsolete members, one of them five members of a single linear chain) and it does **not** stop production: 7.0% of all production lines and **9.6% of all assigned factories** in that save run obsolete-flagged equipment, including USA's 68-factory `tank_usa_medium_chassis_3` line and its 75-factory `usa_mechanized_equipment_4` line. The share *rises* through the campaign. Never conclude "the AI cannot build X" from an obsolete flag — check the lines.
- **`production_upgrade_desire_offset` is not serialized into a country's `ai` section.** Verified with three ungated controls (including the long-standing `SOV_dont_build_shit_guns`), all equally invisible. So a save can never answer "did *this* strategy arm" — probe its *effect* on the production lines instead. The `ai`-section reading that works for R34's `invade` suppressions does not generalise to this type.
  - **Correction (2026-08-17, `7c7803a8` 1943.11): two supporting claims here were wrong.** This entry previously said "only ~10 numeric strategy type codes ever appear" and "**no `ai_strategy` entry carries a negative value at all**". Measured: **24 distinct (kind, type) codes** (14 `ai_strategy` + 10 `persistent_strategy`), and negatives do occur — 16 entries at ≤ −500, e.g. `ai_strategy={ type=6 id=38 value=-2000 }`. Code counts are build- and campaign-dependent, so treat any census as a per-save measurement, never a fixed list. The narrow claim about `production_upgrade_desire_offset` is unaffected.
- **The `ai` section's `type=` codes are NUMBERS WITH NO NAME MAP, and guessing one is a trap that has now caught two passes.** WA declares **95** distinct `type =` names across `common/ai_strategy/`; a save exposes ~24 codes. Nothing in the save or the repo maps code → name, so a census tells you "type 6 armed at −2000 for DEN" — which answers no verification question. **Worked example of the trap (2026-08-17):** `ai_strategy type=6` is region-id-keyed and carries negatives, and `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt` writes `strategic_air_importance` at −20000/−40000 on those ids, so type=6 was identified as `strategic_air_importance` and — since **no value anywhere in the save is below −2000 while positives reach 28 750** — the engine was said to floor negatives at −2000, which would make the whole Allied bombing ladder's −500k/−40k/−20k tiering a no-op. **Every link after the first was false.** DEN, which holds 14 of those entries, is in **no faction and at war with nobody** (`relations --tag DEN`), so an Allies-gated file cannot be its source; no WA file writes air importance for DEN's region set (63, 67, 80–83, 290–295); and type=6 splits **403 sea / 478 land** entries, so it cannot be pinned to an air, naval or area type at all. The −2000 floor has a mundane explanation still standing — the large-negative rules simply never armed in this save. **Only probe a type code you have pinned by independent means** (as R34's `invade` and the `front_armor_score` reconcile were), and never infer a type's identity from the shape of its ids and values.
- **`date="1.1.1.1"` in `technology/technologies` marks a tech being researched RIGHT NOW, not a duplicate or a start-grant.** It carries accumulated `research_points`, no `level=`, and a twin entry under the sibling `technology/slots` block holding the slot's `points_factor`. A name-grep across the whole `technology` section therefore reports a false duplicate for every in-progress tech (ENG 6, GER 6, USA 3 in the `02bd4445` final save; exact 1:1 match with `slots` in all three). Scope to `technologies={}` and select on the presence of `level=`. Start-granted techs carry a real date (`1936.1.1.12`).
- **An annihilated tag keeps its country block, and every variable in it reads as a live value.** The block is never removed — only territory, army and the AI systems that write to it stop. On campaign `be18f9c7`, GER holds **0 owned / 0 controlled states and no `units` section from 1945.7 onward**, yet its 1946.7 block still reports a 4-project PC queue with `wa_ai_pc_assigned_factories_total = 14`, `wa_ai_fielded_eq_ratio` byte-identical at `0.93313` across 13 consecutive saves, and a `ruling_party` that flipped to communism. Everything freezes at the same boundary, so **any probe reading "the last save" for a dead tag is really reading its last live save** — here 1945.6, twelve months earlier. **Prove the tag is alive before trusting a late-campaign variable:** owned states > 0, or a `units` section present, or (on an instrumented build, cheapest) the family's `*_last_t` stamp equal to the live tags' — GER pins at `wa_tlm_comp_last_t = wa_tlm_nav_last_t = 113` while live tags read 126. Two other tells: byte-identical values across consecutive saves, and an aggregate contradicting its own array (that `= 14` total sits over `wa_ai_pc_assigned_factories^0..^3` all reading **0**). When a dead tag is the subject of the probe, run it on its last live save and say so in the evidence line. Distinct from the frozen-sector case in checklist R39/R42, which is a *live* tag the weekly on_action skips.
- **A global flag's set-date is a first-occurrence timestamp only if its `set_global_flag` is guarded.** Re-setting an already-set flag refreshes its date, so an unguarded write records the **latest** occurrence under a name that usually says "first". `first_nuke_dropped` is the live example: set unguarded in `common/on_actions/00_on_actions.txt` `on_nuke_drop` (vanilla-inherited), it reads **1946.5.18.24** on `be18f9c7` — the instant of `JAP_nuke_2` — while the first bomb fell **1945.12.5.23** per the guarded `JAP_nuke_1`, a 164-day error. Read the write site before dating any event from a flag, and anchor timelines on flags that are written once by construction. Same rule for `set_country_flag`.
- **Absence of a country variable does not prove a build lacks the fix that writes it — check the write site's scope first.** `WA_AI_PC_state_type_projects` (Fix 46) is written inside `var:WA_AI_PC_target_state^_project_id = { … }`, i.e. **state scope**, so `var ENG` reports it absent on a build that has it. One build-fingerprint pass concluded a whole commit was OUT on that basis and mis-scored the campaign's headline item until a country-scope fingerprint (`wa_ai_pc_type_id` carrying the new tag values) settled it. Prefer fingerprints you have confirmed are written in the scope you are probing.
- **In the PC queue, an absent per-project variable is not a zero — and three of the families are routinely absent.** `WA_AI_PC_start_project` never initialises `assigned_factories`, `stall_weeks` or `build_time`, and `WA_AI_PC_end_project_by_id` clears them, so a project that has never been funded, or has never yet been through a weekly stall sweep, simply has no entry. Script cannot tell the two apart (`check_variable` reads absent as 0) and neither can a naive parse — which is how "GER 1944.6 has 80 type-13 slots all at exactly 0" was reported for a queue where **none of the 80 carried a stall counter at all**. The `pc` command prints absent as `-` and zero as `0`. On the same save the right reading is "80 railway projects appended since the last assignment pass", which `pc` also states outright.
- **The queue array is sorted only *as of* the last assignment pass.** `WA_AI_PC_assign_factories` rebuilds `wa_ai_pc_queue` in descending priority order, but the strategies run from a 2-day background event and **append**, so a save taken mid-week shows a sorted prefix plus an unsorted tail. Reading queue position as priority rank across that boundary turns "queued three days ago" into "starved": on `be18f9c7` 1944.6, GER's two funded projects are priority-100 while 80 unfunded priority-1100 railways sit behind them, and nothing is wrong. `pc` reports the tail length explicitly.
- **Air-base capacity is booked per wing at the wing type's fixed size, not per plane present.** A save carries only `count=` on a wing (= Σ `equipment.amount`, 1 117/1 117 wings on `af003548` 1944.7); the nominal size is `land_air_wing_size` of the wing's `definition=` in `common/units/air.txt`. "Capacity − planes present" therefore over-reads free room by the wings' fill gap and once produced a confident "the UK held 3 800–5 700 spare slots and the USAAF still would not move" — the same states were at exactly 100.0 % nominal. Use `airload.py`, never a plane count, for any room-on-the-airfield question; the builders' `wa_ai_uk_air_dbg_planes` / `_capacity` gauges are plane counts too and read ~10 % under the true load.
- **The `buildings` header's `states owned=N controlled=M` is not a liberation reading.** "Controlled" counts every state the country controls, owned or not (colonies, Maghreb, states held for someone else), so owned = controlled proves nothing about the homeland: on `a232d96c` FRA read **58/58 at 1946.6 while GER held 20 of the 24 metropolitan French states**. To answer "is France liberated", run `control owner:FRA <save>` (or pass the metropolitan ids) — it counts per holder at both state and province level. The hand-walk that first produced the right answer (GER 20 / FRA 2 / RBE 1 / ITA 1) is what that command now is; do not rebuild it.
- **`wa_tlm_nav_convoys`, `num_equipment@convoy` and `has_equipment = { convoy … }` read the FREE convoy pool — and a free pool of 0 IS a shortage; do not "correct" it with the fleet size.** The fleet is `convoys={ equipment={ … creator= } }` at depth 1 of the country block (sum the entries; `creator=` separates own-built hulls from exile / lend-lease ones), but the fleet count says nothing without the NEED, which is **not serialised**: on `a232d96c` ENG read free 0 for 46 months with a fleet of 627–842, and the in-game tooltip at 1944.6.1 showed 676 held / 676 used, trade **49 of 387** needed, supply 577 — a real famine that a first pass had dismissed as "the fleet never dropped below 600" (retracted the same day; the free pool is the only save-side proxy for Use/Need). `convoys_destroyed=` at country depth 1 is kills **by** that country (= `wa_tlm_nav_conv_killed`), not its losses.
- **Expeditionary forces live in FOUR places, none of them `active_relations` — and the obvious arithmetic test can never detect one.** Measured on `7c7803a8` (2026-08-17), all three saves, all ~70 countries. A lent division is **inserted into the COMMANDER's own `units` section** carrying `expeditionary_owner="<OWNER>"`; the owner keeps `expeditionaries_sent={ { id=N type=T } … }` at **country depth 1**, a sibling of `units` (entry count matches the `expeditionary_owner` count exactly in every pair; two id types, 51 and 4713, both denote a lent division). The engine's own decision is serialised at `<OWNER>/ai/expeditionary_force_data={ tag= casualties= do_not_send_forces= pull_forces_back= }` — **it names both `05_defines.lua` sender latches, so a save answers "did the engine refuse to send" directly**, and the block only exists once the engine has formed an intent toward a specific `tag`, so its ABSENCE means no target was ever selected rather than a target refused. `diplomacy/proposed_diplo_action={ action=send_expeditionary_force index= date= }` is an offer stamp / retry cooldown only.
  - **`active_relations` carries nothing expeditionary** — unlike lend-lease. A whole-file scan for `/expedition/i` under it returns zero. Looking there is a dead end.
  - **"Divisions owned minus divisions commanded" is structurally always 0** and cannot detect lending: the lent division moves into the commander's `units`, so the theatre `member=` list and the `units` count move together. Verified 0 for every country on every save. Only `expeditionary_owner` / `expeditionaries_sent` see it.
  - **`army_manpower_value={ value={ tag= value= } }` is NOT a loan of troops** — it names the tag *contributing manpower* to a division its holder owns. ENG's 1943.11 divisions carry POL 69 500 and FRA 93 000 from the exile-manpower path. Reading it as an expeditionary force inverts who commands what.
  - `expeditionary_force_data` survives on an annihilated tag with no `units` section (SIC holds one naming CHI on all three saves), so its presence alone proves nothing — cross-check `expeditionary_owner` in the named receiver.
- **Lend-lease ledgers are written from the GIVER's side and carry no payload; read direction off `first=`, not off the stockpile.** `active_relations/<B>/lend_lease={ first= second= start_date= }` sits in the **giver's** block with `first=` the giver (three fields — no equipment, amounts or fuel are ever serialised); `lend_lease_to_allies_history.ic_given` in A's block toward B is what **A gave B** (byte-equal to B's `ic_received` toward A); `recently_leased_ic` sits on the **receiver's** side; `diplomacy/proposed_diplo_action { action=lend_lease index= date= }` (country depth 2, `index` = 1-based position in the save's `countries={}` order) is the giver's *offer* stamp — a per-proposal retry cooldown that escalates 4/5/6/7 months and is written on accepted offers too. Two agents in one session (2026-08-16, `a232d96c`) inferred the mirrored convention from a single pair and inverted USA↔SOV; three control pairs (SOV→FRA, USA→CHI, ENG→SOV) settled it — the flow is **SOV → USA 101 697 IC**, and USA divisions hold 1 518 Soviet medium tanks to prove it. Do not size a lend-lease from `creator=` holdings either: the WA relief `send_equipment` legs move rifles without touching the ledger (SOV held 64k `usa_inf_3` in 1942 against 5.5k ledger IC), and `foreign_lease_equipments` is a type catalogue (captures included) with no amounts.

- **Air-wing mission state (verified `a232d96c` 1944.6/1944.9, all tags): the idle test is `mission={ type=0 }` / absent `strategic_region=` — never `active=` and never `mission={}` presence.** Every wing carries `mission={}` and `active=yes` on 1132/1132 wings, missions or not. Keys at `mission` depth 5: `type=` (bitmask: 1 air_superiority, 2 cas, 8 strategic_bomber, 16 naval_bomber, 512 attack_logistics, 1024 air_supply, 16384 recon; 0 = none), `strategic_region=` (assigned), `executing_mission=` (actually flying — `cvair.py --miss` keys "NO-MISSION" on its absence). At wing depth 4: `transferring_to=<STATE id>` (a state, not an air-base id — values 830–860 exceed the base-id space), `transfer_progress=` (accumulator, not %), `transfer_cancelled=yes|no`, `region_to_assign=`. Also: the depth-1 `air_base={}` block's `level=` is NOT the airfield level (Virginia reads `level=1` at capacity 800) — read `capacity=` (= state `air_base` × 100).
- **`naval_base` is not in the state blocks of these saves** — every state's `naval_base` sums to 0 in `1944.6_Jun` (`a232d96c`); naval bases are province-scoped in the top-level `provinces={}` block, along with `rail_way`, `supply_node`, `naval_supply_hub`, `bunker` and `coastal_bunker`. `buildings … --match naval_base` therefore reads a silent 0 for every country — it only ever sees the state block. Use `control <scope> --buildings`, which sums them by the province's real holder (Maghreb at `7c7803a8` 1943.11: FRA 9 naval-base levels / 40 rail, GER 13 / 10).

- **Alliances, subjects and wars have three different layouts and three separate traps. Use `relations`.** All three are quantified on `7c7803a8` 1943.11:
  1. **Faction membership is a TOP-LEVEL `faction={}` block, not anything in a country block, and the leader is `members[0]` — there is no `leader=` field.** Five depth-0 blocks, each with `id={}`, `ideology=`, `members={ "ENG" "UKO" … }`. `members[0]` gives ENG / SOV / GER / CHI / JAP, all correct. **`name=` is often absent** (only renamed factions have one) and a faction block *contains nested intelligence-agency sub-blocks that carry their own `name=`* — so a whole-body `name=` grep reads the Comintern's name as its spymaster's title (`"HSpymaster!"`). Anchor `name=` at depth 1 and fall back to `icon=`.
  2. **`puppet={}` lives in the OVERLORD's `active_relations`**, so a subject's own block never says it is a subject. ENG's block holds 8 (`AST CAN NZL RAJ SAF UKN UKO UKT`); none of those eight say so themselves.
  3. **`war_relation={}` is written on ONE side only**, and the side is arbitrary. **ENG's own block records exactly 1 war (GER). ENG is actually at war with 29 countries — 28 of them are recorded only in the *enemy's* block.** A one-country read is not slightly incomplete here, it is off by 28. Read every country and key on the `first=`/`second=` fields, which is what `relations --tag` does.
- **Rail is stored per EDGE, and "both ends have rail" is NOT a connection. Rail continuity is a widest-path question over edge levels — `rail.py`, never a direct-adjacency check and never a per-province one.** Two readings of the North Africa corridor were both wrong before this settled:
  - **Direct adjacency between corridor nodes calls 12 of 14 hops "no rail".** Pure noise: corridor nodes are **1–5 provinces apart**, so consecutive nodes almost never share an edge at all.
  - **A per-province model ("both endpoints carry rail") under-counts breaks.** The real answer over edge levels is **2 breaks at 1941.6 and 1943.11** — `11957 Gabès → 1149 Tripoli` and `1130 Derna → 5078 Libyan Plateau` — and **1 from 1944.6 on**, the Tunisia/Libya border gap that is never railed. **This vindicates the independently reported "2 genuine breaks"**; a superseded note here guessed that figure conflated BREAK with THIN, and it did not — the looser model did. *Sound lower bound on how loose: of the 7 337 edges with rail at both ends, **1 210 (16 %) share no level and are definitely not railed**. `rail.py` prints this per save.*
  - **The per-edge data is a SECOND, top-level block**, distinct from the per-province `buildings={ rail_way={ level=N } }`: `rail_way={ rail_way={ <prov>={ rail_way={ <one level per engine neighbour> } } } }`. Its province keys sit at **brace depth 2** with their own keys at **column 0** — depth-anchor it, the indentation lies here as everywhere. Confirmed per-edge by three order-free tests (`7c7803a8` 1943.11, 4 456 provinces): every level occurs an **even** number of times globally — each railed edge writes its level into both endpoints — which holds on **all four saves sampled across the campaign (1936.6, 1941.6, 1943.11, 1945.6): 20 of 20 level counts even** (1943.11 = 1:3586 2:2880 3:1900 4:816 5:654); non-zero entries per province are **2 for 3 083** (through-province), 1 for 307 (terminus), 3 for 736 (junction); and `max(levels)` equals the province building level for 4 029.
  - **The index → neighbour order is NOT decodable from this repo, so match on LEVEL instead.** `len(levels) − degree` in `WA_AI_MAP_province_connections.txt` is **always positive** (+1 for 884 provinces, +2 for 310, up to +5): the engine's neighbour set is a strict **superset** of WA's generated graph, because the generator drops connections. Ascending id, descending id and file order all score **~44 %** on the edge-symmetry test (a correct order would score ~100 %) — chance. So `rail.py` takes an edge's level as the widest level **both** provinces report: no genuinely railed edge is ever rejected (a real edge at level L puts L in both lists), which makes **`BREAK` sound**, while two provinces can share a level via other edges, which makes **`ok`/`THIN` an upper bound**.
  - **`BREAK` and `THIN` are different failure modes with different levers** (`WA_AI_LOGISTICS_MODEL.md`): no railed route at all vs a route whose narrowest link is level 1 (throughput `4 + 8*level` = 12 against 28 at level 3). Never report a THIN hop as a missing railway.
  - **The source province's own level caps the answer.** Seeding the search with an unbounded minimum reports a level-1 railhead's route as level 2 (5078→11967 read 2 until the cap was added). Endpoints count, not just the interior.
  - The adjacency data is **fully symmetric** — 59 402 directed edges, **0** asymmetric pairs (verified 2026-08-17) — so treating `WA_AI_MAP_province_connections.txt` as undirected is exact, not an approximation.
- **A landmass id is not a theatre, a continent, or a front — do not gate anything on one.** In the generated `WA_AI_MAP_landmass_data.txt`, landmass **2 is the entire Afro-Eurasian mass, 8 237 provinces**: Rome, Berlin and Tripoli all sit on it, and so does Singapore. "Same landmass" therefore means "reachable on foot in principle" and nothing about proximity, theatre, or whether an army can actually get there — it inverted a proposed design gate before it was caught. For "is this the same theatre" use the strategic-region sets in `common/ai_areas/WA_AI_MILITARY_areas.txt`; for "can this force reach that ground" use the province graph with a real path (see the railway/corridor note in `wa-lessons-learned`), never a landmass equality test.

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

Example — who actually holds Tunisia and Algeria (the Fix 99 geography), and where the ports and rail on that shore really are:

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py control 458,1061,459,460 1943.11_Nov.hoi4 --buildings
python .claude/skills/wa-savegame-analysis/scripts/savegame.py control owner:FRA 1943.11_Nov.hoi4
```

The first prints `458 GER GER  FRA 8  GER 6` — the state label says Germany, the ground says France. The second is the liberation reading for a whole country in one line.

Example — whether the WA_AI cheat ideas were still on GER by 1943:

```bash
python .claude/skills/wa-savegame-analysis/scripts/savegame.py ideas GER GER_1939_05_13_13.hoi4 GER_1943_03_02_02.hoi4 --match "WA_AI|economy_fatigue"
```
