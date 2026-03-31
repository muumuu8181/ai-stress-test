import enum
import re
from typing import List, NamedTuple, Optional

class TokenType(enum.Enum):
    TEXT = "TEXT"
    VAR_START = "VAR_START"  # {{
    VAR_END = "VAR_END"      # }}
    BLOCK_START = "BLOCK_START" # {%
    BLOCK_END = "BLOCK_END"     # %}
    COMMENT = "COMMENT"         # {# ... #}
    EXPRESSION = "EXPRESSION"   # content inside {{ }} or {% %}

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    """
    A simple lexer for the template engine.
    It breaks the template string into tokens.
    """
    def __init__(self, template: str):
        self.template = template
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        """
        Tokenizes the template string.
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

    def _tokenize_tag(self, start_tag: str, end_tag: str, start_type: TokenType, end_type: TokenType):
        # Start tag
        self.tokens.append(Token(start_type, start_tag, self.line, self.column))
        self._advance(len(start_tag))

        # Content
        end_pos = self.template.find(end_tag, self.pos)
        if end_pos == -1:
            raise SyntaxError(f"Unclosed tag starting at line {self.line}, column {self.column}")

        content = self.template[self.pos:end_pos]
        # We might want to further tokenize the content if it's complex,
        # but for now we'll treat it as a single EXPRESSION token.
        if content:
            self.tokens.append(Token(TokenType.EXPRESSION, content, self.line, self.column))
            self._advance_with_newlines(content)

        # End tag
        self.tokens.append(Token(end_type, end_tag, self.line, self.column))
        self._advance(len(end_tag))

    def _tokenize_comment(self):
        start_line, start_col = self.line, self.column
        self._advance(2) # skip {#
        end_pos = self.template.find("#}", self.pos)
        if end_pos == -1:
            raise SyntaxError(f"Unclosed comment starting at line {start_line}, column {start_col}")

        content = self.template[self.pos:end_pos]
        self.tokens.append(Token(TokenType.COMMENT, content, start_line, start_col))
        self._advance_with_newlines(content)
        self._advance(2) # skip #}

    def _tokenize_text(self):
        start_pos = self.pos
        start_line, start_col = self.line, self.column

        # Find next occurrence of any tag start
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
            self._advance_with_newlines(content, update_pos=False)

    def _advance(self, n: int):
        for _ in range(n):
            if self.pos < len(self.template):
                if self.template[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def _advance_with_newlines(self, text: str, update_pos: bool = True):
        for char in text:
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        if update_pos:
            self.pos += len(text)
