"""[armor-template-generator] The pure composition resolver and its enumeration.

`resolve(family_id, facts, registry)` is a pure function of declared inputs: no file access, no
game state. `enumerate_family` walks the CATEGORICAL WINNERS the registry declares for a family -
never the cartesian product of raw country booleans - so the emitted target count grows with the
declared axes and is reported before anything is written.

Order of operations (functional spec section 5.1):
    family restriction -> component eligibility -> priority -> quota -> line allocation ->
    Armoured Waves -> regimental/divisional support -> width.
"""

from __future__ import annotations

import itertools

EMPTY = "none"


class Facts:
    """One categorical point of the enumeration: who won each chain, plus the state axes."""

    __slots__ = ("family", "mobile_infantry", "variant", "td", "spaa", "rockets", "quota",
                 "quota_states", "waves", "heavy_company", "arty")

    def __init__(self, family, mobile_infantry, variant, td, spaa, rockets, quota, waves,
                 heavy_company, quota_states=None, arty=EMPTY):
        self.family = family
        self.mobile_infantry = mobile_infantry
        self.variant = variant
        self.td = td
        self.spaa = spaa
        self.rockets = rockets
        self.quota = quota
        # Kept for the explain fixture: the ladder computes the digit from the industrial cut
        # triggers, so one raw quota state = one digit = one code, duplicates included.
        self.quota_states = tuple(quota_states) if quota_states else (quota,)
        self.waves = waves
        self.heavy_company = heavy_company
        # A21: the regimental-artillery chain winner, resolved independently of `variant`.
        self.arty = arty

    def key(self):
        return (self.family, self.mobile_infantry, self.variant, self.td, self.spaa,
                int(self.rockets), self.quota, int(self.waves), int(self.heavy_company),
                self.arty)

    def __repr__(self):
        return "Facts%r" % (self.key(),)


class Selection:
    __slots__ = ("family", "facts", "line", "regimental", "support", "width", "name",
                 "signature", "conditions", "notes", "code", "codes", "profile")

    def __init__(self, family, facts):
        self.family = family
        self.facts = facts
        self.line = {}
        self.regimental = {}
        self.support = {}
        self.width = 0.0
        self.name = None
        self.signature = None
        self.conditions = []
        self.notes = []
        self.code = None
        self.codes = None      # a declared profile may answer several values
        self.profile = None    # the declared profile that produced it, if any

    def units(self):
        out = set(self.line) | set(self.regimental) | set(self.support)
        return out

    def as_dict(self):
        return {
            "name": self.name,
            "code": self.code,
            "family": self.family,
            "facts": list(self.facts.key()),
            "regiments": dict(sorted(self.line.items())),
            "regimental_support": dict(sorted(self.regimental.items())),
            "support": dict(sorted(self.support.items())),
            "width": round(self.width, 3),
            "signature": self.signature,
            "conditions": list(self.conditions),
            "notes": list(self.notes),
        }


class ResolveError(Exception):
    pass


# --------------------------------------------------------------------------- helpers

def _is_spg(candidate_id):
    return candidate_id.endswith("_spg")


def _tiered(registry, family_id):
    """The modern family reads the _tiered eligibility wrappers: only the hull steps up."""
    fam = registry.families[family_id]
    return fam["chassis"] == "modern" or bool(fam.get("mirror_of"))


def quota_states(registry, family_id):
    fam = registry.families[family_id]
    if not fam.get("medium_support_unit"):
        return [0]
    return [q["count"] for q in registry.composition["medium_support_quota"]]


def mobile_forms(registry, family_id):
    del family_id
    return list(registry.mobile_infantry.keys())


# --------------------------------------------------------------------------- resolver

