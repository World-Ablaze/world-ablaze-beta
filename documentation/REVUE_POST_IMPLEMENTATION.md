# Revue post-implémentation — refactor layers (`ai-rework-layers-draft`)

Revue du 2026-08-29. Relecteur : Fable 5, session indépendante, sans connaissance de la session
d'implémentation. Périmètre : `git diff origin/ai-rework..ai-rework-layers-draft` (29 commits,
225 fichiers, +18133/−11641 — **MEASURED**, `git diff --stat`). Rien n'a été poussé ni corrigé par
cette revue ; sa seule écriture est ce fichier.

Méthode : les vérifications token-à-token ci-dessous utilisent un **comparateur écrit pour cette
revue** (extraction de bloc par équilibrage d'accolades, strip des commentaires, tokenisation,
expansion récursive des triggers nommés), pas les scripts de l'archive d'audit ni ceux de
l'implémenteur. Étiquettes : MEASURED / DERIVED / ASSUMED, contrat d'AGENTS.md.

---

## 1. Verdict global

**L'implémentation tient ses promesses mécaniques ; rien n'a tourné dans le jeu, et l'ordre
prudentiel de la proposition (perf NAVAL avant MILITARY) n'a pas été suivi.**

- **MEASURED** — les 5 outils sortent à 0 : `check_ai_layers.py` (0 ERROR, selftest 10/10),
  `check_constants.py` (0/0/11 info), `check_worklist.py` (0/0/0), `check_skill_refs.py` (0 dead ref).
- **MEASURED** — 15 blocs échantillonnés à travers NAVAL / PRODUCTION / MILITARY (§4) : tous
  token-identiques à l'original, ou identiques modulo une substitution déclarée dont le littéral
  est préservé à l'octet près.
- **MEASURED** — deux balayages mécaniques du dépôt entier : **0 appel orphelin** (5685 appels
  `WA_AI_* = yes/no` vérifiés contre l'union triggers+effects) et **0 gate mort** (658 définitions
  de gates, toutes lues) — la passe de 164 renommages et les fusions n'ont perdu aucun lecteur.
- Ce qui empêche le « prêt à merger » : le boot test, la mesure perf NAVAL (critère d'arrêt déclaré
  de la proposition §4.2), les runs `explain`, et trois écarts non déclarés dans le rapport (§7).

---

## 2. Bilan contre les objectifs initiaux (proposition §1.3)

