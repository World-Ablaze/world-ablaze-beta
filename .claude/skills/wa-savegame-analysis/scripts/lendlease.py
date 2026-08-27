#!/usr/bin/env python
"""Lend-lease picture of a campaign: who gives, who receives, what, over WHICH channel.

Three channels, three data sources, one table each - never conflate them:

  VANILLA (engine, maritime)   countries/<A>/diplomacy/active_relations/<B>/
                               lend_lease_to_allies_history={ ic_given= fuel_given=
                               ic_received= fuel_received= } - CUMULATIVE IC totals per
                               pair, written on BOTH sides (A's ic_given toward B ==
                               B's ic_received toward A; this script reconciles them and
                               flags any mismatch). The engine never serialises WHICH
                               equipment moved - IC and fuel are all a save carries.
                               `lend_lease={ first= second= start_date= }` in the same
                               block marks a LIVE relation (direction = first is the
                               giver); `recently_leased_ic` sits on the receiver's side.
  SCRIPTED (WA relief)         wa_tlm_llr_* country variables. Donor side:
                               llr_sent_n^idx / llr_sent_amount^idx per archetype
                               (1 infantry .. 9 train overland, 10 convoy maritime).
                               Recipient side (builds v32+): llr_recv_donor / _n /
                               _amount - the pair matrix, donor ids scope-encoded
                               (round(v*1e5) - 2^30 = 3 ASCII bytes little-endian,
                               decoded here; encoding save-proven on campaign 0edbc955
                               and re-verified against wa_ai_lend_lease_targets below).
                               Pre-v32 saves lack the recv arrays: the donor->recipient
                               split of the scripted channel is then NOT recoverable
                               from the save, and the tool says so instead of guessing.
  WA TARGETING (vanilla-style) wa_ai_lend_lease_targets array on the donor - the
                               countries WA's coordinator currently tells the engine AI
                               to lend-lease to. Intent, not delivery.

Cumulative counters diffed across saves give the monthly FLOW - pass several saves of
one campaign (date order is handled here; a game_unique_id change is flagged). Amounts
in the scripted tables are UNITS summed across archetypes on the pair rows
(heterogeneous - a magnitude; the per-archetype split lives in the donor table).

What no save can show: the per-equipment-type split of the VANILLA channel (engine
black box) and convoy losses en route. For the receiving stockpile side, cross-read
stock.py (creator= holdings - a stock, not a flow).

usage: lendlease.py FILE... [--tag TAG] [--min-ic N] [--limit N]
  --tag     only pairs/countries touching TAG
  --min-ic  vanilla rows below this cumulative IC are dropped (default 1.0)
  --limit   max rows per table (default 40, 0 = unlimited)
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import savegame as sg  # noqa: E402

BASE = 1 << 30
ARCH = {1: "infantry", 2: "heavy_infantry", 3: "support", 4: "artillery",
        5: "heavy_artillery", 6: "anti_tank", 7: "anti_air", 8: "motorized",
        9: "train", 10: "convoy"}

TAG_OPEN = re.compile(r"^\t([A-Z][A-Z0-9]{2})=\{")
CP_OPEN = re.compile(r'^"?([A-Z][A-Z0-9]{2})"?=\{')
NUM = re.compile(r"^([a-z_0-9^]+)=(-?[0-9.]+)\s*$")
HIST_F = re.compile(r"^(ic_given|fuel_given|ic_received|fuel_received)=(-?[0-9.]+)")
LL_F = re.compile(r'^(first|second|start_date)="?([^"\s]*)"?')
VAR_WANT = re.compile(r"^(wa_tlm_llr_[a-z_]+(?:\^[0-9numa-z]+)?|"
                      r"wa_ai_lend_lease_targets\^[0-9num]+)=(-?[0-9.]+)\s*$")


def dec_country(v):
    """Scope-encoded country ref -> tag, or None (same rule as aifc.py, save-proven)."""
    try:
        p = int(round(float(v) * 1e5)) - BASE
    except (TypeError, ValueError):
        return None
    if p <= 0 or p > 0xFFFFFF:
        return None
    tag = "".join(chr((p >> s) & 0xFF) for s in (0, 8, 16))
    return tag if re.fullmatch(r"[A-Z0-9]{3}", tag) else None


def arr(varz, name):
    """Indexed slots of array `name` as {int index: float}, ^num excluded."""
    out = {}
    pref = name + "^"
    for k, v in varz.items():
        if k.startswith(pref) and not k.endswith("^num"):
            try:
                out[int(k[len(pref):])] = v
            except ValueError:
                pass
    return out


def scan_save(path):
    """One streaming pass. Returns (meta, pairs, varz_by_tag) where
    pairs[(A, B)] = {ic_given, fuel_given, ic_received, fuel_received,   # A's view of B
                     recently_leased_ic, ll_first, ll_start}             # live relation
    varz_by_tag[tag] = {lowercased variable name: float}."""
    meta = sg.read_meta(path)
    pairs, varz_by_tag = {}, {}
    fh = sg.open_save(path)
    for line in fh:
        if line.startswith("countries={"):
            break
    else:
        return meta, pairs, varz_by_tag
    depth = 1
    tag = None
    var_d = diplo_d = ar_d = cp_d = None
    cp = None
    sub = None          # ("hist"|"ll", depth) inside a counterpart
    varz = {}
    for line in fh:
        s = line.strip()
        opens = line.count("{") - line.count("}")
        if sub is not None:
            kind, sub_d = sub
            if kind == "hist":
                m = HIST_F.match(s)
                if m:
                    pairs.setdefault((tag, cp), {})[m.group(1)] = float(m.group(2))
            else:
                m = LL_F.match(s)
                if m:
                    key = "ll_" + m.group(1)
                    pairs.setdefault((tag, cp), {})[key] = m.group(2)
        elif cp is not None:
            if s.startswith("lend_lease_to_allies_history={"):
                sub = ("hist", depth)
            elif s.startswith("lend_lease={"):
                sub = ("ll", depth)
            elif s.startswith("recently_leased_ic="):
                try:
                    pairs.setdefault((tag, cp), {})["recently_leased_ic"] = \
                        float(s.split("=", 1)[1])
                except ValueError:
                    pass
        elif ar_d is not None:
            m = CP_OPEN.match(s)
            if m:
                cp, cp_d = m.group(1), depth
        elif diplo_d is not None:
            if s.startswith("active_relations={"):
                ar_d = depth
        elif var_d is not None:
            m = VAR_WANT.match(s)
            if m:
                varz[m.group(1)] = float(m.group(2))
        elif tag is not None:
            if s.startswith("variables={") and depth == 2:
                var_d = depth
            elif s.startswith("diplomacy={") and depth == 2:
                diplo_d = depth
        else:
            m = TAG_OPEN.match(line)
            if m and depth == 1:
                tag, varz = m.group(1), {}
        depth += opens
        if sub is not None and depth <= sub[1]:
            sub = None
        if cp is not None and depth <= cp_d:
            cp = None
        if ar_d is not None and depth <= ar_d:
            ar_d = None
        if diplo_d is not None and depth <= diplo_d:
            diplo_d = None
        if var_d is not None and depth <= var_d:
            var_d = None
        if tag is not None and depth <= 1:
            if varz:
                varz_by_tag[tag] = varz
            tag = None
        if depth <= 0:
            break
    return meta, pairs, varz_by_tag


def fnum(v, dec=0):
    if v is None:
        return "-"
    return f"{v:,.{dec}f}".replace(",", " ")


def vanilla_rows(pairs, min_ic):
    """[(giver, recip, ic, fuel, mirror_ic, live, start, recent)] from the GIVER side,
    reconciled against the recipient's ic_received toward the giver."""
    rows = []
    for (a, b), f in sorted(pairs.items()):
        ic = f.get("ic_given", 0.0)
        fuel = f.get("fuel_given", 0.0)
        if ic < min_ic and fuel < min_ic:
            continue
        back = pairs.get((b, a), {})
        mirror = back.get("ic_received")
        live = f.get("ll_first")
        start = f.get("ll_start_date", "")
        # the live-relation block sits on the giver's side with first= the giver;
        # keep it on this row only when it describes THIS direction
        live_here = (live == a)
        recent = back.get("recently_leased_ic")
        rows.append((a, b, ic, fuel, mirror, live_here, start if live_here else "",
                     recent))
    rows.sort(key=lambda r: -r[2])
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--tag")
    ap.add_argument("--min-ic", type=float, default=1.0)
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()
    limit = args.limit if args.limit != 0 else 10 ** 9

    scans = []
    for f in args.files:
        p = sg.resolve(f)
        scans.append((p, *scan_save(p)))
    scans.sort(key=lambda t: sg.date_key(t[1].get("date", "0")))
    camp = {m.get("game_unique_id") for _, m, _, _ in scans}
    if len(camp) > 1:
        print(f"!! {len(camp)} different game_unique_id among these saves - "
              f"cross-save deltas below mix campaigns")

    prev_van = prev_sent = prev_recv = None
    for path, meta, pairs, varz_by_tag in scans:
        date = meta.get("date", "?")
        print(f"\n=== {os.path.basename(path)}  {date} ===")

        # ---------------- vanilla channel ----------------
        rows = vanilla_rows(pairs, args.min_ic)
        if args.tag:
            rows = [r for r in rows if args.tag in (r[0], r[1])]
        van = {(r[0], r[1]): r[2] for r in rows}
        print(f"  VANILLA (engine lend-lease, cumulative IC) - {len(rows)} pairs "
              f">= {args.min_ic:g} IC")
        if rows:
            print(f"    {'giver':<6}{'recip':<7}{'ic_given':>10}{'d/save':>9}"
                  f"{'fuel':>8}{'recent':>7}  live since")
            for a, b, ic, fuel, mirror, live, start, recent in rows[:limit]:
                d = ""
                if prev_van is not None:
                    d = fnum(ic - prev_van.get((a, b), 0.0))
                mm = ""
                if mirror is not None and abs(mirror - ic) > 0.5:
                    mm = f"  !! recipient side reads {fnum(mirror)}"
                print(f"    {a:<6}{b:<7}{fnum(ic):>10}{d:>9}{fnum(fuel):>8}"
                      f"{fnum(recent):>7}  {start if live else '-'}{mm}")
            if len(rows) > limit:
                print(f"    ... {len(rows) - limit} more (raise --limit, 0 = all)")
        prev_van = van

        # ---------------- scripted channel, donor side ----------------
        sent = {}
        for tag, varz in sorted(varz_by_tag.items()):
            if args.tag and tag != args.tag:
                continue
            n, amt = arr(varz, "wa_tlm_llr_sent_n"), arr(varz, "wa_tlm_llr_sent_amount")
            for i, v in amt.items():
                if v > 0 or n.get(i, 0) > 0:
                    sent[(tag, i)] = (n.get(i, 0), v)
        print(f"  SCRIPTED relief, DONOR side (wa_tlm_llr_sent_*, cumulative units; "
              f"rows 1-9 overland, 10 maritime convoy)")
        if sent:
            print(f"    {'donor':<6}{'archetype':<16}{'sends':>6}{'units':>10}"
                  f"{'d/save':>9}")
            for (tag, i), (n, v) in sorted(sent.items(), key=lambda kv: -kv[1][1])[:limit]:
                d = ""
                if prev_sent is not None:
                    d = fnum(v - (prev_sent.get((tag, i), (0, 0.0))[1]))
                print(f"    {tag:<6}{ARCH.get(i, i):<16}{fnum(n):>6}{fnum(v):>10}"
                      f"{d:>9}")
        else:
            print("    none (no verified scripted send yet, or pre-v18 build)")
        prev_sent = sent

        # ---------------- scripted channel, recipient pair matrix ----------------
        recv, have_recv = {}, False
        for tag, varz in sorted(varz_by_tag.items()):
            donors = arr(varz, "wa_tlm_llr_recv_donor")
            if not donors:
                continue
            have_recv = True
            if args.tag and tag != args.tag:
                pass  # keep: the donor side of --tag lives on other tags' arrays
            ns, amts = arr(varz, "wa_tlm_llr_recv_n"), arr(varz, "wa_tlm_llr_recv_amount")
            for i, ref in donors.items():
                donor = dec_country(ref) or f"?{ref:g}"
                if args.tag and args.tag not in (tag, donor):
                    continue
                recv[(tag, donor)] = (ns.get(i, 0), amts.get(i, 0.0))
        print(f"  SCRIPTED relief, RECIPIENT pair matrix (wa_tlm_llr_recv_*, v32+; "
              f"units summed across archetypes)")
        if recv:
            print(f"    {'recip':<6}{'donor':<7}{'sends':>6}{'units':>10}{'d/save':>9}")
            for (tag, donor), (n, v) in sorted(recv.items(), key=lambda kv: -kv[1][1])[:limit]:
                d = ""
                if prev_recv is not None:
                    d = fnum(v - prev_recv.get((tag, donor), (0, 0.0))[1])
                print(f"    {tag:<6}{donor:<7}{fnum(n):>6}{fnum(v):>10}{d:>9}")
        elif have_recv:
            print("    (no pair matches the filter)")
        else:
            print("    absent on this save (pre-v32 build) - the donor->recipient "
                  "split of the scripted channel is not recoverable here")
        prev_recv = recv

        # ---------------- recipient/donor counters + WA targeting ----------------
        printed = 0
        header = False
        for tag, varz in sorted(varz_by_tag.items()):
            if args.tag and tag != args.tag:
                continue
            g = varz.get
            cols = (g("wa_tlm_llr_starving_n", 0), g("wa_tlm_llr_donor_selected_n", 0),
                    g("wa_tlm_llr_path_refused_n", 0),
                    g("wa_tlm_llr_convoy_starving_n", 0),
                    g("wa_tlm_llr_convoy_donor_selected_n", 0),
                    g("wa_tlm_llr_send_failed_n", 0))
            targets = [dec_country(v) or f"?{v:g}"
                       for _, v in sorted(arr(varz, "wa_ai_lend_lease_targets").items())]
            if not any(cols) and not targets:
                continue
            if not header:
                print(f"  COUNTERS (weeks; starving/selected/refused = recipient, "
                      f"send_failed = donor) + WA vanilla-style targets")
                print(f"    {'tag':<6}{'starv':>6}{'selct':>6}{'refus':>6}"
                      f"{'cv_st':>6}{'cv_se':>6}{'fail':>6}  targets")
                header = True
            if printed < limit:
                print(f"    {tag:<6}" + "".join(f"{fnum(c):>6}" for c in cols)
                      + "  " + (" ".join(targets) if targets else "-"))
            printed += 1
        if printed > limit:
            print(f"    ... {printed - limit} more (raise --limit, 0 = all)")


if __name__ == "__main__":
    main()
