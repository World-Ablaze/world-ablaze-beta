"""Deterministic campaign snapshots, with bounded streaming save reads.

Two full passes (country/equipment/state data, then the existing air-wing reader).
Only one country's selected sections and one equipment definition are held at once.
Existing save readers own navy counts, resource ledgers, building ownership, division
template classification and the air-wing census. No stdout is parsed and no LLM runs.

Limits: manpower.ratio's free-pool meaning remains ASSUMED; casualty direction is
DERIVED. Production speed/produced fields have no validated daily unit. Armor stock
is signed; it is never subtracted from reinforcement requests to invent a deficit.
Training requirements and variant-specific requirements remain null. Definitions
come from the supplied checkout, not necessarily the historical campaign revision.
Reinforcement needs are registered requests; already dispatched equipment can still
be attached to a request. They are not certified uncovered shortages.
"""
from __future__ import annotations

import importlib
import math
import re
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


_SCRIPT_DIR = Path(__file__).resolve().parents[2] / ".claude/skills/wa-savegame-analysis/scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
sg = importlib.import_module("savegame")
plans = importlib.import_module("plans")
airload = importlib.import_module("airload")


def _metric(label, unit, evidence, source, note=None):
    return dict(label=label, unit=unit, evidence=evidence, source=source,
                **({"note": note} if note else {}))


METRICS = {
    "mobilised_share": _metric("Mobilised share of the population", "percent", "DERIVED", "countries/TAG/manpower/ratio / 1e7", "Recruitable fraction of the population under the conscription law and its modifiers. Scale cross-checked on one state: Ruhr 1943.6 (total - locked) / total = 14.8 % = GER ratio 1481500 / 1e7."),
    "population": _metric("Population of controlled states", "men", "DERIVED", "states/manpower_pool/total, summed over controlled states", "Sum of the state pools' total; non-core states included at their full population."),
    "manpower_free": _metric("Available manpower", "men", "DERIVED", "states/manpower_pool/available, summed over controlled states", "Free pool the engine reports per state; attribution to the controller is assumed for occupied states."),
    "divisions": _metric("Deployed divisions", "count", "MEASURED", "countries/TAG/units/division"),
    "army_manpower": _metric("Army manpower", "men", "DERIVED", "units/division/army_manpower/army_manpower_value", "Sum of all countries' manpower contributions in deployed divisions; excludes the training queue."),
    "ships": _metric("Warships", "count", "DERIVED", "units/fleet/task_force/ship/definition", "Count of existing ships, excluding victims recorded in ship histories."),
    "aircraft": _metric("Aircraft in wings", "count", "DERIVED", "strategic_air/TAG/air_wing_pool/air_wings/count"),
    "aircraft_stock": _metric("Aircraft stockpile", "count", "DERIVED", "production/equipments + equipments + common/units/equipment", "Signed stockpiles of every airframe family (fighters, bombers, transports); roles are classified from the current checkout's definitions."),
    "civilian_factories": _metric("Civilian factories", "count", "DERIVED", "states/buildings/industrial_complex/level", "Installed levels in controlled states, not usable factories after damage and occupation."),
    "military_factories": _metric("Military factories", "count", "DERIVED", "states/buildings/arms_factory/level", "Installed levels in controlled states."),
    "dockyards": _metric("Dockyards", "count", "DERIVED", "states/buildings/dockyard/level", "Installed levels in controlled states."),
    "losses": _metric("Ongoing-war casualties", "men", "DERIVED", "diplomacy/active_relations/*/war_relation/first_casualties,second_casualties", "Counter direction is inferred; peace can remove a counter. The combat/attrition scope is not verified."),
    "stability": _metric("Stability", "percent", "DERIVED", "countries/TAG/stability + stability_factor of held ideas, appointed advisors' and ruling leader's traits and enabled dynamic modifiers + party popularity + coastal protection + at-war term + war-support term, clamped to 0..1", "The in-game value is not stored; it is rebuilt from the stored base and the checkout's definitions. Every line of the ENG, ITA and JAP stability tooltips (August 1941) is reproduced: ruling party popularity x (0.15 + party_popularity_stability_factor); the stored coastal_protection_ratio as is; 'at war' = -0.2 + offensive_war_stability_factor while waging an offensive war + defensive_war_stability_factor while fighting a defensive one; the war_support_during_war static modifier (-0.3) x (1 - war support). A faction manifest's scale modifiers (e.g. the Axis +0.15 offensive factor) multiply a progress ratio rebuilt from the save's state owners/controllers and the checkout's initial cores and continents (in-game core changes are not stored: ASSUMED rare); a manifest whose collections are not reproduced falls back to both bounds and the value is reported only when they agree after clamping (bounds in countries/TAG/politics/manifest_bounds). Per-term breakdown in countries/TAG/politics."),
    "war_support": _metric("War support", "percent", "DERIVED", "countries/TAG/war_support + war_support_factor of held ideas, appointed advisors' and ruling leader's traits, enabled dynamic modifiers and an intact pride of the fleet - 0.2 per offensive war posture + 0.2 per defensive war posture + stored bombing and hero-casualty penalties, clamped to 0..1", "Rebuilt from the stored base; every term matches the in-game tooltip read on ENG, August 1941 (MEASURED: base, offensive -20 and defensive +20 both listed, enemy bombing, spirits, leader, appointed advisor, pride of the fleet). Advisors count when listed in characters/appointed_advisors; the leader in office counts through the leader traits only. World tension counts for 0 in WA (05_defines.lua). A faction manifest's war-support scale modifier (China's +0.1) multiplies a progress ratio rebuilt from state controllers, initial cores and ruling parties (countries/TAG/politics/manifest_ratio). Per-term breakdown in countries/TAG/politics."),
    "stability_base": _metric("Stability (stored base)", "percent", "MEASURED", "countries/TAG/stability", "The base the engine stores; add_stability and weekly modifiers move this number, national spirits do not."),
    "war_support_base": _metric("War support (stored base)", "percent", "MEASURED", "countries/TAG/war_support", "The base the engine stores; add_war_support and weekly modifiers move this number, national spirits do not."),
    "command_power": _metric("Command power", "points", "MEASURED", "countries/TAG/command_power"),
    "political_power": _metric("Political power", "points", "MEASURED", "countries/TAG/politics/political_power", "Stored balance at the save date."),
    "generals": _metric("Generals", "count", "DERIVED", "countries/TAG/characters/character_status (unit_leader=yes) x character_manager corps_commander role", "Characters of the country holding the unit-leader role whose record carries a corps_commander block and no field_marshal block. Retired characters are listed apart and not counted; a leader hidden by an availability trigger is counted (ASSUMED rare)."),
    "field_marshals": _metric("Field marshals", "count", "DERIVED", "countries/TAG/characters/character_status (unit_leader=yes) x character_manager field_marshal role", "Same rule with the field_marshal block."),
    "admirals": _metric("Admirals", "count", "DERIVED", "countries/TAG/characters/character_status (unit_leader=yes) x character_manager navy_leader role", "Same rule with the navy_leader block."),
    "army_xp": _metric("Army XP", "points", "MEASURED", "countries/TAG/experience_status/army_experience"),
    "navy_xp": _metric("Navy XP", "points", "MEASURED", "countries/TAG/experience_status/navy_experience"),
    "air_xp": _metric("Air XP", "points", "MEASURED", "countries/TAG/experience_status/air_experience"),
    "economy_fatigue": _metric("Economy fatigue", "points", "MEASURED", "countries/TAG/variables/economic_fatigue", "WA variable read as stored; the economy_fatigue_N levels are ideas derived from this value."),
    "convoys_pool": _metric("Convoys owned", "count", "DERIVED", "countries/TAG/convoys/equipment/amount", "Sum of the convoy pool over variants; trade, supply and transport use are not separated."),
    "convoys_free": _metric("Free convoys", "count", "MEASURED", "countries/TAG/variables/wa_tlm_nav_convoys", "WA telemetry; 0 is a real famine. Its reading as free convoys is not verified in-game. Unknown when the telemetry exceeds the pool (frozen after a capitulation)."),
    "convoys_in_use": _metric("Convoys in use", "count", "DERIVED", "convoys_pool - convoys_free", "Difference of the two measures; assumes the pool and the telemetry count the same convoys."),
    "convoy_kills": _metric("Convoys sunk by this country (cumulative)", "count", "MEASURED", "countries/TAG/convoys_destroyed", "Cumulative counter on the attacking country."),
}
LEDGER_SOURCE = "sunk_convoys_history/sunk_convoy (month, killer_country, owner, convoys)"


