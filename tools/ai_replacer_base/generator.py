"""
AI Will Do block generation utilities.

Provides functions for generating standardized ai_will_do blocks.
"""

from typing import Optional


def generate_ai_will_do_block(
    triggers: list[str],
    start_year: int,
    indent: str = "\t\t",
    factor: int = 1,
    use_or: bool = True
) -> str:
    """
    Generate ai_will_do block with triggers.

    Single trigger format:
        ai_will_do = {
            factor = 1

            modifier = {
                factor = 0
                NOT = { WA_AI_RESEARCH_needs_X = yes }
            }

            modifier = {
                factor = 0
                OR = {
                    AND = {
                        NOT = { has_country_flag = WA_AI_unused_research_slots }
                        date < YEAR.1.1
                    }
                    AND = {
                        has_country_flag = WA_AI_unused_research_slots
                        date < YEAR-1.1.1
                    }
                }
            }
        }

    Multiple triggers (OR) format:
        ai_will_do = {
            factor = 1

            modifier = {
                factor = 0
                NOT = {
                    OR = {
                        WA_AI_RESEARCH_needs_X = yes
                        WA_AI_RESEARCH_needs_Y = yes
                    }
                }
            }
            ...
        }

    Args:
        triggers: List of trigger names
        start_year: Start year for the tech
        indent: Base indentation string (default: 2 tabs for tech content)
        factor: Base factor value (default: 1)
        use_or: Use OR logic for multiple triggers (default: True)

    Returns:
        Formatted ai_will_do block string
    """
    if not triggers:
        return ""

    lines = [f"{indent}ai_will_do = {{"]
    lines.append(f"{indent}\tfactor = {factor}")
    lines.append("")
    lines.append(f"{indent}\tmodifier = {{")
    lines.append(f"{indent}\t\tfactor = 0")

    # Build the NOT condition
    if len(triggers) == 1:
        # Single trigger - simple NOT block
        lines.append(f"{indent}\t\tNOT = {{ {triggers[0]} = yes }}")
    else:
        # Multiple triggers - use OR condition (research if ANY trigger is needed)
        lines.append(f"{indent}\t\tNOT = {{")
        lines.append(f"{indent}\t\t\tOR = {{")
        for trigger in sorted(triggers):  # Sort for consistent output
            lines.append(f"{indent}\t\t\t\t{trigger} = yes")
        lines.append(f"{indent}\t\t\t}}")
        lines.append(f"{indent}\t\t}}")

    lines.append(f"{indent}\t}}")

    # Build date modifier with unused research slots logic
    early_year = start_year - 1
    lines.append("")
    lines.append(f"{indent}\tmodifier = {{")
    lines.append(f"{indent}\t\tfactor = 0")
    lines.append(f"{indent}\t\tOR = {{")
    lines.append(f"{indent}\t\t\tAND = {{")
    lines.append(f"{indent}\t\t\t\tNOT = {{ has_country_flag = WA_AI_unused_research_slots }}")
    lines.append(f"{indent}\t\t\t\tdate < {start_year}.1.1")
    lines.append(f"{indent}\t\t\t}}")
    lines.append(f"{indent}\t\t\tAND = {{")
    lines.append(f"{indent}\t\t\t\thas_country_flag = WA_AI_unused_research_slots")
    lines.append(f"{indent}\t\t\t\tdate < {early_year}.1.1")
    lines.append(f"{indent}\t\t\t}}")
    lines.append(f"{indent}\t\t}}")
    lines.append(f"{indent}\t}}")
    lines.append(f"{indent}}}")

    return "\n".join(lines)


def generate_simple_ai_will_do(
    trigger: Optional[str],
    date: Optional[int],
    indent: str = "\t\t",
    factor: int = 5
) -> str:
    """
    Generate a simple ai_will_do block without unused research slots logic.

    Used for industry/electronics techs that use simpler format.

    Args:
        trigger: Trigger name (None for factor = 0 block)
        date: Start date (None for no date restriction)
        indent: Base indentation string
        factor: Base factor value

    Returns:
        Formatted ai_will_do block string
    """
    if trigger is None:
        # XOR choice or unknown tech - use factor = 0
        return f"""{indent}ai_will_do = {{
{indent}\tfactor = 0
{indent}}}"""

    if date is None:
        # No date restriction
        return f"""{indent}ai_will_do = {{
{indent}\tfactor = {factor}
{indent}\tmodifier = {{
{indent}\t\tfactor = 0
{indent}\t\tNOT = {{ {trigger} = yes }}
{indent}\t}}
{indent}}}"""
    else:
        return f"""{indent}ai_will_do = {{
{indent}\tfactor = {factor}
{indent}\tmodifier = {{
{indent}\t\tfactor = 0
{indent}\t\tNOT = {{ {trigger} = yes }}
{indent}\t}}
{indent}\tmodifier = {{
{indent}\t\tfactor = 0
{indent}\t\tdate < {date}.1.1
{indent}\t}}
{indent}}}"""
