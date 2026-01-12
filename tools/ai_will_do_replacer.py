#!/usr/bin/env python3
"""
AI Will Do Replacer for HOI4 World Ablaze
Replaces ai_will_do blocks in technology files with standardized triggers.

Usage:
    python ai_will_do_replacer.py <input_file> [--dry-run]
"""

import re
import sys
import argparse
from pathlib import Path
from ai_replacer_base.generator import generate_ai_will_do_block

# =============================================================================
# TECHNOLOGY TO TRIGGER MAPPINGS
# =============================================================================

INDUSTRY_TRIGGERS = {
    # Machine Tools branch
    'basic_machine_tools': ('WA_AI_RESEARCH_needs_machine_tools', None),
    'improved_machine_tools': ('WA_AI_RESEARCH_needs_machine_tools', 1937),
    'advanced_machine_tools': ('WA_AI_RESEARCH_needs_machine_tools', 1939),
    'assembly_line_production': ('WA_AI_RESEARCH_needs_machine_tools', 1941),
    'assembly_cranes': ('WA_AI_RESEARCH_needs_machine_tools', 1943),
    'flexible_line': ('WA_AI_RESEARCH_needs_machine_tools', 1945),
    'streamlined_line': (None, None),  # XOR choice, factor = 0

    # Expanded Industry branch
    'expanded_industry1': ('WA_AI_RESEARCH_needs_expanded_industry', None),
    'expanded_industry2': ('WA_AI_RESEARCH_needs_expanded_industry', 1937),
    'expanded_industry3': ('WA_AI_RESEARCH_needs_expanded_industry', 1939),
    'expanded_industry4': ('WA_AI_RESEARCH_needs_expanded_industry', 1941),
    'expanded_industry5': ('WA_AI_RESEARCH_needs_expanded_industry', 1943),
    'expanded_industry6': ('WA_AI_RESEARCH_needs_expanded_industry', 1945),

    # Industry Infrastructure branch
    'industry_infrastructure': ('WA_AI_RESEARCH_needs_industry_infrastructure', None),
    'industry_infrastructure2': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1937),
    'industry_infrastructure3': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1939),
    'industry_infrastructure4': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1941),
    'industry_infrastructure5': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1943),
    'industry_infrastructure6': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1945),

    # Industry Organization branch (odd = camouflage, even = efficiency)
    'industry_organization': ('WA_AI_RESEARCH_needs_industry_camouflage', None),
    'industry_organization2': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1937),
    'industry_organization3': ('WA_AI_RESEARCH_needs_industry_camouflage', 1939),
    'industry_organization4': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1941),
    'industry_organization5': ('WA_AI_RESEARCH_needs_industry_camouflage', 1943),
    'industry_organization6': ('WA_AI_RESEARCH_needs_industry_infrastructure', 1945),

    # Construction branch (AAT)
    'construction1': ('WA_AI_RESEARCH_needs_construction', None),
    'construction2': ('WA_AI_RESEARCH_needs_construction', 1937),
    'construction3': ('WA_AI_RESEARCH_needs_construction', 1939),
    'construction4': ('WA_AI_RESEARCH_needs_construction', 1941),
    'construction5': ('WA_AI_RESEARCH_needs_construction', 1943),
    'construction6': ('WA_AI_RESEARCH_needs_construction', 1945),

    # Excavation branch (AAT)
    'excavation1': ('WA_AI_RESEARCH_needs_excavation', None),
    'excavation2': ('WA_AI_RESEARCH_needs_excavation', 1937),
    'excavation3': ('WA_AI_RESEARCH_needs_excavation', 1939),
    'excavation4': ('WA_AI_RESEARCH_needs_excavation', 1941),
    'excavation5': ('WA_AI_RESEARCH_needs_excavation', 1943),
    'excavation6': ('WA_AI_RESEARCH_needs_excavation', 1945),

    # Airbase branch (AAT)
    'airbase4': ('WA_AI_RESEARCH_needs_airbases', 1941),
    'airbase5': ('WA_AI_RESEARCH_needs_airbases', 1943),
    'airbase6': ('WA_AI_RESEARCH_needs_airbases', 1945),

    # Fuel Silos
    'fuel_silos': ('WA_AI_RESEARCH_needs_fuel_silos', 1939),

    # Fuel Refining branch
    'fuel_refining': ('WA_AI_RESEARCH_needs_fuel_refining', None),
    'fuel_refining2': ('WA_AI_RESEARCH_needs_fuel_refining', 1937),
    'fuel_refining3': ('WA_AI_RESEARCH_needs_fuel_refining', 1939),
    'fuel_refining4': ('WA_AI_RESEARCH_needs_fuel_refining', 1941),
    'fuel_refining5': ('WA_AI_RESEARCH_needs_fuel_refining', 1943),
    'fuel_refining6': ('WA_AI_RESEARCH_needs_fuel_refining', 1945),

    # Synthetic Oil branch
    'synth_oil_experiments': (['WA_AI_RESEARCH_needs_synth_oil', 'WA_AI_RESEARCH_needs_synth_rubber'], 1936),
    'oil_processing': ('WA_AI_RESEARCH_needs_synth_oil', 1937),
    'improved_oil_processing': ('WA_AI_RESEARCH_needs_synth_oil', 1939),
    'advanced_oil_processing': ('WA_AI_RESEARCH_needs_synth_oil', 1941),
    'superior_oil_processing': ('WA_AI_RESEARCH_needs_synth_oil', 1943),
    'modern_oil_processing': ('WA_AI_RESEARCH_needs_synth_oil', 1945),

    # Synthetic Rubber branch
    'rubber_processing': ('WA_AI_RESEARCH_needs_synth_rubber', 1937),
    'improved_rubber_processing': ('WA_AI_RESEARCH_needs_synth_rubber', 1939),
    'advanced_rubber_processing': ('WA_AI_RESEARCH_needs_synth_rubber', 1941),
    'superior_rubber_processing': ('WA_AI_RESEARCH_needs_synth_rubber', 1943),
    'modern_rubber_processing': ('WA_AI_RESEARCH_needs_synth_rubber', 1945),

    # Starting Industry Techs (mutually exclusive choices)
    'concentrated_industry': (None, None),  # Starting tech, AI shouldn't research
    'standard_industry': (None, None),  # Starting tech
    'dispersed_industry': (None, None),  # Starting tech

    # Hidden/Fix techs
    'trade_fix_tech': (None, None),  # Hidden tech
}

