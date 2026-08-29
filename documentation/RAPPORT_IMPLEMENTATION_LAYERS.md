# Rapport d'implémentation — refactor layers, passe de nuit du 2026-08-29

**Branche : `ai-rework-layers-draft` (locale, JAMAIS poussée), 18 commits au-dessus de
`ai-rework`** (les 15 de la nuit + les 3 de la dédup du lendemain, §9). Rien n'est mergé ; chaque phase = un commit revertable seul. Ce rapport liste
tous les choix, toutes les déviations par rapport à la proposition
(`WA_AI_LAYERS_REFACTOR_PROPOSAL.md` corrigée par `REVUE_LAYERS_REFACTOR.md`), et tout ce qui
t'est dû côté jeu.

## 0. Résultat en cinq lignes

- **Les 774 blocs `allowed`/`enable` bruts du recensement sont convertis** (PRODUCTION 15,
  NAVAL 100, MILITARY 659) — corps déplacés **verbatim**, égalité token-à-token vérifiée
  machine à chaque bloc. `LAYER4-RAW-GATE = 0`.
- Phases 1, 2, 2b, 3a, 3c (re-scopée), 4 complet, checker + baselines, docs + guide : **faites**.
- Phase 3b (dédup des dates/seuils) : non faite pendant la nuit (§5 — c'était ta décision Q4),
  puis **exécutée le lendemain sur tes trois arbitrages** — voir §9. DATE-LEAK 141,
  NUMBER-LEAK 379.
- Les 4 checkers du dépôt + `check_ai_layers.py` (nouveau) : **tous à 0 erreur**.
- **Rien de tout cela n'a tourné dans le jeu.** Le boot test, la mesure perf NAVAL et les runs
  `explain` sont la contrepartie de ta revue (§7).

## 1. Les commits, dans l'ordre

| # | Commit | Contenu | Vérif |
| --- | --- | --- | --- |
| 0 | `docs(layers)` | snapshot des livrables pré-implémentation (proposition, revue, archive, harnais pdx, read_harness_log) | — |
| 1 | `phase 1` | −495 lignes de code mort (§2.1) | 4 checkers verts |
| 2 | `feat(tools) checker` | `check_ai_layers.py` (10 règles, selftest, baselines auto-générées) + AGENTS.md principe 4 / règle 4 réécrite **même commit** + `WA_AI_LAYERS.md` | selftest 10/10 |
| 3 | `phase 2` | classification réunifiée : moves china_front/commonwealth, renommages capacité, alias tués, chaîne pacific effondrée, Q2 `is_industrial_power` | NAME-COLLISION 2→0 |
| 4 | `phase 2b` | les 20 comparaisons `difficulty` brutes → intentions nommées (§2.3) | DIFFICULTY-RAW 20→0 |
| 5 | `phase 3a` | CONFIG purgé de tout état vivant : 7 verdicts évacués/scindés | CONFIG-LIVE 5→0 ; **checker à 0 ERROR pour la première fois** |
| 6 | `phase 4.1` | PRODUCTION fini (15 blocs) — le lot de référence | RAW-GATE 774→759 |
| 7 | `phase 4.2` | pilote NAVAL (100 blocs) + harnais `explain_naval` + interpréteur + correctifs revue de `read_harness_log.py` | 759→659 |
| 8-11 | `phase 4.3-4.6` | MILITARY par domaine : FRONT 261, INVASION 99, THEATRE 167, DIPLOMACY+MISC+AIFC 132 | 659→0, exact à chaque lot |
| 12 | `phase 3c` | les 19 drapeaux `always` → `WA_AI_CONFIG_FLAGS.txt` | verts |
| 13 | `phase 6` | docs, skills, guide contributeur | check_skill_refs 0 |
| 14 | ce rapport + verdicts de la vérification adversariale | — | — |

## 2. Ce qui a été fait, avec les décisions prises

### 2.1 Phase 1 — nettoyage (décisions notables)

- **12 des « 15 » triggers CONFIG morts supprimés, pas 15** : les 2 sous-niveaux de difficulté
  (`is_historical_normal`, `is_competitive_normal`) sont GARDÉS — c'est le vocabulaire de
  couche 1 de l'échelle à 5 niveaux (exception nommée dans le checker) ; et
  `pacific_high_risk` n'était pas supprimable en phase 1 (lecteur interne vivant — c'est la
  correction de la revue), il est parti avec l'effondrement de chaîne en phase 2.
