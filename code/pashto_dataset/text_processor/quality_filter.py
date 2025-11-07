"""
Quality Filter for Pashto Text

Provides comprehensive quality assessment and filtering for Pashto text:
- Content quality scoring
- Language purity assessment
- Readability metrics
- Spam and noise detection
- Pashto-specific quality indicators
"""

import re
import math
from typing import Dict, List, Tuple, Any
from collections import Counter

class QualityFilter:
    """Advanced quality filtering system for Pashto text"""
    
    def __init__(self):
        # Quality thresholds
        self.thresholds = {
            'min_length': 5,
            'max_length': 50000,
            'min_word_count': 2,
            'max_repetition_ratio': 0.3,
            'min_pashto_score': 0.1,
            'min_similarity_threshold': 0.8
        }
        
        # Common noise patterns in Pashto text
        self.noise_patterns = [
            r'(http[s]?://[^\s]+)',  # URLs
            r'(www\.[^\s]+)',        # Website references
            r'([a-zA-Z]{3,})',       # Long English words (potential noise)
            r'(\d{3,})',             # Long numbers
            r'([!@#$%^&*()]{3,})',   # Multiple special characters
            r'(.{50,})',             # Very long single words
        ]
        
        # Pashto quality indicators
        self.pashto_indicators = {
            'common_words': [
                'زه', 'تاسو', 'دوی', 'موږ', 'هغه', 'دا', 'دده', 'تر', 'پر', 
                'سره', 'څخه', 'ته', 'ځان', 'کور', 'ژوند', 'ورځ', 'شپه',
                'ښه', 'بد', 'لوی', 'وړه', 'ډیر', 'کم', 'نوی', 'زړه'
            ],
            'common_verbs': [
                'لري', 'دی', 'دي', 'کول', 'ورکړل', 'اخیستل', 'تلل', 'راتلل',
                'ویل', 'ورلیکل', 'ورسره', 'بولی', 'پوهیدل'
            ],
            'pashto_particles': [
                'دي', 'دی', 'څه', 'په', 'سره', 'تر', 'پر', 'سره', 'دوي'
            ]
        }
        
        # Repetition patterns to detect
        self.repetition_patterns = {
            'repeated_chars': re.compile(r'(.)\1{3,}'),
            'repeated_sequences': re.compile(r'(\w+)\1{2,}'),
            'repeated_punctuation': re.compile(r'([،؛؟۔!]{2,})'),
        }
        
        # Quality scoring weights
        self.quality_weights = {
            'length_score': 0.2,
            'pashto_content_score': 0.3,
            'readability_score': 0.2,
            'structure_score': 0.2,
            'cleanliness_score': 0.1
        }
    
    def calculate_text_quality(self, text: str, tokenization_data: Dict = None) -> Dict[str, Any]:
        """
        Calculate comprehensive quality score for Pashto text
        
        Args:
            text: The text to evaluate
            tokenization_data: Optional tokenization data from PashtoTokenizer
            
        Returns:
            Dictionary containing quality metrics and overall score
        """
        if not text or not text.strip():
            return self._empty_quality_result()
        
        quality_metrics = {}
        scores = {}
        
        # 1. Length-based scoring
        scores['length_score'] = self._calculate_length_score(text)
        quality_metrics['length'] = {
            'char_count': len(text),
            'word_count': len(text.split()) if tokenization_data is None else len(tokenization_data.get('words', [])),
            'sentence_count': len(tokenization_data.get('sentences', [])) if tokenization_data else 1,
            'score': scores['length_score']
        }
        
        # 2. Pashto content quality
        scores['pashto_content_score'] = self._calculate_pashto_content_score(text, tokenization_data)
        quality_metrics['pashto_content'] = {
            'pashto_word_ratio': self._calculate_pashto_word_ratio(text),
            'pashto_indicator_score': self._calculate_pashto_indicators(text),
            'script_purity': self._calculate_script_purity(text),
            'score': scores['pashto_content_score']
        }
        
        # 3. Readability score
        scores['readability_score'] = self._calculate_readability_score(text, tokenization_data)
        quality_metrics['readability'] = {
            'average_word_length': self._calculate_average_word_length(text),
            'sentence_variety': self._calculate_sentence_variety(text),
            'lexical_diversity': self._calculate_lexical_diversity(text),
            'score': scores['readability_score']
        }
        
        # 4. Structural quality
        scores['structure_score'] = self._calculate_structure_score(text, tokenization_data)
        quality_metrics['structure'] = {
            'has_proper_punctuation': self._check_proper_punctuation(text),
            'sentence_completeness': self._assess_sentence_completeness(text, tokenization_data),
            'paragraph_structure': self._assess_paragraph_structure(text),
            'score': scores['structure_score']
        }
        
        # 5. Cleanliness score
        scores['cleanliness_score'] = self._calculate_cleanliness_score(text)
        quality_metrics['cleanliness'] = {
            'noise_ratio': self._calculate_noise_ratio(text),
            'repetition_ratio': self._calculate_repetition_ratio(text),
            'encoding_issues': self._detect_encoding_issues(text),
            'score': scores['cleanliness_score']
        }
        
        # Calculate overall quality score
        overall_score = sum(
            score * self.quality_weights[category] 
            for category, score in scores.items()
        )
        
        # Determine quality grade
        grade = self._determine_quality_grade(overall_score)
        
        # Filtering decision
        should_keep = self._should_keep_text(overall_score, quality_metrics)
        
        return {
            'overall_score': round(overall_score, 3),
            'grade': grade,
            'should_keep': should_keep,
            'scores': scores,
            'quality_metrics': quality_metrics,
            'recommendations': self._generate_recommendations(quality_metrics)
        }
    
    def filter_texts(self, texts: List[str], tokenization_data: List[Dict] = None) -> List[Dict]:
        """
        Filter multiple texts based on quality criteria
        """
        results = []
        
        for i, text in enumerate(texts):
            token_data = tokenization_data[i] if tokenization_data and i < len(tokenization_data) else None
            quality_result = self.calculate_text_quality(text, token_data)
            quality_result['text_index'] = i
            quality_result['original_text'] = text
            results.append(quality_result)
        
        return results
    
    def batch_filter(self, texts: List[str], min_quality_threshold: float = 0.3) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter texts and return both high and low quality texts
        """
        all_results = self.filter_texts(texts)
        
        high_quality = [result for result in all_results if result['should_keep']]
        low_quality = [result for result in all_results if not result['should_keep']]
        
        return high_quality, low_quality
    
    def _empty_quality_result(self) -> Dict:
        """Return empty quality result for invalid input"""
        return {
            'overall_score': 0.0,
            'grade': 'invalid',
            'should_keep': False,
            'scores': {},
            'quality_metrics': {},
            'recommendations': ['Text is empty or invalid']
        }
    
    def _calculate_length_score(self, text: str) -> float:
        """Calculate score based on text length"""
        length = len(text)
        if length < self.thresholds['min_length']:
            return 0.0
        elif length > self.thresholds['max_length']:
            return 0.5  # Penalize very long texts
        
        # Optimal range: 50-500 characters
        if 50 <= length <= 500:
            return 1.0
        elif 20 <= length <= 1000:
            return 0.7
        else:
            return 0.4
    
    def _calculate_pashto_content_score(self, text: str, tokenization_data: Dict = None) -> float:
        """Calculate score based on Pashto content quality"""
        if not text:
            return 0.0
        
        # Calculate components
        pashto_word_ratio = self._calculate_pashto_word_ratio(text)
        pashto_indicators = self._calculate_pashto_indicators(text)
        script_purity = self._calculate_script_purity(text)
        
        # Weighted combination
        return (pashto_word_ratio * 0.4 + pashto_indicators * 0.3 + script_purity * 0.3)
    
    def _calculate_readability_score(self, text: str, tokenization_data: Dict = None) -> float:
        """Calculate readability score"""
        if not text:
            return 0.0
        
        # Calculate readability components
        avg_word_length = self._calculate_average_word_length(text)
        sentence_variety = self._calculate_sentence_variety(text)
        lexical_diversity = self._calculate_lexical_diversity(text)
        
        # Score based on optimal ranges
        word_length_score = 1.0 - abs(avg_word_length - 6) / 10  # Optimal ~6 chars
        sentence_score = min(sentence_variety / 3, 1.0)  # Good variety
        diversity_score = lexical_diversity
        
        return (word_length_score * 0.3 + sentence_score * 0.3 + diversity_score * 0.4)
    
    def _calculate_structure_score(self, text: str, tokenization_data: Dict = None) -> float:
        """Calculate structural quality score"""
        scores = []
        
        # Check punctuation
        has_punctuation = self._check_proper_punctuation(text)
        scores.append(1.0 if has_punctuation else 0.5)
        
        # Check sentence completeness
        sentence_completeness = self._assess_sentence_completeness(text, tokenization_data)
        scores.append(sentence_completeness)
        
        # Check paragraph structure
        paragraph_structure = self._assess_paragraph_structure(text)
        scores.append(paragraph_structure)
        
        return sum(scores) / len(scores)
    
    def _calculate_cleanliness_score(self, text: str) -> float:
        """Calculate text cleanliness score"""
        # Calculate cleanliness components
        noise_ratio = self._calculate_noise_ratio(text)
        repetition_ratio = self._calculate_repetition_ratio(text)
        encoding_issues = self._detect_encoding_issues(text)
        
        # Cleanliness score: lower noise = higher score
        cleanliness = 1.0 - (noise_ratio + repetition_ratio + encoding_issues) / 3
        return max(0.0, min(1.0, cleanliness))
    
    def _calculate_pashto_word_ratio(self, text: str) -> float:
        """Calculate ratio of words that appear to be Pashto"""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        pashto_chars = 'ځڅډړګڼ'
        pashto_word_count = 0
        
        for word in words:
            if any(char in pashto_chars for char in word):
                pashto_word_count += 1
        
        return pashto_word_count / len(words)
    
    def _calculate_pashto_indicators(self, text: str) -> float:
        """Calculate score based on Pashto-specific indicators"""
        if not text:
            return 0.0
        
        score = 0.0
        total_indicators = 0
        
        for category, words in self.pashto_indicators.items():
            for word in words:
                if word in text:
                    score += 1
                total_indicators += 1
        
        return score / total_indicators if total_indicators > 0 else 0.0
    
    def _calculate_script_purity(self, text: str) -> float:
        """Calculate script purity (how much is Arabic script)"""
        if not text:
            return 0.0
        
        # Arabic script Unicode ranges
        arabic_ranges = [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)]
        arabic_count = 0
        total_count = 0
        
        for char in text:
            total_count += 1
            for start, end in arabic_ranges:
                if start <= ord(char) <= end:
                    arabic_count += 1
                    break
        
        return arabic_count / total_count if total_count > 0 else 0.0
    
    def _calculate_average_word_length(self, text: str) -> float:
        """Calculate average word length"""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        return sum(len(word) for word in words) / len(words)
    
    def _calculate_sentence_variety(self, text: str) -> float:
        """Calculate sentence length variety"""
        sentences = re.split(r'[.!?؟۔]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.5
        
        lengths = [len(s) for s in sentences]
        mean_length = sum(lengths) / len(lengths)
        variance = sum((l - mean_length) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        # Normalize by mean (coefficient of variation)
        return std_dev / mean_length if mean_length > 0 else 0.0
    
    def _calculate_lexical_diversity(self, text: str) -> float:
        """Calculate lexical diversity (unique words / total words)"""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        unique_words = set(words)
        return len(unique_words) / len(words)
    
    def _check_proper_punctuation(self, text: str) -> bool:
        """Check if text has proper punctuation"""
        # Look for sentence endings and proper spacing
        has_ending = any(punct in text for punct in '.!?؟۔')
        has_mixed_punct = len([p for p in ',؛؟' if p in text]) > 0
        
        return has_ending and has_mixed_punct
    
    def _assess_sentence_completeness(self, text: str, tokenization_data: Dict = None) -> float:
        """Assess how complete sentences are"""
        if tokenization_data and 'sentences' in tokenization_data:
            sentences = tokenization_data['sentences']
        else:
            sentences = re.split(r'[.!?؟۔]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        complete_sentences = sum(1 for s in sentences if len(s.split()) >= 3)
        return complete_sentences / len(sentences)
    
    def _assess_paragraph_structure(self, text: str) -> float:
        """Assess paragraph structure quality"""
        # Simple paragraph detection based on line breaks
        paragraphs = text.split('\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        if not paragraphs:
            return 0.5
        
        # Score based on paragraph count and average length
        paragraph_count = len(paragraphs)
        avg_length = sum(len(p) for p in paragraphs) / paragraph_count
        
        # Good structure: multiple paragraphs with reasonable length
        if paragraph_count > 1 and 20 < avg_length < 500:
            return 1.0
        elif paragraph_count > 0:
            return 0.7
        else:
            return 0.3
    
    def _calculate_noise_ratio(self, text: str) -> float:
        """Calculate ratio of noise to content"""
        if not text:
            return 0.0
        
        noise_count = 0
        for pattern in self.noise_patterns:
            noise_count += len(re.findall(pattern, text))
        
        return noise_count / len(text) if len(text) > 0 else 0.0
    
    def _calculate_repetition_ratio(self, text: str) -> float:
        """Calculate ratio of repeated content"""
        if not text:
            return 0.0
        
        repetition_count = 0
        
        # Check for repeated characters
        for pattern in self.repetition_patterns.values():
            matches = pattern.findall(text)
            repetition_count += len(matches)
        
        return repetition_count / len(text) if len(text) > 0 else 0.0
    
    def _detect_encoding_issues(self, text: str) -> float:
        """Detect potential encoding issues"""
        if not text:
            return 0.0
        
        # Look for suspicious character combinations
        suspicious_patterns = [
            r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]',  # Control characters
            r'�',  # Replacement character
        ]
        
        issue_count = 0
        for pattern in suspicious_patterns:
            issue_count += len(re.findall(pattern, text))
        
        return issue_count / len(text) if len(text) > 0 else 0.0
    
    def _determine_quality_grade(self, score: float) -> str:
        """Determine quality grade based on score"""
        if score >= 0.8:
            return 'excellent'
        elif score >= 0.6:
            return 'good'
        elif score >= 0.4:
            return 'fair'
        elif score >= 0.2:
            return 'poor'
        else:
            return 'very_poor'
    
    def _should_keep_text(self, score: float, metrics: Dict) -> bool:
        """Determine if text should be kept based on quality criteria"""
        # Must meet minimum score
        if score < self.thresholds['min_pashto_score']:
            return False
        
        # Check for excessive noise
        cleanliness = metrics.get('cleanliness', {})
        if cleanliness.get('score', 1.0) < 0.3:
            return False
        
        # Check for reasonable content
        length = metrics.get('length', {})
        if length.get('word_count', 0) < self.thresholds['min_word_count']:
            return False
        
        return True
    
    def _generate_recommendations(self, quality_metrics: Dict) -> List[str]:
        """Generate improvement recommendations based on quality metrics"""
        recommendations = []
        
        # Length recommendations
        length_metrics = quality_metrics.get('length', {})
        if length_metrics.get('word_count', 0) < 3:
            recommendations.append("Consider adding more content for better quality")
        
        # Content recommendations
        content_metrics = quality_metrics.get('pashto_content', {})
        if content_metrics.get('pashto_word_ratio', 1.0) < 0.5:
            recommendations.append("Increase Pashto content or improve language mixing")
        
        if content_metrics.get('script_purity', 1.0) < 0.7:
            recommendations.append("Standardize script usage for better consistency")
        
        # Cleanliness recommendations
        cleanliness = quality_metrics.get('cleanliness', {})
        if cleanliness.get('noise_ratio', 0) > 0.1:
            recommendations.append("Remove noise and irrelevant content")
        
        if cleanliness.get('repetition_ratio', 0) > 0.1:
            recommendations.append("Reduce repetitive content")
        
        if not recommendations:
            recommendations.append("Text quality is good")
        
        return recommendations