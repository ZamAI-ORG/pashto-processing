"""
Main PDF Processor for Pashto Documents

This module provides the main interface for processing Pashto PDFs with support
for both digital and scanned documents.
"""

import os
import logging
import traceback
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np
from .pashto_utils import PashtoTextUtils
from .ocr_handler import OCRHandler
from .metadata_extractor import MetadataExtractor
from .quality_assessor import QualityAssessor


class PashtoPDFProcessor:
    """
    Main class for processing Pashto PDF documents.
    
    Supports:
    - Digital PDF text extraction
    - OCR for scanned PDFs
    - Text cleaning and normalization
    - Metadata extraction
    - Quality assessment
    """
    
    def __init__(self, 
                 ocr_enabled: bool = True,
                 ocr_languages: str = "eng+pus",
                 log_level: str = "INFO"):
        """
        Initialize the PDF processor.
        
        Args:
            ocr_enabled: Whether to enable OCR for scanned documents
            ocr_languages: Tesseract languages for OCR (eng+pus for English+Pashto)
            log_level: Logging level
        """
        self.ocr_enabled = ocr_enabled
        self.ocr_languages = ocr_languages
        self.pashto_utils = PashtoTextUtils()
        self.ocr_handler = OCRHandler(ocr_languages)
        self.metadata_extractor = MetadataExtractor()
        self.quality_assessor = QualityAssessor()
        
        # Setup logging
        self._setup_logging(log_level)
        
        # Supported Pashto font patterns
        self.pashto_fonts = [
            'pashto', 'afghan', 'unicode', 'arabic', 'times new roman',
            'arial', 'helvetica', 'noto', 'jameel', 'scheherazade'
        ]
        
    def _setup_logging(self, level: str):
        """Setup logging configuration."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def process_pdf(self, 
                   pdf_path: str, 
                   output_dir: str = None,
                   extract_metadata: bool = True,
                   assess_quality: bool = True) -> Dict[str, Any]:
        """
        Process a Pashto PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted content
            extract_metadata: Whether to extract metadata
            assess_quality: Whether to assess text quality
            
        Returns:
            Dictionary containing processing results
        """
        try:
            self.logger.info(f"Processing PDF: {pdf_path}")
            
            # Validate input
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Create output directory if specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Extract metadata first
            metadata = {}
            if extract_metadata:
                metadata = self.metadata_extractor.extract_metadata(pdf_path)
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Process each page
            extracted_pages = []
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                try:
                    page = doc.load_page(page_num)
                    page_result = self._process_page(page, page_num + 1)
                    extracted_pages.append(page_result)
                    
                except Exception as e:
                    self.logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                    extracted_pages.append({
                        'page_number': page_num + 1,
                        'text': '',
                        'extraction_method': 'error',
                        'error': str(e)
                    })
            
            # Compile results
            result = {
                'pdf_path': pdf_path,
                'total_pages': total_pages,
                'processed_pages': len([p for p in extracted_pages if 'error' not in p]),
                'metadata': metadata,
                'pages': extracted_pages,
                'full_text': '\n'.join([p.get('text', '') for p in extracted_pages])
            }
            
            # Clean and normalize the full text
            result['cleaned_text'] = self.pashto_utils.clean_text(result['full_text'])
            result['normalized_text'] = self.pashto_utils.normalize_pashto(result['cleaned_text'])
            
            # Assess quality
            if assess_quality:
                result['quality_assessment'] = self.quality_assessor.assess_document(result)
            
            # Save results if output directory is specified
            if output_dir:
                self._save_results(result, output_dir)
            
            doc.close()
            
            self.logger.info(f"Successfully processed {result['processed_pages']} pages")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                'pdf_path': pdf_path,
                'error': str(e),
                'success': False
            }
    
    def _process_page(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """Process a single PDF page."""
        result = {
            'page_number': page_num,
            'text': '',
            'extraction_method': '',
            'confidence': 0.0,
            'font_info': []
        }
        
        try:
            # First, try to extract text directly
            text_dict = page.get_text("dict")
            extracted_text = self._extract_text_from_dict(text_dict)
            
            if extracted_text and self._is_pashto_text(extracted_text):
                result['text'] = extracted_text
                result['extraction_method'] = 'direct'
                result['confidence'] = 0.9
                result['font_info'] = self._extract_font_info(text_dict)
                return result
            
            # If no Pashto text found, try OCR
            if self.ocr_enabled:
                self.logger.info(f"Trying OCR for page {page_num}")
                ocr_result = self.ocr_handler.extract_text_from_page(page)
                
                if ocr_result['text']:
                    result['text'] = ocr_result['text']
                    result['extraction_method'] = 'ocr'
                    result['confidence'] = ocr_result.get('confidence', 0.0)
                    return result
            
            result['extraction_method'] = 'no_text'
            return result
            
        except Exception as e:
            self.logger.error(f"Error in page processing: {str(e)}")
            result['extraction_method'] = 'error'
            result['error'] = str(e)
            return result
    
    def _extract_text_from_dict(self, text_dict: Dict) -> str:
        """Extract text from PyMuPDF text dictionary."""
        text_blocks = []
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            text_blocks.append(text)
        
        return " ".join(text_blocks)
    
    def _is_pashto_text(self, text: str) -> bool:
        """Check if text contains Pashto characters."""
        if not text:
            return False
        
        # Check for Pashto Unicode ranges
        pashto_chars = sum(1 for char in text if ord(char) in self.pashto_utils.PASHTO_UNICODE_RANGES)
        total_chars = len([char for char in text if char.isalpha()])
        
        return pashto_chars > 0 and (pashto_chars / total_chars) > 0.1 if total_chars > 0 else False
    
    def _extract_font_info(self, text_dict: Dict) -> List[Dict]:
        """Extract font information from text dictionary."""
        fonts = []
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        font_info = {
                            'name': span.get("font", ""),
                            'size': span.get("size", 0),
                            'flags': span.get("flags", 0)
                        }
                        fonts.append(font_info)
        
        return fonts
    
    def _save_results(self, result: Dict[str, Any], output_dir: str):
        """Save processing results to files."""
        pdf_name = Path(result['pdf_path']).stem
        
        # Save full text
        with open(os.path.join(output_dir, f"{pdf_name}_full_text.txt"), 'w', encoding='utf-8') as f:
            f.write(result['full_text'])
        
        # Save cleaned text
        with open(os.path.join(output_dir, f"{pdf_name}_cleaned_text.txt"), 'w', encoding='utf-8') as f:
            f.write(result['cleaned_text'])
        
        # Save normalized text
        with open(os.path.join(output_dir, f"{pdf_name}_normalized_text.txt"), 'w', encoding='utf-8') as f:
            f.write(result['normalized_text'])
        
        # Save metadata
        if result.get('metadata'):
            import json
            with open(os.path.join(output_dir, f"{pdf_name}_metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(result['metadata'], f, ensure_ascii=False, indent=2)
        
        # Save quality assessment
        if result.get('quality_assessment'):
            with open(os.path.join(output_dir, f"{pdf_name}_quality_report.txt"), 'w', encoding='utf-8') as f:
                f.write(self._format_quality_report(result['quality_assessment']))
    
    def _format_quality_report(self, quality_report: Dict) -> str:
        """Format quality assessment report."""
        lines = ["TEXT QUALITY ASSESSMENT REPORT", "=" * 40, ""]
        
        for key, value in quality_report.items():
            if isinstance(value, dict):
                lines.append(f"{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    lines.append(f"  {sub_key.replace('_', ' ').title()}: {sub_value}")
                lines.append("")
            else:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(lines)
    
    def batch_process(self, 
                     pdf_directory: str, 
                     output_directory: str,
                     file_pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Process multiple PDF files in a directory.
        
        Args:
            pdf_directory: Directory containing PDF files
            output_directory: Directory to save results
            file_pattern: Pattern to match PDF files
            
        Returns:
            List of processing results for each file
        """
        pdf_dir = Path(pdf_directory)
        output_dir = Path(output_directory)
        output_dir.mkdir(exist_ok=True)
        
        pdf_files = list(pdf_dir.glob(file_pattern))
        results = []
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                file_output_dir = output_dir / pdf_file.stem
                file_output_dir.mkdir(exist_ok=True)
                
                result = self.process_pdf(
                    str(pdf_file), 
                    str(file_output_dir),
                    extract_metadata=True,
                    assess_quality=True
                )
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing {pdf_file}: {str(e)}")
                results.append({
                    'pdf_path': str(pdf_file),
                    'error': str(e),
                    'success': False
                })
        
        return results