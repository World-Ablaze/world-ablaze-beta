import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)
cfg = 'common/scripted_triggers/WA_AI_CONFIG.txt'
lines = open(cfg, encoding='utf-8-sig').read().split('\n')
blocks = {}
i = 0
while i < len(lines):
    m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{', lines[i])
    if m:
        name = m.group(1)
        depth = lines[i].count('{') - lines[i].count('}')
        body = []
        j = i + 1
        while j < len(lines) and depth > 0:
            depth += lines[j].count('{') - lines[j].count('}')
            if depth > 0:
                body.append(lines[j])
            j += 1
        key = ' '.join(x for x in (re.sub(r'#.*', '', b).strip() for b in body) if x)
        blocks.setdefault(key, []).append((name, i + 1))
        i = j
    else:
        i += 1

print("=== CONFIG triggers with BYTE-IDENTICAL bodies ===")
for k, v in blocks.items():
    if len(v) > 1:
        print("  body: %s" % (k[:110]))
        for n, ln in v:
            print("        L%-6d %s" % (ln, n))
        print()
