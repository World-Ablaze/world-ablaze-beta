# Audit — s'inspirer de l'IA navale du Japon de Kaiserreich (Sheep) pour WA

Date : 2026-09-25. Audit en lecture seule, aucun fichier de jeu modifié.
Labels : **MEASURED** = lu dans un fichier (cité) ; **DERIVED** = déduit (source nommée) ;
**ASSUMED** = non vérifié (moteur, pondérations internes).

Rapports détaillés (tables complètes, `fichier:ligne`) dans
`documentation/AI_NAVAL_KR_JAPAN_AUDIT_2026-09-25/` :

| Fichier | Contenu |
| --- | --- |
| `1_kr_sheep_mechanisms.md` | Catalogue des ~50 mécanismes Sheep + KR, classés A/B/C |
| `2_wa_naval_inventory.md` | Inventaire complet de l'IA navale actuelle de WA et de ses trous |
| `3_balance_kr_vs_wa.md` | Defines, stats de navires, spirits : KR vs vanilla vs WA |

Sources : Sheep's KR Japan AI = workshop `3677914657` ; Kaiserreich = `1521695605` ;
install du jeu `C:\Jeux\steamapps\common\Hearts of Iron IV`.

---

## 0. Verdict

1. **DERIVED** — Le Japon de Sheep est bon par **discipline d'invasion**, pas par gestion de flotte :
   il dit au moteur *quand ne pas débarquer*, *où seulement*, *jusqu'où*, et *quoi faire après*.
2. **MEASURED** — L'équilibrage naval de KR est quasi vanilla (coques, modules, convois, doctrines =
   vanilla ; 4 defines IA changées). Les bons résultats ne viennent donc **pas** de l'équilibrage KR.
3. **MEASURED** — Sheep a **supprimé** les leviers de suprématie de KR (`naval_dominance` ×5,
   `naval_invasion_support_priority` ×5, la flotte `JAP_NavalInvasionSupport_1`). Son fichier de defines
   est entièrement commenté.
4. **MEASURED** — WA Historique ne laisse presque rien au moteur pour le Japon : 30 débarquements
   sont *créés* par `create_unit ... allow_spawning_on_enemy_provs` à dates fixes
   (`WA_KDE_AI_effects.txt:37-135`). En Compétitif, aucun débarquement scripté.
5. **DERIVED** — Donc le gain principal pour WA n'est pas « copier le Japon de KR », mais construire
   une **couche d'invasion générique, sans tag**, pour tous les majeurs (Compétitif, après mi-1942,
   Alliés, ITA, GER). C'est exactement le trou du principe 1 (pas de comportement hors chemin historique).

**Kaiserreich a-t-il intégré le sous-mod ?** **MEASURED** Non : aucun fichier ni identifiant `LSM_*`
dans KR. **DERIVED** Mais KR contient déjà le squelette (flag de stagnation, listes `invade -1000`,
whitelist de plages, rush après débarquement) avec le style de nommage de Sheep : KR a absorbé une
version antérieure, le sous-mod est la version étendue.

---

## 1. Catégorie A — Améliorations MÉCANIQUES (portables, indépendantes de l'équilibrage)

