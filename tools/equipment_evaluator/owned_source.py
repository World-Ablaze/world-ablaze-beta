"""Reconstruct the pre-generator logical source from owned marker blocks.

Analysis must remain stable after generated code is applied. Resource-gate
blocks are removed from the logical view; module replacements restore the
original slot assignment recorded in their marker.
"""

from __future__ import annotations

import re
from typing import List


_FIELD_RE = re.compile(r"([a-z_]+)=([^\s]+)")


def _fields(line: str) -> dict:
    return dict(_FIELD_RE.findall(line))


def logical_source(raw: str) -> str:
    lines = raw.splitlines()
    out: List[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if "WA_EQUIPGEN_BEGIN" not in line:
            out.append(line)
            index += 1
            continue
        fields = _fields(line)
        marker = fields.get("id")
        end = index + 1
        while end < len(lines):
            if "WA_EQUIPGEN_END" in lines[end] and f"id={marker}" in lines[end]:
                break
            end += 1
        if end >= len(lines):
            # Let the normal parser/validator expose malformed ownership; do
            # not silently discard the rest of the file.
            out.append(line)
            index += 1
            continue
        kind = fields.get("kind")
        if fields.get("mode") == "replace" and kind in (
                "module", "supersede", "priority_factor"):
            if kind == "module":
                slot = fields.get("slot")
            elif kind == "supersede":
                slot = "has_tech"
            else:
                slot = "factor"
            original = fields.get("original")
            indent = line[:len(line) - len(line.lstrip())]
            if slot and original:
                out.append(f"{indent}{slot} = {original}")
        # retain_gate, hold_gate and inserted modules did not exist in the
        # baseline, so their complete owned block disappears from this view.
        index = end + 1
    suffix = "\n" if raw.endswith(("\n", "\r")) else ""
    return "\n".join(out) + suffix
