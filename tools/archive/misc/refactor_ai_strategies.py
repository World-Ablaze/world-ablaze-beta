#!/usr/bin/env python3
"""
AI Strategy Refactoring Script for World Ablaze
Works against the committed state on AI-generic-template-system branch.

Performs: bug fixes, strategy moves, deduplication, consolidation, and renaming.
"""

import os
import re
import sys

BASE = r"E:\Projets\HOI4\WA\world-ablaze-beta\common\ai_strategy"

def read_file(name):
    path = os.path.join(BASE, name)
    with open(path, 'r', encoding='utf-8-sig') as f:
        return f.read()

def write_file(name, content):
    path = os.path.join(BASE, name)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

def find_and_extract(lines, name):
    """Find strategy by name at top level (no leading whitespace), return (text, start_0based, end_0based) or None."""
    for i, line in enumerate(lines):
        # Match strategy definition at column 0
        if re.match(r'^' + re.escape(name) + r'\s*=\s*\{', line):
            depth = 0
            for j in range(i, len(lines)):
                depth += lines[j].count('{') - lines[j].count('}')
                if depth == 0:
                    text = '\n'.join(lines[i:j+1])
                    return (text, i, j)
            break
    return None

def remove_strategy(lines, name):
    """Remove a strategy block by name. Returns new lines list."""
    result = find_and_extract(lines, name)
    if result:
        text, start, end = result
        new_lines = lines[:start]
        rest_start = end + 1
        # Skip trailing blank lines (keep at most one)
        blank_count = 0
        while rest_start < len(lines) and lines[rest_start].strip() == '':
            rest_start += 1
            blank_count += 1
        new_lines.append('')  # Keep one separator
        new_lines.extend(lines[rest_start:])
        return new_lines
    else:
        print(f"  WARNING: Could not find '{name}' to remove!")
        return lines

def add_prefix_to_lines(lines, file_label):
    """Add WA_AI_MILITARY_ prefix to top-level strategy definitions that don't have it.
    Skips strategies already starting with WA_AI_MIL_ or WA_AI_MILITARY_."""
    renames = {}
    for i, line in enumerate(lines):
        match = re.match(r'^([A-Za-z]\w*)\s*=\s*\{', line)
        if match:
            name = match.group(1)
            if not name.startswith('WA_AI_MIL'):  # covers both WA_AI_MIL_ and WA_AI_MILITARY_
                new_name = 'WA_AI_MILITARY_' + name
                renames[name] = new_name

    if renames:
        text = '\n'.join(lines)
        for old_name, new_name in sorted(renames.items(), key=lambda x: -len(x[0])):
            text = re.sub(r'^' + re.escape(old_name) + r'(\s*=\s*\{)', new_name + r'\1', text, flags=re.MULTILINE)
        lines = text.split('\n')
        for old_name, new_name in renames.items():
            print(f"  [{file_label}] {old_name} -> {new_name}")

    return lines

def add_prefix_to_text(text, file_label):
    lines = text.split('\n')
    lines = add_prefix_to_lines(lines, file_label)
    return '\n'.join(lines)

def clean_blanks(lines):
    """Reduce 3+ consecutive blank lines to 2, ensure trailing newline."""
    result = []
    blank_count = 0
    for line in lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    while result and result[-1].strip() == '':
        result.pop()
    result.append('')
    return result


# ============================================================================
print("=" * 60)
print("Starting AI Strategy Refactoring")
print("=" * 60)

# Load all files into line arrays
ger = read_file("WA_AI_MILITARY_COUNTRY_GER.txt").split('\n')
jap = read_file("WA_AI_MILITARY_COUNTRY_JAP.txt").split('\n')
raj = read_file("WA_AI_MILITARY_COUNTRY_RAJ.txt").split('\n')
allies = read_file("WA_AI_MILITARY_COUNTRY_ALLIES.txt").split('\n')
usa = read_file("WA_AI_MILITARY_COUNTRY_USA.txt").split('\n')
chi = read_file("WA_AI_MILITARY_COUNTRY_CHI.txt").split('\n')
rom = read_file("WA_AI_MILITARY_COUNTRY_ROM.txt").split('\n')
nzl = read_file("WA_AI_MILITARY_COUNTRY_NZL.txt").split('\n')
man = read_file("WA_AI_MILITARY_COUNTRY_MAN.txt").split('\n')
ast = read_file("WA_AI_MILITARY_COUNTRY_AST.txt").split('\n')
eng = read_file("WA_AI_MILITARY_COUNTRY_ENG.txt").split('\n')
axis = read_file("WA_AI_MILITARY_COUNTRY_AXIS.txt").split('\n')

