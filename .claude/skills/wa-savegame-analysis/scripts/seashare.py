# -*- coding: utf-8 -*-
"""Replicate WA_AI_PRODUCTION_update_coalition_sea_weight (Fix 115/116/117) out of a save.

usage: seashare.py FILE TAG[,TAG,...] [cap|-] [war|faction]
  cap    A* iteration cap to emulate (default none = pure connectivity); the shipped
         pathfind stops at 75, and this BFS is PESSIMISTIC against it - the engine's A*
         is best-first toward a target, so 75 of its iterations reach much further than
         75 breadth-first expansions. Run uncapped for the honest connectivity reading.
  side   'faction' is what the effect does since Fix 117; 'war' reproduces the pre-117
         three-term side and is kept because it is what showed the defect.

THREE TRAPS, each of which produced a confidently wrong table before it was found:
  - `capital=` in a country block is a STATE id, not a province id. Feeding it through the
    province->state map returns a random far-away state (Germany read as Manchukuo).
  - a state omits `controller=` when it equals its owner. Reading the field literally
    leaves most states uncontrolled and the neighbour filter then rejects the whole map.
  - the side definition is the whole ballgame: with `has_war_together_with` in, Japan is an
    Axis coalition member and Germany reads 0.254 instead of 0.056.

Pre-tests checklist R79 leg 1 without waiting for a campaign: does the gauge actually
separate a land coalition from a maritime one?

Faithfulness notes, stated because they decide whether the number is usable:
  - factories: the effect reads num_of_civilian/military/naval_factories, the engine's
    counts. Those are not serialised. Here they are the sum of industrial_complex +
    arms_factory + dockyard LEVELS over states the tag CONTROLS - an upper bound the
    savegame.py `buildings` command documents. Ratios survive that better than absolutes.
  - land access: pathfind type 3 walks neighbour states whose CONTROLLER is ROOT, the
    donor, a subject of either, or a faction ally / co-belligerent of ROOT, skipping
    impassable states, capped at 75 iterations. Replicated as a BFS with the same filter;
    the cap is reported separately so its effect is visible rather than baked in.
  - "our side": self, faction ally, or has_war_together_with - the last replicated as
    "shares at least one enemy with the candidate".
"""
import io, os, re, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import savegame as sg
import rail as rl

FACTORY_KEYS = ("industrial_complex", "arms_factory", "dockyard")


def state_adjacency():
    """{state: {state,...}} lifted from province adjacency through the province->state map."""
    prov2st = sg.province_state_map()
    adj = collections.defaultdict(set)
    for a, nbrs in rl.adjacency().items():
        sa = prov2st.get(a)
        if sa is None:
            continue
        for b in nbrs:
            sb = prov2st.get(b)
            if sb is not None and sb != sa:
                adj[sa].add(sb)
                adj[sb].add(sa)
    return adj


def read_save(path):
    fh = sg.open_save(path)
    ctrl, owner, fac, impassable = {}, {}, collections.Counter(), set()
    for sid, lines in sg.iter_state_blocks(fh):
        o = c = None
        imp = False
        for ln in lines:
            t = ln.strip()
            if t.startswith("owner=") and o is None:
                o = t.split("=", 1)[1].strip('"')
            elif t.startswith("controller=") and c is None:
                c = t.split("=", 1)[1].strip('"')
            elif t.startswith("impassable=yes"):
                imp = True
        if imp:
            impassable.add(sid)
        b, bo, bc = sg._state_buildings(lines)
        if o is None: o = bo
        if c is None: c = bc
        # THE default that decides everything: a state omits controller= when it equals
        # its owner. Reading the field literally leaves most states with no controller and
        # the neighbour filter then rejects the entire map.
        if c is None: c = o
        owner[sid], ctrl[sid] = o, c
        if c:
            fac[c] += sum(int(b.get(k, 0) or 0) for k in FACTORY_KEYS)

    fh = sg.open_save(path)
    factions = {}
    for name, ideo, members in sg.iter_factions(fh):
        for m in members:
            factions[m] = name

    fh = sg.open_save(path)
    enemies = collections.defaultdict(set)
    overlord = {}
    for a, b, kind, _f in sg.iter_relations(fh):
        if kind == "war_relation":
            enemies[a].add(b)
            enemies[b].add(a)
        elif kind == "puppet":
            overlord[b] = a

    fh = sg.open_save(path)
    capital = {}
    tag, depth, incountries = None, 0, False
    for line in fh:
        if not incountries:
            if line.startswith("countries={"):
                incountries, depth = True, 1
            continue
        m = re.match(r"^\t([A-Z0-9]{3})=\{", line)
        if m:
            tag = m.group(1)
        elif tag and line.startswith("\t\tcapital="):
            capital.setdefault(tag, int(line.split("=", 1)[1]))
    return ctrl, owner, fac, impassable, factions, enemies, overlord, capital


