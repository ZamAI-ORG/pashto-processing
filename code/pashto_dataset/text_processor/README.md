# Pashto Text Processing and Tokenization System

A comprehensive, production-ready natural language processing system specifically designed for Pashto text analysis, tokenization, quality filtering, and dataset preparation.

## 🌟 Features

### Core Capabilities
- **Advanced Text Normalization**: Arabic script normalization with Pashto-specific character handling
- **Smart Tokenization**: Right-to-left script tokenization with Pashto linguistic awareness
- **Quality Assessment**: Multi-dimensional quality scoring with Pashto-specific metrics
- **Intelligent Deduplication**: Exact and near-duplicate detection using multiple similarity algorithms
- **Language Detection**: Sophisticated Pashto language identification and Arabic script discrimination
- **Batch Processing**: High-performance processing of large text collections
- **Export Capabilities**: Multiple output formats (JSON, CSV, TXT)

### Pashto-Specific Features
- **Pashto Character Recognition**: Identifies and weights Pashto-specific characters (ځ، څ، ډ، ړ، ږ، ګ، ڼ)
- **Script Direction Handling**: Proper right-to-left text processing
- **Diacritic Management**: Automatic removal of Arabic diacritics and combining marks
- **Tatweel Processing**: Intelligent removal of Arabic stretching characters
- **Linguistic Pattern Recognition**: Pashto grammar markers and common word detection
- **Quality Indicators**: Pashto-specific quality metrics and content validation

## 📁 Project Structure

```
code/pashto_dataset/text_processor/
├── __init__.py                    # Package initialization
├── pashto_nlp_processor.py        # Main processing system
├── text_normalizer.py            # Arabic script normalization
├── pashto_tokenizer.py           # Pashto-aware tokenization
├── quality_filter.py             # Text quality assessment
├── deduplicator.py               # Duplicate detection and removal
├── language_detector.py          # Pashto language identification
├── example_usage.py              # Comprehensive usage examples
└── README.md                     # This documentation
```

## 🚀 Quick Start

### Basic Usage

```python
from pashto_dataset.text_processor import PashtoNLPProcessor

# Initialize the processor
processor = PashtoNLPProcessor(
    enable_normalization=True,
    enable_tokenization=True,
    enable_quality_filtering=True,
    enable_deduplication=True,
    enable_language_detection=True,
    quality_threshold=0.3,
    deduplication_threshold=0.85
)

# Process a single text
text = "زه یو ښوونکی دی چې د ښوونې ښه مینه لري."
result = processor.process_text(text)

print(f"Quality Score: {result['quality_assessment']['overall_score']}")
print(f"Language: {result['language_detection']['detected_language']}")
print(f"Processed Text: {result['processed_text']}")
```

### Batch Processing

```python
# Process multiple texts with deduplication
texts = [
    "زه یو ښوونکی دی.",
    "د افغانستان خلک ښه ژبه لري.",
    "دا یوه ښه ورځ ده.",
    # ... more texts
]

batch_result = processor.process_texts(
    texts, 
    apply_deduplication=True,
    return_removed_content=True
)

print(f"Input: {batch_result['input_count']} texts")
print(f"Output: {batch_result['output_count']} texts")
print(f"Duplicates removed: {batch_result['deduplication']['removed_exact_duplicates']}")
```

## 🔧 Component Details

### 1. PashtoTextNormalizer

Handles Arabic script normalization with Pashto-specific adjustments:

```python
from pashto_dataset.text_processor import PashtoTextNormalizer

normalizer = PashtoTextNormalizer()
text, stats = normalizer.normalize("زه  یو   ښوونکي   دى  چې  په   کور   کې  د  ښونګرونو  ښودل  کېندى .")

# Returns normalized text with processing statistics
```

**Features:**
- Diacritics removal
- Tatweel character elimination  
- Pashto character standardization
- Number normalization
- Whitespace regularization

### 2. PashtoTokenizer

Advanced tokenization for Pashto Arabic script:

```python
from pashto_dataset.text_processor import PashtoTokenizer

tokenizer = PashtoTokenizer()
tokenization_result = tokenizer.tokenize_complete("زه یو ښوونکی دی.")

# Returns structured tokenization with metadata
```

**Features:**
- Right-to-left script handling
- Word boundary detection
- Sentence splitting
- Pashto-specific word recognition
- Script type classification

### 3. QualityFilter

Multi-dimensional text quality assessment:

```python
from pashto_dataset.text_processor import QualityFilter

quality_filter = QualityFilter()
quality_result = quality_filter.calculate_text_quality(text, tokenization_data)

# Returns comprehensive quality score and recommendations
```

**Features:**
- Length-based scoring
- Pashto content analysis
- Readability metrics
- Structural assessment
- Noise detection
- Spam filtering

### 4. TextDeduplicator

Advanced duplicate detection and removal:

