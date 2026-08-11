#!/usr/bin/env python3
"""Navigate and extract data from HOI4 text savegames (World Ablaze workflow).

Savegames are 60-150 MB / ~4.4M lines of PDXScript-like text. Never load one
whole; every command here streams a single pass and stops as early as it can.

Commands:
  list                          saves in the save dir, newest first, with campaign id
  campaigns                     group saves by game_unique_id (campaign identity)
  meta FILE                     header metadata of one save
  sections FILE TAG             depth-2 sections of a country block, with line counts
  section FILE TAG NAME         dump one country section (--grep to filter, --max-lines cap)
  var TAG PATTERN FILE...       matching country variables across saves, date-ordered (trends)
  ideas TAG FILE... [--match]   active ideas (+ timed_idea days) across saves, date-ordered
  flags FILE [TAG] [--match]    global flags (no TAG) or country flags, with set-dates
  tlm TAG FILE... [--match]     WA_TLM telemetry dashboard: scalars + decoded ring buffers
                                (clock values -> dates; see documentation/WA_TLM_TELEMETRY_SYSTEM.md)
"""
import argparse
import io
import os
import re
import sys
import zipfile
from glob import glob

SAVE_DIR = os.path.join(
    os.path.expanduser("~"),
    "Documents", "Paradox Interactive", "Hearts of Iron IV", "save games",
)

META_KEYS = (
    "player", "ideology", "date", "difficulty", "version", "save_version",
    "session", "game_unique_seed", "game_unique_id", "start_date",
)


def resolve(path):
    if os.path.exists(path):
        return path
    candidate = os.path.join(SAVE_DIR, path)
    if os.path.exists(candidate):
        return candidate
    sys.exit(f"not found: {path} (also tried {candidate})")


def open_save(path):
    """Return a text stream over the save's gamestate. Rejects ironman saves."""
    with open(path, "rb") as fh:
        magic = fh.read(7)
    if magic.startswith(b"PK"):
        zf = zipfile.ZipFile(path)
        name = "gamestate" if "gamestate" in zf.namelist() else zf.namelist()[0]
        if zf.open(name).read(7) != b"HOI4txt":
            sys.exit(f"{path}: compressed save's {name} is not HOI4txt")
        return io.TextIOWrapper(zf.open(name), encoding="utf-8", errors="replace")
    if magic == b"HOI4bin":
        sys.exit(f"{path}: binary (ironman) save - not parseable as text")
    if magic != b"HOI4txt":
        sys.exit(f"{path}: unknown header {magic!r} - not a HOI4 text save")
    return open(path, encoding="utf-8", errors="replace")


def read_meta(path, max_lines=30000):
    """Header metadata from the top of the save. Stops at start_date (found a
    few hundred lines in; the cap only guards against a degenerate file)."""
    meta = {"file": path}
    mods = None
    with open_save(path) as fh:
        for i, line in enumerate(fh):
            if i >= max_lines or line.startswith("countries={"):
                break
            if mods is not None:
                if line.startswith("}"):
                    meta["mods"] = ", ".join(mods)
                    mods = None
                else:
                    mods.append(line.strip().strip('"'))
                continue
            if line.startswith("mods={"):
                mods = []
                continue
            if line.startswith("\tironman="):
                meta["ironman"] = line.split("=", 1)[1].strip()
                continue
            m = re.match(r'^([a-z_]+)=("?)([^"\n]*)\2\s*$', line)
            if m and m.group(1) in META_KEYS:
                meta.setdefault(m.group(1), m.group(3))
                if m.group(1) == "start_date":
                    break
    return meta


def date_key(d):
    try:
        return tuple(int(x) for x in d.split("."))
    except (ValueError, AttributeError):
        return (0,)


def sorted_by_date(files):
    entries = [(read_meta(f), f) for f in files]
    entries.sort(key=lambda e: (date_key(e[0].get("date", "0")), e[0].get("session", "")))
    return entries


def iter_country_lines(fh, tag):
    """Yield the lines inside countries={ TAG={ ... } }, excluding the
    opening and closing lines of the TAG block itself."""
    prefix = "\t" + tag + "={"
    depth = None
    for line in fh:
        if depth is None:
            if line.startswith("countries={"):
                depth = 1
            continue
        # Depth counting, not indentation: saves contain malformed blocks
        # (braces at column 0 inside country_leader), so indentation lies.
        if depth == 1 and line.startswith(prefix):
            d = line.count("{") - line.count("}")
            if d <= 0:
                return
            for inner in fh:
                d += inner.count("{") - inner.count("}")
                if d <= 0:
                    return
                yield inner
            return
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            return


def extract_section(fh, tag, section):
    """Return the lines of one depth-2 section of a country block, or None.
    Prefix match at exact depth: two tabs, so nested same-named blocks
    (e.g. variables={} inside program_status) never match."""
    want = "\t\t" + section + "={"
    lines = iter_country_lines(fh, tag)
    for line in lines:
        if line.startswith(want):
            out = [line]
            depth = line.count("{") - line.count("}")
            if depth <= 0:
                return out
            for inner in lines:
                out.append(inner)
                depth += inner.count("{") - inner.count("}")
                if depth <= 0:
                    return out
            return out
    return None


