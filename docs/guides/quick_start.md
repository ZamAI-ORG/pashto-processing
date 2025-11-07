# Quick Start Tutorial

Get up and running with the Pashto Dataset Pipeline in under 10 minutes! This tutorial will guide you through the essential steps to process your first Pashto dataset.

## 🎯 What You'll Learn

- How to configure the pipeline
- Process a sample dataset
- Understand the output format
- Validate results
- Use common commands

## 📋 Prerequisites

- [Installation completed](installation.md)
- Basic familiarity with command line
- Sample Pashto text data (or we'll generate some)

## 🚀 Step 1: Verify Installation

First, let's make sure everything is installed correctly:

```bash
# Check if pipeline is available
pashto-pipeline --version

# Should output something like:
# pashto-dataset-pipeline version 1.0.0
```

## 📂 Step 2: Create a Project Structure

```bash
# Create a new project directory
mkdir my_first_project
cd my_first_project

# Create the standard directory structure
mkdir -p {data/raw,data/processed,config,logs,scripts}

# Your project should look like:
# my_first_project/
# ├── data/
# │   ├── raw/          # Input data
# │   └── processed/    # Output data
# ├── config/           # Configuration files
# ├── logs/            # Log files
# └── scripts/         # Custom scripts
```

## ⚙️ Step 3: Create Basic Configuration

Create a basic configuration file:

**config/basic_config.yaml**
```yaml
# Basic pipeline configuration
pipeline:
  name: "My First Pashto Pipeline"
  version: "1.0"
  description: "Basic Pashto text processing"

# Input configuration
input:
  data_directory: "data/raw"
  supported_formats: ["txt", "json", "csv"]
  encoding: "utf-8"
  
# Processing configuration
processing:
  normalize_text: true
  remove_duplicates: true
  filter_min_length: 10
  filter_max_length: 10000
  
# Output configuration
output:
  data_directory: "data/processed"
  format: "json"
  include_metadata: true
  compress_output: false

# Logging configuration
logging:
  level: "INFO"
  file: "logs/pipeline.log"
  console: true

# Quality settings
quality:
  min_text_quality: 0.7
  require_pashto: true
  max_noise_ratio: 0.3
```

## 📝 Step 4: Prepare Sample Data

Let's create some sample Pashto text data:

**data/raw/sample_pashto.txt**
```
زموږ ژبه د پښتو ژبه ده.
دا ښه ژبه ده چې موږ یې څیړو.
پښتو ژبه د افغانستان د خلکو ژبه ده.
موږ زموږ د ژبې څیړنه کوو.
دا یوه ښه څیړنه ده.
```

```bash
# Create the sample data file
cat > data/raw/sample_pashto.txt << 'EOF'
زموږ ژبه د پښتو ژبه ده.
دا ښه ژبه ده چې موږ یې څیړو.
پښتو ژبه د افغانستان د خلکو ژبه ده.
موږ زموږ د ژبې څیړنه کوو.
دا یوه ښه څیړنه ده.
EOF
```

## 🏃 Step 5: Process the Data

Now let's run the pipeline:

```bash
# Process the data using our configuration
pashto-pipeline process \
  --input data/raw/ \
  --output data/processed/ \
  --config config/basic_config.yaml

# You should see output similar to:
# INFO: Starting pipeline execution...
# INFO: Found 1 input files
# INFO: Processing: sample_pashto.txt
# INFO: Normalizing text...
# INFO: Removing duplicates...
# INFO: Quality filtering...
# INFO: Writing output...
# INFO: Pipeline completed successfully!
# INFO: Processed 5 sentences, 4 unique, quality score: 0.85
```

## 📊 Step 6: Examine the Results

Let's look at what was created:

```bash
# List output files
ls -la data/processed/

# Examine the processed output
cat data/processed/processed_data.json
```

You should see output similar to this:

```json
{
  "pipeline_info": {
    "name": "My First Pashto Pipeline",
    "version": "1.0",
    "timestamp": "2025-11-06T21:41:41Z",
    "input_files": ["sample_pashto.txt"],
    "processing_time": "0.234s"
  },
  "statistics": {
    "total_input": 5,
    "total_output": 4,
    "duplicates_removed": 1,
    "quality_score": 0.85
  },
  "data": [
    {
      "text": "زموږ ژبه د پښتو ژبه ده.",
      "metadata": {
        "source_file": "sample_pashto.txt",
        "line_number": 1,
        "character_count": 22,
        "word_count": 7,
        "quality_score": 0.92
      }
    },
    {
      "text": "دا ښه ژبه ده چې موږ یې څیړو.",
      "metadata": {
        "source_file": "sample_pashto.txt",
        "line_number": 2,
        "character_count": 25,
        "word_count": 8,
        "quality_score": 0.89
      }
    },
    {
      "text": "پښتو ژبه د افغانستان د خلکو ژبه ده.",
      "metadata": {
        "source_file": "sample_pashto.txt",
        "line_number": 3,
        "character_count": 30,
        "word_count": 9,
        "quality_score": 0.91
      }
    },
    {
      "text": "موږ زموږ د ژبې څیړنه کوو.",
      "metadata": {
        "source_file": "sample_pashto.txt",
        "line_number": 4,
        "character_count": 23,
        "word_count": 8,
        "quality_score": 0.87
      }
    }
  ]
}
```

## 🔍 Step 7: Quality Check

Let's validate the quality of our processed data:

```bash
# Run quality assessment
pashto-pipeline quality-check \
  --input data/processed/ \
  --report

# Sample output:
# Quality Report
# ==============
# Total sentences: 4
# Average quality score: 0.898
# Pashto script detection: 100%
# Character distribution: Good
# Length distribution: Good
# No issues detected
```

## 📈 Step 8: Generate Statistics

```bash
# Generate detailed statistics
pashto-pipeline stats \
  --input data/processed/ \
  --detailed

# Output:
# Dataset Statistics
# =================
# 
# Basic Stats:
#   - Total records: 4
#   - Total characters: 100
#   - Average characters per record: 25.0
#   - Character range: 22-30
# 
# Language Stats:
#   - Pashto content: 100%
#   - Arabic script: 100%
#   - Latin script: 0%
# 
# Quality Metrics:
#   - High quality (≥0.8): 4 (100%)
#   - Medium quality (0.5-0.8): 0 (0%)
#   - Low quality (<0.5): 0 (0%)
```

## 🐍 Step 9: Python API Example

Now let's try using the Python API:

**scripts/example_script.py**
```python
#!/usr/bin/env python3
"""
Example script using the Pashto Dataset Pipeline Python API
"""

from pashto_pipeline import Pipeline, Config
import json

def main():
    # Load configuration
    config = Config.from_file('config/basic_config.yaml')
    
    # Create pipeline instance
    pipeline = Pipeline(config)
    
    # Process data
    print("Processing data with Python API...")
    result = pipeline.run('data/raw/', 'data/processed/')
    
    # Display results
    print(f"\nResults:")
    print(f"- Total processed: {result.total_processed}")
    print(f"- Quality score: {result.quality_score:.3f}")
    print(f"- Processing time: {result.processing_time:.2f}s")
    
    # Load and display sample output
    with open('data/processed/processed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\nFirst record:")
    print(f"Text: {data['data'][0]['text']}")
    print(f"Quality: {data['data'][0]['metadata']['quality_score']}")

if __name__ == "__main__":
    main()
```

```bash
# Run the Python script
python scripts/example_script.py
```

## 🔧 Step 10: Common Customizations

### Filtering Options
```bash
# Process with specific filters
pashto-pipeline process \
  --input data/raw/ \
  --output data/processed/ \
  --config config/basic_config.yaml \
  --min-length 15 \
  --max-length 100 \
  --min-quality 0.8
```

### Output Formats
```bash
# Export to CSV
pashto-pipeline export \
  --input data/processed/ \
  --output data/export/ \
  --format csv

# Export to XML
pashto-pipeline export \
  --input data/processed/ \
  --output data/export/ \
  --format xml
```

### Batch Processing
```bash
# Process multiple directories
pashto-pipeline batch-process \
  --input-dirs data/source1/,data/source2/,data/source3/ \
  --output-dir data/batch_output/ \
  --config config/batch_config.yaml
```

## ✅ Step 11: Validation and Testing

```bash
# Validate your configuration
pashto-pipeline validate-config --file config/basic_config.yaml

# Test with sample data
pashto-pipeline test-data --generate --output test_data/
pashto-pipeline process --input test_data/ --output test_output/ --config config/basic_config.yaml

# Check pipeline integrity
pashto-pipeline check-integrity --input data/processed/
```

## 📚 What's Next?

Congratulations! You've successfully processed your first Pashto dataset. Here's what you can explore next:

### Advanced Tutorials
- [Configuration Guide](configuration.md) - Learn about all configuration options
- [Usage Tutorials](usage_tutorials.md) - Step-by-step guides for common tasks
- [Best Practices](best_practices.md) - Professional guidelines for production use

### Specific Use Cases
- **Web Scraping**: Collect Pashto text from websites
- **Social Media**: Process Twitter/Facebook data
- **Document Processing**: Handle PDFs and other document formats
- **Database Integration**: Connect to SQL/NoSQL databases

### API Reference
- [Python API](api/core.md) - Detailed API documentation
- [Command Line Reference](api/cli.md) - Complete CLI reference
- [Configuration Reference](api/config.md) - All configuration options

### Optimization
- [Performance Tuning](troubleshooting/performance.md) - Optimize for large datasets
- [Memory Management](troubleshooting/common_issues.md) - Handle memory constraints
- [Parallel Processing](troubleshooting/performance.md) - Speed up processing

## 🆘 Troubleshooting

If you encountered any issues during this tutorial:

1. **Check the logs**: Look in `logs/pipeline.log` for detailed error messages
2. **Verify configuration**: Run `pashto-pipeline validate-config`
3. **Test with minimal data**: Try with a single small file
4. **Check permissions**: Ensure read/write access to directories

### Common Quick Fixes

```bash
# Fix encoding issues
pashto-pipeline process --input data/raw/ --output data/processed/ --encoding utf-8

# Handle large files
pashto-pipeline process --input data/raw/ --output data/processed/ --batch-size 100

# Debug mode
pashto-pipeline process --input data/raw/ --output data/processed/ --log-level DEBUG
```

## 🎉 Summary

You now have:
- ✅ A working Pashto dataset pipeline
- ✅ Processed sample data with quality metrics
- ✅ Understanding of basic configuration
- ✅ Knowledge of common commands
- ✅ Python API integration skills

**Ready for more?** Check out the [Usage Tutorials](usage_tutorials.md) for advanced scenarios and the [API Reference](api/README.md) for detailed documentation.