```python
from pashto_dataset.text_processor import TextDeduplicator

deduplicator = TextDeduplicator()
dedup_result = deduplicator.deduplicate_texts(texts, remove_near_duplicates=True)

# Returns deduplicated collection with duplicate analysis
```

**Features:**
- Exact duplicate detection using hashing
- Near-duplicate detection using similarity algorithms
- Pashto-specific similarity measures
- Content-based deduplication
- Duplicate pattern analysis

### 5. PashtoLanguageDetector

Specialized language detection for Pashto:

```python
from pashto_dataset.text_processor import PashtoLanguageDetector

detector = PashtoLanguageDetector()
lang_result = detector.detect_language(text)

# Returns language detection with confidence scores
```

**Features:**
- Arabic script language discrimination
- Pashto-specific character analysis
- Common word pattern recognition
- Character frequency analysis
- Confidence scoring

## 📊 Configuration Options

### Processor Configuration

```python
processor = PashtoNLPProcessor(
    enable_normalization=True,        # Enable text normalization
    enable_tokenization=True,         # Enable tokenization
    enable_quality_filtering=True,    # Enable quality filtering
    enable_deduplication=True,        # Enable deduplication
    enable_language_detection=True,   # Enable language detection
    quality_threshold=0.3,            # Minimum quality score (0.0-1.0)
    deduplication_threshold=0.85      # Similarity threshold for duplicates (0.0-1.0)
)
```

### Quality Thresholds

- **0.8+**: Excellent quality
- **0.6-0.8**: Good quality
- **0.4-0.6**: Fair quality
- **0.2-0.4**: Poor quality
- **0.0-0.2**: Very poor quality

### Deduplication Thresholds

- **0.95+**: High similarity (likely duplicates)
- **0.85+**: Medium similarity (near duplicates)
- **0.70+**: Low similarity (possible duplicates)

## 📈 Quality Metrics

### Text Quality Assessment

The system evaluates text quality using multiple dimensions:

1. **Length Score** (20% weight)
   - Character count analysis
   - Word count evaluation
   - Sentence structure assessment

2. **Pashto Content Score** (30% weight)
   - Pashto-specific character usage
   - Common word detection
   - Script purity analysis

3. **Readability Score** (20% weight)
   - Average word length
   - Sentence variety
   - Lexical diversity

4. **Structure Score** (20% weight)
   - Punctuation usage
   - Sentence completeness
   - Paragraph structure

5. **Cleanliness Score** (10% weight)
   - Noise ratio
   - Repetition analysis
   - Encoding issue detection

### Language Detection Scoring

The system uses multiple indicators for Pashto detection:

- **Pashto Characters** (ځ، څ، ډ، ړ، ږ، ګ، ڼ)
- **Common Words** (زه، تاسو، په، د، تر، سره)
- **Pattern Matching** (Pashto-specific grammar markers)
- **Character Frequency** (Distribution analysis)
- **Script Analysis** (Arabic script validation)

## 🔄 Processing Pipeline

```
Input Text
    ↓
Language Detection
    ↓
Text Normalization
    ↓
Tokenization
    ↓
Quality Assessment
    ↓
Deduplication
    ↓
Output Results
```

### Pipeline Steps

1. **Input Validation**: Check for empty or invalid text
2. **Language Detection**: Identify if text contains Arabic script
3. **Early Exit**: Stop if not Arabic script (for non-Pashto texts)
4. **Text Normalization**: Clean and standardize text
5. **Tokenization**: Extract words, sentences, and tokens
6. **Quality Assessment**: Calculate quality score and metrics
7. **Quality Threshold Check**: Filter low-quality content
8. **Deduplication**: Remove exact and near-duplicate content
9. **Output Generation**: Provide comprehensive results

## 📊 Output Formats

### JSON Format

```json
{
  "input_count": 10,
  "output_count": 8,
  "processing_status": "completed",
  "statistics": {
    "language_distribution": {
      "pashto": 7,
      "other_arabic_script": 1
    },
    "quality_distribution": {
      "high": 5,
      "medium": 2,
      "low": 1,
      "average_score": 0.75
    }
  },
  "results": [...]
}
```

### CSV Format

```csv
index,original_text,processed_text,quality_score,language,status
0,زه یو ښوونکی دی.,زه یو ښوونکی دی.,0.85,pashto,completed
1,Hello world,Hello world,0.00,non_arabic,completed
```

### TXT Format

```
Pashto NLP Processing Results
========================================

Text 1:
Original: زه یو ښوونکی دی.
Processed: زه یو ښوونکی دی.
Quality Score: 0.85
Language: pashto
Status: completed
```

## 🎯 Use Cases

### Dataset Preparation
- Clean and standardize Pashto text collections
- Remove low-quality and duplicate content
- Ensure language consistency
- Prepare data for machine learning

### Content Quality Assessment
- Evaluate text quality before publishing
- Filter inappropriate or low-quality content
- Analyze content distribution and patterns
- Generate quality reports

