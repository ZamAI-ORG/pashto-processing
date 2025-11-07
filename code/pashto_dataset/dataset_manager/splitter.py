"""
Dataset Splitter
================

Handles dataset splitting into train/validation/test sets.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Union
import numpy as np
from collections import Counter
from datasets import Dataset, DatasetDict
import pandas as pd

from .config import DatasetConfig


class DatasetSplitter:
    """Handles dataset splitting with various strategies."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.logger = logging.getLogger(f"DatasetSplitter[{config.dataset_name}]")
        random.seed(42)  # For reproducibility
        np.random.seed(42)
    
    def split(self, dataset: Dataset, 
             ratios: Dict[str, float], 
             strategy: str = "random",
             stratified_column: Optional[str] = None,
             group_column: Optional[str] = None) -> DatasetDict:
        """
        Split dataset using various strategies.
        
        Args:
            dataset: Dataset to split
            ratios: Dict with split ratios {'train': 0.8, 'val': 0.1, 'test': 0.1}
            strategy: Splitting strategy ('random', 'stratified', 'group', 'temporal')
            stratified_column: Column for stratified splitting
            group_column: Column for group-based splitting
            
        Returns:
            DatasetDict with splits
        """
        self.logger.info(f"Splitting dataset with strategy: {strategy}")
        
        # Validate ratios
        self._validate_ratios(ratios)
        
        if strategy == "random":
            return self._random_split(dataset, ratios)
        elif strategy == "stratified":
            return self._stratified_split(dataset, ratios, stratified_column)
        elif strategy == "group":
            return self._group_split(dataset, ratios, group_column)
        elif strategy == "temporal":
            return self._temporal_split(dataset, ratios)
        else:
            raise ValueError(f"Unknown splitting strategy: {strategy}")
    
    def _validate_ratios(self, ratios: Dict[str, float]):
        """Validate split ratios."""
        if not ratios:
            raise ValueError("No ratios provided")
        
        total = sum(ratios.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Split ratios must sum to 1.0, got {total}")
        
        for split_name, ratio in ratios.items():
            if not 0 <= ratio <= 1:
                raise ValueError(f"Split ratio for {split_name} must be between 0 and 1, got {ratio}")
    
    def _random_split(self, dataset: Dataset, ratios: Dict[str, float]) -> DatasetDict:
        """Perform random split."""
        self.logger.info("Performing random split")
        
        total_size = len(dataset)
        num_samples = {name: int(total_size * ratio) for name, ratio in ratios.items()}
        
        # Adjust for rounding errors
        total_assigned = sum(num_samples.values())
        if total_assigned < total_size:
            # Add remaining samples to the first split
            first_split = list(ratios.keys())[0]
            num_samples[first_split] += total_size - total_assigned
        
        # Generate random indices
        indices = list(range(total_size))
        random.shuffle(indices)
        
        # Split indices
        splits = {}
        start_idx = 0
        
        for split_name in ratios.keys():
            end_idx = start_idx + num_samples[split_name]
            split_indices = indices[start_idx:end_idx]
            splits[split_name] = dataset.select(split_indices)
            start_idx = end_idx
        
        return DatasetDict(splits)
    
    def _stratified_split(self, dataset: Dataset, 
                         ratios: Dict[str, float], 
                         stratified_column: str) -> DatasetDict:
        """Perform stratified split based on a column."""
        if stratified_column not in dataset.column_names:
            raise ValueError(f"Column '{stratified_column}' not found in dataset")
        
        self.logger.info(f"Performing stratified split on column: {stratified_column}")
        
        # Get column values
        column_values = dataset[stratified_column]
        
        # Group indices by class
        class_indices = {}
        for i, value in enumerate(column_values):
            if value not in class_indices:
                class_indices[value] = []
            class_indices[value].append(i)
        
        # Split each class separately
        splits = {name: [] for name in ratios.keys()}
        
        for class_value, indices in class_indices.items():
            class_size = len(indices)
            class_ratios = {name: int(class_size * ratio) for name, ratio in ratios.items()}
            
            # Adjust for rounding
            total_assigned = sum(class_ratios.values())
            if total_assigned < class_size:
                first_split = list(ratios.keys())[0]
                class_ratios[first_split] += class_size - total_assigned
            
            # Shuffle indices
            random.shuffle(indices)
            
            # Split this class
            start_idx = 0
            for split_name in ratios.keys():
                end_idx = start_idx + class_ratios[split_name]
                split_indices = indices[start_idx:end_idx]
                splits[split_name].extend(split_indices)
                start_idx = end_idx
        
        # Create datasets from selected indices
        result_splits = {}
        for split_name, indices in splits.items():
            result_splits[split_name] = dataset.select(indices)
        
        return DatasetDict(result_splits)
    
    def _group_split(self, dataset: Dataset, 
                    ratios: Dict[str, float], 
                    group_column: str) -> DatasetDict:
        """Perform group-based split to avoid data leakage."""
        if group_column not in dataset.column_names:
            raise ValueError(f"Column '{group_column}' not found in dataset")
        
        self.logger.info(f"Performing group split on column: {group_column}")
        
        # Get group values
        group_values = dataset[group_column]
        
        # Get unique groups
        unique_groups = list(set(group_values))
        random.shuffle(unique_groups)
        
        # Calculate group sizes for each split
        total_groups = len(unique_groups)
        group_counts = {name: int(total_groups * ratio) for name, ratio in ratios.items()}
        
        # Adjust for rounding
        total_assigned = sum(group_counts.values())
        if total_assigned < total_groups:
            first_split = list(ratios.keys())[0]
            group_counts[first_split] += total_groups - total_assigned
        
        # Assign groups to splits
        splits = {name: [] for name in ratios.keys()}
        start_idx = 0
        
        for split_name in ratios.keys():
            end_idx = start_idx + group_counts[split_name]
            split_groups = unique_groups[start_idx:end_idx]
            
            # Find all samples belonging to these groups
            for i, group_value in enumerate(group_values):
                if group_value in split_groups:
                    splits[split_name].append(i)
            
            start_idx = end_idx
        
        # Create datasets from selected indices
        result_splits = {}
        for split_name, indices in splits.items():
            result_splits[split_name] = dataset.select(indices)
        
        return DatasetDict(result_splits)
    
    def _temporal_split(self, dataset: Dataset, ratios: Dict[str, float]) -> DatasetDict:
        """Perform temporal split based on time column."""
        # Look for time-related columns
        time_columns = [col for col in dataset.column_names if any(
            keyword in col.lower() for keyword in ['time', 'date', 'timestamp', 'created', 'updated']
        )]
        
        if not time_columns:
            # Fall back to random split if no time column found
            self.logger.warning("No time column found, falling back to random split")
            return self._random_split(dataset, ratios)
        
        time_column = time_columns[0]  # Use first time column found
        self.logger.info(f"Performing temporal split on column: {time_column}")
        
        # Convert to DataFrame for easier sorting
        df = dataset.to_pandas()
        
        # Sort by time
        df = df.sort_values(by=time_column)
        
        # Calculate split points
        total_size = len(df)
        split_points = {}
        cumulative = 0
        
        for split_name, ratio in ratios.items():
            cumulative += ratio
            split_point = int(total_size * cumulative)
            split_points[split_name] = split_point
        
        # Create splits
        splits = {}
        start_idx = 0
        
        for split_name, end_idx in split_points.items():
            split_df = df.iloc[start_idx:end_idx]
            splits[split_name] = Dataset.from_pandas(split_df, preserve_index=False)
            start_idx = end_idx
        
        return DatasetDict(splits)
    
    def k_fold_split(self, dataset: Dataset, k: int = 5) -> List[DatasetDict]:
        """
        Create k-fold cross-validation splits.
        
        Args:
            dataset: Dataset to split
            k: Number of folds
            
        Returns:
            List of DatasetDict with k-1 train folds and 1 validation fold each
        """
        if k < 2:
            raise ValueError("k must be at least 2")
        
        self.logger.info(f"Creating {k}-fold cross-validation splits")
        
        # Shuffle indices
        indices = list(range(len(dataset)))
        random.shuffle(indices)
        
        # Calculate fold sizes
        fold_size = len(dataset) // k
        remainder = len(dataset) % k
        
        folds = []
        for i in range(k):
            # Adjust fold size for remainder
            current_fold_size = fold_size + (1 if i < remainder else 0)
            
            # Get validation indices
            val_start = i * fold_size
            val_end = val_start + current_fold_size
            val_indices = indices[val_start:val_end]
            
            # Get training indices (all others)
            train_indices = indices[:val_start] + indices[val_end:]
            
            # Create splits
            train_dataset = dataset.select(train_indices)
            val_dataset = dataset.select(val_indices)
            
            fold = DatasetDict({
                'train': train_dataset,
                'validation': val_dataset
            })
            
            folds.append(fold)
        
        return folds
    
    def custom_split(self, dataset: Dataset, 
                    custom_splits: Dict[str, List[int]]) -> DatasetDict:
        """
        Create custom splits using specific indices.
        
        Args:
            dataset: Dataset to split
            custom_splits: Dict mapping split names to list of indices
            
        Returns:
            DatasetDict with custom splits
        """
        self.logger.info("Creating custom splits")
        
        splits = {}
        for split_name, indices in custom_splits.items():
            splits[split_name] = dataset.select(indices)
        
        return DatasetDict(splits)
    
    def analyze_split_balance(self, dataset_dict: DatasetDict, 
                            reference_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze the balance and distribution across splits.
        
        Args:
            dataset_dict: DatasetDict with splits
            reference_column: Column to analyze distribution for
            
        Returns:
            Analysis results
        """
        self.logger.info("Analyzing split balance")
        
        analysis = {
            "split_sizes": {},
            "class_distribution": {},
            "balance_metrics": {}
        }
        
        # Get split sizes
        for split_name, split_dataset in dataset_dict.items():
            analysis["split_sizes"][split_name] = len(split_dataset)
        
        # Analyze class distribution if column specified
        if reference_column:
            for split_name, split_dataset in dataset_dict.items():
                if reference_column in split_dataset.column_names:
                    values = split_dataset[reference_column]
                    distribution = dict(Counter(values))
                    analysis["class_distribution"][split_name] = distribution
        
        # Calculate balance metrics
        total_samples = sum(analysis["split_sizes"].values())
        if total_samples > 0:
            expected_size = total_samples / len(dataset_dict)
            analysis["balance_metrics"]["expected_size"] = expected_size
            
            for split_name, actual_size in analysis["split_sizes"].values():
                deviation = abs(actual_size - expected_size) / expected_size
                analysis["balance_metrics"][f"{split_name}_deviation"] = deviation
        
        return analysis
    
    def merge_splits(self, dataset_dict: DatasetDict, 
                    merge_strategy: str = "concat") -> Dataset:
        """
        Merge multiple splits back into a single dataset.
        
        Args:
            dataset_dict: DatasetDict with splits to merge
            merge_strategy: How to merge ('concat', 'interleave')
            
        Returns:
            Merged Dataset
        """
        self.logger.info(f"Merging splits with strategy: {merge_strategy}")
        
        splits_list = list(dataset_dict.values())
        
        if not splits_list:
            raise ValueError("No splits to merge")
        
        if len(splits_list) == 1:
            return splits_list[0]
        
        if merge_strategy == "concat":
            result = splits_list[0]
            for split in splits_list[1:]:
                result = result.concatenate(split)
        elif merge_strategy == "interleave":
            result = splits_list[0].interleave(splits_list[1:])
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")
        
        self.logger.info(f"Merged {len(splits_list)} splits into {len(result)} samples")
        return result