def resolve(family_id, facts, registry, game=None):
    """Pure: Facts -> Selection. `game` is optional and only used for real unit widths."""
    fam = registry.families[family_id]
    comp = registry.composition
    sel = Selection(family_id, facts)

    # 1. family restriction: no heavy component outside the heavy family, with the single
    #    A6 exception handled separately below.
    for chain_id, cid in (("line_variant", facts.variant), ("tank_destroyer", facts.td),
                          ("spaa", facts.spaa), ("regimental_artillery", facts.arty)):
        if cid == EMPTY:
            continue
        klass = registry.candidate(cid)["class"]
        if klass == "heavy" and fam["chassis"] != "heavy":
            raise ResolveError("%s: heavy candidate %s is not admissible in family %s"
                               % (chain_id, cid, family_id))
    if facts.heavy_company and not fam.get("heavy_divisional_company"):
        raise ResolveError("family %s does not admit the A6 heavy divisional company" % family_id)
    # A19: the company needs the declared factory count and a mechanized composition. Below
    # either, the point of the rectangle resolves to the composition WITHOUT the company, so it
    # deduplicates onto that block instead of emitting a target nothing can select.
    gate = comp.get("heavy_company", {})
    mounts_company = facts.heavy_company
    if mounts_company and gate.get("mechanized_only") and facts.mobile_infantry != "mechanized":
        mounts_company = False
    if mounts_company and gate.get("min_military_factories") is not None:
        bands = [q["count"] for q in comp["medium_support_quota"]]
        if fam.get("medium_support_unit") and facts.quota != bands[-1]:
            mounts_company = False

    # 2/3. line allocation (A11): the variant block replaces medium support first, then tanks.
    budget = comp["line_budget"]
    infantry = comp["mobile_infantry"]
    block = comp["variant_block"]

    s0 = facts.quota if fam.get("medium_support_unit") else 0
    variant_count = variant_block_count(registry, facts.variant, game, block)
    support_count = max(0, s0 - variant_count)
    main_count = budget - support_count - variant_count
    if main_count < 0:
        raise ResolveError("negative main-tank count for %r" % (facts,))

    # 4. Armoured Waves (A9): flat +0.5 per battalion, -1 tank and -2 mechanized.
    if facts.waves:
        main_count += comp["waves"]["main_tank_delta"]
        if (facts.mobile_infantry == "mechanized"
                or comp["waves"].get("applies_to_motorized")):
            infantry += comp["waves"]["mechanized_delta"]
        if main_count < 0 or infantry < 0:
            raise ResolveError("Armoured Waves produced a negative count for %r" % (facts,))

    def add(mapping, unit, count):
        if unit is None or count <= 0:
            return
        mapping[unit] = mapping.get(unit, 0) + count

    add(sel.line, fam["main_tank"], main_count)
    add(sel.line, fam.get("medium_support_unit"), support_count)
    if facts.variant != EMPTY:
        unit = registry.unit_of(facts.variant, "line")
        if unit is None:
            raise ResolveError("line variant %s has no line unit" % facts.variant)
        add(sel.line, unit, variant_count)
    add(sel.line, registry.mobile_infantry[facts.mobile_infantry]["unit"], infantry)

    # 5. regimental support: one tank-destroyer block, one artillery block, each sized by the
    #    columns the line can actually form.
    slots_per_row = regimental_columns(sum(sel.line.values()), game, registry)
    td_chain = registry.chains["tank_destroyer"]
    td_unit = (registry.unit_of(facts.td, "regimental") if facts.td != EMPTY
               else registry.unit_of(td_chain["empty"], "regimental"))
    if td_unit is None:
        raise ResolveError("tank destroyer %s has no regimental unit" % facts.td)
    add(sel.regimental, td_unit, slots_per_row)

    arty = registry.chains["regimental_artillery"]
    slots = slots_per_row
    # A8/A21: the artillery block is the REGIMENTAL chain's own winner, never a by-product of
    # the line winner. The two chains share a candidate set and a rank order, so whenever the
    # line winner owns a regimental company it also wins here - but a line winner that owns
    # none (infantry support, heavy SPG) no longer takes the block away from the assault gun
    # below it. enumerate_family only ever builds pairs that one eligibility set can produce.
    spg_unit = None
    if facts.arty != EMPTY:
        spg_unit = registry.unit_of(facts.arty, "regimental")
        if spg_unit is None:
            raise ResolveError("artillery winner %s has no regimental unit" % facts.arty)
        if facts.arty != facts.variant:
            sel.notes.append(
                "regimental artillery %s resolved apart from the line variant %s"
                % (facts.arty, facts.variant))
    rocket_unit = registry.unit_of(arty["rocket_candidate"], "regimental")
    if spg_unit and facts.rockets:
        cap = arty["rocket_cap"]
        add(sel.regimental, rocket_unit, cap)
        add(sel.regimental, spg_unit, slots - cap)
    elif spg_unit:
        add(sel.regimental, spg_unit, slots)
    elif facts.rockets:
        add(sel.regimental, rocket_unit, slots)
    else:
        add(sel.regimental, registry.unit_of(arty["empty"], "regimental"), slots)

    # 6. divisional support spine, capped by the declared slot count.
    for entry in registry.support_spine:
        unit = None
        if "unit" in entry:
            unit = entry["unit"]
            if entry.get("replaced_by_heavy_company") and mounts_company:
                unit = registry.unit_of("heavy_divisional_company", "divisional")
        elif "chassis_map" in entry:
            unit = entry["chassis_map"].get(fam["chassis"])
            if unit is None:
                raise ResolveError("support %s has no unit for chassis %s"
                                   % (entry["id"], fam["chassis"]))
        elif "chain" in entry:
            chain_id = entry["chain"]
            cid = {"spaa": facts.spaa, "line_variant": facts.variant}[chain_id]
            if cid == EMPTY:
                cid = registry.chains[chain_id]["empty"] if not entry.get("optional") else None
            if cid is not None:
                unit = registry.unit_of(cid, "divisional")
                if unit is None and not entry.get("optional"):
                    raise ResolveError("%s has no divisional unit for %s" % (chain_id, cid))
        if unit:
            add(sel.support, unit, 1)

    capacity = comp["divisional_slots"]
    used = sum(sel.support.values())
    if used > capacity:
        raise ResolveError("divisional support overflow: %d > %d for %r" % (used, capacity, facts))

    reg_used = sum(sel.regimental.values())
    if reg_used > comp["regimental_slots"] * 2:
        raise ResolveError("regimental support overflow: %d for %r" % (reg_used, facts))

    # 7. width, from the declared flat modifier (validate.py checks it against the doctrine).
    per = comp["battalion_width"]
    bonus = comp["waves"]["width_modifier"] if facts.waves else 0.0
    assumed = comp.get("width_assumptions", {}).get("subdoctrines", [])
    if game is not None:
        total = 0.0
        for unit, count in sel.line.items():
            u = game.unit(unit)
            base = u.combat_width if u is not None else per
            # Sub-doctrines the AI is assumed to hold change the battalion's real width; the
            # registry names them, validate.py reports them, nothing here guesses.
            total += count * (base + game.assumed_width_delta(unit, assumed) + bonus)
    else:
        total = sum(sel.line.values()) * (per + bonus)
    sel.width = total

    sel.name = compose_name(registry, family_id, facts, game)
    sel.signature = signature(sel)
    sel.conditions = conditions(registry, family_id, facts)
    return sel