### Language Processing Research
- Pashto linguistic analysis
- Arabic script text processing
- Multilingual text processing research
- NLP algorithm development

### Text Mining Applications
- Extract meaningful Pashto text from mixed content
- Identify and categorize Pashto content
- Search and retrieval optimization
- Content recommendation systems

## 🔧 Advanced Usage

### Custom Quality Filtering

```python
# Create custom quality filter with specific thresholds
custom_filter = QualityFilter()
custom_filter.thresholds['min_length'] = 10
custom_filter.thresholds['min_pashto_score'] = 0.2

# Process with custom filtering
result = custom_filter.calculate_text_quality(text)
```

### Similarity Analysis

```python
# Analyze similarity between texts
similarity_report = deduplicator.get_similarity_report(texts, top_pairs=20)
print(f"Average similarity: {similarity_report['average_similarity']}")
```

### Batch Language Detection

```python
# Detect language for multiple texts
detection_results = language_detector.batch_detect(texts)
pashto_texts = [text for text, result in zip(texts, detection_results) 
                if result['detected_language'] == 'pashto']
```

## 📊 Performance Statistics

The system tracks comprehensive processing statistics:

- **Processing Time**: Average, minimum, maximum processing times
- **Component Usage**: Percentage usage of each component
- **Success Rate**: Ratio of successful to total processing attempts
- **Quality Distribution**: Breakdown of quality scores
- **Language Distribution**: Language detection results
- **Deduplication Statistics**: Duplicate detection and removal metrics

## 🤝 Integration Examples

### With Machine Learning Pipelines

```python
# Prepare text data for ML training
processor = PashtoNLPProcessor()
batch_result = processor.process_texts(raw_texts)

# Extract high-quality, deduplicated Pashto texts
clean_texts = [result['processed_text'] for result in batch_result['results'] 
               if result['processing_status'] == 'completed']

# Use for training
model.fit(clean_texts, labels)
```

### With Data Pipelines

```python
# Process incoming text streams
def process_text_stream(text_stream):
    processor = PashtoNLPProcessor()
    
    for batch in chunk_text_stream(text_stream, batch_size=100):
        results = processor.process_texts(batch, apply_deduplication=True)
        yield from results['results']
```

## 🛠️ Development and Testing

### Running Examples

```python
# Run comprehensive demonstration
from pashto_dataset.text_processor.example_usage import main
main()
```

### Testing Individual Components

```python
# Test normalization
normalizer = PashtoTextNormalizer()
text, stats = normalizer.normalize("زه  یو   ښوونکي   دى")

# Test tokenization
tokenizer = PashtoTokenizer()
tokens = tokenizer.tokenize_words("زه یو ښوونکی دی")

# Test quality assessment
quality_filter = QualityFilter()
quality = quality_filter.calculate_text_quality("زه یو ښوونکی دی")
```

## 📝 Best Practices

### Text Processing
1. **Pre-filter Input**: Remove obvious noise before processing
2. **Batch Processing**: Use batch processing for large collections
3. **Quality Thresholds**: Adjust thresholds based on your use case
4. **Deduplication**: Apply deduplication for dataset preparation

### Performance Optimization
1. **Component Selection**: Disable unnecessary components
2. **Batch Size**: Optimize batch size for your system
3. **Memory Management**: Monitor memory usage for large datasets
4. **Profiling**: Use statistics to identify bottlenecks

### Quality Assessment
1. **Threshold Tuning**: Calibrate quality thresholds for your domain
2. **Manual Validation**: Periodically validate results manually
3. **Component Weights**: Adjust quality component weights if needed
4. **Domain Adaptation**: Consider domain-specific quality factors

## 🐛 Troubleshooting

### Common Issues

1. **Empty Results**: Check if input texts contain Arabic script
2. **Low Quality Scores**: Verify text meets minimum quality criteria
3. **High Duplication**: Adjust deduplication threshold if needed
4. **Memory Issues**: Process large datasets in smaller batches

### Performance Issues

1. **Slow Processing**: Disable unnecessary components
2. **High Memory Usage**: Reduce batch size
3. **Quality Filtering Too Strict**: Lower quality threshold
4. **Deduplication Too Aggressive**: Increase similarity threshold

## 📄 License

This Pashto text processing system is developed for research and educational purposes. Please ensure compliance with relevant data usage and privacy regulations when processing text data.

## 🤝 Contributing

Contributions to improve the Pashto text processing system are welcome! Areas for enhancement:

- Additional Pashto linguistic features
- Performance optimizations
- Quality metric improvements
- Language detection enhancements
- Documentation improvements

## 📞 Support

For questions, issues, or suggestions regarding the Pashto text processing system:

1. Review the example usage and documentation
2. Check the troubleshooting section
3. Examine the component-specific documentation
4. Run the comprehensive demonstration for testing

---

**Pashto Text Processing System v1.0.0**  
*Advanced natural language processing for Pashto text analysis*