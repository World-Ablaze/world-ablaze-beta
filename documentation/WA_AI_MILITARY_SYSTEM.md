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
| Air | `_AIR` | `strategic_air_importance` (when the rule is land-theatre-facing). Generic theatre pulls live in `WA_AI_MILITARY_DEFAULT_AIR_theatres.txt`; coalition bombing-campaign policy in `WA_AI_MILITARY_FACTION_ALLIES_AIR.txt` (the Reich ladder, gated on deployed strategic-bomber count rather than dates — thresholds and rings in `WA_AI_MILITARY_triggers.txt`); contest detection in `WA_AI_MILITARY_AIR_theatre_contested_*` (`WA_AI_MILITARY_triggers.txt`). The companion state-membership triggers `WA_AI_MILITARY_AIR_theatre_state_*` (same file, must-match the contested lists) feed `WA_AI_build_theatre_air_bases` in the construction system, which builds the air-base capacity the pulls need — a pull with no friendly basing in range is inert. |
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

| Type | Engine combination | Policy | Precedence (if Exclusive) | Typical range |
| --- | --- | --- | --- | --- |
| `front_unit_request` | Sums per area | Additive | n/a | -1500 to +200 |
| `area_priority` | Sums per area | Additive | n/a | -200 to +200 |
| `theatre_distribution_demand_increase` | Sums per area | Additive | n/a | 0 to +500 |
| `force_concentration_factor` | Sums, added to define `AIFC_UNIT_RATIO_BASE` (0.15) | Additive | n/a | -100 (hard off) to +25, in percentage points |
| `force_concentration_front_factor` | Sums | Additive | n/a | -100 to +100 (plain percent) |
| `force_concentration_target_weight` | Sums per target | Additive | n/a | -100 to +100 (plain percent) |
| `front_armor_score` | Sums | Additive | n/a | 0 to +50 |
| `strategic_air_importance` | Sums per strategic region, on top of engine terms (own combats x100, own armies x25; hot main front ~35,000) | Additive | n/a | +10,000 standing theatre pull (DEFAULT_AIR); +100k to +500k emergency pushes; -250k to -1M suppressions |
| `garrison` | Max wins; large negatives force-off | Additive (with negative-override convention) | n/a | -5000 (force off) or 0 to 200 |
| `infantry` | Sums | Additive | n/a | 0 to 100 |
| `spare_unit_factor` | Sums | Additive | n/a | 0.0 to 1.0 |
| `front_control` | Per area, last-set wins per mode | **Exclusive per area** | Country > Faction > Default | mode enum |
| `protect` | Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `ignore` | Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `ignore_claim` | Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `contain` | Boolean per target | **Exclusive per target** | Country > Faction > Default | bool |
| `naval_invasion_focus` | Boolean | **Exclusive** | Country > Faction > Default | bool |
| `strike_force_home_base` | Boolean per region | **Exclusive per region** | Country > Faction > Default | bool |
| `dont_defend_ally_borders` | Boolean per ally | **Exclusive per ally** | Country > Faction > Default | bool |
| `force_defend_ally_borders` | Boolean per ally | **Exclusive per ally** | Country > Faction > Default | bool |
| `invasion_unit_request` | Sums | Additive | n/a | 0 to 50 |
| `invade` | Sums per target | Additive per target | n/a | 0 to 200 |
| `conquer` | Sums per target | Additive per target | n/a | 0 to 200 |
| `antagonize` | Sums per target | Additive per target | n/a | 0 to 200 |
| `naval_avoid_region` | Sums per region | Additive per region | n/a | -10000 to +2000 — see the convention note below |
| `naval_convoy_raid_region` | Sums per region | Additive per region | n/a | -1000 to +1000 (negative = suppress raiding there) |
| `naval_dominance` | Sums per region/area | Additive per region | n/a | 0 to 100 |
| `naval_mission_threshold` | Sums per mission | Additive | n/a | -100 to +100 |
| `naval_invasion_dominance_weight` | Sums | Additive | n/a | 0 to +100 |
| `naval_invasion_support_priority` | Sums per region | Additive per region | n/a | 0 to +100 |
| `put_unit_buffers` | Sums per state | Additive per state | n/a | 0 to 100 |
| `declare_war` | Sums per target | Country-only | n/a | 0 to 100 |
| `diplo_action_desire` | Sums per target/action | Country-only | n/a | 0 to 100 |
| `diplo_action_acceptance` | Sums per target/action | Country-only | n/a | 0 to 100 |

