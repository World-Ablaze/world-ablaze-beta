"""AST node definitions for Clausewitz script parsing"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict
from enum import Enum, auto


class DLCContext(Enum):
    """DLC requirement context for a node"""
    NEUTRAL = auto()      # No DLC check - copy to both files
    DLC_REQUIRED = auto() # has_dlc = "DLC" - stays in original (DLC file)
    DLC_EXCLUDED = auto() # NOT = { has_dlc = "DLC" } - moves to non-DLC file


@dataclass
class SourceSpan:
    """Track original source position for formatting preservation"""
    start: int
    end: int

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    # Raw text from source (includes this node's content exactly as written)
    raw_text: str = ""
    # Source span in original file
    span: Optional[SourceSpan] = None
    # DLC context per DLC name (inherited from parent if not explicitly set)
    dlc_context: Dict[str, DLCContext] = field(default_factory=dict)
    # Reference to parent for context inheritance
    parent: Optional['ASTNode'] = None


@dataclass
class CommentNode(ASTNode):
    """A comment line: # comment text"""
    text: str = ""


@dataclass
class VariableDefNode(ASTNode):
    """Variable definition: @1936 = 0"""
    name: str = ""   # @1936
    value: str = ""  # 0


@dataclass
class PropertyNode(ASTNode):
    """Simple key-value: research_cost = 2.5 or has_dlc = "By Blood Alone" """
    key: str = ""
    value: str = ""  # Raw value including quotes if string


@dataclass
class InlineListNode(ASTNode):
    """Inline list: { item1 item2 item3 }"""
    items: List[str] = field(default_factory=list)


@dataclass
class BlockNode(ASTNode):
    """
    Named block: technologies = { ... } or tech_name = { ... }

    Children can be:
    - BlockNode (nested blocks)
    - PropertyNode (key = value)
    - VariableDefNode (@var = value)
    - CommentNode (# comment)
    - InlineListNode ({ items })
    """
    name: str = ""
    children: List[Union['BlockNode', PropertyNode, VariableDefNode, CommentNode, InlineListNode]] = field(default_factory=list)
    # Whether this block has an assignment (name = { }) vs just braces
    has_assignment: bool = True


@dataclass
class FileNode(ASTNode):
    """Root node representing entire file"""
    # Header lines (like #!gfx:interface\...)
    header_lines: List[str] = field(default_factory=list)
    # Top-level variable definitions
    variables: List[VariableDefNode] = field(default_factory=list)
    # Root block (technologies = { ... } or equipments = { ... })
    root_block: Optional[BlockNode] = None
    # Any trailing content after root block
    trailer: str = ""


def clone_node(node: ASTNode, parent: Optional[ASTNode] = None) -> ASTNode:
    """Deep clone an AST node and its children"""
    if isinstance(node, FileNode):
        cloned = FileNode(
            raw_text=node.raw_text,
            span=node.span,
            dlc_context=dict(node.dlc_context),
            header_lines=list(node.header_lines),
            variables=[clone_node(v) for v in node.variables],
            root_block=clone_node(node.root_block) if node.root_block else None,
            trailer=node.trailer,
        )
        if cloned.root_block:
            cloned.root_block.parent = cloned
        return cloned

    elif isinstance(node, BlockNode):
        cloned = BlockNode(
            raw_text=node.raw_text,
            span=node.span,
            dlc_context=dict(node.dlc_context),
            parent=parent,
            name=node.name,
            has_assignment=node.has_assignment,
            children=[],
        )
        cloned.children = [clone_node(child, cloned) for child in node.children]
        return cloned

    elif isinstance(node, PropertyNode):
        return PropertyNode(
            raw_text=node.raw_text,
            span=node.span,
            dlc_context=dict(node.dlc_context),
            parent=parent,
            key=node.key,
            value=node.value,
        )

    elif isinstance(node, VariableDefNode):
        return VariableDefNode(
            raw_text=node.raw_text,
            span=node.span,
            dlc_context=dict(node.dlc_context),
            parent=parent,
            name=node.name,
            value=node.value,
        )

    elif isinstance(node, CommentNode):
        return CommentNode(
            raw_text=node.raw_text,
            span=node.span,
            dlc_context=dict(node.dlc_context),
            parent=parent,
            text=node.text,
        )

    elif isinstance(node, InlineListNode):
        return InlineListNode(
            raw_text=node.raw_text,
            span=node.span,
            dlc_context=dict(node.dlc_context),
            parent=parent,
            items=list(node.items),
        )

    else:
        raise ValueError(f"Unknown node type: {type(node)}")
