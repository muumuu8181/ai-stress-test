import re
from typing import List, Set, Dict, Tuple, Optional, Any
from .index import InvertedIndex
from .ranker import Ranker
from .tokenizer import Tokenizer

class QueryParser:
    """
    Parses complex queries including Boolean operators, phrase search, and wildcards.
    """

    def __init__(self, index: InvertedIndex, ranker: Ranker):
        self.index = index
        self.ranker = ranker
        self.tokenizer = index.tokenizer

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a search query and returns ranked results with metadata.
        """
        if not query.strip():
            return []

        # Extract phrases
        phrases = re.findall(r'"([^"]+)"', query)

        # Extract wildcards
        prefixes = re.findall(r'(\w+)\*', query)
        suffixes = re.findall(r'\*(\w+)', query)

        # Remaining terms for boolean/simple search
        clean_query = query
        for p in phrases:
            clean_query = clean_query.replace(f'"{p}"', ' ')
        for p in prefixes:
            clean_query = clean_query.replace(f'{p}*', ' ')
        for s in suffixes:
            clean_query = clean_query.replace(f'*{s}', ' ')

        tokens = clean_query.split()

        must_not_docs = set()
        must_docs = set()
        or_docs = set()

        search_terms = []
        i = 0
        while i < len(tokens):
            token = tokens[i].upper()
            if token == "NOT" and i + 1 < len(tokens):
                not_term = tokens[i+1].lower()
                must_not_docs |= self._get_docs_with_term(not_term)
                i += 2
            elif token == "OR" and i + 1 < len(tokens):
                or_term = tokens[i+1].lower()
                or_docs |= self._get_docs_with_term(or_term)
                search_terms.append(or_term)
                i += 2
            elif token == "AND":
                i += 1
            else:
                term = tokens[i].lower()
                term_docs = self._get_docs_with_term(term)
                search_terms.append(term)
                if not must_docs and len(search_terms) == 1:
                     must_docs = term_docs
                else:
                     must_docs &= term_docs
                i += 1

        candidate_docs = set(self.index.documents.keys())
        has_positive_filter = False

        if tokens:
            candidate_docs &= must_docs
            has_positive_filter = True

        if phrases:
            has_positive_filter = True
            for phrase in phrases:
                phrase_matches = self._phrase_search(phrase)
                candidate_docs &= phrase_matches
                search_terms.append(phrase)

        if prefixes:
            has_positive_filter = True
            for prefix in prefixes:
                prefix_matches = self._prefix_search(prefix)
                candidate_docs &= prefix_matches
                search_terms.append(prefix)

        if suffixes:
            has_positive_filter = True
            for suffix in suffixes:
                suffix_matches = self._suffix_search(suffix)
                candidate_docs &= suffix_matches
                search_terms.append(suffix)

        if or_docs:
            has_positive_filter = True
            candidate_docs |= or_docs

        if not has_positive_filter:
            candidate_docs = set()

        candidate_docs -= must_not_docs

        # Rank candidates
        ranked_docs = self.ranker.score(search_terms, candidate_docs)

        # Format results
        results = []
        for doc_id, score in ranked_docs:
            text = self.index.documents[doc_id]
            highlighted = self.highlight(text, search_terms)
            results.append({
                "id": doc_id,
                "score": score,
                "text": text,
                "highlighted": highlighted
            })

        return results

    def _get_docs_with_term(self, term: str) -> Set[str]:
        postings = self.index.get_postings(term)
        return set(postings.keys())

    def _phrase_search(self, phrase: str) -> Set[str]:
        matches = set()
        for doc_id, text in self.index.documents.items():
            if phrase.lower() in text.lower():
                matches.add(doc_id)
        return matches

    def _prefix_search(self, prefix: str) -> Set[str]:
        matches = set()
        prefix = prefix.lower()
        for term in self.index.df.keys():
            if term.startswith(prefix):
                matches |= self._get_docs_with_term(term)
        return matches

    def _suffix_search(self, suffix: str) -> Set[str]:
        matches = set()
        suffix = suffix.lower()
        for term in self.index.df.keys():
            if term.endswith(suffix):
                matches |= self._get_docs_with_term(term)
        return matches

    def highlight(self, text: str, query_terms: List[str]) -> str:
        if not query_terms:
            return text
        sorted_terms = sorted(set(t for t in query_terms if t), key=len, reverse=True)
        if not sorted_terms:
            return text
        pattern = re.compile('|'.join(re.escape(t) for t in sorted_terms), re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", text)
