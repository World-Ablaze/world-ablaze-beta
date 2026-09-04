#!/usr/bin/env python3
"""Audit / plan / apply the naming convention of `common/ai_equipment/`.

Convention (full text: documentation/AI_EQUIPMENT_NAMING.md):

  design GROUP key  = <OWNER>_<role_slug>[_<qualifier>]
      OWNER      = upper-case tag of the tech-tree owner (file prefix), or `generic`
      role_slug  = the group's single `roles` entry minus its `land_`/`air_`/`naval_` prefix
      qualifier  = only when the same file carries two groups on one role
  design key        = <type>[__<qualifier>]
      type       = exactly the design's `target_variant.type`
      qualifier  = only when the group carries two designs on one type;
                   closed vocabulary (QUALIFIERS below) or an ordinal `v2`, `v3`, ...
  every design key line carries `# <display name>` (the type's localisation)

Commands:
  audit  (default)  report every violation, exit 1 if any ERROR
  plan              print the rename map (designs, groups, comments) without writing
  apply             rewrite the files in place (keys, WA_EQUIPGEN marker ids, comments)

  --no-groups       leave group keys alone (designs + comments only)
  --json PATH       also write the plan as JSON
  --root PATH       mod root (default: parent of this file's directory)

The file is rewritten by byte spans so indentation, comments, CRLF and the
WA_EQUIPGEN owned blocks are preserved. Marker ids embed
`<country>_<group>_<design>_<kind>_...` (equipment_evaluator/emit.py `_marker_id`),
so they are rewritten with the keys; otherwise the evaluator would report every
owned block as a conflict.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

GROUP_META = {"category", "blocked_for", "available_for", "roles", "priority",
              "allowed_modules", "requirements", "target_variant", "enable"}
ROLE_DOMAIN_RE = re.compile(r"^(land|air|naval)_")
# old-name suffix -> qualifier, used only when a type carries several designs
QUALIFIERS = {
    "cc": "cutting-corners module fit (WA_AI_EQUIPMENT_should_mount_cutting_corners)",
    "lr": "long-range fit",
    "aa": "anti-air refit",
    "atk": "ground-attack fit",
    "int": "interceptor fit",
    "conv": "conversion of an older airframe",
}
OLD_SUFFIX_TO_QUALIFIER = {
    "_cc": "cc", "_lr": "lr", "_aa_upgrade": "aa", "_aa": "aa",
    "_attacker": "atk", "_interceptor": "int", "_conversion": "conv",
}
DESIGN_KEY_RE = re.compile(r"^[A-Za-z0-9_]+(__(?:[a-z]+|v\d+))?$")


# ----------------------------------------------------------------------------
# positional parser (comments skipped, offsets kept)
# ----------------------------------------------------------------------------
TOKEN_RE = re.compile(r"#[^\r\n]*|[^\s{}=<>#]+|[{}=<>]")


def tokenize(text):
    toks = []
    for m in TOKEN_RE.finditer(text):
        if m.group(0).startswith("#"):
            continue
        toks.append((m.group(0), m.start(), m.end()))
    return toks


def parse(toks):
    """Return nested list of (key, key_span, op, value|children, body_span)."""
    pos = 0

    def block():
        nonlocal pos
        items = []
        while pos < len(toks):
            tok, s, e = toks[pos]
            if tok == "}":
                pos += 1
                return items, e
            key, kspan = tok, (s, e)
            pos += 1
            if pos < len(toks) and toks[pos][0] in ("=", "<", ">"):
                op = toks[pos][0]
                pos += 1
                if pos < len(toks) and toks[pos][0] == "{":
                    open_at = toks[pos][1]
                    pos += 1
                    children, close = block()
                    items.append((key, kspan, op, children, (open_at, close)))
                else:
                    v, vs, ve = toks[pos]
                    pos += 1
                    items.append((key, kspan, op, v, (vs, ve)))
            else:
                items.append((key, kspan, None, None, kspan))
        return items, (toks[-1][2] if toks else 0)

    items, _ = block()
    return items


class Design:
    def __init__(self, name, kspan, body_span, dtype, comment):
        self.name, self.kspan, self.body_span = name, kspan, body_span
        self.type, self.comment = dtype, comment
        self.new_name = name


class Group:
    def __init__(self, name, kspan, body_span):
        self.name, self.kspan, self.body_span = name, kspan, body_span
        self.roles, self.available_for, self.blocked_for = [], [], []
        self.designs = []
        self.new_name = name


class ModFile:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as fh:
            raw = fh.read()
        self.bom = raw.startswith(b"\xef\xbb\xbf")
        self.text = raw.decode("utf-8-sig")
        self.owner = os.path.basename(path).split("_")[0]  # GER / generic
        self.groups = []
        for key, kspan, op, val, bspan in parse(tokenize(self.text)):
            if not isinstance(val, list):
                continue
            g = Group(key, kspan, bspan)
            for k2, ks2, o2, v2, bs2 in val:
                if k2 == "roles" and isinstance(v2, list):
                    g.roles = [x[0] for x in v2]
                elif k2 == "available_for" and isinstance(v2, list):
                    g.available_for = [x[0] for x in v2]
                elif k2 == "blocked_for" and isinstance(v2, list):
                    g.blocked_for = [x[0] for x in v2]
                elif isinstance(v2, list) and k2 not in GROUP_META:
                    dtype = None
                    for k3, _, _, v3, _ in v2:
                        if k3 == "target_variant" and isinstance(v3, list):
                            for k4, _, _, v4, _ in v3:
                                if k4 == "type":
                                    dtype = v4
                    g.designs.append(Design(k2, ks2, bs2, dtype, self._comment_after(bs2[0])))
            self.groups.append(g)

    def _comment_after(self, brace_pos):
        line_end = self.text.find("\n", brace_pos)
        if line_end < 0:
            line_end = len(self.text)
        rest = self.text[brace_pos + 1:line_end]
        m = re.match(r"[ \t]*#[ \t]*(.*?)[ \t\r]*$", rest)
        return m.group(1) if m else None


# ----------------------------------------------------------------------------
# localisation lookup for the display-name comment
# ----------------------------------------------------------------------------
def load_localisation(root):
    loc = {}
    pat = re.compile(r'\s*([A-Za-z0-9_.\-]+):\d*\s*"(.*)"')
    for f in glob.glob(os.path.join(root, "localisation", "**", "*_l_english.yml"), recursive=True):
        with open(f, encoding="utf-8-sig", errors="replace") as fh:
            for line in fh:
                m = pat.match(line)
                if m and m.group(1) not in loc:
                    loc[m.group(1)] = _ascii(m.group(2).replace("`", "'"))
    return loc


def _ascii(text):
    """Comments stay 7-bit: the script files are BOM-free UTF-8 and the parser
    ignores comments, but a plain-ASCII display name reads the same everywhere."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


