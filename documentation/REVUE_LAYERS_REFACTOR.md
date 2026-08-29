# Revue adversariale — WA_AI_LAYERS_REFACTOR_PROPOSAL.md

Revue du 2026-08-29, branche `ai-rework`, HEAD `c339245b5`, arbre de travail avec les livrables
non commités. Relecteur : Fable 5 (session dédiée). Tous les chiffres « mon chiffre » ci-dessous
sont **MEASURED** par des scripts écrits indépendamment pour cette revue (tokeniseur propre, pas
une réutilisation des scripts de l'archive), sauf étiquette contraire. Les verdicts des deux
sous-agents du dépôt (`wa-architecture-reviewer`, `wa-lessons-reviewer`, lancés en parallèle
conformément au principe 3d d'AGENTS.md) sont relayés avec leur étiquette d'origine, jamais promus.

---

## 1. Verdict global

**VALIDÉE AVEC CORRECTIONS.**

L'architecture proposée est saine, le recensement central est exact (reproduit à l'identique par
un tokeniseur indépendant : 2418 blocs, 557/217/544/1100, PRODUCTION 15/273, MILITARY 659,
NAVAL 100), la phase 0 est bien conçue et a réellement trouvé un défaut. Mais : quatre chiffres
porteurs sont faux ou mal étiquetés (586, 430, 499, 54) et deux d'entre eux sont des **baselines
de cliquet** ; la conclusion Q2 a un contre-modèle non sondé (« NOT ne lit que son premier
enfant ») qui, s'il était vrai, inverserait le verdict « aucun défaut » ; la portée du défaut §3.6
repose sur une hypothèse moteur non mesurée que la doc de l'install **contredit** ; un des « 15
triggers morts » de la phase 1 n'est pas supprimable ; et la « pièce maîtresse » (la couche portée
par le préfixe) n'est aujourd'hui ni vraie du nommage existant (659/948 triggers hors convention)
ni vérifiée par aucune des 9 règles du checker. Rien de tout cela ne renverse le plan ; tout cela
change des baselines, l'ordre d'une phase, et le sort du harnais de phase 0 (à compléter et
committer, pas à supprimer).

---

## 2. Erreurs factuelles

