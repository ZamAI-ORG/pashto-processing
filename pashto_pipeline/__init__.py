"""
Pashto Processing Pipeline
A comprehensive text processing pipeline for Pashto language.
"""

__version__ = "0.1.0"
__author__ = "Pashto Processing Team"

from pashto_pipeline.core.pipeline import TextProcessingPipeline
from pashto_pipeline.preprocessing.normalizer import PashtoNormalizer
from pashto_pipeline.preprocessing.tokenizer import PashtoTokenizer

__all__ = [
    "TextProcessingPipeline",
    "PashtoNormalizer",
    "PashtoTokenizer",
]
