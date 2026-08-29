# WA_AI_LAYERS — le modèle en couches techniques

Document de référence du modèle introduit par la refactorisation 2026-08-29
(`WA_AI_LAYERS_REFACTOR_PROPOSAL.md`, corrigée par `REVUE_LAYERS_REFACTOR.md`).
Vérification mécanique : `python tools/check_ai_layers.py` (cliquet sur
`tools/ai_layers_baseline.json`, fichier GÉNÉRÉ — jamais édité à la main).

**Vocabulaire** : « couche » (layer) désigne CE modèle technique. Le modèle
Default/Region/Faction/Country de `WA_AI_MILITARY_SYSTEM.md` est un axe de **portée**
orthogonal — dire « échelon » (tier). Un fichier Country (échelon 4) contient des blocs de
couche 4 qui appellent des triggers de couche 3.

## 1. Les quatre couches

| # | Couche | Question | Matière | A le droit de lire |
| --- | --- | --- | --- | --- |
| 1 | **DÉCLARATION** | « Quelle est la valeur ? » | `common/script_constants/wa_ai_*.txt` + `common/scripted_triggers/WA_AI_CONFIG*.txt` | rien |
| 2 | **OBSERVATION** | « Qu'est-ce qui est vrai, maintenant ? » | `WA_AI_<SYS>_is_*` / `_has_*` / `_holds_*` dans `common/scripted_triggers/WA_AI_<SYS>_*.txt` | couche 1 |
| 3 | **DÉCISION** | « Faut-il agir ? » | `WA_AI_<SYS>_should_*` / `_can_*`, mêmes fichiers | couches 1 + 2 |
| 4 | **CONSOMMATION** | — | `common/ai_strategy/`, `common/scripted_effects/`, `events/`, `common/decisions/` | couche 3 (plus l'adressage Country `allowed = { tag = X }`) |

La couche est **portée par le nom** (préfixe + verbe) : c'est ce qui rend le modèle vérifiable
par grep. Les triggers existants antérieurs au modèle ne sont **pas** renommés en masse
(cf. §5) — la frontière 3/4 est un objectif suivi par cliquet (`LAYER4-NON-DECISION`), pas un
invariant déjà vrai.

## 2. Les trois frontières

**Frontière 1/2 — donnée d'identité/de setup vs état du monde vivant.** Une déclaration de
couche 1 lit des **données d'identité et de setup** : `tag`, `original_tag`, `date`, seuils,
`has_tech`, `has_completed_focus`, `has_idea`, `has_government`, `has_autonomy_state`,
`difficulty`. Elle ne lit pas l'**état du monde vivant** : `any_enemy_country`,
`any_country_of`, `has_war*`, `controls_state`, `owns_state`, `surrender_progress`,
`check_variable`, `num_divisions`, tout balayage de pays. Cas limite tranché :
`is_in_faction_with` est toléré en couche 1 **uniquement** quand les tags sont la donnée et
l'appartenance leur lecture naturelle (`is_in_allies`, `is_axis_minor`,
`is_axis_non_german_member`, `is_china_front_member`) — liste d'exceptions nommée dans le
checker, pas une tolérance implicite. (L'ancien test « bouge-t-il tout seul ? » était
incohérent : la guerre et les factions bougent toutes deux par action.)

**Frontière 2/3 — le verdict embarque-t-il une intention ?** Une observation est vraie ou
fausse indépendamment de ce qu'on veut en faire ; une décision embarque l'intention d'agir.
Cette frontière est une **convention de nommage sans règle dure** : aucun cas mesuré de deux
consommateurs opposés d'un même verdict n'existe encore, donc le checker ne la police pas
(décision de la revue — une règle ici serait du méta-travail).