- Q6 (tes 8 triggers assault/support tanks) : **supprimés**, conformément à ta réponse.
- **+2 morts trouvés au-delà de la proposition** : `WA_AI_build_infantry`, `WA_test54` (MISC).
- `use_heavy_at` : 20 branches mortes + 4 membres d'OR retirés de
  `WA_AI_DIVISION_CREATOR_effects.txt` après classification de chaque site (aucun `if` à `else`
  attaché — le danger d'orphelin vérifié AVANT suppression) ; le trigger reste (lecteurs
  scripted_loc), avec un commentaire `[use-heavy-at-off]`.
- Chaque nom supprimé re-greppé sur tools/, tests/, .claude/, localisation/, interface/ : zéro
  lecteur partout.

### 2.2 Phase 2 — classification (déviations)

- **Pas d'alias de compatibilité temporaires** (la proposition en prévoyait) : tous les lecteurs
  migrent dans le même commit — l'alias n'a de sens qu'étalé dans le temps.
- Renames : `is_major_naval → has_ocean_going_fleet`, `is_major_continental → has_mass_army`,
  `major_country → WA_AI_CONFIG_is_industrial_power` (ta décision Q2 ; le corps compose
  maintenant `is_major_country` + la clause >99 usines — même sémantique, divergence explicite).
- La chaîne pacific est UNE observation `WA_AI_MILITARY_pacific_high_risk` définie dans
  MILITARY_triggers ; `pacific_war_active` et l'alias CONFIG sont morts.
- Les docs vivantes (MILITARY_SYSTEM, TYPES_REFERENCE, LEND_LEASE_RELIEF_DESIGN) renommées dans
  le même commit ; `tools/fix_registry.json` volontairement NON réécrit (historique gelé).

### 2.3 Phase 2b — difficulté (changements de comportement VOULUS)

Les 20 sites vivants, deux familles d'intention (le détail par site est dans le message du
commit 4) :

- famille « assists » (`> 2` commenté *Hard and above*) → `WA_AI_CONFIG_cheats_enabled` {1,4} :
  les assists s'allument désormais en **Hist Hard** (le bouton dont le tooltip les promet) et
  s'éteignent en **Comp Normal** (dont le tooltip ne les promet pas). L'ancien code faisait
  l'inverse sur les deux points.
- famille « au-dessus d'Easy » (`> 1`, compensations joueur héritées de vanilla) →
  `NOT { is_historical_easy }` : la compensation couvre désormais aussi Hist Hard (valeur 1).

**Résidu ASSUMED à ton boot test** : `WA_AI_CONFIG_cheats_enabled` est maintenant appelé dans le
bloc `allowed` de l'idée `hard_ai` (`common/ideas/_WA_ai.txt`) — un scripted trigger dans un
`allowed` d'idée n'a pas de précédent mesuré dans le dépôt.

### 2.4 Phase 3a — CONFIG déclare, les systèmes observent

7 verdicts évacués ou scindés (italian_power_shares, western_bulwark, penalised_xp → TEMPLATES,
needs_cv_planes → PRODUCTION, faces_strategic_bombing scindé — l'union prouvée inchangée car son
unique lecteur portait déjà le même balayage —, should_build_capitals scindé avec la fenêtre
`naval_treaty_era_expired` restée en couche 1, RAILWAY_override scindé setup/vivant).
**Déviation** : `needs_cv_planes` est allé dans `WA_AI_PRODUCTION_carrier_planes.txt` (son
lecteur le plus proche), pas `PRODUCTION_navy.txt` comme écrit dans la proposition.

