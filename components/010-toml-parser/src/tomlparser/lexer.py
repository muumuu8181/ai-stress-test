import re
from typing import List, Tuple, Any, Optional
from enum import Enum, auto

class TokenType(Enum):
    BARE_KEY = auto()
    STRING = auto()
    MULTILINE_STRING = auto()
    LITERAL_STRING = auto()
    MULTILINE_LITERAL_STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    DATETIME = auto()
    EQUALS = auto()
    DOT = auto()
    COMMA = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    NEWLINE = auto()
    EOF = auto()

class Token:
    def __init__(self, type: TokenType, value: Any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}:{self.column})"

class Lexer:
    """
    A lexer for tokenizing TOML input string.
    """
    def __init__(self, content: str):
        """
        Initializes the lexer with TOML content.

        Args:
            content: The TOML string to tokenize.
        """
        self.content = content
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def _peek(self, n=1) -> str:
        if self.pos + n > len(self.content):
            return ""
        return self.content[self.pos:self.pos + n]

    def _advance(self, n=1):
        for _ in range(n):
            if self.pos < len(self.content):
                if self.content[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def tokenize(self) -> List[Token]:
        """
        Tokenizes the input TOML content.

        Returns:
            A list of Token objects.
        """
        while self.pos < len(self.content):
            char = self.content[self.pos]

            if char.isspace() and char != '\n':
                self._advance()
                continue

            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                self._advance()
                continue

            if char == '#':
                while self.pos < len(self.content) and self.content[self.pos] != '\n':
                    self._advance()
                continue

            if char == '=':
                self.tokens.append(Token(TokenType.EQUALS, '=', self.line, self.column))
                self._advance()
            elif char == '.':
                self.tokens.append(Token(TokenType.DOT, '.', self.line, self.column))
                self._advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self._advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', self.line, self.column))
                self._advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', self.line, self.column))
                self._advance()
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', self.line, self.column))
                self._advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', self.line, self.column))
                self._advance()
            elif char == '"':
                self._tokenize_string()
            elif char == "'":
                self._tokenize_literal_string()
            else:
                if self._is_key_start(char):
                    self._tokenize_key_or_value()
                else:
                    raise ValueError(f"Unexpected character: {char} at line {self.line}, column {self.column}")

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _is_key_start(self, char: str) -> bool:
        return char.isalnum() or char in '-_+'

    def _tokenize_string(self):
        line, column = self.line, self.column
        if self._peek(3) == '"""':
            self._advance(3)
            value = ""
            while True:
                if self.pos >= len(self.content):
                    raise ValueError(f"Unterminated multi-line string starting at {line}:{column}")

                if self._peek(3) == '"""':
                    # Check if it's escaped \"""
                    break

                char = self.content[self.pos]
                if char == '\\':
                    # Just collect the backslash and the next char to handle escapes later
                    value += char
                    self._advance()
                    if self.pos < len(self.content):
                        value += self.content[self.pos]
                        self._advance()
                else:
                    value += char
                    self._advance()

            # Handle closing """
            self._advance(3)
            # Trim first newline if it exists
            if value.startswith('\n'):
                value = value[1:]
            elif value.startswith('\r\n'):
                value = value[2:]

            value = self._handle_escapes(value)
            self.tokens.append(Token(TokenType.MULTILINE_STRING, value, line, column))
        else:
            self._advance()
            value = ""
            while True:
                if self.pos >= len(self.content) or self._peek() == '\n':
                    raise ValueError(f"Unterminated string starting at {line}:{column}")

                char = self.content[self.pos]
                if char == '"':
                    self._advance()
                    break
                elif char == '\\':
                    value += char
                    self._advance()
                    if self.pos < len(self.content):
                        value += self.content[self.pos]
                        self._advance()
                else:
                    value += char
                    self._advance()

            value = self._handle_escapes(value)
            self.tokens.append(Token(TokenType.STRING, value, line, column))

    def _tokenize_literal_string(self):
        line, column = self.line, self.column
        if self._peek(3) == "'''":
            self._advance(3)
            value = ""
            while self._peek(3) != "'''":
                if self.pos >= len(self.content):
                    raise ValueError(f"Unterminated multi-line literal string starting at {line}:{column}")
                value += self.content[self.pos]
                self._advance()
            self._advance(3)
            if value.startswith('\n'):
                value = value[1:]
            elif value.startswith('\r\n'):
                value = value[2:]
            self.tokens.append(Token(TokenType.MULTILINE_LITERAL_STRING, value, line, column))
        else:
            self._advance()
            value = ""
            while self._peek() != "'":
                if self.pos >= len(self.content) or self._peek() == '\n':
                    raise ValueError(f"Unterminated literal string starting at {line}:{column}")
                value += self.content[self.pos]
                self._advance()
            self._advance()
            self.tokens.append(Token(TokenType.LITERAL_STRING, value, line, column))

    def _handle_escapes(self, s: str) -> str:
        """
        Handles TOML escape sequences in basic and multi-line strings.

        TOML escape sequences: \\b \\t \\n \\f \\r \\" \\\\ \\uXXXX \\UXXXXXXXX
        Also handles multi-line string escape (backslash followed by newline).
        """
        escapes = {
            'b': '\b', 't': '\t', 'n': '\n', 'f': '\f', 'r': '\r', '"': '"', '\\': '\\'
        }
        res = ""
        i = 0
        while i < len(s):
            if s[i] == '\\':
                i += 1
                if i >= len(s):
                    raise ValueError("Incomplete escape sequence")
                char = s[i]
                if char in escapes:
                    res += escapes[char]
                    i += 1
                elif char == 'u':
                    hex_val = s[i+1:i+5]
                    if len(hex_val) < 4:
                        raise ValueError(f"Incomplete \\u escape: \\u{hex_val}")
                    res += chr(int(hex_val, 16))
                    i += 5
                elif char == 'U':
                    hex_val = s[i+1:i+9]
                    if len(hex_val) < 8:
                        raise ValueError(f"Incomplete \\U escape: \\U{hex_val}")
                    res += chr(int(hex_val, 16))
                    i += 9
                elif char == '\n' or char == '\r':
                    # Handle multi-line string escape (line ending backslash)
                    if char == '\r' and i < len(s) and s[i] == '\n':
                        i += 1
                    i += 1
                    while i < len(s) and s[i].isspace():
                        i += 1
                else:
                    raise ValueError(f"Unknown escape sequence: \\{char}")
            else:
                res += s[i]
                i += 1
        return res

    def _tokenize_key_or_value(self):
        line, column = self.line, self.column
        value = ""

        while self.pos < len(self.content):
            char = self.content[self.pos]

            # Check for breaking on dot/colon if it's NOT part of a number/datetime
            if char == '.' and value:
                # Is it a float? 1.2, 1_2.3
                if all(c.isdigit() or c in '+-_' for c in value):
                    pass
                # Is it a datetime? 1979-05-27T... or 12:34:56.123
                elif any(c == '-' for c in value) or any(c == ':' for c in value):
                    pass
                else:
                    break
            elif char == ':' and value:
                # Is it a time/datetime? 12:34, 1979-05-27T...
                if any(c.isdigit() for c in value):
                     pass
                else:
                     break
            elif char == ' ' and value:
                # Only allow space if it's like "1979-05-27 07:32:00"
                if not (len(value) >= 10 and value[4] == '-' and value[7] == '-'):
                    break

            if char.isalnum() or char in '-_:.+TZtz ':
                value += char
                self._advance()
            else:
                break

        value = value.strip()

        # Check if it's a boolean
        if value == "true":
            self.tokens.append(Token(TokenType.BOOLEAN, True, line, column))
            return
        if value == "false":
            self.tokens.append(Token(TokenType.BOOLEAN, False, line, column))
            return

        # Check for inf/nan
        if value in ("inf", "+inf"):
            self.tokens.append(Token(TokenType.FLOAT, float('inf'), line, column))
            return
        if value == "-inf":
            self.tokens.append(Token(TokenType.FLOAT, float('-inf'), line, column))
            return
        if value in ("nan", "+nan", "-nan"):
            self.tokens.append(Token(TokenType.FLOAT, float('nan'), line, column))
            return

        # Try datetime
        from .datetime_util import parse_toml_datetime
        dt = parse_toml_datetime(value)
        if dt is not None:
            self.tokens.append(Token(TokenType.DATETIME, dt, line, column))
            return

        # Try number
        try:
            # Validate underscore placement
            if '_' in value:
                if value.startswith('_') or value.endswith('_'):
                    raise ValueError("Underscore cannot be at the start or end of a number")
                if '__' in value:
                    raise ValueError("Consecutive underscores are not allowed")
                for i in range(len(value)):
                    if value[i] == '_':
                        if i == 0 or i == len(value) - 1:
                             raise ValueError("Underscore cannot be at the start or end of a number")
                        if not (value[i-1].isdigit() and value[i+1].isdigit()):
                            raise ValueError("Underscore must be between digits")

            clean_value = value.replace('_', '')

            # Float branch
            if ('.' in clean_value or ('e' in clean_value.lower() and not clean_value.lower().startswith('0x'))) and \
               (clean_value[0].isdigit() or clean_value[0] in '+-'):
                if clean_value.startswith('.') or clean_value.endswith('.'):
                    raise ValueError("Float cannot start or end with a dot")
                if 'e' in clean_value.lower():
                    parts = clean_value.lower().split('e')
                    if len(parts) != 2 or not parts[0] or not parts[1]:
                        raise ValueError("Invalid exponent format")

                int_part = clean_value.split('.')[0].split('e')[0]
                if (len(int_part) > 1 and int_part.startswith('0')) or \
                   ((int_part.startswith('+') or int_part.startswith('-')) and len(int_part) > 2 and int_part[1] == '0'):
                    raise ValueError("Leading zeros are not allowed in the integer part of a float")

                num = float(clean_value)
                self.tokens.append(Token(TokenType.FLOAT, num, line, column))
                return

            # Integer branch
            elif clean_value.startswith('0x'):
                num = int(clean_value, 16)
                self.tokens.append(Token(TokenType.INTEGER, num, line, column))
                return
            elif clean_value.startswith('0o'):
                num = int(clean_value, 8)
                self.tokens.append(Token(TokenType.INTEGER, num, line, column))
                return
            elif clean_value.startswith('0b'):
                num = int(clean_value, 2)
                self.tokens.append(Token(TokenType.INTEGER, num, line, column))
                return
            elif clean_value.isdigit() or (clean_value.startswith(('+', '-')) and clean_value[1:].isdigit()):
                if (clean_value.startswith('0') and len(clean_value) > 1) or \
                   (clean_value.startswith(('+', '-')) and len(clean_value) > 2 and clean_value[1] == '0'):
                    raise ValueError("Invalid leading zero in integer")
                num = int(clean_value)
                self.tokens.append(Token(TokenType.INTEGER, num, line, column))
                return
        except ValueError as e:
            # If it looks like it was intended to be a number, re-raise the error
            if any(c.isdigit() for c in value) and ('.' in value or 'e' in value.lower() or value.startswith(('0x', '0o', '0b', '+', '-', '0'))):
                raise e
            if '_' in value:
                # Underscore only allowed in numbers
                raise e

        # Bare key fallback
        if all(c.isalnum() or c in '-_' for c in value):
             if value and (value[0].isdigit() or value[0] in '+-'):
                 # It might still be a bare key if it contains letters, e.g., 1abc
                 if all(c.isdigit() or c in '+-_' for c in value):
                     # All digits/signs but failed number parse -> it's a malformed number
                     raise ValueError(f"Malformed number: {value} at {line}:{column}")

             self.tokens.append(Token(TokenType.BARE_KEY, value, line, column))
        else:
             raise ValueError(f"Invalid bare key or malformed value: {value} at {line}:{column}")
