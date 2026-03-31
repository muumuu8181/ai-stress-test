from enum import Enum, auto
from typing import Any, List, Optional, Dict

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    MINUS = auto()
    PLUS = auto()
    SLASH = auto()
    STAR = auto()
    PERCENT = auto()

    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()

    # Keywords
    AND = auto()
    ELSE = auto()
    ELIF = auto()
    FALSE = auto()
    FN = auto()
    FOR = auto()
    IF = auto()
    IN = auto()
    LET = auto()
    NOT = auto()
    OR = auto()
    TRUE = auto()
    WHILE = auto()

    EOF = auto()

class Token:
    """A lexical token representing a single atomic unit of source code."""
    def __init__(self, type: TokenType, lexeme: str, literal: Any, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self) -> str:
        return f"Token({self.type}, {repr(self.lexeme)}, {self.literal}, {self.line})"

class Lexer:
    """Scanner that converts source code string into a list of Tokens."""
    KEYWORDS: Dict[str, TokenType] = {
        "and": TokenType.AND,
        "else": TokenType.ELSE,
        "elif": TokenType.ELIF,
        "false": TokenType.FALSE,
        "fn": TokenType.FN,
        "for": TokenType.FOR,
        "if": TokenType.IF,
        "in": TokenType.IN,
        "let": TokenType.LET,
        "not": TokenType.NOT,
        "or": TokenType.OR,
        "true": TokenType.TRUE,
        "while": TokenType.WHILE,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> List[Token]:
        """Scans the entire source code and returns the list of tokens."""
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        """Scans a single token."""
        c = self.advance()
        if c == '(': self.add_token(TokenType.LEFT_PAREN)
        elif c == ')': self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{': self.add_token(TokenType.LEFT_BRACE)
        elif c == '}': self.add_token(TokenType.RIGHT_BRACE)
        elif c == '[': self.add_token(TokenType.LEFT_BRACKET)
        elif c == ']': self.add_token(TokenType.RIGHT_BRACKET)
        elif c == ',': self.add_token(TokenType.COMMA)
        elif c == '-': self.add_token(TokenType.MINUS)
        elif c == '+': self.add_token(TokenType.PLUS)
        elif c == '*': self.add_token(TokenType.STAR)
        elif c == '%': self.add_token(TokenType.PERCENT)
        elif c == '/':
            self.add_token(TokenType.SLASH)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c in (' ', '\r', '\t'):
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"' or c == "'":
            self.string(c)
        elif c.isdigit():
            self.number()
        elif c.isalpha() or c == '_':
            self.identifier()
        else:
            raise SyntaxError(f"Unexpected character: {c} at line {self.line}")

    def identifier(self):
        """Scans an identifier or keyword."""
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]
        type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def number(self):
        """Scans a numeric literal (integer or float)."""
        is_float = False
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            is_float = True
            self.advance() # Consume the '.'
            while self.peek().isdigit():
                self.advance()

        value = self.source[self.start:self.current]
        if is_float:
            self.add_token(TokenType.FLOAT, float(value))
        else:
            self.add_token(TokenType.INTEGER, int(value))

    def string(self, quote: str):
        """Scans a string literal."""
        while self.peek() != quote and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise SyntaxError(f"Unterminated string at line {self.line}")

        self.advance() # The closing quote
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def match(self, expected: str) -> bool:
        """Returns True if the next character matches expected, and advances if so."""
        if self.is_at_end(): return False
        if self.source[self.current] != expected: return False

        self.current += 1
        return True

    def peek(self) -> str:
        """Returns the current character without advancing."""
        if self.is_at_end(): return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        """Returns the next character without advancing."""
        if self.current + 1 >= len(self.source): return '\0'
        return self.source[self.current + 1]

    def advance(self) -> str:
        """Advances and returns the current character."""
        c = self.source[self.current]
        self.current += 1
        return c

    def is_at_end(self) -> bool:
        """Returns True if at the end of source code."""
        return self.current >= len(self.source)

    def add_token(self, type: TokenType, literal: Any = None):
        """Adds a new token to the list of scanned tokens."""
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
