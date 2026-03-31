import html
from typing import List, Union
from .nodes import (
    Node, InlineNode, BlockNode, Text, LineBreak, Emphasis, InlineCode, Link, Image,
    Heading, Paragraph, BlockQuote, ListItem, ListBlock, CodeBlock, Table, TableRow, TableCell,
    HorizontalRule, Document
)

class HTMLRenderer:
    """Renderer to convert Markdown AST to HTML."""

    def render(self, node: Node) -> str:
        """Entry point for rendering a node."""
        if isinstance(node, Document):
            return self._render_document(node)
        elif isinstance(node, Heading):
            return self._render_heading(node)
        elif isinstance(node, Paragraph):
            return self._render_paragraph(node)
        elif isinstance(node, BlockQuote):
            return self._render_blockquote(node)
        elif isinstance(node, ListBlock):
            return self._render_list_block(node)
        elif isinstance(node, ListItem):
            return self._render_list_item(node)
        elif isinstance(node, CodeBlock):
            return self._render_code_block(node)
        elif isinstance(node, Table):
            return self._render_table(node)
        elif isinstance(node, HorizontalRule):
            return self._render_horizontal_rule(node)
        elif isinstance(node, Text):
            return self._render_text(node)
        elif isinstance(node, LineBreak):
            return "<br />\n"
        elif isinstance(node, Emphasis):
            return self._render_emphasis(node)
        elif isinstance(node, InlineCode):
            return self._render_inline_code(node)
        elif isinstance(node, Link):
            return self._render_link(node)
        elif isinstance(node, Image):
            return self._render_image(node)
        else:
            return ""

    def _render_children(self, children: List[Union[Node, InlineNode, BlockNode]]) -> str:
        """Renders a list of child nodes."""
        return "".join(self.render(child) for child in children)

    def _render_document(self, node: Document) -> str:
        return self._render_children(node.children)

    def _render_heading(self, node: Heading) -> str:
        level = node.level
        content = self._render_children(node.children)
        return f"<h{level}>{content}</h{level}>\n"

    def _render_paragraph(self, node: Paragraph) -> str:
        content = self._render_children(node.children)
        if not content.strip():
            return ""
        return f"<p>{content}</p>\n"

    def _render_blockquote(self, node: BlockQuote) -> str:
        content = self._render_children(node.children)
        return f"<blockquote>\n{content}</blockquote>\n"

    def _render_list_block(self, node: ListBlock) -> str:
        tag = "ol" if node.ordered else "ul"
        start_attr = f' start="{node.start}"' if node.ordered and node.start != 1 else ""
        content = self._render_children(node.children)
        return f"<{tag}{start_attr}>\n{content}</{tag}>\n"

    def _render_list_item(self, node: ListItem) -> str:
        content = self._render_children(node.children)
        return f"<li>{content}</li>\n"

    def _render_code_block(self, node: CodeBlock) -> str:
        lang_class = f' class="language-{html.escape(node.language)}"' if node.language else ""
        content = html.escape(node.content)
        return f"<pre><code{lang_class}>{content}</code></pre>\n"

    def _render_table(self, node: Table) -> str:
        header_content = self._render_table_row(node.header)
        rows_content = "".join(self._render_table_row(row) for row in node.rows)
        return f"<table>\n<thead>\n{header_content}</thead>\n<tbody>\n{rows_content}</tbody>\n</table>\n"

    def _render_table_row(self, node: TableRow) -> str:
        cells_content = "".join(self._render_table_cell(cell) for cell in node.cells)
        return f"<tr>\n{cells_content}</tr>\n"

    def _render_table_cell(self, node: TableCell) -> str:
        tag = "th" if node.header else "td"
        align_attr = f' align="{node.align}"' if node.align else ""
        content = self._render_children(node.children)
        return f"<{tag}{align_attr}>{content}</{tag}>\n"

    def _render_horizontal_rule(self, node: HorizontalRule) -> str:
        return "<hr />\n"

    def _render_text(self, node: Text) -> str:
        return html.escape(node.content)

    def _render_emphasis(self, node: Emphasis) -> str:
        tags = {
            "bold": "strong",
            "italic": "em",
            "strike": "del"
        }
        tag = tags.get(node.style, "span")
        content = self._render_children(node.children)
        return f"<{tag}>{content}</{tag}>"

    def _render_inline_code(self, node: InlineCode) -> str:
        content = html.escape(node.content)
        return f"<code>{content}</code>"

    def _render_link(self, node: Link) -> str:
        url = html.escape(node.url)
        title_attr = f' title="{html.escape(node.title)}"' if node.title else ""
        content = self._render_children(node.children)
        return f'<a href="{url}"{title_attr}>{content}</a>'

    def _render_image(self, node: Image) -> str:
        url = html.escape(node.url)
        alt = html.escape(node.alt)
        title_attr = f' title="{html.escape(node.title)}"' if node.title else ""
        return f'<img src="{url}" alt="{alt}"{title_attr} />'
