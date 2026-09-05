# Tracking-system redesign (proposal, 2026-08-23)

Draft validated and applied (phase A + B) on 2026-08-23. Kept as the record of the diagnosis,
the decisions and the migration mapping.

## 1. Diagnosis (MEASURED, tree as of 2026-08-23)

| Reported symptom | Measurement | Cause |
| --- | --- | --- |
| The single-subject rule blocks parallel work | The single ACTIVE entry of `QUEUE.md` bundled **9 fixes** (Fix 120–128) under one title; that is the rule being worked around, not respected. | The rule constrained the *file*, not the *session*. Working in parallel forced lying to the file. |
| Checklist and queue duplicate each other | 3 live ledgers: `QUEUE.md` (34 QUEUE + 35 DONE rows), `checklist.md` (2685 lines, ~43 R-items, 1 item = 1 fix), `fix_registry.json` (121 numbers). One subject existed in all three (e.g. Fix 92: QUEUE 13 + R7b + R57 + registry). | Three keys (subject / R-item / Fix number) for one object: the *intended behaviour*. |
| The system creates useless tasks | **28 of 35** DONE rows in `QUEUE.md` were meta-work (checker, registry, engine docs, skills, ledger, statuses), not mod behaviour. The checker had **23 rules** (622 lines); half of them policed the consistency of the three ledgers with each other (LEDGER-*, PROBE-UNRUN, NEVER-SCORED, FIX-*, STATUS-*). | Every checker rule manufactures its own category of task. The system was working on itself. |
| No console test after a big change | 7 `WA_TEST_*` harnesses existed, but no rule linked "I changed `WA_AI_lend_lease_effects.txt`" to "run `WA_TEST_lend_lease_relief`". Result: lend-lease broken for a week with no signal. | The test was a good practice, not a subject state. |
| Fix numbering unreadable | **667** `# Fix NN` comments, 135+ numbers, Fix 47 cited 42 times, Fix 97 36 times. Fix→Fix→Fix chains (e.g. 100 → 101 → 102, 87 → 87b). Comment ratio 16% to **31%** (`PRIORITY_core.txt`). | A *commit*-level number was used as a *design*-level identifier. A subject fixed in three passes got three numbers and three comments instead of one. |

## 2. Principle of the redesign

**One object: the SUBJECT.** A subject = one intended behaviour, named by a stable slug
(`lend-lease-relief`, `na-corridor`, `ita-garrison`). Everything attaches to it: commits, code
comments, campaign probe, console harness. Fix numbers, R-items and queue rows disappear in
favour of this single identifier.

## 3. What changes

### 3.1 One file: `WORK.md` (replaces QUEUE.md + checklist R-items + fix_registry.json rules)

One entry per subject, four mandatory fields:

| Field | Content |
| --- | --- |
| Subject (slug) | `ita-garrison` |
| State | `OPEN` → `SHIPPED-UNTESTED` → `TESTED` → `CAMPAIGN-OK` → `CLOSED`; or `PARKED` with its state at parking time |
| Closed when | measurable criterion, one sentence |
| Verification | console harness (`WA_TEST_xxx`) **and/or** campaign probe, one line each |

- Several open subjects: allowed. The single-subject rule becomes **"one session = one subject"**:
  each session names its subject in its first message; an off-subject discovery becomes at most a
  *proposed* entry, which the owner accepts or refuses. Soft limit: ≤ 4 non-`PARKED` subjects.
- **Admission rule** (this is what stops useless tasks): an entry enters `WORK.md` only if (a) the
  owner asked for it **or** (b) it rests on a MEASURED symptom (save, playthrough report) **and**
  concerns mod behaviour. Meta-work (tooling, docs, checker, skills): never without an explicit
  request. Default = do not add; report in one line at end of session.
- `FUNDAMENTAL` F1–F9 of the checklist: kept as they are in `checklist.md`, reduced to those 9
  items + the campaign registry. R-items are either closed (streak reached → deleted) or folded
  into their subject's *Verification* field.
- `fix_registry.json`: frozen into `documentation/FIX_HISTORY.md` (number → commit → subject
  slug), read-only, no checker rule.

### 3.2 Mandatory test after a big scripted-effect change

- **System → harness → console command** table in `wa-testing` (and in the harness file header).
- Any commit touching `common/scripted_effects/WA_AI_*` or `common/scripted_triggers/WA_AI_*` of a
  system that has a harness puts its subject in **`SHIPPED-UNTESTED`**; the subject only moves to
  `TESTED` once the owner has run the harness in the console and pasted the output into `WORK.md`.
