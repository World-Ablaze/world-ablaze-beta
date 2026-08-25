#!/usr/bin/env python3
"""
Self-test for check_worklist.py - one fixture per rule, and a completeness clause.

Builds a clean fixture tree that must report NOTHING, then applies one mutation per rule
and fails if the rule does not fire on the input built to break it. The final clause
fails the test if any rule code named in the checker's docstring has no fixture here -
that clause is the whole point: three rules once shipped inert (2026-08-18) because
nothing proved they could fire.

Run via: python tools/check_worklist.py --selftest
"""
from __future__ import annotations
import datetime
import re
import shutil
import tempfile
from pathlib import Path

import check_worklist as cw

TODAY = datetime.date(2026, 8, 23)

CLEAN_WORK = """# WORK - subjects

## OPEN

### alpha-subject — OPEN (2026-08-22)
- Scope: something.
- Closed when: the probe passes.

### beta-subject — SHIPPED-UNTESTED (2026-08-22)
- Closed when: harness output pasted.

## PARKED

| Subject | State when parked | Symptom (MEASURED) | Closed when |
| --- | --- | --- | --- |
| `gamma` | FAILED (2026-08-01) | a symptom | its probe passes |

## CLOSED (last 10)

| Date | Subject | Note |
| --- | --- | --- |
"""

CLEAN_HARNESS = """# harness-contract: v1
# I-am-ROOT: JAP  scope: country
# control-false: JAP owns Moscow -> must print 0
# STOP: if the control prints 1, stop - every later reading is poisoned
WA_TEST_dummy_run = {
\tlog = "ok"
}
"""


def build_clean(root: Path) -> None:
    (root / "common/scripted_effects").mkdir(parents=True)
    (root / "common/scripted_triggers").mkdir(parents=True)
    (root / "WORK.md").write_text(CLEAN_WORK, encoding="utf-8")
    (root / "common/scripted_effects/WA_TEST_fixture.txt").write_text(
        CLEAN_HARNESS, encoding="utf-8")
    (root / "common/scripted_effects/WA_AI_fixture.txt").write_text(
        "WA_AI_dummy = {\n\tlog = \"x\"\n}\n", encoding="utf-8")


def run_on(root: Path) -> list[dict]:
    cw.REPO, cw.WORK = root, root / "WORK.md"
    rep = cw.Report()
    cw.run_checks(rep, today=TODAY)
    return rep.rows


# One mutation per rule: (code, mutate(root)).
def mut_wip(root: Path) -> None:
    text = (root / "WORK.md").read_text(encoding="utf-8")
    extra = "".join(
        f"\n### filler-{i} — OPEN (2026-08-22)\n- Closed when: never.\n" for i in range(4))
    (root / "WORK.md").write_text(
        text.replace("## PARKED", extra + "\n## PARKED"), encoding="utf-8")


def mut_stale(root: Path) -> None:
    text = (root / "WORK.md").read_text(encoding="utf-8")
    (root / "WORK.md").write_text(
        text.replace("SHIPPED-UNTESTED (2026-08-22)", "SHIPPED-UNTESTED (2026-08-10)"),
        encoding="utf-8")


def mut_noexit(root: Path) -> None:
    text = (root / "WORK.md").read_text(encoding="utf-8")
    (root / "WORK.md").write_text(
        text.replace("- Closed when: the probe passes.\n", ""), encoding="utf-8")


def mut_harness(root: Path) -> None:
    (root / "common/scripted_effects/WA_TEST_new_harness.txt").write_text(
        "WA_TEST_no_header = {\n\tlog = \"x\"\n}\n", encoding="utf-8")


def mut_bom(root: Path) -> None:
    p = root / "common/scripted_triggers/WA_AI_bombed.txt"
    p.write_bytes(b"\xef\xbb\xbfWA_AI_t = { always = yes }\n")


MUTATIONS = [
    ("WIP-LIMIT", mut_wip),
    ("UNTESTED-STALE", mut_stale),
    ("NO-EXIT", mut_noexit),
    ("HARNESS-CONTRACT", mut_harness),
    ("BOM-IN-SCRIPT", mut_bom),
]


def run(verbose: bool = False) -> int:
    orig = (cw.REPO, cw.WORK)
    failures: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="worklist_selftest_"))
    try:
        # 1. Clean tree reports nothing.
        clean = tmp / "clean"
        build_clean(clean)
        rows = run_on(clean)
        if rows:
            failures.append(f"clean fixture not clean: {[r['code'] for r in rows]}")

        # 2. Each mutation makes exactly its rule fire.
        for code, mutate in MUTATIONS:
            root = tmp / code.lower()
            build_clean(root)
            mutate(root)
            fired = {r["code"] for r in run_on(root)}
            if code not in fired:
                failures.append(f"{code}: mutation built to break it did not fire "
                                f"(fired: {sorted(fired) or 'nothing'})")
            elif verbose:
                print(f"ok    {code}")

        # 3. Completeness: every rule code the checker documents has a fixture here.
        documented = set(re.findall(r"^\s*(?:ERROR|WARN)\s+([A-Z-]+)", cw.__doc__, re.M))
        covered = {c for c, _ in MUTATIONS}
        missing = documented - covered
        if missing:
            failures.append(f"documented rule(s) with no self-test fixture: "
                            f"{', '.join(sorted(missing))} - a new rule with no fixture "
                            f"is the inert-rule failure this clause exists to stop")
    finally:
        cw.REPO, cw.WORK = orig
        shutil.rmtree(tmp, ignore_errors=True)

    for f in failures:
        print("FAIL  " + f)
    if verbose and not failures:
        print(f"selftest: {len(MUTATIONS)} rules fired, clean tree clean, "
              f"docstring coverage complete")
    return 1 if failures else 0


if __name__ == "__main__":
    import sys
    sys.exit(run(verbose=True))
