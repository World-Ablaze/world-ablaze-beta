#!/usr/bin/env python
"""AI battle plans: who has an order, of what kind, and where every division sits.

Why this exists (2026-08-17, campaign 7c7803a8): a diagnosis reported that Britain's front
plans "stopped being re-planned after January 1943" and that 29 British divisions stood on
the Tunisian front with no battle plan for 30 months. Both claims were parser artifacts,
reproduced twice by two different agents. A screenshot of the running game killed them.

THE TRAP. Inside `theatres={ theatre={ ... } }` there are TWO kinds of depth-2 block:

    orders_group={                          <- an ARMY (definition, multi-line)
        id={ id=11124 type=53 }
        name="Army 20"
        order_instance={ ... }              <- its own plan, if any
        member={ unit={ id=N type=T } }
    }
    field_marshal_group={                   <- an ARMY GROUP (sibling, NOT nested)
        orders_group={ id=11125 type=53 }   <- single-line ID REFERENCE, not a definition
        orders_group={ id=11124 type=53 }
        name="Army Group 3"
        order_instance={ type=2 path={...} root_front={...} }   <- THE PLAN LIVES HERE
        field_marshal_group=yes
    }

An army group's front order covers its child armies. Scan only `orders_group` and those
children read as orderless while they are in fact executing an army-group plan - which is
exactly how 29 armed divisions were reported idle. Corrected, ENG had 31-36 divisions on
fronts at every sampled date and zero orderless.

SECOND TRAP. `order_instance.creation_date` is stamped once at creation and NEVER
refreshed. A live order keeps re-pathing and rotating members under the same instance_id
and the same date (ENG instance 1982 held "1943.1.10" from 1943.6 to 1945.6 with a
different `path` in every save). So "newest plan date per country" measures front
birth/death, not planner activity, and can move BACKWARDS between saves when a newer front
dies - which alone disproves the re-planning reading. Use --fronts, which prints instance
continuity and the path, not the date alone.

Order types attested in a full 1944 save (all countries, 567 order_instance blocks): only
1, 2, 3, 5. Anything else is new - the script prints it as `type=N` rather than guessing.

    1  front line      has `path`, `order_children`
    2  front advance   root carries `sorted_pairs`, `root_front`, `enemy_controller_area`
    3  naval invasion  has `invasion_source`, `convoys` - and its `path={}` is the TARGET
       province list, `invasion_source=` the staging province (measured on 1ac7e4ea
       1942.10: ENG/USA both carry path 5222 = Madagascar, invasion_source 13018 =
       Mauritius, plus `convoys={ convoys=N total=N }` and one `scheduled_member=` per
       assigned division). --invasions resolves both ends to state names.
    5  area defence    has `states`, `area_defense_settings`:
                         102 = a scripted `put_unit_buffers` garrison (WA ai_strategy)
                         100 = an engine-generated area-defence order
       The 102/100 split is how you separate WA's own garrisons from the engine's. Verified
       by matching 102 state sets against the `states = { }` lists in
       common/ai_strategy/WA_AI_MILITARY_COUNTRY_*_THEATRE.txt.

ORDER OF BATTLE (--oob / --templates). What a division IS is not in its own block: the
division carries `division_template_id={ id=N type=52 }` and nothing else, and the template
that id points at lives in a TOP-LEVEL `division_templates={}` block shared by every country
(1107 templates on a 1945 save). That block precedes `countries={}` (measured on three saves
across two campaigns: 238076 < 1258663, 225782 < 1159695, 167862 < 807177), so one pass reads
both. A division has NO name string in the save - `division_name={ type=0 name_order=2 }` is
an index into a name list - so a division is identified by its template, never by a name.

The FAMILY column (armour / mech / mot / cav / foot) is derived from `common/units/*.txt`,
from the pair (group, type) of each line battalion - never from the battalion's name. WA
renamed every battalion and collapsed mountain, marine, paratrooper and militia into
`type = { infantry }`, so a name-pattern classifier reads all four as line infantry. The
battalion keys themselves are always printed beside the family, because they are the ground
truth the family summarises.

usage: plans.py TAG[,TAG...] FILE... [--armies] [--fronts] [--invasions] [--divisions]
                [--where] [--oob] [--templates] [--limit N]
       plans.py ALL FILE... [--limit N]
  (no flag)    per-save census: armies, army groups, divisions per order class
  --armies     one row per army: class, parent army group, division count
  --fronts     every front order (type 1/2) with instance id, creation date, path -> states
  --invasions  every naval-invasion order (type 3): covered army, divisions, staging
               (invasion_source + where the divisions sit), TARGET path -> states
  --divisions  org / strength / recent-combat share per order class
  --where      divisions per STATE, split by order class - where they are and what they do
  --oob        ORDER OF BATTLE: per army - its order, its template mix, its states
  --templates  per TEMPLATE census: what the country actually fields, and under which order
  --limit N    cap rows in --armies / --fronts / --invasions / --where / --oob /
               --templates (default 40, 0 = unlimited)
"""
import io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402  (resolve, open_save, read_meta)