### 2.5 Phase 4 — les 774 blocs (le cœur de la nuit)

- **Méthode : pipeline déterministe, pas de LLM dans la boucle de conversion.** Tu avais
  autorisé les workflows ; je les ai réservés à la **vérification adversariale** (§6) — la
  conversion elle-même est un script qui déplace le corps verbatim et **refuse** tout bloc dont
  les tokens de destination ≠ tokens d'origine. 774/774 vérifiés à l'octet près, jamais un
  terme déplacé entre `allowed` et `enable` (la cadence d'évaluation étant un fait moteur non
  mesuré).
- **Nommage : la stratégie EST l'intention.** Chaque gate devient
  `WA_AI_<SYS>_should_<intention-de-la-stratégie>` (`should_not_` pour les `dont_`). 1 seul
  doublon d'intention réel trouvé et partagé (`dont_defend_vichy`, GER+ITA, corps identiques).
- Destinations : `WA_AI_NAVAL_triggers.txt` (nouveau), `WA_AI_MILITARY_<DOMAIN>_gate_triggers.txt`
  ×5 (nouveaux), `WA_AI_PRODUCTION_country_triggers.txt` + `_lend_lease_triggers.txt` (nouveaux),
  et le gate AIFC dans `WA_AI_AIFC_triggers.txt` (la règle AGENTS du panneau AIFC).
- Le bloc GER_FRONT:1429 (le `if`-dans-`OR` + le typo `has_war_With`) a été déplacé **tel quel**
  — le corriger est le sujet WORK.md §3.6, pas ce refactor.
- L'adressage Country (`allowed = { tag = X }`) n'a jamais bougé.

### 2.6 Le checker (`tools/check_ai_layers.py`)

