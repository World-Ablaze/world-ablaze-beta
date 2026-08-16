#!/usr/bin/env python3
"""
check_constants.py - the World Ablaze constants registry checker.

HOI4 `@` constants are FILE-SCOPED. The mod therefore redeclares the same
constant in several files (with "# must match <file>" comments), mirrors a few
engine defines (05_defines.lua) and building facts (00_buildings.txt) into
script constants / global variables, and mirrors script constants into the
savegame-analysis tables in savegame.py. Every one of those copies drifts
silently: the game never complains, the behaviour just splits.

This script is the single machine-checkable source of truth for those
contracts. The contracts themselves live in tools/constants_registry.json;
this file only knows how to read values out of the different file formats and
compare them.

    python tools/check_constants.py              # report, exit 1 on any ERROR
    python tools/check_constants.py --strict     # WARN also fails (dead WA_ decls)
    python tools/check_constants.py --json       # machine-readable report
    python tools/check_constants.py --markdown   # registry table for the skill
    python tools/check_constants.py --list       # every @ declaration it can see

What it reports
    ERROR  DRIFT        a registered mirror's value differs from its owner
    ERROR  MISSING      a registered owner/mirror is not declared where the
                        registry says it is (stale "must match" comment, or the
                        registry is stale - fix whichever is wrong)
    ERROR  UNREGISTERED the same @NAME is declared in several files with
                        DIFFERENT values and no registry group covers it
    WARN   UNREGISTERED the same @NAME is declared in several files with the
                        same value and no registry group covers it (an implicit
                        must-match contract nobody is checking - register it,
                        or list the files under "independent_paths")
    WARN   DEAD         a `@` declaration in a WA_* file that nothing in that
                        file reads (registered owners are exempt: they are the
                        reference point; mirrors are not - a mirror nobody
                        reads is a stale copy that will drift)
    INFO   DEAD         same, in a non-WA file (vanilla-derived content)
    INFO   ADVISORY     a group with "policy": "advisory" disagrees - the values
                        are conventionally equal but may diverge deliberately

Stdlib only. Run from anywhere; the repo root is derived from this file.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tools" / "constants_registry.json"

DECL_RE = re.compile(r"^\s*(@[A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\s#]+)")
NUM_RE = re.compile(r"^[-+]?(\d+(\.\d*)?|\.\d+)$")


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def read_text(path: Path) -> str:
    # utf-8-sig tolerates a BOM for READING only; AGENTS.md rule 16 says the
    # .txt files must not carry one, but that is a different checker's job.
    return path.read_text(encoding="utf-8-sig", errors="replace")


def strip_comment(line: str) -> str:
    return line.split("#", 1)[0]


def norm(value):
    """Numeric strings compare as numbers ('0.3' == '0.30'); others as text."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if NUM_RE.match(s):
        return float(s)
    return s


def same(a, b) -> bool:
    a, b = norm(a), norm(b)
    if isinstance(a, float) and isinstance(b, float):
        return abs(a - b) < 1e-9
    return a == b


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


# ----------------------------------------------------------------------------
# extractors - each returns (value, detail) ; value None = not found
# ----------------------------------------------------------------------------
def x_pdx_const(text: str, m: dict):
    name = m["name"]
    for i, line in enumerate(text.splitlines(), 1):
        d = DECL_RE.match(line)
        if d and d.group(1) == name:
            return d.group(2), f"line {i}"
    return None, "not declared"


def x_pdx_global(text: str, m: dict):
    pat = re.compile(r"set_variable\s*=\s*\{\s*global\." + re.escape(m["name"]) + r"\s*=\s*([^\s}]+)")
    for i, line in enumerate(text.splitlines(), 1):
        h = pat.search(strip_comment(line))
        if h:
            return h.group(1), f"line {i}"
    return None, "not set"


