# Posture offensive : analyse d'impact « verdict par ennemi vs verdict par théâtre »

Analyse d'impact (AGENTS.md principe 3, étapes a–g) du système de posture offensive, sans
modification du code. Session du 2026-09-22, campagne `e953ae9b`, saves locales
`battleplan_france.hoi4` (1945.3.20) et `battle_plan2.hoi4` (1945.8.11). Aucun sujet ajouté à
`WORK.md` ; la cause première du symptôme est déjà portée par `britain-buffer-release`.

Labels : **MEASURED** = lu dans une save, un fichier du mod ou du jeu (source nommée) ;
**DERIVED** = calculé à partir d'un MEASURED ; **ASSUMED** = non vérifié.

Sources principales : `common/scripted_effects/WA_AI_MILITARY_posture_effects.txt` (le calcul),
`common/scripted_triggers/WA_AI_MILITARY_posture_triggers.txt` (les interrupteurs),
`common/script_constants/wa_ai_posture.txt` (les seuils),
`common/ai_strategy/WA_AI_MILITARY_DEFAULT_FRONT_posture.txt` (le consommateur),
`common/ai_strategy/documentation.info` § `front_control` (le moteur).

---

## 0. Verdict

**Le pairwise seul n'est pas ce qui a livré le niveau 1 dans la save du symptôme.** Au 1945.8.11
la branche LOCALE le livre aussi, par sa bande de maintien (rapport coalition/GER toutes zones
de contact = **1,20**, au-dessus de `local.ratio_hold` 1,1, entrée déjà faite au 1945.3 à 1,77).
L'option A ne changerait donc rien au verdict mesuré. **DERIVED** des comptes du §2.

**La somme multi-théâtres masque bien un théâtre inversé**, mais ce n'est pas l'Ouest : l'Ouest
lit 1,06 (parité, pas d'infériorité), la Poméranie/Dantzig lit **0,24** (26 divisions allemandes
contre 8 polonaises) et l'Italie lit « ∞ » (28 divisions alliées face à 0 division allemande,
les états y sont tenus par la RSI). **MEASURED** §2.

**Un niveau 3 (careful) à l'Ouest produirait moins d'attaques, pas plus** : `careful` relève le
score minimal d'attaque de 0 à 25 (`PLAN_EXECUTE_CAREFUL_LIMIT`, `00_defines.lua:1078-1079`,
non surchargé). Le zéro attaque de l'Ouest est un problème de masse (81 divisions US parquées en
Angleterre, sujet `britain-buffer-release`) puis d'arbitrage moteur à parité, pas de verdict.

**Recommandation unique : ne pas modifier le calcul maintenant** ; re-scorer sur une save
postérieure à `britain-buffer-release` ; si cette save montre encore un membre de coalition en
exécution `balanced` dans un théâtre lu sous 1,0, la conception à admettre est l'option C2 (§6),
un `front_control` careful **par grappe d'états de contact** via `state_trigger`, dont la
faisabilité se prouve par une sonde console avant toute ligne de code.

---

## 1. Le symptôme en six boîtes (skill `wa-diagnosis`)

