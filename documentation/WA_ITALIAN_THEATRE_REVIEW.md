# The Italian theatre: why the Allied campaign reverses

**Status:** DIAGNOSED 2026-08-12; **causes 1, 2 and the Normandy sibling FIXED the same day — see §10. Causes 3 and 4 remain open.** Written from campaign `9a4cd657` (cloud, BHU observer, 122 monthly saves 1936.2–1946.3, build HEAD `60c7d8f3c`), cross-read against `31eaf7e6` and `911bed3c`. Owner item: **R17** in `.claude/skills/wa-campaign-checklist/references/checklist.md`.

**Read this before touching any Italian-theatre `ai_strategy` block.** Three campaigns of R17 failures were scored as landing/garrison problems. They are not. The landings work — R18 confirms every scripted invasion delivers its designed division count, three campaigns running. The theatre reverses for reasons downstream of the landings, and §1 is the one that matters.

---

## 1. Headline: the Allies are not beaten in Italy — they stand down, and *winning* is what switches them off

The Italian support set is **control-inverted**. Every Allied boost is conditioned on *the enemy* holding ground; every Allied suppression is conditioned on *the Allies* holding it. The entire theatre economy therefore flips sign at a single event: the capture of Calabria (state **156**), which is the moment the Sicily bridgehead succeeds.

At that instant, six things happen at once:

| Event | Δ |
| --- | --- |
| `ALLIES_hold_sicily_bridge_THEATRE` dies (`FACTION_ALLIES_THEATRE.txt:663-698`, needs enemy-held 156) | `area_priority` south_italy **−800**, italy **−400** |
| `ALLIES_hold_sicily_bridge_FRONT` dies (`FACTION_ALLIES_FRONT.txt:872-902`) | region 238 **−50** |
| `ALLIES_no_italy_invasion_early_THEATRE` arms (`FACTION_ALLIES_THEATRE.txt:100-146`) | `area_priority` italy **−200** |
| `ALLIES_no_italy_invasion_early_INVASION` arms (`FACTION_ALLIES_INVASION.txt:435-511`) | `invade ITA` **−2000**, `invasion_unit_request` tag ITA **−1000**, area italy **−100** |
| `USA_sicily_push` resumes (`COUNTRY_USA_FRONT.txt:438-495`) | region 238 **−50** |
| `USA_unit_clumping_fix_2_south_italy` resumes (`COUNTRY_USA_FRONT.txt:351-383`) | south_italy **−35** |
| `ENG_war_against_ITA_2_FRONT` already dead (`COUNTRY_ENG_FRONT.txt:533-575`, needs `115/1032/156 = is_controlled_by = ITA`) | italy **−100**, south_italy **−25** |

**Net swing: `area_priority` italy −600, south_italy −800; the USA's request on region 238 goes from +50 to −85.**

These gates are deliberately identical — the comments at `COUNTRY_USA_FRONT.txt:341-350` and `:453-461` say so explicitly. The bridge blocks and the suppression blocks were designed as a matched pair with a handover; what was not noticed is that the handover hands the theatre *down*, not across.

### 1.1 The unbounded branch — `no_italy_invasion_early` is not early

`FACTION_ALLIES_THEATRE.txt:100-146` gates on:

```
OR = { 1944.3.1 < date < 1944.6.6            # D-Day prep window
       date < 1943.7.1                        # pre-Husky
       AND = { allies control 115, 1032, 156 } }   # <-- NO EXIT CONDITION
```

The third branch has no upper bound. From the day the Allies hold Sicily and Calabria it is **permanently true for the rest of the game**, and it takes the whole invasion economy with it (`invade ITA −2000`). The block's name describes branch 2; branch 3 is a permanent theatre veto wearing branch 2's name.

---

## 2. The defection cliff: the same trigger, wired in opposite directions

Italy leaving the Axis (1944.4.14 in `9a4cd657`) simultaneously arms an Allied brake and a German boost on the *same two strategic regions*:

| Side | Block | file:line | Δ on regions 21 + 23 |
| --- | --- | --- | --- |
| Allies | `ALLIES_avoid_italy_overstack_after_flip` | `FACTION_ALLIES_FRONT.txt:82-98` | **−80** (replaces the −40 of `:66-78`, which keys on `has_war_with = ITA` and switches off) |
| GER | `GER_frontline_requests_6` | `COUNTRY_GER_FRONT.txt:1013-1036` | **+100 / +100** |
| GER | `GER_protect_our_weak_underbelly` | `COUNTRY_GER_FRONT.txt:1257-1289` | **+200** — survives the flip via its `is_in_faction_with = RIT` disjunct |
| RIT | `RIT_defend_italy`, `always = yes` | `COUNTRY_RIT_FRONT.txt:13-41` | **+200** each on 238 / 23 / 21 |

Net on Rome's region (23), mid-1944: **USA −145 to −170** (−65 always-on from `COUNTRY_USA_FRONT.txt:310-338`, −80 overstack, −25 more during the D-Day prep window) against **GER+RIT +300 to +400**.

**This prediction is confirmed in the saves.** ENG nets +20 on the same regions while the USA nets −145, so the theatre should become visibly British — and it does. Divisions in Italy, 1944.10 → 1945.6:

- **USA:** 1, 0, 2, 4, 3, 4, 1, 4, 3
- **ENG:** 10, 10, 4, 26, 26, 27, 29, 36, 34

The United States effectively leaves the Italian theatre while the war there is still being fought.

---

## 3. What the theatre actually looks like (campaign `9a4cd657`)

Divisions physically located in the 18 originally-Italian states, from a `units`-scoped walk cross-checked against `savegame.py army` at three dates (exact agreement on USA/ENG/GER/RIT).

| Month | Allied | Axis | ratio | Southernmost Axis-held state |
| --- | --- | --- | --- | --- |
| 1943.8 | 5 | 44 | 0.11 | 156 Calabria |
| 1943.10 | 23 | 32 | 0.72 | 2 Latium |
| 1944.1 | 52 | 46 | 1.13 | 156 Calabria |
| 1944.2 | 67 | 50 | **1.34** | 156 Calabria (Rome 4/4 ENG) |
| **1944.3** | **73** | **49** | **1.49** | 156 Calabria (Rome 2/4 ENG — losing) |
| 1944.4 | 45 | 47 | 0.96 | 156 Calabria (Rome lost) |
| 1944.6 | 70 | 81 | 0.86 | 157 Abruzzo |
| 1944.9 | 27 | 84 | 0.32 | 156 Calabria |
| 1944.12 | 19 | 40 | 0.48 | **1032 S. Sicily** |
| 1945.6 | 54 | 53 | 1.02 | 1032 S. Sicily |
| 1946.3 | 61 | 62 | 0.98 | 1032 S. Sicily |

**The advance stops at a 1.34–1.49 numerical advantage.** The Allies are not outnumbered when they stop; they stop, then go backwards. 1944.3 is simultaneously the campaign's high-water mark and the first month of retreat.

Three things a state-level read misses entirely:

- **The Axis counter-invaded Sicily and was never cleared.** From 1944.12, RIT holds provinces in both Sicilian states through 1946.3. At the final save S. Sicily physically contains ENG 15, GER 13, BUL 12, ITA 5, USA 5, RIT 5, AST 2 — a ~50-division static front on one island. The *state controller* remains ITA throughout, which is why R17 has been scoring Sicily as "never recaptured".
- **The Allied front was never continuous.** From 1943.11 to 1944.4 the Axis held 4 of 9 Calabrian provinces *while the Allies held all of Rome* — Sicily, a Naples pocket and a Rome pocket with Axis-held Calabria in between. A disconnected-beachhead front the AI never resolved. This is the expected signature of a starved theatre economy: enough divisions to hold pockets, never enough to form a line.
- **Bulgaria is a real belligerent in Italy** from 1944.6, ending with 21 divisions there.

### 3.1 Italy was stripped for Normandy — but the larger strip came first

Anglo-American strength in Italy falls **73 → 45** between 1944.3 and 1944.4 (USA 33→25, ENG 40→20) **while France still holds zero Allied divisions**. That is 28 divisions withdrawn a month before the Italian defection and two months before D-Day. The Normandy strip proper follows at 1944.6→1944.7 (Italy 70→52, France 20→60).

### 3.2 Overlord is annihilated, and Italy is then rebuilt into a cul-de-sac