def _scan_variables(lines, names):
    """Numeric values of a few named country variables, read by regex; the section is never parsed whole."""
    wanted = {name: None for name in names}
    if not lines:
        return wanted
    pattern = re.compile(r"^\s*(" + "|".join(re.escape(n) for n in names) + r")=(-?[0-9.]+)\s*$")
    for line in lines:
        match = pattern.match(line)
        if match and wanted[match.group(1)] is None:
            wanted[match.group(1)] = number(match.group(2))
    return wanted


@lru_cache(maxsize=4)
def conscription_ladder(repo):
    """Ordered ids of the `mobilization_laws` idea category, file order = ladder order."""
    ladder = []
    for path in sorted(Path(repo).glob("common/ideas/*.txt"), key=lambda p: (p.name != "_manpower.txt", p.name)):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        start = text.find("mobilization_laws")
        if start < 0:
            continue
        depth, k = 0, text.index("{", start)
        while k < len(text):
            if text[k] == "{":
                depth += 1
                if depth == 2:
                    match = re.search(r"([A-Za-z0-9_]+)\s*=\s*$", text[max(0, k - 80):k].rstrip())
                    if match and match.group(1) not in ladder:
                        ladder.append(match.group(1))
            elif text[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
    return tuple(ladder)


_POLITICS_KEYS = ("stability_factor", "war_support_factor", "offensive_war_stability_factor",
                  "defensive_war_stability_factor", "party_popularity_stability_factor", "war_stability_factor")
# Vanilla 1.19.2 NDefines.NCountry values; any of them present in the checkout's 05_defines.lua wins.
_NCOUNTRY_DEFAULTS = {"BASE_STABILITY_WAR_FACTOR": -0.2, "BASE_STABILITY_PARTY_POPULARITY_FACTOR": 0.15,
                      "WAR_SUPPORT_OFFNSIVE_WAR": -0.2,
                      "WAR_SUPPORT_DEFENSIVE_WAR": 0.2, "WAR_SUPPORT_TENSION_IMPACT": 0.4,
                      "MIN_STABILITY": 0.0, "MAX_STABILITY": 1.0, "MIN_WAR_SUPPORT": 0.0, "MAX_WAR_SUPPORT": 1.0}


def _modifier_values(node):
    """The stability / war-support modifiers of one definition block, numeric values only."""
    found = {}
    for key in _POLITICS_KEYS:
        value = numeric(node, key)
        if value is not None:
            found[key] = value
    return found


@lru_cache(maxsize=4)
def politics_catalog(repo):
    """Stability / war-support modifiers per idea, leader trait, dynamic modifier and static modifier.

    Dynamic modifiers keep their line order: the save stores their current values as an ordered list.
    Advisor and leader traits are named by the save itself (character_manager); only their values come from here.
    """
    repo = Path(repo)
    ideas, traits, dynamic, static = {}, {}, {}, {}
    for path in sorted(repo.glob("common/ideas/*.txt")):
        for _, category in parse(path.read_text(encoding="utf-8-sig", errors="replace")).block("ideas"):
            if not isinstance(category, Node):
                continue
            for name, idea in category:
                if isinstance(idea, Node) and name not in ideas:
                    found = _modifier_values(idea.block("modifier"))
                    if found:
                        ideas[name] = found
    for path in sorted(repo.glob("common/country_leader/*.txt")):
        for name, trait in parse(path.read_text(encoding="utf-8-sig", errors="replace")).block("leader_traits"):
            if isinstance(trait, Node) and name not in traits:
                found = _modifier_values(trait)
                if found:
                    traits[name] = found
    for path in sorted(repo.glob("common/dynamic_modifiers/*.txt")):
        for name, definition in parse(path.read_text(encoding="utf-8-sig", errors="replace")):
            if isinstance(definition, Node) and name not in dynamic:
                dynamic[name] = [key for key, value in definition if key not in (None, "icon") and not isinstance(value, Node)]
    for path in sorted(repo.glob("common/modifiers/*.txt")):
        for name, definition in parse(path.read_text(encoding="utf-8-sig", errors="replace")):
            if isinstance(definition, Node) and name in ("pride_of_the_fleet_country", "pride_of_the_fleet_sunk_temporary", "war_support_during_war") and name not in static:
                static[name] = _modifier_values(definition)
    manifests = {}
    for path in sorted(repo.glob("common/factions/goals/faction_manifests.txt")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        threshold = re.search(r"@manifest_fulfilled_value\s*=\s*([0-9.]+)", text)
        for name, goal in parse(text):
            if not isinstance(goal, Node) or goal.scalar("is_manifest") != "yes":
                continue
            progress = goal.block("ratio_progress") or goal.block("progress")
            scale = _modifier_values(progress.block("scale"))
            fulfilled = _modifier_values(progress.block("progress_sections").block("manifest_fulfilled").block("modifier"))
            if scale or fulfilled:
                manifests[name] = dict(scale=scale, fulfilled=fulfilled,
                                       range_max=numeric(progress.block("range"), "max") if numeric(progress.block("range"), "max") is not None else 1.0,
                                       fulfilled_min=numeric(progress.block("progress_sections").block("manifest_fulfilled"), "min")
                                       if numeric(progress.block("progress_sections").block("manifest_fulfilled"), "min") is not None
                                       else (float(threshold.group(1)) if threshold else 0.75))
    # Manifest progress collections: initial cores from history/states (in-game core changes are
    # not stored in the save: ASSUMED rare), continents from map/definition.csv via a state's first province.
    state_cores, state_first_province = {}, {}
    for path in sorted(repo.glob("history/states/*.txt")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        sid = re.search(r"^\s*id\s*=\s*(\d+)", text, re.M)
        if not sid:
            continue
        state_cores[int(sid.group(1))] = set(re.findall(r"add_core_of\s*=\s*([A-Z0-9]{3})", text))
        provinces = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
        if provinces and provinces.group(1).split():
            state_first_province[int(sid.group(1))] = int(provinces.group(1).split()[0])
    continent_names, province_continent, state_continent = [], {}, {}
    continents = repo / "map/continent.txt"
    if continents.exists():
        match = re.search(r"continents\s*=\s*\{([^}]*)\}", continents.read_text(encoding="utf-8-sig", errors="replace"))
        continent_names = match.group(1).split() if match else []
    definition = repo / "map/definition.csv"
    if definition.exists() and continent_names:
        wanted = set(state_first_province.values())
        for line in definition.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            cells = line.split(";")
            if len(cells) >= 8 and cells[0].isdigit() and int(cells[0]) in wanted and cells[7].strip().isdigit():
                index = int(cells[7])
                if 1 <= index <= len(continent_names):
                    province_continent[int(cells[0])] = continent_names[index - 1]
        state_continent = {sid: province_continent[pid] for sid, pid in state_first_province.items() if pid in province_continent}
    defines = dict(_NCOUNTRY_DEFAULTS)
    lua = repo / "common/defines/05_defines.lua"
    if lua.exists():
        for match in re.finditer(r"NDefines\.NCountry\.([A-Z_]+)\s*=\s*(-?[0-9.]+)", lua.read_text(encoding="utf-8-sig", errors="replace")):
            if match.group(1) in defines:
                defines[match.group(1)] = float(match.group(2))
    return dict(ideas=ideas, traits=traits, dynamic=dynamic, static=static, manifests=manifests, defines=defines,
                state_cores=state_cores, state_continent=state_continent)


_EMPTY_POLITICS = dict(ideas={}, traits={}, dynamic={}, static={}, manifests={}, defines=dict(_NCOUNTRY_DEFAULTS), state_cores={}, state_continent={})
_NO_CHARACTERS = dict(characters={}, factions={}, states={}, governments={}, capitals={})


def _manifest_ratio(name, faction, context, catalog):
    """Progress ratio of a faction manifest, rebuilt from the save's state owners/controllers and the
    checkout's cores and continents; None when the manifest's collections are not reproduced."""
    states, cores, continent = context.get("states", {}), catalog.get("state_cores", {}), catalog.get("state_continent", {})
    governments = context.get("governments", {})
    members = set(faction["members"])
    if name == "faction_manifest_conquest_of_territory":
        total = sum(1 for sid, (owner, _) in states.items() if owner in members and owner in cores.get(sid, ()))
        done = sum(1 for sid, (_, controller) in states.items() if controller in members and controller not in cores.get(sid, ()))
    elif name == "faction_manifest_china_territorial_integrity":
        chinese = {sid for sid in states if cores.get(sid, set()) & {"CHI", "PRC"}}
        leader_government = governments.get(faction["leader"])
        total = len(chinese)
        done = sum(1 for sid in chinese if states[sid][1] in members and governments.get(states[sid][1]) == leader_government)
    elif name == "faction_manifest_security_through_expansion":
        home = continent.get(context.get("capitals", {}).get(faction["leader"]))
        if home is None:
            return None
        mine = [sid for sid in states if continent.get(sid) == home]
        total = len(mine)
        done = sum(1 for sid in mine if governments.get(states[sid][1]) == "communism")
    else:
        return None
    if not total:
        return None
    return min(catalog["manifests"][name]["range_max"], done / total)


def _political_modifiers(ideas, dynamic_values, catalog):
    """Sum of the stability / war-support modifiers of the ideas and dynamic modifiers a country carries."""
    totals = {key: 0.0 for key in _POLITICS_KEYS}
    sources = []
    for token in ideas:
        found = catalog["ideas"].get(token)
        if found:
            sources.append([token, dict(found)])
            for key, value in found.items():
                totals[key] += value
    for name, values in dynamic_values:
        found = {}
        for key, value in zip(catalog["dynamic"].get(name, []), values):
            if key in _POLITICS_KEYS and value is not None:
                found[key] = found.get(key, 0.0) + value
        if found:
            sources.append(["dynamic:" + name, found])
            for key, value in found.items():
                totals[key] += value
    return totals, sources


def _trait_modifiers(names, catalog):
    found = {}
    for trait in names or ():
        for key, value in catalog["traits"].get(trait, {}).items():
            found[key] = found.get(key, 0.0) + value
    return found


def _days(date):
    parts = sg.date_key(date)
    return parts[0] * 365 + parts[1] * 30 + parts[2]


def _attach_wings(country, wing_counts, definitions, catalog):
    """Aircraft in wings per airframe family / role, from the wings' equipment amounts.

    Air families take the wing aircraft as their `deployed` value (aircraft serve in wings, not
    divisions); variants get theirs as well. Unregistered or unclassified variants are reported.
    """
    families, variants = country["equipment"]["families"], {v["id"]: v for v in country["equipment"]["variants"]}
    by_role = Counter()
    # The production section was read when the aircraft stockpile is known: a family with no stock
    # entry then holds 0, never unknown (an unknown would void the country's family sums).
    zero = 0.0 if country["metrics"].get("aircraft_stock") is not None else None
    for family in families.values():
        if family.get("domain") == "air":
            family["deployed"] = 0.0
    for variant in variants.values():
        if variant.get("domain") == "air":
            variant["deployed"] = 0.0
    for eid, amount in wing_counts.items():
        definition = definitions.get(eid)
        classification = catalog.get(definition["definition"], {}) if definition else {}
        if classification.get("domain") != "air":
            country["issues"].append(f"Wing equipment #{eid} is not a classified airframe; {amount:g} aircraft are not attributed to a family.")
            continue
        family, role = classification["family"], classification.get("role") or classification["family"]
        row = families.setdefault(family, {"domain": "air", "role": role, "stock": zero, "deployed": 0.0, "reinforcement_need": 0.0,
                                           "training_need": None, "deficit": None, "stock_deficit": zero, "active_factories": zero, "production_per_day": None})
        row["deployed"] = (row["deployed"] or 0.0) + amount
        row["role"] = role
        if eid in variants:
            variants[eid]["deployed"] = (variants[eid]["deployed"] or 0.0) + amount
        else:
            country["equipment"]["variants"].append(dict(definition, family=family, domain="air", stock=zero, deployed=amount, active_factories=zero,
                                                         production_per_day=None, reinforcement_need=None, training_need=None, stock_deficit=zero, production_lines=[]))
            variants[eid] = country["equipment"]["variants"][-1]
        by_role[role] += amount
    country["air"]["wings_by_role"] = dict(by_role)


def _finalize_politics(country, catalog, characters=_NO_CHARACTERS, date=None):
    """Rebuild the displayed stability and war support once wars and characters are known.

    War support follows the in-game tooltip read on ENG (August 1941): base, spirits and laws,
    the leader in office and the hired advisors (traits), an intact pride of the fleet, enemy
    bombing, and -0.2 for an offensive war PLUS +0.2 for a defensive war when the country has
    both. Stability (ENG, ITA and JAP tooltips): the same modifier sources; ruling party popularity
    x (0.15 + party_popularity_stability_factor); the stored coastal ratio; "at war" = -0.2 plus the
    offensive factor when waging an offensive war plus the defensive factor when fighting a
    defensive one; and the `war_support_during_war` static modifier x (1 - war support).
    """
    politics = country.get("politics") or {}
    metrics = country["metrics"]
    if "modifiers" not in politics:
        return
    defines, totals, sources = catalog["defines"], politics["modifiers"], politics["sources"]
    extra = []
    ideology, leader_id = politics.pop("_leader", (None, None))
    leader = characters["characters"].get(leader_id)
    if leader:
        found = _trait_modifiers(leader["leaders"].get(ideology), catalog)
        if found:
            extra.append(["leader:" + leader["token"], found])
    for cid in politics.pop("_hired", []):
        advisor = characters["characters"].get(cid)
        if advisor and cid != leader_id:
            found = _trait_modifiers(advisor["advisor_traits"], catalog)
            if found:
                extra.append(["advisor:" + advisor["token"], found])
    pride, lost = politics.pop("_pride", (False, None))
    if pride and lost in (None, "1.1.1.1"):
        extra.append(["static:pride_of_the_fleet_country", dict(catalog["static"].get("pride_of_the_fleet_country", {}))])
    elif pride and lost and date and 0 <= _days(date) - _days(lost) <= 30:
        extra.append(["static:pride_of_the_fleet_sunk_temporary", dict(catalog["static"].get("pride_of_the_fleet_sunk_temporary", {}))])
    for name, found in extra:
        if found:
            sources.append([name, found])
            for key, value in found.items():
                totals[key] += value
    offensive = any(w.get("offensive") is True for w in country["wars"])
    defensive = any(w.get("offensive") is False for w in country["wars"])
    unknown = any(w.get("offensive") is None for w in country["wars"])
    politics["war_posture"] = "peace" if not country["wars"] else "unknown" if unknown else "offensive" if offensive and not defensive else "defensive" if defensive and not offensive else "both"
    popularity = politics.get("ruling_popularity")
    at_war_factor = catalog["static"].get("war_support_during_war", {}).get("stability_factor", 0.0)

    def compute(totals):
        ws_terms = {"base": metrics["war_support_base"], "modifiers": totals["war_support_factor"],
                    "bombing": politics.get("being_bombed_support_penalty") or 0.0,
                    "hero_casualties": politics.get("heroes_dying_war_support_penalty") or 0.0,
                    "tension": 0.0 if defines["WAR_SUPPORT_TENSION_IMPACT"] == 0 else None,
                    "offensive_war": None if unknown else defines["WAR_SUPPORT_OFFNSIVE_WAR"] if offensive else 0.0,
                    "defensive_war": None if unknown else defines["WAR_SUPPORT_DEFENSIVE_WAR"] if defensive else 0.0}
        war_support = None
        if all(v is not None for v in ws_terms.values()):
            war_support = min(defines["MAX_WAR_SUPPORT"], max(defines["MIN_WAR_SUPPORT"], sum(ws_terms.values())))
        terms = {"base": metrics["stability_base"], "modifiers": totals["stability_factor"],
                 "party_popularity": (defines["BASE_STABILITY_PARTY_POPULARITY_FACTOR"] + totals["party_popularity_stability_factor"]) * popularity / 100.0 if popularity is not None else None,
                 "coastal_protection": politics["coastal_protection_ratio"] if politics.get("coastal_protection_ratio") is not None else 0.0,
                 "at_war": (None if unknown else defines["BASE_STABILITY_WAR_FACTOR"] + (totals["offensive_war_stability_factor"] if offensive else 0.0) + (totals["defensive_war_stability_factor"] if defensive else 0.0) + totals["war_stability_factor"]) if country["wars"] else 0.0,
                 "war_support": (at_war_factor * (1 - war_support) if war_support is not None else None) if country["wars"] else 0.0}
        stability = None
        if all(v is not None for v in terms.values()):
            stability = min(defines["MAX_STABILITY"], max(defines["MIN_STABILITY"], sum(terms.values())))
        return dict(stability=stability, war_support=war_support, stability_terms=terms, war_support_terms=ws_terms)

    # Faction manifest: its scale modifiers are multiplied by a progress ratio the save does not
    # store (collections such as core / non-core state counts). Both bounds are evaluated; a value
    # is reported only when the two bounds agree after clamping.
    faction = characters.get("factions", {}).get(country.get("tag"))
    manifest = catalog.get("manifests", {}).get(faction["manifest"]) if faction else None
    if manifest and any(key in manifest["scale"] or key in manifest["fulfilled"] for key in _POLITICS_KEYS):
        politics["faction_manifest"] = faction["manifest"]
        ratio = _manifest_ratio(faction["manifest"], faction, characters, catalog)

        def scaled(progress):
            scaled_totals = dict(totals)
            for key, value in manifest["scale"].items():
                scaled_totals[key] += value * progress
            if progress >= manifest["fulfilled_min"]:
                for key, value in manifest["fulfilled"].items():
                    scaled_totals[key] += value
            return scaled_totals

        if ratio is not None:
            politics["manifest_ratio"] = ratio
            sources.append(["manifest:" + faction["manifest"], {k: v * ratio for k, v in manifest["scale"].items()}, f"scale x progress ratio {ratio:.3f}, rebuilt from history cores and continents"])
            result = compute(scaled(ratio))
        else:
            low_result, high_result = compute(totals), compute(scaled(manifest["range_max"]))
            sources.append(["manifest:" + faction["manifest"], dict(manifest["scale"]), "x progress ratio, not reproduced"])
            result = dict(high_result)
            for metric in ("stability", "war_support"):
                lo, hi = low_result[metric], high_result[metric]
                if lo is None or hi is None or abs(lo - hi) > 1e-9:
                    result[metric] = None
                    country["issues"].append(f"{metric}: the faction manifest progress is not reproduced; the displayed value lies between {lo} and {hi}.")
            politics["manifest_bounds"] = {m: [low_result[m], high_result[m]] for m in ("stability", "war_support")}
    else:
        result = compute(totals)
    politics["stability_terms"], politics["war_support_terms"] = result["stability_terms"], result["war_support_terms"]
    for metric, parts in (("stability", result["stability_terms"]), ("war_support", result["war_support_terms"])):
        metrics[metric] = result[metric]
        if result[metric] is None and any(v is None for v in parts.values()):
            country["issues"].append(f"{metric}: a term is unknown ({', '.join(k for k, v in parts.items() if v is None)}); the displayed value is not reported.")


def convoy_window(date):
    """[first, last] month index of a save's rolling 24-month convoy-loss ledger (last complete month)."""
    parts = sg.date_key(date)
    last = parts[0] * 12 + (parts[1] - 1) - 1
    return [last - 23, last]


# Ordered duplicate-preserving nodes. Unlike the mod-oriented numeric tokenizer,
# save scalars such as 1943.6.1.2 and wa_variable^12 must remain single tokens.
_TOKENS = re.compile(r'"(?:[^"\\]|\\.)*"|\#[^\n]*|[{}]|[=<>]=?|[^\s{}=<>#"]+')


class Node(list):
    def all(self, key):
        return [v for k, v in self if k == key]

    def get(self, key, default=None):
        return next((v for k, v in reversed(self) if k == key), default)

    def block(self, key):
        value = self.get(key)
        return value if isinstance(value, Node) else Node()

    def scalar(self, key, default=None):
        value = self.get(key)
        return value if isinstance(value, str) else default


def parse(text):
    tokens = [m.group() for m in _TOKENS.finditer(text) if not m.group().startswith("#")]
    root = Node()
    stack = [root]
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "}":
            if len(stack) == 1:
                raise ValueError("unbalanced closing brace")
            stack.pop()
            i += 1
            continue
        key = None
        if i + 1 < len(tokens) and tokens[i + 1] in ("=", "<", ">", "<=", ">="):
            key, i = token.strip('"'), i + 2
            if i == len(tokens):
                raise ValueError("missing value")
            token = tokens[i]
        if token == "{":
            child = Node()
            stack[-1].append((key, child))
            stack.append(child)
        else:
            stack[-1].append((key, token[1:-1] if token.startswith('"') else token))
        i += 1
    if len(stack) != 1:
        raise ValueError("unbalanced opening brace")
    return root


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def numeric(node, key):
    return number(node.scalar(key))


def blocks(node, key):
    return (v for v in node.all(key) if isinstance(v, Node))


def walk(node, key):
    for k, value in node:
        if isinstance(value, Node):
            if k == key:
                yield value
            yield from walk(value, key)


_QUOTED_COMMENT = re.compile(r'"(?:[^"\\]|\\.)*"|\#[^\n]*')


def _delta(line):
    # Quoted names and comments can contain literal braces.
    if "{" not in line and "}" not in line:
        return 0
    clean = _QUOTED_COMMENT.sub('', line) if '"' in line or '#' in line else line
    return clean.count("{") - clean.count("}")


def _read_block(fh, opening):
    lines = [opening]
    depth = _delta(opening)
    while depth > 0:
        line = next(fh, None)
        if line is None:
            raise ValueError("truncated block in save")
        lines.append(line)
        depth += _delta(line)
    return lines


_POOL_RE = re.compile(r"^\s*(available|locked|total)=(-?[0-9.]+)\s*$")


def _state_pool(lines):
    """available / locked / total of a state's `manpower_pool` block; missing block -> empty dict."""
    pool, inside = {}, False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("manpower_pool={"):
            inside = True
            continue
        if inside:
            if stripped == "}":
                break
            match = _POOL_RE.match(stripped)
            if match:
                pool[match.group(1)] = float(match.group(2))
    return pool


def _children(fh):
    """Direct entries after a block's opening line; preserve complete children."""
    for line in fh:
        stripped = line.strip()
        if stripped == "}":
            return
        if not stripped:
            continue
        yield _read_block(fh, line)
    raise ValueError("unterminated save section")


@lru_cache(maxsize=4)
def equipment_catalog(repo):
    definitions = {}
    for path in sorted((Path(repo) / "common/units/equipment").glob("*.txt")):
        root = parse(path.read_text(encoding="utf-8-sig", errors="replace"))
        for key, node in root.block("equipments"):
            if isinstance(node, Node):
                definitions[key] = {
                    "archetype": node.scalar("archetype"), "parent": node.scalar("parent"),
                    "is_archetype": node.scalar("is_archetype") == "yes",
                    "type": node.get("type"), "group_by": node.scalar("group_by"),
                }

    def resolve(key, seen=None):
        seen = set() if seen is None else seen
        if key in seen or key not in definitions:
            return dict(family=None, role=None, domain=None)
        seen.add(key)
        row = definitions[key]
        parent = row["archetype"] or row["parent"]
        inherited = resolve(parent, seen) if parent else dict(family=None, role=None, domain=None)
        kinds = row["type"]
        if isinstance(kinds, Node):
            kinds = [v for k, v in kinds if k is None and isinstance(v, str)]
        else:
            kinds = [kinds] if kinds else []
        if "armor" in kinds:
            inherited["domain"] = "armor"
        air_roles = [k for k in kinds if k in {"fighter", "cv_fighter", "cas", "cv_cas", "naval_bomber", "cv_naval_bomber", "heavy_fighter", "tac_bomber", "strat_bomber", "transport_plane", "scout_plane", "maritime_patrol_plane", "heavy_strat_bomber", "jet_fighter", "jet_tac_bomber", "jet_strat_bomber", "interceptor", "tactical_bomber", "strategic_bomber", "air_transport"}]
        if air_roles:
            inherited.update(domain="air", role=air_roles[0])
        elif "armor" not in kinds and set(kinds) & {"infantry", "artillery", "anti_tank", "anti_air", "motorized", "mechanized", "rocket", "railway_gun"}:
            inherited["domain"] = "army"
        # `train` is a military-line equipment like the three above: without a domain its factories
        # were dropped from every total (GER 1942.12: 149 of 710 assigned). Separate from "army"
        # because trains never enter a division, so deployed and reinforcement stay 0 by nature.
        elif "train" in kinds:
            inherited["domain"] = "rail"
        if row["is_archetype"] or not inherited["family"]:
            inherited["family"] = key
        return inherited

    return {key: resolve(key) for key in definitions}


@lru_cache(maxsize=4)
def battalion_catalog(repo):
    families = {}
    for path in sorted((Path(repo) / "common/units").glob("*.txt")):
        plans._scan_sub_units(path.read_text(encoding="utf-8-sig", errors="replace"), families)
    return families


def _id(node, key="id"):
    value = numeric(node.block(key), "id")
    return int(value) if value is not None else None


def _inventory(node):
    amounts = Counter()
    for entry in blocks(node, "equipment"):
        eid, amount = _id(entry), numeric(entry, "amount")
        if eid is not None and amount is not None:
            amounts[eid] += amount
    return amounts


def _manpower(node):
    out = Counter()
    for value in blocks(node, "value"):
        tag, amount = value.scalar("tag"), numeric(value, "value")
        if tag and amount is not None:
            out[tag] += amount
    return dict(out)


def _empty():
    return {"metrics": {key: None for key in METRICS},
            "army": {"types": {}, "templates": [], "manpower_by_origin": {}},
            "navy": {"types": {}}, "air": {"types": {}, "stock_types": {}, "wings_by_role": {}},
            "buildings": {"controlled": {}, "owned": {}}, "resources": {},
            "equipment": {"families": {}, "variants": []}, "wars": [], "issues": [], "conscription_law": None,
            "politics": {}}


REPO_FOR_LADDER = Path(__file__).resolve().parents[2]


def _country(tag, raw, definitions, catalog, templates, battalions, politics=None):
    result = _empty()
    metrics = result["metrics"]
    nodes = {k: parse("".join(v)).block(k) for k, v in raw.items() if k not in ("scalars", "resources", "variables")}
    scalars = parse("".join(raw.get("scalars", [])))
    metrics["command_power"] = numeric(scalars, "command_power")
    metrics["political_power"] = numeric(nodes["politics"], "political_power") if "politics" in nodes else None
    metrics["convoy_kills"] = numeric(scalars, "convoys_destroyed")
    # The stored stability / war support are bases; the displayed values are rebuilt in
    # _finalize_politics once the wars (offensive or defensive) are attached to the country.
    metrics["stability_base"], metrics["war_support_base"] = numeric(scalars, "stability"), numeric(scalars, "war_support")
    metrics["stability"], metrics["war_support"] = metrics["stability_base"], metrics["war_support_base"]
    ideas = []
    if "politics" in nodes:
        ideas = [value for key, value in nodes["politics"].block("ideas") if key is None]
        ladder = conscription_ladder(str(REPO_FOR_LADDER))
        laws = [idea for idea in ideas if idea in ladder]
        if laws:
            result["conscription_law"] = laws[0]
    if metrics["stability_base"] is not None or metrics["war_support_base"] is not None:
        politics = politics or _EMPTY_POLITICS
        ruling = nodes["politics"].scalar("ruling_party") if "politics" in nodes else None
        popularity = numeric(nodes["politics"].block("parties").block(ruling), "popularity") if ruling else None
        dynamic_values = []
        for modifier in blocks(nodes.get("dynamic_modifier", Node()), "modifier"):
            if modifier.scalar("modifier") and modifier.scalar("enabled", "yes") != "no":
                dynamic_values.append((modifier.scalar("modifier"), [number(v) for k, v in modifier.block("value") if k is None]))
        totals, sources = _political_modifiers(ideas, dynamic_values, politics)
        leader = next((v for k, v in nodes["politics"].block("parties").block(ruling).block("country_leader") if k is None and isinstance(v, Node)), None) if ruling else None
        result["politics"] = dict(ruling_party=ruling, ruling_popularity=popularity, modifiers=totals, sources=sources,
                                  _hired=[_id(entry, "character") for key, entry in nodes.get("characters", Node()).block("appointed_advisors") if key is None and isinstance(entry, Node)],
                                  _leader=[leader.scalar("ideology"), _id(leader, "character")] if leader is not None else [None, None],
                                  _pride=[bool(scalars.block("pride_of_the_fleet")), scalars.scalar("pride_of_the_fleet_date_lost")],
                                  _capital=numeric(scalars, "capital"),
                                  _unit_leaders=[_id(status, "character") for status in blocks(nodes.get("characters", Node()), "character_status") if status.scalar("unit_leader") == "yes"],
                                  coastal_protection_ratio=numeric(scalars, "coastal_protection_ratio"),
                                  being_bombed_support_penalty=numeric(scalars, "being_bombed_support_penalty"),
                                  heroes_dying_war_support_penalty=numeric(scalars, "heroes_dying_war_support_penalty"))
    variables = _scan_variables(raw.get("variables"), ("economic_fatigue", "wa_tlm_nav_convoys"))
    metrics["economy_fatigue"] = variables["economic_fatigue"]
    metrics["convoys_free"] = variables["wa_tlm_nav_convoys"]
    if "convoys" in nodes:
        pool = 0.0
        for block in nodes["convoys"].block("equipment").all("equipment"):
            amount = numeric(block, "amount")
            definition = definitions.get(_id(block), {}).get("definition") or ""
            if amount is not None and definition.startswith("convoy"):
                pool += amount
        metrics["convoys_pool"] = pool
    # Telemetry above the pool is a frozen value (the writer stopped, typically at capitulation): the
    # two measures disagree, so neither the free count nor the use derived from it is reported.
    if metrics["convoys_pool"] is not None and metrics["convoys_free"] is not None:
        if metrics["convoys_free"] > metrics["convoys_pool"]:
            metrics["convoys_free"] = None
        else:
            metrics["convoys_in_use"] = metrics["convoys_pool"] - metrics["convoys_free"]
    ratio = numeric(nodes.get("manpower", Node()), "ratio")
    metrics["mobilised_share"] = ratio / 1e7 if ratio is not None else None
    for axis in ("army", "navy", "air"):
        metrics[axis + "_xp"] = numeric(nodes.get("experience_status", Node()), axis + "_experience")

    if "resources" in raw:
        flat, uses = sg._parse_resources(raw["resources"])
        available = uses[0] if uses else {}
        deficit = uses[2] if len(uses) > 2 else None
        # Only the ledger blocks name resources; sibling depth-1 blocks (fuel, lend-lease, convoy
        # counters) carry scalars that are not resources and must not become ledger rows.
        ledger = ("produced", "transfer_overlord_subject", "imported", "to_export", "exported")
        keys = set().union(*(set(flat.get(block, {})) for block in ledger), set(available), set(deficit or {}))
        for resource in sorted(keys):
            row = {key: flat.get(block, {}).get(resource, 0) if block in flat else None
                   for key, block in (("produced", "produced"), ("transfer", "transfer_overlord_subject"), ("imported", "imported"), ("to_export", "to_export"), ("exported", "exported"))}
            row.update(available=available.get(resource, 0) if uses else None,
                       deficit=deficit.get(resource, 0) if deficit is not None else None)
            row["effective"] = row["available"] + row["deficit"] if row["available"] is not None and row["deficit"] is not None else None
            parts = [row[k] for k in ("produced", "transfer", "imported", "available", "to_export")]
            row["residual"] = parts[0] + parts[1] + parts[2] - parts[3] - parts[4] if all(v is not None for v in parts) else None
            result["resources"][resource] = row

    units = nodes.get("units", Node())
    deployed, manpower = Counter(), Counter()
    requirements = Counter()
    template_rows = {}
    unknown_mp = False
    if "units" in nodes:
        divisions = list(blocks(units, "division"))
        metrics["divisions"] = len(divisions)
        kinds = Counter()
        for division in divisions:
            tid = _id(division, "division_template_id")
            family = plans.template_family(templates.get(tid), battalions)
            kinds[family] += 1
            mp = _manpower(division.block("army_manpower").block("army_manpower_value"))
            if not mp:
                unknown_mp = True
            manpower.update(mp)
            if tid not in template_rows:
                template_rows[tid] = dict(id=tid, name=plans.template_label(tid, templates), family=family, count=0, manpower=0, manpower_by_origin={})
            template_rows[tid]["count"] += 1
            template_rows[tid]["manpower"] += sum(mp.values())
            origins = Counter(template_rows[tid]["manpower_by_origin"])
            origins.update(mp)
            template_rows[tid]["manpower_by_origin"] = dict(origins)
            if not mp:
                template_rows[tid]["manpower_incomplete"] = True
            deployed.update(_inventory(division.block("equipment")))
            reinforcement = division.block("requests").block("reinforcement")
            for request in blocks(reinforcement, "request"):
                for key, val in request.block("need"):
                    amount = number(val)
                    if amount is not None:
                        requirements[key] += amount
        for row in template_rows.values():
            if row.pop("manpower_incomplete", False):
                row["manpower"] = None
        metrics["army_manpower"] = sum(manpower.values()) if not unknown_mp else None
        result["army"].update(types=dict(kinds), templates=list(template_rows.values()), manpower_by_origin=dict(manpower))
        if unknown_mp:
            result["issues"].append("Incomplete army manpower: at least one division has no army_manpower_value.")
        fleets = sg._parse_fleets(raw["units"])
        navy = Counter()
        for fleet in fleets:
            for taskforce in fleet["tfs"]:
                navy.update(taskforce["ships"])
        result["navy"]["types"] = dict(navy)
        metrics["ships"] = sum(navy.values())

    production = nodes.get("production", Node())
    inventory = _inventory(production.block("equipments"))
    lines = defaultdict(list)
    for line in blocks(production, "military_lines"):
        eid = _id(line, "equipment_variant_index")
        if eid is not None:
            lines[eid].append({key: numeric(line, key) for key in ("produced", "speed", "cost", "active_factories", "requested_factories", "queued_factories", "damaged_factories")})
    families, variants, aircraft_stock = {}, [], Counter()

    def family_row(family, domain):
        return families.setdefault(family, {"domain": domain, "stock": 0 if "production" in nodes else None,
            "deployed": 0 if "units" in nodes else None,
            "reinforcement_need": 0 if "units" in nodes else None,
            "training_need": None, "deficit": None,
            "stock_deficit": 0 if "production" in nodes else None,
            "active_factories": 0 if "production" in nodes else None, "production_per_day": None})

    for eid in sorted(set(inventory) | set(deployed) | set(lines)):
        definition = definitions.get(eid)
        if not definition:
            result["issues"].append(f"Equipment #{eid} is absent from the save's equipment registry.")
            continue
        classification = catalog.get(definition["definition"], {})
        if definition["definition"] not in catalog:
            result["issues"].append(f"Definition {definition['definition']} is absent from the checkout: classification incomplete.")
        if classification.get("domain") == "air":
            aircraft_stock[classification.get("role") or classification["family"]] += inventory[eid]
        if classification.get("domain") not in ("armor", "army", "air", "rail"):
            continue
        family, domain = classification["family"], classification["domain"]
        # A serialised line without `active_factories=` is a queued line with none assigned yet: the
        # engine omits the field at its default (0). Unknown would poison the family and country sums.
        factories = sum(x["active_factories"] or 0 for x in lines[eid])
        row = dict(definition, family=family, domain=domain, stock=inventory[eid] if "production" in nodes else None,
                   deployed=deployed[eid] if "units" in nodes else None,
                   active_factories=factories if "production" in nodes else None,
                   production_per_day=None, reinforcement_need=None, training_need=None,
                   stock_deficit=max(0, -inventory[eid]) if "production" in nodes else None,
                   production_lines=lines[eid])
        variants.append(row)
        aggregate = family_row(family, domain)
        if domain == "air":
            aggregate["role"] = classification.get("role") or family
        for key in ("stock", "stock_deficit", "deployed", "active_factories"):
            if row[key] is None:
                aggregate[key] = None
            elif aggregate[key] is not None:
                aggregate[key] += row[key]
    for archetype, need in requirements.items():
        classification = catalog.get(archetype, {})
        if classification.get("domain") in ("armor", "army", "air", "rail"):
            family_row(classification["family"], classification["domain"])["reinforcement_need"] += need
    result["equipment"].update(families=families, variants=variants)
    result["air"]["stock_types"] = dict(aircraft_stock)
    metrics["aircraft_stock"] = sum(aircraft_stock.values()) if "production" in nodes else None

    wars = []
    for war in walk(nodes.get("diplomacy", Node()), "war_relation"):
        first, second, start = war.scalar("first"), war.scalar("second"), war.scalar("start_date")
        if first and second:
            instigator = war.scalar("first_was_instigator")
            wars.append(dict(first=first, second=second, start_date=start,
                             first_casualties=numeric(war, "first_casualties"),
                             second_casualties=numeric(war, "second_casualties"),
                             first_was_instigator=None if instigator is None else instigator == "yes"))
    return result, wars


def extract_save(path: Path, repo: Path) -> dict:
    """Return an independent JSON-compatible snapshot of every serialized country."""
    path, repo = Path(path), Path(repo).resolve()
    catalog = equipment_catalog(str(repo))
    battalions = battalion_catalog(str(repo))
    definitions, templates, countries, state_totals, all_wars = {}, {}, {}, defaultdict(lambda: {"owned": Counter(), "controlled": Counter()}), []
    state_pools = defaultdict(Counter)  # controller -> available / locked / total summed over its states
    wing_equipment = defaultdict(Counter)  # tag -> equipment variant id -> aircraft in wings
    warnings = ["Equipment classifications use the current checkout and may differ from the version played.",
                "Daily armor output and training requirements are not computed; the shortfall shown is recorded reinforcement requests minus stock.",
                "Recorded reinforcement requests by family may include equipment already in transit; they are not verified shortages. Training and variant-specific requirements are not established."]
    date = None
    saw_states = saw_air = False
    convoy_losses, saw_ledger = [], False
    politics = politics_catalog(str(repo))
    selected = {"units", "production", "resources", "manpower", "experience_status", "diplomacy", "variables", "convoys", "politics", "dynamic_modifier", "characters"}
    scalar_keys = {"stability", "war_support", "command_power", "convoys_destroyed", "coastal_protection_ratio",
                   "being_bombed_support_penalty", "heroes_dying_war_support_penalty", "pride_of_the_fleet", "pride_of_the_fleet_date_lost", "capital"}
    characters = dict(characters={}, factions={}, states={}, governments={}, capitals={})
    with sg.open_save(str(path)) as fh:
        for line in fh:
            if line.startswith("date="):
                date = line.split("=", 1)[1].strip().strip('"')
            elif line.startswith("states={"):
                saw_states = True
                for chunk in _children(fh):
                    bld, owner, controller = sg._state_buildings(chunk[1:-1])
                    sid = re.match(r"\s*(\d+)=\{", chunk[0])
                    if sid and owner:
                        characters["states"][int(sid.group(1))] = (owner, controller or owner)
                    if owner:
                        state_totals[owner]["owned"].update(bld)
                    if controller:
                        state_totals[controller]["controlled"].update(bld)
                        state_pools[controller].update(_state_pool(chunk[1:-1]))
            elif line.startswith("equipments={"):
                for chunk in _children(fh):
                    node = parse("".join(chunk))
                    for key, block in node:
                        if isinstance(block, Node):
                            eid = _id(block)
                            if eid is not None:
                                definitions[eid] = dict(id=eid, name=block.scalar("name", key), definition=key, creator=block.scalar("creator"))
            elif line.startswith("sunk_convoys_history={"):
                saw_ledger = True
                for chunk in _children(fh):
                    node = parse("".join(chunk)).block("sunk_convoy")
                    month, killer, owner = numeric(node, "month"), node.scalar("killer_country"), node.scalar("owner")
                    if month is not None and killer and owner:
                        convoy_losses.append([int(month), killer, owner, numeric(node, "convoys") or 0])
            elif line.startswith("faction={"):
                faction = parse("".join(_read_block(fh, line))).block("faction")
                manifest = faction.block("goal_status").scalar("manifest")
                members = [member for key, member in faction.block("members") if key is None and isinstance(member, str)]
                for member in members:
                    if manifest:
                        characters["factions"][member] = dict(manifest=manifest, members=members, leader=members[0] if members else None)
            elif line.startswith("character_manager={"):
                # Hired advisors and leaders name their traits here; the trait values come from the checkout.
                # Characters sit one level down, under wrappers such as `historical={`.
                for wrapper in fh:
                    if wrapper.strip() == "}":
                        break
                    if _delta(wrapper) == 0:
                        continue
                    for chunk in _children(fh):
                        node = parse("".join(chunk)).block("character")
                        cid = _id(node)
                        if cid is None:
                            continue
                        leaders, advisor_traits = {}, []
                        for leader in blocks(node.block("country_leaders"), "country_leader"):
                            leaders[leader.scalar("ideology")] = [v for k, v in leader.block("traits") if k is None and isinstance(v, str)]
                        for advisor in blocks(node.block("advisors"), "advisor"):
                            advisor_traits += [v for k, v in advisor.block("traits") if k is None and isinstance(v, str)]
                        characters["characters"][cid] = dict(token=node.scalar("token") or str(cid), leaders=leaders, advisor_traits=advisor_traits,
                                                             roles=[role for role in ("corps_commander", "field_marshal", "navy_leader") if node.block(role)])
            elif line.startswith("division_templates={"):
                templates = plans._read_templates(fh)
            elif line.startswith("strategic_air={"):
                saw_air = True
                # Aircraft in wings per equipment variant: a wing lists its variants with amounts
                # (older variants stay listed at 0). Resolved to families and roles once the registry is complete.
                for chunk in _children(fh):
                    match = re.match(r"\s*([A-Z0-9]{3})=\{", chunk[0])
                    if not match or _delta(chunk[0]) == 0:
                        continue
                    counter = wing_equipment[match.group(1)]
                    for pool in blocks(parse("".join(chunk)).block(match.group(1)), "air_wing_pool"):
                        for wing in blocks(pool, "air_wings"):
                            for entry in blocks(wing.block("equipment"), "equipment"):
                                eid, amount = _id(entry), numeric(entry, "amount")
                                if eid is not None and amount:
                                    counter[eid] += amount
            elif line.startswith("countries={"):
                # Consume one country at a time and discard unneeded child blocks.
                for opening in fh:
                    if opening.strip() == "}":
                        break
                    match = re.match(r'\s*([A-Z0-9]{3})=\{', opening)
                    if not match:
                        continue
                    tag = match.group(1)
                    raw = {"scalars": []}
                    if _delta(opening) == 0:
                        countries[tag] = _empty()
                        continue
                    for chunk in _children(fh):
                        key_match = re.match(r'\s*([a-z_]+)=', chunk[0])
                        key = key_match.group(1) if key_match else None
                        if key in selected:
                            raw[key] = chunk
                        elif len(chunk) == 1 and key in scalar_keys:
                            raw["scalars"].extend(chunk)
                    countries[tag], wars = _country(tag, raw, definitions, catalog, templates, battalions, politics)
                    all_wars.extend(wars)
    # This reader includes all countries in its one pass; no per-tag rescanning.
    _, wings = airload.parse_wings(str(path))
    air_totals = defaultdict(Counter)
    for wing in wings:
        air_totals[wing["tag"]][wing["def"] or "unknown"] += wing["count"]
    for tag, country in countries.items():
        country["air"]["types"] = dict(air_totals[tag])
        country["metrics"]["aircraft"] = sum(air_totals[tag].values()) if saw_air else None
        if saw_air:
            _attach_wings(country, wing_equipment.get(tag, {}), definitions, catalog)
        country["buildings"] = {kind: dict(values) for kind, values in state_totals[tag].items()}
        for metric, key in (("civilian_factories", "industrial_complex"), ("military_factories", "arms_factory"), ("dockyards", "dockyard")):
            country["metrics"][metric] = state_totals[tag]["controlled"].get(key, 0) if saw_states else None
        pool = state_pools[tag]
        country["metrics"]["population"] = pool.get("total", 0.0) if saw_states else None
        country["metrics"]["manpower_free"] = pool.get("available", 0.0) if saw_states else None
    seen = set()
    for war in all_wars:
        identity = (tuple(sorted((war["first"], war["second"]))), war["start_date"])
        if identity in seen:
            warnings.append(f"Duplicate war relation ignored: {identity}")
            continue
        seen.add(identity)
        for side, other in (("first", "second"), ("second", "first")):
            tag = war[side]
            if tag in countries:
                instigator = war.get("first_was_instigator")
                offensive = None if instigator is None else (instigator if side == "first" else not instigator)
                countries[tag]["wars"].append(dict(id="|".join(identity[0]) + "|" + (identity[1] or "?"), enemy=war[other], start_date=war["start_date"], losses=war[side + "_casualties"], offensive=offensive))
    for tag, country in countries.items():
        country_politics = country.get("politics") or {}
        characters["governments"][tag] = country_politics.get("ruling_party")
        capital = country_politics.pop("_capital", None)
        if capital is not None:
            characters["capitals"][tag] = int(capital)
        leaders = country_politics.pop("_unit_leaders", None)
        if leaders is not None and characters["characters"]:
            roles = [set(characters["characters"].get(cid, {}).get("roles", ())) for cid in leaders]
            country["metrics"]["field_marshals"] = sum(1 for r in roles if "field_marshal" in r)
            country["metrics"]["generals"] = sum(1 for r in roles if "corps_commander" in r and "field_marshal" not in r)
            country["metrics"]["admirals"] = sum(1 for r in roles if "navy_leader" in r)
    for tag, country in countries.items():
        country["tag"] = tag
        values = [w["losses"] for w in country["wars"]]
        country["metrics"]["losses"] = sum(values) if all(v is not None for v in values) else None
        _finalize_politics(country, politics, characters, date)
        country.pop("tag", None)
        country["issues"] = list(dict.fromkeys(country["issues"]))
    if date is None:
        raise ValueError(f"No date in save: {path}")
    if not saw_states:
        warnings.append("The states section is missing; building counts are unknown.")
    if not saw_air:
        warnings.append("The strategic_air section is missing; aircraft counts are unknown.")
    return dict(date=date, countries=countries, warnings=warnings,
                convoy_losses=convoy_losses if saw_ledger else None,
                convoy_window=convoy_window(date) if saw_ledger else None)
