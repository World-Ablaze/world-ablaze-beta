# Proposition — faire cohabiter invasions scriptées et invasions « organiques »

Date : 2026-09-25. **Implémenté** sur la branche `ai-rework-naval-invasion` (sujet `naval-invasion-discipline`, spec `WA_AI_MILITARY_SYSTEM.md` §27 - la spec fait foi là où elle diffère d'ici : R1 par théâtre sans test de capacité, règles organiques inactives sous revendication scriptée, B3 retiré, fenêtre R5 7 j). Suite de
`documentation/AI_NAVAL_KR_JAPAN_AUDIT_2026-09-25.md`.
Labels : **MEASURED** (lu, cité) / **DERIVED** (déduit, source nommée) / **ASSUMED** (non vérifié).

---

## 0. Verdict

1. **DERIVED** — Les fenêtres de dates sont un *proxy* de deux conditions : « le front terrestre n'a pas
   besoin de ces divisions » et « on ne disperse pas ». Sheep teste ces deux conditions **directement**.
   On remplace le proxy par les conditions ; les dates restent seulement comme réglage historique.
2. **DERIVED** — Règle de cohabitation unique : **le calendrier scripté possède un théâtre tant qu'il y doit
   une opération ; ailleurs, l'organique joue sous 5 règles de discipline.** WA a déjà les deux briques
   « le calendrier possède » (réservation avant, gel après) ; il manque la discipline organique.
3. **DERIVED** — Le levier clé est `on_naval_invasion` : il ne se déclenche que pour un débarquement moteur
   (**ASSUMED** : pas pour `create_unit` du calendrier — à mesurer). Il distingue donc tout seul organique
   et scripté, sans tag ni date.
4. **DERIVED** — Le rush de tête de pont est un ordre de *front*, pas d'invasion : le gel de 90 j ne le
   bloque pas. Il peut donc aussi s'appliquer aux débarquements scriptés (têtes de pont italiennes 1943).

---

## 1. Ce que WA fait aujourd'hui

| Brique | Quand | Effet | Label / source |
| --- | --- | --- | --- |
| Calendrier scripté | Difficulté historique seulement | ~90 opérations créent des divisions sur la plage (`create_unit`) | **MEASURED** `WA_KDE_AI_effects.txt:37-135`, `WA_AI_DIVISION_CREATOR_effects.txt:2681` |
| Réservation (avant) | Tant que le calendrier doit une opération contre un pays | `invasion_unit_request` -200 sur ce pays, toute la faction | **MEASURED** `WA_AI_MILITARY_DEFAULT_INVASION_landing_freeze.txt:136-149` |
| Gel (après) | 90 j après un débarquement scripté, par macro-théâtre WEST / EAST | `invasion_unit_request` -200 sur le théâtre | **MEASURED** même fichier:51-92 ; `WA_AI_LANDING_triggers.txt:51,104-113` |
| Frein « patrie menacée » | `WA_AI_defend_core` ou capitulation > 5 % | -200 sur tous les ennemis | **MEASURED** `WA_AI_MILITARY_DEFAULT_INVASION.txt:11-21` |
| Bonus « surplus » | Majeur en guerre, `can_open_secondary_fronts` (> 100 div, ou > 50 div et 800k hommes) | +40 sur tous les ennemis | **MEASURED** même fichier:25-36 ; `WA_AI_MILITARY_triggers.txt` |
| Fenêtres japonaises | Prep/fire Philippines → Malaisie → Indonésie, 1941.12.1 → 1942.3.15 | `invade` +4000 cible / -2000 autres, `invasion_unit_request` +1000 | **MEASURED** `WA_AI_MILITARY_COUNTRY_JAP_INVASION.txt:52-276`, `WA_AI_MILITARY_FRONT_gate_triggers.txt:1300-1345` |
| Cap allié sans tête de pont | Alliés en guerre avec GER, pas de pied en France | -100 sur tous les ennemis | **MEASURED** `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt:98-111` |

**DERIVED** du tableau : en Historique, les blocs japonais (+1000) et le gel EAST (-200) sont actifs en même
temps que le calendrier ; les invasions organiques japonaises peuvent donc se superposer aux scriptées
(net +800). **ASSUMED** que cela arrive vraiment : à mesurer avant d'y toucher.

---

## 2. L'architecture proposée — 6 règles, par ordre de préséance

Chaque règle = un trigger de décision (`_should_` / `_can_`) dans `WA_AI_LANDING_triggers.txt` (le panneau de
contrôle existant) + un bloc DEFAULT. Aucun tag, aucune date.

| # | Règle | Problème réglé | Mécanique | Source Sheep/KR |
| --- | --- | --- | --- | --- |
| R0 | **Le calendrier possède** (existant, inchangé) | Le moteur ne concurrence pas une opération scriptée | Réservation + gel | — |
| R1 | **Permission organique** | Ressources immobilisées pendant que le front terrestre en a besoin | Permis seulement si : en guerre ; `can_open_secondary_fronts` ; pas `home_threatened` ; **front terrestre immobile depuis 60 j**. Sinon `invasion_unit_request` -200 | G1+G2 (warplan:350-533) |
| R2 | **Une tête de pont à la fois** | Dispersion | Après un débarquement organique (`on_naval_invasion`), flag « gel organique » sur le théâtre, N jours → -200 ailleurs dans ce théâtre ; le moteur nourrit la tête de pont par terre | G7 « invade once » + cooldown 90 j |
| R3 | **Laisse** (toujours active) | Invasions lointaines qui absorbent convois et flotte | -200 si aucun état côtier tenu par moi/ma faction à < 3000 km ; -100 à < 800 km ; -100 sur les états < 50k habitants tant que le propriétaire est < 70 % de capitulation | R1/R2 range fences, G9 |
| R4 | **Exploitation** (organique ET scripté) | Têtes de pont qui meurent sur place | Flag d'état `beachhead` 30 j posé par `on_naval_invasion` **et** par `WA_AI_DIVISION_spawn_invasion` ; `front_control` `rush_weak` sur ces états + `front_unit_request` + | E1-E3 |
| R5 | **Déblocage** | Corps d'armée parqués sur un plan jamais lancé | Si R1 permet depuis > 90 j sans aucun débarquement : impulsion -9999 pendant 2 j tous les 90 j | E5/E6 |
| R6 | **Couverture navale** | Invasion permise mais pas escortée | Voir section 7 (gestion de la flotte, règles N1-N7) | KR goals 10-20 |

### Détail de R1 — le détecteur « front terrestre immobile »

- **MEASURED** Scopes de `on_state_control_changed` : ROOT = nouveau contrôleur, FROM = ancien,
  FROM.FROM = l'état (`common/on_actions/00_on_actions.txt:2017`).
- Effet : si l'état est intérieur (`is_coastal = no`) et que ROOT et FROM sont en guerre, poser
  `WA_AI_LANDING_land_front_moved` sur **ROOT et FROM** (le front bouge pour les deux).
- R1 lit `has_country_flag = { flag = WA_AI_LANDING_land_front_moved days < 60 }`, même idiome que le gel.
- **DERIVED** le coût est un `if` sur un événement déjà très fréquent ; aucune boucle.
- Portée : par **pays**, pas par théâtre, comme Sheep. **Question propriétaire** : l'Allemagne qui avance en
  URSS doit-elle s'interdire toute invasion ailleurs ? (Sheep : oui.)

### Détail de R3 — coût de la laisse

- **MEASURED** `distance_to` = « distance entre deux états », scope STATE (`triggers_documentation.md:2596-2603`).
- **ASSUMED** unité km, point de mesure non documenté.
- Sheep boucle sur `any_state` (tous les états) pour chaque cible candidate. Le fichier du gel exige des
  `state_trigger` très bon marché (`landing_freeze.txt:40-42`). Variante moins chère proposée : boucler sur
  les états contrôlés par `FROM.FROM` (nous) seulement — **ASSUMED** que `ROOT` désigne l'état candidat
  dans un `state_trigger` (c'est l'usage de Sheep, warplan:1010).

### Détail de R4 — pourquoi ça ne heurte pas le gel

- **MEASURED** le gel et la réservation n'agissent que par `invasion_unit_request` (landing_freeze.txt, en-tête).
- **DERIVED** un `front_control ordertype = front` sur un état tenu n'est pas une demande d'invasion : il ne
  passe pas par ce levier. Le gel reste en place (pas de 2e débarquement) et la tête de pont attaque.
- Risque : préséance avec les autres `front_control` (`WA_AI_MILITARY_SYSTEM.md` §6.1). Priorité à choisir
  sous celle des plans faction explicites.

---

## 2b. Intégration scripté / organique — qui gagne dans chaque conflit

**Principe** : le scripté n'est jamais freiné par l'organique ; l'organique cède toujours au scripté dans le
même théâtre ou contre la même cible. Le scripté ne passe pas par le moteur (`create_unit` sur la plage),
donc aucune règle organique ne peut le bloquer.

| Conflit | Garde | Label / source |
| --- | --- | --- |
| Le moteur prépare une invasion contre un pays que le calendrier doit encore attaquer | Réservation : -200 sur ce pays pour toute la faction, jusqu'à la dernière opération prévue + bail | **MEASURED** `landing_freeze.txt:136-149`, `WA_AI_LANDING_effects.txt:227-252` |
| Le moteur ouvre une 2e plage juste après un débarquement scripté | Gel 90 j du macro-théâtre (WEST / EAST) | **MEASURED** `landing_freeze.txt:51-92` |
| Un plan de faction nomme sa propre plage (D-Day +1000) pendant un gel | +1000 bat -200 : voulu (« une opération scriptée qui nomme sa plage passe avant un frein générique ») | **MEASURED** `WA_AI_MILITARY_SYSTEM.md` §10 |
| Difficulté Compétitive (pas de calendrier) | Aucune réservation ni gel posés → l'organique joue seul sous R1-R5 | **DERIVED** : les flags ne sont posés que par l'exécution du calendrier |
| Ressources : un débarquement scripté et un plan organique veulent les mêmes divisions | Pas de conflit de divisions : le scripté crée ses divisions. Il consomme en revanche l'équipement et la main-d'œuvre du stock (`_force_use_equipment_manpower = 1`, `WA_AI_DIVISION_remove_stockpiles`) | **MEASURED** `WA_AI_DIVISION_CREATOR_effects.txt:2754,2780-2781` |
| **Nouveau** R2 : le gel organique se déclencherait aussi sur un débarquement scripté si `on_naval_invasion` le voit | Garde dans l'effet de R2 : ne rien poser si un flag de gel scripté a moins de 2 jours | **ASSUMED** que `on_naval_invasion` ignore `create_unit` ; la garde rend la question sans risque |
| **Nouveau** R4 : rush de tête de pont | S'applique aux deux ; c'est un ordre de front, non bloqué par le gel | **DERIVED** |
| **Nouveau** R1 : permission organique | Ne concerne que l'organique ; le scripté n'est jamais gaté par R1 | **DERIVED** |

**Trois trous trouvés en vérifiant (à corriger dans le plan)** :

| Trou | Pourquoi | Correction |
| --- | --- | --- |
| T1 — les fenêtres japonaises (+1000 sur PHI / MAL / INS) écrasent la réservation (-200) sur les mêmes cibles | En Historique, l'organique japonais vise donc les pays que le calendrier attaque déjà (net +800) — conflit **existant aujourd'hui**, effet **ASSUMED** | L3 : ajouter « cible non réservée » aux gates des fenêtres japonaises, ou avancer L5. Changement de comportement existant → impact analysis |
| T2 — N4 montait le poids de dominance « pendant une opération réservée » | Pendant une réservation, l'organique contre la cible est à -200 : il n'y a pas de trajet d'invasion moteur à couvrir ; le scripté n'a pas besoin de flotte pour débarquer | N4 : poids 100 **seulement** quand R1 permet l'organique |
| T3 — après un débarquement scripté, la tête de pont doit être ravitaillée par mer, mais aucune règle n'y affecte la flotte | Le scripté ne crée pas d'objectif moteur « soutien d'invasion » (**ASSUMED**) | À mesurer d'abord (convois / dominance autour des têtes de pont scriptées dans un save) ; pas de règle sans symptôme |

## 3. Que deviennent les fenêtres de dates

| Étape | Action | Pourquoi |
| --- | --- | --- |
| 1 | Garder les fenêtres japonaises telles quelles | Principe 1 : l'historique peut *régler*, jamais être le seul chemin. R1-R5 deviennent le chemin générique |
| 2 | Mesurer en campagne la superposition organique + scripté (Japon 1941-42) | Section 1 : **ASSUMED** |
| 3 | Si R1-R5 tiennent : remplacer les dates par des phases d'état (cible précédente capitulée / tête de pont tenue) — les triggers `..._malaya_done` / `..._indonesia_done` existent déjà | Guerre tardive, ahistorique, Compétitif |

---

## 4. Scénarios parcourus (DERIVED des règles ci-dessus)

| Scénario | Aujourd'hui | Avec R0-R6 |
| --- | --- | --- |
| Japon Historique déc. 1941 - mars 1942 | Calendrier + fenêtres | Identique : R0 possède le théâtre EAST ; R4 ajoute le rush sur les plages scriptées |
| Japon après mi-1942 | Plus rien | R1 : invasions permises si le front chinois est figé et > 100 div ; R3 impose le saut d'île en île ; R2 une à la fois |
| Japon Compétitif / guerre en 1943 | Fenêtres fermées, aucun débarquement scripté | Même comportement générique qu'au-dessus |
| Allemagne 1940-41 | Lignes GER « Sealion / not Sealion » | R1 interdit tout débarquement tant que le front en France/URSS avance → pas de Sealion qui vide le front de l'Est |
| Alliés Italie 1943 | Têtes de pont scriptées qui meurent sous le gel | R4 rush la tête de pont ; le gel continue d'empêcher une 2e plage |
| France communiste vs Royaume-Uni (ahistorique) | Rien | R1-R5 s'appliquent sans modification |

---

## 5. Faits moteur à vérifier avant de livrer

| Fait | Pourquoi c'est bloquant | Comment le mesurer |
| --- | --- | --- |
| `on_naval_invasion` ne se déclenche **pas** pour `create_unit` | Sinon R2 gèle aussi après chaque débarquement scripté (double gel) | Compteur `WA_TLM` incrémenté dans `on_naval_invasion` vs nombre d'opérations scriptées exécutées |
| Base de `invasion_unit_request` (-200 = zéro ?) | Toute l'arithmétique des -200 / +1000 | Déjà **ASSUMED** dans le système actuel (landing_freeze.txt:126) |
| -9999 annule un plan existant | R5 | Save avant / après une impulsion |
| `ROOT` = état candidat dans `state_trigger` | R3 | Harness `WA_TEST_*` ou fenêtre `imgui show ai-strategy` |
| Coût CPU de la laisse | R3 | Comparaison de vitesse en jeu |

---

## 6. Plan de livraison proposé

| Lot | Contenu | Fichiers | Validation |
| --- | --- | --- | --- |
| L1 | N1 : priorités des objectifs navals | `common/ai_navy/goals/goals_generic.txt` | Impact analysis (escorte US, corridors atlantiques) ; campagne |
| L1b | N4 : poids de dominance sur le trajet | `WA_AI_NAVAL_triggers.txt`, `WA_AI_NAVAL_DEFAULT.txt` | `check_ai_layers`, reviewers |
| L1c | N6 + N7 : entraînement 0.99, nettoyage `naval_dominance` 500 | `common/defines/05_defines.lua`, `WA_AI_NAVAL_FACTION_ALLIES.txt` | `check_constants` ; livrer N6 avec ou après N1 |
| L1d | N3 corrigé (7.8) : A ratio « part équitable » + hystérésis, puis B maîtrise de la mer par région (générateur + blocs générés) | `WA_AI_NAVAL_*` effects/triggers, pulse mensuel, `tools/gen/map_generators/`, bloc DEFAULT INVASION | `--dry-run`, `check_ai_layers`, `check_constants`, reviewers, harness `WA_TEST_*` (système avec pulse → `SHIPPED-UNTESTED`), sonde `WA_TLM` |
| L2 | R4 : flag `beachhead` (2 points de pose) + bloc rush | `00_on_actions.txt` (`on_naval_invasion`), `WA_AI_LANDING_effects.txt`, nouveau bloc DEFAULT | `check_ai_layers`, `check_constants`, reviewers architecture + lessons |
| L3 | R1 + R2 : détecteur, permission, gel organique | `on_state_control_changed`, `WA_AI_LANDING_triggers.txt`, `landing_freeze.txt` | Idem + harness `WA_TEST_*` (règle WORK.md : système avec harness → `SHIPPED-UNTESTED`) |
| L4 | R3 + R5 : laisse, filtre population, déblocage | Nouveau bloc DEFAULT | Idem + mesure CPU |
| L5 | Étape 3 de la section 3 (dates → phases) | JAP INVASION + gate triggers | Seulement après une campagne qui valide L2-L4 |

Constantes (60 j, 90 j, 800 / 3000 km, 50k habitants) : `common/script_constants/wa_ai_landing.txt` si
lues par plusieurs fichiers, sinon `@` d'un seul fichier (`wa-constants-registry`). **ASSUMED** que
`constant:` est accepté dans `distance_to value` : non listé dans les contextes validés.

---

## 7. Gestion de la flotte (règles N1-N7)

### 7.1 Le modèle moteur — trois étages qu'il ne faut pas confondre

| Étage | Ce qu'il décide | Levier | Label / source |
| --- | --- | --- | --- |
| **Objectifs** (`ai_navy/goals`) | *Quel type* de mission gagne : score = min + (max - min) × importance ; le moteur sert les objectifs par score décroissant | Plage min/max par type d'objectif | **MEASURED** `V/common/ai_navy/_documentation.md` |
| **Importance** (`ai_strategy`) | *Quelle région / quel pays* dans un type : `naval_dominance`, `convoy_raiding_target`, `naval_blockade`, `coast_defense` prennent une valeur 0-100 % | Blocs ai_strategy | **MEASURED** `V/common/ai_strategy/_documentation.md:672-720` ; que ce % soit l'importance 0-1 de l'objectif : **ASSUMED** (même vocabulaire que `convoy_raiding_target`, « objective importance ») |
| **Templates** (`ai_navy/taskforce`, `fleet`) | *Quelles flottes peuvent exister* : sans composition minimale, pas de groupe, donc pas de mission | `min_composition`, `ai_will_do` (scope pays) | **MEASURED** `V/common/ai_navy/taskforce/_documentation.md` |
| Seuils de mission | Score minimal pour assigner une mission (positif = plus dur) | `naval_mission_threshold` | **MEASURED** `lessons-log.md:1356` (signe) |

**DERIVED** — Sheep ne touche presque qu'aux templates et laisse le moteur faire la dominance sur les
trajets d'invasion. KR règle les objectifs (soutien d'invasion 10-20). WA règle surtout l'importance
(21 `naval_dominance` alliés), avec des objectifs qui défavorisent l'invasion.

