# AI Armor Template Generator — Specification and Design Decisions

Date: 2026-09-18. Subject: `armor-template-generator`.
Status: specification before implementation, with approved rules and outstanding design decisions.

This document distinguishes owner-approved decisions, new proposals, and findings from source inspection. The screenshot describes a design; it is not an instruction to implement its changes. This document does not change mod behavior.

## 1. Objective and Approved Concepts

The Python generator must produce the AI armor template files and their template-code calculator from a shared definition. Composition, eligibility, and routing must not be described independently in two manually maintained systems.

Three concepts must remain distinct:

- **Composition family**: light, light support, medium, modern, or heavy.
- **Component selection**: the equipment chosen for each role within the division, according to a priority chain and eligibility conditions.
- **Conversion path**: the progression of existing divisions from one composition to another. This path cannot simply be inferred from the numerical order of template codes.

Priority arrows run from the lowest-priority candidate to the highest-priority candidate. The last eligible candidate wins. Orange heavy candidates participate only when permitted by configuration, without removing other candidates from the chain.

The corrected tank destroyer chain is: **none → mechanized → light → medium → optional heavy → modern**.

The intended progression includes light → medium → modern and light support → medium. Under A5, the existing Soviet light-support conversion to heavy when medium is unavailable is also retained, together with its existing retirement behavior. Variant progression is independent of the main tanks: modern tanks with medium variants are a valid transitional composition. Each variant then advances to modern when eligible. The system must represent different orders of variant availability, rather than a single predetermined sequence.

The “all heavy” restriction depends on the slot, following the owner's clarification on 2026-09-18:

| Slot | Approved rule |
|---|---|
| Armored line battalions | Heavy chassis only; no light, medium, or modern chassis. Motorized/mechanized infantry is not a tank chassis and remains allowed. |
| Armored regimental support | Use the heavy equivalent when one exists. Check the chassis actually required by the unit, not just its name. A4 explicitly permits medium self-propelled artillery as the regimental fallback when no heavy SPG equivalent exists. The owner also explicitly authorizes the existing `heavy_tank_destroyer_company_regimental` despite its medium-chassis requirement; use that unit unchanged. These two named exceptions do not authorize other medium components in the heavy line or regimental slots. |
| Divisional support | The line restriction does not apply. When no heavy equivalent exists, use the closest eligible equivalent for the same role, generally medium, or light if that is the available equivalent. Declare this mapping per role; do not infer a replacement solely from generation order. |

If a composition requires heavy equipment that is unavailable, the calculator must not select that template. This excludes that specific template; it does not require closing the whole family if another eligible composition exists. A divisional support company using its authorized fallback does not make a heavy composition ineligible.

The target combat width of generated divisions is **30**. A3 excludes the former 20-width terrain exceptions from the generated target compositions. A5 still preserves the existing Soviet starting-force and conversion behavior; its source/bridge shapes are not new terrain-based target exceptions. Armoured Waves variants are mandatory and must follow the battalion-count adjustments in the screenshot. Width must be checked after applying doctrine, replacements, and composition modifiers. For Armoured Waves, the owner explicitly requires following the screenshot: preserve its counts rather than rebalance them to force 30. Report the resulting calculated width honestly; do not describe an unverified or different width as 30. This is a specific composition instruction, not restoration of the old terrain exceptions.

## 2. Composition Rules from the Diagram

These rules describe the intended design. Differences from the current code are listed in section 5; unresolved questions are listed in section 6.

