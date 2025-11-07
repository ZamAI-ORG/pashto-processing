"""
Stopwords removal for Pashto text.
"""

from typing import List, Set


class StopwordsRemover:
    """
    Remove common stopwords from Pashto text.
    
    Example:
        >>> remover = StopwordsRemover()
        >>> tokens = ['زه', 'په', 'ښار', 'کې', 'یم']
        >>> filtered = remover.remove(tokens)
    """
    
    # Common Pashto stopwords
    DEFAULT_STOPWORDS = {
        'په', 'کې', 'او', 'چې', 'د', 'له', 'څخه', 'ته', 'یو', 'یوه',
        'هغه', 'دا', 'دغه', 'هم', 'نه', 'نو', 'خو', 'که', 'ځکه',
        'کله', 'چېرته', 'څوک', 'څه', 'څنګه', 'ولې', 'کوم'
    }
    
    def __init__(self, custom_stopwords: Set[str] = None, use_defaults: bool = True):
        """
        Initialize stopwords remover.
        
        Args:
            custom_stopwords: Additional stopwords to include
            use_defaults: Whether to use default Pashto stopwords
        """
        self.stopwords = set()
        
        if use_defaults:
            self.stopwords.update(self.DEFAULT_STOPWORDS)
            
        if custom_stopwords:
            self.stopwords.update(custom_stopwords)
            
    def remove(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of tokens with stopwords removed
        """
        return [token for token in tokens if token not in self.stopwords]
        
    def add_stopwords(self, words: Set[str]) -> None:
        """Add new stopwords."""
        self.stopwords.update(words)
        
    def remove_stopwords(self, words: Set[str]) -> None:
        """Remove words from stopword list."""
        self.stopwords.difference_update(words)
        
    def __call__(self, tokens: List[str]) -> List[str]:
        """Allow the remover to be called as a function."""
        return self.remove(tokens)
