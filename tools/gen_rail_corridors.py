"""
Strategic rail corridor generator for World Ablaze AI.

Generates two files under common/scripted_effects/:
  WA_AI_RAIL_CORRIDOR_data.txt   per-corridor control-gate effects (literal state-id
                                 scopes) and build effects (build_railway segments
                                 between anchor victory-point provinces)
  WA_TEST_rail_corridors.txt     the console harness (report + force-build effects;
                                 event recipe in events/wa_test_rail_corridors.txt)

The corridors are an AI-only pathfinding cheat: once every state along a land
corridor is controlled by one faction, a max-level railway is spawned between the
two endpoint cities so strategic redeployment prefers rail over naval transit.
Corridor definitions (owner request 2026-08-27) are embedded in CORRIDORS below.

Inputs (all read-only):
  common/scripted_effects/WA_AI_MAP_province_connections.txt  (land adjacency)
  common/scripted_effects/WA_AI_MAP_state_provinces.txt       (province -> state)
  common/ai_areas/default.txt                                 (north_africa regions)
  map/strategicregions/*.txt                                  (region -> provinces)

Usage (from tools/):
  python gen_rail_corridors.py --dry-run
  python gen_rail_corridors.py
"""

import argparse
import re
import sys
from collections import deque
from pathlib import Path

# (slug, [anchor provinces, in order], gate_mode)
# gate_mode "path"      -> gate states = states crossed by the BFS path
# gate_mode "na_full"   -> gate states = path states + all North-Africa states
#                          (owner rule: Casablanca-Cairo needs NA 100% controlled)
# Waypoints pin each route to the intended geography: plain BFS minimises HOPS,
# which drags trans-African paths into the huge deep-Sahara provinces instead of
# the Sahel / coastal lines the owner asked for (measured 2026-08-27).
CORRIDORS = [
    # Dakar -> Bamako -> Niamey -> N'Djamena -> Khartoum -> Djibouti (Sahel line)
    ("dakar_djibouti", [4948, 4927, 2056, 2081, 12806, 8124], "path"),
    # Pretoria -> Salisbury -> Dodoma -> Kampala -> Khartoum (east-African line)
    ("pretoria_khartoum", [13606, 10929, 12911, 12989, 12806], "path"),
    ("prayagraj_karachi", [7938, 3456], "path"),     # Prayagraj -> Karachi
    ("karachi_fars", [3456, 10797], "path"),         # Karachi -> prov 10797 (Fars)
    ("kuwait_baghdad", [8085, 2097], "path"),        # Kuwait City -> Baghdad
    ("baghdad_cairo", [2097, 7011], "path"),         # Baghdad -> Cairo
    # Casablanca -> Algiers -> Tunis -> Tripoli -> Bengasi -> Alexandria -> Cairo
    ("casablanca_cairo", [7069, 1145, 11969, 1149, 11954, 4076, 7011], "na_full"),
    # Miami -> Washington -> New York -> Boston -> Halifax (eastern seaboard)
    ("miami_halifax", [1843, 3957, 3878, 6732, 7361], "path"),
]

NORTH_AFRICA_REGIONS = None  # parsed from common/ai_areas/default.txt


def parse_adjacency(path: Path) -> dict:
    adj = {}
    rx = re.compile(r"province_connections_(\d+) = (\d+)")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = rx.search(line)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                adj.setdefault(a, set()).add(b)
    return adj


def parse_province_states(path: Path) -> dict:
    prov_state = {}
    rx = re.compile(r"province_state_id\^(\d+) = (\d+)")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = rx.search(line)
            if m:
                prov_state[int(m.group(1))] = int(m.group(2))
    return prov_state


def parse_north_africa_regions(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"north_africa\s*=\s*\{\s*strategic_regions\s*=\s*\{([^}]*)\}", text)
    if not m:
        raise SystemExit("north_africa area not found in ai_areas/default.txt")
    return [int(x) for x in m.group(1).split()]


