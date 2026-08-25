# Allied home-garrison baseline — campaign "8f9b5653" monthly saves (pre-[allied-total-commitment])

Baseline census of Allied divisions sitting in home garrison, scored against the gates of the NEW
[allied-total-commitment] system (`WA_AI_MILITARY_total_commitment_active` /
`WA_AI_MILITARY_home_theatre_threatened`, working tree 2026-08-25). These saves are the OLD build —
none of the new release blocks existed when they were played.

## Campaign identity (read before citing)

- **MEASURED** — the monthly saves (`1936.2_Feb.hoi4` … `1945.8_Aug.hoi4`) all carry
  `game_unique_id=15176ce6-ae38-4947-b0e9-46d941193986`, player `BHU` (observer), mod
  `world-ablaze-beta`, engine `1.19.2.0`. They are ONE internally consistent campaign.
- **MEASURED** — only the stray `CAN_1942_02_08_01.hoi4` carries `game_unique_id=8f9b5653-…`
  (player CAN, mod `World Ablaze BETA LOCAL`). The label "campaign 8f9b5653" therefore does not
  match the monthly set's own header GUID.
- **DERIVED** — the monthly set is nonetheless the campaign the docs call 8f9b5653: the
  §23 measurement in `documentation/WA_AI_MILITARY_SYSTEM.md` ("CAN 4–9 divisions, 100 % areadef
  home garrison in 4 of 5 saves, campaign 8f9b5653") reproduces exactly on these files
  (CAN deployed 1 / 4 / 7 / 8 / 2 at the five dates below; all-areadef-home in 1941.6, 1942.6,
  1944.6). Treated as the intended baseline per the owner's instruction.
- **ASSUMED** — "pre-[allied-total-commitment]" is the owner's statement; the deleted
  `CAN_FRONT_release_home_garrison` measurement above corroborates it but no in-save build
  fingerprint was checked.

## Method and commands

All extraction through the `wa-savegame-analysis` streaming tooling — no save was opened with
Read or plain grep. Order-class attribution reuses `plans.py`'s `scan`/`classify` (army-group
inheritance handled; the two `orders_group` traps closed).

```bash
# scripts dir: .claude/skills/wa-savegame-analysis/scripts
python savegame.py meta 1940.6_Jun.hoi4                      # (…and the other saves)
python savegame.py relations 1940.6_Jun.hoi4                  # faction tables, 5 saves
python savegame.py relations 1942.6_Jun.hoi4 --tag USA        # USA entry date
python savegame.py army ENG 1940.6_Jun.hoi4 1942.6_Jun.hoi4 1944.6_Jun.hoi4   # closure test
python savegame.py army RAJ 1940.6_Jun.hoi4 1942.6_Jun.hoi4 1944.6_Jun.hoi4
python savegame.py section 1941.6_Jun.hoi4 JAP focus --grep "strike_south"
# driver (scratchpad garrison.py): imports plans.scan/classify + savegame
#   iter_state_blocks/_state_buildings/iter_relations/iter_factions; one census JSON per save.
```

Definitions used:

| Term | Definition | Label |
| --- | --- | --- |
| Order classes | `plans.py`: front / invasion / **buffer** (type-5 order, `area_defense_settings=102` = scripted `put_unit_buffers` garrison) / **areadef** (type 5, engine-generated) / NO_ORDER / UNATTACHED (in no army) | MEASURED |
| Closure test | per-class counts sum to `army` deployed. Verified byte-equal for ENG (36/44/60) and RAJ (24/78/88) at 1940.6/1942.6/1944.6 | MEASURED |
| "Home" | division's state is a start-date core of the tag (`history/states` `add_core_of`) **or owned by the tag in that save**. Core-only under-reports India (princely states not RAJ-cored) and every colonial subject (INS, BRM, BEC); state detail below marks owned-not-cored states `+own` | DERIVED |
| "idle home" | areadef + NO_ORDER divisions on home soil (the headline bucket). UNATTACHED and buffer are tabulated separately | DERIVED |
| fit | owned `arms_factory` levels summed over states > 5 — proxy for `num_of_military_factories > 5` (`WA_AI_MILITARY_is_fit_for_expeditionary_front`); the engine counts *available* factories, which can differ slightly under occupation/trade | DERIVED |
| enemy on core | a core state whose save-side controller is at war with the tag (state-label granularity; the label can be a minority holder — see the control gotcha) | DERIVED |
| pacific threat | `WA_AI_MILITARY_pacific_threat_imminent`: JAP at war with the Allies from **1941.12.5** (MEASURED, USA war_relation) and `JAP_strike_south` completed between 1941.6 and 1942.6 (MEASURED, JAP focus list). Wargoal-in-preparation before 1941.12 not readable from a save — ASSUMED absent | mixed, per cell |

