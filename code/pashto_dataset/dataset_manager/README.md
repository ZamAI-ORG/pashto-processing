# Hugging Face Dataset Management System

A comprehensive system for creating, managing, and maintaining datasets with full Hugging Face integration. This system provides a complete workflow for dataset lifecycle management including creation, validation, splitting, quality assessment, and export capabilities.

## Features

### 🔧 Core Functionality
- **Dataset Creation**: Create datasets from various data formats (JSON, CSV, DataFrame, lists)
- **Memory Optimization**: Efficient processing of large datasets with chunked operations
- **Multi-format Support**: Export in JSON, JSONL, CSV, Parquet, CoNLL, and Hugging Face formats

### 📊 Data Management
- **Version Control**: Semantic versioning with branch and tag support
- **Metadata Management**: Comprehensive metadata tracking and documentation generation
- **Quality Assessment**: Automated quality metrics calculation and validation
- **Data Splitting**: Multiple splitting strategies (random, stratified, group-based, temporal)

### ✅ Validation & Quality
- **Comprehensive Validation**: Structure, content, and statistical validation
- **Quality Metrics**: Completeness, uniqueness, balance, and language-specific metrics
- **Error Detection**: Automatic detection of data quality issues
- **Performance Monitoring**: Memory usage tracking and optimization suggestions

### 🚀 Export & Integration
- **Multiple Export Formats**: JSON, CSV, Parquet, CoNLL, Hugging Face datasets
- **Hugging Face Hub Integration**: Direct upload to HF Hub with proper documentation
- **Batch Export**: Export in multiple formats simultaneously
- **Custom Export**: Flexible export options for specific use cases

## Installation

```bash
# Clone or download the dataset management system
cd dataset_manager

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from dataset_manager import DatasetManager, DatasetConfig
import pandas as pd

# Create configuration
config = DatasetConfig(
    dataset_name="my_pashto_dataset",
    description="A Pashto language dataset",
    language="pas"
)

# Initialize manager
manager = DatasetManager(config)

# Create dataset from data
data = pd.DataFrame({
    "text": ["زه طالب یم", "دا ښه کتاب دی"],
    "label": ["education", "book"]
})
dataset = manager.create_dataset(data)

# Save and version
version = manager.save_dataset("v1.0.0")
print(f"Dataset saved as: {version}")
```

### Advanced Workflow

```python
# Calculate quality metrics
metrics = manager.calculate_quality_metrics()
print(f"Dataset quality: {metrics['overall_completeness']:.2%}")

# Split dataset
splits = manager.split_dataset(
    strategy="stratified", 
    stratified_column="label"
)
print(f"Split sizes: {len(splits['train'])} train, {len(splits['val'])} val, {len(splits['test'])} test")

# Export in multiple formats
for format in ["json", "csv", "parquet"]:
    output_path = manager.export_dataset(format)
    print(f"Exported {format}: {output_path}")

# Upload to Hugging Face Hub
if manager.config.repo_id:
    repo_url = manager.upload_to_hf()
    print(f"Uploaded to: {repo_url}")
```

## Configuration

### DatasetConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_name` | str | "pashto_dataset" | Name of the dataset |
| `dataset_description` | str | "A comprehensive Pashto language dataset" | Description |
| `version` | str | "1.0.0" | Version number |
| `language` | str | "pas" | Language code |
| `license` | str | "CC BY 4.0" | License type |
| `train_ratio` | float | 0.8 | Training split ratio |
| `val_ratio` | float | 0.1 | Validation split ratio |
| `test_ratio` | float | 0.1 | Test split ratio |
| `max_memory_gb` | float | 8.0 | Maximum memory usage |
| `chunk_size` | int | 10000 | Processing chunk size |

### Hugging Face Integration

```python
config = DatasetConfig(
    dataset_name="my_dataset",
    repo_id="username/my-dataset",  # Your HF repository
    token="your_hf_token",  # HF token (or use environment variable)
    private=False  # Public or private repository
)
```

## Core Components

### 1. DatasetManager
The main interface for all dataset operations.

```python
from dataset_manager import DatasetManager

manager = DatasetManager(config)
```

**Key Methods:**
- `create_dataset(data, schema)`: Create new dataset
- `load_dataset(version)`: Load existing dataset
- `save_dataset(version)`: Save current dataset
- `split_dataset()`: Create train/val/test splits
- `validate_dataset()`: Run comprehensive validation
- `calculate_quality_metrics()`: Calculate quality metrics
- `export_dataset(format)`: Export in specified format

### 2. DatasetCreator
Handles dataset creation, loading, and basic operations.

