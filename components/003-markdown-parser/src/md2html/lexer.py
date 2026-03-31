import re
from typing import List, Tuple

class Lexer:
    """Lexer to identify block-level elements in Markdown text."""

    def __init__(self):
        # Patterns for block-level identification
        self.patterns = [
            ('heading', re.compile(r'^(#{1,6})\s+(.*)$')),
            ('hr', re.compile(r'^(\-{3,}|\*{3,})$')),
            ('blockquote', re.compile(r'^>\s?(.*)$')),
            ('unordered_list', re.compile(r'^([\s]{0,3})[\*\-\+]\s+(.*)$')),
            ('ordered_list', re.compile(r'^([\s]{0,3})(\d+)\.\s+(.*)$')),
            ('code_block_start', re.compile(r'^```(\w+)?$')),
            ('table_row', re.compile(r'^\|(.*)\|$')),
        ]

    def lex(self, text: str) -> List[Tuple[str, str, List[str]]]:
        """
        Splits text into lines and identifies block types.
        Returns a list of (type, content, metadata).
        """
        lines = text.splitlines()
        tokens = []
        in_code_block = False
        code_block_content = []
        code_block_lang = None

        for line in lines:
            if in_code_block:
                if line.strip() == "```":
                    tokens.append(('code_block', "\n".join(code_block_content), [code_block_lang]))
                    in_code_block = False
                    code_block_content = []
                    code_block_lang = None
                else:
                    code_block_content.append(line)
                continue

            matched = False
            for token_type, pattern in self.patterns:
                match = pattern.match(line)
                if match:
                    if token_type == 'heading':
                        level = len(match.group(1))
                        tokens.append(('heading', match.group(2), [str(level)]))
                    elif token_type == 'hr':
                        tokens.append(('hr', '', []))
                    elif token_type == 'blockquote':
                        tokens.append(('blockquote', match.group(1), []))
                    elif token_type == 'unordered_list':
                        indent = len(match.group(1))
                        tokens.append(('unordered_list', match.group(2), [str(indent)]))
                    elif token_type == 'ordered_list':
                        indent = len(match.group(1))
                        start = match.group(2)
                        tokens.append(('ordered_list', match.group(3), [str(indent), start]))
                    elif token_type == 'code_block_start':
                        in_code_block = True
                        code_block_lang = match.group(1)
                    elif token_type == 'table_row':
                        tokens.append(('table_row', match.group(1), []))

                    matched = True
                    break

            if not matched:
                if not line.strip():
                    tokens.append(('blank_line', '', []))
                else:
                    tokens.append(('paragraph', line, []))

        # Handle unclosed code block
        if in_code_block:
            tokens.append(('code_block', "\n".join(code_block_content), [code_block_lang]))

        return tokens
