# WA AI Military Types Reference

Per-`type` migration TODO list. Companion to `WA_AI_MILITARY_SYSTEM.md`. Read the system doc first for layer/domain/policy definitions.

## Canonical TYPE \u2192 DOMAIN mapping (post-Phase 6)

This is the **single source of truth** for which `_DOMAIN.txt` file every `ai_strategy` block belongs in. The `tools/wa_ai_military_phase6_domain_split.py` tool encodes this same table in its `CANONICAL_DOMAIN` dict; if the two diverge, the tool wins and this table must be updated to match.

| `type =` value | Domain | File suffix | Rationale |
| --- | --- | --- | --- |
| `front_unit_request` | FRONT | `_FRONT` | Sizes division allocation against an enemy front. |
| `front_control` | FRONT | `_FRONT` | Per-area passive/active mode for an existing front. |
| `front_armor_score` | FRONT | `_FRONT` | Front-line armour scoring. |
| `force_concentration_front_factor` | FRONT | `_FRONT` | Front allocator concentration tuning. |
| `force_concentration_target_weight` | FRONT | `_FRONT` | Front allocator target weighting. |
| `force_ratio` | FRONT | `_FRONT` | Front allocator ratio bias. |
| `infantry` | FRONT | `_FRONT` | Infantry-specific front bias. |
| `garrison` | FRONT | `_FRONT` | Occupation force sizing. May move to `_GARRISON` if a country has many entries (currently none do). |
| `invasion_unit_request` | INVASION | `_INVASION` | Sizes the amphibious-invasion division pool. |
| `invade` | INVASION | `_INVASION` | Picks invasion targets. |
| `naval_invasion_focus` | INVASION | `_INVASION` | Invasion-precondition flag (boolean per target). |
| `naval_avoid_region` | NAVAL | `_NAVAL` | Sea regions the fleet should avoid. |
| `strike_force_home_base` | NAVAL | `_NAVAL` | Designates a base as fleet home. |
| `strategic_air_importance` | NAVAL | `_NAVAL` | Strategic air emphasis (sea-facing). |
| `conquer` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: targets to subdue. |
| `antagonize` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: increase friction. |
| `protect` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: prioritise survival of an ally. |
| `contain` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: contain expansion. |
| `ignore` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: do not model as a threat. |
| `ignore_claim` | DIPLOMACY | `_DIPLOMACY` | Inter-country posture: do not press claim. |
| `declare_war` | DIPLOMACY | `_DIPLOMACY` | Country-only war declaration nudge. |
| `diplo_action_desire` | DIPLOMACY | `_DIPLOMACY` | Country-only diplomatic action weighting. |
| `diplo_action_acceptance` | DIPLOMACY | `_DIPLOMACY` | Country-only diplomatic action acceptance. |
| `dont_defend_ally_borders` | DIPLOMACY | `_DIPLOMACY` | Per-ally umbrella opt-out. Addressed by `id = <ally>`; expresses a stance toward an ally rather than sizing a front against an enemy. Grouped with `protect`/`ignore`/`force_defend_ally_borders` for the same reason. |
| `force_defend_ally_borders` | DIPLOMACY | `_DIPLOMACY` | Per-ally umbrella commitment. Same rationale as above. |
| `theatre_distribution_demand_increase` | THEATRE | `_THEATRE` | Coarse-grained regional emphasis. |
| `area_priority` | THEATRE | `_THEATRE` | Per-area priority (above the front allocator). |
| `put_unit_buffers` | THEATRE | `_THEATRE` | Per-state unit buffer reservations. |
| `spare_unit_factor` | THEATRE | `_THEATRE` | Strategic-reserve factor. |

Domain definitions:

- **FRONT**: how divisions are deployed along **existing** land borders. The front allocator's input set.
- **INVASION**: how the AI **creates new fronts** via amphibious assault. Pre-invasion staging through post-landing buildup.
- **NAVAL**: where the fleet operates, what it avoids, where it stages. Sea-domain emphasis.
- **DIPLOMACY**: posture toward **specific other countries** (allies or enemies, addressed by `id =` or `tag =`). Not the same as front sizing even when the eventual effect is on division placement.
- **THEATRE**: coarse-grained regional emphasis - which map-theatre to weight, per-state pooling, strategic reserves.
- **GARRISON**: per-state occupation force sizing for already-conquered territory. Currently rolled into FRONT; promoted to its own file only if a country has enough garrison rules to warrant it.

