from pathlib import Path
from tempfile import TemporaryDirectory
import itertools
import unittest

from equipment_evaluator.config import load_config
from equipment_evaluator.decide import SWITCH_CONDITIONAL, Transition
from equipment_evaluator.decision_manifest import sha256_bytes
from equipment_evaluator.diagnostics import Diagnostics
from equipment_evaluator.emit import Emitter, GATE_TRIGGERS, _pdx_num
from equipment_evaluator.generation.production_strategy import (
    _step_gates, build_group_blocks, emit_linear)
from equipment_evaluator.generation.adapters import tank_emitter_transition
from equipment_evaluator.generation.apply import apply_plan, verify_plan
from equipment_evaluator.generation.planner import (OperationPlan, ReplaceOperation,
                                                     build_plan, select_patches)
from equipment_evaluator.ground import TankEvaluator
from equipment_evaluator.owned_source import logical_source
from equipment_evaluator.parse_ai_equipment import parse_country_file


MOD_ROOT = Path(__file__).resolve().parents[2]


def operation(path: str, raw_bytes: bytes, original: str, replacement: str,
              operation_id: str = "op") -> ReplaceOperation:
    return ReplaceOperation(
        operation_id=operation_id, path=path, kind="test", group="group",
        design="design", start_hint=raw_bytes.decode("utf-8-sig").replace("\r\n", "\n").find(original),
        end_hint=0, source_fingerprint=sha256_bytes(raw_bytes),
        original_fingerprint=sha256_bytes(original.encode()),
        replacement_fingerprint=sha256_bytes(replacement.encode()),
        original=original, replacement=replacement)


