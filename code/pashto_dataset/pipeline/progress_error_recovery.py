"""
Progress tracking and error recovery system for the Pashto dataset pipeline.
"""

import time
import json
import os
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from contextlib import contextmanager


class StepStatus(Enum):
    """Step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class PipelineStatus(Enum):
    """Pipeline execution status."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RESUMING = "resuming"


@dataclass
class ProgressInfo:
    """Progress information for tracking."""
    current_step: str
    step_status: StepStatus
    overall_progress: float  # 0.0 to 100.0
    step_progress: float     # 0.0 to 100.0
    total_steps: int
    completed_steps: int
    current_step_start_time: datetime
    current_step_duration: float
    estimated_remaining_time: float
    records_processed: int
    total_records: int
    current_rate: float  # records per second
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        info_dict = asdict(self)
        # Convert datetime objects
        for key, value in info_dict.items():
            if isinstance(value, datetime):
                info_dict[key] = value.isoformat()
        return info_dict


@dataclass
class ErrorInfo:
    """Error information for recovery."""
    step_name: str
    error_type: str
    error_message: str
    error_details: Dict[str, Any]
    timestamp: datetime
    retry_count: int
    is_recoverable: bool
    recovery_suggestion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        error_dict = asdict(self)
        error_dict['timestamp'] = self.timestamp.isoformat()
        return error_dict


