# -*- coding: utf-8 -*-
"""revue_reverify.py - independent re-derivation script of documentation/REVUE_LAYERS_REFACTOR.md.
Written for the adversarial review, from the claims, not from the audit scripts (own tokenizer).
Portable: repo root derived from this file's location. Independent re-derivation of the load-bearing MEASURED numbers in
WA_AI_LAYERS_REFACTOR_PROPOSAL.md. Written from the claims, not from the audit scripts.
"""
import os, re, collections, sys
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
os.chdir(REPO)

def read(p):
    with open(p, encoding="utf-8-sig", errors="ignore") as f:
        return f.read()

def strip_comments(s):
    return re.sub(r"#[^\n]*", "", s)

# ---------- 1. block census in common/ai_strategy/WA_AI_* ----------
RAW_TERMS = re.compile(r"\b(date|has_war_with|has_war|num_of_\w+|has_army_manpower|has_navy_size|"
    r"has_completed_focus|has_country_flag|controls_state|owns_state|has_tech|"
    r"is_in_faction_with|surrender_progress|num_divisions|has_idea|has_government|"
    r"divisions_in_state|country_exists|exists|has_capitulated|threat|"
    r"strength_ratio|is_subject_of|has_full_control_of_state)\s*[=<>]")
NAMED = re.compile(r"\bWA_AI_\w+\s*=\s*(?:yes|no)\b")
CFG = re.compile(r"\bWA_AI_CONFIG\w*\s*=\s*(?:yes|no)\b")

def blocks_of(s, keys=("allowed","enable")):
    """Own implementation: tokenizing brace walk, not regex-span."""
    out = []
    # token stream of names, '=', '{', '}'
    toks = re.findall(r"[A-Za-z0-9_.:@\-]+|[{}=<>]", s)
    i = 0
    while i < len(toks):
        if toks[i] in keys and i+2 < len(toks) and toks[i+1] == "=" and toks[i+2] == "{":
            d = 1; j = i+3; body = []
            while j < len(toks) and d:
                if toks[j] == "{": d += 1
                elif toks[j] == "}": d -= 1
                if d: body.append(toks[j])
                j += 1
            out.append(" ".join(body))
            i = j
        else:
            i += 1
    return out

agg = collections.defaultdict(collections.Counter)
cfg_reads_ai_strategy = 0
for f in sorted(os.listdir("common/ai_strategy")):
    if not (f.startswith("WA_AI_") and f.endswith(".txt")):
        continue
    m = re.match(r"WA_AI_([A-Z]+)", f)
    system = m.group(1) if m else "OTHER"
    s = strip_comments(read("common/ai_strategy/" + f))
    agg[system]["files"] += 1
    cfg_reads_ai_strategy += len(CFG.findall(s))
    for b in blocks_of(s):
        nraw = len(RAW_TERMS.findall(b)); nnamed = len(NAMED.findall(b))
        agg[system]["blocks"] += 1
        if nraw and not nnamed: agg[system]["raw"] += 1
        elif nraw and nnamed:   agg[system]["mixed"] += 1
        elif nnamed:            agg[system]["named"] += 1
        else:                   agg[system]["trivial"] += 1

tot = collections.Counter()
print("== 1. census common/ai_strategy/WA_AI_* (my tokenizer) ==")
for k in sorted(agg):
    c = agg[k]; tot.update(c)
    print(f"  {k:12s} files={c['files']:4d} blocks={c['blocks']:5d} raw={c['raw']:4d} mixed={c['mixed']:4d} named={c['named']:4d} trivial={c['trivial']:5d} convert={c['raw']+c['mixed']}")
print(f"  TOTAL        files={tot['files']} blocks={tot['blocks']} raw={tot['raw']} mixed={tot['mixed']} named={tot['named']} trivial={tot['trivial']} convert={tot['raw']+tot['mixed']}")
print(f"  direct CONFIG reads from common/ai_strategy (all WA_AI_ files, whole file): {cfg_reads_ai_strategy}")

# ---------- 2. can_absorb readers ----------
n = 0; files = set()
for dp, dn, fn in os.walk("common"):
    for f in fn:
        if not f.endswith(".txt"): continue
        p = os.path.join(dp, f)
        s = strip_comments(read(p))
        hits = re.findall(r"\bWA_AI_EQUIPMENT_can_absorb_\w+", s)
        # exclude the defining file's definitions? count reads = usages with '= yes/no' plus defs
        if hits:
            # separate defs (name = {) from reads
            defs = re.findall(r"\bWA_AI_EQUIPMENT_can_absorb_\w+\s*=\s*\{", s)
            reads = len(hits) - len(defs)
            if reads:
                n += reads; files.add(p)
