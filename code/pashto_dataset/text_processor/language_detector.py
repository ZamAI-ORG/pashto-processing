"""
Pashto Language Detector

Advanced language detection for Pashto text:
- Script-based language identification
- Character frequency analysis
- Pashto-specific linguistic patterns
- Arabic script language discrimination
- Confidence scoring and validation
"""

import re
from typing import Dict, List, Tuple, Any
from collections import Counter
import math

class PashtoLanguageDetector:
    """Specialized language detection for Pashto text"""
    
    def __init__(self):
        # Arabic script languages for comparison
        self.supported_languages = ['pashto', 'arabic', 'persian', 'urdu', 'kurdish']
        
        # Pashto-specific characters (most discriminative)
        self.pashto_unique_chars = {
            'ځ': {'weight': 3.0, 'name': 'Pashto Tteh'},
            'څ': {'weight': 3.0, 'name': 'Pashto Tcheh'},
            'ډ': {'weight': 2.5, 'name': 'Pashto Dal-ring'},
            'ړ': {'weight': 2.5, 'name': 'Pashto Rail'},
            'ږ': {'weight': 2.0, 'name': 'Pashto Ghayn'},
            'ګ': {'weight': 2.0, 'name': 'Pashto Kaf'},
            'ڼ': {'weight': 1.5, 'name': 'Pashto Noon-ring'},
        }
        
        # Common Pashto words for validation
        self.pashto_common_words = {
            # Pronouns
            'زه': 1.0, 'ته': 1.0, 'هغه': 1.0, 'دا': 1.0, 'موږ': 1.0, 'تاسو': 1.0, 'دوی': 1.0,
            # Prepositions
            'په': 1.0, 'د': 1.0, 'تر': 1.0, 'سره': 1.0, 'څخه': 1.0, 'ته': 1.0, 'راسره': 1.0,
            # Verbs
            'لري': 1.0, 'دی': 1.0, 'دي': 1.0, 'کول': 1.0, 'ورکړل': 1.0, 'ویل': 1.0, 'تلل': 1.0,
            # Common nouns
            'کور': 0.8, 'ژوند': 0.8, 'ورځ': 0.8, 'شپه': 0.8, 'انسان': 0.8, 'ښځه': 0.8, 'سړی': 0.8,
            # Adjectives
            'ښه': 0.8, 'بد': 0.8, 'لوی': 0.8, 'وړه': 0.8, 'نوی': 0.8, 'زړه': 0.8,
            # Particles
            'هم': 0.6, 'یا': 0.6, 'نه': 0.6, 'اوس': 0.6, 'بیا': 0.6
        }
        
        # Arabic script Unicode ranges
        self.arabic_ranges = [
            (0x0600, 0x06FF),      # Arabic
            (0x0750, 0x077F),      # Arabic Supplement
            (0x08A0, 0x08FF),      # Arabic Extended-A
            (0xFB50, 0xFDFF),      # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF),      # Arabic Presentation Forms-B
        ]
        
        # Language-specific character patterns
        self.language_patterns = {
            'pashto': [
                r'ځ', r'څ', r'ډ', r'ړ',  # Pashto-specific characters
                r'\bزه\b', r'\bته\b', r'\bهغه\b', r'\bدا\b',  # Pronouns
                r'\bپه\b', r'\bتر\b', r'\bسره\b', r'\bڅخه\b'  # Prepositions
            ],
            'arabic': [
                r'ال', r'في', r'من', r'إلى', r'على',  # Arabic specific words
                r'الله', r'محمد', r'إسلام'  # Religious terms
            ],
            'persian': [
                r'می', r'را', r'های', r'های',  # Persian grammar markers
                r'که', r'تا', r'تا'  # Persian particles
            ],
            'urdu': [
                r'کہ', r'میں', r'کی', r'تھا',  # Urdu specific
                r'اگر', r'تو', r'ہے'  # Urdu words
            ]
        }
        
        # Character frequency baseline for Arabic script languages
        self.baseline_frequencies = {
            'pashto': {
                'ا': 0.08, 'ب': 0.05, 'ت': 0.04, 'س': 0.04, 'ر': 0.04, 'د': 0.04,
                'ل': 0.03, 'ه': 0.03, 'و': 0.03, 'ن': 0.03, 'م': 0.02, 'ی': 0.02
            },
            'arabic': {
                'ا': 0.10, 'ل': 0.08, 'و': 0.06, 'ن': 0.05, 'ر': 0.05, 'د': 0.04,
                'م': 0.04, 'ه': 0.04, 'ب': 0.04, 'ت': 0.03, 'س': 0.03, 'ی': 0.02
            }
        }
    
    def is_arabic_script(self, text: str) -> bool:
        """Check if text contains Arabic script characters"""
        if not text:
            return False
        
        arabic_count = 0
        for char in text:
            if self._is_arabic_char(char):
                arabic_count += 1
        
        total_count = len([c for c in text if c.strip()])
        return arabic_count / total_count > 0.3 if total_count > 0 else False
    
    def _is_arabic_char(self, char: str) -> bool:
        """Check if character is in Arabic script ranges"""
        code = ord(char)
        for start, end in self.arabic_ranges:
            if start <= code <= end:
                return True
        return False
    
    def detect_pashto_characters(self, text: str) -> Dict[str, Any]:
        """Detect and count Pashto-specific characters"""
        char_counts = {}
        total_pashto_chars = 0
        
        for char, info in self.pashto_unique_chars.items():
            count = text.count(char)
            if count > 0:
                char_counts[char] = {
                    'count': count,
                    'weight': info['weight'],
                    'name': info['name']
                }
                total_pashto_chars += count
        
        return {
            'pashto_characters': char_counts,
            'total_pashto_chars': total_pashto_chars,
            'pashto_char_ratio': total_pashto_chars / len(text) if text else 0,
            'unique_pashto_chars': len(char_counts),
            'pashto_char_density': total_pashto_chars / len(text) if text else 0
        }
    
    def analyze_character_frequencies(self, text: str) -> Dict[str, Any]:
        """Analyze character frequency distribution"""
        if not text:
            return {'error': 'Empty text provided'}
        
        # Count all Arabic script characters
        char_freq = Counter()
        for char in text:
            if self._is_arabic_char(char):
                char_freq[char] += 1
        
        total_chars = sum(char_freq.values())
        
        if total_chars == 0:
            return {
                'total_arabic_chars': 0,
                'frequencies': {},
                'distribution_stats': {}
            }
        
        # Convert to percentages
        frequencies = {char: count / total_chars for char, count in char_freq.items()}
        
        # Calculate distribution statistics
        values = list(frequencies.values())
        # Get most common characters by sorting
        sorted_frequencies = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)[:5]
        distribution_stats = {
            'unique_chars': len(frequencies),
            'most_common': sorted_frequencies,
            'entropy': self._calculate_entropy(frequencies),
            'uniformity': 1.0 - (max(values) - min(values)) if values else 0
        }
        
        return {
            'total_arabic_chars': total_chars,
            'frequencies': frequencies,
            'distribution_stats': distribution_stats
        }
    
    def _calculate_entropy(self, frequencies: Dict[str, float]) -> float:
        """Calculate Shannon entropy of character distribution"""
        if not frequencies:
            return 0.0
        
        entropy = 0.0
        for prob in frequencies.values():
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        return entropy
    
    def detect_common_words(self, text: str) -> Dict[str, Any]:
        """Detect presence of common Pashto words"""
        if not text:
            return {'error': 'Empty text provided'}
        
        text_lower = text.lower()
        detected_words = {}
        total_weight = 0
        max_weight = sum(self.pashto_common_words.values())
        
        for word, weight in self.pashto_common_words.items():
            if word in text_lower:
                # Count occurrences
                count = text_lower.count(word)
                detected_words[word] = {
                    'count': count,
                    'weight': weight,
                    'total_weight': count * weight
                }
                total_weight += count * weight
        
        confidence_score = total_weight / max_weight if max_weight > 0 else 0
        
        return {
            'detected_words': detected_words,
            'total_detected': len(detected_words),
            'total_weight': total_weight,
            'max_possible_weight': max_weight,
            'confidence_score': min(confidence_score, 1.0),
            'word_diversity': len(detected_words) / len(self.pashto_common_words) if self.pashto_common_words else 0
        }
    
    def pattern_match_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze text against language-specific patterns"""
        if not text:
            return {'error': 'Empty text provided'}
        
        pattern_scores = {}
        
        for language, patterns in self.language_patterns.items():
            language_score = 0
            matched_patterns = []
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Weight different pattern types
                    if language == 'pashto' and any(p in pattern for p in ['ځ', 'څ', 'ډ', 'ړ']):
                        pattern_weight = 2.0  # High weight for Pashto-specific characters
                    else:
                        pattern_weight = 1.0
                    
                    language_score += len(matches) * pattern_weight
                    matched_patterns.append({
                        'pattern': pattern,
                        'matches': len(matches),
                        'weight': pattern_weight
                    })
            
            pattern_scores[language] = {
                'score': language_score,
                'matched_patterns': matched_patterns,
                'pattern_count': len(matched_patterns)
            }
        
        return pattern_scores
    
    def calculate_pashto_probability(self, text: str) -> Dict[str, Any]:
        """Calculate probability that text is Pashto"""
        if not text:
            return {'pashto_probability': 0.0, 'confidence': 'low', 'reasons': ['Empty text']}
        
        reasons = []
        scores = {}
        
        # 1. Pashto character analysis
        pashto_chars = self.detect_pashto_characters(text)
        char_score = 0
        
        if pashto_chars['total_pashto_chars'] > 0:
            # Score based on Pashto-specific characters
            if pashto_chars['unique_pashto_chars'] >= 2:
                char_score = 0.9
                reasons.append(f"Contains {pashto_chars['unique_pashto_chars']} Pashto-specific characters")
            elif pashto_chars['unique_pashto_chars'] == 1:
                char_score = 0.6
                reasons.append(f"Contains Pashto-specific character")
            else:
                char_score = 0.2
                reasons.append("No Pashto-specific characters found")
        
        scores['character_score'] = char_score
        
        # 2. Common word analysis
        word_analysis = self.detect_common_words(text)
        word_score = word_analysis.get('confidence_score', 0.0)
        
        if word_score > 0.5:
            reasons.append(f"Contains {word_analysis['total_detected']} common Pashto words")
        elif word_score > 0.2:
            reasons.append("Contains some Pashto words")
        else:
            reasons.append("Few or no common Pashto words detected")
        
        scores['word_score'] = word_score
        
        # 3. Pattern matching analysis
        pattern_scores = self.pattern_match_analysis(text)
        pattern_score = pattern_scores.get('pashto', {}).get('score', 0)
        
        # Normalize pattern score
        if pattern_score > 0:
            max_possible = sum(len(patterns) * 2 for patterns in self.language_patterns.values())
            pattern_score = min(pattern_score / max_possible, 1.0) if max_possible > 0 else 0
        
        if pattern_score > 0.3:
            reasons.append(f"Matches {pattern_scores.get('pashto', {}).get('pattern_count', 0)} Pashto patterns")
        
        scores['pattern_score'] = pattern_score
        
        # 4. Character frequency analysis
        freq_analysis = self.analyze_character_frequencies(text)
        freq_score = 0
        
        if 'frequencies' in freq_analysis and freq_analysis['frequencies']:
            # Compare to Pashto baseline
            freq_dist = freq_analysis['frequencies']
            similarities = []
            
            for char, baseline_freq in self.baseline_frequencies.get('pashto', {}).items():
                if char in freq_dist:
                    similarity = 1.0 - abs(freq_dist[char] - baseline_freq)
                    similarities.append(similarity)
            
            if similarities:
                freq_score = sum(similarities) / len(similarities)
                if freq_score > 0.7:
                    reasons.append("Character frequency matches Pashto patterns")
        
        scores['frequency_score'] = freq_score
        
        # 5. Script analysis
        script_score = 1.0 if self.is_arabic_script(text) else 0.0
        scores['script_score'] = script_score
        
        if not self.is_arabic_script(text):
            reasons.append("Text is not primarily in Arabic script")
        
        # Calculate overall Pashto probability
        weights = {
            'character_score': 0.3,
            'word_score': 0.3,
            'pattern_score': 0.2,
            'frequency_score': 0.15,
            'script_score': 0.05
        }
        
        overall_probability = sum(scores[key] * weights[key] for key in weights.keys())
        
        # Determine confidence level
        if overall_probability >= 0.8:
            confidence = 'very_high'
        elif overall_probability >= 0.6:
            confidence = 'high'
        elif overall_probability >= 0.4:
            confidence = 'medium'
        elif overall_probability >= 0.2:
            confidence = 'low'
        else:
            confidence = 'very_low'
        
        return {
            'pashto_probability': round(overall_probability, 3),
            'confidence': confidence,
            'scores': scores,
            'reasons': reasons,
            'analysis_details': {
                'pashto_characters': pashto_chars,
                'word_analysis': word_analysis,
                'pattern_scores': pattern_scores,
                'frequency_analysis': freq_analysis
            }
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Main language detection function
        
        Returns:
            Complete language detection result
        """
        if not text or not text.strip():
            return {
                'detected_language': 'unknown',
                'confidence': 0.0,
                'is_arabic_script': False,
                'pashto_probability': 0.0,
                'error': 'Empty or invalid text provided'
            }
        
        # Check if it's Arabic script
        is_arabic = self.is_arabic_script(text)
        
        if not is_arabic:
            return {
                'detected_language': 'non_arabic',
                'confidence': 1.0,
                'is_arabic_script': False,
                'pashto_probability': 0.0,
                'error': 'Text is not in Arabic script'
            }
        
        # Calculate Pashto probability
        pashto_analysis = self.calculate_pashto_probability(text)
        
        # Make detection decision
        pashto_prob = pashto_analysis['pashto_probability']
        
        if pashto_prob >= 0.6:
            detected_language = 'pashto'
            confidence = pashto_analysis['confidence']
        else:
            detected_language = 'other_arabic_script'
            confidence = 'low'
        
        return {
            'detected_language': detected_language,
            'confidence': confidence,
            'is_arabic_script': True,
            'pashto_probability': pashto_prob,
            'pashto_analysis': pashto_analysis,
            'text_length': len(text),
            'arabic_char_count': sum(1 for c in text if self._is_arabic_char(c))
        }
    
    def batch_detect(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Detect language for multiple texts"""
        return [self.detect_language(text) for text in texts]
    
    def validate_detection(self, detection_result: Dict[str, Any], 
                          additional_checks: bool = True) -> Dict[str, Any]:
        """Validate and improve language detection results"""
        if not additional_checks:
            return detection_result
        
        validation_result = detection_result.copy()
        
        # Check for conflicting evidence
        pashto_prob = detection_result.get('pashto_probability', 0)
        pashto_analysis = detection_result.get('pashto_analysis', {})
        
        if pashto_prob > 0.3:
            # Additional validation based on analysis details
            analysis_details = pashto_analysis.get('analysis_details', {})
            
            # Check character consistency
            pashto_chars = analysis_details.get('pashto_characters', {})
            if pashto_chars.get('unique_pashto_chars', 0) >= 2:
                validation_result['pashto_probability'] = min(1.0, pashto_prob + 0.1)
                validation_result['validation_notes'] = validation_result.get('validation_notes', [])
                validation_result['validation_notes'].append("Strong Pashto character evidence")
            
            # Check word consistency
            word_analysis = analysis_details.get('word_analysis', {})
            if word_analysis.get('confidence_score', 0) > 0.3:
                validation_result['pashto_probability'] = min(1.0, pashto_prob + 0.05)
                validation_result['validation_notes'] = validation_result.get('validation_notes', [])
                validation_result['validation_notes'].append("Consistent Pashto word patterns")
        
        return validation_result