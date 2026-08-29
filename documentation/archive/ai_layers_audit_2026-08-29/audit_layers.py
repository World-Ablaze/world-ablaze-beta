import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)

# --- 1. Layer-3 discipline: do ai_strategy allowed/enable blocks call named WA_AI triggers,
#        or do they inline raw engine triggers?
RAW = re.compile(r'\b(date|has_war_with|has_war|num_of_\w+|has_army_manpower|has_navy_size|'
                 r'has_completed_focus|has_country_flag|controls_state|owns_state|has_tech|'
                 r'is_in_faction_with|surrender_progress|num_divisions|has_idea|has_government|'
                 r'divisions_in_state|country_exists|exists|has_capitulated|threat|'
                 r'strength_ratio|is_subject_of|has_full_control_of_state)\s*[=<>]')
NAMED = re.compile(r'\bWA_AI_\w+\s*=\s*yes\b|\bWA_AI_\w+\s*=\s*no\b')

def gate_blocks(path):
    """yield (kind, text) for each allowed={} / enable={} block"""
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
        out.append((m.group(1), s[i:j + 1]))
    return out

stats = collections.Counter()
perfile = collections.defaultdict(lambda: [0, 0, 0])  # named-only, raw-only, mixed
for dp, dn, fn in os.walk('common/ai_strategy'):
    for f in sorted(fn):
        if not f.endswith('.txt') or not f.startswith('WA_AI_'):
            continue
        p = (dp + '/' + f).replace('\\', '/')
        for kind, body in gate_blocks(dp + '/' + f):
            nraw = len(RAW.findall(body))
            nnamed = len(NAMED.findall(body))
            stats['blocks'] += 1
            stats['raw_terms'] += nraw
            stats['named_terms'] += nnamed
            if nnamed and not nraw:
                stats['named_only'] += 1
                perfile[p][0] += 1
            elif nraw and not nnamed:
                stats['raw_only'] += 1
                perfile[p][1] += 1
            elif nraw and nnamed:
                stats['mixed'] += 1
                perfile[p][2] += 1
            else:
                stats['empty'] += 1

print("=== ai_strategy WA_AI_*: discipline des blocs allowed/enable ===")
print("  blocs totaux              ", stats['blocks'])
print("  100%% triggers nommes      %d  (%.0f%%)" % (stats['named_only'], 100.0 * stats['named_only'] / max(1, stats['blocks'])))
print("  100%% triggers moteur bruts %d  (%.0f%%)" % (stats['raw_only'], 100.0 * stats['raw_only'] / max(1, stats['blocks'])))
print("  mixtes                    %d  (%.0f%%)" % (stats['mixed'], 100.0 * stats['mixed'] / max(1, stats['blocks'])))
print("  triviaux / vides          ", stats['empty'])
print("  termes moteur bruts       ", stats['raw_terms'])
print("  termes nommes             ", stats['named_terms'])

print()
print("=== pires fichiers (blocs 100%% bruts) ===")
for p, (n, r, m) in sorted(perfile.items(), key=lambda x: -x[1][1])[:12]:
    print("  %-68s brut=%-4d mixte=%-4d nomme=%d" % (os.path.basename(p), r, m, n))

# --- 2. indirection depth: WA_AI trigger -> WA_AI trigger call graph
defs = {}
for folder in ('common/scripted_triggers',):
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.txt'):
            continue
        s = open(folder + '/' + f, encoding='utf-8-sig', errors='ignore').read()
        s2 = re.sub(r'#.*', '', s)
        lines = s2.split('\n')
        i = 0
        while i < len(lines):
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{', lines[i])
            if m:
                name = m.group(1)
                d = lines[i].count('{') - lines[i].count('}')
                body = []
                j = i + 1
                while j < len(lines) and d > 0:
                    d += lines[j].count('{') - lines[j].count('}')
                    if d > 0:
                        body.append(lines[j])
                    j += 1
                defs[name] = (folder + '/' + f, ' '.join(body))
                i = j
            else:
                i += 1

wa = {k: v for k, v in defs.items() if k.startswith('WA_AI_')}
edges = {}
for k, (p, b) in wa.items():
    edges[k] = set(x for x in re.findall(r'\b(WA_AI_\w+)\s*=\s*(?:yes|no)\b', b) if x in wa and x != k)

memo = {}
def depth(n, seen=None):
    if seen is None:
        seen = set()
    if n in seen:
        return 0
    if n in memo:
        return memo[n]
    seen = seen | {n}
    d = 1 + max([depth(c, seen) for c in edges.get(n, ())] or [0])
    memo[n] = d
    return d

dd = collections.Counter()
for k in wa:
    dd[depth(k)] += 1
print()
print("=== profondeur actuelle des chaines de triggers WA_AI_ (1 = feuille) ===")
for k in sorted(dd):
    print("  profondeur %d : %d triggers" % (k, dd[k]))
deepest = sorted(wa, key=lambda x: -depth(x))[:8]
print("  plus profonds :", ', '.join('%s(%d)' % (x, depth(x)) for x in deepest))
