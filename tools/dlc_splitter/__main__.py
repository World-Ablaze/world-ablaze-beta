#!/usr/bin/env python3
"""
HOI4 DLC Content Splitter

Splits technology and equipment files based on DLC content.
Creates non-DLC variant files while leaving originals unchanged.

Usage:
    python -m dlc_splitter <input_path> [options]
    python -m dlc_splitter common/technologies/air_techs_eng.txt --dry-run
    python -m dlc_splitter common/technologies/ --dlc "By Blood Alone"
    python -m dlc_splitter common/units/equipment/ -v
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional

from .parser import Parser, ParseError
from .dlc_detector import DLCDetector
from .splitter import FileSplitter
from .writer import ASTWriter, ast_to_string
from .config import DEFAULT_DLCS


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Configure logging"""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def find_files(path: Path, recursive: bool = True) -> List[Path]:
    """Find all .txt files in directory or return single file"""
    if path.is_file():
        return [path] if path.suffix == '.txt' else []

    if recursive:
        return list(path.rglob('*.txt'))
    else:
        return list(path.glob('*.txt'))


def read_file(path: Path) -> str:
    """Read file content, handling BOM if present"""
    # Try UTF-8-sig first to strip BOM if present
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback to latin-1
        with open(path, 'r', encoding='latin-1') as f:
            return f.read()


def process_file(
    input_path: Path,
    output_dir: Optional[Path],
    dlcs: List[str],
    dry_run: bool = False,
    verbose: bool = False,
) -> Dict[str, any]:
    """
    Process a single file and create non-DLC variants.

    Returns statistics about the processing.
    """
    logger = logging.getLogger(__name__)
    stats = {
        'files_created': 0,
        'files_skipped': 0,
        'errors': [],
    }

    # Read file
    try:
        content = read_file(input_path)
    except Exception as e:
        stats['errors'].append(f"Failed to read {input_path}: {e}")
        return stats

    # Parse
    try:
        parser = Parser(content, str(input_path))
        ast = parser.parse()
    except ParseError as e:
        stats['errors'].append(f"Parse error in {input_path}: {e}")
        return stats
    except Exception as e:
        stats['errors'].append(f"Unexpected error parsing {input_path}: {e}")
        return stats

    # Split
    splitter = FileSplitter(dlcs)
    try:
        split_results = splitter.split(ast, input_path)
    except Exception as e:
        stats['errors'].append(f"Split error in {input_path}: {e}")
        return stats

    if not split_results:
        logger.debug(f"No non-DLC content found in {input_path}")
        stats['files_skipped'] += 1
        return stats

    # Determine output directory
    if output_dir is None:
        output_dir = input_path.parent

    # Write outputs
    writer = ASTWriter()

    for filename, file_ast in split_results.items():
        output_path = output_dir / filename

        if dry_run:
            logger.info(f"Would create: {output_path}")
            if verbose:
                content_preview = ast_to_string(file_ast)
                lines = content_preview.split('\n')
                preview_lines = lines[:20]
                logger.info(f"Content preview ({len(lines)} lines total):")
                for line in preview_lines:
                    logger.info(f"  {line}")
                if len(lines) > 20:
                    logger.info(f"  ... ({len(lines) - 20} more lines)")
        else:
            try:
                writer.write(file_ast, output_path)
                logger.info(f"Created: {output_path}")
            except Exception as e:
                stats['errors'].append(f"Failed to write {output_path}: {e}")
                continue

        stats['files_created'] += 1

    return stats


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Split HOI4 mod files based on DLC content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m dlc_splitter air_techs_eng.txt --dry-run
  python -m dlc_splitter common/technologies/ --dry-run -v
  python -m dlc_splitter common/units/equipment/ --dlc "By Blood Alone"
  python -m dlc_splitter . --recursive
        """
    )

    parser.add_argument(
        'input',
        type=Path,
        help='Input file or directory to process'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=None,
        help='Output directory (default: same as input file)'
    )

    parser.add_argument(
        '--dlc',
        nargs='+',
        default=DEFAULT_DLCS,
        help=f'Target DLCs to split (default: {DEFAULT_DLCS})'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debug output (very verbose)'
    )

    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        default=True,
        help='Recursively process directories (default: True)'
    )

    parser.add_argument(
        '--no-recursive',
        action='store_false',
        dest='recursive',
        help='Do not recursively process directories'
    )

    parser.add_argument(
        '--exclude',
        nargs='*',
        default=['modules'],
        help='Directory patterns to exclude (default: modules)'
    )

    args = parser.parse_args(argv)
    setup_logging(args.verbose, args.debug)
    logger = logging.getLogger(__name__)

    # Validate input
    input_path = args.input
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return 1

    # Find files to process
    files = find_files(input_path, args.recursive)

    # Filter out excluded patterns
    if args.exclude:
        original_count = len(files)
        files = [f for f in files
                 if not any(excl in str(f) for excl in args.exclude)]
        excluded_count = original_count - len(files)
        if excluded_count > 0:
            logger.debug(f"Excluded {excluded_count} files matching patterns: {args.exclude}")

    if not files:
        logger.warning(f"No .txt files found in {input_path}")
        return 0

    logger.info(f"Processing {len(files)} file(s) for DLCs: {args.dlc}")
    if args.dry_run:
        logger.info("DRY RUN - no files will be created")

    # Process files
    total_stats = {
        'files_processed': 0,
        'files_created': 0,
        'files_skipped': 0,
        'errors': [],
    }

    for file_path in files:
        logger.debug(f"Processing: {file_path}")
        stats = process_file(
            file_path,
            args.output,
            args.dlc,
            args.dry_run,
            args.verbose,
        )

        total_stats['files_processed'] += 1
        total_stats['files_created'] += stats['files_created']
        total_stats['files_skipped'] += stats['files_skipped']
        total_stats['errors'].extend(stats['errors'])

    # Summary
    print(f"\nSummary:")
    print(f"  Files processed: {total_stats['files_processed']}")
    print(f"  Non-DLC files created: {total_stats['files_created']}")
    print(f"  Files with no non-DLC content: {total_stats['files_skipped']}")

    if total_stats['errors']:
        print(f"  Errors: {len(total_stats['errors'])}")
        for error in total_stats['errors']:
            logger.error(error)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
