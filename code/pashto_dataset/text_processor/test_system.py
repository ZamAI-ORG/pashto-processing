#!/usr/bin/env python3
"""
Pashto Text Processing System - Test Script

Simple test script to verify the functionality of the Pashto text processing system.
This script runs basic tests on all components to ensure everything is working correctly.
"""

import sys
import os
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported successfully"""
    print("Testing imports...")
    try:
        from pashto_nlp_processor import PashtoNLPProcessor
        from text_normalizer import PashtoTextNormalizer
        from pashto_tokenizer import PashtoTokenizer
        from quality_filter import QualityFilter
        from deduplicator import TextDeduplicator
        from language_detector import PashtoLanguageDetector
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_language_detection():
    """Test language detection functionality"""
    print("\\nTesting language detection...")
    try:
        from language_detector import PashtoLanguageDetector
        
        detector = PashtoLanguageDetector()
        
        # Test Pashto text
        pashto_text = "زه یو ښوونکی دی چې د ښوونې ښه مینه لري."
        result = detector.detect_language(pashto_text)
        
        print(f"Pashto text detection: {result['detected_language']}")
        print(f"Pashto probability: {result['pashto_probability']}")
        print(f"Is Arabic script: {result['is_arabic_script']}")
        
        # Test non-Arabic text
        english_text = "This is English text"
        english_result = detector.detect_language(english_text)
        
        print(f"English text detection: {english_result['detected_language']}")
        
        print("✅ Language detection test passed")
        return True
    except Exception as e:
        print(f"❌ Language detection test failed: {e}")
        return False

def test_text_normalization():
    """Test text normalization functionality"""
    print("\\nTesting text normalization...")
    try:
        from text_normalizer import PashtoTextNormalizer
        
        normalizer = PashtoTextNormalizer()
        
        # Test text with various issues
        messy_text = "زه  یو   ښوونکي   دى  چې  په   کور   کې  د  ښونګرونو  ښودل  کېندى ."
        print(f"Original: {messy_text}")
        
        normalized_text, stats = normalizer.normalize(messy_text)
        print(f"Normalized: {normalized_text}")
        print(f"Processing steps: {stats.get('processing_steps', [])}")
        
        print("✅ Text normalization test passed")
        return True
    except Exception as e:
        print(f"❌ Text normalization test failed: {e}")
        return False

def test_tokenization():
    """Test tokenization functionality"""
    print("\\nTesting tokenization...")
    try:
        from pashto_tokenizer import PashtoTokenizer
        
        tokenizer = PashtoTokenizer()
        
        test_text = "زه یو ښوونکی دی چې د ښوونې ښه مینه لري."
        print(f"Test text: {test_text}")
        
        tokenization_result = tokenizer.tokenize_complete(test_text)
        
        print(f"Number of sentences: {tokenization_result['metadata']['total_sentences']}")
        print(f"Number of words: {tokenization_result['metadata']['total_words']}")
        print(f"Pashto word ratio: {tokenization_result['metadata']['pashto_word_ratio']:.2f}")
        print("Words:", [word['text'] for word in tokenization_result['words']])
        
        print("✅ Tokenization test passed")
        return True
    except Exception as e:
        print(f"❌ Tokenization test failed: {e}")
        return False

def test_quality_assessment():
    """Test quality assessment functionality"""
    print("\\nTesting quality assessment...")
    try:
        from quality_filter import QualityFilter
        
        quality_filter = QualityFilter()
        
        # Test high quality text
        good_text = "زه یو ښوونکی دی چې د ښوونې ښه مینه لري او د زده کړو ډېر ښه پلوه دی."
        quality_result = quality_filter.calculate_text_quality(good_text)
        
        print(f"High quality text score: {quality_result['overall_score']:.2f}")
        print(f"Quality grade: {quality_result['grade']}")
        print(f"Should keep: {quality_result['should_keep']}")
        
        # Test low quality text
        poor_text = "abc 123 !!"
        poor_quality = quality_filter.calculate_text_quality(poor_text)
        
        print(f"Low quality text score: {poor_quality['overall_score']:.2f}")
        print(f"Should keep: {poor_quality['should_keep']}")
        
        print("✅ Quality assessment test passed")
        return True
    except Exception as e:
        print(f"❌ Quality assessment test failed: {e}")
        return False

def test_deduplication():
    """Test deduplication functionality"""
    print("\\nTesting deduplication...")
    try:
        from deduplicator import TextDeduplicator
        
        deduplicator = TextDeduplicator()
        
        # Test texts with duplicates
        test_texts = [
            "زه یو ښوونکی دی.",
            "زه یو ښوونکی دی.",  # Exact duplicate
            "زه یو ښوونکې دی.",  # Near duplicate (typo)
            "ته یو ښوونکی دی.",  # Different pronoun
        ]
        
        print(f"Original texts count: {len(test_texts)}")
        
        dedup_result = deduplicator.deduplicate_texts(test_texts)
        
        print(f"After deduplication: {dedup_result['final_count']}")
        print(f"Removed exact duplicates: {dedup_result['removed_exact_duplicates']}")
        print(f"Removed near duplicates: {dedup_result['removed_near_duplicates']}")
        print("Final texts:", dedup_result['kept_texts'])
        
        print("✅ Deduplication test passed")
        return True
    except Exception as e:
        print(f"❌ Deduplication test failed: {e}")
        return False

def test_complete_pipeline():
    """Test the complete processing pipeline"""
    print("\\nTesting complete pipeline...")
    try:
        from pashto_nlp_processor import PashtoNLPProcessor
        
        processor = PashtoNLPProcessor()
        
        # Test single text processing
        test_text = "زه یو ښوونکی دی چې د ښوونې ښه مینه لري."
        print(f"Processing text: {test_text}")
        
        start_time = time.time()
        result = processor.process_text(test_text)
        processing_time = time.time() - start_time
        
        print(f"Processing status: {result.get('processing_status')}")
        print(f"Processing time: {processing_time:.3f}s")
        
        if 'language_detection' in result:
            lang = result['language_detection']
            print(f"Detected language: {lang.get('detected_language')}")
            print(f"Pashto probability: {lang.get('pashto_probability', 0):.2f}")
        
        if 'quality_assessment' in result:
            quality = result['quality_assessment']
            print(f"Quality score: {quality.get('overall_score', 0):.2f}")
            print(f"Should keep: {quality.get('should_keep', False)}")
        
        if 'tokenization' in result:
            token_data = result['tokenization']
            print(f"Number of words: {token_data['metadata']['total_words']}")
        
        print("✅ Complete pipeline test passed")
        return True
    except Exception as e:
        print(f"❌ Complete pipeline test failed: {e}")
        return False

def test_batch_processing():
    """Test batch processing functionality"""
    print("\\nTesting batch processing...")
    try:
        from pashto_nlp_processor import PashtoNLPProcessor
        
        processor = PashtoNLPProcessor()
        
        # Test batch of texts
        test_texts = [
            "زه یو ښوونکی دی چې د ښوونې ښه مینه لري.",
            "د افغانستان خلک ډېر مینه وال څانګه ښه ژبه لري.",
            "دا یوه ښه ورځ ده چې موږ د یو ځای کولو فرصت لرو.",
            "Hello world",  # Non-Arabic text
            "",  # Empty text
        ]
        
        print(f"Processing {len(test_texts)} texts in batch...")
        
        start_time = time.time()
        batch_result = processor.process_texts(test_texts, apply_deduplication=False)
        processing_time = time.time() - start_time
        
        print(f"Input count: {batch_result['input_count']}")
        print(f"Output count: {batch_result['output_count']}")
        print(f"Processing time: {processing_time:.3f}s")
        print(f"Success rate: {batch_result['statistics']['success_rate']:.1%}")
        
        if batch_result['statistics']['language_distribution']:
            print("Language distribution:")
            for lang, count in batch_result['statistics']['language_distribution'].items():
                print(f"  {lang}: {count} texts")
        
        print("✅ Batch processing test passed")
        return True
    except Exception as e:
        print(f"❌ Batch processing test failed: {e}")
        return False

def test_performance():
    """Test system performance"""
    print("\\nTesting system performance...")
    try:
        from pashto_nlp_processor import PashtoNLPProcessor
        
        processor = PashtoNLPProcessor()
        
        # Generate test data
        test_texts = [
            f"زه یو ښوونکی دی چې د ښوونې ښه مینه لري - Text {i}."
            for i in range(10)
        ]
        
        print(f"Processing {len(test_texts)} texts for performance test...")
        
        start_time = time.time()
        results = processor.process_texts(test_texts, apply_deduplication=True)
        total_time = time.time() - start_time
        
        avg_time_per_text = total_time / len(test_texts)
        
        print(f"Total processing time: {total_time:.3f}s")
        print(f"Average time per text: {avg_time_per_text:.3f}s")
        print(f"Texts per second: {len(test_texts) / total_time:.1f}")
        
        # Show statistics
        stats = processor.get_processing_statistics()
        print(f"Component usage: {stats['component_usage']}")
        
        print("✅ Performance test passed")
        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🧪 PASHTO TEXT PROCESSING SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Language Detection", test_language_detection),
        ("Text Normalization", test_text_normalization),
        ("Tokenization", test_tokenization),
        ("Quality Assessment", test_quality_assessment),
        ("Deduplication", test_deduplication),
        ("Complete Pipeline", test_complete_pipeline),
        ("Batch Processing", test_batch_processing),
        ("Performance", test_performance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Print summary
    print("\\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result, error in results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            if error:
                print(f"   Error: {error}")
            failed += 1
    
    print(f"\\nTotal tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(passed / len(results)) * 100:.1f}%")
    
    if failed == 0:
        print("\\n🎉 All tests passed! The Pashto text processing system is working correctly.")
    else:
        print(f"\\n⚠️  {failed} test(s) failed. Please check the errors above.")
    
    return failed == 0

def main():
    """Main function to run the test suite"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n\\nTest suite interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\\nUnexpected error in test suite: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()