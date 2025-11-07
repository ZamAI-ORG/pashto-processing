#!/usr/bin/env python3
"""
Quick test script to verify the Pashto Processing Pipeline installation.
"""

import sys


def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        from pashto_pipeline import (
            TextProcessingPipeline,
            PashtoNormalizer,
            PashtoTokenizer
        )
        print("✓ Core imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_normalizer():
    """Test the normalizer functionality."""
    print("\nTesting PashtoNormalizer...")
    
    try:
        from pashto_pipeline import PashtoNormalizer
        
        normalizer = PashtoNormalizer(normalize_whitespace=True)
        
        # Test case 1: Whitespace normalization
        text1 = "سلام   دنیا"
        result1 = normalizer.normalize(text1)
        assert "  " not in result1, "Multiple spaces not normalized"
        
        # Test case 2: Digit normalization
        normalizer2 = PashtoNormalizer(normalize_digits='western')
        text2 = "۱۲۳"
        result2 = normalizer2.normalize(text2)
        assert "123" == result2, f"Digits not normalized correctly: {result2}"
        
        print("✓ Normalizer tests passed")
        return True
    except Exception as e:
        print(f"✗ Normalizer test failed: {e}")
        return False


def test_tokenizer():
    """Test the tokenizer functionality."""
    print("\nTesting PashtoTokenizer...")
    
    try:
        from pashto_pipeline import PashtoTokenizer
        
        tokenizer = PashtoTokenizer(preserve_punctuation=True)
        
        # Test case 1: Basic tokenization
        text1 = "سلام دنیا"
        tokens1 = tokenizer.tokenize(text1)
        assert len(tokens1) == 2, f"Expected 2 tokens, got {len(tokens1)}"
        
        # Test case 2: Punctuation preservation
        text2 = "سلام دنیا!"
        tokens2 = tokenizer.tokenize(text2)
        assert '!' in tokens2, "Punctuation not preserved"
        
        # Test case 3: Sentence tokenization
        text3 = "سلام دنیا. دا یو ټیسټ دی."
        sentences = tokenizer.tokenize_sentences(text3)
        assert len(sentences) == 2, f"Expected 2 sentences, got {len(sentences)}"
        
        print("✓ Tokenizer tests passed")
        return True
    except Exception as e:
        print(f"✗ Tokenizer test failed: {e}")
        return False


def test_pipeline():
    """Test the pipeline orchestration."""
    print("\nTesting TextProcessingPipeline...")
    
    try:
        from pashto_pipeline import (
            TextProcessingPipeline,
            PashtoNormalizer,
            PashtoTokenizer
        )
        
        # Create pipeline
        pipeline = TextProcessingPipeline()
        normalizer = PashtoNormalizer()
        tokenizer = PashtoTokenizer()
        
        # Add steps
        pipeline.add_step('normalize', normalizer.normalize)
        pipeline.add_step('tokenize', tokenizer.tokenize)
        
        # Test single processing
        text = "سلام   دنیا"
        result = pipeline.process(text, verbose=False)
        assert isinstance(result, list), "Pipeline should return list from tokenizer"
        
        # Test batch processing
        texts = ["سلام", "دنیا"]
        results = pipeline.process_batch(texts, verbose=False)
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        # Test step management
        assert 'normalize' in pipeline.get_steps(), "normalize step not found"
        assert 'tokenize' in pipeline.get_steps(), "tokenize step not found"
        
        print("✓ Pipeline tests passed")
        return True
    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Pashto Processing Pipeline - Test Suite")
    print("="*60)
    
    tests = [
        test_imports,
        test_normalizer,
        test_tokenizer,
        test_pipeline,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n🎉 All tests passed! The pipeline is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
