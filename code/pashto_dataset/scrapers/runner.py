"""
Pashto Web Scraping Runner
=========================

Main script to run Pashto web scraping operations with various configurations.
Demonstrates how to use the complete scraping system.
"""

import argparse
import logging
import json
import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add the scrapers module to the path
sys.path.append(os.path.dirname(__file__))

from .core import PashtoScraper
from .source_manager import SourceManager, SourceConfig
from .news_scraper import NewsScraper
from .library_scraper import LibraryScraper


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Set up logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


def run_basic_scraping(output_dir: str = "data/scraped_content", 
                      max_workers: int = 3,
                      source_types: List[str] = None,
                      max_sources: int = None) -> Dict[str, Any]:
    """
    Run basic Pashto content scraping.
    
    Args:
        output_dir: Directory to save results
        max_workers: Maximum number of worker threads
        source_types: Types of sources to scrape
        max_sources: Maximum number of sources to process
        
    Returns:
        Scraping results
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting basic Pashto content scraping")
    
    # Initialize scraper
    scraper = PashtoScraper(
        output_dir=output_dir,
        max_workers=max_workers
    )
    
    # Run scraping
    results = scraper.scrape_all_sources(
        source_types=source_types,
        max_sources=max_sources
    )
    
    # Export results
    content_file = scraper.export_content(format='json')
    logger.info(f"Content exported to: {content_file}")
    
    return results


def run_news_scraping(news_urls: List[str], 
                     output_dir: str = "data/news_content",
                     max_articles_per_site: int = 10) -> Dict[str, Any]:
    """
    Run specialized news scraping.
    
    Args:
        news_urls: List of news site URLs
        output_dir: Output directory
        max_articles_per_site: Maximum articles per news site
        
    Returns:
        News scraping results
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting news scraping for {len(news_urls)} sites")
    
    news_scraper = NewsScraper()
    all_results = []
    
    for url in news_urls:
        logger.info(f"Scraping news site: {url}")
        result = news_scraper.scrape_news_site(url, max_articles_per_site)
        all_results.append(result)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"{output_dir}/news_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'scraped_at': datetime.now().isoformat(),
            'total_sites': len(news_urls),
            'results': all_results
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"News results saved to: {results_file}")
    
    return {
        'total_sites': len(news_urls),
        'results': all_results,
        'output_file': results_file
    }


