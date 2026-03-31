import re
from enum import Enum, auto
from typing import List, NamedTuple, Any

class TokenType(Enum):
    ROOT = auto()          # $
    CURRENT = auto()       # @
    DOT = auto()           # .
    DOUBLE_DOT = auto()    # ..
    WILDCARD = auto()      # *
    LEFT_BRACKET = auto()  # [
    RIGHT_BRACKET = auto() # ]
    LEFT_PAREN = auto()    # (
    RIGHT_PAREN = auto()   # )
    FILTER_START = auto()  # ?(
    COMMA = auto()         # ,
    COLON = auto()         # :
    IDENTIFIER = auto()    # e.g., store
    STRING = auto()        # 'string' or "string"
    NUMBER = auto()        # 123, -1, 0.5
    OPERATOR = auto()      # ==, !=, <, <=, >, >=, &&, ||, !
    EOF = auto()

class Token(NamedTuple):
    type: TokenType
    value: Any
    pos: int

class Lexer:
    """Lexer for JSONPath expressions."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < len(self.text):
            char = self.text[self.pos]

            if char.isspace():
                self.pos += 1
                continue

            if char == '$':
                tokens.append(Token(TokenType.ROOT, '$', self.pos))
                self.pos += 1
            elif char == '@':
                tokens.append(Token(TokenType.CURRENT, '@', self.pos))
                self.pos += 1
            elif char == '.':
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '.':
                    tokens.append(Token(TokenType.DOUBLE_DOT, '..', self.pos))
                    self.pos += 2
                else:
                    tokens.append(Token(TokenType.DOT, '.', self.pos))
                    self.pos += 1
            elif char == '*':
                tokens.append(Token(TokenType.WILDCARD, '*', self.pos))
                self.pos += 1
            elif char == '[':
                tokens.append(Token(TokenType.LEFT_BRACKET, '[', self.pos))
                self.pos += 1
            elif char == '?':
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '(':
                    tokens.append(Token(TokenType.FILTER_START, '?(', self.pos))
                    self.pos += 2
                else:
                    raise ValueError(f"Unexpected '?' at {self.pos}")
            elif char == ']':
                tokens.append(Token(TokenType.RIGHT_BRACKET, ']', self.pos))
                self.pos += 1
            elif char == '(':
                tokens.append(Token(TokenType.LEFT_PAREN, '(', self.pos))
                self.pos += 1
            elif char == ')':
                tokens.append(Token(TokenType.RIGHT_PAREN, ')', self.pos))
                self.pos += 1
            elif char == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.pos))
                self.pos += 1
            elif char == ':':
                tokens.append(Token(TokenType.COLON, ':', self.pos))
                self.pos += 1
            elif char == "'" or char == '"':
                quote = char
                start_pos = self.pos
                self.pos += 1
                string_val = ""
                while self.pos < len(self.text) and self.text[self.pos] != quote:
                    if self.text[self.pos] == '\\':
                        self.pos += 1
                        if self.pos < len(self.text):
                            string_val += self.text[self.pos]
                        else:
                            raise ValueError(f"Unterminated escape sequence at {self.pos}")
                    else:
                        string_val += self.text[self.pos]
                    self.pos += 1
                if self.pos >= len(self.text):
                    raise ValueError(f"Unterminated string at {start_pos}")
                tokens.append(Token(TokenType.STRING, string_val, start_pos))
                self.pos += 1
            elif char.isdigit() or (char == '-' and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()):
                start_pos = self.pos
                match = re.match(r'-?\d+(\.\d+)?', self.text[self.pos:])
                if match:
                    num_str = match.group(0)
                    if '.' in num_str:
                        tokens.append(Token(TokenType.NUMBER, float(num_str), start_pos))
                    else:
                        tokens.append(Token(TokenType.NUMBER, int(num_str), start_pos))
                    self.pos += len(num_str)
                else:
                    raise ValueError(f"Invalid number at {self.pos}")
            elif char.isalpha() or char == '_':
                start_pos = self.pos
                match = re.match(r'[a-zA-Z_][a-zA-Z0-9_-]*', self.text[self.pos:])
                if match:
                    id_str = match.group(0)
                    tokens.append(Token(TokenType.IDENTIFIER, id_str, start_pos))
                    self.pos += len(id_str)
                else:
                    raise ValueError(f"Invalid identifier at {self.pos}")
            elif char in "=!<>|&":
                start_pos = self.pos
                match = re.match(r'==|!=|<=|>=|<|>|&&|\|\||!', self.text[self.pos:])
                if match:
                    op_str = match.group(0)
                    tokens.append(Token(TokenType.OPERATOR, op_str, start_pos))
                    self.pos += len(op_str)
                else:
                    raise ValueError(f"Invalid operator at {self.pos}")
            else:
                raise ValueError(f"Unexpected character '{char}' at {self.pos}")

        tokens.append(Token(TokenType.EOF, None, self.pos))
        return tokens