Reproduits exactement (aucune divergence, méthode indépendante) : le tableau §1.2 complet ;
3203 termes bruts / 1207 nommés (§2.2) ; profondeur de chaîne max 8 = `WA_AI_can_upgrade_economy_law`
(§3.3d) ; la liste des 15 jamais-lus-hors-CONFIG ; les 4 MISC morts ; les 2 définitions dupliquées
(chacune deux fois **dans le même fichier**) ; `1942.1.1` × 56 ; 133/144 (144 triggers, 11 vivants) ;
les 3 lecteurs de `use_armored_divisions` et leurs sites exacts ; les deux définitions de « majeur »
(§3.2, l'écart est bien `num_of_civilian_factories > 99`) ; 71 `NOT` multi-enfants dans le périmètre
des 4 dossiers ; 16 harnais ; 6 bundles géographiques ; 24 lectures `use_heavy_at`.

Les erreurs :

| Affirmation | Chiffre proposition | Mon chiffre | Méthode |
| --- | --- | --- | --- |
| §1.2 `can_absorb_*` « lu **586** fois dans 32 fichiers » | 586 / 32 | **293 lectures réelles** dans 32 fichiers `ai_strategy` ; 586 = occurrences **commentaires inclus**. Dépôt entier : 350 lectures `= yes/no` dans 39 fichiers | comptage avec et sans strip des commentaires ; 586/32 reproduit exactement en réintégrant les commentaires |
| §3.4 « **430** dates hors couche 1 » | 430 | **418** hors couche 1. 430 = le **total** (418 + les 12 de CONFIG). La propre ventilation du §3.4 (283+61+48+24+2) somme à 418 | recomptage même périmètre ; la somme interne du § trahit l'erreur |
| §3.4 « **499** seuils hors couche 1 » | 499 | **494** hors couche 1 (+ 5 CONFIG = 499 total) | idem |
| §2.2 / §8.2 « **54 lectures** directes de CONFIG depuis `ai_strategy` » | 54 lectures | 54 = **paires (trigger, fichier) distinctes** (52 hors commentaires), la métrique d'`audit4.py`. Les **occurrences** réelles : **155** (158 avec `WA_AI_DIFFICULTY_*`) | deux métriques recomptées ; l'écart est ×3 sur une baseline de cliquet |
| §3.1 / §5.1 « 15 triggers CONFIG morts — suppression risque nul » | 15 supprimables en phase 1 | **14**. `WA_AI_MILITARY_pacific_high_risk` a 1 lecteur **interne** à CONFIG (`WA_AI_CONFIG_MILITARY_pacific_high_risk`, lui-même lu par `pacific_war_active` qui est vivant). Il n'est supprimable qu'avec l'effondrement de chaîne §5.2.4 — **phase 2, pas phase 1** | grep interne à CONFIG sur les 15 noms |
| §5.2.1 `is_china_front_member` « (14 tags) » | 14 tags | 14 tags **+ `is_in_faction_with = CHI`** (`WA_AI_MILITARY_triggers.txt:511`) — le membre vivant, précisément celui qui rend le déplacement « à l'identique » vers CONFIG contradictoire avec la frontière 1/2 | lecture du fichier |
| §2.3 « 349 lectures » de `WA_AI_DIFFICULTY_*` | 349 | 347–359 selon la métrique (354 hors commentaires − 7 définitions = 347 ; 366 brut). Marginal, l'ordre de grandeur tient | recomptage |
| §3.2 lecteurs de `WA_AI_major_country` : « LAW / LEND_LEASE / DIPLOMACY » | 3 systèmes | + **`events/WA_AI_misc.txt` (4 lectures)** et `wa_events_debug.txt` (2). À intégrer au chiffrage du renommage Q2 | grep dépôt |

**La limite de méthode annoncée par le README s'est matérialisée deux fois**, pas sur la pile
d'accolades (mon tokeniseur indépendant tombe sur les mêmes 2418/557/217/544/1100) mais sur :
(a) le **comptage des commentaires comme lectures** (`audit2.py` scanne le texte brut — le 586, et
un « lecteur » de `use_armored_divisions` qui n'est qu'une chaîne de log du harnais) ; (b) une
**erreur d'agrégation** total-vs-hors-couche-1 (430/499). S'y ajoute une limite de périmètre non
annoncée : le recensement des dates ne voit que les fichiers préfixés `WA_` dans 5 dossiers —
`common/decisions/z_WA_ai*.txt` (**MEASURED** : 27 dates littérales dans les fichiers WA de
`common/decisions/`) et tout `common/ai_equipment/` lui échappent.

---

## 3. Audit des conclusions de phase 0

### Q1 — `if` à limit faux dans un `OR` : **CONFIRMÉE, avec un troisième site jamais discuté**

- La sonde est bien conçue : le contrôle négatif q1c=0 **exclut** le contre-modèle « trigger
  inconnu vaut vrai par défaut » (il aurait lu 1). La sémantique mesurée est proprement une
  **implication** : `if = { limit = X  Y }` ≡ (X → Y). **MEASURED**, run owner.
- **Mais le harnais dit « 3 sites », le §3.6 et l'interpréteur en traitent 2.** Le troisième est
  `WA_AI_pathfinding_effects.txt:268` (`WA_AI_PATHFIND_check_success_conditions`) — un `if` dans
  un `OR`, **suivi d'un `else = { always = no }`** (ligne 293). Ce site est dans le même contexte
  que la mesure Q1 (limit d'un if-effet). Si le `else` ne « garde » pas (si le moteur évalue l'`if`
  vacuant-vrai et le `else` comme un membre indépendant), la condition de succès du pathfinder
  serait toujours vraie pour les types 0/2 — les chemins ferroviaires se termineraient au premier
  nœud. **DERIVED** (campagnes et historique des fixes railway) : le pathfinder produit des routes
  réelles, donc le `else` garde très probablement. Mais la sémantique de `if`/`else` en contexte
  trigger est **ASSUMED** — c'est exactement la sonde qui manque (q1e) et le motif de réparation
  candidat du §3.6. Ne pas supprimer le harnais avant de l'avoir mesurée.

### Q2 — `NOT` multi-enfants : **NUANCÉE — la question n'est fermée qu'à moitié**

Les quatre lectures (`ANSWER=0`, `all-false=1`, `all-true=0`, `three-children=0`) sont toutes
compatibles avec NOR — **et toutes également compatibles avec « `NOT` ne lit que son premier
enfant »** : NOT{oui,non}=0, NOT{non,non}=1, NOT{oui,oui}=0, NOT{oui,non,non}=0 sous les deux
modèles. La sonde discriminante — **premier enfant FAUX, second VRAI** (`NOT = { always = no
always = yes }` : NOR→0, premier-seul→1) — n'existe pas dans le harnais. Sous le contre-modèle,
les 71 sites seraient **cassés** (enfants 2..n ignorés → gardes trop permissives), soit l'inverse
du verdict « aucun défaut ». **ASSUMED** en défaveur du contre-modèle : vanilla dépend massivement
de `NOT` multi-enfants et le jeu ne serait pas jouable s'il ne lisait que le premier — plausible,
mais c'est précisément le genre de raisonnement que la phase 0 existait pour remplacer par une
mesure. **Correction : une sonde q2e, une ligne, avant de fermer Q2 et de rétrograder `NOT-MULTI`.**

### Q3 — date en script constant : **CONFIRMÉE dans sa conséquence, mécanisme sur-étiqueté**

- Le verdict opérationnel (« jamais de date dans un script constant, véhicule = trigger nommé »)
  est **robuste sous toutes les explications candidates** : constante résolvant en garbage,
  clé date rejetée par le schéma `fixed_point` (constante non définie → 0, `date > 0` toujours
  vrai), ou `date >` ignorant un membre droit non parsable. Les trois donnent `past=1 future=1`.
  La décision de conception ne dépend pas du mécanisme : elle tient.
- Deux nuances d'étiquetage : (a) la phrase des notes « *The reference resolves to something
  `date >` compares as always-satisfied* » est un **mécanisme ASSUMED** logé dans un bloc MEASURED
  — dire « l'une des trois explications, indiscernables d'ici, toutes au même effet » ; (b) le
  contrôle `constant-resolves=7` prouve la résolution en contexte **`set_temp_variable` (effet)**,
  pas dans le membre droit d'un trigger `date >` — confusion de contexte possible, sans effet sur
  le verdict, à mentionner.
- `date-file-survived=3` avec `past=1 future=1` : cohérent — le fichier charge, la comparaison ment.

### L'avertissement `Spawned event without any allowed options` : **bénin, CONFIRMÉ**

`events/wa_test_total_commitment.txt` a exactement la même forme (**MEASURED** : `hidden = yes`,
`is_triggered_only = yes`, zéro bloc `option`) et est un harnais accepté du dépôt. Surtout : le
harnais a produit sa sortie complète, donc l'événement a tiré malgré l'avertissement (**MEASURED**,
la sortie collée par l'owner).

### Le résidu `ai_strategy` : **honnête et correct**

Rien dans l'install ne documente le chemin d'évaluation des blocs `allowed`/`enable` ; `imgui show
ai-strategy` est la bonne lecture confirmante. À noter en sens inverse : les **triggers nommés dans
`enable` sont déjà prouvés par l'usage** (**DERIVED** : 273 blocs PRODUCTION nommés tournent en
campagne depuis des mois) — le refactor ne dépend donc pas du résidu ; seul le diagnostic du
2ᵉ site Q1 en dépend.

### Portée du §3.6 : **plus incertaine qu'annoncé — dans les deux sens**

1. `WA_AI_DIFFICULTY_is_historical = { difficulty < 3 }` : **MEASURED** (`WA_AI_CONFIG.txt:16`).
   Les trois lecteurs et leurs sites : **MEASURED**, vérifiés (`WA_AI_TEMPLATES_triggers.txt:178`,
   `WA_AI_CONFIG.txt:509`, `WA_AI_RESEARCH_support.txt:18` — dans les trois, le terme est bien un
   membre direct d'un `OR`, il suffit seul).
2. **Portée : TRANCHÉE après réponse de l'owner (2026-08-29, en session), et telle qu'annoncée.**
   L'échelle réelle a 5 positions (**MEASURED**, owner : vanilla 1-5 = very easy → very hard ;
   confirmé par les clés `FE_DIFFICULTY_VERY_EASY…` de `localisation/english/frontend_l_english.yml`).
   Le trigger est 0-indexé (**DERIVED** : les achievements vanilla exigent `difficulty > 1` =
   « Regular ou plus », ce qui ne colle qu'avec Regular = 2 sur une échelle 0-4). Les valeurs 3-4
   existent donc, `is_competitive` est atteignable, la portée du §3.6 est celle annoncée — et
   l'owner confirme que les builds compétitifs ne sont « pas encore implémentés », ce qui explique
   la survie du défaut exactement comme la proposition le disait. Au passage : l'entrée
   `## difficulty` de `triggers_documentation.md` (« 0-2 enum ») est **périmée dans l'install
   même** — à consigner dans `wa-engine-reference` comme oracle défaillant sur cette entrée.
3. **Fausse alerte de cette revue, soulevée puis RÉFUTÉE le même jour : les sous-niveaux
   normal/hard ne sont PAS inversés.** Cette revue avait dérivé une inversion en supposant que
   l'ordre visuel des boutons suivait l'ordre des valeurs. La vérification du frontend
   (**MEASURED**, `interface/frontendgamesetupview.gui:1852-1943` +
   `localisation/replace/afo_core_l_english.yml`) réfute la supposition : WA **repositionne** les
   boutons vanilla, et c'est le **nom moteur** du bouton qui porte la valeur, pas sa position —
   `very_easy_cb`(0)=« Easy » hist. 1ᵉʳ ; `normal_cb`(**2**)=« Normal » hist. **2ᵉ** ;
   `easy_cb`(**1**)=« Hard » hist. **3ᵉ** (« scripted assists ») ; `hard_cb`(3)=« Normal » comp. ;
   `very_hard_cb`(4)=« Hard » comp. Le code est donc **correct et cohérent de bout en bout** :
   `is_historical_hard`=1 et `is_historical_normal`=2 collent aux boutons ; `cheats_enabled`={1,4}
   = les deux « Hard » (les tooltips « scripted assists » le confirment) ; le ×2 des invasions
   scriptées (`WA_AI_DIVISION_CREATOR_effects.txt:3040`) ne touche que les deux « Hard » ; le
   commentaire « out of order intentionally » disait vrai. Le piège (valeur ≠ position visuelle)
   a failli produire un faux sujet WORK.md — il est désormais documenté dans le code
   (`[difficulty-mapping]`, tête de section de `WA_AI_CONFIG.txt`) à la demande de l'owner.
   Résidu **ASSUMED** (faible) : la liaison nom-de-checkbox → valeur d'enum est un fait moteur
   vanilla non observable depuis le dépôt ; la sonde console d'une ligne (`difficulty > 1` à
   position connue) reste le tueur de doute si on veut du MEASURED.
4. Trois précisions de conséquence : « tout pays reçoit des templates blindés » est l'effet **du
   gate** `use_armor_templates`, pas garanti l'effet final (le bloc porte aussi
   `NOT = { early_game_army_expansion_override }` et l'aval TEMPLATES gate encore — **MEASURED**
   pour le bloc, **DERIVED** pour l'aval). Et le `wa-lessons-reviewer` rappelle deux entrées du
   log qui conditionnent le **remède** : l'échelle if/else vacuant-vraie du système de lois US
   était un **accident porteur** (« audit before cleaning up ») — corriger `use_armored_divisions`
   flippe le trigger pour chaque pays non listé en compétitif, et un flip de
   `use_armor_templates` en cours de campagne est un **hasard de décommission de templates**
   (entrée 2026-08-09). Le sujet WORK.md doit donc inclure la table des pays qui basculent et la
   vérification des cibles `ai_templates`, avant de choisir la forme du fix.

---

## 4. Revue de `tools/read_harness_log.py`

L'outil est globalement bien construit (retrait des préfixes imbriqués correct, détection
début-de-run par bannière correcte au cas nominal, table Q3 à 4 états juste, contrôles-avant-réponse
respectés pour CONTEXTE/Q1/Q2). Défauts, classés :