ELECTRONICS_TRIGGERS = {
    # Base Electronics
    'electronic_mechanical_engineering': ('WA_AI_RESEARCH_needs_electronics_base', None),

    # Radio branch
    'radio': ('WA_AI_RESEARCH_needs_radio', None),

    # Radar branch
    'radio_detection': ('WA_AI_RESEARCH_needs_radar', 1936),
    'decimetric_radar': ('WA_AI_RESEARCH_needs_radar', 1939),
    'improved_decimetric_radar': ('WA_AI_RESEARCH_needs_radar', 1940),
    'centimetric_radar': ('WA_AI_RESEARCH_needs_radar', 1941),
    'improved_centimetric_radar': ('WA_AI_RESEARCH_needs_radar', 1942),
    'advanced_centimetric_radar': ('WA_AI_RESEARCH_needs_radar', 1943),

    # Computing branch
    'mechanical_computing': ('WA_AI_RESEARCH_needs_computing', None),
    'computing_machine': ('WA_AI_RESEARCH_needs_computing', 1938),
    'improved_computing_machine': ('WA_AI_RESEARCH_needs_computing', 1940),
    'advanced_computing_machine': ('WA_AI_RESEARCH_needs_computing', 1942),
    'superior_computing_machine': ('WA_AI_RESEARCH_needs_computing', 1944),

    # Encryption branch
    'basic_encryption': ('WA_AI_RESEARCH_needs_encryption', None),
    'improved_encryption': ('WA_AI_RESEARCH_needs_encryption', 1938),
    'advanced_encryption': ('WA_AI_RESEARCH_needs_encryption', 1940),
    'superior_encryption': ('WA_AI_RESEARCH_needs_encryption', 1942),
    'lar_encryption_bonus_tech': (None, None),  # Hidden LaR tech

    # Decryption branch
    'basic_decryption': ('WA_AI_RESEARCH_needs_decryption', None),
    'improved_decryption': ('WA_AI_RESEARCH_needs_decryption', 1938),
    'advanced_decryption': ('WA_AI_RESEARCH_needs_decryption', 1940),
    'superior_decryption': ('WA_AI_RESEARCH_needs_decryption', 1942),
    'lar_decryption_bonus_tech': (None, None),  # Hidden LaR tech

    # Fire Control Systems
    'basic_fire_control_system': ('WA_AI_RESEARCH_needs_fire_control', 1936),
    'improved_fire_control_system': ('WA_AI_RESEARCH_needs_fire_control', 1939),
    'advanced_fire_control_system': ('WA_AI_RESEARCH_needs_fire_control', 1941),
    'fire_control_methods_1': ('WA_AI_RESEARCH_needs_fire_control', 1936),
    'fire_control_methods_2': ('WA_AI_RESEARCH_needs_fire_control', 1939),
    'fire_control_methods_3': ('WA_AI_RESEARCH_needs_fire_control', 1942),

    # ASW branch
    'depth_charges': ('WA_AI_RESEARCH_needs_asw', 1936),
    'k_guns': ('WA_AI_RESEARCH_needs_asw', 1939),
    'hedgehog_depth_charge_mortar': ('WA_AI_RESEARCH_needs_asw', 1941),
    'squid_depth_charge_mortar': ('WA_AI_RESEARCH_needs_asw', 1943),
    'sonar': ('WA_AI_RESEARCH_needs_asw', 1936),
    'improved_sonar': ('WA_AI_RESEARCH_needs_asw', 1939),
    'advanced_sonar': ('WA_AI_RESEARCH_needs_asw', 1942),

    # Torpedoes/Smoke branch
    'smoke_generator': ('WA_AI_RESEARCH_needs_torpedoes', 1936),
    'magnetic_detonator': ('WA_AI_RESEARCH_needs_torpedoes', 1936),
    'electric_torpedo': ('WA_AI_RESEARCH_needs_torpedoes', 1938),
    'homing_torpedo': ('WA_AI_RESEARCH_needs_torpedoes', 1943),
    'long_lance': ('WA_AI_RESEARCH_needs_torpedoes', 1936),  # Japanese special

    # Naval Mines branch
    'basic_naval_mines': ('WA_AI_RESEARCH_needs_naval_mines', 1936),
    'improved_naval_mines': ('WA_AI_RESEARCH_needs_naval_mines', 1939),
    'advanced_naval_mines': ('WA_AI_RESEARCH_needs_naval_mines', 1942),
    'modern_naval_mines': ('WA_AI_RESEARCH_needs_naval_mines', 1944),
    'degaussing': ('WA_AI_RESEARCH_needs_naval_mines', 1939),
    'airdrop_mines': ('WA_AI_RESEARCH_needs_naval_mines', 1940),
    'airsweep_mines': ('WA_AI_RESEARCH_needs_naval_mines', 1941),
    'airdrop_mines_bba': ('WA_AI_RESEARCH_needs_naval_mines', 1940),
    'airsweep_mines_bba': ('WA_AI_RESEARCH_needs_naval_mines', 1941),
    'mine_destruction_device_tech_bba': ('WA_AI_RESEARCH_needs_naval_mines', 1940),

    # Submarine Equipment branch
    'submarine_mine_laying': ('WA_AI_RESEARCH_needs_submarine_equipment', 1936),
    'improved_submarine_mine_laying': ('WA_AI_RESEARCH_needs_submarine_equipment', 1940),
    'basic_submarine_fuel_tank': ('WA_AI_RESEARCH_needs_submarine_equipment', 1936),
    'improved_submarine_fuel_tank': ('WA_AI_RESEARCH_needs_submarine_equipment', 1939),
    'basic_submarine_snorkel': ('WA_AI_RESEARCH_needs_submarine_equipment', 1942),
    'improved_submarine_snorkel': ('WA_AI_RESEARCH_needs_submarine_equipment', 1944),

    # Damage Control
    'damage_control_1': ('WA_AI_RESEARCH_needs_fire_control', 1936),
    'damage_control_2': ('WA_AI_RESEARCH_needs_fire_control', 1939),
    'damage_control_3': ('WA_AI_RESEARCH_needs_fire_control', 1942),

    # Airplane Launcher
    'improved_airplane_launcher': ('WA_AI_RESEARCH_needs_fire_control', 1939),

    # Amphibious branch (MTG)
    'mtg_transport': ('WA_AI_RESEARCH_needs_amphibious', 1936),
    'mtg_landing_craft': ('WA_AI_RESEARCH_needs_amphibious', 1940),
    'mtg_tank_water_sealants': ('WA_AI_RESEARCH_needs_amphibious', 1940),
    'mtg_tank_snorkals': ('WA_AI_RESEARCH_needs_amphibious', 1942),
    'mtg_amphibious_assault_ships': ('WA_AI_RESEARCH_needs_amphibious', 1943),
    'mtg_large_landing_craft': ('WA_AI_RESEARCH_needs_amphibious', 1943),
    'mtg_tank_floats': ('WA_AI_RESEARCH_needs_amphibious', 1944),

    # Vehicle Electronics (uses trucks trigger per existing file)
    'vehicle_winch': ('WA_AI_RESEARCH_needs_trucks', 1936),

    # Nuclear branch
    'atomic_research': ('WA_AI_RESEARCH_needs_nuclear', 1940),
    'nuclear_reactor': ('WA_AI_RESEARCH_needs_nuclear', 1943),
    'nuclear_reactor_heavy_water': ('WA_AI_RESEARCH_needs_nuclear', 1943),
    'nukes': ('WA_AI_RESEARCH_needs_nuclear', 1945),

    # Rockets/Jets branch
    'experimental_rockets': ('WA_AI_RESEARCH_needs_rockets', 1939),
    'rocket_engines': ('WA_AI_RESEARCH_needs_rockets', 1941),
    'improved_rocket_engines': ('WA_AI_RESEARCH_needs_rockets', 1943),
    'advanced_rocket_engines': ('WA_AI_RESEARCH_needs_rockets', 1945),
    'jet_engines': ('WA_AI_RESEARCH_needs_rockets', 1943),
}


