from pathlib import Path
import unittest

from equipment_evaluator.config import load_config
from equipment_evaluator.efficiency_audit import evaluate_efficiency_domains
from equipment_evaluator.ground import TankEvaluator, evaluate_tech_ground
from equipment_evaluator.infantry import InfantryDB, evaluate_infantry
from equipment_evaluator.production_efficiency import (
    ARCHETYPE, FAMILY, PARENT, UNRELATED, EfficiencyModel, classify_relation,
)


MOD_ROOT = Path(__file__).resolve().parents[2]


class ProductionEfficiencyTests(unittest.TestCase):
    def test_five_percent_efficiency_loss_is_not_penalized(self):
        model = EfficiencyModel()
        self.assertAlmostEqual(0.001, model.adjusted_gain(0.001, 0.95))

    def test_relation_precedence(self):
        parents = {("old", "child")}
        ancestor = lambda a, b: (a, b) in parents
        self.assertEqual(PARENT, classify_relation(
            "old", "child", old_archetype="rifle", new_archetype="rifle",
            old_family="x", new_family="x", is_ancestor=ancestor))
        self.assertEqual(FAMILY, classify_relation(
            "a", "b", old_archetype="rifle", new_archetype="rifle",
            old_family="x", new_family="x", is_ancestor=lambda a, b: False))
        self.assertEqual(ARCHETYPE, classify_relation(
            "a", "b", old_archetype="rifle", new_archetype="rifle",
            old_family=None, new_family=None, is_ancestor=lambda a, b: False))
        self.assertEqual(UNRELATED, classify_relation(
            "a", "b", old_archetype="rifle", new_archetype="tank",
            old_family=None, new_family=None, is_ancestor=lambda a, b: False))

    def test_eng_parent_switch_retains_95_percent(self):
        cfg = load_config()
        rows = evaluate_infantry(MOD_ROOT, cfg, {"ENG"})
        row = next(t for t in rows if t.old.name == "eng_inf_1" and t.new.name == "eng_inf_2")
        self.assertEqual(PARENT, row.relation)
        self.assertAlmostEqual(0.95, row.retention)
        self.assertEqual("SWITCH", row.verdict)

    def test_strong_archetype_only_gain_can_justify_full_switch(self):
        cfg = load_config()
        rows = evaluate_infantry(MOD_ROOT, cfg, {"ENG"})
        row = next(t for t in rows if t.old.name == "eng_inf_3" and t.new.name == "eng_inf_4")
        self.assertEqual(ARCHETYPE, row.relation)
        self.assertAlmostEqual(0.75, row.retention)
        self.assertEqual("SWITCH", row.verdict)

    def test_sov_parallel_file_order_is_not_a_false_transition(self):
        cfg = load_config()
        rows = evaluate_infantry(MOD_ROOT, cfg, {"SOV"})
        pairs = {(t.old.name, t.new.name) for t in rows}
        self.assertNotIn(("sov_inf_2", "sov_inf_9"), pairs)
        self.assertIn(("sov_inf_1", "sov_inf_2"), pairs)
        self.assertIn(("sov_inf_1", "sov_inf_9"), pairs)
        self.assertIn(("sov_inf_9", "sov_inf_10"), pairs)

    def test_all_requested_domains_are_covered(self):
        cfg = load_config()
        domains = {"air", "tanks", "infantry", "artillery", "vehicles"}
        rows = evaluate_efficiency_domains(MOD_ROOT, cfg, domains, {"ENG", "SOV"})
        self.assertEqual(domains, {r.domain for r in rows})

    def test_tech_branches_are_not_treated_as_replacements(self):
        cfg = load_config()
        rows = evaluate_efficiency_domains(
            MOD_ROOT, cfg, {"artillery", "vehicles"}, {"ENG", "SOV"})
        self.assertFalse(any(r.relation == "unrelated" for r in rows))

    def test_sherman_chain_preserves_efficiency(self):
        cfg = load_config()
        rows = evaluate_efficiency_domains(MOD_ROOT, cfg, {"tanks"}, {"USA"})
        sherman_chain = [r for r in rows if r.group == "USA_medium_tank"]
        self.assertTrue(sherman_chain)
        self.assertTrue(all(r.retention >= 0.90 for r in sherman_chain))
        self.assertTrue(all(r.policy == "SWITCH_SAFE" for r in sherman_chain))

    def test_usa_medium_tank_branches_follow_the_technology_tree(self):
        cfg = load_config()
        rows = TankEvaluator(MOD_ROOT, cfg).evaluate({"USA"})
        pairs = {(r.old, r.new) for r in rows if r.group == "USA_medium_tank"}
        # M3 Lee branches to the Sherman family and the T20 family.  File
        # adjacency must never invent M4A3E8 -> T20.
        self.assertIn(("tank_usa_medium_chassis_2", "tank_usa_medium_chassis_3"), pairs)
        self.assertIn(("tank_usa_medium_chassis_2", "tank_usa_medium_chassis_5"), pairs)
        self.assertIn(("tank_usa_medium_chassis_5", "tank_usa_medium_chassis_6"), pairs)
        self.assertNotIn(("tank_usa_medium_chassis_4_2", "tank_usa_medium_chassis_5"), pairs)
        self.assertNotIn(("tank_usa_medium_chassis_4_2", "tank_usa_medium_chassis_6"), pairs)
        e8 = next(r for r in rows if r.group == "USA_medium_tank"
                  and r.old == "tank_usa_medium_chassis_4" and r.new == "tank_usa_medium_chassis_4_2")
        self.assertEqual("SWITCH_CONDITIONAL", e8.verdict)
        self.assertGreater(e8.raw_gain, 0.0)
        self.assertAlmostEqual(e8.raw_gain, e8.adjusted_gain)

    def test_generated_artillery_parent_links_are_case_insensitive(self):
        cfg = load_config()
        rows = evaluate_efficiency_domains(MOD_ROOT, cfg, {"artillery"}, {"CZE"})
        row = next(r for r in rows if r.old == "cze_art_1" and r.new == "cze_art_2")
        self.assertEqual("parent", row.relation)
        self.assertAlmostEqual(0.95, row.retention)

    def test_artillery_gets_integrated_stat_verdict(self):
        cfg = load_config()
        rows = evaluate_tech_ground(
            MOD_ROOT, cfg, "artillery",
            ("*artillery_GENERATED.txt", "*anti_tank_GENERATED.txt", "*anti_air_GENERATED.txt"),
            ("artillery*.txt",),
            {"artillery_equipment", "heavy_artillery_equipment", "pack_artillery_equipment",
             "rocket_artillery_equipment", "anti_tank_equipment", "heavy_anti_tank_equipment",
             "anti_air_equipment", "heavy_anti_air_equipment"}, {"ENG"})
        row = next(r for r in rows if r.old == "eng_art_2" and r.new == "eng_art_3")
        self.assertEqual("SWITCH", row.verdict)
        self.assertGreater(row.raw_gain, 0)

    def test_tank_redesign_recovers_hard_threshold(self):
        cfg = load_config()
        rows = TankEvaluator(MOD_ROOT, cfg).evaluate({"ENG", "SOV", "USA"})
        redesigned = [r for r in rows if r.verdict == "SWITCH_REDESIGNED"]
        self.assertTrue(redesigned)
        self.assertTrue(all(not r.failed_thresholds for r in redesigned))
        self.assertTrue(all(r.redesign_changes for r in redesigned))

    def test_duplicate_tank_design_name_is_not_a_transition(self):
        cfg = load_config()
        rows = TankEvaluator(MOD_ROOT, cfg).evaluate(None)
        self.assertFalse(any(row.old == row.new for row in rows))

    def test_ground_resource_increase_is_conditional(self):
        cfg = load_config()
        rows = TankEvaluator(MOD_ROOT, cfg).evaluate({"USA"})
        conditional = [r for r in rows if r.verdict == "SWITCH_CONDITIONAL"]
        self.assertTrue(conditional)
        self.assertTrue(all(r.significant_resources for r in conditional))


if __name__ == "__main__":
    unittest.main()