Note: `dont_defend_ally_borders` and `force_defend_ally_borders` operate on division placement (FRONT-domain mechanism) but express a stance toward an ally (DIPLOMACY-domain intent). Phase 6 routes them to DIPLOMACY for consistency with `protect`/`ignore` and because they are addressed by ally `id =`, the diplomacy-grammar form. See `WA_AI_MILITARY_SYSTEM.md` \u00a73 for the broader convention.

---

## Per-type migration history (Phase 1 snapshot, kept for reference)

This was a **snapshot** of `common/ai_strategy/WA_AI_MILITARY_*.txt` at the time of Phase 1. Counts have drifted across Phases 2-6. Regenerate current counts by running:

```powershell
python tools/wa_ai_military_phase6_domain_split.py audit
```

## Inventory summary (Phase 1)

- 45 source files
- 28 distinct `type =` values
- 1791 total `ai_strategy` blocks

## Per-type table

For each type: total count, where it currently appears (counts per file), recommended target layer(s), and open questions or known issues.

### `front_unit_request` (469)

- Currently in: `FRONT_archetypes` (15), `FRONT_caps` (12), `FRONT_core` (4), every COUNTRY file with front content (USA 27, GER 84, SOV 60, AXIS 58, ALLIES 38, ENG 33, JAP 19, FRA 17, FIN 14, RAJ 13, CHI 12, CAN 12, RCZ 10, TUR 9, AST 6, ITA 6, PRC 5, GRE 3, RIT 3, CHINA_FRONT 3, ROM 1, SAF 1, NZL 1, POL 1, SPR 1).
- Target: Default for archetype/cap rules; Faction for coalition front shape; Country for tag-specific theatre adjustments.
- Notes: largest type by volume. Phase 4 should pull recurring patterns (e.g. minor-country front floors) out of country files into Default.

### `dont_defend_ally_borders` (228)

- Currently in: AXIS 59, SOUTH_AMERICA 46, ALLIES 28, GER 22, ITA 13, RCZ 11, USA 7, ENG 6, AST 3, CAN 1, CZE 3, FIN 3, CHI 3, CHINA_FRONT 2, BUL 1, POL 1, PRC 1, SIK 1.
- Target: Faction for intra-faction defaults; Country for overrides; Region for stay-at-home patterns (SOUTH_AMERICA).
- Policy: **Exclusive per ally**. Phase 5 must add `WA_AI_MILITARY_country_owns_dont_defend_<ALLY>` triggers.
- Open issue: AXIS file's 59 entries likely target specific allies and may need re-homing to country files in Phase 2.

### `front_control` (208)

- Currently in: GER 25, CHI 19, JAP 19, SOV 18, USA 17, AXIS 14, CAN 14, SPA 10, ITA 10, CHINA_FRONT 6, FIN 3, FRA 3, CZE 3, ALLIES 32, ENG 2, TUR 2, GRE 2, ROM 1, SAF 1, YUG 1, RAJ 1, SPR 4, FRONT_execution 1.
- Target: Default for the global passive/active baseline; Country for per-area overrides.
- Policy: **Exclusive per area**. Phase 5 mutual-exclusion needed.

### `invade` (197)

- Currently in: ALLIES 62, USA 54, JAP 25, SOUTH_AMERICA 19, GER 14, AST 6, ENG 4, GRE 4, SOV 4, GER 14, ITA 1, MAN 1, AXIS 1, RCZ 2, RAJ 0, CHINA_FRONT 0.
- Target: Faction for shared invasion targets; Country for tag-specific overrides.
- Notes: SOUTH_AMERICA's 19 `invade` entries are flagged for Region layer - check whether they are stay-home suppressors (negative values) or actual invasion targets.

### `put_unit_buffers` (150)

- Currently in: SOV 34, USA 21, ENG 17, GER 13, CHI 11, RAJ 9, ITA 6, FRA 5, FIN 3, AST 3, CAN 3, ALLIES 3, RCZ 6, JAP 6, MAN 2, RNC 2, SPR 1, MAL 1, GRE 1, HOL 1, POR 1, TUR 1.
- Target: Country (THEATRE domain). Faction layer should not set state-level buffers.
- Notes: high-volume per-state config. Candidate for tooling-assisted generation in a future phase.

### `area_priority` (124)

