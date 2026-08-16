---
name: wa-campaign-checklist
description: The living verification checklist that every analysed World Ablaze test campaign must be scored against — the WW2 historical arc, balance outcomes, in-flight bug-fix verifications, and AI behaviour probes, each with a PASSED/FAILED status and a retirement rule. Use this IN TANDEM with wa-savegame-analysis whenever a test campaign (cloud observer run or local control run) is being analysed: run the listed probes, mark each item PASSED or FAILED with the campaign's game_unique_id, and update references/checklist.md in the same session. Also use it when a fix commit ships — every fix gets a verification probe added here — and when deciding whether a verified fix can be retired from the list. Analysing a campaign without scoring this checklist wastes the run; the checklist is the institutional memory of what each campaign was supposed to prove.
---

# WA campaign checklist

`references/checklist.md` is the living data file: every item an analysis agent must check when a test campaign is analysed. This SKILL.md is the protocol for running it, scoring it, growing it, and shrinking it.

The point of the mechanism: test campaigns are expensive (multi-hour cloud runs), so each one must be squeezed for every verification it can support, and the results must accumulate across campaigns instead of living in one session's summary. The checklist is that accumulator.

## When to run

Score the checklist **every time a campaign is analysed** with `wa-savegame-analysis` — full audits and narrow bug-hunts alike. On a narrow bug-hunt you still score every item the saves you already opened can answer cheaply; mark the rest `NOT CHECKED` for that campaign rather than guessing.

## How to run the checks

1. **Follow `wa-savegame-analysis` discipline.** All probes go through its `savegame.py` script, run inside subagents so bulky output never enters the main context. Batch probes per country/save so one extraction subagent answers several checklist items in one pass.
2. **Quote the `Probe:` line verbatim into the subagent prompt. Do not paraphrase it.** Copy the whole line, including the caveats and the scoping clauses, and let the subagent read them; add your own context around it, never in place of it. Every qualifier in a `Probe:` line was put there by a scoring session that got burned without it, and the cost of dropping one is silent: the subagent returns a well-formed, confidently-wrong number and nothing in the output says a constraint went missing. **The cautionary case:** R10's probe says to count `division={` **inside `units`**. A paraphrased prompt dropped that scoping, the agent counted the whole country block, and the resulting 8–10% inflation contaminated **F8, R5 and R10** in one campaign scoring before the correction was found. Paraphrasing a probe is how a probe silently changes meaning.
3. **Verify the build first.** Cloud saves carry no reliable local-log evidence (see memory `test-campaigns-cloud-machine`): confirm which commits the campaign actually ran via behavioural fingerprints in the saves (`*_dbg_*` variables, structures only the new code produces) plus git ancestry. An item whose fix commit is **not** in the campaign's build stays `NOT YET TESTED` — a FAILED mark against a build that predates the fix is noise.
4. **Check the DLC bitmask before scoring DLC-gated items.** The save header (~line 20) has `dlcs=`; the cloud test box reports `dlcs=30` (missing La Résistance and Arms Against Tyranny among others), the local full install `dlcs=191999`. Items tagged `DLC-gated` in the checklist (Spain/SCW, espionage, MIOs, international market) are **only scoreable on full-DLC campaigns** — on a cloud run mark them `N/A (DLC)`, which neither advances nor resets their streak.

## How to mark results

Each item carries a status block. After analysing a campaign, in the **same session**:

- Append a history line: `YYYY-MM-DD · <game_unique_id> · PASSED|FAILED|N/A (DLC)|NOT CHECKED — one-line evidence`. Always cite the evidence (the value observed, the date something fired), not just the verdict.
- Update the **Streak** counter: PASSED increments it, FAILED resets it to 0, `N/A (DLC)` and `NOT CHECKED` leave it untouched.
- A pass with a caveat (in tolerance but at the edge, or passing for a known-wrong reason) is a PASSED with the caveat in the evidence — but if the caveat means the mechanism under test didn't actually run, it's `NOT CHECKED`, not PASSED.
- Update the `As of` line at the top of `references/checklist.md`.

