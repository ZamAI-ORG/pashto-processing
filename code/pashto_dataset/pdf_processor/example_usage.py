#!/usr/bin/env python3
"""
Example Usage Script for Pashto PDF Processing Module

This script demonstrates how to use the Pashto PDF processing module
with various scenarios and configurations.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from pdf_processor import (
        PashtoPDFProcessor, 
        PashtoTextUtils,
        OCRHandler,
        MetadataExtractor,
        QualityAssessor
    )
    from config_utils import (
        ProcessingConfig, 
        ConfigManager, 
        FileProcessor,
        PashtoValidationUtils,
        setup_logging,
        get_system_info
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please install required dependencies:")
    print("pip install PyMuPDF pytesseract Pillow opencv-python numpy")
    MODULES_AVAILABLE = False


def example_basic_processing():
    """Example: Basic PDF processing."""
    print("=" * 60)
    print("EXAMPLE 1: Basic PDF Processing")
    print("=" * 60)
    
    if not MODULES_AVAILABLE:
        print("Modules not available. Skipping example.")
        return
    
    # Initialize processor with default settings
    processor = PashtoPDFProcessor(
        ocr_enabled=True,
        ocr_languages="eng+pus"
    )
    
    # Example PDF path (you would replace with actual file)
    pdf_path = "sample_document.pdf"  # Placeholder
    
    if not os.path.exists(pdf_path):
        print(f"Sample PDF not found: {pdf_path}")
        print("Creating a mock example instead...")
        
        # Create mock result for demonstration
        result = {
            'pdf_path': pdf_path,
            'total_pages': 3,
            'processed_pages': 3,
            'full_text': "دا یو ښه ازموینه دی ډول لکه ړ. دا د دویمې پاڼې مینه ده. دا د درییمې پاڼې مینه ده.",
            'cleaned_text': "دا یو ښه ازموینه دی ډول لکه ړ. دا د دویمې پاڼې مینه ده. دا د درییمې پاڼې مینه ده.",
            'normalized_text': "دا یو ښه ازموینه دی ډول لکه ړ. دا د دویمې پاڼې مینه ده. دا د درییمې پاڼې مینه ده.",
            'pages': [
                {
                    'page_number': 1,
                    'text': "دا یو ښه ازموینه دی ډول لکه ړ",
                    'extraction_method': 'direct',
                    'confidence': 0.95
                },
                {
                    'page_number': 2,
                    'text': "دا د دویمې پاڼې مینه ده",
                    'extraction_method': 'direct',
                    'confidence': 0.92
                },
                {
                    'page_number': 3,
                    'text': "دا د درییمې پاڼې مینه ده",
                    'extraction_method': 'ocr',
                    'confidence': 0.88
                }
            ],
            'metadata': {
                'pdf_metadata': {
                    'title': 'Sample Pashto Document',
                    'author': 'Test Author'
                },
                'content_metadata': {
                    'document_type': 'article',
                    'potential_title': 'Sample Pashto Document'
                }
            }
        }
    else:
        # Process actual PDF
        output_dir = "output/basic_example"
        os.makedirs(output_dir, exist_ok=True)
        
        result = processor.process_pdf(
            pdf_path=pdf_path,
            output_dir=output_dir,
            extract_metadata=True,
            assess_quality=True
        )
    
    # Display results
    if result.get('success', True):
        print("✓ Processing successful!")
        print(f"Pages processed: {result['processed_pages']}/{result['total_pages']}")
        
        # Show text preview
        preview_text = result.get('full_text', '')[:200]
        print(f"Text preview: {preview_text}...")
        
        # Show quality assessment
        if 'quality_assessment' in result:
            quality = result['quality_assessment']
            print(f"Quality score: {quality['overall_score']:.2f}")
            print(f"Quality grade: {quality['quality_grade']}")
        
        # Show extraction methods
        extraction_methods = {}
        for page in result.get('pages', []):
            method = page.get('extraction_method', 'unknown')
            extraction_methods[method] = extraction_methods.get(method, 0) + 1
        
        print("Extraction methods used:")
        for method, count in extraction_methods.items():
            print(f"  {method}: {count} pages")
    
    else:
        print(f"✗ Processing failed: {result.get('error', 'Unknown error')}")


def example_advanced_configuration():
    """Example: Advanced configuration and settings."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Advanced Configuration")
    print("=" * 60)
    
    if not MODULES_AVAILABLE:
        print("Modules not available. Skipping example.")
        return
    
    # Create custom configuration
    config = ProcessingConfig(
        ocr_enabled=True,
        ocr_languages="eng+pus",
        ocr_dpi=400,  # Higher DPI for better OCR
        quality_threshold=0.7,  # Higher quality threshold
        save_raw_text=True,
        save_cleaned_text=True,
        save_normalized_text=True,
        save_metadata=True,
        save_quality_report=True,
        output_encoding="utf-8"
    )
    
    print("Custom configuration created:")
    print(f"  OCR enabled: {config.ocr_enabled}")
    print(f"  OCR languages: {config.ocr_languages}")
    print(f"  OCR DPI: {config.ocr_dpi}")
    print(f"  Quality threshold: {config.quality_threshold}")
    print(f"  Output encoding: {config.output_encoding}")
    
    # Save configuration
    config_manager = ConfigManager()
    config_path = "advanced_config.json"
    config_manager.save_config(config, config_path)
    print(f"\nConfiguration saved to: {config_path}")
    
    # Validate configuration
    errors = config_manager.validate_config(config)
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Configuration is valid")
    
    # Create processor with custom settings
    processor = PashtoPDFProcessor(
        ocr_enabled=config.ocr_enabled,
        ocr_languages=config.ocr_languages
    )
    
    print("\nProcessor initialized with custom configuration")


