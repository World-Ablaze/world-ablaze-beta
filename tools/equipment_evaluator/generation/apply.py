"""Transactional and idempotent application of an operation plan."""

from __future__ import annotations

import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from ..decision_manifest import sha256_bytes
from ..pdx import _TOKEN_RE
from .planner import OperationPlan, ReplaceOperation


BEGIN = "WA_EQUIPGEN_BEGIN"
END = "WA_EQUIPGEN_END"


@dataclass
class ApplyResult:
    changed_files: List[str] = field(default_factory=list)
    applied_operations: List[str] = field(default_factory=list)
    noop_operations: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.conflicts


def _balanced(raw: str) -> bool:
    depth = 0
    for match in _TOKEN_RE.finditer(raw):
        if match.lastgroup == "lbrace":
            depth += 1
        elif match.lastgroup == "rbrace":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _validate_owned_markers(raw: str) -> List[str]:
    stack: List[str] = []
    errors: List[str] = []
    seen = set()
    for number, line in enumerate(raw.splitlines(), 1):
        if BEGIN in line:
            marker = line.split("id=", 1)[1].split()[0] if "id=" in line else ""
            if not marker or marker in seen:
                errors.append(f"line {number}: missing or duplicate generated id `{marker}`")
            stack.append(marker)
            seen.add(marker)
        if END in line:
            marker = line.split("id=", 1)[1].split()[0] if "id=" in line else ""
            if not stack or stack.pop() != marker:
                errors.append(f"line {number}: unmatched generated end `{marker}`")
    if stack:
        errors.append("unclosed generated marker(s): " + ", ".join(stack))
    return errors


def _find_state(raw: str, op: ReplaceOperation) -> Tuple[str, int]:
    """Return pending/applied/conflict and the current block position."""
    if raw[op.start_hint:op.end_hint] == op.original:
        return "pending", op.start_hint
    original_positions = []
    pos = raw.find(op.original)
    while pos >= 0:
        original_positions.append(pos)
        pos = raw.find(op.original, pos + 1)
    replacement_positions = []
    pos = raw.find(op.replacement)
    while pos >= 0:
        replacement_positions.append(pos)
        pos = raw.find(op.replacement, pos + 1)
    if len(replacement_positions) == 1:
        return "applied", replacement_positions[0]
    if len(original_positions) == 1:
        return "pending", original_positions[0]
    return "conflict", -1


def _preflight_file(raw: str, operations: List[ReplaceOperation],
                    current_fingerprint: str) -> tuple[str, List[str], List[str]]:
    errors: List[str] = []
    noops: List[str] = []
    states = []
    source_hashes = {op.source_fingerprint for op in operations}
    if len(source_hashes) != 1:
        errors.append("operations disagree on the source fingerprint")
        return raw, noops, errors

    for op in operations:
        state, position = _find_state(raw, op)
        states.append((op, state, position))
        if state == "conflict":
            errors.append(f"{op.operation_id}: original/replacement block is not uniquely locatable")

    if errors:
        return raw, noops, errors
    if current_fingerprint != next(iter(source_hashes)):
        if all(state == "applied" for _op, state, _pos in states):
            return raw, [op.operation_id for op, _state, _pos in states], []
        errors.append("source fingerprint changed after plan generation")
        return raw, noops, errors

    pending = [(op, pos) for op, state, pos in states if state == "pending"]
    noops.extend(op.operation_id for op, state, _pos in states if state == "applied")
    ranges = sorted((pos, pos + len(op.original), op.operation_id) for op, pos in pending)
    for left, right in zip(ranges, ranges[1:]):
        if left[1] > right[0]:
            errors.append(f"overlapping operations: {left[2]} and {right[2]}")
    if errors:
        return raw, noops, errors

    result = raw
    for op, pos in sorted(pending, key=lambda item: item[1], reverse=True):
        result = result[:pos] + op.replacement + result[pos + len(op.original):]
    if not _balanced(result):
        errors.append("generated PDXScript has unbalanced braces")
    errors.extend(_validate_owned_markers(result))
    return result, noops, errors


