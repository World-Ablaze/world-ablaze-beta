# WA_AI lend-lease surplus relief — design v2 (Fix 92, implemented 2026-08-16)

Status: DESIGN, option C **validated by boot test 2026-08-16** (`wa_test.300` + `WA_TEST_LLR_send_one`: GER→ROM `send_equipment` with `amount` and `target` rendered from variables through `meta_effect`, four archetypes, stock moved; the donor needs stock — `ae 10000` first). **IMPLEMENTED as Fix 92 the same day** — `common/script_constants/wa_ai_lend_lease.txt` (9 rows), the CAPABILITY section of `WA_AI_LEND_LEASE_triggers.txt`, the relief core + 9 legs in `WA_AI_lend_lease_effects.txt`, pathfind type 3, WA_TLM v18 `llr_*`, checklist R7b recut. Deviations from the draft below: no `consumes` gate (waste is bounded by `starve`, once); heavy AT/AA, pack and rocket artillery, mechanized NOT in the first 9 rows (add a row + a leg + grow the TLM arrays); tiering by donor-stock bars `tier2`/`tier4` per row. Owes a boot test (see the end of this file). Written after campaign `a232d96c` (checklist R7b/R56) and three
modder rulings the same day. The nine overland legs described below are shipped.

## 2026-08-19 maritime convoy extension (R56 recut)

Campaign `2f8cbd51` closes the production/transfer diagnosis: in 1943.1 ENG had 0 free convoys,
101 controlled dockyards and no convoy line; USA had 1,507 free, 122 dockyards, no convoy line,
and no outgoing lend-lease. The extension is deliberately a **separate maritime branch**. It
does not weaken or bypass the Fix-92 land-access rule for the nine land-equipment rows.

Recipient reserve and maximum weekly send scale with the recipient's naval capacity:

| Recipient dockyards | Minor reserve | Major reserve | Weekly cap |
| ---: | ---: | ---: | ---: |
| 0-20 | 200 | 1,000 | 100 |
| 21-40 | 500 | 1,000 | 250 |
| 41-80 | 1,000 | 1,000 | 500 |
| 81+ | 1,500 | 1,500 | 750 |

The recipient formula is `max(dockyard-band reserve, 1,000 when is_major)`. Thus the January
1943 Soviet Union (22 owned dockyards in the save extraction) targets 1,000 rather than 500,
while a small South African network remains at 200. The weekly cap remains dockyard-scaled:
the Soviet band moves at most 250 per successful weekly pull.

Controlled transfer-only SOV walk at the real weekly cadence, with one eligible 81+ dockyard
donor initially holding 2,500 free; production, losses and changes in convoy usage are fixed at zero:

| Time | Donor free | SOV free | Action |
| --- | ---: | ---: | --- |
| t0, weekly pulse | 2,500 | 0 | send 250 |
| t1, after one week | 2,250 | 250 | send 250 |
| t2, after two weeks | 2,000 | 500 | send 250 |
| t3, after three weeks | 1,750 | 750 | send 250 |
| t4, after four weeks | 1,500 | 1,000 | target reached; no send |
| t5, next weekly pulse | 1,500 | 1,000 | recipient is not starving; no maritime donor selection |

**DERIVED** Four sends of 250 suffice to fill SOV from 0 to 1,000 if no external flow reduces
either free stockpile during the interval. A campaign must measure production, losses and usage.

The donor keeps its own scale-aware floor (200 / 300 / 500 / 1,000). The amount is the minimum
of recipient weekly cap, recipient gap, and donor stock above that floor. Thus the result neither
overshoots the recipient target nor strips the donor. The pair is tag-free: both countries are
living AIs with maritime capacity, and they are in the same faction, share a war, or already carry
the explicit WA lend-lease target flag. One recipient selects at most one maritime donor per weekly
pulse. An 81+ dockyard major also receives convoy `unit_ratio +85` and a 15-dockyard minimum while
any eligible partner is short; every naval producer now receives the baseline ratio 15.

