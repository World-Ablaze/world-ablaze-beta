# WA_AI — Refactorisation en couches : proposition complète

**Statut : PROPOSITION. Rien n'est appliqué. Aucun commit, aucun push.**
Date : 2026-08-29 · branche `ai-rework` · HEAD `c339245b5` · moteur 1.19.2.0
Audits sources : `AUDIT_WA_AI_CONFIG.md`, `ARCHI_COUCHES_WA_AI.md` (scratchpad de session).

---

## 0. Conventions de ce document

| Étiquette | Sens |
| --- | --- |
| **MEASURED** | Lu directement dans un fichier du dépôt ou de l'install 1.19.2. Source nommée. |
| **DERIVED** | Calculé à partir d'un MEASURED. La source du calcul est nommée. |
| **ASSUMED** | Non vérifié. Comportement moteur non observable depuis le dépôt. |

Une affirmation non étiquetée dans ce document est une **décision de conception**, pas un fait.

---

## 1. Résumé exécutif

### 1.1 Le problème, en une phrase

Le mod a trois principes d'architecture AI (point d'entrée unique, config séparée du moteur, pas de
duplication) qui **ne sont écrits nulle part de façon vérifiable**, et qui ont donc cédé partout où
personne ne regardait.

### 1.2 Le fait qui change la nature du chantier

**MEASURED** — conformité des blocs `allowed` / `enable` de `common/ai_strategy/WA_AI_*`
(2418 blocs, script `audit_pilot.py`) :

| Système | Fichiers | Blocs | Bruts | Mixtes | Nommés | Triviaux | **À convertir** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **PRODUCTION** | 51 | 708 | 13 | 2 | **273** | 420 | **15** |
| MILITARY | 113 | 1477 | 461 | 198 | 226 | 592 | **659** |
| NAVAL | 15 | 218 | 83 | 17 | 45 | 73 | **100** |
| RESEARCH + autres | 4 | 15 | 0 | 0 | 0 | 15 | **0** |
| **Total** | **183** | **2418** | **557** | **217** | **544** | **1100** | **774** |

**Le système PRODUCTION applique déjà le modèle cible à ~95 %, sur 51 fichiers.** Ses triggers
`WA_AI_EQUIPMENT_can_absorb_<ressource>_shock_*` sont lus **586 fois dans 32 fichiers**
(**MEASURED**) : une définition, 586 consommateurs, zéro recopie.

**Conséquence sur la nature du travail** : ce n'est pas une refonte spéculative. C'est
l'**extension d'un modèle déjà en production** à deux systèmes qui ne l'ont pas adopté. 85 % du
volume est dans MILITARY seul.

### 1.3 Ce qui est proposé

1. Un modèle **à 4 couches**, dont la frontière est portée **par le préfixe du nom** — donc
   vérifiable par grep, sans parser et sans relecture humaine.
2. Un **outil de vérification dédié** (`tools/check_ai_layers.py`) fonctionnant en **cliquet** :
   il interdit d'aggraver un compteur, il n'exige pas de migrer.
3. Une migration **par système**, du plus fermé au plus transverse, chaque lot précédé de son
   harnais de diagnostic.
4. Trois mesures moteur **bloquantes** avant tout déplacement de code (§4).
5. Un **guide contributeur** en français, écrit pour quelqu'un qui n'a jamais ouvert un
   `.txt` PDXScript.

### 1.4 Ce qui n'est PAS proposé

- Aucun changement de comportement de l'IA. Chaque commit de migration est un
  **diff sémantiquement vide** ou un diff dont la seule différence est un littéral remplacé par une
  référence à la même valeur.
- Aucune réécriture du système de lois (`WA_AI_LAW_triggers.txt`, 2163 lignes) : sujet distinct,
  §11.
- Aucun `push`. Aucun commit tant que la revue Fable 5 n'a pas rendu son verdict et que l'owner
  n'a pas tranché les questions du §12.

---

## 2. Le modèle cible

### 2.1 Les quatre couches

| # | Couche | Question à laquelle elle répond | Matière | A le droit de lire |
| --- | --- | --- | --- | --- |
| **1** | **DÉCLARATION** | « Quelle est la valeur ? » | `common/script_constants/wa_ai_*.txt` + `common/scripted_triggers/WA_AI_CONFIG*.txt` | **rien** |
| **2** | **OBSERVATION** | « Qu'est-ce qui est vrai dans le monde, maintenant ? » | `common/scripted_triggers/WA_AI_<SYS>_*.txt` | couche 1 |
| **3** | **DÉCISION** | « Faut-il agir ? » | `common/scripted_triggers/WA_AI_<SYS>_*.txt` | couches 1 + 2 |
| **4** | **CONSOMMATION** | — | `common/ai_strategy/`, `common/scripted_effects/`, `events/`, `common/decisions/` | couche **3 uniquement** |

### 2.2 Les trois frontières, et le test qui les décide

**Frontière 1 / 2 — « lit-il quelque chose qui bouge tout seul ? »**

> Un bloc de couche 1 ne lit **rien qui change sans qu'un joueur ou une IA ait agi**.
> Autorisé : `tag`, `original_tag`, `date`, seuils numériques, `has_tech`, `has_completed_focus`,
> `has_autonomy_state`, `has_idea`, `has_government`, `difficulty`.
> Interdit : `any_enemy_country`, `any_country_of`, `has_war*`, `controls_state`, `owns_state`,
> `surrender_progress`, `check_variable`, `num_divisions`, tout scope d'un autre pays.

**MEASURED** : le `WA_AI_CONFIG.txt` actuel passe ce test à **133 / 144**. La règle formalise
donc ce que le fichier fait déjà à 92 %.

**Frontière 2 / 3 — « le verdict embarque-t-il une intention ? »**

> Une **observation** est vraie ou fausse indépendamment de ce qu'on veut en faire.
> Une **décision** embarque une intention d'agir.
> Test opérationnel : *si deux consommateurs veulent des choses opposées du même verdict, c'est
> une observation.* `WA_AI_MILITARY_is_axis_member` est une observation (l'Axe s'en sert pour
> coordonner, les Alliés pour cibler). `WA_AI_MILITARY_should_open_east_front` est une décision.

**Frontière 3 / 4 — vérifiable par le nom seul**

