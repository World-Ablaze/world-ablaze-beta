#!/usr/bin/env python3
"""Generate the modern-chassis mirror of the AI medium-armour templates.

[modern-chassis-tier] "Modern" is the last CHASSIS GENERATION of the medium weight class, not a
separate class of division. The mirror therefore has to have exactly the same shape as the medium
ladder: WA_AI_TEMPLATES_calculate_medium_armor_template picks a value V and adds a flat +500 when
the modern-chassis latch is set, so EVERY value the ladder can produce needs a twin at V+500. A
hand-maintained copy would desynchronise the first time someone edits one variant of the medium
ladder, and the failure is silent - the country carries a flag value no ai_template answers, so it
keeps its 1936 template for the rest of the campaign.

Source : common/ai_templates/WA_AI_TEMPLATES_armored_medium.txt   (hand-maintained)
Output : common/ai_templates/WA_AI_TEMPLATES_armored_medium_modern.txt   (GENERATED, do not edit)

Both files declare `role = medium_armor`. That is the shape the light-support templates already
use (WA_light_support_armor_role also declares role = light_armor); only one template is ever
enabled because the flag VALUE selects exactly one.

Usage, from tools/:
    python gen_ai_medium_modern_mirror.py --dry-run
    python gen_ai_medium_modern_mirror.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "common" / "ai_templates" / "WA_AI_TEMPLATES_armored_medium.txt"
DST = REPO / "common" / "ai_templates" / "WA_AI_TEMPLATES_armored_medium_modern.txt"

TIER_OFFSET = 500

# Every unit token the medium templates may contain, and what it becomes one chassis tier up.
# A token missing from this table is a hard error: it means the medium ladder gained a component
# whose modern-tier answer nobody has decided, and guessing it silently is how a mirror rots.
TIER_UP = {
    # medium tier -> modern tier
    "medium_armor_battalion_line": "modern_armor_battalion_line",
    "medium_assault_gun_battalion_line": "modern_assault_gun_battalion_line",
    "medium_assault_gun_company_divisional": "modern_assault_gun_company_divisional",
    # no modern_assault_gun_company_regimental exists in common/units/armor_sp_assault.txt,
    # so the regimental assault company stays at the medium tier. Checked 2026-08-28.
    "medium_assault_gun_company_regimental": "medium_assault_gun_company_regimental",
    "medium_infantry_support_armor_battalion_line": "modern_infantry_support_armor_battalion_line",
    "medium_infantry_support_company_divisional": "modern_infantry_support_company_divisional",
    "medium_self_propelled_anti_air_company_divisional": "modern_self_propelled_anti_air_company_divisional",
    "medium_self_propelled_gun_battalion_line": "modern_self_propelled_gun_battalion_line",
    "medium_self_propelled_gun_company_divisional": "modern_self_propelled_gun_company_divisional",
    "medium_self_propelled_gun_company_regimental": "modern_self_propelled_gun_company_regimental",
    "medium_tank_destroyer_battalion_line": "modern_tank_destroyer_battalion_line",
    "medium_tank_destroyer_company_divisional": "modern_tank_destroyer_company_divisional",
    "medium_tank_destroyer_company_regimental": "modern_tank_destroyer_company_regimental",
    # light tier -> medium tier
    "light_assault_gun_battalion_line": "medium_assault_gun_battalion_line",
    "light_assault_gun_company_divisional": "medium_assault_gun_company_divisional",
    "light_assault_gun_company_regimental": "medium_assault_gun_company_regimental",
    "light_infantry_support_armor_battalion_line": "medium_infantry_support_armor_battalion_line",
    "light_self_propelled_anti_air_company_divisional": "medium_self_propelled_anti_air_company_divisional",
    "light_self_propelled_gun_battalion_line": "medium_self_propelled_gun_battalion_line",
    "light_self_propelled_gun_company_divisional": "medium_self_propelled_gun_company_divisional",
    "light_self_propelled_gun_company_regimental": "medium_self_propelled_gun_company_regimental",
    # tank-chassis support companies follow the main chassis
    "engineer_med_tank_battalion_divisional": "engineer_mod_tank_battalion_divisional",
    "maintenance_med_tank_company_divisional": "maintenance_mod_tank_company_divisional",
    # deliberately unchanged: not tiered, or already at the top tier
    "anti_tank_mot_company_regimental": "anti_tank_mot_company_regimental",
    "engineer_mod_tank_battalion_divisional": "engineer_mod_tank_battalion_divisional",
    "engineer_mot_battalion_divisional": "engineer_mot_battalion_divisional",
    "field_hospital_mot_company_divisional": "field_hospital_mot_company_divisional",
    "heavy_anti_air_mot_company_divisional": "heavy_anti_air_mot_company_divisional",
    "heavy_artillery_mot_company_divisional": "heavy_artillery_mot_company_divisional",
    "infantry_heavy_mechanized_battalion_line": "infantry_heavy_mechanized_battalion_line",
    "infantry_heavy_motorized_battalion_line": "infantry_heavy_motorized_battalion_line",
    "logistics_mot_company_divisional": "logistics_mot_company_divisional",
    "maintenance_mod_tank_company_divisional": "maintenance_mod_tank_company_divisional",
    "maintenance_mot_company_divisional": "maintenance_mot_company_divisional",
    "military_police_mot_company_divisional": "military_police_mot_company_divisional",
    "modern_armor_battalion_line": "modern_armor_battalion_line",
    "modern_self_propelled_anti_air_company_divisional": "modern_self_propelled_anti_air_company_divisional",
    "modern_self_propelled_gun_battalion_line": "modern_self_propelled_gun_battalion_line",
    "modern_self_propelled_gun_company_divisional": "modern_self_propelled_gun_company_divisional",
    "modern_self_propelled_gun_company_regimental": "modern_self_propelled_gun_company_regimental",
    "modern_tank_destroyer_battalion_line": "modern_tank_destroyer_battalion_line",
    "modern_tank_destroyer_company_divisional": "modern_tank_destroyer_company_divisional",
    "modern_tank_destroyer_company_regimental": "modern_tank_destroyer_company_regimental",
    "pack_artillery_mot_company_regimental": "pack_artillery_mot_company_regimental",
    # recon stays a LIGHT tank company on purpose: it is a scout, not a fighting tier
    "recon_light_tank_company_divisional": "recon_light_tank_company_divisional",
    "recon_mot_company_divisional": "recon_mot_company_divisional",
    "signal_mot_company_divisional": "signal_mot_company_divisional",
}

# Keys that are template settings, not units, and carry a bare number.
SETTING_KEYS = {"base", "custom_icon", "reinforce_prio"}

# Icon of the modern-chassis divisions, matching what the retired modern role used.
MODERN_ICON = "109"

# Name-suffix shift, applied after GENERIC_MEDIUM_ARMOR_ -> GENERIC_MODERN_ARMOR_.
# Longest first so MEDIUM_INF_SUPPORT is not eaten by a shorter key.
NAME_SHIFT = [
    ("MEDIUM_INF_SUPPORT", "MODERN_INF_SUPPORT"),
    ("MEDIUM_ASSAULT", "MODERN_ASSAULT"),
    ("MEDIUM_SPAA", "MODERN_SPAA"),
    ("MEDIUM_SPG", "MODERN_SPG"),
    ("MEDIUM_TD", "MODERN_TD"),
    ("LIGHT_INF_SUPPORT", "MEDIUM_INF_SUPPORT"),
    ("LIGHT_ASSAULT", "MEDIUM_ASSAULT"),
    ("LIGHT_SPAA", "MEDIUM_SPAA"),
    ("LIGHT_SPG", "MEDIUM_SPG"),
    ("LIGHT_TD", "MEDIUM_TD"),
]

BLOCK_OPEN = re.compile(r"^\t(WA_AI_TEMPLATES_GENERIC_\w+) = \{$")
ENABLE = re.compile(
    r"^\t\tenable = \{ has_country_flag = \{ flag = (\w+) value = (\d+) \} \}(.*)$"
)
UNIT_LINE = re.compile(r"^(\s*)(\w+) = (\d+)\s*$")


class Block:
    def __init__(self, name: str, flag: str, value: int, lines: list[str]):
        self.name = name
        self.flag = flag
        self.value = value
        self.lines = lines


def parse(text: str) -> list[Block]:
    lines = text.split("\n")
    blocks: list[Block] = []
    i = 0
    while i < len(lines):
        m = BLOCK_OPEN.match(lines[i])
        if not m:
            i += 1
            continue
        start = i
        depth = 0
        while i < len(lines):
            depth += lines[i].count("{") - lines[i].count("}")
            i += 1
            if depth == 0:
                break
        body = lines[start:i]
        em = ENABLE.match(body[1]) if len(body) > 1 else None
        if not em:
            raise SystemExit(
                f"ERROR {SRC.name}: block {m.group(1)} has no recognisable enable line:\n  {body[1] if len(body) > 1 else '<empty>'}"
            )
        blocks.append(Block(m.group(1), em.group(1), int(em.group(2)), body))
    return blocks


def shift_name(name: str) -> str:
    if "GENERIC_MEDIUM_ARMOR_" not in name:
        raise SystemExit(f"ERROR: unexpected template name, cannot mirror: {name}")
    head, _, tail = name.partition("GENERIC_MEDIUM_ARMOR_")
    for src, dst in NAME_SHIFT:
        tail = tail.replace(src, dst)
    return f"{head}GENERIC_MODERN_ARMOR_{tail}"


def mirror(block: Block, used_names: set[str]) -> list[str]:
    out: list[str] = []
    name = shift_name(block.name)
    if name in used_names:
        # The medium ladder itself carries duplicate template names (6105/6108, 6106/6109,
        # 6107/6110 as of 2026-08-28). Never emit a duplicate here: two ai_template entries
        # with one key inside a role group means only one of them is reachable.
        name = f"{name}_{block.value + TIER_OFFSET}"
    used_names.add(name)

    for idx, line in enumerate(block.lines):
        if idx == 0:
            out.append(f"\t{name} = {{")
            continue
        em = ENABLE.match(line)
        if em:
            out.append(
                f"\t\tenable = {{ has_country_flag = {{ flag = {em.group(1)} "
                f"value = {block.value + TIER_OFFSET} }} }}{em.group(3)}"
            )
            continue
        um = UNIT_LINE.match(line)
        if um:
            indent, key, count = um.groups()
            if key in SETTING_KEYS:
                if key == "custom_icon":
                    out.append(f"{indent}custom_icon = {MODERN_ICON}")
                else:
                    out.append(line)
                continue
            if key not in TIER_UP:
                raise SystemExit(
                    f"ERROR {SRC.name}: {block.name} (value {block.value}) uses '{key}', which has "
                    f"no entry in TIER_UP. Decide its modern-tier answer in "
                    f"{Path(__file__).name} before regenerating."
                )
            out.append(f"{indent}{TIER_UP[key]} = {count}")
            continue
        out.append(line)
    return out


HEADER = """\
############################################################################################################
# GENERATED FILE - DO NOT EDIT BY HAND.
# Source    : common/ai_templates/WA_AI_TEMPLATES_armored_medium.txt
# Generator : tools/gen_ai_medium_modern_mirror.py  (run with --dry-run first)
############################################################################################################
# [modern-chassis-tier] The modern-CHASSIS tier of the MEDIUM weight class. Same role, same ladder,
# every component one tier up; values are the medium values + 500. The selector adds that offset
# when WA_AI_TEMPLATES_modern_chassis_owns_medium_role is true, so a medium value with no twin here
# leaves the country holding a flag no template answers - which is why this file is generated.
#
# `role = medium_armor` on purpose, twice in the folder: the same shape WA_light_support_armor_role
# uses for role = light_armor. Only one template is ever enabled, because the flag VALUE picks one.
############################################################################################################

