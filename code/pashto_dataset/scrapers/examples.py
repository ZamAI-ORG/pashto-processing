"""
Example Usage of Pashto Web Scraping Module
==========================================

This script demonstrates how to use the comprehensive Pashto web scraping module
for various types of content collection.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

# Import the scraping components
from core import PashtoScraper
from source_manager import SourceManager, SourceConfig
from news_scraper import NewsScraper
from library_scraper import LibraryScraper
from rate_limiter import AdaptiveRateLimiter
from encoders import PashtoEncoder
from cleaners import ContentCleaner


def example_basic_scraping():
    """Example 1: Basic scraping of all configured sources."""
    print("=" * 60)
    print("Example 1: Basic Pashto Content Scraping")
    print("=" * 60)
    
    # Initialize the main scraper
    scraper = PashtoScraper(
        db_path="examples/data/pashto_sources.db",
        output_dir="examples/data/scraped_content",
        max_workers=3,
        enable_adaptive_rate_limiting=True
    )
    
    # Add some custom sources
    print("Adding custom sources...")
    scraper.add_source(
        name="Example News Site",
        url="https://example.com/pashto-news",
        source_type="news",
        priority=1,
        custom_selectors={
            "title": "h1.news-title",
            "content": ".news-content"
        }
    )
    
    # Run scraping on all sources
    print("Starting comprehensive scraping...")
    results = scraper.scrape_all_sources(
        source_types=["news", "general"],
        max_sources=3  # Limit for example
    )
    
    # Print results
    print(f"Scraping completed!")
    print(f"Sources processed: {results['sources_processed']}/{results['total_sources']}")
    print(f"Total items scraped: {results['overall_stats']['items_scraped']}")
    
    # Export results
    content_file = scraper.export_content(format='json')
    print(f"Content exported to: {content_file}")
    
    return results


def example_news_scraping():
    """Example 2: Specialized news scraping."""
    print("\n" + "=" * 60)
    print("Example 2: News Site Scraping")
    print("=" * 60)
    
    # Initialize news scraper
    news_scraper = NewsScraper()
    
    # List of news sites to scrape (example URLs)
    news_sites = [
        "https://www.bbc.com/pashto",
        "https://www.aljazeera.com/ps/"
    ]
    
    print(f"Scraping {len(news_sites)} news sites...")
    
    all_results = []
    for i, url in enumerate(news_sites, 1):
        print(f"Processing site {i}/{len(news_sites)}: {url}")
        
        try:
            result = news_scraper.scrape_news_site(url, max_articles=5)
            all_results.append(result)
            
            print(f"  Found: {result['articles_found']} articles")
            print(f"  Scraped: {result['articles_scraped']} articles")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Save results
    output_file = f"examples/data/news_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'scraped_at': datetime.now().isoformat(),
            'total_sites': len(news_sites),
            'results': all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {output_file}")
    return all_results


def example_library_scraping():
    """Example 3: Digital library scraping."""
    print("\n" + "=" * 60)
    print("Example 3: Digital Library Scraping")
    print("=" * 60)
    
    # Initialize library scraper
    library_scraper = LibraryScraper()
    
    # Search terms for Pashto content
    search_terms = [
        "pashto poetry",
        "afghan literature", 
        "pashto culture",
        "afghan heritage"
    ]
    
    print(f"Searching for terms: {search_terms}")
    
    try:
        # Search Internet Archive for Pashto content
        results = library_scraper.search_library_content(
            "pashto poetry",
            library="archive_org",
            max_results=10
        )
        
        print(f"Found {len(results)} results in Internet Archive")
        
        # Process first few results
        for i, result in enumerate(results[:3], 1):
            print(f"\nProcessing result {i}: {result.get('title', 'Unknown')}")
            
            # Extract content from the document
            if 'url' in result:
                doc_result = library_scraper.extract_document_content(result['url'])
                print(f"  Extraction success: {doc_result['success']}")
                if doc_result['success']:
                    print(f"  Document type: {doc_result.get('document_type', 'unknown')}")
        
    except Exception as e:
        print(f"Library scraping error: {e}")
    
    return results if 'results' in locals() else []


def example_source_management():
    """Example 4: Source management and statistics."""
    print("\n" + "=" * 60)
    print("Example 4: Source Management")
    print("=" * 60)
    
    # Initialize source manager
    source_manager = SourceManager("examples/data/pashto_sources.db")
    
    # Add new sources
    new_sources = [
        SourceConfig(
            name="Example Academic Site",
            url="https://example.edu/pashto-studies",
            source_type="academic",
            priority=1,
            custom_selectors={
                "title": "h1.academic-title",
                "content": ".academic-content"
            }
        ),
        SourceConfig(
            name="Example Blog",
            url="https://example-blog.com/pashto",
            source_type="blog",
            priority=2,
            rate_limit_config={
                "requests_per_second": 1.0,
                "max_concurrent": 3
            }
        )
    ]
    
    print("Adding new sources...")
    for source in new_sources:
        success = source_manager.add_source(source)
        print(f"  {source.name}: {'Added' if success else 'Failed'}")
    
    # List all sources
    all_sources = source_manager.get_sources()
    print(f"\nTotal sources: {len(all_sources)}")
    
    for source in all_sources:
        print(f"  - {source.name} ({source.source_type}) - Priority: {source.priority}")
    
    # Get statistics
    stats = source_manager.get_source_stats()
    print(f"\nSource Statistics:")
    print(f"  Total sources: {stats['total_sources']}")
    print(f"  Active sources: {stats['active_sources']}")
    print(f"  Total success: {stats['total_success']}")
    print(f"  Total errors: {stats['total_errors']}")
    print(f"  Success rate: {stats['success_rate']:.2%}")
    
    return source_manager


def example_content_processing():
    """Example 5: Content processing and analysis."""
    print("\n" + "=" * 60)
    print("Example 5: Content Processing and Analysis")
    print("=" * 60)
    
    # Initialize processing components
    encoder = PashtoEncoder()
    cleaner = ContentCleaner()
    
    # Sample Pashto text
    sample_texts = [
        "زه یو افغان مېنهوال دی",  # "I am an Afghan lover"
        "د پښتو ژبه ډېر ښه ژبه ده",  # "Pashto language is very beautiful"
        "This is English text for comparison",
        "مېرمن لیلۍ د ښار څانګه پیل کړه"  # "Mrs. Layla started the city branch"
    ]
    
    print("Processing sample texts...")
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nText {i}: {text}")
        
        # Encoding detection
        encoding = encoder.detect_encoding(text)
        print(f"  Detected encoding: {encoding}")
        
        # Pashto content validation
        validation = encoder.validate_pashto_content(text)
        print(f"  Pashto script: {validation['has_pashto_script']}")
        print(f"  Pashto words: {validation['has_pashto_words']}")
        
        # Content quality
        quality = cleaner.validate_content_quality(text)
        print(f"  Quality score: {quality['score']}")
        print(f"  Is valid: {quality['is_valid']}")
    
    # Sample HTML processing
    sample_html = """
    <html>
    <head><title>د پښتو مقاله</title></head>
    <body>
        <h1>د افغانستان تاریخ</h1>
        <p>دا د افغانستان ښکلی تاریخ دی. پښتو ژبه د دغه هیواد د څو اونیو کلتور است.</p>
        <script>console.log('This should be removed');</script>
    </body>
    </html>
    """
    
    print(f"\nProcessing HTML content...")
    result = cleaner.extract_text(sample_html)
    
    print(f"  Clean text: {result['clean_text'][:100]}...")
    print(f"  Metadata title: {result['metadata'].get('title', 'None')}")
    print(f"  Pashto indicators: {result.get('language_indicators', {}).get('pashto_words', 0)}")


def example_rate_limiting():
    """Example 6: Rate limiting demonstration."""
    print("\n" + "=" * 60)
    print("Example 6: Rate Limiting")
    print("=" * 60)
    
    # Initialize rate limiter
    rate_limiter = AdaptiveRateLimiter()
    
    # Test URLs
    test_urls = [
        "https://www.bbc.com/pashto",
        "https://www.aljazeera.com/ps/",
        "https://example.com/news"
    ]
    
    print("Testing rate limiting...")
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        
        # Check if request is allowed
        allowed = rate_limiter.acquire(url)
        print(f"  Request allowed: {allowed}")
        
        if allowed:
            # Simulate some processing time
            import time
            time.sleep(0.1)
            
            # Record successful response
            rate_limiter.record_response(url, 200, 0.1)
            
            # Release the slot
            rate_limiter.release(url)
        
        # Get status
        status = rate_limiter.get_status(url)
        print(f"  Current status: {status}")
    
    print("\nRate limiting demonstration completed.")


def main():
    """Run all examples."""
    print("Pashto Web Scraping Module - Usage Examples")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run examples
        example_basic_scraping()
        example_news_scraping()
        example_library_scraping()
        example_source_management()
        example_content_processing()
        example_rate_limiting()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
        print("\nNext steps:")
        print("1. Modify the examples to use your own sources")
        print("2. Run the main runner: python runner.py --mode basic")
        print("3. Check the generated data files")
        print("4. Customize configurations in config.py")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())