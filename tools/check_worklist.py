#!/usr/bin/env python3
"""
check_worklist.py - keeps the open work honest: QUEUE.md and the campaign checklist.

Two files decide what this project is working on, and both drift the same way: things
get added faster than they get closed, and nothing notices when an entry stops being
true. This checker makes that noticing mechanical.

    python tools/check_worklist.py            # report, exit 1 on any ERROR
    python tools/check_worklist.py --strict   # WARN also fails
    python tools/check_worklist.py --json     # machine-readable
    python tools/check_worklist.py --queue    # QUEUE.md only, fast

QUEUE.md
  ERROR  MULTI-ACTIVE   more than one ACTIVE entry - the scatter this file exists to stop
  ERROR  NO-ACTIVE      no ACTIVE entry while QUEUE is non-empty
  WARN   NO-EXIT        a QUEUE row with no "Closed when" - a wish, not a task

checklist.md - each of these is a real 2026-08-17 defect, made mechanical
  ERROR  ORPHAN-FIX     "Fix under test" cites a commit not reachable from HEAD. The fix
                        was reverted, renumbered or rebased away, so the item now tests
                        nothing. (R65/R66 named Fix 100/101 while the build carried Fix
                        102, which had REMOVED them.)
  ERROR  STATUS-STALE   Status says NOT YET TESTED / no campaign, but the history already
                        records a PASSED or FAILED. (8 items read like this at once.)
  ERROR  RETIRE-DUE     Streak >= Threshold: the skill says delete the item and its
                        instrumentation in the same session.
  WARN   DORMANT        not scored in the last N analysed campaigns - it is riding along
                        unprobed, and its streak means less every campaign.
  WARN   SUPERSEDED     the item says it is superseded/merged and is still here.
  WARN   TLM-ORPHAN     a WA_TLM_r<NN>_* write site (NN = the FIX number) that no live
                        checklist item mentions - telemetry writing for a dead consumer.
  WARN   NO-PROBE       a RETIREABLE item with no Probe line: unscoreable by construction.

Everything here is derived from the files as they are today - no restructuring required.
Where a field is absent the item is reported, never guessed at.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "QUEUE.md"
CHECKLIST = REPO / ".claude/skills/wa-campaign-checklist/references/checklist.md"
DORMANT_AFTER = 3          # campaigns
SCORED = ("PASSED", "FAILED")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


class Report:
    def __init__(self):
        self.rows: list[dict] = []

    def add(self, level, code, message):
        self.rows.append({"level": level, "code": code, "message": message})

    def count(self, lvl):
        return sum(1 for r in self.rows if r["level"] == lvl)


# --------------------------------------------------------------------------- QUEUE

def check_queue(rep: Report) -> None:
    if not QUEUE.exists():
        rep.add("WARN", "NO-QUEUE", "QUEUE.md absent - no work queue is being kept")
        return
    text = read(QUEUE)

    def section(name: str) -> str:
        m = re.search(rf"^## {name}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
        return m.group(1) if m else ""

    active = [l for l in section("ACTIVE").splitlines() if l.strip().startswith("- ")]
    rows = [l for l in section("QUEUE").splitlines()
            if l.strip().startswith("|") and not re.match(r"^\|[\s\-|]+\|$", l.strip())]
    rows = [r for r in rows if not re.search(r"\|\s*#\s*\|", r)]  # drop the header row

    if len(active) > 1:
        rep.add("ERROR", "MULTI-ACTIVE",
                f"QUEUE.md: {len(active)} ACTIVE entries - exactly one. Move the others to QUEUE "
                f"with their state, do not carry two subjects at once")
    elif not active and rows:
        rep.add("ERROR", "NO-ACTIVE", "QUEUE.md: no ACTIVE entry while QUEUE is non-empty")

    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[3]:
            label = cells[1][:48] if len(cells) > 1 else r.strip()[:48]
            rep.add("WARN", "NO-EXIT",
                    f'QUEUE.md: "{label}" has no "Closed when" - a wish, not a task')


# ----------------------------------------------------------------------- CHECKLIST

def split_items(text: str) -> list[tuple[str, str]]:
    """[(id, body)] for every '### F<n>.' / '### R<n>.' heading."""
    parts = re.split(r"^### ((?:F|R)\d+)\.", text, flags=re.M)
    return [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def registry_campaigns(text: str) -> list[str]:
    m = re.search(r"^## Campaign registry.*?$(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        return []
    return re.findall(r"^\|\s*`([0-9a-f]{6,})`", m.group(1), re.M)


def git_state(sha: str) -> str:
    """'ok' reachable from HEAD | 'orphan' a real commit that is not | 'unknown' not a commit."""
    try:
        r = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"],
                           cwd=REPO, capture_output=True)
        if r.returncode != 0:
            return "unknown"
        r = subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"],
                           cwd=REPO, capture_output=True)
        return "ok" if r.returncode == 0 else "orphan"
    except Exception:
        return "ok"   # no git available: do not invent failures


def history_lines(body: str) -> list[tuple[str, str, str]]:
    """[(date, campaign_id, the rest of ITS OWN line)].

    The verdict is read from the history line itself, never from a byte window around the
    campaign id: the same id also appears in Status prose, and a window opened there picks
    up the wrong verdict or none at all - which silently hid R64 from the STATUS-STALE check
    on the first run of this checker.
    """
    out = []
    m = re.search(r"^- \*\*History:?\*\*\s*$(.*)", body, re.M | re.S)
    scope = m.group(1) if m else body
    for line in scope.splitlines():
        h = re.match(r"\s+- (\d{4}-\d\d-\d\d) · `?([0-9a-f]{6,})`?(.*)", line)
        if h:
            out.append((h.group(1), h.group(2), h.group(3)))
    return out


def field(body: str, name: str) -> str | None:
    m = re.search(rf"^- \*\*{name}:?\*\*\s*(.*)$", body, re.M)
    return m.group(1).strip() if m else None


def check_checklist(rep: Report) -> None:
    if not CHECKLIST.exists():
        rep.add("WARN", "NO-CHECKLIST", "checklist.md absent")
        return
    text = read(CHECKLIST)
    items = split_items(text)
    all_campaigns = registry_campaigns(text)
    seen_campaigns: set[str] = set()
    dormancy: dict[str, int] = {}

    # Campaign order = the registry, then anything scored in histories but never registered,
    # placed by the latest date it was scored on. Those extras are by construction the newest
    # campaigns, and leaving them out makes every item scored only in them read as dormant.
    last_seen: dict[str, str] = {}
    for _, b in items:
        for date, cid, _ in history_lines(b):
            last_seen[cid] = max(last_seen.get(cid, ""), date)
    extra = sorted(set(last_seen) - set(all_campaigns), key=lambda c: last_seen[c])
    order = all_campaigns + extra

    for iid, body in items:
        fundamental = iid.startswith("F")

        # ORPHAN-FIX
        fut = field(body, "Fix under test")
        if fut:
            for sha in set(re.findall(r"`([0-9a-f]{7,40})`", fut)):
                # A campaign id is 8 hex and lives in the registry - not a commit.
                if any(c.startswith(sha) or sha.startswith(c) for c in all_campaigns):
                    continue
                st = git_state(sha)
                if st == "orphan":
                    rep.add("ERROR", "ORPHAN-FIX",
                            f"{iid}: 'Fix under test' cites {sha}, a commit git knows but that is "
                            f"NOT reachable from HEAD - rebased away, reverted or on another "
                            f"branch, so this item tests code the build does not carry")
                elif st == "unknown":
                    rep.add("WARN", "UNKNOWN-REF",
                            f"{iid}: 'Fix under test' cites {sha}, which is neither a commit git "
                            f"knows nor a campaign in the registry - dead reference")

        # STATUS-STALE
        status = field(body, "Status") or ""
        hist = history_lines(body)
        scored = [h for h in hist if any(w in h[2] for w in SCORED)]
        seen_campaigns.update(h[1] for h in hist)
        if status and re.search(r"NOT YET TESTED|no campaign", status, re.I) and scored:
            rep.add("ERROR", "STATUS-STALE",
                    f"{iid}: Status still says NOT YET TESTED, but the history records "
                    f"{len(scored)} scored campaign(s) - the field was never refreshed")

        if fundamental:
            continue

        # RETIRE-DUE
        thr, stk = field(body, "Threshold"), field(body, "Streak")
        mt = re.search(r"\d+", thr or "")
        ms = re.search(r"\d+", stk or "")
        if mt and ms and int(ms.group()) >= int(mt.group()):
            rep.add("ERROR", "RETIRE-DUE",
                    f"{iid}: streak {ms.group()} >= threshold {mt.group()} - delete the item AND "
                    f"its instrumentation, add a ledger row (wa-campaign-checklist SKILL.md)")

        # NO-PROBE
        if field(body, "Probe") is None:
            rep.add("WARN", "NO-PROBE",
                    f"{iid}: no Probe line - nothing tells a scoring session how to measure it")

        # DORMANT - measured here, reported once in aggregate below. One line per item
        # would be 27 lines of noise on a 43-item list, and a warning nobody can read is
        # a warning nobody acts on.
        idx = [i for i, c in enumerate(order) if any(c == h[1] for h in scored)]
        # None = never scored at all, which is a different thing from "scored long ago"
        # and must not be printed as a campaign count.
        dormancy[iid] = (len(order) - 1 - max(idx)) if idx else None

        # SUPERSEDED
        if re.search(r"\bsuperseded by (Fix|R)\b|\bmerged into R\d", body, re.I):
            rep.add("WARN", "SUPERSEDED",
                    f"{iid}: says it is superseded/merged and is still present - fold it into "
                    f"the owning item and add a ledger row")

    # DORMANT, in aggregate. NOTE the checker cannot tell a full audit from a narrow
    # bug-hunt: a campaign that deliberately scored four items still counts as a campaign
    # here, so this number is an upper bound on real neglect, never a verdict per item.
    never = sorted(k for k, v in dormancy.items() if v is None)
    stale = {k: v for k, v in dormancy.items() if v is not None and v >= DORMANT_AFTER}
    if never:
        rep.add("ERROR", "NEVER-SCORED",
                f"{len(never)} retireable item(s) have never been scored in ANY campaign - "
                f"they carry a threshold they cannot reach: {', '.join(never)}")
    if stale:
        worst = sorted(stale.items(), key=lambda kv: -kv[1])[:5]
        rep.add("WARN", "DORMANT",
                f"{len(stale)} of {len(dormancy)} retireable items not scored in the last "
                f"{DORMANT_AFTER} campaigns ({', '.join(order[-DORMANT_AFTER:])}); longest "
                f"gap " + ", ".join(f"{k} ({v} campaigns)" for k, v in worst) +
                ". A narrow bug-hunt counts as a campaign here, so this is an upper bound")

    # REGISTRY-MISSING
    for cid in sorted(seen_campaigns - set(all_campaigns)):
        rep.add("ERROR", "REGISTRY-MISSING",
                f"campaign {cid} is scored {text.count(cid)}x in item histories but is absent "
                f"from the 'Campaign registry' table - every dormancy reading computed against "
                f"that table is off by a campaign")

    # TLM-ORPHAN
    seen: dict[str, str] = {}
    for p in list((REPO / "common").rglob("*.txt")) + list((REPO / "events").rglob("*.txt")):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in re.finditer(r"WA_TLM_r(\d+)_\w+", t):
            seen.setdefault(m.group(1), str(p.relative_to(REPO)).replace("\\", "/"))
    # `r<NN>` in a WA_TLM name is the FIX number, not the checklist item number: Fix 99's
    # probe is `wa_tlm_r99_*` and its item is R64. So the consumer test is "does any item
    # still mention this token", not "does item R<NN> exist".
    low = text.lower()
    for num, where in sorted(seen.items(), key=lambda kv: int(kv[0])):
        if f"r{num}_" not in low and f"fix {num}" not in low:
            rep.add("WARN", "TLM-ORPHAN",
                    f"Fix {num}: WA_TLM_r{num}_* still written ({where}) but no checklist item "
                    f"mentions it - retire the instrumentation or promote it (§3.7/§3.8)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="WARN also fails")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--queue", action="store_true", help="QUEUE.md only")
    args = ap.parse_args()

    rep = Report()
    check_queue(rep)
    if not args.queue:
        check_checklist(rep)

    code = 1 if (rep.count("ERROR") or (args.strict and rep.count("WARN"))) else 0

    if args.json:
        print(json.dumps({"rows": rep.rows, "exit": code}, indent=2, ensure_ascii=False))
        return code

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for r in sorted(rep.rows, key=lambda r: (order[r["level"]], r["code"], r["message"])):
        print(f'{r["level"]:5s} {r["code"]:13s} {r["message"]}')
    print(f'\n{rep.count("ERROR")} ERROR, {rep.count("WARN")} WARN')
    return code


if __name__ == "__main__":
    sys.exit(main())
