"""
Pashto Web Scraping Module
==========================

A comprehensive web scraping module specifically designed for Pashto text collection.
Handles Pashto text encoding detection, content extraction, and error management.

Features:
- Pashto text encoding detection (UTF-8, Arabic script)
- Content extraction and cleaning
- Rate limiting and error handling
- Source management
- Dynamic content handling
- Comprehensive logging
"""

from .core import PashtoScraper
from .encoders import PashtoEncoder
from .cleaners import ContentCleaner
from .rate_limiter import RateLimiter
from .source_manager import SourceManager
from .news_scraper import NewsScraper
from .library_scraper import LibraryScraper

__version__ = "1.0.0"
__author__ = "Pashto Dataset Collection Team"

__all__ = [
    "PashtoScraper",
    "PashtoEncoder", 
    "ContentCleaner",
    "RateLimiter",
    "SourceManager",
    "NewsScraper",
    "LibraryScraper"
]