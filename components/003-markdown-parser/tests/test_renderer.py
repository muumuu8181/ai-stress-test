import unittest
from md2html.renderer import HTMLRenderer
from md2html.nodes import (
    Heading, Paragraph, Text, Emphasis, InlineCode, Link, Image, CodeBlock, BlockQuote, ListBlock, ListItem, Table, TableRow, TableCell, HorizontalRule, Document
)

class TestRenderer(unittest.TestCase):
    def setUp(self):
        self.renderer = HTMLRenderer()

    def test_render_heading(self):
        node = Heading(1, [Text("Heading 1")])
        self.assertEqual(self.renderer.render(node), "<h1>Heading 1</h1>\n")

    def test_render_paragraph(self):
        node = Paragraph([Text("Hello World")])
        self.assertEqual(self.renderer.render(node), "<p>Hello World</p>\n")

    def test_render_bold(self):
        node = Paragraph([Emphasis('bold', [Text("bold")])])
        self.assertEqual(self.renderer.render(node), "<p><strong>bold</strong></p>\n")

    def test_render_italic(self):
        node = Paragraph([Emphasis('italic', [Text("italic")])])
        self.assertEqual(self.renderer.render(node), "<p><em>italic</em></p>\n")

    def test_render_strike(self):
        node = Paragraph([Emphasis('strike', [Text("strike")])])
        self.assertEqual(self.renderer.render(node), "<p><del>strike</del></p>\n")

    def test_render_inline_code(self):
        node = Paragraph([InlineCode("code")])
        self.assertEqual(self.renderer.render(node), "<p><code>code</code></p>\n")

    def test_render_link(self):
        node = Paragraph([Link("url", [Text("text")], "title")])
        self.assertEqual(self.renderer.render(node), '<p><a href="url" title="title">text</a></p>\n')

    def test_render_image(self):
        node = Paragraph([Image("url", "alt", "title")])
        self.assertEqual(self.renderer.render(node), '<p><img src="url" alt="alt" title="title" /></p>\n')

    def test_render_code_block(self):
        node = CodeBlock("print()", "python")
        self.assertEqual(self.renderer.render(node), '<pre><code class="language-python">print()</code></pre>\n')

    def test_render_blockquote(self):
        node = BlockQuote([Paragraph([Text("Quote")])])
        self.assertEqual(self.renderer.render(node), "<blockquote>\n<p>Quote</p>\n</blockquote>\n")

    def test_render_unordered_list(self):
        node = ListBlock(False, [ListItem([Paragraph([Text("Item 1")])])])
        self.assertEqual(self.renderer.render(node), "<ul>\n<li><p>Item 1</p>\n</li>\n</ul>\n")

    def test_render_ordered_list(self):
        node = ListBlock(True, [ListItem([Paragraph([Text("Item 1")])])], start=1)
        self.assertEqual(self.renderer.render(node), "<ol>\n<li><p>Item 1</p>\n</li>\n</ol>\n")

    def test_render_table(self):
        header = TableRow([TableCell([Text("H1")], header=True)])
        row = TableRow([TableCell([Text("D1")])])
        node = Table(header, [row])
        expected = "<table>\n<thead>\n<tr>\n<th>H1</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>D1</td>\n</tr>\n</tbody>\n</table>\n"
        self.assertEqual(self.renderer.render(node), expected)

    def test_render_hr(self):
        node = HorizontalRule()
        self.assertEqual(self.renderer.render(node), "<hr />\n")

    def test_html_escaping(self):
        node = Paragraph([Text("<script>alert('xss')</script>")])
        self.assertEqual(self.renderer.render(node), "<p>&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;</p>\n")

if __name__ == '__main__':
    unittest.main()
