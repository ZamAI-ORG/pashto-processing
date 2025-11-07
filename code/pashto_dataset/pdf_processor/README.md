# Pashto PDF Processing Module

A sophisticated PDF text extraction and processing module specifically designed for Pashto documents. This module provides comprehensive support for both digital and scanned PDFs, with specialized handling for Pashto text encoding, font detection, and OCR capabilities.

## Features

### Core Functionality
- **Digital PDF Text Extraction**: Direct text extraction from PDFs with Pashto encoding support
- **OCR for Scanned Documents**: Advanced OCR capabilities using Tesseract for Pashto text
- **Text Cleaning and Normalization**: Specialized Pashto text preprocessing and cleaning
- **Metadata Extraction**: Comprehensive document metadata extraction (title, author, date, source)
- **Quality Assessment**: Advanced text quality evaluation and scoring
- **Batch Processing**: Efficient processing of multiple PDF documents

### Pashto-Specific Features
- **Unicode Support**: Full support for Pashto Unicode ranges (U+0750-U+077F)
- **Font Detection**: Automatic detection of Pashto-compatible fonts
- **Character Normalization**: Proper handling of Pashto character variations
- **Language Detection**: Automatic detection of Pashto content
- **Stopword Filtering**: Built-in Pashto stopword lists
- **Error Handling**: Specialized error handling for common Pashto text issues

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Tesseract OCR Engine** with Pashto language support
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install tesseract-ocr tesseract-ocr-pus
   
   # macOS (with Homebrew)
   brew install tesseract tesseract-lang
   
   # Windows
   # Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

3. **System Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
   
   # macOS
   brew install opencv
   ```

### Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install PyMuPDF pytesseract Pillow opencv-python numpy scipy regex chardet
```

## Quick Start

### Basic Usage

```python
from pashto_dataset.pdf_processor import PashtoPDFProcessor

# Initialize processor
processor = PashtoPDFProcessor(
    ocr_enabled=True,
    ocr_languages="eng+pus"
)

# Process a single PDF
result = processor.process_pdf(
    pdf_path="document.pdf",
    output_dir="output/",
    extract_metadata=True,
    assess_quality=True
)

# Access results
print(f"Extracted text: {result['full_text'][:200]}...")
print(f"Quality score: {result['quality_assessment']['overall_score']}")
print(f"Extraction method: {result['pages'][0]['extraction_method']}")
```

### Batch Processing

```python
# Process multiple PDFs
results = processor.batch_process(
    pdf_directory="pdfs_folder/",
    output_directory="processed_outputs/",
    file_pattern="*.pdf"
)

# Process results
for result in results:
    if result.get('success', True):
        print(f"✓ {result['pdf_path']} - Quality: {result['quality_assessment']['quality_grade']}")
    else:
        print(f"✗ {result['pdf_path']} - Error: {result['error']}")
```

### Advanced Configuration

```python
from pashto_dataset.pdf_processor.config_utils import ProcessingConfig, ConfigManager

# Create custom configuration
config = ProcessingConfig(
    ocr_enabled=True,
    ocr_languages="eng+pus",
    ocr_dpi=300,
    quality_threshold=0.7,
    save_raw_text=True,
    save_cleaned_text=True,
    save_normalized_text=True,
    output_encoding="utf-8"
)

# Save configuration
config_manager = ConfigManager()
config_manager.save_config(config, "my_config.json")

# Load configuration
loaded_config = config_manager.load_config("my_config.json")
```

## Module Structure

### Core Classes

#### `PashtoPDFProcessor`
Main processor class that orchestrates PDF processing workflow.

```python
processor = PashtoPDFProcessor(
    ocr_enabled: bool = True,
    ocr_languages: str = "eng+pus",
    log_level: str = "INFO"
)
```

**Key Methods:**
- `process_pdf()` - Process a single PDF document
- `batch_process()` - Process multiple PDF documents
- `_process_page()` - Process individual pages

#### `PashtoTextUtils`
Specialized utilities for Pashto text processing.

```python
utils = PashtoTextUtils()
```