- Currently in: GER 20, SOV 19, JAP 17, ENG 15, USA 14, MAN 11, ITA 9, ALLIES 9, FRA 5, AXIS 2, CAN 1, RAJ 1, SAF 1.
- Target: Country (THEATRE domain) primarily; Faction for coalition focus.

### `naval_avoid_region` (91)

- Currently in: USA 67, RCZ 11, MAN 5, ALLIES 4, ENG 2, GER 2.
- Target: Country (NAVAL domain).
- **Known issue:** USA's 67 `naval_avoid_region` blocks are a candidate for tooling-assisted generation (one block per region, repetitive structure). Track for a Phase 4+ generator under `tools/`.

### `force_defend_ally_borders` (74)

- Currently in: ENG 14, CHINA_FRONT 13, USA 13, ITA 7, AXIS 3, FRA 3, CAN 3, JAP 2, MAN 2, SIA 2, FIN 0, AST 0, ALLIES 1, HUN 1, PRC 1, SAF 1, CHI 3, RAJ 3, COUNTRY_AXIS 3.
- Target: Faction for coalition defence patterns; Country for per-ally overrides.
- Policy: **Exclusive per ally**. Phase 5 mutual-exclusion needed.

### `conquer` (49)

- Currently in: SOV 13, JAP 12, ALLIES 4, USA 4, GER 3, FRA 2, SIA 3, ITA 2, AXIS 1, RAJ 1, HUN 1, CHINA_FRONT 1, PRC 1, MAN 1.
- Target: Country (DIPLOMACY domain). Faction may set bloc-wide conquer targets but most uses are country-specific.

### `invasion_unit_request` (42)

- Currently in: ALLIES 15, JAP 10, USA 7, GER 7, SOV 1, INVASION_budget 2.
- Target: Default for the global baseline (`INVASION_budget` -> `DEFAULT_INVASION`); Faction for coalition-wide modifiers (e.g. ALLIES); Country for tag-specific tuning.
- Policy: **Additive**. Multiple layers may contribute; the engine sums. ALLIES file's 15 entries can stay at the Faction layer when re-homed in Phase 2 (renamed to `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`).

### `garrison` (38)

- Currently in: FRA 15, GER 4, USA 4, SOV 4, ENG 2, ITA 2, RAJ 2, FIN 1, JAP 1, CHI 1, SPR 1, FRONT_archetypes 1.
- Target: Default for archetype floor (`FRONT_archetypes`); Country for state-specific overrides; `_GARRISON` domain file when a country has many garrison rules (FRA at 15 is the candidate).
- **Known issue:** `WA_AI_MILITARY_COUNTRY_SPR.txt:143-144` uses the documented `value = -5000` force-off override. Preserve this pattern when migrating; do not collapse it into a regular garrison entry.

### `infantry` (34)

- Currently in: ALLIES 28, FRA 6.
- Target: Faction for ALLIES (FRONT domain) and Country for FRA.

### `front_armor_score` (20)

- Currently in: SOV 13, GER 7.
- Target: Country (FRONT domain). Possibly Default for major-continental archetype if pattern repeats elsewhere in Phase 4.

### `strategic_air_importance` (18)

- Currently in: GER 8, ALLIES 4, ITA 3, ENG 2, SOV 1.
- Target: Country (NAVAL or FRONT depending on whether the rule is sea-facing).

### `antagonize` (8)

- Currently in: JAP 3, MAN 1, AXIS 1, SIA 2, ITA 1.
- Target: Country (DIPLOMACY domain). The single AXIS entry should be re-homed.

### `naval_invasion_focus` (6)

- Currently in: JAP 6.
- Target: Country (INVASION domain).
- Policy: **Exclusive**. Single owner today (JAP), so no current conflict.

### `theatre_distribution_demand_increase` (5)

- Currently in: USA 1, ENG 1, JAP 1, SOV 1, ALLIES 1.
- Target: Country (THEATRE domain) for tag-specific; Faction for ALLIES.

### `ignore` (5)

- Currently in: FRA 2, ITA 1, GER 2.
- Target: Country (DIPLOMACY domain).
- Policy: **Exclusive per target**.

### `force_concentration_target_weight` (5)

- Currently in: GER 4, FRA 1.
- Target: Country (FRONT domain).

### `protect` (4)

- Currently in: USA 1, ENG 1, JAP 2.
- Target: Country (DIPLOMACY domain).
- Policy: **Exclusive per target**.

