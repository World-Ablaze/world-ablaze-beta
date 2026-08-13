# `equipment_evaluator` — offline equipment evaluator (air, tanks, infantry, artillery, vehicles)

The mod's AI always produces the newest researched design in a design group.
That is wrong often enough to matter: a newer airframe can lose 30 % of its
combat radius, cost twice the industry, or add a strategic resource the country
does not have. This tool reads the mod's own data offline and says, for every
generation step in every air design group, whether the AI should actually
switch.

Dry-run remains the default. The tool writes analysis reports, a deterministic
decision manifest and a reviewable operation plan under `output/`. Only an
explicit `--apply-plan` command may modify mod files, after source-fingerprint,
overlap, ownership-marker and PDX brace validation.

The infantry domain additionally models production-line efficiency retention,
so a statistically better rifle is not automatically allowed to destroy a
mature production line.

---

## Running it

Run from `tools/` (like `run_generators.py`):

```bash
python -m equipment_evaluator --domain infantry --all
python -m equipment_evaluator --domain infantry --countries ENG,SOV
python -m equipment_evaluator --domain all --all
python -m equipment_evaluator --domain all --all --generate-plan
python -m equipment_evaluator --apply-plan equipment_evaluator/output/equipment_generation_plan.json
python -m equipment_evaluator --verify-plan equipment_evaluator/output/equipment_generation_plan.json
```

The shared production-efficiency audit covers all supported constructible
domains:

```bash
python -m equipment_evaluator --domain air --all
python -m equipment_evaluator --domain tanks --all
python -m equipment_evaluator --domain artillery --all
python -m equipment_evaluator --domain vehicles --all
```

It writes `production_efficiency_transitions.csv` and
`production_efficiency_report.md`. Modular tanks combine country
`ai_equipment` designs with the actual `path/leads_to_tech` graph, so parallel
branches are never mistaken for a sequence. Plane design blocks do not expose
an equivalent `enable` contract and retain their priority-ladder order;
infantry, artillery and vehicles use their actual technology graphs. All five
use the same configurable retention threshold and relation precedence.

### Infantry production-efficiency policy

The infantry evaluator reads each country's real `enable_equipments` order
from `common/technologies/infantry_<TAG>.txt`, then resolves equipment stats and
relationships from `common/units/equipment/infantry.txt`.

| relationship | retained line efficiency |
| --- | ---: |
| variant | 95% |
| parent ↔ child | 95% |
| same `family` | 90% |
| same `archetype` only | 75% |
| unrelated | 10% start efficiency |

Transitions retaining at least `penalty_free_retention` (90% by default) receive
no temporary-efficiency penalty: a positive equipment gain is enough to justify
the switch. Below 90%, a full switch requires the configurable
`low_retention_min_gain` (10% by default); otherwise the verdict is `KEEP_OLD`.
The evaluator deliberately does not emit `NEW_LINES_ONLY`: the AI equipment
interface selects one active design per role and cannot reliably reserve a new
design for newly assigned factories. A resource-significant upgrade receives
`SWITCH_CONDITIONAL`.

`can_convert_from` is reported separately: it governs stockpile conversion,
not production-line efficiency. Outputs are `infantry_equipment_transitions.csv`
and `infantry_equipment_report.md`.

```bash
python -m equipment_evaluator --help
python -m equipment_evaluator --list-countries
python -m equipment_evaluator --countries SOV,ENG
python -m equipment_evaluator --all
python -m equipment_evaluator --countries SOV --roles air_fighter_mr -v
```

Python 3.9+, standard library only — same constraint as the rest of `tools/`.

