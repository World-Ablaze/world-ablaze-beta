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
  ERROR  FIX-UNREGISTERED a Fix NN used in the tree with no row in tools/fix_registry.json.
  ERROR  FIX-ORPHAN      a registry row cites a commit HEAD cannot reach.
  ERROR  FIX-UNRESOLVED  a registry row with no commit AND no note saying why.
  INFO   FIX-UNRESOLVED  no commit recoverable but the row carries a note - an accepted,
                        pre-convention loss. INFO because it is permanent by construction:
                        keeping it WARN trained readers to skim past warnings (2026-08-20).
  ERROR  NEVER-SCORED   never scored in ANY campaign although at least one campaign was
                        analysed after the item opened - a scoring opportunity was missed.
  INFO   AWAITING-CAMPAIGN never scored, but no campaign has been analysed since the item
                        opened: not scoreable yet, clears at the next campaign scoring.
                        Split from NEVER-SCORED 2026-08-20 - as one ERROR, every freshly
                        shipped fix kept the checker at exit 1, and a permanent failure is
                        a failure people learn to ignore.
  ERROR  LEDGER-MISSING an item with no machine-readable Ledger line.
  ERROR  LEDGER-MISMATCH the Ledger and the prose disagree on threshold or streak.
  WARN   STATUS-UNSET   nobody has ever written this item's status down.
  ERROR  CRITERION-UNSCOREABLE  a pass leg compares against a baseline outside the item and
                        carries no number: unscoreable in both directions, for ever.
  ERROR  PROBE-UNRUN    an item opened since the rule shipped with no pasted probe output:
                        nothing shows the probe command has ever been run.
  ERROR  HARNESS-CONTRACT a common/scripted_effects/WA_TEST_*.txt console harness without the v1
                        context header (marker, who/scope lines, known-false control, STOP rule -
                        wa-testing SKILL). The detector that caught the Fix 118 call-site
                        artefact, made mechanical; files shipped before 2026-08-20 are
                        grandfathered until QUEUE 21 rehomes or retires them.
  ERROR  BOM-IN-SCRIPT  a .txt under common/scripted_effects or common/scripted_triggers starting
                        with the UTF-8 BOM (EF BB BF). That parser desyncs on every token after
                        it and the whole file silently fails to load - a re-saved BOM once killed
                        the entire priority-construction system (AGENTS.md rule 16, mechanical).
                        Deliberately narrow: 213 vanilla-inherited BOMs elsewhere run fine.

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
FIX_REGISTRY = REPO / "tools/fix_registry.json"

# The day the PROBE-UNRUN rule shipped. Items opened before it are grandfathered - see
# the rule for why it cannot be applied backwards.
PROBE_OUTPUT_REQUIRED_FROM = "2026-08-19"

# Wordings that point at a value living outside the item.
EXTERNAL_BASELINE = re.compile(
    r"previous campaign|prior campaign|earlier campaign|envelope of the|"
    r"unchanged in shape from|same shape as the|baseline to beat", re.I)
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
    """[(id, body)] for every '### F<n>.' / '### R<n>.' heading.

    An item ends at the next item OR at the next top-level `## ` section - it does not run
    to the end of the file. The last item before the retirement ledger used to swallow the
    whole ledger, so every "merged into R51" in there was read as that item saying it had
    been merged. Caught 2026-08-18 when R71 became the last item and immediately reported
    SUPERSEDED on someone else's obituary.
    """
    parts = re.split(r"^### ((?:F|R)\d+)\.", text, flags=re.M)
    out = []
    for i in range(1, len(parts) - 1, 2):
        body = parts[i + 1]
        cut = re.search(r"^## ", body, re.M)
        out.append((parts[i], body[: cut.start()] if cut else body))
    return out


