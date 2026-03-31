import re
from typing import List, Tuple, NamedTuple, Optional

class TokenType:
    NUMBER = "NUMBER"
    STRING = "STRING"
    RANGE = "RANGE"
    CELL = "CELL"
    FUNCTION = "FUNCTION"
    OPERATOR = "OPERATOR"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"

class Token(NamedTuple):
    type: str
    value: str

class Lexer:
    """
    Lexer for spreadsheet formulas.
    """

    def __init__(self, formula: str) -> None:
        """
        Initialize the lexer.

        Args:
            formula: The formula string (without the leading '=').
        """
        self.formula: str = formula
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """
        Tokenize the formula string.

        Returns:
            A list of Token objects.
        """
        # Sheet name in single quotes or just plain: 'Sheet 1'! or Sheet1!
        SHEET_PATTERN = r"(?:(?:'[^']+')|[A-Za-z0-9_]+)!"
        # Range: (Sheet!)?A1:B5 or (Sheet!)?A:A
        RANGE_PATTERN = r"^(" + SHEET_PATTERN + r")?([A-Z]+[0-9]*:[A-Z]+[0-9]*)"
        # Cell: (Sheet!)?A1
        CELL_PATTERN = r"^(" + SHEET_PATTERN + r")?([A-Z]+[0-9]+)"
        # General function name
        FUNC_PATTERN = r"^[A-Z][A-Z0-9_]*"
        # Number
        NUM_PATTERN = r"^\d+(\.\d+)?"

        self.tokens = []
        pos = 0
        while pos < len(self.formula):
            if self.formula[pos].isspace():
                pos += 1
                continue

            substring = self.formula[pos:]

            # String with escaped quotes (double quotes "")
            if substring.startswith('"'):
                # Basic string handling but allow "" as escaped quote
                res = []
                idx = 1
                while idx < len(substring):
                    if substring[idx] == '"':
                        if idx + 1 < len(substring) and substring[idx+1] == '"':
                            res.append('"')
                            idx += 2
                        else:
                            # End of string
                            self.tokens.append(Token(TokenType.STRING, "".join(res)))
                            pos += idx + 1
                            break
                    else:
                        res.append(substring[idx])
                        idx += 1
                else:
                    raise ValueError("Unterminated string")
                continue

            # Parentheses, Commas, Operators
            if substring[0] == '(':
                self.tokens.append(Token(TokenType.LPAREN, '('))
                pos += 1
                continue
            if substring[0] == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')'))
                pos += 1
                continue
            if substring[0] == ',':
                self.tokens.append(Token(TokenType.COMMA, ','))
                pos += 1
                continue
            if substring[0] in '+-*/':
                self.tokens.append(Token(TokenType.OPERATOR, substring[0]))
                pos += 1
                continue

            # Number
            num_match = re.match(NUM_PATTERN, substring)
            if num_match:
                self.tokens.append(Token(TokenType.NUMBER, num_match.group()))
                pos += num_match.end()
                continue

            # Range
            range_match = re.match(RANGE_PATTERN, substring, re.IGNORECASE)
            if range_match:
                raw_val = range_match.group()
                # Normalize by converting address part to upper
                if '!' in raw_val:
                    sheet_part, rest = raw_val.split('!', 1)
                    # If sheet_part starts with ', it's already quoted
                    self.tokens.append(Token(TokenType.RANGE, f"{sheet_part}!{rest.upper()}"))
                else:
                    self.tokens.append(Token(TokenType.RANGE, raw_val.upper()))
                pos += range_match.end()
                continue

            # Cell or Function
            cell_match = re.match(CELL_PATTERN, substring, re.IGNORECASE)
            if cell_match:
                potential_name = cell_match.group()
                if '!' in potential_name:
                    sheet_part, cell_part = potential_name.split('!', 1)
                    self.tokens.append(Token(TokenType.CELL, f"{sheet_part}!{cell_part.upper()}"))
                    pos += cell_match.end()
                    continue

                after_match = substring[cell_match.end():].lstrip()
                if after_match.startswith('('):
                    self.tokens.append(Token(TokenType.FUNCTION, potential_name.upper()))
                    pos += cell_match.end()
                else:
                    self.tokens.append(Token(TokenType.CELL, potential_name.upper()))
                    pos += cell_match.end()
                continue

            # General Function
            func_match = re.match(FUNC_PATTERN, substring, re.IGNORECASE)
            if func_match:
                self.tokens.append(Token(TokenType.FUNCTION, func_match.group().upper()))
                pos += func_match.end()
                continue

            raise ValueError(f"Unexpected character at position {pos}: {self.formula[pos]}")

        return self.tokens