class GenerationTests(unittest.TestCase):
    def test_apply_is_transactional_idempotent_and_preserves_encoding(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "common/ai_equipment/TEST_planes.txt"
            path.parent.mkdir(parents=True)
            original = "priority = {\n\tfactor = 1\n}"
            replacement = (
                "priority = {\n\tfactor = 1\n"
                "\t# WA_EQUIPGEN_BEGIN id=test_gate kind=hold_gate schema=1\n"
                "\tmodifier = { always = yes factor = 0 }\n"
                "\t# WA_EQUIPGEN_END id=test_gate\n}"
            )
            raw = b"\xef\xbb\xbfgroup = {\r\n\t" + original.replace("\n", "\r\n").encode() + b"\r\n}\r\n"
            path.write_bytes(raw)
            op = operation("common/ai_equipment/TEST_planes.txt", raw, original, replacement)
            op = ReplaceOperation(**{**op.__dict__, "end_hint": op.start_hint + len(original)})
            plan = OperationPlan(3, "manifest", [], [op])

            first = apply_plan(root, plan)
            after_first = path.read_bytes()
            second = apply_plan(root, plan)
            verified = verify_plan(root, plan)

            self.assertTrue(first.ok)
            self.assertEqual(1, len(first.changed_files))
            self.assertTrue(after_first.startswith(b"\xef\xbb\xbf"))
            self.assertIn(b"\r\n", after_first)
            self.assertEqual(after_first, path.read_bytes())
            self.assertEqual(["op"], second.noop_operations)
            self.assertEqual(["op"], verified.noop_operations)

    def test_stale_file_aborts_all_files(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            operations = []
            originals = {}
            for name in ("A", "B"):
                path = root / f"common/ai_equipment/{name}.txt"
                path.parent.mkdir(parents=True, exist_ok=True)
                raw = f"{name} = {{\n\tfactor = 1\n}}\n".encode()
                path.write_bytes(raw)
                originals[path] = raw
                old = "factor = 1"
                new = "factor = 2"
                op = operation(f"common/ai_equipment/{name}.txt", raw, old, new, name)
                operations.append(ReplaceOperation(
                    **{**op.__dict__, "end_hint": op.start_hint + len(old)}))
            # Concurrent edit after the plan was built.
            stale = root / "common/ai_equipment/B.txt"
            stale.write_text("B = {\n\tfactor = 1\n\t# user edit\n}\n", encoding="utf-8")
            stale_before = stale.read_bytes()

            result = apply_plan(root, OperationPlan(3, "manifest", [], operations))
            self.assertFalse(result.ok)
            self.assertEqual(originals[root / "common/ai_equipment/A.txt"],
                             (root / "common/ai_equipment/A.txt").read_bytes())
            self.assertEqual(stale_before, stale.read_bytes())

    def test_owned_module_is_reverted_only_in_logical_view(self):
        generated = (
            "modules = {\n"
            "\t# WA_EQUIPGEN_BEGIN id=x kind=module schema=1 mode=replace "
            "slot=engine original=old_engine\n"
            "\tengine = new_engine\n"
            "\t# WA_EQUIPGEN_END id=x\n"
            "\t# WA_EQUIPGEN_BEGIN id=y kind=module schema=1 mode=insert "
            "slot=tank original=__absent__\n"
            "\ttank = fuel_tank\n"
            "\t# WA_EQUIPGEN_END id=y\n"
            "}\n"
        )
        self.assertEqual("modules = {\n\tengine = old_engine\n}\n",
                         logical_source(generated))

    def test_owned_supersession_rewrite_is_reverted_in_logical_view(self):
        generated = (
            "modifier = {\n"
            "\t# WA_EQUIPGEN_BEGIN id=x kind=supersede schema=1 mode=replace "
            "original=old_tech\n"
            "\thas_tech = later_tech\n"
            "\t# WA_EQUIPGEN_END id=x\n"
            "\tfactor = 0\n"
            "}\n"
        )
        self.assertEqual("modifier = {\n\thas_tech = old_tech\n\tfactor = 0\n}\n",
                         logical_source(generated))

    def test_owned_frontier_factor_is_reverted_in_logical_view(self):
        generated = (
            "priority = {\n"
            "\t# WA_EQUIPGEN_BEGIN id=x kind=priority_factor schema=1 "
            "mode=replace original=100\n"
            "\tfactor = 42.8571428571\n"
            "\t# WA_EQUIPGEN_END id=x\n"
            "}\n"
        )
        self.assertEqual("priority = {\n\tfactor = 100\n}\n",
                         logical_source(generated))

    def test_tank_frontier_scope_keeps_whole_groups_only(self):
        from types import SimpleNamespace
        patches = [
            SimpleNamespace(country="USA", group="USA_medium_tanks", design="a"),
            SimpleNamespace(country="USA", group="USA_medium_tanks", design="b"),
            SimpleNamespace(country="USA", group="USA_fighter", design="c"),
        ]
        selected = select_patches(
            patches, "tank-frontiers", {("USA", "USA_medium_tanks")})
        self.assertEqual(["a", "b"], [item.design for item in selected])

    def test_planner_drops_byte_identical_reconciliation_patches(self):
        from types import SimpleNamespace
        patch = SimpleNamespace(
            country="GER", file="GER_tank.txt", group="GER_heavy_tanks",
            design="heavy_tank_1", kind="priority_chain", start=10, end=20,
            original="priority = { factor = 10 }",
            replacement="priority = { factor = 10 }")
        plan = build_plan(MOD_ROOT, "manifest", [patch], "tank-frontiers")
        self.assertEqual([], plan.operations)

    def test_usa_parallel_tank_branches_compile_one_complete_frontier(self):
        cfg, diag = load_config(), Diagnostics()
        evaluator = TankEvaluator(MOD_ROOT, cfg)
        rows = [row for row in evaluator.evaluate({"USA"})
                if row.group == "USA_medium_tanks"]
        frontiers = [row for row in evaluator.frontier_decisions
                     if row.group == "USA_medium_tanks"]
        groups = parse_country_file(
            MOD_ROOT / "common/ai_equipment/USA_tank.txt", "USA", diag, "land")
        emitter = Emitter(cfg, diag, file_suffix="tank", domain="tanks")
        emitter.run([tank_emitter_transition(row) for row in rows],
                    {"USA": groups}, MOD_ROOT / "common/ai_equipment", frontiers)

        patches = [patch for patch in emitter.patches
                   if patch.group == "USA_medium_tanks"]
        # On an ungenerated source this is seven complete priority patches;
        # on the repository after deployment it is a clean no-op.
        self.assertIn(len(patches), (0, 7))
        self.assertFalse(any(item.group == "USA_medium_tanks"
                             for item in emitter.blocked))
        if not patches:
            raw = (MOD_ROOT / "common/ai_equipment/USA_tank.txt").read_text(
                encoding="utf-8-sig")
            self.assertEqual(7, sum(
                f"USA_USA_medium_tanks_medium_tank_{i}_priority_factor_" in raw
                for i in range(1, 8)))
        primary = next(row for row in frontiers if row.action == "PRIMARY")
        self.assertEqual("medium_tank_5", primary.design)  # M4A3E8 Sherman
        self.assertGreater(primary.priority_factor,
                           next(row.priority_factor for row in frontiers
                                if row.design == "medium_tank_6"))  # T20
        by_rank = {row.rank: row.priority_factor for row in frontiers}
        self.assertEqual(
            [0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0],
            [by_rank[rank] for rank in range(1, 8)])

    def test_every_branched_tank_group_has_one_gap_free_frontier(self):
        cfg = load_config()
        evaluator = TankEvaluator(MOD_ROOT, cfg)
        evaluator.evaluate(None)
        by_group = {}
        for row in evaluator.frontier_decisions:
            by_group.setdefault((row.country, row.group), []).append(row)
        self.assertEqual(11, len(by_group))
        for key, rows in by_group.items():
            self.assertEqual(1, sum(row.action == "PRIMARY" for row in rows), key)
            self.assertTrue(all(row.priority_factor > 0 for row in rows), key)
            self.assertEqual(len(rows), len({row.rank for row in rows}), key)
            self.assertEqual(list(range(1, len(rows) + 1)),
                             sorted(row.rank for row in rows), key)
            ordered = sorted(rows, key=lambda row: row.rank, reverse=True)
            self.assertEqual(max(row.priority_factor for row in rows),
                             ordered[0].priority_factor, key)
            self.assertTrue(all(
                better.priority_factor / worse.priority_factor >= 3.0 - 1e-9
                for better, worse in zip(ordered, ordered[1:])), key)
            by_name = {row.design: row for row in rows}
            for row in rows:
                if row.fallback_design:
                    self.assertIn(row.fallback_design, by_name, key)
                    self.assertEqual(row.rank - 1,
                                     by_name[row.fallback_design].rank, key)

    def test_frontier_redesigns_keep_required_slots_and_count_limits_legal(self):
        cfg, diag = load_config(), Diagnostics()
        evaluator = TankEvaluator(MOD_ROOT, cfg)
        evaluator.evaluate(None)
        designs = {}
        ai_dir = MOD_ROOT / "common/ai_equipment"
        for path in ai_dir.glob("*_tank.txt"):
            tag = path.name.split("_", 1)[0]
            for group in parse_country_file(path, tag, diag, "land"):
                for design in group.designs:
                    designs[(tag, group.name, design.name)] = design
        for row in evaluator.frontier_decisions:
            if not row.redesign_changes:
                continue
            design = designs[(row.country, row.group, row.design)]
            modules = evaluator.model.effective_modules(design)
            slots = evaluator.db.resolve_slots(design.airframe or "")
            for change in row.redesign_changes:
                slot, values = change.split(":", 1)
                _old, new = values.split("->", 1)
                slot, new = slot.strip(), new.strip()
                self.assertFalse(slots[slot].required and new == "empty",
                                 (row.design, change))
                modules[slot] = new
            self.assertEqual([], evaluator.db.count_limit_violations(
                design.airframe or "", modules), row.design)
            default_stats = evaluator.model.compute(design)
            redesigned_resources = row.resources
            unsupported = {
                resource for resource, delta in redesigned_resources.items()
                if delta - default_stats.resources.get(resource, 0.0)
                >= cfg.resource_threshold(resource)
            } - cfg.runtime_resource_gates
            self.assertEqual(set(), unsupported, row.design)

    def test_configured_runtime_gates_match_emitter_vocabulary(self):
        self.assertEqual(load_config().runtime_resource_gates,
                         set(GATE_TRIGGERS))

    def test_la5_manual_gate_remains_under_manual_ownership(self):
        cfg, diag = load_config(), Diagnostics()
        groups = parse_country_file(
            MOD_ROOT / "common/ai_equipment/SOV_planes.txt", "SOV", diag)
        group = next(item for item in groups if item.name == "SOV_fighter_mr")
        transition = Transition(
            country="SOV", group=group.name, role=group.role,
            from_design="fighter_mr_6", to_design="fighter_mr_7",
            verdict=SWITCH_CONDITIONAL,
            res_significant={"aluminium": 1.0})
        emitter = Emitter(cfg, diag)
        emitter.run([transition], {"SOV": [group]},
                    MOD_ROOT / "common/ai_equipment")
        self.assertFalse(emitter.patches)
        self.assertTrue(any("already hand-gated" in item.reason
                            for item in emitter.blocked))


class ProductionStrategyTests(unittest.TestCase):
    """The production-line layer (ai_strategy production_upgrade_desire_offset).

    `ai_equipment` priority is the design layer and does not decide what a
    running line produces - campaign `bec4d829` failed R30/R31/R32/R33/R35 on
    that confusion.  These tests pin the two properties the emitted strategy
    has to have: every reachable gate state names exactly one wanted design,
    and no gate state leaves a branched role with nothing to build.
    """

    @classmethod
    def setUpClass(cls):
        cfg = load_config(MOD_ROOT / "tools/equipment_evaluator/config.json")
        evaluator = TankEvaluator(MOD_ROOT, cfg)
        evaluator.evaluate(None)
        cls.rows = evaluator.frontier_decisions
        cls.groups = {}
        for row in cls.rows:
            cls.groups.setdefault((row.country, row.group), []).append(row)

    def _gate_states(self, ordered):
        gates = {row.rank: set(_step_gates(row)) for row in ordered}
        universe = sorted(set().union(*gates.values())) if gates else []
        for size in range(len(universe) + 1):
            for combo in itertools.combinations(universe, size):
                yield set(combo), gates

    def test_equipment_token_is_carried(self):
        """The `id` of every strategy comes from target_variant `type =`."""
        missing = [f"{r.country}/{r.group}/{r.design}"
                   for r in self.rows if not r.equipment_type]
        self.assertEqual([], missing)

    def test_no_gate_state_empties_a_branched_role(self):
        """R35 leg (3): a closed gate must expose a fallback, never a hole."""
        for (country, group), rows in sorted(self.groups.items()):
            ordered = sorted(rows, key=lambda r: r.rank)
            for open_gates, gates in self._gate_states(ordered):
                reachable = [r for r in ordered if gates[r.rank] <= open_gates]
                self.assertTrue(
                    reachable,
                    f"{country}/{group} has no candidate with gates "
                    f"{sorted(open_gates)}")

    def test_emitted_blocks_are_exactly_the_reachable_winners(self):
        """One +100 per gate state - never zero, never two competing."""
        for (country, group), rows in sorted(self.groups.items()):
            ordered = sorted(rows, key=lambda r: r.rank)
            winners = set()
            for open_gates, gates in self._gate_states(ordered):
                reachable = [r for r in ordered if gates[r.rank] <= open_gates]
                if reachable:
                    winners.add(max(reachable, key=lambda r: r.rank).design)
            lines, _ = build_group_blocks(rows)
            text = "\n".join(lines)
            emitted = {r.design for r in ordered
                       if f"_{r.group}_{r.design} = {{" in text}
            self.assertEqual(
                winners, emitted,
                f"{country}/{group}: emitted {sorted(emitted)} but "
                f"{sorted(winners)} are reachable winners")

    def test_usa_medium_is_the_canonical_regression(self):
        """M4A3E8 with tungsten, M4A2 without - never T20/T23."""
        rows = self.groups[("USA", "USA_medium_tanks")]
        lines, _ = build_group_blocks(rows)
        text = "\n".join(lines)
        want = [ln for ln in lines if "value = 100" in ln]
        self.assertEqual(2, len(want), "expected exactly two wanted designs")
        # M4A3E8 is tank_usa_medium_chassis_4_2, M4A2 is _4, T20 _5, T23 _6.
        self.assertIn("id = tank_usa_medium_chassis_4_2", text)
        self.assertIn("id = tank_usa_medium_chassis_4", text)
        self.assertIn("WA_AI_EQUIPMENT_can_absorb_tungsten_shock_small", text)
        for prototype in ("tank_usa_medium_chassis_5", "tank_usa_medium_chassis_6"):
            block = text.split(f"id = {prototype}\n")[1].splitlines()[0]
            self.assertIn("value = -100", block,
                          f"{prototype} must be suppressed, not wanted")

    def test_linear_chain_suppression_rules(self):
        """KEEP_OLD/CONDITIONAL suppress; SWITCH-reachable and non-tags do not."""
        rows = [
            {"country": "USA", "group": "art", "old": "a1", "new": "a2",
             "old_label": "A1", "new_label": "A2", "verdict": "KEEP_OLD",
             "gates": [], "reason": ""},
            {"country": "USA", "group": "art", "old": "b1", "new": "b2",
             "old_label": "B1", "new_label": "B2",
             "verdict": "SWITCH_CONDITIONAL",
             "gates": ["WA_AI_EQUIPMENT_can_absorb_steel_shock_small"],
             "reason": ""},
            # reached by a plain SWITCH elsewhere -> must NOT be suppressed
            {"country": "USA", "group": "art", "old": "c1", "new": "c2",
             "old_label": "C1", "new_label": "C2", "verdict": "KEEP_OLD",
             "gates": [], "reason": ""},
            {"country": "USA", "group": "art", "old": "c0", "new": "c2",
             "old_label": "C0", "new_label": "C2", "verdict": "SWITCH",
             "gates": [], "reason": ""},
            # shared equipment bucket, not a country tag -> must NOT be emitted
            {"country": "GENERIC", "group": "art", "old": "g1", "new": "g2",
             "old_label": "G1", "new_label": "G2", "verdict": "KEEP_OLD",
             "gates": [], "reason": ""},
        ]
        with TemporaryDirectory() as tmp:
            files, skipped = emit_linear(tmp, "artillery", rows, apply=False)
        self.assertEqual(
            ["common/ai_strategy/WA_AI_PRODUCTION_COUNTRY_USA_ARTILLERY.txt"],
            sorted(files))
        text = files["common/ai_strategy/WA_AI_PRODUCTION_COUNTRY_USA_ARTILLERY.txt"]
        self.assertIn("id = a2", text)
        self.assertIn("id = b2", text)
        self.assertIn("NOT = { WA_AI_EQUIPMENT_can_absorb_steel_shock_small = yes }",
                      text)
        self.assertNotIn("id = c2", text)
        self.assertNotIn("GENERIC", str(files))
        self.assertEqual(2, len(skipped))
        self.assertEqual(2, text.count("value = -100"))
        self.assertEqual(0, text.count("value = 100"))

    def test_no_scientific_notation_reaches_pdxscript(self):
        """`factor = 9e-06` is read as 9 by the HOI4 parser - see _pdx_num."""
        self.assertEqual("0.000009", _pdx_num(9e-06))
        self.assertEqual("0.00003", _pdx_num(3e-05))
        self.assertEqual("100", _pdx_num(100.0))
        self.assertEqual("0", _pdx_num(0))


if __name__ == "__main__":
    unittest.main()
