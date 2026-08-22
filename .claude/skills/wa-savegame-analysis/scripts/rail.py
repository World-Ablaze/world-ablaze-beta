#!/usr/bin/env python
"""Rail continuity between two provinces: is there a railway path, and how thin is it.

Why this exists (2026-08-17, North Africa corridor). The question "is this corridor
railed" was answered inline by reading DIRECT adjacency between the corridor's nodes.
That reported NO RAIL for 12 of 14 hops - and it was noise, not pessimism: corridor nodes
are 1-5 provinces apart, so almost no consecutive pair shares an edge at all. This script
still prints that naive count beside the real one so nobody re-reports it.

TWO FAILURE MODES, TWO LEVERS - the distinction WA_AI_LOGISTICS_MODEL.md insists on:

    BREAK  no rail-continuous path exists at all      -> build rail, or route elsewhere
    THIN   a path exists but its narrowest link is low -> raise the LEVEL of that link

Engine railway throughput is `4 + 8 * level`, so level 1 = 12 and level 3 = 28. A THIN hop
is a throughput problem and must never be reported as a missing railway.

RAIL IS PER-EDGE, NOT PER-PROVINCE. The load-bearing fact. Two provinces can both be
railed with no railway running between them, so "both ends have rail" is not a connection.
The per-edge data is a SECOND, top-level block, distinct from the per-province building
level in `provinces={}`:

    rail_way={ rail_way={ <prov>={ rail_way={ <one level per engine neighbour> } } } }

Confirmed per-edge by three order-free tests on `7c7803a8` 1943.11 (4 456 provinces):
  - every level occurs an EVEN number of times globally - each railed edge contributes its
    level to BOTH endpoints' lists. Holds on all four saves sampled across the campaign
    (1936.6, 1941.6, 1943.11, 1945.6): 20 of 20 level counts even, e.g. 1943.11 reads
    1:3586 2:2880 3:1900 4:816 5:654 and 1936.6 reads 1:3896 2:2860 3:2066 4:514 5:32;
  - non-zero entries per province are 2 for 3 083 provinces (a through-province), 1 for
    307 (a terminus) and 3 for 736 (a junction) - the shape of a rail network;
  - `max(levels)` equals the province's `provinces={}` building level for 4 029 of 4 456.

THE NEIGHBOUR ORDER IS NOT DECODED, and cannot be recovered from this repo's data:
`len(levels) - degree` in `WA_AI_MAP_province_connections.txt` is **always positive**
(+1 for 884 provinces, +2 for 310, up to +5), so the engine's neighbour set is a strict
SUPERSET of WA's generated graph - the generator drops connections. Ascending id,
descending id and file order all score ~44 % on the edge-symmetry test (a correct order
would score ~100 %), i.e. chance. So index -> neighbour is unavailable.

WHAT THIS SCRIPT DOES INSTEAD - level matching, which needs no order. Edge (a,b) is
traversable at `max(levels(a) & levels(b))`, 0 if the two share no level. This is SOUND:
a genuinely railed edge at level L puts L in both endpoints' lists, so no real edge is
ever rejected. It is still a superset of the true network - two provinces can share a
level without that railway being the one between them - so:

    BREAK      sound. No railed route exists.
    ok / THIN  an UPPER BOUND on connectivity.

Measured tightness: of the 7 337 edges whose two endpoints both carry rail, **1 210 (16 %)
share no level and are therefore definitely NOT railed** - that is a sound lower bound on
what the older per-province model got wrong, and this script prints it per save.

The level-matched model finds 2 breaks on the North Africa corridor at 1941.6 and 1943.11
(11957 Gabes -> 1149 Tripoli, and 1130 Derna -> 5078 Libyan Plateau) and 1 from 1944.6 on
(the Tunisia/Libya border gap is never railed). It **reproduces the independently reported
"2 genuine breaks"** that the earlier per-province model in this script under-counted as 1.
A retracted note here previously guessed that figure was a BREAK/THIN conflation; it was
not - the looser model was.

Adjacency comes from the generated `WA_AI_MAP_province_connections.txt`, which is fully
symmetric (59 402 directed edges, 0 asymmetric pairs), so treating it as undirected is
exact. Levels come from the SAVE, never from the `wa_ai_pc_railway_connection_level_*`
globals - those are WA's own cached view and can disagree with what is built.

usage: rail.py A B FILE...                     one province pair
       rail.py --corridor P1,P2,P3,... FILE...  every consecutive hop along a corridor
  --path      print the province path of each hop
  --thin N    flag a hop whose narrowest link is <= N as THIN (default 1)
"""
import collections
import heapq
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402

CONNECTIONS = os.path.join(sg.REPO, "common", "scripted_effects",
                           "WA_AI_MAP_province_connections.txt")
