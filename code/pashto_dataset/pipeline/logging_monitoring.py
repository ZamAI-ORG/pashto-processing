"""
Logging and monitoring system for the Pashto dataset pipeline.
"""

import logging
import sys
import os
import time
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from contextlib import contextmanager


@dataclass
class PipelineMetrics:
    """Pipeline execution metrics."""
    pipeline_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    current_step: Optional[str] = None
    error_count: int = 0
    warning_count: int = 0
    
    # Resource usage
    peak_memory_mb: float = 0.0
    peak_cpu_percent: float = 0.0
    peak_disk_usage_gb: float = 0.0
    
    # Performance metrics
    total_duration: Optional[float] = None  # seconds
    average_step_duration: float = 0.0
    slowest_step: Optional[str] = None
    fastest_step: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        metrics_dict = asdict(self)
        # Convert datetime objects to ISO format
        for key, value in metrics_dict.items():
            if isinstance(value, datetime):
                metrics_dict[key] = value.isoformat()
        return metrics_dict
    
    @classmethod
    def from_dict(cls, metrics_dict: Dict[str, Any]) -> 'PipelineMetrics':
        """Create metrics from dictionary."""
        # Convert ISO datetime strings back to datetime objects
        for key, value in metrics_dict.items():
            if key in ['start_time', 'end_time'] and isinstance(value, str):
                metrics_dict[key] = datetime.fromisoformat(value)
        return cls(**metrics_dict)


@dataclass
class StepMetrics:
    """Individual step execution metrics."""
    step_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, cancelled
    retry_count: int = 0
    input_files: List[str] = None
    output_files: List[str] = None
    records_processed: int = 0
    records_failed: int = 0
    error_messages: List[str] = None
    warnings: List[str] = None
    duration: Optional[float] = None  # seconds
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0
    
    def __post_init__(self):
        if self.input_files is None:
            self.input_files = []
        if self.output_files is None:
            self.output_files = []
        if self.error_messages is None:
            self.error_messages = []
        if self.warnings is None:
            self.warnings = []


class MetricsCollector:
    """Collects and manages pipeline metrics."""
    
    def __init__(self, pipeline_id: str, logs_path: str):
        self.pipeline_id = pipeline_id
        self.logs_path = Path(logs_path)
        self.metrics_file = self.logs_path / f"{pipeline_id}_metrics.json"
        self.steps_dir = self.logs_path / "steps"
        self.steps_dir.mkdir(exist_ok=True)
        
        self.pipeline_metrics = PipelineMetrics(
            pipeline_id=pipeline_id,
            start_time=datetime.now()
        )
        self.step_metrics: Dict[str, StepMetrics] = {}
        self._system_monitor = SystemMonitor()
    
    def start_step(self, step_name: str, input_files: List[str] = None) -> StepMetrics:
        """Start tracking a new step."""
        step_metrics = StepMetrics(
            step_name=step_name,
            start_time=datetime.now(),
            input_files=input_files or []
        )
        self.step_metrics[step_name] = step_metrics
        self.pipeline_metrics.current_step = step_name
        self.pipeline_metrics.total_steps += 1
        return step_metrics
    
    def complete_step(self, step_name: str, status: str = "completed", 
                     output_files: List[str] = None, records_processed: int = 0,
                     records_failed: int = 0, error_messages: List[str] = None,
                     warnings: List[str] = None):
        """Complete step tracking."""
        if step_name not in self.step_metrics:
            return
        
        step_metrics = self.step_metrics[step_name]
        step_metrics.end_time = datetime.now()
        step_metrics.status = status
        step_metrics.output_files = output_files or []
        step_metrics.records_processed = records_processed
        step_metrics.records_failed = records_failed
        step_metrics.error_messages = error_messages or []
        step_metrics.warnings = warnings or []
        step_metrics.duration = (step_metrics.end_time - step_metrics.start_time).total_seconds()
        
        # Get system metrics
        step_metrics.memory_usage_mb = self._system_monitor.get_memory_usage()
        step_metrics.cpu_percent = self._system_monitor.get_cpu_usage()
        
        # Update pipeline metrics
        if status == "completed":
            self.pipeline_metrics.completed_steps += 1
        elif status == "failed":
            self.pipeline_metrics.failed_steps += 1
            self.pipeline_metrics.error_count += len(error_messages or [])
        elif status == "warning":
            self.pipeline_metrics.warning_count += len(warnings or [])
        
        # Update system resource usage
        self._update_system_resources()
        
        # Save step metrics
        self._save_step_metrics(step_metrics)
        
        # Save pipeline metrics
        self._save_pipeline_metrics()
        
        # Clear current step if completed
        if status in ["completed", "failed", "cancelled"]:
            self.pipeline_metrics.current_step = None
    
    def add_warning(self, step_name: str, warning: str):
        """Add warning to step."""
        if step_name in self.step_metrics:
            self.step_metrics[step_name].warnings.append(warning)
            self.pipeline_metrics.warning_count += 1
    
    def add_error(self, step_name: str, error: str):
        """Add error to step."""
        if step_name in self.step_metrics:
            self.step_metrics[step_name].error_messages.append(error)
            self.pipeline_metrics.error_count += 1
    
    def complete_pipeline(self, status: str = "completed"):
        """Complete pipeline tracking."""
        self.pipeline_metrics.end_time = datetime.now()
        self.pipeline_metrics.status = status
        self.pipeline_metrics.total_duration = (
            self.pipeline_metrics.end_time - self.pipeline_metrics.start_time
        ).total_seconds()
        
        # Calculate step statistics
        completed_steps = [s for s in self.step_metrics.values() if s.status == "completed"]
        if completed_steps:
            durations = [s.duration for s in completed_steps if s.duration]
            self.pipeline_metrics.average_step_duration = sum(durations) / len(durations)
            
            slowest = max(completed_steps, key=lambda s: s.duration or 0)
            fastest = min(completed_steps, key=lambda s: s.duration or float('inf'))
            self.pipeline_metrics.slowest_step = slowest.step_name
            self.pipeline_metrics.fastest_step = fastest.step_name
        
        self._update_system_resources()
        self._save_pipeline_metrics()
    
    def _update_system_resources(self):
        """Update system resource usage."""
        self.pipeline_metrics.peak_memory_mb = max(
            self.pipeline_metrics.peak_memory_mb,
            self._system_monitor.get_memory_usage()
        )
        self.pipeline_metrics.peak_cpu_percent = max(
            self.pipeline_metrics.peak_cpu_percent,
            self._system_monitor.get_cpu_usage()
        )
        self.pipeline_metrics.peak_disk_usage_gb = max(
            self.pipeline_metrics.peak_disk_usage_gb,
            self._system_monitor.get_disk_usage()
        )
    
    def _save_step_metrics(self, step_metrics: StepMetrics):
        """Save step metrics to file."""
        step_file = self.steps_dir / f"{step_metrics.step_name}_{self.pipeline_id}.json"
        with open(step_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(step_metrics), f, indent=2, default=str)
    
    def _save_pipeline_metrics(self):
        """Save pipeline metrics to file."""
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.pipeline_metrics.to_dict(), f, indent=2, default=str)
    
    def get_metrics(self) -> PipelineMetrics:
        """Get current pipeline metrics."""
        return self.pipeline_metrics
    
    def get_step_metrics(self, step_name: str) -> Optional[StepMetrics]:
        """Get metrics for a specific step."""
        return self.step_metrics.get(step_name)


