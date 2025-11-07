"""
Configuration management for the Pashto dataset pipeline orchestration system.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class PipelineConfig:
    """Main pipeline configuration."""
    pipeline_name: str = "pashto_dataset_pipeline"
    pipeline_version: str = "1.0.0"
    
    # Paths
    base_path: str = "/workspace/code/pashto_dataset"
    data_path: str = "data"
    raw_data_path: str = "data/raw"
    processed_data_path: str = "data/processed"
    output_path: str = "output"
    logs_path: str = "logs"
    
    # Processing settings
    max_workers: int = 4
    chunk_size: int = 1000
    batch_size: int = 100
    timeout_seconds: int = 3600
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # Validation settings
    validation_strict: bool = True
    auto_validation: bool = True
    validation_level: str = "standard"  # basic, standard, strict
    
    # Monitoring settings
    enable_monitoring: bool = True
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_rotation: str = "daily"
    log_retention_days: int = 30
    
    # Scheduling settings
    enable_scheduling: bool = False
    schedule_expression: str = "0 2 * * *"  # Daily at 2 AM
    timezone: str = "UTC"
    
    # Performance settings
    memory_limit_mb: int = 2048
    disk_limit_gb: int = 10
    cpu_limit_percent: int = 80
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Ensure all paths are absolute and exist
        self.base_path = os.path.abspath(self.base_path)
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        for path_attr in [self.data_path, self.raw_data_path, self.processed_data_path, 
                         self.output_path, self.logs_path]:
            full_path = os.path.join(self.base_path, path_attr)
            Path(full_path).mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PipelineConfig':
        """Create config from dictionary."""
        return cls(**config_dict)
    
    def save(self, config_path: str):
        """Save configuration to file."""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, config_path: str) -> 'PipelineConfig':
        """Load configuration from file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def update(self, **kwargs):
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Unknown configuration key: {key}")


@dataclass
class PipelineStepConfig:
    """Configuration for individual pipeline steps."""
    step_name: str
    enabled: bool = True
    dependencies: list = None
    timeout: Optional[int] = None
    retry_count: int = 0
    parallel: bool = False
    validation_required: bool = True
    custom_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.custom_config is None:
            self.custom_config = {}


class ConfigManager:
    """Configuration management class."""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or "/workspace/code/pashto_dataset"
        self.config_file = os.path.join(self.base_path, "pipeline_config.json")
        self.step_configs_file = os.path.join(self.base_path, "step_configs.json")
    
    def load_pipeline_config(self) -> PipelineConfig:
        """Load main pipeline configuration."""
        if os.path.exists(self.config_file):
            return PipelineConfig.load(self.config_file)
        else:
            config = PipelineConfig()
            config.save(self.config_file)
            return config
    
    def save_pipeline_config(self, config: PipelineConfig):
        """Save main pipeline configuration."""
        config.save(self.config_file)
    
    def load_step_configs(self) -> Dict[str, PipelineStepConfig]:
        """Load pipeline step configurations."""
        if os.path.exists(self.step_configs_file):
            with open(self.step_configs_file, 'r', encoding='utf-8') as f:
                configs_dict = json.load(f)
            return {name: PipelineStepConfig(**config) for name, config in configs_dict.items()}
        else:
            return self._get_default_step_configs()
    
    def save_step_configs(self, configs: Dict[str, PipelineStepConfig]):
        """Save pipeline step configurations."""
        configs_dict = {name: asdict(config) for name, config in configs.items()}
        with open(self.step_configs_file, 'w', encoding='utf-8') as f:
            json.dump(configs_dict, f, indent=2, ensure_ascii=False)
    
    def _get_default_step_configs(self) -> Dict[str, PipelineStepConfig]:
        """Get default step configurations."""
        return {
            "data_collection": PipelineStepConfig(
                step_name="data_collection",
                enabled=True,
                dependencies=[],
                timeout=3600,
                retry_count=3,
                parallel=False,
                validation_required=True
            ),
            "data_cleaning": PipelineStepConfig(
                step_name="data_cleaning",
                enabled=True,
                dependencies=["data_collection"],
                timeout=1800,
                retry_count=2,
                parallel=True,
                validation_required=True
            ),
            "text_normalization": PipelineStepConfig(
                step_name="text_normalization",
                enabled=True,
                dependencies=["data_cleaning"],
                timeout=1200,
                retry_count=2,
                parallel=True,
                validation_required=True
            ),
            "data_validation": PipelineStepConfig(
                step_name="data_validation",
                enabled=True,
                dependencies=["text_normalization"],
                timeout=600,
                retry_count=1,
                parallel=False,
                validation_required=False
            ),
            "format_conversion": PipelineStepConfig(
                step_name="format_conversion",
                enabled=True,
                dependencies=["data_validation"],
                timeout=900,
                retry_count=2,
                parallel=True,
                validation_required=True
            ),
            "quality_check": PipelineStepConfig(
                step_name="quality_check",
                enabled=True,
                dependencies=["format_conversion"],
                timeout=300,
                retry_count=1,
                parallel=False,
                validation_required=True
            )
        }
    
    def get_config_for_step(self, step_name: str) -> Optional[PipelineStepConfig]:
        """Get configuration for a specific step."""
        configs = self.load_step_configs()
        return configs.get(step_name)
    
    def update_step_config(self, step_name: str, **kwargs):
        """Update configuration for a specific step."""
        configs = self.load_step_configs()
        if step_name in configs:
            config = configs[step_name]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                else:
                    raise ValueError(f"Unknown configuration key for step {step_name}: {key}")
        else:
            raise ValueError(f"Unknown step: {step_name}")
        
        self.save_step_configs(configs)