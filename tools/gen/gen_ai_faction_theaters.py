#!/usr/bin/env python3
"""
Generate WA's common/ai_faction_theaters/ai_faction_theaters.txt.

WHY THIS EXISTS
---------------
`common/ai_faction_theaters` is the engine's faction-theatre definition: which strategic
regions form a theatre, how likely a faction member is to take it, when to abandon it.
WA did not replace the folder, so vanilla's file ran in every campaign - and WA re-cut the
strategic-region map (383 regions against vanilla's 304), reusing ids for different
geography. Vanilla region 239 is Alborz in Iran; WA region 239 is Northern France. The
theatres therefore described a map that no longer existed.

The engine resolves a `theatre_distribution_demand_increase id = <state>` through the LIVE
region map to the theatre that contains it, so the mismatch is not cosmetic: measured
2026-08-18, of WA's six writers of that type, two resolved correctly, three resolved to no
theatre at all, and Canada's European demand landed on the Middle East theatre.

WHAT IT DOES
------------
Keeps every vanilla theatre's identity, `ai_will_do`, `cancel`, `preferred_countries` and
`can_skip_first_region` verbatim, and rewrites ONLY the `regions = { ... }` list: for each
theatre it takes the province area the vanilla region list covered and emits the WA region
ids that cover the same ground (a WA region joins the theatre when at least
--overlap of its provinces lie inside that area).

Region order is load-bearing: the engine requires the FIRST region in the list to be
available before it will create the theatre, unless `can_skip_first_region = yes`. The
generator therefore puts the WA regions covering vanilla's first region first.

The engine also requires a theatre's area to be CONNECTED. The generator measures that on
map/provinces.bmp directly - the generated WA_AI_MAP_province_connections effect is a LAND
pathfinding graph with no sea province in it, and theatres mix land and sea. Regions that
come out detached from the theatre's main body are dropped, unless vanilla itself named
them: vanilla's own strategic regions carry stray high-id provinces (its `163-Amazonian
Brazil` owns the Scheldt) which WA re-homed into 1-2 province regions, so a single shared
province otherwise scores a 100% overlap and puts Lake Ladoga in the Brazil theatre.
Positive control: 29 of vanilla's 30 theatres pass this connectivity test on the vanilla
map; `north_sea_region` (Ireland) is the one that does not, and WA keeps that as-is.

USAGE
-----
    python gen_ai_faction_theaters.py --dry-run      # report only, write nothing
    python gen_ai_faction_theaters.py                # write the file

The default --mod-root is the repo this script lives in; run it from any directory.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Set, Tuple

DEFAULT_INSTALL = Path(r"C:/Jeux/steamapps/common/Hearts of Iron IV")
DEFAULT_OVERLAP = 0.5


# ---------------------------------------------------------------- parsing helpers


def strip_comments(text: str) -> str:
    """Blank out comments WITHOUT changing length, so offsets stay valid against the raw text."""
    return re.sub(r"#[^\n]*", lambda m: " " * len(m.group(0)), text)


def match_brace(text: str, open_index: int) -> int:
    """Return the index just past the '}' matching the '{' at open_index."""
    depth = 0
    i = open_index
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced braces")


def load_regions(directory: Path) -> Dict[int, Tuple[str, Set[int]]]:
    """strategic region id -> (file stem, province set)."""
    out: Dict[int, Tuple[str, Set[int]]] = {}
    for path in sorted(directory.glob("*.txt")):
        body = strip_comments(path.read_text(encoding="utf-8-sig", errors="replace"))
        rid = re.search(r"strategic_region\s*=\s*\{\s*id\s*=\s*(\d+)", body)
        provinces = re.search(r"provinces\s*=\s*\{([^}]*)\}", body)
        if not rid:
            continue
        ids = {int(p) for p in provinces.group(1).split()} if provinces else set()
        out[int(rid.group(1))] = (path.stem, ids)
    return out


class Theatre:
    def __init__(self, name: str, body: str):
        self.name = name
        self.body = body
        block = re.search(r"regions\s*=\s*\{", strip_comments(body))
        if not block:
            raise ValueError(f"{name}: no regions block")
        end = match_brace(strip_comments(body), block.end() - 1)
        self.vanilla_regions = [
            int(x) for x in strip_comments(body)[block.end() : end - 1].split()
        ]
        self.new_regions: List[int] = []


def load_theatres(path: Path) -> List[Theatre]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    bare = strip_comments(text)
    out: List[Theatre] = []
    for m in re.finditer(r"^(\w+)\s*=\s*\{", bare, re.M):
        end = match_brace(bare, m.end() - 1)
        out.append(Theatre(m.group(1), text[m.start() : end]))
    return out


def load_province_adjacency(map_dir: Path) -> Dict[int, Set[int]]:
    """
    True province adjacency, read off provinces.bmp.

    The generated WA_AI_MAP_province_connections effect is NOT usable here: it is a land
    pathfinding graph and carries no sea province at all, which makes every naval theatre
    read as N disconnected pieces. Theatres mix land and sea, so connectivity has to be
    measured on the map itself. ~1s with numpy.
    """
    import csv

    import numpy as np
    from PIL import Image

    rgb_to_id: Dict[int, int] = {}
    with open(map_dir / "definition.csv", encoding="utf-8", errors="replace") as handle:
        for row in csv.reader(handle, delimiter=";"):
            if len(row) >= 5 and row[0].isdigit():
                key = (int(row[1]) << 16) | (int(row[2]) << 8) | int(row[3])
                rgb_to_id[key] = int(row[0])

    image = np.array(Image.open(map_dir / "provinces.bmp").convert("RGB"), dtype=np.uint32)
    keys = (image[:, :, 0] << 16) | (image[:, :, 1] << 8) | image[:, :, 2]
    lut = np.full(1 << 24, -1, dtype=np.int32)
    for key, pid in rgb_to_id.items():
        lut[key] = pid
    provinces = lut[keys]

    adjacency: Dict[int, Set[int]] = defaultdict(set)

    def collect(left, right) -> None:
        mask = (left != right) & (left >= 0) & (right >= 0)
        pairs = np.unique(np.stack([left[mask], right[mask]], 1), axis=0)
        for a, b in pairs:
            adjacency[int(a)].add(int(b))
            adjacency[int(b)].add(int(a))

    collect(provinces[:, :-1], provinces[:, 1:])
    collect(provinces[:-1, :], provinces[1:, :])
    collect(provinces[:, -1], provinces[:, 0])  # the map wraps east-west

    # straits and canals are adjacency the bitmap cannot show
    special = map_dir / "adjacencies.csv"
    if special.exists():
        with open(special, encoding="utf-8", errors="replace") as handle:
            for row in csv.reader(handle, delimiter=";"):
                if len(row) >= 2 and row[0].strip().isdigit() and row[1].strip().isdigit():
                    a, b = int(row[0]), int(row[1])
                    if a >= 0 and b >= 0:
                        adjacency[a].add(b)
                        adjacency[b].add(a)
    return adjacency


# ---------------------------------------------------------------- the remap


def remap(
    theatre: Theatre,
    vanilla: Dict[int, Tuple[str, Set[int]]],
    wa: Dict[int, Tuple[str, Set[int]]],
    overlap: float,
) -> List[str]:
    """Fill theatre.new_regions. Returns warnings."""
    warnings: List[str] = []
    missing = [r for r in theatre.vanilla_regions if r not in vanilla]
    if missing:
        warnings.append(f"{theatre.name}: vanilla regions absent from the vanilla map: {missing}")

    area: Set[int] = set()
    for rid in theatre.vanilla_regions:
        area |= vanilla.get(rid, ("", set()))[1]
    anchor: Set[int] = vanilla.get(theatre.vanilla_regions[0], ("", set()))[1]

    scored: List[Tuple[float, float, int]] = []
    for rid, (_stem, provinces) in wa.items():
        if not provinces:
            continue
        share = len(provinces & area) / len(provinces)
        if share < overlap:
            continue
        anchor_share = len(provinces & anchor) / len(provinces)
        scored.append((anchor_share, share, rid))

    # The anchor is not optional: the engine will not create the theatre until its FIRST
    # region is available, so whichever WA region covers most of vanilla's anchor is force-
    # included even if it falls under the ratio threshold. WA re-cut region 139 South Africa
    # wider than vanilla's, which put it at 0.47 and would have decapitated that theatre.
    if anchor:
        best = max(wa.items(), key=lambda kv: len(kv[1][1] & anchor))
        if len(best[1][1] & anchor) > 0 and best[0] not in {rid for _a, _s, rid in scored}:
            forced = len(best[1][1] & anchor) / len(best[1][1])
            scored.append((forced, len(best[1][1] & area) / len(best[1][1]), best[0]))
            warnings.append(
                f"{theatre.name}: anchor region {best[0]} ({wa[best[0]][0]}) force-included at "
                f"overlap {forced:.2f}, under the {overlap} threshold"
            )

    # anchor regions first (the engine gates theatre creation on the first entry),
    # then by how completely the region sits inside the theatre, then by id for stability.
    scored.sort(key=lambda t: (-round(t[0], 6), -round(t[1], 6), t[2]))
    theatre.new_regions = [rid for _a, _s, rid in scored]

    if not theatre.new_regions:
        warnings.append(f"{theatre.name}: NO WA region reaches the overlap threshold - theatre dropped")
    elif scored[0][0] == 0.0:
        warnings.append(
            f"{theatre.name}: no WA region covers vanilla's anchor region "
            f"{theatre.vanilla_regions[0]} - first entry is a fallback"
        )
    return warnings


def prune_detached(
    theatre: Theatre,
    wa: Dict[int, Tuple[str, Set[int]]],
    adjacency: Dict[int, Set[int]],
) -> List[str]:
    """
    Drop regions that are not reachable from the theatre's main body.

    Vanilla's own strategic regions carry a handful of stray high-id provinces - vanilla
    `163-Amazonian Brazil` owns province 13353, which is the Scheldt in Belgium, and
    `284-Southern Andes` owns 13304, the Chesapeake. WA re-homed those strays into small
    1-2 province regions, so a single shared province scores a 100% overlap and drops
    Lake Ladoga into the Brazil theatre. Connectivity is what tells the two apart.

    A detached piece is KEPT when it contains a region id vanilla itself named for this
    theatre - vanilla wanted the Red Sea in north_africa, and vanilla's own north_sea_region
    is disconnected the same way (positive control: 29 of 30 vanilla theatres pass this test
    on the vanilla map, north_sea_region/Ireland is the one that does not).
    """
    if not theatre.new_regions:
        return []
    components = connected(theatre.new_regions, wa, adjacency)
    if len(components) <= 1:
        return []
    components.sort(key=len, reverse=True)
    intended = set(theatre.vanilla_regions)
    keep: Set[int] = set(components[0])
    notes: List[str] = []
    for piece in components[1:]:
        if intended & set(piece):
            keep |= set(piece)
            notes.append(
                f"{theatre.name}: keeping detached piece {[wa[r][0] for r in piece]} - "
                f"vanilla named it too"
            )
        else:
            notes.append(
                f"{theatre.name}: dropped detached {[wa[r][0] for r in piece]} - "
                f"stray-province artefact, vanilla never named it"
            )
    theatre.new_regions = [rid for rid in theatre.new_regions if rid in keep]
    return notes


def connected(regions: List[int], wa: Dict[int, Tuple[str, Set[int]]],
              adjacency: Dict[int, Set[int]]) -> List[List[int]]:
    """Split a region list into connected components using province adjacency."""
    province_owner: Dict[int, int] = {}
    for rid in regions:
        for p in wa.get(rid, ("", set()))[1]:
            province_owner[p] = rid

    neighbours: Dict[int, Set[int]] = {rid: set() for rid in regions}
    for province, owner in province_owner.items():
        for other in adjacency.get(province, ()):
            target = province_owner.get(other)
            if target is not None and target != owner:
                neighbours[owner].add(target)
                neighbours[target].add(owner)

    seen: Set[int] = set()
    components: List[List[int]] = []
    for rid in regions:
        if rid in seen:
            continue
        queue = deque([rid])
        seen.add(rid)
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for nxt in neighbours[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        components.append(sorted(component))
    return components


# ---------------------------------------------------------------- emit


def render(theatre: Theatre, wa: Dict[int, Tuple[str, Set[int]]]) -> str:
    """Rewrite the theatre block with the new regions list, everything else verbatim."""
    body = theatre.body
    bare = strip_comments(body)
    block = re.search(r"regions\s*=\s*\{", bare)
    end = match_brace(bare, block.end() - 1)
    lines = ["\tregions = {"]
    for rid in theatre.new_regions:
        lines.append(f"\t\t{rid}\t# {wa[rid][0]}")
    lines.append("\t}")
    return body[: block.start()] + "\n".join(lines) + body[end:]


HEADER = """\
############################################################################################################
# WA AI faction theatres - GENERATED, do not hand-edit
############################################################################################################
# Source of truth: tools/gen/gen_ai_faction_theaters.py. Regenerate with:
#     python tools/gen/gen_ai_faction_theaters.py
#
# WHY THIS FILE EXISTS AS A WA FILE
# Vanilla ships this file and WA did not replace the folder, so vanilla's copy ran in every
# campaign. WA re-cut the strategic-region map - <WA_COUNT> regions against vanilla's <VANILLA_COUNT> -
# and reused ids for different ground (vanilla 239 = Alborz, WA 239 = Northern France), so the
# vanilla region lists described a map that no longer existed. The engine resolves
# `theatre_distribution_demand_increase id = <state>` through the LIVE region map, so the
# mismatch was live: of WA's six writers of that type, three resolved to no theatre and one
# put Canada's European demand on the Middle East theatre (measured 2026-08-18).
#
# WHAT IS GENERATED AND WHAT IS NOT
# Every theatre's name, ai_will_do, cancel, preferred_countries and can_skip_first_region are
# vanilla's, copied verbatim - change them by editing this file's SOURCE in the install and
# re-running, or by taking ownership of a block here and saying so at the site.
# Only `regions = { ... }` is computed: the WA regions covering the province area the vanilla
# list covered, at an overlap threshold of <OVERLAP>. First entry matters - the engine will not
# create a theatre until its first region is available unless can_skip_first_region = yes - so
# the regions covering vanilla's anchor region are emitted first.
############################################################################################################

