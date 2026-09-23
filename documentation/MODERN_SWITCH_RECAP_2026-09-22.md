# Medium -> modern armour switch (World Ablaze AI): experiment recap

> **Resolution (same day, after this recap was written):** the intermediate-template design of
> section 6 was tried (`test12`, `test13`) and shipped as `[modern-tier-ladder]` - see the full
> report's sections 7e-7g. Sections 1-5 below are the research record that led there.

Date: 2026-09-22. Branch `ai-rework`. Engine Hearts of Iron IV 1.19.3.0. Country observed: Germany (GER), AI-controlled.
Full report: `documentation/MODERN_SWITCH_BRAKE_EXPERIMENT_2026-09-21.md` (sections 1 to 7d).
Readers and scripts: `tools/archive/modern_switch_experiment/`.

Convention: **MEASURED** = read from a savegame, a game file or a mod file (source named).
**DERIVED** = computed from a MEASURED. **ASSUMED** = not verified.

---

## 1. The problem

When the AI unlocks the modern tank chassis, the "medium armour" template role retargets to a
modern template. Every existing armoured division is then re-cut in the field, one battalion per
step, while the modern chassis stockpile is 0.

Symptom, **MEASURED** (campaign `02795c2d`, 1943.8.1, four months after the switch): 17 "modern"
divisions hold ~150 modern chassis in total for ~2 550 required; medium tanks per division fell
from ~197 to ~8. The divisions are at 4/7 of their armoured strength.

Owner's goal: switch only once a modern stock exists, and have the mod build that stock before
the switch.

## 2. What the engine does (established outside the runs)

| Fact | Label | Source |
| --- | --- | --- |
| The AI's unit of work is the role ENTRY (`WA_..._role = { ... }`), not the role name. Each entry has its own XP lottery, its own target list, its own arrow (currently targeted template). | MEASURED | `hoi4.exe` strings, owner's imgui `ai_templates` |
| A disabled target (`enable = no`) does not exist for the engine: its `can_upgrade_in_field` is never read. | MEASURED | install `common/ai_templates/_documentation.md` |
| `replace_with` resolves only inside its own entry. | MEASURED | live 2026-08-29 |
| Vanilla and Expert AI put the `can_upgrade_in_field` brake on the SOURCE target; WA put it on the DESTINATION targets (the modern ones), where it can do nothing. | MEASURED | install, EAI 5.0, `WA_AI_TEMPLATES_armored_medium_modern.txt` |
| The designer climbs ONE battalion per step (7+0 -> 6+1 -> 5+2 -> ...), one template generation per step, and the park follows every child. | MEASURED | template ids and `obsolete_change_date` in the saves |
| The `equipment_variant_production_factor` lever multiplies a NEED; the need exists only once a template mounts the battalion. Before the switch it is inert. | MEASURED | install doc, `bascule3` |
| The `equipment_production_min_factories_archetype` floor is need-blind and "doesn't take into account how many factories are actually available" (doc); measured: on a saturated pool, 30 requested, 0 assigned. | MEASURED | install doc, `bascule3` (1943.5, 662 of 716 factories committed) |

## 3. The runs

Two test beds. Bed 1 (this machine): `trade_issue.hoi4`, campaign `02795c2d`, GER, 1943.3.5,
switch on 1943.4.1, park = template G (7 medium battalions), 20 divisions tracked by id. Bed 2
(second machine): `modern_bed.hoi4`, campaign `d6190fb7`, switch on 1943.5.1, 17 divisions. Each
bed has a frozen cohort (11 and 9 divisions, cause: heavy chassis deficit) that is never counted.
Every run: fresh exe (a hot reload poisons triggers), load, `observe`, dated saves. Each save
carries a distinct mod checksum, which proves the edited file loaded.

Notation: "5+2" = 5 medium + 2 modern battalions per division. "gun tanks" = medium main-gun tanks
held per division (195 = full for 7+0, 25 per battalion).

### 3a. Brake on a source target (bed 1, single reading at +30 d, 1943.5.1)

| Run | Setup | Park at +30 d | Live templates | Modern lines requested | Verdict |
| --- | --- | --- | --- | --- | --- |
| baseline B3 / B4 | no edit | Modern B (2+5) 15 / Medium D (5+2) 17 | one | 301 / 151 | two baselines three rungs apart on the same date |
| `test1` | source target 21718 kept enabled in the medium entry (weight 0), brake CLOSED | G (7+0) 20 | G | 16 | everything frozen: park, recruits, modern need |
| `test2` | same, read at 1943.6.1 | G 20, 27 divisions with recruits | G | 1 | freeze confirmed at +60 d |
| `test3` | same, brake OPEN | G 20 | G | 16 | identical to `test1`: the freeze comes from the separate entry, not the brake |
| `test4` | copy of the source INSIDE the modern entry, prio 5, no `replace_with`, brake closed | A (6+1) 18, G 2 | A | 169 | holds nothing |
| `test5` | copy first in the modern entry, prio 10, `replace_with` -> modern target, `replace_at_match 0.9`, brake CLOSED | A 18, G 2 | A, C, D (three) | 211 | read at the time as "the brake works through the edge" |
| `test6` | `test5` with brake OPEN | E (4+3) 19 | E only | 151 | read as the control of `test5` |

