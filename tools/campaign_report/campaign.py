"""Campaign selection: dates are observations, never proof of branch continuity."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def legacy_savegame(repo: Path = REPO):
    path = repo / ".claude/skills/wa-savegame-analysis/scripts/savegame.py"
    spec = importlib.util.spec_from_file_location("_campaign_savegame", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def date_key(value: str) -> tuple[int, int, int, int]:
    parts = [int(x) for x in value.split(".")]
    if not 3 <= len(parts) <= 4:
        raise ValueError(f"Invalid save date: {value}")
    if len(parts) == 3:
        parts.append(0)
    datetime(*parts)
    return tuple(parts)


def digest_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_manifest(path: Path) -> list[Path]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    files = data.get("files") if isinstance(data, dict) else data
    if not isinstance(files, list) or not files or not all(isinstance(x, str) for x in files):
        raise ValueError("Le manifeste doit contenir une liste non vide de chemins (ou {files: [...]}).")
    return [(path.parent / f).resolve() for f in files]


def discover(paths: list[Path], recursive: bool = False, repo: Path = REPO) -> tuple[list[dict], list[str]]:
    files = set()
    for path in paths:
        if not path.exists():
            raise ValueError(f"Chemin absent : {path}")
        if path.is_dir():
            files.update(p.resolve() for p in (path.rglob("*") if recursive else path.iterdir())
                         if p.is_file() and p.suffix.lower() in {".hoi4", ".zip"})
        else:
            files.add(path.resolve())
    reader = legacy_savegame(repo)
    entries, errors = [], []
    for path in sorted(files):
        try:
            meta = reader.read_meta(str(path))
            if not meta.get("game_unique_id"):
                raise ValueError("game_unique_id missing; campaign undetermined")
            date_key(meta.get("date", ""))
            entries.append({**meta, "file": str(path)})
        except (SystemExit, ValueError, OSError, KeyError) as exc:
            errors.append(f"{path.name} : {exc}")
    return entries, errors


def summarize(entries: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in entries:
        groups[row["game_unique_id"]].append(row)
    return [{"id": identity, "count": len(rows),
             "start": min(rows, key=lambda r: date_key(r["date"]))["date"],
             "end": max(rows, key=lambda r: date_key(r["date"]))["date"],
             "mods": sorted({r.get("mods", "unknown") for r in rows})}
            for identity, rows in sorted(groups.items())]


def select(entries: list[dict], identity: str | None, *, explicit_manifest: bool = False,
           allow_ambiguous: bool = False) -> tuple[list[dict], list[str]]:
    identities = sorted({r["game_unique_id"] for r in entries})
    if identity:
        identities = [i for i in identities if i == identity or i.startswith(identity)]
    if len(identities) != 1:
        raise ValueError("Choose a single campaign with --campaign (see the list command).")
    rows = [dict(r) for r in entries if r["game_unique_id"] == identities[0]]
    if explicit_manifest and len(rows) != len(entries):
        raise ValueError("The manifest mixes several campaigns.")
    by_date, warnings = defaultdict(list), []
    for row in rows:
        by_date[date_key(row["date"])].append(row)
    selected = []
    for day, candidates in sorted(by_date.items()):
        if len(candidates) > 1:
            for row in candidates:
                row["sha256"] = digest_file(Path(row["file"]))
            if len({r["sha256"] for r in candidates}) != 1:
                names = ", ".join(Path(r["file"]).name for r in candidates)
                raise ValueError(f"Two different states at {candidates[0]['date']}: {names}. "
                                 "Select one branch with --manifest.")
            warnings.append(f"{len(candidates) - 1} identical copy/copies ignored at {candidates[0]['date']}.")
        selected.append(sorted(candidates, key=lambda r: r["file"])[0])
    sessions = [(r, int(r["session"])) for r in selected if str(r.get("session", "")).isdigit()]
    reversals = [(a[0]["date"], b[0]["date"]) for a, b in zip(sessions, sessions[1:]) if b[1] < a[1]]
    if reversals and not (explicit_manifest or allow_ambiguous):
        raise ValueError("Session order contradicts date order: ambiguous branch. "
                         "Choose the files with --manifest, or explicitly accept "
                         "--allow-ambiguous-timeline after checking.")
    if reversals:
        warnings.append("ASSUMED — continuity was explicitly selected despite session-order reversals.")
    if len({r.get("mods") for r in selected}) > 1:
        warnings.append("The mod list changes between the selected saves.")
    return selected, warnings