Techniques qui marchent par la façon dont le moteur réagit. Classées par impact **ASSUMED**
(la pondération moteur n'est pas observable).

| # | Mécanisme Sheep/KR | Preuve (**MEASURED**) | État WA | Portage WA proposé |
| --- | --- | --- | --- | --- |
| A1 | **Porte « front terrestre bloqué »** : `on_state_control_changed` pose un flag quand un état *intérieur* change de main ; tant que ce flag a < 60 j, ou que le pays a < 80 divisions, `invade` = -1000 sur tous les ennemis | KR `on_actions_Japan.txt:247-261` ; Sheep `LSM_JAP_warplan.txt:350-533` | **MEASURED** absent. WA utilise des fenêtres de dates (`WA_AI_MILITARY_FRONT_gate_triggers.txt:1300-1345`, fin 1942.3.15) | Trigger de décision sans tag `WA_AI_LANDING_should_hold_invasions` : « mon front terrestre avance » OU « trop peu de divisions ». Remplace les dates par l'état du jeu → marche en guerre tardive et ahistorique |
| A2 | **Rush de tête de pont** : `on_naval_invasion` pose un flag d'état 25-30 j ; `front_control` `rush_weak` priorité 200, 8 j sur 14, + `front_unit_request` +4 | KR `on_actions_Japan.txt:263-314` ; warplan:920-991 | **MEASURED** absent : l'`on_naval_invasion` de WA ne sert qu'à la maîtrise marines-cavalerie (`00_on_actions.txt:2386`) | Flag d'état générique + bloc DEFAULT. **DERIVED** entre en conflit avec le gel de 90 j après débarquement scripté (têtes de pont italiennes mortes, campagne 66636ff4) → à régler ensemble |
| A3 | **Clôtures de distance** : `invasion_unit_request` -2000 au-delà de 3000 km d'un état côtier allié, -100 au-delà de 800 km | KR `00_default.txt:557-615` (tous majeurs) ; warplan:992-1183 | **MEASURED** absent (`distance_to` n'apparaît que dans `SPR.txt`) | Bloc DEFAULT sans tag. Coupe les invasions fantaisistes transocéaniques, impose le saut d'île en île |
| A4 | **Filtre population** : `invasion_unit_request` -100 sur `state_population_k < 50` tant que le propriétaire a `surrender_progress < 0.70` | warplan:849-919 | **MEASURED** absent | Bloc DEFAULT sans tag : ignorer les atolls sans valeur jusqu'à l'effondrement |
| A5 | **Reset périodique des invasions bloquées** : -9999 sur invasions pendant 2-3 j tous les 90/120 j quand aucun débarquement récent | warplan:2804-2837 ; KR `00_default.txt:617-647` | **MEASURED** absent | Bloc DEFAULT. **ASSUMED** que -9999 annule les plans existants. **DERIVED** ne corrige pas le blocage Alliés de 30 mois (`WORK.md:97-111`) : là, c'est un cap -100 qui empêche la première tête de pont |
| A6 | **Groupe d'attaque à 1 porte-avions** : `JAP_KidoButai_1` min 1 CV, `keep_updated` | Sheep `ai_navy/taskforce/JAP_taskforce_templates.txt:1-35` | **MEASURED** le seul strike-force WA exige 2 CV + 2 BB + 10 CL (`generic_taskforce_templates.txt:8-19`), et `MIN_CAPITALS_FOR_CARRIER_TASKFORCE` = 10 (vanilla 6) | Template générique plus souple. **ASSUMED** que le minimum actuel empêche souvent le strike-force de se former. `ai_navy` est en `replace_path` → WA possède seul ces fichiers |
| A7 | **Libération des garnisons sur ratio naval** : `garrison` -25 tant que `enemies_naval_strength_ratio < 1.5` ; -1000 hors capitulation | Sheep `JAP.txt:709-778` | **MEASURED** partiel : le trigger existe dans WA mais seulement pour ITA en Méditerranée (`WA_AI_NAVAL_triggers.txt:478-480`) | Généraliser aux archétypes insulaires/navals via CONFIG |
| A8 | **Déprio tête de pont retardée** : `MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS` = 100 | `KR_defines.lua:175` | **MEASURED** WA = 60 (`05_defines.lua:1064`) + durée 270 j (`:1062`) | Passage 60 → 100 : faible risque, IA seulement. Impact analysis requise (valeur WA choisie) |
| A9 | **Entraînement et XP** : `MAX_FULLY_TRAINED_SHIP_RATIO_FOR_TRAINING` 0.99 ; `RESEARCH_WITH_XP_AI_WEIGHT_MULT` 4.0 ; `navy_xp_spend_priority equipment_variant` +500 | `KR_defines.lua:105-106,188` ; Sheep `JAP.txt:323-336` | **MEASURED** WA 0.8 (`:1370`), `XP_RATIO_REQUIRED` déjà 1.0 (`:1581`) | Faible risque, IA seulement |
| A10 | **Échelle de convois** : `equipment_production_min_factories convoy` croissant avec guerre / chantiers | Sheep `JAP.txt:162-225` ; KR `00_naval_production.txt:545-623` | À vérifier dans `WA_AI_PRODUCTION_*` | **DERIVED** d'autant plus utile que WA fait coûter un convoi 700 (vanilla 70) |
| A11 | **Batch d'invasions** : `front_control ordertype invasion execute_order = no` 45 j sur 90 (KR, retiré par Sheep) | KR `JAP.txt:1051-1074` | **MEASURED** absent | Option. **DERIVED** Sheep l'a retiré → valeur incertaine |
| A12 | **Pilotage par faux spirits** : copie d'un spirit, visible IA seulement, `ai_will_do` 5000 — mêmes modificateurs | `LSM_JAP_fake_navy_spirit.txt` | Non audité côté WA | Technique de pilotage, pas triche. Utile seulement si le choix de spirit naval pose problème (non mesuré) |
| A13 | **Défense réactive** : `put_unit_buffers` sur la métropole seulement quand un ennemi *humain* a des paras / une flotte proche | warplan:207-295, 1853-1948 | **MEASURED** absent | Modèle pour l'anti-joueur sans tag |