| Flag | Meaning |
| --- | --- |
| `--countries TAGS` | Comma-separated tags, e.g. `SOV,ENG,USA` |
| `--all` | Every country with a `<TAG>_planes.txt` |
| `--roles ROLES` | Restrict to air roles, e.g. `air_fighter,air_cas` |
| `--groups NAMES` | Restrict to design-group names |
| `--config PATH` | Alternate config JSON (default `config.json`) |
| `--mod-root PATH` | Mod root (default: auto-detected as `tools/../`) |
| `--output-dir PATH` | Report destination (default `<package>/output`) |
| `--no-redesign` | Skip the range-restoring module search |
| `--emit` | Also write a reviewable `ai_equipment` patch document. **Still a dry run** — writes nothing into `common/` |
| `--generate-plan` | Write the deterministic decision manifest and operation plan; requires `--domain all` and remains a dry run |
| `--plan-scope all\|tank-frontiers` | Restrict the operation plan; `tank-frontiers` owns complete branched tank groups only |
| `--apply-plan PLAN` | Transactionally apply a reviewed plan; abort all files on any conflict |
| `--verify-plan PLAN` | Confirm that every operation in a plan is already present |
| `-v` | One console line per transition |

Outputs (`output/` is gitignored by `tools/equipment_evaluator/.gitignore`):

* `air_equipment_transitions.csv` — one row per country/role/transition with
  every computed number and the verdict. This is the machine-readable artefact
  phase 3 will consume.
* `air_equipment_report.md` — the human review surface: every `KEEP_OLD`, every
  `SWITCH_REDESIGNED` with its full module list, every `SWITCH_CONDITIONAL`
  with its per-unit resource delta, every `PARALLEL_VARIANT` (pairs that are
  not a generation step), the chain-order inversions, plus the complete
  diagnostics.
* `data_integrity_audit.md` — findings about the **mod**, not about switching:
  `target_variant` blocks that mount more of a module than the airframe
  permits, slots given a module of a disallowed category, and design chains
  that run backwards in airframe year. A design in the first two categories
  cannot be matched by the in-game designer at all, so the AI silently never
  builds it. Always written.
* `emit_ai_equipment.md` — `--emit` only. The proposed `ai_equipment` patches,
  each quoted before/after against real line numbers, plus everything that was
  *not* emitted and why.
* `equipment_decisions.json` — deterministic cross-domain manifest. Every
  verdict records its source fingerprint and encodability status.
* `equipment_generation_plan.json` — exact before/after operations generated
  from encodable aviation and modular-tank decisions. Replaying the same plan
  is a no-op.
* `equipment_generation_plan_tank_frontiers.json` — scoped deployment plan
  containing only complete competitive-frontier selectors for branched tank
  roles. It never mixes them with linear air/tank decisions.
* `equipment_encodability_report.md` — per-domain coverage counts plus every
  decision intentionally blocked from code generation and its reason.

Generated blocks carry stable `WA_EQUIPGEN_BEGIN/END` ownership markers. The
analyser reconstructs a logical pre-generation view from those markers, so an
analyse/apply/analyse cycle reproduces the same decisions and emits an empty
second plan. Manual edits inside an owned block or changes after plan creation
are reported as conflicts rather than overwritten.

---

## Package layout

```
tools/equipment_evaluator/
├── __main__.py            CLI entry point
├── config.py              config loading + validation
├── config.json            all tunable knobs (see below)
├── pdx.py                 PDXScript reader (tokenizer + value tree)
├── parse_equipment.py     airframes + modules, inheritance resolution
├── parse_ai_equipment.py  ai_equipment design groups -> generations
├── technology_graph.py    tech paths -> branch-safe design succession
├── stats.py               stat model (airframe + module stacking)
├── decide.py              scoring, redesign search, verdicts
├── spans.py               source-span index over an ai_equipment file
├── emit.py                verdicts -> reviewable ai_equipment patches
├── data_audit.py          integrity checks on the mod's own design data
├── report.py              CSV + Markdown writers
├── diagnostics.py         flag collector (nothing is silently dropped)
└── output/                generated reports (gitignored)
```

The adoption pipeline is intentionally split into three layers:

1. domain evaluators (`decide.py`, `ground.py`, `infantry.py`) resolve stats,
   hard requirements and legal redesign candidates;
2. `production_efficiency.py` classifies line-retention relationships;
3. `decision_policy.py` applies the single shared efficiency/resource verdict
   policy for every domain.

Code generation adds a second, one-way pipeline:

1. `decision_manifest.py` serializes every domain decision deterministically;
2. `generation/planner.py` converts encodable emitter patches into exact,
   fingerprinted replacement operations;
3. `generation/apply.py` preflights all operations and writes all files or none;
4. `owned_source.py` removes owned generated blocks from the analysis view so
   regeneration reaches a fixed point.

For a branched role this pipeline owns the whole selector or none of it. It
does not emit pairwise partial rewrites and does not attempt `NEW_LINES_ONLY`.
The highest-ranked researched and affordable model wins; lower ranks are the
explicit continuity/economy floor. This is why the USA medium-tank result is
`M4A3E8 > M4A2 > T23 > T20 > M4A1`, rather than the fictitious file-order
sequence `Sherman -> T20`.

### Why a new parser

`tools/ai_replacer_base/` is regex + brace-matching specialised for technology
blocks (`TechBlock`, `find_ai_will_do_block`) and never builds a value tree.
`tools/dlc_splitter/` does have a real lexer and parser, but its AST exists to
*round-trip formatting* for rewriting files — overhead this read-only tool does
not need across ~6 MB of airframe and module data. `pdx.py` keeps the same
token grammar as `dlc_splitter/lexer.py` (identifier / number / string /
`= < >` / braces / `#` comments / `@vars`) but scans with one compiled regex
and emits a plain ordered multimap.

---

## The stat model

### Data sources

| What | Where |
| --- | --- |
| Design groups, generations, `target_variant` | `common/ai_equipment/<TAG>_planes.txt` |
| Airframe base stats, slots, `default_modules`, `resources` | `common/units/equipment/*plane*.txt` |
| Module `add_stats` / `multiply_stats` / `build_cost_resources` | `common/units/equipment/modules/*plane_modules*.txt` |
| `THRUST_WEIGHT_AGILITY_FACTOR` | `common/defines/05_defines.lua` |

### Stacking formula

For every stat `s`:

```
final[s] = (base[s] + SUM add_stats[s]) * (1 + SUM multiply_stats[s])
```

`base[s]` is the airframe's own value, resolved up the `parent` → `archetype`
chain. Two pieces of evidence from the mod's own data pin this down:

* `SOV_i_15_airframe` declares `maximum_speed = 317` with the author's
  annotation `#367`, and its default engine `SOV_engine_shvetsov_m_25a_1x` has
  `multiply_stats = { maximum_speed = 0.156 }`. `317 × 1.156 = 366.5`. So
  `multiply_stats` is a *fraction of the base added on*, not a raw multiplier.
* `non_strategic_materials` (wooden construction) has
  `multiply_stats = { thrust = -0.15 }`, yet **no airframe declares a base
  `thrust` at all** — thrust comes entirely from engine `add_stats`. Under a
  "multiply the base only" reading, wooden construction would be a no-op on
  thrust, which is plainly not the intent. Multipliers therefore apply to
  `base + adds`.

`stat_model.multiply_base_only = true` flips this back to
`base × (1 + Σmult) + Σadd` if an in-game measurement ever contradicts the
reading above.

### Derived stats

