"""[armor-template-generator] Rendering: ai_template files, the selection ladders, the
generated decision predicates and the manifest.

Everything here is a pure function of the compiled selections, so `--check` can compare bytes.
Output is tab-indented, LF, UTF-8 without BOM (editing rule 16).
"""

from __future__ import annotations

import json

from . import resolve as R

MARKER = "[armor-template-generator]"
TAB = "\t"


def _header(source_note):
    return (
        "############################################################################################################\n"
        "# GENERATED FILE - DO NOT EDIT. %s\n"
        "# Source : tools/armor_templates_registry.json\n"
        "# Writer : tools/gen/gen_ai_armor_templates.py\n"
        "# %s\n"
        "############################################################################################################\n"
        % (MARKER, source_note)
    )


# --------------------------------------------------------------------- templates

def family_file(registry, family_id, selections, game=None):
    fam = registry.families[family_id]
    out = [_header("Composition targets for the %s armour family." % family_id)]
    out.append("\n%s = {\n" % fam["role_group"])
    out.append("%srole = %s\n" % (TAB, fam["role"]))
    override = fam.get("front_role_override")
    if override:
        # The engine keys front assignment on `role = armor` or this override (defines
        # ASSIGN_TANKS_TO_WAR_FRONT). WA uses granular role tokens, so a role group without the
        # line has every front_armor_score entry go inert and its divisions distributed like
        # infantry. Declared per family in the registry, never inferred from the role name.
        out.append("%sfront_role_override = %s\n" % (TAB, override))
    out.append("%supgrade_prio = {\n" % TAB)
    out.append("%sbase = 100\n" % (TAB * 2))
    out.append("%s# [dead-role-entry] A role entry whose targets are all disabled still wins the\n"
               % (TAB * 2))
    out.append("%s# engine's role lottery and becomes an army-XP sink; both modifiers below take\n"
               % (TAB * 2))
    out.append("%s# its weight to zero when no target of this file can be selected.\n"
               % (TAB * 2))
    out.append("%smodifier = {\n%sfactor = 0\n%sNOT = { has_country_flag = %s }\n%s}\n"
               % (TAB * 2, TAB * 3, TAB * 3, fam["flag"], TAB * 2))
    extra = fam.get("extra_admission")
    if extra:
        out.append("%smodifier = {\n%sfactor = 0\n%sNOT = { %s = yes }\n%s}\n"
                   % (TAB * 2, TAB * 3, TAB * 3, extra, TAB * 2))
    else:
        for other in registry.families.values():
            if other.get("mirror_of") == family_id and other.get("extra_admission"):
                out.append("%smodifier = {\n%sfactor = 0\n%s%s = yes\n%s}\n"
                           % (TAB * 2, TAB * 3, TAB * 3, other["extra_admission"], TAB * 2))
    out.append("%s}\n" % TAB)

    for sel in selections:
        out.append(_target_block(registry, fam, sel))
    out.append("}\n")
    return "".join(out)


def _target_block(registry, fam, sel):
    lines = ["\n%s%s = {\n" % (TAB, sel.name)]
    lines.append("%senable = { has_country_flag = { flag = %s value = %d } }\n"
                 % (TAB * 2, fam["flag"], sel.code))
    lines.append("%sreinforce_prio = 1\n" % (TAB * 2))
    lines.append("%scustom_icon = %d\n" % (TAB * 2, fam.get("custom_icon", 140)))
    lines.append("%scan_upgrade_in_field = { always = yes }\n" % (TAB * 2))
    lines.append("%supgrade_prio = { base = 10 }\n" % (TAB * 2))
    lines.append("%starget_template = {\n" % (TAB * 2))
    for section, mapping in (("regiments", sel.line),
                             ("regimental_support", sel.regimental),
                             ("support", sel.support)):
        lines.append("%s%s = {\n" % (TAB * 3, section))
        for unit, count in sorted(mapping.items()):
            lines.append("%s%s = %d\n" % (TAB * 4, unit, count))
        lines.append("%s}\n" % (TAB * 3))
    lines.append("%s}\n" % (TAB * 2))
    lines.append("%s}\n" % TAB)
    return "".join(lines)


# ----------------------------------------------------------------------- ladders

SCRATCH = "_wa_ag_digit"


def effects_file(registry, groups, planes_by_family):
    """One calculation effect per template flag.

    The value is COMPUTED, not looked up: each declared axis contributes one digit of a
    mixed-radix code, so a family costs one test per axis value instead of one conjunction per
    target. A flat ladder of every target would be thousands of trigger evaluations per country
    per monthly pulse.
    """
    out = [_header("Selection ladders. The template value is a mixed-radix code: one digit per "
                   "declared axis, dense inside each family's range.")]
    for group_name, families in groups:
        out.append("\n%s = {\n" % group_name)
        first = registry.families[families[0]]
        out.append("%sset_temp_variable = { _template_type_code = %d }\n"
                   % (TAB, first["type_code"]))
        out.append("%sset_temp_variable = { _template_value = 0 }\n" % TAB)
        out.append("%sset_temp_variable = { _template_claimed = 0 }\n" % TAB)
        out.append("%sset_temp_variable = { %s = 0 }\n" % (TAB, SCRATCH))
        for family_id in families:
            out.append(_family_branch(registry, family_id, planes_by_family[family_id]))
        out.append("%sclear_temp_variable = %s\n" % (TAB, SCRATCH))
        out.append("%sWA_AI_TEMPLATES_update_target_template = yes\n" % TAB)
        out.append("}\n")
    return "".join(out)


