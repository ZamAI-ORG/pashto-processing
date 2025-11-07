"""
Metadata Manager
===============

Handles dataset metadata management and documentation generation.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import pandas as pd
from datasets import Dataset

from .config import DatasetConfig


class MetadataManager:
    """Manages dataset metadata and documentation."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.metadata_path = self.config.metadata_path
        self.logger = logging.getLogger(f"MetadataManager[{config.dataset_name}]")
    
    def initialize_metadata(self, dataset: Dataset):
        """Initialize metadata for a new dataset."""
        self.logger.info("Initializing dataset metadata")
        
        metadata = {
            "dataset_name": self.config.dataset_name,
            "description": self.config.dataset_description,
            "version": self.config.version,
            "license": self.config.license,
            "language": self.config.language,
            "created_at": datetime.now().isoformat(),
            "num_samples": len(dataset),
            "columns": list(dataset.column_names),
            "features": dataset.features.to_dict(),
            "size_mb": dataset.dataset_size / (1024 * 1024),
            "memory_usage_mb": dataset.nbytes / (1024 * 1024)
        }
        
        # Save initial metadata
        self.save_metadata("init", metadata)
        
        self.logger.info("Metadata initialized")
    
    def update_metadata(self, dataset: Dataset, version: str):
        """Update metadata for a dataset version."""
        self.logger.info(f"Updating metadata for version: {version}")
        
        # Load existing metadata if available
        existing_metadata = self.get_metadata(version)
        if not existing_metadata:
            existing_metadata = {}
        
        # Update with current information
        metadata = {
            **existing_metadata,  # Keep existing data
            "updated_at": datetime.now().isoformat(),
            "num_samples": len(dataset),
            "columns": list(dataset.column_names),
            "features": dataset.features.to_dict(),
            "size_mb": dataset.dataset_size / (1024 * 1024),
            "memory_usage_mb": dataset.nbytes / (1024 * 1024)
        }
        
        # Save updated metadata
        self.save_metadata(version, metadata)
        
        self.logger.info("Metadata updated")
    
    def save_metadata(self, version: str, metadata: Dict[str, Any]):
        """Save metadata to file."""
        version_file = self.metadata_path / f"metadata_{version}.json"
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Update index file
        self._update_metadata_index(version, metadata)
    
    def get_metadata(self, version: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific version."""
        version_file = self.metadata_path / f"metadata_{version}.json"
        
        if not version_file.exists():
            return None
        
        with open(version_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_all_versions(self) -> List[Dict[str, Any]]:
        """List all dataset versions with their metadata."""
        metadata_files = list(self.metadata_path.glob("metadata_*.json"))
        versions = []
        
        for file_path in metadata_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                versions.append(metadata)
            except Exception as e:
                self.logger.warning(f"Could not read metadata file {file_path}: {e}")
        
        return sorted(versions, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def save_quality_metrics(self, version: str, metrics: Dict[str, Any]):
        """Save quality metrics for a version."""
        metrics_file = self.metadata_path / f"quality_metrics_{version}.json"
        
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    def get_quality_metrics(self, version: str) -> Optional[Dict[str, Any]]:
        """Get quality metrics for a version."""
        metrics_file = self.metadata_path / f"quality_metrics_{version}.json"
        
        if not metrics_file.exists():
            return None
        
        with open(metrics_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_splits(self, dataset_dict: "DatasetDict", 
                     ratios: Dict[str, float], 
                     strategy: str, 
                     stratified_column: Optional[str] = None):
        """Update metadata with split information."""
        self.logger.info("Updating split information")
        
        # Calculate split information
        split_info = {
            "strategy": strategy,
            "ratios": ratios,
            "stratified_column": stratified_column,
            "splits": {
                split_name: {
                    "num_samples": len(split_dataset),
                    "ratio": ratios[split_name],
                    "percentage": (len(split_dataset) / sum(len(s) for s in dataset_dict.values())) * 100
                }
                for split_name, split_dataset in dataset_dict.items()
            },
            "total_samples": sum(len(split_dataset) for split_dataset in dataset_dict.values())
        }
        
        # Get current version or use "current"
        version = getattr(dataset_dict, '_version', 'current')
        
        # Save split information
        splits_file = self.metadata_path / f"splits_{version}.json"
        with open(splits_file, 'w', encoding='utf-8') as f:
            json.dump(split_info, f, indent=2, ensure_ascii=False)
    
    def _update_metadata_index(self, version: str, metadata: Dict[str, Any]):
        """Update the metadata index file."""
        index_file = self.metadata_path / "metadata_index.json"
        
        # Load existing index
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"versions": []}
        
        # Update or add version
        existing_entry = None
        for entry in index["versions"]:
            if entry["version"] == version:
                existing_entry = entry
                break
        
        if existing_entry:
            existing_entry.update({
                "num_samples": metadata.get("num_samples"),
                "size_mb": metadata.get("size_mb"),
                "updated_at": metadata.get("updated_at")
            })
        else:
            index["versions"].append({
                "version": version,
                "num_samples": metadata.get("num_samples"),
                "size_mb": metadata.get("size_mb"),
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at")
            })
        
        # Save index
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def generate_dataset_card(self, config: DatasetConfig, 
                            num_samples: int, 
                            metrics: Dict[str, Any],
                            metadata: Optional[Dict] = None) -> str:
        """
        Generate a comprehensive dataset card (README.md).
        
        Args:
            config: Dataset configuration
            num_samples: Number of samples
            metrics: Quality metrics
            metadata: Additional metadata
            
        Returns:
            Dataset card content as string
        """
        self.logger.info("Generating dataset card")
        
        # Start building the dataset card
        lines = []
        
        # Title
        lines.append(f"# {config.dataset_name}")
        lines.append("")
        
        # Description
        lines.append("## Dataset Description")
        lines.append("")
        lines.append(config.dataset_description)
        lines.append("")
        
        # Basic information
        lines.append("### Basic Information")
        lines.append("")
        lines.append(f"- **Name**: {config.dataset_name}")
        lines.append(f"- **Version**: {config.version}")
        lines.append(f"- **License**: {config.license}")
        lines.append(f"- **Language**: {config.language}")
        lines.append(f"- **Samples**: {num_samples:,}")
        
        if config.repo_id:
            lines.append(f"- **Repository**: https://huggingface.co/datasets/{config.repo_id}")
        
        lines.append("")
        
        # Usage
        lines.append("## Usage")
        lines.append("")
        lines.append("```python")
        lines.append("from datasets import load_dataset")
        lines.append("")
        if config.repo_id:
            lines.append(f"dataset = load_dataset('{config.repo_id}')")
        else:
            lines.append("dataset = load_dataset('path/to/dataset')")
        lines.append("```")
        lines.append("")
        
        # Dataset structure
        lines.append("## Dataset Structure")
        lines.append("")
        lines.append("### Data Instances")
        lines.append("Each example in the dataset contains:")
        
        if metadata and 'columns' in metadata:
            for col in metadata['columns']:
                lines.append(f"- **{col}**: Sample data")
        
        lines.append("")
        
        # Quality metrics
        if metrics:
            lines.append("## Quality Metrics")
            lines.append("")
            
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, float):
                    lines.append(f"- **{metric_name}**: {metric_value:.3f}")
                else:
                    lines.append(f"- **{metric_name}**: {metric_value}")
            lines.append("")
        
        # Citing
        lines.append("## Citation")
        lines.append("")
        if metadata and 'created_at' in metadata:
            lines.append(f"Created: {metadata['created_at']}")
        lines.append("")
        lines.append("Please cite this dataset as:")
        lines.append("")
        lines.append("```")
        citation = f"@dataset{{{config.dataset_name.lower().replace(' ', '_')},"
        if metadata and 'created_at' in metadata:
            citation += f"\n  title={{{config.dataset_name}}}," 
            citation += f"\n  author={{Dataset Contributors}},"
            citation += f"\n  year={{{metadata['created_at'][:4]}}}," 
        citation += "\n}"
        lines.append(citation)
        lines.append("```")
        lines.append("")
        
        # Contributing
        lines.append("## Contributing")
        lines.append("")
        lines.append("Contributions to improve this dataset are welcome!")
        lines.append("")
        
        # License
        lines.append("## License")
        lines.append("")
        lines.append(f"This dataset is available under the {config.license} license.")
        lines.append("")
        
        return "\n".join(lines)
    
    def export_metadata_report(self, output_path: Path):
        """Export a comprehensive metadata report."""
        self.logger.info("Exporting metadata report")
        
        # Collect all information
        versions = self.list_all_versions()
        latest_metadata = versions[0] if versions else {}
        
        report = {
            "dataset_info": {
                "name": self.config.dataset_name,
                "description": self.config.dataset_description,
                "version": self.config.version,
                "license": self.config.license,
                "language": self.config.language
            },
            "versions": versions,
            "latest_metrics": self.get_quality_metrics(latest_metadata.get("version", "latest")),
            "exported_at": datetime.now().isoformat()
        }
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Metadata report exported to: {output_path}")
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate metadata structure and content."""
        errors = []
        
        # Required fields
        required_fields = [
            "dataset_name", "description", "version", "license", 
            "language", "num_samples", "columns", "features"
        ]
        
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")
        
        # Validate specific fields
        if "num_samples" in metadata and not isinstance(metadata["num_samples"], int):
            errors.append("num_samples must be an integer")
        
        if "columns" in metadata and not isinstance(metadata["columns"], list):
            errors.append("columns must be a list")
        
        if "features" in metadata and not isinstance(metadata["features"], dict):
            errors.append("features must be a dictionary")
        
        return errors