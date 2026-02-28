"""DLC context detection and propagation for AST nodes"""

from typing import Dict, List, Set, Optional
from .ast_nodes import (
    ASTNode, FileNode, BlockNode, PropertyNode,
    VariableDefNode, CommentNode, DLCContext
)
from .config import CONDITION_BLOCKS, CONTAINER_BLOCKS


class DLCDetector:
    """
    Analyzes AST to detect and propagate DLC context.

    Rules:
    1. has_dlc = "DLC Name" in allow_branch/can_be_produced -> DLC_REQUIRED
    2. NOT = { has_dlc = "DLC Name" } -> DLC_EXCLUDED
    3. No DLC check -> NEUTRAL
    4. Tech tree inheritance: techs linked via path = { leads_to_tech = X }
       inherit DLC context from their parent tech
    5. Sub-technologies inherit parent context
    """

    def __init__(self, target_dlcs: List[str]):
        self.target_dlcs = set(target_dlcs)
        # Maps tech name -> BlockNode
        self.tech_nodes: Dict[str, BlockNode] = {}
        # Maps tech name -> list of child tech names (from path leads_to_tech)
        self.tech_children: Dict[str, List[str]] = {}
        # Maps tech name -> parent tech name
        self.tech_parents: Dict[str, str] = {}
        # Maps tech name -> list of sub_technologies names
        self.sub_techs: Dict[str, List[str]] = {}

    def analyze(self, ast: FileNode) -> None:
        """Walk AST and set dlc_context on all nodes"""
        if ast.root_block:
            # Phase 1: Build the tech tree graph
            self._build_tech_graph(ast.root_block)

            # Phase 2: Detect DLC context on each tech (without inheritance)
            self._detect_local_dlc_context(ast.root_block)

            # Phase 3: Propagate DLC context through tech tree
            self._propagate_through_tech_tree(ast.root_block)

            # Phase 4: Propagate to nested children
            self._propagate_to_nested_children(ast.root_block)

    def _build_tech_graph(self, root: BlockNode) -> None:
        """
        Build a graph of tech relationships.

        Extracts:
        - path = { leads_to_tech = X } links
        - sub_technologies = { X Y Z } links
        """
        for child in root.children:
            if isinstance(child, BlockNode):
                tech_name = child.name
                self.tech_nodes[tech_name] = child
                self.tech_children[tech_name] = []
                self.sub_techs[tech_name] = []

                # Scan for path blocks and sub_technologies
                for inner in child.children:
                    if isinstance(inner, BlockNode):
                        if inner.name == 'path':
                            # Look for leads_to_tech property
                            for prop in inner.children:
                                if isinstance(prop, PropertyNode) and prop.key == 'leads_to_tech':
                                    target_tech = prop.value.strip('"')
                                    self.tech_children[tech_name].append(target_tech)
                                    # Track parent relationship
                                    if target_tech not in self.tech_parents:
                                        self.tech_parents[target_tech] = tech_name

                        elif inner.name == 'sub_technologies':
                            # sub_technologies = { tech1 tech2 tech3 }
                            # These are parsed as BlockNode with PropertyNode children
                            # where each child has key=tech_name and empty value
                            for sub_child in inner.children:
                                if isinstance(sub_child, PropertyNode):
                                    sub_name = sub_child.key
                                    self.sub_techs[tech_name].append(sub_name)
                                    if sub_name not in self.tech_parents:
                                        self.tech_parents[sub_name] = tech_name

                    elif isinstance(inner, PropertyNode):
                        if inner.key == 'sub_technologies':
                            # Parse the inline list
                            subs = self._parse_inline_list(inner.value)
                            self.sub_techs[tech_name].extend(subs)
                            for sub in subs:
                                if sub not in self.tech_parents:
                                    self.tech_parents[sub] = tech_name

    def _parse_inline_list(self, value: str) -> List[str]:
        """Parse { item1 item2 item3 } into list of items"""
        if not value:
            return []
        # Remove braces and split
        content = value.strip()
        if content.startswith('{') and content.endswith('}'):
            content = content[1:-1].strip()
        return content.split()

    def _detect_local_dlc_context(self, root: BlockNode) -> None:
        """
        Detect DLC context on each tech based on its own allow_branch/can_be_produced.
        Does not consider inheritance yet.
        """
        root.dlc_context = {dlc: DLCContext.NEUTRAL for dlc in self.target_dlcs}

        for child in root.children:
            if isinstance(child, BlockNode):
                # Initialize as neutral
                local_context = {dlc: DLCContext.NEUTRAL for dlc in self.target_dlcs}

                # Look for condition blocks with DLC checks
                for inner in child.children:
                    if isinstance(inner, BlockNode) and inner.name in CONDITION_BLOCKS:
                        dlc_conditions = self._scan_condition_block(inner)
                        local_context.update(dlc_conditions)

                child.dlc_context = local_context

    def _propagate_through_tech_tree(self, root: BlockNode) -> None:
        """
        Propagate DLC context through the tech tree.

        Techs inherit DLC context from their parent in the tech tree
        (via path leads_to_tech or sub_technologies).
        """
        # Find root techs (those with no parent or with explicit DLC checks)
        root_techs = set()
        for tech_name, node in self.tech_nodes.items():
            has_dlc_check = any(
                ctx != DLCContext.NEUTRAL
                for ctx in node.dlc_context.values()
            )
            if has_dlc_check:
                root_techs.add(tech_name)

        # Propagate from each root tech
        visited = set()
        for root_tech in root_techs:
            self._propagate_from_tech(root_tech, visited)

        # Also propagate for techs that are children but whose parent wasn't a root
        # (they might inherit from grandparent)
        for tech_name in self.tech_nodes:
            if tech_name not in visited:
                self._propagate_from_tech(tech_name, visited)

    def _propagate_from_tech(self, tech_name: str, visited: Set[str]) -> None:
        """Propagate DLC context from a tech to all its descendants"""
        if tech_name in visited:
            return
        if tech_name not in self.tech_nodes:
            return

        visited.add(tech_name)
        node = self.tech_nodes[tech_name]
        parent_context = dict(node.dlc_context)

        # Get children from path leads_to_tech
        children = self.tech_children.get(tech_name, [])

        # Get sub_technologies
        sub_techs = self.sub_techs.get(tech_name, [])

        all_children = set(children + sub_techs)

        for child_name in all_children:
            if child_name in self.tech_nodes:
                child_node = self.tech_nodes[child_name]

                # Inherit parent's non-NEUTRAL context
                for dlc, ctx in parent_context.items():
                    if ctx != DLCContext.NEUTRAL:
                        # Only inherit if child doesn't have its own explicit check
                        child_ctx = child_node.dlc_context.get(dlc, DLCContext.NEUTRAL)
                        if child_ctx == DLCContext.NEUTRAL:
                            child_node.dlc_context[dlc] = ctx

                # Recursively propagate
                self._propagate_from_tech(child_name, visited)

    def _propagate_to_nested_children(self, root: BlockNode) -> None:
        """
        Final pass: propagate DLC context to all nested children of each tech.
        This handles the inner blocks like enable_equipments, path, ai_will_do, etc.
        """
        for child in root.children:
            if isinstance(child, BlockNode):
                self._propagate_context(child, child.dlc_context)

    def _propagate_context(self, node: BlockNode, context: Dict[str, DLCContext]) -> None:
        """Propagate DLC context to all descendants"""
        node.dlc_context = dict(context)

        for child in node.children:
            child.dlc_context = dict(context)
            if isinstance(child, BlockNode):
                self._propagate_context(child, context)

    def _scan_condition_block(self, block: BlockNode) -> Dict[str, DLCContext]:
        """
        Scan a condition block (allow_branch, can_be_produced, etc.) for DLC checks.

        Handles:
        - has_dlc = "DLC Name"
        - NOT = { has_dlc = "DLC Name" }
        """
        conditions: Dict[str, DLCContext] = {}

        for child in block.children:
            # Direct has_dlc property
            if isinstance(child, PropertyNode) and child.key == 'has_dlc':
                dlc_name = self._extract_dlc_name(child.value)
                if dlc_name in self.target_dlcs:
                    conditions[dlc_name] = DLCContext.DLC_REQUIRED

            # NOT block containing has_dlc
            elif isinstance(child, BlockNode) and child.name == 'NOT':
                for not_child in child.children:
                    if isinstance(not_child, PropertyNode) and not_child.key == 'has_dlc':
                        dlc_name = self._extract_dlc_name(not_child.value)
                        if dlc_name in self.target_dlcs:
                            conditions[dlc_name] = DLCContext.DLC_EXCLUDED

            # Nested blocks (OR, AND, etc.) - recurse
            elif isinstance(child, BlockNode) and child.name in ('OR', 'AND', 'if', 'else', 'else_if', 'limit'):
                nested_conditions = self._scan_condition_block(child)
                # Nested conditions can be complex - for simplicity, take them as-is
                for dlc, ctx in nested_conditions.items():
                    if dlc not in conditions:
                        conditions[dlc] = ctx

        return conditions

    def _extract_dlc_name(self, value: str) -> str:
        """Extract DLC name from property value, removing quotes"""
        return value.strip('"')


def detect_dlc_context(ast: FileNode, target_dlcs: List[str]) -> None:
    """Convenience function to detect DLC context in AST"""
    detector = DLCDetector(target_dlcs)
    detector.analyze(ast)