| Component | Target rule |
|---|---|
| Main tanks | A base budget of 10 armored line slots, shared between main tanks, medium support, and line variants; never 10 tanks with those components added on top. Priority: light → medium → optional heavy → modern, subject to family restrictions. This chain does not permit modern chassis in a heavy template's line. |
| Medium Support | 6 battalions replacing tanks, reduced to 3 at 300 military factories, then 0 at 500. Without another line variant, this produces 4+6, 7+3, and 10+0 respectively within the budget of 10. Do not confuse this component with infantry-support variants. Competition with line variants follows the approved allocation rule below. |
| Mobile infantry | 5 battalions; motorized → mechanized. |
| Tank destroyers | The corrected chain in section 1; used as regimental support. |
| Assault / infantry support / self-propelled artillery | None → light assault → medium assault → optional heavy assault → light infantry support → medium infantry support → optional heavy infantry support → light self-propelled artillery → medium → optional heavy → modern. A block of 3 line battalions replaces existing armored line battalions according to the allocation rule below; the diagram also includes divisional and regimental support uses. Under A7, assault and infantry-support variants become obsolete only when a higher-priority replacement is eligible for the relevant slot, not merely researched. |
| Self-propelled anti-air | None → light → medium → modern; divisional support. |
| Mobile regimental artillery | Motorized pack artillery → mechanized self-propelled artillery → mechanized rockets → light self-propelled artillery → medium → optional heavy → modern → mechanized rockets, with this final priority capped at 2 of 5 slots. The earlier rocket priority may fill all 5 slots while no later SPG candidate is eligible. Once a later SPG candidate is eligible, use 2 eligible rocket companies plus 3 companies of the highest-priority eligible SPG; without eligible rockets, fill all 5 from the best eligible artillery candidate. |
| Armoured Waves | Mandatory variant: apply the diagram's adjustments, −1 tank battalion and −2 mechanized battalions, and check the resulting width with the doctrine. Keep these screenshot adjustments even if the calculated width differs from the general 30-width objective; do not retain old counts or retune the adjustments to force 30. The −2 instruction names mechanized battalions, not motorized battalions; do not extend that subtraction to motorized infantry. |
| Heavy Support | Heavy support replaces divisional heavy artillery support. |

### Shared Line Budget and Coexisting Variants

**Owner-approved decision:** medium support replaces tanks; the 6/3/0 counts are never added on top of the 10 armored slots. Main tanks, medium support, and other line variants must share the same base budget of 10. The 5 mobile infantry battalions are counted separately. This budget describes the base composition, before the previously requested Armoured Waves adjustment.

**Owner-approved allocation rule:** the 3 battalions in the assault / infantry-support / self-propelled artillery chain replace existing medium support first, then main tanks once the medium-support quota is exhausted. The 6/3/0 counts are therefore the medium-support quota in the absence of those variants, not a minimum to preserve in every composition. The owner approved this replacement priority on 2026-09-18.

The purpose of this rule is to preserve the number of main tanks while medium-support battalions can give up their slots. This design choice does not claim proven combat superiority. Keeping 6 medium support and taking all 3 variant slots from the main tanks would instead produce 1 main tank + 6 medium support + 3 variants; that also totals 10, but reduces main tanks further and is not the selected allocation rule.

Let `S0` be the industrial medium-support quota: 6, 3, or 0 when that component is permitted and eligible, otherwise 0. Let `V` be the selected line-variant count: 3 if a candidate in the line chain is eligible, otherwise 0. The approved rule is `S = max(0, S0 - V)` and `C = 10 - S - V`, where `C` is the main-tank count and `S` is the actual medium-support count.

| Initial medium-support quota | Line variant | Main tanks | Actual medium support | Actual variants | Total armored line battalions |
|---:|---|---:|---:|---:|---:|
| 6 | None | 4 | 6 | 0 | 10 |
| 6 | Eligible self-propelled artillery | 4 | 3 | 3 | 10 |
| 3 | None | 7 | 3 | 0 | 10 |
| 3 | Eligible self-propelled artillery | 7 | 0 | 3 | 10 |
| 0 | None | 10 | 0 | 0 | 10 |
| 0 | Eligible self-propelled artillery | 7 | 0 | 3 | 10 |

Candidates within the line chain replace one another: unlocking both assault guns and self-propelled artillery does not create two separate blocks of 3. A single highest-priority eligible candidate occupies this block.

In the screenshot's current design, tank destroyers occupy regimental support: their availability therefore does not add a line battalion or change this allocation. A division may thus field 4 medium tanks + 3 medium support + 3 self-propelled artillery in the line, with tank destroyers in regimental support. Adding line tank destroyers later would require an explicit rule for sharing the same 10 slots.

The calculator must apply family restrictions before this allocation: a heavy line has a medium-support quota of zero, and only heavy candidates may occupy the variant block. Regimental and divisional support follow their own rules and do not consume the 10 line slots. This does not remove the requirement to calculate the effective width of the complete composition.

Armoured Waves then applies as an explicit transformation of the base composition. Do not automatically put a battalion back after the tank reduction to artificially restore the total to 10; calculate and report the resulting width without overriding the screenshot adjustments. Subtract the specified tank battalion and, where present, the specified two mechanized battalions; do not subtract two motorized battalions in their place or produce a negative battalion count.

