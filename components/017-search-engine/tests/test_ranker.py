import pytest
from searchengine.tokenizer import Tokenizer
from searchengine.index import InvertedIndex
from searchengine.ranker import Ranker

def test_ranker_scoring():
    index = InvertedIndex(Tokenizer())
    index.add_document("doc1", "apple banana")
    index.add_document("doc2", "apple apple cherry")
    index.add_document("doc3", "banana")

    ranker = Ranker(index)

    # apple appears in doc1 (1 time) and doc2 (2 times). Total docs: 3, df(apple): 2.
    # Score for apple: TF * log(3/2)
    # doc2 should have higher score than doc1 for "apple"
    results = ranker.score(["apple"], {"doc1", "doc2", "doc3"})
    assert results[0][0] == "doc2"
    assert results[1][0] == "doc1"

    # "banana" appears in doc1 and doc3
    results = ranker.score(["banana"], {"doc1", "doc2", "doc3"})
    # Both doc1 and doc3 have banana once, scores should be equal
    assert results[0][1] == results[1][1]

def test_ranker_empty_index():
    index = InvertedIndex(Tokenizer())
    ranker = Ranker(index)
    results = ranker.score(["anything"], set())
    assert results == []