def example_text_analysis():
    """Example: Text analysis and processing."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Text Analysis and Processing")
    print("=" * 60)
    
    if not MODULES_AVAILABLE:
        print("Modules not available. Skipping example.")
        return
    
    utils = PashtoTextUtils()
    
    # Sample Pashto text for analysis
    sample_texts = [
        "دا یو ښه ازموینه دی ډول لکه ړ. زموږ د ښوونې هدف دا دی چې زموږ خپلوان زیات معلومات واخلي.",
        "په دغه کال کې موږ ډېر کارونه ترسره کړل. دا د ټولنې د ښه والی لپاره ډېر ګټور دی.",
        "زموږ د ځانګړي ملګري احمد په کال ۱۴۰۲ کې زیږیدلی او اوس د ښوونځي ښوونکی دی."
    ]
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nText Sample {i}:")
        print(f"Original: {text}")
        
        # Text cleaning
        cleaned = utils.clean_text(text)
        print(f"Cleaned: {cleaned}")
        
        # Normalization
        normalized = utils.normalize_pashto(text)
        print(f"Normalized: {normalized}")
        
        # Sentence extraction
        sentences = utils.extract_sentences(text)
        print(f"Sentences ({len(sentences)}): {sentences}")
        
        # Word extraction
        words = utils.extract_words(text)
        print(f"Words ({len(words)}): {words[:10]}..." if len(words) > 10 else f"Words: {words}")
        
        # Word frequency
        freq = utils.get_word_frequency(text)
        print(f"Top words: {sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]}")
        
        # Text statistics
        stats = utils.get_text_statistics(text)
        print(f"Statistics: Pashto ratio: {stats['pashto_ratio']:.2%}, Words: {stats['total_words']}")


def example_batch_processing():
    """Example: Batch processing multiple documents."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Batch Processing")
    print("=" * 60)
    
    if not MODULES_AVAILABLE:
        print("Modules not available. Skipping example.")
        return
    
    # Create sample PDF directory structure
    sample_dir = "sample_pdfs"
    os.makedirs(sample_dir, exist_ok=True)
    
    processor = PashtoPDFProcessor(
        ocr_enabled=True,
        ocr_languages="eng+pus"
    )
    
    # Simulate batch processing (since we don't have real PDFs)
    print("Simulating batch processing...")
    
    # Create mock results for multiple documents
    mock_results = [
        {
            'pdf_path': f'{sample_dir}/document1.pdf',
            'total_pages': 5,
            'processed_pages': 5,
            'quality_assessment': {'overall_score': 0.85, 'quality_grade': 'excellent'},
            'success': True
        },
        {
            'pdf_path': f'{sample_dir}/document2.pdf',
            'total_pages': 3,
            'processed_pages': 3,
            'quality_assessment': {'overall_score': 0.72, 'quality_grade': 'good'},
            'success': True
        },
        {
            'pdf_path': f'{sample_dir}/document3.pdf',
            'error': 'File not found',
            'success': False
        }
    ]
    
    print("Batch processing results:")
    for result in mock_results:
        if result.get('success', True):
            score = result.get('quality_assessment', {}).get('overall_score', 0)
            grade = result.get('quality_assessment', {}).get('quality_grade', 'unknown')
            print(f"✓ {Path(result['pdf_path']).name} - Score: {score:.2f} ({grade})")
        else:
            print(f"✗ {Path(result['pdf_path']).name} - Error: {result.get('error', 'Unknown')}")
    
    # Show statistics
    successful = sum(1 for r in mock_results if r.get('success', True))
    total = len(mock_results)
    print(f"\nSuccess rate: {successful}/{total} ({successful/total*100:.1f}%)")