def _family_gate(registry, family_id):
    fam = registry.families[family_id]
    terms = [("yes", fam["admission"])]
    if fam.get("extra_admission"):
        terms.append(("yes", fam["extra_admission"]))
    else:
        for other in registry.families.values():
            if other.get("mirror_of") == family_id and other.get("extra_admission"):
                terms.append(("no", other["extra_admission"]))
    return terms


def _terms(terms, depth):
    out = []
    for polarity, trigger in terms:
        if polarity == "yes":
            out.append("%s%s = yes\n" % (TAB * depth, trigger))
        else:
            out.append("%sNOT = { %s = yes }\n" % (TAB * depth, trigger))
    return "".join(out)


def _family_branch(registry, family_id, planes):
    fam = registry.families[family_id]
    lines = ["\n%s# %s: codes %d-%d\n"
             % (TAB, family_id, planes[0].base, planes[-1].base + planes[-1].size - 1)]
    lines.append("%sif = {\n%slimit = {\n" % (TAB, TAB * 2))
    lines.append("%scheck_variable = { _template_claimed = 0 }\n" % (TAB * 3))
    lines.append(_terms(_family_gate(registry, family_id), 3))
    lines.append("%s}\n" % (TAB * 2))
    mech = registry.mobile_infantry["mechanized"]["eligibility"]
    for index, plane in enumerate(planes):
        opener = "if" if index == 0 else "else_if" if index < len(planes) - 1 else "else"
        if opener == "else":
            lines.append("%selse = {\n" % (TAB * 2))
        else:
            polarity = "yes" if plane.form == "mechanized" else "no"
            lines.append("%s%s = {\n%slimit = {\n%s%s\n%s}\n"
                         % (TAB * 2, opener, TAB * 3,
                            TAB * 4,
                            "%s = yes" % mech if polarity == "yes"
                            else "NOT = { %s = yes }" % mech, TAB * 3))
        lines.append("%s# %s plane, %d codes\n" % (TAB * 3, plane.form, plane.size))
        lines.append("%sset_temp_variable = { _template_value = %d }\n" % (TAB * 3, plane.base))
        for axis, values in plane.axes:
            lines.append(_digit_block(registry, family_id, axis, values,
                                      plane.strides[axis], 3))
        lines.append("%s}\n" % (TAB * 2))
    lines.append("%sset_temp_variable = { _template_claimed = 1 }\n" % (TAB * 2))
    lines.append("%s}\n" % TAB)
    return "".join(lines)


def _digit_block(registry, family_id, axis, values, stride, depth):
    if len(values) < 2:
        return ""
    lines = ["%s# %s\n" % (TAB * depth, axis)]
    lines.append("%sset_temp_variable = { %s = 0 }\n" % (TAB * depth, SCRATCH))
    for index, value in enumerate(values):
        if index == 0:
            continue
        terms = _axis_terms(registry, family_id, axis, value)
        lines.append("%sif = {\n%slimit = {\n" % (TAB * depth, TAB * (depth + 1)))
        lines.append(_terms(terms, depth + 2))
        lines.append("%s}\n" % (TAB * (depth + 1)))
        lines.append("%sset_temp_variable = { %s = %d }\n" % (TAB * (depth + 1), SCRATCH, index))
        lines.append("%s}\n" % (TAB * depth))
    if stride != 1:
        lines.append("%smultiply_temp_variable = { %s = %d }\n" % (TAB * depth, SCRATCH, stride))
    lines.append("%sadd_to_temp_variable = { _template_value = %s }\n" % (TAB * depth, SCRATCH))
    return "".join(lines)


def _axis_terms(registry, family_id, axis, value):
    """The trigger terms that select one value of one axis. Values are mutually exclusive."""
    if axis in ("variant", "td", "spaa"):
        chain = {"variant": "line_variant", "td": "tank_destroyer", "spaa": "spaa"}[axis]
        return [("yes", R.wins_trigger_name(family_id, chain, value))]
    if axis == "rockets":
        return [("yes", registry.candidate("mechanized_rockets")["eligibility"])]
    if axis == "quota":
        return R.quota_conditions(registry, value)
    if axis == "company":
        return [("yes", registry.candidate("heavy_divisional_company")["eligibility"])]
    if axis == "waves":
        return [("yes", "WA_AI_TEMPLATES_use_armoured_waves_templates")]
    raise ValueError("unknown axis %s" % axis)


# ---------------------------------------------------------------------- triggers

