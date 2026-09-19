"""[armor-template-generator] Static checks over the compiled selections.

A check that cannot be evaluated reports UNRESOLVED; it never passes by assumption. The width
check in particular refuses to publish a number while the installed doctrine disagrees with the
registry (A9), and names the structural cause when a target misses the target width (A13).
"""

from __future__ import annotations

ERROR, WARN, INFO = "ERROR", "WARN", "INFO"

HEAVY_PREFIXES = ("heavy_tank_chassis", "heavy_tank_destroyer_chassis",
                  "heavy_tank_support_chassis", "heavy_tank_artillery_chassis",
                  "heavy_tank_anti_air_chassis")

# A6: the one heavy component admitted outside a heavy division, and where.
A6_UNIT = "heavy_armor_company_divisional"
A6_FAMILIES = ("medium", "modern")


class Finding(tuple):
    def __new__(cls, level, code, message):
        return super().__new__(cls, (level, code, message))

    level = property(lambda self: self[0])
    code = property(lambda self: self[1])
    message = property(lambda self: self[2])

    def __str__(self):
        return "%-5s %-22s %s" % (self[0], self[1], self[2])


def run(registry, game, per_family_selections, stats):
    findings = []
    findings += _inputs(registry, game)
    for family_id, sels in sorted(per_family_selections.items()):
        findings += _family(registry, game, family_id, sels)
    findings += _codes(per_family_selections)
    findings += _doctrine(registry, game, per_family_selections)
    findings += _growth(registry, stats)
    return findings


def _inputs(registry, game):
    out = []
    for unit in sorted(game.missing_units(registry.referenced_units())):
        out.append(Finding(ERROR, "UNIT-MISSING",
                           "registry names %s, no sub_unit defines it" % unit))
    for trigger in sorted(game.missing_triggers(registry.referenced_triggers())):
        out.append(Finding(ERROR, "TRIGGER-MISSING",
                           "registry names %s, no scripted trigger defines it" % trigger))
    # The heavy chassis contract the upstream bugfix restored: a heavy sub-unit that demands a
    # lighter chassis is a regression, never an authorised exception.
    for uid, unit in sorted(game.units.items()):
        if not uid.startswith("heavy_") or not unit.need:
            continue
        wrong = [k for k in unit.need if k.startswith(("light_", "medium_", "modern_"))]
        if wrong and "fighter" not in uid:
            out.append(Finding(ERROR, "HEAVY-DEMAND",
                               "%s (%s) demands %s" % (uid, unit.source, ", ".join(wrong))))
    return out


def _family(registry, game, family_id, sels):
    out = []
    fam = registry.families[family_id]
    comp = registry.composition
    budget = comp["line_budget"]
    names, gap_reported = set(), False
    mobile_units = set(f["unit"] for f in registry.mobile_infantry.values())

    for sel in sels:
        if sel.name in names:
            out.append(Finding(ERROR, "NAME-COLLISION", "duplicate target name %s" % sel.name))
        names.add(sel.name)

        # slot legality, read from the unit definition rather than from the name
        for section, expected in (("line", "line"), ("regimental", "regimental"),
                                  ("support", "divisional")):
            for unit in getattr(sel, section):
                u = game.unit(unit)
                if u is None:
                    out.append(Finding(ERROR, "UNIT-MISSING",
                                       "%s uses undefined %s" % (sel.name, unit)))
                    continue
                if u.slot != expected:
                    out.append(Finding(ERROR, "SLOT-ILLEGAL",
                                       "%s puts %s (%s) in %s"
                                       % (sel.name, unit, u.slot, section)))

        # A4/A6: heavy equipment only inside the heavy family, one named exception
        if fam["chassis"] != "heavy":
            for unit in sorted(sel.units()):
                u = game.unit(unit)
                if u is None or not u.need:
                    continue
                if any(k.startswith(HEAVY_PREFIXES) for k in u.need):
                    if unit == A6_UNIT and family_id in A6_FAMILIES:
                        continue
                    out.append(Finding(ERROR, "HEAVY-IN-NON-HEAVY",
                                       "%s fields %s, which demands %s"
                                       % (sel.name, unit, sorted(u.need))))
        if A6_UNIT in sel.support and family_id not in A6_FAMILIES:
            out.append(Finding(ERROR, "A6-SCOPE",
                               "%s fields %s outside medium/modern" % (sel.name, A6_UNIT)))

        # counts
        armoured = sum(v for k, v in sel.line.items() if k not in mobile_units)
        expected_line = budget + (comp["waves"]["main_tank_delta"] if sel.facts.waves else 0)
        if armoured != expected_line:
            out.append(Finding(ERROR, "LINE-BUDGET",
                               "%s has %d armoured line battalions, expected %d"
                               % (sel.name, armoured, expected_line)))
        if any(v < 0 for v in sel.line.values()):
            out.append(Finding(ERROR, "NEGATIVE-COUNT", sel.name))

        arty = registry.chains["regimental_artillery"]
        rocket_unit = registry.unit_of(arty["rocket_candidate"], "regimental")
        if sel.regimental.get(rocket_unit, 0) > arty["block_size"]:
            out.append(Finding(ERROR, "ROCKET-CAP", sel.name))
        if sum(sel.regimental.values()) != comp["regimental_slots"] * 2:
            out.append(Finding(ERROR, "REGIMENTAL-BLOCK",
                               "%s fills %d regimental slots, expected %d"
                               % (sel.name, sum(sel.regimental.values()),
                                  comp["regimental_slots"] * 2)))
        if sum(sel.support.values()) > game.divisional_capacity(comp["divisional_slots"]):
            out.append(Finding(ERROR, "DIVISIONAL-OVERFLOW", sel.name))
        if sum(sel.regimental.values()) > game.regimental_capacity(comp["regimental_slots"] * 2):
            out.append(Finding(ERROR, "REGIMENTAL-OVERFLOW", sel.name))

        if sel.notes and not gap_reported:
            out.append(Finding(INFO, "CAPABILITY-GAP", "%s: %s" % (sel.name, "; ".join(sel.notes))))
            gap_reported = True
    return out


