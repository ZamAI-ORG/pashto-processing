"""
Quality Assessor for Pashto Text Extraction

This module provides quality assessment capabilities for evaluating the quality
of extracted Pashto text from PDF documents.
"""

import re
import math
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter
import numpy as np
from .pashto_utils import PashtoTextUtils


class QualityAssessor:
    """
    Assesses the quality of extracted Pashto text from PDF documents.
    """
    
    def __init__(self):
        """Initialize quality assessor."""
        self.pashto_utils = PashtoTextUtils()
        
        # Quality thresholds
        self.thresholds = {
            'excellent': {
                'pashto_ratio': 0.7,
                'text_density': 0.8,
                'word_coverage': 0.8,
                'sentence_coherence': 0.7,
                'character_quality': 0.8
            },
            'good': {
                'pashto_ratio': 0.5,
                'text_density': 0.6,
                'word_coverage': 0.6,
                'sentence_coherence': 0.5,
                'character_quality': 0.6
            },
            'acceptable': {
                'pashto_ratio': 0.3,
                'text_density': 0.4,
                'word_coverage': 0.4,
                'sentence_coherence': 0.3,
                'character_quality': 0.4
            }
        }
        
        # Common Pashto words for validation
        self.common_pashto_words = {
            'د', 'په', 'سره', 'ته', 'له', 'څخه', 'ډول', 'لکه', 'نو', 'هم',
            'او', 'یا', 'مګر', 'خو', 'چې', 'که', 'نه', 'بل', 'نور', 'ډېر',
            'زموږ', 'زموږ', 'ستاسو', 'دوی', 'دوی', 'هغه', 'دا', 'داده',
            'لومړی', 'دویم', 'دریم', 'شپږم', 'آخر', 'وړاندې', ' وروسته'
        }
        
        # Pashto punctuation patterns
        self.punctuation_patterns = {
            'pashto_punctuation': r'[،۔؟٫٬]',
            'standard_punctuation': r'[.,!?;:]',
            'brackets': r'[\[\]\(\)\{\}]',
            'quotes': r'["\'""]'
        }
    
    def assess_document(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the overall quality of a document extraction.
        
        Args:
            result: Document processing result
            
        Returns:
            Quality assessment report
        """
        try:
            # Extract relevant data
            full_text = result.get('full_text', '')
            cleaned_text = result.get('cleaned_text', '')
            normalized_text = result.get('normalized_text', '')
            total_pages = result.get('total_pages', 0)
            processed_pages = result.get('processed_pages', 0)
            
            # Perform various quality checks
            metrics = {}
            
            # Basic text metrics
            metrics['basic_metrics'] = self._assess_basic_metrics(
                full_text, cleaned_text, normalized_text
            )
            
            # Language quality
            metrics['language_quality'] = self._assess_language_quality(normalized_text)
            
            # Content quality
            metrics['content_quality'] = self._assess_content_quality(
                normalized_text, total_pages, processed_pages
            )
            
            # Structure quality
            metrics['structure_quality'] = self._assess_structure_quality(full_text)
            
            # Technical quality
            metrics['technical_quality'] = self._assess_technical_quality(
                result.get('pages', []), full_text
            )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(metrics)
            quality_grade = self._determine_quality_grade(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics, quality_grade)
            
            assessment_report = {
                'overall_score': overall_score,
                'quality_grade': quality_grade,
                'metrics': metrics,
                'recommendations': recommendations,
                'assessment_timestamp': np.datetime64('now'),
                'text_statistics': self.pashto_utils.get_text_statistics(normalized_text)
            }
            
            return assessment_report
            
        except Exception as e:
            return {
                'error': str(e),
                'overall_score': 0.0,
                'quality_grade': 'failed',
                'assessment_successful': False
            }
    
    def _assess_basic_metrics(self, full_text: str, cleaned_text: str, 
                            normalized_text: str) -> Dict[str, float]:
        """Assess basic text metrics."""
        metrics = {}
        
        # Text length metrics
        metrics['full_text_length'] = len(full_text)
        metrics['cleaned_text_length'] = len(cleaned_text)
        metrics['normalized_text_length'] = len(normalized_text)
        metrics['compression_ratio'] = (
            len(cleaned_text) / len(full_text) if full_text else 0
        )
        
        # Word count metrics
        full_words = self.pashto_utils.extract_words(full_text)
        cleaned_words = self.pashto_utils.extract_words(cleaned_text)
        normalized_words = self.pashto_utils.extract_words(normalized_text)
        
        metrics['full_text_words'] = len(full_words)
        metrics['cleaned_text_words'] = len(cleaned_words)
        metrics['normalized_text_words'] = len(normalized_words)
        
        # Density metrics
        if full_text:
            metrics['text_density'] = len(cleaned_words) / len(full_words) * 100
        else:
            metrics['text_density'] = 0.0
        
        return metrics
    
    def _assess_language_quality(self, text: str) -> Dict[str, float]:
        """Assess language-specific quality metrics."""
        if not text:
            return {'error': 'No text to assess'}
        
        metrics = {}
        
        # Character analysis
        text_stats = self.pashto_utils.get_text_statistics(text)
        metrics['pashto_ratio'] = text_stats.get('pashto_ratio', 0.0)
        metrics['alphabetic_ratio'] = (
            text_stats.get('alphabetic_characters', 0) / 
            max(text_stats.get('total_characters', 1), 1)
        )
        
        # Word analysis
        words = self.pashto_utils.extract_words(text)
        word_freq = self.pashto_utils.get_word_frequency(text)
        
        # Common word ratio (quality indicator)
        common_word_count = sum(1 for word in words if word in self.common_pashto_words)
        metrics['common_word_ratio'] = common_word_count / len(words) if words else 0.0
        
        # Word length distribution
        word_lengths = [len(word) for word in words]
        avg_word_length = np.mean(word_lengths) if word_lengths else 0
        metrics['average_word_length'] = avg_word_length
        
        # Vocabulary richness
        unique_words = len(set(words))
        metrics['vocabulary_richness'] = unique_words / len(words) if words else 0.0
        
        # Character quality
        metrics['character_quality'] = self._assess_character_quality(text)
        
        return metrics
    
    def _assess_content_quality(self, text: str, total_pages: int, 
                              processed_pages: int) -> Dict[str, float]:
        """Assess content quality metrics."""
        metrics = {}
        
        # Page processing success rate
        metrics['page_success_rate'] = (
            processed_pages / total_pages if total_pages > 0 else 0
        )
        
        # Content completeness
        sentences = self.pashto_utils.extract_sentences(text)
        metrics['sentence_count'] = len(sentences)
        metrics['avg_sentence_length'] = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        
        # Content coherence indicators
        metrics['content_coherence'] = self._assess_content_coherence(sentences)
        
        # Information density
        if text:
            info_indicators = self._count_information_indicators(text)
            total_chars = len(text)
            metrics['information_density'] = info_indicators / total_chars if total_chars > 0 else 0
        else:
            metrics['information_density'] = 0
        
        return metrics
    
    def _assess_structure_quality(self, text: str) -> Dict[str, float]:
        """Assess structural quality of the text."""
        metrics = {}
        
        # Line structure
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        metrics['line_count'] = len(lines)
        metrics['avg_line_length'] = np.mean([len(line) for line in lines]) if lines else 0
        
        # Punctuation analysis
        pashto_punct_count = len(re.findall(self.punctuation_patterns['pashto_punctuation'], text))
        standard_punct_count = len(re.findall(self.punctuation_patterns['standard_punctuation'], text))
        bracket_count = len(re.findall(self.punctuation_patterns['brackets'], text))
        quote_count = len(re.findall(self.punctuation_patterns['quotes'], text))
        
        total_punct = pashto_punct_count + standard_punct_count
        if total_punct > 0:
            metrics['pashto_punctuation_ratio'] = pashto_punct_count / total_punct
        else:
            metrics['pashto_punctuation_ratio'] = 0.0
        
        metrics['punctuation_diversity'] = (pashto_punct_count > 0) + (standard_punct_count > 0) + (bracket_count > 0) + (quote_count > 0)
        
        # Paragraph structure
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        metrics['paragraph_count'] = len(paragraphs)
        metrics['avg_paragraph_length'] = np.mean([len(p.split()) for p in paragraphs]) if paragraphs else 0
        
        return metrics
    
    def _assess_technical_quality(self, pages: List[Dict], full_text: str) -> Dict[str, float]:
        """Assess technical quality of extraction."""
        metrics = {}
        
        # Page-level analysis
        extraction_methods = [page.get('extraction_method', 'unknown') for page in pages]
        method_counts = Counter(extraction_methods)
        
        metrics['direct_extraction_rate'] = method_counts.get('direct', 0) / len(pages) if pages else 0
        metrics['ocr_extraction_rate'] = method_counts.get('ocr', 0) / len(pages) if pages else 0
        metrics['error_rate'] = method_counts.get('error', 0) / len(pages) if pages else 0
        
        # Confidence analysis
        confidences = [page.get('confidence', 0) for page in pages if page.get('confidence', 0) > 0]
        if confidences:
            metrics['average_confidence'] = np.mean(confidences)
            metrics['confidence_std'] = np.std(confidences)
            metrics['high_confidence_pages'] = sum(1 for c in confidences if c >= 0.8) / len(confidences)
        else:
            metrics['average_confidence'] = 0.0
            metrics['confidence_std'] = 0.0
            metrics['high_confidence_pages'] = 0.0
        
        # Text continuity
        metrics['text_continuity'] = self._assess_text_continuity(pages)
        
        return metrics
    
    def _assess_character_quality(self, text: str) -> float:
        """Assess character-level quality of the text."""
        if not text:
            return 0.0
        
        # Check for common OCR/encoding errors
        error_patterns = {
            'encoding_errors': r'[^\w\s\.,!?;:\-()"\']',  # Invalid characters
            'repeated_chars': r'(.)\1{3,}',  # Repeated characters
            'broken_words': r'\b\w{1,2}\s+\w{1,2}\b',  # Likely broken words
            'mixed_encoding': r'[a-zA-Z]{3,}[^\w\s]*[۰-۹]'  # Mixed language errors
        }
        
        total_issues = 0
        text_length = len(text)
        
        for error_type, pattern in error_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            total_issues += matches
        
        # Calculate quality score (inverse of error rate)
        if text_length == 0:
            return 0.0
        
        error_rate = total_issues / text_length
        quality_score = max(0.0, 1.0 - error_rate)
        
        return quality_score
    
    def _assess_content_coherence(self, sentences: List[str]) -> float:
        """Assess coherence of content."""
        if len(sentences) < 2:
            return 1.0
        
        # Simple coherence measures
        coherence_score = 0.0
        
        # Sentence length consistency
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = np.var(sentence_lengths) if sentence_lengths else 0
        length_consistency = 1.0 / (1.0 + length_variance / 100)  # Normalize
        
        # Transition word presence
        transition_words = ['او', 'مګر', 'نو', 'که', 'چې', 'بیا', 'بیا', 'نو']
        transition_count = sum(1 for sentence in sentences for word in transition_words if word in sentence)
        transition_ratio = transition_count / len(sentences) if sentences else 0
        
        # Combine measures
        coherence_score = (length_consistency * 0.6) + (min(transition_ratio, 0.5) * 0.4)
        
        return min(coherence_score, 1.0)
    
    def _count_information_indicators(self, text: str) -> int:
        """Count information density indicators."""
        # Count various information indicators
        indicators = {
            'numbers': len(re.findall(r'\d+', text)),
            'proper_nouns': len(re.findall(r'\b[A-Z][a-z]+\b', text)),
            'technical_terms': len(re.findall(r'\b[A-Z]{2,}\b', text)),
            'dates': len(re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)),
            'proper_pashto': len(re.findall(r'\b[څږښځګړڼڝڟڧڑښږډ]', text))
        }
        
        return sum(indicators.values())
    
    def _assess_text_continuity(self, pages: List[Dict]) -> float:
        """Assess continuity of text across pages."""
        if len(pages) < 2:
            return 1.0
        
        # Check for page numbering
        page_numbers = []
        for i, page in enumerate(pages):
            text = page.get('text', '')
            # Look for page numbers
            page_num_matches = re.findall(r'(?:Page|صفحه)\s*(\d+)', text, re.IGNORECASE)
            if page_num_matches:
                try:
                    page_numbers.append(int(page_num_matches[0]))
                except ValueError:
                    pass
            else:
                page_numbers.append(i + 1)
        
        if len(page_numbers) > 1:
            # Check if page numbers are sequential
            expected_sequence = list(range(1, len(page_numbers) + 1))
            correct_positions = sum(1 for actual, expected in zip(page_numbers, expected_sequence) 
                                  if actual == expected)
            continuity_score = correct_positions / len(page_numbers)
        else:
            continuity_score = 0.5  # No clear page numbering
        
        return continuity_score
    
    def _calculate_overall_score(self, metrics: Dict[str, Dict]) -> float:
        """Calculate overall quality score."""
        weights = {
            'basic_metrics': 0.1,
            'language_quality': 0.3,
            'content_quality': 0.25,
            'structure_quality': 0.15,
            'technical_quality': 0.2
        }
        
        component_scores = {}
        
        # Basic metrics score
        basic = metrics.get('basic_metrics', {})
        basic_score = min(basic.get('text_density', 0) / 100, 1.0)
        component_scores['basic_metrics'] = basic_score
        
        # Language quality score
        language = metrics.get('language_quality', {})
        lang_score = (
            language.get('pashto_ratio', 0) * 0.3 +
            language.get('common_word_ratio', 0) * 0.2 +
            language.get('character_quality', 0) * 0.3 +
            language.get('vocabulary_richness', 0) * 0.2
        )
        component_scores['language_quality'] = lang_score
        
        # Content quality score
        content = metrics.get('content_quality', {})
        content_score = (
            content.get('page_success_rate', 0) * 0.4 +
            content.get('content_coherence', 0) * 0.3 +
            min(content.get('information_density', 0) * 10, 1.0) * 0.3
        )
        component_scores['content_quality'] = content_score
        
        # Structure quality score
        structure = metrics.get('structure_quality', {})
        struct_score = (
            min(structure.get('pashto_punctuation_ratio', 0), 1.0) * 0.4 +
            min(structure.get('punctuation_diversity', 0) / 4, 1.0) * 0.3 +
            min(structure.get('avg_paragraph_length', 0) / 50, 1.0) * 0.3
        )
        component_scores['structure_quality'] = struct_score
        
        # Technical quality score
        technical = metrics.get('technical_quality', {})
        tech_score = (
            technical.get('direct_extraction_rate', 0) * 0.3 +
            technical.get('average_confidence', 0) * 0.4 +
            technical.get('text_continuity', 0) * 0.3
        )
        component_scores['technical_quality'] = tech_score
        
        # Calculate weighted overall score
        overall_score = sum(
            component_scores[component] * weights[component] 
            for component in weights.keys()
        )
        
        return min(overall_score, 1.0)
    
    def _determine_quality_grade(self, score: float) -> str:
        """Determine quality grade from score."""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'acceptable'
        elif score >= 0.2:
            return 'poor'
        else:
            return 'failed'
    
    def _generate_recommendations(self, metrics: Dict[str, Dict], 
                                quality_grade: str) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Language quality recommendations
        language = metrics.get('language_quality', {})
        if language.get('pashto_ratio', 0) < 0.5:
            recommendations.append("Consider using better Pashto OCR training or font recognition")
        
        if language.get('character_quality', 0) < 0.6:
            recommendations.append("Apply additional text cleaning to remove character encoding errors")
        
        # Content quality recommendations
        content = metrics.get('content_quality', {})
        if content.get('page_success_rate', 0) < 0.8:
            recommendations.append("Improve page processing to handle more pages successfully")
        
        if content.get('content_coherence', 0) < 0.5:
            recommendations.append("Review text extraction for better sentence boundary detection")
        
        # Technical quality recommendations
        technical = metrics.get('technical_quality', {})
        if technical.get('direct_extraction_rate', 0) < 0.5:
            recommendations.append("Optimize PDF text extraction settings for digital documents")
        
        if technical.get('average_confidence', 0) < 0.6:
            recommendations.append("Improve OCR preprocessing and parameter tuning")
        
        # Overall recommendations based on grade
        if quality_grade == 'failed':
            recommendations.append("Document extraction failed - check file integrity and format")
        elif quality_grade == 'poor':
            recommendations.append("Significant quality issues detected - manual review recommended")
        elif quality_grade == 'acceptable':
            recommendations.append("Content is usable but could benefit from additional processing")
        
        return recommendations
    
    def compare_extraction_quality(self, result1: Dict, result2: Dict) -> Dict[str, Any]:
        """Compare quality between two extraction results."""
        assessment1 = self.assess_document(result1)
        assessment2 = self.assess_document(result2)
        
        comparison = {
            'result1_score': assessment1.get('overall_score', 0),
            'result2_score': assessment2.get('overall_score', 0),
            'quality_improvement': assessment2.get('overall_score', 0) - assessment1.get('overall_score', 0),
            'result1_grade': assessment1.get('quality_grade', 'unknown'),
            'result2_grade': assessment2.get('quality_grade', 'unknown'),
            'detailed_comparison': {}
        }
        
        # Compare individual metrics
        metrics1 = assessment1.get('metrics', {})
        metrics2 = assessment2.get('metrics', {})
        
        for category in metrics1.keys():
            if category in metrics2:
                comparison['detailed_comparison'][category] = {
                    'metric': category,
                    'result1': metrics1[category],
                    'result2': metrics2[category]
                }
        
        return comparison