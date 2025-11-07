"""
Dataset Validator
================

Performs comprehensive validation checks on datasets.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from collections import Counter
import numpy as np
import pandas as pd
from datasets import Dataset, DatasetDict
import warnings

from .config import DatasetConfig


class DatasetValidator:
    """Validates datasets for quality, consistency, and integrity."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.logger = logging.getLogger(f"DatasetValidator[{config.dataset_name}]")
    
    def validate_dataset(self, dataset: Dataset) -> Dict[str, Any]:
        """
        Perform comprehensive validation on a dataset.
        
        Args:
            dataset: Dataset to validate
            
        Returns:
            Validation results dictionary
        """
        self.logger.info("Starting comprehensive dataset validation")
        
        results = {
            "overall_status": "PASS",
            "errors": [],
            "warnings": [],
            "metrics": {},
            "checks": {}
        }
        
        # Basic structure validation
        structure_results = self._validate_structure(dataset)
        results["checks"]["structure"] = structure_results
        results["errors"].extend(structure_results.get("errors", []))
        results["warnings"].extend(structure_results.get("warnings", []))
        
        # Data quality validation
        quality_results = self._validate_data_quality(dataset)
        results["checks"]["data_quality"] = quality_results
        results["errors"].extend(quality_results.get("errors", []))
        results["warnings"].extend(quality_results.get("warnings", []))
        
        # Content validation
        content_results = self._validate_content(dataset)
        results["checks"]["content"] = content_results
        results["errors"].extend(content_results.get("errors", []))
        results["warnings"].extend(content_results.get("warnings", []))
        
        # Statistical validation
        statistical_results = self._validate_statistics(dataset)
        results["checks"]["statistics"] = statistical_results
        results["errors"].extend(statistical_results.get("errors", []))
        results["warnings"].extend(statistical_results.get("warnings", []))
        
        # Memory usage validation
        memory_results = self._validate_memory_usage(dataset)
        results["checks"]["memory"] = memory_results
        results["errors"].extend(memory_results.get("errors", []))
        results["warnings"].extend(memory_results.get("warnings", []))
        
        # Calculate overall status
        if results["errors"]:
            results["overall_status"] = "FAIL"
        elif results["warnings"]:
            results["overall_status"] = "PASS_WITH_WARNINGS"
        
        # Calculate metrics
        results["metrics"] = self._calculate_validation_metrics(results)
        
        self.logger.info(f"Validation completed with status: {results['overall_status']}")
        return results
    
    def _validate_structure(self, dataset: Dataset) -> Dict[str, Any]:
        """Validate dataset structure."""
        results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # Check if dataset is empty
        if len(dataset) == 0:
            results["errors"].append("Dataset is empty")
            results["status"] = "FAIL"
            return results
        
        # Check minimum size
        if len(dataset) < self.config.min_samples:
            results["warnings"].append(
                f"Dataset has {len(dataset)} samples, less than minimum of {self.config.min_samples}"
            )
        
        # Check column consistency
        if not dataset.column_names:
            results["errors"].append("Dataset has no columns")
            results["status"] = "FAIL"
        else:
            results["warnings"].append(f"Dataset has {len(dataset.column_names)} columns")
        
        # Check for duplicate column names
        column_names = dataset.column_names
        if len(column_names) != len(set(column_names)):
            results["errors"].append("Dataset has duplicate column names")
            results["status"] = "FAIL"
        
        # Validate features
        if not dataset.features:
            results["warnings"].append("Dataset has no feature definitions")
        else:
            feature_validation = self._validate_features(dataset.features)
            if not feature_validation["valid"]:
                results["errors"].extend(feature_validation["errors"])
                results["status"] = "FAIL"
        
        return results
    
    def _validate_features(self, features) -> Dict[str, Any]:
        """Validate dataset features."""
        validation = {"valid": True, "errors": []}
        
        try:
            features_dict = features.to_dict()
            
            # Check for empty feature definitions
            if not features_dict:
                validation["errors"].append("Features definition is empty")
                validation["valid"] = False
            
            # Validate each feature
            for feature_name, feature_info in features_dict.items():
                if not isinstance(feature_info, dict):
                    validation["errors"].append(f"Invalid feature definition for '{feature_name}'")
                    validation["valid"] = False
                
        except Exception as e:
            validation["errors"].append(f"Error parsing features: {str(e)}")
            validation["valid"] = False
        
        return validation
    
    def _validate_data_quality(self, dataset: Dataset) -> Dict[str, Any]:
        """Validate data quality aspects."""
        results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        for column in dataset.column_names:
            column_results = self._validate_column_quality(dataset, column)
            results["errors"].extend(column_results.get("errors", []))
            results["warnings"].extend(column_results.get("warnings", []))
        
        # Check overall completeness
        completeness = self._calculate_completeness(dataset)
        if completeness < self.config.min_completeness:
            results["errors"].append(
                f"Dataset completeness {completeness:.2%} below minimum {self.config.min_completeness:.2%}"
            )
            results["status"] = "FAIL"
        
        # Check for duplicate rows
        duplicates = self._check_duplicate_rows(dataset)
        if duplicates["ratio"] > 0.1:  # More than 10% duplicates
            results["warnings"].append(
                f"High duplicate rate: {duplicates['ratio']:.2%} ({duplicates['count']} rows)"
            )
        
        return results
    
    def _validate_column_quality(self, dataset: Dataset, column: str) -> Dict[str, Any]:
        """Validate quality of a specific column."""
        results = {
            "errors": [],
            "warnings": []
        }
        
        # Sample data for analysis
        sample_size = min(1000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample_data = dataset.select(sample_indices)[column]
        
        # Check for null values
        null_count = sum(1 for item in sample_data if item is None or item == "")
        null_ratio = null_count / len(sample_data)
        
        if null_ratio > 0.1:  # More than 10% null
            results["warnings"].append(
                f"Column '{column}' has {null_ratio:.2%} null values"
            )
        
        # Check text length constraints if text column
        if any(keyword in column.lower() for keyword in ['text', 'content', 'description']):
            text_lengths = [len(str(item)) for item in sample_data if item is not None]
            
            if text_lengths:
                avg_length = np.mean(text_lengths)
                max_length = max(text_lengths)
                min_length = min(text_lengths)
                
                if max_length > self.config.max_text_length:
                    results["warnings"].append(
                        f"Column '{column}' has very long text (max: {max_length})"
                    )
                
                if min_length < self.config.min_text_length:
                    results["warnings"].append(
                        f"Column '{column}' has very short text (min: {min_length})"
                    )
                
                results[f"{column}_avg_length"] = avg_length
                results[f"{column}_max_length"] = max_length
                results[f"{column}_min_length"] = min_length
        
        return results
    
    def _validate_content(self, dataset: Dataset) -> Dict[str, Any]:
        """Validate content aspects."""
        results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # Language detection for text columns
        text_columns = [col for col in dataset.column_names if any(
            keyword in col.lower() for keyword in ['text', 'content', 'description', 'title']
        )]
        
        for column in text_columns:
            # Sample text for language detection
            sample_size = min(100, len(dataset))
            sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
            sample_data = dataset.select(sample_indices)[column]
            
            non_null_texts = [str(item) for item in sample_data if item is not None and str(item).strip()]
            
            if non_null_texts:
                language_result = self._detect_language_consistency(non_null_texts)
                results[f"{column}_language"] = language_result
                
                if not language_result.get("consistent", True):
                    results["warnings"].append(
                        f"Language inconsistency detected in column '{column}'"
                    )
        
        # Check for potentially harmful content
        harmful_patterns = self._check_harmful_content(dataset)
        if harmful_patterns["found"]:
            results["warnings"].append(
                f"Potentially harmful content patterns found: {list(harmful_patterns['patterns'].keys())}"
            )
        
        return results
    
    def _detect_language_consistency(self, texts: List[str]) -> Dict[str, Any]:
        """Detect language consistency in text samples."""
        # Simple language detection using character patterns
        pashto_patterns = [
            r'ء', r'آ', r'أ', r'إ', r'ؤ', r'ئ',  # Arabic diacritics
            r'پ', r'چ', r'ځ', r'څ', r'ڈ', r'ړ',  # Pashto-specific characters
            r'ښ', r'ڛ', r'ڝ', r'ڞ', r'ڟ', r'ڠ',
            r'ڢ', r'ڣ', r'ڤ', r'ڥ', r'ڦ', r'ڧ',
            r'ڨ', r'ک', r'ڪ', r'ګ', r'ڬ', r'ڭ',
            r'ڮ', r'ی', r'ۍ', r'ێ', r'ې', r'ۑ'
        ]
        
        pashto_count = 0
        for text in texts:
            for pattern in pashto_patterns:
                if re.search(pattern, text):
                    pashto_count += 1
                    break
        
        ratio = pashto_count / len(texts) if texts else 0
        
        return {
            "pashto_ratio": ratio,
            "consistent": ratio > 0.7,  # 70% threshold
            "detected_language": "pas" if ratio > 0.5 else "unknown"
        }
    
    def _check_harmful_content(self, dataset: Dataset) -> Dict[str, Any]:
        """Check for potentially harmful content patterns."""
        patterns = {
            "personal_info": [r'\b\d{3}-\d{2}-\d{4}\b', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            "phone_numbers": [r'\b\d{3}-\d{3}-\d{4}\b', r'\b\(\d{3}\)\s*\d{3}-\d{4}\b'],
            "credit_cards": [r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b']
        }
        
        found = False
        pattern_counts = {}
        
        # Sample a subset for performance
        sample_size = min(1000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        text_columns = [col for col in dataset.column_names if any(
            keyword in col.lower() for keyword in ['text', 'content', 'description']
        )]
        
        for column in text_columns:
            for pattern_name, regex_list in patterns.items():
                for regex_pattern in regex_list:
                    matches = 0
                    for text in sample[column]:
                        if text and re.search(regex_pattern, str(text)):
                            matches += 1
                    
                    if matches > 0:
                        found = True
                        if pattern_name not in pattern_counts:
                            pattern_counts[pattern_name] = 0
                        pattern_counts[pattern_name] += matches
        
        return {
            "found": found,
            "patterns": pattern_counts
        }
    
    def _validate_statistics(self, dataset: Dataset) -> Dict[str, Any]:
        """Validate statistical aspects of the dataset."""
        results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # Calculate basic statistics
        stats = {}
        for column in dataset.column_names:
            column_stats = self._calculate_column_statistics(dataset, column)
            stats[column] = column_stats
        
        # Check for class imbalance
        categorical_columns = [col for col in dataset.column_names if 
                             hasattr(dataset.features.get(col), 'names')]
        
        for column in categorical_columns:
            class_dist = self._get_class_distribution(dataset, column)
            imbalance = self._calculate_imbalance_ratio(class_dist)
            
            if imbalance > 0.8:  # Very imbalanced
                results["warnings"].append(
                    f"High class imbalance in column '{column}' (imbalance ratio: {imbalance:.2f})"
                )
        
        return results
    
    def _calculate_column_statistics(self, dataset: Dataset, column: str) -> Dict[str, Any]:
        """Calculate statistics for a column."""
        # Sample data for performance
        sample_size = min(10000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample_data = dataset.select(sample_indices)[column]
        
        # Remove None values
        clean_data = [item for item in sample_data if item is not None]
        
        if not clean_data:
            return {"error": "No valid data"}
        
        # Type-specific statistics
        if isinstance(clean_data[0], (int, float)):
            return {
                "type": "numeric",
                "count": len(clean_data),
                "mean": np.mean(clean_data),
                "std": np.std(clean_data),
                "min": np.min(clean_data),
                "max": np.max(clean_data),
                "median": np.median(clean_data)
            }
        else:
            text_lengths = [len(str(item)) for item in clean_data]
            return {
                "type": "text",
                "count": len(clean_data),
                "avg_length": np.mean(text_lengths),
                "max_length": max(text_lengths),
                "min_length": min(text_lengths),
                "unique_count": len(set(clean_data))
            }
    
    def _get_class_distribution(self, dataset: Dataset, column: str) -> Dict[str, Any]:
        """Get class distribution for a categorical column."""
        # Sample data for performance
        sample_size = min(10000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample_data = dataset.select(sample_indices)[column]
        
        # Remove None values
        clean_data = [item for item in sample_data if item is not None]
        
        return dict(Counter(clean_data))
    
    def _calculate_imbalance_ratio(self, class_distribution: Dict[str, Any]) -> float:
        """Calculate imbalance ratio (max_class_count / min_class_count)."""
        if not class_distribution:
            return 0
        
        counts = list(class_distribution.values())
        return max(counts) / min(counts)
    
    def _validate_memory_usage(self, dataset: Dataset) -> Dict[str, Any]:
        """Validate memory usage and optimization."""
        results = {
            "status": "PASS",
            "errors": [],
            "warnings": []
        }
        
        # Get memory usage
        memory_mb = dataset.nbytes / (1024 * 1024)
        size_mb = dataset.dataset_size / (1024 * 1024)
        
        results["memory_usage_mb"] = memory_mb
        results["storage_size_mb"] = size_mb
        
        # Check if memory usage is reasonable
        if memory_mb > self.config.max_memory_gb * 1024:
            results["warnings"].append(
                f"High memory usage: {memory_mb:.1f} MB"
            )
        
        # Check compression ratio
        if size_mb > 0:
            compression_ratio = memory_mb / size_mb
            results["compression_ratio"] = compression_ratio
            
            if compression_ratio > 10:  # Very low compression
                results["warnings"].append(
                    f"Poor data compression: ratio {compression_ratio:.1f}x"
                )
        
        return results
    
    def _calculate_completeness(self, dataset: Dataset) -> float:
        """Calculate overall dataset completeness."""
        total_cells = len(dataset) * len(dataset.column_names)
        if total_cells == 0:
            return 0
        
        non_null_count = 0
        
        # Sample for performance
        sample_size = min(1000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        for column in sample.column_names:
            non_null_count += sum(1 for item in sample[column] if item is not None and item != "")
        
        sample_cells = len(sample) * len(sample.column_names)
        return non_null_count / sample_cells if sample_cells > 0 else 0
    
    def _check_duplicate_rows(self, dataset: Dataset) -> Dict[str, Any]:
        """Check for duplicate rows."""
        # Sample for performance
        sample_size = min(5000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        # Convert to pandas for easier duplicate detection
        df = sample.to_pandas()
        
        duplicates = df.duplicated()
        duplicate_count = duplicates.sum()
        ratio = duplicate_count / len(df) if len(df) > 0 else 0
        
        return {
            "count": int(duplicate_count),
            "ratio": ratio
        }
    
    def _calculate_validation_metrics(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate validation metrics."""
        total_checks = 0
        passed_checks = 0
        
        for check_results in validation_results["checks"].values():
            if check_results.get("status") == "PASS":
                passed_checks += 1
            total_checks += 1
        
        return {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "pass_rate": passed_checks / total_checks if total_checks > 0 else 0,
            "error_count": len(validation_results["errors"]),
            "warning_count": len(validation_results["warnings"])
        }
    
    def validate_splits(self, dataset_dict: DatasetDict) -> Dict[str, Any]:
        """Validate dataset splits."""
        self.logger.info("Validating dataset splits")
        
        results = {
            "overall_status": "PASS",
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        # Check split sizes
        total_size = sum(len(split) for split in dataset_dict.values())
        expected_size = len(list(dataset_dict.values())[0]) * len(dataset_dict)
        
        if total_size != expected_size:
            results["errors"].append(
                f"Total size mismatch: {total_size} vs expected {expected_size}"
            )
            results["overall_status"] = "FAIL"
        
        # Check for empty splits
        for split_name, split_dataset in dataset_dict.items():
            if len(split_dataset) == 0:
                results["errors"].append(f"Split '{split_name}' is empty")
                results["overall_status"] = "FAIL"
        
        # Check split ratios
        if len(dataset_dict) > 1:
            split_sizes = [len(split) for split in dataset_dict.values()]
            split_ratios = [size / total_size for size in split_sizes]
            
            for i, (split_name, ratio) in enumerate(zip(dataset_dict.keys(), split_ratios)):
                results["checks"][f"{split_name}_ratio"] = ratio
        
        return results