### Notes on the policy column

- **Additive** means the engine combines values from multiple `ai_strategy` blocks (typically by sum, sometimes by max). Layers may safely contribute to the same key. Tuning differences between layers are by design.
- **Exclusive** means the WA system enforces single-layer ownership for a given key (target, area, ally, region, mode). The engine may still technically allow multiple writers, but stacking writers produces unpredictable behaviour. Phase 5 will introduce mutual-exclusion triggers to enforce this; until then, authors must hold the precedence rule manually.
- `naval_avoid_region` **is signed, and a negative value is an attraction, not a weaker avoidance.** Reading only the region id will mislead you. Corrected 2026-08-14 (Fix 63): the range column previously read "0 to +500", which no file in the mod has ever respected. Measured across the 402 entries actually in `common/ai_strategy/`, the values in use are `2000` (326 entries), `1000` (29), `100` (23), `-1000` (18), `200` (3), `-2000` (2) and `-10000` (1). The working convention is therefore:

  | Value | Meaning |
  | --- | --- |
  | `100` – `200` | soft nudge; the AI still deploys there routinely |
  | `1000` | soft wall — the paired suppression half of a corridor plan |
  | `2000` | hard wall — "do not go here", the mod's default deterrent |
  | `-1000` | the pull half of a corridor plan (`WA_AI_NAVAL_FACTION_ALLIES` corridors) |
  | `-2000` / `-10000` | force a route open (USA Torch, `ENG_protect_home` on the Channel) |

  Because the type is Additive per region, **always sum every writer for a region before concluding what the AI will do** — a `-2000` "open this route" can be, and in the Bay of Biscay case is, silently outvoted by three `+2000` walls. `WA_AI_NAVAL_COUNTRY_USA_operation_torch_preparation` carries a worked example of that arithmetic in its header comment.
- `naval_dominance` values in use are 70–80 (18 entries), well inside the documented 0–100. Sums may still exceed 100 when layers stack; that is legal but should be called out at the site.
- `garrison` uses a **negative-override convention**: a single block of `value = -5000` is the documented way to force garrison off in a state, and is treated as authoritative regardless of other writers. This is how `WA_AI_MILITARY_COUNTRY_SPR.txt:143-144` disables garrison in a specific configuration.
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
5. **Do not duplicate behaviour across layers.** If a Default rule and a Country rule cover the same intent, the Country rule should either differ meaningfully (Additive types) or replace the Default rule under Phase 5 mutual-exclusion (Exclusive types). For Phase 1, document the duplication in `WA_AI_MILITARY_TYPES_REFERENCE.md` rather than fixing it.
6. **Country-specific blocks living in faction files must be re-homed** to `WA_AI_MILITARY_COUNTRY_<TAG>_<DOMAIN>.txt` during Phase 2-4. Until then, keep them where they are but flag them in the types reference.

---

## 6. Mutual exclusion mechanism (preview, deferred to Phase 5)

For Exclusive-policy types, pairs of scripted triggers will guard layers so that the Country layer takes precedence over Faction, and Faction over Default, on a per-key basis (per target, per area, per ally, per region, per mode):

- `WA_AI_MILITARY_country_owns_<exclusive_key> = yes` - Country layer asserts ownership of this key.
- Faction blocks add `NOT = { WA_AI_MILITARY_country_owns_<exclusive_key> = yes }` to their `enable`.
- Default blocks add both `NOT = { WA_AI_MILITARY_country_owns_<exclusive_key> = yes }` and `NOT = { WA_AI_MILITARY_faction_owns_<exclusive_key> = yes }`.

Additive types are never gated by these triggers. Phase 5 will define the exact set of `<exclusive_key>` slugs and generate the trigger pairs; Phase 1 only commits to the contract.

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
`invasion_unit_request` is the only one accepting a geographic scope (`documentation.info:250-266` -
`tag` / `state` / `strategic_region` / `area` / `country_trigger` / `state_trigger`, tested against the
invasion **target**) and the only one that throttles what an invasion order may request rather than which
country looks attractive. `state_trigger` acceptance on this type is established in-repo -
`WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt:442`.

**Value is -200, deliberately.** The type is Additive over a base of 100, so -200 already floors the
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