### 7.2 Où WA perd aujourd'hui (DERIVED des plages MEASURED de `goals_generic.txt`)

| Exemple | Score WA | Qui gagne |
| --- | --- | --- |
| Invasion importante (importance 0.8) | 4 + 11 × 0.8 = **12.8** | — |
| Escorte de convoi banale (0.2) | 15 + 15 × 0.2 = **18** | l'escorte |
| Entraînement moyen (0.5) | 10 + 10 × 0.5 = **15** | l'entraînement |
| Dominance moyenne (0.5) | **15** | la dominance |

Une invasion prioritaire passe après une escorte banale et après l'entraînement. **ASSUMED** que les
navires s'épuisent avant d'arriver à elle (le moteur « sert autant d'objectifs que possible »).

### 7.3 Les règles

| # | Règle | Mécanique proposée | Source | Risque |
| --- | --- | --- | --- | --- |
| N1 | **Réordonner les objectifs** | `naval_invasion_support` 4-15 → **12-24**. Une invasion importante (0.8 → 21.6) passe devant l'escorte moyenne (0.4 → 21) ; une ligne de convois critique (0.9 → 28.5) garde la tête. Ne pas baisser `convoy_protection` ni `naval_dominance` (flotte de Méditerranée et corridors atlantiques en dépendent) | KR goals 10-20 | Moyen : l'escorte US a déjà été un problème (`lessons-log.md:1915`) ; impact analysis obligatoire |
| N3 | **RÉVISÉ (7.8) — la version ci-contre est remplacée** — Posture navale par ratio de force (sans tag) | Triggers `WA_AI_NAVAL_is_navally_superior` / `_inferior` sur `enemies_naval_strength_ratio` (seuils 0.8 / 1.5). **Supérieur** : garnisons côtières réduites (Sheep -25), R1 plus permissif. **Inférieur** : seuil `MISSION_STRIKE_FORCE` relevé (ne pas jeter la flotte), raiders de surface activés par l'`ai_will_do` du template, invasions organiques limitées à la laisse de 800 km | Sheep M2 (`JAP.txt:709-722`), passivité GEA (KR), gate du `DeathSquad` (Sheep) | Moyen : s'additionne au bloc `legacy_AI_naval_mission_fix` (-500 / -1000, toujours actif, `WA_AI_NAVAL_DEFAULT.txt:377`) |
| N4 | **Dominance : dynamique sur les trajets, statique seulement aux détroits** | (a) `naval_invasion_dominance_weight` : 50 → 100 tant que R1 (permission organique) est vrai ; 50 sinon (R0 retiré de la condition, voir 2b T2) (le cas « inférieur » tombe avec N3). (b) `naval_dominance` par région : réservé aux fichiers REGION, gaté par la géographie (qui tient les deux rives), comme la Méditerranée actuelle. (c) **Pas** de listes de dominance pour le Pacifique japonais | Sheep a retiré les 5 `naval_dominance` KR (`K/…/JAP.txt:797-855`) | Faible ; (a) est un type global, pas par théâtre |
| N6 | **Entraînement jusqu'à 0.99 (ce define seulement)** | `NDefines.NAI.MAX_FULLY_TRAINED_SHIP_RATIO_FOR_TRAINING` 0.8 → **0.99** (`05_defines.lua:1371`). Pas de changement de `RESEARCH_WITH_XP_AI_WEIGHT_MULT` ni d'autre define | KR `KR_defines.lua:188` | **DERIVED** un navire à l'entraînement compte ×0 en dominance (`00_defines.lua:1914-1925`) : sans N1, moins de navires pour les invasions. Carburant plafonné par `MAX_FUEL_CONSUMPTION_RATIO_FOR_NAVY_TRAINING` 0.2 (WA). Global, IA seulement |
| N7 | **Nettoyage** | `naval_dominance` 500 → ≤ 100 (`WA_AI_NAVAL_FACTION_ALLIES.txt:741,766`) et doc §21 alignée | — | **ASSUMED** effet nul si le moteur plafonne à 100 |

### 7.4 Ce qu'on ne reprend pas

| Élément | Pourquoi | Label |
| --- | --- | --- |
| Refus des droits d'amarrage (Sheep X1) | Gain non mesuré, effet diplomatique visible du joueur | **ASSUMED** |
| Faux spirits navals, sous-doctrines gratuites | Pilotage de doctrine / triche IA : autre sujet | **MEASURED** Sheep |
| N2 — templates de flotte (porte-avions dès 1 CV, groupe de surface, petites patrouilles) | Sorti du plan (décision propriétaire 2026-09-25). Le constat reste mesuré (7.7) : GER / ITA / SOV / FRA ne forment aucun strike-force | **MEASURED** |
| N5 — production navale (escortes sous menace convoi, escorteurs par capitaux, XP navale en designs) | Sorti du plan (décision propriétaire 2026-09-25) ; l'échelle de convois existe déjà dans WA (`WA_AI_PRODUCTION_DEFAULT_navy.txt:148-321`) | **MEASURED** |
| Zones d'évitement imposées à l'adversaire (GEA, Chinois) | Rend l'adversaire passif ; dans WA l'adversaire du Japon est la marine la plus forte (USA 42 chantiers) | **MEASURED** / **DERIVED** |

### 7.5 Scénarios (DERIVED)

| Cas | Effet attendu de N1, N4, N6 |
| --- | --- |
| Japon fin 1941 | Le poids de dominance monte pendant les opérations réservées ; les invasions passent devant l'entraînement (N1), qui dure plus longtemps (N6) |
| USA dans l'Atlantique | Les lignes de convois critiques gardent la priorité ; les escortes banales passent après une invasion importante |
| Alliés en Méditerranée (§21) | Inchangé : `naval_dominance` statique conservé, seulement normalisé |

### 7.7 Mesure N2 / N3 (campagnes `73c03fd3` cloud, 111 saves 1936.2-1945.4 ; `e953ae9b` local, 98 saves jusqu'à 1944.3)

Détail : `documentation/AI_NAVAL_KR_JAPAN_AUDIT_2026-09-25/4_measure_n2_n3.md`.

**N2 — confirmé (N2 est sorti du plan ; le constat reste).**

| Constat | Label |
| --- | --- |
| 161 observations de strike-force : uniquement ENG, JAP, USA ; toutes remplissent 2 CV + 2 BB + 10 CL ; composition toujours bornée par l'optimal de `StrikeForce_1` → le moteur ne forme pas de strike-force hors template | **MEASURED** / **DERIVED** |
| GER, ITA, SOV : 0 porte-avions ; FRA : 1 → aucun strike-force de toute la guerre | **MEASURED** |
| Au plus 1 strike-force par pays et par save ; des groupes capables restent en hold (221), réserve (61), entraînement (31) | **MEASURED** |
| 1943.6, en guerre : navires sans mission active USA 47 %, GER 44 %, ENG 43 %, JAP 34 % | **MEASURED** ; la cause (objectifs N1 ou templates N2) est **ASSUMED** |

**N3 — impact mesuré : peu utile, un dégât majeur.** Ratio approché (capitaux 10, CA 5, CL 3, DD/SS 1) ;
la formule moteur de `enemies_naval_strength_ratio` n'est pas documentée → **DERIVED** approché.

| Pays | Posture sur la guerre | Effet de N3 | Label |
| --- | --- | --- | --- |
| GER, ITA, SOV, FRA | Inférieur ~100 % du temps (ratio 1.6 à 28) | Aucun effet utile : ils n'ont de toute façon aucun strike-force (N2) ; N3 = constante | **DERIVED** |
| JAP | Supérieur tant qu'il ne combat que la Chine, **inférieur 3.5-4.1 dès 1942.1** | **Dégât** : le seuil strike relevé et la laisse de 800 km couperaient l'offensive japonaise dès Pearl Harbor. Cause : le ratio compte toutes les flottes ennemies du monde (Atlantique compris), pas le théâtre | **DERIVED** |
| ENG, USA | Neutre 0.84-1.41 en 1942-45, près du seuil 0.8 | Risque de bascule si la formule moteur diffère de ~10 % | **DERIVED** ; **ASSUMED** pour la formule |
| Bascule rapide | Une seule (ITA/SOV, armistice italien 1943.11-12) | Faible | **DERIVED** |

**Décision proposée** : N3 suspendu. Un ratio *global* ne dit rien du théâtre. Une variante valable
devrait comparer à l'adversaire du théâtre (`naval_strength_comparison { other = … }`, donc Faction ou
Region layer) — à ne concevoir que si un symptôme mesuré le demande.

