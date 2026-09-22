"""THROWAWAY - a tier LADDER on every modern target (never commit the OUTPUT).
Experiment record: documentation/MODERN_SWITCH_BRAKE_EXPERIMENT_2026-09-21.md (section 7f, test13).

For a modern target with N modern main-gun battalions, emit N copies: tier k (1..N) mounts
(N-k) medium_armor_battalion_line + k modern_armor_battalion_line. Tier k is enabled by the
target's own flag value AND the country flag ZZ_TEST13_tier = k-1 (tier 1 also when the flag is
absent); the top tier (the original composition) is enabled at every value >= N-1. The flag is
advanced by common/scripted_effects/ZZ_THROWAWAY_test13_effects.txt (weekly, one step, when the
modern main-gun fill of the armies is above the bar).

usage: python tier_ladder_targets.py apply|check
Revert : git checkout -- common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILE = ROOT / "common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt"
MARK = "# THROWAWAY-TEST tier ladder - DO NOT COMMIT (GENERATED file)"
TIER_FLAG = "ZZ_TEST13_tier"
MAX_VALUE = 9
HEAD = re.compile(r"^\t(WA_AI_TEMPLATES_GENERIC_MODERN_ARMOR_[A-Z0-9_]+) = \{$")
ENABLE = re.compile(r"^\t\tenable = \{ (.*) \}$")
UNIT = re.compile(r"^(\t+)([a-z_]+) = (\d+)$")


def tier_term(k, n):
    if k == 1:
        return ["\t\t\tOR = {",
                "\t\t\t\tNOT = { has_country_flag = %s }" % TIER_FLAG,
                "\t\t\t\thas_country_flag = { flag = %s value = 0 }" % TIER_FLAG,
                "\t\t\t}"]
    if k < n:
        return ["\t\t\thas_country_flag = { flag = %s value = %d }" % (TIER_FLAG, k - 1)]
    out = ["\t\t\tOR = {"]
    for v in range(n - 1, MAX_VALUE + 1):
        out.append("\t\t\t\thas_country_flag = { flag = %s value = %d }" % (TIER_FLAG, v))
    out.append("\t\t\t}")
    return out


def emit(block):
    name = HEAD.match(block[0]).group(1)
    n = None
    for line in block:
        m = UNIT.match(line)
        if m and m.group(2) == "modern_armor_battalion_line":
            n = int(m.group(3))
    assert n and n >= 2, (name, n)
    out = []
    for k in range(1, n + 1):
        out.append("\t" + MARK)
        out.append("\t%s__T13_%d = {" % (name, k))
        body = []
        for line in block[1:]:
            e = ENABLE.match(line)
            if e:
                body.append("\t\tenable = {")
                body.append("\t\t\t" + e.group(1))
                body += tier_term(k, n)
                body.append("\t\t}")
                continue
            m = UNIT.match(line)
            if m and m.group(2) == "modern_armor_battalion_line":
                if n - k > 0:
                    body.append("%smedium_armor_battalion_line = %d" % (m.group(1), n - k))
                body.append("%smodern_armor_battalion_line = %d" % (m.group(1), k))
                continue
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
        out += body
        out.append("")
    return out, n


def main():
    mode = sys.argv[1]
    raw = FILE.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "BOM"
    text = raw.decode("ascii")
    assert MARK not in text and "THROWAWAY" not in text, "throwaway edit already present - git checkout the file first"
    lines = text.split("\r\n")
    out, i, targets, tiers = [], 0, 0, 0
    while i < len(lines):
        if HEAD.match(lines[i]):
            j = i
            while lines[j] != "\t}":
                j += 1
            new, n = emit(lines[i:j + 1])
            out += new
            targets += 1
            tiers += n
            i = j + 1
        else:
            out.append(lines[i])
            i += 1
    new = "\r\n".join(out)
    assert new.count("{") == new.count("}"), "brace imbalance"
    print("modern targets: %d ; tier targets emitted: %d ; lines %d -> %d" % (targets, tiers, len(lines), len(out)))
    if mode == "apply":
        FILE.write_bytes(new.encode("ascii"))
        print("written:", FILE)


main()