- System without a harness + "big" change (proposed threshold: > 40 lines, or any signature/scope
  change of an effect called by an on_action): the subject **includes writing the harness** before
  `SHIPPED`.
- Checker: `SHIPPED-UNTESTED` for > 3 days = ERROR. The one rule that would have caught lend-lease.

### 3.3 The checker shrinks to 5 rules

| Rule | Kept because |
| --- | --- |
| `BOM-IN-SCRIPT` | real silent breakage |
| `HARNESS-CONTRACT` | a harness without context already produced a false result |
| `NO-EXIT` (subject without "Closed when") | otherwise a wish-list |
| `UNTESTED-STALE` (new, 3.2) | the lend-lease case |
| `WIP-LIMIT` (non-parked subjects > 4) | replaces MULTI-ACTIVE |

Removed: LEDGER-*, PROBE-UNRUN, NEVER-SCORED, AWAITING-CAMPAIGN, DORMANT, FIX-*, STATUS-*,
TLM-ORPHAN, CRITERION-UNSCOREABLE, SUPERSEDED, ORPHAN-FIX, MULTI/NO-ACTIVE, and RETIRE-DUE
(it only applied to R-items, which are gone; F-items never retire). The self-test is adapted
accordingly.

### 3.4 Comments in code

Single rule: **one comment per protected behaviour, named by its subject, no history.**

```
# [na-corridor] level-0 segment outranks over-consolidation; assumes the cap is 4 (constant:wa_ai_pc.rail.cap)
```

- Forbidden: `# Fix NN`, "Fix 3 fixes Fix 2 which fixed Fix 1" chains, campaign measurements,
  reviewer exchanges, dates. Git carries the history.
- Effect/trigger header: ≤ 5 lines (what / scope / what it assumes / how to tell that fact is gone).
- Migration: `tools/archive/fix_tracking/collapse_fix_comments.py` (to write) — replaces `# Fix NN` with `# [slug]` via
  `FIX_HISTORY.md`, merges consecutive duplicates of the same slug, then **human re-read** of the
  15 most-cited numbers (Fix 47, 97, 90, 96, 88, 40, 49, 81, 62, 41, 51, 135, 129, 95, 87), where
  chains are likely. The other 120 numbers are handled mechanically.

### 3.5 AGENTS.md

- § "One subject at a time" → § "Subjects and sessions" (3.1).
- Principle 3 (impact analysis): unchanged in substance.
- Editing rule 7 (comments): replaced by 3.4, short form.
- Editing rule 16 (BOM): unchanged.
- Validation table: `WORK.md` row + "mandatory harness" row (3.2).

## 4. Phasing

| Phase | Content | Size |
| --- | --- | --- |
| A | `WORK.md` created from QUEUE + open R-items; reduced checker + self-test; AGENTS.md; frozen `FIX_HISTORY.md` | 1 session |
| B | System → harness table; `SHIPPED-UNTESTED` contract; missing harnesses listed (not written) | ½ session |
| C | Comment-collapse script, mechanical pass, human re-read of the 15 hot numbers | 1–2 sessions, per file, behaviour-neutral (diff = comments only) |

## 5. Owner decisions requested

1. Open-subject limit: 3, 4, or no limit?
2. Comments: replace `# Fix NN` with `# [slug]` everywhere (phase C), or only forbid new ones?
3. Open R-items (~70): fold into their subject (keeps the probe) or delete outright unless asked?

---

## 6. Decisions taken (2026-08-23)

| Question | Decision |
| --- | --- |
| Open-subject limit | **4** (non-`PARKED`) |
| Existing `# Fix NN` | **Collapse all of the existing ones** (phase C) |
| Open R-items | Table below, validated 2026-08-23 with the human verdicts |

Human verdicts 2026-08-23 on the 4 proposed OPEN subjects: `na-corridor` **tested and functional
→ CLOSED**; `med-axis-posture` **tested and functional → CLOSED**; `commonwealth-handoff` **in
progress → OPEN**; `lend-lease-relief` **validated, final audit owed → TESTED**. The `RETIRE-DUE`
rule is removed along with the R-items (F-items never retire): the final checker has 5 rules.

