# Building synthetic refineries before the shortage — diagnosis and Fix 76

**Date:** 2026-08-14 · **Evidence:** cloud campaign `be18f9c7-9d55-456b-9264-78cbdddb67f0`, build `d683fb022`, 126 monthly saves 1936.2–1946.7 · **Checklist item:** R48 · **Related:** `WA_REFINERY_CONTROLLER_REVIEW.md` (a *different* system — the on/off controller for an already-built park), checklist R24 (the industrial overextension brake), R29.

The ask was: *the AI should build synthetic refineries in advance of the shortage rather than reacting once it is already in a permanent deficit — USA as the motivating case.* This document is the diagnosis that preceded the fix, the fix, and its impact analysis.

---

## 1. Step 0 — the deficit is real, and it is not the resource anyone expected

The brief flagged a risk that the USA might not be in deficit at all and that ENG's aluminium collapse was the stronger case. Both halves of that turned out to be true *and* beside the point, because the resource a `synthetic_refinery` produces is neither aluminium nor steel.

### 1.1 The USA has no bauxite, iron, coal or oil problem

Reading the **EFFECTIVE** column (`to_use[0] + to_use[2]` — net available *minus* unmet demand, which is what `resource@X` returns in script; not `produced`, not `net`), across 12 saves spanning 1936.6–1946.7:

| Resource | Campaign minimum | From 1943 on |
| --- | --- | --- |
| bauxite | **+69** (1936.6) | +10 059 … +10 412 |
| iron | **+54** (1936.6) | +3 390 … +3 598 |
| coal | **+1 000** (1938.6) | +4 567 … +8 934, *rising* |
| oil | **+197** (1938.6) | +1 650 … +1 718, unmet demand exactly 0.0 in every save |

The USA never crosses zero on any of them. It also never parks a refinery: `aluminium_refinery_inactive` does not exist in a single USA save, and `steel_refinery_inactive` runs 47 → 76 → **0 from 1940.6** and stays there. The R29 shutdown pathology is an ENG phenomenon and is absent on the USA.

### 1.2 The USA's genuine deficit is rubber — which is exactly what the building makes

`common/buildings/00_buildings.txt`:

```
synthetic_refinery = {
    base_cost = 18000
    local_resources_rubber = 5
    country_modifiers = { fuel_gain_from_states = 2.0 }
    country_modifiers = { country_resource_cost_coal = 60 }
}
```

So "synthetic refinery" in WA means **rubber plus fuel, paid for in coal**. Measured USA rubber:

| date | rubber EFFECTIVE | imported | `wa_ai_needs_rubber` | `synthetic_refinery` levels |
| --- | ---: | ---: | ---: | ---: |
| 1936.6 | +1 | 10 | 0 | 0 |
| **1938.6** | −5.7 | 13.3 | **3** | 0 |
| 1939.9 | +3 | 20 | 3 | 0 |
| **1940.6** | +9 | **60** | 3 | 0 |
| **1941.6** | +4 | **86** | 3 | 0 |
| **1942.6** | **−168** | **0** | 3 | **0** |
| 1943.6 | −417.6 | 226.4 | 3 | 0 |
| 1943.12 | −378 | 239 | 3 | 0 |
| **1944.6** | −472.7 | 191.3 | 3 | **6** |
| 1945.6 | −338.8 | 245.2 | 3 | 25 |
| 1946.6 | −386.8 | 233.2 | 3 | 41 |
| 1946.7 | **−614** | 200 | 3 | 41 |

**Three numbers define the defect:**

- the deficit opens at **1942.6** (Japan cuts the supply: imports 86 → 0);
- the first refinery level appears at **1944.6** — **24 months late**;
- the warning signal `wa_ai_needs_rubber = 3` has been continuously on since **1938.6** — **72 months** before anything was built.

Even the eventual 41 levels are only 205 rubber/day against a −614 balance. This is a country that started raising an 18 000-IC-per-level industry two years after it needed it and never caught up.

ENG is the same shape, milder: rubber goes negative at 1942.6 (−78.1) and its synthetic park moves 2 → 4 (1944.6) → 5.

