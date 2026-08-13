"""
CLI entry point for the World Ablaze equipment evaluator.

Run from `tools/`:

    python -m equipment_evaluator --all
    python -m equipment_evaluator --countries SOV,ENG
    python -m equipment_evaluator --countries SOV --roles air_fighter_mr -v

REPORT-ONLY BY DESIGN: this version never writes into `common/` or any other
mod content directory. Its output is a decision report under
`tools/equipment_evaluator/output/`. Generation of `ai_equipment` priority
blocks is phase 3, after an in-game pilot validates the model.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List

if __package__ in (None, ""):  # allow `python equipment_evaluator/__main__.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = "equipment_evaluator"

from equipment_evaluator import __version__
from equipment_evaluator.config import DEFAULT_CONFIG_PATH, load_config
from equipment_evaluator.decide import (SWITCH, SWITCH_CONDITIONAL,
                                        SWITCH_REDESIGNED, Evaluator, Transition)
from equipment_evaluator.decision_policy import apply_efficiency_gate
from equipment_evaluator.decision_manifest import (build_manifest,
                                                    write_encodability_report,
                                                    write_manifest)
from equipment_evaluator.diagnostics import Diagnostics
from equipment_evaluator.parse_ai_equipment import (DesignGroup, discover_countries,
                                                    parse_country_file)
from equipment_evaluator.parse_equipment import EquipmentDB, find_files
from equipment_evaluator.emit import Emitter
from equipment_evaluator.generation.production_strategy import (
    emit as production_strategy_emit,
    emit_linear as production_strategy_emit_linear)


def _gates_for(significant, cfg) -> list:
    """Runtime gate symbols for a significant-resource-increase mapping."""
    from equipment_evaluator.emit import _gate_for
    gates = []
    for resource, delta in sorted((significant or {}).items()):
        gate = _gate_for(resource, delta)
        if gate and gate not in gates:
            gates.append(gate)
    return gates


def _linear_rows(kind, rows, cfg) -> list:
    """Normalise the three unrelated transition dataclasses onto one shape.

    Air carries `from_airframe`/`to_airframe`; artillery/vehicles carry raw
    equipment token names in `old`/`new`; infantry carries `LandEquipment`
    objects and - unlike the other two - throws its significant-resource
    mapping away (infantry.py:247), so it is recomputed here from
    `resource_delta`.
    """
    from equipment_evaluator.decision_policy import significant_increases
    out = []
    for t in rows:
        if kind == "air":
            old_tok, new_tok = t.from_airframe, t.to_airframe
            old_lab, new_lab = t.from_label, t.to_label
            group, significant = t.role, t.res_significant
        elif kind == "infantry":
            old_tok, new_tok = t.old.name, t.new.name
            old_lab, new_lab = t.old.name, t.new.name
            group = t.technology_file
            significant = significant_increases(
                t.resource_delta, cfg.resource_threshold)
        else:                                   # artillery / vehicles
            old_tok, new_tok = t.old, t.new
            old_lab, new_lab = t.old, t.new
            group, significant = t.role, t.significant_resources
        if not old_tok or not new_tok:
            continue
        out.append({
            "country": t.country, "group": group,
            "old": old_tok, "new": new_tok,
            "old_label": old_lab, "new_label": new_lab,
            "verdict": t.verdict,
            "gates": (_gates_for(significant, cfg)
                      if t.verdict == "SWITCH_CONDITIONAL" else []),
            "reason": "; ".join(getattr(t, "notes", []) or [])[:160],
        })
    return out


def emit_production_strategy(args, mod_root, out_dir, tank_frontiers) -> None:
    """Render (and optionally write) the production-line strategy files."""
    if not tank_frontiers:
        print("\nProduction strategy: no branched tank frontiers evaluated "
              "(need --domain tanks or all).")
        return
    files, skipped = production_strategy_emit(
        str(mod_root), tank_frontiers, apply=args.apply_production_strategy)
    preview_dir = out_dir / "production_strategy"
    preview_dir.mkdir(parents=True, exist_ok=True)
    for rel, text in sorted(files.items()):
        (preview_dir / Path(rel).name).write_text(text, encoding="utf-8")
    verb = "WROTE into common/" if args.apply_production_strategy else "DRY RUN"
    entries = sum(text.count("ai_strategy = {") for text in files.values())
    print(f"\nProduction strategy ({verb}): {len(files)} file(s), "
          f"{entries} ai_strategy entries")
    for rel in sorted(files):
        print(f"  {rel}")
    print(f"  Preview               : {preview_dir}")
    if skipped:
        print(f"  Unreachable ranks ({len(skipped)}) - reported, not emitted:")
        for note in skipped:
            print(f"    - {note}")


def emit_linear_strategy(args, mod_root, out_dir, cfg, kind, rows) -> None:
    """Emit the KEEP_OLD / SWITCH_CONDITIONAL suppressions of a linear domain."""
    if not args.emit_production_strategy and not args.apply_production_strategy:
        return
    normalised = _linear_rows(kind, rows, cfg)
    if not normalised:
        return
    files, skipped = production_strategy_emit_linear(
        str(mod_root), kind, normalised, apply=args.apply_production_strategy)
    preview_dir = out_dir / "production_strategy"
    preview_dir.mkdir(parents=True, exist_ok=True)
    for rel, text in sorted(files.items()):
        (preview_dir / Path(rel).name).write_text(text, encoding="utf-8")
    verb = "WROTE into common/" if args.apply_production_strategy else "DRY RUN"
    entries = sum(text.count("ai_strategy = {") for text in files.values())
    considered = len(normalised)
    print(f"\nProduction strategy - {kind} ({verb}): {len(files)} file(s), "
          f"{entries} suppressions out of {considered} transitions")
    for rel in sorted(files):
        print(f"  {rel}")
    if skipped:
        print(f"  Not suppressed ({len(skipped)}): a plain SWITCH also reaches "
              f"the successor, or a duplicate step")
from equipment_evaluator.efficiency_audit import (evaluate_efficiency_domains,
                                                  write_efficiency_audit)
from equipment_evaluator.infantry import evaluate_infantry, write_infantry_reports
from equipment_evaluator.ground import (TankEvaluator, evaluate_tech_ground,
                                        write_coverage_audit,
                                        write_ground_reports)
from equipment_evaluator.generation import (PLAN_SCOPES, apply_plan, build_plan,
                                            load_plan, select_patches,
                                            tank_emitter_transition, verify_plan,
                                            write_plan)
from equipment_evaluator.data_audit import audit as data_audit
from equipment_evaluator.report import (write_csv, write_data_audit, write_emit_patch,
                                        write_markdown)
from equipment_evaluator.stats import StatModel
from equipment_evaluator.technology_graph import TechnologyGraph

# tools/equipment_evaluator/__main__.py -> tools/ -> <mod root>
DEFAULT_MOD_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m equipment_evaluator",
        description=(
            "Offline evaluator and idempotent code-plan generator for World Ablaze "
            "equipment. It evaluates air, tanks, infantry, artillery and vehicles "
            "with shared efficiency/resource policy and domain-specific stats."
        ),
        epilog=(
            "Dry-run is the default. --generate-plan writes a reviewable operation "
            "plan; only --apply-plan may modify mod files.\n\n"
            "Examples:\n"
            "  python -m equipment_evaluator --all\n"
            "  python -m equipment_evaluator --countries SOV,ENG\n"
            "  python -m equipment_evaluator --countries SOV --roles air_fighter_mr -v\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--countries", metavar="TAGS",
                   help="Comma-separated country tags, e.g. SOV,ENG,USA")
    p.add_argument("--all", action="store_true",
                   help="Evaluate every discoverable country in the selected domain")
    p.add_argument("--domain",
                   choices=("air", "tanks", "infantry", "artillery", "vehicles", "all"),
                   default="air",
                   help="Equipment domain (default: air). Every domain applies the shared "
                        "production-efficiency retention policy; all runs all five.")
    p.add_argument("--roles", metavar="ROLES",
                   help="Comma-separated air roles to restrict to, e.g. air_fighter,air_cas")
    p.add_argument("--groups", metavar="NAMES",
                   help="Comma-separated design-group names to restrict to")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH,
                   help=f"Config JSON (default: {DEFAULT_CONFIG_PATH.name})")
    p.add_argument("--mod-root", type=Path, default=DEFAULT_MOD_ROOT,
                   help="Mod root directory (default: auto-detected from this file)")
    p.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
                   help="Where to write the report (default: <package>/output)")
    p.add_argument("--no-redesign", action="store_true",
                   help="Skip the range-restoring module search (faster, more KEEP_OLD)")
    p.add_argument("--emit", action="store_true",
                   help="Also write a reviewable ai_equipment patch document to "
                        "<output>/emit_ai_equipment.md. DRY RUN - still writes "
                        "nothing into common/.")
    p.add_argument("--emit-production-strategy", action="store_true",
                   help="Render the branched tank roles as ai_strategy "
                        "`production_upgrade_desire_offset` files "
                        "(common/ai_strategy/WA_AI_PRODUCTION_COUNTRY_<TAG>_TANKS.txt) "
                        "into <output>/production_strategy/. DRY RUN - writes "
                        "nothing into common/ unless --apply-production-strategy.")
    p.add_argument("--apply-production-strategy", action="store_true",
                   help="Write the files rendered by --emit-production-strategy "
                        "into common/ai_strategy/. Modifies mod files.")
    p.add_argument("--generate-plan", action="store_true",
                   help="Write deterministic decision manifest and operation plan. "
                        "Requires --domain all; does not modify common/.")
    p.add_argument("--plan-scope", choices=PLAN_SCOPES, default="all",
                   help="Operation-plan scope (default: all). `tank-frontiers` "
                        "contains only complete branched tank-role selectors.")
    p.add_argument("--apply-plan", type=Path, metavar="PLAN",
                   help="Transactionally apply a previously reviewed JSON plan. "
                        "This is the only mode that modifies mod files.")
    p.add_argument("--verify-plan", type=Path, metavar="PLAN",
                   help="Verify that every operation from PLAN is already applied.")
    p.add_argument("--list-countries", action="store_true",
                   help="List discoverable country tags and exit")
    p.add_argument("-v", "--verbose", action="store_true", help="Per-transition console output")
    p.add_argument("--version", action="version", version=f"equipment_evaluator {__version__}")
    return p


def main(argv: List[str] = None) -> int:
    args = build_parser().parse_args(argv)
    t0 = time.time()

    mod_root: Path = args.mod_root.resolve()
    if not (mod_root / "descriptor.mod").exists():
        print(f"WARNING: {mod_root} does not look like the mod root "
              f"(no descriptor.mod); continuing anyway.", file=sys.stderr)

    if args.apply_plan or args.verify_plan:
        plan_path = (args.apply_plan or args.verify_plan).resolve()
        try:
            plan = load_plan(plan_path)
            result = (apply_plan(mod_root, plan) if args.apply_plan
                      else verify_plan(mod_root, plan))
        except (OSError, ValueError) as exc:
            print(f"PLAN ERROR: {exc}", file=sys.stderr)
            return 2
        mode = "apply" if args.apply_plan else "verify"
        print(f"Generation plan {mode}: changed_files={len(result.changed_files)} "
              f"applied={len(result.applied_operations)} "
              f"already_applied={len(result.noop_operations)} "
              f"conflicts={len(result.conflicts)}")
        for conflict in result.conflicts:
            print(f"  CONFLICT: {conflict}", file=sys.stderr)
        return 0 if result.ok else 3

    if args.generate_plan and args.domain != "all":
        print("ERROR: --generate-plan currently requires --domain all so the manifest "
              "cannot silently omit an equipment domain.", file=sys.stderr)
        return 2
    if args.plan_scope != "all" and not args.generate_plan:
        print("ERROR: --plan-scope requires --generate-plan.", file=sys.stderr)
        return 2

    cfg = load_config(args.config)
    problems = cfg.validate()
    if problems:
        for pb in problems:
            print(f"CONFIG ERROR: {pb}", file=sys.stderr)
        return 2
    if args.no_redesign:
        cfg.raw.setdefault("redesign", {})["enabled"] = False

    selected = None
    if args.countries:
        selected = {c.strip().upper() for c in args.countries.split(",") if c.strip()}
    efficiency_domains = ({"air", "tanks", "infantry", "artillery", "vehicles"}
                          if args.domain == "all" else {args.domain})
    efficiency_rows = evaluate_efficiency_domains(mod_root, cfg, efficiency_domains, selected)
    out_dir: Path = args.output_dir.resolve()
    write_efficiency_audit(out_dir, efficiency_rows, cfg)
    efficiency_counts = Counter((r.domain, r.policy) for r in efficiency_rows)
    print("Production-efficiency retention audit:")
    for domain in sorted(efficiency_domains):
        safe = efficiency_counts.get((domain, "SWITCH_SAFE"), 0)
        review = efficiency_counts.get((domain, "LOW_RETENTION_REVIEW"), 0)
        print(f"  {domain:<10} safe={safe:<4} low-retention-review={review}")
    print(f"  Report                : {out_dir / 'production_efficiency_report.md'}")

    ground_rows = []
    infantry_rows = []
    tank_frontiers = []
    coverage_gaps = []
    if args.domain in ("tanks", "all"):
        tank_evaluator = TankEvaluator(mod_root, cfg)
        ground_rows += tank_evaluator.evaluate(selected)
        tank_frontiers = tank_evaluator.frontier_decisions
        coverage_gaps = tank_evaluator.coverage_gaps
    if args.domain in ("artillery", "all"):
        ground_rows += evaluate_tech_ground(
            mod_root, cfg, "artillery",
            ("*artillery_GENERATED.txt", "*anti_tank_GENERATED.txt", "*anti_air_GENERATED.txt"),
            ("artillery*.txt",),
            {"artillery_equipment", "heavy_artillery_equipment", "pack_artillery_equipment",
             "rocket_artillery_equipment", "anti_tank_equipment", "heavy_anti_tank_equipment",
             "anti_air_equipment", "heavy_anti_air_equipment"}, selected)
    if args.domain in ("vehicles", "all"):
        ground_rows += evaluate_tech_ground(
            mod_root, cfg, "vehicles", ("motorized.txt", "mechanized.txt"),
            ("armor*.txt",),
            {"motorized_equipment", "mechanized_equipment", "mechanized_td_equipment",
             "mechanized_artillery_equipment", "mechanized_aa_equipment",
             "amphibious_mechanized_equipment"}, selected)
    if ground_rows:
        write_ground_reports(out_dir, ground_rows, tank_frontiers)
        ground_counts = Counter((r.domain, r.verdict) for r in ground_rows)
        print("Integrated ground decisions (stats + efficiency + resources):")
        for domain in sorted({r.domain for r in ground_rows}):
            summary = ", ".join(f"{v}={n}" for (d, v), n in sorted(ground_counts.items()) if d == domain)
            print(f"  {domain:<10} {summary}")
        print(f"  Report                : {out_dir / 'ground_equipment_report.md'}")
        if tank_frontiers:
            print(f"  Parallel branches     : {out_dir / 'parallel_branch_decisions.md'}")
        if coverage_gaps:
            write_coverage_audit(out_dir, coverage_gaps)
            branched = [g for g in coverage_gaps if g.branched]
            print(f"  COVERAGE GAPS         : {len(coverage_gaps)} chassis researchable "
                  f"inside a role that no design describes "
                  f"({len(branched)} of them in a BRANCHED role)")
            for gap in branched[:12]:
                print(f"    - {gap.country}/{gap.group}: {gap.equipment} "
                      f"(unlocked by {gap.unlock_tech})")
            if len(branched) > 12:
                print(f"    ... and {len(branched) - 12} more")
            print(f"  Coverage report       : {out_dir / 'coverage_gaps.md'}")

    # Infantry is independent of ai_equipment design groups: technology file
    # order is the unlock chain and infantry.txt owns the parent/family links.
    if args.domain in ("infantry", "all"):
        infantry_rows = evaluate_infantry(mod_root, cfg, selected)
        write_infantry_reports(out_dir, infantry_rows, cfg)
        infantry_counts = Counter(t.verdict for t in infantry_rows)
        print("Infantry equipment (production-efficiency aware):")
        print(f"  transitions evaluated : {len(infantry_rows)}")
        for verdict in ("SWITCH", "SWITCH_CONDITIONAL", "KEEP_OLD"):
            print(f"  {verdict:<21} : {infantry_counts.get(verdict, 0)}")
        print(f"  CSV                   : {out_dir / 'infantry_equipment_transitions.csv'}")
        print(f"  Markdown              : {out_dir / 'infantry_equipment_report.md'}")
    # Every non-air domain is fully evaluated by this point, so the hook sits
    # ahead of BOTH early returns - `--domain infantry` and `--domain tanks`
    # are the cheap ways to regenerate one domain without a full air pass.
    # Air runs its own call further down, once `transitions` exists.
    if args.emit_production_strategy or args.apply_production_strategy:
        emit_production_strategy(args, mod_root, out_dir, tank_frontiers)
        for linear in ("artillery", "vehicles"):
            emit_linear_strategy(
                args, mod_root, out_dir, cfg, linear,
                [row for row in ground_rows if row.domain == linear])
        emit_linear_strategy(args, mod_root, out_dir, cfg,
                             "infantry", infantry_rows)

    if args.domain == "infantry":
        return 0

    if args.domain in ("tanks", "artillery", "vehicles"):
        return 0

    ai_dir = cfg.dir_for("ai_equipment_dir", mod_root)
    eq_dir = cfg.dir_for("equipment_dir", mod_root)
    mod_dir = cfg.dir_for("modules_dir", mod_root)
    for label, d in (("ai_equipment_dir", ai_dir), ("equipment_dir", eq_dir),
                     ("modules_dir", mod_dir)):
        if not d.is_dir():
            print(f"ERROR: {label} not found: {d}", file=sys.stderr)
            return 2

    available = discover_countries(ai_dir)
    if args.list_countries:
        print("Countries with a *_planes.txt design set:")
        for tag in available:
            print(f"  {tag}")
        return 0

    if args.all:
        countries = available
    elif args.countries:
        countries = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    else:
        print("ERROR: specify --countries TAGS or --all (or --list-countries).",
              file=sys.stderr)
        return 2

    unknown = [c for c in countries if c not in available]
    for c in unknown:
        print(f"ERROR: no {c}_planes.txt in {ai_dir}", file=sys.stderr)
    countries = [c for c in countries if c in available]
    if not countries:
        return 2

    role_filter = {r.strip() for r in args.roles.split(",")} if args.roles else None
    group_filter = {g.strip() for g in args.groups.split(",")} if args.groups else None

    diag = Diagnostics()

    # ---------------------------------------------------------------- parse
    print(f"Loading airframe definitions from {eq_dir} ...")
    db = EquipmentDB(diag)
    airframe_files = find_files(eq_dir, cfg.globs_for("airframe_globs"))
    if not airframe_files:
        print(f"ERROR: no airframe files matched {cfg.globs_for('airframe_globs')} in {eq_dir}",
              file=sys.stderr)
        return 2
    db.load_airframes(airframe_files)
    print(f"  {len(airframe_files)} file(s), {len(db.airframes)} airframe/archetype entries")

    print(f"Loading plane modules from {mod_dir} ...")
    module_files = find_files(mod_dir, cfg.globs_for("module_globs"))
    db.load_modules(module_files)
    print(f"  {len(module_files)} file(s), {len(db.modules)} modules")

    print(f"Loading AI design groups for: {', '.join(countries)}")
    groups_by_country: Dict[str, List[DesignGroup]] = {}
    for tag in countries:
        path = ai_dir / f"{tag}_planes.txt"
        groups = parse_country_file(path, tag, diag)
        groups_by_country[tag] = groups

    total_groups = sum(len(g) for g in groups_by_country.values())
    total_designs = sum(len(gr.designs) for gs in groups_by_country.values() for gr in gs)
    print(f"  {total_groups} air design group(s), {total_designs} design(s)")

    # --------------------------------------------------------------- evaluate
    model = StatModel(db, diag,
                      multiply_base_only=cfg.multiply_base_only,
                      thrust_weight_agility_factor=cfg.thrust_weight_agility_factor)
    evaluator = Evaluator(db, model, cfg, diag, TechnologyGraph(mod_root, diag))
    evaluator.build_availability(groups_by_country)

    transitions: List[Transition] = []
    for tag in countries:
        for group in groups_by_country[tag]:
            if group_filter and group.name not in group_filter:
                continue
            if role_filter and not (set(group.roles) & role_filter):
                continue
            group_transitions = evaluator.evaluate_group(group)
            transitions.extend(group_transitions)
            if args.verbose:
                for t in group_transitions:
                    print(f"  [{t.verdict:<18}] {t.country} {t.role:<22} "
                          f"{t.from_design} -> {t.to_design}  "
                          f"range {t.range_old:.0f} -> {t.range_new:.0f} km  "
                          f"gain {t.gain:+.3f}")

    # Domain scoring stays in Evaluator; adoption policy is shared by domains.
    efficiency_by_transition = {
        (r.country, r.group, r.old, r.new): r for r in efficiency_rows if r.domain == "air"
    }
    for t in transitions:
        erow = efficiency_by_transition.get((t.country, t.group, t.from_design, t.to_design))
        if not erow:
            continue
        t.efficiency_relation = erow.relation
        t.efficiency_retention = erow.retention
        gated = apply_efficiency_gate(
            t.verdict, t.gain, erow.retention, cfg.efficiency_model)
        if gated != t.verdict:
            t.efficiency_original_verdict = t.verdict
            t.verdict = gated
            t.notes.append(
                f"production efficiency: {erow.relation} retains only "
                f"{erow.retention:.0%} and gain {t.gain:+.3f} does not clear "
                f"the low-retention threshold {cfg.efficiency_model.low_retention_min_gain}")

    # ----------------------------------------------------------------- report
    out_dir: Path = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "air_equipment_transitions.csv"
    md_path = out_dir / "air_equipment_report.md"

    meta = {
        "mod_root": str(mod_root),
        "countries": countries,
        "country_count": len(countries),
        "group_count": total_groups,
        "design_count": total_designs,
        "airframe_count": len(db.airframes),
        "module_count": len(db.modules),
    }
    emit_linear_strategy(args, mod_root, out_dir, cfg, "air", transitions)

    write_csv(csv_path, transitions, cfg)
    write_markdown(md_path, transitions, diag, cfg, meta)

    data_findings = data_audit(db, groups_by_country)
    write_data_audit(out_dir / "data_integrity_audit.md", data_findings)

    emitted_patches = []
    emission_blocked = []
    if args.emit or args.generate_plan:
        air_emitter = Emitter(cfg, diag)
        air_emitter.run(transitions, groups_by_country, ai_dir)
        emitted_patches.extend(air_emitter.patches)
        emission_blocked.extend(air_emitter.blocked)

        tank_rows = [row for row in ground_rows if row.domain == "tanks"]
        tank_groups = {}
        for tag in sorted({row.country for row in tank_rows}):
            path = ai_dir / f"{tag}_tank.txt"
            if path.exists():
                tank_groups[tag] = parse_country_file(
                    path, tag, diag, category_filter="land")
        if tank_groups:
            tank_emitter = Emitter(cfg, diag, file_suffix="tank", domain="tanks")
            tank_emitter.run([tank_emitter_transition(row) for row in tank_rows],
                             tank_groups, ai_dir, tank_frontiers)
            emitted_patches.extend(tank_emitter.patches)
            emission_blocked.extend(tank_emitter.blocked)

        write_emit_patch(out_dir / "emit_ai_equipment.md",
                         emitted_patches, emission_blocked, meta)

    if args.generate_plan:
        manifest = build_manifest(mod_root, cfg.raw, transitions,
                                  ground_rows, infantry_rows, emission_blocked,
                                  frontier_rows=tank_frontiers)
        manifest_path = out_dir / "equipment_decisions.json"
        encodability_path = out_dir / "equipment_encodability_report.md"
        plan_name = ("equipment_generation_plan.json" if args.plan_scope == "all"
                     else f"equipment_generation_plan_{args.plan_scope.replace('-', '_')}.json")
        plan_path = out_dir / plan_name
        write_manifest(manifest_path, manifest)
        write_encodability_report(encodability_path, manifest)
        frontier_groups = {(row.country, row.group) for row in tank_frontiers}
        scoped_patches = select_patches(
            emitted_patches, args.plan_scope, frontier_groups)
        plan = build_plan(mod_root, manifest.fingerprint, scoped_patches,
                          scope=args.plan_scope)
        write_plan(plan_path, plan)
        encodability = Counter(item.encodability for item in manifest.decisions)
        print("  decision manifest      : " + str(manifest_path))
        print("  generation plan       : " + str(plan_path))
        print("  plan scope            : " + plan.scope)
        print("  encodability report   : " + str(encodability_path))
        print("  planned operations    : " + str(len(plan.operations)))
        print("  encodability          : " + ", ".join(
            f"{key}={value}" for key, value in sorted(encodability.items())))

    counts = Counter(t.verdict for t in transitions)
    print()
    print("=" * 60)
    print("Summary (REPORT-ONLY - no mod file was modified)")
    print("=" * 60)
    print(f"  transitions evaluated : {len(transitions)}")
    for verdict in ("SWITCH", "SWITCH_REDESIGNED", "SWITCH_CONDITIONAL",
                    "KEEP_OLD", "PARALLEL_VARIANT", "UNRESOLVED"):
        print(f"  {verdict:<21} : {counts.get(verdict, 0)}")
    print(f"  diagnostics           : {diag.error_count} error(s), "
          f"{diag.warn_count} warning(s)")
    print(f"  CSV                   : {csv_path}")
    print(f"  Markdown              : {md_path}")
    print(f"  data-integrity        : {len(data_findings)} finding(s) -> "
          f"{out_dir / 'data_integrity_audit.md'}")
    if args.emit or args.generate_plan:
        print(f"  emit patches          : {len(emitted_patches)} "
              f"({len(emission_blocked)} blocked, DRY RUN - common/ untouched)")
        print(f"  Patch document        : {out_dir / 'emit_ai_equipment.md'}")
    print(f"  elapsed               : {time.time() - t0:.1f}s")

    if diag.error_count:
        print("\nUnresolved references were FLAGGED, not skipped - see the "
              "Diagnostics section of the Markdown report.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