def signature(sel):
    def part(mapping):
        return ",".join("%s=%d" % kv for kv in sorted(mapping.items()))
    return "|".join((sel.family, part(sel.line), part(sel.regimental), part(sel.support)))


SHORT = {
    "light_assault": "LASS", "medium_assault": "MASS", "heavy_assault": "HASS",
    "light_inf_support": "LISP", "medium_inf_support": "MISP", "heavy_inf_support": "HISP",
    "light_spg": "LSPG", "medium_spg": "MSPG", "modern_spg": "XSPG", "heavy_spg": "HSPG",
    "mechanized_td": "ETD", "light_td": "LTD", "medium_td": "MTD", "modern_td": "XTD",
    "heavy_td": "HTD",
    "light_spaa": "LAA", "medium_spaa": "MAA", "modern_spaa": "XAA",
}


def compose_name(registry, family_id, facts, game=None):
    fam = registry.families[family_id]
    parts = ["WA_AI_TEMPLATES_GENERIC", fam["name_token"],
             str(registry.composition["target_width"]),
             registry.mobile_infantry[facts.mobile_infantry]["tag"]]
    if fam.get("medium_support_unit"):
        # Both the industrial band and the resulting battalion count: two bands can resolve to
        # the same count, and two targets may not share a name.
        bands = [q["count"] for q in registry.composition["medium_support_quota"]]
        parts.append("F%d" % bands.index(facts.quota))
        used = variant_block_count(registry, facts.variant, game,
                                   registry.composition["variant_block"])
        support = max(0, facts.quota - used)
        if support:
            parts.append("S%d" % support)
    for cid in (facts.variant, facts.td, facts.spaa):
        if cid != EMPTY:
            parts.append(SHORT[cid])
    if facts.arty != EMPTY and facts.arty != facts.variant:
        parts.append("R" + SHORT[facts.arty])
    if facts.rockets:
        parts.append("ROC")
    if facts.heavy_company:
        parts.append("HSUP")
    if facts.waves:
        parts.append("WAVES")
    return "_".join(parts)


