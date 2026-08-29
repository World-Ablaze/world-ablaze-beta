import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)

# ai_strategy: find tag/original_tag inside allowed={} or enable={} in non-COUNTRY layer files
hits = collections.defaultdict(list)
for dp, dn, fn in os.walk('common/ai_strategy'):
    for f in sorted(fn):
        if not f.endswith('.txt'):
            continue
        p = (dp + '/' + f).replace('\\', '/')
        s = open(dp + '/' + f, encoding='utf-8-sig', errors='ignore').read()
        lines = s.split('\n')
        stack = []
        ingate = 0
        for i, l in enumerate(lines):
            code = re.sub(r'#.*', '', l)
            for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{|\{|\}|((?:original_)?tag)\s*=\s*([A-Z][A-Z0-9]{2})', code):
                t = m.group(0)
                if m.group(2):
                    if any(x in ('allowed', 'enable') for x in stack):
                        hits[p].append((i + 1, l.strip()))
                    continue
                if t == '}':
                    if stack:
                        stack.pop()
                elif t == '{':
                    stack.append('?')
                else:
                    stack.append(m.group(1))

country = [p for p in hits if '_COUNTRY_' in p]
other = [p for p in hits if '_COUNTRY_' not in p]
print("=== ai_strategy: tag gating in allowed/enable, NON-COUNTRY layer (rule-4 zone) ===")
for p in sorted(other):
    print("  %-72s %d" % (p, len(hits[p])))
    for n, l in hits[p][:6]:
        print("        L%-6d %s" % (n, l))
print()
print("=== COUNTRY-layer files (permitted) ===", len(country), "files,", sum(len(hits[p]) for p in country), "lines")
