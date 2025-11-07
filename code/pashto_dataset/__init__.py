"""
Pashto Dataset Processing System

A comprehensive system for processing and managing Pashto language datasets
with advanced pipeline orchestration capabilities.
"""

__version__ = "1.0.0"
__author__ = "Pashto Processing Team"

# Make key components easily importable
try:
    from code.pashto_dataset.text_processor.text_normalizer import PashtoTextNormalizer
    from code.pashto_dataset.text_processor.pashto_tokenizer import PashtoTokenizer
    from code.pashto_dataset.text_processor.quality_filter import QualityFilter
    from code.pashto_dataset.text_processor.deduplicator import Deduplicator
except ImportError:
    # Allow module to be imported even if dependencies are not installed yet
    pass

__all__ = [
    "PashtoTextNormalizer",
    "PashtoTokenizer", 
    "QualityFilter",
    "Deduplicator",
]