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
    """

    gen = LexerGenerator.from_dsl(dsl)
    code = gen.generate(class_name="MyLexer")

    lexer_file = tmp_path / "my_lexer.py"
    lexer_file.write_text(code)

    sys.path.append(str(tmp_path))
    try:
        from my_lexer import MyLexer

        lexer = MyLexer("if x1 = 123 + 456 # comment")
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

def test_multiline_pattern_in_generated_lexer(tmp_path):
    # Test that regex with newline is handled via repr()
    gen = LexerGenerator()
    gen.add_token("NEWLINE_PATTERN", "a\nb")
    gen.add_skip(" ")
    code = gen.generate(class_name="NewlineLexer")

    lexer_file = tmp_path / "newline_lexer.py"
    lexer_file.write_text(code)

    sys.path.append(str(tmp_path))
    try:
        from newline_lexer import NewlineLexer

        lexer = NewlineLexer("a\nb")
        tokens = list(lexer.tokenize())
        assert len(tokens) == 1
        assert tokens[0].type == "NEWLINE_PATTERN"
    finally:
        sys.path.remove(str(tmp_path))
        if "newline_lexer" in sys.modules:
            del sys.modules["newline_lexer"]
