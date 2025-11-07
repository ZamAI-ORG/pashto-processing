# Configuration Guide

Complete guide to configuring the Pashto Dataset Pipeline. Learn how to customize every aspect of the pipeline to meet your specific needs.

## 📋 Table of Contents

- [Configuration Overview](#configuration-overview)
- [Basic Configuration](#basic-configuration)
- [Input Configuration](#input-configuration)
- [Processing Configuration](#processing-configuration)
- [Output Configuration](#output-configuration)
- [Quality Settings](#quality-settings)
- [Logging Configuration](#logging-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Configuration Validation](#configuration-validation)
- [Environment Variables](#environment-variables)

## 🔧 Configuration Overview

The Pashto Dataset Pipeline uses YAML configuration files to control all aspects of operation. Configuration can be provided through:

1. **Configuration Files**: YAML files (`.yaml` or `.yml`)
2. **Environment Variables**: System environment settings
3. **Command Line Arguments**: Override specific options
4. **Python API**: Programmatic configuration

### Configuration File Structure

```yaml
# Top-level sections
pipeline:
  # Pipeline metadata and behavior

input:
  # Input data source configuration

processing:
  # Text processing and cleaning options

output:
  # Output format and destination settings

quality:
  # Quality assessment and filtering

logging:
  # Logging and monitoring settings

advanced:
  # Advanced and expert options
```

## 🏗️ Basic Configuration

Here's a complete basic configuration file:

**config/basic_config.yaml**
```yaml
# Basic Pipeline Configuration
pipeline:
  name: "My Pashto Dataset Pipeline"
  version: "1.0"
  description: "Custom Pashto text processing pipeline"
  author: "Your Name"
  created: "2025-11-06"
  
  # Pipeline behavior
  stop_on_error: false
  continue_on_warning: true
  max_retries: 3

# Input Configuration
input:
  # Data source
  data_directory: "data/raw"
  recursive: true
  max_files: 1000
  
  # Supported formats
  supported_formats: ["txt", "json", "csv", "xml"]
  
  # File handling
  encoding: "utf-8"
  encoding_fallback: ["utf-8", "cp1256", "iso-8859-1"]
  skip_empty_files: true
  min_file_size: 10  # bytes
  
  # Text extraction
  extract_text_from_pdf: false
  extract_text_from_html: false
  handle_zip_files: false

# Processing Configuration
processing:
  # Text normalization
  normalize_text: true
  normalization_form: "NFC"  # NFC, NFD, NFKC, NFKD
  remove_bom: true
  convert_arabic_digits: true
  
  # Character handling
  remove_control_chars: true
  remove_punctuation: false
  remove_numbers: false
  remove_urls: true
  remove_emails: true
  
  # Text filtering
  filter_min_length: 5
  filter_max_length: 10000
  require_min_words: 2
  require_max_words: 1000
  
  # Language filtering
  require_pashto: true
  min_pashto_ratio: 0.7
  detect_other_languages: ["english", "dari", "urdu", "persian"]
  
  # Deduplication
  remove_duplicates: true
  duplicate_sensitivity: "fuzzy"  # exact, fuzzy, semantic
  fuzzy_threshold: 0.85
  
  # Noise removal
  remove_spam_patterns: true
  remove_repetitive_text: true
  max_repetition_ratio: 0.3

# Output Configuration
output:
  # Output destination
  data_directory: "data/processed"
  create_subdirs: true
  
  # Format settings
  format: "json"  # json, csv, xml, parquet, sql
  include_metadata: true
  include_statistics: true
  pretty_print: false
  
  # Compression
  compress_output: false
  compression_format: "gzip"  # gzip, bzip2, zip
  
  # File naming
  filename_pattern: "{date}_{source}_{type}.{ext}"
  include_timestamp: true
  include_source_in_filename: true
  
  # Database output (if using SQL)
  database_url: null
  table_name: "pashto_dataset"

# Quality Configuration
quality:
  # Quality scoring
  min_quality_score: 0.6
  enable_quality_scoring: true
  
  # Content quality
  min_grammar_score: 0.5
  min_coherence_score: 0.4
  min_relevance_score: 0.6
  
  # Technical quality
  max_typo_ratio: 0.1
  max_encoding_errors: 0.05
  max_formatting_issues: 0.2
  
  # Language quality
  require_proper_casing: true
  require_proper_spacing: true
  check_spellings: false

# Logging Configuration
logging:
  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: "INFO"
  console: true
  file: "logs/pipeline.log"
  max_file_size: "100MB"
  backup_count: 5
  
  # Log format
  format: "[{timestamp}] {level:8} {name:20} {message}"
  date_format: "%Y-%m-%d %H:%M:%S"
  
  # Filtering
  log_filtered_items: false
  log_quality_scores: true
  log_processing_stats: true

# Advanced Configuration
advanced:
  # Performance
  max_workers: 4
  batch_size: 100
  memory_limit: "4GB"
  
  # Caching
  enable_caching: true
  cache_directory: "cache"
  cache_ttl: 3600  # seconds
  
  # Validation
  strict_validation: false
  validate_input_integrity: true
  
  # Experimental features
  enable_gpu: false
  enable_ml_features: false
```

## 📂 Input Configuration

Configure how the pipeline reads and processes input data.

### Basic Input Settings

```yaml
input:
  # Source directory or file
  data_directory: "data/raw"
  recursive: true  # Include subdirectories
  max_files: 1000  # Limit number of files
  
  # File formats
  supported_formats: 
    - "txt"    # Plain text
    - "json"   # JSON files
    - "csv"    # CSV files
    - "xml"    # XML files
    - "pdf"    # PDF documents (if enabled)
    - "html"   # HTML files (if enabled)
  
  # Encoding
  encoding: "utf-8"
  encoding_fallback: 
    - "utf-8"
    - "cp1256"  # Windows Arabic
    - "iso-8859-1"  # Latin-1
    - "utf-16"  # Unicode
  
  # File filtering
  skip_empty_files: true
  min_file_size: 10  # bytes
  max_file_size: "100MB"
  
  # Name patterns
  include_patterns: ["*.txt", "*.json"]
  exclude_patterns: ["*~", "*.bak", ".git/*"]
```

### Web Scraping Configuration

```yaml
input:
  type: "web_scraping"
  
  scraping:
    urls:
      - "https://example.com/pashto"
      - "https://news.af/pashto"
    
    selectors:
      article_content: "article p"
      title: "h1"
      metadata: ".meta"
    
    rate_limiting:
      requests_per_second: 1
      delay_between_requests: 1.0
      timeout: 30
    
    browser:
      user_agent: "Mozilla/5.0 (compatible; PashtoBot/1.0)"
      headless: true
      window_size: [1920, 1080]
```

### Database Input

```yaml
input:
  type: "database"
  
  database:
    connection_url: "postgresql://user:pass@localhost/db"
    query: "SELECT text, metadata FROM pashto_texts WHERE language = 'ps'"
    batch_size: 1000
    max_rows: 10000
```

## ⚙️ Processing Configuration

Control text processing and cleaning operations.

### Text Normalization

```yaml
processing:
  # Unicode normalization
  normalize_text: true
  normalization_form: "NFC"  # NFC, NFD, NFKC, NFKD
  remove_bom: true
  
  # Character conversions
  convert_arabic_digits: true
  convert_persian_digits: true
  unify_arabic_letters: true
  
  # Character filtering
  remove_control_chars: true
  remove_zero_width: true
  remove_bidirectional_markers: false
```

### Text Cleaning

```yaml
processing:
  # Content removal
  remove_urls: true
  remove_emails: true
  remove_phone_numbers: true
  remove_addresses: false
  
  # Punctuation
  remove_punctuation: false
  keep_sentence_endings: true
  keep_quotes: true
  
  # Spacing
  normalize_spaces: true
  remove_extra_blank_lines: true
  fix_arabic_spacing: true
```

### Length and Content Filtering

```yaml
processing:
  # Length constraints
  filter_min_length: 10   # minimum characters
  filter_max_length: 5000 # maximum characters
  require_min_words: 2
  require_max_words: 500
  
  # Content requirements
  require_pashto: true
  min_pashto_ratio: 0.7
  require_sentences: true
  min_sentences: 1
  max_sentences: 50
```

### Deduplication

```yaml
processing:
  # Duplicate removal
  remove_duplicates: true
  duplicate_strategy: "fuzzy"  # exact, fuzzy, semantic
  
  # Exact duplicates
  case_sensitive: false
  ignore_whitespace: true
  
  # Fuzzy duplicates
  fuzzy_threshold: 0.85
  fuzzy_algorithm: "levenshtein"  # levenshtein, jaro_winkler
  max_fuzzy_distance: 3
  
  # Semantic duplicates (requires ML)
  semantic_similarity: false
  embedding_model: "pashto-bert-base"
```

## 📤 Output Configuration

Configure how processed data is saved.

### Basic Output

```yaml
output:
  # Destination
  data_directory: "data/processed"
  create_subdirs: true
  
  # Format
  format: "json"  # json, csv, xml, parquet, sql
  include_metadata: true
  include_statistics: true
  pretty_print: false
```

### JSON Output Format

```yaml
output:
  format: "json"
  json_options:
    indent: 2
    ensure_ascii: true
    sort_keys: false
    include_pipeline_info: true
    include_quality_metrics: true
    include_processing_time: true
```

### CSV Output Format

```yaml
output:
  format: "csv"
  csv_options:
    delimiter: ","
    quotechar: '"'
    include_header: true
    encoding: "utf-8"
    columns:
      - "text"
      - "source_file"
      - "quality_score"
      - "word_count"
      - "char_count"
```

### Database Output

```yaml
output:
  format: "sql"
  sql_options:
    connection_url: "postgresql://user:pass@localhost/db"
    table_name: "pashto_dataset"
    if_exists: "replace"  # replace, append, fail
    batch_size: 1000
    
    schema:
      text: "TEXT NOT NULL"
      quality_score: "FLOAT"
      source_file: "VARCHAR(255)"
      processed_at: "TIMESTAMP"
      metadata: "JSONB"
```

## 🎯 Quality Settings

Configure quality assessment and filtering.

### Quality Scoring

```yaml
quality:
  # Enable quality assessment
  enable_quality_scoring: true
  min_quality_score: 0.6
  
  # Individual quality metrics
  metrics:
    grammar:
      enabled: true
      weight: 0.3
      min_score: 0.5
    
    coherence:
      enabled: true
      weight: 0.3
      min_score: 0.4
    
    relevance:
      enabled: true
      weight: 0.2
      min_score: 0.6
    
    technical:
      enabled: true
      weight: 0.2
      max_typo_ratio: 0.1
      max_encoding_errors: 0.05
```

### Language Quality

```yaml
quality:
  # Pashto language detection
  require_pashto: true
  min_pashto_ratio: 0.7
  detect_other_languages: ["english", "dari", "urdu", "persian"]
  
  # Text structure
  require_proper_casing: true
  require_proper_spacing: true
  require_sentence_structure: true
  
  # Content quality
  check_spellings: false
  grammar_check: false
  spell_check: false
```

## 📝 Logging Configuration

Configure logging and monitoring.

```yaml
logging:
  # Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: "INFO"
  console: true
  file: "logs/pipeline.log"
  
  # File rotation
  max_file_size: "100MB"
  backup_count: 5
  
  # Format
  format: "[{timestamp}] {level:8} {name:20} {message}"
  date_format: "%Y-%m-%d %H:%M:%S"
  
  # Filtering
  log_filtered_items: false
  log_quality_scores: true
  log_processing_stats: true
  
  # Custom loggers
  loggers:
    pashto_pipeline.processors:
      level: "DEBUG"
    pashto_pipeline.quality:
      level: "INFO"
```

## ⚡ Advanced Configuration

Advanced settings for performance and specialized use cases.

### Performance Tuning

```yaml
advanced:
  # Parallel processing
  max_workers: 4
  use_multiprocessing: true
  process_pool_size: 2
  
  # Memory management
  memory_limit: "4GB"
  garbage_collect_frequency: 100  # items
  cache_intermediate_results: true
  
  # Batch processing
  batch_size: 100
  streaming_mode: false
  
  # I/O optimization
  use_memory_mapping: true
  async_io: true
  io_buffer_size: "8MB"
```

### Caching

```yaml
advanced:
  # Enable caching
  enable_caching: true
  cache_directory: "cache"
  cache_ttl: 3600  # seconds
  
  # Cache levels
  cache_levels:
    raw_data: true
    processed_data: true
    quality_scores: true
    language_detection: true
```

### ML and AI Features

```yaml
advanced:
  # Machine learning
  enable_ml_features: false
  use_gpu: false
  embedding_model: "pashto-bert-base"
  
  # Models
  language_detection_model: "fasttext-langdetect"
  quality_assessment_model: "pashto-quality-v1"
  spell_check_model: "hunspell-ps"
  
  # Training
  auto_retrain: false
  model_update_frequency: "weekly"
```

### Experimental Features

```yaml
advanced:
  # Experimental settings
  experimental_features: false
  
  # Feature flags
  enable_semantic_deduplication: false
  enable_grammar_checking: false
  enable_style_analysis: false
  enable_sentiment_analysis: false
```

## 🔍 Configuration Validation

### Validate Configuration File

```bash
# Validate configuration
pashto-pipeline validate-config --file config/my_config.yaml

# Validate and show resolved configuration
pashto-pipeline validate-config --file config/my_config.yaml --resolve
```

### Configuration Schema

The configuration follows this schema:

```python
ConfigSchema = {
    "pipeline": {
        "name": str,
        "version": str,
        "description": str,
        "stop_on_error": bool,
        "continue_on_warning": bool,
        "max_retries": int
    },
    "input": {
        "data_directory": str,
        "recursive": bool,
        "supported_formats": [str],
        "encoding": str,
        "max_files": int
    },
    "processing": {
        "normalize_text": bool,
        "remove_duplicates": bool,
        "filter_min_length": int,
        "require_pashto": bool,
        "min_pashto_ratio": float
    },
    # ... more sections
}
```

## 🌐 Environment Variables

Override configuration with environment variables:

```bash
# Pipeline settings
export PASHTOPIPELINE_PIPELINE_NAME="My Pipeline"
export PASHTOPIPELINE_MAX_WORKERS="8"
export PASHTOPIPELINE_LOG_LEVEL="DEBUG"

# Input settings
export PASHTOPIPELINE_INPUT_DIR="data/custom_input"
export PASHTOPIPELINE_ENCODING="utf-8"

# Processing settings
export PASHTOPIPELINE_MIN_LENGTH="15"
export PASHTOPIPELINE_REMOVE_DUPLICATES="true"
export PASHTOPIPELINE_MIN_PASHTO_RATIO="0.8"

# Output settings
export PASHTOPIPELINE_OUTPUT_DIR="data/custom_output"
export PASHTOPIPELINE_FORMAT="csv"

# Quality settings
export PASHTOPIPELINE_MIN_QUALITY="0.7"
export PASHTOPIPELINE_ENABLE_SCORING="true"
```

## 📋 Configuration Examples

### Minimal Configuration
```yaml
input:
  data_directory: "data/raw"

processing:
  filter_min_length: 10
  require_pashto: true

output:
  data_directory: "data/processed"
  format: "json"
```

### Web Scraping Configuration
```yaml
input:
  type: "web_scraping"
  scraping:
    urls:
      - "https://example.com/pashto-articles"
    
    rate_limiting:
      requests_per_second: 0.5
      delay_between_requests: 2.0

processing:
  filter_min_length: 100
  require_pashto: true
  min_pashto_ratio: 0.9

quality:
  min_quality_score: 0.8
```

### Batch Processing Configuration
```yaml
advanced:
  max_workers: 8
  batch_size: 500
  memory_limit: "8GB"

processing:
  remove_duplicates: true
  duplicate_strategy: "fuzzy"
  fuzzy_threshold: 0.9

output:
  compress_output: true
  compression_format: "gzip"
```

## 🔧 Configuration Best Practices

1. **Start Simple**: Begin with basic configuration and add complexity gradually
2. **Version Control**: Keep configuration files in version control
3. **Environment Specific**: Use different configs for dev, staging, production
4. **Documentation**: Comment your configuration files
5. **Validation**: Always validate configuration before use
6. **Backup**: Keep backups of working configurations
7. **Testing**: Test configurations with sample data first

## 📚 Next Steps

- [Usage Tutorials](usage_tutorials.md) - Learn common workflows
- [Best Practices](best_practices.md) - Professional guidelines
- [API Reference](../api/README.md) - Complete API documentation
- [Troubleshooting](../troubleshooting/common_issues.md) - Configuration issues