> Un fichier de couche 4 ne nomme que des triggers `_should_*` / `_can_*` (couche 3),
> plus le scoping par tag de son propre fichier Country (`allowed = { tag = GER }`, qui est
> l'adressage du fichier, pas une lecture de config).

**MEASURED** : `common/ai_strategy` lit aujourd'hui **54 triggers CONFIG directement** et contient
**3203 termes moteur bruts** contre 1207 termes nommés.

### 2.3 Convention de nommage — la pièce maîtresse

C'est **le préfixe qui porte la couche**. Sans cela, aucune règle n'est vérifiable à coût nul.

| Couche | Forme du nom | Exemple existant conforme |
| --- | --- | --- |
| 1 | `WA_AI_CONFIG_<domaine>_<sujet>` | `WA_AI_CONFIG_MILITARY_is_axis_eastern_force` |
| 1 | `constant:wa_ai_<système>.<groupe>.<clé>` | `constant:wa_ai_pc.budget.max_projects` |
| 2 | `WA_AI_<SYS>_is_*` / `_has_*` / `_holds_*` | `WA_AI_MILITARY_is_axis_member` |
| 3 | `WA_AI_<SYS>_should_*` / `_can_*` | `WA_AI_EQUIPMENT_can_absorb_steel_shock_small` |
| test | `WA_TEST_*` | inchangé |
| télémétrie | `WA_TLM_*` | inchangé |

Deux familles historiques à traiter explicitement :

- `WA_AI_DIFFICULTY_*` (7 triggers, **349 lectures MEASURED**) : renommer coûterait 349 éditions
  pour un gain nul. **Décision : garder le nom, documenter l'exception** comme membre de la
  couche 1. Une exception nommée dans le checker est une donnée ; une exception implicite est une
  dette.
- Les triggers `WA_AI_<SYS>_<verbe>_*` sans préfixe de couche (`WA_AI_can_take_war_economy`,
  `WA_AI_needs_synth_fuel`…) : renommage **au fil de l'eau uniquement**, quand le fichier est
  touché pour une autre raison. Jamais de commit de renommage massif (§10.3).

### 2.4 Ce que le modèle ne couvre PAS — trous assumés

Ces trois trous sont **structurels**, pas des oublis. Les cacher serait la faute.

| Trou | Nature | **MEASURED / ASSUMED** |
| --- | --- | --- |
| `ai_strategy value = <nombre>` ne peut appeler ni trigger ni `constant:` | Le modèle couvre le **gating**, pas le **tuning**. Les nombres des `value =` restent littéraux dans 183 fichiers. | **MEASURED** — skill `wa-constants-registry`, contextes validés 2026-08-16 |
| Une date **ne peut pas** vivre dans un script constant, et l'échec est **silencieux** | Le véhicule d'une date est le **trigger nommé** portant le littéral. | **MEASURED 2026-08-29** (harnais `WA_TEST_pdx_semantics`) : le fichier charge, mais `date > constant:...past` **et** `date > constant:...future` lisent tous deux VRAI, alors que le contrôle littéral `date > 2000.1.1` lit correctement FAUX. Un gate qui cesse de garder sans erreur. |
| Coût de performance d'une chaîne de triggers plus profonde | HOI4 réévalue les blocs `enable` fréquemment. | **ASSUMED** — aucune mesure, moteur boîte noire. Mesure §4.2. |

---

## 3. État des lieux — l'inventaire complet à traiter

### 3.1 Ce qui est cassé ou mort (traitement immédiat, risque nul)

| Item | Volume | **MEASURED** |
| --- | --- | --- |
| Triggers CONFIG jamais lus hors CONFIG | **15** | `audit2.py`, 0 lecture externe |
| Triggers `WA_AI_MISC_triggers.txt` morts (`civil_war_country`, `asian_minor`, `commonwealth`, `european_minor`) | **4** | 1 occurrence chacun = leur définition |
| Définitions dupliquées à l'identique (`WA_AI_TEMPLATES_has_mechanized_spaa_unlocked`, `WA_add_mastery_strike_75`) | **2** | corps byte-identiques |
| Listes de tags commentées dans `use_anti_tank_brigades` / `use_anti_air_brigades` | ~35 lignes | lecture directe |
| Branches mortes derrière `use_heavy_at = always no` dans `WA_AI_DIVISION_CREATOR_effects.txt` | **24 lectures** | `grep -c` |

### 3.2 Les trois tables de classification concurrentes

| Table | Fichier | Triggers | Problème |
| --- | --- | --- | --- |
| A | `WA_AI_CONFIG.txt` | 144 | la table officielle |
| B | `WA_AI_MISC_triggers.txt` | 6 | **`WA_AI_major_country` ≠ `WA_AI_CONFIG_is_major_country`** : le premier ajoute `num_of_civilian_factories > 99`. Lois, prêt-bail et diplomatie utilisent donc une définition de « majeur » différente du reste du mod. **MEASURED**, et rien ne le signale. |
| C | `WA_AI_MILITARY_triggers.txt:463-523` | 8 | classification pays dans le fichier « panneau de contrôle » : `is_china_front_member` (14 tags), `is_commonwealth_member` (7 tags) |
| D | `common/script_constants/country_groups.txt` | 1 groupe actif | quatrième syntaxe, **jamais lue par un fichier `WA_AI_*`** |

### 3.3 Les collisions et inversions

| # | Cas | **MEASURED** |
| --- | --- | --- |
| a | `WA_AI_CONFIG_MILITARY_is_major_naval` (6 tags, identité) **vs** `WA_AI_MILITARY_is_major_naval` (`has_navy_size > 100`, capacité) — 7 caractères d'écart, sens opposés, lus dans les mêmes fichiers | CONFIG:1146 / MILITARY_triggers:467 |
| b | Inversion de couche : `WA_AI_CONFIG_MILITARY_is_axis_minor` → `WA_AI_MILITARY_is_minor_country` → `WA_AI_CONFIG_is_major_country` | CONFIG:1090 → MIL:463 → CONFIG:61 |
| c | Chaîne d'alias à 3 sauts traversant deux fois la frontière : `WA_AI_MILITARY_pacific_war_active` → `WA_AI_CONFIG_MILITARY_pacific_high_risk` → `WA_AI_MILITARY_pacific_high_risk` (défini **dans CONFIG**) | MIL:533 → CONFIG:1114 → CONFIG:1101 |
| d | Profondeur de chaîne jusqu'à **8** (`WA_AI_can_upgrade_economy_law`) | `audit_layers.py` |

### 3.4 Les données hors de leur couche

| Donnée | Dans couche 1 | Hors couche 1 | Conformité |
| --- | --- | --- | --- |
| Dates littérales `date [<>] YYYY.M.D` | 12 | **430** | **2,8 %** |
| Seuils numériques | 5 | **499** | **1,0 %** |

Répartition des 430 dates (**MEASURED**) : `ai_strategy` 283 · `events` 61 ·
`scripted_triggers` hors CONFIG 48 · `scripted_effects` 24 · divers 2.

Dates répétées : **`1942.1.1` 56 fois**, `1940.1.1` 32, `1941.1.1` 26, `1938.1.1` 15,
`1944.6.6` 10.

Les *script constants* existent et fonctionnent, mais seuls 8 systèmes les utilisent
(**MEASURED**, lectures `constant:`) : PC 214 · lend-lease 105 · railway 78 · posture 44 ·
resource 31 · AIFC 30 · production 18 · leaders 7. **Militaire, templates, lois, recherche,
doctrines : zéro.**

### 3.5 Les deux inconnues moteur

**RÉSOLUES le 2026-08-29** par le harnais console `WA_TEST_pdx_semantics` (partie 1936.1.1, tag
GER, en-tête de contexte `1 1 1 1 0`, contrôles positifs et négatifs valides sur les trois sondes).
Détail et sondes exactes : `documentation/PDXSCRIPT_LANGUAGE_NOTES.md`, section *Measured Engine
Semantics (1.19.2.0)*.

| # | Question | Réponse **MEASURED** | Conséquence |
| --- | --- | --- | --- |
| a | `if` à `limit` faux, dans un `OR` | **VRAI VACUANT** | **DÉFAUT CONFIRMÉ**, voir §3.6 |
| b | `NOT = { A B }` à ≥ 2 enfants | **NOR** — « aucun de ceux-ci » | **Aucun défaut.** Les 71 sites se lisent comme leurs auteurs les ont écrits |
| c | `date > constant:x.y.z` | **SILENCIEUSEMENT PERMISSIF** — toujours vrai | Les 430 dates passent par des **triggers nommés**, jamais par des constantes |

Ce que cela change pour le plan : la question Q2, qui menaçait 71 sites dont 16 dans le système de
lois, est **close sans défaut**. La question Q3 est close **par la négative**, ce qui fixe le
véhicule de la phase 3b. La question Q1 a trouvé un vrai bug.

### 3.6 Le défaut trouvé par la phase 0 — **MEASURED**

`WA_AI_CONFIG_DIVISIONS_use_armored_divisions` (`WA_AI_CONFIG.txt:425-442`) contient un `if` à
l'intérieur d'un `OR` :

```
OR = {
    original_tag = ENG … SOV
    if = {
        limit = { WA_AI_DIFFICULTY_is_historical = yes }
        OR = { original_tag = JAP  original_tag = ITA }
    }
}
```

- Difficulté **historique** (0-2) : `limit` vrai, la branche s'évalue normalement. Comportement
  correct.
- Difficulté **compétitive** (3-4) : `limit` faux → l'`if` vaut VRAI → **le `OR` entier est vrai
  pour tous les pays du monde.**

Chaîne de conséquences (**MEASURED**, 3 lecteurs) :

| Lecteur | Effet en difficulté compétitive |
| --- | --- |
| `WA_AI_TEMPLATES_use_armor_templates` (`WA_AI_TEMPLATES_triggers.txt:178`) | **tout pays** reçoit des templates blindés — le terme suffit à lui seul à satisfaire le `OR` externe |
| `WA_AI_CONFIG_DIVISIONS_uses_motorized_hq` (`WA_AI_CONFIG.txt:511`) | **tout pays** reçoit un QG d'armée motorisé (`history/general/taog_hq_template.txt`) |
| `WA_AI_RESEARCH_needs_maintenance_company` (`WA_AI_RESEARCH_support.txt:18`) | **tout pays** pondère la recherche de compagnie de maintenance |

**Portée honnête** : le défaut ne mord **qu'en difficulté compétitive**. Les campagnes de test en
difficulté historique ne l'ont jamais vu, ce qui explique qu'il ait survécu.

**Résidu moteur, dit franchement** : la sémantique est prouvée en contexte trigger d'événement/effet.
Que les blocs `allowed`/`enable` d'`ai_strategy` parsent à l'identique n'est **pas** prouvé ici —
le moteur les évalue par un autre chemin d'appel. Le second site (`WA_AI_MILITARY_COUNTRY_GER_FRONT.txt:1429`,
un `enable` AIFC) est donc **ASSUMED** touché, pas MEASURED. Sa lecture confirmante est
`imgui show ai-strategy` sur une sauvegarde vivante.

