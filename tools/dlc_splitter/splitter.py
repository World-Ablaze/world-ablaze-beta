"""File splitting logic based on DLC context"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
from .ast_nodes import (
    FileNode, BlockNode, PropertyNode, VariableDefNode,
    CommentNode, ASTNode, DLCContext, clone_node
)
from .dlc_detector import DLCDetector
from .config import DLC_SHORT_NAMES

logger = logging.getLogger(__name__)


class FileSplitter:
    """
    Splits AST content based on DLC context.

    Split behavior:
    - DLC_REQUIRED content -> stays in original file ONLY
    - DLC_EXCLUDED content -> moves to non-DLC file ONLY
    - NEUTRAL content -> stays in original file ONLY (no duplication)

    Both original and non-DLC files are generated to avoid duplicates.
    Each tech/equipment entry exists in exactly ONE file.
    """

    def __init__(self, target_dlcs: List[str]):
        self.target_dlcs = target_dlcs
        self.dlc_detector = DLCDetector(target_dlcs)

    def split(self, ast: FileNode, source_path: Path) -> Dict[str, FileNode]:
        """
        Split AST into original (DLC) and non-DLC file variants.

        Args:
            ast: Parsed AST with DLC context already analyzed
            source_path: Original source file path

        Returns:
            Dict mapping output filename to filtered AST.
            Includes:
            - Original filename -> AST with DLC_EXCLUDED content removed
            - Non-DLC filenames -> AST with only DLC_EXCLUDED content
        """
        # Ensure DLC context is analyzed
        self.dlc_detector.analyze(ast)

        results: Dict[str, FileNode] = {}

        # Track which DLCs affect this file
        relevant_dlcs = []

        for dlc in self.target_dlcs:
            # Only process if this file has DLC-specific content
            if not self._has_dlc_specific_content(ast, dlc):
                continue

            # Check file state BEFORE processing
            file_state = self._analyze_file_state(ast, dlc)

            # Skip if file is already in post-split state (prevents data loss)
            if file_state in ("DLC_ONLY", "NON_DLC_ONLY"):
                logger.warning(
                    f"File {source_path.name} appears to be already split "
                    f"(state: {file_state}). Skipping to prevent data loss. "
                    f"To re-split, ensure the source file contains BOTH DLC-required "
                    f"and DLC-excluded content."
                )
                return {}  # Return empty to prevent any processing

            # Only proceed if file is in PRE_SPLIT state
            if file_state != "PRE_SPLIT":
                logger.debug(f"File {source_path.name} has no mixed DLC content (state: {file_state})")
                continue

            relevant_dlcs.append(dlc)

            # Generate non-DLC filename (returns None if already a non-DLC file)
            non_dlc_filename = self._generate_non_dlc_filename(source_path, dlc)

            # Skip if this is already a non-DLC file for this DLC
            if non_dlc_filename is None:
                continue

            # Filter AST for non-DLC version (only DLC_EXCLUDED content)
            filtered_ast = self._filter_for_non_dlc(ast, dlc)

            if filtered_ast and self._has_meaningful_content(filtered_ast):
                results[non_dlc_filename] = filtered_ast

        # Generate modified original file (with DLC_EXCLUDED content removed)
        if relevant_dlcs:
            original_filename = source_path.name
            original_ast = self._filter_for_dlc(ast, relevant_dlcs)
            if original_ast:
                results[original_filename] = original_ast

        # Validate split completeness (ensure no content was lost)
        if results and not self._validate_split_completeness(ast, results):
            logger.error(
                f"Content validation failed for {source_path.name}! "
                f"Some technologies may have been lost during split. "
                f"Split operation aborted."
            )
            return {}  # Return empty dict to prevent writing incomplete split

        return results

    def _has_dlc_specific_content(self, ast: FileNode, dlc_name: str) -> bool:
        """
        Check if AST has any DLC-specific content for the given DLC.

        Returns True only if the file has content that is either:
        - DLC_REQUIRED (has_dlc = "X") - content that requires the DLC
        - DLC_EXCLUDED (NOT = { has_dlc = "X" }) - content for non-DLC users

        If the file has only NEUTRAL content for this DLC, returns False
        because that DLC is irrelevant to this file.
        """
        if not ast.root_block:
            return False

        for child in ast.root_block.children:
            if isinstance(child, BlockNode):
                ctx = child.dlc_context.get(dlc_name, DLCContext.NEUTRAL)
                # Only count DLC_REQUIRED or DLC_EXCLUDED as "DLC-specific"
                if ctx in (DLCContext.DLC_REQUIRED, DLCContext.DLC_EXCLUDED):
                    return True

        return False

    def _has_meaningful_content(self, ast: FileNode) -> bool:
        """Check if AST has meaningful content (not just empty blocks)"""
        if not ast.root_block:
            return False

        # Check if root block has any non-comment children
        for child in ast.root_block.children:
            if isinstance(child, BlockNode):
                return True

        return False

    def _analyze_file_state(self, ast: FileNode, dlc_name: str) -> str:
        """
        Analyze if file is in pre-split, post-split, or neutral state.

        Returns:
            "PRE_SPLIT": Has both DLC_REQUIRED and DLC_EXCLUDED content (needs splitting)
            "DLC_ONLY": Has only DLC_REQUIRED content (already split original)
            "NON_DLC_ONLY": Has only DLC_EXCLUDED content (already split non-DLC)
            "NEUTRAL_ONLY": Has only NEUTRAL content (no DLC dependencies)
        """
        if not ast.root_block:
            return "NEUTRAL_ONLY"

        has_required = 0
        has_excluded = 0
        has_neutral = 0

        for child in ast.root_block.children:
            if isinstance(child, BlockNode):
                ctx = child.dlc_context.get(dlc_name, DLCContext.NEUTRAL)
                if ctx == DLCContext.DLC_REQUIRED:
                    has_required += 1
                elif ctx == DLCContext.DLC_EXCLUDED:
                    has_excluded += 1
                elif ctx == DLCContext.NEUTRAL:
                    has_neutral += 1

        if has_required > 0 and has_excluded > 0:
            return "PRE_SPLIT"
        elif has_required > 0 and has_excluded == 0:
            return "DLC_ONLY"
        elif has_required == 0 and has_excluded > 0:
            return "NON_DLC_ONLY"
        else:
            return "NEUTRAL_ONLY"

    def _validate_split_completeness(
        self,
        original_ast: FileNode,
        split_results: Dict[str, FileNode]
    ) -> bool:
        """
        Validate that split results contain all content from original.

        Returns:
            True if split is complete, False if content was lost
        """
        # Count tech definitions in original
        original_count = 0
        if original_ast.root_block:
            for child in original_ast.root_block.children:
                if isinstance(child, BlockNode):
                    original_count += 1

        # Count tech definitions in all split results
        split_count = 0
        for file_ast in split_results.values():
            if file_ast.root_block:
                for child in file_ast.root_block.children:
                    if isinstance(child, BlockNode):
                        split_count += 1

        if original_count != split_count:
            logger.error(
                f"Content count mismatch: original={original_count}, "
                f"split={split_count}"
            )
            return False

        return True

    def _filter_for_non_dlc(self, ast: FileNode, dlc_name: str) -> FileNode:
        """
        Create filtered AST for non-DLC file.

        Includes ONLY:
        - Nodes with DLC_EXCLUDED context for this DLC

        Excludes:
        - Nodes with DLC_REQUIRED context
        - Nodes with NEUTRAL context (these stay in original file)
        """
        # Clone the file structure
        filtered = FileNode(
            raw_text="",  # Will be regenerated
            header_lines=list(ast.header_lines),
            variables=[clone_node(v) for v in ast.variables],
            trailer=ast.trailer,
        )

        if ast.root_block:
            filtered.root_block = self._filter_block_non_dlc(ast.root_block, dlc_name)
            if filtered.root_block:
                filtered.root_block.parent = filtered

        return filtered

    def _filter_for_dlc(self, ast: FileNode, dlc_names: List[str]) -> FileNode:
        """
        Create filtered AST for original (DLC) file.

        Includes:
        - Nodes with DLC_REQUIRED context
        - Nodes with NEUTRAL context

        Excludes:
        - Nodes with DLC_EXCLUDED context for ANY of the target DLCs
        """
        # Clone the file structure
        filtered = FileNode(
            raw_text="",  # Will be regenerated
            header_lines=list(ast.header_lines),
            variables=[clone_node(v) for v in ast.variables],
            trailer=ast.trailer,
        )

        if ast.root_block:
            filtered.root_block = self._filter_block_dlc(ast.root_block, dlc_names)
            if filtered.root_block:
                filtered.root_block.parent = filtered

        return filtered

    def _filter_block_non_dlc(self, block: BlockNode, dlc_name: str) -> Optional[BlockNode]:
        """
        Filter block for non-DLC file - only include DLC_EXCLUDED content.
        """
        filtered = BlockNode(
            raw_text="",
            name=block.name,
            has_assignment=block.has_assignment,
            dlc_context=dict(block.dlc_context),
        )

        for child in block.children:
            # Comments: only include if adjacent to included content
            if isinstance(child, CommentNode):
                filtered.children.append(clone_node(child, filtered))
                continue

            # Variables always included
            if isinstance(child, VariableDefNode):
                filtered.children.append(clone_node(child, filtered))
                continue

            # For blocks (tech/equipment definitions), check DLC context
            if isinstance(child, BlockNode):
                ctx = child.dlc_context.get(dlc_name, DLCContext.NEUTRAL)

                # Only include DLC_EXCLUDED content in non-DLC file
                if ctx == DLCContext.DLC_EXCLUDED:
                    cloned = self._clone_and_clean_block(child, dlc_name, filtered)
                    if cloned:
                        filtered.children.append(cloned)
                continue

            # Properties - include
            if isinstance(child, PropertyNode):
                filtered.children.append(clone_node(child, filtered))

        return filtered

    def _filter_block_dlc(self, block: BlockNode, dlc_names: List[str]) -> Optional[BlockNode]:
        """
        Filter block for DLC (original) file - exclude DLC_EXCLUDED content.
        Keep DLC_REQUIRED and NEUTRAL content.
        """
        filtered = BlockNode(
            raw_text="",
            name=block.name,
            has_assignment=block.has_assignment,
            dlc_context=dict(block.dlc_context),
        )

        for child in block.children:
            # Comments always included
            if isinstance(child, CommentNode):
                filtered.children.append(clone_node(child, filtered))
                continue

            # Variables always included
            if isinstance(child, VariableDefNode):
                filtered.children.append(clone_node(child, filtered))
                continue

            # For blocks (tech/equipment definitions), check DLC context
            if isinstance(child, BlockNode):
                # Check if excluded for ANY of the target DLCs
                is_excluded = False
                for dlc_name in dlc_names:
                    ctx = child.dlc_context.get(dlc_name, DLCContext.NEUTRAL)
                    if ctx == DLCContext.DLC_EXCLUDED:
                        is_excluded = True
                        break

                if is_excluded:
                    # Skip - this goes to non-DLC file
                    continue

                # DLC_REQUIRED or NEUTRAL - include it
                cloned = self._clone_and_clean_block(child, dlc_names[0] if dlc_names else "", filtered)
                if cloned:
                    filtered.children.append(cloned)
                continue

            # Properties - include
            if isinstance(child, PropertyNode):
                filtered.children.append(clone_node(child, filtered))

        return filtered

    def _clone_and_clean_block(self, block: BlockNode, dlc_name: str, parent: ASTNode) -> BlockNode:
        """
        Clone a block and optionally clean up DLC-related conditions.

        For DLC_EXCLUDED blocks, we could remove the NOT = { has_dlc } check,
        but for safety we keep the original structure intact.
        """
        cloned = BlockNode(
            raw_text=block.raw_text,  # Preserve raw text for now
            span=block.span,
            name=block.name,
            has_assignment=block.has_assignment,
            dlc_context=dict(block.dlc_context),
            parent=parent,
        )

        for child in block.children:
            if isinstance(child, CommentNode):
                cloned.children.append(clone_node(child, cloned))
            elif isinstance(child, VariableDefNode):
                cloned.children.append(clone_node(child, cloned))
            elif isinstance(child, PropertyNode):
                cloned.children.append(clone_node(child, cloned))
            elif isinstance(child, BlockNode):
                # Recursively clone nested blocks
                nested = self._clone_and_clean_block(child, dlc_name, cloned)
                cloned.children.append(nested)

        return cloned

    def _generate_non_dlc_filename(self, source_path: Path, dlc_name: str) -> Optional[str]:
        """
        Generate filename for non-DLC version.

        Pattern: {base}_non_{dlc}_{country}.txt
        Example: air_techs_eng.txt -> air_techs_non_bba_eng.txt

        For files without country code:
        Example: armor.txt -> armor_non_nsb.txt

        Returns None if file is already a non-DLC version for this DLC.
        """
        stem = source_path.stem  # e.g., "air_techs_eng" or "armor"
        dlc_short = DLC_SHORT_NAMES.get(dlc_name, dlc_name.lower().replace(" ", "_"))

        # Check if file is already a non-DLC version (contains _non_{dlc})
        non_dlc_marker = f"_non_{dlc_short}"
        if non_dlc_marker in stem:
            # Already a non-DLC file for this DLC, return None to skip
            return None

        # Try to detect country code (last segment, typically 3 chars)
        parts = stem.rsplit('_', 1)

        if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isalpha():
            # Has country code: air_techs_eng -> air_techs_non_bba_eng
            base, country = parts
            return f"{base}_non_{dlc_short}_{country}.txt"
        else:
            # No country code: armor -> armor_non_nsb
            return f"{stem}_non_{dlc_short}.txt"


def split_file(ast: FileNode, source_path: Path, target_dlcs: List[str]) -> Dict[str, FileNode]:
    """Convenience function to split a file"""
    splitter = FileSplitter(target_dlcs)
    return splitter.split(ast, source_path)