```python
from dataset_manager import DatasetCreator

creator = DatasetCreator(config)
dataset = creator.create_dataset(data)
```

### 3. MemoryOptimizer
Optimizes memory usage for large datasets.

```python
from dataset_manager import MemoryOptimizer

optimizer = MemoryOptimizer(config)
optimized_dataset = optimizer.optimize_dataset(dataset)
```

**Features:**
- Automatic data type optimization
- Chunked processing for large datasets
- Memory usage analysis
- Compression for large datasets
- Memory-mapped storage

### 4. QualityMetrics
Calculates comprehensive quality metrics.

```python
from dataset_manager import QualityMetrics

metrics = QualityMetrics(config)
quality_report = metrics.calculate_all_metrics(dataset)
```

**Metrics Include:**
- Completeness (missing values)
- Uniqueness (duplicate detection)
- Balance (class distribution)
- Diversity (lexical, semantic, feature)
- Statistical properties
- Language-specific metrics (for Pashto)

### 5. DatasetSplitter
Provides multiple splitting strategies.

```python
from dataset_manager import DatasetSplitter

splitter = DatasetSplitter(config)

# Random split
splits = splitter.split(dataset, {"train": 0.8, "val": 0.1, "test": 0.1})

# Stratified split
splits = splitter.split(dataset, {"train": 0.7, "val": 0.15, "test": 0.15}, 
                       strategy="stratified", stratified_column="label")

# Group-based split (for cross-validation)
splits = splitter.split(dataset, {"train": 0.7, "val": 0.15, "test": 0.15},
                       strategy="group", group_column="document_id")
```

### 6. DatasetExporter
Handles export in multiple formats.

```python
from dataset_manager import DatasetExporter

exporter = DatasetExporter(config)

# Export single dataset
json_path = exporter.export_dataset(dataset, "json")
csv_path = exporter.export_dataset(dataset, "csv")

# Export splits
hf_path = exporter.export_dataset_dict(splits, "hf_dataset")

# Upload to Hugging Face Hub
repo_url = exporter.upload_to_hub(dataset)
```

### 7. DatasetValidator
Performs comprehensive validation.

```python
from dataset_manager import DatasetValidator

validator = DatasetValidator(config)
validation_results = validator.validate_dataset(dataset)
```

**Validation Checks:**
- Structure validation (columns, features, data types)
- Data quality validation (completeness, uniqueness)
- Content validation (language detection, harmful content)
- Statistical validation (distribution analysis)
- Memory usage validation

### 8. Versioning
Manages dataset versions with semantic versioning.

```python
from dataset_manager import DatasetVersioning

versioning = DatasetVersioning(config)

# Generate new version
new_version = versioning.generate_version()  # "1.0.1"
patch_version = versioning.generate_version(patch=5)  # "1.0.5"

# Create version
version_info = versioning.create_version(dataset, "1.0.0", "Initial release")

# Compare versions
comparison = versioning.compare_versions("1.0.0", "1.0.1")

# Create branch
branch_version = versioning.create_branch("1.0.0", "experimental")
```

### 9. MetadataManager
Handles metadata and documentation generation.

```python
from dataset_manager import MetadataManager

metadata_manager = MetadataManager(config)

# Initialize metadata
metadata_manager.initialize_metadata(dataset)

# Update metadata
metadata_manager.update_metadata(dataset, "v1.0.0")

# Generate dataset card (README.md)
card_content = metadata_manager.generate_dataset_card(config, num_samples, metrics)
```

## Data Formats

### Input Formats
- **Pandas DataFrame**: `Dataset.from_pandas(df)`
- **Dictionary**: `Dataset.from_dict(data_dict)`
- **List**: `Dataset.from_list(data_list)`

### Output Formats
- **JSON**: `{"column1": [...], "column2": [...]}`
- **JSONL**: One JSON object per line
- **CSV**: Standard CSV format
- **Parquet**: Columnar storage format
- **CoNLL**: For NLP tasks (NER, POS tagging)
- **Hugging Face**: Native HF dataset format

### Export Examples

```python
# JSON export
manager.export_dataset("json")
# Output: exports/dataset_json/dataset.json

# CSV export (with splits)
splits = manager.split_dataset()
manager.export_dataset("csv")
# Output: exports/dataset_csv/train.csv, val.csv, test.csv

# Hugging Face format
manager.export_dataset("hf_dataset")
# Output: exports/dataset_hf_dataset/ (HF format)

# Custom export
manager.export_dataset("json", output_path=Path("custom/path"))
```

## Memory Optimization

