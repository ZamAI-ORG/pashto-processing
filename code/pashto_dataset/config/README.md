# Pashto Dataset Pipeline Configuration System

## Overview

This repository contains a comprehensive configuration system for building Pashto text datasets, including source configurations, processing pipelines, and quality control mechanisms specifically designed for the Pashto language and Perso-Arabic script processing.

## Directory Structure

```
code/pashto_dataset/config/
├── configs/
│   ├── main_config.json          # Main configuration settings
│   ├── scraping_config.json      # Web scraping and data collection
│   ├── processing_config.json    # Text processing and quality control
│   └── pashto_pipeline_example.py # Example implementation
├── documentation/
│   └── pashto_research_report.md # Comprehensive research findings
├── sources/
│   └── source_config.json        # Source-specific configurations
└── samples/
    └── pashto_text_samples.md    # Test samples for validation
```

## Configuration Files

### 1. Main Configuration (`main_config.json`)
Global settings for the entire pipeline:
- Unicode normalization rules
- Text quality thresholds
- Output format preferences
- Logging configuration
- Data storage structure

**Key Settings:**
- Encoding: UTF-8 with NFC normalization
- RTL text handling: Enabled
- Quality threshold: 0.6
- Output formats: JSON, CSV, TXT, XML

### 2. Source Configuration (`source_config.json`)
Detailed configurations for all Pashto text sources:

**Digital Libraries:**
- **ACKU Digital Repository**: Afghanistan Center at Kabul University
- **Afghanistan Digital Library (NYU)**: 576 digitized documents
- **UNO Dari/Pashto Collection**: University of Nebraska Omaha
- **UCLA Middle Eastern Studies**: Islamic manuscripts collection

**Academic Datasets:**
- **CC100-Pashto**: Commoncrawl-derived monolingual corpus
- **EPLD Dataset**: English-Pashto parallel corpus
- **NLPashto Corpus**: 15+ million words NLP corpus

**News Media:**
- **Afghan Central Press**: 4 Kabul newspapers
- **Khalq Newspaper Archives**: Historical newspaper collection

**Quality Ratings:** All sources are rated 6-9/10 for content quality and academic value.

### 3. Scraping Configuration (`scraping_config.json`)
Technical specifications for data collection:

**Web Scraping Settings:**
- User-Agent rotation for respectful crawling
- Rate limiting (15-60 requests/minute depending on source)
- Session management and cookie handling
- HTML parsing with BeautifulSoup4

**Pashto-Specific Processing:**
- Unicode range validation (U+0600-U+06FF, U+0750-U+077F, etc.)
- RTL text preservation
- Encoding detection and validation
- Language detection with Pashto-specific rules

**Error Handling:**
- Exponential backoff for failed requests
- Fallback encoding strategies
- Quality-based filtering

### 4. Processing Configuration (`processing_config.json`)
Advanced text processing rules:

**Unicode Handling:**
- NFC normalization as default
- Zero-width character removal
- Arabic shape normalization
- Bidirectional text support

**Quality Assessment:**
- Character ratio analysis (minimum 60% Pashto characters)
- Length filtering (50-100,000 characters)
- Duplicate detection using fuzzy matching
- Spam detection algorithms

**Language Processing:**
- Primary: langdetect library
- Fallback: Character frequency analysis
- Confidence threshold: 0.7

## Usage Examples

### Basic Pipeline Usage

```python
from pashto_pipeline_example import PashtoDatasetPipeline

# Initialize pipeline
pipeline = PashtoDatasetPipeline()

# Add Pashto text
pashto_text = "پښتو د پښتنو ژبه ده چې د افغانستان او پاکستان په ځینو سیمو کې ویل کېږي."
success = pipeline.add_sample_text(pashto_text, "sample")

# Save results
pipeline.save_results(output_dir="output")
```

### Advanced Configuration

```python
from pashto_pipeline_example import PashtoConfigManager

# Load configurations
config_manager = PashtoConfigManager()

# Get specific settings
main_config = config_manager.get("main")
scraping_config = config_manager.get("scraping", "source_specific_configs")

# Access source information
acku_config = scraping_config.get("acku_digital_repository", {})
print(f"ACKU rate limit: {acku_config.get('rate_limit', 'N/A')}")
```

### Custom Text Processing

```python
from pashto_pipeline_example import PashtoTextProcessor

# Initialize processor
processor = PashtoTextProcessor(config_manager)

# Process text
text = "د افغانستان د سولې لپاره ټول باید هڅه وکړي."
result = processor.process_text(text, "custom_source")

print(f"Language: {result.language}")
print(f"Quality: {result.quality_score:.2f}")
print(f"Word count: {result.word_count}")
```

## Pashto Text Characteristics

### Script Features
- **Writing System**: Extended Arabic script (Perso-Arabic)
- **Direction**: Right-to-left (RTL)
- **Character Set**: 44+ alphabets
- **Unicode Ranges**: U+0600-U+06FF, U+0750-U+077F, U+FB50-U+FDFF, U+FE70-U+FEFF

### Processing Challenges
1. **Cursive Script**: Characters change shape based on position
2. **Bidirectional Text**: Mixed LTR numbers and English words
3. **Encoding Variations**: Multiple Unicode representations
4. **Diacritical Marks**: Extensive use of combining marks
5. **Variant Forms**: Same character with different Unicode forms