SIDE_MODE = "war"


def side_of(tag, factions, enemies, overlord=None):
    """SIDE_MODE 'war': self + faction + anyone sharing an enemy (has_war_together_with).
    SIDE_MODE 'faction': self + faction members + subjects of any of them."""
    out = {tag}
    f = factions.get(tag)
    if f:
        out |= {t for t, ff in factions.items() if ff == f}
    if SIDE_MODE == "faction":
        if overlord:
            out |= {t for t, o in overlord.items() if o in out}
        return out
    mine = enemies.get(tag, set())
    if mine:
        out |= {t for t in enemies if enemies[t] & mine}
    return out


def reachable(start_state, cand, member, adj, ctrl, impassable, factions, enemies,
              overlord, cap=None):
    """BFS with pathfind type 3's neighbour filter. Returns (found, expansions)."""
    allowed_ctrl = {cand, member}
    allowed_ctrl |= {t for t, o in overlord.items() if o in (cand, member)}
    f = factions.get(cand)
    if f:
        allowed_ctrl |= {t for t, ff in factions.items() if ff == f}
    mine = enemies.get(cand, set())
    if mine:
        allowed_ctrl |= {t for t in enemies if enemies[t] & mine}
    target = None
    seen, q, exp = {start_state}, collections.deque([start_state]), 0
    while q:
        cur = q.popleft()
        exp += 1
        if cap is not None and exp > cap:
            return False, exp
        for nb in adj.get(cur, ()):
            if nb in seen or nb in impassable:
                continue
            if ctrl.get(nb) not in allowed_ctrl:
                continue
            if nb == target_state[0]:
                return True, exp
            seen.add(nb)
            q.append(nb)
    return False, exp


target_state = [None]


CAP = None


def main(argv):
    global CAP
    path = argv[0]
    CAP = int(argv[2]) if len(argv) > 2 and argv[2] != "-" else None
    global SIDE_MODE
    if len(argv) > 3: SIDE_MODE = argv[3]
    tags = [t.upper() for t in argv[1].split(",")]
    ctrl, owner, fac, impassable, factions, enemies, overlord, capital = read_save(path)
    adj = state_adjacency()
    prov2st = sg.province_state_map()
    date = sg.read_meta(path).get("date", "?")
    print(f"=== {date}  {os.path.basename(path)} ===")
    for cand in tags:
        # capital= in a country block is a STATE id, not a province id. Mapping it through
        # the province->state table returns a random far-away state (GER read as Manchukuo).
        cstate = capital.get(cand)
        if cstate is None:
            print(f"  {cand}: no capital state")
            continue
        side = side_of(cand, factions, enemies, overlord)
        tot = off = 0
        offlist, onlist = [], []
        for m in sorted(side):
            ic = fac.get(m, 0)
            if ic <= 0:
                continue
            tot += ic
            if m == cand:
                onlist.append((m, ic))
                continue
            mstate = capital.get(m)
            if mstate is None:
                off += ic
                offlist.append((m, ic, "no capital"))
                continue
            target_state[0] = mstate
            found, exp = reachable(cstate, cand, m, adj, ctrl, impassable,
                                   factions, enemies, overlord, cap=CAP)
            if found:
                onlist.append((m, ic))
            else:
                off += ic
                offlist.append((m, ic, f"{exp} exp"))
        share = (off / tot) if tot else 0.0
        print(f"  {cand}: side={len(side)} tags, industry={tot}, unreachable={off}"
              f"   ->  coalition_sea_share = {share:.3f}")
        offlist.sort(key=lambda r: -r[1])
        onlist.sort(key=lambda r: -r[1])
        print("       overland  : " + "  ".join(f"{m}:{ic}" for m, ic in onlist[:8]))
        print("       across sea: " + "  ".join(f"{m}:{ic}" for m, ic, _ in offlist[:8]))


if __name__ == "__main__":
    main(sys.argv[1:])
