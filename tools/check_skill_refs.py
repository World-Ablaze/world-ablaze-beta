#!/usr/bin/env python3
"""
check_skill_refs.py - the agent instructions must not cite files that no longer exist.

The .claude/skills and .claude/agents files are loaded as working knowledge every session, and
they drift the same way all documentation here drifts (lessons log, "Documentation drifts"):
the 2026-08-20 audit sampled ~45 concrete references and found 6 dead (~13%), including a
subsystem table still listing a file deleted four days earlier. Nothing checked them - the
engine docs have check_engine_docs.py, the constants have check_constants.py, the skills had
prose. This makes the file-reference half mechanical.

    python tools/check_skill_refs.py             # report, exit 1 on any dead reference
    python tools/check_skill_refs.py --selftest  # prove the rule fires, and only when it should

What is checked: every backtick-quoted, path-looking token in .claude/skills/*/SKILL.md,
.claude/agents/*.md, AGENTS.md and CLAUDE.md must resolve inside the repo - as a root-relative
path, a path relative to the citing file's directory, a glob (>= 1 match), or a bare filename
that exists anywhere in the tree.

What is deliberately NOT flagged (the false-positive classes measured while designing this):
- tokens with <placeholders>, URLs, absolute paths - not repo references;
- lines that say the file is dead ON the line (deleted / removed / retired / superseded / ...):
  recording a deletion is the skill doing its job;
- lines citing the GAME INSTALL or peer mods (install / vanilla / Expert AI / EAI_ / steamapps /
  hoi4.exe): wa-engine-reference cites `documentation/effects_documentation.md` meaning the
  install's copy, which must not be resolved against the repo's documentation/ folder.
Counts, line numbers and dates stay unchecked - a number cannot be resolved mechanically.
"""
from __future__ import annotations
import argparse
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SCAN = ("AGENTS.md", "CLAUDE.md")
SCAN_GLOBS = (".claude/skills/*/SKILL.md", ".claude/agents/*.md")

# A candidate is a path-looking run inside a backtick span: has a known suffix, or contains a
# separator and a known top-level directory.
SUFFIXES = (".txt", ".md", ".py", ".lua", ".json", ".csv", ".yml", ".info", ".mod", ".bmp")
CANDIDATE = re.compile(r"[A-Za-z0-9_./\\-]+")
TOPDIRS = ("common/", "events/", "tools/", "documentation/", "tests/", "map/", ".claude/",
           "history/", "localisation/", "interface/", "gfx/", "references/", "scripts/")

# Line-level exemptions. A dead file named on a line that SAYS it is dead is the skill working;
# install / peer-mod citations are not repo paths. Lowercase substring match on purpose - the
# selftest proves the rule still fires on an unexempted line.
EXEMPT = ("deleted", "removed", "retired", "gone", "superseded", "renamed", "no longer",
          "used to", "install", "vanilla", "expert ai", "eai_", "steamapps", "hoi4.exe",
          "workshop", "engine's", "the engine")


def candidates(line: str) -> list[str]:
    out = []
    for span in re.findall(r"`([^`]+)`", line):
        if "<" in span or ">" in span:
            continue  # `events/WA_AI_<TAG>.txt` is a pattern for the reader, not a checkable path
        # `*` stays inside the token so globs survive extraction whole
        for tok in re.findall(r"[A-Za-z0-9_.*/\\-]+", span):
            t = tok[2:] if tok.startswith("./") else tok
            t = t.rstrip("/")
            if not t or t in (".", ".."):
                continue
            if t.startswith(".") and "/" not in t:
                continue  # a bare extension mention (`.txt`), not a file
            low = t.lower()
            if "/" in t and not any(low.startswith(d) for d in TOPDIRS):
                # `ai_strategy/_documentation.md` - a path under an UNKNOWN base (usually the
                # game install's common/). Not resolvable against the repo, so not checkable.
                continue
            looks = low.endswith(SUFFIXES) or (
                "/" in t and any(low.startswith(d) for d in TOPDIRS))
            if not looks:
                # a glob with a top-level dir but no suffix (`common/ai_strategy/WA_AI_*`)
                looks = "*" in t and "/" in t and any(low.startswith(d) for d in TOPDIRS)
            if looks:
                out.append(t.replace("\\", "/"))
    return out


def resolves(tok: str, base_dir: Path, filenames: set[str]) -> bool:
    if "*" in tok:
        try:
            if list(REPO.glob(tok)) or list(base_dir.glob(tok)):
                return True
            # bare glob with no directory: match by filename anywhere
            if "/" not in tok and list(REPO.rglob(tok)):
                return True
        except (ValueError, OSError):
            return True  # an unglobbable pattern is not evidence of a dead file
        return False
    if (REPO / tok).exists() or (base_dir / tok).exists():
        return True
    # `references/checklist.md` cited from AGENTS.md is relative to the OWNING skill's directory
    try:
        if list(REPO.glob(".claude/skills/*/" + tok)):
            return True
    except (ValueError, OSError):
        pass
    return "/" not in tok and tok in filenames


def scan(repo: Path) -> list[tuple[str, int, str]]:
    """[(citing file, line number, dead token)] - deduplicated per (file, token)."""
    files = [repo / f for f in SCAN if (repo / f).exists()]
    for g in SCAN_GLOBS:
        files.extend(sorted(repo.glob(g)))
    filenames = {p.name for p in repo.rglob("*") if p.is_file()}
    dead, seen = [], set()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if any(w in low for w in EXEMPT):
                continue
            for tok in candidates(line):
                key = (f, tok)
                if key in seen:
                    continue
                seen.add(key)
                if not resolves(tok, f.parent, filenames):
                    dead.append((str(f.relative_to(repo)).replace("\\", "/"), i, tok))
    return dead


def selftest() -> int:
    """Two-sided: a tree with one dead ref must report exactly it; a clean tree reports nothing."""
    global REPO
    saved = REPO
    failures = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "common").mkdir()
        (root / "common/live_file.txt").write_text("x", encoding="utf-8")
        skill = root / ".claude/skills/demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "See `common/live_file.txt` and glob `common/live_*.txt`.\n"
            "Fix 1 deleted `common/dead_but_recorded.txt` - exempt line.\n"
            "install `documentation/only_in_the_install.md` - exempt line.\n"
            "Broken pointer to `common/definitely_dead.txt` on a plain line.\n"
            "Placeholder `events/WA_AI_<TAG>.txt` is skipped.\n"
            "Unknown base `ai_strategy/_documentation.md` is skipped (install path).\n"
            "A bare extension mention like `.txt` is skipped.\n",
            encoding="utf-8")
        REPO = root
        try:
            dead = scan(root)
        finally:
            REPO = saved
        toks = [t for _, _, t in dead]
        if toks != ["common/definitely_dead.txt"]:
            failures.append(f"expected exactly the one dead ref, got {toks}")
        REPO = root
        try:
            (skill / "SKILL.md").write_text("only `common/live_file.txt` here\n", encoding="utf-8")
            if scan(root):
                failures.append("clean tree reported findings")
        finally:
            REPO = saved
    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  " + f)
        return 1
    print("selftest ok - fires on the dead ref, silent on live/glob/exempt/placeholder/clean")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    dead = scan(REPO)
    for f, i, tok in dead:
        print(f"ERROR DEAD-REF {f}:{i}: `{tok}` resolves to nothing in the repo - fix the "
              f"reference, or state on the same line why the file is legitimately absent")
    print(f"\n{len(dead)} dead reference(s)")
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