**So the user's country was right and the resource was rubber.** The bauxite/iron/coal framing in the brief pointed at the *activation controller* (`WA_REFINERY_CONTROLLER_REVIEW.md`), a genuinely separate system that switches an existing park on and off. Nothing below touches it.

---

## 2. Why it was late — every build path required the deficit to already exist

There are exactly three code paths that can raise a synthetic refinery for an AI country. All three are reactive on the same term.

| Path | Gate | Reachable on `be18f9c7`? |
| --- | --- | --- |
| `WA_AI_C.10` refinery branch (`events/WA_AI_construction.txt`) → `WA_AI_queue_REF` ×2 | `resource_consumed@rubber > 9`, **`resource@rubber < 0`**, `resource@coal > -10`, `has_tech = synth_oil_experiments`, **`date > 1941.1.1`** | **Yes for USA** — this built all 41 levels. **No for ENG** — C.10 has been silent since Jan 1943 (R24). |
| `WA_AI_build_refinery_resource_shortage_rubber` (`WA_AI_CONSTRUCTION_PRIORITY_strategies.txt`) → type-8 PC project | `WA_AI_resource_rubber_shortage_months = 3`, which itself needs **`resource@rubber < 0`** | **No for USA** — zero type-8 projects in its PC queue at 1940.6, 1943.6 and 1946.7. Yes for ENG. |
| `WA_AI_overext_substitute_MIC` refinery leg (Fix 39) | industry-overextension flag + tech + coal + law ≥ war economy | **No for anyone.** `wa_ai_overext_dbg_mic_redirects_refinery` is **absent on USA, ENG, GER, SOV and JAP at all 26 sampled dates** — it has never executed once. |

Two further facts fall out of that table and are worth recording independently of the fix.

**(a) The USA's priority-construction refinery lane is choked by radar.** Every refinery strategy sits behind `WA_AI_PC_active_nonrail_projects < 5`. The USA's PC queue at the three sampled dates:

| date | non-rail projects | composition |
| --- | ---: | --- |
| 1940.6 | **5** | radar ×4, infrastructure ×1 |
| 1943.6 | **8** | radar ×6, infrastructure ×1, UK air base ×1 (prio 300) |
| 1946.7 | **6** | radar ×4, infrastructure ×1, aluminium refinery ×1 (prio 250) |

The gate is `< 5` and the count is 5, 8, 6 — **shut at every sample**. The lone aluminium refinery at 1946.7 shows the door does open occasionally; it is a narrow, intermittent one. This is not fixed here (see §4.3) but it is why the fix does not rely on that host alone.

**(b) The C.10 branch carries a hard `date > 1941.1.1`.** That is a story gate in the AGENTS.md principle-1 sense: in a game whose rubber crisis arrives in 1938 or 1939, the reactive path is silent no matter how deep the deficit. Also not changed here — see §4.3.

---

## 3. The fix (Fix 76) — a proactive layer keyed on import dependence

### 3.1 The forward-looking signal

The question a proactive rule has to answer is *"what tells me a shortage is coming while my balance is still fine?"* The answer already sits in the same variable family the reactive paths read: **`resource_imported@rubber`**.

It is the volume this country covers from someone else's territory. It is therefore, by definition, the volume that vanishes when a war, a blockade or a faction realignment cuts the route — and it says so years before the balance moves. On the USA it reads 60 at 1940.6 and 86 at 1941.6, **with a positive balance both times**.

This deliberately reuses the prospecting system's existing vocabulary (`WA_AI_RESOURCE_NEEDS_triggers.txt` splits reactive / cooperative / proactive) rather than inventing a fourth axis. This is the **proactive** layer for refinery construction: not "I am short", but "I am structurally dependent".

### 3.2 The trigger

`WA_AI_CONSTRUCTION_should_pre_build_synth_rubber`, in `common/scripted_triggers/WA_AI_CONSTRUCTION_triggers.txt` — the system's own trigger file, not `WA_AI_CONFIG.txt`, because it is a *capability* question, not a country classification. It contains no tags.

