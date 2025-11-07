"""
Metadata Extractor for Pashto PDF Documents

This module extracts and processes metadata from Pashto PDF documents
including title, author, creation date, and other document properties.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import fitz  # PyMuPDF
import json
from pathlib import Path


class MetadataExtractor:
    """
    Extracts and processes metadata from Pashto PDF documents.
    """
    
    def __init__(self):
        """Initialize metadata extractor."""
        # Common Pashto document title patterns
        self.title_patterns = [
            r'^(.+?)(?:\s*[\.\-\|]\s*|$)',  # Title at start
            r'(?:Title|سرلیک|عنوان)[:\s]*([^\n\r]+)',  # Explicit title field
            r'^([^\n\r]{10,100})(?:\n|$)',  # First meaningful line
        ]
        
        # Author name patterns (common Pashto/Afghan names)
        self.pashto_names = [
            'احمد', 'علي', 'حسين', 'محمد', 'عبدالله', 'حبيب', 'نور',
            'احمد', 'فريد', 'طاهر', 'غلام', 'عبدالرحمن', 'عبدالله',
            'احمد', 'سيد', 'شير', 'رحيم', 'صالح', 'مختار', 'موسي',
            'abdul', 'ahmad', 'ali', 'hussain', 'mohammad', 'khan',
            'ahmed', 'farid', 'tahir', 'gul', 'rahman', 'sayed'
        ]
        
        # Date patterns in various formats
        self.date_patterns = [
            r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b',  # YYYY-MM-DD
            r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b',  # DD-MM-YYYY
            r'\b(\d{4})\s+.*?(\d{1,2})\s+.*?(\d{1,2})\b',  # Persian/Arabic date
            r'January|February|March|April|May|June|July|August|September|October|November|December',
            r'جنوري|فبروري|مارچ|اپریل|مۍ|جون|جولای|اګست|سپټمبر|اکټوبر|نومبر|ډسمبر'
        ]
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted metadata
        """
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Extract basic metadata
            pdf_metadata = self._extract_pdf_metadata(doc)
            
            # Extract content-based metadata
            content_metadata = self._extract_content_metadata(doc)
            
            # Extract structural metadata
            structural_metadata = self._extract_structural_metadata(doc)
            
            # Extract language information
            language_info = self._detect_language_info(doc)
            
            # Compile all metadata
            all_metadata = {
                'file_info': {
                    'pdf_path': pdf_path,
                    'file_name': os.path.basename(pdf_path),
                    'file_size': os.path.getsize(pdf_path),
                    'creation_time': datetime.fromtimestamp(os.path.getctime(pdf_path)),
                    'modification_time': datetime.fromtimestamp(os.path.getmtime(pdf_path)),
                },
                'pdf_metadata': pdf_metadata,
                'content_metadata': content_metadata,
                'structural_metadata': structural_metadata,
                'language_info': language_info,
            }
            
            doc.close()
            
            return all_metadata
            
        except Exception as e:
            return {
                'error': str(e),
                'pdf_path': pdf_path,
                'extraction_successful': False
            }
    
    def _extract_pdf_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extract standard PDF metadata."""
        metadata = {}
        
        try:
            # Get basic PDF metadata
            pdf_info = doc.metadata
            
            # Map PDF metadata fields
            field_mapping = {
                'title': ['title', 'subject'],
                'author': ['author', 'creator'],
                'subject': ['subject', 'keywords'],
                'creator': ['creator', 'producer'],
                'producer': ['producer', 'creator'],
                'creationDate': ['creationDate', 'created'],
                'modDate': ['modDate', 'modified'],
            }
            
            for standard_field, possible_keys in field_mapping.items():
                for key in possible_keys:
                    if key in pdf_info and pdf_info[key]:
                        metadata[standard_field] = pdf_info[key]
                        break
            
            # Convert dates
            if 'creationDate' in metadata:
                metadata['creationDate'] = self._parse_pdf_date(metadata['creationDate'])
            
            if 'modDate' in metadata:
                metadata['modDate'] = self._parse_pdf_date(metadata['modDate'])
            
            # Add document statistics
            metadata['total_pages'] = len(doc)
            metadata['has_form_fields'] = bool(doc.get_page_fonts())
            metadata['has_embedded_fonts'] = len(doc.get_page_fonts()) > 0
            metadata['has_images'] = self._count_images(doc) > 0
            
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    def _extract_content_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extract metadata from document content."""
        content_info = {}
        
        try:
            # Extract text from first few pages to find titles, etc.
            sample_text = ""
            for page_num in range(min(5, len(doc))):  # First 5 pages
                page = doc.load_page(page_num)
                text_dict = page.get_text("dict")
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                sample_text += span.get("text", "") + " "
            
            # Find potential title
            content_info['potential_title'] = self._extract_potential_title(sample_text)
            
            # Find potential author
            content_info['potential_author'] = self._extract_potential_author(sample_text)
            
            # Find potential date
            content_info['potential_date'] = self._extract_potential_date(sample_text)
            
            # Extract keywords/tags
            content_info['potential_keywords'] = self._extract_potential_keywords(sample_text)
            
            # Find document type
            content_info['document_type'] = self._classify_document_type(sample_text)
            
        except Exception as e:
            content_info['extraction_error'] = str(e)
        
        return content_info
    
    def _extract_structural_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Extract structural metadata from the document."""
        structural = {}
        
        try:
            # Analyze page structure
            page_analysis = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get page text
                text_dict = page.get_text("dict")
                
                # Count elements
                text_blocks = len([b for b in text_dict.get("blocks", []) if "lines" in b])
                images = len([b for b in text_dict.get("blocks", []) if "type" in b and b["type"] == 1])
                drawings = len([b for b in text_dict.get("blocks", []) if "type" in b and b["type"] == 2])
                
                # Get page dimensions
                rect = page.rect
                
                page_info = {
                    'page_number': page_num + 1,
                    'text_blocks': text_blocks,
                    'images': images,
                    'drawings': drawings,
                    'width': rect.width,
                    'height': rect.height,
                }
                page_analysis.append(page_info)
            
            structural['page_analysis'] = page_analysis
            structural['total_pages'] = len(doc)
            structural['total_text_blocks'] = sum(p['text_blocks'] for p in page_analysis)
            structural['total_images'] = sum(p['images'] for p in page_analysis)
            structural['total_drawings'] = sum(p['drawings'] for p in page_analysis)
            structural['average_page_size'] = {
                'width': sum(p['width'] for p in page_analysis) / len(page_analysis),
                'height': sum(p['height'] for p in page_analysis) / len(page_analysis)
            }
            
        except Exception as e:
            structural['extraction_error'] = str(e)
        
        return structural
    
    def _detect_language_info(self, doc: fitz.Document) -> Dict[str, Any]:
        """Detect language and character encoding information."""
        lang_info = {}
        
        try:
            # Sample text from multiple pages
            sample_text = ""
            for page_num in range(min(10, len(doc))):
                page = doc.load_page(page_num)
                sample_text += page.get_text()
            
            # Detect character types
            char_analysis = self._analyze_character_types(sample_text)
            lang_info['character_analysis'] = char_analysis
            
            # Determine likely language
            language_score = self._score_pashto_content(sample_text)
            lang_info['pashto_confidence'] = language_score
            
            # Font analysis
            font_analysis = self._analyze_fonts(doc)
            lang_info['font_analysis'] = font_analysis
            
        except Exception as e:
            lang_info['extraction_error'] = str(e)
        
        return lang_info
    
    def _extract_potential_title(self, text: str) -> Optional[str]:
        """Extract potential title from text."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for title patterns
        for pattern in self.title_patterns:
            for line in lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    if len(title) > 5 and len(title) < 200:  # Reasonable title length
                        return title
        
        # If no pattern matches, use first substantial line
        for line in lines:
            if len(line) > 10 and len(line) < 200:
                return line
        
        return None
    
    def _extract_potential_author(self, text: str) -> Optional[str]:
        """Extract potential author name from text."""
        # Common author indicators
        author_indicators = [
            r'(?:نویسنده|لیکوال|تألیف|ژباړه|Translation|Author|Author:)',
            r'(?:by|written by|prepared by|compiled by)',
        ]
        
        for pattern in author_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Look for name patterns after the indicator
                name_pattern = r'(?:نویسنده|لیکوال|تألیف|ژباړه|Translation|Author|Author:)\s*[:\-]?\s*([A-Za-z\s\.]+)'
                name_matches = re.findall(name_pattern, text, re.IGNORECASE)
                if name_matches:
                    return name_matches[0].strip()
        
        # Look for common Pashto names in the beginning of the document
        lines = text.split('\n')[:10]  # First 10 lines
        for line in lines:
            for name in self.pashto_names:
                if re.search(r'\b' + re.escape(name) + r'\b', line, re.IGNORECASE):
                    # Return the line containing the name
                    return line.strip()
        
        return None
    
    def _extract_potential_date(self, text: str) -> Optional[str]:
        """Extract potential date from text."""
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    return '/'.join(matches[0])
                else:
                    return matches[0]
        
        return None
    
    def _extract_potential_keywords(self, text: str) -> List[str]:
        """Extract potential keywords from text."""
        # Simple keyword extraction based on common patterns
        keywords = []
        
        # Look for capitalized words (often important terms)
        capitalized_words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', text)
        keywords.extend(capitalized_words[:10])  # Top 10
        
        # Look for words in parentheses
        paren_words = re.findall(r'\(([^)]+)\)', text)
        keywords.extend(paren_words)
        
        return keywords[:20]  # Limit to top 20
    
    def _classify_document_type(self, text: str) -> str:
        """Classify the type of document based on content."""
        document_types = {
            'article': ['abstract', 'introduction', 'conclusion', 'references', 'چکیده', 'مقدمه', 'نتیجه'],
            'book': ['chapter', 'section', 'بخش', 'فصل', 'کتاب'],
            'news': ['news', 'report', 'خبر', 'راپور', 'گزارش'],
            'academic': ['research', 'study', 'analysis', 'څېړنه', 'زیار', 'تحلیل'],
            'religious': ['quran', 'hadith', 'islam', 'قران', 'حدیث', 'اسلام'],
            'literary': ['story', 'poem', 'novel', 'کیسه', 'شعر', 'نګار']
        }
        
        text_lower = text.lower()
        
        for doc_type, keywords in document_types.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                return doc_type
        
        return 'unknown'
    
    def _parse_pdf_date(self, date_str: str) -> Optional[datetime]:
        """Parse PDF date string to datetime object."""
        try:
            # Common PDF date format: D:YYYYMMDDHHmmSSOHH'mm'
            if date_str.startswith('D:'):
                date_str = date_str[2:]
            
            # Extract basic date parts
            parts = date_str[:8]  # YYYYMMDD
            if len(parts) >= 8:
                year = int(parts[:4])
                month = int(parts[4:6])
                day = int(parts[6:8])
                
                return datetime(year, month, day)
            
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _count_images(self, doc: fitz.Document) -> int:
        """Count images in the document."""
        count = 0
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_dict = page.get_text("dict")
            count += len([b for b in text_dict.get("blocks", []) if "type" in b and b["type"] == 1])
        return count
    
    def _analyze_character_types(self, text: str) -> Dict[str, int]:
        """Analyze character types in the text."""
        stats = {
            'total_chars': len(text),
            'pashto_chars': 0,
            'arabic_chars': 0,
            'english_chars': 0,
            'numbers': 0,
            'punctuation': 0,
        }
        
        for char in text:
            if '0x' in repr(char):
                char_code = ord(char)
            else:
                char_code = ord(char)
            
            # Pashto ranges
            if 0x0750 <= char_code <= 0x077F:
                stats['pashto_chars'] += 1
            elif 0x0600 <= char_code <= 0x06FF:
                stats['arabic_chars'] += 1
            elif char.isalpha() and char.isascii():
                stats['english_chars'] += 1
            elif char.isdigit():
                stats['numbers'] += 1
            elif not char.isspace():
                stats['punctuation'] += 1
        
        return stats
    
    def _score_pashto_content(self, text: str) -> float:
        """Score how likely the content is Pashto."""
        if not text:
            return 0.0
        
        # Simple scoring based on character distribution
        char_analysis = self._analyze_character_types(text)
        total_chars = char_analysis['total_chars']
        
        if total_chars == 0:
            return 0.0
        
        # Score based on Pashto character ratio
        pashto_ratio = char_analysis['pashto_chars'] / total_chars
        arabic_ratio = char_analysis['arabic_chars'] / total_chars
        
        # Combine ratios (Pashto is most important, Arabic secondary)
        score = (pashto_ratio * 0.7) + (arabic_ratio * 0.3)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _analyze_fonts(self, doc: fitz.Document) -> Dict[str, Any]:
        """Analyze fonts used in the document."""
        font_info = {
            'total_fonts': 0,
            'font_names': set(),
            'font_families': set(),
            'pashto_compatible_fonts': []
        }
        
        pashto_fonts = ['pashto', 'afghan', 'arabic', 'unicode', 'noto', 'scheherazade']
        
        for page_num in range(min(10, len(doc))):
            page = doc.load_page(page_num)
            
            # Get text dictionary with font info
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            font_name = span.get("font", "").lower()
                            if font_name:
                                font_info['font_names'].add(font_name)
                                
                                # Check if it's Pashto compatible
                                for pashto_font in pashto_fonts:
                                    if pashto_font in font_name:
                                        font_info['pashto_compatible_fonts'].append(font_name)
                                        break
        
        font_info['total_fonts'] = len(font_info['font_names'])
        font_info['font_names'] = list(font_info['font_names'])
        font_info['font_families'] = list(font_info['font_families'])
        font_info['pashto_compatible_fonts'] = list(set(font_info['pashto_compatible_fonts']))
        
        return font_info
    
    def save_metadata(self, metadata: Dict[str, Any], output_path: str) -> None:
        """Save metadata to a JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            raise Exception(f"Error saving metadata: {str(e)}")
    
    def get_metadata_summary(self, metadata: Dict[str, Any]) -> str:
        """Get a human-readable summary of metadata."""
        summary_lines = ["METADATA SUMMARY", "=" * 40, ""]
        
        # File info
        file_info = metadata.get('file_info', {})
        summary_lines.extend([
            f"File: {file_info.get('file_name', 'Unknown')}",
            f"Size: {file_info.get('file_size', 0):,} bytes",
            f"Pages: {metadata.get('pdf_metadata', {}).get('total_pages', 'Unknown')}",
            ""
        ])
        
        # Content metadata
        content = metadata.get('content_metadata', {})
        if content.get('potential_title'):
            summary_lines.append(f"Title: {content['potential_title']}")
        
        if content.get('potential_author'):
            summary_lines.append(f"Author: {content['potential_author']}")
        
        if content.get('document_type'):
            summary_lines.append(f"Type: {content['document_type']}")
        
        # Language info
        lang_info = metadata.get('language_info', {})
        if lang_info.get('pashto_confidence'):
            summary_lines.append(f"Pashto Confidence: {lang_info['pashto_confidence']:.2f}")
        
        return "\n".join(summary_lines)