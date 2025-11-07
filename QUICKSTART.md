# Quick Start Guide

Get started with the Pashto Processing Pipeline in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

## Installation

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/tasal9/Pashto-Processing-pipeline.git
cd Pashto-Processing-pipeline

# Run the installation script
bash install.sh

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Method 2: Manual Install

```bash
# Clone the repository
git clone https://github.com/tasal9/Pashto-Processing-pipeline.git
cd Pashto-Processing-pipeline

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Verify Installation

Run the test script to verify everything is working:

```bash
python test_installation.py
```

You should see:
```
🎉 All tests passed! The pipeline is working correctly.
```

## Your First Pipeline

### Example 1: Basic Text Processing

Create a file `my_first_pipeline.py`:

```python
from pashto_pipeline import PashtoNormalizer, PashtoTokenizer

# Initialize components
normalizer = PashtoNormalizer(normalize_whitespace=True)
tokenizer = PashtoTokenizer()

# Your Pashto text
text = "سلام دنیا! دا د پښتو متن دی."

# Process the text
normalized = normalizer.normalize(text)
tokens = tokenizer.tokenize(normalized)

print(f"Original: {text}")
print(f"Normalized: {normalized}")
print(f"Tokens: {tokens}")
```

Run it:
```bash
python my_first_pipeline.py
```

### Example 2: Using the Pipeline Object

```python
from pashto_pipeline import TextProcessingPipeline, PashtoNormalizer, PashtoTokenizer

# Create a pipeline
pipeline = TextProcessingPipeline()

# Add processing steps
pipeline.add_step('normalize', PashtoNormalizer().normalize)
pipeline.add_step('tokenize', PashtoTokenizer().tokenize)

# Process text
result = pipeline.process("سلام دنیا!", verbose=True)
print(result)
```

### Example 3: Batch Processing

```python
from pashto_pipeline import TextProcessingPipeline, PashtoNormalizer

# Create pipeline
pipeline = TextProcessingPipeline()
pipeline.add_step('normalize', PashtoNormalizer().normalize)

# Process multiple texts
texts = [
    "زه په کابل کې اوسېږم.",
    "پښتو یوه ښکلې ژبه ده.",
    "نن ډېره ښه ورځ ده."
]

results = pipeline.process_batch(texts, verbose=True)

for i, result in enumerate(results, 1):
    print(f"{i}. {result}")
```

## Common Operations

### Normalize Pashto Text

```python
from pashto_pipeline import PashtoNormalizer

# Create normalizer with options
normalizer = PashtoNormalizer(
    unicode_form='NFC',           # Unicode normalization
    remove_diacritics=False,      # Keep diacritics
    normalize_digits='western',   # Convert to 0-9
    normalize_whitespace=True     # Clean whitespace
)

text = "۱۲۳   سلام"
result = normalizer.normalize(text)
print(result)  # Output: "123 سلام"
```

### Tokenize Pashto Text

```python
from pashto_pipeline import PashtoTokenizer

# Create tokenizer
tokenizer = PashtoTokenizer(preserve_punctuation=True)

# Word tokenization
tokens = tokenizer.tokenize("سلام دنیا!")
print(tokens)  # ['سلام', 'دنیا', '!']

# Sentence tokenization
sentences = tokenizer.tokenize_sentences("سلام دنیا! دا ښه ده.")
print(sentences)  # ['سلام دنیا!', 'دا ښه ده.']
```

### Remove Stopwords

```python
from pashto_pipeline.preprocessing.stopwords import StopwordsRemover

remover = StopwordsRemover()
tokens = ['زه', 'په', 'ښار', 'کې', 'یم']
filtered = remover.remove(tokens)
print(filtered)  # ['ښار', 'یم']
```

## Running Examples

The repository includes several example scripts:

```bash
# Basic usage example
python examples/basic_usage.py

# Advanced examples
python examples/python/basic_example.py
python examples/python/advanced_example.py
```

## Next Steps

1. **Read the Documentation**: Check the `docs/` folder for detailed guides
2. **Explore Examples**: Look at `examples/` for more use cases
3. **Customize**: Modify configurations to fit your needs
4. **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Configuration

Create a YAML configuration file for your pipeline:

```yaml
# config.yaml
pipeline:
  name: "my_pashto_pipeline"

processing:
  normalize:
    unicode_form: "NFC"
    normalize_digits: "western"
    normalize_whitespace: true
  
  tokenize:
    preserve_punctuation: true
```

Use it in your code:

```python
import yaml
from pashto_pipeline import TextProcessingPipeline, PashtoNormalizer, PashtoTokenizer

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create components from config
norm_config = config['processing']['normalize']
normalizer = PashtoNormalizer(**norm_config)

tok_config = config['processing']['tokenize']
tokenizer = PashtoTokenizer(**tok_config)

# Build pipeline
pipeline = TextProcessingPipeline()
pipeline.add_step('normalize', normalizer.normalize)
pipeline.add_step('tokenize', tokenizer.tokenize)
```

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Make sure the package is installed
pip install -e .

# Check installation
python -c "import pashto_pipeline; print('OK')"
```

### Unicode Errors

If you encounter encoding issues:
```python
# Ensure UTF-8 encoding when reading files
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
```

### Module Not Found

If modules are not found:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall in development mode
pip install -e .
```

## Need Help?

- **Documentation**: See `docs/` folder
- **Examples**: Check `examples/` folder
- **Issues**: [GitHub Issues](https://github.com/tasal9/Pashto-Processing-pipeline/issues)
- **FAQ**: [docs/troubleshooting/faq.md](docs/troubleshooting/faq.md)

## Summary

You now know how to:
- ✅ Install the Pashto Processing Pipeline
- ✅ Create and use processing components
- ✅ Build custom pipelines
- ✅ Process Pashto text in various ways
- ✅ Configure your pipeline

Happy processing! 🎉

---

**Next**: Check out the [Usage Tutorials](docs/guides/usage_tutorials.md) for more advanced examples.
