"""Resolve WA strategic-region ids to their in-game names.

Region ids appear in savegames (a fleet's `strategic_region={}`, `regional_convoys`
indices) and all over `common/ai_strategy/WA_AI_NAVAL_*`. Three identifiers exist per
region and they do NOT always agree:

  * the number in the FILENAME under map/strategicregions/
  * the `id =` inside the block   <- this is what every script reference means
  * the `name = STRATEGICREGION_<n>` localisation key

`237-Azores Region.txt` carries `id = 112`, so id 112 displays as "Azores Region".
WA also replaces the whole table: 383 regions against vanilla's 304, with vanilla ids
repurposed (vanilla 241 = Dasht-e Kavir, WA 241 = Irish Sea) and 79 WA-only ids that a
vanilla or wiki lookup simply cannot find. Resolve id -> name token -> localisation,
against the MOD's files, or you will name the wrong sea.

Usage (from the repo root, or pass --root):
    python .claude/skills/wa-savegame-analysis/scripts/regions.py 18 368 43
    python .claude/skills/wa-savegame-analysis/scripts/regions.py --grep "channel|approach"
"""
import argparse
import io
import os
import re
from glob import glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def load(root):
    """{id: (loc_name, name_token, filename)} for the mod's strategic regions."""
    regions = {}
    for p in glob(os.path.join(root, "map", "strategicregions", "*.txt")):
        text = io.open(p, encoding="utf-8-sig", errors="replace").read()
        i = re.search(r"^\s*id\s*=\s*(\d+)", text, re.M)
        n = re.search(r'^\s*name\s*=\s*"?(\w+)', text, re.M)
        if i:
            regions[int(i.group(1))] = [None, n.group(1) if n else None,
                                        os.path.basename(p)]
    names = {}
    for p in glob(os.path.join(root, "localisation", "**", "*.yml"), recursive=True):
        for line in io.open(p, encoding="utf-8-sig", errors="replace"):
            m = re.match(r'\s*(STRATEGICREGION_\w+):\s*\d*\s*"(.*)"', line)
            if m:
                names.setdefault(m.group(1), m.group(2))
    for entry in regions.values():
        entry[0] = names.get(entry[1], "(no localisation)")
    return regions


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", type=int, help="region ids to resolve")
    ap.add_argument("--grep", help="instead, list regions whose name matches this regex")
    ap.add_argument("--root", default=REPO, help="mod root (default: this repo)")
    args = ap.parse_args()
    regions = load(args.root)
    if not regions:
        raise SystemExit(f"no strategic regions found under {args.root}/map/strategicregions")
    if args.grep:
        rx = re.compile(args.grep, re.I)
        for i in sorted(regions):
            if rx.search(regions[i][0]):
                print("id=%-4s %s" % (i, regions[i][0]))
        return
    for i in args.ids:
        name, token, fn = regions.get(i, ("(no block with this id)", None, "-"))
        print("id=%-4s %-30s token=%-22s file=%s" % (i, name, token, fn))


if __name__ == "__main__":
    main()
