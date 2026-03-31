from enum import Enum, auto
from typing import NamedTuple, List

class TokenType(Enum):
    LITERAL = auto()
    DOT = auto()
    CARET = auto()
    DOLLAR = auto()
    STAR = auto()
    PLUS = auto()
    QUESTION = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LPAREN = auto()
    RPAREN = auto()
    PIPE = auto()
    ESCAPED = auto()
    EOF = auto()

class Token(NamedTuple):
    type: TokenType
    value: str

class Lexer:
    """
    Lexer for regex patterns.
    Converts a regex string into a list of Tokens.
    """
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.pos = 0

    def tokenize(self) -> List[Token]:
        """
        Tokenizes the input pattern.

        Returns:
            List[Token]: A list of tokens representing the regex pattern.
        """
        tokens = []
        while self.pos < len(self.pattern):
            char = self.pattern[self.pos]
            if char == '\\':
                self.pos += 1
                if self.pos < len(self.pattern):
                    tokens.append(Token(TokenType.ESCAPED, self.pattern[self.pos]))
                    self.pos += 1
                else:
                    # Trailing backslash - could be an error or literal backslash
                    # Standard regex usually treats this as an error.
                    raise ValueError("Trailing backslash")
            elif char == '.':
                tokens.append(Token(TokenType.DOT, '.'))
                self.pos += 1
            elif char == '^':
                tokens.append(Token(TokenType.CARET, '^'))
                self.pos += 1
            elif char == '$':
                tokens.append(Token(TokenType.DOLLAR, '$'))
                self.pos += 1
            elif char == '*':
                tokens.append(Token(TokenType.STAR, '*'))
                self.pos += 1
            elif char == '+':
                tokens.append(Token(TokenType.PLUS, '+'))
                self.pos += 1
            elif char == '?':
                tokens.append(Token(TokenType.QUESTION, '?'))
                self.pos += 1
            elif char == '{':
                tokens.append(Token(TokenType.LBRACE, '{'))
                self.pos += 1
            elif char == '}':
                tokens.append(Token(TokenType.RBRACE, '}'))
                self.pos += 1
            elif char == '[':
                tokens.append(Token(TokenType.LBRACKET, '['))
                self.pos += 1
            elif char == ']':
                tokens.append(Token(TokenType.RBRACKET, ']'))
                self.pos += 1
            elif char == '(':
                tokens.append(Token(TokenType.LPAREN, '('))
                self.pos += 1
            elif char == ')':
                tokens.append(Token(TokenType.RPAREN, ')'))
                self.pos += 1
            elif char == '|':
                tokens.append(Token(TokenType.PIPE, '|'))
                self.pos += 1
            else:
                tokens.append(Token(TokenType.LITERAL, char))
                self.pos += 1

        tokens.append(Token(TokenType.EOF, ''))
        return tokens