def registry_campaigns(text: str) -> list[str]:
    m = re.search(r"^## Campaign registry.*?$(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        return []
    return re.findall(r"^\|\s*`([0-9a-f]{6,})`", m.group(1), re.M)


def registry_dates(text: str) -> list[str]:
    """The 'Analysed' dates of the campaign registry - its rows end `| YYYY-MM-DD |`."""
    m = re.search(r"^## Campaign registry.*?$(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        return []
    return re.findall(r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*$", m.group(1), re.M)


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


def live_text(text: str) -> str:
    """The checklist minus the retirement ledger SECTION.

    Positional slicing was wrong twice. `index` caught the table of contents 34 lines in and
    left almost nothing live; `rindex` assumed the ledger is the last section, and R71 had
    been filed AFTER it - so R71 was silently outside every check that used the split. Cut the
    section itself: from its heading to the next top-level heading, or EOF.
    """
    m = re.search(r"^## Retired and merged items.*?(?=^## |\Z)", text, re.M | re.S)
    return text[: m.start()] + text[m.end():] if m else text


def field(body: str, name: str) -> str | None:
    # The label may carry a qualifier before the colon - R57 writes
    # "- **Probe (reads engine save fields; no WA_TLM metric):**". Requiring a bare
    # "- **Probe:**" reported that item as having no probe at all for as long as the
    # check existed, which is a false NO-PROBE on the one item that documents WHY it
    # has no WA_TLM metric.
    m = re.search(rf"^- \*\*{name}[^\*\n]*:?\*\*\s*(.*)$", body, re.M)
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
    opened_dates: dict[str, str] = {}

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

        # LEDGER
        # One line per item carrying the numbers a scoring session manipulates, so the
        # arithmetic stops depending on how the prose was phrased. It duplicates the prose
        # fields ON PURPOSE: the duplication is the cross-check, and a mismatch is reported.
        # `status` is COPIED from the prose, never derived. Deriving it was tried and
        # rejected 2026-08-18 - "streak > 0 = passing" mislabels every item whose history
        # carries a pre-fix baseline row, and each refinement moved the errors around
        # instead of removing them (7 wrong, then 6 wrong including 3 newly wrong). An item
        # whose prose never stated a status carries `status=UNSET` and is reported, because
        # the honest answer is that nobody has written it down.
        led = re.search(r"^- \*\*Ledger:\*\*\s*`([^`]*)`", body, re.M)
        if not led:
            rep.add("ERROR", "LEDGER-MISSING",
                    f"{iid}: no Ledger line - add one with class / threshold / streak / fix / status")
        else:
            kv = dict(re.findall(r"(\w+)=(\S+)", led.group(1)))
            if kv.get("status") == "UNSET":
                rep.add("WARN", "STATUS-UNSET",
                        f"{iid}: ledger status is UNSET - the item has never stated one in prose "
                        f"either, so no scoring session can say whether it is passing")
            for key, prose in (("threshold", field(body, "Threshold")),
                               ("streak", field(body, "Streak"))):
                want = re.search(r"-?\d+", prose or "")
                want = want.group() if want else "none"
                if kv.get(key, "none") != want:
                    rep.add("ERROR", "LEDGER-MISMATCH",
                            f"{iid}: ledger says {key}={kv.get(key)} but the prose line says "
                            f"{want} - one of the two was edited without the other")

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

        # CRITERION-UNSCOREABLE
        # A pass leg may only compare against a number that lives INSIDE the item. R60 leg 4
        # read "stay in the envelope of the previous campaign" with that envelope written
        # nowhere, and scored NOT TESTED on two consecutive campaigns - it could never have
        # scored anything else, in either direction. Naming a prior campaign is fine as long
        # as the leg also carries the value; what is not fine is a comparison with no number
        # at all, because the reader has nowhere to get it.
        pass_block = re.search(
            r"^- \*\*Pass[^" + chr(10) + r"]*\*\*(.*?)(?=^- \*\*(?:Probe|Threshold|Streak|Status|History))",
            body, re.M | re.S)
        if pass_block:
            for leg in re.findall(r"^\s{0,4}(?:\d+\.|-)\s.*?(?=^\s{0,4}(?:\d+\.|-)\s|\Z)",
                                  pass_block.group(1), re.M | re.S):
                m = EXTERNAL_BASELINE.search(leg)
                # "does the leg contain a digit anywhere" is not a test - "type-13" satisfies
                # it and the rule never fires. The value has to be AT the comparison, so look
                # for a number in the 200 characters that follow the phrase. That accepts
                # "Baseline to beat: `f9321934` 1946.8, ~8.9 levels" and R65's "unchanged in
                # shape from `7c7803a8` (iron ~25 -> ~48)", and rejects "the envelope of the
                # previous campaign (the skip gate keys on rail)".
                if m and not re.search(r"\d", leg[m.end(): m.end() + 200]):
                    rep.add("ERROR", "CRITERION-UNSCOREABLE",
                            f"{iid}: a pass leg compares against a baseline outside the item and "
                            f"carries no number - write the value in, or recut the leg to compare "
                            f"against this item's own History")

        # PROBE-UNRUN
        # A probe nobody has run is not a probe. `pc <TAG> --match corridor` sat in two
        # items for months and returns "(no projects matched)" for every tag and save,
        # because --match filters the building name and never the strategy tag; a session
        # scoring off it would have recorded a false FAIL. The only way to know a probe
        # command produces output BEFORE the campaign it is meant to score exists is to
        # run it against the pre-fix baseline and paste what came back.
        #
        # Applies to items opened on or after the day this rule shipped. It is not
        # retroactive: the baseline saves the older items were written against are not
        # all still on disk, so demanding their output now would be a demand to fabricate.
        opened = re.search(r"\*\*Opened (\d{4}-\d{2}-\d{2})\*\*", body)
        if opened:
            opened_dates[iid] = opened.group(1)
        if opened and opened.group(1) >= PROBE_OUTPUT_REQUIRED_FROM and "```" not in body:
            rep.add("ERROR", "PROBE-UNRUN",
                    f"{iid}: opened {opened.group(1)} with no fenced block - paste the probe's "
                    f"actual output (command + the lines it returned) so the next session knows "
                    f"the command runs and what shape the answer has")

        # DORMANT - measured here, reported once in aggregate below. One line per item
        # would be 27 lines of noise on a 43-item list, and a warning nobody can read is
        # a warning nobody acts on.
        idx = [i for i, c in enumerate(order) if any(c == h[1] for h in scored)]
        # None = never scored at all, which is a different thing from "scored long ago"
        # and must not be printed as a campaign count.
        dormancy[iid] = (len(order) - 1 - max(idx)) if idx else None

        # SUPERSEDED
        # The `\b` after the alternation used to end the pattern, so "superseded by R2" did
        # NOT match - a word boundary cannot sit between "R" and "2". Only "merged into R\d"
        # was doing any work. Found 2026-08-18 by the self-test, not by reading the line.
        if re.search(r"\b(superseded by|merged into)\s+(Fix\s*)?R?\d+", body, re.I):
            rep.add("WARN", "SUPERSEDED",
                    f"{iid}: says it is superseded/merged and is still present - fold it into "
                    f"the owning item and add a ledger row")

    # DORMANT, in aggregate. NOTE the checker cannot tell a full audit from a narrow
    # bug-hunt: a campaign that deliberately scored four items still counts as a campaign
    # here, so this number is an upper bound on real neglect, never a verdict per item.
    never = sorted(k for k, v in dormancy.items() if v is None)
    stale = {k: v for k, v in dormancy.items() if v is not None and v >= DORMANT_AFTER}
    # An item nobody COULD have scored yet is a different fact from an item everybody skipped.
    # `latest_analysed` = the newest analysis date the file knows (the registry's trailing
    # 'Analysed' column, plus history dates of scored-but-unregistered campaigns). An item
    # opened on or after that date has had no scoring opportunity - even a pre-fix baseline
    # row needs a campaign analysed after the item exists. With no date to compare against,
    # everything stays ERROR: "cannot prove it is waiting" must not silence the check.
    latest_analysed = max(registry_dates(text) + list(last_seen.values()), default="")
    waiting = sorted(k for k in never
                     if latest_analysed and opened_dates.get(k, "") >= latest_analysed)
    missed = sorted(set(never) - set(waiting))
    if missed:
        rep.add("ERROR", "NEVER-SCORED",
                f"{len(missed)} retireable item(s) never scored although at least one campaign "
                f"was analysed after they opened - they carry a threshold they cannot reach: "
                f"{', '.join(missed)}")
    if waiting:
        rep.add("INFO", "AWAITING-CAMPAIGN",
                f"{len(waiting)} item(s) opened on/after the last analysed campaign "
                f"({latest_analysed}), not scoreable yet: {', '.join(waiting)} - clears at the "
                f"next campaign scoring")
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
        # Comments are not write sites. A retirement note names the family it deleted
        # ("(WA_TLM_r74_ally_rail_* retired 2026-08-18 ...)"), and counting that as a write
        # keeps the probe orphaned forever - the check would flag the very comment that
        # records the fix. `#` starts a comment in PDXScript.
        code = re.sub(r"#.*", "", t)
        for m in re.finditer(r"WA_TLM_r(\d+)_\w+", code):
            seen.setdefault(m.group(1), str(p.relative_to(REPO)).replace("\\", "/"))
    # `r<NN>` in a WA_TLM name is the FIX number, not the checklist item number: Fix 99's
    # probe is `wa_tlm_r99_*` and its item is R64. So the consumer test is "does any item
    # still mention this token", not "does item R<NN> exist".
    #
    # The retirement ledger at the foot of the checklist is NOT a consumer. Its rows name the
    # retired item and its fix - "R46 Allies build logistics on an ally's soil (Fix 74)" - so a
    # whole-file search finds `r74_` and calls the probe live forever. That is exactly how the
    # r74 and r97 families kept writing for retired items until 2026-08-18: the check passed on
    # a mention in the obituary. Cut the ledger off before searching. Take the LAST occurrence
    # of the heading, not the first - the file opens with a table of contents that names it too.
    low = live_text(text).lower()
    # Token only. The old test also accepted a bare "fix NN" anywhere in the checklist, which
    # any passing narrative mention satisfies - and did: the live text says in so many words
    # "retired this session: R46 (Fix 74) ... instrumentation disposition recorded as a debt",
    # and the check still passed. Section 3.7 requires an item to name its probe family, so the
    # `r<NN>_` token IS the contract; a fix number in prose is not a consumer.
    for num, where in sorted(seen.items(), key=lambda kv: int(kv[0])):
        if f"r{num}_" not in low:
            rep.add("WARN", "TLM-ORPHAN",
                    f"Fix {num}: WA_TLM_r{num}_* still written ({where}) but no LIVE checklist "
                    f"item mentions it - retire the instrumentation or promote it (§3.7/§3.8)")


# Console harnesses shipped before the contract (2026-08-20). A new WA_TEST_*.txt scripted-effect
# file must carry the harness-contract marker and its pieces; these stay exempt until QUEUE 21
# rehomes or retires them. Do not add to this list - write the header instead.
HARNESS_GRANDFATHER = {
    "WA_TEST_spirits.txt", "WA_TEST_stats.txt", "WA_TEST_railway.txt",
    "WA_TEST_air_actors.txt", "WA_TEST_lend_lease_relief.txt",
    "WA_TEST_scope_isolation_effects.txt",
}


def check_harness_contract(rep: Report) -> None:
    """A measurement instrument must carry its own validity detector (wa-testing SKILL, contract v1).

    Fix 118 shipped on a reading from a harness whose call site poisoned every country-valued
    trigger; the context header (who/scope lines + a known-false control + the STOP rule) is the
    detector that caught it. The prose lesson alone did not prevent the class recurring - this
    makes the header mechanical for every harness written after 2026-08-20.
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
                    f"{', '.join(repr(m) for m in missing)} - copy the context-header block from "
                    f"the wa-testing SKILL (marker, who/scope lines, known-false control, STOP rule)")


def check_bom(rep: Report) -> None:
    """No UTF-8 BOM where the parser is MEASURED to choke on it (AGENTS.md rule 16, mechanical).

    The scripted_effects / scripted_triggers parser treats EF BB BF as a stray token and desyncs
    on every `=` / `}` after it, so the whole file silently fails to load. Seen 2026-08-15:
    WA_AI_CONSTRUCTION_PRIORITY_core.txt was re-saved with a BOM and the entire
    priority-construction system stopped parsing - no error, no crash, just absent behaviour.

    The walk is DELIBERATELY narrow. Measured 2026-08-20: 213 .txt files under common/ and
    events/ carry a BOM today (110 in common/units, ~97 vanilla-override event files) and their
    content demonstrably runs in campaigns - the engine tolerates the BOM in those folders, as
    vanilla's own files do. Flagging them would be 213 permanent ERRORs about working files.
    Widen this walk only with a measurement showing another folder's parser chokes too.
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
                        f"{p.relative_to(REPO)}: starts with the UTF-8 BOM - the HOI4 parser "
                        f"will silently drop the whole file. Re-save as plain UTF-8")


def check_fix_registry(rep: Report) -> None:
    """One fix number = one registry row = one commit that is on HEAD.

    Fix numbers are the only cross-reference this repo has between a code comment, a
    checklist item and the commit that introduced a behaviour. Nothing held them together:
    three items shipped carrying a literal `<FILL AT COMMIT>` placeholder that was never
    written back, and two of those commits can no longer be recovered from git at all
    because no commit message ever named the fix.
    """
    if not FIX_REGISTRY.exists():
        rep.add("WARN", "NO-FIX-REGISTRY", "tools/fix_registry.json absent")
        return
    reg = json.loads(read(FIX_REGISTRY))

    used: dict[str, str] = {}
    for base in ("common", "events", "documentation", ".claude", "tools"):
        root = REPO / base
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in (".txt", ".md", ".lua"):
                continue
            try:
                body = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            # The word boundaries are spelled out and the digit class is literal on purpose.
            # This line shipped once with a backspace byte where each boundary should have
            # been: it scanned 2,346 files, matched nothing, and reported a clean result.
            # A control with an invented Fix 999 is what caught it, not review.
            for m in re.finditer(r"\bFix ([0-9]{1,3})\b", body):
                used.setdefault(m.group(1), str(path.relative_to(REPO)).replace("\\", "/"))

    for num, where in sorted(used.items(), key=lambda kv: int(kv[0])):
        if num not in reg:
            rep.add("ERROR", "FIX-UNREGISTERED",
                    f"Fix {num}: used in {where} but absent from tools/fix_registry.json - "
                    f"a number nothing can resolve to a commit")

    for num, row in sorted(reg.items(), key=lambda kv: int(kv[0])):
        sha = row.get("commit")
        if not sha:
            if not row.get("note"):
                rep.add("ERROR", "FIX-UNRESOLVED",
                        f"Fix {num}: registry row has no commit and no note saying why")
            else:
                # INFO, not WARN: a noted, pre-convention loss is permanent by construction,
                # and a warning that can never be cleared is a warning readers learn to skim.
                rep.add("INFO", "FIX-UNRESOLVED",
                        f"Fix {num}: no implementing commit recoverable - {row['note'][:80]}")
        elif git_state(sha) == "orphan":
            rep.add("ERROR", "FIX-ORPHAN",
                    f"Fix {num}: registry cites {sha}, which git knows but HEAD cannot reach - "
                    f"the fix this number names is not in the build")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="WARN also fails")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--queue", action="store_true", help="QUEUE.md only")
    ap.add_argument("--selftest", action="store_true",
                    help="prove every rule still fires on a fixture built to break it")
    args = ap.parse_args()

    if args.selftest:
        import check_worklist_selftest
        return check_worklist_selftest.run(verbose=True)

    rep = Report()
    check_queue(rep)
    if not args.queue:
        check_checklist(rep)
        check_fix_registry(rep)
        check_harness_contract(rep)
        check_bom(rep)

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
