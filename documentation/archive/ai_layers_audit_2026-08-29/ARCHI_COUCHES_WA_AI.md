# Modèle en couches WA_AI — évaluation de ta vision et contre-proposition

Complément à `AUDIT_WA_AI_CONFIG.md`. Même base : branche `ai-rework`, HEAD `c339245b5`.

---

## 1. Ta vision, telle que je la comprends

| Couche | Rôle | Matière |
| --- | --- | --- |
| 1 | **CONFIG** — point d'entrée unique, tous les éléments de configuration | `WA_AI_CONFIG*` |
| 2 | **Runtime** — assemble les éléments de config en portes logiques | `scripted_triggers` |
| 3 | **Consommateurs** — le reste du code IA | `ai_strategy`, `scripted_effects`, `events` |

**Verdict : la direction est juste, et elle est meilleure que ce qui existe aujourd'hui**
— parce que ce qui existe n'est ni écrit ni vérifié, et qu'une règle explicite bat toujours une
règle implicite. Mais elle a trois défauts structurels qui, laissés tels quels, reproduiront
exactement la dérive des derniers mois.

---

## 2. Défaut 1 — les couches 1 et 2 sont faites de la même matière

En PDXScript, un `scripted_trigger` est une **fonction booléenne**. Il n'existe aucun type
« déclaration ». Les seules matières disponibles sont :