Gate walked (working tree `common/scripted_triggers/WA_AI_MILITARY_triggers.txt`):
`total_commitment_active` = is_ai ∧ minor (not ENG/FRA/USA/GER/ITA/JAP/SOV) ∧ has_war ∧
(in faction ∨ subject) ∧ fit ∧ ¬`home_theatre_threatened`; threatened = collapse metric ∨ enemy
on a core ∨ hostile home-area border ∨ (AST/NZL/RAJ ∧ pacific threat). The hostile-border term was
not walked mechanically; for the oceanic dominions (CAN/AST/NZL/SAF) no hostile land border exists
at any of these dates (DERIVED from geography + war lists). The collapse metric
(`surrender_progress`) was not read; enemy-on-core covers every case that mattered here.

## Per-country census — all five dates

All rows MEASURED (driver over `plans.py` scan; closure verified). `mil` = owned arms_factory sum
(DERIVED proxy). `idle home/abr` = areadef+NO_ORDER on own soil / elsewhere (core∪owned).
Wars column: which of GER/ITA/JAP the tag is at war with.

### 1940.6.1

| tag | dep | front | inv | buffer | areadef | NO_ORD | UNATT | idle home | idle abr | mil | war | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG | 36 | 11 | 0 | 14 | 11 | 0 | 0 | 3 | 8 | 146 | G | 8 "abroad" areadef = France (battle of France) |
| FRA | 121 | 109 | 0 | 0 | 12 | 0 | 0 | 11 | 1 | 239 | G | mid-collapse; home areadef legitimate |
| USA | 11 | 0 | 0 | 0 | 8 | 3 | 0 | 11 | 0 | 97 | — | neutral, whole army home |
| BEL | 9 | 6 | 0 | 0 | 3 | 0 | 0 | 3 | 0 | 19 | G | enemy on cores 34/790/979/985 |
| NOR | 12 | 4 | 0 | 0 | 4 | 4 | 0 | 8 | 0 | 12 | G | enemy on 6 cores (invasion running) |
| AST | 8 | 7 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 39 | G | 1 areadef in Norway |
| NZL | 6 | 5 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 10 | G | 1 areadef in France |
| CAN | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 28 | G | |
| SAF | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 11 | G | NO_ORDER in Constantine |
| RAJ | 24 | 13 | 0 | 7 | 3 | 0 | 1 | 1 | 2 | 30 | G | |
| NEP | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 1 | G | all on scripted buffer |
| BEC | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | G | Congo buffer |
| FRM | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 6 | 0 | 0 | G | Morocco areadef |
| FRN | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 5 | 0 | 1 | G | |
| INS | 14 | 0 | 0 | 0 | 14 | 0 | 0 | 14 | 0 | 0 | G | East Indies areadef (own soil) |
| HOL | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 26 | G | enemy on cores |
| ETH | 0 | | | | | | | | | 0 | — | annexed at this date |

### 1941.6.1

