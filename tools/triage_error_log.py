#!/usr/bin/env python3
"""
Triage a HOI4 error.log: separate the known-benign noise from what is actually ours.

WHY THIS EXISTS
---------------
A boot writes thousands of lines and almost all of them are one false-positive family, so a
real error is invisible. Measured 2026-08-18 on a 2.3 MB log: 662 distinct message shapes,
of which the top two accounted for 7,190 lines - and the 105 lines that mattered (a WA file
that had stopped parsing that morning) were 1.4% of the file.

The big family is `Invalid scope type for <trigger|effect> X in <file> line : N`. The engine
validates scripted effects and triggers at load time without knowing what scope they will
run in, so anything callable from two scopes reports here. It is noise. It is also 4,000+
lines a boot, which is why nobody reads this file.

WHAT IS ACTIONABLE
------------------
- `parser.cpp` - a file failed to parse. Always ours, always real. This is how a vendored
  markdown doc dropped into common/characters was caught.
- `root: Invalid Scope` - a scope wrapper that resolves to the wrong thing. Proven real:
  `visible = { ROOT = { ... } }` on the toolpack windows produced 3,531 of these plus 3,627
  paired character-lookup failures, and every other scripted GUI in the mod writes the same
  triggers bare.
- `tried to use character root as scope` - the paired half of the above.
- `Invalid name group` - a names file the engine could not use.
- Anything unrecognised. An unknown shape is reported as UNKNOWN, never assumed benign: the
  point of this tool is that a new error must not disappear into the noise.

USAGE
-----
    python tools/triage_error_log.py                 # the user's live error.log
    python tools/triage_error_log.py <path>          # a specific log
    python tools/triage_error_log.py <path> --all    # also list the benign families
"""

from __future__ import annotations

import collections
import os
import re
import sys

DEFAULT = os.path.expandvars(
    r"%USERPROFILE%/Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log"
)

LINE = re.compile(r"^\[[\d:]+\]\[([^\]]*)\]\[([^:\]]+)[^\]]*\]:\s*(.*)$")

# (name, pattern, verdict, why). First match wins, so order matters.
RULES = [
    # FIRST question: is it even our file. The launcher parses every installed mod's
    # descriptor, and two Workshop ones fail on a `thumbnail` token - they were landing in
    # ACTIONABLE as parse failures until this rule was moved above them (2026-08-18).
    ("other-mod", re.compile(r"in\s+file:\s*\"?mod/"), "BENIGN",
     "another mod's descriptor in the launcher's list, not ours"),

    # The engine writes parse failures TWO ways - "unexpected token in file: X" and
    # 'Error: "Unexpected token: <tok>, near line: N" in file: "X"'. Matching only the first
    # left the second in UNKNOWN, which is how the bucket earns its keep.
    ("parse-failure", re.compile(r"[Uu]nexpected token"), "ACTIONABLE",
     "a file failed to parse - the engine is not reading what you think it is"),
    ("root-scope", re.compile(r"root: Invalid Scope"), "ACTIONABLE",
     "a scope wrapper resolving to the wrong thing (the toolpack `visible = { ROOT = {` shape)"),
    ("character-root", re.compile(r"tried to use character root as scope"
                                  r"|Country is mandatory when setting character scope"), "ACTIONABLE",
     "paired with root-scope: the engine tried to read a character that is not there"),
    ("name-group", re.compile(r"Invalid name group"), "ACTIONABLE",
     "a names file the engine could not use"),
    ("missing-history", re.compile(r"is missing a history file"), "ACTIONABLE",
     "a country tag with no history file - it starts as whatever the engine defaults to"),

    ("missing-entity", re.compile(r"doesn't have an entity"), "ACTIONABLE",
     "a WA building with no 3D entity - cosmetic in play, but it is ours"),
    ("missing-token", re.compile(r"dynamic token that does not exist"), "ACTIONABLE",
     "a token something asked for and did not get"),

    ("other-mod", re.compile(r"in\s+file:\s*mod/|in file: \"mod/"), "BENIGN",
     "another mod's descriptor in the launcher's list, not ours"),
    ("separator", re.compile(r"^=+$|^no errors\.$"), "BENIGN",
     "section separators the engine writes between log blocks"),

    ("scope-validation", re.compile(r"Invalid scope type for (trigger|effect) "), "BENIGN",
     "load-time validation of scripted content, which does not know the runtime scope - "
     "anything callable from two scopes reports here"),
    ("texticon", re.compile(r"Couldnt find texticon"), "BENIGN",
     "a UI icon string with no art behind it - cosmetic"),
    ("duplicate-stat", re.compile(r"Duplicated equipment stat type"), "BENIGN",
     "the engine says it combines the values"),
]


def classify(msg: str):
    for name, pat, verdict, why in RULES:
        if pat.search(msg):
            return name, verdict, why
    return "unrecognised", "UNKNOWN", "not a shape this tool knows - triage it and add a rule"


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    show_all = "--all" in argv
    path = args[0] if args else DEFAULT
    if not os.path.exists(path):
        print(f"no such log: {path}", file=sys.stderr)
        return 2

    counts = collections.Counter()
    families = collections.defaultdict(collections.Counter)
    total = unparsed = 0
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        total += 1
        m = LINE.match(line)
        if not m:
            unparsed += 1
            continue
        msg = m.group(3)
        name, verdict, _why = classify(msg)
        counts[verdict] += 1
        # The site is what a reader acts on. A parse failure names its file in quotes and
        # repeats once per bad token, so key it on the FILE - otherwise 105 lines from one
        # broken file spread across a dozen rows and none of them looks urgent.
        key = None
        quoted = re.search(r'file:\s*"([^"]+)"', msg)
        if name == "parse-failure" and quoted:
            key = quoted.group(1)
        if key is None:
            site = re.search(r"((?:common|events|history|map)/\S+?):(\d+)", msg)
            key = f"{site.group(1)}:{site.group(2)}" if site else re.sub(r"\d+", "N", msg)[:90]
        families[verdict][(name, key)] += 1

    size = os.path.getsize(path)
    print(f"{path}\n{total} lines, {size/1024:.1f} KB"
          f"{f', {unparsed} not in the standard format' if unparsed else ''}\n")
    for verdict in ("ACTIONABLE", "UNKNOWN", "BENIGN"):
        n = counts[verdict]
        share = f"{100*n/total:.1f}%" if total else "-"
        print(f"{verdict:11} {n:>7} lines  {share:>6}")
    print()

    for verdict in ("ACTIONABLE", "UNKNOWN"):
        rows = families[verdict].most_common()
        if not rows:
            print(f"no {verdict} lines.")
            continue
        print(f"{verdict} - {len(rows)} site(s):")
        for (name, key), n in rows:
            print(f"  {n:>6}  [{name}] {key}")
        print()

    if show_all and families["BENIGN"]:
        print("BENIGN families (suppressed by default):")
        for (name, key), n in families["BENIGN"].most_common(20):
            print(f"  {n:>6}  [{name}] {key}")

    return 1 if counts["ACTIONABLE"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
