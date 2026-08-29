# Audit WA_AI_CONFIG + proposition de refactorisation

Date : 2026-08-29 · branche `ai-rework` · HEAD `c339245b5`
Périmètre : `common/scripted_triggers/WA_AI_CONFIG.txt` (1566 lignes, 144 triggers) et **tous** ses
sites de lecture (`common/`, `events/`, `history/`).

Base de référence avant travaux : `python tools/check_constants.py` = **0 erreur / 0 warning**,
`python tools/check_worklist.py` = **0 ERROR / 0 WARN**. Toute régression introduite par la
refactorisation sera donc visible.

---

## 0. Étiquettes

| Étiquette | Sens |
| --- | --- |
| **MEASURED** | Lu directement dans un fichier du dépôt ou de l'install. Source nommée. |
| **DERIVED** | Calculé à partir d'un MEASURED. La source du calcul est nommée. |
| **ASSUMED** | Non vérifié. Comportement moteur non observable depuis le dépôt. |

---

## 1. La surface, en chiffres

**MEASURED** (comptage `common/` + `events/`, 2026-08-29) :

| Zone | Fichiers `WA_AI_*` | Lignes |
| --- | --- | --- |
| `common/scripted_triggers` | 31 | 17 468 |
| `common/scripted_effects` | 39 | 159 058 |
| `common/ai_strategy` | 183 | 50 120 |
| `events` | 22 | 16 630 |
| `common/on_actions` | 2 | 1 025 |
| **Triggers `WA_AI_*` définis** | | **937** |
| **Effects `WA_AI_*` définis** | | **276** |

CONFIG en représente 144 (15 % des triggers). Les 793 autres sont censés être des « portes
logiques ». Le §3 montre que ce n'est plus vrai.

Répartition des lecteurs de CONFIG (**MEASURED**, nombre de triggers distincts lus par dossier) :

| Dossier lecteur | Triggers CONFIG distincts lus |
| --- | --- |
| `common/scripted_triggers` | 147 |
| `common/ai_strategy` | 54 |
| `common/scripted_effects` | 31 |
| `common/country_leader` | 11 |
| `common/scripted_localisation` | 5 |
| `common/on_actions` | 3 |
| `events` | 3 |
| `common/ai_equipment` | 3 |
| `history/general`, `common/decisions`, `common/ideas` | 1 chacun |

Détail exhaustif par trigger : `config_usage.tsv` (à côté de ce fichier).

---

## 2. Ce que CONFIG contient réellement

> **Règle de périmètre (owner, 2026-08-29)** : appartiennent à CONFIG les **tags**, les
> **variables numériques** et les **dates**. Autrement dit CONFIG déclare des **valeurs** ; le
> moteur pose des **questions au monde vivant**. Toute cette section et la phase 3 du §5 appliquent
> cette règle. *(Une version antérieure de ce rapport classait les dates comme intruses dans
> CONFIG — c'était faux, et §5 phase 3 en est ressorti inversé : le travail n'est pas de sortir les
> dates de CONFIG, c'est d'y faire remonter les 430 qui sont ailleurs. Voir §3.4.)*

Classification automatique des 144 corps de triggers (**MEASURED**, script `audit8.py`) :

| Catégorie | Nb | Verdict |
| --- | --- | --- |
| **Déclaration pure** — tags, dates, seuils numériques, identifiants (`has_tech`, `has_completed_focus`, `has_autonomy_state`…) | **102** | ✅ à sa place |
| **Drapeau** `always = yes` / `always = no` | 22 | ⚠️ à sa place, mais à isoler et à documenter (§2.2) |
| **Composition** d'autres triggers CONFIG | 9 | ✅ à sa place |
| **Mixte** : déclaration **+** interrogation d'un autre pays | 7 | ⚠️ à scinder (§2.4) |
| **Verdict** sur l'état vivant du monde, aucune donnée déclarée | 4 | ❌ sort de CONFIG (§2.4) |
| *(transversal)* jamais lu hors de CONFIG | **15** | ❌ code mort (§2.1) |

**Le fichier CONFIG est donc en bien meilleur état que ne le suggère sa réputation : 133 des 144
triggers sont légitimes sous ta règle.** Le problème n'est pas ce que CONFIG contient — c'est ce
qui *devrait y être et n'y est pas* (§3.4), et les tables concurrentes (§3.1, §3.2).

Les familles de nommage se sont fragmentées (**MEASURED**) :
`WA_AI_CONFIG_*` 44 · `WA_AI_CONFIG_DIVISIONS_*` 43 · `WA_AI_CONFIG_MILITARY_*` 37 ·
`WA_AI_DIFFICULTY_*` 7 · `WA_AI_CONFIG_AIRFORCE_*` 7 · `WA_AI_CONFIG_TEMPLATES_*` 2 ·
`WA_AI_CONFIG_RAILWAY_*` 2 · `WA_AI_CONFIG_PC_*` 1 · `WA_AI_MILITARY_*` 1.

Huit triggers définis dans CONFIG ne portent pas le préfixe `WA_AI_CONFIG_` : les 7
`WA_AI_DIFFICULTY_*` (acceptable, famille cohérente) et **`WA_AI_MILITARY_pacific_high_risk`**
(§4.3).

### 2.1 Code mort dans CONFIG (15 triggers, **MEASURED** : 0 lecture hors CONFIG)

```
WA_AI_CONFIG_DIVISIONS_has_access_to_oil               (porte un TODO)
WA_AI_CONFIG_DIVISIONS_use_heavy_assault_tanks
WA_AI_CONFIG_DIVISIONS_use_heavy_infantry_support_tanks
WA_AI_CONFIG_DIVISIONS_use_light_assault_tanks
WA_AI_CONFIG_DIVISIONS_use_light_infantry_support_tanks
WA_AI_CONFIG_DIVISIONS_use_medium_assault_tanks
WA_AI_CONFIG_DIVISIONS_use_medium_infantry_support_tanks
WA_AI_CONFIG_DIVISIONS_use_modern_assault_tanks
WA_AI_CONFIG_DIVISIONS_use_modern_infantry_support_tanks
WA_AI_CONFIG_MILITARY_is_german_homeland_power         (créé 2026-08-21, jamais branché)
WA_AI_CONFIG_MILITARY_is_minor_naval
WA_AI_CONFIG_has_special_ai_navy_files
WA_AI_DIFFICULTY_is_competitive_normal
WA_AI_DIFFICULTY_is_historical_normal
WA_AI_MILITARY_pacific_high_risk                       (1 lecture, interne à CONFIG)
```