Allied divisions in metropolitan France: 60 (1944.7) → 49 → **69 (1944.9)** → **0 (1944.10)**, and zero for every one of the remaining 18 months, with GER holding 23–25 there to the end. Italy is subsequently rebuilt to 44–69 Allied divisions with no effect, because those divisions are penned on Sicily and Sardinia behind an Axis lodgement. **This is F5's failure and it is larger than "the beachhead was retaken"** — a 69-division Allied presence in France was eliminated in a single month.

---

## 4. Ruled out — do NOT re-investigate

- **AIFC / schwerpunkt selection is NOT the cause. Measured and refuted 2026-08-12.** Italy *was* the Allied schwerpunkt for most of the war: USA anchored in Italian states (regions 21/23/238) for **10 consecutive months** 1943.8–1944.5; ENG for **22 of 32 saves**, including an unbroken **15-month run** 1945.1–1946.3 that is still live at the final save. `sector_age` cycles healthily 1–4 on both (note the real ceiling is `@WA_AI_AIFC_SECTOR_MAX_AGE = 4` at `WA_AI_AIFC_core.txt:47`, not the 1–5 R1 quotes). The theoretical argument that narrow fronts and mountain terrain (`WA_AI_AIFC_helpers.txt:361-368`, mountain −50) should exclude Italy is **wrong in practice** — do not rebuild it.
- **`CAPS_remote_fronts_*` is not the throttle.** All three cap blocks (`DEFAULT_FRONT_caps.txt:11-122`) sink only Africa, SE Asia, South America and Central America. Italy is in no sink area, and `home_threatened` is inert for USA/ENG in 1943–45 (`surrender_progress` ≈ 0).
- **The scripted invasions are not the problem.** R18 retired at 3/3 — Husky, Avalanche, Torch, Shingle and Iceberg all deliver their designed division counts.
- **The `fall_achse` buffer does not hold the German army in Italy.** `WA_AI_MILITARY_COUNTRY_GER_THEATRE.txt:592-627` is gated `NOT = { has_war_with = ITA }` with `abort_when_not_enabled = yes`, and Italy's defection event declares war on the Axis faction leader the next day (`events/wa_ita_events.txt:5325`, target resolved at `:5148-5153`). The buffer's window on the defection path is **one day** (flag 1944.4.13, war 1944.4.14). The 0.2 × 280 ≈ 56 ≈ the observed 55 divisions is a **coincidence of two independent ~20% claims**. R17 criterion (4) has been crediting the buffer for a front stack the buffer never supplied.

---

## 5. Why Germany's commitment is elastic and the Allies' is a fixed negative

The 10-vs-55 difference between `911bed3c` and `9a4cd657` is not a code change — `f99217c39` is an ancestor of both builds and the Italy files are byte-identical across them. It is a *consequence of fixing the Eastern Front*.

`front_unit_request` is a percent factor on a **computed front need**. In `911bed3c` Germany won the east and a continent-wide Ostfront absorbed the army. In `9a4cd657` Fix 43 worked, the Soviets pushed Germany back to a short Poland/Romania line, and a short front cannot absorb 280 divisions. The surplus flows to whichever theatre bids highest — and Italy outbids the east:

| GER pull | Value |
| --- | --- |
| `front_unit_request area = italy` (`GER_FRONT.txt:787-797`) | +200 |
| `protect_our_weak_underbelly area = italy` (`:1257-1289`) | +200 |
| `frontline_requests_6` regions 21 + 23 (`:1013-1036`) | +100 each |
| **Eastern areas (`:684-712`, `:825-851`)** | **+200, single block** |

The economy pass clamped every GER `front_unit_request` to the +200 ceiling — the east had been **1000** and Italy **450** (the `# economy: was 1000 / was 450` comments are still in the file). That clamp destroyed the ordering. Three additive Italy blocks now stack to ~+500 against the east's +200.

**Fixing the Eastern Front is what fed the Italian one.** Expect this coupling to persist: any future improvement to Soviet performance shortens the Ostfront and pushes more Wehrmacht into Italy, unless the bidding is rebalanced.

Structural asymmetries behind it:

