"""Cumulative convoy losses per country, derived at build time from the per-save ledgers.

Each save carries a rolling 24-month `sunk_convoys_history` window. Stitching every save of the
campaign (the latest save covering a month wins) gives one record set per month; the running sum of
a country's losses up to each save's last complete month is the cumulative series the report shows
beside the per-month one. A month inside the range that no save covers makes the cumulative unknown
from that month on, so a gap in the saves never reads as "no losses". This runs after extraction
(it needs the whole campaign), so it does not touch the per-save cache.
"""
from __future__ import annotations

CUMULATIVE_METRIC = {
    "convoys_lost_cumulative": {
        "label": "Convoys lost (cumulative)", "unit": "count", "evidence": "DERIVED",
        "source": "sunk_convoys_history stitched over the campaign, summed up to each save's last complete month",
        "note": "Unknown from the first month no save covers; a covered month with no record is 0.",
    },
}


def month_index(date: str) -> int:
    parts = [int(x) for x in date.split(".")]
    return parts[0] * 12 + parts[1] - 1


def stitched_ledger(snapshots: list[dict]) -> dict[int, list]:
    """month index -> [month, killer, owner, convoys] records, latest covering save wins."""
    by_month: dict[int, list] = {}
    for snap in snapshots:
        window, rows = snap.get("convoy_window"), snap.get("convoy_losses")
        if not window or rows is None:
            continue
        for m in range(window[0], window[1] + 1):
            by_month[m] = []
        for row in rows:
            if row[0] in by_month:
                by_month[row[0]].append(row)
    return by_month


def enrich_cumulative_losses(snapshots: list[dict]) -> list[dict]:
    """Write `metrics.convoys_lost_cumulative` into every country of every snapshot, in place."""
    by_month = stitched_ledger(snapshots)
    if not by_month:
        for snap in snapshots:
            for country in snap.get("countries", {}).values():
                country.setdefault("metrics", {})["convoys_lost_cumulative"] = None
        return snapshots
    first = min(by_month)
    running: dict[str, float] = {}
    covered_up_to = first - 1          # last month with continuous coverage from `first`
    cursor = first
    for snap in snapshots:
        last_complete = month_index(snap["date"]) - 1
        while cursor <= last_complete:
            if cursor not in by_month:
                break
            for _m, _killer, owner, n in by_month[cursor]:
                running[owner] = running.get(owner, 0.0) + n
            covered_up_to = cursor
            cursor += 1
        known = last_complete <= covered_up_to
        for tag, country in snap.get("countries", {}).items():
            country.setdefault("metrics", {})["convoys_lost_cumulative"] = running.get(tag, 0.0) if known else None
    return snapshots
