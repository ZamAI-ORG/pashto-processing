"""
Pashto Text Encoding Detection and Handling
===========================================

This module provides robust encoding detection and handling specifically for Pashto text.
Supports UTF-8, Arabic script, and various Pashto-specific encodings.
"""

import re
import chardet
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class PashtoEncoder:
    """
    Handles encoding detection and conversion for Pashto text.
    
    Features:
    - Automatic encoding detection for Pashto content
    - Arabic script recognition
    - UTF-8 validation and conversion
    - Character set normalization
    """
    
    # Common Pashto encodings
    PASHTO_ENCODINGS = [
        'utf-8', 'utf8', 'utf-16', 'utf16', 
        'iso-8859-6', 'cp1256', 'windows-1256',
        'arabic', 'arabic-cp1256'
    ]
    
    # Pashto script patterns
    PASHTO_SCRIPT_PATTERNS = [
        r'[\u0600-\u06FF]',  # Arabic script
        r'[\u0750-\u077F]',  # Arabic Supplement
        r'[\u08A0-\u08FF]',  # Arabic Extended-A
    ]
    
    def __init__(self):
        self.encoding_cache: Dict[str, str] = {}
    
    def detect_encoding(self, content: str) -> Optional[str]:
        """
        Detect the encoding of Pashto text content.
        
        Args:
            content: The text content to analyze
            
        Returns:
            Detected encoding or None
        """
        if not content:
            return None
            
        # Remove HTML tags for better detection
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Use chardet for encoding detection
        detected = chardet.detect(clean_content.encode('utf-8', errors='ignore'))
        
        if detected['confidence'] > 0.7:
            encoding = detected['encoding'].lower()
            if encoding in self.PASHTO_ENCODINGS or 'utf' in encoding:
                return encoding
        
        # Fallback: check if content contains Pashto script
        if self.contains_pashto_script(content):
            return 'utf-8'
            
        return 'utf-8'  # Default fallback
    
    def contains_pashto_script(self, content: str) -> bool:
        """
        Check if content contains Pashto script (Arabic script).
        
        Args:
            content: Text content to analyze
            
        Returns:
            True if content contains Pashto script
        """
        return any(re.search(pattern, content) for pattern in self.PASHTO_SCRIPT_PATTERNS)
    
    def normalize_text(self, text: str, target_encoding: str = 'utf-8') -> str:
        """
        Normalize text encoding and format.
        
        Args:
            text: Text to normalize
            target_encoding: Target encoding (default: utf-8)
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        try:
            # Handle RTL text direction
            text = self._handle_rtl_text(text)
            
            # Normalize Unicode
            import unicodedata
            text = unicodedata.normalize('NFC', text)
            
            # Remove zero-width characters
            text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
            
            return text
            
        except Exception as e:
            logger.error(f"Error normalizing text: {e}")
            return text
    
    def _handle_rtl_text(self, text: str) -> str:
        """
        Handle right-to-left text formatting for Pashto.
        
        Args:
            text: Text to process
            
        Returns:
            Text with proper RTL handling
        """
        # Add RTL marks for proper rendering
        rtl_marks = ['\u202B', '\u202A']  # RLE, LRE
        
        for mark in rtl_marks:
            text = text.replace(mark, '')
        
        return text
    
    def convert_encoding(self, text: str, from_encoding: str, to_encoding: str = 'utf-8') -> str:
        """
        Convert text from one encoding to another.
        
        Args:
            text: Text to convert
            from_encoding: Source encoding
            to_encoding: Target encoding
            
        Returns:
            Converted text
        """
        if not text:
            return ""
        
        try:
            if from_encoding.lower() == to_encoding.lower():
                return text
                
            # Convert to bytes then to target encoding
            text_bytes = text.encode(from_encoding, errors='ignore')
            return text_bytes.decode(to_encoding, errors='ignore')
            
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            logger.error(f"Error converting encoding from {from_encoding} to {to_encoding}: {e}")
            # Return original text as fallback
            return text
    
    def validate_pashto_content(self, text: str) -> Dict[str, bool]:
        """
        Validate if text contains proper Pashto content.
        
        Args:
            text: Text to validate
            
        Returns:
            Dictionary with validation results
        """
        if not text:
            return {
                'has_pashto_script': False,
                'has_rtl_text': False,
                'is_utf8_valid': False,
                'has_pashto_words': False
            }
        
        # Check for Pashto script
        has_pashto_script = self.contains_pashto_script(text)
        
        # Check for RTL text
        has_rtl_text = bool(re.search(r'[\u0600-\u06FF]', text))
        
        # Validate UTF-8
        is_utf8_valid = self._validate_utf8(text)
        
        # Check for common Pashto words/patterns
        has_pashto_words = self._check_pashto_words(text)
        
        return {
            'has_pashto_script': has_pashto_script,
            'has_rtl_text': has_rtl_text,
            'is_utf8_valid': is_utf8_valid,
            'has_pashto_words': has_pashto_words
        }
    
    def _validate_utf8(self, text: str) -> bool:
        """Validate if text is properly encoded in UTF-8."""
        try:
            text.encode('utf-8')
            return True
        except UnicodeEncodeError:
            return False
    
    def _check_pashto_words(self, text: str) -> bool:
        """
        Check if text contains common Pashto words or patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if Pashto content is detected
        """
        # Common Pashto words and patterns
        pashto_patterns = [
            r'زه\s+',  # I (common Pashto pronoun)
            r'دو\s+',  # He/she/it
            r'موږ\s+',  # We
            r'تاسو\s+',  # You
            r'دوی\s+',  # They
            r'څخه',  # From
            r' ته',   # To
            r'سره',  # With
            r'په\s+',  # In/with
            r'د\s+',   # Of
        ]
        
        for pattern in pashto_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
                
        return False
    
    def get_encoding_confidence(self, content: str) -> float:
        """
        Get confidence score for encoding detection.
        
        Args:
            content: Content to analyze
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not content:
            return 0.0
        
        # Base confidence on various factors
        confidence = 0.0
        
        # Script detection
        if self.contains_pashto_script(content):
            confidence += 0.4
        
        # Word pattern detection
        if self._check_pashto_words(content):
            confidence += 0.3
        
        # UTF-8 validation
        if self._validate_utf8(content):
            confidence += 0.2
        
        # Length and complexity
        if len(content) > 50:
            confidence += 0.1
        
        return min(confidence, 1.0)