| tag | dep | front | inv | buffer | areadef | NO_ORD | UNATT | idle home | idle abr | mil | war | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG | 30 | 12 | 5 | 8 | 5 | 0 | 0 | 5 | 0 | 215 | G+I | |
| FRA | 10 | 0 | 1 | 1 | 8 | 0 | 0 | 8* | 0 | 177 | G+I | *exile; the 8 = owned Pacific/colonial islands |
| USA | 11 | 0 | 0 | 0 | 8 | 3 | 0 | 11 | 0 | 225 | — | neutral, unchanged since 1940 |
| AST | 7 | 5 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 62 | G+I | 1 areadef Somaliland |
| NZL | 8 | 6 | 0 | 0 | 1 | 1 | 0 | 0 | 2 | 17 | G+I | |
| CAN | 4 | 0 | 0 | 0 | 3 | 1 | 0 | 3 | 1 | 35 | G+I | 100 % of home-based army idle |
| SAF | 5 | 3 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 23 | G+I | |
| RAJ | 21 | 9 | 0 | 5 | 3 | 4 | 0 | 3 | 4 | 56 | G+I | 4 NO_ORDER stragglers in E.Africa/Norway |
| NEP | 8 | 0 | 0 | 7 | 0 | 1 | 0 | 1 | 0 | 1 | G+I | |
| BEC | 5 | 0 | 0 | 4 | 0 | 1 | 0 | 1 | 0 | 0 | G+I | |
| BRM | 6 | 0 | 0 | 0 | 5 | 1 | 0 | 6 | 0 | 2 | G+I | Burma areadef |
| INS | 14 | 0 | 0 | 0 | 13 | 1 | 0 | 14 | 0 | 0 | G+I | |
| ETH | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 4 | G+I | restored; 1 unattached |
| BEL/HOL | 0 | | | | | | | | | | | armies destroyed |

### 1942.6.1 (Japan in the war since 1941.12.5)

| tag | dep | front | inv | buffer | areadef | NO_ORD | UNATT | idle home | idle abr | mil | war | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG | 44 | 13 | 0 | 16 | 15 | 0 | 0 | 13 | 2 | 265 | G+I+J | 12 areadef in UK cores + Malta |
| USA | 12 | 0 | 0 | 10 | 2 | 0 | 0 | 1 | 1 | 502 | G+I+J | buffers incl. 6 in UK/Pacific staging |
| FRA | 9 | 0 | 0 | 0 | 9 | 0 | 0 | 7* | 2 | 177 | G+I+J | *owned islands (Tahiti, N.Caledonia…) |
| AST | 10 | 0 | 0 | 0 | 10 | 0 | 0 | 9 | 1 | 81 | G+I+J | all-areadef army, 8 states of Australia |
| NZL | 9 | 0 | 0 | 0 | 9 | 0 | 0 | 8 | 1 | 22 | G+I+J | all-areadef army |
| RAJ | 78 | 24 | 0 | 47 | 7 | 0 | 0 | 7 | 0 | 90 | G+I+J | 44 buffer on Indian soil (Bengal wall) |
| CAN | 7 | 0 | 0 | 0 | 7 | 0 | 0 | 7 | 0 | 68 | G+I+J | **100 % areadef home** |
| SAF | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 4 | 1 | 32 | G+I+J | |
| ARG | 11 | 1 | 3 | 0 | 7 | 0 | 0 | 7 | 0 | 18 | G+I+J | Allies member since ~1942 |
| MEX | 17 | 0 | 2 | 0 | 13 | 2 | 0 | 14 | 1 | 14 | G+I+J | |
| CHL | 6 | 0 | 1 | 0 | 5 | 0 | 0 | 5 | 0 | 2 | G+I+J | unfit |
| ETH | 4 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | 0 | 4 | G+I+J | |
| NEP | 6 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 1 | G+I+J | |
| BEC | 5 | 0 | 0 | 4 | 0 | 1 | 0 | 1 | 0 | 0 | G+I+J | |
| HOL | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 | G+I+J | 2 unattached abroad |
| INS | — | | | | | | | | | | | gone (Japanese conquest) |

### 1943.6.1