| # | Boîte | Contenu |
| --- | --- | --- |
| 1 | **Symptôme** | Aucune attaque alliée en cours à l'Ouest alors que USA et ENG portent `posture_vs_GER = 1` (exécuter, `balanced`) et que le bloc `WA_AI_MILITARY_DEFAULT_FRONT_posture_execute` est armé (capture owner `imgui show ai-strategy`). |
| 2 | **Mesure** | **MEASURED** `battle_plan2.hoi4` 1945.8.11 : ligne Ouest 17 états GER 64 / USA 31 / ENG 28 / FRA 2, 0 attaque alliée sur 19 combats mondiaux (session du 2026-09-22, WORK.md L181-186). Reconstruction du compte que l'effet voit (§2, sous-agent, `plans.scan` + adjacence `WA_AI_MAP_*`) : USA vs GER **toutes zones 113 vs 94 bandé = 1,20**, Ouest seul 56 vs 53 = 1,06. |
| 3 | **État du mod** | **MEASURED** (`savegame.py var TAG "posture"`) : USA `posture_vs_ger = 1` (agrégat 3, porté par des entrées `vs_ita = 3` / `vs_jap = 3`), ENG `vs_ger = 1`, SOV `vs_ger = 1`, GER agrégat **0** avec `WA_AI_AIFC_hold_the_line` posé le 1945.8.7 (`wa_ai_fielded_eq_ratio` 0,880 < `enter.min_eq` 0,9 + `home_threatened`). `WA_TLM_r51_local_hold_n` USA = 19, dernier tampon t = 102 (la save est à t = 115). |
| 4 | **Décision du mod** | **DERIVED** : au 1945.8 `_post_local_ok = 1` par la bande de maintien (`WA_AI_MILITARY_posture_vs_GER > 0` ∧ 113 > 94 × 1,1 = 103,4) ; `_post_local_inferior = 0` (113 > 94 × 1,0) ; le pairwise n'est pas l'unique route (le tampon R51, qui ne compte que les niveaux 1 livrés par la bande de maintien AVEC pairwise en échec, s'est arrêté à t = 102 : après, soit le pairwise passe, soit le local dépasse 1,5). Niveau 1 → bloc execute `balanced`. |
| 5 | **Ligne de script** | `WA_AI_MILITARY_posture_effects.txt:511-523` (`_post_local_ok`, somme toutes zones), `:527-541` (`_post_local_inferior`, même somme), `:575-593` (échelle 1/3) ; consommateur `WA_AI_MILITARY_DEFAULT_FRONT_posture.txt:34-44` (un `country_trigger` par ennemi, donc un seul type d'exécution pour tous les fronts contre GER). |
| 6 | **Frontière moteur** | **ASSUMED** : pourquoi un ordre `balanced` armé n'attaque pas à 1,06. Le moteur exige un score de plan ≥ 0 (`PLAN_EXECUTE_BALANCED_LIMIT`), un avantage ≥ 0,5 contre une ligne « heavily defended » (`ATTACK_HEAVILY_DEFENDED_LIMIT`, `00_defines.lua:2871`), une org ≥ 0,75 pour `balanced` (`PLAN_ATTACK_MIN_ORG_FACTOR_MED`, surcharge WA `05_defines.lua:1401`) ; le score de plan lui-même n'est pas observable. |

Diagnostic COMPLET : la boîte 5 est remplie ; la boîte 6 nomme ce que le save ne montre pas.

---

## 2. Mesures : ce que l'effet voit réellement (sous-agent d'extraction)

Méthode (sous-agent, MEASURED sauf mention) : divisions par état via `plans.scan`
(`location=` → état par `WA_AI_MAP_state_provinces`), contrôleurs via le parseur de `control`,
adjacence via `WA_AI_MAP_province_connections`, échelle bandée et bonus mobile transcrits de
`WA_AI_MILITARY_posture_count_state_divs` (`posture_effects.txt:806-846`). Test de clôture
PASSÉ : la somme par état = `army deployed` pour les 12 pays (USA 291 = 216 + 75 en mer).
**ASSUMED** : le classement blindé/mécanisé par famille de bataillon majoritaire
(`plans.template_family`) tient lieu de `divisions_in_state type =`.

### 2.1 `battle_plan2.hoi4` 1945.8.11, ROOT = USA, ennemi = GER (« notre côté » = 33 membres des Nations Unies en guerre avec GER, ITA/FRA/POL/CAN/ENG inclus)

| Théâtre (états GER de contact ↔ nos états) | États GER | GER brut (blindés) | GER bandé | Alliés brut (bl./méca.) | Alliés bandé | Rapport (DERIVED) |
| --- | --- | --- | --- | --- | --- | --- |
| OUEST (8, 21, 28, 32, 35, 42, 735, 790 ↔ 6, 17, 18, 20, 22, 34, 800, 979, 985) | 8 | 46 (16) | 53 | 49 (8/9) | 56 | **1,06** |
| EST / Poméranie (63, 85 ↔ 86, 797) | 2 | 26 (1) | 29 | 8 (0/0) | 7 | **0,24** |
| BALKANS (105, 108 ↔ 103, 104, 913) | 2 | 10 (1) | 12 | 18 (1/0) | 19 | 1,58 |
| ITALIE (2, 157 tenus par RIT ↔ 117, 986) | 2 | **0** | **0** | 28 (3/1) | 31 | ∞ |
| **TOUTES ZONES (ce que le code somme)** | **14** | 82 | **94** | 103 | **113** | **1,20** |

Seuils (`wa_ai_posture.txt:34-45`) : entrée 1,5 / maintien 1,1 / infériorité 1,0 / maintien
infériorité 1,2. Le plafond `local.max_states` 40 n'est jamais atteint (max 18 états).

### 2.2 Même save, autres paires

| Paire | États ennemis | Ennemi bandé / nôtre | Rapport | Lecture |
| --- | --- | --- | --- | --- |
| SOV vs GER, EST seul | 10 | 61 / 139 | **2,28** | entrée franche |
| SOV vs GER, toutes zones | 16 | 72 / 199 | 2,76 | idem |
| GER vs SOV | 18 | 170 / 94 | **0,55** | infériorité → niveau 3 attendu (verdict réel 0 : frein dur) |
| GER vs USA | **0** | 0 / 0 | n/a | **aucun état de contact** : USA ne contrôle aucun état européen (les états libérés sont FRA/ENG/ITA/POL) |
| GER vs ENG | 3 | 11 / 14 | 1,27 | |
| JAP vs CHI | 14 | 61 / 132 | 2,16 | verdict réel 0 : `eq` 0,882 < 0,9 (`_post_bars_ok = 0`) |
| CHI vs JAP | 16 | 147 / 202 | 1,37 | verdict 1 (agrégat) ; `vs_jap` lu 0 |
| USA vs JAP | 8 | 21 / 35 | 1,67 | verdict 3 |

### 2.3 `battleplan_france.hoi4` 1945.3.20

| Paire / théâtre | États ennemis | Ennemi bandé / nôtre | Rapport |
| --- | --- | --- | --- |
| USA vs GER, OUEST | 12 | 70 / 96 | **1,37** |
| USA vs GER, ITALIE | 2 | 0 / 28 | ∞ |
| USA vs GER, toutes zones | 14 | 70 / 124 | **1,77** (entrée > 1,5) |
| SOV vs GER, EST | 13 | 117 / 194 | 1,66 |
| SOV vs GER, toutes zones | 15 | 118 / 199 | 1,69 |
| GER vs SOV | 11 | 244 / 193 | 0,79 (niveau 3 ; verdict réel GER agrégat 3, `vs_sov` 0) |
| USA vs JAP | 11 | 33 / 29 | 0,88 |

### 2.4 Trois angles morts mesurés en passant (observations, pas de sujet)

1. **GER lit 0 état de contact contre USA** dans les deux saves : la passe 1
   (`posture_effects.txt:277-299`) marche les états contrôlés par l'ENNEMI ; un ennemi
   expéditionnaire qui ne contrôle aucun sol lit une ligne vide, et la branche locale ne peut ni
   entrer ni freiner (commentaire `:397-399`). Même forme GER vs FRA au 1945.3 (7 états FRA de
   contact, 57 divisions alliées dont 0 française).
2. **54 divisions allemandes stationnées sur des états contrôlés par SOV** (89 Stanisławów 17,
   69 Sudètes 10, 996 Brandebourg-Nord 9, 152 Haute-Autriche 7…, `control` sans contradiction de
   province) ne sont comptées par personne : elles ne sont pas dans `every_controlled_state` de
   GER, donc `_post_local_enemy` de SOV (72) sous-estime les Allemands au contact d'environ 75 %.
3. **L'Italie gonfle le rapport USA vs GER de 94→113 à 94→82 sans elle** : les deux états de
   contact (Latium, Abruzzes) sont tenus par la RSI, sujet de GER ; la passe ennemie ne compte que
   les divisions de CET ennemi (simplification documentée `:258-260`), la passe amie compte les 28
   divisions alliées en face.

---

## 3. Étape (a) : lecteurs et appelants

`grep` sur `WA_AI_MILITARY_posture_vs_`, `should_posture_`, `posture_execute|careful|pursuit`,
`WA_AI_MILITARY_posture`, `WA_AI_AIFC_hold_the_line` dans `common/` et `events/` (MEASURED).

| Lecteur | Fichier:ligne | Ce qu'il lit | Cadence |
| --- | --- | --- | --- |
| Écrivain unique | `WA_AI_misc_on_actions.txt:174` → `WA_AI_MILITARY_update_posture` | — | hebdo, bloc `is_ai` + `has_capitulated = no` |
| Famille Default (3 blocs) | `WA_AI_MILITARY_DEFAULT_FRONT_posture.txt:42,73-74,104` | `posture_vs_@PREV` = 1 / 2-3 / 4 dans un `country_trigger` | réévaluation moteur de l'`enable` (ASSUMED quotidienne) + `country_trigger` par candidat |
| Portes des 3 blocs | `WA_AI_MILITARY_FRONT_gate_triggers.txt:3455-3476` | `posture_has_execute/careful/pursuit_target` (`posture_triggers.txt:187-221`) | idem |
| Slug d'ownership | `WA_AI_MILITARY_ownership_triggers.txt:314-343` (`country_owns_front_control_scripted_opening`) | fait céder la famille aux ouvertures JAP/ITA/SOV | idem |
| SOV counterattack | `WA_AI_MILITARY_FRONT_gate_triggers.txt:1917` → `COUNTRY_SOV_FRONT.txt:702-724` | `posture_vs_GER > 0` (tag littéral, Country layer) | idem |
| JAP Ichi-Go | `FRONT_gate_triggers.txt:1466,1481` → `COUNTRY_JAP_FRONT.txt:299-320` | `posture_vs_CHI > 0` | idem |
| Allies downfall | `FRONT_gate_triggers.txt:2959` → `FACTION_ALLIES_FRONT.txt:552-574` | `posture_vs_JAP > 0` | idem |
| ITA Afrique du Nord / Afrique de l'Est | `WA_AI_MILITARY_triggers.txt:451,2208` (`north_africa_offensive_viable`, `east_africa_offensive_viable`) | `posture_vs_@PREV > 0` | idem |
| AIFC | `WA_AI_AIFC_triggers.txt:190` (`hold_the_line`) ; `:107` interdit explicitement de lire `WA_AI_MILITARY_posture` | drapeau | 5 jours |
| Frein bas équipement | `WA_AI_MILITARY_DEFAULT_FRONT_control.txt:57-73` (priorité 500) | drapeau `WA_AI_defensive_front_strategy` | moteur |
| Harnais | `WA_TEST_posture.txt:208`, `events/wa_test_posture.txt` | tout | console |
| Télémétrie | `WA_TLM_post_*`, `WA_TLM_r51_*` (`posture_effects.txt:595-613, 676-703`) | écriture seule | hebdo |

Tout lecteur consomme un **niveau par ennemi** ; aucun ne connaît un théâtre. Une option qui
publie un niveau par théâtre doit soit garder la variable par ennemi (compat), soit réécrire les
9 sites ci-dessus.

## 4. Étape (b) : populations et cadences atteintes

| Population | Atteinte | Par quoi |
| --- | --- | --- |
| Tout pays IA en guerre non capitulé | calcul hebdo | `WA_AI_MILITARY_should_update_posture` (`posture_triggers.txt:57-62`) |
| Chaque ennemi major ou > 4 états | un verdict | `every_enemy_country` limit (`posture_effects.txt:192-200`) |
| USA / ENG / FRA / CAN / POL / ITA (UN) vs GER | même compte local (même coalition) | §2.1 : ITA vs GER = 1,20 identique à USA |
| SOV (+ MON ROM SIK TUR) vs GER | compte à part | §2.2 |
| JAP vs CHI, CHI vs JAP | idem | ownership `scripted_opening` fait céder la famille à `chinese_war_1-4` |
| ITA vs ETH 1936 | idem, cède aux blocs éthiopiens | ownership |
| Minors (ennemi ≤ 4 états) | pas de verdict, branche « trop petit » = exécuter | `posture_triggers.txt:187-198` |
| Cadences | calcul **hebdo** ; sauvegarde mensuelle ; `enable` moteur ASSUMED quotidien ; AIFC 5 jours ; hystérésis locale 1,5 / 1,1 et 1,0 / 1,2 sur le pas hebdo | |

## 5. Étape (c) : scénarios déroulés

Chaque ligne : ce que fait le code ACTUEL, puis ce que ferait A, puis C2 (§6).

| Scénario | Actuel | Option A | Option C2 |
| --- | --- | --- | --- |
| **SOV 1943-44 vs GER, historique** (MEASURED fork `d1c51a6c` 1945.4 : coalition 224 vs 168 = **1,33**, WORK.md L3172-3173 ; campagne `d1c51a6c` : `vs_ger = 1` sur toutes les saves 1942.9→1945.8) | 1,33 entre 1,0 et 1,5 : niveau 1 par le **pairwise** (probe (iii) PASS, 35 états repris en 26 mois) | A littéral : semaine 1 → 3 (pairwise sans local), semaine 2 → **1** car la bande de maintien teste `posture_vs > 0` et 3 > 0 (`:516-518`) : un retard d'une semaine, rien d'autre. A durci (maintien sur `= 1`) : **niveau 3 pendant tout l'arc** — la régression exacte que la leçon L715-731 interdit | Est à 2,28 (cette campagne) : aucune grappe inférieure, rien ne change |
| **SOV vs GER, cette campagne** (§2.2, 2,76) | niveau 1 par le local | inchangé | inchangé |
| **USA 1944.9 France 59 vs 106** (cas du doc §9, `5d2a391c`) | corrigé par `[posture-v3]` : infériorité < 1,0 → niveau 3 ; sur `d1c51a6c` 1944.9 le bucket Ouest coalition lit 203 vs 128 = 1,59 (WORK.md L3210-3214) | idem actuel | idem, la grappe Ouest n'est pas inférieure |
| **USA 1945.8 cette campagne** (§2.1) | 1,20 → maintien → niveau 1 ; Ouest 1,06 non inférieur | **inchangé** (maintien local passe) | Ouest inchangé ; grappe Poméranie 0,24 → careful pour la coalition là-bas (POL 8 div.) |
| **POL 1945.8 vs GER** | même compte 1,20 → POL ordonne `balanced` avec 8 div. contre 26 : le vrai coût de la somme | inchangé | careful sur la grappe |
| **JAP vs CHI 1944 (Ichi-Go)** | `chinese_war_4` lit `vs_chi > 0` ; cette campagne `vs_chi = 0` (eq 0,882 < 0,9) — porte `_bars_ok`, pas le local | JAP vs CHI local 2,16 : passe de toute façon | inchangé |
| **ITA vs ETH 1936** | ownership `scripted_opening` : famille cédée ; ETH ≤ 4 états → pas de verdict | inchangé | inchangé |
| **Minor contre major, ahistorique** (ex. FIN seule vs SOV) | pairwise échoue toujours (leçon L240-246) ; local seul ; ligne d'un seul théâtre | A ne change rien à un pays qui n'a pas le pairwise | grappe unique = compte actuel |
| **Débarquement avant contact** (USA 1943, aucun état de contact) | ligne vide : `_post_local_enemy = 0`, aucune branche locale ; verdict = pairwise (`:397-399`) | **A littéral → niveau 3 pour tout ennemi séparé par la mer**, `posture_careful` armé sur un pays sans front terrestre (inoffensif mais faux) ; A doit garder la garde `_post_local_enemy > 0` de `:531` | sans grappe : inchangé |
| **GER vs USA** (§2.4-1, 0 état) | pairwise seul par construction | 3 permanent | inchangé |
| **Ahistorique, pays hors faction vs major** | famille Default (`[posture-v3]`) ; coalition = lui seul | idem A | idem |

## 6. Les options

### 6.1 Option A — le pairwise seul ne donne plus le niveau 1

Périmètre : `posture_effects.txt:575-593` (échelle) ; conserver `is_major` et `_post_local_enemy
> 0` (`:529-531`) ; durcir la bande de maintien `:516-518` sur `= 1` (sinon A est un retard d'une
semaine, §5 ligne 1).

| Étape | Résultat |
| --- | --- |
| (d) leçons / slugs cassés | L240-246 (« pairwise is pairwise ») respectée ; **L715-731** (arc SOV 1943-44, « a brake whose release cannot be met by getting stronger is a death spiral ») **CASSÉE** par A durci : 1,33 ne franchit jamais 1,5 ; `:524-526` (« a scripted opening against a minor must not be turned careful ») à préserver ; `:397-399` (ligne vide) à préserver. Verdict lessons-reviewer : CONCERNS |
| (e) régression | SOV 1943-45 en `careful` sur `d1c51a6c` (1,33) et tout pays fort dont la ligne lit entre 1,0 et 1,5 ; USA de cette campagne inchangé (1,20 > 1,1, entrée faite à 1,77) |
| (f) t0/t1/t2 | voir §7 |
| (g) | Objection du proposant : « à parité locale le pairwise seul suffit ». Réponse : **la mienne la couvre parce que** dans la save citée le local livre aussi le niveau 1 (1,20 > 1,1, §2.1) ; à parité stricte 1,0-1,1 sans entrée préalable, le code ACTUEL donne déjà 3 si < 1,0 et 1 si ≥ 1,0 par pairwise, et c'est le cas SOV 1,33 qui doit rester 1 |

**Écartée.** Elle ne modifie pas le verdict mesuré et régresse l'arc soviétique.

### 6.2 Option B — compter par `ai_area`, un `front_control` par area

| Question | Réponse |
| --- | --- |
| Trigger d'appartenance d'un état à une `ai_area` | **N'existe pas** en PDXScript (MEASURED : aucun `is_in_area`/équivalent dans `documentation.info` ni dans le repo ; les areas ne sont lisibles que comme cible `area =` d'un `ai_strategy`). Alternatives : `region = N` (région stratégique, MEASURED `WA_AI_MILITARY_triggers.txt:194-198`), `is_on_continent`, listes d'états, arrays temp construits par le scan hebdo |
| Coût | un `every_controlled_state` par ennemi existe déjà (≤ 40 états, jamais atteint) ; classer chaque état de contact par region = 1 lookup ; **pas de nouvel `every_state`** |
| Limite 72 areas | **MEASURED** `WA_AI_MILITARY_areas.txt:4-9` : 72 total, 73 plante (`ai_area.cpp`, C0000005) ; 5 alias WA déjà, aucun slot. Réutiliser les 67 areas `default.txt` (`benelux`, `germany`, `prussia`, `east_europe`, `italy`…) est possible mais les areas vanilla se chevauchent (`north_france`/`france`/`west_france`) et 380/381 ont montré qu'un état peut n'être dans aucune area (leçon L2042-2050) |
| Nombre de blocs | un bloc `front_control area = X` par area et par niveau : ~10 areas de contact européennes × 2 niveaux = 20 blocs statiques, chacun avec un `country_trigger` lisant `posture_vs_@PREV_<area>` — variable à **double substitution**, ASSUMED non supportée ; sinon 20 variables nommées par area |
| Précédence | deux entrées `front_control` à 340 contre le même ennemi (une par area) = le cas « résolution par champ ou par bloc » **non résolu** de §6.1.1 (`WA_AI_MILITARY_SYSTEM.md` L220-246) ; la ligne « Exclusive per front » de `DEFAULT_FRONT_posture.txt:21` devient fausse |
| §6.2 ownership | compatible : le slug reste `scripted_opening` dans l'`enable`, pas dans le `country_trigger` ; mais tout front hors area retombe sur… rien (le bloc par ennemi disparaît) : re-création du trou « verdict sans consommateur » (leçon L2006-2013) |
| Verdict lessons-reviewer | **CONFLICT** |

**Écartée.** (g) Objection du proposant : « la somme multi-théâtres masque un théâtre faible ».
Réponse : **la mienne la couvre parce que** C2 découpe par grappe d'adjacence, sans area, sans
slot, sans nouveau bloc par théâtre, et garde le bloc par ennemi comme repli.

### 6.3 Option C2 — careful par grappe d'états de contact via `state_trigger` (la plus petite qui traite le théâtre inversé)

Idée : le scan hebdo existe déjà et possède les deux arrays `_post_enemy_front` /
`_post_our_front`. Il partitionne les états ennemis de contact en **grappes connexes** (BFS sur
`any_neighbor_state`, ≤ 40 états), calcule le rapport bandé par grappe avec la même échelle, et
publie sur ROOT un array persistant `WA_AI_MILITARY_posture_careful_states_ref` (références
d'état encodées, idiome AIFC `WA_AI_AIFC_sector_states_ref`,
`WA_AI_MILITARY_DEFAULT_FRONT_aifc.txt:206-216`) contenant les états ennemis des grappes lues
sous `local.inferior` (avec maintien `inferior_hold`). Le verdict par ennemi ne change pas. Un
4ᵉ bloc Default `WA_AI_MILITARY_DEFAULT_FRONT_posture_careful_cluster`, priorité **345**
(entre execute 340 et pursuit 350), `execution_type = careful`, `manual_attack = yes`,
`state_trigger = { is_in_array = { FROM.FROM.WA_AI_MILITARY_posture_careful_states_ref = THIS.id } }`,
surclasse le `balanced` par ennemi sur ces seuls états.

| Question | Réponse |
| --- | --- |
| `front_control` accepte-t-il `state_trigger` ? | **MEASURED** oui : `documentation.info` § `front_control` (« state_trigger … Scope is state. FROM scope is enemy country FROM.FROM scope is our country »). Le lessons-reviewer l'avait supposé absent ; réfuté par lecture |
| Précédent in-repo | `state_trigger` sur `front_unit_request` (×14) et sur les `force_concentration_*` avec `is_in_array` sur `_ref` ; **aucun sur `front_control`** → ASSUMED que le champ est honoré pour ce type ; l'appariement `is_in_array` + `THIS.id` en `state_trigger` est lui-même encore **non prouvé en moteur** (memory `aifc-armor-steering-scripted`) |
| `ratio = 0.2` | « ratio du front couvert par les cibles » : une grappe de 2 états sur un front de 14 couvre ~14 % de provinces → **ASSUMED** que le bloc grappe doit passer `ratio = 0` (comme `EXEC_low_equipment_hold`) |
| Résolution par champ / par bloc (§6.1.1) | **indifférente ici** : les deux entrées fixent les trois mêmes champs (`execution_type`, `execute_order`, `manual_attack`) ; quelle que soit la règle, l'entrée 345 gagne sur les états de la grappe |
| §6.2 ownership | inchangé : même `enable` que la famille (`should_posture_careful` étendu ou une 4ᵉ porte `should_posture_careful_cluster`), slug `scripted_opening` dans l'`enable` |
| Layer (principe 4) | DECLARATION : deux constantes existantes réutilisées ; OBSERVATION : rien ; DECISION : nouvelle porte `_should_` ; CONSOMMATION : 1 bloc + 1 array publié par l'effet ; aucun tag, aucune date |
| Coût | BFS PDXScript sur ≤ 40 états × adjacence (`every_neighbor_state` + `is_in_array`) une fois par ennemi par semaine ; l'échelle bandée déjà évaluée par état est réutilisée si le comptage est fait par état puis sommé par grappe (accumulateur par grappe = array temp) ; **DERIVED** ≤ 2× le coût du scan actuel, dont le coût réel est lui-même ASSUMED négligeable (WORK.md L3147-3148, jamais mesuré) |
| Hygiène temp | arrays temp nommés (`_post_cluster_id`, `_post_cluster_friendly`, `_post_cluster_enemy`), `break` explicite (leçon L417-432), effacés en fin d'ennemi |
| Régression | (i) une grappe d'UN état ennemi tenu par 1 division isolée face à 0 division amie lit « inférieure » : borner par un plancher `enemy bandé ≥ N` (à déclarer, ex. 8) ; (ii) les 54 divisions GER sur sol SOV (§2.4-2) restent invisibles ; (iii) si `is_in_array`/`THIS.id` ne matche pas, le bloc est un no-op **silencieux** : c'est pourquoi la sonde console précède le code |
| Taille | ~60-90 lignes dans un effet `WA_AI_*` avec harnais → **big change** → extension obligatoire de `WA_TEST_posture.txt` (§8) |
| Verdict lessons-reviewer | « C-state_trigger : CONFLICT until the token oracle is read » → oracle lu, MEASURED ; reste CONCERNS sur l'appariement non prouvé |

**Admise comme conception de repli**, pas comme changement à faire : dans cette campagne son
seul effet mesurable serait de passer POL (8 divisions) en careful sur la Poméranie. L'Ouest
(1,06) ne bouge pas.

### 6.4 Option C-seuil (écartée en deux lignes)

Relever `local.inferior` 1,0 → 1,2 rendrait l'Ouest 1,06 « inférieur »… mais le compte que le
code lit est la somme 1,20, pas l'Ouest. Pour toucher la somme il faudrait `inferior` > 1,2, qui
dépasse `ratio_hold` 1,1 : les deux paires d'hystérésis se chevauchent et un front oscille 1↔3
au pas hebdo (leçon L1168-1181, « move the same distance both ways »). Et cela régresse SOV 1,33.

---

## 7. Étape (f) : tables t0/t1/t2 aux cadences réelles

Cadences : calcul **hebdo** (lundi de pulse) ; `enable` moteur ASSUMED quotidien ; save
mensuelle ; hystérésis locale entrée 1,5 / maintien 1,1, infériorité 1,0 / maintien 1,2.

### 7.1 Option A durcie (maintien sur `= 1`), SOV `d1c51a6c` à 1,33 pairwise OK

| t | Semaine | `vs_GER` | Route | Ordre armé |
| --- | --- | --- | --- | --- |
| t0 | S0 (commit chargé) | 1 (ancien) → recalcul | pairwise OK, local 1,33 < 1,5, maintien exige `= 1` et 1,33 > 1,1 → **1** | execute balanced |
| t1 | S1 | 1 | idem : le maintien tient tant que ≥ 1,1 | balanced |
| t2 | première semaine où le local passe sous 1,1 (renfort GER) | **3** | pairwise OK, pas de local | careful |
| t3 | retour du local à 1,2 | 3 (maintien niveau 1 perdu, entrée 1,5 jamais atteinte) | **piégé en 3** tant que < 1,5 | careful jusqu'à la fin de l'arc |

Le piège t3 est la régression : sous le code actuel t3 relit 1 par le pairwise.

### 7.2 Option A littérale (maintien sur `> 0`), même cas

| t | `vs_GER` | Route |
| --- | --- | --- |
| t0 | 3 | pairwise OK, local 1,33 < 1,5, `vs` = 1 > 0 ∧ 1,33 > 1,1 → **1** (la bande de maintien accepte 1) — en fait 1 dès t0 ; 3 seulement si l'entrée est vierge (`vs` = 0) |
| t1 | 1 | `vs` = 3 > 0 ∧ 1,33 > 1,1 → 1 |

A littérale = un retard d'une semaine pour un pays sans entrée préalable, sinon rien.

### 7.3 Option C2, POL / coalition vs GER, grappe Poméranie 0,24, `battle_plan2` comme t0

| t | Semaine | `vs_GER` (inchangé) | array grappe | Bloc actif sur 63/85 | Ailleurs |
| --- | --- | --- | --- | --- | --- |
| t0 | S0 | 1 | {63, 85} publié (0,24 < 1,0) | **345 careful** dès la réévaluation moteur (≤ 1 j ASSUMED) | 340 balanced |
| t1 | S1-S4 | 1 | maintenu tant que < 1,2 | careful | balanced |
| t2 | save mensuelle | 1 | lisible : `savegame.py var POL "posture_careful_states"` | — | — |
| t3 | renfort allié → 1,25 | 1 | grappe retirée (> 1,2) | 340 balanced | balanced |

Borne : au pire une grappe reste careful 1 semaine de trop (le pas du calcul) ; aucun état
d'oscillation entre deux pulses car l'array n'est écrit qu'au pulse.

---

## 8. Sonde et harnais exigés (règle « big scripted-effect change », AGENTS.md)

Le système a déjà un harnais contrat v1 : `common/scripted_effects/WA_TEST_posture.txt` +
`events/wa_test_posture.txt` (`wa_post.1` rapport, `.2` hebdo on, `.3` tick, `.4` off, à tirer
**depuis l'observateur, jamais après `tag`** : le pulse hebdo est `is_ai`-gaté, MEASURED WORK.md
L3177-3190). Pour C2 il faut, dans l'ordre :

1. **Sonde de faisabilité, avant tout code** (console, owner) : un bloc jetable `front_control`
   `state_trigger = { is_in_array = { FROM.FROM.<array> = THIS.id } }` sur un array publié par
   `wa_post.2`, vérifié dans `imgui show ai-strategy` (bloc listé) ET par un changement
   d'`execution_type` visible sur l'ordre de front de la grappe (fenêtre d'ordre). Sans ce
   résultat, C2 n'est pas admissible : un no-op silencieux est le mode de panne (§6.3 iii).
2. **Extension du harnais** `WA_TEST_posture_report` : une ligne par grappe et par ennemi
   (`cluster k: states=… enemy=… ours=… ratio=… inferior=0/1`), comptée par une marche
   **indépendante** (contrat v1 : pas de helper partagé avec l'effet), et la colonne
   `shipped-cluster` lisant l'array publié. La marche indépendante et l'array doivent bouger
   dans le même sens ; une divergence de direction est le défaut que le harnais existe pour
   attraper.
3. **Probe WA_TLM** (doc §7, écriture seule, `# tlm:` au site) : `WA_TLM_post_cluster_inf_n`
   (compteur : observations hebdo où un ennemi de niveau 1 porte au moins une grappe inférieure),
   `WA_TLM_post_cluster_inf_first_t` / `_last_t` (tampons, contrat d'absence §3.5), enregistrés au
   §5 du doc TLM, init dans `WA_TLM_init_country` + bump de version. Second signal de validation
   : la ligne `cluster` du harnais sur la même save.

Sujet : ne pas l'ouvrir maintenant (WIP 4 déjà dépassé : 8 OPEN/SHIPPED-UNTESTED). S'il est
admis plus tard, `SHIPPED-UNTESTED` jusqu'au collage de la sortie harnais avec `shipped-fresh=1`.

## 9. Critère de clôture campagne

Deux saves d'une campagne portant `britain-buffer-release` :

| Critère | Mesure | Passe si |
| --- | --- | --- |
| Masse (sujet buffer) | `plans.py USA <save> --oob` : 0 ordre type 5 en Angleterre du Sud ; divisions USA sur les états Ouest | Ouest coalition > GER (`>` 1,0 bandé, même méthode que §2) |
| Le verdict n'est pas le frein | `savegame.py var USA "posture"` + attaques en cours (`plans.py --attacks` ou équivalent) | `vs_ger = 1` ET ≥ 1 attaque alliée live à l'Ouest sur la save |
| Théâtre inversé (justifie ou non C2) | même reconstruction par grappe qu'en §2 sur chaque save | aucune grappe < 1,0 avec ≥ 8 divisions ennemies bandées où un membre de coalition exécute `balanced` → C2 **non nécessaire** ; sinon C2 admise avec la sonde §8-1 |

Si, la masse revenue, l'Ouest lit > 1,0 et n'attaque toujours pas, la question suivante est la
boîte 6 (arbitrage moteur : org 0,75, `ATTACK_HEAVILY_DEFENDED_LIMIT` 0,5), pas la posture.

---

## 10. Observations hors sujet (une ligne chacune, aucune admise)

- GER lit 0 état de contact contre un ennemi expéditionnaire (USA, FRA libre) : la passe ennemie
  marche le sol contrôlé par l'ennemi (§2.4-1).
- 54 divisions GER sur sol SOV comptées par personne (§2.4-2) ; l'Italie tenue par la RSI gonfle
  le rapport USA vs GER (§2.4-3).
- Télémétrie : `wa_tlm_post_*` de JAP FROZEN (t 110 dans les deux saves), `post_exec_xr_*` d'ITA
  et de CHI figés alors que `post_last_t` avance (MEASURED sous-agent) — deux formes différentes.
- `WA_AI_defensive_front_strategy` absent des 8 tags dans les deux saves (seuil 0,6 jamais
  franchi) : le frein GER du 1945.8.7 vient de la branche `home_threatened` + eq < 0,9.
- Les entrées `vs_ita = 3` sur USA/ENG/SOV survivent à la défection italienne de 1943.10.30
  (lingering documenté, inerte par `has_war_with`) mais portent l'agrégat USA à 3.