| Promesse | Verdict | Preuve |
| --- | --- | --- |
| 1. Modèle 4 couches vérifiable par grep, porté par le nom | **TENUE** | **MEASURED** — `WA_AI_LAYERS.md` (modèle + grammaire §7), AGENTS.md principe 4 + règle 4 réécrite dans le même commit que le checker (`e2a12b47e`, exigence bloquante n°2 de la revue pré-implémentation, respectée) |
| 2. Checker à cliquet (`check_ai_layers.py`) | **TENUE** | **MEASURED** — 10 règles, `--selftest` une fixture par règle (10/10), `RATCHET-STALE` force la mise à jour à la baisse, baselines auto-générées (correction de la revue appliquée : 420/494/158 mesurés, pas 430/499/54). Vérifié par re-run du checker sur 7 arbres de commits intermédiaires : chaque baseline committée égale le compte mesuré de son propre arbre |
| 3. Migration par système, chaque lot avec son harnais de diagnostic | **PARTIELLEMENT TENUE** | Migration par système : faite (774 → 0 en 6 lots, compte exact à chaque commit — **MEASURED**, baselines). Harnais : **un seul `explain` existe (NAVAL)**. PRODUCTION et les 659 blocs MILITARY sont partis **sans** explain — la proposition §7.2 le disait « obligatoire, livré dans le même lot, pas après », avec critère d'acceptation. **MEASURED** : `ls common/scripted_effects/WA_TEST_*` ne contient que `explain_naval`. Cet écart n'est PAS dans la liste « tous listés » du rapport §4 |
| 4. Aucun changement de comportement hors exceptions déclarées | **TENUE** (sur l'échantillon) | §4 et §5 ci-dessous. Déclarés : phase 2b (20 sites difficulté), dédup 3b (réécritures `< N+1` → `NOT { > N }`, équivalence entière exacte). Rien d'autre trouvé |
| 5. Guide contributeur français | **TENUE** | **MEASURED** — `documentation/GUIDE_CONTRIBUTEUR_IA.md`, 111 lignes, structure du §9 de la proposition |

Non-objectifs (§1.4) :

| Engagement | Verdict | Preuve |
| --- | --- | --- |
| Pas de réécriture du système de lois | **RESPECTÉ** (déviation déclarée) | **MEASURED** — `WA_AI_LAW_triggers.txt` : 23 lignes changées, toutes des substitutions date→fenêtre CONFIG, zéro autre terme touché (diff filtré). La déviation « ses dates seulement » est déclarée au rapport §9 |
| Pas de push | **RESPECTÉ** | **MEASURED** — `git branch -vv` : la branche n'a pas d'upstream |
| Diffs sémantiquement vides | **RESPECTÉ** sur l'échantillon | §4 |

**Un écart d'ORDRE non déclaré comme tel** : la proposition (§10.1) plaçait la mesure perf du
pilote NAVAL **avant** la conversion MILITARY — « 659 blocs convertis sur une hypothèse de
performance fausse seraient irréversibles en pratique » (§4.2). Les phases 4.3-4.6 ont été
exécutées la même nuit, sans la mesure. **DERIVED** (ordre des commits + rapport §7 « rien n'a vu
le jeu ») : le critère d'arrêt est devenu un critère de *revert* — il porte maintenant sur 759
blocs au lieu de 100. Les commits restent revertables un par un (mitigation réelle), mais c'est
exactement le scénario que le §4.2 voulait éviter, et le rapport ne le nomme pas dans ses écarts.

---

## 3. Le cliquet, tracé commit par commit

**MEASURED** — j'ai re-exécuté le checker sur les arbres de 7 commits intermédiaires (worktrees
jetables). Chaque baseline committée égale le compte mesuré de son arbre. État final :

| Compteur | Départ | Fin | Chemin notable |
| --- | --- | --- | --- |
| LAYER4-RAW-GATE | 774 | **0** | −15 (4.1), −100 (4.2), −261, −99, −167, −132 : exact à chaque lot |
| DIFFICULTY-RAW | 20 | **0** | phase 2b |
| DATE-LEAK | 420 | **130** | −279 (3b), −18 (lot A), **+7** (ré-inline des bornes mono-lecteur, déclaré §11 du rapport) |
| NUMBER-LEAK | 494 | **351** | −116 (3b), −23 (lot A), −4 (lot B), −1 (mop-up) |
| LAYER4-READS-CONFIG | 158 | **183** | +9 (2b), −4 (3a), −17/−16 (4.x), **+15** (3b, aborts — déclaré §9), **+32 (lot C — voir ci-dessous)** |
| LAYER4-NON-DECISION | 740 | **330** | −379 (4.x), **−31 (lot C)** |

**La hausse +32 du lot C n'est déclarée nulle part.** **MEASURED** (re-run du checker sur les
arbres avant/après `910d1f7c8`) : l'effondrement de l'alias `WA_AI_MILITARY_is_allies_member` →
`WA_AI_CONFIG_is_in_allies` transfère ~32 lectures du compteur NON-DECISION vers READS-CONFIG —
la dette ne disparaît pas, elle change de règle. Le message du commit documente la fusion (« one
vocabulary for one fact ») mais pas l'échange de compteurs ; le rapport s'arrête à « 136 → 151 »
(§9) et **le chiffre final 183 n'apparaît dans aucun document** — seule la mission de cette revue
le nommait. Fond du problème : « un seul vocabulaire par fait » (lot C) et « la couche 4 ne lit
jamais CONFIG » (frontière 3/4) tirent en sens opposés sur les observations d'identité très lues.
C'est un choix défendable — mais c'est un choix, et il n'est écrit nulle part.

