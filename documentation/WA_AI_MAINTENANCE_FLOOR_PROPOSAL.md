# WA_AI maintenance floors — keeping a fielded park supplied

Status: **IMPLEMENTED, NOT COMMITTED** (2026-09-11). Revision 4, owner decision "B": the shortage
gate becomes a RATIO with `enable`/`abort` hysteresis, and armour moves from the `armor` type to
four chassis ARCHETYPES — both changes taken from Expert AI 5.0 (§2).

Files in the working tree:

| File | |
| --- | --- |
| `common/script_constants/wa_ai_production.txt` | new `maintenance` group, **7 numbers** |
| `common/scripted_triggers/WA_AI_PRODUCTION_maintenance_triggers.txt` | 60 triggers, 10 keys x 6 |
| `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_maintenance.txt` | 20 blocks, 10 keys x base/deep |
| `common/scripted_effects/WA_TEST_maintenance.txt` + `events/wa_test_maintenance.txt` | harness v1, namespace `wa_maint` |
| `common/scripted_effects/WA_TLM_core.txt` + `documentation/WA_TLM_TELEMETRY_SYSTEM.md` | probe `WA_TLM_r115_maint_*`, TLM v37 |

Gates: `check_constants` 0 error / 0 warning / 84 groups · `check_worklist` 0 ERROR ·
`check_ai_layers` unchanged from HEAD (same single pre-existing `NAME-COLLISION`, all six ratchets
identical) · `check_skill_refs` 0 dead · 60 triggers, no dangling reference, none unread.

**Owed before this can be committed** — all owner decisions, not code:

1. **Phase 0 not run.** The two engine facts of §7 are ASSUMED. `event wa_maint.3 <TAG>`, then the
   production panel.
2. **No `WORK.md` subject.** The checker's OPEN set already holds four (`air-budget`,
   `sov-conscription-oscillation`, `ger-labour-law`, `repeatable-pp-decisions`), so admitting
   `maintenance-floor` trips WIP-LIMIT unless one is parked.
3. **Probe r115 has no checklist item** (`WA_TLM_TELEMETRY_SYSTEM.md` §7.4).
4. **Sequencing.** `armor-prod-category` is PARKED awaiting a campaign probe on the armour lines;
   this ships onto the same lines.

---

## 1. What the system does

A small factory floor so a park the AI has stopped expanding still receives new equipment, and
therefore still **modernises**: at zero factories a mature park drives the chassis and fires the
guns it had when the line went quiet, for the rest of the campaign. That is the mechanism the air
lines already run (`WA_AI_PRODUCTION_air.txt` § MAINTENANCE), generalised to land.

**Two reasons a land park goes unsupplied, and they need different gates:**

| | Trigger | Keys |
| --- | --- | --- |
| **ARMOUR** | WA itself closes the lines — the class ladder, the era boundary, a fielded cap | `light_tank_chassis`, `medium_tank_chassis`, `heavy_tank_chassis`, `modern_tank_chassis` |
| **SUPPORT** | nothing closes anything. Anti-tank, AA, heavy AA, heavy and pack artillery had **no factory floor anywhere in the DEFAULT tier**, so the engine's need heuristic alone decided whether they were built | `anti_tank_equipment`, `anti_air_equipment`, `heavy_anti_air_equipment`, `heavy_artillery_equipment`, `pack_artillery_equipment` |
| both | amtrac is a support archetype whose line *does* close (peace), so it carries a closure term too | `amphibious_mechanized_equipment` |

**MEASURED** (inventory of every `equipment_production_min_factories*` block in
`common/ai_strategy/` and `common/ai_strategy_plans/`), the DEFAULT tier floored exactly this before
this change: infantry 1/5/12, support 2/5, trucks 3/6/10, artillery 1 (majors only), mechanized
3/8/15, amtrac 3/8/15, plus the air roles and convoys. **MEASURED** over `common/ai_templates/`, the
five unfloored archetypes are mounted in almost every AI division:
`anti_tank_mot_company_regimental` 113 occurrences (need 12 each),
`heavy_artillery_mot_company_divisional` 108 (need 6), `pack_artillery_mot_company_regimental` 74,
`heavy_anti_air_mot_company_divisional` 73, `anti_air` companies 27. That is the larger of the two
gaps, and the closure question hides it completely.

---

## 2. What Expert AI does, and what this took from it

**MEASURED**, Expert AI 5.0 (`supported_version="1.19.1.0"`), `EAI_PRODUCTION_equipment_strategies.txt`
(57 KB, **116** floors) and `EAI_PRODUCTION_equipment_strategy_effects.txt`. The copy on this machine
is under `steamapps/workshop/reset-backup-394360-20260830-015238/content-394360/741805475` — the
`C:\Jeux\...` path in `wa-engine-reference` no longer exists.

