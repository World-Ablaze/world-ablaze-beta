"""Production-counter differences must not turn gaps or resets into output."""
import unittest

from .armor_production import enrich_snapshots, production_counter
from .extract import parse


def snapshot(date, value=None, tag="GER"):
    return {"date": date, "file": date + ".hoi4",
            "countries": {tag: {"armor": {"production_total": value}}}}


class ProductionCounterTests(unittest.TestCase):
    def test_counter_preserves_zero_and_missing(self):
        self.assertIsNone(production_counter(None))
        self.assertIsNone(production_counter(parse("")))
        self.assertEqual(production_counter(parse("equipment_production={armor=0}")), 0)
        self.assertEqual(production_counter(parse("equipment_production={armor=12386}")), 12386)
        for value in ("-1", "nan", "inf", "unreadable"):
            self.assertIsNone(production_counter(parse("equipment_production={armor=" + value + "}")))

    def test_interval_uses_calendar_days_and_records_provenance(self):
        rows = [snapshot("1943.5.1.2", 11791), snapshot("1943.6.1.2", 12386)]
        self.assertIs(enrich_snapshots(rows), rows)
        armor = rows[1]["countries"]["GER"]["armor"]
        self.assertAlmostEqual(armor["observed_production_per_day"], 595 / 31)
        self.assertEqual(armor["observed_production_count"], 595)
        self.assertEqual(armor["production_interval"],
                         {"from": "1943.5.1.2", "to": "1943.6.1.2", "days": 31,
                          "previous_file": "1943.5.1.2.hoi4"})
        self.assertIsNone(rows[0]["countries"]["GER"]["armor"]["observed_production_per_day"])

    def test_leap_day_and_hours(self):
        rows = [snapshot("1940.2.1.2", 0), snapshot("1940.3.1.14", 59)]
        enrich_snapshots(rows)
        self.assertEqual(rows[1]["countries"]["GER"]["armor"]["observed_production_per_day"], 2)

    def test_resets_missing_and_country_disappearance_break_intervals(self):
        for rows in ([snapshot("1943.5.1", 20), snapshot("1943.6.1", 5)],
                     [snapshot("1943.5.1", None), snapshot("1943.6.1", 5)],
                     [snapshot("1943.5.1", 5), snapshot("1943.6.1", None)],
                     [snapshot("1943.5.1", 5), snapshot("1943.6.1", 7, "USA")],
                     [snapshot("1943.5.1", 5), snapshot("1943.6.1", 7, "USA"), snapshot("1943.7.1", 10)]):
            enrich_snapshots(rows)
            for country in rows[-1]["countries"].values():
                self.assertIsNone(country["armor"]["observed_production_per_day"])

    def test_dates_must_increase_and_zero_delta_is_valid(self):
        for first, second in (("1943.5.1", "1943.5.1"), ("1943.6.1", "1943.5.1"), ("bad", "1943.5.1")):
            rows = [snapshot(first, 5), snapshot(second, 5)]
            enrich_snapshots(rows)
            self.assertIsNone(rows[1]["countries"]["GER"]["armor"]["observed_production_per_day"])
        rows = [snapshot("1943.5.1", 5), snapshot("1943.6.1", 5)]
        enrich_snapshots(rows)
        self.assertEqual(rows[1]["countries"]["GER"]["armor"]["observed_production_per_day"], 0)

    def test_reenrichment_clears_stale_values_after_filtering(self):
        rows = [snapshot("1943.5.1", 5), snapshot("1943.6.1", 10)]
        enrich_snapshots(rows)
        enrich_snapshots(rows[1:])
        self.assertIsNone(rows[1]["countries"]["GER"]["armor"]["observed_production_per_day"])


if __name__ == "__main__":
    unittest.main()
