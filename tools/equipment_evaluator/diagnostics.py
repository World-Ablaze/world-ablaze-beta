"""
Diagnostics collector.

Repo convention (AGENTS.md / wa-tooling): silent truncation is forbidden.
Anything the evaluator cannot parse or cannot resolve is recorded here and
surfaced in both the CSV (`flags` column) and the Markdown report, never
dropped.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List


# Severity ordering, worst first.
ERROR = "ERROR"
WARN = "WARN"
INFO = "INFO"


@dataclass
class Issue:
    severity: str
    kind: str          # short machine-readable code, e.g. "unresolved_airframe"
    where: str         # file / country / design path
    detail: str


@dataclass
class Diagnostics:
    issues: List[Issue] = field(default_factory=list)
    _seen: set = field(default_factory=set)

    def add(self, severity: str, kind: str, where: str, detail: str, *, dedupe: bool = True) -> None:
        key = (severity, kind, where, detail)
        if dedupe:
            if key in self._seen:
                return
            self._seen.add(key)
        self.issues.append(Issue(severity, kind, where, detail))

    def error(self, kind: str, where: str, detail: str) -> None:
        self.add(ERROR, kind, where, detail)

    def warn(self, kind: str, where: str, detail: str) -> None:
        self.add(WARN, kind, where, detail)

    def info(self, kind: str, where: str, detail: str) -> None:
        self.add(INFO, kind, where, detail)

    # -- reporting --------------------------------------------------------
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ERROR)

    @property
    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == WARN)

    def by_kind(self) -> Dict[str, int]:
        return dict(Counter(i.kind for i in self.issues))

    def filtered(self, severity: str) -> List[Issue]:
        return [i for i in self.issues if i.severity == severity]
