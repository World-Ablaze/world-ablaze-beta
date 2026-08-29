import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)

DATE = re.compile(r'\bdate\s*[<>=]+\s*(\d{4}\.\d{1,2}\.\d{1,2})')
# numeric threshold on a state/capability trigger
NUM = re.compile(r'\b(num_of_\w+|has_army_manpower|has_navy_size|num_divisions|has_war_support|has_stability|surrender_progress|arms_factory_level|threat|has_manpower|amount_research_slots|has_political_power|command_power|has_equipment)\b[^\n]{0,40}?([<>]=?)\s*(-?[\d.]+)')

def bucket(p):
    b = os.path.basename(p)
    if b.startswith('WA_AI_CONFIG'):
        return 'CONFIG'
    if '/script_constants/' in p:
        return 'script_constants'
    if '/ai_strategy/' in p:
        return 'ai_strategy'
    if '/scripted_triggers/' in p:
        return 'scripted_triggers'
    if '/scripted_effects/' in p:
        return 'scripted_effects'
    if p.startswith('events'):
        return 'events'
    return 'other'

dates = collections.Counter()
nums = collections.Counter()
dperfile = collections.Counter()
nperfile = collections.Counter()
distinct_dates = collections.Counter()

for folder in ('common/scripted_triggers', 'common/scripted_effects', 'common/ai_strategy', 'events', 'common/on_actions'):
    for dp, dn, fn in os.walk(folder):
        for f in sorted(fn):
            if not f.endswith('.txt') or not f.startswith('WA_'):
                continue
            p = (dp + '/' + f).replace('\\', '/')
            s = open(dp + '/' + f, encoding='utf-8-sig', errors='ignore').read()
            s = re.sub(r'#.*', '', s)
            b = bucket(p)
            d = DATE.findall(s)
            n = NUM.findall(s)
            dates[b] += len(d)
            nums[b] += len(n)
            if d:
                dperfile[p] = len(d)
            if n:
                nperfile[p] = len(n)
            for x in d:
                distinct_dates[x] += 1

print("=== literal `date > YYYY.M.D` in WA_* AI files, by zone ===")
for k, v in dates.most_common():
    print("  %-22s %d" % (k, v))
print("  TOTAL", sum(dates.values()))
print()
print("=== numeric thresholds (num_of_*, manpower, navy size, war support...) by zone ===")
for k, v in nums.most_common():
    print("  %-22s %d" % (k, v))
print("  TOTAL", sum(nums.values()))
print()
print("=== top files by literal dates ===")
for k, v in dperfile.most_common(15):
    print("  %-70s %d" % (k, v))
print()
print("=== top files by numeric thresholds ===")
for k, v in nperfile.most_common(15):
    print("  %-70s %d" % (k, v))
print()
print("=== most repeated literal dates (same date hardcoded N times) ===")
for k, v in distinct_dates.most_common(15):
    print("  %-14s %d" % (k, v))
