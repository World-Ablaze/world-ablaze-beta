# WA AI Military Value Economy

Phase 7 contract for every numeric value written by a military/naval `ai_strategy` block.
Companion to `WA_AI_MILITARY_SYSTEM.md` (layer model, domains, overlap policy). Where a
"typical range" in that document's section 4 conflicts with a rule here, **this document wins** —
section 4 described what the codebase did at Phase 1; this document prescribes what it must
converge to.

Enforced by `tools/military_economy_audit.py` (report-only linter; run it before and after any
change to `common/ai_strategy/`).

---

## 1. Why an economy

The 2026-08-09 frontline audit (vanilla 1.19.2 vs Expert AI 5.0 vs this mod) found the front
misbehaviour — fronts ignored for months, fronts manned far below available strength — is not one
bug but the product of an **escalation spiral**: with ~5,000 additively-stacked strategy blocks and
no declared baseline, no author knows what a new value competes against, so every rule shouts
louder than the unknown opposition. The measured results:

| Signal | Vanilla band | This mod (audit) |
| --- | --- | --- |
| `area_priority` | −300…+800, de-facto baseline 100 | −5000…+5000 (22 blocks at −5000) |
| `front_unit_request` (a **percent factor**; −100 already zeroes a front) | −200…+300 | −5000…+2000, 142 blocks at −1000 |
| `put_unit_buffers` ratio (fraction of the **whole army**) | ≤ 0.40, tightly gated | up to **10.0**, incl. an always-on 2.6 |
| Front demand defines (`MIN/DESIRED/MAX_UNITS_FACTOR_FRONT_ORDER`) | 1.0 / 1.1 / 1.0 | 2.0 / 3.0 / 3.0 |

Saturated values destroy the *ordering* the engine's theatre distributor depends on; whole-army
buffers hide the divisions that should have answered front demand; 3× inflated demand keeps the
distributor permanently in triage. Expert AI avoids all of this with the same engine by keeping
values small around a flat baseline and subtracting instead of shouting — that model, adapted to
WA's layer architecture, is what this contract encodes.

## 2. The model

1. **Flat baseline.** Every AI area carries a baseline `area_priority` of **100** for every country
   (Phase 8 introduces the single always-on DEFAULT block that provides it, replacing the legacy
   `wa_default.txt` partial baseline). All other `area_priority` blocks are **deltas** against 100.
2. **Suppress to zero, never to a black hole.** "This area does not matter to this country right
   now" is expressed by driving the *net* sum toward 0 (a delta near −100), not by −2000. The net
   per (country, area) must stay ≥ −200. Deep negatives add nothing once the area has lost the
   sort — they only make every other signal unreadable.
3. **Boost narrowly, brake broadly.** Large positive priorities are reserved for *narrow* areas
   (1–2 strategic regions — mint one if needed, `common/ai_areas/`); continent-scale areas are only
   ever nudged. Precision on the accelerator, a broad brush on the brake.
4. **Vetoes carry their own escape hatch.** Any veto-class value (see per-type rules) must
   self-disable for a country the veto would starve — typically `NOT = { any_state = { <target
   area> is_owned_by = ROOT } }` or an archetype trigger encoding the same. A veto that can apply
   to the country whose homeland it covers is a starvation bug by construction.
5. **Buffers are garrisons, not armies.** `put_unit_buffers` `ratio` is a fraction of the entire
   army; blocks must be small, threat-gated, and self-disabling. Reserving multiples of the army is
   never correct.
6. **Concentration moves the schwerpunkt, not the garrison.** Only the AIFC system writes
   `force_concentration_*`. Steering *where the AI attacks* uses AIFC; steering *how many units a
   front holds* uses the request/priority types. Mixing the two is how secondary fronts get
   stripped.
7. **Absent measurements read as unknown, not zero.** Scripted variables consumed by `enable`
   triggers (e.g. `WA_AI_fielded_eq_ratio`) must be guarded with `has_variable` on any branch where
   an absent value would trigger a brake or a suppression.

## 3. Per-type rules (normative, linted)

