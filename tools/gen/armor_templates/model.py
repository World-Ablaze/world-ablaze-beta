"""[armor-template-generator] Registry schema, loading and structural validation.

Reads tools/armor_templates_registry.json. Rejects unknown fields, missing references and
non-integer counts before anything is resolved, so a typo fails here rather than emitting a
template the engine will silently ignore.
"""

from __future__ import annotations

import json
from pathlib import Path

SCHEMA_VERSION = 1

TOP_LEVEL = {
    "schema_version",
    "_comment",
    "composition",
    "candidates",
    "chains",
    "support_spine",
    "mobile_infantry",
    "families",
    "transitions",
}

CANDIDATE_FIELDS = {"class", "chain_rank", "eligibility", "eligibility_tiered", "units",
                    "exception"}
CHAIN_FIELDS = {"slot", "block_size", "order", "empty", "rocket_candidate", "rocket_cap",
                "_comment"}
FAMILY_FIELDS = {"chassis", "main_tank", "medium_support_unit", "role", "role_group", "flag",
                 "type_code", "admission", "extra_admission", "file", "name_token",
                 "custom_icon", "code_range", "waves", "heavy_divisional_company", "enumerate",
                 "mirror_of", "emit", "front_role_override",
                 "mode", "profiles", "reinforce_prio", "can_upgrade_in_field", "_comment"}

# A family is either ENUMERATED (its targets are the product of declared axes) or DECLARED (its
# targets are written out one by one, because they are a conversion state machine and not a
# composition), or both. A declared profile either names `facts` - and the resolver builds its
# composition from the same rules as every other target - or spells its sections out verbatim,
# which is how a deliberate blend or a mission corps survives regeneration.
PROFILE_FIELDS = {"id", "codes", "facts", "regiments", "regimental_support", "support",
                  "replace_with", "replace_at_match", "target_min_match", "custom_icon",
                  "reinforce_prio", "upgrade_prio_base", "can_upgrade_in_field",
                  "enable_extra", "enable_raw",
                  "width_exception", "emit",
                  "_comment"}
MODES = {"enumerated", "declared", "both"}

CLASSES = {"none", "light", "medium", "modern", "heavy", "mechanized"}


class RegistryError(Exception):
    """Invalid registry input. Always carries the offending key."""


def _require(cond, msg):
    if not cond:
        raise RegistryError(msg)