| Term | Why |
| --- | --- |
| `has_tech = synth_oil_experiments` | the tech that unlocks the building |
| `has_capitulated = no`, `surrender_progress < 0.3` | same capability guards as the sibling refinery strategies |
| `resource_consumed@rubber > 9` | relevance floor; same value the reactive C.10 branch uses |
| **`resource@rubber > -1`** | **pre-shortage lane only** — see §3.3 |
| `resource_imported@rubber > 20` | the leading signal; above `WA_AI_check_resource_needs`' own import leg of 10 so trade noise cannot arm an 18 000-IC building |
| `resource@coal > 50`, `resource_imported@coal < 20` | mandatory: 60 coal/level, and WA sets `BASE_FACTORY_SPEED = 0.0` against `POWERED_FACTORY_SPEED = 2.5`, so a coal deficit is catastrophic rather than tolerable |
| `WA_AI_PC_has_project_civs_20` | scale; floored variant, because the bare engine availability reads ~0 once the vanilla queue saturates (the Fix 40 finding) |

On the measured USA data this arms at **1940.6** — two years before the shock, four years before the AI actually built anything.

### 3.3 Three properties that come from the shape, not from tuning

**Mutually exclusive with the reactive lanes, structurally.** `resource@rubber > -1` fires only while the balance is non-negative; every reactive path requires it to be negative. No call site can double-queue, and the proactive lane can never widen the reactive behaviour it sits beside — it covers exactly the window the reactive paths cannot see.

**Self-limiting, so no capacity counter is needed.** Each level raises domestic rubber production; the engine's trade AI then buys less; `resource_imported@rubber` falls below the floor; the trigger closes itself. A country-scope sum of `synthetic_refinery` over every owned state on a 2-day pulse would cost more than the feedback loop it replaced.

**Setup-agnostic.** No dates, no tags, no faction, ideology or war-entry terms, no assumption that Pearl Harbor happened. §4.2 walks two scenarios.

### 3.4 One host — and the second one was removed after measurement

**`WA_AI_C.10` refinery block** (`events/WA_AI_construction.txt`), a strictly additive `else_if`: the existing reactive `if` is byte-unchanged and can only be followed, never replaced. One `WA_AI_queue_REF` against the reactive branch's two, so speculative capacity ramps rather than binges; C.10's own 75–1000 day re-arm timer is the cadence bound.

A second host in `WA_AI_build_refinery_resource_shortage_rubber` (the priority-construction lane) was written, then **removed before shipping**. Its justification — *"ENG's C.10 is silent (R24), so ENG needs a PC host"* — is refuted by the campaign, and the refutation is worth recording because it is a class of error, not a slip: **the argument was about reachability and never checked eligibility.** ENG cannot use the lane at all, so which host it would have used is moot.

Who actually qualifies (rubber balance ≥ 0 **and** imports > 20 **and** the coal guard satisfied, at any sampled date):

| Tag | Qualifies? | Why |
| --- | --- | --- |
| **USA** | trigger yes — 1940.6, 1941.6 · **but the lane is DEAD, see below** | the motivating case; the trigger arms, **C.10 never fires** |
| **JAP** | yes — 1937.6 … 1940.6 | already raises a park unaided, 0 → 4 |
| **SOV** | yes — 1938.6 … 1941.12 | already raises a park unaided, 13 → 55 |
| **ENG** | **never** | owns Malaya → imports **0** rubber across the whole 1936.6–1941.6 positive-balance stretch. Every date it does import (1942.6+, 106–210) already has a negative balance and belongs to the reactive path. A pre-build lane cannot help a country whose supply is domestic right up to the moment it is conquered. |
| **GER** | **never** | rubber imports 0 from 1938 on — because GER is **already pre-built by hand**: the `original_tag = GER` startup block in `events/WA_AI_construction.txt` adds **22** refinery levels (park 4 → 15 → 34 → **36 by 1940.6**, against a balance that only turns negative in 1942.6) |
| **ITA** | **never** | clears the rubber terms three times (1937.6, 1940.6, 1943.6) and is rejected by the **coal guard** every time — it imports 700–1600 coal. The guard doing exactly its job. |