def parse_region_provinces(region_dir: Path, region_ids: set) -> set:
    provs = set()
    for f in region_dir.glob("*.txt"):
        text = f.read_text(encoding="utf-8", errors="replace")
        mid = re.search(r"id\s*=\s*(\d+)", text)
        if not mid or int(mid.group(1)) not in region_ids:
            continue
        mp = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
        if mp:
            body = re.sub(r"#[^\n]*", "", mp.group(1))
            provs.update(int(x) for x in body.split())
    return provs


def parse_special_pairs(path: Path):
    """Province pairs from map/adjacencies.csv, split by kind.

    Returns (impassable, other): `impassable` rows BLOCK a bmp-adjacency in the engine.
    The shared province_connections generator strips them from the land graph since
    2026-08-27; the strip below is kept as defense against pathing over a stale
    generated file. `other` rows (straits, canals) are real crossings a railway may
    still not be buildable over - warned, not removed.
    """
    impassable, other = set(), set()
    if not path.exists():
        return impassable, other
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            cells = line.split(";")
            try:
                a, b = int(cells[0]), int(cells[1])
            except (ValueError, IndexError):
                continue
            kind = cells[2].strip().lower() if len(cells) > 2 else ""
            dest = impassable if kind == "impassable" else other
            dest.add((a, b))
            dest.add((b, a))
    return impassable, other


def bfs_path(adj: dict, start: int, goal: int) -> list:
    if start == goal:
        return [start]
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in adj.get(cur, ()):
            if nxt not in prev:
                prev[nxt] = cur
                if nxt == goal:
                    path = [goal]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    return list(reversed(path))
                q.append(nxt)
    return []