def _find_block(text: str, block: str):
    """Return (start, end) offsets of the body of the first `block = {` at any depth."""
    h = re.search(r"(?m)^\s*" + re.escape(block) + r"\s*=\s*\{", text)
    if not h:
        return None
    depth, i = 0, h.end() - 1
    while i < len(text):
        c = text[i]
        if c == "#":
            nl = text.find("\n", i)
            i = len(text) if nl < 0 else nl
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return h.end(), i
        i += 1
    return None


def x_pdx_block_key(text: str, m: dict):
    span = _find_block(text, m["block"])
    if not span:
        return None, f"block `{m['block']}` not found"
    body = text[span[0]:span[1]]
    # walk sub-blocks if key is dotted, e.g. "level_cap.state_max"
    keys = m["key"].split(".")
    for k in keys[:-1]:
        sub = _find_block(body, k)
        if not sub:
            return None, f"sub-block `{k}` not found in `{m['block']}`"
        body = body[sub[0]:sub[1]]
    pat = re.compile(r"(?m)^\s*" + re.escape(keys[-1]) + r"\s*=\s*([^\s#}]+)")
    for line in body.splitlines():
        h = pat.match(strip_comment(line))
        if h:
            return h.group(1), f"{m['block']}.{m['key']}"
    return None, f"key `{m['key']}` not found in `{m['block']}`"


def x_lua_define(text: str, m: dict):
    pat = re.compile(r"^\s*" + re.escape(m["name"]) + r"\s*=\s*([^\s,-]+)")
    for i, line in enumerate(text.splitlines(), 1):
        code = line.split("--", 1)[0]
        h = pat.match(code)
        if h:
            return h.group(1), f"line {i}"
    return None, "not defined"


def x_py_assign(text: str, m: dict):
    pat = re.compile(r"^" + re.escape(m["name"]) + r"\s*=\s*([^\s#]+)")
    for i, line in enumerate(text.splitlines(), 1):
        h = pat.match(line)
        if h:
            return h.group(1), f"line {i}"
    return None, "not assigned"


def _py_literal(text: str, name: str):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            try:
                return ast.literal_eval(node.value), node.lineno
            except ValueError:
                return None, node.lineno
    return None, None


def x_py_literal_has(text: str, m: dict):
    """Presence check inside a python literal: dict key, sequence item, or first
    element of a tuple item. Returns the expected value itself when present."""
    lit, ln = _py_literal(text, m["name"])
    if lit is None:
        return None, f"`{m['name']}` not found / not a literal"
    want = norm(m["value"])
    if isinstance(lit, dict):
        found = any(same(k, want) for k in lit)
    else:
        found = False
        for item in lit:
            if isinstance(item, (tuple, list)) and item and same(item[0], want):
                found = True
            elif same(item, want):
                found = True
    return (m["value"], f"line {ln}") if found else (None, f"{m['value']} absent from `{m['name']}` (line {ln})")


def x_regex(text: str, m: dict):
    """All captures of group 1 across the file must agree; that value is returned."""
    pat = re.compile(m["pattern"], re.M)
    hits = [(h.group(1), text.count("\n", 0, h.start()) + 1) for h in pat.finditer(text)]
    if not hits:
        return None, "pattern matched nothing"
    vals = {norm(v) for v, _ in hits}
    if len(vals) > 1:
        return None, "pattern matched INCONSISTENT values: " + ", ".join(f"{v}@{ln}" for v, ln in hits)
    return hits[0][0], f"{len(hits)} site(s), first line {hits[0][1]}"


EXTRACTORS = {
    "pdx_const": x_pdx_const,
    "pdx_global": x_pdx_global,
    "pdx_block_key": x_pdx_block_key,
    "lua_define": x_lua_define,
    "py_assign": x_py_assign,
    "py_literal_has": x_py_literal_has,
    "regex": x_regex,
}


def member_label(m: dict) -> str:
    kind = m["kind"]
    if kind == "pdx_block_key":
        what = f"{m['block']}.{m['key']}"
    elif kind == "regex":
        what = "regex " + m["pattern"][:40] + ("..." if len(m["pattern"]) > 40 else "")
    elif kind == "py_literal_has":
        what = f"{m['name']}[{m['value']}]"
    else:
        what = m["name"]
    return f"{m['file']} :: {what}"