Cas notable : les 8 `*_assault_tanks` / `*_infantry_support_tanks` forment une famille complète
jamais câblée. Le commentaire de `WA_AI_CONFIG_MILITARY_is_western_european_bulwark`
(« les deux identités dont le déclencheur d'entrée italienne a besoin ») annonce
`is_german_homeland_power` comme utilisé — **il ne l'est pas**. C'est un exemple direct de
dérive commentaire/code que l'AGENTS.md règle 7 met en garde.

### 2.2 Drapeaux constants jamais basculés (22)

`always = yes` (13) : `use_default_templates`, `use_medium/heavy/modern_tank_destroyers`,
`use_light/medium/modern_self_propelled_gun`, `use_light/medium/modern_self_propelled_aa`,
`uses_default_ground_production`, `uses_default_tanks_production`, `uses_default_army_composition`.

`always = no` (9) : `use_motorized_divisions`, `use_armored_cars`, `use_modern_assault_tanks`,
`use_light_infantry_support_tanks`, `use_modern_infantry_support_tanks`,
`use_heavy_self_propelled_gun`, `use_mechanized_tank_destroyers`,
`use_mechanized_self_propelled_gun`, **`use_heavy_at`**.

Le pire : **`WA_AI_CONFIG_DIVISIONS_use_heavy_at = always no`, lu 24 fois dans
`common/scripted_effects/WA_AI_DIVISION_CREATOR_effects.txt`** (**MEASURED**). 24 branches mortes
dans le créateur de divisions, dont chacune doit être lue et comprise par quiconque touche ce
fichier. Le corps du trigger ne contient qu'un commentaire d'intention (« for development »).

Ces 22 drapeaux ne sont pas tous à supprimer : `uses_default_*` sont des interrupteurs de
migration délibérés. Mais ils doivent être **déclarés comme tels**, pas mélangés aux archétypes.

### 2.3 Corps strictement identiques (**MEASURED**)

| Corps | Triggers |
| --- | --- |
| `OR = { GER ENG }` | `AIRFORCE_uses_strike_bombers`, `AIRFORCE_uses_fast_bombers` |
| `OR = { ENG USA }` | `is_strategic_bombing_airforce`, `AIRFORCE_uses_heavy_strategic` |
| `OR = { GER ENG USA SOV FRA ITA JAP }` | `AIRFORCE_uses_multirole_fighters`, `AIRFORCE_uses_attackers` |
| `OR = { FRA ENG USA ITA JAP GER SOV }` | `DIVISIONS_focus_on_medium_armor`, `DIVISIONS_focus_on_light_armor` |
| `OR = { GER ENG SOV }` | `use_heavy_assault_tanks`, `use_heavy_infantry_support_tanks` |
| `OR = { GER SOV }` | `focus_on_cruiser_submarines`, `use_light_assault_tanks`, `use_medium_assault_tanks` |
| `original_tag = RAJ` | `is_commonwealth_egypt_support`, `is_commonwealth_gulf_guard`, `is_commonwealth_east_africa` |
| `original_tag = ENG` | `is_reserve_materiel_limited`, `MILITARY_is_british_mission_owner` |
| `original_tag = GER` | `is_mobile_warfare`, `MILITARY_is_german_homeland_power` |
| `original_tag = SOV` | `is_deep_battle`, `use_mechanized_self_propelled_aa` |
| `original_tag = USA` | `is_superior_firepower`, `DIVISIONS_is_expeditionary_mechanized_major` |

**DERIVED** : les trois `RAJ` et la paire `ENG`/`GER` sont **intentionnels** — leurs en-têtes
documentent explicitement « l'identité vit ici, la capacité vit ailleurs ». Ils ne doivent pas être
fusionnés. En revanche `strike_bombers` / `fast_bombers` (le commentaire dit lui-même
« similar to strike bombers ») et `focus_on_medium_armor` / `focus_on_light_armor` sont des
duplications **fonctionnelles** : deux noms, une seule notion.

### 2.4 Les 11 triggers CONFIG qui interrogent le monde vivant (**MEASURED**)

Sous ta règle, ce sont les seuls candidats à la sortie. Ils ne déclarent pas une valeur : ils
posent une question dont la réponse change en cours de partie.

| Ligne | Trigger | Ce qu'il interroge | Destination proposée |
| --- | --- | --- | --- |
| 990 | `WA_AI_CONFIG_faces_strategic_bombing` | `any_enemy_country` **+** liste GER/JAP/ITA | **scinder** : la liste reste, le balayage part dans `WA_AI_RESEARCH_*` |
| 365 | `WA_AI_CONFIG_majors_should_build_capitals` | `any_country_of` + `has_naval_treaty_trigger` | **scinder** : le seuil `1948.1.1` et la liste des 7 restent en CONFIG |
| 1072 | `WA_AI_CONFIG_RAILWAY_override_GER_to_SOV` | `SOV = { exists / has_war_with / is_in_faction_with }` | **scinder** : tag + dates + id de focus restent, la relation part dans les triggers railway |
| 1101 | `WA_AI_MILITARY_pacific_high_risk` | `any_enemy_country` | **sort** → `WA_AI_MILITARY_triggers.txt` (§4.3) |
| 1325 | `WA_AI_CONFIG_MILITARY_italian_power_shares_german_ideology` | compare deux gouvernements | **sort** → `WA_AI_MILITARY_triggers.txt` |
| 1336 | `WA_AI_CONFIG_MILITARY_western_bulwark_is_collapsing` | `FRA = { surrender_progress > 0 }` | **sort** → `WA_AI_MILITARY_triggers.txt` |
| 576 | `WA_AI_CONFIG_has_penalised_army_xp_gain` | `check_variable modifier@…` | **sort** → `WA_AI_TEMPLATES_triggers.txt` |
| 313 | `WA_AI_CONFIG_needs_cv_planes` | `has_navy_size type = carrier` | **sort** → `WA_AI_PRODUCTION_*` (c'est « ai-je un porte-avions », pas un seuil de réglage) |
| 100 | `WA_AI_CONFIG_is_in_allies` | `is_in_faction_with ENG/USA` | **reste** : les deux tags sont la donnée, l'appartenance en est la lecture naturelle |
| 1090 | `WA_AI_CONFIG_MILITARY_is_axis_minor` | `is_in_faction_with GER` + minor | **reste**, même raison |
| 1095 | `WA_AI_CONFIG_MILITARY_is_axis_non_german_member` | idem | **reste**, même raison |

Volume réel du déplacement : **6 triggers sortent, 3 se scindent, 2 restent.** C'est petit — et
c'est la bonne nouvelle du rapport.

---

## 3. La violation structurelle principale : trois couches de classification concurrentes

Le principe « toute la config dans WA_AI_CONFIG » a été **contourné à trois endroits**.

### 3.1 `WA_AI_MISC_triggers.txt` — une deuxième table de classification pays

**MEASURED**, `common/scripted_triggers/WA_AI_MISC_triggers.txt` définit :

| Trigger | Contenu | Lecteurs |
| --- | --- | --- |
| `WA_AI_major_country` | 7 tags majeurs **+ `num_of_civilian_factories > 99`** | LAW, LEND_LEASE, DIPLOMACY, `events/WA_AI_misc.txt`, debug |
| `WA_AI_civil_war_country` | D01–D15 | **aucun** (mort) |
| `WA_AI_asian_minor` | 15 tags | **aucun** (mort) |
| `WA_AI_commonwealth` | 5 tags | **aucun** (mort) |
| `WA_AI_european_minor` | 14 tags | **aucun** (mort) |
| `WA_AI_neutral_country` | 8 tags | LEND_LEASE |

**C'est le piège le plus dangereux du dépôt aujourd'hui.**
`WA_AI_major_country` ≠ `WA_AI_CONFIG_is_major_country` : le premier ajoute
`num_of_civilian_factories > 99`. Donc **le système de lois, le prêt-bail et la diplomatie
utilisent une définition de « majeur » différente de celle utilisée par les templates, la
production, la recherche, les doctrines et le militaire** (**DERIVED** du tableau ci-dessus).
Rien dans les deux fichiers ne signale cette divergence. Un lecteur qui modifie la liste des
majeurs dans CONFIG ne changera pas le comportement des lois.

Quatre des six triggers sont du code mort pur.

### 3.2 `WA_AI_MILITARY_triggers.txt` — une troisième table, dans le « moteur »

**MEASURED**, `common/scripted_triggers/WA_AI_MILITARY_triggers.txt:463-523` définit de la
classification pays dans le fichier censé être le panneau de contrôle :

```
WA_AI_MILITARY_is_minor_country      = NOT { WA_AI_CONFIG_is_major_country }   ← alias pur
WA_AI_MILITARY_is_major_naval        = has_navy_size > 100                     ← COLLISION (§4.1)
WA_AI_MILITARY_is_major_continental  = has_army_manpower > 1 000 000
WA_AI_MILITARY_is_axis_member        = is_in_faction_with GER
WA_AI_MILITARY_is_comintern_member   = tag SOV | in faction with SOV
WA_AI_MILITARY_is_co_prosperity_member = tag JAP | in faction with JAP
WA_AI_MILITARY_is_china_front_member = 14 tags littéraux + in faction with CHI
WA_AI_MILITARY_is_commonwealth_member= 7 original_tag littéraux
```

`is_china_front_member` (14 tags) et `is_commonwealth_member` (7 tags) sont de la classification
pure par tag : leur place est CONFIG. `is_commonwealth_member` n'est d'ailleurs lu que dans son
propre fichier (**MEASURED** : 2 occurrences, dont la définition) — quasi-mort.

`WA_AI_CONFIG_MILITARY_is_chinese_warlord` (CONFIG, 11 tags) et
`WA_AI_MILITARY_is_china_front_member` (MILITARY, 14 tags) décrivent le même espace de pays avec
deux listes qui ne coïncident pas. Le commentaire de CONFIG l'admet (« Distinct from … which
includes the leaders ») mais les deux listes doivent être maintenues à la main en parallèle.

### 3.3 `common/ai_strategy/WA_AI_MILITARY_*` — 55 portes par tag hors couche Country

L'AGENTS.md règle 4 interdit `tag =` / `original_tag =` comme terme de **gating** (dans
`allowed = {}` / `enable = {}`) hors des fichiers de couche Country. **MEASURED** (script
`audit6.py`, pseudo-scopes ROOT/PREV/FROM exclus, comparaisons dans un scope imbriqué exclues) :

