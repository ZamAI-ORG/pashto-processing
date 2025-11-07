"""
Configuration file for Pashto Web Scraping Module
===============================================

This file contains default configurations and settings for the Pashto scraping system.
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    # Data directories
    'data_dir': 'data',
    'output_dir': 'data/scraped_content',
    'cache_dir': 'data/cache',
    'log_dir': 'logs',
    
    # Database settings
    'db_path': 'data/pashto_sources.db',
    
    # Scraping settings
    'max_workers': 5,
    'request_timeout': 30,
    'max_retries': 3,
    'retry_delay': 1.0,
    
    # Rate limiting
    'default_requests_per_second': 1.0,
    'default_requests_per_minute': 60,
    'default_max_concurrent': 5,
    'enable_adaptive_rate_limiting': True,
    
    # Content filtering
    'min_content_length': 100,
    'min_quality_score': 60,
    'require_pashto_indicators': True,
    
    # Output settings
    'export_formats': ['json', 'txt'],
    'include_metadata': True,
    'include_error_logs': True,
    
    # News site configurations
    'news_sites': {
        'bbc_pashto': {
            'name': 'BBC Pashto',
            'url': 'https://www.bbc.com/pashto',
            'rate_limit': {
                'requests_per_second': 0.5,
                'requests_per_minute': 30,
                'max_concurrent': 2
            },
            'selectors': {
                'title': 'h1[data-testid="main-heading"], h1',
                'content': '[data-testid="article-body"], .story-body',
                'date': 'time[datetime], time[data-testid="timestamp"]'
            }
        },
        'aljazeera_pashto': {
            'name': 'Al Jazeera Pashto',
            'url': 'https://www.aljazeera.com/ps/',
            'rate_limit': {
                'requests_per_second': 0.5,
                'requests_per_minute': 30,
                'max_concurrent': 2
            },
            'selectors': {
                'title': '.article-title h1, h1.article-title',
                'content': '.article-content, .wysiwyg',
                'date': 'time[datetime], .article-date'
            }
        }
    },
    
    # Library configurations
    'digital_libraries': {
        'archive_org': {
            'name': 'Internet Archive',
            'base_url': 'https://archive.org',
            'search_url': 'https://archive.org/advancedsearch.php',
            'rate_limit': {
                'requests_per_second': 0.3,
                'requests_per_minute': 20,
                'max_concurrent': 2
            }
        }
    },
    
    # Pashto language detection
    'pashto_indicators': [
        'pashto', 'پښتو', 'pus', 'ps', 'afghan', 'afghanistan'
    ],
    'pashto_patterns': [
        r'زه\s+', r'دو\s+', r'موږ\s+', r'تاسو\s+', r'دوی\s+',
        r'څخه', r'ته', r'سره', r'په\s+', r'د\s+'
    ],
    
    # Content cleaning
    'noise_patterns': [
        r'<script[^>]*>.*?</script>',
        r'<style[^>]*>.*?</style>',
        r'<nav[^>]*>.*?</nav>',
        r'<header[^>]*>.*?</header>',
        r'<footer[^>]*>.*?</footer>',
        r'<aside[^>]*>.*?</aside>',
        r'<!--.*?-->',
    ],
    
    # Logging
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_to_file': True,
    'log_file_max_size': 10485760,  # 10MB
    'log_file_backup_count': 5
}


def get_config(config_file: str = None) -> Dict[str, Any]:
    """
    Load configuration from file or return default.
    
    Args:
        config_file: Path to configuration file (JSON format)
        
    Returns:
        Configuration dictionary
    """
    if config_file and os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Merge with defaults
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
            print("Using default configuration")
    
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any], config_file: str):
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_file: Path to save configuration
    """
    try:
        import json
        import os
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Configuration saved to {config_file}")
    except Exception as e:
        print(f"Error saving config file {config_file}: {e}")


def create_sample_config(output_file: str = "pashto_scraper_config.json"):
    """Create a sample configuration file."""
    sample_config = DEFAULT_CONFIG.copy()
    
    # Customize some settings for the sample
    sample_config['output_dir'] = 'sample_data/scraped_content'
    sample_config['log_level'] = 'DEBUG'
    
    save_config(sample_config, output_file)


if __name__ == "__main__":
    # Create sample configuration
    create_sample_config()
    print("Sample configuration created: pashto_scraper_config.json")