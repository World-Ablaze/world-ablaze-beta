# WA AI Military System

Authoritative spec for the layer model, domain split, per-type overlap policy, and naming convention used by every `ai_strategy` block in `common/ai_strategy/WA_AI_MILITARY_*.txt`.

Read this document **before** adding or changing any military `ai_strategy` block. The companion file `WA_AI_MILITARY_TYPES_REFERENCE.md` lists every `type =` currently in use, where it lives today, and its target layer.

This is the Phase 1 contract. It describes the target shape of the system. Existing files do not yet conform on every point; migration is staged across Phases 2-6 (see end of this document). Until each phase lands, the rules below apply to **new and modified** blocks.

---

## 1. Purpose

The WA AI military system steers AI strategic-level military behaviour: front allocation and unit requests, front control modes, invasion budgets and targets, garrison weighting, theatre distribution, naval region avoidance, strike-force basing, force concentration, and country-to-country diplomatic intent flags (`conquer`, `protect`, `ignore`, `contain`, etc.). It does **not** cover production, templates, equipment design, lend-lease, or research; those are owned by other WA_AI subsystems documented in `AGENTS.md`.

All system content lives in `common/ai_strategy/WA_AI_MILITARY_*.txt` and is gated by triggers in `common/scripted_triggers/WA_AI_MILITARY_triggers.txt` and `common/scripted_triggers/WA_AI_CONFIG.txt`.

---

## 2. Layer model (4 layers)

| Layer | Files | Gating | Country tags allowed? |
| --- | --- | --- | --- |
| **Default** | `WA_AI_MILITARY_DEFAULT_*.txt` | Archetype triggers only (`WA_AI_MILITARY_is_major_continental`, `WA_AI_MILITARY_is_major_naval`, `WA_AI_MILITARY_is_minor_country`, etc.) | No |
| **Region** | `WA_AI_MILITARY_REGION_<NAME>.txt` | Geography triggers (e.g. `WA_AI_CONFIG_MILITARY_is_south_america`) | No |
| **Faction** | `WA_AI_MILITARY_FACTION_<NAME>[_<DOMAIN>].txt` | Faction-membership triggers (`WA_AI_MILITARY_is_allies_member`, `_is_axis_member`, `_is_comintern_member`, `_is_co_prosperity_member`, `_is_china_front_member`, `_is_commonwealth_member`) plus optional `WA_AI_CONFIG_MILITARY_*` archetype refinement | No |
| **Country** | `WA_AI_MILITARY_COUNTRY_<TAG>[_<DOMAIN>].txt` | Country gating; `tag = <TAG>` and `original_tag = <TAG>` are allowed and expected | Yes |

### Layer responsibilities

- **Default** carries generic archetype-driven behaviour for any country matching an archetype trigger. Examples: minimum garrison floor for minors, default armor scoring for continental majors, default unit-request scaling for naval majors. Default rules must work for any country that hits the archetype trigger without further customisation.
- **Region** carries geography-driven shared rules that span multiple countries but are not faction-bound. Example: South American countries staying at home and not invading distant theatres regardless of faction membership.
- **Faction** carries coalition behaviour: where the bloc collectively defends, where it invades, who it ignores, intra-faction `force_defend_ally_borders` patterns, etc. Faction blocks may further refine by archetype (`WA_AI_CONFIG_MILITARY_is_axis_minor` inside an Axis faction file is fine), but they may not target individual countries by tag.
- **Country** carries country-specific behaviour. This is the only layer permitted to use `tag = <TAG>` and `original_tag = <TAG>`. If a rule depends on a single country's geography, doctrine, or historical role, it belongs here.

### When a behaviour spans layers

If the same intent can be expressed at multiple layers, prefer the **highest-shared layer** (Default > Region > Faction > Country). Push down to a lower layer only when the higher layer's archetype/region/faction trigger does not capture the actual scope of the rule. Do not duplicate the same block at multiple layers; that is exactly what Phase 4 will de-duplicate, and what the Phase 5 mutual-exclusion triggers exist to manage for the few Exclusive types.

---

## 3. Domain split convention

Every country and every faction with content in more than one domain is split into one file per domain. This is a uniform structure, applied even for small files, so that adding a new strategy block always has a predictable destination.

| Domain | File suffix | Strategy types it owns |
| --- | --- | --- |
| Front | `_FRONT` | `front_unit_request`, `front_control`, `front_armor_score`, `force_concentration_front_factor`, `force_concentration_target_weight`, `garrison` (small/normal cases). **`force_ratio` and `infantry` are NOT `ai_strategy` types** and were removed from this list 2026-08-18 - see the note under §4 |
| Invasion | `_INVASION` | `invasion_unit_request`, `invade`, `naval_invasion_focus` |
| Naval | `WA_AI_NAVAL_*` | `naval_avoid_region`, `naval_convoy_raid_region`, `naval_dominance`, `naval_mission_threshold`, `strike_force_home_base`, `naval_invasion_dominance_weight`, `naval_invasion_support_priority`, `strategic_air_importance` (when the rule is sea-facing) |
| Air | `_AIR` | `strategic_air_importance` (when the rule is land-theatre-facing). **The type ranks regions for the planes the engine already requests; it does not create demand** — requests come from own combats/armies, enemy planes in a combat region, enemy factories, ships (verified `a232d96c`, checklist R15 RECUT 2026-08-16), so a pull decides where wanted planes go and cannot stage an air force ahead of the ground war. **The demand side is the `NDefines.NAI` air block of `common/defines/05_defines.lua`, and WA overrides it.** Since 2026-08-18 that includes two request FLOORS: `NAVAL_MIN_EXCORT_PLANES = 100` (vanilla **0** - a floor where the engine had none) and `LAND_COMBAT_MIN_EXCORT_PLANES = 200` (vanilla **80**), alongside the older `STR_BOMB_MIN_EXCORT_PLANES = 500` (vanilla 200), `LAND_COMBAT_CAS_PER_COMBAT = 300` (vanilla 60) and `LAND_COMBAT_BOMBERS_PER_LAND_FORT_LEVEL = 30` (vanilla 6). A define is **global**: unlike an `ai_strategy` type it reaches every country at engine cadence and cannot be gated, so it is the wrong instrument whenever a type would do. None of these numbers is campaign-calibrated - they are **ASSUMED**. Generic theatre pulls live in `WA_AI_MILITARY_DEFAULT_AIR_theatres.txt`; coalition policy in `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt` — the Reich ladder (gated on deployed strategic-bomber count rather than dates) and, since Phase 7d, the whole former ENG.txt Allied family (Channel-coast push/avoidance, Sicily push, home-islands threat/lost, occupied-Europe and out-of-theatre avoidance) gated on `WA_AI_MILITARY_is_allies_member` plus state triggers (staging armies, footholds, human enemy on the far shore) instead of tag lists and dates — all switches in `WA_AI_MILITARY_triggers.txt`; Phase 7e did the same for the GER.txt family: Axis-wide avoidance (front not open, unfronted France, British Isles outside the Battle-of-Britain window) in `WA_AI_MILITARY_FACTION_AXIS_AIR.txt`, the Reich air-defence pull in `WA_AI_MILITARY_COUNTRY_GER_AIR.txt` (the +100k schwerpunkt push was not carried over: the +50k contested pull composed with the -40k unfronted-France suppression already yields the north/south differential); contest detection in `WA_AI_MILITARY_AIR_theatre_contested_*` (`WA_AI_MILITARY_triggers.txt`). The companion state-membership triggers `WA_AI_MILITARY_AIR_theatre_state_*` (same file, must-match the contested lists) feed `WA_AI_build_theatre_air_bases` in the construction system, which builds the air-base capacity the pulls need — a pull with no friendly basing in range is inert. **Membership is a geographic block, not a target list:** since **Fix 114** (2026-08-20) that builder walks its ladder twice, admitting only states on the contested edge (`WA_AI_PC_state_is_near_contested_edge`, two neighbour rings from enemy-held ground) before falling back to the whole theatre, because campaign `3d68a183` put three of four North African air-base projects in Morocco while front-line Constantine ran at 150 % of nominal capacity. Probe: `WA_TLM_r114_thair_near_n` / `_far_n`, checklist R78. |
| Diplomacy | `_DIPLOMACY` | `conquer`, `antagonize`, `protect`, `contain`, `ignore`, `ignore_claim`, `declare_war`, `diplo_action_desire`, `diplo_action_acceptance`, `dont_defend_ally_borders`, `force_defend_ally_borders` |
| Theatre | `_THEATRE` | `theatre_distribution_demand_increase`, `area_priority`, `put_unit_buffers`, `spare_unit_factor` |
| Garrison | `_GARRISON` | Only when garrison rules for one country are large enough to warrant their own file; otherwise garrison stays inside `_FRONT` |

Naval rules must remain adaptive. The layer owns the concern (`Country > Faction > Default`), but the `enable = {}` block should also call readiness/opportunity triggers when a rule depends on changing strategic conditions. For example, Axis deep-Atlantic avoidance is a Faction constraint while the United Kingdom is operational; it is disabled by `WA_AI_MILITARY_NAVAL_axis_has_atlantic_opening` after the fall/capitulation of the UK so Axis countries can use Country or future Faction plans in the Atlantic.

A given country only gets a file for the domains in which it actually has content. A Default or Faction file may be unsplit if it only carries one domain (e.g. `WA_AI_MILITARY_DEFAULT_INVASION.txt` is fine without a `_FRONT` sibling).

Names follow the pattern `WA_AI_MILITARY_<LAYER>_<DOMAIN>[_<TAG>].txt` for military domains. Naval files use the domain-first pattern `WA_AI_NAVAL_<LAYER>[_<TAG_OR_SCOPE>].txt`. Examples:

- `WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt`
- `WA_AI_MILITARY_REGION_SOUTH_AMERICA.txt`
- `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`
- `WA_AI_NAVAL_COUNTRY_USA.txt`

---

## 4. Per-type overlap policy

This is the master legend. For each `ai_strategy` `type` currently in use, it states how the engine combines values, whether the WA system treats the type as **Additive** (multiple layers may contribute) or **Exclusive** (only one layer should set it), and the precedence rule when Exclusive.

> **Value ranges:** the "Typical range" column below is descriptive (Phase 1 snapshot). The
> **normative** ranges and value-economy rules are in `WA_AI_MILITARY_ECONOMY.md` (Phase 7
> contract), linted by `tools/military_economy_audit.py`. Where the two disagree, the economy
> document wins for new and modified blocks.

> **The combination column is mostly inference.** `common/ai_strategy/documentation.info` states a
> cross-block combination rule for exactly ONE pair - `avoid_starting_wars` + `conquer`. Every other
> combination below is WA's reverse-engineering. Each cell is tagged **E** (the engine doc says it) or
> **I** (WA inference, never confirmed). Treat an **I** cell as ASSUMED.

| Type | Combination (**E**ngine / **I**nference) | Policy | Precedence (if Exclusive) | Typical range |
| --- | --- | --- | --- | --- |
| `front_unit_request` | **E** for the relation to the engine's own request: `value` "will be added as a factor over regular requests". **No base is stated** - the "base of 100" belief came from the unrelated `unit_ratio` section. Cross-block summing: **I** | Additive | n/a | -1500 to +200 |
| `area_priority` | **I** - token listed, no engine section, despite being the 3rd-heaviest type in the mod (321 uses) | Additive | n/a | -200 to +200 |
| `theatre_distribution_demand_increase` | **E** - `value` is an **absolute count of divisions** added to the demand of the theatre containing the `id` state (`documentation.info` section `theatre_distribution_demand_increase`) | Additive | n/a | 4 to 10 - every live value in the mod. NOT a percentage: `500` would order 500 extra divisions into one theatre |
| `force_concentration_factor` | **I** - Sums, added to define `AIFC_UNIT_RATIO_BASE` (0.15) | Additive | n/a | -100 (hard off) to +25, in percentage points |
| `force_concentration_front_factor` | **I** - Sums | Additive | n/a | -100 to +100 (plain percent) |
| `force_concentration_target_weight` | **I** - Sums per target | Additive | n/a | -100 to +100 (plain percent) |
| `front_armor_score` | **I** - Sums | Additive | n/a | 0 to +50 |
| `strategic_air_importance` | **I** - Sums per strategic region, on top of engine terms (own combats x100, own armies x25; hot main front ~35,000). **Ranks only** — the plane request is engine-side (see §3 Air) | Additive | n/a | +50,000 standing theatre pull (DEFAULT_AIR); +100k / +200k emergency pushes (Faction); -2k to -40k retuned suppressions (Faction); the -500k black holes survive only in the FRA/JAP/SOV Country legacy blocks |
| `garrison` | **I** throughout - the engine doc has **no `garrison` section at all**, only the bare token. "Max wins" and the -5000 force-off are WA convention observed in play, not engine text | Convention: negative-override | n/a | -5000 (force off) or 0 to 200 |
| `spare_unit_factor` | **I** - token listed, no engine section | Additive | n/a | 0.0 to 1.0 |
| `front_control` | **Native integer precedence: `priority`, default 0, "higher prio strats will override lower"** (`common/ai_strategy/documentation.info` section `front_control`). Ties at equal priority are undocumented. | **Exclusive per area** | Two mechanisms, see §6 | mode enum |
| `protect` | **I** - Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `ignore` | **I** - Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `ignore_claim` | **I** - Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `contain` | **I** - Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `naval_invasion_focus` | **I** - Boolean | **Exclusive** | Country > Faction > Default | bool |
| `strike_force_home_base` | **I** - token listed, no engine section | **Exclusive per region** | Country > Faction > Default | bool |
| `dont_defend_ally_borders` | **E** per block: binary, ">0 activates, <=0 deactivates" (`documentation.info` section `dont_defend_ally_borders`). **Engine silent on multi-writer resolution** - "highest value wins" was an inference and is withdrawn; if the engine sums first, a -100 and a +100 cancel | **Exclusive per ally** | Country > Faction > Default | bool |
| `force_defend_ally_borders` | **I** - no engine section; assumed to mirror `dont_defend_ally_borders` | **Exclusive per ally** | Country > Faction > Default | bool |
| `invasion_unit_request` | **I** - Sums | Additive | n/a | 0 to 50 |
| `invade` | **I** - Sums per target | Additive per target | n/a | 0 to 200 |
| `conquer` | **I** - Sums per target | Additive per target | n/a | 0 to 200 |
| `antagonize` | **I** - Sums per target | Additive per target | n/a | 0 to 200 |
| `support` | **Unverified** — assumed to sum per target by analogy with its neighbours, never measured | Additive per target (assumed) | n/a | 100 (nudge) / 200 / 500 (strong) / -1000 to -5000 (suppress) |
| `naval_avoid_region` | **I** - no engine section; the signed convention below is grounded in a 402-entry measurement, not in engine text | Additive per region | n/a | -10000 to +2000 — see the convention note below |
| `naval_convoy_raid_region` | **I** - token listed, no engine section | Additive per region | n/a | -1000 to +1000 (negative = suppress raiding there) |
| `naval_dominance` | **E** - "used to **set** the naval dominance for an AI area", `value` a "Percentage between 0 and 100" (`documentation.info` section `naval_dominance`). The engine states no additive behaviour; "Additive" is an inference | Additive per region | n/a | 70 - 80, the only values live (6 entries) |
| `naval_mission_threshold` | **I** - token listed, no engine section | Additive | n/a | -100 to +100 |
| `naval_invasion_dominance_weight` | **I** - Sums | Additive | n/a | 0 to +100 |
| `naval_invasion_support_priority` | **Real type, undocumented.** Absent from both editions of `documentation.info`, but the literal string is present in `hoi4.exe` (1.19.2) and vanilla's own `ENG.txt` writes 7 entries of it. Combination and range: **I**, and untested - **WA has zero uses** | Additive per region | n/a | vanilla uses 200 / 25 / -100 keyed by `id = <strategic region>` |
| `put_unit_buffers` | **E** - `ratio` is a **fraction of the country's whole army**; blocks sharing an `order_id` **share** one ratio rather than summing; `states` places the garrison order, `area` chooses which orders may draw on the pool (`documentation.info` section `put_unit_buffers`). Combination across *different* order_ids: engine silent | Additive per **order** | n/a | 0.01 to 1.0. `1.0` is deliberate in the five "everything home" blocks (`ENG_germany_has_won`, `FRA_paris_commune_sit_tight`, `MAN_pacify_part_1`, `USA_oh_shit`, `ALLIES_commonwealth_stage_usa_east`) |
| `declare_war` | **I** - Sums per target | Country-only | n/a | 0 to 100 |
| `diplo_action_desire` | **I** - Sums per target/action | Country-only | n/a | 0 to 100 |
| `diplo_action_acceptance` | **I** - Sums per target/action | Country-only | n/a | 0 to 100 |

### Notes on the policy column