# ============================================================================
# PHASE 1: BUG FIXES
# ============================================================================
print("\n--- Phase 1: Bug Fixes ---")

# 1.1 Rename duplicate GER_frontline_requests_5 at line 1319
print("1.1 Renaming duplicate GER_frontline_requests_5 -> GER_frontline_requests_6")
assert ger[1318].startswith('GER_frontline_requests_5'), f"Line 1319: {ger[1318]}"
ger[1318] = ger[1318].replace('GER_frontline_requests_5', 'GER_frontline_requests_6')

# 1.2 Remove dead RAJ_help_in_africa_1 (lines 228-302)
print("1.2 Removing dead RAJ_help_in_africa_1")
assert 'RAJ_help_in_africa_1' in raj[227], f"Line 228: {raj[227]}"
raj = raj[:226] + raj[302:]  # Remove lines 227-302 (0-based 226..301), also eat blank line before

# 1.3 Fix is_fully_controlled_by = controller -> ROOT in JAP.txt
print("1.3 Fixing is_fully_controlled_by = controller -> ROOT in JAP.txt")
for line_1based in [169, 178, 203, 212, 229]:
    idx = line_1based - 1
    assert 'is_fully_controlled_by = controller' in jap[idx], f"Line {line_1based}: {jap[idx]}"
    jap[idx] = jap[idx].replace('is_fully_controlled_by = controller', 'is_fully_controlled_by = ROOT')

# 1.4 Remove duplicate state 614 block at JAP.txt lines 194-201
print("1.4 Removing duplicate state 614 block")
assert '614' in jap[193], f"Line 194: {jap[193]}"
jap = jap[:193] + jap[201:]

# 1.5 Remove 2 of 3 duplicate invade RIT entries in ENG minor_allies_dont_invade
# The 3 RIT entries are at ENG lines 2596, 2626, 2641 — keep first (2596), remove 2626 and 2641
print("1.5 Removing duplicate RIT invade entries from ENG minor_allies_dont_invade")
# Work backwards to keep indices valid
# Line 2639-2643: the block around line 2641
assert '"RIT"' in eng[2640], f"Line 2641: {eng[2640]}"
# Remove lines 2639-2643 (the ai_strategy block: 2639=\tai_strategy = {, 2640=\t\ttype = invade, 2641=\t\tid = "RIT", 2642=\t\tvalue = -2000, 2643=\t})
# Actually, looking at the format - each entry is 4 lines:
# \tai_strategy = {\n\t\ttype = invade\n\t\tid = "RIT"\n\t\tvalue = -2000\n\t}
# Lines 2639-2643 (0-based 2638-2642)
eng = eng[:2638] + eng[2643:]
# Now remove the second duplicate (was at line 2624-2628, but shifted by 5)
# After removal above, the block at original 2624 is now at 2624-5=2619 offset...
# Actually let me just re-find and remove by looking for second RIT
rit_count = 0
remove_start = None
for i in range(len(eng)):
    if '"RIT"' in eng[i] and 'invade' in eng[i-1]:
        rit_count += 1
        if rit_count == 2:
            # Find the start of this ai_strategy block (go back to find "ai_strategy = {")
            for k in range(i, i-5, -1):
                if 'ai_strategy' in eng[k] and '{' in eng[k]:
                    remove_start = k
                    break
            # Find end (closing })
            for k in range(i, i+5):
                if eng[k].strip() == '}':
                    eng = eng[:remove_start] + eng[k+1:]
                    break
            break

# 1.6 Add allowed blocks
print("1.6 Adding missing allowed blocks")

# 1.6a GER_dont_invade_greenland (line 2731 in GER) — add allowed = { tag = GER }
for i, line in enumerate(ger):
    if line.startswith('GER_dont_invade_greenland'):
        for j in range(i + 1, i + 5):
            if 'enable' in ger[j]:
                ger.insert(j, '\tallowed = {\n\t\ttag = GER\n\t}')
                break
        break

