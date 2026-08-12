"""Technology-graph ownership for modular equipment design succession.

The order of blocks in ``common/ai_equipment`` is presentation/authoring order,
not a guarantee that every adjacent design supersedes the previous one.  A
country may place several parallel research branches in one production role
(USA Sherman and T20 are the canonical example).  This module resolves the
actual nearest design successors through ``path/leads_to_tech`` edges.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from .diagnostics import Diagnostics
from .parse_ai_equipment import DesignGroup
from .pdx import Node, ParseError, parse_file


@dataclass(frozen=True)
class DesignGraph:
    """Nearest design-to-design edges for one ai_equipment group."""

    edges: Tuple[Tuple[str, str], ...]
    roots: Tuple[str, ...]

    @property
    def branched(self) -> bool:
        outgoing: Dict[str, int] = {}
        incoming: Dict[str, int] = {}
        for old, new in self.edges:
            outgoing[old] = outgoing.get(old, 0) + 1
            incoming[new] = incoming.get(new, 0) + 1
        return any(n > 1 for n in outgoing.values()) or any(n > 1 for n in incoming.values())

    def adjacency(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        for old, new in self.edges:
            result.setdefault(old, []).append(new)
        return result


class TechnologyGraph:
    """Read-only graph assembled from every technology file in the mod."""

    def __init__(self, mod_root: Path, diag: Diagnostics) -> None:
        self.edges: Dict[str, Set[str]] = {}
        self.diag = diag
        tech_dir = mod_root / "common/technologies"
        for path in sorted(tech_dir.glob("*.txt")):
            try:
                root = parse_file(path)
            except (OSError, ParseError) as exc:
                diag.warn("technology_graph_parse", str(path), str(exc))
                continue
            technologies = root.get_block("technologies")
            if technologies is None:
                continue
            for tech_name, tech in technologies.named_blocks():
                for _key, _op, value in tech.all("path"):
                    if not isinstance(value, Node):
                        continue
                    target = value.get_str("leads_to_tech")
                    if target:
                        self.edges.setdefault(tech_name, set()).add(target)

    def design_graph(self, group: DesignGroup,
                     stop_techs: Iterable[str] = ()) -> DesignGraph:
        """Return nearest successors without crossing another group design.

        Walking stops independently on each research branch as soon as a tech
        enabling another design in this group is found.  Intermediate techs
        which unlock modules only are therefore transparent.
        """
        all_designs = [d for d in group.designs if d.airframe]
        designs = [d for d in all_designs if len(d.enable_techs) == 1]
        # Plane design blocks generally have no explicit enable condition: the
        # availability is encoded by their module techs and priority ladder.
        # Keep the existing ordered-ladder interpretation for that legacy
        # shape.  Tank groups do expose enable techs and therefore never use
        # this fallback; that distinction is what prevents Sherman/T20 from
        # being collapsed into one fictitious sequence.
        if len(designs) < 2:
            edges = tuple((old.name, new.name)
                          for old, new in zip(all_designs, all_designs[1:])
                          if old.name != new.name)
            roots = (all_designs[0].name,) if edges else ()
            return DesignGraph(edges, roots)
        by_tech: Dict[str, List[str]] = {}
        position = {d.name: d.index for d in designs}
        for design in designs:
            by_tech.setdefault(design.enable_techs[0], []).append(design.name)
        barriers = set(stop_techs) | set(by_tech)

        found: Set[Tuple[str, str]] = set()
        for design in designs:
            start = design.enable_techs[0]
            frontier = sorted(self.edges.get(start, set()))
            visited: Set[str] = set()
            while frontier:
                tech = frontier.pop(0)
                if tech in visited:
                    continue
                visited.add(tech)
                targets = [name for name in by_tech.get(tech, []) if name != design.name]
                if targets:
                    found.update((design.name, name) for name in targets)
                    continue
                # Another ai_equipment group owns this unlock.  It is a real
                # production-role boundary (for example M26 Pershing between
                # the Sherman and T23 branches), not a transparent module tech.
                if tech in barriers:
                    continue
                frontier.extend(sorted(self.edges.get(tech, set()) - visited))

        ordered = tuple(sorted(found, key=lambda edge: (
            position.get(edge[0], 10**9), position.get(edge[1], 10**9), edge)))
        incoming = {new for _old, new in ordered}
        participating = {name for edge in ordered for name in edge}
        roots = tuple(sorted(
            (name for name in participating if name not in incoming),
            key=lambda name: position.get(name, 10**9)))
        return DesignGraph(ordered, roots)