"""


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--install", type=Path, default=DEFAULT_INSTALL, help="HOI4 install directory")
    parser.add_argument("--mod-root", type=Path, default=Path(__file__).resolve().parents[2], help="mod root (default: the repo this script lives in)")
    parser.add_argument("--overlap", type=float, default=DEFAULT_OVERLAP,
                        help="minimum share of a WA region's provinces that must lie in the theatre")
    parser.add_argument("--dry-run", action="store_true", help="report only, write nothing")
    args = parser.parse_args(argv)

    source = args.install / "common/ai_faction_theaters/ai_faction_theaters.txt"
    vanilla_regions_dir = args.install / "map/strategicregions"
    wa_regions_dir = args.mod_root / "map/strategicregions"
    output = args.mod_root / "common/ai_faction_theaters/ai_faction_theaters.txt"

    for required in (source, vanilla_regions_dir, wa_regions_dir,
                     args.mod_root / "map/definition.csv", args.mod_root / "map/provinces.bmp"):
        if not required.exists():
            print(f"ERROR missing input: {required}", file=sys.stderr)
            return 2

    vanilla = load_regions(vanilla_regions_dir)
    wa = load_regions(wa_regions_dir)
    theatres = load_theatres(source)
    adjacency = load_province_adjacency(args.mod_root / "map")
    print(f"vanilla regions {len(vanilla)}, WA regions {len(wa)}, theatres {len(theatres)}, "
          f"province adjacency entries {len(adjacency)}")

    warnings: List[str] = []
    for theatre in theatres:
        warnings += remap(theatre, vanilla, wa, args.overlap)
    for theatre in theatres:
        warnings += prune_detached(theatre, wa, adjacency)

    print(f"\n{'theatre':28} {'vanilla':>7} {'WA':>4}  pieces  first region")
    for theatre in theatres:
        components = connected(theatre.new_regions, wa, adjacency) if theatre.new_regions else []
        first = theatre.new_regions[0] if theatre.new_regions else None
        flag = "" if len(components) <= 1 else f"  <- {len(components)} PIECES"
        print(f"{theatre.name:28} {len(theatre.vanilla_regions):>7} {len(theatre.new_regions):>4}  "
              f"{len(components):>6}  {wa[first][0] if first else '-'}{flag}")
        if len(components) > 1:
            # after prune_detached, a surviving split is one vanilla shipped too
            stray = [c for c in components if not set(c) & set(theatre.vanilla_regions)]
            level = "WARN" if stray else "note"
            warnings.append(
                f"[{level}] {theatre.name}: area is in {len(components)} pieces "
                f"{[len(c) for c in components]} - vanilla's own list splits the same way"
                if not stray else
                f"[{level}] {theatre.name}: area is not connected - {len(components)} pieces "
                f"{[len(c) for c in components]}; the engine requires a connected theatre"
            )

    covered = {rid for t in theatres for rid in t.new_regions}
    print(f"\nWA regions placed in at least one theatre: {len(covered)} / {len(wa)} "
          f"(vanilla placed {len({r for t in theatres for r in t.vanilla_regions})} / {len(vanilla)})")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  WARN {w}")

    text = (HEADER.replace("<WA_COUNT>", str(len(wa)))
                  .replace("<VANILLA_COUNT>", str(len(vanilla)))
                  .replace("<OVERLAP>", str(args.overlap)))
    text += "\n".join(render(t, wa) for t in theatres) + "\n"

    if args.dry_run:
        print(f"\nDRY RUN - would write {len(text)} bytes to {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(text.encode("utf-8"))  # no BOM: AGENTS.md editing rule 16
    print(f"\nwrote {output} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
