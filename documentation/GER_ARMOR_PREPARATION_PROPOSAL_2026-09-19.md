# Proposition — blindés disponibles avant Barbarossa

**Mise à jour :** cette proposition préliminaire est remplacée par les constats et priorités de [l'analyse historique de la campagne 40995eb2](GER_ARMOR_HISTORY_40995eb2_2026-09-19.md). Les sauvegardes ont depuis été analysées ; conserver ce texte comme proposition initiale, pas comme dernier diagnostic.

Statut : INCOMPLETE DIAGNOSIS. Proposition de réglage, aucun changement de comportement.
Source de campagne : trois captures fournies par le propriétaire, datées novembre 1943 par celui-ci. Aucune sauvegarde analysée ; version de campagne non identifiée. Le code lu est le code de travail du 19 septembre 2026, pas une preuve de la version exécutée sur les captures.

## Diagnostic en six cases

| Case | Résultat |
| --- | --- |
| Symptôme | Rapport propriétaire : 12–13 divisions blindées en juin 1941, chute de production pendant Barbarossa, conversion moderne trop rapide et sept divisions encore classées légères. |
| Mesure | **MEASURED** — Capture 1, lecture visuelle : 249 divisions actives, 333 souhaitées ; légères 7/0, moyennes 18/83, infanterie 185/216, montagne 14/33 (présentes/souhaitées). Les quatre lignes présentes totalisent 224, pas 249 : ne pas les présenter comme un inventaire exhaustif. Aucun relevé de juin 1941. |
| État du mod | Inconnu dans cette campagne : stocks, usines affectées/demandées, drapeaux de modèles et version exécutée. Les captures ne les donnent pas. |
| Décision du mod | Inconnue dans cette campagne. **MEASURED** — Le code actuel déclenche le verrou moderne sur autorisation des moyens, technologie moderne et autorisation mécanisée, sans test de stock dans ce verrou. |
| Ligne causale | Non établie pour cette campagne. Candidats lus : `common/scripted_effects/WA_AI_TEMPLATES_effects.txt:446`, `common/script_constants/wa_ai_production.txt:39`, `common/ai_strategy/WA_AI_PRODUCTION_DEFAULT_tanks.txt:317`, `common/ai_templates/WA_AI_TEMPLATES_armored_light.txt:1015`. |
| Frontière moteur | **ASSUMED** — Arbitrage entre demandes industrielles et attribution du rôle après conversion. Une composition contenant des moyens ne prouve pas à elle seule que le moteur doit déjà reclasser la division. |

## Hypothèses concurrentes et mesures discriminantes

| Hypothèse | Mesure qui la réfuterait |
| --- | --- |
| **ASSUMED** — Objectif blindé trop faible avant 1941. | Objectif déjà très supérieur au nombre présent et à la file de formation en 1939–1941. La capture 1943 ne répond pas à cette question. |
| **ASSUMED** — Usines retirées aux chars au profit des remplacements d'infanterie. | Affectation industrielle blindée stable sur juin–décembre 1941 ; il faudrait alors examiner pertes, efficacité, ressources et changements de lignes. |
| **ASSUMED** — Conversion moderne sans matériel suffisant. | Stocks couvrant effectivement les besoins supplémentaires de la conversion, accompagnés d'un bon équipement des unités avant et après. |
| **ASSUMED** — Le passage léger → moyen reste bloqué par un écart de composition. | Composition finale correspondante atteinte et rôle correctement réattribué dans la sauvegarde ; le problème se déplacerait vers la lecture de l'interface ou une autre étape. |

## Changements proposés, dans l'ordre

1. Définir la réussite par des divisions équipées : cible de travail de 25 divisions blindées en juin 1941, avec au moins 90 % de dotation dans chaque famille critique. Seuil proposé, pas résultat démontré. Compter séparément légères en transition, moyennes et modernes ; publier aussi le total équipé pour éviter un succès seulement nominal.
2. Financer la préparation avant la guerre majeure : si les demandes dépassent déjà largement les réalisations, traiter l'allocation industrielle avant de relever les objectifs. Protéger une enveloppe blindée adaptée à l'industrie et aux besoins restants, avec sortie sur stocks suffisants et exception en crise d'équipement générale. Inclure les composants nécessaires aux divisions, pas seulement les châssis.
3. Ajuster ensuite l'objectif précoce des pays orientés vers une armée blindée, si le relevé 1939–1941 le justifie. **MEASURED** — La rampe actuelle est 5/10/15/20/25, de l'avant-1939 à 1942. Ne pas imposer 25 divisions à chaque pays ni conditionner toute la politique à une guerre GER–SOV historique.
4. Séparer ouverture de production moderne et conversion des divisions. Préparer une réserve, puis autoriser des étapes dont le besoin matériel supplémentaire peut être couvert. **MEASURED** — Les incitations modernes actuelles suivent le verrou de modèle (`WA_AI_TEMPLATES_triggers.txt:324`). **DERIVED** — Ajouter seulement un seuil de stock au verrou, sans voie de production préalable, exposerait le système à une attente circulaire. La possibilité de convertir des lots de divisions doit être vérifiée avant de la promettre ; une transition par compositions intermédiaires est une autre option.
5. Vérifier la fin de conversion des sept légères : étape active, composition cible, correspondance avec le moyen courant, classement observé. **MEASURED** — Le fichier léger contient une étape finale avec des bataillons moyens tout en restant dans le groupe léger. **ASSUMED** — Sa réattribution par le moteur échoue dans la campagne montrée. Corriger le registre/générateur uniquement après localisation du blocage.

## Vérification et risques

| Point | Exigence proposée |
| --- | --- |
| Série minimale | Même campagne : début 1940, juin 1941, septembre 1941, décembre 1941 ; plus novembre 1943 pour les conversions. Vérifier la version exécutée. |
| Mesures | Divisions présentes/souhaitées/en formation par rôle ; dotation par équipement ; stocks ; usines affectées et demandées ; sorties et pertes de matériel quand disponibles ; composition et rôle des sept anciennes légères. |
| Succès pré-guerre | 25 divisions blindées réellement équipées, sans déficit critique de l'infanterie. |
| Succès pendant la guerre | Comparaison avec une campagne témoin : production blindée soutenue, dotation des formations et pertes examinées ensemble. Ne pas confondre recul d'une production avec hausse des pertes. |
| Modernisation | Pas de déficit créé durablement par une conversion que l'industrie ne peut financer ; capacité de remplacer les pertes conservée. |
| Risques | Une enveloppe trop rigide peut affamer l'infanterie ; un objectif trop haut peut gonfler les files ; un seuil de conversion sans production préalable peut empêcher toute modernisation ; un reclassement mal ciblé peut toucher d'autres pays. |

Avant modification : analyse des appelants, revue des leçons et revue d'architecture selon AGENTS.md, puis tests du système et essai console propriétaire. Aucun sujet ajouté à WORK.md à ce stade de proposition.
