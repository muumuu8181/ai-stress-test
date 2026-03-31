import math
from typing import Dict, List, Set, Tuple
from .index import InvertedIndex

class Ranker:
    """
    Ranks search results using the TF-IDF scoring algorithm.
    """

    def __init__(self, index: InvertedIndex):
        self.index = index

    def score(self, search_terms: List[str], doc_ids: Set[str]) -> List[Tuple[str, float]]:
        """
        Calculates scores for a set of documents based on the given search terms.
        """
        if not doc_ids:
            return []

        scores: Dict[str, float] = {doc_id: 0.0 for doc_id in doc_ids}
        total_docs = self.index.get_document_count()

        if total_docs == 0:
            return []

        # Use all constituent words and N-grams for scoring if available
        effective_terms = set()
        for term in search_terms:
            if not term: continue
            effective_terms.add(term)
            if ' ' in term:
                effective_terms.update(term.split())

        for term in effective_terms:
            df = self.index.df.get(term, 0)
            if df == 0:
                continue

            idf = math.log(total_docs / df)
            postings = self.index.get_postings(term)

            for doc_id in doc_ids:
                if doc_id in postings:
                    tf = len(postings[doc_id])
                    scores[doc_id] += (tf * idf)

        # Sort documents by score in descending order
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_scores
