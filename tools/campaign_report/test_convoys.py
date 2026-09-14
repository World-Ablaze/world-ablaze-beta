"""Cumulative convoy losses: stitching, running sums, and unknown once a month is uncovered."""
from __future__ import annotations

import unittest

from .convoys import enrich_cumulative_losses, stitched_ledger


def snap(date, window=None, losses=None, tags=("ENG", "GER")):
    return {"date": date, "countries": {t: {"metrics": {}} for t in tags},
            "convoy_window": window, "convoy_losses": losses}


class CumulativeLossTests(unittest.TestCase):
    def test_running_sum_follows_the_stitched_ledger(self):
        m = 1940 * 12 + 5  # June 1940 = last complete month of a 1940.7 save
        saves = [
            snap("1940.6.1.2", [m - 24, m - 1], [[m - 1, "GER", "ENG", 4]]),
            snap("1940.7.1.2", [m - 23, m], [[m - 1, "GER", "ENG", 4], [m, "GER", "ENG", 6], [m, "ENG", "GER", 1]]),
            snap("1940.8.1.2", [m - 22, m + 1], [[m, "GER", "ENG", 6], [m, "ENG", "GER", 1], [m + 1, "ITA", "ENG", 2]]),
        ]
        enrich_cumulative_losses(saves)
        eng = [s["countries"]["ENG"]["metrics"]["convoys_lost_cumulative"] for s in saves]
        ger = [s["countries"]["GER"]["metrics"]["convoys_lost_cumulative"] for s in saves]
        # The 1940.8 save also covers m-1 and records nothing there: latest covering save wins, so the
        # 4 convoys of m-1 are superseded, not kept.
        self.assertEqual(eng, [0.0, 6.0, 8.0])
        self.assertEqual(ger, [0.0, 1.0, 1.0])

    def test_uncovered_month_makes_later_values_unknown(self):
        m = 1941 * 12 + 2
        saves = [snap("1941.4.1.2", [m - 23, m], [[m, "GER", "ENG", 3]]),
                 snap("1943.6.1.2", [m + 4, m + 27], [[m + 27, "GER", "ENG", 5]])]  # gap: m+1..m+3 uncovered
        enrich_cumulative_losses(saves)
        self.assertEqual(saves[0]["countries"]["ENG"]["metrics"]["convoys_lost_cumulative"], 3.0)
        self.assertIsNone(saves[1]["countries"]["ENG"]["metrics"]["convoys_lost_cumulative"])
        self.assertEqual(sorted(stitched_ledger(saves))[:2], [m - 23, m - 22])

    def test_no_ledger_anywhere_stays_unknown(self):
        saves = [snap("1936.2.1.2"), snap("1936.3.1.2")]
        enrich_cumulative_losses(saves)
        self.assertIsNone(saves[1]["countries"]["ENG"]["metrics"]["convoys_lost_cumulative"])


if __name__ == "__main__":
    unittest.main()
