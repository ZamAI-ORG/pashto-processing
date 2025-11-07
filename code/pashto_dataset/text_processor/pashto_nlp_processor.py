"""
Pashto NLP Processor - Main Integration Module

Comprehensive Pashto text processing system that integrates:
- Text normalization
- Tokenization
- Quality filtering
- Deduplication
- Language detection
- Batch processing capabilities
"""

from typing import List, Dict, Any, Tuple
import json
import time
from datetime import datetime

try:
    from .text_normalizer import PashtoTextNormalizer
    from .pashto_tokenizer import PashtoTokenizer
    from .quality_filter import QualityFilter
    from .deduplicator import TextDeduplicator
    from .language_detector import PashtoLanguageDetector
except ImportError:
    from text_normalizer import PashtoTextNormalizer
    from pashto_tokenizer import PashtoTokenizer
    from quality_filter import QualityFilter
    from deduplicator import TextDeduplicator
    from language_detector import PashtoLanguageDetector

class PashtoNLPProcessor:
    """Main Pashto NLP processing system"""
    
    def __init__(self, 
                 enable_normalization: bool = True,
                 enable_tokenization: bool = True,
                 enable_quality_filtering: bool = True,
                 enable_deduplication: bool = True,
                 enable_language_detection: bool = True,
                 quality_threshold: float = 0.3,
                 deduplication_threshold: float = 0.85):
        """
        Initialize the Pashto NLP processor
        
        Args:
            enable_normalization: Enable text normalization
            enable_tokenization: Enable tokenization
            enable_quality_filtering: Enable quality filtering
            enable_deduplication: Enable deduplication
            enable_language_detection: Enable language detection
            quality_threshold: Minimum quality score for text retention
            deduplication_threshold: Similarity threshold for deduplication
        """
        self.config = {
            'enable_normalization': enable_normalization,
            'enable_tokenization': enable_tokenization,
            'enable_quality_filtering': enable_quality_filtering,
            'enable_deduplication': enable_deduplication,
            'enable_language_detection': enable_language_detection,
            'quality_threshold': quality_threshold,
            'deduplication_threshold': deduplication_threshold
        }
        
        # Initialize components
        self.normalizer = PashtoTextNormalizer() if enable_normalization else None
        self.tokenizer = PashtoTokenizer() if enable_tokenization else None
        self.quality_filter = QualityFilter() if enable_quality_filtering else None
        self.deduplicator = TextDeduplicator() if enable_deduplication else None
        self.language_detector = PashtoLanguageDetector() if enable_language_detection else None
        
        # Processing statistics
        self.stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processes': 0,
            'processing_times': [],
            'component_usage': {
                'normalization': 0,
                'tokenization': 0,
                'quality_filtering': 0,
                'deduplication': 0,
                'language_detection': 0
            }
        }
    
    def process_text(self, text: str, 
                    apply_all_steps: bool = True,
                    return_full_analysis: bool = True) -> Dict[str, Any]:
        """
        Process a single Pashto text through the complete pipeline
        
        Args:
            text: Pashto text to process
            apply_all_steps: Apply all processing steps
            return_full_analysis: Return complete analysis results
            
        Returns:
            Comprehensive processing results
        """
        start_time = time.time()
        
        if not text or not text.strip():
            return {
                'original_text': text,
                'processed_text': text,
                'processing_status': 'failed',
                'error': 'Empty or invalid text provided',
                'processing_time': time.time() - start_time
            }
        
        result = {
            'original_text': text,
            'processing_timestamp': datetime.now().isoformat(),
            'processing_config': self.config.copy()
        }
        
        try:
            # Step 1: Language Detection (early exit if not Arabic script)
            if self.language_detector and (apply_all_steps or return_full_analysis):
                language_result = self.language_detector.detect_language(text)
                result['language_detection'] = language_result
                self.stats['component_usage']['language_detection'] += 1
                
                # Early exit if not Arabic script
                if not language_result.get('is_arabic_script', False):
                    result['processed_text'] = text
                    result['processing_status'] = 'completed_early'
                    result['early_exit_reason'] = 'not_arabic_script'
                    result['processing_time'] = time.time() - start_time
                    return result
            
            # Step 2: Text Normalization
            if self.normalizer and (apply_all_steps or return_full_analysis):
                normalized_text, normalization_stats = self.normalizer.normalize(text)
                result['normalization'] = {
                    'normalized_text': normalized_text,
                    'normalization_stats': normalization_stats
                }
                self.stats['component_usage']['normalization'] += 1
                text = normalized_text
            
            # Step 3: Tokenization
            if self.tokenizer and (apply_all_steps or return_full_analysis):
                tokenization_result = self.tokenizer.tokenize_complete(text)
                result['tokenization'] = tokenization_result
                self.stats['component_usage']['tokenization'] += 1
            else:
                # Create basic tokenization if tokenizer not available
                result['tokenization'] = {
                    'text': text,
                    'words': [{'text': word, 'start': 0, 'end': len(word)} for word in text.split()],
                    'metadata': {'total_words': len(text.split())}
                }
            
            # Step 4: Quality Assessment
            if self.quality_filter and (apply_all_steps or return_full_analysis):
                quality_result = self.quality_filter.calculate_text_quality(
                    text, 
                    result['tokenization']
                )
                result['quality_assessment'] = quality_result
                self.stats['component_usage']['quality_filtering'] += 1
                
                # Check if text meets quality threshold
                if quality_result['overall_score'] < self.config['quality_threshold']:
                    result['processed_text'] = text
                    result['processing_status'] = 'low_quality'
                    result['quality_issues'] = quality_result.get('recommendations', [])
                    result['processing_time'] = time.time() - start_time
                    return result
            
            # Step 5: Set final processed text
            result['processed_text'] = text
            result['processing_status'] = 'completed'
            result['processing_time'] = time.time() - start_time
            
            # Update statistics
            self.stats['total_processed'] += 1
            self.stats['successful_processed'] += 1
            self.stats['processing_times'].append(result['processing_time'])
            
        except Exception as e:
            result['processed_text'] = text
            result['processing_status'] = 'failed'
            result['error'] = str(e)
            result['processing_time'] = time.time() - start_time
            self.stats['total_processed'] += 1
            self.stats['failed_processes'] += 1
        
        return result
    
    def process_texts(self, texts: List[str], 
                     apply_deduplication: bool = True,
                     return_removed_content: bool = False) -> Dict[str, Any]:
        """
        Process multiple texts through the pipeline with optional deduplication
        
        Args:
            texts: List of Pashto texts to process
            apply_deduplication: Apply deduplication after processing
            return_removed_content: Return information about removed content
            
        Returns:
            Comprehensive batch processing results
        """
        start_time = time.time()
        
        if not texts:
            return {
                'input_count': 0,
                'output_count': 0,
                'processing_status': 'no_input',
                'processing_time': 0
            }
        
        # Track processing results
        processing_results = []
        processed_texts = []
        quality_scores = []
        language_results = []
        
        # Process each text individually
        for i, text in enumerate(texts):
            try:
                # Apply only essential processing for batch operations
                result = self.process_text(
                    text, 
                    apply_all_steps=True,
                    return_full_analysis=True
                )
                
                result['text_index'] = i
                result['original_text_index'] = i
                processing_results.append(result)
                
                # Collect successful results
                if result['processing_status'] == 'completed':
                    processed_texts.append(result['processed_text'])
                    
                    # Collect quality score
                    if 'quality_assessment' in result:
                        quality_scores.append(result['quality_assessment']['overall_score'])
                    
                    # Collect language detection result
                    if 'language_detection' in result:
                        language_results.append(result['language_detection'])
                
            except Exception as e:
                print(f"Error processing text {i}: {str(e)}")
                continue
        
        # Apply deduplication if enabled
        deduplication_info = {}
        if apply_deduplication and self.deduplicator and len(processed_texts) > 1:
            deduplication_result = self.deduplicator.deduplicate_texts(
                processed_texts,
                remove_exact=True,
                remove_near_duplicates=True,
                near_duplicate_threshold=self.config['deduplication_threshold']
            )
            
            deduplication_info = {
                'deduplication_applied': True,
                'original_count': len(processed_texts),
                'final_count': deduplication_result['final_count'],
                'removed_exact_duplicates': deduplication_result['removed_exact_duplicates'],
                'removed_near_duplicates': deduplication_result['removed_near_duplicates'],
                'kept_indices': deduplication_result['kept_indices'],
                'duplicate_groups': deduplication_result['duplicate_groups']
            }
            
            # Filter results to only include kept texts
            kept_indices = set(deduplication_result['kept_indices'])
            filtered_results = [r for r in processing_results if r.get('text_index') in kept_indices]
            processing_results = filtered_results
            processed_texts = deduplication_result['kept_texts']
        
        # Calculate final statistics
        total_processing_time = time.time() - start_time
        
        # Language distribution
        language_distribution = {}
        if language_results:
            for lang_result in language_results:
                lang = lang_result.get('detected_language', 'unknown')
                language_distribution[lang] = language_distribution.get(lang, 0) + 1
        
        # Quality distribution
        quality_distribution = {}
        if quality_scores:
            high_quality = sum(1 for score in quality_scores if score >= 0.7)
            medium_quality = sum(1 for score in quality_scores if 0.4 <= score < 0.7)
            low_quality = sum(1 for score in quality_scores if score < 0.4)
            
            quality_distribution = {
                'high': high_quality,
                'medium': medium_quality,
                'low': low_quality,
                'average_score': sum(quality_scores) / len(quality_scores)
            }
        
        batch_result = {
            'input_count': len(texts),
            'output_count': len(processed_texts),
            'processing_status': 'completed',
            'processing_time': total_processing_time,
            'deduplication': deduplication_info,
            'statistics': {
                'language_distribution': language_distribution,
                'quality_distribution': quality_distribution,
                'component_usage': self.stats['component_usage'].copy(),
                'success_rate': len(processed_texts) / len(texts) if texts else 0
            },
            'results': processing_results
        }
        
        if return_removed_content:
            batch_result['removed_content_info'] = {
                'total_removed': len(texts) - len(processed_texts),
                'removal_reasons': self._analyze_removal_reasons(processing_results)
            }
        
        return batch_result
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        stats = self.stats.copy()
        
        # Calculate additional statistics
        if stats['processing_times']:
            stats['average_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])
            stats['max_processing_time'] = max(stats['processing_times'])
            stats['min_processing_time'] = min(stats['processing_times'])
        else:
            stats['average_processing_time'] = 0
            stats['max_processing_time'] = 0
            stats['min_processing_time'] = 0
        
        # Calculate component usage percentages
        total_operations = sum(stats['component_usage'].values())
        if total_operations > 0:
            stats['component_usage_percentages'] = {
                component: (count / total_operations) * 100 
                for component, count in stats['component_usage'].items()
            }
        else:
            stats['component_usage_percentages'] = {}
        
        return stats
    
    def export_results(self, results: Dict[str, Any], output_path: str, 
                      format: str = 'json') -> bool:
        """
        Export processing results to file
        
        Args:
            results: Processing results to export
            output_path: Path to save the results
            format: Output format ('json', 'csv', 'txt')
            
        Returns:
            Success status
        """
        try:
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
            
            elif format.lower() == 'csv':
                # Convert to CSV format (simplified)
                import csv
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    if 'results' in results:
                        writer = csv.writer(f)
                        writer.writerow(['index', 'original_text', 'processed_text', 
                                       'quality_score', 'language', 'status'])
                        
                        for result in results['results']:
                            writer.writerow([
                                result.get('text_index', ''),
                                result.get('original_text', ''),
                                result.get('processed_text', ''),
                                result.get('quality_assessment', {}).get('overall_score', ''),
                                result.get('language_detection', {}).get('detected_language', ''),
                                result.get('processing_status', '')
                            ])
            
            elif format.lower() == 'txt':
                # Simple text format
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("Pashto NLP Processing Results\n")
                    f.write("=" * 40 + "\n\n")
                    
                    if 'results' in results:
                        for i, result in enumerate(results['results']):
                            f.write(f"Text {i+1}:\n")
                            f.write(f"Original: {result.get('original_text', '')}\n")
                            f.write(f"Processed: {result.get('processed_text', '')}\n")
                            f.write(f"Quality Score: {result.get('quality_assessment', {}).get('overall_score', 'N/A')}\n")
                            f.write(f"Language: {result.get('language_detection', {}).get('detected_language', 'N/A')}\n")
                            f.write(f"Status: {result.get('processing_status', 'N/A')}\n")
                            f.write("-" * 30 + "\n\n")
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return True
            
        except Exception as e:
            print(f"Error exporting results: {str(e)}")
            return False
    
    def reset_statistics(self):
        """Reset processing statistics"""
        self.stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processes': 0,
            'processing_times': [],
            'component_usage': {
                'normalization': 0,
                'tokenization': 0,
                'quality_filtering': 0,
                'deduplication': 0,
                'language_detection': 0
            }
        }
    
    def _analyze_removal_reasons(self, processing_results: List[Dict]) -> Dict[str, int]:
        """Analyze reasons for text removal during processing"""
        removal_reasons = {
            'low_quality': 0,
            'not_arabic_script': 0,
            'empty_text': 0,
            'processing_error': 0,
            'other': 0
        }
        
        for result in processing_results:
            status = result.get('processing_status', '')
            
            if status == 'low_quality':
                removal_reasons['low_quality'] += 1
            elif status == 'completed_early' and result.get('early_exit_reason') == 'not_arabic_script':
                removal_reasons['not_arabic_script'] += 1
            elif status == 'failed':
                removal_reasons['processing_error'] += 1
            elif not result.get('original_text', '').strip():
                removal_reasons['empty_text'] += 1
            else:
                removal_reasons['other'] += 1
        
        return removal_reasons
    
    def configure(self, **kwargs):
        """Update processor configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                print(f"Updated configuration: {key} = {value}")
            else:
                print(f"Unknown configuration option: {key}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for detection"""
        if self.language_detector:
            return self.language_detector.supported_languages
        return []
    
    def validate_text(self, text: str) -> Dict[str, Any]:
        """
        Quick validation of text without full processing
        
        Args:
            text: Text to validate
            
        Returns:
            Validation results
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'recommendations': []
        }
        
        if not text or not text.strip():
            validation_result['is_valid'] = False
            validation_result['issues'].append('Text is empty')
            return validation_result
        
        # Check length
        if len(text.strip()) < 3:
            validation_result['is_valid'] = False
            validation_result['issues'].append('Text too short')
            validation_result['recommendations'].append('Add more content')
        
        # Check for Arabic script
        if self.language_detector:
            is_arabic = self.language_detector.is_arabic_script(text)
            if not is_arabic:
                validation_result['is_valid'] = False
                validation_result['issues'].append('No Arabic script detected')
                validation_result['recommendations'].append('Ensure text contains Arabic script characters')
        
        # Check for excessive noise (basic check)
        noise_chars = sum(1 for char in text if char in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()')
        if len(text) > 0 and noise_chars / len(text) > 0.3:
            validation_result['recommendations'].append('High amount of non-Arabic characters detected')
        
        return validation_result