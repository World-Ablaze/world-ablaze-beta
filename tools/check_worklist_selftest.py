#!/usr/bin/env python3
"""
Self-test for check_worklist.py: prove every rule still fires.

WHY THIS EXISTS
---------------
On 2026-08-18 four rules were written in one session and three of them shipped inert:

- `CRITERION-UNSCOREABLE` asked "is there a digit in this leg", which `type-13` satisfies.
- the status derivation mislabelled every item whose history carried a baseline row.
- `FIX-UNREGISTERED` had a backspace byte where a `\\b` should have been. It walked 2,346
  files, matched nothing, and printed a clean report - byte for byte what success looks like.

None of that was caught by reading the diff. Every one was caught by building an input that
MUST fail and watching whether it did. This module makes that step a part of the tool instead
of something a session remembers to do.

HOW IT WORKS
------------
One BASELINE set of files that is valid and must produce **zero** findings. Every case is the
baseline with a single mutation, and asserts one rule code appears. Two-sided by construction:
a rule that never fires fails its own case, and a rule that fires on everything fails the
baseline. There is no way for both halves to pass while the rule does nothing.

THE CLAUSE THAT MAKES IT NON-OPTIONAL
-------------------------------------
Every `rep.add(...)` code in check_worklist.py must have a case here. A new rule with no case
fails the self-test, which is the only reason this file cannot rot.

    python tools/check_worklist.py --selftest
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load():
    """Load check_worklist.py FROM SOURCE, never from __pycache__.

    `spec.loader.exec_module` honours the bytecode cache. A stale .pyc had this self-test
    exercising an older copy of the checker while the file on disk said something else -
    it reported a rule as firing after that rule had been broken, which is precisely the
    lie this module exists to make impossible. Compiling the text is the only way to be
    sure the thing under test is the thing on disk.
    """
    path = HERE / "check_worklist.py"
    src = path.read_text(encoding="utf-8")
    spec = importlib.util.spec_from_file_location("cw", path)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = str(path)
    exec(compile(src, str(path), "exec"), mod.__dict__)
    return mod


# --------------------------------------------------------------------- baseline

BASE_QUEUE = """# Work queue

## ACTIVE

- **A subject.** Why it matters. **Closed when** something measurable happens.

---

## QUEUE

| # | Subject | Why it matters | Closed when |
| --- | --- | --- | --- |
| 1 | A queued subject | Because. | A number is written down |

---

## DONE

| Date | Subject | Trace |
| --- | --- | --- |
"""

BASE_CHECKLIST = """# Checklist

## Campaign registry (analysed to date)

| Campaign | Date |
| --- | --- |
| `aaaaaaaa` | 2026-08-18 |

## RETIREABLE - fix verifications

### R1. A thing holds

- **Ledger:** `class=RETIREABLE threshold=3 streak=1 fix=deadbeef1 status=PASSING`
- **Opened 2026-08-01** from campaign `aaaaaaaa`.
- **Fix under test:** `deadbeef1`
- **Pass:**
  1. The counter is above 5 on every save.
- **Probe:** `savegame.py tlm ENG <saves> --match r1`
- **Threshold:** 3
- **Streak:** 1
- **Status:** PASSED once (`aaaaaaaa`)
- **History:**
  - 2026-08-18 · `aaaaaaaa` · PASSED

## Retired and merged items - ledger

| Item | State | When | Note |
| --- | --- | --- | --- |
"""

BASE_REGISTRY = '{\n "1": {"commit": "deadbeef1", "subject": "fix(ai): a thing", "reachable": true, "note": ""}\n}\n'

BASE_TREE = {
    "common/scripted_effects/WA_TLM_core.txt": "# nothing\n",
}


def _write_tree(root: Path, queue: str, checklist: str, registry: str, tree: dict) -> None:
    (root / "QUEUE.md").write_text(queue, encoding="utf-8")
    chk = root / ".claude/skills/wa-campaign-checklist/references"
    chk.mkdir(parents=True, exist_ok=True)
    (chk / "checklist.md").write_text(checklist, encoding="utf-8")
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "tools/fix_registry.json").write_text(registry, encoding="utf-8")
    for rel, body in tree.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


def _run(cw, queue=None, checklist=None, registry=None, tree=None, git_state=None):
    """Run every check against a throwaway tree. Returns the set of codes reported."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _write_tree(root,
                    BASE_QUEUE if queue is None else queue,
                    BASE_CHECKLIST if checklist is None else checklist,
                    BASE_REGISTRY if registry is None else registry,
                    BASE_TREE if tree is None else tree)
        saved = (cw.REPO, cw.QUEUE, cw.CHECKLIST, cw.FIX_REGISTRY, cw.git_state)
        cw.REPO = root
        cw.QUEUE = root / "QUEUE.md"
        cw.CHECKLIST = root / ".claude/skills/wa-campaign-checklist/references/checklist.md"
        cw.FIX_REGISTRY = root / "tools/fix_registry.json"
        cw.git_state = git_state or (lambda sha: "reachable")
        try:
            rep = cw.Report()
            cw.check_queue(rep)
            cw.check_checklist(rep)
            cw.check_fix_registry(rep)
            cw.check_harness_contract(rep)
            cw.check_bom(rep)
            return {r["code"] for r in rep.rows}, rep.rows
        finally:
            (cw.REPO, cw.QUEUE, cw.CHECKLIST, cw.FIX_REGISTRY, cw.git_state) = saved