def run_library_scraping(library: str,
                        search_terms: List[str],
                        output_dir: str = "data/library_content",
                        max_results_per_term: int = 10) -> Dict[str, Any]:
    """
    Run specialized digital library scraping.
    
    Args:
        library: Digital library to search
        search_terms: Search terms
        output_dir: Output directory
        max_results_per_term: Maximum results per search term
        
    Returns:
        Library scraping results
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting library scraping in {library} for terms: {search_terms}")
    
    library_scraper = LibraryScraper()
    result = library_scraper.scrape_digital_library(
        library_name=library,
        search_terms=search_terms,
        max_results_per_term=max_results_per_term
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"{output_dir}/library_results_{library}_{timestamp}.json"
    
    os.makedirs(output_dir, exist_ok=True)
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Library results saved to: {results_file}")
    
    return result


def add_custom_source(name: str, url: str, source_type: str,
                     output_dir: str = "data",
                     priority: int = 2,
                     **kwargs) -> bool:
    """
    Add a custom source to the scraping system.
    
    Args:
        name: Name of the source
        url: Base URL of the source
        source_type: Type of source ('news', 'blog', 'library', 'general')
        output_dir: Data directory
        priority: Priority level (1=high, 2=medium, 3=low)
        **kwargs: Additional source configuration
        
    Returns:
        True if source was added successfully
    """
    logger = logging.getLogger(__name__)
    
    # Initialize source manager
    db_path = os.path.join(output_dir, "pashto_sources.db")
    source_manager = SourceManager(db_path)
    
    # Create source configuration
    source = SourceConfig(
        name=name,
        url=url,
        source_type=source_type,
        priority=priority,
        **kwargs
    )
    
    # Add source
    success = source_manager.add_source(source)
    
    if success:
        logger.info(f"Successfully added source: {name} ({url})")
    else:
        logger.error(f"Failed to add source: {name}")
    
    return success


def list_sources(source_type: str = None, output_dir: str = "data") -> Dict[str, Any]:
    """
    List all configured sources.
    
    Args:
        source_type: Filter by source type
        output_dir: Data directory
        
    Returns:
        Source information
    """
    db_path = os.path.join(output_dir, "pashto_sources.db")
    source_manager = SourceManager(db_path)
    
    sources = source_manager.get_sources(source_type=source_type)
    
    source_info = {
        'total_sources': len(sources),
        'sources': [
            {
                'name': s.name,
                'url': s.url,
                'type': s.source_type,
                'active': s.active,
                'priority': s.priority,
                'success_count': s.success_count,
                'error_count': s.error_count,
                'last_scraped': s.last_scraped
            }
            for s in sources
        ]
    }
    
    return source_info


def get_scraping_stats(output_dir: str = "data") -> Dict[str, Any]:
    """
    Get comprehensive scraping statistics.
    
    Args:
        output_dir: Data directory
        
    Returns:
        Scraping statistics
    """
    db_path = os.path.join(output_dir, "pashto_sources.db")
    source_manager = SourceManager(db_path)
    
    scraper = PashtoScraper(output_dir=os.path.join(output_dir, "scraped_content"))
    
    stats = {
        'source_stats': source_manager.get_source_stats(),
        'scraping_stats': scraper.get_stats(),
        'timestamp': datetime.now().isoformat()
    }
    
    return stats


def main():
    """Main entry point for the Pashto scraping tool."""
    parser = argparse.ArgumentParser(
        description="Pashto Web Scraping Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scraping of all sources
  python -m pashto_scrapers.runner --mode basic
  
  # News scraping
  python -m pashto_scrapers.runner --mode news --urls https://www.bbc.com/pashto https://www.aljazeera.com/ps/
  
  # Library scraping
  python -m pashto_scrapers.runner --mode library --library archive_org --terms "pashto poetry" "afghan literature"
  
  # Add custom source
  python -m pashto_scrapers.runner --mode add-source --name "My Source" --url "https://example.com" --type news
  
  # List sources
  python -m pashto_scrapers.runner --mode list-sources --type news
        """
    )
    
    parser.add_argument('--mode', required=True, 
                       choices=['basic', 'news', 'library', 'add-source', 'list-sources', 'stats'],
                       help='Scraping mode')
    
    # General options
    parser.add_argument('--output-dir', default='data', 
                       help='Output directory (default: data)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--log-file', 
                       help='Log file path')
    
    # Basic scraping options
    parser.add_argument('--max-workers', type=int, default=3,
                       help='Maximum worker threads')
    parser.add_argument('--source-types', nargs='*',
                       help='Source types to scrape')
    parser.add_argument('--max-sources', type=int,
                       help='Maximum number of sources to process')
    
    # News scraping options
    parser.add_argument('--urls', nargs='*',
                       help='News site URLs')
    parser.add_argument('--max-articles', type=int, default=10,
                       help='Maximum articles per site')
    
    # Library scraping options
    parser.add_argument('--library', 
                       choices=['archive_org', 'hathitrust', 'world_digital_library'],
                       help='Digital library to search')
    parser.add_argument('--terms', nargs='*',
                       help='Search terms')
    parser.add_argument('--max-results', type=int, default=10,
                       help='Maximum results per search term')
    
    # Add source options
    parser.add_argument('--name',
                       help='Source name')
    parser.add_argument('--url',
                       help='Source URL')
    parser.add_argument('--type',
                       choices=['news', 'blog', 'library', 'general', 'academic'],
                       help='Source type')
    parser.add_argument('--priority', type=int, default=2,
                       help='Source priority (1=high, 2=medium, 3=low)')
    
    # List sources options
    parser.add_argument('--type-filter',
                       help='Filter sources by type')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    try:
        if args.mode == 'basic':
            results = run_basic_scraping(
                output_dir=os.path.join(args.output_dir, 'scraped_content'),
                max_workers=args.max_workers,
                source_types=args.source_types,
                max_sources=args.max_sources
            )
            print(f"Basic scraping completed. Found {results['sources_processed']} sources.")
        
        elif args.mode == 'news':
            if not args.urls:
                logger.error("News URLs required for news mode")
                return 1
            
            results = run_news_scraping(
                news_urls=args.urls,
                output_dir=os.path.join(args.output_dir, 'news_content'),
                max_articles_per_site=args.max_articles
            )
            print(f"News scraping completed. Processed {results['total_sites']} sites.")
        
        elif args.mode == 'library':
            if not args.library or not args.terms:
                logger.error("Library and terms required for library mode")
                return 1
            
            results = run_library_scraping(
                library=args.library,
                search_terms=args.terms,
                output_dir=os.path.join(args.output_dir, 'library_content'),
                max_results_per_term=args.max_results
            )
            print(f"Library scraping completed. Found {results['documents_found']} documents.")
        
        elif args.mode == 'add-source':
            if not all([args.name, args.url, args.type]):
                logger.error("Name, URL, and type required for add-source mode")
                return 1
            
            success = add_custom_source(
                name=args.name,
                url=args.url,
                source_type=args.type,
                output_dir=args.output_dir,
                priority=args.priority
            )
            print(f"Source addition {'successful' if success else 'failed'}.")
        
        elif args.mode == 'list-sources':
            source_info = list_sources(
                source_type=args.type_filter,
                output_dir=args.output_dir
            )
            print(f"Found {source_info['total_sources']} sources:")
            for source in source_info['sources']:
                print(f"  {source['name']} ({source['type']}) - {source['url']}")
        
        elif args.mode == 'stats':
            stats = get_scraping_stats(args.output_dir)
            print("Scraping Statistics:")
            print(f"  Total sources: {stats['source_stats']['total_sources']}")
            print(f"  Active sources: {stats['source_stats']['active_sources']}")
            print(f"  Total items scraped: {stats['scraping_stats']['items_scraped']}")
            print(f"  Success rate: {stats['scraping_stats']['success_rate']:.2%}")
    
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())