| Fichier (couche) | Portes par tag |
| --- | --- |
| `WA_AI_MILITARY_FACTION_ALLIES_DIPLOMACY.txt` | 15 |
| `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt` | 7 |
| `WA_AI_MILITARY_FACTION_AXIS_DIPLOMACY.txt` | 6 |
| `WA_AI_MILITARY_FACTION_AXIS_FRONT.txt` | 6 |
| `WA_AI_MILITARY_FACTION_ALLIES_THEATRE.txt` | 5 |
| `WA_AI_MILITARY_FACTION_ALLIES_FRONT.txt` | 3 |
| `WA_AI_MILITARY_FACTION_CHINA_FRONT_DIPLOMACY.txt` | 2 |
| `WA_AI_MILITARY_FACTION_CO_PROSPERITY_FRONT.txt` | 2 |
| `WA_AI_MILITARY_DEFAULT_THEATRE.txt` | 2 |
| `WA_AI_PRODUCTION_lend_lease.txt` | 5 |
| **Total** | **55** |

Deux listes multi-tags franches restent en couche Faction :
`ALLIES_DIPLOMACY.txt:99-104` (SPR POR LUX BEL HOL SWI) et `:142-148` (POL CZE HUN ROM YUG ALB GRE).
La phase 3 du refactor militaire les avait manquées.