### `strike_force_home_base` (4)

- Currently in: ITA 4.
- Target: Country (NAVAL domain).
- Policy: **Exclusive per region**.

### `contain` (3)

- Currently in: ALLIES 2, USA 1.
- Target: Faction (DIPLOMACY) for ALLIES; Country for USA.
- Policy: **Exclusive per target**.

### `spare_unit_factor` (2)

- Currently in: USA 1, CHINA_FRONT 1.
- Target: Country (THEATRE domain) for USA. The CHINA_FRONT entry sits inside `WA_AI_MILITARY_CHINA_FRONT_sic_support_chi_against_japan` and is **country-specific** (gated by `tag = SIC`); see "Cross-cutting issues" below.

### `force_concentration_front_factor` (2)

- Currently in: GER 1, FRA 1.
- Target: Country (FRONT domain).

### `declare_war` (2)

- Currently in: GER 1, ITA 1.
- Target: Country only (DIPLOMACY domain).

### `diplo_action_desire` (1)

- Currently in: BUL 1.
- Target: Country only (DIPLOMACY domain).

### `diplo_action_acceptance` (1)

- Currently in: BUL 1.
- Target: Country only (DIPLOMACY domain).

### `ignore_claim` (1)

- Currently in: ITA 1.
- Target: Country (DIPLOMACY domain).
- Policy: **Exclusive per target**.

---

## Phase 4 audit: cross-layer duplication is mostly by-design

Phase 4 was originally scoped to "consolidate cross-layer duplicates" — i.e. find cases where the same `(type, key)` block appears in DEFAULT/REGION/FACTION/COUNTRY and lift the duplicate to the highest shared layer. A scan across the 94 post-Phase-3 ai_strategy files (1826 indexed `ai_strategy = {}` blocks) found 153 cross-layer `(type, key)` groups. Closer inspection showed the headline number is misleading.

### Breakdown of the 153 cross-layer groups

| Type | Groups | Engine policy | Phase 4 actionable? |
| --- | --- | --- | --- |
| `dont_defend_ally_borders` | 58 | Exclusive per ally (highest value wins) | No - distinct rules from distinct sources targeting the same ally |
| `front_unit_request` | 35 | Additive | No - sums are intended |
| `invade` | 32 | Additive per target | No |
| `front_control` | 7 (128 instances) | Exclusive per area | Cannot be safely auto-deduped (see below) |
| `area_priority` / `put_unit_buffers` / `conquer` / `naval_avoid_region` / `strategic_air_importance` / `invasion_unit_request` / `garrison` / `spare_unit_factor` | 13 total | Additive | No |
| `force_defend_ally_borders` | 4 | Exclusive per ally | Reviewed; gates are meaningfully distinct |
| `contain` | 1 | Exclusive | Reviewed; legitimate |

### Why mechanical de-dup does not apply

1. **Cross-layer Exclusive entries are not duplicates.** For example, `dont_defend_ally_borders id = FIN` appears in 15 distinct blocks across REGION/FACTION/COUNTRY. They are gated on different sources (e.g. `BUL_stay_out_of_finland`, `GER_army_group_finland_does_not_exist`, `AXIS_hungary_stop_crowding_up_the_soviet_line`, `SOUTH_AMERICA_stay_in_south_america`). Each is the right rule for its source country/region. The engine's "highest value wins" semantic correctly resolves overlap; merging them would either lose semantics or require conditional payloads that the `ai_strategy` DSL does not support.
2. **`ai_strategy` blocks are definitions, not effects.** They cannot be emitted from scripted effects (verified: zero `ai_strategy = {` occurrences in `common/scripted_effects/`). The only consolidation tool is collapsing the *outer* containing block by widening `allowed`/`enable` and accepting any per-tag tweaks as cross-cutting noise.
3. **Near-duplicate outer blocks have meaningful gate differences.** The 5-block `AXIS_*_stop_crowding_up_the_soviet_line` family is the closest candidate for collapse: all five share ~9 `dont_defend_ally_borders` entries plus ~4 `front_unit_request` entries. But each variant has at least one meaningful difference - Romania has an extra `NOT = { has_defensive_war_with = SOV ... }` clause, Bulgaria omits all `front_unit_request` and the `support_requested_by_germany` exclusion, Italy adds `crimea` plus ROM/BUL to the ally list, the "iberian" general variant uses a different gate. Forcibly merging them would either lose these differences or require complex conditional payloads.
4. **`front_control` cannot be safely auto-deduped.** All 128 instances collapse to `KEY=None` in the scanner because `front_control` is gated on embedded `country_trigger`/`state_trigger`/`ordertype` blocks rather than a top-level `id`/`area`/`target` field. The blocks are Exclusive-per-area in the spec, but mechanical overlap detection requires evaluating those embedded gates - this belongs to Phase 5 (mutual-exclusion triggers), not Phase 4.