Bounded walk at the real weekly cadence (USA 1,507 free; ENG 0 free in 1943.1):

| Time | USA free | ENG free | Action |
| --- | ---: | ---: | --- |
| t0, weekly pulse | 1,507 | 0 | USA selected; amount clamps to min(750, 1,500 gap, 507 donor headroom) = 507 |
| t1, after verified send | 1,000 | 507 | recipient stock rose; TLM records convoy idx 10 |
| t2, next weekly pulse without new production | 1,000 | 507 | no donor scan succeeds: USA is at its floor |

With production replenishment, later weekly sends resume until ENG reaches 1,500. Strategy removal
after that condition becomes false depends on the engine's internal reevaluation cadence and remains
unverified until a campaign. South Africa in the 0-20 band instead fills 0 -> 100 -> 200 over two
successful weekly sends.

Objection retained from Fix 92: **"the relief system is an overland transfer by ruling"**. Mine
covers it because the convoy branch is separate and never calls the A* used by the nine land cargos.

## 1. Rulings that drive the redesign

1. **Land access only.** The `send_equipment` relief imitates an overland truck
   convoy. It fires only when a state path exists between the two CAPITALS that
   crosses nothing but territory controlled by the recipient, the donor, a subject
   of either, or a faction member / co-belligerent of the recipient. USA→ENG,
   USA→SOV, CAN→SOV, anything by sea = the ENGINE's native lend-lease, never this.
   Same landmass is NOT enough (Eurasia is one landmass).
2. **Archetypes are complementary, never summed.** `infantry_equipment` and
   `heavy_infantry_equipment` are both consumed by a WA division; a leg exists per
   archetype, gates read that archetype only, and a country short of one gets that
   one.
3. **Scope widens.** Beyond rifles/support: heavy infantry, artillery (line, heavy,
   pack, rocket), anti-tank / heavy AT, anti-air / heavy AA, trucks
   (`motorized_equipment`), trains (`train_equipment`), possibly mechanized. Convoys
   leave (sea transfer by construction, and the leg never fired — donor bar > 1 999
   free convoys is unreachable when every major is short).

## 2. What is invariant across archetypes (→ shared core)

| Concern | Today | v2 |
| --- | --- | --- |
| Who pulls | recipient, weekly, `random_other_country` = 1 donor/week | same (proven scope form: send runs in donor scope, `target = ROOT`) |
| Pair validity | `WA_AI_LEND_LEASE_relief_pair_is_valid` (not self, both alive, donor AI, common enemy OR WA target flag) | same + **land-access path** (see §4), evaluated ONCE per pair per pull and cached in a temp var for all legs |
| Donor policy | GER/SOV export gates (`WA_AI_special_lend_lease_rules_*`) | unchanged |
| Tiering | 3 hard-coded tiers per leg | one shared rule: `amount = base × tier`, tier ∈ {1,2,4} by donor stock vs `donor_floor` (×1 / ×~2 / ×~4) — same shape as today, numbers per archetype in script constants |
| Telemetry | none | `WA_TLM_llr_*` family (v18): `donor_selected_n`, `path_refused_n`, `sent_n^<arch_idx>`, `sent_amount^<arch_idx>`, `first_t/last_t` — counted on the verified `send_equipment`, never on entry |
| Logging | one line | one line per leg fired, with archetype |

## 3. What varies per archetype (→ a row in a table)

Per archetype `A` (index `i`, used for the TLM arrays):