STATE_LOC = os.path.join(sg.REPO, "localisation", "english",
                         "state_names_l_english.yml")

_adj = None
_names = None


def adjacency():
    """{province: {neighbour, ...}} from the generated map data, undirected."""
    global _adj
    if _adj is None:
        _adj = collections.defaultdict(set)
        rx = re.compile(r"province_connections_(\d+) = (\d+)")
        with io.open(CONNECTIONS, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = rx.search(line)
                if m:
                    a, b = int(m.group(1)), int(m.group(2))
                    _adj[a].add(b)
                    _adj[b].add(a)
    return _adj


def state_names():
    global _names
    if _names is None:
        _names = {}
        try:
            with io.open(STATE_LOC, encoding="utf-8-sig", errors="replace") as fh:
                for line in fh:
                    m = re.match(r'\s*STATE_(\d+):\d*\s*"(.*)"', line)
                    if m:
                        _names[int(m.group(1))] = m.group(2)
        except OSError:
            pass
    return _names


def label(prov):
    st = sg.province_state_map().get(prov)
    if st is None:
        return "province %d (no state in map data)" % prov
    return state_names().get(st, "state %d" % st)


def rail_levels(path):
    """{province: set of its railed-edge levels} from the top-level rail_way={} map.

    The block nests one level deeper than it looks - `rail_way={ rail_way={ <prov>={
    rail_way={ ... } } } }` - and its province keys sit at brace depth 2 with their own
    keys at column 0, so this is depth-anchored, never indentation-anchored. Zeros are
    dropped: they are the province's unrailed edges and carry no information here.
    """
    out = {}
    started, d = False, 0
    depth, cur, vals = 0, None, None
    with sg.open_save(sg.resolve(path)) as fh:
        for line in fh:
            if not started:
                if depth == 0 and line.startswith("rail_way={"):
                    started = True
                    d = line.count("{") - line.count("}")
                    continue
                depth += line.count("{") - line.count("}")
                continue
            s = line.strip()
            before = d
            d += line.count("{") - line.count("}")
            if before == 2:
                m = re.match(r"^(\d+)=\{$", s)
                if m:
                    cur, vals = int(m.group(1)), []
            elif before >= 4 and vals is not None and s and re.match(r"^[\d\s]+$", s):
                vals.extend(int(x) for x in s.split())
            if cur is not None and d <= 2:
                lv = {x for x in vals if x}
                if lv:
                    out[cur] = lv
                cur, vals = None, None
            if d <= 0:
                break
    return out


def edge_level(rail, a, b):
    """Rail level of the a-b edge: the widest level both endpoints report, else 0.

    Level matching, because index -> neighbour inside a province's level list is not
    decodable from this repo (see the header). Sound in the direction that matters: a
    genuinely railed edge at level L puts L in BOTH lists, so no real edge is rejected.
    It is still a superset - two provinces can share a level via other edges - so a
    positive answer is an upper bound while a zero is trustworthy.
    """
    common = rail.get(a, ()) and rail.get(b, ())
    if not common:
        return 0
    shared = rail[a] & rail[b]
    return max(shared) if shared else 0


def province_level(rail, prov):
    """The province's widest railed edge - what its `provinces={}` building level tracks."""
    lv = rail.get(prov)
    return max(lv) if lv else 0


def unrailed_bound(rail):
    """(definitely-unrailed, both-ends-railed) over every edge - the model's tightness.

    A sound LOWER bound on what a per-province model ("both ends have rail") gets wrong:
    these edges have rail at both ends yet share no level, so no railway joins them.
    """
    adj = adjacency()
    both = definitely = 0
    for a in rail:
        for b in adj.get(a, ()):
            if b < a or b not in rail:
                continue
            both += 1
            if not (rail[a] & rail[b]):
                definitely += 1
    return definitely, both


def widest(rail, a, b):
    """(narrowest level on the best route, path) - (0, None) when no railed route exists.

    Dijkstra with min-instead-of-sum over EDGE levels. Seeded from the source's widest
    edge, so a level-1 railhead can never yield a route reported as wider than 1.
    """
    start = province_level(rail, a)
    if start <= 0:
        return 0, None
    if a == b:
        return start, [a]
    adj = adjacency()
    best = {a: start}
    pq = [(-start, a, [a])]
    while pq:
        neg, cur, path = heapq.heappop(pq)
        bound = -neg
        if cur == b:
            return bound, path
        if bound < best.get(cur, 0):
            continue
        for nxt in adj.get(cur, ()):
            w = min(bound, edge_level(rail, cur, nxt))
            if w > 0 and w > best.get(nxt, 0):
                best[nxt] = w
                heapq.heappush(pq, (-w, nxt, path + [nxt]))
    return 0, None


def throughput(level):
    """Engine railway supply throughput: 4 + 8 * level (WA_AI_LOGISTICS_MODEL.md)."""
    return 4 + 8 * level


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    corridor, files, show_path, thin_bar = None, [], False, 1
    pair = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--corridor":
            if i + 1 >= len(argv):
                sys.exit("--corridor needs a comma-separated province list")
            corridor = [int(x) for x in re.findall(r"\d+", argv[i + 1])]
            i += 2
            continue
        if a == "--thin":
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                sys.exit("--thin needs a number")
            thin_bar = int(argv[i + 1])
            i += 2
            continue
        if a == "--path":
            show_path = True
        elif a.startswith("--"):
            sys.exit("unknown option %s" % a)
        elif corridor is None and len(pair) < 2 and a.isdigit():
            pair.append(int(a))
        else:
            files.append(a)
        i += 1

    if corridor is None:
        if len(pair) != 2:
            sys.exit(__doc__.strip().split("usage:")[1].strip())
        hops = [(pair[0], pair[1])]
        corridor = pair
    else:
        if len(corridor) < 2:
            sys.exit("--corridor needs at least two provinces")
        hops = list(zip(corridor, corridor[1:]))
    if not files:
        sys.exit("no save files given")

    adj = adjacency()
    no_direct = sum(1 for a, b in hops if b not in adj.get(a, ()))
    off_graph = [p for p in corridor if p not in adj]

    print("# Rail continuity by widest-path over the province graph. BREAK = no railed "
          "route exists")
    print("#   (build rail / reroute); THIN = a route exists but its narrowest link is "
          "low (raise that")
    print("#   link's LEVEL). Throughput is 4 + 8*level, so level 1 = 12 and level 3 = "
          "28 - a THIN hop")
    print("#   is a throughput problem and is NOT a missing railway.")
    print("# Rail is stored per EDGE, and an edge is matched by the widest level BOTH its "
          "provinces")
    print("#   report (index -> neighbour is not decodable - see this script's header). "
          "No real edge is")
    print("#   ever rejected, so a BREAK is sound; the model is still a superset, so an "
          "ok/THIN is an")
    print("#   UPPER BOUND on connectivity. 'both ends have rail' is NOT a connection.")
    if off_graph:
        print("# corridor provinces absent from the adjacency graph (sea/wasteland?): %s"
              % ", ".join(str(p) for p in off_graph))

    for meta, f in sg.sorted_by_date([sg.resolve(x) for x in files]):
        rail = rail_levels(f)
        print("\n=== %s  %s  (%d provinces carry rail) ==="
              % (meta.get("date", "?"), os.path.basename(f), len(rail)))
        print("  %-8s %-8s %-7s %-8s %-5s %-7s %s"
              % ("from", "to", "rail", "narrow", "hops", "verdict", "states"))
        n_break = n_thin = 0
        for a, b in hops:
            level, path = widest(rail, a, b)
            if level <= 0:
                verdict, n_break = "BREAK", n_break + 1
                narrow, nhops = "-", "-"
            else:
                if level <= thin_bar:
                    verdict, n_thin = "THIN", n_thin + 1
                else:
                    verdict = "ok"
                narrow, nhops = str(level), str(len(path) - 1)
            print("  %-8d %-8d %-7s %-8s %-5s %-7s %s -> %s"
                  % (a, b, "%d/%d" % (province_level(rail, a), province_level(rail, b)),
                     narrow, nhops, verdict, label(a), label(b)))
            if show_path and path:
                # Edge levels, not province levels - the edge is what carries supply.
                print("      path: %s" % " ".join(
                    ["%d" % path[0]] + ["=%d= %d" % (edge_level(rail, x, y), y)
                                        for x, y in zip(path, path[1:])]))
        ok = len(hops) - n_break - n_thin
        print("  summary: %d hop(s)  BREAK=%d  THIN=%d (narrowest <= %d, throughput <= %d)"
              "  ok=%d" % (len(hops), n_break, n_thin, thin_bar, throughput(thin_bar), ok))
        definitely, both = unrailed_bound(rail)
        print("  model tightness: of %d edges with rail at BOTH ends, %d (%.0f%%) share no "
              "level and are"
              % (both, definitely, 100.0 * definitely / both if both else 0))
        print("    definitely NOT railed - a per-province model would traverse all %d of "
              "them" % both)
        print("  naive direct-adjacency check would call %d of %d hop(s) 'no rail' - "
              "that reading is noise, corridor nodes are 1-5 provinces apart"
              % (no_direct, len(hops)))


if __name__ == "__main__":
    main(sys.argv[1:])
