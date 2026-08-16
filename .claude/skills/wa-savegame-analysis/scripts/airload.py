#!/usr/bin/env python
"""Air-base LOAD per state: NOMINAL wing slots vs capacity, beside planes present.

Why this exists (2026-08-16, campaign af003548): the engine books air-base capacity per
WING at the wing's fixed type size (`land_air_wing_size` in common/units/air.txt - 100 for
every type except tac_bomber 200, strat/heavy_strat 300, scout/maritime_patrol 25), not per
plane present. A save stores only `count=` (planes present) on the wing, so any reading of
"capacity - planes present" over-reads the free room: on 1944.7_Jul the 11 UK hosting
states looked 23% empty by planes and were at exactly 100.0% nominal in 7 of 11 states.
The nominal size is derivable because the wing pool's `definition=` IS the sub_units key of
air.txt. This script computes both numbers per state.

Structure read (two streaming passes per save):
  states={ <id>={ owner= controller= buildings={ air_base={ level= } } } }   (pass 1)
  strategic_air={ air_base={ id={ id=N } state=S }  <TAG>={ air_wing_pool={ definition=X
                  air_base={ id=N } air_wings={ count= } } } }               (pass 2)
Carrier decks (bases with no state=) are excluded - they are not state capacity.

usage: airload.py [--states 857,127,...] [--owner ENG] [--tag USA] [--top N] [--all] FILE...
  --states  only these state ids
  --owner   only states owned by this tag (e.g. ENG for the British Isles + empire)
  --tag     count only this country's wings in the per-state actual/nominal columns
            (capacity and totals still list every tag; a 'by tag' column shows the mix)
  --top     print the N most loaded states (by nominal) - default 30
  --all     print states with zero wings too
"""
import io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402  (open_save, resolve, iter_state_blocks, _state_buildings)

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
AIR_TXT = os.path.join(REPO, "common", "units", "air.txt")
STATE_LOC = os.path.join(REPO, "localisation", "english", "state_names_l_english.yml")
CAP_PER_LEVEL = 100  # NDefines.NBuildings.AIRBASE_CAPACITY_MULT (common/defines/05_defines.lua)
TAGRE = re.compile(r'^([A-Z][A-Z0-9]{2})=\{$')

# Fallback if air.txt cannot be read (values as of 2026-08-16).
FALLBACK_SIZES = {"tac_bomber": 200, "strat_bomber": 300, "heavy_strat_bomber": 300,
                  "scout_plane": 25, "maritime_patrol_plane": 25}


def wing_sizes():
    """{sub_unit definition: land_air_wing_size} from common/units/air.txt (default 100)."""
    sizes = {}
    try:
        lines = io.open(AIR_TXT, encoding="utf-8", errors="replace").read().split("\n")
    except OSError:
        return dict(FALLBACK_SIZES)
    # line-based brace walk: sub_units={ <name>={ ... land_air_wing_size = N ... } }
    depth, name = 0, None
    for raw in lines:
        s = raw.split("#")[0].strip()
        if not s:
            continue
        if depth == 1:
            m = re.match(r"^([a-z_0-9]+)\s*=\s*\{", s)
            if m:
                name = m.group(1)
        elif depth >= 2 and name:
            m = re.match(r"^land_air_wing_size\s*=\s*(\d+)", s)
            if m:
                sizes[name] = int(m.group(1))
        depth += s.count("{") - s.count("}")
        if depth < 2:
            name = name if depth >= 2 else None
    return sizes or dict(FALLBACK_SIZES)


def state_names():
    names = {}
    try:
        for line in io.open(STATE_LOC, encoding="utf-8-sig", errors="replace"):
            m = re.match(r'\s*STATE_(\d+):\d*\s*"(.*)"', line)
            if m:
                names[int(m.group(1))] = m.group(2)
    except OSError:
        pass
    return names


def parse_states(path):
    """{state_id: (owner, controller, air_base_level)}"""
    out = {}
    with sg.open_save(path) as fh:
        for sid, lines in sg.iter_state_blocks(fh):
            b, owner, ctrl = sg._state_buildings(lines)
            out[sid] = (owner, ctrl, b.get("air_base", 0))
    return out


def parse_wings(path):
    """-> ({base_id: state_id}, [{tag, def, base, count}]) for land + deck wings."""
    base_state = {}
    wings = []
    with sg.open_save(path) as fh:
        depth, found, mode, tag = 0, False, None, None
        curbase = None
        pooldef = poolbase = w = None
        for line in fh:
            s = line.strip()
            d = s.count("{") - s.count("}")
            if not found:
                if depth == 0 and s.startswith("strategic_air={"):
                    found, depth = True, 1
                    continue
                depth += d
                continue
            if depth == 1:
                if d > 0:
                    m = TAGRE.match(s)
                    if s.startswith("air_base={"):
                        mode, curbase = "base", None
                    elif m:
                        mode, tag = "tag", m.group(1)
                        pooldef = poolbase = w = None
                    else:
                        mode = None
            elif mode == "base":
                if depth == 2:
                    if s.startswith("id={ id="):
                        curbase = s.split("id=")[2].split()[0]
                    elif s.startswith("state=") and curbase is not None:
                        base_state[curbase] = int(s.split("=")[1])
            elif mode == "tag":
                if depth == 2 and s.startswith("air_wing_pool={"):
                    pooldef = poolbase = w = None
                elif depth == 3 and s.startswith("definition="):
                    pooldef = s.split("=")[1]
                elif depth == 3 and s.startswith("air_base={ id="):
                    poolbase = s.split("id=")[1].split()[0]
                elif depth == 3 and s.startswith("air_wings={"):
                    w = {"tag": tag, "def": pooldef, "base": poolbase, "count": 0}
                    wings.append(w)
                elif w is not None and depth == 4 and s.startswith("count="):
                    w["count"] = int(s.split("=")[1])
            depth += d
            if depth <= 0:
                break
    return base_state, wings


