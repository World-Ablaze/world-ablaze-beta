# AI Armor Template Generator — Technical Implementation Specification

Date: 2026-09-18. Subject: `armor-template-generator`.
Status: all five families are generated. Owner revision 2026-09-19 supersedes the ordinary-light transfer design: post-boundary light targets remain light-only and carry no `replace_with`; only the Soviet light-support family retains its historical conversion graph. Step 6 (in-game validation) is owed.
Functional authority: [WA_AI_ARMOR_GENERATOR_SPEC.md](WA_AI_ARMOR_GENERATOR_SPEC.md), including the latest owner decisions A1-A12.

This document specifies proposed interfaces and algorithms. Paths marked **new** do not exist yet. Statements about existing code are labeled; requirements and proposed designs describe what must be implemented, not measured engine behavior.

## 1. Scope and Non-negotiable Behavior

Implement one Python generator that owns the five armor template files, their generic selection logic, generated selection predicates, and a machine-readable manifest connecting every selection code to its target.

The implementation must preserve:

- Existing startup/monthly scheduling and admission rules. Preserve the ordinary light park as light-only and preserve the Soviet mission, conversion and intentional retirement policy.
- Existing role identities: light and light support share `light_armor`; medium and modern share `medium_armor`; heavy uses `heavy_armor`.
- A1 readiness and A2 reevaluation. `heavy_armor_company_divisional` is the sole exception to the ban on heavy components outside heavy divisions; it is admitted in the medium and modern families only, and never in heavy, light or light-support divisions.
- The approved 10-slot line allocation and independent component progression; no universal upgrade of all variants when the main chassis changes.
- Armoured Waves `combat_width = +0.5`, a flat per-battalion addition, with the exact screenshot adjustments -1 main tank / -2 mechanized; together they hold the wave target at 30. Validate corrected doctrine inputs; do not silently use the installed -0.4 value.
- Heavy priority after all non-heavy candidates, filtered by family and slot before selection, support companies included. Retain explicit non-heavy support fallbacks in heavy divisions; remove the obsolete heavy-TD/medium-equipment waiver.

Countries configured for 20-width divisions still receive 30-width armor targets. The Armoured Waves doctrine correction is an explicit prerequisite of `--apply`, applied by `python tools/gen/gen_ai_armor_templates.py --doctrine-patch` **in the same commit as the generated templates**. **MEASURED (2026-09-19)** - shipping the +0.5 alone makes the CURRENT live templates 37.5 wide (base) and 45 wide (wave twin, 18 battalions) for any country holding the doctrine, so the value and the templates land together or neither does. The generator neither edits doctrine during `--apply` nor substitutes its value silently. No other doctrine redesign is included. No save migration is required. Do not rewrite other infantry templates, change unit equipment definitions, redesign doctrine effects, or add a new recruitment role for modern armor.

## 2. Existing Interfaces and Impact Surface

| Existing interface | Evidence and implementation consequence |
|---|---|
| Scheduling | **MEASURED** — `common/on_actions/WA_AI_startup_on_actions.txt` and `WA_AI_misc_on_actions.txt:263` call progression updates before template calculation. Keep that order and cadence. |
| Orchestration | **MEASURED** — `WA_AI_TEMPLATES_calculate_all_templates` in `common/scripted_effects/WA_AI_TEMPLATES_effects.txt:730` calculates medium before light, and calls the historical light-support path only once per pass. Preserve the call contract. |
| Numeric-to-flag interface | **MEASURED** — `WA_AI_TEMPLATES_update_target_template` takes `_template_type_code` and `_template_value`, clears the corresponding flag, and writes a nonzero value. `common/scripted_localisation/WA_AI_templates_scripted_loc.txt` maps types 4/5/6/14 to light/medium/heavy/light-support flags. Retain this interface. |
| Modern output | **DONE** - `tools/gen/gen_ai_medium_modern_mirror.py` is deleted and `_armored_medium_modern.txt` is written by the new generator as its own family, with its own code range `8000-8999` instead of the +500 offset. The constants group `templates_modern_tier_offset` is retired with it. |
| Existing checker | **MEASURED** — `tools/check_templates.py:557` reads one hard-coded effects file and understands existing code offsets. Its analysis must be extended when generic selectors move to generated files. A wrapper calling another effect is not sufficient for its current scan. |
| Production | **MEASURED** — `common/scripted_triggers/WA_AI_PRODUCTION_tanks.txt` shares component eligibility predicates with template selection. Separate “may produce/use a component” from the generated “wins this slot” predicates. Do not make production contingent on already winning a template slot. |
| Role budget | **MEASURED** — `common/scripted_effects/WA_AI_PRODUCTION_armor_budget.txt` reconciles role shares after calculation. Keep the same role set and weights; a modern chassis is not an additional budget share. |
| Readers requiring audit | **MEASURED** — Searches of `common/`, `events/`, and `tools/` find armor flag/code readers in `WA_AI_TEMPLATES_triggers.txt`, `WA_AI_PRODUCTION_army_composition.txt`, `WA_TEST_templates.txt`, `WA_TEST_armor_budget.txt`, and `WA_TLM_core.txt`, in addition to template files and the old generator. Each must be classified before renumbering. |
| Tests already present | **MEASURED** — `common/scripted_effects/WA_TEST_templates.txt` and `events/wa_test_templates.txt` provide an existing context-checked harness. Extend the actual files rather than relying on an older skill table saying no template harness exists. |

