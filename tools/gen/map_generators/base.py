"""
Abstract base class for all HOI4 map data generators.

Provides common structure for:
- Configuration management
- Input validation
- Output writing
- Step-by-step processing with logging
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import setup_logging, write_file_utf8


@dataclass
class GeneratorConfig:
    """Configuration for a generator run."""

    map_dir: Path = field(default_factory=lambda: Path("../map"))
    output_dir: Path = field(default_factory=lambda: Path("../common/scripted_effects"))
    states_dir: Path = field(default_factory=lambda: Path("../history/states"))
    verbose: bool = False
    debug: bool = False
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Convert string paths to Path objects if needed."""
        if isinstance(self.map_dir, str):
            self.map_dir = Path(self.map_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.states_dir, str):
            self.states_dir = Path(self.states_dir)


@dataclass
class GeneratorResult:
    """Result of a generator run."""

    success: bool = True
    output_file: Optional[Path] = None
    items_processed: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class BaseMapGenerator(ABC):
    """
    Abstract base class for map data generators.

    Subclasses must implement:
    - name: Property returning the generator name
    - description: Property returning description for help text
    - get_output_filename(): Return output filename
    - get_required_inputs(): Return list of required input files
    - process(): Main processing logic
    - format_output(): Format data for output file
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """
        Initialize the generator.

        Args:
            config: Generator configuration. Uses defaults if not provided.
        """
        self.config = config or GeneratorConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._step_count = 0

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the generator name (used in CLI)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return description for help text."""
        pass

    @abstractmethod
    def get_output_filename(self) -> str:
        """Return the output filename."""
        pass

    @abstractmethod
    def get_required_inputs(self) -> List[Path]:
        """Return list of required input file paths."""
        pass

    @abstractmethod
    def process(self) -> Dict[str, Any]:
        """
        Main processing logic.

        Returns:
            Dictionary of processed data to be formatted for output.
        """
        pass

    @abstractmethod
    def format_output(self, data: Dict[str, Any]) -> str:
        """
        Format processed data for output file.

        Args:
            data: Processed data from process().

        Returns:
            Formatted string content for output file.
        """
        pass

    def log_step(self, message: str) -> None:
        """
        Log a processing step with step number.

        Args:
            message: Step description.
        """
        self._step_count += 1
        self.logger.info(f"Step {self._step_count}: {message}")

    def validate_inputs(self) -> List[str]:
        """
        Validate that all required input files exist.

        Returns:
            List of error messages (empty if all valid).
        """
        errors = []
        for input_path in self.get_required_inputs():
            if not input_path.exists():
                errors.append(f"Required file not found: {input_path}")
        return errors

    def get_output_path(self) -> Path:
        """
        Get the full output file path.

        Returns:
            Path to output file.
        """
        return self.config.output_dir / self.get_output_filename()

    def run(self) -> GeneratorResult:
        """
        Run the generator.

        Returns:
            GeneratorResult with success/failure and statistics.
        """
        result = GeneratorResult()
        self._step_count = 0

        # Setup logging
        setup_logging(
            verbose=self.config.verbose,
            debug=self.config.debug,
        )

        self.logger.info(f"Running {self.name}...")

        # Validate inputs
        errors = self.validate_inputs()
        if errors:
            for error in errors:
                self.logger.error(error)
            result.success = False
            result.errors = errors
            return result

        try:
            # Process data
            data = self.process()

            # Format output
            output_content = self.format_output(data)

            # Write output
            output_path = self.get_output_path()

            if self.config.dry_run:
                self.logger.info(f"DRY RUN: Would write to {output_path}")
                lines = output_content.count("\n")
                self.logger.info(f"Output would be {lines} lines")
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                write_file_utf8(output_path, output_content)
                self.logger.info(f"Wrote output to {output_path}")
                result.output_file = output_path

            result.success = True
            self.logger.info("Done!")

        except Exception as e:
            self.logger.error(f"Error during processing: {e}")
            result.success = False
            result.errors.append(str(e))
            if self.config.debug:
                import traceback
                traceback.print_exc()

        return result