| # | Gravité | Défaut | Entrée qui le fait échouer |
| --- | --- | --- | --- |
| 1 | **MOYEN** | **Minuit** : `errors_in_window` compare des chaînes `HH:MM:SS` ; un run à cheval sur minuit donne `wall_from > wall_to` → zéro erreur trouvée → l'outil imprime « *(aucune - le run est propre)* ». Faux négatif exactement là où l'outil promet d'attraper la fausse lecture. Corollaire : sur un `game.log` multi-sessions, les erreurs d'une autre session à la même heure entrent dans la fenêtre | run logué 23:59:58 → 00:00:04, une erreur à 00:00:01 |
| 2 | **MOYEN** | **Contrat de sortie non tenu** : le code 2 n'est posé que dans la branche `--interpret`. Sans `--interpret`, un run dont l'en-tête dit STOP sort **0** (« lecture propre ») — le docstring promet 2 sans condition. Et avec `--runs 3`, un **vieux** run STOP force 2 même si le dernier est propre | `--marker "PDX TEST"` sans `--interpret` sur un run 1 1 1 1 1 |
| 3 | **MOYEN** | **`--list` ne voit que les marqueurs finissant par `TEST`** (regex `[A-Z][A-Z0-9_ ]{2,30}TEST`). Les harnais `explain` du §7.2, interrogés au §8.4 par `--marker "EXPLAIN MILITARY"`, seront invisibles à l'inventaire — contradiction interne avec le rôle « Inventorie » du §7.3 | un `game.log` contenant `EXPLAIN NAVAL` |
| 4 | mineur | **Code mort** : `joined = {"" : ""}` dans `interpret_pdx_semantics` (ligne 154), jamais lu — la variable inutilisée annoncée | — |
| 5 | mineur | **L'interpréteur promeut un ASSUMED en verdict** : Q1 vacuant-vrai imprime « 2 sites a corriger » alors que la proposition elle-même classe le 2ᵉ site (chemin `ai_strategy`) ASSUMED, et que le 3ᵉ (pathfinding, gardé par `else`) n'est mentionné nulle part | tout run Q1=1 |
| 6 | mineur | **Un échec de contrôle rapporté « répondu »** : `date-file-survived != 3` → verdict « NON » alors qu'une faute de frappe de clé/groupe dans la constante donnerait la même lecture 0. Partiellement contrôlé par la séparation en deux fichiers ; « NON (ou clé illisible — vérifier le nom) » serait honnête | renommer `guard` en `gard` dans le fichier de sonde |
| 7 | mineur | Chemins d'erreur (`game.log` absent, `--logs` invalide, userdir introuvable) sortent 1 via `sys.exit(str)`, indiscernables de « marqueur absent » | `--logs C:\n'existe\pas` |
| 8 | mineur | `extract_runs` : le repli « chaque hit est un début » (harnais sans bannière) fait de la ligne de clôture « `---- end PDX TEST` » un début de run fantôme | harnais sans bannières `====` |
| 9 | consultatif | Sa place dans `tools/` est justifiée, mais il transforme des nombres en verdicts sur lesquels l'owner agit : il lui faut un **`--selftest`** au contrat de `check_worklist.py`, avec pour fixtures les journaux synthétiques que le §7.3 dit avoir utilisés (**déclaré, non vérifiable** : ils ne sont pas commis). C'est aussi le seul moyen de rendre falsifiable le critère d'acceptation §7.2 sans re-déplacer le jugement dans un interpréteur non testé. Le `wa-lessons-reviewer` ajoute : l'outil devrait afficher un avertissement de provenance (une lecture issue d'un hot-reload n'est pas une mesure — entrée « Scope errors after hot reload ») | — |

---

## 5. Objections d'architecture

Par gravité décroissante. « Bloquante » = à corriger avant la phase qu'elle touche, pas avant tout.

1. **BLOQUANTE (avant d'écrire le checker) — les baselines du cliquet sont fausses ou ambiguës.**
   `DATE-LEAK` 430 → 418 (+ périmètre `z_WA_ai*`/`ai_equipment` à trancher), `NUMBER-LEAK` 499 →
   494, `LAYER4-READS-CONFIG` 54 = des paires, pas des lectures (occurrences : 155), et le README
   de l'archive dit lui-même que 774 est un **plancher**. Correction structurelle : le checker
   **régénère ses baselines lui-même à son premier run** — `tools/ai_layers_baseline.json` est un
   fichier généré (à ajouter à la table *Generated And Tool-Managed Content*, verdict
   `wa-architecture-reviewer`), jamais recopié de la proposition. Chaque règle cliquet définit sa
   métrique dans son docstring (occurrences ? blocs ? paires ? quels dossiers ? commentaires
   strippés ?).

2. **BLOQUANTE (même commit que le checker) — `LAYER4-READS-CONFIG` criminalise un comportement
   aujourd'hui prescrit.** Verdict `wa-architecture-reviewer` (CONFLICT) : la règle 4 actuelle
   d'AGENTS.md **ordonne** aux couches Default/Region/Faction d'utiliser
   `WA_AI_CONFIG_MILITARY_*` — les 54 paires que le cliquet compte comme dette sont l'obéissance à
   la règle écrite. La réécriture de la règle 4 (§6) doit atterrir **dans le commit qui introduit
   le checker**, sinon le dépôt porte deux règles contradictoires.

3. **BLOQUANTE (avant la phase 4) — la frontière 3/4 « vérifiable par le nom seul » n'est vérifiée
   par rien.** Aucune des 9 règles ne vérifie qu'un bloc de couche 4 n'appelle que du `_should_` /
   `_can_` ; un bloc nommant `WA_AI_MILITARY_is_axis_member` (couche 2) compte « nommé » pour
   `LAYER4-RAW-GATE`. Et le nommage existant ne porte pas la couche : **MEASURED, 659 des 948**
   triggers `WA_AI_*` de `common/scripted_triggers/` n'ont ni préfixe CONFIG/DIFFICULTY ni verbe
   `is/has/should/can` (`WA_AI_AIFC_enabled`, `WA_AI_available_AIR`…). « Renommer au fil de l'eau »
   est incompatible avec une règle de checker au jour 1 qui classerait par le nom. Deux issues
   cohérentes : (a) une règle cliquet supplémentaire (`LAYER4-CALLS-NON-DECISION`, baseline
   générée) ; (b) rétrograder le §2.3 : le préfixe porte la couche **pour les triggers nouveaux ou
   touchés**, et la frontière 3/4 reste un objectif, pas un invariant vérifié. L'une ou l'autre —
   mais pas l'ambiguïté actuelle.

4. **MOYENNE — le périmètre de la couche 4 est incohérent entre §2.1 et le plan.** §2.1 met
   `scripted_effects`, `events`, `decisions` dans la couche 4 ; le recensement, les 774 et le
   re-routage §5.4 ne couvrent que `ai_strategy`. **MEASURED** : ~30 paires (trigger, fichier) de
   lectures CONFIG depuis `common/scripted_effects/`, 3 depuis `events/`, 2 depuis
   `common/on_actions/`, 1 + 1 depuis `decisions`/`ideas` — non planifiées. Et
   **`common/ai_equipment/` n'apparaît dans aucune couche** alors qu'il porte des gates
   `available` et 57 lectures `can_absorb` dans 7 fichiers (**MEASURED**). Soit la couche 4 se
   redéfinit « `ai_strategy` d'abord, le reste en lots ultérieurs nommés », soit le checker doit
   dire explicitement ce qu'il ne couvre pas.

5. **MOYENNE — la frontière 1/2 est incohérente en l'état** (verdict `wa-architecture-reviewer`,
   CONFLICT en prose) : `is_in_faction_with` (bouge par action) est toléré par silence — trois
   triggers §5.3, plus `china_front`/`commonwealth` déplacés « à l'identique » — pendant que
   `has_war*` (bouge par action, pareil) est interdit ; et `CONFIG-LIVE` ne liste pas
   `is_in_faction_with`, donc le checker et la prose divergent. Redessiner le test : « donnée
   d'identité/de setup » vs « état du monde vivant », avec une **liste d'exceptions nommées** dans
   le checker (le mécanisme que la proposition applique déjà à `WA_AI_DIFFICULTY_*`). Même
   verdict signale que l'extension du mandat de CONFIG (fichiers `_WINDOWS`/`_FLAGS`) contredit la
   décision enregistrée « CONFIG = classification tag/archétype seulement » (2026-08) — c'est
   défendable, mais c'est une **révision de décision** à faire trancher par l'owner, pas un détail.

6. **MOYENNE — 4 couches vs 3.** Aucun cas mesuré de deux consommateurs opposés d'un même verdict
   n'est produit, ni trouvé par cette revue (le meilleur candidat, `is_axis_member`, est lu dans
   17 fichiers `ai_strategy` des deux camps — **MEASURED** — mais « coordonner vs cibler » n'a pas
   été vérifié site par site). La séparation 2/3 est donc bien de la conviction. Elle est peu
   coûteuse **tant qu'elle reste une convention de nommage sans règle dure** : recommandation —
   garder les 4 couches dans le document, ne mettre **aucune règle de checker sur la frontière
   2/3** tant qu'un cas réel ne l'a pas justifiée (sinon c'est le méta-travail que le docstring de
   `check_worklist.py` proscrit).

7. **MOYENNE — le vocabulaire « couche vs échelon » aggrave plutôt qu'il ne résout.**
   `WA_AI_MILITARY_SYSTEM.md` et AGENTS.md appellent déjà « 4-layer model » le
   Default/Region/Faction/Country ; imposer « échelon » à l'existant exige de réécrire ce
   vocabulaire dans un document de 155 Ko, AGENTS.md, les skills et les habitudes — le risque réel
   est la demi-migration verbale. Moins coûteux et plus sûr : **c'est le modèle nouveau qui cède
   le mot** — l'appeler « rôles » (R1-R4 : déclaration/observation/décision/consommation) ou
   « étages », et ne toucher à rien du vocabulaire militaire.

8. **CONSULTATIVE — le cliquet converge-t-il ?** Il empêche l'aggravation nette ; il ne fait
   converger que si les lots continuent (pas d'échéance — assumé par la proposition, acceptable).
   Deux modes de défaillance à documenter : (a) la règle « exige la mise à jour quand ça baisse »
   fait que le baseline == compte courant en permanence — un commit qui ajoute 1 bloc brut et en
   retire 1 ailleurs passe sans bruit ; un rapport **par fichier** dans la sortie du checker rend
   ce churn visible à la revue humaine, à défaut d'être bloquant. (b) un revert de lot doit
   revert le baseline (la proposition le dit — bien).

9. **CONSULTATIVE — l'ordre est bon, avec deux précisions.** Finir PRODUCTION (15 blocs) d'abord
   est un coût borné qui produit la référence et les fixtures — ce n'est pas un report de la
   mesure perf, à condition de le **timeboxer**. Sur la mesure elle-même : le coût se paie sur
   `enable` (réévalué en continu), pas sur `allowed` — le pilote NAVAL doit convertir
   majoritairement des blocs `enable` pour que la mesure ne sous-estime pas. Et le
   `wa-lessons-reviewer` ajoute un point que la proposition ne dit pas : la cadence d'évaluation
   `allowed` (une fois au démarrage ?) vs `enable` est **ASSUMED** — la règle « mêmes termes,
   mêmes valeurs, même ordre » doit dire explicitement « **même bloc** » (un terme qui migre
   d'`allowed` vers `enable` ou l'inverse est un changement de comportement même à diff
   « sémantiquement vide »).

10. **CONSULTATIVE — le critère d'acceptation de l'`explain` (§13.3).** Oui, « l'outil nomme la
    couche qui bloque sans lecture humaine » est falsifiable — mais seulement si l'interpréteur
    est lui-même testé. Sans fixtures, le jugement subjectif est déplacé dans l'interpréteur,
    exactement la crainte du §13.3. Exigence : chaque entrée d'`INTERPRETERS` livrée avec sa
    fixture dans le `--selftest` de l'outil (voir §4.9 ci-dessus). Avec cela, le critère est réel.

---

## 6. Ce que la proposition a manqué

| Trouvaille | Étiquette |
| --- | --- |
| **Le 3ᵉ site `if`-dans-`OR`** (`WA_AI_pathfinding_effects.txt:268`) : compté par le harnais (« 3 sites »), jamais discuté ; gardé par un `else = { always = no }` dont la sémantique en contexte trigger est non mesurée — et qui est le motif de réparation candidat du §3.6 | **MEASURED** (site), **ASSUMED** (sémantique du else), **DERIVED** (il garde en pratique — le pathfinder produit des routes réelles) |
| **Q2 n'est pas fermée** : contre-modèle « premier enfant seul » compatible avec les 4 lectures ; sonde q2e manquante (voir §3) | **MEASURED** (analyse des sondes) |
| **Le mapping difficulté valeur↔bouton n'était documenté nulle part côté script** : la valeur ne suit pas l'ordre visuel des boutons (WA repositionne les checkboxes vanilla dans le `.gui`), piège qui a fait dériver à cette revue même une fausse « inversion normal/hard » (réfutée — §3 point 3). Corrigé : table `[difficulty-mapping]` ajoutée en tête de section difficulté de `WA_AI_CONFIG.txt` (demande owner). La doc moteur `## difficulty` (« 0-2 enum ») est par ailleurs périmée — 5 valeurs réelles | **MEASURED** (`.gui` + `afo_core_l_english.yml` + code) |
| **2 morts de plus dans `WA_AI_MISC_triggers.txt`** : `WA_AI_build_infantry` et `WA_test54` — 1 occurrence chacun (leur définition). La passe morte du §3.1 en a compté 4 sur 6 | **MEASURED** (grep dépôt hors tests/doc/.claude) |
| **`WORK.md` est déjà à la limite WIP** : 4 sujets non parqués (`armor-class-handoff`, `armor-budget-ramp`, `armor-ladder-integrity`, `mech-window`, tous SHIPPED-UNTESTED 2026-08-29). Ouvrir le sujet §3.6 maintenant violerait `WIP-LIMIT` | **MEASURED** (WORK.md) |
| **Le harnais de phase 0 est untracked** : le supprimer avant de le committer laisserait `PDXSCRIPT_LANGUAGE_NOTES.md` citer une évidence qui n'a jamais existé dans l'historique | **MEASURED** (git status ; relevé par `wa-lessons-reviewer`) |
| **Le remède §3.6 croise deux leçons du log** : l'échelle vacuant-vraie du système de lois US était un accident porteur (« audit before cleaning up »), et un flip de gate de templates en cours de campagne est un hasard de décommission (2026-08-09). La table des pays qui basculent est un prérequis du fix | **MEASURED** (entrées du log, via `wa-lessons-reviewer`) |
| **La suppression au re-grep seul est en-dessous du standard du log** : « grep yields candidates only — read the block » (meta_trigger et noms assemblés dynamiquement sont invisibles au grep) ; et la leçon force_concentration-CTD impose un **boot test par lot** de suppression, pas seulement une revue de parse | **MEASURED** (entrées du log, via `wa-lessons-reviewer`) |
| **`check_engine_docs.py` a déjà 1 ERROR** (`common/raids/_documentation.md` en dérive) — préexistant, sans rapport avec la proposition, mais la matrice de validation qu'elle étend n'est pas au vert aujourd'hui | **MEASURED** (run de cette revue) |
| **La table des contextes validés du skill `wa-constants-registry` doit gagner une ligne FORBIDDEN** `date > constant:` (silencieusement permissif) — le §6.1 dit « étendre le skill » sans nommer cette ligne | verdict `wa-architecture-reviewer` |
| Lecteurs hors-AI de la couche 1 (§13.6) : rien de plus que la liste de la proposition (country_leader 11, scripted_localisation 5, decisions/ideas/history 1 chacun — reproduits). Réponse à sa question : **exceptions nommées dans le checker**, comme `WA_AI_DIFFICULTY_*` — ces lecteurs consomment la classification à bon droit ; les re-router serait un sujet séparé sans bénéfice démontré | **MEASURED** (recomptage) |
| Le choix d'un outil séparé plutôt que d'étendre `check_worklist.py` : **bon choix, pas une esquive** — son docstring dit « nothing more » et le contrat fixture/selftest est exactement ce que le nouveau checker doit copier | **MEASURED** (docstring) |
| §11 (LAW hors périmètre) : **justifié** — 2163 lignes de miroir de données vanilla, problème de génération, pas de couches. D'accord avec la proposition | jugement |