*(Ce même bloc GER porte aussi `has_war_With = POL`, avec un `W` majuscule — **MEASURED**. Casse
probablement sans effet (**ASSUMED**), mais deux hasards se superposent au même endroit.)*

### 3.7 Les comparaisons brutes de `difficulty` — 20 sites qui ne peuvent pas dire ce qu'ils veulent dire

*(Ajouté le 2026-08-29 sur décision owner, après la revue.)*

Le mapping difficulté de WA est **non monotone par construction** : le moteur pré-sélectionne la
valeur 2 à la création de partie, donc Normal historique doit occuper la valeur 2, ce qui ne
laisse que la valeur 1 au Hard historique (0 = Easy, 3-4 = compétitif). La remise en ordre a été
tentée côté GUI et **revertée** (**MEASURED** : `41498591f` 2026-07-25 → revert `e8ddf8153`
2026-07-30, puis fix côté script `4dcc2b403` « out of order intentionally »). La table
autoritaire vit dans le commentaire `[difficulty-mapping]` en tête de la section difficulté de
`WA_AI_CONFIG.txt`.

**Conséquence mécanique** : hors de la couche 1, **aucune comparaison `difficulty >` ne peut
exprimer « normal ou plus dur » ni « hard inclus »** — `> 1` sélectionne {2,3,4} et `> 2`
sélectionne {3,4}, qui excluent tous deux le Hard historique (1). Chaque site brut est donc un
trou potentiel où Hard est plus laxiste que Normal.

**MEASURED** (recomptage revue, hors commentaires) : **20 comparaisons brutes vivantes hors
CONFIG** — 10 `> 1` et 10 `> 2` — dans 11 fichiers : `common/decisions/BUL.txt` (4),
`SPR.txt` (4), `z_WA_ai.txt` (2), `z_WA_ai_SOV.txt` (2), `common/national_focus/spain.txt` (2),
`z_WA_ai_GER.txt`, `common/ideas/_WA_ai.txt`, `common/on_actions/05_lar_on_actions.txt`,
`events/LAR_Spain.txt`, `events/WA_AI_CHI.txt`, `events/WA_AI_GER.txt` (1 chacun). Le commentaire
de BUL (« Hard and above Difficulty » sur un `> 2`) est déjà faux sous ce mapping.

Le traitement est la phase 2b (§5.2b) ; la règle de checker est `DIFFICULTY-RAW` (§8.2).

---

## 4. Phase 0 — les mesures bloquantes

**Rien ne bouge avant.** Trois questions décident de ~500 sites et du véhicule de la phase 3.

### 4.1 Harnais `WA_TEST_pdx_semantics`

Nouveau fichier `common/scripted_effects/WA_TEST_pdx_semantics.txt`, fichier d'événements dédié
`events/wa_test_pdx_semantics.txt` (jamais `events/wa_events_test.txt` — son site d'appel a
empoisonné des triggers country-valués, cause inconnue, cf. `wa-testing`).

Contrat harnais v1 obligatoire : marqueur `harness-contract: v1`, lignes `who` / `scope`,
contrôle `I-am-ROOT`, contrôle connu-faux `control-false`, règle `STOP` — inline, jamais derrière
un helper partagé. `tools/check_worklist.py` le vérifie mécaniquement (`HARNESS-CONTRACT`).

Les trois mesures :

| # | Sonde | Décide |
| --- | --- | --- |
| Q1 | `OR = { always = no  if = { limit = { always = no } always = no } }` | §3.5a — 3 sites |
| Q2 | `NOT = { always = yes  always = no }` | §3.5b — 71 sites |
| Q3 | `date > constant:wa_ai_test.dates.probe` — parse-t-il ? compare-t-il juste ? | §2.4 — véhicule des 430 dates |

Une constante jetable `common/script_constants/wa_ai_test.txt` porte la sonde Q3 ; elle est
supprimée après la mesure.

**Sortie attendue** : 3 lignes de log + le bloc de contexte. **L'owner lance le harnais en console
et colle la sortie dans le document de suivi.** C'est la règle du dépôt pour tout effet scripté.

### 4.2 Mesure de performance (lot pilote uniquement)

**ASSUMED** aujourd'hui. Protocole proposé, à valider par la revue :

1. Sauvegarde de référence, date fixe, même seed.
2. Chronométrer N ticks avant conversion du système NAVAL.
3. Convertir NAVAL (100 blocs), rechronométrer les mêmes N ticks sur la même sauvegarde.
4. Si la dégradation dépasse un seuil que l'owner fixe, **le modèle est révisé avant MILITARY**,
   pas après.

**Cette mesure est un critère d'arrêt, pas une formalité.** 659 blocs MILITARY convertis sur une
hypothèse de performance fausse seraient irréversibles en pratique.

### 4.3 Résultats — phase 0 CLOSE le 2026-08-29

| Question | Réponse **MEASURED** | Conséquence appliquée |
| --- | --- | --- |
| Q1 `if` à limit faux dans un `OR` | **VRAI VACUANT** | Défaut confirmé sur `use_armored_divisions` (§3.6). Devient un sujet WORK.md avec sa sonde. Le 2ᵉ site (`GER_FRONT.txt:1429`) reste **ASSUMED** — chemin d'appel `ai_strategy` non prouvé |
| Q2 `NOT` multi-enfants | **NOR** | **Aucun défaut.** Les 71 sites sont corrects. La règle `NOT-MULTI` du checker tombe à INFO documentaire, ou disparaît |
| Q3 `date > constant:` | **SILENCIEUSEMENT PERMISSIF** | Véhicule de la phase 3b **fixé** : trigger nommé portant le littéral, jamais une constante. Le motif existe déjà (`WA_AI_CONFIG_switch_from_light_to_medium_armor`) |