### 7.8 N3 corrigé — un ratio calculé par WA + la maîtrise de la mer par région

**Les deux causes de l'effet de bord (DERIVED de 7.7)** :

| Cause | Effet |
| --- | --- |
| C1 — le déclencheur moteur `enemies_naval_strength_ratio` compte **toutes** les flottes ennemies du monde, sans savoir qu'elles se battent aussi ailleurs | JAP 1942 compté contre toute la flotte US et britannique, Atlantique compris |
| C2 — les conséquences s'appliquent **au pays entier** (seuil strike, laisse de 800 km) | Un seul mauvais chiffre rend toute la marine passive, partout |

**Correctif A (calcul) — ratio « part équitable » calculé chaque mois par WA.**

- Force d'un pays S = somme pondérée de `num_ships_with_type@carrier / @capital / @screen / @submarine`
  (**MEASURED** variables moteur, `dynamic_variables_documentation.md:677-681`).
- Chaque ennemi E partage sa flotte entre ses propres ennemis, au prorata de leur force. La part tournée
  contre moi, rapportée à ma force, se simplifie en : **ratio = Σ sur mes ennemis E de S(E) / S(tous les
  ennemis de E)**.
- Hystérésis : inférieur à l'entrée > 1.5, à la sortie < 1.3 ; supérieur à l'entrée < 0.8, à la sortie > 0.9.
- Écrit dans une variable pays `WA_AI_NAVAL_fair_ratio` par un effet mensuel (pulse mensuel existant),
  majeurs en guerre seulement ; sonde `WA_TLM` de la valeur.

