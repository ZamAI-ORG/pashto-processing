"""
Pashto Text Processing and Tokenization System

A comprehensive NLP toolkit for processing Pashto text including:
- Text normalization and cleaning for Arabic script
- Pashto-specific tokenization
- Quality filtering and scoring
- Deduplication
- Language detection
- Pashto linguistic features handling
"""

from .pashto_tokenizer import PashtoTokenizer
from .text_normalizer import PashtoTextNormalizer
from .quality_filter import QualityFilter
from .deduplicator import TextDeduplicator
from .language_detector import PashtoLanguageDetector
from .pashto_nlp_processor import PashtoNLPProcessor

__version__ = "1.0.0"
__author__ = "Pashto NLP System"

__all__ = [
    "PashtoTokenizer",
    "PashtoTextNormalizer", 
    "QualityFilter",
    "TextDeduplicator",
    "PashtoLanguageDetector",
    "PashtoNLPProcessor"
]