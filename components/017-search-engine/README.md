# Simple Python Full-text Search Engine

A lightweight, pure-Python full-text search engine implementing core information retrieval concepts.

## Features

- **Inverted Index**: Efficient mapping from terms to document IDs and positions.
- **Tokenization**: Supports whitespace splitting and N-gram (Bigram) tokenization (useful for CJK languages).
- **Ranking**: TF-IDF scoring algorithm for relevance.
- **Boolean Queries**: `AND`, `OR`, and `NOT` operators.
- **Phrase Search**: Exact matching for phrases wrapped in quotes (e.g., `"exact phrase"`).
- **Wildcard Search**: Prefix (`term*`) and suffix (`*term`) matching.
- **Persistence**: Save and load the index using JSON format.
- **Highlighting**: Automatic `<mark>` tagging of search terms in results.

## Installation

No external dependencies required. Built using only the Python standard library.

## Usage Example

```python
from searchengine.tokenizer import Tokenizer
from searchengine.index import InvertedIndex
from searchengine.ranker import Ranker
from searchengine.query import QueryParser
from searchengine.storage import Storage

# 1. Setup components
tokenizer = Tokenizer(ngram=2)
storage = Storage("index.json") # Optional: for persistence
index = InvertedIndex(tokenizer, storage)

# 2. Index documents
index.add_document("doc1", "The quick brown fox jumps over the lazy dog")
index.add_document("doc2", "Quick rabbits can run very fast")
index.add_document("doc3", "Full-text search is powerful")

# 3. Create search parser
ranker = Ranker(index)
parser = QueryParser(index, ranker)

# 4. Perform searches
# Simple search
results = parser.search("quick")

# Boolean search
results = parser.search("quick NOT fox")

# Phrase search
results = parser.search('"lazy dog"')

# Wildcard search
results = parser.search("rabbit*")

# 5. Display results
for res in results:
    print(f"ID: {res['id']}, Score: {res['score']:.4f}")
    print(f"Text: {res['text']}")
    print(f"Highlighted: {res['highlighted']}")
    print("-" * 20)
```

## Running Tests

To run the unit tests, use `pytest`:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests/
```

## Implementation Details

- **Tokenizer**: Lowercases text, removes extra whitespace, and generates both word tokens and character N-grams.
- **Index**: Stores document mappings and term frequencies. Supports incremental updates and deletions.
- **Ranker**: Uses standard TF-IDF (Term Frequency - Inverse Document Frequency) to rank documents.
- **Query Parser**: Linear evaluation of Boolean operators. Phrases are matched as exact substrings. Wildcards expand to matching terms in the index.
