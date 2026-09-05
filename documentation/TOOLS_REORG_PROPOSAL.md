# Proposition de réorganisation de `tools/`

Date : 2026-09-05. Statut : APPLIQUÉ le 2026-09-05 (§3 est la structure en place ; `tools/README.md` en est l’index court).
Demande du propriétaire : séparer les scripts d'usage très régulier des scripts à usage unique ou limité.

## 1. Mesure : qui sert à quoi, et à quelle fréquence

Deux signaux, tous deux **MEASURED** :

- **Commits** touchant le fichier depuis 2026-03-01 (`git log --since=2026-03-01`) et date du dernier commit.
- **Citations** dans `AGENTS.md`, `.claude/` (skills + agents) : ce que chaque session lit et exécute.
  La colonne « docs » compte en plus `documentation/` et `WORK.md`.

| Fichier / dossier | Commits | Dernier | Cit. AGENTS+.claude | Cit. docs | Rôle |
| --- | ---: | --- | ---: | ---: | --- |
| `check_constants.py` + `constants_registry.json` | 2 + 31 | 2026-09-05 | 26 + 17 | 35 + 23 | Porte pré-commit (matrice de validation AGENTS.md) |
| `check_ai_layers.py` + `ai_layers_baseline.json` | 2 + 22 | 2026-09-04 | 7 + 4 | 17 + 8 | Porte pré-commit (ratchet) |
| `check_worklist.py` + `check_worklist_selftest.py` | 12 + 5 | 2026-08-23 | 8 | 15 | Porte pré-commit + pré-scoring campagne |
| `check_ai_equipment_names.py` | 2 | 2026-09-04 | 2 | 7 | Porte pré-commit (`ai_equipment/`) |
| `check_engine_docs.py` + `engine_docs_manifest.json` | 2 + 3 | 2026-08-18 | 2 + 3 | 2 + 3 | Porte pré-commit (docs moteur) |
| `check_skill_refs.py` | 1 | 2026-08-20 | 1 | 4 | Porte pré-commit (`.claude/`, AGENTS.md) |
| `check_templates.py` | 1 | 2026-08-29 | 0 | 3 | Contrôle chaîne templates (silencieux en jeu) |
| `military_economy_audit.py` | 5 | 2026-08-18 | 0 | 3 | Lint report-only `ai_strategy/` |
| `read_harness_log.py` | 2 | 2026-08-29 | 2 | 11 | Lecture harness console après chaque test propriétaire |
| `triage_error_log.py` | 1 | 2026-08-18 | 0 | 1 | Triage `error.log` après chaque boot |
| `run_generators.py` + `map_generators/` + `core/` | 0 + 1 + 0 | 2026-08-27 | 4 | 5 + 5 + 1 | Régénération données carte (quand la carte change) |
| `gen_rail_corridors.py` | 5 | 2026-08-27 | 2 | 2 | Générateur (quand les corridors changent) |
| `gen_ai_medium_modern_mirror.py` | 3 | 2026-09-04 | 1 | 5 | Générateur (quand l'échelle medium change) |
| `gen_ai_faction_theaters.py` | 1 | 2026-08-18 | 3 | 4 | Générateur (`--dry-run` d'abord) |
| `gen_ai_landing_reservations.py` | 1 | 2026-08-23 | 1 | 2 | Générateur (`--dry-run` d'abord) |
| `equipment_evaluator/` (package + 2 tests pytest) | 6 | 2026-09-04 | 0 | 12 | Évaluateur équipement, projet SUSPENDU côté généralisation |
| `ai_will_do_replacer_all.py` + 8 parsers + `ai_replacer_base/` + `REFACTORING_SUMMARY.md` | 12 au total | 2026-08-28 | 5 + 3 | 7 + 5 + 4 | Pipeline de migration `ai_will_do` technos ; dernière exécution complète : logs de 2026-01-13 |
| `ai_will_do_replacer_prospecting.py` + `needs_aware_generator.py` + `prospecting_decision_analyzer.py` | 0 + 1 + 1 | 2026-08-16 | 3 + 2 + 2 | 3 + 2 + 2 | Pipeline de migration `ai_will_do` prospection |
| `collapse_fix_comments.py` + `fix_slug_map.json` + `fix_registry.json` | 1 + 1 + 19 | 2026-08-23 | 0 + 0 + 1 | 2 + 2 + 6 | Phase C du redesign 2026-08-23, APPLIQUÉE ; le script attend `fix_collapse_baseline.json` qui n'existe plus |
| `misc/` (2 scripts) | 0 | 2026-01-30 | 0 | 2 | Scripts uniques de janvier |
| `dlc_splitter/` | 0 | 2026-01-26 | 0 | 1 | Outil unique de janvier |
| `apply_output.log`, `full_run.log` | 0 | 2026-01-13 | 0 | 1 | Sorties d'exécution de janvier, versionnées par erreur |
| `__pycache__/`, `.pytest_cache/` | – | – | – | – | Caches, non versionnés, non ignorés explicitement |

Lecture de la table :

- **DERIVED** — trois niveaux d'usage se dégagent. *Porte* : lancé avant chaque commit ou chaque scoring de campagne. *Générateur* : lancé quand sa source change, quelques fois par mois. *Migration* : lancé une fois, gardé pour la traçabilité.
- **MEASURED** — les 8 fichiers `ai_will_do_replacer_*` n'ont pas produit de sortie depuis janvier (les deux logs) ; 3 d'entre eux (`_land`, `_armor`, `_infantry`) ont encore reçu des commits en août, donc le pipeline n'est pas mort, il est *peu utilisé*.
- **MEASURED** — `collapse_fix_comments.py` référence `tools/fix_collapse_baseline.json` (ligne 33) qui n'existe pas : le script n'est plus exécutable en l'état.

## 2. Couplages qui décident du coût d'un déplacement

Tous **MEASURED** (grep `__file__`, `sys.path`, imports) :

| Couplage | Effet si on déplace |
| --- | --- |
| Chaque `check_*.py`, `gen_*.py`, `military_economy_audit.py` calcule `REPO = parent.parent` | Un niveau de dossier en plus casse le chemin : passer à `parents[2]` dans chaque script déplacé |
| `check_constants.py`, `check_ai_layers.py`, `check_engine_docs.py` codent en dur `tools/<fichier>.json` | Ne pas déplacer ces JSON sans le script, et inversement |
| `run_generators.py` fait `sys.path.insert(parent)` puis `from map_generators import` ; `map_generators/*.py` font `sys.path.insert(parent.parent)` puis `from core import` | Déplacer `run_generators.py`, `map_generators/`, `core/` **ensemble** : la structure relative reste valide |
| `ai_will_do_replacer_all.py` importe `ai_will_do_replacer_{infantry,support,armor}` ; ceux-ci importent `ai_replacer_base` | Déplacer les 8 parsers + `ai_replacer_base/` **ensemble** |
| `ai_will_do_replacer_prospecting.py` fait `sys.path.insert(parent)` puis importe `needs_aware_generator`, `prospecting_decision_analyzer` | Déplacer le trio **ensemble** |
| `equipment_evaluator/__main__.py` : `DEFAULT_MOD_ROOT = parents[2]` ; ses tests aussi | Ne pas déplacer, c'est déjà un package autonome |
| `check_skill_refs.py` vérifie que tout chemin cité dans `.claude/skills`, `.claude/agents`, `AGENTS.md` existe | Filet de sécurité : toute citation oubliée dans ces fichiers fait échouer le checker. **Il ne couvre pas `documentation/` ni `WORK.md`** |

## 3. Proposition recommandée

Principe : **la racine de `tools/` = ce qu'une session lance sans réfléchir**. Tout le reste descend d'un niveau, rangé par fréquence.

```
tools/
├── check_constants.py            constants_registry.json        ┐
├── check_ai_layers.py            ai_layers_baseline.json        │
├── check_worklist.py             check_worklist_selftest.py     │ PORTES : inchangées,
├── check_ai_equipment_names.py                                  │ 0 citation à modifier
├── check_engine_docs.py          engine_docs_manifest.json      │ (61 citations AGENTS/.claude,
├── check_skill_refs.py                                          │  ~110 dans documentation/)
├── check_templates.py                                           │
├── military_economy_audit.py                                    │
├── read_harness_log.py                                          │
├── triage_error_log.py                                          ┘
├── README.md                     NOUVEAU : index par niveau (cette table, en 20 lignes)
│
├── gen/                          GÉNÉRATEURS : lancés quand leur source change
│   ├── run_generators.py  map_generators/  core/
│   ├── gen_rail_corridors.py
│   ├── gen_ai_medium_modern_mirror.py
│   ├── gen_ai_faction_theaters.py
│   └── gen_ai_landing_reservations.py
│
├── equipment_evaluator/          inchangé (package autonome, tests pytest)
│
├── migrations/                   PIPELINES DE MIGRATION : rejouables, rarement rejoués
│   ├── ai_will_do/               ai_will_do_replacer*.py (9), ai_replacer_base/, REFACTORING_SUMMARY.md
│   └── prospecting/              ai_will_do_replacer_prospecting.py, needs_aware_generator.py,
│                                 prospecting_decision_analyzer.py
│
└── archive/                      UNIQUE, DÉJÀ APPLIQUÉ : gardé pour la traçabilité, non maintenu
    ├── fix_tracking/             collapse_fix_comments.py, fix_slug_map.json, fix_registry.json
    ├── misc/                     ai_will_do_date_updater.py, delete_naval_cheat_events.py
    └── dlc_splitter/
```

Supprimés (git garde l'historique) : `apply_output.log`, `full_run.log`. Ajout à `.gitignore` : `__pycache__/`, `.pytest_cache/`, `tools/**/*.log`.

### Pourquoi ce découpage et pas un autre

- **Les portes restent à la racine** : ce sont les commandes de la matrice de validation d'AGENTS.md et des skills ; 61 citations dans les fichiers chargés à chaque session, aucune à toucher.
- **`gen/` est un vrai niveau intermédiaire**, pas de la migration : ces scripts se relancent à chaque changement de leur source (5 commits sur `gen_rail_corridors.py` en août). Les mettre dans `migrations/` mentirait sur leur cadence.
- **`migrations/` ≠ `archive/`** : un pipeline `ai_will_do` se rejoue quand un trigger `WA_AI_RESEARCH_*` change (AGENTS.md : « Preserve existing trigger logic when regenerating ») ; `collapse_fix_comments.py` ne se rejouera jamais et ne tourne d'ailleurs plus.
- **Rejeté : tout laisser à plat et n'ajouter qu'un README.** Les préfixes `check_` / `gen_` / `ai_will_do_` portent déjà une partie de l'information, mais 37 fichiers à la racine dont 14 morts ou dormants restent illisibles, et le README dériverait comme toute doc ici.
- **Rejeté : déplacer aussi les portes dans `checks/`.** Coût : réécrire 61 citations dans `.claude/` + AGENTS.md et ~110 dans `documentation/`, pour aucun gain de lisibilité (elles sont déjà groupées par le préfixe).

## 4. Coût de la migration recommandée

| Poste | Quantité | Comment |
| --- | ---: | --- |
| `git mv` | 4 groupes | Bloc ci-dessous |
| Corriger `REPO = parent.parent` → `parents[2]` | 11 scripts | `gen_rail_corridors.py`, `gen_ai_medium_modern_mirror.py`, `gen_ai_faction_theaters.py`, `gen_ai_landing_reservations.py`, `ai_will_do_replacer_all.py` et les 5 parsers avec `base_path` (`_armor`, `_infantry`, `_land`, `_naval`, `_support`) ; `_air_techs` fait `project_root = script_dir.parent` (ligne 598), même correction |
| Citations à réécrire dans `.claude/` + AGENTS.md | ~30 lignes | `sed` ; `python tools/check_skill_refs.py` prouve qu'il n'en reste aucune |
| Citations à réécrire dans `documentation/` + `WORK.md` | ~35 lignes | `sed` ; **pas de checker** : la liste `grep -rn 'tools/' documentation WORK.md` est la preuve |
| Doc à mettre à jour | 3 | AGENTS.md § Generated (chemins + « run from `tools/gen/` »), `wa-tooling/SKILL.md`, `wa-orientation/SKILL.md` |
| Vérification | 3 commandes | `python tools/check_skill_refs.py` ; `python tools/gen/run_generators.py all --dry-run` (depuis `tools/gen/`) ; `python -m pytest tools/equipment_evaluator` |

Non-régression : aucun de ces scripts n'est appelé par le jeu ni par un hook (`.claude/settings*.json` et `.claude/hooks` ne citent pas `tools/`, **MEASURED**). Le seul risque est une citation oubliée dans `documentation/`, qui ne casse rien à l'exécution.

### Bloc `git mv`

```bash
cd tools
mkdir -p gen migrations/ai_will_do migrations/prospecting archive/fix_tracking
git mv run_generators.py map_generators core gen_rail_corridors.py gen_ai_medium_modern_mirror.py gen_ai_faction_theaters.py gen_ai_landing_reservations.py gen/
git mv ai_will_do_replacer.py ai_will_do_replacer_all.py ai_will_do_replacer_air_techs.py ai_will_do_replacer_armor.py ai_will_do_replacer_industry_electronics.py ai_will_do_replacer_infantry.py ai_will_do_replacer_land.py ai_will_do_replacer_naval.py ai_will_do_replacer_support.py ai_replacer_base REFACTORING_SUMMARY.md migrations/ai_will_do/
git mv ai_will_do_replacer_prospecting.py needs_aware_generator.py prospecting_decision_analyzer.py migrations/prospecting/
git mv collapse_fix_comments.py fix_slug_map.json fix_registry.json archive/fix_tracking/
git mv misc dlc_splitter archive/
git rm apply_output.log full_run.log
```

## 5. Observations hors sujet, non traitées

- **MEASURED** — `documentation/WA_AI_RAILWAY_SYSTEM.md`, `WA_AI_LEND_LEASE_RELIEF_DESIGN.md`, `WORK.md` (ligne 1789) et le lessons-log citent 4 outils qui n'existent plus : `gen_ai_armor_conversion_finals.py`, `lend_lease_relief_generator.py`, `generate_railway_connections.py`, `generate_province_connections.py`. `check_skill_refs.py` ne scanne pas `documentation/`, donc personne ne le voit.
- **MEASURED** — `check_worklist.py` et `check_ai_layers.py` sont les seuls checkers avec self-test ; `check_constants.py` (26 citations) n'en a pas.
