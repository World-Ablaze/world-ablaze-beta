# Q-N2 / Q-N3 naval measurement (2026-09-25)

## Sources
- **MEASURED** campaign `73c03fd3` (cloud BHU observer run, mod checksum 64aa, engine v1.19.3.0): 111 monthly saves `1936.2_Feb.hoi4` .. `1945.4_Apr.hoi4`, one timeline.
- **MEASURED** campaign `e953ae9b` (local, player SWE = non-major, checksum 0ff9): 98 monthly saves `autosave_128.hoi4` (1936.2) .. `autosave_31.hoi4` (1944.3). Stopped at 1944.3: from 1944.4 the player tag-switched to GER/USA/SOV/FRA and the campaign branches (duplicate dates) - those saves are excluded.
- Third campaign `02795c2d` NOT used: GER is player-controlled throughout (GER navy not AI).
- Extractor: scratchpad `navx.py` (ship `definition=` at ship depth 1 only, per the skill gotcha; raw mission id kept; wars = every `war_relation` in every country's `active_relations`, both sides). Analysis: `nava.py`. Per-save JSON under `navjson/`.

## Mission id labels
| id | label | evidence |
|---|---|---|
| 0 | none/hold | DERIVED: savegame.py `_NAVAL_MISSIONS` says "none"; its note "only a neutral shows it" is stale - here 9 313 TF-obs, mostly at-war majors |
| 1 | patrol | DERIVED (tool map) |
| 2 | strike force | DERIVED (tool map); every id-2 TF measured here is StrikeForce_1-shaped |
| 3 | convoy raid | DERIVED (tool map) |
| 4 | convoy escort | DERIVED (tool map) |
| 5 | mine (planting?) | DERIVED (tool map says 5/6 = mines, order unknown) |
| 7 | training | DERIVED (tool map) |
| 8 | reserve (fleet "Reserve fleet", no region) | DERIVED (tool map) |
| 9 | naval invasion support | DERIVED: not in the tool map; all 136 id-9 TF-obs satisfy NavalInvasionSupport_1 min (>=1 CA + >=4 CL) |

"Idle" below = 0 + 8 (+7 training listed apart).

## Strength weights (Q-N3)
(a) weighted: CV / BB / BC = 10, CA = 5, CVL = 5 (my choice, not in the brief), CL = 3, DD = 1, FF = 1 (my choice), SS = 1, SSC (cruiser_submarine) = 1 (my choice).
(b) plain hull count. Only ships in fleets are counted (no ships under construction). Enemies = every country with a war_relation to the tag at that save (subjects, exiles, minors included).
Posture: superior ratio < 0.8, inferior > 1.5, else neutral. Ratio = inf when own strength = 0. **ASSUMED**: the engine's `enemies_naval_strength_ratio` uses a different formula; this is an approximation only.
Flap = posture changes and returns to the previous value within the next 3 monthly saves.

# Campaign 73c03fd3: 111 saves 1936.2.1.2 .. 1945.4.1.2

## Q-N2a. Every task force with mission=2 (strike), all countries, all saves

| date | tag | fleet | TF ships | TF meets 2CV+2BB+10CL | country total CV/BB/CL | country meets |
|---|---|---|---|---|---|---|
| 1937.9.1 | JAP | Empire of Japan Fleet 2 | CV3 BB6 CA10 CL20 DD30 | True | 3/6/20 | True |
| 1937.10.1 | JAP | Empire of Japan Fleet 2 | CV3 BB6 CA10 CL20 DD30 | True | 3/6/20 | True |
| 1937.11.1 | JAP | Empire of Japan Fleet 2 | CV3 BB6 CA10 CL20 DD30 | True | 3/6/20 | True |
| 1939.11.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 6/7/23 | True |
| 1939.12.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/23 | True |
| 1940.1.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/24 | True |
| 1940.2.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/24 | True |
| 1940.3.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/24 | True |
| 1940.4.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/24 | True |
| 1940.5.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/25 | True |
| 1940.6.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/25 | True |
| 1940.7.1 | ENG | United Kingdom Fleet 12 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/42 | True |
| 1940.7.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/25 | True |
| 1940.8.1 | ENG | United Kingdom Fleet 12 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/43 | True |
| 1940.8.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/25 | True |
| 1940.9.1 | ENG | United Kingdom Fleet 12 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/44 | True |
| 1940.9.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/26 | True |
| 1940.10.1 | ENG | United Kingdom Fleet 12 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/44 | True |
| 1940.10.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/26 | True |
| 1940.11.1 | ENG | United Kingdom Fleet 12 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/44 | True |
| 1940.11.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/26 | True |
| 1940.12.1 | ENG | United Kingdom Fleet 12 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/46 | True |
| 1940.12.1 | JAP | Empire of Japan Fleet 4 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/27 | True |
| 1941.1.1 | ENG | United Kingdom Fleet 12 | CV3 BB8 CA10 CL19 DD30 | True | 7/17/46 | True |
| 1941.3.1 | ENG | United Kingdom Fleet 12 | CV4 BB8 CA9 CL19 DD30 | True | 7/17/45 | True |
| 1941.4.1 | ENG | United Kingdom Fleet 12 | CV2 BB8 CA9 CL19 DD30 | True | 7/17/46 | True |
| 1941.5.1 | ENG | United Kingdom Fleet 12 | CV2 BB8 CA9 CL19 DD30 | True | 7/17/46 | True |
| 1941.8.1 | ENG | United Kingdom Fleet 12 | CV2 BB8 CA9 CL19 DD30 | True | 7/17/48 | True |
| 1941.9.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 7/17/48 | True |
| 1942.1.1 | USA | USS Navy Group 12 | CV4 BB8 CA10 CL20 DD30 | True | 7/21/32 | True |
| 1942.2.1 | ENG | United Kingdom Fleet 5 | CV2 BB7 CA9 CL19 DD30 | True | 7/17/50 | True |
| 1942.2.1 | JAP | Empire of Japan Fleet 7 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/32 | True |
| 1942.2.1 | USA | USS Navy Group 12 | CV4 BB8 CA10 CL20 DD30 | True | 7/21/34 | True |
| 1942.3.1 | ENG | United Kingdom Fleet 10 | CV2 BB7 CA9 CL19 DD30 | True | 7/17/51 | True |
| 1942.3.1 | JAP | Empire of Japan Fleet 12 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/32 | True |
| 1942.3.1 | USA | USS Navy Group 9 | CV4 BB8 CA10 CL20 DD30 | True | 7/22/35 | True |
| 1942.4.1 | ENG | United Kingdom Fleet 10 | CV2 BB7 CA9 CL19 DD30 | True | 7/17/51 | True |
| 1942.5.1 | JAP | Empire of Japan Fleet 5 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/33 | True |
| 1942.6.1 | JAP | Empire of Japan Fleet 7 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/33 | True |
| 1942.8.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA9 CL19 DD30 | True | 7/17/53 | True |
| 1942.8.1 | JAP | Empire of Japan Fleet 5 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/34 | True |
| 1942.8.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 7/22/38 | True |
| 1942.9.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA9 CL19 DD30 | True | 7/17/53 | True |
| 1942.9.1 | JAP | Empire of Japan Fleet 5 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/34 | True |
| 1942.9.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 7/23/39 | True |
| 1942.10.1 | ENG | United Kingdom Fleet 9 | CV2 BB7 CA9 CL19 DD30 | True | 7/17/54 | True |
| 1942.11.1 | ENG | United Kingdom Fleet 14 | CV2 BB7 CA9 CL19 DD30 | True | 9/17/54 | True |
| 1942.11.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA9 CL20 DD30 | True | 9/7/35 | True |
| 1942.11.1 | USA | USS Navy Group 12 | CV4 BB8 CA10 CL20 DD30 | True | 8/23/41 | True |
| 1943.5.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA9 CL19 DD30 | True | 10/17/58 | True |
| 1943.5.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 11/24/45 | True |
| 1943.6.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 10/17/59 | True |
| 1943.6.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 11/24/45 | True |
| 1943.7.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 11/24/45 | True |
| 1943.8.1 | USA | USS Navy Group 5 | CV4 BB8 CA9 CL20 DD30 | True | 11/24/46 | True |
| 1943.9.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 10/17/61 | True |
| 1943.9.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 13/24/47 | True |
| 1943.10.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 10/17/61 | True |
| 1943.10.1 | USA | USS Navy Group 5 | CV4 BB8 CA8 CL20 DD30 | True | 13/24/48 | True |
| 1943.11.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 10/17/62 | True |
| 1943.11.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 14/24/49 | True |
| 1943.12.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 10/17/62 | True |
| 1943.12.1 | JAP | Empire of Japan Fleet 4 | CV4 BB8 CA10 CL20 DD30 | True | 10/8/41 | True |
| 1943.12.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 14/24/49 | True |
| 1944.1.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 10/17/63 | True |
| 1944.1.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 14/25/50 | True |
| 1944.3.1 | ENG | United Kingdom Fleet 18 | CV2 BB7 CA7 CL19 DD30 | True | 10/17/68 | True |
| 1944.3.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 18/26/52 | True |
| 1944.4.1 | ENG | United Kingdom Fleet 14 | CV2 BB7 CA7 CL19 DD30 | True | 10/18/69 | True |
| 1944.4.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 18/26/52 | True |
| 1944.5.1 | ENG | United Kingdom Fleet 14 | CV2 BB7 CA7 CL19 DD30 | True | 10/18/70 | True |
| 1944.5.1 | JAP | Empire of Japan Fleet 4 | CV4 BB6 CA10 CL20 DD30 | True | 10/8/42 | True |
| 1944.5.1 | USA | USS Navy Group 5 | CV4 BB8 CA10 CL20 DD30 | True | 19/26/53 | True |
| 1944.6.1 | JAP | Empire of Japan Fleet 4 | CV4 BB6 CA10 CL20 DD30 | True | 10/8/43 | True |
| 1944.8.1 | ENG | United Kingdom Fleet 12 | CV2 BB7 CA7 CL19 DD30 | True | 10/18/68 | True |
| 1944.8.1 | USA | USS Navy Group 5 | CV4 BB6 CA9 CL20 DD30 | True | 20/25/55 | True |
| 1944.9.1 | ENG | United Kingdom Fleet 11 | CV2 BB7 CA7 CL19 DD30 | True | 10/18/68 | True |
| 1944.9.1 | USA | USS Navy Group 5 | CV4 BB6 CA9 CL20 DD30 | True | 21/25/56 | True |
| 1944.10.1 | ENG | United Kingdom Fleet 5 | CV2 BB7 CA7 CL19 DD30 | True | 10/18/68 | True |
| 1944.10.1 | USA | USS Navy Group 5 | CV4 BB6 CA9 CL20 DD30 | True | 21/25/57 | True |
| 1944.11.1 | ENG | United Kingdom Fleet 6 | CV2 BB7 CA7 CL19 DD30 | True | 10/18/69 | True |
| 1944.11.1 | JAP | Empire of Japan Fleet 2 | CV4 BB6 CA10 CL20 DD30 | True | 10/8/45 | True |
| 1944.11.1 | USA | USS Navy Group 5 | CV4 BB6 CA9 CL20 DD30 | True | 21/25/58 | True |
| 1944.12.1 | USA | USS Navy Group 5 | CV4 BB6 CA9 CL20 DD30 | True | 22/25/58 | True |
| 1945.3.1 | JAP | Empire of Japan Fleet 6 | CV4 BB6 CA10 CL20 DD30 | True | 10/8/47 | True |
| 1945.4.1 | JAP | Empire of Japan Fleet 4 | CV4 BB6 CA10 CL20 DD30 | True | 10/8/47 | True |
| 1945.4.1 | USA | USS Navy Group 5 | CV4 BB6 CA9 CL20 DD30 | True | 23/26/62 | True |
| 1945.4.1 | USA | USS Navy Group 9 | CV4 BB8 CA10 CL20 DD30 | True | 23/26/62 | True |

Total strike-TF observations: 88

Mission-id census (TF observations over all saves, all countries): 0=9313, 1=3337, 2=88, 3=2201, 4=780, 5=33, 7=2307, 8=6425, 9=87

## Q-N2c. Task forces that satisfy StrikeForce_1 min (>=2CV,>=2BB,>=10CL), by mission (TF-observations; distinct tag list)

- none/hold: 221 TF-obs, tags ['ENG', 'JAP', 'USA']
- strike: 88 TF-obs, tags ['ENG', 'JAP', 'USA']
- reserve: 61 TF-obs, tags ['ENG', 'USA']
- train: 31 TF-obs, tags ['ENG', 'JAP', 'USA']
- fleet-region split: none/hold/fleet has regions=5, none/hold/fleet no regions=216, reserve/fleet no regions=61, strike/fleet has regions=88, train/fleet has regions=31
- first save per (tag, mission): ENG:none/hold@1936.9.1, ENG:reserve@1940.9.1, ENG:strike@1940.7.1, ENG:train@1936.2.1, JAP:none/hold@1936.5.1, JAP:strike@1937.9.1, JAP:train@1936.2.1, USA:none/hold@1936.3.1, USA:reserve@1943.1.1, USA:strike@1942.1.1, USA:train@1936.5.1

Mission x fleet-has-strategic_region (TF obs): escort/noreg=5, escort/reg=775, inv-support?/reg=87, mine5/reg=33, none/hold/noreg=8232, none/hold/reg=1081, patrol/reg=3337, raid/noreg=20, raid/reg=2181, reserve/noreg=6425, strike/reg=88, train/reg=2307

## Q-N2b. Majors at the sampled dates

### 1939.9.1.2 (1939.9_Sep.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SS26 SSC43 FF12 DD16 (n=113) | False | 0 | 50 | 50 | 13 | none/hold:4, reserve:1, train:5 |
| ITA | BB6 CA9 CL17 FF56 DD88 SSC13 SS55 (n=244) | False | 0 | 156 | 40 | 48 | none/hold:11, reserve:4, train:2 |
| JAP | BC4 CV6 BB7 CVL2 CA21 CL23 FF32 DD133 SS53 SSC8 (n=289) | True | 100 | 158 | 0 | 31 | none/hold:9, patrol:5, reserve:3 |
| ENG | BB14 BC3 CV6 CVL1 CA16 CL41 DD271 SSC21 FF114 SS35 (n=522) | True | 0 | 300 | 133 | 89 | none/hold:14, reserve:2, train:9 |
| FRA | CV1 BB5 BC2 CA7 CL12 SSC40 DD50 FF64 SS41 (n=222) | False | 0 | 121 | 70 | 31 | none/hold:9, reserve:3, train:5 |
| USA | BB16 CV6 CA18 CL19 SSC3 SS81 DD300 (n=443) | True | 0 | 341 | 50 | 52 | none/hold:22, reserve:3, train:4 |
| SOV | BB3 CA2 CL5 SS91 FF18 SSC35 DD23 (n=177) | False | 0 | 135 | 30 | 12 | none/hold:12, reserve:4, train:3 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: none/hold [CA4 CL8] x1; none/hold [DD16] x1; none/hold [FF12] x1; none/hold [SS10] x1; reserve [BB2 CA2 SS6 SSC3] x1; train [SS10] x1; train [SSC10] x4
- **ITA**: none/hold [CA4 CL12] x1; none/hold [DD20] x3; none/hold [FF20] x1; none/hold [SS10] x5; none/hold [SSC10] x1; reserve [BB6 CA4 CL5 FF15 DD8 SSC3 SS4] x1; reserve [CA1] x1; reserve [FF1] x1; reserve [SS1] x1; train [DD20] x1; train [FF20] x1
- **JAP**: none/hold [BC2 CA6] x1; none/hold [CV4 BB7 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x1; none/hold [SS10] x5; none/hold [SSC8] x1; patrol [DD20] x5; reserve [BC1] x1; reserve [CV2 BC1 CA2 CL3 FF12 DD3 SS3] x1; reserve [CVL1 CA3] x1
- **ENG**: none/hold [BC2 CA6] x1; none/hold [CV4 BB8 CA10 CL20 DD30] x1; none/hold [DD20] x7; none/hold [FF20] x3; none/hold [SS10] x1; none/hold [SSC10] x1; reserve [BB4 BC1 CL15 DD1 SSC1] x1; reserve [CV2 BB2 CL6 DD40 FF12 SS5] x1; train [CVL1 FF20] x1; train [DD20] x3; train [FF2] x1; train [FF20] x1; train [SS10] x2; train [SSC10] x1
- **FRA**: none/hold [BC2 CA6] x1; none/hold [CA1 CL12] x1; none/hold [DD20] x2; none/hold [FF20] x1; none/hold [SS10] x2; none/hold [SSC10] x2; reserve [BB2 DD10 FF4 SSC2 SS1] x1; reserve [BB3] x1; reserve [CV1 SSC8] x1; train [FF20] x2; train [SS10] x2; train [SSC10] x1
- **USA**: none/hold [CV4 BB8 CA10 CL19 DD30] x1; none/hold [DD10] x8; none/hold [DD20] x6; none/hold [SS10] x7; reserve [BB8 CA6 SSC3 SS3] x1; reserve [CV2 CA2 DD20 SS1] x1; reserve [SS7] x1; train [DD10] x3; train [DD20] x1
- **SOV**: none/hold [CA2 CL5] x1; none/hold [DD20] x1; none/hold [FF18] x1; none/hold [SS10] x6; none/hold [SSC10] x3; reserve [BB1] x1; reserve [BB2] x1; reserve [DD3 SSC5] x1; reserve [SS1] x1; train [SS10] x3

### 1941.6.1.2 (1941.6_Jun.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SS12 SSC58 DD16 FF12 (n=114) | False | 98 | 12 | 0 | 4 | escort:1, none/hold:1, patrol:1, raid:8, reserve:1 |
| ITA | BB8 CA9 CL21 SSC13 DD82 SS35 FF36 (n=204) | False | 143 | 36 | 0 | 25 | escort:1, none/hold:2, patrol:5, raid:5, reserve:2 |
| JAP | CV8 BC4 BB7 CA21 CVL2 CL29 FF58 DD160 SS56 SSC8 (n=353) | True | 120 | 194 | 0 | 39 | none/hold:11, patrol:6, reserve:2 |
| ENG | BB17 BC3 CV7 CA15 CL47 DD323 SS12 FF115 SSC8 (n=547) | True | 340 | 69 | 0 | 138 | escort:6, none/hold:2, patrol:10, raid:3, reserve:4 |
| FRA | CV1 BB3 FF3 DD3 SS2 SSC4 (n=16) | False | 0 | 0 | 0 | 16 | reserve:1 |
| USA | BB18 CV7 CA18 CL28 SSC3 SS86 DD349 (n=509) | True | 140 | 334 | 0 | 35 | none/hold:25, patrol:7, reserve:2 |
| SOV | BB3 CA3 CL5 SS91 SSC47 FF18 DD23 (n=190) | False | 20 | 156 | 0 | 14 | none/hold:15, patrol:1, reserve:4 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: escort [FF12] x1; none/hold [CA4 CL8] x1; patrol [DD16] x1; raid [SS6] x2; raid [SSC10] x4; raid [SSC9] x2; reserve [BB2 CA2] x1
- **ITA**: escort [FF16] x1; none/hold [CA4 CL12] x1; none/hold [FF20] x1; patrol [DD12] x1; patrol [DD14] x1; patrol [DD16] x1; patrol [DD20] x2; raid [SS10] x1; raid [SS8] x2; raid [SS9] x1; raid [SSC10] x1; reserve [BB8 CA4 CL9 SSC3] x1; reserve [CA1] x1
- **JAP**: none/hold [BC2 CA4 CL9] x1; none/hold [BC2 CA6] x1; none/hold [CV4 BB7 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x2; none/hold [SS10] x5; none/hold [SSC8] x1; patrol [DD20] x6; reserve [CA1] x1; reserve [CV4 FF18 DD10 SS6] x1
- **ENG**: escort [FF18] x3; escort [FF20] x3; none/hold [CV2 BB8 CA9 CL19 DD30] x1; none/hold [FF1] x1; patrol [DD20] x10; raid [BC2 CA6] x1; raid [SS10] x1; raid [SSC8] x1; reserve [BB4 BC1 CL13] x1; reserve [CV2] x1; reserve [CV3 BB5 CL15 DD50 SS2] x1; reserve [DD43] x1
- **FRA**: reserve [CV1 BB3 FF3 DD3 SS2 SSC4] x1
- **USA**: none/hold [CA4 CL8] x1; none/hold [CV4 BB8 CA10 CL20 DD30] x1; none/hold [DD10] x11; none/hold [DD20] x3; none/hold [SS1] x1; none/hold [SS10] x7; none/hold [SS9] x1; patrol [DD20] x7; reserve [BB8 CA2 SSC3 SS5] x1; reserve [CV3 BB2 CA2 DD9 SS1] x1
- **SOV**: none/hold [CA3 CL5] x1; none/hold [FF18] x1; none/hold [SS10] x9; none/hold [SSC10] x4; patrol [DD20] x1; reserve [BB1 SSC2] x1; reserve [BB2] x1; reserve [DD3 SSC5] x1; reserve [SS1] x1

### 1942.6.1.2 (1942.6_Jun.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SSC33 SS7 DD16 FF11 (n=83) | False | 75 | 1 | 0 | 7 | escort:1, inv-support?:1, none/hold:1, patrol:1, raid:4, reserve:2 |
| ITA | BB9 CA10 CL24 DD37 SS26 SSC9 FF34 (n=149) | False | 49 | 50 | 0 | 50 | none/hold:3, patrol:1, raid:3, reserve:2 |
| JAP | CV9 BC4 BB7 CA21 CVL2 CL33 FF74 DD176 SS58 SSC8 (n=392) | True | 277 | 80 | 0 | 35 | none/hold:4, patrol:7, raid:7, reserve:2, strike:1 |
| ENG | BB17 CV7 BC3 CA10 CVL1 CL52 DD347 FF143 SSC8 SS7 (n=595) | True | 315 | 124 | 0 | 156 | escort:5, none/hold:4, patrol:10, raid:2, reserve:4 |
| FRA | CV1 BB3 FF3 DD3 SS3 SSC4 (n=17) | False | 0 | 0 | 0 | 17 | reserve:2 |
| USA | BB22 CV7 CA18 CL36 SSC3 DD381 SS91 FF20 (n=578) | True | 220 | 288 | 0 | 70 | none/hold:25, patrol:10, raid:2, reserve:2 |
| SOV | BB3 CA3 CL5 SS91 SSC56 DD23 FF18 (n=199) | False | 174 | 12 | 0 | 13 | escort:1, none/hold:2, patrol:1, raid:14, reserve:4 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: escort [FF11] x1; inv-support? [CA4 CL8] x1; none/hold [SSC1] x1; patrol [DD16] x1; raid [SS7] x1; raid [SSC10] x2; raid [SSC9] x1; reserve [BB2 CA2] x1; reserve [SSC3] x1
- **ITA**: none/hold [CA4 CL12] x1; none/hold [FF16] x1; none/hold [FF18] x1; patrol [DD20] x1; raid [SS10] x2; raid [SSC9] x1; reserve [BB9 CA5 CL12 DD17 SS6] x1; reserve [CA1] x1
- **JAP**: none/hold [BC2 CA4 CL12] x1; none/hold [CVL1 FF20] x2; none/hold [FF20] x1; patrol [DD20] x7; raid [BC2 CA6] x1; raid [SS10] x5; raid [SSC8] x1; reserve [CA1] x1; reserve [CV5 CL1 FF14 DD6 SS8] x1; strike [CV4 BB7 CA10 CL20 DD30] x1
- **ENG**: escort [FF20] x5; none/hold [BC3 CA1 CL12] x1; none/hold [CV2 BB7 CA9 CL19 DD30] x1; none/hold [CVL1 FF20] x1; none/hold [FF20] x1; patrol [DD20] x10; raid [SS7] x1; raid [SSC8] x1; reserve [BB4 CL16] x1; reserve [CV2 BB1] x1; reserve [CV3 BB5 CL5 DD74 FF3] x1; reserve [DD43] x1
- **FRA**: reserve [CV1 BB3 FF3 DD3 SS2 SSC4] x1; reserve [SS1] x1
- **USA**: none/hold [CA4 CL12] x1; none/hold [CV4 BB8 CA10 CL20 DD30] x1; none/hold [DD10] x11; none/hold [FF1] x3; none/hold [FF17] x1; none/hold [SS1] x1; none/hold [SS10] x6; none/hold [SS9] x1; patrol [DD20] x10; raid [SS10] x2; reserve [BB8 CA2 SSC3] x1; reserve [CV3 BB6 CA2 CL4 DD41 SS1] x1
- **SOV**: escort [FF18] x1; none/hold [CA3 CL5] x1; none/hold [SSC4] x1; patrol [DD20] x1; raid [SS10] x9; raid [SSC10] x4; raid [SSC6] x1; reserve [BB1 SSC5] x1; reserve [BB2] x1; reserve [DD3 SSC1] x1; reserve [SS1] x1

### 1943.6.1.2 (1943.6_Jun.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SSC27 DD16 SS4 FF10 (n=73) | False | 41 | 17 | 0 | 15 | escort:1, none/hold:6, patrol:1, raid:2, reserve:3 |
| ITA | BB9 CA10 CL26 DD44 SS21 SSC8 FF34 (n=152) | False | 102 | 16 | 0 | 34 | escort:2, none/hold:1, patrol:2, raid:3, reserve:2 |
| JAP | CV10 BB7 BC4 CA21 CVL2 CL38 FF92 DD197 SS53 SSC8 (n=432) | True | 285 | 112 | 0 | 35 | escort:3, none/hold:5, patrol:8, raid:7, reserve:1 |
| ENG | BB17 CV10 BC3 CA10 CVL1 CL59 DD380 FF179 SSC8 SS9 (n=676) | True | 386 | 77 | 0 | 213 | escort:5, mine5:1, none/hold:4, patrol:10, raid:2, reserve:5, strike:1 |
| FRA | CV1 BB3 FF4 DD4 SS3 SSC4 (n=19) | False | 0 | 0 | 0 | 19 | reserve:2 |
| USA | BB24 CV11 CA21 CL45 SSC3 DD419 FF57 SS92 (n=672) | True | 358 | 170 | 0 | 144 | escort:3, none/hold:18, patrol:10, raid:6, reserve:2, strike:1 |
| SOV | BB3 CA3 CL5 SS91 SSC67 FF18 DD23 (n=210) | False | 166 | 30 | 0 | 14 | none/hold:3, patrol:1, raid:15, reserve:4 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: escort [FF10] x1; none/hold [CA4 CL8] x1; none/hold [SSC1] x5; patrol [DD16] x1; raid [SSC10] x1; raid [SSC5] x1; reserve [BB2 CA2 SS4 SSC5] x1; reserve [SSC1] x2
- **ITA**: escort [FF16] x1; escort [FF18] x1; none/hold [CA4 CL12] x1; patrol [DD20] x2; raid [SS10] x2; raid [SSC8] x1; reserve [BB9 CA5 CL14 DD4 SS1] x1; reserve [CA1] x1
- **JAP**: escort [CVL1 FF20] x1; escort [FF20] x2; none/hold [BC2 CA4 CL12] x1; none/hold [CV4 BB7 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x1; none/hold [SS1] x2; patrol [DD20] x8; raid [BC2 CA6] x1; raid [SS10] x4; raid [SS8] x1; raid [SSC8] x1; reserve [CV6 CA1 CL6 FF12 DD7 SS3] x1
- **ENG**: escort [FF20] x5; mine5 [FF4] x1; none/hold [BC3 CA1 CL12] x1; none/hold [CVL1 FF20] x1; none/hold [FF20] x2; patrol [DD20] x10; raid [SS9] x1; raid [SSC8] x1; reserve [BB4 CL15] x1; reserve [CA2] x1; reserve [CV2 BB1] x1; reserve [CV6 BB5 CL13 DD107 FF15] x1; reserve [DD43] x1; strike [CV2 BB7 CA7 CL19 DD30] x1
- **FRA**: reserve [CV1 BB3 FF3 DD3 SS2 SSC4] x1; reserve [FF1 DD1 SS1] x1
- **USA**: escort [DD10] x3; none/hold [CA4 CL12] x1; none/hold [DD1] x1; none/hold [DD10] x8; none/hold [FF20] x2; none/hold [SS1] x3; none/hold [SS10] x3; patrol [DD19] x1; patrol [DD20] x9; raid [SS10] x5; raid [SS7] x1; reserve [BB8 CA2 SSC3] x1; reserve [CV7 BB8 CA5 CL13 DD79 FF17 SS2] x1; strike [CV4 BB8 CA10 CL20 DD30] x1
- **SOV**: none/hold [CA3 CL5] x1; none/hold [FF18] x1; none/hold [SSC4] x1; patrol [DD20] x1; raid [SS10] x9; raid [SSC10] x5; raid [SSC6] x1; reserve [BB1 SSC6] x1; reserve [BB2] x1; reserve [DD3 SSC1] x1; reserve [SS1] x1

### 1944.3.1.2 (1944.3_Mar.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SSC42 DD16 SS4 FF10 (n=88) | False | 36 | 32 | 0 | 20 | escort:1, none/hold:11, patrol:1, raid:1, reserve:6 |
| ITA | BB9 CA10 CL28 DD60 SSC8 SS9 (n=124) | False | 77 | 16 | 0 | 31 | none/hold:1, patrol:3, raid:2, reserve:2 |
| JAP | CV10 BC4 BB8 CA21 CVL5 CL41 FF108 DD212 SS52 SSC8 (n=469) | True | 246 | 193 | 0 | 30 | none/hold:7, patrol:9, raid:7, reserve:2 |
| ENG | BB17 CV10 BC3 CA13 CVL1 CL68 DD415 FF198 SSC7 SS56 (n=788) | True | 427 | 120 | 0 | 241 | escort:4, mine5:1, none/hold:6, patrol:11, raid:7, reserve:7, strike:1 |
| FRA | CV1 BB3 FF4 DD4 SS3 SSC4 (n=19) | False | 0 | 0 | 0 | 19 | reserve:2 |
| USA | BB26 CV18 BC2 CA20 CL52 SSC3 SS62 DD451 FF86 (n=720) | True | 368 | 172 | 0 | 180 | escort:4, none/hold:14, patrol:10, raid:6, reserve:3, strike:1 |
| SOV | BB3 CA3 CL5 SS91 SSC77 FF18 DD23 (n=220) | False | 176 | 30 | 0 | 14 | none/hold:3, patrol:1, raid:16, reserve:4 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: escort [FF10] x1; none/hold [CA4 CL8] x1; none/hold [SSC1] x7; none/hold [SSC2] x1; none/hold [SSC4] x1; none/hold [SSC7] x1; patrol [DD16] x1; raid [SSC10] x1; reserve [BB2 CA2 SS4 SSC1] x1; reserve [SSC1] x3; reserve [SSC2] x1; reserve [SSC6] x1
- **ITA**: none/hold [CA4 CL12] x1; patrol [DD20] x3; raid [SS9] x1; raid [SSC8] x1; reserve [BB9 CA5 CL16] x1; reserve [CA1] x1
- **JAP**: none/hold [BC2 CA4 CL12] x1; none/hold [CV4 BB6 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x5; patrol [DD20] x9; raid [BC2 CA6] x1; raid [SS10] x5; raid [SSC8] x1; reserve [BB2] x1; reserve [CV6 CA1 CL9 FF8 DD2 SS2] x1
- **ENG**: escort [FF20] x4; mine5 [FF5] x1; none/hold [BC3 CA4 CL12] x1; none/hold [CVL1 FF20] x1; none/hold [FF20] x4; patrol [DD20] x11; raid [SS10] x2; raid [SS6] x2; raid [SS9] x2; raid [SSC7] x1; reserve [BB4 CL15] x1; reserve [CA1 CL3] x1; reserve [CA1 DD43] x1; reserve [CL1 DD1 SS6] x1; reserve [CV2 BB1] x1; reserve [CV6 BB5 CL18 DD119 FF13] x1; reserve [DD2] x1; strike [CV2 BB7 CA7 CL19 DD30] x1
- **FRA**: reserve [CV1 BB3 FF3 DD3 SS2 SSC4] x1; reserve [FF1 DD1 SS1] x1
- **USA**: escort [DD10] x4; none/hold [BC2 CA4 CL12] x1; none/hold [DD10] x7; none/hold [FF20] x4; none/hold [SS1] x1; none/hold [SS3] x1; patrol [DD20] x10; raid [SS10] x4; raid [SS7] x1; raid [SS9] x1; reserve [BB8 SSC3 SS1] x1; reserve [CV14 BB10 CA6 CL20 DD111 FF6] x1; reserve [SS1] x1; strike [CV4 BB8 CA10 CL20 DD30] x1
- **SOV**: none/hold [CA3 CL5] x1; none/hold [FF18] x1; none/hold [SSC4] x1; patrol [DD20] x1; raid [SS10] x9; raid [SSC10] x6; raid [SSC6] x1; reserve [BB1 SSC6] x1; reserve [BB2] x1; reserve [DD3 SSC1] x1; reserve [SS1] x1

## Q-N3 (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1) - ratio = sum(enemy strength) / own strength, monthly

| tag | war-months | superior | neutral | inferior | flips | flaps(<=3mo) |
|---|---|---|---|---|---|---|
| GER | 63 | 0 (0%) | 0 (0%) | 63 (100%) | 0 | 0 |
| ITA | 62 | 4 (6%) | 0 (0%) | 58 (94%) | 1 | 0 |
| JAP | 92 | 52 (57%) | 0 (0%) | 40 (43%) | 1 | 0 |
| ENG | 66 | 29 (44%) | 37 (56%) | 0 (0%) | 2 | 0 |
| FRA | 66 | 8 (12%) | 0 (0%) | 58 (88%) | 1 | 0 |
| USA | 40 | 3 (8%) | 37 (92%) | 0 (0%) | 1 | 0 |
| SOV | 47 | 4 (9%) | 2 (4%) | 41 (87%) | 3 | 0 |

### GER (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: none
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1945.1.1 | inferior | 6.66-27.91 | 173..139 | 1351..3880 |

### ITA (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1940.7.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1936.2.1 | 1936.5.1 | superior | 0.00-0.00 | 234..246 | 0..0 |
| 1940.7.1 | 1945.4.1 | inferior | 3.08-12.96 | 400..144 | 1232..898 |

### JAP (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1942.1.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1937.9.1 | 1941.12.1 | superior | 0.04-0.05 | 479..707 | 23..26 |
| 1942.1.1 | 1945.4.1 | inferior | 3.56-4.08 | 710..898 | 2529..3667 |

### ENG (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1942.1.1 sup->neu; 1945.2.1 neu->sup
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1941.12.1 | superior | 0.19-0.65 | 895..971 | 173..466 |
| 1942.1.1 | 1945.1.1 | neutral | 1.05-1.23 | 965..1152 | 1182..1209 |
| 1945.2.1 | 1945.4.1 | superior | 0.77-0.79 | 1154..1170 | 907..898 |

### FRA (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1940.7.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.6.1 | superior | 0.49-0.49 | 350..373 | 173..183 |
| 1940.7.1 | 1945.4.1 | inferior | 8.88-inf | 0..63 | 585..898 |

### USA (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1945.2.1 neu->sup
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1942.1.1 | 1945.1.1 | neutral | 0.88-1.26 | 936..1380 | 1182..1209 |
| 1945.2.1 | 1945.4.1 | superior | 0.65-0.66 | 1380..1386 | 907..898 |

### SOV (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1941.7.1 sup->inf; 1944.12.1 inf->neu; 1945.4.1 neu->sup
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.2.1 | superior | 0.06-0.07 | 223..225 | 13..15 |
| 1941.7.1 | 1944.11.1 | inferior | 1.59-2.26 | 240..279 | 542..448 |
| 1944.12.1 | 1945.1.1 | neutral | 1.06-1.09 | 282..285 | 307..302 |
| 1945.4.1 | 1945.4.1 | superior | 0.00-0.00 | 293..293 | 0..0 |

## Q-N3 (plain hull count) - ratio = sum(enemy strength) / own strength, monthly

| tag | war-months | superior | neutral | inferior | flips | flaps(<=3mo) |
|---|---|---|---|---|---|---|
| GER | 63 | 0 (0%) | 0 (0%) | 63 (100%) | 0 | 0 |
| ITA | 62 | 4 (6%) | 0 (0%) | 58 (94%) | 1 | 0 |
| JAP | 92 | 52 (57%) | 0 (0%) | 40 (43%) | 1 | 0 |
| ENG | 66 | 29 (44%) | 37 (56%) | 0 (0%) | 2 | 0 |
| FRA | 66 | 8 (12%) | 0 (0%) | 58 (88%) | 1 | 0 |
| USA | 40 | 3 (8%) | 37 (92%) | 0 (0%) | 1 | 0 |
| SOV | 47 | 6 (13%) | 39 (83%) | 2 (4%) | 3 | 0 |

### GER (plain hull count)

Flips: none
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1945.1.1 | inferior | 5.99-34.85 | 115..81 | 839..2377 |

### ITA (plain hull count)

Flips: 1940.7.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1936.2.1 | 1936.5.1 | superior | 0.00-0.00 | 160..168 | 0..0 |
| 1940.7.1 | 1945.4.1 | inferior | 2.92-21.05 | 263..63 | 772..494 |

### JAP (plain hull count)

Flips: 1942.1.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1937.9.1 | 1941.12.1 | superior | 0.03-0.04 | 247..373 | 9..10 |
| 1942.1.1 | 1945.4.1 | inferior | 3.89-4.38 | 376..494 | 1564..2163 |

### ENG (plain hull count)

Flips: 1942.1.1 sup->neu; 1945.2.1 neu->sup
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1941.12.1 | superior | 0.22-0.78 | 529..574 | 115..252 |
| 1942.1.1 | 1945.1.1 | neutral | 0.91-1.09 | 578..693 | 625..659 |
| 1945.2.1 | 1945.4.1 | superior | 0.70-0.73 | 693..707 | 505..494 |

### FRA (plain hull count)

Flips: 1940.7.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.6.1 | superior | 0.50-0.53 | 226..238 | 115..125 |
| 1940.7.1 | 1945.4.1 | inferior | 15.75-inf | 0..27 | 390..494 |

### USA (plain hull count)

Flips: 1945.2.1 neu->sup
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1942.1.1 | 1945.1.1 | neutral | 0.93-1.14 | 548..712 | 625..659 |
| 1945.2.1 | 1945.4.1 | superior | 0.70-0.71 | 710..703 | 505..494 |

### SOV (plain hull count)

Flips: 1941.7.1 sup->inf; 1941.9.1 inf->neu; 1944.12.1 neu->sup
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.2.1 | superior | 0.04-0.07 | 178..180 | 13..7 |
| 1941.7.1 | 1941.8.1 | inferior | 1.74-1.75 | 191..191 | 334..333 |
| 1941.9.1 | 1944.11.1 | neutral | 0.92-1.42 | 192..230 | 272..215 |
| 1944.12.1 | 1945.4.1 | superior | 0.00-0.67 | 233..244 | 155..0 |


# Campaign e953ae9b: 98 saves 1936.2.1.2 .. 1944.3.1.2

## Q-N2a. Every task force with mission=2 (strike), all countries, all saves

| date | tag | fleet | TF ships | TF meets 2CV+2BB+10CL | country total CV/BB/CL | country meets |
|---|---|---|---|---|---|---|
| 1937.9.1 | JAP | Empire of Japan Fleet 2 | CV3 BB6 CA10 CL20 DD30 | True | 3/6/20 | True |
| 1937.10.1 | JAP | Empire of Japan Fleet 2 | CV3 BB6 CA10 CL20 DD30 | True | 3/6/20 | True |
| 1940.7.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/42 | True |
| 1940.8.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/43 | True |
| 1940.9.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/44 | True |
| 1940.10.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/44 | True |
| 1940.11.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/44 | True |
| 1940.12.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/46 | True |
| 1941.1.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL19 DD30 | True | 8/17/46 | True |
| 1941.2.1 | ENG | United Kingdom Fleet 11 | CV2 BB8 CA10 CL19 DD30 | True | 7/17/46 | True |
| 1941.3.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/47 | True |
| 1941.4.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/48 | True |
| 1941.5.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/48 | True |
| 1941.6.1 | ENG | United Kingdom Fleet 9 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/49 | True |
| 1941.7.1 | ENG | United Kingdom Fleet 3 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/50 | True |
| 1941.8.1 | ENG | United Kingdom Fleet 3 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/50 | True |
| 1941.9.1 | ENG | United Kingdom Fleet 3 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/51 | True |
| 1941.10.1 | ENG | United Kingdom Fleet 10 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/51 | True |
| 1941.11.1 | ENG | United Kingdom Fleet 3 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/52 | True |
| 1941.12.1 | ENG | United Kingdom Fleet 3 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/52 | True |
| 1942.1.1 | ENG | United Kingdom Fleet 3 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/53 | True |
| 1942.1.1 | USA | USS Navy Group 2 | CV4 BB8 CA10 CL20 DD30 | True | 7/21/32 | True |
| 1942.2.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/53 | True |
| 1942.2.1 | JAP | Empire of Japan Fleet 6 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/31 | True |
| 1942.2.1 | USA | USS Navy Group 2 | CV4 BB7 CA8 CL18 DD30 | True | 7/20/30 | True |
| 1942.3.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/54 | True |
| 1942.3.1 | JAP | Empire of Japan Fleet 6 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/31 | True |
| 1942.3.1 | USA | USS Navy Group 2 | CV4 BB7 CA5 CL14 DD30 | True | 7/21/27 | True |
| 1942.4.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/54 | True |
| 1942.4.1 | JAP | Empire of Japan Fleet 5 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/31 | True |
| 1942.4.1 | USA | USS Navy Group 2 | CV4 BB7 CA5 CL15 DD30 | True | 7/20/28 | True |
| 1942.5.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/55 | True |
| 1942.6.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/56 | True |
| 1942.7.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/56 | True |
| 1942.7.1 | JAP | Empire of Japan Fleet 6 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/33 | True |
| 1942.7.1 | USA | USS Navy Group 2 | CV4 BB7 CA5 CL17 DD30 | True | 7/19/30 | True |
| 1942.8.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/57 | True |
| 1942.8.1 | USA | USS Navy Group 2 | CV4 BB6 CA4 CL18 DD30 | True | 7/19/31 | True |
| 1942.9.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/57 | True |
| 1942.9.1 | USA | USS Navy Group 2 | CV4 BB5 CA5 CL18 DD30 | True | 7/19/30 | True |
| 1942.10.1 | ENG | United Kingdom Fleet 9 | CV4 BB8 CA10 CL20 DD30 | True | 7/17/58 | True |
| 1942.10.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/34 | True |
| 1942.10.1 | USA | USS Navy Group 9 | CV4 BB5 CA5 CL18 DD30 | True | 8/19/31 | True |
| 1942.11.1 | ENG | United Kingdom Fleet 9 | CV4 BB8 CA10 CL20 DD30 | True | 9/17/59 | True |
| 1942.11.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/34 | True |
| 1942.11.1 | USA | USS Navy Group 9 | CV4 BB6 CA5 CL18 DD30 | True | 8/19/30 | True |
| 1942.12.1 | ENG | United Kingdom Fleet 6 | CV4 BB8 CA10 CL20 DD30 | True | 9/17/59 | True |
| 1942.12.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/35 | True |
| 1942.12.1 | USA | USS Navy Group 2 | CV4 BB6 CA5 CL19 DD30 | True | 8/19/31 | True |
| 1943.1.1 | ENG | United Kingdom Fleet 6 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/60 | True |
| 1943.1.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/35 | True |
| 1943.1.1 | USA | USS Navy Group 2 | CV4 BB6 CA5 CL17 DD29 | True | 9/20/29 | True |
| 1943.2.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/36 | True |
| 1943.3.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 8/7/36 | True |
| 1943.4.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/62 | True |
| 1943.4.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/36 | True |
| 1943.4.1 | USA | USS Navy Group 2 | CV4 BB6 CA5 CL19 DD30 | True | 10/20/32 | True |
| 1943.5.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/62 | True |
| 1943.5.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/37 | True |
| 1943.6.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/63 | True |
| 1943.6.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/37 | True |
| 1943.7.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/64 | True |
| 1943.7.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/38 | True |
| 1943.8.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/64 | True |
| 1943.8.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/38 | True |
| 1943.9.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/65 | True |
| 1943.9.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/38 | True |
| 1943.9.1 | USA | USS Navy Group 2 | CV4 BB6 CA5 CL20 DD30 | True | 13/20/34 | True |
| 1943.10.1 | ENG | United Kingdom Fleet 11 | CV4 BB8 CA10 CL20 DD30 | True | 10/17/65 | True |
| 1943.10.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/39 | True |
| 1943.10.1 | USA | USS Navy Group 2 | CV4 BB6 CA5 CL20 DD30 | True | 13/20/35 | True |
| 1943.11.1 | JAP | Empire of Japan Fleet 2 | CV4 BB7 CA10 CL20 DD30 | True | 9/7/39 | True |
| 1944.1.1 | JAP | Empire of Japan Fleet 11 | CV4 BB7 CA10 CL20 DD30 | True | 10/7/39 | True |

Total strike-TF observations: 73

Mission-id census (TF observations over all saves, all countries): 0=7853, 1=2505, 2=73, 3=1558, 4=677, 5=53, 7=2476, 8=5397, 9=49

## Q-N2c. Task forces that satisfy StrikeForce_1 min (>=2CV,>=2BB,>=10CL), by mission (TF-observations; distinct tag list)

- none/hold: 187 TF-obs, tags ['ENG', 'JAP', 'USA']
- strike: 73 TF-obs, tags ['ENG', 'JAP', 'USA']
- reserve: 43 TF-obs, tags ['ENG']
- train: 33 TF-obs, tags ['ENG', 'JAP', 'USA']
- fleet-region split: none/hold/fleet has regions=6, none/hold/fleet no regions=181, reserve/fleet no regions=43, strike/fleet has regions=73, train/fleet has regions=33
- first save per (tag, mission): ENG:none/hold@1936.10.1, ENG:reserve@1940.9.1, ENG:strike@1940.7.1, ENG:train@1936.2.1, JAP:none/hold@1936.6.1, JAP:strike@1937.9.1, JAP:train@1936.2.1, USA:none/hold@1936.3.1, USA:strike@1942.1.1, USA:train@1936.5.1

Mission x fleet-has-strategic_region (TF obs): escort/reg=677, inv-support?/reg=49, mine5/reg=53, none/hold/noreg=6895, none/hold/reg=958, patrol/noreg=1, patrol/reg=2504, raid/noreg=11, raid/reg=1547, reserve/noreg=5397, strike/reg=73, train/reg=2476

## Q-N2b. Majors at the sampled dates

### 1939.9.1.2 (autosave_85.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 FF12 SSC44 SS26 DD16 (n=114) | False | 0 | 68 | 32 | 14 | none/hold:6, reserve:1, train:3 |
| ITA | BB6 CA9 CL18 FF56 DD91 SSC13 SS55 (n=248) | False | 0 | 146 | 50 | 52 | none/hold:9, reserve:4, train:4 |
| JAP | BC4 CV6 BB7 CVL2 CA21 CL23 DD131 FF31 SS52 SSC8 (n=285) | True | 88 | 150 | 0 | 47 | none/hold:8, patrol:4, raid:1, reserve:3 |
| ENG | BB14 BC3 CV6 CVL1 CA16 CL41 DD270 SSC21 FF112 SS35 (n=519) | True | 0 | 280 | 153 | 86 | none/hold:14, reserve:2, train:9 |
| FRA | CV1 BB5 BC2 CA7 CL12 SSC40 DD49 FF64 SS41 (n=221) | False | 0 | 101 | 90 | 30 | none/hold:7, reserve:3, train:7 |
| USA | BB16 CV6 CA18 CL19 SSC3 DD298 SS81 (n=441) | True | 0 | 321 | 80 | 40 | none/hold:22, reserve:2, train:6 |
| SOV | BB3 CA2 CL5 SS91 SSC35 DD23 FF18 (n=177) | False | 0 | 115 | 50 | 12 | none/hold:11, reserve:4, train:5 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: none/hold [CA4 CL8] x1; none/hold [DD16] x1; none/hold [SS10] x2; none/hold [SSC10] x2; reserve [BB2 CA2 SS6 SSC4] x1; train [FF12] x1; train [SSC10] x2
- **ITA**: none/hold [CA4 CL12] x1; none/hold [DD20] x3; none/hold [FF20] x2; none/hold [SS10] x3; reserve [BB6 CA4 CL6 FF15 DD11 SSC3 SS4] x1; reserve [CA1] x1; reserve [FF1] x1; reserve [SS1] x1; train [DD20] x1; train [SS10] x2; train [SSC10] x1
- **JAP**: none/hold [BC2 CA6] x1; none/hold [CV4 BB7 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x1; none/hold [SS10] x5; patrol [DD20] x4; raid [SSC8] x1; reserve [BC1] x1; reserve [CV2 BC1 CA2 CL3 DD21 FF11 SS2] x1; reserve [CVL1 CA3] x1
- **ENG**: none/hold [BC2 CA6] x1; none/hold [CV4 BB8 CA10 CL20 DD30] x1; none/hold [DD20] x7; none/hold [FF20] x1; none/hold [SS10] x2; none/hold [SSC10] x2; reserve [BB4 BC1 CL15 DD1 SSC1] x1; reserve [CV2 BB2 CL6 DD39 FF10 SS5] x1; train [CVL1 FF20] x1; train [DD20] x3; train [FF2] x1; train [FF20] x3; train [SS10] x1
- **FRA**: none/hold [BC2 CA6] x1; none/hold [CA1 CL12] x1; none/hold [DD20] x2; none/hold [FF20] x1; none/hold [SS10] x1; none/hold [SSC10] x1; reserve [BB2 DD9 FF4 SSC2 SS1] x1; reserve [BB3] x1; reserve [CV1 SSC8] x1; train [FF20] x2; train [SS10] x3; train [SSC10] x2
- **USA**: none/hold [CV4 BB8 CA10 CL19 DD30] x1; none/hold [DD10] x8; none/hold [DD20] x5; none/hold [SS10] x6; none/hold [SS3] x1; none/hold [SS7] x1; reserve [BB8 CA6 SSC3] x1; reserve [CV2 CA2 DD18 SS1] x1; train [DD10] x3; train [DD20] x2; train [SS10] x1
- **SOV**: none/hold [CA2 CL5] x1; none/hold [DD20] x1; none/hold [FF18] x1; none/hold [SS10] x4; none/hold [SSC1] x1; none/hold [SSC10] x2; none/hold [SSC9] x1; reserve [BB1] x1; reserve [BB2] x1; reserve [DD3 SSC1] x1; reserve [SS1 SSC4] x1; train [SS10] x5

### 1941.6.1.2 (autosave_64.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 FF12 SS7 SSC66 DD16 (n=117) | False | 63 | 44 | 0 | 10 | none/hold:4, patrol:1, raid:5, reserve:2 |
| ITA | BB8 CA9 CL22 FF54 DD123 SS17 SSC10 (n=243) | False | 187 | 16 | 0 | 40 | escort:2, none/hold:1, patrol:6, raid:3, reserve:2 |
| JAP | CV8 BB7 BC4 CA21 CVL2 CL28 FF48 DD157 SS55 SSC8 (n=338) | True | 130 | 183 | 0 | 25 | none/hold:10, patrol:6, raid:1, reserve:2 |
| ENG | CV7 BB17 BC3 CVL1 CA16 CL49 DD285 FF134 SSC15 SS10 (n=537) | True | 431 | 0 | 0 | 106 | escort:6, mine5:1, patrol:10, raid:4, reserve:2, strike:1 |
| FRA | CV1 BB3 DD3 FF3 SS2 SSC7 (n=19) | False | 7 | 0 | 0 | 12 | raid:1, reserve:2 |
| USA | BB18 CV7 CA18 CL28 SSC3 SS86 DD345 (n=505) | True | 140 | 334 | 0 | 31 | none/hold:24, patrol:7, reserve:2 |
| SOV | BB3 CA3 CL5 SS91 SSC48 FF18 DD23 (n=191) | False | 20 | 146 | 0 | 25 | none/hold:14, patrol:1, reserve:6 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: none/hold [CA4 CL8] x1; none/hold [FF12] x1; none/hold [SSC10] x2; patrol [DD16] x1; raid [SS7] x1; raid [SSC10] x4; reserve [BB2 CA2] x1; reserve [SSC6] x1
- **ITA**: escort [FF20] x2; none/hold [CA4 CL12] x1; patrol [DD20] x6; raid [SS10] x1; raid [SS7] x1; raid [SSC10] x1; reserve [BB8 CA4 CL10 FF13 DD3] x1; reserve [CA1 FF1] x1
- **JAP**: none/hold [BC2 CA4 CL8] x1; none/hold [BC2 CA6] x1; none/hold [CV4 BB7 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x2; none/hold [SS10] x4; none/hold [SSC8] x1; patrol [DD20] x6; raid [SS10] x1; reserve [CA1] x1; reserve [CV4 FF8 DD7 SS5] x1
- **ENG**: escort [CVL1 FF20] x1; escort [FF20] x5; mine5 [FF5] x1; patrol [DD20] x10; raid [BC2 CA6] x1; raid [SS10] x1; raid [SSC7] x1; raid [SSC8] x1; reserve [CL2 FF9 DD9] x1; reserve [CV3 BB9 BC1 CL27 DD46] x1; strike [CV4 BB8 CA10 CL20 DD30] x1
- **FRA**: raid [SSC7] x1; reserve [BB2 FF3 SS2] x1; reserve [CV1 BB1 DD3] x1
- **USA**: none/hold [CA4 CL8] x1; none/hold [CV4 BB8 CA10 CL20 DD30] x1; none/hold [DD10] x11; none/hold [DD20] x3; none/hold [SS10] x8; patrol [DD20] x7; reserve [BB8 CA2 SSC3 SS5] x1; reserve [CV3 BB2 CA2 DD5 SS1] x1
- **SOV**: none/hold [CA3 CL5] x1; none/hold [FF18] x1; none/hold [SS10] x9; none/hold [SSC10] x3; patrol [DD20] x1; reserve [BB1] x1; reserve [BB2] x1; reserve [DD3 SSC1] x1; reserve [SS1 SSC8] x1; reserve [SSC1] x1; reserve [SSC8] x1

### 1942.6.1.2 (autosave_52.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SS3 FF12 SSC80 DD16 (n=127) | False | 94 | 25 | 0 | 8 | none/hold:4, patrol:1, raid:8, reserve:2 |
| ITA | BB9 CA10 CL26 FF2 SSC4 SS13 DD76 (n=140) | False | 86 | 16 | 0 | 38 | none/hold:1, patrol:5, raid:1, reserve:2 |
| JAP | CV8 BC4 BB7 CA20 CVL2 CL32 FF60 DD175 SS57 SSC8 (n=373) | True | 206 | 131 | 0 | 36 | none/hold:4, patrol:7, raid:7, reserve:1 |
| ENG | CV7 BB17 BC2 CVL2 CA12 CL56 DD356 FF163 SS11 SSC14 (n=640) | True | 460 | 0 | 0 | 180 | escort:7, inv-support?:1, mine5:1, patrol:10, raid:3, reserve:4, strike:1 |
| FRA | CV1 BB3 DD3 FF3 SS2 SSC7 (n=19) | False | 7 | 0 | 0 | 12 | raid:1, reserve:2 |
| USA | BB19 CV7 CA14 CL29 SSC3 SS69 DD380 FF18 (n=539) | True | 271 | 194 | 0 | 74 | escort:1, none/hold:18, patrol:10, raid:6, reserve:12 |
| SOV | BB3 CA3 CL5 SSC43 SS55 DD23 FF18 (n=150) | False | 104 | 32 | 0 | 14 | escort:1, none/hold:12, patrol:1, raid:7, reserve:6 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: none/hold [] x1; none/hold [CA4 CL8] x1; none/hold [FF12] x1; none/hold [SSC1] x1; patrol [DD16] x1; raid [SSC10] x7; raid [SSC8] x1; reserve [BB2 CA2 SS3] x1; reserve [SSC1] x1
- **ITA**: none/hold [CA4 CL12] x1; patrol [DD11] x1; patrol [DD16] x1; patrol [DD20] x2; patrol [DD9] x1; raid [SS10] x1; reserve [BB9 CA5 CL14 FF2 SSC4 SS3] x1; reserve [CA1] x1
- **JAP**: none/hold [BC2 CA4 CL12] x1; none/hold [CV4 BB7 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x2; patrol [DD20] x7; raid [BC2 CA6] x1; raid [SS10] x5; raid [SSC8] x1; reserve [CV4 FF20 DD5 SS7] x1
- **ENG**: escort [CVL1 FF20] x2; escort [FF20] x5; inv-support? [BC2 CA2 CL12] x1; mine5 [FF6] x1; patrol [DD20] x10; raid [SS10] x1; raid [SSC7] x2; reserve [CL4 DD37 FF16 SS1] x1; reserve [CV3 BB9 CL20 DD46] x1; reserve [DD43] x1; reserve [FF1] x1; strike [CV4 BB8 CA10 CL20 DD30] x1
- **FRA**: raid [SSC7] x1; reserve [BB2 FF3 SS2] x1; reserve [CV1 BB1 DD3] x1
- **USA**: escort [FF15] x1; none/hold [BB1] x1; none/hold [CA4 CL12] x1; none/hold [CV4 BB7 CA5 CL17 DD30] x1; none/hold [DD10] x11; none/hold [FF1] x3; none/hold [SS1] x1; patrol [DD20] x10; raid [SS10] x4; raid [SS7] x1; raid [SS9] x1; reserve [BB5 SSC3] x1; reserve [CV3 BB6 CA5 DD40] x1; reserve [SS1] x9; reserve [SS3] x1
- **SOV**: escort [FF18] x1; none/hold [CA3 CL5] x1; none/hold [SS10] x1; none/hold [SSC1] x8; none/hold [SSC3] x2; patrol [DD20] x1; raid [SS10] x4; raid [SSC8] x1; raid [SSC9] x2; reserve [BB1 SSC2] x1; reserve [BB2] x1; reserve [DD3] x1; reserve [SS1] x1; reserve [SS4] x1; reserve [SSC1] x1

### 1943.6.1.2 (autosave_40.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SS3 SSC77 DD16 FF12 (n=124) | False | 91 | 26 | 0 | 7 | escort:1, none/hold:6, patrol:1, raid:7, reserve:1 |
| ITA | BB9 CA10 CL29 FF2 SSC4 SS13 DD36 (n=103) | False | 46 | 16 | 0 | 41 | none/hold:1, patrol:2, raid:1, reserve:2 |
| JAP | CV9 BB7 BC4 CA21 CVL2 CL37 FF77 DD194 SS52 SSC8 (n=411) | True | 375 | 2 | 0 | 34 | escort:3, inv-support?:1, none/hold:2, patrol:8, raid:7, reserve:1, strike:1 |
| ENG | CV10 BB17 BC2 CVL2 CA12 CL63 DD391 FF199 SS14 SSC14 (n=724) | True | 477 | 23 | 0 | 224 | escort:9, mine5:1, none/hold:2, patrol:10, raid:2, reserve:4, strike:1 |
| FRA | CV1 BB3 DD3 FF3 SS2 SSC7 (n=19) | False | 7 | 0 | 0 | 12 | raid:1, reserve:2 |
| USA | BB20 CV11 CA15 CL32 SSC3 DD403 FF54 SS39 (n=577) | True | 276 | 194 | 0 | 107 | escort:5, none/hold:18, patrol:10, raid:3, reserve:2 |
| SOV | BB3 CA3 CL5 SSC41 SS55 DD3 FF18 (n=128) | False | 100 | 16 | 0 | 12 | escort:1, none/hold:9, raid:9, reserve:5 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: escort [FF12] x1; none/hold [CA4 CL8] x1; none/hold [SSC1] x4; none/hold [SSC10] x1; patrol [DD16] x1; raid [SSC10] x3; raid [SSC7] x1; raid [SSC8] x1; raid [SSC9] x2; reserve [BB2 CA2 SS3] x1
- **ITA**: none/hold [CA4 CL12] x1; patrol [DD16] x1; patrol [DD20] x1; raid [SS10] x1; reserve [BB9 CA5 CL17 FF2 SSC4 SS3] x1; reserve [CA1] x1
- **JAP**: escort [CVL1 FF20] x2; escort [FF20] x1; inv-support? [BC2 CA4 CL12] x1; none/hold [SS1] x2; patrol [DD20] x8; raid [BC2 CA6] x1; raid [SS10] x4; raid [SS8] x1; raid [SSC8] x1; reserve [CV5 CA1 CL5 FF17 DD4 SS2] x1; strike [CV4 BB7 CA10 CL20 DD30] x1
- **ENG**: escort [CVL1 FF20] x2; escort [FF20] x7; mine5 [FF6] x1; none/hold [BC2 CA2 CL12] x1; none/hold [SSC7] x1; patrol [DD20] x10; raid [SS10] x1; raid [SSC7] x1; reserve [CV3 BB9 CL20 DD46] x1; reserve [CV3 CL11 DD72 FF12 SS4] x1; reserve [DD43] x1; reserve [FF1] x1; strike [CV4 BB8 CA10 CL20 DD30] x1
- **FRA**: raid [SSC7] x1; reserve [BB2 FF3 SS2] x1; reserve [CV1 BB1 DD3] x1
- **USA**: escort [DD10] x4; escort [DD6] x1; none/hold [CA1] x1; none/hold [CA4 CL12] x1; none/hold [CL1] x1; none/hold [CV4 BB6 CA4 CL19 DD30] x1; none/hold [DD1] x4; none/hold [DD10] x6; none/hold [FF20] x2; none/hold [SS1] x1; none/hold [SS8] x1; patrol [DD20] x10; raid [SS10] x3; reserve [BB4 SSC3] x1; reserve [CV7 BB10 CA6 DD63 FF14] x1
- **SOV**: escort [FF18] x1; none/hold [CA3 CL5] x1; none/hold [SSC1] x8; raid [SS10] x5; raid [SSC10] x1; raid [SSC5] x1; raid [SSC8] x1; raid [SSC9] x1; reserve [BB1 SSC1] x1; reserve [BB2] x1; reserve [DD3] x1; reserve [SS1] x1; reserve [SS4] x1

### 1944.3.1.2 (autosave_31.hoi4)

| tag | total by type | meets 2CV+2BB+10CL | ships active (patrol/strike/raid/escort/inv) | idle none/hold | train | reserve | TFs by mission |
|---|---|---|---|---|---|---|---|
| GER | BB2 CA6 CL8 SS3 FF12 SSC88 DD16 (n=135) | False | 92 | 35 | 0 | 8 | none/hold:5, patrol:1, raid:8, reserve:2 |
| ITA | BB6 CA4 CL19 DD26 SSC1 SS8 (n=64) | False | 30 | 9 | 0 | 25 | none/hold:1, patrol:2, raid:1, reserve:2 |
| JAP | CV10 BB7 BC4 CVL5 CA21 CL40 DD209 FF91 SSC8 SS46 (n=441) | True | 222 | 173 | 0 | 46 | none/hold:6, patrol:8, raid:7, reserve:1 |
| ENG | CV10 BB18 BC2 CVL2 CA12 CL69 DD416 FF224 SS16 SSC14 (n=783) | True | 390 | 131 | 0 | 262 | escort:8, mine5:1, none/hold:5, patrol:10, raid:3, reserve:5 |
| FRA | CV1 BB3 DD3 FF4 SS3 SSC5 (n=19) | False | 5 | 0 | 0 | 14 | raid:1, reserve:3 |
| USA | BB22 CV18 BC2 CA17 CL38 DD403 SSC3 FF84 SS7 (n=594) | True | 303 | 177 | 0 | 114 | escort:9, none/hold:12, patrol:10, raid:1, reserve:2 |
| SOV | BB3 CA3 CL5 SSC50 SS55 DD3 FF18 (n=137) | False | 107 | 9 | 0 | 21 | escort:1, none/hold:2, raid:9, reserve:5 |

Task-force detail (grouped: mission x composition -> count of TFs)

- **GER**: none/hold [CA4 CL8] x1; none/hold [FF12] x1; none/hold [SSC1] x2; none/hold [SSC9] x1; patrol [DD16] x1; raid [SSC10] x4; raid [SSC9] x4; reserve [BB2 CA2 SS3] x1; reserve [SSC1] x1
- **ITA**: none/hold [CA1 CL8] x1; patrol [DD12] x2; raid [SS6] x1; reserve [BB6 CA2 CL11 DD2 SSC1 SS2] x1; reserve [CA1] x1
- **JAP**: none/hold [BC2 CA4 CL12] x1; none/hold [CV4 BB7 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x4; patrol [DD20] x8; raid [BC2 CA6] x1; raid [SS10] x3; raid [SS7] x1; raid [SS9] x1; raid [SSC8] x1; reserve [CV6 CVL1 CA1 CL8 DD19 FF11] x1
- **ENG**: escort [CVL1 FF20] x1; escort [FF19] x1; escort [FF20] x6; mine5 [FF6] x1; none/hold [BC2 CA2 CL12] x1; none/hold [CV4 BB8 CA10 CL20 DD30] x1; none/hold [CVL1 FF20] x1; none/hold [FF2] x1; none/hold [FF20] x1; patrol [DD20] x10; raid [SS10] x1; raid [SSC7] x2; reserve [BB1] x1; reserve [CV3 BB9 CL20 DD46] x1; reserve [CV3 CL17 DD97 FF16 SS6] x1; reserve [DD43] x1; reserve [FF1] x1
- **FRA**: raid [SSC5] x1; reserve [BB2 FF3 SS2] x1; reserve [CV1 BB1 DD3] x1; reserve [FF1 SS1] x1
- **USA**: escort [DD10] x7; escort [DD8] x1; escort [FF20] x1; none/hold [BC2 CA4 CL12] x1; none/hold [CV4 BB6 CA5 CL20 DD30] x1; none/hold [DD1] x2; none/hold [DD10] x3; none/hold [FF20] x3; none/hold [SS1] x2; patrol [DD20] x10; raid [SS5] x1; reserve [BB4 DD55 SSC3] x1; reserve [CV14 BB12 CA8 CL6 DD8 FF4] x1
- **SOV**: escort [FF18] x1; none/hold [CA3 CL5] x1; none/hold [SSC1] x1; raid [SS10] x5; raid [SSC10] x3; raid [SSC9] x1; reserve [BB1 SSC5 SS1] x1; reserve [BB2] x1; reserve [DD3] x1; reserve [SS4] x1; reserve [SSC5] x1

## Q-N3 (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1) - ratio = sum(enemy strength) / own strength, monthly

| tag | war-months | superior | neutral | inferior | flips | flaps(<=3mo) |
|---|---|---|---|---|---|---|
| GER | 53 | 0 (0%) | 0 (0%) | 53 (100%) | 0 | 0 |
| ITA | 49 | 4 (8%) | 1 (2%) | 44 (90%) | 3 | 1 |
| JAP | 79 | 52 (66%) | 0 (0%) | 27 (34%) | 1 | 0 |
| ENG | 53 | 26 (49%) | 27 (51%) | 0 (0%) | 1 | 0 |
| FRA | 53 | 8 (15%) | 0 (0%) | 45 (85%) | 1 | 0 |
| USA | 27 | 0 (0%) | 27 (100%) | 0 (0%) | 0 | 0 |
| SOV | 35 | 2 (6%) | 1 (3%) | 32 (91%) | 3 | 1 |

### GER (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: none
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1944.3.1 | inferior | 6.79-16.85 | 173..193 | 1346..3253 |

### ITA (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1940.7.1 sup->inf; 1943.11.1 inf->neu; 1943.12.1 neu->inf
Flaps: 1943.11.1..1943.12.1

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1936.2.1 | 1936.5.1 | superior | 0.00-0.00 | 234..247 | 0..0 |
| 1940.7.1 | 1943.10.1 | inferior | 3.18-10.17 | 412..288 | 1610..2925 |
| 1943.11.1 | 1943.11.1 | neutral | 0.80-0.80 | 287..287 | 230..230 |
| 1943.12.1 | 1944.3.1 | inferior | 6.60-6.73 | 172..172 | 1135..1158 |

### JAP (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1942.1.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1937.9.1 | 1941.12.1 | superior | 0.04-0.05 | 479..678 | 23..26 |
| 1942.1.1 | 1944.3.1 | inferior | 3.46-3.80 | 684..814 | 2397..3093 |

### ENG (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1942.1.1 sup->neu
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1941.12.1 | superior | 0.19-0.65 | 891..1012 | 173..614 |
| 1942.1.1 | 1944.3.1 | neutral | 0.84-1.27 | 1011..1247 | 1285..1158 |

### FRA (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1940.7.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.6.1 | superior | 0.49-0.50 | 349..372 | 173..182 |
| 1940.7.1 | 1944.3.1 | inferior | 1.58-23.51 | 374..55 | 590..1158 |

### USA (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: none
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1942.1.1 | 1944.3.1 | neutral | 0.98-1.41 | 926..1116 | 1285..1158 |

### SOV (weighted CV/BB/BC=10, CA/CVL=5, CL=3, DD/FF/SS/SSC=1)

Flips: 1941.7.1 sup->inf; 1943.11.1 inf->neu; 1943.12.1 neu->inf
Flaps: 1943.11.1..1943.12.1

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.1.1 | superior | 0.06-0.08 | 224..225 | 13..19 |
| 1941.7.1 | 1943.10.1 | inferior | 2.42-3.16 | 241..181 | 611..517 |
| 1943.11.1 | 1943.11.1 | neutral | 1.27-1.27 | 181..181 | 230..230 |
| 1943.12.1 | 1944.3.1 | inferior | 1.85-1.88 | 182..186 | 343..344 |

## Q-N3 (plain hull count) - ratio = sum(enemy strength) / own strength, monthly

| tag | war-months | superior | neutral | inferior | flips | flaps(<=3mo) |
|---|---|---|---|---|---|---|
| GER | 53 | 0 (0%) | 0 (0%) | 53 (100%) | 0 | 0 |
| ITA | 49 | 4 (8%) | 0 (0%) | 45 (92%) | 1 | 0 |
| JAP | 79 | 52 (66%) | 0 (0%) | 27 (34%) | 1 | 0 |
| ENG | 53 | 27 (51%) | 26 (49%) | 0 (0%) | 3 | 1 |
| FRA | 53 | 8 (15%) | 0 (0%) | 45 (85%) | 1 | 0 |
| USA | 27 | 0 (0%) | 27 (100%) | 0 (0%) | 0 | 0 |
| SOV | 35 | 2 (6%) | 1 (3%) | 32 (91%) | 3 | 1 |

### GER (plain hull count)

Flips: none
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1944.3.1 | inferior | 5.94-14.52 | 115..135 | 834..1941 |

### ITA (plain hull count)

Flips: 1940.7.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1936.2.1 | 1936.5.1 | superior | 0.00-0.00 | 160..169 | 0..0 |
| 1940.7.1 | 1944.3.1 | inferior | 1.59-17.68 | 273..64 | 1009..656 |

### JAP (plain hull count)

Flips: 1942.1.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1937.9.1 | 1941.12.1 | superior | 0.03-0.04 | 247..355 | 9..10 |
| 1942.1.1 | 1944.3.1 | inferior | 3.96-4.14 | 359..441 | 1453..1814 |

### ENG (plain hull count)

Flips: 1942.1.1 sup->neu; 1943.11.1 neu->sup; 1943.12.1 sup->neu
Flaps: 1943.11.1..1943.12.1

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1941.12.1 | superior | 0.22-0.75 | 525..610 | 115..388 |
| 1942.1.1 | 1943.10.1 | neutral | 0.92-1.19 | 615..749 | 733..702 |
| 1943.11.1 | 1943.11.1 | superior | 0.79-0.79 | 759..759 | 598..598 |
| 1943.12.1 | 1944.3.1 | neutral | 0.83-0.84 | 766..783 | 641..656 |

### FRA (plain hull count)

Flips: 1940.7.1 sup->inf
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.6.1 | superior | 0.51-0.52 | 225..237 | 115..124 |
| 1940.7.1 | 1944.3.1 | inferior | 1.66-38.58 | 237..19 | 393..656 |

### USA (plain hull count)

Flips: none
Flaps: none

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1942.1.1 | 1944.3.1 | neutral | 1.01-1.36 | 538..594 | 733..656 |

### SOV (plain hull count)

Flips: 1941.7.1 sup->inf; 1943.11.1 inf->neu; 1943.12.1 neu->inf
Flaps: 1943.11.1..1943.12.1

| from | to | posture | ratio range | own | enemies' |
|---|---|---|---|---|---|
| 1939.11.1 | 1940.1.1 | superior | 0.06-0.07 | 179..180 | 13..11 |
| 1941.7.1 | 1943.10.1 | inferior | 1.68-2.68 | 192..132 | 393..280 |
| 1943.11.1 | 1943.11.1 | neutral | 1.30-1.30 | 132..132 | 172..172 |
| 1943.12.1 | 1944.3.1 | inferior | 1.57-1.61 | 133..137 | 214..215 |