À noter aussi : la sémantique de l'alias était **MEASURED** vide (le corps origin de
`is_allies_member` est exactement `WA_AI_CONFIG_is_in_allies = yes`) — aucun risque de
comportement, uniquement une question d'architecture et de traçabilité.

---

## 4. Vérification par échantillonnage — 15 blocs, 3 systèmes

Comparateur indépendant (§ méthode). « IDENTIQUE » = même séquence de tokens, commentaires exclus.
« IDENTIQUE\* » = identique après expansion des triggers nommés introduits par le refactor, chaque
littéral vérifié préservé dans sa définition. Tous **MEASURED**.

| # | Bloc (origin) | Passes traversées | Verdict |
| --- | --- | --- | --- |
| 1 | NAVAL `GER_gank_everyone` | conversion 4.2 | IDENTIQUE |
| 2 | NAVAL `GER_focus_on_north_africa` | conversion 4.2 | IDENTIQUE |
| 3 | NAVAL `GER_battle_of_britain_yes` | conversion + fenêtre 3b | IDENTIQUE\* (`date < 1940.11.1` → `WA_AI_CONFIG_before_1940_11`, littéral exact en CONFIG:1413) |
| 4 | NAVAL `GER_legacy_avoid_the_med` | conversion + grammaire (`legacy_` retiré du nom du trigger) | IDENTIQUE |
| 5-6 | PRODUCTION `WA_DEFAULT_production_navy_*` ×4 sites (dont un `= no`) | scission 3a de `majors_should_build_capitals` | IDENTIQUE\* — corps recomposé égal : `any_country_of` (monde vivant) sorti de CONFIG vers PRODUCTION, `date > 1948.1.1` reste en couche 1 sous `naval_treaty_era_expired`, polarité `= no` conservée |
| 7 | MILITARY `GER_dont_suicide_into_maginot_line` | conversion 4.3 + grammaire (`dont_` → `not_`) | IDENTIQUE — **le `if`-dans-`OR` et le typo `has_war_With` préservés à l'octet** (le défaut §3.6 est bien resté un sujet séparé, non « corrigé en passant ») |
| 8-9 | MILITARY `CHI_war_with_JAP_AI_{DIPLOMACY,FRONT}` | conversion 4.3+4.6 → fusion lot A → renommage | IDENTIQUE — les deux corps origin sont token-identiques entre eux et au trigger fusionné |
| 10 | MILITARY `ALLIES_husky_fire_INVASION` | conversion → extraction lot D (`axis_holds_{southern,northern}_sicily`) | IDENTIQUE\* — la recomposition gate + observations lot D redonne le bloc origin token à token (états 115/1032 vérifiés) |
| 11 | MILITARY `ALLIES_dday_fire_FRONT` | conversion → fenêtres 3b (`overlord` ×2, `global_war_begins`) → alias lot C (`is_in_allies`) | IDENTIQUE\* — cas le plus composé de l'échantillon, trois passes empilées, littéraux 1944.6.6 / 1942.1.1 exacts |
| 12-13 | MILITARY `JAP_chinese_war_invasions_3_INVASION`, `JAP_Japan_southern_expansion_1_fire_INVASION` | conversion + fusion lot A (canonique dans le fichier FRONT) | IDENTIQUE — les dates de séquence scriptée (`1942.1.1`+`1942.1.15`) restées littérales dans le trigger d'intention, conformément à la règle « un nom par intention » |
| 14-15 | MILITARY `SOV_{defense_of_sevastapol,winter_war_invasion_time}_THEATRE` | conversion 4.5 + fenêtres | IDENTIQUE\* |

Balayages mécaniques complémentaires (dépôt entier, `common/` + `events/`) :

