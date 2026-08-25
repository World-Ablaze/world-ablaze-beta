#!/usr/bin/env python3
"""
check_worklist.py - keeps the open work honest: WORK.md and the script folders.

Since 2026-08-23 the project tracks SUBJECTS in WORK.md (one subject = one intended
behaviour, slug-named); the per-fix checklist items, the fix registry rules and the
QUEUE.md ledger are retired (documentation/PROCESS_REDESIGN_PROPOSAL.md). This checker
keeps the five rules whose absence already cost a debugging session each - nothing more:
a rule that polices the tracker itself creates meta-work, which is the failure the
redesign removed.

    python tools/check_worklist.py            # report, exit 1 on any ERROR
    python tools/check_worklist.py --strict   # WARN also fails
    python tools/check_worklist.py --json     # machine-readable
    python tools/check_worklist.py --selftest # prove every rule fires on a fixture

WORK.md
  ERROR  WIP-LIMIT       more than MAX_OPEN subjects under '## OPEN' - the scatter this
                         file exists to stop. Park or close before opening.
  ERROR  UNTESTED-STALE  a subject in SHIPPED-UNTESTED for more than STALE_DAYS days.
                         The rule that would have caught lend-lease: code shipped, the
                         owner never ran the console harness, broken for a week silently.
  WARN   NO-EXIT         an OPEN subject without a 'Closed when' line, or a
                         PARKED row without its 4th column - a wish, not a task.

script folders
  ERROR  HARNESS-CONTRACT a common/scripted_effects/WA_TEST_*.txt console harness without
                         the v1 context header (marker, who/scope lines, known-false
                         control, STOP rule - wa-testing SKILL). The detector that caught
                         the Fix 118 call-site artefact, made mechanical; files shipped
                         before 2026-08-20 are grandfathered.
  ERROR  BOM-IN-SCRIPT   a .txt under common/scripted_effects or common/scripted_triggers
                         starting with the UTF-8 BOM (EF BB BF). That parser desyncs on
                         every token after it and the whole file silently fails to load -
                         a re-saved BOM once killed the entire priority-construction
                         system (AGENTS.md rule 16, mechanical).
"""
from __future__ import annotations
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = REPO / "WORK.md"

MAX_OPEN = 4          # WIP limit, owner decision 2026-08-23
STALE_DAYS = 3        # SHIPPED-UNTESTED older than this is an ERROR
OPEN_STATES = {"OPEN", "SHIPPED-UNTESTED", "TESTED", "CAMPAIGN-OK"}
# Heading contract: ### <slug> — <STATE> (<YYYY-MM-DD>)   (em dash or hyphen accepted)
HEADING = re.compile(r"^### ([a-z0-9-]+)\s+[—-]+\s+([A-Z-]+)\s*\((\d{4}-\d{2}-\d{2})\)",
                     re.M)
EXIT_LINE = re.compile(r"^- Closed when\s*:", re.M | re.I)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


class Report:
    def __init__(self):
        self.rows: list[dict] = []

    def add(self, level, code, message):
        self.rows.append({"level": level, "code": code, "message": message})

    def count(self, lvl):
        return sum(1 for r in self.rows if r["level"] == lvl)


# --------------------------------------------------------------------------- WORK.md

