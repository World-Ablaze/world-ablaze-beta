#!/usr/bin/env python
"""Carrier-aircraft deck-vs-land split for EVERY country, one pass per save.

Structure: top-level strategic_air={ } contains, at depth 1:
  air_base={ id={ id=N type=T } state=S ... }   <- land bases carry state=
  air_base={ id={ id=N ... } ... }              <- carrier decks have NO state=
  <TAG>={ air_wing_pool={ definition=X air_base={ id=N } air_wings={ ... } } }

Depths (strategic_air body = depth 1): TAG body at 2, air_wing_pool body at 3,
air_wings body at 4. `count=` ALSO occurs one level deeper inside combat-history
enemy={} records -> anchor strictly on depth (the trap air.py already hit).

usage: cvair.py [--tags A,B] [--miss] [--all] FILE...
"""
import io, os, re, sys, zipfile, collections

SAVEDIR = os.path.expanduser(r"~\Documents\Paradox Interactive\Hearts of Iron IV\save games")
TAGRE = re.compile(r'^([A-Z][A-Z0-9]{2})=\{$')


def openfile(name):
    p = name if (os.path.sep in name or '/' in name) else os.path.join(SAVEDIR, name)
    with open(p, 'rb') as fh:
        magic = fh.read(7)
    if magic.startswith(b'PK'):
        z = zipfile.ZipFile(p)
        return io.TextIOWrapper(z.open('gamestate'), encoding='utf-8', errors='replace')
    return io.open(p, encoding='utf-8', errors='replace')


def parse(name):
    """-> (date, landbases, allbases, wings[{tag,def,base,count,mission,region}])"""
    f = openfile(name)
    depth = 0
    date = None
    found = False
    landbases, allbases = set(), set()
    mode = None            # 'base' | 'tag' at depth>=2
    tag = None
    curbase = None
    wings = []
    pooldef = poolbase = None
    w = None
    for line in f:
        s = line.strip()
        if date is None and s.startswith('date="'):
            date = s.split('"')[1]
        d = s.count('{') - s.count('}')
        if not found:
            if depth == 0 and s.startswith('strategic_air={'):
                found = True
                depth = 1
                continue
            depth += d
            continue

        if depth == 1:
            # dispatch on the depth-1 entry we are about to enter
            if d > 0:
                m = TAGRE.match(s)
                if s.startswith('air_base={'):
                    mode, curbase = 'base', None
                elif m:
                    mode, tag = 'tag', m.group(1)
                    pooldef = poolbase = w = None
                else:
                    mode = None
        elif mode == 'base':
            if depth == 2:
                if s.startswith('id={ id='):
                    curbase = s.split('id=')[2].split()[0]
                    allbases.add(curbase)
                elif s.startswith('state=') and curbase is not None:
                    landbases.add(curbase)
        elif mode == 'tag':
            if depth == 2 and s.startswith('air_wing_pool={'):
                pooldef = poolbase = None
                w = None
            elif depth == 3 and s.startswith('definition='):
                pooldef = s.split('=')[1]
            elif depth == 3 and s.startswith('air_base={ id='):
                poolbase = s.split('id=')[1].split()[0]
            elif depth == 3 and s.startswith('air_wings={'):
                w = {'tag': tag, 'def': pooldef, 'base': poolbase, 'count': 0,
                     'mission': None, 'region': None}
                wings.append(w)
            elif w is not None and depth == 4:
                if s.startswith('count='):
                    w['count'] = int(s.split('=')[1])
            elif w is not None and depth == 5:
                if s.startswith('executing_mission='):
                    w['mission'] = s.split('=')[1]
                elif s.startswith('strategic_region='):
                    w['region'] = s.split('=')[1]
        depth += d
        if depth <= 0:
            break
    f.close()
    return date, landbases, allbases, wings


def main():
    args = sys.argv[1:]
    only, miss, showall = None, False, False
    while args and args[0].startswith('--'):
        a = args.pop(0)
        if a == '--tags':
            only = set(args.pop(0).split(','))
        elif a == '--miss':
            miss = True
        elif a == '--all':
            showall = True
    for name in args:
        date, landbases, allbases, wings = parse(name)
        per = collections.defaultdict(collections.Counter)
        landmiss = collections.defaultdict(collections.Counter)
        deckrole = collections.defaultdict(collections.Counter)
        landrole = collections.defaultdict(collections.Counter)
        for wg in wings:
            if only and wg['tag'] not in only:
                continue
            iscv = (wg['def'] or '').startswith('cv_')
            onland = wg['base'] in landbases
            c = per[wg['tag']]
            c['air_total'] += wg['count']
            if iscv:
                c['cv_land' if onland else 'cv_deck'] += wg['count']
                (landrole if onland else deckrole)[wg['tag']][wg['def']] += wg['count']
                if onland:
                    landmiss[wg['tag']][wg['mission'] or 'NO-MISSION'] += wg['count']
            else:
                c['other_land' if onland else 'other_deck'] += wg['count']
        print('=== %s (%s) land_bases=%d decks=%d' %
              (date, os.path.basename(name), len(landbases), len(allbases) - len(landbases)))
        print('  %-4s %8s %8s %8s %7s %9s %6s' %
              ('TAG', 'cv_deck', 'cv_land', 'cv_tot', 'land:dk', 'air_tot', 'cv%air'))
        rows = sorted(per.items(), key=lambda kv: -(kv[1]['cv_land'] + kv[1]['cv_deck']))
        for t, c in rows:
            tot = c['cv_land'] + c['cv_deck']
            if tot == 0 and not showall:
                continue
            r = ('%.2f' % (c['cv_land'] / c['cv_deck'])) if c['cv_deck'] else 'inf'
            pct = (100.0 * tot / c['air_total']) if c['air_total'] else 0
            print('  %-4s %8d %8d %8d %7s %9d %5.0f%%' %
                  (t, c['cv_deck'], c['cv_land'], tot, r, c['air_total'], pct))
            if c['other_deck']:
                print('       non-cv ON DECK: %d' % c['other_deck'])
            if miss:
                if deckrole[t]:
                    print('       deck roles: ' + ' '.join('%s=%d' % kv for kv in deckrole[t].most_common()))
                if landrole[t]:
                    print('       land roles: ' + ' '.join('%s=%d' % kv for kv in landrole[t].most_common()))
                if landmiss[t]:
                    print('       land cv missions: ' +
                          ' '.join('%s=%d' % kv for kv in landmiss[t].most_common(8)))


main()
