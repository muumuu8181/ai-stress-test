import math
from typing import Dict, List, Set, Tuple
from .index import InvertedIndex

class Ranker:
    """
    Ranks search results using the TF-IDF scoring algorithm.
    """

    def __init__(self, index: InvertedIndex):
        self.index = index

    def score(self, query_terms: List[str], doc_ids: Set[str]) -> List[Tuple[str, float]]:
        """
        Calculates scores for a set of documents based on the given query terms.
        """
        scores: Dict[str, float] = {}
        total_docs = self.index.get_document_count()

        if total_docs == 0:
            return []

        for term in query_terms:
            df = self.index.df.get(term, 0)
            if df == 0:
                continue

            # Calculate IDF (Inverse Document Frequency)
            # log(N / df)
            idf = math.log(total_docs / df)

            postings = self.index.get_postings(term)
            for doc_id in doc_ids:
                if doc_id in postings:
                    # Calculate TF (Term Frequency)
                    tf = len(postings[doc_id])

                    # Accumulate TF-IDF score
                    scores[doc_id] = scores.get(doc_id, 0.0) + (tf * idf)

        # Sort documents by score in descending order
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_scores