def _codes(per_family_selections):
    out, seen = [], {}
    for family_id, sels in sorted(per_family_selections.items()):
        for sel in sels:
            if sel.code in seen:
                out.append(Finding(ERROR, "CODE-COLLISION",
                                   "%d used by %s and %s" % (sel.code, seen[sel.code], sel.name)))
            seen[sel.code] = sel.name
    return out


def _doctrine(registry, game, per_family_selections):
    out = []
    want = registry.composition["waves"]["width_modifier"]
    installed = game.waves_modifiers
    if not installed:
        return [Finding(ERROR, "WAVES-UNRESOLVED",
                        "no combat_width modifier parsed out of the armoured_waves sub-doctrine")]
    wrong = sorted(set(v for v in installed.values() if v != want))
    if wrong:
        out.append(Finding(ERROR, "WAVES-VALUE",
                           "armoured_waves declares %s, the registry requires %+0.1f (A9) - "
                           "patch the doctrine before publishing any width"
                           % (", ".join("%+0.1f" % v for v in wrong), want)))
    needed = set()
    for sels in per_family_selections.values():
        for sel in sels:
            if sel.facts.waves:
                needed.update(sel.line)
    uncovered = sorted(u for u in needed if u not in installed)
    if uncovered:
        out.append(Finding(ERROR, "WAVES-COVERAGE",
                           "the sub-doctrine does not modify %s, so a wave target that fields it "
                           "is wider than its base target" % ", ".join(uncovered)))

    target = registry.composition["target_width"]
    mode = registry.composition.get("variant_block_mode")
    for family_id, sels in sorted(per_family_selections.items()):
        bad = [s for s in sels if abs(s.width - target) > 1e-6]
        if not bad:
            continue
        widths = sorted(set(round(s.width, 2) for s in bad))
        culprits = sorted(set(
            u for s in bad for u in s.line
            if game.unit(u) is not None and game.unit(u).combat_width != 2.0))
        hint = ""
        if mode == "count" and culprits:
            hint = (" - %s is width 3, so a 3-battalion block is 9 width instead of 6; "
                    'composition.variant_block_mode = "width" sizes the block by width and lands '
                    "every target on %s (A13)" % (", ".join(culprits), target))
        out.append(Finding(ERROR, "WIDTH",
                           "%s: %d of %d targets are %s wide instead of %s%s"
                           % (family_id, len(bad), len(sels),
                              "/".join("%g" % w for w in widths), target, hint)))
    return out


def _growth(registry, stats):
    out = []
    for family_id, fam in sorted(registry.families.items()):
        used = stats["per_family"].get(family_id, 0)
        lo, hi = fam["code_range"]
        room = hi - lo + 1
        if used > room:
            out.append(Finding(ERROR, "CODE-BUDGET",
                               "%s needs %d codes, range holds %d" % (family_id, used, room)))
        elif used > room * 0.8:
            out.append(Finding(WARN, "CODE-BUDGET",
                               "%s uses %d of %d codes" % (family_id, used, room)))
    return out