Les trois réponses sont consignées dans `documentation/PDXSCRIPT_LANGUAGE_NOTES.md`
(*Measured Engine Semantics (1.19.2.0)*), avec les sondes exactes et leurs contrôles.

**Ce que la phase 0 a coûté et rapporté** : un harnais jetable et un redémarrage du jeu, contre
un défaut trouvé, une menace de 71 sites écartée, et une décision de conception (le véhicule des
430 dates) prise sur une mesure au lieu d'une intuition. **Q3 est le résultat qui justifie le plus
la phase à lui seul** : sans elle, la phase 3b partait sur des constantes, et 430 gates auraient
cessé de garder sans un seul message d'erreur.

---

## 5. Changements de CODE

### 5.1 Phase 1 — nettoyage (aucun lecteur touché)

| Action | Volume | Vérification |
| --- | --- | --- |
| Supprimer les 15 triggers CONFIG morts | −~90 lignes | re-grep du nom sur **tout** le dépôt, `localisation/`, `tools/`, `tests/` inclus, avant chaque suppression |
| Supprimer les 4 triggers MISC morts | −~50 lignes | idem |
| Supprimer les 2 définitions dupliquées | −~25 lignes | corps byte-identiques vérifiés |
| Supprimer les listes de tags commentées | −~35 lignes | — |
| Supprimer les 24 branches `use_heavy_at` | à chiffrer | le trigger reste (`always = no`), les branches partent |

Sortie : `check_constants.py` = 0, `check_worklist.py` = 0, `check_skill_refs.py` = 0.

### 5.2 Phase 2 — réunifier la classification

1. **Déplacer vers CONFIG à l'identique** : `WA_AI_MILITARY_is_china_front_member` (14 tags) →
   `WA_AI_CONFIG_MILITARY_is_china_front_member` ; `WA_AI_MILITARY_is_commonwealth_member`
   (7 tags) → `WA_AI_CONFIG_MILITARY_is_commonwealth_member`. Alias de compatibilité temporaire,
   supprimé dans le commit du dernier lecteur migré.
2. **Renommer pour tuer la collision §3.3a** : `WA_AI_MILITARY_is_major_naval` →
   `WA_AI_MILITARY_has_ocean_going_fleet` ; `WA_AI_MILITARY_is_major_continental` →
   `WA_AI_MILITARY_has_mass_army`. **MEASURED** : 4 fichiers lecteurs.
3. **Supprimer l'alias pur** `WA_AI_MILITARY_is_minor_country`, remplacé chez ses 3 lecteurs
   externes par `WA_AI_CONFIG_is_minor_country` (qui existe déjà). Supprime aussi l'inversion
   §3.3b.
4. **Effondrer la chaîne §3.3c** : un seul `WA_AI_MILITARY_pacific_high_risk`, défini dans
   `WA_AI_MILITARY_triggers.txt` (c'est une observation), les deux autres maillons supprimés.
5. **`WA_AI_major_country` — DÉCISION OWNER REQUISE** (§12 Q2). Recommandation : le renommer
   `WA_AI_CONFIG_is_industrial_power` (7 majeurs OU > 99 usines civiles), le déplacer en CONFIG,
   laisser LAW / LEND_LEASE / DIPLOMACY le lire sous ce nom. **Zéro changement de comportement**,
   et la divergence devient explicite au lieu d'être un piège.
6. **`country_groups.txt` — DÉCISION OWNER REQUISE** (§12 Q5).

### 5.2b Phase 2b — migrer les 20 comparaisons brutes de difficulté (décision owner 2026-08-29)

Les 20 sites du §3.7, un lot dédié, petit et auto-porteur. C'est l'application la plus pure de la
philosophie du modèle : **un nombre brut qui ne peut pas dire ce qu'il veut dire est remplacé par
un nom qui le dit.**

- **Véhicule** : les 7 triggers `WA_AI_DIFFICULTY_*` existants et leurs compositions. Les
  intentions usuelles s'expriment sans rien inventer : « pas en easy » = `NOT = {
  WA_AI_DIFFICULTY_is_historical_easy = yes }` ; « un des deux Hard » =
  `WA_AI_CONFIG_cheats_enabled` ; « compétitif » = `WA_AI_DIFFICULTY_is_competitive`. Un nouveau
  trigger d'intention nommé (en couche 1, dans CONFIG) n'est créé que si un site exprime une
  intention qu'aucune composition ne couvre lisiblement.
- **Un site = une lecture d'intention, pas une transcription.** `difficulty > 1` ne se traduit
  PAS mécaniquement : il faut décider si le site voulait {2,3,4} (ce qu'il fait) ou « normal ou
  plus dur » {1,2,3,4} (ce qu'il ne peut pas faire). Règle par défaut pour les sites hérités de
  vanilla (BUL, SPR, spain — où `> 1` signifiait « Regular ou plus ») : l'intention est une borne
  de sévérité, donc **Hard historique inclus** — c'est un changement de comportement voulu, une
  ligne de justification par site dans le commit. Un site dont l'intention est illisible est
  laissé brut avec un commentaire `# [difficulty-raw] intention inconnue`, et compte dans le
  cliquet.
- **Vérification** : `check_ai_layers.py` (`DIFFICULTY-RAW` → 0 ou résiduel commenté),
  `check_constants.py`, et — parce que des sites changent de comportement — les 20 diffs relus un
  par un contre la table `[difficulty-mapping]`.

### 5.3 Phase 3 — remonter les données en couche 1

**3a — sortir les 6 verdicts de CONFIG** (petit, mécanique) :

| Trigger | Destination |
| --- | --- |
| `WA_AI_MILITARY_pacific_high_risk` | `WA_AI_MILITARY_triggers.txt` |
| `WA_AI_CONFIG_MILITARY_italian_power_shares_german_ideology` | `WA_AI_MILITARY_triggers.txt` |
| `WA_AI_CONFIG_MILITARY_western_bulwark_is_collapsing` | `WA_AI_MILITARY_triggers.txt` |
| `WA_AI_CONFIG_has_penalised_army_xp_gain` | `WA_AI_TEMPLATES_triggers.txt` |
| `WA_AI_CONFIG_needs_cv_planes` | `WA_AI_PRODUCTION_navy.txt` |
| + 3 mixtes à scinder | `faces_strategic_bombing`, `majors_should_build_capitals`, `RAILWAY_override_GER_to_SOV` : la liste de tags / les dates restent en CONFIG, le balayage du monde part avec le verdict |

Restent en CONFIG malgré un `is_in_faction_with` : `is_in_allies`, `MILITARY_is_axis_minor`,
`MILITARY_is_axis_non_german_member` — les tags sont la donnée, l'appartenance en est la lecture
naturelle.

**3b — faire remonter 430 dates + 499 seuils**, par système, un commit par lot :