`WA_AI_espionage_strategies.txt:142,167` utilise `tag = var:WA_AI_boost_resistance_operation_target`
— légitime (cible dynamique), à exclure de tout compteur automatique.

### 3.4 Le vrai trou : 430 dates et 499 seuils numériques vivent hors de CONFIG

C'est la conséquence la plus lourde de ta règle, et elle n'apparaissait pas dans la version
précédente de cet audit.

**MEASURED** (script `audit_numbers.py`, commentaires exclus, fichiers `WA_*` de
`scripted_triggers` / `scripted_effects` / `ai_strategy` / `events` / `on_actions`) :

| Zone | `date [<>] YYYY.M.D` littérales | Seuils numériques (`num_of_*`, manpower, taille de flotte, war support…) |
| --- | --- | --- |
| `common/ai_strategy` | **283** | **190** |
| `events` | 61 | 80 |
| `common/scripted_triggers` (hors CONFIG) | 48 | 174 |
| `common/scripted_effects` | 24 | 40 |
| `common/on_actions` + divers | 2 | 10 |
| **`WA_AI_CONFIG.txt`** | **12** | **5** |
| **Total** | **430** | **499** |

**DERIVED** : CONFIG détient **2,8 %** des dates et **1,0 %** des seuils du système AI. Le principe
« les dates et les nombres sont en config » n'est pas *érodé*, il n'a **jamais** été appliqué en
dehors des systèmes qui ont adopté les *script constants* (voir plus bas).

Fichiers les plus chargés en dates littérales (**MEASURED**) :

| Fichier | Dates |
| --- | --- |
| `WA_AI_MILITARY_COUNTRY_JAP_FRONT.txt` | 28 |
| `WA_AI_MILITARY_FACTION_ALLIES_INVASION.txt` | 23 |
| `WA_AI_LAW_triggers.txt` | 21 |
| `WA_AI_MILITARY_COUNTRY_JAP_INVASION.txt` | 19 |
| `WA_AI_MILITARY_COUNTRY_SOV_THEATRE.txt` | 18 |
| `WA_AI_MILITARY_COUNTRY_GER_FRONT.txt` | 17 |
| `WA_AI_MILITARY_FACTION_ALLIES_FRONT.txt` | 17 |

Dates répétées à l'identique dans des fichiers différents (**MEASURED**) : `1942.1.1` **56 fois**,
`1940.1.1` 32 fois, `1941.1.1` 26 fois, `1938.1.1` 15 fois, `1944.6.6` 10 fois. Chacune est une
décision de conception (« la guerre est mondiale », « la France est tombée », « Overlord ») recopiée
à la main N fois, sans nom, sans point de vérité.

**Il existe déjà un mécanisme, mais seulement 8 systèmes l'utilisent.** `common/script_constants/`
(HOI4 1.18, lu par `constant:<cat>.<groupe>.<clé>`) est adopté par PC (214 lectures), lend-lease
(105), railway (78), posture (44), resource (31), AIFC (30), production (18), leaders (7)
— **MEASURED**. Les systèmes militaire, templates, lois, recherche et doctrines en utilisent
**zéro**. Ce sont exactement ceux qui portent les 430 dates.

**Deux obstacles techniques, à ne pas sous-estimer :**

1. **ASSUMED** — `date > constant:x.y.z` n'est écrit **nulle part** dans le dépôt (**MEASURED** :
   0 occurrence) et une date PDXScript n'est pas un nombre. Il est donc probable que les *script
   constants* ne sachent pas porter une date. Le véhicule pour une date est alors le **trigger
   nommé en CONFIG** — le motif que CONFIG applique déjà correctement avec
   `WA_AI_CONFIG_switch_from_light_to_medium_armor` et
   `WA_AI_CONFIG_DIVISIONS_mechanization_window_open`. À mesurer en phase 0.
2. **MEASURED** (skill `wa-constants-registry`) — `constant:` ne fonctionne **pas** dans
   `ai_strategy value =`. Or `common/ai_strategy` porte 283 des 430 dates et 190 des 499 seuils.
   Les `date`/`num_of_*` situés dans les blocs `allowed`/`enable` sont, eux, en contexte trigger et
   restent adressables ; ceux situés dans `value =` ne le sont pas.

### 3.5 Une quatrième maison pour les listes de tags — **MEASURED**

`common/script_constants/country_groups.txt` définit `country_groups.continental_europe_1936`
(25 tags), plus deux groupes entièrement commentés (`nordics`, `literally_china`). Lu par
`common/collections/collections.txt` et `common/factions/goals/faction_goals_medium_term.txt`
— **jamais par un fichier `WA_AI_*`**.