**Ce qui ne se porte PAS tel quel (piège) :**

| Élément | Pourquoi | Label |
| --- | --- | --- |
| Ajouter `naval_dominance` / `naval_invasion_support_priority` au Japon WA | Sheep a retiré exactement ces lignes de KR pour obtenir son résultat. Le trou « pas de dominance pour JAP » de l'inventaire WA n'est pas la priorité | **DERIVED** du diff KR→Sheep (`K/…/JAP.txt:797-855`) |
| `AREA_DEFENSE_SETTING_COASTLINES = false` (KR) | Define **globale** : toute IA arrête de garder les côtes nues, y compris l'Allemagne face au Débarquement et le Japon sur ses îles | **MEASURED** `KR_defines.lua:183` vs WA `05_defines.lua:1001` ; effet **ASSUMED** |
| Bloc `JAP_oceania_invade_reverse` (`reversed = yes`, `invade id=JAP 1000`) | **ASSUMED** bug de Sheep : lu comme le bloc `reversed` de KR, il pousse les ennemis à envahir le Japon | warplan:1366-1481 |

---

## 2. Catégorie B — Améliorations qui marchent grâce à l'ÉQUILIBRAGE de KR (≠ WA)

À ne pas copier tel quel : leur valeur dépend de stats et d'une économie que WA n'a pas.

| # | Élément KR/Sheep | Preuve (**MEASURED**) | Pourquoi ça ne transpose pas | Label |
| --- | --- | --- | --- | --- |
| B1 | Quotas de construction : destroyers +200 jusqu'à 170, sous-marins +1000 jusqu'à 30, croiseurs ensuite | Sheep `JAP.txt:227-322` | 170 DD est un chiffre de l'économie KR. **MEASURED** WA Japon n'a pas de `unit_ratio` naval, un ratio chantier 40 (`JAP.txt:941`) et un mix `role_ratio` défaut. La *technique* (quota par `has_navy_size`) est A ; les chiffres sont B | **DERIVED** |
| B2 | Designs torpilleurs japonais (DD 2-4 torpilles, CL 2 torpilles, croiseur-torpilleur 4 torpilles) ; designs génériques KR bloqués pour JAP | Sheep `ai_equipment/LSM_japan_*.txt` | Valeur des torpilles = équilibrage de combat. WA a 72 designs JAP propres (`JAP_naval.txt`) et des stats de combat différentes | **ASSUMED** que la torpille vaut moins/plus dans WA ; non mesuré |
| B3 | Sous-doctrines gratuites (`torpedo_primacy`, `long_range_submarines`) par décision IA sans coût | `LSM_JAP_decisions.txt:211-266` | Vraie triche IA (XP non dépensée) ; sa valeur dépend des doctrines WA | **MEASURED** |
| B4 | Focus navals poussés dans les plans (`JAP_maintain_kantai_kessen`, `JAP_improve_the_long_lance`) | Sheep `JAP_strategy_plan.txt` | Récompenses = contenu KR | **MEASURED** |
| B5 | Capacité d'invasion : KR plafond tech 15 div / 9 plans ; JAP +5 et +7 par focus/événement | KR `JAP ideas (Japan).txt:2921,2950` | **DERIVED** WA plafonne à 9 div / 6 plans, base 3 (`05_defines.lua:696`). Augmenter = équilibrage joueur, sauf via `base_ai` / `hard_ai` | **DERIVED** |

**Équilibrage propre à WA qui change le comportement de toute technique importée :**

