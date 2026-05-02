"""Output writer for AST - reconstructs Clausewitz script files"""

from typing import TextIO, Optional
from pathlib import Path
from io import StringIO
from .ast_nodes import (
    FileNode, BlockNode, PropertyNode, VariableDefNode,
    CommentNode, InlineListNode, ASTNode
)


class ASTWriter:
    """
    Writes AST back to Clausewitz script format.

    Strategy:
    - If raw_text is available and node wasn't modified, use raw_text
    - Otherwise, reconstruct from AST structure

    Output encoding: UTF-8 without BOM (HOI4 preference)
    """

    def __init__(self, indent_char: str = '\t'):
        self.indent_char = indent_char

    def write(self, ast: FileNode, output_path: Path) -> None:
        """Write AST to file"""
        content = self.to_string(ast)
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)

    def to_string(self, ast: FileNode) -> str:
        """Convert AST to string"""
        buffer = StringIO()
        self._write_file(ast, buffer)
        return buffer.getvalue()

    def _write_file(self, node: FileNode, out: TextIO) -> None:
        """Write file node"""
        # Write header lines (#!gfx:...)
        for header in node.header_lines:
            out.write(header)
            out.write('\n')

        # Write root block
        if node.root_block:
            self._write_block(node.root_block, out, depth=0)

        # Write trailer if any
        if node.trailer:
            out.write(node.trailer)

    def _write_block(self, node: BlockNode, out: TextIO, depth: int) -> None:
        """Write block node"""
        indent = self.indent_char * depth

        # If we have preserved raw_text and it's a leaf-ish block, use it
        if node.raw_text and self._should_use_raw_text(node):
            # Need to properly indent the raw text
            lines = node.raw_text.split('\n')
            for i, line in enumerate(lines):
                if i > 0:
                    out.write('\n')
                # First line gets current indent, others keep relative indent
                if i == 0:
                    out.write(indent)
                out.write(line.lstrip('\t') if i == 0 else line)
            out.write('\n')
            return

        # Block header
        out.write(f"{indent}{node.name} = {{\n")

        # Children
        for child in node.children:
            self._write_node(child, out, depth + 1)

        # Closing brace
        out.write(f"{indent}}}\n")

    def _write_node(self, node: ASTNode, out: TextIO, depth: int) -> None:
        """Write any AST node"""
        if isinstance(node, BlockNode):
            self._write_block(node, out, depth)
        elif isinstance(node, PropertyNode):
            self._write_property(node, out, depth)
        elif isinstance(node, VariableDefNode):
            self._write_variable(node, out, depth)
        elif isinstance(node, CommentNode):
            self._write_comment(node, out, depth)
        elif isinstance(node, InlineListNode):
            self._write_inline_list(node, out, depth)

    def _write_property(self, node: PropertyNode, out: TextIO, depth: int) -> None:
        """Write property node"""
        indent = self.indent_char * depth

        # Use raw_text if available
        if node.raw_text:
            out.write(f"{indent}{node.raw_text.strip()}\n")
        else:
            out.write(f"{indent}{node.key} = {node.value}\n")

    def _write_variable(self, node: VariableDefNode, out: TextIO, depth: int) -> None:
        """Write variable definition"""
        indent = self.indent_char * depth

        if node.raw_text:
            out.write(f"{indent}{node.raw_text.strip()}\n")
        else:
            out.write(f"{indent}{node.name} = {node.value}\n")

    def _write_comment(self, node: CommentNode, out: TextIO, depth: int) -> None:
        """Write comment"""
        indent = self.indent_char * depth
        out.write(f"{indent}{node.text}\n")

    def _write_inline_list(self, node: InlineListNode, out: TextIO, depth: int) -> None:
        """Write inline list"""
        indent = self.indent_char * depth
        items_str = " ".join(node.items)
        out.write(f"{indent}{{ {items_str} }}\n")

    def _should_use_raw_text(self, node: BlockNode) -> bool:
        """
        Determine if we should use raw_text for a block.

        We use raw_text for "definition" blocks (technologies, equipment)
        to preserve exact formatting, but not for the root container.
        """
        # Don't use raw_text for root blocks (technologies, equipments)
        if node.name in ('technologies', 'equipments'):
            return False

        # Use raw_text for definition blocks if available
        return bool(node.raw_text)


def write_ast(ast: FileNode, output_path: Path) -> None:
    """Convenience function to write AST to file"""
    writer = ASTWriter()
    writer.write(ast, output_path)


def ast_to_string(ast: FileNode) -> str:
    """Convenience function to convert AST to string"""
    writer = ASTWriter()
    return writer.to_string(ast)
