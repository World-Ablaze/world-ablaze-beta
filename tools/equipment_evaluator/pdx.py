"""
Minimal PDXScript (Clausewitz) reader used by the equipment evaluator.

Why this module exists rather than reusing an existing parser
------------------------------------------------------------
`tools/migrations/ai_will_do/ai_replacer_base/` is regex + brace-matching and is specialised for
technology blocks (`TechBlock`, `find_ai_will_do_block`); it does not produce a
value tree.  `tools/archive/dlc_splitter/` has a real lexer and parser, but its AST is
built to *round-trip formatting* for rewriting files, which we do not need and
which costs a lot of time on the ~6 MB of airframe/module data we read.

This module keeps the *token grammar* of `tools/archive/dlc_splitter/lexer.py`
(identifier / number / string / `=` `<` `>` / braces / `#` comments / `@vars`)
but scans with a single compiled regex and emits a plain, read-only tree.
The evaluator never writes PDXScript, so nothing here needs to preserve
whitespace.

Tree shape
----------
`Node` holds an ordered list of `(key, op, value)` entries where `value` is
either a `str` (scalar) or a nested `Node`.  Duplicate keys are legal and
preserved (HOI4 uses them, e.g. repeated `module_count_limit`).
Anonymous list items (`{ a b c }`) are stored with ``key=None, op=None``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Optional, Tuple, Union

__all__ = ["Node", "ParseError", "parse_text", "parse_file"]


class ParseError(Exception):
    """Raised when a file cannot be turned into a tree at all."""


# One regex, one pass. Order matters: comments before '#'-less tokens, strings
# before identifiers, numbers before identifiers (so -1.5 lexes as a number).
_TOKEN_RE = re.compile(
    r"""
      (?P<ws>[ \t\r\n]+)
    | (?P<comment>\#[^\r\n]*)
    | (?P<string>"(?:[^"\\]|\\.)*")
    | (?P<lbrace>\{)
    | (?P<rbrace>\})
    | (?P<op>[=<>]=?)
    | (?P<number>-?\d+(?:\.\d+)?)
    | (?P<ident>[@A-Za-z_][A-Za-z0-9_.:\-]*)
    | (?P<other>\S)
    """,
    re.VERBOSE,
)

Entry = Tuple[Optional[str], Optional[str], Union[str, "Node"]]


class Node:
    """An ordered multimap of PDXScript entries."""

    __slots__ = ("entries",)

    def __init__(self, entries: Optional[List[Entry]] = None) -> None:
        self.entries: List[Entry] = entries if entries is not None else []

    # -- construction -----------------------------------------------------
    def append(self, key: Optional[str], op: Optional[str], value) -> None:
        self.entries.append((key, op, value))

    # -- lookups ----------------------------------------------------------
    def all(self, key: str) -> Iterator[Entry]:
        """Yield every entry with this key, in file order."""
        for k, op, v in self.entries:
            if k == key:
                yield (k, op, v)

    def get(self, key: str, default=None):
        """Last value for `key` (HOI4 last-wins), or `default`."""
        found = default
        for _, _, v in self.all(key):
            found = v
        return found

    def get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        v = self.get(key)
        if isinstance(v, str):
            return v.strip('"')
        return default

    def get_float(self, key: str, default: Optional[float] = None) -> Optional[float]:
        v = self.get(key)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return default
        return default

    def get_block(self, key: str) -> Optional["Node"]:
        v = self.get(key)
        return v if isinstance(v, Node) else None

    def get_bool(self, key: str, default: bool = False) -> bool:
        v = self.get_str(key)
        if v is None:
            return default
        return v.lower() == "yes"

    def items(self) -> Iterator[Entry]:
        return iter(self.entries)

    def scalars(self) -> List[str]:
        """Anonymous items of a list block: `{ a b c }` -> ['a','b','c']."""
        return [v for k, _, v in self.entries if k is None and isinstance(v, str)]

    def named_blocks(self) -> Iterator[Tuple[str, "Node"]]:
        for k, _, v in self.entries:
            if k is not None and isinstance(v, Node):
                yield k, v

    def scalar_map(self) -> dict:
        """`{ a = 1 b = 2 }` -> {'a': '1', 'b': '2'} (last wins)."""
        out = {}
        for k, _, v in self.entries:
            if k is not None and isinstance(v, str):
                out[k] = v.strip('"')
        return out

    def float_map(self) -> dict:
        out = {}
        for k, v in self.scalar_map().items():
            try:
                out[k] = float(v)
            except ValueError:
                continue
        return out

    def __contains__(self, key: str) -> bool:
        return any(k == key for k, _, _ in self.entries)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        keys = [k for k, _, _ in self.entries[:6] if k]
        return f"<Node {len(self.entries)} entries {keys}>"


def _tokenize(text: str):
    for m in _TOKEN_RE.finditer(text):
        kind = m.lastgroup
        if kind in ("ws", "comment"):
            continue
        yield kind, m.group()


def parse_text(text: str, *, source: str = "<text>") -> Node:
    """Parse PDXScript into a `Node`. Raises `ParseError` on unbalanced braces."""
    tokens = list(_tokenize(text))
    n = len(tokens)
    root = Node()
    stack: List[Node] = [root]
    # pending key/operator waiting for a value
    pending_key: Optional[str] = None
    pending_op: Optional[str] = None
    i = 0

    while i < n:
        kind, tok = tokens[i]

        if kind == "op":
            if pending_key is None:
                # Stray operator (e.g. `count < 1` where `count` was consumed
                # as an anonymous item). Recover by promoting the previous
                # anonymous scalar back into a key.
                cur = stack[-1]
                if cur.entries and cur.entries[-1][0] is None and isinstance(cur.entries[-1][2], str):
                    pending_key = cur.entries.pop()[2]
                else:
                    i += 1
                    continue
            pending_op = tok
            i += 1
            continue

        if kind == "lbrace":
            child = Node()
            stack[-1].append(pending_key, pending_op or "=", child)
            pending_key, pending_op = None, None
            stack.append(child)
            i += 1
            continue

        if kind == "rbrace":
            if len(stack) == 1:
                raise ParseError(f"{source}: unbalanced '}}' (extra closing brace)")
            stack.pop()
            pending_key, pending_op = None, None
            i += 1
            continue

        # scalar-ish token (ident / number / string / other)
        if pending_op is not None:
            stack[-1].append(pending_key, pending_op, tok)
            pending_key, pending_op = None, None
            i += 1
            continue

        # No operator yet: this token may be a key (next token is an operator)
        # or an anonymous list item.
        nxt = tokens[i + 1][0] if i + 1 < n else None
        if nxt == "op":
            pending_key = tok
            i += 1
            continue

        stack[-1].append(None, None, tok)
        i += 1

    if len(stack) != 1:
        raise ParseError(f"{source}: unbalanced '{{' ({len(stack) - 1} block(s) left open)")
    return root


def parse_file(path: Path) -> Node:
    """Read `path` (BOM-tolerant, latin-1 fallback) and parse it."""
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - latin-1 never fails
        raise ParseError(f"{path}: could not decode")
    return parse_text(text, source=str(path))
