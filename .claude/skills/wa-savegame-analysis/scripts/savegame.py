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
  army TAG FILE...              deployed division count (units section ONLY) + cross-checks
  resources TAG FILE...         per-resource ledger: produced/transfer/imported/net/deficit/export
  buildings TAG FILE... [--match] building levels summed over owned vs controlled states,
                                *_inactive twins shown next to their active counterpart
  decisions TAG FILE... [--match]  decoded decision_status: live entries (days) vs the
                                random_item cumulative fire counters, labelled separately
  pc TAG FILE... [--match]      priority-construction queue: per-project table (building
                                type, strategy tag and priority band by NAME) + a
                                per-country summary with the civ-factory share
  control SCOPE FILE...         who really holds the ground: province-level control with
                                both omitted-field defaults applied, and the states whose
                                province split contradicts their state controller
  relations FILE... [--tag]     factions (top-level blocks, leader = members[0]), subjects
                                (puppet= sits in the OVERLORD's block) and wars, read from
                                BOTH sides - war_relation is written on one side only
"""
import argparse
import io
import os
import collections
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

# The mod root, four levels up from .claude/skills/wa-savegame-analysis/scripts/.
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "..", ".."))


def resolve(path):
    for candidate in (path, os.path.join(SAVE_DIR, path)):
        if os.path.isdir(candidate):
            sys.exit(f"{candidate}: is a directory, not a save file")
        if os.path.exists(candidate):
            return candidate
    sys.exit(f"not found: {path} (also tried {os.path.join(SAVE_DIR, path)})")


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


def collect_sections(fh, tag, names):
    """One streaming pass: return {name: lines} for several depth-2 sections of
    a country block. Same exact-depth prefix match as extract_section; missing
    sections are simply absent from the result. Stops as soon as all are found."""
    wanted = {"\t\t" + n + "={": n for n in names}
    out = {}
    lines = iter_country_lines(fh, tag)
    for line in lines:
        name = None
        for pref, n in wanted.items():
            if line.startswith(pref):
                name = n
                break
        if name is None:
            continue
        buf = [line]
        depth = line.count("{") - line.count("}")
        if depth > 0:
            for inner in lines:
                buf.append(inner)
                depth += inner.count("{") - inner.count("}")
                if depth <= 0:
                    break
        out[name] = buf
        if len(out) == len(wanted):
            break
    return out


def iter_state_blocks(fh):
    """Yield (state_id, lines) for every state in the top-level states={} block.
    Brace-counted per state, so the save's lying indentation cannot split one."""
    for line in fh:
        if line.startswith("states={"):
            break
    else:
        return
    depth, sid, buf, sdepth = 1, None, None, 0
    for line in fh:
        if buf is None:
            m = re.match(r"^\t(\d+)=\{", line)
            if m:
                sid = int(m.group(1))
                sdepth = line.count("{") - line.count("}")
                if sdepth <= 0:
                    yield sid, []
                    continue
                buf = []
                continue
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                return
            continue
        sdepth += line.count("{") - line.count("}")
        if sdepth <= 0:
            yield sid, buf
            buf = None
            continue
        buf.append(line)


def _match_report(pattern, matched, candidates, thing, indent="  ", sample=12):
    """The line every --match owes its reader: what it caught, or that it caught
    nothing.

    Two silent failures this closes, both of which were written into the
    verification checklist as measurements (2026-08-17):
      * a pattern that can never match (`pc TAG --match corridor`, which filters a
        building/tag/band LABEL, not the strategy name) returned an empty table that
        read as "the system did nothing";
      * an over-broad substring (`--match Somaliland`) silently swept French and
        British Somaliland into one country's totals.
    A legitimately empty result is still exit 0 - the point is that it says so.
    """
    if pattern is None:
        return
    cands = sorted(set(candidates))
    if not matched:
        print(f"{indent}NO MATCH: pattern '{pattern}' matched 0 of {len(cands)} "
              f"candidate {thing}")
        if cands:
            print(f"{indent}  available {thing}: {', '.join(cands[:sample])}"
                  f"{' ...' if len(cands) > sample else ''}")
        return
    names = sorted(set(matched))
    print(f"{indent}MATCHED {len(names)} of {len(cands)} {thing}: "
          f"{', '.join(names[:sample])}{' ...' if len(names) > sample else ''}")


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
    # --limit 0 means unlimited here, as it does for `section --max-lines`,
    # `pc --limit` and `control --limit`. A scoring probe assumed that and got a
    # silently truncated (here: empty) listing instead.
    for f in (files if not args.limit else files[: args.limit]):
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
        allideas = re.findall(r"[A-Za-z0-9_.\-]+", m.group(1)) if m else []
        ideas = [i for i in allideas if pat.search(i)] if pat else allideas
        party = re.search(r"ruling_party=(\w+)", text)
        pp = re.search(r"political_power=([\d.\-]+)", text)
        print(f"{date}  ruling_party={party.group(1) if party else '?'} "
              f"political_power={pp.group(1) if pp else '?'} ideas={len(ideas)}")
        _match_report(args.match, ideas, allideas, "ideas", indent="\t")
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
    found = re.findall(r'(\w+)=\{\s*value=(-?\d+)\s*(?:date="([^"]+)")?', text)
    hits = [f[0] for f in found if not pat or pat.search(f[0])]
    _match_report(args.match, hits, [f[0] for f in found], "flag names", indent="")
    for name, value, date in found:
        if pat and not pat.search(name):
            continue
        print(f"{name}\tvalue={value}\tset={date}")


def _tlm_date(clock):
    """WA_TLM clock (months since 1936.1) -> 'YYYY.MM'."""
    m = int(round(clock))
    return f"{1936 + m // 12}.{1 + m % 12}"


def _tlm_clock(date):
    """The save's own date ('1946.2.1.2') on the WA_TLM clock, or None."""
    parts = (date or "").split(".")
    try:
        return (int(parts[0]) - 1936) * 12 + (int(parts[1]) - 1)
    except (IndexError, ValueError):
        return None


# How far a family's _last_t may lag the save before the gauge is called frozen.
# The standard sample is MONTHLY (WA_TLM_monthly_sample), and a save is a snapshot
# taken between two samples, so a lag of one month is ordinary cadence. Two months
# is the first age that cadence cannot explain.
_TLM_FROZEN_MONTHS = 2


def _tlm_family_stamps(scalars):
    """{family prefix: last_t} from every wa_tlm_*_last_t in a country's scalars.

    'wa_tlm_r99_tunis_last_t' -> prefix 'wa_tlm_r99_tunis_', which every metric of
    that family shares. Longest matching prefix wins, so a nested family
    (wa_tlm_pc_ inside wa_tlm_) is attributed to its own stamp.
    """
    return {n[: -len("last_t")]: v for n, v in scalars.items()
            if n.endswith("_last_t")}


def _tlm_freshness(name, stamps, now):
    """The annotation a WA_TLM value row owes its reader about its own age.

    A gauge stops being updated when its condition closes and the last value
    persists forever: GER read wa_tlm_r99_tunis_states_manned=3 for 11 months after
    leaving Africa entirely, and it was scored as a live reading. The stamp is the
    only thing in the save that can tell the two apart, so it is put on the value
    row itself, not in a footnote.
    """
    if now is None:
        return ""
    best = None
    for pref in stamps:
        if name.startswith(pref) and (best is None or len(pref) > len(best)):
            best = pref
    if best is None:
        return ""
    t = stamps[best]
    if t <= 0:
        return "  [never sampled]"
    age = now - t
    if age > _TLM_FROZEN_MONTHS:
        return f"  FROZEN {age:.0f}mo (last sampled {_tlm_date(t)})"
    return ""


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
        stamps = _tlm_family_stamps(scalars)
        now = _tlm_clock(date)
        # Families may run their own axis when they sample under a different gate
        # (a shared axis + a gate mismatch desynchronises index i for every series
        # on it). Pick the most specific axis whose prefix the series shares:
        # wa_tlm_nav_port_pct_hist -> wa_tlm_nav_hist_t, falling back to wa_tlm_hist_t.
        axes = {n: arrays.pop(n) for n in list(arrays) if n.endswith("_hist_t")}

        def axis_for(series_name):
            best = None
            for n in axes:
                prefix = n[:-len("hist_t")]          # "wa_tlm_" or "wa_tlm_nav_"
                if series_name.startswith(prefix) and (best is None or len(n) > len(best)):
                    best = n
            return best

        printable = list(scalars) + list(arrays)
        hits = [n for n in printable if not pat or pat.search(n)]
        _match_report(args.match, hits, printable, "metrics")
        for name in sorted(scalars):
            if pat and not pat.search(name):
                continue
            val = scalars[name]
            age = _tlm_freshness(name, stamps, now)
            if name.endswith("_t") and val > 0:
                print(f"  {name}={val:g}  ({_tlm_date(val)}){age}")
            else:
                print(f"  {name}={val:g}{age}")
        for name in sorted(arrays):
            if pat and not pat.search(name):
                continue
            series = arrays[name]
            age = _tlm_freshness(name, stamps, now)
            # ONLY a `_hist` array is a ring buffer that pairs with a `_hist_t` axis
            # (WA_TLM_TELEMETRY_SYSTEM.md: the ring-buffer suffix IS `_hist`).
            # Everything else is an indexed scalar table keyed by the family's own
            # key - a building type id, a project slot - and rendering it under a
            # date axis invents a time series that does not exist:
            # wa_tlm_pc_built_by_type^13 = 450 railways printed as "1939.7  450".
            if not name.endswith("_hist"):
                print(f"  table {name} ({len(series)} entries, INDEXED - the index is "
                      f"this family's own key, NOT time){age}:")
                for i in sorted(series):
                    # A `_t` table stores clock VALUES, so the value (not the index)
                    # is the thing with a date.
                    when = (f"  ({_tlm_date(series[i])})"
                            if name.endswith("_t") and series[i] > 0 else "")
                    print(f"    [{i}]  {series[i]:g}{when}")
                continue
            axis_name = axis_for(name)
            axis = axes.get(axis_name)
            print(f"  series {name} ({len(series)} samples"
                  + (f", axis {axis_name}" if axis_name else "") + f"){age}:")
            if axis is None:
                print("    (!) no matching *_hist_t axis found - printing raw indices")
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


def _count_divisions(units_lines):
    """Number of division={ blocks that are *direct children* of units={}.

    `division={ id=N type=N }` also appears inside experience_status'
    xp_by_template blocks, which are SIBLINGS of units, not nested in it - a
    naive whole-country-block count over-reports by 8-10%. Counting at exactly
    one level inside units excludes them and excludes the one-line
    division={ id= type= } references too (depth never opens for those)."""
    depth = 1  # we are inside units={ already
    n = 0
    for line in units_lines[1:]:
        before = depth
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            break
        if before == 1 and line.lstrip().startswith("division={") and depth > 1:
            n += 1
    return n


def cmd_army(args):
    """Deployed division count. See _count_divisions for why `units` scoping is
    the whole point of this command."""
    print("# deployed divisions = division={ blocks inside `units` ONLY "
          "(experience_status holds siblings that inflate a naive count).")
    print("# cross-checks: num_armies_for_training (engine) and "
          "wa_tlm_comp_div_total (WA_TLM gauge) - both matched units-only on 911bed3c.")
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            secs = collect_sections(fh, args.tag, ("units", "variables", "experience_status"))
        if "units" not in secs:
            print(f"{date}\t({os.path.basename(f)}: no units section for {args.tag} "
                  f"- country dead, never existed, or has no army)")
            continue
        deployed = _count_divisions(secs["units"])
        train = re.search(r"num_armies_for_training=([\d.\-]+)",
                          "".join(secs.get("experience_status", [])))
        tlm = re.search(r"^\s*wa_tlm_comp_div_total=(-?[\d.]+)\s*$",
                        "".join(secs.get("variables", [])), re.M)
        extra = []
        extra.append(f"num_armies_for_training={float(train.group(1)):.1f}" if train
                     else "num_armies_for_training=-")
        extra.append(f"wa_tlm_comp_div_total={float(tlm.group(1)):g}" if tlm
                     else "wa_tlm_comp_div_total=- (pre-TLM build or unsampled)")
        print(f"{date}\t{args.tag}\tdeployed={deployed}\t" + "\t".join(extra))


# Resource ledger blocks, in report order. to_use is positional, not keyed.
_RES_FLAT = ("produced", "transfer_overlord_subject", "imported", "to_export", "exported")


def _parse_resources(sec):
    """{block: {resource: value}} for the depth-1 ledger blocks of a country
    `resources` section, plus to_use as a positional list of dicts.

    Only depth-1 blocks are read: the section also carries delivery_routes,
    origin/export sub-blocks and their own nested resources={} lists."""
    flat, to_use = {}, []
    depth, cur = 1, None
    for line in sec[1:]:
        before = depth
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            break
        s = line.strip()
        if before == 1:
            m = re.match(r"^([a-z_0-9]+)=\{", s)
            cur = m.group(1) if m else None
            continue
        if cur == "to_use":
            if before == 2 and s.startswith("{"):
                to_use.append({})
            elif before == 3 and to_use:
                m = re.match(r"^([a-z_0-9]+)=(-?[\d.]+)\s*$", s)
                if m:
                    to_use[-1][m.group(1)] = float(m.group(2))
            continue
        if before == 2 and cur:
            m = re.match(r"^([a-z_0-9]+)=(-?[\d.]+)\s*$", s)
            if m:
                flat.setdefault(cur, {})[m.group(1)] = float(m.group(2))
    return flat, to_use


def cmd_resources(args):
    print("# WARNING: `resource@X` in script reads the `effective` column below "
          "= net + deficit")
    print("#   (to_use[0] + to_use[2]), NOT `produced` and NOT `net` alone. "
          "Measured 2026-08-13")
    print("#   on campaign 02bd4445: 36 discriminating WA_AI_EQUIPMENT latch "
          "readings all side with")
    print("#   net+deficit, zero with net. ENG aluminium 1942.6 is net 807.3, "
          "deficit -799.0,")
    print("#   effective +8.3 - which is why its `> 50` gate stayed shut while "
          "the net column")
    print("#   looked like 16x headroom. The older `net alone` rule was drawn "
          "from ENG bauxite,")
    print("#   whose deficit happened to be -1.0 so both readings coincided.")
    print("# net = to_use[0] (available now) | deficit = to_use[2] (unmet demand, "
          "negative)")
    print("# identity: produced + transfer + imported = net + to_export; `resid` is "
          "the leftover")
    print("#   (marked ! above 1.0; a residual of ~1 shows up on resources whose gross "
          "domestic")
    print("#   production is negative, e.g. ENG bauxite - benign, not a parse error).")
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            sec = extract_section(fh, args.tag, "resources")
        print(f"=== {date}  {args.tag}  ({os.path.basename(f)}) ===")
        if not sec:
            print("  (no resources section - country dead or never scripted)")
            continue
        flat, to_use = _parse_resources(sec)
        net = to_use[0] if len(to_use) > 0 else {}
        deficit = to_use[2] if len(to_use) > 2 else {}
        names = []
        for block in (flat.get("produced", {}), net, deficit, flat.get("imported", {}),
                      flat.get("transfer_overlord_subject", {}),
                      flat.get("to_export", {}), flat.get("exported", {})):
            for k in block:
                if k not in names:
                    names.append(k)
        if not names:
            print("  (resources section carries no ledger blocks)")
            continue
        print(f"  {'resource':<11}{'produced':>11}{'transfer':>10}{'imported':>11}"
              f"{'net':>11}{'deficit':>10}{'EFFECTIVE':>11}{'to_export':>11}"
              f"{'exported':>10}{'resid':>8}")
        for r in sorted(names):
            prod = flat.get("produced", {}).get(r, 0.0)
            tr = flat.get("transfer_overlord_subject", {}).get(r, 0.0)
            imp = flat.get("imported", {}).get(r, 0.0)
            av = net.get(r, 0.0)
            dfc = deficit.get(r, 0.0)
            # What `check_variable = { resource@<r> > N }` actually compares.
            effective = av + dfc
            exp_t = flat.get("to_export", {}).get(r, 0.0)
            exp_a = flat.get("exported", {}).get(r, 0.0)
            resid = (prod + tr + imp) - (av + exp_t)
            mark = " !" if abs(resid) > 1.0 else ""
            print(f"  {r:<11}{prod:>11.1f}{tr:>10.1f}{imp:>11.1f}{av:>11.1f}"
                  f"{dfc:>10.1f}{effective:>11.1f}{exp_t:>11.1f}{exp_a:>10.1f}"
                  f"{resid:>8.1f}{mark}")


def _state_buildings(lines):
    """{building: summed level} for one state block, plus (owner, controller).
    Levels are summed at any depth under the building name, so a province-keyed
    building (naval_base) totals correctly instead of reading 0."""
    out, owner, controller = {}, None, None
    depth, name, in_b = 0, None, False
    for line in lines:
        if not in_b:
            if line.startswith("\t\tbuildings={"):
                in_b = True
                depth = line.count("{") - line.count("}")
                continue
            m = re.match(r'^\t\t(owner|controller)="(\w+)"', line)
            if m:
                if m.group(1) == "owner":
                    owner = m.group(2)
                else:
                    controller = m.group(2)
            continue
        before = depth
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            in_b = False
            continue
        s = line.strip()
        if before == 1:
            m = re.match(r"^([a-z_0-9]+)=\{", s)
            name = m.group(1) if m else None
        elif before >= 2 and name:
            m = re.match(r"^level=(-?\d+)", s)
            if m:
                out[name] = out.get(name, 0) + int(m.group(1))
    # A state block omits controller= entirely when the controller IS the owner;
    # taking it literally reports a country as controlling only its conquests.
    return out, owner, (controller or owner)


_BUILDINGS_TXT = os.path.join(REPO, "common", "buildings", "00_buildings.txt")

# Fallback if 00_buildings.txt is unreadable (derived from it, 2026-08-18).
_FALLBACK_PROVINCE_BUILDINGS = (
    "air_facility", "bunker", "bunker_ai", "canal_kiel", "canal_panama",
    "coastal_bunker", "dam", "dam_mountain", "land_facility", "naval_base",
    "naval_facility", "naval_headquarters", "naval_supply_hub",
    "nuclear_facility", "rail_way", "supply_node",
)
_building_scopes = None


def building_scopes():
    """(province-scoped names, state-scoped names) from common/buildings/00_buildings.txt.

    A building declaring `province_max` is province-scoped: it is serialized inside the
    top-level provinces={} block and NEVER inside a state's buildings={}. That is a hard
    structural fact, not a per-save accident, which is why `buildings --match naval_base`
    is refused rather than allowed to return a plausible-looking zero.
    """
    global _building_scopes
    if _building_scopes is None:
        prov, state, depth, name = set(), set(), 0, None
        try:
            with io.open(_BUILDINGS_TXT, encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    s = raw.split("#")[0]
                    if depth == 1:
                        m = re.match(r"^\s*([a-z_0-9]+)\s*=\s*\{", s)
                        if m:
                            name = m.group(1)
                            state.add(name)
                    if depth >= 2 and name and re.match(r"^\s*province_max\s*=", s):
                        prov.add(name)
                    depth += s.count("{") - s.count("}")
        except OSError:
            prov = set(_FALLBACK_PROVINCE_BUILDINGS)
        if not prov:
            prov = set(_FALLBACK_PROVINCE_BUILDINGS)
        # `*_spawn` blocks are spawn-point definitions (`spawn_point = naval_base_spawn`
        # inside naval_base), not buildings that can appear in a state block. Leaving
        # them in the state set let `--match naval_base` escape the refusal by matching
        # naval_base_spawn.
        state = {n for n in state - prov if not n.endswith("_spawn")}
        _building_scopes = (prov, state)
    return _building_scopes


def _building_sort_key(name):
    """Sort an *_inactive twin immediately after its active counterpart."""
    base = name[: -len("_inactive")] if name.endswith("_inactive") else name
    return (base, 1 if name.endswith("_inactive") else 0)


def cmd_buildings(args):
    pat = re.compile(args.match) if args.match else None
    # Refuse a --match that can only ever hit a province-scoped key. This command reads
    # state blocks; naval_base/rail_way/supply_node/naval_supply_hub/bunkers are not in
    # one, so the query is structurally unanswerable here and used to return an empty
    # table that read as "zero ports built" (2026-08-17 scoring session).
    if pat:
        prov, state = building_scopes()
        hit_prov = sorted(n for n in prov if pat.search(n))
        hit_state = sorted(n for n in state if pat.search(n))
        if hit_prov and not hit_state:
            sys.exit(
                f"buildings --match '{args.match}' can only match province-scoped "
                f"building(s): {', '.join(hit_prov)}.\n"
                "These live in the save's top-level provinces={} block and are NEVER "
                "in a state's buildings={}, so this command would return an empty table "
                "that reads as a real zero.\n"
                f"Use instead:  control <SCOPE> {os.path.basename(args.files[0])} "
                "--buildings   (SCOPE is a state-id list or owner:TAG) - it sums them "
                "by the province's real holder.")
    print("# building levels summed over states, owned vs controlled (a state can be "
          "in both).")
    print("# *_inactive twins are listed under their active counterpart: an inactive "
          "refinery")
    print("#   produces nothing AND consumes nothing (no local_resources_*, no "
          "country_modifiers),")
    print("#   which is why a shutdown hides itself from every net-balance need "
          "detector - see R29.")
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        owned, controlled = {}, {}
        n_owned = n_controlled = 0
        with open_save(f) as fh:
            for _sid, lines in iter_state_blocks(fh):
                if not lines:
                    continue
                b, owner, controller = _state_buildings(lines)
                if owner == args.tag:
                    n_owned += 1
                    for k, v in b.items():
                        owned[k] = owned.get(k, 0) + v
                if controller == args.tag:
                    n_controlled += 1
                    for k, v in b.items():
                        controlled[k] = controlled.get(k, 0) + v
        print(f"=== {date}  {args.tag}  ({os.path.basename(f)})  "
              f"states owned={n_owned} controlled={n_controlled} ===")
        allnames = sorted(set(owned) | set(controlled), key=_building_sort_key)
        names = [n for n in allnames if pat.search(n)] if pat else allnames
        _match_report(args.match, names, allnames, "building names")
        if not names:
            if not pat:
                print("  (this tag holds no states with buildings in this save)")
            continue
        print(f"  {'building':<34}{'owned':>8}{'controlled':>12}")
        for n in names:
            print(f"  {n:<34}{owned.get(n, 0):>8}{controlled.get(n, 0):>12}")


def _decision_entries(sec):
    """Group decision_status into its entry kinds. Each kind is a list of dicts
    of its raw key=value fields, in file order."""
    kinds, taken = {}, []
    depth, cur, buf = 1, None, None
    for line in sec[1:]:
        before = depth
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            break
        s = line.strip()
        if before == 1:
            m = re.match(r"^([a-z_0-9]+)=\{", s)
            cur = m.group(1) if m else None
            buf = {} if cur else None
            if cur and cur != "decisions_taken":
                kinds.setdefault(cur, []).append(buf)
            continue
        if cur == "decisions_taken":
            taken.extend(re.findall(r"[A-Za-z0-9_.\-]+", s))
        elif buf is not None and before == 2:
            for k, v in re.findall(r'([a-z_0-9]+)=("?[A-Za-z0-9_.\-]+"?)', s):
                buf[k] = v.strip('"')
    return kinds, taken


# label -> (header note, field order). Anything unlisted is printed generically.
_DECISION_KINDS = (
    ("active_timed_decision",
     "LIVE timed decisions/missions. days = time REMAINING when state=active "
     "(<= the decision's days_mission_timeout); when state=failed or "
     "re_enable_cooldown it is a RE-ARM cooldown instead - a different clock, "
     "not mission time. Absent = not currently live."),
    ("active_targeted_decision",
     "LIVE target-scoped decisions, one entry per target."),
    ("decision_to_re_enable",
     "cooldown before the decision can be taken again; days = remaining."),
    ("decision_to_remove",
     "queued removal; days = remaining."),
)


_DECISIONS_DIR = os.path.join(REPO, "common", "decisions")
_fire_once = None


def fire_only_once_decisions():
    """Names declared `fire_only_once = yes` anywhere in common/decisions/.

    Used only to CALIBRATE the random_item counter on the reader's own save: such a
    decision can fire at most once per target, so any count above 1 on one of them is
    proof, from the save in front of you, that count is not a firing count. Best effort
    - returns an empty set when the repo is not next to the script, and the calibration
    line is then simply omitted.
    """
    global _fire_once
    if _fire_once is None:
        _fire_once = set()
        for path in sorted(glob(os.path.join(_DECISIONS_DIR, "*.txt"))):
            try:
                fh = io.open(path, encoding="utf-8", errors="replace")
            except OSError:
                continue
            with fh:
                depth, name, ndepth = 0, None, 0
                for raw in fh:
                    s = raw.split("#")[0]
                    if name is None and depth == 1:
                        m = re.match(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{\s*$", s)
                        if m:
                            name, ndepth = m.group(1), depth
                    elif name is not None and re.match(
                            r"^\s*fire_only_once\s*=\s*yes", s):
                        _fire_once.add(name)
                    depth += s.count("{") - s.count("}")
                    if name is not None and depth <= ndepth:
                        name = None
    return _fire_once


# What the random_item table may and may not claim. Everything here is derived from the
# save data itself (calibration below), not from a remembered rule of thumb: the rule
# that count is exactly twice the firings was carried into two scoring sessions and is
# false - coal_prospecting alone breaks it, and so does every fire_only_once decision
# that reads 1.
_RANDOM_ITEM_NOTE = (
    "count is a MONOTONE CUMULATIVE COUNTER the engine keeps per (decision, TARGET) "
    "pair - not a state, not days. Two things it is NOT. (1) It is not per decision: a "
    "targeted decision has one row per target, so a decision's total is the SUM of its "
    "rows (printed below as TOTAL), never one row. (2) It is not a verified firing "
    "count, and this script cannot derive the firing-to-count ratio from a save. "
    "Calibrating against decisions that can fire at most ONCE per target "
    "(fire_only_once = yes) shows counts of 1, 2 and 4 on the same save - so no single "
    "multiplier exists and the old 'halve it' rule is wrong. Read it as monotone "
    "activity, comparable across saves for the same (decision, target); for an exact "
    "firing count use a scripted counter or a WA_TLM metric."
)


def cmd_decisions(args):
    pat = re.compile(args.match) if args.match else None
    print("# decision_status holds entry kinds with INCOMPATIBLE number semantics - "
          "they are")
    print("#   labelled separately below and must never be read as one figure:")
    print("#   * active_* / decision_to_* entries carry `days`, a countdown, and exist "
          "only while live.")
    print("#   * random_item entries carry `count`, a cumulative per-(decision,target) "
          "counter whose")
    print("#     ratio to actual firings is NOT determinable from a save - see the note "
          "on that table.")
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            sec = extract_section(fh, args.tag, "decision_status")
        print(f"=== {date}  {args.tag}  ({os.path.basename(f)}) ===")
        if not sec:
            print("  (no decision_status section)")
            continue
        kinds, taken = _decision_entries(sec)
        allnames = [e.get("decision", "?") for rows in kinds.values() for e in rows]
        hits = [n for n in allnames if not pat or pat.search(n)]
        _match_report(args.match, hits, allnames, "decision names")
        described = dict(_DECISION_KINDS)
        order = [k for k, _ in _DECISION_KINDS if k in kinds]
        order += [k for k in kinds if k not in described and k != "random_item"]
        for kind in order:
            rows = [e for e in kinds[kind]
                    if not pat or pat.search(e.get("decision", ""))]
            if not rows:
                continue
            print(f"  -- {kind} ({len(rows)}) --")
            note = described.get(kind)
            if note:
                for chunk in _wrap(note, 92):
                    print(f"     # {chunk}")
            for e in rows:
                name = e.get("decision", "?")
                bits = []
                if "state" in e:
                    bits.append(f"state={e['state']}")
                if "days" in e:
                    bits.append(f"days={e['days']}")
                if e.get("target", "0") not in ("0", None):
                    bits.append(f"target={e['target']}")
                print(f"     {name:<52}{'  '.join(bits)}")
        if "random_item" in kinds:
            rows = [e for e in kinds["random_item"]
                    if not pat or pat.search(e.get("decision", ""))]
            if rows:
                once = fire_only_once_decisions()
                print(f"  -- random_item ({len(rows)}) --")
                for chunk in _wrap(_RANDOM_ITEM_NOTE, 92):
                    print(f"     # {chunk}")
                totals = collections.Counter()
                targets = collections.Counter()
                for e in rows:
                    totals[e.get("decision", "?")] += int(e.get("count", 0) or 0)
                    targets[e.get("decision", "?")] += 1
                for e in sorted(rows, key=lambda e: -int(e.get("count", 0) or 0)):
                    tgt = e.get("target", "0")
                    name = e.get("decision", "?")
                    bits = []
                    if tgt not in ("0", None):
                        bits.append(f"target={tgt}")
                    if name in once:
                        bits.append("fire_only_once")
                    print(f"     {name:<52}count={e.get('count','?'):<6}"
                          + "  ".join(bits))
                multi = [d for d in targets if targets[d] > 1]
                if multi:
                    print("     -- per-decision TOTALS (targeted decisions: the rows "
                          "above are per target) --")
                    for d in sorted(multi, key=lambda d: -totals[d]):
                        print(f"     {d:<52}TOTAL count={totals[d]} over "
                              f"{targets[d]} target(s)")
                # The calibration, computed on THIS save, that kills the 2x rule.
                cal = collections.Counter(int(e.get("count", 0) or 0)
                                          for e in rows if e.get("decision") in once)
                if cal:
                    spread = " ".join(f"count={k} x{v}" for k, v in sorted(cal.items()))
                    print(f"     # calibration on this save: {sum(cal.values())} row(s) "
                          f"belong to fire_only_once decisions (at most ONE firing per "
                          f"target) and read {spread}"
                          + (" - so count is NOT the firing count and no fixed ratio "
                             "exists." if len(cal) > 1 or max(cal) > 1
                             else " - consistent with 1 count per firing HERE, which "
                                  "does not generalise to timed decisions."))
        if taken and not pat:
            print(f"  -- decisions_taken ({len(taken)}) -- "
                  "flat list, no counts or timers")
            for chunk in _wrap(" ".join(sorted(taken)), 92):
                print(f"     {chunk}")


# Naval mission ids. The save stores `mission={ mission=N }` as a bare enum with no
# name anywhere in the game files; this map was derived empirically on campaign
# bec4d829 (2026-08-13) and every entry has a signature you can re-verify:
#   0  no mission   - no accessible_regions; only state a neutral (SWE/POR) ever shows
#   1  patrol       - carries spotting_region/hours_in_spotting_region + radar
#   2  strike force - carrier/battleship task forces, navy_engagement_rule=4
#   3  convoy raid  - 5-boat submarine task forces, never a single screen in them
#   4  convoy escort- war-only, peaks 1942-44, regions == the country's own
#                     high `required_convoys` regions in strategic_navy
#   7  training     - the only mission any major runs in 1936-1939
#   8  reserve/none - no regions; holds the fleets auto-named "Reserve fleet"
# 5 and 6 (mine planting / sweeping, in some order) were never observed in use.
# Treat 0 and 8 alike: both mean the task force is parked in port.
_NAVAL_MISSIONS = {
    "0": "none", "1": "patrol", "2": "strike", "3": "raid",
    "4": "escort", "5": "mine?", "6": "mine?", "7": "train", "8": "reserve",
}
_NAVAL_IDLE = ("none", "reserve")
# screen_ship category per common/units/ship_*.txt: these are the escort hulls.
_NAVAL_SCREENS = ("destroyer", "frigate", "light_cruiser")


def _parse_fleets(units_lines):
    """[{name, leader, regions, tfs:[{mission, name, ships:Counter}]}] from a
    country `units` section. Fleets and task forces are brace-counted, and ship
    blocks are skipped wholesale so their inner `name=`/`location=` fields cannot
    be mistaken for task-force fields."""
    fleets = []
    fleet = tf = None
    fdepth = tdepth = sdepth = mdepth = None
    in_regions = False
    for line in units_lines:
        st = line.strip()
        delta = line.count("{") - line.count("}")
        # --- dispatch on the state this line is read in. Opening lines set their
        # level's depth to 0; the single bookkeeping pass below adds delta once, so
        # no depth is ever incremented twice for the same line.
        if fleet is None:
            if not st.startswith("fleet={"):
                continue
            fleet = {"name": None, "leader": False, "regions": [], "tfs": []}
            fleets.append(fleet)
            fdepth = 0
            in_regions = False
        elif sdepth is not None:                    # inside ship={}
            # depth 1 ONLY: a ship's history holds sunk_ship={} kill records that
            # carry their own definition= (the VICTIM's hull). Counting those makes
            # every successful sub-hunting destroyer read as a submarine - it is what
            # produced the bogus "ENG has 204 cruiser_submarines" reading (2026-08-13).
            if sdepth == 1 and st.startswith("definition="):
                tf["ships"][st.split("=", 1)[1]] += 1
        elif tf is not None:                        # inside task_force={}
            if st.startswith("ship={"):
                sdepth = 0
            elif mdepth is not None:                # inside mission={}
                if st.startswith("mission="):
                    tf["mission"] = _NAVAL_MISSIONS.get(st.split("=")[1], st.split("=")[1])
            elif st.startswith("mission={"):
                mdepth = 0
            elif st.startswith("name=") and tf["name"] is None:
                tf["name"] = st.split("=", 1)[1].strip('"')
        else:                                       # fleet level
            if st.startswith("task_force={"):
                tf = {"mission": None, "name": None, "ships": collections.Counter()}
                fleet["tfs"].append(tf)
                tdepth = 0
            elif st.startswith("leader={"):
                fleet["leader"] = True
            elif st.startswith("name=") and fleet["name"] is None:
                fleet["name"] = st.split("=", 1)[1].strip('"')
            elif st.startswith("strategic_region={"):
                in_regions = True
            elif in_regions:
                if st.startswith("}"):
                    in_regions = False
                else:
                    fleet["regions"] += st.replace("}", "").split()
        # --- one depth update per line, innermost level closed first
        fdepth += delta
        if mdepth is not None:
            mdepth += delta
            if mdepth <= 0:
                mdepth = None
        if sdepth is not None:
            sdepth += delta
            if sdepth <= 0:
                sdepth = None
        if tdepth is not None:
            tdepth += delta
            if tdepth <= 0:
                tdepth = tf = None
        if fdepth <= 0:
            fdepth = fleet = None
    return fleets


def cmd_navy(args):
    """Fleet / task-force / mission breakdown. The mission split is NOT visible to
    PDXScript (no trigger reads a task force's mission), so this command is the only
    way to answer "is the AI actually escorting convoys" - WA_TLM covers the outcome
    side (convoy threat, convoy war-support malus) but never the assignment side."""
    print("# mission ids are empirically mapped - see _NAVAL_MISSIONS in this file.")
    print("# 'idle' = mission none|reserve (parked in port). screens = "
          + "+".join(_NAVAL_SCREENS) + ".")
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            secs = collect_sections(fh, args.tag, ("units",))
        if "units" not in secs:
            print(f"{date}\t({os.path.basename(f)}: no units section for {args.tag})")
            continue
        fleets = _parse_fleets(secs["units"])
        per = collections.defaultdict(collections.Counter)
        total = collections.Counter()
        idle_led = idle_unled = ships_led = ships_unled = 0
        for fl in fleets:
            n = sum(sum(t["ships"].values()) for t in fl["tfs"])
            idle = sum(sum(t["ships"].values()) for t in fl["tfs"]
                       if t["mission"] in _NAVAL_IDLE or t["mission"] is None)
            if fl["leader"]:
                ships_led += n
                idle_led += idle
            else:
                ships_unled += n
                idle_unled += idle
            for t in fl["tfs"]:
                per[t["mission"] or "none"].update(t["ships"])
                total.update(t["ships"])

        def scr(c):
            return sum(v for k, v in c.items() if k in _NAVAL_SCREENS)

        ships = sum(total.values())
        idle = idle_led + idle_unled
        led = sum(1 for x in fleets if x["leader"])
        print(f"{date}\t{args.tag}\tships={ships} (screens {scr(total)})\t"
              f"fleets={len(fleets)} ({led} with admiral, {len(fleets) - led} without)")
        order = sorted(per, key=lambda m: (m in _NAVAL_IDLE, m))
        cells = [f"{m}={sum(per[m].values())}({scr(per[m])}scr)" for m in order]
        print("        missions: " + "  ".join(cells))
        pct = (100.0 * idle / ships) if ships else 0.0
        share = (100.0 * idle_unled / idle) if idle else 0.0
        print(f"        idle={idle} ({pct:.0f}% of the navy); "
              f"{idle_unled} of them ({share:.0f}%) sit in fleets with NO admiral "
              f"[admiral-led fleets: {ships_led} ships, {idle_led} idle]")
        if args.fleets:
            for fl in fleets:
                mm = collections.Counter(t["mission"] or "none" for t in fl["tfs"])
                n = sum(sum(t["ships"].values()) for t in fl["tfs"])
                print("          %-34s adm=%-3s tf=%-3d ships=%-4d regions=%-2d %s"
                      % ((fl["name"] or "")[:34], "yes" if fl["leader"] else "NO",
                         len(fl["tfs"]), n, len(fl["regions"]),
                         " ".join(f"{k}:{v}" for k, v in sorted(mm.items()))))


# --- priority construction (PC) ---------------------------------------------
#
# The PC queue is a country-scope array (wa_ai_pc_queue) of project ids plus ~11
# parallel indexed variable families keyed by that id. Owner:
# common/scripted_effects/WA_AI_CONSTRUCTION_PRIORITY_core.txt.

# wa_ai_pc_building_type -> what WA_AI_PC_add_finished_building_by_id actually
# spawns. SOURCE OF TRUTH is that effect's ladder, not the cost table above it in
# the same file (the cost table shares the numbering but prices 9/10 as
# conversions and says nothing about which building appears).
_PC_BUILDING = {
    1: "infrastructure", 2: "air_base", 3: "anti_air", 4: "radar",
    5: "arms_factory", 6: "industrial_cx", 7: "dockyard", 8: "synth_refinery",
    9: "conv_mil2civ", 10: "conv_civ2mil", 11: "hydro_steel", 12: "hydro_alu",
    13: "railway", 14: "naval_base", 15: "steel_refinery", 16: "alu_refinery",
    17: "supply_hub",   # Fix 95: supply_node, province building (corridor depots)
}

# wa_ai_pc_type_id is the STRATEGY tag, not the building type. Only callers that
# need an independent _project_queue_max budget set one (Fix 47); most call sites
# leave it 0, so "-" is the normal reading, not a missing value.
_PC_TYPE_ID = {
    0: "-",                # unscoped: shares the country-wide per-building budget
    13: "rail",            # constant:wa_ai_pc.type_id.rail  (railway_core / _helpers)
    14: "port",            # frontier-port helper       (railway_helpers)
    20: "uk_air",          # constant:wa_ai_pc.type_id.uk_air      (strategies)
    21: "theatre_air",     # constant:wa_ai_pc.type_id.theatre_air (strategies)
    23: "islands",         # constant:wa_ai_pc.type_id.islands     (strategies, Fix 90)
    24: "supply_line",     # constant:wa_ai_pc.type_id.supply_line (strategies, Fix 90b)
    25: "inf_resource",    # constant:wa_ai_pc.type_id.inf_resource (queue_functions, Fix 90b)
    27: "corridor",        # constant:wa_ai_pc.type_id.corridor (railway_core corridor pass, Fix 95)
}

# Fix 41 priority band table - one declaration, common/script_constants/wa_ai_pc.txt
# (constant:wa_ai_pc.prio.*), read by core / strategies / queue_functions / railway_*.
# 1100 = rail-war x1.1 for a high-value route and is the highest value a post-Fix-41
# build can write; anything above it is a legacy pre-Fix-41 priority that the next
# assign_factories pass clamps to 1000.
# REGISTRY: every value in _PC_TYPE_ID, _PC_BANDS and the _PC_* allocation constants
# below is a mirror registered in tools/constants_registry.json;
# `python tools/check_constants.py` fails when the script and this table disagree.
_PC_BANDS = ((1100, "rail-war+"), (1000, "rail-war"), (500, "rail-prewar"),
             (350, "air-front"), (300, "air-basing"), (250, "strategic"),
             (100, "default"))

# Allocation constants: constant:wa_ai_pc.alloc.* (common/script_constants/wa_ai_pc.txt).
_PC_ALLOC_FRACTION = 0.40
_PC_STABLE_BASE_FRACTION = 0.30
_PC_ALLOC_HARD_CAP_FRACTION = 0.50
_PC_STALL_CANCEL_WEEKS = 30
_PC_AGING_LANE_WEEKS = 12
_PC_MAX_PER_PROJECT = 20

# Families cleared by WA_AI_PC_end_project_by_id and never initialised by
# WA_AI_PC_start_project: an index is absent until something writes it.
_PC_SPARSE = ("assigned_factories", "stall_weeks", "build_time")


def _pc_band(prio):
    if prio is None:
        return "?"
    if prio > 1100:
        return "LEGACY!"
    for floor, name in _PC_BANDS:
        if prio >= floor:
            return name
    return "sub-default"


def _pc_parse_vars(sec):
    """(scalars, families) over the PC namespaces of a `variables` section.

    Both wa_ai_pc_* (system state) and wa_tlm_pc_* (telemetry) are collected: the
    per-project queue-entry stamp lives in the telemetry namespace on purpose, so
    that writing it may read global.WA_TLM_clock.

    families[name][index] = value. An array's declared length is kept in scalars
    as "name^num" so a queue whose ^num disagrees with its element count stays
    visible instead of being silently normalised."""
    scalars, families = {}, {}
    for line in (l.strip() for l in sec[1:-1]):
        m = re.match(r"^(wa_(?:ai|tlm)_pc_[a-z0-9_]+?)(?:\^(\d+|num))?=(-?[\d.]+)$",
                     line)
        if not m:
            continue
        name, idx, val = m.group(1), m.group(2), float(m.group(3))
        if idx is None:
            scalars[name] = val
        elif idx == "num":
            scalars[name + "^num"] = val
        else:
            families.setdefault(name, {})[int(idx)] = val
    return scalars, families


def _pc_num(v, absent="-"):
    """Absent -> '-', present -> the number. Keeping the two apart is the point of
    this command: script reads an absent variable as 0 (check_variable), and so
    does a naive parse, which is how "80 railway projects all at stall_weeks 0"
    got reported for a queue where the stall counter had simply never been
    written for any of them."""
    return absent if v is None else f"{v:g}"


def _pc_int(v, absent="-"):
    """Rounded reading for the columns whose script value carries fractional
    noise (progress decays by speed*factories*days; build_time is that divided
    again). The fraction is never the question being asked."""
    return absent if v is None else f"{v:.0f}"


def _pc_median(vals):
    s = sorted(vals)
    return s[len(s) // 2]


def cmd_pc(args):
    """Priority-construction queue: per-project table + per-country summary."""
    print("# Rows are in QUEUE ORDER. WA_AI_PC_assign_factories rebuilds wa_ai_pc_queue "
          "sorted by")
    print("#   priority descending and then fills winner-takes-most from the top - "
          f"min(pool, {_PC_MAX_PER_PROJECT})")
    print("#   each - so the funded projects are the head of the queue and everything "
          "below them sits")
    print("#   at 0 until they complete. The order is only sorted AS OF the last assign "
          "pass, though:")
    print("#   the strategies run from a 2-day background event and APPEND, so a save "
          "taken mid-week")
    print("#   shows a sorted prefix plus an unsorted tail of projects that have never "
          "been costed for")
    print("#   factories. The 'appended since the last assignment pass' line below counts "
          "that tail -")
    print("#   read it before concluding that a high-priority project is being starved.")
    print("# ABSENT IS NOT ZERO for fact/stall/eta. WA_AI_PC_start_project does not "
          "initialise those")
    print("#   three families and WA_AI_PC_end_project_by_id clears them, so '-' means "
          "'never written")
    print("#   for this project' - never funded, or never yet seen by a weekly stall "
          "sweep - while '0'")
    print("#   means a pass ran and wrote zero. Script cannot tell them apart "
          "(check_variable reads")
    print("#   absent as 0); this command can, and the difference is what separates an "
          "aged-out")
    print("#   project from a freshly requeued one.")
    print("# age_m is MONTHS IN THE QUEUE, from wa_tlm_pc_queued_t (a WA_TLM v14+ metric) "
          "against the")
    print("#   country's wa_tlm_pc_last_t. It reads '-' on older builds, where queue age "
          "is recorded")
    print("#   nowhere at all. Do not substitute the stall column for it: stall_weeks "
          "resets to 0 every")
    print("#   time a project is funded for a week, so it is the current starvation "
          "streak, and the two")
    print("#   diverge on exactly the projects worth asking about.")
    print("# eta_d is wa_ai_pc_build_time, days left at the CURRENT assignment. It is "
          "only refreshed")
    print("#   for projects that had factories this week, so it is printed only for "
          "those; on an")
    print("#   unfunded project the stored value is a stale reading from whenever it "
          "last had any.")
    print("# civ = industrial_complex levels in states this tag CONTROLS. It is an UPPER "
          "BOUND on the")
    print("#   engine's num_of_civilian_factories (occupied-territory factories are only "
          "partly")
    print("#   available) and it is NOT the pool PC may touch. The real allocation base, "
          "the engine's")
    print("#   num_of_civilian_factories_available_for_projects, is not serialized "
          "anywhere in a save -")
    print("#   read wa_tlm_pc_civs_avail / wa_tlm_pc_alloc_base on instrumented builds "
          "(`tlm TAG FILE`).")
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        civ = 0
        with open_save(f) as fh:
            # states={} precedes countries={} in every save, so the state sweep and
            # the country sections share one pass over the file.
            for _sid, lines in iter_state_blocks(fh):
                if not lines:
                    continue
                b, _owner, controller = _state_buildings(lines)
                if controller == args.tag:
                    civ += b.get("industrial_complex", 0)
            secs = collect_sections(fh, args.tag, ("variables", "flags"))
        print(f"=== {date}  {args.tag}  ({os.path.basename(f)}) ===")
        if "variables" not in secs:
            print("  (no variables section - country dead or never scripted)")
            continue
        scalars, fam = _pc_parse_vars(secs["variables"])
        if not scalars and not fam:
            print("  (no wa_ai_pc_* variables - PC never initialised for this country)")
            continue

        queue = fam.get("wa_ai_pc_queue", {})
        order = [int(queue[i]) for i in sorted(queue)]

        def val(family, pid):
            return fam.get("wa_ai_pc_" + family, {}).get(pid)

        # Queue age in months. wa_tlm_pc_queued_t is the clock when the slot entered
        # the queue (v14+); wa_tlm_pc_last_t is the clock at the country's last monthly
        # sample, i.e. "now" to within a month - the save's own date is not on the same
        # axis. Absent on pre-v14 builds, where age is simply not recorded anywhere.
        now_t = scalars.get("wa_tlm_pc_last_t")
        queued = fam.get("wa_tlm_pc_queued_t", {})

        def age(pid):
            q = queued.get(pid)
            return None if q is None or now_t is None else max(0.0, now_t - q)

        # --- summary -------------------------------------------------------
        total = scalars.get("wa_ai_pc_assigned_factories_total")
        air = scalars.get("wa_ai_pc_air_factories_assigned")
        active = scalars.get("wa_ai_pc_active_projects")
        nonrail = scalars.get("wa_ai_pc_active_nonrail_projects")
        summed = sum(v for v in (val("assigned_factories", p) for p in order)
                     if v is not None)
        print(f"  queue={len(order)} projects   assigned_factories_total="
              f"{_pc_num(total)} (per-project sum {summed:g})   "
              f"air_factories_assigned={_pc_num(air)}")
        if total is not None and abs(total - summed) > 0.5:
            print(f"  (!) assigned_factories_total ({total:g}) disagrees with the "
                  f"per-project sum ({summed:g}) - the aggregate is stale. On a tag "
                  "with no states and no units this is the annihilated-country freeze: "
                  "the country block survives and every variable in it keeps its last "
                  "live value")
        cap = _PC_ALLOC_HARD_CAP_FRACTION * civ
        floor = _PC_STABLE_BASE_FRACTION * civ
        share = f"{100.0 * summed / civ:.1f}%" if civ else "n/a"
        capshare = f"{100.0 * summed / cap:.0f}%" if cap else "n/a"
        print(f"  civ levels controlled={civ}   PC is using {share} of them   "
              f"({capshare} of the {cap:.0f}-factory hard ceiling; stable-base floor "
              f"{floor:.0f})")
        ovr = scalars.get("wa_ai_pc_override_max_factories_factor")
        live = re.search(r"WA_AI_PC_override_max_factories_factor=\{\s*value=(-?\d+)"
                         r'\s*(?:date="([^"]+)")?', "".join(secs.get("flags", [])))
        if ovr is not None or live:
            state = (f"flag LIVE (set {live.group(2)}) -> base x{_pc_num(ovr)}"
                     if live else
                     f"flag EXPIRED -> base x{_PC_ALLOC_FRACTION} "
                     f"(stale variable {_pc_num(ovr)} is inert without the flag)")
            print(f"  alloc override: {state}")
        else:
            print(f"  alloc override: none -> base x{_PC_ALLOC_FRACTION} "
                  "(constant:wa_ai_pc.alloc.fraction)")
        if active is not None and active != len(order):
            print(f"  (!) wa_ai_pc_active_projects={active:g} but the queue holds "
                  f"{len(order)} - the +1/-1 bookkeeping has desynced (it is "
                  "resynced on the next assign_factories pass)")
        print(f"  gate counters: active_projects={_pc_num(active)} "
              f"active_nonrail={_pc_num(nonrail)} "
              "(nonrail excludes types 13/14 and feeds the `< 5` strategy gates)")

        # --- per building type ---------------------------------------------
        groups = collections.OrderedDict()
        for pid in order:
            bt = val("building_type", pid)
            key = int(bt) if bt is not None else -1
            groups.setdefault(key, []).append(pid)
        if groups:
            print(f"  {'building type':<20}{'n':>4}{'funded':>8}{'civs':>6}   "
                  f"{'priority bands':<30}{'stall wks min/med/max':<26}age_m med")
        for key in sorted(groups, key=lambda k: -len(groups[k])):
            pids = groups[key]
            label = f"{_PC_BUILDING.get(key, 'type ' + str(key))}({key})"
            facts = [val("assigned_factories", p) for p in pids]
            funded = sum(1 for v in facts if v)
            civs = sum(v for v in facts if v)
            bands = collections.Counter(_pc_band(val("priority", p)) for p in pids)
            bandtxt = " ".join(f"{b}x{c}" for b, c in bands.most_common())
            st = [v for v in (val("stall_weeks", p) for p in pids) if v is not None]
            sttxt = (f"{min(st):g}/{_pc_median(st):g}/{max(st):g}"
                     f" ({len(st)}/{len(pids)} written)"
                     if st else f"- (0/{len(pids)} written)")
            ag = [v for v in (age(p) for p in pids) if v is not None]
            agtxt = f"{_pc_median(ag):.0f}" if ag else "-"
            print(f"  {label:<20}{len(pids):>4}{funded:>8}{civs:>6.0f}   "
                  f"{bandtxt:<30}{sttxt:<26}{agtxt}")
        tags = collections.Counter(
            _PC_TYPE_ID.get(int(val("type_id", p) or 0), f"id {val('type_id', p):g}")
            for p in order)
        if tags:
            print("  strategy tags (wa_ai_pc_type_id): "
                  + "  ".join(f"{k}x{v}" for k, v in tags.most_common()))

        # --- anomalies ------------------------------------------------------
        # Length of the descending-priority prefix = what the last assign pass saw.
        # Everything after it was appended by a strategy since, and has never been
        # eligible for factories: an unfunded project inside the tail is NOT starved.
        tail = 0
        for i in range(1, len(order)):
            if (val("priority", order[i]) or 0) > (val("priority", order[i - 1]) or 0):
                tail = len(order) - i
                break
        if tail:
            print(f"  {tail} project(s) appended since the last assignment pass "
                  "(queue order breaks its descending-priority sort there) - they have "
                  "not yet been eligible for factories, so 0/'-' there is expected")
        for family in _PC_SPARSE:
            missing = sum(1 for p in order if val(family, p) is None)
            if missing and missing == len(order) and len(order) > 4:
                print(f"  (!) wa_ai_pc_{family} is absent for ALL {missing} queued "
                      "projects - that code path has not run for this country since "
                      "the queue was last rebuilt; the value is unknown, not 0")
        st_all = [v for v in (val("stall_weeks", p) for p in order) if v is not None]
        if len(st_all) > 4 and len(set(st_all)) == 1:
            print(f"  (!) every written stall counter reads {st_all[0]:g} - a "
                  "synchronised whole-queue reset, so per-project age is not "
                  "measurable from this save alone")
        aged = [p for p in order
                if (val("stall_weeks", p) or 0) > _PC_STALL_CANCEL_WEEKS]
        if aged:
            print(f"  (!) {len(aged)} project(s) past the {_PC_STALL_CANCEL_WEEKS}-week "
                  "stall-sweep bar are still queued - the sweep only fires when "
                  "assigned_factories_total > 0")
        lane = [p for p in order
                if _PC_AGING_LANE_WEEKS <= (val("stall_weeks", p) or 0)]
        if lane:
            print(f"  {len(lane)} project(s) at or past the {_PC_AGING_LANE_WEEKS}-week "
                  "overtake-lane bar (one is served per weekly pass)")
        broken = [p for p in order if not val("target_state", p)]
        if broken:
            print(f"  (!) {len(broken)} queued project(s) carry target_state 0/absent - "
                  "the cleanup pass removes these as broken")
        slots = fam.get("wa_ai_pc_target_state", {})
        orphans = [i for i, v in slots.items() if v and i not in order]
        if orphans:
            print(f"  (!) {len(orphans)} slot(s) hold a target_state but are not in the "
                  f"queue: {orphans[:12]}{' ...' if len(orphans) > 12 else ''} - "
                  "leaked slots, reusable only after target_state returns to 0")

        # --- per-project table ----------------------------------------------
        pat = re.compile(args.match) if args.match else None
        rows, labels, hitlabels = [], [], []
        for rank, pid in enumerate(order):
            bt = val("building_type", pid)
            btn = _PC_BUILDING.get(int(bt), f"type{bt:g}") if bt is not None else "?"
            tid = val("type_id", pid)
            tidn = _PC_TYPE_ID.get(int(tid), f"id{tid:g}") if tid is not None else "?"
            prio = val("priority", pid)
            cost = val("project_cost", pid)
            prog = val("progress", pid)
            done = (f"{100.0 * (cost - prog) / cost:.0f}%"
                    if cost and prog is not None else "-")
            label = f"{btn} {tidn} {_pc_band(prio)}"
            labels.append(label)
            if pat and not pat.search(label):
                continue
            hitlabels.append(label)
            rows.append((rank, pid, btn, tidn, val("target_state", pid),
                         val("target_province", pid), val("connect_province", pid),
                         prio, val("assigned_factories", pid), prog, cost, done,
                         val("stall_weeks", pid), val("build_time", pid), age(pid)))
        if pat:
            # --match filters the composed '<building> <strategy tag> <priority band>'
            # LABEL of each project, and nothing else. It does NOT see the WA strategy
            # name or the # Fix nn tag: `pc GER --match corridor` matched 0 rows for two
            # checklist items because the label carries the building type (railway) and
            # the type_id name, never the caller's own wording.
            _match_report(args.match, hitlabels, labels, "project labels")
        if not rows:
            if not pat:
                print("  (queue empty)")
            continue
        print(f"  {'#':>3} {'id':>4}  {'building':<15}{'tag':<12}{'state':>6}"
              f"{'prov':>7}{'->prov':>7}{'prio':>7}{'fact':>5}"
              f"{'progress':>10}{'cost':>8}{'done':>6}{'stall':>6}{'eta_d':>7}"
              f"{'age_m':>6}")
        shown = rows if not args.limit else rows[: args.limit]
        for (rank, pid, btn, tidn, state, prov, conn, prio, fact, prog, cost,
             done, stall, eta, agem) in shown:
            print(f"  {rank:>3} {pid:>4}  {btn:<15}{tidn:<12}{_pc_num(state):>6}"
                  f"{_pc_num(prov, '0'):>7}{_pc_num(conn, '0'):>7}{_pc_num(prio):>7}"
                  f"{_pc_num(fact):>5}{_pc_int(prog):>10}{_pc_int(cost):>8}"
                  f"{done:>6}{_pc_num(stall):>6}{_pc_int(eta) if fact else '-':>7}"
                  f"{_pc_int(agem):>6}")
        if len(shown) < len(rows):
            print(f"  ... {len(rows) - len(shown)} more project(s); "
                  "use --limit 0 or --match")


_MAP_STATE_PROVINCES = os.path.join(
    REPO, "common", "scripted_effects", "WA_AI_MAP_state_provinces.txt")

_province_state = None


def province_state_map():
    """{province_id: state_id} from the generated WA map data, or {} if unreadable.

    The save cannot answer this: a state block carries owner/controller/buildings but
    never lists its provinces. Coverage is land provinces only (11 203 of ~14 000), and
    impassable/wasteland states are absent entirely - callers must report a scope state
    with no provinces rather than silently treating it as uncontested.
    """
    global _province_state
    if _province_state is None:
        _province_state = {}
        try:
            with io.open(_MAP_STATE_PROVINCES, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    m = re.search(r"WA_AI_MAP_province_state_id\^(\d+) = (\d+)", line)
                    if m:
                        _province_state[int(m.group(1))] = int(m.group(2))
        except OSError:
            pass
    return _province_state


def iter_province_blocks(fh):
    """Yield (province_id, lines) for every entry of the top-level provinces={} block.

    Depth-anchored rather than indentation-anchored: this file's sibling rail_way={}
    block puts its province keys at column 0, so a tab-anchored key regex is not safe
    over the top-level blocks. provinces={} precedes states={} in the save, so one pass
    can read this and then hand the same handle to iter_state_blocks.
    """
    for line in fh:
        if line.startswith("provinces={"):
            break
    else:
        return
    depth, pid, buf, pdepth = 1, None, None, 0
    for line in fh:
        if buf is None:
            m = re.match(r"^\s*(\d+)=\{", line)
            if m and depth == 1:
                pid = int(m.group(1))
                pdepth = line.count("{") - line.count("}")
                if pdepth <= 0:
                    yield pid, []
                    continue
                buf = []
                continue
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                return
            continue
        pdepth += line.count("{") - line.count("}")
        if pdepth <= 0:
            yield pid, buf
            buf = None
            continue
        buf.append(line)


def province_body(lines):
    """(controller_or_None, {building: summed level}) for one province block.
    Public: rail.py reads province rail levels through this.

    A province omits controller= when its controller is its state's controller, exactly
    as a state omits it when the controller is the owner. The caller applies the two
    defaults in order (province -> state controller -> state owner).
    """
    ctrl, blds = None, {}
    bdepth, odepth, name, in_b = 0, 0, None, False
    for line in lines:
        s = line.strip()
        opens = line.count("{") - line.count("}")
        if not in_b:
            if odepth == 0 and s.startswith("buildings={"):
                in_b, bdepth = True, opens
                continue
            # Only depth-0 keys are the province's OWN fields. Province blocks do carry
            # nested sub-blocks (strategic_province_location={}), and reading controller=
            # at any depth is how the sibling faction parser came to report an
            # intelligence agency's spymaster title as the faction name. First wins.
            if odepth == 0 and ctrl is None:
                m = re.match(r'^controller="(\w+)"', s)
                if m:
                    ctrl = m.group(1)
            odepth += opens
            continue
        before = bdepth
        bdepth += opens
        if bdepth <= 0:
            in_b = False
            continue
        if before == 1:
            m = re.match(r"^([a-z_0-9]+)=\{", s)
            name = m.group(1) if m else None
        elif before >= 2 and name:
            m = re.match(r"^level=(-?\d+)", s)
            if m:
                blds[name] = blds.get(name, 0) + int(m.group(1))
    return ctrl, blds


def _tally(counter, limit=8):
    """'GER 271  FRA 41  ITA 12' - descending, ties by tag."""
    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    head = "  ".join(f"{t} {n}" for t, n in items[:limit])
    if len(items) > limit:
        head += f"  (+{len(items) - limit} more)"
    return head or "(none)"


def cmd_control(args):
    p2s = province_state_map()
    if not p2s:
        sys.exit(f"cannot read {_MAP_STATE_PROVINCES} - province->state join unavailable")
    s2p = collections.defaultdict(list)
    for prov, st in p2s.items():
        s2p[st].append(prov)

    scope = args.scope.strip()
    owner_scope, want_ids = None, None
    if ":" in scope:
        kind, val = scope.split(":", 1)
        if kind.lower() != "owner":
            sys.exit("SCOPE is a comma-separated state-id list or 'owner:TAG'")
        owner_scope = val.upper()
    else:
        want_ids = set(int(x) for x in re.findall(r"\d+", scope))
        if not want_ids:
            sys.exit("SCOPE is a comma-separated state-id list or 'owner:TAG'")

    print("# Province control, with BOTH omitted-field defaults applied: a province "
          "omits controller=")
    print("#   when it matches its state's controller, and a state omits controller= "
          "when it matches")
    print("#   its owner. Reading either literally is how a contested theatre reports "
          "the wrong holder.")
    print("# The state-controller column is the engine's single-owner label for the "
          "whole state; when")
    print("#   the province split disagrees with it, the split is the ground truth.")

    for meta, f in sorted_by_date([resolve(x) for x in args.files]):
        date = meta.get("date", "?")
        pctrl, pbld = {}, {}
        states = {}
        with open_save(f) as fh:
            for pid, lines in iter_province_blocks(fh):
                if not lines or pid not in p2s:
                    continue
                c, b = province_body(lines)
                if c is not None:
                    pctrl[pid] = c
                if b and args.buildings:
                    pbld[pid] = b
            # provinces={} precedes states={}, so the same handle continues forward.
            for sid, lines in iter_state_blocks(fh):
                if not lines:
                    states[sid] = (None, None)
                    continue
                # Reuse the proven state parser instead of a second, looser one - the
                # buildings dict is discarded here, but there is only one place that can
                # drift on how owner/controller are anchored.
                _b, owner, ctrl = _state_buildings(lines)
                states[sid] = (owner, ctrl)

        if owner_scope:
            sel = sorted(s for s, (o, _c) in states.items() if o == owner_scope)
        else:
            sel = sorted(want_ids)

        st_count, pr_count = collections.Counter(), collections.Counter()
        bld_by_ctrl = collections.defaultdict(collections.Counter)
        rows, no_map, missing = [], [], []
        for sid in sel:
            if sid not in states:
                missing.append(sid)
                continue
            owner, sctrl = states[sid]
            st_count[sctrl or "?"] += 1
            provs = s2p.get(sid, [])
            if not provs:
                no_map.append(sid)
                continue
            per = collections.Counter()
            for prov in provs:
                holder = pctrl.get(prov) or sctrl or owner or "?"
                per[holder] += 1
                pr_count[holder] += 1
                for name, lvl in pbld.get(prov, {}).items():
                    bld_by_ctrl[holder][name] += lvl
            if len(per) > 1 or (sctrl and sctrl not in per):
                rows.append((sid, owner, sctrl, per))

        label = f"owner:{owner_scope}" if owner_scope else f"{len(sel)} state ids"
        print(f"\n=== {date}  {os.path.basename(f)}  scope={label}  "
              f"({len(sel)} states, {sum(pr_count.values())} provinces) ===")
        print(f"  by state controller : {_tally(st_count)}")
        print(f"  by province control : {_tally(pr_count)}")
        if missing:
            print(f"  not present in this save's states={{}}: "
                  f"{', '.join(str(s) for s in missing)}")
        if no_map:
            print(f"  no provinces in the generated map data (impassable/wasteland "
                  f"states are absent from it): {', '.join(str(s) for s in no_map[:20])}"
                  f"{' ...' if len(no_map) > 20 else ''}")
        if rows:
            print(f"  states whose province split contradicts the state controller "
                  f"({len(rows)}):")
            print(f"    {'state':<7}{'owner':<7}{'st.ctrl':<9}provinces by controller")
            # --limit 0 means unlimited, as in cmd_pc; do not silently print nothing.
            shown = rows if not args.limit else rows[: args.limit]
            for sid, owner, sctrl, per in shown:
                print(f"    {sid:<7}{owner or '?':<7}{sctrl or '?':<9}{_tally(per)}")
            if len(shown) < len(rows):
                print(f"    ... {len(rows) - len(shown)} more (raise --limit, 0 = all)")
        else:
            print("  no state's province split contradicts its state controller")
        if args.buildings:
            names = sorted({n for c in bld_by_ctrl.values() for n in c})
            print(f"  province-scoped buildings by province controller "
                  f"(naval_base and rail_way live ONLY here, never in a state block):")
            print(f"    {'controller':<12}" + "".join(f"{n:>19}" for n in names))
            for holder in sorted(bld_by_ctrl, key=lambda h: -sum(bld_by_ctrl[h].values())):
                print(f"    {holder:<12}"
                      + "".join(f"{bld_by_ctrl[holder].get(n, 0):>19}" for n in names))
        if args.provinces:
            print(f"    {'province':<10}{'state':<7}{'holder':<8}explicit?")
            for sid in sel:
                if sid not in states:
                    continue
                owner, sctrl = states[sid]
                for prov in sorted(s2p.get(sid, [])):
                    holder = pctrl.get(prov) or sctrl or owner or "?"
                    mark = "province" if prov in pctrl else "inherited"
                    print(f"    {prov:<10}{sid:<7}{holder:<8}{mark}")


_REL_KINDS = ("war_relation", "puppet", "lend_lease", "guarantee",
              "non_aggression_pact", "military_access", "docking_rights")
_REL_FIELDS = ("first", "second", "start_date", "date")


def iter_relations(fh):
    """Yield (owner, counterpart, kind, fields) for every relation sub-block in every
    country's diplomacy/active_relations. One pass, depth-tracked.

    Each country lists ~409 counterparts, almost all carrying nothing but cached_sum and
    attitude; only counterparts with an actual relation sub-block are yielded.
    """
    for line in fh:
        if line.startswith("countries={"):
            break
    else:
        return
    depth = 1
    tag = None
    diplo_d = ar_d = cp_d = kind_d = None
    cp = kind = None
    fields = {}
    for line in fh:
        s = line.strip()
        opens = line.count("{") - line.count("}")
        if kind is not None:
            m = re.match(r'^(%s)="?([^"\s]*)"?' % "|".join(_REL_FIELDS), s)
            if m:
                fields.setdefault(m.group(1), m.group(2))
        elif cp is not None:
            m = re.match(r"^(%s)=\{" % "|".join(_REL_KINDS), s)
            if m:
                kind, kind_d, fields = m.group(1), depth, {}
        elif ar_d is not None:
            m = re.match(r'^"?([A-Z][A-Z0-9]{2})"?=\{', s)
            if m:
                cp, cp_d = m.group(1), depth
        elif diplo_d is not None:
            if s.startswith("active_relations={"):
                ar_d = depth
        elif tag is not None:
            if s.startswith("diplomacy={"):
                diplo_d = depth
        elif depth == 1:
            m = re.match(r"^\t([A-Z][A-Z0-9]{2})=\{", line)
            if m:
                tag = m.group(1)
        depth += opens
        # Close contexts innermost-first as the depth falls back past each opener.
        if kind is not None and depth <= kind_d:
            yield tag, cp, kind, fields
            kind, fields = None, {}
        if cp is not None and depth <= cp_d:
            cp = None
        if ar_d is not None and depth <= ar_d:
            ar_d = None
        if diplo_d is not None and depth <= diplo_d:
            diplo_d = None
        if tag is not None and depth <= 1:
            tag = None
        if depth <= 0:
            return


def _faction_block(body):
    """(name, ideology, [members]) from one faction block's lines, depth-anchored.

    Depth matters twice here. A faction block CONTAINS nested intelligence-agency
    sub-blocks that carry their own name=, and a faction that was never renamed has no
    depth-1 name= at all - so a whole-body name grep reads an agency's spymaster title
    as the faction's name (the Comintern read as "HSpymaster!" until this was anchored).
    Fall back to the icon, which every faction has.
    """
    name = ideo = icon = None
    members = []
    depth, in_members = 0, False
    for line in body:
        s = line.strip()
        before = depth
        depth += line.count("{") - line.count("}")
        if in_members:
            if before >= 1:
                members.extend(re.findall(r'"([A-Z][A-Z0-9]{2})"', s))
            if depth <= 0:
                in_members = False
            continue
        if before != 0:
            continue
        if s.startswith("members={"):
            members.extend(re.findall(r'"([A-Z][A-Z0-9]{2})"', s))
            in_members = depth > 0
            continue
        m = re.match(r'^name="([^"]*)"', s)
        if m:
            name = m.group(1)
            continue
        m = re.match(r"^ideology=(\w+)", s)
        if m:
            ideo = m.group(1)
            continue
        m = re.match(r'^icon="GFX_faction_(?:logo_|icon_)?(\w+)"', s)
        if m:
            icon = m.group(1)
    return name or (icon or "?"), ideo or "?", members


def iter_factions(fh):
    """Yield (name, ideology, [members]) for each top-level faction={} block.

    Faction membership is NOT in a country block, and there is no leader= field -
    members[0] is the leader (corroborated on 7c7803a8 1943.11: ENG, SOV, GER, CHI, JAP
    lead the five factions). The faction blocks sit after countries={} in the save.
    """
    depth = 0
    grab = None
    body = None
    for line in fh:
        if grab is None:
            if depth == 0 and line.startswith("faction={"):
                grab, body = line.count("{") - line.count("}"), []
                continue
            depth += line.count("{") - line.count("}")
            continue
        grab += line.count("{") - line.count("}")
        if grab <= 0:
            yield _faction_block(body)
            grab, body = None, None
            continue
        body.append(line)


def cmd_relations(args):
    print("# Alliances, subjects and wars, read from BOTH sides. Three layouts, three "
          "traps:")
    print("#   faction membership is a TOP-LEVEL faction={} block with no leader= field "
          "(members[0]")
    print("#     is the leader), puppet={} sits in the OVERLORD's block, and "
          "war_relation={} is")
    print("#     written on ONE side only - so a single-country read silently loses wars.")
    for meta, f in sorted_by_date([resolve(x) for x in args.files]):
        rel = collections.defaultdict(list)
        with open_save(f) as fh:
            for owner, cp, kind, fields in iter_relations(fh):
                rel[kind].append((owner, cp, fields))
            factions = list(iter_factions(fh))
        print(f"\n=== {meta.get('date', '?')}  {os.path.basename(f)} ===")

        fac_of = {}
        for name, ideo, members in factions:
            for tag in members:
                fac_of[tag] = (name, members[0] if members else "?")
        if args.tag is None:
            for name, ideo, members in factions:
                print(f"  {name:<22} {ideo:<12} leader={members[0] if members else '?':<5}"
                      f" {len(members)} members: "
                      f"{' '.join(members[:14])}{' ...' if len(members) > 14 else ''}")
            for kind in _REL_KINDS:
                n = len(rel.get(kind, ()))
                if n:
                    print(f"  {kind:<22} {n} recorded")
            continue

        tag = args.tag.upper()
        fac = fac_of.get(tag)
        print(f"  faction        : "
              + (f"{fac[0]} (leader {fac[1]})" if fac else "none"))
        wars = []
        for owner, cp, fl in rel.get("war_relation", ()):
            first, second = fl.get("first"), fl.get("second")
            if tag not in (first, second):
                continue
            other = second if first == tag else first
            wars.append((other, fl.get("start_date", "?"), owner))
        if wars:
            print(f"  at war with    : {len(wars)}")
            for other, since, owner in sorted(wars, key=lambda w: date_key(w[1])):
                side = "own block" if owner == tag else f"{owner}'s block ONLY"
                print(f"    {other:<5} since {since:<16} recorded in {side}")
            missed = sum(1 for _o, _s, owner in wars if owner != tag)
            if missed:
                print(f"    -> {missed} of these are invisible from {tag}'s own block")
        else:
            print("  at war with    : none")
        subs = [cp for owner, cp, _f in rel.get("puppet", ()) if owner == tag]
        over = [owner for owner, cp, _f in rel.get("puppet", ()) if cp == tag]
        print(f"  subjects       : {' '.join(sorted(subs)) if subs else 'none'}")
        print(f"  overlord       : {' '.join(sorted(over)) if over else 'none'}")
        gave = [cp for owner, cp, fl in rel.get("lend_lease", ()) if fl.get("first") == tag]
        got = [fl.get("first") for _o, cp, fl in rel.get("lend_lease", ())
               if fl.get("second") == tag]
        print(f"  lend-lease to  : {' '.join(sorted(gave)) if gave else 'none'}")
        print(f"  lend-lease from: {' '.join(sorted(x for x in got if x)) if got else 'none'}")
        # These four carry no first=/second=, so the only thing the save tells us is WHICH
        # BLOCK holds the record. That is a serialisation detail, not a direction: a
        # non_aggression_pact is mutual by nature, and inferring direction from which side
        # a record sits on is exactly how a lend-lease flow was published inverted (see the
        # lend-lease gotcha in SKILL.md). Labelled by block, never as "to"/"from".
        # puppet and lend_lease above ARE directional - their direction is verified.
        rows = []
        for kind in ("guarantee", "non_aggression_pact", "military_access",
                     "docking_rights"):
            mine = sorted({cp for owner, cp, _f in rel.get(kind, ()) if owner == tag})
            theirs = sorted({owner for owner, cp, _f in rel.get(kind, ()) if cp == tag})
            if mine or theirs:
                rows.append((kind, mine, theirs))
        if rows:
            print(f"  --- recorded in {tag}'s own block | recorded in the other side's "
                  f"block (which side holds the record is NOT a direction) ---")
            for kind, mine, theirs in rows:
                print(f"  {kind:<20}: {' '.join(mine) or '-'}   "
                      f"| {' '.join(theirs) or '-'}")


def _wrap(text, width):
    out, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help="list saves, newest first")
    s.add_argument("--dir", default=SAVE_DIR)
    s.add_argument("--limit", type=int, default=30,
                   help="cap saves listed, 0 = unlimited (default 30)")
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

    s = sub.add_parser("army", help="deployed division count (units section only)")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.set_defaults(fn=cmd_army)

    s = sub.add_parser("navy", help="fleet/task-force/mission breakdown across saves")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--fleets", action="store_true", help="one line per fleet")
    s.set_defaults(fn=cmd_navy)

    s = sub.add_parser("resources", help="per-resource ledger across saves")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.set_defaults(fn=cmd_resources)

    s = sub.add_parser("buildings", help="building levels by owned/controlled states")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--match", help="only building names matching this regex. Refused "
                                   "with an error when it can only match a "
                                   "province-scoped building (naval_base, rail_way, "
                                   "supply_node, naval_supply_hub, bunkers) - those are "
                                   "not in a state block at all; use "
                                   "`control SCOPE FILE --buildings`")
    s.set_defaults(fn=cmd_buildings)

    s = sub.add_parser("decisions", help="decode the decision_status block")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--match", help="only decision names matching this regex")
    s.set_defaults(fn=cmd_decisions)

    s = sub.add_parser("pc", help="priority-construction queue and factory share")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--match", help="only projects whose "
                                   "'<building> <strategy tag> <priority band>' label "
                                   "matches this regex (e.g. railway, uk_air, rail-war)")
    s.add_argument("--limit", type=int, default=30,
                   help="cap project rows per save, 0 = unlimited (default 30)")
    s.set_defaults(fn=cmd_pc)

    s = sub.add_parser("control", help="province-level control of a set of states")
    s.add_argument("scope", metavar="SCOPE",
                   help="comma-separated state ids (e.g. 16,17,18) or 'owner:TAG' for "
                        "every state that TAG owns")
    s.add_argument("files", nargs="+")
    s.add_argument("--provinces", action="store_true",
                   help="one row per province: holder, and whether the holder came from "
                        "the province's own controller= or was inherited")
    s.add_argument("--buildings", action="store_true",
                   help="sum the province-scoped buildings (naval_base, rail_way, "
                        "bunker, coastal_bunker) by province controller")
    s.add_argument("--limit", type=int, default=30,
                   help="cap rows in the contradiction table, 0 = all (default 30)")
    s.set_defaults(fn=cmd_control)

    s = sub.add_parser("relations", help="factions, subjects and wars, read from both sides")
    s.add_argument("files", nargs="+")
    s.add_argument("--tag", help="one country's full picture; omit for the faction table "
                                 "plus a per-kind relation census")
    s.set_defaults(fn=cmd_relations)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