Two things follow. First, **the mod already pre-builds synthetic refineries — but only for Germany, hardcoded, at startup.** Fix 76 is the generic, tag-free form of a behaviour the repo already believed in. Second, the removed host had no beneficiary: every qualifying tag either reaches C.10 (USA) or already builds enough without help (JAP, SOV). Shipping it would have been code justified by a hypothesis the data contradicts.

*If a future campaign shows a **qualifying** country whose C.10 is silent, re-adding the PC `else_if` is the fix — but bring the measurement, and note that the PC strategy's own `active_nonrail < 5` gate is shut on exactly the big saturated-queue countries such an argument would invoke.*

### 3.4b CRITICAL DEFECT FOUND IN REVIEW (2026-08-15) — Fix 76 is inert for the USA, and for ENG

**Fix 76 as shipped cannot fire for its motivating country.** The proactive lane's only host is
`WA_AI_C.10`, and the daily dispatcher that calls it (`common/on_actions/WA_AI_misc_on_actions.txt:67-87`)
carries a pre-existing exclusion:

```
NOT = { OR = { AND = { tag = ENG  date < 1942.1.1 }
               AND = { tag = USA  date < 1942.6.1 } } }
```

The table above verified the *trigger's* terms against saves. It never checked whether the host event
fires. It does not, for exactly the two tags this fix cares about.

**Measured on campaign `be18f9c7`** (`savegame.py resources USA`, EFFECTIVE column = `net + deficit`,
which is what `resource@X` reads in script):

| date | rubber EFFECTIVE | rubber imported | trigger armed? | C.10 may fire? |
| --- | --- | --- | --- | --- |
| 1940.6 | **+9.0** | 60.0 | yes | **no** (date < 1942.6.1) |
| 1941.6 | **+4.0** | 86.0 | yes | **no** (date < 1942.6.1) |
| 1942.6 | **−168.0** | **0.0** | **no** — both the balance and the import term fail | yes |

The first pulse on which C.10 may fire for the USA is the first pulse on which the trigger is already
shut, and it never reopens. `wa_tlm_r48_prebuild_synth_n` will read **0** for the USA in every
campaign. ENG is excluded on the same mechanism, though ENG fails the import term anyway (row above).

### 3.4c RESOLVED by Fix 80 (2026-08-15) — option (b), after measuring the exposure

Three options were on the table: (a) hoist the proactive lane out of C.10 into its own host,
(b) narrow the dispatcher exclusion, (c) accept the lane as JAP/SOV-only. **(b) was chosen after
establishing what the exclusion actually protects**, which nobody had done — it is inherited from
Expert AI, predates the EAI → WA rename (`bd11fde6b`), and no WA commit states its purpose.

**The change is one term.** The exclusion stays, with an escape: `OR = { <the existing NOT block>,
WA_AI_CONSTRUCTION_should_pre_build_synth_rubber = yes }`. The escape therefore only opens on the
days the pre-build lane actually wants to build.

**Exposure, measured branch by branch rather than assumed.** C.10 has 16 branches; on an escape day
the pre-build lane is not the only one that evaluates, so each was checked:

| Branch | Status on an escape day | Why |
| --- | --- | --- |
| Reactive refinery | shut | mutually exclusive by construction — needs `rubber < 0`, the lane needs `>= 0` |
| Steel refinery | shut | USA steel effective **+392** (1940.6) and **+31** (1941.6) against a `< -20` bar |
| Aluminium smelter | shut | USA aluminium effective **+7** and **+17**, same bar |
| AA | shut | needs an enemy with deployed strategic/tactical bombers |
| Air base | shut | needs 1 000 deployed planes |
| Fuel silo | shut | excludes USA by name |
| ENG programme | n/a | `original_tag = ENG` |
| Generic tail | shut | an **empty `else_if`** for GER/ITA/USA/JAP — already a deliberate no-op |
| **Resource-state infrastructure** | **opens** | the only one |

