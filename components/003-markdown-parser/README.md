# Markdown to HTML Converter

A simple Markdown to HTML converter built using only the Python standard library.

## Features

- **Headings**: `#` to `######`
- **Paragraphs & Line Breaks**
- **Emphasis**: `**bold**`, `*italic*`, `~~strike~~`, `` `code` ``
- **Links**: `[text](url "title")`
- **Images**: `![alt](url "title")`
- **Lists**:
  - Unordered: `*`, `-`, `+`
  - Ordered: `1.`, `2.`, etc.
  - Supports basic nesting (e.g., inside blockquotes)
- **Code Blocks**: \` \` \`language specify\` \` \`
- **Blockquotes**: `> Quote`
- **Tables**: `| header | header |`
- **Horizontal Rules**: `---`, `***`

## Usage

```python
from md2html import markdown_to_html

md_text = """
# Welcome to md2html

This is a **Markdown** to HTML converter.

- Feature 1
- Feature 2

[Visit GitHub](https://github.com)
"""

html_output = markdown_to_html(md_text)
print(html_output)
```

## Package Structure

- `src/md2html/`: Source code
  - `lexer.py`: Identifies block-level elements.
  - `parser.py`: Builds the AST (Abstract Syntax Tree).
  - `renderer.py`: Converts AST to HTML.
  - `nodes.py`: AST node definitions.
- `tests/`: Unit and integration tests.

## Quality Assurance

- **Testing**: 98% test coverage with `pytest`.
- **Type Hinting**: All public APIs include type hints.
- **Security**: HTML special characters are escaped to prevent XSS.