WA_medium_armor_modern_role = {
\trole = medium_armor
\tfront_role_override = offence\t# Engine keys front assignment on 'role = armor' or this override
\t\t\t\t\t\t\t\t\t# (defines ASSIGN_TANKS_TO_WAR_FRONT = 6.0). WA uses its own granular role
\t\t\t\t\t\t\t\t\t# tokens, so without this line armour was distributed like infantry and
\t\t\t\t\t\t\t\t\t# every front_armor_score entry in the mod was inert.
\tupgrade_prio = {
\t\tbase = 100
\t\t# [dead-role-entry] The engine's role-entry lottery gives full weight to an entry whose
\t\t# targets are all disabled, turning it into a permanent army-XP sink. This entry's enables
\t\t# all key on modern-range (+500) values, reachable only while the modern latch is set.
\t\tmodifier = {
\t\t\tfactor = 0
\t\t\tNOT = { has_country_flag = WA_AI_TEMPLATES_modern_chassis_earned }
\t\t}
\t\tmodifier = {
\t\t\tfactor = 0
\t\t\tNOT = { has_country_flag = WA_MEDIUM_ARMOR_TEMPLATE }
\t\t}
\t}
"""


def build(blocks: list[Block]) -> str:
    medium = [b for b in blocks if b.flag == "WA_MEDIUM_ARMOR_TEMPLATE"]
    if not medium:
        raise SystemExit(f"ERROR {SRC.name}: no WA_MEDIUM_ARMOR_TEMPLATE blocks found")
    used: set[str] = set()
    out = [HEADER]
    for width, label in ((0, "20 Width"), (100, "30 Width")):
        group = [b for b in medium if width <= b.value % 1000 < width + 100]
        if not group:
            continue
        out.append("")
        out.append(f"\t######################################################################### {label}")
        out.append("")
        for b in sorted(group, key=lambda x: x.value):
            out.extend(mirror(b, used))
    out.append("}")
    out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print what would change, write nothing")
    args = ap.parse_args()

    if not SRC.exists():
        print(f"ERROR: source not found: {SRC}", file=sys.stderr)
        return 2

    blocks = parse(SRC.read_text(encoding="utf-8"))
    stale = [b for b in blocks if b.flag != "WA_MEDIUM_ARMOR_TEMPLATE"]
    if stale:
        names = ", ".join(f"{b.name}({b.flag} {b.value})" for b in stale)
        print(
            f"ERROR {SRC.name}: blocks keyed on a flag other than WA_MEDIUM_ARMOR_TEMPLATE: {names}\n"
            "       The modern role was retired 2026-08-28; the modern-chassis tier lives in this\n"
            "       generated mirror, not behind a second flag.",
            file=sys.stderr,
        )
        return 2

    new = build(blocks)
    old = DST.read_text(encoding="utf-8") if DST.exists() else ""

    if new == old:
        print(f"up to date: {DST.relative_to(REPO)} ({len(blocks)} source templates mirrored)")
        return 0

    print(f"{'would write' if args.dry_run else 'writing'}: {DST.relative_to(REPO)}")
    print(f"  source templates : {len(blocks)}")
    print(f"  value range      : {min(b.value for b in blocks) + TIER_OFFSET}"
          f"-{max(b.value for b in blocks) + TIER_OFFSET}")
    print(f"  bytes            : {len(old)} -> {len(new)}")
    if args.dry_run:
        return 0

    # BOM-free, LF: AGENTS.md editing rule 16.
    DST.write_bytes(new.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