Ce n'est pas un problème aujourd'hui (3 lectures), mais c'est la quatrième syntaxe qui prétend
héberger une liste de pays, après CONFIG, `WA_AI_MISC_triggers` et `WA_AI_MILITARY_triggers`. La
refactorisation doit trancher : soit `country_groups` devient le porteur officiel des listes de
tags (avantage : c'est une *donnée*, itérable, pas un trigger booléen), soit il est déclaré hors
périmètre AI et documenté comme tel.

---

## 4. Cas étranges à te signaler

### 4.1 Collision de noms : deux `is_major_naval` de sens opposés — **MEASURED**

| Nom | Fichier | Corps | Sens |
| --- | --- | --- | --- |
| `WA_AI_CONFIG_MILITARY_is_major_naval` | CONFIG:1146 | `tag = ENG/USA/JAP/GER/ITA/FRA` | **identité** |
| `WA_AI_MILITARY_is_major_naval` | MILITARY_triggers:467 | `has_navy_size > 100` | **capacité** |

Deux noms qui diffèrent de 7 caractères, deux sémantiques différentes, lus dans les mêmes
fichiers (`WA_AI_MILITARY_DEFAULT_FRONT_archetypes.txt` lit le second ; `WA_AI_NAVAL_*` lit les
deux familles). C'est exactement le genre de paire où une faute de frappe ne produit aucune
erreur de parsing et un comportement silencieusement faux.

### 4.2 Inversion de couche : CONFIG → moteur → CONFIG — **MEASURED**

```
WA_AI_CONFIG_MILITARY_is_axis_minor   (CONFIG:1090)
  └─ WA_AI_MILITARY_is_minor_country  (MILITARY_triggers:463)   ← couche moteur
       └─ WA_AI_CONFIG_is_major_country (CONFIG:61)             ← retour dans CONFIG
```

CONFIG dépend du moteur qui dépend de CONFIG. Pas de récursion infinie (les nœuds diffèrent), mais
la règle « CONFIG ne dépend de rien » est cassée, et le graphe n'est plus lisible en une passe.

### 4.3 Chaîne d'alias à trois sauts qui traverse deux fois la frontière — **MEASURED**

```
WA_AI_MILITARY_pacific_war_active      (MILITARY_triggers:533)   moteur
  └─ WA_AI_CONFIG_MILITARY_pacific_high_risk (CONFIG:1114)       config, alias pur
       └─ WA_AI_MILITARY_pacific_high_risk   (CONFIG:1101)       ← nom « moteur », défini dans CONFIG
```

Trois noms pour une seule question. Le maillon du milieu n'ajoute rien. Le maillon du bas porte le
préfixe `WA_AI_MILITARY_` alors qu'il est défini dans CONFIG — il est d'ailleurs le seul trigger
de CONFIG à ne respecter aucune des deux conventions de nommage du fichier.

### 4.4 `if = { }` imbriqué directement dans `OR = { }` — **ASSUMED**, 3 occurrences

**MEASURED** (script `audit_ifor.py`) — 3 sites :

| Site | Contexte |
| --- | --- |
| `common/scripted_triggers/WA_AI_CONFIG.txt:433` | `WA_AI_CONFIG_DIVISIONS_use_armored_divisions` |
| `common/ai_strategy/WA_AI_MILITARY_COUNTRY_GER_FRONT.txt:1429` | `enable` d'un bloc AIFC Alsace-Lorraine |
| `common/scripted_effects/WA_AI_pathfinding_effects.txt:268` | effet, sémantique différente |

Le cas CONFIG:425-442 :

```
WA_AI_CONFIG_DIVISIONS_use_armored_divisions = {
	OR = {
		original_tag = ENG … SOV
		if = {
			limit = { WA_AI_DIFFICULTY_is_historical = yes }
			OR = { original_tag = JAP  original_tag = ITA }
		}
	}
}
```

**ASSUMED** : si `if` dont le `limit` est faux s'évalue à **vrai** (comportement Clausewitz
usuel), alors en difficulté *compétitive* ce `OR` est vrai **pour tous les pays**, et
`use_armored_divisions` devient universel. Or ce trigger pilote aussi
`WA_AI_CONFIG_DIVISIONS_uses_motorized_hq` → `history/general/taog_hq_template.txt`, plus
`WA_AI_RESEARCH_needs_maintenance_company` et `needs_mechanized` : l'impact ne serait pas limité
aux templates blindés.

**La documentation du moteur ne tranche pas.** `documentation/triggers_documentation.md` de
l'install 1.19.2 (section `## if`) dit seulement `if = { limit = { <triggers> } <trigger> }`, sans
préciser la valeur quand `limit` est faux. **Ce point doit être MESURÉ avant toute décision.**

### 4.5 `NOT = { A  B  C }` à plusieurs enfants — **ASSUMED**, 71 occurrences

**MEASURED** (script `audit_not.py`) : 71 blocs `NOT` à ≥ 2 enfants directs dans les fichiers
`WA_*` AI.

| Fichier | Occurrences |
| --- | --- |
| `WA_AI_LAW_triggers.txt` | 16 |
| `events/WA_AI_GER.txt` | 13 |
| `WA_AI_MILITARY_triggers.txt` | 9 |
| `WA_AI_LEND_LEASE_triggers.txt` | 6 |
| `WA_AI_DIVISION_CREATOR_effects.txt` | 4 |
| `WA_production_strategy_effects.txt` | 4 |
| 17 autres fichiers | 19 |

Exemple, `WA_AI_LAW_triggers.txt:107-114` :

```
NOT = {
	WA_AI_can_take_civilian_economy = yes
	WA_AI_can_take_partial_economic_mobilisation = yes
	WA_AI_can_take_war_economy = yes
	WA_AI_can_take_tot_economic_mobilisation = yes
	WA_AI_can_take_over_mobilisation = yes
}
```

L'intention est manifestement « aucune de ces cinq ». Si le moteur évalue `NOT` comme **NAND**
(`NOT(A ET B ET C…)`), la condition est vraie dès qu'une seule des cinq est fausse — c'est-à-dire
presque toujours — et la garde ne garde rien. Si le moteur évalue **NOR**, l'intention est
respectée.

`documentation/triggers_documentation.md` (section `## not`) dit exactement :
« negates content of trigger ». **Ambigu.** Ce point aussi doit être MESURÉ.

C'est la découverte à la plus forte valeur du présent audit : **71 sites dépendent d'une
sémantique que personne dans ce dépôt n'a vérifiée**, dont 16 dans le système de lois et 13 dans
les événements AI allemands.

### 4.6 Faute de casse : `has_war_With` — **MEASURED**