The single branch that newly opens builds infrastructure on resource states, and the USA carries
`wa_ai_needs_aluminium = 3` from 1940. That is behaviour the blanket gate was suppressing, not a
regression introduced here.

**ENG is unaffected in practice.** It owns Malaya, imports 0 rubber across the whole positive-balance
stretch, and therefore never satisfies the pre-build trigger — the escape never opens for it, and its
large tag-specific build programme stays behind the date gate untouched.

**R48's USA legs are scoreable again.** The probe is unchanged.

### 3.5 Instrumentation

`WA_TLM_r48_prebuild_synth_n` / `_first_t` / `_last_t`, registered in `WA_TLM_TELEMETRY_SYSTEM.md` §5, zero-initialised in `WA_TLM_init_country`, `wa_tlm_version` ≥ 13. Both write sites count **verified effect only** — `break = 1` after `WA_AI_queue_REF` at the C.10 site, `WA_AI_PC_queue` growth at the PC site (the Fix 39/40 idiom) — never on entry to the code path.

The counter is *build-started*, not build-finished; read it against `savegame.py buildings <TAG> --match refinery`.

---

## 4. Impact analysis (AGENTS.md principle 3)

### 4.1 Blast radius — every caller and reader

| Symbol | Status | Readers |
| --- | --- | --- |
| `WA_AI_CONSTRUCTION_should_pre_build_synth_rubber` | **new** | 2, both created by this fix |
| `@AI_SYNTH_PREBUILD_IMPORT_FLOOR`, `@AI_SYNTH_PREBUILD_CONSUMED_FLOOR` | **new**, file-scoped to the triggers file where the only consumer lives — no cross-file duplication to keep in sync |
| `WA_AI_C.10` refinery `if` block | **unchanged**, byte for byte |
| `WA_AI_build_refinery_resource_shortage_rubber` | **unchanged code**, byte for byte — a comment block records the removed prototype host and why |
| `WA_AI_priority_queue_synthetic_refinery` | **unchanged, and no new caller** |
| `WA_AI_queue_REF` | **unchanged** — one new caller |
| `WA_TLM_init_country`, `@WA_TLM_VERSION` | additive rows + version bump; init is preserving, so resumed campaigns keep their values |

Nothing existing changed behaviour. Every new code path is behind a trigger that is false whenever any pre-existing path was true.

### 4.2 Who reaches it, and both scenarios walked

**Population.** Measured, not estimated: **USA, JAP and SOV only** — see the table in §3.4. ENG, GER and ITA never enter the qualifying state at any sampled date. Rubber *exporters* (MAL, INS, BRA) never arm. That is a small, well-understood set, and the one country with the actual problem is in it.

**Historical scenario.** USA: imports climb through 1939–41 with a healthy balance; the lane arms ~1940.6; C.10 adds one level per firing through 1941; Pearl Harbor cuts imports to zero at 1942.6; the balance turns negative, the proactive lane switches itself off by its own `> -1` term, and the pre-existing reactive branch takes over from a park that is no longer zero. Coal is never at risk (EFFECTIVE +1 573 to +2 403 in the arming window, imports 0).

**Ahistorical scenario.** Japan stays neutral and the USA is never cut off. Imports keep flowing, the lane builds a handful of levels, domestic output substitutes, `resource_imported@rubber` falls under 20, the trigger closes. The spend is real but bounded by the cadence and the feedback loop, and the output is not wasted — a synthetic refinery also carries `fuel_gain_from_states = 2.0`. Second variant: GER goes democratic, ITA is the aggressor, and ENG's Malayan supply is cut in 1938 — ENG's imports are high, the lane arms, and ENG pre-builds. Under the current code ENG would have waited for `date > 1941.1.1`.

### 4.3 What the surrounding `# Fix NN:` comments encode, and what is deliberately left alone