def get_tech_base_name(tech_name: str) -> str:
    """Remove _comp suffix to get base tech name for mapping lookup."""
    if tech_name.endswith('_comp'):
        return tech_name[:-5]
    return tech_name


def get_trigger_mapping(tech_name: str, file_type: str) -> tuple:
    """Get the trigger and date for a technology."""
    base_name = get_tech_base_name(tech_name)

    if file_type == 'industry':
        return INDUSTRY_TRIGGERS.get(base_name, (None, None))
    elif file_type == 'electronics':
        return ELECTRONICS_TRIGGERS.get(base_name, (None, None))
    return (None, None)


def should_use_factor_1(tech_name: str, trigger: str) -> bool:
    """Determine if tech should use factor 1 (mines, fire control, excavation, and airbase techs)."""
    if trigger is None:
        return False
    
    # Fire control techs
    if trigger == 'WA_AI_RESEARCH_needs_fire_control' or 'fire_control' in tech_name.lower():
        return True
    
    # Mine techs
    if trigger == 'WA_AI_RESEARCH_needs_naval_mines' or 'mine' in tech_name.lower():
        return True
    
    # Excavation techs
    if trigger == 'WA_AI_RESEARCH_needs_excavation' or 'excavation' in tech_name.lower():
        return True
    
    # Airbase techs
    if trigger == 'WA_AI_RESEARCH_needs_airbases' or 'airbase' in tech_name.lower():
        return True
    
    return False