If a FAILED reveals a *new* defect (not the one the item tracks), that's a finding for the session summary and possibly a new checklist item — don't overload an existing item's meaning.

## FUNDAMENTAL vs RETIREABLE

- **FUNDAMENTAL** items define what a healthy campaign looks like (the WW2 arc, no-pathology invariants, the game boots). They are **never removed**, keep accumulating history forever, and their streak is informational only.
- **RETIREABLE** items verify a specific shipped fix. Each carries a retirement threshold chosen when the item is created: **3 consecutive PASSED** for narrow probes (a variable exists, a factory count clears a floor), **5 consecutive PASSED** for behavioural outcomes (a front moves, an army composition stays sane). When the streak reaches the threshold, **delete the item** from the checklist in the same session, noting the retirement in the commit message, and add one row to the `## Retired and merged items — ledger` at the end of `references/checklist.md` (item, disposition, date · campaign · streak, where the mechanism lives now). If the fix was subtle enough to deserve a permanent record, its durable rule belongs in `wa-lessons-learned` — the checklist is a working queue, not an archive; do **not** leave retirement essays inline in the preamble or inside another item's history. An item whose mechanism has been taken over by a later fix (its own text says "superseded by Fix NN — the question moves to R<MM>") is **merged**: fold its live leg and its last evidence into the owning item as an "Absorbed from R<NN>" bullet, delete it, and add a MERGED ledger row.
- **Retiring an item also retires its instrumentation, in the same session.** Delete the item's probe write sites, init lines, and registry row (`WA_TLM_r<NN>_*` per `documentation/WA_TLM_TELEMETRY_SYSTEM.md` §3.7; legacy `*_dbg_*` families likewise — several items carry an explicit "retire the instrumentation with this item" note). Orphaned telemetry that keeps writing after its consumer is gone is the failure mode the WA_TLM registry exists to prevent. **Exception — promotion:** before deleting, apply the standing-vs-probe test (doc §3.8). If analysis sessions used the metric beyond the item's own pass/fail (it fed a FUNDAMENTAL item, it replaced a multi-save parse), promote it to a standing `WA_TLM_<system>_*` name with a registry row instead of deleting it, and say so in the retirement commit.

## Adding items — every fix ships with a probe

When a fix commit lands on the AI/balance stack, add a RETIREABLE item **in the same session as the fix**, before the next campaign runs:

- State the pass criterion concretely (thresholds, dates, tags/archetypes) and the exact probe (`savegame.py` command or section+pattern) an extraction subagent can run without further context.
- Cite the fix commit hash, choose 3 or 5 for the threshold and say which and why.
- If the fix has no natural save-visible fingerprint, add instrumentation to the fix itself so the probe exists (see memory `test-campaigns-cloud-machine`). New instrumentation follows the WA_TLM standard (`documentation/WA_TLM_TELEMETRY_SYSTEM.md`): a `WA_TLM_r<NN>_*` metric registered there, zero-initialised, counters incremented only on *verified* effect (never on code-path entry), stamps as `_first_t`/`_last_t` pairs (a lone `fire_only_once` stamp over-affirms). Probe with `savegame.py tlm TAG <saves>`. Existing `*_dbg_*` families stay as they are and retire with their items.
- Initial status is `NOT YET TESTED`, streak 0.

New FUNDAMENTAL items are rare and are a design statement — add one only when the definition of a healthy campaign genuinely grows (e.g. a Pacific-termination chain finally exists and must keep working).

## Reading the checklist honestly

- Known gaps are listed as FAILED-by-design with a `KNOWN GAP` note; they stay visible so no analysis "rediscovers" them, but they don't trigger re-diagnosis unless the gap's scope changes.
- The `Recurring cosmetic anomalies` section lists save artefacts that look alarming and are not — check it before reporting an anomaly as a finding.
- Tolerances in brackets (dates ± months) are part of the pass criterion; a result outside tolerance is FAILED even when the mechanism "worked eventually".