| Balayage | Résultat |
| --- | --- |
| Appels `WA_AI_* = yes/no` sans définition (triggers ∪ effects) | **0 / 5685** — **MEASURED** |
| Gates définis jamais lus (les 8 fichiers de gates, 658 définitions) | **0** — **MEASURED** |
| BOM dans les fichiers script neufs (7 vérifiés dont CONFIG et les 5 gate_triggers) | **0** — **MEASURED** (et `check_worklist` `BOM-IN-SCRIPT` couvre la zone) |
| Fichiers touchés hors `common/`, `events/`, `tools/`, `documentation/`, `.claude/`, AGENTS.md | **0** — **MEASURED** |

**Limite honnête de l'échantillon** : 15 blocs sur 774 (~2 %), choisis pour couvrir les trois
systèmes, les quatre domaines MILITARY et les empilements de passes — pas tirés au hasard. La
confiance sur les 759 autres repose sur : la vérification machine de l'implémenteur (774/774,
refus sur mismatch), ses 10 relecteurs adversariaux (dont un contrôle positif de corrupteur), et
la convergence de mes 15 sondes indépendantes avec zéro écart. **DERIVED**, pas MEASURED-exhaustif.

---

## 5. Les changements de comportement déclarés

### 5.1 Phase 2b — les 20 comparaisons de difficulté

**MEASURED** — la table `[difficulty-mapping]` (CONFIG:11-26) : 0=Easy hist, **1=Hard hist**,
2=Normal hist, 3=Normal comp, 4=Hard comp — non monotone, la valeur suit le NOM moteur du
checkbox, pas sa position visuelle.

- `WA_AI_CONFIG_cheats_enabled` = `is_historical_hard` {1} ∪ `is_competitive_hard` {4} — **exact**
  contre la table (**MEASURED**, CONFIG:39-68 : bornes 0<d<2 et d>3).
- Sites vérifiés sur le diff (`events/WA_AI_GER.txt:931`, `common/ideas/_WA_ai.txt:154`, CHI,
  LAR_Spain) : le motif est bien `difficulty > 2` → `cheats_enabled` (famille assists) et
  `difficulty > 1` → `NOT { is_historical_easy }` (famille compensations) — conformes au message
  du commit `c5527bc0c`, qui liste les 20 sites et assume les deux inversions de comportement
  (assists désormais ON en Hist Hard / OFF en Comp Normal).
- **Complétude** : **MEASURED** — `DIFFICULTY-RAW = 0` (périmètre : tout `common/` + `events/`,
  commentaires strippés) ; mon propre grep ne trouve plus que des comparaisons dans des blocs
  commentés de `z_WA_ai.txt`. Rien d'autre n'a changé sur cet axe.
- Résidu correctement étiqueté par l'implémenteur : un scripted trigger dans l'`allowed` d'une
  idée (`hard_ai`) est **ASSUMED** fonctionner — sans précédent dans le dépôt, c'est au boot test.

### 5.2 Dédup 3b

- **Garde d'invasion** : **MEASURED** — origin `events/WA_AI_invasions.txt` contient **86**
  `surrender_progress < 0.1` ; l'arbre final en contient 0 et **86** lectures de
  `WA_AI_MILITARY_invasion_launcher_not_collapsing` (corps = le littéral, défini une fois).
  Substitution 1:1 exacte. *Le commentaire du trigger et le rapport disent « 75 » — le compte
  réel est 86 ; inexactitude documentaire sans effet.*
- **Fenêtres** : 5 vérifiées (`before_1940_11`, `naval_treaty_era_expired`,
  `after_global_war_begins`, `before_overlord`, `after_overlord`) — chaque littéral exact,
  `after_X` et `before_X` portent chacun leur littéral (la différence au jour de borne est
  préservée, comme annoncé).