### Decision

Phase 4 (cross-layer duplicate consolidation) is **closed without a refactor commit**. The cross-layer counts represent legitimately distinct rules from distinct sources, not duplication. The genuine overlap-management work moves to **Phase 5**, which adds mutual-exclusion triggers (e.g. `WA_AI_MILITARY_country_owns_ally_borders_directive_<TAG>`) for Exclusive types so multiple sources can be layered without silent override.

Scanner artifact: `phase4_dup_scan.py` and `phase4_report.md` (1826 blocks, 153 cross-layer groups) preserved in the agent scratch directory for reference.

---

## Cross-cutting issues to address in Phases 2-4

1. **`WA_AI_MILITARY_COUNTRY_SOUTH_AMERICA.txt` is misnamed.** It is a regional rule, not a country file. Phase 2 renamed it to `WA_AI_MILITARY_REGION_SOUTH_AMERICA.txt`. **Phase 3 added `WA_AI_CONFIG_MILITARY_is_south_american` to `WA_AI_CONFIG.txt`** and replaced the inline 31-tag OR-lists in both `allowed` and `enable` with the trigger.

2. **`WA_AI_MILITARY_COUNTRY_CHINA_FRONT.txt` was a faction file with embedded country-specific blocks.** Phase 2 split the file into `WA_AI_MILITARY_FACTION_CHINA_FRONT_<DOMAIN>.txt`. **Phase 3** then:
   - Moved `WA_AI_MILITARY_CHINA_FRONT_sic_support_chi_against_japan` (gated on `tag = SIC`) into the new `WA_AI_MILITARY_COUNTRY_SIC_DIPLOMACY.txt`.
   - Replaced the warlord OR-tag-list in `WA_AI_MILITARY_CHINA_FRONT_warlords_china_needs_you` with the new `WA_AI_CONFIG_MILITARY_is_chinese_warlord` trigger (excludes CHI/PRC/SHX, distinct from the existing `WA_AI_MILITARY_is_china_front_member` which includes them).
   - Replaced the all-China-states OR-tag-list in `WA_AI_MILITARY_CHINA_FRONT_all_warlords_support_china_in_war` with the existing `WA_AI_MILITARY_is_china_front_member` trigger.

3. **`WA_AI_MILITARY_COUNTRY_AXIS.txt`, `_ALLIES.txt`, `_COMINTERN.txt`, `_CO_PROSPERITY.txt`** were faction files mis-prefixed `COUNTRY_`. Phase 2 renamed them to `WA_AI_MILITARY_FACTION_<NAME>_<DOMAIN>.txt`. (Note: COMINTERN and CO_PROSPERITY were initially flagged as empty during Phase 1 inventory; they actually contain real `front_unit_request` content gated on the corresponding `WA_AI_MILITARY_is_<faction>_member` trigger.)

4. **`WA_AI_MILITARY_COUNTRY_ALLIES.txt`** contains 15 `invasion_unit_request` blocks. Since `invasion_unit_request` is Additive, these can stay at the Faction layer; Phase 2 just renames the file to `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt`.

5. **USA `naval_avoid_region` (67 blocks)** is the largest single repetitive pattern in the system. Phase 4 audit determined these are Additive and the duplication is by-design (per-region per-doctrine entries). No consolidation needed; revisit only if a per-region helper trigger emerges naturally.

6. **AXIS file's 59 `dont_defend_ally_borders` blocks.** Phase 2 split these across `WA_AI_MILITARY_FACTION_AXIS_*.txt` and `WA_AI_MILITARY_COUNTRY_*` files. Phase 4 audit confirmed the remaining FACTION-layer blocks (`AXIS_*_stop_crowding_up_the_soviet_line` family) have meaningfully distinct gates and cannot be safely merged. See "Phase 4 audit" section above.

7. **`WA_AI_MILITARY_FRONT_execution.txt`** carries a single `front_control` block. Rename to `WA_AI_MILITARY_DEFAULT_FRONT_control.txt` in Phase 2.