# 1.6b GER_ignore_invading_these_countries — add allowed = { OR = { tag = GER is_in_faction_with = GER } }
for i, line in enumerate(ger):
    if line.startswith('GER_ignore_invading_these_countries'):
        for j in range(i + 1, i + 5):
            if 'enable' in ger[j]:
                ger.insert(j, '\tallowed = {\n\t\tOR = {\n\t\t\ttag = GER\n\t\t\tis_in_faction_with = GER\n\t\t}\n\t}')
                break
        break

# 1.6c ENG_azores_fallen — add allowed = { is_in_faction_with = ENG }
for i, line in enumerate(eng):
    if line.startswith('ENG_azores_fallen'):
        for j in range(i + 1, i + 5):
            if 'enable' in eng[j]:
                eng.insert(j, '\tallowed = {\n\t\tis_in_faction_with = ENG\n\t}')
                break
        break

# 1.7 Fix typos in JAP.txt
print("1.7 Fixing typos in JAP.txt")
for i, line in enumerate(jap):
    if 'JAP_conuering_india_means_you_get_cut_up' in line:
        jap[i] = line.replace('JAP_conuering', 'JAP_conquering')
        break
for i, line in enumerate(jap):
    if 'JAP_protect_conqured_lands' in line:
        jap[i] = line.replace('JAP_protect_conqured', 'JAP_protect_conquered')
        break
for i, line in enumerate(jap):
    if 'MAN_help_in_northen_china' in line:
        jap[i] = line.replace('MAN_help_in_northen', 'MAN_help_in_northern')
        break

print("Phase 1 complete.\n")

# ============================================================================
# PHASE 2: EXTRACT STRATEGIES TO MOVE
# ============================================================================
print("--- Phase 2: Extracting strategies for moves ---")

# From GER -> AXIS
ger_to_axis_names = [
    'GER_run_fools_you_are_encircled',
    'GER_run_fools_you_are_encircled_3',
    'war_with_soviets_barbarossa',
    'war_with_soviets_barbarossa_2',
    'war_with_soviets_barbarossa_2_ai',
    'war_with_soviets_barbarossa_3',
    'war_with_soviets_barbarossa_4',
    'GER_ITA_stop_shuffling',
    'axis_minors_no_finland',
    'GER_ITA_close_up_maginot_line_after_FRA_falls',
    'hungary_stop_crowding_up_the_soviet_line',
    'hungary_help_germany',
    'romania_stop_crowding_up_the_soviet_line',
    'romania_help_germany',
    'spain_stop_crowding_up_the_soviet_line',
    'spain_help_germany',
    'bulgaria_stop_crowding_up_the_soviet_line',
    'italy_stop_crowding_up_the_soviet_line',
]

ger_extracted = {}
for name in ger_to_axis_names:
    result = find_and_extract(ger, name)
    if result:
        ger_extracted[name] = result[0]
        print(f"  GER->AXIS: '{name}' (lines {result[1]+1}-{result[2]+1})")
    else:
        print(f"  WARNING: '{name}' not found in GER!")

# From JAP -> new files
jap_sia = find_and_extract(jap, 'SIA_siams_job')
if jap_sia: print(f"  JAP->SIA: SIA_siams_job ({jap_sia[1]+1}-{jap_sia[2]+1})")

jap_man = find_and_extract(jap, 'MAN_help_in_northern_china')
if jap_man: print(f"  JAP->MAN: MAN_help_in_northern_china ({jap_man[1]+1}-{jap_man[2]+1})")

jap_rnc = find_and_extract(jap, 'RNC_protect_home')
if jap_rnc: print(f"  JAP->RNC: RNC_protect_home ({jap_rnc[1]+1}-{jap_rnc[2]+1})")

# From USA -> ALLIES
usa_minors = find_and_extract(usa, 'allied_minors_make_way')
if usa_minors: print(f"  USA->ALLIES: allied_minors_make_way ({usa_minors[1]+1}-{usa_minors[2]+1})")

# From CHI -> ALLIES
chi_no_help = find_and_extract(chi, 'DEFAULT_no_one_helps_china')
if chi_no_help: print(f"  CHI->ALLIES: DEFAULT_no_one_helps_china ({chi_no_help[1]+1}-{chi_no_help[2]+1})")