REPO = sg.REPO
STATE_LOC = os.path.join(REPO, "localisation", "english", "state_names_l_english.yml")

TAG_RE = re.compile(r"^\t([A-Z][A-Z0-9]{2})=\{")
SECTION_RE = re.compile(r"^\t\t([A-Za-z_0-9]+)=\{")
# A single-line `orders_group={ id=N type=T }` is a REFERENCE, never a definition.
REF_RE = re.compile(r"^orders_group=\{ id=(\d+) type=\d+ \}$")
GROUP_ID_RE = re.compile(r"id=\{ id=(\d+) type=53 \}")
UNIT_RE = re.compile(r"^\s*unit=\{ id=(\d+) type=\d+ \}", re.M)

FRONT_TYPES = ("1", "2")
CLASS_ORDER = ("front", "invasion", "buffer", "areadef", "NO_ORDER")

UNITS_DIR = os.path.join(REPO, "common", "units")
# A template slot: `infantry_heavy_horse_battalion_line={ x=0 y=2 }`.
SLOT_RE = re.compile(r"^([a-z_0-9]+)=\{ x=\d+ y=\d+ \}")
TEMPLATE_ID_RE = re.compile(r"^id=\{ id=(\d+) type=52 \}")
DIV_TEMPLATE_RE = re.compile(r"^division_template_id=\{ id=(\d+) type=52 \}")
# Dominant-family tie-break, strongest first: a template with as many armour as foot
# battalions is an armour template.
FAMILY_ORDER = ("armour", "mech", "mot", "cav", "foot")


def order_class(order):
    """Order class name from an order_instance dict. Unknown types stay visible."""
    t = order["type"]
    if t in FRONT_TYPES:
        return "front"
    if t == "3":
        return "invasion"
    if t == "5":
        return "buffer" if order["ads"] == "102" else "areadef"
    return "type=%s" % t


# ---------------------------------------------------------------- lookups

_state_name = None

# province -> state comes from savegame.province_state_map(): one loader, one cache, and
# one place that knows the coverage caveats (land only, impassable states absent).
province_state = sg.province_state_map


def state_names():
    global _state_name
    if _state_name is None:
        _state_name = {}
        try:
            for line in io.open(STATE_LOC, encoding="utf-8-sig", errors="replace"):
                m = re.match(r'\s*STATE_(\d+):\d*\s*"(.*)"', line)
                if m:
                    _state_name[int(m.group(1))] = m.group(2)
        except OSError:
            pass
    return _state_name


def path_states(path):
    """'4163 1046 14172' -> 'Tunisia, Bizerte' (ordered, de-duplicated)."""
    p2s, names = province_state(), state_names()
    out = []
    for tok in path.split():
        if not tok.isdigit():
            continue
        st = p2s.get(int(tok))
        if st is None:
            continue
        label = names.get(st, "state %d" % st)
        if label not in out:
            out.append(label)
    return ", ".join(out)


# ---------------------------------------------------------------- sub-unit families

_families = None


def _family_of(seg):
    """Family of one sub_unit, from its (group, type) pair. See the header note."""
    g = re.search(r"^\s*group\s*=\s*(\S+)", seg, re.M)
    t = re.search(r"\btype\s*=\s*\{([^}]*)\}", seg)
    group = g.group(1) if g else ""
    types = set((t.group(1) if t else "").split())
    # Line artillery / AT / AA are real battalions but never define what a division IS,
    # so they are held apart from the five manoeuvre families and excluded from the
    # dominant-family vote: 10 infantry + 3 artillery is an infantry division.
    if group in ("combat_support", "mobile_combat_support"):
        return "sup"
    if group == "support":
        return "coy"          # support company slot - lives in support={}, not regiments={}
    if group == "armor":
        return "armour"
    if "mechanized" in types:
        return "mech"
    if "motorized" in types:
        return "mot"
    if group == "mobile" and "infantry" in types:
        return "cav"          # horse cavalry: group mobile, but type infantry
    if group == "infantry" or "infantry" in types:
        return "foot"
    return "?"


def _scan_sub_units(text, out):
    """Fill {sub_unit key: family} from one common/units file."""
    text = re.sub(r"#[^\n]*", "", text)          # WA comments out whole `type={}` blocks
    m = re.search(r"sub_units\s*=\s*\{", text)
    if not m:
        return
    body = text[m.end():]
    depth, name, start = 0, None, 0
    for tok in re.finditer(r"([A-Za-z_0-9]+)\s*=\s*\{|\{|\}", body):
        if tok.group(0) == "}":
            depth -= 1
            if depth < 0:
                break
            if depth == 0 and name:
                out[name] = _family_of(body[start:tok.start()])
                name = None
        else:
            if depth == 0 and tok.group(1):
                name, start = tok.group(1), tok.end()
            depth += 1


