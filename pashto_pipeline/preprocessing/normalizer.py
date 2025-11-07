"""
Pashto Text Normalizer
Handles normalization of Pashto text including Unicode normalization,
character standardization, and diacritic handling.
"""

import re
import unicodedata
from typing import Optional


class PashtoNormalizer:
    """
    Normalizer for Pashto text.
    
    Handles various normalization tasks including:
    - Unicode normalization
    - Character standardization
    - Whitespace normalization
    - Diacritic removal (optional)
    - Number normalization
    
    Example:
        >>> normalizer = PashtoNormalizer()
        >>> text = "سلام   دنیا"
        >>> normalized = normalizer.normalize(text)
    """
    
    # Pashto specific character mappings
    CHAR_MAPPINGS = {
        'ي': 'ی',  # Arabic Ya to Farsi Ye
        'ك': 'ک',  # Arabic Kaf to Farsi Kaf
        'ۀ': 'ه',  # Hamza above to He
    }
    
    # Pashto digits (Eastern Arabic-Indic)
    PASHTO_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
    ARABIC_DIGITS = '٠١٢٣٤٥٦٧٨٩'
    WESTERN_DIGITS = '0123456789'
    
    def __init__(
        self,
        unicode_form: str = 'NFC',
        remove_diacritics: bool = False,
        normalize_digits: Optional[str] = None,
        normalize_whitespace: bool = True
    ):
        """
        Initialize the normalizer.
        
        Args:
            unicode_form: Unicode normalization form (NFC, NFD, NFKC, NFKD)
            remove_diacritics: Whether to remove diacritical marks
            normalize_digits: Target digit system ('western', 'pashto', 'arabic', or None)
            normalize_whitespace: Whether to normalize whitespace
        """
        self.unicode_form = unicode_form
        self.remove_diacritics = remove_diacritics
        self.normalize_digits = normalize_digits
        self.normalize_whitespace = normalize_whitespace
        
    def normalize(self, text: str) -> str:
        """
        Apply all normalization steps to the text.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return text
            
        # Unicode normalization
        text = unicodedata.normalize(self.unicode_form, text)
        
        # Character standardization
        text = self._standardize_characters(text)
        
        # Remove diacritics if requested
        if self.remove_diacritics:
            text = self._remove_diacritics(text)
            
        # Normalize digits
        if self.normalize_digits:
            text = self._normalize_digits(text)
            
        # Normalize whitespace
        if self.normalize_whitespace:
            text = self._normalize_whitespace(text)
            
        return text
        
    def _standardize_characters(self, text: str) -> str:
        """Standardize Pashto characters to preferred forms."""
        for old_char, new_char in self.CHAR_MAPPINGS.items():
            text = text.replace(old_char, new_char)
        return text
        
    def _remove_diacritics(self, text: str) -> str:
        """Remove Arabic/Pashto diacritical marks."""
        # Remove combining marks (diacritics)
        text = ''.join(
            char for char in text
            if unicodedata.category(char) != 'Mn'
        )
        return text
        
    def _normalize_digits(self, text: str) -> str:
        """Normalize digits to the specified system."""
        if self.normalize_digits == 'western':
            # Convert Pashto and Arabic digits to Western
            trans_table = str.maketrans(
                self.PASHTO_DIGITS + self.ARABIC_DIGITS,
                self.WESTERN_DIGITS * 2
            )
            text = text.translate(trans_table)
        elif self.normalize_digits == 'pashto':
            # Convert Western and Arabic digits to Pashto
            trans_table = str.maketrans(
                self.WESTERN_DIGITS + self.ARABIC_DIGITS,
                self.PASHTO_DIGITS * 2
            )
            text = text.translate(trans_table)
        elif self.normalize_digits == 'arabic':
            # Convert Western and Pashto digits to Arabic
            trans_table = str.maketrans(
                self.WESTERN_DIGITS + self.PASHTO_DIGITS,
                self.ARABIC_DIGITS * 2
            )
            text = text.translate(trans_table)
            
        return text
        
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace (multiple spaces to single, trim)."""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Trim leading and trailing whitespace
        text = text.strip()
        return text
        
    def __call__(self, text: str) -> str:
        """Allow the normalizer to be called as a function."""
        return self.normalize(text)
