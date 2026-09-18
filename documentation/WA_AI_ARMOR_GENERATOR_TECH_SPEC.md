# AI Armor Template Generator — Technical Implementation Specification

Date: 2026-09-18. Subject: `armor-template-generator`.
Status: implementation design; no generator or gameplay change has been implemented by this document.
Functional authority: [WA_AI_ARMOR_GENERATOR_SPEC.md](WA_AI_ARMOR_GENERATOR_SPEC.md), including the latest owner decisions A1–A11.

This document specifies proposed interfaces and algorithms. Paths marked **new** do not exist yet. Statements about existing code are labeled; requirements and proposed designs describe what must be implemented, not measured engine behavior.

## 1. Scope and Non-negotiable Behavior

Implement one Python generator that owns the five armor template files, their generic selection logic, generated selection predicates, and a machine-readable manifest connecting every selection code to its targets and conversion path.

The implementation must preserve:

- Existing startup/monthly scheduling, admission rules, explicit progression memories, and the Soviet mission/conversion/retirement state machine.
- Existing role identities: light and light support share `light_armor`; medium and modern share `medium_armor`; heavy uses `heavy_armor`.
- A1's existing readiness alternatives and threshold, A2's live reevaluation, A5's Soviet heavy alternative and retirement, and A6's heavy-support/heavy-division exclusion.
- The approved 10-slot line allocation and independent component progression; no universal upgrade of all variants when the main chassis changes.
- The exact Armoured Waves adjustments, including their explicit precedence over attempts to force a calculated width of 30.
- The named regimental exceptions: medium SPG when no heavy equivalent exists, and the existing heavy TD unit despite its medium-equipment requirement.

No save migration is required. New campaigns must still convert their starting and subsequently created divisions. Do not rewrite other infantry templates, change unit equipment definitions, redesign doctrine effects, or add a new recruitment role for modern armor.

## 2. Existing Interfaces and Impact Surface

| Existing interface | Evidence and implementation consequence |
|---|---|
| Scheduling | **MEASURED** — `common/on_actions/WA_AI_startup_on_actions.txt` and `WA_AI_misc_on_actions.txt:263` call progression updates before template calculation. Keep that order and cadence. |
| Orchestration | **MEASURED** — `WA_AI_TEMPLATES_calculate_all_templates` in `common/scripted_effects/WA_AI_TEMPLATES_effects.txt:730` calculates medium before light, and calls the historical light-support path only once per pass. Preserve the call contract. |
| Numeric-to-flag interface | **MEASURED** — `WA_AI_TEMPLATES_update_target_template` takes `_template_type_code` and `_template_value`, clears the corresponding flag, and writes a nonzero value. `common/scripted_localisation/WA_AI_templates_scripted_loc.txt` maps types 4/5/6/14 to light/medium/heavy/light-support flags. Retain this interface. |
| Modern output | **MEASURED** — `tools/gen/gen_ai_medium_modern_mirror.py` currently owns `_armored_medium_modern.txt`, with a +500 offset and composition overrides. Replace its ownership explicitly; it must not remain a second writer. |
| Existing checker | **MEASURED** — `tools/check_templates.py:557` reads one hard-coded effects file and understands existing code offsets. Its analysis must be extended when generic selectors move to generated files. A wrapper calling another effect is not sufficient for its current scan. |
| Production | **MEASURED** — `common/scripted_triggers/WA_AI_PRODUCTION_tanks.txt` shares component eligibility predicates with template selection. Separate “may produce/use a component” from the generated “wins this slot” predicates. Do not make production contingent on already winning a template slot. |
| Role budget | **MEASURED** — `common/scripted_effects/WA_AI_PRODUCTION_armor_budget.txt` reconciles role shares after calculation. Keep the same role set and weights; a modern chassis is not an additional budget share. |
| Readers requiring audit | **MEASURED** — Searches of `common/`, `events/`, and `tools/` find armor flag/code readers in `WA_AI_TEMPLATES_triggers.txt`, `WA_AI_PRODUCTION_army_composition.txt`, `WA_TEST_templates.txt`, `WA_TEST_armor_budget.txt`, and `WA_TLM_core.txt`, in addition to template files and the old generator. Each must be classified before renumbering. |
| Tests already present | **MEASURED** — `common/scripted_effects/WA_TEST_templates.txt` and `events/wa_test_templates.txt` provide an existing context-checked harness. Extend the actual files rather than relying on an older skill table saying no template harness exists. |

