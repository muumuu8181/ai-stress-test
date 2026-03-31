from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Union


class TokenType(Enum):
    NUMBER = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    LPAREN = auto()
    RPAREN = auto()
    IDENTIFIER = auto()
    ASSIGN = auto()
    COMMA = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Optional[Union[float, str]] = None

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value})"


class ASTNode:
    pass


@dataclass
class NumberNode(ASTNode):
    value: float


@dataclass
class BinaryOpNode(ASTNode):
    left: ASTNode
    op: TokenType
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    op: TokenType
    expr: ASTNode


@dataclass
class FunctionCallNode(ASTNode):
    name: str
    args: List[ASTNode]


@dataclass
class VariableNode(ASTNode):
    name: str


@dataclass
class AssignmentNode(ASTNode):
    name: str
    expr: ASTNode
