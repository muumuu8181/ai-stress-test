from jsonpath.lexer import Lexer
from jsonpath.parser import Parser
from jsonpath.nodes import RootNode, FieldNode, IndexNode, WildcardNode, RecursiveDescentNode, SliceNode, FilterNode, UnionNode

def test_parser_basic():
    tokens = Lexer("$.store.book[0].title").tokenize()
    nodes = Parser(tokens).parse()
    assert len(nodes) == 5
    assert isinstance(nodes[0], RootNode)
    assert isinstance(nodes[1], FieldNode)
    assert nodes[1].name == "store"
    assert isinstance(nodes[2], FieldNode)
    assert nodes[2].name == "book"
    assert isinstance(nodes[3], IndexNode)
    assert nodes[3].index == 0
    assert isinstance(nodes[4], FieldNode)
    assert nodes[4].name == "title"

def test_parser_recursive():
    tokens = Lexer("$..author").tokenize()
    nodes = Parser(tokens).parse()
    assert len(nodes) == 3
    assert isinstance(nodes[0], RootNode)
    assert isinstance(nodes[1], RecursiveDescentNode)
    assert isinstance(nodes[2], FieldNode)
    assert nodes[2].name == "author"

def test_parser_wildcard():
    tokens = Lexer("$.*[*]").tokenize()
    nodes = Parser(tokens).parse()
    assert len(nodes) == 3
    assert isinstance(nodes[0], RootNode)
    assert isinstance(nodes[1], WildcardNode)
    assert isinstance(nodes[2], WildcardNode)

def test_parser_slice():
    tokens = Lexer("$[:3]").tokenize()
    nodes = Parser(tokens).parse()
    assert len(nodes) == 2
    assert isinstance(nodes[0], RootNode)
    assert isinstance(nodes[1], SliceNode)
    assert nodes[1].start is None
    assert nodes[1].stop == 3

    tokens = Lexer("$[0:5:2]").tokenize()
    nodes = Parser(tokens).parse()
    assert len(nodes) == 2
    assert isinstance(nodes[1], SliceNode)
    assert nodes[1].start == 0
    assert nodes[1].stop == 5
    assert nodes[1].step == 2

def test_parser_union():
    tokens = Lexer("$['store', 'office']").tokenize()
    nodes = Parser(tokens).parse()
    assert len(nodes) == 2
    assert isinstance(nodes[0], RootNode)
    assert isinstance(nodes[1], UnionNode)
    assert len(nodes[1].selectors) == 2
    assert nodes[1].selectors[0].name == "store"
    assert nodes[1].selectors[1].name == "office"

def test_parser_filter():
    tokens = Lexer("$[?(@.price < 10)]").tokenize()
    nodes = Parser(tokens).parse()
    assert len(nodes) == 2
    assert isinstance(nodes[0], RootNode)
    assert isinstance(nodes[1], FilterNode)
