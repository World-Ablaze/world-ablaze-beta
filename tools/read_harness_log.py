#!/usr/bin/env python3
"""
read_harness_log.py - read a WA_TEST console harness straight out of HOI4's logs.

WHY THIS EXISTS. A HOI4 scripted effect can only WRITE (`log = "..."`). It cannot read a
file, so the "read it back" half of every console harness has always been the owner
copy-pasting out of logs/game.log by hand - which loses the error.log correlation, loses
which run was which, and is where a misread turns into a wrong conclusion.

    python tools/read_harness_log.py --list
    python tools/read_harness_log.py --marker "PDX TEST"
    python tools/read_harness_log.py --marker "PDX TEST" --interpret pdx_semantics
    python tools/read_harness_log.py --marker "TC TEST" --runs 3 --errors

WHAT IT DOES
  * finds the HOI4 user directory (logs/), or takes $HOI4_USERDIR / --logs
  * strips HOI4's doubled `[time][date][file:line]:` prefixes so the harness text reads
    as the harness author wrote it
  * extracts the LAST run of a marker by default (--runs N for more)
  * correlates logs/error.log over the same wall-clock window - a harness that read
    strangely because its file failed to parse is the single most common false reading,
    and error.log is where that shows
  * --interpret applies a harness-specific verdict table (see INTERPRETERS below)

WHAT IT CANNOT DO
  It reads what the game wrote. It cannot fire the event, cannot know whether you were
  `tag`-ed as the intended country, and cannot tell a stale run from a fresh one except by
  the in-game timestamp it prints. Check the date on the run before trusting it.

Stdlib only. Exit 0 on a clean read, 1 if the marker was never found (or the logs are
unreadable), 2 if --interpret ran and any shown run's context header says STOP. Without
--interpret the header is not parsed and a STOP run still exits 0.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# HOI4 writes its logs under the user directory, not the install.
DEFAULT_USERDIRS = [
    Path.home() / "Documents" / "Paradox Interactive" / "Hearts of Iron IV",
    Path.home() / "OneDrive" / "Documents" / "Paradox Interactive" / "Hearts of Iron IV",
    Path.home() / "Documents" / "Paradox Interactive" / "Hearts of Iron IV BETA",
]

# `[05:23:34][1941.05.05.15][effectbase.cpp:1799]: ` - and the engine nests it twice.
PREFIX = re.compile(r"^\s*\[(\d\d:\d\d:\d\d)\]\[([\d.]+)\]\[[^\]]+\]:\s?")


def find_logs(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if p.is_dir():
            return p
        sys.exit(f"--logs: not a directory: {p}")
    env = os.environ.get("HOI4_USERDIR")
    if env:
        p = Path(env) / "logs"
        if p.is_dir():
            return p
        sys.exit(f"$HOI4_USERDIR set but {p} is not a directory")
    for d in DEFAULT_USERDIRS:
        if (d / "logs").is_dir():
            return d / "logs"
    sys.exit("no HOI4 logs directory found - pass --logs or set $HOI4_USERDIR")


def strip_prefixes(line: str) -> tuple[str, str, str]:
    """Return (wall_clock, game_date, text) with every nested engine prefix removed."""
    wall = game = ""
    while True:
        m = PREFIX.match(line)
        if not m:
            break
        if not wall:
            wall, game = m.group(1), m.group(2)
        line = line[m.end():]
    return wall, game, line.rstrip("\n")


def read_lines(p: Path) -> list[str]:
    if not p.exists():
        return []
    # HOI4 logs are latin-1-ish; never let a stray byte kill the read.
    return p.read_text(encoding="utf-8", errors="replace").splitlines()


def extract_runs(lines: list[str], marker: str) -> list[list[tuple[str, str, str]]]:
    """A run = the marker line plus every following line until the harness's end rule.

    End rule, in order of preference: the closing `====` banner, the next marker, or a
    line that carries no harness indentation. Harnesses in this repo bracket their output
    with `====` banners (wa-testing contract), so the first rule is what normally fires.
    """
    parsed = [strip_prefixes(l) for l in lines]

    def is_banner(i: int) -> bool:
        t = parsed[i][2].strip()
        return bool(t) and set(t) == {"="}

    hits = [i for i, (_, _, t) in enumerate(parsed) if marker in t]
    # A harness legitimately repeats its own marker in a closing line ("---- end PDX TEST"),
    # so a marker hit is a run START only when the line above it is the opening banner.
    # Harnesses without banners fall back to "every hit is a start".
    starts = [i for i in hits if i > 0 and is_banner(i - 1)] or hits
    runs = []
    consumed = -1
    for s in starts:
        if s <= consumed:
            continue
        # walk back to the opening banner if the marker line is preceded by one
        begin = s
        if s > 0 and set(parsed[s - 1][2].strip()) == {"="} and parsed[s - 1][2].strip():
            begin = s - 1
        end = len(parsed)
        for j in range(s + 1, len(parsed)):
            t = parsed[j][2].strip()
            if t and set(t) == {"="}:
                end = j + 1
                break
            if j in starts:
                end = j
                break
        runs.append(parsed[begin:end])
        consumed = end - 1
    return runs


def errors_in_window(logdir: Path, wall_from: str, wall_to: str) -> list[str]:
    """Wall-clock window match. HH:MM:SS strings carry no date, so a run that crosses
    midnight has wall_from > wall_to - treat that as a wrapped window instead of an
    empty one, and say so in the output."""
    out = []
    wrapped = wall_from > wall_to
    for line in read_lines(logdir / "error.log"):
        wall, _, text = strip_prefixes(line)
        if not wall or not text.strip():
            continue
        hit = (wall >= wall_from or wall <= wall_to) if wrapped else (wall_from <= wall <= wall_to)
        if hit:
            out.append(f"[{wall}] {text}")
    if wrapped:
        out.insert(0, "(fenetre a cheval sur minuit - correlation par heure seule, "
                      "des erreurs d'une autre session peuvent s'y glisser)")
    return out


# --------------------------------------------------------------------------------------
# INTERPRETERS - a verdict table per harness. Each takes the run's text lines and returns
# a list of (label, verdict, detail). They read ONLY what the harness printed; they never
# infer. A control that fails makes the probe UNREADABLE, never "answered".
# --------------------------------------------------------------------------------------

def _nums(text: str) -> dict[str, int]:
    """`key=3` / `key = 3` pairs out of one harness line."""
    return {k: int(v) for k, v in re.findall(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*(-?\d+)", text)}


def interpret_pdx_semantics(lines: list[str]) -> list[tuple[str, str, str]]:
    v: list[tuple[str, str, str]] = []
    scope = q1 = q2 = q3c = q3d = None
    for t in lines:
        if "scope :" in t:
            scope = _nums(t)
        elif "Q1 if-in-OR" in t:
            q1 = _nums(t)
        elif "Q2 NOT-multi" in t:
            q2 = _nums(t)
        elif "Q3 controls" in t:
            q3c = _nums(t)
        elif "Q3 date-const" in t:
            q3d = _nums(t)

    if scope is None:
        return [("CONTEXTE", "ABSENT", "pas de ligne `scope :` - ce n'est pas un run de ce harnais")]
    ok = (scope.get("always") == 1 and scope.get("I-am-ROOT") == 1
          and scope.get("I-am-THIS") == 1 and scope.get("ROOT-scope-usable") == 1
          and scope.get("control-false") == 0)
    v.append(("CONTEXTE", "OK" if ok else "STOP",
              "1 1 1 1 0 attendu, lu " + " ".join(str(scope.get(k)) for k in
              ("always", "I-am-ROOT", "I-am-THIS", "ROOT-scope-usable", "control-false"))))
    if not ok:
        v.append(("TOUT LE RESTE", "NON MESURE", "en-tete de contexte invalide - rien en dessous n'est une mesure"))
        return v

    if q1 is None:
        v.append(("Q1 if-dans-OR", "ABSENT", "ligne Q1 non trouvee"))
    elif q1.get("pos-control") != 1 or q1.get("neg-control") != 0:
        v.append(("Q1 if-dans-OR", "ILLISIBLE",
                  f"controles invalides (pos={q1.get('pos-control')} attendu 1, neg={q1.get('neg-control')} attendu 0) - `if` ne fonctionne pas comme suppose dans un trigger"))
    elif q1.get("ANSWER") == 1:
        v.append(("Q1 if-dans-OR", "VRAI VACUANT",
                  "un `if` a limit faux vaut VRAI dans un OR -> WA_AI_CONFIG_DIVISIONS_use_armored_divisions est VRAI POUR TOUS LES PAYS en difficulte competitive (site MEASURED). Le site ai_strategy GER_FRONT:1429 reste ASSUMED (autre chemin d'appel), et le site pathfinding est garde par un else non mesure (q1e)."))
    elif q1.get("ANSWER") == 0:
        v.append(("Q1 if-dans-OR", "SAIN",
                  "un `if` a limit faux vaut FAUX dans un OR - les 2 sites se comportent comme ecrits"))
    else:
        v.append(("Q1 if-dans-OR", "ILLISIBLE", f"ANSWER={q1.get('ANSWER')}"))

    if q2 is None:
        v.append(("Q2 NOT multi-enfants", "ABSENT", "ligne Q2 non trouvee"))
    elif q2.get("all-false") != 1 or q2.get("all-true") != 0:
        v.append(("Q2 NOT multi-enfants", "ILLISIBLE",
                  f"controles invalides (all-false={q2.get('all-false')} attendu 1, all-true={q2.get('all-true')} attendu 0)"))
    elif q2.get("ANSWER") == 1:
        detail = "NAND : `NOT = {A B}` vaut NOT(A ET B). Une garde ecrite pour dire 'aucun de ceux-ci' se declenche des qu'UN SEUL est faux : elle ne garde rien. 71 sites a relire, dont 16 dans WA_AI_LAW_triggers.txt."
        if q2.get("three-children") not in (None, 1):
            detail += f" ATTENTION : la sonde a 3 enfants lit {q2.get('three-children')}, incoherent avec NAND - re-lancer."
        v.append(("Q2 NOT multi-enfants", "NAND - DEFAUT MAJEUR", detail))
    elif q2.get("ANSWER") == 0:
        detail = "NOR : `NOT = {A B}` vaut NOT(A OU B). Les 71 sites se lisent comme prevu, aucun defaut."
        if q2.get("three-children") not in (None, 0):
            detail += f" ATTENTION : la sonde a 3 enfants lit {q2.get('three-children')}, incoherent avec NOR - re-lancer."
        v.append(("Q2 NOT multi-enfants", "NOR - SAIN", detail))
    else:
        v.append(("Q2 NOT multi-enfants", "ILLISIBLE", f"ANSWER={q2.get('ANSWER')}"))

    if q3c is None or q3d is None:
        v.append(("Q3 date en constante", "ABSENT", "lignes Q3 non trouvees"))
    elif q3c.get("constant-resolves") != 7:
        v.append(("Q3 date en constante", "ILLISIBLE",
                  f"constant-resolves={q3c.get('constant-resolves')} au lieu de 7 - `constant:` n'atteint pas ce contexte, l'experience ne dit rien"))
    elif q3c.get("date-file-survived") != 3:
        v.append(("Q3 date en constante", "NON",
                  "le fichier de constantes contenant des dates n'a pas charge -> vehicule des 430 dates = trigger CONFIG nomme, pas une constante"))
    elif q3d.get("literal-past") != 1 or q3d.get("literal-future") != 0:
        v.append(("Q3 date en constante", "ILLISIBLE",
                  f"controles litteraux invalides (past={q3d.get('literal-past')} attendu 1, future={q3d.get('literal-future')} attendu 0)"))
    else:
        pair = (q3d.get("past"), q3d.get("future"))
        table = {
            (1, 0): ("OUI", "les dates peuvent vivre dans un script constant - vehicule = constante nommee"),
            (1, 1): ("SILENCIEUSEMENT PERMISSIF - NE JAMAIS LIVRER",
                     "la constante ne resout pas et `date >` est toujours vrai. C'est le pire resultat possible : un gate qui ne garde rien sans le dire. Vehicule = trigger CONFIG nomme."),
            (0, 0): ("SILENCIEUSEMENT RESTRICTIF",
                     "toujours faux. Vehicule = trigger CONFIG nomme."),
            (0, 1): ("INCOHERENT", "past=0 et future=1 est impossible - re-lancer le harnais"),
        }
        verdict, detail = table.get(pair, ("ILLISIBLE", f"past={pair[0]} future={pair[1]}"))
        v.append(("Q3 date en constante", verdict, detail))
    return v


def interpret_naval(lines: list[str]) -> list[tuple[str, str, str]]:
    """EXPLAIN NAVAL: name the layer that blocks, without a human reading the journal.
    Controls first; then armed L3 gates; then, for context, the L1/L2 inputs at 0."""
    v: list[tuple[str, str, str]] = []
    scope = None
    layers: dict[str, dict[str, int]] = {}
    for t in lines:
        if "scope :" in t:
            scope = _nums(t)
        elif "L1 declarations" in t:
            layers.setdefault("L1", {}).update(_nums(t))
        elif "L2 observations" in t:
            layers.setdefault("L2", {}).update(_nums(t))
        elif "L3 decisions" in t:
            layers.setdefault("L3", {}).update(_nums(t))
    if scope is None:
        return [("CONTEXTE", "ABSENT", "pas de ligne `scope :` - ce n'est pas un run de ce harnais")]
    ok = (scope.get("always") == 1 and scope.get("I-am-ROOT") == 1
          and scope.get("I-am-THIS") == 1 and scope.get("ROOT-scope-usable") == 1
          and scope.get("control-false") == 0)
    v.append(("CONTEXTE", "OK" if ok else "STOP",
              "1 1 1 1 0 attendu, lu " + " ".join(str(scope.get(k)) for k in
              ("always", "I-am-ROOT", "I-am-THIS", "ROOT-scope-usable", "control-false"))))
    if not ok:
        v.append(("TOUT LE RESTE", "NON MESURE", "en-tete de contexte invalide"))
        return v
    l3 = layers.get("L3", {})
    armed = sorted(k for k, x in l3.items() if x == 1)
    v.append(("L3 armees", str(len(armed)) if armed else "AUCUNE",
              ", ".join(armed) if armed else "aucun gate naval arme pour ce pays a cet instant"))
    for lname in ("L2", "L1"):
        zeros = sorted(k for k, x in layers.get(lname, {}).items() if x == 0)
        if zeros:
            v.append((f"{lname} a zero", str(len(zeros)),
                      ", ".join(zeros) + " - si un gate attendu manque en L3, le blocage est ici"))
    return v


INTERPRETERS = {"pdx_semantics": interpret_pdx_semantics, "naval": interpret_naval}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--marker", help='harness marker, e.g. "PDX TEST" or "TC TEST"')
    ap.add_argument("--runs", type=int, default=1, help="how many of the most recent runs (default 1)")
    ap.add_argument("--logs", help="HOI4 logs directory (default: auto, or $HOI4_USERDIR)")
    ap.add_argument("--errors", action="store_true",
                    help="also show error.log lines from the run's wall-clock window")
    ap.add_argument("--interpret", choices=sorted(INTERPRETERS),
                    help="apply a harness-specific verdict table")
    ap.add_argument("--list", action="store_true",
                    help="list harness markers found in game.log and exit")
    args = ap.parse_args()

    logdir = find_logs(args.logs)
    gamelog = logdir / "game.log"
    if not gamelog.exists():
        sys.exit(f"no game.log in {logdir}")
    lines = read_lines(gamelog)
    print(f"# logs   : {logdir}")
    print(f"# game.log: {len(lines)} lignes, modifie {__import__('datetime').datetime.fromtimestamp(gamelog.stat().st_mtime):%Y-%m-%d %H:%M:%S}")

    if args.list or not args.marker:
        seen: dict[str, int] = {}
        for line in lines:
            _, _, t = strip_prefixes(line)
            m = re.search(r"\b([A-Z][A-Z0-9_ ]{2,30}TEST)\b", t)
            if m:
                seen[m.group(1).strip()] = seen.get(m.group(1).strip(), 0) + 1
        print("\n# marqueurs de harnais trouves dans game.log :")
        if not seen:
            print("  (aucun - le harnais n'a pas encore ete lance, ou le jeu n'a pas ecrit game.log)")
        for k, n in sorted(seen.items(), key=lambda x: -x[1]):
            print(f"  {n:4d}x  {k}")
        if not args.marker:
            print("\n  relancer avec --marker \"<un de ces marqueurs>\"")
            return 0

    runs = extract_runs(lines, args.marker)
    if not runs:
        print(f"\n!! marqueur {args.marker!r} absent de game.log.")
        print("   Le harnais n'a pas ete lance, ou le jeu n'a pas encore vide son tampon d'ecriture.")
        print("   Dans la console HOI4 : `tag GER` puis `event wa_pdx.1`, puis re-lancer cette commande.")
        return 1

    chosen = runs[-args.runs:]
    print(f"\n# {len(runs)} run(s) de {args.marker!r} dans le journal ; affichage du/des {len(chosen)} dernier(s).\n")

    status = 0
    for idx, run in enumerate(chosen, 1):
        walls = [w for w, _, _ in run if w]
        dates = [d for _, d, _ in run if d]
        print("=" * 96)
        print(f"RUN {idx}/{len(chosen)}   horloge {walls[0] if walls else '?'} -> {walls[-1] if walls else '?'}"
              f"   date de partie {dates[0] if dates else '?'}")
        print("=" * 96)
        for _, _, t in run:
            print(t)

        if args.interpret:
            print("\n" + "-" * 96)
            print("INTERPRETATION")
            print("-" * 96)
            for label, verdict, detail in INTERPRETERS[args.interpret]([t for _, _, t in run]):
                print(f"  {label:24s} {verdict}")
                for chunk in re.findall(r".{1,88}(?:\s|$)", detail):
                    print(f"  {'':24s}   {chunk.strip()}")
                if verdict in ("STOP", "NON MESURE"):
                    status = 2

        if args.errors and walls:
            errs = errors_in_window(logdir, walls[0], walls[-1])
            print("\n" + "-" * 96)
            print(f"ERROR.LOG sur la meme fenetre ({walls[0]} -> {walls[-1]})")
            print("-" * 96)
            if errs:
                for e in errs:
                    print("  " + e)
                print("\n  !! des erreurs pendant le run : une lecture etrange vient peut-etre de la,")
                print("     pas du comportement mesure. Les traiter avant de conclure.")
            else:
                print("  (aucune - le run est propre)")
        print()

    return status


if __name__ == "__main__":
    raise SystemExit(main())