| Lot | Cible | Dates | Seuils | Véhicule (selon Q3) |
| --- | --- | --- | --- | --- |
| 1 | `WA_AI_MILITARY_COUNTRY_JAP_*` | 47 | — | trigger CONFIG nommé par fenêtre |
| 2 | `WA_AI_MILITARY_FACTION_ALLIES_*` | 52 | — | idem |
| 3 | `WA_AI_MILITARY_COUNTRY_GER_*` / `SOV_*` | 62 | — | idem |
| 4 | `WA_AI_LAW_triggers.txt` | 21 | 33 | **hors périmètre**, §11 |
| 5 | `events/WA_AI_invasions.txt` | — | 75 | `common/script_constants/wa_ai_invasions.txt` |
| 6 | `WA_AI_PRODUCTION_*` | — | 66 | étendre `wa_ai_production.txt` (existe) |

**Règle de découpe : un nom par intention, pas un nom par date.** Si les 56 sites `1942.1.1`
disent la même chose (« la guerre est mondiale »), c'est **un** trigger lu 56 fois. S'ils disent
des choses différentes, ce sont plusieurs noms — et le fait qu'ils portent la même date devient
visible et questionnable. **DÉCISION OWNER REQUISE** (§12 Q4).

**3c — découper CONFIG** une fois le volume connu (~2500 lignes attendues) :

| Fichier | Contenu | Nb estimé |
| --- | --- | --- |
| `WA_AI_CONFIG.txt` | identités, archétypes, compositions | ~110 |
| `WA_AI_CONFIG_WINDOWS.txt` | fenêtres temporelles, seuils nommés | ~80 |
| `WA_AI_CONFIG_FLAGS.txt` | les 22 `always = yes/no`, chacun avec sa ligne « ce qui le ferait basculer » | 22 |

Même dossier, même préfixe : le moteur ne voit pas la frontière de fichier. **Sans BOM**
(AGENTS.md règle 16 — `BOM-IN-SCRIPT` le vérifie).

### 5.4 Phase 4 — convertir la couche 4 (le gros du chantier)

774 blocs. Ordre imposé par le risque, pas par le volume :

| Ordre | Système | Blocs | Rôle du lot |
| --- | --- | --- | --- |
| 1 | **PRODUCTION** | **15** | finir le système déjà à 95 % → **référence écrite** et **fixtures** du checker |
| 2 | **NAVAL** | **100** | pilote réel : mesure du coût de conversion **et** du coût de performance (§4.2) |
| 3 | MILITARY `_FRONT` | ~à ventiler | famille par famille |
| 4 | MILITARY `_INVASION` | | |
| 5 | MILITARY `_THEATRE` | | |
| 6 | MILITARY `_DIPLOMACY` | | |
| 7 | MILITARY `_GARRISON` + reste | | |

Pour chaque bloc converti :

```
# AVANT (couche 4 réimplémente la couche 2)
enable = {
    date > 1942.1.1
    has_war_with = JAP
    num_of_military_factories > 20
}

# APRÈS (couche 4 nomme une décision de couche 3)
enable = {
    WA_AI_MILITARY_should_reinforce_pacific = yes
}
```

…avec, en couche 3, un trigger qui compose une observation et une déclaration, et en couche 1 la
date nommée. Le diff est vérifié bloc par bloc : **mêmes termes, mêmes valeurs, même ordre**.

Les **54 lectures CONFIG directes depuis `ai_strategy`** sont re-routées dans le même passage.

### 5.5 Ce qui reste littéral, et pourquoi