for dp, dn, fn in os.walk("events"):
    for f in fn:
        if not f.endswith(".txt"): continue
        p = os.path.join(dp, f)
        s = strip_comments(read(p))
        hits = re.findall(r"\bWA_AI_EQUIPMENT_can_absorb_\w+\s*=\s*(?:yes|no)", s)
        if hits: n += len(hits); files.add(p)
print(f"\n== 2. can_absorb reads: {n} in {len(files)} files ==")

# ---------- 3. dates + thresholds, their scope ----------
DATE = re.compile(r"\bdate\s*[<>=]+\s*(\d{4}\.\d{1,2}\.\d{1,2})")
NUM = re.compile(r"\b(num_of_\w+|has_army_manpower|has_navy_size|num_divisions|has_war_support|has_stability|surrender_progress|arms_factory_level|threat|has_manpower|amount_research_slots|has_political_power|command_power|has_equipment)\b[^\n]{0,40}?([<>]=?)\s*(-?[\d.]+)")
dcount = collections.Counter(); ncount = collections.Counter(); ddist = collections.Counter()
for folder in ("common/scripted_triggers","common/scripted_effects","common/ai_strategy","events","common/on_actions"):
    for dp, dn, fn in os.walk(folder):
        for f in sorted(fn):
            if not f.endswith(".txt") or not f.startswith("WA_"): continue
            p = (dp + "/" + f).replace("\\","/")
            s = strip_comments(read(p))
            zone = "CONFIG" if f.startswith("WA_AI_CONFIG") else folder
            d = DATE.findall(s); nn = NUM.findall(s)
            dcount[zone] += len(d); ncount[zone] += len(nn)
            for x in d: ddist[x] += 1
d_out = sum(v for k,v in dcount.items() if k != "CONFIG")
n_out = sum(v for k,v in ncount.items() if k != "CONFIG")
print(f"\n== 3. literal dates outside CONFIG: {d_out} (CONFIG: {dcount['CONFIG']}) ; thresholds outside CONFIG: {n_out} (CONFIG: {ncount['CONFIG']}) ==")
print("   by zone dates:", dict(dcount))
print("   top dates:", ddist.most_common(6))

# ---------- 4. CONFIG triggers: total, dead, purity ----------
cfg_src = read("common/scripted_triggers/WA_AI_CONFIG.txt")
cfg_nc = strip_comments(cfg_src)
defs = re.findall(r"^([A-Za-z0-9_]+)\s*=\s*\{", cfg_nc, re.M)
print(f"\n== 4. CONFIG triggers defined: {len(defs)} ==")
# dead = never read outside CONFIG (scan common/, events/, history/)
all_text = {}
for folder in ("common","events","history"):
    for dp, dn, fn in os.walk(folder):
        for f in fn:
            if f.endswith(".txt") or f.endswith(".lua"):
                p = os.path.join(dp,f)
                all_text[p] = strip_comments(read(p))
dead = []
for name in defs:
    ext = 0
    pat = re.compile(r"\b" + re.escape(name) + r"\b")
    for p, s in all_text.items():
        if p.endswith("WA_AI_CONFIG.txt"): continue
        ext += len(pat.findall(s))
    if ext == 0: dead.append(name)
print(f"   dead (no read outside CONFIG in common/+events/+history/): {len(dead)}")
for d in dead: print("     -", d)

FORBID = re.compile(r"\b(any_enemy_country|any_country_of|has_war\w*|controls_state|owns_state|surrender_progress|check_variable|num_divisions|any_other_country|all_country|any_country\b|any_neighbor_country|is_in_faction_with)\b")
# purity per the proposal's frontier-1/2 test (their allowed list keeps is_in_faction_with OUT? proposal says
# interdit includes scopes of another country; but 3 faction triggers stay in CONFIG per 5.3. Count both ways.
impure = [n for n, body in re.findall(r"^([A-Za-z0-9_]+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})", cfg_nc, re.M)
          if FORBID.search(body)]
print(f"   impure (broad list incl. is_in_faction_with/any_*): {len(impure)} -> {impure}")

