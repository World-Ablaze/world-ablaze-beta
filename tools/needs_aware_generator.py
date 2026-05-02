"""
Generator for needs-aware ai_will_do blocks for prospecting decisions.

Creates blocks with reactive, cooperative, and proactive layers.
"""

import re
from typing import Optional
from prospecting_decision_analyzer import (
    DecisionMetadata,
    STRATEGIC_RESOURCES,
    STRATEGIC_EXPORTERS,
    is_strategic_exporter_decision,
)


def extract_existing_modifiers(ai_will_do_block: str) -> list[str]:
    """
    Extract existing modifier blocks that should be preserved.

    Looks for modifiers that are country-specific (tag, original_tag, SOV_*, etc)
    and should not be overwritten. Properly handles nested braces.
    """
    preserved = []

    # Find all "modifier = {" positions
    for match in re.finditer(r'modifier\s*=\s*\{', ai_will_do_block):
        start_pos = match.start()
        brace_start = match.end() - 1  # Position of the opening brace

        # Find matching closing brace with proper nesting
        brace_count = 1
        end_pos = brace_start + 1
        while end_pos < len(ai_will_do_block) and brace_count > 0:
            if ai_will_do_block[end_pos] == '{':
                brace_count += 1
            elif ai_will_do_block[end_pos] == '}':
                brace_count -= 1
            end_pos += 1

        # Extract the complete modifier block
        modifier_block = ai_will_do_block[start_pos:end_pos]

        # Check if this is a country-specific or special modifier
        if any(pattern in modifier_block for pattern in [
            'original_tag',
            'tag',
            'has_completed_focus',
            'SOV_',
            'has_war',
            'date <',
            'date >',
        ]):
            preserved.append(modifier_block)

    return preserved


def get_factor_multipliers(metadata: DecisionMetadata) -> tuple[int, int, int]:
    """
    Determine factor multipliers based on resource type.

    Returns: (reactive_factor, cooperative_factor, proactive_factor)
    """
    if metadata.resource_type in STRATEGIC_RESOURCES:
        # Strategic resources get higher multipliers
        return (15, 15, 100)
    else:
        # Commodity resources get standard multipliers
        return (10, 5, 100)


def generate_reactive_modifier(resource_type: str, reactive_factor: int) -> str:
    """Generate reactive modifier (AI needs this resource) - 3 tab indentation."""
    return f"""\t\t\t# Reactive: AI needs {resource_type}
\t\t\tmodifier = {{
\t\t\t\tfactor = {reactive_factor}
\t\t\t\tOR = {{
\t\t\t\t\tcheck_variable = {{ WA_AI_needs_{resource_type} > 1 }}
\t\t\t\t\tcheck_variable = {{ WA_AI_resource_{resource_type}_shortage_months > 0 }}
\t\t\t\t}}
\t\t\t}}"""


def generate_cooperative_modifier(resource_type: str, cooperative_factor: int) -> str:
    """Generate cooperative modifier (Allies need this resource) - 3 tab indentation."""
    return f"""\t\t\t# Cooperative: Allies need {resource_type}
\t\t\tmodifier = {{
\t\t\t\tfactor = {cooperative_factor}
\t\t\t\tany_faction_member = {{
\t\t\t\t\tNOT = {{ tag = ROOT }}
\t\t\t\t\tcheck_variable = {{ WA_AI_needs_{resource_type} = 3 }}
\t\t\t\t}}
\t\t\t}}"""


def generate_proactive_modifier(metadata: DecisionMetadata) -> Optional[str]:
    """Generate proactive modifier (Strategic exporter boost) - 3 tab indentation."""
    # Only generate proactive modifier if this is for a strategic exporter
    if not is_strategic_exporter_decision(metadata):
        return None

    # Find which tag(s) are strategic exporters
    exporter_tags = [tag for tag in metadata.country_tags if tag in STRATEGIC_EXPORTERS]
    if not exporter_tags:
        return None

    # Build OR clause for tags
    tag_conditions = '\n\t\t\t\t\t'.join([f'tag = {tag}' for tag in exporter_tags])

    # Check for strategic exporter focus or Free Trade law
    return f"""\t\t\t# Proactive: Strategic exporter boost
\t\t\tmodifier = {{
\t\t\t\tfactor = 100
\t\t\t\thas_war = no
\t\t\t\tOR = {{
\t\t\t\t\t{tag_conditions}
\t\t\t\t}}
\t\t\t\tOR = {{
\t\t\t\t\thas_idea = free_trade
\t\t\t\t\thas_completed_focus = POR_extraction_industries
\t\t\t\t}}
\t\t\t}}"""