Les `ai_strategy value = <nombre>` (**MEASURED** : `constant:` n'y fonctionne pas). Ils reçoivent
un commentaire d'une ligne nommant l'exception, **pas** un contournement.

---

## 6. Changements de DOCUMENTATION

| Fichier | Changement | Pourquoi |
| --- | --- | --- |
| `AGENTS.md` § *AI Design Philosophy* | Ajouter un **principe 4 : « la couche est portée par le préfixe »**, avec le tableau des 4 couches et les 3 tests de frontière | C'est la règle que les principes 1-3 supposaient sans la dire |
| `AGENTS.md` § *Editing Rules* règle 4 | Réécrire : la règle actuelle ne parle que des tags dans `WA_AI_MILITARY_*`. Elle devient le cas particulier d'une règle générale sur les couches | La règle actuelle est trop étroite pour couvrir les 430 dates et les 499 seuils |
| `AGENTS.md` § *Validation Guidance* | Ajouter la ligne `check_ai_layers.py` | Nouveau checker |
| `AGENTS.md` § *Generic Systems* | Ajouter `WA_AI_CONFIG_WINDOWS.txt` / `_FLAGS.txt` à la table d'ownership | Nouveaux fichiers |
| `documentation/WA_AI_MILITARY_SYSTEM.md` (155 Ko) | Le modèle 4-couches **compose** avec le modèle 4-couches *militaire* existant (Default / Region / Faction / Country), il ne le remplace pas. Ajouter une section explicitant les deux axes : **couche technique** (déclaration/observation/décision/consommation) × **couche de portée** (Default/Region/Faction/Country) | Risque réel de confusion : deux modèles « à 4 couches » dans le même mod |
| `documentation/WA_AI_MILITARY_TYPES_REFERENCE.md` | Colonne supplémentaire : quel trigger de décision arme ce `type =` | Rend le doc utilisable pour la conversion |
| `documentation/PDXSCRIPT_LANGUAGE_NOTES.md` | Consigner les 3 réponses de la phase 0 (`if`-dans-`OR`, `NOT` multi-enfants, `date > constant:`) avec leur date de mesure et la version moteur | Ce sont des faits moteur durables, pas des notes de session |
| `documentation/WA_TEST_WRITING_GUIDELINES.md` | Ajouter le motif `WA_TEST_explain_<système>` (§7.2) **et la relecture par `tools/read_harness_log.py`** (§7.3) : un harnais se livre désormais avec son interpréteur, pas seulement avec ses `log =` | Nouveau type de harnais ; supprime le copier-coller manuel de `game.log` |
| **NOUVEAU** `documentation/WA_AI_LAYERS.md` | **Le document de référence du modèle** : les 4 couches, les 3 tests, la convention de nommage, les 3 trous assumés, la table des exceptions nommées | Un modèle sans document de référence redevient une convention orale |
| **NOUVEAU** `documentation/GUIDE_CONTRIBUTEUR_IA.md` | §9 — le guide junior, en français | Demande explicite de l'owner |
| `documentation/FIX_HISTORY.md` | Inchangé | — |

### 6.1 Changements de SKILLS

| Skill | Changement |
| --- | --- |
| `.claude/skills/wa-orientation/SKILL.md` | Router « où va ma nouvelle règle ? » vers `WA_AI_LAYERS.md`. C'est la question la plus fréquente et elle n'a pas de propriétaire aujourd'hui |
| `.claude/skills/wa-ai-systems/SKILL.md` | Section « les 4 couches » + le tableau de conformité par système (il change à chaque lot, donc : lien vers le rapport du checker, pas de chiffre figé) |
| `.claude/skills/wa-constants-registry/SKILL.md` | Étendre : la déclaration a **deux** véhicules (script constant pour les nombres, trigger CONFIG pour les tags et — selon Q3 — les dates). Aujourd'hui le skill ne parle que du premier |
| `.claude/skills/wa-pdxscript/SKILL.md` | Ajouter les 2 pièges mesurés en phase 0 |
| `.claude/skills/wa-testing/SKILL.md` | Ajouter le motif `explain` |
| `.claude/agents/wa-architecture-reviewer.md` | Ajouter le modèle en couches à sa liste de rulebooks structurels, et `check_ai_layers.py` à ses outils |

Après chaque édition de skill : `python tools/check_skill_refs.py` (exit 0 requis).

---

## 7. Changements de HARNESS

### 7.1 `WA_TEST_pdx_semantics` — phase 0

Décrit au §4.1. Fichier d'événements dédié. Contrat v1. **Supprimé après mesure**, ses résultats
consignés dans `PDXSCRIPT_LANGUAGE_NOTES.md` — un harnais dont la question est répondue est du
code mort.

### 7.2 `WA_TEST_explain_<système>` — le motif nouveau, et il est **obligatoire**

**Le risque numéro un de cette refactorisation est de rendre le diagnostic plus difficile.**
Aujourd'hui, un bloc `enable` contient ses termes : on les lit. Demain il contient un nom, dont la
définition est ailleurs, qui en appelle d'autres. `imgui show ai-strategy` dit *quel bloc est
armé*, il ne dit pas *quel maillon de la chaîne est faux*.

Le motif `explain` répond exactement à ça. Pour un système donné et un pays donné, il journalise
**le verdict de chaque couche séparément** :

```
[1943.06] EXPLAIN NAVAL | GER
  who   : THIS = German Reich  ROOT = German Reich  FROM = —
  scope : always=1  I-am-ROOT=1  I-am-THIS=1  ROOT-scope-usable=1  control-false=0
          (anything but 1 1 1 1 0 here: STOP.)
  L1 declarations : is_submarine_navy=1  owns_naval_atlantic_corridor=1  window_open=0 (date 1943.6 vs 1943.1)
  L2 observations : has_ocean_going_fleet=0 (navy 62, floor 100)  atlantic_contested=1
  L3 decisions    : should_raid_convoys=1  should_contest_atlantic=0
  → le blocage est en L2 : has_ocean_going_fleet
```

Règles du motif :

- Un `explain` **par système migré**, livré **dans le même lot** que la migration. Pas après.
- Il suit le contrat harnais v1 (marqueur, who/scope, contrôle connu-faux, STOP).
- Il **journalise**, il ne décide jamais. Aucun code de gameplay ne le lit.
- Fichier d'événements dédié par système.
- **Critère d'acceptation du lot** : si l'`explain` ne rend pas le diagnostic *plus facile*
  qu'avant la migration, **le lot n'est pas accepté**. C'est la contrepartie explicite de
  l'indirection ajoutée.

### 7.3 `tools/read_harness_log.py` — lire le harnais depuis le disque

**Le problème** : un effet scripté HOI4 ne sait qu'**écrire** (`log = "..."`). Il ne peut pas lire
un fichier. La moitié « relecture » de chaque harnais console a donc toujours été l'owner qui
copie-colle à la main depuis `logs/game.log` — ce qui perd la corrélation avec `error.log`, perd
quel run était lequel, et est exactement l'endroit où une mauvaise lecture devient une conclusion
fausse.

La moitié lecture est donc nécessairement **côté outil**, pas côté script. Cet outil :

| Fonction | Détail |
| --- | --- |
| Trouve les journaux | `Documents/Paradox Interactive/Hearts of Iron IV/logs`, ou `$HOI4_USERDIR`, ou `--logs` |
| Retire les préfixes | HOI4 imbrique `[heure][date][fichier:ligne]:` **deux fois** ; le texte redevient celui que l'auteur a écrit |
| Extrait le **dernier** run | `--runs N` pour davantage ; délimité par les bannières `====` du contrat harnais |
| Corrèle `error.log` | `--errors` affiche les erreurs sur la **même fenêtre d'horloge** — un harnais qui a lu bizarrement parce que son fichier n'a pas parsé est la fausse lecture la plus fréquente, et c'est là qu'elle se voit |
| Interprète | `--interpret <harnais>` applique une table de verdicts : contrôles d'abord, puis la réponse. **Un contrôle en échec rend la sonde ILLISIBLE, jamais « répondue »** |
| Inventorie | `--list` liste les marqueurs présents dans `game.log` |

```bash
python tools/read_harness_log.py --marker "PDX TEST" --interpret pdx_semantics --errors
```

Codes de sortie : `0` lecture propre · `1` marqueur absent (harnais jamais lancé) · `2` l'en-tête
de contexte du run dit STOP.

**MEASURED 2026-08-29** : testé sur un vrai run (`CONVOY ARSENAL TEST`, `game.log` 1592 lignes) et
sur des journaux synthétiques couvrant les trois chemins (propre / STOP / marqueur absent) ; les
trois codes de sortie sont conformes.

**Ce que l'outil ne peut pas faire, et qu'il ne prétend pas faire** : il lit ce que le jeu a
écrit. Il ne déclenche pas l'événement, ne sait pas si l'owner était bien `tag`-é sur le pays
voulu, et ne distingue un run périmé d'un run frais que par la date de partie qu'il affiche. **La
date du run est à vérifier avant de faire confiance à la lecture.**

**Extension prévue** : chaque `WA_TEST_explain_<système>` (§7.2) livre son interpréteur dans
`INTERPRETERS`, au même titre que `pdx_semantics`. C'est ce qui rend le critère d'acceptation du
§7.2 opérationnel — « le diagnostic est-il plus facile » devient « l'outil nomme-t-il la couche
qui bloque, sans lecture humaine du journal ».

### 7.4 Harnais existants

**MEASURED** : 16 harnais `WA_TEST_*` existent. Ceux qui lisent un trigger renommé en phase 2
(`WA_TEST_total_commitment.txt` lit `WA_AI_MILITARY_is_minor_country`) sont mis à jour **dans le
commit du renommage**, pas dans un commit de suivi.

---

## 8. Changements de COMMENTAIRES et de TESTS

### 8.1 Commentaires

La règle actuelle d'AGENTS.md (règle 7 : *un commentaire par comportement protégé, nommé par son
sujet, sans historique, en-tête ≤ 5 lignes*) est **conservée telle quelle**. Deux ajouts :

1. **Chaque trigger déclare sa couche par son nom**, donc le commentaire n'a plus à l'expliquer.
   Un en-tête qui dit « ceci est de la config » devient redondant et doit être supprimé au passage.
2. **Une déclaration de couche 1 porte une ligne « ce qui la ferait changer »** — la valeur, la
   supposition, et le signal que la supposition est morte. C'est déjà le motif des bons en-têtes
   existants (`[mech-window]`, `[armor-class-handoff]`) ; il devient la règle pour les 22 drapeaux
   `always = yes/no` qui n'en ont pas.

**Nettoyage à faire au passage** (**MEASURED**) : le commentaire de
`WA_AI_CONFIG_MILITARY_is_western_european_bulwark` annonce
`WA_AI_CONFIG_MILITARY_is_german_homeland_power` comme utilisé — il ne l'est nulle part. Dérive
commentaire/code exactement du type que la règle 7 vise.

### 8.2 Nouveau checker : `tools/check_ai_layers.py`

**Pourquoi un nouvel outil et pas une extension de `check_worklist.py`** : son docstring dit
explicitement qu'il garde « les cinq règles dont l'absence a coûté une session de debug chacune -
rien de plus », et qu'« une règle qui police le tracker crée du méta-travail ». Y greffer 7 règles
d'architecture contredirait sa raison d'être. Un outil séparé, avec son propre `--selftest`, est
la forme respectueuse.

