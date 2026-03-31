import unittest
from md2html.lexer import Lexer

class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_heading(self):
        tokens = self.lexer.lex("# Heading 1\n## Heading 2")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], ('heading', 'Heading 1', ['1']))
        self.assertEqual(tokens[1], ('heading', 'Heading 2', ['2']))

    def test_horizontal_rule(self):
        tokens = self.lexer.lex("---\n***")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], ('hr', '', []))
        self.assertEqual(tokens[1], ('hr', '', []))

    def test_blockquote(self):
        tokens = self.lexer.lex("> Quote")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], ('blockquote', 'Quote', []))

    def test_unordered_list(self):
        tokens = self.lexer.lex("* Item 1\n- Item 2")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], ('unordered_list', 'Item 1', ['0']))
        self.assertEqual(tokens[1], ('unordered_list', 'Item 2', ['0']))

    def test_ordered_list(self):
        tokens = self.lexer.lex("1. Item 1\n2. Item 2")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], ('ordered_list', 'Item 1', ['0', '1']))
        self.assertEqual(tokens[1], ('ordered_list', 'Item 2', ['0', '2']))

    def test_code_block(self):
        tokens = self.lexer.lex("```python\nprint('hello')\n```")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], ('code_block', "print('hello')", ['python']))

    def test_table_row(self):
        tokens = self.lexer.lex("| header1 | header2 |")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], ('table_row', ' header1 | header2 ', []))

    def test_paragraph(self):
        tokens = self.lexer.lex("Just a paragraph.")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0], ('paragraph', 'Just a paragraph.', []))

    def test_blank_line(self):
        tokens = self.lexer.lex("\n\n")
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], ('blank_line', '', []))
        self.assertEqual(tokens[1], ('blank_line', '', []))

if __name__ == '__main__':
    unittest.main()
