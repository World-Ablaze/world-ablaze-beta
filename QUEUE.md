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

- *(none - telemetry debt closed 2026-08-18. Promote one QUEUE row before starting work.)*

---

## QUEUE

| # | Subject | Why it matters | Closed when |
| --- | --- | --- | --- |
| 1 | Remaining invalid probes in the checklist | 8 defects found 2026-08-17; the tooling now covers 7, but nothing validates a probe **at creation**. | An item cannot be added without a non-empty probe output pasted into its text |
| 2 | Unmeasurable pass criteria | R62 leg 4 reads "≤ the previous campaign's reading" with that number written nowhere → unscoreable forever, in both directions. | Every pass criterion contains a number |
| 3 | Structured checklist + semi-automatic scoring | 52 items in prose today; scoring a campaign is redone by hand every time. A structured header would unlock `savegame.py score`. | Decision made: migrate, or accept the prose |
| 4 | Fix numbering and commit discipline | Fixes 102/103/105 renumbered; one commit rebased off the branch with its content absorbed by an unrelated one. `git blame` lies. | One number = one registry row, checked by a checker |
| 5 | 18 stale engine docs | Handled by a background task started 2026-08-18. | `check_engine_docs.py` at 0 WARN and its diff report read |
| 6 | `has_deployed_air_force_size` thresholds are labelled wings, the engine counts aircraft | `common/scripted_triggers/WA_AI_MILITARY_triggers.txt:1975` calls the Reich bombing-ladder thresholds (299/450/700/900) "deployed strategic_bomber **wings**"; install `documentation/triggers_documentation.md` section `has_deployed_air_force_size` says "amount of aircrafts". The values were calibrated on campaign 973154a7 so behaviour is right - the word is wrong, and it is the same wings/planes confusion that left two `*_MIN_EXCORT_WINGS` defines dead for years. | The comment says aircraft, and every other WA comment on that trigger family is checked for the same word |
| 7 | `front_control`: the priority ladder and the ownership gates disagree | §6.1 measures a **semantic** ladder (brake 10000/500 > Faction posture 300-340 > routine 100 > 0) while §6.2 states Country > Faction. Wherever no `fc_*` slug gates the pair, the Faction posture block wins - e.g. `USA_operation_torch_landing_FRONT` (100) under `ALLIES_exec_vs_germany` (300). Nothing says that outcome was chosen. | Every Country-layer `front_control` block that can co-apply with a 300+ posture block is confirmed subordinate on purpose, or re-tiered / given a slug |
| 8 | WA pulls no `naval_invasion_support_priority` at all | The type is real (present in `hoi4.exe`, 7 entries in vanilla `ENG.txt`) and ranks sea regions for invasion support. `common/ai_strategy` is a `replace_path` folder, so vanilla's Mediterranean-first sequencing for ENG does not run and WA replaced it with nothing. | A decision is recorded: WA adopts the type with a measured value, or states why theatre sequencing is handled elsewhere |
| 9 | The faction-theatre remap is DERIVED, never observed | §15's before/after table assumes the engine resolves a `theatre_distribution_demand_increase` state through the live region map to a theatre. That chain is the only one the engine documents, but nobody has watched it happen, and 4 of 6 writers changed target. | A campaign save shows the six theatres exist and carry the extra demand, or shows they do not |
| 10 | `toolpack` scripted GUI floods error.log while it is enabled | 3,531 `root: Invalid Scope` at `common/scripted_guis/toolpack.txt:10` plus 3,627 paired `could not find this character in country SWE`, in ~2 minutes of a paused 1936.1.1 game - the `visible` block re-evaluates every tick. Absent from all 45 archived crash logs, but the GUI only runs behind `has_global_flag = toolpack_enabled`, so that proves nothing about age. | The two signatures are gone from a boot with the toolpack enabled, or the GUI is gated so it cannot evaluate in a character scope |
| 11 | error.log is unusable without triage | One boot writes ~4,200 load-time lines, almost all the known `Invalid scope type for <trigger/effect> in <scripted effect>` false-positive family the engine emits when it validates a scripted effect without knowing its runtime scope. A real error hides in that. Historical logs run to 3 MB on unrelated runaway spam (missing texticons, SOV character flags). | A triage tool classifies a log into known-benign and actionable, and the actionable list for a clean boot is written down |

---

## DONE