**Mesure du correctif A** (mêmes 209 saves, pondération 7.7 ; détail
`AI_NAVAL_KR_JAPAN_AUDIT_2026-09-25/5_measure_n3_fix.md`) — **DERIVED** :

| Pays | Ratio global (actuel) | Part équitable (A) | Lecture |
| --- | --- | --- | --- |
| JAP 1942-44 | 3.5 - 4.0 | **1.9 - 2.5** | Surcompte divisé par ~1.6, mais reste inférieur : les USA + ENG surpassent vraiment le Japon, même partagés |
| ENG, USA 1942-45 | 0.84 - 1.41 (près du seuil) | **0.33 - 0.52** | Supérieurs stables : plus de risque de bascule |
| GER, ITA | 7 - 26 / 3 - 12 | 2.1 - 4.8 / 2.2 - 3.1 | Inférieurs, chiffres réalistes |
| SOV, FRA après 1940 | Inférieurs | **Supérieurs 100 %** | **Artefact** : la flotte allemande est « partagée » avec ENG/USA alors que sa flotte de la Baltique fait face à l'URSS |

**Conclusion** : A corrige le surcompte et la bascule, mais un calcul par *nombre* ne sait pas *où* sont les
flottes (cas SOV). Il faut donc aussi B.

**Correctif B (lieu) — la maîtrise de la mer du moteur, région par région.**

