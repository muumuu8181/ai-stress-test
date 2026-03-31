from typing import List, Any, Optional, Dict
from .lexer import Token, TokenType

class ASTNode:
    """Base class for AST nodes."""
    pass

class NumberNode(ASTNode):
    """Node representing a numeric value."""
    def __init__(self, value: float) -> None:
        self.value = value

class StringNode(ASTNode):
    """Node representing a string literal."""
    def __init__(self, value: str) -> None:
        self.value = value

class CellNode(ASTNode):
    """Node representing a cell reference."""
    def __init__(self, address: str) -> None:
        self.address = address

class RangeNode(ASTNode):
    """Node representing a range reference."""
    def __init__(self, range_ref: str) -> None:
        self.range_ref = range_ref

class BinaryOpNode(ASTNode):
    """Node representing a binary operation."""
    def __init__(self, left: ASTNode, op: str, right: ASTNode) -> None:
        self.left = left
        self.op = op
        self.right = right

class FunctionCallNode(ASTNode):
    """Node representing a function call."""
    def __init__(self, name: str, args: List[ASTNode]) -> None:
        self.name = name
        self.args = args

class Parser:
    """
    Parser for spreadsheet formulas, converting tokens into an internal representation.
    """

    def __init__(self, tokens: List[Token]) -> None:
        """
        Initialize the parser.

        Args:
            tokens: A list of tokens from the lexer.
        """
        self.tokens: List[Token] = tokens
        self.pos: int = 0

    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peeks at the token at the specified offset."""
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, expected_type: Optional[str] = None) -> Token:
        """Consumes the current token if it matches the expected type."""
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of formula")
        if expected_type and token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, but got {token.type}")
        self.pos += 1
        return token

    def parse(self) -> ASTNode:
        """
        Parse the tokens and return the root node.

        Returns:
            The root ASTNode.
        """
        if not self.tokens:
            raise ValueError("Empty formula")
        res = self.parse_expression()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token at position {self.pos}: {self.peek()}")
        return res

    def parse_expression(self) -> ASTNode:
        """Parse additive expression (+, -)"""
        node = self.parse_term()

        while self.peek() and self.peek().type == TokenType.OPERATOR and self.peek().value in "+-":
            op = self.consume().value
            right = self.parse_term()
            node = BinaryOpNode(node, op, right)

        return node

    def parse_term(self) -> ASTNode:
        """Parse multiplicative expression (*, /)"""
        node = self.parse_factor()

        while self.peek() and self.peek().type == TokenType.OPERATOR and self.peek().value in "*/":
            op = self.consume().value
            right = self.parse_factor()
            node = BinaryOpNode(node, op, right)

        return node

    def parse_factor(self) -> ASTNode:
        """Parse primary elements, unary operators, or parentheses"""
        token = self.peek()

        if token is None:
            raise ValueError("Unexpected end of formula")

        if token.type == TokenType.OPERATOR and token.value == "-":
            self.consume()
            return BinaryOpNode(NumberNode(0.0), "-", self.parse_factor())

        if token.type == TokenType.NUMBER:
            return NumberNode(float(self.consume().value))

        if token.type == TokenType.STRING:
            return StringNode(self.consume().value)

        if token.type == TokenType.CELL:
            return CellNode(self.consume().value)

        if token.type == TokenType.RANGE:
            return RangeNode(self.consume().value)

        if token.type == TokenType.FUNCTION:
            func_name = self.consume().value
            self.consume(TokenType.LPAREN)
            args = []
            if self.peek() and self.peek().type != TokenType.RPAREN:
                args.append(self.parse_expression())
                while self.peek() and self.peek().type == TokenType.COMMA:
                    self.consume()
                    args.append(self.parse_expression())
            self.consume(TokenType.RPAREN)
            return FunctionCallNode(func_name, args)

        if token.type == TokenType.LPAREN:
            self.consume()
            node = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return node

        raise ValueError(f"Unexpected token: {token}")