Before applying gameplay output, produce an impact inventory listing every definition, caller, flag reader, numeric range reader, startup/monthly call site, and test consumer affected. Search both exact names and value-range checks; record which consumers remain unchanged, are regenerated, or need a reviewed edit. Country eligibility must come from CONFIG/capability predicates, including adopted trees and granted technologies.

## 3. File Ownership

| Path | Ownership and purpose |
|---|---|
| `tools/armor_templates_registry.json` **new** | Human-maintained schema-versioned families, candidates, chains, slot mappings, composition profiles, exceptions, and transition profiles. No country-tag lists or copied technology lists. |
| `tools/gen/gen_ai_armor_templates.py` **new** | CLI entry point. Resolve repository root from the script location. Standard library only. |
| `tools/gen/armor_templates/` **new** | Small implementation package: `model.py`, `inputs.py`, `resolve.py`, `transitions.py`, `emit.py`, `validate.py`. Avoid a framework with one class per template. |
| `common/ai_templates/WA_AI_TEMPLATES_armored_{light,light_support,medium,medium_modern,heavy}.txt` | Fully generated. Preserve appropriate role metadata, front-role override, reinforcement priority, icons, and naming groups from explicit registry profiles. |
| `common/scripted_effects/WA_AI_TEMPLATES_ARMOR_generated.txt` **new** | Generated generic selection effects. Contains no duplicate definitions of public wrappers. |
| `common/scripted_triggers/WA_AI_TEMPLATES_ARMOR_generated.txt` **new** | Generated decision predicates for candidate winners, template activation, semantic code sets, and bridge entry/exit conditions. |
| `common/scripted_effects/WA_AI_TEMPLATES_effects.txt` | Retains scheduling-facing wrappers, flag writer, admission/spirit handling, existing progression updates, and Soviet phase orchestration. Replace only generic armor calculation bodies with calls to generated implementations. |
| `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt` | Retains shared equipment/capability policy. Make A7's obsolescence change in reviewed component predicates; do not duplicate stock/resource tests in generated template blocks. |
| `common/script_constants/wa_ai_armor_templates.txt` **new** | Authoritative shared numeric tuning: base counts, factory thresholds, variant count, Armoured Waves deltas, and transition thresholds. Read by Python as input; do not maintain a second numeric copy in JSON. Reuse the existing readiness threshold in `wa_ai_production.txt`. |
| `tools/generated/armor_templates_manifest.json` **new** | Generated signatures, codes, group ownership, conditions, full slot compositions, actual equipment demand, conversion edges, exemptions, and input digests. No timestamps in deterministic artifacts. |
| `tools/constants_registry.json` | Reviewed integration edit: register new rendered numeric mirrors and retire the old modern-tier offset group only when its source and mirror are both removed. Not an unrestricted generator rewrite target. |
| `tools/tests/test_armor_templates.py` **new** | Hand-authored fixtures and semantic/compiler/CLI tests using `unittest`. |
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
| Profile | ID, family restrictions, mobile-infantry type, support policy, base-count constant references, applied modifiers, metadata, optional preserved legacy phase. |
| Transition | ID, source-profile set, destination-profile rule, local group, entry condition, source-presence condition, phase/exit handling, match thresholds, destination pinning policy. |
| Exception | Exact ID, eligible families/slots/unit IDs, reason, owner decision, actual equipment mapping, permitted diagnostic. No wildcard “ignore heavy checks.” |

Keep three different concepts in the model: `medium_support` (the 6/3/0 substitute), `medium_infantry_support` (a candidate in the three-battalion chain), and `heavy_divisional_support` (a support company). Their names must never alias.