# ----------------------------------------------------------------------------
# naming rules
# ----------------------------------------------------------------------------
def role_slug(role):
    return ROLE_DOMAIN_RE.sub("", role)


def target_group_name(mf, g, twins):
    """<OWNER>_<role_slug>[_<qualifier>]; qualifier from the old name's extra words."""
    if len(g.roles) != 1:
        return g.name
    owner = mf.owner.upper() if mf.owner != "generic" else "generic"
    slug = role_slug(g.roles[0])
    if twins.get(g.roles[0], 0) > 1:
        old = re.sub(r"^([A-Za-z]{3}|generic)_", "", g.name)
        old_words = [w for w in old.split("_") if w and w not in ("naval", "tanks", "tank")]
        role_words = set(slug.split("_"))
        extra = [w for w in old_words if w.rstrip("s") not in role_words]
        if extra:
            slug = slug + "_" + "_".join(extra)
    return f"{owner}_{slug}"


def target_design_names(g):
    """Assign <type>[__qualifier] inside one group, file order."""
    by_type = defaultdict(list)
    for d in g.designs:
        by_type[d.type].append(d)
    for dtype, ds in by_type.items():
        if dtype is None:
            continue
        if len(ds) == 1:
            ds[0].new_name = dtype
            continue
        used = set()
        ordinal = 2
        for i, d in enumerate(ds):
            qual = None
            if "__" in d.name:  # already on the convention: keep its qualifier
                q = d.name.split("__", 1)[1]
                if q in QUALIFIERS or re.match(r"^v\d+$", q):
                    qual = q
            for suf, q in OLD_SUFFIX_TO_QUALIFIER.items():
                if qual is None and d.name.endswith(suf):
                    qual = q
                    break
            if qual is None and i == 0:
                d.new_name = dtype
                used.add("")
                continue
            if qual is None or qual in used:
                while f"v{ordinal}" in used:
                    ordinal += 1
                qual = f"v{ordinal}"
                ordinal += 1
            used.add(qual)
            d.new_name = f"{dtype}__{qual}"
        if "" not in used:  # every design carried a suffix: promote the first to bare
            ds[0].new_name = dtype