- **Sign.** German Italian entries are +100…+200 and *increase* at the defection; Allied entries are −40 → −80 and become *more negative* at the same event.
- **Elasticity.** Germany's `put_unit_buffers` `ratio` is a fraction of the **total army** (`common/ai_strategy/documentation.info:196-203`), so its Italian commitment scales with the Wehrmacht. The Allies have **zero `put_unit_buffers` in Italy**; the only army-fraction reserve the USA owns points at the Pacific (`COUNTRY_USA_THEATRE.txt:216-338`, order 9101, `subtract_fronts_from_need = no` — a hard reserve that does not yield to front demand).
- **No Region layer exists for the Mediterranean.** The only Region-layer files in the mod are South America. Everything Italian is Faction or Country, which is why the logic is an unowned pile of additive suppressions.
- **No Allied `theatre_distribution_demand_increase` anywhere in Italy.** The only one in the Med is Alexandria +10 (`FACTION_ALLIES_THEATRE.txt:207-219`). Whole-mod inventory of that type: ids 126, 146, 447, 533, 629.
- **German buffer pools have no budget.** GER's distinct `order_id` pools sum to **1.49 × total army** (≈417 divisions demanded of 280). `WA_AI_MILITARY_ECONOMY.md` E4 lints per block (`ratio ≤ 0.25`) and never sums.

---

## 6. The RIT support stack

RIT's army itself is proportionate and is **not** the problem: a one-shot `transfer_units_fraction` from ITA (`common/decisions/GER.txt:3820-3828`, `size = 0.4 / army_ratio = 0.3`) gave it 20 divisions in one month (ITA 81→55, RIT 0→20), and it then sat **flat at 16–17 divisions for 22 months**. RIT never wins anything by itself — Rome falls to the GER+BUL mass behind it (GER 44 + BUL 14 in Italy at 1944.9). The clause has a ratio but no absolute cap, which is why `911bed3c` produced 30 from a bigger ITA.

What is disproportionate is the support stack keeping those 17 divisions advancing:

1. **`add_core_of = RIT` on every ITA core state** (`GER.txt:3784-3789`) — Rome, Latium and Sicily are permanent RIT cores, so the AI is motivated to retake them regardless of what it holds or its 0.043 war support.
2. **`puppet_ai` grants `out_of_supply_factor = -1.0`** (`common/ideas/_WA_ai.txt:113-117`, RIT listed at `:44`) — RIT divisions take *zero* out-of-supply penalty, so pushing beyond its hubs costs nothing.
3. **Uncapped repeatable German resupply** (`GER.txt:3255`, `:3404`) — 5000 infantry equipment / 3500 support / 30000 manpower per fire, `cost = 0`, no `fire_only_once`. RIT banks manpower monotonically to 750 000 while its army stays at 17.
4. **The Allies are told six times not to invade it.** `invade id = "RIT"` suppressions at `FACTION_ALLIES_INVASION.txt:383, 679, 684, 905, 910, 1292`, additive to roughly **−2500**, plus `COUNTRY_USA_FRONT.txt:142` de-prioritising the RIT front by −15. **Amphibious envelopment — the manoeuvre that historically broke the Gothic Line — is switched off.** A supply-immune rump on a peninsula that cannot be flanked from the sea can only be fought frontally up the spine of Italy.

RIT ends the war with **168 arms factories to Italy's 17**. Both sides are 100% straight-leg infantry (`wa_tlm_comp_armor` and `_comp_mech` are 0 for both at every date).

---

## 7. Ranked causes

1. **The control-inverted gate set, and the unbounded third branch of `no_italy_invasion_early`** (§1). Winning the bridgehead disarms the theatre, permanently.
2. **The opposite-sign twin reaction to the Italian defection** (§2). Confirmed by the theatre becoming British: USA 0–4 divisions vs ENG 26–36 through 1945.
3. **The RIT support stack, especially the ≈ −2500 anti-invasion suppression** (§6), which removes the only way to break a frontal stalemate on a peninsula.
4. **The German bidding asymmetry** (§5), which is now coupled to Eastern-Front success and will worsen as the SOV AI improves.

---

## 8. Open questions — verify before fixing

