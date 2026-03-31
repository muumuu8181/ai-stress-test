import unittest
from md2html import markdown_to_html

class TestEdgeCases(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(markdown_to_html(""), "")

    def test_null_input(self):
        self.assertEqual(markdown_to_html(None), "")

    def test_whitespace_only(self):
        self.assertEqual(markdown_to_html("   "), "")

    def test_multiple_blank_lines(self):
        self.assertEqual(markdown_to_html("\n\n\n"), "")

    def test_unclosed_bold(self):
        # Should be treated as plain text
        self.assertEqual(markdown_to_html("**bold"), "<p>**bold</p>\n")

    def test_unclosed_link(self):
        # Should be treated as plain text
        self.assertEqual(markdown_to_html("[text](url"), "<p>[text](url</p>\n")

    def test_nested_emphasis(self):
        self.assertEqual(markdown_to_html("**bold *italic***"), "<p><strong>bold <em>italic</em></strong></p>\n")

    def test_complex_nesting(self):
        # Nested list and blockquote
        md = "> - item 1\n> - item 2"
        html = markdown_to_html(md)
        self.assertIn("<blockquote>", html)
        self.assertIn("<ul>", html)

    def test_nested_list(self):
        md = "- item 1\n  - subitem 1\n- item 2"
        html = markdown_to_html(md)
        self.assertIn("<ul>", html)
        self.assertIn("<li>", html)
        self.assertEqual(html.count("<ul>"), 2)
        self.assertEqual(html.count("</ul>"), 2)

    def test_malformed_table(self):
        md = "| header1 |\n| --- |"
        html = markdown_to_html(md)
        self.assertIn("<table>", html)
        self.assertIn("<th>header1</th>", html)

    def test_long_input(self):
        md = "# Title\n\n" + "Paragraph\n\n" * 100
        html = markdown_to_html(md)
        self.assertIn("<h1>Title</h1>", html)
        self.assertEqual(html.count("<p>Paragraph</p>"), 100)

if __name__ == '__main__':
    unittest.main()
