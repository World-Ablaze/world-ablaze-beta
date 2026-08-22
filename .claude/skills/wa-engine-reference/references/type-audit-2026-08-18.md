# `ai_strategy` type audit - WA claims vs the engine's own documentation

> **Superseded in part, same day.** `common/ai_strategy/documentation.info` was refreshed to the
> install's 2024-11 edition on 2026-08-18 and registered in `tools/engine_docs_manifest.json`.
> **Every `documentation.info:NNN` line number in THIS report describes the pre-refresh 2023-07
> file** and is kept as evidence; everywhere else in the repo those citations were rewritten to
> section names. The findings themselves (contradictions, unsupported claims) are untouched and
> still open.

Date: 2026-08-18. Read-only audit. No file was changed **by the audit**.

> **Disposition, 2026-08-18.** Every claim below was re-verified against the install before acting - the
> audit was accurate on every row checked. Status per row is in the **Done** column of the summary
> table. C2/X1 closed in `a62d04860`; C1, C3, C4, C5, C8, U1-U7, X2, X3, X4 closed in the commit that
> carries this note. C6 and C7 stay open under their own QUEUE row (three types documented as live that
> do not exist). This file is kept as the evidence trail; the corrections live in the WA documents.

## Sources

| Ref | File | Size / date |
| --- | --- | --- |
| **ENGINE** | `C:\Jeux\steamapps\common\Hearts of Iron IV\common\ai_strategy\_documentation.md` | 712 lines, header "updated 2024-11" |
| **STALE** | `E:\Projets\HOI4\WA\world-ablaze-beta\common\ai_strategy\documentation.info` | 422 lines, header "updated 2023-07" |
| DEFINES | install `common/defines/00_defines.lua` | 1.19.2.0 |
| PEER | Expert AI 5.0 `C:\Jeux\steamapps\workshop\content\394360\741805475\common\` | supported_version 1.19.2.0 |
| WA-A | `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` | 372 lines |
| WA-B | `documentation/WA_AI_MILITARY_SYSTEM.md` | 456 lines |
| WA-C | `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt` header | 455 lines |

## Framing correction (measured, read first)

The task premise was that no WA document cites the engine's `ai_strategy` documentation. That is **not
quite right**, and the truth is worse than the premise.

- WA **ships its own copy** of the engine file, in a replaced folder, at
  `common/ai_strategy/documentation.info` (422 lines). It is the **2023-07** edition. The install's is
  the **2024-11** edition (712 lines). The two are not the same file (`diff`: DIFFERENT).
- WA-A cites it by name and by line number twice (`WA_AI_MILITARY_TYPES_REFERENCE.md:159`
  "documentation.info lines 228-266"; `WA_AI_MILITARY_SYSTEM.md:333` "documentation.info:250-266").
  WA-C cites the install file correctly by name ("documented in vanilla
  common/ai_strategy/_documentation.md", `WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt:18`).
- Token-list delta, measured by `comm` on the two extracted lists:

| Direction | Tokens |
| --- | --- |
| **Present only in 2024-11 (missing from WA's copy)** | `become_spymaster`, `convoy_raiding_target`, `equipment_production_min_factories_archetype`, **`force_concentration_factor`**, **`force_concentration_front_factor`**, **`force_concentration_target_weight`**, `naval_dominance`, `naval_invasion_dominance_weight`, `raid_target_country`, `research_weight_factor` |
| **Present only in 2023-07 (renamed away)** | `naval_invasion_supremacy_weight` -> now `naval_invasion_dominance_weight` |

**The entire AIFC foundation is absent from the copy the repo reads.** That single fact explains most of
the contradictions below: the AIFC system was reverse-engineered against a document that does not contain
the three types it is built on, while a per-parameter spec for all three sat in the install.

`common/ai_strategy` is a `replace_path` folder, so `documentation.info` is a WA-owned artifact, not a
live vanilla file. Nothing loads it; it is a comment file. Replacing it is a documentation decision, not
a behaviour one.

---

## Summary table

| # | Type | Class | WA says | Engine says | Where | Done |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | `force_concentration_front_factor` / `_target_weight` | **CONTRADICTION** | only `front_control` / `front_unit_request` / `invasion_unit_request` take generic targeting; the FC types "additionally take `state_trigger`" | both FC types take the full set `tag` / `state` / `strategic_region` / `area` / `country_trigger` / `state_trigger` (+ `ratio` on `_front_factor`) | WA-A:159 vs ENGINE:238-244, 265-270 | **FIXED** - TYPES_REFERENCE targeting sentence rewritten, with the AIFC consequence |
| C2 | `front_control` | **RESOLVED 2026-08-18** | "Per area, last-set wins per mode"; Phase 5 will add scripted mutual-exclusion triggers | `priority = 0  # Default 0, higher prio strats will override lower` | WA-B:90, WA-B:156-166 vs ENGINE:292 - **closed:** "last-set wins" removed, `priority` documented with the live ladder in `WA_AI_MILITARY_SYSTEM.md` §6.1 | **FIXED** `a62d04860` - SYSTEM.md §6 |
| C3 | `naval_dominance` | **CONTRADICTION** | "Sums per region/area", range 0-100, "values in use are 70-80 (18 entries)" | "value = 99 # Percentage between 0 and 100"; a set value, no additive statement | WA-B:106,130 vs ENGINE:672-682; 8 live entries at `value = 1000` in `WA_AI_NAVAL_COUNTRY_ENG.txt:897-918` | **FIXED** - §4 row + note; the 1000s were already retired |
| C4 | `put_unit_buffers` | **CONTRADICTION** | "Sums per state / Additive per state / range 0 to 100" | `ratio` = share of the country's total armies (0..1); "ratio of same orders ids will be share same ratio" | WA-B:110 vs ENGINE:352-357 | **FIXED** - §4 row, new order_id note, Fix 96 arithmetic corrected |
| C5 | `theatre_distribution_demand_increase` | **CONTRADICTION** | range "0 to +500" | "value = 10 # Increase desired unit demand by 10" - absolute unit count | WA-B:81 vs ENGINE:386-388 | **FIXED** - §4 row: absolute divisions, 4-10 in use |
| C6 | `naval_invasion_support_priority` | **AUDIT WAS WRONG - the type is real** | a live NAVAL type with combination rule and range 0..+100 | token does not exist in either doc edition | WA-A:28, WA-B:109 vs ENGINE token list :53-61 | **CORRECTED 2026-08-18** - absent from both doc editions, but present in `hoi4.exe` and used 7x by vanilla `ENG.txt`. "Invented type" withdrawn; row rewritten as a real, undocumented, unused lever |
| C7 | `force_ratio`, `infantry` | **CONTRADICTION** | FRONT-domain `ai_strategy` types with domains, ranges and counts | neither token exists in either edition | WA-A:17-18, WA-B:47,88 | **FIXED 2026-08-18** - both removed from the domain table, the policy table and 35 `# Phase 6 split:` headers |
| C8 | `garrison` | **CONTRADICTION** | `value = -5000` is "the documented way to force garrison off" | `garrison` has **no section at all** - bare token-list entry | WA-B:87,131 / WA-A:147 vs ENGINE:45 | **FIXED** - §4 row + note: convention, not engine text |
| U1 | `area_priority` | UNSUPPORTED | "Sums per area", range -200..+200 | token listed, **no section** in either edition | WA-B:80 | **FIXED** - tagged **I** in §4 |
| U2 | every "Sums per X" row in the §4 policy table | UNSUPPORTED | 25 types given an explicit engine combination rule | the file states additivity for exactly **one** pair (`avoid_starting_wars` + `conquer`) | WA-B:79-113 vs ENGINE:197-210 | **FIXED** - column renamed and every cell tagged E / I |
| U3 | `dont_defend_ally_borders` | UNSUPPORTED | "Exclusive per ally (highest value wins)" | binary (">0 activates, <=0 deactivates"); **silent** on multi-writer resolution | WA-A:278, WA-B:97 vs ENGINE:222-229 | **FIXED** - §4 row + the de-dup argument now carries the caveat |
| U4 | `spare_unit_factor`, `garrison_reinforcement_priority`, `naval_mission_threshold`, `strike_force_home_base`, `naval_convoy_raid_region`, `naval_avoid_region` | UNSUPPORTED | ranges + combination rules | token-list only, no section | WA-B:89,96,104,105,107 | **FIXED** - all five tagged **I** |
| U5 | `support` | UNSUPPORTED (**correctly labelled**) | "Unverified - assumed to sum, never measured" | token listed, no section | WA-B:103,132 - honest | **CHECKED, no change needed** - already honest |
| U6 | `support` "engine description" quote | UNSUPPORTED | quotes "*Pursues AI to support a certain country within wars, sending lend lease, volunteers, or expeditionary forces*" and attributes it to `documentation.info` | that string does not occur anywhere in the install (grep -r, 0 hits) nor in `documentation.info` | WA-A:97 | **FIXED** - quote relabelled ASSUMED, provenance unknown |
| U7 | `front_unit_request` base of 100 | UNSUPPORTED | "Additive over a base of 100, so -200 already floors the request at zero" | "will be added as a factor over regular requests" - no base stated | WA-B:338 vs ENGINE:331 | **FIXED** - §4 row + the -200 rationale now says ASSUMED |
| X1 | `front_control priority` | **RESOLVED 2026-08-18 - the premise was wrong twice** | Phase 5 will build scripted `*_owns_*` mutual-exclusion triggers to enforce Country > Faction > Default | the engine has a native integer precedence field | WA-B:156-166 vs ENGINE:292 - **closed:** the capability is NOT unused (56 of 215 blocks set `priority`), and Phase 5 is NOT a plan (shipped `d149a204b`, 50 slugs, 43 of them for types with no `priority` field). §6 | **FIXED** `a62d04860` - premise was wrong twice, see §6 |
| X2 | `force_concentration_* country_trigger` / `tag` / `strategic_region` | **UNUSED CAPABILITY** | AIFC Layer 4 targets only via `state_trigger` + encoded `*_ref` arrays (Fix 31), a workaround whose `-10737.4` unresolved-token risk is still open | `country_trigger` and `tag` are documented on both FC types | WA-C:395-433, WA-B:426-428 vs ENGINE:265-270 | **FIXED** - documented at both the AIFC risk note and TYPES_REFERENCE |
| X3 | `put_unit_buffers order_id` semantics | UNUSED CAPABILITY | order_id used in 154 places for pool separation, but no WA doc states what it does | "ratio of same orders ids will be share same ratio" | WA-B:110 (silent) vs ENGINE:354-355 | **FIXED** - new `order_id` note in §4 |
| X4 | `avoid_starting_wars` | UNUSED CAPABILITY | 1 use mod-wide, undocumented in WA | the only documented additive pair in the file, designed to work with `conquer` | ENGINE:197-210 | **FIXED** - new `avoid_starting_wars` note in §4 |