# From ENG -> ALLIES (multi-country strategies)
eng_to_allies_names = [
    'ENG_azores_fallen',
    'minor_allies_dont_invade',
    'stay_in_west_europe',
    'stay_in_east_europe',
]

eng_extracted = {}
for name in eng_to_allies_names:
    result = find_and_extract(eng, name)
    if result:
        eng_extracted[name] = result[0]
        print(f"  ENG->ALLIES: '{name}' ({result[1]+1}-{result[2]+1})")

print("Phase 2 complete.\n")

# ============================================================================
# PHASE 3: REMOVE FROM SOURCE FILES
# ============================================================================
print("--- Phase 3: Removing from source files ---")

for name in ger_to_axis_names:
    ger = remove_strategy(ger, name)
    print(f"  Removed '{name}' from GER")

for name in ['SIA_siams_job', 'MAN_help_in_northern_china', 'RNC_protect_home']:
    jap = remove_strategy(jap, name)
    print(f"  Removed '{name}' from JAP")

usa = remove_strategy(usa, 'allied_minors_make_way')
print("  Removed 'allied_minors_make_way' from USA")

chi = remove_strategy(chi, 'DEFAULT_no_one_helps_china')
print("  Removed 'DEFAULT_no_one_helps_china' from CHI")

for name in eng_to_allies_names:
    eng = remove_strategy(eng, name)
    print(f"  Removed '{name}' from ENG")

# Remove defend_home duplications
rom = remove_strategy(rom, 'ROM_defend_home')
print("  Removed ROM_defend_home")
nzl = remove_strategy(nzl, 'NZL_defend_home')
print("  Removed NZL_defend_home")
man = remove_strategy(man, 'MAN_defend_home')
print("  Removed MAN_defend_home")
ast = remove_strategy(ast, 'AST_defend_home')
print("  Removed AST_defend_home")

# RIT - clear to header only
rit_lines = ['############################################################################################################',
             '# WA Military V2 - RIT Division Placement Rules',
             '############################################################################################################', '']
print("  Cleared RIT (header only)")

# POR - clear to header only
por_lines = ['############################################################################################################',
             '# WA Military V2 - POR Division Placement Rules',
             '############################################################################################################', '']
print("  Cleared POR (header only)")

# Remove USA_abandon_turkey
usa = remove_strategy(usa, 'USA_abandon_turkey')
print("  Removed USA_abandon_turkey")

# Remove RAJ invisible Africa values (-20/-40) from raj_unit_distribution
print("  Removing RAJ invisible Africa values")
raj_text = '\n'.join(raj)
# Pattern: tab + ai_strategy block with area = north_africa/south_africa/central_africa and value = -20 or -40
# These have blank lines in them, so use multiline
raj_text = re.sub(r'\n\t\n\tai_strategy = \{\n\t\ttype = front_unit_request\n\t\n\t\tarea = north_africa\n\t\tvalue = -20\n\t\}', '', raj_text)
raj_text = re.sub(r'\n\t\n\tai_strategy = \{\n\t\ttype = front_unit_request\n\t\n\t\tarea = south_africa\n\t\tvalue = -40\n\t\}', '', raj_text)
raj_text = re.sub(r'\n\t\n\tai_strategy = \{\n\t\ttype = front_unit_request\n\t\n\t\tarea = central_africa\n\t\tvalue = -40\n\t\}', '', raj_text)
raj = raj_text.split('\n')

print("Phase 3 complete.\n")

# ============================================================================
# PHASE 3b: CONSOLIDATE USA_europe_first + USA_bad_torpedos_suck
# ============================================================================
print("--- Phase 3b: Consolidating USA strategies ---")

