# WA_AI maintenance floors — keeping a fielded park supplied

Status: **IMPLEMENTED, NOT COMMITTED**. Owner revision 2026-09-19: **every** armour chassis
archetype — the four main gun classes and all 32 variant chassis — keeps a flat five-factory floor
whenever fielded divisions require that chassis. Their captured stock no longer disables
maintenance. Support-equipment floors retain the ratio and hysteresis model below.

**Why the variants were added (owner directive, 2026-09-19).** A Flakpanzer I is
`light_spaa_tank_chassis` and a Sturmpanzer I 'Bison' is `light_assault_tank_chassis`: to the engine
these are **not** `light_tank_chassis`, so the four main-class floors never reached them
(**MEASURED**, `common/units/equipment/tank_chassis.txt` + `x_tank_chassis.txt`: 36 tank archetypes,
of which the floors covered 4). GER 1939 was seen running a Panzer II line at exactly the 5-factory
floor beside a Flakpanzer line at 2 and a Bison line at 15 — the floor working on one archetype and
absent on the others.

Files in the working tree:

| File | |
| --- | --- |
| `common/script_constants/wa_ai_production.txt` | `maintenance` group, **6 numbers** |
| `common/scripted_triggers/WA_AI_PRODUCTION_maintenance_triggers.txt` | 108 triggers: 2 per armour chassis (36 of them), 6 per support key |
| `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_maintenance.txt` | 48 blocks: one per armour chassis (36), base/deep for six support keys |
| `common/scripted_effects/WA_TEST_maintenance.txt` + `events/wa_test_maintenance.txt` | harness v1, namespace `wa_maint` |
| `common/scripted_effects/WA_TLM_core.txt` + `documentation/WA_TLM_TELEMETRY_SYSTEM.md` | probe `WA_TLM_r115_maint_*` + `_armor_var_n`, TLM **v39** |

Gates: `check_constants` 0 error / 0 warning / 88 groups · generator tests 73/73 ·
`check_ai_layers` unchanged from HEAD (same single pre-existing `NAME-COLLISION`, all six ratchets
identical) · 44 maintenance triggers, no dangling armour-maintenance reference.

**Owed before this can be marked TESTED:**

1. **Phase 0 not run.** The two engine facts of §7 are ASSUMED. `event wa_maint.3 <TAG>`, then the
   production panel.

---

## 1. What the system does

A small factory floor so a park the AI has stopped expanding still receives new equipment, and
therefore still **modernises**: at zero factories a mature park drives the chassis and fires the
guns it had when the line went quiet, for the rest of the campaign. That is the mechanism the air
lines already run (`WA_AI_PRODUCTION_air.txt` § MAINTENANCE), generalised to land.

**Two reasons a land park goes unsupplied, and they need different gates:**

| | Trigger | Keys |
| --- | --- | --- |
| **ARMOUR** | fielded divisions still require the chassis, regardless of captured stock or expansion demand | all **36** tank archetypes: `light/medium/heavy/modern_tank_chassis`, the four `_tank_destroyer_`, four `_tank_artillery_` (+ `medium_tank_rocket_`), four `_assault_tank_`, four `_spaa_tank_`, four `_infantry_support_tank_`, three `_tank_support_`, the four super-heavy / `landkruiser_tank_chassis`, `amphibious_tank_chassis`, `scout_car_chassis`, `combat_car_chassis` |
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
floors): `WA_AI_PRODUCTION_lend_lease.txt` floors the `anti_tank` (8/3), `anti_air` (3/4) and
`artillery` (10) types on donors. Those countries maintain deeper. Bounded, intended, printed by the
harness.

**Corrected 2026-09-16, `[minor-gun-floor]`.** The `armor` TYPE floors this paragraph used to name
are gone or were never there. POL/HUN/SWE's floor of 1 went out with `minor_unit_production`; the
"CZE historical plan at 2" never existed in this tree - `CZE_unit_production` and
`CZE_highered_armored_production` both carry **zero** `ai_strategy` entries (MEASURED, whole-file
scan), as did `minor_highered_armored_production`. **No `equipment_production_min_factories` on
`id = armor` exists anywhere in `common/ai_strategy/` any more**, which makes
`[armor-prod-category]`'s "tank chassis carry NO floor" universally true for the first time.

---

## 4. The gate

For every armour chassis archetype, the 2026-09-19 owner revision replaces the ratio gate below:
maintenance is active whenever `num_target_equipment_in_armies_k@<chassis> > target_min_k` and the
country passes the shared industry floor. Captured stock does not close it. The ratio/Schmitt model
below now describes support equipment and amtracs only.

```
ratio(X) = num_equipment@X / num_target_equipment_in_armies_k@X / 1000     # spares / required
```

