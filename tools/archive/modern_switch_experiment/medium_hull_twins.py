"""THROWAWAY - medium-hull twins for EVERY modern target (never commit the OUTPUT).
Experiment record: documentation/MODERN_SWITCH_BRAKE_EXPERIMENT_2026-09-21.md (section 7b).

usage: python medium_hull_twins.py apply|check [--brake no|yes] [--ram 0.9]
  apply   : insert one twin S(M) immediately before each modern target M
  check   : report what apply would do, write nothing
  --brake : value of the twin's can_upgrade_in_field = { always = ... } (default no = closed)
  --ram   : the twin's replace_at_match (default 0.3; test7 = 0.3, test8/test9 = 0.9)
Revert : git checkout -- common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILE = ROOT / "common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt"
MARK = "# THROWAWAY-TEST medium-hull twin - DO NOT COMMIT (GENERATED file)"
SWAP = {
    "modern_armor_battalion_line": "medium_armor_battalion_line",
    "engineer_mod_tank_battalion_divisional": "engineer_med_tank_battalion_divisional",
    "maintenance_mod_tank_company_divisional": "maintenance_med_tank_company_divisional",
}
HEAD = re.compile(r"^\t(WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_[A-Z0-9_]+) = \{$")
CODE = re.compile(r"flag = WA_MEDIUM_ARMOR_TEMPLATE value = (\d+)")
UNIT = re.compile(r"^(\t+)([a-z_]+) = (\d+)$")


def twin(block, brake, ram="0.3"):
    name = HEAD.match(block[0]).group(1)
    code = CODE.search(block[1]).group(1)
    out = ["\t" + MARK,
           "\tWA_AI_TEMPLATES_THROWAWAY_TEST_MEDIUM_HULL_TWIN_%s = {" % code]
    swapped = 0
    body = []
    for line in block[1:-1]:
        if line.lstrip().startswith("can_upgrade_in_field"):
            line = "\t\tcan_upgrade_in_field = { always = %s }" % brake
        m = UNIT.match(line)
        if m and m.group(2) in SWAP:
            line = "%s%s = %s" % (m.group(1), SWAP[m.group(2)], m.group(3))
            swapped += 1
        body.append(line)
    # keep each unit list alphabetical, as the generator emits it
    i = 0
    while i < len(body):
        if UNIT.match(body[i]):
            j = i
            while j < len(body) and UNIT.match(body[j]):
                j += 1
            body[i:j] = sorted(body[i:j], key=lambda s: s.strip())
            i = j
        else:
            i += 1
    assert swapped == 3, (name, swapped)
    out += body
    out += ["\t\treplace_at_match = %s" % ram,
            "\t\treplace_with = %s" % name,
            "\t\ttarget_min_match = 0.1",
            "\t}",
            ""]
    return out


def main():
    mode = sys.argv[1]
    brake = "no"
    if "--brake" in sys.argv:
        brake = sys.argv[sys.argv.index("--brake") + 1]
    ram = "0.3"
    if "--ram" in sys.argv:
        ram = sys.argv[sys.argv.index("--ram") + 1]
    raw = FILE.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "BOM"
    text = raw.decode("ascii")
    assert MARK not in text, "twins already present - git checkout the file first"
    lines = text.split("\r\n")
    out, i, n = [], 0, 0
    while i < len(lines):
        if HEAD.match(lines[i]):
            j = i
            while lines[j] != "\t}":
                j += 1
            block = lines[i:j + 1]
            out += twin(block, brake, ram)
            out += block
            n += 1
            i = j + 1
        else:
            out.append(lines[i])
            i += 1
    new = "\r\n".join(out)
    assert new.count("{") == new.count("}"), "brace imbalance"
    print("modern targets twinned: %d ; brake always = %s ; replace_at_match = %s ; lines %d -> %d"
          % (n, brake, ram, len(lines), len(out)))
    if mode == "apply":
        FILE.write_bytes(new.encode("ascii"))
        print("written:", FILE)


main()
