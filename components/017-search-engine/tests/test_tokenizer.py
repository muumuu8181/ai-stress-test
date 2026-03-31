import pytest
from searchengine.tokenizer import Tokenizer

def test_normalize():
    tokenizer = Tokenizer()
    assert tokenizer.normalize(" Hello  World ") == "hello world"
    assert tokenizer.normalize("PYTHON") == "python"
    assert tokenizer.normalize("") == ""
    assert tokenizer.normalize(None) == ""

def test_tokenize_simple():
    tokenizer = Tokenizer(ngram=2)
    tokens = tokenizer.tokenize("hello")
    # hello -> h, e, l, l, o
    # n-grams: he, el, ll, lo
    # tokens: hello, he, el, ll, lo
    assert "hello" in tokens
    assert "he" in tokens
    assert "el" in tokens
    assert "ll" in tokens
    assert "lo" in tokens

def test_tokenize_japanese_like():
    # N-gram is useful for CJK
    tokenizer = Tokenizer(ngram=2)
    tokens = tokenizer.tokenize("こんにちは")
    # こん, んに, にち, ちは
    assert "こんにちは" in tokens
    assert "こん" in tokens
    assert "んに" in tokens
    assert "にち" in tokens
    assert "ちは" in tokens

def test_tokenize_with_positions():
    tokenizer = Tokenizer(ngram=2)
    tokens_pos = tokenizer.tokenize_with_positions("abc def")
    # abc: (abc, 0), (ab, 0), (bc, 1)
    # def: (def, 4), (de, 4), (ef, 5)

    # Sort for consistent checking
    tokens_pos.sort()

    expected = [
        ("ab", 0), ("abc", 0), ("bc", 1),
        ("de", 4), ("def", 4), ("ef", 5)
    ]
    expected.sort()

    assert tokens_pos == expected