def extract(m: dict, cache: dict):
    path = REPO / m["file"]
    if not path.exists():
        return None, "FILE MISSING"
    if path not in cache:
        cache[path] = read_text(path)
    return EXTRACTORS[m["kind"]](cache[path], m)


# ----------------------------------------------------------------------------
# scan all @ declarations
# ----------------------------------------------------------------------------
def scan_declarations(roots):
    """{name: [(relpath, line, value)]}, {relpath: text}"""
    decls = defaultdict(list)
    texts = {}
    for root in roots:
        for path in sorted((REPO / root).rglob("*.txt")):
            text = read_text(path)
            hit = False
            for i, line in enumerate(text.splitlines(), 1):
                d = DECL_RE.match(line)
                if d:
                    decls[d.group(1)].append((rel(path), i, d.group(2)))
                    hit = True
            if hit:
                texts[rel(path)] = text
    return decls, texts


def matches_any(relpath: str, globs) -> bool:
    return any(fnmatch.fnmatch(relpath, g) for g in globs)


# ----------------------------------------------------------------------------
# main check
# ----------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.items = []  # dicts: level, kind, msg, group

    def add(self, level, kind, msg, group=None):
        self.items.append({"level": level, "kind": kind, "msg": msg, "group": group})

    def count(self, level):
        return sum(1 for i in self.items if i["level"] == level)


def run(manifest: dict, strict: bool) -> tuple[Report, list]:
    rep = Report()
    cache = {}
    registered = defaultdict(set)   # (relpath, name) of every registered pdx_const member -> group ids
    owners = set()                  # (relpath, name) of owner pdx_const members
    resolved = []                   # for --markdown / --json

    for g in manifest["groups"]:
        gid = g["id"]
        policy = g.get("policy", "strict")
        owner = g["owner"]
        oval, odet = extract(owner, cache)
        row = {"id": gid, "policy": policy, "governs": g.get("governs", ""), "owner": member_label(owner),
               "value": oval, "mirrors": []}
        if owner["kind"] == "pdx_const":
            registered[(owner["file"], owner["name"])].add(gid)
            owners.add((owner["file"], owner["name"]))
        if oval is None:
            rep.add("ERROR", "MISSING", f"[{gid}] owner {member_label(owner)}: {odet}", gid)
        for m in g.get("mirrors", []):
            mval, mdet = extract(m, cache)
            if m["kind"] == "pdx_const":
                registered[(m["file"], m["name"])].add(gid)
            row["mirrors"].append({"label": member_label(m), "value": mval, "note": m.get("note", "")})
            if mval is None:
                rep.add("ERROR", "MISSING", f"[{gid}] mirror {member_label(m)}: {mdet}", gid)
            elif oval is not None and not same(oval, mval):
                if policy == "advisory":
                    rep.add("INFO", "ADVISORY", f"[{gid}] {member_label(m)} = {mval} vs owner {oval} ({owner['file']})", gid)
                else:
                    rep.add("ERROR", "DRIFT",
                            f"[{gid}] {member_label(m)} = {mval} but owner {member_label(owner)} = {oval}"
                            + (f" - {g['governs']}" if g.get("governs") else ""), gid)
        resolved.append(row)

    # ---- unregistered duplicates ------------------------------------------------
    decls, texts = scan_declarations(manifest.get("scan_roots", ["common", "events"]))
    indep = manifest.get("independent_paths", [])
    for name, sites in sorted(decls.items()):
        sites_f = [s for s in sites if not matches_any(s[0], indep)]
        files = {s[0] for s in sites_f}
        if len(files) < 2:
            continue
        unreg = [s for s in sites_f if (s[0], name) not in registered]
        if len({s[0] for s in unreg}) < 2 and all((s[0], name) in registered for s in sites_f):
            continue
        if not unreg:
            continue
        vals = {norm(s[2]) for s in sites_f}
        where = "; ".join(f"{p}:{ln}={v}" for p, ln, v in sites_f)
        if len(vals) > 1:
            rep.add("ERROR", "UNREGISTERED", f"{name} declared with DIFFERENT values and no registry group: {where}")
        else:
            rep.add("WARN", "UNREGISTERED", f"{name} declared in {len(files)} files, not registered (implicit must-match): {where}")

    # ---- dead declarations -----------------------------------------------------
    allow = {(a["file"], a["name"]): a.get("reason", "") for a in manifest.get("dead_allowlist", [])}
    for relpath, text in sorted(texts.items()):
        if matches_any(relpath, indep):
            continue
        lines = text.splitlines()
        names = {}
        for i, line in enumerate(lines, 1):
            d = DECL_RE.match(line)
            if d and d.group(1) not in names:
                names[d.group(1)] = i
        for name, ln in names.items():
            if (relpath, name) in owners or (relpath, name) in allow:
                continue
            pat = re.compile(re.escape(name) + r"(?![A-Za-z0-9_])")
            used = False
            for line in lines:
                d = DECL_RE.match(line)
                if d and d.group(1) == name:
                    continue
                if pat.search(strip_comment(line)):
                    used = True
                    break
            if not used:
                is_wa = Path(relpath).name.startswith(("WA_", "wa_"))
                mirror = (relpath, name) in registered
                lvl = "WARN" if is_wa else "INFO"
                tag = "DEAD" + ("-MIRROR" if mirror else "")
                rep.add(lvl, tag, f"{name} declared at {relpath}:{ln} but never read in that file")

    return rep, resolved


