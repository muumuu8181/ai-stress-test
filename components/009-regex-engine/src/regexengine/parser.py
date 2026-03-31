from typing import List, Optional, Union, Tuple
from .lexer import Token, TokenType, Lexer

class ASTNode:
    """Base class for AST nodes."""
    pass

class LiteralNode(ASTNode):
    def __init__(self, char: str) -> None:
        self.char = char

class DotNode(ASTNode):
    pass

class CaretNode(ASTNode):
    pass

class DollarNode(ASTNode):
    pass

class QuantifierNode(ASTNode):
    def __init__(self, node: ASTNode, min_count: int, max_count: Optional[int]) -> None:
        self.node = node
        self.min_count = min_count
        self.max_count = max_count

class CharClassNode(ASTNode):
    def __init__(self, chars: List[str], ranges: List[Tuple[str, str]], negated: bool, special: Optional[str] = None) -> None:
        self.chars = chars
        self.ranges = ranges
        self.negated = negated
        self.special = special # 'd', 'w', 's' etc.

class GroupNode(ASTNode):
    def __init__(self, node: ASTNode, group_index: int) -> None:
        self.node = node
        self.group_index = group_index

class AlternationNode(ASTNode):
    def __init__(self, nodes: List[ASTNode]) -> None:
        self.nodes = nodes

class ConcatenationNode(ASTNode):
    def __init__(self, nodes: List[ASTNode]) -> None:
        self.nodes = nodes

class Parser:
    """
    Parser for regex patterns.
    Converts a list of Tokens into an AST.
    """
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.group_count = 0

    def peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.EOF, '')

    def advance(self) -> Token:
        token = self.peek()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def consume(self, expected_type: TokenType) -> Token:
        token = self.advance()
        if token.type != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token.type} at position {self.pos}")
        return token

    def parse(self) -> ASTNode:
        node = self.parse_alternation()
        if self.peek().type != TokenType.EOF:
            raise ValueError(f"Unexpected token {self.peek()} at position {self.pos}")
        return node

    def parse_alternation(self) -> ASTNode:
        nodes = [self.parse_concatenation()]
        while self.peek().type == TokenType.PIPE:
            self.advance()
            nodes.append(self.parse_concatenation())

        if len(nodes) == 1:
            return nodes[0]
        return AlternationNode(nodes)

    def parse_concatenation(self) -> ASTNode:
        nodes = []
        while True:
            token_type = self.peek().type
            if token_type in (TokenType.PIPE, TokenType.RPAREN, TokenType.EOF):
                break

            node = self.parse_quantifier()
            if node:
                nodes.append(node)
            else:
                # If we can't parse a quantifier/primary, we might be stuck.
                # In standard regex, some characters like ')' without '(' are literals or errors.
                # Here we'll treat unrecognized tokens as errors if they'd cause an infinite loop.
                # But parse_primary should handle most cases.
                break

        if not nodes:
            return LiteralNode("") # Empty string matches
        if len(nodes) == 1:
            return nodes[0]
        return ConcatenationNode(nodes)

    def parse_quantifier(self) -> Optional[ASTNode]:
        node = self.parse_primary()
        if not node:
            return None

        while True:
            token = self.peek()
            if token.type == TokenType.STAR:
                self.advance()
                node = QuantifierNode(node, 0, None)
            elif token.type == TokenType.PLUS:
                self.advance()
                node = QuantifierNode(node, 1, None)
            elif token.type == TokenType.QUESTION:
                self.advance()
                node = QuantifierNode(node, 0, 1)
            elif token.type == TokenType.LBRACE:
                self.advance()
                min_count, max_count = self.parse_brace_counts()
                self.consume(TokenType.RBRACE)
                node = QuantifierNode(node, min_count, max_count)
            else:
                break

        return node

    def parse_brace_counts(self) -> Tuple[int, Optional[int]]:
        num_str = ""
        while self.peek().type == TokenType.LITERAL and self.peek().value.isdigit():
            num_str += self.advance().value

        if not num_str:
            raise ValueError("Expected number in brace quantifier")

        min_count = int(num_str)
        max_count: Optional[int] = min_count

        if self.peek().type == TokenType.LITERAL and self.peek().value == ',':
            self.advance()
            num_str = ""
            while self.peek().type == TokenType.LITERAL and self.peek().value.isdigit():
                num_str += self.advance().value

            if num_str:
                max_count = int(num_str)
                if max_count < min_count:
                    raise ValueError(f"Max count {max_count} is less than min count {min_count}")
            else:
                max_count = None # {n,}
        elif self.peek().type == TokenType.RBRACE:
            pass # {n}

        return min_count, max_count

    def parse_primary(self) -> Optional[ASTNode]:
        token = self.peek()
        if token.type == TokenType.LITERAL:
            self.advance()
            return LiteralNode(token.value)
        elif token.type == TokenType.DOT:
            self.advance()
            return DotNode()
        elif token.type == TokenType.CARET:
            self.advance()
            return CaretNode()
        elif token.type == TokenType.DOLLAR:
            self.advance()
            return DollarNode()
        elif token.type == TokenType.ESCAPED:
            self.advance()
            if token.value in ('d', 'w', 's'):
                return CharClassNode([], [], False, special=token.value)
            return LiteralNode(token.value)
        elif token.type == TokenType.LPAREN:
            self.advance()
            self.group_count += 1
            current_group = self.group_count
            node = self.parse_alternation()
            self.consume(TokenType.RPAREN)
            return GroupNode(node, current_group)
        elif token.type == TokenType.LBRACKET:
            return self.parse_char_class()

        return None

    def parse_char_class(self) -> ASTNode:
        self.consume(TokenType.LBRACKET)
        negated = False
        if self.peek().type == TokenType.CARET:
            self.advance()
            negated = True

        chars = []
        ranges = []

        while self.peek().type != TokenType.RBRACKET and self.peek().type != TokenType.EOF:
            token = self.advance()
            if token.type == TokenType.EOF:
                raise ValueError("Unterminated character class")

            if token.type == TokenType.ESCAPED and token.value in ('d', 'w', 's'):
                # Expand shorthand classes inside []
                if token.value == 'd':
                    ranges.append(('0', '9'))
                elif token.value == 'w':
                    chars.append('_')
                    ranges.append(('a', 'z'))
                    ranges.append(('A', 'Z'))
                    ranges.append(('0', '9'))
                elif token.value == 's':
                    chars.extend([' ', '\t', '\n', '\r', '\f', '\v'])
                continue

            start_char = token.value

            if self.peek().type == TokenType.LITERAL and self.peek().value == '-':
                # Potential range
                self.advance()
                if self.peek().type == TokenType.RBRACKET:
                    # Trailing hyphen
                    chars.append(start_char)
                    chars.append('-')
                else:
                    end_char_token = self.advance()
                    if end_char_token.type == TokenType.EOF:
                        raise ValueError("Unterminated character class")
                    end_char = end_char_token.value
                    ranges.append((start_char, end_char))
            else:
                chars.append(start_char)

        if not chars and not ranges:
            raise ValueError("Empty character class")
        self.consume(TokenType.RBRACKET)
        return CharClassNode(chars, ranges, negated)