def section(text: str, name: str) -> str:
    m = re.search(rf"^## {name}\b.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def check_work(rep: Report, today: datetime.date | None = None) -> None:
    if not WORK.exists():
        rep.add("WARN", "NO-WORK", "WORK.md absent - no subject list is being kept")
        return
    text = read(WORK)
    today = today or datetime.date.today()

    open_sec = section(text, "OPEN")
    subjects = []  # (slug, state, date, body)
    parts = re.split(HEADING, open_sec)
    for i in range(1, len(parts) - 3, 4):
        subjects.append((parts[i], parts[i + 1], parts[i + 2], parts[i + 3]))

    # WIP-LIMIT
    live = [s for s in subjects if s[1] != "PARKED"]
    if len(live) > MAX_OPEN:
        rep.add("ERROR", "WIP-LIMIT",
                f"WORK.md: {len(live)} subjects under OPEN, limit is {MAX_OPEN} - park or "
                f"close one before opening another ({', '.join(s[0] for s in live)})")

    for slug, state, date, body in subjects:
        # UNTESTED-STALE
        if state == "SHIPPED-UNTESTED":
            try:
                age = (today - datetime.date.fromisoformat(date)).days
            except ValueError:
                age = None
            if age is None or age > STALE_DAYS:
                rep.add("ERROR", "UNTESTED-STALE",
                        f"WORK.md: '{slug}' has been SHIPPED-UNTESTED since {date} "
                        f"(> {STALE_DAYS} days) - run the console harness, paste the "
                        f"output, and move it to TESTED (or park it with its state)")
        # NO-EXIT
        if not EXIT_LINE.search(body):
            rep.add("WARN", "NO-EXIT",
                    f"WORK.md: '{slug}' has no 'Closed when' line - a wish, not a task")

    # NO-EXIT on PARKED rows (4 columns mandatory)
    for row in section(text, "PARKED").splitlines():
        row = row.strip()
        if not row.startswith("|") or re.match(r"^\|[\s\-|]+\|$", row):
            continue
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cells and cells[0].lower().startswith("subject"):
            continue
        if len(cells) < 4 or not cells[3]:
            rep.add("WARN", "NO-EXIT",
                    f"WORK.md PARKED: \"{cells[0][:48]}\" has no 'Closed when' column")


# --------------------------------------------------------------- script folders

# Console harnesses shipped before the contract (2026-08-20). A new WA_TEST_*.txt file
# must carry the harness-contract marker and its pieces. Do not add to this list - write
# the header instead.
HARNESS_GRANDFATHER = {
    "WA_TEST_spirits.txt", "WA_TEST_stats.txt", "WA_TEST_railway.txt",
    "WA_TEST_air_actors.txt", "WA_TEST_lend_lease_relief.txt",
    "WA_TEST_scope_isolation_effects.txt",
}


def check_harness_contract(rep: Report) -> None:
    """A measurement instrument must carry its own validity detector (wa-testing, contract v1).

    Fix 118 shipped on a reading from a harness whose call site poisoned every
    country-valued trigger; the context header (who/scope lines + a known-false control +
    the STOP rule) is the detector that caught it.
    """
    root = REPO / "common/scripted_effects"
    if not root.exists():
        return
    pieces = ("harness-contract: v1", "I-am-ROOT", "control-false", "STOP")
    for p in sorted(root.glob("WA_TEST_*.txt")):
        body = read(p)
        if pieces[0] not in body and p.name in HARNESS_GRANDFATHER:
            continue
        missing = [w for w in pieces if w not in body]
        if missing:
            rep.add("ERROR", "HARNESS-CONTRACT",
                    f"{p.name}: console harness without the v1 contract piece(s) "
                    f"{', '.join(repr(m) for m in missing)} - copy the context-header "
                    f"block from the wa-testing SKILL")


def check_bom(rep: Report) -> None:
    """No UTF-8 BOM where the parser is MEASURED to choke on it (AGENTS.md rule 16).

    The scripted_effects / scripted_triggers parser treats EF BB BF as a stray token and
    desyncs on every `=` / `}` after it - the whole file silently fails to load (seen
    2026-08-15 on WA_AI_CONSTRUCTION_PRIORITY_core.txt). The walk is DELIBERATELY narrow:
    213 vanilla-inherited BOMs elsewhere demonstrably run in campaigns. Widen only with a
    measurement showing another folder's parser chokes too.
    """
    for base in ("common/scripted_effects", "common/scripted_triggers"):
        root = REPO / base
        if not root.exists():
            continue
        for p in sorted(root.rglob("*.txt")):
            try:
                head = p.open("rb").read(3)
            except Exception:
                continue
            if head == b"\xef\xbb\xbf":
                rep.add("ERROR", "BOM-IN-SCRIPT",
                        f"{p.relative_to(REPO)}: starts with the UTF-8 BOM - the HOI4 "
                        f"parser will silently drop the whole file. Re-save as plain UTF-8")


def run_checks(rep: Report, today: datetime.date | None = None) -> None:
    check_work(rep, today)
    check_harness_contract(rep)
    check_bom(rep)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="WARN also fails")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="prove every rule still fires on a fixture built to break it")
    args = ap.parse_args()

    if args.selftest:
        import check_worklist_selftest
        return check_worklist_selftest.run(verbose=True)

    rep = Report()
    run_checks(rep)

    code = 1 if (rep.count("ERROR") or (args.strict and rep.count("WARN"))) else 0

    if args.json:
        print(json.dumps({"rows": rep.rows, "exit": code}, indent=2, ensure_ascii=False))
        return code

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for r in sorted(rep.rows, key=lambda r: (order[r["level"]], r["code"], r["message"])):
        print(f'{r["level"]:5s} {r["code"]:13s} {r["message"]}')
    print(f'\n{rep.count("ERROR")} ERROR, {rep.count("WARN")} WARN, {rep.count("INFO")} INFO')
    return code


if __name__ == "__main__":
    sys.exit(main())