| Règle | Niveau | Détecte | Compteur initial **MEASURED** |
| --- | --- | --- | --- |
| `LAYER4-RAW-GATE` | cliquet | Bloc `allowed`/`enable` d'un fichier `ai_strategy/WA_AI_*` contenant un terme moteur brut | **774** |
| `LAYER4-READS-CONFIG` | cliquet | Fichier de couche 4 nommant un `WA_AI_CONFIG_*` | **54** |
| `DATE-LEAK` | cliquet | `date [<>] YYYY.M.D` littérale dans un `WA_AI_*` hors couche 1 | **430** |
| `NUMBER-LEAK` | cliquet | Seuil numérique dans un `WA_AI_*` hors couche 1 et hors `script_constants` | **499** |
| `DIFFICULTY-RAW` | cliquet → ERROR après la phase 2b | Comparaison brute `difficulty [<>=]` hors `WA_AI_CONFIG*` (tout `common/` + `events/`, commentaires strippés — le mapping non monotone du §3.7 rend ces comparaisons inaptes à dire « normal ou plus dur ») | **20** |
| `CONFIG-LIVE` | ERROR | `any_enemy_country` / `any_country_of` / `has_war*` / `surrender_progress` / `check_variable` dans `WA_AI_CONFIG*` | 11 → 0 après phase 3a |
| `CONFIG-DEAD` | ERROR | Trigger défini dans `WA_AI_CONFIG*` et lu nulle part | 15 → 0 après phase 1 |
| `NAME-COLLISION` | ERROR | Deux triggers dont les noms ne diffèrent que par un segment de préfixe | 1 (`is_major_naval`) → 0 |
| `DUP-DEF` | ERROR | Un même nom de trigger/effect défini deux fois | 2 → 0 |
| `NOT-MULTI` | selon Q2 | `NOT` à ≥ 2 enfants directs | 71 |

**Le cliquet** : chaque règle « cliquet » lit son compteur de référence dans
`tools/ai_layers_baseline.json`, échoue si le compte **remonte**, et **exige la mise à jour du
fichier** quand il baisse. On n'oblige personne à migrer 774 blocs avant de committer ; on interdit
d'en ajouter un 775ᵉ. **C'est le seul dispositif qui fait converger la migration** — sans lui, on
migre 40 blocs pendant que 10 apparaissent ailleurs, ce qui est précisément le mécanisme par
lequel les principes d'origine se sont érodés.

**`--selftest` obligatoire** : chaque règle arrive avec sa fixture, construite pour la déclencher.
Une règle sans fixture fait échouer le self-test. C'est déjà le contrat de `check_worklist.py`
(trois règles y ont été livrées inertes le 2026-08-18 avant que ce contrat existe).

### 8.3 Tests de campagne et bundles

| Test | Changement |
| --- | --- |
| `tests/wa_ai_military_strict_parity.txt` | Inchangé — c'est un test de parité vanilla, insensible au refactor |
| `tests/wa_*_geographic.txt` (6 fichiers) | **Ce sont les tests de non-régression du refactor.** Chaque lot MILITARY converti doit les laisser passer à l'identique. Ils ne changent pas ; ils sont le filet |
| Nouveau | Aucun nouveau bundle. Le refactor est censé être sémantiquement neutre : un test qui changerait de résultat signale un bug de migration, pas un besoin de test |

### 8.4 Vérification par lot

Chaque commit de migration :

```bash
python tools/check_ai_layers.py
```
```bash
python tools/check_constants.py && python tools/check_worklist.py && python tools/check_skill_refs.py
```

Plus, pour les lots MILITARY : le bundle géographique du pays concerné, et l'`explain` du
système relu par l'outil, pas à l'œil :

```bash
python tools/read_harness_log.py --marker "EXPLAIN MILITARY" --interpret military --errors
```

---

## 9. Le GUIDE CONTRIBUTEUR (`documentation/GUIDE_CONTRIBUTEUR_IA.md`)

Public : quelqu'un qui n'a jamais ouvert un `.txt` PDXScript et veut changer un comportement de
l'IA. Écrit en français. Structure proposée :

### 9.1 « Je veux changer un comportement — où je vais ? »

Un arbre de décision de 4 questions, sans jargon :

```
Tu veux changer QUOI ?

├─ Une VALEUR (un pays de plus dans une liste, une date, un seuil)
│    → couche 1 : common/scripted_triggers/WA_AI_CONFIG*.txt
│                 ou common/script_constants/wa_ai_<système>.txt
│    → tu n'as rien d'autre à toucher. C'est le cas le plus fréquent.
│
├─ CE QUE L'IA CONSIDÈRE COMME VRAI (« le front est en danger »)
│    → couche 2 : WA_AI_<SYSTÈME>_triggers.txt, nom en _is_ / _has_
│
├─ QUAND L'IA AGIT (« attaquer si… »)
│    → couche 3 : WA_AI_<SYSTÈME>_triggers.txt, nom en _should_ / _can_
│
└─ CE QUE L'IA FAIT (un ordre nouveau, un bâtiment, une stratégie)
     → couche 4 : common/ai_strategy/, events/, common/scripted_effects/
     → et là, tu ne mets JAMAIS de date ni de tag dans le bloc : tu appelles un _should_.
```

### 9.2 « Les 5 règles qui te font tout casser sans message d'erreur »

Le mod ne dit jamais qu'il s'est trompé. Ces cinq-là sont mesurées, pas théoriques :

1. **Pas de BOM.** Un fichier `scripted_effects` / `scripted_triggers` sauvé avec un BOM UTF-8 ne
   se charge pas **du tout**, silencieusement. Un système entier a disparu comme ça le 2026-08-15.
2. **Un tag ne va jamais ailleurs qu'en couche 1.** Si tu écris `tag = GER` dans un
   `ai_strategy`, la règle qui devait valoir pour « toute grande puissance de l'Axe » ne vaudra
   que pour l'Allemagne — et le jour où la partie diverge de l'histoire, l'IA n'a **aucun**
   comportement.
3. **Une date non nommée est une date perdue.** `1942.1.1` est écrite 56 fois dans le mod. Si tu en
   ajoutes une 57ᵉ, personne ne saura jamais laquelle changer.
4. **`always = no` ne veut pas dire « désactivé proprement ».** Un trigger `always = no` lu 24
   fois laisse 24 branches mortes que tout le monde devra relire.
5. **Diagnostiquer avant de corriger.** La première hypothèse sur un mauvais comportement de l'IA
   dans ce dépôt est *habituellement fausse*. Lance l'`explain` du système avant de toucher au
   code.

### 9.3 « Ton premier changement, pas à pas »

Un exemple complet et réel, déroulé du début à la fin : *ajouter la Roumanie à la liste des pays
qui utilisent de l'artillerie lourde*. Une ligne en couche 1, aucun autre fichier, la commande de
vérification, ce qu'on doit voir passer.

### 9.4 « Ce qui doit être mesuré, jamais supposé »

Les trois étiquettes MEASURED / DERIVED / ASSUMED, pourquoi elles existent, et la phrase qui
résume : *« Le moteur est une boîte noire. Ce que tu n'as pas lu dans un fichier, tu ne le sais
pas. »*

### 9.5 « Les commandes »

Les quatre checkers, un bloc `bash` chacun, ce que chacun attrape, et la règle : **exit 0 partout
avant de proposer un changement.**

### 9.6 « Où demander »

`WORK.md`, les skills, et la règle qu'un sujet sans critère de fermeture est un souhait, pas une
tâche.

---

## 10. Ordre d'exécution, risques et repli

### 10.1 Ordre

```
Phase 0   mesures moteur (owner, console)          BLOQUANT
Phase 1   nettoyage code mort                      risque nul
Phase 8.2 checker + cliquet + selftest             AVANT toute migration
Phase 2   réunifier la classification              1 décision owner
Phase 2b  20 comparaisons difficulté → noms        petit, comportement relu site par site
Phase 3a  6 verdicts sortent de CONFIG             mécanique
Phase 4.1 finir PRODUCTION (15 blocs)              donne la référence + les fixtures
Phase 4.2 pilote NAVAL (100 blocs) + explain + perf  CRITÈRE D'ARRÊT
Phase 3b  430 dates + 499 seuils, par lot          gros volume
Phase 3c  découpage de CONFIG en 3 fichiers        cosmétique, à la fin
Phase 4.3+ MILITARY, famille par famille (659)     85 % du chantier
Phase 6   documentation + guide                    en continu, pas à la fin
```