# ---------- 5. use_armored_divisions readers ----------
pat = re.compile(r"\bWA_AI_CONFIG_DIVISIONS_use_armored_divisions\b")
print("\n== 5. readers of use_armored_divisions ==")
for p, s in sorted(all_text.items()):
    c = len(pat.findall(s))
    if c: print(f"   {p}: {c}")

# ---------- 6. WA_AI_major_country ----------
print("\n== 6. WA_AI_major_country readers (files) ==")
pat = re.compile(r"\bWA_AI_major_country\b")
for p, s in sorted(all_text.items()):
    c = len(pat.findall(s))
    if c: print(f"   {p}: {c}")

# ---------- 7. NOT multi-child + if-in-OR counts ----------
def count_not_multi(s):
    """NOT blocks with >= 2 direct children (token-level)."""
    toks = re.findall(r"[A-Za-z0-9_.:@\-]+|[{}=<>]", s)
    cnt = 0
    for i in range(len(toks)):
        if toks[i] == "NOT" and i+2 < len(toks) and toks[i+1] == "=" and toks[i+2] == "{":
            d = 1; j = i+3; children = 0; expect_key = True
            while j < len(toks) and d:
                t = toks[j]
                if t == "{": d += 1
                elif t == "}": d -= 1
                elif d == 1 and t == "=":
                    children += 1
                j += 1
            if children >= 2: cnt += 1
    return cnt

nm = 0; ifor = 0
for folder in ("common","events"):
    for dp, dn, fn in os.walk(folder):
        for f in fn:
            if not f.endswith(".txt") or not f.startswith("WA_"): continue
            s = strip_comments(read(os.path.join(dp,f)))
            nm += count_not_multi(s)
            # if directly inside OR: token walk
            toks = re.findall(r"[A-Za-z0-9_.:@\-]+|[{}=<>]", s)
            for i in range(len(toks)):
                if toks[i] == "OR" and i+2 < len(toks) and toks[i+1] == "=" and toks[i+2] == "{":
                    d = 1; j = i+3
                    while j < len(toks) and d:
                        t = toks[j]
                        if t == "{": d += 1
                        elif t == "}": d -= 1
                        elif d == 1 and t == "if" and j+1 < len(toks) and toks[j+1] == "=":
                            ifor += 1
                        j += 1
print(f"\n== 7. NOT multi-child in WA_* (common/+events/): {nm} ; if-directly-in-OR: {ifor} ==")

# ---------- 8. WA_AI_DIFFICULTY_* reads ----------
pat = re.compile(r"\bWA_AI_DIFFICULTY_\w+\b")
total = 0; defs_d = 0
for p, s in all_text.items():
    hits = pat.findall(s)
    if p.endswith("WA_AI_CONFIG.txt"):
        defs_d += len(re.findall(r"^WA_AI_DIFFICULTY_\w+\s*=\s*\{", s, re.M))
    total += len(hits)
print(f"\n== 8. WA_AI_DIFFICULTY_* occurrences total (common/events/history incl defs): {total} (defs in CONFIG: {defs_d}) ==")

# ---------- 9. chain depth of WA_AI_can_upgrade_economy_law ----------
# build def map from all scripted_triggers files
trig_defs = {}
for dp, dn, fn in os.walk("common/scripted_triggers"):
    for f in fn:
        if not f.endswith(".txt"): continue
        s = strip_comments(read(os.path.join(dp,f)))
        for m in re.finditer(r"^([A-Za-z0-9_]+)\s*=\s*\{", s, re.M):
            name = m.group(1)
            # capture body by brace walk from m.end()-1
            i = m.end()-1; d=0; j=i
            while j < len(s):
                if s[j]=="{": d+=1
                elif s[j]=="}":
                    d-=1
                    if d==0: break
                j+=1
            trig_defs[name] = s[i:j+1]
def depth(name, seen=None):
    if seen is None: seen = set()
    if name in seen: return 0
    seen = seen | {name}
    body = trig_defs.get(name)
    if body is None: return 0
    subs = set(re.findall(r"\b(WA_AI_\w+)\s*=\s*(?:yes|no)", body))
    if not subs: return 1
    return 1 + max(depth(s2, seen) for s2 in subs)
print(f"\n== 9. chain depth WA_AI_can_upgrade_economy_law: {depth('WA_AI_can_upgrade_economy_law')} ==")
maxd = max((depth(n), n) for n in trig_defs if n.startswith("WA_AI_"))
print(f"   max depth over all WA_AI_ triggers: {maxd}")