| Matière | Peut porter | Ne peut pas porter |
| --- | --- | --- |
| `common/script_constants/` | nombres, tableaux de tags | dates (**ASSUMED**, §3.4 de l'audit), booléens |
| `scripted_trigger` | tout, mais **sous forme de porte logique** | une valeur nue |
| `05_defines.lua` | nombres moteur | rien d'autre |

Conséquence : dès qu'on écrit une date en config, on écrit **déjà une porte logique**.
`WA_AI_CONFIG_switch_from_light_to_medium_armor` *est* la date **et** la porte. La frontière
entre ta couche 1 et ta couche 2 n'est donc pas exprimable dans le langage — elle ne peut être
qu'une **convention**. Et une convention que rien ne vérifie est exactement ce qui a cédé.

**Ce qu'il faut à la place : une propriété testable.** Je propose celle-ci, parce qu'elle est
mécanisable en une règle de checker :

> **Un bloc CONFIG ne lit rien qui change sans qu'un joueur ou une IA ait agi.**
> Pas de guerre, pas de contrôleur, pas de front, pas de scope d'un autre pays,
> pas de `check_variable`. Tags, dates, seuils, identifiants (`has_tech`, `has_completed_focus`,
> `has_autonomy_state`) : oui.

**MEASURED** : le CONFIG actuel passe déjà ce test à **133/144**. Les 11 exceptions sont listées
au §2.4 de l'audit. La règle n'est donc pas une refonte, c'est la formalisation de ce que le
fichier fait déjà à 92 %.

---

## 3. Défaut 2 — « point d'entrée unique » est un goulot, pas une vertu

**MEASURED** : les 144 triggers CONFIG sont lus depuis **11 dossiers** ;
`WA_AI_CONFIG_is_major_country` est lu par **11 fichiers** appartenant à 6 systèmes différents.

C'est précisément pourquoi personne n'ose y toucher — et pourquoi quelqu'un a fini par forker
`WA_AI_major_country` dans `WA_AI_MISC_triggers.txt` avec un `num_of_civilian_factories > 99` en
plus (§3.1 de l'audit). **Le fork n'est pas de l'indiscipline : c'est la réponse rationnelle à un
goulot.** Quand modifier la valeur partagée est trop risqué, on en fait une copie.

Point de vérité unique **par concept** ≠ fichier unique. Ce qui manque n'est pas l'unicité du
fichier, c'est **une règle sur qui a le droit de lire CONFIG**.

> **CONFIG n'est jamais lu par la couche consommateur.** Un `ai_strategy`, un `event`, un
> `scripted_effect` ne nomme jamais un `WA_AI_CONFIG_*` directement. Il nomme un trigger de
> décision, qui lui-même lit CONFIG.

Cette règle-là fait tout le travail que « point d'entrée unique » essayait de faire, et elle est
vérifiable par grep. **MEASURED** : aujourd'hui `common/ai_strategy` lit **54 triggers CONFIG
directement** — 54 violations de cette règle.

*(Exception à garder : le scoping par tag d'un fichier de couche Country, `allowed = { tag = GER }`,
n'est pas une lecture de config, c'est l'adressage du fichier.)*

---

## 4. Défaut 3 — ta couche 2 fait deux métiers, et c'est ce qui produit les fichiers de 3600 lignes

« Assembler les éléments de config en portes logiques » décrit **un** métier. Mais l'IA doit aussi
**observer le monde vivant** : suis-je en guerre, le front s'effondre-t-il, qui tient Tobrouk,
l'Italie est-elle entrée. Ce n'est pas de l'assemblage de config — aucune valeur déclarée ne
répond à ces questions.

**MEASURED** : `WA_AI_MILITARY_triggers.txt` fait **3613 lignes / 175 triggers**, et sa majorité
est de l'observation du monde, pas de l'assemblage de CONFIG. C'est le symptôme : quand une couche
a deux métiers, elle grossit sans borne parce que rien ne dit où s'arrêter.

**MEASURED** — profondeur actuelle des chaînes de triggers `WA_AI_*` (1 = feuille) :

| Profondeur | Triggers |
| --- | --- |
| 1 | 473 |
| 2 | 198 |
| 3 | 98 |
| 4 | 106 |
| 5 | 45 |
| 6 | 24 |
| 7 | 1 |
| 8 | 1 |

Les plus profonds : `WA_AI_can_upgrade_economy_law` (8), `WA_AI_can_take_low_economic_mobilisation`
(7). Un modèle en couches **borne** cette profondeur par construction ; l'absence de modèle
produit des chaînes de 8.

---

## 5. Contre-proposition : 4 couches, frontière définie par une question

| # | Couche | Question à laquelle elle répond | Nommage | Lit |
| --- | --- | --- | --- | --- |
| 1 | **DÉCLARATION** | « Quelle est la valeur ? » | `WA_AI_CONFIG_*` + `constant:wa_ai_*` | **rien** |
| 2 | **OBSERVATION** | « Qu'est-ce qui est vrai dans le monde, maintenant ? » | `WA_AI_<SYS>_is_*` / `_has_*` | couche 1 |
| 3 | **DÉCISION** | « Faut-il agir ? » | `WA_AI_<SYS>_should_*` / `_can_*` | couches 1 + 2 |
| 4 | **CONSOMMATION** | `ai_strategy`, `effects`, `events` | — | **couche 3 seulement** |

Trois propriétés que ce modèle a et que le tien à 3 couches n'a pas :

1. **La frontière 1/2 est testable** (§2) : « lit-il quelque chose qui bouge tout seul ? »
2. **La frontière 2/3 est testable** : une observation est vraie ou fausse indépendamment de ce
   qu'on veut en faire ; une décision embarque une intention. Si un trigger a deux consommateurs
   qui en veulent des choses opposées, c'est une observation, pas une décision.
3. **La frontière 3/4 est vérifiable par le nom seul** : la couche 4 ne peut nommer que des
   `_should_*` / `_can_*`. Un checker le vérifie par grep, sans parser.

C'est le point clé : **le préfixe porte la couche**, donc l'invariant se vérifie sans comprendre
le code. C'est ce qui manque aujourd'hui et c'est ce qui coûte le moins cher à adopter.

### Profondeur bornée

Le modèle plafonne à 4. Les deux chaînes à 7 et 8 sauts (système de lois) deviennent des défauts
détectables, pas des accidents invisibles.

---

## 6. Impact sur la base de code — chiffré et honnête

### 6.1 L'écart réel : la couche 4 ne consomme pas la couche 2/3, elle la réimplémente

**MEASURED** — les 2418 blocs `allowed` / `enable` des fichiers `common/ai_strategy/WA_AI_*` :

| Contenu du bloc | Blocs | Part |
| --- | --- | --- |
| 100 % triggers nommés `WA_AI_*` | 544 | 22 % |
| 100 % triggers moteur bruts (`date`, `has_war_with`, `num_of_*`, `controls_state`…) | 557 | 23 % |
| Mixte | 217 | 9 % |
| Triviaux (`always = yes`, scoping par tag) | 1100 | 46 % |

**3203 termes moteur bruts contre 1207 termes nommés.** Ta couche 4 est conforme à **22 %**.

C'est là qu'est le travail, pas dans CONFIG. Pires fichiers (**MEASURED**, blocs 100 % bruts) :

| Fichier | Blocs bruts | Mixtes | Nommés |
| --- | --- | --- | --- |
| `WA_AI_MILITARY_COUNTRY_SOV_FRONT.txt` | 37 | 0 | 0 |
| `WA_AI_MILITARY_COUNTRY_GER_FRONT.txt` | 31 | 5 | 2 |
| `WA_AI_MILITARY_COUNTRY_JAP_FRONT.txt` | 25 | 0 | 0 |
| `WA_AI_MILITARY_COUNTRY_ITA_DIPLOMACY.txt` | 24 | 1 | 1 |
| `WA_AI_NAVAL_DEFAULT.txt` | 20 | 0 | 0 |
| `WA_AI_NAVAL_COUNTRY_GER.txt` | 19 | 0 | 0 |

### 6.1 bis — Le modèle marche déjà : la production en est la preuve

Le chiffre global de 22 % masque une réalité beaucoup plus utile. **MEASURED**, même mesure
ventilée par système :

| Système | Fichiers | Blocs | Bruts | Mixtes | Nommés | Triviaux | **À convertir** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **PRODUCTION** | 51 | 708 | 13 | 2 | **273** | 420 | **15** |
| MILITARY | 113 | 1477 | 461 | 198 | 226 | 592 | **659** |
| NAVAL | 15 | 218 | 83 | 17 | 45 | 73 | **100** |
| RESEARCH + autres | 4 | 15 | 0 | 0 | 0 | 15 | 0 |

**Le système de production respecte déjà ton modèle à ~95 %** : 273 blocs 100 % nommés contre 15 à
convertir, sur 51 fichiers. Ses triggers `WA_AI_EQUIPMENT_can_absorb_<ressource>_shock_*` sont lus
**586 fois dans 32 fichiers** (**MEASURED**) — une définition, 586 sites qui en dépendent sans la
recopier.

C'est le résultat le plus important de cette analyse : **ta vision n'est pas une hypothèse, elle
est déjà implémentée et elle tient**, sur le système qui a le plus de fichiers. Ce qui reste à
faire n'est pas de prouver le modèle, c'est de l'étendre à MILITARY (659) et NAVAL (100) —
**774 blocs, dont 85 % dans un seul système**.

### 6.2 Volume du chantier

| Chantier | Volume **MEASURED** | Nature |
| --- | --- | --- |
| Blocs couche 4 à convertir | **774** (557 bruts + 217 mixtes) | mécanique, mais long |
| Triggers nommés à créer | **~250-400** *(DERIVED : 774 blocs, forte redondance entre fichiers d'un même système)* | conception, pas mécanique |
| Lectures directes CONFIG depuis `ai_strategy` à re-router | **54** | mécanique |
| Triggers CONFIG à sortir/scinder | **11** | mécanique |
| Blocs `allowed`/`enable` dupliqués ≥ 3× | 1429 blocs pour 869 formes distinctes | ~1019 blocs supprimables par nommage |

### 6.3 Simplification ou complexité ? Les deux, et pas pour les mêmes gens

**Simplification — pour le lecteur, et c'est le gros du bénéfice :**

- « Où je regarde ? » devient une réponse en 4 pas au lieu d'une recherche dans 183 fichiers
  `ai_strategy`.
- Le nombre total de lignes **baisse** : ~1019 blocs dupliqués remplacés par des références.
- La profondeur maximale passe de 8 à 4, bornée par construction.
- Un néophyte peut modifier un comportement en couche 1 sans lire le moteur — c'est exactement
  le retour « organisation complexe pour les néophytes ».

**Complexité — pour un type d'auteur précis, et il faut l'assumer :**

- Écrire une règle **ponctuelle** coûte plus cher. Aujourd'hui : 3 lignes de `date > 1942.1.1` dans
  le bloc. Demain : une constante en couche 1, un trigger d'observation en 2, un trigger de
  décision en 3, une référence en 4. **Quatre fichiers pour une règle.** C'est le prix, et il est
  réel.
- Le débogage devient indirect. `imgui show ai-strategy` dit *quel bloc est armé*, pas *quel maillon
  de la chaîne est faux*. **Mitigation obligatoire** : un harnais `WA_TEST_explain_<système>` par
  système, qui journalise le verdict de chaque couche pour un pays donné. Sans ça, la 4ᵉ couche
  rend le diagnostic plus dur qu'aujourd'hui, et ce serait une régression nette.

**Deux coûts que je ne peux pas chiffrer, et que je ne vais pas minimiser :**

- **`ai_strategy value =` ne peut appeler ni trigger ni `constant:`** (**MEASURED**, skill
  `wa-constants-registry`). Le modèle en couches couvre le **gating**, pas le **tuning**. Les
  nombres des `value =` restent littéraux, dans 183 fichiers. C'est un trou permanent du modèle,
  à documenter comme exception assumée, pas à masquer.
- **Performance : ASSUMED.** HOI4 réévalue les blocs `enable` fréquemment ; des chaînes de
  triggers plus profondes coûtent plus cher. Je n'ai aucune mesure, et le moteur est une boîte
  noire sur ce point. À mesurer avant de convertir les 774 blocs — un lot pilote sur un système,
  puis comparaison du temps de tick.

---

## 7. Une alternative que j'ai écartée, et pourquoi

**Découper CONFIG par système plutôt que par nature** : chaque système AI porte sa propre config
(`WA_AI_MILITARY_CONFIG.txt`, `WA_AI_TEMPLATES_CONFIG.txt`…).

Avantage réel : supprime le goulot du §3, chaque équipe touche sa config sans risque croisé.
Inconvénient qui l'emporte : les tags majeurs, les archétypes de doctrine et les dates de la
guerre sont **transverses par nature**. `is_major_country` est lu par 6 systèmes. Le découpage par
système forcerait soit une duplication (le mal qu'on soigne), soit un « CONFIG commun » — et on
retombe sur le modèle proposé, en ayant ajouté un niveau.

Je garde donc : **un namespace CONFIG unique, découpé en fichiers par nature (identités / fenêtres
/ drapeaux), plus la règle « la couche 4 ne lit jamais CONFIG »**. C'est cette dernière règle, pas
le découpage, qui supprime le goulot.

---

## 8. Ce que je recommande de faire, dans cet ordre

1. **Adopter la convention de nommage** (`_is_`/`_has_` = observation, `_should_`/`_can_` =
   décision). Coût nul, aucun code déplacé, et c'est ce qui rend tout le reste vérifiable.
2. **Poser les règles de checker** en mode cliquet, avec le compte actuel comme référence :
   `LAYER-4-READS-CONFIG` (54), `LAYER-4-RAW-GATE` (774), `DATE-LEAK` (430), `NUMBER-LEAK` (499),
   `CONFIG-LIVE` (11). On interdit d'aggraver, on n'exige pas de migrer.
3. **Finir PRODUCTION d'abord** : 15 blocs à convertir sur 708. C'est une demi-journée, et ça
   donne **un système 100 % conforme** qui sert de référence écrite pour tous les autres — et de
   fixture pour le checker.
4. **Pilote réel : `WA_AI_NAVAL_*`** — 100 blocs à convertir sur 15 fichiers, périmètre fermé, peu
   de lecteurs croisés. On y mesure le coût réel de conversion **et** le coût de performance,
   avant de s'engager sur les 659 de MILITARY.
5. **Un harnais `WA_TEST_explain_naval`** dans le même lot pilote. S'il ne rend pas le diagnostic
   plus facile qu'aujourd'hui, le modèle est à revoir avant d'aller plus loin.
6. **MILITARY en dernier**, système par système (`FRONT`, puis `INVASION`, `THEATRE`, `DIPLOMACY`,
   `GARRISON`), un commit par famille. 659 blocs = 85 % du chantier ; c'est aussi le code le plus
   load-bearing du mod, donc celui qui bénéficie le plus d'un pilote déjà validé.

---

## 9. Réponse directe à tes questions

| Question | Réponse |
| --- | --- |
| Ma vision est-elle la bonne ? | **Oui, et elle est déjà prouvée** : le système PRODUCTION la respecte à ~95 % sur 51 fichiers. Deux corrections seulement : 3 couches en fusionnent deux qui ont des métiers différents (observation / décision), et « point d'entrée unique » vise le mauvais invariant — le bon est « le consommateur ne lit jamais CONFIG ». |
| As-tu de meilleures idées ? | **4 couches**, frontières définies par des questions testables, et surtout **la couche portée par le préfixe du nom** — c'est ce qui rend l'invariant vérifiable par grep, sans parser et sans relecture. |
| Impacts sur la base de code ? | 774 blocs à convertir — **dont 659 dans MILITARY seul et 15 dans PRODUCTION**. Plus ~250-400 triggers à créer, 54 lectures CONFIG à re-router depuis `ai_strategy`, 11 triggers CONFIG à déplacer. Conformité couche 4 : 22 % global, **95 % en production**, 15 % en militaire. |
| Simplification ? | **Oui pour le lecteur** : −1019 blocs dupliqués, profondeur bornée à 4 au lieu de 8, chemin de lecture déterministe en 4 pas au lieu d'une recherche dans 183 fichiers. |
| Plus de complexité ? | **Oui pour l'auteur d'une règle ponctuelle** : 4 fichiers au lieu d'un bloc. Et le débogage devient indirect — le harnais `explain` n'est pas optionnel, c'est la condition pour que le modèle soit un gain net. Plus deux coûts non chiffrables : les `value =` restent hors modèle, et le coût de performance est **ASSUMED**. |
