"""
Configuration module for Dataset Management System
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatasetConfig:
    """Configuration class for dataset management."""
    
    # Basic dataset information
    dataset_name: str = "pashto_dataset"
    dataset_description: str = "A comprehensive Pashto language dataset"
    version: str = "1.0.0"
    license: str = "CC BY 4.0"
    language: str = "pas"
    
    # Hugging Face specific
    repo_id: Optional[str] = None
    token: Optional[str] = None
    private: bool = False
    
    # Directory paths
    base_dir: str = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: str = "data"
    metadata_dir: str = "metadata"
    exports_dir: str = "exports"
    cache_dir: str = "cache"
    
    # Memory optimization settings
    max_memory_gb: float = 8.0
    chunk_size: int = 10000
    max_workers: int = 4
    
    # Split ratios
    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1
    
    # File formats
    supported_formats: List[str] = field(default_factory=lambda: [
        "json", "jsonl", "csv", "parquet", "pickle"
    ])
    
    # Validation thresholds
    min_samples: int = 100
    max_text_length: int = 10000
    min_text_length: int = 1
    
    # Quality metrics thresholds
    min_completeness: float = 0.95
    min_uniqueness: float = 0.8
    min_balance: float = 0.7
    
    # Export formats
    export_formats: List[str] = field(default_factory=lambda: [
        "hf_dataset", "json", "csv", "parquet", "conll"
    ])
    
    def __post_init__(self):
        """Set up directory paths after initialization."""
        self.base_path = Path(self.base_dir)
        self.data_path = self.base_path / self.data_dir
        self.metadata_path = self.base_path / self.metadata_dir
        self.exports_path = self.base_path / self.exports_dir
        self.cache_path = self.base_path / self.cache_dir
        
        # Create directories if they don't exist
        for path in [self.data_path, self.metadata_path, self.exports_path, self.cache_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_dataset_card_path(self) -> Path:
        """Get path for dataset card (README.md)."""
        return self.base_path / "README.md"
    
    def get_config_path(self) -> Path:
        """Get path for configuration file."""
        return self.metadata_path / "config.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                config_dict[key] = str(value)
            else:
                config_dict[key] = value
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DatasetConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'DatasetConfig':
        """Load configuration from file."""
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to file."""
        import json
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# Default configuration instance
default_config = DatasetConfig()


# Environment variables
HF_TOKEN_ENV = "HUGGINGFACE_HUB_TOKEN"
CACHE_DIR_ENV = "HF_CACHE_DIR"
DATASET_CACHE_DIR_ENV = "HF_DATASET_CACHE_DIR"


def get_hf_token() -> Optional[str]:
    """Get Hugging Face token from environment or config."""
    return os.getenv(HF_TOKEN_ENV, default_config.token)


def get_cache_dir() -> str:
    """Get cache directory from environment or config."""
    return os.getenv(CACHE_DIR_ENV, str(default_config.cache_path))


def validate_config(config: DatasetConfig) -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []
    
    # Check required fields
    if not config.dataset_name or not config.dataset_name.strip():
        errors.append("Dataset name cannot be empty")
    
    # Check ratios
    if abs(config.train_ratio + config.val_ratio + config.test_ratio - 1.0) > 0.001:
        errors.append("Split ratios must sum to 1.0")
    
    for ratio in [config.train_ratio, config.val_ratio, config.test_ratio]:
        if not 0 <= ratio <= 1:
            errors.append(f"Split ratio {ratio} must be between 0 and 1")
    
    # Check thresholds
    if not 0 <= config.min_completeness <= 1:
        errors.append("Min completeness must be between 0 and 1")
    
    if not 0 <= config.min_uniqueness <= 1:
        errors.append("Min uniqueness must be between 0 and 1")
    
    if not 0 <= config.min_balance <= 1:
        errors.append("Min balance must be between 0 and 1")
    
    return errors