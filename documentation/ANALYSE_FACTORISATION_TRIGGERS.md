# Analyse de factorisation — gates, triggers scriptés, CONFIG (2026-08-30)

**MEASURED** sur 2505 triggers scriptés (`common/scripted_triggers/`, corps normalisés en
tokens, commentaires exclus), branche `ai-rework-layers-draft`. Analyse seulement — rien n'est
appliqué. Cinq axes ; chaque catégorie porte sa recommandation.

## Verdict d'ensemble

Oui, il y a de la vraie factorisation à faire, mais elle n'est pas uniforme :
**~96 triggers se récupèrent sans aucun jugement** (copies multi-domaines d'une même intention,
fusion sémantiquement vide), **~40-60 de plus sur arbitrage owner** (mêmes corps, intentions à
trancher), et **~8 observations partagées à extraire** (blocs longs répétés jusqu'à 8-11 fois).
À l'inverse, deux grosses familles qui *ressemblent* à des doublons doivent rester séparées :
les alias-API de la recherche (interface des `ai_will_do` générés) et les coïncidences de corps
à intentions différentes (la règle Q4).

## A. Copies multi-domaines d'une même intention — fusion sûre, mécanique

**MEASURED : 144 groupes de corps token-identiques ; 77 groupes dont tous les noms ne diffèrent
que par le domaine (`_diplomacy`/`_front`/`_theatre`/`_invasion`) = 96 définitions
récupérables**, plancher — le vrai chiffre est plus haut car des copies inter-systèmes
(MILITARY+NAVAL, ex. `gank_everyone`, `rcz_only_garrison` ×4, `torch` ×5) échappent au
détecteur de préfixe.

Origine : la phase 4 a converti 1:1 des blocs que le mod d'origine avait copiés-collés entre
ses fichiers de domaine. Exemples : `sov_war_with_germany` ×5, `winter_war` ×4 (+`_invasion_time`
×4), `husky_prep` ×4, `husky_fire` ×4, `fatherland` ×3, `fra_protect_the_homeland` ×3,
`eng_all_in` ×4, `war_against_ita_north_africa` ×4, `pacific_offensive` ×4-6.

**Recommandation : fusionner — un trigger par intention, les N gates le lisent.** Diff
sémantiquement vide (corps identiques prouvés), vérifiable machine comme la phase 4, et
l'`explain` y gagne (une ligne au lieu de quatre). Coût de re-séparation future trivial si un
domaine doit diverger. Le nom fusionné perd le suffixe de domaine.

## B. Mêmes corps, intentions différentes — arbitrage owner, pas de fusion aveugle

**67 groupes** restants. La règle Q4 (« un nom par intention ») dit de NE PAS fusionner sur la
seule identité du corps — ex. `is_in_faction_with = GER + has_war_with = SOV` porte 4 noms
(`ita_share_borders_with_ger_against_sov`, `invasions_are_pointless_if_at_war_with_the_soviets`,
…) : mêmes termes, questions différentes, tuning futur différent. **Garder.**

Quatre sous-familles méritent en revanche une fusion *de conception* (même question, noms
par cible) :

| Famille | Membres | Fusion proposée |
| --- | --- | --- |
| `ger_festung_{berlin,breslau,danzig,poznan,stettin}` | 5 corps = `surrender_progress > 0 + has_war_with = SOV` | UN `should_ger_hold_festungen` ; les 5 stratégies gardent leurs payloads |
| `{hun,rom,bul,fin}_help_germany_*` | 4 = `support_requested_by_germany + axis + guerre SOV` | UN `should_axis_minor_answer_german_support_request` |
| `country_owns_dont_defend_ally_borders_{HUN,RKA,RPO,…}` | 5 corps = la même liste `BUL HUN ITA RCZ ROM` | UN trigger ; la liste de tags devrait d'ailleurs descendre en CONFIG (c'est une classification) |
| `DOCTRINES_SELECT_*` (air ×11 + ×9, land ×3 + ×3) | 26 sélecteurs sur 4 corps « historique: oui / compétitif: méta » | fusion possible MAIS ces noms sont probablement l'API des `ai_will_do` de doctrines — à faire via l'outillage replacer, pas à la main |

## C. Alias purs (corps = un seul appel) — deux classes, ne pas confondre

**MEASURED : ~40 alias.**