- **Seuils** : la réécriture `< N+1` → `NOT { > N }` sur comptes entiers est une équivalence
  exacte (**DERIVED**, arithmétique) ; les constantes n'ont été introduites que dans des contextes
  `constant:` prouvés par l'usage existant (**MEASURED** pour l'échelle industrie et les bornes
  donneur, par leurs lectures préexistantes).

---

## 6. Résidus et risques

### 6.1 Ce que seul le jeu peut trancher (rien n'a tourné — **MEASURED**, rapport §7, aucune trace de run)

| # | Run dû | Ce qui reste ASSUMED tant qu'il n'a pas tourné |
| --- | --- | --- |
| 1 | Boot test | ~160 fichiers touchés parsent ; l'`allowed` d'idée avec scripted trigger (`hard_ai`) ; les deux fichiers de constantes étendus ; CONFIG ré-unifié à 1659 lignes |
| 2 | Perf NAVAL (critère d'arrêt §4.2 — seuil Q7 jamais fixé) | le coût d'une chaîne de triggers dans `enable` réévalué en continu. Contre-indice rassurant mais partiel : les 273 blocs nommés de PRODUCTION tournent depuis des mois (**DERIVED**) |
| 3 | `explain_naval` + `read_harness_log --interpret naval` | le critère d'acceptation du pilote ; et le résidu standard : un trigger appelé depuis un gate évalue avec les mêmes scopes ROOT/THIS que l'inline (**ASSUMED**, non observable depuis les fichiers) |
| 4 | Les 6 bundles géographiques | non-régression MILITARY |
| 5 | Sondes q1e (`if`+`else` dans un `OR`), q2e (`NOT` premier-enfant), sonde difficulté | **MEASURED** — les sondes ne sont PAS dans `WA_TEST_pdx_semantics.txt` (q1a-c/q2a-d/q3 seulement). Q2 reste « close sous réserve » ; le 3ᵉ site Q1 (pathfinding:268, gardé par `else`) reste non mesuré |

### 6.2 Cliquets non nuls — nature du résidu

- **READS-CONFIG 183** : majoritairement des blocs `abort`/hors-gate (hors recensement d'origine)
  **plus** les ~32 lectures directes du lot C (§3). Le lot « abort-gates » annoncé les traitera —
  mais la part lot C est un choix de conception, pas une dette de migration : elle ne baissera pas
  sans revenir sur « un seul vocabulaire ».
- **NON-DECISION 330** : gates nommant des observations (couche 2) directement. Lot futur, gelé.
- **DATE-LEAK 130 / NUMBER-LEAK 351** : les <4× et valeurs uniques, gelés dans leurs triggers
  d'intention — l'objectif « une date non nommée est une date perdue » est atteint pour l'anonymat
  (plus aucune date nue dans un bloc de stratégie), pas pour la dédup complète. Conforme au plan.

### 6.3 Les 26 `TODO(owner)`

**MEASURED** — 26 fenêtres calendaires purement calendaires (`after_1938`…), chacune avec sa liste
de lecteurs en commentaire. C'est le reliquat assumé de la décision Q4 (« je ne devine jamais une
intention »). Risque réel tant que ça dure : un contributeur lit `WA_AI_CONFIG_after_1938` comme
un nom stable et l'ajoute à un 9ᵉ lecteur avec une intention différente — le jour où l'owner
éclate la fenêtre par intention, ce lecteur sera mal classé. Le TODO le dit ; il faut surtout que
la liste de lecteurs ne rouille pas. Détail cosmétique : `before_1936_5_16` porte `1936.05.16`
(zéro non significatif), seul du fichier — à normaliser au passage.

### 6.4 Processus

- **Le refactor n'a aucun sujet WORK.md** (**MEASURED** — aucun heading layers ; méta-travail sur
  demande owner, admission OK), donc les 6 runs dus du rapport §7 vivent hors du tracker qui
  impose `SHIPPED-UNTESTED` → `TESTED`. La règle « big scripted change ⇒ console test owner »
  d'AGENTS.md s'applique pourtant ici plus que jamais. WORK.md est à sa limite WIP (4 sujets
  armor/mech en SHIPPED-UNTESTED du 2026-08-29 — **MEASURED**) : merger le refactor par-dessus
  ajouterait une seconde couche de non-testé sur du non-testé.
