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
        blocks[name] = (i + 1, ' '.join(x for x in (re.sub(r'#.*', '', b).strip() for b in body) if x))
        i = j
    else:
        i += 1

# CONFIG-legitimate vocabulary under the owner's rule: tags, numbers, dates, and *identifiers*
TAG = re.compile(r'\b(original_)?tag\s*=\s*[A-Z]{3}\b')
DATE = re.compile(r'\bdate\s*[<>]\s*\d{4}\.')
NUMTHR = re.compile(r'\b(difficulty|num_of_\w+|has_army_manpower|has_navy_size|num_divisions)\b')
IDENT = re.compile(r'\b(has_tech|has_completed_focus|has_autonomy_state|has_idea|has_dynamic_modifier|has_country_flag|has_government)\s*=')
# live-state verdicts: these ask the world, not the data sheet
LIVE = re.compile(r'\b(any_enemy_country|any_country_of|any_country|surrender_progress|has_war_with|has_war\b|is_in_faction_with|check_variable|exists|has_naval_treaty_trigger|is_subject|is_historical_focus_on|has_capitulated|country_exists)\b')
SELF = re.compile(r'\bWA_AI_\w+\s*=\s*yes\b')

rows = []
for name, (ln, body) in blocks.items():
    if body in ('always = yes', 'always = no'):
        rows.append(('FLAG', name, ln))
        continue
    has = {
        'tag': bool(TAG.search(body)),
        'date': bool(DATE.search(body)),
        'num': bool(NUMTHR.search(body)),
        'ident': bool(IDENT.search(body)),
        'live': bool(LIVE.search(body)),
        'ref': bool(SELF.search(body)),
    }
    decl = has['tag'] or has['date'] or has['num'] or has['ident']
    if has['live'] and not decl:
        rows.append(('LIVE-ONLY', name, ln))
    elif has['live'] and decl:
        rows.append(('DECL+LIVE', name, ln))
    elif decl:
        rows.append(('DECL', name, ln))
    elif has['ref']:
        rows.append(('COMPOSE', name, ln))
    else:
        rows.append(('OTHER', name, ln))

g = collections.defaultdict(list)
for k, n, ln in rows:
    g[k].append((n, ln))

LABEL = {
    'DECL': 'DECLARATION pure (tags / dates / nombres / identifiants) -> RESTE en CONFIG',
    'FLAG': 'DRAPEAU always = yes|no -> reste, mais zone dediee',
    'COMPOSE': 'COMPOSITION d autres triggers CONFIG -> reste en CONFIG',
    'DECL+LIVE': 'MIXTE declaration + interrogation du monde -> A SCINDER',
    'LIVE-ONLY': 'VERDICT sur l etat vivant du monde, aucune donnee -> SORT de CONFIG',
    'OTHER': 'autre',
}
for k in ('DECL', 'FLAG', 'COMPOSE', 'DECL+LIVE', 'LIVE-ONLY', 'OTHER'):
    print("\n=== %s (%d) ===" % (LABEL[k], len(g[k])))
    if k in ('DECL', 'FLAG'):
        continue
    for n, ln in sorted(g[k]):
        print("  L%-6d %s" % (ln, n))
