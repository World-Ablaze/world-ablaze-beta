"""
Main entry point for all World Ablaze map data generators.

Usage:
    python run_generators.py --help                  # Show available generators
    python run_generators.py all                     # Run all generators
    python run_generators.py landmass                # Run specific generator
    python run_generators.py landmass province_terrain  # Run multiple
    python run_generators.py all --dry-run -v        # Dry run with verbose
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Type

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from map_generators import (
    BaseMapGenerator,
    GeneratorConfig,
    GeneratorResult,
    GENERATORS,
    EXECUTION_ORDER,
)


def run_generators(
    names: List[str],
    config: GeneratorConfig,
) -> Dict[str, GeneratorResult]:
    """
    Run specified generators in dependency order.

    Args:
        names: List of generator names to run ('all' for all).
        config: Generator configuration.

    Returns:
        Dictionary of generator_name -> GeneratorResult.
    """
    results: Dict[str, GeneratorResult] = {}

    # Determine which generators to run
    if "all" in names:
        to_run = EXECUTION_ORDER
    else:
        # Sort by execution order to respect dependencies
        to_run = [name for name in EXECUTION_ORDER if name in names]
        # Add any names not in EXECUTION_ORDER (shouldn't happen, but be safe)
        for name in names:
            if name not in to_run and name in GENERATORS:
                to_run.append(name)

    for name in to_run:
        if name not in GENERATORS:
            print(f"Unknown generator: {name}")
            continue

        generator_class = GENERATORS[name]
        generator = generator_class(config)

        print(f"\n{'=' * 60}")
        print(f"Running: {generator.name}")
        print(f"{'=' * 60}")

        result = generator.run()
        results[name] = result

        if not result.success:
            print(f"FAILED: {name}")
            for error in result.errors:
                print(f"  Error: {error}")

    return results


def main(argv: List[str] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run World Ablaze map data generators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available generators:
  all                   Run all generators in dependency order
  landmass              Generate province/state landmass mappings
  province_connections  Generate province adjacency map
  province_positions    Generate province center coordinates
  province_terrain      Generate province terrain types
  railway_connections   Generate railway connection levels
  state_provinces       Generate state-to-province mappings
  state_vp_provinces    Generate state-to-VP-province mappings (for capitals)

Examples:
  python run_generators.py all --dry-run
  python run_generators.py province_terrain -v
  python run_generators.py landmass state_provinces
        """,
    )

    parser.add_argument(
        "generators",
        nargs="+",
        choices=list(GENERATORS.keys()) + ["all"],
        help="Generator(s) to run",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )
    parser.add_argument(
        "--map-dir",
        type=Path,
        default=Path("../map"),
        help="Path to map folder (default: ../map)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../common/scripted_effects"),
        help="Output directory (default: ../common/scripted_effects)",
    )
    parser.add_argument(
        "--states-dir",
        type=Path,
        default=Path("../history/states"),
        help="Path to states folder (default: ../history/states)",
    )

    args = parser.parse_args(argv)

    config = GeneratorConfig(
        map_dir=args.map_dir,
        output_dir=args.output_dir,
        states_dir=args.states_dir,
        verbose=args.verbose,
        debug=args.debug,
        dry_run=args.dry_run,
    )

    results = run_generators(args.generators, config)

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")

    success_count = sum(1 for r in results.values() if r.success)
    fail_count = len(results) - success_count

    for name, result in results.items():
        status = "OK" if result.success else "FAILED"
        output_info = ""
        if result.output_file:
            output_info = f" -> {result.output_file.name}"
        print(f"  {name}: {status}{output_info}")

    print(f"\nTotal: {success_count} succeeded, {fail_count} failed")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
