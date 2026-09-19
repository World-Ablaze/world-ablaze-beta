"""[armor-template-generator] Read-only adapters over the game files the generator depends on.

Nothing here writes. Every record carries the file it came from, so a validation error can name
the source instead of a guess. Unit existence, slot legality and equipment demand are READ, never
inferred from the unit's name.

Sources
    common/units/*.txt                      sub-unit definitions (group/divisional/regimental,
                                            combat_width, need)
    common/scripted_triggers/WA_AI_*.txt    the eligibility triggers the registry references
    common/doctrines/subdoctrines/land/     the Armoured Waves width modifier (A9)
    common/defines/05_defines.lua           support-slot geometry
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_MARKER = "descriptor.mod"


def _import_pdx(repo_root: Path):
    """Reuse tools/equipment_evaluator/pdx.py through sys.path, read-only."""
    tools = str(Path(repo_root) / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    from equipment_evaluator import pdx  # noqa: E402  (deliberate late import)

    return pdx


class Unit:
    __slots__ = ("id", "source", "group", "divisional", "regimental", "combat_width", "need",
                 "categories", "active")

    def __init__(self, uid, source):
        self.id = uid
        self.source = source
        self.group = None
        self.divisional = False
        self.regimental = False
        self.combat_width = 0.0
        self.need = {}
        self.categories = ()
        self.active = True

    @property
    def slot(self):
        """line / divisional / regimental, as the engine reads the definition."""
        if self.group == "support":
            if self.divisional:
                return "divisional"
            if self.regimental:
                return "regimental"
            return "support"
        return "line"

    def demands_class(self, prefix):
        return any(k.startswith(prefix) for k in self.need)

    def __repr__(self):
        return "<Unit %s %s w=%s>" % (self.id, self.slot, self.combat_width)


class GameFiles:
    """Everything the generator reads out of the mod, parsed once."""

    def __init__(self, repo_root: Path):
        self.root = Path(repo_root)
        self.pdx = _import_pdx(self.root)
        self.units = {}
        self.triggers = {}
        self.effects = {}
        self.waves_modifiers = {}
        self.subdoctrine_widths = {}
        self.subdoctrine_source = {}
        self.defines = {}
        self._load_units()
        self._load_triggers()
        self._load_waves()
        self._load_defines()

    # ------------------------------------------------------------------ units
    def _load_units(self):
        for path in sorted((self.root / "common" / "units").glob("*.txt")):
            try:
                tree = self.pdx.parse_file(path)
            except Exception:  # a names/ file or anything else this parser dislikes
                continue
            sub = tree.get_block("sub_units")
            if sub is None:
                continue
            for uid, body in sub.named_blocks():
                unit = Unit(uid, str(path.relative_to(self.root)))
                unit.group = body.get_str("group")
                unit.divisional = body.get_bool("divisional")
                unit.regimental = body.get_bool("regimental")
                unit.combat_width = body.get_float("combat_width", 0.0) or 0.0
                unit.active = body.get_bool("active", True)
                need = body.get_block("need")
                if need is not None:
                    unit.need = dict(
                        (k, float(v)) for k, _, v in need.items()
                        if isinstance(v, str) and k is not None
                    )
                cats = body.get_block("categories")
                if cats is not None:
                    unit.categories = tuple(cats.scalars())
                if uid in self.units:
                    # Last definition wins in the engine; keep it but remember the collision.
                    pass
                self.units[uid] = unit

    # --------------------------------------------------------------- triggers
    def _load_triggers(self):
        pattern = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*)\s*=\s*\{", re.M)
        for folder, into in (("scripted_triggers", self.triggers),
                             ("scripted_effects", self.effects)):
            for path in sorted((self.root / "common" / folder).glob("*.txt")):
                text = path.read_text(encoding="utf-8-sig", errors="replace")
                for m in pattern.finditer(text):
                    into.setdefault(m.group(1), str(path.relative_to(self.root)))

    # ----------------------------------------------------------- sub-doctrines
    def _load_waves(self):
        """Every land sub-doctrine's per-unit combat_width modifier, keyed by sub-doctrine.

        A division's real width is its battalions' base width plus whatever sub-doctrines the
        country holds, so reading base widths alone gets armour wrong: pre_assault_bombardment
        alone takes 1 off every self-propelled gun battalion.
        """
        folder = self.root / "common" / "doctrines" / "subdoctrines" / "land"
        unit_mod = re.compile(r"([a-z_0-9]+)\s*=\s*\{[^{}]*?combat_width\s*=\s*(-?[\d.]+)")
        for path in sorted(folder.glob("*.txt")):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            for m in re.finditer(r"\n\s*([a-z_0-9]+)\s*=\s*\{", text):
                name = m.group(1)
                open_at = text.index("{", m.end() - 1)
                depth, end = 0, len(text)
                for i in range(open_at, len(text)):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            end = i
                            break
                body = text[open_at:end]
                if "combat_width" not in body:
                    continue
                mods = dict((u.group(1), float(u.group(2))) for u in unit_mod.finditer(body))
                if mods:
                    self.subdoctrine_widths[name] = mods
                    self.subdoctrine_source[name] = str(path.relative_to(self.root))
        self.waves_modifiers = self.subdoctrine_widths.get("armoured_waves", {})

    def assumed_width_delta(self, unit_id, subdoctrines):
        """Total combat_width modifier a unit gets from the named sub-doctrines."""
        return sum(self.subdoctrine_widths.get(name, {}).get(unit_id, 0.0)
                   for name in subdoctrines)

    # --------------------------------------------------------------- defines
    def _load_defines(self):
        path = self.root / "common" / "defines" / "05_defines.lua"
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for key in ("DIVISIONAL_SUPPORT_WIDTH", "DIVISIONAL_SUPPORT_HEIGHT",
                    "REGIMENTAL_SUPPORT_WIDTH", "REGIMENTAL_SUPPORT_HEIGHT"):
            m = re.search(key + r"\s*=\s*(\d+)", text)
            if m:
                self.defines[key] = int(m.group(1))
        m = re.search(r"REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS\s*=\s*\{([^}]*)\}", text)
        if m:
            self.defines["REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS"] = [
                int(x) for x in re.findall(r"\d+", m.group(1))
            ]

    # ---------------------------------------------------------------- lookups
    def unit(self, uid):
        return self.units.get(uid)

    def missing_units(self, ids):
        return sorted(u for u in ids if u not in self.units)

    def missing_triggers(self, names):
        return sorted(n for n in names if n not in self.triggers)

    def divisional_capacity(self, default=10):
        w = self.defines.get("DIVISIONAL_SUPPORT_WIDTH")
        h = self.defines.get("DIVISIONAL_SUPPORT_HEIGHT")
        return w * h if w and h else default

    def regimental_capacity(self, default=10):
        w = self.defines.get("REGIMENTAL_SUPPORT_WIDTH")
        h = self.defines.get("REGIMENTAL_SUPPORT_HEIGHT")
        return w * h if w and h else default