---

## 7. Corrections proposées, section par section

- **§1.2** : remplacer « 586 lectures dans 32 fichiers » par « 293 lectures dans 32 fichiers
  `ai_strategy` (586 en comptant les mentions en commentaire) ». La thèse (une définition, des
  centaines de consommateurs) tient.
- **§2.2** : « 54 lectures » → « 54 paires trigger×fichier ; 155 occurrences ». Choisir la
  métrique du cliquet et l'écrire.
- **§2.3** : quantifier l'écart de nommage (659/948 triggers hors convention) et trancher
  l'objection 5.3 (règle cliquet supplémentaire, ou rétrogradation explicite de la frontière 3/4).
- **§3.1 / §5.1** : 15 → **14 supprimables en phase 1** ; `pacific_high_risk` se supprime dans le
  commit §5.2.4. Ajouter `WA_AI_build_infantry` et `WA_test54` à la passe MISC. Renforcer le
  protocole : lecture du bloc (pas seulement re-grep), vérification zéro-lecteur dans
  `common/ai_templates/`, boot test par lot.
- **§3.2** : ajouter `events/WA_AI_misc.txt` (4 lectures) aux lecteurs de `WA_AI_major_country`.
- **§3.4** : 430 → 418, 499 → 494 (CONFIG en porte 12 et 5 ; les totaux sont 430/499). Nommer le
  trou de périmètre (`z_WA_ai*`, `ai_equipment`).