Before applying gameplay output, produce an impact inventory listing every definition, caller, flag reader, numeric range reader, startup/monthly call site, and test consumer affected. Search both exact names and value-range checks; record which consumers remain unchanged, are regenerated, or need a reviewed edit. Country eligibility must come from CONFIG/capability predicates, including adopted trees and granted technologies.

## 3. File Ownership

| Path | Ownership and purpose |
|---|---|
| `tools/armor_templates_registry.json` | EXISTS. Human-maintained schema-versioned families, candidates, chains, slot mappings, composition profiles and exceptions. Ordinary light declares no transition; Soviet light-support conversion remains in its declared profiles and handwritten calculator. No copied technology lists. |
| `tools/gen/gen_ai_armor_templates.py` | EXISTS. CLI entry point, standard library only, resolves the repository root from its own location. |
| `tools/gen/armor_templates/` | EXISTS: `model.py` (registry schema), `inputs.py` (read-only adapters over `common/units`, the scripted triggers, the sub-doctrine and the defines), `resolve.py` (pure resolver + enumeration), `emit.py`, `validate.py`, `transitions.py`. |
| `common/ai_templates/WA_AI_TEMPLATES_armored_{light,light_support,medium,medium_modern,heavy}.txt` | Fully generated. Preserve appropriate role metadata, front-role override, reinforcement priority, icons, and naming groups from explicit registry profiles. |
| `common/scripted_effects/WA_AI_TEMPLATES_ARMOR_generated.txt` | WRITTEN. Generated selection ladders, one effect per template flag. Rendered at 20.7 KiB. |
| `common/scripted_triggers/WA_AI_TEMPLATES_ARMOR_generated.txt` | WRITTEN. Generated decision predicates: the chain winners, the two industrial cuts and the semantic code sets. Rendered at 13.6 KiB. |
| `common/scripted_effects/WA_AI_TEMPLATES_effects.txt` | Retains scheduling-facing wrappers, flag writer, admission/spirit handling, existing progression updates, and Soviet mission/retirement orchestration. Replace generic armor calculation bodies with generated implementations, and deliberately retire conversion-only phases/codes/readers after an impact inventory. |
| `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt` | Retains shared equipment/capability policy. Make A7's obsolescence change in reviewed component predicates; do not duplicate stock/resource tests in generated template blocks. |
| `common/script_constants/wa_ai_armor_templates.txt` **new** | Authoritative shared numeric tuning: base counts, factory thresholds, variant count and Armoured Waves count deltas. The doctrine file owns its Armoured Waves width modifier; register any validation mirror instead of duplicating a tunable doctrine value. Read by Python as input; do not maintain a second numeric copy in JSON. Reuse the existing readiness threshold in `wa_ai_production.txt`. |
| `tools/generated/armor_templates_manifest.json` | WRITTEN. One row per code: name, categorical facts, full composition, width. The ladder computes the code arithmetically, so no per-target trigger conjunction is carried. Rendered at 2.1 MiB. |
| `tools/constants_registry.json` | Reviewed integration edit: register new rendered numeric mirrors and retire the old modern-tier offset group only when its source and mirror are both removed. Not an unrestricted generator rewrite target. |
| `tools/tests/test_armor_templates.py` | EXISTS. 34 hand-authored `unittest` cases over the owner decisions, the code assignment and the rendering. |
| `documentation/WA_AI_DIVISION_TEMPLATES.md` | Update maintenance instructions and code/role model when the implementation ships. |

