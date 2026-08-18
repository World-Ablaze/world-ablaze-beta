#!/usr/bin/env python3
"""
check_engine_docs.py - keeps the vendored ENGINE documentation honest.

Replacing a vanilla folder means copying it, and every `common/<folder>` the mod
replaced arrived with the engine's own `_documentation.md` inside it. Those copies
are frozen at whatever patch they were taken from. The game never reads them, so
nothing complains - but agents and humans read them as if they described the
running engine, and they stop being true the next time Paradox edits one.

2026-08-18 is what this checker exists to prevent: `common/ai_strategy/documentation.info`
was the **2023-07** edition, 291 lines shorter than the installed 2024-11 one, and it
did not contain a single `force_concentration_*` token - the three types the whole
AIFC system is built on. That system was reverse-engineered against a file that did
not document it, and a dozen repo documents cited the stale file by line number.

    python tools/check_engine_docs.py           # report, exit 1 on any ERROR
    python tools/check_engine_docs.py --strict  # WARN also fails
    python tools/check_engine_docs.py --json    # machine-readable report
    python tools/check_engine_docs.py --sync-hint PATH   # print the copy command

The contract lives in tools/engine_docs_manifest.json. A file listed there is
SYNCED: it must still match the install byte for byte (WA-SYNC header excluded),
and the install must still match the hash recorded when it was synced. A vendored
doc *not* listed is only reported, never fatal - the repo has 18 of those and
adopting them is a decision, not an accident to be forced.

ERROR  DRIFT-REPO     a synced copy no longer matches the install
ERROR  DRIFT-INSTALL  the install changed since the sync (game patched) - re-sync
ERROR  MISSING-REPO   a manifest entry points at a repo file that does not exist
WARN   STALE          a vendored doc, not in the manifest, differs from the install
WARN   NO-INSTALL     a vendored doc with no counterpart in the install
INFO   UNSYNCED-OK    a vendored doc, not in the manifest, identical to the install

If the game install cannot be found (cloud runner, fresh checkout), every check is
SKIPPED and the exit code is 0. A checker that fails where it cannot see is a
checker people disable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tools" / "engine_docs_manifest.json"

# Where the HOI4 install usually is. Override with $HOI4_INSTALL.
INSTALL_CANDIDATES = [
    r"C:\Jeux\steamapps\common\Hearts of Iron IV",
    r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV",
    r"D:\Steam\steamapps\common\Hearts of Iron IV",
    r"E:\Steam\steamapps\common\Hearts of Iron IV",
    r"F:\SteamLibrary\steamapps\common\Hearts of Iron IV",
]

WA_SYNC = re.compile(r"^\s*(<!--\s*)?WA-SYNC:.*$")


def find_install() -> Path | None:
    env = os.environ.get("HOI4_INSTALL")
    if env and Path(env).is_dir():
        return Path(env)
    for c in INSTALL_CANDIDATES:
        if Path(c).is_dir():
            return Path(c)
    return None


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_sync_header(text: str) -> str:
    """Drop the WA-SYNC provenance block so the body compares byte for byte."""
    lines = text.splitlines(keepends=True)
    out, i = [], 0
    if lines and lines[0].lstrip().startswith("<!--") and "WA-SYNC" in lines[0]:
        while i < len(lines):
            line = lines[i]
            i += 1
            if line.rstrip().endswith("-->"):
                break
        while i < len(lines) and not lines[i].strip():
            i += 1
    out = lines[i:]
    return "".join(out)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def install_counterpart(install: Path, repo_rel: str) -> Path | None:
    """The engine doc sitting in the same folder, whatever it is named."""
    folder = install / Path(repo_rel).parent
    if not folder.is_dir():
        return None
    hits = [f for f in sorted(os.listdir(folder)) if "documentation" in f.lower()]
    return folder / hits[0] if hits else None


def vendored_docs() -> list[str]:
    out = []
    for root, _dirs, files in os.walk(REPO / "common"):
        for fn in files:
            if "documentation" in fn.lower():
                out.append(str(Path(root, fn).relative_to(REPO)).replace("\\", "/"))
    return sorted(out)


class Report:
    def __init__(self):
        self.rows: list[dict] = []

    def add(self, level, code, message):
        self.rows.append({"level": level, "code": code, "message": message})

    def count(self, level):
        return sum(1 for r in self.rows if r["level"] == level)


def run(strict: bool) -> tuple[Report, int]:
    rep = Report()
    install = find_install()
    if install is None:
        rep.add("INFO", "SKIPPED",
                "no HOI4 install found - set $HOI4_INSTALL to check. Nothing verified.")
        return rep, 0

    manifest = json.loads(read(MANIFEST)) if MANIFEST.exists() else {"synced": []}
    synced = {e["repo"]: e for e in manifest.get("synced", [])}

    for rel in vendored_docs():
        repo_path = REPO / rel
        game_path = install_counterpart(install, rel)
        entry = synced.get(rel)

        if game_path is None or not game_path.exists():
            rep.add("WARN", "NO-INSTALL", f"{rel}: no counterpart in the install")
            continue

        repo_body = strip_sync_header(read(repo_path))
        game_body = read(game_path)

        if entry:
            if sha(game_body) != entry.get("install_sha256"):
                rep.add("ERROR", "DRIFT-INSTALL",
                        f"{rel}: the install's {game_path.name} changed since "
                        f"{entry.get('synced')} - the game was patched, re-sync and re-read "
                        f"anything that cites it")
            if sha(repo_body) != sha(game_body):
                d = len(game_body.splitlines()) - len(repo_body.splitlines())
                rep.add("ERROR", "DRIFT-REPO",
                        f"{rel}: synced copy no longer matches the install "
                        f"({d:+d} lines) - hand-edited, or the sync never completed")
        else:
            if sha(repo_body) == sha(game_body):
                rep.add("INFO", "UNSYNCED-OK", f"{rel}: identical to the install")
            else:
                d = len(game_body.splitlines()) - len(repo_body.splitlines())
                rep.add("WARN", "STALE",
                        f"{rel}: {d:+d} lines vs the install's {game_path.name} - "
                        f"NOT in the manifest, so read the install, not this copy")

    for rel, entry in synced.items():
        if not (REPO / rel).exists():
            rep.add("ERROR", "MISSING-REPO", f"{rel}: manifest entry, file absent")

    fail = rep.count("ERROR") or (strict and rep.count("WARN"))
    return rep, (1 if fail else 0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="WARN also fails")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--sync-hint", metavar="REPO_PATH",
                    help="print how to refresh one vendored doc from the install")
    args = ap.parse_args()

    if args.sync_hint:
        install = find_install()
        if install is None:
            print("no HOI4 install found - set $HOI4_INSTALL")
            return 1
        g = install_counterpart(install, args.sync_hint)
        print(f'cp "{g}" "{REPO / args.sync_hint}"   # then re-add the WA-SYNC header')
        return 0

    rep, code = run(args.strict)

    if args.json:
        print(json.dumps({"rows": rep.rows, "exit": code}, indent=2))
        return code

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for r in sorted(rep.rows, key=lambda r: (order[r["level"]], r["code"], r["message"])):
        print(f'{r["level"]:5s} {r["code"]:14s} {r["message"]}')
    print(f'\n{rep.count("ERROR")} ERROR, {rep.count("WARN")} WARN, {rep.count("INFO")} INFO')
    return code


if __name__ == "__main__":
    sys.exit(main())