def conditions(registry, family_id, facts):
    """The exact trigger terms the generated ladder tests for this composition."""
    fam = registry.families[family_id]
    comp = registry.composition
    out = [("yes", fam["admission"])]
    if fam.get("extra_admission"):
        out.append(("yes", fam["extra_admission"]))
    elif fam["chassis"] == "medium":
        # The medium hull owns the role only while the modern latch is closed.
        for other in registry.families.values():
            if other.get("mirror_of") == family_id and other.get("extra_admission"):
                out.append(("no", other["extra_admission"]))

    mech = registry.mobile_infantry["mechanized"]["eligibility"]
    out.append(("yes" if facts.mobile_infantry == "mechanized" else "no", mech))

    chains_named = [("line_variant", facts.variant), ("tank_destroyer", facts.td),
                    ("spaa", facts.spaa)]
    if "regimental_artillery" in fam.get("enumerate", {}):
        chains_named.append(("regimental_artillery", facts.arty))
    for chain_id, cid in chains_named:
        out.append(("yes", wins_trigger_name(family_id, chain_id, cid)))

    rockets = registry.candidate("mechanized_rockets")["eligibility"]
    out.append(("yes" if facts.rockets else "no", rockets))

    out.extend(industrial_conditions(registry, family_id, facts.quota, facts.heavy_company))

    waves = "WA_AI_TEMPLATES_use_armoured_waves_templates"
    out.append(("yes" if facts.waves else "no", waves))
    return out


def industrial_conditions(registry, family_id, quota, company):
    """The terms of one value of the merged industrial axis.

    The three bands are ordered, so the two cut triggers name each one; the company sits on the
    top band alone and adds its own latch and its own factory cut.
    """
    fam = registry.families[family_id]
    out = []
    if fam.get("medium_support_unit"):
        out.extend(quota_conditions(registry, quota))
    if not fam.get("heavy_divisional_company"):
        return out
    gate = registry.composition.get("heavy_company", {})
    latch = registry.candidate("heavy_divisional_company")["eligibility"]
    out.append(("yes" if company else "no", latch))
    if gate.get("trigger"):
        out.append(("no" if company else "yes", gate["trigger"]))
    return out


def quota_conditions(registry, quota):
    """The industrial terms of one quota state. The three states are ordered, so the two cut
    triggers name each one exactly."""
    triggers = registry.composition["quota_triggers"]
    first, second = triggers["6"], triggers["3"]
    if quota == 6:
        return [("yes", first)]
    if quota == 3:
        return [("no", first), ("yes", second)]
    return [("no", second)]


def wins_trigger_name(family_id, chain_id, candidate_id):
    return "WA_AI_TEMPLATES_ARMOR_%s_wins_%s_%s" % (family_id, chain_id, candidate_id)


# --------------------------------------------------------------------- enumeration

AXIS_ORDER = ("variant_arty", "td", "spaa", "rockets", "industrial", "waves")


def variant_arty_pairs(registry, family_id, form):
    """The (line winner, artillery winner) pairs ONE eligibility set can actually produce.

    A21: the two chains are resolved independently but read the same candidates under the same
    rank order, so most combinations are arithmetically impossible - a candidate that outranks
    the line winner cannot be eligible, or it would have won the line. Enumerating the pairs
    instead of a rectangle is what keeps the code count at 11 values for medium rather than 35,
    and it is why the joint axis exists at all. A pair is reachable when the minimal eligibility
    set {v, a} reproduces both winners.
    """
    enum = registry.families[family_id]["enumerate"]
    line = list(enum.get("line_variant", []))
    arty = list(enum.get("regimental_artillery", []))
    drop = registry.composition.get("motorized_plane", {}).get("drop_axes", [])
    rank = lambda cid: registry.candidate(cid).get("chain_rank", 0)   # noqa: E731

    def top(members, pool):
        chosen = [c for c in members if c in pool]
        return max(chosen, key=rank) if chosen else EMPTY

    if form != "mechanized" and "variant" in drop:
        # The motorized plane drops the LINE variant only: the registry keeps its regimental
        # axes, and the artillery block is one of them. No coupling to reproduce.
        return [(EMPTY, a) for a in [EMPTY] + arty]

    pairs = []
    for v in [EMPTY] + line:
        for a in [EMPTY] + arty:
            members = [c for c in (v, a) if c != EMPTY]
            if top(members, line) == v and top(members, arty) == a:
                pairs.append((v, a))
    return pairs