Retire the old mirror generator as a writer in the same change that transfers ownership. Either remove it after updating every caller, or retain a deprecated forwarding CLI that invokes the new pipeline and cannot emit its old mirror independently.

All game `.txt` output is UTF-8 without BOM, tab-indented, with LF line endings. Each generated file has a source/generator header and `[armor-template-generator]` marker. Files outside the ownership list must remain untouched by generator execution.

## 4. Source Model and Parsed Inputs

### 4.1 Registry structure

Use JSON with `schema_version = 1`; reject unknown fields, duplicate IDs, missing references, and non-integer counts. The following is a schema sketch, not an immediately runnable registry:

```json
{
  "schema_version": 1,
  "families": {},
  "candidates": {},
  "chains": {},
  "profiles": {},
  "transitions": {},
  "exceptions": {}
}
```

| Entity | Required fields |
|---|---|
| Family | ID, output file, role-group ID, engine role, flag, existing type code, admission predicate, chassis selection policy, permitted profiles. |
| Candidate | ID, semantic chassis class, role/capability, actual unit IDs by slot, unlock/eligibility predicate references, optional CONFIG policy reference, successor relationships used by A7. |
| Chain | ID, slot, ordered candidate IDs, empty/default candidate, optional capped-tail rule. Numeric order is explicit; JSON object ordering is not semantic. |
| Profile | ID, family restrictions, mobile-infantry type, support policy, base-count constant references, applied modifiers, metadata, optional preserved mission profile. |
| Profile (DECLARED family) | ID, the codes it answers, then EITHER `facts` - resolved by the same composition rules as any enumerated target - OR explicit `regiments` / `regimental_support` / `support` sections kept verbatim. Optional `replace_with` (must name a profile of the SAME family: a cross-group pointer does not resolve), `replace_at_match`, `target_min_match`, `enable_extra` trigger terms, `custom_icon`, `reinforce_prio`, `upgrade_prio_base`, and `width_exception` naming why this target is not 30 wide. Declaration ORDER is preserved: it is what breaks a tie between two targets at equal upgrade_prio. |
| Transition | Empty for ordinary light. Country-specific light-support conversion remains expressed by declared profiles and handwritten phase logic. |
| Exception | Exact ID, eligible families/slots/unit IDs, reason, owner decision, actual equipment mapping, permitted diagnostic. No wildcard “ignore heavy checks.” |

Keep four different concepts in the model, never aliased: `medium_support` (the 6/3/0 line substitute), `medium_infantry_support` (a candidate in the three-battalion chain), `heavy_divisional_support` (the A6 exception, unit `heavy_armor_company_divisional`, medium and modern only), and `heavy_support_battalion` (unit `heavy_support_armor_battalion_divisional`, used by no template today, scope open under A12).

Example candidate mapping:

```json
{
  "id": "heavy_td",
  "semantic_class": "heavy",
  "eligibility_ref": "WA_AI_TEMPLATES_use_heavy_td_armor",
  "units": {"regimental_support": "heavy_tank_destroyer_company_regimental"},
  "allowed_families": ["heavy"]
}
```

**MEASURED** — Parse actual demand: after upstream commit `e7e9fb979b`, this unit requires 12 heavy TD chassis. Validate that mapping; a medium demand is a regression, not an authorized exception. A1 readiness policy remains separate from actual equipment demand.

`tier_ladder` (optional, per family; A22): `{flag, unit, fallback_unit, max_value}`. `unit` must be
the family's `main_tank`. `emit._tier_blocks` renders N targets per composition group (N = the
composition's count of `unit`), all on the group's codes; `model.py` validates the shape;
`check_templates.py` treats a flag written by `set_country_flag = { flag = F value = N }` in the
templates effects file as reachable at N, so the ladder flag is not reported as calculator-less.

### 4.2 Input adapters

Parse `common/units/*.txt` for unit definitions, slot classification, width, categories, and `need`; parse relevant script constants and doctrine modifiers; index scripted trigger/effect definitions and the existing type map. Every parsed record carries file and source location. Do not infer unit existence or slot legality from naming alone.