## 3. Proposal: The `replace_with` Conversion Contract

### Rule to Include in the Specification

**The generator must explicitly describe conversion paths for existing divisions, in addition to target compositions. Each replacement links an identifiable source composition to an eligible destination, with entry conditions, progression conditions, and an exit condition. A completed conversion must not reactivate its starting composition solely because its bridge remains active. This anti-loop requirement does not prohibit an intentional composition change after reevaluating current conditions under A2.**

The calculator selects the desired composition and, when conversion is necessary, the current step in the path. The generator emits the targets and `replace_with` links needed for that path. Do not assume that a new code alone converts all existing divisions, or mechanically link every pair of consecutive codes.

Each transition must define:

| Logical field | Proposed requirement |
|---|---|
| Source | The existing composition the transition must handle, including starting divisions. |
| Destination | A composition derived from the same shared definition as the normal target. It retains previous variants when their successors are ineligible. |
| Entry | The destination is permitted and its required components are eligible. Recruitment of the old composition must not close before a successor is available, unless retirement is explicitly intended. |
| Step priority | A deterministic entry point; any intermediate and terminal targets must not compete ambiguously. |
| Progression | Explicit match thresholds for the source and destination. Do not reuse a universal threshold without checking the compositions involved. |
| Field conversion | Explicit permission to upgrade already-deployed divisions. Separate this permission from selecting a target for new divisions. |
| Exit | An observable completion criterion and persistent state that prevents the conversion bridge from reactivating. A fixed duration alone must not be presented as proof of completed conversion. |
| Temporarily unavailable destination | Keep the last permitted step or wait; do not delete divisions, force prohibited equipment, or invent a successor. Reevaluate live eligibility under A2, while retaining existing conversion-phase memories and the explicitly retained Soviet retirement behavior under A5. |
| Final target ownership | If conversion prepares a transfer to another recruitment role, generate its terminal target from the composition actually selected for that role, with the same variants and modifiers. |

Proposed organization: generate links local to the template group. When the destination belongs to another group, generate a local terminal target from the destination's shared definition. This duplication in generated output must not become duplication of maintained rules. Actual takeover by the destination role must be verified in game.

The system must support different destinations depending on country state. A link written in the files points to a specific name: the generator may therefore emit several conditional bridges, without exposing competing entry points.

### What the Engine Documentation Says, and the Limits of This Reading

| Finding | Source / limitation |
|---|---|
| **MEASURED** — The documentation states that `enable`, priorities, and `replace_with` participate in selecting a role's target. Declaration order matters when priorities are equal. | Installation: `C:/Jeux/steamapps/common/Hearts of Iron IV/common/ai_templates/_documentation.md`, sections “How do AI templates work?” and “Examples.” |
| **MEASURED** — `replace_at_match` sets the minimum match with the source; `target_min_match` sets the required match with the destination. `can_upgrade_in_field` permits consideration of conversion toward `replace_with`, subject to sufficient manpower and equipment. | Same documentation, `infantry_1` example. This describes the engine; it is not a measurement of an executed conversion. |
| **MEASURED** — All 27 links found across the five armor files point to a target in the same group: 16 in light armor, 11 in light support armor. | Structural inventory of the five files using the parser from `tools/check_templates.py`. No links in the medium, modern, or heavy files. |
| **MEASURED** — WA comments require destinations local to the group and describe risks of returning to an old composition when a bridge remains active. | `common/ai_templates/WA_AI_TEMPLATES_armored_light.txt:1079`; `common/scripted_effects/WA_AI_TEMPLATES_effects.txt:1989`. |
| **ASSUMED** — The exact scope of resolution across groups, the timing of takeover by another role, and conversion delays are not established here through engine observation. | Do not turn WA comments into experimental proof. Plan an in-game test of the new path. |

### Example Paths to Cover

| Situation | Proposed expected path |
|---|---|
| Light divisions, eligible medium tanks | Old light composition → suitable bridge → the medium composition actually selected. |
| Medium tanks, modern main tanks available, modern variants absent | Medium composition → modern main tanks with eligible older variants. |
| Modern tank destroyers ready before modern artillery | Modern composition with modern tank destroyers and medium artillery → composition with modern artillery once eligible. |
| Several variants become ready together | Reach an eligible destination without imposing historical steps that are no longer useful, unless a conversion requirement is demonstrated. |
| Old light divisions still present in the modern era | Provide a path to the current target, without permanently stopping on an old medium composition. Direct conversion or conversion through a medium step must depend on verified conversion constraints. |
| A country acquires foreign technology | Use its actual capabilities and configuration; do not infer equipment solely from its country of origin. |

