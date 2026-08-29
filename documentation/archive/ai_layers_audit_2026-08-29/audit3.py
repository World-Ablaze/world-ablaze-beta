import os as _os, sys as _sys
# Repo root derived from this file's location: documentation/archive/<dir>/<script>.py
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import re, os, collections

os.chdir(_REPO)
cfg = 'common/scripted_triggers/WA_AI_CONFIG.txt'
raw = open(cfg, encoding='utf-8-sig').read()
lines = raw.split('\n')

# parse top-level blocks
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
        blocks[name] = (i + 1, body)
        i = j
    else:
        i += 1

def strip(body):
    out = []
    for l in body:
        l = re.sub(r'#.*', '', l).strip()
        if l:
            out.append(l)
    return out

const_yes, const_no, alias, tagonly, mixed, statebased = [], [], [], [], [], []
STATE = re.compile(r'\b(date|has_war|has_tech|num_of_|has_army_manpower|has_navy_size|check_variable|has_country_flag|has_completed_focus|is_in_faction_with|has_government|has_dynamic_modifier|has_idea|surrender_progress|any_enemy_country|any_country_of|has_autonomy_state|difficulty|is_historical_focus_on|is_subject|exists|has_naval_treaty|modifier@)\b')
TAG = re.compile(r'\b(original_)?tag\s*=\s*[A-Z]')

for name, (ln, body) in blocks.items():
    b = strip(body)
    j = ' '.join(b)
    if b == ['always = yes']:
        const_yes.append((name, ln))
    elif b == ['always = no']:
        const_no.append((name, ln))
    elif len(b) <= 3 and re.fullmatch(r'(OR = \{ )?[A-Za-z_]+ = yes( \})?', j.replace('{ ', '{ ').strip()):
        alias.append((name, ln, j))
    else:
        has_tag = bool(TAG.search(j))
        has_state = bool(STATE.search(j))
        if has_tag and has_state:
            mixed.append((name, ln))
        elif has_tag:
            tagonly.append((name, ln))
        elif has_state:
            statebased.append((name, ln))

def dump(t, lst):
    print("\n=== %s (%d) ===" % (t, len(lst)))
    for x in sorted(lst, key=lambda z: z[0]):
        print("  L%-5d %s" % (x[1], x[0]) + (("   -> " + x[2]) if len(x) > 2 else ""))

dump("CONSTANT always = yes", const_yes)
dump("CONSTANT always = no", const_no)
dump("PURE ALIAS (single delegate)", alias)
dump("PURE TAG CLASSIFICATION (correct for CONFIG)", tagonly)
dump("MIXED tag + game state (config/engine leak)", mixed)
dump("PURE GAME STATE, no tag (does not belong in CONFIG)", statebased)
