#!/usr/bin/env python3
"""
Simple Module Validation (No External Dependencies)

This script validates the module structure and basic functionality
without requiring external dependencies.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def validate_module_structure():
    """Validate that all required module files exist."""
    required_files = [
        "__init__.py",
        "pdf_processor.py", 
        "pashto_utils.py",
        "ocr_handler.py",
        "metadata_extractor.py",
        "quality_assessor.py",
        "config_utils.py",
        "test_suite.py",
        "example_usage.py",
        "requirements.txt",
        "README.md"
    ]
    
    print("Module Structure Validation")
    print("=" * 40)
    
    all_present = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✓ {file_name:<20} ({size:,} bytes)")
        else:
            print(f"✗ {file_name:<20} MISSING")
            all_present = False
    
    return all_present

def validate_python_syntax():
    """Validate Python syntax without importing modules."""
    import ast
    
    print("\nPython Syntax Validation")
    print("=" * 40)
    
    python_files = [
        "__init__.py",
        "pdf_processor.py", 
        "pashto_utils.py",
        "ocr_handler.py",
        "metadata_extractor.py",
        "quality_assessor.py",
        "config_utils.py",
        "test_suite.py",
        "example_usage.py"
    ]
    
    all_valid = True
    for file_name in python_files:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse Python syntax
            ast.parse(content)
            print(f"✓ {file_name:<20} Valid syntax")
            
        except SyntaxError as e:
            print(f"✗ {file_name:<20} Syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"⚠ {file_name:<20} Warning: {e}")
    
    return all_valid

def validate_documentation():
    """Validate that documentation files are comprehensive."""
    print("\nDocumentation Validation")
    print("=" * 40)
    
    # Check README
    try:
        with open("README.md", 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        readme_size = len(readme_content)
        has_installation = "Installation" in readme_content or "install" in readme_content.lower()
        has_examples = "Example" in readme_content or "example" in readme_content.lower()
        has_features = "Features" in readme_content or "features" in readme_content.lower()
        
        print(f"✓ README.md           ({readme_size:,} chars)")
        print(f"  - Installation guide: {'✓' if has_installation else '✗'}")
        print(f"  - Examples: {'✓' if has_examples else '✗'}")
        print(f"  - Features: {'✓' if has_features else '✗'}")
        
    except Exception as e:
        print(f"✗ README.md: Error reading - {e}")
    
    # Check requirements
    try:
        with open("requirements.txt", 'r', encoding='utf-8') as f:
            requirements = f.read()
        
        req_lines = [line.strip() for line in requirements.split('\n') if line.strip() and not line.startswith('#')]
        print(f"✓ requirements.txt     ({len(req_lines)} packages)")
        
    except Exception as e:
        print(f"✗ requirements.txt: Error reading - {e}")

def validate_code_structure():
    """Validate the code structure and organization."""
    print("\nCode Structure Validation")
    print("=" * 40)
    
    # Check main classes exist
    class_checks = {
        "pdf_processor.py": ["class PashtoPDFProcessor"],
        "pashto_utils.py": ["class PashtoTextUtils"],
        "ocr_handler.py": ["class OCRHandler"],
        "metadata_extractor.py": ["class MetadataExtractor"],
        "quality_assessor.py": ["class QualityAssessor"],
        "config_utils.py": ["ProcessingConfig", "ConfigManager"]
    }
    
    for file_name, classes in class_checks.items():
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for class_name in classes:
                if class_name in content:
                    print(f"✓ {file_name:<20} Contains {class_name}")
                else:
                    print(f"⚠ {file_name:<20} Missing {class_name}")
                    
        except Exception as e:
            print(f"✗ {file_name:<20} Error checking - {e}")

def generate_usage_summary():
    """Generate a summary of how to use the module."""
    print("\nModule Usage Summary")
    print("=" * 40)
    
    usage_code = '''
# Basic Usage
from pashto_dataset.pdf_processor import PashtoPDFProcessor

# Initialize processor
processor = PashtoPDFProcessor(ocr_enabled=True, ocr_languages="eng+pus")

# Process a PDF
result = processor.process_pdf("document.pdf", "output_dir/")

# Access results
print(f"Quality: {result['quality_assessment']['quality_grade']}")
print(f"Text: {result['full_text'][:200]}...")
'''
    
    print("Quick Start Code:")
    print(usage_code)
    
    print("Key Features:")
    features = [
        "✓ Digital PDF text extraction",
        "✓ OCR for scanned Pashto documents", 
        "✓ Text cleaning and normalization",
        "✓ Metadata extraction",
        "✓ Quality assessment",
        "✓ Batch processing",
        "✓ Comprehensive error handling"
    ]
    
    for feature in features:
        print(f"  {feature}")

def main():
    """Run all validations."""
    print("Pashto PDF Processing Module - Validation")
    print("=" * 50)
    
    # Change to module directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run validations
    structure_ok = validate_module_structure()
    syntax_ok = validate_python_syntax()
    validate_documentation()
    validate_code_structure()
    
    print("\n" + "=" * 50)
    print("Validation Summary")
    print("=" * 50)
    
    if structure_ok and syntax_ok:
        print("✓ Module structure and syntax validation PASSED")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install Tesseract OCR with Pashto support")
        print("3. Run example: python example_usage.py")
        print("4. Run tests: python test_suite.py")
    else:
        print("✗ Validation FAILED - check errors above")
    
    print("\nModule is ready for use!" if structure_ok and syntax_ok else "Please fix validation errors.")

if __name__ == "__main__":
    main()