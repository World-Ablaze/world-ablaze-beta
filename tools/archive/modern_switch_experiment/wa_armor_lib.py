#!/usr/bin/env python
"""wa_armor_lib.py - shared reader for the medium -> modern armour switch readings.

Library only (imported by read_run.py, cohort_history.py, q_reference.py).

load(path, tag) -> dict, from TWO streaming passes over one save:
  pass A  stock.equipment_definitions  -> {variant id: (definition name, creator)}
  pass B  top-level division_templates={} (every template whose country == tag, full
          composition incl. regimental_support, role, obsolete, obsolete_change_date),
          then the tag's country block: the two flags, the country's own
          division_template_id list, units (division id -> template id, equipment),
          production (military_lines, stockpile), deployment (training queue).

Nothing here interprets: every field is a direct read. Bucketing of chassis is by
DEFINITION NAME substring, most specific first (see chassis_bucket).
"""
import collections
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SCRIPTS = os.path.join(REPO, ".claude", "skills", "wa-savegame-analysis", "scripts")
sys.path.insert(0, SCRIPTS)
import savegame as sg  # noqa: E402
import stock  # noqa: E402

ID_RE = re.compile(r"id=\{ id=(\d+) type=(\d+) \}")
SLOT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=\{")
KV_RE = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)="?([^"\n]*?)"?$')

FLAGS = ("WA_MEDIUM_ARMOR_TEMPLATE", "WA_AI_TEMPLATES_modern_chassis_earned")

# order matters: most specific first
BUCKETS = (
    ("medium_chassis_td", "medium_td"),
    ("modern_chassis", "modern"),
    ("medium_chassis", "medium"),
    ("heavy_chassis", "heavy"),
)


def chassis_bucket(defname):
    for needle, bucket in BUCKETS:
        if needle in defname:
            return bucket
    return None


def _delta(line):
    return line.count("{") - line.count("}")


def read_templates(fh, tag):
    """Consume division_templates={} (handle is just past its opening line)."""
    out, cur, slot, depth = {}, None, None, 1
    for line in fh:
        s = line.strip()
        before = depth
        depth += _delta(line)
        if depth <= 0:
            break
        if before == 1:
            if s.startswith("division_template={"):
                cur = {"id": None, "name": None, "country": None, "role": None,
                       "obsolete": False, "obsolete_change_date": None,
                       "regiments": collections.Counter(),
                       "support": collections.Counter(),
                       "regimental_support": collections.Counter(),
                       "other_keys": set()}
                slot = None
            continue
        if cur is None:
            continue
        if before == 2:
            slot = None
            m = ID_RE.match(s)
            if m and cur["id"] is None:
                cur["id"] = int(m.group(1))
            elif s.startswith("regiments={"):
                slot = "regiments"
            elif s.startswith("support={"):
                slot = "support"
            elif s.startswith("regimental_support={"):
                slot = "regimental_support"
            else:
                m = KV_RE.match(s)
                if m:
                    k, v = m.group(1), m.group(2)
                    if k == "name" and cur["name"] is None:
                        cur["name"] = v
                    elif k == "country":
                        cur["country"] = v
                    elif k == "role":
                        cur["role"] = v
                    elif k == "obsolete":
                        cur["obsolete"] = (v == "yes")
                    elif k == "obsolete_change_date":
                        cur["obsolete_change_date"] = v
                    else:
                        cur["other_keys"].add(k)
            if depth <= 1:
                if cur["id"] is not None and cur["country"] == tag:
                    out[cur["id"]] = cur
                cur = None
        elif before == 3 and slot:
            m = SLOT_RE.match(s)
            if m:
                cur[slot][m.group(1)] += 1
    return out


def country_body(fh, tag):
    """Lines of the tag's country block (handle positioned anywhere before it)."""
    for line in fh:
        if line.startswith("countries={"):
            break
    else:
        return []
    depth = 1
    head = "\t%s={" % tag
    for line in fh:
        if depth == 1 and line.startswith(head):
            d = _delta(line)
            body = []
            for nxt in fh:
                d += _delta(nxt)
                if d <= 0:
                    break
                body.append(nxt)
            return body
        depth += _delta(line)
        if depth <= 0:
            break
    return []