10 règles, `--selftest` avec une fixture par règle (10/10), baselines **auto-générées** —
jamais recopiées de la proposition (correction de la revue : les vrais comptes initiaux étaient
420 dates / 495 seuils / 158 lectures CONFIG, pas 430/499/54). `--update-baseline` accepte les
baisses ET les hausses justifiées (2 hausses cette nuit, toutes deux des déplacements comptés,
justifiées dans les messages de commit). Exceptions en DONNÉES avec leur raison (vocabulaire
difficulté, paires exporteurs capacité-compose-identité, renommage au fil de l'eau).

## 3. État final des compteurs

| Compteur | Début de nuit | Fin | Sens |
| --- | --- | --- | --- |
| LAYER4-RAW-GATE | 774 | **0** | plus un seul gate brut dans `ai_strategy` |
| DIFFICULTY-RAW | 20 | **0** | plus une comparaison `difficulty` hors CONFIG |
| CONFIG-LIVE | 6 | **0** | CONFIG ne lit plus le monde vivant |
| NAME-COLLISION / DUP-DEF / CONFIG-DEAD | 5 / 2 / 15 | **0 / 0 / 0** | (morts : supprimés ou exceptés) |
| LAYER4-READS-CONFIG | 158 | 136 | résidu = blocs `abort` et contextes hors gate — hors recensement d'origine, gelé par le cliquet |
| LAYER4-NON-DECISION | 740 | 361 | idem — lot futur |
| DATE-LEAK / NUMBER-LEAK | 420 / 494 | 420 / 495 | voir §5 (3b) ; +1 = déplacement compté de `needs_cv_planes` |

## 4. Écarts à la proposition, tous listés

1. Pas d'alias temporaires en phase 2 (§2.2).
2. `needs_cv_planes` → `carrier_planes.txt` (§2.4).
3. Phase 3c re-scopée : `WA_AI_CONFIG_FLAGS.txt` créé (19 drapeaux, pas 22 — le vrai compte
   post-nettoyage), **pas** de `WA_AI_CONFIG_WINDOWS.txt` — après la phase 4 il n'existe qu'UNE
   fenêtre calendaire pure ; le fichier naîtra avec la dédup 3b. Les lignes « ce qui le ferait
   basculer » des drapeaux non commentés te sont dues (connaissance owner).
4. Phase 3b non exécutée (§5).
5. MILITARY converti en 4 lots/commits (FRONT, INVASION, THEATRE, DIPLOMACY+MISC+AIFC) au lieu
   de 7 familles — même contenu, découpage par domaine de fichier.
6. Workflows utilisés pour la vérification, pas pour la conversion (§2.5).
7. En passant (hors périmètre strict, faible risque, commentaires seuls) : la table
   `[difficulty-mapping]` et la correction des labels périmés de `00_static_modifiers.txt`
   étaient déjà dans l'arbre avant la nuit.

## 5. Phase 3b : pourquoi je ne l'ai PAS faite, délibérément

Le but de 3b (« une date non nommée est une date perdue ») est **aux trois quarts atteint par la
phase 4** : chaque date et chaque seuil vit désormais À L'INTÉRIEUR d'un trigger nommé par son
intention (`date > 1942.1.1` n'est plus anonyme dans un bloc de stratégie — il est dans
`WA_AI_MILITARY_should_jap_…`). Ce qui reste de 3b est la **dédup** : décider si les 56 sites
`1942.1.1` disent la même chose. C'est exactement ta question Q4, que tu as réservée (« l'owner
sait si ces 56 sites disent la même chose »), et la règle de la nuit était : **un site à
intention illisible reste littéral, je ne devine jamais**. Déduire 161 intentions de dates
militaires sans toi aurait été l'erreur la plus probable de la nuit. Les compteurs DATE-LEAK
(420) et NUMBER-LEAK (495) restent gelés par le cliquet ; la dédup se fera lot par lot quand tu
auras tranché Q4 — et c'est à ce moment que `WA_AI_CONFIG_WINDOWS.txt` prendra son sens.

## 6. Vérification adversariale (workflow, 10 relecteurs indépendants)

Chaque relecteur a comparé `git show ai-rework:<fichier>` à l'état final, avec mission de
prouver une différence sémantique. Verdicts :

| Relecteur | Périmètre | Verdict |
| --- | --- | --- |
| naval:GER+DEFAULT | 19 blocs GER (+110 payloads), 5 DEFAULT, la réutilisation vichy | **OK** — 0 différence, token-à-token |
| naval:ENG+USA | 24 blocs, diffs entiers relus | **OK** — seuls les corps d'enable ont bougé |
| mil:GER_FRONT | 34 blocs, dont le `if`-dans-`OR` :1429 et les typos `has_war_With`/`has_War_With` | **OK** — préservés verbatim, pas de croisement dans les familles jumelles (GRE, frontline_requests) |
| mil:SOV+JAP_FRONT | 62 blocs + inventaire | **OK** — payloads/allowed/abort intouchés |
| mil:THEATRE | USA 16 + SOV 39 (les 26 mixtes inclus) | **OK** — la seule « différence » est l'effondrement d'alias pacific, prouvé vide |
| mil:DIPLO+INV | 58 sites, **contrôle positif du comparateur** (corruption volontaire détectée) | **OK** |
| production | les 15 + les blocs non touchés | **OK** — 13/15 verbatim, 2 égalités sémantiques (renames 3a) prouvées |
| difficulty-2b | les 20 sites vs la table `[difficulty-mapping]` | **OK** — les 2 motifs d'intention exacts partout ; a trouvé le commentaire périmé `# 2 or 4` de cheats_enabled (corrigé au commit final) |
| renames-2-3a | 11 anciens noms, 12 remplaçants | **OK** — zéro lecteur périmé, chaque remplaçant défini une fois, aucun orphelin |
| phase1-deletions | 19 noms, DIVISION_CREATOR (−137/0), chaînes else | **OK** — aucun else orphelin (scan mécanique), accolades 1792/1792 |