def sub_unit_families():
    """{battalion key: family} for every sub_unit WA defines, cached.

    Derived from `common/units/*.txt`, from the pair (group, type) - never from the
    battalion NAME. WA renamed every battalion and gives mountaineer, marine,
    paratrooper and militia line units the same `type = { infantry }`, so a name-pattern
    classifier reads all four as ordinary infantry; the (group, type) pair is what
    actually separates armour / mech / mot / cavalry / foot. An unreadable common/units/
    yields {} and every family column prints `?` - the battalion keys are printed beside
    it either way, and they are the ground truth the family only summarises.
    """
    global _families
    if _families is None:
        _families = {}
        try:
            for fn in sorted(os.listdir(UNITS_DIR)):
                if not fn.endswith(".txt"):
                    continue
                with io.open(os.path.join(UNITS_DIR, fn), encoding="utf-8",
                             errors="replace") as fh:
                    _scan_sub_units(fh.read(), _families)
        except OSError:
            pass
    return _families


# ---------------------------------------------------------------- templates

def _read_templates(fh):
    """Consume the top-level `division_templates={}` block -> {template id: record}.

    The handle is left just past the block closing brace, so the caller scan for
    `countries={}` continues from there: the two blocks are read in ONE pass because
    division_templates always precedes countries (see the header measurement).
    """
    out, cur, slot, depth = {}, None, None, 1
    for line in fh:
        s = line.strip()
        before = depth
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            break
        if before == 1:
            if s.startswith("division_template={"):
                cur = {"id": None, "name": None, "country": None,
                       "regs": collections.Counter(), "sup": collections.Counter()}
                slot = None
            continue
        if cur is None:
            continue
        if before == 2:
            slot = None
            m = TEMPLATE_ID_RE.match(s)
            if m and cur["id"] is None:
                cur["id"] = int(m.group(1))
            m = re.match(r'name="(.*)"', s)
            if m and cur["name"] is None:
                cur["name"] = m.group(1)
            m = re.match(r'country="(\w+)"', s)
            if m:
                cur["country"] = m.group(1)
            if s.startswith("regiments={"):
                slot = "regs"
            elif s.startswith("support={"):
                slot = "sup"
            elif depth <= 1:                      # the template block just closed
                if cur["id"] is not None:
                    out[cur["id"]] = cur
                cur = None
        elif before == 3 and slot:
            m = SLOT_RE.match(s)
            if m:
                cur[slot][m.group(1)] += 1
    return out


def template_label(tid, templates):
    """A division is identified by its template - the save holds no division name."""
    if tid is None:
        return "(no template id)"
    rec = templates.get(tid)
    if rec is None:
        return "template #%d (not in this save)" % tid
    return rec["name"] or "(unnamed template #%d)" % tid


def template_family(rec, fams):
    """Dominant manoeuvre family of a template, ties broken by FAMILY_ORDER."""
    if not rec:
        return "?"
    counts = collections.Counter()
    support = 0
    for key, n in rec["regs"].items():
        f = fams.get(key, "?")
        if f in FAMILY_ORDER:
            counts[f] += n
        elif f == "sup":
            support += n
    if not counts:
        # No manoeuvre battalion at all. `sup` when the template is pure line artillery /
        # AT / AA (RCZ "Artillery template A" is 4 artillery + 2 AT), `?` when it is empty
        # or common/units/ could not be read.
        return "sup" if support else "?"
    best = max(counts.values())
    for f in FAMILY_ORDER:
        if counts.get(f) == best:
            return f
    return "?"


_BN_SUFFIX = re.compile(r"_(?:battalion|battalion)(?:_line)?$|_line$")


def bn_mix(counter, top=4):
    """10x infantry_heavy_horse, 3x artillery_horse (+2 more).

    Only the `_battalion_line` suffix is stripped (and the `_battalion_line` typo
    variant, which real WA templates use); the rest of the key is printed verbatim
    because it is the one measured statement about what the division is made of.
    """
    if not counter:
        return "-"
    items = counter.most_common()
    head = ", ".join("%dx %s" % (n, _BN_SUFFIX.sub("", k)) for k, n in items[:top])
    if len(items) > top:
        head += " (+%d more)" % (len(items) - top)
    return head


def _mean(vals):
    return sum(vals) / len(vals) if vals else 0.0


def _top(counter, n=4, xfirst=False, sep=", "):
    """Top-n of a Counter. `xfirst` prints '8x Infantry template F' instead of
    'Infantry template F 8' - used where the key is a multi-word name."""
    if not counter:
        return "-"
    items = counter.most_common()
    fmt = (lambda k, v: "%dx %s" % (v, k)) if xfirst else (lambda k, v: "%s %d" % (k, v))
    head = sep.join(fmt(k, v) for k, v in items[:n])
    if len(items) > n:
        head += " (+%d more)" % (len(items) - n)
    return head


def division_classes(country):
    """{division id: order class} - UNATTACHED for a division in no army member list."""
    cls = classify(country)
    out = {}
    for aid, a in country["armies"].items():
        for uid in a["members"]:
            out[uid] = cls[aid][0]
    for uid in country["divisions"]:
        out.setdefault(uid, "UNATTACHED")
    return out


# ---------------------------------------------------------------- parsing


