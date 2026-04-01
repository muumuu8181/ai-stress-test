from typing import List, Optional
from .lexer import Token, TokenType
from .nodes import (
    Node, RootNode, TextNode, ExpressionNode, IfNode, EachNode
)

class TemplateSyntaxError(Exception):
    """Custom exception for syntax errors in templates."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column

class Parser:
    """
    Parses a list of tokens into an AST.
    """
    def __init__(self, tokens: List[Token]):
        """
        Initializes the parser.

        Args:
            tokens: A list of tokens from the Lexer.
        """
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> RootNode:
        """
        Parses the tokens into a RootNode.

        Returns:
            The root node of the AST.
        """
        return RootNode(self._parse_nodes())

    def _peek(self, offset: int = 0) -> Optional[Token]:
        """Peeks at the token at the given offset."""
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def _advance(self) -> Optional[Token]:
        """Advances and returns the current token."""
        token = self._peek()
        if token:
            self.pos += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        """Expects a token of a certain type, or raises an error."""
        token = self._advance()
        if not token or token.type != token_type:
            msg = f"Expected {token_type.name}, but got {token.type.name if token else 'EOF'}"
            raise TemplateSyntaxError(msg, token.line if token else 0, token.column if token else 0)
        return token

    def _parse_nodes(self, stop_tokens: Optional[List[TokenType]] = None) -> List[Node]:
        """Parses a sequence of nodes until a stop token is encountered or EOF."""
        if stop_tokens is None:
            stop_tokens = []
        nodes = []
        while self.pos < len(self.tokens):
            token = self._peek()

            if token.type in stop_tokens:
                break

            if token.type == TokenType.EXPR_START:
                nodes.append(self._parse_expression())
            elif token.type == TokenType.IF_START:
                nodes.append(self._parse_if())
            elif token.type == TokenType.EACH_START:
                nodes.append(self._parse_each())
            elif token.type == TokenType.TEXT:
                nodes.append(TextNode(token.value, token.line, token.column))
                self._advance()
            else:
                # Unexpected token type (e.g., closing tags without matching opening tags)
                raise TemplateSyntaxError(f"Unexpected token {token.type.name}", token.line, token.column)
        return nodes

    def _parse_expression(self) -> ExpressionNode:
        """Parses ${...} expression."""
        start_token = self._expect(TokenType.EXPR_START)
        content_token = self._expect(TokenType.TEXT)
        self._expect(TokenType.EXPR_END)
        return ExpressionNode(content_token.value.strip(), start_token.line, start_token.column)

    def _parse_if(self) -> IfNode:
        """Parses {?condition}...{/?} conditional block."""
        start_token = self._expect(TokenType.IF_START)
        condition_token = self._expect(TokenType.TEXT)
        self._expect(TokenType.IF_END)

        body_nodes = self._parse_nodes(stop_tokens=[TokenType.END_IF])
        self._expect(TokenType.END_IF)

        return IfNode(condition_token.value.strip(), body_nodes, start_token.line, start_token.column)

    def _parse_each(self) -> EachNode:
        """Parses {@each items as item}...{/each} loop block."""
        start_token = self._expect(TokenType.EACH_START)
        content_token = self._expect(TokenType.TEXT)
        self._expect(TokenType.EACH_END)

        content = content_token.value.strip()
        # Expected format: "items as item"
        import re
        match = re.match(r"^(.+?)\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*)$", content)
        if not match:
             raise TemplateSyntaxError(f"Invalid @each syntax: '{content}'. Expected '@each items as item'",
                                     content_token.line, content_token.column)

        items_expr, item_name = match.groups()
        body_nodes = self._parse_nodes(stop_tokens=[TokenType.END_EACH])
        self._expect(TokenType.END_EACH)

        return EachNode(items_expr.strip(), item_name.strip(), body_nodes, start_token.line, start_token.column)