8. **`WA_AI_MILITARY_INVASION_budget.txt`** carries 2 default `invasion_unit_request` blocks. Rename to `WA_AI_MILITARY_DEFAULT_INVASION.txt` in Phase 2.

---

## Per-file summary (current state)

| File | Total blocks | Domain mix |
| --- | --- | --- |
| `WA_AI_MILITARY_FRONT_archetypes.txt` | 16 | FRONT |
| `WA_AI_MILITARY_FRONT_caps.txt` | 12 | FRONT |
| `WA_AI_MILITARY_FRONT_core.txt` | 4 | FRONT |
| `WA_AI_MILITARY_FRONT_execution.txt` | 1 | FRONT (control) |
| `WA_AI_MILITARY_INVASION_budget.txt` | 2 | INVASION |
| `WA_AI_MILITARY_COUNTRY_ALLIES.txt` | 231 | mixed (faction) |
| `WA_AI_MILITARY_COUNTRY_AXIS.txt` | 139 | mixed (faction) |
| `WA_AI_MILITARY_COUNTRY_COMINTERN.txt` | 0 | empty |
| `WA_AI_MILITARY_COUNTRY_CO_PROSPERITY.txt` | 0 | empty |
| `WA_AI_MILITARY_COUNTRY_CHINA_FRONT.txt` | 26 | mixed (faction + SIC) |
| `WA_AI_MILITARY_COUNTRY_SOUTH_AMERICA.txt` | 65 | DIPLOMACY+INVASION (region) |
| `WA_AI_MILITARY_COUNTRY_USA.txt` | 239 | mixed (all 5 domains) |
| `WA_AI_MILITARY_COUNTRY_GER.txt` | 219 | mixed |
| `WA_AI_MILITARY_COUNTRY_SOV.txt` | 168 | mixed |
| `WA_AI_MILITARY_COUNTRY_JAP.txt` | 124 | mixed |
| `WA_AI_MILITARY_COUNTRY_ENG.txt` | 99 | mixed |
| `WA_AI_MILITARY_COUNTRY_FRA.txt` | 76 | mixed |
| `WA_AI_MILITARY_COUNTRY_ITA.txt` | 67 | mixed |
| `WA_AI_MILITARY_COUNTRY_CHI.txt` | 49 | mixed |
| `WA_AI_MILITARY_COUNTRY_RCZ.txt` | 40 | mixed |
| `WA_AI_MILITARY_COUNTRY_CAN.txt` | 34 | FRONT+THEATRE+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_RAJ.txt` | 30 | mixed |
| `WA_AI_MILITARY_COUNTRY_FIN.txt` | 24 | FRONT+THEATRE |
| `WA_AI_MILITARY_COUNTRY_MAN.txt` | 23 | THEATRE+DIPLOMACY+NAVAL |
| `WA_AI_MILITARY_COUNTRY_AST.txt` | 18 | FRONT+INVASION+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_TUR.txt` | 12 | FRONT |
| `WA_AI_MILITARY_COUNTRY_SPA.txt` | 10 | FRONT |
| `WA_AI_MILITARY_COUNTRY_GRE.txt` | 10 | FRONT+INVASION |
| `WA_AI_MILITARY_COUNTRY_PRC.txt` | 8 | FRONT+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_SIA.txt` | 7 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_SPR.txt` | 7 | FRONT+THEATRE+GARRISON |
| `WA_AI_MILITARY_COUNTRY_CZE.txt` | 6 | FRONT+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_BUL.txt` | 4 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_SAF.txt` | 4 | FRONT+THEATRE |
| `WA_AI_MILITARY_COUNTRY_RIT.txt` | 3 | FRONT |
| `WA_AI_MILITARY_COUNTRY_HUN.txt` | 2 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_POL.txt` | 2 | FRONT+DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_RNC.txt` | 2 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_ROM.txt` | 2 | FRONT |
| `WA_AI_MILITARY_COUNTRY_HOL.txt` | 1 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_MAL.txt` | 1 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_NZL.txt` | 1 | FRONT |
| `WA_AI_MILITARY_COUNTRY_POR.txt` | 1 | THEATRE |
| `WA_AI_MILITARY_COUNTRY_SIK.txt` | 1 | DIPLOMACY |
| `WA_AI_MILITARY_COUNTRY_YUG.txt` | 1 | FRONT |
