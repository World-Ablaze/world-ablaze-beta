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

# A declared family (light, light_support) has no axes to enumerate: its targets are written out
# one by one because it is a conversion state machine, and its phase codes are written by the
# hand-written calculator that owns that machine.
ENUMERATED = [f for f, fam in REGISTRY.families.items()
              if fam.get("mode", "enumerated") != "declared"]
DECLARED = [f for f, fam in REGISTRY.families.items()
            if fam.get("mode", "enumerated") == "declared"]


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
        for family_id in ENUMERATED:
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

    def test_uncovered_wave_units_are_reported_not_assumed(self):
        """The doctrine prerequisite is not applied yet, so the gap must be a finding."""
        needed = set()
        per_family = {}
        for family_id in ENUMERATED:
            sels, _e, _p = resolve.enumerate_family(family_id, REGISTRY, GAME)
            per_family[family_id] = sels
            for s in sels:
                if s.facts.waves:
                    needed.update(s.line)
        uncovered = sorted(u for u in needed if u not in GAME.waves_modifiers)
        findings = validate._doctrine(REGISTRY, GAME, per_family)
        codes = [f.code for f in findings]
        want = REGISTRY.composition["waves"]["width_modifier"]
        installed = set(GAME.waves_modifiers.values())
        if uncovered:
            self.assertIn("WAVES-COVERAGE", codes)
        if installed - {want}:
            self.assertIn("WAVES-VALUE", codes)
        if not uncovered and not (installed - {want}):
            self.assertEqual(codes, [])


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
        for family_id in ENUMERATED:
            fam = REGISTRY.families[family_id]
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
        for family_id in ENUMERATED:
            planes = resolve.build_planes(REGISTRY, family_id)
            base = planes[0].base
            self.assertEqual(base, REGISTRY.families[family_id]["code_range"][0])
            for plane in planes:
                self.assertEqual(plane.size,
                                 _product(len(v) for _n, v in plane.axes))

    def test_every_target_name_is_unique(self):
        names = set()
        for family_id in ENUMERATED:
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

    def test_every_role_group_keeps_its_front_role_override(self):
        """Without it the engine distributes armour like infantry and every
        front_armor_score entry in the mod goes inert."""
        for family_id, fam in REGISTRY.families.items():
            sels = (resolve.enumerate_family(family_id, REGISTRY, GAME)[0]
                    if family_id in ENUMERATED else [])
            text = emit.family_file(REGISTRY, family_id, sels, GAME,
                                    declared=resolve.declared_profiles(
                                        REGISTRY, family_id, GAME))
            self.assertIn("front_role_override = %s" % fam["front_role_override"], text,
                          family_id)

    def test_every_emitted_unit_exists(self):
        for family_id in ENUMERATED:
            sels, _e, _p = resolve.enumerate_family(family_id, REGISTRY, GAME)
            for s in sels:
                for unit in s.units():
                    self.assertIsNotNone(GAME.unit(unit), unit)


class ShippedLadder(unittest.TestCase):
    """The join key between the ladder and the templates, re-derived from the SHIPPED script.

    A checker that only reads the generator's own manifest vouches for the generator with the
    generator; this reads the arithmetic out of the emitted effect instead.
    """

    def setUp(self):
        sys.path.insert(0, str(REPO / "tools"))
        import check_templates
        self.ct = check_templates

    def test_derivation_matches_the_manifest(self):
        import json
        derived, complaints = self.ct.derive_generated_values(REPO)
        self.assertEqual(complaints, [])
        manifest = json.loads((REPO / "tools" / "generated"
                               / "armor_templates_manifest.json").read_text(encoding="utf-8"))
        declared = {}
        for family in manifest["families"].values():
            if not family.get("emitted", True) or family.get("mode") == "declared":
                continue
            declared.setdefault(family["flag"], set()).update(
                x["code"] for x in family["targets"])
        self.assertEqual({k: sorted(v) for k, v in sorted(derived.items())},
                         {k: sorted(v) for k, v in sorted(declared.items())})

    def test_derivation_reads_the_script_and_not_the_manifest(self):
        """Mutating one stride in a copy of the ladder must change the derived set."""
        import re, shutil, tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "common" / "scripted_effects").mkdir(parents=True)
            src = REPO.joinpath(*self.ct.GENERATED_EFFECTS)
            text = src.read_text(encoding="utf-8")
            mutated = re.sub(r"multiply_temp_variable = \{ _wa_ag_digit = 24 \}",
                             "multiply_temp_variable = { _wa_ag_digit = 25 }", text, count=1)
            self.assertNotEqual(mutated, text, "fixture found no stride to mutate")
            (root.joinpath(*self.ct.GENERATED_EFFECTS)).write_text(mutated, encoding="utf-8")
            derived, _ = self.ct.derive_generated_values(root)
            original, _ = self.ct.derive_generated_values(REPO)
            self.assertNotEqual(derived, original)


