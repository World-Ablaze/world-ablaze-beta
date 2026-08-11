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
    print("# WARNING: `resource@X` in script reads the NET AVAILABLE column "
          "(to_use[0]), NOT `produced`.")
    print("#   A negative `produced` with positive imports/transfers is still a "
          "POSITIVE resource@X")
    print("#   (ENG 1942.6: produced -329, imported +320, transfer +19 -> net ~+10). "
          "Never score a")
    print("#   resource@X guard off the produced line alone - that nearly produced a "
          "false FAIL on R25.")
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
              f"{'net':>11}{'deficit':>10}{'to_export':>11}{'exported':>10}{'resid':>8}")
        for r in sorted(names):
            prod = flat.get("produced", {}).get(r, 0.0)
            tr = flat.get("transfer_overlord_subject", {}).get(r, 0.0)
            imp = flat.get("imported", {}).get(r, 0.0)
            av = net.get(r, 0.0)
            dfc = deficit.get(r, 0.0)
            exp_t = flat.get("to_export", {}).get(r, 0.0)
            exp_a = flat.get("exported", {}).get(r, 0.0)
            resid = (prod + tr + imp) - (av + exp_t)
            mark = " !" if abs(resid) > 1.0 else ""
            print(f"  {r:<11}{prod:>11.1f}{tr:>10.1f}{imp:>11.1f}{av:>11.1f}"
                  f"{dfc:>10.1f}{exp_t:>11.1f}{exp_a:>10.1f}{resid:>8.1f}{mark}")


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


def _building_sort_key(name):
    """Sort an *_inactive twin immediately after its active counterpart."""
    base = name[: -len("_inactive")] if name.endswith("_inactive") else name
    return (base, 1 if name.endswith("_inactive") else 0)


def cmd_buildings(args):
    pat = re.compile(args.match) if args.match else None
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
        names = sorted(set(owned) | set(controlled), key=_building_sort_key)
        if pat:
            names = [n for n in names if pat.search(n)]
        if not names:
            print("  (no buildings matched)")
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


def cmd_decisions(args):
    pat = re.compile(args.match) if args.match else None
    print("# decision_status holds entry kinds with INCOMPATIBLE number semantics - "
          "they are")
    print("#   labelled separately below and must never be read as one figure:")
    print("#   * active_* / decision_to_* entries carry `days`, a countdown, and exist "
          "only while live.")
    print("#   * random_item entries carry `count`, a MONOTONE CUMULATIVE FIRE COUNTER "
          "- not a state,")
    print("#     not days. It is the right field for 'how many times did this decision "
          "fire'.")
    for meta, f in sorted_by_date([resolve(f) for f in args.files]):
        date = meta.get("date", "?")
        with open_save(f) as fh:
            sec = extract_section(fh, args.tag, "decision_status")
        print(f"=== {date}  {args.tag}  ({os.path.basename(f)}) ===")
        if not sec:
            print("  (no decision_status section)")
            continue
        kinds, taken = _decision_entries(sec)
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
                print(f"  -- random_item ({len(rows)}) --")
                print("     # count = CUMULATIVE times fired since campaign start. "
                      "Not a state, not days.")
                for e in sorted(rows, key=lambda e: -int(e.get("count", 0) or 0)):
                    tgt = e.get("target", "0")
                    suffix = f"  target={tgt}" if tgt not in ("0", None) else ""
                    print(f"     {e.get('decision','?'):<52}count={e.get('count','?')}{suffix}")
        if taken and not pat:
            print(f"  -- decisions_taken ({len(taken)}) -- "
                  "flat list, no counts or timers")
            for chunk in _wrap(" ".join(sorted(taken)), 92):
                print(f"     {chunk}")


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

    s = sub.add_parser("army", help="deployed division count (units section only)")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.set_defaults(fn=cmd_army)

    s = sub.add_parser("resources", help="per-resource ledger across saves")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.set_defaults(fn=cmd_resources)

    s = sub.add_parser("buildings", help="building levels by owned/controlled states")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--match", help="only building names matching this regex")
    s.set_defaults(fn=cmd_buildings)

    s = sub.add_parser("decisions", help="decode the decision_status block")
    s.add_argument("tag")
    s.add_argument("files", nargs="+")
    s.add_argument("--match", help="only decision names matching this regex")
    s.set_defaults(fn=cmd_decisions)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
