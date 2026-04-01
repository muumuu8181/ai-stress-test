import textwrap
from typing import List, Tuple, Optional
from .dsl import DSLDefinition, DSLParser
from .core import BaseLexer, Token

class LexerGenerator:
    """Generates a Python lexer class from a DSL or manual rules."""

    def __init__(self, definition: Optional[DSLDefinition] = None):
        self.definition = definition or DSLDefinition()

    @classmethod
    def from_dsl(cls, dsl_text: str) -> 'LexerGenerator':
        """Creates a generator from DSL text."""
        parser = DSLParser()
        definition = parser.parse(dsl_text)
        return cls(definition)

    def add_token(self, name: str, pattern: str, priority: int = 0) -> None:
        """Manually adds a token rule."""
        self.definition.tokens.append((name, pattern, priority))

    def add_skip(self, pattern: str) -> None:
        """Manually adds a skip rule."""
        self.definition.skips.append(pattern)

    def generate(self, class_name: str = 'Lexer') -> str:
        """Generates the Python code for a self-contained lexer class."""

        # We need the core classes to be present in the generated code
        # Alternatively, we can import them, but the requirement was "standalone" or "from DSL to Python code".
        # Let's include the core logic in the generated file to make it more self-contained.

        core_code = textwrap.dedent("""
            import re
            from typing import List, Tuple, Callable, Optional, Iterator, Any, Dict, Union

            class LexerError(Exception):
                \"\"\"Exception raised for errors during lexing.\"\"\"
                def __init__(self, message: str, line: int, column: int):
                    super().__init__(f"{message} at line {line}, column {column}")
                    self.line = line
                    self.column = column

            class Token:
                \"\"\"Represents a token produced by the lexer.\"\"\"
                def __init__(self, type: str, value: str, line: int, column: int, offset: int):
                    self.type = type
                    self.value = value
                    self.line = line
                    self.column = column
                    self.offset = offset

                def __repr__(self) -> str:
                    return f"Token({self.type!r}, {self.value!r}, {self.line}, {self.column})"

            class LexerRule:
                \"\"\"Represents a rule for matching tokens.\"\"\"
                def __init__(self, name: str, pattern: str, action: Optional[Callable[['BaseLexer', Token], Optional[Token]]] = None, priority: int = 0):
                    self.name = name
                    self.pattern = re.compile(pattern, re.DOTALL | re.UNICODE)
                    self.action = action
                    self.priority = priority

            class BaseLexer:
                \"\"\"Base class for lexers.\"\"\"
                def __init__(self, text: str):
                    self.text: str = text
                    self.pos: int = 0
                    self.line: int = 1
                    self.column: int = 1
                    self.rules: List[LexerRule] = []
                    self.skip_rules: List[re.Pattern] = []
                    self.errors: List[LexerError] = []

                def add_rule(self, name: str, pattern: str, action: Optional[Callable[['BaseLexer', Token], Optional[Token]]] = None, priority: int = 0) -> None:
                    self.rules.append(LexerRule(name, pattern, action, priority))

                def add_skip_rule(self, pattern: str) -> None:
                    self.skip_rules.append(re.compile(pattern, re.DOTALL | re.UNICODE))

                def tokenize(self) -> Iterator[Token]:
                    while self.pos < len(self.text):
                        skipped = False
                        for skip_pattern in self.skip_rules:
                            match = skip_pattern.match(self.text, self.pos)
                            if match:
                                self._advance(match.end() - self.pos)
                                skipped = True
                                break
                        if skipped: continue
                        if self.pos >= len(self.text): break

                        matched = False
                        best_match = None
                        best_match_len = -1
                        best_rule = None

                        for rule in self.rules:
                            match = rule.pattern.match(self.text, self.pos)
                            if match:
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
                            if best_rule.action:
                                token = best_rule.action(self, token)
                            self._advance(len(value))
                            if token is not None:
                                yield token
                            matched = True

                        if not matched:
                            err_char = self.text[self.pos]
                            error = LexerError(f"Unexpected character {err_char!r}", self.line, self.column)
                            self.errors.append(error)
                            self._advance(1)

                def _advance(self, length: int) -> None:
                    for _ in range(length):
                        if self.text[self.pos] == '\\n':
                            self.line += 1
                            self.column = 1
                        else:
                            self.column += 1
                        self.pos += 1
        """).lstrip()

        class_definition = f"class {class_name}(BaseLexer):\n"
        class_definition += "    def __init__(self, text: str):\n"
        class_definition += "        super().__init__(text)\n"

        for pattern in self.definition.skips:
            # We use r'' for patterns, so we only need to escape single quotes
            escaped_pattern = pattern.replace("'", "\\'")
            class_definition += f"        self.add_skip_rule(r'{escaped_pattern}')\n"

        for name, pattern, priority in self.definition.tokens:
            escaped_pattern = pattern.replace("'", "\\'")
            class_definition += f"        self.add_rule('{name}', r'{escaped_pattern}', action=getattr(self, 'action_{name}', None), priority={priority})\n"

        return core_code + "\n" + class_definition