def example_quality_assessment():
    """Example: Quality assessment and comparison."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Quality Assessment")
    print("=" * 60)
    
    if not MODULES_AVAILABLE:
        print("Modules not available. Skipping example.")
        return
    
    assessor = QualityAssessor()
    
    # Create mock documents with different quality levels
    high_quality_result = {
        'full_text': "دا یو ښه ازموینه دی ډول لکه ړ. دا مینه د پوهې وړتیا لري. زموږ د ښوونې نظام ډېر ښه دی.",
        'cleaned_text': "دا یو ښه ازموینه دی ډول لکه ړ. دا مینه د پوهې وړتیا لري. زموږ د ښوونې نظام ډېر ښه دی.",
        'normalized_text': "دا یو ښه ازموینه دی ډول لکه ړ. دا مینه د پوهې وړتیا لري. زموږ د ښوونې نظام ډېر ښه دی.",
        'total_pages': 3,
        'processed_pages': 3,
        'pages': [
            {'extraction_method': 'direct', 'confidence': 0.95},
            {'extraction_method': 'direct', 'confidence': 0.93},
            {'extraction_method': 'direct', 'confidence': 0.91}
        ]
    }
    
    low_quality_result = {
        'full_text': "abc def ghi jkl 123 456 789",
        'cleaned_text': "abc def ghi jkl 123 456 789",
        'normalized_text': "abc def ghi jkl 123 456 789",
        'total_pages': 3,
        'processed_pages': 2,
        'pages': [
            {'extraction_method': 'ocr', 'confidence': 0.45},
            {'extraction_method': 'ocr', 'confidence': 0.52},
            {'extraction_method': 'error', 'confidence': 0.0}
        ]
    }
    
    # Assess quality
    print("Assessing document quality...")
    
    high_quality_assessment = assessor.assess_document(high_quality_result)
    low_quality_assessment = assessor.assess_document(low_quality_result)
    
    print(f"\nHigh Quality Document:")
    print(f"  Overall Score: {high_quality_assessment['overall_score']:.2f}")
    print(f"  Quality Grade: {high_quality_assessment['quality_grade']}")
    print(f"  Pashto Content: High")
    
    print(f"\nLow Quality Document:")
    print(f"  Overall Score: {low_quality_assessment['overall_score']:.2f}")
    print(f"  Quality Grade: {low_quality_assessment['quality_grade']}")
    print(f"  Pashto Content: Low")
    
    # Compare
    comparison = assessor.compare_extraction_quality(high_quality_result, low_quality_result)
    print(f"\nQuality Comparison:")
    print(f"  High Quality Score: {comparison['result1_score']:.2f}")
    print(f"  Low Quality Score: {comparison['result2_score']:.2f}")
    print(f"  Difference: {comparison['quality_improvement']:.2f}")


def example_system_info():
    """Example: System information and validation."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: System Information")
    print("=" * 60)
    
    if not MODULES_AVAILABLE:
        print("Modules not available. Skipping example.")
        return
    
    # Get system information
    system_info = get_system_info()
    
    print("System Information:")
    print(f"  Platform: {system_info.get('platform', 'Unknown')}")
    print(f"  Python Version: {system_info.get('python_version', 'Unknown')}")
    
    print("\nDependencies Status:")
    for dep, status in system_info.get('dependencies', {}).items():
        status_symbol = "✓" if status == "available" else "✗"
        print(f"  {status_symbol} {dep}: {status}")
    
    # Check Tesseract
    if 'tesseract' in system_info:
        tesseract_info = system_info['tesseract']
        if 'error' not in tesseract_info:
            print(f"\nTesseract Information:")
            print(f"  Version: {tesseract_info.get('tesseract_version', 'Unknown')}")
            print(f"  Available Languages: {tesseract_info.get('available_languages', [])}")
            print(f"  Pashto Available: {tesseract_info.get('is_pashto_available', False)}")
        else:
            print(f"\nTesseract Error: {tesseract_info['error']}")
    
    # Validate Pashto content
    print("\nPashto Content Validation:")
    test_texts = [
        "دا یو ښه ازموینه دی",
        "This is English text",
        "Mixed text دا English with پاستو"
    ]
    
    for text in test_texts:
        is_valid = PashtoValidationUtils.is_valid_pashto_text(text, min_ratio=0.3)
        status = "✓" if is_valid else "✗"
        print(f"  {status} '{text[:30]}...' - {'Valid' if is_valid else 'Invalid'} Pashto")


def main():
    """Run all examples."""
    print("Pashto PDF Processing Module - Usage Examples")
    print("=" * 60)
    
    # Setup logging
    setup_logging(level="INFO")
    
    # Check system information first
    example_system_info()
    
    # Run examples
    try:
        example_basic_processing()
        example_advanced_configuration()
        example_text_analysis()
        example_batch_processing()
        example_quality_assessment()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
        print("\nNext Steps:")
        print("1. Install required dependencies: pip install -r requirements.txt")
        print("2. Install Tesseract OCR with Pashto support")
        print("3. Place your Pashto PDF files in a directory")
        print("4. Run: processor.batch_process('your_pdf_dir/', 'output_dir/')")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()