def _orders(lines):
    """Every order_instance in a block body, outermost first."""
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].strip().startswith("order_instance={"):
            depth = lines[i].count("{") - lines[i].count("}")
            j, sub = i + 1, []
            while j < n and depth > 0:
                depth += lines[j].count("{") - lines[j].count("}")
                if depth <= 0:
                    break
                sub.append(lines[j])
                j += 1
            body = "".join(sub)
            ty = re.search(r"^\s*type=(\d+)", body, re.M)
            ads = re.search(r"area_defense_settings=(\d+)", body)
            cd = re.search(r'creation_date="([^"]*)"', body)
            iid = re.search(r"instance_id=(\d+)", body)
            pth = re.search(r"path=\{([^}]*)\}", body)
            sts = re.search(r"states=\{([^}]*)\}", body)
            src = re.search(r"^\s*invasion_source=(\d+)", body, re.M)
            cnv = re.search(r"convoys=\{\s*convoys=(\d+)\s*total=(\d+)", body)
            sched = set(int(x) for x in
                        re.findall(r"scheduled_member=\{ id=(\d+)", body))
            out.append({
                "type": ty.group(1) if ty else "?",
                "ads": ads.group(1) if ads else None,
                "cd": cd.group(1) if cd else "?",
                "iid": iid.group(1) if iid else "?",
                "path": pth.group(1).strip() if pth else "",
                "states": sts.group(1).strip() if sts else "",
                "src": int(src.group(1)) if src else None,
                "convoys": "%s/%s" % cnv.groups() if cnv else None,
                "can_execute": "can_execute=1" in body,
                "sched": len(sched),
                "sched_ids": sched,
            })
            i = j + 1
            continue
        i += 1
    return out


def _summarise(lines, kind):
    body = "".join(lines)
    rec = {"kind": kind, "name": "?", "id": None, "refs": [], "members": set(),
           "orders": _orders(lines)}
    m = re.search(r'name="([^"]*)"', body)
    if m:
        rec["name"] = m.group(1)
    if kind == "army":
        m = GROUP_ID_RE.search(body)
        if m:
            rec["id"] = int(m.group(1))
    else:
        for mm in re.finditer(r"^\s*orders_group=\{ id=(\d+) type=\d+ \}\s*$", body, re.M):
            rec["refs"].append(int(mm.group(1)))
    for mm in UNIT_RE.finditer(body):
        rec["members"].add(int(mm.group(1)))
    return rec


def _blank_country():
    return {"armies": {}, "groups": [], "divisions": {}}


def scan(path, tags=None, want_divisions=False, want_templates=False):
    """One streaming pass.
    -> ({tag: {'armies', 'groups', 'divisions'}}, {template id: rec}, in-game date or None)

    `tags` None means every country. Only `theatres` (and `units`, when asked) are read
    inside the countries block; `division_templates={}` is a TOP-LEVEL block that comes
    BEFORE it, so asking for templates costs the same single pass, not a second one.
    The `date=` header sits a few lines in and rides along for free.
    """
    out, templates, date = {}, {}, None
    with sg.open_save(sg.resolve(path)) as fh:
        for line in fh:
            if line.startswith("countries={"):
                break
            if date is None:
                m = re.match(r'^date="?(\d+(?:\.\d+)*)', line)
                if m:
                    date = m.group(1)
            if want_templates and line.startswith("division_templates={"):
                templates = _read_templates(fh)
        else:
            return out, templates, date
        depth, tag, section, sdepth = 1, None, None, 0
        buf, kind, base, bdepth = None, None, 0, 0
        div_id, div, ddepth = None, {}, None
        for line in fh:
            m = TAG_RE.match(line)
            if m and depth == 1:
                tag = m.group(1) if (tags is None or m.group(1) in tags) else None
                section, buf = None, None
                if tag:
                    out.setdefault(tag, _blank_country())
            elif tag:
                if section is None:
                    ms = SECTION_RE.match(line)
                    if ms and ms.group(1) in ("theatres", "units"):
                        section, sdepth = ms.group(1), 0
                        if section == "units" and not want_divisions:
                            section = None
                elif section == "theatres":
                    s = line.strip()
                    if buf is None and sdepth == 2 and not REF_RE.match(s):
                        if s.startswith("orders_group={"):
                            kind, buf, base = "army", [], sdepth
                        elif s.startswith("field_marshal_group={"):
                            kind, buf, base = "group", [], sdepth
                    elif buf is not None:
                        buf.append(line)
                    sdepth += line.count("{") - line.count("}")
                    if buf is not None and sdepth <= base:
                        rec = _summarise(buf, kind)
                        if kind == "army":
                            if rec["id"] is not None:
                                out[tag]["armies"][rec["id"]] = rec
                        else:
                            out[tag]["groups"].append(rec)
                        buf = None
                    if sdepth <= 0:
                        section = None
                    depth += line.count("{") - line.count("}")
                    if depth <= 0:
                        break
                    continue
                elif section == "units":
                    s = line.strip()
                    if s.startswith("division={"):
                        if div_id is not None:
                            out[tag]["divisions"][div_id] = div
                        div_id, div, ddepth = None, {}, 0
                    elif ddepth is not None:
                        # Read a division's fields at its DIRECT children only. `location=`
                        # occurs 110 times at division depth 0 on ENG 1943.11 and 255 times
                        # at depth 3 (sub-unit / supply blocks), so an unanchored read is one
                        # missing own-location away from silently reporting a sub-unit's
                        # province as the division's. `id={}` also repeats at depth 0.
                        if ddepth == 0:
                            md = re.match(r"^id=\{ id=(\d+) type=\d+ \}", s)
                            if md and div_id is None:
                                div_id = int(md.group(1))
                            for key in ("organisation", "strength", "location"):
                                mv = re.match(r"^%s=([\d.\-]+)" % key, s)
                                if mv and key not in div:
                                    div[key] = float(mv.group(1))
                            mc = re.match(r'^last_combat_date="([\d.]+)"', s)
                            if mc and "lc" not in div:
                                div["lc"] = mc.group(1)
                            # What the division IS. The save carries no division name -
                            # `division_name={}` is an index into a name list - so this
                            # id, joined to division_templates={}, is the only identity.
                            mt = DIV_TEMPLATE_RE.match(s)
                            if mt and "tid" not in div:
                                div["tid"] = int(mt.group(1))
                        ddepth += line.count("{") - line.count("}")
                    sdepth += line.count("{") - line.count("}")
                    if sdepth <= 0:
                        if div_id is not None:
                            out[tag]["divisions"][div_id] = div
                        div_id, div, section, ddepth = None, {}, None, None
                    depth += line.count("{") - line.count("}")
                    if depth <= 0:
                        break
                    continue
                if section is not None and sdepth == 0:
                    sdepth += line.count("{") - line.count("}")
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                break
    return out, templates, date