class SystemMonitor:
    """Monitors system resource usage."""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return self.process.cpu_percent()
    
    def get_disk_usage(self) -> float:
        """Get current disk usage in GB."""
        disk_usage = psutil.disk_usage('/')
        return (disk_usage.total - disk_usage.free) / (1024**3)
    
    def get_system_load(self) -> Dict[str, float]:
        """Get system load averages."""
        load_avg = os.getloadavg()
        return {
            "1min": load_avg[0],
            "5min": load_avg[1],
            "15min": load_avg[2]
        }


class PipelineLogger:
    """Custom logger for pipeline operations."""
    
    def __init__(self, name: str, logs_path: str, log_level: str = "INFO", 
                 log_format: str = None, log_rotation: str = "daily", 
                 log_retention_days: int = 30):
        self.name = name
        self.logs_path = Path(logs_path)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set format
        if log_format is None:
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)
        
        # File handler with rotation
        log_file = self.logs_path / f"{name}.log"
        if log_rotation == "daily":
            file_handler = TimedRotatingFileHandler(
                log_file, when='midnight', interval=1, backupCount=log_retention_days
            )
        else:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=log_retention_days
            )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Error file handler
        error_log_file = self.logs_path / f"{name}_errors.log"
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    @contextmanager
    def step_context(self, step_name: str, logger: 'PipelineLogger' = None):
        """Context manager for step logging."""
        start_time = time.time()
        logger.info(f"Starting step: {step_name}")
        try:
            yield
            duration = time.time() - start_time
            logger.info(f"Completed step: {step_name} (duration: {duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed step: {step_name} (duration: {duration:.2f}s, error: {str(e)})")
            raise


class MonitoringDashboard:
    """Real-time monitoring dashboard."""
    
    def __init__(self, metrics_collector: MetricsCollector, logger: PipelineLogger):
        self.metrics_collector = metrics_collector
        self.logger = logger
        self.last_update = time.time()
        self.update_interval = 30  # seconds
    
    def update(self, force: bool = False) -> bool:
        """Update monitoring dashboard."""
        now = time.time()
        if not force and (now - self.last_update) < self.update_interval:
            return False
        
        self.last_update = now
        metrics = self.metrics_collector.get_metrics()
        
        # Log current status
        if metrics.current_step:
            self.logger.info(f"Pipeline {metrics.pipeline_id} - Current step: {metrics.current_step} "
                           f"({metrics.completed_steps}/{metrics.total_steps} completed)")
        
        return True
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get pipeline status summary."""
        metrics = self.metrics_collector.get_metrics()
        return {
            "pipeline_id": metrics.pipeline_id,
            "status": metrics.status,
            "progress": {
                "completed": metrics.completed_steps,
                "total": metrics.total_steps,
                "percentage": (metrics.completed_steps / metrics.total_steps * 100) if metrics.total_steps > 0 else 0
            },
            "current_step": metrics.current_step,
            "duration": f"{metrics.total_duration:.2f}s" if metrics.total_duration else "N/A",
            "errors": metrics.error_count,
            "warnings": metrics.warning_count,
            "resources": {
                "memory_mb": f"{metrics.peak_memory_mb:.1f}",
                "cpu_percent": f"{metrics.peak_cpu_percent:.1f}",
                "disk_gb": f"{metrics.peak_disk_usage_gb:.1f}"
            }
        }