Example candidate mapping:

```json
{
  "id": "heavy_td",
  "semantic_class": "heavy",
  "eligibility_ref": "WA_AI_TEMPLATES_use_heavy_td_armor",
  "units": {"regimental_support": "heavy_tank_destroyer_company_regimental"},
  "exceptions": ["owner_heavy_td_uses_medium_equipment"]
}
```

The example's semantic class does not override the equipment definition. Parse the unit's actual `need` block and report medium TD demand. Preserve its current availability policy under A1; do not silently add a new medium-stock threshold because the unit is an exception.

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

`CountryFacts` is a test/compile-time representation of booleans and categories, not a Python connection to the running game. Runtime evaluates corresponding scripted predicates. `Selection` is either disabled with a reason, or contains a semantic signature, composition, selected candidates, exceptions, and transition context.

### 5.1 Evaluation order

1. Evaluate existing admission and family policy. A disabled family returns code zero through the existing writer. Preserve historical park overrides.
2. Select the main chassis family and mobile-infantry form, honoring existing explicit progression flags. Modern remains a chassis tier of the medium role.
3. Resolve candidate eligibility. Preserve existing unlock and readiness terms, applying A7 as described below.
4. Filter each slot's candidates by family restrictions and exact owner-authorized exceptions. Filter before priority selection.
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

Omit zero-count entries. Before doctrine adjustment, assert `C + S + V == B`. A heavy line has `S0 = 0`; its line variant must be heavy. TD remains regimental and consumes no line slot. One line variant wins; do not add separate three-battalion blocks for assault and SPG.

Armoured Waves: subtract one from the main-tank count and two from mechanized infantry when that form is present. Leave motorized infantry unchanged. Apply exactly once, after allocation; do not refill slots to restore ten. Reject negative counts. This produces a distinct signature and manifest entry. Report the width difference from 30 as an explicit owner-accepted Armoured Waves diagnostic, not an excuse to change counts.

### 5.4 Regimental and divisional support

Regimental artillery uses the approved chain in the functional specification:

- Without an eligible SPG candidate later than the early rocket position, early rockets may occupy all five artillery slots if they win.
- If a later SPG candidate and rockets are both eligible, use two rocket companies plus three companies of the highest eligible SPG.
- Without eligible rockets, give all five to the highest eligible artillery candidate.
- Aggregate repeated unit IDs; never emit duplicate keys as a way to express counts.

The TD chain is none → mechanized → light → medium → optional heavy → modern, filtered for the family. The heavy TD named exception remains available in its allowed regimental context despite its actual medium demand. The heavy-family medium-SPG exception is also limited to regimental support.

Divisional engineer/maintenance/recon and other support use an explicit per-role fallback table. No generic “nearest chassis” arithmetic: the registry must map real unit IDs. Heavy support replaces divisional heavy artillery: require at most one of the pair in the final composition. Selection of divisional support must not alter the ten-slot line budget.

## 6. Compilation, Signatures, and Codes

Build a typed intermediate representation before rendering any file. It must contain both composition and selection behavior; neither the calculator nor template emitter independently reconstructs the rules.

A normalized composition signature contains family, main chassis, motorization, sorted units/counts in all three slot maps, metadata, and owner exceptions. A selection identity additionally contains role group, phase, admission context, and transition destination. Two identical compositions with different conversion semantics must not be merged as one target.

Enumerate categorical choices after priority resolution, not all combinations of arbitrary country booleans. Prune only combinations proved illegal by declared constraints; do not prune based on historical country assumptions. Record conservative reachability when external predicates are opaque. Deduplicate identical composition payloads internally; emit local copies when group ownership requires them.

Assign deterministic positive dense integer codes per flag from sorted selection identities. Zero remains disabled. A code is opaque; no arithmetic +50/+100/+500 convention in the new generic system. Reserve light-support values 15000–15016 while the retained Soviet state machine reads/writes those values; reserve additional legacy values only when the integration inventory demonstrates a live retained reader. This is preservation of current orchestration, not save migration.

