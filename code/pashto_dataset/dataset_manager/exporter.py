"""
Dataset Exporter
================

Handles exporting datasets in various formats and uploading to Hugging Face Hub.
"""

import json
import logging
import shutil
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
from datasets import Dataset, DatasetDict
import yaml

try:
    from huggingface_hub import HfApi, Repository
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logging.warning("HuggingFace Hub not available. Install with: pip install huggingface_hub")

from .config import DatasetConfig, get_hf_token


class DatasetExporter:
    """Exports datasets in various formats."""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.exports_path = self.config.exports_path
        self.logger = logging.getLogger(f"DatasetExporter[{config.dataset_name}]")
        
        if HF_AVAILABLE:
            self.hf_api = HfApi()
            self.token = get_hf_token()
            if self.token:
                self.hf_api.login(token=self.token)
        else:
            self.hf_api = None
    
    def export_dataset(self, dataset: Dataset, format: str, 
                      output_path: Optional[Path] = None,
                      **kwargs) -> Path:
        """
        Export a single dataset in specified format.
        
        Args:
            dataset: Dataset to export
            format: Export format (json, csv, parquet, conll, txt)
            output_path: Optional output path
            **kwargs: Additional export parameters
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.exports_path / f"dataset_{format}"
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            return self._export_json(dataset, output_path, **kwargs)
        elif format == "jsonl":
            return self._export_jsonl(dataset, output_path, **kwargs)
        elif format == "csv":
            return self._export_csv(dataset, output_path, **kwargs)
        elif format == "parquet":
            return self._export_parquet(dataset, output_path, **kwargs)
        elif format == "conll":
            return self._export_conll(dataset, output_path, **kwargs)
        elif format == "txt":
            return self._export_txt(dataset, output_path, **kwargs)
        elif format == "hf_dataset":
            return self._export_hf_dataset(dataset, output_path, **kwargs)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def export_dataset_dict(self, dataset_dict: DatasetDict, format: str,
                           output_path: Optional[Path] = None,
                           **kwargs) -> Path:
        """
        Export a dataset dictionary (splits) in specified format.
        
        Args:
            dataset_dict: DatasetDict to export
            format: Export format
            output_path: Optional output path
            **kwargs: Additional export parameters
            
        Returns:
            Path to exported directory
        """
        if output_path is None:
            output_path = self.exports_path / f"dataset_dict_{format}"
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            return self._export_dataset_dict_json(dataset_dict, output_path, **kwargs)
        elif format == "jsonl":
            return self._export_dataset_dict_jsonl(dataset_dict, output_path, **kwargs)
        elif format == "csv":
            return self._export_dataset_dict_csv(dataset_dict, output_path, **kwargs)
        elif format == "parquet":
            return self._export_dataset_dict_parquet(dataset_dict, output_path, **kwargs)
        elif format == "conll":
            return self._export_dataset_dict_conll(dataset_dict, output_path, **kwargs)
        elif format == "hf_dataset":
            return self._export_hf_dataset_dict(dataset_dict, output_path, **kwargs)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, dataset: Dataset, output_path: Path, **kwargs) -> Path:
        """Export to JSON format."""
        output_file = output_path / "dataset.json"
        
        # Convert to dict and save
        data_dict = dataset.to_dict()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Dataset exported to JSON: {output_file}")
        return output_file
    
    def _export_jsonl(self, dataset: Dataset, output_path: Path, **kwargs) -> Path:
        """Export to JSONL format."""
        output_file = output_path / "dataset.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in dataset:
                json.dump(item, f, ensure_ascii=False)
                f.write('\n')
        
        self.logger.info(f"Dataset exported to JSONL: {output_file}")
        return output_file
    
    def _export_csv(self, dataset: Dataset, output_path: Path, **kwargs) -> Path:
        """Export to CSV format."""
        output_file = output_path / "dataset.csv"
        
        # Convert to DataFrame and save
        df = dataset.to_pandas()
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        self.logger.info(f"Dataset exported to CSV: {output_file}")
        return output_file
    
    def _export_parquet(self, dataset: Dataset, output_path: Path, **kwargs) -> Path:
        """Export to Parquet format."""
        output_file = output_path / "dataset.parquet"
        
        # Convert to DataFrame and save
        df = dataset.to_pandas()
        df.to_parquet(output_file, index=False)
        
        self.logger.info(f"Dataset exported to Parquet: {output_file}")
        return output_file
    
    def _export_conll(self, dataset: Dataset, output_path: Path, **kwargs) -> Path:
        """Export to CoNLL format for NLP tasks."""
        output_file = output_path / "dataset.conll"
        
        # Determine format based on columns
        columns = dataset.column_names
        
        if 'text' in columns and 'labels' in columns:
            # Named Entity Recognition format
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in dataset:
                    tokens = str(item['text']).split()
                    labels = item['labels'] if isinstance(item['labels'], list) else [item['labels']]
                    
                    for token, label in zip(tokens, labels):
                        f.write(f"{token} {label}\n")
                    f.write("\n")
        
        elif 'text' in columns and 'pos_tags' in columns:
            # Part-of-speech tagging format
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in dataset:
                    tokens = str(item['text']).split()
                    pos_tags = item['pos_tags'] if isinstance(item['pos_tags'], list) else [item['pos_tags']]
                    
                    for token, pos_tag in zip(tokens, pos_tags):
                        f.write(f"{token} {pos_tag}\n")
                    f.write("\n")
        
        else:
            # Simple text format
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in dataset:
                    if 'text' in item:
                        f.write(f"{item['text']}\n")
                    else:
                        f.write(f"{str(item)}\n")
        
        self.logger.info(f"Dataset exported to CoNLL: {output_file}")
        return output_file
    
    def _export_txt(self, dataset: Dataset, output_path: Path, **kwargs) -> Path:
        """Export to plain text format."""
        output_file = output_path / "dataset.txt"
        
        text_column = kwargs.get('text_column', 'text')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in dataset:
                if text_column in item:
                    f.write(f"{item[text_column]}\n")
                else:
                    f.write(f"{str(item)}\n")
        
        self.logger.info(f"Dataset exported to TXT: {output_file}")
        return output_file
    
    def _export_hf_dataset(self, dataset: Dataset, output_path: Path, **kwargs) -> Path:
        """Export as Hugging Face dataset format."""
        # Save using Hugging Face's format
        dataset.save_to_disk(str(output_path))
        
        self.logger.info(f"Dataset exported in HF format: {output_path}")
        return output_path
    
    def _export_dataset_dict_json(self, dataset_dict: DatasetDict, output_path: Path, **kwargs) -> Path:
        """Export DatasetDict as JSON files."""
        output_path = output_path / "json"
        output_path.mkdir(exist_ok=True)
        
        for split_name, split_dataset in dataset_dict.items():
            split_file = output_path / f"{split_name}.json"
            data_dict = split_dataset.to_dict()
            
            with open(split_file, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"DatasetDict exported to JSON: {output_path}")
        return output_path
    
    def _export_dataset_dict_jsonl(self, dataset_dict: DatasetDict, output_path: Path, **kwargs) -> Path:
        """Export DatasetDict as JSONL files."""
        output_path = output_path / "jsonl"
        output_path.mkdir(exist_ok=True)
        
        for split_name, split_dataset in dataset_dict.items():
            split_file = output_path / f"{split_name}.jsonl"
            
            with open(split_file, 'w', encoding='utf-8') as f:
                for item in split_dataset:
                    json.dump(item, f, ensure_ascii=False)
                    f.write('\n')
        
        self.logger.info(f"DatasetDict exported to JSONL: {output_path}")
        return output_path
    
    def _export_dataset_dict_csv(self, dataset_dict: DatasetDict, output_path: Path, **kwargs) -> Path:
        """Export DatasetDict as CSV files."""
        output_path = output_path / "csv"
        output_path.mkdir(exist_ok=True)
        
        for split_name, split_dataset in dataset_dict.items():
            split_file = output_path / f"{split_name}.csv"
            df = split_dataset.to_pandas()
            df.to_csv(split_file, index=False, encoding='utf-8')
        
        self.logger.info(f"DatasetDict exported to CSV: {output_path}")
        return output_path
    
    def _export_dataset_dict_parquet(self, dataset_dict: DatasetDict, output_path: Path, **kwargs) -> Path:
        """Export DatasetDict as Parquet files."""
        output_path = output_path / "parquet"
        output_path.mkdir(exist_ok=True)
        
        for split_name, split_dataset in dataset_dict.items():
            split_file = output_path / f"{split_name}.parquet"
            df = split_dataset.to_pandas()
            df.to_parquet(split_file, index=False)
        
        self.logger.info(f"DatasetDict exported to Parquet: {output_path}")
        return output_path
    
    def _export_dataset_dict_conll(self, dataset_dict: DatasetDict, output_path: Path, **kwargs) -> Path:
        """Export DatasetDict as CoNLL files."""
        output_path = output_path / "conll"
        output_path.mkdir(exist_ok=True)
        
        for split_name, split_dataset in dataset_dict.items():
            split_file = output_path / f"{split_name}.conll"
            
            with open(split_file, 'w', encoding='utf-8') as f:
                for item in split_dataset:
                    if 'text' in item and 'labels' in item:
                        tokens = str(item['text']).split()
                        labels = item['labels'] if isinstance(item['labels'], list) else [item['labels']]
                        
                        for token, label in zip(tokens, labels):
                            f.write(f"{token} {label}\n")
                        f.write("\n")
        
        self.logger.info(f"DatasetDict exported to CoNLL: {output_path}")
        return output_path
    
    def _export_hf_dataset_dict(self, dataset_dict: DatasetDict, output_path: Path, **kwargs) -> Path:
        """Export DatasetDict in Hugging Face format."""
        # Save each split
        for split_name, split_dataset in dataset_dict.items():
            split_path = output_path / split_name
            split_dataset.save_to_disk(str(split_path))
        
        # Save dataset dict
        dataset_dict.save_to_disk(str(output_path))
        
        self.logger.info(f"DatasetDict exported in HF format: {output_path}")
        return output_path
    
    def upload_to_hub(self, dataset: Dataset, version: str = "latest",
                     commit_message: Optional[str] = None) -> str:
        """
        Upload dataset to Hugging Face Hub.
        
        Args:
            dataset: Dataset to upload
            version: Version to upload
            commit_message: Commit message
            
        Returns:
            Repository URL
        """
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace Hub not available. Install with: pip install huggingface_hub")
        
        if not self.config.repo_id:
            raise ValueError("Repository ID not configured. Set config.repo_id to upload to Hub.")
        
        self.logger.info(f"Uploading dataset to Hugging Face Hub: {self.config.repo_id}")
        
        try:
            # Create or get repository
            repo_url = self.hf_api.create_repo(
                repo_id=self.config.repo_id,
                repo_type="dataset",
                exist_ok=True,
                private=self.config.private
            )
            
            # Save dataset temporarily
            temp_dir = Path("temp_upload")
            temp_dir.mkdir(exist_ok=True)
            dataset.save_to_disk(str(temp_dir))
            
            # Upload to hub
            self.hf_api.upload_folder(
                folder_path=str(temp_dir),
                repo_id=self.config.repo_id,
                commit_message=commit_message or f"Upload dataset version {version}",
                repo_type="dataset"
            )
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            repository_url = f"https://huggingface.co/datasets/{self.config.repo_id}"
            self.logger.info(f"Dataset uploaded successfully: {repository_url}")
            
            return repository_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload to Hub: {str(e)}")
            raise
    
    def repository_exists(self) -> bool:
        """Check if repository exists on Hugging Face Hub."""
        if not HF_AVAILABLE or not self.config.repo_id:
            return False
        
        try:
            self.hf_api.dataset_info(self.config.repo_id)
            return True
        except:
            return False
    
    def create_repository(self) -> str:
        """Create repository on Hugging Face Hub."""
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace Hub not available. Install with: pip install huggingface_hub")
        
        if not self.config.repo_id:
            raise ValueError("Repository ID not configured. Set config.repo_id to create repository.")
        
        repo_url = self.hf_api.create_repo(
            repo_id=self.config.repo_id,
            repo_type="dataset",
            exist_ok=True,
            private=self.config.private
        )
        
        return repo_url
    
    def create_dataset_card(self, metadata: Dict[str, Any]) -> str:
        """Create a dataset card (README.md) for the repository."""
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace Hub not available. Install with: pip install huggingface_hub")
        
        # Basic dataset card content
        card_content = f"""---
{language: {self.config.language or "und"}
license: {self.config.license}
size_categories: {self._get_size_category(metadata.get("num_samples", 0))}
task_categories: []
task_ids: []
pretty_name: {self.config.dataset_name}
---

# {self.config.dataset_name}

{self.config.dataset_description}

## Dataset Description

- **Curated by:** Dataset Contributors
- **Language(s):** {self.config.language or "und"}
- **License:** {self.config.license}
- **Size:** {metadata.get("num_samples", 0):,} samples

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{self.config.repo_id}")
```

## Citation

```
@dataset{{{self.config.dataset_name.lower().replace(" ", "_")},
  title={{{self.config.dataset_name}}},
  author={{Dataset Contributors}},
  year={{{metadata.get("created_at", "2023").split("-")[0]}}},
  url={{"https://huggingface.co/datasets/{self.config.repo_id}"}}
}}
```
"""
        
        return card_content
    
    def _get_size_category(self, num_samples: int) -> str:
        """Get appropriate size category for dataset card."""
        if num_samples < 1000:
            return "n_<1K"
        elif num_samples < 10000:
            return "1K<n<10K"
        elif num_samples < 100000:
            return "10K<n<100K"
        elif num_samples < 1000000:
            return "100K<n<1M"
        else:
            return "n_>1M"
    
    def export_metadata_yaml(self, output_path: Path, metadata: Dict[str, Any]):
        """Export metadata as YAML file."""
        output_file = output_path / "metadata.yaml"
        
        # Prepare metadata for YAML
        yaml_metadata = {
            "dataset_name": self.config.dataset_name,
            "description": self.config.dataset_description,
            "version": self.config.version,
            "language": self.config.language,
            "license": self.config.license,
            "size": metadata.get("num_samples", 0),
            "features": len(metadata.get("columns", [])),
            "created_at": metadata.get("created_at", ""),
            "last_updated": metadata.get("updated_at", "")
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_metadata, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.info(f"Metadata exported to YAML: {output_file}")
        return output_file
    
    def create_license_file(self, output_path: Path):
        """Create license file for the dataset."""
        output_file = output_path / "LICENSE"
        
        # Simple license template
        license_text = f"""MIT License

Copyright (c) 2023 Dataset Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(license_text)
        
        self.logger.info(f"License file created: {output_file}")
        return output_file
    
    def batch_export_formats(self, dataset: Dataset, formats: List[str],
                           output_base: Optional[Path] = None) -> Dict[str, Path]:
        """
        Export dataset in multiple formats at once.
        
        Args:
            dataset: Dataset to export
            formats: List of formats to export
            output_base: Base output directory
            
        Returns:
            Dictionary mapping format to output path
        """
        if output_base is None:
            output_base = self.exports_path / "batch_export"
        
        output_base.mkdir(parents=True, exist_ok=True)
        
        results = {}
        for format_name in formats:
            try:
                format_path = output_base / format_name
                results[format_name] = self.export_dataset(dataset, format_name, format_path)
                self.logger.info(f"Exported {format_name} format successfully")
            except Exception as e:
                self.logger.error(f"Failed to export {format_name} format: {str(e)}")
                results[format_name] = None
        
        return results
    
    def validate_export(self, exported_path: Path) -> Dict[str, Any]:
        """Validate exported dataset."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        # Check if path exists
        if not exported_path.exists():
            validation_results["valid"] = False
            validation_results["errors"].append(f"Exported path does not exist: {exported_path}")
            return validation_results
        
        # Check if it's a file or directory
        if exported_path.is_file():
            # Single file format
            validation_results["info"]["type"] = "file"
            validation_results["info"]["size_mb"] = exported_path.stat().st_size / (1024 * 1024)
        else:
            # Directory format
            validation_results["info"]["type"] = "directory"
            files = list(exported_path.glob("*"))
            validation_results["info"]["file_count"] = len(files)
            validation_results["info"]["total_size_mb"] = sum(
                f.stat().st_size for f in files if f.is_file()
            ) / (1024 * 1024)
        
        return validation_results