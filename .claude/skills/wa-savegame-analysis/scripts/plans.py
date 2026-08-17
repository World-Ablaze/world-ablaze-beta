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
    3  naval invasion  has `invasion_source`, `convoys`
    5  area defence    has `states`, `area_defense_settings`:
                         102 = a scripted `put_unit_buffers` garrison (WA ai_strategy)
                         100 = an engine-generated area-defence order
       The 102/100 split is how you separate WA's own garrisons from the engine's. Verified
       by matching 102 state sets against the `states = { }` lists in
       common/ai_strategy/WA_AI_MILITARY_COUNTRY_*_THEATRE.txt.

usage: plans.py TAG[,TAG...] FILE... [--armies] [--fronts] [--divisions] [--where]
                [--limit N]
       plans.py ALL FILE... [--limit N]
  (no flag)    per-save census: armies, army groups, divisions per order class
  --armies     one row per army: class, parent army group, division count
  --fronts     every front order (type 1/2) with instance id, creation date, path -> states
  --divisions  org / strength / recent-combat share per order class
  --where      divisions per STATE, split by order class - where they are and what they do
  --limit N    cap rows in --armies / --fronts / --where (default 40)
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
            out.append({
                "type": ty.group(1) if ty else "?",
                "ads": ads.group(1) if ads else None,
                "cd": cd.group(1) if cd else "?",
                "iid": iid.group(1) if iid else "?",
                "path": pth.group(1).strip() if pth else "",
                "states": sts.group(1).strip() if sts else "",
                "can_execute": "can_execute=1" in body,
                "sched": len(set(re.findall(r"scheduled_member=\{ id=(\d+)", body))),
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


def scan(path, tags=None, want_divisions=False):
    """One streaming pass. -> {tag: {'armies': {id: rec}, 'groups': [rec], 'divisions': {}}}

    `tags` None means every country. Only `theatres` (and `units`, when asked) are read.
    """
    out = {}
    with sg.open_save(sg.resolve(path)) as fh:
        for line in fh:
            if line.startswith("countries={"):
                break
        else:
            return out
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
    return out


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
    for aid, a in rows[:limit]:
        c, src = cls[aid]
        print("    %-16s %-10s %-6d %s" % (a["name"][:16], c, len(a["members"]),
                                           src or "(own order)"))
    if len(rows) > limit:
        print("    ... %d more armies" % (len(rows) - limit))


def report_fronts(tag, save, country, limit):
    print("%s  %s" % (tag, save))
    fronts = front_orders(country)
    if not fronts:
        print("    no front orders")
        return
    print("    %-16s %-4s %-8s %-16s %-4s %s"
          % ("owner", "type", "instance", "created", "divs", "path -> states"))
    for name, is_group, o in fronts[:limit]:
        print("    %-16s t=%-2s %-8s %-16s %-4d %s"
              % (("*" if is_group else " ") + name[:15], o["type"], o["iid"],
                 o["cd"].strip('"'), o["sched"], path_states(o["path"]) or "-"))
    if len(fronts) > limit:
        print("    ... %d more front orders" % (len(fronts) - limit))
    print("    * = army-group order (covers its child armies)")


def report_divisions(tag, save, country):
    cls = classify(country)
    year = save[:4]
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
            agg[c]["recent"].append(1 if d.get("lc", "1.1.1.1").split(".")[0] >= year else 0)
    print("%s  %s" % (tag, save))
    print("    %-10s %-5s %-8s %-9s %s" % ("class", "n", "org", "strength", "fought this year"))
    for c in _sorted_classes(agg):
        a = agg[c]
        if not a["strength"]:
            continue
        mean = lambda k: sum(a[k]) / len(a[k])  # noqa: E731
        print("    %-10s %-5d %-8.1f %-9.1f %.0f%%"
              % (c, len(a["strength"]), mean("organisation"), mean("strength"),
                 100 * mean("recent")))


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
    for label, row in rows[:limit]:
        print("    %-26s %-5d %s"
              % (label[:26], sum(row.values()),
                 " ".join("%-9d" % row.get(c, 0) for c in classes)))
    if len(rows) > limit:
        rest = sum(sum(r.values()) for _l, r in rows[limit:])
        print("    ... %d more state(s) holding %d divisions (raise --limit)"
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
    # --where needs the same units-section pass as --divisions (it reads `location=`).
    want_div = "--divisions" in flags or "--where" in flags
    for save in files:
        data = scan(save, tags, want_divisions=want_div)
        if not data:
            print("%s: no matching country" % save)
            continue
        for tag in sorted(data):
            country = data[tag]
            if not country["armies"] and not country["groups"]:
                continue
            if "--armies" in flags:
                report_armies(tag, save, country, limit)
            elif "--fronts" in flags:
                report_fronts(tag, save, country, limit)
            elif "--where" in flags:
                report_where(tag, save, country, limit)
            elif want_div:
                report_divisions(tag, save, country)
            else:
                report_census(tag, save, country)
            print()


if __name__ == "__main__":
    main(sys.argv[1:])