def classify(country):
    """{army_id: (class, source)} - source is '' for its own order, the group name if inherited."""
    cls = {}
    for aid, a in country["armies"].items():
        if a["orders"]:
            cls[aid] = (order_class(a["orders"][0]), "")
    for g in country["groups"]:
        if not g["orders"]:
            continue
        c = order_class(g["orders"][0])
        for ref in g["refs"]:
            if ref in country["armies"] and ref not in cls:
                cls[ref] = (c, g["name"])
    for aid in country["armies"]:
        cls.setdefault(aid, ("NO_ORDER", ""))
    return cls


def front_orders(country):
    """[(owner_name, is_group, order)] for every type-1/2 order, army groups first."""
    out = []
    for g in country["groups"]:
        for o in g["orders"]:
            if o["type"] in FRONT_TYPES:
                out.append((g["name"], True, o))
    for a in country["armies"].values():
        for o in a["orders"]:
            if o["type"] in FRONT_TYPES:
                out.append((a["name"], False, o))
    return out


def invasion_orders(country):
    """[(owner_name, is_group, covered division ids, order)] for every type-3 order."""
    out = []
    for g in country["groups"]:
        for o in g["orders"]:
            if o["type"] == "3":
                members = set()
                for ref in g["refs"]:
                    if ref in country["armies"]:
                        members |= country["armies"][ref]["members"]
                out.append((g["name"], True, members, o))
    for a in country["armies"].values():
        for o in a["orders"]:
            if o["type"] == "3":
                out.append((a["name"], False, set(a["members"]), o))
    return out


# ---------------------------------------------------------------- reports


def _sorted_classes(counts):
    known = [c for c in CLASS_ORDER if c in counts]
    return known + sorted(c for c in counts if c not in CLASS_ORDER)


def report_census(tag, save, country):
    cls = classify(country)
    armies, divs, inherited = collections.Counter(), collections.Counter(), collections.Counter()
    for aid, a in country["armies"].items():
        c, src = cls[aid]
        armies[c] += 1
        divs[c] += len(a["members"])
        if src:
            inherited[c] += len(a["members"])
    total = sum(divs.values())
    print("%s  %s   armies=%d  army_groups=%d  divisions_in_groups=%d"
          % (tag, save, len(country["armies"]), len(country["groups"]), total))
    for c in _sorted_classes(divs):
        extra = "  (%d via army group)" % inherited[c] if inherited[c] else ""
        print("    %-10s armies=%-3d divisions=%-4d%s" % (c, armies[c], divs[c], extra))
    fronts = front_orders(country)
    if fronts:
        newest = max(o["cd"] for _, _, o in fronts)
        print("    newest front creation_date=%s  (stamped once - see --fronts before "
              "reading this as re-planning)" % newest)


def report_armies(tag, save, country, limit):
    cls = classify(country)
    print("%s  %s" % (tag, save))
    print("    %-16s %-10s %-6s %s" % ("army", "class", "divs", "plan owner"))
    rows = sorted(country["armies"].items(), key=lambda kv: -len(kv[1]["members"]))
    # --limit 0 = unlimited, as in savegame.py's `section`/`pc`/`control`.
    for aid, a in (rows if not limit else rows[:limit]):
        c, src = cls[aid]
        print("    %-16s %-10s %-6d %s" % (a["name"][:16], c, len(a["members"]),
                                           src or "(own order)"))
    if limit and len(rows) > limit:
        print("    ... %d more armies (raise --limit, 0 = all)" % (len(rows) - limit))