Keep generated code magnitudes within the already-used 15016 envelope for the first implementation: fail on exhaustion rather than widen silently. Emit counts before writing: signatures per family, targets per group, bridges, output bytes, and largest code. This is a conservative encoding limit, not a claim about the engine's maximum supported integer.

The manifest maps `(flag, code)` to one deterministic entry/path, not necessarily one active target block. Produce semantic code-set predicates from the manifest for waves, modern chassis, medium infantry support, heavy support, and transition phases. Replace handwritten numeric bands in tests/readers with these definitions where applicable. Flag presence alone remains distinct from component choice.

### Runtime code selection

Compile the resolver into a nested decision tree over reusable predicates and selected categorical values. Each leaf writes a literal `_template_value`, with a disabled default. Avoid a flat repeated conjunction for every target; share prefixes and component tests. Initialize every `_wa_ag_*` temporary at entry and clear owned scratch at exit; public `_template_type_code` and `_template_value` follow the existing writer contract.

Use mutually exclusive branches or explicit first-claim guards. Generated input predicates and the Python resolver must be tested against the rendered script tree, so tests do not merely compare two calls to the same function. Avoid unsupported dynamic identifiers and arbitrary runtime string construction.

Every generated target has exactly one `upgrade_prio` block. Template `enable` calls a generated decision predicate. Preserve group-level zero upgrade weight when no target in that group is selectable; preserve medium-versus-modern and light-versus-light-support ownership gates.

Compute group activity from the generated selectable code/path set, including active bridges. Do not copy a chassis-latch-only group shutdown if it would disable the old group's bridge to the new chassis. During a medium→modern bridge, its code belongs to the source group and enables the local modern terminal there; the normal modern group must not concurrently become the recruitment entry for the same selection identity. Transition exit selects the normal destination entry. For separate light/light-support flags sharing a role, preserve their existing ownership policy and test both flags together. This is an entry-ownership rule, not a new recruitment role or budget share.

## 7. Conversion Graph and Existing-Division Handling

Generate explicit local `replace_with` graphs from declarative transition profiles. A profile is a conversion need, not a link between consecutive numeric codes. Preserve threshold pairs from existing profiles as initial data, then verify each new composition pair in game. Both `replace_at_match` and `target_min_match` must be present and tested.

For each supported source shape and selected destination:

1. Generate a source-matching bridge only when that source is present and the transition's admission conditions hold.
2. Generate the terminal target in the same role group from the destination's complete resolved payload: line, regimental support, divisional support, metadata, and doctrine form. Do not copy only its main battalions.
3. Give bridge and terminal explicit priorities and deterministic declaration order; ensure the terminal is enabled whenever its bridge can point to it.
4. Give the bridge an exit condition based on available source-presence checks and retained phase state. Absence of a selection flag alone is not proof all divisions converted.
5. Keep generic live destination reevaluation under A2. Preserve the existing Soviet pinned destination/class/motorization where its phase machine requires it. An intentional new decision is not an accidental bridge loop.

Cover starting light divisions, starting light-support brigade/corps shapes, light→medium, medium-chassis→modern-chassis, and independent component upgrades/downgrades selected under A2. Source profiles must include intermediate compositions the generator can emit; a path that only handles starting units does not cover a later partially modernized division.

Do not generate the unrestricted Cartesian product of every old and new target. Author allowed transition axes and source-presence equivalence classes; compose multi-axis changes through explicit intermediate steps when required. Any unresolved source class must appear in a coverage error, not silently disappear. The first implementation must report graph size and prove path coverage for all generated source signatures before applying output.

Prior design objection: **MEASURED** — The lessons review found the earlier concern “~9 000 generated lines a massive complexity increase” in `.claude/skills/wa-lessons-learned/references/lessons-log.md:2642`. This design covers that concern because the maintained source is a shared registry and pure resolver, generated targets are deduplicated where semantics permit, transition profiles restrict pairing, and every dry-run reports total output size and growth. These measures make complexity visible; they do not establish that a large generated output is harmless to the engine. If the graph still expands excessively, revise the representation before applying output rather than hand-maintain thousands of exceptions.