def sections(body):
    """{section name: [ (start, end) ]} for the depth-1 children of a country body."""
    out = collections.defaultdict(list)
    depth, name, start = 0, None, None
    for i, line in enumerate(body):
        if depth == 0:
            m = SLOT_RE.match(line.strip())
            if m and _delta(line) > 0:
                name, start = m.group(1), i
        depth += _delta(line)
        if depth == 0 and name is not None:
            out[name].append((start, i))
            name = None
    return out


def child_blocks(lines, key):
    """Yield the line lists of every DIRECT child block `key={ ... }` of `lines`
    (lines[0] is the parent opening line)."""
    depth, buf = 0, None
    for line in lines:
        before = depth
        depth += _delta(line)
        if buf is not None:
            buf.append(line)
            if depth <= 1:
                yield buf
                buf = None
        elif before == 1 and line.strip().startswith(key + "={") and depth > 1:
            buf = [line]


def read_equipment(block_lines):
    """{variant id: amount} from the FIRST `equipment={ equipment={ id amount } }`
    wrapper that is a direct child of block_lines."""
    out = collections.Counter()
    for wrap in child_blocks(block_lines, "equipment"):
        for ent in child_blocks(wrap, "equipment"):
            eid, amount = None, None
            for l in ent:
                s = l.strip()
                m = ID_RE.match(s)
                if m and eid is None:
                    eid = int(m.group(1))
                elif s.startswith("amount="):
                    amount = float(s.split("=", 1)[1])
            if eid is not None and amount is not None:
                out[eid] += amount
        break
    return out


def direct_fields(block_lines, keys):
    out, depth = {}, 0
    for line in block_lines:
        before = depth
        depth += _delta(line)
        if before == 1:
            s = line.strip()
            m = ID_RE.match(s)
            if m and "id" not in out:
                out["id"] = int(m.group(1))
                continue
            for k in keys:
                if s.startswith(k + "=") and k not in out:
                    out[k] = s.split("=", 1)[1].strip().strip('"')
    return out


def load(path, tag="GER"):
    full = sg.resolve(path)
    meta = sg.read_meta(full)
    with sg.open_save(full) as fh:
        defs = stock.equipment_definitions(fh)
    templates = {}
    with sg.open_save(full) as fh:
        for line in fh:
            if line.startswith("division_templates={"):
                templates = read_templates(fh, tag)
                break
        body = country_body(fh, tag)
    if not templates:
        # division_templates not found before countries: reopen for the body
        with sg.open_save(full) as fh:
            body = country_body(fh, tag)
    sec = sections(body)
    res = {"file": os.path.basename(full), "path": full, "meta": meta, "defs": defs,
           "templates": templates, "flags": {}, "own_template_ids": [],
           "divisions": {}, "lines": [], "stock": collections.Counter(),
           "queue": [], "alive": bool(sec.get("units"))}
    # own template list (depth-1 single-line refs)
    depth = 0
    for line in body:
        if depth == 0:
            m = re.match(r"^\s*division_template_id=\{ id=(\d+) type=\d+ \}", line)
            if m:
                res["own_template_ids"].append(int(m.group(1)))
        depth += _delta(line)
    # flags
    for a, b in sec.get("flags", []):
        lines = body[a:b + 1]
        for name in FLAGS:
            for blk in child_blocks(lines, name):
                res["flags"][name] = direct_fields(blk, ("value", "date"))
            if name not in res["flags"]:
                for l in lines:      # single-line form `NAME=1` fallback
                    s = l.strip()
                    if s.startswith(name + "="):
                        res["flags"][name] = {"value": s.split("=", 1)[1]}
    # units
    for a, b in sec.get("units", []):
        lines = body[a:b + 1]
        # independent count, the same function `savegame.py army` uses (closure test)
        res["army_count"] = res.get("army_count", 0) + sg._count_divisions(lines)
        for blk in child_blocks(lines, "division"):
            f = direct_fields(blk, ("organisation", "strength", "location",
                                    "last_combat_date"))
            tid = None
            d = 0
            for l in blk:
                bd = d
                d += _delta(l)
                if bd == 1:
                    m = re.match(r"^\s*division_template_id=\{ id=(\d+)", l)
                    if m:
                        tid = int(m.group(1))
                        break
            f["tid"] = tid
            f["equipment"] = read_equipment(blk)
            if "id" in f:
                res["divisions"][f["id"]] = f
    # production
    for a, b in sec.get("production", []):
        lines = body[a:b + 1]
        for blk in child_blocks(lines, "military_lines"):
            f = direct_fields(blk, ("active_factories", "requested_factories",
                                    "priority", "amount", "produced"))
            vid = None
            for l in blk:
                m = re.match(r"^\s*equipment_variant_index=\{ id=(\d+)", l)
                if m:
                    vid = int(m.group(1))
                    break
            f["variant"] = vid
            f["defname"] = defs.get(vid, ("?", None))[0] if vid is not None else None
            res["lines"].append(f)
        for blk in child_blocks(lines, "equipments"):
            for ent in child_blocks(blk, "equipment"):
                eid, amount = None, None
                for l in ent:
                    s = l.strip()
                    m = ID_RE.match(s)
                    if m and eid is None:
                        eid = int(m.group(1))
                    elif s.startswith("amount="):
                        amount = float(s.split("=", 1)[1])
                if eid is not None and amount is not None:
                    res["stock"][eid] += amount
    # deployment (training queue)
    for a, b in sec.get("deployment", []):
        lines = body[a:b + 1]
        for blk in child_blocks(lines, "military_deployment_conveyor"):
            f = direct_fields(blk, ("name", "amount", "role", "closed"))
            tid = None
            for l in blk:
                m = re.match(r"^\s*division_template_id=\{ id=(\d+)", l)
                if m:
                    tid = int(m.group(1))
                    break
            f["tid"] = tid
            f["n_lines"] = sum(1 for _ in child_blocks(blk, "military_deployment_line"))
            res["queue"].append(f)
    return res