**MEASURED** — `tools/equipment_evaluator/pdx.py` exposes `parse_file`, `parse_text`, and an ordered tree preserving duplicate entries and comparison operators. Reuse it through an adapter for read-only input. Do not rewrite existing game files with this parser. Validate that duplicate unit definitions, unsupported expressions, and unresolved inherited data are surfaced rather than silently resolved by a convenience `get` call.

For surgical wrapper extraction, use brace-aware source spans and exact expected definition counts. Refuse to edit if a public effect is missing or duplicated. The one-time integration patch is reviewed separately from recurring generation.

### 4.3 Constants and layers

Shared tuning is declared once in script constants. Registry entries refer to those keys; Python reads their values. Generated numeric literals in unit counts or engine parameters are permitted only as rendered mirrors where constant support is not established, with a generated check and constants-registry ownership. Do not assume `constant:` works in every engine field.

CONFIG remains the sole owner of country classification. New observation predicates use `_has_`/`_is_`; new decisions use `_can_`/`_should_`. Generated consumers call decisions instead of copying tag/date/resource conditions. Existing public `use_*` names remain compatibility interfaces for callers, not a pattern for new names.

## 5. Pure Composition Resolver

Implement a pure function:

```python
resolve(family_id: str, facts: CountryFacts, policy: Registry) -> Selection
```

`CountryFacts` is a test/compile-time representation of booleans and categories, not a Python connection to the running game. Runtime evaluates corresponding scripted predicates. `Selection` is either disabled with a reason, or contains a semantic signature, composition, selected candidates, exceptions and admission context.

### 5.1 Evaluation order

1. Evaluate existing admission and family policy. A disabled family returns code zero through the existing writer. Preserve historical park overrides.
2. Select the main chassis family and mobile-infantry form, honoring existing explicit progression flags. Modern remains a chassis tier of the medium role.
3. Resolve candidate eligibility. Preserve existing unlock and readiness terms, applying A7 as described below.
4. Filter each slot by family before priority selection: heavy candidates only in heavy divisions, support companies included. The single exception is `heavy_armor_company_divisional`, admitted in medium and modern and forbidden in heavy. That exception never authorizes heavy TD/SPG/assault or heavy line components in a medium/modern division, and never admits any heavy component into light or light support.
5. Choose the highest-priority eligible candidate for each chain. Component progress is independent: modern main tanks may keep medium TD/SPG/AA until the corresponding modern candidate wins.
6. Calculate the medium-support quota from current military factories: below 300 → 6, 300–499 → 3, 500 or above → 0; use zero if medium support is ineligible or prohibited for the family. Emit exact boundary comparisons, e.g. `> 299` and `> 499` for integral factory counts, not an unverified `>=` spelling.
7. Allocate armored line counts, then apply Armoured Waves.
8. Resolve regimental and divisional support, including the rocket allocation and heavy-artillery replacement.
9. Validate units/counts/slots, normalize the signature, and select the code/path entry.

### 5.2 Eligibility and obsolescence

A1 remains technology/family prerequisites AND the existing component readiness alternatives. Preserve the strict `> 100` stock and in-armies tests as separate alternatives, plus the current economic alternatives; mechanized components retain their own existing predicates rather than inheriting tank readiness by assumption.

A7 requires an acyclic two-stage model:

- `raw_eligible(candidate, slot)` checks capability, readiness, policy, and slot/family compatibility, without its old “successor merely researched” veto.
- `selected(candidate, slot)` applies chain priorities to raw-eligible candidates. A lower candidate remains a valid fallback until a higher one is raw-eligible for that slot.

Do not implement obsolescence by making two shared `use_*` predicates negate each other. Audit callers of changed assault/infantry-support predicates in research and production; use named helpers to preserve their intended contexts. Availability of a technology granted outside its original tree still counts. A branch absent from a tree is not the same fact as an unresearched technology.

### 5.3 Line allocation

Read the approved constants `B = 10`, `I = 5`, and variant block size `V = 3` (or 0 if no eligible candidate). Let `S0` be the industrial medium-support quota:

```text
S = max(0, S0 - V)
C = B - S - V
line = {main_tank: C, medium_support: S, selected_line_variant: V, mobile_infantry: I}
```

Omit zero-count entries. Before doctrine adjustment, assert `C + S + V == B`. A heavy line has `S0 = 0`; its line variant must be heavy. TD remains regimental and consumes no line slot. One line variant wins; do not add separate three-battalion blocks for assault and SPG. **A21: `selected_line_variant` is the LINE chain's winner only.** The regimental artillery company is `selected(regimental_artillery)`, a separate resolution over the candidates that own a company in that slot, and it consumes no line slot either.