- **Le rapport d'implémentation n'a pas de table finale des compteurs** : §0 dit « DATE-LEAK 141,
  NUMBER-LEAK 379 », §9 « 136→151 », §11 « 123→130 » — l'état réel (130/351/183/330) ne figure
  que dans `tools/ai_layers_baseline.json`. À corriger dans le rapport, sinon la première lecture
  future partira sur des chiffres périmés.
- `read_harness_log.py` : correction minuit appliquée (fenêtre enroulée + avertissement —
  **MEASURED**, lignes 132-149), contrat de sortie documenté plutôt que corrigé (honnête), mais
  **pas de `--selftest`** — l'exigence de la revue pré-implémentation (chaque interpréteur livré
  avec sa fixture) n'est pas tenue ; le critère d'acceptation de l'explain repose donc sur un
  interpréteur non testé.

---

## 7. Trouvailles de cette revue (résumé)

| # | Trouvaille | Gravité |
| --- | --- | --- |
| 1 | L'ordre prudentiel violé : MILITARY (659 blocs) converti avant la mesure perf NAVAL, le critère d'arrêt est devenu un critère de revert — non nommé dans les écarts du rapport | **moyenne** (mitigée : commits revertables un à un) |
| 2 | Le motif `explain` obligatoire (§7.2) n'existe que pour NAVAL ; PRODUCTION et MILITARY sont partis sans — absent de la liste « tous listés » des écarts | **moyenne** |
| 3 | Lot C : +32 sur READS-CONFIG non déclaré, tension de conception « un vocabulaire » vs « couche 4 ne lit pas CONFIG » non arbitrée par écrit | faible-moyenne |
| 4 | Rapport sans état final des compteurs (183/330/130/351 nulle part dans la doc) | faible |
| 5 | Compte « 75 » de la garde d'invasion : le vrai compte est 86 (substitution 1:1 néanmoins exacte) | cosmétique |
| 6 | Sondes q1e/q2e/difficulté non ajoutées au harnais ; `read_harness_log.py` sans selftest | faible (dû connu) |
| 7 | Aucun sujet WORK.md ne porte les 6 runs dus | faible-moyenne (processus) |
| 8 | `before_1936_5_16` : format de date à zéro non significatif, unique dans CONFIG | cosmétique |

Aucune de ces trouvailles n'est un défaut de comportement. **Aucun changement de comportement non
déclaré n'a été trouvé** — ni par l'échantillon, ni par les balayages, ni par la trace du cliquet.

---

## 8. Recommandations, dans l'ordre

