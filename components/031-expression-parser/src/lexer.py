from typing import List, Optional

from .ast_nodes import Token, TokenType


class Lexer:
    """A lexical analyzer for mathematical expressions."""

    def __init__(self, text: str) -> None:
        """
        Initialize the lexer with input text.

        Args:
            text (str): The mathematical expression to tokenize.
        """
        self.text = text
        self.pos = 0
        self.current_char: Optional[str] = self.text[0] if self.text else None

    def advance(self) -> None:
        """Advance the current position and update current_char."""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self) -> None:
        """Skip all whitespace characters."""
        while self.current_char and self.current_char.isspace():
            self.advance()

    def get_number(self) -> Token:
        """
        Extract a numeric value from the input.

        Returns:
            Token: A NUMBER token with the float value.

        Raises:
            ValueError: If the numeric value is malformed.
        """
        result = ""
        dot_count = 0
        while self.current_char and (
            self.current_char.isdigit() or self.current_char == "."
        ):
            if self.current_char == ".":
                dot_count += 1
            if dot_count > 1:
                raise ValueError(
                    f"Malformed number: {result + self.current_char}"
                )
            result += self.current_char
            self.advance()
        return Token(TokenType.NUMBER, float(result))

    def get_identifier(self) -> Token:
        """
        Extract an identifier (variable or function name) from the input.

        Returns:
            Token: An IDENTIFIER token with the string value.
        """
        result = ""
        while self.current_char and (
            self.current_char.isalnum() or self.current_char == "_"
        ):
            result += self.current_char
            self.advance()
        return Token(TokenType.IDENTIFIER, result)

    def get_next_token(self) -> Token:
        """
        Lexical analyzer (tokenizer).

        Returns:
            Token: The next token in the input string.

        Raises:
            ValueError: If an unexpected character is encountered.
        """
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit() or self.current_char == ".":
                return self.get_number()

            if self.current_char.isalpha() or self.current_char == "_":
                return self.get_identifier()

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS)

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS)

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MULTIPLY)

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIVIDE)

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN)

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN)

            if self.current_char == "=":
                self.advance()
                return Token(TokenType.ASSIGN)

            if self.current_char == ",":
                self.advance()
                return Token(TokenType.COMMA)

            raise ValueError(f"Unexpected character: {self.current_char}")

        return Token(TokenType.EOF)

    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire input string.

        Returns:
            List[Token]: A list of all tokens extracted from the input.
        """
        tokens = []
        token = self.get_next_token()
        while token.type != TokenType.EOF:
            tokens.append(token)
            token = self.get_next_token()
        tokens.append(token)
        return tokens
