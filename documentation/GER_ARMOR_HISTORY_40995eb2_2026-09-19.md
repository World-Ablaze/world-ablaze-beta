# Allemagne — historique des blindés, campagne 40995eb2

**Diagnostic causal incomplet ; symptômes et chronologie mesurés.** L'étude établit les écarts de formation, l'effondrement des usines demandées en 1941, la persistance des sept anciennes légères et la pénurie moderne. Elle ne reconstitue pas l'arbitrage interne qui ouvre les formations ou calcule les demandes d'usines.

## Provenance et limites

- **MEASURED** — Campagne `40995eb2-cdd5-4ebe-ae5c-a8c619611a49`, World Ablaze BETA LOCAL, moteur `Operation Postern v1.19.3.0.c01a (5f47)`, save_version 33. Installation locale : rawVersion 1.19.3.0. La référence 1.19.2 des instructions est dépassée pour ce test.
- **MEASURED** — 18 copies de janvier 1939 à février 1944 ; mai–décembre 1941 mensuel. Dates, noms et empreintes SHA256 dans `../.cache/ger_armor_20260919/frozen_manifest.json`. Les autosaves originales roulaient pendant l'analyse : seules les copies figées sont utilisées ici.
- **DERIVED** — Aucun conflit de date/session détecté dans la sélection ; cela ne prouve pas l'absence de branche dans les intervalles non observés.
- **ASSUMED** — Commit exact exécuté inconnu. Les codes de modèles 20xxx/24xxx mesurés montrent l'emploi du schéma généré ; ils n'identifient pas un commit unique.
- Trois agents gpt-5.6-sol ont effectué sélection, extraction et analyse. Leur limite d'utilisation a interrompu leurs conclusions ; le parent a repris leurs artefacts et complété les relevés de formation avec le lecteur du dépôt. Aucun script de jeu modifié.

## Résultats

### 1. Douze divisions en juin 1941 ; la file, pas seulement l'industrie

| Date | Divisions totales | Blindées par composition | Formations blindées instanciées | Formations d'infanterie instanciées | Total souhaité enregistré |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1939.01 | 75 | 4 | 1 | 9 | 93 |
| 1940.01 | 104 | 7 | 2 | 11 | 135 |
| 1941.01 | 137 | 11 | 2 | 0 | 132 |
| 1941.05 | 155 | 12 | 1 | 1 | 165 |
| 1941.06 | 169 | 12 | 1 | 0 | 161 |
| 1941.07 | 168 | 13 | 0 | 0 | 152 |
| 1941.08 | 170 | 13 | 0 | 0 | 190 |
| 1941.09 | 170 | 13 | 0 | 1 | 209 |
| 1941.10 | 175 | 13 | 1 | 1 | 222 |
| 1941.11 | 178 | 13 | 3 | 10 | 230 |
| 1941.12 | 179 | 13 | 3 | 11 | 240 |
| 1942.08 | 209 | 18 | 0 | 0 | 278 |
| 1943.01 | 226 | 21 | 6 | 10 | 314 |
| 1943.11 | 249 | 25 | 1 | 1 | 334 |

**MEASURED** — Entrées de divisions, instances de `deployment/military_deployment_conveyor/.../military_deployment` et `ai/num_wanted_divisions` des copies figées. **DERIVED** — Famille blindée classée à partir des bataillons par l'outil ; ce n'est pas le rôle IA. Une instance est comptée une fois, sans multiplier les répétitions futures d'une file. Les autres familles de formation sont exclues des deux colonnes de formation, pas du total déployé.

**MEASURED** — Au 1er juin 1941 : 1 105,5 châssis moyens en stock, 2 364 déployés, zéro demande de renfort enregistrée pour ces châssis dans les divisions déployées ; 2 831,75 mécanisés en stock ; une seule division moyenne en formation. Son champ `training` est 0,80877. Le stock des châssis moyens de soutien d'infanterie est zéro ; 444 sont déployés.

**DERIVED** — Un excédent de châssis moyens n'est pas treize divisions complètes : variantes, soutiens, hommes et équipement de formation doivent aussi être financés. Les données justifient d'examiner en premier le débit de formation et ses conditions, avant d'imposer davantage d'usines.

**MEASURED** — En juin, le total réel 169 dépasse le total souhaité enregistré 161 ; juillet 168 contre 152. **ASSUMED** — Ce dépassement peut inhiber de nouvelles formations malgré une composition insuffisamment blindée. Ce n'est pas un veto moteur démontré : en août, la cible remonte à 190 mais la file reste vide.

**MEASURED** — Les entrées sauvegardées de stratégie numérique `type=9` portent medium_armor=32 et infantry=113 en juin ; en novembre 1943, 84 et 217. **DERIVED** — Leur concordance avec les objectifs affichés (83/216 sur la capture, instant différent) suggère des objectifs par rôle, pas des pourcentages. Ne pas les appeler `role_ratio` : le numéro de type n'a pas été décodé avec certitude. La table brute est dans `division_training.json`.

