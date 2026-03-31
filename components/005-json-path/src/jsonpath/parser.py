from typing import List, Any, Optional
from .lexer import Token, TokenType, Lexer
from .nodes import (
    Node, RootNode, CurrentNode, FieldNode, IndexNode, SliceNode,
    WildcardNode, RecursiveDescentNode, UnionNode, FilterNode,
    ExpressionNode, BinaryExpressionNode, UnaryExpressionNode,
    PathExpressionNode, LiteralNode
)

class Parser:
    """Parser for JSONPath expressions."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: TokenType) -> Token:
        token = self.peek()
        if token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type} at {token.pos}")
        self.pos += 1
        return token

    def parse(self) -> List[Node]:
        nodes = []
        if self.peek().type == TokenType.ROOT:
            self.consume(TokenType.ROOT)
            nodes.append(RootNode())
        else:
             raise ValueError(f"JSONPath must start with '$' or be a relative path (not yet supported). Got {self.peek().type}")

        while self.peek().type != TokenType.EOF:
            token = self.peek()
            if token.type == TokenType.DOT:
                self.consume(TokenType.DOT)
                next_token = self.peek()
                if next_token.type == TokenType.WILDCARD:
                    self.consume(TokenType.WILDCARD)
                    nodes.append(WildcardNode())
                elif next_token.type == TokenType.IDENTIFIER:
                    nodes.append(FieldNode(self.consume(TokenType.IDENTIFIER).value))
                else:
                    raise ValueError(f"Expected identifier or wildcard after '.' at {next_token.pos}")
            elif token.type == TokenType.DOUBLE_DOT:
                self.consume(TokenType.DOUBLE_DOT)
                nodes.append(RecursiveDescentNode())
                next_token = self.peek()
                if next_token.type == TokenType.IDENTIFIER:
                    nodes.append(FieldNode(self.consume(TokenType.IDENTIFIER).value))
                elif next_token.type == TokenType.WILDCARD:
                    self.consume(TokenType.WILDCARD)
                    nodes.append(WildcardNode())
                # Handle cases like $..[0] if needed, for now just allow field/wildcard
            elif token.type == TokenType.LEFT_BRACKET:
                nodes.append(self.parse_bracket())
            elif token.type == TokenType.FILTER_START:
                # Filter as a separate node after something else
                nodes.append(self.parse_filter())
            else:
                break
        return nodes

    def parse_bracket(self) -> Node:
        self.consume(TokenType.LEFT_BRACKET)
        selectors = []

        if self.peek().type == TokenType.FILTER_START:
            selectors.append(self.parse_filter())
            self.consume(TokenType.RIGHT_BRACKET)
            return selectors[0]

        while self.peek().type != TokenType.RIGHT_BRACKET:
            token = self.peek()
            if token.type == TokenType.NUMBER:
                start = self.consume(TokenType.NUMBER).value
                if self.peek().type == TokenType.COLON:
                    self.consume(TokenType.COLON)
                    stop = None
                    if self.peek().type == TokenType.NUMBER:
                        stop = self.consume(TokenType.NUMBER).value

                    step = None
                    if self.peek().type == TokenType.COLON:
                        self.consume(TokenType.COLON)
                        if self.peek().type == TokenType.NUMBER:
                            step = self.consume(TokenType.NUMBER).value
                    selectors.append(SliceNode(start, stop, step))
                else:
                    selectors.append(IndexNode(start))
            elif token.type == TokenType.COLON:
                self.consume(TokenType.COLON)
                stop = None
                if self.peek().type == TokenType.NUMBER:
                    stop = self.consume(TokenType.NUMBER).value

                step = None
                if self.peek().type == TokenType.COLON:
                    self.consume(TokenType.COLON)
                    if self.peek().type == TokenType.NUMBER:
                        step = self.consume(TokenType.NUMBER).value
                selectors.append(SliceNode(None, stop, step))
            elif token.type == TokenType.STRING:
                selectors.append(FieldNode(self.consume(TokenType.STRING).value))
            elif token.type == TokenType.WILDCARD:
                self.consume(TokenType.WILDCARD)
                selectors.append(WildcardNode())
            elif token.type == TokenType.FILTER_START:
                selectors.append(self.parse_filter())

            if self.peek().type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
            elif self.peek().type != TokenType.RIGHT_BRACKET:
                 # If not comma and not right bracket, might be multiple selectors like [0,1]
                 pass

        self.consume(TokenType.RIGHT_BRACKET)
        if len(selectors) == 1:
            return selectors[0]
        return UnionNode(selectors)

    def parse_filter(self) -> FilterNode:
        if self.peek().type == TokenType.FILTER_START:
            self.consume(TokenType.FILTER_START)
        else:
            # This happens when parse_filter is called from parse_bracket which already saw ?(
            # But in my current lexer FILTER_START is '?(' as one token.
            pass

        expr = self.parse_expression()
        self.consume(TokenType.RIGHT_PAREN)
        # Note: if it was inside brackets, the bracket will consume the closing ']'
        return FilterNode(expr)

    def parse_expression(self) -> ExpressionNode:
        # Simple recursive descent for expressions
        return self.parse_or_expression()

    def parse_or_expression(self) -> ExpressionNode:
        left = self.parse_and_expression()
        while self.peek().type == TokenType.OPERATOR and self.peek().value == '||':
            op = self.consume(TokenType.OPERATOR).value
            right = self.parse_and_expression()
            left = BinaryExpressionNode(left, op, right)
        return left

    def parse_and_expression(self) -> ExpressionNode:
        left = self.parse_comparison_expression()
        while self.peek().type == TokenType.OPERATOR and self.peek().value == '&&':
            op = self.consume(TokenType.OPERATOR).value
            right = self.parse_comparison_expression()
            left = BinaryExpressionNode(left, op, right)
        return left

    def parse_comparison_expression(self) -> ExpressionNode:
        left = self.parse_primary_expression()
        if self.peek().type == TokenType.OPERATOR and self.peek().value in ('==', '!=', '<', '<=', '>', '>='):
            op = self.consume(TokenType.OPERATOR).value
            right = self.parse_primary_expression()
            return BinaryExpressionNode(left, op, right)
        return left

    def parse_primary_expression(self) -> ExpressionNode:
        token = self.peek()
        if token.type == TokenType.CURRENT:
            return self.parse_path_expression()
        elif token.type == TokenType.ROOT:
             return self.parse_path_expression()
        elif token.type == TokenType.STRING or token.type == TokenType.NUMBER:
            return LiteralNode(self.consume(token.type).value)
        elif token.type == TokenType.LEFT_PAREN:
            self.consume(TokenType.LEFT_PAREN)
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN)
            return expr
        elif token.type == TokenType.OPERATOR and token.value == '!':
            op = self.consume(TokenType.OPERATOR).value
            operand = self.parse_primary_expression()
            return UnaryExpressionNode(op, operand)
        elif token.type == TokenType.IDENTIFIER:
             # handle case where identifier is a literal like true, false, null
             val = self.consume(TokenType.IDENTIFIER).value
             if val == 'true': return LiteralNode(True)
             if val == 'false': return LiteralNode(False)
             if val == 'null': return LiteralNode(None)
             # If it's just an identifier, it might be a property of @
             return PathExpressionNode([CurrentNode(), FieldNode(val)])
        else:
            raise ValueError(f"Unexpected token in expression: {token.type} at {token.pos}")

    def parse_path_expression(self) -> PathExpressionNode:
        nodes = []
        token = self.peek()
        if token.type == TokenType.ROOT:
            self.consume(TokenType.ROOT)
            nodes.append(RootNode())
        elif token.type == TokenType.CURRENT:
            self.consume(TokenType.CURRENT)
            nodes.append(CurrentNode())

        while self.peek().type != TokenType.EOF:
            token = self.peek()
            if token.type == TokenType.DOT:
                self.consume(TokenType.DOT)
                next_token = self.peek()
                if next_token.type == TokenType.IDENTIFIER:
                    nodes.append(FieldNode(self.consume(TokenType.IDENTIFIER).value))
                elif next_token.type == TokenType.WILDCARD:
                    self.consume(TokenType.WILDCARD)
                    nodes.append(WildcardNode())
                elif next_token.type == TokenType.LEFT_BRACKET:
                     # Handled by the outer while loop's next iteration if we don't break
                     pass
                else:
                    break
            elif token.type == TokenType.LEFT_BRACKET:
                 # Simplified bracket parsing for paths inside expressions
                 self.consume(TokenType.LEFT_BRACKET)
                 next_token = self.peek()
                 if next_token.type == TokenType.STRING:
                     nodes.append(FieldNode(self.consume(TokenType.STRING).value))
                 elif next_token.type == TokenType.NUMBER:
                     nodes.append(IndexNode(self.consume(TokenType.NUMBER).value))
                 # Could support more here if needed
                 self.consume(TokenType.RIGHT_BRACKET)
            elif token.type == TokenType.IDENTIFIER and len(nodes) > 0 and isinstance(nodes[-1], CurrentNode):
                 # Handle @.length as @ length
                 # Wait, usually it's @.length. But some implementations might allow @length.
                 # Actually, my lexer handles @. as CURRENT then DOT.
                 break
            else:
                break

        # Special case for @.length or similar properties
        if len(nodes) == 1 and isinstance(nodes[0], (CurrentNode, RootNode)):
            # Check if followed by identifier WITHOUT dot? unlikely in standard but script can be [?(@.length > 5)]
            pass

        return PathExpressionNode(nodes)
