#!/usr/bin/env python3
"""
Advanced Example: Web Scraping with Pashto Dataset Pipeline

This example demonstrates advanced web scraping capabilities
including custom processors, quality assessment, and batch processing.
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

# Import pipeline components
try:
    from pashto_pipeline import Pipeline, Config
    from pashto_pipeline.processors import BaseProcessor
    from pashto_pipeline.quality import QualityChecker
    from pashto_pipeline.exceptions import PipelineError, ProcessingError
    from pashto_pipeline.text import PashtoText
except ImportError:
    print("Error: Pashto Pipeline not installed.")
    print("Install it with: pip install pashto-dataset-pipeline")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('examples/logs/web_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CustomWebScrapingProcessor(BaseProcessor):
    """
    Custom processor for web-scraped Pashto content.
    
    This processor adds web-specific cleaning and quality checks.
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.remove_web_noise = config.get('remove_web_noise', True)
        self.extract_metadata = config.get('extract_metadata', True)
        self.min_content_length = config.get('min_content_length', 50)
        
        # Web-specific patterns to remove
        self.noise_patterns = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URLs
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            r'©\s*\d{4}.*',  # Copyright notices
            r'All rights reserved\.?',  # Rights notices
            r'Contact us.*',  # Contact info
            r'Click here.*',  # Call-to-action text
        ]
        
        # Pashto web content indicators
        self.pashto_indicators = [
            'زموږ', 'ژبه', 'پښتو', 'افغانستان', 'افغان', 'کابل', 'پاکستان'
        ]
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process web-scraped content.
        
        Args:
            data: Dictionary containing web content and metadata
            
        Returns:
            Processed content dictionary
        """
        try:
            # Extract content
            text = data.get('text', '')
            metadata = data.get('metadata', {})
            
            if not text:
                raise ProcessingError("No text content provided")
            
            # Clean web-specific noise
            if self.remove_web_noise:
                text = self._remove_web_noise(text)
            
            # Extract structured content
            structured_content = self._extract_structured_content(text, metadata)
            
            # Add Pashto-specific processing
            processed_text = self._process_pashto_content(structured_content['text'])
            
            # Create final result
            result = {
                'text': processed_text,
                'metadata': {
                    **metadata,
                    'original_length': len(text),
                    'processed_length': len(processed_text),
                    'noise_removed': len(text) - len(processed_text),
                    'pashto_indicators_found': self._count_pashto_indicators(processed_text)
                },
                'structured_content': structured_content,
                'processing_timestamp': time.time()
            }
            
            # Validate result
            if len(processed_text) < self.min_content_length:
                raise ProcessingError(f"Content too short after processing: {len(processed_text)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Web scraping processing failed: {e}")
            raise ProcessingError(f"Processing failed: {e}")
    
    def _remove_web_noise(self, text: str) -> str:
        """Remove web-specific noise from text."""
        import re
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove noise patterns
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_structured_content(self, text: str, metadata: dict) -> Dict[str, str]:
        """Extract structured content from text."""
        sentences = text.split('.')
        
        return {
            'text': text,
            'sentences': [s.strip() for s in sentences if s.strip()],
            'paragraphs': text.split('\n\n'),
            'word_count': len(text.split()),
            'character_count': len(text)
        }
    
    def _process_pashto_content(self, text: str) -> str:
        """Apply Pashto-specific processing."""
        # Normalize Pashto text
        pstext = PashtoText(text)
        normalized = pstext.normalize()
        
        return normalized.text
    
    def _count_pashto_indicators(self, text: str) -> int:
        """Count Pashto content indicators."""
        count = 0
        for indicator in self.pashto_indicators:
            count += text.count(indicator)
        return count

class WebScrapingExample:
    """
    Advanced example for web scraping with the Pashto Pipeline.
    """
    
    def __init__(self, config_path: str = "examples/config/web_scraping.yaml"):
        """
        Initialize the web scraping example.
        
        Args:
            config_path: Path to web scraping configuration
        """
        self.config_path = config_path
        self.config = None
        self.pipeline = None
        self.quality_checker = None
        self.custom_processor = None
        self.setup()
    
    def setup(self):
        """Setup the web scraping pipeline."""
        try:
            logger.info("Setting up web scraping pipeline...")
            
            # Load configuration
            if not os.path.exists(self.config_path):
                logger.warning(f"Configuration file not found: {self.config_path}")
                logger.info("Using default configuration")
                self.config = self._create_default_config()
            else:
                self.config = Config.from_file(self.config_path)
                logger.info(f"Configuration loaded from: {self.config_path}")
            
            # Create pipeline
            self.pipeline = Pipeline(self.config)
            
            # Create quality checker
            self.quality_checker = QualityChecker(self.config.get_quality_config())
            
            # Create custom processor
            self.custom_processor = CustomWebScrapingProcessor(
                self.config.get_processing_config()
            )
            
            logger.info("Web scraping pipeline setup completed")
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            raise
    
    def _create_default_config(self) -> Config:
        """Create default configuration for demonstration."""
        config_data = {
            'pipeline': {
                'name': 'Web Scraping Demo',
                'version': '1.0'
            },
            'processing': {
                'remove_web_noise': True,
                'extract_metadata': True,
                'min_content_length': 50
            },
            'quality': {
                'min_quality_score': 0.6
            }
        }
        return Config.from_dict(config_data)
    
    def create_sample_web_data(self, directory: str) -> List[str]:
        """
        Create sample web-scraped data.
        
        Args:
            directory: Directory to create sample data
            
        Returns:
            List of created file paths
        """
        logger.info(f"Creating sample web data in: {directory}")
        
        os.makedirs(directory, exist_ok=True)
        
        # Sample web content
        web_samples = [
            {
                'url': 'https://example.com/news/article1',
                'title': 'د افغانستان د ژبې څیړنه',
                'text': '''زموږ د ژبې څیړنه ډېر ښه کار دی. د افغانستان د خلکو ژبه د پښتو ژبه ده. 
                دا ژبه ډېر ښه دی او موږ یې ډېر څیړو. پښتو ژبه د نړۍ د ژبو څخه یوه ښه ژبه ده.
                زموږ د کابل ښار ډېر ښه دی. موږ د خپلو کلتور او ژبې خوښي لرو.''',
                'metadata': {
                    'author': 'احمد علی',
                    'publish_date': '2025-11-06',
                    'category': 'news',
                    'source_domain': 'example.com'
                }
            },
            {
                'url': 'https://example.com/blog/post1',
                'title': 'د پښتو شاعراني څیړنه',
                'text': '''پښتو شاعراني ډېر ښه دی. زموږ د لیکلو هنر ډېر ښه دی. 
                د افغانستان تاریخ ډېر ښه دی. موږ د خپلو شاعرانو څیړنه کوو. 
                دا څیړنه به زموږ ژبه ډېر ښه کړي. Contact us for more information. 
                Visit http://example.com for details. All rights reserved.''',
                'metadata': {
                    'author': 'فاطمه احمد',
                    'publish_date': '2025-11-05',
                    'category': 'blog',
                    'source_domain': 'example.com'
                }
            },
            {
                'url': 'https://example.com/news/mixed-content',
                'title': 'Mixed Language Content Demo',
                'text': '''This is English text mixed with Pashto: زموږ ژبه ښه ده. 
                دا یوه ښه مثال دی چې موږ د ژبې څیړنه کوو. The research on language is important. 
                د افغانستان د ژبې اهمیت ډېر لوی دی.''',
                'metadata': {
                    'author': 'Mixed Author',
                    'publish_date': '2025-11-04',
                    'category': 'bilingual',
                    'source_domain': 'example.com'
                }
            }
        ]
        
        created_files = []
        
        for i, sample in enumerate(web_samples, 1):
            # Create JSON file
            file_path = os.path.join(directory, f"web_sample_{i:02d}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample, f, ensure_ascii=False, indent=2)
            created_files.append(file_path)
        
        logger.info(f"Created {len(web_samples)} web sample files")
        return created_files
    
    def process_web_content(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        Process web content with custom processor.
        
        Args:
            input_dir: Input directory
            output_dir: Output directory
            
        Returns:
            Processing results
        """
        logger.info("Processing web content with custom processor...")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            results = {
                'processed_files': 0,
                'total_processed': 0,
                'high_quality_count': 0,
                'processing_time': 0,
                'errors': []
            }
            
            start_time = time.time()
            
            # Process each file
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        
                        try:
                            # Load web content
                            with open(file_path, 'r', encoding='utf-8') as f:
                                web_data = json.load(f)
                            
                            # Process with custom processor
                            processed = self.custom_processor.process(web_data)
                            
                            # Quality check
                            quality_result = self.quality_checker.assess_text(processed['text'])
                            
                            # Create output
                            output_data = {
                                'original': web_data,
                                'processed': processed,
                                'quality': {
                                    'score': quality_result.score,
                                    'metrics': quality_result.metrics
                                }
                            }
                            
                            # Save processed content
                            output_file = os.path.join(output_dir, f"processed_{file}")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                json.dump(output_data, f, ensure_ascii=False, indent=2)
                            
                            # Update statistics
                            results['processed_files'] += 1
                            results['total_processed'] += 1
                            
                            if quality_result.score >= 0.7:
                                results['high_quality_count'] += 1
                            
                            logger.info(f"Processed: {file} (Quality: {quality_result.score:.3f})")
                            
                        except Exception as e:
                            error_msg = f"Failed to process {file}: {e}"
                            logger.error(error_msg)
                            results['errors'].append(error_msg)
            
            results['processing_time'] = time.time() - start_time
            
            logger.info(f"Web content processing completed in {results['processing_time']:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Web content processing failed: {e}")
            raise
    
    def analyze_web_content(self, output_dir: str) -> Dict[str, Any]:
        """
        Analyze processed web content.
        
        Args:
            output_dir: Output directory containing processed files
            
        Returns:
            Analysis results
        """
        logger.info("Analyzing web content...")
        
        analysis = {
            'total_files': 0,
            'quality_statistics': {},
            'content_analysis': {},
            'language_analysis': {},
            'source_analysis': {}
        }
        
        try:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.startswith('processed_') and file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Basic statistics
                        analysis['total_files'] += 1
                        
                        # Quality analysis
                        if 'quality' in data:
                            score = data['quality']['score']
                            if 'quality_distribution' not in analysis['quality_statistics']:
                                analysis['quality_statistics'] = {
                                    'scores': [],
                                    'high_quality': 0,
                                    'medium_quality': 0,
                                    'low_quality': 0
                                }
                            
                            analysis['quality_statistics']['scores'].append(score)
                            
                            if score >= 0.7:
                                analysis['quality_statistics']['high_quality'] += 1
                            elif score >= 0.5:
                                analysis['quality_statistics']['medium_quality'] += 1
                            else:
                                analysis['quality_statistics']['low_quality'] += 1
                        
                        # Content analysis
                        if 'processed' in data:
                            processed = data['processed']
                            original_length = processed['metadata'].get('original_length', 0)
                            processed_length = processed['metadata'].get('processed_length', 0)
                            noise_removed = processed['metadata'].get('noise_removed', 0)
                            
                            if 'content_stats' not in analysis['content_analysis']:
                                analysis['content_analysis'] = {
                                    'original_lengths': [],
                                    'processed_lengths': [],
                                    'noise_removed': []
                                }
                            
                            analysis['content_analysis']['original_lengths'].append(original_length)
                            analysis['content_analysis']['processed_lengths'].append(processed_length)
                            analysis['content_analysis']['noise_removed'].append(noise_removed)
                        
                        # Source analysis
                        if 'original' in data and 'metadata' in data['original']:
                            source = data['original']['metadata'].get('source_domain', 'unknown')
                            if source not in analysis['source_analysis']:
                                analysis['source_analysis'][source] = 0
                            analysis['source_analysis'][source] += 1
            
            # Calculate summary statistics
            if analysis['quality_statistics']['scores']:
                scores = analysis['quality_statistics']['scores']
                analysis['quality_statistics']['average_score'] = sum(scores) / len(scores)
                analysis['quality_statistics']['min_score'] = min(scores)
                analysis['quality_statistics']['max_score'] = max(scores)
            
            logger.info("Web content analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Web content analysis failed: {e}")
            return analysis
    
    def demonstrate_batch_processing(self, input_dir: str, output_dir: str) -> Dict[str, Any]:
        """
        Demonstrate batch processing capabilities.
        
        Args:
            input_dir: Input directory
            output_dir: Output directory
            
        Returns:
            Batch processing results
        """
        logger.info("Demonstrating batch processing...")
        
        try:
            # Use the main pipeline for batch processing
            result = self.pipeline.run(input_dir, output_dir)
            
            batch_results = {
                'total_processed': result.total_processed,
                'batch_size': result.total_processed,
                'throughput': result.total_processed / result.processing_time if result.processing_time > 0 else 0,
                'processing_time': result.processing_time,
                'quality_score': result.quality_score
            }
            
            logger.info(f"Batch processing completed: {batch_results}")
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise
    
    def run_advanced_example(self) -> None:
        """
        Run the complete advanced example workflow.
        """
        logger.info("="*60)
        logger.info("Starting Pashto Pipeline Advanced Web Scraping Example")
        logger.info("="*60)
        
        # Setup directories
        input_dir = "examples/data/web_input"
        output_dir = "examples/data/web_output"
        
        try:
            # Step 1: Create sample web data
            web_files = self.create_sample_web_data(input_dir)
            
            # Step 2: Process web content with custom processor
            web_results = self.process_web_content(input_dir, output_dir)
            
            # Step 3: Analyze web content
            web_analysis = self.analyze_web_content(output_dir)
            
            # Step 4: Demonstrate batch processing
            batch_results = self.demonstrate_batch_processing(input_dir, output_dir)
            
            # Step 5: Print comprehensive summary
            self.print_advanced_summary(web_results, web_analysis, batch_results)
            
            logger.info("="*60)
            logger.info("Advanced web scraping example completed successfully!")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Advanced example failed: {e}")
            raise
    
    def print_advanced_summary(self, web_results: Dict, web_analysis: Dict, batch_results: Dict) -> None:
        """
        Print comprehensive summary of advanced example results.
        
        Args:
            web_results: Web content processing results
            web_analysis: Web content analysis results
            batch_results: Batch processing results
        """
        print("\n" + "="*70)
        print("PASHT0 DATASET PIPELINE - ADVANCED WEB SCRAPING EXAMPLE")
        print("="*70)
        
        print(f"\n🕸️  WEB CONTENT PROCESSING:")
        print(f"   • Files processed: {web_results['processed_files']}")
        print(f"   • Total items: {web_results['total_processed']}")
        print(f"   • High quality items: {web_results['high_quality_count']}")
        print(f"   • Processing time: {web_results['processing_time']:.2f}s")
        print(f"   • Errors encountered: {len(web_results['errors'])}")
        
        if web_results['errors']:
            print(f"   • Error details:")
            for error in web_results['errors'][:3]:  # Show first 3 errors
                print(f"     - {error}")
        
        print(f"\n📊 QUALITY ANALYSIS:")
        if web_analysis.get('quality_statistics'):
            qs = web_analysis['quality_statistics']
            print(f"   • Total files analyzed: {web_analysis['total_files']}")
            print(f"   • Average quality score: {qs.get('average_score', 0):.3f}")
            print(f"   • Quality range: {qs.get('min_score', 0):.3f} - {qs.get('max_score', 0):.3f}")
            print(f"   • High quality (≥0.7): {qs.get('high_quality', 0)}")
            print(f"   • Medium quality (0.5-0.7): {qs.get('medium_quality', 0)}")
            print(f"   • Low quality (<0.5): {qs.get('low_quality', 0)}")
        
        print(f"\n🔍 CONTENT ANALYSIS:")
        if web_analysis.get('content_analysis'):
            ca = web_analysis['content_analysis']
            if ca.get('original_lengths'):
                orig_avg = sum(ca['original_lengths']) / len(ca['original_lengths'])
                proc_avg = sum(ca['processed_lengths']) / len(ca['processed_lengths'])
                noise_avg = sum(ca['noise_removed']) / len(ca['noise_removed'])
                
                print(f"   • Average original length: {orig_avg:.0f} characters")
                print(f"   • Average processed length: {proc_avg:.0f} characters")
                print(f"   • Average noise removed: {noise_avg:.0f} characters")
        
        print(f"\n🌐 SOURCE ANALYSIS:")
        if web_analysis.get('source_analysis'):
            for source, count in web_analysis['source_analysis'].items():
                print(f"   • {source}: {count} files")
        
        print(f"\n⚡ BATCH PROCESSING RESULTS:")
        print(f"   • Batch size: {batch_results['batch_size']} items")
        print(f"   • Processing time: {batch_results['processing_time']:.2f}s")
        print(f"   • Throughput: {batch_results['throughput']:.1f} items/sec")
        print(f"   • Quality score: {batch_results['quality_score']:.3f}")
        
        print(f"\n💡 ADVANCED FEATURES DEMONSTRATED:")
        print(f"   • Custom web scraping processor")
        print(f"   • Web-specific content cleaning")
        print(f"   • Pashto language processing")
        print(f"   • Quality assessment and filtering")
        print(f"   • Batch processing capabilities")
        print(f"   • Comprehensive analytics")
        
        print(f"\n📁 OUTPUT DIRECTORIES:")
        print(f"   • Web processed files: {os.path.abspath(output_dir)}")
        print(f"   • Pipeline output: {os.path.abspath(output_dir)}")
        print(f"   • Log files: {os.path.abspath('examples/logs')}")
        
        print("="*70)

def main():
    """
    Main function to run the advanced example.
    """
    # Parse command line arguments
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "examples/config/web_scraping.yaml"
    
    try:
        # Create and run advanced example
        example = WebScrapingExample(config_path)
        example.run_advanced_example()
        
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.error(f"Advanced example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()