`common/ai_strategy/WA_AI_MILITARY_COUNTRY_GER_FRONT.txt:1431` écrit `has_war_With = POL`
(`W` majuscule). **ASSUMED** : le parseur PDXScript est généralement insensible à la casse pour
les noms de triggers, donc probablement sans effet — mais c'est le même bloc que le §4.4, donc
deux hasards s'y superposent.

### 4.7 Définitions dupliquées à l'identique — **MEASURED**

| Nom | Fichier | Lignes |
| --- | --- | --- |
| `WA_AI_TEMPLATES_has_mechanized_spaa_unlocked` | `WA_AI_TEMPLATES_triggers.txt` | 1266 **et** 1627 (corps identiques) |
| `WA_add_mastery_strike_75` | `WA_scripted_effects.txt` | 12739 **et** 12840 |

Sans conséquence fonctionnelle (le moteur en retient une), mais c'est du bruit dans un fichier de
1756 lignes.

### 4.8 `common/country_leader/00_traits.txt` lit 11 triggers CONFIG — **MEASURED**

C'est le 5ᵉ plus gros lecteur de CONFIG, dans un dossier remplacé de vanilla. Rien d'illégal, mais
c'est un couplage que ni `AGENTS.md` ni les skills ne mentionnent : quiconque modifie un archétype
de doctrine dans CONFIG modifie aussi la sélection des traits de dirigeants.

### 4.9 `WA_AI_LAW_triggers.txt` : 2163 lignes, 20 triggers, 272 tags — **MEASURED**