**10/10 OK, 0 CONCERNS, 0 BROKEN.** Résidu commun, honnête (**ASSUMED**, standard) : un scripted
trigger appelé depuis un gate évalue avec les mêmes scopes ROOT/THIS que l'inline qu'il
remplace — non observable depuis les fichiers, c'est ce que ton boot test + l'explain couvrent.
Observations cosmétiques consignées : `should_focus_on_land_war_in_north_africa` sans préfixe
`eng_` alors que son corps est ENG-spécifique ; quelques `allowed` non convertis (sous le
plancher RAW) gardés tels quels.

## 7. Ce qui t'est dû — rien de tout cela n'a vu le jeu

| # | Run | Commande / geste | Ce que ça tranche |
| --- | --- | --- | --- |
| 1 | **Boot test** | lancer le jeu, lire error.log | 160 fichiers touchés parsent ; l'idée `hard_ai` (§2.3) charge |
| 2 | **Perf NAVAL (critère d'arrêt §4.2)** | ta sauvegarde de référence, N ticks avant/après (avant = branche `ai-rework`) | si la dégradation dépasse ton seuil Q7, on revert les lots 4.x — c'est prévu pour |
| 3 | **explain NAVAL** | `tag GER` puis `event wa_explain_naval.1`, puis `python tools/read_harness_log.py --marker "EXPLAIN NAVAL" --interpret naval --errors` | le critère d'acceptation du lot pilote : l'outil nomme la couche qui bloque |
| 4 | **Bundles géographiques** | les 6 `tests/wa_*_geographic.txt` | non-régression MILITARY |
| 5 | **Sondes q1e / q2e / difficulté** | compléter le harnais pdx (3 sondes d'une ligne), 1 relance | ferme Q1/Q2 pour de bon + confirme le 0-indexage de `difficulty` |
| 6 | Décision Q4 (dédup dates) + lignes « bascule » des drapeaux | — | débloque la vraie 3b et finit 3c |

## 8. Comment revoir (suggestion)

```bash
git log --oneline ai-rework..ai-rework-layers-draft
```
Un commit = un lot = un revert possible. Les gros diffs (4.x) se relisent par échantillon : le
corps de chaque trigger `*_gate_triggers.txt` doit être l'ancien bloc au token près — c'est ce
que la machine a vérifié 774 fois et que les 10 relecteurs ont contre-vérifié par sondage. Si un
lot te déplaît : `git revert <commit>` + `python tools/check_ai_layers.py --update-baseline`
dans le même commit de revert.

## 9. Dédup (phase 3b) — exécutée le 2026-08-30, sur tes trois décisions

Décisions owner : **véhicule hybride** ; **périmètre dates + seuils lots 5/6** ; **LAW inclus**
(déviation assumée du §11, ses dates seulement — le fichier reste par ailleurs le sujet
« miroir vanilla »).

- **Dates** : 37 bornes calendaires partagées dans le NOUVEAU
  `common/scripted_triggers/WA_AI_CONFIG_WINDOWS.txt` (le fichier que la 3c attendait), 279
  sites remplacés (les répétées ≥4×, aborts inclus — 51 sites d'abort). `after_X` et `before_X`
  portent chacun leur littéral (NOT{after} ≠ before le jour même de la borne). Noms d'époque
  seulement là où le sens est hors de doute (`global_war_begins`, `overlord`) ; calendaires +
  commentaire ailleurs — un nom d'époque faux serait pire qu'un nom transparent, renommage
  trivial (un grep). DATE-LEAK 420 → **141** (les <4× restent gelés dans leurs triggers
  d'intention).
- **Lot 5 (invasions)** : les 75 gardes identiques `surrender_progress < 0.1` (« le front
  intérieur du lanceur tient ») = UNE observation nommée
  `WA_AI_MILITARY_invasion_launcher_not_collapsing`. Le 0.1 existe une fois.
- **Lot 6 (production)** : constantes uniquement dans les contextes `constant:` PROUVÉS par
  l'usage — l'échelle de taille industrielle `wa_ai_production.industry` (20/29/49/99/299,
  29 lectures) et les bornes donneur lend-lease `wa_ai_lend_lease.donor` (75000/300000/199/479,
  14 lectures). Les compléments `< borne+1` sont réécrits `NOT = { > borne }` (comptes entiers :
  équivalence exacte, 5 sites) — une seule quantité, un seul nom, au lieu d'un second nombre
  qui dérive. Le miroir registry `truck_stock_starve_floor` devient une lecture directe de sa
  constante propriétaire (le groupe quitte le manifest, 78 groupes, registry.md régénéré).
  NUMBER-LEAK 495 → **379** (les valeurs uniques restent gelées).
- LAYER4-READS-CONFIG 136 → 151 : lectures de milestones depuis les blocs `abort` — les aborts
  étaient hors recensement ; un lot « gates d'abort » reste à faire, le cliquet le tient.

**Dû côté jeu, en plus du §7** : les milestones et constantes passent par les mêmes contextes
que l'existant (prouvés par l'usage), mais le boot test couvre maintenant aussi
`WA_AI_CONFIG_WINDOWS.txt` et les deux fichiers de constantes étendus.

## 10. Factorisation (lots A-D) — exécutée le 2026-08-30

Sur la base de `ANALYSE_FACTORISATION_TRIGGERS.md`, quatre lots, un commit chacun :

- **A** : 77 groupes de gates multi-domaines token-identiques fusionnés — **−96 définitions**,
  canonique sans suffixe de domaine, garde-fou d'égalité de signature avant chaque fusion.
- **C** : alias effondrés — `is_allies_member` → `CONFIG_is_in_allies` (85 lectures, un seul
  vocabulaire), la famille morte `owns_naval_*` supprimée de bout en bout (alias ET cibles CONFIG,
  commentaire [atlantic-naval] annoté), `italy_theatre_contested` dé-aliasé,
  `ast_protect_home` unifié. GARDÉS sciemment : l'API `RESEARCH_needs_*` (170 lectures générées),
  le hub `ground_is_enabled` (21 lectures — pas une simple marche), `refinery_region_priority`
  (alias d'intention), les alias armor (sujets WORK.md vivants).
- **D** : 8 observations partagées extraites (44 copies inline remplacées par sous-séquence de
  tokens, sous-arbres équilibrés uniquement) : `french_africa_flank_quiet` (le pavé VIC de 462
  tokens), `sov_free_of_leningrad_commitment`, `german_soviet_war_running`,
  `axis_holds_{southern,northern}_sicily` (états 1032/115 vérifiés), `at_war_in_southeast_asia`,
  `at_war_with_european_axis`, `paris_held_by_own_faction` (855 = Paris, l'ancre RCZ).
- **B** : deux fusions de conception (`should_ger_hold_festungen` ×5→1,
  `should_axis_minor_answer_german_support_request` ×4→1). **Deux renoncements documentés** :
  les `country_owns_*` (le header d'`ownership_triggers` impose un trigger par paire Exclusive —
  les corps identiques y sont un contrat, pas un doublon) et les 26 `DOCTRINES_SELECT_*`
  (API `ai_will_do` — sujet outillage replacer).

Vérification : signature identique exigée à la fusion (lot A), sous-arbres exacts (lot D),
sondages `git show` post-hoc — le corps canonique de `husky_fire` égale l'ancien **modulo
l'expansion des observations du lot D** : les deux passes composent. Checkers : 0 erreur
partout ; NUMBER-LEAK 356→352, NOT-MULTI 76→72 (corps dupliqués disparus).
Bilan net des quatre lots : **environ −110 définitions** et 44 corps raccourcis.

