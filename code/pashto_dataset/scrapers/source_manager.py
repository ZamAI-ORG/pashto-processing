"""
Source Manager Module
====================

This module manages various sources of Pashto content including news sites,
digital libraries, blogs, and other websites.
"""

import json
import logging
import sqlite3
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urlparse, urljoin
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class SourceConfig:
    """Configuration for a content source."""
    name: str
    url: str
    source_type: str  # 'news', 'blog', 'library', 'archive', 'general'
    language: str = 'ps'  # Pashto language code
    active: bool = True
    priority: int = 1  # 1=high, 2=medium, 3=low
    rate_limit_config: Optional[Dict[str, Any]] = None
    custom_selectors: Optional[Dict[str, str]] = None
    max_pages: int = 100
    last_scraped: Optional[str] = None
    last_success: Optional[str] = None
    success_count: int = 0
    error_count: int = 0
    total_items_scraped: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SourceConfig':
        """Create from dictionary."""
        return cls(**data)


class SourceManager:
    """
    Manages various sources of Pashto content.
    
    Features:
    - Source registration and configuration
    - SQLite database for persistent storage
    - Source prioritization and scheduling
    - Success/error tracking
    - Automatic source discovery
    """
    
    def __init__(self, db_path: str = "data/pashto_sources.db"):
        self.db_path = db_path
        self.sources: Dict[str, SourceConfig] = {}
        self._ensure_db_directory()
        self._init_database()
        self._load_sources()
        self._setup_default_sources()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _init_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    language TEXT DEFAULT 'ps',
                    active BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 1,
                    rate_limit_config TEXT,
                    custom_selectors TEXT,
                    max_pages INTEGER DEFAULT 100,
                    last_scraped TEXT,
                    last_success TEXT,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    total_items_scraped INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Scraping history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    items_scraped INTEGER DEFAULT 0,
                    error_message TEXT,
                    pages_scraped INTEGER DEFAULT 0,
                    duration REAL,
                    FOREIGN KEY (source_name) REFERENCES sources (name)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _load_sources(self):
        """Load sources from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM sources WHERE active = TRUE')
                rows = cursor.fetchall()
                
                columns = [desc[0] for desc in cursor.description]
                
                for row in rows:
                    data = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    if data['rate_limit_config']:
                        try:
                            data['rate_limit_config'] = json.loads(data['rate_limit_config'])
                        except json.JSONDecodeError:
                            data['rate_limit_config'] = None
                    
                    if data['custom_selectors']:
                        try:
                            data['custom_selectors'] = json.loads(data['custom_selectors'])
                        except json.JSONDecodeError:
                            data['custom_selectors'] = None
                    
                    if data['metadata']:
                        try:
                            data['metadata'] = json.loads(data['metadata'])
                        except json.JSONDecodeError:
                            data['metadata'] = None
                    
                    source = SourceConfig.from_dict(data)
                    self.sources[source.name] = source
                
                logger.info(f"Loaded {len(self.sources)} active sources from database")
                
        except Exception as e:
            logger.error(f"Error loading sources from database: {e}")
    
    def _setup_default_sources(self):
        """Set up default Pashto sources if none exist."""
        if self.sources:
            return  # Don't overwrite existing sources
        
        default_sources = [
            {
                "name": "BBC Pashto",
                "url": "https://www.bbc.com/pashto",
                "source_type": "news",
                "priority": 1,
                "custom_selectors": {
                    "title": "h1, h2",
                    "content": ".story-body, .article-body",
                    "date": "time, .date"
                }
            },
            {
                "name": "Al Jazeera Pashto",
                "url": "https://www.aljazeera.com/ps/",
                "source_type": "news",
                "priority": 1,
                "custom_selectors": {
                    "title": "h1, h2, .article-title",
                    "content": ".article-content, .wysiwyg",
                    "date": "time, .date"
                }
            },
            {
                "name": "Afghan Academy",
                "url": "https://www.afghanacademy.org",
                "source_type": "academic",
                "priority": 2,
                "rate_limit_config": {
                    "requests_per_second": 0.5,
                    "max_concurrent": 2
                }
            },
            {
                "name": "Pashto Poetry Archive",
                "url": "https://www.pashtopoetry.org",
                "source_type": "literature",
                "priority": 2,
                "custom_selectors": {
                    "content": ".poem-text, .poetry-content"
                }
            },
            {
                "name": "Afghan Digital Library",
                "url": "https://www.afghandigitallibrary.org",
                "source_type": "library",
                "priority": 2,
                "rate_limit_config": {
                    "requests_per_second": 0.3,
                    "max_concurrent": 1
                }
            }
        ]
        
        for source_data in default_sources:
            try:
                source = SourceConfig(**source_data)
                self.add_source(source)
                logger.info(f"Added default source: {source.name}")
            except Exception as e:
                logger.error(f"Error adding default source {source_data['name']}: {e}")
    
    def add_source(self, source: SourceConfig) -> bool:
        """
        Add a new content source.
        
        Args:
            source: Source configuration
            
        Returns:
            True if added successfully
        """
        try:
            # Validate source
            if not self._validate_source(source):
                return False
            
            # Add to memory
            self.sources[source.name] = source
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if source already exists
                cursor.execute('SELECT id FROM sources WHERE name = ?', (source.name,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing source
                    cursor.execute('''
                        UPDATE sources SET
                            url = ?, source_type = ?, language = ?, active = ?,
                            priority = ?, rate_limit_config = ?, custom_selectors = ?,
                            max_pages = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE name = ?
                    ''', (
                        source.url, source.source_type, source.language, source.active,
                        source.priority, json.dumps(source.rate_limit_config),
                        json.dumps(source.custom_selectors), source.max_pages,
                        json.dumps(source.metadata), source.name
                    ))
                else:
                    # Insert new source
                    cursor.execute('''
                        INSERT INTO sources (
                            name, url, source_type, language, active, priority,
                            rate_limit_config, custom_selectors, max_pages, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        source.name, source.url, source.source_type, source.language,
                        source.active, source.priority, json.dumps(source.rate_limit_config),
                        json.dumps(source.custom_selectors), source.max_pages,
                        json.dumps(source.metadata)
                    ))
                
                conn.commit()
            
            logger.info(f"Source '{source.name}' added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error adding source '{source.name}': {e}")
            return False
    
    def remove_source(self, source_name: str) -> bool:
        """Remove a content source."""
        try:
            if source_name in self.sources:
                del self.sources[source_name]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM sources WHERE name = ?', (source_name,))
                conn.commit()
            
            logger.info(f"Source '{source_name}' removed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error removing source '{source_name}': {e}")
            return False
    
    def get_sources(self, source_type: str = None, active_only: bool = True) -> List[SourceConfig]:
        """
        Get sources by type.
        
        Args:
            source_type: Filter by source type
            active_only: Only return active sources
            
        Returns:
            List of sources
        """
        sources = []
        
        for source in self.sources.values():
            if active_only and not source.active:
                continue
            if source_type and source.source_type != source_type:
                continue
            sources.append(source)
        
        # Sort by priority (high to low) and success count
        sources.sort(key=lambda s: (s.priority, -s.success_count))
        return sources
    
    def get_next_source(self) -> Optional[SourceConfig]:
        """Get the next source to scrape based on priority and scheduling."""
        sources = self.get_sources()
        
        if not sources:
            return None
        
        # Simple round-robin with priority weighting
        for priority in [1, 2, 3]:  # Priority levels
            priority_sources = [s for s in sources if s.priority == priority]
            if priority_sources:
                # Return the source with lowest recent activity
                priority_sources.sort(key=lambda s: (
                    s.last_success or '',
                    s.last_scraped or '',
                    s.error_count
                ))
                return priority_sources[0]
        
        return sources[0]  # Fallback
    
    def update_source_stats(self, source_name: str, success: bool, 
                          items_scraped: int = 0, error_message: str = None,
                          pages_scraped: int = 0, duration: float = 0):
        """Update source statistics after scraping."""
        try:
            if source_name not in self.sources:
                return
            
            source = self.sources[source_name]
            current_time = datetime.now().isoformat()
            
            if success:
                source.success_count += 1
                source.last_success = current_time
                source.total_items_scraped += items_scraped
            else:
                source.error_count += 1
            
            source.last_scraped = current_time
            
            # Update in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sources SET
                        success_count = ?, error_count = ?, last_scraped = ?,
                        last_success = ?, total_items_scraped = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                ''', (
                    source.success_count, source.error_count, source.last_scraped,
                    source.last_success, source.total_items_scraped, source_name
                ))
                
                # Add to history
                cursor.execute('''
                    INSERT INTO scraping_history (
                        source_name, status, items_scraped, error_message,
                        pages_scraped, duration
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    source_name, 'success' if success else 'error',
                    items_scraped, error_message, pages_scraped, duration
                ))
                
                conn.commit()
            
        except Exception as e:
            logger.error(f"Error updating source stats for '{source_name}': {e}")
    
    def discover_sources(self, base_url: str, max_sources: int = 10) -> List[str]:
        """
        Discover potential Pashto sources from a base URL.
        
        Args:
            base_url: Base URL to discover sources from
            max_sources: Maximum number of sources to discover
            
        Returns:
            List of discovered source URLs
        """
        discovered = []
        
        try:
            # This is a placeholder implementation
            # In a real implementation, you might:
            # 1. Scrape the site for language indicators
            # 2. Check for Pashto content
            # 3. Extract navigation links
            # 4. Test for Pashto text
            # 5. Check site structure
            
            logger.info(f"Source discovery from {base_url} not fully implemented")
            return discovered
            
        except Exception as e:
            logger.error(f"Error during source discovery: {e}")
            return discovered
    
    def _validate_source(self, source: SourceConfig) -> bool:
        """Validate source configuration."""
        if not source.name or not source.url:
            logger.error("Source must have name and URL")
            return False
        
        if source.name in self.sources:
            logger.error(f"Source name '{source.name}' already exists")
            return False
        
        # Validate URL
        try:
            parsed = urlparse(source.url)
            if not parsed.scheme or not parsed.netloc:
                logger.error(f"Invalid URL: {source.url}")
                return False
        except Exception:
            logger.error(f"Invalid URL format: {source.url}")
            return False
        
        return True
    
    def get_source_stats(self) -> Dict[str, Any]:
        """Get overall statistics about sources."""
        total_sources = len(self.sources)
        active_sources = len([s for s in self.sources.values() if s.active])
        total_success = sum(s.success_count for s in self.sources.values())
        total_errors = sum(s.error_count for s in self.sources.values())
        total_items = sum(s.total_items_scraped for s in self.sources.values())
        
        by_type = {}
        for source in self.sources.values():
            source_type = source.source_type
            if source_type not in by_type:
                by_type[source_type] = {'count': 0, 'active': 0, 'success': 0}
            by_type[source_type]['count'] += 1
            if source.active:
                by_type[source_type]['active'] += 1
            by_type[source_type]['success'] += source.success_count
        
        return {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'total_success': total_success,
            'total_errors': total_errors,
            'total_items_scraped': total_items,
            'success_rate': total_success / (total_success + total_errors) if (total_success + total_errors) > 0 else 0,
            'by_type': by_type
        }
    
    def export_sources(self, file_path: str):
        """Export sources to JSON file."""
        try:
            sources_data = {name: source.to_dict() for name, source in self.sources.items()}
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sources_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Sources exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting sources: {e}")
    
    def import_sources(self, file_path: str):
        """Import sources from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sources_data = json.load(f)
            
            imported_count = 0
            for name, data in sources_data.items():
                try:
                    source = SourceConfig.from_dict(data)
                    self.add_source(source)
                    imported_count += 1
                except Exception as e:
                    logger.error(f"Error importing source {name}: {e}")
            
            logger.info(f"Imported {imported_count} sources from {file_path}")
            
        except Exception as e:
            logger.error(f"Error importing sources: {e}")