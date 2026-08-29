# Audit WA_AI — couches et configuration (2026-08-29)

Matériel source de `documentation/WA_AI_LAYERS_REFACTOR_PROPOSAL.md`.
Archivé pour que la proposition soit auditable **sans dépendre de la session qui l'a produite**.

Base : branche `ai-rework`, HEAD `c339245b5`, moteur 1.19.2.0.
Base de référence des checkers à cette date : `check_constants.py` 0 erreur / 0 warning,
`check_worklist.py` 0 ERROR / 0 WARN, `check_skill_refs.py` 0 référence morte.

---

## Les deux rapports

| Fichier | Contenu |
| --- | --- |
| `AUDIT_WA_AI_CONFIG.md` | Audit de `common/scripted_triggers/WA_AI_CONFIG.txt` (1566 lignes, 144 triggers) et de tous ses sites de lecture. Code mort, tables de classification concurrentes, collisions de noms, données hors couche, et 8 « cas étranges » dont deux inconnues moteur. |
| `ARCHI_COUCHES_WA_AI.md` | Évaluation du modèle en couches proposé par l'owner, contre-proposition à 4 couches, et chiffrage de l'écart par système. |

`config_usage.tsv` : le recensement complet, un trigger CONFIG par ligne, avec son nombre de
lectures externes, son nombre de fichiers lecteurs et la liste de ces fichiers.

---

## Les scripts

Tous sont **autonomes** (stdlib seule) et **portables** : ils dérivent la racine du dépôt de leur
propre emplacement (`documentation/archive/<ce dossier>/` → trois niveaux au-dessus). Ils
s'exécutent depuis n'importe quel répertoire :

```bash
python documentation/archive/ai_layers_audit_2026-08-29/audit_pilot.py
```

Tous sont **en lecture seule** sauf `audit2.py`, qui écrit `config_usage.tsv` à côté de lui.

| Script | Mesure | Résultat au 2026-08-29 |
| --- | --- | --- |
| `audit2.py` | Recensement des lectures de chaque trigger CONFIG sur tout le dépôt. Écrit `config_usage.tsv`. | 144 triggers, **15 jamais lus hors CONFIG** |
| `audit3.py` | Classification des corps de triggers CONFIG (taxonomie initiale : tag pur / constante / alias / mixte / état) | 81 tag pur, 22 constantes, 4 alias, 30 mixtes ou état |
| `audit4.py` | Agrégats de lecteurs : par dossier, par fichier, triggers les plus lus | `scripted_triggers` 147, `ai_strategy` 54, `country_leader` 11 |
| `audit5.py` | Portes par tag dans `allowed`/`enable` de `common/ai_strategy` (détecteur large) | vue brute, affinée par `audit6.py` |
| `audit6.py` | Idem, affiné : pseudo-scopes (`ROOT`/`PREV`/`FROM`…) et scopes imbriqués exclus, couche Country exclue | **55** portes par tag hors couche Country |
| `audit7.py` | Triggers CONFIG dont les corps sont byte-identiques | 13 groupes, dont 3 intentionnels documentés |
| `audit8.py` | Reclassification sous la règle de l'owner (CONFIG = tags + nombres + dates) | **102 déclarations pures, 22 drapeaux, 9 compositions, 7 mixtes, 4 verdicts** |
| `audit_dupes.py` | Définitions dupliquées (même nom, deux endroits) + familles de nommage | 2 duplicatas réels, 9 familles de préfixes dans CONFIG |
| `audit_ifor.py` | `if = { }` imbriqué directement dans `OR = { }` — risque de vrai-vacuant | **3** occurrences |
| `audit_not.py` | Blocs `NOT` à ≥ 2 enfants directs — NAND vs NOR | **71** occurrences |
| `audit_numbers.py` | Dates littérales et seuils numériques hors couche 1 | **430 dates, 499 seuils** ; CONFIG en porte 12 et 5 |
| `audit_patterns.py` | Blocs `allowed`/`enable` identiques répétés | 1429 blocs pour 869 formes ; ~1019 supprimables par nommage |
| `audit_layers.py` | Discipline de la couche 4 + profondeur des chaînes de triggers | 22 % de blocs 100 % nommés ; profondeur max **8** |
| `audit_pilot.py` | Idem ventilé **par système** — le chiffre qui a décidé du plan | PRODUCTION 15 à convertir, NAVAL 100, MILITARY **659** |
| `revue_reverify.py` | **Ajouté par la revue adversariale** (`documentation/REVUE_LAYERS_REFACTOR.md`) : re-dérivation indépendante des chiffres porteurs, tokeniseur propre, écrit depuis les affirmations et non depuis les scripts ci-dessus | census identique (2418/557/217/544/1100) ; corrige 586→293, 430→418, 499→494, 54 paires vs 155 occurrences |

---

## Limites de méthode — à lire avant de citer un chiffre

- **Détection par expression régulière, pas par parseur PDXScript.** Les scripts comptent des
  motifs textuels avec un suivi de pile d'accolades. Ils sont fiables sur du script bien indenté
  et peuvent se tromper sur des constructions exotiques. **Tout chiffre porteur doit être
  re-dérivé indépendamment avant d'engager du travail dessus.**
- **Les commentaires sont retirés** (`re.sub(r'#.*', '', s)`) avant comptage, mais un `#` à
  l'intérieur d'une chaîne de localisation serait mal traité. Aucun cas connu dans les fichiers
  balayés.
- **Périmètre du balayage** : `common/` et `events/`, plus `history/` pour `audit2.py`.
  `tests/`, `documentation/` et `.claude/` sont exclus. Un trigger cité uniquement dans un bundle
  de test ou dans un skill est donc compté comme mort par `audit2.py` — **re-grep obligatoire
  avant toute suppression**, `localisation/`, `tools/` et `tests/` inclus.
- **`audit_pilot.py` et `audit_layers.py`** classent un bloc « brut » dès qu'il contient un terme
  moteur de la liste `RAW` et aucun `WA_AI_*`. Cette liste est explicite dans le script et n'est
  pas exhaustive : le compte de 774 est un **plancher**, pas un total.
- Les scripts ne mesurent **rien du comportement du moteur**. Les deux inconnues moteur
  (`if` dans `OR`, `NOT` multi-enfants) restent **ASSUMED** jusqu'à la mesure console —
  harnais `common/scripted_effects/WA_TEST_pdx_semantics.txt`.
