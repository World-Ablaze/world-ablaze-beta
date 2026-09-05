"""Configuration for DLC splitter"""

from typing import Dict, List, Set

# Default target DLCs
DEFAULT_DLCS: List[str] = [
    "By Blood Alone",
    "No Step Back",
]

# DLC short names for filenames
DLC_SHORT_NAMES: Dict[str, str] = {
    "By Blood Alone": "bba",
    "No Step Back": "nsb",
    "Man the Guns": "mtg",
    "La Resistance": "lar",
    "Arms Against Tyranny": "aat",
    "Battle for the Bosporus": "bftb",
    "Death or Dishonor": "dod",
    "Together for Victory": "tfv",
}

# Blocks that may contain DLC conditions
CONDITION_BLOCKS: Set[str] = {
    'allow_branch',
    'can_be_produced',
    'allow',
    'visible',
    'available',
}

# Root block names for different file types
ROOT_BLOCKS: Set[str] = {
    'technologies',
    'equipments',
}

# Blocks that are containers, not tech/equipment definitions
CONTAINER_BLOCKS: Set[str] = {
    'technologies',
    'equipments',
    'categories',
    'path',
    'folder',
    'sub_technologies',
    'enable_equipments',
    'enable_equipment_modules',
    'enable_subunits',
    'modifier',
    'on_research_complete',
    'on_research_complete_limit',
    'research_cost_coeff',
    'XOR',
    'OR',
    'AND',
    'NOT',
    'if',
    'else',
    'else_if',
    'limit',
    'ai_will_do',
    'default_modules',
    'module_slots',
    'module_count_limit',
    'resources',
}
