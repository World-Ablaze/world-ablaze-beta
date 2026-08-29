#!/usr/bin/env python3
"""
check_ai_layers.py - holds the WA_AI 4-layer model (declaration / observation / decision /
consumption) mechanically. Companion of documentation/WA_AI_LAYERS.md; introduced with the
layers refactor (proposal: documentation/WA_AI_LAYERS_REFACTOR_PROPOSAL.md, corrected by
documentation/REVUE_LAYERS_REFACTOR.md).

    python tools/check_ai_layers.py                    # report, exit 1 on any ERROR
    python tools/check_ai_layers.py --update-baseline  # accept improved ratchet counts
    python tools/check_ai_layers.py --json             # machine-readable
    python tools/check_ai_layers.py --selftest         # prove every rule fires on a fixture

OWNERSHIP BOUNDARY. This tool owns LAYER discipline (who reads what, where literals live).
check_constants.py owns VALUE equality across formats (script constants, @, defines, buildings,
savegame tables). A number's location is judged here; a number's cross-format consistency there.

RATCHET RULES read their reference count from tools/ai_layers_baseline.json (a GENERATED file -
never hand-edit; regenerate with --update-baseline). A missing file or key is initialized from
the current count (INFO). A count above baseline is an ERROR (you added debt). A count below
baseline is an ERROR too (RATCHET-STALE) until --update-baseline is run in the same commit -
that is what makes the baseline history-honest. Metric definitions live with each rule below;
every count is comment-stripped.

ratchet  LAYER4-RAW-GATE    allowed/enable blocks in common/ai_strategy/WA_AI_*.txt containing a
                            raw engine term (RAW_TERMS list - the audit's list, explicit, a floor; bare
                            tag/original_tag are NOT raw - Country-file addressing is legal) and
                            convertible: counts blocks that are raw-only or mixed.
ratchet  LAYER4-READS-CONFIG occurrences (not files, not pairs) of a trigger defined in
                            WA_AI_CONFIG*.txt referenced from common/ai_strategy/WA_AI_*.txt.
ratchet  LAYER4-NON-DECISION occurrences of a WA_AI_* (non-CONFIG/DIFFICULTY/TEST/TLM) trigger
                            referenced in an allowed/enable block whose name carries no decision
                            verb (_should_/_can_): layer 4 naming layer 2 directly.
ratchet  DATE-LEAK          literal `date [<>=] YYYY.M.D` in a WA_*-prefixed .txt under
                            scripted_triggers/, scripted_effects/, ai_strategy/, on_actions/,
                            events/, EXCLUDING WA_AI_CONFIG*.txt and script_constants/.
                            (Files not WA_-prefixed - country decisions, focus trees - are NOT
                            counted; widening the scope is a deliberate baseline bump.)
ratchet  NUMBER-LEAK        numeric threshold on a state/capability trigger (NUM_TERMS list) in
                            the same scope as DATE-LEAK. `ai_strategy value =` payload numbers
                            and file-local @constants are NOT matched (allowed by design:
                            AGENTS.md rule 10 and the validated-contexts table).
ratchet  DIFFICULTY-RAW     raw `difficulty [<>=]` comparison anywhere in common/ + events/
                            outside WA_AI_CONFIG*.txt. The difficulty mapping is non-monotonic
                            ([difficulty-mapping] in WA_AI_CONFIG.txt), so a raw comparison
                            cannot express "normal or harder" - gate on the named triggers.
ERROR    CONFIG-LIVE        a term that moves on its own (LIVE_TERMS) inside a WA_AI_CONFIG*
                            trigger body. Named exceptions: CONFIG_LIVE_EXCEPTIONS.
ERROR    CONFIG-DEAD        a trigger defined in WA_AI_CONFIG*.txt read nowhere else in
                            common/, events/, history/ (scripted_localisation counts as a
                            reader). Named exceptions: CONFIG_DEAD_EXCEPTIONS.
ERROR    NAME-COLLISION     two trigger names identical after stripping the WA_AI_CONFIG_ /
                            WA_AI_<SYS>_ prefix, defined in different files (7-characters-apart
                            trap of is_major_naval).
ERROR    DUP-DEF            the same trigger/effect name defined twice anywhere under
                            common/scripted_triggers + common/scripted_effects.
INFO     NOT-MULTI          NOT with >= 2 direct children. Measured NOR (2026-08-29) but the
                            first-child-only confound is unprobed (q2e owed) - stays INFO.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASELINE_PATH = os.path.join(REPO, "tools", "ai_layers_baseline.json")

RAW_TERMS = re.compile(
    r"\b(date|has_war_with|has_war|num_of_\w+|has_army_manpower|has_navy_size|"
    r"has_completed_focus|has_country_flag|controls_state|owns_state|has_tech|"
    r"is_in_faction_with|surrender_progress|num_divisions|has_idea|has_government|"
    r"divisions_in_state|country_exists|exists|has_capitulated|threat|"
    r"strength_ratio|is_subject_of|has_full_control_of_state)\s*[=<>]")
NAMED_REF = re.compile(r"\b(WA_AI_\w+)\s*=\s*(?:yes|no)\b")
DATE_LIT = re.compile(r"\bdate\s*[<>=]+\s*\d{4}\.\d{1,2}\.\d{1,2}")
NUM_TERMS = re.compile(
    r"\b(num_of_\w+|has_army_manpower|has_navy_size|num_divisions|has_war_support|"
    r"has_stability|surrender_progress|arms_factory_level|threat|has_manpower|"
    r"amount_research_slots|has_political_power|command_power|has_equipment)\b"
    r"[^\n]{0,40}?[<>]=?\s*-?[\d.]+")
DIFF_RAW = re.compile(r"\bdifficulty\s*[<>=]+\s*\d")
LIVE_TERMS = re.compile(
    r"\b(any_enemy_country|any_country_of|any_other_country|any_neighbor_country|"
    r"has_war\b|has_war_with|has_war_together_with|surrender_progress|check_variable|"
    r"num_divisions|all_country|any_country)\b")

# Exceptions are DATA, not comments: each carries its reason.
CONFIG_LIVE_EXCEPTIONS = {
    # faction membership is the natural reading of a tag list; frontier 1/2 names these
    # (WA_AI_LAYERS.md "identity vs live world"); is_in_faction_with is not in LIVE_TERMS anyway.
}
CONFIG_DEAD_EXCEPTIONS = {
    "WA_AI_DIFFICULTY_is_historical_easy": "couche-1 vocabulary for the 5-level ladder",
    "WA_AI_DIFFICULTY_is_historical_normal": "couche-1 vocabulary for the 5-level ladder",
    "WA_AI_DIFFICULTY_is_competitive_normal": "couche-1 vocabulary for the 5-level ladder",
}
NAME_COLLISION_EXCEPTIONS = {
    # capability-composes-identity pairs (config-vs-system pattern): the WA_AI_ trigger reads
    # the WA_AI_CONFIG_ identity and adds live conditions. Renaming the capability half is
    # deferred - its readers live in GENERATED prospecting decisions (needs_aware_generator).
    "is_strategic_oil_exporter": "capability composes identity; readers generated",
    "is_strategic_rubber_exporter": "capability composes identity; readers generated",
    "is_strategic_tungsten_exporter": "capability composes identity; readers generated",
}
DECISION_VERB = re.compile(r"_(should|can)_")
LAYER4_NAME_EXEMPT = re.compile(r"^(WA_AI_CONFIG_|WA_AI_DIFFICULTY_|WA_TEST_|WA_TLM_)")

LEAK_FOLDERS = ("common/scripted_triggers", "common/scripted_effects",
                "common/ai_strategy", "common/on_actions", "events")


def read(p):
    with open(p, encoding="utf-8-sig", errors="ignore") as f:
        return f.read()


def strip_comments(s):
    return re.sub(r"#[^\n]*", "", s)


def gate_blocks(s):
    """allowed/enable blocks of an ai_strategy file, by token brace-walk."""
    toks = re.findall(r"[A-Za-z0-9_.:@\-]+|[{}=<>]", s)
    out = []
    i = 0
    while i < len(toks):
        if toks[i] in ("allowed", "enable") and i + 2 < len(toks) \
                and toks[i + 1] == "=" and toks[i + 2] == "{":
            d = 1
            j = i + 3
            body = []
            while j < len(toks) and d:
                if toks[j] == "{":
                    d += 1
                elif toks[j] == "}":
                    d -= 1
                if d:
                    body.append(toks[j])
                j += 1
            out.append(" ".join(body))
            i = j
        else:
            i += 1
    return out


PDX_KEYWORDS = {"OR", "AND", "NOT", "if", "else", "else_if", "limit", "hidden_trigger",
                "custom_trigger_tooltip", "custom_override_tooltip", "tooltip"}


def trigger_defs(path):
    s = strip_comments(read(path))
    return [n for n in re.findall(r"(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{", s)
            if n not in PDX_KEYWORDS]


def not_multi_count(s):
    toks = re.findall(r"[A-Za-z0-9_.:@\-]+|[{}=<>]", s)
    cnt = 0
    for i in range(len(toks)):
        if toks[i] == "NOT" and i + 2 < len(toks) and toks[i + 1] == "=" and toks[i + 2] == "{":
            d = 1
            j = i + 3
            children = 0
            while j < len(toks) and d:
                t = toks[j]
                if t == "{":
                    d += 1
                elif t == "}":
                    d -= 1
                elif d == 1 and t == "=":
                    children += 1
                j += 1
            if children >= 2:
                cnt += 1
    return cnt


def collect(repo):
    """All measurements over one repo root. Returns dict of counters + finding details."""
    r = {"LAYER4-RAW-GATE": 0, "LAYER4-READS-CONFIG": 0, "LAYER4-NON-DECISION": 0,
         "DATE-LEAK": 0, "NUMBER-LEAK": 0, "DIFFICULTY-RAW": 0, "NOT-MULTI": 0}
    details = {"CONFIG-LIVE": [], "CONFIG-DEAD": [], "NAME-COLLISION": [], "DUP-DEF": []}

    cfg_glob = []
    trig_dir = os.path.join(repo, "common", "scripted_triggers")
    if os.path.isdir(trig_dir):
        cfg_glob = [os.path.join(trig_dir, f) for f in os.listdir(trig_dir)
                    if f.startswith("WA_AI_CONFIG") and f.endswith(".txt")]
    cfg_defs = set()
    for p in cfg_glob:
        cfg_defs.update(trigger_defs(p))
    cfg_ref = re.compile(r"\b(" + "|".join(sorted(cfg_defs, key=len, reverse=True)) + r")\b") \
        if cfg_defs else None

    # ---- layer 4: common/ai_strategy/WA_AI_* ----
    strat_dir = os.path.join(repo, "common", "ai_strategy")
    if os.path.isdir(strat_dir):
        for f in sorted(os.listdir(strat_dir)):
            if not (f.startswith("WA_AI_") and f.endswith(".txt")):
                continue
            s = strip_comments(read(os.path.join(strat_dir, f)))
            if cfg_ref:
                r["LAYER4-READS-CONFIG"] += len(cfg_ref.findall(s))
            for b in gate_blocks(s):
                named = NAMED_REF.findall(b)
                nraw = len(RAW_TERMS.findall(b))
                if nraw:
                    r["LAYER4-RAW-GATE"] += 1
                for n in named:
                    if n in cfg_defs or LAYER4_NAME_EXEMPT.match(n):
                        continue
                    if not DECISION_VERB.search(n):
                        r["LAYER4-NON-DECISION"] += 1

    # ---- leaks over WA_* files in the five folders ----
    for folder in LEAK_FOLDERS:
        d = os.path.join(repo, folder)
        if not os.path.isdir(d):
            continue
        for dp, dn, fn in os.walk(d):
            for f in sorted(fn):
                if not f.endswith(".txt") or not f.startswith("WA_"):
                    continue
                if f.startswith("WA_AI_CONFIG"):
                    continue
                s = strip_comments(read(os.path.join(dp, f)))
                r["DATE-LEAK"] += len(DATE_LIT.findall(s))
                r["NUMBER-LEAK"] += len(NUM_TERMS.findall(s))
                r["NOT-MULTI"] += not_multi_count(s)

    # ---- DIFFICULTY-RAW over all of common/ + events/ ----
    for folder in ("common", "events"):
        d = os.path.join(repo, folder)
        if not os.path.isdir(d):
            continue
        for dp, dn, fn in os.walk(d):
            if "script_constants" in dp:
                continue
            for f in sorted(fn):
                if not f.endswith(".txt") or f.startswith("WA_AI_CONFIG"):
                    continue
                s = strip_comments(read(os.path.join(dp, f)))
                r["DIFFICULTY-RAW"] += len(DIFF_RAW.findall(s))

    # ---- CONFIG-LIVE ----
    for p in cfg_glob:
        s = strip_comments(read(p))
        for m in re.finditer(r"(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{", s):
            name = m.group(1)
            i = m.end() - 1
            d = 0
            j = i
            while j < len(s):
                if s[j] == "{":
                    d += 1
                elif s[j] == "}":
                    d -= 1
                    if d == 0:
                        break
                j += 1
            body = s[i:j + 1]
            hit = LIVE_TERMS.search(body)
            if hit and name not in CONFIG_LIVE_EXCEPTIONS:
                details["CONFIG-LIVE"].append(f"{name}: {hit.group(1)}")

    # ---- CONFIG-DEAD ----
    if cfg_defs:
        readers = {n: 0 for n in cfg_defs}
        for folder in ("common", "events", "history"):
            d = os.path.join(repo, folder)
            if not os.path.isdir(d):
                continue
            for dp, dn, fn in os.walk(d):
                for f in fn:
                    if not f.endswith(".txt") or f.startswith("WA_AI_CONFIG"):
                        continue
                    s = strip_comments(read(os.path.join(dp, f)))
                    for m in cfg_ref.finditer(s):
                        readers[m.group(1)] += 1
        # internal chains count too: a CONFIG trigger read by another CONFIG trigger is alive
        # only if the chain reaches an external reader; simple rule: internal reads count.
        for p in cfg_glob:
            s = strip_comments(read(p))
            for m in cfg_ref.finditer(s):
                pass  # definitions match too; handled below by subtracting defs
            for n in cfg_defs:
                occ = len(re.findall(r"\b" + n + r"\b", s))
                defs = len(re.findall(r"(?m)^" + n + r"\s*=\s*\{", s))
                readers[n] += occ - defs
        for n in sorted(cfg_defs):
            if readers[n] == 0 and n not in CONFIG_DEAD_EXCEPTIONS:
                details["CONFIG-DEAD"].append(n)

    # ---- NAME-COLLISION + DUP-DEF over scripted_triggers + scripted_effects ----
    all_defs = {}
    for folder in ("common/scripted_triggers", "common/scripted_effects"):
        d = os.path.join(repo, folder)
        if not os.path.isdir(d):
            continue
        for dp, dn, fn in os.walk(d):
            for f in sorted(fn):
                if not f.endswith(".txt"):
                    continue
                p = os.path.join(dp, f)
                for n in trigger_defs(p):
                    all_defs.setdefault(n, []).append(os.path.relpath(p, repo))
    for n, ps in sorted(all_defs.items()):
        if len(ps) > 1:
            details["DUP-DEF"].append(f"{n}: {', '.join(ps)}")
    stems = {}
    for n in all_defs:
        m = re.match(r"WA_AI_(?:CONFIG_)?([A-Z]+_)?(.+)", n)
        if not m:
            continue
        stem = (m.group(1) or "") + m.group(2)
        stems.setdefault(stem, set()).add(n)
    for stem, names in sorted(stems.items()):
        if len(names) > 1:
            # only flag the CONFIG-vs-non-CONFIG prefix trap, not unrelated coincidences
            has_cfg = any(x.startswith("WA_AI_CONFIG_") for x in names)
            has_plain = any(not x.startswith("WA_AI_CONFIG_") for x in names)
            if has_cfg and has_plain and stem not in NAME_COLLISION_EXCEPTIONS:
                details["NAME-COLLISION"].append(f"{stem}: {', '.join(sorted(names))}")
    return r, details


RATCHET_RULES = ("LAYER4-RAW-GATE", "LAYER4-READS-CONFIG", "LAYER4-NON-DECISION",
                 "DATE-LEAK", "NUMBER-LEAK", "DIFFICULTY-RAW")


def run(repo, update_baseline=False, as_json=False, baseline_path=None):
    baseline_path = baseline_path or BASELINE_PATH
    counts, details = collect(repo)
    findings = []  # (level, rule, message)

    baseline = {}
    if os.path.exists(baseline_path):
        baseline = json.load(open(baseline_path, encoding="utf-8"))
    dirty = False
    for rule in RATCHET_RULES:
        cur = counts[rule]
        if rule not in baseline:
            baseline[rule] = cur
            dirty = True
            findings.append(("INFO", rule, f"baseline initialized at {cur}"))
        elif cur > baseline[rule]:
            if update_baseline:
                baseline[rule] = cur
                dirty = True
                findings.append(("INFO", rule,
                                 f"baseline RAISED to {cur} - a deliberate widening; justify it "
                                 f"in the same commit message"))
            else:
                findings.append(("ERROR", rule,
                                 f"{cur} > baseline {baseline[rule]} - new debt added; convert it "
                                 f"or justify a deliberate scope widening with --update-baseline"))
        elif cur < baseline[rule]:
            if update_baseline:
                baseline[rule] = cur
                dirty = True
                findings.append(("INFO", rule, f"baseline lowered to {cur}"))
            else:
                findings.append(("ERROR", "RATCHET-STALE",
                                 f"{rule}: {cur} < baseline {baseline[rule]} - run "
                                 f"--update-baseline in this same commit"))
        else:
            findings.append(("OK", rule, f"{cur} (== baseline)"))
    if dirty:
        json.dump(baseline, open(baseline_path, "w", encoding="utf-8"),
                  indent=1, sort_keys=True)

    for rule in ("CONFIG-LIVE", "CONFIG-DEAD", "NAME-COLLISION", "DUP-DEF"):
        for d in details[rule]:
            findings.append(("ERROR", rule, d))
    findings.append(("INFO", "NOT-MULTI", f"{counts['NOT-MULTI']} multi-child NOT blocks "
                     f"(measured NOR 2026-08-29; q2e first-child probe still owed)"))

    errors = [f for f in findings if f[0] == "ERROR"]
    if as_json:
        print(json.dumps({"counts": counts, "findings": findings}, indent=1))
    else:
        for lvl, rule, msg in findings:
            if lvl == "OK":
                continue
            print(f"{lvl:5s} {rule:20s} {msg}")
        print(f"\n{len(errors)} ERROR(s); ratchet counts: " +
              "  ".join(f"{k}={counts[k]}" for k in RATCHET_RULES))
    return 1 if errors else 0


# ------------------------------- selftest ---------------------------------------------------

FIXTURES = {
    # each fixture is (relative path, content, rule that MUST fire on it)
    "LAYER4-RAW-GATE": ("common/ai_strategy/WA_AI_MILITARY_X.txt",
                        "x = { enable = { date > 1942.1.1 } }"),
    "LAYER4-READS-CONFIG": ("common/ai_strategy/WA_AI_MILITARY_Y.txt",
                            "y = { enable = { WA_AI_CONFIG_MILITARY_is_test_thing = yes } }"),
    "LAYER4-NON-DECISION": ("common/ai_strategy/WA_AI_MILITARY_Z.txt",
                            "z = { enable = { WA_AI_MILITARY_is_axis_member_fx = yes } }"),
    "DATE-LEAK": ("common/scripted_triggers/WA_AI_MILITARY_triggers.txt",
                  "t = { date > 1941.6.22 }"),
    "NUMBER-LEAK": ("common/scripted_effects/WA_AI_FOO_effects.txt",
                    "e = { if = { limit = { num_of_military_factories > 20 } } }"),
    "DIFFICULTY-RAW": ("common/decisions/z_test.txt",
                       "d = { available = { difficulty > 1 } }"),
    "CONFIG-LIVE": ("__cfg__", "WA_AI_CONFIG_bad_live = { any_enemy_country = { exists = yes } }"),
    "CONFIG-DEAD": ("__cfg__", "WA_AI_CONFIG_never_read = { always = no }"),
    "NAME-COLLISION": ("common/scripted_triggers/WA_AI_MILITARY_triggers2.txt",
                       "WA_AI_MILITARY_is_test_thing = { always = no }"),
    "DUP-DEF": ("common/scripted_effects/WA_dup_effects.txt",
                "WA_dup_one = { }\nWA_dup_one = { }"),
}


def selftest():
    failures = []
    for rule, (rel, content) in FIXTURES.items():
        with tempfile.TemporaryDirectory() as td:
            # minimal healthy skeleton: a CONFIG file whose one trigger is read once
            cfg = ("WA_AI_CONFIG_MILITARY_is_test_thing = { original_tag = GER }\n")
            reader = "r = { enable = { WA_AI_CONFIG_MILITARY_nothing = yes } }\n"
            os.makedirs(os.path.join(td, "common", "scripted_triggers"))
            os.makedirs(os.path.join(td, "common", "scripted_effects"))
            os.makedirs(os.path.join(td, "common", "ai_strategy"))
            os.makedirs(os.path.join(td, "common", "decisions"))
            os.makedirs(os.path.join(td, "events"))
            if rel == "__cfg__":
                cfg += content + "\n"
            cfgp = os.path.join(td, "common", "scripted_triggers", "WA_AI_CONFIG.txt")
            open(cfgp, "w", encoding="utf-8").write(cfg)
            # a live external reader for is_test_thing so it is not CONFIG-DEAD noise
            open(os.path.join(td, "common", "scripted_triggers", "WA_AI_OTHER_triggers.txt"),
                 "w", encoding="utf-8").write(
                "WA_AI_OTHER_reader = { WA_AI_CONFIG_MILITARY_is_test_thing = yes }\n")
            if rel != "__cfg__":
                p = os.path.join(td, rel)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w", encoding="utf-8").write(content + "\n")
            counts, details = collect(td)
            fired = counts.get(rule, 0) > 0 or bool(details.get(rule))
            # CONFIG-LIVE fixture name must not be excepted
            if not fired:
                failures.append(rule)
    if failures:
        print("SELFTEST FAILED - rules with a fixture that did not fire:", ", ".join(failures))
        return 1
    print(f"selftest OK - {len(FIXTURES)} rules, each fired on the fixture built to break it")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return run(REPO, update_baseline=a.update_baseline, as_json=a.json)


if __name__ == "__main__":
    raise SystemExit(main())
