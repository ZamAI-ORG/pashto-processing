# Frequently Asked Questions (FAQ)

Common questions and answers about the Pashto Dataset Pipeline.

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [Processing and Usage](#processing-and-usage)
- [Quality and Language](#quality-and-language)
- [Performance and Optimization](#performance-and-optimization)
- [Data Formats and Output](#data-formats-and-output)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)
- [Development and Contributing](#development-and-contributing)

## ❓ General Questions

### What is the Pashto Dataset Pipeline?

The Pashto Dataset Pipeline is a comprehensive toolkit designed for processing, cleaning, and managing Pashto language datasets. It provides tools for:

- Text normalization and cleaning
- Language detection and quality assessment
- Web scraping and data collection
- Batch processing of large datasets
- Multiple output formats
- Configurable processing workflows

### Who should use this pipeline?

The pipeline is ideal for:

- **Researchers** working with Pashto text data
- **Developers** building Pashto NLP applications
- **Data scientists** processing multilingual datasets
- **Content creators** working with Pashto content
- **Organizations** handling Pashto language data at scale

### What makes this pipeline special for Pashto?

The pipeline is specifically designed for Pashto language characteristics:

- **Unicode support** for Pashto script variations
- **Language-specific normalization** rules
- **Pashto-aware quality assessment**
- **Dialect handling** for different Pashto variants
- **Cultural and linguistic context** awareness

### Is it free to use?

Yes, the Pashto Dataset Pipeline is open-source and free to use under the MIT License. You can use it for personal, commercial, and research purposes.

### What programming languages are supported?

- **Python 3.8+** (primary interface)
- **Command Line Interface** (CLI) for all platforms
- **Configuration files** in YAML format
- **API support** for integration with other tools

## 🛠️ Installation and Setup

### What are the minimum system requirements?

**Minimum Requirements:**
- Python 3.8 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection for installation

**Recommended Requirements:**
- Python 3.9+
- 8GB+ RAM
- SSD storage
- Multi-core CPU (4+ cores)

### Which operating systems are supported?

- **Linux** (Ubuntu 18.04+, CentOS 7+, Debian 9+)
- **macOS** (10.14+)
- **Windows** (10+)

### How do I install the pipeline?

```bash
# Using pip (recommended)
pip install pashto-dataset-pipeline

# Or for development
git clone https://github.com/your-org/pashto-dataset-pipeline.git
cd pashto-dataset-pipeline
pip install -e .
```

See the [Installation Guide](../guides/installation.md) for detailed instructions.

### Do I need to install additional dependencies?

Most dependencies are installed automatically. For specific features:

```bash
# For PDF processing
pip install pashto-dataset-pipeline[pdf]

# For web scraping
pip install pashto-dataset-pipeline[web]

# For machine learning features
pip install pashto-dataset-pipeline[ml]

# For all features
pip install pashto-dataset-pipeline[all]
```

### Can I use it without Python?

Yes, the pipeline provides a command-line interface that can be used without programming:

```bash
# Basic processing
pashto-pipeline process --input data/ --output processed/ --config config.yaml

# Quality assessment
pashto-pipeline quality-check --input processed/ --report

# Generate statistics
pashto-pipeline stats --input processed/ --detailed
```

## ⚙️ Configuration

### What configuration formats are supported?

- **YAML files** (.yaml, .yml) - Primary format
- **JSON files** (.json) - Alternative format
- **Environment variables** - For overriding settings
- **Python dictionaries** - For programmatic configuration

### How do I create a configuration file?

```bash
# Create default configuration
pashto-pipeline create-config --output my_config.yaml

# Or start with examples
cp examples/config/basic_config.yaml my_config.yaml
```

See the [Configuration Guide](../guides/configuration.md) for detailed options.

### Can I use different configurations for different environments?

Yes, you can create environment-specific configurations:

- `config/development.yaml`
- `config/staging.yaml`
- `config/production.yaml`

And use environment variables to override settings:

```bash
export PASHTOPIPELINE_MAX_WORKERS=8
export PASHTOPIPELINE_LOG_LEVEL=DEBUG
```

### What are the most important configuration options?

**Essential settings:**
```yaml
# Input/Output
input:
  data_directory: "data/raw"
output:
  data_directory: "data/processed"

# Processing
processing:
  require_pashto: true
  min_pashto_ratio: 0.7
  filter_min_length: 10

# Quality
quality:
  min_quality_score: 0.6

# Performance
advanced:
  max_workers: 4
  batch_size: 100
```

## 🔄 Processing and Usage

### What file formats are supported for input?

**Text Formats:**
- Plain text (.txt)
- JSON (.json)
- CSV (.csv)
- XML (.xml)
- Parquet (.parquet)

**Document Formats (with optional dependencies):**
- PDF documents (.pdf)
- HTML files (.html)

**Database Sources:**
- PostgreSQL
- MySQL
- MongoDB
- SQLite

### What are the supported output formats?

- **JSON** - Structured data with metadata
- **CSV** - Tabular format for spreadsheet applications
- **XML** - Structured markup format
- **Parquet** - Columnar format for analytics
- **SQL** - Direct database insertion

### How do I process a single file?

```python
from pashto_pipeline import Pipeline, Config

# Load configuration
config = Config.from_file('config.yaml')
pipeline = Pipeline(config)

# Process single file
result = pipeline.process_file('input.txt')
print(f"Processed: {result.text}")
```

### How do I process multiple files?

```python
# Process directory
result = pipeline.run('data/raw/', 'data/processed/')

# Process specific files
file_paths = ['file1.txt', 'file2.txt', 'file3.txt']
result = pipeline.process_batch(file_paths)
```

### Can I process data in real-time?

Yes, the pipeline supports streaming and real-time processing:

```yaml
# config/streaming.yaml
pipeline:
  mode: "streaming"

streaming:
  sources:
    - type: "websocket"
      url: "wss://example.com/pashto-stream"
    - type: "kafka"
      topic: "pashto-messages"
```

## 🎯 Quality and Language

### How does the quality assessment work?

The pipeline evaluates text quality across multiple dimensions:

1. **Basic Quality** - Length, completeness, structure
2. **Linguistic Quality** - Pashto language detection, script consistency
3. **Content Quality** - Grammar, coherence, relevance
4. **Technical Quality** - Encoding, formatting, noise

Quality scores range from 0.0 to 1.0, where 1.0 represents perfect quality.

### What language detection methods are used?

- **Unicode-based detection** for script analysis
- **Statistical models** for language classification
- **Pattern matching** for Pashto-specific features
- **ML models** for advanced language detection (optional)

### Can it handle mixed-language content?

Yes, the pipeline can:

- **Detect** multiple languages in text
- **Extract** Pashto segments from mixed content
- **Rate** language ratios
- **Filter** based on minimum Pashto content

```yaml
processing:
  require_pashto: true
  min_pashto_ratio: 0.7
  detect_other_languages: ["english", "dari", "urdu"]
```

### What about different Pashto dialects?

The pipeline handles:

- **Southern Pashto** (Afghan dialect)
- **Northern Pashto** (Pakistani dialect)
- **Western Pashto** variants
- **Transliterations** (Latin script)

Quality assessment is dialect-agnostic and focuses on linguistic validity.

## ⚡ Performance and Optimization

### How fast is the processing?

Processing speed depends on:

- **Text complexity**
- **System hardware**
- **Configuration settings**
- **Quality assessment depth**

Typical speeds:
- **Simple text**: 1,000-5,000 items/second
- **Complex processing**: 100-1,000 items/second
- **With quality assessment**: 50-500 items/second

### How can I improve processing speed?

**Configuration optimizations:**

```yaml
# Increase workers
advanced:
  max_workers: 8

# Reduce expensive operations
processing:
  remove_duplicates: false
  check_spellings: false

# Use faster formats
output:
  format: "csv"  # Faster than JSON
```

**Hardware optimizations:**
- Use SSD storage
- Increase RAM
- Use more CPU cores
- Enable SIMD instructions

### Can it handle very large datasets?

Yes, the pipeline supports:

- **Streaming processing** for datasets larger than RAM
- **Batch processing** with configurable batch sizes
- **Parallel processing** across multiple cores/machines
- **Sharding** for distributed processing

```yaml
advanced:
  streaming_mode: true
  batch_size: 10000
  max_workers: 16
```

### How much memory does it use?

Memory usage depends on configuration:

- **Basic processing**: 100-500MB
- **With caching**: 500MB-2GB
- **Large batch mode**: 1-8GB
- **Streaming mode**: 100-500MB (constant)

Control memory usage:

```yaml
advanced:
  memory_limit: "4GB"
  streaming_mode: true
  enable_caching: false
```

## 📁 Data Formats and Output

### What does the JSON output look like?

```json
{
  "pipeline_info": {
    "name": "Pashto Dataset Pipeline",
    "version": "1.0",
    "timestamp": "2025-11-06T21:41:41Z"
  },
  "statistics": {
    "total_processed": 100,
    "quality_score": 0.85
  },
  "data": [
    {
      "text": "زموږ ژبه ښه ده",
      "metadata": {
        "source_file": "input.txt",
        "quality_score": 0.92,
        "word_count": 4,
        "character_count": 11
      }
    }
  ]
}
```

### Can I customize the output format?

Yes, you can:

1. **Include/exclude metadata**
2. **Change field names**
3. **Add custom fields**
4. **Modify structure**

```yaml
output:
  include_metadata: true
  include_statistics: true
  custom_fields:
    - "custom_score"
    - "domain_classification"
```

### How do I export to different formats?

```bash
# CSV export
pashto-pipeline export --input processed/ --output exports/ --format csv

# XML export
pashto-pipeline export --input processed/ --output exports/ --format xml

# Database export
pashto-pipeline export --input processed/ --output database/ --format sql
```

### Can I save intermediate results?

Yes, enable intermediate caching:

```yaml
advanced:
  enable_caching: true
  cache_intermediate_results: true
  cache_ttl: 3600  # 1 hour
```

## 🛠️ Troubleshooting

### Why is processing so slow?

**Common causes and solutions:**

1. **Too many quality checks**
   ```yaml
   quality:
     enable_quality_scoring: false  # Disable for speed
   ```

2. **Insufficient workers**
   ```yaml
   advanced:
     max_workers: 8  # Increase worker count
   ```

3. **Slow storage**
   ```yaml
   advanced:
     use_memory_mapping: true  # Enable for SSD
   ```

4. **Large batch sizes**
   ```yaml
   advanced:
     batch_size: 50  # Reduce batch size
   ```

### Why am I getting memory errors?

**Solutions:**

1. **Enable streaming mode**
   ```yaml
   advanced:
     streaming_mode: true
   ```

2. **Reduce batch size**
   ```yaml
   advanced:
     batch_size: 25
   ```

3. **Disable caching**
   ```yaml
   advanced:
     enable_caching: false
   ```

4. **Use smaller chunks**
   ```yaml
   advanced:
     stream_chunk_size: 100
   ```

### Why are quality scores too low?

**Common reasons:**

1. **Mixed-language content**
   - Lower the Pashto ratio threshold
   - Enable code-switching handling

2. **Encoding issues**
   - Check input file encoding
   - Use encoding fallback

3. **Text quality**
   - Review source data quality
   - Adjust quality thresholds

### How do I debug configuration issues?

```bash
# Validate configuration
pashto-pipeline validate-config --file config.yaml

# Test with sample data
pashto-pipeline test-config --config config.yaml --sample-data data/sample/

# Run in debug mode
pashto-pipeline process --config config.yaml --log-level DEBUG
```

## 🚀 Advanced Features

### Can I create custom processors?

Yes, extend the base processor class:

```python
from pashto_pipeline.processors import BaseProcessor

class CustomProcessor(BaseProcessor):
    def process(self, data):
        # Your custom processing logic
        processed = self.custom_function(data)
        return processed

# Add to pipeline
pipeline.add_processor(CustomProcessor(config))
```

### Does it support machine learning models?

Yes, with optional ML dependencies:

```bash
pip install pashto-dataset-pipeline[ml]
```

Features include:
- Advanced language detection
- Semantic deduplication
- Quality assessment models
- Custom ML integrations

### Can I integrate with databases?

Yes, supports major databases:

```yaml
input:
  type: "database"
  database:
    connection_url: "postgresql://user:pass@localhost/db"
    query: "SELECT text FROM pashto_table"

output:
  type: "database"
  database:
    connection_url: "postgresql://user:pass@localhost/processed"
    table_name: "processed_pashto"
```

### Can I run it on a schedule?

Yes, use cron or task schedulers:

```bash
# Daily processing
0 2 * * * pashto-pipeline process --config /path/to/config.yaml

# Hourly with monitoring
0 * * * * pashto-pipeline process --config /path/to/config.yaml && pashto-pipeline health-check
```

### Does it provide a web API?

Yes, run as a service:

```bash
pashto-pipeline serve --port 8080 --host 0.0.0.0
```

API endpoints:
- `POST /process` - Process text
- `GET /health` - Health check
- `GET /stats` - Statistics

## 💻 Development and Contributing

### How can I contribute to the project?

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests
5. **Submit** a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

### How do I report bugs?

1. **Check** existing issues first
2. **Create** a new issue with:
   - System information
   - Configuration (redacted)
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior

### Can I extend the language support?

Yes, the pipeline is designed to be extensible:

- **Language processors** for other languages
- **Quality checkers** for specific domains
- **Exporters** for custom formats
- **Input sources** for new data types

### How do I run tests?

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/performance/   # Performance tests

# Run with coverage
pytest tests/ --cov=pashto_pipeline
```

### How do I build documentation?

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build documentation
cd docs/
make html

# Serve locally
python -m http.server 8000 -d _build/html/
```

## 📚 Additional Resources

### Where can I find more examples?

- [Examples Directory](../examples/) - Code examples and scripts
- [Usage Tutorials](../guides/usage_tutorials.md) - Step-by-step guides
- [Best Practices](../guides/best_practices.md) - Professional guidelines

### Where can I get help?

1. **Documentation** - This comprehensive guide
2. **GitHub Issues** - Bug reports and feature requests
3. **GitHub Discussions** - General questions and community support
4. **Stack Overflow** - Use tag `pashto-dataset-pipeline`

### Are there any tutorials or workshops?

- **Online Documentation** - This guide
- **Example Scripts** - In the examples directory
- **Video Tutorials** - Available on the project website
- **Workshop Materials** - For training sessions

### What's the roadmap?

Current development focus:

- **Enhanced ML models** for better quality assessment
- **Real-time processing** improvements
- **Distributed processing** capabilities
- **More export formats**
- **Performance optimizations**

## 📞 Contact and Support

### How do I contact the maintainers?

- **Email**: support@pashto-pipeline.org
- **GitHub**: https://github.com/your-org/pashto-dataset-pipeline
- **Website**: https://pashto-pipeline.org

### Can I request features?

Yes! We welcome feature requests:

1. **Check** existing issues
2. **Create** a new issue with:
   - Use case description
   - Expected behavior
   - Implementation ideas
   - Priority level

### Is commercial support available?

Yes, commercial support options:

- **Priority support** with guaranteed response times
- **Custom development** for specific requirements
- **Training and workshops** for teams
- **Consultation** for large-scale deployments

Contact: commercial@pashto-pipeline.org

---

**Still have questions?** Check the [Troubleshooting Guide](common_issues.md) or [create an issue](https://github.com/your-org/pashto-dataset-pipeline/issues).