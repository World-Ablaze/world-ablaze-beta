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
    "aircraft_stock": _metric("Aircraft stockpile", "count", "DERIVED", "production/equipments + equipments + common/units/equipment", "Signed stockpiles; roles are classified from the current checkout's definitions."),
    "civilian_factories": _metric("Civilian factories", "count", "DERIVED", "states/buildings/industrial_complex/level", "Installed levels in controlled states, not usable factories after damage and occupation."),
    "military_factories": _metric("Military factories", "count", "DERIVED", "states/buildings/arms_factory/level", "Installed levels in controlled states."),
    "dockyards": _metric("Dockyards", "count", "DERIVED", "states/buildings/dockyard/level", "Installed levels in controlled states."),
    "losses": _metric("Ongoing-war casualties", "men", "DERIVED", "diplomacy/active_relations/*/war_relation/first_casualties,second_casualties", "Counter direction is inferred; peace can remove a counter. The combat/attrition scope is not verified."),
    "stability": _metric("Stability", "percent", "MEASURED", "countries/TAG/stability"),
    "war_support": _metric("War support", "percent", "MEASURED", "countries/TAG/war_support"),
    "command_power": _metric("Command power", "points", "MEASURED", "countries/TAG/command_power"),
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
        air_roles = [k for k in kinds if k in {"fighter", "cv_fighter", "cas", "cv_cas", "naval_bomber", "cv_naval_bomber", "heavy_fighter", "tac_bomber", "strat_bomber", "transport_plane", "scout_plane", "maritime_patrol_plane", "heavy_strat_bomber", "jet_fighter", "jet_tac_bomber", "jet_strat_bomber", "interceptor"}]
        if air_roles:
            inherited.update(domain="air", role=air_roles[0])
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
            "navy": {"types": {}}, "air": {"types": {}, "stock_types": {}},
            "buildings": {"controlled": {}, "owned": {}}, "resources": {},
            "armor": {"families": {}, "variants": []}, "wars": [], "issues": [], "conscription_law": None}


REPO_FOR_LADDER = Path(__file__).resolve().parents[2]


def _country(tag, raw, definitions, catalog, templates, battalions):
    result = _empty()
    metrics = result["metrics"]
    nodes = {k: parse("".join(v)).block(k) for k, v in raw.items() if k not in ("scalars", "resources", "variables")}
    scalars = parse("".join(raw.get("scalars", [])))
    for name in ("stability", "war_support", "command_power"):
        metrics[name] = numeric(scalars, name)
    metrics["convoy_kills"] = numeric(scalars, "convoys_destroyed")
    if "politics" in nodes:
        ideas = [value for key, value in nodes["politics"].block("ideas") if key is None]
        ladder = conscription_ladder(str(REPO_FOR_LADDER))
        laws = [idea for idea in ideas if idea in ladder]
        if laws:
            result["conscription_law"] = laws[0]
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

    def family_row(family):
        return families.setdefault(family, {"stock": 0 if "production" in nodes else None,
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
        if classification.get("domain") != "armor":
            continue
        family = classification["family"]
        # A serialised line without `active_factories=` is a queued line with none assigned yet: the
        # engine omits the field at its default (0). Unknown would poison the family and country sums.
        factories = sum(x["active_factories"] or 0 for x in lines[eid])
        row = dict(definition, family=family, stock=inventory[eid] if "production" in nodes else None,
                   deployed=deployed[eid] if "units" in nodes else None,
                   active_factories=factories if "production" in nodes else None,
                   production_per_day=None, reinforcement_need=None, training_need=None,
                   stock_deficit=max(0, -inventory[eid]) if "production" in nodes else None,
                   production_lines=lines[eid])
        variants.append(row)
        aggregate = family_row(family)
        for key in ("stock", "stock_deficit", "deployed", "active_factories"):
            if row[key] is None:
                aggregate[key] = None
            elif aggregate[key] is not None:
                aggregate[key] += row[key]
    for archetype, need in requirements.items():
        classification = catalog.get(archetype, {})
        if classification.get("domain") == "armor":
            family_row(classification["family"])["reinforcement_need"] += need
    result["armor"].update(families=families, variants=variants)
    result["air"]["stock_types"] = dict(aircraft_stock)
    metrics["aircraft_stock"] = sum(aircraft_stock.values()) if "production" in nodes else None

    wars = []
    for war in walk(nodes.get("diplomacy", Node()), "war_relation"):
        first, second, start = war.scalar("first"), war.scalar("second"), war.scalar("start_date")
        if first and second:
            wars.append(dict(first=first, second=second, start_date=start,
                             first_casualties=numeric(war, "first_casualties"),
                             second_casualties=numeric(war, "second_casualties")))
    return result, wars


def extract_save(path: Path, repo: Path) -> dict:
    """Return an independent JSON-compatible snapshot of every serialized country."""
    path, repo = Path(path), Path(repo).resolve()
    catalog = equipment_catalog(str(repo))
    battalions = battalion_catalog(str(repo))
    definitions, templates, countries, state_totals, all_wars = {}, {}, {}, defaultdict(lambda: {"owned": Counter(), "controlled": Counter()}), []
    state_pools = defaultdict(Counter)  # controller -> available / locked / total summed over its states
    warnings = ["Equipment classifications use the current checkout and may differ from the version played.",
                "Daily armor output and training requirements are not computed; the shortfall shown is recorded reinforcement requests minus stock.",
                "Recorded reinforcement requests by family may include equipment already in transit; they are not verified shortages. Training and variant-specific requirements are not established."]
    date = None
    saw_states = saw_air = False
    convoy_losses, saw_ledger = [], False
    selected = {"units", "production", "resources", "manpower", "experience_status", "diplomacy", "variables", "convoys", "politics"}
    with sg.open_save(str(path)) as fh:
        for line in fh:
            if line.startswith("date="):
                date = line.split("=", 1)[1].strip().strip('"')
            elif line.startswith("states={"):
                saw_states = True
                for chunk in _children(fh):
                    bld, owner, controller = sg._state_buildings(chunk[1:-1])
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
            elif line.startswith("division_templates={"):
                templates = plans._read_templates(fh)
            elif line.startswith("strategic_air={"):
                saw_air = True
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
                        elif len(chunk) == 1 and key in {"stability", "war_support", "command_power", "convoys_destroyed"}:
                            raw["scalars"].extend(chunk)
                    countries[tag], wars = _country(tag, raw, definitions, catalog, templates, battalions)
                    all_wars.extend(wars)
    # This reader includes all countries in its one pass; no per-tag rescanning.
    _, wings = airload.parse_wings(str(path))
    air_totals = defaultdict(Counter)
    for wing in wings:
        air_totals[wing["tag"]][wing["def"] or "unknown"] += wing["count"]
    for tag, country in countries.items():
        country["air"]["types"] = dict(air_totals[tag])
        country["metrics"]["aircraft"] = sum(air_totals[tag].values()) if saw_air else None
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
                countries[tag]["wars"].append(dict(id="|".join(identity[0]) + "|" + (identity[1] or "?"), enemy=war[other], start_date=war["start_date"], losses=war[side + "_casualties"]))
    for country in countries.values():
        values = [w["losses"] for w in country["wars"]]
        country["metrics"]["losses"] = sum(values) if all(v is not None for v in values) else None
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