### 2. La chute de 1941 touche les demandes d'usines

| Date | Usines blindées affectées / demandées | Usines d'infanterie affectées / demandées | Autre matériel terrestre affecté | Aviation affectée |
| --- | ---: | ---: | ---: | ---: |
| 1941.01 | 292 / 328 | 1 / 4 | 18 | 174 |
| 1941.05 | 216 / 221 | 32 / 94 | 37 | 212 |
| 1941.06 | 165 / 168 | 74 / 164 | 69 | 197 |
| 1941.07 | 109 / 113 | 127 / 200 | 101 | 164 |
| 1941.08 | 57 / 58 | 158 / 193 | 151 | 154 |
| 1941.09 | 32 / 33 | 182 / 182 | 162 | 142 |
| 1941.11 | 132 / 141 | 135 / 135 | 114 | 153 |
| 1941.12 | 128 / 134 | 105 / 105 | 120 | 178 |

**MEASURED** — Champs `active_factories` et `requested_factories` des lignes. **DERIVED** — Sommes par famille de l'outil : blindés comprend les familles classées armor, dont les véhicules blindés ; infanterie regroupe équipement ordinaire et lourd. Autre matériel terrestre inclut les mécanisés : ne pas les ajouter une seconde fois.

**DERIVED** — Mai–septembre : −85,2 % d'usines blindées affectées, mais aussi −85,1 % demandées. Presque toute la demande restante est servie. La question première est donc pourquoi cette demande baisse, pas pourquoi 221 usines demandées resteraient sans affectation.

**MEASURED** — Les stocks agrégés d'équipement d'infanterie valent 39 667 en mai, 15 273 en juin, 19 101 en juillet ; leurs demandes de renfort enregistrées sont respectivement 2, 112 et 710. Les demandes montent ensuite à 4 491 en août, 12 696 en septembre et 25 175 en octobre. Les stocks agrégés ne prouvent pas la disponibilité de chaque type ou variante.

**DERIVED** — La réallocation vers l'infanterie est réelle, mais son explication exclusive par les pertes de Barbarossa est insuffisante : la baisse est déjà visible avant juillet, avec une faible demande de renfort d'infanterie enregistrée. L'autre matériel terrestre prend aussi beaucoup de capacité. L'aviation diminue pendant cette période.

**MEASURED** — En août 1942, les blindés reçoivent 62 usines pour 203 demandées. **DERIVED** — Il existe aussi un problème d'affectation, mais ce relevé est distinct du mécanisme observé à l'été 1941.

**ASSUMED** — Pas de série certifiée de chars produits par jour : les champs bruts de ligne et les compteurs ne permettent pas ici d'établir cette mesure. Les chiffres ci-dessus portent sur les usines, pas sur un flux de production. Un delta de stock n'est jamais présenté comme production.

### 3. Les sept anciennes légères ont changé de composition

**MEASURED** — Identifiants suivis : 6, 7, 8, 19983, 27184, 28087, 32234. Les sept sont sur Light Tank template D en janvier 1940, Medium Tank template J dès mai 1941, puis Medium Tank template I en décembre 1942 et novembre 1943. En février 1944, six restent sur I, une passe sur A.

**MEASURED** — En novembre 1943, leur ligne comporte 6 bataillons moyens + 3 moyens de soutien d'infanterie + 1 léger + 5 mécanisés. La capture du propriétaire affiche encore sept divisions sous light_armor.

**DERIVED** — Le problème n'est pas sept divisions demeurées entièrement légères : ce sont les mêmes unités, presque entièrement converties, dont la composition garde un bataillon léger. **ASSUMED** — Que ce bataillon ou un seuil de correspondance explique le rôle restant léger doit être vérifié ; la causalité exacte de reclassement n'est pas sérialisée dans les artefacts employés.

### 4. Pénurie moderne confirmée

| Date | Châssis modernes en stock | Déployés | Demande de renfort enregistrée | Usines affectées |
| --- | ---: | ---: | ---: | ---: |
| 1943.11 | 0 | 12 | 1 161 | 81 |
| 1943.12 | 0 | 50 | 1 122 | 69 |
| 1944.02 | 0 | 260 | 913 | 148 |

**MEASURED** — Famille `modern_tank_chassis` dans les relevés figés. Ces demandes peuvent inclure des livraisons en transit : elles ne sont pas une mesure certifiée du déficit logistique instantané.