Armoured Waves: require the corrected doctrine modifier `combat_width = +0.5`, flat per battalion, on the declared affected units, then subtract one from the main-tank count and two from mechanized infantry when that form is present. Leave motorized infantry unchanged. Apply exactly once, after allocation; do not refill slots to restore ten. Reject negative counts. This produces a distinct signature and manifest entry. **DERIVED** - base 15 battalions x 2 = 30 and waves 12 x 2.5 = 30, so the wave target must also validate at 30; a wave composition that does not reach 30 is a conflict to report, not an accepted difference. **MEASURED** - the pulled doctrine (`armor_subdoctrines.txt:345-416`, at `e7e9fb979b`) declares `combat_width = -0.4` per armour battalion line and covers no mobile-infantry line, while the armour templates field `infantry_heavy_mechanized_battalion_line` and `infantry_heavy_motorized_battalion_line` (both width 2). Compatibility checking must fail on both mismatches: the wrong value, and a modifier that does not reach the mobile-infantry lines (which would yield 28.5).

### 5.4 Regimental and divisional support

Regimental artillery uses the revised functional chain, **resolved independently of the line chain (A8/A21)**. A chain may only offer candidates that declare a unit for the slot it fills; `model.py` rejects a registry that breaks this, which is what keeps a line-only candidate (infantry support, heavy SPG) out of a regimental chain. Filter candidate family and actual slot availability first:

1. If a heavy division has an eligible real heavy regimental candidate, fill all five artillery slots with it; it outranks even the final capped rocket option. Today that candidate is `heavy_assault_gun_company_regimental`; there is no heavy regimental SPG unit and none is to be fabricated.
2. Otherwise, early rockets may fill five while no later eligible non-heavy candidate exists.
3. With an eligible later non-heavy candidate and rockets, use two rockets plus three of it.
4. Without rockets, use five of it. `medium_spg` inside a heavy division stays the explicitly scoped non-heavy fallback, expressed as an ordinary chain candidate below `heavy_assault`.

**Enumeration.** The line and artillery chains share a candidate set and one rank order, so their winners are not independent coordinates: a candidate that outranks the line winner cannot be eligible. Enumerate the REACHABLE pairs - a pair `(v, a)` is reachable iff the minimal eligibility set `{v, a}` reproduces both winners - and carry them as ONE joint digit. The rectangle would cost 35 values for medium where 11 are reachable, and would overflow the family's declared code range.

TD: none → mechanized → light → medium → modern → heavy. Line/support assault chain: none → light assault → medium assault → light infantry support → medium infantry support → light SPG → medium SPG → modern SPG → heavy assault → heavy infantry support → heavy SPG. Family filtering prevents these terminal heavy choices from entering medium/modern compositions.

Divisional engineer/maintenance/recon/AA use explicit real-unit fallback tables. `heavy_armor_company_divisional` (`common/units/armor_tanks.txt:388`, 12 `heavy_tank_chassis`) is the one deliberate exception: admitted in the medium and modern families, forbidden in heavy, light and light support. On full-slot rungs it replaces `heavy_artillery_mot_company_divisional` and never adds a company on top; on the 20-width rungs it occupies a free slot. Do not apply its exception to any other heavy unit, and do not alias it with `heavy_support_armor_battalion_divisional` (`common/units/armor_support.txt:390`, 25 `heavy_tank_support_chassis`), which no AI template uses and whose scope is open under A12.

**MEASURED** - the fetched correction `e7e9fb979b` modifies `armor_tank_destroyer.txt:756` (`medium_tank_destroyer_chassis` to `heavy_tank_destroyer_chassis`), not SPG; after it, no land `heavy_*` sub-unit declares a light, medium or modern chassis in its `need` block. `armor_sp_artillery.txt` has heavy line/divisional SPG but no heavy regimental SPG. Record the missing slot capability and retain the approved fallback; if later input adds a real heavy regimental SPG, it takes the final priority automatically after validation.

## 6. Compilation, Signatures, and Codes

Build a typed intermediate representation before rendering any file. It must contain both composition and selection behavior; neither the calculator nor template emitter independently reconstructs the rules.

