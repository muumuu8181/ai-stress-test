import re
from typing import List, Optional, Tuple, Any
from .nodes import (
    Node, InlineNode, BlockNode, Text, LineBreak, Emphasis, InlineCode, Link, Image,
    Heading, Paragraph, BlockQuote, ListItem, ListBlock, CodeBlock, Table, TableRow, TableCell,
    HorizontalRule, Document
)

class InlineParser:
    """Parser for inline Markdown elements."""

    def __init__(self):
        # Specific patterns to handle nested and unclosed marks
        # Bold: (**|__)
        # Italic: (*|_)
        self.bold_pattern = re.compile(r'(\*\*|__)(?=\S)(.+?[*_]*)(?<=\S)\1')
        self.italic_pattern = re.compile(r'(\*|_)(?=\S)(.+?)(?<=\S)\1')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^\s\)]+)(?:\s+"([^"]*)")?\)')
        self.link_pattern = re.compile(r'\[([^\]]*)\]\(([^\s\)]+)(?:\s+"([^"]*)")?\)')
        self.strike_pattern = re.compile(r'(~~)(?=\S)(.+?)(?<=\S)\1')
        self.code_pattern = re.compile(r'(`+)(.+?)\1')

    def parse(self, text: str) -> List[InlineNode]:
        """Parses text into a list of inline nodes."""
        if not text:
            return []

        nodes = []
        i = 0
        while i < len(text):
            matches = []

            m = self.image_pattern.search(text, i)
            if m: matches.append(('image', m))
            m = self.link_pattern.search(text, i)
            if m: matches.append(('link', m))
            m = self.bold_pattern.search(text, i)
            if m: matches.append(('bold', m))
            m = self.italic_pattern.search(text, i)
            if m: matches.append(('italic', m))
            m = self.strike_pattern.search(text, i)
            if m: matches.append(('strike', m))
            m = self.code_pattern.search(text, i)
            if m: matches.append(('code', m))

            if not matches:
                nodes.append(Text(text[i:]))
                break

            # Sort by start position, then by length (longer first)
            matches.sort(key=lambda x: (x[1].start(), -len(x[1].group(0))))

            best_token_type, best_match = matches[0]

            if best_match.start() > i:
                nodes.append(Text(text[i:best_match.start()]))

            content = best_match.group(2)
            if best_token_type == 'image':
                nodes.append(Image(best_match.group(2), best_match.group(1), best_match.group(3)))
            elif best_token_type == 'link':
                nodes.append(Link(best_match.group(2), self.parse(content), best_match.group(3)))
            elif best_token_type == 'bold':
                nodes.append(Emphasis('bold', self.parse(content)))
            elif best_token_type == 'italic':
                nodes.append(Emphasis('italic', self.parse(content)))
            elif best_token_type == 'strike':
                nodes.append(Emphasis('strike', self.parse(content)))
            elif best_token_type == 'code':
                nodes.append(InlineCode(content))

            i = best_match.end()

        return nodes

class Parser:
    """Parser for block-level Markdown elements."""

    def __init__(self):
        self.inline_parser = InlineParser()

    def parse(self, tokens: List[Tuple[str, str, List[str]]]) -> Document:
        """Parses tokens into a Document AST."""
        blocks = self._parse_blocks(tokens)
        return Document(blocks)

    def _parse_blocks(self, tokens: List[Tuple[str, str, List[str]]]) -> List[BlockNode]:
        blocks = []
        i = 0
        while i < len(tokens):
            token_type, content, meta = tokens[i]

            if token_type == 'heading':
                blocks.append(Heading(int(meta[0]), self.inline_parser.parse(content)))
                i += 1
            elif token_type == 'hr':
                blocks.append(HorizontalRule())
                i += 1
            elif token_type == 'code_block':
                blocks.append(CodeBlock(content, meta[0]))
                i += 1
            elif token_type == 'blockquote':
                bq_tokens = []
                while i < len(tokens) and tokens[i][0] == 'blockquote':
                    bq_line = tokens[i][1]
                    from .lexer import Lexer
                    inner_lexer = Lexer()
                    bq_tokens.extend(inner_lexer.lex(bq_line))
                    i += 1
                blocks.append(BlockQuote(self._parse_blocks(bq_tokens)))
            elif token_type in ('unordered_list', 'ordered_list'):
                list_type = token_type
                ordered = (list_type == 'ordered_list')
                start_index = i

                # Group list items of same level
                current_level_tokens = []
                base_indent = int(tokens[i][2][0])

                while i < len(tokens) and tokens[i][0] == list_type:
                    item_indent = int(tokens[i][2][0])
                    if item_indent == base_indent:
                        # Current level item
                        # Collect sub-items if any
                        item_content = tokens[i][1]
                        i += 1
                        sub_tokens = []
                        while i < len(tokens) and tokens[i][0] == list_type and int(tokens[i][2][0]) > base_indent:
                            sub_tokens.append(tokens[i])
                            i += 1

                        item_blocks = [Paragraph(self.inline_parser.parse(item_content))]
                        if sub_tokens:
                            item_blocks.extend(self._parse_blocks(sub_tokens))

                        current_level_tokens.append(ListItem(item_blocks))
                    else:
                        # This should not happen due to the logic above, but for safety:
                        break

                start_val = int(tokens[start_index][2][1]) if ordered else 1
                blocks.append(ListBlock(ordered, current_level_tokens, start_val))

            elif token_type == 'table_row':
                header_row = TableRow([TableCell(self.inline_parser.parse(cell.strip()), header=True) for cell in content.split('|') if cell.strip()])
                i += 1
                if i < len(tokens) and tokens[i][0] == 'paragraph' and re.match(r'^[\s\|:\-]+$', tokens[i][1]):
                    i += 1

                rows = []
                while i < len(tokens) and tokens[i][0] == 'table_row':
                    cells = [TableCell(self.inline_parser.parse(cell.strip())) for cell in tokens[i][1].split('|') if cell.strip()]
                    rows.append(TableRow(cells))
                    i += 1
                blocks.append(Table(header_row, rows))
            elif token_type == 'paragraph':
                para_content = [content]
                i += 1
                while i < len(tokens) and tokens[i][0] == 'paragraph':
                    para_content.append(tokens[i][1])
                    i += 1
                blocks.append(Paragraph(self.inline_parser.parse(" ".join(para_content))))
            elif token_type == 'blank_line':
                i += 1
            else:
                i += 1

        return blocks