**MEASURED** — The same lessons review identifies “The field-upgrade destination is the FINAL's best EXISTING match, not the FINAL” (`lessons-log.md:2627`). The runtime test must therefore inspect competing existing templates, including heavy shapes, not merely compare generated FINAL payloads. Test both thresholds against an intermediate composition reachable through the actual designer edits.

**ASSUMED** — Static graph validity does not prove engine matching or field conversion. Whether same-role target reselection suffices for a particular component change must be established through a cold-start owner test. The technical requirement is coverage of fielded divisions, not “every change must have its own bridge.” Omit a bridge only when the simpler path has validation evidence recorded for that transition class.

### Soviet compatibility island

Retain the current MISSION → BRIDGE → STABLE → CONVERT-1 → CONVERT-2 orchestration, counters, destination memory, and retirement event. Represent its exact starting/phase target payloads as explicitly named registry profiles, not undocumented exceptions in emitter code. Preserve starting shapes and timing even though generic terrain exceptions are removed. Its terminal forms must remain consistent with the retained behavior; any intentional alignment to new generic targets requires comparison of full payloads and the owner-run conversion test.

The historical path must advance once per existing monthly calculation. An explain/report command must never call the real phase-advancing calculator. Do not “test idempotence” by invoking a phase counter twice and then treating the extra pulse as a gameplay result.

## 8. CLI and Safe Publication of Output

```text
python tools/gen/gen_ai_armor_templates.py --dry-run
python tools/gen/gen_ai_armor_templates.py --check
python tools/gen/gen_ai_armor_templates.py --apply
python tools/gen/gen_ai_armor_templates.py --explain tools/tests/fixtures/armor_case.json
```

No flag defaults to dry-run. `--dry-run` validates and reports changed paths/diff/counts without writing. `--check` validates and compares canonical output byte-for-byte. `--apply` writes only declared outputs after all validation passes. `--explain` is an offline fixture explanation: evaluated facts, rejected candidates, winning chains, allocations, exceptions, and conversion path; it does not claim to read the running game.

Exit codes: 0 success/clean; 1 drift in check mode; 2 invalid input or semantic validation failure; 3 write failure. Resolve imports and paths so execution works outside the repository cwd.

Render and validate all outputs in memory/staging before writes. Capture input/output digests and refuse to overwrite if they changed between planning and apply. Replace individual files safely; a multi-file filesystem update is not assumed atomic. Keep restoration bytes for files replaced during that apply and restore them on a caught write failure; report any incomplete restoration with exact paths. Never delete unrelated files or stage unrelated working-tree changes.

## 9. Static Checks and Tests

| Check | Required assertion |
|---|---|
| Registry/schema | References exist; chains are ordered and acyclic; no raw country tags; documented exemptions have exact scopes. |
| Unit demand | Actual units and slot flags exist; heavy line consumes heavy equipment; allowed regimental exceptions report their true demand. |
| Column geometry | Check `same_support_type`, allowed battalion groups, available regiment columns, per-row battalion requirements, and divisional support capacity. A legal total count is insufficient: test reachable intermediate edits and mixed rocket/SPG placement across columns. |
| Counts | Six approved quota/variant examples match; armored line totals 10 before waves; waves applies once; all counts nonnegative; rocket count and remaining artillery sum to five. |
| Width | Calculate effective width for each declared modifier scenario. Ordinary final targets must satisfy 30 with no implicit tolerance. Named preserved starting/bridge profiles and the exact owner-prescribed Armoured Waves transform are the only declared exceptions. Unsupported modifier semantics produce an unresolved-calculation error, never an assumed 30. Do not alter approved counts to hide a conflict. |
| Selection | Zero on genuine closed admission; otherwise a deterministic selectable path; no uncovered code, ambiguous equal-priority entry, or first-branch starvation. |
| Generated behavior | Evaluate an independently parsed subset of rendered selector conditions against hand-authored facts and compare expected selection. Unsupported script syntax fails validation instead of being assumed true. |
| Conversion | All referenced targets are local/existent/enabled under source conditions; graph has no unintended cycle; required sources reach destinations; final payload equals its intended resolved destination. |
| Stability | Repeated identical input produces byte-identical output; registry object reordering does not change semantic output; check mode never writes. |
| Consumers | No generic dependency on retired code offsets; checker follows generated effect definitions; semantic test/telemetry readers agree with manifest code sets. |
| Performance | Report emitted targets, edges, bytes, and maximum predicate-tree depth; inspect growth when adding one candidate. Do not disguise multiplicative expansion with a successful syntax check. |

