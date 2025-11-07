"""
Pashto Text Processing System - Example Usage and Testing

This module demonstrates how to use the comprehensive Pashto text processing system
with practical examples and test cases.
"""

import os
import json
import time
from typing import List, Dict, Any
from datetime import datetime

# Import the Pashto text processing modules
from pashto_nlp_processor import PashtoNLPProcessor
from text_normalizer import PashtoTextNormalizer
from pashto_tokenizer import PashtoTokenizer
from quality_filter import QualityFilter
from deduplicator import TextDeduplicator
from language_detector import PashtoLanguageDetector

class PashtoTextProcessorDemo:
    """Demonstration class for Pashto text processing capabilities"""
    
    def __init__(self):
        """Initialize the demo with test data and processor"""
        # Initialize the main processor
        self.processor = PashtoNLPProcessor(
            enable_normalization=True,
            enable_tokenization=True,
            enable_quality_filtering=True,
            enable_deduplication=True,
            enable_language_detection=True,
            quality_threshold=0.3,
            deduplication_threshold=0.85
        )
        
        # Sample Pashto texts for testing
        self.sample_texts = [
            "زه یو ښوونکی دی چې په کور کې د ښونګرونو ښودل کېندی.",
            "د افغانستان خلک ډېر مینه وال څانګه ښه ژبه لري.",
            "دا یوه ښه ورځ ده چې موږ د یو ځای کولو فرصت لرو.",
            "زموږ هیواد ډېر تاریخي ځایونه لري چې د لیدلو وړتیا لري.",
            "ښوونې د ژوند د بدلونو لپاره ډېر ښه وسیله ده.",
            # Some mixed quality examples
            "Hello world this is English mixed with پښتو",  # Mixed script
            "",  # Empty text
            "د کور ښه دی",  # Short text
            "زه ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر ډېر کور دی",  # Repetitive
        ]
    
    def demo_individual_components(self):
        """Demonstrate individual component functionality"""
        print("=" * 60)
        print("PASHTO TEXT PROCESSING - INDIVIDUAL COMPONENTS DEMO")
        print("=" * 60)
        
        test_text = "زه یو ښوونکی دی چې په کور کې د ښونګرونو ښودل کېندی."
        print(f"Test text: {test_text}")
        print()
        
        # 1. Language Detection Demo
        print("1. LANGUAGE DETECTION")
        print("-" * 30)
        if self.processor.language_detector:
            lang_result = self.processor.language_detector.detect_language(test_text)
            print(f"Detected Language: {lang_result['detected_language']}")
            print(f"Confidence: {lang_result['confidence']}")
            print(f"Is Arabic Script: {lang_result['is_arabic_script']}")
            print(f"Pashto Probability: {lang_result['pashto_probability']}")
            print()
        
        # 2. Text Normalization Demo
        print("2. TEXT NORMALIZATION")
        print("-" * 30)
        if self.processor.normalizer:
            original_text = "زه  یو   ښوونکي   دى  چې  په   کور   کې  د  ښونګرونو  ښودل  کېندى ."
            print(f"Original (with spacing issues): {original_text}")
            normalized_text, stats = self.processor.normalizer.normalize(original_text)
            print(f"Normalized: {normalized_text}")
            print(f"Processing steps: {stats.get('processing_steps', [])}")
            print()
        
        # 3. Tokenization Demo
        print("3. TOKENIZATION")
        print("-" * 30)
        if self.processor.tokenizer:
            tokenization_result = self.processor.tokenizer.tokenize_complete(test_text)
            print(f"Number of sentences: {tokenization_result['metadata']['total_sentences']}")
            print(f"Number of words: {tokenization_result['metadata']['total_words']}")
            print(f"Pashto word ratio: {tokenization_result['metadata']['pashto_word_ratio']:.2f}")
            print("Words:", [word['text'] for word in tokenization_result['words'][:5]])
            print()
        
        # 4. Quality Assessment Demo
        print("4. QUALITY ASSESSMENT")
        print("-" * 30)
        if self.processor.quality_filter:
            quality_result = self.processor.quality_filter.calculate_text_quality(test_text)
            print(f"Overall Quality Score: {quality_result['overall_score']:.2f}")
            print(f"Quality Grade: {quality_result['grade']}")
            print(f"Should Keep: {quality_result['should_keep']}")
            print("Quality metrics:")
            for category, metrics in quality_result['quality_metrics'].items():
                if isinstance(metrics, dict) and 'score' in metrics:
                    print(f"  {category}: {metrics['score']:.2f}")
            print()
        
        # 5. Deduplication Demo
        print("5. DEDUPLICATION")
        print("-" * 30)
        if self.processor.deduplicator:
            # Create some duplicate and near-duplicate texts
            test_texts = [
                "زه یو ښوونکی دی.",
                "زه یو ښوونکی دی.",  # Exact duplicate
                "زه یو ښوونکې دی.",  # Near duplicate (typo)
                "ته یو ښوونکی دی.",  # Different pronoun
            ]
            
            dedup_result = self.processor.deduplicator.deduplicate_texts(test_texts)
            print(f"Original count: {dedup_result['original_count']}")
            print(f"After deduplication: {dedup_result['final_count']}")
            print(f"Removed exact duplicates: {dedup_result['removed_exact_duplicates']}")
            print(f"Removed near duplicates: {dedup_result['removed_near_duplicates']}")
            print()
    
    def demo_complete_pipeline(self):
        """Demonstrate the complete processing pipeline"""
        print("=" * 60)
        print("COMPLETE PIPELINE PROCESSING DEMO")
        print("=" * 60)
        
        # Process each sample text through complete pipeline
        for i, text in enumerate(self.sample_texts[:3]):  # Process first 3 texts
            print(f"\\nProcessing Text {i+1}: '{text}'")
            print("-" * 50)
            
            result = self.processor.process_text(text, apply_all_steps=True, return_full_analysis=True)
            
            print(f"Status: {result.get('processing_status')}")
            print(f"Processing time: {result.get('processing_time', 0):.3f}s")
            
            if 'language_detection' in result:
                lang = result['language_detection']
                print(f"Language: {lang.get('detected_language', 'Unknown')}")
                print(f"Pashto probability: {lang.get('pashto_probability', 0):.2f}")
            
            if 'quality_assessment' in result:
                quality = result['quality_assessment']
                print(f"Quality score: {quality.get('overall_score', 0):.2f}")
                print(f"Should keep: {quality.get('should_keep', False)}")
            
            if 'error' in result:
                print(f"Error: {result['error']}")
    
    def demo_batch_processing(self):
        """Demonstrate batch processing capabilities"""
        print("\\n" + "=" * 60)
        print("BATCH PROCESSING DEMO")
        print("=" * 60)
        
        # Add some duplicate and similar texts for testing
        batch_texts = self.sample_texts.copy()
        batch_texts.extend([
            "زه یو ښوونکی دی چې په کور کې د ښونګرونو ښودل کېندی.",  # Duplicate
            "زه یوه ښوونکې دې چې په کور کې د ښونګرونو ښودل کېندی.",  # Near duplicate
            "Hello world",  # Non-Arabic text
            "د تعلیم اهمیت ډېر لوی دی",  # Good Pashto
            "د ښوونې او زده کړې ښه پروسه ده",  # Another good text
        ])
        
        print(f"Processing {len(batch_texts)} texts in batch...")
        start_time = time.time()
        
        batch_result = self.processor.process_texts(
            batch_texts, 
            apply_deduplication=True,
            return_removed_content=True
        )
        
        processing_time = time.time() - start_time
        
        print(f"\\nBatch Processing Results:")
        print(f"Input count: {batch_result['input_count']}")
        print(f"Output count: {batch_result['output_count']}")
        print(f"Processing time: {processing_time:.3f}s")
        print(f"Success rate: {batch_result['statistics']['success_rate']:.1%}")
        
        # Language distribution
        if batch_result['statistics']['language_distribution']:
            print("\\nLanguage Distribution:")
            for lang, count in batch_result['statistics']['language_distribution'].items():
                print(f"  {lang}: {count} texts")
        
        # Quality distribution
        if batch_result['statistics']['quality_distribution']:
            quality_dist = batch_result['statistics']['quality_distribution']
            print(f"\\nQuality Distribution:")
            print(f"  High quality: {quality_dist['high']}")
            print(f"  Medium quality: {quality_dist['medium']}")
            print(f"  Low quality: {quality_dist['low']}")
            print(f"  Average score: {quality_dist['average_score']:.2f}")
        
        # Deduplication results
        if batch_result.get('deduplication', {}).get('deduplication_applied'):
            dedup = batch_result['deduplication']
            print(f"\\nDeduplication Results:")
            print(f"  Removed exact duplicates: {dedup['removed_exact_duplicates']}")
            print(f"  Removed near duplicates: {dedup['removed_near_duplicates']}")
        
        # Removal analysis
        if 'removed_content_info' in batch_result:
            removal_info = batch_result['removed_content_info']
            print(f"\\nRemoval Analysis (Total removed: {removal_info['total_removed']}):")
            for reason, count in removal_info['removal_reasons'].items():
                if count > 0:
                    print(f"  {reason}: {count}")
    
    def demo_export_functionality(self):
        """Demonstrate result export functionality"""
        print("\\n" + "=" * 60)
        print("EXPORT FUNCTIONALITY DEMO")
        print("=" * 60)
        
        # Process a small batch for export demo
        export_texts = self.sample_texts[:3]
        results = self.processor.process_texts(export_texts)
        
        # Create output directory
        output_dir = "pashto_processing_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Export in different formats
        export_formats = ['json', 'csv', 'txt']
        
        for format_type in export_formats:
            output_path = f"{output_dir}/pashto_results.{format_type}"
            success = self.processor.export_results(results, output_path, format_type)
            
            if success:
                file_size = os.path.getsize(output_path)
                print(f"✓ Exported {format_type.upper()} format: {output_path} ({file_size} bytes)")
            else:
                print(f"✗ Failed to export {format_type.upper()} format")
    
    def demo_configuration_options(self):
        """Demonstrate configuration options"""
        print("\\n" + "=" * 60)
        print("CONFIGURATION OPTIONS DEMO")
        print("=" * 60)
        
        # Test text for consistency
        test_text = "زه یو ښوونکی دی چې د ښوونې ښه مینه لري."
        
        # Default processor
        print("1. DEFAULT CONFIGURATION")
        default_result = self.processor.process_text(test_text)
        print(f"Quality score with defaults: {default_result.get('quality_assessment', {}).get('overall_score', 'N/A')}")
        
        # High quality threshold
        print("\\n2. HIGH QUALITY THRESHOLD (0.8)")
        high_quality_processor = PashtoNLPProcessor(quality_threshold=0.8)
        high_result = high_quality_processor.process_text(test_text)
        print(f"Quality score with high threshold: {high_result.get('quality_assessment', {}).get('overall_score', 'N/A')}")
        print(f"Should keep: {high_result.get('quality_assessment', {}).get('should_keep', 'N/A')}")
        
        # Low deduplication threshold
        print("\\n3. STRICT DEDUPLICATION (0.7)")
        strict_dedup_processor = PashtoNLPProcessor(deduplication_threshold=0.7)
        
        # Test texts with different similarity
        similar_texts = [
            "زه یو ښوونکی دی",
            "زه یو ښوونکې دی",  # Very similar
            "زه ښوونکی دی",    # Less similar
        ]
        
        dedup_result = strict_dedup_processor.deduplicator.deduplicate_texts(
            similar_texts, 
            remove_near_duplicates=True,
            near_duplicate_threshold=0.7
        )
        
        print(f"Original count: {dedup_result['original_count']}")
        print(f"After strict deduplication: {dedup_result['final_count']}")
        print(f"Removed near duplicates: {dedup_result['removed_near_duplicates']}")
        
        # Minimal processing
        print("\\n4. MINIMAL PROCESSING (only essential steps)")
        minimal_processor = PashtoNLPProcessor(
            enable_normalization=False,
            enable_tokenization=False,
            enable_quality_filtering=False,
            enable_deduplication=False,
            enable_language_detection=True
        )
        
        minimal_result = minimal_processor.process_text(test_text)
        print(f"Processing time (minimal): {minimal_result.get('processing_time', 0):.3f}s")
        print(f"Components used: {[k for k, v in minimal_processor.stats['component_usage'].items() if v > 0]}")
    
    def run_full_demo(self):
        """Run the complete demonstration"""
        print("🚀 PASHTO TEXT PROCESSING SYSTEM DEMONSTRATION")
        print("=" * 80)
        
        # Run all demos
        self.demo_individual_components()
        self.demo_complete_pipeline()
        self.demo_batch_processing()
        self.demo_export_functionality()
        self.demo_configuration_options()
        
        # Show final statistics
        print("\\n" + "=" * 60)
        print("PROCESSING STATISTICS")
        print("=" * 60)
        
        stats = self.processor.get_processing_statistics()
        print(f"Total texts processed: {stats['total_processed']}")
        print(f"Successful processing: {stats['successful_processed']}")
        print(f"Failed processing: {stats['failed_processes']}")
        print(f"Average processing time: {stats['average_processing_time']:.3f}s")
        
        if stats['component_usage_percentages']:
            print("\\nComponent usage:")
            for component, percentage in stats['component_usage_percentages'].items():
                print(f"  {component}: {percentage:.1f}%")
        
        print("\\n✅ Demonstration completed successfully!")


def main():
    """Main function to run the demonstration"""
    try:
        demo = PashtoTextProcessorDemo()
        demo.run_full_demo()
    except Exception as e:
        print(f"❌ Error running demonstration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()