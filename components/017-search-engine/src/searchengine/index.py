from typing import Dict, List, Set, Optional, Any
from .tokenizer import Tokenizer
from .storage import Storage

class InvertedIndex:
    """
    An inverted index that maps terms to document IDs and their positions.
    """

    def __init__(self, tokenizer: Tokenizer, storage: Optional[Storage] = None):
        self.tokenizer = tokenizer
        self.storage = storage
        # term -> {doc_id -> [positions]}
        self.index: Dict[str, Dict[str, List[int]]] = {}
        # doc_id -> original_text
        self.documents: Dict[str, str] = {}
        # term -> document_frequency
        self.df: Dict[str, int] = {}

        if self.storage:
            self.load()

    def add_document(self, doc_id: str, text: str) -> None:
        """
        Adds a document to the index. If doc_id already exists, it updates it.
        """
        if doc_id in self.documents:
            self.remove_document(doc_id)

        self.documents[doc_id] = text
        tokens_with_positions = self.tokenizer.tokenize_with_positions(text)

        seen_terms_in_doc = set()
        for term, pos in tokens_with_positions:
            if term not in self.index:
                self.index[term] = {}
            if doc_id not in self.index[term]:
                self.index[term][doc_id] = []
            self.index[term][doc_id].append(pos)
            seen_terms_in_doc.add(term)

        for term in seen_terms_in_doc:
            self.df[term] = self.df.get(term, 0) + 1

        if self.storage:
            self.save()

    def remove_document(self, doc_id: str) -> None:
        """
        Removes a document from the index.
        """
        if doc_id not in self.documents:
            return

        text = self.documents[doc_id]
        tokens = set(self.tokenizer.tokenize(text))

        for term in tokens:
            if term in self.index and doc_id in self.index[term]:
                del self.index[term][doc_id]
                if not self.index[term]:
                    del self.index[term]

                self.df[term] -= 1
                if self.df[term] <= 0:
                    del self.df[term]

        del self.documents[doc_id]

        if self.storage:
            self.save()

    def update_document(self, doc_id: str, text: str) -> None:
        """
        Updates an existing document in the index.
        """
        self.add_document(doc_id, text)

    def get_postings(self, term: str) -> Dict[str, List[int]]:
        """
        Returns the postings list for a given term.
        """
        return self.index.get(term, {})

    def get_document_count(self) -> int:
        """
        Returns the total number of documents in the index.
        """
        return len(self.documents)

    def save(self) -> None:
        """
        Saves the current index state to storage.
        """
        if self.storage:
            data = {
                "index": self.index,
                "documents": self.documents,
                "df": self.df
            }
            self.storage.save(data)

    def load(self) -> None:
        """
        Loads the index state from storage.
        """
        if self.storage:
            data = self.storage.load()
            self.index = data.get("index", {})
            self.documents = data.get("documents", {})
            self.df = data.get("df", {})