A normalized composition signature contains family, main chassis, motorization, sorted units/counts in all three slot maps, metadata, and owner exceptions. A selection identity additionally contains role group, mission context and admission context.

Enumerate categorical choices after priority resolution, not all combinations of arbitrary country booleans. Prune only combinations proved illegal by declared constraints; do not prune based on historical country assumptions. Record conservative reachability when external predicates are opaque. Deduplicate identical composition payloads internally. Do not emit duplicate destination payloads in source groups merely to build role-conversion ladders.

Assign deterministic positive dense integer codes per flag. The code is COMPUTED, not looked up: each declared axis is one digit of a mixed-radix value, dense inside the family's declared range, with one rectangular plane per mobile-infantry form (the motorized plane carries no Armoured Waves digit). Zero remains disabled; no generic +50/+100/+500 arithmetic survives - the modern family owns `8000-8999` instead of medium+500. Inventory Soviet phase-code readers and retire conversion-only codes together with their effects, triggers, template entries, reports and telemetry readers. No save migration is required.

Keep generated code magnitudes within the already-used 15016 envelope: the largest code rendered today is 8863. Fail on exhaustion rather than widen silently - `--dry-run` prints the per-family plane bases and sizes and the code-budget warning at 80 % of a range.

The manifest maps `(flag, code)` to one deterministic target selection. Produce semantic code-set predicates from the manifest for waves, modern chassis, medium infantry support and heavy support. Replace handwritten numeric bands in tests/readers with these definitions where applicable. Flag presence alone remains distinct from component choice.

### Runtime code selection

Compile the resolver into a nested decision tree over reusable predicates and selected categorical values. Each leaf writes a literal `_template_value`, with a disabled default. Avoid a flat repeated conjunction for every target; share prefixes and component tests. Initialize every `_wa_ag_*` temporary at entry and clear owned scratch at exit; public `_template_type_code` and `_template_value` follow the existing writer contract.

**MEASURED (2026-09-19, `--apply`)** — all five families are generated, in two modes. ENUMERATED: medium 1368, modern 402 and heavy 200 targets. DECLARED: light 30 targets on retained 5100-5222 selector values and light_support 18 on 15000-15016. Current output totals 2018 targets; the manifest declares no ordinary-light transition. The arithmetic encoding keeps the runtime ladder compact by sharing prefixes instead of emitting one full conjunction per target.


Use mutually exclusive branches or explicit first-claim guards. Generated input predicates and the Python resolver must be tested against the rendered script tree, so tests do not merely compare two calls to the same function. Avoid unsupported dynamic identifiers and arbitrary runtime string construction.

Every generated target has exactly one `upgrade_prio` block. Template `enable` calls a generated decision predicate. Preserve group-level zero upgrade weight when no target in that group is selectable; preserve medium-versus-modern and light-versus-light-support ownership gates.

Compute group activity from legal selectable targets. Medium/modern ownership remains mutually exclusive for recruitment selection; light/light-support sharing a role must not produce ambiguous entries. Opening the medium group changes new recruitment and does not transfer ordinary light divisions.

## 7. Ordinary light preservation and Soviet conversion

The medium boundary changes new recruitment only. Historical 51xx/52xx selector values remain for
compatibility, but every emitted ordinary-light target uses light chassis exclusively and emits no
`replace_with` or FINAL. The manifest therefore declares no ordinary light transition.

The Soviet light-support conversion remains a separate system. Preserve its mission admission,
starting-force purpose, phase progression and intentional retirement. Test that path independently
from ordinary light preservation.

## 8. CLI and Safe Publication of Output

```text
python tools/gen/gen_ai_armor_templates.py --dry-run
python tools/gen/gen_ai_armor_templates.py --check
python tools/gen/gen_ai_armor_templates.py --apply
python tools/gen/gen_ai_armor_templates.py --explain tools/tests/fixtures/armor_case.json
```

Invocation without a mode flag defaults to dry-run. `--dry-run` validates and reports changed paths/diff/counts without writing. `--check` validates and compares canonical output byte-for-byte. `--apply` writes only declared outputs after all validation passes. `--explain` is an offline fixture explanation: evaluated facts, rejected candidates, winning chains, allocations, exceptions, and conversion path; it does not claim to read the running game.

Exit codes: 0 success/clean; 1 drift in check mode; 2 invalid input or semantic validation failure; 3 write failure. Resolve imports and paths so execution works outside the repository cwd.