- **Additive** means the engine combines values from multiple `ai_strategy` blocks (typically by sum, sometimes by max). Layers may safely contribute to the same key. Tuning differences between layers are by design.
- **Exclusive** means the WA system enforces single-layer ownership for a given key (target, area, ally, region, mode). The engine may still technically allow multiple writers, but stacking writers produces unpredictable behaviour. The Phase 5 mutual-exclusion triggers that enforce this **shipped in `d149a204b`** and live in `common/scripted_triggers/WA_AI_MILITARY_PHASE5_ownership_triggers.txt`; §6 is their contract and inventory.
- `naval_avoid_region` **is signed, and a negative value is an attraction, not a weaker avoidance.** Reading only the region id will mislead you. Corrected 2026-08-14 (Fix 63): the range column previously read "0 to +500", which no file in the mod has ever respected. Measured across the 402 entries actually in `common/ai_strategy/`, the values in use are `2000` (326 entries), `1000` (29), `100` (23), `-1000` (18), `200` (3), `-2000` (2) and `-10000` (1). The working convention is therefore:

  | Value | Meaning |
  | --- | --- |
  | `100` – `200` | soft nudge; the AI still deploys there routinely |
  | `1000` | soft wall — the paired suppression half of a corridor plan |
  | `2000` | hard wall — "do not go here", the mod's default deterrent |
  | `-1000` | the pull half of a corridor plan (`WA_AI_NAVAL_FACTION_ALLIES` corridors) |
  | `-2000` / `-10000` | force a route open (USA Torch, `ENG_protect_home` on the Channel) |

  Because the type is Additive per region, **always sum every writer for a region before concluding what the AI will do** — a `-2000` "open this route" can be, and in the Bay of Biscay case is, silently outvoted by three `+2000` walls. `WA_AI_NAVAL_COUNTRY_USA_operation_torch_preparation` carries a worked example of that arithmetic in its header comment.
- `naval_dominance` values in use are 70–80 (6 entries), inside the documented 0–100. The engine says the type **sets** a percentage and says nothing about stacking, so "sums over 100 are legal" was an inference and is withdrawn - keep every writer inside 0–100 and call out any overlap at the site. (The 8 out-of-scale `value = 1000` entries this note used to miss were retired 2026-08-18 with the ENG `naval_dominance` probe.)
- `garrison` uses a **negative-override convention**: a single block of `value = -5000` is the way WA forces garrison off in a state. **This is convention, not engine text** - the engine doc has no `garrison` section, only the bare token, so both the override and "authoritative regardless of other writers" are ASSUMED. This is how `WA_AI_MILITARY_COUNTRY_SPR.txt:143-144` disables garrison in a specific configuration.
- `support` is the engine's “help this country win its wars” dial - **it carries lend-lease, volunteers AND expeditionary forces together**, and it is the ONLY script-side lever on the last of those (there is no expeditionary `type`, no scripted effect sends one, `diplomatic_relation` has no such relation, and `transfer_units_fraction` hands over ownership permanently rather than lending). **Faction layer is sanctioned for it**, and that does not extend the Country-only rule below: `declare_war` and the two `diplo_action_*` types are sovereign decisions a coalition must not take for a member, whereas lending weight inside a coalition you already belong to is coalition behaviour by definition. First Faction-layer writer: `WA_AI_MILITARY_ALLIES_back_the_coalition_major_{ENG,USA}_DIPLOMACY` (Fix 106). **Its combination rule is asserted, not measured** - assumed to sum by analogy with its neighbours in this table. The mod DOES already stack it: `USA.txt`'s `USA_stop_uk_from_falling` is one block under one `enable` and writes `support` toward LUX at :2321 and :2333, and toward GUA at :2388 and :2448 (both -1000). So a sum is what the author of that block assumed too - it has simply never been verified in a save. (A first pass at this note claimed nothing in the mod stacked, generalising from POR → SPA, which IS two mutually exclusive focus branches. Grouping by file rather than by enclosing block is what hid the USA case.) The Fix 106 blocks cannot stack with `USA.txt`'s `support id = ENG value = 500` regardless, because they exclude ENG and USA as writers. **Open question the campaign must settle:** whether the type CREATES an expeditionary intent or merely RANKS one the engine already forms - on campaign `7c7803a8` all three countries that actually lent divisions (SIK, ITL, BUL) carried **no** `support` block at all, so ranking-not-creating is live, and checklist R70 leg 1 is its falsifier.
- **`force_ratio` and `infantry` are not `ai_strategy` types.** Neither string appears in either edition of `documentation.info`; `force_ratio` is not even present in `hoi4.exe`. Every `type = infantry` in `common/ai_strategy/` - 82 of them - sits inside a `divisions_in_state = { type = infantry size > N state = M }` **trigger**, not an `ai_strategy` block; the earlier "34 instances" count was a grep artifact from matching `type =` without checking the enclosing block. Both were removed from the domain table, from this policy table and from the 35 `# Phase 6 split:` file headers on 2026-08-18.
- `put_unit_buffers` `order_id` is **pool identity, and the engine documents it**: "ratio of same orders ids will be share same ratio" (`documentation.info` section `put_unit_buffers`). Two blocks with the same `order_id` therefore **share** one ratio - they do not add. Give a buffer its own `order_id` whenever it must not be diluted by an existing one (WA already does: 9102, 9606, 9608). What the engine does NOT say is how *different* order_ids combine.
- `avoid_starting_wars` is the one type the engine gives an explicit stacking contract: it is targetless and "additive with the `conquer` strategy", so `avoid_starting_wars = -200` plus `conquer id = GER value = 200` yields conquer 0 for Germany and -200 for everyone else. That is the declarative form of "suppress everything, then re-enable one target", which WA writes by hand elsewhere. One use mod-wide.
- `declare_war`, `diplo_action_desire`, and `diplo_action_acceptance` are Country-only by convention: the Default and Faction layers should never push a country to declare war or accept diplomacy; that decision belongs in the country's own file.

---

## 5. Authoring rules

1. **Every block must declare an `enable = { ... }` clause.** `always = yes` is forbidden except for an explicitly justified static defensive bias. Such blocks must include a comment beginning with `# always-on:` explaining why no dynamic gate is appropriate.
2. **No `tag = X` or `original_tag = X` outside Country layer files.** Faction, Region, and Default layers must use `WA_AI_CONFIG_MILITARY_*` archetype/region triggers or `WA_AI_MILITARY_is_<faction>_member` triggers.
   - **Grace clause:** until Phase 3 is complete, existing tag lists in faction files (e.g. `WA_AI_MILITARY_COUNTRY_CHINA_FRONT.txt`) may remain in place. They must not be **extended**, and any modification of an existing block in those files must replace the tag list with an archetype trigger or relocate the block to a Country file.
3. **Each strategy block must include a header comment** with at least: `purpose`, `range`, `policy` (Additive or Exclusive), and `domain`. Example:
   ```
   # purpose: discourage USN from sailing into the Black Sea
   # range:   0 to +500
   # policy:  Additive per region
   # domain:  NAVAL
   WA_AI_NAVAL_COUNTRY_USA_avoid_black_sea = { ... }
   ```
4. **Block names must follow** `WA_AI_MILITARY_<LAYER>_<DOMAIN>_<DESCRIPTOR>` for Default/Region/Faction military-domain blocks, `WA_AI_MILITARY_COUNTRY_<TAG>_<DOMAIN>_<DESCRIPTOR>` for Country military-domain blocks, and `WA_AI_NAVAL_<LAYER>[_<TAG_OR_SCOPE>]_<DESCRIPTOR>` for naval blocks. The descriptor is lowercase snake_case and should describe the *behaviour*, not the tag.
5. **Do not duplicate behaviour across layers.** If a Default rule and a Country rule cover the same intent, the Country rule should either differ meaningfully (Additive types) or take the Default rule's place through an ownership slug (Exclusive types - §6.2). If neither is possible, document the duplication in `WA_AI_MILITARY_TYPES_REFERENCE.md` rather than leaving it silent.
6. **Country-specific blocks living in faction files must be re-homed** to `WA_AI_MILITARY_COUNTRY_<TAG>_<DOMAIN>.txt` during Phase 2-4. Until then, keep them where they are but flag them in the types reference.

---

## 6. Mutual exclusion for Exclusive types - two mechanisms, and which one owns what

**Shipped, not planned.** The scripted ownership triggers this section used to defer to "Phase 5"
live in `common/scripted_triggers/WA_AI_MILITARY_PHASE5_ownership_triggers.txt` since `d149a204b`:
**49 slugs, all 49 read by at least one `ai_strategy` block, zero orphans** (measured 2026-08-19).

There are two mechanisms in play, and they are not interchangeable.

### 6.1 The engine's own precedence field - `front_control` only

`front_control` carries a native integer: `priority = 0  # Default 0, higher prio strats will
override lower` (`common/ai_strategy/documentation.info` section `front_control`). It is the only
Exclusive type in this mod's vocabulary that has one - `protect`, `ignore`, `ignore_claim`,
`contain`, `naval_invasion_focus`, `strike_force_home_base`, `dont_defend_ally_borders` and
`force_defend_ally_borders` have no `priority` parameter in either documentation edition. That is
why the scripted gates cannot be replaced by the engine field: they carry 42 of their 49 slugs for
types the engine gives no precedence field at all.

**The mod already uses `priority`, and it spends it on a semantic ladder, not a layer ladder.**
56 of 215 `front_control` blocks set it; the other 159 sit at the default 0. The tiers in use:

| Tier | Layer | Blocks | Meaning |
| --- | --- | --- | --- |
| `10000` | Default | 1 | `EXEC_no_stockpiles_stop` - emergency stop, must beat everything |
| `500` | Default | 1 | `EXEC_low_equipment_hold` - equipment brake |
| `320` - `340` | Faction | 12 | CHINA_FRONT exec/grind and careful-exec posture blocks |
| `300` | Faction | 4 | ALLIES / AXIS exec/grind posture blocks (§9) |
| `100` | Country (18), Faction (20), Region (2) | 40 | ordinary targeted control |
| `0` (unset) | Country (133), Faction (26) | 159 | everything else |

