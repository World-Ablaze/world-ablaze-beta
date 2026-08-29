import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)
PSEUDO = {'ROOT', 'PREV', 'THIS', 'FROM', 'OWNER', 'CONTROLLER', 'OVERLORD', 'CAPITAL'}
SCOPES = {'CONTROLLER', 'OWNER', 'OVERLORD', 'any_country', 'any_other_country', 'all_country',
          'any_enemy_country', 'any_allied_country', 'any_neighbor_country', 'every_country',
          'any_state', 'any_owned_state', 'any_controlled_state', 'CAPITAL', 'any_subject_country',
          'FROM', 'PREV', 'ROOT', 'THIS'}

hits = collections.defaultdict(list)
for dp, dn, fn in os.walk('common/ai_strategy'):
    for f in sorted(fn):
        if not f.endswith('.txt') or not f.startswith('WA_AI_'):
            continue
        p = (dp + '/' + f).replace('\\', '/')
        lines = open(dp + '/' + f, encoding='utf-8-sig', errors='ignore').read().split('\n')
        stack = []
        for i, l in enumerate(lines):
            code = re.sub(r'#.*', '', l)
            for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*|\d+)\s*=\s*\{|\{|\}|((?:original_)?tag)\s*=\s*([A-Za-z][A-Za-z0-9]{2,})', code):
                t = m.group(0)
                if m.group(2):
                    val = m.group(3)
                    if val in PSEUDO:
                        continue
                    gate = None
                    for x in stack:
                        if x in ('allowed', 'enable'):
                            gate = x
                    if not gate:
                        continue
                    # inside a nested country/state scope after the gate?
                    gi = len(stack) - 1 - stack[::-1].index(gate)
                    nested = [x for x in stack[gi + 1:] if x in SCOPES or x.isdigit()]
                    hits[p].append((i + 1, gate, bool(nested), l.strip()))
                    continue
                if t == '}':
                    if stack:
                        stack.pop()
                elif t == '{':
                    stack.append('?')
                else:
                    stack.append(m.group(1))

print("=== WA_AI_* ai_strategy: literal tag in allowed/enable (ROOT-scope gating only) ===")
tot = 0
for p in sorted(hits):
    direct = [h for h in hits[p] if not h[2]]
    if not direct:
        continue
    layer = 'COUNTRY' if '_COUNTRY_' in p else ('DEFAULT' if '_DEFAULT' in p else ('REGION' if '_REGION' in p else ('FACTION' if '_FACTION' in p else 'OTHER')))
    if layer == 'COUNTRY':
        continue
    tot += len(direct)
    print("  [%s] %s  -> %d" % (layer, os.path.basename(p), len(direct)))
    for n, g, nest, l in direct[:40]:
        print("        L%-6d (%s) %s" % (n, g, l))
print("TOTAL non-COUNTRY-layer gating tags:", tot)
