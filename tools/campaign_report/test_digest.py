"""The agent-facing digest: sampling, missing values, war lifetimes, caps and the CLI path."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from . import SCHEMA_VERSION
from .__main__ import main
from .digest import MAX_TAGS, digest, sample_indices


def snapshot(date, file, countries):
    return {"date": date, "file": file, "warnings": [], "countries": countries}


def country(divisions=None, wars=(), issues=(), armor=None, resources=None):
    return {"metrics": {"manpower_free": 1000.0, "divisions": divisions, "losses": 5.5, "stability": 0.5},
            "army": {"types": {"foot": 3, "armour": 1}, "manpower_by_origin": {"GER": 900.0, "HUN": 100.0},
                     "templates": [{"name": "Infantry A", "family": "foot", "count": 3}]},
            "navy": {"types": {}}, "air": {"types": {"fighter": 40}},
            "equipment": {"families": {k: dict(domain="armor", **v) for k, v in (armor or {}).items()}}, "resources": resources or {},
            "wars": list(wars), "issues": list(issues)}


def data(snapshots, tags=("GER", "ENG")):
    return {"schema_version": SCHEMA_VERSION, "campaign": {"id": "abc", "count": len(snapshots), "selection": "campaign"},
            "generated_at": "2026-09-07T00:00:00+00:00", "default_tags": list(tags),
            "metric_catalog": {"manpower": {"label": "Available manpower", "evidence": "ASSUMED",
                                            "source": "countries/TAG/manpower/ratio", "note": "raw"}},
            "dependencies_sha256": "0123456789abcdef", "inputs": [{"file": s["file"], "version": "1.19.2", "mods": "wa"} for s in snapshots],
            "warnings": ["top-level caveat"], "snapshots": snapshots, "build": {"cache_hits": len(snapshots)}}


class DigestTests(unittest.TestCase):
    def three(self):
        war = {"id": "GER|POL|1939.9.1.1", "enemy": "POL", "start_date": "1939.9.1.1", "losses": 10.0}
        return [
            snapshot("1939.6.1.2", "a.hoi4", {"GER": country(10), "ENG": country(None)}),
            snapshot("1939.12.1.2", "b.hoi4", {"GER": country(12, wars=[{**war, "losses": 20.0}], issues=["late issue"])}),
            snapshot("1940.1.1.2", "c.hoi4", {"GER": country(14, armor={"medium_tank_chassis": {"stock": -1.0, "deployed": 5, "reinforcement_need": 30, "active_factories": 2}},
                                                              resources={"steel": {"produced": 10, "imported": 2, "available": 12, "effective": -3},
                                                                         "delivered": {"produced": 0, "imported": 0, "available": 0, "effective": 0}}),
                                              "ENG": country(3)}),
        ]

    def test_sampling_keeps_first_of_bucket_and_last(self):
        snaps = self.three()
        self.assertEqual(sample_indices(snaps, 12), [0, 2])
        self.assertEqual(sample_indices(snaps, 6), [0, 1, 2])
        self.assertEqual(sample_indices(snaps[:1], 12), [0])

    def test_missing_values_and_absent_country_print_as_dash_never_zero(self):
        text = digest(data(self.three()), every=6)
        self.assertIn("| 1939.06 | 1000 | — |", text)          # ENG divisions None at first save
        self.assertIn("| 1939.12 | — | — |", text)              # ENG absent from the second save
        self.assertIn("No deployed-division record for ENG from 1939.06 to before 1940.01.", text)
        self.assertNotIn("No deployed-division record for GER", text)
        self.assertIn("**ASSUMED**", text)
        self.assertIn("`countries/TAG/manpower/ratio`", text)

    def test_war_lifetime_marks_vanished_relation(self):
        text = digest(data(self.three()))
        self.assertIn("| POL | 1939.9.1.1 | 1939.12 | 1939.12 (gone) | 20 |", text)
        self.assertIn("ENG — 0 war relation(s)", text)

    def test_last_save_sections_and_pseudo_resources_filtered(self):
        text = digest(data(self.three()))
        self.assertIn("medium_tank_chassis: shortfall 31 = requests 30 - stock -1; deployed 5, active factories 2", text)
        self.assertIn("- ENG: none", text)
        self.assertIn("steel produced 10 / imported 2 / available 12 / effective -3", text)
        self.assertNotIn("delivered", text)
        self.assertIn("Foreign manpower in commanded divisions: HUN 100", text)
        self.assertIn("- GER: late issue (1 save(s))", text)
        self.assertIn("- top-level caveat", text)
        self.assertIn("`a.hoi4`, `b.hoi4`, `c.hoi4`", text)

    def test_convoy_section_stitches_ledgers_and_shares(self):
        snaps = self.three()
        m = 1939 * 12 + 10  # 1939.11 as index
        snaps[1].update(convoy_window=[m - 23, m], convoy_losses=[[m, "GER", "ENG", 7], [m, "ITA", "ENG", 3], [m - 1, "GER", "ENG", 10]])
        snaps[2].update(convoy_window=[m - 22, m + 1], convoy_losses=[[m + 1, "GER", "ENG", 4], [m, "GER", "ENG", 7], [m, "ITA", "ENG", 3]])
        snaps[2]["countries"]["ENG"]["metrics"].update(convoys_pool=900, convoys_free=100)
        text = digest(data(snaps))
        # The later save also covers month m-1 and records no loss there: the latest covering save
        # wins, so the earlier save's 10 convoys at m-1 are superseded, never added.
        self.assertIn("| ENG | 14 | GER 79 % (11), ITA 21 % (3) | 0 | — | 900 / 100 |", text)
        self.assertIn("| GER | 0 | — | 11 | ENG 100 % (11) | — / — |", text)
        self.assertIn("25 months covered", text)
        self.assertIn("No convoy-loss ledger", digest(data(self.three())))

    def test_caps_and_validation(self):
        with self.assertRaisesRegex(ValueError, "At most"):
            digest(data(self.three()), tags=[f"T{i:02d}" for i in range(MAX_TAGS + 1)])
        with self.assertRaisesRegex(ValueError, "every"):
            digest(data(self.three()), every=0)
        with self.assertRaisesRegex(ValueError, "nothing to digest"):
            digest(data([]))
        text = digest(data(self.three()), tags=["XXX"])
        self.assertIn("No observation of XXX", text)

    def test_cli_digest_from_json(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "campaign.json"
            source.write_text(json.dumps(data(self.three())), encoding="utf-8")
            self.assertEqual(main(["digest", str(source), "--tags", "ger", "--every", "6"]), 0)
            written = (root / "campaign_digest.md").read_text(encoding="utf-8")
            self.assertIn("### GER", written)
            self.assertNotIn("### ENG", written)
            self.assertNotIn("\r", written)
            bad = root / "bad.json"
            bad.write_text(json.dumps({"schema_version": SCHEMA_VERSION, "snapshots": []}), encoding="utf-8")
            self.assertEqual(main(["digest", str(bad)]), 2)


if __name__ == "__main__":
    unittest.main()
