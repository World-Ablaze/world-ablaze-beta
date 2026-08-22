---
name: wa-diagnosis
description: The protocol for going from an observed symptom to the script line that causes it, when something in World Ablaze misbehaved - the AI did not build, did not attack, did not defend, built the wrong thing, or a campaign reading looks wrong. Defines the six-box output contract every diagnosis is delivered in (symptom, measurement, mod state, mod decision, script line, engine boundary), the ladder to work down without skipping a rung, and the four techniques that have each already caught a wrong conclusion in this repo - competing hypotheses with one killing measurement each, the positive control, the closure test, and naming the rival explanation. Use it whenever a task asks WHY something happened rather than WHAT happened, including every campaign-analysis finding and every bug report from a playthrough. An analysis that names the symptom and stops is the failure this skill exists to prevent.
---

# Diagnosis - from symptom to script line

"The Allies did not build enough railways in North Africa" is not a finding. It restates what was
already visible and says nothing anyone can act on. A diagnosis ends at a line someone can edit, or
at a documented boundary of the engine — nowhere in between.

## The output contract - six boxes

Every diagnosis is delivered as these six, in this order. A box you cannot fill is written
`— unknown` with one line saying what would fill it. It is never dropped silently.

| # | Box | Answers | Rule |
| --- | --- | --- | --- |
| 1 | **Symptom** | what looked wrong | one sentence, containing no cause |
| 2 | **Measurement** | the number, in which save, at which date | **MEASURED**, with the exact command |
| 3 | **Mod state** | which WA variable / flag / array held what value | the state the code actually reads |
| 4 | **Mod decision** | which trigger armed, which did not, and on which term it failed | name the trigger, not the system |
| 5 | **Script line** | `file:line` | the thing a person would edit |
| 6 | **Engine boundary** | what the engine decided that no save shows | **ASSUMED**, explicitly |

**Box 5 empty ⇒ the report's first line is `INCOMPLETE DIAGNOSIS`.** Not "largely done", not a
caveat in the last paragraph. The reader must see the gap before reading anything else — an
incomplete diagnosis presented as a complete one is how a guess becomes an established fact.

Box 6 empty is fine and common. Box 6 filled while box 4 is empty is not a diagnosis; it is
speculation with a measurement attached.

## The ladder - work down, never skip a rung

    symptom -> measurement -> mod state -> mod decision -> script line -> engine boundary

Each rung answers *why* for the rung above it. The characteristic failures are all skips:

| Skip | What you actually produced |
| --- | --- |
| symptom → script line | a guess dressed as a finding |
| measurement, then stop | you know it did not happen, not why |
| mod state, then stop | you know the code saw a value, not what it did with it |
| decision, then stop | a suspect, not a fix |
| straight to "the engine decided" | an unfalsifiable claim |

Rung 3 vs rung 4 is the one people collapse. "The variable was 0" (state) and "the trigger's third
term was false" (decision) are different facts, and only the second points at a line.

## Four techniques, each of which already caught a wrong conclusion here

Not general advice. Each of these turned a published claim in this repo out to be wrong.

### Competing hypotheses, one killing measurement each

Write 3–5 candidate causes **before** measuring. For each, name the single measurement that kills
*that one alone*. Then measure once.

A hypothesis with no killing measurement is not a hypothesis, it is a preference — and a
measurement that would be consistent with three of your five candidates has not narrowed anything.
(2026-08-17: the convoy hypothesis was refuted cleanly in one pass this way, against four rivals.)

### The positive control

Before reading a zero as "the mechanism is broken", prove the mechanism can produce a non-zero
*somewhere* in the same campaign.

(2026-08-17, expeditionary forces: checking that the engine **does** lend divisions elsewhere —
SIK→SOV, ITL→ITA — turned an ambiguous zero into a solid negative.) A zero with no positive
control cannot distinguish "broken" from "never asked", and those need opposite fixes.

### The closure test

Whenever you split a whole into buckets, find the identity that must hold and check it.

`plans.py --where` totalled per state must equal `army`'s deployed count. If it does not, the
attribution is wrong whatever the rows say — two independent agents published a wrong division
attribution before this test caught it. Find the identity **before** you trust the split.

### Naming the rival

For any reading that supports a conclusion, ask: *what else would produce exactly this reading?*

The recurring rivals in this repo: a second code path doing the same work (a building that also
reaches the queue through priority construction), a **frozen gauge** (a WA_TLM value stops updating
when its condition closes and keeps its last number forever — `savegame.py tlm` now prints
`FROZEN Nmo`), a counter that counts something other than what its name suggests (`random_item`
counts per *target*, not per decision, and is not a firing count at all).

A conclusion with no named rival is a conclusion that was never tested.

## The engine boundary - where diagnosis legitimately stops

HOI4's internal AI weighting, its front assignment and its unit-request arbitration are not
observable from a savegame. When the ladder reaches them:

1. **Check `wa-engine-reference` first.** The engine documents far more than this repo assumed —
   `common/ai_strategy/documentation.info` alone carries 103 type tokens with parameters and
   semantics. A boundary that turns out to be documented is not a boundary, it is unread code.
2. If it is genuinely unobservable, say so in box 6, labelled **ASSUMED**.
3. **Do not invent a mechanism to fill the gap.** "The engine probably ranks X above Y" with no
   file behind it is exactly what this box exists to stop.

A diagnosis that ends at a real engine boundary with boxes 1–5 filled is **COMPLETE**. The boundary
is a result, not a failure — but it must be named, so the next session does not re-derive it.

## Where the work goes

The six boxes are short by construction: one to three lines each. They go in chat.

The evidence behind them — extraction tables, save-by-save series, the hypothesis grid — goes to a
file or the scratchpad, with the link in chat (`AGENTS.md`, section "Talking to the user"). If the
diagnosis produced a durable rule, it goes to `wa-lessons-learned`; if it produced a fix, the fix
ships with a probe in `wa-campaign-checklist`.

## Subagents

An extraction subagent asked *why* rather than *what* returns the six boxes too, with its own
MEASURED / DERIVED / ASSUMED labels. The main agent relays them without upgrading a label — a
subagent's DERIVED stays DERIVED. Reassembling six labelled boxes is also the cheapest way to notice
that two subagents disagreed about rung 3.

## Routing

| You need | Go to |
| --- | --- |
| To measure rungs 2–3 out of a savegame | skill `wa-savegame-analysis` |
| To know which WA system owns rung 4–5 | skill `wa-ai-systems`, then `AGENTS.md` |
| To settle rung 6 against the engine | skill `wa-engine-reference` |
| To check the cause is not one already known | subagent `wa-lessons-reviewer` |
| To record the result | skill `wa-campaign-checklist` (probe) or `wa-lessons-learned` (rule) |