Wrapped in the `if / else = { always = no }` division-by-zero guard — the shape Expert AI uses for
the same computation.

```
WA_AI_PRODUCTION_should_maintain_<armor_class>_tank = {
	WA_AI_PRODUCTION_tanks_is_enabled = yes
	num_of_military_factories > constant:wa_ai_production.industry.wartime_min_mils
	check_variable = { num_target_equipment_in_armies_k@<chassis> > constant:wa_ai_production.maintenance.target_min_k }
}
```

For armour, `should_hold_maintain_<key>` repeats the same fielded-demand gate. Support equipment
keeps the ratio form: its hold trigger swaps `_short` for `NOT = { _supplied }`. Every strategy
reads `enable = { should_maintain }` / `abort = { NOT = { should_hold_maintain } }`.

**`abort` is not the negation of `enable`.** It must also fire when a closure term comes back, or a
reopened line would keep its floor — which is why `should_hold_maintain_*` repeats the closure
terms rather than carrying only the stock bar.

**Why the category push may coexist with the armour floor.** The old design excluded it because it
raises perceived demand:

> Tank chassis carry **NO floor**: the armor category factor above is their only lever. A floor is
> need-blind […] re-adding one under the category factor would force allocation on top of a raised
> demand and **double-count**. — `[armor-prod-category]`, `WA_AI_PRODUCTION_DEFAULT_tanks.txt`,
> owner instruction 2026-09-01

The 2026-09-19 owner revision supersedes that exclusion. The demand factor may allocate more than
five factories, while the archetype minimum guarantees five when captured stock suppresses demand.
The floor does not add five above an allocation already at or above five. The harness now asserts
that every armour gate — main class and variant — agrees with fielded demand (`armor-fielded-gates`).

---

## 5. The numbers

`common/script_constants/wa_ai_production.txt`, group `maintenance`. **Six**, down from the
sixteen absolute bars revision 3 had to guess — the ratio removed the need for a park bar and a
stock ceiling per archetype.

| Key | Shipped | Meaning |
| --- | --- | --- |
| `target_min_k` | 0.1 | the armies must require at least ~100 of it before a floor is owed |
| `shortage_enable` | 0.10 | arm: free spares under 10 % of what the armies require |
| `shortage_abort` | 0.25 | release: spares back to 25 %. **Never equal to the above** |
| `floor_base` | 5 | each armour chassis archetype required by fielded divisions, variants included |
| `ground_floor_base` | 1 | support equipment |
| `ground_floor_deep_add` | 2 | → 3 |

Armour is the deeper pair because a chassis is two orders of magnitude dearer than a towed gun
(**MEASURED** `build_cost_ic = 200` per chassis), so one factory is a trickle there and a real flow
for a support gun.

The armour keys have one `ai_strategy value = 5` literal each; support keys keep base/deep pairs.
These are the one place `constant:` cannot be used. `tools/constants_registry.json` checks all **36**
armour copies strictly against `floor_base`; every other reader takes the constants.

**Who this newly reaches — the ahistorical/minor walk (AGENTS P3 b–c).** Three of the 32 variants
are not armour-doctrine equipment at all:

| Archetype | Carried by | Who now reserves 5 mils |
| --- | --- | --- |
| `scout_car_chassis` | `recon_scout_car_company_divisional` (15/company, `common/units/support_recon.txt`), `scout_car_battalion_line` | **any** AI above `wartime_min_mils` whose divisions take the scout-car recon company — most minors with an industry |
| `combat_car_chassis` | armoured-car recon (`common/units/armor_armored_cars.txt`) | same shape |
| `*_infantry_support_tank_chassis` | `*_infantry_support_armor_battalion_line` | a country with infantry-support armour but no tank arm |

