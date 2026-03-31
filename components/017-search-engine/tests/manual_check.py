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

def test_manual_check(query_parser):
    print("\nDocuments in index:")
    for id, text in query_parser.index.documents.items():
        print(f"{id}: {text}")

    print("\nSearch for '\"lazy dog\"':")
    res = query_parser.search('"lazy dog"')
    print(res)

    print("\nSearch for 'rabbit*':")
    res = query_parser.search('rabbit*')
    print(res)
