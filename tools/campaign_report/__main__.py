"""python -m tools.campaign_report list|build|render|digest --help"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import DEFAULT_TAGS, SCHEMA_VERSION
from .cache import atomic_json, dependency_digest, extract_job
from .campaign import REPO, date_key, discover, read_manifest, select, summarize
from .convoys import CUMULATIVE_METRIC, enrich_cumulative_losses
from .digest import write_digest
from .render import presentation, write_report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Offline World Ablaze campaign report (HTML, JSON, Markdown digest); no LLM involved.")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("list", "build"):
        cmd = sub.add_parser(name, help="List campaigns" if name == "list" else "Extract the saves and generate the report")
        cmd.add_argument("--saves", type=Path, nargs="+", help="Save folders or files; the HOI4 save folder by default")
        cmd.add_argument("--recursive", action="store_true", help="Also search sub-folders")
        cmd.add_argument("--manifest", type=Path, help="Explicit JSON list of the files of one branch")
        if name == "list":
            cmd.add_argument("--json", action="store_true")
            continue
        cmd.add_argument("--campaign", help="Full campaign identity or a unique prefix")
        cmd.add_argument("--output", type=Path, default=REPO / "tools/campaign_report/output/campaign.html")
        cmd.add_argument("--cache", type=Path, default=REPO / ".cache/campaign_report")
        cmd.add_argument("--refresh", action="store_true", help="Re-extract even when a cache entry exists")
        cmd.add_argument("--workers", type=int, default=2, help="Concurrent save readers (1 to 8, default 2)")
        cmd.add_argument("--allow-ambiguous-timeline", action="store_true",
                         help="Explicitly accept session-order reversals (does not resolve same-date duplicates)")
        cmd.add_argument("--from", dest="start", help="First extracted date, YYYY.MM.DD")
        cmd.add_argument("--to", dest="end", help="Last extracted date, YYYY.MM.DD")
        cmd.add_argument("--title", default="World Ablaze · Campaign overview")
        cmd.add_argument("--digest-tags", help="Countries of the Markdown digest (comma-separated; default: the seven majors)")
        cmd.add_argument("--digest-every", type=int, default=12, help="Digest sampling step in months (default 12)")
    cmd = sub.add_parser("render", help="Re-render the HTML from the JSON without reading the saves")
    cmd.add_argument("data", type=Path)
    cmd.add_argument("--output", type=Path, required=True)
    cmd = sub.add_parser("digest", help="Write the Markdown digest (agent view) from the JSON without reading the saves")
    cmd.add_argument("data", type=Path)
    cmd.add_argument("--output", type=Path, help="Default: <data>_digest.md next to the JSON")
    cmd.add_argument("--tags", help="Countries, comma-separated (default: the seven majors)")
    cmd.add_argument("--every", type=int, default=12, help="Sampling step in months (default 12)")
    return p


def split_tags(value: str | None) -> list[str] | None:
    return [t.strip().upper() for t in value.split(",") if t.strip()] if value else None


def digest_path(output: Path) -> Path:
    return output.with_name(f"{output.stem}_digest.md")


def run(args) -> None:
    if args.command in {"render", "build"} and args.output.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("--output must end in .html or .htm.")
    if args.command == "render":
        data = json.loads(args.data.read_text(encoding="utf-8"))
        if data.get("schema_version") != SCHEMA_VERSION or not data.get("snapshots"):
            raise ValueError("Incompatible JSON or no observations.")
        write_report(data, args.output)
        print(f"HTML: {args.output.resolve()}")
        return
    if args.command == "digest":
        data = json.loads(args.data.read_text(encoding="utf-8"))
        if data.get("schema_version") != SCHEMA_VERSION or not data.get("snapshots"):
            raise ValueError("Incompatible JSON or no observations.")
        target = write_digest(data, args.output or digest_path(args.data), split_tags(args.tags), args.every)
        print(f"DIGEST: {target.resolve()} ({target.stat().st_size / 1000:.1f} kB)")
        return
    paths = read_manifest(args.manifest) if args.manifest else args.saves
    paths = paths or [Path.home() / "Documents/Paradox Interactive/Hearts of Iron IV/save games"]
    entries, skipped = discover(paths, args.recursive)
    if args.command == "list":
        groups = summarize(entries)
        if args.json:
            print(json.dumps({"campaigns": groups, "skipped": skipped}, ensure_ascii=False, indent=2))
        else:
            for row in groups:
                print(f"{row['id']}  {row['count']} saves  {row['start']} — {row['end']}  {'; '.join(row['mods'])}")
            for warning in skipped:
                print(f"SKIPPED: {warning}", file=sys.stderr)
        return
    if skipped and args.manifest:
        raise ValueError("The manifest lists unreadable files: " + "; ".join(skipped))
    selected, warnings = select(entries, args.campaign, explicit_manifest=bool(args.manifest),
                                allow_ambiguous=args.allow_ambiguous_timeline)
    if args.start:
        selected = [r for r in selected if date_key(r["date"]) >= date_key(args.start)]
    if args.end:
        selected = [r for r in selected if date_key(r["date"]) <= date_key(args.end + (".23" if args.end.count(".") == 2 else ""))]
    if not selected:
        raise ValueError("No save in the requested period.")
    if not 1 <= args.workers <= 8:
        raise ValueError("--workers must be between 1 and 8.")
    from .extract import METRICS
    begin = time.perf_counter()
    dependencies = dependency_digest(REPO)
    snapshots, inputs, hits = [], [], 0
    jobs = [(Path(m["file"]), args.cache, dependencies, args.refresh) for m in selected]
    pool = ProcessPoolExecutor(max_workers=args.workers) if args.workers > 1 else None
    try:
        results = pool.map(extract_job, jobs) if pool else map(extract_job, jobs)
        for i, (meta, (item, hit, sha256)) in enumerate(zip(selected, results), 1):
            path = Path(meta["file"])
            if date_key(item["date"]) != date_key(meta["date"]):
                raise ValueError(f"Extracted date inconsistent with the header in {path.name}.")
            # Source filename belongs to this run (identical content may be cached under another name).
            item = {**item, "file": path.name}
            snapshots.append(item)
            inputs.append({"file": path.name, "sha256": sha256, "date": meta["date"],
                           "session": meta.get("session"), "version": meta.get("version"), "mods": meta.get("mods")})
            hits += hit
            print(f"[{i}/{len(selected)}] {meta['date']} · {'cache' if hit else 'extracted'} · {len(item['countries'])} countries", flush=True)
    finally:
        if pool:
            pool.shutdown(wait=True, cancel_futures=True)
    enrich_cumulative_losses(snapshots)  # campaign-wide derivation, after the per-save cache
    if dependency_digest(REPO) != dependencies:
        raise ValueError("The extractors or the mod definitions changed during the build. Run again for a consistent reading.")
    warnings.extend(f"Skipped file: {x}" for x in skipped)
    if len(snapshots) == 1:
        warnings.append("Only one save: a snapshot is available, but change over time cannot be measured.")
    warnings.append("Classifications use local mod definitions at extraction time; each save's exact historical mod revision is not certified.")
    data = {"schema_version": SCHEMA_VERSION, "title": args.title,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "campaign": {"id": selected[0]["game_unique_id"], "start": snapshots[0]["date"],
                         "end": snapshots[-1]["date"], "count": len(snapshots),
                         "selection": "manifest" if args.manifest else "campaign"},
            "default_tags": list(DEFAULT_TAGS), "metric_catalog": {**METRICS, **CUMULATIVE_METRIC},
            "dependencies_sha256": dependencies, "inputs": inputs,
            "warnings": warnings, "snapshots": snapshots,
            "build": {"seconds": round(time.perf_counter() - begin, 2), "cache_hits": hits}}
    json_path = args.output.with_suffix(".json")
    if json_path.resolve() == args.output.resolve():
        raise ValueError("--output must name an HTML file, not the JSON.")
    data = presentation(data)
    atomic_json(json_path, data)
    write_report(data, args.output)
    md_path = write_digest(data, digest_path(args.output), split_tags(args.digest_tags), args.digest_every)
    print(f"HTML: {args.output.resolve()}\nJSON: {json_path.resolve()}\nDIGEST: {md_path.resolve()}\n"
          f"Duration: {data['build']['seconds']} s · cache: {hits}/{len(selected)} · "
          f"HTML: {args.output.stat().st_size / 1_000_000:.1f} MB")


def main(argv=None) -> int:
    try:
        run(parser().parse_args(argv))
        return 0
    except (ValueError, OSError, KeyError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