- **Is `target =` a valid selector for `front_unit_request`?** `documentation.info:250-266` lists only `tag / state / strategic_region / area / country_trigger / state_trigger`; `target =` is the `build_building` selector (`ENG.txt:50-55`). If it is silently dropped, then **all of Canada's European weighting** (`COUNTRY_CAN_FRONT.txt:27-66`), `ALLIES_focus_on_europe_post_france` (`FACTION_ALLIES_FRONT.txt:334-373`), `ENG_gang_up_GER_with_USA_FRONT`, `USA_gang_up_GER_with_ENG` and `ENG_war_against_ITA_3_DIPLOMACY` contribute nothing. CAN never appears in Italy in any month of `9a4cd657`, which is consistent. **Cheap to test and affects far more than Italy.**
- **Does `front_unit_request tag = GER` reach ITA/RIT-owned provinces?** `documentation.info:258` glosses `tag =` as "province of a specific country". If that reading is right, `ALLIES_europe_first`'s +150 — the Allies' single largest positive European pull — never reaches the Italian peninsula at all, while every negative is region-keyed and does.
- **Why do USA and ENG lose their entire AIFC variable block in the 1944.6 save** (five days before D-Day)? Not just the sector — every `wa_ai_aifc_*` variable is absent for both countries in that one save. ENG then has no sector for 1944.9–1944.12.
- **Why does the USA schwerpunkt leave Europe for good at 1944.7?** USA anchors Italy → Pacific (669 SW Papua, then Tinian, then Mindanao) and never returns for 21 saves. **Neither the USA nor ENG ever anchors a sector in France at any point in the campaign.** This is adjacent to the Overlord annihilation in §3.2 and may be the larger finding.

---

## 9. Cross-campaign consistency

| Campaign | Sicily | Deepest advance | Outcome |
| --- | --- | --- | --- |
| `31eaf7e6` | taken, 7 divisions | stalls on the Calabria/Campania line; Anzio beachhead **destroyed** by 1944.4 | ITA never capitulates; Italy flips only 1945.9 by another path |
| `911bed3c` | taken, 5 divisions | Anzio survives; reaches Rome **ahead of history** | ITA defects 1944.4.19 → RIT (30 div) holds **every** Italian state incl. Sicily by 1946.4 |
| `9a4cd657` | taken, 2 divisions | Rome 1944.1.27, 1.49 force ratio at peak | ITA defects 1944.4.14 → GER 55 div; RIT retakes Rome/Latium; Axis lodgement on Sicily to the end |

The Allied garrison on Sicily declines monotonically across the three campaigns (7 → 5 → 2) while the depth of the initial advance *improves*. That is the §1 mechanism getting relatively stronger as the landings get better: the faster Calabria falls, the sooner the theatre economy is switched off.

---

## 10. What shipped (2026-08-12) — causes 1, 2 and the Normandy sibling

Five files, six blocks, two new scripted triggers. **Nothing that computes "is Sicily held" was touched** — that predicate is inlined in 12 places and is also North Africa's off-switch (risk 1 below), so the fix changes what happens *after* the foothold exists, not how it is detected. The INVASION domain was left alone, honouring `2e3686fa1`'s explicit carve-out.

