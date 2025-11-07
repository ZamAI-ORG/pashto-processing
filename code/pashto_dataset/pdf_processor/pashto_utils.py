"""
Pashto Text Utilities

This module provides specialized utilities for handling Pashto text processing,
including encoding detection, text cleaning, and normalization.
"""

import re
import unicodedata
from typing import List, Dict, Set, Tuple
import string


class PashtoTextUtils:
    """
    Utility class for Pashto text processing and manipulation.
    """
    
    # Pashto Unicode ranges
    PASHTO_UNICODE_RANGES = [
        (0x0750, 0x077F),  # Pashto
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
        (0x0600, 0x06FF),  # Arabic
        (0x07C0, 0x07FF),  # NKo
    ]
    
    # Common Pashto punctuation and special characters
    PASHTO_PUNCTUATION = {
        '،': ',',  # Arabic comma
        '۔': '.',  # Arabic full stop
        '؟': '?',  # Arabic question mark
        '！': '!',  # Arabic exclamation mark
        '٫': '-',  # Arabic decimal separator
        '٬': ',',  # Arabic thousands separator
    }
    
    # Pashto stopwords (common words to filter out)
    PASHTO_STOPWORDS = {
        'د', 'په', 'سره', 'ته', 'له', 'څخه', 'ډول', 'لکه', 'نو', 'هم',
        'او', 'یا', 'مګر', 'خو', 'چې', 'که', 'نه', 'بل', 'نور', 'ډېر',
        'لومړی', 'دویم', 'دریم', 'شپږم', 'آخر', 'وړاندې', ' وروسته',
        'زموږ', 'زموږ', 'ستاسو', 'دوی', 'دوی', 'هغه', 'دا', 'داده',
        'دغه', 'دا', 'همغه', 'چې', 'که', 'نه', 'هو', 'ای', 'یا',
        'آ', 'اې', 'او', 'یو', 'دوه', 'درې', 'څلور', 'پنځه', 'شپږ',
        'اته', 'نهه', 'لس', 'شپږ', 'دووشپږ', 'شپږم', 'اشاره', 'بیا',
        'نو', 'اوس', 'بیا', 'بل', 'نو', 'دوباره', 'لا', 'تر', 'ترې',
        'سره', 'بې', 'سربېره', 'نږدې', 'لمر', 'لاسونو', 'ساته', 'ورځ',
        'شپه', 'سبا', 'پرون', 'نن', 'اوس', 'بیا', 'واړه', 'ټول', 'غوښتنه',
        'کول', 'کړل', 'کړ', 'لیکل', 'لیکل', 'ویل', 'راویستل', 'ورکول',
        'ګوتل', 'لیدل', 'اوریدل', 'خوندول', 'څکول', 'حس کول', 'زیاتول'
    }
    
    def __init__(self):
        """Initialize Pashto text utilities."""
        self.setup_regex_patterns()
    
    def setup_regex_patterns(self):
        """Setup regex patterns for Pashto text processing."""
        # Pashto character patterns
        self.pashto_char_pattern = self._build_pashto_char_pattern()
        self.english_char_pattern = re.compile(r'[a-zA-Z0-9]')
        
        # Common noise patterns
        self.noise_patterns = {
            'extra_spaces': re.compile(r'\s+'),
            'page_numbers': re.compile(r'^[\d\s]+$'),
            'line_numbers': re.compile(r'^[\d\s\.\-]+$'),
            'headers_footers': re.compile(r'^(?:Page\s+\d+|صفحه\s+\d+|pdf|djvu)'),
            'email_pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'url_pattern': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'phone_pattern': re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d'),
        }
        
        # Text cleaning patterns
        self.cleaning_patterns = {
            'multiple_newlines': re.compile(r'\n\s*\n+'),
            'leading_trailing_spaces': re.compile(r'^\s+|\s+$'),
            'multiple_dots': re.compile(r'\.{3,}'),
            'broken_words': re.compile(r'\b\w+-\n\w+\b'),
        }
    
    def _build_pashto_char_pattern(self) -> str:
        """Build regex pattern for Pashto characters."""
        char_ranges = []
        for start, end in self.PASHTO_UNICODE_RANGES:
            if start < 0x10000:
                char_ranges.append(f'\\u{start:04x}-\\u{end:04x}')
            else:
                char_ranges.append(f'\\U{start:08x}-\\U{end:08x}')
        
        return f'[{"|".join(char_ranges)}]'
    
    def detect_encoding(self, text: str) -> str:
        """
        Detect the text encoding based on character patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected encoding
        """
        if not text:
            return 'unknown'
        
        # Count different character types
        pashto_count = sum(1 for char in text if self._is_pashto_char(char))
        arabic_count = sum(1 for char in text if 0x0600 <= ord(char) <= 0x06FF)
        english_count = sum(1 for char in text if char in string.ascii_letters)
        total_chars = len([char for char in text if char.isalpha()])
        
        if total_chars == 0:
            return 'unknown'
        
        pashto_ratio = pashto_count / total_chars
        arabic_ratio = arabic_count / total_chars
        english_ratio = english_count / total_chars
        
        if pashto_ratio > 0.3:
            return 'pashto'
        elif arabic_ratio > 0.5:
            return 'arabic'
        elif english_ratio > 0.5:
            return 'english'
        else:
            return 'mixed'
    
    def _is_pashto_char(self, char: str) -> bool:
        """Check if a character is a Pashto character."""
        for start, end in self.PASHTO_UNICODE_RANGES:
            if start <= ord(char) <= end:
                return True
        return False
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize Pashto text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        # Normalize Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Replace Pashto punctuation with standard ones
        for pashto_punct, standard_punct in self.PASHTO_PUNCTUATION.items():
            text = text.replace(pashto_punct, standard_punct)
        
        # Apply noise removal
        for pattern_name, pattern in self.noise_patterns.items():
            if pattern_name in ['extra_spaces', 'multiple_newlines', 'leading_trailing_spaces']:
                text = pattern.sub(' ', text)
            else:
                text = pattern.sub(' ', text)
        
        # Clean up patterns
        for pattern_name, pattern in self.cleaning_patterns.items():
            if pattern_name == 'multiple_newlines':
                text = pattern.sub('\n\n', text)
            elif pattern_name == 'leading_trailing_spaces':
                text = pattern.sub('', text)
            elif pattern_name == 'broken_words':
                text = pattern.sub(lambda m: m.group(0).replace('\n', ''), text)
            else:
                text = pattern.sub('.', text)
        
        # Remove isolated characters (likely noise)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 2:  # Skip very short lines
                continue
            
            # Skip lines that are mostly numbers
            if sum(c.isdigit() for c in line) / len(line) > 0.7:
                continue
            
            # Skip page numbers
            if self.noise_patterns['page_numbers'].match(line):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def normalize_pashto(self, text: str) -> str:
        """
        Normalize Pashto text for better consistency.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Normalize Arabic diacritics and forms
        text = unicodedata.normalize('NFC', text)
        
        # Standardize common Pashto letter variations
        normalization_map = {
            'ډ': 'ډ',  # Daal
            'ړ': 'ړ',  # Raal
            'ږ': 'ږ',  # Gaaf
            'ښ': 'ښ',  # Sseen
            'ځ': 'ځ',  # Jeem
            'څ': 'څ',  # Che
            'ګ': 'ګ',  # Gaaf
            'ڼ': 'ڼ',  # Noon
        }
        
        for old_char, new_char in normalization_map.items():
            text = text.replace(old_char, new_char)
        
        # Fix common OCR errors
        text = re.sub(r'\b([Aa])\s+([Bb])\b', r'\1 \2', text)  # Fix separated characters
        
        # Normalize spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from Pashto text.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        # Common sentence endings in Pashto
        sentence_endings = r'[.!?۔؟!]'
        
        # Split by sentence endings
        sentences = re.split(sentence_endings, text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Keep meaningful sentences
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def extract_words(self, text: str) -> List[str]:
        """
        Extract words from Pashto text.
        
        Args:
            text: Input text
            
        Returns:
            List of words
        """
        if not text:
            return []
        
        # Split on whitespace and punctuation
        words = re.findall(r'\b\w+\b', text)
        
        # Filter out very short words and numbers
        words = [word for word in words if len(word) > 1 and not word.isdigit()]
        
        return words
    
    def get_word_frequency(self, text: str, min_length: int = 2) -> Dict[str, int]:
        """
        Calculate word frequency in text.
        
        Args:
            text: Input text
            min_length: Minimum word length to consider
            
        Returns:
            Dictionary of word frequencies
        """
        words = self.extract_words(text)
        words = [word for word in words if len(word) >= min_length]
        
        # Remove stopwords
        words = [word for word in words if word not in self.PASHTO_STOPWORDS]
        
        # Count frequencies
        frequency = {}
        for word in words:
            frequency[word] = frequency.get(word, 0) + 1
        
        return frequency
    
    def filter_noise_lines(self, lines: List[str]) -> List[str]:
        """
        Filter out noise lines from text.
        
        Args:
            lines: List of text lines
            
        Returns:
            Filtered list of lines
        """
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip very short lines
            if len(line) < 3:
                continue
            
            # Skip lines that are mostly punctuation
            if sum(c in string.punctuation for c in line) / len(line) > 0.5:
                continue
            
            # Skip lines with too many numbers
            digit_ratio = sum(c.isdigit() for c in line) / len(line)
            if digit_ratio > 0.7:
                continue
            
            # Skip common noise patterns
            skip_patterns = [
                r'^[\d\s\-]+$',  # Line numbers
                r'^pdf|^\s*djvu',  # File format indicators
                r'^page\s+\d+|^صفحه\s+\d+',  # Page numbers
                r'^header|^footer',  # Headers/footers
            ]
            
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if not should_skip:
                filtered_lines.append(line)
        
        return filtered_lines
    
    def get_text_statistics(self, text: str) -> Dict[str, int]:
        """
        Get basic statistics about the text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {}
        
        words = self.extract_words(text)
        sentences = self.extract_sentences(text)
        
        # Character counts
        total_chars = len(text)
        alphabetic_chars = sum(1 for char in text if char.isalpha())
        pashto_chars = sum(1 for char in text if self._is_pashto_char(char))
        
        # Line statistics
        lines = [line for line in text.split('\n') if line.strip()]
        
        stats = {
            'total_characters': total_chars,
            'alphabetic_characters': alphabetic_chars,
            'pashto_characters': pashto_chars,
            'pashto_ratio': pashto_chars / alphabetic_chars if alphabetic_chars > 0 else 0,
            'total_words': len(words),
            'unique_words': len(set(words)),
            'total_sentences': len(sentences),
            'total_lines': len(lines),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'avg_words_per_line': len(words) / len(lines) if lines else 0,
        }
        
        return stats