import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections, json

os.chdir(_REPO)
OUT = _HERE + '/'

cfg = 'common/scripted_triggers/WA_AI_CONFIG.txt'
txt = open(cfg, encoding='utf-8-sig').read()
defs = re.findall(r'(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{', txt)
defset = set(defs)
big = re.compile(r'\b(' + '|'.join(sorted(defset, key=len, reverse=True)) + r')\b')

counts = collections.Counter()
sites = collections.defaultdict(collections.Counter)
skipdirs = {'.git', 'tests', 'documentation', '.claude'}
for dirpath, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skipdirs]
    for f in files:
        if not f.endswith('.txt'):
            continue
        p = (dirpath + '/' + f).replace('\\', '/').lstrip('./')
        try:
            s = open(dirpath + '/' + f, encoding='utf-8-sig', errors='ignore').read()
        except Exception:
            continue
        for m in big.finditer(s):
            counts[m.group(1)] += 1
            sites[m.group(1)][p] += 1

internal = collections.Counter()
for m in big.finditer(txt):
    internal[m.group(1)] += 1

lines = []
lines.append("name\text_reads\text_files\tinternal_refs\tfiles")
for d in sorted(defset):
    ext = counts[d] - internal[d]
    fl = {p: n for p, n in sites[d].items() if not p.endswith('WA_AI_CONFIG.txt')}
    lines.append("%s\t%d\t%d\t%d\t%s" % (d, ext, len(fl), internal[d] - 1, ';'.join(sorted(fl))))
open(_os.path.join(_HERE, 'config_usage.tsv'), 'w', encoding='utf-8').write('\n'.join(lines))

dead = [d for d in sorted(defset) if counts[d] - internal[d] <= 0]
print("=== TOTAL DEFS:", len(defset))
print("=== NEVER READ OUTSIDE CONFIG (%d) ===" % len(dead))
for d in dead:
    print("   %-58s internal=%d" % (d, internal[d] - 1))
