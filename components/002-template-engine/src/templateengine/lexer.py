import enum
import re
from typing import List, NamedTuple, Optional

class TokenType(enum.Enum):
    """Enumeration of all supported token types."""
    TEXT = "TEXT"
    VAR_START = "VAR_START"  # {{
    VAR_END = "VAR_END"      # }}
    BLOCK_START = "BLOCK_START" # {%
    BLOCK_END = "BLOCK_END"     # %}
    COMMENT = "COMMENT"         # {# ... #}
    EXPRESSION = "EXPRESSION"   # content inside {{ }} or {% %}

class Token(NamedTuple):
    """Represents a single token in the template source."""
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    """
    A lexer for the template engine.
    It breaks the template string into tokens, correctly handling delimiters in strings.
    """
    def __init__(self, template: str):
        """
        Initializes the lexer.

        Args:
            template: The template source string.
        """
        self.template = template
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        """
        Tokenizes the template string.

        Returns:
            A list of Token objects.
        """
        while self.pos < len(self.template):
            if self.template.startswith("{{", self.pos):
                self._tokenize_tag("{{", "}}", TokenType.VAR_START, TokenType.VAR_END)
            elif self.template.startswith("{%", self.pos):
                self._tokenize_tag("{%", "%}", TokenType.BLOCK_START, TokenType.BLOCK_END)
            elif self.template.startswith("{#", self.pos):
                self._tokenize_comment()
            else:
                self._tokenize_text()
        return self.tokens

    def _tokenize_tag(self, start_tag: str, end_tag: str, start_type: TokenType, end_type: TokenType) -> None:
        """Tokenizes a tag, handling potential delimiters inside string literals."""
        start_line, start_col = self.line, self.column
        self.tokens.append(Token(start_type, start_tag, self.line, self.column))
        self._advance(len(start_tag))

        content_start = self.pos
        while self.pos < len(self.template):
            if self.template.startswith(end_tag, self.pos):
                break

            char = self.template[self.pos]
            if char in ('"', "'"):
                quote = char
                self._advance(1)
                while self.pos < len(self.template):
                    if self.template[self.pos] == quote and self.template[self.pos-1] != '\\':
                        self._advance(1)
                        break
                    self._advance(1)
            else:
                self._advance(1)

        if not self.template.startswith(end_tag, self.pos):
             raise SyntaxError(f"Unclosed tag starting at line {start_line}, column {start_col}")

        content = self.template[content_start:self.pos]
        if content:
            self.tokens.append(Token(TokenType.EXPRESSION, content, start_line, start_col + len(start_tag)))

        self.tokens.append(Token(end_type, end_tag, self.line, self.column))
        self._advance(len(end_tag))

    def _tokenize_comment(self) -> None:
        """Tokenizes a comment block."""
        start_line, start_col = self.line, self.column
        self._advance(2) # skip {#
        end_pos = self.template.find("#}", self.pos)
        if end_pos == -1:
            raise SyntaxError(f"Unclosed comment starting at line {start_line}, column {start_col}")

        content = self.template[self.pos:end_pos]
        self.tokens.append(Token(TokenType.COMMENT, content, start_line, start_col))
        self._advance_with_newlines(content)
        self._advance(2) # skip #}

    def _tokenize_text(self) -> None:
        """Tokenizes plain text."""
        start_line, start_col = self.line, self.column

        next_tag = float('inf')
        for tag in ["{{", "{%", "{#"]:
            p = self.template.find(tag, self.pos)
            if p != -1:
                next_tag = min(next_tag, p)

        if next_tag == float('inf'):
            content = self.template[self.pos:]
            self.pos = len(self.template)
        else:
            content = self.template[self.pos:next_tag]
            self.pos = next_tag

        if content:
            self.tokens.append(Token(TokenType.TEXT, content, start_line, start_col))
            for char in content:
                if char == '\n':
                    start_line += 1
                    start_col = 1
                else:
                    start_col += 1
            self.line = start_line
            self.column = start_col

    def _advance(self, n: int) -> None:
        """Advances the lexer by n characters."""
        for _ in range(n):
            if self.pos < len(self.template):
                if self.template[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def _advance_with_newlines(self, text: str, update_pos: bool = True) -> None:
        """Advances the lexer, accounting for newlines in the provided text."""
        for char in text:
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        if update_pos:
            self.pos += len(text)
