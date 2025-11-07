"""
Hugging Face Dataset Management System
=====================================

A comprehensive system for creating, managing, and maintaining datasets
with full Hugging Face integration.
"""

from .dataset_manager import DatasetManager
from .dataset_creator import DatasetCreator
from .metadata_manager import MetadataManager
from .versioning import DatasetVersioning
from .splitter import DatasetSplitter
from .validator import DatasetValidator
from .quality_metrics import QualityMetrics
from .exporter import DatasetExporter
from .memory_optimizer import MemoryOptimizer
from .config import DatasetConfig

__version__ = "1.0.0"
__author__ = "Dataset Management System"

__all__ = [
    "DatasetManager",
    "DatasetCreator", 
    "MetadataManager",
    "DatasetVersioning",
    "DatasetSplitter",
    "DatasetValidator",
    "QualityMetrics",
    "DatasetExporter",
    "MemoryOptimizer",
    "DatasetConfig"
]