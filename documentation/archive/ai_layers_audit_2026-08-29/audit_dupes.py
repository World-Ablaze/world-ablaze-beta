import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections, json

os.chdir(_REPO)

def topdefs(path):
    s = open(path, encoding='utf-8-sig', errors='ignore').read()
    return re.findall(r'(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{', s)

owner = collections.defaultdict(list)
for folder in ('common/scripted_triggers', 'common/scripted_effects'):
    for f in sorted(os.listdir(folder)):
        if not f.endswith('.txt'):
            continue
        p = folder + '/' + f
        for d in topdefs(p):
            owner[d].append(p)

print("=== DUPLICATE DEFINITIONS (same name, 2+ places) ===")
for k, v in sorted(owner.items()):
    if len(v) > 1:
        print("  %-55s %s" % (k, v))

print()
print("=== WA_AI_* triggers defined OUTSIDE their prefix file ===")
mis = []
for k, v in sorted(owner.items()):
    if not k.startswith('WA_AI_'):
        continue
    for p in v:
        base = os.path.basename(p)
        if 'scripted_triggers' not in p:
            continue
        # prefix after WA_AI_
        parts = k.split('_')
        mis.append((k, base))

# naming families inside CONFIG
cfg = 'common/scripted_triggers/WA_AI_CONFIG.txt'
cd = topdefs(cfg)
fam = collections.Counter()
for d in cd:
    m = re.match(r'(WA_AI_[A-Z]+(?:_[A-Z]+)?)_', d)
    fam[m.group(1) if m else d] += 1
print("=== CONFIG naming families ===")
for k, v in fam.most_common():
    print("  %-40s %d" % (k, v))

print()
print("=== CONFIG defs NOT starting with WA_AI_CONFIG_ ===")
for d in cd:
    if not d.startswith('WA_AI_CONFIG_'):
        print("  ", d)