What 3a establishes (MEASURED): an enabled source in a separate entry freezes everything; a source
inside the same entry with no edge holds nothing. The causal reading of `test5`/`test6` (one run
each, one date) fell in 3c.

### 3b. Medium-hull twins for all 258 modern targets (bed 2)

A twin = a copy of each modern target with medium battalions in place of modern ones, enabled by
the same flag value, `replace_with` to its modern target, `target_min_match 0.1`.

| Run | `replace_at_match` | Brake | +31 d | +75 d | +120 d | Modern lines active | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | - | - | C (5+2) 15 | F (4+3) 15 | F 15, 2.4 modern/div | 0 -> 50 -> 200 | reference (cloud build, not HEAD) |
| `test7` | 0.3 | closed | B (6+1) 17 | Modern A (3+4) 17, 75 gun tanks | same, 10 modern/div | 0 -> 32 -> 186 | full descent, four rungs in 16 days; holds nothing |
| `test8` | 0.9 | closed | C 11, B 3, A 3 (+50 d) | **A (7+0) 16, live again** | A 17, then a new 7+0 "E" | **0 -> 0 -> 0** | goes down then comes BACK to 7+0; no modern template designed, 0 modern chassis built for four months |

### 3c. The one-line control (bed 1, same three dates: +50 / +75 / +120 d)

| Run | Setup | +50 d | +75 d | +120 d | Modern designed / active | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `test8'` | 258 twins, 0.9, brake CLOSED | D (5+2) 17, 130 gun tanks | **G (7+0) 19, live again**, 193 gun tanks | C (7+0) 17, 192 gun tanks | never / 0, 0, 1 | descent, back to 7+0, modern frozen |
| `test9` | 258 twins, 0.9, brake OPEN | C (5+2) 14, 139 gun tanks | **G (7+0) 16, live again**, 184 gun tanks | F (7+0) 9, H (6+1) 5, 176 gun tanks | never / 0, 0, 12 | same trajectory |

One line differs between the two runs (`can_upgrade_in_field = { always = no | yes }` on the 258
twins), same bed, same exe. Same trajectory. **The brake is inert** (MEASURED). The down-and-back
movement is produced by the 0.9 threshold alone (ASSUMED reading: the arrow stays on the modern
target while the best live template matches the twin at >= 0.9, then returns to the twin and the
designer re-cuts 7+0). `test5` was a snapshot of that same descent.

### 3d. The engine valve (bed 1, no twin)

| Run | Setup | +50 d | +75 d | +120 d | Verdict |
| --- | --- | --- | --- | --- | --- |
| `test10` | `NDefines.NAI.UPGRADES_DEFICIT_LIMIT_DAYS` 90 -> 30 ("AI will avoid upgrading units in the field to new templates if it takes longer than this to fulfil their equipment need") | C (5+2) **20**, 125 gun tanks | 5+2 / 5+3, 125 gun tanks | 4+3, 101 gun tanks, 2.3 modern/div | **inert**: full-speed descent with 0 stock and 0 modern factories, as in the unedited campaign |

### 3e. Owner runs of 2026-09-20 (priming build, before the stock bar was removed)

| Run | Reading | Verdict |
| --- | --- | --- |
| `bascule3` (1943.5) | 662 of 716 factories committed; 30-factory modern floor REQUESTED, 0 ASSIGNED; ten lines waiting | a need-blind floor does not preempt a saturated pool |
| `bascule4` (1943.11) | modern 253 requested / 113 assigned; 26 armoured divisions at ~500 strength | symptom absent on that run; contradicted by `02795c2d` (1943.8, ~10 modern/div), cause of the disagreement unknown, console harness never run |

## 4. What works, what does not

