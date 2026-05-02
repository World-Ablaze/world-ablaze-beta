"""
AI Will Do Replacer Base Module

Common utilities and base classes for all AI research trigger replacer parsers.
"""

from .file_processor import BaseFileProcessor, ProcessingStats
from .block_finder import (
    TechBlock,
    find_tech_blocks,
    find_matching_brace,
    find_ai_will_do_block,
    extract_block_content,
)
from .trigger_resolver import BaseTriggerResolver
from .tech_graph import TechGraph, build_tech_graph, get_reachable_techs, get_reachable_triggers
from .generator import generate_ai_will_do_block
from .text_utils import (
    extract_start_year,
    extract_categories,
    extract_dependencies,
    extract_leads_to_techs,
    extract_enable_equipments,
)

__all__ = [
    # File processor
    'BaseFileProcessor',
    'ProcessingStats',
    # Block finder
    'TechBlock',
    'find_tech_blocks',
    'find_matching_brace',
    'find_ai_will_do_block',
    'extract_block_content',
    # Trigger resolver
    'BaseTriggerResolver',
    # Tech graph
    'TechGraph',
    'build_tech_graph',
    'get_reachable_techs',
    'get_reachable_triggers',
    # Generator
    'generate_ai_will_do_block',
    # Text utils
    'extract_start_year',
    'extract_categories',
    'extract_dependencies',
    'extract_leads_to_techs',
    'extract_enable_equipments',
]