| # | Change | File |
| --- | --- | --- |
| P1 | Deleted the unbounded third `enable` branch from `ALLIES_no_italy_invasion_early_THEATRE`. Removes the permanent `area_priority italy -200` that armed on holding Sicily + Calabria. | `WA_AI_MILITARY_FACTION_ALLIES_THEATRE.txt` |
| P1b | Documented on the INVASION twin **why it keeps the same branch**: it is the anti-scatter rule (2b607968: 32 divisions in Sardinia/Calabria/Dodecanese plans while 13 fought on Sicily) and its payload also carries Balkan and anti-Sealion policy. | `..._FACTION_ALLIES_INVASION.txt` |
| P2 | New `ALLIES_italy_mainland_push_THEATRE` / `_FRONT` — the successor the bridge never had. Arms when the bridge disarms, mutually exclusive by construction. `area_priority italy +400 / south_italy +100`, `front_unit_request` regions 21 + 23 at +60. | `..._THEATRE.txt`, `..._FRONT.txt` |
| P3 | `ALLIES_avoid_italy_overstack{,_after_flip}`: added `allowed = is_western_allies_major` (the brakes previously reached **every** Allies member while all boosts were ENG/USA/CAN); added the principle-4 escape hatch; dropped `has_government = democratic` so a non-democratic Italian defection behaves the same. | `..._FRONT.txt` |
| P4 | Re-homed `ENG_war_against_ITA_3_FRONT` → `ALLIES_italy_cobelligerent_support_FRONT`, values unchanged. It was the only post-flip Italian positive in the mod and applied to England alone — the whole of the ENG +20 / USA −145 split. Country copy deleted, not left to stack. | `..._FRONT.txt`, `WA_AI_MILITARY_COUNTRY_ENG_FRONT.txt` |
| N1 | **Normandy sibling.** `ALLIES_dday_hold` branch 2 was the bare pair `date > 1944.12.1 AND has_war_with = JAP` — no exit, so from Dec 1944 the bloc was permanently forbidden to invade Germany or France while Japan fought on. Paired with `GER = { surrender_progress > 0.5 }`, mirroring the exit `dday_fire_FRONT` already received for the identical construct. | `..._FACTION_ALLIES_INVASION.txt` |
| T | New triggers `WA_AI_MILITARY_italy_theatre_contested` (delegates to the existing 15-state `AIR_theatre_contested_italy`, which unlike the bridge counts co-belligerents via `has_war_together_with`) and `WA_AI_MILITARY_owns_italy_mainland` (the escape hatch). | `common/scripted_triggers/WA_AI_MILITARY_triggers.txt` |

**Correction to §3.2 / the first write-up of the Normandy sibling:** `dday_hold` *does* carry `abort_when_not_enabled = yes`, so its branch 4 (Allies hold nine French states) self-releases when the ground is lost. Branch 2 is the permanent one. An earlier draft named branch 4; that was wrong.

### Validation performed
- Brace balance on all five files: **delta 0** (comments stripped).
- `tools/military_economy_audit.py`: **29 violations, none in any edited file** — all pre-existing in `COUNTRY_ENG_THEATRE.txt` (strategic-bombing blocks, explicitly exempted by the Phase 8 pass) and `GER.txt` (legacy `force_concentration`, the load-bearing CTD blocks from `d69eef2fa`).
- New triggers confirmed defined once and referenced from both consumers; no dangling references to the deleted ENG block.
- **Boot test owed** before the next campaign. No `force_concentration` block was added or deleted, so the `d69eef2fa` CTD class is not engaged, but `common/ai_strategy` is a `replace_path` folder and parse errors only surface at launch.

### Regression risks accepted (from the pre-change impact analysis)
1. **Untouched but adjacent:** the Sicily predicate is what retires ENG's North African `order_id = 1` buffer and `ENG_defense_of_el_alamein`. Not modified, so no change expected — but if African reserves behave oddly next campaign, look here first.
2. **P3 narrows the brake audience.** FRA/RAJ/SAF/NZL/AST no longer take the Italy density brake. They also never had the boosts, so this removes an asymmetry rather than creating one — but it does mean more non-major Allied divisions may flow to Italy.
3. **P2 and the bridge must stay mutually exclusive.** If a future edit changes either gate so both can be live, `area_priority italy` becomes +800 and the bridge's sizing rationale (below the +1000 husky pull) breaks.
4. **N1 changes Pacific-pivot timing.** After Dec 1944 the bloc now keeps investing in European invasions until Germany passes 0.5 surrender progress. In a campaign where Germany is winning, that delays the Pacific pivot — which is the intended trade, but it is a behaviour change beyond Italy.
5. **The German bidding coupling (§5) is untouched.** Any Soviet improvement still shortens the Ostfront and pushes more Wehrmacht into Italy. P1–P4 raise the Allied floor; they do not address the German ceiling.

### Still open after this commit
Cause 3 (the RIT support stack — supply immunity, uncapped resupply, the ≈ −2500 anti-invasion suppression) and cause 4 (German bidding asymmetry). Plus every item in §8, of which the `target =` selector question is now **answered**: `documentation.info:250-266` lists the accepted set as `tag / state / strategic_region / area / country_trigger / state_trigger`, so `target =` is invalid and Canada's entire European weighting is presumed inert. That is its own commit and affects far more than Italy.