def ordered_unique(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--mod-root", type=Path, default=Path(".."))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = args.mod_root
    fx = root / "common" / "scripted_effects"
    adj = parse_adjacency(fx / "WA_AI_MAP_province_connections.txt")
    prov_state = parse_province_states(fx / "WA_AI_MAP_state_provinces.txt")
    impassable_pairs, special_pairs = parse_special_pairs(root / "map" / "adjacencies.csv")
    for a, b in impassable_pairs:
        if a in adj:
            adj[a].discard(b)
        if b in adj:
            adj[b].discard(a)
    na_regions = set(parse_north_africa_regions(root / "common" / "ai_areas" / "default.txt"))
    na_provs = parse_region_provinces(root / "map" / "strategicregions", na_regions)

    # A state belongs to North Africa when at least half of its provinces sit in
    # the north_africa strategic regions (states can straddle a region border).
    state_provs = {}
    for p, s in prov_state.items():
        state_provs.setdefault(s, []).append(p)
    na_states = sorted(
        s for s, plist in state_provs.items()
        if sum(1 for p in plist if p in na_provs) * 2 >= len(plist)
    )

    corridors = []
    summary = []
    for idx, (slug, anchors, gate_mode) in enumerate(CORRIDORS, start=1):
        path_provs = []
        for a, b in zip(anchors, anchors[1:]):
            seg = bfs_path(adj, a, b)
            if not seg:
                raise SystemExit(f"no land path {a} -> {b} for corridor {slug}")
            path_provs.extend(seg)
        path_provs = ordered_unique(path_provs)
        gate_states = ordered_unique(prov_state[p] for p in path_provs if p in prov_state)
        if gate_mode == "na_full":
            extra = [s for s in na_states if s not in gate_states]
            gate_states = gate_states + extra

        # cheap short-circuit: evaluate the far endpoint's state second, so a
        # corridor whose two ends are not even on the same side fails after two
        # state reads instead of walking the whole list.
        if len(gate_states) > 2:
            far = prov_state[anchors[-1]]
            rest = [s for s in gate_states if s not in (gate_states[0], far)]
            gate_states = [gate_states[0], far] + rest

        for a, b in zip(path_provs, path_provs[1:]):
            if (a, b) in special_pairs:
                print(f"WARNING: corridor {slug} path uses special adjacency {a}-{b} "
                      f"(map/adjacencies.csv) - build_railway may reject it; add a waypoint")

        corridors.append((idx, slug, anchors, gate_mode, gate_states, path_provs))
        summary.append(
            f"#   {idx}. {slug}: {len(path_provs)} provinces, "
            f"{len(gate_states)} gate states ({gate_mode})"
        )

    # ---------------- data file: gates + builds ----------------
    lines = []
    lines.append("# GENERATED FILE - do not hand-edit. Regenerate with:")
    lines.append("#   cd tools && python gen_rail_corridors.py")
    lines.append("# [rail-corridors] AI-only pathfinding cheat: spawns max-level railways along")
    lines.append("# faction-controlled land corridors so strategic redeployment stops shipping")
    lines.append("# divisions across oceans. No economic intent; dispatch and gating rules live in")
    lines.append("# WA_AI_RAIL_CORRIDOR_effects.txt / WA_AI_RAIL_CORRIDOR_triggers.txt.")
    lines.append("# Corridor summary:")
    lines.extend(summary)
    lines.append("")
    lines.append("@WA_RAIL_CORRIDOR_LEVEL = 5  # engine MAX_RAILWAY_LEVEL (base 00_defines.lua:4263)")
    lines.append("")
    for idx, slug, anchors, gate_mode, gate_states, path_provs in corridors:
        lines.append(f"# corridor {idx}: {slug} - anchors {anchors} - gate {gate_mode}, "
                     f"{len(gate_states)} states")
        lines.append(f"# Sets _rc_ok = 0 unless every gate state is same-side with the anchor")
        lines.append(f"# (= controller of the first endpoint's state). Order: endpoint A, endpoint B,")
        lines.append(f"# then the rest - two reads kill the walk when the ends are not even allied.")
        lines.append(f"WA_AI_RAIL_CORRIDOR_gate_{idx} = {{")
        lines.append("\tset_temp_variable = { _rc_ok = 1 }")
        lines.append("\tset_temp_variable = { _rc_anchor = 0 }")
        lines.append(f"\t{gate_states[0]} = {{ CONTROLLER = {{ set_temp_variable = {{ _rc_anchor = THIS.id }} }} }}")
        lines.append("\t# an unset anchor must fail the gate, never reach a var: compare as garbage")
        lines.append("\tif = { limit = { check_variable = { _rc_anchor = 0 } } set_temp_variable = { _rc_ok = 0 } }")
        lines.append("\tif = {")
        lines.append("\t\tlimit = {")
        lines.append("\t\t\tNOT = {")
        lines.append("\t\t\t\tAND = {")
        for s in gate_states:
            lines.append(f"\t\t\t\t\t{s} = {{ WA_AI_RAIL_CORRIDOR_state_is_friendly = yes }}")
        lines.append("\t\t\t\t}")
        lines.append("\t\t\t}")
        lines.append("\t\t}")
        lines.append("\t\tset_temp_variable = { _rc_ok = 0 }")
        lines.append("\t}")
        lines.append("}")
        lines.append("")
        lines.append(f"# Built EDGE BY EDGE (path = {{ a b }}), the only build_railway form this repo has")
        lines.append(f"# proven in campaigns (PC core uses it for every railway project). A 30-province")
        lines.append(f"# path list no-opped silently on the 2026-08-27 owner test (corridor 1: built flag")
        lines.append(f"# set, zero track on the map) while shorter-legged corridors built - per-edge builds")
        lines.append(f"# salvage every good edge, log each refused one, and keep the PC mirror honest:")
        lines.append(f"# the mirror (readers: PC railway_helpers/_core, WA_AI_pathfinding_effects) is")
        lines.append(f"# stamped ONLY for an edge that passed can_build_railway and was actually built.")
        lines.append(f"WA_AI_RAIL_CORRIDOR_build_{idx} = {{")
        for a, b in zip(path_provs, path_provs[1:]):
            lines.append(f"\tif = {{ limit = {{ can_build_railway = {{ path = {{ {a} {b} }} }} }}")
            lines.append(f"\t\tbuild_railway = {{ level = @WA_RAIL_CORRIDOR_LEVEL path = {{ {a} {b} }} }}")
            lines.append(f"\t\tset_variable = {{ global.WA_AI_PC_railway_connections^{a} = 1 }}")
            lines.append(f"\t\tset_variable = {{ global.WA_AI_PC_railway_connections^{b} = 1 }}")
            lines.append(f"\t\tset_variable = {{ global.WA_AI_PC_railway_connection_level_{a}^{b} = @WA_RAIL_CORRIDOR_LEVEL }}")
            lines.append(f"\t\tset_variable = {{ global.WA_AI_PC_railway_connection_level_{b}^{a} = @WA_RAIL_CORRIDOR_LEVEL }}")
            lines.append("\t}")
            lines.append(f"\telse_if = {{ limit = {{ NOT = {{ has_railway_connection = {{ path = {{ {a} {b} }} }} }} }}")
            lines.append(f'\t\tlog = "[GetDateText] WA_AI_RAIL_CORRIDOR: corridor {idx} edge {a}-{b} REFUSED by can_build_railway and not already railed"')
            lines.append("\t}")
        lines.append(f"\t# endpoint-to-endpoint post-check: a corridor that did not come out connected")
        lines.append(f"\t# latches an _incomplete flag (save-visible) instead of failing silently.")
        lines.append(f"\tif = {{ limit = {{ NOT = {{ has_railway_connection = {{ start_province = {anchors[0]} target_province = {anchors[-1]} }} }} }}")
        lines.append(f"\t\tset_global_flag = WA_rail_corridor_{idx}_incomplete")
        lines.append(f'\t\tlog = "[GetDateText] WA_AI_RAIL_CORRIDOR: corridor {idx} ({slug}) INCOMPLETE after build - see REFUSED edges above"')
        lines.append("\t}")
        lines.append("}")
        lines.append("")
    data_text = "\n".join(lines) + "\n"

    # ---------------- harness file: report + force-builds ----------------
    # Independent walk on purpose (wa-testing contract v1 piece 4): the per-state
    # verdict below duplicates the predicate INLINE instead of calling the shipped
    # WA_AI_RAIL_CORRIDOR_state_is_friendly, so a disagreement between the logged
    # verdicts and the shipped gate's _rc_ok localises the fault.
    INLINE_PRED = (
        "OR = {{ is_controlled_by = var:_rt_anchor "
        "CONTROLLER = {{ OR = {{ is_in_faction_with = var:_rt_anchor "
        "is_subject_of = var:_rt_anchor "
        "var:_rt_anchor = {{ is_subject_of = PREV }} "
        "OVERLORD = {{ is_in_faction_with = var:_rt_anchor }} }} }} }}"
    )
    h = []
    h.append("# GENERATED FILE - do not hand-edit. Regenerate with:")
    h.append("#   cd tools && python gen_rail_corridors.py")
    h.append("# [rail-corridors] console harness for the strategic rail corridor cheat.")
    h.append("# Recipe: events/wa_test_rail_corridors.txt (event wa_test_rail.1 = report;")
    h.append("# wa_test_rail.11-18 = force-build corridor 1-8). harness-contract: v1 (wa-testing SKILL).")
    h.append("")
    h.append("WA_TEST_rail_corridors_report = {")
    h.append('\tlog = "=== RAIL CORRIDOR TEST [GetDateText] ==="')
    h.append("\t### CONTEXT HEADER - printed FIRST, on every run. harness-contract: v1 (wa-testing SKILL).")
    h.append('\tlog = "  who   : THIS = [This.GetName]   ROOT = [Root.GetName]   FROM = [From.GetName]"')
    for i in range(1, 6):
        h.append(f"\tset_temp_variable = {{ _rt_e{i}_ = 0 }}")
    h.append("\tif = { limit = { always = yes } set_temp_variable = { _rt_e1_ = 1 } }")
    h.append("\tif = { limit = { tag = ROOT } set_temp_variable = { _rt_e2_ = 1 } }")
    h.append("\tif = { limit = { tag = THIS } set_temp_variable = { _rt_e3_ = 1 } }")
    h.append("\tif = { limit = { ROOT = { always = yes } } set_temp_variable = { _rt_e4_ = 1 } }")
    h.append("\tif = { limit = { NOT = { always = yes } } set_temp_variable = { _rt_e5_ = 1 } }")
    h.append('\tlog = "  scope : always=[?_rt_e1_|.0]  I-am-ROOT=[?_rt_e2_|.0]  I-am-THIS=[?_rt_e3_|.0]  ROOT-scope-usable=[?_rt_e4_|.0]  control-false=[?_rt_e5_|.0]"')
    h.append('\tlog = "            (anything but 1 1 1 1 0 here: STOP. Nothing below is a measurement. Re-fire the same report from another event file - tag GER then event wa_iso.3 - before editing a line of this effect.)"')
    for idx, slug, anchors, gate_mode, gate_states, path_provs in corridors:
        h.append(f'\tlog = "  corridor {idx} {slug}: anchors {anchors[0]} -> {anchors[-1]}, {len(gate_states)} gate states"')
        h.append(f"\tif = {{ limit = {{ has_global_flag = WA_rail_corridor_{idx}_built }}")
        h.append(f'\t\tlog = "    corridor {idx}: already BUILT (global flag set)"')
        h.append("\t}")
        h.append("\telse = {")
        h.append(f"\t\tWA_AI_RAIL_CORRIDOR_gate_{idx} = yes")
        h.append(f'\t\tlog = "    corridor {idx}: shipped gate _rc_ok = [?_rc_ok|.0]"')
        h.append("\t\tset_temp_variable = { _rt_anchor = 0 }")
        h.append(f"\t\t{gate_states[0]} = {{ CONTROLLER = {{")
        h.append("\t\t\tset_temp_variable = { _rt_anchor = THIS.id }")
        h.append(f'\t\t\tlog = "    corridor {idx}: anchor controller = [This.GetName]"')
        h.append("\t\t} }")
        h.append("\t\tif = { limit = { check_variable = { _rt_anchor = 0 } }")
        h.append(f'\t\t\tlog = "    corridor {idx}: NO ANCHOR CONTROLLER - per-state verdicts below are void"')
        h.append("\t\t}")
        for s in gate_states:
            h.append(f"\t\t{s} = {{ if = {{ limit = {{ NOT = {{ {INLINE_PRED.format()} }} }}")
            h.append(f'\t\t\tCONTROLLER = {{ log = "    corridor {idx} BLOCKED at state {s} by [This.GetName]" }}')
            h.append("\t\t} }")
        h.append("\t}")
        h.append(f"\tif = {{ limit = {{ has_railway_connection = {{ start_province = {anchors[0]} target_province = {anchors[-1]} }} }}")
        h.append(f'\t\tlog = "    corridor {idx}: endpoint rail connection = YES"')
        h.append("\t}")
        h.append("\telse = {")
        h.append(f'\t\tlog = "    corridor {idx}: endpoint rail connection = NO"')
        h.append("\t}")
    h.append('\tlog = "=== RAIL CORRIDOR TEST END ==="')
    h.append("}")
    h.append("")
    for idx, slug, anchors, gate_mode, gate_states, path_provs in corridors:
        h.append(f"# Force-build corridor {idx} ({slug}) regardless of control - visual check of")
        h.append("# build_railway behaviour (level clamp, path taken) in the supply mapmode.")
        h.append(f"WA_TEST_rail_corridors_force_build_{idx} = {{")
        h.append(f"\tWA_AI_RAIL_CORRIDOR_build_{idx} = yes")
        h.append(f"\tset_global_flag = WA_rail_corridor_{idx}_built")
        h.append(f'\tlog = "WA_TEST rail corridors: FORCE-BUILT corridor {idx} ({slug})"')
        h.append("}")
        h.append("")
    harness_text = "\n".join(h) + "\n"

    data_path = fx / "WA_AI_RAIL_CORRIDOR_data.txt"
    harness_path = fx / "WA_TEST_rail_corridors.txt"
    print("\n".join(summary))
    if args.dry_run:
        print(f"[dry-run] would write {data_path} ({len(data_text)} bytes)")
        print(f"[dry-run] would write {harness_path} ({len(harness_text)} bytes)")
        return 0
    data_path.write_text(data_text, encoding="utf-8", newline="\n")
    harness_path.write_text(harness_text, encoding="utf-8", newline="\n")
    print(f"wrote {data_path} ({len(data_text)} bytes)")
    print(f"wrote {harness_path} ({len(harness_text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
