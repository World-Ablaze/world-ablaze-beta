"""
Analyzer for prospecting decision metadata.

Extracts decision name, resource type, state ID, and other metadata
from prospecting decision blocks.
"""

import re
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class DecisionMetadata:
    """Metadata extracted from a prospecting decision."""
    name: str
    state_id: Optional[int]
    resource_type: Optional[str]
    resource_amount: Optional[int]
    icon: Optional[str]
    original_factor: Optional[int]
    has_country_specific_mods: bool
    country_tags: list[str]
    start_line: int
    end_line: int


STRATEGIC_RESOURCES = {'tungsten', 'rubber', 'chromium', 'aluminum'}
COMMODITY_RESOURCES = {'coal', 'oil', 'iron', 'steel', 'bauxite'}
ALL_RESOURCES = STRATEGIC_RESOURCES | COMMODITY_RESOURCES

# Strategic exporters: tag -> resource
STRATEGIC_EXPORTERS = {
    'SWE': 'tungsten',
    'POR': 'tungsten',
    'MAL': 'rubber',
    'INS': 'rubber',
    'IRQ': 'oil',
    'BRA': 'rubber',
}


def extract_resource_type(content: str) -> Optional[str]:
    """Extract resource type from decision content."""
    # Look for: add_resource = { type = [resource] amount = [amount] }
    match = re.search(r'type\s*=\s*(\w+)', content)
    if match:
        resource = match.group(1).lower()
        if resource in ALL_RESOURCES:
            return resource
    return None


def extract_resource_amount(content: str) -> Optional[int]:
    """Extract resource amount from decision content."""
    match = re.search(r'amount\s*=\s*(\d+)', content)
    if match:
        return int(match.group(1))
    return None


def extract_state_id(content: str) -> Optional[int]:
    """Extract state ID from decision content."""
    # Look for highlight_state_targets or state references
    match = re.search(r'state\s*=\s*(\d+)', content)
    if match:
        return int(match.group(1))
    return None


def extract_icon(content: str) -> Optional[str]:
    """Extract icon name from decision."""
    match = re.search(r'icon\s*=\s*(\w+)', content)
    if match:
        return match.group(1)
    return None


def extract_original_factor(content: str) -> Optional[int]:
    """Extract original ai_will_do factor from decision."""
    # Look for factor = [number] in ai_will_do block
    match = re.search(r'ai_will_do\s*=\s*\{[^}]*factor\s*=\s*(\d+)', content, re.DOTALL)
    if match:
        return int(match.group(1))
    return None


def extract_country_tags(content: str) -> list[str]:
    """Extract country tags from decision (tag, original_tag references)."""
    tags = []
    for match in re.finditer(r'(?:tag|original_tag)\s*=\s*([A-Z]{3})', content):
        tags.append(match.group(1))
    return list(set(tags))  # Deduplicate


def has_country_specific_modifiers(content: str) -> bool:
    """Check if decision has country-specific ai_will_do modifiers."""
    ai_will_do_section = re.search(r'ai_will_do\s*=\s*\{[^}]*\}', content, re.DOTALL)
    if not ai_will_do_section:
        return False

    ai_section = ai_will_do_section.group(0)

    # Check for country-specific patterns
    patterns = [
        r'original_tag\s*=',
        r'tag\s*=',
        r'has_completed_focus\s*=',
        r'SOV_save_pp_for_manpower_trouble',
        r'has_war\s*=\s*no',
        r'date\s*<'
    ]

    for pattern in patterns:
        if re.search(pattern, ai_section):
            return True

    return False


def analyze_decision(decision_content: str, decision_name: str, start_line: int, end_line: int) -> Optional[DecisionMetadata]:
    """
    Analyze a decision block and extract metadata.

    Args:
        decision_content: The decision block content
        decision_name: Name of the decision
        start_line: Starting line number
        end_line: Ending line number

    Returns:
        DecisionMetadata object or None if invalid
    """
    # Must have a resource type to be processed
    resource_type = extract_resource_type(decision_content)
    if not resource_type:
        return None

    return DecisionMetadata(
        name=decision_name,
        state_id=extract_state_id(decision_content),
        resource_type=resource_type,
        resource_amount=extract_resource_amount(decision_content),
        icon=extract_icon(decision_content),
        original_factor=extract_original_factor(decision_content),
        has_country_specific_mods=has_country_specific_modifiers(decision_content),
        country_tags=extract_country_tags(decision_content),
        start_line=start_line,
        end_line=end_line,
    )


def is_strategic_exporter_decision(metadata: DecisionMetadata) -> bool:
    """Check if this decision is for a strategic exporter country."""
    for tag in metadata.country_tags:
        if tag in STRATEGIC_EXPORTERS:
            expected_resource = STRATEGIC_EXPORTERS[tag]
            if metadata.resource_type == expected_resource:
                return True
    return False
