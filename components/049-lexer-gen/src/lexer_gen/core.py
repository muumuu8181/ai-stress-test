import re
from typing import List, Tuple, Callable, Optional, Iterator, Any, Dict, Union

class LexerError(Exception):
    """Exception raised for errors during lexing.

    Attributes:
        message -- explanation of the error
        line -- line number where the error occurred
        column -- column number where the error occurred
    """
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"{message} at line {line}, column {column}")
        self.line = line
        self.column = column

class Token:
    """Represents a token produced by the lexer.

    Attributes:
        type -- the type of the token (e.g., 'NUMBER', 'IDENTIFIER')
        value -- the literal value of the token from the input text
        line -- the line number where the token starts (1-indexed)
        column -- the column number where the token starts (1-indexed)
        offset -- the byte or character offset from the start of the input
    """
    def __init__(self, type: str, value: str, line: int, column: int, offset: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.offset = offset

    def __repr__(self) -> str:
        return f"Token({self.type!r}, {self.value!r}, {self.line}, {self.column})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and
                self.value == other.value and
                self.line == other.line and
                self.column == other.column and
                self.offset == other.offset)

class LexerRule:
    """Represents a rule for matching tokens."""
    def __init__(self, name: str, pattern: str, action: Optional[Callable[['BaseLexer', Token], Optional[Token]]] = None, priority: int = 0):
        self.name = name
        self.pattern = re.compile(pattern, re.UNICODE)
        self.action = action
        self.priority = priority

class BaseLexer:
    """Base class for lexers.

    This class handles the core logic of scanning through text and matching patterns.
    """
    def __init__(self, text: str):
        self.text: str = text
        self.pos: int = 0
        self.line: int = 1
        self.column: int = 1
        self.rules: List[LexerRule] = []
        self.skip_rules: List[re.Pattern] = []
        self.errors: List[LexerError] = []

    def add_rule(self, name: str, pattern: str, action: Optional[Callable[['BaseLexer', Token], Optional[Token]]] = None, priority: int = 0) -> None:
        """Adds a token rule. Rules are checked in the order they are added.

        Longest match is preferred. If lengths are equal, higher priority is preferred.
        If priority is also equal, the first added rule is preferred.
        """
        # Ensure pattern does not match empty string to avoid infinite loop
        compiled = re.compile(pattern, re.UNICODE)
        if compiled.match(""):
            raise ValueError(f"Rule {name!r} pattern {pattern!r} matches empty string, which is not allowed.")
        self.rules.append(LexerRule(name, pattern, action, priority))

    def add_skip_rule(self, pattern: str) -> None:
        """Adds a pattern to skip (e.g., whitespace, comments)."""
        compiled = re.compile(pattern, re.UNICODE)
        if compiled.match(""):
            raise ValueError(f"Skip pattern {pattern!r} matches empty string, which is not allowed.")
        self.skip_rules.append(compiled)

    def tokenize(self) -> Iterator[Token]:
        """Iterates over the input text and yields tokens."""
        while self.pos < len(self.text):
            # Try to match skip rules first
            skipped = False
            for skip_pattern in self.skip_rules:
                match = skip_pattern.match(self.text, self.pos)
                if match and match.end() > self.pos:
                    self._advance(match.end() - self.pos)
                    skipped = True
                    break

            if skipped:
                continue

            if self.pos >= len(self.text):
                break

            # Try to match token rules
            matched = False
            best_match = None
            best_match_len = -1
            best_rule = None

            for rule in self.rules:
                match = rule.pattern.match(self.text, self.pos)
                if match and match.end() > self.pos:
                    match_len = len(match.group(0))
                    if (best_match is None or
                        match_len > best_match_len or
                        (match_len == best_match_len and rule.priority > best_rule.priority)):
                        best_match = match
                        best_match_len = match_len
                        best_rule = rule

            if best_match:
                start_pos = self.pos
                start_line = self.line
                start_column = self.column
                value = best_match.group(0)

                token = Token(best_rule.name, value, start_line, start_column, start_pos)

                # Apply action if provided
                if best_rule.action:
                    token = best_rule.action(self, token)

                self._advance(len(value))

                if token is not None:
                    yield token

                matched = True

            if not matched:
                # Error recovery: record the error and skip one character
                err_char = self.text[self.pos]
                error = LexerError(f"Unexpected character {err_char!r}", self.line, self.column)
                self.errors.append(error)
                self._advance(1)

    def _advance(self, length: int) -> None:
        """Advances the internal position and updates line/column tracking."""
        for _ in range(length):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
