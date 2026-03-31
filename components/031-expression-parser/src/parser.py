from typing import List, Optional

from .ast_nodes import (AssignmentNode, ASTNode, BinaryOpNode,
                        FunctionCallNode, NumberNode, Token, TokenType,
                        UnaryOpNode, VariableNode)
from .lexer import Lexer


class Parser:
    """
    A recursive descent parser for mathematical expressions.

    Grammar:
    expression   : identifier ASSIGN expression | sum
    sum          : term ( ( PLUS | MINUS ) term )*
    term         : factor ( ( MULTIPLY | DIVIDE ) factor )*
    factor       : PLUS factor | MINUS factor | power
    power        : primary ( '^' primary )* # For now only simple primary
    primary      : NUMBER
                 | identifier ( LPAREN ( expression ( COMMA expression )* )? RPAREN )?
                 | LPAREN expression RPAREN
    """

    def __init__(self, text: str) -> None:
        """
        Initialize the parser with input text.

        Args:
            text (str): The mathematical expression to parse.
        """
        self.lexer = Lexer(text)
        self.current_token: Token = self.lexer.get_next_token()

    def advance(self) -> None:
        """Advance the current token."""
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type: TokenType) -> None:
        """
        Consume a token of a specific type.

        Args:
            token_type (TokenType): The expected token type.

        Raises:
            SyntaxError: If the current token type does not match.
        """
        if self.current_token.type == token_type:
            self.advance()
        else:
            raise SyntaxError(
                f"Invalid syntax: Expected {token_type}, but found {self.current_token.type}"
            )

    def parse(self) -> ASTNode:
        """
        Parse the input and return the root AST node.

        Returns:
            ASTNode: The root of the Abstract Syntax Tree.
        """
        node = self.expression()
        if self.current_token.type != TokenType.EOF:
            raise SyntaxError(f"Unexpected token: {self.current_token.type}")
        return node

    def expression(self) -> ASTNode:
        """
        expression : identifier ASSIGN expression | sum
        """
        if self.current_token.type == TokenType.IDENTIFIER:
            # Check for assignment without advancing the main lexer.
            # Since my Lexer doesn't easily support peek, I'll just check
            # if it's followed by ASSIGN by creating a temporary lexer.
            temp_lexer = Lexer(self.lexer.text[self.lexer.pos :])
            next_token = temp_lexer.get_next_token()

            if next_token.type == TokenType.ASSIGN:
                name = str(self.current_token.value)
                self.eat(TokenType.IDENTIFIER)
                self.eat(TokenType.ASSIGN)
                expr = self.expression()
                return AssignmentNode(name, expr)

        return self.sum()

    def sum(self) -> ASTNode:
        """
        sum : term ( ( PLUS | MINUS ) term )*
        """
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinaryOpNode(left=node, op=token.type, right=self.term())

        return node

    def term(self) -> ASTNode:
        """
        term : factor ( ( MULTIPLY | DIVIDE ) factor )*
        """
        node = self.factor()

        while self.current_token.type in (
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
        ):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)

            node = BinaryOpNode(left=node, op=token.type, right=self.factor())

        return node

    def factor(self) -> ASTNode:
        """
        factor : PLUS factor | MINUS factor | primary
        """
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOpNode(op=TokenType.PLUS, expr=self.factor())
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOpNode(op=TokenType.MINUS, expr=self.factor())
        else:
            return self.primary()

    def primary(self) -> ASTNode:
        """
        primary : NUMBER
                | identifier ( LPAREN ( expression ( COMMA expression )* )? RPAREN )?
                | LPAREN expression RPAREN
        """
        token = self.current_token

        if token.type == TokenType.NUMBER:
            val = token.value
            if not isinstance(val, (int, float)):
                raise ValueError("Expected number value")
            self.eat(TokenType.NUMBER)
            return NumberNode(value=float(val))

        if token.type == TokenType.IDENTIFIER:
            name = str(token.value)
            self.eat(TokenType.IDENTIFIER)

            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args: List[ASTNode] = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        args.append(self.expression())
                self.eat(TokenType.RPAREN)
                return FunctionCallNode(name=name, args=args)
            else:
                return VariableNode(name=name)

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expression()
            self.eat(TokenType.RPAREN)
            return node

        raise SyntaxError(f"Unexpected token: {token.type}")
