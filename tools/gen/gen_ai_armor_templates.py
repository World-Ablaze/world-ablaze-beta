#!/usr/bin/env python3
"""Generate the AI armour templates, their selection ladders and their decision predicates.

[armor-template-generator] One definition (tools/armor_templates_registry.json) owns composition,
eligibility references and routing, so the five ai_template files and the calculator can no longer
drift apart. Functional authority: documentation/WA_AI_ARMOR_GENERATOR_SPEC.md (A1-A12);
implementation contract: documentation/WA_AI_ARMOR_GENERATOR_TECH_SPEC.md.

Modes (no flag = --dry-run; nothing is written unless --apply is given):
    python tools/gen/gen_ai_armor_templates.py --dry-run
    python tools/gen/gen_ai_armor_templates.py --check
    python tools/gen/gen_ai_armor_templates.py --apply
    python tools/gen/gen_ai_armor_templates.py --explain tools/tests/fixtures/armor_case.json

Exit codes: 0 clean, 1 drift in --check, 2 invalid input or failed validation, 3 write failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "gen"))

from armor_templates import emit, inputs, model, resolve, transitions, validate  # noqa: E402

EFFECTS_OUT = "common/scripted_effects/WA_AI_TEMPLATES_ARMOR_generated.txt"
TRIGGERS_OUT = "common/scripted_triggers/WA_AI_TEMPLATES_ARMOR_generated.txt"
MANIFEST_OUT = "tools/generated/armor_templates_manifest.json"


def compile_all(registry, game):
    """Registry + game files -> per-family selections, code planes, ladder groups, stats."""
    per_family, planes_by_family, errors = {}, {}, []
    for family_id in registry.families:
        sels, errs, planes = resolve.enumerate_family(family_id, registry, game)
        per_family[family_id] = sels
        planes_by_family[family_id] = planes
        errors.extend((family_id,) + e for e in errs)

    groups, by_flag = [], {}
    for family_id, fam in registry.families.items():
        by_flag.setdefault((fam["flag"], fam["type_code"]), []).append(family_id)
    for (flag, _code), families in sorted(by_flag.items()):
        families = sorted(families, key=lambda f: registry.families[f]["code_range"][0])
        name = "WA_AI_TEMPLATES_ARMOR_calculate_%s" % flag.replace("WA_", "").lower()
        groups.append((name, families))

    stats = {
        "per_family": dict((f, len(s)) for f, s in sorted(per_family.items())),
        "targets": sum(len(s) for s in per_family.values()),
        "ladder_groups": len(groups),
        "resolve_errors": len(errors),
        "planes": dict((f, [(p.form, p.base, p.size) for p in ps])
                       for f, ps in sorted(planes_by_family.items())),
    }
    return per_family, planes_by_family, groups, stats, errors


def render(registry, game, per_family, planes_by_family, groups, stats):
    files = {}
    for family_id, sels in per_family.items():
        files[registry.families[family_id]["file"]] = emit.family_file(
            registry, family_id, sels, game)
    files[EFFECTS_OUT] = emit.effects_file(registry, groups, planes_by_family)
    files[TRIGGERS_OUT] = emit.triggers_file(registry, per_family)
    manifest = json.loads(emit.manifest(registry, per_family, stats))
    manifest["transitions_resolved"] = transitions.build(registry, per_family)
    files[MANIFEST_OUT] = json.dumps(manifest, indent=1) + "\n"
    return files


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def write(path: Path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--explain", metavar="FIXTURE")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    try:
        registry = model.load(REPO)
    except model.RegistryError as exc:
        print("REGISTRY: %s" % exc)
        return 2
    game = inputs.GameFiles(REPO)

    if args.explain:
        return explain(registry, game, Path(args.explain))

    try:
        per_family, planes_by_family, groups, stats, errors = compile_all(registry, game)
    except resolve.ResolveError as exc:
        print("COMPILE: %s" % exc)
        return 2

    findings = validate.run(registry, game, per_family, stats)
    for item in errors:
        findings.append(validate.Finding(validate.ERROR, "RESOLVE",
                                         "%s %s: %s" % (item[0], item[1], item[2])))

    print("targets: %d  (%s)" % (stats["targets"], ", ".join(
        "%s %d" % kv for kv in stats["per_family"].items())))
    print("ladders: %d" % stats["ladder_groups"])
    for family_id, planes in sorted(stats["planes"].items()):
        print("         %-8s %s" % (family_id, "  ".join(
            "%s %d..%d" % (form, base, base + size - 1) for form, base, size in planes)))

    files = render(registry, game, per_family, planes_by_family, groups, stats)
    total = sum(len(t) for t in files.values())
    print("output : %d files, %.1f KiB" % (len(files), total / 1024.0))
    for path in sorted(files):
        print("         %-70s %7.1f KiB  %s"
              % (path, len(files[path]) / 1024.0, digest(files[path])))

    errors_n = sum(1 for f in findings if f.level == validate.ERROR)
    warns_n = sum(1 for f in findings if f.level == validate.WARN)
    for finding in findings:
        if args.verbose or finding.level != validate.INFO:
            print(finding)
    print("%d ERROR, %d WARN" % (errors_n, warns_n))

    if args.check:
        drift = []
        for rel, text in sorted(files.items()):
            path = REPO / rel
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                drift.append(rel)
        if drift:
            print("DRIFT: %s" % ", ".join(drift))
            return 1
        return 2 if errors_n else 0

    if args.apply:
        if errors_n:
            print("refusing to write: %d ERROR" % errors_n)
            return 2
        try:
            for rel, text in sorted(files.items()):
                write(REPO / rel, text)
        except OSError as exc:
            print("WRITE: %s" % exc)
            return 3
        print("applied %d files" % len(files))
        return 0

    return 2 if errors_n else 0


def explain(registry, game, fixture: Path):
    """Offline explanation of one declared case. Reads no game state."""
    with open(fixture, encoding="utf-8") as fh:
        case = json.load(fh)
    facts = resolve.Facts(
        case["family"], case["mobile_infantry"], case.get("variant", resolve.EMPTY),
        case.get("td", resolve.EMPTY), case.get("spaa", resolve.EMPTY),
        bool(case.get("rockets")), int(case.get("quota", 0)), bool(case.get("waves")),
        bool(case.get("heavy_company")))
    try:
        sel = resolve.resolve(case["family"], facts, registry, game)
    except resolve.ResolveError as exc:
        print("REJECTED: %s" % exc)
        return 2
    print(json.dumps(sel.as_dict(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