# ------------------------------------------------------------------ derived helpers

def comp_str(counter):
    return ", ".join("%s x%d" % (k, v) for k, v in sorted(counter.items())) or "-"


def split_label(t):
    """'<medium>+<modern>' line battalions of a template (medium_armor / modern_armor)."""
    med = sum(v for k, v in t["regiments"].items() if k.startswith("medium_armor_battalion"))
    mod = sum(v for k, v in t["regiments"].items() if k.startswith("modern_armor_battalion"))
    return "%d+%d" % (med, mod)


def is_armour_template(t):
    """role says armour, or a line battalion name carries `_armor_battalion`."""
    role = t.get("role") or ""
    if "armor" in role:
        return True
    return any("_armor_battalion" in k for k in t["regiments"])


GUN_RE = re.compile(r"_(medium|modern)_chassis_\d")


def is_gun_tank(defname):
    """The plain gun tank of the medium/modern family: `..._medium_chassis_<digit>...`.
    Excludes the _assault_, _infantry_support_, _aa_, _td_ variants, which the doc's
    `medium_chassis` substring bucket lumps in with it."""
    return bool(GUN_RE.search(defname))


def div_chassis(div, defs):
    """Counter: the four doc buckets + `medium_gun` (subset of `medium`)."""
    out = collections.Counter()
    for eid, amt in div["equipment"].items():
        name = defs.get(eid, ("?", None))[0]
        b = chassis_bucket(name)
        if b:
            out[b] += amt
            if b == "medium" and is_gun_tank(name):
                out["medium_gun"] += amt
    return out


def stock_chassis(res, own_tag=None):
    """Free stockpile per bucket. own_tag given -> only variants whose creator is that tag."""
    out = collections.Counter()
    for eid, amt in res["stock"].items():
        name, creator = res["defs"].get(eid, ("?", None))
        if own_tag is not None and creator != own_tag:
            continue
        b = chassis_bucket(name)
        if b:
            out[b] += amt
            if b == "medium" and is_gun_tank(name):
                out["medium_gun"] += amt
    return out


def lines_by_bucket(res):
    out = {}
    for ln in res["lines"]:
        b = chassis_bucket(ln.get("defname") or "")
        if not b:
            continue
        o = out.setdefault(b, {"n": 0, "active": 0, "requested": 0})
        o["n"] += 1
        o["active"] += int(float(ln.get("active_factories", 0)))
        o["requested"] += int(float(ln.get("requested_factories", 0)))
    return out


def divs_by_template(res):
    out = collections.defaultdict(list)
    for did, d in res["divisions"].items():
        out[d["tid"]].append(did)
    return out


def tlabel(res, tid):
    t = res["templates"].get(tid)
    if t is None:
        return "#%s (not a %s template in this save)" % (tid, "tag")
    return "#%d %s" % (tid, t["name"])
