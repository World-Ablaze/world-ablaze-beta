"""Parser for Clausewitz script format - preserves raw text for reconstruction"""

from typing import List, Optional, Tuple
from .lexer import Lexer, Token, TokenType
from .ast_nodes import (
    ASTNode, FileNode, BlockNode, PropertyNode,
    VariableDefNode, CommentNode, InlineListNode, SourceSpan
)


class ParseError(Exception):
    """Error during parsing"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.token = token
        if token:
            super().__init__(f"{message} at line {token.line}, column {token.column}")
        else:
            super().__init__(message)


class Parser:
    """
    Parser for Clausewitz script format.

    This parser preserves the raw text of each construct to enable
    accurate reconstruction when writing output files.

    Strategy: For each node, capture the raw_text from the source
    spanning from start to end position.
    """

    def __init__(self, content: str, filename: str = ""):
        self.content = content
        self.filename = filename
        self.tokens: List[Token] = []
        self.pos = 0

    def parse(self) -> FileNode:
        """Parse entire file into AST"""
        # Tokenize
        lexer = Lexer(self.content)
        self.tokens = lexer.tokenize()
        self.pos = 0

        file_node = FileNode()
        file_node.span = SourceSpan(0, len(self.content))
        file_node.raw_text = self.content

        # Parse header lines (#!gfx:... or leading comments)
        file_node.header_lines = self._parse_header_lines()

        # Skip whitespace/newlines to find first real content
        self._skip_trivia()

        # Parse top-level variable definitions and root block
        while not self._is_eof():
            self._skip_trivia()
            if self._is_eof():
                break

            token = self._current()

            # Variable definition
            if token.type == TokenType.VARIABLE:
                var_node = self._parse_variable_def()
                if var_node:
                    file_node.variables.append(var_node)

            # Root block (technologies = { ... } or equipments = { ... })
            elif token.type == TokenType.IDENTIFIER:
                file_node.root_block = self._parse_block()
                break

            else:
                # Skip unknown tokens
                self._advance()

        return file_node

    def _parse_header_lines(self) -> List[str]:
        """Parse header lines like #!gfx:interface\\..."""
        headers = []
        while not self._is_eof():
            token = self._current()

            # Header comment starting with #!
            if token.type == TokenType.COMMENT and token.value.startswith('#!'):
                headers.append(token.value)
                self._advance()
                # Skip the newline after header
                if self._current().type == TokenType.NEWLINE:
                    self._advance()

            # Regular comment at top of file
            elif token.type == TokenType.COMMENT:
                headers.append(token.value)
                self._advance()
                if self._current().type == TokenType.NEWLINE:
                    self._advance()

            # Skip leading whitespace/newlines
            elif token.type in (TokenType.WHITESPACE, TokenType.NEWLINE):
                self._advance()

            else:
                # Non-header content found
                break

        return headers

    def _parse_variable_def(self) -> Optional[VariableDefNode]:
        """Parse: @name = value"""
        start_pos = self._current().start_pos

        var_token = self._expect(TokenType.VARIABLE)
        self._skip_whitespace()
        self._expect(TokenType.EQUALS)
        self._skip_whitespace()

        # Value can be number or identifier
        value_token = self._current()
        if value_token.type in (TokenType.NUMBER, TokenType.IDENTIFIER):
            self._advance()
        else:
            return None

        end_pos = value_token.end_pos

        node = VariableDefNode(
            raw_text=self.content[start_pos:end_pos],
            span=SourceSpan(start_pos, end_pos),
            name=var_token.value,
            value=value_token.value,
        )
        return node

    def _parse_block(self) -> BlockNode:
        """Parse: name = { children... }"""
        start_pos = self._current().start_pos

        # Block name
        name_token = self._expect(TokenType.IDENTIFIER)
        self._skip_whitespace()
        self._expect(TokenType.EQUALS)
        self._skip_whitespace()
        self._expect(TokenType.LBRACE)

        block = BlockNode(
            name=name_token.value,
            has_assignment=True,
        )

        # Parse children until closing brace
        while not self._is_eof():
            self._skip_trivia()

            if self._is_eof():
                break

            token = self._current()

            # End of block
            if token.type == TokenType.RBRACE:
                self._advance()
                break

            # Comment
            if token.type == TokenType.COMMENT:
                comment = CommentNode(
                    raw_text=token.value,
                    span=SourceSpan(token.start_pos, token.end_pos),
                    text=token.value,
                )
                block.children.append(comment)
                self._advance()
                continue

            # Variable definition
            if token.type == TokenType.VARIABLE:
                var_node = self._parse_variable_def()
                if var_node:
                    var_node.parent = block
                    block.children.append(var_node)
                continue

            # Identifier - could be block, property, or inline value
            if token.type == TokenType.IDENTIFIER:
                child = self._parse_block_or_property()
                if child:
                    child.parent = block
                    block.children.append(child)
                continue

            # Skip other tokens
            self._advance()

        end_pos = self.tokens[self.pos - 1].end_pos if self.pos > 0 else start_pos
        block.span = SourceSpan(start_pos, end_pos)
        block.raw_text = self.content[start_pos:end_pos]

        return block

    def _parse_block_or_property(self) -> Optional[ASTNode]:
        """
        Parse either:
        - Block: name = { ... }
        - Property: key = value
        - Property with inline list: key = { val1 val2 }
        """
        start_pos = self._current().start_pos

        name_token = self._expect(TokenType.IDENTIFIER)
        self._skip_whitespace()

        # Check what follows
        if self._is_eof() or self._current().type != TokenType.EQUALS:
            # Standalone identifier (rare, but handle it)
            return PropertyNode(
                raw_text=name_token.value,
                span=SourceSpan(start_pos, name_token.end_pos),
                key=name_token.value,
                value="",
            )

        self._expect(TokenType.EQUALS)
        self._skip_whitespace()

        token = self._current()

        # Block: name = { ... }
        if token.type == TokenType.LBRACE:
            # Need to determine if it's a real block or an inline list
            # Peek ahead to see what's inside
            if self._is_inline_list():
                return self._parse_inline_list_property(name_token, start_pos)
            else:
                # Rewind and parse as block
                # Actually we need to include the name in the block
                self._advance()  # consume {

                block = BlockNode(
                    name=name_token.value,
                    has_assignment=True,
                )

                # Parse children
                while not self._is_eof():
                    self._skip_trivia()

                    if self._is_eof():
                        break

                    t = self._current()

                    if t.type == TokenType.RBRACE:
                        self._advance()
                        break

                    if t.type == TokenType.COMMENT:
                        comment = CommentNode(
                            raw_text=t.value,
                            span=SourceSpan(t.start_pos, t.end_pos),
                            text=t.value,
                        )
                        block.children.append(comment)
                        self._advance()
                        continue

                    if t.type == TokenType.VARIABLE:
                        var_node = self._parse_variable_def()
                        if var_node:
                            var_node.parent = block
                            block.children.append(var_node)
                        continue

                    if t.type == TokenType.IDENTIFIER:
                        child = self._parse_block_or_property()
                        if child:
                            child.parent = block
                            block.children.append(child)
                        continue

                    self._advance()

                end_pos = self.tokens[self.pos - 1].end_pos if self.pos > 0 else start_pos
                block.span = SourceSpan(start_pos, end_pos)
                block.raw_text = self.content[start_pos:end_pos]
                return block

        # Property with value
        else:
            value = self._parse_value()
            end_pos = self.tokens[self.pos - 1].end_pos if self.pos > 0 else start_pos

            return PropertyNode(
                raw_text=self.content[start_pos:end_pos],
                span=SourceSpan(start_pos, end_pos),
                key=name_token.value,
                value=value,
            )

    def _is_inline_list(self) -> bool:
        """
        Check if current { starts an inline list vs a block.

        Inline list: { item1 item2 item3 } - no = inside, typically on one line
        Block: { key = value ... } - has = assignments
        """
        # Save position
        saved_pos = self.pos

        # Skip the {
        self._advance()
        self._skip_trivia()

        # Check content
        result = False
        depth = 1

        while not self._is_eof() and depth > 0:
            token = self._current()

            if token.type == TokenType.LBRACE:
                depth += 1
            elif token.type == TokenType.RBRACE:
                depth -= 1
            elif token.type == TokenType.EQUALS:
                # Found assignment - this is a block, not inline list
                result = False
                break

            # Check if we have multiple identifiers/values without =
            if token.type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.NUMBER):
                self._advance()
                self._skip_whitespace()
                next_tok = self._current()
                if next_tok.type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.NUMBER, TokenType.RBRACE):
                    # Multiple values or closing brace - likely inline list
                    result = True
                elif next_tok.type == TokenType.EQUALS:
                    result = False
                break

            self._advance()

        # Restore position
        self.pos = saved_pos
        return result

    def _parse_inline_list_property(self, name_token: Token, start_pos: int) -> PropertyNode:
        """Parse: key = { item1 item2 item3 }"""
        self._expect(TokenType.LBRACE)

        items = []
        while not self._is_eof():
            self._skip_trivia()

            token = self._current()

            if token.type == TokenType.RBRACE:
                self._advance()
                break

            if token.type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.NUMBER, TokenType.VARIABLE):
                items.append(token.value)
                self._advance()
            else:
                self._advance()

        end_pos = self.tokens[self.pos - 1].end_pos if self.pos > 0 else start_pos

        # Create as property with inline list representation
        list_str = "{ " + " ".join(items) + " }"

        return PropertyNode(
            raw_text=self.content[start_pos:end_pos],
            span=SourceSpan(start_pos, end_pos),
            key=name_token.value,
            value=list_str,
        )

    def _parse_value(self) -> str:
        """Parse a property value (string, number, identifier, or yes/no)"""
        token = self._current()

        if token.type in (TokenType.STRING, TokenType.NUMBER, TokenType.IDENTIFIER, TokenType.VARIABLE):
            self._advance()
            return token.value

        return ""

    def _current(self) -> Token:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, "", 0, 0, len(self.content), len(self.content))

    def _advance(self) -> Token:
        """Advance and return previous token"""
        token = self._current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        """Expect and consume a specific token type"""
        token = self._current()
        if token.type != token_type:
            raise ParseError(f"Expected {token_type.name}, got {token.type.name}", token)
        self._advance()
        return token

    def _skip_whitespace(self) -> None:
        """Skip whitespace tokens (not newlines or comments)"""
        while not self._is_eof() and self._current().type == TokenType.WHITESPACE:
            self._advance()

    def _skip_trivia(self) -> None:
        """Skip whitespace and newlines"""
        while not self._is_eof() and self._current().type in (TokenType.WHITESPACE, TokenType.NEWLINE):
            self._advance()

    def _is_eof(self) -> bool:
        """Check if at end of file"""
        return self.pos >= len(self.tokens) or self._current().type == TokenType.EOF


def parse_file(content: str, filename: str = "") -> FileNode:
    """Convenience function to parse file content"""
    parser = Parser(content, filename)
    return parser.parse()