* **Agility** gets `THRUST_WEIGHT_AGILITY_FACTOR × max(0, thrust − weight)`
  added on top (the define is `1`, documented as "additive agility bonus per
  point of thrust exceeding weight").
* **Resources** = the airframe's inherited `resources = {}` plus every module's
  `build_cost_resources`, clamped at ≥ 0. Per-unit, unrounded.
* **Range** is the `air_range` stat. Fuel-tank modules add flat km
  (`fuel_tanks_medium: +300`); drop tanks multiply
  (`drop_tanks_2x: air_range × 0.5`); some late engines carry a range penalty
  (`SOV_engine_shvetsov_m_82fn_1x: air_range −0.1`).

### Mission-conditional stats

A module may declare `mission_type_stats = { limit = { <missions> } add_stats
multiply_stats add_average_stats }`, applying only while the aircraft flies one
of those missions. The mod's plane modules carry **683** such blocks, and they
hold most of what actually separates two designs in the same role:

| Stat | Blocks | Range | Where it matters |
| --- | --- | --- | --- |
| `air_agility` | 302 | −18.4 … +2.0 | every ordnance-carrying role |
| `air_attack` | 224 | −0.25 … +121.9 | `interception` |
| `naval_strike_targetting` | 159 | +4 … +18 | every torpedo mount |
| `naval_strike_attack` | 69 | −0.2 … +44.8 | naval strike |
| `air_ground_attack` | 61 | +0.05 … +11.4 | `attack_logistics` |
| `surface_detection` / `sub_detection` | 3 + 3 | +20/+30/+40, +1/+2/+3 | the air-ground radars |

The detection case shows why this cannot be skipped: the only modules granting
surface/sub detection through plain `add_stats` are `floats` (+5/+1) and
`flying_boat_large` (+10/+1), while `air_ground_radar_1/2` grant +30/+40 and
+2/+3 through `mission_type_stats`. Without them a radar-equipped patrol
aircraft scores zero detection in a role that puts 60 % of its weight there.

`config.role_missions` maps each role to **one** primary mission. One, not a
set: a design is scored as if flying a single job, and applying every block
that overlaps a role's mission set would double-count. Both sides of a
transition use the same mission, so the comparison stays fair regardless.

`add_average_stats` is a third stacking kind (183 uses, 159 of them nested in
`mission_type_stats`): contributions are **averaged** over the modules that
declare the stat rather than summed — two torpedo mounts declaring
`naval_strike_targetting = 10` give 10, not 20. It is folded into the additive
bucket after averaging, so the stacking formula above is otherwise unchanged.

None of these blocks touch `air_range`, `build_cost_ic` or
`build_cost_resources`, so the range gate and the per-unit resource footprint
are unaffected by the mission choice.

### Effective loadout

A `target_variant.modules` block states *match requirements*. Per
`common/ai_equipment/_documentation.info` — *"Modules not in this list will not
be used in any remaining open slots"* — slots the design does not mention stay
**empty** unless they are `required`, because no plane design in this mod
declares `allowed_modules`. The tool therefore takes the design's `modules` and
fills the airframe's inherited `default_modules` into *required* slots only.
Four designs in the mod declare a completely empty `modules = {}` block and
would otherwise be scored as an airframe with no engine; those are flagged
`defaults_assumed`.

A slot value may legally name a **module category** rather than a module
("the latest available will be favored"). The tool resolves a category to its
last member in file order that is generic or carries this country's tag, and
flags it `category_slot`.

### Documented approximations

1. **Inheritance order.** HOI4 inherits undeclared fields from `archetype`; the
   mod additionally uses `parent` for model-to-model lineage. The tool consults
   `parent` before `archetype`, on the grounds that a variant's immediate
   predecessor is the more specific source. This applies uniformly to stats,
   resources, slots, `module_count_limit` and `year`.
1b. **`module_count_limit` overrides, it does not accumulate.** A concrete
   airframe lifts or tightens an archetype cap by re-declaring it for the same
   target, nearest declaration winning — `SOV_la_5_airframe` declares
   `module_count_limit = { module = self_sealing_fuel_tanks_large count = any }`
   solely to lift the `count < 1` its archetype imposes, and a `count = any`
   entry is meaningless under any other reading (the Fix 47 annotation in
   `SOV_planes.txt` states the same). Verified against the data, **not**
   in-game: 618 of 2119 airframes are affected, mostly on the large fuel-tank
   modules, so a wrong reading here silently removes the best range fixes from
   the redesign search.
2. **No tech/doctrine/spirit modifiers.** Research bonuses, national spirits,
   designer traits, and equipment upgrade levels
   (`common/units/equipment/upgrades/`) are not applied. All designs are
   compared on bare stats, so the *comparison* is fair even though the absolute
   numbers are lower than in-game.
2b. **One mission per role.** `mission_type_stats` blocks are applied for the
   role's primary mission only (`config.role_missions`). A multirole design
   that in practice flies two missions is scored on one of them.
3. **No thrust → speed relationship.** No define ties thrust to speed and the
   mod bakes speed into engine `multiply_stats`, so none is modelled.
4. **Module availability is inferred, not read from tech.** The tool does not
   parse `common/technologies/`. A module counts as available to a redesign of
   an airframe of year *Y* if the same country's own design set already uses
   that module on some airframe of year ≤ *Y*. This is a proxy; it can be
   slightly optimistic (a module used by another role's earlier airframe) or
   pessimistic (a module the country researches but never scripts).
5. **Empty `allowed_module_categories` means "no candidates offered".** Archetype
   slots declare the list empty and concrete airframes override it; where a
   concrete airframe also leaves it empty the tool refuses to invent modules
   for that slot rather than produce an illegal design.
6. **`any_of` takes the first entry**, and a relative bound (`slot > module`)
   is treated as exactly that module. Both are flagged. Neither construct is
   currently used in the plane files (4 `any_of` uses in `USA_cas`, no
   relative bounds).
7. **Rounding.** HOI4 rounds per-unit resource costs for display; the tool
   reports raw floats.

---

## The decision algorithm

For each design group, designs are ordered by file position — that ordering
*is* the generation chain. Every consecutive pair `(N, N+1)` is one transition.

**1. Compute** both designs' stats: range, IC, per-resource footprint, and the
role-relevant combat stats, both flying the role's primary mission.

**1b. Is it a generation step at all?** A design group may hold sibling
loadouts on one airframe (`GER heavy_fighter_5_1` air-to-air vs `5_2`
tank-buster) or two parallel families (`JAP_strike_bomber` holds both
`heavy_strike_bomber_*` and `light_strike_bomber_*`). Neither is a
supersession, so no switch decision applies and the pair is emitted as
`PARALLEL_VARIANT` with its numbers intact:

```
old.airframe == new.airframe                       -> PARALLEL_VARIANT  (flag same_airframe)
airframe year regresses AND design family differs   -> PARALLEL_VARIANT  (flag parallel_family)
airframe year regresses, same family                -> evaluated normally, flag chain_order_inversion
```

Design family is the name with trailing numeric suffixes stripped
(`heavy_strike_bomber_3_1` -> `heavy_strike_bomber`). The year test is what
keeps `fighter_7 -> jet_fighter_1` a real transition: the family changes, but
the chain still moves forward in time. A same-family year regression is a real
transition in a suspicious order — it is flagged rather than hidden, because it
usually means the design order in `common/ai_equipment/` is wrong.

**2. Range gate.** `range_target(role)` from the config, default **1000 km for
every role**, individually overridable.

**3. Redesign search** (only when the gate fails). On the new airframe, the
tool walks slots whose `allowed_module_categories` include a fuel/drop-tank
category, plus the engine slot, and tries every combination of up to
`max_slot_changes` slots drawn from the country's plausibly-available module
pool (plus `empty`, since dropping ordnance frees range-relevant capacity).
Candidates that reach the range target are ranked by weighted combat score
against the **new default design**, so the winner is the variant with the least
combat sacrifice. Modules the airframe caps at `count < 1` are excluded.

**4. Verdict.**

```
range_new >= target:
    range_old < target <= range_new and gain < 0          -- range recovery
        gain >= -range_recovery_max_sacrifice
                                   -> SWITCH / SWITCH_CONDITIONAL
        else                       -> KEEP_OLD
    gain < 0                       -> KEEP_OLD            (flat regression)
    significant resource increase  -> SWITCH_CONDITIONAL
    otherwise                      -> SWITCH              (noted if gain < min_net_gain)

range_new < target:
    usable redesign found          -> SWITCH_REDESIGNED   (module list recorded)
    else gain >= range_override_gain
                                   -> SWITCH / SWITCH_CONDITIONAL
                                      (below target but genuinely better, and
                                       nothing on this airframe can fix it)
    else                           -> KEEP_OLD

not a generation step              -> PARALLEL_VARIANT    (see step 1b)
airframe or module unresolvable    -> UNRESOLVED          (row still emitted)
```

The **range recovery** branch exists because the range gate is otherwise
one-sided: it tests only the new design, and `air_range` is deliberately not a
scored stat, so a step whose whole purpose is reach reads as a pure regression.
Without it the tool marked the mod's own Fix 47 (`SOV fighter_mr_7_lr`,
836 -> 1017 km) and Fix 49 (`ENG strategic_bomber_2_lr`, 950 -> 1038 km)
long-range variants `KEEP_OLD`. `range_recovery_max_sacrifice` is the same
"range at any price" guard `max_redesign_sacrifice` applies to the search.

A redesign counts as *usable* when its gain over the old generation clears
`redesign_min_gain` **and** it gives up no more than `max_redesign_sacrifice`
against the new default design — the guard against "range at any price".

`range_override_gain` exists because many 1930s airframes physically cannot
reach 1000 km. Without it the tool would freeze every early-war line on its
first design purely because no biplane has the legs.

**5. Scoring.** A dimensionless weighted relative gain:

```
gain = ( SUM_s  w_s · (new_s − old_s) / max(|old_s|, floor_s) ) / SUM_s |w_s|
```

`w_s` comes from `role_weights[role]` and may be negative (`build_cost_ic` is
`−0.10`, i.e. cheaper is better). `floor_s` from `stat_relative_floors` stops a
`0 → small` change producing an infinite gain. `air_range` is deliberately
**not** in the weights: it is the gate, not a scored stat.

---

## Config knobs (`config.json`)

| Section | Knob | Default | What it does |
| --- | --- | --- | --- |
| `stat_model` | `multiply_base_only` | `false` | Flip the stacking formula (see above) |
| | `thrust_weight_agility_factor` | `1.0` | Mirrors the HOI4 define |
| `range_targets` | `default` + per role | `1000` | Minimum acceptable range, km |
| `role_missions` | `default` + per role | — | Primary HOI4 mission each role is scored as flying; selects which `mission_type_stats` apply |
| `role_weights` | `default` + per role | — | Signed stat weights; negative = lower is better |
| `stat_relative_floors` | per stat | — | Denominator floor for relative change |
| `switch` | `min_net_gain` | `0.05` | Below this a range-passing switch is only "marginal" (noted) |
| | `range_override_gain` | `0.05` | Gain required to adopt a short-ranged, un-redesignable new generation |
| | `redesign_min_gain` | `0.0` | Redesign must beat the old generation by at least this |
| | `max_redesign_sacrifice` | `0.25` | Max combat score the redesign may give up vs the new default |
| | `range_recovery_max_sacrifice` | `0.25` | Max combat score a step may give up when it lifts the design over the range target the old generation missed |
| `resource_significance` | per resource | `1.0`–`2.0` | Per-unit increase that triggers `SWITCH_CONDITIONAL` |
| `redesign` | `enabled` | `true` | Turn the module search off |
| | `max_slot_changes` | `2` | How many slots may be altered at once |
| | `allow_engine_swap` | `true` | Include the engine slot in the search |
| | `range_module_categories` | `extra_fuel`, `drop_tanks`, `fuel_tank` | Category substrings that mark a slot range-relevant |
| | `max_candidates_per_slot` | `24` | Search width per slot |
| `paths` | dirs + globs | — | Where to read from, relative to the mod root |

Keys starting with `_` are documentation and are ignored by the loader.

---

## Diagnostics contract

Repo convention forbids silent truncation. Everything the tool cannot parse or
resolve is recorded, counted by kind, and printed in the report's Diagnostics
section; per-transition problems also land in the CSV `flags` column. A
transition whose airframe or module cannot be resolved is still emitted, with
verdict `UNRESOLVED` — never dropped.

Current state on a full `--all` run: **0 errors, 19 warnings**. Every warning is
listed in the generated report rather than silently dropping a transition.

---

## Known limitations / generator coverage

* **The design layer can be missing the chassis the AI actually builds — run the
  coverage audit.** `ai_equipment` only steers equipment it has a design for.
  When a technology inside a role unlocks a chassis the role's group never
  mentions, the engine auto-designs and builds it, and the ranking, the
  `WA_AI_EQUIPMENT_*` resource gates and the emitted
  `production_upgrade_desire_offset` blocks all miss it. A `--domain tanks` run
  now reports these and writes `output/coverage_gaps.md`; as of 2026-08-13 there
  are **39, of which 11 sit in a branched role**. The case that exposed it: ENG
  builds `tank_eng_medium_chassis_5` (Comet) with 30+ factories from 1944.6
  while `ENG_medium_tanks` stops at the Cromwell — so
  `WA_AI_PRODUCTION_COUNTRY_ENG_TANKS.txt` emits one `+100` and no suppression,
  and the frontier is moot from 1944 on. **A gap is invisible in every other
  output**: the role looks fully covered and simply ranks its top design first.
  Closing one means *authoring the missing design* so the evaluator can rank it.
  The audit deliberately does **not** auto-suppress an uncovered chassis — it has
  not been scored, so a blanket `-100` would be an unevaluated guess, the same
  reasoning `emit_linear` uses when it refuses to decide for shared equipment
  buckets.
* **Generator coverage is intentionally narrower than analysis coverage.** Air
  and modular-tank `SWITCH_CONDITIONAL`, `SWITCH_REDESIGNED`, and linear
  `KEEP_OLD` ladders are encodable. Branched modular-tank groups use a complete
  competitive frontier: every candidate in the shared role gets a global
  quality rank, research controls availability, hard-stat failures become
  low-priority emergency fallbacks (never a production gap), and strategic
  resource shocks temporarily drop a candidate to the next rank. The compiler
  preserves the group's historical maximum factor and assigns lower ranks from
  a configurable geometric `1 / 0.3 / 0.1 / 0.03 / ...` ladder. This keeps the
  best affordable design dominant even if the engine interprets priority as a
  weight rather than a strict maximum. Obsolete file-order supersession hooks
  are neutralised under reversible ownership markers.
  Non-modular infantry/artillery/vehicles still need a verified per-model
  engine lever.
* **Technology topology outranks file order.** Tank succession is read from
  `common/technologies`, with every other ai-equipment role acting as a traversal
  barrier. This is required for graphs such as `M3 Lee -> {Sherman, T20}` which
  later converge on the Pershing. Plane files currently lack explicit per-design
  enable techs, so their legacy linear priority ladder remains the fallback.
* **No speculative translation.** Unsupported decisions remain in the
  manifest and never produce an operation. A successful apply therefore means
  "all planned operations applied", not "all analysis decisions encoded".
* **Role weights are unvalidated priors — now the biggest remaining gap.** They
  were chosen to be plausible, not measured, and several roles omit stats their
  designs plainly care about: `air_maritime_patrol` scores no `air_bombing` or
  `naval_strike_attack`, so the Shackleton's 6x bombing and 9x torpedo gains
  over the Seaford count for nothing; `air_light_bomber` scores no naval strike,
  so an Ar 234 C that gains 6x naval_strike_attack lands at gain +0.014. The
  in-game pilot should check whether the `KEEP_OLD` and `SWITCH_REDESIGNED`
  calls match what a human would do; the weights are the first thing to retune
  if they do not, and no `KEEP_OLD` verdict should be acted on before then.
* **The flat 1000 km range target is a blunt prior.** Historically a Bf 109 E
  (660 km) or a Spitfire (668 km) is a perfectly good point-defence fighter,
  yet the gate freezes those lines or demands drop tanks. Targets should
  plausibly differ by role. See `output/AUDIT_non_switch.md` §6 Tier 3.
* **Detailed combat scoring now covers every requested domain.** Tanks,
  infantry, artillery and vehicles use configurable role weights, hard minimum
  stats, production-efficiency retention and per-resource significance gates.
  Tanks additionally search legal, plausibly available non-armament module
  replacements when reliability or speed misses its role threshold. The tool
  remains report-only: a `SWITCH_CONDITIONAL` identifies the runtime economy
  gate that an emitter must generate; it does not inspect a live country's
  current imports or stockpile offline.
* **No cross-role competition.** Each design group is evaluated in isolation.
  The tool cannot say "build more fighters instead of these bombers".
