# Pashto Web Scraping Module

A comprehensive web scraping module specifically designed for Pashto text collection. This module provides robust tools for extracting, processing, and managing Pashto content from various online sources including news sites, digital libraries, and cultural repositories.

## 🌟 Features

- **Pashto Text Encoding Detection**: Automatic detection and handling of UTF-8, Arabic script, and Pashto-specific encodings
- **Content Extraction & Cleaning**: Sophisticated HTML parsing and content cleaning specifically optimized for Pashto text
- **Rate Limiting & Error Handling**: Intelligent request throttling with adaptive rate limiting and comprehensive error management
- **Source Management**: Persistent storage and management of content sources with SQLite database
- **Dynamic Content Handling**: Support for various website structures and dynamic content
- **Specialized Scrapers**: Dedicated scrapers for news sites, digital libraries, and academic content
- **Quality Assessment**: Built-in content validation and quality scoring
- **Multi-format Export**: Export scraped content in JSON, TXT, and CSV formats

## 📁 Project Structure

```
code/pashto_dataset/scrapers/
├── __init__.py                 # Module initialization
├── core.py                     # Main scraping engine
├── encoders.py                 # Pashto encoding detection and handling
├── cleaners.py                 # Content extraction and cleaning
├── rate_limiter.py             # Request throttling and rate limiting
├── source_manager.py           # Source management and database
├── news_scraper.py            # Specialized news site scraper
├── library_scraper.py         # Digital library and archive scraper
├── runner.py                  # Command-line interface
├── config.py                  # Configuration management
├── examples.py                # Usage examples
└── README.md                  # This file
```

## 🚀 Quick Start

### Installation

```bash
# Install required dependencies
pip install requests beautifulsoup4 chardet lxml

# Or install with all optional dependencies
pip install requests beautifulsoup4 chardet lxml pandas numpy
```

### Basic Usage

```python
from pashto_scrapers import PashtoScraper

# Initialize the scraper
scraper = PashtoScraper(
    db_path="data/pashto_sources.db",
    output_dir="data/scraped_content",
    max_workers=5
)

# Run comprehensive scraping
results = scraper.scrape_all_sources()

# Export results
content_file = scraper.export_content(format='json')
```

### Command Line Usage

```bash
# Basic scraping of all sources
python -m pashto_scrapers.runner --mode basic

# News scraping
python -m pashto_scrapers.runner --mode news \
    --urls https://www.bbc.com/pashto https://www.aljazeera.com/ps/ \
    --max-articles 20

# Library searching
python -m pashto_scrapers.runner --mode library \
    --library archive_org --terms "pashto poetry" "afghan literature"

# Add custom source
python -m pashto_scrapers.runner --mode add-source \
    --name "My Pashto Site" --url "https://example.com" --type news
```

## 📖 Detailed Usage

### 1. Core Scraper Usage

The `PashtoScraper` is the main entry point for most scraping operations:

```python
from pashto_scrapers import PashtoScraper, SourceConfig

# Initialize with custom settings
scraper = PashtoScraper(
    db_path="my_sources.db",
    output_dir="my_output",
    max_workers=3,
    enable_adaptive_rate_limiting=True
)

# Add a custom source
source = SourceConfig(
    name="Example News",
    url="https://example.com/pashto",
    source_type="news",
    priority=1,
    custom_selectors={
        "title": "h1.article-title",
        "content": ".article-body"
    }
)
scraper.source_manager.add_source(source)

# Scrape specific source types
results = scraper.scrape_all_sources(
    source_types=["news", "blog"],
    max_sources=5
)
```

### 2. News Scraping

Specialized scraper for Pashto news websites:

```python
from pashto_scrapers import NewsScraper

news_scraper = NewsScraper()

# Scrape a specific news site
result = news_scraper.scrape_news_site(
    "https://www.bbc.com/pashto",
    max_articles=15
)

# Extract individual article
article = news_scraper.extract_news_article(
    "https://www.bbc.com/pashto/news/articles/..."
)

# Discover articles from a site
articles = news_scraper.discover_news_articles(
    "https://www.aljazeera.com/ps/",
    max_articles=20
)
```

### 3. Digital Library Scraping

Search and extract content from digital libraries:

```python
from pashto_scrapers import LibraryScraper

library_scraper = LibraryScraper()

# Search for Pashto content
results = library_scraper.search_library_content(
    "pashto poetry",
    library="archive_org",
    max_results=50
)

# Extract document content
doc_result = library_scraper.extract_document_content(
    "https://archive.org/details/pashto-collection"
)

# Scrape a digital library
library_results = library_scraper.scrape_digital_library(
    library_name="archive_org",
    search_terms=["afghan literature", "pashto culture"],
    max_results_per_term=10
)
```

### 4. Content Processing

Direct usage of content processing components:

```python
from pashto_scrapers import PashtoEncoder, ContentCleaner

encoder = PashtoEncoder()
cleaner = ContentCleaner()

# Sample Pashto text
text = "زه یو افغان مېنهوال دی. د پښتو ژبه ډېر ښه ژبه ده."

# Detect encoding
encoding = encoder.detect_encoding(text)
print(f"Encoding: {encoding}")

# Validate Pashto content
validation = encoder.validate_pashto_content(text)
print(f"Has Pashto script: {validation['has_pashto_script']}")
print(f"Has Pashto words: {validation['has_pashto_words']}")

# Extract from HTML
html = "<h1>د پښتو مقاله</h1><p>دا ښکلی متن دی</p>"
content = cleaner.extract_text(html)
print(f"Extracted text: {content['clean_text']}")
```

### 5. Source Management

Manage content sources and track statistics:

```python
from pashto_scrapers import SourceManager, SourceConfig

source_manager = SourceManager("sources.db")

# Add new source
source = SourceConfig(
    name="Academic Papers",
    url="https://example.edu/pashto",
    source_type="academic",
    priority=1
)
source_manager.add_source(source)

# Get sources by type
news_sources = source_manager.get_sources(source_type="news")
academic_sources = source_manager.get_sources(source_type="academic")

# Get statistics
stats = source_manager.get_source_stats()
print(f"Total sources: {stats['total_sources']}")
print(f"Success rate: {stats['success_rate']:.2%}")

# Export/import sources
source_manager.export_sources("my_sources.json")
source_manager.import_sources("my_sources.json")
```

### 6. Rate Limiting

Configure intelligent request throttling:

```python
from pashto_scrapers import AdaptiveRateLimiter, RateLimitConfig

# Initialize adaptive rate limiter
rate_limiter = AdaptiveRateLimiter()

# Configure domain-specific limits
from pashto_scrapers.rate_limiter import RateLimitConfig
config = RateLimitConfig(
    requests_per_second=0.5,
    requests_per_minute=30,
    max_concurrent=2
)
rate_limiter.set_domain_config("news_sites", config)

# Check if request is allowed
if rate_limiter.acquire("https://example.com/news"):
    # Make your request
    rate_limiter.release("https://example.com/news")

# Get current status
status = rate_limiter.get_status("https://example.com/news")
print(f"Current status: {status}")
```

## ⚙️ Configuration

### Default Configuration

The module uses a comprehensive default configuration that can be customized:

```python
from pashto_scrapers.config import get_config, save_config

# Load configuration
config = get_config("my_config.json")

# Customize settings
config['max_workers'] = 3
config['default_requests_per_second'] = 0.5
config['min_quality_score'] = 70

# Save modified configuration
save_config(config, "my_custom_config.json")
```

### Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `data_dir` | Main data directory | `data` |
| `output_dir` | Scraped content output | `data/scraped_content` |
| `max_workers` | Maximum worker threads | `5` |
| `request_timeout` | HTTP request timeout | `30` seconds |
| `enable_adaptive_rate_limiting` | Enable smart rate limiting | `True` |
| `min_content_length` | Minimum content length | `100` characters |
| `min_quality_score` | Minimum quality score | `60` |
| `require_pashto_indicators` | Require Pashto language detection | `True` |

## 🎯 Supported Sources

### News Sites
- BBC Pashto
- Al Jazeera Pashto
- Tolo News
- 1TV News
- Other Pashto news websites

### Digital Libraries
- Internet Archive
- HathiTrust Digital Library
- World Digital Library
- Local digital collections

### Academic Sources
- University repositories
- Research databases
- Academic journals
- Conference proceedings

### Cultural Repositories
- Poetry collections
- Literature archives
- Cultural heritage sites
- Historical documents

## 🔧 Advanced Features

### Custom Content Selectors

Define custom CSS selectors for specific websites:

```python
source = SourceConfig(
    name="Custom Site",
    url="https://example.com",
    custom_selectors={
        "title": "h1.page-title, .article-headline",
        "content": ".main-content, .article-body",
        "date": ".publish-date, time[datetime]",
        "author": ".byline, .author-name"
    }
)
```

### Content Quality Assessment

The module automatically assesses content quality:

```python
# Quality factors considered:
# - Content length
# - Pashto language indicators
# - Text structure
# - Error rates
# - Encoding validity

quality = cleaner.validate_content_quality(text)
print(f"Quality score: {quality['score']}/100")
print(f"Is valid: {quality['is_valid']}")
print(f"Issues: {quality['issues']}")
```

### Error Handling and Recovery

Comprehensive error handling with automatic recovery:

```python
# The system handles:
# - Network timeouts
# - HTTP errors (404, 500, etc.)
# - Encoding issues
# - Rate limiting
# - Content extraction failures
# - Malformed HTML

# All errors are logged and tracked
# Failed requests are retried with backoff
# Source statistics are maintained
```

### Export Options

Multiple export formats available:

```python
# JSON format (recommended)
content_file = scraper.export_content(format='json')

# Text format
text_file = scraper.export_content(format='txt')

# CSV format
csv_file = scraper.export_content(format='csv')
```

## 📊 Monitoring and Statistics

### Real-time Statistics

```python
# Get current scraping statistics
stats = scraper.get_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Items scraped: {stats['items_scraped']}")
print(f"Processing speed: {stats['items_per_second']:.2f} items/sec")
```

### Source Performance Tracking

```python
# Track individual source performance
for source in scraper.source_manager.get_sources():
    print(f"{source.name}:")
    print(f"  Successes: {source.success_count}")
    print(f"  Errors: {source.error_count}")
    print(f"  Last scraped: {source.last_scraped}")
    print(f"  Items scraped: {source.total_items_scraped}")
```

## 🚨 Best Practices

### Respectful Scraping

1. **Rate Limiting**: Always use appropriate rate limits
2. **User-Agent**: Set meaningful user agents
3. **Robots.txt**: Check and respect robots.txt files
4. **Terms of Service**: Review and comply with site terms

### Content Quality

1. **Validation**: Always validate extracted content
2. **Encoding**: Ensure proper UTF-8 encoding
3. **Cleaning**: Remove noise and unwanted content
4. **Verification**: Verify Pashto language presence

### Performance Optimization

1. **Concurrency**: Use appropriate worker counts
2. **Caching**: Cache successful requests
3. **Filtering**: Filter content before processing
4. **Monitoring**: Monitor performance and errors

### Error Handling

1. **Logging**: Enable comprehensive logging
2. **Recovery**: Implement automatic recovery
3. **Monitoring**: Track error rates and patterns
4. **Fallbacks**: Have fallback strategies ready

## 🐛 Troubleshooting

### Common Issues

1. **Encoding Errors**
   ```python
   # Ensure proper encoding detection
   encoding = encoder.detect_encoding(content)
   normalized = encoder.normalize_text(content, encoding)
   ```

2. **Rate Limiting**
   ```python
   # Check rate limiter status
   status = rate_limiter.get_status(url)
   wait_time = rate_limiter.wait_time(url)
   ```

3. **Content Not Found**
   ```python
   # Verify selectors
   quality = cleaner.validate_content_quality(text)
   if not quality['is_valid']:
       print(f"Issues: {quality['issues']}")
   ```

### Debugging

```python
# Enable debug logging
import logging
logging.getLogger('pashto_scrapers').setLevel(logging.DEBUG)

# Check source configuration
source_manager = SourceManager()
for source in source_manager.get_sources():
    print(f"Source: {source.name}")
    print(f"Config: {source.custom_selectors}")
```

## 📝 Examples

Run the comprehensive examples:

```bash
cd code/pashto_dataset/scrapers
python examples.py
```

This will demonstrate:
- Basic scraping operations
- News site processing
- Digital library searching
- Source management
- Content processing
- Rate limiting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd pashto-scrapers

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run examples
python examples.py
```

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- Pashto language processing communities
- Open source web scraping frameworks
- Digital library initiatives
- Afghan cultural preservation efforts

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the examples and documentation
- Review the troubleshooting section

---

**Note**: This tool is designed for educational and research purposes. Always respect website terms of service, robots.txt files, and applicable laws when scraping content.