class EmittedVocabulary(unittest.TestCase):
    """Every name the generated script uses must exist. `clear_temp_variable` did not, and only
    the boot log said so - four "Unknown effect-type" errors from a file that had passed every
    offline check."""

    def _rendered(self):
        import gen_ai_armor_templates as cli
        pf, planes, decl, groups, stats, _errs = cli.compile_all(REGISTRY, GAME)
        return cli.render(REGISTRY, GAME, pf, planes, decl, groups, stats)

    def test_no_invented_name_in_the_emitted_script(self):
        self.assertEqual(validate.rendered_scripts(self._rendered(), GAME), [])

    def test_the_gate_catches_the_effect_that_shipped_broken(self):
        body = "\n".join(["X = {", "\tclear_temp_variable = _wa_ag_digit", "}", ""])
        fake = {"common/scripted_effects/FAKE.txt": body}
        codes = [f.code for f in validate.rendered_scripts(fake, GAME)]
        self.assertIn("UNKNOWN-NAME", codes)

    def test_the_generated_files_no_longer_use_it(self):
        for path in ("common/scripted_effects/WA_AI_TEMPLATES_ARMOR_generated.txt",
                     "common/scripted_triggers/WA_AI_TEMPLATES_ARMOR_generated.txt"):
            self.assertNotIn("clear_temp_variable",
                             (REPO / path).read_text(encoding="utf-8"))


class RegimentalGeometry(unittest.TestCase):
    """The regimental block must fit the columns the battalion count can form.

    MEASURED (common/defines/05_defines.lua): 5 columns, 2 rows, 3 battalions required per row,
    and AI_BATTALION_BUILD_ORDER fills a column three deep before opening the next. So N
    battalions open floor(N/3) columns and carry 2 companies each. A wider block has companies
    the division designer can never place.
    """

    def test_fifteen_battalions_carry_five_plus_five(self):
        s = sel("medium", quota=0)
        self.assertEqual(sum(s.line.values()), 15)
        self.assertEqual(sorted(s.regimental.values()), [5, 5])

    def test_twelve_battalions_carry_four_plus_four(self):
        s = sel("medium", quota=0, waves=True)
        self.assertEqual(sum(s.line.values()), 12)
        self.assertEqual(sorted(s.regimental.values()), [4, 4])

    def test_the_rocket_cap_still_holds_in_a_four_slot_block(self):
        s = sel("medium", quota=0, waves=True, rockets=True, variant="medium_spg")
        rockets = s.regimental["mechanized_sp_rocket_artillery_company_regimental"]
        self.assertEqual(rockets, 2)
        self.assertEqual(sum(s.regimental.values()), 8)

    def test_no_emitted_target_asks_for_more_than_it_can_place(self):
        for family_id in ENUMERATED:
            for s in resolve.enumerate_family(family_id, REGISTRY, GAME)[0]:
                per_row = resolve.regimental_columns(sum(s.line.values()), GAME, REGISTRY)
                self.assertEqual(sum(s.regimental.values()), per_row * 2, s.name)


class DeclaredFamilies(unittest.TestCase):
    """light and light_support: a conversion state machine, declared target by target."""

    def test_both_families_are_declared(self):
        self.assertEqual(sorted(DECLARED), ["light", "light_support"])

    def test_every_declared_profile_resolves(self):
        for family_id in DECLARED:
            sels = resolve.declared_profiles(REGISTRY, family_id, GAME)
            self.assertEqual(len(sels), len(REGISTRY.families[family_id]["profiles"]))
            for s in sels:
                for unit in s.units():
                    self.assertIsNotNone(GAME.unit(unit), "%s: %s" % (s.name, unit))

    def test_the_soviet_park_survives_regeneration(self):
        """The COUNTRY_SOV_* profiles reproduce a real 1941 corps; they are the one place in this
        generator where a country tag is the point, and they must come through verbatim."""
        sels = {s.name: s for s in resolve.declared_profiles(REGISTRY, "light_support", GAME)}
        corps = sels["WA_AI_TEMPLATES_COUNTRY_SOV_LIGHT_SUPPORT_ARMOR_44_TEMPORARY"]
        self.assertEqual(corps.line, {"light_support_armor_battalion_line": 12,
                                      "light_armor_battalion_line": 6,
                                      "infantry_heavy_motorized_battalion_line": 4})
        self.assertAlmostEqual(corps.width, 44.0)
        self.assertIn("44", corps.profile["width_exception"])
        self.assertEqual(len([n for n in sels if "COUNTRY_SOV" in n]), 6)

    def test_declared_width_exceptions_are_named(self):
        for family_id in DECLARED:
            for s in resolve.declared_profiles(REGISTRY, family_id, GAME):
                if abs(s.width - 30.0) > 1e-6:
                    self.assertTrue((s.profile or {}).get("width_exception"),
                                    "%s is %g wide and declares no exception" % (s.name, s.width))

    def test_the_finals_mirror_the_medium_role_current_target(self):
        """A FINAL whose composition is not the destination role's CURRENT target makes the
        converting division land on a class nobody chose."""
        base = sel("medium", quota=0)
        for family_id in DECLARED:
            for s in resolve.declared_profiles(REGISTRY, family_id, GAME):
                if s.name.endswith(("TRANSITION_MOT_FINAL", "TRANSITION_MEC_FINAL")):
                    self.assertEqual(s.line["medium_armor_battalion_line"],
                                     base.line["medium_armor_battalion_line"], s.name)

    def test_every_replace_with_resolves_inside_its_own_group(self):
        """A cross-group replace_with pointer is the stall the owner measured live."""
        for family_id in DECLARED:
            ids = set(p["id"] for p in REGISTRY.families[family_id]["profiles"])
            for prof in REGISTRY.families[family_id]["profiles"]:
                if prof.get("replace_with"):
                    self.assertIn(prof["replace_with"], ids, prof["id"])

    def test_declared_families_emit_no_ladder(self):
        """Their phase codes are written by the hand-written calculator that owns the machine."""
        import gen_ai_armor_templates as cli
        _pf, _pl, _decl, groups, _stats, _errs = cli.compile_all(REGISTRY, GAME)
        for _name, families in groups:
            for family_id in families:
                self.assertNotIn(family_id, DECLARED)


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