**Le checker vient en 3ᵉ position, avant toute migration.** C'est ce qui fait converger le reste.

### 10.2 Risques

| Risque | Gravité | Mitigation |
| --- | --- | --- |
| Le diagnostic devient plus dur | **élevée** | `explain` livré dans le même lot ; critère d'acceptation explicite (§7.2) |
| Coût de performance | **inconnue (ASSUMED)** | mesuré sur le pilote NAVAL avant MILITARY ; critère d'arrêt (§4.2) |
| Régression silencieuse pendant la conversion | élevée | diff bloc par bloc ; bundles géographiques ; `check_constants` + `check_worklist` à 0 |
| Confusion entre les deux modèles « 4 couches » (technique vs Default/Region/Faction/Country) | **moyenne, sous-estimée** | section dédiée dans `WA_AI_MILITARY_SYSTEM.md` (§6) ; vocabulaire distinct imposé : **couche** (technique) vs **échelon** (portée) |
| Le refactor s'arrête à mi-chemin et laisse deux styles | moyenne | le cliquet garantit que l'état intermédiaire ne se dégrade pas ; chaque lot est autonome et livrable |
| Renommage massif qui casse un lecteur non trouvé | moyenne | re-grep sur **tout** le dépôt avant chaque suppression/renommage, `localisation/` `tools/` `tests/` inclus |

### 10.3 Ce qu'on s'interdit

- **Pas de commit de renommage massif.** Les renommages de convenance se font au fil de l'eau,
  quand le fichier est déjà ouvert pour une autre raison. Un commit qui ne fait que renommer 300
  triggers rend tout `git blame` inutilisable sur le code le plus load-bearing du mod.
- **Pas de « pendant qu'on y est ».** Un lot de migration ne corrige pas un bug trouvé en chemin :
  il devient un sujet WORK.md séparé.
- **Pas de push tant que la revue Fable 5 et les décisions du §12 ne sont pas rendues.**

### 10.4 Repli

Chaque phase est un ou plusieurs commits indépendants sur `ai-rework`. Un lot qui échoue à son
critère (bundle géographique, `explain`, perf) se `revert` seul, sans toucher aux lots précédents.
Le cliquet du checker se met à jour dans le même commit que le lot, donc un revert de lot
s'accompagne d'un revert du baseline.

---

## 11. Hors périmètre — à traiter séparément

**`WA_AI_LAW_triggers.txt`** : 2163 lignes, 20 triggers, **272 tags**, 21 dates, 33 seuils, 16
`NOT` multi-enfants, chaînes de profondeur 7-8 (**MEASURED**). Le fichier recopie à la main les
`available` des lois vanilla (il le dit lui-même : *« copy from idea file »*). Ce n'est pas une
question de couches, c'est un **miroir de données vanilla** avec un risque de dérive à chaque patch
Paradox. Sa question de conception propre : génération par outil depuis `common/ideas/` ?

Ne pas l'emballer dans ce refactor. Il mérite son propre sujet WORK.md.

---

## 12. Décisions owner requises avant application

| # | Question | Recommandation |
| --- | --- | --- |
| **Q1** | Lancer le harnais `WA_TEST_pdx_semantics` en console et coller la sortie ? | **Bloquant.** Sans ça, 74 sites restent ASSUMED et le véhicule des 430 dates est inconnu |
| **Q2** | `WA_AI_major_country` (§5.2.5) : renommer en `WA_AI_CONFIG_is_industrial_power` ? | **Oui** — comportement inchangé, divergence rendue explicite. Les alternatives changent le comportement des lois |
| **Q3** | Portée de la phase 3b : les 6 lots, ou seulement les 3 lots militaires (~110 dates) ? | Les 3 militaires d'abord ; 5 et 6 sont peu risqués et peuvent suivre ; 4 est hors périmètre |
| **Q4** | Granularité de nommage : un seul nom pour les 56 `1942.1.1`, ou un nom par intention ? | **Un nom par intention.** Les collisions de date deviennent visibles et discutables. Mais l'owner sait si ces 56 sites disent la même chose |
| **Q5** | `country_groups.txt` : porteur officiel des listes de tags AI, ou hors périmètre AI ? | **Hors périmètre**, documenté comme tel. Il n'est lu par aucun fichier `WA_AI_*` et introduire une 4ᵉ syntaxe pendant qu'on en unifie trois serait contradictoire |
| **Q6** | Les 8 triggers `*_assault_tanks` / `*_infantry_support_tanks` morts : supprimer, ou brancher ? | Question de conception, pas d'architecture. L'owner seul sait si c'était une famille en cours |
| **Q7** | Seuil de dégradation de performance qui arrête le chantier (§4.2) | À fixer par l'owner avant le pilote, pas après la mesure |

---

## 13. Ce que la revue doit challenger en priorité

0. **La phase 0 est close (§4.3).** La revue n'a plus à juger si les inconnues moteur méritaient
   d'être mesurées — elles l'ont été, et l'une des trois a trouvé un bug. Ce qui reste à
   challenger : le défaut §3.6 est-il correctement borné à la difficulté compétitive, et le
   résidu `ai_strategy` y est-il traité honnêtement ?
1. **Le modèle à 4 couches est-il le bon, ou 3 suffisent-elles ?** La séparation
   observation / décision est ma conviction, pas un fait mesuré. Le contre-argument à examiner :
   elle ajoute une indirection dont le bénéfice est théorique tant qu'aucun système n'a deux
   consommateurs opposés du même verdict.
2. **Le cliquet est-il suffisant pour faire converger 774 blocs ?** Ou faut-il une échéance ?
3. **Le critère d'acceptation de l'`explain` est-il opérationnalisable ?** La proposition avance
   maintenant une forme falsifiable (§7.3) : *l'interpréteur de `read_harness_log.py` nomme la
   couche qui bloque, sans lecture humaine du journal*. Est-ce suffisant, ou est-ce déplacer le
   jugement subjectif dans l'interpréteur ?
4. **Le risque de confusion entre les deux modèles « 4 couches » est-il sous-estimé ?**
   `WA_AI_MILITARY_SYSTEM.md` fait 155 Ko et son modèle Default/Region/Faction/Country est déjà
   la source de confusion la plus fréquente du dépôt.
5. **L'ordre est-il juste ?** En particulier : finir PRODUCTION avant NAVAL est-il un vrai gain,
   ou une façon de repousser la mesure de performance ?
6. **Qu'est-ce que j'ai manqué ?** Le recensement des lecteurs de couche 1 a balayé tout le dépôt
   sauf `tests/`, `documentation/` et `.claude/` (**MEASURED**, `audit2.py`), et a trouvé des
   lecteurs inattendus : `common/country_leader/00_traits.txt` (**11 triggers CONFIG**, 5ᵉ plus
   gros lecteur du mod), `common/scripted_localisation/` (5), `history/general/` (1),
   `common/decisions/` (1), `common/ideas/` (1). Ces lecteurs hors-IA ne sont **pas** traités par
   les phases 1-4 de cette proposition, et la règle « la couche 4 ne lit jamais CONFIG » ne dit
   rien d'eux. **C'est un trou réel du plan** : faut-il les inclure, les exempter nommément, ou
   les traiter comme un sujet distinct ?
