from typing import Any, List, Optional, Union
from .lexer import Token, TokenType

class Expr:
    """Base class for all expression nodes."""
    pass

class BinaryExpr(Expr):
    """Binary operation expression (e.g., x + y)."""
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExpr(Expr):
    """Unary operation expression (e.g., -x, not x)."""
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

class LiteralExpr(Expr):
    """Literal value expression (e.g., 10, "hello", true)."""
    def __init__(self, value: Any):
        self.value = value

class GroupingExpr(Expr):
    """Parenthesized expression (e.g., (x + y))."""
    def __init__(self, expression: Expr):
        self.expression = expression

class VariableExpr(Expr):
    """Variable access expression (e.g., x)."""
    def __init__(self, name: Token):
        self.name = name

class AssignExpr(Expr):
    """Variable assignment expression (e.g., x = 10)."""
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

class ArrayExpr(Expr):
    """Array literal expression (e.g., [1, 2, 3])."""
    def __init__(self, elements: List[Expr]):
        self.elements = elements

class IndexExpr(Expr):
    """Array index access expression (e.g., arr[0])."""
    def __init__(self, array: Expr, bracket: Token, index: Expr):
        self.array = array
        self.bracket = bracket
        self.index = index

class CallExpr(Expr):
    """Function call expression (e.g., print(x))."""
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

class LogicalExpr(Expr):
    """Logical operation expression (e.g., a and b, a or b)."""
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

class Stmt:
    """Base class for all statement nodes."""
    pass

class ExpressionStmt(Stmt):
    """Statement consisting of a single expression."""
    def __init__(self, expression: Expr):
        self.expression = expression

class LetStmt(Stmt):
    """Variable declaration statement (e.g., let x = 10)."""
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

class BlockStmt(Stmt):
    """Block of statements (e.g., { stmt1; stmt2; })."""
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

