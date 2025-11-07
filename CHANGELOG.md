# Changelog

All notable changes to the Pashto Processing Pipeline will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-07

### 🎉 Initial Release

Complete Pashto text processing pipeline with comprehensive features for dataset creation and management.

### Added

#### Core Components
- **TextProcessingPipeline**: Flexible pipeline orchestration system
  - Add/remove processing steps dynamically
  - Single and batch text processing
  - Progress tracking with tqdm
  - Configurable step chaining

- **PashtoNormalizer**: Advanced text normalization
  - Unicode normalization (NFC, NFD, NFKC, NFKD)
  - Character standardization (ي→ی, ك→ک)
  - Digit normalization (Pashto ↔ Arabic ↔ Western)
  - Diacritic removal (optional)
  - Whitespace normalization

- **PashtoTokenizer**: Context-aware tokenization
  - Word tokenization with punctuation handling
  - Sentence tokenization
  - Character tokenization
  - Token detokenization
  - Pashto-specific punctuation support

- **StopwordsRemover**: Pashto stopword filtering
  - Default Pashto stopword list
  - Custom stopword support
  - Add/remove stopwords dynamically

#### Extended Features (code/pashto_dataset/)
- **Web Scrapers**: Multi-source data collection
  - News scraper for Pashto news sites
  - Library scraper for document repositories
  - Rate limiting and error handling
  - Encoding detection and normalization

- **PDF Processor**: PDF text extraction
  - Text extraction with PyPDF2, pdfplumber, PyMuPDF
  - OCR support with Tesseract and EasyOCR
  - Metadata extraction
  - Quality assessment
  - Pashto-specific utilities

- **Text Processor**: Advanced NLP features
  - Language detection
  - Quality filtering
  - Deduplication with multiple algorithms
  - NLP processing pipeline

- **Dataset Manager**: Dataset creation and management
  - Dataset creation from multiple sources
  - Train/validation/test splitting
  - Quality metrics calculation
  - Multiple export formats (JSON, CSV, Parquet, HF)
  - Version management
  - Memory optimization

- **Pipeline Orchestration**: Advanced pipeline management
  - Configuration management
  - Logging and monitoring
  - Progress tracking and error recovery
  - Scheduler for automated runs
  - Validation system

#### Utility Features
- **I/O Utilities**: File operations
  - Read/write text files with UTF-8 support
  - JSON file handling
  - Line-based file operations
  - Path management

- **Logging**: Comprehensive logging
  - Console and file logging
  - Configurable log levels
  - UTF-8 support for Pashto text
  - Structured logging format

#### Documentation
- **User Guides**:
  - Installation guide
  - Quick start tutorial
  - Configuration guide
  - Usage tutorials
  - Best practices

- **API Documentation**:
  - Complete API reference
  - Code examples
  - Type hints

- **Troubleshooting**:
  - Common issues and solutions
  - Performance optimization tips
  - FAQ

#### Examples
- **Python Examples**:
  - Basic usage examples
  - Advanced pipeline examples
  - Batch processing examples

- **Configuration Files**:
  - Basic configuration
  - Batch processing configuration
  - Web scraping configuration

- **Shell Scripts**:
  - CLI usage examples
  - Automation scripts

#### Installation & Setup
- **install.sh**: Automated installation script
  - Virtual environment creation
  - Dependency installation
  - NLTK data download
  - Directory structure setup
  - Support for dev/minimal installs

- **setup.py**: Package setup configuration
  - Automatic dependency resolution
  - Entry points for CLI tools
  - Development extras
  - Package metadata

- **requirements.txt**: Comprehensive dependency list
  - Core data processing libraries
  - NLP and ML libraries
  - Web scraping tools
  - PDF processing utilities
  - Testing and quality tools

#### Testing
- **test_installation.py**: Installation verification
  - Import tests
  - Component functionality tests
  - Integration tests
  - Automated test suite

- **Unit Tests**: Component-specific tests
  - Normalizer tests
  - Tokenizer tests
  - Pipeline tests

#### Project Infrastructure
- **.gitignore**: Comprehensive ignore rules
  - Python artifacts
  - IDE files
  - Build directories
  - Data directories (with .gitkeep)
  - Log files

- **LICENSE**: MIT License
- **CONTRIBUTING.md**: Contribution guidelines
- **QUICKSTART.md**: Quick start guide
- **README.md**: Comprehensive project documentation

### Features by Category

#### Text Processing
- Unicode normalization (4 forms)
- Character standardization
- Digit normalization (3 systems)
- Whitespace cleaning
- Diacritic handling
- Word tokenization
- Sentence segmentation
- Stopword removal

#### Data Collection
- Web scraping (news, libraries)
- PDF text extraction
- OCR for scanned documents
- Encoding detection
- Rate limiting
- Error handling

#### Quality Control
- Language detection
- Quality filtering
- Deduplication
- Metadata extraction
- Quality metrics
- Validation

#### Dataset Management
- Dataset creation
- Data splitting
- Format conversion
- Version control
- Memory optimization
- Export to HuggingFace

#### Pipeline Features
- Flexible step chaining
- Batch processing
- Progress tracking
- Error recovery
- Configuration management
- Logging and monitoring
- Scheduling

### Technical Details

#### Supported Python Versions
- Python 3.8+
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

#### Dependencies
- Core: numpy, pandas, pyyaml, tqdm
- NLP: nltk, spacy, transformers
- Web: requests, beautifulsoup4, selenium, scrapy
- PDF: PyPDF2, pdfplumber, pymupdf
- OCR: pytesseract, easyocr
- ML: scikit-learn, datasets
- Testing: pytest, pytest-cov
- Quality: black, flake8, isort

#### Supported Formats
- Input: Text, PDF, HTML, JSON, CSV
- Output: JSON, CSV, Parquet, HuggingFace Dataset, XML

#### Language Support
- Pashto (Southern, Northern, Western dialects)
- Perso-Arabic script
- Unicode support
- Multiple encodings

### Performance
- Memory-efficient batch processing
- Configurable batch sizes
- Progress tracking
- Parallel processing support (where applicable)

### Known Limitations
- OCR requires Tesseract installation
- Some dependencies are optional
- Large files may require memory optimization
- Network required for web scraping

### Notes
- First stable release
- Production-ready
- Actively maintained
- Community contributions welcome

---

## [Unreleased]

### Planned Features
- Part-of-speech tagging for Pashto
- Named entity recognition
- Sentiment analysis
- Dialect detection
- Speech-to-text integration
- Enhanced OCR for handwriting
- Cloud deployment guides
- Docker support
- API server
- Web interface

---

For older versions, see the git history.