def report_fronts(tag, save, country, limit):
    print("%s  %s" % (tag, save))
    fronts = front_orders(country)
    if not fronts:
        print("    no front orders")
        return
    print("    %-16s %-4s %-8s %-16s %-4s %s"
          % ("owner", "type", "instance", "created", "divs", "path -> states"))
    for name, is_group, o in (fronts if not limit else fronts[:limit]):
        print("    %-16s t=%-2s %-8s %-16s %-4d %s"
              % (("*" if is_group else " ") + name[:15], o["type"], o["iid"],
                 o["cd"].strip('"'), o["sched"], path_states(o["path"]) or "-"))
    if limit and len(fronts) > limit:
        print("    ... %d more front orders (raise --limit, 0 = all)"
              % (len(fronts) - limit))
    print("    * = army-group order (covers its child armies)")


def report_invasions(tag, save, country, limit):
    """Every type-3 (naval invasion) order, both ends resolved to state names.

    TARGET is the order's own `path={}` (province list) and staging is
    `invasion_source=` - see the type table in this file's header. Staging is printed
    twice on purpose: the order's invasion_source, and the states the scheduled
    divisions actually sit in - they can differ while the force converges. An order
    with no target/path field SAYS SO instead of printing nothing: that negative is a
    finding, not a formatting gap.
    """
    invs = invasion_orders(country)
    print("%s  %s   %d naval-invasion (type 3) order(s)" % (tag, save, len(invs)))
    if not invs:
        return
    names, p2s = state_names(), province_state()
    for name, is_group, members, o in (invs if not limit else invs[:limit]):
        # scheduled_member is the division set assigned to the invasion; the covering
        # army's member list is the fallback when the order schedules nobody.
        div_ids = o["sched_ids"] or members
        print("    %-16s instance=%-6s created=%-13s divisions=%-3d convoys=%s"
              % (("*" if is_group else " ") + name[:15], o["iid"],
                 o["cd"].strip('"'), len(div_ids), o["convoys"] or "-"))
        if o["src"] is not None:
            st = p2s.get(o["src"])
            label = names.get(st, "state %d" % st) if st is not None \
                else "(sea/unmapped province)"
            print("        source     province %d -> %s" % (o["src"], label))
        else:
            print("        source     NO invasion_source field in this order")
        per_s = collections.Counter()
        for uid in div_ids:
            d = country["divisions"].get(uid)
            loc = d.get("location") if d else None
            st = p2s.get(int(loc)) if loc else None
            per_s[names.get(st, "state %d" % st) if st is not None
                  else "(not deployed)"] += 1
        print("        staging    %s" % _top(per_s, 6))
        toks = [int(t) for t in o["path"].split() if t.isdigit()]
        if not toks:
            print("        TARGET     NO target recorded - this order carries no "
                  "path={} province list")
            continue
        seen, parts = set(), []
        for pid in toks:
            st = p2s.get(pid)
            label = names.get(st, "state %d" % st) if st is not None \
                else "province %d (sea/unmapped)" % pid
            if label not in seen:
                seen.add(label)
                parts.append(label)
        print("        TARGET     %s  (provinces %s)"
              % (", ".join(parts), " ".join(str(t) for t in toks)))
    if limit and len(invs) > limit:
        print("    ... %d more invasion orders (raise --limit, 0 = all)"
              % (len(invs) - limit))


def save_year(date, path):
    """Campaign year for 'fought this year'. The save's own `date=` header is the
    source; the filename prefix serves only names that start with the year
    (1944.6_Jun.hoi4 yes, GER_1945_07_01_01.hoi4 no - its prefix is the tag)."""
    if date:
        return date.split(".")[0]
    head = os.path.basename(path)[:4]
    return head if head.isdigit() else None


def report_divisions(tag, save, country, year):
    cls = classify(country)
    agg = collections.defaultdict(lambda: collections.defaultdict(list))
    for aid, a in country["armies"].items():
        c = cls[aid][0]
        for uid in a["members"]:
            d = country["divisions"].get(uid)
            if not d:
                continue
            for key in ("organisation", "strength"):
                if key in d:
                    agg[c][key].append(d[key])
            agg[c]["recent"].append(
                1 if year and d.get("lc", "1.1.1.1").split(".")[0] >= year else 0)
    print("%s  %s" % (tag, save))
    print("    %-10s %-5s %-8s %-9s %s" % ("class", "n", "org", "strength", "fought this year"))
    for c in _sorted_classes(agg):
        a = agg[c]
        if not a["strength"]:
            continue
        mean = lambda k: sum(a[k]) / len(a[k])  # noqa: E731
        recent = "%.0f%%" % (100 * mean("recent")) if year else "? (no date header)"
        print("    %-10s %-5d %-8.1f %-9.1f %s"
              % (c, len(a["strength"]), mean("organisation"), mean("strength"), recent))


