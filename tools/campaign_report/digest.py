"""Agent-facing Markdown digest: the campaign's high-level view in one small, labelled file.

The HTML report is for a human in a browser. An analysis agent cannot afford it, nor the
80 MB JSON behind it, so this module folds the same observations into a few hundred lines:
sampled trends per country, wars, composition, armor pressure and resource balance at the
last save, coverage caveats, and the save filenames to hand to `savegame.py` for anything
deeper. Every metric carries the evidence label of its catalog entry; nothing is invented
for a missing value (it prints as "—").
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import DEFAULT_TAGS

MAX_TAGS = 12
TREND_COLUMNS = (
    ("manpower_free", "free mp"), ("mobilised_share", "mob %"), ("divisions", "div"), ("army_manpower", "army mp"),
    ("ships", "ships"), ("aircraft", "aircraft"), ("civilian_factories", "civ"),
    ("military_factories", "mil"), ("dockyards", "dock"), ("losses", "casualties"),
    ("stability", "stab"), ("war_support", "ws"), ("economy_fatigue", "fatigue"),
)
MAX_WARS_PER_TAG = 15
MAX_ARMOR_ROWS = 8
MAX_TEMPLATES = 5


def num(value, decimals: int = 2) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.{decimals}f}"
    return str(value)


def year_month(date: str) -> tuple[int, int]:
    parts = date.split(".")
    return int(parts[0]), int(parts[1])


def sample_indices(snapshots: list[dict], every: int) -> list[int]:
    """First snapshot of every `every`-month bucket, plus the first and the last save."""
    seen, chosen = set(), []
    for i, snap in enumerate(snapshots):
        year, month = year_month(snap["date"])
        bucket = (year, (month - 1) // every)
        if bucket not in seen:
            seen.add(bucket)
            chosen.append(i)
    last = len(snapshots) - 1
    if last not in chosen:
        chosen.append(last)
    return chosen


def short_date(date: str) -> str:
    year, month = year_month(date)
    return f"{year}.{month:02d}"


def country(snapshot: dict, tag: str) -> dict | None:
    return snapshot.get("countries", {}).get(tag)


def types_line(mapping: dict | None) -> str:
    if not mapping:
        return "—"
    items = sorted(mapping.items(), key=lambda kv: (-(kv[1] or 0), kv[0]))
    return ", ".join(f"{name} {num(count)}" for name, count in items)


def absence_lines(snapshots: list[dict], tag: str) -> list[str]:
    """Contiguous save ranges where the country has no deployed-division record: the cheapest
    MEASURED signal of a capitulation or annexation, stated instead of left to the dashes."""
    ranges, start = [], None
    for snap in snapshots:
        c = country(snap, tag)
        absent = c is None or c.get("metrics", {}).get("divisions") is None
        if absent and start is None:
            start = snap["date"]
        elif not absent and start is not None:
            ranges.append((start, snap["date"]))
            start = None
    if start is not None:
        ranges.append((start, None))
    if not ranges or (len(ranges) == 1 and ranges[0][0] == snapshots[0]["date"] and ranges[0][1] is None):
        return []
    parts = [f"from {short_date(a)}" + (f" to before {short_date(b)}" if b else " to the last save") for a, b in ranges]
    return ["", f"No deployed-division record for {tag} " + "; ".join(parts) + "."]


def month_index(date: str) -> int:
    year, month = year_month(date)
    return year * 12 + month - 1


def month_label(index: int) -> str:
    return f"{index // 12}.{index % 12 + 1:02d}"


def convoy_ledger(snapshots: list[dict]) -> dict:
    """Stitch the per-save 24-month ledgers: month -> records, the latest covering save wins."""
    by_month: dict[int, list] = {}
    for snap in snapshots:
        window, rows = snap.get("convoy_window"), snap.get("convoy_losses")
        if not window or rows is None:
            continue
        for m in range(window[0], window[1] + 1):
            by_month[m] = []
        for row in rows:
            if row[0] in by_month:
                by_month[row[0]].append(row)
    return by_month


def convoy_lines(snapshots: list[dict], tags: list[str], w) -> None:
    by_month = convoy_ledger(snapshots)
    if not by_month:
        w("No convoy-loss ledger in these saves.")
        w("")
        return
    months = sorted(by_month)
    w(f"Ledger `sunk_convoys_history` stitched over {month_label(months[0])} → {month_label(months[-1])} "
      f"({len(months)} months covered; a save keeps its last 24 complete months). Shares are of the "
      f"victim's losses; convoy pool / free / kills are the last save's values.")
    w("")
    w("| country | convoys lost | attackers (share) | convoys sunk by it | top victims | pool / free at last save |")
    w("| --- | ---: | --- | ---: | --- | --- |")
    last = snapshots[-1]
    for tag in tags:
        lost, sunk, by_killer, by_victim = 0, 0, {}, {}
        for rows in by_month.values():
            for m, killer, owner, n in rows:
                if owner == tag:
                    lost += n
                    by_killer[killer] = by_killer.get(killer, 0) + n
                if killer == tag:
                    sunk += n
                    by_victim[owner] = by_victim.get(owner, 0) + n
        share = lambda d, total: ", ".join(f"{k} {round(v / total * 100)} % ({num(v)})" for k, v in sorted(d.items(), key=lambda kv: -kv[1])[:4]) if total else "—"
        metrics = (country(last, tag) or {}).get("metrics", {})
        w(f"| {tag} | {num(lost)} | {share(by_killer, lost)} | {num(sunk)} | {share(by_victim, sunk)} | "
          f"{num(metrics.get('convoys_pool'))} / {num(metrics.get('convoys_free'))} |")
    w("")


def digest(data: dict, tags: list[str] | None = None, every: int = 12) -> str:
    snapshots = data.get("snapshots") or []
    if not snapshots:
        raise ValueError("The JSON carries no observations: nothing to digest.")
    if not 1 <= every <= 24:
        raise ValueError("--every must be between 1 and 24 months.")
    tags = list(tags or data.get("default_tags") or DEFAULT_TAGS)
    if len(tags) > MAX_TAGS:
        raise ValueError(f"At most {MAX_TAGS} countries per digest ({len(tags)} requested).")
    catalog = data.get("metric_catalog", {})
    campaign = data.get("campaign", {})
    inputs = data.get("inputs", [])
    file_of = {s["date"]: s.get("file") or "?" for s in snapshots}
    last = snapshots[-1]
    rows = sample_indices(snapshots, every)
    out: list[str] = []
    w = out.append

    w(f"# Campaign digest — `{campaign.get('id', '?')}`")
    w("")
    w("Generated by `python -m tools.campaign_report` from the same observations as the HTML "
      "report. Evidence labels per metric are in the table below; a `—` is a missing value, "
      "never a zero. Counts describe the units a country commands (expeditionary forces and "
      "foreign manpower are not netted out).")
    w("")
    w(f"- Saves: {campaign.get('count', len(snapshots))} · span {snapshots[0]['date']} → {last['date']} "
      f"· selection `{campaign.get('selection', '?')}`")
    w(f"- Generated: {data.get('generated_at', '?')} · cache hits {data.get('build', {}).get('cache_hits', '?')}"
      f"/{len(snapshots)} · dependencies `{str(data.get('dependencies_sha256', ''))[:12]}`")
    versions = sorted({str(i.get("version")) for i in inputs if i.get("version")})
    mods = sorted({str(i.get("mods")) for i in inputs if i.get("mods")})
    if versions:
        w(f"- Engine: {'; '.join(versions)} · mods: {'; '.join(mods) or '?'}")
    w(f"- Countries in this digest: {', '.join(tags)} (of {len(last.get('countries', {}))} in the last save)")
    w("")

    w("## Evidence labels")
    w("")
    w("| Metric | Evidence | Source | Note |")
    w("| --- | --- | --- | --- |")
    for key, entry in catalog.items():
        w(f"| {entry.get('label', key)} (`{key}`) | **{entry.get('evidence', 'ASSUMED')}** | "
          f"`{entry.get('source', '?')}` | {entry.get('note', '')} |")
    w("")

    w(f"## Trends — first save of every {every}-month bucket, plus the last save")
    w("")
    w("`free mp` is the available pool summed from the state pools of the controlled states; `mob %` is the "
      "recruitable share of the population under the conscription law (country `manpower.ratio` / 1e7). "
      "The law at each sampled save is listed under the table.")
    w("")
    header = "| date | " + " | ".join(label for _, label in TREND_COLUMNS) + " |"
    sep = "| --- | " + " | ".join("---:" for _ in TREND_COLUMNS) + " |"
    for tag in tags:
        w(f"### {tag}")
        w("")
        present = [i for i in rows if country(snapshots[i], tag)]
        if not present:
            w(f"No observation of {tag} in the sampled saves.")
            w("")
            continue
        w(header)
        w(sep)
        for i in rows:
            c = country(snapshots[i], tag)
            if c is None:
                w(f"| {short_date(snapshots[i]['date'])} | " + " | ".join("—" for _ in TREND_COLUMNS) + " |")
                continue
            metrics = c.get("metrics", {})
            w(f"| {short_date(snapshots[i]['date'])} | " + " | ".join(num(metrics.get(k) * 100, 1) if k == "mobilised_share" and metrics.get(k) is not None else num(metrics.get(k)) for k, _ in TREND_COLUMNS) + " |")
        laws = [(short_date(snapshots[i]["date"]), (country(snapshots[i], tag) or {}).get("conscription_law")) for i in rows]
        changes = [f"{d} {law}" for k, (d, law) in enumerate(laws) if law and (k == 0 or law != laws[k - 1][1])]
        if changes:
            w("")
            w("Conscription law at the sampled saves (only changes): " + "; ".join(changes) + ".")
        for line in absence_lines(snapshots, tag):
            w(line)
        w("")

    w("## Wars — as recorded on the digested country's side")
    w("")
    w("`first`/`last` are the first and last saves that carry the war relation; a `last` before "
      "the final save means the relation vanished (peace, capitulation, annexation) and its "
      "casualty counter is the last one seen, not a certified total.")
    w("")
    for tag in tags:
        wars: dict[str, dict] = {}
        for snap in snapshots:
            c = country(snap, tag)
            if not c:
                continue
            for war in c.get("wars", []) or []:
                entry = wars.setdefault(war["id"], {"enemy": war.get("enemy"), "start": war.get("start_date"),
                                                    "first": snap["date"], "last": snap["date"], "losses": None})
                entry["last"] = snap["date"]
                entry["losses"] = war.get("losses")
        w(f"### {tag} — {len(wars)} war relation(s)")
        w("")
        if not wars:
            w("None recorded.")
            w("")
            continue
        ordered = sorted(wars.values(), key=lambda e: (-(e["losses"] or 0), e["start"] or ""))
        shown = ordered[:MAX_WARS_PER_TAG]
        w("| enemy | war start | first | last | casualties at last |")
        w("| --- | --- | --- | --- | ---: |")
        for e in sorted(shown, key=lambda e: e["start"] or ""):
            ended = "" if e["last"] == last["date"] else " (gone)"
            w(f"| {e['enemy']} | {e['start']} | {short_date(e['first'])} | {short_date(e['last'])}{ended} | {num(e['losses'])} |")
        if len(ordered) > len(shown):
            rest = ordered[len(shown):]
            w(f"| +{len(rest)} smaller | | | | {num(sum(r['losses'] or 0 for r in rest))} |")
        w("")

    w("## Convoy war")
    w("")
    convoy_lines(snapshots, tags, w)

    w(f"## Composition at the last save ({last['date']}, `{file_of[last['date']]}`)")
    w("")
    for tag in tags:
        c = country(last, tag)
        w(f"### {tag}")
        w("")
        if not c:
            w("Not present in the last save.")
            w("")
            continue
        army, navy, air = c.get("army", {}) or {}, c.get("navy", {}) or {}, c.get("air", {}) or {}
        w(f"- Army by family: {types_line(army.get('types'))}")
        templates = sorted(army.get("templates", []) or [], key=lambda t: -(t.get("count") or 0))[:MAX_TEMPLATES]
        if templates:
            w("- Largest templates: " + "; ".join(
                f"{t.get('name', '?')} ×{num(t.get('count'))} ({t.get('family', '?')})" for t in templates))
        origins = army.get("manpower_by_origin") or {}
        foreign = {k: v for k, v in origins.items() if k != tag}
        if foreign:
            w("- Foreign manpower in commanded divisions: " + types_line(foreign))
        w(f"- Navy by hull: {types_line(navy.get('types'))}")
        w(f"- Air in wings: {types_line(air.get('types'))}")
        w("")

    w("## Armor pressure at the last save")
    w("")
    w("Families whose recorded reinforcement requests exceed the stock (shortfall = requests - stock, "
      "DERIVED). Requests may include equipment in transit, so this is pressure, not a certified "
      "shortage; training need and daily output are not computed (null in the JSON).")
    w("")
    for tag in tags:
        c = country(last, tag)
        families = {name: f for name, f in (((c or {}).get("equipment", {}) or {}).get("families", {}) or {}).items() if f.get("domain") == "armor"}
        shortfall = lambda f: max(0.0, (f.get("reinforcement_need") or 0) - (f.get("stock") or 0))
        pressed = [(name, f) for name, f in families.items() if shortfall(f) > 0]
        pressed.sort(key=lambda nf: -shortfall(nf[1]))
        if not pressed:
            w(f"- {tag}: none")
            continue
        w(f"- {tag}:")
        for name, f in pressed[:MAX_ARMOR_ROWS]:
            w(f"  - {name}: shortfall {num(shortfall(f))} = requests {num(f.get('reinforcement_need'))} - stock "
              f"{num(f.get('stock'))}; deployed {num(f.get('deployed'))}, active factories {num(f.get('active_factories'))}")
        if len(pressed) > MAX_ARMOR_ROWS:
            w(f"  - +{len(pressed) - MAX_ARMOR_ROWS} more families")
    w("")

    w("## Resource balance at the last save")
    w("")
    w("Only resources with a negative effective balance (unmet demand after imports and transfers). "
      "Columns follow the save's ledger: produced, imported, available, effective.")
    w("")
    for tag in tags:
        c = country(last, tag)
        ledger = (c or {}).get("resources", {}) or {}
        short = [(name, r) for name, r in ledger.items()
                 if isinstance(r, dict) and (r.get("effective") or 0) < 0
                 and any((r.get(k) or 0) for k in ("produced", "imported", "available"))]
        short.sort(key=lambda nr: nr[1].get("effective") or 0)
        if not short:
            w(f"- {tag}: no deficit")
            continue
        w(f"- {tag}: " + "; ".join(
            f"{name} produced {num(r.get('produced'))} / imported {num(r.get('imported'))} / "
            f"available {num(r.get('available'))} / effective {num(r.get('effective'))}" for name, r in short))
    w("")

    w("## Coverage notes")
    w("")
    for warning in data.get("warnings", []) or []:
        w(f"- {warning}")
    snap_warnings = Counter(x for s in snapshots for x in (s.get("warnings") or []))
    for text, count in snap_warnings.most_common(10):
        w(f"- {text} ({count} save(s))")
    issues = Counter((tag, x) for s in snapshots for tag in tags
                     for x in ((country(s, tag) or {}).get("issues") or []))
    for (tag, text), count in issues.most_common(15):
        w(f"- {tag}: {text} ({count} save(s))")
    if not (data.get("warnings") or snap_warnings or issues):
        w("- None recorded.")
    w("")

    w("## Going deeper")
    w("")
    w("This digest carries no AI variables, flags, ideas, telemetry, battle plans or per-state "
      "control: those come from `.claude/skills/wa-savegame-analysis/scripts/savegame.py` on the "
      "save files below (skill `wa-savegame-analysis`). The full observation set is "
      "`campaign.json` next to this file (`snapshots[i].countries[TAG]`).")
    w("")
    w("Sampled rows above map to these saves:")
    w("")
    for i in rows:
        w(f"- {snapshots[i]['date']} → `{file_of[snapshots[i]['date']]}`")
    w("")
    w("All saves of the campaign, in order: " + ", ".join(f"`{file_of[s['date']]}`" for s in snapshots))
    w("")
    return "\n".join(out)


def write_digest(data: dict, path: Path, tags: list[str] | None = None, every: int = 12) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(digest(data, tags, every), encoding="utf-8", newline="\n")
    return path