# --- commands ---------------------------------------------------------------


def cmd_list(args):
    files = glob(os.path.join(args.dir, "*.hoi4"))
    files.sort(key=os.path.getmtime, reverse=True)
    for f in files[: args.limit]:
        try:
            m = read_meta(f)
        except SystemExit as e:
            print(f"skip: {e}")
            continue
        gid = (m.get("game_unique_id") or "?")[:8]
        size = os.path.getsize(f) / 1e6
        print(f"{os.path.basename(f):32} {m.get('date',''):14} player={m.get('player',''):4} "
              f"campaign={gid} session={m.get('session','')} {size:.0f}MB")


def cmd_campaigns(args):
    files = glob(os.path.join(args.dir, "*.hoi4"))
    groups = {}
    for f in sorted(files):
        try:
            m = read_meta(f)
        except SystemExit as e:
            print(f"skip: {e}")
            continue
        groups.setdefault(m.get("game_unique_id", "?"), []).append(m)
    for gid, ms in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        ms.sort(key=lambda m: (date_key(m.get("date", "0")), m.get("session", "")))
        print(f"campaign {gid}")
        print(f"  seed={ms[0].get('game_unique_seed')} start={ms[0].get('start_date')} "
              f"mods=[{ms[0].get('mods','')}] saves={len(ms)}")
        for m in ms:
            print(f"  {m.get('date',''):14} session={m.get('session',''):>7} "
                  f"player={m.get('player',''):4} {os.path.basename(m['file'])}")
        print()


def cmd_meta(args):
    m = read_meta(resolve(args.file))
    for k, v in m.items():
        print(f"{k}={v}")


def cmd_sections(args):
    with open_save(resolve(args.file)) as fh:
        depth = 1
        current = None
        count = 0
        found_any = False
        for line in iter_country_lines(fh, args.tag):
            header = re.match(r"^\t\t([a-z_0-9]+)={", line) if depth == 1 else None
            opens, closes = line.count("{"), line.count("}")
            if header and opens > closes:
                current, count = header.group(1), 0
            elif header:
                print(f"{header.group(1):36} 1")
                found_any = True
            depth += opens - closes
            if current:
                count += 1
                if depth == 1:
                    print(f"{current:36} {count}")
                    found_any = True
                    current = None
        if not found_any:
            print(f"no country block found for tag {args.tag}")


def cmd_section(args):
    with open_save(resolve(args.file)) as fh:
        sec = extract_section(fh, args.tag, args.name)
    if sec is None:
        sys.exit(f"section '{args.name}' not found in {args.tag} "
                 f"(run 'sections' to list what exists)")
    pat = re.compile(args.grep) if args.grep else None
    shown = 0
    for line in sec:
        if pat and not pat.search(line):
            continue
        sys.stdout.write(line)
        shown += 1
        if args.max_lines and shown >= args.max_lines:
            print(f"... truncated at {args.max_lines} lines "
                  f"(section has {len(sec)} total; use --max-lines 0 or --grep)")
            break


def cmd_var(args):
    pat = re.compile(args.pattern)
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            sec = extract_section(fh, args.tag, "variables")
        if not sec:
            print(f"{date}\t({os.path.basename(f)}: no variables section for {args.tag})")
            continue
        hits = [s for s in (l.strip() for l in sec[1:-1]) if pat.search(s)]
        if not hits:
            print(f"{date}\t(no variable matching /{args.pattern}/)")
        for h in hits:
            print(f"{date}\t{h}")


def cmd_ideas(args):
    pat = re.compile(args.match) if args.match else None
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            sec = extract_section(fh, args.tag, "politics")
        if not sec:
            print(f"{date}\t({os.path.basename(f)}: no politics section for {args.tag})")
            continue
        text = "".join(sec)
        timed = dict(re.findall(r'timed_idea=\{\s*idea="([^"]+)"\s*days=(\d+)', text))
        m = re.search(r"\n\t\t\tideas=\{([^}]*)\}", text)
        ideas = re.findall(r"[A-Za-z0-9_.\-]+", m.group(1)) if m else []
        if pat:
            ideas = [i for i in ideas if pat.search(i)]
        party = re.search(r"ruling_party=(\w+)", text)
        pp = re.search(r"political_power=([\d.\-]+)", text)
        print(f"{date}  ruling_party={party.group(1) if party else '?'} "
              f"political_power={pp.group(1) if pp else '?'} ideas={len(ideas)}")
        for i in ideas:
            suffix = f"  (timed, {timed[i]}d left)" if i in timed else ""
            print(f"\t{i}{suffix}")


