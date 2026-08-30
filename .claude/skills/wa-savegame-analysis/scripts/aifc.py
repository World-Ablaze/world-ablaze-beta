#!/usr/bin/env python
"""AIFC (AI Force Concentration) state out of a save: sector, armour book, ledger.

WHAT IT READS (all save-visible, verified on 1945.6_Jun / campaign saves 2026-08-27):
  variables   wa_ai_aifc_sector_{states,objectives}[_ref], _anchor, _age, _enemy,
              wa_ai_aifc_armor_boost, wa_ai_aifc_armor_suppressed,
              wa_tlm_r67_aifc_arm_* (churn telemetry, builds from 2026-08-11 on)
  ai section  persistent_strategy={ type=83 id=N value=+-400|+-150 } - the ENGINE's
              applied front_armor_score ledger. `id` is the 1-based position of the
              target in the save's countries={} order; this script collects that
              order in the same pass, so no second read.

ENCODINGS (decode rules, save-proven 2026-08-17 campaign 0edbc955):
  state scope ref    negative float: id = round(v*1e5) + 2^30   (-10737.41578 -> 246)
  country scope ref  positive float: round(v*1e5) - 2^30 = tag as 3 ASCII bytes
                     little-endian (10793.98227 -> SOV). sector_enemy, armor_boost
                     and armor_suppressed[] all use this; sector_states/objectives
                     hold PLAIN map ids and their _ref twins hold the encoded form.

THE CLOSURE TEST (the payload, not a footnote): the ledger's NET per tag must equal
the book exactly - boost tag +400, each suppressed tag -150, PLUS +400 per entry in
wa_ai_aifc_armor_pending_boost and -150 per entry in wa_ai_aifc_armor_pending_supp
(the [aifc-revived-tag-residue] debt books: cancels owed to tags that were dead at
retirement, emitted by the weekly sweep once the tag exists again; builds from
2026-08-31 on). A nonzero NET on a tag outside book+pending is a RESIDUAL: expected
on dead tags of PRE-pending builds (the old reconcile dropped the debt - the
historical KNOWN GAP), an alarm on a live one. A book tag whose NET is not its
expected value is a MISMATCH and always an alarm. A pending id on a LIVE tag is an
alarm too (the sweep drains within a week of revival) unless the save caught that
one week.

  ai section  force_concentration_target={ target=<prov> from=<prov> progress=<f> }
              - one block per ACTIVE engine AIFC push, present ONLY on a country
              with a live plan right now (2026-11, ENG_1943_11_06: USA had 2,
              ENG 0, matching the owner's imgui screenshot). `progress` is the
              imgui "Freshness" byte-equal. Printed as "active push".

WHAT A SAVE CANNOT TELL YOU: whether Layer 4 (force_concentration_* state_triggers)
consumed the arrays - file-defined ai_strategy blocks never serialise - and whether
the engine actually massed divisions BECAUSE of the sector. Of the live imgui
window (`imgui show ai_force_concentration`) fields, only the push's EXISTENCE,
its target/from provinces and its freshness serialise; the per-front AIFC score,
the should-receive / assigned-units counts and the strategic-target list are
engine-runtime-only (searched the save 2026-11, not found). Correlate with
plans.py --where (is the corridor's front manned) and control (was it taken);
the full window is owner-run live only (skill wa-diagnosis, technique 5).

usage: aifc.py TAG[,TAG,...]|ALL FILE... [--ledger] [--limit N]
  ALL       every country with any AIFC state (silent tags are skipped)
  --ledger  full NET-by-tag table (default: closure verdict + offenders only)
  --limit   max rows in NET/residual listings (default 16, 0 = unlimited)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402

BASE = 1 << 30
TAG_RE = re.compile(r"^\t([A-Z0-9]{3})=\{")
SEC_RE = re.compile(r"^\t\t([a-z_]+)=\{")
VAR_PREFIXES = ("wa_ai_aifc_", "wa_tlm_r67_aifc_")
STRAT_RE = re.compile(r"type=(\d+)\s+id=(\d+)\s+value=(-?\d+(?:\.\d+)?)")
FCT_RE = re.compile(r"target=(\d+)\s+from=(\d+)\s+progress=(-?\d+(?:\.\d+)?)")
BOOST, SUPPRESS = 400, -150

STATE_LOC = os.path.join(sg.REPO, "localisation", "english",
                         "state_names_l_english.yml")
_state_name = None


def state_names():
    global _state_name
    if _state_name is None:
        _state_name = {}
        try:
            import io
            for line in io.open(STATE_LOC, encoding="utf-8-sig", errors="replace"):
                m = re.match(r'\s*STATE_(\d+):\d*\s*"(.*)"', line)
                if m:
                    _state_name[int(m.group(1))] = m.group(2)
        except OSError:
            pass
    return _state_name


def dec_country(v):
    """Encoded country scope ref -> tag, or None if it does not decode cleanly."""
    p = int(round(v * 1e5)) - BASE
    if p <= 0 or p > 0xFFFFFF:
        return None
    tag = "".join(chr((p >> s) & 0xFF) for s in (0, 8, 16))
    return tag if re.fullmatch(r"[A-Z0-9]{3}", tag) else None


def dec_state(v):
    """Encoded state scope ref (negative float) -> plain state id."""
    return int(round(v * 1e5)) + BASE


def scan_save(fh, want):
    """ONE pass over countries={}: (tag order list, {tag: (vars, ledger)}).

    vars   {name: float} for wa_ai_aifc_* / wa_tlm_r67_aifc_* variables
    ledger [(id, value), ...] from type=83 persistent_strategy/ai_strategy entries

    Not built on iter_country_lines: that helper consumes the stream up to its tag,
    so multi-tag use silently loses earlier tags (same trap stock.py documents).
    The FULL block is always walked even after every wanted tag is captured,
    because the ledger's id -> tag decode needs the complete countries={} order.
    """
    order, data = [], {}
    for line in fh:
        if line.startswith("countries={"):
            break
    else:
        return order, data
    depth, cur, section, capture = 1, None, None, False
    varz, ledger, acc, fc = None, None, None, None
    for line in fh:
        delta = line.count("{") - line.count("}")
        if cur is None:
            m = TAG_RE.match(line) if depth == 1 else None
            if m and delta > 0:
                cur = m.group(1)
                order.append(cur)
                capture = want is None or cur in want
                varz, ledger, section = {}, [], None
                fc, fct = None, []
                alive = False
            depth += delta
            if depth <= 0:
                break
            continue
        # inside a country block (country body depth counted from 2)
        if capture:
            if section is None and depth == 2:
                m = SEC_RE.match(line)
                if m and delta > 0:
                    section = (m.group(1), depth + delta)
                    # liveness: an annihilated tag keeps its whole country block
                    # with frozen variables but loses `units` (savegame skill,
                    # dead-tag gotcha) - SHA read as R1 churn for 13 saves.
                    if m.group(1) == "units":
                        alive = True
            elif section is not None:
                name, base = section
                if name == "variables":
                    t = line.strip()
                    if t.startswith(VAR_PREFIXES):
                        k, _, v = t.partition("=")
                        try:
                            varz[k] = float(v)
                        except ValueError:
                            pass
                elif name == "ai":
                    if acc is not None:
                        acc.append(line)
                        if sum(x.count("{") - x.count("}") for x in acc) <= 0 \
                                or len(acc) > 10:
                            m = STRAT_RE.search(" ".join(x.strip() for x in acc))
                            if m and m.group(1) == "83":
                                ledger.append((int(m.group(2)), float(m.group(3))))
                            acc = None
                    elif fc is not None:
                        # force_concentration_target block: one per ACTIVE engine
                        # push; only a country with a live plan has any. `progress`
                        # is the imgui window's "Freshness" (byte-equal, 2026-11).
                        fc.append(line.strip())
                        if sum(x.count("{") - x.count("}") for x in fc) <= 0:
                            m = FCT_RE.search(" ".join(fc))
                            fct.append((int(m.group(1)), int(m.group(2)),
                                        float(m.group(3))) if m else None)
                            fc = None
                    else:
                        t = line.strip()
                        if t.startswith("force_concentration_target={"):
                            if delta <= 0:  # single-line block: close it at once
                                m = FCT_RE.search(t)
                                fct.append((int(m.group(1)), int(m.group(2)),
                                            float(m.group(3))) if m else None)
                            else:
                                fc = [t]
                        elif t.startswith(("persistent_strategy={", "ai_strategy={")):
                            if delta <= 0:
                                m = STRAT_RE.search(t)
                                if m and m.group(1) == "83":
                                    ledger.append((int(m.group(2)),
                                                   float(m.group(3))))
                            else:
                                acc = [line]
                if depth + delta <= base - 1 and delta < 0:
                    section, acc = None, None
        depth += delta
        if depth <= 1:
            if capture and (varz or ledger or fct):
                data[cur] = (varz, ledger, alive, fct)
            cur, section, acc, capture = None, None, None, False
            if depth <= 0:
                break
    return order, data


def arr(varz, name):
    """wa-array (name^0..name^N, name^num) -> ordered value list."""
    out = []
    i = 0
    while f"{name}^{i}" in varz:
        out.append(varz[f"{name}^{i}"])
        i += 1
    return out


def sname(sid):
    n = state_names().get(sid)
    return f"{sid} {n}" if n else str(sid)


def fmt_states(ids, names=True):
    return ", ".join(sname(int(i)) if names else str(int(i)) for i in ids)


def report(tag, varz, ledger, order, date, show_ledger, limit, trend, alive=True,
           fct=None):
    print(f"\n=== {date}  {tag} ==={'' if alive else '  [DEAD TAG]'}")
    if not alive:
        print("  !! no `units` section - annihilated tag, every value below FROZE at")
        print("     its last live save; age/sector here is not a live selection.")
    states = arr(varz, "wa_ai_aifc_sector_states")
    anchor = varz.get("wa_ai_aifc_sector_anchor")
    age = varz.get("wa_ai_aifc_sector_age")
    enemy_v = varz.get("wa_ai_aifc_sector_enemy")
    enemy = dec_country(enemy_v) if enemy_v is not None else None

    # -- sector --
    if states:
        objectives = arr(varz, "wa_ai_aifc_sector_objectives")
        print(f"  sector: anchor={sname(int(anchor)) if anchor else '?'}"
              f"  enemy={enemy or '?'}"
              f"  age={int(age) if age is not None else '?'}wk")
        print(f"  corridor ({len(states)}): {fmt_states(states)}")
        print(f"  objectives ({len(objectives)}): {fmt_states(objectives)}")
        # ref-twin consistency: decoded _ref set must equal the plain set
        for nm in ("sector_states", "sector_objectives"):
            plain = {int(v) for v in arr(varz, f"wa_ai_aifc_{nm}")}
            refs = {dec_state(v) for v in arr(varz, f"wa_ai_aifc_{nm}_ref")}
            if refs and refs != plain:
                print(f"  !! REF MISMATCH {nm}: plain={sorted(plain)} "
                      f"decoded_ref={sorted(refs)} - Layer 4 sees the _ref set")
    else:
        print("  no sector (corridor empty - not eligible, no land contact, or "
              "selection lapsed this week)")

    # -- armour book --
    boost_v = varz.get("wa_ai_aifc_armor_boost")
    boost = dec_country(boost_v) if boost_v is not None else None
    supp = [dec_country(v) or f"<{v}>"
            for v in arr(varz, "wa_ai_aifc_armor_suppressed")]
    pend_b = [dec_country(v) or f"<{v}>"
              for v in arr(varz, "wa_ai_aifc_armor_pending_boost")]
    pend_s = [dec_country(v) or f"<{v}>"
              for v in arr(varz, "wa_ai_aifc_armor_pending_supp")]
    if boost or supp:
        print(f"  armor book: boost={boost or '-'}  "
              f"suppressed({len(supp)})={','.join(supp) if supp else '-'}")
    else:
        print("  armor book: empty (steering off, no sector, or mid-lapse)")
    if pend_b or pend_s:
        # [aifc-revived-tag-residue] cancels owed to tags dead at retirement; the
        # weekly sweep emits them when the tag exists again. Normal on dead tags.
        print(f"  pending cancels: boost(-400 owed)={','.join(pend_b) or '-'}  "
              f"supp(+150 owed)={','.join(pend_s) or '-'}")

    # -- active engine push (force_concentration_target blocks) --
    # Present ONLY on a country whose AIFC has a live plan right now. The save
    # carries the push's target province, its launch province, and `progress`
    # (= the imgui window's "Freshness"). It does NOT carry the per-front AIFC
    # score, the should-receive / assigned counts, or the strategic-target list.
    if fct:
        p2s = sg.province_state_map()
        print(f"  active push ({len(fct)} plan"
              f"{'s' if len(fct) > 1 else ''}):")
        for rec in fct:
            if rec is None:
                print("     <unparsed force_concentration_target block>")
                continue
            tgt, frm, prog = rec
            ts, fs = p2s.get(tgt), p2s.get(frm)
            print(f"     -> target {sname(ts) if ts else f'prov {tgt}'}"
                  f"  from {sname(fs) if fs else f'prov {frm}'}"
                  f"  freshness={prog:g}")
    # absent = no active plan this save; says nothing about the sector above.

    # -- ledger + closure --
    if ledger:
        net, pairs = {}, set()
        for i, v in ledger:
            t = order[i - 1] if 0 < i <= len(order) else f"<id {i}>"
            net[t] = net.get(t, 0.0) + v
            pairs.add((i, v))
        expected = {}
        if boost:
            expected[boost] = float(BOOST)
        for t in supp:
            expected[t] = expected.get(t, 0.0) + SUPPRESS
        # [aifc-revived-tag-residue] pending debts: the engine still carries the
        # stale entry, so it belongs in the expectation until the sweep emits.
        for t in pend_b:
            expected[t] = expected.get(t, 0.0) + BOOST
        for t in pend_s:
            expected[t] = expected.get(t, 0.0) + SUPPRESS
        # a tag in BOTH a pending and an active book is impossible if the sweep
        # works: section 0b drains pending before sections 1/3 install. Alarm.
        both = (set(pend_b) | set(pend_s)) & (set(supp) | ({boost} if boost else set()))
        if both:
            print("  !! PENDING+ACTIVE on the same tag - the revival sweep did not "
                  "fire before an install: " + " ".join(sorted(both)))
        mism = [(t, net.get(t, 0.0), want) for t, want in expected.items()
                if abs(net.get(t, 0.0) - want) > 0.5]
        resid = sorted((t, v) for t, v in net.items()
                       if t not in expected and abs(v) > 0.5)
        print(f"  ledger type=83: {len(ledger)} entries, "
              f"{len(pairs)} distinct (id,value) pairs"
              + ("  <- accumulation is churn: read wa_tlm_r67 below"
                 if len(ledger) > 3 * max(len(pairs), 1) else ""))
        if mism:
            print(f"  !! CLOSURE MISMATCH ({len(mism)}) - book+pending and ledger "
                  "disagree, an alarm on any campaign started on a pending-books "
                  "build; on a campaign begun BEFORE 2026-08-31 a dead-then-revived "
                  "tag's mismatch is LEGACY residue (debt predates the books, "
                  "unrecoverable - script cannot read the engine ledger):")
            for t, got, want in mism[:limit or None]:
                print(f"     {t}: ledger NET {got:+.0f}, book expects {want:+.0f}")
        else:
            print(f"  closure book<->ledger: OK "
                  f"({len(expected)} tracked entries all at expected NET)")
        if resid:
            shown = resid if limit == 0 else resid[:limit]
            print(f"  residuals ({len(resid)}, NET!=0 outside book+pending - "
                  "expected on dead tags of pre-pending builds (legacy KNOWN GAP); "
                  "on a pending-books campaign a dead tag should sit in pending "
                  "instead, and a LIVE residual is an alarm): "
                  + "  ".join(f"{t} {v:+.0f}" for t, v in shown)
                  + ("  ..." if len(resid) > len(shown) else ""))
        if show_ledger:
            rows = sorted(net.items(), key=lambda kv: -abs(kv[1]))
            shown = rows if limit == 0 else rows[:limit]
            print("  NET by tag: "
                  + "  ".join(f"{t} {v:+.0f}" for t, v in shown if abs(v) > 0.5)
                  + ("  ..." if len(rows) > len(shown) else ""))
    elif boost or supp:
        print("  !! book non-empty but ZERO type=83 ledger entries - the emitters "
              "never ran or the meta_effect failed silently")
    else:
        print("  ledger type=83: empty")

    # -- R67 telemetry --
    r67 = {k[len("wa_tlm_r67_aifc_arm_"):]: v for k, v in varz.items()
           if k.startswith("wa_tlm_r67_aifc_arm_")}
    if r67:
        lapse, ret = r67.get("lapse_wk", 0), r67.get("retire_n", 0)
        last = r67.get("last_t", 0)
        print(f"  r67: entries_n={r67.get('entries_n', 0):.0f} "
              f"lapse_wk={lapse:.0f} retire_n={ret:.0f} "
              f"install_n={r67.get('install_n', 0):.0f}  "
              f"last emit={sg._tlm_date(last) if last else 'never'}")
        # lapse_wk is never reset at first install: it carries every pre-install
        # week, so lapse_wk/retire_n is NOT a mean episode length (GER read 195wk
        # for a 1wk episode). No per-episode mean is derivable from a save.
        if lapse and ret:
            print("  r67 note: lapse_wk includes pre-install weeks - do NOT size "
                  "a grace window on lapse_wk/retire_n")
    else:
        print("  r67: absent (pre-R67 build - telemetry void, not zero)")

    trend.append((date, tag,
                  int(anchor) if anchor else None, enemy,
                  int(age) if age is not None else None,
                  len(states), len(ledger), len(supp)))


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tags, files, show_ledger, limit = None, [], False, 16
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--ledger":
            show_ledger = True
        elif a == "--limit":
            i += 1
            limit = int(argv[i])
        elif a.startswith("--"):
            sys.exit(f"unknown option {a}")
        elif tags is None:
            tags = [t.strip().upper() for t in a.split(",") if t.strip()]
        else:
            files.append(a)
        i += 1
    if not tags or not files:
        sys.exit(__doc__)
    want = None if tags == ["ALL"] else set(tags)

    print("# AIFC state per country. The CLOSURE test is the payload: ledger NET per")
    print("#   tag must equal the book (boost +400, suppressed -150, others 0).")
    print("# RESIDUALS on dead/annexed tags are the documented KNOWN GAP, not a bug.")
    print("# A save CANNOT show Layer 4 consumption (file ai_strategy never")
    print("#   serialises) nor causality - correlate with plans.py --where / control.")

    trend = []
    for meta, f in sg.sorted_by_date([sg.resolve(f) for f in files]):
        date = meta.get("date", "?")
        with sg.open_save(f) as fh:
            order, data = scan_save(fh, want)
        found = [t for t in (sorted(data) if want is None else tags) if t in data]
        quiet = []
        for t in found:
            varz, ledger, alive, fct = data[t]
            # ALL mode: a tag whose only AIFC trace is the r67 lapse counters has
            # never held a sector or an armour entry - one census line, not a block.
            if want is None and not ledger \
                    and not any(k.startswith(("wa_ai_aifc_sector_states^",
                                              "wa_ai_aifc_armor_")) for k in varz):
                quiet.append(t)
                continue
            report(t, varz, ledger, order, date, show_ledger, limit, trend,
                   alive=alive, fct=fct)
        if quiet:
            print(f"\n  ({len(quiet)} more tags carry only r67 lapse counters - "
                  f"never held a sector: {' '.join(quiet[:20])}"
                  f"{' ...' if len(quiet) > 20 else ''})")
        if want is not None:
            for t in tags:
                if t not in data:
                    print(f"\n=== {date}  {t} ===\n  no AIFC state at all "
                          "(never eligible, or pre-AIFC build)")

    if len(files) > 1 and trend:
        print("\n# trend (date-ordered). age pinned at 1 in EVERY save = weekly")
        print("#   re-selection pathology (the historical R1 bug shape) - but only")
        print("#   on a LIVE tag; a [DEAD TAG] block above froze, not churns.")
        print(f"{'date':<12}{'tag':<5}{'anchor':>7}{'enemy':>6}{'age':>5}"
              f"{'corr':>5}{'ledger':>7}{'supp':>5}")
        for d, t, a, e, ag, c, led, sp in trend:
            print(f"{d:<12}{t:<5}{a if a is not None else '-':>7}"
                  f"{e or '-':>6}{ag if ag is not None else '-':>5}"
                  f"{c:>5}{led:>7}{sp:>5}")


if __name__ == "__main__":
    main(sys.argv[1:])