class ProgressTracker:
    """Tracks pipeline progress and provides real-time updates."""
    
    def __init__(self, pipeline_id: str, logs_path: str):
        self.pipeline_id = pipeline_id
        self.logs_path = Path(logs_path)
        self.progress_file = self.logs_path / f"{pipeline_id}_progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.steps: List[str] = []
        self.step_status: Dict[str, StepStatus] = {}
        self.step_progress: Dict[str, float] = {}
        self.step_start_times: Dict[str, datetime] = {}
        self.step_durations: Dict[str, float] = {}
        self.step_records: Dict[str, int] = {}
        self.total_records: int = 0
        
        self.current_step: Optional[str] = None
        self.overall_progress: float = 0.0
        self.total_steps: int = 0
        self.completed_steps: int = 0
        self.start_time: datetime = datetime.now()
        
        self._lock = threading.RLock()
        self._callbacks: List[Callable] = []
        
        # Load existing progress if available
        self._load_progress()
    
    def register_callback(self, callback: Callable[[ProgressInfo], None]):
        """Register a callback for progress updates."""
        with self._lock:
            self._callbacks.append(callback)
    
    def set_steps(self, steps: List[str], total_records: int = 0):
        """Set the pipeline steps."""
        with self._lock:
            self.steps = steps
            self.total_steps = len(steps)
            self.total_records = total_records
            
            for step in steps:
                if step not in self.step_status:
                    self.step_status[step] = StepStatus.PENDING
                    self.step_progress[step] = 0.0
                    self.step_records[step] = 0
            
            self._save_progress()
    
    def start_step(self, step_name: str, estimated_records: int = 0):
        """Start tracking a new step."""
        with self._lock:
            if step_name not in self.steps:
                self.steps.append(step_name)
                self.total_steps = len(self.steps)
            
            self.current_step = step_name
            self.step_status[step_name] = StepStatus.RUNNING
            self.step_start_times[step_name] = datetime.now()
            self.step_progress[step_name] = 0.0
            self.step_records[step_name] = 0
            
            if estimated_records > 0:
                self.total_records = max(self.total_records, estimated_records)
            
            self._save_progress()
            self._notify_progress()
    
    def update_step_progress(self, step_name: str, current_records: int, 
                           additional_info: Dict[str, Any] = None):
        """Update step progress."""
        with self._lock:
            if step_name not in self.steps or step_name not in self.step_start_times:
                return
            
            self.step_records[step_name] = current_records
            
            # Calculate step progress
            if self.total_records > 0:
                step_progress = (current_records / self.total_records) * 100
                self.step_progress[step_name] = min(step_progress, 100.0)
            elif 'estimated_records' in (additional_info or {}):
                estimated = additional_info['estimated_records']
                step_progress = (current_records / estimated) * 100
                self.step_progress[step_name] = min(step_progress, 100.0)
            else:
                # Use additional info progress if available
                if additional_info and 'step_progress' in additional_info:
                    self.step_progress[step_name] = additional_info['step_progress']
            
            # Calculate overall progress
            completed_steps = sum(1 for status in self.step_status.values() 
                                if status == StepStatus.COMPLETED)
            self.completed_steps = completed_steps
            
            if self.total_steps > 0:
                self.overall_progress = (completed_steps / self.total_steps) * 100
            
            self._save_progress()
            self._notify_progress()
    
    def complete_step(self, step_name: str, success: bool = True):
        """Mark a step as completed."""
        with self._lock:
            if step_name not in self.steps:
                return
            
            end_time = datetime.now()
            start_time = self.step_start_times.get(step_name, end_time)
            duration = (end_time - start_time).total_seconds()
            
            self.step_durations[step_name] = duration
            self.step_status[step_name] = StepStatus.COMPLETED if success else StepStatus.FAILED
            
            if success:
                self.completed_steps += 1
            
            if self.current_step == step_name:
                self.current_step = None
            
            # Recalculate overall progress
            if self.total_steps > 0:
                self.overall_progress = (self.completed_steps / self.total_steps) * 100
            
            self._save_progress()
            self._notify_progress()
    
    def skip_step(self, step_name: str):
        """Mark a step as skipped."""
        with self._lock:
            if step_name not in self.steps:
                return
            
            self.step_status[step_name] = StepStatus.SKIPPED
            self._save_progress()
            self._notify_progress()
    
    def cancel_pipeline(self):
        """Cancel the entire pipeline."""
        with self._lock:
            if self.current_step:
                self.step_status[self.current_step] = StepStatus.CANCELLED
                self.current_step = None
            
            self._save_progress()
            self._notify_progress()
    
    def get_progress_info(self) -> ProgressInfo:
        """Get current progress information."""
        with self._lock:
            now = datetime.now()
            
            # Calculate current step duration
            current_step_duration = 0.0
            if self.current_step and self.current_step in self.step_start_times:
                current_step_duration = (now - self.step_start_times[self.current_step]).total_seconds()
            
            # Calculate estimated remaining time
            estimated_remaining_time = self._estimate_remaining_time()
            
            # Calculate current processing rate
            current_rate = self._calculate_current_rate()
            
            return ProgressInfo(
                current_step=self.current_step or "",
                step_status=(
                    self.step_status.get(self.current_step, StepStatus.PENDING) 
                    if self.current_step else StepStatus.PENDING
                ),
                overall_progress=self.overall_progress,
                step_progress=(
                    self.step_progress.get(self.current_step, 0.0) 
                    if self.current_step else 0.0
                ),
                total_steps=self.total_steps,
                completed_steps=self.completed_steps,
                current_step_start_time=(
                    self.step_start_times.get(self.current_step, now) 
                    if self.current_step else now
                ),
                current_step_duration=current_step_duration,
                estimated_remaining_time=estimated_remaining_time,
                records_processed=sum(self.step_records.values()),
                total_records=self.total_records,
                current_rate=current_rate
            )
    
    def _estimate_remaining_time(self) -> float:
        """Estimate remaining time for pipeline completion."""
        if not self.current_step:
            return 0.0
        
        # Get average step duration so far
        completed_durations = [d for d in self.step_durations.values() if d > 0]
        if not completed_durations:
            return 0.0
        
        avg_duration = sum(completed_durations) / len(completed_durations)
        remaining_steps = self.total_steps - self.completed_steps
        return remaining_steps * avg_duration
    
    def _calculate_current_rate(self) -> float:
        """Calculate current processing rate."""
        if not self.current_step:
            return 0.0
        
        duration = self.step_durations.get(self.current_step, 0)
        if duration <= 0:
            return 0.0
        
        processed = self.step_records.get(self.current_step, 0)
        return processed / duration if duration > 0 else 0.0
    
    def _notify_progress(self):
        """Notify all registered callbacks."""
        progress_info = self.get_progress_info()
        for callback in self._callbacks:
            try:
                callback(progress_info)
            except Exception:
                pass  # Ignore callback errors
    
    def _save_progress(self):
        """Save progress to file."""
        progress_data = {
            "pipeline_id": self.pipeline_id,
            "steps": self.steps,
            "step_status": {k: v.value for k, v in self.step_status.items()},
            "step_progress": self.step_progress,
            "step_start_times": {
                k: v.isoformat() for k, v in self.step_start_times.items()
            },
            "step_durations": self.step_durations,
            "step_records": self.step_records,
            "total_records": self.total_records,
            "current_step": self.current_step,
            "overall_progress": self.overall_progress,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "start_time": self.start_time.isoformat()
        }
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2)
    
    def _load_progress(self):
        """Load existing progress from file."""
        if not self.progress_file.exists():
            return
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            # Restore data
            self.steps = progress_data.get("steps", [])
            self.total_records = progress_data.get("total_records", 0)
            self.current_step = progress_data.get("current_step")
            self.overall_progress = progress_data.get("overall_progress", 0.0)
            self.total_steps = progress_data.get("total_steps", 0)
            self.completed_steps = progress_data.get("completed_steps", 0)
            self.start_time = datetime.fromisoformat(
                progress_data.get("start_time", datetime.now().isoformat())
            )
            
            # Restore step data
            for step_name in self.steps:
                if step_name in progress_data.get("step_status", {}):
                    self.step_status[step_name] = StepStatus(
                        progress_data["step_status"][step_name]
                    )
                if step_name in progress_data.get("step_progress", {}):
                    self.step_progress[step_name] = progress_data["step_progress"][step_name]
                if step_name in progress_data.get("step_durations", {}):
                    self.step_durations[step_name] = progress_data["step_durations"][step_name]
                if step_name in progress_data.get("step_records", {}):
                    self.step_records[step_name] = progress_data["step_records"][step_name]
        
        except Exception:
            # If loading fails, start fresh
            pass


