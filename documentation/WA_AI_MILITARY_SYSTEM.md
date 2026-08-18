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
| Front | `_FRONT` | `front_unit_request`, `front_control`, `front_armor_score`, `force_concentration_front_factor`, `force_concentration_target_weight`, `force_ratio`, `infantry`, `garrison` (small/normal cases) |
| Invasion | `_INVASION` | `invasion_unit_request`, `invade`, `naval_invasion_focus` |
| Naval | `WA_AI_NAVAL_*` | `naval_avoid_region`, `naval_convoy_raid_region`, `naval_dominance`, `naval_mission_threshold`, `strike_force_home_base`, `naval_invasion_dominance_weight`, `naval_invasion_support_priority`, `strategic_air_importance` (when the rule is sea-facing) |
| Air | `_AIR` | `strategic_air_importance` (when the rule is land-theatre-facing). **The type ranks regions for the planes the engine already requests; it does not create demand** — requests come from own combats/armies, enemy planes in a combat region, enemy factories, ships (verified `a232d96c`, checklist R15 RECUT 2026-08-16), so a pull decides where wanted planes go and cannot stage an air force ahead of the ground war. **The demand side is the `NDefines.NAI` air block of `common/defines/05_defines.lua`, and WA overrides it.** Since 2026-08-18 that includes two request FLOORS: `NAVAL_MIN_EXCORT_PLANES = 100` (vanilla **0** - a floor where the engine had none) and `LAND_COMBAT_MIN_EXCORT_PLANES = 200` (vanilla **80**), alongside the older `STR_BOMB_MIN_EXCORT_PLANES = 500` (vanilla 200), `LAND_COMBAT_CAS_PER_COMBAT = 300` (vanilla 60) and `LAND_COMBAT_BOMBERS_PER_LAND_FORT_LEVEL = 30` (vanilla 6). A define is **global**: unlike an `ai_strategy` type it reaches every country at engine cadence and cannot be gated, so it is the wrong instrument whenever a type would do. None of these numbers is campaign-calibrated - they are **ASSUMED**. Generic theatre pulls live in `WA_AI_MILITARY_DEFAULT_AIR_theatres.txt`; coalition policy in `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt` — the Reich ladder (gated on deployed strategic-bomber count rather than dates) and, since Phase 7d, the whole former ENG.txt Allied family (Channel-coast push/avoidance, Sicily push, home-islands threat/lost, occupied-Europe and out-of-theatre avoidance) gated on `WA_AI_MILITARY_is_allies_member` plus state triggers (staging armies, footholds, human enemy on the far shore) instead of tag lists and dates — all switches in `WA_AI_MILITARY_triggers.txt`; Phase 7e did the same for the GER.txt family: Axis-wide avoidance (front not open, unfronted France, British Isles outside the Battle-of-Britain window) in `WA_AI_MILITARY_FACTION_AXIS_AIR.txt`, the Reich air-defence pull in `WA_AI_MILITARY_COUNTRY_GER_AIR.txt` (the +100k schwerpunkt push was not carried over: the +50k contested pull composed with the -40k unfronted-France suppression already yields the north/south differential); contest detection in `WA_AI_MILITARY_AIR_theatre_contested_*` (`WA_AI_MILITARY_triggers.txt`). The companion state-membership triggers `WA_AI_MILITARY_AIR_theatre_state_*` (same file, must-match the contested lists) feed `WA_AI_build_theatre_air_bases` in the construction system, which builds the air-base capacity the pulls need — a pull with no friendly basing in range is inert. |
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
| `infantry` | **I** - Sums | Additive | n/a | 0 to 100 |
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
| `naval_invasion_support_priority` | **I** - Sums per region | Additive per region | n/a | 0 to +100 |
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
**50 slugs, all 50 read by at least one `ai_strategy` block, zero orphans** (measured 2026-08-18).

There are two mechanisms in play, and they are not interchangeable.

### 6.1 The engine's own precedence field - `front_control` only