def to_markdown(resolved) -> str:
    out = ["<!-- GENERATED by `python tools/check_constants.py --markdown` from tools/constants_registry.json - do not hand-edit -->",
           "", "# Constants registry (generated)", "",
           "One row per synchronised group. **Owner** is the authoritative declaration; every **mirror** must carry the same value. "
           "`advisory` groups are conventionally equal but may diverge on purpose (the checker only reports INFO).", ""]
    out.append("| group | value | owner | mirrors | governs |")
    out.append("|---|---|---|---|---|")
    for r in resolved:
        mirrors = "<br>".join(f"`{m['label']}`" + (f" ({m['note']})" if m["note"] else "") for m in r["mirrors"]) or "-"
        pol = " *(advisory)*" if r["policy"] == "advisory" else ""
        out.append(f"| `{r['id']}`{pol} | `{r['value']}` | `{r['owner']}` | {mirrors} | {r['governs']} |")
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--repo", default=None, help="check another checkout (e.g. a `git archive` of HEAD) with this manifest")
    ap.add_argument("--strict", action="store_true", help="WARN also fails")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", action="store_true", help="print the registry table (for the skill reference)")
    ap.add_argument("--list", action="store_true", help="dump every @ declaration seen")
    ap.add_argument("-q", "--quiet", action="store_true", help="errors and warnings only")
    args = ap.parse_args(argv)
    if args.repo:
        global REPO
        REPO = Path(args.repo).resolve()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if args.list:
        decls, _ = scan_declarations(manifest.get("scan_roots", ["common", "events"]))
        for name, sites in sorted(decls.items()):
            for p, ln, v in sites:
                print(f"{name}\t{v}\t{p}:{ln}")
        return 0

    rep, resolved = run(manifest, args.strict)
    if args.markdown:
        sys.stdout.write(to_markdown(resolved))
        return 0
    if args.json:
        print(json.dumps({"groups": resolved, "findings": rep.items}, indent=1))
    else:
        order = {"ERROR": 0, "WARN": 1, "INFO": 2}
        for it in sorted(rep.items, key=lambda i: (order[i["level"]], i["kind"], i["msg"])):
            if args.quiet and it["level"] == "INFO":
                continue
            print(f"{it['level']:5} {it['kind']:12} {it['msg']}")
        print(f"\n{len(resolved)} groups checked - {rep.count('ERROR')} error(s), {rep.count('WARN')} warning(s), {rep.count('INFO')} info")
    fail = rep.count("ERROR") > 0 or (args.strict and rep.count("WARN") > 0)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