| tag | dep | front | inv | buffer | areadef | NO_ORD | UNATT | idle home | idle abr | mil | war | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG | 63 | 41 | 0 | 14 | 8 | 0 | 0 | 8 | 0 | 304 | G+I+J | army mostly on fronts now |
| USA | 24 | 6 | 0 | 16 | 1 | 0 | 1 | 0 | 1 | 822 | G+I+J | 12 buffer staging abroad |
| FRA | 6 | 5 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 178 | G+I+J | |
| AST | 9 | 0 | 0 | 0 | 9 | 0 | 0 | 5 | 4 | 94 | G+I+J | 2 in Somaliland, 2 unmapped |
| NZL | 7 | 2 | 0 | 0 | 5 | 0 | 0 | 3 | 2 | 29 | G+I+J | |
| RAJ | 75 | 28 | 0 | 41 | 6 | 0 | 0 | 3 | 3 | 117 | G+I+J | enemy on core 430 (East Bengal, JAP) |
| CAN | 8 | 7 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 83 | G+I+J | fronts (best CAN date) |
| SAF | 5 | 1 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 37 | G+I+J | |
| ARG | 13 | 5 | 1 | 0 | 7 | 0 | 0 | 7 | 0 | 19 | G+I+J | |
| MEX | 6 | 4 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | 16 | G+I+J | |
| CHL | 9 | 1 | 1 | 0 | 7 | 0 | 0 | 7 | 0 | 3 | G+I+J | unfit |
| ETH | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 7 | G+I+J | fit but 100 % unattached |
| NEP | 12 | 2 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 1 | G+I+J | |
| BEC | 5 | 0 | 0 | 4 | 0 | 1 | 0 | 1 | 0 | 0 | G+I+J | |
| HOL | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 | G+I+J | |

### 1944.6.1

| tag | dep | front | inv | buffer | areadef | NO_ORD | UNATT | idle home | idle abr | mil | war | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ENG | 60 | 31 | 2 | 17 | 10 | 0 | 0 | 9 | 1 | 326 | G+I+J | 8 UK areadef + Malta |
| USA | 54 | 10 | 9 | 22 | 10 | 3 | 0 | 10 | 3 | 959 | G+I+J | 10 areadef back in CONUS at D-Day+ |
| FRA | 8 | 5 | 0 | 0 | 3 | 0 | 0 | 3* | 0 | 180 | G+I+J | *owned islands |
| AST | 21 | 0 | 0 | 1 | 18 | 0 | 2 | 16 | 2 | 97 | G+I+J | 15 areadef across Australia |
| NZL | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 3 | 3 | 30 | G+I+J | |
| RAJ | 88 | 20 | 0 | 60 | 8 | 0 | 0 | 8 | 0 | 125 | G+I+J | 56 buffer on Indian soil; enemy still on 430 |
| CAN | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 2 | 0 | 93 | G+I+J | army shrank to 2, both areadef home |
| SAF | 5 | 1 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 41 | G+I+J | |
| ARG | 19 | 9 | 1 | 0 | 9 | 0 | 0 | 8 | 1 | 19 | G+I+J | 1 areadef in… Rajahsthan (India) |
| MEX | 6 | 2 | 1 | 0 | 3 | 0 | 0 | 3 | 0 | 26 | G+I+J | |
| CHL | 12 | 3 | 1 | 0 | 8 | 0 | 0 | 8 | 0 | 5 | G+I+J | unfit (5 mil, bar is >5) |
| ETH | 4 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 7 | G+I+J | still 100 % unattached |
| NEP | 12 | 7 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 1 | G+I+J | |
| BEC | 5 | 0 | 0 | 4 | 0 | 1 | 0 | 1 | 0 | 0 | G+I+J | |
| HOL | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 | G+I+J | |

State-level detail (which UK/US/Australian/Indian states the idle divisions sit in) is in the
driver JSON (`scratchpad gall2.json`, `detail` field); the notable ones are quoted in the anomaly
list below.

## Verdict per country-date against the NEW gates

Verdict = what `WA_AI_MILITARY_total_commitment_active` would do to this country at this date.
Term named where the gate closes. All verdicts DERIVED from the MEASURED inputs above.

