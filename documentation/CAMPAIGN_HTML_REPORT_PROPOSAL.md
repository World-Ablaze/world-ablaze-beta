# Rapport HTML de campagne — proposition

Statut : générateur implémenté le 2026-09-07 ; rapport en anglais livré, limites ci-dessous.
Sujet : `campaign-html-report`. La conception initiale est conservée après la note de livraison.

## Livraison du 2026-09-07

Le générateur, son interface et les tests sont sous `tools/campaign_report/`.
Le [guide en anglais](../tools/campaign_report/README.md) documente les commandes,
les fichiers à modifier et les contrats de mesure. Aucun appel LLM n'est utilisé.
Le rapport HTML et son JSON sont sous `tools/campaign_report/output/` ; ce dossier
et `.cache/campaign_report/` sont ignorés par Git.

| Contrôle | Résultat |
| --- | --- |
| Campagne complète | **MEASURED** — le JSON généré pour `a100b67c` contient 132 sauvegardes, du 1936.2.1 au 1947.1.1, avec 409 tags sérialisés. Les sept majeurs et toute la période sont sélectionnés par défaut. |
| Coût observé | Premier passage : 723,62 s, 4 workers et 4 entrées déjà en cache. Second passage : 21,79 s de sélection/extraction avec 132/132 résultats en cache, hors écriture finale. HTML compressé : 8,35 Mo. Ce sont des mesures locales, pas des garanties de durée. |
| Présentation | Six onglets en anglais ; courbes, compositions, tableaux, filtres pays/période/date inspectée, comparaison en base 100, provenance par graphique. Noms originaux des modèles conservés. |
| Tests Python | 17 tests réussis, 1 test de parité locale optionnel ignoré lors du dernier passage standard. La parité sur trois dates réelles a été exécutée séparément et a réussi. Syntaxe JavaScript et `git diff --check` valides. |
| Navigateur | Six onglets, Army/Navy/Air, états possédés, recherche et retrait d'un pays, sélection vide, sept majeurs, dates, curseurs, période rapide, base 100, tableaux sources et filtres de variantes vérifiés sur le rapport complet servi localement. Aucune erreur JavaScript observée. |
| Limites de vérification UI | L'ouverture `file://` est bloquée par la politique du navigateur intégré ; l'autonomie est vérifiée dans le contenu du HTML, mais l'ouverture directe n'a pas été validée ici. Le téléchargement CSV n'a pas produit de confirmation dans ce navigateur. Export JSON et affichage mobile restent à contrôler dans un navigateur de bureau. |
| Mesures encore indisponibles | Débit quotidien exact des chars, besoin d'entraînement, déficit net et besoin par variante restent `null`, avec explication visible. Les champs bruts des lignes de production restent inspectables. |
| Réserves de sens | **ASSUMED** — interprétation de `manpower.ratio` comme réserve libre, héritée explicitement de `losses.py`. **DERIVED** — attribution des compteurs de pertes suivant ce lecteur. Demandes de renforcement, usines installées et stocks signés portent leurs périmètres dans le guide ; aucun déficit net n'est inventé. |

Commande disponible : `python -m tools.campaign_report build --campaign a100b67c`.
Pour changer uniquement la présentation, utiliser la commande `render` du guide,
sans refaire l'extraction. L'implémentation regroupe le modèle et les extracteurs
dans `extract.py` plutôt que de créer tous les modules envisagés ci-dessous.

Les validations sémantiques et les contrôles de téléchargement/ouverture directe
restent explicitement ouverts ; cette livraison ne les déclare pas résolus.

## Objectif et livraison

Créer un outil Python conservé dans le dépôt, qui transforme une série de sauvegardes
d'une campagne en un rapport HTML interactif, autonome et utilisable hors connexion.
Le rapport doit permettre de comparer les moyens des pays, leur composition et leurs
tensions économiques dans le temps. Les explications causales de comportement IA
restent une analyse distincte, appuyée sur les scripts et les observations.

