"""
World Ablaze AI map data generators.

This package contains generators for creating precomputed map data files
used by the World Ablaze AI system.

Available generators:
- ProvinceTerrainGenerator: Province terrain type mappings
- ProvinceConnectionsGenerator: Province adjacency data
- ProvincePositionsGenerator: Province center coordinates
- RailwayConnectionsGenerator: Railway connection levels
- StateProvincesGenerator: State-to-province mappings
- StateVpProvincesGenerator: State-to-VP-province mappings (for capital detection)
- LandmassGenerator: Connected landmass identification
"""

from .base import BaseMapGenerator, GeneratorConfig, GeneratorResult
from .province_terrain import ProvinceTerrainGenerator
from .province_connections import ProvinceConnectionsGenerator
from .province_positions import ProvincePositionsGenerator
from .railway_connections import RailwayConnectionsGenerator
from .state_provinces import StateProvincesGenerator
from .state_vp_provinces import StateVpProvincesGenerator
from .landmass import LandmassGenerator

__all__ = [
    # Base classes
    "BaseMapGenerator",
    "GeneratorConfig",
    "GeneratorResult",
    # Generators
    "ProvinceTerrainGenerator",
    "ProvinceConnectionsGenerator",
    "ProvincePositionsGenerator",
    "RailwayConnectionsGenerator",
    "StateProvincesGenerator",
    "StateVpProvincesGenerator",
    "LandmassGenerator",
]

# Registry of all generators
GENERATORS = {
    "province_terrain": ProvinceTerrainGenerator,
    "province_connections": ProvinceConnectionsGenerator,
    "province_positions": ProvincePositionsGenerator,
    "railway_connections": RailwayConnectionsGenerator,
    "state_provinces": StateProvincesGenerator,
    "state_vp_provinces": StateVpProvincesGenerator,
    "landmass": LandmassGenerator,
}

# Recommended execution order (respects dependencies)
EXECUTION_ORDER = [
    "province_connections",  # No dependencies
    "province_positions",  # No dependencies
    "province_terrain",  # No dependencies
    "railway_connections",  # No dependencies
    "state_provinces",  # No dependencies
    "state_vp_provinces",  # No dependencies (reads from history/states)
    "landmass",  # Depends on province_connections and state_provinces
]
