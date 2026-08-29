import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os

os.chdir(_REPO)

# find `if = {` whose nearest enclosing block opener is `OR = {`
targets = []
for folder in ('common/scripted_triggers', 'common/scripted_effects', 'common/ai_strategy', 'events'):
    for dp, dn, fn in os.walk(folder):
        for f in fn:
            if not f.endswith('.txt'):
                continue
            if not (f.startswith('WA_') or 'WA_AI' in f):
                continue
            p = (dp + '/' + f).replace('\\', '/')
            s = open(p, encoding='utf-8-sig', errors='ignore').read()
            lines = s.split('\n')
            stack = []
            for i, l in enumerate(lines):
                code = re.sub(r'#.*', '', l)
                # tokens
                for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{|\{|\}', code):
                    t = m.group(0)
                    if t == '}':
                        if stack:
                            stack.pop()
                    elif t == '{':
                        stack.append('?')
                    else:
                        key = m.group(1)
                        if key == 'if' and stack and stack[-1] == 'OR':
                            targets.append((p, i + 1, l.strip()))
                        stack.append(key)
print("=== `if = {` nested DIRECTLY inside `OR = {` (vacuous-true hazard) ===")
for p, n, l in targets:
    print("  %s:%d  %s" % (p, n, l))
print(len(targets), "occurrences")