**Phase A applied 2026-08-23**: `WORK.md` created, `QUEUE.md` deleted, checklist reduced to F1–F9
+ registry + cosmetic anomalies (2685 → 298 lines), R-items frozen in
`documentation/archive/CHECKLIST_R_ARCHIVE.md`, `documentation/FIX_HISTORY.md` generated (121
numbers, 60 mapped), checker rewritten (5 rules + self-test), AGENTS.md and skills updated.
**Phase B applied 2026-08-23** (system → harness routing table in `wa-testing`).
Remaining: phase C (collapse of the 667 comments).

## 7. Folding the R-items (70 items MEASURED in `checklist.md`) into subjects

Suggestion legend:
- **CLOSE** — passed in a campaign, no regression signal: deleted, probe deleted. The safety net
  remains F1–F9. (The "streak up to N" model disappears: a criterion met once = closed; a
  regression reopens from the symptom.)
- **→ slug** — folded into the named subject; its probe becomes a line of the subject's
  *Verification* field.
- **PARK** — real symptom, no owner and no fix in flight: one `PARKED` row in `WORK.md` with the
  symptom and the closing criterion.
- **DROP** — deleted without replacement (duplicate, or no value).

### 7.1 The 4 proposed OPEN subjects

| Slug | Scope | Initial state | Folded R-items |
| --- | --- | --- | --- |
| `na-corridor` | North-African corridor logistics: rail, depots, ports, theatre air bases, sizing | `SHIPPED-UNTESTED` (Fix 120/130/135 in `bc90346af`) | R9, R13, R52, R60, R68, R69, R71, R77, R78, R81, R91, R96 |
| `med-axis-posture` | Axis Mediterranean posture: Afrika Korps, Tunis, Italian peninsula/Adriatic/southern France, Ethiopia, Med fleet, convoy interdiction | `SHIPPED-UNTESTED` (Fix 121–122, 131, 133, 136–137) | R17, R61, R63, R64, R74, R75, R76, R80, R82, R83, R92, R94, R97 |
| `commonwealth-handoff` | Commonwealth defensive missions, East Africa, Kuwait, El Alamein, Pacific garrison, dominion ship designs | `SHIPPED-UNTESTED` (Fix 123–129, 132, 134) | R70, R72, R73, R84–R86, R88–R90, R93, R95 |
| `lend-lease-relief` | Lend-lease surplus relief (Fix 92) + USA native offers; harness `WA_TEST_lend_lease_relief` exists | `SHIPPED-UNTESTED` (broken a week with no signal) | R7b, R57 |

### 7.2 Full table