def variant_block_count(registry, variant_id, game, default):
    """How many battalions the assault / infantry-support / SPG block holds.

    mode 'count' keeps the screenshot's 3 battalions whatever their width; mode 'width' keeps the
    block's WIDTH and lets a width-3 SPG battalion take 2 slots instead of 3 (A13).
    """
    if variant_id == EMPTY:
        return 0
    comp = registry.composition
    if comp.get("variant_block_mode") != "width":
        return default
    unit = registry.unit_of(variant_id, "line")
    width = comp["battalion_width"]
    if game is not None and game.unit(unit) is not None:
        width = game.unit(unit).combat_width or width
    return max(1, int(round(comp.get("variant_block_width", default * width) / width)))


class Plane:
    """One rectangular sub-space of a family's codes: a mobile-infantry form and its axes."""

    __slots__ = ("family", "form", "axes", "base", "strides", "size")

    def __init__(self, family, form, axes, base):
        self.family = family
        self.form = form
        self.axes = axes
        self.base = base
        self.strides = {}
        stride = 1
        for name, values in reversed(axes):
            self.strides[name] = stride
            stride *= len(values)
        self.size = stride

    def code(self, digits):
        return self.base + sum(self.strides[name] * index for name, index in digits.items())


def axis_values(registry, family_id, axis, form):
    fam = registry.families[family_id]
    enum = fam["enumerate"]
    comp = registry.composition
    # The motorized plane carries a declared subset of the axes: see composition.motorized_plane.
    if (form != "mechanized" and axis != "variant_arty"
            and axis in comp.get("motorized_plane", {}).get("drop_axes", [])):
        return [EMPTY] if axis in ("variant", "td", "spaa") else [False]
    if axis == "variant_arty":
        return variant_arty_pairs(registry, family_id, form)
    if axis == "td":
        return [EMPTY] + list(enum.get("tank_destroyer", []))
    if axis == "spaa":
        return [EMPTY] + list(enum.get("spaa", []))
    if axis == "rockets":
        return [False, True] if enum.get("rockets") else [False]
    if axis == "industrial":
        # ONE axis for the industrial state, because the two halves never cross: the heavy
        # company exists only at the top band (A19). A 3 x 2 rectangle would spend a third of
        # its points on combinations the ladder can never write. Each value is a (support
        # quota, mounts the company) pair.
        bands = ([q["count"] for q in comp["medium_support_quota"]]
                 if fam.get("medium_support_unit") else [0])
        values = [(band, False) for band in bands]
        gate = comp.get("heavy_company", {})
        if (fam.get("heavy_divisional_company")
                and not (gate.get("mechanized_only") and form != "mechanized")):
            values.append((bands[-1], True))
        return values
    if axis == "waves":
        if not fam.get("waves"):
            return [False]
        if form != "mechanized" and not comp["waves"].get("applies_to_motorized"):
            # A9/A14: the wave transform subtracts mechanized battalions, so the motorized
            # plane carries no wave twin and a motorized country keeps its base target.
            return [False]
        return [False, True]
    raise ResolveError("unknown axis %s" % axis)


def build_planes(registry, family_id):
    lo, _hi = registry.families[family_id]["code_range"]
    planes, base = [], lo
    for form in registry.mobile_infantry:
        axes = [(axis, axis_values(registry, family_id, axis, form)) for axis in AXIS_ORDER]
        plane = Plane(family_id, form, axes, base)
        planes.append(plane)
        base += plane.size
    return planes