Livrables proposés : code et tests sous `tools/campaign_report/`, commande documentée,
HTML autonome, données JSON réutilisables et export CSV depuis chaque graphique.
Les rapports et caches générés seraient exclus de Git ; le générateur, les règles
de classement et les ressources graphiques seraient versionnés.

## Navigation et valeurs par défaut

| Élément | Comportement proposé |
| --- | --- |
| Campagne | Une campagne et une branche explicites par rapport. Afficher identité, couverture et nombre de sauvegardes. |
| Pays | Allemagne GER, Royaume-Uni ENG, États-Unis USA, URSS SOV, Japon JAP, Italie ITA, France FRA cochés. Tous les pays présents restent sélectionnables avec recherche. |
| Temps | Toute la période disponible ; début/fin par champs de date et curseur à deux poignées. Raccourcis dernière année, trois dernières années, tout. |
| Date d'inspection | Dernière sauvegarde dans la fenêtre ; déplaçable sur la chronologie. Toutes les cartes et compositions suivent cette date. |
| Comparaison | Une couleur constante par pays ; une mesure par graphique, sept courbes au maximum par défaut. Mode indice 100 optionnel, valeur initiale nulle explicitement non normalisable. |
| Composition | Petits graphiques comparables par pays, plutôt que pays × catégories sur une seule courbe. Effectifs absolus par défaut ; parts en % optionnelles. |
| Agrégation | Aucun total des sept pays par défaut. Somme explicite seulement pour des quantités additives et un périmètre sans double compte ; pas de somme de stabilité, de soutien ou d'XP. |
| Détail | Clic sur pays, famille ou indicateur pour ouvrir catégories et tableau exact ; retour conservant tous les filtres. |
| Courbes | Points datés, pas de lissage ; pas de zéro fabriqué pour une valeur absente. Signaler et interrompre les séries lors des lacunes identifiées. |
| Lisibilité | Axes et unités visibles ; pas de double axe par défaut. Une échelle commune entre les panneaux comparables, avec option d'échelle individuelle clairement indiquée. |

## Six onglets

| Onglet | Graphiques et indicateurs | Sélections initiales |
| --- | --- | --- |
| **Vue d'ensemble** | Tableau compact par pays avec valeurs à la date choisie et variation depuis le début de fenêtre ; mini-courbes de manpower, divisions, navires, avions, industrie et pertes. Matrice colorée pays × tensions mesurables. | Sept pays ; totaux ; faits chiffrés uniquement. Aucun score global arbitraire de « qualité de l'IA ». |
| **Forces** | Trois sections Terre / Mer / Air. Courbes des totaux par pays. Composition empilée par famille, dans un panneau par pays. Terre : nombre de divisions et effectifs humains dans deux graphiques alignés ; détail des modèles. Mer : nombre de navires par type. Air : appareils en unités par rôle et réserves dans des séries distinctes. | Terre ouverte ; forces déployées ; toutes familles. Détail des prêts/forces commandées et des appareils embarqués accessible. |
| **Industrie et ressources** | Civiles, militaires et chantiers navals en graphiques alignés. Raffineries : trois familles, barres ou aires empilées actives/inactives. Ressources : matrice pays × ressource à la date choisie puis production/importations/exportations et balance/déficit dans des panneaux temporels alignés. | Bâtiments des états contrôlés ; variantes hydro incluses dans leur famille. Toutes ressources dans la matrice ; vue temporelle des déficits. |
| **Blindés** | Familles de chars et dérivés : courbes de stock, équipement déployé et besoin vérifié en unités ; déficit en panneau séparé ; production en unités/jour dans un autre panneau. Usines affectées et efficacité en complément. Tableau des variantes : nom, créateur, famille, stock, lignes, production, besoin disponible. | Tous chars et dérivés ; agrégation par famille. Tous créateurs, avec filtre national/étranger. Variantes dans le détail. |
| **Guerres et pertes** | Pertes cumulées des guerres en cours, courbe par pays ; détail par adversaire/conflit. Manpower et effectifs dans des graphiques alignés. Variations de pertes entre observations lorsque le périmètre est comparable. | Guerres présentes à chaque date ; cumul depuis le début de chaque guerre, sans remise à zéro au début du filtre temporel. Changements de périmètre annotés. |
| **État du pays** | Stabilité et soutien à la guerre ensemble, de 0 à 100 %, dans un panneau par pays. XP terrestre/navale/aérienne ensemble en points, dans un autre panneau. Puissance de commandement à part. | Toutes ces mesures ; mêmes filtres de pays et dates. |