| # | Action | Qui décide | Coût |
| --- | --- | --- | --- |
| 1 | **Boot test + run `explain_naval` + les 6 bundles géographiques**, avant toute autre chose | owner (console) | 1 lancement + ~1 h |
| 2 | **Fixer le seuil Q7 puis mesurer la perf** (sauvegarde de référence, N ticks sur `ai-rework` puis sur la branche). Si dépassement : revert des lots 4.x + baseline, comme prévu §10.4 | owner (seuil) / mécanique (mesure) | 2 runs chronométrés |
| 3 | **Ne PAS merger dans `ai-rework` avant 1 et 2.** Le merge lui-même est sûr côté git (aucun commit owner concurrent sur les fichiers convertis depuis `e53cea6e5` — DERIVED de l'historique), mais merger avant les runs mettrait 774 blocs non bootés sous les 4 sujets armor déjà SHIPPED-UNTESTED | owner | — |
| 4 | Ouvrir (ou noter en une ligne en attendant un créneau WIP) un **sujet WORK.md `layers-refactor`** portant les 6 runs dus comme critère de fermeture — sinon la règle SHIPPED-UNTESTED ne mord pas sur le plus gros lot de l'année | owner (admission) | 10 lignes |
| 5 | **Les 26 TODO(owner)** : une session dédiée, fenêtre par fenêtre — nommer l'intention partagée ou éclater. Mécanique ensuite (chaque TODO liste déjà ses lecteurs). Pas bloquant pour le merge ; bloquant pour dire la 3b « finie » | owner | ~26 décisions courtes |
| 6 | **Compléter le harnais pdx** (q1e, q2e, sonde difficulté — 3 sondes d'une ligne) et relancer une fois ; ensuite seulement clore Q1/Q2 et rétrograder `NOT-MULTI` | mécanique (écriture) + owner (run) | trivial |
| 7 | **Lots restants** : (a) abort-gates en premier — c'est le gros de READS-CONFIG 183 et le motif est identique à la phase 4 ; (b) seuils MILITARY (NUMBER-LEAK 351) ensuite ; (c) DOCTRINES via le replacer — c'est un sujet outillage, le garder hors des lots à la main comme le lot B l'a conclu. Avant (a), **écrire l'arbitrage** « vocabulaire unique vs frontière 3/4 » (trouvaille 3) : il décide si une lecture CONFIG directe dans un abort est une cible ou un état final | mécanique, sauf l'arbitrage (owner) | par lot, comme la phase 4 |
| 8 | Corriger le rapport : table finale des compteurs, écarts 1 et 2 ajoutés à la liste §4, « 75 » → 86 | mécanique | 15 min |
| 9 | Un `--selftest` pour `read_harness_log.py` avec les journaux synthétiques en fixtures — condition pour que le critère d'acceptation de l'explain soit réel ; décider si l'absence d'explain MILITARY est acceptée (exception écrite) ou si un explain MILITARY est dû avant le prochain travail de comportement militaire | owner (décision) / mécanique (outil) | ~1 h outil |

---

> **Addendum 2026-08-29** — condition (1) : boot test rapporté **OK** par l'owner (déclaration en
> session, sortie error.log non collée — owner-reported, pas MEASURED par cette revue). Restent
> ouvertes : (2) perf NAVAL (seuil Q7 à fixer d'abord), (3) `explain_naval` relu par l'outil,
> puis les bundles géographiques avant la prochaine campagne scorée.

## 9. Verdict final

**Prêt à merger ? NON en l'état — OUI sous trois conditions, toutes côté jeu :**
(1) boot test propre (error.log lu, l'idée `hard_ai` chargée), (2) perf NAVAL sous le seuil Q7
que l'owner doit d'abord fixer, (3) `explain_naval` relu par l'outil et nommant la couche qui
bloque. Les bundles géographiques peuvent suivre le merge (ils tournent sur campagne), mais avant
la prochaine campagne scorée. Côté code, cette revue n'a trouvé **aucun** défaut de conversion :
l'échantillon, les balayages orphelins/morts et la trace du cliquet concordent à zéro écart.

**Les 3 recommandations prioritaires** : n°1 (boot + explain), n°2 (seuil Q7 + mesure perf),
n°4 (sujet WORK.md pour que les runs dus soient traqués là où le checker mord).

**La chose la plus importante que l'owner doit savoir** : *tout est vert, et rien n'a jamais
tourné.* Les cinq checkers à zéro mesurent la **forme** du refactor — la seule chose qu'ils ne
peuvent pas voir, c'est un fichier qui ne parse pas ou un scope qui se perd dans l'indirection,
et c'est précisément ce que la proposition avait placé en critère d'arrêt AVANT les 659 blocs
MILITARY. Cette marche de prudence a été sautée : elle se rattrape en un boot test et deux runs
chronométrés — mais tant qu'ils n'ont pas eu lieu, l'état honnête de la branche est
« SHIPPED-UNTESTED », au sens exact que WORK.md donne à ce mot, et il n'est écrit nulle part
dans le tracker.
