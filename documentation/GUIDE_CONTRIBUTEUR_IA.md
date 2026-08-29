# Guide du contributeur IA — World Ablaze

Pour toi qui n'as jamais ouvert un `.txt` PDXScript et veux changer un comportement de l'IA.
Tout est en français ; les noms de code restent en anglais. Référence complète du modèle :
`documentation/WA_AI_LAYERS.md`.

## 1. « Je veux changer un comportement — où je vais ? »

```
Tu veux changer QUOI ?

├─ Une VALEUR (un pays de plus dans une liste, une date, un seuil)
│    → couche 1 : common/scripted_triggers/WA_AI_CONFIG.txt (identités, listes de pays)
│                 common/scripted_triggers/WA_AI_CONFIG_FLAGS.txt (interrupteurs oui/non)
│                 common/script_constants/wa_ai_<système>.txt (nombres partagés)
│    → tu n'as RIEN d'autre à toucher. C'est le cas le plus fréquent.
│
├─ CE QUE L'IA CONSIDÈRE COMME VRAI (« le front est en danger »)
│    → couche 2 : common/scripted_triggers/WA_AI_<SYSTÈME>_*.txt, nom en _is_ / _has_
│
├─ QUAND L'IA AGIT (« attaquer si… »)
│    → couche 3 : mêmes fichiers, nom en _should_ / _can_
│      (les gates des stratégies vivent dans WA_AI_<SYS>_*gate_triggers.txt / WA_AI_NAVAL_triggers.txt)
│
└─ CE QUE L'IA FAIT (un ordre nouveau, un bâtiment, une stratégie)
     → couche 4 : common/ai_strategy/, events/, common/scripted_effects/
     → et là, tu ne mets JAMAIS de date, de tag ni de seuil dans le bloc :
       tu appelles un trigger _should_. Le checker te le rappellera.
```

## 2. Les 6 règles qui te font tout casser sans message d'erreur

Le mod ne dit jamais qu'il s'est trompé. Celles-ci sont mesurées, pas théoriques :

1. **Pas de BOM.** Un fichier `scripted_effects` / `scripted_triggers` sauvé avec un BOM UTF-8
   ne se charge pas **du tout**, silencieusement. Un système entier a disparu comme ça.
   (Vérifie : les trois premiers octets ne doivent pas être `EF BB BF`.)
2. **Un tag ne va jamais ailleurs qu'en couche 1** (exception : `allowed = { tag = X }` d'un
   fichier Country, qui est une adresse, pas une règle). Si tu écris `tag = GER` dans un
   `ai_strategy`, le jour où la partie diverge de l'histoire, l'IA n'a **aucun** comportement.
3. **Une date ne va jamais dans un script constant.** `date > constant:...` est silencieusement
   **toujours vrai** (mesuré). Une date partagée = un trigger CONFIG nommé.
4. **Ne compare jamais `difficulty` à un nombre hors de CONFIG.** L'ordre des valeurs n'est pas
   l'ordre des boutons (voir la table `[difficulty-mapping]` en tête de `WA_AI_CONFIG.txt`) :
   `difficulty > 1` ne veut PAS dire « normal ou plus dur ». Utilise `WA_AI_DIFFICULTY_*` /
   `WA_AI_CONFIG_cheats_enabled`.
5. **Un `if` dans un `OR` ne restreint rien** : à `limit` faux il vaut VRAI et satisfait tout
   l'OR (mesuré). Écris un membre `AND = { condition résultat }` à la place.
6. **`always = no` ne veut pas dire « désactivé proprement ».** Un interrupteur éteint dont les
   branches consommatrices restent en place laisse du code mort que tout le monde relira.

## 3. Ton premier changement, pas à pas

*Exemple réel : donner les brigades antichar à un pays de plus.*

1. Ouvre `common/scripted_triggers/WA_AI_CONFIG.txt`, trouve
   `WA_AI_CONFIG_DIVISIONS_use_anti_tank_brigades`.
2. La règle actuelle est « les 7 majeurs, ou plus de 8 usines militaires ». Si ton pays doit y
   entrer par identité, ajoute `original_tag = XXX` dans le `OR`. C'est TOUT : aucun autre
   fichier, les lecteurs passent tous par ce nom.
3. Vérifie :

```bash
python tools/check_ai_layers.py
```

```bash
python tools/check_constants.py
```

   Les deux doivent finir à 0 erreur. Si le premier râle, tu as mis la donnée au mauvais étage.

## 4. Ce qui doit être mesuré, jamais supposé

Trois étiquettes pour toute affirmation : **MEASURED** (lu dans un fichier ou une sortie de
jeu — nomme la source), **DERIVED** (calculé depuis un MEASURED), **ASSUMED** (pas vérifié).
La phrase à retenir : *le moteur est une boîte noire — ce que tu n'as pas lu dans un fichier,
tu ne le sais pas.* Et la première hypothèse sur un mauvais comportement de l'IA dans ce dépôt
est habituellement fausse : **diagnostique avant de corriger** — lance l'`explain` du système
(`tag <pays>` puis `event wa_explain_naval.1` en console, puis
`python tools/read_harness_log.py --marker "EXPLAIN NAVAL" --interpret naval`).

## 5. Les commandes

Exit 0 partout avant de proposer un changement :

```bash
python tools/check_ai_layers.py
```
attrape : donnée au mauvais étage, gate brut, date/`difficulty` hors couche 1, trigger CONFIG mort.

```bash
python tools/check_constants.py
```
attrape : un nombre décliné en deux copies qui divergent, un `@` partagé entre deux fichiers.

```bash
python tools/check_worklist.py
```
attrape : WORK.md malade, harnais sans en-tête de contrat, BOM dans un script.

```bash
python tools/check_skill_refs.py
```
attrape : une doc/skill qui cite un fichier qui n'existe plus.

## 6. Où demander

`WORK.md` est le registre des sujets ouverts (un sujet = un comportement voulu, avec son critère
de fermeture — un sujet sans critère est un souhait, pas une tâche). Les skills `.claude/skills/`
portent le savoir de travail ; commence par `wa-orientation`.
