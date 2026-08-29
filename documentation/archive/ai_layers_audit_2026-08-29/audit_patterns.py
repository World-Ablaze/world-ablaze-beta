import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)

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

norm = collections.Counter()
where = collections.defaultdict(set)
for dp, dn, fn in os.walk('common/ai_strategy'):
    for f in sorted(fn):
        if not f.endswith('.txt') or not f.startswith('WA_AI_'):
            continue
        p = (dp + '/' + f).replace('\\', '/')
        for b in gate_blocks(dp + '/' + f):
            k = re.sub(r'\s+', ' ', b).strip()
            if len(k) < 12 or len(k) > 400:
                continue
            norm[k] += 1
            where[k].add(os.path.basename(p))

print("=== blocs allowed/enable IDENTIQUES repetes (candidats a un trigger nomme) ===")
tot_dup = 0
for k, v in norm.most_common(20):
    if v < 3:
        break
    tot_dup += v - 1
    print("  x%-3d  %-3d fichiers  %s" % (v, len(where[k]), k[:150]))
print()
print("blocs dupliques >=3x :", sum(v for k, v in norm.items() if v >= 3),
      " / blocs uniques :", len(norm))
print("lignes economisables si chaque bloc duplique >=3x devient un trigger nomme :", tot_dup)
