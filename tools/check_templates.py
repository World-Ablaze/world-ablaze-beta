#!/usr/bin/env python3
"""Mechanical integrity check of the AI division-template selection chain.

The chain has three links and every one of them fails SILENTLY in game:

    WA_AI_TEMPLATES_calculate_*_template   picks an integer  (scripted_effects)
        -> WA_<TYPE>_TEMPLATE country flag holding that integer
            -> the one ai_template entry whose `enable` reads that flag value

A calculator that writes a value no ai_template answers leaves the country with a
flag nobody reads, so it keeps its previous template for the rest of the campaign.
Nothing is logged. The `armor-ladder-integrity` subject found four such pairs by
hand; this script is that audit made permanent.

Checks, each identified by the tag printed on its line:

  VALUE-NO-TEMPLATE    ERROR  calculator writes N, no ai_template enables on N
  TEMPLATE-NO-VALUE    WARN   ai_template enables on N, no calculator writes N
  DUP-CONDITION        ERROR  two branches of one chain share an identical condition set
  UNREACHABLE-BRANCH   ERROR  branch k implies an earlier branch j, so k never runs
  DUP-TEMPLATE-NAME    ERROR  two entries share a name inside one role group
  SLOT-SUFFIX-MISMATCH ERROR  a unit whose name suffix does not match the slot it sits in
  ELSE-SEPARATED       WARN   an else/else_if separated from its if by other statements
  NO-DIRECT-EFFECT     WARN   an if/else block whose body holds no effect of its own
  CLAIM-GUARD-MISSING  ERROR  a branch of a claim-cascade calculator without its guard

Usage, from the repo root:
    python tools/check_templates.py            # exit 1 on any ERROR
    python tools/check_templates.py --strict   # exit 1 on any ERROR or WARN
    python tools/check_templates.py --verbose  # also print the reachable-value map
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EFFECTS = REPO / "common" / "scripted_effects" / "WA_AI_TEMPLATES_effects.txt"
LOC = REPO / "common" / "scripted_localisation" / "WA_AI_templates_scripted_loc.txt"
TEMPLATE_DIR = REPO / "common" / "ai_templates"

# The two value-rewriting effects the calculators call. Each turns one written value N into a
# second reachable value; a checker that ignores them reports every mirror target as orphaned.
#   +100 : WA_AI_TEMPLATES_apply_motorized_hospital_mirror   [mot-field-hospital]
#   +500 : add_to_temp_variable = { _template_value = _tier_offset }   [modern-chassis-tier]
HOSPITAL_MIRROR_EFFECT = "WA_AI_TEMPLATES_apply_motorized_hospital_mirror"
HOSPITAL_MIRROR_OFFSET = 100
TIER_OFFSET = 500

# A unit name carries the slot it belongs to as its last word, and the convention holds without a
# single exception across common/ai_templates (measured 2026-08-29: 278/278 `_line` in `regiments`,
# 206/206 `_regimental`, 911/911 `_divisional`). A mismatch is a copy-paste that the engine accepts
# and quietly drops, which is how a line battalion ended up in a divisional support slot.
SLOT_SUFFIX = {
    "regiments": "line",
    "regimental_support": "regimental",
    "support": "divisional",
}

# Tokens that separate a key from its value in PDXScript. `>` and `<` matter here: consuming them
# as if they were the value is what silently ate the following `}` and truncated the parse.
_OPERATORS = ("=", "<", ">", "<=", ">=", "!=", "==")

# Which `if` an else/else_if binds to when both readings are available - it sits inside one `if`
# and follows another. NO syntactic rule recovers the intent for every calculator: the infantry,
# marines and armour ladders mean "not the OUTER if" (nested) while the mountaineer one means
# "not the INNER if" (sibling). The default here only decides what this checker reports; the
# flattened calculators carry no else at all, which is the point of flattening them.
PREFER_NESTED = False


# ----------------------------------------------------------------------------- parser


class Node:
    """One `key = value` entry. `block` is a list of Nodes when the value was a brace block."""

    __slots__ = ("key", "scalar", "block", "line", "end_line")

    def __init__(self, key, scalar=None, block=None, line=0, end_line=0):
        self.key = key
        self.scalar = scalar
        self.block = block
        self.line = line
        self.end_line = end_line or line

    def get(self, key):
        for n in self.block or ():
            if n.key == key:
                return n
        return None

    def __repr__(self):
        return "<%s @%d>" % (self.key, self.line)


_TOKEN = re.compile(r'#[^\n]*|"[^"]*"|[{}=]|[^\s{}=]+')


def tokenize(text):
    out = []
    pos = 0
    line = 1
    for m in _TOKEN.finditer(text):
        line += text.count("\n", pos, m.start())
        pos = m.start()
        tok = m.group(0)
        if tok.startswith("#"):
            continue
        out.append((tok, line))
    return out


def parse(text):
    """Parse a PDXScript file into a list of top-level Nodes. Tolerant, not validating."""
    toks = tokenize(text)
    i = 0

    def parse_block():
        nonlocal i
        nodes = []
        while i < len(toks):
            tok, line = toks[i]
            if tok == "}":
                i += 1
                return nodes
            if tok in ("=", "{"):
                # stray token (a bare value inside a list, a comparison operator) - skip
                i += 1
                continue
            key = tok
            i += 1
            if i < len(toks) and toks[i][0] in _OPERATORS:
                i += 1
            if i < len(toks) and toks[i][0] == "{":
                i += 1
                inner = parse_block()
                close = toks[i - 1][1] if i else line
                nodes.append(Node(key, block=inner, line=line, end_line=close))
            elif i < len(toks) and toks[i][0] not in ("}", "{"):
                nodes.append(Node(key, scalar=toks[i][0], line=line))
                i += 1
            else:
                # a bare token in a value list, or a key whose value is the block terminator
                nodes.append(Node(key, line=line))
        return nodes

    return parse_block()


# ------------------------------------------------------------------- if/else chain model


class Branch:
    """One arm of an if / else_if / else chain."""

    __slots__ = ("kind", "cond", "body", "line", "opaque", "node")

    def __init__(self, kind, cond, body, line, opaque, node=None):
        self.kind = kind          # "if" | "else_if" | "else"
        self.cond = cond          # frozenset of literals, None for a bare else
        self.body = body          # list of Nodes
        self.line = line
        self.opaque = opaque      # a condition this checker cannot read as a plain conjunction
        self.node = node          # the source Node, so a caller can re-read its raw `limit`


def read_limit(limit_node):
    """Turn a `limit` block into a frozenset of literals, plus an `opaque` flag.

    Only a flat conjunction of `X = yes` and `NOT = { X = yes }` is read exactly. Anything
    else (OR, nested AND, check_variable, date) becomes one opaque literal carrying its own
    source line, so it can never compare equal to another condition. That is the safe
    direction: an unreadable condition is reported as neither duplicate nor unreachable.
    """
    lits = set()
    opaque = False
    if limit_node is None or limit_node.block is None:
        return frozenset(), False
    for n in limit_node.block:
        if n.key == "NOT" and n.block and len(n.block) == 1 and n.block[0].scalar == "yes":
            lits.add("!" + n.block[0].key)
        elif n.scalar == "yes" and n.block is None:
            lits.add(n.key)
        else:
            opaque = True
            lits.add("?opaque@%d" % n.line)
    return frozenset(lits), opaque


def chains_in_block(block, issues, path):
    """Rebuild the if / else_if / else chains that start at THIS block level. Not recursive.

    Both spellings are live in this repo and both are legal - measured in the 1.19.2 install:
    1049 of 7659 vanilla else/else_if sit inside their own if block.
      sibling  -  if = { ... }  else = { ... }     the else follows the if in this block
      nested   -  if = { ... else = { ... } }      the else is a child of the if block
    A chain may switch spelling mid-way, and the light-armour ladder does: its first else_if is
    nested inside the if, and the other nineteen are siblings OF THAT else_if.

    Binding rule: an else/else_if belongs to the last if/else_if BEFORE IT IN ITS OWN BLOCK, and
    only when its block holds no earlier `if` does it belong to the if that contains the block.
    Sibling therefore wins over nesting. Reading it the other way round says the mountaineer
    `else` is the "no mountaineers" arm rather than the "no marshes" arm, which would hand
    2002/2003 to a country that wants no mountain divisions at all - the opposite of the
    `set _template_value = 0` that opens the effect.
    """
    chains = []
    i = 0
    while i < len(block):
        if block[i].key != "if":
            i += 1
            continue

        arms = []
        container, idx = block, i
        while True:
            cur = container[idx]

            # (1) an arm following cur in its own container, (2) otherwise an arm nested in cur -
            # but only one that comes before any `if` of cur, since a later one belongs to that if
            nxt_container = nxt_idx = None

            def _nested():
                for k, n in enumerate(cur.block or ()):
                    if n.key == "if" and not PREFER_NESTED:
                        return None
                    if n.key in ("else", "else_if"):
                        return k
                return None

            def _sibling():
                j = idx + 1
                skipped = 0
                while j < len(container) and container[j].key not in ("else", "else_if", "if"):
                    skipped += 1
                    j += 1
                if j < len(container) and container[j].key in ("else", "else_if"):
                    return j, skipped
                return None, 0

            if PREFER_NESTED:
                k = _nested()
                if k is not None:
                    nxt_container, nxt_idx = cur.block, k
            if nxt_container is None:
                j, skipped = _sibling()
                if j is not None:
                    if skipped:
                        issues.append(
                            ("WARN", "ELSE-SEPARATED", path, container[j].line,
                             "`%s` is separated from its `if` by %d statement(s); the engine "
                             "binding of this form is unverified" % (container[j].key, skipped)))
                    nxt_container, nxt_idx = container, j
                    if container is block:
                        i = j
            if nxt_container is None and not PREFER_NESTED:
                k = _nested()
                if k is not None:
                    nxt_container, nxt_idx = cur.block, k
            nxt = nxt_container[nxt_idx] if nxt_container is not None else None
            arms.append((cur, nxt))
            if nxt is None:
                break
            container, idx = nxt_container, nxt_idx

        # A branch body keeps every else/else_if that belongs to a chain nested INSIDE it; only
        # this branch's own continuation is removed. Dropping them all is what made the arms of
        # an inner chain vanish from the walk.
        chain = []
        for cur, nxt in arms:
            if cur.key == "else":
                cond, opaque = None, False
            else:
                cond, opaque = read_limit(cur.get("limit"))
            body = [n for n in (cur.block or ()) if n.key != "limit" and n is not nxt]
            chain.append(Branch(cur.key, cond, body, cur.line, opaque, cur))
        chains.append(chain)
        i += 1
    return chains


def all_chains(block, issues, path, out=None):
    """Every chain in the subtree, for the ordering checks. Context is not tracked here."""
    if out is None:
        out = []
    found = chains_in_block(block, issues, path)
    out.extend(found)
    owned = set()
    for chain in found:
        for br in chain:
            for n in br.body:
                owned.add(id(n))
            all_chains(br.body, issues, path, out)
    for n in block:
        if n.block and n.key not in ("if", "else", "else_if") and id(n) not in owned:
            all_chains(n.block, issues, path, out)
    return out


# --------------------------------------------------------------- calculator value extraction


def walk_values(block, ctx, out, mirrors, sink):
    """Record every `_template_value = N` write, in source order, with its condition context."""

    def emit(nodes, local):
        for n in nodes:
            if n.key == "set_temp_variable" and n.block:
                kv = n.block[0]
                if kv.key == "_template_value" and kv.scalar is not None:
                    try:
                        out.append((int(kv.scalar), frozenset(local), n.line))
                    except ValueError:
                        pass
            elif n.key == HOSPITAL_MIRROR_EFFECT and out:
                mirrors.add(out[-1][0])

    chains = chains_in_block(block, sink, "")
    emit([n for n in block if n.key not in ("if", "else", "else_if")], ctx)

    for chain in chains:
        negated = []
        for br in chain:
            local = set(ctx)
            for prev in negated:
                local.add(("NOT", prev))
            if br.cond is not None:
                local |= br.cond
                negated.append(br.cond)
            # walk_values re-emits this body's own statements; emitting them here too would
            # double every write.
            walk_values(br.body, local, out, mirrors, sink)



def no_direct_effect(block, issues, path):
    """Flag an if / else_if / else block whose body contains no effect of its own.

    Owner ruling 2026-08-29: inside a scripted EFFECT file the engine does not accept an
    if/else block that holds only nested if/else blocks - it has to see an effect to treat the
    block as one. That is what the six `_weird_debug` sentinel lines in the armour calculators
    are: a throwaway `set_temp_variable` supplying the missing effect, with the comment "for
    some reason, removing this line breaks the function".

    MEASURED 2026-08-29 over the eleven calculators: the six sentinels sit in exactly the six
    blocks that would otherwise have zero direct effect, and seventeen further blocks have zero
    direct effect with no sentinel. Whether those seventeen actually misbehave is not settled
    here - this is a WARN, and only a console run or a save can promote it.

    `limit` is not an effect, and neither is a nested if/else/else_if. Everything else counts.
    """
    STRUCTURAL = ("limit", "if", "else", "else_if")
    for n in block:
        if not n.block:
            continue
        if n.key in ("if", "else", "else_if"):
            if not any(c.key not in STRUCTURAL for c in n.block):
                issues.append(("WARN", "NO-DIRECT-EFFECT", path, n.line,
                               "`%s` block holds only nested if/else and no effect of its own; "
                               "the engine may not run it" % n.key))
        no_direct_effect(n.block, issues, path)



CLAIM_VAR = "_template_claimed"


def claim_guards(calc, issues, path):
    """In a claim-cascade calculator, every value-writing branch must carry the guard.

    The flattened calculators are ordered first-match-wins sequences: each branch tests
    `check_variable = { _template_claimed = 0 }` and sets it to 1 once it takes the role. A branch
    added later without both halves does not fall through - it OVERWRITES whatever an earlier,
    higher-priority branch already chose, and nothing says so. This rule is what makes the
    cascade a structure rather than a convention.

    Only calculators that open with `_template_claimed = 0` are checked, so a calculator that
    has not been flattened is left alone.
    """
    opens = any(n.key == "set_temp_variable" and n.block
                and n.block[0].key == CLAIM_VAR and n.block[0].scalar == "0"
                for n in calc.block)
    if not opens:
        return
    for chain in all_chains(calc.block, [], path):
        for br in chain:
            writes = [n for n in br.body
                      if n.key == "set_temp_variable" and n.block
                      and n.block[0].key == "_template_value"
                      and n.block[0].scalar not in (None, "0")]
            if not writes:
                continue
            lim = br.node.get("limit")
            guarded = any(t.key == "check_variable" and t.block
                          and t.block[0].key == CLAIM_VAR and t.block[0].scalar == "0"
                          for t in (lim.block if lim and lim.block else ()))
            claims = any(n.key == "set_temp_variable" and n.block
                         and n.block[0].key == CLAIM_VAR and n.block[0].scalar == "1"
                         for n in br.body)
            if not guarded or not claims:
                missing = []
                if not guarded:
                    missing.append("no `check_variable = { %s = 0 }` in its limit" % CLAIM_VAR)
                if not claims:
                    missing.append("does not set `%s = 1`" % CLAIM_VAR)
                issues.append(("ERROR", "CLAIM-GUARD-MISSING", path, br.line,
                               "%s: this branch writes %s but %s; it would overwrite a "
                               "higher-priority branch"
                               % (calc.key, writes[0].block[0].scalar, " and ".join(missing))))


def sets_tier_offset(block):
    """True when this calculator can add the +500 chassis tier anywhere in its body."""
    for n in block:
        if n.key == "set_temp_variable" and n.block:
            kv = n.block[0]
            if kv.key == "_tier_offset" and kv.scalar == str(TIER_OFFSET):
                return True
        if n.block and sets_tier_offset(n.block):
            return True
    return False


# ----------------------------------------------------------------------------- ai_templates


def load_templates(template_dir):
    """Return (flag -> {value: [(name, file, line)]}, list of entries for the shape checks)."""
    by_flag = {}
    entries = []
    for f in sorted(template_dir.glob("*.txt")):
        roots = parse(f.read_text(encoding="utf-8-sig", errors="ignore"))
        for group in roots:
            if group.block is None:
                continue
            names = {}
            for entry in group.block:
                if entry.block is None or entry.get("target_template") is None:
                    continue
                entries.append(("ENTRY", f, group.key, entry))
                names.setdefault(entry.key, []).append(entry.line)
                enable = entry.get("enable")
                if enable is None:
                    continue
                flag = enable.get("has_country_flag")
                if flag is None or flag.block is None:
                    continue
                fname = fval = None
                for kv in flag.block:
                    if kv.key == "flag":
                        fname = kv.scalar
                    elif kv.key == "value":
                        fval = kv.scalar
                if fname and fval and fval.isdigit():
                    by_flag.setdefault(fname, {}).setdefault(int(fval), []).append(
                        (entry.key, f, entry.line))
            for name, lines in names.items():
                if len(lines) > 1:
                    entries.append(("DUP", f, group.key, (name, lines)))
    return by_flag, entries


def load_type_map(loc_file):
    """template_type_code -> flag name, read from the scripted localisation (the live map)."""
    roots = parse(loc_file.read_text(encoding="utf-8-sig", errors="ignore"))
    out = {}
    for d in roots:
        if d.key != "defined_text" or d.block is None:
            continue
        name = d.get("name")
        if name is None or name.scalar != "WA_AI_TEMPLATE_TYPE":
            continue
        for t in d.block:
            if t.key != "text" or t.block is None:
                continue
            trig, key = t.get("trigger"), t.get("localization_key")
            if trig is None or key is None or key.scalar is None:
                continue
            cv = trig.get("check_variable")
            if cv is None or cv.block is None:
                continue
            for kv in cv.block:
                if kv.key == "_template_type_code" and kv.scalar and kv.scalar.isdigit():
                    out[int(kv.scalar)] = "WA_" + key.scalar.strip('"') + "_TEMPLATE"
    return out


# ----------------------------------------------------------------------------- checks


def run(root):
    """Run every check against the mod tree at `root`. Returns (issues, reachable)."""
    effects = root / "common" / "scripted_effects" / "WA_AI_TEMPLATES_effects.txt"
    loc = root / "common" / "scripted_localisation" / "WA_AI_templates_scripted_loc.txt"
    template_dir = root / "common" / "ai_templates"

    issues = []
    eff_rel = effects.relative_to(root).as_posix()
    roots = parse(effects.read_text(encoding="utf-8-sig", errors="ignore"))
    type_map = load_type_map(loc)
    by_flag, entries = load_templates(template_dir)

    reachable = {}
    for calc in roots:
        if not re.fullmatch(r"WA_AI_TEMPLATES_calculate_\w+_template", calc.key):
            continue
        if calc.block is None:
            continue

        code = None
        for n in calc.block:
            if n.key == "set_temp_variable" and n.block:
                kv = n.block[0]
                if kv.key == "_template_type_code" and kv.scalar and kv.scalar.isdigit():
                    code = int(kv.scalar)
        # `_tier_offset = 500` is set inside a gate, never at the top of the effect, so this has
        # to look through the whole body - scanning only the top level is what made every 6500+
        # mirror target read as orphaned.
        offset_500 = sets_tier_offset(calc.block)
        if code is None:
            issues.append(("ERROR", "NO-TYPE-CODE", eff_rel, calc.line,
                           "%s sets no _template_type_code" % calc.key))
            continue
        flag = type_map.get(code)
        if flag is None:
            issues.append(("ERROR", "NO-TYPE-CODE", eff_rel, calc.line,
                           "%s uses code %d, absent from WA_AI_TEMPLATE_TYPE"
                           % (calc.key, code)))
            continue

        written, mirrors, sink = [], set(), []
        walk_values(calc.block, set(), written, mirrors, sink)
        vals = {v for v, _, _ in written if v != 0}
        vals |= {v + HOSPITAL_MIRROR_OFFSET for v in mirrors if v != 0}
        if offset_500:
            vals |= {v + TIER_OFFSET for v in set(vals)}
        reachable.setdefault(flag, set()).update(vals)

        no_direct_effect(calc.block, issues, eff_rel)
        claim_guards(calc, issues, eff_rel)
        for chain in all_chains(calc.block, issues, eff_rel):
            seen = []
            for br in chain:
                if br.cond is None or br.opaque or not br.cond:
                    continue
                for prev_cond, prev_line in seen:
                    if br.cond == prev_cond:
                        issues.append(("ERROR", "DUP-CONDITION", eff_rel, br.line,
                                       "%s: same condition as the branch at line %d; only the "
                                       "first can ever run" % (calc.key, prev_line)))
                        break
                    if prev_cond < br.cond:
                        issues.append(("ERROR", "UNREACHABLE-BRANCH", eff_rel, br.line,
                                       "%s: condition implies the branch at line %d (%s), so "
                                       "this branch is never reached"
                                       % (calc.key, prev_line, sorted(prev_cond))))
                        break
                seen.append((br.cond, br.line))

    for flag, vals in sorted(reachable.items()):
        have = by_flag.get(flag, {})
        for v in sorted(vals):
            if v not in have:
                issues.append(("ERROR", "VALUE-NO-TEMPLATE", "common/ai_templates/", 0,
                               "%s value %d is reachable but no ai_template enables on it"
                               % (flag, v)))
        for v in sorted(have):
            if v not in vals:
                name, f, line = have[v][0]
                issues.append(("WARN", "TEMPLATE-NO-VALUE", f.relative_to(root).as_posix(), line,
                               "%s enables on %s value %d, which no calculator writes"
                               % (name, flag, v)))
    for flag in sorted(set(by_flag) - set(reachable)):
        issues.append(("WARN", "TEMPLATE-NO-VALUE", "common/ai_templates/", 0,
                       "flag %s is read by ai_templates but written by no calculator" % flag))

    for item in entries:
        if item[0] == "DUP":
            _, f, group, (name, lines) = item
            issues.append(("ERROR", "DUP-TEMPLATE-NAME", f.relative_to(root).as_posix(), lines[0],
                           "`%s` declared %d times in role group `%s` (lines %s); only one is "
                           "reachable" % (name, len(lines), group, lines)))
            continue
        _, f, group, entry = item
        tt = entry.get("target_template")
        for slot, suffix in SLOT_SUFFIX.items():
            sn = tt.get(slot) if tt else None
            if sn is None or sn.block is None:
                continue
            for unit in sn.block:
                if unit.scalar is None or not unit.scalar.isdigit():
                    continue
                if not unit.key.endswith("_" + suffix):
                    issues.append(("ERROR", "SLOT-SUFFIX-MISMATCH",
                                   f.relative_to(root).as_posix(), unit.line,
                                   "%s: `%s` sits in the `%s` slot, which takes `_%s` units"
                                   % (entry.key, unit.key, slot, suffix)))

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    issues.sort(key=lambda x: (order[x[0]], x[1], x[2], x[3]))
    return issues, reachable


# ----------------------------------------------------------------------------- self-test

# A clean fixture, then one mutation per rule. A rule whose mutation does not make it fire is
# inert and the self-test fails - that clause is the whole point. The clean fixture keeps a real
# effect in every if body, so the NO-DIRECT-EFFECT baseline is silent and its mutation is the
# only thing that can make it speak.

FIXTURE_LOC = """defined_text = {
\tname = WA_AI_TEMPLATE_TYPE
\ttext = {
\t\ttrigger = { check_variable = { _template_type_code = 1 } }
\t\tlocalization_key = "INFANTRY"
\t}
}
"""

FIXTURE_EFFECTS = """WA_AI_TEMPLATES_calculate_infantry_template = {
\tset_temp_variable = { _template_type_code = 1 }
\tset_temp_variable = { _template_value = 0 }
\tif = {
\t\tlimit = { WA_AI_TEMPLATES_use_a = yes }
\t\tset_temp_variable = { _template_value = 1000 }
\t\telse_if = {
\t\t\tlimit = { WA_AI_TEMPLATES_use_b = yes }
\t\t\tset_temp_variable = { _template_value = 1001 }
\t\t}
\t}
\tWA_AI_TEMPLATES_update_target_template = yes
}
"""

# The flattened shape, for the CLAIM-GUARD-MISSING mutation: a calculator that opens the cascade
# and whose branches all carry both halves of the guard.
FIXTURE_CASCADE = """WA_AI_TEMPLATES_calculate_infantry_template = {
\tset_temp_variable = { _template_type_code = 1 }
\tset_temp_variable = { _template_value = 0 }
\tset_temp_variable = { _template_claimed = 0 }
\tif = {
\t\tlimit = {
\t\t\tcheck_variable = { _template_claimed = 0 }
\t\t\tWA_AI_TEMPLATES_use_a = yes
\t\t}
\t\tset_temp_variable = { _template_value = 1000 }
\t\tset_temp_variable = { _template_claimed = 1 }
\t}
\tif = {
\t\tlimit = {
\t\t\tcheck_variable = { _template_claimed = 0 }
\t\t\tWA_AI_TEMPLATES_use_b = yes
\t\t}
\t\tset_temp_variable = { _template_value = 1001 }
\t\tset_temp_variable = { _template_claimed = 1 }
\t}
\tWA_AI_TEMPLATES_update_target_template = yes
}
"""

FIXTURE_TEMPLATES = """WA_infantry_role = {
\trole = infantry
\tWA_T_1000 = {
\t\tenable = { has_country_flag = { flag = WA_INFANTRY_TEMPLATE value = 1000 } }
\t\ttarget_template = {
\t\t\tregiments = { infantry_battalion_line = 10 }
\t\t\tregimental_support = { pack_artillery_company_regimental = 1 }
\t\t\tsupport = { engineer_company_divisional = 1 }
\t\t}
\t}
\tWA_T_1001 = {
\t\tenable = { has_country_flag = { flag = WA_INFANTRY_TEMPLATE value = 1001 } }
\t\ttarget_template = {
\t\t\tregiments = { infantry_battalion_line = 10 }
\t\t\tsupport = { engineer_company_divisional = 1 }
\t\t}
\t}
}
"""

# tag -> (fixture file to mutate, needle, replacement)
MUTATIONS = {
    "VALUE-NO-TEMPLATE": ("effects", "_template_value = 1001 }", "_template_value = 1099 }"),
    "TEMPLATE-NO-VALUE": ("templates", "value = 1001 }", "value = 1098 }"),
    "DUP-CONDITION": ("effects", "WA_AI_TEMPLATES_use_b = yes", "WA_AI_TEMPLATES_use_a = yes"),
    "UNREACHABLE-BRANCH": ("effects", "limit = { WA_AI_TEMPLATES_use_b = yes }",
                           "limit = { WA_AI_TEMPLATES_use_a = yes WA_AI_TEMPLATES_use_b = yes }"),
    "DUP-TEMPLATE-NAME": ("templates", "WA_T_1001 = {", "WA_T_1000 = {"),
    "SLOT-SUFFIX-MISMATCH": ("templates", "engineer_company_divisional = 1",
                             "engineer_company_line = 1"),
    "NO-DIRECT-EFFECT": ("effects", "\t\tset_temp_variable = { _template_value = 1000 }\n",
                         "\t\tif = { limit = { always = yes } "
                         "set_temp_variable = { _template_value = 1000 } }\n"),
    "CLAIM-GUARD-MISSING": ("cascade",
                            "\t\t\tcheck_variable = { _template_claimed = 0 }\n"
                            "\t\t\tWA_AI_TEMPLATES_use_b = yes",
                            "\t\t\tWA_AI_TEMPLATES_use_b = yes"),
    "ELSE-SEPARATED": ("effects",
                       "\t\telse_if = {\n"
                       "\t\t\tlimit = { WA_AI_TEMPLATES_use_b = yes }\n"
                       "\t\t\tset_temp_variable = { _template_value = 1001 }\n"
                       "\t\t}\n\t}\n",
                       "\t}\n"
                       "\tset_country_flag = spacer\n"
                       "\telse_if = {\n"
                       "\t\tlimit = { WA_AI_TEMPLATES_use_b = yes }\n"
                       "\t\tset_temp_variable = { _template_value = 1001 }\n"
                       "\t}\n"),
}


def _write_fixture(root, effects=None, templates=None):
    (root / "common" / "scripted_effects").mkdir(parents=True, exist_ok=True)
    (root / "common" / "scripted_localisation").mkdir(parents=True, exist_ok=True)
    (root / "common" / "ai_templates").mkdir(parents=True, exist_ok=True)
    (root / "common" / "scripted_localisation"
     / "WA_AI_templates_scripted_loc.txt").write_text(FIXTURE_LOC, encoding="utf-8")
    (root / "common" / "scripted_effects" / "WA_AI_TEMPLATES_effects.txt").write_text(
        effects or FIXTURE_EFFECTS, encoding="utf-8")
    (root / "common" / "ai_templates" / "WA_AI_TEMPLATES_infantry.txt").write_text(
        templates or FIXTURE_TEMPLATES, encoding="utf-8")


def selftest():
    import tempfile

    failures = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _write_fixture(root)
        issues, _ = run(root)
        if issues:
            failures.append("the clean fixture is not clean")
            for i in issues:
                print("   baseline noise:", i[1], i[3], i[4])

        for tag, (which, needle, repl) in sorted(MUTATIONS.items()):
            eff, tpl = FIXTURE_EFFECTS, FIXTURE_TEMPLATES
            if which == "cascade":
                eff = FIXTURE_CASCADE
            target = tpl if which == "templates" else eff
            if needle not in target:
                failures.append("%s: its needle is not in the fixture any more" % tag)
                print("  %-22s NEEDLE MISSING" % tag)
                continue
            if which == "templates":
                tpl = tpl.replace(needle, repl, 1)
            else:
                eff = eff.replace(needle, repl, 1)
            _write_fixture(root, eff, tpl)
            issues, _ = run(root)
            fired = any(i[1] == tag for i in issues)
            if not fired:
                failures.append("%s did NOT fire on the input built to break it (got %s)"
                                % (tag, sorted({i[1] for i in issues}) or "nothing"))
            print("  %-22s %s" % (tag, "fires" if fired else "INERT"))

    if failures:
        print("\nSELFTEST FAILED")
        for f in failures:
            print("  -", f)
        return 1
    print("\nSELFTEST OK - every rule fires on the input built to break it")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit 1 on WARN too")
    ap.add_argument("--verbose", action="store_true", help="print the reachable-value map")
    ap.add_argument("--selftest", action="store_true",
                    help="check every rule fires on a fixture built to break it")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    issues, reachable = run(REPO)

    if args.verbose:
        print("Reachable template values per flag:")
        for flag, vals in sorted(reachable.items()):
            print("  %-34s %3d  %s" % (flag, len(vals), sorted(vals)))
        print()

    for sev, tag, path, line, msg in issues:
        loc = "%s:%d" % (path, line) if line else path
        print("%-5s %-20s %s  %s" % (sev, tag, loc, msg))

    n_err = sum(1 for i in issues if i[0] == "ERROR")
    n_warn = sum(1 for i in issues if i[0] == "WARN")
    print("\n%d ERROR, %d WARN" % (n_err, n_warn))
    if n_err or (args.strict and n_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