Une même unité ne suffit pas à justifier une fusion : les effectifs disponibles et
les pertes cumulées restent dans deux panneaux, tandis que les trois XP peuvent
partager un graphique par pays. Une variation de stock reste nommée « variation
de stock » ; elle ne devient jamais une mesure de production.

## Sources existantes et contrats à préciser

Les sources ci-dessous ont été ouvertes pendant cette session. Les états « à ajouter »
désignent un travail futur, pas une extraction déjà livrée.

| Donnée | Base vérifiée | Travail proposé / limite |
| --- | --- | --- |
| Divisions | **MEASURED** — `savegame.py`, `_count_divisions`, compte les divisions directement dans `units`. `plans.py` expose `scan`, `template_family` et les modèles de divisions. | Adapter ces résultats en objets structurés ; conserver les bataillons sources du classement. Distinguer forces possédées et commandées pour les prêts. Vérifier séparément la somme des effectifs humains. |
| Flotte | **MEASURED** — `savegame.py` et sa compétence documentent `navy` et ses catégories. | Réutiliser le recensement, auditer le classement par définition d'équipement et isoler les types inconnus. Conserver les convois séparés des navires de guerre. |
| Aviation | **MEASURED** — `cvair.py`, `parse`, renvoie les unités aériennes avec pays, définition, base et nombre d'appareils. | Généraliser la présentation à tous les rôles ; contrôler les stocks séparément. Ne pas compter les historiques de combat imbriqués. |
| Stocks et variantes | **MEASURED** — `stock.py`, `equipment_definitions` et `holders_equipment`, associe identifiant de variante, définition, créateur et quantité. | Joindre aux définitions de `common/units/equipment/`. Préserver les stocks signés. Vérifier le périmètre exact des blocs avant de réutiliser le classement. |
| Ressources | **MEASURED** — `savegame.py`, `_parse_resources` et `cmd_resources`, lit production, transferts, imports, disponible, déficit et exports. | Exposer les colonnes et la formule de balance utilisée ; distinguer exportable et réellement exporté. Contrôler le résidu de l'identité comptable. |
| Bâtiments | **MEASURED** — `savegame.py`, `_state_buildings` et `cmd_buildings`, produit des sommes par propriétaire et contrôleur et conserve les bâtiments `_inactive`. | Afficher des niveaux installés ; ne pas les nommer capacité économique utilisable sans autre lecture validée. Détail par état pour audit. |
| Raffineries | **MEASURED** — `common/buildings/00_buildings.txt:285` et suivantes définit synthétique, acier, acier hydro, aluminium et aluminium hydro. | Trois familles d'affichage : synthétique, acier, aluminium ; sous-types hydro dépliables et ventilation actif/inactif. |
| Pertes | **MEASURED** — `losses.py`, `scan` et `tally`, lit les deux compteurs des relations de guerre et identifie les conflits par paire + début. **DERIVED** — leur attribution aux pertes subies par chaque côté est explicitement une inférence dans l'en-tête du script. | Préserver ce niveau de preuve. Compter chaque relation une fois ; ne pas annoncer un total historique exhaustif lorsque des relations disparaissent entre deux sauvegardes. |
| Manpower disponible | **MEASURED** — `losses.py` lit `manpower.ratio`. **ASSUMED** — son interprétation comme réserve disponible est déclarée non vérifiée dans l'en-tête. | Comparer la valeur à l'interface du jeu avant de retirer cette réserve sémantique. |
| Production et besoin des chars | **MEASURED** — la compétence `wa-savegame-analysis` décrit les lignes de production et la jointure des variantes aux définitions du mod. | Ajouter un extracteur spécialisé. Vérifier sens, unité et période des champs de production. Besoin de renforcement, entraînement et remplacement doivent rester distincts. Ne jamais déduire le besoin d'une variante particulière d'un manque connu seulement par famille. |
| Stabilité, soutien, commandement, XP | **MEASURED** — le contrôle délégué sur GER, `1943.6_Jun.hoi4`, lit `stability=1`, `war_support=0.964`, `command_power=10` et les XP de `experience_status` : terre 38.37820, mer 999, air 999. | Ajouter un petit extracteur scalaire ; conserver le chemin exact des champs et valider leur présentation. |

