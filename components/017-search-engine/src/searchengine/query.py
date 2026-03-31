import re
from typing import List, Set, Dict, Tuple, Optional, Any
from .index import InvertedIndex
from .ranker import Ranker
from .tokenizer import Tokenizer

class QueryParser:
    """
    Parses queries including Boolean operators (AND, OR, NOT), phrase search, and wildcards.
    Supports robust Boolean logic and proper scoring for all query types.
    """

    def __init__(self, index: InvertedIndex, ranker: Ranker):
        self.index = index
        self.ranker = ranker
        self.tokenizer = index.tokenizer

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        # 1. Tokenize query into units
        pattern = r'"[^"]+"|\S+\*|\*\S+|OR|AND|NOT|\S+'
        tokens = re.findall(pattern, query)
        if not tokens: return []

        all_doc_ids = set(self.index.documents.keys())
        current_docs: Set[str] = set()
        scoring_terms: List[str] = []

        # 2. Linear Boolean processing
        # Initial doc set: if first unit is NOT, start with everything.
        if tokens[0].upper() == "NOT":
            current_docs = all_doc_ids.copy()

        op = "AND"
        i = 0
        while i < len(tokens):
            token = tokens[i]
            token_upper = token.upper()

            if token_upper in ("AND", "OR", "NOT"):
                op = token_upper
                i += 1
                continue

            unit_docs, unit_terms = self._evaluate_unit(token)
            scoring_terms.extend(unit_terms)

            if i == 0:
                current_docs = unit_docs
            elif op == "AND":
                current_docs &= unit_docs
            elif op == "OR":
                current_docs |= unit_docs
            elif op == "NOT":
                current_docs -= unit_docs

            op = "AND" # Reset to default
            i += 1

        # 3. Rank and format
        ranked_docs = self.ranker.score(scoring_terms, current_docs)
        results = []
        for doc_id, score in ranked_docs:
            text = self.index.documents[doc_id]
            results.append({
                "id": doc_id, "score": score, "text": text,
                "highlighted": self.highlight(text, scoring_terms)
            })
        return results

    def _evaluate_unit(self, token: str) -> Tuple[Set[str], List[str]]:
        if token.startswith('"') and token.endswith('"'):
            phrase = token[1:-1]
            return self._phrase_search(phrase), phrase.split()

        if '*' in token:
            if token.startswith('*'): return self._wildcard_search(token[1:], False)
            if token.endswith('*'): return self._wildcard_search(token[:-1], True)

        term = token.lower()
        return set(self.index.get_postings(term).keys()), [term]

    def _phrase_search(self, phrase: str) -> Set[str]:
        matches = set()
        phrase_lower = phrase.lower()
        for doc_id, text in self.index.documents.items():
            if phrase_lower in text.lower(): matches.add(doc_id)
        return matches

    def _wildcard_search(self, pattern: str, is_prefix: bool) -> Tuple[Set[str], List[str]]:
        matches = set()
        terms = []
        pattern = pattern.lower()
        for term in self.index.df.keys():
            if (is_prefix and term.startswith(pattern)) or (not is_prefix and term.endswith(pattern)):
                matches |= set(self.index.get_postings(term).keys())
                terms.append(term)
        return matches, terms

    def highlight(self, text: str, query_terms: List[str]) -> str:
        if not query_terms: return text
        sorted_terms = sorted(set(t for t in query_terms if t), key=len, reverse=True)
        if not sorted_terms: return text
        pattern = re.compile('|'.join(re.escape(t) for t in sorted_terms), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", text)