- **À GARDER (API délibérée)** : les `WA_AI_RESEARCH_needs_*` → CONFIG/TEMPLATES/PRODUCTION
  (ex. `needs_light_armor` : **170 lectures dans `common/technologies/` générées**). C'est
  l'interface stable que le replacer `ai_will_do` cible ; un alias à 1 définition ne dérive
  pas. Idem `PRODUCTION_build_*` → `ground_is_enabled` (groupement lisible).
- **À COLLAPSER (candidats)** :
  - `WA_AI_MILITARY_is_allies_member` → `WA_AI_CONFIG_is_in_allies` : **85 lectures** — deux
    vocabulaires pour un même fait dans tout le dépôt. Collapse = gros diff mécanique, gain de
    vocabulaire réel. À faire en lot dédié.
  - `WA_AI_MILITARY_COUNTRY_owns_naval_{atlantic,pacific,home}_*` → alias 1:1 des CONFIG (×3).
  - `should_ast_protect_home_{diplomacy,invasion}` : DEUX triggers dont le corps est
    `WA_AI_CONFIG_before_1946` → un seul `should_ast_protect_home` (cas A d'ailleurs).
  - la double marche `build_* → ground_is_enabled → CONFIG_uses_default_ground_production` :
    une marche suffit.
  - `WA_AI_refinery_region_priority` → `WA_AI_region_priority` (1 saut sec).

## D. Observations partagées à extraire — les blocs longs répétés

Conjonctions multi-termes identiques répétées à travers des triggers **différents**
(**MEASURED**, hôtes distincts) :

| Bloc | Hôtes | Extraction proposée (couche 2) |
| --- | --- | --- |
| le pavé VIC/665/458 (Vichy tient ses colonies…) | ×8 | `WA_AI_MILITARY_vichy_africa_intact` — le plus gros gain lisibilité |
| le pavé SOV `secure_leningrad`/focus | ×8 | `WA_AI_MILITARY_sov_leningrad_push_committed` |
| `NOT{soviet_union_defeated} + GER={has_war_with=SOV}` | ×10 | `WA_AI_MILITARY_east_front_alive` — **vérifier le recouvrement avec `east_front_war_active` existant avant d'en créer un second** |
| `OR{has_war_with INS/MAL/PHI}` | ×12 | `WA_AI_MILITARY_at_war_in_southeast_asia` |
| `any_country={axis controls_state 1032}` / `…115` | ×8 + ×8 | `WA_AI_MILITARY_axis_holds_tripoli` / `_axis_holds_sicily` |
| `855={CONTROLLER={is_in_faction_with=ROOT}}` | ×11 | `WA_AI_MILITARY_holds_bohemia_anchor` (nommer après lecture du sens de 855) |
| `OR{has_war_with GER, has_war_with ITA}` | ×11 | `WA_AI_MILITARY_at_war_with_european_axis` |
| `has_navy_size = { size > 9 }` | ×20 (famille avoid_sea_region) | optionnel : `WA_AI_NAVAL_has_meaningful_fleet` |

Déjà bien factorisés (rien à faire) : `NOT{home_threatened}` ×19,
`NOT{early_game_army_expansion_override}` ×19, `NOT{pacific_offensive_ready}` ×9.

## E. Familles paramétriques — laisser en l'état

`avoid_sea_region_*` ×18, `NOR_has_*_convoys` ×6, `FROM_is_*er` ×6 : même forme, valeurs
différentes. PDXScript n'a pas de triggers paramétrés ; la régularité EST la lisibilité, et un
`meta_trigger` les rendrait illisibles et hors-gates. **Ne pas factoriser.**

## Ce que ça donnerait, chiffré

| Lot | Nature | Volume | Risque |
| --- | --- | --- | --- |
| A | fusion mécanique des copies multi-domaines | −96 défs (plancher), prouvable token-à-token | nul (corps identiques) |
| B (4 sous-familles) | fusion de conception | −12 défs + 1 liste de tags vers CONFIG | faible, décision owner |
| C | collapse d'alias (hors API RESEARCH) | −8 défs, ~95 lectures re-pointées | faible, mécanique |
| D | extraction de 6-8 observations | +8 défs, ~70 corps raccourcis | faible ; UN point à vérifier (recouvrement east_front) |
| E | rien | — | — |

Ordre suggéré si tu valides : A (mécanique, même harnais de vérification que la phase 4) →
C → D → B. Chaque lot un commit, cliquets mis à jour, l'explain NAVAL/MILITARY inchangé dans
sa forme.
