import pytest
import os
from searchengine.tokenizer import Tokenizer
from searchengine.index import InvertedIndex
from searchengine.storage import Storage

@pytest.fixture
def index():
    return InvertedIndex(Tokenizer())

def test_add_document(index):
    index.add_document("doc1", "hello world")
    assert "doc1" in index.documents
    assert index.get_document_count() == 1
    # Check postings
    assert "hello" in index.index
    assert "doc1" in index.index["hello"]
    assert index.df["hello"] == 1

def test_remove_document(index):
    index.add_document("doc1", "hello world")
    index.remove_document("doc1")
    assert "doc1" not in index.documents
    assert index.get_document_count() == 0
    assert "hello" not in index.index
    assert "hello" not in index.df

def test_update_document(index):
    index.add_document("doc1", "hello world")
    index.update_document("doc1", "bye world")
    assert index.documents["doc1"] == "bye world"
    assert "hello" not in index.index
    assert "bye" in index.index
    assert index.df["bye"] == 1

def test_persistence(tmp_path):
    storage_path = str(tmp_path / "index.json")
    storage = Storage(storage_path)
    tokenizer = Tokenizer()

    idx1 = InvertedIndex(tokenizer, storage)
    idx1.add_document("doc1", "hello world")

    # Reload from storage
    idx2 = InvertedIndex(tokenizer, storage)
    assert "doc1" in idx2.documents
    assert idx2.documents["doc1"] == "hello world"
    assert "hello" in idx2.index