| Date | Subject | Trace |
| --- | --- | --- |
| 2026-08-18 | Telemetry debt cleared: `WA_TLM_r74_ally_rail_*` and `WA_TLM_r97_ea_*` deleted with their retired items R46 / R62 (write sites, init lines, registry rows; no version bump, §3.7). **The checker had been passing them on their own obituary** - the retirement ledger at the foot of the checklist names the item and its fix, so a whole-file search always found the token; and a bare `fix NN` anywhere in prose satisfied the fallback. Now: ledger cut off before searching (last heading occurrence - the table of contents names it too), token-only consumer test, and comments no longer count as write sites | `WA_TLM_core.txt`, `WA_AI_CONSTRUCTION_PRIORITY_railway_strategies.txt`, `WA_TLM_TELEMETRY_SYSTEM.md`, `tools/check_worklist.py`, `checklist.md`, `AGENTS.md`, `WA_AI_MILITARY_SYSTEM.md` |
| 2026-08-18 | error.log triage after the boot test. **One regression, ours, from the same day:** the engine-doc sync wrote markdown prose into `common/characters/_documentation.txt`, a `.txt` in a replace_path folder HOI4 parses - 105 `unexpected token` errors per boot, where the 13-line all-comment stub it replaced had produced none. Renamed to `.md`, guarded by a new `PARSED-DOC` check. Nothing in the log names anything else changed that day; the two runaway runtime signatures are queued | `common/characters/_documentation.md`, `tools/check_engine_docs.py`, `tools/engine_docs_manifest.json`, `wa-engine-reference/SKILL.md` |
| 2026-08-18 | `common/ai_faction_theaters` taken over by WA. Vanilla's file was live against WA's re-cut region map - 74 of the 223 ids its theatres name cover completely different ground (vanilla 239 = Alborz, WA 239 = Northern France), so 4 of WA's 6 `theatre_distribution_demand_increase` writers were inert or aimed at the wrong theatre. Generated from vanilla's theatres by province overlap, keeping `ai_will_do` / `cancel` verbatim; connectivity measured on the bitmap, positive-controlled against vanilla's own 30 theatres | `tools/gen_ai_faction_theaters.py`, `common/ai_faction_theaters/`, `descriptor.mod` (**gitignored - not committed**), `WA_AI_MILITARY_SYSTEM.md` §15, `AGENTS.md`, `wa-engine-reference/SKILL.md` |
| 2026-08-18 | The three "phantom" `ai_strategy` types: `force_ratio` and `infantry` removed from both docs and 35 file headers (every `type = infantry` is a `divisions_in_state` trigger hit); `naval_invasion_support_priority` **kept - the audit was wrong**, the token is in `hoi4.exe` and vanilla uses it 7x. Binary-grep-with-a-control added to the engine-reference skill | `WA_AI_MILITARY_SYSTEM.md`, `WA_AI_MILITARY_TYPES_REFERENCE.md`, 35x `common/ai_strategy/*_FRONT.txt` headers, `wa-engine-reference/SKILL.md`, `type-audit-2026-08-18.md` |
| 2026-08-18 | The `ai_strategy` type audit: 17 of 19 summary rows closed. §4's "Engine combination" column was inference for all but one pair - renamed and every cell tagged **E** / **I**. Real corrections: `theatre_distribution_demand_increase` is an absolute division count (doc said 0-500), `put_unit_buffers` `ratio` is a fraction of the whole army and same-`order_id` blocks SHARE it, `naval_dominance` sets rather than sums, `garrison`'s -5000 override is convention not engine text, `front_unit_request` has no documented base of 100, `dont_defend_ally_borders` "highest value wins" withdrawn. C6/C7 routed to their own row | `WA_AI_MILITARY_SYSTEM.md`, `WA_AI_MILITARY_TYPES_REFERENCE.md`, `type-audit-2026-08-18.md` |
| 2026-08-18 | `front_control` / Phase 5: the premise was wrong twice - Phase 5 shipped in `d149a204b` (50 slugs, 0 orphans) and the engine's `priority` covers only 7 of them; the other 43 are types with no `priority` field. `priority` is already in use on a brake > posture > routine ladder, not a layer ladder | `WA_AI_MILITARY_SYSTEM.md` §6 (rewritten, cites the engine section), `WA_AI_MILITARY_TYPES_REFERENCE.md`, `type-audit-2026-08-18.md` C2 + X1 |
| 2026-08-18 | 19 dead `05_defines.lua` writes: 17 deleted, 2 renamed to their live engine key with a new value, 1 given its missing `NDefines.NAir.` prefix. Logistics doc was wrong by 15x on `SUPPLY_FROM_DAMAGED_INFRA` | `common/defines/05_defines.lua`, `documentation/WA_AI_LOGISTICS_MODEL.md`, `documentation/WA_AI_MILITARY_SYSTEM.md`, `tools/constants_registry.json`, `lessons-log.md` |
| 2026-08-18 | `naval_dominance` out of scale: the 8 blocks at 1000 were a self-labelled probe (`289f1318f`) whose question R36 already answered - retired; region 356 moved to the Faction south corridor at 70 with its avoid pair | `WA_AI_NAVAL_COUNTRY_ENG.txt`, `WA_AI_NAVAL_FACTION_ALLIES.txt` |
| 2026-08-18 | Work queue + checklist decay checker (one ACTIVE, orphan fixes, stale statuses, dormancy) | `QUEUE.md`, `tools/check_worklist.py` |
| 2026-08-18 | Diagnosis protocol — six boxes; a missing script line makes the report `INCOMPLETE DIAGNOSIS` | `.claude/skills/wa-diagnosis/` |
| 2026-08-18 | Engine doc `ai_strategy` refreshed 2023-07 → 2024-11 (+291 lines), 20 citations moved to section names, drift checker | `tools/check_engine_docs.py` |
| 2026-08-18 | Engine reference: game install + Expert AI + wiki, with the "read before you assert" rule | `.claude/skills/wa-engine-reference/` |
| 2026-08-18 | `savegame.py`: 7 tooling defects that made wrong readings silent | `savegame.py`, `plans.py`, `airload.py`, `regions.py` |
| 2026-08-18 | Communication rule: answer first, MEASURED / DERIVED / ASSUMED labels | `AGENTS.md` § Talking to the user |