The system includes comprehensive memory optimization for large datasets:

```python
# Automatic optimization
optimized_dataset = manager.optimizer.optimize_dataset(large_dataset)

# Memory analysis
analysis = manager.optimizer.analyze_memory_usage(dataset)
print(f"Memory usage: {analysis['estimated_memory_mb']:.1f} MB")
print(f"Recommendations: {analysis['recommendations']}")

# Chunked processing
processed = manager.optimizer.process_in_chunks(
    large_dataset, 
    process_func=my_processing_function,
    chunk_size=5000
)

# Cache management
cache_path = manager.optimizer.cache_dataset(dataset, "my_cache_key")
cached_dataset = manager.optimizer.load_cached_dataset("my_cache_key")
```

## Quality Assessment

### Automatic Quality Metrics

```python
metrics = manager.calculate_quality_metrics()

# Basic metrics
print(f"Samples: {metrics['num_samples']:,}")
print(f"Features: {metrics['num_features']}")
print(f"Completeness: {metrics['overall_completeness']:.2%}")
print(f"Uniqueness: {metrics['overall_uniqueness']:.2%}")
print(f"Balance: {metrics['overall_balance_score']:.2%}")

# Content quality
if 'text_quality' in metrics:
    for column, quality in metrics['text_quality'].items():
        print(f"{column} - Language consistency: {quality['language_consistency']['consistency_score']:.2%}")

# Pashto-specific metrics
if 'pashto_specific' in metrics:
    for column, pashto_metrics in metrics['pashto_specific'].items():
        print(f"{column} - Pashto quality: {pashto_metrics['overall_pashto_quality']:.2%}")
```

### Validation Results

```python
validation = manager.validate_dataset()

print(f"Status: {validation['overall_status']}")
print(f"Errors: {len(validation['errors'])}")
print(f"Warnings: {len(validation['warnings'])}")

if validation['errors']:
    print("Errors found:")
    for error in validation['errors']:
        print(f"  - {error}")

if validation['warnings']:
    print("Warnings:")
    for warning in validation['warnings']:
        print(f"  - {warning}")
```

## Hugging Face Hub Integration

### Upload to Hub

```python
# Configure for Hub upload
config = DatasetConfig(
    dataset_name="my_pashto_dataset",
    repo_id="username/my-dataset",
    token="hf_your_token_here"
)

manager = DatasetManager(config)

# Generate documentation
manager._generate_dataset_card()

# Upload dataset
repo_url = manager.upload_to_hf("v1.0.0", "Initial release")
print(f"Dataset uploaded: {repo_url}")
```

### Download from Hub

```python
from datasets import load_dataset

# Load dataset from Hub
dataset = load_dataset("username/my-dataset")

# Or load specific split
train_dataset = load_dataset("username/my-dataset", split="train")
```

## Examples

Run the comprehensive examples:

```python
from dataset_manager.examples import main

# Run all examples
main()

# Run specific examples
from dataset_manager.examples import basic_usage_example, full_workflow_example

manager, dataset = basic_usage_example()
manager, dataset, splits = full_workflow_example()
```

## File Structure

```
dataset_manager/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── dataset_manager.py       # Main DatasetManager class
├── dataset_creator.py       # Dataset creation and loading
├── memory_optimizer.py      # Memory optimization
├── quality_metrics.py       # Quality metrics calculation
├── dataset_splitter.py      # Dataset splitting strategies
├── dataset_validator.py     # Data validation
├── dataset_exporter.py      # Export and HuggingFace Hub integration
├── metadata_manager.py      # Metadata and documentation
├── versioning.py            # Version control system
├── examples.py              # Usage examples
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Performance

The system is optimized for performance with:

- **Chunked Processing**: Large datasets processed in memory-efficient chunks
- **Lazy Loading**: Data loaded on-demand to minimize memory usage
- **Automatic Optimization**: Data types optimized automatically
- **Caching**: Intelligent caching of processed data
- **Parallel Processing**: Multi-threaded operations where possible

### Performance Tips

1. **Use appropriate chunk sizes** for large datasets
2. **Enable memory optimization** for datasets > 100K samples
3. **Use stratified splitting** for balanced train/val/test sets
4. **Cache intermediate results** for repeated operations
5. **Monitor memory usage** with built-in analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is available under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the examples in `examples.py`
- Review the documentation in this README

## Changelog

### Version 1.0.0
- Initial release
- Complete dataset lifecycle management
- Hugging Face Hub integration
- Memory optimization for large datasets
- Comprehensive quality metrics
- Multiple export formats
- Version control system
- Automated documentation generation