- **Fix 39** (`WA_AI_overext_substitute_MIC`): its refinery leg is provably dead (§2). The fix does not route through it and does not try to revive it — that is R24's problem.
- **Fix 40**: moved the refinery strategies out of `WA_AI_PC_can_afford_project` because the bare engine availability reads ~0 on a saturated queue, and shipped `WA_AI_PC_has_project_civs_20` as the floored replacement. The new trigger uses that floored variant for the same reason.
- **Fix 41**: the 250 strategic band. The proactive lane inherits it rather than inventing a fourth band — a pre-build is not cheaper to the country than a shortage-driven build, and a new band would change the ordering every other refinery caller sees.
- **`date > 1941.1.1` on the reactive C.10 branch — LEFT IN.** Removing it would widen the *reactive* lane for every AI from 1936. That is a much larger blast radius than this fix and a separate decision. The proactive lane carries no date, which closes the ahistorical gap that actually mattered. Recorded here so the next reader knows it was seen, not missed.
- **`WA_AI_PC_active_nonrail_projects < 5` — LEFT IN.** Shared by every PC strategy; it bounds queue growth for every country. The USA's radar-dominated queue choking its own refinery lane is a real finding (§2a) and deserves its own item, but the C.10 host makes Fix 76 work for the USA regardless.

### 4.4 Regression risk — stated explicitly

**The claim is: no country that did not previously build a synthetic refinery is made worse off on any existing path, because no existing path changed.** The residual risks are all on the new path:

1. **Coal, the one that matters.** 60 coal/level, spent *earlier* than before. The guard is the same pair the reactive lane already carried, but a pre-build front-loads it. A major whose `r48_prebuild_synth_n` is large *and* whose coal EFFECTIVE goes negative is a failure of the guard, not of the concept. Watch it first.
2. **Speculative IC.** 18 000 IC per level bought before the shortage exists. Bounded by one-level-per-firing, C.10's 75–1000 day timer, `_project_queue_max = 1` on the PC side, and the import feedback loop. Failure shape: a large counter next to a stalled civilian-factory count.
3. **`break` is caller-managed shared temp state — handled, not merely noted.** `WA_AI_queue_REF`'s `for_each_scope_loop` uses `break` as its break variable *and* reads it after the loop, and never zeroes it on entry. So zeroing is **required** for the call to do anything (a stale `1` breaks the loop immediately), and the incoming value is **saved and restored** around the branch, so nothing later in the same C.10 firing can see a value it would not have seen without the branch. This is the one place the fix touches state shared with unrelated code, and it is closed.

4. **A speculative build must never demolish industry — guarded.** When `WA_AI_queue_REF`'s slot loop finds nothing it falls through to a MIC-replacement leg that removes an `arms_factory` to make room. Defensible for the reactive branch (the country is already short); wrong for a refinery bought years early. The proactive branch therefore carries an `any_of_scopes` precondition requiring a genuinely free core site, which keeps it out of that leg. Without it, "one cheap level per firing" would have been false.
4. **JAP and SOV qualify without needing the lane.** Both already raise healthy synthetic parks (0 → 4, 13 → 55). The lane will now add a few levels to countries that were coping. Cheap, and the coal guard and the import feedback still bound it — but it is the population where the fix buys the least, and it is the one to check first if speculative spend shows up as a problem.

Full pass criteria and probes: checklist **R48**.

---

## 5. Findings handed off, not owned by this fix

1. **`wa_ai_overext_dbg_mic_redirects_refinery` has never been written**, on any of five majors, across 10.5 years. Fix 39's refinery substitution is dead code in practice. Belongs to **R24**, which has now FAILED seven campaigns with a related signature.
2. **The USA's PC queue is radar-dominated and permanently at or above the `active_nonrail < 5` gate** (5 / 8 / 6 at the three sampled dates, 4–6 of them radar). Every priority-construction strategy the USA has is competing against a standing radar backlog. Worth its own item.
3. **`resource@rubber < 0` is the sole trigger term shared by all three build paths** — the single point of reactivity this fix works around rather than removes. The same "no controller derives a signal from *intended* capacity, only from *realised* flow" blind spot that `WA_REFINERY_CONTROLLER_REVIEW.md` §4 names for the activation controller. Import dependence is one forward-looking signal; it is not the general answer to that blind spot.
