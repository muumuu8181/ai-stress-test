from jsonpath.lexer import Lexer, TokenType

def test_lexer_basic():
    l = Lexer("$.store.book[0].title")
    tokens = l.tokenize()
    types = [t.type for t in tokens]
    assert types == [
        TokenType.ROOT, TokenType.DOT, TokenType.IDENTIFIER, TokenType.DOT,
        TokenType.IDENTIFIER, TokenType.LEFT_BRACKET, TokenType.NUMBER,
        TokenType.RIGHT_BRACKET, TokenType.DOT, TokenType.IDENTIFIER, TokenType.EOF
    ]

def test_lexer_recursive():
    l = Lexer("$..author")
    tokens = l.tokenize()
    types = [t.type for t in tokens]
    assert types == [TokenType.ROOT, TokenType.DOUBLE_DOT, TokenType.IDENTIFIER, TokenType.EOF]

def test_lexer_wildcard():
    l = Lexer("$.*[*]")
    tokens = l.tokenize()
    types = [t.type for t in tokens]
    assert types == [TokenType.ROOT, TokenType.DOT, TokenType.WILDCARD, TokenType.LEFT_BRACKET, TokenType.WILDCARD, TokenType.RIGHT_BRACKET, TokenType.EOF]

def test_lexer_filter():
    l = Lexer("[?(@.price < 10)]")
    tokens = l.tokenize()
    types = [t.type for t in tokens]
    assert types == [
        TokenType.LEFT_BRACKET, TokenType.FILTER_START, TokenType.CURRENT,
        TokenType.DOT, TokenType.IDENTIFIER, TokenType.OPERATOR, TokenType.NUMBER,
        TokenType.RIGHT_PAREN, TokenType.RIGHT_BRACKET, TokenType.EOF
    ]

def test_lexer_string_and_comma():
    l = Lexer("['store', 'office']")
    tokens = l.tokenize()
    types = [t.type for t in tokens]
    assert types == [
        TokenType.LEFT_BRACKET, TokenType.STRING, TokenType.COMMA,
        TokenType.STRING, TokenType.RIGHT_BRACKET, TokenType.EOF
    ]
