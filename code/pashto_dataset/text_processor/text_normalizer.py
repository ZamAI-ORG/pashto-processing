"""
Pashto Text Normalizer

Handles text normalization and cleaning specific to Pashto Arabic script.
Features:
- Arabic script normalization
- Pashto character standardization
- Diacritic handling
- Tatweel (stretching character) removal
- Pashto-specific text cleaning
"""

import re
import unicodedata
from typing import List, Dict, Set, Tuple
import string

class PashtoTextNormalizer:
    """Pashto text normalizer for Arabic script processing"""
    
    def __init__(self):
        self.arabic_ranges = [
            (0x0600, 0x06FF),      # Arabic
            (0x0750, 0x077F),      # Arabic Supplement
            (0x08A0, 0x08FF),      # Arabic Extended-A
            (0xFB50, 0xFDFF),      # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),      # Arabic Presentation Forms-B
        ]
        
        # Pashto specific character mappings
        self.pashto_character_map = {
            # Convert similar looking characters to standard Pashto forms
            'ي': 'ی',  # Arabic letter to Pashto letter
            'ك': 'ک',  # Arabic kaf to Persian kaf
            'ه': 'ه',  # Standardize heh
        }
        
        # Characters to remove completely
        self.remove_chars = set([
            '\u0640',  # Tatweel (ـ)
            '\u064B',  # Fathatan
            '\u064C',  # Dammatan
            '\u064D',  # Kasratan
            '\u064E',  # Fatha
            '\u064F',  # Damma
            '\u0650',  # Kasra
            '\u0651',  # Shadda
            '\u0652',  # Sukun
            '\u0653',  # Maddah above
            '\u0654',  # Hamza above
            '\u0655',  # Hamza below
            '\u0656',  # Subscript Alef
            '\u0657',  # Inverted Damma
            '\u0658',  # Pre敦煌-ring
            '\u0659',  # Pre敦煌-zwarakay
            '\u065A',  # V above
            '\u065B',  # Dot above
            '\u065C',  # V below
            '\u065D',  # Dot below
            '\u065E',  # Wavy accent above
            '\u065F',  # Wavy accent below
        ])
        
        # Pashto specific patterns - simplified to avoid regex issues
        self.pashto_digits = '۰۱۲۳۴۵۶۷۸۹'
        self.arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        self.latin_digits = '0123456789'
        self.english_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        self.pashto_patterns = {
            'multiple_spaces': re.compile(r'\s+'),
        }
        
    def is_arabic_script(self, char: str) -> bool:
        """Check if character is from Arabic script ranges"""
        code = ord(char)
        for start, end in self.arabic_ranges:
            if start <= code <= end:
                return True
        return False
    
    def normalize_pashto_characters(self, text: str) -> str:
        """Normalize Pashto specific characters"""
        result = text
        for arabic_char, pashto_char in self.pashto_character_map.items():
            result = result.replace(arabic_char, pashto_char)
        return result
    
    def remove_diacritics_and_marks(self, text: str) -> str:
        """Remove diacritics and combining marks"""
        # Remove combining diacritical marks
        text = ''.join(char for char in text if char not in self.remove_chars)
        
        # Remove combining diacritical marks using Unicode categories
        normalized = unicodedata.normalize('NFKD', text)
        return ''.join(char for char in normalized if not unicodedata.combining(char))
    
    def remove_tatweel_and_extra_spaces(self, text: str) -> str:
        """Remove tatweel and normalize spacing"""
        # Remove tatweel
        text = re.sub(r'ـ+', '', text)
        
        # Normalize multiple spaces to single space
        text = self.pashto_patterns['multiple_spaces'].sub(' ', text)
        
        # Remove spaces at beginning and end
        text = text.strip()
        
        return text
    
    def standardize_numbers(self, text: str) -> str:
        """Standardize numbers to common format"""
        # Convert Pashto and Arabic digits to Latin digits
        pashto_digits = '۰۱۲۳۴۵۶۷۸۹'
        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        latin_digits = '0123456789'
        
        # Create individual translation mappings
        translation_dict = {}
        for i, char in enumerate(pashto_digits):
            translation_dict[ord(char)] = ord(latin_digits[i])
        for i, char in enumerate(arabic_digits):
            translation_dict[ord(char)] = ord(latin_digits[i])
        
        return text.translate(translation_dict)
    
    def handle_punctuation(self, text: str) -> str:
        """Handle and standardize punctuation"""
        # Replace various dash types with standard dash
        text = re.sub(r'[—–−]', '-', text)
        
        # Standardize quotes
        text = re.sub(r'[""''„]', '"', text)
        text = re.sub(r'['']', "'", text)
        
        return text
    
    def detect_script_mixing(self, text: str) -> Dict[str, any]:
        """Detect script mixing and provide statistics"""
        stats = {
            'has_arabic': False,
            'has_latin': False,
            'has_mixed': False,
            'arabic_ratio': 0.0,
            'latin_ratio': 0.0,
            'pashto_score': 0.0
        }
        
        if not text:
            return stats
            
        total_chars = len([c for c in text if c.strip()])
        if total_chars == 0:
            return stats
            
        arabic_count = sum(1 for c in text if self.is_arabic_script(c))
        latin_count = sum(1 for c in text if c.isascii() and c.isalpha())
        
        stats['has_arabic'] = arabic_count > 0
        stats['has_latin'] = latin_count > 0
        stats['has_mixed'] = stats['has_arabic'] and stats['has_latin']
        stats['arabic_ratio'] = arabic_count / total_chars
        stats['latin_ratio'] = latin_count / total_chars
        
        return stats
    
    def calculate_pashto_indicator_score(self, text: str) -> float:
        """Calculate how likely text is in Pashto based on character usage"""
        if not text:
            return 0.0
            
        # Common Pashto specific characters and their weights
        pashto_indicators = {
            'ځ': 2.0,   # Pashto-specific Tteh
            'څ': 2.0,   # Pashto-specific Tcheh
            'ډ': 2.0,   # Pashto-specific Dal-ring
            'ړ': 2.0,   # Pashto-specific Rail
            'ږ': 1.5,   # Pashto Ghayn
            'ګ': 1.5,   # Pashto Kaf
            'ڼ': 1.5,   # Pashto Noon-ring
        }
        
        score = 0.0
        total_weight = 0.0
        
        for char, weight in pashto_indicators.items():
            count = text.count(char)
            if count > 0:
                score += count * weight
                total_weight += weight
                
        # Normalize by text length
        text_length = len(text)
        if text_length > 0:
            score = (score / text_length) * 10  # Scale to 0-10 range
            
        return min(score, 10.0)
    
    def normalize(self, text: str) -> Tuple[str, Dict[str, any]]:
        """
        Main normalization function
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Tuple of (normalized_text, processing_stats)
        """
        if not text or not text.strip():
            return text or "", {"error": "Empty text provided"}
        
        stats = {
            "original_length": len(text),
            "processing_steps": [],
            "script_stats": {},
            "pashto_score": 0.0,
            "quality_metrics": {}
        }
        
        original_text = text
        
        # Step 1: Remove diacritics and combining marks
        text = self.remove_diacritics_and_marks(text)
        stats["processing_steps"].append("removed_diacritics")
        
        # Step 2: Normalize Pashto characters
        text = self.normalize_pashto_characters(text)
        stats["processing_steps"].append("normalized_pashto_chars")
        
        # Step 3: Remove tatweel and normalize spaces
        text = self.remove_tatweel_and_extra_spaces(text)
        stats["processing_steps"].append("normalized_spaces")
        
        # Step 4: Standardize numbers
        text = self.standardize_numbers(text)
        stats["processing_steps"].append("standardized_numbers")
        
        # Step 5: Handle punctuation
        text = self.handle_punctuation(text)
        stats["processing_steps"].append("handled_punctuation")
        
        # Calculate final statistics
        stats["final_length"] = len(text)
        stats["length_change_ratio"] = stats["final_length"] / stats["original_length"] if stats["original_length"] > 0 else 0
        stats["script_stats"] = self.detect_script_mixing(text)
        stats["pashto_score"] = self.calculate_pashto_indicator_score(text)
        
        # Quality metrics
        stats["quality_metrics"] = {
            "has_content": len(text.strip()) > 0,
            "script_purity": 1.0 - (1 if stats["script_stats"]["has_mixed"] else 0),
            "normalization_success": stats["final_length"] > 0 and stats["original_length"] >= stats["final_length"],
            "pashto_indicators": stats["pashto_score"] > 0
        }
        
        return text, stats
    
    def batch_normalize(self, texts: List[str]) -> List[Tuple[str, Dict[str, any]]]:
        """Process multiple texts in batch"""
        return [self.normalize(text) for text in texts]