class Registry:
    def __init__(self, data, path):
        self.path = path
        self.raw = data
        self.composition = data["composition"]
        self.candidates = data["candidates"]
        self.chains = data["chains"]
        self.support_spine = data["support_spine"]["entries"]
        self.mobile_infantry = data["mobile_infantry"]
        self.families = data["families"]
        self.transitions = data.get("transitions", {})
        self._validate()

    # ---------------------------------------------------------------- validation
    def _validate(self):
        _require(self.raw.get("schema_version") == SCHEMA_VERSION,
                 "schema_version must be %d" % SCHEMA_VERSION)
        unknown = set(self.raw) - TOP_LEVEL
        _require(not unknown, "unknown top-level keys: %s" % sorted(unknown))

        for cid, cand in self.candidates.items():
            extra = set(cand) - CANDIDATE_FIELDS
            _require(not extra, "candidate %s: unknown fields %s" % (cid, sorted(extra)))
            _require(cand.get("class") in CLASSES,
                     "candidate %s: class %r not in %s" % (cid, cand.get("class"), sorted(CLASSES)))
            for slot, unit in cand.get("units", {}).items():
                _require(slot in ("line", "divisional", "regimental"),
                         "candidate %s: bad slot %r" % (cid, slot))
                _require(isinstance(unit, str) and unit,
                         "candidate %s: slot %s has no unit id" % (cid, slot))

        for chid, chain in self.chains.items():
            extra = set(chain) - CHAIN_FIELDS
            _require(not extra, "chain %s: unknown fields %s" % (chid, sorted(extra)))
            _require(isinstance(chain.get("block_size"), int) and chain["block_size"] > 0,
                     "chain %s: block_size must be a positive integer" % chid)
            seen = set()
            for cid in chain["order"]:
                _require(cid in self.candidates, "chain %s: unknown candidate %s" % (chid, cid))
                _require(cid not in seen, "chain %s: duplicate candidate %s" % (chid, cid))
                seen.add(cid)
            ranks = [self.candidates[c].get("chain_rank", 0) for c in chain["order"]]
            _require(ranks == sorted(ranks),
                     "chain %s: order must be ascending by chain_rank, got %s" % (chid, ranks))
            _require(chain["empty"] in self.candidates,
                     "chain %s: unknown empty candidate %s" % (chid, chain["empty"]))
            # [armor-template-generator] A21: a chain may only offer candidates that own a
            # company in the slot it fills. Infantry support declares no regimental unit, so
            # listing it in an regimental chain would silently hand the block to a candidate
            # that cannot fill it - which is exactly how the line chain used to swallow the
            # assault gun's regimental company. Checked here so it can never come back.
            # The `none` sentinel is the block being ABSENT, not a unit that fills it.
            slot = chain["slot"]
            checked = list(chain["order"])
            if chain["empty"] != "none":
                checked.append(chain["empty"])
            for cid in checked:
                _require(self.unit_of(cid, slot),
                         "chain %s fills slot %s but candidate %s declares no %s unit"
                         % (chid, slot, cid, slot))

        codes_seen = []
        for fid, fam in self.families.items():
            extra = set(fam) - FAMILY_FIELDS
            _require(not extra, "family %s: unknown fields %s" % (fid, sorted(extra)))
            mode = fam.get("mode", "enumerated")
            _require(mode in MODES, "family %s: mode %r not in %s" % (fid, mode, sorted(MODES)))
            required = ["chassis", "main_tank", "role", "role_group", "flag", "admission",
                        "file", "name_token"]
            if mode in ("enumerated", "both"):
                required += ["code_range", "enumerate"]
            for key in required:
                _require(key in fam, "family %s: missing %s" % (fid, key))
            if mode in ("declared", "both"):
                _require(fam.get("profiles"), "family %s: mode %s needs profiles" % (fid, mode))
                self._validate_profiles(fid, fam)
            if "code_range" not in fam:
                continue
            lo, hi = fam["code_range"]
            _require(isinstance(lo, int) and isinstance(hi, int) and lo < hi,
                     "family %s: bad code_range" % fid)
            for other, olo, ohi in codes_seen:
                _require(hi < olo or lo > ohi,
                         "family %s code_range overlaps %s" % (fid, other))
            codes_seen.append((fid, lo, hi))
            for chid, allowed in fam["enumerate"].items():
                if chid == "rockets":
                    _require(isinstance(allowed, bool), "family %s: rockets must be bool" % fid)
                    continue
                _require(chid in self.chains, "family %s: unknown chain %s" % (fid, chid))
                for cid in allowed:
                    _require(cid in self.candidates,
                             "family %s chain %s: unknown candidate %s" % (fid, chid, cid))
                    _require(cid in self.chains[chid]["order"],
                             "family %s chain %s: %s is not in the chain order" % (fid, chid, cid))
            mirror = fam.get("mirror_of")
            _require(mirror is None or mirror in self.families,
                     "family %s: mirror_of %r is not a family" % (fid, mirror))

        for entry in self.support_spine:
            _require("id" in entry, "support_spine entry without id")
            has = sum(1 for k in ("unit", "chassis_map", "chain") if k in entry)
            _require(has == 1,
                     "support_spine %s: exactly one of unit/chassis_map/chain" % entry["id"])
            if "chain" in entry:
                _require(entry["chain"] in self.chains,
                         "support_spine %s: unknown chain %s" % (entry["id"], entry["chain"]))

        quotas = self.composition["medium_support_quota"]
        _require(all(isinstance(q["count"], int) for q in quotas),
                 "medium_support_quota counts must be integers")

    def _validate_profiles(self, fid, fam):
        seen_ids, seen_codes = set(), set()
        known = set(p["id"] for p in fam["profiles"])
        for prof in fam["profiles"]:
            extra = set(prof) - PROFILE_FIELDS
            _require(not extra, "%s/%s: unknown profile fields %s"
                     % (fid, prof.get("id"), sorted(extra)))
            pid = prof.get("id")
            _require(pid and pid not in seen_ids, "%s: duplicate profile id %r" % (fid, pid))
            seen_ids.add(pid)
            for code in prof.get("codes", []):
                _require(isinstance(code, int), "%s/%s: non-integer code" % (fid, pid))
                seen_codes.add(code)
            has_facts = "facts" in prof
            has_sections = any(k in prof for k in
                               ("regiments", "regimental_support", "support"))
            _require(has_facts != has_sections,
                     "%s/%s: exactly one of `facts` or explicit sections" % (fid, pid))
            if prof.get("replace_with"):
                _require(prof["replace_with"] in known,
                         "%s/%s: replace_with %s is not a profile of this family - a cross-group "
                         "pointer does not resolve" % (fid, pid, prof["replace_with"]))

    # ---------------------------------------------------------------- helpers
    def candidate(self, cid):
        return self.candidates[cid]

    def unit_of(self, cid, slot):
        return self.candidates[cid].get("units", {}).get(slot)

    def eligibility_of(self, cid, tiered=False):
        cand = self.candidates[cid]
        if tiered and cand.get("eligibility_tiered"):
            return cand["eligibility_tiered"]
        return cand.get("eligibility")

    def referenced_triggers(self):
        names = set()
        for cand in self.candidates.values():
            for key in ("eligibility", "eligibility_tiered"):
                if cand.get(key):
                    names.add(cand[key])
        for fam in self.families.values():
            names.add(fam["admission"])
            if fam.get("extra_admission"):
                names.add(fam["extra_admission"])
        for form in self.mobile_infantry.values():
            if form.get("eligibility"):
                names.add(form["eligibility"])
        for tr in self.transitions.values():
            if tr.get("admission"):
                names.add(tr["admission"])
        return names

    def referenced_units(self):
        units = set()
        for cand in self.candidates.values():
            units.update(cand.get("units", {}).values())
        for fam in self.families.values():
            units.add(fam["main_tank"])
            if fam.get("medium_support_unit"):
                units.add(fam["medium_support_unit"])
        for entry in self.support_spine:
            if "unit" in entry:
                units.add(entry["unit"])
            if "chassis_map" in entry:
                units.update(entry["chassis_map"].values())
        for form in self.mobile_infantry.values():
            units.add(form["unit"])
        return units


def load(repo_root: Path) -> Registry:
    path = Path(repo_root) / "tools" / "armor_templates_registry.json"
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return Registry(data, path)