- **MEASURED** `has_enemy_naval_control = <région>` / `has_naval_control = <région>` : le moteur dit si
  l'ennemi (ou mon camp) a assez de dominance pour contrôler une région de mer
  (`triggers_documentation.md:3805-3818,4393-4406`). C'est le calcul de dominance du moteur : il tient
  compte de la position des flottes, de l'aviation, des radars, des bases.
- Donnée générée (nouveau générateur, même chaîne que `province_connections.py`) : pour chaque région de
  mer, les états côtiers qui la bordent (`map/strategicregions/` + `provinces.bmp` / `definition.csv`).
- Conséquences **par région**, jamais au pays entier :

| # | Conséquence | Condition | Mécanique |
| --- | --- | --- | --- |
| B1 | Ne pas jeter la flotte dans une mer perdue | L'ennemi contrôle la région **et** A dit « inférieur » | Bloc généré par région de mer : `naval_avoid_region` +500 sur cette région (Sheep `G/…/JAP.txt:533-568` : +500 quand la flotte est perdue) |
| B2 | Pas d'invasion organique à travers une mer perdue | La cible borde une région contrôlée par l'ennemi | Effet mensuel : flag d'état `WA_AI_NAVAL_enemy_sea_for_<TAG>` sur les états côtiers concernés ; bloc DEFAULT `invasion_unit_request` -200 sur ces états (même idiome `@FROM` que la réservation, **ASSUMED** comme elle) |
| B3 | Garnisons côtières réduites seulement si c'est sûr | Aucune mer bordant mes côtes n'est contrôlée par l'ennemi **et** A dit « supérieur » | `garrison` -25 (Sheep M2) |
| — | **Supprimé** : relever le seuil strike au niveau du pays, laisse de 800 km forcée | — | C'étaient les deux conséquences qui coupaient l'offensive japonaise |

