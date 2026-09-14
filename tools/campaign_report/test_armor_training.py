"""Boundaries that prevent plausible but fabricated training shortages."""
import tempfile
import unittest
from pathlib import Path

from .armor_training import analyze_training, unit_equipment_needs
from .extract import parse


class TrainingTests(unittest.TestCase):
    catalog = {
        "tank": {"domain": "armor", "family": "tank"},
        "tank_model": {"domain": "armor", "family": "tank"},
        "rifle": {"domain": None, "family": "rifle"},
    }
    templates = {1: {"regs": {"armor": 2}, "sup": {"support": 1}}}
    definitions = {7: {"definition": "tank_model"}}
    needs = {"armor": {"tank": 25}, "support": {"tank": 5, "rifle": 10}}

    def analyze(self, text, **kwargs):
        return analyze_training(parse(text).block("deployment"),
                                kwargs.get("templates", self.templates), self.definitions,
                                self.catalog, kwargs.get("needs", self.needs))

    @staticmethod
    def deployment(amounts, repeat=1):
        lines = "".join(
            "military_deployment_line={ amount=" + str(repeat) + " military_deployment={ equipment={ equipment={ id={id=7} amount=" + str(amount) + "} } } }"
            for amount in amounts)
        return "deployment={ military_deployment_conveyor={division_template_id={id=1} amount=-1 " + lines + "} }"

    def test_template_support_and_instances_without_future_repeats(self):
        result = self.analyze(self.deployment([10, 60], repeat=8))
        self.assertEqual(result["instances"], 2)
        self.assertEqual(result["families"]["tank"], {"requirement": 110, "held": 70, "gap": 45})
        self.assertEqual(result["variants"], {7: 70})

    def test_missing_deployment_and_empty_queue_are_distinct(self):
        result = analyze_training(None, {}, {}, {}, {})
        self.assertFalse(result["requirements_complete"])
        empty = self.analyze("deployment={}")
        self.assertTrue(empty["requirements_complete"])
        self.assertEqual(empty["instances"], 0)

    def test_missing_template_or_unit_prevents_partial_total(self):
        for kwargs in ({"templates": {}}, {"needs": {"armor": {"tank": 25}}}):
            result = self.analyze(self.deployment([10]), **kwargs)
            self.assertIsNone(result["families"]["tank"]["requirement"])
            self.assertIsNone(result["families"]["tank"]["gap"])
            self.assertEqual(result["families"]["tank"]["held"], 10)

    def test_unknown_held_variant_prevents_invented_gap(self):
        result = self.analyze(self.deployment([10]).replace("id=7", "id=99"))
        self.assertEqual(result["families"]["tank"]["requirement"], 55)
        self.assertIsNone(result["families"]["tank"]["held"])
        self.assertIsNone(result["families"]["tank"]["gap"])

    def test_waiting_serial_line_does_not_invent_training_instance(self):
        result = self.analyze("deployment={military_deployment_conveyor={division_template_id={id=1} military_deployment_line={amount=10}}}")
        self.assertEqual(result["instances"], 0)
        self.assertEqual(result["families"], {})

    def test_catalog_refuses_expressions_and_ignores_comments(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder) / "common/units"
            directory.mkdir(parents=True)
            (directory / "units.txt").write_text("sub_units={ armor={need={tank=25}} bad={need={tank=constant:unknown}} missing={} # fake={need={tank=999}}\n }", encoding="utf-8")
            self.assertEqual(unit_equipment_needs(folder), {"armor": {"tank": 25}, "bad": None, "missing": None})


if __name__ == "__main__":
    unittest.main()
