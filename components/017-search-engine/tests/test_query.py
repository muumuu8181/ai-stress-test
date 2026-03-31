import pytest
from searchengine.tokenizer import Tokenizer
from searchengine.index import InvertedIndex
from searchengine.ranker import Ranker
from searchengine.query import QueryParser

@pytest.fixture
def query_parser():
    index = InvertedIndex(Tokenizer())
    index.add_document("doc1", "The quick brown fox jumps over the lazy dog")
    index.add_document("doc2", "Quick rabbits can run very fast")
    index.add_document("doc3", "The lazy dog is sleeping")
    ranker = Ranker(index)
    return QueryParser(index, ranker)

def test_simple_search(query_parser):
    results = query_parser.search("quick")
    print(f"Results for 'quick': {results}")
    assert len(results) == 2

def test_phrase_search(query_parser):
    results = query_parser.search('"lazy dog"')
    print(f"Results for '\"lazy dog\"': {results}")
    assert len(results) == 2

def test_boolean_search(query_parser):
    results = query_parser.search("quick fox")
    assert len(results) == 1
    assert results[0]["id"] == "doc1"

    results = query_parser.search("fox OR rabbits")
    assert len(results) == 2

    results = query_parser.search("quick NOT fox")
    assert len(results) == 1
    assert results[0]["id"] == "doc2"

def test_wildcard_search(query_parser):
    results = query_parser.search("rabbit*")
    print(f"Results for 'rabbit*': {results}")
    assert len(results) == 1

    results = query_parser.search("*dog")
    print(f"Results for '*dog': {results}")
    assert len(results) == 2

def test_highlighting(query_parser):
    results = query_parser.search("quick")
    for res in results:
        assert "<mark>quick</mark>" in res["highlighted"].lower()
