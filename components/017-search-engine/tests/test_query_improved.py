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

def test_complex_boolean(query_parser):
    # fox OR rabbits
    results = query_parser.search("fox OR rabbits")
    assert len(results) == 2

    # quick AND NOT fox
    results = query_parser.search("quick NOT fox")
    assert len(results) == 1
    assert results[0]["id"] == "doc2"

def test_not_only(query_parser):
    # NOT fox -> should return doc2 and doc3
    results = query_parser.search("NOT fox")
    assert len(results) == 2
    doc_ids = [r["id"] for r in results]
    assert "doc1" not in doc_ids
    assert "doc2" in doc_ids
    assert "doc3" in doc_ids

def test_wildcard_scoring(query_parser):
    # rabbit* should find doc2 and have positive score
    results = query_parser.search("rabbit*")
    assert len(results) == 1
    assert results[0]["score"] > 0
    assert "rabbits" in results[0]["highlighted"]

def test_phrase_boolean(query_parser):
    # fox OR "lazy dog" -> should find doc1 and doc3
    results = query_parser.search('fox OR "lazy dog"')
    assert len(results) == 2
    doc_ids = [r["id"] for r in results]
    assert "doc1" in doc_ids
    assert "doc3" in doc_ids
