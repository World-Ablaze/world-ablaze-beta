import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)

TOKEN = re.compile(r'([A-Za-z_][A-Za-z0-9_@:.]*)\s*=\s*\{|([A-Za-z_][A-Za-z0-9_@:.]*)\s*[=<>]+\s*([^\s{}]+)|(\{)|(\})')

def scan(path):
    lines = open(path, encoding='utf-8-sig', errors='ignore').read().split('\n')
    # build a flat token stream with line numbers
    toks = []
    for i, l in enumerate(lines):
        code = re.sub(r'#.*', '', l)
        for m in TOKEN.finditer(code):
            if m.group(1):
                toks.append(('OPEN', m.group(1), i + 1))
            elif m.group(4):
                toks.append(('OPEN', '?', i + 1))
            elif m.group(5):
                toks.append(('CLOSE', None, i + 1))
            else:
                toks.append(('LEAF', m.group(2), i + 1))
    out = []
    stack = []  # each: [name, line, child_count]
    for kind, name, ln in toks:
        if kind == 'OPEN':
            if stack:
                stack[-1][2] += 1
            stack.append([name, ln, 0])
        elif kind == 'LEAF':
            if stack:
                stack[-1][2] += 1
        else:
            if stack:
                n, l0, cc = stack.pop()
                if n.upper() == 'NOT' and cc > 1:
                    out.append((l0, cc))
    return out

tot = 0
per = collections.Counter()
for folder in ('common/scripted_triggers', 'common/scripted_effects', 'common/ai_strategy', 'events'):
    for dp, dn, fn in os.walk(folder):
        for f in sorted(fn):
            if not f.endswith('.txt') or not f.startswith('WA_'):
                continue
            p = (dp + '/' + f).replace('\\', '/')
            r = scan(p)
            if r:
                per[p] = len(r)
                tot += len(r)

print("=== multi-child NOT = { ... } blocks in WA_* AI files (NAND vs NOR hazard) ===")
for k, v in per.most_common(25):
    print("  %-72s %d" % (k, v))
print("TOTAL:", tot)