Ce n'est pas de la config au sens du principe 2 : les blocs `if = { limit = { original_tag = HUN }
… }` recopient à la main les `available` des lois vanilla (le fichier le dit lui-même : « copy from
idea file »). C'est un **miroir de données vanilla**, avec un risque de dérive à chaque patch
Paradox, et un ratio de 108 lignes par trigger. Il mérite sa propre catégorie et son propre plan,
distinct de la refactorisation CONFIG.

---

## 5. Proposition de refactorisation

Principe directeur : **aucune modification de comportement dans les phases 1 à 4.** Chaque phase
se termine par `check_constants.py` + `check_worklist.py` à 0, et par un diff sémantique vérifié.
Les changements de comportement sont isolés en phase 5, un par sujet WORK.md, chacun avec son
critère de fermeture.

### Phase 0 — Mesurer les deux inconnues moteur (BLOQUANT)

Rien ne doit bouger avant. Trois questions, un seul harnais console `WA_TEST_pdx_semantics`
(contrat harnais v1, fichier d'événements dédié) :

1. `OR = { always = no  if = { limit = { always = no }  always = no } }` → vrai ou faux ?
   *(décide §4.4, 2 sites, dont un trigger CONFIG lu par 3 systèmes)*
2. `NOT = { always = yes  always = no }` → vrai (NAND) ou faux (NOR) ?
   *(décide §4.5, 71 sites)*
3. `date > constant:wa_ai_test.dates.probe` → parse-t-il, et compare-t-il juste ?
   *(décide §3.4 : si oui, les 430 dates peuvent devenir des constantes nommées ; si non, le
   véhicule est le trigger CONFIG nommé, et le plan de la phase 3 change de forme)*

Sortie attendue : trois lignes de log, plus un contrôle connu-faux. **Tu dois lancer ce harnais en
console et coller la sortie** — c'est la règle du dépôt pour tout effet scripté, et ici les trois
réponses décident de 500 sites.

Selon les réponses :
- si `if`-faux → vrai : `WA_AI_CONFIG_DIVISIONS_use_armored_divisions` est cassé en compétitif et
  `GER_FRONT.txt:1429` est plus large que prévu → deux sujets WORK.md.
- si `NOT` = NAND : les 71 sites doivent être relus un par un ; les 16 du système de lois en
  priorité.
- si `date > constant:` échoue : la phase 3 passe par des triggers CONFIG nommés (pas de
  constantes), ce qui est plus verbeux mais reste conforme à ta règle.

### Phase 1 — Nettoyage sans risque (aucun lecteur touché)

| Action | Volume | Risque |
| --- | --- | --- |
| Supprimer les 15 triggers CONFIG jamais lus (§2.1) | −~90 lignes | nul (**MEASURED** : 0 lecteur) |
| Supprimer les 4 triggers MISC morts (§3.1) | −~50 lignes | nul |
| Supprimer la 2ᵉ définition de `WA_AI_TEMPLATES_has_mechanized_spaa_unlocked` et de `WA_add_mastery_strike_75` | −~25 lignes | nul (corps identiques) |
| Retirer les listes de tags commentées dans `use_anti_tank_brigades` / `use_anti_air_brigades` | −~35 lignes | nul |

Avant suppression de chaque trigger : re-grep du nom sur tout le dépôt **y compris
`localisation/`, `tools/` et `tests/`**, pour éviter le cas d'un nom cité dans un harnais.

### Phase 2 — Réunifier la classification (sémantique préservée, sauf un cas à trancher)

1. **Déplacer** vers CONFIG, à l'identique, avec le préfixe `WA_AI_CONFIG_MILITARY_` :
   `is_china_front_member` (14 tags), `is_commonwealth_member` (7 tags). Laisser dans
   `WA_AI_MILITARY_triggers.txt` un alias de compatibilité **temporaire** le temps de migrer les
   lecteurs, puis le supprimer dans le même commit que le dernier lecteur migré.
2. **Laisser dans le moteur** `is_major_naval` (taille de flotte) et `is_major_continental`
   (manpower) : ce sont des capacités, pas des identités. Mais **renommer**
   `WA_AI_MILITARY_is_major_naval` → `WA_AI_MILITARY_has_ocean_going_fleet` et
   `WA_AI_MILITARY_is_major_continental` → `WA_AI_MILITARY_has_mass_army`, pour tuer la collision
   §4.1. 4 fichiers lecteurs (**MEASURED**).
3. **Supprimer** l'alias pur `WA_AI_MILITARY_is_minor_country` : le remplacer chez ses 3 lecteurs
   externes par `NOT = { WA_AI_CONFIG_is_major_country = yes }`, ou mieux, créer
   `WA_AI_CONFIG_is_minor_country` (qui existe déjà !) et l'utiliser. Cela supprime aussi
   l'inversion de couche §4.2.
4. **Effondrer** la chaîne §4.3 : garder un seul `WA_AI_MILITARY_pacific_high_risk` défini dans
   `WA_AI_MILITARY_triggers.txt` (c'est une capacité : « une guerre pacifique me menace »),
   supprimer les deux autres maillons, migrer les lecteurs.
5. **`WA_AI_major_country` (MISC) — DÉCISION REQUISE.** C'est le seul point de la phase 2 qui
   change potentiellement du comportement. Trois options, dans mon ordre de préférence :
   - **(a) recommandé** — reconnaître que c'est une notion différente et la renommer
     `WA_AI_CONFIG_is_industrial_power` (7 majeurs OU > 99 civils), la déplacer dans CONFIG, et
     laisser LAW/LEND_LEASE/DIPLOMACY la lire sous ce nom. **Zéro changement de comportement**,
     et la divergence devient explicite au lieu d'être un piège.
   - (b) aligner LAW/LEND_LEASE/DIPLOMACY sur `WA_AI_CONFIG_is_major_country` → **change** le
     comportement des lois pour tout pays à > 99 usines civiles non majeur (à mesurer sur save
     avant de trancher).
   - (c) ajouter `num_of_civilian_factories > 99` à `WA_AI_CONFIG_is_major_country` → **change**
     le comportement de 11 fichiers. À écarter.

### Phase 3 — Faire de CONFIG le porteur réel des tags, nombres et dates

Deux mouvements de sens opposé. Le second est de loin le plus gros.

**3a — Sortir les 6 verdicts qui n'ont rien à déclarer (§2.4).** Petit, mécanique, sans
changement sémantique : déplacer le bloc tel quel vers le fichier de triggers du système qui le
consomme, garder un alias de compatibilité le temps de migrer les lecteurs, supprimer l'alias dans
le commit du dernier lecteur. Scinder les 3 mixtes : la partie « valeur » reste en CONFIG, la
partie « question au monde » part avec le verdict.

**3b — Faire remonter les dates et les nombres (§3.4).** 430 dates et 499 seuils. On ne les traite
pas d'un coup ; on les traite **par système, dans l'ordre du volume**, un commit par système :

| Lot | Cible | Dates | Seuils | Véhicule |
| --- | --- | --- | --- | --- |
| 1 | `WA_AI_MILITARY_COUNTRY_JAP_*` (FRONT + INVASION) | 47 | — | trigger CONFIG nommé par fenêtre (ex. `WA_AI_CONFIG_JAP_southward_window_open`) |
| 2 | `WA_AI_MILITARY_FACTION_ALLIES_*` | 52 | — | idem, fenêtres de coalition |
| 3 | `WA_AI_MILITARY_COUNTRY_GER_*` / `SOV_*` | 62 | — | idem |
| 4 | `WA_AI_LAW_triggers.txt` | 21 | 33 | à traiter avec le §4.9, séparément |
| 5 | `events/WA_AI_invasions.txt` | — | 75 | `common/script_constants/wa_ai_invasions.txt` (contexte trigger, `constant:` valide) |
| 6 | `WA_AI_PRODUCTION_*` | — | 66 | `wa_ai_production.txt` existe déjà, il suffit de l'étendre |

Règle de découpe pour chaque lot : **un nom par intention, pas un nom par date.** `1942.1.1`
apparaît 56 fois — s'il s'agit bien d'une seule intention (« la guerre est devenue mondiale »),
c'est **un** trigger CONFIG lu 56 fois, pas 56 constantes. S'il s'agit de plusieurs intentions qui
coïncident, ce sont plusieurs noms, et le fait qu'ils portent la même date devient visible et
questionnable — ce qui est précisément l'intérêt.

Ce lot dépend de la réponse 3 de la phase 0 : constante nommée si `date > constant:` fonctionne,
trigger CONFIG nommé sinon. **Dans les deux cas la donnée remonte en CONFIG ; seule la syntaxe
change.** Les `value =` des blocs `ai_strategy` ne sont pas adressables par `constant:`
(**MEASURED**) et restent donc littéraux — à documenter comme exception, pas à masquer.

**3c — Organisation du fichier.** CONFIG passera de 1566 à ~2500 lignes une fois les fenêtres
remontées. Le découper alors en trois fichiers du même dossier et du même préfixe (le moteur ne
voit pas la frontière de fichier) :

| Fichier | Contenu | Nb estimé |
| --- | --- | --- |
| `WA_AI_CONFIG.txt` | Identités : tags, archétypes, compositions | ~110 |
| `WA_AI_CONFIG_WINDOWS.txt` | Toutes les fenêtres temporelles et tous les seuils nommés | ~80 |
| `WA_AI_CONFIG_FLAGS.txt` | Les 22 `always = yes/no`, chacun avec une ligne disant *ce qui le ferait basculer* | 22 |

Rien ne bouge en sémantique dans les phases 3a et 3c : déplacements de blocs à l'octet près,
**sans BOM** (règle 16). La phase 3b change du texte mais pas des valeurs — chaque commit se
vérifie par un diff qui montre littéral remplacé par référence, jamais un nombre modifié.

### Phase 4 — Résorber les 55 portes par tag hors couche Country (§3.3)

Par fichier, du plus gros au plus petit, un commit par fichier :

1. `ALLIES_DIPLOMACY.txt:99-104` → nouvel archétype `WA_AI_CONFIG_MILITARY_is_western_neutral`
   (SPR POR LUX BEL HOL SWI).
2. `ALLIES_DIPLOMACY.txt:142-148` → `WA_AI_CONFIG_MILITARY_is_eastern_european_state`
   (POL CZE HUN ROM YUG ALB GRE).
3. Les mono-tags restants (`tag = ENG`, `NOT = { tag = CHI }`, …) sont **autorisés** par la règle 4
   telle qu'écrite. Les laisser, mais ajouter au checker une liste blanche explicite, pour que
   « ce mono-tag est délibéré » devienne une donnée et pas une lecture d'intention.

### Phase 5 — Mécaniser l'invariant (le point qui empêche la re-dérive)

C'est la seule vraie leçon des « mois de changements » : les principes n'ont pas tenu parce que
rien ne les vérifiait. Ajouter à `tools/check_worklist.py` (qui a déjà un `--selftest` avec fixture
obligatoire par règle) :

| Règle | Détecte |
| --- | --- |
| `CONFIG-DEAD` | Un trigger défini dans `WA_AI_CONFIG*` et lu nulle part. |
| **`DATE-LEAK`** | Une `date [<>] YYYY.M.D` littérale dans un fichier `WA_AI_*` **hors** `WA_AI_CONFIG*`. **C'est la règle centrale de ta politique.** Seuil de départ = compte actuel (430), à faire décroître ; la règle échoue si le compte remonte. |
| **`NUMBER-LEAK`** | Un seuil numérique (`num_of_*`, `has_army_manpower`, `has_navy_size`, `has_war_support`…) dans un fichier `WA_AI_*` hors `WA_AI_CONFIG*` et hors `script_constants`. Même mécanique de cliquet (499). |
| `CONFIG-LIVE` | Un `any_enemy_country` / `any_country_of` / `surrender_progress` / `check_variable` dans `WA_AI_CONFIG*` : CONFIG déclare, il n'interroge pas le monde. |
| `CLASSIFICATION-LEAK` | Un `original_tag =` littéral dans un `OR` de ≥ 3 termes hors `WA_AI_CONFIG*` et hors couche Country. |
| `NAME-COLLISION` | Deux triggers dont les noms ne diffèrent que par un segment de préfixe (`WA_AI_X_foo` / `WA_AI_CONFIG_X_foo`). |
| `DUP-DEF` | Un même nom de trigger/effect défini deux fois. |
| `NOT-MULTI` | Un `NOT` à ≥ 2 enfants directs (avertissement, tant que §4.5 n'est pas mesuré). |

Le **cliquet** (`DATE-LEAK` / `NUMBER-LEAK` avec un compte de référence qui ne peut que baisser)
est le seul dispositif qui rend la phase 3b faisable sans tout bloquer : on ne demande à personne
de migrer 430 dates avant de pouvoir committer, on interdit seulement d'en ajouter une 431ᵉ.

Chaque règle arrive avec sa fixture, sinon `--selftest` la rejette — c'est déjà le contrat du
fichier.

### Hors périmètre, à traiter séparément

`WA_AI_LAW_triggers.txt` (§4.9). 2163 lignes de miroir de données vanilla. C'est un sujet à part
entière, avec sa propre question de conception (génération par outil depuis
`common/ideas/` plutôt que copie manuelle ?). Ne pas l'emballer dans la refactorisation CONFIG.

---

## 6. Ordre d'exécution recommandé

```
Phase 0  (harnais console, TOI)             → débloque tout le reste
Phase 1  (suppressions, 0 risque)           → −200 lignes, checkers à 0
Phase 5  (checker, AVANCÉE ICI)             → pose le cliquet avant de migrer quoi que ce soit
Phase 2  (réunification, 1 décision)        → tue §4.1 §4.2 §4.3 §3.1
Phase 3a (6 verdicts sortent de CONFIG)     → petit, mécanique
Phase 4  (55 portes par tag)                → règle 4 respectée
Phase 3b (430 dates + 499 seuils remontent) → 6 lots, un commit par système, le gros du travail
Phase 3c (découpage en 3 fichiers)          → une fois le volume connu
```

**La phase 5 passe en 3ᵉ position.** Poser le cliquet `DATE-LEAK` / `NUMBER-LEAK` *avant* la
migration est ce qui garantit que la phase 3b converge : sans lui, on migre 40 dates pendant que
10 nouvelles apparaissent ailleurs, ce qui est exactement le mécanisme par lequel les principes
d'origine se sont érodés.

Phases 1, 2, 3a, 3c, 4 : aucune vérification en campagne nécessaire si le diff sémantique est vide
(sauf le choix 2.b/2.c, qui en exigerait une). Phase 3b : diff littéral→référence à relire lot par
lot. Phase 0 : harnais console obligatoire.

---

## 7. Ce que je te demande de trancher

1. **Phase 0** : acceptes-tu de lancer le harnais `WA_TEST_pdx_semantics` en console ? Sans ça, les
   §4.4 et §4.5 restent ASSUMED, je ne peux pas dire si 71 gardes fonctionnent, et je ne sais pas
   quel véhicule utiliser pour les 430 dates.
2. **`WA_AI_major_country`** (§3.1, phase 2 point 5) : option (a) renommer en
   `WA_AI_CONFIG_is_industrial_power` — c'est ma recommandation, comportement inchangé ?
3. **Portée de la phase 3b** (§3.4) : 430 dates + 499 seuils, c'est le plus gros lot du plan.
   Tu veux les **six lots**, ou seulement les lots militaires 1-3 (~110 dates) en laissant les
   lois, les invasions et la production pour plus tard ?
4. **Granularité de nommage** (phase 3b) : `1942.1.1` apparaît **56 fois**. Un seul nom partagé
   (« la guerre est mondiale »), ou un nom par système quitte à ce que plusieurs portent la même
   date ? Ma recommandation : **un nom par intention** — les collisions de date deviennent alors
   visibles et discutables. Mais c'est toi qui sais si ces 56 sites disent la même chose.
5. **`country_groups.txt`** (§3.5) : porteur officiel des listes de tags AI, ou hors périmètre AI
   et documenté comme tel ?
6. Les 8 triggers `*_assault_tanks` / `*_infantry_support_tanks` morts (§2.1) : suppression, ou
   c'était une famille en cours de câblage qu'il faut au contraire brancher ?