### Contrôle borné sur une sauvegarde réelle

Lecture déléguée conformément à la compétence de sauvegardes ; aucune analyse
causale de campagne n'a été conduite. Source : campagne locale `a100b67c`, fichier
`1943.6_Jun.hoi4` dans le dossier HOI4 `save games`, pays GER.

| Observation | Conséquence proposée |
| --- | --- |
| **MEASURED** — `countries/GER/manpower/ratio=1481500`. | Valeur extractible ; son sens de réserve disponible reste **ASSUMED**, comme dans `losses.py`. |
| **MEASURED** — une division porte 17 657 hommes présents et un besoin de 18 200 dans `army_manpower`, avec pays contributeur. | **DERIVED** — une somme des effectifs réels est réalisable en étendant la lecture des divisions ; garder recrutement et contributions étrangères séparés. |
| **MEASURED** — 32 lignes `production/military_lines`, avec des champs `produced`, `speed`, `cost`, `active_factories`, `requested_factories` et `equipment_variant_index`. | **DERIVED** — modèles et usines affectées sont accessibles. **ASSUMED** — la conversion de ces champs en débit quotidien exact n'est pas validée par cette passe. |
| **MEASURED** — les demandes sous `units/division/requests/reinforcement/request/need` portent des catégories d'équipement, dont `motorized_equipment=15`. | **DERIVED** — extraire le besoin au niveau compatible documenté. Le contrôle ne prouve pas encore un besoin de chars complet ; ne pas promettre une répartition par variante. |

Ces observations démontrent des champs présents sur cet échantillon ; elles ne
valident pas encore leur couverture pour tous les pays et toutes les versions.

## Architecture proposée

Commande cible, désormais disponible :

```text
python -m tools.campaign_report build --saves "<dossier>" --campaign "<id>" --output "<rapport.html>"
```

| Élément proposé | Responsabilité |
| --- | --- |
| `tools/campaign_report/__main__.py` | Commandes de découverte, extraction et génération ; diagnostics lisibles. |
| `campaign.py` | Métadonnées, identité, ordre des dates, doublons et choix explicite de branche. |
| `extractors/` | Lectures déterministes par domaine, réutilisant les lecteurs existants via des adaptateurs. Aucun découpage des sorties console pour produire les données. |
| `model.py` et `metrics.json` | Schéma versionné ; définition des métriques, unités, périmètres, formules, règles de classement. |
| `cache.py` | Résultats par sauvegarde, invalidés par contenu, version d'extracteur et dépendances aux définitions du mod. |
| `render.py` et `web/` | HTML, CSS et JavaScript séparés en source ; données et ressources intégrées au HTML final. Graphiques interactifs, exports et navigation locale. |
| `tests/` et `README.md` | Extraits de sauvegarde minimaux, invariants, parité et procédure de reproduction. |

Objectif de performance : parcourir chaque sauvegarde pour tous les pays ensemble,
avec un nombre borné de passes par domaine ; mettre en cache l'extraction, puis
régénérer l'interface sans relire les sauvegardes. Mesurer durée, mémoire et taille
du rapport sur une campagne complète avant d'annoncer un temps de génération.
La bibliothèque graphique éventuelle devra être locale, figée et distribuable avec
sa licence ; aucun téléchargement requis à l'ouverture du rapport.

