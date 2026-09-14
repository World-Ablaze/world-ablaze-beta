"""Selection, cache invalidation and standalone export regression contracts."""
from __future__ import annotations

import json
import base64
import gzip
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock

from .cache import snapshot
from .campaign import REPO, discover, read_manifest, select
from .render import document, equipment_names, presentation


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def save(self, name="a.hoi4", identity="campaign-a", date="1940.1.1.12", session=1):
        path = self.root / name
        path.write_text(f'HOI4txt\nplayer="GER"\ndate="{date}"\nsession={session}\n'
                        f'game_unique_id="{identity}"\nstart_date="1936.1.1.12"\ncountries={{\n}}\n', encoding="utf-8")
        return path

    def test_equipment_names_resolve_bare_registry_keys_from_localisation(self):
        loc = self.root / "localisation/replace"
        loc.mkdir(parents=True)
        (loc / "x_l_english.yml").write_text('\ufeffl_english:\n tank_usa_medium_chassis_td_4:0 "M36 Jackson"\n'
                                             ' other_key:0 "Ignored" # comment\n', encoding="utf-8")
        names = equipment_names({"tank_usa_medium_chassis_td_4", "missing_key", None}, self.root)
        self.assertEqual(names, {"tank_usa_medium_chassis_td_4": "M36 Jackson"})
        self.assertEqual(equipment_names(set(), self.root), {})

    def test_identity_not_player_filename_and_multiple_campaigns_require_choice(self):
        self.save("GER_a.hoi4")
        self.save("BHU_b.hoi4", date="1940.2.1.12", session=2)
        self.save("GER_c.hoi4", identity="another")
        rows, errors = discover([self.root])
        self.assertFalse(errors)
        with self.assertRaisesRegex(ValueError, "single campaign"):
            select(rows, None)
        chosen, _ = select(rows, "campaign-a")
        self.assertEqual([r["date"] for r in chosen], ["1940.1.1.12", "1940.2.1.12"])

    def test_duplicate_dates_different_content_refused_even_with_override(self):
        self.save("a.hoi4")
        self.save("b.hoi4", session=2)
        rows, _ = discover([self.root])
        with self.assertRaisesRegex(ValueError, "Two different states"):
            select(rows, None, allow_ambiguous=True)

    def test_identical_duplicates_deduplicated(self):
        a = self.save()
        (self.root / "copy.hoi4").write_bytes(a.read_bytes())
        rows, _ = discover([self.root])
        chosen, warnings = select(rows, None)
        self.assertEqual(len(chosen), 1)
        self.assertEqual(len(warnings), 1)

    def test_session_reversal_requires_explicit_branch_selection(self):
        self.save("a.hoi4", session=5)
        self.save("b.hoi4", date="1941.1.1.12", session=2)
        rows, _ = discover([self.root])
        with self.assertRaisesRegex(ValueError, "ambiguous branch"):
            select(rows, None)
        chosen, warnings = select(rows, None, explicit_manifest=True)
        self.assertEqual(len(chosen), 2)
        self.assertTrue(any("ASSUMED" in w for w in warnings))

    def test_manifest_relative_paths_and_mixed_campaign_refused(self):
        self.save("a.hoi4")
        self.save("b.hoi4", identity="other")
        manifest = self.root / "branch.json"
        manifest.write_text('["a.hoi4", "b.hoi4"]')
        rows, _ = discover(read_manifest(manifest))
        with self.assertRaisesRegex(ValueError, "mixes"):
            select(rows, "campaign-a", explicit_manifest=True)

    def test_binary_and_corrupt_files_are_reported_not_zero_snapshots(self):
        self.save()
        (self.root / "binary.hoi4").write_bytes(b"HOI4bin1234")
        rows, errors = discover([self.root])
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("binary", errors[0])

    def test_zipped_text_metadata(self):
        text = self.save().read_bytes()
        archive = self.root / "compressed.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("gamestate", text)
        rows, errors = discover([archive])
        self.assertFalse(errors)
        self.assertEqual(rows[0]["game_unique_id"], "campaign-a")

    def test_cache_depends_on_bytes_and_dependencies_and_recovers_corruption(self):
        path = self.save()
        extractor = Mock(return_value={"date": "1940.1.1.12", "countries": {"GER": {}}})
        cache = self.root / "cache"
        args = (path, cache, "definitions-a", extractor, REPO)
        data, hit, first_hash = snapshot(*args)
        self.assertFalse(hit)
        self.assertTrue(snapshot(*args)[1])
        self.assertEqual(extractor.call_count, 1)
        next(cache.glob("*.json")).write_text("{unfinished", encoding="utf-8")
        self.assertFalse(snapshot(*args)[1])
        self.assertEqual(extractor.call_count, 2)
        self.assertFalse(snapshot(path, cache, "definitions-b", extractor, REPO)[1])
        path.write_bytes(path.read_bytes() + b"\n")
        _, hit, new_hash = snapshot(*args)
        self.assertFalse(hit)
        self.assertNotEqual(first_hash, new_hash)

    def test_html_is_self_contained_and_escapes_save_names(self):
        attack = '</script><script>alert(1)</script> /*__REPORT_APP__*/ <img src=x onerror=alert(1)>'
        data = {"title": attack, "snapshots": [{"name": attack}]}
        html = document(data)
        payload = re.search(r'<script id="report-data" type="application/json">(.*?)</script>', html, re.S).group(1)
        self.assertEqual(json.loads(payload), presentation(data))
        self.assertNotIn("</script>", payload)
        self.assertEqual(len(re.findall(r"<script\b", html)), 2)
        self.assertNotRegex(html, r'<(?:script|link)\b[^>]*(?:src|href)="https?://')
        self.assertNotIn('<img src=x', html)

    def test_presentation_adds_metadata_without_touching_observations(self):
        from .extract import METRICS
        data = {"metric_catalog": METRICS, "snapshots": [{"countries": {"GER": {"metrics": {"stability": .8}, "issues": ["kept as is"]}},
                "warnings": ["kept as is"]}]}
        shown = presentation(data)
        self.assertEqual(shown["metric_catalog"]["stability"]["label"], "Stability")
        self.assertEqual(shown["title"], "World Ablaze · Campaign overview")
        self.assertEqual(shown["snapshots"], data["snapshots"])
        self.assertEqual(shown["equipment_names"], {})
        self.assertEqual(presentation(shown), shown)

    def test_large_report_embeds_lossless_compressed_data(self):
        data = {"snapshots": [{"countries": {}, "test_padding": "source data " * 100000}]}
        html = document(data)
        payload = json.loads(re.search(r'<script id="report-data" type="application/json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(payload["encoding"], "gzip-base64")
        decoded = json.loads(gzip.decompress(base64.b64decode(payload["payload"])))
        self.assertEqual(decoded, presentation(data))
        self.assertLess(len(html), 100000)

    def test_package_cli_builds_with_spawn_workers_then_reuses_cache(self):
        first = self.save()
        second = self.save("b.hoi4", date="1941.1.1.12", session=2)
        output = self.root / "output/report.html"
        command = [sys.executable, "-m", "tools.campaign_report", "build", "--saves",
                   str(first), str(second), "--workers", "2", "--cache", str(self.root / "cache"),
                   "--output", str(output)]
        for expected in (0, 2):
            result = subprocess.run(command, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual(data["build"]["cache_hits"], expected)
            self.assertEqual(len(data["snapshots"]), 2)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