**Frontière 3/4 — vérifiable par le nom.** Un bloc `allowed`/`enable` de couche 4 nomme des
`_should_`/`_can_` (plus l'adressage Country). Suivie par les cliquets `LAYER4-RAW-GATE`
(termes moteur bruts) et `LAYER4-NON-DECISION` (noms de couche 2 dans un gate).

## 3. Où va une donnée ?

| Donnée | Véhicule | Jamais |
| --- | --- | --- |
| Tag / liste de pays | trigger `WA_AI_CONFIG_*` (archétype) | dans un gate de couche 4 hors adressage Country |
| Nombre partagé | `common/script_constants/wa_ai_<système>.txt` (`constant:`) | un `@` lu par deux fichiers |
| **Date partagée** | **trigger CONFIG nommé portant le littéral** | **un script constant — `date > constant:` est silencieusement toujours vrai (MEASURED 2026-08-29)** |
| Niveau de difficulté | les triggers `WA_AI_DIFFICULTY_*` et leurs compositions | une comparaison brute `difficulty > N` hors CONFIG — le mapping est non monotone (`[difficulty-mapping]`), `> N` ne peut pas dire « normal ou plus dur » |
| Nombre de tuning `ai_strategy value =` | littéral + commentaire d'une ligne | `constant:` n'y fonctionne pas (contextes validés 2026-08-16) |

## 4. Trous assumés du modèle

1. `ai_strategy value =` : le modèle couvre le **gating**, pas le **tuning** (cf. table).
2. Coût de performance d'une chaîne de triggers dans `enable` (réévalué en continu) :
   **ASSUMED** tant que la mesure du pilote NAVAL n'a pas tourné (critère d'arrêt).
3. La cadence d'évaluation `allowed` (au démarrage ?) vs `enable` est un fait moteur non
   mesuré : une conversion ne déplace **jamais** un terme d'un bloc à l'autre.
4. Lecteurs de couche 1 hors systèmes IA (`common/country_leader/00_traits.txt`,
   `common/scripted_localisation/`, `history/general/`…) : légitimes, hors périmètre du
   checker, listés dans la proposition §13.6.

## 5. Exceptions nommées

Tenues dans `tools/check_ai_layers.py` (données, pas commentaires) :

| Exception | Raison |
| --- | --- |
| `WA_AI_DIFFICULTY_*` garde son préfixe historique | 7 triggers, ~350 lectures ; renommer coûterait tout ça pour un gain nul |
| `WA_AI_DIFFICULTY_is_historical_normal` / `is_competitive_normal` sans lecteur | vocabulaire couche 1 de l'échelle à 5 niveaux, requis par les intentions de la phase 2b |
| paires `is_strategic_<r>_exporter` (CONFIG vs WA_AI) | capacité-compose-identité ; lecteurs dans des décisions générées, renommage différé |
| triggers à `is_in_faction_with` en couche 1 | les tags sont la donnée (frontière 1/2 ci-dessus) |
| renommage des triggers antérieurs au modèle | au fil de l'eau uniquement, jamais de commit de renommage massif |

## 6. Le motif `explain`

Chaque système migré livre un harnais `WA_TEST_explain_<système>` (contrat harnais v1) qui
journalise le verdict de chaque couche séparément, relu par
`python tools/read_harness_log.py --marker "EXPLAIN <SYS>" --interpret <sys>`. Critère
d'acceptation d'un lot : l'interpréteur nomme la couche qui bloque sans lecture humaine du
journal. Un harnais sans interpréteur livré n'est pas un explain.

## 7. Grammaire de nommage des gates (normalisée le 2026-08-30)

Un gate de couche 3 s'écrit `WA_AI_<SYS>_should_[<tag>_][not_]<intention>[_N]` :

- `<tag>` (minuscules) est présent si et seulement si le gate n'est lu que par les fichiers
  Country d'UN pays — le nom dit alors qui décide. Un gate de faction/région n'a pas de tag.
- `not_` est la seule forme de négation dans un nom (jamais `dont_`).
- Aucun mot de domaine (`front`/`diplomacy`/`theatre`/`invasion`) dans le nom — le domaine est
  porté par le fichier de stratégie qui lit le gate, pas par l'intention. Exception : les
  groupes de coïncidence où le mot de domaine est la seule chose qui distingue deux intentions
  distinctes à corps identique (règle Q4) — ils le gardent.
- Jamais `legacy_` — l'histoire vit dans git, pas dans les noms.
- `_N` final = échelon d'une séquence scriptée (les phases `chinese_war_1..5`, la ligne Staline
  `_10/_11`) : légitime tant que la séquence existe ; un `_2` qui ne fait pas partie d'une
  échelle est un nom à finir d'écrire.
- Suffixe `_allowed` : la moitié `allowed` d'un bloc converti dont l'`enable` a son propre gate.

Une observation de couche 2 contient `is_` / `has_` / `holds_` (`is_at_war_with_european_axis`,
`axis_holds_southern_sicily`).