## 4. Current State Read from the Files

| Element | Sourced finding |
|---|---|
| Files | **MEASURED** — The five files are `WA_AI_TEMPLATES_armored_light.txt`, `_light_support.txt`, `_medium.txt`, `_medium_modern.txt`, and `_heavy.txt`, under `common/ai_templates/`. The structural inventory contains 35, 18, 124, 124, and 30 targets respectively. |
| Existing generation | **MEASURED** — The modern file is already generated from the medium file by `tools/gen/gen_ai_medium_modern_mirror.py`. The `TIER_UP` dictionary retains variants; `COMPOSITION_OVERRIDE` contains modern composition exceptions (`:181`). The project must explicitly integrate or replace this partial generator. |
| Roles and codes | **MEASURED** — Light and light support declare `role = light_armor`. Medium and modern declare `role = medium_armor`. The modern calculator is integrated into the medium calculator with an offset of 500 (`common/scripted_effects/WA_AI_TEMPLATES_effects.txt:1374`). The five families are therefore not five independent roles. |
| Cadence | **MEASURED** — Calls occur at startup and monthly; persistent progression flags are updated before calculation. Medium is calculated before light, which reads its selection. Sources: `common/on_actions/WA_AI_startup_on_actions.txt:17`, `common/on_actions/WA_AI_misc_on_actions.txt:263`, `common/scripted_effects/WA_AI_TEMPLATES_effects.txt:730`. |
| Admission | **MEASURED** — Calculation is gated by default-template use, doctrine spirits, and system admission conditions; the Soviet tank force has an exception. Sources: `WA_AI_TEMPLATES_effects.txt:545` and `:730`. |
| Existing validation | **MEASURED** — Running `python tools/check_templates.py` reported 4 unit-naming convention errors, all in `WA_AI_TEMPLATES_hq.txt:30,33,44,47`, and 0 warnings. No behavior file was changed during this audit. This result does not validate in-game conversions. |

## 5. Cases Missing or Insufficiently Specified in the Initial Specification