def generate_ai_will_do(trigger, date: int, factor: int = 5) -> str:
    """Generate the standardized ai_will_do block - delegates to new base module.

    Args:
        trigger: Single trigger string, list of triggers, or None
        date: Start year for date restriction
        factor: Base factor value
    """
    # Use the new generator from base module with proper unused_research_slots logic
    if trigger is None:
        # XOR choice or unknown tech - use factor = 0
        return """		ai_will_do = {
			factor = 0
		}"""

    # Handle both single trigger and list of triggers
    if isinstance(trigger, list):
        triggers = trigger
    else:
        triggers = [trigger]

    if date is None:
        # No date restriction - generate simple trigger block
        if len(triggers) == 1:
            return f"""		ai_will_do = {{
			factor = {factor}
			modifier = {{
				factor = 0
				NOT = {{ {triggers[0]} = yes }}
			}}
		}}"""
        else:
            # Multiple triggers with OR
            or_block = "\n".join([f"\t\t\t\t{t} = yes" for t in triggers])
            return f"""		ai_will_do = {{
			factor = {factor}
			modifier = {{
				factor = 0
				NOT = {{
					OR = {{
{or_block}
					}}
				}}
			}}
		}}"""

    return generate_ai_will_do_block(triggers, date, indent="		", factor=factor)