Its model: **seven stacking rungs per archetype**, each a country flag, each a Schmitt pair on
(industry, stockpile) — arm at 25/50/75/100/125/150/175 mils, release 10 points lower, and only
while `num_equipment@<arch> < 250`. The seven blocks sum: anti-tank runs 2 factories at 25 mils and
10 at 175+. **The shortage gate is confirmed by the peer**, and the rung ladder is the part not
taken (it needs computed flags; §8).

Three things it proved that this document previously asserted were impossible:

| | |
| --- | --- |
| **A ratio can be computed inside a trigger** | `EAI_PROD_EQUIP_REDUCE_infantry_equipment` runs `set_temp_variable` / `divide_temp_variable` inside its `enable` block. **MEASURED** independently: `set_temp_variable` appears in 17 Expert AI trigger files (249 uses) and in 6 WA trigger files already |
| **Hysteresis needs no latch flag** | `enable` at ratio > 0.50 and `abort` at ratio > 0.25, in the same block. A Schmitt pair with no flag |
| **`num_target_equipment_in_armies_k@<arch>` exists** | what the armies REQUIRE, in thousands. **MEASURED** in the **1.19.2.0** install's `documentation/dynamic_variables_documentation.md` — version-matched, not merely peer evidence — and WA already reads it in `WA_AI_MILITARY_posture_effects.txt:208` and `WA_AI_misc_effects.txt:232` |

And one piece of peer evidence on the lever: **115 of Expert AI's 116 floors are `_archetype`; one
is a type (`train`)**. It floors `light_tank_chassis` / `medium_tank_chassis` / `heavy_tank_chassis`
at 4 each. That is what decided B.

---

## 3. Why `_archetype` and not the type

An engine type is shared. **MEASURED** (the `type =` blocks of `common/units/equipment/`):

| type | covers |
| --- | --- |
| `armor` | all **36** tank chassis — every class, every variant, the scout and combat cars |
| `anti_tank` | towed AT **+ the 4 tank destroyers** |
| `anti_air` | towed AA **+ the 5 SPAA chassis** |
| `artillery` | every gun **+ the 5 SPG chassis + mechanized artillery** |
| `infantry` | infantry, heavy infantry, towed AT, towed AA, all artillery, support equipment |

A floor on `armor` cannot tell a light park from a modern one; a floor on `anti_tank` would be
satisfied by tank-destroyer production while the towed park stayed empty. The archetype is the
granularity that maps to a park, which is why the peer uses it 115 times out of 116.

**Also floored elsewhere, and floors on one id SUM** (**MEASURED** additive on the air carrier
floors): `minor_unit_production` floors the `armor` type at 1 for POL/HUN/SWE, the CZE historical
plan at 2, and `WA_AI_PRODUCTION_lend_lease.txt` floors the `anti_tank` (8/3), `anti_air` (3/4) and
`artillery` (10) types on donors. Those countries maintain deeper. Bounded, intended, printed by the
harness.

---

## 4. The gate

```
ratio(X) = num_equipment@X / num_target_equipment_in_armies_k@X / 1000     # spares / required
```

Wrapped in the `if / else = { always = no }` division-by-zero guard — the shape Expert AI uses for
the same computation.

```
WA_AI_PRODUCTION_should_maintain_<key> = {
	<domain>                                              # tanks_is_enabled / ground_is_enabled
	NOT = { WA_AI_PRODUCTION_armor_category_push = yes }  # armour keys only - see below
	NOT = { WA_AI_PRODUCTION_build_<class>_armor = yes }  # armour keys + amtrac: the line is closed
	num_of_military_factories > constant:wa_ai_production.industry.wartime_min_mils
	WA_AI_PRODUCTION_is_<key>_short = yes                 # ratio < shortage_enable
}
```

`should_hold_maintain_<key>` repeats every term but swaps the last for
`NOT = { is_<key>_supplied }` (ratio < `shortage_abort`), and the `ai_strategy` block reads
`enable = { should_maintain }` / `abort = { NOT = { should_hold_maintain } }`.

**`abort` is not the negation of `enable`.** It must also fire when a closure term comes back, or a
reopened line would keep its floor — which is why `should_hold_maintain_*` repeats the closure
terms rather than carrying only the stock bar.

**Why the category push is negated on the armour keys.** `WA_AI_PRODUCTION_armor_category_push`
raises the engine's perceived NEED for armour; a floor FORCES allocation regardless of need. The two
together double-count, which is why the per-chassis floors were dropped once before:

> Tank chassis carry **NO floor**: the armor category factor above is their only lever. A floor is
> need-blind […] re-adding one under the category factor would force allocation on top of a raised
> demand and **double-count**. — `[armor-prod-category]`, `WA_AI_PRODUCTION_DEFAULT_tanks.txt`,
> owner instruction 2026-09-01