def cmd_flags(args):
    pat = re.compile(args.match) if args.match else None
    with open_save(resolve(args.file)) as fh:
        if args.tag:
            sec = extract_section(fh, args.tag, "flags")
            text = "".join(sec or [])
        else:
            collected = []
            in_flags = False
            for line in fh:
                if not in_flags:
                    if line.startswith("flags={"):
                        in_flags = True
                    continue
                if line.startswith("}"):
                    break
                collected.append(line)
            text = "".join(collected)
    for name, value, date in re.findall(
            r'(\w+)=\{\s*value=(-?\d+)\s*(?:date="([^"]+)")?', text):
        if pat and not pat.search(name):
            continue
        print(f"{name}\tvalue={value}\tset={date}")


def _tlm_date(clock):
    """WA_TLM clock (months since 1936.1) -> 'YYYY.MM'."""
    m = int(round(clock))
    return f"{1936 + m // 12}.{1 + m % 12}"


def cmd_tlm(args):
    """WA_TLM telemetry: scalars, stamps decoded to dates, ring buffers paired
    with the wa_tlm_hist_t axis. Namespace contract (absence semantics, types):
    documentation/WA_TLM_TELEMETRY_SYSTEM.md."""
    pat = re.compile(args.match) if args.match else None
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            sec = extract_section(fh, args.tag, "variables")
        print(f"=== {date}  {args.tag}  ({os.path.basename(f)}) ===")
        if not sec:
            print("  (no variables section - country dead or never scripted)")
            continue
        scalars, arrays = {}, {}
        for line in (l.strip() for l in sec[1:-1]):
            m = re.match(r"^(wa_tlm_[a-z0-9_]+?)(?:\^(\d+|num))?=(-?[\d.]+)$", line)
            if not m:
                continue
            name, idx, val = m.group(1), m.group(2), float(m.group(3))
            if idx is None:
                scalars[name] = val
            elif idx != "num":
                arrays.setdefault(name, {})[int(idx)] = val
        if not scalars and not arrays:
            print("  (no wa_tlm_* variables - build predates WA_TLM: probe void, not FAILED)")
            continue
        for name in sorted(scalars):
            if pat and not pat.search(name):
                continue
            val = scalars[name]
            if name.endswith("_t") and val > 0:
                print(f"  {name}={val:g}  ({_tlm_date(val)})")
            else:
                print(f"  {name}={val:g}")
        axis = arrays.pop("wa_tlm_hist_t", None)
        for name in sorted(arrays):
            if pat and not pat.search(name):
                continue
            series = arrays[name]
            print(f"  series {name} ({len(series)} samples):")
            if axis is None:
                print("    (!) no wa_tlm_hist_t axis found - printing raw indices")
                for i in sorted(series):
                    print(f"    [{i}]  {series[i]:g}")
                continue
            if len(axis) != len(series):
                print(f"    (!) axis/series length mismatch ({len(axis)} vs {len(series)}) - "
                      "pairing is unreliable, report as instrumentation bug")
            for i in sorted(series):
                t = axis.get(i)
                label = _tlm_date(t) if t is not None else f"[{i}]"
                print(f"    {label:>9}  {series[i]:g}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="list saves, newest first")
    s.add_argument("--dir", default=SAVE_DIR)
    s.add_argument("--limit", type=int, default=30)
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("campaigns", help="group saves by campaign identity")
    s.add_argument("--dir", default=SAVE_DIR)
    s.set_defaults(fn=cmd_campaigns)

    s = sub.add_parser("meta", help="header metadata of one save")
    s.add_argument("file")
    s.set_defaults(fn=cmd_meta)

    s = sub.add_parser("sections", help="list depth-2 sections of a country block")
    s.add_argument("file")
    s.add_argument("tag")
    s.set_defaults(fn=cmd_sections)

    s = sub.add_parser("section", help="dump one country section")
    s.add_argument("file")
    s.add_argument("tag")
    s.add_argument("name")
    s.add_argument("--grep", help="only lines matching this regex")
    s.add_argument("--max-lines", type=int, default=400,
                   help="cap output lines, 0 = unlimited (default 400)")
    s.set_defaults(fn=cmd_section)

    s = sub.add_parser("var", help="country variables matching a regex, across saves")
    s.add_argument("tag")
    s.add_argument("pattern")
    s.add_argument("files", nargs="+")
    s.set_defaults(fn=cmd_var)

    s = sub.add_parser("ideas", help="active ideas across saves")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--match", help="only ideas matching this regex")
    s.set_defaults(fn=cmd_ideas)

    s = sub.add_parser("flags", help="global flags (no tag) or country flags")
    s.add_argument("file")
    s.add_argument("tag", nargs="?")
    s.add_argument("--match", help="only flag names matching this regex")
    s.set_defaults(fn=cmd_flags)

    s = sub.add_parser("tlm", help="WA_TLM telemetry dashboard for a country")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--match", help="only metric names matching this regex")
    s.set_defaults(fn=cmd_tlm)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