Minimum fixtures: quota boundaries 299/300/499/500; zero/100/101 stock; 60 stock+60 deployed; zero stock with economic admission; modern chassis without modern variants; modern TD before modern SPG and reverse; heavy without heavy SPG; accepted heavy TD requiring medium; technology granted outside original tree; no relevant tech branch; heavy support on/off; waves on/off with motorized/mechanized; all rocket stages; A7 researched-but-ineligible successor; resource deterioration under A2; light-support mission and phase boundaries; no destination class; delayed light conversion at modern era.

Negative tests must include unknown unit, fabricated heavy SPG, invalid slot, code collision, destination outside group, disabled destination, stale phase target, missing consumer mapping, repeated modifier application, and zero-code transformed into a valid code by an offset.

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

Owner-run scenarios must include a historical major, a country using an adopted/foreign technology path, a minor with no medium unlock, and the Soviet mission/retirement sequence. Test new recruitment separately from already-deployed divisions. Observe the source, intermediate stage, terminal stage, and later reevaluation; do not infer completion from a single flag or a monthly elapsed-time count.

Use existing WA_TLM probes when sufficient. Any new save-visible probe follows `documentation/WA_TLM_TELEMETRY_SYSTEM.md`: write-only, initialized, registered, and explicit about whether it measures selection intent or actual unit composition. No gameplay decisions may read telemetry. Do not add a conversion-complete counter based solely on bridge activation.

The implementation subject remains `SHIPPED-UNTESTED` after a qualifying script commit until the owner runs the harness and records its output in WORK.md. No game test is implied by publication of this design.

## 11. Implementation Sequence and Completion Criteria

| Step | Deliverable and exit condition |
|---|---|
| 1. Inventory | Source/consumer report, unit/slot map, all preserved Soviet profiles, measured generator/checker baseline. Every unit named by the functional chains maps to a real definition or explicit fallback. |
| 2. Model and resolver | Registry, constant input adapter, pure resolver, hand-authored fixtures for all owner decisions. No game output applied. |
| 3. Code and graph compiler | Deterministic manifest, selector tree, conversion graph, code-set predicates. Structural and path coverage checks pass; output size is reported and reviewed. |
| 4. Dry-run rendering | All five files and generated scripts produced consistently; exact full-payload terminal matching; one owner per output; no duplicate public effect. |
| 5. Integration | Public wrappers delegate, old mirror writer retired, checker and all code readers adapted, production/readiness consumers reviewed, docs synchronized. |
| 6. Validation | Static checks reported honestly; owner cold-start harness and field-conversion results recorded; expected A5 retirement distinguished from unintended unit loss. |

Completion means the generator reproduces its committed outputs, every selected code resolves, approved cases are covered by independent tests, and the owner-run checks demonstrate recruitment and conversion behavior. No claim of bounded conversion duration is part of this design.

Primary regression risks: shared eligibility changes unintentionally closing research/production, explosion of generated combinations, destination payload mismatch, bridge reactivation, empty role entries still receiving upgrade priority, Soviet phase counters advanced twice, and a caller continuing to interpret old code ranges. The implementation review must examine both historical and ahistorical paths and verify the explicit owner exceptions rather than “cleaning them up.”
