"""
Quality Metrics
==============

Calculates comprehensive quality metrics for datasets.
"""

import logging
import math
from typing import Dict, List, Any, Optional, Union
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from datasets import Dataset
import warnings
import re

from .config import DatasetConfig


class QualityMetrics:
    """Calculates comprehensive quality metrics for datasets."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.logger = logging.getLogger(f"QualityMetrics[{config.dataset_name}]")
    
    def calculate_all_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """
        Calculate all quality metrics for a dataset.
        
        Args:
            dataset: Dataset to analyze
            
        Returns:
            Dictionary containing all quality metrics
        """
        self.logger.info("Calculating comprehensive quality metrics")
        
        metrics = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "dataset_size": len(dataset),
            "features": list(dataset.column_names)
        }
        
        # Basic metrics
        metrics.update(self._calculate_basic_metrics(dataset))
        
        # Data quality metrics
        metrics.update(self._calculate_data_quality_metrics(dataset))
        
        # Diversity metrics
        metrics.update(self._calculate_diversity_metrics(dataset))
        
        # Balance metrics
        metrics.update(self._calculate_balance_metrics(dataset))
        
        # Statistical metrics
        metrics.update(self._calculate_statistical_metrics(dataset))
        
        # Content quality metrics
        metrics.update(self._calculate_content_quality_metrics(dataset))
        
        # Completeness metrics
        metrics.update(self._calculate_completeness_metrics(dataset))
        
        # Language-specific metrics
        metrics.update(self._calculate_language_specific_metrics(dataset))
        
        self.logger.info("Quality metrics calculation completed")
        return metrics
    
    def _calculate_basic_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate basic dataset metrics."""
        metrics = {}
        
        # Size metrics
        metrics["num_samples"] = len(dataset)
        metrics["num_features"] = len(dataset.column_names)
        metrics["memory_usage_mb"] = dataset.nbytes / (1024 * 1024)
        metrics["storage_size_mb"] = dataset.dataset_size / (1024 * 1024)
        metrics["compression_ratio"] = metrics["memory_usage_mb"] / metrics["storage_size_mb"] if metrics["storage_size_mb"] > 0 else 0
        
        # Feature metrics
        feature_types = {}
        for column in dataset.column_names:
            feature_type = dataset.features[column].dtype if hasattr(dataset.features[column], 'dtype') else str(type(dataset.features[column]))
            feature_types[column] = feature_type
        
        metrics["feature_types"] = feature_types
        
        # Categorical features
        categorical_features = [col for col in dataset.column_names 
                              if hasattr(dataset.features.get(col), 'names')]
        metrics["num_categorical_features"] = len(categorical_features)
        metrics["categorical_features"] = categorical_features
        
        # Text features
        text_features = [col for col in dataset.column_names if any(
            keyword in col.lower() for keyword in ['text', 'content', 'description', 'title', 'body']
        )]
        metrics["num_text_features"] = len(text_features)
        metrics["text_features"] = text_features
        
        return metrics
    
    def _calculate_data_quality_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate data quality related metrics."""
        metrics = {}
        
        # Sample data for analysis (for performance)
        sample_size = min(10000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Completeness metrics
        completeness_scores = []
        for column in sample.column_names:
            non_null_count = sum(1 for item in sample[column] if item is not None and str(item).strip() != "")
            completeness = non_null_count / len(sample) if len(sample) > 0 else 0
            completeness_scores.append(completeness)
        
        metrics["overall_completeness"] = np.mean(completeness_scores) if completeness_scores else 0
        metrics["min_completeness"] = min(completeness_scores) if completeness_scores else 0
        metrics["max_completeness"] = max(completeness_scores) if completeness_scores else 0
        
        # Uniqueness metrics
        uniqueness_scores = []
        for column in sample.column_names:
            unique_values = set(str(item) for item in sample[column] if item is not None)
            uniqueness = len(unique_values) / len(sample) if len(sample) > 0 else 0
            uniqueness_scores.append(uniqueness)
        
        metrics["overall_uniqueness"] = np.mean(uniqueness_scores) if uniqueness_scores else 0
        metrics["min_uniqueness"] = min(uniqueness_scores) if uniqueness_scores else 0
        metrics["max_uniqueness"] = max(uniqueness_scores) if uniqueness_scores else 0
        
        # Duplicate row detection
        df = sample.to_pandas()
        duplicates = df.duplicated()
        metrics["duplicate_row_ratio"] = duplicates.sum() / len(df) if len(df) > 0 else 0
        metrics["unique_row_ratio"] = 1 - metrics["duplicate_row_ratio"]
        
        return metrics
    
    def _calculate_diversity_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate diversity metrics."""
        metrics = {}
        
        # Sample for performance
        sample_size = min(10000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Lexical diversity for text columns
        text_columns = [col for col in sample.column_names if any(
            keyword in col.lower() for keyword in ['text', 'content', 'description', 'title', 'body']
        )]
        
        lexical_diversity_scores = {}
        for column in text_columns:
            texts = [str(item) for item in sample[column] if item is not None and str(item).strip()]
            if texts:
                # Calculate Type-Token Ratio (TTR)
                all_words = []
                for text in texts:
                    words = re.findall(r'\b\w+\b', text.lower())
                    all_words.extend(words)
                
                if all_words:
                    unique_words = set(all_words)
                    ttr = len(unique_words) / len(all_words)
                    lexical_diversity_scores[column] = ttr
        
        metrics["lexical_diversity"] = lexical_diversity_scores
        metrics["avg_lexical_diversity"] = np.mean(list(lexical_diversity_scores.values())) if lexical_diversity_scores else 0
        
        # Semantic diversity using character n-grams
        semantic_diversity_scores = {}
        for column in text_columns:
            texts = [str(item) for item in sample[column] if item is not None and str(item).strip()]
            if texts:
                # Character n-gram diversity
                ngrams = []
                for text in texts:
                    for i in range(len(text) - 2):
                        ngrams.append(text[i:i+3])
                
                if ngrams:
                    unique_ngrams = set(ngrams)
                    semantic_diversity = len(unique_ngrams) / len(ngrams)
                    semantic_diversity_scores[column] = semantic_diversity
        
        metrics["semantic_diversity"] = semantic_diversity_scores
        metrics["avg_semantic_diversity"] = np.mean(list(semantic_diversity_scores.values())) if semantic_diversity_scores else 0
        
        # Feature diversity
        categorical_columns = [col for col in sample.column_names if hasattr(sample.features.get(col), 'names')]
        
        feature_diversity_scores = {}
        for column in categorical_columns:
            values = [str(item) for item in sample[column] if item is not None]
            if values:
                unique_values = set(values)
                diversity = len(unique_values) / len(values)
                feature_diversity_scores[column] = diversity
        
        metrics["feature_diversity"] = feature_diversity_scores
        metrics["avg_feature_diversity"] = np.mean(list(feature_diversity_scores.values())) if feature_diversity_scores else 0
        
        return metrics
    
    def _calculate_balance_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate balance metrics for categorical features."""
        metrics = {}
        
        # Sample for performance
        sample_size = min(10000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Categorical feature balance
        categorical_columns = [col for col in sample.column_names if hasattr(sample.features.get(col), 'names')]
        
        balance_metrics = {}
        for column in categorical_columns:
            values = [str(item) for item in sample[column] if item is not None]
            if values:
                counter = Counter(values)
                counts = list(counter.values())
                
                # Calculate balance metrics
                mean_count = np.mean(counts)
                std_count = np.std(counts)
                cv = std_count / mean_count if mean_count > 0 else 0  # Coefficient of variation
                
                # Gini coefficient for perfect equality
                sorted_counts = sorted(counts)
                n = len(sorted_counts)
                index = np.arange(1, n + 1)
                gini = (2 * np.sum(index * sorted_counts)) / (n * np.sum(sorted_counts)) - (n + 1) / n
                
                balance_metrics[column] = {
                    "num_classes": len(counter),
                    "mean_count": mean_count,
                    "std_count": std_count,
                    "coefficient_of_variation": cv,
                    "gini_coefficient": gini,
                    "min_count": min(counts),
                    "max_count": max(counts),
                    "imbalance_ratio": max(counts) / min(counts) if min(counts) > 0 else 0
                }
        
        metrics["categorical_balance"] = balance_metrics
        
        # Overall balance score
        if balance_metrics:
            avg_cv = np.mean([bm["coefficient_of_variation"] for bm in balance_metrics.values()])
            avg_gini = np.mean([bm["gini_coefficient"] for bm in balance_metrics.values()])
            
            # Convert to balance score (0 = perfectly imbalanced, 1 = perfectly balanced)
            balance_score = 1 / (1 + avg_cv)
            
            metrics.update({
                "avg_coefficient_of_variation": avg_cv,
                "avg_gini_coefficient": avg_gini,
                "overall_balance_score": balance_score
            })
        
        return metrics
    
    def _calculate_statistical_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate statistical metrics."""
        metrics = {}
        
        # Sample for performance
        sample_size = min(10000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Numeric features statistics
        numeric_columns = [col for col in sample.column_names if isinstance(sample[0][col], (int, float)) if sample[0][col] is not None]
        
        numeric_stats = {}
        for column in numeric_columns:
            values = [item for item in sample[column] if item is not None and isinstance(item, (int, float))]
            if values:
                numeric_stats[column] = {
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "q25": np.percentile(values, 25),
                    "q75": np.percentile(values, 75),
                    "skewness": self._calculate_skewness(values),
                    "kurtosis": self._calculate_kurtosis(values)
                }
        
        metrics["numeric_statistics"] = numeric_stats
        
        # Text length statistics
        text_columns = [col for col in sample.column_names if any(
            keyword in col.lower() for keyword in ['text', 'content', 'description', 'title', 'body']
        )]
        
        text_length_stats = {}
        for column in text_columns:
            texts = [str(item) for item in sample[column] if item is not None and str(item).strip()]
            if texts:
                lengths = [len(text) for text in texts]
                text_length_stats[column] = {
                    "mean_length": np.mean(lengths),
                    "median_length": np.median(lengths),
                    "std_length": np.std(lengths),
                    "min_length": min(lengths),
                    "max_length": max(lengths),
                    "total_characters": sum(lengths),
                    "total_words": sum(len(text.split()) for text in texts)
                }
        
        metrics["text_length_statistics"] = text_length_stats
        
        return metrics
    
    def _calculate_skewness(self, values: List[float]) -> float:
        """Calculate skewness of a list of values."""
        if len(values) < 2:
            return 0
        
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return 0
        
        n = len(values)
        skewness = np.sum(((values - mean) / std) ** 3) / n
        return skewness
    
    def _calculate_kurtosis(self, values: List[float]) -> float:
        """Calculate kurtosis of a list of values."""
        if len(values) < 2:
            return 0
        
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return 0
        
        n = len(values)
        kurtosis = np.sum(((values - mean) / std) ** 4) / n - 3
        return kurtosis
    
    def _calculate_content_quality_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate content quality metrics."""
        metrics = {}
        
        # Sample for performance
        sample_size = min(5000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Text quality metrics
        text_columns = [col for col in sample.column_names if any(
            keyword in col.lower() for keyword in ['text', 'content', 'description', 'title', 'body']
        )]
        
        text_quality_metrics = {}
        for column in text_columns:
            texts = [str(item) for item in sample[column] if item is not None and str(item).strip()]
            if texts:
                # Language consistency
                language_scores = self._assess_language_quality(texts)
                
                # Readability metrics
                readability_scores = self._assess_readability(texts)
                
                # Content richness
                richness_scores = self._assess_content_richness(texts)
                
                text_quality_metrics[column] = {
                    "language_consistency": language_scores,
                    "readability": readability_scores,
                    "content_richness": richness_scores
                }
        
        metrics["text_quality"] = text_quality_metrics
        
        # Overall content quality score
        if text_quality_metrics:
            overall_scores = []
            for col_metrics in text_quality_metrics.values():
                col_score = (col_metrics["language_consistency"]["consistency_score"] + 
                           col_metrics["readability"]["avg_readability_score"] + 
                           col_metrics["content_richness"]["avg_richness_score"]) / 3
                overall_scores.append(col_score)
            
            metrics["overall_content_quality"] = np.mean(overall_scores)
        
        return metrics
    
    def _assess_language_quality(self, texts: List[str]) -> Dict[str, Any]:
        """Assess language quality of texts."""
        # Pashto character patterns
        pashto_chars = 'ءآأإؤئپچځڅڈړښڛڝڞڟڠڢڣڤڥڦڧڨکڪګڬڭڮیۍێېۑ'
        
        pashto_ratios = []
        for text in texts:
            if text:
                pashto_count = sum(1 for char in text if char in pashto_chars)
                total_chars = len(text)
                ratio = pashto_count / total_chars if total_chars > 0 else 0
                pashto_ratios.append(ratio)
        
        consistency_score = 1 - np.std(pashto_ratios) if pashto_ratios else 0
        
        return {
            "avg_pashto_ratio": np.mean(pashto_ratios) if pashto_ratios else 0,
            "pashto_ratio_std": np.std(pashto_ratios) if pashto_ratios else 0,
            "consistency_score": consistency_score
        }
    
    def _assess_readability(self, texts: List[str]) -> Dict[str, Any]:
        """Assess readability of texts."""
        # Simple readability metrics
        readability_scores = []
        
        for text in texts:
            if text:
                words = text.split()
                sentences = text.split('.')
                
                # Average words per sentence
                avg_words_per_sentence = len(words) / len([s for s in sentences if s.strip()]) if len(sentences) > 0 else len(words)
                
                # Average word length
                avg_word_length = np.mean([len(word) for word in words]) if words else 0
                
                # Simple readability score (higher is more readable)
                readability = 1 / (1 + avg_words_per_sentence * avg_word_length / 10)
                readability_scores.append(readability)
        
        return {
            "avg_readability_score": np.mean(readability_scores) if readability_scores else 0,
            "readability_std": np.std(readability_scores) if readability_scores else 0
        }
    
    def _assess_content_richness(self, texts: List[str]) -> Dict[str, Any]:
        """Assess richness of text content."""
        richness_scores = []
        
        for text in texts:
            if text:
                words = text.split()
                
                # Unique word ratio
                unique_words = set(word.lower() for word in words)
                unique_ratio = len(unique_words) / len(words) if words else 0
                
                # Vocabulary diversity (character n-grams)
                char_ngrams = set()
                for i in range(len(text) - 2):
                    ngram = text[i:i+3]
                    char_ngrams.add(ngram)
                
                ngram_diversity = len(char_ngrams) / max(1, len(text) - 2)
                
                # Richness score combines unique words and character diversity
                richness = (unique_ratio + ngram_diversity) / 2
                richness_scores.append(richness)
        
        return {
            "avg_richness_score": np.mean(richness_scores) if richness_scores else 0,
            "richness_std": np.std(richness_scores) if richness_scores else 0
        }
    
    def _calculate_completeness_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate completeness metrics."""
        metrics = {}
        
        # Sample for performance
        sample_size = min(10000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Per-column completeness
        column_completeness = {}
        for column in sample.column_names:
            non_null_count = sum(1 for item in sample[column] if item is not None and str(item).strip() != "")
            completeness = non_null_count / len(sample) if len(sample) > 0 else 0
            column_completeness[column] = completeness
        
        metrics["column_completeness"] = column_completeness
        
        # Overall completeness
        total_non_null = sum(column_completeness.values())
        total_cells = len(sample.column_names)
        overall_completeness = total_non_null / total_cells if total_cells > 0 else 0
        
        metrics["overall_completeness"] = overall_completeness
        
        # Completeness variance (how much completeness varies across columns)
        completeness_values = list(column_completeness.values())
        metrics["completeness_variance"] = np.var(completeness_values) if completeness_values else 0
        metrics["completeness_std"] = np.std(completeness_values) if completeness_values else 0
        
        return metrics
    
    def _calculate_language_specific_metrics(self, dataset: Dataset) -> Dict[str, Any]:
        """Calculate Pashto-specific language metrics."""
        metrics = {}
        
        # Check if this is a Pashto dataset
        if self.config.language != "pas":
            return metrics
        
        # Sample for performance
        sample_size = min(5000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Text columns
        text_columns = [col for col in sample.column_names if any(
            keyword in col.lower() for keyword in ['text', 'content', 'description', 'title', 'body']
        )]
        
        pashto_metrics = {}
        for column in text_columns:
            texts = [str(item) for item in sample[column] if item is not None and str(item).strip()]
            if texts:
                pashto_character_usage = self._analyze_pashto_characters(texts)
                script_consistency = self._analyze_script_consistency(texts)
                dialect_markers = self._detect_dialect_markers(texts)
                
                pashto_metrics[column] = {
                    "pashto_character_usage": pashto_character_usage,
                    "script_consistency": script_consistency,
                    "dialect_markers": dialect_markers
                }
        
        metrics["pashto_specific"] = pashto_metrics
        
        # Overall Pashto quality score
        if pashto_metrics:
            quality_scores = []
            for col_metrics in pashto_metrics.values():
                score = (col_metrics["pashto_character_usage"]["score"] + 
                        col_metrics["script_consistency"]["consistency_score"]) / 2
                quality_scores.append(score)
            
            metrics["overall_pashto_quality"] = np.mean(quality_scores)
        
        return metrics
    
    def _analyze_pashto_characters(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze usage of Pashto-specific characters."""
        # Common Pashto characters
        pashto_chars = 'ءآأإؤئپچځڅڈړښڛڝڞڟڠڢڣڤڥڦڧڨکڪګڬڭڮیۍێېۑ'
        
        char_usage = {}
        for char in pashto_chars:
            count = 0
            for text in texts:
                count += text.count(char)
            char_usage[char] = count
        
        # Calculate score based on character usage distribution
        total_chars = sum(char_usage.values())
        usage_values = [count for count in char_usage.values() if count > 0]
        
        score = len(usage_values) / len(pashto_chars) if len(pashto_chars) > 0 else 0
        
        return {
            "character_usage": char_usage,
            "total_pashto_chars": total_chars,
            "unique_char_count": len(usage_values),
            "score": score
        }
    
    def _analyze_script_consistency(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze script consistency in texts."""
        # Count different scripts
        arabic_chars = 0
        latin_chars = 0
        other_chars = 0
        
        for text in texts:
            for char in text:
                if 'آأإؤئء'.find(char) >= 0 or (ord(char) >= 0x0600 and ord(char) <= 0x06FF):
                    arabic_chars += 1
                elif char.isalpha() and ord(char) < 128:
                    latin_chars += 1
                else:
                    other_chars += 1
        
        total_chars = arabic_chars + latin_chars + other_chars
        
        if total_chars == 0:
            return {"consistency_score": 0}
        
        arabic_ratio = arabic_chars / total_chars
        
        # Score based on Arabic script dominance
        consistency_score = arabic_ratio if arabic_ratio > 0.5 else 0.5 - abs(arabic_ratio - 0.5)
        
        return {
            "arabic_ratio": arabic_ratio,
            "latin_ratio": latin_chars / total_chars,
            "other_ratio": other_chars / total_chars,
            "consistency_score": consistency_score
        }
    
    def _detect_dialect_markers(self, texts: List[str]) -> Dict[str, Any]:
        """Detect dialect markers in Pashto texts."""
        # Common Pashto dialect indicators
        southern_markers = ['زه', 'ته', 'موږ', 'دغه', 'دغه']
        northern_markers = ['زې', 'ته', 'موږ', 'دا', 'دا']
        
        southern_count = 0
        northern_count = 0
        
        for text in texts:
            for marker in southern_markers:
                if marker in text:
                    southern_count += 1
            for marker in northern_markers:
                if marker in text:
                    northern_count += 1
        
        total_samples = len(texts)
        southern_ratio = southern_count / total_samples if total_samples > 0 else 0
        northern_ratio = northern_count / total_samples if total_samples > 0 else 0
        
        return {
            "southern_marker_count": southern_count,
            "northern_marker_count": northern_count,
            "southern_ratio": southern_ratio,
            "northern_ratio": northern_ratio,
            "dialect_diversity": abs(southern_ratio - northern_ratio)
        }
    
    def generate_quality_report(self, metrics: Dict[str, Any]) -> str:
        """Generate a human-readable quality report."""
        report_lines = []
        
        # Header
        report_lines.append("Dataset Quality Report")
        report_lines.append("=" * 50)
        report_lines.append("")
        
        # Basic information
        report_lines.append("Basic Information:")
        report_lines.append(f"  - Samples: {metrics.get('num_samples', 'N/A'):,}")
        report_lines.append(f"  - Features: {metrics.get('num_features', 'N/A')}")
        report_lines.append(f"  - Memory Usage: {metrics.get('memory_usage_mb', 0):.1f} MB")
        report_lines.append("")
        
        # Quality scores
        if 'overall_completeness' in metrics:
            completeness_pct = metrics['overall_completeness'] * 100
            report_lines.append(f"Overall Completeness: {completeness_pct:.1f}%")
        
        if 'overall_uniqueness' in metrics:
            uniqueness_pct = metrics['overall_uniqueness'] * 100
            report_lines.append(f"Overall Uniqueness: {uniqueness_pct:.1f}%")
        
        if 'overall_balance_score' in metrics:
            balance_pct = metrics['overall_balance_score'] * 100
            report_lines.append(f"Overall Balance: {balance_pct:.1f}%")
        
        if 'overall_content_quality' in metrics:
            content_pct = metrics['overall_content_quality'] * 100
            report_lines.append(f"Content Quality: {content_pct:.1f}%")
        
        report_lines.append("")
        
        # Overall assessment
        quality_scores = [
            metrics.get('overall_completeness', 0),
            metrics.get('overall_uniqueness', 0),
            metrics.get('overall_balance_score', 0),
            metrics.get('overall_content_quality', 0)
        ]
        
        avg_quality = np.mean([score for score in quality_scores if score > 0])
        
        if avg_quality > 0.8:
            assessment = "Excellent"
        elif avg_quality > 0.6:
            assessment = "Good"
        elif avg_quality > 0.4:
            assessment = "Fair"
        else:
            assessment = "Poor"
        
        report_lines.append(f"Overall Quality Assessment: {assessment}")
        report_lines.append("")
        
        return "\n".join(report_lines)