def main():
    args = sys.argv[1:]
    only_states, owner, only_tag, top, showall = None, None, None, 30, False
    while args and args[0].startswith("--"):
        a = args.pop(0)
        if a == "--states":
            only_states = {int(x) for x in args.pop(0).split(",")}
        elif a == "--owner":
            owner = args.pop(0)
        elif a == "--tag":
            only_tag = args.pop(0)
        elif a == "--top":
            top = int(args.pop(0))
        elif a == "--all":
            showall = True
        else:
            sys.exit("unknown option " + a)
    if not args:
        sys.exit(__doc__)
    sizes = wing_sizes()
    names = state_names()
    for name in args:
        path = sg.resolve(name)
        date = sg.read_meta(path).get("date", "?")
        states = parse_states(path)
        base_state, wings = parse_wings(path)
        per = collections.defaultdict(lambda: {"actual": 0, "nominal": 0, "wings": 0,
                                                "bytag": collections.Counter(),
                                                "types": collections.Counter()})
        deck_wings = 0
        for w in wings:
            sid = base_state.get(w["base"])
            if sid is None:
                deck_wings += 1
                continue
            if only_tag and w["tag"] != only_tag:
                continue
            nom = sizes.get(w["def"], 100)
            p = per[sid]
            p["actual"] += w["count"]
            p["nominal"] += nom
            p["wings"] += 1
            p["bytag"][w["tag"]] += w["count"]
            p["types"][w["def"]] += 1
        rows = []
        for sid, (own, ctrl, lvl) in states.items():
            if only_states and sid not in only_states:
                continue
            if owner and own != owner:
                continue
            p = per.get(sid)
            if p is None and not showall and not only_states:
                continue
            p = p or {"actual": 0, "nominal": 0, "wings": 0, "bytag": {}, "types": {}}
            cap = lvl * CAP_PER_LEVEL
            rows.append((sid, own, ctrl, lvl, cap, p))
        rows.sort(key=lambda r: (-r[5]["nominal"], r[0]))
        print("=== %s (%s)  wing sizes: %s  [land wings %d, deck wings %d excluded]" %
              (date, os.path.basename(name),
               " ".join("%s=%d" % kv for kv in sorted(sizes.items()) if kv[1] != 100) + " others=100",
               len(wings) - deck_wings, deck_wings))
        print("  %-5s %-22s %-4s %-4s %3s %6s %7s %5s %8s %5s %5s  %s" %
              ("state", "name", "own", "ctrl", "lvl", "cap", "actual", "wings", "NOMINAL",
               "act%", "nom%", "by tag / types"))
        tcap = tact = tnom = twings = 0
        for sid, own, ctrl, lvl, cap, p in rows[:top]:
            ap = (100.0 * p["actual"] / cap) if cap else 0
            npc = (100.0 * p["nominal"] / cap) if cap else 0
            flag = " FULL" if cap and p["nominal"] >= cap else ""
            bt = " ".join("%s=%d" % kv for kv in sorted(p["bytag"].items(), key=lambda kv: -kv[1])[:4])
            ty = " ".join("%dx%s" % (n, t) for t, n in sorted(p["types"].items(), key=lambda kv: -kv[1])[:4])
            print("  %-5d %-22s %-4s %-4s %3d %6d %7d %5d %8d %4.0f%% %4.0f%%%s  %s | %s" %
                  (sid, (names.get(sid, "?"))[:22], own or "-", ctrl or "-", lvl, cap,
                   p["actual"], p["wings"], p["nominal"], ap, npc, flag, bt, ty))
        for sid, own, ctrl, lvl, cap, p in rows:
            tcap += cap
            tact += p["actual"]
            tnom += p["nominal"]
            twings += p["wings"]
        if len(rows) > top:
            print("  ... %d more states (totals below include them)" % (len(rows) - top))
        if tcap:
            print("  TOTAL %d states: cap %d  actual %d (%.0f%%)  wings %d  NOMINAL %d (%.0f%%)" %
                  (len(rows), tcap, tact, 100.0 * tact / tcap, twings, tnom, 100.0 * tnom / tcap))
        print("  Read NOMINAL against cap - that is what the engine books; actual is what a plane"
              " count sees. A state at NOMINAL >= cap is full whatever actual says.")


if __name__ == "__main__":
    main()