| Field | Meaning | Lives in |
| --- | --- | --- |
| `donor_floor` | donor keeps at least this; `has_equipment = { A > donor_floor }` | `common/script_constants/wa_ai_lend_lease.txt` → `constant:wa_ai_lend_lease.<A>.donor_floor` |
| `starve` | recipient below this = starving; `NOT = { has_equipment = { A > starve } }` | idem `.starve` |
| `base` | tier-1 amount | idem `.base` |
| `tier2` / `tier4` | donor stock bars for ×2 / ×4 | idem `.tier2`, `.tier4` (or one shared multiplier — decide) |
| consumes gate | recipient can use it at all: trucks → any template with motorized/mechanized or `has_tech`; trains → always (rail supply); AT/AA/artillery → `has_equipment` history or template check; hv_inf → mod-wide yes | scripted trigger `WA_AI_LEND_LEASE_consumes_<A>` (one per archetype, most are `always = yes`) |

Rows (initial proposal, thresholds to calibrate — the current ones are: inf 34 999 / 10 000 / 6 000; support 5 999 / 3 999 / 1 200):

| A | donor_floor | starve | base | consumes |
| --- | --- | --- | --- | --- |
| infantry_equipment | 34 999 | 10 000 | 6 000 | always |
| heavy_infantry_equipment | 20 000 | 6 000 | 3 000 | always |
| support_equipment | 5 999 | 3 999 | 1 200 | always |
| artillery_equipment | 4 000 | 1 000 | 500 | always |
| heavy_artillery_equipment | 2 000 | 400 | 200 | fields it |
| pack_artillery_equipment | 2 000 | 400 | 200 | fields it |
| rocket_artillery_equipment | 1 500 | 300 | 150 | fields it |
| anti_tank_equipment / heavy_anti_tank_equipment | 2 000 / 1 000 | 500 / 200 | 250 / 100 | fields it |
| anti_air_equipment / heavy_anti_air_equipment | 2 000 / 1 000 | 500 / 200 | 250 / 100 | fields it |
| motorized_equipment (trucks) | 6 000 | 1 500 | 750 | fields motorized/mech OR supply trucks |
| train_equipment | 300 | 60 | 30 | always (rail supply) |

"fields it": recipient has ≥1 deployed division whose template uses the archetype —
readable only through `has_equipment`/`has_deployed_equipment`-style tokens; if no
cheap trigger exists, fall back to `always = yes` for artillery/AT/AA (every WA
army fields some) and keep the explicit check for trucks only.

## 4. Land-access check

`WA_AI_PATHFIND_get_path` (state-level A*, `WA_AI_pathfinding_effects.txt`, 75
iterations) with a NEW pathfind type (3, additive — types 0/1/2 untouched):

```
neighbour filter (type 3):
  impassable = no
  CONTROLLER = { OR = {
      tag = ROOT                       # recipient (pull scope)
      tag = var:_llr_donor             # donor
      is_subject_of = ROOT
      is_subject_of = var:_llr_donor
      is_in_faction_with = ROOT
      has_war_together_with = ROOT     # co-belligerent (FIN–GER case)
  } }
```

start = recipient capital state, target = donor capital state. Called once per pair
per weekly pull, inside `random_other_country`'s body (NOT in its `limit`, which
would run the A* for every candidate). Result → `_llr_path_ok`; every leg tests it.
Cost: ≤ 1 A* per starving recipient per week; 75 iterations covers Berlin→Bucharest
/ Delhi→Chungking; if it does not, the pair is refused (conservative) and
`path_refused_n` says so.

Open point: `WA_AI_PATHFIND_get_path` reads ROOT for logging flags and uses
`_pathfind_type`; verify it is re-entrant inside `random_other_country` (temp arrays
`open_list`, `neighbors` are cleared per call — check `closed_list` too).

## 5. Factorisation — how the legs are written

PDXScript constraint: `send_equipment = { type = <literal archetype> … }` — the
archetype cannot be a variable directly. **`meta_effect` is NOT ruled out** (correction
2026-08-16): the v1 push version (`982ebfd12`) used it and never fired, but the
rebuild commit `128cc7995` names two independent causes — an unpassable AND'd surplus
gate, and a temp variable resolved after a scope switch with the unproven
`equipment =` parameter — and dropped meta_effect out of caution, not proof. It renders
text and compiles it; the real pitfalls are (a) temp vars must be set in the SAME
scope as the render, (b) the rendered token must be an exact archetype name,
(c) failure is silent → prove it with a boot test (WA_AI_logging + recipient stock
moving) and count only the verified send in TLM. Three options:

- **C (preferred if the boot test passes): one meta_effect send in the core.**
  `text = { send_equipment = { type = [ARCH] amount = [AMT] target = [TGT] } }` with
  `AMT = "[?_llr_amount]"`, `TGT = "[ROOT.GetTag]"`, and `ARCH` rendered from a
  per-archetype 2-line index→literal mapping (variables are numeric; there is no
  named object whose `GetName` yields an archetype token, so the literal still has
  to be written once per archetype — but only once, not per tier/gate). Gates read
  the archetype through the same index → `has_equipment` still needs the literal, so
  the per-archetype trigger triple stays (small). Net: core written once, ~2–4 lines
  per archetype. **Boot test PASSED 2026-08-16** (`events/wa_events_test.txt` `wa_test.300`, `common/scripted_effects/WA_TEST_lend_lease_relief.txt`): `amount = [AMT]` / `target = [TGT]` rendered from temp variables in the same scope, `type` literal per branch — the transfer lands. Keep the harness; it is the regression test for the send form.
  **Probe #2 FAILED the same day (and was removed):** rendering the archetype token itself
  from a scripted localisation keyed on a country variable (`[GetWA_TEST_LLR_arch]`) —
  the `log` line rendered it, but the `meta_effect` / `meta_trigger` render received the
  fallback branch (`NONE`; error.log: `equipment type is not valid (memfile:1: has_equipment)`,
  `invalid database object … NONE`): the meta render does not see the country scope's
  variables through scripted loc. Two side lessons: (a) a `has_equipment` meta_trigger with
  an invalid token EVALUATES TRUE — a malformed meta gate lets everything through;
  (b) a loc value equal to an existing key (`infantry_equipment`) is re-localised to its
  display name. So the archetype literal stays per branch; `amount`/`target`/thresholds
  are the data-driven part.

- **A (recommended): generator.** `tools/lend_lease_relief_generator.py` reads a
  small table (the §3 rows) and emits (i) the three scripted triggers per archetype
  into a marked region of `WA_AI_LEND_LEASE_triggers.txt`, (ii) the leg blocks into a
  marked region of `WA_AI_lend_lease_effects.txt`, (iii) the script-constants file,
  (iv) the TLM index table. Same dry-run discipline as `tools/ai_will_do_replacer_*`.
  Adding an archetype = one row.
- **B: hand-written legs** from one template comment; acceptable up to ~6 archetypes,
  drifts beyond.

Either way the shared core (pair validity, path, tier rule, telemetry, logging) is
written once and the per-archetype block is ~10 lines.

## 6. Interactions and risks (impact analysis, to complete before shipping)

- The land-access rule REMOVES the flows observed on `a232d96c` (USA→SOV 30 430
  rifles, USA/CAN→ENG/SOV support). Those pairs then depend on the engine's native
  lend-lease, which is currently dead for the USA (0 agreements 1943–46; separate
  diagnosis task). Ship the rule together with — or after — that repair, or SOV/ENG
  lose their only support-equipment source.
- Support drip pinning recipients at 4 000–5 100 with own production ≈ 0 (seen on
  every campaign since `9be92c89`): a per-archetype `starve` bar just above the drip
  reproduces this; consider a "recipient must have a production line for A or a
  deficit vs deployed need" clause later, not now.
- `random_other_country` one-donor lottery: still the suspect for silent weeks; the
  `donor_selected_n` counter finally measures it.
- Removing the convoy leg also removes `WA_AI_LEND_LEASE_*_convoys` triggers; grep
  callers (`WA_AI_PRODUCTION_DEFAULT_navy.txt` header mentions them in a comment
  only).
