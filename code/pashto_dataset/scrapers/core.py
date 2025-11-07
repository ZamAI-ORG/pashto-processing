"""
Core Pashto Web Scraper
======================

The main scraping engine that coordinates all components for collecting
Pashto text from various sources.
"""

import time
import requests
import logging
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime

try:
    from .encoders import PashtoEncoder
    from .cleaners import ContentCleaner
    from .rate_limiter import AdaptiveRateLimiter, RateLimiter
    from .source_manager import SourceManager, SourceConfig
except ImportError:
    from encoders import PashtoEncoder
    from cleaners import ContentCleaner
    from rate_limiter import AdaptiveRateLimiter, RateLimiter
    from source_manager import SourceManager, SourceConfig

# Set up logging
logger = logging.getLogger(__name__)


class PashtoScraper:
    """
    Main Pashto web scraping engine.
    
    Coordinates encoding detection, content cleaning, rate limiting,
    and source management for comprehensive Pashto text collection.
    """
    
    def __init__(self, 
                 db_path: str = "data/pashto_sources.db",
                 output_dir: str = "data/scraped_content",
                 max_workers: int = 5,
                 enable_adaptive_rate_limiting: bool = True):
        
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.session = requests.Session()
        
        # Initialize components
        self.encoder = PashtoEncoder()
        self.cleaner = ContentCleaner()
        self.rate_limiter = AdaptiveRateLimiter() if enable_adaptive_rate_limiting else RateLimiter()
        self.source_manager = SourceManager(db_path)
        
        # Session configuration
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ps,fa,ur,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Results storage
        self.scraped_content = []
        self.errors = []
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'items_scraped': 0,
            'sources_processed': 0
        }
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Create output directory
        import os
        os.makedirs(output_dir, exist_ok=True)
    
    def scrape_url(self, url: str, source_config: Optional[SourceConfig] = None) -> Dict[str, Any]:
        """
        Scrape a single URL and extract Pashto content.
        
        Args:
            url: URL to scrape
            source_config: Optional source configuration
            
        Returns:
            Dictionary containing scraped content and metadata
        """
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'content': {},
            'metadata': {},
            'errors': []
        }
        
        try:
            # Check rate limit
            if not self.rate_limiter.acquire(url):
                wait_time = self.rate_limiter.wait_time(url)
                result['errors'].append(f"Rate limited. Wait time: {wait_time:.2f}s")
                return result
            
            # Make request
            response = self._make_request(url)
            if not response:
                result['errors'].append("Failed to get response")
                return result
            
            # Record response for adaptive rate limiting
            if hasattr(self.rate_limiter, 'record_response'):
                self.rate_limiter.record_response(url, response.status_code, response.elapsed.total_seconds())
            
            self.stats['total_requests'] += 1
            
            if response.status_code == 200:
                self.stats['successful_requests'] += 1
                
                # Extract content
                content_result = self.cleaner.extract_text(response.text)
                
                # Clean and validate content
                clean_text = self.cleaner.clean_text(content_result['clean_text'])
                quality_assessment = self.cleaner.validate_content_quality(clean_text, content_result['metadata'])
                
                # Encode and validate Pashto content
                encoding = self.encoder.detect_encoding(clean_text)
                normalized_text = self.encoder.normalize_text(clean_text, encoding)
                pashto_validation = self.encoder.validate_pashto_content(normalized_text)
                
                result['content'] = {
                    'raw_text': content_result['clean_text'],
                    'clean_text': clean_text,
                    'structured_text': content_result['structured_text'],
                    'normalized_text': normalized_text,
                    'encoding': encoding,
                    'pashto_validation': pashto_validation,
                    'quality_score': quality_assessment['score'],
                    'is_valid': quality_assessment['is_valid']
                }
                
                result['metadata'] = {
                    **content_result['metadata'],
                    'pashto_indicators': content_result.get('language_indicators', {}),
                    'extraction_method': 'text',
                    'response_size': len(response.text),
                    'encoding_confidence': self.encoder.get_encoding_confidence(clean_text)
                }
                
                result['success'] = result['content']['is_valid'] or result['content']['pashto_validation']['has_pashto_script']
                
                if result['success']:
                    self.stats['items_scraped'] += 1
                    logger.info(f"Successfully scraped {url} (Quality: {result['content']['quality_score']})")
                else:
                    result['errors'].append("Content validation failed")
                    
            else:
                self.stats['failed_requests'] += 1
                result['errors'].append(f"HTTP {response.status_code}")
                logger.warning(f"HTTP {response.status_code} for {url}")
        
        except Exception as e:
            self.stats['failed_requests'] += 1
            error_msg = f"Error scraping {url}: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        finally:
            # Release rate limit slot
            self.rate_limiter.release(url)
            
            # Store result
            with self.lock:
                self.scraped_content.append(result)
        
        return result
    
    def scrape_source(self, source: SourceConfig, max_pages: int = None) -> Dict[str, Any]:
        """
        Scrape all content from a specific source.
        
        Args:
            source: Source configuration
            max_pages: Maximum pages to scrape
            
        Returns:
            Dictionary containing scraping results
        """
        if max_pages is None:
            max_pages = source.max_pages
        
        logger.info(f"Starting to scrape source: {source.name} ({source.url})")
        
        source_result = {
            'source_name': source.name,
            'source_url': source.url,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'total_pages': 0,
            'successful_pages': 0,
            'failed_pages': 0,
            'items_scraped': 0,
            'pages_results': [],
            'errors': []
        }
        
        try:
            # Discover pages to scrape
            urls_to_scrape = self._discover_pages(source, max_pages)
            source_result['total_pages'] = len(urls_to_scrape)
            
            if not urls_to_scrape:
                source_result['errors'].append("No URLs discovered for scraping")
                return source_result
            
            # Scrape pages
            for i, url in enumerate(urls_to_scrape):
                logger.info(f"Scraping page {i+1}/{len(urls_to_scrape)}: {url}")
                
                page_result = self.scrape_url(url, source)
                page_result['source_name'] = source.name
                
                source_result['pages_results'].append(page_result)
                
                if page_result['success']:
                    source_result['successful_pages'] += 1
                    source_result['items_scraped'] += 1
                else:
                    source_result['failed_pages'] += 1
                
                # Add delay between pages
                if i < len(urls_to_scrape) - 1:
                    time.sleep(2)
            
        except Exception as e:
            error_msg = f"Error scraping source {source.name}: {str(e)}"
            source_result['errors'].append(error_msg)
            logger.error(error_msg)
        
        finally:
            source_result['end_time'] = datetime.now().isoformat()
            
            # Update source statistics
            success = source_result['failed_pages'] == 0
            self.source_manager.update_source_stats(
                source.name, 
                success, 
                source_result['items_scraped'],
                '; '.join(source_result['errors']) if source_result['errors'] else None,
                source_result['total_pages'],
                0  # Duration would be calculated from timestamps
            )
        
        return source_result
    
    def scrape_all_sources(self, source_types: List[str] = None, max_sources: int = None) -> Dict[str, Any]:
        """
        Scrape all configured sources.
        
        Args:
            source_types: List of source types to scrape ('news', 'blog', 'library', etc.)
            max_sources: Maximum number of sources to process
            
        Returns:
            Overall scraping results
        """
        self.stats['start_time'] = datetime.now()
        logger.info("Starting comprehensive Pashto content scraping")
        
        # Get sources to scrape
        sources = self.source_manager.get_sources()
        if source_types:
            sources = [s for s in sources if s.source_type in source_types]
        
        if max_sources:
            sources = sources[:max_sources]
        
        if not sources:
            logger.warning("No sources found to scrape")
            return {'error': 'No sources configured'}
        
        logger.info(f"Found {len(sources)} sources to scrape")
        
        # Process sources with threading
        overall_results = {
            'start_time': self.stats['start_time'].isoformat(),
            'sources_processed': 0,
            'total_sources': len(sources),
            'sources_results': [],
            'overall_stats': {}
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all source scraping tasks
            future_to_source = {
                executor.submit(self.scrape_source, source): source 
                for source in sources
            }
            
            # Process completed tasks
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result()
                    overall_results['sources_results'].append(result)
                    overall_results['sources_processed'] += 1
                    self.stats['sources_processed'] += 1
                    
                    logger.info(f"Completed scraping {source.name} "
                              f"({overall_results['sources_processed']}/{len(sources)})")
                
                except Exception as e:
                    logger.error(f"Error processing source {source.name}: {e}")
                    overall_results['sources_results'].append({
                        'source_name': source.name,
                        'error': str(e),
                        'success': False
                    })
        
        self.stats['end_time'] = datetime.now()
        overall_results['end_time'] = self.stats['end_time'].isoformat()
        overall_results['overall_stats'] = self.get_stats()
        
        # Save results
        self._save_results(overall_results)
        
        logger.info(f"Completed scraping {overall_results['sources_processed']}/{len(sources)} sources")
        logger.info(f"Total items scraped: {self.stats['items_scraped']}")
        
        return overall_results
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with error handling."""
        try:
            response = self.session.get(url, timeout=30)
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
    
    def _discover_pages(self, source: SourceConfig, max_pages: int) -> List[str]:
        """Discover pages to scrape from a source."""
        discovered_urls = [source.url]  # Start with the main page
        
        try:
            # For now, just return the source URL
            # In a full implementation, this would:
            # 1. Scrape the main page
            # 2. Find navigation links
            # 3. Discover pagination
            # 4. Filter for Pashto content
            pass
            
        except Exception as e:
            logger.error(f"Error discovering pages for {source.name}: {e}")
        
        return discovered_urls[:max_pages]
    
    def _save_results(self, results: Dict[str, Any]):
        """Save scraping results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save overall results
        results_file = f"{self.output_dir}/scraping_results_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save individual content items
        content_file = f"{self.output_dir}/scraped_content_{timestamp}.json"
        content_data = {
            'scraped_at': datetime.now().isoformat(),
            'total_items': len(self.scraped_content),
            'items': [item for item in self.scraped_content if item['success']]
        }
        
        with open(content_file, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        # Save errors
        if self.errors:
            errors_file = f"{self.output_dir}/scraping_errors_{timestamp}.json"
            with open(errors_file, 'w', encoding='utf-8') as f:
                json.dump({'errors': self.errors}, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {self.output_dir}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current scraping statistics."""
        duration = None
        if self.stats['start_time'] and self.stats['end_time']:
            duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        return {
            **self.stats,
            'duration_seconds': duration,
            'items_per_second': self.stats['items_scraped'] / duration if duration and duration > 0 else 0,
            'success_rate': (self.stats['successful_requests'] / self.stats['total_requests'] 
                           if self.stats['total_requests'] > 0 else 0),
            'active_sources': len(self.source_manager.sources),
            'scraped_content_items': len([item for item in self.scraped_content if item['success']])
        }
    
    def export_content(self, format: str = 'json', output_file: str = None) -> str:
        """
        Export scraped content in various formats.
        
        Args:
            format: Export format ('json', 'txt', 'csv')
            output_file: Optional output file path
            
        Returns:
            Path to exported file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.output_dir}/exported_content_{timestamp}.{format}"
        
        successful_items = [item for item in self.scraped_content if item['success']]
        
        if format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'exported_at': datetime.now().isoformat(),
                    'total_items': len(successful_items),
                    'items': successful_items
                }, f, indent=2, ensure_ascii=False)
        
        elif format == 'txt':
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in successful_items:
                    f.write(f"URL: {item['url']}\n")
                    f.write(f"Title: {item['metadata'].get('title', 'N/A')}\n")
                    f.write(f"Content: {item['content']['clean_text']}\n")
                    f.write("=" * 80 + "\n\n")
        
        elif format == 'csv':
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Title', 'Content', 'Quality_Score', 'Timestamp'])
                
                for item in successful_items:
                    writer.writerow([
                        item['url'],
                        item['metadata'].get('title', 'N/A'),
                        item['content']['clean_text'][:1000],  # Truncate for CSV
                        item['content']['quality_score'],
                        item['timestamp']
                    ])
        
        logger.info(f"Content exported to {output_file}")
        return output_file
    
    def add_source(self, name: str, url: str, source_type: str, **kwargs) -> bool:
        """Convenience method to add a new source."""
        source = SourceConfig(
            name=name,
            url=url,
            source_type=source_type,
            **kwargs
        )
        return self.source_manager.add_source(source)
    
    def get_source_stats(self) -> Dict[str, Any]:
        """Get source management statistics."""
        return self.source_manager.get_source_stats()