**Key Methods:**
- `clean_text()` - Clean and normalize Pashto text
- `normalize_pashto()` - Normalize Pashto character variations
- `extract_sentences()` - Extract sentences from text
- `get_word_frequency()` - Calculate word frequencies
- `get_text_statistics()` - Get comprehensive text statistics

#### `OCRHandler`
OCR functionality for scanned PDF documents.

```python
ocr = OCRHandler(languages="eng+pus")
```

**Key Methods:**
- `extract_text_from_page()` - OCR text from PDF page
- `extract_text_from_image_file()` - OCR text from image file
- `batch_ocr()` - Perform OCR on multiple images
- `optimize_for_pashto()` - Optimize settings for Pashto

#### `MetadataExtractor`
Extract comprehensive metadata from PDF documents.

```python
extractor = MetadataExtractor()
```

**Key Methods:**
- `extract_metadata()` - Extract all metadata
- `save_metadata()` - Save metadata to JSON
- `get_metadata_summary()` - Get human-readable summary

#### `QualityAssessor`
Assess the quality of extracted text.

```python
assessor = QualityAssessor()
```

**Key Methods:**
- `assess_document()` - Assess document quality
- `compare_extraction_quality()` - Compare two extractions
- `_assess_language_quality()` - Language-specific quality metrics

### Utility Classes

#### `ProcessingConfig`
Configuration dataclass for all processing settings.

#### `ConfigManager`
Manage configuration loading, saving, and validation.

#### `FileProcessor`
Utility functions for file operations.

#### `PashtoValidationUtils`
Validation utilities for Pashto content.

## Configuration Options

### OCR Settings
```python
ProcessingConfig(
    ocr_enabled=True,              # Enable OCR
    ocr_languages="eng+pus",       # Tesseract languages
    ocr_dpi=300,                   # Rendering DPI
    ocr_config="--psm 6"           # Custom Tesseract config
)
```

### Text Processing
```python
ProcessingConfig(
    clean_text=True,               # Clean extracted text
    normalize_text=True,           # Normalize Pashto text
    remove_noise=True,             # Remove noise characters
    min_word_length=2              # Minimum word length
)
```

### Output Settings
```python
ProcessingConfig(
    save_raw_text=True,            # Save raw extracted text
    save_cleaned_text=True,        # Save cleaned text
    save_normalized_text=True,     # Save normalized text
    save_metadata=True,            # Save metadata JSON
    save_quality_report=True,      # Save quality assessment
    output_encoding="utf-8"        # Output file encoding
)
```

## Quality Assessment

The module provides comprehensive quality assessment with the following metrics:

### Overall Score (0.0 - 1.0)
- **Excellent** (0.8+): High-quality extraction with minimal issues
- **Good** (0.6-0.8): Acceptable quality with minor issues
- **Acceptable** (0.4-0.6): Usable but may need review
- **Poor** (0.2-0.4): Significant issues detected
- **Failed** (<0.2): Extraction failed or very low quality

### Assessment Categories

1. **Basic Metrics**: Text density, word count, compression ratio
2. **Language Quality**: Pashto ratio, character quality, vocabulary richness
3. **Content Quality**: Page success rate, content coherence, information density
4. **Structure Quality**: Punctuation usage, paragraph structure
5. **Technical Quality**: Extraction method success, confidence scores

## Output Files

When processing with output directory specified, the module generates:

### Text Files
- `{filename}_full_text.txt` - Raw extracted text
- `{filename}_cleaned_text.txt` - Cleaned text
- `{filename}_normalized_text.txt` - Normalized text

### Metadata Files
- `{filename}_metadata.json` - Comprehensive metadata
- `{filename}_quality_report.txt` - Quality assessment report

## Error Handling

The module includes comprehensive error handling:

```python
try:
    result = processor.process_pdf("document.pdf")
    if not result.get('success', True):
        print(f"Processing failed: {result.get('error', 'Unknown error')}")
    else:
        print("Processing successful")
except Exception as e:
    print(f"Critical error: {str(e)}")
```

