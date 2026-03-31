from .lexer import Lexer
from .parser import Parser
from .renderer import HTMLRenderer

def markdown_to_html(md_text: str) -> str:
    """
    Converts Markdown text to HTML.

    Args:
        md_text: The Markdown text to convert.

    Returns:
        The converted HTML string.
    """
    if md_text is None:
        return ""

    lexer = Lexer()
    parser = Parser()
    renderer = HTMLRenderer()

    tokens = lexer.lex(md_text)
    ast = parser.parse(tokens)
    html_output = renderer.render(ast)

    return html_output
