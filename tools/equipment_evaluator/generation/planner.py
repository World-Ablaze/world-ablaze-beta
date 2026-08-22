"""Convert emitter patches into a deterministic, replayable operation plan."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List

from ..decision_manifest import sha256_bytes, sha256_file


PLAN_SCHEMA_VERSION = 3
PLAN_SCOPES = ("all", "tank-frontiers")


@dataclass(frozen=True)
class ReplaceOperation:
    operation_id: str
    path: str
    kind: str
    group: str
    design: str
    start_hint: int
    end_hint: int
    source_fingerprint: str
    original_fingerprint: str
    replacement_fingerprint: str
    original: str
    replacement: str


@dataclass(frozen=True)
class OperationPlan:
    schema_version: int
    manifest_fingerprint: str
    required_symbols: List[str]
    operations: List[ReplaceOperation]
    scope: str = "all"

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "manifest_fingerprint": self.manifest_fingerprint,
            "scope": self.scope,
            "required_symbols": self.required_symbols,
            "operations": [asdict(op) for op in self.operations],
        }

    def canonical_bytes(self) -> bytes:
        return (json.dumps(self.to_dict(), indent=2, sort_keys=True,
                           ensure_ascii=False) + "\n").encode("utf-8")


def _operation_id(path: str, patch) -> str:
    identity = f"{path}|{patch.group}|{patch.design}|{patch.kind}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]


def select_patches(patches: Iterable, scope: str,
                   frontier_groups=()) -> List:
    """Return the complete, auditable patch subset owned by one plan scope."""
    if scope not in PLAN_SCOPES:
        raise ValueError(f"unsupported plan scope: {scope}")
    patches = list(patches)
    if scope == "all":
        return patches
    keys = set(frontier_groups)
    return [patch for patch in patches
            if (patch.country, patch.group) in keys]


def build_plan(mod_root: Path, manifest_fingerprint: str,
               patches: Iterable, scope: str = "all") -> OperationPlan:
    operations = []
    for patch in patches:
        # A full frontier reconciliation may rebuild an owned priority block
        # byte-for-byte identically. Such a patch is not an operation: keeping
        # it makes a second apply report it as perpetually pending after the
        # file fingerprint changes for neighbouring real edits.
        if patch.original == patch.replacement:
            continue
        relative = f"common/ai_equipment/{patch.file}".replace("\\", "/")
        operations.append(ReplaceOperation(
            operation_id=_operation_id(relative, patch), path=relative,
            kind=patch.kind, group=patch.group, design=patch.design,
            start_hint=patch.start, end_hint=patch.end,
            source_fingerprint=sha256_file(mod_root / relative),
            original_fingerprint=sha256_bytes(patch.original.encode("utf-8")),
            replacement_fingerprint=sha256_bytes(patch.replacement.encode("utf-8")),
            original=patch.original, replacement=patch.replacement))
    operations.sort(key=lambda op: (op.path, -op.start_hint, op.operation_id))
    required_symbols = sorted({
        symbol
        for op in operations
        for symbol in re.findall(r"\bWA_AI_EQUIPMENT_can_absorb_[A-Za-z0-9_]+",
                                 op.replacement)
    })
    return OperationPlan(PLAN_SCHEMA_VERSION, manifest_fingerprint,
                         required_symbols, operations, scope)


def write_plan(path: Path, plan: OperationPlan) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(plan.canonical_bytes())


def load_plan(path: Path) -> OperationPlan:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != PLAN_SCHEMA_VERSION:
        raise ValueError(f"unsupported plan schema: {raw.get('schema_version')}")
    scope = raw.get("scope", "all")
    if scope not in PLAN_SCOPES:
        raise ValueError(f"unsupported plan scope: {scope}")
    return OperationPlan(raw["schema_version"], raw["manifest_fingerprint"],
                         list(raw.get("required_symbols", [])),
                         [ReplaceOperation(**item) for item in raw["operations"]],
                         scope)
