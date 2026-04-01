import enum
import re
from typing import List, NamedTuple, Optional

class TokenType(enum.Enum):
    """Enumeration of all supported token types."""
    TEXT = "TEXT"
    EXPR_START = "EXPR_START"    # ${
    EXPR_END = "EXPR_END"        # }
    IF_START = "IF_START"        # {?
    IF_END = "IF_END"            # }
    END_IF = "END_IF"            # {/?}
    EACH_START = "EACH_START"    # {@each
    EACH_END = "EACH_END"        # }
    END_EACH = "END_EACH"        # {/each}

class Token(NamedTuple):
    """Represents a single token in the template source."""
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    """
    A lexer for the template literal engine.
    It breaks the template string into tokens, tracking line and column numbers.
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
            if self.template.startswith("${", self.pos):
                self._tokenize_expression()
            elif self.template.startswith("{?", self.pos):
                self._tokenize_if()
            elif self.template.startswith("{/?}", self.pos):
                self.tokens.append(Token(TokenType.END_IF, "{/?}", self.line, self.column))
                self._advance(4)
            elif self.template.startswith("{@each", self.pos):
                self._tokenize_each()
            elif self.template.startswith("{/each}", self.pos):
                self.tokens.append(Token(TokenType.END_EACH, "{/each}", self.line, self.column))
                self._advance(7)
            else:
                self._tokenize_text()
        return self.tokens

    def _tokenize_expression(self) -> None:
        """Tokenizes ${...} expression."""
        start_line, start_col = self.line, self.column
        self.tokens.append(Token(TokenType.EXPR_START, "${", self.line, self.column))
        self._advance(2)

        content_start = self.pos
        while self.pos < len(self.template):
            if self.template.startswith("}", self.pos):
                break
            # Handle strings inside expressions to avoid premature closing
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

        if not self.template.startswith("}", self.pos):
            raise SyntaxError(f"Unclosed expression starting at line {start_line}, column {start_col}")

        content = self.template[content_start:self.pos]
        if content:
            self.tokens.append(Token(TokenType.TEXT, content, start_line, start_col + 2))

        self.tokens.append(Token(TokenType.EXPR_END, "}", self.line, self.column))
        self._advance(1)

    def _tokenize_if(self) -> None:
        """Tokenizes {?condition}."""
        start_line, start_col = self.line, self.column
        self.tokens.append(Token(TokenType.IF_START, "{?", self.line, self.column))
        self._advance(2)

        content_start = self.pos
        while self.pos < len(self.template):
            if self.template.startswith("}", self.pos):
                break
            self._advance(1)

        if not self.template.startswith("}", self.pos):
            raise SyntaxError(f"Unclosed if-start tag starting at line {start_line}, column {start_col}")

        content = self.template[content_start:self.pos]
        if content:
            self.tokens.append(Token(TokenType.TEXT, content, start_line, start_col + 2))

        self.tokens.append(Token(TokenType.IF_END, "}", self.line, self.column))
        self._advance(1)

    def _tokenize_each(self) -> None:
        """Tokenizes {@each items as item}."""
        start_line, start_col = self.line, self.column
        self.tokens.append(Token(TokenType.EACH_START, "{@each", self.line, self.column))
        self._advance(6)

        content_start = self.pos
        while self.pos < len(self.template):
            if self.template.startswith("}", self.pos):
                break
            self._advance(1)

        if not self.template.startswith("}", self.pos):
            raise SyntaxError(f"Unclosed each-start tag starting at line {start_line}, column {start_col}")

        content = self.template[content_start:self.pos]
        if content:
            self.tokens.append(Token(TokenType.TEXT, content, start_line, start_col + 6))

        self.tokens.append(Token(TokenType.EACH_END, "}", self.line, self.column))
        self._advance(1)

    def _tokenize_text(self) -> None:
        """Tokenizes plain text."""
        start_line, start_col = self.line, self.column

        next_tag = float('inf')
        for tag in ["${", "{?", "{/?}", "{@each", "{/each}"]:
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
            # Manually update line and column for the text
            for char in content:
                if char == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1

    def _advance(self, n: int) -> None:
        """Advances the lexer by n characters, updating line and column."""
        for _ in range(n):
            if self.pos < len(self.template):
                if self.template[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