def enumerate_family(family_id, registry, game=None):
    """Every composition of a family, its dense code, and whatever could not be resolved."""
    fam = registry.families[family_id]
    lo, hi = fam["code_range"]
    planes = build_planes(registry, family_id)
    total = sum(p.size for p in planes)
    if lo + total - 1 > hi:
        raise ResolveError(
            "family %s needs %d codes, range %d-%d holds %d - widen the declared range or "
            "drop an enumerated axis" % (family_id, total, lo, hi, hi - lo + 1))

    selections, errors = [], []
    for plane in planes:
        names = [a[0] for a in plane.axes]
        for combo in itertools.product(*[range(len(a[1])) for a in plane.axes]):
            digits = dict(zip(names, combo))
            chosen = dict((name, plane.axes[i][1][combo[i]]) for i, name in enumerate(names))
            quota, company = chosen["industrial"]
            variant, arty = chosen["variant_arty"]
            facts = Facts(family_id, plane.form, variant, chosen["td"],
                          chosen["spaa"], chosen["rockets"], quota,
                          chosen["waves"], company, arty=arty)
            try:
                sel = resolve(family_id, facts, registry, game)
            except ResolveError as exc:
                errors.append((facts.key(), str(exc)))
                continue
            sel.code = plane.code(digits)
            selections.append(sel)
    selections.sort(key=lambda s: s.code)
    return selections, errors, planes



def regimental_columns(line_battalions, game, registry):
    """How many regimental-support companies fit per row, from the engine's own geometry.

    MEASURED (common/defines/05_defines.lua): MAX_REGIMENTAL_SUPPORT_WIDTH = 5 columns,
    MAX_REGIMENTAL_SUPPORT_HEIGHT = 2 rows, and REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS = {3, 3} -
    "for each regimental support row, how many battalions are required in the REGIMENT to place a
    support in that row". AI_BATTALION_BUILD_ORDER fills a column three deep before opening the
    next, so N battalions open floor(N / 3) columns, capped at 5. A block wider than that has
    companies the designer can never place: 15 battalions carry 5 + 5, 12 carry only 4 + 4.
    """
    required = 3
    width = 5
    if game is not None:
        required = (game.defines.get("REGIMENTAL_SUPPORT_REQUIRED_BATTALIONS") or [3])[0]
        width = game.defines.get("REGIMENTAL_SUPPORT_WIDTH", 5)
    declared = registry.composition["regimental_slots"]
    return max(0, min(declared, width, line_battalions // max(1, required)))


# ------------------------------------------------------------------ declared profiles

def resolve_profile(registry, family_id, profile, game=None):
    """One declared target: either resolved from `facts` like any other, or taken verbatim.

    Verbatim is for the shapes that are NOT a composition - a conversion blend, a mission corps,
    a starter park. Running them through the resolver would silently rewrite the state machine
    the conversion chain depends on.
    """
    if "facts" in profile:
        f = profile["facts"]
        variant = f.get("variant", EMPTY)
        # A declared profile states its artillery winner only when it differs from the line
        # winner. The default is the pre-A21 derivation, so every hand-declared target keeps
        # the composition it had.
        default_arty = (variant if variant != EMPTY
                        and registry.unit_of(variant, "regimental") else EMPTY)
        facts = Facts(family_id, f.get("mobile_infantry", "mechanized"), variant,
                      f.get("td", EMPTY), f.get("spaa", EMPTY), bool(f.get("rockets")),
                      int(f.get("quota", 0)), bool(f.get("waves")), bool(f.get("heavy_company")),
                      arty=f.get("arty", default_arty))
        sel = resolve(family_id, facts, registry, game)
    else:
        facts = Facts(family_id, "motorized", EMPTY, EMPTY, EMPTY, False, 0, False, False,
                      arty=EMPTY)
        sel = Selection(family_id, facts)
        sel.line = dict(profile.get("regiments", {}))
        sel.regimental = dict(profile.get("regimental_support", {}))
        sel.support = dict(profile.get("support", {}))
        per = registry.composition["battalion_width"]
        assumed = registry.composition.get("width_assumptions", {}).get("subdoctrines", [])
        total = 0.0
        for unit, count in sel.line.items():
            base = per
            if game is not None and game.unit(unit) is not None:
                base = game.unit(unit).combat_width
            total += count * (base + (game.assumed_width_delta(unit, assumed) if game else 0.0))
        sel.width = total
        sel.signature = signature(sel)
    sel.name = profile["id"]
    sel.codes = list(profile.get("codes", []))
    sel.code = sel.codes[0] if sel.codes else None
    sel.profile = profile
    return sel


def declared_profiles(registry, family_id, game=None):
    fam = registry.families[family_id]
    return [resolve_profile(registry, family_id, p, game)
            for p in fam.get("profiles", []) if p.get("emit", True)]
