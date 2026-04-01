import re
from typing import List, Tuple, Optional

class DSLParserError(Exception):
    """Exception raised for errors during DSL parsing."""
    pass

class DSLDefinition:
    """Represents a lexer definition parsed from DSL."""
    def __init__(self):
        self.tokens: List[Tuple[str, str, int]] = []  # name, pattern, priority
        self.skips: List[str] = []  # patterns

class DSLParser:
    """Parses the Lexer Generator DSL.

    Syntax:
    %skip /pattern/
    TOKEN_NAME: /pattern/ [priority]
    """

    def parse(self, dsl_text: str) -> DSLDefinition:
        definition = DSLDefinition()
        lines = dsl_text.splitlines()

        for i, line in enumerate(lines, 1):
            original_line = line.strip()
            line = original_line
            if not line:
                continue

            # Strip trailing comments
            # Strategy: look for '#' outside of '/.../'
            # We assume '/' are only used for regex delimiters and they are balanced
            in_regex = False
            comment_start = -1
            for idx, char in enumerate(line):
                if char == '/':
                    # Check if it's escaped (simple check)
                    if idx == 0 or line[idx-1] != '\\':
                        in_regex = not in_regex
                elif char == '#' and not in_regex:
                    comment_start = idx
                    break

            if comment_start != -1:
                line = line[:comment_start].rstrip()

            if not line:
                continue

            # Skip rule: %skip /pattern/
            skip_match = re.match(r'^%skip\s+/(.*)/$', line)
            if skip_match:
                definition.skips.append(skip_match.group(1))
                continue

            # Token rule: TOKEN_NAME: /pattern/ [priority]
            token_match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*:\s*/(.*)/\s*(\d+)?$', line)
            if token_match:
                name = token_match.group(1)
                pattern = token_match.group(2)
                priority = int(token_match.group(3)) if token_match.group(3) else 0
                definition.tokens.append((name, pattern, priority))
                continue

            raise DSLParserError(f"Invalid DSL syntax at line {i}: {line}")

        return definition