Render and validate all outputs in memory/staging before writes. Capture input/output digests and refuse to overwrite if they changed between planning and apply. Replace individual files safely; a multi-file filesystem update is not assumed atomic. Keep restoration bytes for files replaced during that apply and restore them on a caught write failure; report any incomplete restoration with exact paths. Never delete unrelated files or stage unrelated working-tree changes.

## 9. Static Checks and Tests

| Check | Required assertion |
|---|---|
| Registry/schema | References exist; chains are ordered and acyclic; no raw country tags; documented exemptions have exact scopes. |
| Unit demand | Actual units and slot flags exist; heavy line consumes heavy equipment; corrected heavy TD uses heavy chassis; no land heavy unit declares a non-heavy chassis; no heavy component in a non-heavy family except `heavy_armor_company_divisional` in medium and modern. Support fallback demand remains explicit. |
| Column geometry | Check `same_support_type`, allowed battalion groups, available regiment columns, per-row battalion requirements, and divisional support capacity. A legal total count is insufficient: test normal designer edits and mixed rocket/SPG placement across columns, without emitting CONVERT templates. |
| Counts | Six approved quota/variant examples match; armored line totals 10 before waves; waves applies once; all counts nonnegative; rocket count and remaining artillery sum to five; eligible heavy SPG overrides the capped rocket mix. |
| Width | Calculate effective width for each declared modifier scenario using the flat per-battalion values. Both the base and the Armoured Waves target must satisfy 30 with no implicit tolerance; existing source profiles are the only declared exception. Require the corrected `+0.5` doctrine covering every battalion line the composition fields, mobile infantry included; an uncovered line or an installed -0.4 is a validation error, never an assumed result. 20-width-country armor targets are still 30. Unsupported modifier semantics produce an unresolved-calculation error, never an assumed 30. Do not alter approved counts to hide a conflict. |
| Selection | Zero on genuine closed admission; otherwise a deterministic selectable path; no uncovered code, ambiguous equal-priority entry, or first-branch starvation. |
| Generated behavior | Evaluate an independently parsed subset of rendered selector conditions against hand-authored facts and compare expected selection. Unsupported script syntax fails validation instead of being assumed true. |
| Light behavior | Ordinary light has no transition contract and no `replace_with`; Soviet light-support retains its declared, country-specific conversion graph. |
| Stability | Repeated identical input produces byte-identical output; registry object reordering does not change semantic output; check mode never writes. |
| Consumers | No generic dependency on retired code offsets; checker follows generated effect definitions; semantic test/telemetry readers agree with manifest code sets. |
| Performance | Report emitted targets, edges, bytes, and maximum predicate-tree depth; inspect growth when adding one candidate. Do not disguise multiplicative expansion with a successful syntax check. |

Minimum fixtures: quota boundaries 299/300/499/500; zero/100/101 stock; 60 stock+60 deployed; zero stock with economic admission; modern chassis without modern variants; modern TD before modern SPG and reverse; heavy without heavy SPG; corrected heavy TD requiring heavy; rejection of heavy TD/SPG in medium/modern; the `heavy_armor_company_divisional` exception accepted in medium and in modern and rejected in heavy, light and light support; technology granted outside original tree; no relevant tech branch; heavy support on/off; waves on/off with motorized/mechanized; all rocket stages; A7 researched-but-ineligible successor; resource deterioration under A2; ordinary light preservation across the medium boundary; light-support mission/conversion/retirement boundaries; countries configured for 20-width divisions.

Negative tests must include unknown unit, fabricated heavy SPG, invalid slot, code collision, an ordinary-light transition entry, ordinary-light `replace_with`, stale conversion-phase reader, missing consumer mapping, repeated modifier application, and zero-code transformed into a valid code by an offset.

Expected existing-check commands after implementation:

```text
python -m unittest discover -s tools/tests -p test_armor_templates.py
python tools/gen/gen_ai_armor_templates.py --check
python tools/check_templates.py
python tools/check_constants.py
python tools/check_ai_layers.py
python tools/gen/gen_techtree_membership.py --check
python tools/gen/gen_techtree_gates.py --check
python tools/check_worklist.py
git diff --check
```

**MEASURED** — The earlier audit of this workspace reported four existing HQ naming errors from `check_templates.py`; record the implementation-time baseline. Do not claim that checker passed while those errors remain, and do not fix unrelated HQ content as part of this task. Require no newly introduced errors, separately identifying any baseline failures preventing a completely clean run.

