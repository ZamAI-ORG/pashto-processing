"""
Dataset Creator
==============

Handles dataset creation, loading, and basic operations.
"""

import json
import pickle
import logging
from typing import Dict, List, Any, Union, Optional
from pathlib import Path
import pandas as pd
from datasets import Dataset, Features, Value, Sequence, ClassLabel
import numpy as np

from .config import DatasetConfig


class DatasetCreator:
    """Creates and manages Hugging Face datasets."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.logger = logging.getLogger(f"DatasetCreator[{config.dataset_name}]")
    
    def create_dataset(self, data: Union[Dict, List, pd.DataFrame], 
                      schema: Optional[Dict] = None) -> Dataset:
        """
        Create a new dataset from various data formats.
        
        Args:
            data: Input data (dict, list, DataFrame)
            schema: Optional schema definition
            
        Returns:
            Created Dataset object
        """
        self.logger.info("Creating dataset from data")
        
        # Convert different data formats to a common format
        if isinstance(data, pd.DataFrame):
            dataset = Dataset.from_pandas(data, features=schema)
        elif isinstance(data, dict):
            dataset = Dataset.from_dict(data, features=schema)
        elif isinstance(data, list):
            dataset = Dataset.from_list(data, features=schema)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        # Apply schema if provided
        if schema is not None:
            dataset = dataset.cast(Features.from_dict(schema))
        
        self.logger.info(f"Dataset created with {len(dataset)} samples")
        return dataset
    
    def create_empty_dataset(self, schema: Dict) -> Dataset:
        """
        Create an empty dataset with the given schema.
        
        Args:
            schema: Dataset schema definition
            
        Returns:
            Empty Dataset object
        """
        self.logger.info("Creating empty dataset")
        
        # Create features from schema
        features = self._create_features_from_schema(schema)
        
        # Create empty dataset
        dataset = Dataset.from_dict(
            {col: [] for col in features.keys()},
            features=features
        )
        
        self.logger.info("Empty dataset created")
        return dataset
    
    def load_dataset_from_version(self, version: str) -> Optional[Dataset]:
        """
        Load dataset from a specific version.
        
        Args:
            version: Version string
            
        Returns:
            Loaded Dataset or None if not found
        """
        self.logger.info(f"Loading dataset version: {version}")
        
        version_dir = self.config.data_path / f"v{version}"
        
        if not version_dir.exists():
            self.logger.warning(f"Version directory not found: {version_dir}")
            return None
        
        # Try different loading methods
        dataset = self._try_load_dataset_formats(version_dir)
        
        if dataset is None:
            self.logger.error(f"Could not load dataset version: {version}")
            return None
        
        self.logger.info(f"Successfully loaded dataset version {version} with {len(dataset)} samples")
        return dataset
    
    def _try_load_dataset_formats(self, version_dir: Path) -> Optional[Dataset]:
        """Try loading dataset in different formats."""
        # Try Arrow format (Hugging Face default)
        arrow_file = version_dir / "dataset.arrow"
        if arrow_file.exists():
            try:
                return Dataset.load_from_disk(str(version_dir))
            except Exception as e:
                self.logger.warning(f"Could not load Arrow format: {e}")
        
        # Try JSON format
        json_file = version_dir / "dataset.json"
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Dataset.from_dict(data)
            except Exception as e:
                self.logger.warning(f"Could not load JSON format: {e}")
        
        # Try JSONL format
        jsonl_file = version_dir / "dataset.jsonl"
        if jsonl_file.exists():
            try:
                return Dataset.from_json(str(jsonl_file), features=None)
            except Exception as e:
                self.logger.warning(f"Could not load JSONL format: {e}")
        
        # Try CSV format
        csv_file = version_dir / "dataset.csv"
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                return Dataset.from_pandas(df)
            except Exception as e:
                self.logger.warning(f"Could not load CSV format: {e}")
        
        # Try Parquet format
        parquet_file = version_dir / "dataset.parquet"
        if parquet_file.exists():
            try:
                df = pd.read_parquet(parquet_file)
                return Dataset.from_pandas(df)
            except Exception as e:
                self.logger.warning(f"Could not load Parquet format: {e}")
        
        # Try Pickle format
        pickle_file = version_dir / "dataset.pkl"
        if pickle_file.exists():
            try:
                with open(pickle_file, 'rb') as f:
                    data = pickle.load(f)
                if isinstance(data, dict):
                    return Dataset.from_dict(data)
                elif isinstance(data, list):
                    return Dataset.from_list(data)
            except Exception as e:
                self.logger.warning(f"Could not load Pickle format: {e}")
        
        return None
    
    def save_dataset(self, dataset: Dataset, version: str):
        """
        Save dataset in multiple formats.
        
        Args:
            dataset: Dataset to save
            version: Version string
        """
        self.logger.info(f"Saving dataset version: {version}")
        
        version_dir = self.config.data_path / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Save in multiple formats for compatibility
        formats = {
            'arrow': self._save_arrow,
            'json': self._save_json,
            'jsonl': self._save_jsonl,
            'csv': self._save_csv,
            'parquet': self._save_parquet
        }
        
        for format_name, save_func in formats.items():
            try:
                save_func(dataset, version_dir)
                self.logger.info(f"Dataset saved in {format_name} format")
            except Exception as e:
                self.logger.warning(f"Failed to save in {format_name} format: {e}")
    
    def _save_arrow(self, dataset: Dataset, version_dir: Path):
        """Save dataset in Arrow format."""
        dataset.save_to_disk(str(version_dir))
    
    def _save_json(self, dataset: Dataset, version_dir: Path):
        """Save dataset in JSON format."""
        json_file = version_dir / "dataset.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(dataset.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _save_jsonl(self, dataset: Dataset, version_dir: Path):
        """Save dataset in JSONL format."""
        jsonl_file = version_dir / "dataset.jsonl"
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for item in dataset:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
    
    def _save_csv(self, dataset: Dataset, version_dir: Path):
        """Save dataset in CSV format."""
        csv_file = version_dir / "dataset.csv"
        df = dataset.to_pandas()
        df.to_csv(csv_file, index=False, encoding='utf-8')
    
    def _save_parquet(self, dataset: Dataset, version_dir: Path):
        """Save dataset in Parquet format."""
        parquet_file = version_dir / "dataset.parquet"
        df = dataset.to_pandas()
        df.to_parquet(parquet_file, index=False)
    
    def _create_features_from_schema(self, schema: Dict) -> Features:
        """
        Create Hugging Face Features from schema definition.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            Features object
        """
        features = {}
        
        for field_name, field_info in schema.items():
            if isinstance(field_info, dict):
                field_type = field_info.get('type', 'string')
                if field_type == 'string':
                    features[field_name] = Value('string')
                elif field_type == 'int':
                    features[field_name] = Value('int32')
                elif field_type == 'float':
                    features[field_name] = Value('float32')
                elif field_type == 'bool':
                    features[field_name] = Value('bool')
                elif field_type == 'sequence':
                    subfield_type = field_info.get('subtype', 'string')
                    if subfield_type == 'string':
                        features[field_name] = Sequence(Value('string'))
                    elif subfield_type == 'int':
                        features[field_name] = Sequence(Value('int32'))
                    elif subfield_type == 'float':
                        features[field_name] = Sequence(Value('float32'))
                elif field_type == 'class_label':
                    class_names = field_info.get('class_names', [])
                    features[field_name] = ClassLabel(names=class_names)
                else:
                    features[field_name] = Value('string')
            else:
                # Simple type definition
                features[field_name] = Value(field_info)
        
        return Features(features)
    
    def merge_datasets(self, datasets: List[Dataset], merge_strategy: str = "concat") -> Dataset:
        """
        Merge multiple datasets.
        
        Args:
            datasets: List of datasets to merge
            merge_strategy: Merge strategy ('concat', 'interleave', 'join')
            
        Returns:
            Merged Dataset
        """
        if not datasets:
            raise ValueError("No datasets provided for merging")
        
        if len(datasets) == 1:
            return datasets[0]
        
        self.logger.info(f"Merging {len(datasets)} datasets with strategy: {merge_strategy}")
        
        if merge_strategy == "concat":
            merged = datasets[0]
            for dataset in datasets[1:]:
                merged = merged.concatenate(dataset)
        elif merge_strategy == "interleave":
            merged = datasets[0].interleave(datasets[1:])
        elif merge_strategy == "join":
            # For joining, we need common columns
            common_columns = set(datasets[0].column_names)
            for dataset in datasets[1:]:
                common_columns = common_columns.intersection(set(dataset.column_names))
            
            if not common_columns:
                raise ValueError("No common columns found for joining")
            
            # Simple inner join on first dataset
            merged = datasets[0]
            for dataset in datasets[1:]:
                merged = merged.join(dataset, keys=list(common_columns))
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")
        
        self.logger.info(f"Merge completed with {len(merged)} samples")
        return merged
    
    def filter_dataset(self, dataset: Dataset, filter_func) -> Dataset:
        """
        Filter dataset using a function.
        
        Args:
            dataset: Dataset to filter
            filter_func: Filter function that takes a sample and returns bool
            
        Returns:
            Filtered Dataset
        """
        self.logger.info("Filtering dataset")
        filtered_dataset = dataset.filter(filter_func)
        self.logger.info(f"Filtered dataset from {len(dataset)} to {len(filtered_dataset)} samples")
        return filtered_dataset
    
    def map_dataset(self, dataset: Dataset, map_func, batched: bool = False) -> Dataset:
        """
        Map function over dataset.
        
        Args:
            dataset: Dataset to map
            map_func: Mapping function
            batched: Whether to use batched processing
            
        Returns:
            Mapped Dataset
        """
        self.logger.info("Mapping dataset")
        mapped_dataset = dataset.map(map_func, batched=batched)
        self.logger.info(f"Dataset mapping completed")
        return mapped_dataset