class ErrorRecovery:
    """Handles error recovery and retry logic."""
    
    def __init__(self, logs_path: str):
        self.logs_path = Path(logs_path)
        self.errors_file = self.logs_path / "errors.json"
        self.errors_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.errors: List[ErrorInfo] = []
        self.recovery_strategies: Dict[str, Callable] = {}
        self._load_errors()
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register a recovery strategy for a specific error type."""
        self.recovery_strategies[error_type] = strategy
    
    def add_error(self, step_name: str, error: Exception, 
                 is_recoverable: bool = True, recovery_suggestion: str = None) -> ErrorInfo:
        """Add an error to the recovery system."""
        error_info = ErrorInfo(
            step_name=step_name,
            error_type=type(error).__name__,
            error_message=str(error),
            error_details={
                "type": str(type(error)),
                "module": getattr(error, '__module__', 'unknown'),
                "args": getattr(error, 'args', [])
            },
            timestamp=datetime.now(),
            retry_count=0,
            is_recoverable=is_recoverable,
            recovery_suggestion=recovery_suggestion
        )
        
        self.errors.append(error_info)
        self._save_errors()
        return error_info
    
    def get_errors_for_step(self, step_name: str) -> List[ErrorInfo]:
        """Get all errors for a specific step."""
        return [error for error in self.errors if error.step_name == step_name]
    
    def get_retryable_errors(self, step_name: str) -> List[ErrorInfo]:
        """Get all retryable errors for a step."""
        return [
            error for error in self.errors 
            if error.step_name == step_name and error.is_recoverable
        ]
    
    def can_retry(self, step_name: str, max_retries: int, 
                 retry_delay: float, exponential_backoff: bool = True) -> bool:
        """Check if a step can be retried."""
        retryable_errors = self.get_retryable_errors(step_name)
        if not retryable_errors:
            return True
        
        # Check retry count
        total_retries = sum(error.retry_count for error in retryable_errors)
        if total_retries >= max_retries:
            return False
        
        # Check retry delay
        latest_error = max(retryable_errors, key=lambda e: e.timestamp)
        time_since_error = (datetime.now() - latest_error.timestamp).total_seconds()
        
        if exponential_backoff:
            delay = retry_delay * (2 ** latest_error.retry_count)
        else:
            delay = retry_delay
        
        return time_since_error >= delay
    
    def increment_retry_count(self, step_name: str):
        """Increment retry count for step errors."""
        for error in self.errors:
            if error.step_name == step_name:
                error.retry_count += 1
        
        self._save_errors()
    
    def clear_errors_for_step(self, step_name: str):
        """Clear errors for a completed step."""
        self.errors = [error for error in self.errors if error.step_name != step_name]
        self._save_errors()
    
    def apply_recovery_strategy(self, step_name: str, error: ErrorInfo) -> bool:
        """Apply recovery strategy for an error."""
        strategy = self.recovery_strategies.get(error.error_type)
        if not strategy:
            return False
        
        try:
            result = strategy(error)
            return result if result is not None else True
        except Exception:
            return False
    
    def get_recovery_suggestions(self, step_name: str) -> List[str]:
        """Get recovery suggestions for a step."""
        return [
            error.recovery_suggestion for error in self.get_errors_for_step(step_name)
            if error.recovery_suggestion
        ]
    
    def _save_errors(self):
        """Save errors to file."""
        error_data = [error.to_dict() for error in self.errors]
        with open(self.errors_file, 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2)
    
    def _load_errors(self):
        """Load errors from file."""
        if not self.errors_file.exists():
            return
        
        try:
            with open(self.errors_file, 'r', encoding='utf-8') as f:
                error_data = json.load(f)
            
            self.errors = []
            for data in error_data:
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                self.errors.append(ErrorInfo(**data))
        
        except Exception:
            # If loading fails, start with empty list
            self.errors = []


@contextmanager
def progress_context(progress_tracker: ProgressTracker, step_name: str, 
                    total_records: int = 0, logger = None):
    """Context manager for progress tracking."""
    progress_tracker.start_step(step_name, total_records)
    start_time = time.time()
    
    try:
        yield progress_tracker
        progress_tracker.complete_step(step_name, success=True)
        if logger:
            logger.info(f"Step '{step_name}' completed successfully")
    except Exception as e:
        progress_tracker.complete_step(step_name, success=False)
        if logger:
            logger.error(f"Step '{step_name}' failed: {str(e)}")
        raise
    finally:
        if logger:
            duration = time.time() - start_time
            logger.debug(f"Step '{step_name}' duration: {duration:.2f}s")