| tag | 1940.6 | 1941.6 | 1942.6 | 1943.6 | 1944.6 |
| --- | --- | --- | --- | --- | --- |
| CAN | RELEASED (0 idle) | **RELEASED (3)** | **RELEASED (7)** | RELEASED (0) | RELEASED (2) |
| SAF | RELEASED (0) | RELEASED (1) | **RELEASED (4)** | **RELEASED (4)** | **RELEASED (4)** |
| AST | RELEASED (0) | RELEASED (0) | KEPT pacific (9) | KEPT pacific (5) | KEPT pacific (16) |
| NZL | RELEASED (0) | RELEASED (0) | KEPT pacific (8) | KEPT pacific (3) | KEPT pacific (3) |
| RAJ | RELEASED (1) | **RELEASED (3)** | KEPT pacific (7) | KEPT pacific + enemy-on-core 430 (3) | KEPT pacific + enemy-on-core (8) |
| ARG | — (not yet Allied) | — | **RELEASED (7)** | **RELEASED (7)** | **RELEASED (8)** |
| MEX | — | — | **RELEASED (14)** | RELEASED (2) | RELEASED (3) |
| CHL | — | — | KEPT unfit (5) | KEPT unfit (7) | KEPT unfit (8) |
| NEP | KEPT unfit (0) | KEPT unfit (1) | KEPT unfit (0) | KEPT unfit (0) | KEPT unfit (0) |
| BEC | KEPT unfit (0) | KEPT unfit (1) | KEPT unfit (1) | KEPT unfit (1) | KEPT unfit (1) |
| INS | KEPT unfit (14) | KEPT unfit (14) | — conquered | — | — |
| BRM | — | KEPT unfit (6) | — (absorbed) | — | — |
| FRM/FRN | KEPT unfit (11) | — | — | — | — |
| BEL | KEPT enemy-on-core (3) | army dead | — | — | — |
| NOR | KEPT enemy-on-core (8) | annexed | — | — | — |
| HOL | KEPT enemy-on-core (0) | (0) | (0; 2 unattached) | (0) | (0) |
| ETH | — | KEPT unfit (0) | KEPT unfit (0) | fit, but 4/4 UNATTACHED — beyond the levers | same |
| ENG | NOT COVERED (3) | NOT COVERED (5) | NOT COVERED (13) | NOT COVERED (8) | NOT COVERED (9) |
| USA | NOT COVERED (11; neutral) | NOT COVERED (11; neutral) | NOT COVERED (1) | NOT COVERED (0) | NOT COVERED (10) |
| FRA | NOT COVERED (11) | NOT COVERED (8*) | NOT COVERED (7*) | NOT COVERED (1) | NOT COVERED (3*) |

Notes: USA 1940/41 is neutral (no war), so even a minor in its position would fail `has_war` — the
NOT COVERED label is about the majors exclusion, which is what remains once it is in the war.
FRA* = owned colonial islands, not the metropole (occupied from 1940.7 on).

## Headline — home areadef+NO_ORDER divisions per date

DERIVED from the tables above. (a) = would-be-released by the new gate; (b) = kept home by a
designed term (named); (c) = majors, out of the system's scope.

| date | (a) released | (b) by design | (c) majors | total home-idle |
| --- | --- | --- | --- | --- |
| 1940.6 | 1 (RAJ 1) | 36 = enemy-on-core 11 (BEL 3, NOR 8) + unfit 25 (INS 14, FRM 6, FRN 5) | 25 (ENG 3, FRA 11, USA 11) | 62 |
| 1941.6 | 7 (CAN 3, RAJ 3, SAF 1) | 22 = unfit (BRM 6, INS 14, NEP 1, BEC 1) | 24 (ENG 5, FRA 8*, USA 11) | 53 |
| 1942.6 | **32 (MEX 14, CAN 7, ARG 7, SAF 4)** | 30 = pacific 24 (AST 9, NZL 8, RAJ 7) + unfit 6 (CHL 5, BEC 1) | 21 (ENG 13, FRA 7*, USA 1) | 83 |
| 1943.6 | 13 (ARG 7, SAF 4, MEX 2) | 19 = pacific 11 (AST 5, NZL 3, RAJ 3) + unfit 8 (CHL 7, BEC 1) | 9 (ENG 8, FRA 1) | 41 |
| 1944.6 | 17 (ARG 8, SAF 4, MEX 3, CAN 2) | 36 = pacific 27 (AST 16, NZL 3, RAJ 8) + unfit 9 (CHL 8, BEC 1) | 22 (ENG 9, USA 10, FRA 3*) | 75 |

