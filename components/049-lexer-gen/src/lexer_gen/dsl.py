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
            line = line.strip()
            if not line:
                continue

            # Strip trailing comments
            # Note: This is a simple strip. If /pattern/ contains #, it might fail.
            # But according to our DSL, /pattern/ is delimited by /.
            if '#' in line:
                # Find the last slash to avoid stripping # inside a regex /.../
                last_slash = line.rfind('/')
                if last_slash != -1:
                    comment_start = line.find('#', last_slash)
                    if comment_start != -1:
                        line = line[:comment_start].rstrip()
                else:
                    line = line.split('#')[0].rstrip()

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