Read the ladder top-down and it is deliberate: a brake outranks an offensive posture, a posture
outranks routine per-area tuning. `WA_AI_MILITARY_DEFAULT_FRONT_control.txt` states that intent at
the code site ("priority 500 outranks the posture exec/grind blocks (300) ... and yields to
`no_stockpiles_stop` above (10000)").

### 6.1.1 The collision, audited (2026-08-18) - and the audit's own errors

The ladder and the layer rule do disagree, but the surface is much smaller than a first pass
suggests, and a first pass got four of ten rows wrong. Both are recorded here because the wrong
version was written down before the reviewers took it apart.

Of 81 Country-layer `front_control` blocks below priority 300, only **10** can co-apply with one of
the 8 Faction posture blocks at 300-340 - the rest target a different enemy or belong to a country
in no such faction. After correction:

| Block | Prio | Verdict |
| --- | --- | --- |
| `GER_germany_protect_the_fatherland_FRONT` | 100 | **real collision.** `tag = SOV ratio = 0.75 careful execute_order = no`, outranked by `AXIS_exec_vs_sov` (300) |
| `CZE_sit_on_your_forts_FRONT` | 100 | **real collision.** `execute_order = no` (`CZE_FRONT.txt:38`) under `ALLIES_exec_vs_germany` (300) |
| `FRA_paris_commune_sit_tight_2` | 0 | **real collision**, and a blanket one - no `tag`, no `area`, `execute_order = no` + `manual_attack = no` |
| `CHI_war_with_JAP_FRONT`, `_AI_FRONT` | 0 | **conditional** - both are holds, but see the resolution question below |
| `CHI_war_with_JAP_2_FRONT`, `_3` | 0 | **NOT holds.** `_2_` sets no `execute_order` at all; `_3` is `balanced` + `manual_attack = yes` |
| `CZE_help_france_FRONT` | 100 | **NOT a hold** - `execute_order = yes` (`CZE_FRONT.txt:65`). Aligned with the executor, harmless |
| `SPR_dont_attack_at_startup_of_civil_war` | 0 | **cannot co-apply.** Gated on `has_global_flag = SPR_civil_war_startup`, a ~3-day 1936 window; `AXIS_exec_vs_sov` needs Axis membership |
| `SPA_nationalist_all_out_push` | 0 | aligned with the executor (`rush`, `execute_order = yes`), harmless |

**The question the whole audit rests on is unanswered.** `documentation.info` says only "higher prio
strats will override lower" and, per field, "if set will override". Whether resolution is
**per-field or whole-block is ASSUMED**. It matters: `CHINA_FRONT_careful_exec_vs_japan` (330) sets
no `execute_order`, so under per-field resolution it never overrode the CHI holds and two of the
rows above are not collisions at all. Settle that before acting on any of them.

**Do not fix this by raising the holds above the posture tier.** That was proposed on 2026-08-18 and
both reviewers returned CONFLICT, for reasons worth keeping:

- It is the re-tiering the paragraph above forbids, proposed by the same session that wrote the
  paragraph.
- `GER_germany_protect_the_fatherland_FRONT` enables on a `surrender_progress > 0.05` branch that is
  **monotonic for a losing Germany**. Above every executor it stops being a hold and becomes a
  permanent Eastern-Front veto - the shape that killed the Soviet offensive in campaign `911bed3c`.
- `FRA_paris_commune_sit_tight_2` releases when the civil war ends, which requires somebody to
  attack. Raised, it is self-latching.
- The sanctioned mechanism is 6.2: an ownership slug, with the exclusion written **inside the exec
  block's `country_trigger`** - not in its `enable`, which would disarm the executor against every
  enemy rather than the owned one.
- And the effect is currently unscoreable: nothing in a save distinguishes "the hold was overridden"
  from "the hold never enabled", so any change here needs a probe before it can be verified.

**Consequence you must hold when writing a `front_control` block:** the layer precedence in 6.2 is
NOT what the engine applies to this type. Wherever no ownership slug gates the pair, a Faction
posture block at 300 outranks a Country block at 100 or 0. Do not "fix" this by re-tiering by
layer - the single integer is already carrying the brake/posture/routine meaning, and a layer
scheme written into the same field would silently disarm the brakes.

### 6.2 The scripted ownership gates - all nine Exclusive types

For Exclusive-policy types, scripted triggers guard layers so that the Country layer takes
precedence over Faction, and Faction over Default, on a per-key basis (per target, per area, per
ally, per region, per mode):

- `WA_AI_MILITARY_country_owns_<exclusive_key> = yes` - Country layer asserts ownership of this key.
- Faction blocks add `NOT = { WA_AI_MILITARY_country_owns_<exclusive_key> = yes }` to their `enable`.
- Default blocks add both `NOT = { WA_AI_MILITARY_country_owns_<exclusive_key> = yes }` and `NOT = { WA_AI_MILITARY_faction_owns_<exclusive_key> = yes }`.

Additive types are never gated by these triggers. The slug inventory as shipped:

| Slug prefix | Type | Slugs | Engine `priority` available? |
| --- | --- | --- | --- |
| `ddab_<TAG>` | `dont_defend_ally_borders` | 36 | no |
| `fc_area_<area>` / `fc_state_<id>` | `front_control` | 7 | yes - see 6.1 |
| `fdab_<TAG>` / `fdab_target_<area>` | `force_defend_ally_borders` | 4 | no |
| `sfhb_<region>` | `strike_force_home_base` | 2 | no |
| `contain_<TAG>` | `contain` | 1 | no |

A slug encodes **ownership, not intention**: add a tag to a trigger only when a Country-layer block
actually writes that (type, key). The file's own header carries that rule.

Region-layer writers of an Exclusive key follow the Faction rule (they gate on `NOT = { WA_AI_MILITARY_country_owns_<key> = yes }`); precedence is Country > Faction = Region > Default, and a Faction and a Region block must not write the same key with different intent (Fix 96: `WA_AI_MILITARY_REGION_ITALY_homeland_invaded_exec_FRONT` writes `front_control area = italy / south_italy` for the Italian owner, `WA_AI_MILITARY_AXIS_hold_italy_after_defection_FRONT` writes a country-keyed `front_control` for the owner's enemies - disjoint audiences by construction; slug `WA_AI_MILITARY_country_owns_fc_area_italy`).

---

## 7. Target file layout (post-refactor, for reference)

This is the post-Phase-2/3 target. It is reproduced here so that authors can choose the right destination today even though the rename is not yet done.

```
common/ai_strategy/
  WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt
  WA_AI_MILITARY_DEFAULT_FRONT_caps.txt
  WA_AI_MILITARY_DEFAULT_FRONT_core.txt
  WA_AI_MILITARY_DEFAULT_FRONT_control.txt          (was FRONT_execution)
  WA_AI_MILITARY_DEFAULT_INVASION.txt               (was INVASION_budget)
  WA_AI_MILITARY_REGION_SOUTH_AMERICA.txt           (was COUNTRY_SOUTH_AMERICA)
  WA_AI_MILITARY_FACTION_ALLIES_FRONT.txt
  WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt
  WA_AI_MILITARY_FACTION_ALLIES_DIPLOMACY.txt
  WA_AI_MILITARY_FACTION_ALLIES_THEATRE.txt
  WA_AI_MILITARY_FACTION_ALLIES_AIR.txt
  WA_AI_MILITARY_FACTION_AXIS_FRONT.txt
  WA_AI_MILITARY_FACTION_AXIS_DIPLOMACY.txt
  WA_AI_MILITARY_FACTION_COMINTERN_FRONT.txt
  WA_AI_MILITARY_FACTION_CO_PROSPERITY_FRONT.txt
  WA_AI_MILITARY_FACTION_CHINA_FRONT_FRONT.txt
  WA_AI_MILITARY_FACTION_CHINA_FRONT_DIPLOMACY.txt
  WA_AI_MILITARY_COUNTRY_USA_FRONT.txt
  WA_AI_MILITARY_COUNTRY_USA_INVASION.txt
  WA_AI_NAVAL_COUNTRY_USA.txt
  WA_AI_MILITARY_COUNTRY_USA_DIPLOMACY.txt
  WA_AI_MILITARY_COUNTRY_USA_THEATRE.txt
  ...
  WA_AI_MILITARY_COUNTRY_<TAG>_<DOMAIN>.txt         (one file per (country, domain) pair with content)
```

The current set of source files is the input to this layout; see `WA_AI_MILITARY_TYPES_REFERENCE.md` for the per-file inventory.

---

## 8. Phase plan

Phase 1 (this document): documentation and contract only. No script edits.

| Phase | Scope | Behaviour change |
| --- | --- | --- |
| 2 | File renames and domain splits per the target layout. Move country-specific blocks out of faction files. | None intended (pure relocation). |
| 3 | Replace inline `tag = X` lists in faction/region/default files with `WA_AI_CONFIG_MILITARY_*` archetype triggers. Add new triggers as needed. | None intended for in-scope countries; behaviour for newly-covered countries possible. |
| 4 | De-duplicate content across layers using the policy table. Lift shared behaviour up; push country-specific behaviour down. | Possible, controlled by parity tests. |
| 5 | Introduce mutual-exclusion triggers (`WA_AI_MILITARY_country_owns_*`, `WA_AI_MILITARY_faction_owns_*`) for Exclusive types only. | Yes, by design: Country overrides Faction overrides Default for Exclusive keys. |
| 6 | Validation harness: parity tests under `tests/`, optional in-game logging effect that dumps active strategies per AI per tick. | None. |

Each phase is a separate PR. Do not pre-empt later phases inside earlier ones.

---

## 9. Offensive posture system (scripted support layer)

`front_control` execution vs a major enemy is not gated on raw `ai_strategy` triggers but on a weekly
scripted verdict, the **offensive posture** - the answer to "is executing battle plans useful right now,
and against whom?". Rationale: the engine's `alliance_strength_ratio` compares worldwide faction strength,
which permanently disabled the Allied `execute_order` blocks in any late war with a full-strength Axis,
regardless of local superiority (the 1944 France passivity bug).

| Piece | File |
| --- | --- |
| Thresholds and switches (control panel) | `common/scripted_triggers/WA_AI_MILITARY_posture_triggers.txt` |
| Weekly calculus and publication | `common/scripted_effects/WA_AI_MILITARY_posture_effects.txt` |
| Cadence | `on_weekly` in `common/on_actions/WA_AI_misc_on_actions.txt` |
| Consumers (Faction layer) | `WA_AI_MILITARY_ALLIES_exec_vs_germany` / `_grind_vs_germany` and `WA_AI_MILITARY_ALLIES_downfall_push_FRONT` (ALLIES), `WA_AI_MILITARY_AXIS_exec_vs_sov` / `_grind_vs_sov` (AXIS), `WA_AI_MILITARY_CHINA_FRONT_exec_vs_japan` / `_grind_vs_japan` (CHINA_FRONT). **Since Fix 54 the six exec/grind blocks no longer name an enemy tag** — their `enable` reads `WA_AI_MILITARY_posture_has_execute_target` / `_has_grind_target` and their `front_control` targets a `country_trigger` on the per-enemy verdict, so puppets and ahistorical enemies are covered without a tag list. `downfall_push_FRONT` still names JAP: it is a theatre-specific invasion push, not a generic front executor. Their names are now historical; stage 2 collapses the three pairs into one Default-layer pair. |
| Consumers (Country layer) | `WA_AI_MILITARY_SOV_counterattack` (SOV vs GER), `WA_AI_MILITARY_JAP_chinese_war_4` + the posture-0 fallback in `_chinese_war_3` (JAP vs CHI), `WA_AI_MILITARY_ITA_north_africa_offensive_exec_FRONT` (ITA vs the East-Egypt controller, via `WA_AI_MILITARY_north_africa_offensive_viable`) |
| Consumers (Default layer) | `WA_AI_MILITARY_EXEC_low_equipment_hold` |
| Consumers (AIFC) | `WA_AI_AIFC_posture_offensive` reads the `WA_AI_MILITARY_posture` aggregate; `WA_AI_AIFC_posture_defensive` reads the `WA_AI_AIFC_hold_the_line` flag |

Published state per AI country: `WA_AI_MILITARY_posture` (0 = hold, 1 = execute, 2 = attrition grind),
`WA_AI_MILITARY_posture_vs_<TAG>` per major enemy, and the `WA_AI_AIFC_hold_the_line` flag while the hard
brake is engaged (which also drops AIFC into linear defence). Level 1 keys on
`fighting_army_strength_ratio` (the engine's quality-weighted estimate) OR on the front-local branch:
the divisions our side actually has standing on the shared contact line outweigh the enemy divisions
across it by 1.5x to START executing and by 1.1x to KEEP executing once under way (Fix 83, campaign
`af003548`: the single 1.5 bar retracted every western execute order the month Germany reinforced
Normandy 26 → 95 divisions against 121 Allied — 1.27 — with the equipment ratio at 0.93+, and the
unordered beachhead was rolled back 6 → 2 states; the enter/hold pair mirrors Fix 55's equipment
gate) (banded `divisions_in_state` counting, armour double-weighted; skipped when the
pairwise ratio already passes). The local branch is load-bearing - the pairwise ratio compares one
country against the enemy's whole fighting army, so without it no Allied member except the USA ever
passed vs Germany and the coalition never attacked together (July 1944 diagnosis: ENG at level 1 vs
every Axis minor, 0 vs GER/ITA/JAP). It is deliberately local rather than a global force sum: global
counts are quality-blind and mix separate wars (Burma divisions voting on France, Germany's
SOV-facing army inflating the denominator the western Allies face). Level 2 fires when the enemy is at maximum mobilization with a nearly dry manpower pool while our faction
holds a deep reserve - attrition is then profitable even at odds below the level-1 bar, executed
`careful`. The long-orphaned `WA_AI_defensive_front_strategy` low-equipment flag
(`WA_AI_misc_effects.txt`) is the primary hard-brake input and now has a Default-layer `front_control`
consumer.

**This system is the single writer of "we are collapsing" (Fix 43).** Every hard-brake branch pairs lost
ground with a capability term, so the brake releases when the country recovers: the `> 0.2` tier pairs
with equipment-or-manpower, and the near-capitulation `> 0.45` tier pairs with
`WA_AI_MILITARY_army_still_operational` (>40 divisions AND >20 controlled states AND the manpower floor
AND `WA_AI_fielded_eq_ratio` > 0.9 - a four-term conjunction, because equipment alone calls a
fully-equipped 3-division rump operational). Other systems consume the verdict rather than re-deriving
one; AIFC in particular reads the published `WA_AI_AIFC_hold_the_line` flag and the
`WA_AI_MILITARY_posture` aggregate. **Do not gate AI capability on `surrender_progress` anywhere.** It
measures VP loss, so a country with a script-raised capitulation limit occupies any threshold
indefinitely - the USSR held above 0.2 for four game-years in campaign `911bed3c` with 350-400
divisions at full equipment, and every bare threshold it crossed became a permanent lockout.

Two secondary inputs refine the verdicts (constants at the top of the effects file):

- **Casualty exchange rate** - weekly deltas of `casualties_k` (own, and per enemy against baselines
  stored on the observer: `WA_AI_MILITARY_cas_prev` / `_cas_prev_<TAG>`). A measured favourable
  exchange substitutes for the dry-pool test and unlocks level 2; an unfavourable one vetoes level 2.
  Quiet fronts, first observations, and stale baselines produce no signal. Baselines persist across
  peace deliberately (`casualties_k` is monotonic).
- **Air superiority** - per-enemy sizes from `WA_AI_calc_air_force_sizes` vs own planes + fighter
  stockpile. Clear superiority lowers the level-1 bar to the hollow bar; clear inferiority vetoes
  level 1. The grind is exempt from the air veto (infantry attrition works without the sky).

Not every `execute_order = yes` is posture-gated, by design. Scripted historical war openings
(Barbarossa 1941-42, Japan's 1937-40 China pushes, the southern-expansion timetable), pushes against
minor enemies (posture publishes no verdict for them), home-territory defence
(`WA_AI_MILITARY_JAP_operation_downfall`), island-hopping onto lightly-held states, and the
flag-coordinated `WA_AI_MILITARY_SOV_coordinate_offensive` all stay unconditional - the posture
calculus would either stall them at war start (no engaged armies yet, so
`fighting_army_strength_ratio` reads near zero) or add nothing.

Authoring rule: a new `execute_order = yes` block against a major enemy should gate on
`check_variable = { WA_AI_MILITARY_posture_vs_<TAG> = <level> }` (plus `has_war_with` - per-enemy posture
variables linger after a peace) rather than re-deriving strength conditions inline. Pair level 1 with
`execution_type = balanced` and level 2 with `execution_type = careful` + `manual_attack = yes`, as the
existing Faction-layer pairs do.

---

## 10. Scripted-landing invasion freeze (scripted support layer)

When a country **executes** a WA-scripted amphibious landing, AI-planned naval invasions are suppressed
across that country's whole faction for 90 days, so the scripted operation is not diluted by the engine
opening a competing beachhead at the same time.

| Piece | File |
| --- | --- |
| Switches, window length, macro-theatre definitions (control panel) | `common/scripted_triggers/WA_AI_LANDING_triggers.txt` |
| Marker (stamps the freeze faction-wide) | `common/scripted_effects/WA_AI_LANDING_effects.txt` |
| Call site | `common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt`, inside `WA_AI_DIVISION_spawn_invasion` |
| Consumers (Default layer) | `common/ai_strategy/WA_AI_MILITARY_DEFAULT_INVASION_landing_freeze.txt` |
| Probe | checklist R44, `WA_TLM_r44_freeze_*` (telemetry doc §5) |

**The marker is generic, and that is the whole point.** All ~90 scripted operations in
`events/WA_AI_invasions.txt` - Weserübung, Beowulf, Mercury, the entire Japanese Pacific opening, Torch,
Husky, Avalanche, Shingle, Neptune/D-Day, Dragoon, Watchtower, Downfall - execute through the single
scripted effect `WA_AI_DIVISION_spawn_invasion`, so the freeze is stamped once, there, with no
per-operation wiring and no reference to a date or a country tag. A rule keyed on D-Day specifically would
be exactly the historical-path-only behaviour `AGENTS.md` design principle 1 forbids.

**Execution, not enablement.** An `ai_strategy` block cannot set a flag, and a landing's `enable` turning
true is not the same event as a landing happening - every operation re-fires itself every 7 days until its
preconditions hold, so "enabled" is true for months before anything lands. `spawn_invasion` is the only
place that knows divisions have actually been created on an enemy beach. The call sits inside that
effect's existing `has_relation_modifier` guard, which collapses a multi-wave operation into one stamp per
(invader, target, 14 days).

**The suppression lever is `invasion_unit_request`, and the choice is forced.** Of the three
INVASION-domain types, `naval_invasion_focus` is a boolean priority rather than a brake; `invade` is keyed
per target country, which cannot express "not in this theatre" (Germany and Japan each span several
theatres, so an `invade` freeze is either an enumeration that goes stale or a blanket); and
`invasion_unit_request` is the only one accepting a geographic scope (`documentation.info section front_unit_request / invasion_unit_request` -
`tag` / `state` / `strategic_region` / `area` / `country_trigger` / `state_trigger`, tested against the
invasion **target**) and the only one that throttles what an invasion order may request rather than which
country looks attractive. `state_trigger` acceptance on this type is established in-repo -
`WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt:442`.

**Value is -200, deliberately.** The engine says only that the value "will be added as a factor over
regular requests" (`documentation.info` section `front_unit_request`) - **it states no base**, so "-200
floors the request at zero" is ASSUMED, not measured (the base-of-100 wording came from the unrelated
`unit_ratio` section). On that assumption -200 floors the
request at zero - the same magnitude `WA_AI_MILITARY_INV_freeze_when_home_threatened` uses for the same
job. Staying at -200 rather than -2000 is load-bearing: `WA_AI_MILITARY_ALLIES_dday_prep_INVASION` puts
+1000 on states 15 and 1016 while it assembles Normandy, and Anzio (1944.1.21, europe) lands inside that
prep window. At -200 the boosted beach still nets +800; a -2000 blanket would flatten a deliberate
Faction-layer plan. **A scripted operation that names its own beach must outrank a generic brake.**

**Theatre-scoped by default, blanket one switch away.** The freeze is split into two macro-theatres by the
landing state's continent (WEST = europe + africa + middle_east, EAST = asia + australia; the Americas
deliberately map to neither). `is_on_continent` rather than strategic regions, because WA replaces the
whole region table and region ids are a documented source of wrong claims. Setting
`WA_AI_LANDING_freeze_is_faction_wide` to `always = yes` gives the literal faction-wide form and switches
the two theatre blocks off, so the modes never stack.

The measurement behind that default: `WA_KDE_AI_effects.txt` schedules **17 USA scripted landings in 1944
alone** plus 9 in 1945, and the largest gap between two consecutive Allied landings in 1944 is **89 days**.
A 90-day blanket freeze would therefore hold the Allied faction frozen **continuously from 1944.1.21 into
1946** - a two-year lockout on AI invasion planning, not an occasional stall. Splitting by theatre is what
keeps D-Day from freezing the Pacific.

**Superseded on the same change:** `AI_naval_invasion_fix` in `common/decisions/z_WA_ai_fixes.txt` - a
USA/ENG-only, 1944.2.1-1944.3.15 hard-dated decision whose payload `naval_invasion_capacity = -50` its
author believed dead. It is not dead (the modifier is live in 1.18.0), which means it had been zeroing
both countries' invasion capacity - Pacific included - for ~40 days every campaign. Removed; the removal
comment in that file carries the full reasoning and the behaviour delta.

---

## 11. Italian theatre - geography-gated home defence and ally guard (Fix 96, 2026-08-17)

Campaign `0edbc955` (Oct-Dec 1943): mainland Italy fell to 7-12 Allied divisions because 0-3 Italian and 0-2 German
divisions stood on it. Every rule of the theatre keyed on a tag, a date or an event - the ITA/ITL Libyan controller lists,
`date > 1937/1938`, `tag = RIT` always-on, `has_war_with = ITA`, `is_in_faction_with = ITA`, `country_exists = RIT`, and
Germany's `GER_fall_achse_prepared` flag (stamped 60 days after `ita_armor.893`, i.e. after the fall) - and none asked the only
question that generalises: **who owns this soil, and is an enemy standing on it?**

| Piece | File |
| --- | --- |
| Tag-free triggers (control panel) | `WA_AI_MILITARY_triggers.txt`: `WA_AI_MILITARY_is_italian_homeland_power` (owns AND cores any of the 15 mainland + Sicily states - Sicily/south included because the Fall Achse transfer can leave the co-belligerent ITA owning nothing north of Naples), `_italy_homeland_invaded`, `_italy_home_threatened` (invaded, or owned island / Adriatic-gate ground enemy-held - Sardinia, Corsica, Dodecanese, Istria, Primorska; not Albania/Zadar - or both shores of the Sicilian strait enemy-held: Tunisia 458+1061 AND Malta 116; never a lone pre-war holding), `_ally_italy_at_war` / `_theatre_threatened` / `_invaded` (walk `any_allied_country` AND `any_subject_country` - the RSI is a German subject, never a faction member), `_allied_with_` / `_at_war_with_italian_homeland_power`, `_libya_bridgehead_held` (own / subject port; an ally's port only while an enemy holds East Egypt or Tunisia - so ENG's Libya is not the co-belligerent's bridgehead), `_ethiopian_war_finished` (no Italy is in a colonial ETH war fought against no major; evaluated over `any_country` so allies read the same answer) - **Fix 108 (2026-08-19)** moved the three `war_against_ENG` blocks (FRONT `garrison = -5000`, DIPLOMACY `force_defend_ally_borders`, NAVAL air weights) onto it: they were gated on `NOT = { has_war_with = ETH }`, which a liberated co-belligerent Ethiopia holds false forever |
| Owner (Region layer, whichever tag is an Italy: ITA on either side of its flip, RIT, a civil-war Italy) | `WA_AI_MILITARY_REGION_ITALY_THEATRE.txt` (floor / threatened buffers + `area_priority`; **Fix 111 (2026-08-19)** added `order_id = 9615`, state 1 Corsica, ratio 0.03 to the floor tier - the belt island `_italy_home_threatened` reacts to losing while no buffer had ever placed a division on it, covered only by an engine area-defence order that Fix 108 removes), `WA_AI_MILITARY_REGION_ITALY_FRONT.txt` (`front_unit_request` +200 on 238/23/21 and careful `front_control` while invaded). Replaces `COUNTRY_RIT_FRONT` (deleted). Gates live in `enable`, never `allowed` - `allowed` is evaluated at country creation, before a released RIT owns anything |
| ITA periphery (Country layer) | `WA_AI_MILITARY_COUNTRY_ITA_THEATRE.txt`: independent rear-area buffers for Southern France and all seven Greek 1936 states plus Dodecanese (0.15). **Fix 110 (2026-08-19) split Southern France in two:** the Mediterranean shore {21 Provence, 22 Languedoc, 735 French Alpes} keeps `order_id = 9610` at 0.08 and no longer yields to a front (it is the anti-landing reserve), the six inland states move to `order_id = 9614` at 0.03 and keep the yielding semantics - the flat nine-state list put six divisions on five inland states and none in Provence on campaign 07270b64. **Fix 109 (2026-08-19)** added `order_id = 9613`, ratio 0.06, over the eastern Adriatic shore {736 Istria, 886 Primorska, 1022 Gorski Kotar, 163 Zadar, 908 Split} under the SAME Otranto gate as Albania, `subtract_fronts_from_need = no`; all five sit in strategic region 24, already inside `area = central_balkans`, so no ai_area was minted (the 72-definition budget is full). Albania has its own 0.10 buffer only while `WA_AI_MILITARY_otranto_closed_to_our_enemies` is false; that trigger tests Otranto's exact required provinces (11998 in Calabria / 11767 in Albania), rejects the `contested` case where their controllers fight each other, then requires for every Italian enemy that one controller is at war with it. This mirrors the adjacency rule: contested Otranto permits naval access, while an uncontested hostile side controller denies it. If a land front opens in one of these areas, its demand replaces rather than stacks with the rear reserve (`subtract_fronts_from_need = yes`). Cross-block `order_id` arbitration remains **ASSUMED**; the three sectors use distinct ids and are sized independently. |
| Owner's Africa effort (Country ITA) | `WA_AI_MILITARY_COUNTRY_ITA_THEATRE.txt`: one +200 while a Libyan port is held and home is safe, +50 when threatened, -200 when no port is held or the mainland is invaded (three stacked +200s and the "all four Libyan states lost" switch are gone); the R13 pair aborts on the geographic threat instead of `surrender_progress` |
| Ally guard (Faction AXIS) | `WA_AI_MILITARY_FACTION_AXIS_THEATRE.txt` `AXIS_italy_theatre_guard_THEATRE` / `_invaded_THEATRE` (0.06 / 0.12 buffers on the 15 states, own order_id, `subtract_fronts_from_need = no`), `WA_AI_MILITARY_FACTION_AXIS_FRONT.txt` `AXIS_italy_theatre_guard_FRONT` (+150) and `AXIS_hold_italy_after_defection_FRONT` (at war with an Italy). Replaces GER `fall_achse_a/b/c`, `protect_our_weak_underbelly`, `frontline_requests_6` (deleted); the Fall Achse political chain is untouched |
| Allied side | `avoid_italy_overstack(_after_flip)`, `italy_cobelligerent_support_FRONT`, `ENG_war_against_ITA_3_DIPLOMACY` (gated `ally_italy_at_war` - the commitment starts the day the co-belligerent fights, not at the first lost state), `USA_sicily_push`, `ALLIES_sicily_push_FRONT` re-gated on the same triggers; the date-boxed Husky family is out of scope |
| Probe | checklist R61, `WA_TLM_r96_italy_*` (telemetry doc 5) |

**Never gate an Italy rule on `tag = ITA/RIT`, `has_war_with = ITA` or `is_controlled_by = ITL`**:
the 1943 flip keeps the ITA tag, RIT is a released tag, and ITL is annexed the same tick.

**All triggers are PREV-relative from the state scope, not ROOT-relative**, because `_ally_italy_theatre_*` evaluate them inside `any_allied_country` / `any_subject_country` from another country's scope. The AXIS guard tiers exclude the `at_war_with_italian_homeland_power` case (the `hold_italy_after_defection` block owns it) so the two never stack. Post-code review 2026-08-17 (8 angles) found and fixed: 10-anchor set, ally-port bridgehead, subject RSI, flip window, peace-time floor, invasion-veto gates, Albania belt, Tunisia heuristic, ETH reader relativity. Every state list must match `WA_AI_MILITARY_AIR_theatre_contested_italy` (mainland 10 + Sicily 5). Ratios per state group: owner 0.10 / 0.20 (Sicily/south), 0.15 / 0.10 (mainland anchors), plus the ally's 0.06 or 0.12 - two armies, two pools. **They do not sum.** `put_unit_buffers` ratios are fractions of the country's whole army, and blocks sharing an `order_id` share one ratio (§4 note); the two Axis ally-guard blocks both carry `order_id = 9606` (`WA_AI_MILITARY_FACTION_AXIS_THEATRE.txt`). They are mutually exclusive by gate, so the live effect is unchanged - the arithmetic in the earlier wording was not the engine's.

---

## 12. East Africa - a theatre, not a sink (Fix 97, 2026-08-17)

Campaign `0edbc955`: Italy lost the 1936 Ethiopian war, ITS never existed, and every East-Africa rule on both sides
keyed on `country_exists = ITS` / `tag = ITS` / a date - none fired. Region 17 (Eritrea/Ethiopia/Somalias) sat inside
`WA_AI_MILITARY_sink_africa_regions`, so ENG netted about -200 there against one +100 diluted over `central_africa`;
regions 380 (Sudan-South/Darfur) and 381 (Kenya/Uganda/Tanganyika) belonged to no ai_area at all. Italy parked 39/61
divisions in the AOI in 1940 (engine border-threat reflex against a neutral 40-division Ethiopia) and camped inside the
Sudan/Kenya out of supply for three years; the Allies never fielded more than one 4-6-division army per axis.

| Piece | File |
| --- | --- |
| Areas | `common/ai_areas/WA_AI_MILITARY_areas.txt`: `WA_AI_MILITARY_east_africa_regions` {17,217,380,381} (theatre pulls / brakes / contested area_priority), `_east_africa_corridor_regions` {380,381} (baseline-bearing subset - 17/217 already carry the central_africa baseline), sink alias without 17 (header sentence records why) |
| Triggers | `WA_AI_MILITARY_triggers.txt`: `WA_AI_MILITARY_AIR_theatre_contested_east_africa` (+ `_theatre_state_`), `_east_africa_theatre_contested`, `_east_africa_enemy_held` (AOI core), `_holds_east_africa_colony` (self / subject / ally-Italy owns-or-controls 550 or 559 - PREV-relative), `_east_africa_offensive_viable` (the north_africa pattern) |
| Allied side | `WA_AI_MILITARY_ALLIES_east_africa_contested_FRONT` (+150) / `_THEATRE` (+100, parity with the Commonwealth north_africa support) / `_exec_FRONT` (posture-gated; anchors = the colonial coast 550/559/268/269, minor bar > 4 states as in the posture calculus) - Faction, every Allies member; replaces the ITS/date `war_against_ITA_central_africa` family and the SAF/RAJ Country execs; RAJ keeps an "Asia first" -100 and an ITS-forced `conquer` block; ENG `africa_war_1` -50 (user decision), `africa_war_no_RAJ_*` deleted, `africa_war_2_*` DELETED (its `OR{...} AND NOT{...}` gate was X AND NOT X since the first authoring - never live; reviving it would triple-stack +200 north_africa) |
| Default | baseline +100 / non-African -90 on the corridor alias; the sinks that mean "stay out" (CAPS x3, COMINTERN x2, CO_PROSPERITY x2, AXIS minors) name the theatre alias explicitly; `naval_majors_global_balance`, `european_continental_majors_focus_landfronts`, `minors_home_first` and the `CORE_secondary_sink` caps do not (they also match ENG / SAF / RAJ - the countries the theatre is fought by); the `italy_ethiopian_war_active` exemption on the two CORE caps was removed with its reason |
| Axis side | `AXIS_abandon_east_africa_*` gated `holds_east_africa_colony`, aimed at the theatre alias; ITA `east_africa_garrison_THEATRE` (0.10 on 550/559, buffer `area` = `WA_AI_MILITARY_east_africa_colony_regions` {17} - put_unit_buffers `area` names the orders that MAY DRAW on the buffer, so the Sudan offensive in 217 may not) and `ignore_neutral_ethiopia_DIPLOMACY/_FRONT` |
| Probe | none. Checklist R62 was retired early by owner decision (1 of 3) and its `WA_TLM_r97_ea_*` family was deleted with it on 2026-08-18. Re-instrument before scoring this theatre again. |

`NOT = { A B C }` is a **NOR** in PDXScript (see the lessons log) - the `africa_war_2` gate had been `OR{A B C} AND NOT{A B C ...}` since its first authoring. Post-code review (2 angles) fixed: minors/continental archetypes not re-adding the alias, the viable trigger's anchors and bar, THEATRE +100, RAJ conquer split, the buffer's `area`.

**Engine limit found by the owed boot test (2026-08-17, HOI4 1.19.2):** the effective global `ai_area` ceiling is 72 definitions. `default.txt` defines 67; the parent plus 4 WA aliases (71) booted, either new Fix 97 alias alone (72) booted, and both together (73) crashed with C0000005 in `ai_area.cpp` while strategy data loaded. Renaming the sixth alias, changing its regions, making them disjoint and disabling its readers did not change the result. Remediation: remove the unreferenced India alias; replace the custom Italy alias with the default `italy` area, which has the same {21,23} membership; replace the former Southeast-Asia sink area with `WA_AI_MILITARY_is_southeast_asia_sink_state` in its nine `front_unit_request` readers; spend that slot on the two-reader corridor baseline alias. Current `WA_AI_MILITARY_areas.txt` still has 5 definitions (72 total). This exact composition passed AI-strategy and on-action loading with no related `error.log` entry or crash report. It preserves the independently addressable four-region theatre, corridor baseline and colony buffer. `tests/wa_ai_military_strict_parity.txt` encodes the state-scope assertion for one state in each of regions 142/167/196/260/340 plus a Northern-France rejection; the bundle still needs an in-game test run, and campaign R62 owns the remaining area-vs-state-trigger aggregation risk. Re-test the 72/73 boundary after engine upgrades.

---

**Fix 132 (2026-08-21, campaign `8c0fea4c`, checklist R93) - occupying the AOI is not expelling the
colonial power.**

`WA_AI_MILITARY_east_africa_theatre_contested` was a one-line alias of
`WA_AI_MILITARY_AIR_theatre_contested_east_africa`, whose enemy limb is
`<state> = { CONTROLLER = { has_war_with = ROOT } }`. MEASURED on `8c0fea4c`: at **1941.4.28** every AOI
core state was held by ENG or ETH, so the verdict read FALSE and the whole Fix 97 Allied family fell on
`abort_when_not_enabled` that day - while ITS still existed, was still at war, and still **OWNED** 550
Eritrea and 559 Italian Somaliland. The Allies had 11 divisions in the theatre, five of them RAJ with no
order at all. **Four weeks later Italy held 12 divisions in 559, nine of them on a front order**, and the
state was Italian again; it took until September to undo.

The trigger now reads:

```
WA_AI_MILITARY_east_africa_theatre_contested = {
    OR = {
        WA_AI_MILITARY_AIR_theatre_contested_east_africa = yes
        AND = {
            WA_AI_MILITARY_east_africa_not_pacified = yes    # enemy HOLDS ... or still OWNS
            WA_AI_MILITARY_east_africa_side_present = yes    # and we stand there
        }
    }
}
```

`WA_AI_MILITARY_east_africa_not_pacified` is the existing enemy-holds test OR
`<550 559 268 269 271 909 910> = { OWNER = { has_war_with = ROOT } }`. `OWNER` is a state-scope target
documented in the 1.19.2 install (`documentation/effects_documentation.md`, "Supported Targets: THIS,
ROOT, PREV, FROM, OWNER, CONTROLLER, OCCUPIED, CAPITAL") and already used elsewhere in the mod.

**Two triggers deliberately NOT widened.** `WA_AI_MILITARY_AIR_theatre_contested_east_africa` itself is
also read by `WA_AI_build_theatre_air_bases`, and widening it there would keep building East-African
airfields after the campaign is won. `WA_AI_MILITARY_ethiopian_war_finished` gates RAJ's Kuwait guard
and Italy's `protect_periphery` blocks and answers a different question - has the colonial WAR ended,
not has the colonial POWER been expelled.

**Consumers, all Allied-side** (grep, 2026-08-21): `WA_AI_MILITARY_ENG_east_africa_delegated_FRONT`,
`WA_AI_MILITARY_ALLIES_east_africa_contested_FRONT` / `_exec_FRONT`,
`WA_AI_MILITARY_ALLIES_east_africa_contested_THEATRE`, `WA_AI_MILITARY_RAJ_kill_ITS_DIPLOMACY`,
`WA_AI_MILITARY_RAJ_east_africa_available`, and `WA_TLM_core` (write-only). The widening therefore moves
exactly one side's behaviour, which is the intent. R93 has a mandatory RELEASE leg for the same reason:
a gate that never lets go is not a fix.

## 13. The 1936 Ethiopian war - AI Italy attacks the mission's states, on every aggressive rule (Fix 98, 2026-08-17)

Campaign `0edbc955`: Italy lost the war by the `ETH_push_into_ethiopia_mission` timeout (100 days from 1936.5.1; success =
control of BOTH 910 Amhara AND 909 Somali) while winning 17:1 - the AIFC sector anchored on Addis (271) and drained the
Somali armies toward Oromia. The only execute block (`crush_ethiopia_1`) was `date < 1937.1.1` + rule ∈ {DEFAULT,
FASCIST_HISTORICAL}: FASCIST_ALTERNATE / RANDOM had no execute vs Ethiopia before 1937, nobody after 1938.

| Piece | File |
| --- | --- |
| Rush for the whole war on every rule except DEMOCRATIC / MONARCHIST | `WA_AI_MILITARY_COUNTRY_ITA_{FRONT,THEATRE,DIPLOMACY}.txt` `crush_ethiopia_1_*` (crush_ethiopia_2 merged) |
| Objective steering | `WA_AI_MILITARY_ITA_ethiopia_mission_objectives_FRONT` - `# aifc-tuning:` `force_concentration_target_weight` 909/910 +80, 271 -60, `front_unit_request state = 909/910` +50, while either mission state is still Ethiopian. Steering *where* the AI attacks is AIFC's job (ECONOMY rule 6); `front_control state =` only selects which orders a mode applies to and would have been a no-op |
| DEM/MON slow path | unchanged except the 16-17 May hole (`end_the_struggle` `date > 1936.05.15`) |
| Not touched (user decisions) | the mission timers / ETH acceptance / dead BBA events; supply ideas or cheats |
| Probe | checklist R63, `WA_TLM_r98_eth_both_*` |

Open item found on the way: on `0edbc955` every `wa_ai_aifc_*_ref` array (GER, SOV, ENG, ITA) reads `-10737.4x`, an unresolved
token, so the DEFAULT aifc block's `state_trigger is_in_array = { FROM.FROM.WA_AI_AIFC_sector_*_ref = THIS.id }` pairs may
have been inert campaign-wide - the sector was computed, the engine-side weighting may not have followed. Separate diagnosis.
**A route that avoids the question entirely:** both `force_concentration_front_factor` and
`force_concentration_target_weight` document `tag` / `state` / `strategic_region` / `area` /
`country_trigger` alongside `state_trigger` (`documentation.info` sections for the two types). The
encoded `*_ref` array is a workaround for a targeting limitation these types do not have. Whatever the
diagnosis concludes, a `country_trigger` route needs no scope reference to resolve.

---

## 14. The Axis Tunis bridge - garrison a Tunisian port when an enemy lands behind the African front (Fix 99, 2026-08-17)

Campaign `0edbc955` (Nov 1942 - Jun 1943): Torch landed 1942.11.8, Case Anton handed Tunisia 458/1061/665 to Germany within
days, and not one German division ever stood in Africa (252-263 divisions, 0 in Africa/Sicily in every save); a French division
walked into Tunis ~5 weeks later. No Axis block named a Tunisian state as a destination, no Axis trigger read Algeria (only the AIR
contest trigger did), Germany's post-Barbarossa net on the 7-region `north_africa` blob was area +20 / `front_unit_request` -175
(`war_with_soviets_2` -75, `africa_is_lost` -100 on a `date > 1942.10.1` + Suez calendar), and `libya_bridgehead_held` had no
Tunisian term, so a Tunis-only foothold read "no bridgehead" and armed Italy's -200 abandon.

| Piece | File |
| --- | --- |
| Triggers (control panel, PREV-relative) | `WA_AI_MILITARY_triggers.txt` Fix 99 section: `WA_AI_MILITARY_tunis_bridge_held` (own side controls 458 or 1061), `_maghreb_enemy_landed` (enemy controls an Algerian/Moroccan anchor - the AIR contest lists), `_tunis_bridge_contested` (at war ∧ held ∧ landed - THE gate), `_african_shore_port_held` (Libyan four + Tunis + Bizerte; sibling of `libya_bridgehead_held`, which stays the gate of everything that needs LIBYAN ground). One "our side": self / subject / faction ally / `has_war_together_with` - the last term makes a subject of an ally (ITL) count |
| Area | `WA_AI_MILITARY_areas.txt` `WA_AI_MILITARY_tunisia_regions` {329} - the buffer's `area` (orders that may draw on it) and the pull's key |
| Faction AXIS | `WA_AI_MILITARY_FACTION_AXIS_THEATRE.txt` `AXIS_tunis_bridge_THEATRE` (`put_unit_buffers` 458/1061/665, ratio 0.05 ≈ 13 divisions on the 1942 Heer = 5th Panzer Army, order_id 9608, `subtract_fronts_from_need = no`), `WA_AI_MILITARY_FACTION_AXIS_FRONT.txt` `AXIS_tunis_bridge_FRONT` (`front_unit_request strategic_region = 329` +200 - offsets the blob's -175 on the Tunisian front only). Gate: `is_axis_member` ∧ `can_open_secondary_fronts` ∧ NOT `home_threatened` ∧ NOT `italy_homeland_invaded` ∧ `tunis_bridge_contested`; releases when Tunis and Bizerte are lost or the Maghreb is cleared |
| Country ITA | `africa_pull` / `_reduced` / `abandon_north_africa` re-pointed to `african_shore_port_held` (+ 459/460 in the pull's enemy list); `protect_libya`, the R13 pair, the NAVAL air weights and `ita_armor.915` deliberately KEPT on `libya_bridgehead_held` (they need Libyan ground) |
| Country GER | `africa_is_lost_FRONT` / `_DIPLOMACY` re-gated `has_war ∧ NOT african_shore_port_held` (was the vanilla-inherited post-El-Alamein calendar; historical walk in the block header: arms 1939.9 inert, releases 1940.6, held through Torch, arms when Tunis + Libya are gone). `GER_focus_on_north_africa_*` (`NOT has_war_with = SOV`) untouched by decision; `GER_ignore_invading_these_countries_FRONT` (no Axis invasion order into north_africa) untouched - the bridge is held by sea-lift into an own port, not re-conquered |
| Probe | checklist R64, `WA_TLM_r99_tunis_*` (v23) |

Bounded claim (t0 Torch+Anton day 0-5 trigger true / t1 day 7-14 assignment + embarkation / t2 day 21-35 garrison before the ~day-35-50
walk-in): t1 is a hypothesis about the engine's sea-lift cadence whose only precedent is ENG's Egypt/Malta buffers under naval supremacy -
R64 leg 1 is its falsifier. Residual: an enemy-controlled strait leaves the buffer unfilled; nothing re-conquers a lost Tunis. Two engine
assumptions: the custom ai_area in `put_unit_buffers` `area` passed AI-strategy/on-action loading in the 2026-08-17 F9 boot;
campaign R64 must still prove that the buffer draws correctly and that a region-keyed `front_unit_request` sums with an area-keyed
one on the same front. Rejected alternative, recorded: a scripted Axis spawn into Tunis mirroring Torch (Option Q of the
design note) - historical-mode-only behaviour and a divisions-from-nothing spawn on the Axis side; kept behind a campaign result.

---

**Fix 133 (2026-08-21, campaign `8c0fea4c`, checklist R94) - the bridge on an ALLY's ground, and the
Italian tier.**

MEASURED at 1942.11.21: Tunis 458, Bizerte 1061 and Gabes 665 all read owner GER, controller GER. Italy
fielded **107 divisions** and had **one** in Tunisia, on a buffer order; `plans.py ITA --fronts` returns
only Army 14 and Army 15, both on Marsa Matruh / the Libyan plateau, and **no order of any kind touches
Tunisia**. Germany had none in Africa at all. By 1943.3.22 all three states read controller FRA.

The gate was never the problem - `WA_AI_MILITARY_tunis_bridge_contested` was TRUE on that save (458 held
by GER, in faction with ITA; 459/460 held by FRA, at war with ITA since 1940.6.11). **The FRONT half was
inert.** `front_unit_request strategic_region = 329` sizes an EXISTING front, and on an ally's ground
Italy has no border with the enemy inside region 329, so the +200 weights nothing. Same class as the
inert `front_armor_score id = "ITL"` that Fix 119 deleted from the German file.

Two changes:

| Piece | What |
| --- | --- |
| `WA_AI_MILITARY_AXIS_tunis_bridge_defend_ally_DIPLOMACY` (new, `WA_AI_MILITARY_FACTION_AXIS_DIPLOMACY.txt`) | `force_defend_ally_borders target = WA_AI_MILITARY_tunisia_regions value = 200`, on the bridge gate plus "458 and 1061 are NOT ours or a subject's". The type whose documented job is a per-ally umbrella commitment rather than a front sizing. |
| `_tunis_bridge_THEATRE` split into `_italy_THEATRE` (0.15, order_id 9619) and `_other_THEATRE` (0.05, order_id 9608) | Gate-exclusive on `WA_AI_MILITARY_is_italian_homeland_power`. 0.05 was sized on the 260-division Heer; on Italy the same number asked for 5 and delivered 1. 0.15 x 107 is ~16, still under the 0.25 Italy reserves for Libya itself. |

`WA_AI_MILITARY_tunisia_regions` is an EXISTING alias and must stay one: the engine takes at most **72**
`ai_area` definitions across the replaced folder and WA sits at exactly 72 - the 73rd crashed with
`C0000005` in `ai_area.cpp`, boot-tested (see the header of `common/ai_areas/WA_AI_MILITARY_areas.txt`).

**Deliberately NOT added: a `front_control` executor on region 329.**
`WA_AI_MILITARY_ITA_north_africa_offensive_exec_FRONT` already writes `ordertype = front` on
`area = north_africa`, which CONTAINS region 329; a second writer on overlapping ground breaks the
per-area+ordertype exclusivity policy of section 4. If the DIPLOMACY writer works, the existing executor
runs the front; if it does not, a second executor would not have helped.

**ASSUMED, and it is the one unverified term of the fix:** that `force_defend_ally_borders` on an area
makes the front allocator adopt an ally's border inside it. The 1.19.2 install documents no
`force_defend_ally_borders` section at all; the reading comes from vanilla usage and from
`WA_AI_MILITARY_TYPES_REFERENCE.md`. R94 leg 1 is its falsifier, and the recorded next lever if it fails
is a heavier `put_unit_buffers` - the only type whose effect is measured in this repo.

## 15. Faction theatres - WA owns them now (2026-08-18)

`common/ai_faction_theaters` defines the engine's theatres: a named list of strategic regions,
an `ai_will_do` that decides how likely a faction member is to take it, and a `cancel` that makes
it abandon one. **WA did not replace the folder, so vanilla's file ran in every campaign.**

### Why that was not harmless

WA re-cut the strategic-region map - **383 regions against vanilla's 304** - and **reused ids for
different ground**. Vanilla region 239 is Alborz in Iran; WA region 239 is Northern France. Measured
2026-08-18 over the 223 region ids vanilla's 30 theatres name:

| Compared to what vanilla meant | Ids |
| --- | --- |
| identical province set | 14 |
| mostly the same | 76 |
| mostly different | 59 |
| **completely disjoint - the id was repurposed** | **74** |

Province ids themselves are stable (WA keeps all 13,414 vanilla provinces and adds 1,111), so the
damage is entirely in the region layer.

The engine resolves `theatre_distribution_demand_increase id = <state>` to "the theatre containing
that state" through the **live** region map, so the mismatch reached behaviour. WA's six writers of
that type, before and after:

| Writer | State | WA region | Theatre BEFORE | Theatre AFTER |
| --- | --- | --- | --- | --- |
| `CAN_theatre_boost_europe` | 15 Lower Normandy | 239 Northern France | `middle_east` / `persia` | `western_europe` |
| `JAP_theatre_boost_home` | 533 Tohoku | 377 N. Home Islands | none - inert | `japanese_home_islands` |
| `SOV_theatre_boost_finland` | 146 Viipurin Karjala | 326 S. Karelia | none - inert | `barbarossa_north` |
| `USA_theatre_boost_pacific` | 629 Hawaii | 349 Hawaii | none - inert | `central_pacific` / `us_west_coast` |
| `ENG` | 126 North London | 1 S. England | `western_europe` | unchanged |
| `ALLIES` | 447 Alexandria | 128 Egypt | `north_africa` (+`_uk`) | unchanged |

Two of six worked. **The resolution chain is DERIVED** - state to region to theatre is the only
mapping the engine documents, but nobody has watched the engine do it. The falsifier is a campaign
reading; until then treat the AFTER column as the intended target, not a measured one.

### What WA generates and what it does not

`tools/gen_ai_faction_theaters.py` writes `common/ai_faction_theaters/ai_faction_theaters.txt`.
Every theatre's `name`, `ai_will_do`, `cancel`, `preferred_countries` and `can_skip_first_region`
are **vanilla's, verbatim** - only `regions = { }` is computed, as the WA regions covering the
province area the vanilla list covered (threshold: half the WA region's provinces inside it).
Result: 272 of WA's 383 regions now sit in a theatre, against 223 of 304 for vanilla.

Two rules the generator encodes, both engine facts:

- **The first region is a gate.** The engine will not create a theatre until its first region is
  available, unless `can_skip_first_region = yes`. The regions covering vanilla's anchor are emitted
  first, and the best cover of the anchor is force-included even below threshold - WA cut region 139
  South Africa wider than vanilla's, putting it at 0.47, and dropping it would have decapitated that
  theatre.
- **The area must be connected.** Measured on `map/provinces.bmp` directly, because the generated
  `WA_AI_MAP_province_connections` effect is a LAND pathfinding graph with no sea province in it and
  theatres mix land and sea. Detached regions are dropped unless vanilla named them too: vanilla's
  own regions carry stray high-id provinces (its `163-Amazonian Brazil` owns province 13353, the
  Scheldt in Belgium), which WA re-homed into 1-2 province regions, so one shared province scores a
  100% overlap and would drop Lake Ladoga into the Brazil theatre. Positive control: 29 of vanilla's
  30 theatres pass this test on the vanilla map - `north_sea_region` (Ireland) is the one that does
  not, and WA keeps that split rather than inventing a fix vanilla never had.

**Do not hand-edit the generated file.** Change the generator and re-run it from `tools/`.

### Nothing in a savegame can verify this (measured 2026-08-18 on `0bbc1f60`)

The before/after table above is **DERIVED**, and it has to stay that way: a save does not expose
faction theatres at all. Three readings, all from the same 1946.5 save:

| What the save holds | Reading |
| --- | --- |
| `theatres={ theatre={ id area={...} orders_group={...} } }` | **98 theatres, 98 areas** captured by a brace-matched walk. Area sizes: min 1, median 31, **max 140 provinces**. A WA faction theatre spans 5-23 strategic regions, i.e. many hundreds of provinces. These are army-side operational areas - each one carries the `orders_group` blocks of the armies working it. |
| `theater_group={ name="..." }` | **133 groups, 64 distinct names**: Europe 19, Asia 10, South America 10, Middle East 6, Africa 5, then auto-generated "British Theater 1", "Swedish Theater 1"... Continents and nationalities. **Not one matches an `ai_faction_theater_id`.** |
| the theatre ids themselves | `japanese_home_islands`, `north_africa_uk`, `central_pacific`: **zero occurrences**. The strings never reach the save. |

So the falsifier this section used to carry - "a campaign save shows the six theatres exist and carry
the extra demand" - **is not executable, and no rewrite of it is**. The indirect route is worse: the
remap's effect is extra unit demand on a theatre's fronts, which is confounded by every other demand
term in the engine.

**What IS verifiable, and was:** the file parses and its region ids resolve. HOI4 logs a complaint
for a malformed theatre or an unknown region, and `0bbc1f60`'s boot produced **zero** mentions of
`ai_faction_theaters` in `error.log`. That establishes the file is live and well-formed - not that
the mapping is right.

**Correctness of the mapping is a build-time property, not a runtime one**, and that is where it is
checked: `gen_ai_faction_theaters.py` verifies connectivity on the real province bitmap, force-includes
each theatre's anchor, and is positive-controlled against vanilla's own 30 theatres on the vanilla map
(29 of 30 connected; `north_sea_region`/Ireland is vanilla's own split). Re-run the generator and read
its warnings - that is the verification. Do not open a savegame expecting one.

### How it takes over from vanilla, and the one loose end

WA's file has the same relative path and name as vanilla's, so it overrides it file-for-file -
**ASSUMED**, that is standard HOI4 mod loading, not something verified this session.
`replace_path="common/ai_faction_theaters"` was also added to `descriptor.mod` as belt and braces
(it additionally deletes anything else vanilla might put in that folder in a future patch).

**`descriptor.mod` is in `.gitignore` and is not tracked**, so that line is a local change on one
machine. Whatever descriptor actually ships needs the same line adding by hand, or the folder rests
on the filename override alone.

---

## 16. Commonwealth defensive handoff (2026-08-19)

The British Country layer delegates three static defensive burdens to Commonwealth field armies,
but keeps a dynamically selected fallback. The delegate and ENG read the same availability trigger:
if that verdict becomes false, the delegate aborts and the matching British fallback becomes live.
Country identity is confined to `WA_AI_CONFIG.txt`; readiness is based on current war, army size,
controlled ground and home pressure rather than a focus, date or historical faction.

| Mission | Delegate live | ENG floor | ENG fallback | Delegate gate |
| --- | ---: | ---: | ---: | --- |
| British Isles | CAN `0.25` normally / `0.50` during an actual invasion | `0.10` | `0.25` | AI CAN-role country, >11 divisions, common war plus faction/subject/access relation with ENG, Britain held by ENG's side, no enemy on a Canadian core, no home-area neighbour at war with CAN and no war with USA |
| El-Alamein primary guard | SAF `0.25` on Marsa Matruh | see ladder | see ladder | AI SAF-role country, >4 divisions, common war plus access relation, Egyptian line active, Marsa Matruh friendly, no SAF home/border threat |
| El-Alamein support | RAJ `0.05` on Marsa Matruh | `0.05` if both live | `0.15` if exactly one lives; `0.25` if neither lives | AI RAJ-role country, >49 divisions, operational army, common war plus access relation, Egyptian line active, Marsa Matruh friendly, no enemy on a RAJ core and no home-area neighbour at war with RAJ |
| Kuwait | RAJ `0.05` | `0.02` | `0.08` | AI RAJ-role country, >29 divisions, operational army, common war plus access relation, Kuwait held by ENG's side **and the Gulf approach threatened (Fix 125)**, Ethiopian colonial war finished, no enemy on a RAJ core and no home-area neighbour at war with RAJ |
| **East Africa (Fix 124, 2026-08-21)** — an OFFENSIVE mission, the first of the family | RAJ `front_unit_request +100` on `WA_AI_MILITARY_east_africa_regions`, on top of the Faction `+150` | — | ENG returns to the Faction `+150` when the delegate is unavailable | AI RAJ-role country, >29 divisions, **delegate force floor** (controlled states + manpower, no 41-division/0.9-equipment brake — 2026-08-24, see below), common war plus access relation, the East-African theatre contested, **the Pacific quiet (`NOT pacific_threat_imminent`)**, no enemy on a RAJ core and no home-area neighbour at war with RAJ |

**Fix 124 — East Africa (2026-08-21, campaign `8c0fea4c`, checklist R85).** The first *offensive*
delegation of the family: the other three park divisions, this one sends them. ENG's half is
`WA_AI_MILITARY_ENG_east_africa_delegated_FRONT`, `-130` on the same area while the delegate is live
(was `-75` until 2026-08-24, see below), netting ENG `+20` against RAJ's `+250` — deliberately below
ENG's `north_africa` net, so Egypt outbids East Africa while the delegate carries the theatre.

**That `north_africa` net is CONDITIONAL since [commonwealth-handoff] (2026-08-24).** It is `+25` while
Egypt is clear (Faction `+75`, `africa_war_1` `-40`, `africa_war_3` `-20`,
`focus_on_land_War_in_north_africa` `+10`) and **`+85` while an enemy stands on Egyptian soil**, when
the two negatives stand down — they now live in
`WA_AI_MILITARY_COUNTRY_ENG_FRONT_north_africa_brake_egypt_held` / `_border_held`, gated on
`NOT = { WA_AI_MILITARY_egypt_is_invaded = yes }`. The delegation's `-130` is NOT re-sized: its
intent (Egypt outbids East Africa) holds at both nets — the margin widens from 5 points to 65
exactly when Egypt is under attack, which is the case the delegation was written for. **Both numbers
assume the engine SUMS `front_unit_request` entries sharing an `area`, which is unresolved** — see
`.claude/skills/wa-diagnosis/SKILL.md` technique 5 rule 3. Any retune of these values waits on that
question; the throttle split does not, because removing an entry works under either reading.
On regions 17/217 the `central_africa` `-50` of `africa_war_1` also applies (that alias contains
both), taking ENG to `-30` there under delegation. **The ENG half is the point** — without it the
delegate only adds divisions to Ethiopia and nothing is freed for Egypt.

**Deepening to `-130` (2026-08-24, campaign `eefaa9fc`, save 1940.10).** MEASURED: ENG held **40 of
62 divisions in East Africa + Sudan against 9 Italian**, and **3 in Egypt against 39** (Italy already
in Marsa Matruh) — at `-75` the East-African net (`+75`) still outbid Egypt (`+25`) 3:1. Two caveats,
both open: (a) **the delegation was OFF in that save** — RAJ (36 divisions, `WA_AI_fielded_eq_ratio`
0.6033) fails `WA_AI_MILITARY_army_still_operational` (bars 41 divisions / 0.9 equipment, calibrated
on major-power collapse data in `WA_AI_MILITARY_posture_triggers.txt`), so no readiness verdict of
the Commonwealth family armed, while the Faction `+150` still sent 16 RAJ divisions to East Africa
anyway — the delegate fights unready, only ENG's stand-down waits for paper readiness; (b) cross-AREA
ordering of `front_unit_request` values (Egypt `+25` beating East Africa `+20`) is ASSUMED engine
behaviour, same status as the §17 magnitude caveat — verification is the campaign probe on
`commonwealth-handoff` in WORK.md.

**(a) resolved (2026-08-24, owner decision "plancher léger").** The two ADD-force verdicts —
`WA_AI_MILITARY_RAJ_east_africa_available` and `WA_AI_MILITARY_RAJ_egypt_reinforcement_available` —
now read `WA_AI_MILITARY_delegate_force_floor` (controlled states + manpower + equipment
`constant:wa_ai_posture.delegate.min_eq` = 0.45, calibrated to the delegate population's healthy
~0.6 baseline rather than major-power collapse; `has_variable` reads absent as not-proven; each
verdict keeps its own `num_divisions` bar) instead of the full `army_still_operational` brake. The
`delegate.*` keys are deliberately separate from `alive.*`/`manpower.*` (advisory registry groups)
so retuning the collapse brake never silently moves the handoff. The three pure STAND-DOWN verdicts
(El-Alamein support/handoff, Kuwait guard, UK guard) keep the full brake unchanged: a weaker gate
there makes the guarded ground weaker (Fix 128 warning). The East-Africa verdict is ADD-force for
RAJ **and** stand-down for ENG in one sentence — the 0.45 equipment term is what keeps a hollow
delegate (30+ paper divisions, no equipment) from releasing ENG there. With RAJ's measured 1940 army
(36 divisions, equipment 0.60) both ADD verdicts now arm: RAJ bids `+50` on `north_africa` and ENG's
`-130` stand-down goes live. MEASURED at 1940.10: ENG had **37 of its 66
divisions (56 %) in the East-African theatre and 8 in Egypt/Libya**, while RAJ had **24 of 42 (57 %)
sitting in India**. The pull already reached RAJ (Faction `+150`) and its own `-100` Asia-first
suppression was not armed — the Indian army was *reserved*, not unasked, which is why Fix 123 is a
hard prerequisite and R85 cannot pass while R84 fails.

**Fix 123 — releasing the Pacific Commonwealth's home garrison (2026-08-21, checklist R84).**
`WA_AI_MILITARY_ARCHETYPE_minors_home_first` (`WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt`) gives
**every minor at war `garrison = +50`** — more engine area defence, not less. AST and NZL have no
`garrison` writer of their own, so MEASURED at 1941.6 they held **17 of 22 (77 %)** and **8 of 11
(73 %)** of their armies in area-defence orders while Japan was still neutral; RAJ held 17 of 40.
`WA_AI_MILITARY_ALLIES_pacific_quiet_release_garrison` (`WA_AI_MILITARY_FACTION_ALLIES_FRONT.txt`)
writes `garrison = -5000` plus `+60` on `north_africa` and on the East-Africa alias for AST / NZL /
RAJ, behind `WA_AI_MILITARY_pacific_commonwealth_garrison_releasable`.

The switch is **`WA_AI_MILITARY_pacific_threat_imminent`**: a Pacific war is running, a Pacific
expansionist has a wargoal against us, is justifying one, or has completed a southward focus
(`WA_AI_CONFIG_MILITARY_pacific_offensive_posture`, which is where the focus ids live because focus
ids are tag-specific classification).

**`JAP_strike_south_doctrine` was in that posture list for one build and was removed on 2026-08-21.**
It is an army-branch *doctrine* focus, not a decision to attack, and it completes far too early to be
a warning: MEASURED on the retest, absent at 1940.6.24, complete by 1941.5.23, against a Japanese war
on Britain starting **1942.1**. Eight to twelve months of false alarm, during which this release and
the Fix 124 delegation were both held OFF and RAJ sat on 25–29 of its 40 divisions in India. What
remains is `JAP_strike_south` — the actual southward war focus — plus the wargoal pair, which is a
real intent signal rather than a doctrine purchase. `WA_AI_MILITARY_AST_japan_war` and
`WA_AI_MILITARY_RAJ_japan_war` read the same verdict and therefore arm later than they used to; that
is the deliberate trade and R84 leg 4 is its falsifier. It now also gates `WA_AI_MILITARY_AST_japan_war`,
`WA_AI_MILITARY_RAJ_japan_war` and `WA_AI_MILITARY_RAJ_unit_saving`, so the release and the
re-garrison are two sides of one verdict rather than three independent Japan tests.

**`garrison = -5000` is no longer an untested convention.** The paragraph below this table used to
say the force-off convention "is not documented by the engine and remains a campaign test" — RAJ is
its own control on campaign `8c0fea4c` and answers it: area-defence divisions read **14 / 17 / 16**
at 1940.10 / 1941.6 / 1941.12 with no `-5000` armed, and **0 / 3 / 2** at 1942.3 / 1942.6 / 1943.6
once the JAP war armed `WA_AI_MILITARY_RAJ_core_front_requests`, while the BUFFER count *rose*
17 → 21 → 25. **DERIVED**, rival explanation named: the switch coincides with Japan's entry, which
also opens fronts. The cross-section closes it without the date — on the single 1941.6 save, GER
reads 1 of 203 and ITA 4 of 84 (both carry `-5000`) against AST's 77 % and NZL's 73 % (neither does).
`garrison` is **Additive** (owner ruling 2026-08-21), so `-5000` over `+50` nets `-4950`; R84's first
fail-tell is the falsifier if that ruling is wrong.

**Fix 128 — the El-Alamein mission had a bar nobody could clear (2026-08-21, checklist R89).**
The support mission's verdict `WA_AI_MILITARY_RAJ_egypt_support_available` requires
`num_divisions > 49`. MEASURED on the retest of campaign `8c0fea4c`: RAJ fields **59** divisions in
June 1940, loses its BEF / Norway contingents with France, and runs at **40 / 40 / 42** at 1941.5.23 /
1941.6.10 / 1941.10.6 — so **the mission has never armed in any campaign**, and RAJ held **25 / 29 /
25** divisions in India while the entire Allied force on the Egyptian front was **13 / 13 / 15**.

**The bar was not lowered, and that is the point.** ENG's three-tier ladder reads the same verdict and
**stands down** when it is true (0.25 → 0.15 with one delegate → 0.05 with two). On the measured armies
lowering it would have taken ENG from 0.15×55 ≈ 8.2 to 0.05×55 ≈ 2.8 against RAJ's 0.05×40 = 2 — a net
**loss** of about 3.5 divisions at El Alamein, the opposite of the report. Fix 128 adds a **second
verdict**, `WA_AI_MILITARY_RAJ_egypt_reinforcement_available`, identical except `num_divisions > 29`,
read by the three RAJ writers that ADD force (`_FRONT_support_el_alamein` +50, `_THEATRE_support_el_alamein`
0.05, `_DIPLOMACY_defend_north_africa` 100) and by nothing else.

**Stated departure from the handoff invariant of this section:** between 30 and 49 RAJ divisions, ENG
does *not* stand down and RAJ reinforces anyway, so Egypt is deliberately double-covered. The change is
monotone in RAJ's army size — below 30 nothing moves, above 49 both verdicts are true and the ladder
behaves exactly as before — and there is no band where Egypt is weaker than it is today. R89 leg 3 is
the regression test for the split.

**Fix 125 — the Kuwait guard needs a threat (2026-08-21, checklist R86).**
`WA_AI_MILITARY_ENG_kuwait_guard_active` asked only "is ENG at war" and "do we hold 656", so the
mission ran from 1939.9 to the end of the war over interior allied ground: MEASURED, ENG held
1 / 1 / 3 / 4 divisions in Kuwait at 1940.10 / 1941.6 / 1942.6 / 1943.6 and RAJ never took the
delegated mission at all. The third term is `WA_AI_MILITARY_gulf_approach_threatened` — an enemy of
ENG on 291 / 675 / 1041 (Iraq), 413 (Khuzestan) or 292 (Nejd), or `ENG = { pacific_war_active }`.
The maritime half deliberately uses `pacific_war_active`, **not** `pacific_threat_imminent`: a fleet
has to be at war to appear in the Gulf, and the owner's rule for Kuwait was literally "Japan not in
the war" where the rule for the dominions' garrison was the wider "not about to attack". The term
disarms all three consumers together — ENG floor, ENG fallback and RAJ's delegate — which is the
intent: there is no mission, so there is nothing to delegate.

CAN's Canadian-front request is split into a safe floor (`+10`) and a threatened tier (`+200`).
The threatened tier re-arms on an enemy-controlled Canadian core, a home-area neighbour at war or war
with the USA; CAN's British mission is disabled on the same verdict. While that mission is live, a
Country `garrison = -5000` applies WA's force-off convention to release the generic minor-country
area-defence army. **That convention is no longer untested** - the `garrison = -5000` paragraph
above measures it on RAJ and on a five-country cross-section of one save (2026-08-21, campaign
`8c0fea4c`). It is still undocumented by the engine; what changed is that its effect is observed.
The historical Africa/date block and the permanent Dover buffer are deleted, so Canada is not told
to defend Britain and Africa at once. The normal and invasion tiers are exclusive: one `0.25` order
outside an invasion, one `0.50` order during it; no ratio is inferred by adding two orders.

SAF and RAJ receive matching `front_unit_request` (`+50 north_africa`) and
`force_defend_ally_borders` (`100 north_africa`) writers while their El-Alamein availability is true.
The former Faction SAF/RAJ Africa trio is deleted; AST/NZL retain only the existing `0.10` Egyptian
top-up. RAJ's former Iraq/Kuwait pair is narrowed to Kuwait, after the Ethiopian campaign gate.

### Historical and ahistorical walks

| Situation | Result |
| --- | --- |
| Historical coalition, all delegates ready | CAN guards Britain; SAF guards Marsa Matruh; RAJ supports Marsa Matruh and guards Kuwait; ENG runs reduced floors. |
| CAN-role country absent, player-controlled, weak, without access, threatened at home or fighting USA | CAN mission aborts; ENG restores its `0.25` British reserve. |
| SAF or RAJ absent, player-controlled, weak or under its safety threshold | ENG uses the middle `0.15` Egyptian tier when one delegate remains, or restores the former `0.25` tier when neither remains. |
| Ethiopia survives outside Italy's colonial war | The generic `ethiopian_war_finished` verdict can release RAJ once no Italian homeland power is fighting a colonial-only Ethiopian war; no annexation, focus or calendar is required. |
| ENG changes faction or the historical setup diverges | A delegate needs a real common war with ENG. If it cannot take the mission, the ENG fallback remains the owner; no historical-focus branch is required. |

### Campaign probe

Pre-change baseline: campaign `2f8cbd51-0a44-40a2-a371-714ba21c96b5`, save
`1942.7_Jul.hoi4` at `1942.7.1.2`. ENG had 85 divisions: 54 in buffers, 7 on fronts,
18 in area defence and 6 in invasions. Eight of its nine armoured divisions were in buffers.
CAN had 16 divisions (14 in Canada, 2 in Britain); SAF had 6 (none in Egypt); RAJ had 61,
including 12 with no order.

The next campaign closes this change when the same date/state shows:

1. the eligible delegate orders on Britain, Marsa Matruh and Kuwait, with the Canadian area-defence count falling from its pre-change 12;
2. the corresponding reduced ENG tier, with exactly one Egyptian ENG tier active;
3. automatic restoration of each ENG fallback after making its delegate unavailable;
4. fewer ENG divisions in buffers and more than one ENG armoured division on a front;
5. no loss of Britain, Marsa Matruh or Kuwait attributable to the handoff.

Engine boundary: `put_unit_buffers` cannot select an infantry template. The script reduces the
British reserve demand and transfers destinations to other countries; the exact British divisions
released, and whether the engine selects armour for a remaining buffer, are not observable script
decisions and must be measured in the campaign.

---

**Fix 134 (2026-08-21, campaign `8c0fea4c`, checklist R95) - the Kuwait guard is sized against the
force on the approach.**

MEASURED: Kuwait 656 held **1 RAJ division** at 1941.4.28 while Iraq had **7** on the approach (Dhi Qar
3, Al Hajara 2, Ninawa 1, Baghdad 1). The state read controller GER by 1941.9.20 and IRQ by 1942.4.4.
RAJ fielded 45 divisions and ENG 68, so the guard was not short of men.

**The arming was never the defect.** The pre-Fix-125 gate was true throughout; every tier of the family
is a fraction of the GUARD's own army (0.05 RAJ, 0.02 ENG delegated, 0.08 ENG fallback) and nothing in
it reads the other side. 0.05 x 45 = 2, and it would have been 2 against 7 or against 70.

| Trigger (new) | Question it answers |
| --- | --- |
| `WA_AI_MILITARY_gulf_approach_massing` | PREV-relative, for `any_country`: does this country have `divisions_in_state size > 2` on 291 / 675 / 1041 / 1042 / 413 / 292 |
| `WA_AI_MILITARY_gulf_approach_massed` | the same asked at fixed ENG scope - the SIZE question, read by the reinforced tiers |
| `WA_AI_MILITARY_gulf_approach_imminent` | a non-allied holder of the approach that is preparing a war on Britain (`has_wargoal_against` / `is_justifying_wargoal_against`) **or** massing - the ARMING question, added as a limb of Fix 125's `gulf_approach_threatened` so the buffer is not still empty on the day of the declaration |

Sizing becomes two gate-exclusive tiers on `_massed`: RAJ 0.05 -> **0.15** (order_id 9208), ENG fallback
0.08 -> **0.20** (order_id 17). Exclusive, not additive, and on separate order_ids - this repo sizes
`put_unit_buffers` tiers exclusively (see the handoff table above: "no ratio is inferred by adding two
orders") and a shared id would be one diluted pool.

`divisions_in_state` is a COMPARISON trigger - script carries no exact per-state count - so "massing" is
a threshold on ONE state, never a sum across the approach. `> 2` is the bar because three divisions in
one border state already outnumbers a 0.05-sized guard two to one; on the measured save Dhi Qar reads 3
and clears it, **four months before the state falls**.

## 17. The Afrika Korps window - a German armoured expedition toward Egypt (Fix 119, 2026-08-20)

User decision 2026-08-20: Germany sends armour to attack Egypt at least until the Soviet war or a
D-Day-type landing; Italy garrisons the conquered Egyptian ports and holds the line.

Pre-fix state (MEASURED this session): Germany's whole Africa posture was negative
(`focus_on_north_africa` `front_unit_request` -75, standing area tilt -80, `war_with_soviets_2` -75)
and its only armour steer toward Africa, `front_armor_score id = "ITL"` 10, was **inert** - `id` is
the ENEMY tag of the front (vanilla usage: GER `id = POL` 250, `id = SOV` 500) and Germany is never
at war with its ITL ally. Germany also had no `ordertype = front` control on the `north_africa`
area, so German divisions there would never have executed an offensive.

The window: `WA_AI_MILITARY_afrika_korps_window` (`WA_AI_MILITARY_triggers.txt`, Fix 99 family) -
allied with the Italian homeland power, our-side Libyan staging ground (Fix 99 one-side definition:
`libya_bridgehead_held` is unreadable from GER's scope because ITL is ITA's subject, not a faction
member), an enemy controlling the East-Egypt anchor 446/447/453, NOT `home_threatened`, and NOT
`AIR_theatre_contested_western_europe` - the last term covers both the Battle of France and any
D-Day dynamically. The "no Soviet war" clause is deliberately NOT in the shared trigger (the
section is tag-free); it sits in the `enable` of each GER consumer.

Consumers, all Country-layer GER: `WA_AI_MILITARY_GER_focus_on_north_africa_FRONT` (+60
`front_unit_request` on the blob; `front_armor_score` 150 on the ENG/UKE/UKM anchor payload tags -
an ahistorical Egypt controller gets request+exec but no armour bias, a named degradation),
`_THEATRE` (area_priority 130, nets +50 over the -80 tilt), and
`WA_AI_MILITARY_GER_north_africa_offensive_exec_FRONT` (`front_control` balanced, gated on the
generic `north_africa_offensive_viable` verdict - the R13 mirror). Italy's rear:
`WA_AI_MILITARY_ITA_garrison_conquered_ports_THEATRE` (`put_unit_buffers` order 9616, states
447/452/923 at 0.10, gate survives full conquest via a control branch).

Window close (Barbarossa or D-Day) removes the pull, not the force: t0 the blocks abort and
`war_with_soviets_2` re-arms -75; t1 the weekly allocator re-targets surplus and AIFC re-steers
armour; t2 the force drains at convoy speed - a cut strait strands it (historical DAK shape,
accepted; R80 fail-tell). Sea-lift INTO Africa is MEASURED viable (R64: 0 -> 8 GER divisions into
Tunisia in 31 days on 9d83084c). Probe: checklist R80. R64 leg 3 was re-cut the same day - its old
"GER divisions in Libya/Egypt stay <= 3" bar forbade exactly this expedition.

**Fix 121 (2026-08-21, campaign `8c0fea4c`, checklist R82) - the expedition halved.** Fix 119 worked,
and that is the problem this retune answers. MEASURED: German divisions in the African scope went
2 (1940.9) -> 9 (1940.11) -> **16 (1940.12)** -> 15 (1941.1) -> 1 (1941.2) -> 7 (1941.6) -> 0 (1941.12),
the window opening on Italy's entry and closing on Barbarossa exactly as designed. But at the 1940.12
peak the Axis held **57 divisions** in the scope (GER 16, ITA 35, ITL 6) on a corridor with **4 BREAK
hops out of 9** and nothing above level 1 east of Sirte (same month, the Fix 120 reading in
`WA_AI_RAILWAY_SYSTEM.md`). User ruling 2026-08-21: reduce, do not cancel; start at 50 %.
`front_unit_request` **60 -> 30** and `area_priority` **130 -> 105** - the standing area tilt is -80, so
the net goes +50 -> +25, half measured on the net, which is the number the engine sees.
`front_armor_score` 150 is deliberately **not** halved: armour is the nature of the expedition, not its
size.

**The risk, stated.** It is **ASSUMED** that halving a `front_unit_request` weight halves the divisions
that arrive; the engine's weight-to-division mapping is not observable in a save, and the one anchor
that is measured is "at 60, the peak was 16". A division-count brake (`divisions_in_state` caps on the
corridor states - COUNTRY scope, already used as an ai_strategy gate at
`WA_AI_MILITARY_COUNTRY_GER_FRONT.txt` `FRA = { divisions_in_state = { state = 28 size > 4 } }`) was
designed and **DEFERRED by owner decision**: do the arithmetic cut, measure, then decide. R82 leg 1's
fail-tell is what puts the brake back on the table. **R80 and R82 are twins and must be scored in the
same session** - R82 leg 2 ("not cancelled") is R80 leg 1 read from the other side.

---

**Fix 131 (2026-08-21, campaign `8c0fea4c`, checklist R92) - the window no longer closes at Barbarossa.**
User ruling 2026-08-21, which reverses one half of the 2026-08-20 rule this section was written to:
German armour STAYS in Africa. The `NOT = { has_war_with = SOV }` clause is deleted from all three GER
consumers. The D-Day half of the original rule is untouched and still dynamic - it lives inside
`WA_AI_MILITARY_afrika_korps_window` as `NOT = { WA_AI_MILITARY_AIR_theatre_contested_western_europe }`,
so the window still closes by itself when the West opens, with no date and no tag.

**The paired half, and it is not optional.** `front_unit_request` is ADDITIVE per area, so removing the
gate alone would have left `WA_AI_MILITARY_GER_war_with_soviets_2_FRONT`'s `area = north_africa` `-75`
standing against the expedition's `+30`: net -45 over the standing -80 tilt, an expedition that exists
in the file and never arrives. That one line is therefore split out into
`WA_AI_MILITARY_GER_war_with_soviets_africa_suppression_FRONT`, gated `has_war_with = SOV` AND
`NOT = { afrika_korps_window }` - exclusive with the expedition, re-arming on the same tick the window
closes. The two `strategic_region` -35 lines and both `garrison` lines stay where they were: they are
not part of this trade.

**MEASURED, and it is why this is a fix and not a preference.** On campaign `8c0fea4c`, **zero** German
divisions stood anywhere in North Africa on all five saves from 1941.4.28 to 1943.3.22 - including
1942.11.21, four weeks after Torch, when Germany **owned and controlled** Tunis 458, Bizerte 1061 and
Gabes 665 and they were defended by **one Italian division** (section 14, Fix 133). Italy, and so
Germany, had entered the Soviet war on 1941.6.22. Every one of the window's five terms was true on that
save; the SOV clause was the only lock.

Fix 121's magnitudes (`front_unit_request` 30, `area_priority` 105) are **deliberately unchanged**.
Extending the duration and raising the weight in one commit makes the next campaign unreadable: R92 asks
whether the force survives Barbarossa and whether it still comes home for a D-Day, and both questions
need the old weights to mean what they meant.

---

**Fix 137 (2026-08-21, campaign `8c0fea4c`, checklist R82) - `front_unit_request` 30 -> 40.** Owner
ruling after the first in-game run of Fixes 120-135 (build `bc90346af`, saves 1940.7.24 → 1941.10.23).

**MEASURED on that run.** German divisions in the African scope: 0 (1940.7) → 2 (1940.10) → **7
(1940.11)** → 0 (1941.4) → 0 (1941.6) → 0 (1941.10). German front orders touching Africa: 8 divisions
on a "Marsa Matruh" front at 1940.11, **1** division at 1941.4, **no African front at all** at 1941.10.
Every one of the window's five terms was TRUE at every one of those dates (Axis with ITA/ITL; ITL holds
448/450/451/663 on all six saves; ENG holds 446/447/453 on all six; GER `surrender_progress` 0; Western
Europe = GER 16 / VIC 9 / RBE 5 / RHO 3, no enemy). So R82 leg 1 (peak ≤ 8) is met and **leg 2 (≥3
divisions on ≥3 consecutive saves) fails**.

**Why the number alone probably does not close it, stated before it is tested.** The collapse to ~0 in
early 1941 also happened at weight 60 (16 at 1940.12 → 1 at 1941.2, previous campaign) - it PRECEDES the
Fix 121 cut and is independent of it. The binding constraint is the engine's arbitration between 18
contiguous eastern fronts and one overseas theatre; no `front_unit_request` magnitude is known to move
it, and the mapping from weight to divisions is **ASSUMED** (§17, Fix 121's stated risk). +10 buys
margin, not a mechanism. Recorded next lever if leg 2 fails again:
`theatre_distribution_demand_increase` on `north_africa` gated on the window - a demand type rather than
a front bias.

**Ruled out as the lever, with the measurement (2026-08-21).** AIFC cannot bring the armour: it
redistributes units already assigned to a front (`documentation.info` `force_concentration_factor`), it
needs an African front to rank (`AIFC_MAX_NR_FRONTS = 4`) and Germany has none, and its sector engine
can never anchor there - the native pass needs a ROOT-controlled state adjacent to an enemy, and the
expeditionary pass (`WA_AI_AIFC_helpers.txt:119`) is gated on `_aifc_cand^num < 3`, which Germany's
eastern candidates never satisfy. MEASURED sector: 144 Nord-Norge + 878 Troms from 1940.11 to 1941.6,
then Chernigov / Sumy / Bryansk / Gomel / Kiev / Poltava at 1941.10.
**One real collision found and NOT fixed here:** `WA_AI_AIFC_armor_reconcile` writes +400 on the sector
enemy and **−150 on every other enemy**; MEASURED in the save (88 `persistent_strategy type=83` entries,
net per country) SOV +400 and **ENG −150**, exactly cancelling this section's `front_armor_score id =
"ENG" value = 150`. The claim in `WA_AI_AIFC_helpers.txt` that −150 always sits "below the explicit
faction/country steering entries" is false for that entry. Left alone deliberately - it is second-order
while Germany has no African front, and fixing two things at once makes R82 unreadable. QUEUE it.

`area_priority` (105 over the standing −80, net +25) is **deliberately not raised with it**, for the same
reason Fix 131 gave: two magnitudes in one commit and the next campaign cannot attribute the outcome.

## 18. Allied and Axis air policy - the Reich bombing ladder and the Western Europe / Mediterranean family

(Moved here 2026-08-20 from the AGENTS.md system table, verbatim in substance - this section is the owner.)

Every coalition-level `strategic_air_importance` rule of the Allies, and the mirrored Axis family.

| Piece | File |
| --- | --- |
| Allied faction rules | `common/ai_strategy/WA_AI_MILITARY_FACTION_ALLIES_AIR.txt` |
| Axis-wide avoidance | `common/ai_strategy/WA_AI_MILITARY_FACTION_AXIS_AIR.txt` |
| Reich air-defence pull | `common/ai_strategy/WA_AI_MILITARY_COUNTRY_GER_AIR.txt` |
| Switches (control panel) | `common/scripted_triggers/WA_AI_MILITARY_triggers.txt`, sections "AIR - Allied Reich bombing ladder", "AIR - Allied Western Europe / Mediterranean state triggers", "AIR - Axis western front / Battle of Britain / Reich air defence" |
| Type semantics | `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` (`strategic_air_importance`) |

**First fact: the type ranks regions for the planes the engine already requests, it does not create
demand** - requests come from own combats/armies, enemy planes, enemy factories, ships (campaign
`a232d96c`, checklist R15 RECUT) - so no value here can stage an air force ahead of the ground war.

**Phase 7d (2026-08-16)** moved the whole former ENG.txt Allied family to the Faction layer
(Channel-coast push/avoidance, Sicily push, home-islands threat/lost, occupied-Europe and
out-of-theatre avoidance), gated on `WA_AI_MILITARY_is_allies_member` plus state triggers (an
overseas ally staging in a Channel county, a Sicily foothold, a human enemy on the far shore)
instead of eight-tag lists and 1943/1944 date windows; the last -500k black holes of that family
were retuned to the -20k tier. **Phase 7e** did the same for the GER.txt family (Axis-wide
avoidance in the AXIS file, the Reich air-defence pull in the GER Country file). It replaced the
legacy ENG.txt date-gated family (`Allies_bombing_germany_is_too_costly`,
`allies_avoid_bombing_austria_prussia`, `ENG_FRA_allies_avoid_bombing_GER`).

**Small-force home defence (2026-08-18):** an Allies member fielding <= 399 aircraft
(`@WA_AI_AIR_HOME_ONLY_ARM`, released above 499) gets -300,000 on every foreign air theatre and
keeps its whole force over its own capital theatre - twelve `WA_AI_MILITARY_ALLIES_AIR_home_only_*`
blocks, gated only on faction membership, plane count and control of its own capital; the exclusion
is a per-block `capital_scope` region test, so no tag and no archetype list. The goal is the
coalition's, not the minor's: forward air-base capacity is finite and half of vanilla's in WA
(`AIRBASE_CAPACITY_MULT` 100 vs 200), so a slot a minor does not occupy is a slot the majors'
better aircraft do.

**The Reich bombing ladder:** how hard the western Allies are told to avoid German air space, and
when that lifts. Three additive `strategic_air_importance` rungs over the near ring (regions
6/7/8/296) and deep ring (294/38), each gated on a **deployed strategic-bomber count** rather than
a date, each enabling below its own bar and aborting above the next one so the net walks down with
hysteresis. The four thresholds, the ring membership and the contested-Germany backstop are all in
the trigger sections above - **change behaviour there, never by editing the strategy blocks**.

The positive half of the campaign is `WA_AI_MILITARY_ENG_strategic_bombing_focus_THEATRE`, which
writes `area_priority` and is a separate axis.

---

## 19. Allied convoy interdiction in the Mediterranean (Fix 122, 2026-08-21)

User report on campaign `8c0fea4c`: Britain should raid harder in the central Mediterranean, with
surface fleets if that is what it takes - regions **29** (Strait of Sicily) and **269** (Ionian Basin)
for as long as Malta or Tunis is Allied-held, and **327** (Levantine Basin) while Tobruk is Axis-held.

**The pre-fix state is a repo measurement, and it is the strongest half of the evidence.** A census of
every `ai_strategy` in `common/ai_strategy/WA_AI_NAVAL_*.txt` finds **no Allied
`naval_convoy_raid_region` on 29, 269 or 327 at all**. The only writers on those three regions are
`WA_AI_NAVAL_COUNTRY_USA_legacy_USA_convoy_raid_strategy` at **-1000** and
`WA_AI_NAVAL_COUNTRY_GER_legacy_GER_dont_convoy_raid_too_far_away` at -1000. ENG's only positive raid
regions are 16, 18 and 365 - all home waters, all gated on Britain being invaded. The campaign
consequence: Italy's free convoy pool read **1023 / 1008 / 1004** at 1941.6 / 1942.6 / 1943.6, a 1.9 %
dent over three years of running the entire Libyan supply line, while 35-42 Italian divisions and up to
16 German ones were fed across it.

| Piece | File |
| --- | --- |
| Faction blocks | `common/ai_strategy/WA_AI_NAVAL_FACTION_ALLIES.txt`: `WA_AI_NAVAL_FACTION_ALLIES_med_lifeline_raid` (29 + 269 at +250, `naval_avoid_region` -250, `naval_mission_threshold "MISSION_CONVOY_RAIDING" -100`) and `_tobruk_route_raid` (327 at +250, avoid -250) |
| Switches (control panel) | `WA_AI_MILITARY_triggers.txt`, the Fix 122 section next to the NAVAL corridor triggers: `WA_AI_MILITARY_NAVAL_med_raid_base_held` (Malta 116, Tunis 458 or Bizerte 1061 held by our side), `_axis_african_lifeline_active` (an enemy holds 448/450/451/458/1061 - the convoys exist), `_tobruk_held_by_enemy` (state 451). Same PREV.PREV "our side" idiom as the Fix 99 family |
| Capability gate | `WA_AI_MILITARY_is_major_naval` (`has_navy_size = { size > 100 }`) in each block's `enable` - **owner ruling 2026-08-21: only large, major navies raid the narrows**. MEASURED 1941.6: ENG 494 hulls and USA 476 pass; AST 11, FRA 21, NZL 7, CAN 2, RAJ 1, SAF 0 do not |
| Probe | checklist R83 |

**Three things to know before touching it.**

- **The type ranks, it does not recruit.** `naval_convoy_raid_region` orders the regions the engine has
  already decided to raid in; it cannot stage a task force that is committed elsewhere. **ASSUMED**, by
  analogy with the documented behaviour of `strategic_air_importance` (section 18). R83 leg 1 measures
  the outcome (the Italian convoy pool) precisely because the arming is not observable.
- **The surface-fleet lever is `naval_mission_threshold "MISSION_CONVOY_RAIDING"`**, which lowers the
  strength ratio the AI demands before committing a task force to that mission. The magnitude `-100`
  copies vanilla's own `MISSION_PATROL -100` (`ENG.txt:1378`) and is ASSUMED. Removing that one line
  turns the interdiction back into a submarine campaign.
  **The key is `MISSION_CONVOY_RAIDING`, and `MISSION_CONVOY_RAID` shipped here first and was rejected
  at boot** — `Error: "bad mission type: MISSION_CONVOY_RAID, near line: 860"`. It had been "verified
  present in `hoi4.exe`" with `grep -c` plus a negative control, and **grep matches substrings**, so
  the hit was the longer name. The mission enum is named in the install's `common/defines/00_defines.lua`
  `MISSION_FUEL_COSTS` comment block (HOLD, PATROL, STRIKE FORCE, CONVOY RAIDING, CONVOY ESCORT, MINES
  PLANTING, MINES SWEEPING, TRAIN, RESERVE_FLEET, NAVAL_INVASION_SUPPORT), and the exact literals come
  out of the binary by extracting whole `MISSION_[A-Z_]+` matches, never by counting substring hits.
- **It does not fight `ENG_med_is_lost`.** That legacy block writes `naval_avoid_region 29 = +2000`, but
  it needs Malta **lost**, and `med_raid_base_held` needs Malta or a Tunisian port **held**. Lose Malta
  with no Tunisian port and this block aborts in the same pass the other arms. MEASURED on `8c0fea4c`:
  `med_is_lost` never fired - Malta 116 and Gibraltar 118 were ENG on all 121 saves, which is also why
  **Malta, not Tunis, is what actually carries the gate** (Tunis 458 / Bizerte 1061 were Vichy until
  1942.12 and German after, so the Tunisian terms only pay from 1943.6). Both terms are kept: a world
  where Malta falls is exactly the world the Tunisian ones are for.

## 20. The Italian-entry tripwire on the colonial frontiers (Fix 127, 2026-08-21)

Section 12 gave East Africa a theatre. This gives it a **frontier before the war reaches it**.

User report on campaign `8c0fea4c`: "il n'y avait personne à la frontière ITS". MEASURED at the
**1940.6** save, four weeks before Italy's declaration on **1940.6.30**: ENG held **2 divisions in
Aden and nothing else** on the Sudan / Kenya / Somaliland frontier; RAJ **zero**; SAF **zero**.

**Why neither existing family could cover it.** Both are reactive by construction:
`WA_AI_MILITARY_ALLIES_east_africa_contested_FRONT` (§12) needs
`WA_AI_MILITARY_east_africa_theatre_contested`, which needs an **enemy already holding**
East-African ground; `WA_AI_MILITARY_ENG_el_alamein_guard_active` needs an enemy on Libyan ground
(450/663/451). Before the declaration neither can arm, and the region sits in the DEFAULT sink
lists. The Axis has no such gap — ITA's `east_africa_garrison_THEATRE` stands on 550/559 in peace.

| Piece | File |
| --- | --- |
| Verdict | `WA_AI_MILITARY_triggers.txt` `WA_AI_MILITARY_italian_entry_likely` — the ideology match AND (the bulwark collapsing OR `date > 1940.8.1`) |
| Release | `WA_AI_MILITARY_italian_entry_still_pending` — false the moment the Italian homeland power is at war with us, at which point §12 and the El-Alamein ladder own the ground (Italy owns the AOI, so `east_africa_theatre_contested` is true from day one). Exclusive **by timing**, not by a gate term |
| Identities and the pair test | `WA_AI_CONFIG.txt` — `_is_western_european_bulwark`, `_is_german_homeland_power`, `_italian_power_shares_german_ideology`, `_western_bulwark_is_collapsing`, `_is_italian_frontier_tripwire_force` (ENG + RAJ) |
| Payload | `WA_AI_MILITARY_FACTION_ALLIES_THEATRE.txt` `WA_AI_MILITARY_ALLIES_italian_entry_tripwire_THEATRE` — `put_unit_buffers` order **9617** at 0.06 on {551 Khartoum, 1096 Kurdufan, 549 South Sudan, 1100 Northern Kenya, 269 British Somaliland, 659 Aden}, order **9618** at 0.04 on {452 Marsa Matruh, 960 Libyan Plateau} |
| Probe | checklist R88 |

**There is no "same ideology as" trigger in HOI4 1.19.2.** `has_government` takes a literal ideology
group and nothing compares two countries' governments (checked in the install's
`documentation/triggers_documentation.md`), so
`WA_AI_CONFIG_MILITARY_italian_power_shares_german_ideology` enumerates the four groups. It lives in
CONFIG because it needs two tags and CONFIG is the only WA_AI file allowed to carry them.

**The date term is an OR fallback, never the only path** (design principle 1): it can only make the
tripwire arm *earlier* in a world where France does not fall, and deleting it leaves the dynamic
term standing alone.

**KNOWN LIMITATION, measured before shipping.** On this campaign the rule as specified cannot arm
much before the declaration. France held **29 of 29** metropolitan states at 1940.6.1 — one province
lost, Belgium already entirely German — so `surrender_progress > 0` is at best a mid-June event, and
`date > 1940.8.1` falls **after** Italy declared on 1940.6.30, so the calendar fallback never fires
here at all. Expect days to three weeks of warning. The recorded widening, **not applied, owner
decision pending**: a third OR term "the German homeland power is at war with the western bulwark",
which on this campaign is true from **1939.9.1** and would give ten months. R88's first fail-tell
points at it, and it is a one-line change to `WA_AI_MILITARY_italian_entry_likely`.

**Ratios are a tripwire, not an army** — on the 1940.6 army sizes, ENG 66 × 0.06 ≈ 4 and RAJ 42 ×
0.06 ≈ 2 in East Africa, ≈ 3 + 2 on the Libyan border. The point is that the border is not *empty*
when the war starts. AST / NZL / CAN / SAF are excluded from `_is_italian_frontier_tripwire_force`:
a buffer they cannot reach is a wasted order, and SAF fielded three divisions in 1940.

## 21. The Mediterranean Fleet - a base at Alexandria and a sea-control target (Fix 136, 2026-08-21)

Section 19 gave the Mediterranean a **raiding priority**. It never gave it a **presence**.

User report on campaign `8c0fea4c`: "la royal navy n'employait pas ses flottes lourdes de surface dans
la méditerranée. La royal navy, qui doit être basée vers Alexandrie, doit tenter de construire de la
suprématie navale sur les régions 69, 327, 269 et 29."

**MEASURED on the `1942.10_Oct` save.** ENG holds **46 heavy hulls** (battleship / battlecruiser /
heavy cruiser / carrier). Where every one of them was:

| Fleet | ships | heavy | mission | strategic regions |
| --- | --- | --- | --- | --- |
| Fleet 13 | 80 | **20** | escort + strike | 60 West Indian Ocean, 85 SW Indian Ocean |
| Fleet 12 | 5 | **5** | raid | 72 Straits of Malacca |
| Fleet 5 | 49 | **13** | reserve | none - in port, no admiral |
| Reserve fleet 3 | 30 | **6** | reserve | none - in port, no admiral |
| Fleet 3 | 102 | **2** | none | none - in port, no admiral |
| Fleet 15 | 7 | 0 | raid | 30, 312, **69**, 323, **327** |
| Fleet 11 | 20 | 0 | escort | **269** |
| Fleet 14 | 10 | 0 | raid | 48, 249 |
| Fleet 17 | 5 | 0 | raid | 68 |
| Fleet 10 | 40 | 0 | escort | 249 |

**Zero heavy hulls in any Mediterranean region.** 25 of the 46 were in the Indian Ocean and Malacca;
the other 21 sat in port in fleets with no admiral. The Mediterranean was a destroyer-and-submarine
war.

**The script line.** ENG's `strike_force_home_base` set is `{ 16 North Sea, 365 Southern Bight,
18 English Channel, 112 Azores, 249 Alboran }` (`WA_AI_NAVAL_COUNTRY_ENG.txt:105-270`). **Nothing in
the mod based a strike force east of Gibraltar**, and a census of `common/ai_strategy/` finds **no
`naval_dominance` on 29 / 269 / 327 / 69 anywhere** - Allied sea-control blocks cover the Atlantic
corridors (43/55/50/247/243/244/44 at 80; 54/57/112/47/48/61/356/371/370/53 at 70) and, in the Med,
only 249 Alboran and 68 Algerian Coast at 70.

**Alexandria is region 69.** MEASURED from `WA_AI_MAP_province_coordinates.txt`: region 69's province
13330 lies **79 map units** from Alexandria's port province 4076 (state 447, `naval_base = 4`,
Mediterranean Fleet HQ), against **259** for the nearest province of any other Mediterranean region.

| Piece | File |
| --- | --- |
| Faction blocks | `common/ai_strategy/WA_AI_NAVAL_FACTION_ALLIES.txt`: `WA_AI_NAVAL_FACTION_ALLIES_med_fleet_alexandria` (`strike_force_home_base 69`, `naval_dominance` 69 at 80 / 327 at 70, `naval_avoid_region` -1000 on both) and `_med_narrows_sea_control` (`naval_dominance` 269 / 29 at 70, `naval_avoid_region` -1000 on both) |
| Switch (control panel) | `WA_AI_MILITARY_triggers.txt`, Fix 136 section: `WA_AI_MILITARY_NAVAL_med_fleet_base_held` = `controls_state = 447` |
| Capability gate | `WA_AI_MILITARY_is_major_naval`, the same Fix 122 owner ruling |
| Probe | checklist R97 |

**Four things to know before touching it.**

- **`controls_state = 447` is the tag-free way to mean "the Royal Navy".** MEASURED 1941.6: ENG 494
  hulls and USA 476 both clear `is_major_naval`, but only Britain holds Alexandria - so only Britain
  gets told to keep a strike force there, and the block releases by itself the day Egypt falls. This
  is deliberate: a `strike_force_home_base` handed to the USN at Alexandria would pull the fleet that
  has to invade Sicily out of the western basin.
- **The two blocks have different lives on purpose.** The eastern pair keys on Alexandria; the
  narrows pair keys on the Fix 122 raid gate (Malta 116, or Tunis 458 / Bizerte 1061). Losing Malta
  must stop the push into the narrows without evicting the fleet from its own base.
- **The avoid arithmetic, because the type is Additive and one writer misleads.** 69: this -1000, plus
  `_trade_through_cape` +2000 only when Suez or Gibraltar is hostile, so +1000 net in that contingency
  - a soft wall, not a hard one, which is right for a fleet still based there. 327 / 269 / 29: this
  -1000 plus Fix 122's -250 = -1250 while its gates hold. `ENG_med_is_lost`'s +2000 on 29 cannot be
  live at the same time as the narrows block (it needs Malta **lost**, `_med_raid_base_held` needs
  Malta or Tunis **held**).
- **What neither type can do. ASSUMED**, and it is the same honesty Fix 122 owes: `strike_force_home_base`
  is a boolean with no engine documentation section, and `naval_dominance` is documented only as
  "used to set the naval dominance for an AI area", value "a Percentage between 0 and 100". Neither
  recruits a task force out of a fleet with no admiral - and 21 of ENG's 46 heavy hulls were exactly
  that. If R97 comes back with the base taken and the heavies still in port, the next lever is
  `naval_mission_threshold "MISSION_STRIKE_FORCE"`, **not** more dominance. That literal was verified
  as a whole `MISSION_[A-Z_]+` token extracted from `hoi4.exe` 1.19.2, never by a substring count -
  see section 19 for the boot error a substring count already shipped once.

**Known residual, recorded rather than silently edited.**
`WA_AI_NAVAL_COUNTRY_ENG_legacy_ENG_try_to_avoid_the_med` still writes `naval_avoid_region 218`
(Ionian Sea) `= +2000` for ENG whenever Libya 448 is Italian and ENG is at war with ITA or GER. 218 is
not one of the four regions the user named. MEASURED on 1942.10: Allied task forces reached 269 and
327 with that wall standing, so it is not a blocker today, but it is the first thing to look at if the
fleet bases at Alexandria and then never sails west. QUEUE row, not a silent edit.

---

## 22. Scripted-target reservation - the calendar's targets are off-limits BEFORE the operation ([scripted-invasion-reservation], 2026-08-23)

Owner request (2026-08-23): while the scripted-invasion system is active, the invader's faction must
not run ENGINE-planned naval invasions **against the countries the calendar will hit** until the date
of the LAST scripted invasion against that country - the engine parking a corps for its own Brittany
landing while the calendar will open Normandy immobilises divisions for nothing. Per COUNTRY, not per
state - the owner's explicit call over a state-level draft.

Forward-looking twin of the sec.10 freeze: sec.10 suppresses the theatre for 90 days AFTER a scripted
landing executes; this suppresses the calendar's own targets BEFORE their scheduled dates.

| Piece | File |
| --- | --- |
| Calendar data (GENERATED - regenerate, never hand-edit) | `common/scripted_effects/WA_AI_LANDING_reservations_data.txt` via `tools/gen_ai_landing_reservations.py` |
| Epoch init + monthly updater + stamp | `common/scripted_effects/WA_AI_LANDING_effects.txt` (reservation section) |
| Switch (control panel) | `common/scripted_triggers/WA_AI_LANDING_triggers.txt`, `WA_AI_LANDING_reservations_enabled` |
| Consumer (Default layer) | `common/ai_strategy/WA_AI_MILITARY_DEFAULT_INVASION_landing_freeze.txt`, `WA_AI_MILITARY_INV_reserved_scripted_target` |
| Wiring | `WA_AI_startup_on_actions.txt` (load + epoch), `WA_AI_misc_on_actions.txt` on_monthly (update, after `WA_TLM_tick_clock`) |
| Probe | `WA_TLM_resv_stamp_n` / `_first_t` / `_last_t` (telemetry doc §5, v30) |

**Mechanism.** The generator reads the two hand-maintained sources - `WA_KDE_AI_effects.txt` (who
fires which `WA_AI_invasions.N` in which year at which day offset; `#`-commented lines skipped) and
`events/WA_AI_invasions.txt` (each operation's ANCHOR STATE: the state whose CONTROLLER the event
reads as its target; three events read OWNER, same anchor either way) - and emits per-invader arrays
`WA_AI_LANDING_op_anchor` / `WA_AI_LANDING_op_expiry` (expiry = scheduled day since 1936.1.1 + 45
grace). 75 active operations, 5 invaders (AST 5, ENG 6, GER 4, JAP 30, USA 30) at generation time.

Monthly, each AI invader on the historical difficulty (`WA_AI_DIFFICULTY_is_historical` - the same
gate the calendar events carry) at war walks its pending ops. Target = CURRENT controller of the
anchor state - dynamic geography, never a stored tag: a fallen France reserves GER, a Torch against
an unconquered Vichy reserves VIC, and an ahistorical world reserves whoever actually holds the
anchor. If the target is at war with the invader, a timed flag
`WA_AI_LANDING_reserved_for_<TAG>` (lease 50 days > the 31-day pulse gap) is stamped ON THE TARGET
for the invader and every AI faction member. The lease renews while any op against that target is
pending and dies by itself within one lease of the last scheduled operation - which is the requested
"until the date of the last scripted invasion", to a bounded tail: t0 stamp, t+31 re-stamp, t+50
expiry after the final pulse that still saw a pending op.

The consumer is one Default-layer block, `invasion_unit_request value = -200` with
`country_trigger = { has_country_flag = WA_AI_LANDING_reserved_for_@FROM }` (country_trigger scope =
enemy country, FROM = the evaluating country - `documentation.info` section `front_unit_request /
invasion_unit_request`). Same -200 magnitude and same base assumption as sec.10: ASSUMED it floors
the request at zero; a deliberate Faction-layer site boost (`WA_AI_MILITARY_ALLIES_dday_prep_INVASION`
+1000 on the Normandy states) still outranks it, which is intended - the scripted operation's own
staging must survive its own reservation.

**Epoch.** Day arithmetic uses the engine's `global.num_days` (install
`dynamic_variables_documentation.md`, global scope) minus `global.WA_AI_LANDING_epoch`, calibrated at
startup to 1936.1.1 (the Blitzkrieg 1939.8.14 bookmark backdates by 1321 days; a third bookmark
needs its own branch in `WA_AI_LANDING_init_reservations`).

**Stated ASSUMED, and how a campaign falsifies it.** (a) `@FROM` dynamic-flag rendering inside an
ai_strategy `country_trigger` - vanilla idiom in decisions (`WTT_border_conflict_*_@FROM`), no other
ai_strategy user in this repo; if inert, saves show `wa_tlm_resv_stamp_n > 0` and the reservation
flags on targets while the faction still opens engine invasions against them. (b) -200 floors the
request - inherited from sec.10, still unmeasured. PDXScript fails silently; the probe row in the
telemetry doc names both.

**Timing residuals, tabulated (AGENTS rule f) - monthly pulse (31d max gap) vs lease 50 vs grace 45:**

| Case | t0 | t1 | t2 | Residual |
| --- | --- | --- | --- | --- |
| Nominal | pulse stamps (op pending) | every following pulse re-stamps | last pulse with a pending op: last-scheduled-day + 45 grace | flag dies alone <= 50d after t2 -> reservation ends <= 95d after the last scheduled date |
| Op fires LATE (preconditions unmet > 45d past schedule) | schedule passes | grace passes, reservation lapses | op still refires weekly and may land later | UNPROTECTED window between t1 and the landing - accepted: post-landing the sec.10 freeze takes over, and the reservation's purpose (do not park divisions in advance) matters before the schedule, not after |
| Op succeeds EARLY in its window | landing executes | ops against that target all past -> pulses stop stamping | — | suppression lingers <= last-stamp + 50d on a target that may already be half-conquered - harmless: engine invasions of a collapsing enemy resume within the lease |
| Target changes controller between pulses | stamp on old controller | next pulse (<= 31d) stamps the new controller | old lease expires <= 50d after t0 | <= 50d of stale reservation on the old controller |
| Country joins the faction mid-war | — | next pulse (<= 31d) stamps its flag | — | <= 31d without protection for the newcomer |

**Scheduled, not fired.** Expiry keys on the calendar's SCHEDULED day, never on whether the KDE event
actually fired - script cannot see a hidden event's execution short of hooking `spawn_invasion`, and
the two accepted residuals above (late-firing, early-success) are exactly the cost of that choice.

**Resumed saves.** `on_startup` does NOT re-fire when a savegame is loaded (MEASURED - lessons-log
entry of that name), so the loader runs once at NEW-GAME creation and everything persists in the
save thereafter. ACCEPTED consequence: a campaign saved on a build without this system never
initializes it - inert for that campaign, fingerprint = `wa_tlm_resv_*` absent. No migration path
on purpose; the mis-dated-epoch scenario (init running mid-campaign) cannot occur for the same
reason.

**What this supersedes eventually, not yet.** The hand-dated Allied holds
(`WA_AI_MILITARY_ALLIES_dday_hold`, `_no_italy_invasion_early_INVASION`,
`_norway_invasion_hold_INVASION`) express the same intent for three specific cases with literal
dates. They stay untouched - retiring them is its own subject with its own impact analysis, recorded
in WORK.md, not a side effect of this one.
