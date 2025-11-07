"""
Pashto Text Tokenizer
Handles tokenization of Pashto text into words, sentences, or other units.
"""

import re
from typing import List, Optional


class PashtoTokenizer:
    """
    Tokenizer for Pashto text.
    
    Provides tokenization at different levels:
    - Word tokenization
    - Sentence tokenization
    - Character tokenization
    
    Example:
        >>> tokenizer = PashtoTokenizer()
        >>> tokens = tokenizer.tokenize("سلام دنیا! څنګه یاست؟")
        >>> # ['سلام', 'دنیا', '!', 'څنګه', 'یاست', '؟']
    """
    
    # Pashto sentence boundary markers
    SENTENCE_DELIMITERS = ['؟', '!', '۔', '.', '،']
    
    # Pashto punctuation marks
    PUNCTUATION = [
        '،', '؍', '؎', '؏', '؛', '؟', '۔',  # Pashto/Arabic
        '.', ',', ';', ':', '!', '?', '-', '—',  # Western
        '(', ')', '[', ']', '{', '}', '"', "'", '«', '»'
    ]
    
    def __init__(
        self,
        preserve_punctuation: bool = True,
        lowercase: bool = False
    ):
        """
        Initialize the tokenizer.
        
        Args:
            preserve_punctuation: Whether to keep punctuation as separate tokens
            lowercase: Whether to convert to lowercase (not common for Pashto)
        """
        self.preserve_punctuation = preserve_punctuation
        self.lowercase = lowercase
        
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
            
        # Handle punctuation
        if self.preserve_punctuation:
            # Add spaces around punctuation for splitting
            for punct in self.PUNCTUATION:
                text = text.replace(punct, f' {punct} ')
                
        # Split on whitespace
        tokens = text.split()
        
        # Remove empty tokens
        tokens = [token for token in tokens if token.strip()]
        
        # Lowercase if requested (uncommon for Pashto)
        if self.lowercase:
            tokens = [token.lower() for token in tokens]
            
        return tokens
        
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text to split
            
        Returns:
            List of sentences
        """
        if not text:
            return []
            
        # Create regex pattern for sentence boundaries
        pattern = '|'.join(re.escape(delim) for delim in self.SENTENCE_DELIMITERS)
        
        # Split on sentence boundaries
        sentences = re.split(f'({pattern})', text)
        
        # Rejoin delimiters with sentences
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = (sentences[i] + sentences[i + 1]).strip()
                if sentence:
                    result.append(sentence)
            else:
                sentence = sentences[i].strip()
                if sentence:
                    result.append(sentence)
                    
        # Add last sentence if exists
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())
            
        return result
        
    def tokenize_chars(self, text: str) -> List[str]:
        """
        Tokenize text into characters.
        
        Args:
            text: Input text
            
        Returns:
            List of characters
        """
        return list(text)
        
    def detokenize(self, tokens: List[str]) -> str:
        """
        Join tokens back into text.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Joined text
        """
        if not tokens:
            return ""
            
        result = []
        for i, token in enumerate(tokens):
            # Don't add space before punctuation
            if i > 0 and token not in self.PUNCTUATION:
                result.append(' ')
            result.append(token)
            
        return ''.join(result)
        
    def __call__(self, text: str) -> List[str]:
        """Allow the tokenizer to be called as a function."""
        return self.tokenize(text)
