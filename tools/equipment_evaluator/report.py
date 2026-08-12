"""
Report writers.

Two outputs, both under `tools/equipment_evaluator/output/`:

* `air_equipment_transitions.csv` - one row per country/role/transition with
  every computed number and the verdict. Machine-readable input for phase 3.
* `air_equipment_report.md`       - the human review surface: KEEP_OLD,
  SWITCH_REDESIGNED (with module lists), SWITCH_CONDITIONAL (with resource
  deltas), and the full diagnostics.

Nothing here writes into mod content directories.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .config import Config
from .decide import (KEEP_OLD, PARALLEL_VARIANT, REPORT_STATS, SWITCH,
                     SWITCH_CONDITIONAL, SWITCH_REDESIGNED, UNRESOLVED,
                     Transition)
from .diagnostics import ERROR, INFO, WARN, Diagnostics

VERDICT_ORDER = (KEEP_OLD, SWITCH_REDESIGNED, SWITCH_CONDITIONAL, SWITCH,
                 PARALLEL_VARIANT, UNRESOLVED)


def _fmt(v: float) -> str:
    return f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def _res_str(d: Dict[str, float]) -> str:
    return ";".join(f"{k}={_fmt(v)}" for k, v in sorted(d.items()) if abs(v) > 1e-9)


def write_csv(path: Path, transitions: List[Transition], cfg: Config) -> None:
    resources = [r for r in cfg.raw.get("resource_significance", {}) if r != "default"]
    resources.sort()

    header = [
        "country", "group", "role", "mission",
        "from_design", "from_label", "from_airframe", "from_year",
        "to_design", "to_label", "to_airframe", "to_year",
        "verdict",
        "range_old_km", "range_new_km", "range_target_km", "range_gate",
        "ic_old", "ic_new", "ic_delta",
        "weighted_gain",
        "efficiency_relation", "efficiency_retention", "efficiency_original_verdict",
    ]
    header += [f"{s}_old" for s in REPORT_STATS]
    header += [f"{s}_new" for s in REPORT_STATS]
    header += [f"res_{r}_old" for r in resources]
    header += [f"res_{r}_new" for r in resources]
    header += [f"res_{r}_delta" for r in resources]
    header += [
        "res_old_all", "res_new_all", "res_delta_all", "res_significant",
        "redesign_changes", "redesign_range_km", "redesign_gain_vs_old",
        "redesign_gain_vs_new", "redesign_ic", "redesign_res_delta",
        "flags", "notes",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for t in transitions:
            row = [
                t.country, t.group, t.role, t.mission,
                t.from_design, t.from_label, t.from_airframe,
                t.from_year if t.from_year is not None else "",
                t.to_design, t.to_label, t.to_airframe,
                t.to_year if t.to_year is not None else "",
                t.verdict,
                _fmt(t.range_old), _fmt(t.range_new), _fmt(t.range_target), t.range_gate,
                _fmt(t.ic_old), _fmt(t.ic_new), _fmt(t.ic_new - t.ic_old),
                _fmt(t.gain),
                t.efficiency_relation, _fmt(t.efficiency_retention),
                t.efficiency_original_verdict,
            ]
            row += [_fmt(t.old_stats.get(s, 0.0)) for s in REPORT_STATS]
            row += [_fmt(t.new_stats.get(s, 0.0)) for s in REPORT_STATS]
            row += [_fmt(t.res_old.get(r, 0.0)) for r in resources]
            row += [_fmt(t.res_new.get(r, 0.0)) for r in resources]
            row += [_fmt(t.res_delta.get(r, 0.0)) for r in resources]
            rd = t.redesign
            row += [
                _res_str(t.res_old), _res_str(t.res_new), _res_str(t.res_delta),
                _res_str(t.res_significant),
                rd.change_str() if rd else "",
                _fmt(rd.stats.range_km) if rd else "",
                _fmt(rd.gain_vs_old) if rd else "",
                _fmt(rd.gain_vs_new) if rd else "",
                _fmt(rd.stats.cost_ic) if rd else "",
                _res_str({k: rd.stats.resources.get(k, 0.0) - t.res_old.get(k, 0.0)
                          for k in set(rd.stats.resources) | set(t.res_old)}) if rd else "",
                "|".join(t.flags),
                " | ".join(t.notes),
            ]
            w.writerow(row)


def write_data_audit(path: Path, findings: List) -> None:
    """Data-integrity findings about the MOD (see `data_audit.py`)."""
    by_kind: Dict[str, List] = defaultdict(list)
    for f in findings:
        by_kind[f.kind].append(f)

    TITLES = {
        "count_limit": "Designs that mount more of a module than their airframe permits",
        "slot_category": "Designs that put a module in a slot whose category list excludes it",
        "chain_order": "Design chains that run backwards in airframe year",
    }

    L: List[str] = []
    L.append("# `ai_equipment` data-integrity audit")
    L.append("")

    L.append(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by "
             f"`tools/equipment_evaluator`. Findings about the MOD, not about switching._")
    L.append("")
    L.append("A `target_variant` that names a module its airframe cannot mount, or in a count "
             "the airframe caps below, **cannot be matched by the in-game designer** - so the AI "
             "silently never builds that design and the group behaves as if the generation were "
             "missing. That is worth more than any switching verdict.")
    L.append("")
    L.append("> **Verify before acting.** `module_count_limit` override semantics are inferred "
             "from the data (a `count = any` declaration is only meaningful as an override, and "
             "the Fix 47 annotation in `SOV_planes.txt` reads it that way), **not** confirmed "
             "in-game. Spot-check one finding before working the whole list.")
    L.append("")
    L += _table([[k, str(len(v))] for k, v in sorted(by_kind.items(), key=lambda kv: -len(kv[1]))],
                ["finding", "count"])
    L.append("")

    for kind in ("count_limit", "slot_category", "chain_order"):
        rows_src = by_kind.get(kind, [])
        L.append(f"## {TITLES.get(kind, kind)} — {len(rows_src)}")
        L.append("")
        if not rows_src:
            L.append("_None._")
            L.append("")
            continue
        rows = [[f.country, f"`{f.group}`", f"`{f.design}`", f"`{f.airframe}`",
                 f.detail, f.suggestion] for f in rows_src]
        L += _table(rows, ["country", "group", "design", "airframe", "problem", "suggested fix"])
        L.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def write_emit_patch(path: Path, patches: List, blocked: List, meta: Dict[str, object]) -> None:
    """The reviewable patch document for `--emit`. Writes nothing into `common/`."""
    by_file: Dict[str, List] = defaultdict(list)
    for p in patches:
        by_file[p.file].append(p)

    kinds = Counter(p.kind for p in patches)
    L: List[str] = []
    L.append("# Proposed `ai_equipment` patches")
    L.append("")
    L.append(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by "
             f"`tools/equipment_evaluator --emit`. **Nothing under `common/` was modified.**_")
    L.append("")
    L.append(f"- Patches: **{len(patches)}** across {len(by_file)} file(s)  ")
    L.append(f"- By kind: " + ", ".join(f"`{k}` {v}" for k, v in sorted(kinds.items())) + "  ")
    L.append(f"- Blocked (reported, never silently dropped): **{len(blocked)}**  ")
    L.append("")
    L.append("Each patch is an anchored replacement of an existing block, quoted exactly as the "
             "file has it. Apply order within a file matters: apply from the bottom up, or "
             "re-index between edits, because earlier insertions shift later line numbers.")
    L.append("")

    for fname in sorted(by_file):
        ps = sorted(by_file[fname], key=lambda p: -p.anchor_line)
        L.append(f"## `common/ai_equipment/{fname}` — {len(ps)} patch(es)")
        L.append("")
        for p in ps:
            L.append(f"### `{p.group}` / `{p.design}` — {p.kind} "
                     f"(line {p.anchor_line}, {p.n_added:+d} lines)")
            L.append("")
            for r in p.rationale:
                L.append(f"- {r}")
            L.append("")
            L.append("Before:")
            L.append("")
            L.append("```")
            L.append(p.original)
            L.append("```")
            L.append("")
            L.append("After:")
            L.append("")
            L.append("```")
            L.append(p.replacement)
            L.append("```")
            L.append("")

    L.append("## Blocked — needs a decision before it can be emitted")
    L.append("")
    if not blocked:
        L.append("_None._")
    else:
        rows = [[b.country, b.group, b.transition, b.reason] for b in blocked]
        L += _table(rows, ["country", "group", "transition", "why it was not emitted"])
    L.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def _table(rows: List[List[str]], header: List[str]) -> List[str]:
    out = ["| " + " | ".join(header) + " |",
           "| " + " | ".join("---" for _ in header) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return out


def write_markdown(path: Path, transitions: List[Transition], diag: Diagnostics,
                   cfg: Config, meta: Dict[str, object]) -> None:
    by_verdict: Dict[str, List[Transition]] = defaultdict(list)
    for t in transitions:
        by_verdict[t.verdict].append(t)

    per_country: Dict[str, Counter] = defaultdict(Counter)
    for t in transitions:
        per_country[t.country][t.verdict] += 1

    L: List[str] = []
    L.append("# WA air equipment transition report")
    L.append("")
    L.append(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by "
             f"`tools/equipment_evaluator` (report-only; no mod file was modified)._")
    L.append("")
    L.append(f"- Config: `{cfg.path.name}`  ")
    L.append(f"- Mod root: `{meta.get('mod_root')}`  ")
    L.append(f"- Countries: {meta.get('country_count')} "
             f"({', '.join(meta.get('countries', []))})  ")
    L.append(f"- Design groups: {meta.get('group_count')}  |  Designs: {meta.get('design_count')}"
             f"  |  Transitions: {len(transitions)}  ")
    L.append(f"- Airframes parsed: {meta.get('airframe_count')}  |  "
             f"Plane modules parsed: {meta.get('module_count')}  ")
    L.append(f"- Diagnostics: {diag.error_count} error(s), {diag.warn_count} warning(s)  ")
    L.append("")

    L.append("## Verdict summary")
    L.append("")
    counts = Counter(t.verdict for t in transitions)
    L += _table([[v, str(counts.get(v, 0))] for v in VERDICT_ORDER], ["verdict", "count"])
    L.append("")

    L.append("### Per country")
    L.append("")
    rows = []
    for country in sorted(per_country):
        c = per_country[country]
        rows.append([country] + [str(c.get(v, 0)) for v in VERDICT_ORDER]
                    + [str(sum(c.values()))])
    L += _table(rows, ["country"] + list(VERDICT_ORDER) + ["total"])
    L.append("")

    # ---------------------------------------------------------------- KEEP_OLD
    L.append("## KEEP_OLD - the new generation is a regression")
    L.append("")
    keep = by_verdict.get(KEEP_OLD, [])
    if not keep:
        L.append("_None._")
    else:
        rows = []
        for t in sorted(keep, key=lambda x: (x.country, x.role, x.group, x.to_design)):
            rows.append([
                t.country, t.role, f"{t.from_design} -> {t.to_design}",
                f"{t.from_label} -> {t.to_label}".strip(" ->"),
                f"{t.range_old:.0f} -> {t.range_new:.0f}",
                f"{t.range_target:.0f}",
                f"{t.gain:+.3f}",
                " | ".join(t.notes),
            ])
        L += _table(rows, ["country", "role", "transition", "aircraft", "range km",
                           "target", "gain", "why"])
    L.append("")

    # -------------------------------------------------------- SWITCH_REDESIGNED
    L.append("## SWITCH_REDESIGNED - adopt, but with a modified loadout")
    L.append("")
    red = by_verdict.get(SWITCH_REDESIGNED, [])
    if not red:
        L.append("_None._")
    else:
        for t in sorted(red, key=lambda x: (x.country, x.role, x.group, x.to_design)):
            rd = t.redesign
            L.append(f"### {t.country} / {t.role} / `{t.group}` : "
                     f"`{t.from_design}` -> `{t.to_design}`"
                     + (f"  ({t.from_label} -> {t.to_label})" if t.to_label else ""))
            L.append("")
            L.append(f"- Airframe: `{t.to_airframe}`"
                     + (f" (year {t.to_year})" if t.to_year else ""))
            L.append(f"- Range: default design **{t.range_new:.0f} km** "
                     f"(target {t.range_target:.0f}, old gen {t.range_old:.0f}) "
                     f"-> redesigned **{rd.stats.range_km:.0f} km**")
            L.append(f"- Weighted gain: new default vs old `{t.gain:+.3f}`; "
                     f"redesigned vs old `{rd.gain_vs_old:+.3f}`; "
                     f"redesigned vs new default `{rd.gain_vs_new:+.3f}`")
            L.append(f"- IC: {t.ic_old:.2f} -> {t.ic_new:.2f} "
                     f"(redesigned {rd.stats.cost_ic:.2f})")
            L.append("- Module changes vs the scripted `target_variant`:")
            for slot, a, b in rd.changes:
                L.append(f"  - `{slot}`: `{a or 'empty'}` -> `{b or 'empty'}`")
            L.append("- Full redesigned loadout:")
            for slot, mod in sorted(rd.modules.items()):
                L.append(f"  - `{slot} = {mod}`")
            delta = {k: rd.stats.resources.get(k, 0.0) - t.res_old.get(k, 0.0)
                     for k in set(rd.stats.resources) | set(t.res_old)}
            delta = {k: v for k, v in delta.items() if abs(v) > 1e-9}
            if delta:
                L.append("- Resource delta vs old generation: "
                         + ", ".join(f"`{k} {v:+.2f}`" for k, v in sorted(delta.items())))
            if t.flags:
                L.append(f"- Flags: `{'`, `'.join(t.flags)}`")
            L.append("")
    L.append("")

    # ------------------------------------------------------- SWITCH_CONDITIONAL
    L.append("## SWITCH_CONDITIONAL - better, but resource-significant")
    L.append("")
    cond = by_verdict.get(SWITCH_CONDITIONAL, [])
    if not cond:
        L.append("_None._")
    else:
        rows = []
        for t in sorted(cond, key=lambda x: (x.country, x.role, x.group, x.to_design)):
            rows.append([
                t.country, t.role, f"{t.from_design} -> {t.to_design}",
                f"{t.from_label} -> {t.to_label}".strip(" ->"),
                ", ".join(f"{k} +{v:.2f}" for k, v in sorted(t.res_significant.items())),
                _res_str(t.res_delta),
                f"{t.gain:+.3f}",
                f"{t.ic_old:.1f} -> {t.ic_new:.1f}",
                f"{t.range_new:.0f}",
            ])
        L += _table(rows, ["country", "role", "transition", "aircraft",
                           "significant resource delta / unit", "all resource deltas",
                           "gain", "IC", "range km"])
    L.append("")

    # -------------------------------------------------------- PARALLEL_VARIANT
    L.append("## PARALLEL_VARIANT - not a generation step")
    L.append("")
    L.append("_These pairs are adjacent in file order but are not a supersession: "
             "either both designs sit on the same airframe (sibling loadouts for "
             "different jobs), or the chain crosses two parallel families inside one "
             "design group. Numbers are published for reference; no switch decision "
             "applies._")
    L.append("")
    par = by_verdict.get(PARALLEL_VARIANT, [])
    if not par:
        L.append("_None._")
    else:
        rows = []
        for t in sorted(par, key=lambda x: (x.country, x.role, x.group, x.to_design)):
            rows.append([
                t.country, t.role, f"{t.from_design} -> {t.to_design}",
                f"{t.from_airframe} -> {t.to_airframe}",
                f"{t.from_year or '?'} -> {t.to_year or '?'}",
                f"{t.range_old:.0f} -> {t.range_new:.0f}",
                f"{t.gain:+.3f}",
                "|".join(t.flags),
            ])
        L += _table(rows, ["country", "role", "designs", "airframes", "year",
                           "range km", "gain", "why"])
    L.append("")

    # ---------------------------------------------------- chain order warnings
    inverted = [t for t in transitions if "chain_order_inversion" in t.flags]
    L.append("### Chain-order inversions still treated as real transitions")
    L.append("")
    L.append("_Same design family, but the airframe year runs backwards. These are "
             "genuine transitions in a suspicious order - worth checking the design "
             "order in `common/ai_equipment/`._")
    L.append("")
    if not inverted:
        L.append("_None._")
    else:
        rows = []
        for t in sorted(inverted, key=lambda x: (x.country, x.role, x.group, x.to_design)):
            rows.append([t.country, t.role, t.group,
                         f"{t.from_design} -> {t.to_design}",
                         f"{t.from_airframe} ({t.from_year}) -> "
                         f"{t.to_airframe} ({t.to_year})",
                         t.verdict])
        L += _table(rows, ["country", "role", "group", "designs", "airframes", "verdict"])
    L.append("")

    # ------------------------------------------------------------- UNRESOLVED
    unres = by_verdict.get(UNRESOLVED, [])
    L.append("## UNRESOLVED - the tool could not compute these")
    L.append("")
    if not unres:
        L.append("_None._")
    else:
        rows = []
        for t in sorted(unres, key=lambda x: (x.country, x.group, x.to_design)):
            rows.append([t.country, t.role, f"{t.from_design} -> {t.to_design}",
                         t.from_airframe, t.to_airframe, "|".join(t.flags)])
        L += _table(rows, ["country", "role", "transition", "from airframe",
                           "to airframe", "flags"])
    L.append("")

    # ------------------------------------------------------------ diagnostics
    L.append("## Diagnostics")
    L.append("")
    kinds = diag.by_kind()
    if kinds:
        L += _table([[k, str(v)] for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])],
                    ["kind", "count"])
    else:
        L.append("_Clean run - nothing unresolved._")
    L.append("")
    for severity, title in ((ERROR, "Errors"), (WARN, "Warnings"), (INFO, "Notes")):
        issues = diag.filtered(severity)
        if not issues:
            continue
        L.append(f"### {title} ({len(issues)})")
        L.append("")
        shown = issues[:400]
        L += _table([[i.kind, i.where, i.detail] for i in shown],
                    ["kind", "where", "detail"])
        if len(issues) > len(shown):
            L.append("")
            L.append(f"_...and {len(issues) - len(shown)} more (see CSV `flags` column)._")
        L.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
