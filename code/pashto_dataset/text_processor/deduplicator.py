"""
Text Deduplicator for Pashto Dataset

Advanced deduplication system for Pashto text:
- Exact duplicate detection
- Near-duplicate detection using similarity algorithms
- Pashto-specific similarity measures
- Semantic similarity detection
- Content-based deduplication
"""

import hashlib
import re
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict
import difflib
from difflib import SequenceMatcher

class TextDeduplicator:
    """Advanced text deduplication system for Pashto content"""
    
    def __init__(self):
        # Similarity thresholds
        self.thresholds = {
            'exact_match': 1.0,
            'high_similarity': 0.95,
            'medium_similarity': 0.85,
            'low_similarity': 0.70
        }
        
        # Pashto-specific text normalization for comparison
        self.normalization_patterns = {
            'whitespace': re.compile(r'\s+'),
            'punctuation': re.compile(r'[،؛؟۔!.,;:()[\]{}"\'-]'),
            'diacritics': re.compile(r'[\u064B-\u065F]'),
            'tatweel': re.compile(r'ـ+')
        }
        
        # Content-based similarity features
        self.feature_weights = {
            'word_overlap': 0.4,
            'character_similarity': 0.3,
            'ngram_similarity': 0.2,
            'length_ratio': 0.1
        }
        
        # Hash-based duplicate detection
        self.hash_cache = {}
        self.exact_duplicates = defaultdict(list)
        
    def create_normalized_text(self, text: str) -> str:
        """
        Create normalized version of text for comparison
        
        Args:
            text: Original Pashto text
            
        Returns:
            Normalized text string
        """
        if not text:
            return ""
        
        normalized = text
        
        # Remove diacritics and combining marks
        normalized = self.normalization_patterns['diacritics'].sub('', normalized)
        
        # Remove tatweel (stretching character)
        normalized = self.normalization_patterns['tatweel'].sub('', normalized)
        
        # Normalize whitespace
        normalized = self.normalization_patterns['whitespace'].sub(' ', normalized)
        
        # Remove or normalize punctuation
        normalized = self.normalization_patterns['punctuation'].sub(' ', normalized)
        
        # Strip and convert to lowercase
        normalized = normalized.strip().lower()
        
        return normalized
    
    def create_text_hash(self, text: str) -> str:
        """Create hash for exact duplicate detection"""
        normalized = self.create_normalized_text(text)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def find_exact_duplicates(self, texts: List[str]) -> List[List[int]]:
        """
        Find exact duplicate texts
        
        Args:
            texts: List of texts to check
            
        Returns:
            List of groups, where each group contains indices of duplicate texts
        """
        text_groups = defaultdict(list)
        
        for i, text in enumerate(texts):
            if text and text.strip():
                text_hash = self.create_text_hash(text)
                text_groups[text_hash].append(i)
        
        # Return only groups with duplicates
        return [indices for indices in text_groups.values() if len(indices) > 1]
    
    def calculate_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """
        Calculate comprehensive similarity between two Pashto texts
        
        Returns:
            Dictionary with different similarity measures
        """
        if not text1 or not text2:
            return {'overall_similarity': 0.0}
        
        # Create normalized versions
        norm1 = self.create_normalized_text(text1)
        norm2 = self.create_normalized_text(text2)
        
        if not norm1 or not norm2:
            return {'overall_similarity': 0.0}
        
        # Calculate different similarity measures
        similarity_scores = {}
        
        # 1. Character-level similarity
        similarity_scores['character_similarity'] = self._character_similarity(norm1, norm2)
        
        # 2. Word-level similarity
        similarity_scores['word_similarity'] = self._word_similarity(norm1, norm2)
        
        # 3. N-gram similarity
        similarity_scores['ngram_similarity'] = self._ngram_similarity(norm1, norm2)
        
        # 4. Sequence similarity (using difflib)
        similarity_scores['sequence_similarity'] = SequenceMatcher(None, norm1, norm2).ratio()
        
        # 5. Length-based similarity
        similarity_scores['length_similarity'] = self._length_similarity(text1, text2)
        
        # 6. Pashto-specific content similarity
        similarity_scores['pashto_content_similarity'] = self._pashto_content_similarity(text1, text2)
        
        # Calculate overall similarity
        overall = self._calculate_overall_similarity(similarity_scores)
        similarity_scores['overall_similarity'] = overall
        
        return similarity_scores
    
    def _character_similarity(self, text1: str, text2: str) -> float:
        """Calculate character-level similarity"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _word_similarity(self, text1: str, text2: str) -> float:
        """Calculate word-level similarity"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _ngram_similarity(self, text1: str, text2: str, n: int = 3) -> float:
        """Calculate n-gram similarity"""
        ngrams1 = set(self._get_ngrams(text1, n))
        ngrams2 = set(self._get_ngrams(text2, n))
        
        if not ngrams1 and not ngrams2:
            return 1.0
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        
        return intersection / union if union > 0 else 0.0
    
    def _get_ngrams(self, text: str, n: int) -> List[str]:
        """Extract n-grams from text"""
        return [text[i:i+n] for i in range(len(text) - n + 1)]
    
    def _length_similarity(self, text1: str, text2: str) -> float:
        """Calculate length-based similarity"""
        len1, len2 = len(text1), len(text2)
        
        if len1 == 0 and len2 == 0:
            return 1.0
        
        if len1 == 0 or len2 == 0:
            return 0.0
        
        min_len, max_len = min(len1, len2), max(len1, len2)
        return min_len / max_len
    
    def _pashto_content_similarity(self, text1: str, text2: str) -> float:
        """Calculate Pashto-specific content similarity"""
        # Extract Pashto-specific features
        features1 = self._extract_pashto_features(text1)
        features2 = self._extract_pashto_features(text2)
        
        similarity_scores = []
        
        # Compare common Pashto words
        common_words1 = set(features1['common_words'])
        common_words2 = set(features2['common_words'])
        
        if common_words1 and common_words2:
            word_intersection = len(common_words1.intersection(common_words2))
            word_union = len(common_words1.union(common_words2))
            word_similarity = word_intersection / word_union if word_union > 0 else 0.0
            similarity_scores.append(word_similarity)
        
        # Compare script characteristics
        script1 = features1['script_ratio']
        script2 = features2['script_ratio']
        script_similarity = 1.0 - abs(script1 - script2)
        similarity_scores.append(script_similarity)
        
        # Compare character patterns
        char1 = features1['pashto_chars']
        char2 = features2['pashto_chars']
        char_similarity = len(char1.intersection(char2)) / max(len(char1), len(char2), 1)
        similarity_scores.append(char_similarity)
        
        return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
    
    def _extract_pashto_features(self, text: str) -> Dict[str, Any]:
        """Extract Pashto-specific features from text"""
        # Common Pashto words to look for
        common_pashto_words = [
            'زه', 'تاسو', 'دوی', 'موږ', 'هغه', 'دا', 'دده', 'تر', 'پر', 'سره',
            'څخه', 'ته', 'ځان', 'کور', 'ژوند', 'ورځ', 'شپه', 'ښه', 'بد', 'لري'
        ]
        
        # Pashto-specific characters
        pashto_chars = set('ځڅډړګڼ')
        
        text_lower = text.lower()
        
        # Find common words
        found_words = [word for word in common_pashto_words if word in text_lower]
        
        # Calculate script ratio
        arabic_count = sum(1 for char in text if self._is_arabic_script(char))
        script_ratio = arabic_count / len(text) if text else 0
        
        # Find Pashto-specific characters
        found_pashto_chars = [char for char in pashto_chars if char in text]
        
        return {
            'common_words': found_words,
            'script_ratio': script_ratio,
            'pashto_chars': set(found_pashto_chars)
        }
    
    def _is_arabic_script(self, char: str) -> bool:
        """Check if character is Arabic script"""
        code = ord(char)
        return (
            (0x0600 <= code <= 0x06FF) or
            (0x0750 <= code <= 0x077F) or
            (0x08A0 <= code <= 0x08FF)
        )
    
    def _calculate_overall_similarity(self, similarity_scores: Dict[str, float]) -> float:
        """Calculate weighted overall similarity score"""
        if not similarity_scores:
            return 0.0
        
        # Default weights
        weights = {
            'character_similarity': 0.25,
            'word_similarity': 0.25,
            'ngram_similarity': 0.20,
            'sequence_similarity': 0.15,
            'length_similarity': 0.10,
            'pashto_content_similarity': 0.05
        }
        
        overall = 0.0
        total_weight = 0.0
        
        for measure, score in similarity_scores.items():
            weight = weights.get(measure, 0.0)
            overall += score * weight
            total_weight += weight
        
        return overall / total_weight if total_weight > 0 else 0.0
    
    def find_near_duplicates(self, texts: List[str], threshold: float = None) -> List[List[int]]:
        """
        Find near-duplicate texts using similarity analysis
        
        Args:
            texts: List of texts to check
            threshold: Similarity threshold for near-duplicate detection
            
        Returns:
            List of groups of similar texts
        """
        if threshold is None:
            threshold = self.thresholds['medium_similarity']
        
        if len(texts) <= 1:
            return []
        
        similar_groups = []
        processed = set()
        
        for i in range(len(texts)):
            if i in processed:
                continue
                
            current_group = [i]
            
            for j in range(i + 1, len(texts)):
                if j in processed:
                    continue
                
                similarity = self.calculate_similarity(texts[i], texts[j])
                
                if similarity['overall_similarity'] >= threshold:
                    current_group.append(j)
                    processed.add(j)
            
            if len(current_group) > 1:
                similar_groups.append(current_group)
                processed.update(current_group)
        
        return similar_groups
    
    def deduplicate_texts(self, texts: List[str], 
                         remove_exact: bool = True,
                         remove_near_duplicates: bool = True,
                         near_duplicate_threshold: float = None) -> Dict[str, Any]:
        """
        Comprehensive deduplication of text collection
        
        Args:
            texts: List of texts to deduplicate
            remove_exact: Whether to remove exact duplicates
            remove_near_duplicates: Whether to remove near duplicates
            near_duplicate_threshold: Threshold for near duplicate detection
            
        Returns:
            Dictionary with deduplication results
        """
        if not texts:
            return {
                'original_count': 0,
                'final_count': 0,
                'removed_exact_duplicates': 0,
                'removed_near_duplicates': 0,
                'kept_texts': [],
                'duplicate_groups': []
            }
        
        # Track original indices
        original_texts = texts.copy()
        kept_indices = set(range(len(texts)))
        duplicate_groups = []
        
        # Remove exact duplicates
        if remove_exact:
            exact_duplicate_groups = self.find_exact_duplicates(texts)
            
            for group in exact_duplicate_groups:
                # Keep only the first occurrence
                for index in group[1:]:
                    kept_indices.discard(index)
                duplicate_groups.append(('exact', group))
        
        # Remove near duplicates
        if remove_near_duplicates and len(kept_indices) > 1:
            remaining_texts = [texts[i] for i in sorted(kept_indices)]
            near_duplicate_groups = self.find_near_duplicates(
                remaining_texts, 
                near_duplicate_threshold
            )
            
            # Adjust indices to original positions
            index_mapping = {i: original_idx for i, original_idx in enumerate(sorted(kept_indices))}
            
            for group in near_duplicate_groups:
                adjusted_group = [index_mapping[i] for i in group]
                # Keep only the first occurrence
                for index in adjusted_group[1:]:
                    kept_indices.discard(index)
                duplicate_groups.append(('near_duplicate', adjusted_group))
        
        # Prepare final results
        kept_texts = [texts[i] for i in sorted(kept_indices)]
        
        return {
            'original_count': len(texts),
            'final_count': len(kept_texts),
            'removed_exact_duplicates': len(texts) - len(kept_texts) - 
                                     sum(1 for group_type, _ in duplicate_groups if group_type == 'near_duplicate'),
            'removed_near_duplicates': sum(1 for group_type, _ in duplicate_groups if group_type == 'near_duplicate'),
            'kept_texts': kept_texts,
            'kept_indices': sorted(kept_indices),
            'duplicate_groups': duplicate_groups
        }
    
    def analyze_duplicate_patterns(self, duplicate_groups: List[Tuple[str, List[int]]], 
                                  texts: List[str]) -> Dict[str, Any]:
        """
        Analyze patterns in duplicate content
        
        Args:
            duplicate_groups: List of (type, indices) tuples
            texts: Original text list
            
        Returns:
            Analysis of duplicate patterns
        """
        if not duplicate_groups:
            return {'message': 'No duplicates found for analysis'}
        
        analysis = {
            'total_groups': len(duplicate_groups),
            'group_types': defaultdict(int),
            'group_sizes': [],
            'similarity_statistics': [],
            'length_statistics': [],
            'content_analysis': {}
        }
        
        for group_type, indices in duplicate_groups:
            analysis['group_types'][group_type] += 1
            group_size = len(indices)
            analysis['group_sizes'].append(group_size)
            
            # Analyze group content
            if group_size >= 2:
                texts_in_group = [texts[i] for i in indices if i < len(texts)]
                if len(texts_in_group) >= 2:
                    # Calculate similarity within group
                    similarities = []
                    for i in range(len(texts_in_group)):
                        for j in range(i + 1, len(texts_in_group)):
                            sim = self.calculate_similarity(texts_in_group[i], texts_in_group[j])
                            similarities.append(sim['overall_similarity'])
                    
                    if similarities:
                        analysis['similarity_statistics'].append({
                            'group_size': group_size,
                            'avg_similarity': sum(similarities) / len(similarities),
                            'min_similarity': min(similarities),
                            'max_similarity': max(similarities)
                        })
                    
                    # Analyze length patterns
                    lengths = [len(text) for text in texts_in_group]
                    analysis['length_statistics'].append({
                        'group_size': group_size,
                        'avg_length': sum(lengths) / len(lengths),
                        'min_length': min(lengths),
                        'max_length': max(lengths)
                    })
        
        return analysis
    
    def get_similarity_report(self, texts: List[str], top_pairs: int = 10) -> Dict[str, Any]:
        """
        Generate similarity report for all text pairs
        
        Args:
            texts: List of texts to analyze
            top_pairs: Number of most similar pairs to include
            
        Returns:
            Comprehensive similarity report
        """
        if len(texts) < 2:
            return {'message': 'Need at least 2 texts for similarity analysis'}
        
        similarities = []
        
        # Calculate all pairwise similarities
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                similarity_scores = self.calculate_similarity(texts[i], texts[j])
                similarities.append({
                    'text1_index': i,
                    'text2_index': j,
                    'text1_length': len(texts[i]),
                    'text2_length': len(texts[j]),
                    'similarity': similarity_scores['overall_similarity'],
                    'detailed_scores': similarity_scores
                })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'total_pairs': len(similarities),
            'highest_similarity': similarities[0]['similarity'] if similarities else 0,
            'lowest_similarity': similarities[-1]['similarity'] if similarities else 0,
            'average_similarity': sum(s['similarity'] for s in similarities) / len(similarities) if similarities else 0,
            'top_similar_pairs': similarities[:top_pairs],
            'duplicates_above_threshold': len([s for s in similarities if s['similarity'] >= self.thresholds['medium_similarity']])
        }