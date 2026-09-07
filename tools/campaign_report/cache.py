"""Content-addressed snapshot cache, also keyed by extractor and mod definitions."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from . import SCHEMA_VERSION
from .campaign import digest_file


def dependency_digest(repo: Path) -> str:
    paths = set((repo / "tools/campaign_report").glob("*.py"))
    paths.update((repo / ".claude/skills/wa-savegame-analysis/scripts").glob("*.py"))
    paths.update((repo / "common/units").rglob("*.txt"))
    paths.update((repo / "common/buildings").glob("*.txt"))
    paths.update((repo / "common/ideas").glob("*.txt"))  # the conscription ladder and idea modifiers
    # Displayed stability / war support: advisor traits, dynamic modifiers, NCountry defines.
    paths.update((repo / "common/characters").glob("*.txt"))
    paths.update((repo / "common/country_leader").glob("*.txt"))
    paths.update((repo / "common/dynamic_modifiers").glob("*.txt"))
    paths.add(repo / "common/defines/05_defines.lua")
    # UI/render/CLI do not change an extracted value; changing them must reuse the cache.
    paths = {p for p in paths if p.name not in {"render.py", "__main__.py", "campaign.py", "cache.py", "digest.py", "convoys.py"}
             and not p.name.startswith("test_")}
    digest = hashlib.sha256(f"schema:{SCHEMA_VERSION}".encode())
    for path in sorted(paths):
        digest.update(path.relative_to(repo).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".writing-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def snapshot(path: Path, root: Path, dependencies: str, extract, repo: Path,
             *, refresh: bool = False) -> tuple[dict, bool, str]:
    before = path.stat()
    content_hash = digest_file(path)
    hashed = path.stat()
    if (before.st_size, before.st_mtime_ns) != (hashed.st_size, hashed.st_mtime_ns):
        raise ValueError(f"The save changed while it was being hashed: {path.name}.")
    key = hashlib.sha256(f"{SCHEMA_VERSION}:{content_hash}:{dependencies}".encode()).hexdigest()
    target = root / f"{key}.json"
    if target.exists() and not refresh:
        try:
            cached = json.loads(target.read_text(encoding="utf-8"))
            if (cached.get("key") == key and isinstance(cached.get("snapshot"), dict)
                    and isinstance(cached["snapshot"].get("countries"), dict)
                    and cached["snapshot"].get("date")):
                return cached["snapshot"], True, content_hash
        except (ValueError, OSError):
            pass  # Corrupt/truncated cache: reconstruct from the save, never emit fake zeros.
    data = extract(path, repo)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f"The save changed while it was being read: {path.name}. Run again once it is complete.")
    atomic_json(target, {"key": key, "snapshot": data})
    return data, False, content_hash


def extract_job(job):
    """Importable worker entry point (package __main__ is not spawn-pickleable)."""
    from .campaign import REPO
    from .extract import extract_save
    path, cache, dependencies, refresh = job
    return snapshot(path, cache, dependencies, extract_save, REPO, refresh=refresh)