def _sub(text: str, old: str, new: str) -> str:
    assert old in text, f"fixture drifted, missing: {old[:60]}"
    return text.replace(old, new, 1)


# ------------------------------------------------------------------------ cases
# Each entry: code -> a callable returning kwargs for _run(). One mutation each.

CASES = {
    "NO-QUEUE":      lambda: dict(queue="__DELETE__"),
    "NO-CHECKLIST":  lambda: dict(checklist="__DELETE__"),
    "NO-FIX-REGISTRY": lambda: dict(registry="__DELETE__"),

    "NO-ACTIVE": lambda: dict(queue=_sub(BASE_QUEUE, "- **A subject.** Why it matters. **Closed when** something measurable happens.", "")),
    "MULTI-ACTIVE": lambda: dict(queue=_sub(
        BASE_QUEUE, "- **A subject.** Why it matters. **Closed when** something measurable happens.",
        "- **A subject.** **Closed when** x.\n- **A second subject.** **Closed when** y.")),
    "NO-EXIT": lambda: dict(queue=_sub(BASE_QUEUE,
        "| 1 | A queued subject | Because. | A number is written down |",
        "| 1 | A queued subject | Because. |  |")),

    "LEDGER-MISSING": lambda: dict(checklist=_sub(BASE_CHECKLIST,
        "- **Ledger:** `class=RETIREABLE threshold=3 streak=1 fix=deadbeef1 status=PASSING`\n", "")),
    "LEDGER-MISMATCH": lambda: dict(checklist=_sub(BASE_CHECKLIST, "streak=1 fix=deadbeef1", "streak=9 fix=deadbeef1")),
    "STATUS-UNSET": lambda: dict(checklist=_sub(BASE_CHECKLIST, "status=PASSING", "status=UNSET")),

    "NO-PROBE": lambda: dict(checklist=_sub(BASE_CHECKLIST,
        "- **Probe:** `savegame.py tlm ENG <saves> --match r1`\n", "")),
    "PROBE-UNRUN": lambda: dict(checklist=_sub(BASE_CHECKLIST, "**Opened 2026-08-01**", "**Opened 2026-12-01**")),
    "CRITERION-UNSCOREABLE": lambda: dict(checklist=_sub(BASE_CHECKLIST,
        "  1. The counter is above 5 on every save.",
        "  1. The counter stays in the envelope of the previous campaign, whatever that was.")),

    "STATUS-STALE": lambda: dict(checklist=_sub(BASE_CHECKLIST,
        "- **Status:** PASSED once (`aaaaaaaa`)", "- **Status:** NOT YET TESTED")),
    "RETIRE-DUE": lambda: dict(checklist=_sub(BASE_CHECKLIST, "- **Threshold:** 3", "- **Threshold:** 1")),
    "NEVER-SCORED": lambda: dict(checklist=_sub(BASE_CHECKLIST,
        "  - 2026-08-18 · `aaaaaaaa` · PASSED", "  - 2026-08-18 · `aaaaaaaa` · NOT CHECKED")),
    # Never scored AND opened after the last analysed campaign (2026-08-18 in the baseline):
    # must fire the INFO, not the ERROR. PROBE-UNRUN also fires here (late Opened, no fenced
    # block) - membership is all the harness asserts, so that is fine.
    "AWAITING-CAMPAIGN": lambda: dict(checklist=_sub(_sub(BASE_CHECKLIST,
        "  - 2026-08-18 · `aaaaaaaa` · PASSED", "  - 2026-08-18 · `aaaaaaaa` · NOT CHECKED"),
        "**Opened 2026-08-01**", "**Opened 2026-12-01**")),
    "REGISTRY-MISSING": lambda: dict(checklist=_sub(BASE_CHECKLIST, "| `aaaaaaaa` | 2026-08-18 |", "")),
    "SUPERSEDED": lambda: dict(checklist=_sub(BASE_CHECKLIST, "### R1. A thing holds",
                                              "### R1. A thing holds - superseded by R2 in a later pass")),
    "DORMANT": lambda: dict(checklist=_sub(BASE_CHECKLIST,
        "| `aaaaaaaa` | 2026-08-18 |",
        "| `aaaaaaaa` | 2026-08-18 |\n| `bbbbbbbb` | 2026-08-19 |\n| `cccccccc` | 2026-08-20 |\n| `dddddddd` | 2026-08-21 |")),

    "ORPHAN-FIX":  lambda: dict(git_state=lambda sha: "orphan"),
    "UNKNOWN-REF": lambda: dict(git_state=lambda sha: "unknown"),
    "FIX-ORPHAN":  lambda: dict(git_state=lambda sha: "orphan"),

    "TLM-ORPHAN": lambda: dict(tree={"common/scripted_effects/WA_TLM_core.txt":
                                     "x = { set_variable = { WA_TLM_r55_thing_n = 1 } }\n"}),
    "FIX-UNREGISTERED": lambda: dict(tree={"common/scripted_effects/a.txt": "# Fix 999 did a thing\n"}),
    # A new (non-grandfathered) console harness with no context header at all.
    "HARNESS-CONTRACT": lambda: dict(tree={"common/scripted_effects/WA_TEST_new_probe.txt":
                                           'WA_TEST_NP_report = { log = "x" }\n'}),
    # ﻿ written as utf-8 emits the EF BB BF byte order mark the rule must catch.
    "BOM-IN-SCRIPT": lambda: dict(tree={"common/scripted_effects/a.txt": "﻿# innocuous\n"}),
    "FIX-UNRESOLVED": lambda: dict(registry='{\n "1": {"commit": null, "subject": "", "reachable": false, "note": "cannot be recovered"}\n}\n'),
}