**MEASURED** — The architecture review run for this document reports `check_constants.py` exit 0 (85 groups, 0 errors, 0 warnings) and `check_ai_layers.py` exit 1 for the existing `is_strategic_chromium_exporter` name collision. Treat these as dated baseline results, not validation of future generated code. The registry currently contains `templates_modern_tier_offset`, linking the old effect's `_tier_offset` and old generator's `TIER_OFFSET`; retire that group as part of removing the +500 contract, or the new implementation would leave a stale registry owner/mirror.

**MEASURED** — `common/defines/05_defines.lua:346–356` specifies divisional support dimensions 2×5, regimental support dimensions 5×2, and `REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS = { 3, 3 }`. Medium SPG and mechanized rockets both declare `same_support_type = regimental_arty_guns` (`common/units/armor_sp_artillery.txt:850`, `common/units/land_mot_mech_artillery.txt:382`). Read effective defines from the installed base plus mod overrides; do not copy historical values out of a lesson. **DERIVED** — The reduced Armoured Waves line requires a separate geometry check before assuming all five artillery supports fit. If required screenshot counts and required support slots cannot coexist, emit a precise structural-conflict report with the unit/column requirements; do not silently drop companies, change doctrine, or refill removed battalions. The owner accepted a width difference, not an unbuildable target.

## 10. In-Game Validation and Observability

Extend the existing template report with generated code-to-composition decoding while keeping its measurement walk independent from the production selector. Preserve harness context header, known-false control, and STOP rule. Use its dedicated event file, not `events/wa_events_test.txt`.

Require a full game restart after generated definitions/constants change. Inspect `imgui show ai_templates` and `imgui show ai_division_production`; record selected group/target, best existing template, both match thresholds, actual deployed composition, and requested role counts. A written code only proves selector intent.

Include a live recruitment queue in conversion checks, record engine upgrade/design progress after the restart, and inspect intermediate column layout. Do not interpret an observation made after hot reload as validation of the new designer behavior.

Owner-run scenarios must include a historical major, a country using an adopted/foreign technology path, a minor with no medium unlock, and the Soviet mission/retirement sequence. Test new recruitment separately from already-deployed divisions. Observe that ordinary light stays light-only while new recruitment moves to medium; test the Soviet conversion separately.

Use existing WA_TLM probes when sufficient. Any new save-visible probe follows `documentation/WA_TLM_TELEMETRY_SYSTEM.md`: write-only, initialized, registered, and explicit about whether it measures selection intent or actual unit composition. No gameplay decisions may read telemetry. Do not add a conversion-complete counter based solely on a transition request or spawn command.

The implementation subject remains `SHIPPED-UNTESTED` after a qualifying script commit until the owner runs the harness and records its output in WORK.md. No game test is implied by publication of this design.

## 11. Implementation Sequence and Completion Criteria

| Step | Deliverable and exit condition |
|---|---|
| 1. Inventory | Source/consumer report, unit/slot map, Soviet mission/retirement dependencies and conversion-only readers, measured generator/checker baseline. Every unit named by the functional chains maps to a real definition or explicit fallback. |
| 2. Model and resolver | Registry, constant input adapter, pure resolver, hand-authored fixtures for all owner decisions. No game output applied. |
| 3. Code compiler | Deterministic manifest, selector tree and semantic predicates. Ordinary light has no transition entry. |
| 4. Dry-run rendering | All five files and generated scripts produced consistently; exact destination-payload matching; one owner per output; no duplicate public effect. |
| 5. Integration | Public wrappers delegate, old mirror writer retired, checker and all code readers adapted, production/readiness consumers reviewed, docs synchronized. |
| 6. Validation | Static checks reported honestly; owner cold-start harness records ordinary light preservation, medium recruitment and the separate Soviet light-support conversion. |

Completion means the generator reproduces its committed outputs, every selected code resolves, approved cases are covered by independent tests, and the owner-run checks demonstrate medium recruitment, ordinary light preservation and the separate Soviet conversion behavior.

Primary regression risks: shared eligibility changes unintentionally closing research/production, explosion of generated combinations, ordinary light targets acquiring medium components, Soviet phase counters advancing twice, and a caller continuing to interpret old code ranges. The implementation review must examine both historical and ahistorical paths and verify the explicit owner exceptions.