- Checklist: R7b recut per archetype (GER-created hv_inf/artillery/AT in ROM/HUN/BUL;
  negative probe: zero `creator=USA` `send_equipment` entries in ENG/SOV stockpiles
  after the fix), plus `path_refused_n > 0` as the mechanism probe.

## 6b. Accepted consequences (architecture review 2026-08-16)

- **Fix 92 ships BEFORE the native USA lend-lease repair.** Until that lands, the USA→SOV /
  USA→ENG / CAN→SOV support-equipment and rifle flows seen on `a232d96c` (USA→SOV 30 430
  rifles, USA/CAN support into ENG/SOV) stop and are not replaced by anything. Accepted by the
  modder's ruling (the sea channel is the engine's), and it is the point: the native path has to
  carry it. Score both on the next campaign; if SOV/ENG support goes to zero and the native path
  is still dead, that is the native diagnosis' problem, not a reason to re-open the sea leg here.
- `WA_AI_LEND_LEASE_has_exportable_surplus` (the OR read by the GER/SOV native-export escape
  gates in `WA_AI_special_lend_lease_rules_SENDER/TARGET`, triggers.txt ~:424 / :450 / :520) now
  includes heavy_infantry: GER holding > 20 000 free hv_inf may now be allowed to export
  natively where it was not before. Intended — that stock is its real surplus.
- The two `WA_TLM_llr_*` arrays are now `size = 11` (idx 0 unused, land rows 1-9, convoy 10).
  Both WA_TLM init and the late-tag guard grow any array whose `^num < 11`, so a resumed v18-v27
  save preserves rows 1-9 while gaining row 10.

- **FIN beside a GER surplus (the 9be92c89 case) reverts to starving by design:** the type-3
  filter's co-belligerent clause admits Finnish/German-controlled states, but there is no land
  route Helsinki→Berlin that avoids Sweden/USSR, so the A* refuses the pair. Correct under the
  ruling (Finland was supplied by sea) — the engine's native lend-lease is the channel.

## 7. Boot test (v18 build) — DEFERRED to the next cloud campaign by the modder (2026-08-16)

The telemetry below is what replaces steps 2–5: on the next cloud run, `wa_tlm_llr_send_failed_n`
must read 0 on every donor (else the meta send is broken), `llr_path_refused_n > 0` on at least
one overseas recipient and `llr_sent_n^*` > 0 on at least one continental pair (else the A* is
broken one way or the other), `llr_starving_n` > `llr_donor_selected_n` ≥ `llr_path_refused_n`.
Steps kept for a local re-run if the cloud reading is ambiguous.

1. Start 1936, console `tag GER`, `ae 20000` (rifles), `event wa_test.300` — the send form (regression).
2. Then set logging on a starving continental minor and its donor, e.g. `tag ROM`, drain a
   stock (`ae -X`) below the row's `starve`, `tag GER`, `ae 30000` hv_inf; give both
   `WA_AI_logging` (`set_country_flag WA_AI_logging` via a debug decision or `event`) and run
   a week: game.log must show `LEND-LEASE: surplus relief archetype 2 x 3000 received from
   German Reich` on ROM, ROM's stock moves, `wa_tlm_llr_sent_n^2` on GER = 1.
3. Sea pair control: `tag ENG` drained + `tag USA` rich → after a week the log shows
   `refused - no land access between capitals` (or nothing at all if the lottery did not pick
   USA) and `wa_tlm_llr_path_refused_n` on ENG > 0 while ENG's stock does NOT move.
4. error.log clean of `memfile:1`, `WA_AI_LEND_LEASE`, `WA_AI_PATHFIND` lines. Set
   `WA_AI_pathfind_logging` on the recipient to see `PATHFIND: START/found path/END` lines and
   record the sign of `[?_pathfind_start]` (state `.id` is engine-encoded).
5. `wa_tlm_llr_send_failed_n` on the donor must stay 0.
