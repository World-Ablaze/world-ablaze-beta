"""
Generator for needs-aware ai_will_do blocks for prospecting decisions.

Creates blocks with reactive, cooperative, and proactive layers.
"""

import re
from typing import Optional
from prospecting_decision_analyzer import (
    DecisionMetadata,
    STRATEGIC_RESOURCES,
)


def is_generated_modifier(modifier_block: str) -> bool:
    """True if this modifier block was emitted by this generator (any version)."""
    if 'WA_AI_should_prospect_resource_' in modifier_block:
        return True
    if 'WA_AI_allies_need_' in modifier_block:
        return True
    if 'WA_AI_is_strategic_' in modifier_block:
        return True
    # Legacy inline reactive/cooperative form (pre scripted-trigger)
    if 'WA_AI_needs_' in modifier_block or 'WA_AI_resource_' in modifier_block:
        return True
    # Proactive strategic-exporter block signature
    if ('has_idea = free_trade' in modifier_block
            and 'has_completed_focus = POR_extraction_industries' in modifier_block
            and 'has_war = no' in modifier_block):
        return True
    return False


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

        # Skip blocks this generator emitted on a previous run (re-running on
        # already-generated output must be idempotent). The proactive block
        # matches the 'tag'/'has_completed_focus' patterns below and used to be
        # re-preserved as a duplicate on every run.
        if is_generated_modifier(modifier_block):
            continue

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
    Determine layer weights based on resource type.

    Since 2026-08-15 the base weight is 0 and every layer is an ``add``, so
    these are absolute weights, not multipliers: a decision whose layers are all
    false has weight 0 and is never taken.  Before that the base was
    ``factor = 1`` and the layers were multiplicative boosts, which meant the AI
    took every available prospecting decision regardless of need (GER
    re-prospecting all its coal states in late 1943 on a +15 000 balance).

    Returns: (reactive_weight, cooperative_weight, proactive_weight)
    """
    if metadata.resource_type in STRATEGIC_RESOURCES:
        # Strategic resources get higher weights
        return (15, 15, 100)
    else:
        # Commodity resources get standard weights
        return (10, 5, 100)


def generate_reactive_modifier(resource_type: str, reactive_weight: int) -> str:
    """Generate reactive modifier (AI needs this resource) - 3 tab indentation.

    Reads the scripted trigger ``WA_AI_should_prospect_resource_<r>`` from
    common/scripted_triggers/WA_AI_RESOURCE_NEEDS_triggers.txt rather than
    inlining the variable checks: the trigger is where per-resource nuances
    live (aluminium spelling, the coal proactive buffer, ...).
    """
    return f"""\t\t\t# Reactive: AI needs {resource_type}
\t\t\tmodifier = {{
\t\t\t\tadd = {reactive_weight}
\t\t\t\tWA_AI_should_prospect_resource_{resource_type} = yes
\t\t\t}}"""


def generate_cooperative_modifier(resource_type: str, cooperative_weight: int) -> str:
    """Generate cooperative modifier (Allies need this resource) - 3 tab indentation."""
    return f"""\t\t\t# Cooperative: Allies need {resource_type}
\t\t\tmodifier = {{
\t\t\t\tadd = {cooperative_weight}
\t\t\t\tWA_AI_allies_need_{resource_type} = yes
\t\t\t}}"""


# Resources that have a WA_AI_is_strategic_<r>_exporter capability trigger in
# common/scripted_triggers/WA_AI_RESOURCE_NEEDS_triggers.txt (whose tag list is
# WA_AI_CONFIG_is_strategic_<r>_exporter in WA_AI_CONFIG.txt).
EXPORTER_TRIGGER_RESOURCES = {'tungsten', 'rubber', 'oil'}


def generate_proactive_modifier(metadata: DecisionMetadata) -> Optional[str]:
    """Generate proactive modifier (Strategic exporter boost) - 3 tab indentation.

    Emitted for EVERY decision of a resource that has an exporter trigger; the
    trigger decides at runtime who the exporter is (country tags live in
    WA_AI_CONFIG.txt, never in generated script - AGENTS.md principle 2).
    """
    if metadata.resource_type not in EXPORTER_TRIGGER_RESOURCES:
        return None

    # ``add``, not ``factor``: on a base of 0 a factor would zero itself out.
    return f"""\t\t\t# Proactive: Strategic exporter boost
\t\t\tmodifier = {{
\t\t\t\tadd = 100
\t\t\t\tWA_AI_is_strategic_{metadata.resource_type}_exporter = yes
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
    # base = 0 (vanilla's additive-weight form, e.g. BUL.txt): the AI only
    # prospects when at least one layer below adds weight. Not root ``factor``,
    # which HOI4 treats as a multiplier and would zero the whole block.
    # Preserved country-specific ``factor = 0`` gates are appended AFTER the
    # add layers so they still multiply the accumulated weight down to 0.
    lines = [
        '\t\tai_will_do = {',
        '\t\t\tbase = 0',
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