def report_where(tag, save, country, limit):
    """Divisions per STATE, split by order class - where they are and what they are doing.

    Two buckets that are NOT the same thing and get conflated:
      NO_ORDER    the division is in an army, and that army (and its army group) has no
                  order - see the army-group trap in this file's header.
      UNATTACHED  the division is deployed in `units` but is in no army's member list at
                  all, so no order could reach it however the plans are read.
    A division whose `location=` province is missing from the generated map data lands in
    "(no state)" rather than being dropped - impassable states carry no provinces there.
    """
    cls = classify(country)
    names, p2s = state_names(), province_state()
    dcls = {}
    for aid, a in country["armies"].items():
        for uid in a["members"]:
            dcls[uid] = cls[aid][0]
    per = collections.defaultdict(collections.Counter)
    for uid, d in country["divisions"].items():
        loc = d.get("location")
        st = p2s.get(int(loc)) if loc else None
        label = names.get(st, "state %d" % st) if st is not None else "(no state)"
        per[label][dcls.get(uid, "UNATTACHED")] += 1
    if not per:
        print("%s  %s   no deployed divisions" % (tag, save))
        return
    classes = _sorted_classes({c for row in per.values() for c in row})
    rows = sorted(per.items(), key=lambda kv: -sum(kv[1].values()))
    total = sum(sum(r.values()) for r in per.values())
    print("%s  %s   %d divisions in %d state(s)" % (tag, save, total, len(per)))
    print("    %-26s %-5s %s" % ("state", "divs",
                                 " ".join("%-9s" % c for c in classes)))
    for label, row in (rows if not limit else rows[:limit]):
        print("    %-26s %-5d %s"
              % (label[:26], sum(row.values()),
                 " ".join("%-9d" % row.get(c, 0) for c in classes)))
    if limit and len(rows) > limit:
        rest = sum(sum(r.values()) for _l, r in rows[limit:])
        print("    ... %d more state(s) holding %d divisions (raise --limit, 0 = all)"
              % (len(rows) - limit, rest))


def _oob_block(label, cls_name, owner, members, country, templates, fams, names, p2s):
    """One army (or the UNATTACHED bucket) as four lines: header, families, templates,
    states. `members` is a set of division ids; ids with no `division={}` in `units` are
    counted under `(not deployed)` rather than dropped."""
    per_t, per_f, per_s = collections.Counter(), collections.Counter(), collections.Counter()
    org, stg = [], []
    for uid in members:
        d = country["divisions"].get(uid)
        if d is None:
            per_t["(not deployed)"] += 1
            per_f["?"] += 1
            per_s["(not deployed)"] += 1
            continue
        tid = d.get("tid")
        rec = templates.get(tid) if tid is not None else None
        per_t[template_label(tid, templates)] += 1
        per_f[template_family(rec, fams) if rec else "?"] += 1
        loc = d.get("location")
        st = p2s.get(int(loc)) if loc else None
        per_s[names.get(st, "state %d" % st) if st is not None else "(no state)"] += 1
        if "organisation" in d:
            org.append(d["organisation"])
        if "strength" in d:
            stg.append(d["strength"])
    print("  %-20s %-10s %-22s %3d div  org %5.1f  str %5.1f"
          % (label[:20], cls_name, owner[:22], len(members), _mean(org), _mean(stg)))
    print("      families   %s" % _top(per_f, 6))
    print("      templates  %s" % _top(per_t, 5, xfirst=True, sep=" | "))
    print("      states     %s" % _top(per_s, 5))


def report_oob(tag, save, country, templates, limit):
    """ORDER OF BATTLE: per army - what it is made of, what order covers it, where it is.

    The four questions in one block. Armies are sorted by division count, and every
    division that no army claims lands in the trailing UNATTACHED bucket, so the block
    count closes against `savegame.py army TAG` exactly as --where does."""
    cls = classify(country)
    fams, names, p2s = sub_unit_families(), state_names(), province_state()
    rows = sorted(country["armies"].items(), key=lambda kv: -len(kv[1]["members"]))
    attached = set()
    for _aid, a in rows:
        attached |= a["members"]
    loose = set(country["divisions"]) - attached
    print("%s  %s   %d deployed divisions | %d armies | %d army groups | %d unattached"
          % (tag, save, len(country["divisions"]), len(country["armies"]),
             len(country["groups"]), len(loose)))
    if not templates:
        print("    ! division_templates={} not read - template and family columns blank")
    if not fams:
        print("    ! common/units/*.txt unreadable - family column reads '?'")
    for aid, a in (rows if not limit else rows[:limit]):
        c, src = cls[aid]
        _oob_block(a["name"], c, ("via *" + src) if src else "(own order)", a["members"],
                   country, templates, fams, names, p2s)
    if limit and len(rows) > limit:
        print("  ... %d more armies (raise --limit, 0 = all)" % (len(rows) - limit))
    if loose:
        # No army claims these, so no order can reach them - the owner column is not
        # "(own order)" but nothing at all.
        _oob_block("(UNATTACHED)", "UNATTACHED", "-", loose, country, templates, fams,
                   names, p2s)


