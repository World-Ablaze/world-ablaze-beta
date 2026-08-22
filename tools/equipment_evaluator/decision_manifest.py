"""Deterministic, domain-neutral output of the equipment analysis."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from collections import Counter


SCHEMA_VERSION = 2


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes()) if path.exists() else "MISSING"


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    domain: str
    country: str
    role: str
    group: str
    old_design: str
    new_design: str
    verdict: str
    retention: float
    gain: float
    source: str
    source_fingerprint: str
    encodability: str
    resource_gates: Dict[str, float] = field(default_factory=dict)
    redesign: Dict[str, str] = field(default_factory=dict)
    blockers: List[str] = field(default_factory=list)
    rank: int = 0
    action: str = ""
    priority_factor: float = 0.0
    fallback_design: str = ""


@dataclass(frozen=True)
class DecisionManifest:
    schema_version: int
    config_fingerprint: str
    decisions: List[DecisionRecord]

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "config_fingerprint": self.config_fingerprint,
            "decisions": [asdict(item) for item in self.decisions],
        }

    def canonical_bytes(self) -> bytes:
        return (json.dumps(self.to_dict(), indent=2, sort_keys=True,
                           ensure_ascii=False) + "\n").encode("utf-8")

    @property
    def fingerprint(self) -> str:
        return sha256_bytes(self.canonical_bytes())


def _source(mod_root: Path, relative: str) -> tuple[str, str]:
    path = mod_root / relative
    return relative.replace("\\", "/"), sha256_file(path)


def _air_encodability(verdict: str, resources: Dict[str, float]) -> tuple[str, List[str]]:
    if verdict == "SWITCH":
        return "NO_CHANGE_REQUIRED", []
    if verdict == "SWITCH_CONDITIONAL":
        supported = {"steel", "aluminium", "chromium", "tungsten"}
        missing = sorted(set(resources) - supported)
        return (("ENCODABLE_WITH_GATE", []) if not missing else
                ("ENGINE_UNSUPPORTED", ["missing resource gates: " + ", ".join(missing)]))
    if verdict == "SWITCH_REDESIGNED":
        return "REQUIRES_GENERATED_DESIGN", []
    if verdict in ("PARALLEL_VARIANT", "UNRESOLVED"):
        return "NOT_APPLICABLE", []
    if verdict == "KEEP_OLD":
        return "ENCODABLE_CHAIN_POLICY", []
    return "BACKEND_NOT_IMPLEMENTED", ["verdict backend is not implemented"]


def build_manifest(mod_root: Path, config_raw: dict, air_rows: Iterable,
                   ground_rows: Iterable, infantry_rows: Iterable,
                   emission_blocked: Iterable = (),
                   frontier_rows: Iterable = ()) -> DecisionManifest:
    decisions: List[DecisionRecord] = []
    config_bytes = json.dumps(config_raw, sort_keys=True, separators=(",", ":")).encode("utf-8")
    blocked_groups = {(item.country, item.group): item.reason for item in emission_blocked
                      if item.transition == f"{item.country}/{item.group}"}
    blocked_rows = {(item.country, item.group, item.transition): item.reason
                    for item in emission_blocked}
    frontier_groups = {(row.country, row.group) for row in frontier_rows}

    def generator_block(country: str, group: str, old: str, new: str) -> Optional[str]:
        return (blocked_groups.get((country, group)) or
                blocked_rows.get((country, group, f"{old} -> {new}")))

    for row in air_rows:
        relative, fingerprint = _source(
            mod_root, f"common/ai_equipment/{row.country}_planes.txt")
        resources = dict(sorted(row.res_significant.items()))
        encodability, blockers = _air_encodability(row.verdict, resources)
        blocked = generator_block(row.country, row.group, row.from_design, row.to_design)
        if blocked and encodability not in ("NO_CHANGE_REQUIRED", "NOT_APPLICABLE"):
            encodability, blockers = "ENGINE_UNSUPPORTED", [blocked]
        redesign = {}
        if row.redesign:
            redesign = {slot: module for slot, _old, module in row.redesign.changes}
        decisions.append(DecisionRecord(
            decision_id=f"air:{row.country}:{row.group}:{row.from_design}:{row.to_design}",
            domain="air", country=row.country, role=row.role, group=row.group,
            old_design=row.from_design, new_design=row.to_design,
            verdict=row.verdict, retention=row.efficiency_retention,
            gain=row.gain, source=relative, source_fingerprint=fingerprint,
            encodability=encodability, resource_gates=resources,
            redesign=dict(sorted(redesign.items())), blockers=blockers))

    for row in ground_rows:
        base = "common/ai_equipment" if row.domain == "tanks" else "common/technologies"
        relative, fingerprint = _source(mod_root, f"{base}/{row.source}")
        encodability = "BACKEND_NOT_IMPLEMENTED"
        blockers = [f"{row.domain} code-generation backend is not implemented"]
        if row.verdict == "SWITCH":
            encodability, blockers = "NO_CHANGE_REQUIRED", []
        elif row.domain == "tanks" and row.verdict == "SWITCH_CONDITIONAL":
            supported = {"steel", "aluminium", "chromium", "tungsten"}
            missing = sorted(set(row.significant_resources) - supported)
            if missing:
                encodability, blockers = "ENGINE_UNSUPPORTED", [
                    "missing resource gates: " + ", ".join(missing)]
            else:
                encodability, blockers = "ENCODABLE_WITH_GATE", []
        elif row.domain == "tanks" and row.verdict == "SWITCH_REDESIGNED":
            encodability, blockers = "REQUIRES_GENERATED_DESIGN", []
        elif row.domain == "tanks" and row.verdict == "KEEP_OLD":
            encodability, blockers = "ENCODABLE_CHAIN_POLICY", []
        blocked = generator_block(row.country, row.group, row.old, row.new)
        if row.domain == "tanks" and (row.country, row.group) in frontier_groups:
            encodability, blockers = "ENCODED_BY_FRONTIER_POLICY", []
        if blocked and encodability != "NO_CHANGE_REQUIRED":
            encodability, blockers = "ENGINE_UNSUPPORTED", [blocked]
        decisions.append(DecisionRecord(
            decision_id=f"{row.domain}:{row.country}:{row.group}:{row.old}:{row.new}",
            domain=row.domain, country=row.country, role=row.role, group=row.group,
            old_design=row.old, new_design=row.new, verdict=row.verdict,
            retention=row.retention, gain=row.adjusted_gain, source=relative,
            source_fingerprint=fingerprint, encodability=encodability,
            resource_gates=dict(sorted(row.significant_resources.items())),
            redesign={str(i): value for i, value in enumerate(row.redesign_changes)},
            blockers=blockers))

    for row in frontier_rows:
        relative, fingerprint = _source(
            mod_root, f"common/ai_equipment/{row.country}_tank.txt")
        decisions.append(DecisionRecord(
            decision_id=f"tank_frontier:{row.country}:{row.group}:{row.design}",
            domain="tanks", country=row.country, role=row.role, group=row.group,
            old_design=row.fallback_design, new_design=row.design,
            verdict=row.action, retention=1.0, gain=row.score,
            source=relative, source_fingerprint=fingerprint,
            encodability="ENCODABLE_FRONTIER_POLICY",
            resource_gates=dict(sorted(row.resource_gates.items())),
            redesign={str(i): value for i, value in enumerate(row.redesign_changes)},
            blockers=list(row.failed_thresholds), rank=row.rank,
            action=row.action, priority_factor=row.priority_factor,
            fallback_design=row.fallback_design))

    for row in infantry_rows:
        relative, fingerprint = _source(
            mod_root, f"common/technologies/{row.technology_file}")
        encodability = "NO_CHANGE_REQUIRED" if row.verdict == "SWITCH" else "ENGINE_UNSUPPORTED"
        blockers = [] if encodability == "NO_CHANGE_REQUIRED" else [
            "no verified per-model ai_equipment selector for non-modular infantry"]
        decisions.append(DecisionRecord(
            decision_id=f"infantry:{row.country}:infantry_equipment:{row.old.name}:{row.new.name}",
            domain="infantry", country=row.country, role="infantry_equipment",
            group="infantry_equipment", old_design=row.old.name,
            new_design=row.new.name, verdict=row.verdict, retention=row.retention,
            gain=row.adjusted_gain, source=relative, source_fingerprint=fingerprint,
            encodability=encodability,
            resource_gates={k: v for k, v in sorted(row.resource_delta.items()) if v > 0},
            blockers=blockers))

    decisions.sort(key=lambda item: item.decision_id)
    return DecisionManifest(SCHEMA_VERSION, sha256_bytes(config_bytes), decisions)


def write_manifest(path: Path, manifest: DecisionManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(manifest.canonical_bytes())


def write_encodability_report(path: Path, manifest: DecisionManifest) -> None:
    counts = Counter((item.domain, item.encodability) for item in manifest.decisions)
    lines = [
        "# Equipment generator encodability audit", "",
        "This report distinguishes analysis coverage from code-generation coverage.", "",
        "| domain | status | decisions |", "| --- | --- | ---: |",
    ]
    lines.extend(f"| {domain} | {status} | {count} |"
                 for (domain, status), count in sorted(counts.items()))
    lines += ["", "## Decisions requiring another backend or engine proof", "",
              "| decision | verdict | status | reason |", "| --- | --- | --- | --- |"]
    for item in manifest.decisions:
        if item.encodability not in ("BACKEND_NOT_IMPLEMENTED", "ENGINE_UNSUPPORTED"):
            continue
        reason = " ; ".join(item.blockers).replace("|", "\\|")
        lines.append(f"| `{item.decision_id}` | {item.verdict} | "
                     f"{item.encodability} | {reason} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