| Item | Short title | MEASURED status | Suggestion | Reason |
| --- | --- | --- | --- | --- |
| R6 | Majors mechanize | FAILED, streak 0, fix 2026-08-17 | **PARK** `majors-mechanize` | real symptom, no fix since the failure |
| R7b | Lend-lease relief overland | PASSED 1/5, leg 3 unchecked | **→ lend-lease-relief** | |
| R8 | UK air hosting | FAILED 0/5 | **→ uk-air-basing** (PARK) | same subject as R54; no fix in flight |
| R9 | Supply-line corridors | FAILED 0/3 (2026-08-15) | **→ na-corridor** | subsumed by Fix 95/120 |
| R10 | USA army composition | PASSED 1/5 | **CLOSE** | |
| R13 | North Africa front moves | PASSED 1/5 | **→ na-corridor** | macro outcome of the corridor |
| R15 | Air forces deploy to theatres | FAILED 0/5 | **PARK** `air-deployment` | no fix since the failure |
| R17 | Italian campaign | FAILED 0/5 (2026-08-15) | **→ med-axis-posture** | subsumed by Fix 96/108–110 |
| R19 | Starved PC projects age out | PASSED 2/3 | **CLOSE** | |
| R24 | Overextension brake | FAILED 0/3 (2026-08-15) | **PARK** `overextension-brake` | no fix since |
| R28 | Trade-law ladder | DIAGNOSED, partial fix `32c03c550` untested (QUEUE 0e) | **PARK** `trade-law` as `SHIPPED-UNTESTED` | 5th subject: waits for a slot |
| R29 | Refinery activation | DIAGNOSED, NOT FIXED | **PARK** `refineries` | groups R55 |
| R31 | SOV multirole range | PASSED 1/3 | **CLOSE** | |
| R32 | ENG bomber aluminium | FAILED 0/3 | **PARK** `equipment-selection` | evaluator project SUSPENDED |
| R35 | Parallel tank branches | FAILED 0/3 | **PARK** `equipment-selection` | idem |
| R36 | Escorts to sea | FAILED 0/3 | **PARK** `convoys` | |
| R38 | Front execution reaches puppets | PASSED 2/5 | **CLOSE** | |
| R39 | AIFC schwerpunkt | PASSED 2/3 | **CLOSE** | |
| R40 | No dead-end research | PASSED 2/3 | **CLOSE** | |
| R41 | SOV subs leave coastal boat | FAILED 0/3 | **PARK** `equipment-selection` | |
| R42 | AIFC ally soil | PASSED 2/3 | **CLOSE** | |
| R43 | Carrier aircraft for decks | FAILED 0/5 | **PARK** `equipment-selection` | |
| R44 | Landing freeze own theatre | PASSED 3/5 | **CLOSE** | |
| R45 | Historical ship names | PASSED 2/3 | **CLOSE** | cosmetic |
| R47 | Capitulated country runs PC | FAILED 0/3 | **PARK** `pc-queue` | groups QUEUE 17 (FRA deadlock) |
| R49 | Refinery shared-slot queues | PASSED 1/3 | **CLOSE** | |
| R50 | Narvik holds | PASSED 1/3 | **CLOSE** | |
| R51 | Landing hysteresis | FAILED (outcome leg) 0/5 | **PARK** `landing-freeze` | mechanism OK, outcome not |
| R52 | Theatre air-base builder | FAILED 0/3 | **→ na-corridor** | subsumed by Fix 114 (R78) + QUEUE 0r |
| R53 | Construction bursts top-K | NOT CHECKED, probe calls a tool that does not exist (QUEUE 8) | **DROP** | unverifiable as written; reopen on symptom |
| R54 | UK air-basing throughput | FAILED 0/3 | **→ uk-air-basing** (PARK) | with R8 |
| R55 | Refineries own budget | FAILED 0/3 | **→ refineries** (PARK) | with R29 |
| R56 | Convoys built and shared | PASSED 1/3 | **CLOSE** | R79/R87 cover the follow-up |
| R57 | USA native lend-lease | FAILED 0/2 | **→ lend-lease-relief** | |
| R60 | NA corridor logistics | PASSED 2/3, war-side depot never fired | **→ na-corridor** | |
| R61 | Italian peninsula defended | PASSED 1/3 | **→ med-axis-posture** | |
| R63 | Italy wins Ethiopia | PASSED 1/3 | **→ med-axis-posture** | |
| R64 | Tunis bridge | PASSED 1/3 | **→ med-axis-posture** | with R94 |
| R65 | Coal coop prospecting | FAILED 0/3 | **PARK** `prospecting-coop` | with R66, QUEUE 0b |
| R66 | Positive balance coop | PASSED 1/3 | **→ prospecting-coop** (PARK) | |
| R68 | Corridor hop permission/payment | FAILED 0/3 | **→ na-corridor** | |
| R69 | Ally cannot pay | PASSED 1/3 | **→ na-corridor** | |
| R70 | Smaller Allies back major | FAILED 0/3 | **→ commonwealth-handoff** | |
| R71 | Corridor sized to war | PASSED 1/3 | **→ na-corridor** | |
| R72 | Commonwealth defensive missions | FAILED 0/3 | **→ commonwealth-handoff** | |
| R73 | SAF El-Alamein guard | NOT YET TESTED | **→ commonwealth-handoff** | |
| R74 | Liberated Ethiopia | NOT YET TESTED | **→ med-axis-posture** | |
| R75 | Adriatic shore / Otranto | NOT YET TESTED | **→ med-axis-posture** | |
| R76 | Southern-France reserve | NOT YET TESTED | **→ med-axis-posture** | |
| R77 | Invader's approach march | NOT YET TESTED | **→ na-corridor** | |
| R78 | Theatre air bases on edge | NOT YET TESTED | **→ na-corridor** | |
| R79 | Land coalition no convoy arsenal | NOT YET TESTED | **PARK** `convoys` | with R36, R87, QUEUE 15/20 |
| R80 | Afrika-Korps expedition | NOT YET TESTED | **→ med-axis-posture** | |
| R81 | Corridor connects first | NOT YET TESTED | **→ na-corridor** | |
| R82 | Afrika Korps halved | NOT YET TESTED | **→ med-axis-posture** | |
| R83 | Allies cut Med lifeline | NOT YET TESTED | **→ med-axis-posture** | |
| R84 | Pacific Commonwealth garrison | NOT YET TESTED | **→ commonwealth-handoff** | |
| R85 | East Africa = Indian army | NOT YET TESTED | **→ commonwealth-handoff** | |
| R86 | Kuwait guard needs threat | NOT YET TESTED | **→ commonwealth-handoff** | with R95 |
| R87 | Surplus dockyards → convoys | NOT YET TESTED | **PARK** `convoys` | |
| R88 | Allies man Italian frontiers | NOT YET TESTED | **→ commonwealth-handoff** | |
| R89 | Indian army at El Alamein | NOT YET TESTED | **→ commonwealth-handoff** | |
| R90 | Dominion ship design | NOT YET TESTED | **→ commonwealth-handoff** | with QUEUE 0l |
| R91 | Tobruk → 5078 inland | NOT YET TESTED | **→ na-corridor** | |
| R92 | German armour stays in Africa | NOT YET TESTED | **→ med-axis-posture** | |
| R93 | Allies stay in East Africa | NOT YET TESTED | **→ commonwealth-handoff** | |
| R94 | Italy mans Tunis (German ground) | NOT YET TESTED | **→ med-axis-posture** | |
| R95 | Kuwait guard sized | NOT YET TESTED | **→ commonwealth-handoff** | |
| R96 | Rail route sized to demand | NOT YET TESTED | **→ na-corridor** | |
| R97 | Mediterranean Fleet | NOT YET TESTED | **→ med-axis-posture** | with QUEUE 0t |