def generate_ai_will_do_block(metadata: DecisionMetadata, preserved_modifiers: list[str]) -> str:
    """
    Generate a needs-aware ai_will_do block.

    ALL DECISIONS USE 2-TAB INDENTATION FOR ai_will_do (standard format).
    This function generates with 2-tab indentation.

    Args:
        metadata: Decision metadata
        preserved_modifiers: List of existing modifier blocks to preserve (already indented)

    Returns:
        Complete ai_will_do block as string
    """
    resource = metadata.resource_type

    # Get factor multipliers
    reactive_factor, cooperative_factor, proactive_factor = get_factor_multipliers(metadata)

    # ALWAYS 2 tabs for ai_will_do in decisions
    # Build the block with fixed 2-tab indentation
    lines = [
        '\t\tai_will_do = {',
        '\t\t\tfactor = 1',
        '',
    ]

    # Add reactive modifier
    lines.append(generate_reactive_modifier(resource, reactive_factor))
    lines.append('')

    # Add cooperative modifier
    lines.append(generate_cooperative_modifier(resource, cooperative_factor))
    lines.append('')

    # Add proactive modifier if applicable
    proactive = generate_proactive_modifier(metadata)
    if proactive:
        lines.append(proactive)
        lines.append('')

    # Add preserved modifiers
    if preserved_modifiers:
        lines.append('\t\t\t# Preserve existing country-specific modifiers')
        for mod in preserved_modifiers:
            # Preserved modifiers are already extracted and indented from original ai_will_do
            # We need to preserve their internal indentation structure while re-indenting to match our context (3 tabs)
            mod_lines = mod.strip().split('\n')

            # Find the minimum indentation of opening and closing braces
            # Content should be indented 1 tab MORE than braces
            brace_indent = float('inf')
            content_indent = float('inf')

            for i, mod_line in enumerate(mod_lines):
                if mod_line.strip():
                    indent = len(mod_line) - len(mod_line.lstrip('\t'))
                    # First line (opening brace) and last line (closing brace) are at base level
                    if i == 0 or i == len(mod_lines) - 1:
                        brace_indent = min(brace_indent, indent)
                    else:
                        content_indent = min(content_indent, indent)

            if brace_indent == float('inf'):
                brace_indent = 0
            if content_indent == float('inf'):
                content_indent = 0

            # Re-indent: move braces to 3 tabs, move content to 4 tabs
            # Preserve relative indentation differences
            for i, mod_line in enumerate(mod_lines):
                if mod_line.strip():
                    # First line is "modifier = {", place at 3 tabs
                    if i == 0:
                        lines.append('\t\t\t' + mod_line.lstrip())
                    # Last line is closing brace, place at 3 tabs
                    elif i == len(mod_lines) - 1:
                        lines.append('\t\t\t' + mod_line.lstrip())
                    # Content lines: place at 4 tabs (3 context + 1 nesting)
                    # But preserve any relative indentation beyond the base content indent
                    else:
                        stripped = mod_line[content_indent:] if len(mod_line) >= content_indent else mod_line
                        lines.append('\t\t\t\t' + stripped.lstrip('\t'))
                else:
                    lines.append('')
        lines.append('')

    lines.append('\t\t}')

    return '\n'.join(lines)


def replace_ai_will_do_block(full_decision: str, metadata: DecisionMetadata, preserved_modifiers: list[str]) -> str:
    """
    Replace ai_will_do block in a decision with needs-aware version.

    Args:
        full_decision: The complete decision block content
        metadata: Decision metadata
        preserved_modifiers: Existing modifiers to preserve

    Returns:
        Decision with updated ai_will_do block
    """
    # Find and replace ai_will_do block
    ai_will_do_pattern = r'\tai_will_do\s*=\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
    new_block = generate_ai_will_do_block(metadata, preserved_modifiers)

    # Handle nested braces more carefully - look for ai_will_do = { and find matching }
    # This regex handles modifier sub-blocks
    pattern = r'(\tai_will_do\s*=\s*\{)(.*?)(\n\t\}(?:\n|$))'

    def replacer(match):
        # Keep indentation, replace content
        new_content = generate_ai_will_do_block(metadata, preserved_modifiers)[1:]
        return f'\tai_will_do = {{\n{new_content}\n\t}}\n'

    result = re.sub(pattern, replacer, full_decision, flags=re.DOTALL)

    # If pattern didn't match, try simpler approach
    if result == full_decision:
        # Simple replacement for straightforward ai_will_do blocks
        simple_pattern = r'\tai_will_do\s*=\s*\{[^}]*\}'
        result = re.sub(simple_pattern, new_block, full_decision)

    return result


def detect_resource_from_icon(icon: Optional[str]) -> Optional[str]:
    """Detect resource type from icon name if resource type not found in code."""
    if not icon:
        return None

    icon_lower = icon.lower()
    from prospecting_decision_analyzer import ALL_RESOURCES

    for resource in ALL_RESOURCES:
        if resource in icon_lower:
            return resource

    return None