Additional buckets the headline does not count:

- **UNATTACHED** (in no army — beyond every ai_strategy lever, §23 known limit): ETH 4 from
  1943.6 on (fit, 100 % of its army), HOL 2 from 1942.6 on, AST 2 and USA 1 once each.
- **buffer** (scripted `put_unit_buffers` garrisons — designed placement, not idleness): RAJ's
  Bengal/South-India wall grows 44 → 41 → 56 (1942.6 → 1944.6) on Indian soil facing Japan;
  ENG keeps 4-5 in UK south-coast states through the whole war plus Gibraltar/Malta/Aden;
  NEP holds 5-10 in Nepal; USA's 10-22 buffers are mostly staging in the UK and Pacific atolls.

## Anomalies worth a line

1. **MEASURED — CAN 1942.6: 7/7 divisions areadef at home** (Quebec, BC, Nova Scotia…), fit at 68
   mil factories, no reachable enemy. The cleanest single justification for the new system; already
   quoted in §23. By 1944.6 Canada's army has shrunk to 2 divisions — both still areadef home.
2. **MEASURED — MEX 1942.6: 14 of 17 home**, fit — the largest single would-be-release of any date.
   Mexico then does move (4 front by 1943.6); the release would have moved it a year earlier.
3. **MEASURED — ARG holds 7-8 areadef in Pampas/Patagonia at every date from 1942.6**, fit, never
   threatened — a steady, releasable 7-8 divisions nobody has looked at. Bonus: 1 Argentine
   areadef division in Rajahsthan, India at 1944.6 (order class areadef, far abroad).
4. **MEASURED — AST 1944.6: 18 of 21 divisions areadef, 15-16 spread across Australia** while the
   Pacific front has moved to New Guinea and beyond. KEPT by the pacific term as designed — but the
   design keeps ~85 % of the Australian army home for as long as Japan exists. If that reads as too
   blunt later, the lever is `pacific_threat_imminent`, not the gate.
5. **MEASURED — ENG keeps 8-13 areadef in UK cores at every date** (plus 4-5 south-coast buffers):
   ~40 % of the army in 1942.6 (18 of 44 in the UK), still 13 of 60 at 1944.6. This is the (c)
   bucket's core: the next design question is ENG's home garrison, ~10 divisions deep through the
   whole war.
6. **MEASURED — USA 1944.6: 10 areadef + 3 NO_ORDER back in CONUS** (Texas, Florida, Arizona…) out
   of only 54 deployed divisions, in D-Day month. Also: the USA fields 54 divisions on 959 military
   factories — the army-size anomaly dwarfs the garrison anomaly.
7. **MEASURED — ETH is fit from 1943.6 (7 mil factories) but its whole 4-division army is
   UNATTACHED** — in no army, reachable by no order, released by nothing. A release system predicated
   on areadef orders never touches it.
8. **MEASURED — Japan stands on RAJ core 430 (East Bengal) at 1943.6 and 1944.6** — the
   enemy-on-core term would be live for RAJ even without the pacific term; RAJ's 41-60 scripted
   buffers on Indian soil are the (pre-existing) intended response.
9. **DERIVED — the fitness bar cuts exactly where intended**: CHL sits at 5 owned mil factories at
   1944.6 against the `> 5` bar — one factory short of releasing 8 divisions. NEP/BEC/INS/BRM
   (0-2 mil) all fail it; their garrisons are colonial-soil areadefs and Congo/Nepal buffers.
10. **MEASURED — the campaign-id mismatch**: monthly saves say `15176ce6`, only the stray CAN save
    says `8f9b5653`. Anyone re-deriving this baseline must select by the monthly filenames, not by
    GUID.
