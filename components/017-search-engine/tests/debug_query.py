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

def test_debug_query(query_parser):
    import re
    query = '"lazy dog"'
    phrases = re.findall(r'"([^"]+)"', query)
    print(f"Phrases found: {phrases}")

    query2 = "rabbit*"
    prefixes = re.findall(r'(\w+)\*', query2)
    print(f"Prefixes found: {prefixes}")

    results = query_parser.search(query)
    print(f"Results for {query}: {results}")
