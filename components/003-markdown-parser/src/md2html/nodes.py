from typing import List, Optional

class Node:
    """Base class for all AST nodes."""
    pass

class InlineNode(Node):
    """Base class for inline AST nodes."""
    pass

class BlockNode(Node):
    """Base class for block AST nodes."""
    pass

class Text(InlineNode):
    """Plain text node."""
    def __init__(self, content: str):
        self.content = content

class LineBreak(InlineNode):
    """Hard line break node."""
    pass

class Emphasis(InlineNode):
    """Emphasis node (bold, italic, strike)."""
    def __init__(self, style: str, children: List[InlineNode]):
        self.style = style  # 'bold', 'italic', 'strike'
        self.children = children

class InlineCode(InlineNode):
    """Inline code node."""
    def __init__(self, content: str):
        self.content = content

class Link(InlineNode):
    """Link node."""
    def __init__(self, url: str, children: List[InlineNode], title: Optional[str] = None):
        self.url = url
        self.children = children
        self.title = title

class Image(InlineNode):
    """Image node."""
    def __init__(self, url: str, alt: str, title: Optional[str] = None):
        self.url = url
        self.alt = alt
        self.title = title

class Heading(BlockNode):
    """Heading node."""
    def __init__(self, level: int, children: List[InlineNode]):
        self.level = level
        self.children = children

class Paragraph(BlockNode):
    """Paragraph node."""
    def __init__(self, children: List[InlineNode]):
        self.children = children

class BlockQuote(BlockNode):
    """Blockquote node."""
    def __init__(self, children: List[BlockNode]):
        self.children = children

class ListItem(BlockNode):
    """List item node."""
    def __init__(self, children: List[BlockNode]):
        self.children = children

class ListBlock(BlockNode):
    """List node (ordered or unordered)."""
    def __init__(self, ordered: bool, children: List[ListItem], start: int = 1):
        self.ordered = ordered
        self.children = children
        self.start = start

class CodeBlock(BlockNode):
    """Code block node."""
    def __init__(self, content: str, language: Optional[str] = None):
        self.content = content
        self.language = language

class TableCell(Node):
    """Table cell node."""
    def __init__(self, children: List[InlineNode], header: bool = False, align: Optional[str] = None):
        self.children = children
        self.header = header
        self.align = align

class TableRow(Node):
    """Table row node."""
    def __init__(self, cells: List[TableCell]):
        self.cells = cells

class Table(BlockNode):
    """Table node."""
    def __init__(self, header: TableRow, rows: List[TableRow]):
        self.header = header
        self.rows = rows

class HorizontalRule(BlockNode):
    """Horizontal rule node."""
    pass

class Document(Node):
    """Root node of the AST."""
    def __init__(self, children: List[BlockNode]):
        self.children = children