| Case | Current source reading | Consequence for the specification |
|---|---|---|
| Production readiness | **MEASURED** — Variant conditions check technology, then stock greater than 100 OR equipment in armies greater than 100 OR a favorable economic condition. Sources: `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt:462`, `common/script_constants/wa_ai_production.txt:96`. | Define whether “produced” means stock, already-deployed equipment, an open production line, or economic capacity. Do not replace this mechanism with a strict stock requirement without providing a way to start production. |
| Production/template coupling | **MEASURED** — Variant production conditions call template-component conditions. Source: `common/scripted_triggers/WA_AI_PRODUCTION_tanks.txt:53` and `:196`. **DERIVED** — Requiring existing stock in a shared condition may also close the production path intended to build that stock. | Separate production startup from permission to convert divisions where necessary. Check shared consumers before changing conditions. |
| Modern tanks with older variants | **MEASURED** — The modern generator retains older variants; `_tiered` conditions delegate to light/medium variant conditions. Sources: `tools/gen/gen_ai_medium_modern_mirror.py:42`, `WA_AI_TEMPLATES_triggers.txt:732`. **DERIVED** — This preserves the fallback but does not by itself express the new complete progression toward modern variants. | Also generate mixed compositions and subsequent modernization for each component role. |
| Mixed heavy compositions | **MEASURED** — The heavy calculator selects branches with modern, medium, or light artillery/anti-air; one heavy composition includes line `medium_support_armor`. Sources: `WA_AI_TEMPLATES_effects.txt:1771`, `common/ai_templates/WA_AI_TEMPLATES_armored_heavy.txt:187`. | Remove non-heavy chassis from the generated line; assess support by slot rather than treating every non-heavy component as a violation. |
| Reconnaissance, engineers, maintenance | **MEASURED** — Medium engineers require 12 medium chassis, medium maintenance requires 10, and light reconnaissance requires 15 light chassis. Sources: `common/units/support_engineer.txt:217`, `support_maintenance.txt:111`, `support_recon.txt:443`, `need` blocks. | Owner-approved divisional fallbacks: medium engineers and maintenance; light reconnaissance when no closer equivalent exists. Do not invent a medium reconnaissance company or a heavy support unit. |
| Heavy regimental support | **MEASURED** — `heavy_assault_gun_company_regimental` requires 6 heavy assault chassis (`common/units/armor_sp_assault.txt:786`). `heavy_tank_destroyer_company_regimental` exists, but its `need` block requires 12 MEDIUM tank destroyer chassis (`common/units/armor_tank_destroyer.txt:722`). The inventory of regimental units in `common/units/*.txt` found no regimental self-propelled artillery consuming heavy chassis. | Heavy assault can be a genuinely heavy candidate. The owner explicitly accepts the existing heavy-named TD with its medium requirement as a named exception. Use medium regimental SPG when no heavy equivalent exists. Do not invent a heavy regimental SPG unit or correct the TD definition as part of this work. |
| Size and terrain | **MEASURED** — Calculators contain 20-width branches for countries configured for mountains/marshes, before other branches; ordinary compositions do not all follow 10 tanks + 5 infantry. Sources: `WA_AI_TEMPLATES_effects.txt:985`, `:1383`, `:1775`, `WA_AI_TEMPLATES_armored_medium.txt:124`. | The requested target is now 30. Do not automatically retain 20-width formats; any exception must be explicitly chosen. |
| Armoured Waves | **MEASURED** — The ordinary mechanized medium composition has 9 tanks + 6 infantry; its Armoured Waves counterpart has 12 + 6. Source: `WA_AI_TEMPLATES_armored_medium.txt:153` and `:1066`. The doctrine writes `combat_width = -0.4` for the listed armored battalions (`common/doctrines/subdoctrines/land/armor_subdoctrines.txt:346`). | Apply the screenshot's rule and verify the complete width calculation. The −1/−2 subtractions alone do not prove a width of 30. Follow the screenshot literally: do not substitute motorized battalions for its mechanized subtraction, and report the calculated width without retuning the prescribed counts. |
| Heavy support | **MEASURED** — A modern composition with heavy support retains heavy artillery and adds the heavy company. Source: `WA_AI_TEMPLATES_armored_medium_modern.txt:1104`. **MEASURED** — Access to heavy support closes the heavy-division family (`WA_AI_TEMPLATES_triggers.txt:278`). | Apply the requested artillery replacement; separately decide whether heavy support and heavy divisions should remain mutually exclusive. |
| Persistent progression | **MEASURED** — Chassis modernization, mechanization, and heavy support have persistent flags. Source: `WA_AI_TEMPLATES_effects.txt:446`, `:502`, `:535`. | Define what is permanently acquired, what is reevaluated, and what is frozen only during conversion. Also address the 300/500 thresholds. |
| Soviet tank force | **MEASURED** — The calculator contains five phases, a special starting composition, a possible heavy destination, and a persistent completion state. Source: `WA_AI_TEMPLATES_effects.txt:1977`. | Decide whether these exceptions belong in the generated definition or remain in separate orchestration. The heavy destination goes beyond the light support → medium path described so far. |
| Retirement versus conversion | **MEASURED** — Event `sov_armor.981` calls deletion of templates and their units, and closes the tank-force program. Sources: `events/WA_AI_SOV.txt:427`, `WA_AI_TEMPLATES_effects.txt:2178`. | Do not confuse conversion with disbanding. Decide whether this retirement remains allowed while unconverted divisions still exist. |
| Obsolescence | **MEASURED** — Some assault variants are excluded as soon as self-propelled artillery technologies are held, before the replacement's economic check. Source: `WA_AI_TEMPLATES_triggers.txt:506`. | Specify whether a variant becomes obsolete when its successor is researched or only when an eligible replacement exists. |
| Multiple conversion targets | **MEASURED** — Light support activates a starter and destination under the same code, with different priorities; some light terminal targets are enabled by conditions without their own code. Sources: `WA_AI_TEMPLATES_armored_light_support.txt:54`, `WA_AI_TEMPLATES_armored_light.txt:1085`. | Replace the overly strict “one code = one active block” rule with “one code = a deterministic path toward a target composition.” |
| Technology trees and configuration | **MEASURED** — Equipment access uses `WA_AI_TECHTREE_has_*` conditions, while family and heavy-support permissions are separate. Sources: `WA_AI_TEMPLATES_triggers.txt:890`, `common/scripted_triggers/WA_AI_CONFIG.txt:649`. | Do not merge permission for a heavy division, permission for a heavy component, and possession of a technology. Keep adopted trees and event-granted technologies within scope. |