Tally: **14 CLOSE, 1 DROP, 38 folded into the 4 OPEN subjects, 17 folded into 11 PARKED
subjects** (`majors-mechanize`, `uk-air-basing`, `air-deployment`, `overextension-brake`,
`trade-law`, `refineries`, `equipment-selection`, `convoys`, `pc-queue`, `landing-freeze`,
`prospecting-coop`).

### 7.3 The 34 QUEUE rows (same treatment)

| Rows | Suggestion |
| --- | --- |
| 0q, 0r, 0m, 0i | **→ na-corridor** |
| 0t, 0h, 0f, 0g | **→ med-axis-posture** (0g: DROP if no measurement supports it) |
| 0l, 14 | **→ commonwealth-handoff** |
| 0e, 0a, 0d | **→ trade-law** (PARK, `SHIPPED-UNTESTED`) |
| 0b | **→ prospecting-coop** (PARK) |
| 0 (garrison echelon) | **→ med-axis-posture** verification; CLOSE if campaign `8c0fea4c` validates it |
| 15, 20 | **→ convoys** (PARK) |
| 17 | **→ pc-queue** (PARK) |
| 12 (320 countries without template) | **PARK** `templates-coverage` — MEASURED symptom, closed when a criterion is written |
| 9, 10 (F5 too slow / counting control) | 9: **→ F5** (already fundamental); 10: tooling → **DROP** from WORK.md, note in `wa-savegame-analysis` |
| 1, 2, 3 (front_control) | **PARK** `front-control` (one subject, three evidence lines) |
| 11 (put_unit_buffers docs) | **DROP**; doc correction done in passing by the subject that touches the file |
| 19 (resource need blind) | **PARK** `resource-needs` |
| 0j (8c0fea4c unscored) | **DROP** as a task: scoring happens per subject, on the 4 OPEN, at the next analysis session |
| 0s, 4, 5, 6, 7, 8, 21 | **DROP**: meta-work (tooling, checker, triage, harness) — admission rule §3.1; 21 is absorbed by the "one harness = one file" rule already in force |

Effect: 34 rows → **0 standalone rows**; everything is either in one of the 4 OPEN, in one of the
~14 PARKED, or deleted.

**Phase C applied 2026-08-23.** Mechanical pass (`tools/archive/fix_tracking/collapse_fix_comments.py` + `tools/archive/fix_tracking/fix_slug_map.json`, 117 numbers -> 20 slugs): 1121 comment lines rewritten across 117 files, zero code deviations by construction. The Fix 28 number collision (posture verdict vs railway overseas fallback) was split per file (`offensive-posture` / `railway-pathfinding`); 54/55 follow the posture family. Nine `log = "..."` strings carrying fix numbers were renamed by hand (plain slug text, no `[...]` - the engine parses bracketed tokens in log strings). Condensation wave (5 review agents, 11 hottest files): comment lines 19848 -> 18746 overall (-1102), ~120 history chains merged into single current-rule comments; per-file code-identity verified against HEAD. `common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_caps.txt` and `common/scripted_triggers/WA_AI_MILITARY_triggers.txt` carry unrelated in-flight code edits (new `unfit_army_stays_home` block) and were excluded from condensation. Zero `Fix NN` tokens remain under `common/` + `events/`.