Counts: **8 CONTRADICTION**, **7 UNSUPPORTED**, **4 UNUSED CAPABILITY**, **12 CONFIRMED** (list below).

---

## C1 - the `force_concentration_*` targeting fields

**WA-A:159** (`WA_AI_MILITARY_TYPES_REFERENCE.md`):

> Only `front_control`, `front_unit_request` and `invasion_unit_request` take the generic country/state
> targeting fields (see `common/ai_strategy/documentation.info` lines 228-266); the `force_concentration_*`
> types additionally take `state_trigger`.

**ENGINE:265-270** (`force_concentration_target_weight`) - identical block at **238-244** for
`force_concentration_front_factor`:

```
	tag = GER							# Target a specific country. Can specify multiple.
	state = 42							# Target a state. Can specify multiple.
	strategic_region = 65				# Target a strategic region. Can specify multiple.
	area = europe						# Target a specific ai area. Can specify multiple.
	country_trigger = { always = no }	# Trigger to check against a specific country...
	state_trigger = { always = no }		# Trigger to check against a state...
```

`force_concentration_front_factor` additionally documents `ratio = 0.0` (ENGINE:244);
`force_concentration_target_weight` does not.

WA-C, the AIFC header, states this **correctly** (`WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt:30`: "Both
targeted types accept tag / state / strategic_region / area / country_trigger / state_trigger"). So the
two WA documents disagree with each other and WA-A is the wrong one. Root cause: WA-A's line-number
citation points into the **2023-07** copy, which has no force_concentration section to read.

---

## C2 - `front_control` precedence

**WA-B:90** (policy table):

| `front_control` | Per area, last-set wins per mode | **Exclusive per area** | Country > Faction > Default |

and **WA-B:156-166** builds an entire deferred subsystem on that belief: "For Exclusive-policy types,
pairs of scripted triggers will guard layers so that the Country layer takes precedence over Faction".

**ENGINE:292**:

```
	priority = 0						# Default 0, higher prio strats will override lower.
```

The engine resolves overlapping `front_control` writers by an explicit integer, not by file order.
Measured in-repo: WA already writes `priority` in 57 `front_control` blocks
(40x `priority = 100`, 5x `320`, 4x `300`, 2x `340`, 1x each `330` / `500` / `10000`, plus two
malformed-looking `priority=2` / `priority=5`). The **code** uses the mechanism; the **spec** does not
know it exists and proposes to reimplement it in script. Note also `priority = 10000` - with no documented
ceiling, that entry silently outranks every other writer mod-wide.

---

## C3 - `naval_dominance` is a percentage, and 8 live entries are 10x over the ceiling

**WA-B:106 / 130**:

| `naval_dominance` | Sums per region/area | Additive | 0 to 100 |

> `naval_dominance` values in use are 70-80 (18 entries), well inside the documented 0-100. Sums may
> still exceed 100 when layers stack; that is legal but should be called out at the site.

**ENGINE:672-682**:

```
### `naval_dominance`
Used to set the naval dominance for an AI area
	id = winter_war_front # AI area key   OR   id = 271 # region id
	value = 99 # Percentage between 0 and 100
```

"Used to **set**" - the engine documents no additive behaviour, and bounds the value. The claim that
sums over 100 are "legal" has no support.

Measured: `WA_AI_NAVAL_COUNTRY_ENG.txt:897-918` contains **8 entries at `value = 1000`** (regions 43,
44, 243, 247 and four more), against 18 entries at 70/80 elsewhere. WA-B:130's inventory missed them.
Whether the engine clamps or misbehaves at 1000 is not documented - **silent**.

---

## C4 - `put_unit_buffers` ratio and order_id

**WA-B:110**:

| `put_unit_buffers` | Sums per state | Additive per state | 0 to 100 |

**ENGINE:346-378**:

```
	# ratio of total armeis in country to be buffered
	ratio = 0.4
	# you can specify an order id. ratio of same orders ids will be share same ratio
	order_id = 2
	# states to put garrison orders (if no state is friendly, strat is invalid)
	states = { 125 126 ... }
	# ai areas that the orders will use these buffers in
	area = europe
```

Three separate corrections:

1. `ratio` is a **fraction of the country's whole army**, in 0..1, not a per-state 0..100 score. WA's
   code is right (measured: every WA `ratio` is 0 .. 0.25); WA-B's documented range is wrong by 400x and
   invites a value that would order the entire army into a buffer.
2. Same-`order_id` blocks **share** one ratio; they do not sum. The engine is silent on blocks with
   *different* order_ids.
3. The mechanism is per **order**, not per state - `states` chooses where the garrison order sits,
   `area` chooses which orders may draw on the pool.

Consequence for a live claim: **WA-B:383** (Fix 96) states "Ratios per state group, **summed**: owner
0.10 + 0.20 (Sicily/south), 0.15 + 0.10 (mainland anchors), plus the ally's 0.06 or 0.12". Measured, the
two Axis ally-guard blocks both carry `order_id = 9606`
(`WA_AI_MILITARY_FACTION_AXIS_THEATRE.txt:146` and `:197`) - per ENGINE:354-355 those two **share** a
ratio rather than summing it. They are mutually-exclusive tiers by gate, so the practical effect is
nil today, but the arithmetic in the doc is not the engine's arithmetic.

WA's use of a distinct `order_id` to keep a pool separate (9606, 9608) is correct engine practice and
should be kept.

---

## C5 - `theatre_distribution_demand_increase` scale

**WA-B:81**: range "0 to +500".

**ENGINE:386-388**:

```
	id = 447  # State ID for Alexandria, so will target the theatre where Alexandria belongs
	value = 10  # Increase desired unit demand by 10
```

The value is an **absolute count of divisions** added to a theatre's demand, not a percentage. WA's live
values are 4, 4, 6, 6, 10, 10 (measured across CAN/ENG/JAP/SOV/USA/ALLIES `_THEATRE.txt`) - i.e. the
code is calibrated correctly and the documented ceiling is ~50x the largest value ever used. A future
author trusting "0 to +500" would order 500 extra divisions into one theatre.

The `id =` semantics (a **state** id, resolving to the theatre containing it) is CONFIRMED - all six WA
ids are state ids.

---

## C6 - `naval_invasion_support_priority` DOES exist - this row's verdict was wrong

> **Corrected 2026-08-18.** The conclusion below ("It is an invented type") was drawn from the
> documentation alone. Two measurements overturn it: the literal string
> `naval_invasion_support_priority` is **present in `hoi4.exe` (1.19.2)** - checked against a control
> string that is not - and vanilla's own `common/ai_strategy/ENG.txt` writes **7 entries** of it
> (`id = 29 / 68 / 69 / 169 / 202` at `value = 200`, plus two on the Bismarck Sea). The type is real
> and undocumented. What survives from the row: WA has **zero uses** of it, and the range/combination
> WA's docs gave it were invented. The `supremacy` -> `dominance` rename below is unaffected.
>
> **Method note:** "absent from `_documentation.md`" is not evidence a token does not exist. The
> install ships 103 documented types and more than that in the binary. Grep the exe, and check a
> control string in the same run.

## C6 (original text) - `naval_invasion_support_priority` does not exist; `supremacy` was renamed

**WA-A:28** lists `naval_invasion_support_priority` as a NAVAL type ("Priority for naval invasion
support in a sea region"); **WA-B:109** gives it a combination rule ("Sums per region") and a range
("0 to +100").

**ENGINE:53-61** (the navy token list) contains: `naval_avoid_region`, `naval_convoy_raid_region`,
`naval_invasion_focus`, `naval_invasion_dominance_weight`, `naval_mission_threshold`,
`strike_force_home_base`, `naval_dominance`, `convoy_raiding_target`. No `naval_invasion_support_priority`.
It is absent from the 2023-07 copy too. **It is an invented type.**

Related rename: WA's 2023-07 copy lists `naval_invasion_supremacy_weight` (`documentation.info:52, :322`);
2024-11 replaced it with `naval_invasion_dominance_weight` (ENGINE:57, 391-398). WA-A:27 already uses the
new name.

No live risk: **zero uses** of `naval_invasion_support_priority`, `naval_invasion_dominance_weight` and
`naval_invasion_supremacy_weight` in `common/ai_strategy/` (measured). The damage is documentary - two
of the three rows in the NAVAL domain table describe types the mod does not and cannot use.

---

## C7 - `force_ratio` and `infantry` are not `ai_strategy` types

**WA-A:17-18** lists both in the canonical TYPE -> DOMAIN table ("`force_ratio` | FRONT | Front allocator
ratio bias", "`infantry` | FRONT | Infantry-specific front bias"). **WA-B:47** repeats them in the domain
table and **WA-B:88** gives `infantry` a combination rule and a 0..100 range. **WA-A:149-152** claims 34
instances ("ALLIES 28, FRA 6").

Neither token appears in the 2024-11 or the 2023-07 token list.

Measured in `common/ai_strategy/`:
- `type = force_ratio`: **0 occurrences**.
- `type = infantry`: every occurrence is inside a `divisions_in_state = { type = infantry size > 2
  state = N }` **trigger**, not an `ai_strategy` block - e.g.
  `WA_AI_MILITARY_COUNTRY_ENG_INVASION.txt:250, :257, :264`. The Phase 1 count of 34 is a grep artifact
  from matching `type =` without checking the enclosing block.

---

## C8 - the `garrison` "-5000 documented override"

**WA-B:131**: "`garrison` uses a **negative-override convention**: a single block of `value = -5000` is
the **documented** way to force garrison off in a state, and is treated as authoritative regardless of
other writers." **WA-A:147** repeats it: "uses the **documented** `value = -5000` force-off override.
Preserve this pattern".

**ENGINE:45** is the entirety of what either edition says about `garrison`:

```
- `garrison`
```

There is no `### garrison` section, no parameters, no example, in 2024-11 or in 2023-07. The convention
may well be correct in-engine, but calling it "documented" is false, and "treated as authoritative
regardless of other writers" is asserted with no source. Note also that WA-B:87 gives the same type a
self-contradicting row: engine combination "Max wins", policy "Additive".

---

## CONFIRMED - repo beliefs the engine file backs

Compact list. Each is a WA claim the 2024-11 file directly supports.

| # | Claim | WA | ENGINE |
| --- | --- | --- | --- |
| 1 | `front_armor_score` keys on `role = armor` **or** `front_role_override = offence` in the template | WA-A:158 | :39 |
| 2 | `front_armor_score` takes no generic targeting (id-keyed only) - the "Unexpected token: country_trigger" measurement | WA-A:159-160 | :39 (one-line entry, no parameter block) - engine consistent, does not contradict |
| 3 | `front_unit_request` / `invasion_unit_request` accept `tag` / `state` / `strategic_region` / `area` / `country_trigger` / `state_trigger`, tested against the invasion target for invasions and the front provinces for fronts | WA-B:333 | :315-332 |
| 4 | `state_trigger` scoping: THIS = the state, FROM = the enemy country, FROM.FROM = us | WA-C:31 | :329, :243, :270 |
| 5 | `force_concentration_factor` arithmetic: `value = 20` on a 15% base -> 35% of surplus | WA-C:20-22, WA-B:82 | :251-256 |
| 6 | `AIFC_UNIT_RATIO_BASE = 0.15`, `AIFC_UPDATE_FREQUENCY_DAYS = 5`, `AIFC_MAX_NR_FRONTS = 4`, not overridden by WA | WA-C:33-35 | DEFINES:3499, 3494, 3500; WA `05_defines.lua` has 0 hits for `AIFC` / `FORCE_CONCENTRATION` |
| 7 | `force_concentration_front_factor` supports `ratio` (targets must cover that fraction of the front); `_target_weight` does not | WA-C:25-26 | :244 present, absent from :259-273 |
| 8 | `front_control` parameters `ordertype` (front/invasion), `execution_type` (careful/balanced/rush/rush_weak), `execute_order`, `manual_attack`, `ratio` | WA-B §9, all WA `front_control` blocks | :290-297 |
| 9 | `put_unit_buffers` `subtract_fronts_from_need` exists; subtraction is the default and `no` disables it | WA's `subtract_fronts_from_need = no` in the Fix 96 / Fix 99 buffers | :375-377 |
| 10 | `theatre_distribution_demand_increase` `id` is a **state** id, targeting the theatre that state belongs to | WA-A:42 usage | :386 |
| 11 | `strategic_air_importance` `id` is a strategic region, and "a stocked main front in active combat is usually around 35,000" | WA-A:167, WA-B:86 (quotes the 35,000 verbatim) | :643-650 |
| 12 | `invade`: negative avoids invasions completely, positive multiplies the invasion importance score; keyed per target country only, so it cannot express "not in this theatre" | WA-B:330-332 | :335-343 |
| 13 | `dont_defend_ally_borders` is addressed by `id = <ally tag>` and is binary (>0 on, <=0 off) | WA-A:40, WA-B:97 | :222-229 |
| 14 | `abort` or `abort_when_not_enabled` should be on every block | WA's near-universal use (1335 abort tokens over 1305 top-level blocks) | :183-189 |

**One place where the engine doc is wrong and WA is right.** ENGINE:255 names the define
`FORCE_CONCENTRATION_UNIT_RATIO_BASE`. That key **does not exist** in `00_defines.lua` (0 hits); the live
key is `AIFC_UNIT_RATIO_BASE` (DEFINES:3499), which is what WA-C:20 and WA-B:82 use. The engine doc's
2024-11 text lags a rename. Real usage settles it in WA's favour.

---

## UNSUPPORTED - stated as fact, engine silent

1. **`area_priority`** (321 uses, 3rd-heaviest THEATRE type). Listed at ENGINE:33, **no section in
   either edition**. WA-B:80's "Sums per area / -200 to +200" is entirely reverse-engineered and is not
   labelled as such.
2. **The §4 combination column as a whole** (WA-B:79-113). It assigns an engine combination rule to 25
   types. The engine file states a combination rule for exactly one pair: `avoid_starting_wars` and
   `conquer`, "this value is additive with the 'conquer' strategy" (ENGINE:202-209). Every other "Sums
   per X" in that table is a WA inference presented in a column headed *"Engine combination"*.
3. **"Highest value wins"** for `dont_defend_ally_borders` / `force_defend_ally_borders` (WA-A:278,
   WA-B:97). The engine states the per-block semantic (binary) and is **silent** on multi-writer
   resolution. If the engine sums before thresholding, a `-100` suppressor and a `+100` activator
   cancel - the opposite of "highest wins". WA-A:288 leans on this to justify not de-duplicating 58
   cross-layer groups.
4. **Ranges for the token-list-only types**: `spare_unit_factor` (0.0-1.0), `garrison_reinforcement_priority`,
   `naval_mission_threshold` (-100..+100), `strike_force_home_base` (bool), `naval_convoy_raid_region`
   (-1000..+1000). No sections exist.
5. **`naval_avoid_region`'s signed convention** (WA-B:119-128). No engine section. **Correctly framed**
   though - WA-B says "The **working convention** is therefore" and grounds the table in a 402-entry
   measurement. This is the right shape for an unsupported claim; the rest of §4 is not written this way.
6. **`support`** (WA-B:103, 132). No engine section in either edition. WA-B **correctly and repeatedly**
   labels the combination rule as "Unverified", "asserted, not measured". Good. But **WA-A:97 quotes an
   "Engine description" - "Pursues AI to support a certain country within wars, sending lend lease,
   volunteers, or expeditionary forces" - and attributes it to `documentation.info`.** That string occurs
   nowhere in the install (`grep -r`, 0 hits) and nowhere in `documentation.info`. Its provenance is
   unknown; the wiki is the likely source. It should carry the ASSUMED label, not an engine attribution.
7. **`front_unit_request`'s "base of 100"** (WA-B:338, load-bearing for the Fix 105 `-200` choice). The
   engine says only "will be added as a factor over regular requests" (ENGINE:331). The base is not
   stated. The `unit_ratio` section states a base of 100 for a *different* type ("Unit ratios are
   calculated as a base of 100", ENGINE:159) - which is probably where the belief came from, and is not
   the same type.

---

## UNUSED CAPABILITY

Only cases where the repo visibly built a workaround.

- **X1 `front_control priority`.** WA-B §6 defers an entire subsystem
  (`WA_AI_MILITARY_country_owns_<key>` / `faction_owns_<key>` scripted trigger pairs, Phase 5) to enforce
  Country > Faction > Default on Exclusive types. For `front_control` - the type WA-A:291 calls the
  hardest of them, 128 instances that "cannot be safely auto-deduped" - the engine already provides
  `priority`, and WA already sets it in 57 blocks without the spec acknowledging it. A layer-indexed
  priority convention (e.g. Default 100 / Region 200 / Faction 300 / Country 400) would express the whole
  precedence contract declaratively.
- **X2 `force_concentration_* country_trigger` / `tag` / `strategic_region` / `area`.** AIFC Layer 4
  targets exclusively through `state_trigger` + the engine-encoded `*_ref` arrays (Fix 31 comment,
  WA-C:395-401), and the armour-steering rule was moved out of `ai_strategy` into a weekly scripted
  `add_ai_strategy` emitter because "a runtime-chosen target cannot be expressed in an ai_strategy file
  at all" (WA-C:437-455). That reasoning is correct for `front_armor_score`, which is id-keyed. It is
  **not** correct for the two force_concentration types, which take `country_trigger`. WA-B:426-428
  records an open risk that all four `*_ref` arrays read `-10737.4` (unresolved token) campaign-wide and
  Layer 4 may have been inert - the documented `country_trigger` / `tag` route is an alternative that
  does not depend on encoded scope references at all.
- **X3 `put_unit_buffers order_id`.** Used 154 times across 25 WA files, and Fix 96 / Fix 99 explicitly
  reason about "own order_id" for pool separation. No WA document states what the parameter means. Its
  documented meaning (ENGINE:354-355, same-id blocks *share* a ratio) is exactly the fact needed to
  evaluate WA-B:383's summing arithmetic.
- **X4 `avoid_starting_wars`.** One use mod-wide. It is the only type the engine documents an explicit
  stacking contract for, designed as the targetless counterpart to a per-target `conquer` (ENGINE:197-210)
  - the shape of "suppress everything, then re-enable one target" that WA writes by hand elsewhere.

---

## Question (a) - do a region-keyed and an area-keyed `front_unit_request` sum on the same front?

**The engine file does not answer it. It is silent.**

- ENGINE:315-332 documents the type's parameters and says of the target keys "Can specify multiple" -
  that is an OR over targets **within one block**, not a statement about two blocks.
- The `value` line reads "Will be added as a factor over regular requests" (ENGINE:331) - it describes
  the relation between the strategy and the *engine's base request*, not between two strategies.
- The file states cross-block additivity **once**, for `avoid_starting_wars` + `conquer` (ENGINE:202-209).
  The fact that the author felt the need to spell it out there, and nowhere else, cuts weakly **against**
  assuming it is the universal default - but that is an inference, not a reading.

Usage does not settle it either. Vanilla and Expert AI both write many `front_unit_request` blocks per
country without ever documenting an intended sum, and neither offers a case where a region-keyed and an
area-keyed entry provably overlap on one front with an observable outcome.

**Verdict for WA-B:454 / checklist R64:** the assumption stays an assumption. The engine documentation
is not a source that can retire it; campaign R64 remains the falsifier. What the engine file *does*
change is the confidence in the assumption's neighbours - the "Engine combination" column of WA-B §4 is
inference throughout, so R64 tests a belief the whole table shares, not a one-off.

## Question (b) - is a custom `ai_area` valid as `put_unit_buffers`'s `area =`?

**Almost certainly yes, and peer usage proves the general mechanism on 1.19.2 - but not for this type
specifically.**

What is measured:

1. The engine documents `area` on `put_unit_buffers` as "ai areas that the orders will use these buffers
   in" (ENGINE:370-372). It names a key, with no enumeration and no restriction to base-game keys.
2. The same `area = europe` parameter on `front_control` / `front_unit_request` /
   `force_concentration_*` is documented as "Target a specific ai area" (ENGINE:241, 268, 287, 327).
3. `naval_dominance` documents `id = winter_war_front # AI area key` (ENGINE:677) - area keys are
   resolved **by name from `common/ai_areas/`**, not from a fixed enum. `winter_war_front`
   (`ai_areas/default.txt:333`) and `normandy_landing_zone` (`:138`) are ordinary content definitions, not
   engine constants.
4. **Peer proof (Expert AI 5.0, supported_version 1.19.2.0):** EAI defines its own areas in
   `common/ai_areas/EAI_ai_areas.txt` (`EAI_pacific_islands`, `EAI_russia_plains`, `EAI_east_asia`,
   `EAI_southern_africa`, …) and consumes them as `area = EAI_russia_plains` etc. in **8 `front_control`
   blocks and 2 `front_unit_request` blocks**. A mod-defined ai_area therefore resolves as an `area =`
   argument on this engine version.
5. EAI's own `put_unit_buffers` blocks use only base-game areas (`asia`, `just_norway` - the latter is
   vanilla, `default.txt:313`). So there is **no peer instance** of a custom area on `put_unit_buffers`
   specifically.
6. In-repo evidence: WA uses exactly two custom areas in `put_unit_buffers`
   (`WA_AI_MILITARY_tunisia_regions`, `WA_AI_MILITARY_east_africa_colony_regions`), against 100+ uses of
   base-game areas. WA-B:453 records that the 2026-08-17 F9 boot loaded them without error.

**Verdict:** the "load risk" recorded for Fix 99 can be closed - loading is proven twice over (WA's own
boot, and EAI shipping custom areas into the same parameter family). The *behavioural* half - that the
buffer actually lets orders in that area draw on it - is **not** settled by any document; ENGINE:370-372
describes the intent but nothing measures it. Keep R64 leg 1 as the falsifier for drawing, drop it as a
falsifier for loading.

---

## Notes for whoever acts on this

- Nothing here was changed. Every finding is documentation-level except **C3** (8 live
  `naval_dominance` entries at 1000 against a documented 0-100 ceiling), which is the only
  finding with a plausible in-game effect, and **C2/X1** (the engine's `priority` field vs the deferred
  Phase 5 subsystem), which is a design decision rather than a bug.
- The single highest-leverage repair is replacing `common/ai_strategy/documentation.info` with the
  2024-11 edition, or deleting it and pointing WA-A/WA-B/WA-C at the install path. Every
  line-number citation in WA-A and WA-B currently indexes into the 2023-07 file and does not resolve
  against the install's.
