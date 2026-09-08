# WA research rush — bonus-gated ahead-of-time research for the AI

Subject `research-rush` (WORK.md). Owner intent, 2026-09-08: the AI may start a technology
**one year** before its `start_year` while a research bonus (`add_tech_bonus`) is available for
it, and **two years** before when that bonus carries `ahead_reduction >= 2`. Without a bonus the
generated date gate stays as it was (start_year, or start_year − 1 with the
`WA_AI_unused_research_slots` flag).

## Why a script-side ledger

`has_tech_bonus` cannot answer "is a bonus available for this tech". Measured in console
(harness `WA_TEST_research_bonus`, `events/wa_test_research_bonus.txt`, six owner runs on
1.19.2, 2026-09-08):

| Form | Reads |
| --- | --- |
| `has_tech_bonus = { technology = X }` | true almost always, including with no bonus at all (LUX); never true *because* a bonus covers X |
| `has_tech_bonus = { category = C }` | true while a limited-bonus record of category C exists — spent or not; the engine never deletes a record (20-save trace) |

So WA keeps its own counters on the country. Bug report for Paradox:
scratchpad `has_tech_bonus_bug_report.md` (owner's copy).

## The three pieces

| Piece | Where | Owner tool |
| --- | --- | --- |
| **Grant** — after every `add_tech_bonus = { … }` under `common/` and `events/` (1 610 blocks, 83 files): `add_to_variable = { WA_rb_uses_<key> = <uses> }`, plus `WA_rb_ahead2_<key>` when `ahead_reduction >= 2`. Key = each `category =` of the block, or `t_<tech>` for each `technology =` | managed `# WA_RB_GRANT begin/end` region, same scope as the grant | `tools/gen/gen_research_bonus_tracking.py` |
| **Consume** — every technology (4 357) carries in its `on_research_complete` an `if / else_if` chain: the tech's own `t_` key first, then its categories in file order; the first key with uses left is decremented (and its `ahead2` twin), a key reaching 0 is cleared | managed `# WA_RB_CONSUME begin/end` region inside the (created or existing) `on_research_complete = { }` | same tool |
| **Gate** — the generated `ai_will_do` date modifier gets two blocks before the normal date gate: `OR = { NOT = { OR = { check_variable = { WA_rb_uses_<key> > 0 } … } } date < start_year−1 }` and the same on `WA_rb_ahead2_*` with `start_year−2` | 4 203 gates in `common/technologies/*.txt` | `tools/migrations/ai_will_do/ai_replacer_base/generator.py` (+ air / naval / legacy replacers) for regeneration; `tools/migrations/ai_will_do/add_research_bonus_exemption.py` migrated the on-disk blocks |

Veto logic of the gate: `factor = 0` iff (no 1-year rush available OR date < Y−1) AND (no 2-year
rush OR date < Y−2) AND (normal date gate). With a plain bonus in 1937 for a 1938 tech: rush
available, date ≥ 1937 → no veto. With an `ahead_reduction = 2` bonus in 1936: no veto. Without
any bonus: today's behaviour.

## Approximations, stated

| Case | Behaviour | Why accepted |
| --- | --- | --- |
| A tech of the category already RUNNING when the bonus is granted completes first | the chain decrements in the bonus's place; the gate closes one research early, never late | there is no engine hook at research START (`on_research_complete` is per-tech only; no global on_action — install `common/on_actions/*`, 0 occurrence) |
| One block lists several technologies with `uses = N` | each tech key gets `max(1, N // count)`; siblings may stay open after one of them consumed the record | 154 such blocks; the alternative needs a shared key the gate generator cannot derive per tech |
| Both a plain and an `ahead2` bonus cover the key | `ahead2` decremented together with `uses` on the first completion | conservative: the 2-year window closes first |
| Speed-only bonuses (`bonus =` without `ahead_reduction`, 1 270 blocks) | open the 1-year rush like any other | owner ruling 2026-09-08 ("tous les bonus") |
| `add_tech_bonus` with neither category nor technology (`events/AAT_Norway.txt:2587`, vanilla-inherited) | skipped with a warning | it grants nothing in-engine either |
| A human player | counters are written and consumed but only `ai_will_do` reads them | no gameplay effect |

## Regeneration and checks

```
python tools/gen/gen_research_bonus_tracking.py --dry-run     # grants + consume blocks
python tools/gen/gen_research_bonus_tracking.py               # write
python tools/gen/gen_research_bonus_tracking.py --check       # exit 1 if out of date
python tools/migrations/ai_will_do/add_research_bonus_exemption.py --check   # every gate in counter form
python tools/migrations/ai_will_do/ai_will_do_replacer_all.py                # dry-run: 0 blocks to regenerate (support: 3, pre-existing drift)
```

Adding a focus / decision / event with `add_tech_bonus`: run the tracking generator (it inserts
the grant lines). Adding a technology: run the ai_will_do replacer for its file and the tracking
generator (consume block). Both are idempotent and byte-preserving outside their markers.

## Verification

- Console harness: `tag ENG`, `event wa_rb.1` prints the counters and the replicated gate; `event
  wa_rb.2` grants a 1-use `cat_transport` bonus and its counter, so the gate on the Bristol Bombay
  flips from veto to open on the same tick; a normal completion of a `cat_transport` tech must
  bring `WA_rb_uses_cat_transport` back to 0.
- Save probe: `savegame.py var <TAG> "^wa_rb_" <save>` — counters at 0 are cleared, so a country
  with no bonus in flight has none; a counter that only grows across saves means the consume
  chain never fires (check `on_research_complete` of the techs of that category).
- Campaign probe (WORK.md `research-rush`): in the first year after a major completes a focus
  with `ahead_reduction = 2` on category C, a C tech with `start_year = year + 2` is in progress or
  done; and no tech is ever in progress more than 2 years before `start_year` with every
  `wa_rb_*` counter absent on that country.
