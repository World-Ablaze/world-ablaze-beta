#!/usr/bin/env python3
"""
collapse_fix_comments.py - phase C of the 2026-08-23 tracking redesign.

Replaces the retired `Fix NN` numbering inside PDXScript COMMENTS with the subject slug
that absorbed the fix (`# Fix 95: ...` -> `# [na-corridor] ...`), across common/ and
events/. Numbers resolve through tools/archive/fix_tracking/fix_slug_map.json; the historical number->commit
table stays in documentation/FIX_HISTORY.md.

Safety: the transform must be behaviour-neutral. Only the text at or after the first `#`
of a line is ever touched, and --verify recomputes the code-only content (everything
before the first `#` of every line) of every file and fails if a single code byte
changed. Run order:

    python tools/archive/fix_tracking/collapse_fix_comments.py --dry-run   # report what would change
    python tools/archive/fix_tracking/collapse_fix_comments.py             # apply + verify
    python tools/archive/fix_tracking/collapse_fix_comments.py --verify    # standalone: code equals baseline

--dry-run and the apply run both write a baseline manifest of code-only hashes to the
scratch file next to this script (fix_collapse_baseline.json) before touching anything,
so --verify can prove the invariant even across sessions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MAP = REPO / "tools/archive/fix_tracking/fix_slug_map.json"
BASELINE = REPO / "tools/fix_collapse_baseline.json"
BASES = ("common", "events")

TOKEN = re.compile(r"\bFix(?:es)? (\d{1,3}[a-z]?)((?:\s*[/+&]\s*\d{1,3}[a-z]?)*)\b")


def code_hash(text: str) -> str:
    """Hash of the code-only view: every line truncated at its first '#'."""
    code = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    return hashlib.sha256(code.encode("utf-8", "replace")).hexdigest()


def load_map() -> dict[str, str]:
    m = json.loads(MAP.read_text(encoding="utf-8"))
    bad = [k for k, v in m.items() if not re.fullmatch(r"[a-z0-9-]+", v)]
    if bad:
        sys.exit(f"fix_slug_map.json: non-slug values for {bad}")
    return m


def slug_for(num: str, m: dict[str, str]) -> str | None:
    return m.get(num) or m.get(re.sub(r"[a-z]$", "", num))


def transform_comment(comment: str, m: dict[str, str], misses: set[str]) -> str:
    """Rewrite one comment chunk (text starting at '#')."""
    def repl(match: re.Match) -> str:
        nums = [match.group(1)] + re.findall(r"\d{1,3}[a-z]?", match.group(2) or "")
        slugs, out_nums = [], []
        for n in nums:
            s = slug_for(n, m)
            if s is None:
                misses.add(n)
                out_nums.append(n)
            elif s not in slugs:
                slugs.append(s)
        if out_nums:            # any unmapped number: leave the whole token untouched
            return match.group(0)
        return " + ".join(f"[{s}]" for s in slugs)
    out = TOKEN.sub(repl, comment)
    # tidy the seam the substitution leaves: "# [slug]: text" -> "# [slug] text"
    out = re.sub(r"(\[[a-z0-9-]+\])\s*:\s", r"\1 ", out)
    return out


def process(text: str, m: dict[str, str], misses: set[str]) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    changed = 0
    for i, line in enumerate(lines):
        h = line.find("#")
        if h < 0 or "Fix" not in line[h:]:
            continue
        new = transform_comment(line[h:], m, misses)
        if new != line[h:]:
            lines[i] = line[:h] + new
            changed += 1
    return "".join(lines), changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="only check code-vs-baseline equality")
    args = ap.parse_args()

    files = [p for b in BASES for p in (REPO / b).rglob("*.txt")]

    if args.verify:
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        bad = []
        for f, h in base.items():
            raw = (REPO / f).read_bytes()
            if code_hash(raw.decode("utf-8", errors="replace")) != h:
                bad.append(f)
        for f in bad:
            print(f"CODE CHANGED: {f}")
        print(f"verify: {len(base)} files, {len(bad)} code deviations")
        return 1 if bad else 0

    m = load_map()
    baseline: dict[str, str] = {}
    misses: set[str] = set()
    total_lines = total_files = 0
    skipped: list[str] = []
    for p in sorted(files):
        rel = str(p.relative_to(REPO)).replace("\\", "/")
        raw = p.read_bytes()
        # Newlines are preserved: everything runs on the exact decoded bytes and the
        # write goes back as bytes - no universal-newline translation anywhere.
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            if b"Fix " in raw:
                skipped.append(rel)   # non-UTF-8 legacy file: leave for a manual pass
            continue
        new, n = process(text, m, misses)
        if n:
            baseline[rel] = code_hash(text)
            total_files += 1
            total_lines += n
            if args.dry_run:
                print(f"{n:4d} lines  {rel}")
            else:
                if code_hash(new) != baseline[rel]:
                    print(f"ABORT: code changed in {rel}")
                    return 1
                p.write_bytes(new.encode("utf-8"))
    BASELINE.write_text(json.dumps(baseline, indent=1), encoding="utf-8")
    print(f"{'would change' if args.dry_run else 'changed'}: "
          f"{total_lines} comment lines in {total_files} files")
    if misses:
        print(f"unmapped numbers left untouched: {', '.join(sorted(misses))}")
    if skipped:
        print(f"non-UTF-8 files skipped (manual pass): {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
