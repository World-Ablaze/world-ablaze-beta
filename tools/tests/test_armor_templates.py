"""[armor-template-generator] Semantic tests for the armour template generator.

Run: python -m unittest discover -s tools/tests -p test_armor_templates.py

The fixtures are hand-authored: they state what each owner decision must produce, so a change to
the resolver that quietly breaks A6, A8 or A11 fails here rather than in a campaign. Tests that
need the real unit definitions read them once; tests of the pure resolver do not.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "gen"))

from armor_templates import emit, inputs, model, resolve, validate  # noqa: E402

REGISTRY = model.load(REPO)
GAME = inputs.GameFiles(REPO)
E = resolve.EMPTY


def facts(family, **kw):
    base = dict(mobile_infantry="mechanized", variant=E, td=E, spaa=E, rockets=False,
                quota=0, waves=False, heavy_company=False)
    base.update(kw)
    return resolve.Facts(family, base["mobile_infantry"], base["variant"], base["td"],
                         base["spaa"], base["rockets"], base["quota"], base["waves"],
                         base["heavy_company"])


def sel(family, **kw):
    return resolve.resolve(family, facts(family, **kw), REGISTRY, GAME)


class LineAllocation(unittest.TestCase):
    """A11: the variant block replaces medium support first, then main tanks."""

    MAIN = "medium_armor_battalion_line"
    SUP = "medium_support_armor_battalion_line"
    SPG = "medium_self_propelled_gun_battalion_line"

    def test_quota_six_no_variant(self):
        s = sel("medium", quota=6)
        self.assertEqual(s.line[self.MAIN], 4)
        self.assertEqual(s.line[self.SUP], 6)

    def test_quota_three_no_variant(self):
        s = sel("medium", quota=3)
        self.assertEqual(s.line[self.MAIN], 7)
        self.assertEqual(s.line[self.SUP], 3)

    def test_quota_zero_no_variant(self):
        s = sel("medium", quota=0)
        self.assertEqual(s.line[self.MAIN], 10)
        self.assertNotIn(self.SUP, s.line)

    def test_quota_six_with_variant(self):
        s = sel("medium", quota=6, variant="medium_inf_support")
        self.assertEqual(s.line[self.MAIN], 4)
        self.assertEqual(s.line[self.SUP], 3)
        self.assertEqual(s.line["medium_infantry_support_armor_battalion_line"], 3)

    def test_quota_three_with_variant_keeps_seven_tanks(self):
        s = sel("medium", quota=3, variant="medium_inf_support")
        self.assertEqual(s.line[self.MAIN], 7)
        self.assertNotIn(self.SUP, s.line)

    def test_budget_is_ten_before_waves(self):
        for quota in (6, 3, 0):
            for variant in (E, "medium_assault", "medium_inf_support"):
                s = sel("medium", quota=quota, variant=variant)
                armoured = sum(v for k, v in s.line.items()
                               if not k.startswith("infantry_heavy_"))
                self.assertEqual(armoured, 10, (quota, variant))

    def test_mobile_infantry_is_five(self):
        s = sel("medium", quota=6)
        self.assertEqual(s.line["infantry_heavy_mechanized_battalion_line"], 5)


class Waves(unittest.TestCase):
    """A9: -1 main tank, -2 mechanized, applied once."""

    def test_deltas(self):
        base = sel("medium", quota=0)
        wave = sel("medium", quota=0, waves=True)
        self.assertEqual(wave.line["medium_armor_battalion_line"],
                         base.line["medium_armor_battalion_line"] - 1)
        self.assertEqual(wave.line["infantry_heavy_mechanized_battalion_line"],
                         base.line["infantry_heavy_mechanized_battalion_line"] - 2)

    def test_twelve_battalions_reach_thirty(self):
        wave = sel("medium", quota=0, waves=True)
        self.assertEqual(sum(wave.line.values()), 12)
        self.assertAlmostEqual(wave.width, 30.0)

    def test_motorized_has_no_wave_plane_by_default(self):
        values = resolve.axis_values(REGISTRY, "medium", "waves", "motorized")
        self.assertEqual(values, [False])


class Width(unittest.TestCase):
    """The 30-width target, including the sub-doctrines the registry assumes the AI holds."""

    ASSUMED = ("pre_assault_bombardment",)

    def test_registry_assumes_pre_assault_bombardment(self):
        self.assertEqual(
            tuple(REGISTRY.composition["width_assumptions"]["subdoctrines"]), self.ASSUMED)

    def test_that_subdoctrine_takes_one_off_every_spg_line(self):
        for unit in ("light_self_propelled_gun_battalion_line",
                     "medium_self_propelled_gun_battalion_line",
                     "modern_self_propelled_gun_battalion_line",
                     "heavy_self_propelled_gun_battalion_line"):
            self.assertEqual(GAME.assumed_width_delta(unit, self.ASSUMED), -1.0, unit)

    def test_spg_block_is_six_wide_like_the_others(self):
        spg = sel("medium", variant="medium_spg")
        assault = sel("medium", variant="medium_assault")
        self.assertAlmostEqual(spg.width, assault.width)
        self.assertAlmostEqual(spg.width, 30.0)

    def test_every_target_is_thirty_wide(self):
        for family_id in REGISTRY.families:
            sels, _e, _p = resolve.enumerate_family(family_id, REGISTRY, GAME)
            for s in sels:
                self.assertAlmostEqual(s.width, 30.0, msg=s.name)

    def test_dropping_the_assumption_breaks_the_spg_block(self):
        """The assumption is load-bearing: without it the SPG block is 9 wide, not 6."""
        comp = REGISTRY.composition
        saved = comp["width_assumptions"]["subdoctrines"]
        comp["width_assumptions"]["subdoctrines"] = []
        try:
            self.assertAlmostEqual(sel("medium", variant="medium_spg").width, 33.0)
        finally:
            comp["width_assumptions"]["subdoctrines"] = saved

    def test_waves_modifier_covers_every_line_unit_a_wave_target_fields(self):
        needed = set()
        for family_id in REGISTRY.families:
            sels, _e, _p = resolve.enumerate_family(family_id, REGISTRY, GAME)
            for s in sels:
                if s.facts.waves:
                    needed.update(s.line)
        self.assertEqual(sorted(u for u in needed if u not in GAME.waves_modifiers), [])


class HeavyRestriction(unittest.TestCase):
    """A4/A6."""

    def test_heavy_candidate_rejected_in_medium(self):
        with self.assertRaises(resolve.ResolveError):
            sel("medium", variant="heavy_spg")

    def test_heavy_company_rejected_in_heavy(self):
        with self.assertRaises(resolve.ResolveError):
            sel("heavy", heavy_company=True)

    def test_heavy_company_admitted_in_medium_and_modern(self):
        for family in ("medium", "modern"):
            s = sel(family, heavy_company=True)
            self.assertIn("heavy_armor_company_divisional", s.support)

    def test_heavy_company_replaces_the_towed_artillery_company(self):
        plain = sel("medium")
        twin = sel("medium", heavy_company=True)
        self.assertIn("heavy_artillery_mot_company_divisional", plain.support)
        self.assertNotIn("heavy_artillery_mot_company_divisional", twin.support)
        self.assertEqual(sum(plain.support.values()), sum(twin.support.values()))

    def test_no_heavy_equipment_in_a_medium_target(self):
        s = sel("medium", variant="medium_spg", td="medium_td", spaa="medium_spaa")
        for unit in s.units():
            demand = GAME.unit(unit).need if GAME.unit(unit) else {}
            self.assertFalse(any(k.startswith("heavy_tank") for k in demand), unit)


class RegimentalSupport(unittest.TestCase):
    """A8: five tank-destroyer slots, five artillery slots, rockets capped at two."""

    def test_towed_fallbacks(self):
        s = sel("medium")
        self.assertEqual(s.regimental["anti_tank_mot_company_regimental"], 5)
        self.assertEqual(s.regimental["pack_artillery_mot_company_regimental"], 5)

    def test_rockets_alone_fill_five(self):
        s = sel("medium", rockets=True)
        self.assertEqual(s.regimental["mechanized_sp_rocket_artillery_company_regimental"], 5)

    def test_spg_alone_fills_five(self):
        s = sel("medium", variant="medium_spg")
        self.assertEqual(s.regimental["medium_self_propelled_gun_company_regimental"], 5)

    def test_two_rockets_plus_three_spg(self):
        s = sel("medium", variant="medium_spg", rockets=True)
        self.assertEqual(s.regimental["mechanized_sp_rocket_artillery_company_regimental"], 2)
        self.assertEqual(s.regimental["medium_self_propelled_gun_company_regimental"], 3)

    def test_heavy_spg_has_no_regimental_unit_and_says_so(self):
        s = sel("heavy", variant="heavy_spg")
        self.assertTrue(s.notes)
        self.assertNotIn("heavy_self_propelled_gun_company_regimental", s.regimental)

    def test_tank_destroyer_block(self):
        s = sel("medium", td="medium_td")
        self.assertEqual(s.regimental["medium_tank_destroyer_company_regimental"], 5)
        self.assertNotIn("anti_tank_mot_company_regimental", s.regimental)


class DivisionalSupport(unittest.TestCase):
    def test_capacity(self):
        s = sel("medium", variant="medium_spg", spaa="medium_spaa", heavy_company=True)
        self.assertLessEqual(sum(s.support.values()), REGISTRY.composition["divisional_slots"])

    def test_spaa_replaces_the_towed_anti_air(self):
        plain = sel("medium")
        spaa = sel("medium", spaa="medium_spaa")
        self.assertIn("heavy_anti_air_mot_company_divisional", plain.support)
        self.assertIn("medium_self_propelled_anti_air_company_divisional", spaa.support)
        self.assertNotIn("heavy_anti_air_mot_company_divisional", spaa.support)

    def test_chassis_tiered_engineer(self):
        self.assertIn("engineer_med_tank_battalion_divisional", sel("medium").support)
        self.assertIn("engineer_mod_tank_battalion_divisional", sel("modern").support)
        self.assertIn("engineer_mot_battalion_divisional", sel("light").support)


class Codes(unittest.TestCase):
    def test_codes_are_dense_and_unique_inside_the_declared_range(self):
        seen = set()
        for family_id, fam in REGISTRY.families.items():
            sels, errors, planes = resolve.enumerate_family(family_id, REGISTRY, GAME)
            self.assertEqual(errors, [], family_id)
            codes = [s.code for s in sels]
            self.assertEqual(len(codes), len(set(codes)), family_id)
            self.assertEqual(sorted(codes), list(range(min(codes), max(codes) + 1)), family_id)
            lo, hi = fam["code_range"]
            self.assertGreaterEqual(min(codes), lo)
            self.assertLessEqual(max(codes), hi)
            self.assertFalse(seen & set(codes), family_id)
            seen |= set(codes)

    def test_plane_arithmetic_matches_the_enumerated_code(self):
        for family_id in REGISTRY.families:
            planes = resolve.build_planes(REGISTRY, family_id)
            base = planes[0].base
            self.assertEqual(base, REGISTRY.families[family_id]["code_range"][0])
            for plane in planes:
                self.assertEqual(plane.size,
                                 _product(len(v) for _n, v in plane.axes))

    def test_every_target_name_is_unique(self):
        names = set()
        for family_id in REGISTRY.families:
            sels, _e, _p = resolve.enumerate_family(family_id, REGISTRY, GAME)
            for s in sels:
                self.assertNotIn(s.name, names)
                names.add(s.name)


class Rendering(unittest.TestCase):
    def test_output_is_deterministic(self):
        sels, _e, planes = resolve.enumerate_family("heavy", REGISTRY, GAME)
        first = emit.family_file(REGISTRY, "heavy", sels, GAME)
        second = emit.family_file(REGISTRY, "heavy", sels, GAME)
        self.assertEqual(first, second)

    def test_no_bom_and_lf_only(self):
        sels, _e, planes = resolve.enumerate_family("heavy", REGISTRY, GAME)
        text = emit.family_file(REGISTRY, "heavy", sels, GAME)
        self.assertFalse(text.startswith("﻿"))
        self.assertNotIn("\r", text)

    def test_braces_balance(self):
        sels, _e, planes = resolve.enumerate_family("heavy", REGISTRY, GAME)
        for text in (emit.family_file(REGISTRY, "heavy", sels, GAME),
                     emit.effects_file(REGISTRY, [("WA_TEST_effect", ["heavy"])],
                                       {"heavy": planes}),
                     emit.triggers_file(REGISTRY, {"heavy": sels})):
            self.assertEqual(text.count("{"), text.count("}"))

    def test_every_emitted_unit_exists(self):
        for family_id in REGISTRY.families:
            sels, _e, _p = resolve.enumerate_family(family_id, REGISTRY, GAME)
            for s in sels:
                for unit in s.units():
                    self.assertIsNotNone(GAME.unit(unit), unit)


class Inputs(unittest.TestCase):
    def test_registry_references_resolve(self):
        self.assertEqual(GAME.missing_units(REGISTRY.referenced_units()), [])
        self.assertEqual(GAME.missing_triggers(REGISTRY.referenced_triggers()), [])

    def test_heavy_subunits_demand_heavy_chassis(self):
        findings = validate._inputs(REGISTRY, GAME)
        self.assertEqual([f for f in findings if f.code == "HEAVY-DEMAND"], [])

    def test_measured_widths(self):
        self.assertEqual(GAME.unit("medium_armor_battalion_line").combat_width, 2.0)
        self.assertEqual(GAME.unit("infantry_heavy_mechanized_battalion_line").combat_width, 2.0)
        self.assertEqual(GAME.unit("medium_self_propelled_gun_battalion_line").combat_width, 3.0)


def _product(values):
    out = 1
    for v in values:
        out *= v
    return out


if __name__ == "__main__":
    unittest.main()
