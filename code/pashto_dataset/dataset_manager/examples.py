"""
Example Usage of Dataset Management System
==========================================

This file demonstrates how to use the complete Hugging Face dataset 
management system for creating, managing, and maintaining datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging

# Import the dataset management system
from .dataset_manager import DatasetManager
from .config import DatasetConfig


def create_sample_dataset():
    """Create a sample dataset for demonstration."""
    print("Creating sample Pashto dataset...")
    
    # Create sample data
    data = {
        "text": [
            "زه یو طالب یم چې زده کړه غواړم",
            "دغه کتاب ښه دی او ډېر ګټور معلومات لري",
            "موږ باید د کورونو صفایي وکړو",
            "دا سیمه ډېر ښه او عالي ځای دی",
            "زموږ د کورنۍ غړي ډېر مینه والا دي"
        ] * 20,  # Repeat to make dataset larger
        "label": ["education", "book", "house", "place", "family"] * 20,
        "sentiment": ["positive", "positive", "neutral", "positive", "positive"] * 20,
        "source": ["manual", "web", "manual", "manual", "manual"] * 20,
        "length": [15, 25, 18, 22, 28] * 20
    }
    
    return pd.DataFrame(data)


def basic_usage_example():
    """Basic usage of the dataset management system."""
    print("\n" + "="*50)
    print("BASIC USAGE EXAMPLE")
    print("="*50)
    
    # Create a custom configuration
    config = DatasetConfig(
        dataset_name="pashto_corpus_example",
        dataset_description="Example Pashto language dataset",
        version="1.0.0",
        language="pas",
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15
    )
    
    # Initialize the dataset manager
    manager = DatasetManager(config)
    
    # Create sample dataset
    sample_data = create_sample_dataset()
    
    # Create dataset
    dataset = manager.create_dataset(sample_data, validate_data=True)
    print(f"Created dataset with {len(dataset)} samples")
    
    # Save dataset
    version = manager.save_dataset("v1.0.0")
    print(f"Saved dataset as version: {version}")
    
    # Get dataset information
    info = manager.get_dataset_info()
    print(f"Dataset info: {json.dumps(info, indent=2)}")
    
    return manager, dataset


def advanced_features_example(manager, dataset):
    """Demonstrate advanced features."""
    print("\n" + "="*50)
    print("ADVANCED FEATURES EXAMPLE")
    print("="*50)
    
    # Validate dataset
    print("Validating dataset...")
    validation_results = manager.validate_dataset()
    print(f"Validation status: {validation_results['overall_status']}")
    
    # Calculate quality metrics
    print("Calculating quality metrics...")
    metrics = manager.calculate_quality_metrics()
    print(f"Dataset quality score: {metrics.get('overall_completeness', 0):.2%}")
    
    # Split dataset
    print("Splitting dataset...")
    dataset_dict = manager.split_dataset(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        strategy="stratified",
        stratified_column="label"
    )
    
    print(f"Split sizes: { {name: len(split) for name, split in dataset_dict.items()} }")
    
    return dataset_dict


def export_example(manager, dataset_dict):
    """Demonstrate export capabilities."""
    print("\n" + "="*50)
    print("EXPORT EXAMPLE")
    print("="*50)
    
    # Export in multiple formats
    formats = ["json", "csv", "parquet", "hf_dataset"]
    
    for fmt in formats:
        print(f"Exporting in {fmt} format...")
        output_path = manager.export_dataset(fmt)
        print(f"Exported to: {output_path}")


def memory_optimization_example():
    """Demonstrate memory optimization features."""
    print("\n" + "="*50)
    print("MEMORY OPTIMIZATION EXAMPLE")
    print("="*50)
    
    # Create a large dataset for demonstration
    print("Creating large sample dataset...")
    large_data = {
        "text": [f"样本文本 {i}" for i in range(10000)],
        "label": [f"label_{i % 5}" for i in range(10000)],
        "number": list(range(10000)),
        "float_data": [float(i) / 100 for i in range(10000)]
    }
    
    from datasets import Dataset
    large_dataset = Dataset.from_dict(large_data)
    
    # Initialize optimizer
    from .memory_optimizer import MemoryOptimizer
    config = DatasetConfig()
    optimizer = MemoryOptimizer(config)
    
    # Analyze memory usage
    print("Analyzing memory usage...")
    analysis = optimizer.analyze_memory_usage(large_dataset)
    print(f"Estimated memory usage: {analysis['estimated_memory_mb']:.1f} MB")
    print(f"Recommendations: {analysis['recommendations']}")
    
    # Optimize dataset
    print("Optimizing dataset...")
    optimized_dataset = optimizer.optimize_dataset(large_dataset)
    print("Optimization completed")


def version_management_example():
    """Demonstrate version management features."""
    print("\n" + "="*50)
    print("VERSION MANAGEMENT EXAMPLE")
    print("="*50)
    
    config = DatasetConfig(
        dataset_name="versioned_dataset",
        version="1.0.0"
    )
    
    from .versioning import DatasetVersioning
    versioning = DatasetVersioning(config)
    
    # Create multiple versions
    versions = []
    for i in range(3):
        version_str = versioning.generate_version(patch=i)
        versions.append(version_str)
        print(f"Generated version: {version_str}")
    
    # List all versions
    all_versions = versioning.list_all_versions()
    print(f"Available versions: {all_versions}")
    
    return versions


def metadata_management_example(manager, dataset):
    """Demonstrate metadata management features."""
    print("\n" + "="*50)
    print("METADATA MANAGEMENT EXAMPLE")
    print("="*50)
    
    # Update metadata
    manager.metadata_manager.update_metadata(dataset, "v1.0.0")
    
    # Generate dataset card
    config = manager.config
    metrics = manager.calculate_quality_metrics()
    
    card_content = manager.metadata_manager.generate_dataset_card(
        config, 
        len(dataset), 
        metrics, 
        manager.metadata_manager.get_metadata("v1.0.0")
    )
    
    print("Generated dataset card (first 200 characters):")
    print(card_content[:200] + "...")
    
    # Export metadata report
    report_path = manager.config.metadata_path / "metadata_report.json"
    manager.metadata_manager.export_metadata_report(report_path)
    print(f"Metadata report exported to: {report_path}")


def full_workflow_example():
    """Complete workflow example."""
    print("\n" + "="*60)
    print("COMPLETE WORKFLOW EXAMPLE")
    print("="*60)
    
    # Step 1: Setup configuration
    print("Step 1: Setting up configuration...")
    config = DatasetConfig(
        dataset_name="pashto_complete_workflow",
        dataset_description="Complete workflow demonstration",
        language="pas",
        train_ratio=0.8,
        val_ratio=0.1,
        test_ratio=0.1
    )
    
    # Step 2: Initialize manager
    print("Step 2: Initializing dataset manager...")
    manager = DatasetManager(config)
    
    # Step 3: Create dataset
    print("Step 3: Creating dataset...")
    sample_data = create_sample_dataset()
    dataset = manager.create_dataset(sample_data, validate_data=True)
    
    # Step 4: Calculate quality metrics
    print("Step 4: Calculating quality metrics...")
    metrics = manager.calculate_quality_metrics()
    print(f"Quality metrics calculated: {len(metrics)} metrics")
    
    # Step 5: Save dataset
    print("Step 5: Saving dataset...")
    version = manager.save_dataset("v1.0.0")
    print(f"Dataset saved as: {version}")
    
    # Step 6: Split dataset
    print("Step 6: Splitting dataset...")
    dataset_dict = manager.split_dataset(strategy="stratified", stratified_column="label")
    split_sizes = {name: len(split) for name, split in dataset_dict.items()}
    print(f"Dataset splits: {split_sizes}")
    
    # Step 7: Export dataset
    print("Step 7: Exporting dataset...")
    for fmt in ["json", "csv"]:
        output_path = manager.export_dataset(fmt)
        print(f"Exported {fmt}: {output_path}")
    
    # Step 8: Generate documentation
    print("Step 8: Generating documentation...")
    card_path = manager.config.get_dataset_card_path()
    if card_path.exists():
        print(f"Dataset card created: {card_path}")
    
    print("\nComplete workflow finished successfully!")
    print(f"Dataset contains {len(dataset)} samples in {len(dataset.column_names)} columns")
    print(f"Available splits: {list(dataset_dict.keys())}")
    print(f"Exported formats: json, csv, parquet, hf_dataset")
    
    return manager, dataset, dataset_dict


def performance_comparison_example():
    """Compare performance with and without optimization."""
    print("\n" + "="*50)
    print("PERFORMANCE COMPARISON EXAMPLE")
    print("="*50)
    
    import time
    from .memory_optimizer import MemoryOptimizer
    from .config import DatasetConfig
    
    # Create large dataset
    print("Creating large dataset...")
    large_data = {
        "text": [f"متن {i} " * 50 for i in range(5000)],
        "label": [f"class_{i % 10}" for i in range(5000)],
        "number": list(range(5000))
    }
    
    from datasets import Dataset
    large_dataset = Dataset.from_dict(large_data)
    
    config = DatasetConfig()
    optimizer = MemoryOptimizer(config)
    
    # Test without optimization
    print("Testing without optimization...")
    start_time = time.time()
    original_size = large_dataset.nbytes / (1024 * 1024)
    original_time = time.time() - start_time
    
    # Test with optimization
    print("Testing with optimization...")
    start_time = time.time()
    optimized_dataset = optimizer.optimize_dataset(large_dataset)
    optimized_size = optimized_dataset.nbytes / (1024 * 1024)
    optimized_time = time.time() - start_time
    
    print(f"Original size: {original_size:.1f} MB")
    print(f"Optimized size: {optimized_size:.1f} MB")
    print(f"Size reduction: {(1 - optimized_size/original_size)*100:.1f}%")
    print(f"Optimization time: {optimized_time:.2f} seconds")


def main():
    """Run all examples."""
    print("HUGGING FACE DATASET MANAGEMENT SYSTEM")
    print("="*50)
    print("This example demonstrates the complete dataset management system.")
    
    # Basic usage
    manager, dataset = basic_usage_example()
    
    # Advanced features
    dataset_dict = advanced_features_example(manager, dataset)
    
    # Export capabilities
    export_example(manager, dataset_dict)
    
    # Memory optimization
    memory_optimization_example()
    
    # Version management
    versions = version_management_example()
    
    # Metadata management
    metadata_management_example(manager, dataset)
    
    # Complete workflow
    final_manager, final_dataset, final_splits = full_workflow_example()
    
    # Performance comparison
    performance_comparison_example()
    
    print("\n" + "="*50)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("\nThe dataset management system provides:")
    print("- Complete dataset lifecycle management")
    print("- Advanced splitting and validation")
    print("- Memory optimization for large datasets")
    print("- Multiple export formats")
    print("- Version control and metadata management")
    print("- Quality metrics and documentation generation")
    print("- Hugging Face Hub integration")


if __name__ == "__main__":
    main()