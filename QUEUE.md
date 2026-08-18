# Work queue

Exactly one **ACTIVE** subject at a time. Anything found on the way goes to **QUEUE**, never into
the subject in hand. That is the rule that stops a session fanning out into six directions.

Enforced by `python tools/check_worklist.py`.

- **ACTIVE** — exactly one entry. Opening a second means demoting the first to QUEUE with its state.
- **QUEUE** — three columns are mandatory: the subject, why it matters, and **what would close it**.
  A row with no closing criterion is a wish, not a task.
- **DONE** — the last ten, then pruned. `git log` is the archive.

---

## ACTIVE

- *(none - the last subject closed. Promote one QUEUE row before starting work.)*

---

## QUEUE

| # | Subject | Why it matters | Closed when |
| --- | --- | --- | --- |
| 1 | `front_control`: the engine already has `priority` | `WA_AI_MILITARY_SYSTEM.md` defers a whole scripted mutual-exclusion subsystem to Phase 5, for a problem `priority = 0 # higher prio strats will override lower` already solves. 57 blocks write `priority` today. | Phase 5 is cancelled or justified by a measurement, and `SYSTEM.md` cites the engine section |
| 2 | The other 6 contradictions from the type audit | `.claude/skills/wa-engine-reference/references/type-audit-2026-08-18.md`. Beliefs reverse-engineered against a stale 2023 copy of the engine doc. | Every row of its summary table is corrected, or marked "checked, the doc is wrong" |
| 3 | 3 types documented as live that do not exist | `force_ratio`, `infantry`, `naval_invasion_support_priority` appear in no engine edition. `infantry`'s "34 instances" are `divisions_in_state` trigger hits. | `TYPES_REFERENCE.md` no longer lists them as types |
| 4 | `common/ai_faction_theaters`: live and unowned | Not replaced by the mod, so vanilla's 22 KB file runs in every campaign. No WA document mentions it. It decides how the engine groups a faction into theatres. | We know what it does in our campaigns, and have decided to replace it or leave it |
| 5 | Telemetry debt | `WA_TLM_r74_*` and `WA_TLM_r97_ea_*` still write for retired items. Cheaper than assumed: `WA_TLM_TELEMETRY_SYSTEM.md` §3.7 says removing a metric does **not** bump the version. | `check_worklist.py` reports no TLM-ORPHAN |
| 6 | Remaining invalid probes in the checklist | 8 defects found 2026-08-17; the tooling now covers 7, but nothing validates a probe **at creation**. | An item cannot be added without a non-empty probe output pasted into its text |
| 7 | Unmeasurable pass criteria | R62 leg 4 reads "≤ the previous campaign's reading" with that number written nowhere → unscoreable forever, in both directions. | Every pass criterion contains a number |
| 8 | Structured checklist + semi-automatic scoring | 52 items in prose today; scoring a campaign is redone by hand every time. A structured header would unlock `savegame.py score`. | Decision made: migrate, or accept the prose |
| 9 | Fix numbering and commit discipline | Fixes 102/103/105 renumbered; one commit rebased off the branch with its content absorbed by an unrelated one. `git blame` lies. | One number = one registry row, checked by a checker |
| 10 | 18 stale engine docs | Handled by a background task started 2026-08-18. | `check_engine_docs.py` at 0 WARN and its diff report read |
| 11 | `has_deployed_air_force_size` thresholds are labelled wings, the engine counts aircraft | `common/scripted_triggers/WA_AI_MILITARY_triggers.txt:1975` calls the Reich bombing-ladder thresholds (299/450/700/900) "deployed strategic_bomber **wings**"; install `documentation/triggers_documentation.md` section `has_deployed_air_force_size` says "amount of aircrafts". The values were calibrated on campaign 973154a7 so behaviour is right - the word is wrong, and it is the same wings/planes confusion that left two `*_MIN_EXCORT_WINGS` defines dead for years. | The comment says aircraft, and every other WA comment on that trigger family is checked for the same word |

---

## DONE

| Date | Subject | Trace |
| --- | --- | --- |
| 2026-08-18 | 19 dead `05_defines.lua` writes: 17 deleted, 2 renamed to their live engine key with a new value, 1 given its missing `NDefines.NAir.` prefix. Logistics doc was wrong by 15x on `SUPPLY_FROM_DAMAGED_INFRA` | `common/defines/05_defines.lua`, `documentation/WA_AI_LOGISTICS_MODEL.md`, `documentation/WA_AI_MILITARY_SYSTEM.md`, `tools/constants_registry.json`, `lessons-log.md` |
| 2026-08-18 | `naval_dominance` out of scale: the 8 blocks at 1000 were a self-labelled probe (`289f1318f`) whose question R36 already answered - retired; region 356 moved to the Faction south corridor at 70 with its avoid pair | `WA_AI_NAVAL_COUNTRY_ENG.txt`, `WA_AI_NAVAL_FACTION_ALLIES.txt` |
| 2026-08-18 | Work queue + checklist decay checker (one ACTIVE, orphan fixes, stale statuses, dormancy) | `QUEUE.md`, `tools/check_worklist.py` |
| 2026-08-18 | Diagnosis protocol — six boxes; a missing script line makes the report `INCOMPLETE DIAGNOSIS` | `.claude/skills/wa-diagnosis/` |
| 2026-08-18 | Engine doc `ai_strategy` refreshed 2023-07 → 2024-11 (+291 lines), 20 citations moved to section names, drift checker | `tools/check_engine_docs.py` |
| 2026-08-18 | Engine reference: game install + Expert AI + wiki, with the "read before you assert" rule | `.claude/skills/wa-engine-reference/` |
| 2026-08-18 | `savegame.py`: 7 tooling defects that made wrong readings silent | `savegame.py`, `plans.py`, `airload.py`, `regions.py` |
| 2026-08-18 | Communication rule: answer first, MEASURED / DERIVED / ASSUMED labels | `AGENTS.md` § Talking to the user |