def generate_ai_will_do_old(trigger: str, date: int, factor: int = 5) -> str:
    """OLD VERSION - kept for reference but not used."""
    if trigger is None:
        # XOR choice or unknown tech - use factor = 0
        return """\t\tai_will_do = {
			factor = 0
		}"""

    if date is None:
        # No date restriction
        return f"""\t\tai_will_do = {{
			factor = {factor}
			modifier = {{
				factor = 0
				NOT = {{ {trigger} = yes }}
			}}
		}}"""
    else:
        return f"""\t\tai_will_do = {{
			factor = {factor}
			modifier = {{
				factor = 0
				NOT = {{ {trigger} = yes }}
			}}
			modifier = {{
				factor = 0
				date < {date}.1.1
			}}
		}}"""


def extract_start_year(tech_content: str) -> int:
    """Extract start_year from a technology block."""
    match = re.search(r'start_year\s*=\s*(\d{4})', tech_content)
    if match:
        return int(match.group(1))
    return None


def find_ai_will_do_blocks(content: str) -> list:
    """Find all ai_will_do blocks with their positions and tech names."""
    blocks = []

    # Pattern to find tech definitions
    tech_pattern = re.compile(r'^\t(\w+)\s*=\s*\{', re.MULTILINE)

    # Find each tech and its ai_will_do block
    current_pos = 0
    for match in tech_pattern.finditer(content):
        tech_name = match.group(1)
        tech_start = match.start()

        # Find the ai_will_do block within this tech
        # We need to find the matching closing brace for the tech first
        brace_count = 0
        in_tech = False
        ai_start = None
        ai_end = None

        i = match.end() - 1  # Start from the opening brace
        while i < len(content):
            char = content[i]
            if char == '{':
                brace_count += 1
                if not in_tech:
                    in_tech = True
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    # End of tech definition
                    tech_end = i + 1
                    break
            i += 1

        # Search for ai_will_do within this tech block
        tech_content = content[tech_start:tech_end]
        ai_match = re.search(r'\n[\t]*ai_will_do\s*=\s*\{', tech_content)

        if ai_match:
            ai_block_start = tech_start + ai_match.start() + 1  # +1 to skip newline

            # Find matching closing brace for ai_will_do
            brace_count = 0
            i = ai_block_start
            while i < tech_end + tech_start:
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        ai_block_end = i + 1
                        break
                i += 1

            # Extract start_year from tech content
            start_year = extract_start_year(tech_content)

            blocks.append({
                'tech_name': tech_name,
                'start': ai_block_start,
                'end': ai_block_end,
                'original': content[ai_block_start:ai_block_end],
                'tech_content': tech_content,
                'start_year': start_year
            })

    return blocks