| Mechanism | Result | Label |
| --- | --- | --- |
| `can_upgrade_in_field` brake on the destination target (shipped state) | does nothing, conversion starts at stock 0 | MEASURED |
| Brake on an enabled source in a separate entry | freezes park, recruits AND modern need: deadlock (no need -> no stock -> never opens) | MEASURED |
| Brake on a twin source in the same entry, with or without `replace_with`, at 0.3 or 0.9, open or closed | inert | MEASURED (9 runs) |
| `replace_at_match = 0.9` threshold on a twin | produces a down-and-back oscillation and freezes modern design (no modern template, 0 chassis built) | MEASURED |
| `UPGRADES_DEFICIT_LIMIT_DAYS` valve at 30 | inert | MEASURED |
| Production factor on the modern chassis before the switch | inert (no need) | MEASURED |
| Need-blind factory floor before the switch (6 / 15 / 30 by industrial size) | 0 assigned on a saturated pool | MEASURED |
| Cover bar in the latch (modern stock / medium demand of the park) | removed by the owner on 09-20: a major at war never reaches it. Since then the priming window lasts 0 days and the floor has never run | MEASURED (commit `6f04283f85`) |
| Engine need-driven allocation, after the switch | works, but ~75 days late | MEASURED |

## 5. The measured bottleneck

On every run on both beds (`test7` to `test10`, baselines), **MEASURED**:

| After the switch | Modern lines (active / requested) | Medium lines active (of which main gun) | Free medium tanks | Park |
| --- | --- | --- | --- | --- |
| +50 d | 0 / 199 | 163 (60) | ~4 900 | already 5+2 everywhere |
| +75 d | 0 / 210 | 145 (34) | ~4 900 | 5+3 |
| +120 d | 169 / 225 | 53 (5) | ~5 000 | 4+3, 2.3 modern/div |

The park finished converting in 50 days. The modern lines get their first factory around +75 days
whatever they request, and reach 170-200 factories only at +120 days; on top of that comes WA's
production ramp (a line starts at 1 % efficiency). Meanwhile 60 factories produce medium main-gun
tanks with ~5 000 free medium tanks in stock.

The hollow division is: medium battalions FULL (4 x 25 = 101 gun tanks) and modern battalions
EMPTY (2 held of 75 required). **DERIVED**: the symptom is the gap between conversion speed
(50 days) and pool reallocation speed (a quarter), not a template defect.

## 6. What is still open

Nothing moves factories to modern faster than the pool releases them: brake, valve and floor all
fail on that same fact. The open question is **why the AI keeps 60 factories on a tank it holds
in surplus**. Three hypotheses, all ASSUMED, none readable from a save:

| Hypothesis | What would kill it |
| --- | --- |
| The free stock is an older variant (`medium_chassis_3_2`) and does not count against the need of the new one (`3_3`, line switched at +75 d). | The production view shows a medium need > 0 despite the stock. |
| The pool reassigns only as lines drain, never by arbitration between lines. | Wanted factories per line are already zero on medium yet stay assigned. |
| The +75 factors on the five medium variant lines (infantry support, assault, tank destroyer, AA), which the mod does not touch at the switch, hold the pool. | The perceived variant need is most of the figure. |

Reading requested: `imgui` production view on GER at +30 d after the switch (wanted and assigned
factories per line, need per equipment). Only the owner can take it.

Only action possible without that reading, not recommended before it: cap the modern target at
5+2 while cover is zero (a "modern battalion count" axis in the generator). It keeps 125 gun tanks
per division instead of 100 through the quarter; it does not shorten it.

## 7. References

| What | Where |
| --- | --- |
| Full report, detailed tables, labelled claims | `documentation/MODERN_SWITCH_BRAKE_EXPERIMENT_2026-09-21.md` |
| Subject tracker | `WORK.md`, subject `modern-switch-amorce` |
| Run reader (`read_run.py <reference save> <run saves>`), twin writer (`medium_hull_twins.py apply --ram 0.9 --brake yes|no`) | `tools/archive/modern_switch_experiment/` |
| Raw readings of the six saves of 3c and the three of 3d | `tools/archive/modern_switch_experiment/test8p_read.txt`, `test9_read.txt`, `test10_read.txt` |
| Latch, priming floor, catch-up | `common/scripted_effects/WA_AI_TEMPLATES_effects.txt` (`WA_AI_TEMPLATES_update_modern_chassis_latch`), `common/scripted_triggers/WA_AI_PRODUCTION_tanks.txt`, `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_tanks.txt` |
| Modern targets (generated, 258) | `common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt`, generator `tools/gen/gen_ai_armor_templates.py` |
| Engine defines | `common/defines/05_defines.lua` (`UPGRADES_DEFICIT_LIMIT_DAYS`, `DAYS_BETWEEN_CHECK_BEST_TEMPLATE`) |
| Saves | bed 1: `trade_issue.hoi4`, `test1`-`test6`, `test8a-c` (= `test8'`), `test9a-c`, `test10`, `test10b-c`; bed 2: `modern_bed.hoi4`, `test7a-c`, `test8a-c`. Saves do not travel between machines; the two `test8a-c` sets are different runs. |
