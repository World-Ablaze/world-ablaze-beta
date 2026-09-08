"""Deterministic extraction contracts; optional real-save parity uses three dates.

Run normal tests with unittest. Set WA_REPORT_REAL_SAVES=1 to run the slower
campaign fixture check against the owner's local a100b67c monthly saves.
"""
import os
import tempfile
import time
import json
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from . import extract as ex


class ExtractionTests(unittest.TestCase):
    def test_lexer_keeps_dates_duplicate_keys_and_quoted_braces(self):
        root = ex.parse('x={ start_date="1943.6.1.2" name="brace } name" need={a=1} need={a=2} }')
        node = root.block("x")
        self.assertEqual(node.scalar("start_date"), "1943.6.1.2")
        self.assertEqual(node.scalar("name"), "brace } name")
        self.assertEqual(len(node.all("need")), 2)
        self.assertEqual(ex.parse("date=1943.6.1.2").scalar("date"), "1943.6.1.2")
        self.assertEqual(ex._delta('name="literal { } }" # {'), 0)

    def test_signed_stock_and_compatible_requests_never_invent_variant_deficit(self):
        raw = {
            "scalars": ["stability=0.8\n"],
            "production": ["production={ equipments={ equipment={ id={id=9 type=70} amount=-12 } } military_lines={ equipment_variant_index={id=9 type=70} active_factories=3 speed=99 } }"],
            "units": ["units={ division={ division_template_id={id=2 type=52} equipment={equipment={id={id=9 type=70} amount=8}} army_manpower={army_manpower_value={value={tag=GER value=100} value={tag=HUN value=20}}} requests={reinforcement={request={need={medium_tank_chassis=4}}}} } division={division_template_id={id=2 type=52} army_manpower={army_manpower_value={value={tag=GER value=80}}}} }"],
            "diplomacy": ["diplomacy={active_relations={SOV={war_relation={first=GER second=SOV start_date=1941.6.22.12 first_casualties=5 second_casualties=7}}}}"],
        }
        definitions = {9: dict(id=9, definition="actual_chassis", name="Variant", creator="HUN")}
        catalog = {key: dict(domain="armor", family="medium_tank_chassis", role=None)
                   for key in ("actual_chassis", "medium_tank_chassis")}
        result, wars = ex._country("GER", raw, definitions, catalog, {}, {})
        family = result["equipment"]["families"]["medium_tank_chassis"]
        self.assertEqual(family["stock"], -12)
        self.assertEqual(family["stock_deficit"], 12)
        self.assertEqual(family["deployed"], 8)
        self.assertEqual(family["reinforcement_need"], 4)
        self.assertIsNone(family["deficit"])
        self.assertIsNone(family["production_per_day"])
        self.assertIsNone(result["equipment"]["variants"][0]["reinforcement_need"])
        self.assertEqual(result["army"]["manpower_by_origin"], {"GER": 180, "HUN": 20})
        self.assertEqual(result["metrics"]["army_manpower"], 200)
        self.assertEqual(result["metrics"]["divisions"], 2)
        self.assertEqual(wars[0]["start_date"], "1941.6.22.12")

    def test_resource_rows_come_only_from_ledger_blocks(self):
        lines = ["resources={\n", "\tproduced={\n", "\t\tsteel=100.0\n", "\t}\n",
                 "\tfuel={\n", "\t\tfuel_daily=3.0\n", "\t\tfuel_sent=1.0\n", "\t}\n",
                 "\tlend_lease={\n", "\t\tlended_cic=5.0\n", "\t\trequest=2.0\n", "\t}\n",
                 "\tto_use={\n", "\t\t{\n", "\t\t\tsteel=90.0\n", "\t\t}\n", "\t\t{\n", "\t\t}\n",
                 "\t\t{\n", "\t\t\tsteel=-4.0\n", "\t\t}\n", "\t}\n", "}\n"]
        result, _ = ex._country("GER", {"resources": lines}, {}, {}, {}, {})
        self.assertEqual(sorted(result["resources"]), ["steel"])
        self.assertEqual(result["resources"]["steel"]["produced"], 100.0)
        self.assertEqual(result["resources"]["steel"]["effective"], 86.0)

    def test_convoys_fatigue_and_kills_come_from_their_own_sections(self):
        raw = {"scalars": ["convoys_destroyed=9\n"],
               "variables": ["variables={\n", "\teconomic_fatigue=14\n", "\twa_tlm_nav_convoys=1841\n", "\tother=3\n", "}\n"],
               "convoys": ["convoys={ equipment={ equipment={ id={ id=65 type=70 } amount=18 } equipment={ id={ id=66 type=70 } amount=5 } } }"]}
        definitions = {65: dict(id=65, definition="convoy_1", creator="USA"), 66: dict(id=66, definition="not_a_convoy", creator="USA")}
        result, _ = ex._country("USA", raw, definitions, {}, {}, {})
        m = result["metrics"]
        self.assertEqual((m["convoy_kills"], m["economy_fatigue"], m["convoys_pool"]), (9, 14, 18))
        self.assertIsNone(m["convoys_in_use"])  # telemetry above the pool: the two measures disagree
        self.assertIsNone(m["convoys_free"])
        raw["variables"][2] = "\twa_tlm_nav_convoys=5\n"
        self.assertEqual(ex._country("USA", raw, definitions, {}, {}, {})[0]["metrics"]["convoys_in_use"], 13)
        empty, _ = ex._country("USA", {}, {}, {}, {}, {})
        for key in ("convoy_kills", "economy_fatigue", "convoys_free", "convoys_pool", "convoys_in_use"):
            self.assertIsNone(empty["metrics"][key], key)
        self.assertEqual(ex.convoy_window("1944.6.1.2"), [1944 * 12 + 4 - 23, 1944 * 12 + 4])

    def test_queued_line_without_active_factories_counts_as_zero_not_unknown(self):
        raw = {"production": ["production={ equipments={ equipment={ id={id=9 type=70} amount=3 } } "
                              "military_lines={ equipment_variant_index={id=9 type=70} queued_factories=26 requested_factories=26 } "
                              "military_lines={ equipment_variant_index={id=9 type=70} active_factories=4 } }"]}
        definitions = {9: dict(id=9, definition="chassis", name="v", creator="USA")}
        catalog = {"chassis": dict(domain="armor", family="medium_tank_chassis", role=None)}
        result, _ = ex._country("USA", raw, definitions, catalog, {}, {})
        self.assertEqual(result["equipment"]["families"]["medium_tank_chassis"]["active_factories"], 4)
        self.assertEqual(result["equipment"]["variants"][0]["active_factories"], 4)
        self.assertIsNone(result["equipment"]["variants"][0]["production_lines"][0]["active_factories"])  # raw line kept as recorded
        self.assertEqual(result["equipment"]["variants"][0]["production_lines"][0]["queued_factories"], 26)
        self.assertIsNone(result["equipment"]["variants"][0]["production_lines"][0]["damaged_factories"])

    def test_conscription_law_comes_from_the_mobilization_ladder(self):
        ladder = ex.conscription_ladder(str(ex.REPO_FOR_LADDER))
        self.assertEqual(ladder[:3], ("disarmed_nation", "volunteer_only", "limited_conscription"))
        raw = {"politics": ["politics={ ideas={ over_mobilisation service_by_requirement mandatory_army_service } ruling_party=fascism }"]}
        result, _ = ex._country("GER", raw, {}, {}, {}, {})
        self.assertEqual(result["conscription_law"], "service_by_requirement")
        none, _ = ex._country("GER", {"politics": ["politics={ ideas={ over_mobilisation } }"]}, {}, {}, {}, {})
        self.assertIsNone(none["conscription_law"])
        pool = ex._state_pool(["\tmanpower_pool={\n", "\t\tavailable=53353\n", "\t\tlocked=3002102\n", "\t\ttotal=3524214\n", "\t}\n", "\tresources={\n"])
        self.assertEqual(pool, {"available": 53353.0, "locked": 3002102.0, "total": 3524214.0})
        self.assertEqual(ex._state_pool(["\towner=\"GER\"\n"]), {})

        result, _ = ex._country("GER", {}, {}, {}, {}, {})
        for key in ("mobilised_share", "divisions", "army_manpower", "ships", "aircraft_stock", "stability"):
            self.assertIsNone(result["metrics"][key], key)

    def test_displayed_stability_is_rebuilt_from_base_and_terms(self):
        catalog = dict(ideas={"spirit": {"stability_factor": 0.1, "war_support_factor": 0.05}, "law": {"stability_factor": -0.1}},
                       traits={"figurehead": {"stability_factor": 0.15}, "iron": {"war_support_factor": 0.05}, "censor": {"war_support_factor": 0.1}},
                       dynamic={"faction": ["political_power_gain", "stability_factor"]},
                       static={"pride_of_the_fleet_country": {"war_support_factor": 0.05}, "pride_of_the_fleet_sunk_temporary": {"war_support_factor": -0.1},
                               "war_support_during_war": {"stability_factor": -0.3}},
                       defines=dict(ex._NCOUNTRY_DEFAULTS, WAR_SUPPORT_TENSION_IMPACT=0.0))
        characters = dict(characters={7: dict(token="leader_x", leaders={"conservatism": ["iron"], "despotism": ["figurehead"]}, advisor_traits=["censor"]),
                                      9: dict(token="minister", leaders={}, advisor_traits=["censor", "figurehead"]),
                                      11: dict(token="idle", leaders={}, advisor_traits=["censor"])})
        raw = {"scalars": ["stability=0.3\n", "war_support=0.4\n", "coastal_protection_ratio=0.5\n", "being_bombed_support_penalty=-0.1\n",
                           "pride_of_the_fleet={ id=108 type=51 }\n", 'pride_of_the_fleet_date_lost="1.1.1.1"\n'],
               "politics": ["politics={ parties={ democratic={ popularity=80 country_leader={ { ideology=conservatism character={ id=7 type=73 } } { ideology=despotism character={ id=8 type=73 } } } } fascism={ popularity=20 } } ideas={ spirit unknown } ruling_party=democratic }"],
               "characters": ["characters={ character_status={ character={ id=11 type=73 } advisor=yes } appointed_advisors={ { slot=\"interior_minister\" character={ id=7 type=73 } } { slot=\"political_advisor\" character={ id=9 type=73 } } } }"],
               "dynamic_modifier": ['dynamic_modifier={ modifier={ modifier="faction" value={ 0.2 0.05 } enabled=yes } modifier={ modifier="off" value={ 1 } enabled=no } }'],
               "diplomacy": ["diplomacy={active_relations={GER={war_relation={first=ENG second=GER start_date=1939.9.1.3 first_casualties=5 second_casualties=7 first_was_instigator=no}}}}"]}
        result, wars = ex._country("ENG", raw, {}, {}, {}, {}, catalog)
        self.assertEqual(result["metrics"]["stability_base"], 0.3)
        self.assertEqual(result["metrics"]["stability"], 0.3)  # not final before the wars are attached
        self.assertAlmostEqual(result["politics"]["modifiers"]["stability_factor"], 0.15)  # spirit 0.1 + dynamic 0.05
        self.assertEqual(result["politics"]["_leader"], ["conservatism", 7])
        self.assertEqual(result["politics"]["_hired"], [7, 9])
        self.assertIs(wars[0]["first_was_instigator"], False)
        result["wars"].append(dict(enemy="GER", offensive=False))
        ex._finalize_politics(result, catalog, characters, "1941.8.1.2")
        # The leader counts once (leader traits only, even when appointed), the appointed minister counts, an unappointed advisor does not.
        self.assertEqual([s[0] for s in result["politics"]["sources"]], ["spirit", "dynamic:faction", "leader:leader_x", "advisor:minister", "static:pride_of_the_fleet_country"])
        ws = result["politics"]["war_support_terms"]
        self.assertEqual(result["politics"]["war_posture"], "defensive")
        self.assertEqual((ws["offensive_war"], ws["defensive_war"]), (0.0, 0.2))
        expected_ws = 0.4 + 0.05 + 0.05 + 0.1 + 0.05 + 0.2 - 0.1  # spirit + leader + minister + pride + defensive - bombing
        self.assertAlmostEqual(result["metrics"]["war_support"], expected_ws)
        terms = result["politics"]["stability_terms"]
        self.assertAlmostEqual(terms["party_popularity"], 0.12)
        self.assertAlmostEqual(terms["coastal_protection"], 0.5)
        self.assertAlmostEqual(terms["war_support"], -0.3 * (1 - expected_ws))
        self.assertAlmostEqual(terms["at_war"], -0.2)  # at war, no offensive or defensive factor held
        self.assertAlmostEqual(result["metrics"]["stability"], min(1.0, 0.3 + 0.15 + 0.15 + 0.12 + 0.5 - 0.2 - 0.3 * (1 - expected_ws)))
        self.assertNotIn("_hired", result["politics"])
        # Offensive plus defensive wars: both war-support terms apply; the defensive stability bonus applies.
        catalog["ideas"]["spirit"].update(offensive_war_stability_factor=0.2, defensive_war_stability_factor=0.15)
        result, _ = ex._country("ENG", raw, {}, {}, {}, {}, catalog)
        result["wars"] += [dict(enemy="GER", offensive=False), dict(enemy="FRC", offensive=True)]
        ex._finalize_politics(result, catalog, characters, "1941.8.1.2")
        self.assertEqual(result["politics"]["war_posture"], "both")
        self.assertEqual((result["politics"]["war_support_terms"]["offensive_war"], result["politics"]["war_support_terms"]["defensive_war"]), (-0.2, 0.2))
        self.assertAlmostEqual(result["politics"]["stability_terms"]["at_war"], -0.2 + 0.2 + 0.15)  # both factors apply with both postures
        catalog["ideas"]["spirit"]["party_popularity_stability_factor"] = 0.2
        result, _ = ex._country("ENG", raw, {}, {}, {}, {}, catalog)
        ex._finalize_politics(result, catalog, characters, "1941.8.1.2")
        self.assertAlmostEqual(result["politics"]["stability_terms"]["party_popularity"], (0.15 + 0.2) * 0.8)
        # A pride of the fleet lost within 30 days carries the temporary penalty instead of the bonus.
        raw["scalars"][-1] = 'pride_of_the_fleet_date_lost="1941.7.20.1"\n'
        result, _ = ex._country("ENG", raw, {}, {}, {}, {}, catalog)
        ex._finalize_politics(result, catalog, characters, "1941.8.1.2")
        self.assertIn("static:pride_of_the_fleet_sunk_temporary", [s[0] for s in result["politics"]["sources"]])
        # A faction manifest scales with a progress ratio: rebuilt from state owners/controllers and history cores
        # when its collections are reproduced, otherwise reported only when both bounds agree.
        catalog["manifests"] = {"faction_manifest_conquest_of_territory": dict(scale={"offensive_war_stability_factor": 0.15}, fulfilled={}, range_max=1.0, fulfilled_min=0.75),
                                "unknown_manifest": dict(scale={"offensive_war_stability_factor": 0.15}, fulfilled={}, range_max=1.0, fulfilled_min=0.75)}
        catalog["state_cores"] = {1: {"ENG"}, 2: {"ENG"}, 3: {"FRA"}, 4: {"FRA"}}
        raw["scalars"][-1] = 'pride_of_the_fleet_date_lost="1.1.1.1"\n'
        raw["scalars"][0] = "stability=0.0\n"  # keep the sum below the cap so the two bounds differ
        context = dict(characters, states={1: ("ENG", "ENG"), 2: ("ENG", "ENG"), 3: ("FRA", "ENG"), 4: ("FRA", "FRA")},
                       factions={"ENG": dict(manifest="faction_manifest_conquest_of_territory", members=["ENG"], leader="ENG")})
        result, _ = ex._country("ENG", raw, {}, {}, {}, {}, catalog)
        result["tag"] = "ENG"
        result["wars"] += [dict(enemy="FRC", offensive=True)]
        ex._finalize_politics(result, catalog, context, "1941.8.1.2")
        self.assertAlmostEqual(result["politics"]["manifest_ratio"], 0.5)  # 1 controlled non-core state / 2 owned core states
        self.assertAlmostEqual(result["politics"]["stability_terms"]["at_war"], -0.2 + 0.2 + 0.15 * 0.5)
        self.assertIsNotNone(result["metrics"]["stability"])
        context["factions"]["ENG"] = dict(manifest="unknown_manifest", members=["ENG"], leader="ENG")
        result, _ = ex._country("ENG", raw, {}, {}, {}, {}, catalog)
        result["tag"] = "ENG"
        result["wars"] += [dict(enemy="FRC", offensive=True)]
        ex._finalize_politics(result, catalog, context, "1941.8.1.2")
        self.assertIsNone(result["metrics"]["stability"])
        lo, hi = result["politics"]["manifest_bounds"]["stability"]
        self.assertGreater(hi, lo)
        self.assertTrue(any("manifest progress" in issue for issue in result["issues"]))
        self.assertIsNotNone(result["metrics"]["war_support"])  # the manifest carries no war-support term
        # A country without a politics block has no popularity: the displayed value stays unknown, never a guess.
        bare, _ = ex._country("GER", {"scalars": ["stability=1\n"]}, {}, {}, {}, {})
        ex._finalize_politics(bare, ex._EMPTY_POLITICS)
        self.assertIsNone(bare["metrics"]["stability"])
        self.assertEqual(bare["metrics"]["stability_base"], 1)
        self.assertTrue(any("party_popularity" in issue for issue in bare["issues"]))

    def test_stock_shortfalls_do_not_cancel_other_variants_surpluses(self):
        raw = {"production": ["production={equipments={equipment={id={id=1} amount=-12} equipment={id={id=2} amount=20}}}"]}
        definitions = {i: dict(id=i, definition="chassis", name=str(i), creator="GER") for i in (1, 2)}
        catalog = {"chassis": dict(domain="armor", family="medium_tank_chassis")}
        result, _ = ex._country("GER", raw, definitions, catalog, {}, {})
        family = result["equipment"]["families"]["medium_tank_chassis"]
        self.assertEqual(family["stock"], 8)
        self.assertEqual(family["stock_deficit"], 12)
        self.assertIsNone(family["deficit"])

    def test_missing_division_manpower_is_not_silently_dropped(self):
        result, _ = ex._country("GER", {"units": ["units={division={division_template_id={id=1}}}"]}, {}, {}, {}, {})
        self.assertEqual(result["metrics"]["divisions"], 1)
        self.assertIsNone(result["metrics"]["army_manpower"])
        self.assertIsNone(result["army"]["templates"][0]["manpower"])
        self.assertTrue(result["issues"])

    def test_aircraft_in_wings_attach_to_airframe_families(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wings.hoi4"
            path.write_text('HOI4txt\ndate="1941.8.1.2"\nequipments={\n\tsmall_fighter_airframe={\n\t\tid={ id=7 type=70 }\n\t\tname="Spitfire"\n\t\tcreator="ENG"\n\t}\n\tinfantry_equipment={\n\t\tid={ id=8 type=70 }\n\t\tname="Rifle"\n\t\tcreator="ENG"\n\t}\n}\n'
                            'countries={\n\tENG={\n\t\tstability=0.5\n\t\tproduction={\n\t\t\tequipments={\n\t\t\t\tequipment={ id={ id=7 type=70 } amount=40 }\n\t\t\t}\n\t\t}\n\t}\n}\n'
                            'strategic_air={\n\tENG={\n\t\tair_wing_pool={\n\t\t\tdefinition=fighter_multirole\n\t\t\tair_wings={\n\t\t\t\tcount=100\n\t\t\t\tequipment={\n\t\t\t\t\tequipment={ id={ id=7 type=70 } amount=100 }\n\t\t\t\t\tequipment={ id={ id=8 type=70 } amount=0 }\n\t\t\t\t\tequipment={ id={ id=9 type=70 } amount=3 }\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}\n}\n', encoding="utf-8")
            catalog = {"small_fighter_airframe": dict(domain="air", family="small_fighter_airframe", role="fighter"),
                       "infantry_equipment": dict(domain="army", family="infantry_equipment", role=None)}
            with patch.object(ex, "equipment_catalog", return_value=catalog), patch.object(ex, "battalion_catalog", return_value={}), \
                    patch.object(ex, "politics_catalog", return_value=ex._EMPTY_POLITICS):
                data = ex.extract_save(path, Path(directory))
            country = data["countries"]["ENG"]
            family = country["equipment"]["families"]["small_fighter_airframe"]
            self.assertEqual((family["domain"], family["role"], family["stock"], family["deployed"]), ("air", "fighter", 40, 100))
            self.assertEqual(country["air"]["wings_by_role"], {"fighter": 100})
            self.assertEqual([v["deployed"] for v in country["equipment"]["variants"] if v["id"] == 7], [100])
            self.assertTrue(any("Wing equipment #9" in issue for issue in country["issues"]))  # unregistered variant reported, not dropped

    def test_missing_global_sections_keep_global_counts_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.hoi4"
            path.write_text('HOI4txt\ndate="1936.1.1.12"\ncountries={\n\tGER={\n\t\tstability=1\n\t}\n}\n', encoding="utf-8")
            with patch.object(ex, "equipment_catalog", return_value={}), patch.object(ex, "battalion_catalog", return_value={}):
                data = ex.extract_save(path, Path(directory))
            for metric in ("aircraft", "civilian_factories", "military_factories", "dockyards"):
                self.assertIsNone(data["countries"]["GER"]["metrics"][metric])
            self.assertTrue(any("states section is missing" in warning for warning in data["warnings"]))


@unittest.skipUnless(os.environ.get("WA_REPORT_REAL_SAVES") == "1", "local campaign parity is opt-in")
class CampaignParityTests(unittest.TestCase):
    def test_beginning_middle_end_against_existing_readers(self):
        import losses
        import stock
        repo = Path(__file__).resolve().parents[2]
        for name in ("1936.2_Feb.hoi4", "1943.6_Jun.hoi4", "1947.1_Jan.hoi4"):
            with self.subTest(save=name):
                path = Path(ex.sg.resolve(name))
                started = time.perf_counter()
                data = ex.extract_save(path, repo)
                print(f"\n{data['date']}: extraction {time.perf_counter()-started:.2f}s; {len(data['countries'])} countries", flush=True)
                if name == "1943.6_Jun.hoi4":
                    output = repo / ".cache/campaign_report/sample_snapshot.json"
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False), encoding="utf-8")
                with ex.sg.open_save(str(path)) as fh:
                    wars, context = losses.scan(fh)
                totals, _ = losses.tally(wars)
                for tag in ("GER", "ENG", "SOV"):
                    country = data["countries"][tag]
                    with ex.sg.open_save(str(path)) as fh:
                        sections = ex.sg.collect_sections(fh, tag, ("units", "resources", "production"))
                    self.assertEqual(country["metrics"]["divisions"], context[tag][0] if "units" in sections else None)
                    self.assertAlmostEqual(country["metrics"]["mobilised_share"] * 1e7, context[tag][1], places=3)  # losses.py mp_pool = manpower.ratio
                    # The older reader supplies zero for omitted casualty fields.
                    # New extraction intentionally keeps omitted fields unknown.
                    if country["metrics"]["losses"] is not None:
                        self.assertEqual(country["metrics"]["losses"], totals.get(tag, {}).get("lost", 0))
                    # Scope the legacy scanner to production. Its whole-country
                    # wrapper also includes division and recruitment inventories.
                    holdings, _ = stock._scan_country_body(sections.get("production", []), tag)
                    for variant in country["equipment"]["variants"]:
                        self.assertEqual(variant["stock"], holdings.get(variant["id"], 0) if "production" in sections else None)
                    ships = sum(sum(tf["ships"].values()) for f in ex.sg._parse_fleets(sections["units"]) for tf in f["tfs"]) if "units" in sections else None
                    self.assertEqual(country["metrics"]["ships"], ships)
                    flat, uses = ex.sg._parse_resources(sections.get("resources", []))
                    for resource, value in flat.get("produced", {}).items():
                        self.assertEqual(country["resources"][resource]["produced"], value)
                _, wings = ex.airload.parse_wings(str(path))
                self.assertEqual(sum(c["metrics"]["aircraft"] for c in data["countries"].values()), sum(w["count"] for w in wings))
                buildings = {"owned": Counter(), "controlled": Counter()}
                with ex.sg.open_save(str(path)) as fh:
                    for _, lines in ex.sg.iter_state_blocks(fh):
                        values, owner, controller = ex.sg._state_buildings(lines)
                        if owner == "GER":
                            buildings["owned"].update(values)
                        if controller == "GER":
                            buildings["controlled"].update(values)
                self.assertEqual(data["countries"]["GER"]["buildings"], {k: dict(v) for k, v in buildings.items()})


if __name__ == "__main__":
    unittest.main()