def triggers_file(registry, per_family_selections, max_or_terms=64):
    out = [_header("Decision predicates: which candidate wins its chain, the industrial cuts, "
                   "and the semantic code sets.")]

    quota = registry.composition
    cuts = quota["medium_support_quota"]
    trig = quota["quota_triggers"]
    out.append("\n# Industrial cuts of the medium-support quota (%s).\n"
               % ", ".join("%s below %s factories" % (c["count"], c["below_military_factories"])
                           for c in cuts if c["below_military_factories"]))
    for key, cut in (("6", cuts[0]), ("3", cuts[1])):
        out.append("%s = {\n%snum_of_military_factories < %d\n}\n"
                   % (trig[key], TAB, cut["below_military_factories"]))

    for family_id in sorted(per_family_selections):
        fam = registry.families[family_id]
        tiered = R._tiered(registry, family_id)
        out.append("\n########## %s\n" % family_id)
        for chain_id, allowed in sorted(fam["enumerate"].items()):
            if chain_id == "rockets":
                continue
            order = [c for c in registry.chains[chain_id]["order"] if c in allowed]
            for index, cid in enumerate(order):
                name = R.wins_trigger_name(family_id, chain_id, cid)
                own = registry.eligibility_of(cid, tiered)
                out.append("%s = {\n" % name)
                out.append("%s%s = yes\n" % (TAB, own))
                for higher in order[index + 1:]:
                    out.append("%sNOT = { %s = yes }\n"
                               % (TAB, registry.eligibility_of(higher, tiered)))
                out.append("}\n")
            name = R.wins_trigger_name(family_id, chain_id, R.EMPTY)
            out.append("%s = {\n" % name)
            for cid in order:
                out.append("%sNOT = { %s = yes }\n" % (TAB, registry.eligibility_of(cid, tiered)))
            out.append("}\n")

    out.append("\n########## Semantic code sets (read by tests and telemetry, never by the AI)\n")
    for family_id in sorted(per_family_selections):
        fam = registry.families[family_id]
        sels = per_family_selections[family_id]
        for label, predicate in (("waves", lambda s: s.facts.waves),
                                 ("heavy_support", lambda s: s.facts.heavy_company)):
            codes = [s.code for s in sels if predicate(s)]
            if not codes:
                continue
            name = "WA_AI_TEMPLATES_ARMOR_%s_is_%s_code" % (family_id, label)
            if len(codes) > max_or_terms:
                out.append("# %s: %d codes, contiguous %d-%d - see the manifest; an OR of that "
                           "size is a parser cost, not a predicate.\n"
                           % (name, len(codes), min(codes), max(codes)))
                continue
            out.append("%s = {\n%sOR = {\n" % (name, TAB))
            for code in codes:
                out.append("%shas_country_flag = { flag = %s value = %d }\n"
                           % (TAB * 2, fam["flag"], code))
            out.append("%s}\n}\n" % TAB)
    return "".join(out)


# ---------------------------------------------------------------------- manifest

def _manifest_row(sel):
    return {
        "code": sel.code,
        "name": sel.name,
        "facts": list(sel.facts.key()),
        "regiments": dict(sorted(sel.line.items())),
        "regimental_support": dict(sorted(sel.regimental.items())),
        "support": dict(sorted(sel.support.items())),
        "width": round(sel.width, 3),
    }


def manifest(registry, per_family_selections, stats, extra=None):
    data = {
        "marker": MARKER,
        "schema_version": registry.raw["schema_version"],
        "families": {},
        "stats": stats,
        "transitions": registry.transitions,
    }
    data.update(extra or {})
    for family_id, sels in sorted(per_family_selections.items()):
        fam = registry.families[family_id]
        data["families"][family_id] = {
            # emitted=false: modelled and code-assigned, but its ai_template file and ladder are
            # NOT written, so its codes are not reachable in game. Readers must filter on this.
            "emitted": fam.get("emit") is not False,
            "flag": fam["flag"],
            "type_code": fam["type_code"],
            "role": fam["role"],
            "file": fam["file"],
            "code_range": fam["code_range"],
            "codes_used": [min(s.code for s in sels), max(s.code for s in sels)] if sels else [],
            # One row per code: what the engine will field, and which categorical point produced
            # it. The ladder computes the code arithmetically, so the per-target trigger
            # conjunction is not part of the contract and is not carried here.
            "targets": [_manifest_row(s) for s in sels],
        }
    # One target per LINE. The manifest is committed and check_templates.py reads it, so an
    # indented dump of 2016 targets would put 75k lines of diff noise in every axis change.
    rows = {}
    for family_id, family in data["families"].items():
        rows[family_id] = family["targets"]
        family["targets"] = "@@%s@@" % family_id
    text = json.dumps(data, indent=1, sort_keys=False)
    for family_id, targets in rows.items():
        body = ",\n  ".join(json.dumps(row, sort_keys=True) for row in targets)
        text = text.replace('"@@%s@@"' % family_id,
                            "[\n  %s\n ]" % body if targets else "[]")
    return text + "\n"