def run(verbose: bool = False) -> int:
    cw = _load()
    failures: list[str] = []

    declared = set(re.findall(r'rep\.add\(\s*"(?:ERROR|WARN|INFO)",\s*"([A-Z0-9-]+)"',
                              (HERE / "check_worklist.py").read_text(encoding="utf-8")))
    missing = sorted(declared - set(CASES))
    if missing:
        failures.append(f"rules with no self-test case: {', '.join(missing)}")
    stale = sorted(set(CASES) - declared)
    if stale:
        failures.append(f"self-test cases for rules that no longer exist: {', '.join(stale)}")

    codes, rows = _run(cw)
    if codes:
        failures.append(f"the BASELINE must be clean but reported {sorted(codes)}")
    elif verbose:
        print("  baseline clean")

    for code in sorted(CASES):
        kwargs = CASES[code]()
        for key in ("queue", "checklist", "registry"):
            if kwargs.get(key) == "__DELETE__":
                kwargs[key] = None
                kwargs["_delete"] = key
        delete = kwargs.pop("_delete", None)
        if delete:
            got = _run_with_missing(cw, delete)
        else:
            got, _ = _run(cw, **kwargs)
        if code not in got:
            failures.append(f"{code}: its fixture did not make it fire (got {sorted(got) or 'nothing'}) "
                            f"- the rule is inert, or the fixture no longer exercises it")
        elif verbose:
            print(f"  {code} fires")

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"selftest ok - baseline clean, {len(CASES)} rules each fire on their own fixture")
    return 0


def _run_with_missing(cw, which: str) -> set:
    """The three 'file absent' guards need the file genuinely gone, not empty."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _write_tree(root, BASE_QUEUE, BASE_CHECKLIST, BASE_REGISTRY, BASE_TREE)
        target = {"queue": root / "QUEUE.md",
                  "checklist": root / ".claude/skills/wa-campaign-checklist/references/checklist.md",
                  "registry": root / "tools/fix_registry.json"}[which]
        target.unlink()
        saved = (cw.REPO, cw.QUEUE, cw.CHECKLIST, cw.FIX_REGISTRY, cw.git_state)
        cw.REPO = root
        cw.QUEUE = root / "QUEUE.md"
        cw.CHECKLIST = root / ".claude/skills/wa-campaign-checklist/references/checklist.md"
        cw.FIX_REGISTRY = root / "tools/fix_registry.json"
        cw.git_state = lambda sha: "reachable"
        try:
            rep = cw.Report()
            cw.check_queue(rep)
            cw.check_checklist(rep)
            cw.check_fix_registry(rep)
            cw.check_harness_contract(rep)
            cw.check_bom(rep)
            return {r["code"] for r in rep.rows}
        finally:
            (cw.REPO, cw.QUEUE, cw.CHECKLIST, cw.FIX_REGISTRY, cw.git_state) = saved


if __name__ == "__main__":
    sys.exit(run(verbose="-v" in sys.argv))
