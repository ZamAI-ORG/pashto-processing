"""
Pashto PDF Processing Module

A comprehensive PDF text extraction and processing module specifically designed 
for Pashto documents with support for both digital and scanned PDFs.

Features:
- Digital PDF text extraction with Pashto encoding support
- OCR capabilities for scanned documents
- Text cleaning and normalization
- Metadata extraction
- Text quality assessment
- Error handling and logging
"""

from .pdf_processor import PashtoPDFProcessor
from .pashto_utils import PashtoTextUtils
from .ocr_handler import OCRHandler
from .metadata_extractor import MetadataExtractor
from .quality_assessor import QualityAssessor

__version__ = "1.0.0"
__all__ = [
    "PashtoPDFProcessor",
    "PashtoTextUtils", 
    "OCRHandler",
    "MetadataExtractor",
    "QualityAssessor"
]