## 6. Decision Register

Owner decisions recorded on 2026-09-18. Approved rules below supersede the earlier proposals in the audit's consequence column. A1 retains current behavior; its optional future refinement is not approved. The owner has also resolved the remaining A4, A8, and A9 choices: accept the existing heavy-named TD unchanged, use rockets as an early main option and a later capped complement, and follow the Armoured Waves screenshot without rebalancing its counts to force 30.

| ID | Decision | Approved rule / remaining detail |
|---|---|---|
| A1 | When is a variant ready for transition? | **RETAIN CURRENT BEHAVIOR.** Reuse existing technology, equipment-presence, and economic readiness conditions. Do not add a stock-only gate or a new threshold. See the detailed explanation and optional proposal below. |
| A2 | Should conditions be reevaluated? | **APPROVED: reevaluate as today.** Reevaluate live composition/component conditions; do not introduce blanket permanent acquisition of the new 300/500 industrial quotas. Preserve existing explicit chassis, mechanization, heavy-support, and conversion-phase memories rather than silently deleting them. |
| A3 | Retain terrain-based size exceptions? | **APPROVED: all generated target divisions use the 30-width objective.** Do not retain 20-width terrain exceptions. Existing Soviet source/bridge handling retained by A5 remains necessary to convert starting divisions. |
| A4 | Missing heavy regimental SPG? | **APPROVED: use medium regimental SPG when no heavy equivalent exists.** This is a regimental exception, not permission for medium SPG in the heavy line. **ALSO APPROVED:** use the existing `heavy_tank_destroyer_company_regimental` despite its medium-chassis requirement. Record it as a named exception and leave the unit definition unchanged. |
| A5 | Retain light support → heavy and Soviet retirement? | **RETAIN CURRENT BEHAVIOR**, including the conditional heavy destination, existing phases, and retirement/disbanding path. Preserve these exceptions explicitly in the refactor. |
| A6 | Can heavy support and heavy divisions coexist? | **RETAIN CURRENT BEHAVIOR:** heavy support and the heavy-division family remain mutually exclusive. The already specified replacement of divisional heavy artillery by heavy support remains a separate composition rule. |
| A7 | When does assault / infantry support become obsolete? | **APPROVED:** only when its higher-priority successor is eligible for the relevant slot. Research alone must not remove the previous useful component while its replacement is ineligible. |
| A8 | Must line and regimental artillery choose the same equipment? | **APPROVED:** select independently by slot; at the final capped rocket priority, use up to 2 rocket companies and fill the other 3 slots from the best eligible alternative. **ALSO APPROVED:** the earlier rocket priority can fill all 5 slots while no later SPG candidate is eligible; once a later SPG is eligible, retain rockets as the 2-slot complement. The cap is not universal. |
| A9 | Armoured Waves counts and target width? | **APPROVED: follow the screenshot.** Apply −1 tank and −2 mechanized battalions; do not reinterpret the latter as motorized infantry. Preserve these adjustments rather than retuning them to force 30. Calculate and report effective width; do not claim that the prescribed counts prove width 30. |
| A10 | Compatibility with existing saves? | **APPROVED: development refactor, no save migration required.** Do not add a compatibility mapping or migration framework. Converting divisions during a newly started campaign remains in scope. |
| A11 | Which battalions do line variants replace first? | **APPROVED:** shared base budget of 10; replace medium support first, then main tanks. Quotas 6/3/0 apply before substitution. A quota of 6 plus 3 SPG gives 4 tanks + 3 medium support + 3 SPG. Regimental TD do not alter that allocation. |

### A1 — Retained Eligibility Policy and Optional Refinement

The approved baseline is to preserve existing component eligibility. Do not replace it with an unconditional requirement for equipment already in stock. Preserve component-specific technology and family checks; A7 separately changes the timing of obsolescence.