**MEASURED** — Neuf divisions portent un modèle moderne en novembre : huit avec 4 bataillons modernes, 3 moyens, 3 moyens de soutien et 5 mécanisés ; une avec 7 modernes, 3 canons automoteurs moyens et 5 mécanisés. Le drapeau autorisant le châssis moderne est daté du 1er avril 1943.

**DERIVED** — L'étiquette « moderne » masque un parc moderne très incomplet, et la pression de renfort persiste au moins sur novembre–février. **ASSUMED** — La durée exacte de six mois pour les mêmes divisions n'est pas établie : le drapeau d'avril n'est pas la date de leur conversion et les copies sélectionnées ne couvrent pas avril–octobre 1943.

## Six cases de diagnostic

| Case | Conclusion |
| --- | --- |
| Symptôme | **MEASURED** — 12 blindées juin 1941, usines demandées en chute, sept anciennes légères et pénurie moderne. |
| Mesure | **MEASURED** — Tables ci-dessus, copies figées, rapport et lecteur du dépôt ; commandes plus bas. |
| État du mod | **MEASURED** — Drapeaux de modèles, date du verrou moderne, stocks, formations et demandes industrielles extraits. |
| Décision | **ASSUMED** — Calcul moteur de l'ouverture d'une formation, de la demande d'usines et du reclassement non reconstitué. Pas de preuve d'un veto unique. |
| Ligne causale | Inconnue pour le refus de formation et le reclassement. **MEASURED** — Le verrou actuel `WA_AI_TEMPLATES_update_modern_chassis_latch`, `common/scripted_effects/WA_AI_TEMPLATES_effects.txt:446`, n'exige pas de réserve de matériel. Cela localise un levier, pas à lui seul la cause historique complète. |
| Frontière moteur | **ASSUMED** — Priorités et seuils internes non observés. La documentation de l'installation décrit les leviers, pas les décisions instantanées prises dans la campagne. |

## Proposition révisée

1. **Priorité : faire effectivement former davantage de blindés avant 1941.** Mesurer et tester les conditions d'ouverture des files : besoin total, composition, hommes disponibles et ensemble des équipements. Cible d'essai : 25 divisions équipées ; ne pas annoncer que 1 105 moyens en stock suffisent à la financer. Préparer cette capacité en 1939–1940, pas uniquement relever le souhait de juin 1941.
2. Rééquilibrer l'expansion d'infanterie et de blindés, sans bloquer les renforts d'infanterie pendant une crise. **ASSUMED** — Davantage de blindés avant guerre pourrait entretenir leur demande de matériel ; cela ne prouve pas que 25 empêcheraient l'effondrement.
3. Pour l'industrie, cibler le creux de demande confirmé. Ne pas imposer d'emblée un plancher permanent : des stocks anciens ou incompatibles peuvent masquer une pénurie précise ; un plancher trop large immobiliserait des usines sans produire les composants manquants. Le code actuel possède déjà un supplément GER de 35 (`common/ai_strategy/WA_AI_PRODUCTION_COUNTRY_GER.txt:34`), malgré un commentaire resté à 60 ; effet historique non attribuable sans version.
4. Distinguer ouverture de la ligne moderne et autorisation de convertir le parc. Préproduction et réserves par composants avant changement de modèle ; conversion progressive à valider avec les mécanismes réellement disponibles. Ne pas baisser globalement les conversions avant d'avoir protégé le passage des anciennes légères : les deux chemins partagent les réglages moteur.
5. Traiter la fin de conversion des sept anciennes légères, en comparant la composition finale du parcours léger à la cible moyenne/moderne active. Modifier le registre/générateur seulement après localisation du blocage.

**Risques à contrôler :** réserves d'infanterie insuffisantes, files blindées ouvertes sans tous leurs composants, modernisation définitivement bloquée par un seuil sans préproduction, régression des conversions légères, impact sur les autres pays. Aucun de ces changements n'est appliqué dans cette analyse.

## Reproduction

Artefacts dans `../.cache/ger_armor_20260919/` : `frozen_manifest.json`, `frozen_report.json`, `production.csv`, `armor_divisions.csv`, `template_flags.txt`, `plans_templates.txt`, `division_training.json`, `finish_analysis.py`.

```powershell
python -m tools.campaign_report build --saves .cache/ger_armor_20260919/saves --campaign 40995eb2 --output .cache/ger_armor_20260919/frozen_report.html --workers 4 --digest-tags GER
python .cache/ger_armor_20260919/finish_analysis.py
```

Le CSV de l'agent `armor_divisions.csv` inclut aussi des unités d'infanterie à cause d'un filtre large sur « tank » dans « anti_tank ». Ici seules les unités appartenant aux modèles blindés du rapport sont utilisées ; aucune somme brute de ce CSV n'est un effectif blindé. Le rapport provisoire `production.md` appelait à tort `role_ratio` les entrées numériques type 9 : utiliser la distinction explicitée ci-dessus.
