"""
News Site Scraper
================

Specialized scraper for Pashto news websites with features for:
- News article extraction
- Metadata handling (dates, authors, categories)
- Pagination and navigation
- Breaking news detection
- Source-specific optimizations
"""

import re
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

try:
    from .encoders import PashtoEncoder
    from .cleaners import ContentCleaner
    from .rate_limiter import RateLimiter
except ImportError:
    from encoders import PashtoEncoder
    from cleaners import ContentCleaner
    from rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class NewsScraper:
    """
    Specialized scraper for Pashto news websites.
    
    Handles news-specific content extraction, metadata processing,
    and domain-specific optimizations for various news sites.
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.encoder = PashtoEncoder()
        self.cleaner = ContentCleaner()
        
        # News site specific configurations
        self.news_configs = {
            'bbc_pashto': {
                'name': 'BBC Pashto',
                'base_url': 'https://www.bbc.com/pashto',
                'article_selectors': {
                    'title': 'h1[data-testid="main-heading"], h1',
                    'content': '[data-testid="article-body"], .story-body, .article-content',
                    'date': 'time[datetime], time[data-testid="timestamp"]',
                    'author': '.byline-name, [data-testid="byline"]'
                },
                'pagination_selectors': {
                    'next': 'a[rel="next"], .pagination-next, .next-page',
                    'articles_list': 'a[href*="/news/"]'
                }
            },
            'aljazeera_pashto': {
                'name': 'Al Jazeera Pashto',
                'base_url': 'https://www.aljazeera.com/ps/',
                'article_selectors': {
                    'title': '.article-title h1, h1.article-title',
                    'content': '.article-content, .wysiwyg, .article-body',
                    'date': 'time[datetime], .article-date',
                    'author': '.author-name, .byline'
                },
                'pagination_selectors': {
                    'next': '.pagination .next, .next-page',
                    'articles_list': 'a[href*="/news/"]'
                }
            },
            'tolonews': {
                'name': 'Tolo News',
                'base_url': 'https://www.tolonews.com',
                'article_selectors': {
                    'title': 'h1.title, h1',
                    'content': '.article-content, .content, .story',
                    'date': '.date, time, .published-date',
                    'author': '.author, .byline'
                },
                'pagination_selectors': {
                    'next': '.next, .pagination-next',
                    'articles_list': 'a[href*="/news/"]'
                }
            }
        }
        
        # Common patterns for news sites
        self.url_patterns = {
            'article': re.compile(r'/news/|\.html?$|article|pashto'),
            'category': re.compile(r'/category/|/section/|/topic/'),
            'search': re.compile(r'/search|\?s=|\?q=')
        }
    
    def detect_news_site(self, url: str) -> Optional[str]:
        """
        Detect if URL belongs to a known news site and return config key.
        
        Args:
            url: URL to check
            
        Returns:
            Config key for the news site or None
        """
        url_lower = url.lower()
        
        for site_key, config in self.news_configs.items():
            base_url = config['base_url'].lower()
            if base_url in url_lower or any(indicator in url_lower for indicator in ['bbc', 'aljazeera', 'tolonews']):
                return site_key
        
        return None
    
    def extract_news_article(self, url: str, site_config: str = None) -> Dict[str, Any]:
        """
        Extract news article content with news-specific metadata.
        
        Args:
            url: URL of the news article
            site_config: Specific site configuration key
            
        Returns:
            Dictionary containing extracted news article
        """
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'type': 'news_article',
            'success': False,
            'content': {},
            'metadata': {},
            'errors': []
        }
        
        try:
            # Detect site configuration if not provided
            if not site_config:
                site_config = self.detect_news_site(url)
            
            # Check rate limit
            if not self.rate_limiter.acquire(url):
                result['errors'].append("Rate limited")
                return result
            
            # Make request
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract content based on site configuration
                if site_config and site_config in self.news_configs:
                    content_data = self._extract_with_config(soup, url, self.news_configs[site_config])
                else:
                    content_data = self._extract_generic_news(soup, url)
                
                result['content'] = content_data
                result['success'] = bool(content_data.get('title') and content_data.get('content'))
                
                if result['success']:
                    logger.info(f"Successfully extracted news article: {url}")
                else:
                    result['errors'].append("Failed to extract required content")
            else:
                result['errors'].append(f"HTTP {response.status_code}")
        
        except Exception as e:
            error_msg = f"Error extracting news article {url}: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg)
        
        finally:
            self.rate_limiter.release(url)
        
        return result
    
    def _extract_with_config(self, soup: BeautifulSoup, url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content using site-specific configuration."""
        content_data = {}
        
        # Extract title
        title_selector = config['article_selectors']['title']
        title_element = soup.select_one(title_selector) if title_selector else None
        if not title_element:
            # Fallback to generic title extraction
            title_element = soup.find('h1') or soup.find('title')
        
        content_data['title'] = self._clean_text(title_element.get_text() if title_element else '')
        
        # Extract main content
        content_selector = config['article_selectors']['content']
        content_element = soup.select_one(content_selector) if content_selector else None
        if not content_element:
            # Fallback to article or main tag
            content_element = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'content|article'))
        
        if content_element:
            # Remove unwanted elements
            for unwanted in content_element.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                unwanted.decompose()
            
            content_data['content'] = self._clean_text(content_element.get_text())
        else:
            content_data['content'] = ''
        
        # Extract date
        date_element = self._extract_date(soup, config['article_selectors'].get('date'))
        content_data['date'] = date_element
        
        # Extract author
        author_selector = config['article_selectors'].get('author')
        author_element = soup.select_one(author_selector) if author_selector else None
        if not author_element:
            author_element = soup.find(class_=re.compile(r'author|byline'))
        
        content_data['author'] = self._clean_text(author_element.get_text()) if author_element else ''
        
        # Extract category/tags
        content_data['category'] = self._extract_category(soup, url)
        
        # Extract image URLs
        content_data['images'] = [img.get('src', img.get('data-src', '')) for img in soup.find_all('img') if img.get('src')]
        
        return content_data
    
    def _extract_generic_news(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract news content using generic approach."""
        content_data = {}
        
        # Try multiple title extraction strategies
        title_element = (soup.find('h1') or 
                        soup.find(class_=re.compile(r'title|headline')) or 
                        soup.find('title'))
        content_data['title'] = self._clean_text(title_element.get_text() if title_element else '')
        
        # Extract main content using multiple strategies
        content_selectors = [
            'article', 'main', '.article-content', '.story-body', 
            '.content', '.post-content', '[role="main"]'
        ]
        
        content_text = ''
        for selector in content_selectors:
            element = soup.select_one(selector) or soup.find(selector)
            if element and len(element.get_text().strip()) > 100:
                # Clean the element
                for unwanted in element.find_all(['script', 'style', 'nav', 'header']):
                    unwanted.decompose()
                content_text = self._clean_text(element.get_text())
                break
        
        content_data['content'] = content_text
        
        # Extract metadata
        content_data['date'] = self._extract_date(soup)
        content_data['author'] = self._extract_author(soup)
        content_data['category'] = self._extract_category(soup, url)
        content_data['images'] = [img.get('src', img.get('data-src', '')) for img in soup.find_all('img') if img.get('src')]
        
        return content_data
    
    def _extract_date(self, soup: BeautifulSoup, date_selector: str = None) -> str:
        """Extract publication date from news article."""
        # Try provided selector first
        if date_selector:
            date_element = soup.select_one(date_selector)
            if date_element:
                date_text = date_element.get('datetime') or date_element.get_text()
                return self._parse_date(date_text)
        
        # Fallback strategies
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}[./]\d{1,2}[./]\d{4}',  # DD/MM/YYYY or DD.MM.YYYY
            r'\d{1,2}\s+\w+\s+\d{4}',  # DD Month YYYY
            r'\w+\s+\d{1,2},?\s+\d{4}'  # Month DD, YYYY
        ]
        
        # Search in meta tags
        for meta in soup.find_all('meta'):
            if meta.get('property') in ['article:published_time', 'og:updated_time'] or \
               meta.get('name') in ['date', 'pubdate']:
                date_text = meta.get('content', '')
                parsed_date = self._parse_date(date_text)
                if parsed_date:
                    return parsed_date
        
        # Search in time tags
        for time_tag in soup.find_all('time'):
            date_text = time_tag.get('datetime') or time_tag.get_text()
            parsed_date = self._parse_date(date_text)
            if parsed_date:
                return parsed_date
        
        # Search in text content
        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text)
            if match:
                parsed_date = self._parse_date(match.group())
                if parsed_date:
                    return parsed_date
        
        return ''
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author information."""
        # Common author selectors
        author_selectors = [
            '.author', '.byline', '.writer', '.reporter',
            '[itemprop="author"]', '.article-author'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                return self._clean_text(element.get_text())
        
        # Search in meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name') in ['author', 'byline'] or \
               meta.get('property') == 'article:author':
                return self._clean_text(meta.get('content', ''))
        
        return ''
    
    def _extract_category(self, soup: BeautifulSoup, url: str) -> str:
        """Extract category or section information."""
        # Check URL path
        url_parts = urlparse(url).path.split('/')
        for part in url_parts:
            if part and part not in ['', 'index', 'home']:
                return part
        
        # Check for category indicators in the page
        category_indicators = ['category', 'section', 'topic', 'tag']
        for indicator in category_indicators:
            element = soup.find(class_=re.compile(indicator)) or \
                     soup.find(id=re.compile(indicator))
            if element:
                return self._clean_text(element.get_text())
        
        return ''
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """Parse date string into ISO format."""
        if not date_text:
            return None
        
        try:
            # Clean the date text
            date_text = date_text.strip()
            
            # Common date formats to try
            date_formats = [
                '%Y-%m-%dT%H:%M:%S%z',  # ISO format
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%d.%m.%Y',
                '%d %B %Y',
                '%B %d, %Y'
            ]
            
            # Try parsing with different formats
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(date_text, fmt)
                    return date_obj.isoformat()
                except ValueError:
                    continue
            
            # Try regex-based extraction
            date_pattern = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
            if date_pattern:
                return datetime.fromisoformat(date_pattern.group()).isoformat()
            
        except Exception as e:
            logger.debug(f"Error parsing date '{date_text}': {e}")
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def discover_news_articles(self, base_url: str, max_articles: int = 50) -> List[str]:
        """
        Discover news article URLs from a news site.
        
        Args:
            base_url: Base URL of the news site
            max_articles: Maximum number of articles to discover
            
        Returns:
            List of article URLs
        """
        discovered_urls = []
        
        try:
            if not self.rate_limiter.acquire(base_url):
                logger.warning(f"Rate limited when discovering articles from {base_url}")
                return discovered_urls
            
            response = requests.get(base_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find article links
                article_links = []
                
                # Common patterns for article links
                link_selectors = [
                    'a[href*="news"]', 'a[href*="article"]', 'a[href*="story"]',
                    '.article-link', '.news-link', '.story-link'
                ]
                
                for selector in link_selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href:
                            full_url = urljoin(base_url, href)
                            # Filter for actual article URLs
                            if self._is_article_url(full_url):
                                article_links.append(full_url)
                
                # Remove duplicates and limit
                discovered_urls = list(set(article_links))[:max_articles]
                
                logger.info(f"Discovered {len(discovered_urls)} article URLs from {base_url}")
        
        except Exception as e:
            logger.error(f"Error discovering articles from {base_url}: {e}")
        
        finally:
            self.rate_limiter.release(base_url)
        
        return discovered_urls
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL likely points to a news article."""
        url_lower = url.lower()
        
        # Check for article indicators
        article_indicators = [
            'news', 'article', 'story', 'report', 'breaking',
            'pashto', '/ps/', 'ps/'
        ]
        
        return any(indicator in url_lower for indicator in article_indicators)
    
    def scrape_news_site(self, base_url: str, max_articles: int = 20) -> Dict[str, Any]:
        """
        Scrape a complete news site.
        
        Args:
            base_url: Base URL of the news site
            max_articles: Maximum number of articles to scrape
            
        Returns:
            Dictionary with scraping results
        """
        logger.info(f"Starting to scrape news site: {base_url}")
        
        result = {
            'site_url': base_url,
            'start_time': datetime.now().isoformat(),
            'site_config': self.detect_news_site(base_url),
            'articles_found': 0,
            'articles_scraped': 0,
            'success': True,
            'articles': []
        }
        
        try:
            # Discover article URLs
            article_urls = self.discover_news_articles(base_url, max_articles)
            result['articles_found'] = len(article_urls)
            
            if not article_urls:
                result['success'] = False
                result['error'] = "No articles discovered"
                return result
            
            # Scrape each article
            for i, article_url in enumerate(article_urls):
                logger.info(f"Scraping article {i+1}/{len(article_urls)}: {article_url}")
                
                article_result = self.extract_news_article(article_url, result['site_config'])
                result['articles'].append(article_result)
                
                if article_result['success']:
                    result['articles_scraped'] += 1
                
                # Add delay between requests
                if i < len(article_urls) - 1:
                    time.sleep(1)
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            logger.error(f"Error scraping news site {base_url}: {e}")
        
        finally:
            result['end_time'] = datetime.now().isoformat()
        
        return result