def report_templates(tag, save, country, templates, limit):
    """Per-TEMPLATE census of what the country actually fields, and under which order.

    Keyed on the division's own `division_template_id`, not on the template's
    `country=` field: a template can be foreign-designed or inherited, and what matters
    is which template the deployed divisions point at."""
    fams = sub_unit_families()
    dcls = division_classes(country)
    per = collections.defaultdict(lambda: {"n": 0, "org": [], "str": [],
                                           "cls": collections.Counter()})
    for uid, d in country["divisions"].items():
        rec = per[d.get("tid")]
        rec["n"] += 1
        if "organisation" in d:
            rec["org"].append(d["organisation"])
        if "strength" in d:
            rec["str"].append(d["strength"])
        rec["cls"][dcls.get(uid, "UNATTACHED")] += 1
    if not per:
        print("%s  %s   no deployed divisions" % (tag, save))
        return
    print("%s  %s   %d deployed divisions over %d template(s) in the field"
          % (tag, save, len(country["divisions"]), len(per)))
    if not templates:
        print("    ! division_templates={} not read - names and battalions unavailable")
    print("    %-5s %-7s %-8s %-6s %-6s %s"
          % ("n", "family", "bn/coy", "org", "str", "template"))
    rows = sorted(per.items(), key=lambda kv: -kv[1]["n"])
    for tid, r in (rows if not limit else rows[:limit]):
        rec = templates.get(tid) if tid is not None else None
        width = sum(rec["regs"].values()) if rec else 0
        coys = sum(rec["sup"].values()) if rec else 0
        print("    %-5d %-7s %-8s %-6.1f %-6.1f %s"
              % (r["n"], template_family(rec, fams) if rec else "?",
                 "%d/%d" % (width, coys) if rec else "-",
                 _mean(r["org"]), _mean(r["str"]), template_label(tid, templates)))
        print("            battalions %s" % (bn_mix(rec["regs"], 5) if rec else "-"))
        print("            orders     %s" % _top(r["cls"], 6))
    if limit and len(rows) > limit:
        rest = sum(r["n"] for _t, r in rows[limit:])
        print("    ... %d more template(s) holding %d divisions (raise --limit, 0 = all)"
              % (len(rows) - limit, rest))


def main(argv):
    # State names carry accents (Gabès, Kraków); a cp1252 console would mangle them.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args, flags, limit = [], set(), 40
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--limit":
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                sys.exit("--limit needs a number")
            limit = int(argv[i + 1])
            i += 2
            continue
        if a.startswith("--limit="):
            tail = a.split("=", 1)[1]
            if not tail.isdigit():
                sys.exit("--limit needs a number")
            limit = int(tail)
        elif a.startswith("--"):
            flags.add(a)
        else:
            args.append(a)
        i += 1
    if len(args) < 2:
        sys.exit(__doc__.strip().split("usage:")[1].strip())
    tag_arg, files = args[0], args[1:]
    tags = None if tag_arg.upper() == "ALL" else set(tag_arg.upper().split(","))
    # --where needs the same units-section pass as --divisions (it reads `location=`);
    # --invasions reads it too (staging = the scheduled divisions' locations);
    # --oob and --templates need that pass AND the top-level division_templates block.
    want_tmpl = "--oob" in flags or "--templates" in flags
    want_div = (want_tmpl or "--divisions" in flags or "--where" in flags
                or "--invasions" in flags)
    for save in files:
        data, templates, date = scan(save, tags, want_divisions=want_div,
                                     want_templates=want_tmpl)
        if not data:
            print("%s: no matching country" % save)
            continue
        # An order-of-battle question asked about a named country must never be answered
        # with silence: "no output" and "no divisions" are different findings.
        if want_tmpl and tags:
            for tag in sorted(tags - set(data)):
                print("%s  %s   country absent from this save" % (tag, save))
            for tag in sorted(t for t in tags & set(data)
                              if not data[t]["armies"] and not data[t]["groups"]
                              and not data[t]["divisions"]):
                print("%s  %s   no armies and no deployed divisions" % (tag, save))
        for tag in sorted(data):
            country = data[tag]
            # --oob / --templates still have something to say about a country with
            # divisions but no army at all (every division reads UNATTACHED).
            if (not country["armies"] and not country["groups"]
                    and not country["divisions"]):
                continue
            if "--oob" in flags:
                report_oob(tag, save, country, templates, limit)
            elif "--templates" in flags:
                report_templates(tag, save, country, templates, limit)
            elif "--armies" in flags:
                report_armies(tag, save, country, limit)
            elif "--fronts" in flags:
                report_fronts(tag, save, country, limit)
            elif "--invasions" in flags:
                report_invasions(tag, save, country, limit)
            elif "--where" in flags:
                report_where(tag, save, country, limit)
            elif want_div:
                report_divisions(tag, save, country, save_year(date, save))
            else:
                report_census(tag, save, country)
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
