"""
Parser for `common/ai_equipment/<TAG>_planes.txt` design groups.

Shape (see `common/ai_equipment/_documentation.info`):

    <group> = {
        category = air
        available_for = { TAGS }        # inclusive allow-list
        blocked_for  = { TAGS }         # exclusive block-list
        roles = { air_fighter ... }
        priority = { factor = N ... }
        <design> = {                    # generations, in file order
            priority = { ... }
            enable = { ... }
            target_variant = {
                match_value = N
                type = <airframe>
                modules = { <slot> = <module> ... }
            }
            requirements = { ... }
            allowed_modules = { ... }
        }
    }
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .diagnostics import Diagnostics
from .owned_source import logical_source
from .pdx import Node, ParseError, parse_text

# Keys inside a design group that are group metadata, not designs.
_GROUP_META = {
    "category", "blocked_for", "available_for", "roles", "priority",
    "allowed_modules", "requirements", "target_variant", "enable",
}


@dataclass
class Design:
    """One generation inside a design group."""
    name: str
    index: int                      # 0-based position within the group
    country: str
    group: str
    comment: str = ""
    airframe: Optional[str] = None
    modules: Dict[str, str] = field(default_factory=dict)   # slot -> module ('empty' kept)
    allowed_modules: List[str] = field(default_factory=list)
    enable_techs: List[str] = field(default_factory=list)
    match_value: float = 0.0
    flags: List[str] = field(default_factory=list)
    # -- priority block (phase 3 / emit) ---------------------------------
    priority_factor: Optional[float] = None
    # `has_tech` values on modifiers that zero this design out, i.e. the techs
    # whose arrival supersedes it. This is the hook a resource gate attaches to.
    supersede_techs: List[str] = field(default_factory=list)
    # Does the priority block already speak the WA_AI_EQUIPMENT vocabulary?
    # Fix 47 / Fix 49 designs do; the generator must not double-gate them.
    already_gated: bool = False

    @property
    def path(self) -> str:
        return f"{self.country}/{self.group}/{self.name}"


@dataclass
class DesignGroup:
    name: str
    country: str
    source_file: str
    category: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    available_for: List[str] = field(default_factory=list)
    blocked_for: List[str] = field(default_factory=list)
    designs: List[Design] = field(default_factory=list)
    # Filled by the evaluator from common/technologies path edges.  File order
    # is not succession order when a group contains parallel research branches.
    technology_edges: List[tuple[str, str]] = field(default_factory=list)

    @property
    def role(self) -> str:
        return self.roles[0] if self.roles else "unknown"


def _comment_for(text: str, design_name: str) -> str:
    """Best-effort: pull the trailing `# Yak-9U` comment off the design header."""
    import re
    m = re.search(rf"^[ \t]*{re.escape(design_name)}[ \t]*=[ \t]*\{{[ \t]*#(.*)$", text, re.M)
    return m.group(1).strip() if m else ""


def _read_priority(design: "Design", pri: Optional[Node]) -> None:
    """Pull the supersession hooks out of a design's `priority` block.

    The mod's blanket supersession idiom is

        priority = { factor = N  modifier = { has_tech = <next> factor = 0 } }

    i.e. "the moment the next tech lands, stop building this". Those `has_tech`
    values are where a resource or situation gate has to attach, so the emitter
    needs them. A block that already mentions `WA_AI_EQUIPMENT_` has been gated
    by hand (Fix 47 / Fix 49) and must be left alone.
    """
    if pri is None:
        return
    design.priority_factor = pri.get_float("factor")
    for _k, _op, mod in pri.all("modifier"):
        if not isinstance(mod, Node):
            continue
        factor = mod.get_float("factor")
        for key, _o, val in mod.items():
            if key and key.startswith("WA_AI_EQUIPMENT_"):
                design.already_gated = True
            if isinstance(val, Node):
                for k2, _o2, _v2 in val.items():          # NOT = { ... } / AND = { ... }
                    if k2 and k2.startswith("WA_AI_EQUIPMENT_"):
                        design.already_gated = True
        if factor is not None and factor == 0.0:
            tech = mod.get_str("has_tech")
            if tech:
                design.supersede_techs.append(tech)


def parse_country_file(path: Path, country: str, diag: Diagnostics,
                       category_filter: str = "air") -> List[DesignGroup]:
    raw_text = path.read_text(encoding="utf-8-sig", errors="replace")
    analysis_text = logical_source(raw_text)
    try:
        root = parse_text(analysis_text, source=str(path))
    except ParseError as exc:
        diag.error("parse_failure", str(path), str(exc))
        return []

    groups: List[DesignGroup] = []

    for gname, gbody in root.named_blocks():
        category = gbody.get_str("category")
        if category != category_filter:
            if category is not None:
                diag.info("wrong_category_group", f"{country}/{gname}",
                          f"category = {category}; skipped ({category_filter} requested)")
            continue

        group = DesignGroup(
            name=gname,
            country=country,
            source_file=path.name,
            category=category,
        )
        roles = gbody.get_block("roles")
        if roles is not None:
            group.roles = roles.scalars()
        if not group.roles:
            diag.warn("group_without_roles", f"{country}/{gname}",
                      "design group declares no roles; scored under 'unknown' role weights")
        av = gbody.get_block("available_for")
        if av is not None:
            group.available_for = av.scalars()
        bl = gbody.get_block("blocked_for")
        if bl is not None:
            group.blocked_for = bl.scalars()

        index = 0
        for dname, dbody in gbody.named_blocks():
            if dname in _GROUP_META:
                continue
            design = Design(
                name=dname, index=index, country=country, group=gname,
                comment=_comment_for(analysis_text, dname),
            )
            index += 1

            tv = dbody.get_block("target_variant")
            if tv is None:
                design.flags.append("no_target_variant")
                diag.warn("design_without_target_variant", design.path,
                          "design block has no target_variant; not evaluable")
                group.designs.append(design)
                continue

            design.airframe = tv.get_str("type")
            if design.airframe is None:
                design.flags.append("no_airframe_type")
                diag.warn("design_without_type", design.path,
                          "target_variant has no `type =` airframe reference")
            design.match_value = tv.get_float("match_value", 0.0) or 0.0

            mods = tv.get_block("modules")
            if mods is not None:
                for slot, op, value in mods.items():
                    if slot is None:
                        continue
                    if isinstance(value, Node):
                        # nested { module = X } / { any_of = { ... } }
                        picked = value.get_str("module")
                        if picked is None:
                            anyof = value.get_block("any_of")
                            if anyof is not None and anyof.scalars():
                                picked = anyof.scalars()[0]
                                design.flags.append(f"any_of:{slot}")
                                diag.warn("any_of_slot", design.path,
                                          f"slot `{slot}` uses any_of; first entry `{picked}` assumed")
                        if picked is None:
                            design.flags.append(f"unreadable_slot:{slot}")
                            diag.warn("unreadable_slot", design.path,
                                      f"slot `{slot}` has a nested spec with no resolvable module")
                            continue
                        design.modules[slot] = picked
                        continue
                    if op in ("<", ">"):
                        design.flags.append(f"operator_slot:{slot}{op}")
                        diag.warn("operator_slot", design.path,
                                  f"slot `{slot}` uses `{op}` (relative module bound); "
                                  f"treated as exactly `{value}`")
                    design.modules[slot] = value
            else:
                design.flags.append("no_modules_block")
                diag.warn("design_without_modules", design.path,
                          "target_variant has no `modules = {}` block; airframe defaults not simulated")

            allowed = dbody.get_block("allowed_modules")
            if allowed is not None:
                design.allowed_modules = allowed.scalars()

            enable = dbody.get_block("enable")
            if enable is not None:
                design.enable_techs = [str(value) for key, _op, value in enable.items()
                                       if key == "has_tech" and not isinstance(value, Node)]

            if dbody.get_block("requirements") is not None:
                design.flags.append("has_requirements")

            _read_priority(design, dbody.get_block("priority"))

            group.designs.append(design)

        if not group.designs:
            diag.warn("empty_design_group", f"{country}/{gname}", "air group with no designs")
        groups.append(group)

    return groups


def discover_countries(ai_equipment_dir: Path, suffix: str = "planes") -> List[str]:
    """Country tags that have a ``<TAG>_<suffix>.txt`` file."""
    tags = []
    marker = f"_{suffix}.txt"
    for p in sorted(ai_equipment_dir.glob(f"*{marker}")):
        tag = p.name.split(marker)[0]
        if tag and tag.upper() == tag:
            tags.append(tag)
    return tags