### Quality Metrics
- **Pashto Character Ratio**: Minimum 60% of characters from Pashto Unicode ranges
- **Length Requirements**: 50-100,000 characters per document
- **Language Confidence**: Minimum 0.7 for language detection
- **Encoding Validity**: 100% valid UTF-8 encoding required

## Data Sources Priority

### Tier 1 (High Priority)
- ACKU Digital Repository
- Pashto Academy Peshawar
- UCLA Middle Eastern Studies

### Tier 2 (Medium Priority)
- Afghanistan Digital Library (NYU)
- EPLD Dataset
- Afghan Central Press

### Tier 3 (Lower Priority)
- CC100-Pashto Dataset
- UNO Dari/Pashto Collection
- Archive.org Pashto Collection

## Installation and Dependencies

### Required Python Packages
```bash
pip install langdetect beautifulsoup4 requests unicodedata
pip install python-arabic-reshaper python-bidi  # For advanced Arabic processing
```

### Optional Packages
```bash
pip install PyPDF2 pytesseract  # For PDF processing and OCR
pip install pandas  # For CSV export
```

## Configuration Customization

### Modifying Quality Thresholds
Edit `configs/main_config.json`:
```json
{
  "global_settings": {
    "text_processing": {
      "min_pashto_ratio": 0.8,        // Increase Pashto content requirement
      "quality_threshold": 0.7,       // Higher quality requirement
      "min_text_length": 100          // Longer minimum text
    }
  }
}
```

### Adding New Sources
Edit `configs/source_config.json`:
```json
{
  "sources": {
    "your_new_source": {
      "name": "Your Source Name",
      "url": "https://example.com",
      "access_type": "web",
      "quality_score": 8,
      "scraping_strategy": "web_scraping"
    }
  }
}
```

### Custom Processing Rules
Edit `configs/processing_config.json`:
```json
{
  "text_processing": {
    "pashto_specific": {
      "normalize_variant_forms": true,  // Enable variant normalization
      "preserve_orf": false             // ORF normalization
    }
  }
}
```

## Testing and Validation

### Using Sample Texts
The repository includes comprehensive sample texts in `samples/pashto_text_samples.md`:

1. **Basic Samples**: Simple sentences and daily conversation
2. **Literary Text**: Poetry and complex prose
3. **Technical Content**: Academic and scientific writing
4. **News Content**: Contemporary news articles
5. **Mixed Content**: Code-switched and multilingual text
6. **Edge Cases**: Short texts, long texts, Unicode challenges

### Running the Example
```bash
cd code/pashto_dataset/config/configs/
python pashto_pipeline_example.py
```

### Validation Checklist
- [ ] Unicode normalization working correctly
- [ ] Language detection identifying Pashto texts
- [ ] Quality scoring filtering appropriately
- [ ] RTL text handling properly
- [ ] Output formats generating correctly
- [ ] No encoding errors or data corruption

## Performance Considerations

### Batch Processing
- Process texts in batches of 100 documents
- Use parallel processing (4-8 cores recommended)
- Monitor memory usage (limit to 1GB per batch)
- Enable caching for repeated operations

### Storage Optimization
- Use gzip compression for JSON outputs
- Implement incremental processing
- Regular cleanup of temporary files
- Backup processed data automatically

### Quality vs. Speed Trade-offs
- **High Quality**: Strict filtering, detailed metadata, extensive validation
- **Fast Processing**: Relaxed quality thresholds, minimal processing steps
- **Balanced**: Default configuration provides good quality with reasonable speed

## Troubleshooting

### Common Issues

1. **Unicode Errors**
   - Ensure UTF-8 encoding throughout the pipeline
   - Check for invalid character sequences
   - Verify font support for Pashto characters

2. **Language Detection Failures**
   - Increase confidence threshold
   - Add custom Pashto validation
   - Check for encoding corruption

3. **Quality Score Too Low**
   - Adjust Pashto character ratio threshold
   - Check for mixed-language content
   - Verify text cleaning procedures

4. **Memory Issues**
   - Reduce batch size
   - Process texts sequentially
   - Clear intermediate results

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

### Adding New Sources
1. Research and verify source availability
2. Add configuration to `source_config.json`
3. Implement scraping strategy in `scraping_config.json`
4. Test with sample data
5. Document in research report

### Improving Processing
1. Identify specific Pashto text processing challenges
2. Propose algorithm improvements
3. Add new quality metrics
4. Test against diverse Pashto content

## Research Foundation

This configuration system is based on comprehensive research including:

- **Academic Papers**: 50+ research papers on Pashto NLP
- **Digital Libraries**: Survey of 20+ Afghan/Pashto digital collections  
- **Technical Standards**: Unicode specifications and Arabic script processing
- **Best Practices**: RTL language processing and low-resource language datasets
- **Community Input**: Pashto language experts and NLP researchers

See `documentation/pashto_research_report.md` for detailed findings.

## License and Usage

This configuration system is designed for:
- Academic research on Pashto language processing
- Development of Pashto NLP tools and datasets
- Educational purposes in computational linguistics
- Non-commercial language preservation efforts

When using these configurations, please:
- Respect source website terms of service
- Follow ethical data collection practices
- Credit original sources appropriately
- Contribute improvements back to the community

## Contact and Support

For questions, improvements, or contributions:
- Review the research documentation
- Check the configuration examples
- Test with provided sample texts
- Document any issues or improvements

This configuration system provides a solid foundation for building high-quality Pashto datasets while respecting the linguistic complexity and cultural importance of the Pashto language.