Conserver les commandes existantes pendant cette évolution. Les changements du
lecteur partagé devront préserver leurs sorties et être testés sur des cas de
régression. Le rapport ne nécessite pas de modification de logique IA.

## Fiabilité des séries

Chaque valeur doit porter une date d'observation, une unité, un périmètre, une source
(fichier + chemin logique du champ), un état de disponibilité et un niveau de preuve
`MEASURED`, `DERIVED` ou `ASSUMED`. Une formule dérivée conserve ses entrées et leurs
réserves. Le graphe expose ces informations dans l'infobulle et le tableau de données.

- Distinguer zéro réel, champ absent, pays absent et extraction non prise en charge.
- Une sauvegarde isolée fournit une photographie. Les courbes exigent plusieurs
  observations ou un historique enregistré et vérifié pour la métrique concernée.
- **MEASURED** — `savegame.py` utilise `game_unique_id` pour le regroupement ; la
  compétence signale que rechargements et dates peuvent introduire plusieurs branches.
  Exiger une sélection explicite quand une ambiguïté est détectée ; le tri ne prouve
  pas, seul, la continuité d'une campagne.
- **MEASURED** — `savegame.py` propose une fraîcheur des séries `wa_tlm_*` et réserve
  l'axe temporel aux tableaux historiques. Réutiliser ces contrôles pour tout complément
  provenant de la télémétrie ; ne pas confondre tableau indexé et série datée.
- Une guerre disparue termine sa série observée. Sa dernière valeur connue ne prouve
  pas le total au moment de la paix. Les différences ne doivent pas traverser cette
  rupture comme si le périmètre était constant.
- Pour les besoins d'équipement, conserver une catégorie « non attribuable à une
  variante ». N'afficher un déficit net qu'après validation du périmètre commun du
  stock et du besoin ; documenter la formule et éviter de compter deux fois un manque
  déjà représenté par un stock négatif.
- Enregistrer la révision des définitions utilisée pour classifier les équipements.
  Une ancienne sauvegarde interprétée avec les fichiers actuels doit le signaler.

## Place des LLM

Zéro appel LLM dans la chaîne obligatoire : lecture, classement, calcul, cache,
graphiques et constats arithmétiques doivent être reproductibles.

Une option future pourrait produire une courte synthèse à partir du JSON déjà
validé : observations sourcées et questions à investiguer. Elle aurait un budget,
un cache et une provenance propres, sans modifier les chiffres. Une valeur absente
ou une unité non comprise reste indisponible ; un modèle ne la reconstitue pas.
Une classification manuelle versionnée reste préférable lorsque peu de types sont
ambigus. Réévaluer l'intérêt d'un modèle seulement sur un cas réel avec un coût
d'extraction déterministe documenté.

## Ordre d'implémentation et clôture

1. Stabiliser le schéma et les contrats des champs incertains, sur quelques
   sauvegardes de début, milieu et fin d'une même campagne.
2. Livrer ensemble extraction, cache et les six onglets ; afficher explicitement
   les mesures dont la sémantique n'a pas encore été validée.
3. Valider les champs restants, contrôler la campagne complète et mesurer les coûts.

Critères de clôture proposés : toutes les données demandées sont soit disponibles
avec un contrat vérifié, soit accompagnées d'une limite précise acceptée ; filtre
des sept pays et fenêtre temporelle opérationnels dans tous les onglets ; concordance
avec les extracteurs de référence ; sommes de catégories égales aux totaux ; aucun
doublon de guerre ; tests de valeurs absentes et de ruptures ; HTML utilisable hors
connexion ; génération reproductible depuis une commande documentée.

Risque principal : une extraction syntaxiquement exacte avec un intitulé erroné
(production, manpower ou besoin). Le contrôle des unités et périmètres prime sur
l'ajout de graphiques. Les validations visuelles couvrent les filtres, légendes,
infobulles, dates irrégulières, données manquantes et tableaux de variantes volumineux.