- **§3.5 / §4.3 / PDXSCRIPT_LANGUAGE_NOTES** : Q2 passe de « close sans défaut » à « close sous
  réserve de q2e » ; Q1 mentionne le 3ᵉ site et son `else` non mesuré ; Q3 : étiqueter le
  mécanisme ASSUMED, garder le verdict.
- **§3.6** : la borne « compétitive seulement » devient DERIVED-sous-hypothèse ; ajouter la mesure
  de l'échelle `difficulty` au sujet WORK.md, plus la table des pays qui basculent et la
  vérification décommission (leçons citées au §6 ci-dessus).
- **§4.1 / §7.1** : le harnais ne se supprime pas encore — il lui manque q1e (`if`+`else` dans un
  `OR`), q2e (`NOT { no yes }`), et idéalement la sonde `difficulty`. Et il se **committe d'abord**
  (il est untracked), suppression dans un commit ultérieur.
- **§5.2.1** : documenter le membre `is_in_faction_with = CHI` et le réconcilier avec la frontière
  1/2 (exception nommée, ou scission avant déplacement).
- **§5.4** : dire explicitement que le lot couvre `ai_strategy` seulement, et créer une ligne de
  plan pour les lectures CONFIG depuis `scripted_effects`/`events`/`on_actions` et pour
  `ai_equipment` (même s'il conclut « lots ultérieurs »).
- **§7.3** : corriger l'outil (minuit, contrat de sortie, `--list`, code mort, messages Q1) et lui
  donner un `--selftest` avec les journaux synthétiques en fixtures ; chaque interpréteur `explain`
  livré avec sa fixture.
- **§8.2** : baselines régénérées par l'outil, `ai_layers_baseline.json` dans la table des
  fichiers générés, métrique par règle dans le docstring, allowlists explicites
  (`ai_strategy value =`, `@` mono-fichier, `tag =` d'adressage Country), frontière de
  responsabilité écrite vs `check_constants.py`, et la réécriture de la règle 4 d'AGENTS.md **dans
  le même commit**. `NOT-MULTI` reste INFO tant que q2e n'est pas mesurée.
- **§12** : retirer Q1 (déjà exécutée). Compléter Q6 : « brancher » les 8 triggers est un hasard
  de décommission (leçon 2026-08-09) — pencher pour supprimer.

---

## 8. Recommandation à l'owner

**Appliquer, après corrections.** Aucune objection ne renverse le modèle ni le plan ; les
bloquantes portent sur les baselines du checker, la synchronisation avec AGENTS.md règle 4, et
l'ordre `pacific_high_risk`. Les phases 1-2 peuvent démarrer dès ces corrections faites.

**Les 7 décisions du §12** : Q2, Q3, Q4, Q5, Q7 sont bien posées et les recommandations sont
bonnes (pour Q2, ajouter `events/WA_AI_misc.txt` au chiffrage). Deux sont mal posées :

- **Q1 est obsolète** — le harnais a été lancé, les résultats sont dans le document. À retirer.
- **Q6 est posée sans son risque** : « brancher » les 8 triggers assault/support tanks n'est pas
  symétrique de « supprimer » — c'est un hasard de décommission de templates en cours de campagne
  (leçon 2026-08-09). Si l'owner veut cette famille, c'est un sujet WORK.md avec sa propre analyse
  d'impact, pas une option de la phase 1.

**Les deux questions ouvertes** :

1. *Ouvrir un sujet WORK.md pour le défaut §3.6 ?* **Oui sur l'admission** (symptôme MEASURED),
   **pas maintenant** : WORK.md est à 4 sujets non parqués — la limite. La portée est tranchée
   (compétitif atteignable, échelle 0-4, mapping frontend vérifié — la fausse alerte « inversion
   normal/hard » de cette revue est réfutée §3 point 3, et aucun sujet n'a été ouvert pour elle).
   Le sujet §3.6 doit inclure : table des pays qui basculent en compétitif, vérification
   décommission (leçons citées §6), et forme du fix en `AND` explicite
   (`AND = { WA_AI_DIFFICULTY_is_historical = yes  OR = { JAP ITA } }`) plutôt qu'un `else` —
   pour ne dépendre d'aucune sémantique non mesurée.
2. *Supprimer le harnais de phase 0 maintenant ?* **Non.** D'abord le **committer** (il est
   untracked — le supprimer maintenant laisserait les notes citer une évidence sans historique),
   puis le **compléter** (q1e `if`+`else` dans un `OR`, q2e `NOT { no yes }`, et une sonde
   `difficulty > 1` / `> 2` pour confirmer le 0-indexage — quelques `if` d'une ligne), re-lancer
   une fois, et le supprimer dans un commit dédié une fois Q1/Q2 réellement closes.

**Bilan chiffré** : 8 erreurs factuelles (2 sur des baselines de cliquet), 3 objections
bloquantes, 1 site de défaut potentiel non discuté (pathfinding), 2 sondes manquantes, 2 morts
supplémentaires trouvés — et 1 fausse alerte émise puis réfutée par cette revue elle-même
(« inversion normal/hard », §3 point 3), close par la table `[difficulty-mapping]` désormais dans
le code.

**La chose la plus importante** : *la portée du §3.6 est maintenant entièrement tranchée — le
compétitif est atteignable (valeurs 3-4) mais « pas encore implémenté », donc le défaut est réel
et dormant.* Il devient un sujet WORK.md dès qu'un créneau se libère, avec sa table de bascule et
son fix en `AND` explicite. Et le piège qui a produit la fausse alerte de cette revue — la valeur
de `difficulty` ne suit pas l'ordre visuel des boutons — est exactement le genre de fait qui doit
vivre dans le code, pas dans la mémoire d'une session : c'est fait.
