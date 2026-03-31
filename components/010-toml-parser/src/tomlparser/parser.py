from typing import Any, Dict, List, Optional, Union
from .lexer import Token, TokenType

class Parser:
    """
    A parser for converting a list of TOML tokens into a dictionary.
    """
    def __init__(self, tokens: List[Token]):
        """
        Initializes the parser with a list of tokens.

        Args:
            tokens: A list of Token objects from the lexer.
        """
        self.tokens = tokens
        self.pos = 0
        self.result: Dict[str, Any] = {}
        self.current_table = self.result
        # Track defined tables to prevent redefinition
        self.defined_tables = set()

    def _peek(self, n=0) -> Token:
        if self.pos + n >= len(self.tokens):
            return Token(TokenType.EOF, None, -1, -1)
        return self.tokens[self.pos + n]

    def _advance(self, n=1):
        self.pos += n

    def _consume(self, expected_type: TokenType) -> Token:
        token = self._peek()
        if token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type} at {token.line}:{token.column}")
        self._advance()
        return token

    def parse(self) -> Dict[str, Any]:
        """
        Parses the tokens into a dictionary.

        Returns:
            A dictionary representation of the TOML tokens.
        """
        while self.pos < len(self.tokens):
            token = self._peek()
            if token.type == TokenType.NEWLINE:
                self._advance()
            elif token.type == TokenType.LBRACKET:
                self._parse_table()
            elif token.type in (TokenType.BARE_KEY, TokenType.STRING):
                self._parse_key_value(self.current_table)
            elif token.type == TokenType.EOF:
                break
            elif token.type in (TokenType.INTEGER, TokenType.FLOAT, TokenType.BOOLEAN, TokenType.DATETIME):
                # A value without a key
                raise ValueError(f"Value without key at {token.line}:{token.column}")
            else:
                # Other tokens might be part of an unexpected sequence
                self._advance()
        return self.result

    def _parse_key(self) -> List[str]:
        keys = []
        while True:
            token = self._peek()
            if token.type in (TokenType.BARE_KEY, TokenType.STRING):
                keys.append(token.value)
                self._advance()
            else:
                raise ValueError(f"Expected key, got {token.type} at {token.line}:{token.column}")

            if self._peek().type == TokenType.DOT:
                self._advance()
            else:
                break
        return keys

    def _parse_key_value(self, target: Dict[str, Any]):
        keys = self._parse_key()
        self._consume(TokenType.EQUALS)
        value = self._parse_value()

        # Handle dotted keys
        curr = target
        for i, key in enumerate(keys[:-1]):
            if key not in curr:
                curr[key] = {}
            elif not isinstance(curr[key], dict):
                raise ValueError(f"Key {key} already exists and is not a table")
            curr = curr[key]

        final_key = keys[-1]
        if final_key in curr:
            raise ValueError(f"Duplicate key: {final_key}")
        curr[final_key] = value

    def _parse_value(self) -> Any:
        token = self._peek()
        if token.type in (TokenType.STRING, TokenType.MULTILINE_STRING,
                          TokenType.LITERAL_STRING, TokenType.MULTILINE_LITERAL_STRING,
                          TokenType.INTEGER, TokenType.FLOAT, TokenType.BOOLEAN, TokenType.DATETIME):
            self._advance()
            return token.value
        elif token.type == TokenType.LBRACKET:
            return self._parse_array()
        elif token.type == TokenType.LBRACE:
            return self._parse_inline_table()
        else:
            raise ValueError(f"Unexpected token {token.type} for value at {token.line}:{token.column}")

    def _parse_array(self) -> List[Any]:
        self._consume(TokenType.LBRACKET)
        array = []
        while self._peek().type != TokenType.RBRACKET:
            if self._peek().type == TokenType.NEWLINE:
                self._advance()
                continue
            array.append(self._parse_value())
            if self._peek().type == TokenType.COMMA:
                self._advance()
            elif self._peek().type == TokenType.RBRACKET:
                break
            elif self._peek().type == TokenType.NEWLINE:
                continue
            else:
                # TOML allows trailing commas and newlines in arrays
                pass
        self._consume(TokenType.RBRACKET)
        return array

    def _parse_inline_table(self) -> Dict[str, Any]:
        self._consume(TokenType.LBRACE)
        table = {}
        while self._peek().type != TokenType.RBRACE:
            self._parse_key_value(table)
            if self._peek().type == TokenType.COMMA:
                self._advance()
            elif self._peek().type == TokenType.RBRACE:
                break
            else:
                raise ValueError(f"Expected comma or }}, got {self._peek().type}")
        self._consume(TokenType.RBRACE)
        return table

    def _parse_table(self):
        self._consume(TokenType.LBRACKET)
        is_array_of_tables = False
        if self._peek().type == TokenType.LBRACKET:
            self._advance()
            is_array_of_tables = True

        keys = self._parse_key()

        if is_array_of_tables:
            self._consume(TokenType.RBRACKET)
            self._consume(TokenType.RBRACKET)

            curr = self.result
            for key in keys[:-1]:
                if key not in curr:
                    curr[key] = {}
                curr = curr[key]

            final_key = keys[-1]
            if final_key not in curr:
                curr[final_key] = []
            if not isinstance(curr[final_key], list):
                raise ValueError(f"Key {final_key} already exists and is not an array of tables")

            new_table = {}
            curr[final_key].append(new_table)
            self.current_table = new_table
        else:
            self._consume(TokenType.RBRACKET)

            table_name = ".".join(keys)
            if table_name in self.defined_tables:
                raise ValueError(f"Table redefinition: {table_name}")
            self.defined_tables.add(table_name)

            curr = self.result
            for key in keys:
                if key not in curr:
                    curr[key] = {}
                elif not isinstance(curr[key], dict):
                    # Special case: it might be an array of tables
                    if isinstance(curr[key], list) and len(curr[key]) > 0:
                        curr = curr[key][-1]
                        continue
                    raise ValueError(f"Key {key} already exists and is not a table")
                curr = curr[key]
            self.current_table = curr