| # | Type | Rule |
| --- | --- | --- |
| E1 | `area_priority` | Delta in **[−200, +200]** for areas of ≥3 strategic regions; up to **+1000** for narrow areas (≤2 regions). Baseline is provided by exactly one DEFAULT block (Phase 8). |
| E2 | `front_unit_request` | **[−100, +200]**. It is a percent factor: −100 is a full veto; anything lower is saturation. Values ≤ −50 are veto-class → escape-hatch rule (§2.4) applies. |
| E3 | `theatre_distribution_demand_increase` | **[0, +15]**. The value is an absolute division count. |
| E4 | `put_unit_buffers` | Single-block `ratio` ≤ **0.25** for a normal garrison. No `enable = { always = yes }` — buffers must at least be war-gated. `subtract_fronts_from_need = no` requires a `# pool:` comment in the block explaining why this buffer must not yield to front demand (cf. the Atlantic Wall lesson). The ladder above 0.25 requires a `# siege:` comment: **0.5** for a fortress line or strategic staging (Maginot, El Alamein, pre-D-Day US army in Britain), **1.0** for an exile/last-stand scenario (government-in-exile, continental last stand) — never more, **and the `enable` must match the justification** — an ungated 0.5 is not a siege ratio, it is a permanent hoard (Fix 100). `area =` names the areas whose orders may draw on the buffered units: omitting it seals the garrison so nothing else can use it, which is correct for a fortress point (the GER *festung* and SOV Stalin-line families) and wrong for a theatre reserve the local front is meant to draw on. Reference points: vanilla max 0.40; Expert AI's whole home-island pool is 0.45 total. |
| E4b | `put_unit_buffers` pool coherence | Entries sharing an `order_id` share **one ratio pool** (`common/ai_strategy/documentation.info section put_unit_buffers`; the 2026-08-09 Atlantic Wall lesson). All members of a pool must therefore agree on `subtract_fronts_from_need` and on whether they declare an `area` — otherwise one member's flag silently decides for states it was never written for. A garrison that must hold against front demand gets **its own** `order_id`, not a shared one. |
| E4c | `put_unit_buffers` country budget | Per country, the summed ratio of the **non-yielding** pools (those containing a `subtract_fronts_from_need = no`) stays ≤ **0.75** of the army. A yielding buffer shrinks as fronts demand units and cannot starve a front indefinitely; a non-yielding one can, so rule §2.5 ("reserving multiples of the army is never correct") is enforced on that subset. Counted worst-case: `enable` gating is not statically decidable, so mutually exclusive blocks count as simultaneous. A pool's size is the largest ratio among its members. |
| E5 | `force_concentration_factor` / `_front_factor` / `_target_weight` | Written by `WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt` (the only *generic* writer). A Country-layer FRONT file may carry a country-specific concentration block **only** with an `# aifc-tuning:` comment explaining how it complements the AIFC sector engine (e.g. the Maginot-suicide safety rails, scripted Fall Rot / Barbarossa schwerpunkts). Boost and paired suppression must share the same gating (same `enable`, same `ratio` gate or none on both). |
| E6 | `front_armor_score` | **[−150, +400]**; the ±schwerpunkt pair belongs to AIFC, country files may add within [−100, +100]. |
| E7 | `garrison` | **[0, +200]**, or exactly **−5000** as the documented single-writer force-off. Other negatives are noise. |
| E8 | Front-math defines | `NDefines.NAI` front demand/assignment values (`MIN/DESIRED/MAX_UNITS_FACTOR_*_ORDER`, `FRONT_UNITS_CAP_FACTOR`, …) stay at vanilla unless the deviation cites a campaign measurement in a comment (`-- measured: <campaign/save>, <finding>`). |
| E9 | Legacy containment | Files outside `WA_AI_MILITARY_*` / `WA_AI_NAVAL_*` must not contain front-domain types (`area_priority`, `front_unit_request`, `front_armor_score`, `front_control`, `put_unit_buffers`, `theatre_distribution_demand_increase`, `force_concentration_*`). Existing occurrences are the Phase 7c retirement worklist, not a licence. |
| E10 | Gating | Every strategy block declares `enable`; `always = yes` requires the `# always-on:` justification comment (rule 1 of `WA_AI_MILITARY_SYSTEM.md` §5, now linted). |

## 4. Migration phases

| Phase | Scope | Status |
| --- | --- | --- |
| 7a | Measurement: observer campaign, count divisions in buffer orders vs front orders vs unassigned per misbehaving country; net priority sums per area. Grounds E8 and the E1/E2 renormalisation. | pending (needs a cloud test campaign) |
| 7b | Unambiguous defect fixes valid under any economy: `has_variable` guards on `WA_AI_fielded_eq_ratio` readers (done 2026-08-09), AIFC gating seams (boost/suppression pairing fixed 2026-08-09; **still open:** the sector list refreshes weekly while the engine re-scores every 5 days, so a captured corridor can leave the −99 catch-all pointing at stale states for up to 7 days — fix is a cheap daily validity check in `WA_AI_misc_on_actions.txt`, deferred because that file carries unrelated in-flight work), no-op define cleanup. | in progress |
| 7c | Retire the legacy strategy stack (61 pre-refactor files, ~2,500 blocks) — relocate or delete per the Phase 2 method, parity-checked. E9 count goes to zero here. | pending |
| 8 | Renormalise values to this contract, one layer at a time (DEFAULT → FACTION → COUNTRY, worst offenders first: GER, ENG, SOV, USA theatre files), introduce the baseline block, campaign-test per stage. E1–E7 counts go to zero here. | pending |

The linter's per-rule violation count is the burndown metric across 7c/8. New or modified blocks
must conform immediately; pre-existing violations are worklist, and must not be *extended*.
