"""
Province position generator for World Ablaze AI.

Reads HOI4 map files (definition.csv and provinces.bmp) and generates
precomputed province position mappings for pathfinding.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import parse_definition_for_colors
from map_generators.base import BaseMapGenerator, GeneratorConfig

try:
    from PIL import Image
except ImportError:
    raise ImportError(
        "Pillow is required for this generator. Install with: pip install Pillow"
    )


def calculate_province_positions(
    provinces_bmp_path: Path,
    color_to_province: Dict[Tuple[int, int, int], int],
    logger,
) -> Dict[int, Tuple[int, int]]:
    """
    Calculate province center positions from provinces.bmp.

    Args:
        provinces_bmp_path: Path to the provinces.bmp file.
        color_to_province: Mapping of (r, g, b) -> province_id.
        logger: Logger instance.

    Returns:
        Dictionary mapping province_id -> (x, y) center position.
    """
    logger.info(f"Loading provinces.bmp from {provinces_bmp_path}...")

    # Accumulators for calculating centroids
    province_x_sum: Dict[int, int] = defaultdict(int)
    province_y_sum: Dict[int, int] = defaultdict(int)
    province_count: Dict[int, int] = defaultdict(int)

    with Image.open(provinces_bmp_path) as img:
        width, height = img.size
        logger.info(f"Map size: {width} x {height}")

        if img.mode != "RGB":
            img = img.convert("RGB")

        pixels = img.load()
        for y in range(height):
            if y % 500 == 0:
                logger.debug(f"Processing row {y}/{height}")

            for x in range(width):
                pixel = pixels[x, y]
                if pixel in color_to_province:
                    province_id = color_to_province[pixel]
                    province_x_sum[province_id] += x
                    # HOI4 uses inverted Y (0 at top)
                    province_y_sum[province_id] += height - 1 - y
                    province_count[province_id] += 1

    # Calculate centroids
    province_positions: Dict[int, Tuple[int, int]] = {}
    for province_id in province_count:
        count = province_count[province_id]
        if count > 0:
            avg_x = province_x_sum[province_id] // count
            avg_y = province_y_sum[province_id] // count
            province_positions[province_id] = (avg_x, avg_y)

    logger.info(f"Calculated positions for {len(province_positions)} provinces")
    return province_positions


class ProvincePositionsGenerator(BaseMapGenerator):
    """Generator for province center coordinate mappings."""

    @property
    def name(self) -> str:
        return "province_positions"

    @property
    def description(self) -> str:
        return "Generate province positions for World Ablaze AI pathfinding"

    def get_output_filename(self) -> str:
        return "WA_AI_MAP_province_coordinates.txt"

    def get_required_inputs(self) -> List[Path]:
        return [
            self.config.map_dir / "definition.csv",
            self.config.map_dir / "provinces.bmp",
        ]

    def process(self) -> Dict[str, Any]:
        """Parse map files and calculate province positions."""
        map_dir = self.config.map_dir

        self.log_step("Parsing definition.csv for land provinces...")
        color_to_province = parse_definition_for_colors(
            map_dir / "definition.csv", land_only=True
        )

        self.log_step("Calculating province positions from provinces.bmp...")
        province_positions = calculate_province_positions(
            map_dir / "provinces.bmp", color_to_province, self.logger
        )

        return {"province_positions": province_positions}

    def format_output(self, data: Dict[str, Any]) -> str:
        """Format position data for output file."""
        province_positions = data["province_positions"]

        lines: List[str] = []
        lines.append("WA_AI_MAP_set_province_pos = {")

        for province_id in sorted(province_positions.keys()):
            x, y = province_positions[province_id]
            lines.append(
                f"    set_variable = {{ global.WA_AI_MAP_province_x_pos^{province_id} = {x} }}"
                f"     set_variable = {{ global.WA_AI_MAP_province_y_pos^{province_id} = {y} }}"
            )

        lines.append("}")

        return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate province positions for World Ablaze AI pathfinding."
    )
    parser.add_argument(
        "--map-dir",
        type=Path,
        default=Path("../map"),
        help="Path to the map folder",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("../common/scripted_effects"),
        help="Output directory",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    config = GeneratorConfig(
        map_dir=args.map_dir,
        output_dir=args.output_dir,
        verbose=args.verbose,
        dry_run=args.dry_run,
    )

    generator = ProvincePositionsGenerator(config)
    result = generator.run()

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