def process_file(file_path: Path, file_type: str, dry_run: bool = False) -> dict:
    """Process a single file and replace ai_will_do blocks."""
    # Check if file has BOM
    has_bom = False
    with open(file_path, 'rb') as f:
        first_bytes = f.read(3)
        has_bom = first_bytes == b'\xef\xbb\xbf'
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    original_content = content
    blocks = find_ai_will_do_blocks(content)

    stats = {
        'total': len(blocks),
        'replaced': 0,
        'skipped': 0,
        'unknown': []
    }

    # Process blocks in reverse order to maintain positions
    for block in reversed(blocks):
        tech_name = block['tech_name']
        trigger, mapping_date = get_trigger_mapping(tech_name, file_type)

        # Use start_year from tech file if available, otherwise fall back to mapping date
        start_year = block.get('start_year')
        if start_year is None:
            start_year = mapping_date
        elif mapping_date is not None:
            # If both exist, prefer start_year from tech file (it's the source of truth)
            # But warn if they don't match
            if start_year != mapping_date and dry_run:
                print(f"  WARNING: {tech_name}: start_year={start_year} doesn't match mapping date={mapping_date}, using start_year")

        if trigger is None and start_year is None:
            base_name = get_tech_base_name(tech_name)
            if base_name not in (INDUSTRY_TRIGGERS if file_type == 'industry' else ELECTRONICS_TRIGGERS):
                stats['unknown'].append(tech_name)
                stats['skipped'] += 1
                continue

        # Determine factor: 1 for mines and fire control, 5 for others
        factor = 1 if should_use_factor_1(tech_name, trigger) else 5
        new_ai_will_do = generate_ai_will_do(trigger, start_year, factor)

        # Replace the block
        content = content[:block['start']] + new_ai_will_do + content[block['end']:]
        stats['replaced'] += 1

        if dry_run:
            factor_str = f", factor={factor}" if trigger is not None else ""
            print(f"  {tech_name}: {trigger or 'factor=0'}, date={start_year}{factor_str} (from {'tech file' if block.get('start_year') else 'mapping'})")

    # Always rewrite file without BOM if it had BOM or content changed
    if not dry_run and (content != original_content or has_bom):
        # Write UTF-8 without BOM (HOI4 parser doesn't handle BOM)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return stats


def main():
    parser = argparse.ArgumentParser(description='Replace ai_will_do blocks in HOI4 tech files')
    parser.add_argument('file', help='Input file path')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying')
    parser.add_argument('--type', choices=['industry', 'electronics', 'auto'], default='auto',
                        help='File type (auto-detect by default)')
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Auto-detect file type
    file_type = args.type
    if file_type == 'auto':
        if 'industry' in file_path.name.lower():
            file_type = 'industry'
        elif 'electronic' in file_path.name.lower():
            file_type = 'electronics'
        else:
            print("Error: Could not auto-detect file type. Use --type to specify.")
            sys.exit(1)

    print(f"Processing {file_path} as {file_type}...")
    if args.dry_run:
        print("DRY RUN - no changes will be made\n")

    stats = process_file(file_path, file_type, args.dry_run)

    print(f"\nResults:")
    print(f"  Total ai_will_do blocks found: {stats['total']}")
    print(f"  Replaced: {stats['replaced']}")
    print(f"  Skipped: {stats['skipped']}")

    if stats['unknown']:
        print(f"\nUnknown technologies (no mapping defined):")
        for tech in stats['unknown']:
            print(f"  - {tech}")


if __name__ == '__main__':
    main()