**Parcours DERIVED** :

| Cas | Avant (N3 initial) | Après (A + B) |
| --- | --- | --- |
| JAP déc. 1941 - 1942 | Passif partout dès 1942.1 | A = inférieur (2.2), mais tant que l'ennemi ne contrôle pas les mers autour du Japon et des cibles, B1 / B2 ne font rien : l'offensive continue. Quand les USA prennent une mer, le Japon évite **cette** mer seulement. Que l'ennemi n'y ait pas le contrôle en 1942 : **ASSUMED** (non lisible dans les saves extraits) |
| SOV 1941-44 | Inférieur | A dit « supérieur » (artefact), mais B3 exige aussi qu'aucune mer côtière ne soit perdue : si la flotte allemande contrôle la Baltique, les garnisons restent |
| GER vs Royaume-Uni | Inférieur partout | B1 évite les mers que la Royal Navy contrôle ; la Baltique reste jouable |
| ENG, USA | Bascule possible | Supérieurs stables (A) ; B ne s'active que là où ils perdent réellement la mer |

**Faits moteur à vérifier (bloquants)** :

| Fait | Pourquoi | Comment |
| --- | --- | --- |
| `num_ships_with_type@capital` : quelles coques (CA inclus ?) | Pondération de S | Harness `WA_TEST_*` : afficher les 4 compteurs pour un pays connu |
| `has_enemy_naval_control` utilisable dans un `enable` d'ai_strategy | B1 | Vanilla l'utilise dans les objectifs de faction (**MEASURED** 29 occurrences, `common/factions/goals/`) ; en ai_strategy : **ASSUMED** |
| Coût : ~200 blocs générés évalués par le moteur | B1 | Comparaison de vitesse ; repli = un effet mensuel qui pose des flags de pays, blocs gatés par flag |

Lot de livraison : **L1d** (A puis B), après L1 ; générateur en `--dry-run` d'abord.

### 7.6 Faits moteur à vérifier

| Fait | Pour | Comment |
| --- | --- | --- |
| Part de la flotte à l'entraînement avant / après N6 | N6 | Save : missions « training » par majeur, 1939-1942 (base mesurée : ENG 133, FRA 70, GER 50, USA 50 navires en 1939.9, `4_measure_n2_n3.md`) |
| % de `naval_dominance` = importance d'objectif | N4, N7 | Fenêtre `imgui show ai-strategy` / save |
| Épuisement des navires avant les objectifs bas | N1 | Save : missions assignées par type, avant / après |