The negation makes them mutually exclusive **by construction**: this floor can only run while that
lever has nothing to multiply. Option B re-introduces per-chassis floors knowingly, with that guard
and after the objection was quoted; the harness asserts the exclusivity on every run
(`exclusive-with-category-push`).

---

## 5. The numbers

`common/script_constants/wa_ai_production.txt`, group `maintenance`. **Seven**, down from the
sixteen absolute bars revision 3 had to guess — the ratio removed the need for a park bar and a
stock ceiling per archetype.

| Key | Shipped | Meaning |
| --- | --- | --- |
| `target_min_k` | 0.1 | the armies must require at least ~100 of it before a floor is owed |
| `shortage_enable` | 0.10 | arm: free spares under 10 % of what the armies require |
| `shortage_abort` | 0.25 | release: spares back to 25 %. **Never equal to the above** |
| `floor_base` | 2 | armour chassis |
| `floor_deep_add` | 3 | added above `industry.tier_large_mils` → 5 |
| `ground_floor_base` | 1 | support equipment |
| `ground_floor_deep_add` | 2 | → 3 |

Armour is the deeper pair because a chassis is two orders of magnitude dearer than a towed gun
(**MEASURED** `build_cost_ic = 200` per chassis), so one factory is a trickle there and a real flow
for a support gun.

The two `ai_strategy value =` literals per key are the one place `constant:` cannot be used and are
kept equal by hand; every other reader — the probe, the harness — takes the constants, so retuning
cannot make them disagree with the shipped floor.

---

## 6. Edge cases

| # | Case | Guard |
| --- | --- | --- |
| 1 | **1936, 20 mils, 5 maintenance factories on chars** | Three independent guards: `wartime_min_mils` holds the system off at or below 20; `target_min_k` fails because the armies require almost nothing; and the ratio is high because the starting stockpile is full |
| 2 | Captured stock inflates the park | The denominator is what the armies REQUIRE, not what they hold, so a captured stockpile *raises* the ratio and releases the floor — the correct direction |
| 3 | A country with no AT templates gets AT factories forced | `target_min_k`: no requirement, no floor. The gate cannot fire on equipment the templates never mount |
| 4 | Entry accumulation (the AIFC 517-entry failure) | Not reachable: static `ai_strategy` blocks with `enable`/`abort`, no `add_ai_strategy` |
| 5 | A park sitting on the bar toggles every evaluation | The Schmitt pair, 0.10 / 0.25. The harness asserts the bars have not crossed (`schmitt-disjoint`) |
| 6 | The floor runs for ever | It cannot: producing raises the numerator, the ratio crosses 0.25, the block aborts. The shortage is self-extinguishing — this is what replaced revision 3's absolute stock ceiling |
| 7 | Floors starve the factory pool | 10 keys x at most 5 = 25 factories worst case, and only on a country short of all ten at once above 49 mils. The harness prints the running total |
| 8 | Two floors on one id | §3: the `armor`, `anti_tank`, `anti_air` and `artillery` TYPES carry floors elsewhere and sum with these. Bounded, printed |
| 9 | Puppets and subjects | All reads are ROOT-scoped country variables; re-check the puppet-scope trap in `wa-lessons-learned` before the first commit |
| 10 | A floor buys volume, not modernisation | The AI walks the `parent` chain to the deepest producible variant. **ASSUMED** — §7 |

---

## 7. The two engine facts this rests on

Both **ASSUMED**, both owed an owner console reading (`event wa_maint.3 <TAG>`, then the production
panel). Neither is decidable from script.

| | Question | If false |
| --- | --- | --- |
| **F1** | Does `equipment_production_min_factories_archetype` force allocation on an archetype whose perceived need is ~0? The engine doc says it "forces" but also that it ignores how many factories are available — that sentence is about the *pool*, not about *need* | The whole system has no lever. Gone when a country the harness reads as maintained shows 0 factories on that archetype |
| **F2** | Do those factories land on the **newest** producible variant? | The floor produces but does not modernise, which is the entire point. Gone when a maintained park keeps receiving its oldest variant |

The probe `WA_TLM_r115_maint_at_ratio` is the campaign-scale version of the same question: free
anti-tank spares over requirement must **rise** on a country reading `ground_n > 0`. If it does not,
F1 is gone.

---

## 8. Not done

- **The Expert AI rung ladder** (7 stacking rungs instead of 2). It needs country flags computed in
  a scripted effect; the 2-rung form is the same shape at a tenth of the surface. Revisit if a
  campaign shows the floor is the wrong size for large industries.
- **Infantry, support equipment, trucks, trains, mechanized**: already floored, and none showed a
  symptom. Adding one later is a key in the generator, not a redesign.
- **A `WORK.md` subject** — admission is the owner's call.