| Current check | Meaning and source |
|---|---|
| **MEASURED** — Technology and applicable template conditions must pass. | For example, `common/scripted_triggers/WA_AI_TEMPLATES_triggers.txt:473` checks armor-template use and medium TD unlock before its readiness alternatives. |
| **MEASURED** — Stock above 100 OR equipment in armies above 100 passes the equipment-presence branch. | `WA_AI_TEMPLATES_triggers.txt:473`; threshold `common/script_constants/wa_ai_production.txt:96`. These are separate comparisons, not the sum of stock and deployed equipment; exactly 100 does not pass a strict `>` check. |
| **MEASURED** — The small chromium-shock readiness flag can independently satisfy readiness. | `WA_AI_EQUIPMENT_can_absorb_chromium_shock_small`, `common/scripted_triggers/WA_AI_EQUIPMENT_triggers.txt:253`, reads `WA_AI_EQUIPMENT_chr_small_ok`. |
| **MEASURED** — Absence of the major chromium-shortage condition also independently satisfies readiness. | `WA_AI_TEMPLATES_triggers.txt:473`; `common/scripted_triggers/WA_AI_RESOURCE_NEEDS_triggers.txt:405` defines the major-shortage condition using the shortage counter. |
| **DERIVED** — An eligible researched variant can therefore be selected with zero stock and zero deployed equipment if either economic alternative passes. | Inferred directly from the OR block above. This permits selection before equipment has accumulated; it is not proof that a particular division can immediately be fully equipped. |

For the generator, represent these existing conditions as reusable component predicates. Apply family and slot restrictions, then component eligibility, then priority selection. Select an eligible newer variant for each slot; otherwise keep the highest-priority eligible older candidate. Do not add a production-line requirement, sum the two equipment counters, or reinterpret the current threshold as a percentage of the whole army's conversion demand.

**Optional future proposal, not part of the approved baseline:** distinguish “may begin production / be selected as a target” from “ready to convert an existing division.” Keep the current readiness rule for the first question. For the second, investigate a check against the destination's additional equipment requirement for a conversion batch, rather than an arbitrary new global stock count. Existing deployed equipment could support continued use without being treated as free stock for equipping another division. Before proposing numbers or implementation, establish what the engine already checks for field upgrades and what is observable by script. Do not introduce this second gate during the initial refactor without a separate decision.

The purpose of that optional refinement would be to limit premature field conversion while leaving a route to start production. Its feasibility and effect are not established by this static audit.

## 7. Generator Contract and Future Validation

The shared definition must contain families, slots, candidates, priorities, conditions, composition profiles, modifiers, and conversion paths. Classification data remains in CONFIG; shared numbers remain in constants; decision conditions remain in their owning files. Do not generate every theoretical combination without filtering: emit only legal compositions and necessary steps.

Generation must be deterministic, offer a preview and drift checking, and reject missing destinations, incompatible duplicate codes, replacement cycles, nonexistent units, incorrect slots, negative counts, and chassis prohibited in that slot. The chassis audit must read units' actual equipment requirements. It must accept declared divisional fallbacks and the explicit medium-SPG regimental fallback under A4. It must also accept the owner-authorized `heavy_tank_destroyer_company_regimental` with its actual medium-chassis requirement as a named exception. Keep that requirement visible in equipment eligibility and demand checks; do not falsely count it as consuming heavy TD equipment. Other name/equipment mismatches still require review. Heavy support, Armoured Waves, and modern-transition rules must compose without relying on scattered, manually maintained code offsets.

For each composition, produce a detailed width calculation with and without Armoured Waves, accounting for units and applicable modifiers. The target is 30, with no terrain-based size exceptions under A3; any numerical tolerance must be declared and approved, never inferred from the template's name. Armoured Waves is governed by the owner's explicit screenshot instruction: retain −1 tank and −2 mechanized rather than rebalance to force 30, and report any resulting width difference. Do not reopen this design choice solely because the prescribed counts produce a different calculated width.

Validation must cover both sides: selection of new targets and conversion of existing divisions. Include technologies acquired in different orders, permanent absence of a branch, zero stock, stock transferred into armies, shortages, industrial thresholds crossed and later lost, foreign technology, conversion states reached during a new campaign, and coexistence of older compositions. Loading pre-refactor saves does not require migration under A10.

For each conversion, verify the starting state, intermediate stage, arrival, and absence of an unintended bridge-driven return to the starting state after several recalculations in game. Separately test deliberate reevaluation under A2 and retained retirement under A5. Check recruitment, production, and final-role assignment separately. This specification promises no maximum conversion time.

Implementation risks to control: premature closure of a family, selection of equipment that cannot be supplied, return to an old composition, a destination with no matching target, unintended disbanding, or competition between groups sharing the same role. This audit is static; it measures none of those campaign outcomes.
