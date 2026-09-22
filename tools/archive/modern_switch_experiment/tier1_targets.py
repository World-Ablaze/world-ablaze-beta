"""THROWAWAY - cap every modern target at ONE modern main-gun battalion (never commit the OUTPUT).
Experiment record: documentation/MODERN_SWITCH_BRAKE_EXPERIMENT_2026-09-21.md (section 7e, test12).

usage: python tier1_targets.py apply|check [--modern 1]
  apply    : in each modern target, modern_armor_battalion_line = N becomes
             medium_armor_battalion_line = N-k + modern_armor_battalion_line = k (default k = 1)
  check    : report what apply would do, write nothing
  --modern : k, the number of modern main-gun battalions kept (tier)
Revert : git checkout -- common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILE = ROOT / "common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt"
MARK = "# THROWAWAY-TEST tier cap - DO NOT COMMIT (GENERATED file)"
HEAD = re.compile(r"^\t(WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_[A-Z0-9_]+) = \{$")
UNIT = re.compile(r"^(\t+)([a-z_]+) = (\d+)$")


def cap(block, k):
    out = [block[0], "\t\t" + MARK]
    changed = 0
    body = []
    for line in block[1:]:
        m = UNIT.match(line)
        if m and m.group(2) == "modern_armor_battalion_line" and int(m.group(3)) > k:
            n = int(m.group(3))
            body.append("%smedium_armor_battalion_line = %d" % (m.group(1), n - k))
            body.append("%smodern_armor_battalion_line = %d" % (m.group(1), k))
            changed += 1
        else:
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
    return out + body, changed


def main():
    mode = sys.argv[1]
    k = 1
    if "--modern" in sys.argv:
        k = int(sys.argv[sys.argv.index("--modern") + 1])
    raw = FILE.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "BOM"
    text = raw.decode("ascii")
    assert MARK not in text, "cap already present - git checkout the file first"
    lines = text.split("\r\n")
    out, i, n, c = [], 0, 0, 0
    while i < len(lines):
        if HEAD.match(lines[i]):
            j = i
            while lines[j] != "\t}":
                j += 1
            new, changed = cap(lines[i:j + 1], k)
            out += new
            n += 1
            c += changed
            i = j + 1
        else:
            out.append(lines[i])
            i += 1
    new = "\r\n".join(out)
    assert new.count("{") == new.count("}"), "brace imbalance"
    print("modern targets: %d ; capped at %d modern main-gun battalion(s): %d ; lines %d -> %d"
          % (n, k, c, len(lines), len(out)))
    if mode == "apply":
        FILE.write_bytes(new.encode("ascii"))
        print("written:", FILE)


main()
