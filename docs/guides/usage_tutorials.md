# Usage Tutorials

Step-by-step tutorials for common workflows and use cases with the Pashto Dataset Pipeline.

## 📋 Table of Contents

- [Basic Text Processing](#basic-text-processing)
- [Web Scraping Tutorial](#web-scraping-tutorial)
- [Social Media Data Processing](#social-media-data-processing)
- [PDF Document Processing](#pdf-document-processing)
- [Database Integration](#database-integration)
- [Batch Processing Large Datasets](#batch-processing-large-datasets)
- [Custom Quality Filters](#custom-quality-filters)
- [Real-time Processing](#real-time-processing)
- [Multi-language Support](#multi-language-support)
- [Performance Optimization](#performance-optimization)

## 📖 Basic Text Processing

### Tutorial 1: Process Plain Text Files

Learn the fundamentals of processing Pashto text files.

#### Step 1: Prepare Text Data
```bash
# Create sample text files
mkdir -p data/raw/texts
cd data/raw/texts

# Create sample Pashto text files
cat > article1.txt << 'EOF'
زموږ ژبه د پښتو ژبه ده چې د افغانستان او پاکستان د خلکو ژبه ده.
دا ښه ژبه ده او موږ یې ډېر څیړو.
پښتو ژبه د نړۍ د ژبو څخه یوه ښه ژبه ده.
EOF

cat > article2.txt << 'EOF'
د ژبې څیړنه ډېر ښه کار دی.
موږ باید زموږ د ژبې څیړنه وکړو.
دا څیړنه به زموږ ژبه ډېر ښه کړي.
EOF

cat > duplicate.txt << 'EOF'
زموږ ژبه د پښتو ژبه ده چې د افغانستان او پاکستان د خلکو ژبه ده.
دا ښه ژبه ده او موږ یې ډېر څیړو.
پښتو ژبه د نړۍ د ژبو څخه یوه ښه ژبه ده.
EOF
```

#### Step 2: Create Configuration
```yaml
# config/text_processing.yaml
pipeline:
  name: "Basic Text Processing"
  version: "1.0"

input:
  data_directory: "data/raw/texts"
  supported_formats: ["txt"]
  encoding: "utf-8"

processing:
  normalize_text: true
  filter_min_length: 20
  require_pashto: true
  remove_duplicates: true
  duplicate_strategy: "fuzzy"

output:
  data_directory: "data/processed/texts"
  format: "json"
  include_metadata: true

quality:
  min_quality_score: 0.6
  enable_quality_scoring: true
```

#### Step 3: Process the Data
```bash
# Run the pipeline
pashto-pipeline process \
  --input data/raw/texts/ \
  --output data/processed/texts/ \
  --config config/text_processing.yaml \
  --verbose

# Expected output:
# INFO: Starting pipeline execution...
# INFO: Found 3 input files
# INFO: Processing: article1.txt (3 sentences)
# INFO: Processing: article2.txt (3 sentences)
# INFO: Processing: duplicate.txt (3 sentences)
# INFO: Duplicate detection found 3 duplicates
# INFO: Removing 1 exact duplicate
# INFO: Removing 2 fuzzy duplicates
# INFO: Quality scoring completed
# INFO: Pipeline completed successfully!
# INFO: Results: 5 unique sentences, avg quality: 0.87
```

## 🌐 Web Scraping Tutorial

### Tutorial 2: Collect Pashto Content from Websites

Learn how to scrape Pashto text from websites and online sources.

#### Step 1: Configure Web Scraping
```yaml
# config/web_scraping.yaml
pipeline:
  name: "Web Scraping Pipeline"
  description: "Collect Pashto content from websites"

input:
  type: "web_scraping"
  data_directory: null
  
  scraping:
    urls:
      - "https://example.com/pashto/news"
      - "https://news.af/pashto"
      - "https://www.bbc.com/pashto"
    
    selectors:
      article_content: "article p, .article-content p"
      title: "h1, .article-title"
      date: "time, .publish-date"
      author: ".author, .byline"
    
    rate_limiting:
      requests_per_second: 0.5
      delay_between_requests: 2.0
      timeout: 30
      max_retries: 3
    
    browser:
      user_agent: "Mozilla/5.0 (compatible; PashtoBot/1.0)"
      headless: true
      window_size: [1920, 1080]
      javascript_enabled: true
    
    proxy:
      enabled: false
      # proxy_url: "http://proxy:8080"
    
    extraction:
      clean_html: true
      remove_scripts: true
      remove_styles: true
      extract_metadata: true

processing:
  normalize_text: true
  filter_min_length: 50
  filter_max_length: 2000
  require_pashto: true
  min_pashto_ratio: 0.8
  remove_html_tags: true
  remove_scripts_and_styles: true
  decode_html_entities: true

output:
  data_directory: "data/processed/web_scraped"
  format: "json"
  include_metadata: true
  include_source_url: true
  include_extraction_date: true

logging:
  level: "INFO"
  log_filtered_items: true
```

#### Step 2: Advanced Scraping Configuration
```yaml
# config/advanced_scraping.yaml
input:
  type: "web_scraping"
  
  scraping:
    # Multiple page types
    page_types:
      news:
        url_pattern: "https://example.com/news/*"
        selectors:
          content: ".news-content p"
          title: "h1.news-title"
      blog:
        url_pattern: "https://example.com/blog/*"
        selectors:
          content: ".post-content p"
          title: "h1.post-title"
    
    # Pagination
    pagination:
      enabled: true
      next_page_selector: "a.next"
      max_pages: 10
    
    # Content filtering
    content_filter:
      min_content_length: 100
      exclude_patterns:
        - "advertisement"
        - "cookie"
        - "privacy"
        - "sitemap"
      include_patterns:
        - "pashto"
        - "افغان"
        - "پښتو"
```

#### Step 3: Run Web Scraping
```bash
# Start scraping
pashto-pipeline scrape \
  --config config/web_scraping.yaml \
  --output data/processed/web_scraped/ \
  --max-pages 50

# Monitor progress
tail -f logs/pipeline.log

# Alternative: Run in background
pashto-pipeline scrape \
  --config config/web_scraping.yaml \
  --output data/processed/web_scraped/ \
  --background \
  --pid-file scraper.pid

# Check status
pashto-pipeline status --pid-file scraper.pid
```

## 📱 Social Media Data Processing

### Tutorial 3: Process Twitter and Facebook Data

Handle social media content with special processing for hashtags, mentions, and URLs.

#### Step 1: Social Media Configuration
```yaml
# config/social_media.yaml
pipeline:
  name: "Social Media Processing"
  description: "Process Pashto content from social platforms"

input:
  data_directory: "data/raw/social"
  supported_formats: ["json", "csv"]
  
  social_media:
    platforms: ["twitter", "facebook", "instagram"]
    
    # Twitter specific
    twitter:
      api_version: "2.0"
      max_tweets: 1000
      filter_lang: "und"  # Undetermined language
      
    # Facebook specific  
    facebook:
      access_token_required: true
      max_posts: 500
      
    # Instagram specific
    instagram:
      access_token_required: true
      max_posts: 500

processing:
  # Social media specific processing
  handle_hashtags: true
  handle_mentions: true
  handle_urls: true
  handle_emojis: true
  
  # Text cleaning for social media
  remove_duplicate_posts: true
  filter_min_length: 10
  filter_max_length: 280  # Twitter limit
  require_pashto: true
  min_pashto_ratio: 0.5  # Lower for social media
  
  # Remove noise
  remove_retweet_indicators: true
  remove_reply_indicators: true
  extract_original_content: true
  
  # Handle languages
  detect_code_switching: true
  extract_pashto_segments: true

output:
  data_directory: "data/processed/social"
  format: "json"
  include_metadata: true
  include_platform: true
  include_engagement_metrics: true
  
  metadata_fields:
    - "post_id"
    - "platform"
    - "author"
    - "timestamp"
    - "likes"
    - "shares"
    - "comments"
    - "hashtags"
    - "mentions"
    - "urls"

quality:
  min_quality_score: 0.5  # Lower for social media
  platform_aware_scoring: true
  engagement_weighted_quality: true
```

#### Step 2: Process Social Media Data
```bash
# Process collected social media data
pashto-pipeline process \
  --input data/raw/social/ \
  --output data/processed/social/ \
  --config config/social_media.yaml \
  --filter-platform twitter \
  --min-engagement 10

# Generate social media report
pashto-pipeline social-report \
  --input data/processed/social/ \
  --output reports/social_analysis.html
```

## 📄 PDF Document Processing

### Tutorial 4: Extract Text from Pashto PDFs

Handle PDF documents with OCR and text extraction for scanned documents.

#### Step 1: PDF Processing Configuration
```yaml
# config/pdf_processing.yaml
input:
  data_directory: "data/raw/pdf"
  supported_formats: ["pdf"]
  
  pdf:
    # Text extraction
    extract_text: true
    extract_text_method: "pdfplumber"  # pdfplumber, pymupdf, pypdf
    
    # OCR settings (for scanned documents)
    ocr_enabled: true
    ocr_language: "pus"  # Pashto
    ocr_engine: "tesseract"  # tesseract, easyocr
    
    # OCR preprocessing
    preprocess_images: true
    denoise: true
    deskew: true
    enhance_contrast: true
    
    # Page handling
    extract_pages: "all"  # all, 1-10, odd, even
    skip_empty_pages: true
    min_text_per_page: 50
    
    # Metadata extraction
    extract_metadata: true
    include_page_numbers: true

processing:
  # PDF specific processing
  normalize_pdf_text: true
  fix_line_breaks: true
  merge_broken_words: true
  remove_header_footer: true
  
  # Quality filtering
  filter_min_length: 100
  require_pashto: true
  min_pashto_ratio: 0.6
  min_ocr_confidence: 60

output:
  data_directory: "data/processed/pdf"
  format: "json"
  include_metadata: true
  include_ocr_confidence: true
  include_page_structure: true
```

#### Step 2: Install PDF Dependencies
```bash
# Install PDF processing dependencies
pip install pdfplumber PyMuPDF pytesseract pillow

# Install Tesseract OCR
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocrpus

# macOS:
brew install tesseract tesseract-lang

# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

#### Step 3: Process PDFs
```bash
# Process PDFs with OCR
pashto-pipeline process \
  --input data/raw/pdf/ \
  --output data/processed/pdf/ \
  --config config/pdf_processing.yaml \
  --enable-ocr \
  --ocr-language pus

# Process specific pages
pashto-pipeline process \
  --input data/raw/pdf/document.pdf \
  --output data/processed/pdf/ \
  --pages 1-50 \
  --config config/pdf_processing.yaml

# Batch process with progress
pashto-pipeline batch-process \
  --input-dirs data/raw/pdf/ \
  --output-dir data/processed/pdf/ \
  --config config/pdf_processing.yaml \
  --progress
```

## 🗄️ Database Integration

### Tutorial 5: Work with Database Sources

Connect to SQL and NoSQL databases for large-scale data processing.

#### Step 1: Database Configuration
```yaml
# config/database.yaml
input:
  type: "database"
  
  database:
    # PostgreSQL example
    connection_url: "postgresql://user:password@localhost:5432/pashto_db"
    
    # Query configuration
    query: |
      SELECT 
        text_content,
        source_id,
        created_at,
        metadata
      FROM pashto_texts 
      WHERE language = 'ps' 
        AND created_at >= '2023-01-01'
        AND quality_score > 0.6
      ORDER BY created_at DESC
    
    # Connection settings
    batch_size: 1000
    max_rows: 50000
    timeout: 300
    
    # Alternative: MongoDB
    # mongodb:
    #   connection_url: "mongodb://localhost:27017/"
    #   database: "pashto_db"
    #   collection: "texts"
    #   query: {"language": "ps", "created_at": {"$gte": "2023-01-01"}}

processing:
  # Database specific processing
  handle_large_texts: true
  batch_processing: true
  memory_efficient: true
  
  # Quality validation
  validate_database_integrity: true
  check_text_encoding: true
  verify_language_consistency: true

output:
  type: "database"
  database:
    connection_url: "postgresql://user:password@localhost:5432/pashto_processed"
    table_name: "processed_pashto_texts"
    if_exists: "append"  # replace, append, fail
    
    schema:
      text_content: "TEXT NOT NULL"
      original_id: "VARCHAR(255)"
      source_table: "VARCHAR(100)"
      quality_score: "FLOAT"
      processing_date: "TIMESTAMP"
      metadata: "JSONB"
      indexes: ["original_id", "quality_score", "processing_date"]
```

#### Step 2: Database Operations
```bash
# Export from database to files
pashto-pipeline extract \
  --config config/database.yaml \
  --output data/extracted/ \
  --format json

# Process and store in database
pashto-pipeline process \
  --config config/database.yaml \
  --input-query "SELECT * FROM raw_pashto_texts WHERE processed = false"

# Sync database with processed files
pashto-pipeline sync-database \
  --source config/database.yaml \
  --target data/processed/
```

## 🔄 Batch Processing Large Datasets

### Tutorial 6: Handle Millions of Records

Scale the pipeline for enterprise-level datasets.

#### Step 1: High-Performance Configuration
```yaml
# config/batch_processing.yaml
advanced:
  # Performance settings
  max_workers: 16
  use_multiprocessing: true
  process_pool_size: 8
  
  # Memory management
  memory_limit: "32GB"
  garbage_collect_frequency: 1000
  streaming_mode: true
  
  # Caching
  enable_caching: true
  cache_directory: "cache"
  cache_ttl: 7200
  cache_size_limit: "10GB"

processing:
  # Batch processing
  batch_size: 1000
  chunk_size: 10000
  streaming_chunk_size: 5000
  
  # Optimization
  parallel_file_processing: true
  memory_mapped_io: true
  async_io: true
  
  # Quality at scale
  sample_quality_check: true
  quality_sample_rate: 0.1  # Check 10% of data
  approximate_quality_scoring: true

output:
  # Efficient output
  compress_output: true
  compression_format: "gzip"
  streaming_output: true
  
  # Sharding
  shard_output: true
  shard_size: 10000
  shard_by: "source"  # source, date, quality
  
  # Database output for scale
  database_batch_insert: true
  database_batch_size: 5000
```

#### Step 2: Batch Processing Commands
```bash
# Process large directory with progress
pashto-pipeline process \
  --input data/large_dataset/ \
  --output data/processed_large/ \
  --config config/batch_processing.yaml \
  --progress \
  --workers 16

# Resume interrupted processing
pashto-pipeline process \
  --input data/large_dataset/ \
  --output data/processed_large/ \
  --config config/batch_processing.yaml \
  --resume \
  --checkpoint-interval 1000

# Parallel directory processing
pashto-pipeline parallel-process \
  --input-dirs data/dir1/,data/dir2/,data/dir3/ \
  --output-dir data/combined/ \
  --config config/batch_processing.yaml \
  --merge-results

# Monitor processing
pashto-pipeline monitor \
  --input data/large_dataset/ \
  --output data/processed_large/ \
  --config config/batch_processing.yaml \
  --dashboard
```

## 🎯 Custom Quality Filters

### Tutorial 7: Implement Domain-Specific Quality Rules

Create custom quality assessment for specific domains like news, academic, or conversational text.

#### Step 1: Custom Quality Configuration
```yaml
# config/custom_quality.yaml
quality:
  # Domain-specific scoring
  domain: "academic"  # academic, news, conversational, general
  
  # Academic text specific
  academic:
    min_academic_terms: 3
    max_informal_language: 0.2
    min_sentence_complexity: 0.6
    max_repetition: 0.15
    
    # Academic vocabulary
    academic_keywords:
      - "څیړنه"  # research
      - "تحلیل"  # analysis
      - "نتیجه"  # result
      - "مطالعه"  # study
      - "تیوري"  # theory
      - "روش"  # method
      - "نظریه"  # theory
      - "وړاندې"  # propose
      - "دروون"  # results
      - "پایلې"  # conclusions
  
  # News text specific
  news:
    min_news_terms: 2
    max_casual_language: 0.3
    require_recent_references: true
    max_opinion_ratio: 0.4
    
    # News vocabulary
    news_keywords:
      - "خبر"  # news
      - "راپور"  # report
      - "اعلان"  # announcement
      - "وړاندې"  # reported
      - "دولت"  # government
      - "سیاست"  # policy
      - "اقتصاد"  # economy
      - "ټولنه"  # society

  # Conversational text specific
  conversational:
    max_formal_language: 0.2
    min_conversational_indicators: 1
    max_question_ratio: 0.6
    
    # Conversational indicators
    conversational_markers:
      - "?"  # questions
      - "!"  # exclamations
      - "زه"  # I
      - "تاسو"  # you
      - "موږ"  # we
      - "زموږ"  # our
```

#### Step 2: Custom Quality Rules
```python
# scripts/custom_quality.py
from pashto_pipeline.quality import BaseQualityChecker
from pashto_pipeline.text import PashtoText

class AcademicQualityChecker(BaseQualityChecker):
    """Custom quality checker for academic Pashto text"""
    
    def __init__(self, config):
        super().__init__(config)
        self.academic_keywords = config.get('academic_keywords', [])
        self.min_academic_terms = config.get('min_academic_terms', 3)
        self.max_informal_ratio = config.get('max_informal_language', 0.2)
    
    def check_quality(self, text):
        """Check quality of academic text"""
        score = 0.0
        issues = []
        
        # Check for academic terminology
        academic_term_count = 0
        for keyword in self.academic_terms:
            if keyword in text:
                academic_term_count += 1
        
        if academic_term_count >= self.min_academic_terms:
            score += 0.4
        else:
            issues.append(f"Insufficient academic terms: {academic_term_count}")
        
        # Check formality ratio
        formal_score = self._check_formality(text)
        if formal_score >= 0.8:
            score += 0.3
        else:
            issues.append("Text too informal for academic context")
        
        # Check sentence complexity
        complexity_score = self._check_complexity(text)
        if complexity_score >= 0.6:
            score += 0.3
        else:
            issues.append("Sentences too simple for academic context")
        
        return {
            'score': min(score, 1.0),
            'issues': issues,
            'academic_term_count': academic_term_count,
            'formality_score': formal_score,
            'complexity_score': complexity_score
        }
    
    def _check_formality(self, text):
        """Assess formality of text"""
        informal_indicators = [
            "زه", "ته", "زموږ", "ښه", "ډېر", "ډېره"
        ]
        
        informal_count = sum(1 for indicator in informal_indicators if indicator in text)
        total_indicators = len([word for word in text.split() if word in informal_indicators + self.academic_keywords])
        
        if total_indicators == 0:
            return 0.5
        
        informal_ratio = informal_count / total_indicators
        return 1.0 - min(informal_ratio / self.max_informal_ratio, 1.0)
    
    def _check_complexity(self, text):
        """Assess sentence complexity"""
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Academic text typically has longer sentences
        if avg_sentence_length >= 15:
            return 1.0
        elif avg_sentence_length >= 10:
            return 0.8
        elif avg_sentence_length >= 7:
            return 0.6
        else:
            return 0.3
```

#### Step 3: Use Custom Quality Checker
```bash
# Use custom quality configuration
pashto-pipeline process \
  --input data/academic/ \
  --output data/processed/ \
  --config config/custom_quality.yaml \
  --quality-checker academic

# Generate quality report
pashto-pipeline quality-report \
  --input data/processed/ \
  --output reports/academic_quality.html \
  --config config/custom_quality.yaml
```

## ⚡ Real-time Processing

### Tutorial 8: Process Streaming Data

Handle real-time data streams and continuous processing.

#### Step 1: Stream Configuration
```yaml
# config/streaming.yaml
pipeline:
  mode: "streaming"  # batch, streaming, real-time

streaming:
  # Input streams
  sources:
    - type: "websocket"
      url: "wss://example.com/pashto-stream"
      buffer_size: 1000
    
    - type: "kafka"
      topic: "pashto-text-stream"
      brokers: ["localhost:9092"]
      group_id: "pashto-processor"
    
    - type: "redis"
      channel: "pashto_messages"
      host: "localhost"
      port: 6379
  
  # Processing settings
  buffer_size: 500
  flush_interval: 10  # seconds
  max_latency: 5  # seconds
  
  # Output streams
  output_streams:
    - type: "elasticsearch"
      index: "pashto_processed"
      hosts: ["localhost:9200"]
    
    - type: "mongodb"
      collection: "processed_pashto"
      connection_string: "mongodb://localhost:27017/"

processing:
  # Real-time processing
  real_time: true
  fast_mode: true
  skip_expensive_operations: true
  cache_decisions: true
  
  # Simplified quality scoring
  quick_quality_check: true
  quality_sample_rate: 1.0
  approximate_scoring: true

output:
  # Streaming output
  stream_output: true
  buffer_flush_size: 100
  flush_on_timeout: true
  
  # Persistence
  persist_state: true
  state_file: "streaming_state.json"
```

#### Step 2: Start Real-time Processing
```bash
# Start streaming processor
pashto-pipeline stream \
  --config config/streaming.yaml \
  --source websocket \
  --output elasticsearch

# Start Kafka consumer
pashto-pipeline stream \
  --config config/streaming.yaml \
  --source kafka \
  --kafka-topic pashto-text-stream

# Monitor streaming processor
pashto-pipeline stream-status \
  --pid-file streaming.pid \
  --metrics
```

## 🌍 Multi-language Support

### Tutorial 9: Process Multi-language Data

Handle datasets containing multiple languages and code-switching.

#### Step 1: Multi-language Configuration
```yaml
# config/multilingual.yaml
processing:
  # Language detection
  detect_languages: true
  supported_languages: ["pashto", "dari", "english", "urdu", "persian"]
  min_language_confidence: 0.7
  
  # Code-switching handling
  handle_code_switching: true
  extract_pashto_segments: true
  max_non_pashto_ratio: 0.3
  
  # Language-specific processing
  language_rules:
    pashto:
      normalize_arabic_script: true
      apply_pashto_specific_rules: true
    
    dari:
      normalize_persian_arabic: true
      similar_to_pashto: true
    
    english:
      remove_english_content: false
      keep_english_terms: true
    
    urdu:
      handle_urdu_similarities: true

quality:
  # Multi-language quality assessment
  multilingual_quality: true
  language_aware_scoring: true
  
  # Quality by language
  quality_by_language:
    pashto:
      min_score: 0.6
      weight: 1.0
    
    dari:
      min_score: 0.5
      weight: 0.8
      similar_to_pashto: true
    
    english:
      min_score: 0.4
      weight: 0.3
      keep_only_relevant: true

output:
  # Language-tagged output
  include_language_tags: true
  separate_by_language: true
  language_statistics: true
  
  # Language-specific files
  language_files:
    pashto: "pashto_processed.json"
    dari: "dari_processed.json"
    mixed: "mixed_language_processed.json"
```

#### Step 2: Multi-language Processing
```bash
# Process multilingual dataset
pashto-pipeline process \
  --input data/multilingual/ \
  --output data/processed/ \
  --config config/multilingual.yaml \
  --language-detection

# Generate language distribution report
pashto-pipeline language-stats \
  --input data/processed/ \
  --output reports/language_distribution.html

# Extract pure Pashto content
pashto-pipeline filter \
  --input data/processed/ \
  --output data/pure_pashto/ \
  --language pashto \
  --min-confidence 0.8
```

## ⚡ Performance Optimization

### Tutorial 10: Optimize for Maximum Performance

Learn advanced optimization techniques for different hardware configurations.

#### Step 1: Hardware-Specific Configurations

**High-Memory Server (64GB+)**
```yaml
# config/high_memory.yaml
advanced:
  max_workers: 32
  process_pool_size: 16
  memory_limit: "64GB"
  batch_size: 10000
  cache_size_limit: "20GB"
  
  # Parallel processing
  parallel_file_processing: true
  parallel_text_processing: true
  use_multiprocessing: true
  
  # I/O optimization
  async_io: true
  io_buffer_size: "64MB"
  memory_mapped_io: true
  
  # Caching
  enable_caching: true
  cache_everything: true
  cache_ttl: 86400  # 24 hours
```

**GPU-Accelerated (NVIDIA CUDA)**
```yaml
# config/gpu_accelerated.yaml
advanced:
  enable_gpu: true
  gpu_device: 0
  max_workers: 8
  batch_size: 5000
  
  # GPU-specific processing
  gpu_quality_scoring: true
  gpu_language_detection: true
  gpu_semantic_analysis: true
  
  # Mixed precision
  mixed_precision: true
  gpu_memory_fraction: 0.8

ml:
  models:
    quality_assessment:
      model_type: "gpu_transformer"
      model_name: "pashto-quality-gpu-v1"
    
    language_detection:
      model_type: "gpu_classifier"
      model_name: "fasttext-gpu"
    
    semantic_similarity:
      model_type: "gpu_embeddings"
      model_name: "pashto-bert-gpu"
```

**Low-Memory System (4GB)**
```yaml
# config/low_memory.yaml
advanced:
  max_workers: 2
  process_pool_size: 1
  memory_limit: "3GB"
  batch_size: 100
  stream_processing: true
  
  # Memory optimization
  disable_caching: true
  aggressive_gc: true
  gc_frequency: 10
  memory_mapped_io: false
  
  # Simplified processing
  skip_expensive_operations: true
  approximate_scoring: true
  fast_quality_check: true
```

#### Step 2: Performance Monitoring
```bash
# Monitor resource usage during processing
pashto-pipeline process \
  --input data/large/ \
  --output data/processed/ \
  --config config/high_memory.yaml \
  --monitor-resources \
  --profile

# Generate performance report
pashto-pipeline performance-report \
  --log-file logs/pipeline.log \
  --output reports/performance.html \
  --include-memory-usage \
  --include-cpu-usage

# Benchmark processing speed
pashto-pipeline benchmark \
  --input data/sample/ \
  --config config/benchmark_config.yaml \
  --iterations 3 \
  --report
```

#### Step 3: Optimization Tips

**Memory Optimization**
```python
# Use generators for large files
def process_large_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            yield process_line(line)

# Process in chunks
for chunk in read_file_chunks('large_file.txt', chunk_size=1000):
    process_chunk(chunk)
    gc.collect()  # Force garbage collection
```

**I/O Optimization**
```bash
# Use faster storage
# Mount data directories on SSD
mount -t tmpfs -o size=10G tmpfs /fast_cache

# Disable swap for better performance
swapoff -a

# Optimize file system
echo noatime > /proc/sys/fs/file-nr
```

**Network Optimization**
```bash
# Increase network buffer sizes
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728

# Optimize TCP settings
sysctl -w net.ipv4.tcp_window_scaling=1
sysctl -w net.ipv4.tcp_congestion_control=bbr
```

## 📚 Summary

You now have comprehensive knowledge of:

- ✅ Basic text processing workflows
- ✅ Web scraping and data collection
- ✅ Social media data processing
- ✅ PDF document handling
- ✅ Database integration
- ✅ Large-scale batch processing
- ✅ Custom quality assessment
- ✅ Real-time streaming
- ✅ Multi-language support
- ✅ Performance optimization

## 🚀 Next Steps

- [Best Practices Guide](best_practices.md) - Professional guidelines
- [API Reference](../api/README.md) - Complete API documentation
- [Troubleshooting](../troubleshooting/common_issues.md) - Solve common issues
- [Examples](../examples/) - More code examples and scripts