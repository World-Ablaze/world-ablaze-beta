---
name: wa-campaign-checklist
description: Scoring an analysed World Ablaze test campaign — the FUNDAMENTAL items (F2, F5, F6, F8, F9 — WW2 arc, no-pathology invariants, boot) in references/checklist.md, plus the Verification lines of every non-PARKED subject in WORK.md. Use this IN TANDEM with wa-savegame-analysis whenever a test campaign (cloud observer run or local control run) is being analysed: verify the build, run the probes verbatim, record the verdicts with evidence in the same session. Also use it when a subject ships code — every subject carries its own verification (console harness and/or campaign probe) before it can close. Analysing a campaign without scoring wastes the run; the checklist and WORK.md are the institutional memory of what each campaign was supposed to prove.
---

# WA campaign checklist

Two things get scored when a campaign is analysed (protocol changed 2026-08-23,
`documentation/PROCESS_REDESIGN_PROPOSAL.md`):

1. **`references/checklist.md`** — the FUNDAMENTAL items **F2, F5, F6, F8, F9** (what a healthy
   campaign looks like; F1/F3/F4/F7 retired 2026-08-27 on owner order — always-passing, git holds
   them), the campaign registry, and the cosmetic-anomaly list.
2. **`WORK.md`** — the *Verification* lines of every subject in OPEN. A subject whose
   criterion is met records the evidence and moves toward `CAMPAIGN-OK`/`CLOSED`; a
   regression on a CLOSED subject reopens it from the symptom.

The retired per-fix R-items are frozen in `documentation/archive/CHECKLIST_R_ARCHIVE.md` —
recover a probe from there when reopening a subject; never score the archive.

Test campaigns are expensive (multi-hour cloud runs): squeeze each one for every
verification it can support, and record results in the files, not only in the session
summary.

## When to run

Score **every time a campaign is analysed** with `wa-savegame-analysis` — full audits and
narrow bug-hunts alike. On a narrow bug-hunt, still score the FUNDAMENTAL items and any OPEN subject the
saves you already opened can answer cheaply; mark the rest `NOT CHECKED` rather than
guessing. Run `python tools/check_worklist.py` first (BOM, harness contract, WIP, stale
untested subjects).

## How to run the checks

1. **Follow `wa-savegame-analysis` discipline.** All probes go through its `savegame.py`
   script, run inside subagents so bulky output never enters the main context. Batch probes
   per country/save so one extraction subagent answers several items in one pass.
2. **Quote the probe line verbatim into the subagent prompt. Do not paraphrase it.** Every
   qualifier in a probe line was put there by a scoring session that got burned without it;
   the cost of dropping one is a well-formed, confidently-wrong number. The cautionary
   case: R10's probe said to count `division={` **inside `units`**; a paraphrase dropped
   the scoping and the 8–10% inflation contaminated three items in one scoring.
3. **Verify the build first.** Cloud saves carry no reliable local-log evidence (memory
   `test-campaigns-cloud-machine`): confirm which commits the campaign actually ran via
   behavioural fingerprints in the saves plus git ancestry. A subject whose commits are
   **not** in the campaign's build is not scoreable — a FAILED against a build that
   predates the code is noise.
4. **Check the DLC bitmask before scoring DLC-gated items.** Save header (~line 20) has
   `dlcs=`; cloud test box `dlcs=30`, local full install `dlcs=191999`. DLC-gated items
   (F7 Spain/SCW among them) are only scoreable on full-DLC campaigns — otherwise mark
   `N/A (DLC)`.

## How to mark results

In the **same session** as the analysis:

- F items: append a history line `YYYY-MM-DD · <game_unique_id> · PASSED|FAILED|N/A (DLC)|NOT CHECKED — one-line evidence`.
  Always cite the evidence (the value observed, the date something fired), never just the
  verdict. Tolerances in brackets are part of the criterion: outside tolerance is FAILED
  even when the mechanism "worked eventually".
- Subjects: write the verdict and evidence into the subject's body in `WORK.md`, and move
  the state (`TESTED` → `CAMPAIGN-OK`, or reopen). A pass whose caveat means the mechanism
  under test didn't actually run is `NOT CHECKED`, not a pass.
- A FAILED that reveals a *new* defect is a finding for the session summary — and a
  *candidate* subject, admitted only per the WORK.md admission rule (owner request, or
  MEASURED symptom about mod behaviour).

## Writing a subject's verification

When a subject ships code, its *Verification* lines are written in the same session:

- Console harness first (`WA_TEST_*`, wa-testing contract v1) — this is what moves
  `SHIPPED-UNTESTED` → `TESTED`, and the checker errors on a subject stuck untested.
- Campaign probe: state the pass criterion concretely (thresholds, dates, archetypes) and
  the exact `savegame.py` command an extraction subagent can run without further context.
  **A criterion may only compare against a number written inside the subject** — "stays in
  the envelope of the previous campaign" is unscoreable forever.
- **Run the probe against a pre-fix baseline save before writing it down, and paste what
  came back** (three lines is enough; zeros are a fine answer). `pc <TAG> --match corridor`
  sat unrun for months and returns "(no projects matched)" for every input — a session
  scoring off it would have recorded a false FAIL.
- If the fix has no save-visible fingerprint, add WA_TLM instrumentation with the fix
  (`documentation/WA_TLM_TELEMETRY_SYSTEM.md`): registered, zero-initialised, incremented
  only on *verified* effect, probed with `savegame.py tlm`. When the subject closes, its
  instrumentation is deleted in the same session unless promoted to a standing metric
  (doc §3.8) — orphaned telemetry is the failure the registry exists to prevent.

New FUNDAMENTAL items are rare and are a design statement — add one only when the
definition of a healthy campaign genuinely grows.

## Reading honestly

- Known gaps are FAILED-by-design with a `KNOWN GAP` note; they stay visible so no
  analysis "rediscovers" them.
- The `Recurring cosmetic anomalies` section of `references/checklist.md` lists save
  artefacts that look alarming and are not — check it before reporting a "finding".