class IfStmt(Stmt):
    """If-elif-else statement."""
    def __init__(self, condition: Expr, then_branch: Stmt, elif_branches: List[tuple[Expr, Stmt]], else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches
        self.else_branch = else_branch

class WhileStmt(Stmt):
    """While loop statement."""
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

class ForStmt(Stmt):
    """For-in loop statement (e.g., for x in arr { body })."""
    def __init__(self, item: Token, iterable: Expr, body: Stmt):
        self.item = item
        self.iterable = iterable
        self.body = body

class FunctionStmt(Stmt):
    """Function definition statement (e.g., fn name(a, b) { body })."""
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

class Parser:
    """Recursive descent parser for the programming language."""
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[Stmt]:
        """Parses the entire token stream and returns a list of statements."""
        statements: List[Stmt] = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Stmt:
        """Handles top-level declarations."""
        try:
            if self.match(TokenType.LET):
                return self.let_declaration()
            if self.match(TokenType.FN):
                return self.function_declaration()
            return self.statement()
        except SyntaxError as e:
            self.synchronize()
            raise e

    def let_declaration(self) -> Stmt:
        """Parses a variable declaration: let name = expression."""
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        self.consume(TokenType.EQUAL, "Expect '=' after variable name.")
        initializer = self.expression()
        return LetStmt(name, initializer)

    def function_declaration(self) -> FunctionStmt:
        """Parses a function definition."""
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")
        params: List[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before function body.")
        body = self.block()
        return FunctionStmt(name, params, body)

    def statement(self) -> Stmt:
        """Parses a single statement."""
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.LEFT_BRACE):
            return BlockStmt(self.block())
        return self.expression_statement()

    def if_statement(self) -> IfStmt:
        """Parses an if statement with optional elif and else branches."""
        condition = self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after if condition.")
        then_branch = BlockStmt(self.block())

        elif_branches = []
        while self.match(TokenType.ELIF):
            elif_cond = self.expression()
            self.consume(TokenType.LEFT_BRACE, "Expect '{' after elif condition.")
            elif_body = BlockStmt(self.block())
            elif_branches.append((elif_cond, elif_body))

        else_branch = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.LEFT_BRACE, "Expect '{' after else.")
            else_branch = BlockStmt(self.block())

        return IfStmt(condition, then_branch, elif_branches, else_branch)

    def while_statement(self) -> WhileStmt:
        """Parses a while loop."""
        condition = self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after while condition.")
        body = BlockStmt(self.block())
        return WhileStmt(condition, body)

    def for_statement(self) -> ForStmt:
        """Parses a for-in loop."""
        item = self.consume(TokenType.IDENTIFIER, "Expect variable name after 'for'.")
        self.consume(TokenType.IN, "Expect 'in' after variable name.")
        iterable = self.expression()
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after iterable.")
        body = BlockStmt(self.block())
        return ForStmt(item, iterable, body)

    def block(self) -> List[Stmt]:
        """Parses a block of statements."""
        statements: List[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self) -> Stmt:
        """Parses an expression statement."""
        expr = self.expression()
        return ExpressionStmt(expr)

    def expression(self) -> Expr:
        """Entry point for parsing an expression."""
        return self.assignment()

    def assignment(self) -> Expr:
        """Parses an assignment expression."""
        expr = self.logical_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, VariableExpr):
                name = expr.name
                return AssignExpr(name, value)

            raise SyntaxError(f"Invalid assignment target at {equals.lexeme}")

        return expr

    def logical_or(self) -> Expr:
        """Parses a logical OR expression."""
        expr = self.logical_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = LogicalExpr(expr, operator, right)
        return expr

    def logical_and(self) -> Expr:
        """Parses a logical AND expression."""
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = LogicalExpr(expr, operator, right)
        return expr

    def equality(self) -> Expr:
        """Parses equality expressions (==, !=)."""
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        """Parses comparison expressions (>, >=, <, <=)."""
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def term(self) -> Expr:
        """Parses term expressions (+, -)."""
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        """Parses factor expressions (*, /, %)."""
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.PERCENT):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        """Parses unary expressions (not, -)."""
        if self.match(TokenType.NOT, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpr(operator, right)
        return self.call()

    def call(self) -> Expr:
        """Parses function call and index access expressions."""
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.expression()
                bracket = self.previous()
                self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after index.")
                expr = IndexExpr(expr, bracket, index)
            else:
                break
        return expr

    def finish_call(self, callee: Expr) -> Expr:
        """Finishes parsing a function call's arguments."""
        arguments: List[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return CallExpr(callee, paren, arguments)

    def primary(self) -> Expr:
        """Parses primary expressions (literals, identifiers, groups, arrays)."""
        if self.match(TokenType.FALSE): return LiteralExpr(False)
        if self.match(TokenType.TRUE): return LiteralExpr(True)
        if self.match(TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING):
            return LiteralExpr(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return VariableExpr(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)
        if self.match(TokenType.LEFT_BRACKET):
            elements = []
            if not self.check(TokenType.RIGHT_BRACKET):
                while True:
                    elements.append(self.expression())
                    if not self.match(TokenType.COMMA):
                        break
            self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after array elements.")
            return ArrayExpr(elements)
        raise SyntaxError(f"Expect expression at {self.peek().lexeme}")

    def match(self, *types: TokenType) -> bool:
        """Returns True if the current token matches any of the types and advances."""
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        """Advances if the current token matches type, otherwise raises error."""
        if self.check(type): return self.advance()
        raise SyntaxError(f"{message} at {self.peek().lexeme}")

    def check(self, type: TokenType) -> bool:
        """Returns True if current token matches type without advancing."""
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self) -> Token:
        """Advances and returns the current token."""
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """Returns True if at the end of token stream."""
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        """Returns current token."""
        return self.tokens[self.current]

    def previous(self) -> Token:
        """Returns previous token."""
        return self.tokens[self.current - 1]

    def synchronize(self):
        """Discards tokens until a potential statement boundary is reached."""
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.EOF: return
            if self.peek().type in (TokenType.LET, TokenType.IF, TokenType.WHILE, TokenType.FOR, TokenType.FN):
                return
            self.advance()
