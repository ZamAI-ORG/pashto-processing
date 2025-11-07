"""
Content Extraction and Cleaning Module
=====================================

This module provides comprehensive content extraction and cleaning capabilities
specifically designed for Pashto text from various website structures.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class ContentCleaner:
    """
    Handles content extraction and cleaning for Pashto text.
    
    Features:
    - HTML tag removal and content extraction
    - Pashto text normalization
    - Noise removal (ads, navigation, etc.)
    - Content structure preservation
    - Multiple content extraction strategies
    """
    
    # Common noise patterns to remove
    NOISE_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'<style[^>]*>.*?</style>',
        r'<nav[^>]*>.*?</nav>',
        r'<header[^>]*>.*?</header>',
        r'<footer[^>]*>.*?</footer>',
        r'<aside[^>]*>.*?</aside>',
        r'<!--.*?-->',
        r'<noscript[^>]*>.*?</noscript>',
    ]
    
    # Content tags that usually contain main text
    CONTENT_TAGS = [
        'article', 'main', 'div', 'section', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'pre', 'code', 'ul', 'ol', 'li'
    ]
    
    # Navigation and structure tags
    STRUCTURAL_TAGS = [
        'nav', 'header', 'footer', 'aside', 'menu', 'menubar', 'toolbar'
    ]
    
    # Pashto-specific content indicators
    PASHTO_INDICATORS = [
        'pashto', 'پښتو', 'ps', 'پښتو ژبه'
    ]
    
    def __init__(self):
        self.extraction_rules = self._load_extraction_rules()
        self.noise_patterns = [re.compile(pattern, re.DOTALL | re.IGNORECASE) 
                              for pattern in self.NOISE_PATTERNS]
    
    def _load_extraction_rules(self) -> Dict[str, List[str]]:
        """Load content extraction rules for different website types."""
        return {
            'news_sites': [
                '.article-body', '.content', '.post-content', '.entry-content',
                '.story-body', '.article-content', 'article', '.main-content'
            ],
            'blogs': [
                '.post-content', '.entry-content', '.article', '.blog-content',
                '.content', '.post-body', '.article-body'
            ],
            'libraries': [
                '.text-content', '.book-content', '.document', '.manuscript',
                '.text-body', '.reading-content', '.content-area'
            ],
            'general': [
                'article', 'main', '.content', '.main-content', 
                '.article-content', '.post-content'
            ]
        }
    
    def clean_html(self, html: str) -> str:
        """
        Clean HTML content by removing unwanted elements.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Cleaned HTML content
        """
        if not html:
            return ""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove noise patterns
            for pattern in self.noise_patterns:
                for match in soup.find_all(string=pattern):
                    match.extract()
            
            # Remove specific unwanted tags
            unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside']
            for tag in unwanted_tags:
                for element in soup.find_all(tag):
                    element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Remove empty elements
            self._remove_empty_elements(soup)
            
            return str(soup)
            
        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html
    
    def extract_text(self, html: str, extraction_method: str = 'auto') -> Dict[str, str]:
        """
        Extract clean text content from HTML.
        
        Args:
            html: HTML content to process
            extraction_method: Method to use ('auto', 'text', 'content', 'selectors')
            
        Returns:
            Dictionary with extracted content types
        """
        if not html:
            return {'clean_text': '', 'structured_text': '', 'metadata': {}}
        
        try:
            # Clean the HTML first
            cleaned_html = self.clean_html(html)
            soup = BeautifulSoup(cleaned_html, 'html.parser')
            
            # Extract different content types
            results = {
                'clean_text': self._extract_clean_text(soup),
                'structured_text': self._extract_structured_text(soup),
                'metadata': self._extract_metadata(soup, html),
                'links': self._extract_links(soup),
                'language_indicators': self._detect_language_indicators(soup)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {'clean_text': '', 'structured_text': '', 'metadata': {}}
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text without HTML tags."""
        # Get text and clean it
        text = soup.get_text(separator=' ', strip=True)
        
        # Additional cleaning
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'\n\s*\n', '\n', text)  # Remove empty lines
        text = text.strip()
        
        return text
    
    def _extract_structured_text(self, soup: BeautifulSoup) -> str:
        """Extract text while preserving some structure."""
        structured_parts = []
        
        # Extract headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = heading.get_text(strip=True)
            if text:
                structured_parts.append(f"# {text}")
        
        # Extract paragraphs
        for para in soup.find_all('p'):
            text = para.get_text(strip=True)
            if text and len(text) > 10:  # Filter out very short paragraphs
                structured_parts.append(text)
        
        # Extract lists
        for ul in soup.find_all(['ul', 'ol']):
            for li in ul.find_all('li'):
                text = li.get_text(strip=True)
                if text:
                    structured_parts.append(f"- {text}")
        
        return '\n\n'.join(structured_parts)
    
    def _extract_metadata(self, soup: BeautifulSoup, html: str) -> Dict[str, any]:
        """Extract metadata from HTML."""
        metadata = {}
        
        # Title
        title = soup.find('title')
        if title:
            metadata['title'] = title.get_text(strip=True)
        
        # Meta description
        desc = soup.find('meta', attrs={'name': 'description'}) or \
               soup.find('meta', attrs={'property': 'og:description'})
        if desc:
            metadata['description'] = desc.get('content', '')
        
        # Meta keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords:
            metadata['keywords'] = keywords.get('content', '')
        
        # Author
        author = soup.find('meta', attrs={'name': 'author'}) or \
                 soup.find('meta', attrs={'property': 'article:author'})
        if author:
            metadata['author'] = author.get('content', '')
        
        # Date
        date = soup.find('meta', attrs={'property': 'article:published_time'}) or \
               soup.find('meta', attrs={'name': 'date'}) or \
               soup.find('time')
        if date:
            metadata['date'] = date.get('content') or date.get_text(strip=True)
        
        # Language
        html_tag = soup.find('html')
        if html_tag:
            metadata['language'] = html_tag.get('lang', '')
        
        # Content indicators
        metadata['has_pashto_indicators'] = self._detect_pashto_indicators(soup, html)
        
        return metadata
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all links from the page."""
        links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if href and href.startswith('http'):
                links.append(href)
        return links
    
    def _detect_language_indicators(self, soup: BeautifulSoup) -> Dict[str, any]:
        """Detect language indicators in the content."""
        text = soup.get_text()
        
        indicators = {
            'pashto_words': self._count_pashto_words(text),
            'arabic_script': bool(re.search(r'[\u0600-\u06FF]', text)),
            'pashto_indicators': self._detect_pashto_indicators(soup, text)
        }
        
        return indicators
    
    def _detect_pashto_indicators(self, soup: BeautifulSoup, text: str) -> Dict[str, bool]:
        """Detect Pashto-specific indicators."""
        content_lower = text.lower()
        indicators = {}
        
        # Look for Pashto language indicators
        for indicator in self.PASHTO_INDICATORS:
            indicators[f'has_{indicator}'] = indicator in content_lower
        
        # Check for Pashto script in text
        indicators['has_arabic_script'] = bool(re.search(r'[\u0600-\u06FF]', text))
        
        # Check meta language
        html_tag = soup.find('html')
        if html_tag:
            lang = html_tag.get('lang', '').lower()
            indicators['meta_lang_ps'] = lang in ['ps', 'pashto', 'prs', 'fa']
        
        return indicators
    
    def _count_pashto_words(self, text: str) -> int:
        """Count potential Pashto words in text."""
        # Simple pattern matching for common Pashto words
        pashto_patterns = [
            r'\bزه\b', r'\bدو\b', r'\bموږ\b', r'\bتاسو\b', r'\bدوی\b',
            r'\bڅخه\b', r'\bته\b', r'\bسره\b', r'\bپه\b', r'\bد\b'
        ]
        
        count = 0
        for pattern in pashto_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return count
    
    def _remove_empty_elements(self, soup: BeautifulSoup):
        """Remove empty elements from the HTML."""
        for element in soup.find_all():
            if len(element.get_text(strip=True)) == 0 and not element.find('img'):
                element.decompose()
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text content.
        
        Args:
            text: Text content to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove non-printable characters except newlines
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive empty lines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text
    
    def validate_content_quality(self, text: str, metadata: Dict = None) -> Dict[str, any]:
        """
        Validate the quality of extracted content.
        
        Args:
            text: Text content to validate
            metadata: Extracted metadata
            
        Returns:
            Quality assessment
        """
        if not text:
            return {'is_valid': False, 'score': 0, 'issues': ['empty_content']}
        
        quality_score = 0
        issues = []
        
        # Length check
        if len(text) < 100:
            issues.append('content_too_short')
        else:
            quality_score += 20
        
        # Word count
        words = len(text.split())
        if words < 20:
            issues.append('insufficient_words')
        else:
            quality_score += 20
        
        # Pashto content indicators
        pashto_score = 0
        if metadata:
            if metadata.get('has_pashto_indicators', {}).get('has_arabic_script', False):
                pashto_score += 25
            if metadata.get('has_pashto_indicators', {}).get('has_pashto', False):
                pashto_score += 25
        
        if pashto_score > 0:
            quality_score += pashto_score
        else:
            issues.append('no_pashto_indicators')
        
        # Structure indicators (headings, paragraphs)
        if '\n' in text and len([line for line in text.split('\n') if line.strip()]) > 3:
            quality_score += 15
        
        # URL preservation (if metadata has links)
        if metadata and metadata.get('links'):
            quality_score += 10
        
        # Check for reasonable sentence structure
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) >= 3:
            quality_score += 10
        
        return {
            'is_valid': quality_score >= 60,
            'score': min(quality_score, 100),
            'issues': issues,
            'recommendations': self._generate_recommendations(issues)
        }
    
    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on quality issues."""
        recommendations = []
        
        if 'content_too_short' in issues:
            recommendations.append("Content may be incomplete; consider extracting from additional pages")
        
        if 'no_pashto_indicators' in issues:
            recommendations.append("Content may not be in Pashto; verify language detection")
        
        if 'insufficient_words' in issues:
            recommendations.append("Content is very short; may be navigation or metadata")
        
        return recommendations