def verify_plan(mod_root: Path, plan: OperationPlan) -> ApplyResult:
    result = ApplyResult()
    result.conflicts.extend(_missing_symbols(mod_root, plan))
    by_path: Dict[str, List[ReplaceOperation]] = defaultdict(list)
    for op in plan.operations:
        by_path[op.path].append(op)
    for relative, operations in sorted(by_path.items()):
        path = mod_root / relative
        if not path.exists():
            result.conflicts.append(f"{relative}: file is missing")
            continue
        raw = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        for op in operations:
            state, _position = _find_state(raw, op)
            if state == "applied":
                result.noop_operations.append(op.operation_id)
            elif state == "pending":
                result.conflicts.append(f"{relative}:{op.operation_id}: operation is pending")
            else:
                result.conflicts.append(f"{relative}:{op.operation_id}: generated block conflicts")
        result.conflicts.extend(f"{relative}: {e}" for e in _validate_owned_markers(raw))
    return result


def apply_plan(mod_root: Path, plan: OperationPlan) -> ApplyResult:
    """Preflight every file, then replace all or none; repeated apply is a no-op."""
    result = ApplyResult()
    result.conflicts.extend(_missing_symbols(mod_root, plan))
    by_path: Dict[str, List[ReplaceOperation]] = defaultdict(list)
    for op in plan.operations:
        by_path[op.path].append(op)

    originals: Dict[Path, bytes] = {}
    rendered: Dict[Path, bytes] = {}
    for relative, operations in sorted(by_path.items()):
        path = (mod_root / relative).resolve()
        try:
            path.relative_to(mod_root.resolve())
        except ValueError:
            result.conflicts.append(f"{relative}: target escapes mod root")
            continue
        if not path.exists():
            result.conflicts.append(f"{relative}: file is missing")
            continue
        original_bytes = path.read_bytes()
        had_bom = original_bytes.startswith(b"\xef\xbb\xbf")
        decoded = original_bytes.decode("utf-8-sig")
        newline = "\r\n" if "\r\n" in decoded else "\n"
        raw = decoded.replace("\r\n", "\n").replace("\r", "\n")
        new_raw, noops, errors = _preflight_file(
            raw, operations, sha256_bytes(original_bytes))
        result.noop_operations.extend(noops)
        result.conflicts.extend(f"{relative}: {error}" for error in errors)
        originals[path] = original_bytes
        if new_raw != raw:
            encoded = new_raw.replace("\n", newline).encode("utf-8")
            rendered[path] = (b"\xef\xbb\xbf" + encoded) if had_bom else encoded
            result.applied_operations.extend(
                op.operation_id for op in operations if op.operation_id not in noops)

    if result.conflicts:
        result.applied_operations.clear()
        return result

    temp_paths: Dict[Path, Path] = {}
    replaced: List[Path] = []
    try:
        for path, data in rendered.items():
            fd, temp_name = tempfile.mkstemp(prefix=path.name + ".wa-equipgen-",
                                             dir=str(path.parent))
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            temp_paths[path] = Path(temp_name)
        for path in sorted(rendered, key=lambda item: str(item)):
            os.replace(temp_paths[path], path)
            replaced.append(path)
            result.changed_files.append(str(path.relative_to(mod_root)))
    except Exception as exc:
        result.conflicts.append(f"transaction failed: {exc}")
        for path in replaced:
            path.write_bytes(originals[path])
        result.changed_files.clear()
        result.applied_operations.clear()
    finally:
        for temp_path in temp_paths.values():
            if temp_path.exists():
                temp_path.unlink()
    return result


def _missing_symbols(mod_root: Path, plan: OperationPlan) -> List[str]:
    if not plan.required_symbols:
        return []
    trigger_dir = mod_root / "common/scripted_triggers"
    corpus = ""
    if trigger_dir.is_dir():
        corpus = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace")
                           for path in sorted(trigger_dir.glob("*.txt")))
    return [f"required scripted trigger is missing: {symbol}"
            for symbol in plan.required_symbols if f"{symbol} = {{" not in corpus]
