"""
Source-span index over an `ai_equipment` country file.

`pdx.py` builds a value tree but deliberately throws away positions - it exists
to *read* PDXScript fast, not to rewrite it. The emitter needs the opposite:
the exact byte/line range of a specific `priority = {}` block so a patch can be
anchored to it and reviewed against the file as written, comments and all.

This module walks the same token stream `pdx.py` uses (so comments and quoted
strings cannot be mistaken for braces) and records, for every named block, its
nesting depth and source range. The three depths the emitter cares about:

    depth 0   <design group>  = {        e.g. SOV_fighter_mr
    depth 1     <design>      = {        e.g. fighter_mr_7
    depth 2       priority    = {

Read-only: nothing here writes, and `Span.text` is a slice of the original.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .pdx import _TOKEN_RE


@dataclass
class Span:
    key: str
    depth: int
    start: int          # byte offset of the first character of `key`
    body_start: int     # byte offset of the opening `{`
    end: int            # byte offset one past the closing `}`
    line: int           # 1-based line of `key`
    end_line: int       # 1-based line of the closing `}`
    children: List["Span"]

    @property
    def n_lines(self) -> int:
        return self.end_line - self.line + 1

    def text(self, raw: str) -> str:
        return raw[self.start:self.end]

    def child(self, key: str) -> Optional["Span"]:
        for c in self.children:
            if c.key == key:
                return c
        return None


def index_file(raw: str) -> List[Span]:
    """Top-level named blocks, each carrying its nested children."""
    line_starts = [0]
    for i, ch in enumerate(raw):
        if ch == "\n":
            line_starts.append(i + 1)

    def line_of(pos: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    roots: List[Span] = []
    stack: List[Span] = []
    pending_key: Optional[str] = None
    pending_pos: int = 0

    for m in _TOKEN_RE.finditer(raw):
        kind = m.lastgroup
        if kind in ("ws", "comment"):
            continue
        if kind == "lbrace":
            span = Span(key=pending_key or "", depth=len(stack),
                        start=pending_pos if pending_key else m.start(),
                        body_start=m.start(), end=-1,
                        line=line_of(pending_pos if pending_key else m.start()),
                        end_line=-1, children=[])
            if stack:
                stack[-1].children.append(span)
            else:
                roots.append(span)
            stack.append(span)
            pending_key = None
            continue
        if kind == "rbrace":
            if stack:
                span = stack.pop()
                span.end = m.end()
                span.end_line = line_of(m.start())
            pending_key = None
            continue
        if kind in ("ident", "string", "number", "other"):
            pending_key = m.group()
            pending_pos = m.start()
            continue
        # operators leave `pending_key` alone: `key = {` must remember `key`

    return roots


def find_priority(raw: str, group: str, design: str) -> Optional[Span]:
    """The `priority = {}` span of one design, or None if it has none."""
    for g in index_file(raw):
        if g.key != group:
            continue
        for d in g.children:
            if d.key == design:
                return d.child("priority")
    return None


def find_design(raw: str, group: str, design: str) -> Optional[Span]:
    for g in index_file(raw):
        if g.key != group:
            continue
        for d in g.children:
            if d.key == design:
                return d
    return None


def indent_of(raw: str, span: Span) -> str:
    """The leading whitespace of the line `span` starts on (tabs preserved)."""
    line_start = raw.rfind("\n", 0, span.start) + 1
    lead = raw[line_start:span.start]
    return lead if lead.strip() == "" else ""


def build_index(raw: str) -> Dict[str, Dict[str, Span]]:
    """group name -> design name -> design span."""
    out: Dict[str, Dict[str, Span]] = {}
    for g in index_file(raw):
        out.setdefault(g.key, {})
        for d in g.children:
            out[g.key][d.key] = d
    return out
