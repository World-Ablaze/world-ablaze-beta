import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import collections, os

OUT = _HERE + '/'
rows = [l.split('\t') for l in open(_os.path.join(_HERE, 'config_usage.tsv'), encoding='utf-8').read().split('\n')[1:] if l.strip()]

byfile = collections.Counter()
bydir = collections.Counter()
for name, ext, nf, internal, files in rows:
    for p in files.split(';'):
        if not p:
            continue
        byfile[p] += 1
        bydir[os.path.dirname(p)] += 1

print("=== CONFIG readers by directory (distinct triggers read) ===")
for k, v in bydir.most_common():
    print("  %-45s %d" % (k, v))
print()
print("=== Top reader files ===")
for k, v in byfile.most_common(25):
    print("  %-70s %d" % (k, v))
print()
print("=== Most-read config triggers ===")
for name, ext, nf, internal, files in sorted(rows, key=lambda r: -int(r[1]))[:20]:
    print("  %-58s %4s reads / %2s files" % (name, ext, nf))