consolidated = '''USA_europe_first = {
\tallowed = {
\t\toriginal_tag = USA
\t}
\tenable = {
\t\tdate < 1943.6.1
\t\tOR = {
\t\t\thas_war_with = JAP
\t\t\tthreat > 0.70
\t\t\tis_in_faction_with = ENG
\t\t}
\t}

\tabort_when_not_enabled = yes

\tai_strategy = {
\t\ttype = dont_defend_ally_borders
\t\tid = "INS"
\t\tvalue = 1000
\t}

\tai_strategy = {
\t\ttype = dont_defend_ally_borders
\t\tid = "AST"
\t\tvalue = 1000
\t}

\tai_strategy = {
\t\ttype = area_priority
\t\tid = oceania
\t\tvalue = -2000
\t}

\tai_strategy = {
\t\ttype = area_priority
\t\tid = australia_new_zealand
\t\tvalue = -2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 177 #W N Pacific
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 88
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 96
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 84 #Bismark Sea
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 82 #Gulf of carpentaria
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 60 #W Indian Ocean
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 85 #SW Indian Ocean
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 74 #S Indian Ocean
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 99 #Far E Indian Ocean
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 67
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 79
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = invade
\t\tid = "SIA"
\t\tvalue = -2000
\t}

\tai_strategy = {
\t\ttype = invade
\t\tid = "IPP"
\t\tvalue = -2000
\t}

\tai_strategy = {
\t\ttype = invade
\t\tid = "IPM"
\t\tvalue = -2000
\t}

\tai_strategy = {
\t\ttype = invade
\t\tid = "IPI"
\t\tvalue = -2000
\t}

\tai_strategy = {
\t\ttype = invade
\t\tid = "IPS"
\t\tvalue = -2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 81
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 83
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 93
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 72
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 73
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 71
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 101
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 91
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 92
\t\tvalue = 2000
\t}

\tai_strategy = {
\t\ttype = naval_avoid_region
\t\tid = 98
\t\tvalue = 2000
\t}
}'''

usa = remove_strategy(usa, 'USA_bad_torpedos_suck')
usa = remove_strategy(usa, 'USA_europe_first')

# Insert consolidated where USA_europe_first was (before USA_protect_the_philippines)
insert_idx = None
for i, line in enumerate(usa):
    if line.startswith('USA_protect_the_philippines'):
        insert_idx = i
        break

if insert_idx:
    usa = usa[:insert_idx] + consolidated.split('\n') + [''] + usa[insert_idx:]
    print("  Consolidated USA_europe_first + USA_bad_torpedos_suck")
else:
    print("  WARNING: Could not find insertion point!")

print("Phase 3b complete.\n")

# ============================================================================
# PHASE 4: APPEND TO DESTINATION FILES
# ============================================================================
print("--- Phase 4: Appending to destinations ---")

# AXIS.txt
while axis and axis[-1].strip() == '':
    axis.pop()
axis.append('')
axis.append('############################################################################################################')
axis.append('# Moved from GER.txt - Multi-nation Axis strategies')
axis.append('############################################################################################################')
for name in ger_to_axis_names:
    if name in ger_extracted:
        axis.append('')
        axis.extend(ger_extracted[name].split('\n'))
print("  Appended to AXIS.txt")

# ALLIES.txt
while allies and allies[-1].strip() == '':
    allies.pop()
allies.append('')
allies.append('############################################################################################################')
allies.append('# Moved from ENG.txt - Multi-nation Allied strategies')
allies.append('############################################################################################################')
for name in eng_to_allies_names:
    if name in eng_extracted:
        allies.append('')
        allies.extend(eng_extracted[name].split('\n'))

allies.append('')
allies.append('############################################################################################################')
allies.append('# Moved from other country files - Multi-nation Allied strategies')
allies.append('############################################################################################################')
if usa_minors:
    allies.append('')
    allies.extend(usa_minors[0].split('\n'))
if chi_no_help:
    allies.append('')
    allies.extend(chi_no_help[0].split('\n'))
print("  Appended to ALLIES.txt")

# MAN.txt
while man and man[-1].strip() == '':
    man.pop()
if jap_man:
    man.append('')
    man.extend(jap_man[0].split('\n'))
print("  Appended MAN_help_in_northern_china to MAN.txt")

# Create SIA.txt
sia_content = '############################################################################################################\n'
sia_content += '# WA Military V2 - Siam Specific Allocation Rules\n'
sia_content += '############################################################################################################\n\n'
if jap_sia:
    sia_content += jap_sia[0] + '\n'
print("  Created SIA.txt")

# Create RNC.txt
rnc_content = '############################################################################################################\n'
rnc_content += '# WA Military V2 - Reformed Nanjing China Specific Allocation Rules\n'
rnc_content += '############################################################################################################\n\n'
if jap_rnc:
    rnc_content += jap_rnc[0] + '\n'
print("  Created RNC.txt")

print("Phase 4 complete.\n")

# ============================================================================
# PHASE 5: RENAME with WA_AI_MILITARY_ prefix
# ============================================================================
print("--- Phase 5: Renaming ---")

