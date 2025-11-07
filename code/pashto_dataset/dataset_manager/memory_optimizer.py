"""
Memory Optimizer
===============

Handles memory optimization for large datasets and efficient processing.
"""

import logging
import gc
import pickle
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import psutil
import numpy as np
from datasets import Dataset, DatasetDict
import warnings

from .config import DatasetConfig


class MemoryOptimizer:
    """Optimizes memory usage for large datasets."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.cache_path = self.config.cache_path
        self.logger = logging.getLogger(f"MemoryOptimizer[{config.dataset_name}]")
        
        # Memory thresholds
        self.max_memory_gb = config.max_memory_gb
        self.max_memory_mb = self.max_memory_gb * 1024
        self.chunk_size = config.chunk_size
        
        # Create cache directory
        self.cache_path.mkdir(parents=True, exist_ok=True)
    
    def optimize_dataset(self, dataset: Dataset) -> Dataset:
        """
        Optimize dataset for memory usage.
        
        Args:
            dataset: Dataset to optimize
            
        Returns:
            Optimized dataset
        """
        self.logger.info("Starting dataset memory optimization")
        
        current_memory_mb = self._get_memory_usage() / (1024 * 1024)
        self.logger.info(f"Current memory usage: {current_memory_mb:.1f} MB")
        
        if current_memory_mb > self.max_memory_mb:
            self.logger.warning("Memory usage exceeds threshold, applying optimization")
        
        # Apply various optimizations
        optimized_dataset = dataset
        
        # 1. Optimize features (data types)
        optimized_dataset = self._optimize_features(optimized_dataset)
        
        # 2. Apply compression for large datasets
        if len(dataset) > 100000:  # For large datasets
            optimized_dataset = self._apply_compression(optimized_dataset)
        
        # 3. Optimize memory mapping
        optimized_dataset = self._optimize_memory_mapping(optimized_dataset)
        
        # 4. Clean up temporary data
        self._cleanup_memory()
        
        final_memory_mb = self._get_memory_usage() / (1024 * 1024)
        self.logger.info(f"Memory optimization completed. Final usage: {final_memory_mb:.1f} MB")
        
        return optimized_dataset
    
    def optimize_dataset_dict(self, dataset_dict: DatasetDict) -> DatasetDict:
        """
        Optimize DatasetDict (multiple splits) for memory usage.
        
        Args:
            dataset_dict: DatasetDict to optimize
            
        Returns:
            Optimized DatasetDict
        """
        self.logger.info("Starting DatasetDict memory optimization")
        
        optimized_dict = {}
        for split_name, split_dataset in dataset_dict.items():
            self.logger.info(f"Optimizing split: {split_name}")
            optimized_dict[split_name] = self.optimize_dataset(split_dataset)
        
        optimized_dataset_dict = DatasetDict(optimized_dict)
        
        self.logger.info("DatasetDict optimization completed")
        return optimized_dataset_dict
    
    def _optimize_features(self, dataset: Dataset) -> Dataset:
        """Optimize feature data types for better memory usage."""
        self.logger.info("Optimizing feature data types")
        
        # Convert to pandas for easier optimization
        df = dataset.to_pandas()
        
        # Optimize numeric types
        for column in df.columns:
            if df[column].dtype == 'int64':
                # Downcast to int32 or int16
                if df[column].min() >= -32768 and df[column].max() <= 32767:
                    df[column] = df[column].astype('int16')
                elif df[column].min() >= -2147483648 and df[column].max() <= 2147483647:
                    df[column] = df[column].astype('int32')
            
            elif df[column].dtype == 'float64':
                # Downcast to float32
                df[column] = df[column].astype('float32')
            
            elif df[column].dtype == 'object':
                # Optimize string columns
                if column in df.select_dtypes(include=['object']).columns:
                    # Convert to category if low cardinality
                    unique_ratio = df[column].nunique() / len(df)
                    if unique_ratio < 0.5:  # Less than 50% unique values
                        df[column] = df[column].astype('category')
        
        # Convert back to Dataset
        optimized_dataset = Dataset.from_pandas(df)
        return optimized_dataset
    
    def _apply_compression(self, dataset: Dataset) -> Dataset:
        """Apply compression for large datasets."""
        self.logger.info("Applying compression for large dataset")
        
        # For very large datasets, we might want to use memory mapping
        if len(dataset) > 500000:  # 500K+ samples
            # Create memory-mapped cache
            cache_key = f"compressed_{hash(str(dataset.column_names))}"
            cache_file = self.cache_path / f"{cache_key}.pkl"
            
            if not cache_file.exists():
                # Save with compression
                with open(cache_file, 'wb') as f:
                    pickle.dump(dataset, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                self.logger.info(f"Created compressed cache: {cache_file}")
            
            # Load and return
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        return dataset
    
    def _optimize_memory_mapping(self, dataset: Dataset) -> Dataset:
        """Optimize memory mapping for large datasets."""
        if len(dataset) < 50000:  # Don't optimize small datasets
            return dataset
        
        self.logger.info("Optimizing memory mapping")
        
        # For large datasets, try to optimize the underlying storage
        try:
            # Convert to memory-efficient format
            dataset = dataset.with_format("numpy")
            
            # Force garbage collection
            gc.collect()
            
            return dataset
        except Exception as e:
            self.logger.warning(f"Memory mapping optimization failed: {str(e)}")
            return dataset
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except:
            # Fallback: estimate based on dataset size
            return 0
    
    def _cleanup_memory(self):
        """Clean up temporary memory usage."""
        gc.collect()
    
    def process_in_chunks(self, dataset: Dataset, 
                         process_func,
                         chunk_size: Optional[int] = None,
                         **kwargs) -> Dataset:
        """
        Process dataset in chunks to manage memory usage.
        
        Args:
            dataset: Dataset to process
            process_func: Function to apply to each chunk
            chunk_size: Size of each chunk
            **kwargs: Additional arguments for process_func
            
        Returns:
            Processed dataset
        """
        if chunk_size is None:
            chunk_size = self.chunk_size
        
        self.logger.info(f"Processing dataset in chunks of {chunk_size}")
        
        total_samples = len(dataset)
        processed_chunks = []
        
        for start_idx in range(0, total_samples, chunk_size):
            end_idx = min(start_idx + chunk_size, total_samples)
            
            # Get chunk
            chunk_indices = list(range(start_idx, end_idx))
            chunk = dataset.select(chunk_indices)
            
            # Process chunk
            try:
                processed_chunk = process_func(chunk, **kwargs)
                processed_chunks.append(processed_chunk)
            except Exception as e:
                self.logger.error(f"Failed to process chunk {start_idx}-{end_idx}: {str(e)}")
                raise
            
            # Progress logging
            progress = (end_idx / total_samples) * 100
            self.logger.info(f"Progress: {progress:.1f}% ({end_idx}/{total_samples})")
            
            # Clean up memory
            del chunk
            gc.collect()
        
        # Concatenate all processed chunks
        if processed_chunks:
            result = processed_chunks[0]
            for chunk in processed_chunks[1:]:
                result = result.concatenate(chunk)
            return result
        else:
            raise RuntimeError("No chunks were processed successfully")
    
    def filter_in_memory(self, dataset: Dataset, 
                        filter_func,
                        use_memory_mapping: bool = True) -> Dataset:
        """
        Filter dataset with memory optimization.
        
        Args:
            dataset: Dataset to filter
            filter_func: Filter function
            use_memory_mapping: Whether to use memory mapping for large datasets
            
        Returns:
            Filtered dataset
        """
        if len(dataset) > 100000 and use_memory_mapping:
            self.logger.info("Using memory-optimized filtering")
            return self.process_in_chunks(dataset, self._filter_chunk, filter_func=filter_func)
        else:
            return dataset.filter(filter_func)
    
    def _filter_chunk(self, chunk: Dataset, filter_func) -> Dataset:
        """Filter a single chunk."""
        return chunk.filter(filter_func)
    
    def map_in_memory(self, dataset: Dataset,
                     map_func,
                     batched: bool = False,
                     batch_size: Optional[int] = None) -> Dataset:
        """
        Map function over dataset with memory optimization.
        
        Args:
            dataset: Dataset to map
            map_func: Mapping function
            batched: Whether to use batched processing
            batch_size: Batch size for batched processing
            
        Returns:
            Mapped dataset
        """
        if len(dataset) > 50000 and not batched:
            self.logger.info("Using memory-optimized mapping")
            return self.process_in_chunks(dataset, self._map_chunk, map_func=map_func, batched=batched)
        else:
            return dataset.map(map_func, batched=batched, batch_size=batch_size)
    
    def _map_chunk(self, chunk: Dataset, map_func, batched: bool = False) -> Dataset:
        """Map function over a single chunk."""
        return chunk.map(map_func, batched=batched)
    
    def analyze_memory_usage(self, dataset: Dataset) -> Dict[str, Any]:
        """
        Analyze memory usage of the dataset.
        
        Args:
            dataset: Dataset to analyze
            
        Returns:
            Memory analysis results
        """
        analysis = {
            "dataset_size": len(dataset),
            "num_columns": len(dataset.column_names),
            "estimated_memory_mb": dataset.nbytes / (1024 * 1024),
            "column_analysis": {},
            "recommendations": []
        }
        
        # Analyze each column
        for column in dataset.column_names:
            column_info = self._analyze_column_memory(dataset, column)
            analysis["column_analysis"][column] = column_info
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_memory_recommendations(analysis)
        
        return analysis
    
    def _analyze_column_memory(self, dataset: Dataset, column: str) -> Dict[str, Any]:
        """Analyze memory usage of a specific column."""
        # Sample for analysis
        sample_size = min(1000, len(dataset))
        sample_indices = list(range(0, len(dataset), max(1, len(dataset) // sample_size)))
        sample = dataset.select(sample_indices)
        
        column_data = sample[column]
        
        analysis = {
            "type": str(type(column_data[0]) if column_data else "unknown"),
            "sample_memory_bytes": 0,
            "estimated_total_memory_mb": 0,
            "optimization_potential": "low"
        }
        
        try:
            # Calculate memory usage of sample
            import sys
            sample_memory = sys.getsizeof(column_data)
            analysis["sample_memory_bytes"] = sample_memory
            
            # Estimate total memory
            estimated_memory = (sample_memory * len(dataset)) / len(sample)
            analysis["estimated_total_memory_mb"] = estimated_memory / (1024 * 1024)
            
            # Assess optimization potential
            if len(set(str(item) for item in column_data if item is not None)) / len(column_data) < 0.5:
                analysis["optimization_potential"] = "high"
            elif estimated_memory > 50 * 1024 * 1024:  # 50MB
                analysis["optimization_potential"] = "medium"
        except Exception as e:
            self.logger.warning(f"Could not analyze column {column}: {str(e)}")
        
        return analysis
    
    def _generate_memory_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate memory optimization recommendations."""
        recommendations = []
        
        total_memory_mb = analysis["estimated_memory_mb"]
        
        if total_memory_mb > self.max_memory_mb:
            recommendations.append(
                f"Total memory usage ({total_memory_mb:.1f}MB) exceeds threshold ({self.max_memory_mb:.1f}MB)"
            )
            recommendations.append("Consider using chunked processing")
            recommendations.append("Apply feature type optimization")
        
        # Check individual columns
        for column, column_info in analysis["column_analysis"].items():
            if column_info["optimization_potential"] == "high":
                recommendations.append(f"Column '{column}' has high optimization potential (category conversion)")
            elif column_info["estimated_total_memory_mb"] > 10:
                recommendations.append(f"Column '{column}' is large ({column_info['estimated_total_memory_mb']:.1f}MB), consider compression")
        
        if len(analysis["dataset_size"]) > 100000:
            recommendations.append("Large dataset detected, consider using memory mapping")
        
        return recommendations
    
    def cache_dataset(self, dataset: Dataset, cache_key: str) -> Path:
        """
        Cache dataset to disk to free up memory.
        
        Args:
            dataset: Dataset to cache
            cache_key: Unique key for the cache
            
        Returns:
            Path to cached file
        """
        cache_file = self.cache_path / f"{cache_key}.pkl"
        
        self.logger.info(f"Caching dataset with key: {cache_key}")
        
        with open(cache_file, 'wb') as f:
            pickle.dump(dataset, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        return cache_file
    
    def load_cached_dataset(self, cache_key: str) -> Optional[Dataset]:
        """
        Load dataset from cache.
        
        Args:
            cache_key: Cache key used during caching
            
        Returns:
            Cached dataset or None if not found
        """
        cache_file = self.cache_path / f"{cache_key}.pkl"
        
        if not cache_file.exists():
            self.logger.warning(f"Cache file not found: {cache_file}")
            return None
        
        self.logger.info(f"Loading dataset from cache: {cache_key}")
        
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load cached dataset: {str(e)}")
            return None
    
    def clear_cache(self):
        """Clear all cached files."""
        self.logger.info("Clearing cache directory")
        
        for cache_file in self.cache_path.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                self.logger.warning(f"Could not delete cache file {cache_file}: {str(e)}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "total_memory_gb": memory.total / (1024**3),
                "available_memory_gb": memory.available / (1024**3),
                "used_memory_gb": memory.used / (1024**3),
                "memory_usage_percent": memory.percent,
                "process_memory_mb": self._get_memory_usage() / (1024**2)
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def suggest_chunk_size(self, dataset: Dataset) -> int:
        """
        Suggest optimal chunk size for processing.
        
        Args:
            dataset: Dataset to analyze
            
        Returns:
            Suggested chunk size
        """
        # Get memory statistics
        memory_stats = self.get_memory_stats()
        
        if "error" in memory_stats:
            # Fallback to default
            return self.chunk_size
        
        available_memory_mb = memory_stats["available_memory_gb"] * 1024
        process_memory_mb = memory_stats["process_memory_mb"]
        
        # Estimate dataset memory usage
        dataset_memory_mb = dataset.nbytes / (1024 * 1024)
        
        # Calculate safe chunk size
        # Use 10% of available memory or 25% of the difference between available and current
        safe_memory = min(
            available_memory_mb * 0.1,
            (available_memory_mb - process_memory_mb) * 0.25
        )
        
        if dataset_memory_mb > 0:
            chunk_size = int((len(dataset) * safe_memory) / dataset_memory_mb)
            chunk_size = max(1000, min(chunk_size, 50000))  # Clamp between 1K and 50K
        else:
            chunk_size = 10000
        
        self.logger.info(f"Suggested chunk size: {chunk_size}")
        return chunk_size