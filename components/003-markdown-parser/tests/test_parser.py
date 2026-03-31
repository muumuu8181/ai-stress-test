import unittest
from md2html.parser import Parser, InlineParser
from md2html.nodes import Heading, Paragraph, Emphasis, InlineCode, Link, Image, HorizontalRule, CodeBlock, BlockQuote, ListBlock, Table, Document

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()
        self.inline_parser = InlineParser()

    def test_parse_heading(self):
        tokens = [('heading', 'Title', ['1'])]
        doc = self.parser.parse(tokens)
        self.assertIsInstance(doc.children[0], Heading)
        self.assertEqual(doc.children[0].level, 1)
        self.assertEqual(doc.children[0].children[0].content, 'Title')

    def test_parse_paragraph(self):
        tokens = [('paragraph', 'Line 1', []), ('paragraph', 'Line 2', [])]
        doc = self.parser.parse(tokens)
        self.assertIsInstance(doc.children[0], Paragraph)
        self.assertEqual(len(doc.children[0].children), 1)
        self.assertEqual(doc.children[0].children[0].content, 'Line 1 Line 2')

    def test_parse_hr(self):
        tokens = [('hr', '', [])]
        doc = self.parser.parse(tokens)
        self.assertIsInstance(doc.children[0], HorizontalRule)

    def test_parse_code_block(self):
        tokens = [('code_block', 'print()', ['python'])]
        doc = self.parser.parse(tokens)
        self.assertIsInstance(doc.children[0], CodeBlock)
        self.assertEqual(doc.children[0].content, 'print()')
        self.assertEqual(doc.children[0].language, 'python')

    def test_parse_blockquote(self):
        tokens = [('blockquote', 'Quote', [])]
        doc = self.parser.parse(tokens)
        self.assertIsInstance(doc.children[0], BlockQuote)
        self.assertIsInstance(doc.children[0].children[0], Paragraph)

    def test_parse_list(self):
        tokens = [('unordered_list', 'Item 1', ['0']), ('unordered_list', 'Item 2', ['0'])]
        doc = self.parser.parse(tokens)
        self.assertIsInstance(doc.children[0], ListBlock)
        self.assertFalse(doc.children[0].ordered)
        self.assertEqual(len(doc.children[0].children), 2)

    def test_parse_table(self):
        tokens = [('table_row', ' H1 | H2 ', []), ('paragraph', '|---|---|', []), ('table_row', ' D1 | D2 ', [])]
        doc = self.parser.parse(tokens)
        self.assertIsInstance(doc.children[0], Table)
        self.assertEqual(len(doc.children[0].header.cells), 2)
        self.assertEqual(len(doc.children[0].rows), 1)

    def test_inline_bold(self):
        nodes = self.inline_parser.parse("**bold**")
        self.assertIsInstance(nodes[0], Emphasis)
        self.assertEqual(nodes[0].style, 'bold')

    def test_inline_italic(self):
        nodes = self.inline_parser.parse("*italic*")
        self.assertIsInstance(nodes[0], Emphasis)
        self.assertEqual(nodes[0].style, 'italic')

    def test_inline_strike(self):
        nodes = self.inline_parser.parse("~~strike~~")
        self.assertIsInstance(nodes[0], Emphasis)
        self.assertEqual(nodes[0].style, 'strike')

    def test_inline_code(self):
        nodes = self.inline_parser.parse("`code`")
        self.assertIsInstance(nodes[0], InlineCode)
        self.assertEqual(nodes[0].content, 'code')

    def test_inline_link(self):
        nodes = self.inline_parser.parse("[text](url)")
        self.assertIsInstance(nodes[0], Link)
        self.assertEqual(nodes[0].url, 'url')

    def test_inline_image(self):
        nodes = self.inline_parser.parse("![alt](url)")
        self.assertIsInstance(nodes[0], Image)
        self.assertEqual(nodes[0].url, 'url')
        self.assertEqual(nodes[0].alt, 'alt')

if __name__ == '__main__':
    unittest.main()
