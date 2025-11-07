# API Reference

Complete API reference for the Pashto Dataset Pipeline. This documentation provides detailed information about all classes, methods, and functions.

## 📋 Table of Contents

- [Core Classes](#core-classes)
- [Pipeline Class](#pipeline-class)
- [Configuration Classes](#configuration-classes)
- [Data Processors](#data-processors)
- [Quality Assessment](#quality-assessment)
- [Text Processing](#text-processing)
- [I/O Operations](#io-operations)
- [Utilities](#utilities)
- [Exceptions](#exceptions)

## 🏗️ Core Classes

### Pipeline

The main class for processing Pashto datasets.

```python
from pashto_pipeline import Pipeline, Config

class Pipeline:
    """
    Main pipeline class for processing Pashto datasets.
    
    The Pipeline class orchestrates the entire data processing workflow,
    from reading input data to writing processed output.
    
    Attributes:
        config (Config): Configuration object
        processors (list): List of data processors
        quality_checker (QualityChecker): Quality assessment component
        logger (Logger): Logger instance
        
    Example:
        >>> config = Config.from_file('config.yaml')
        >>> pipeline = Pipeline(config)
        >>> result = pipeline.run('input/', 'output/')
        >>> print(f"Processed {result.total_processed} items")
    """
```

#### Constructor

```python
def __init__(self, config: Config) -> None:
    """
    Initialize the pipeline with configuration.
    
    Args:
        config: Configuration object containing all pipeline settings
        
    Raises:
        ConfigurationError: Invalid configuration provided
        
    Example:
        >>> config = Config.from_file('config.yaml')
        >>> pipeline = Pipeline(config)
    """
```

#### Main Methods

##### run()

```python
def run(self, input_path: str, output_path: str) -> ProcessingResult:
    """
    Run the complete pipeline processing.
    
    This method executes the entire processing workflow:
    1. Load input data
    2. Apply preprocessing
    3. Run quality checks
    4. Apply filters
    5. Save results
    
    Args:
        input_path: Path to input data directory or file
        output_path: Path to output directory
        
    Returns:
        ProcessingResult object containing processing statistics
        
    Raises:
        ProcessingError: Processing failed
        InputError: Invalid input data
        OutputError: Cannot write to output directory
        
    Example:
        >>> result = pipeline.run('data/raw/', 'data/processed/')
        >>> print(f"Quality score: {result.quality_score:.2f}")
    """
```

##### process_file()

```python
def process_file(self, file_path: str) -> ProcessedData:
    """
    Process a single input file.
    
    Args:
        file_path: Path to file to process
        
    Returns:
        ProcessedData object with processed content
        
    Raises:
        FileNotFoundError: Input file not found
        ProcessingError: File processing failed
    """
```

##### process_batch()

```python
def process_batch(self, file_paths: List[str]) -> BatchResult:
    """
    Process multiple files in batch.
    
    Args:
        file_paths: List of file paths to process
        
    Returns:
        BatchResult object with batch processing results
        
    Raises:
        ProcessingError: Batch processing failed
    """
```

#### Configuration Methods

##### from_config()

```python
@classmethod
def from_config(cls, config_path: str) -> 'Pipeline':
    """
    Create pipeline from configuration file.
    
    Args:
        config_path: Path to configuration YAML file
        
    Returns:
        Pipeline instance configured from file
        
    Raises:
        ConfigurationError: Invalid configuration file
        FileNotFoundError: Configuration file not found
        
    Example:
        >>> pipeline = Pipeline.from_config('config/production.yaml')
    """
```

##### validate_config()

```python
def validate_config(self) -> bool:
    """
    Validate current configuration.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigurationError: Configuration validation failed
    """
```

#### Utility Methods

##### get_statistics()

```python
def get_statistics(self) -> PipelineStatistics:
    """
    Get pipeline processing statistics.
    
    Returns:
        PipelineStatistics object with processing metrics
    """
```

##### reset()

```python
def reset(self) -> None:
    """
    Reset pipeline state and clear caches.
    """
```

##### save_state()

```python
def save_state(self, state_path: str) -> None:
    """
    Save current pipeline state.
    
    Args:
        state_path: Path to save state file
    """
```

##### load_state()

```python
def load_state(self, state_path: str) -> None:
    """
    Load pipeline state from file.
    
    Args:
        state_path: Path to state file to load
    """
```

## ⚙️ Configuration Classes

### Config

Main configuration class.

```python
class Config:
    """
    Configuration management class.
    
    Handles loading, validation, and access to configuration settings.
    
    Attributes:
        data (dict): Raw configuration data
        pipeline_config (dict): Pipeline-specific configuration
        input_config (dict): Input processing configuration
        processing_config (dict): Text processing configuration
        output_config (dict): Output configuration
        quality_config (dict): Quality assessment configuration
    """
```

#### Constructor and Factories

```python
def __init__(self, data: dict) -> None:
    """
    Initialize configuration from data dictionary.
    
    Args:
        data: Configuration data dictionary
    """
```

```python
@classmethod
def from_file(cls, config_path: str) -> 'Config':
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Config instance
        
    Raises:
        ConfigurationError: Invalid configuration file
        FileNotFoundError: Configuration file not found
        
    Example:
        >>> config = Config.from_file('config/basic_config.yaml')
    """
```

```python
@classmethod
def from_dict(cls, config_dict: dict) -> 'Config':
    """
    Create configuration from dictionary.
    
    Args:
        config_dict: Configuration dictionary
        
    Returns:
        Config instance
    """
```

```python
@classmethod
def from_env(cls) -> 'Config':
    """
    Create configuration from environment variables.
    
    Returns:
        Config instance
    """
```

#### Configuration Access

```python
def get(self, key: str, default: Any = None) -> Any:
    """
    Get configuration value by key.
    
    Args:
        key: Configuration key (supports dot notation)
        default: Default value if key not found
        
    Returns:
        Configuration value
        
    Example:
        >>> config.get('pipeline.name')
        >>> config.get('processing.min_length', 10)
    """
```

```python
def get_pipeline_config(self) -> dict:
    """Get pipeline configuration section."""
```

```python
def get_input_config(self) -> dict:
    """Get input configuration section."""
```

```python
def get_processing_config(self) -> dict:
    """Get processing configuration section."""
```

```python
def get_output_config(self) -> dict:
    """Get output configuration section."""
```

```python
def get_quality_config(self) -> dict:
    """Get quality configuration section."""
```

#### Configuration Validation

```python
def validate(self) -> bool:
    """
    Validate configuration.
    
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigurationError: Configuration validation failed
    """
```

```python
def validate_required_keys(self) -> bool:
    """Validate required configuration keys are present."""
```

```python
def validate_types(self) -> bool:
    """Validate configuration value types."""
```

#### Configuration Updates

```python
def update(self, updates: dict) -> None:
    """
    Update configuration with new values.
    
    Args:
        updates: Dictionary of configuration updates
    """
```

```python
def merge(self, other_config: 'Config') -> 'Config':
    """
    Merge with another configuration.
    
    Args:
        other_config: Configuration to merge
        
    Returns:
        New Config instance with merged values
    """
```

```python
def override(self, **overrides) -> 'Config':
    """
    Create configuration with overrides.
    
    Args:
        **overrides: Key-value pairs to override
        
    Returns:
        New Config instance with overrides
    """
```

## 🔄 Data Processors

### BaseProcessor

Abstract base class for all data processors.

```python
from abc import ABC, abstractmethod
from typing import Protocol

class BaseProcessor(ABC):
    """
    Abstract base class for data processors.
    
    All data processors must inherit from this class and implement
    the process method.
    
    Attributes:
        config (dict): Processor configuration
        logger (Logger): Logger instance
    """
```

```python
@abstractmethod
def process(self, data: Any) -> Any:
    """
    Process input data.
    
    Args:
        data: Input data to process
        
    Returns:
        Processed data
        
    Raises:
        ProcessingError: Processing failed
    """
```

### TextProcessor

Specialized processor for text data.

```python
class TextProcessor(BaseProcessor):
    """
    Processor for Pashto text data.
    
    Handles text normalization, cleaning, and filtering.
    
    Example:
        >>> processor = TextProcessor(config)
        >>> processed = processor.process(raw_text)
    """
```

#### Main Processing Methods

```python
def normalize_text(self, text: str) -> str:
    """
    Normalize Pashto text according to Unicode standards.
    
    Args:
        text: Raw text to normalize
        
    Returns:
        Normalized text
        
    Example:
        >>> normalized = processor.normalize_text("مونږ ژبه")
        >>> print(normalized)  # "موږ ژبه"
    """
```

```python
def clean_text(self, text: str) -> str:
    """
    Clean text by removing unwanted content.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
        
    Example:
        >>> cleaned = processor.clean_text("Visit http://example.com")
        >>> print(cleaned)  # "Visit "
    """
```

```python
def filter_text(self, text: str) -> bool:
    """
    Check if text meets filtering criteria.
    
    Args:
        text: Text to filter
        
    Returns:
        True if text passes filters
    """
```

```python
def process_text(self, text: str) -> ProcessedText:
    """
    Complete text processing pipeline.
    
    Args:
        text: Raw text input
        
    Returns:
        ProcessedText object with results
        
    Example:
        >>> result = processor.process_text("زموږ ژبه ښه ده")
        >>> print(result.text)
        >>> print(result.quality_score)
    """
```

#### Language-Specific Methods

```python
def detect_language(self, text: str) -> LanguageDetection:
    """
    Detect language and confidence of text.
    
    Args:
        text: Text to analyze
        
    Returns:
        LanguageDetection result
        
    Example:
        >>> detection = processor.detect_language("زموږ ژبه")
        >>> print(detection.language)  # 'pashto'
        >>> print(detection.confidence)  # 0.95
    """
```

```python
def normalize_pashto_script(self, text: str) -> str:
    """
    Normalize Pashto script variations.
    
    Args:
        text: Text with script variations
        
    Returns:
        Normalized text
    """
```

```python
def check_pashto_compliance(self, text: str) -> ComplianceResult:
    """
    Check if text complies with Pashto language rules.
    
    Args:
        text: Text to check
        
    Returns:
        ComplianceResult with details
    """
```

### WebScrapingProcessor

Processor for web-scraped data.

```python
class WebScrapingProcessor(BaseProcessor):
    """
    Processor for web-scraped Pashto content.
    
    Handles HTML cleaning, content extraction, and web-specific
    text processing.
    """
```

#### Web Processing Methods

```python
def extract_text_from_html(self, html_content: str) -> str:
    """
    Extract clean text from HTML content.
    
    Args:
        html_content: HTML content to process
        
    Returns:
        Extracted and cleaned text
    """
```

```python
def clean_web_content(self, text: str) -> str:
    """
    Clean web-specific content (scripts, styles, etc.).
    
    Args:
        text: Web content to clean
        
    Returns:
        Cleaned web text
    """
```

```python
def extract_metadata(self, html_content: str) -> dict:
    """
    Extract metadata from web content.
    
    Args:
        html_content: HTML content
        
    Returns:
        Dictionary of extracted metadata
    """
```

### SocialMediaProcessor

Processor for social media data.

```python
class SocialMediaProcessor(BaseProcessor):
    """
    Processor for social media content.
    
    Handles hashtags, mentions, URLs, and social media
    specific text patterns.
    """
```

#### Social Media Methods

```python
def extract_hashtags(self, text: str) -> List[str]:
    """
    Extract hashtags from social media text.
    
    Args:
        text: Social media text
        
    Returns:
        List of extracted hashtags
    """
```

```python
def extract_mentions(self, text: str) -> List[str]:
    """
    Extract mentions from social media text.
    
    Args:
        text: Social media text
        
    Returns:
        List of extracted mentions
    """
```

```python
def process_engagement_metrics(self, post_data: dict) -> dict:
    """
    Process engagement metrics from social media post.
    
    Args:
        post_data: Social media post data
        
    Returns:
        Processed engagement metrics
    """
```

## 🎯 Quality Assessment

### QualityChecker

Main quality assessment class.

```python
class QualityChecker:
    """
    Comprehensive quality assessment for Pashto datasets.
    
    Implements multiple quality metrics including linguistic,
    statistical, and domain-specific checks.
    
    Attributes:
        config (dict): Quality configuration
        checks (dict): Registered quality check functions
        
    Example:
        >>> checker = QualityChecker(config)
        >>> result = checker.assess('data/processed/')
        >>> print(f"Quality score: {result['overall']['score']:.2f}")
    """
```

#### Main Assessment Methods

```python
def assess(self, dataset_path: str) -> QualityResult:
    """
    Perform comprehensive quality assessment.
    
    Args:
        dataset_path: Path to dataset to assess
        
    Returns:
        QualityResult object with assessment results
        
    Raises:
        QualityError: Quality assessment failed
        
    Example:
        >>> result = checker.assess('data/processed/')
        >>> print(f"Overall: {result.overall_score:.2f}")
        >>> print(f"Language: {result.language_quality:.2f}")
    """
```

```python
def assess_text(self, text: str) -> TextQualityResult:
    """
    Assess quality of individual text.
    
    Args:
        text: Text to assess
        
    Returns:
        TextQualityResult with detailed metrics
    """
```

```python
def assess_dataset(self, dataset: Dataset) -> DatasetQualityResult:
    """
    Assess quality of entire dataset.
    
    Args:
        dataset: Dataset to assess
        
    Returns:
        DatasetQualityResult with dataset metrics
    """
```

#### Specific Quality Checks

```python
def check_language_quality(self, text: str) -> float:
    """
    Check language-specific quality metrics.
    
    Args:
        text: Text to assess
        
    Returns:
        Language quality score (0.0 to 1.0)
    """
```

```python
def check_technical_quality(self, text: str) -> float:
    """
    Check technical quality (encoding, formatting, etc.).
    
    Args:
        text: Text to assess
        
    Returns:
        Technical quality score (0.0 to 1.0)
    """
```

```python
def check_content_quality(self, text: str) -> float:
    """
    Check content quality (grammar, coherence, etc.).
    
    Args:
        text: Text to assess
        
    Returns:
        Content quality score (0.0 to 1.0)
    """
```

```python
def check_statistical_quality(self, text: str) -> float:
    """
    Check statistical quality metrics.
    
    Args:
        text: Text to assess
        
    Returns:
        Statistical quality score (0.0 to 1.0)
    """
```

### Quality Metrics

#### Basic Metrics

```python
class BasicMetrics:
    """Basic text quality metrics."""
    
    @staticmethod
    def text_length(text: str) -> int:
        """Get text length in characters."""
    
    @staticmethod
    def word_count(text: str) -> int:
        """Get word count."""
    
    @staticmethod
    def sentence_count(text: str) -> int:
        """Get sentence count."""
    
    @staticmethod
    def average_word_length(text: str) -> float:
        """Get average word length."""
    
    @staticmethod
    def average_sentence_length(text: str) -> float:
        """Get average sentence length."""
```

#### Language Metrics

```python
class LanguageMetrics:
    """Pashto language-specific quality metrics."""
    
    @staticmethod
    def pashto_ratio(text: str) -> float:
        """Calculate ratio of Pashto content."""
    
    @staticmethod
    def script_consistency(text: str) -> float:
        """Check script consistency."""
    
    @staticmethod
    def character_distribution(text: str) -> dict:
        """Get character distribution."""
    
    @staticmethod
    def word_frequency_analysis(text: str) -> dict:
        """Analyze word frequency distribution."""
```

#### Quality Scoring

```python
class QualityScorer:
    """Overall quality scoring."""
    
    def __init__(self, config: dict):
        self.config = config
        self.weights = config.get('weights', {})
    
    def calculate_score(self, metrics: dict) -> float:
        """
        Calculate overall quality score from metrics.
        
        Args:
            metrics: Dictionary of quality metrics
            
        Returns:
            Overall quality score (0.0 to 1.0)
        """
```

## 📝 Text Processing

### PashtoText

Text representation with Pashto-specific functionality.

```python
class PashtoText:
    """
    Text representation optimized for Pashto language processing.
    
    Provides methods for text manipulation, analysis, and
    Pashto-specific operations.
    
    Attributes:
        text (str): The text content
        encoding (str): Text encoding
        metadata (dict): Text metadata
        
    Example:
        >>> pstext = PashtoText("زموږ ژبه ښه ده")
        >>> print(pstext.word_count)
        >>> print(pstext.is_pashto)
    """
```

#### Constructor

```python
def __init__(self, text: str, encoding: str = "utf-8", metadata: dict = None):
    """
    Initialize Pashto text object.
    
    Args:
        text: Text content
        encoding: Text encoding
        metadata: Additional metadata
    """
```

#### Properties

```python
@property
def text(self) -> str:
    """Get text content."""
    return self._text

@property
def word_count(self) -> int:
    """Get word count."""
    return len(self.words)

@property
def character_count(self) -> int:
    """Get character count."""
    return len(self.text)

@property
def sentence_count(self) -> int:
    """Get sentence count."""
    return len(self.sentences)

@property
def is_pashto(self) -> bool:
    """Check if text is primarily Pashto."""
```

#### Text Analysis

```python
def detect_language(self) -> LanguageDetection:
    """
    Detect language of the text.
    
    Returns:
        LanguageDetection result
    """
```

```python
def get_character_stats(self) -> CharacterStats:
    """
    Get character-level statistics.
    
    Returns:
        CharacterStats object
    """
```

```python
def get_word_frequency(self) -> WordFrequency:
    """
    Get word frequency analysis.
    
    Returns:
        WordFrequency object
    """
```

```python
def find_patterns(self, pattern: str) -> List[Match]:
    """
    Find text patterns.
    
    Args:
        pattern: Regular expression pattern
        
    Returns:
        List of pattern matches
    """
```

#### Text Manipulation

```python
def normalize(self) -> 'PashtoText':
    """
    Normalize the text.
    
    Returns:
        New normalized PashtoText instance
    """
```

```python
def clean(self) -> 'PashtoText':
    """
    Clean the text.
    
    Returns:
        New cleaned PashtoText instance
    """
```

```python
def filter(self, min_length: int = None, max_length: int = None) -> 'PashtoText':
    """
    Filter the text based on criteria.
    
    Args:
        min_length: Minimum text length
        max_length: Maximum text length
        
    Returns:
        New filtered PashtoText instance
    """
```

```python
def split_sentences(self) -> List['PashtoText']:
    """
    Split text into sentences.
    
    Returns:
        List of PashtoText objects (one per sentence)
    """
```

### TextNormalizer

Text normalization utilities.

```python
class TextNormalizer:
    """
    Text normalization utilities for Pashto.
    
    Provides methods for Unicode normalization, character
    standardization, and Pashto-specific text cleaning.
    """
```

#### Normalization Methods

```python
def normalize_unicode(self, text: str, form: str = "NFC") -> str:
    """
    Normalize Unicode text.
    
    Args:
        text: Text to normalize
        form: Unicode normalization form (NFC, NFD, NFKC, NFKD)
        
    Returns:
        Normalized text
        
    Example:
        >>> normalized = normalizer.normalize_unicode("مونږ ژبه")
    """
```

```python
def normalize_arabic_script(self, text: str) -> str:
    """
    Normalize Arabic script variations.
    
    Args:
        text: Text with script variations
        
    Returns:
        Normalized text
    """
```

```python
def normalize_digits(self, text: str) -> str:
    """
    Normalize digit representations.
    
    Args:
        text: Text with mixed digit formats
        
    Returns:
        Text with normalized digits
    """
```

```python
def normalize_punctuation(self, text: str) -> str:
    """
    Normalize punctuation marks.
    
    Args:
        text: Text with punctuation
        
    Returns:
        Text with normalized punctuation
    """
```

#### Cleaning Methods

```python
def remove_control_characters(self, text: str) -> str:
    """
    Remove control characters.
    
    Args:
        text: Text containing control characters
        
    Returns:
        Text with control characters removed
    """
```

```python
def remove_html_entities(self, text: str) -> str:
    """
    Remove HTML entities.
    
    Args:
        text: Text with HTML entities
        
    Returns:
        Text with HTML entities decoded
    """
```

```python
def remove_urls(self, text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Text containing URLs
        
    Returns:
        Text with URLs removed
    """
```

```python
def remove_punctuation(self, text: str, keep_sentence_endings: bool = True) -> str:
    """
    Remove punctuation from text.
    
    Args:
        text: Text to process
        keep_sentence_endings: Keep sentence ending punctuation
        
    Returns:
        Text with punctuation removed
    """
```

## 💾 I/O Operations

### DataLoader

Load data from various sources.

```python
class DataLoader:
    """
    Load data from various sources.
    
    Supports multiple file formats and data sources.
    
    Attributes:
        config (dict): Loading configuration
        supported_formats (list): Supported file formats
    """
```

#### Loading Methods

```python
def load_file(self, file_path: str) -> Dataset:
    """
    Load data from a single file.
    
    Args:
        file_path: Path to file to load
        
    Returns:
        Dataset object
        
    Raises:
        FileNotFoundError: File not found
        UnsupportedFormatError: File format not supported
        
    Example:
        >>> loader = DataLoader(config)
        >>> dataset = loader.load_file('data/texts.txt')
    """
```

```python
def load_directory(self, directory_path: str) -> Dataset:
    """
    Load data from directory.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        Dataset object containing all files
    """
```

```python
def load_from_url(self, url: str) -> Dataset:
    """
    Load data from URL.
    
    Args:
        url: URL to load data from
        
    Returns:
        Dataset object
        
    Example:
        >>> dataset = loader.load_from_url('https://example.com/data.json')
    """
```

#### Format-Specific Loaders

```python
def load_json(self, file_path: str) -> Dataset:
    """Load data from JSON file."""
```

```python
def load_csv(self, file_path: str) -> Dataset:
    """Load data from CSV file."""
```

```python
def load_xml(self, file_path: str) -> Dataset:
    """Load data from XML file."""
```

```python
def load_text(self, file_path: str) -> Dataset:
    """Load data from text file."""
```

### DataSaver

Save processed data to various formats.

```python
class DataSaver:
    """
    Save data to various formats and destinations.
    
    Supports multiple output formats and destinations.
    
    Attributes:
        config (dict): Saving configuration
        supported_formats (list): Supported output formats
    """
```

#### Saving Methods

```python
def save_dataset(self, dataset: Dataset, output_path: str) -> None:
    """
    Save dataset to output location.
    
    Args:
        dataset: Dataset to save
        output_path: Output path
        
    Raises:
        OutputError: Cannot write to output location
        
    Example:
        >>> saver = DataSaver(config)
        >>> saver.save_dataset(dataset, 'output/processed.json')
    """
```

```python
def save_json(self, data: list, file_path: str) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Output file path
    """
```

```python
def save_csv(self, data: list, file_path: str) -> None:
    """
    Save data to CSV file.
    
    Args:
        data: Data to save
        file_path: Output file path
    """
```

```python
def save_xml(self, data: list, file_path: str) -> None:
    """
    Save data to XML file.
    
    Args:
        data: Data to save
        file_path: Output file path
    """
```

## 🔧 Utilities

### Logger

Logging utilities.

```python
class PipelineLogger:
    """
    Pipeline-specific logging utilities.
    
    Provides structured logging for pipeline operations.
    
    Example:
        >>> logger = PipelineLogger('pipeline.log')
        >>> logger.info('Processing started', extra={'file': 'input.txt'})
    """
```

#### Logging Methods

```python
def info(self, message: str, **kwargs) -> None:
    """Log info message."""
```

```python
def warning(self, message: str, **kwargs) -> None:
    """Log warning message."""
```

```python
def error(self, message: str, **kwargs) -> None:
    """Log error message."""
```

```python
def debug(self, message: str, **kwargs) -> None:
    """Log debug message."""
```

### ProgressMonitor

Track processing progress.

```python
class ProgressMonitor:
    """
    Monitor and report processing progress.
    
    Provides real-time progress tracking for long-running
    processing operations.
    
    Example:
        >>> monitor = ProgressMonitor(total=1000)
        >>> monitor.update(100)
        >>> print(monitor.get_progress_string())
    """
```

#### Progress Methods

```python
def __init__(self, total: int, description: str = "Processing"):
    """
    Initialize progress monitor.
    
    Args:
        total: Total number of items to process
        description: Description of operation
    """
```

```python
def update(self, current: int) -> None:
    """
    Update progress.
    
    Args:
        current: Current progress count
    """
```

```python
def increment(self, amount: int = 1) -> None:
    """
    Increment progress.
    
    Args:
        amount: Amount to increment
    """
```

```python
def get_progress_string(self) -> str:
    """
    Get formatted progress string.
    
    Returns:
        Progress string
    """
```

```python
def get_eta(self) -> str:
    """
    Get estimated time remaining.
    
    Returns:
        ETA string
    """
```

### Validator

Input validation utilities.

```python
class Validator:
    """
    Input validation utilities.
    
    Provides validation for various input types and formats.
    """
```

#### Validation Methods

```python
def validate_file_path(self, file_path: str) -> bool:
    """
    Validate file path.
    
    Args:
        file_path: File path to validate
        
    Returns:
        True if file path is valid
        
    Raises:
        ValidationError: File path is invalid
    """
```

```python
def validate_text(self, text: str) -> bool:
    """
    Validate text content.
    
    Args:
        text: Text to validate
        
    Returns:
        True if text is valid
    """
```

```python
def validate_encoding(self, text: str, encoding: str) -> bool:
    """
    Validate text encoding.
    
    Args:
        text: Text to validate
        encoding: Expected encoding
        
    Returns:
        True if encoding is valid
    """
```

## ⚠️ Exceptions

### Base Exceptions

```python
class PipelineError(Exception):
    """Base exception for pipeline operations."""
```

```python
class ConfigurationError(PipelineError):
    """Configuration-related errors."""
```

```python
class ProcessingError(PipelineError):
    """Processing-related errors."""
```

```python
class QualityError(PipelineError):
    """Quality assessment errors."""
```

```python
class InputError(PipelineError):
    """Input data errors."""
```

```python
class OutputError(PipelineError):
    """Output data errors."""
```

```python
class ValidationError(PipelineError):
    """Validation errors."""
```

### Specific Exceptions

```python
class FileNotFoundError(PipelineError):
    """File not found error."""
```

```python
class UnsupportedFormatError(PipelineError):
    """Unsupported file format error."""
```

```python
class EncodingError(PipelineError):
    """Text encoding error."""
```

```python
class LanguageError(PipelineError):
    """Language detection/processing error."""
```

## 📚 Usage Examples

### Basic Pipeline Usage

```python
from pashto_pipeline import Pipeline, Config

# Load configuration
config = Config.from_file('config.yaml')

# Create pipeline
pipeline = Pipeline(config)

# Process data
result = pipeline.run('data/input/', 'data/output/')

print(f"Processed: {result.total_processed}")
print(f"Quality: {result.quality_score:.2f}")
print(f"Time: {result.processing_time:.2f}s")
```

### Custom Processor

```python
from pashto_pipeline.processors import BaseProcessor

class CustomProcessor(BaseProcessor):
    def process(self, data):
        # Your custom processing logic
        processed = do_custom_processing(data)
        return processed

# Use custom processor
pipeline = Pipeline(config)
pipeline.add_processor(CustomProcessor(config))
```

### Quality Assessment

```python
from pashto_pipeline.quality import QualityChecker

# Create quality checker
checker = QualityChecker(config)

# Assess dataset
result = checker.assess('data/processed/')

# Check individual text
text_result = checker.assess_text("زموږ ژبه ښه ده")

print(f"Dataset quality: {result.overall_score:.2f}")
print(f"Text quality: {text_result.score:.2f}")
```

### Text Processing

```python
from pashto_pipeline.text import PashtoText, TextNormalizer

# Create text object
pstext = PashtoText("زموږ ژبه ښه ده")

# Analyze text
print(f"Word count: {pstext.word_count}")
print(f"Is Pashto: {pstext.is_pashto}")

# Normalize text
normalizer = TextNormalizer()
normalized = normalizer.normalize_unicode(pstext.text)
print(f"Normalized: {normalized}")
```

## 📖 Complete API Reference

For the complete API reference with all methods, parameters, and return types, see:

- [Core Classes](core.md) - Pipeline and main classes
- [Processors](processors.md) - Data processing classes
- [Quality Assessment](quality.md) - Quality checking and scoring
- [Configuration](config.md) - Configuration management
- [Text Processing](text.md) - Text processing utilities
- [I/O Operations](io.md) - Data loading and saving
- [Utilities](utils.md) - Utility classes and functions

## 🔗 Related Documentation

- [Installation Guide](../guides/installation.md)
- [Configuration Guide](../guides/configuration.md)
- [Usage Tutorials](../guides/usage_tutorials.md)
- [Best Practices](../guides/best_practices.md)
- [Troubleshooting](../troubleshooting/common_issues.md)