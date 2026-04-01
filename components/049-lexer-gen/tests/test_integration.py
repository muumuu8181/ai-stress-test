import os
import sys
import pytest
from lexer_gen.generator import LexerGenerator

def test_full_generation_flow(tmp_path):
    dsl = r"""
    %skip /[ \t\r\n]+/
    %skip /#.*/

    KEYWORD_IF: /if/ 10
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /\d+/
    PLUS: /\+/
    MINUS: /-/
    """

    gen = LexerGenerator.from_dsl(dsl)
    code = gen.generate(class_name="MyLexer")

    # Save the generated code to a temporary file
    lexer_file = tmp_path / "my_lexer.py"
    lexer_file.write_text(code)

    # Import the generated lexer
    sys.path.append(str(tmp_path))
    try:
        from my_lexer import MyLexer

        lexer = MyLexer("if x1 = 123 + 456 # comment")
        # Note: '=' is an invalid character in our DSL rules
        tokens = list(lexer.tokenize())

        assert len(tokens) == 5
        assert tokens[0].type == "KEYWORD_IF"
        assert tokens[1].type == "IDENTIFIER"
        assert tokens[1].value == "x1"
        assert tokens[2].type == "NUMBER"
        assert tokens[2].value == "123"
        assert tokens[3].type == "PLUS"
        assert tokens[4].type == "NUMBER"
        assert tokens[4].value == "456"

        assert len(lexer.errors) == 1
        assert "Unexpected character '='" in str(lexer.errors[0])

    finally:
        sys.path.remove(str(tmp_path))
        if "my_lexer" in sys.modules:
            del sys.modules["my_lexer"]

def test_custom_action_in_generated_lexer(tmp_path):
    dsl = r"""
    NUMBER: /\d+/
    %skip /\s+/
    """
    gen = LexerGenerator.from_dsl(dsl)
    code = gen.generate(class_name="ActionLexer")

    # Add custom action to the generated code
    code += "\n"
    code += "    def action_NUMBER(self, lexer, token):\n"
    code += "        token.value = int(token.value)\n"
    code += "        return token\n"

    lexer_file = tmp_path / "action_lexer.py"
    lexer_file.write_text(code)

    sys.path.append(str(tmp_path))
    try:
        from action_lexer import ActionLexer

        lexer = ActionLexer("123 456")
        tokens = list(lexer.tokenize())

        assert tokens[0].value == 123
        assert tokens[1].value == 456

    finally:
        sys.path.remove(str(tmp_path))
        if "action_lexer" in sys.modules:
            del sys.modules["action_lexer"]

def test_multiline_token_generation(tmp_path):
    dsl = r"""
    STRING: /'[^']*'/
    %skip /\s+/
    """
    gen = LexerGenerator.from_dsl(dsl)
    code = gen.generate(class_name="StringLexer")

    lexer_file = tmp_path / "string_lexer.py"
    lexer_file.write_text(code)

    sys.path.append(str(tmp_path))
    try:
        from string_lexer import StringLexer

        lexer = StringLexer("'multi\nline'")
        tokens = list(lexer.tokenize())

        assert len(tokens) == 1
        assert tokens[0].value == "'multi\nline'"
        assert tokens[0].line == 1
        assert lexer.line == 2

    finally:
        sys.path.remove(str(tmp_path))
        if "string_lexer" in sys.modules:
            del sys.modules["string_lexer"]