**This does not contradict the `[minor-gun-floor]` owner ruling of 2026-09-16** ("a country that does
not pass `WA_AI_TEMPLATES_use_armor_templates` … builds no tanks at all … never add a bootstrap floor
to 'fix' it"). That ruling forbids a floor that *gives* a country a tank arm. Every floor here arms
only on `num_target_equipment_in_armies_k@<arch> > 0.1k` — the country's own divisions already
require the chassis — so it replaces attrition losses on a park that exists and can never create one.
A country with zero armour battalions reads `require = 0` on all 36 and gets nothing. The ruling's
text is restored verbatim at `WA_AI_PRODUCTION_DEFAULT_tanks.txt` with this distinction attached.
**ASSUMED** and owed the harness: that a recon-only minor reads `armor_var_n = 1-2` and not more.

### The aggregate cost table (AGENTS P3 f) — **this is the open question**

The floors SUM on the same military pool. `wartime_min_mils` only asks for 21, so the aggregate is
**not** bounded by anything. Three timepoints:

**t0 — 1936 start templates.** **MEASURED** by mapping every `x = / y =` regiment in
`history/units/*_1936.txt` through the `*_chassis` reference of its sub-unit in `common/units/`, and
summing `arms_factory` over `history/states/` per owner. Only **19 of 313** country files field any
armour archetype at all, and the `> 20 mils` gate silences the small ones (BUL 5, SAF 4, NZL 2,
AST/BEL 10). What is left:

| Tag | Archetypes | Floor | Mils 1936 | Floor / mils |
| --- | --- | --- | --- | --- |
| USA | 4 | 20 | 21 | **95 %** |
| FRA | 6 | 30 | 59 | **51 %** |
| ENG | 4 | 20 | 45 | **44 %** |
| ITA | 4 | 20 | 49 | **41 %** |
| JAP | 4 | 20 | 59 | 34 % |
| GER | 4 | 20 | 93 | 22 % |
| SOV | 5 | 25 | 133 | 19 % |
| CZE | 1 | 5 | 32 | 16 % |
| CRO | 3 | 15 | 0 | inert (under the mils gate) |

**t1 / t2 — as WA's own AI templates open more roles.** **DERIVED**, not measured: the same mapping
over `common/ai_templates/WA_AI_TEMPLATES_*.txt` reaches **21 distinct chassis archetypes** (the four
gun classes plus TD, SP artillery, assault gun, SPAA, infantry-support and support tank in the light /
medium / heavy / modern families). At that ceiling a single country requests **105 factories** of
maintenance floor. A 1943 major holds 150–200 mils, so the ceiling is **over half its arsenal**.

**No taper is implemented.** `floor_base` is flat 5 for all 36 ids, per the owner directive of
2026-09-19. The three obvious levers, none chosen: a smaller `variant_floor_base` (a Flakpanzer
company is ~1/10 the equipment demand of a tank battalion); a per-country cap on the sum; or scaling
the floor by the band ladder in `wa_ai_production.industry` the way the ground floors do. **The
number to watch in a campaign is `WA_TLM_r115_maint_floor` against that country's mils.**

**The floors SUM, and that is the cost of this revision.** Each armed archetype reserves 5
factories, and `wartime_min_mils` only asks for 21. A country whose divisions field six armour
archetypes (a plausible GER 1939: light tank, light SPAA, light assault gun, light TD, medium tank,
scout car) has **30 factories reserved before anything else is weighed** — **DERIVED** from
6 × `floor_base`, not measured in a campaign. The self-limiting gate keeps an *unfielded* archetype
free, but it does nothing about a country that genuinely fields many. The harness totals line prints
the factory sum beside `mils` for exactly this reason; read it before calling a campaign healthy.

---

## 6. Edge cases

| # | Case | Guard |
| --- | --- | --- |
| 1 | **1936, 20 mils, 5 maintenance factories on chars** | `wartime_min_mils` holds the system off at or below 20; above it, any main chassis actually required by fielded divisions receives its floor, including in 1936 |
| 2 | Captured stock inflates an armour park | Armour ignores the surplus ratio and keeps five factories while the chassis remains required by fielded divisions. Support equipment still releases its floor through the ratio. |
| 3 | A country with no AT templates gets AT factories forced | `target_min_k`: no requirement, no floor. The gate cannot fire on equipment the templates never mount |
| 4 | Entry accumulation (the AIFC 517-entry failure) | Not reachable: static `ai_strategy` blocks with `enable`/`abort`, no `add_ai_strategy` |
| 5 | A support park sitting on the bar toggles every evaluation | The support-equipment Schmitt pair, 0.10 / 0.25. The harness asserts the bars have not crossed (`schmitt-disjoint`) |
| 6 | An armour floor runs after its class disappears | The identical hold gate aborts when fielded divisions no longer require that chassis |
| 7 | Floors starve the factory pool | Armour reserves 5/10/15/20 factories when 1/2/3/4 main chassis classes coexist; support floors add only while short. The harness prints the running total. |
| 8 | Two floors on one id | No other main-chassis archetype floor exists. Support type/archetype floors can still sum. **[minor-gun-floor], 2026-09-16**: `WA_AI_PRODUCTION_DEFAULT_ground.txt` carries a baseline archetype floor of 1 on `anti_tank_equipment`, so anti-tank totals are **2 while short, 4 deep**. Printed by harness section B2 |
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

**F1 now also carries the `[minor-gun-floor]` baseline floors** of
`common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_ground.txt` (`artillery_equipment` for non-majors,
`anti_tank_equipment` for everyone, both at >= 10 military factories with a non-zero
establishment). If F1 is false those two are inert as well. Harness section B2 of
`WA_TEST_maintenance.txt` prints their verdicts next to the establishment they read.

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
