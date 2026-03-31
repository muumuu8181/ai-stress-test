import re
from typing import List, Tuple

class Tokenizer:
    """
    A tokenizer that supports whitespace splitting and N-gram (Bigram) tokenization.
    """

    def __init__(self, ngram: int = 2):
        self.ngram = ngram

    def normalize(self, text: str) -> str:
        """
        Normalizes the input text by lowercasing and removing extra whitespaces.
        """
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Replace multiple whitespaces with a single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes the text using both whitespace and N-gram.
        """
        text = self.normalize(text)
        if not text:
            return []

        tokens = set()

        # Whitespace splitting
        words = text.split()
        for word in words:
            tokens.add(word)

            # N-gram for each word (if word is long enough)
            if len(word) >= self.ngram:
                for i in range(len(word) - self.ngram + 1):
                    tokens.add(word[i : i + self.ngram])
            else:
                # If word is shorter than ngram, just the word is already added
                pass

        return sorted(list(tokens))

    def tokenize_with_positions(self, text: str) -> List[Tuple[str, int]]:
        """
        Tokenizes the text and returns tokens with their start positions.
        This is useful for phrase search and highlighting.
        """
        normalized_text = self.normalize(text)
        if not normalized_text:
            return []

        # For positions, we need to be careful with the original text positions vs normalized.
        # But usually we index the normalized text.

        tokens_with_positions = []

        # Whitespace splitting with positions
        # Use finditer to get positions in normalized_text
        for match in re.finditer(r'\S+', normalized_text):
            word = match.group()
            start = match.start()
            tokens_with_positions.append((word, start))

            # N-gram
            if len(word) >= self.ngram:
                for i in range(len(word) - self.ngram + 1):
                    ngram_token = word[i : i + self.ngram]
                    tokens_with_positions.append((ngram_token, start + i))

        return tokens_with_positions
