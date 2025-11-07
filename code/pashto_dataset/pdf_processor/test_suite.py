"""
Test Suite and Example Usage for Pashto PDF Processing Module

This module provides comprehensive tests and examples for the Pashto PDF
processing functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image

# Import modules to test
try:
    from .pdf_processor import PashtoPDFProcessor
    from .pashto_utils import PashtoTextUtils
    from .ocr_handler import OCRHandler
    from .metadata_extractor import MetadataExtractor
    from .quality_assessor import QualityAssessor
    from .config_utils import ProcessingConfig, ConfigManager, PashtoValidationUtils
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available for testing: {e}")
    IMPORTS_AVAILABLE = False


class TestPashtoTextUtils(unittest.TestCase):
    """Test Pashto text utilities."""
    
    def setUp(self):
        if not IMPORTS_AVAILABLE:
            self.skipTest("Modules not available")
        self.utils = PashtoTextUtils()
    
    def test_pashto_char_detection(self):
        """Test Pashto character detection."""
        # Test Pashto characters
        self.assertTrue(self.utils._is_pashto_char('ډ'))  # Daal
        self.assertTrue(self.utils._is_pashto_char('ړ'))  # Raal
        self.assertTrue(self.utils._is_pashto_char('ږ'))  # Gaaf
        
        # Test non-Pashto characters
        self.assertFalse(self.utils._is_pashto_char('a'))
        self.assertFalse(self.utils._is_pashto_char('1'))
        self.assertFalse(self.utils._is_pashto_char(' '))
    
    def test_encoding_detection(self):
        """Test text encoding detection."""
        # Test Pashto text
        pashto_text = "دا یو ازموینه دی ډول لکه ړ"
        result = self.utils.detect_encoding(pashto_text)
        self.assertEqual(result, 'pashto')
        
        # Test English text
        english_text = "This is a test"
        result = self.utils.detect_encoding(english_text)
        self.assertEqual(result, 'english')
        
        # Test empty text
        result = self.utils.detect_encoding("")
        self.assertEqual(result, 'unknown')
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        # Test noise removal
        dirty_text = "  This   is   a    test\n\n\nwith extra    spaces   "
        cleaned = self.utils.clean_text(dirty_text)
        
        # Check for single spaces and normalized newlines
        self.assertNotIn("  ", cleaned)  # No double spaces
        self.assertIn(" ", cleaned)  # Has single spaces
    
    def test_normalization(self):
        """Test Pashto text normalization."""
        # Test with mixed characters
        mixed_text = "دا  یو  ازموینه  دی"
        normalized = self.utils.normalize_pashto(mixed_text)
        
        # Check for proper spacing
        self.assertNotIn("  ", normalized)  # No double spaces
    
    def test_sentence_extraction(self):
        """Test sentence extraction."""
        text = "دا جمله لومړۍ ده. دا دویمه جمله ده! دا درییمه جمله ده؟"
        sentences = self.utils.extract_sentences(text)
        
        self.assertGreaterEqual(len(sentences), 3)
        self.assertTrue(all(len(s) > 5 for s in sentences))
    
    def test_word_extraction(self):
        """Test word extraction."""
        text = "دا یو ازموینه دی ډول لکه ړ"
        words = self.utils.extract_words(text)
        
        self.assertGreater(len(words), 0)
        self.assertTrue(all(len(w) > 1 for w in words))  # No single characters


class TestOCRHandler(unittest.TestCase):
    """Test OCR functionality."""
    
    def setUp(self):
        if not IMPORTS_AVAILABLE:
            self.skipTest("Modules not available")
        self.ocr = OCRHandler()
    
    @patch('pytesseract.image_to_data')
    def test_ocr_mock(self, mock_tesseract):
        """Test OCR with mocked Tesseract."""
        # Mock Tesseract response
        mock_tesseract.return_value = {
            'text': ['test', 'pashto', 'text'],
            'conf': [95, 87, 92]
        }
        
        # Create dummy image
        dummy_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        result = self.ocr._perform_ocr(dummy_image)
        
        self.assertIn('text', result)
        self.assertIn('confidence', result)
        self.assertGreater(result['confidence'], 0)
    
    def test_preprocessing(self):
        """Test image preprocessing."""
        # Create dummy image
        dummy_image = np.ones((50, 50, 3), dtype=np.uint8) * 128
        
        # Test preprocessing
        processed = self.ocr._preprocess_image(dummy_image)
        
        # Check that preprocessing returns an image
        self.assertEqual(processed.shape[2], 3)  # RGB image


class TestMetadataExtractor(unittest.TestCase):
    """Test metadata extraction."""
    
    def setUp(self):
        if not IMPORTS_AVAILABLE:
            self.skipTest("Modules not available")
        self.extractor = MetadataExtractor()
    
    def test_title_extraction(self):
        """Test title extraction patterns."""
        # Test with explicit title
        text = "Title: دا یو ازموینه دی\nSome content here"
        title = self.extractor._extract_potential_title(text)
        
        self.assertIsNotNone(title)
        self.assertIn("ازموینه", title)
    
    def test_author_extraction(self):
        """Test author extraction."""
        # Test with author indicator
        text = "Author: احمد محمد\nSome content"
        author = self.extractor._extract_potential_author(text)
        
        self.assertIsNotNone(author)
    
    def test_date_extraction(self):
        """Test date extraction."""
        # Test with various date formats
        text1 = "2023-12-25"
        text2 = "25/12/2023"
        
        date1 = self.extractor._extract_potential_date(text1)
        date2 = self.extractor._extract_potential_date(text2)
        
        # At least one should be detected
        self.assertTrue(date1 is not None or date2 is not None)


class TestQualityAssessor(unittest.TestCase):
    """Test quality assessment functionality."""
    
    def setUp(self):
        if not IMPORTS_AVAILABLE:
            self.skipTest("Modules not available")
        self.assessor = QualityAssessor()
    
    def test_basic_assessment(self):
        """Test basic quality assessment."""
        # Create mock result
        mock_result = {
            'full_text': "دا یو ښه ازموینه دی ډول لکه ړ",
            'cleaned_text': "دا یو ښه ازموینه دی",
            'normalized_text': "دا یو ښه ازموینه دی",
            'total_pages': 1,
            'processed_pages': 1,
            'pages': [{
                'text': "دا یو ښه ازموینه دی",
                'extraction_method': 'direct',
                'confidence': 0.9
            }]
        }
        
        assessment = self.assessor.assess_document(mock_result)
        
        self.assertIn('overall_score', assessment)
        self.assertIn('quality_grade', assessment)
        self.assertIn('metrics', assessment)
        
        # Check score range
        self.assertGreaterEqual(assessment['overall_score'], 0.0)
        self.assertLessEqual(assessment['overall_score'], 1.0)
    
    def test_quality_grading(self):
        """Test quality grade determination."""
        # Test different score thresholds
        self.assertEqual(self.assessor._determine_quality_grade(0.9), 'excellent')
        self.assertEqual(self.assessor._determine_quality_grade(0.7), 'good')
        self.assertEqual(self.assessor._determine_quality_grade(0.5), 'acceptable')
        self.assertEqual(self.assessor._determine_quality_grade(0.3), 'poor')
        self.assertEqual(self.assessor._determine_quality_grade(0.1), 'failed')


class TestConfigUtils(unittest.TestCase):
    """Test configuration utilities."""
    
    def setUp(self):
        if not IMPORTS_AVAILABLE:
            self.skipTest("Modules not available")
    
    def test_processing_config(self):
        """Test ProcessingConfig creation."""
        config = ProcessingConfig(
            ocr_enabled=True,
            ocr_languages="eng+pus",
            quality_threshold=0.7
        )
        
        self.assertTrue(config.ocr_enabled)
        self.assertEqual(config.ocr_languages, "eng+pus")
        self.assertEqual(config.quality_threshold, 0.7)
    
    def test_config_manager(self):
        """Test configuration management."""
        config_manager = ConfigManager()
        
        # Test default config creation
        config = config_manager.load_config()
        self.assertIsInstance(config, ProcessingConfig)
        
        # Test validation
        errors = config_manager.validate_config(config)
        self.assertIsInstance(errors, list)
    
    def test_pashto_validation(self):
        """Test Pashto validation utilities."""
        # Test valid Pashto text
        valid_text = "دا یو ښه ازموینه دی ډول لکه ړ"
        result = PashtoValidationUtils.is_valid_pashto_text(valid_text, min_ratio=0.3)
        
        self.assertTrue(result)
        
        # Test invalid text
        invalid_text = "This is English text"
        result = PashtoValidationUtils.is_valid_pashto_text(invalid_text, min_ratio=0.3)
        
        self.assertFalse(result)


class TestPashtoPDFProcessor(unittest.TestCase):
    """Test main PDF processor functionality."""
    
    def setUp(self):
        if not IMPORTS_AVAILABLE:
            self.skipTest("Modules not available")
        self.processor = PashtoPDFProcessor()
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertTrue(hasattr(self.processor, 'pashto_utils'))
        self.assertTrue(hasattr(self.processor, 'ocr_handler'))
        self.assertTrue(hasattr(self.processor, 'metadata_extractor'))
        self.assertTrue(hasattr(self.processor, 'quality_assessor'))
    
    def test_pashto_text_detection(self):
        """Test Pashto text detection."""
        # Test with Pashto text
        pashto_text = "دا یو ازموینه دی ډول لکه ړ"
        result = self.processor._is_pashto_text(pashto_text)
        self.assertTrue(result)
        
        # Test with non-Pashto text
        english_text = "This is English text"
        result = self.processor._is_pashto_text(english_text)
        self.assertFalse(result)
    
    @patch('fitz.open')
    def test_processing_with_mock_pdf(self, mock_fitz):
        """Test processing with mocked PDF."""
        # Create mock PDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "دا یو ازموینه دی"
        mock_doc.__enter__.return_value = mock_doc
        mock_doc.__exit__.return_value = None
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        
        mock_fitz.return_value = mock_doc
        
        # Test processing
        result = self.processor.process_pdf("test.pdf", extract_metadata=False, assess_quality=False)
        
        self.assertIn('pdf_path', result)
        self.assertIn('pages', result)
        self.assertEqual(result['total_pages'], 1)


def create_test_sample_files():
    """Create sample test files."""
    if not IMPORTS_AVAILABLE:
        print("Cannot create test files - modules not available")
        return
    
    # Create sample configuration
    config = ProcessingConfig(
        ocr_enabled=True,
        ocr_languages="eng+pus",
        quality_threshold=0.6
    )
    
    config_manager = ConfigManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, "test_config.json")
        config_manager.save_config(config, config_path)
        print(f"Sample configuration saved to: {config_path}")
        
        # Load and validate
        loaded_config = config_manager.load_config(config_path)
        print(f"Loaded configuration: {loaded_config.ocr_languages}")


def run_performance_tests():
    """Run performance tests with sample data."""
    if not IMPORTS_AVAILABLE:
        print("Performance tests require full module availability")
        return
    
    print("Running Performance Tests...")
    
    # Test text processing performance
    utils = PashtoTextUtils()
    large_text = "دا یو ښه ازموینه دی " * 1000  # Repeat 1000 times
    
    import time
    start_time = time.time()
    
    # Test various operations
    cleaned = utils.clean_text(large_text)
    normalized = utils.normalize_pashto(cleaned)
    words = utils.extract_words(normalized)
    sentences = utils.extract_sentences(normalized)
    stats = utils.get_text_statistics(normalized)
    
    end_time = time.time()
    
    print(f"Text processing time: {end_time - start_time:.3f} seconds")
    print(f"Original length: {len(large_text)}")
    print(f"Cleaned length: {len(cleaned)}")
    print(f"Words extracted: {len(words)}")
    print(f"Sentences extracted: {len(sentences)}")
    print(f"Pashto ratio: {stats.get('pashto_ratio', 0):.2%}")


def demonstrate_pashto_capabilities():
    """Demonstrate Pashto text capabilities."""
    if not IMPORTS_AVAILABLE:
        print("Demonstration requires full module availability")
        return
    
    print("Pashto Text Processing Demonstration")
    print("=" * 50)
    
    # Initialize utilities
    utils = PashtoTextUtils()
    processor = PashtoPDFProcessor()
    
    # Sample Pashto text
    sample_texts = [
        "دا یو ښه ازموینه دی ډول لکه ړ",
        "زموږ د ښوونې او زده کړې موخه دا ده چې",
        "په دغه سلسله کې موږ به د ادبیاتو تاریخ وګورم",
        "احمد محمد په کال ۱۴۰۲ کې زیږیدلی"
    ]
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\nSample {i}: {text}")
        print("-" * 40)
        
        # Detect encoding
        encoding = utils.detect_encoding(text)
        print(f"Detected encoding: {encoding}")
        
        # Clean text
        cleaned = utils.clean_text(text)
        print(f"Cleaned: {cleaned}")
        
        # Normalize
        normalized = utils.normalize_pashto(text)
        print(f"Normalized: {normalized}")
        
        # Extract words
        words = utils.extract_words(normalized)
        print(f"Words: {words}")
        
        # Get statistics
        stats = utils.get_text_statistics(normalized)
        print(f"Statistics: {stats}")


def main():
    """Run all tests and demonstrations."""
    print("Pashto PDF Processing Module - Test Suite")
    print("=" * 60)
    
    # Check module availability
    if not IMPORTS_AVAILABLE:
        print("Some modules are not available for testing.")
        print("Please ensure all dependencies are installed:")
        print("pip install PyMuPDF pytesseract Pillow opencv-python numpy")
        return
    
    # Create test sample files
    print("\n1. Creating Sample Configuration...")
    create_test_sample_files()
    
    # Run unit tests
    print("\n2. Running Unit Tests...")
    test_suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Run performance tests
    print("\n3. Running Performance Tests...")
    run_performance_tests()
    
    # Demonstrate capabilities
    print("\n4. Demonstrating Pashto Capabilities...")
    demonstrate_pashto_capabilities()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print("\nTest suite completed!")


if __name__ == "__main__":
    main()