ger = add_prefix_to_lines(ger, "GER")
jap = add_prefix_to_lines(jap, "JAP")
raj = add_prefix_to_lines(raj, "RAJ")
usa = add_prefix_to_lines(usa, "USA")
rom = add_prefix_to_lines(rom, "ROM")
nzl = add_prefix_to_lines(nzl, "NZL")
man = add_prefix_to_lines(man, "MAN")
ast = add_prefix_to_lines(ast, "AST")
chi = add_prefix_to_lines(chi, "CHI")
eng = add_prefix_to_lines(eng, "ENG")
axis = add_prefix_to_lines(axis, "AXIS")
allies = add_prefix_to_lines(allies, "ALLIES")

sia_content = add_prefix_to_text(sia_content, "SIA")
rnc_content = add_prefix_to_text(rnc_content, "RNC")

print("Phase 5 complete.\n")

# ============================================================================
# PHASE 6: WRITE FILES
# ============================================================================
print("--- Phase 6: Writing files ---")

for name, lines in [
    ("WA_AI_MILITARY_COUNTRY_GER.txt", ger),
    ("WA_AI_MILITARY_COUNTRY_JAP.txt", jap),
    ("WA_AI_MILITARY_COUNTRY_RAJ.txt", raj),
    ("WA_AI_MILITARY_COUNTRY_ALLIES.txt", allies),
    ("WA_AI_MILITARY_COUNTRY_USA.txt", usa),
    ("WA_AI_MILITARY_COUNTRY_CHI.txt", chi),
    ("WA_AI_MILITARY_COUNTRY_ROM.txt", rom),
    ("WA_AI_MILITARY_COUNTRY_NZL.txt", nzl),
    ("WA_AI_MILITARY_COUNTRY_MAN.txt", man),
    ("WA_AI_MILITARY_COUNTRY_AST.txt", ast),
    ("WA_AI_MILITARY_COUNTRY_ENG.txt", eng),
    ("WA_AI_MILITARY_COUNTRY_AXIS.txt", axis),
]:
    write_file(name, '\n'.join(clean_blanks(lines)))
    print(f"  Wrote {name}")

write_file("WA_AI_MILITARY_COUNTRY_RIT.txt", '\n'.join(rit_lines))
print("  Wrote RIT.txt")
write_file("WA_AI_MILITARY_COUNTRY_POR.txt", '\n'.join(por_lines))
print("  Wrote POR.txt")
write_file("WA_AI_MILITARY_COUNTRY_SIA.txt", sia_content)
print("  Wrote SIA.txt (NEW)")
write_file("WA_AI_MILITARY_COUNTRY_RNC.txt", rnc_content)
print("  Wrote RNC.txt (NEW)")

print("Phase 6 complete.\n")

# ============================================================================
# PHASE 7: VERIFICATION
# ============================================================================
print("--- Phase 7: Verification ---")

import glob
all_names = {}
errors = 0

for filepath in glob.glob(os.path.join(BASE, "WA_AI_MILITARY_*.txt")):
    fname = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    # Check for duplicate strategy names
    for match in re.finditer(r'^([A-Za-z]\w*)\s*=\s*\{', content, re.MULTILINE):
        name = match.group(1)
        if name in all_names:
            print(f"  DUPLICATE: '{name}' in {fname} AND {all_names[name]}")
            errors += 1
        else:
            all_names[name] = fname

    # Check brace balance
    opens = content.count('{')
    closes = content.count('}')
    if opens != closes:
        print(f"  BRACE MISMATCH in {fname}: {opens} opens vs {closes} closes")
        errors += 1

# Check missing prefix in COUNTRY files only
for filepath in glob.glob(os.path.join(BASE, "WA_AI_MILITARY_COUNTRY_*.txt")):
    fname = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    for match in re.finditer(r'^([A-Za-z]\w*)\s*=\s*\{', content, re.MULTILINE):
        name = match.group(1)
        if not name.startswith('WA_AI_MIL'):
            print(f"  MISSING PREFIX: '{name}' in {fname}")
            errors += 1

if errors == 0:
    print("  All checks passed!")
else:
    print(f"  {errors} error(s) found - see above")

print("\n" + "=" * 60)
print("Refactoring complete!")
print("=" * 60)
