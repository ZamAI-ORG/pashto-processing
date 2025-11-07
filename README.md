# Pashto Processing Pipeline 🇦🇫

[![Documentation Status](https://img.shields.io/badge/docs-latest-blue.svg)](https://github.com/tasal9/Pashto-Processing-pipeline)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, production-ready pipeline for processing, cleaning, and managing Pashto language datasets. This system combines advanced NLP techniques, web scraping, PDF processing, and dataset management capabilities specifically designed for the Pashto language.

## ✨ Features

### Core Capabilities
- **🔤 Text Processing**: Advanced Pashto text normalization, tokenization, and cleaning
- **🌐 Web Scraping**: Multi-source data collection from Pashto websites and news sources
- **📄 PDF Processing**: Extract and process text from Pashto PDF documents
- **🎯 Quality Control**: Built-in quality assessment and deduplication
- **📊 Dataset Management**: Create, manage, and export Pashto datasets
- **🔄 Pipeline Orchestration**: Flexible, configurable processing pipelines
- **📈 Monitoring**: Comprehensive logging and progress tracking

### Language Features
- **Unicode Support**: Full Unicode compatibility for Pashto script
- **Character Normalization**: Standardize Pashto character variations
- **Digit Normalization**: Convert between Western, Pashto, and Arabic numerals
- **Diacritic Handling**: Optional diacritic removal and standardization
- **Tokenization**: Context-aware Pashto word and sentence tokenization
- **Stopwords**: Built-in Pashto stopword lists

## 📦 Repository Structure

```
Pashto-Processing-pipeline/
├── pashto_pipeline/          # Main package - Core processing modules
│   ├── core/                 # Pipeline orchestration
│   ├── preprocessing/        # Text normalization and tokenization
│   └── utils/                # Utility functions
│
├── code/pashto_dataset/      # Extended dataset processing system
│   ├── pipeline/             # Advanced pipeline management
│   ├── text_processor/       # Text processing modules
│   ├── scrapers/             # Web scraping tools
│   ├── pdf_processor/        # PDF extraction
│   └── dataset_manager/      # Dataset creation and management
│
├── docs/                     # Documentation
│   ├── guides/               # User guides and tutorials
│   ├── api/                  # API documentation
│   └── troubleshooting/      # Common issues and FAQ
│
├── examples/                 # Example code and configurations
│   ├── python/               # Python examples
│   ├── config/               # Sample configurations
│   └── bash/                 # Shell scripts
│
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
│
├── data/                     # Data directories
│   ├── raw/                  # Raw input data
│   └── processed/            # Processed output data
│
└── models/                   # Trained models and resources
```

## 🚀 Quick Start

### Installation

#### Option 1: Using the installation script (Recommended)
```bash
# Clone the repository
git clone https://github.com/tasal9/Pashto-Processing-pipeline.git
cd Pashto-Processing-pipeline

# Run the installation script
bash install.sh

# Activate the virtual environment
source venv/bin/activate
```

#### Option 2: Manual installation
```bash
# Clone the repository
git clone https://github.com/tasal9/Pashto-Processing-pipeline.git
cd Pashto-Processing-pipeline

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

#### Example 1: Simple Text Processing
```python
from pashto_pipeline import PashtoNormalizer, PashtoTokenizer

# Initialize components
normalizer = PashtoNormalizer(
    normalize_whitespace=True,
    normalize_digits='western'
)
tokenizer = PashtoTokenizer(preserve_punctuation=True)

# Process text
text = "سلام دنیا! دا د پښتو متن پروسس کولو یوه ساده بېلګه ده."
normalized = normalizer.normalize(text)
tokens = tokenizer.tokenize(normalized)

print(f"Tokens: {tokens}")
```

#### Example 2: Using the Pipeline
```python
from pashto_pipeline import TextProcessingPipeline, PashtoNormalizer, PashtoTokenizer

# Create pipeline
pipeline = TextProcessingPipeline()

# Add processing steps
pipeline.add_step('normalize', PashtoNormalizer().normalize)
pipeline.add_step('tokenize', PashtoTokenizer().tokenize)

# Process text
result = pipeline.process("سلام دنیا!", verbose=True)
print(result)

# Batch processing
texts = ["زه په کابل کې اوسېږم.", "پښتو یوه ښکلې ژبه ده."]
results = pipeline.process_batch(texts)
```

#### Example 3: Advanced Dataset Processing
```python
from code.pashto_dataset.text_processor.text_normalizer import PashtoTextNormalizer
from code.pashto_dataset.text_processor.quality_filter import QualityFilter

# Initialize advanced components
normalizer = PashtoTextNormalizer()
quality_filter = QualityFilter()

# Process and filter text
text = "سلام دنیا"
normalized = normalizer.normalize(text)
is_quality = quality_filter.is_high_quality(normalized)

print(f"Text quality: {'High' if is_quality else 'Low'}")
```

## 📚 Documentation

### Quick Links
- [Installation Guide](docs/guides/installation.md)
- [Configuration Guide](docs/guides/configuration.md)
- [Usage Tutorials](docs/guides/usage_tutorials.md)
- [Best Practices](docs/guides/best_practices.md)
- [API Reference](docs/api/README.md)
- [Troubleshooting](docs/troubleshooting/common_issues.md)
- [FAQ](docs/troubleshooting/faq.md)

### Examples
Check the `examples/` directory for:
- **Python Examples**: `examples/python/`
- **Configuration Files**: `examples/config/`
- **Shell Scripts**: `examples/bash/`

## 🔧 Configuration

The pipeline is highly configurable. See `examples/config/` for sample configuration files:

```yaml
# example: basic_config.yaml
pipeline:
  name: "pashto_processing"
  version: "1.0"

processing:
  normalize:
    unicode_form: "NFC"
    remove_diacritics: false
    normalize_digits: "western"
  
  tokenize:
    preserve_punctuation: true
    lowercase: false
```

## 🛠️ Components

### Core Components (`pashto_pipeline/`)
- **TextProcessingPipeline**: Main pipeline orchestrator
- **PashtoNormalizer**: Unicode and character normalization
- **PashtoTokenizer**: Word and sentence tokenization
- **StopwordsRemover**: Remove common Pashto stopwords

### Extended Components (`code/pashto_dataset/`)
- **Web Scrapers**: Collect data from Pashto websites
- **PDF Processor**: Extract text from PDFs
- **Quality Filter**: Assess text quality
- **Deduplicator**: Remove duplicate content
- **Dataset Manager**: Create and manage datasets

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pashto_pipeline --cov-report=html

# Run specific test file
pytest tests/unit/test_normalizer.py
```

## 📊 Supported Data Sources

- **Web Scraping**: Pashto news sites, forums, and blogs
- **PDF Documents**: Books, articles, and reports
- **Text Files**: Plain text, CSV, JSON
- **Databases**: SQL and NoSQL databases
- **APIs**: Integration with external Pashto language APIs

## 🌍 Language Support

- **Pashto Dialects**: Southern, Northern, and Western Pashto
- **Script**: Perso-Arabic script (Pashto variant)
- **Encodings**: UTF-8, UTF-16, legacy encodings
- **Normalization**: NFC, NFD, NFKC, NFKD forms

## 📈 Performance

- **Memory Efficient**: Optimized for large datasets
- **Batch Processing**: Process multiple texts efficiently
- **Progress Tracking**: Real-time monitoring with tqdm
- **Parallel Processing**: Multi-threading support (where applicable)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Pashto NLP Research Community
- Unicode Consortium for Pashto script support
- Contributors and maintainers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tasal9/Pashto-Processing-pipeline/issues)
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory

## 🗺️ Roadmap

- [ ] Add more Pashto-specific NLP tools
- [ ] Improve dialect detection
- [ ] Add part-of-speech tagging
- [ ] Support for speech-to-text integration
- [ ] Enhanced OCR for Pashto handwriting
- [ ] Cloud deployment guides

---

**Made with ❤️ for the Pashto language community**