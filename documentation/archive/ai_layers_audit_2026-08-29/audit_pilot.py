import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)
RAW = re.compile(r'\b(date|has_war_with|has_war|num_of_\w+|has_army_manpower|has_navy_size|'
                 r'has_completed_focus|has_country_flag|controls_state|owns_state|has_tech|'
                 r'is_in_faction_with|surrender_progress|num_divisions|has_idea|has_government|'
                 r'divisions_in_state|country_exists|exists|has_capitulated|threat|'
                 r'strength_ratio|is_subject_of|has_full_control_of_state)\s*[=<>]')
NAMED = re.compile(r'\bWA_AI_\w+\s*=\s*(?:yes|no)\b')
CFG = re.compile(r'\bWA_AI_CONFIG\w*\s*=\s*(?:yes|no)\b')

def gate_blocks(path):
    s = open(path, encoding='utf-8-sig', errors='ignore').read()
    s = re.sub(r'#.*', '', s)
    out = []
    for m in re.finditer(r'\b(allowed|enable)\s*=\s*\{', s):
        i = m.end() - 1
        d = 0
        j = i
        while j < len(s):
            if s[j] == '{':
                d += 1
            elif s[j] == '}':
                d -= 1
                if d == 0:
                    break
            j += 1
        out.append(s[i:j + 1])
    return out

def system(f):
    m = re.match(r'WA_AI_([A-Z]+)', f)
    return m.group(1) if m else 'OTHER'

agg = collections.defaultdict(lambda: collections.Counter())
for dp, dn, fn in os.walk('common/ai_strategy'):
    for f in sorted(fn):
        if not f.endswith('.txt') or not f.startswith('WA_AI_'):
            continue
        sys_ = system(f)
        agg[sys_]['files'] += 1
        for b in gate_blocks(dp + '/' + f):
            nraw = len(RAW.findall(b))
            nnamed = len(NAMED.findall(b))
            agg[sys_]['blocks'] += 1
            agg[sys_]['cfgreads'] += len(CFG.findall(b))
            if nraw and not nnamed:
                agg[sys_]['raw_only'] += 1
            elif nraw and nnamed:
                agg[sys_]['mixed'] += 1
            elif nnamed:
                agg[sys_]['named_only'] += 1
            else:
                agg[sys_]['trivial'] += 1

print("%-14s %6s %7s %8s %7s %7s %8s %9s" % ('SYSTEME', 'fich', 'blocs', 'bruts', 'mixtes', 'nommes', 'triviaux', 'lit CONFIG'))
rows = sorted(agg.items(), key=lambda x: -(x[1]['raw_only'] + x[1]['mixed']))
for k, c in rows:
    conv = c['raw_only'] + c['mixed']
    print("%-14s %6d %7d %8d %7d %7d %8d %9d   -> a convertir: %d" % (
        k, c['files'], c['blocks'], c['raw_only'], c['mixed'], c['named_only'], c['trivial'], c['cfgreads'], conv))