def audit(files, loc):
    errors, warns = [], []
    for mf in files:
        role_count = Counter(r for g in mf.groups for r in g.roles)
        for g in mf.groups:
            where = f"{os.path.basename(mf.path)}:{g.name}"
            if not re.match(r"^([A-Z]{3}|generic)_", g.name):
                errors.append(("G1-PREFIX", where, "group key must start with <TAG>_ or generic_"))
            elif g.available_for and g.name[:3] != "gen" and g.name[:3] not in g.available_for:
                errors.append(("G1-OWNER", where, f"prefix {g.name[:3]} not in available_for"))
            if len(g.roles) != 1:
                errors.append(("G2-ROLE", where, f"group must declare exactly one role, has {g.roles}"))
            else:
                want = target_group_name(mf, g, role_count)
                if g.name != want:
                    errors.append(("G3-SLUG", where, f"expected {want}"))
            seen = Counter(d.name for d in g.designs)
            for name, n in seen.items():
                if n > 1:
                    errors.append(("D1-DUP", f"{where}.{name}", f"key defined {n} times in one group"))
            for d in g.designs:
                dw = f"{where}.{d.name}"
                if d.type is None:
                    errors.append(("D0-TYPE", dw, "no target_variant.type"))
                    continue
                base = d.name.split("__", 1)[0]
                if base != d.type or not DESIGN_KEY_RE.match(d.name):
                    errors.append(("D2-KEY", dw, f"key must be {d.type} or {d.type}__<qualifier>"))
                elif "__" in d.name:
                    q = d.name.split("__", 1)[1]
                    if q not in QUALIFIERS and not re.match(r"^v\d+$", q):
                        errors.append(("D2-QUAL", dw, f"qualifier '{q}' not in vocabulary {sorted(QUALIFIERS)} / vN"))
                if not d.comment:
                    warns.append(("D3-COMMENT", dw, f"missing '# {loc.get(d.type, '?')}'"))
    return errors, warns


def build_plan(files, loc, rename_groups=True):
    plan = {"groups": [], "designs": [], "comments": []}
    for mf in files:
        role_count = Counter(r for g in mf.groups for r in g.roles)
        for g in mf.groups:
            if rename_groups:
                g.new_name = target_group_name(mf, g, role_count)
                if g.new_name != g.name:
                    plan["groups"].append({"file": os.path.basename(mf.path), "old": g.name, "new": g.new_name})
            target_design_names(g)
            for d in g.designs:
                if d.new_name != d.name:
                    plan["designs"].append({"file": os.path.basename(mf.path), "group": g.name,
                                            "old": d.name, "new": d.new_name, "type": d.type,
                                            "name": loc.get(d.type)})
                if not d.comment and d.type in loc:
                    plan["comments"].append({"file": os.path.basename(mf.path), "group": g.name,
                                             "design": d.new_name, "comment": loc[d.type]})
    # cross-file uniqueness of the new design keys (informational)
    cnt = Counter()
    for mf in files:
        for g in mf.groups:
            for d in g.designs:
                cnt[d.new_name] += 1
    plan["shared_keys_after"] = sorted(k for k, n in cnt.items() if n > 1)
    return plan


MARKER_RE = re.compile(r"WA_EQUIPGEN_(BEGIN|END) id=(\S+)")