| Différence WA | Valeur | Conséquence pour l'IA | Label |
| --- | --- | --- | --- |
| Dégâts → pertes de navires | 0.15 vs 0.6 vanilla/KR ; fuite de combat plus rapide (`05_defines.lua:727,874-875`) | Une flotte supérieure ne détruit pas vite la plus faible → la maîtrise de la mer se gagne lentement | **MEASURED** / **DERIVED** |
| Repérage des convois d'invasion | ~4× plus rapide (10 vs 2.4, 0.5 vs 0.12 ; `:730-731`) | Les invasions se font intercepter plus souvent | **MEASURED** |
| Vitesse des flottes | 0.032 vs 0.1 (`:890`) | Réaction navale ~3× plus lente | **MEASURED** |
| Coût d'un convoi | 700 vs 70 (`convoys.txt:41`) | Les convois d'invasion pèsent lourd | **MEASURED** |
| Aides IA déjà présentes | -75 % temps de prépa pour toute IA ; pas de pénalité amphibie en difficile ; JAP +500 % attaque amphibie après Strike South (`_WA_ai.txt:263,297`, `japan.txt:3807-3808`) | WA aide *déjà plus* ses invasions IA que KR | **MEASURED** |

**DERIVED** — Avec combat peu létal et repérage fort, la *discipline* (A1-A5 : ne débarquer
qu'au bon moment, près, puis exploiter) vaut plus dans WA que dans KR, et courir après la dominance vaut moins.

---

## 3. Catégorie C — Spécifique au SCÉNARIO KR (à ré-exprimer, pas à copier)

| # | Élément | Preuve (**MEASURED**) | Noyau réutilisable dans WA |
| --- | --- | --- | --- |
| C1 | Chine d'abord : `area_priority china +300`, `pacific -100`, pas d'aviation embarquée pendant la guerre de Chine | warplan:73-205 | « Une guerre à la fois » par archétype, déjà partiellement exprimée par les fenêtres WA |
| C2 | Whitelist de 8 états à l'embouchure du Yangtsé, `invade` +1005 (×11.05), puis « envahir la Chine une fois » (-1000 dès que Nankin/Nantong tenu) + cooldown 90 j | warplan:596-847 | **Un seul débarquement décisif par cible, puis ravitaillement par terre** — exprimable sans tag avec un flag de tête de pont tenue |
| C3 | Priorité continent en Asie du Sud-Est, îles ensuite | warplan:849-919 | Voir A4 |
| C4 | 16 blocs de ports construits aux points de débarquement (IDs de provinces) | warplan:1949-2803 | Type de projet PC « port de tête de pont » (système PC existant) plutôt que IDs en dur |
| C5 | Passivité des adversaires : GEA évite les mers japonaises si ratio JAP > 0.6 ; les Chinois évitent la mer Jaune +1000 | KR `GEA.txt:199-235`, `china.txt:970-983` | Règle générique « flotte plus faible évite les eaux d'origine d'une plus forte » (`naval_strength_comparison` + `naval_avoid_region`) — effet sur les Alliés WA à analyser |
| C6 | Adversaires faibles : KR JAP 15 chantiers vs USA 32, GEA 0 ; guerre civile US qui scinde la flotte | `01_American Civil War effects.txt:717,1863-2126` | Aucun. **DERIVED** WA JAP 21 vs USA 42, UK 50 : l'adversaire est bien plus fort, donc les résultats KR ne sont pas attendus à l'identique |
| C7 | Raiders surface activés quand Hawaï est tenu (`JAP_DeathSquad_1`) | Sheep taskforce:55-83 | « Activer un template raider quand une base avancée est tenue » |

---

## 4. Où WA doit appliquer ça (DERIVED de l'inventaire WA)

| Situation WA | Aujourd'hui | Ce que la couche A apporterait |
| --- | --- | --- |
| Japon Historique 1938-1942 | Débarquements créés par script, contrôle naval jamais vérifié contre une IA | Peu : le calendrier court-circuite le moteur. Ne pas y toucher d'abord |
| Japon après mi-1942 | Plus de plan : les murs de régions tombent, rien ne les remplace | A1-A4 donnent un comportement par défaut |
| Japon en Compétitif / guerre tardive | Aucun débarquement scripté ; fenêtres fermées au 1942.3.15 ; un débarquement manqué n'est pas rejoué | A1 remplace les dates par l'état → trou du principe 1 comblé |
| Alliés (Torch, Italie, Débarquement) | 0 ordre d'invasion IA pendant 30 mois (campagne 24933fb9) ; têtes de pont qui meurent sous le gel | A2 (rush) + réglage du gel ; A5 ne suffit pas pour le blocage de 30 mois |
| Tous majeurs | Pas de clôture de distance, pas de filtre population | A3, A4 |

---

## 5. Recommandation

Ordre proposé (chaque ligne = un sujet candidat ; **aucun n'est ajouté à `WORK.md`** — admission par le propriétaire) :

| Ordre | Sujet candidat | Catégorie | Coût | Risque |
| --- | --- | --- | --- | --- |
| 1 | `invasion-discipline` : couche DEFAULT sans tag = A1 + A3 + A4 (+ A5) | A | Moyen (on_action + triggers + ai_strategy) | Moyen : interagit avec le gel et la réservation des cibles scriptées ; impact analysis + reviewers obligatoires |
| 2 | `beachhead-exploitation` : A2 + A8, traité **avec** le gel de 90 j | A | Moyen | Moyen : c'est le gel qui a tué l'Italie 1943 |
| 3 | `carrier-strike-template` : A6 (template à 1 CV) | A | Faible | Faible, mais touche tous les pays (template générique) |
| 4 | Defines IA faible risque : A9 | A | Faible | Faible |
| — | Ne pas faire : copier B1-B5, `AREA_DEFENSE_SETTING_COASTLINES = false`, ajouter de la dominance au Japon | B / piège | — | — |

---

## 5b. Ajout — la suprématie d'invasion est faite par le moteur, et WA la rétrograde

**MEASURED** priorités des objectifs navals (`common/ai_navy/goals/goals_generic.txt` ; score d'un objectif
= min + (max - min) × importance, `V/common/ai_navy/_documentation.md`) :

| Objectif | Vanilla | KR | WA |
| --- | --- | --- | --- |
| `naval_invasion_support` | 4-14 | **10-20** | 4-15 |
| `naval_invasion_defense` | 15-25 | 10-18 | 15-25 |
| `convoy_protection` | 1-5 | 1-5 | **15-30** |
| `naval_dominance` | 1-13 | 1-13 | **10-20** |
| `coast_defense` | 1-16 | 1-12 | 5-16 |
| `training` / `naval_blockade` | 10-20 | 10-20 | 10-20 |

- **DERIVED** KR met le soutien d'invasion en tête (10-20) ; WA le met sous l'escorte de convois : le max
  du soutien d'invasion (15) = le min de l'escorte (15). La flotte WA sert d'abord les convois, puis la
  dominance générale, et le soutien d'invasion reçoit le reste.
- **ASSUMED** que cela explique une partie des invasions IA sans couverture (Alliés 30 mois sans ordre,
  têtes de pont perdues) ; aucun save ne le montre encore.
- **MEASURED** leviers moteur de dominance sur le trajet d'invasion (vanilla, non surchargés par KR ni WA) :
  `PATROL_FLEETS_PER_INVASION_REGION_ON_PATH = 2`, `AI_MIN_DOMINANCE_MARGIN = 200`,
  `DOMINANCE_CONTROLLED_THRESHOLD_RATIO = 0.60` (`00_defines.lua:3564-3565,1729`).
- **MEASURED** WA lance les plans d'invasion à une valeur bien plus basse : `MIN_INVASION_PLAN_VALUE_TO_EXECUTE`
  0.05 (`05_defines.lua:1379`) vs 0.3 vanilla/KR.

---

## 6. Anomalies relevées en passant (hors sujet, une ligne chacune)

| Anomalie | Label |
| --- | --- |
| Les blocs Mediterranean Fleet écrivent `naval_dominance` 500 (`WA_AI_NAVAL_FACTION_ALLIES.txt:741,766`) ; `WA_AI_MILITARY_SYSTEM.md` §21 dit 80/70 ; le moteur documente 0-100 % | **MEASURED** ; effet au-delà de 100 **ASSUMED** |
| La porte historique des navires capitaux (`WA_AI_PRODUCTION_navy.txt:136-151`) contredit son commentaire | **MEASURED** ; l'intention **ASSUMED** |
| Le jeu installé est 1.19.3.0 (`launcher-settings.json`), AGENTS.md dit 1.19.2 | **MEASURED** (par le sous-agent) |