`front_control` carries a native integer: `priority = 0  # Default 0, higher prio strats will
override lower` (`common/ai_strategy/documentation.info` section `front_control`). It is the only
Exclusive type in this mod's vocabulary that has one - `protect`, `ignore`, `ignore_claim`,
`contain`, `naval_invasion_focus`, `strike_force_home_base`, `dont_defend_ally_borders` and
`force_defend_ally_borders` have no `priority` parameter in either documentation edition. That is
why the scripted gates cannot be replaced by the engine field: they carry 43 of their 50 slugs for
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
| Tag-free triggers (control panel) | `WA_AI_MILITARY_triggers.txt`: `WA_AI_MILITARY_is_italian_homeland_power` (owns AND cores any of the 15 mainland + Sicily states - Sicily/south included because the Fall Achse transfer can leave the co-belligerent ITA owning nothing north of Naples), `_italy_homeland_invaded`, `_italy_home_threatened` (invaded, or owned island / Adriatic-gate ground enemy-held - Sardinia, Corsica, Dodecanese, Istria, Primorska; not Albania/Zadar - or both shores of the Sicilian strait enemy-held: Tunisia 458+1061 AND Malta 116; never a lone pre-war holding), `_ally_italy_at_war` / `_theatre_threatened` / `_invaded` (walk `any_allied_country` AND `any_subject_country` - the RSI is a German subject, never a faction member), `_allied_with_` / `_at_war_with_italian_homeland_power`, `_libya_bridgehead_held` (own / subject port; an ally's port only while an enemy holds East Egypt or Tunisia - so ENG's Libya is not the co-belligerent's bridgehead), `_ethiopian_war_finished` (no Italy is in a colonial ETH war fought against no major; evaluated over `any_country` so allies read the same answer) |
| Owner (Region layer, whichever tag is an Italy: ITA on either side of its flip, RIT, a civil-war Italy) | `WA_AI_MILITARY_REGION_ITALY_THEATRE.txt` (floor / threatened buffers + `area_priority`), `WA_AI_MILITARY_REGION_ITALY_FRONT.txt` (`front_unit_request` +200 on 238/23/21 and careful `front_control` while invaded). Replaces `COUNTRY_RIT_FRONT` (deleted). Gates live in `enable`, never `allowed` - `allowed` is evaluated at country creation, before a released RIT owns anything |
| Owner's Africa effort (Country ITA) | `WA_AI_MILITARY_COUNTRY_ITA_THEATRE.txt`: one +200 while a Libyan port is held and home is safe, +50 when threatened, -200 when no port is held or the mainland is invaded (three stacked +200s and the "all four Libyan states lost" switch are gone); the R13 pair aborts on the geographic threat instead of `surrender_progress` |
| Ally guard (Faction AXIS) | `WA_AI_MILITARY_FACTION_AXIS_THEATRE.txt` `AXIS_italy_theatre_guard_THEATRE` / `_invaded_THEATRE` (0.06 / 0.12 buffers on the 15 states, own order_id, `subtract_fronts_from_need = no`), `WA_AI_MILITARY_FACTION_AXIS_FRONT.txt` `AXIS_italy_theatre_guard_FRONT` (+150) and `AXIS_hold_italy_after_defection_FRONT` (at war with an Italy). Replaces GER `fall_achse_a/b/c`, `protect_our_weak_underbelly`, `frontline_requests_6` (deleted); the Fall Achse political chain is untouched |
| Allied side | `avoid_italy_overstack(_after_flip)`, `italy_cobelligerent_support_FRONT`, `ENG_war_against_ITA_3_DIPLOMACY` (gated `ally_italy_at_war` - the commitment starts the day the co-belligerent fights, not at the first lost state), `USA_sicily_push`, `ALLIES_sicily_push_FRONT` re-gated on the same triggers; the date-boxed Husky family is out of scope |
| Probe | checklist R61, `WA_TLM_r96_italy_*` (telemetry doc 5) |

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
| Probe | checklist R62, `WA_TLM_r97_ea_*` |

`NOT = { A B C }` is a **NOR** in PDXScript (see the lessons log) - the `africa_war_2` gate had been `OR{A B C} AND NOT{A B C ...}` since its first authoring. Post-code review (2 angles) fixed: minors/continental archetypes not re-adding the alias, the viable trigger's anchors and bar, THEATRE +100, RAJ conquer split, the buffer's `area`.

**Engine limit found by the owed boot test (2026-08-17, HOI4 1.19.2):** the effective global `ai_area` ceiling is 72 definitions. `default.txt` defines 67; the parent plus 4 WA aliases (71) booted, either new Fix 97 alias alone (72) booted, and both together (73) crashed with C0000005 in `ai_area.cpp` while strategy data loaded. Renaming the sixth alias, changing its regions, making them disjoint and disabling its readers did not change the result. Remediation: remove the unreferenced India alias; replace the custom Italy alias with the default `italy` area, which has the same {21,23} membership; replace the former Southeast-Asia sink area with `WA_AI_MILITARY_is_southeast_asia_sink_state` in its nine `front_unit_request` readers; spend that slot on the two-reader corridor baseline alias. Current `WA_AI_MILITARY_areas.txt` still has 5 definitions (72 total). This exact composition passed AI-strategy and on-action loading with no related `error.log` entry or crash report. It preserves the independently addressable four-region theatre, corridor baseline and colony buffer. `tests/wa_ai_military_strict_parity.txt` encodes the state-scope assertion for one state in each of regions 142/167/196/260/340 plus a Northern-France rejection; the bundle still needs an in-game test run, and campaign R62 owns the remaining area-vs-state-trigger aggregation risk. Re-test the 72/73 boundary after engine upgrades.

---

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
