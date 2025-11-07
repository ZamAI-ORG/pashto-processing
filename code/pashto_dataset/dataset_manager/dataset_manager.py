"""
Core Dataset Manager
===================

Main interface for dataset creation, management, and operations.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
from datasets import Dataset, DatasetDict
import numpy as np

from .config import DatasetConfig, default_config, validate_config
from .dataset_creator import DatasetCreator
from .metadata_manager import MetadataManager
from .versioning import DatasetVersioning
from .splitter import DatasetSplitter
from .validator import DatasetValidator
from .quality_metrics import QualityMetrics
from .exporter import DatasetExporter
from .memory_optimizer import MemoryOptimizer


class DatasetManager:
    """
    Main dataset management system with full Hugging Face integration.
    """
    
    def __init__(self, config: Optional[DatasetConfig] = None):
        """
        Initialize the dataset manager.
        
        Args:
            config: Configuration object. Uses default if None.
        """
        self.config = config or default_config
        
        # Validate configuration
        errors = validate_config(self.config)
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        # Set up logging
        self._setup_logging()
        
        # Initialize components
        self.creator = DatasetCreator(self.config)
        self.metadata_manager = MetadataManager(self.config)
        self.versioning = DatasetVersioning(self.config)
        self.splitter = DatasetSplitter(self.config)
        self.validator = DatasetValidator(self.config)
        self.quality_metrics = QualityMetrics(self.config)
        self.exporter = DatasetExporter(self.config)
        self.optimizer = MemoryOptimizer(self.config)
        
        # Internal state
        self._dataset: Optional[Dataset] = None
        self._dataset_dict: Optional[DatasetDict] = None
        self._current_version: Optional[str] = None
        
        self.logger.info(f"DatasetManager initialized for {self.config.dataset_name}")
    
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f"DatasetManager[{self.config.dataset_name}]")
    
    def create_dataset(self, data: Union[Dict, List, pd.DataFrame], 
                      schema: Optional[Dict] = None,
                      validate_data: bool = True) -> Dataset:
        """
        Create a new dataset from data.
        
        Args:
            data: Input data (dict, list, or DataFrame)
            schema: Optional schema definition
            validate_data: Whether to validate the data
            
        Returns:
            Created Dataset object
        """
        self.logger.info("Creating new dataset")
        
        # Create dataset
        self._dataset = self.creator.create_dataset(data, schema)
        
        # Validate if requested
        if validate_data:
            self.validator.validate_dataset(self._dataset)
        
        # Apply memory optimization
        self._dataset = self.optimizer.optimize_dataset(self._dataset)
        
        # Initialize metadata
        self.metadata_manager.initialize_metadata(self._dataset)
        
        self.logger.info(f"Dataset created with {len(self._dataset)} samples")
        return self._dataset
    
    def load_dataset(self, version: Optional[str] = None) -> Dataset:
        """
        Load a dataset from storage.
        
        Args:
            version: Optional version to load. Loads latest if None.
            
        Returns:
            Loaded Dataset object
        """
        self.logger.info(f"Loading dataset version: {version or 'latest'}")
        
        # Get version information
        if version is None:
            version = self.versioning.get_latest_version()
        
        self._current_version = version
        
        # Load dataset
        self._dataset = self.creator.load_dataset_from_version(version)
        
        if self._dataset is None:
            raise FileNotFoundError(f"Dataset version {version} not found")
        
        self.logger.info(f"Dataset loaded with {len(self._dataset)} samples")
        return self._dataset
    
    def save_dataset(self, version: Optional[str] = None) -> str:
        """
        Save the current dataset to storage.
        
        Args:
            version: Optional version string. Auto-generates if None.
            
        Returns:
            Version string of saved dataset
        """
        if self._dataset is None:
            raise ValueError("No dataset to save. Create or load a dataset first.")
        
        self.logger.info("Saving dataset")
        
        # Generate version if not provided
        if version is None:
            version = self.versioning.generate_version()
        
        # Create version
        self.versioning.create_version(self._dataset, version)
        
        # Update metadata
        self.metadata_manager.update_metadata(self._dataset, version)
        
        # Save dataset
        self.creator.save_dataset(self._dataset, version)
        
        # Calculate and store quality metrics
        metrics = self.quality_metrics.calculate_all_metrics(self._dataset)
        self.metadata_manager.save_quality_metrics(version, metrics)
        
        self._current_version = version
        self.logger.info(f"Dataset saved as version: {version}")
        return version
    
    def split_dataset(self, train_ratio: Optional[float] = None,
                     val_ratio: Optional[float] = None,
                     test_ratio: Optional[float] = None,
                     strategy: str = "random",
                     stratified_column: Optional[str] = None) -> DatasetDict:
        """
        Split dataset into train/validation/test sets.
        
        Args:
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            strategy: Splitting strategy ('random', 'stratified', 'custom')
            stratified_column: Column for stratified splitting
            
        Returns:
            DatasetDict with splits
        """
        if self._dataset is None:
            raise ValueError("No dataset to split. Create or load a dataset first.")
        
        self.logger.info("Splitting dataset")
        
        # Use config ratios if not provided
        ratios = {
            'train': train_ratio or self.config.train_ratio,
            'val': val_ratio or self.config.val_ratio,
            'test': test_ratio or self.config.test_ratio
        }
        
        # Verify ratios sum to 1
        total = sum(ratios.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Split ratios must sum to 1.0, got {total}")
        
        # Split dataset
        self._dataset_dict = self.splitter.split(
            self._dataset, 
            ratios, 
            strategy, 
            stratified_column
        )
        
        # Validate splits
        self.validator.validate_splits(self._dataset_dict)
        
        # Apply memory optimization to splits
        self._dataset_dict = self.optimizer.optimize_dataset_dict(self._dataset_dict)
        
        # Update metadata
        self.metadata_manager.update_splits(self._dataset_dict, ratios, strategy, stratified_column)
        
        total_samples = sum(len(split) for split in self._dataset_dict.values())
        self.logger.info(f"Dataset split into {len(self._dataset_dict)} sets with {total_samples} total samples")
        
        return self._dataset_dict
    
    def validate_dataset(self) -> Dict[str, Any]:
        """
        Validate the current dataset.
        
        Returns:
            Validation results dictionary
        """
        if self._dataset is None:
            raise ValueError("No dataset to validate. Create or load a dataset first.")
        
        self.logger.info("Validating dataset")
        
        results = self.validator.validate_dataset(self._dataset)
        return results
    
    def calculate_quality_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive quality metrics for the dataset.
        
        Returns:
            Quality metrics dictionary
        """
        if self._dataset is None:
            raise ValueError("No dataset for metrics. Create or load a dataset first.")
        
        self.logger.info("Calculating quality metrics")
        
        metrics = self.quality_metrics.calculate_all_metrics(self._dataset)
        return metrics
    
    def export_dataset(self, format: str, 
                      output_path: Optional[Path] = None,
                      **kwargs) -> Path:
        """
        Export dataset in various formats.
        
        Args:
            format: Export format (json, csv, parquet, conll, etc.)
            output_path: Optional output path
            **kwargs: Additional export parameters
            
        Returns:
            Path to exported file
        """
        if self._dataset is None:
            raise ValueError("No dataset to export. Create or load a dataset first.")
        
        self.logger.info(f"Exporting dataset in {format} format")
        
        if self._dataset_dict is not None:
            # Export splits
            export_path = self.exporter.export_dataset_dict(self._dataset_dict, format, output_path, **kwargs)
        else:
            # Export single dataset
            export_path = self.exporter.export_dataset(self._dataset, format, output_path, **kwargs)
        
        self.logger.info(f"Dataset exported to: {export_path}")
        return export_path
    
    def upload_to_hf(self, version: Optional[str] = None,
                    commit_message: Optional[str] = None) -> str:
        """
        Upload dataset to Hugging Face Hub.
        
        Args:
            version: Version to upload
            commit_message: Commit message
            
        Returns:
            Repository URL
        """
        if self._dataset is None:
            raise ValueError("No dataset to upload. Create or load a dataset first.")
        
        self.logger.info("Uploading dataset to Hugging Face Hub")
        
        if version is None:
            version = self._current_version or "latest"
        
        # Create repository if needed
        if not self.exporter.repository_exists():
            self.exporter.create_repository()
        
        # Generate documentation
        self._generate_dataset_card()
        
        # Upload dataset
        repo_url = self.exporter.upload_to_hub(
            self._dataset,
            version,
            commit_message
        )
        
        self.logger.info(f"Dataset uploaded to: {repo_url}")
        return repo_url
    
    def _generate_dataset_card(self):
        """Generate README.md for the dataset."""
        readme_path = self.config.get_dataset_card_path()
        
        # Collect information
        version = self._current_version or "latest"
        num_samples = len(self._dataset) if self._dataset else 0
        metrics = self.quality_metrics.calculate_all_metrics(self._dataset) if self._dataset else {}
        metadata = self.metadata_manager.get_metadata(version)
        
        # Generate content
        content = self.metadata_manager.generate_dataset_card(
            self.config,
            num_samples,
            metrics,
            metadata
        )
        
        # Write file
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the current dataset.
        
        Returns:
            Dataset information dictionary
        """
        if self._dataset is None:
            return {"status": "No dataset loaded"}
        
        info = {
            "version": self._current_version,
            "num_samples": len(self._dataset),
            "columns": list(self._dataset.column_names),
            "features": self._dataset.features,
            "size_mb": self._dataset.dataset_size / (1024 * 1024),
            "memory_usage_mb": self._dataset.nbytes / (1024 * 1024)
        }
        
        if self._dataset_dict is not None:
            info["splits"] = {
                split_name: len(split_dataset) 
                for split_name, split_dataset in self._dataset_dict.items()
            }
        
        return info
    
    def clear_cache(self):
        """Clear all cache files."""
        self.logger.info("Clearing cache")
        self.optimizer.clear_cache()
    
    def __str__(self) -> str:
        """String representation of the dataset manager."""
        return f"DatasetManager(name={self.config.dataset_name}, version={self._current_version})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"DatasetManager(config={self.config}, version={self._current_version}, samples={len(self._dataset) if self._dataset else 0})"