def rewrite_file(mf, loc):
    """Apply new group/design keys, marker ids and missing comments by spans."""
    edits = []  # (start, end, replacement)
    for g in mf.groups:
        if g.new_name != g.name:
            edits.append((g.kspan[0], g.kspan[1], g.new_name))
        for d in g.designs:
            if d.new_name != d.name:
                edits.append((d.kspan[0], d.kspan[1], d.new_name))
            if not d.comment and d.type in loc:
                edits.append((d.body_span[0] + 1, d.body_span[0] + 1, f" # {loc[d.type]}"))
        # marker ids inside this group's body (only when a key actually changes)
        if g.new_name == g.name and all(d.new_name == d.name for d in g.designs):
            continue
        body = mf.text[g.body_span[0]:g.body_span[1]]
        for m in MARKER_RE.finditer(body):
            mid = m.group(2)
            for d in g.designs:
                for kind in ("priority_factor", "supersede", "chain_guard", "retain_gate",
                             "hold_gate", "reject_design", "module"):
                    old_prefix = f"{mf.owner}_{g.name}_{d.name}_{kind}"
                    if mid == old_prefix or mid.startswith(old_prefix + "_"):
                        new_prefix = f"{mf.owner}_{g.new_name}_{d.new_name}_{kind}"
                        s = g.body_span[0] + m.start(2)
                        edits.append((s, s + len(old_prefix), new_prefix))
                        break
                else:
                    continue
                break
    edits.sort(key=lambda e: e[0])
    out, cur = [], 0
    for s, e, rep in edits:
        assert s >= cur, "overlapping edits"
        out.append(mf.text[cur:s])
        out.append(rep)
        cur = e
    out.append(mf.text[cur:])
    new_text = "".join(out)
    with open(mf.path, "wb") as fh:
        fh.write((b"\xef\xbb\xbf" if mf.bom else b"") + new_text.encode("utf-8"))
    return len(edits)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="audit", choices=["audit", "plan", "apply"])
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--no-groups", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--limit", type=int, default=25, help="rows shown per plan section")
    args = ap.parse_args(argv)

    paths = sorted(glob.glob(os.path.join(args.root, "common", "ai_equipment", "*.txt")))
    files = [ModFile(p) for p in paths]
    loc = load_localisation(args.root)

    if args.command == "audit":
        errors, warns = audit(files, loc)
        by_rule = Counter(e[0] for e in errors)
        for e in errors[: args.limit]:
            print(f"ERROR {e[0]:12s} {e[1]}: {e[2]}")
        if len(errors) > args.limit:
            print(f"... {len(errors) - args.limit} more errors")
        for w in warns[: max(0, args.limit - len(errors))]:
            print(f"WARN  {w[0]:12s} {w[1]}: {w[2]}")
        print(f"\nfiles {len(files)}, groups {sum(len(f.groups) for f in files)}, "
              f"designs {sum(len(g.designs) for f in files for g in f.groups)}")
        print("errors by rule:", dict(sorted(by_rule.items())), "| warnings:", len(warns))
        return 1 if errors else 0

    plan = build_plan(files, loc, rename_groups=not args.no_groups)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, indent=1, ensure_ascii=False)
    print(f"group renames  : {len(plan['groups'])}")
    for r in plan["groups"][: args.limit]:
        print(f"  {r['file']:16s} {r['old']:36s} -> {r['new']}")
    print(f"design renames : {len(plan['designs'])}")
    for r in plan["designs"][: args.limit]:
        print(f"  {r['file']:16s} {r['group']:28s} {r['old']:32s} -> {r['new']:44s} # {r['name']}")
    print(f"comments added : {len(plan['comments'])}")
    print(f"design keys shared by >1 group after rename: {len(plan['shared_keys_after'])}")
    if args.command == "plan":
        return 0
    total = 0
    for mf in files:
        total += rewrite_file(mf, loc)
    print(f"applied {total} edits to {len(files)} files")
    files = [ModFile(p) for p in paths]
    errors, warns = audit(files, loc)
    print(f"post-apply audit: {len(errors)} errors, {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