## Performance Optimization

### For Large Documents
```python
config = ProcessingConfig(
    max_pages_per_batch=10,        # Process in smaller batches
    parallel_processing=True,      # Use multiple workers
    max_workers=4                  # Number of parallel workers
)
```

### For Better OCR Results
```python
# Optimize for Pashto
ocr.optimize_for_pashto()

# High DPI for better recognition
config = ProcessingConfig(ocr_dpi=400)
```

## Troubleshooting

### Common Issues

1. **Tesseract Not Found**
   ```bash
   # Verify installation
   tesseract --version
   tesseract --list-langs
   
   # Check Pashto support
   echo " pashto" | tesseract stdin stdout -l pus
   ```

2. **Low OCR Quality**
   - Increase DPI: `ocr_dpi=400`
   - Optimize preprocessing: `ocr.optimize_for_pashto()`
   - Check image quality: Use higher resolution scans

3. **Character Encoding Issues**
   - Ensure UTF-8 encoding: `output_encoding="utf-8"`
   - Check PDF font support
   - Verify system locale settings

4. **Memory Issues with Large PDFs**
   - Reduce batch size: `max_pages_per_batch=5`
   - Disable parallel processing for large files
   - Process pages individually

### Logging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or specify log level in processor
processor = PashtoPDFProcessor(log_level="DEBUG")
```

## Advanced Usage Examples

### Custom Text Processing Pipeline
```python
from pashto_dataset.pdf_processor import PashtoPDFProcessor, PashtoTextUtils

# Initialize components
processor = PashtoPDFProcessor()
utils = PashtoTextUtils()

# Process PDF
result = processor.process_pdf("document.pdf")

# Custom text processing
if result.get('full_text'):
    # Clean text
    cleaned = utils.clean_text(result['full_text'])
    
    # Extract specific content
    words = utils.extract_words(cleaned)
    sentences = utils.extract_sentences(cleaned)
    
    # Get statistics
    stats = utils.get_text_statistics(cleaned)
    print(f"Pashto ratio: {stats['pashto_ratio']:.2%}")
```

### Quality Comparison
```python
from pashto_dataset.pdf_processor import QualityAssessor

assessor = QualityAssessor()

# Process same document with different settings
result1 = processor.process_pdf("document.pdf")  # Standard settings
result2 = processor.process_pdf("document.pdf")  # High DPI OCR

# Compare quality
comparison = assessor.compare_extraction_quality(result1, result2)
print(f"Quality improvement: {comparison['quality_improvement']:.2%}")
```

### Batch Validation
```python
from pashto_dataset.pdf_processor.config_utils import PashtoValidationUtils

# Validate PDFs before processing
pdf_files = FileProcessor.list_pdfs("pdfs_folder/")

for pdf_file in pdf_files:
    validation = PashtoValidationUtils.validate_pdf_for_pashto(pdf_file)
    
    if validation['file_valid'] and validation['estimated_pashto_content'] > 0.3:
        print(f"✓ {pdf_file} - Good for processing")
    else:
        print(f"⚠ {pdf_file} - {validation['recommendations']}")
```

## Contributing

1. **Code Style**: Follow PEP 8 guidelines
2. **Documentation**: Update docstrings and README
3. **Testing**: Add tests for new functionality
4. **Pashto Support**: Ensure compatibility with Pashto text

## License

This module is provided as-is for educational and research purposes. Please ensure compliance with any applicable licenses for dependencies (PyMuPDF, Tesseract, etc.).

## Acknowledgments

- PyMuPDF (fitz) for PDF processing capabilities
- Tesseract OCR for text recognition
- Pashto language community for input and testing
- Unicode Consortium for Pashto character support

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review existing issues and documentation
3. Create detailed bug reports with example files
4. Include system information and error logs

## Version History

- **v1.0.0**: Initial release with core functionality
  - Digital PDF text extraction
  - OCR support for Pashto
  - Text cleaning and normalization
  - Metadata extraction
  - Quality assessment
  - Batch processing capabilities