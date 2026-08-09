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

| Type | Engine combination | Policy | Precedence (if Exclusive) | Typical range |
| --- | --- | --- | --- | --- |
| `front_unit_request` | Sums per area | Additive | n/a | -1500 to +200 |
| `area_priority` | Sums per area | Additive | n/a | -200 to +200 |
| `theatre_distribution_demand_increase` | Sums per area | Additive | n/a | 0 to +500 |
| `force_concentration_factor` | Sums, added to define `AIFC_UNIT_RATIO_BASE` (0.15) | Additive | n/a | -100 (hard off) to +25, in percentage points |
| `force_concentration_front_factor` | Sums | Additive | n/a | -100 to +100 (plain percent) |
| `force_concentration_target_weight` | Sums per target | Additive | n/a | -100 to +100 (plain percent) |
| `front_armor_score` | Sums | Additive | n/a | 0 to +50 |
| `strategic_air_importance` | Sums per area | Additive | n/a | 0 to +500 |
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
| `naval_avoid_region` | Sums per region | Additive per region | n/a | 0 to +500 |
| `naval_convoy_raid_region` | Sums per region | Additive per region | n/a | 0 to +500 |
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
| Consumers (Faction layer) | `WA_AI_MILITARY_ALLIES_exec_vs_germany` / `_grind_vs_germany` and `WA_AI_MILITARY_ALLIES_downfall_push_FRONT` (ALLIES), `WA_AI_MILITARY_AXIS_exec_vs_sov` / `_grind_vs_sov` (AXIS), `WA_AI_MILITARY_CHINA_FRONT_exec_vs_japan` / `_grind_vs_japan` (CHINA_FRONT) |
| Consumers (Country layer) | `WA_AI_MILITARY_SOV_counterattack` (SOV vs GER), `WA_AI_MILITARY_JAP_chinese_war_4` + the posture-0 fallback in `_chinese_war_3` (JAP vs CHI) |
| Consumers (Default layer) | `WA_AI_MILITARY_EXEC_low_equipment_hold` |

Published state per AI country: `WA_AI_MILITARY_posture` (0 = hold, 1 = execute, 2 = attrition grind),
`WA_AI_MILITARY_posture_vs_<TAG>` per major enemy, and the `WA_AI_AIFC_hold_the_line` flag while the hard
brake is engaged (which also drops AIFC into linear defence). Level 1 keys on
`fighting_army_strength_ratio` (the engine's quality-weighted estimate) OR on the front-local branch:
the divisions our side actually has standing on the shared contact line outweigh the enemy divisions
across it by 1.5x (banded `divisions_in_state` counting, armour double-weighted; skipped when the
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
