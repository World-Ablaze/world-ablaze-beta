"""Tokenizer for Clausewitz script format"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Iterator, List, Optional
import re


class TokenType(Enum):
    """Token types for Clausewitz script"""
    IDENTIFIER = auto()    # tech_name, key names, NOT, OR, AND
    STRING = auto()        # "By Blood Alone"
    NUMBER = auto()        # 2.5, 1936, -2
    EQUALS = auto()        # =
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LESS_THAN = auto()     # <
    GREATER_THAN = auto()  # >
    COMMENT = auto()       # # comment text (to end of line)
    NEWLINE = auto()       # \n
    WHITESPACE = auto()    # tabs, spaces (not newlines)
    VARIABLE = auto()      # @1936
    EOF = auto()


@dataclass
class Token:
    """A single token from the lexer"""
    type: TokenType
    value: str
    line: int
    column: int
    start_pos: int
    end_pos: int

    def __repr__(self) -> str:
        val = self.value[:20] + "..." if len(self.value) > 20 else self.value
        return f"Token({self.type.name}, {val!r}, L{self.line}:{self.column})"


class Lexer:
    """
    Tokenizer for Clausewitz script format.

    Preserves all whitespace and comments as separate tokens
    for accurate reconstruction of output.
    """

    def __init__(self, content: str):
        self.content = content
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(content)

    def tokenize(self) -> List[Token]:
        """Tokenize entire content and return list of tokens"""
        tokens = []
        while self.pos < self.length:
            token = self._next_token()
            if token:
                tokens.append(token)
        tokens.append(Token(TokenType.EOF, "", self.line, self.column, self.pos, self.pos))
        return tokens

    def _next_token(self) -> Optional[Token]:
        """Get next token from input"""
        if self.pos >= self.length:
            return None

        char = self.content[self.pos]
        start_pos = self.pos
        start_line = self.line
        start_col = self.column

        # Newline
        if char == '\n':
            self._advance()
            return Token(TokenType.NEWLINE, '\n', start_line, start_col, start_pos, self.pos)

        # Carriage return (handle \r\n and \r)
        if char == '\r':
            self._advance()
            if self.pos < self.length and self.content[self.pos] == '\n':
                self._advance()
                return Token(TokenType.NEWLINE, '\r\n', start_line, start_col, start_pos, self.pos)
            return Token(TokenType.NEWLINE, '\r', start_line, start_col, start_pos, self.pos)

        # Whitespace (not newlines)
        if char in ' \t':
            return self._read_whitespace(start_pos, start_line, start_col)

        # Comment
        if char == '#':
            return self._read_comment(start_pos, start_line, start_col)

        # String
        if char == '"':
            return self._read_string(start_pos, start_line, start_col)

        # Variable (@name)
        if char == '@':
            return self._read_variable(start_pos, start_line, start_col)

        # Single character tokens
        if char == '=':
            self._advance()
            return Token(TokenType.EQUALS, '=', start_line, start_col, start_pos, self.pos)
        if char == '{':
            self._advance()
            return Token(TokenType.LBRACE, '{', start_line, start_col, start_pos, self.pos)
        if char == '}':
            self._advance()
            return Token(TokenType.RBRACE, '}', start_line, start_col, start_pos, self.pos)
        if char == '<':
            self._advance()
            return Token(TokenType.LESS_THAN, '<', start_line, start_col, start_pos, self.pos)
        if char == '>':
            self._advance()
            return Token(TokenType.GREATER_THAN, '>', start_line, start_col, start_pos, self.pos)

        # Number (including negative)
        if char.isdigit() or (char == '-' and self._peek_digit()):
            return self._read_number(start_pos, start_line, start_col)

        # Identifier
        if self._is_identifier_start(char):
            return self._read_identifier(start_pos, start_line, start_col)

        # Unknown character - skip it
        self._advance()
        return Token(TokenType.IDENTIFIER, char, start_line, start_col, start_pos, self.pos)

    def _advance(self) -> str:
        """Advance position and return current character"""
        char = self.content[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def _peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character without advancing"""
        pos = self.pos + offset
        if pos < self.length:
            return self.content[pos]
        return None

    def _peek_digit(self) -> bool:
        """Check if next char is a digit"""
        next_char = self._peek(1)
        return next_char is not None and next_char.isdigit()

    def _is_identifier_start(self, char: str) -> bool:
        """Check if character can start an identifier"""
        return char.isalpha() or char == '_'

    def _is_identifier_char(self, char: str) -> bool:
        """Check if character can be part of an identifier"""
        return char.isalnum() or char in '_.'

    def _read_whitespace(self, start_pos: int, start_line: int, start_col: int) -> Token:
        """Read whitespace (spaces and tabs, not newlines)"""
        while self.pos < self.length and self.content[self.pos] in ' \t':
            self._advance()
        value = self.content[start_pos:self.pos]
        return Token(TokenType.WHITESPACE, value, start_line, start_col, start_pos, self.pos)

    def _read_comment(self, start_pos: int, start_line: int, start_col: int) -> Token:
        """Read comment from # to end of line"""
        while self.pos < self.length and self.content[self.pos] not in '\r\n':
            self._advance()
        value = self.content[start_pos:self.pos]
        return Token(TokenType.COMMENT, value, start_line, start_col, start_pos, self.pos)

    def _read_string(self, start_pos: int, start_line: int, start_col: int) -> Token:
        """Read quoted string"""
        self._advance()  # Skip opening quote
        while self.pos < self.length:
            char = self.content[self.pos]
            if char == '"':
                self._advance()  # Include closing quote
                break
            if char == '\\' and self.pos + 1 < self.length:
                self._advance()  # Skip escape char
            self._advance()
        value = self.content[start_pos:self.pos]
        return Token(TokenType.STRING, value, start_line, start_col, start_pos, self.pos)

    def _read_variable(self, start_pos: int, start_line: int, start_col: int) -> Token:
        """Read variable starting with @"""
        self._advance()  # Skip @
        while self.pos < self.length and self._is_identifier_char(self.content[self.pos]):
            self._advance()
        value = self.content[start_pos:self.pos]
        return Token(TokenType.VARIABLE, value, start_line, start_col, start_pos, self.pos)

    def _read_number(self, start_pos: int, start_line: int, start_col: int) -> Token:
        """Read number (integer or float, possibly negative)"""
        if self.content[self.pos] == '-':
            self._advance()

        # Integer part
        while self.pos < self.length and self.content[self.pos].isdigit():
            self._advance()

        # Decimal part
        if self.pos < self.length and self.content[self.pos] == '.':
            self._advance()
            while self.pos < self.length and self.content[self.pos].isdigit():
                self._advance()

        value = self.content[start_pos:self.pos]
        return Token(TokenType.NUMBER, value, start_line, start_col, start_pos, self.pos)

    def _read_identifier(self, start_pos: int, start_line: int, start_col: int) -> Token:
        """Read identifier"""
        while self.pos < self.length and self._is_identifier_char(self.content[self.pos]):
            self._advance()
        value = self.content[start_pos:self.pos]
        return Token(TokenType.IDENTIFIER, value, start_line, start_col, start_pos, self.pos)
