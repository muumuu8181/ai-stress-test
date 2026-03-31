import re
from typing import List, Optional, Any, Dict
from .lexer import Token, TokenType
from .nodes import (
    Node, RootNode, TextNode, VariableNode, IfNode, ForNode, ExtendsNode, BlockNode
)

class Parser:
    """
    Parses a list of tokens into an AST.
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> RootNode:
        """Parses the tokens into a RootNode."""
        return RootNode(self._parse_nodes())

    def _peek(self, offset: int = 0) -> Optional[Token]:
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def _advance(self) -> Optional[Token]:
        token = self._peek()
        if token:
            self.pos += 1
        return token

    def _expect(self, token_type: TokenType) -> Token:
        token = self._advance()
        if not token or token.type != token_type:
            msg = f"Expected {token_type}, but got {token.type if token else 'EOF'}"
            if token:
                msg += f" at line {token.line}, column {token.column}"
            raise SyntaxError(msg)
        return token

    def _parse_nodes(self, stop_tokens: Optional[List[str]] = None) -> List[Node]:
        """Parses a sequence of nodes until a stop token is encountered or EOF."""
        if stop_tokens is None:
            stop_tokens = []
        nodes = []
        while self.pos < len(self.tokens):
            token = self._peek()

            if token.type == TokenType.BLOCK_START:
                # Check for stop tokens like 'endif', 'else', 'elif', 'endfor'
                next_token = self._peek(1)
                if next_token and next_token.type == TokenType.EXPRESSION:
                    first_word = next_token.value.strip().split()[0]
                    if first_word in stop_tokens:
                        break

                nodes.append(self._parse_block())
            elif token.type == TokenType.VAR_START:
                nodes.append(self._parse_variable())
            elif token.type == TokenType.TEXT:
                nodes.append(TextNode(token.value))
                self._advance()
            elif token.type == TokenType.COMMENT:
                # Ignore comments
                self._advance()
            else:
                # Unexpected token type for top-level nodes
                self._advance()
        return nodes

    def _parse_variable(self) -> VariableNode:
        """Parses a variable expression."""
        self._expect(TokenType.VAR_START)
        expr_token = self._expect(TokenType.EXPRESSION)
        self._expect(TokenType.VAR_END)
        return VariableNode(expr_token.value, expr_token.line, expr_token.column)

    def _parse_block(self) -> Node:
        """Parses a block tag."""
        self._expect(TokenType.BLOCK_START)
        expr_token = self._expect(TokenType.EXPRESSION)
        self._expect(TokenType.BLOCK_END)

        content = expr_token.value.strip()
        parts = content.split()
        if not parts:
            raise SyntaxError(f"Empty block at line {expr_token.line}, column {expr_token.column}")

        tag = parts[0]

        if tag == "if":
            condition = " ".join(parts[1:])
            then_nodes = self._parse_nodes(stop_tokens=["elif", "else", "endif"])

            elif_nodes = []
            while True:
                next_tag = self._peek_tag()
                if next_tag == "elif":
                    self._expect(TokenType.BLOCK_START)
                    elif_expr = self._expect(TokenType.EXPRESSION)
                    self._expect(TokenType.BLOCK_END)
                    elif_condition = " ".join(elif_expr.value.strip().split()[1:])
                    elif_body = self._parse_nodes(stop_tokens=["elif", "else", "endif"])
                    elif_nodes.append((elif_condition, elif_body))
                else:
                    break

            else_nodes = []
            if self._peek_tag() == "else":
                self._expect(TokenType.BLOCK_START)
                self._expect(TokenType.EXPRESSION) # 'else'
                self._expect(TokenType.BLOCK_END)
                else_nodes = self._parse_nodes(stop_tokens=["endif"])

            self._expect(TokenType.BLOCK_START)
            self._expect(TokenType.EXPRESSION) # 'endif'
            self._expect(TokenType.BLOCK_END)

            return IfNode(condition, then_nodes, elif_nodes, else_nodes, expr_token.line, expr_token.column)

        elif tag == "for":
            # Expected: for item in items
            if len(parts) < 4 or parts[2] != "in":
                 raise SyntaxError(f"Invalid for loop syntax at line {expr_token.line}")
            item_name = parts[1]
            collection_expr = " ".join(parts[3:])
            body_nodes = self._parse_nodes(stop_tokens=["endfor"])

            self._expect(TokenType.BLOCK_START)
            self._expect(TokenType.EXPRESSION) # 'endfor'
            self._expect(TokenType.BLOCK_END)

            return ForNode(item_name, collection_expr, body_nodes, expr_token.line, expr_token.column)

        elif tag == "extends":
            parent = content[len("extends"):].strip()
            return ExtendsNode(parent, expr_token.line, expr_token.column)

        elif tag == "block":
            if len(parts) < 2:
                 raise SyntaxError(f"Invalid block name at line {expr_token.line}")
            block_name = parts[1]
            body_nodes = self._parse_nodes(stop_tokens=["endblock"])

            self._expect(TokenType.BLOCK_START)
            self._expect(TokenType.EXPRESSION) # 'endblock'
            self._expect(TokenType.BLOCK_END)

            return BlockNode(block_name, body_nodes, expr_token.line, expr_token.column)

        else:
            raise SyntaxError(f"Unknown tag '{tag}' at line {expr_token.line}")

    def _peek_tag(self) -> Optional[str]:
        """Peeks at the tag name if the next token is a block start."""
        token = self._peek()
        if token and token.type == TokenType.BLOCK_START:
            next_token = self._peek(1)
            if next_token and next_token.type == TokenType.EXPRESSION:
                return next_token.value.strip().split()[0]
        return None
