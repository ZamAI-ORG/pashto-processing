"""
Digital Library Scraper
======================

Specialized scraper for Pashto digital libraries, archives, and cultural repositories.
Handles academic papers, books, manuscripts, and cultural documents.
"""

import re
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import json

try:
    from .encoders import PashtoEncoder
    from .cleaners import ContentCleaner
    from .rate_limiter import RateLimiter
except ImportError:
    from encoders import PashtoEncoder
    from cleaners import ContentCleaner
    from rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class LibraryScraper:
    """
    Specialized scraper for Pashto digital libraries and archives.
    
    Features:
    - Academic paper extraction
    - Manuscript and book handling
    - PDF document processing
    - Metadata preservation
    - Cultural context preservation
    - Citation and reference extraction
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.encoder = PashtoEncoder()
        self.cleaner = ContentCleaner()
        
        # Library-specific configurations
        self.library_configs = {
            'archive_org': {
                'name': 'Internet Archive',
                'search_url': 'https://archive.org/search.php',
                'base_url': 'https://archive.org',
                'language_codes': ['ps', 'pus'],  # Pashto language codes
                'selectors': {
                    'title': 'h1.title',
                    'description': '.description',
                    'download_links': '.download-links a',
                    'metadata': '.metadata-item'
                }
            },
            'hathitrust': {
                'name': 'HathiTrust Digital Library',
                'search_url': 'https://catalog.hathitrust.org',
                'base_url': 'https://hdl.handle.net',
                'selectors': {
                    'title': '.title',
                    'fulltext': '.fulltext',
                    'metadata': '.metadata'
                }
            },
            'world_digital_library': {
                'name': 'World Digital Library',
                'base_url': 'https://www.wdl.org',
                'selectors': {
                    'title': '.item-title',
                    'content': '.item-content',
                    'description': '.item-description'
                }
            }
        }
        
        # Document type patterns
        self.document_patterns = {
            'academic_paper': re.compile(r'paper|research|journal|thesis|dissertation', re.IGNORECASE),
            'book': re.compile(r'book|volume|chapter', re.IGNORECASE),
            'manuscript': re.compile(r'manuscript|手稿|خطوط', re.IGNORECASE),
            'cultural_document': re.compile(r'cultural|heritage|history|tradition', re.IGNORECASE),
            'poetry': re.compile(r'poetry|poem|shairi|شعر', re.IGNORECASE)
        }
        
        # Pashto content indicators
        self.pashto_indicators = [
            'pashto', 'پښتو', 'pus', 'ps', 'afghan', 'afghanistan'
        ]
    
    def search_library_content(self, search_query: str, library: str = 'archive_org', 
                             max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for Pashto content in digital libraries.
        
        Args:
            search_query: Search query
            library: Library configuration key
            max_results: Maximum number of results
            
        Returns:
            List of search results with metadata
        """
        if library not in self.library_configs:
            logger.error(f"Unknown library: {library}")
            return []
        
        config = self.library_configs[library]
        results = []
        
        try:
            if library == 'archive_org':
                results = self._search_archive_org(search_query, max_results)
            elif library == 'hathitrust':
                results = self._search_hathitrust(search_query, max_results)
            elif library == 'world_digital_library':
                results = self._search_wdl(search_query, max_results)
            
            # Filter for Pashto content
            pashto_results = []
            for result in results:
                if self._is_pashto_content(result):
                    pashto_results.append(result)
            
            logger.info(f"Found {len(pashto_results)} Pashto items in {library}")
            return pashto_results[:max_results]
        
        except Exception as e:
            logger.error(f"Error searching {library}: {e}")
            return []
    
    def _search_archive_org(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Internet Archive for Pashto content."""
        results = []
        
        # Add Pashto language filters
        search_params = {
            'query': f'{query} AND language:pus OR language:ps OR language:pashto',
            'output': 'json',
            'num': min(max_results * 2, 100)  # Get more results to filter
        }
        
        try:
            if not self.rate_limiter.acquire('archive.org'):
                return results
            
            response = requests.get(
                'https://archive.org/advancedsearch.php',
                params=search_params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                for doc in data.get('response', {}).get('docs', []):
                    result = {
                        'title': doc.get('title', ''),
                        'identifier': doc.get('identifier', ''),
                        'url': f"https://archive.org/details/{doc.get('identifier', '')}",
                        'description': doc.get('description', ''),
                        'language': doc.get('language', []),
                        'date': doc.get('date', ''),
                        'creator': doc.get('creator', []),
                        'subject': doc.get('subject', []),
                        'type': doc.get('mediatype', ''),
                        'download_url': f"https://archive.org/download/{doc.get('identifier', '')}",
                        'library': 'archive_org'
                    }
                    results.append(result)
        
        except Exception as e:
            logger.error(f"Error searching Archive.org: {e}")
        
        finally:
            self.rate_limiter.release('archive.org')
        
        return results
    
    def _search_hathitrust(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search HathiTrust Digital Library (placeholder implementation)."""
        # This would require API access and proper authentication
        # For now, return empty list
        logger.info("HathiTrust search not implemented - requires API access")
        return []
    
    def _search_wdl(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search World Digital Library (placeholder implementation)."""
        # This would require understanding the WDL API
        # For now, return empty list
        logger.info("World Digital Library search not implemented")
        return []
    
    def _is_pashto_content(self, item: Dict[str, Any]) -> bool:
        """Check if content item contains Pashto material."""
        # Check language
        language = item.get('language', [])
        if isinstance(language, str):
            language = [language]
        
        pashto_languages = ['ps', 'pus', 'pashto', 'afghani']
        if any(lang.lower() in pashto_languages for lang in language):
            return True
        
        # Check title and description
        text_content = ' '.join([
            str(item.get('title', '')),
            str(item.get('description', '')),
            str(item.get('subject', []))
        ]).lower()
        
        # Check for Pashto indicators
        if any(indicator in text_content for indicator in self.pashto_indicators):
            return True
        
        # Check for Pashto script
        if re.search(r'[\u0600-\u06FF]', str(item.get('title', '') + item.get('description', ''))):
            return True
        
        return False
    
    def extract_document_content(self, document_url: str, document_type: str = 'auto') -> Dict[str, Any]:
        """
        Extract content from a digital document.
        
        Args:
            document_url: URL of the document
            document_type: Type of document ('book', 'manuscript', 'paper', 'auto')
            
        Returns:
            Dictionary containing extracted content
        """
        result = {
            'url': document_url,
            'timestamp': datetime.now().isoformat(),
            'type': 'document',
            'document_type': document_type,
            'success': False,
            'content': {},
            'metadata': {},
            'errors': []
        }
        
        try:
            # Detect document type if auto
            if document_type == 'auto':
                document_type = self._detect_document_type(document_url)
            
            # Check rate limit
            if not self.rate_limiter.acquire(document_url):
                result['errors'].append("Rate limited")
                return result
            
            # Extract based on type
            if document_type == 'pdf':
                result = self._extract_pdf_content(document_url)
            elif document_type == 'html':
                result = self._extract_html_document(document_url)
            elif document_type == 'image':
                result = self._extract_image_document(document_url)
            else:
                result = self._extract_generic_document(document_url)
            
            result['document_type'] = document_type
            
        except Exception as e:
            error_msg = f"Error extracting document {document_url}: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        finally:
            self.rate_limiter.release(document_url)
        
        return result
    
    def _detect_document_type(self, url: str) -> str:
        """Detect document type from URL and content."""
        url_lower = url.lower()
        
        # Check URL patterns
        if url_lower.endswith('.pdf'):
            return 'pdf'
        elif any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.tiff', '.gif']):
            return 'image'
        elif '/details/' in url_lower or '/download/' in url_lower:
            return 'html'
        else:
            return 'html'  # Default fallback
    
    def _extract_pdf_content(self, pdf_url: str) -> Dict[str, Any]:
        """Extract content from PDF documents."""
        result = {
            'url': pdf_url,
            'type': 'pdf_document',
            'success': False,
            'content': {},
            'metadata': {},
            'errors': []
        }
        
        try:
            # Download PDF
            response = requests.get(pdf_url, timeout=60)
            if response.status_code != 200:
                result['errors'].append(f"Failed to download PDF: HTTP {response.status_code}")
                return result
            
            # This is a simplified PDF extraction
            # In a real implementation, you would use PyPDF2, pdfplumber, or similar
            pdf_content = response.content
            
            # For now, just save metadata
            result['content'] = {
                'pdf_size': len(pdf_content),
                'pdf_url': pdf_url,
                'extraction_method': 'placeholder'
            }
            
            result['metadata'] = {
                'file_type': 'pdf',
                'download_successful': True,
                'file_size': len(pdf_content)
            }
            
            result['success'] = True
            logger.info(f"PDF content detected: {pdf_url}")
        
        except Exception as e:
            result['errors'].append(f"PDF extraction error: {str(e)}")
        
        return result
    
    def _extract_html_document(self, doc_url: str) -> Dict[str, Any]:
        """Extract content from HTML documents."""
        result = {
            'url': doc_url,
            'type': 'html_document',
            'success': False,
            'content': {},
            'metadata': {},
            'errors': []
        }
        
        try:
            response = requests.get(doc_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract document content
                content_data = self._extract_document_structure(soup, doc_url)
                
                result['content'] = content_data
                result['success'] = bool(content_data.get('content') or content_data.get('text'))
                
                if result['success']:
                    logger.info(f"Successfully extracted HTML document: {doc_url}")
        
        except Exception as e:
            result['errors'].append(f"HTML extraction error: {str(e)}")
        
        return result
    
    def _extract_image_document(self, image_url: str) -> Dict[str, Any]:
        """Extract metadata from image documents."""
        result = {
            'url': image_url,
            'type': 'image_document',
            'success': False,
            'content': {},
            'metadata': {},
            'errors': []
        }
        
        try:
            # Check if image exists and get metadata
            response = requests.head(image_url, timeout=10)
            if response.status_code == 200:
                result['content'] = {
                    'image_url': image_url,
                    'content_type': response.headers.get('content-type', ''),
                    'file_size': response.headers.get('content-length', ''),
                    'extraction_method': 'metadata_only'
                }
                
                result['metadata'] = {
                    'file_type': 'image',
                    'accessible': True,
                    'requires_ocr': True  # Most image documents will need OCR
                }
                
                result['success'] = True
                logger.info(f"Image document metadata extracted: {image_url}")
        
        except Exception as e:
            result['errors'].append(f"Image extraction error: {str(e)}")
        
        return result
    
    def _extract_generic_document(self, doc_url: str) -> Dict[str, Any]:
        """Extract content using generic approach."""
        result = {
            'url': doc_url,
            'type': 'generic_document',
            'success': False,
            'content': {},
            'metadata': {},
            'errors': []
        }
        
        # Try HTML extraction as fallback
        return self._extract_html_document(doc_url)
    
    def _extract_document_structure(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract structured content from document page."""
        content_data = {}
        
        # Extract title
        title_selectors = ['h1', '.title', '.document-title', '[itemprop="name"]']
        for selector in title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                content_data['title'] = self._clean_text(title_element.get_text())
                break
        
        if not content_data.get('title'):
            content_data['title'] = urlparse(url).path.split('/')[-1]
        
        # Extract main content
        content_selectors = [
            '.document-content', '.text-content', 'main', 'article', 
            '.content', '#content', '[itemprop="text"]'
        ]
        
        content_text = ''
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Remove unwanted elements
                for unwanted in content_element.find_all(['script', 'style', 'nav', 'header']):
                    unwanted.decompose()
                content_text = self._clean_text(content_element.get_text())
                break
        
        content_data['content'] = content_text
        
        # Extract metadata
        content_data['metadata'] = self._extract_document_metadata(soup)
        
        # Extract references/citations
        content_data['references'] = self._extract_references(soup)
        
        # Extract cultural context if available
        content_data['cultural_context'] = self._extract_cultural_context(soup)
        
        return content_data
    
    def _extract_document_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from document page."""
        metadata = {}
        
        # Title and description
        title = soup.find('title')
        if title:
            metadata['page_title'] = title.get_text()
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
            elif name == 'date':
                metadata['date'] = content
        
        # Schema.org metadata
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if data.get('@type') == 'Book':
                        metadata['book_info'] = data
                    elif data.get('@type') == 'ScholarlyArticle':
                        metadata['article_info'] = data
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return metadata
    
    def _extract_references(self, soup: BeautifulSoup) -> List[str]:
        """Extract references and citations from document."""
        references = []
        
        # Look for references section
        ref_indicators = ['references', 'bibliography', 'sources', 'works cited']
        for indicator in ref_indicators:
            ref_section = soup.find(text=re.compile(indicator, re.IGNORECASE))
            if ref_section:
                # Find the parent section
                section = ref_section.find_parent(['div', 'section', 'h2', 'h3', 'h4'])
                if section:
                    # Extract list items or paragraphs
                    for item in section.find_all(['li', 'p']):
                        ref_text = item.get_text().strip()
                        if ref_text and len(ref_text) > 10:
                            references.append(ref_text)
        
        return references[:20]  # Limit to first 20 references
    
    def _extract_cultural_context(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract cultural and historical context information."""
        context = {}
        
        # Look for cultural indicators in text
        text_content = soup.get_text().lower()
        
        cultural_keywords = {
            'afghan_heritage': ['heritage', 'afghan', 'afghanistan', 'cultural'],
            'historical_periods': ['ancient', 'medieval', 'modern', 'traditional'],
            'literary_forms': ['poetry', 'story', 'folklore', 'epic', 'ballad'],
            'social_context': ['tribal', 'family', 'community', 'society']
        }
        
        for category, keywords in cultural_keywords.items():
            context[category] = [kw for kw in keywords if kw in text_content]
        
        return context
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def scrape_digital_library(self, library_name: str, search_terms: List[str], 
                             max_results_per_term: int = 10) -> Dict[str, Any]:
        """
        Scrape a digital library for Pashto content.
        
        Args:
            library_name: Name of the digital library
            search_terms: List of search terms
            max_results_per_term: Maximum results per search term
            
        Returns:
            Dictionary with scraping results
        """
        logger.info(f"Starting to scrape {library_name} for Pashto content")
        
        result = {
            'library': library_name,
            'start_time': datetime.now().isoformat(),
            'search_terms': search_terms,
            'total_searches': 0,
            'documents_found': 0,
            'documents_scraped': 0,
            'success': True,
            'search_results': [],
            'errors': []
        }
        
        try:
            for term in search_terms:
                logger.info(f"Searching for: {term}")
                
                # Search for content
                search_results = self.search_library_content(term, library_name, max_results_per_term)
                result['total_searches'] += 1
                result['documents_found'] += len(search_results)
                
                term_result = {
                    'search_term': term,
                    'results_found': len(search_results),
                    'documents': []
                }
                
                # Process each document
                for doc in search_results:
                    if 'url' in doc:
                        doc_result = self.extract_document_content(doc['url'])
                        term_result['documents'].append({
                            **doc,
                            'extraction_result': doc_result
                        })
                        
                        if doc_result['success']:
                            result['documents_scraped'] += 1
                
                result['search_results'].append(term_result)
                
                # Delay between searches
                time.sleep(2)
        
        except Exception as e:
            result['success'] = False
            result['errors'].append(str(e))
            logger.error(f"Error scraping {library_name}: {e}")
        
        finally:
            result['end_time'] = datetime.now().isoformat()
        
        return result